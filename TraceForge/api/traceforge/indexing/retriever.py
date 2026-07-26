# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: §4.3 retrieval. Agent 1 (Requirement Extractor) deliberately does NOT use this —
# Date: 2025-12-07
# ---------------------------------------------------------------------------
"""§4.3 retrieval. Agent 1 (Requirement Extractor) deliberately does NOT use this —
it sweeps the entire corpus in document order (see agents/extractor.py) because a RAG
query would under-cover the source material. This module is for the enrichment pass,
Test Designer's incident-evidence injection, and doc-author section grounding.

Hybrid retrieval, built for real this pass: pgvector cosine + Postgres ts_rank_cd BM25
(against the `bm25_tsv` generated column already on `chunk`), fused with Reciprocal
Rank Fusion (k=60), reranked top-50->top-12 with a local cross-encoder. Vector-only
retrieval is a known failure mode for exact identifiers ('INC0012345', 'ZORDER_CREATE')
— BM25 catches what cosine similarity alone misses.
"""
from __future__ import annotations

import asyncio
import uuid
from functools import lru_cache

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from traceforge.db.models import Chunk, SourceDocument
from traceforge.indexing.embedder import embed_texts

_RRF_K = 60
_VECTOR_CANDIDATES = 50
_BM25_CANDIDATES = 50
_RERANK_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"


# Function: similarity_search
async def similarity_search(session: AsyncSession, project_id: uuid.UUID, query: str, top_k: int = 12) -> list[Chunk]:
    """Plain pgvector cosine search — kept as a standalone building block (used
    directly where a caller doesn't need the full hybrid+rerank pipeline, e.g.
    TestPlan's project-level context lookup)."""
    [query_vec] = await embed_texts([query])
    stmt = (
        select(Chunk).join(SourceDocument, Chunk.source_document_id == SourceDocument.id)
        .where(
            Chunk.project_id == project_id,
            Chunk.embedding.is_not(None),
            SourceDocument.deleted_at.is_(None),
            SourceDocument.status == "INDEXED",
        )
        .order_by(Chunk.embedding.cosine_distance(query_vec)).limit(top_k)
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())


# Function: _bm25_search
async def _bm25_search(session: AsyncSession, project_id: uuid.UUID, query: str, top_k: int) -> list[uuid.UUID]:
    result = await session.execute(
        text(
            """
            SELECT c.id FROM chunk c
            JOIN source_document s ON s.id = c.source_document_id
            WHERE c.project_id = :project_id
              AND s.deleted_at IS NULL AND s.status = 'INDEXED'
              AND c.bm25_tsv @@ plainto_tsquery('english', :query)
            ORDER BY ts_rank_cd(c.bm25_tsv, plainto_tsquery('english', :query)) DESC
            LIMIT :top_k
            """
        ),
        {"project_id": str(project_id), "query": query, "top_k": top_k},
    )
    return [row[0] for row in result.all()]


# Function: _vector_search_ids
async def _vector_search_ids(session: AsyncSession, project_id: uuid.UUID, query_vec: list[float], top_k: int) -> list[uuid.UUID]:
    result = await session.execute(
        select(Chunk.id).join(SourceDocument, Chunk.source_document_id == SourceDocument.id)
        .where(
            Chunk.project_id == project_id,
            Chunk.embedding.is_not(None),
            SourceDocument.deleted_at.is_(None),
            SourceDocument.status == "INDEXED",
        )
        .order_by(Chunk.embedding.cosine_distance(query_vec)).limit(top_k)
    )
    return [row[0] for row in result.all()]


# Function: _reciprocal_rank_fusion
def _reciprocal_rank_fusion(ranked_lists: list[list[uuid.UUID]], k: int = _RRF_K) -> list[uuid.UUID]:
    scores: dict[uuid.UUID, float] = {}
    for ranked in ranked_lists:
        for rank, chunk_id in enumerate(ranked):
            scores[chunk_id] = scores.get(chunk_id, 0.0) + 1.0 / (k + rank + 1)
    return [chunk_id for chunk_id, _ in sorted(scores.items(), key=lambda item: item[1], reverse=True)]


# Function: _get_reranker
@lru_cache(maxsize=1)
def _get_reranker():
    from sentence_transformers import CrossEncoder
    # Explicitly CPU: this box's GPU is a shared vGPU slice (A10-8Q) that Ollama already
    # keeps busy generating — a MiniLM cross-encoder auto-detecting CUDA here contends
    # with Ollama for scarce vGPU memory/scheduling and can stall for minutes. A tiny
    # cross-encoder is fast enough on CPU (~10ms/pair) that there's no reason to compete.
    return CrossEncoder(_RERANK_MODEL, device="cpu")


# Function: _rerank
def _rerank(query: str, chunks: list[Chunk], top_k: int) -> list[Chunk]:
    if not chunks:
        return []
    try:
        model = _get_reranker()
    except Exception:  # noqa: BLE001 — model download/load failure must degrade, not crash retrieval
        return chunks[:top_k]
    pairs = [(query, c.text[:1000]) for c in chunks]
    scores = model.predict(pairs)
    ranked = sorted(zip(chunks, scores), key=lambda pair: pair[1], reverse=True)
    return [c for c, _ in ranked[:top_k]]


# Function: hybrid_search
async def hybrid_search(session: AsyncSession, project_id: uuid.UUID, query: str, top_k: int = 12) -> list[Chunk]:
    """pgvector cosine + BM25 -> RRF fusion -> cross-encoder rerank -> top_k."""
    # Embedding is remote GPU I/O; overlap it with the independent BM25 query.
    embedding_task = asyncio.create_task(embed_texts([query]))
    bm25_ids = await _bm25_search(session, project_id, query, _BM25_CANDIDATES)
    [query_vec] = await embedding_task
    vector_ids = await _vector_search_ids(session, project_id, query_vec, _VECTOR_CANDIDATES)
    fused_ids = _reciprocal_rank_fusion([vector_ids, bm25_ids])[:50]
    if not fused_ids:
        return []

    result = await session.execute(select(Chunk).where(Chunk.id.in_(fused_ids)))
    chunks_by_id = {c.id: c for c in result.scalars().all()}
    ordered_chunks = [chunks_by_id[cid] for cid in fused_ids if cid in chunks_by_id]

    # _rerank is synchronous CPU work (model load + inference) — off the event loop so it
    # doesn't block other coroutines (health-check pings, other concurrent jobs) for its duration.
    return await asyncio.to_thread(_rerank, query, ordered_chunks, top_k)
