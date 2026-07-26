# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Vector store management using PostgreSQL + pgvector.
# Date: 2025-10-02
# ---------------------------------------------------------------------------
"""Vector store management using PostgreSQL + pgvector."""
from __future__ import annotations

import json
import logging
import re
import uuid
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout
from functools import lru_cache
from typing import List, Tuple

import backend.config as cfg
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from backend.config import (
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    MIN_RELEVANCE_SCORE,
    TOP_K_RESULTS,
    VECTOR_BACKEND,
    VECTOR_COLLECTION,
)
from backend.services.postgres_store import ensure_common_schema, get_connection

logger = logging.getLogger(__name__)


# Function: _postgres_enabled
def _postgres_enabled() -> bool:
    return getattr(cfg, "DB_BACKEND", "postgres").strip().lower() in {"postgres", "postgresql"}


# Function: _db_features
@lru_cache(maxsize=1)
def _db_features() -> dict[str, bool]:
    """Detect optional PostgreSQL features once per process."""
    if not _postgres_enabled():
        return {"pg_trgm": False}
    ensure_common_schema()
    out = {"pg_trgm": False}
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT extname FROM pg_extension")
            names = {str(r[0]).strip().lower() for r in cur.fetchall()}
    out["pg_trgm"] = "pg_trgm" in names
    return out


class _CollectionAdapter:
    """Back-compat adapter for call sites that access vs._collection."""

    # Function: count
    def count(self) -> int:
        ensure_common_schema()
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM vector_chunks WHERE collection_name = %s", (VECTOR_COLLECTION,))
                value = int(cur.fetchone()[0] or 0)
            conn.commit()
        return value

    # Function: get
    def get(self, include=None, limit=None, offset=0, where=None):
        include = include or ["documents", "metadatas"]
        ensure_common_schema()

        where_sql = ["collection_name = %s"]
        params: list = [VECTOR_COLLECTION]

        if where and isinstance(where, dict):
            src = where.get("source")
            if isinstance(src, str) and src.strip():
                where_sql.append("source = %s")
                params.append(src.strip())

        sql = (
            "SELECT id, document, metadata_json "
            "FROM vector_chunks "
            f"WHERE {' AND '.join(where_sql)} "
            "ORDER BY created_at ASC "
            + ("LIMIT %s " if limit is not None else "")
            + "OFFSET %s"
        )

        if limit is not None:
            params.append(int(limit))
        params.append(int(offset))

        ids: list[str] = []
        docs: list[str] = []
        metas: list[dict] = []

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, tuple(params))
                for row in cur.fetchall():
                    ids.append(row[0])
                    docs.append(row[1] or "")
                    metas.append(row[2] or {})
            conn.commit()

        result = {}
        if "ids" in include:
            result["ids"] = ids
        if "documents" in include:
            result["documents"] = docs
        if "metadatas" in include:
            result["metadatas"] = metas
        return result


class _VectorStoreAdapter:
    # Function: __init__
    def __init__(self):
        self._collection = _CollectionAdapter()


_vectorstore_adapter = _VectorStoreAdapter()
_EMBED_EXECUTOR = ThreadPoolExecutor(max_workers=4)


# Function: _get_embeddings
@lru_cache(maxsize=4)
def _get_embeddings(provider: str) -> Embeddings:
    from backend.config import OLLAMA_BASE_URL, OLLAMA_EMBED_MODEL, OPENAI_API_KEY, EMBEDDING_MODEL, EMBEDDING_DEVICE

    if provider == "openai" and OPENAI_API_KEY:
        from langchain_openai import OpenAIEmbeddings

        return OpenAIEmbeddings(api_key=OPENAI_API_KEY)

    # Use sentence-transformers when EMBEDDING_MODEL is a HuggingFace model path.
    if EMBEDDING_MODEL and "/" in EMBEDDING_MODEL:
        try:
            import warnings
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                from langchain_community.embeddings import HuggingFaceEmbeddings
                logger.info("Using HuggingFace embedding model '%s' on device '%s'", EMBEDDING_MODEL, EMBEDDING_DEVICE)
                return HuggingFaceEmbeddings(
                    model_name=EMBEDDING_MODEL,
                    model_kwargs={"device": EMBEDDING_DEVICE},
                    encode_kwargs={"normalize_embeddings": True},
                )
        except Exception as exc:
            logger.warning("HuggingFace embeddings unavailable (%s), falling back to Ollama", exc)

    from langchain_ollama import OllamaEmbeddings

    return OllamaEmbeddings(model=OLLAMA_EMBED_MODEL, base_url=OLLAMA_BASE_URL)


# Function: _to_vector_literal
def _to_vector_literal(values: list[float]) -> str:
    return "[" + ",".join(f"{float(v):.8f}" for v in values) + "]"


# Function: _embed_query_vector
def _embed_query_vector(query: str, provider: str) -> list[float]:
    timeout_sec = max(2, int(getattr(cfg, "OLLAMA_EMBED_TIMEOUT_SECONDS", 12) or 12))
    future = _EMBED_EXECUTOR.submit(_get_embeddings(provider).embed_query, query)
    try:
        emb = future.result(timeout=timeout_sec)
        return [float(x) for x in emb]
    except FutureTimeout as exc:
        future.cancel()
        raise RuntimeError(f"embedding timed out after {timeout_sec}s") from exc


# Function: _row_to_document
def _row_to_document(row) -> Tuple[Document, float]:
    meta = row[2] or {}
    content = row[1] or ""
    score = float(row[3] or 0.0)
    return Document(page_content=content, metadata=meta), score


# Function: get_vectorstore
def get_vectorstore(provider: str = "ollama") -> _VectorStoreAdapter:
    if not _postgres_enabled():
        return _vectorstore_adapter
    ensure_common_schema()
    return _vectorstore_adapter


# Function: reset_vectorstore
def reset_vectorstore():
    _get_embeddings.cache_clear()
    _db_features.cache_clear()


# Function: split_documents
def split_documents(docs: List[Document]) -> List[Document]:
    atomic = [d for d in docs if d.metadata.get("atomic")]
    splittable = [d for d in docs if not d.metadata.get("atomic")]

    result: List[Document] = list(atomic)

    if splittable:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            separators=["\n\n\n", "\n\n", "\n", ". ", " ", ""],
        )
        result.extend(splitter.split_documents(splittable))

    return result


# Function: wipe_collection
def wipe_collection(provider: str = "ollama") -> int:
    if not _postgres_enabled():
        return 0
    ensure_common_schema()
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM vector_chunks WHERE collection_name = %s", (VECTOR_COLLECTION,))
            deleted = int(cur.fetchone()[0] or 0)
            cur.execute("DELETE FROM vector_chunks WHERE collection_name = %s", (VECTOR_COLLECTION,))
        conn.commit()
    return deleted


# Function: _embed_sub_batch_with_retry
def _embed_sub_batch_with_retry(embed_model, sub: list[str], provider: str, batch_no: int, batch_total: int) -> tuple:
    """Embed one sub-batch, retrying up to 3 times with a fresh embedding model on failure."""
    for attempt in range(1, 4):
        try:
            return embed_model.embed_documents(sub), embed_model
        except Exception as exc:
            if attempt == 3:
                raise
            logger.warning(
                "Embed sub-batch %d/%d attempt %d failed (%s) — retrying in 3s",
                batch_no,
                batch_total,
                attempt,
                exc,
            )
            import time as _time
            _time.sleep(3)
            _get_embeddings.cache_clear()
            embed_model = _get_embeddings(provider)


# Function: _embed_texts_in_batches
def _embed_texts_in_batches(texts: list[str], provider: str) -> list:
    """Sub-batch embed calls so the Ollama runner doesn't crash on large inputs.

    Testing shows the nomic-embed-text runner silently dies above ~200 texts per call.
    """
    embed_batch = max(1, int(getattr(cfg, "OLLAMA_EMBED_BATCH_SIZE", 150)))
    embeddings: list = []
    embed_model = _get_embeddings(provider)
    batch_total = (len(texts) + embed_batch - 1) // embed_batch
    for i in range(0, len(texts), embed_batch):
        sub = texts[i : i + embed_batch]
        sub_embeddings, embed_model = _embed_sub_batch_with_retry(
            embed_model, sub, provider, i // embed_batch + 1, batch_total
        )
        embeddings.extend(sub_embeddings)
    return embeddings


# Function: index_documents
def index_documents(docs: List[Document], provider: str = "ollama") -> int:
    if not docs:
        return 0
    if not _postgres_enabled():
        logger.info("Skipping PostgreSQL pgvector indexing because DB_BACKEND=%s", cfg.DB_BACKEND)
        return 0

    ensure_common_schema()
    chunks = split_documents(docs)
    texts = [d.page_content or "" for d in chunks]
    metadatas = [d.metadata or {} for d in chunks]

    embeddings = _embed_texts_in_batches(texts, provider)

    rows_to_insert: list[tuple] = []
    with get_connection() as conn:
        with conn.cursor() as cur:
            for content, meta, emb in zip(texts, metadatas, embeddings):
                source = str(meta.get("source", "") or "")
                vec = _to_vector_literal([float(x) for x in emb])
                rows_to_insert.append(
                    (
                        str(uuid.uuid4()),
                        VECTOR_COLLECTION,
                        source,
                        content,
                        json.dumps(meta, ensure_ascii=True),
                        vec,
                    )
                )

            cur.executemany(
                """
                INSERT INTO vector_chunks(id, collection_name, source, document, metadata_json, embedding, updated_at)
                VALUES (%s, %s, %s, %s, %s::jsonb, %s::vector, NOW())
                """,
                rows_to_insert,
            )
        conn.commit()

    inserted = len(rows_to_insert)
    logger.info("Indexed %d chunks into PostgreSQL pgvector table.", inserted)
    return inserted


# Function: similarity_search
def similarity_search(
    query: str,
    provider: str = "ollama",
    k: int = TOP_K_RESULTS,
) -> List[Tuple[Document, float]]:
    if not query.strip():
        return []

    try:
        query_vector = _embed_query_vector(query=query, provider=provider)
    except Exception as exc:
        logger.warning("Embedding unavailable for similarity search: %s", exc)
        return []

    # Try LanceDB first if enabled
    if VECTOR_BACKEND in {"lancedb", "hybrid"}:
        lancedb_results = _similarity_search_lancedb(vector=query_vector, text_query=query, k=k)
        logger.debug("LanceDB returned %d results for query %s", len(lancedb_results), query[:60])
        if lancedb_results:
            return lancedb_results
        if VECTOR_BACKEND == "lancedb":
            logger.warning("LanceDB returned 0 results for query: %s", query[:120])
            return []
        logger.info("LanceDB empty, falling back to Qdrant for query: %s", query[:80])

    # Try Qdrant as fallback
    if VECTOR_BACKEND in {"qdrant", "hybrid"}:
        qdrant_results = _similarity_search_qdrant(vector=query_vector, k=k)
        logger.debug("Qdrant returned %d results for query %s", len(qdrant_results), query[:60])
        if qdrant_results:
            return qdrant_results
        if VECTOR_BACKEND == "qdrant":
            logger.warning("Qdrant returned 0 results for query: %s", query[:120])
            return []
        logger.info("Qdrant empty, falling back to pgvector for query: %s", query[:80])

    ensure_common_schema()
    qvec = _to_vector_literal(query_vector)

    with get_connection() as conn:
        with conn.cursor() as cur:
            # Keep a strong ANN recall window with better latency on larger corpora.
            try:
                cur.execute("SET LOCAL hnsw.ef_search = 120")
            except Exception:
                pass  # HNSW index not yet built or pgvector < 0.5 — harmless
            cur.execute(
                """
                SELECT id, document, metadata_json,
                       (1 - (embedding <=> %s::vector)) AS score
                FROM vector_chunks
                WHERE collection_name = %s
                ORDER BY embedding <=> %s::vector
                LIMIT %s
                """,
                # k * 6 keeps reranker diversity while reducing query/transfer cost.
                (qvec, VECTOR_COLLECTION, qvec, int(max(1, k * 6))),
            )
            rows = cur.fetchall()
        conn.commit()

    results = [_row_to_document(row) for row in rows]
    return [(doc, score) for doc, score in results if score >= MIN_RELEVANCE_SCORE][:k]


# Function: _fetch_qdrant_rows
def _fetch_qdrant_rows(vector: list[float], k: int):
    try:
        from backend.services.qdrant_store import get_points_count, search_by_vector

        # Fast-path: skip embedding work when collection is empty.
        if int(get_points_count() or 0) <= 0:
            return []

        return search_by_vector(vector=vector, limit=max(1, int(k * 4)))
    except Exception as exc:
        logger.warning("Qdrant similarity search unavailable, falling back to pgvector: %s", exc)
        return None


# Function: _qdrant_row_to_result
def _qdrant_row_to_result(row):
    payload = dict(getattr(row, "payload", {}) or {})
    text = str(payload.get("description_chunk") or payload.get("text") or "").strip()
    if not text:
        return None

    score = float(getattr(row, "score", 0.0) or 0.0)
    metadata = {
        "source": payload.get("source_name") or "servicenow_qdrant",
        "type": payload.get("source_type") or "servicenow_incident",
        "incident_number": payload.get("ticket_id") or "",
        "category": payload.get("category") or "",
        "state": payload.get("state") or "",
        "assignment_group": payload.get("group") or "",
    }
    return Document(page_content=text, metadata=metadata), score


# Function: _similarity_search_qdrant
def _similarity_search_qdrant(
    vector: list[float],
    k: int,
) -> List[Tuple[Document, float]]:
    if not vector:
        return []

    rows = _fetch_qdrant_rows(vector, k)
    if not rows:
        return []

    out = [item for item in (_qdrant_row_to_result(row) for row in rows) if item is not None]
    return [(doc, score) for doc, score in out if score >= MIN_RELEVANCE_SCORE][:k]


# Function: _fetch_lancedb_similarity_rows
def _fetch_lancedb_similarity_rows(vector: list[float], text_query: str, k: int):
    try:
        from backend.services.lancedb_store import (
            get_points_count,
            search_by_vector as lancedb_search_vector,
            search_hybrid,
        )

        # Fast-path: skip when table is empty.
        if int(get_points_count() or 0) <= 0:
            return []

        # Use hybrid search if text_query provided, otherwise vector-only
        if text_query:
            return search_hybrid(vector=vector, text_query=text_query, limit=max(1, int(k * 4)))
        return lancedb_search_vector(vector=vector, limit=max(1, int(k * 4)))

    except Exception as exc:
        logger.warning("LanceDB similarity search unavailable: %s", exc)
        return None


# Function: _lancedb_similarity_row_to_result
def _lancedb_similarity_row_to_result(row):
    # LanceDB returns dicts with schema: incident_id, embedding, text_chunk, metadata
    text = str(row.get("text_chunk") or "").strip()
    if not text:
        return None

    # LanceDB returns _distance as cosine distance (0=identical, 1=opposite).
    # Convert to similarity score: similarity = 1.0 - distance.
    raw_dist = row.get("_distance")
    if raw_dist is not None:
        score = max(0.0, 1.0 - float(raw_dist))
    else:
        score = float(row.get("score") or 0.5)

    # Extract metadata from the metadata object
    metadata_obj = row.get("metadata", {})
    metadata = {
        "source": metadata_obj.get("source_name") or "servicenow_lancedb",
        "type": metadata_obj.get("source_type") or "servicenow_incident",
        "incident_number": row.get("incident_id") or "",
        "category": metadata_obj.get("category") or "",
        "state": metadata_obj.get("state") or "",
        "assignment_group": metadata_obj.get("assignment_group") or "",
    }
    return Document(page_content=text, metadata=metadata), score


# Function: _similarity_search_lancedb
def _similarity_search_lancedb(
    vector: list[float],
    text_query: str = "",
    k: int = TOP_K_RESULTS,
) -> List[Tuple[Document, float]]:
    """Search LanceDB for similar vectors."""
    if not vector:
        return []

    rows = _fetch_lancedb_similarity_rows(vector, text_query, k)
    if not rows:
        return []

    out = [item for item in (_lancedb_similarity_row_to_result(row) for row in rows) if item is not None]
    return [(doc, score) for doc, score in out if score >= MIN_RELEVANCE_SCORE][:k]


_SOLUTION_KEYWORDS = ("solution", "resolution", "resolved", "fix", "workaround", "steps", "action taken")


# Function: fetch_solution_chunks
def fetch_solution_chunks(sources: List[str], provider: str = "ollama") -> List[Document]:
    if not sources:
        return []
    if not _postgres_enabled():
        return []

    like_sql = " OR ".join(["document ILIKE %s" for _ in _SOLUTION_KEYWORDS])
    like_params = [f"%{k}%" for k in _SOLUTION_KEYWORDS]

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT id, document, metadata_json
                FROM vector_chunks
                WHERE collection_name = %s
                  AND source = ANY(%s)
                  AND ({like_sql})
                LIMIT 500
                """,
                (VECTOR_COLLECTION, sources, *like_params),
            )
            rows = cur.fetchall()
        conn.commit()

    return [Document(page_content=row[1] or "", metadata=row[2] or {}) for row in rows]


# Function: get_collection_stats
def get_collection_stats(provider: str = "ollama") -> dict:
    pg_total = 0
    if _postgres_enabled():
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM vector_chunks WHERE collection_name = %s", (VECTOR_COLLECTION,))
                pg_total = int(cur.fetchone()[0] or 0)
            conn.commit()

    qdrant_total = 0
    if VECTOR_BACKEND in {"qdrant", "hybrid"}:
        try:
            from backend.services.qdrant_store import get_points_count
            qdrant_total = int(get_points_count() or 0)
        except Exception:
            qdrant_total = 0

    lancedb_total = 0
    if VECTOR_BACKEND in {"lancedb", "hybrid"}:
        try:
            from backend.services.lancedb_store import get_points_count as ldb_count
            lancedb_total = int(ldb_count() or 0)
        except Exception:
            lancedb_total = 0

    if VECTOR_BACKEND == "qdrant":
        total = qdrant_total
    elif VECTOR_BACKEND == "lancedb":
        total = lancedb_total if lancedb_total > 0 else pg_total
    else:
        total = max(pg_total, qdrant_total, lancedb_total)

    return {
        "collection": VECTOR_COLLECTION,
        "total_chunks": total,
        "pgvector_chunks": pg_total,
        "qdrant_points": qdrant_total,
        "lancedb_points": lancedb_total,
        "vector_backend": VECTOR_BACKEND,
    }


# Function: delete_by_source
def delete_by_source(source_name: str, provider: str = "ollama") -> int:
    if not _postgres_enabled():
        return 0
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT COUNT(*) FROM vector_chunks WHERE collection_name = %s AND source = %s",
                (VECTOR_COLLECTION, source_name),
            )
            total = int(cur.fetchone()[0] or 0)
            cur.execute(
                "DELETE FROM vector_chunks WHERE collection_name = %s AND source = %s",
                (VECTOR_COLLECTION, source_name),
            )
        conn.commit()
    return total


_METADATA_ILIKE_SQL = """
SELECT id, document, metadata_json
FROM vector_chunks
WHERE collection_name = %s
  AND document ILIKE %s
LIMIT %s
"""


# Function: _metadata_search_exact_then_ilike
def _metadata_search_exact_then_ilike(cur, run, results, k, exact_sql, exact_value, exact_score, fallback_score):
    """Run the exact-match query, then fall back to ILIKE if still short of k results."""
    run(cur, exact_sql, (VECTOR_COLLECTION, exact_value, int(k)), exact_score)
    if len(results) < int(k):
        run(cur, _METADATA_ILIKE_SQL, (VECTOR_COLLECTION, f"%{exact_value}%", int(k)), fallback_score)


# Function: metadata_search
def metadata_search(
    entities: dict,
    provider: str = "ollama",
    k: int = 5,
) -> List[Tuple[Document, float]]:
    # Skip expensive postgres metadata search when Postgres is disabled.
    if not _postgres_enabled() or VECTOR_BACKEND in {"qdrant", "lancedb"}:
        return []
    results: list[Tuple[Document, float]] = []
    seen: set[str] = set()

    # Function: _run
    def _run(cur, q: str, params: tuple, score: float):
        cur.execute(q, params)
        rows = cur.fetchall()
        for row in rows:
            key = row[0]
            if key in seen:
                continue
            seen.add(key)
            results.append((Document(page_content=row[1] or "", metadata=row[2] or {}), score))

    inc_exact_sql = """
    SELECT id, document, metadata_json
    FROM vector_chunks
    WHERE collection_name = %s
      AND (metadata_json->>'incident_number') = %s
    LIMIT %s
    """
    solman_exact_sql = """
    SELECT id, document, metadata_json
    FROM vector_chunks
    WHERE collection_name = %s
      AND (metadata_json->>'solman_id') = %s
    LIMIT %s
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            for inc in entities.get("inc_numbers", []):
                _metadata_search_exact_then_ilike(cur, _run, results, k, inc_exact_sql, inc, 1.0, 0.9)

            for sid in entities.get("solman_ids", []):
                _metadata_search_exact_then_ilike(cur, _run, results, k, solman_exact_sql, sid, 0.95, 0.85)

            for dnum in entities.get("delivery_numbers", []):
                _run(
                    cur,
                    """
                    SELECT id, document, metadata_json
                    FROM vector_chunks
                    WHERE collection_name = %s
                      AND document ILIKE %s
                    LIMIT %s
                    """,
                    (VECTOR_COLLECTION, f"%{dnum}%", int(k)),
                    0.90,
                )

    return results[:k]


_KW_STOPWORDS = frozenset(
    {
        "when",
        "what",
        "where",
        "which",
        "there",
        "their",
        "about",
        "would",
        "could",
        "should",
        "have",
        "been",
        "this",
        "that",
        "with",
        "from",
        "into",
        "were",
        "they",
        "also",
        "will",
        "does",
        "used",
        "using",
        "data",
        "error",
        "issue",
        "problem",
        "system",
        "please",
        "hello",
        "user",
        "query",
        "request",
    }
)

_EXCEPTION_CLASS_RE = re.compile(r"\b([A-Za-z_][A-Za-z0-9_.]*Exception)\b")
_WIN_PATH_RE = re.compile(r"([A-Za-z]:\\[^\n'\" ]{8,260})")
_METHOD_TOKEN_RE = re.compile(r"\b([A-Za-z_][A-Za-z0-9_.]{6,})\([^\)]{0,60}\)")
# SAP / enterprise error code patterns
_SAP_ERR_CODE_RE = re.compile(r"\b(ORA-\d{3,6}|SQL\d{3,6}[A-Za-z]?|[A-Z]{2,6}\d{3,6}[A-Za-z]?|0x[0-9A-Fa-f]{6,})\b")
# SAP transaction codes (/N prefix optional)
_SAP_TCODE_RE = re.compile(r"\b((?:/N)?[A-Z]{2,5}\d{2,4})\b")
# SAP job keys (e.g. Jobkey 1234/56789)
_SAP_JOBKEY_RE = re.compile(r"(Jobkey\s*\d{4,}/\d+)", re.IGNORECASE)
# RCS names
_SAP_RCS_RE = re.compile(r"(RCS\s*['\"]?[A-Z0-9_#\-]{2,20}['\"]?)", re.IGNORECASE)
# Interface / channel / service names
_SAP_IF_RE = re.compile(r"\b((?:SI|IF|API|EAI)_[A-Za-z0-9_]{4,})\b", re.IGNORECASE)
# JDBC / channel name patterns
_SAP_CHANNEL_RE = re.compile(r"\b((?:JDBC|RFC|IDOC|SOAP|REST|HTTP|HTTPS)_[A-Z0-9_]{3,})\b", re.IGNORECASE)
# Message GUID / Transaction ID
_SAP_MSG_GUID_RE = re.compile(r"Message\s+GUID\s*:\s*([A-Za-z0-9]{12,64})", re.IGNORECASE)
_SAP_TX_ID_RE = re.compile(r"Transaction\s+ID\s*:\s*([A-Za-z0-9]{10,64})", re.IGNORECASE)
# Integration flow names (uppercase with version suffix)
_SAP_FLOW_RE = re.compile(r"\b([A-Z][A-Z0-9_]{10,}_v\d{3})\b", re.IGNORECASE)
_UNIX_PATH_RE = re.compile(r"(/(?:[A-Za-z0-9_.-]+/){1,8}[A-Za-z0-9_.-]{2,120})")
_ERROR_TOKEN_RE = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]{2,}(?:Error|Exception|Fault))\b")
_STACK_LINE_RE = re.compile(r"\b([A-Za-z_][A-Za-z0-9_.$]{4,}\([^\)]{0,120}\))")
_SYMBOLIC_TECH_RE = re.compile(r"\b([A-Za-z0-9_./:\\#-]{6,120})\b")


# Function: _extract_flat_regex_signals
def _extract_flat_regex_signals(q: str) -> list[tuple[str, float]]:
    """Signals from regexes that need no per-match filtering (single-pass, high precision)."""
    signals: list[tuple[str, float]] = []
    for exc in _EXCEPTION_CLASS_RE.findall(q):
        signals.append((exc.strip(), 0.99))
    for token in _ERROR_TOKEN_RE.findall(q):
        signals.append((token.strip(), 0.97))
    for code in _SAP_ERR_CODE_RE.findall(q):
        signals.append((code.strip(), 0.98))
    for jk in _SAP_JOBKEY_RE.findall(q):
        signals.append((jk.strip(), 0.97))
    for rcs in _SAP_RCS_RE.findall(q):
        signals.append((rcs.strip(), 0.96))
    for iface in _SAP_IF_RE.findall(q):
        signals.append((iface.strip(), 0.95))
    for chan in _SAP_CHANNEL_RE.findall(q):
        signals.append((chan.strip(), 0.94))
    for guid in _SAP_MSG_GUID_RE.findall(q):
        signals.append((guid.strip(), 0.97))
    for txid in _SAP_TX_ID_RE.findall(q):
        signals.append((txid.strip(), 0.97))
    for flow in _SAP_FLOW_RE.findall(q):
        signals.append((flow.strip(), 0.96))
    return signals


# Function: _extract_path_regex_signals
def _extract_path_regex_signals(q: str) -> list[tuple[str, float]]:
    """Windows and Unix path signals, plus the file basename when it looks like a filename."""
    signals: list[tuple[str, float]] = []

    for path in _WIN_PATH_RE.findall(q):
        p = path.strip()
        signals.append((p, 0.98))
        base = p.split("\\")[-1]
        if "." in base:
            signals.append((base, 0.96))

    for path in _UNIX_PATH_RE.findall(q):
        p = path.strip()
        if len(p) >= 8:
            signals.append((p, 0.97))
            base = p.split("/")[-1]
            if "." in base:
                signals.append((base, 0.95))

    return signals


# Function: _extract_qualified_token_signals
def _extract_qualified_token_signals(q: str) -> list[tuple[str, float]]:
    """Method/class qualified tokens, stack trace fragments, and SAP transaction codes."""
    signals: list[tuple[str, float]] = []

    for method in _METHOD_TOKEN_RE.findall(q):
        m = method.strip()
        if "." in m:
            signals.append((m, 0.95))

    for stack_token in _STACK_LINE_RE.findall(q):
        st = stack_token.strip()
        if len(st) >= 10:
            signals.append((st, 0.94))

    # SAP transaction codes (lower priority to avoid over-matching)
    for tcode in _SAP_TCODE_RE.findall(q):
        if tcode.upper() not in {"HTTP", "HTTPS", "ERROR", "INFO", "WARN"}:
            signals.append((tcode.strip(), 0.90))

    return signals


# Function: _extract_symbolic_regex_signals
def _extract_symbolic_regex_signals(q: str) -> list[tuple[str, float]]:
    """Wider symbolic technical tokens for adapters, channel IDs, traces, and flow labels."""
    signals: list[tuple[str, float]] = []
    for token in _SYMBOLIC_TECH_RE.findall(q):
        t = token.strip()
        if len(t) < 8:
            continue
        has_alpha = any(ch.isalpha() for ch in t)
        has_numeric_or_symbol = any(ch.isdigit() for ch in t) or any(ch in "._:/-#\\" for ch in t)
        if has_alpha and has_numeric_or_symbol:
            signals.append((t, 0.86))
    return signals


_KNOWN_PHRASE_SIGNALS = (
    ("cannot access the file", 0.92),
    ("being used by another process", 0.92),
    ("ioexception", 0.90),
    ("unable to establish connection", 0.91),
    ("driver returns: io error", 0.91),
    ("integration flow", 0.85),
    ("idocs got failed", 0.88),
    ("cancelled state", 0.87),
    ("reprocessed", 0.85),
)


# Function: _extract_phrase_signals
def _extract_phrase_signals(q_low: str) -> list[tuple[str, float]]:
    return [(phrase, score) for phrase, score in _KNOWN_PHRASE_SIGNALS if phrase in q_low]


# Function: _dedupe_signals
def _dedupe_signals(signals: list[tuple[str, float]]) -> list[tuple[str, float]]:
    """Deduplicate preserving first occurrence and highest score."""
    deduped: list[tuple[str, float]] = []
    seen: set[str] = set()
    for value, score in sorted(signals, key=lambda x: x[1], reverse=True):
        key = value.lower()
        if key in seen:
            continue
        seen.add(key)
        deduped.append((value, score))
    return deduped


# Function: _extract_regex_signals
def _extract_regex_signals(query: str) -> list[tuple[str, float]]:
    """Extract high-precision diagnostic signals from user query for exact-match DB search."""
    q = query or ""

    signals: list[tuple[str, float]] = []
    signals.extend(_extract_flat_regex_signals(q))
    signals.extend(_extract_path_regex_signals(q))
    signals.extend(_extract_qualified_token_signals(q))
    signals.extend(_extract_symbolic_regex_signals(q))
    signals.extend(_extract_phrase_signals(q.lower()))

    return _dedupe_signals(signals)[:28]


# Function: _fetch_lancedb_pandas_rows
def _fetch_lancedb_pandas_rows(log_context: str):
    """Open the LanceDB table and return all rows as a DataFrame, or None if unavailable."""
    try:
        from backend.services.lancedb_store import get_lancedb_client, lancedb_enabled, _table_exists
        import backend.config as _cfg

        if not lancedb_enabled():
            return None

        client = get_lancedb_client()
        table_name = _cfg.LANCEDB_TABLE
        if not _table_exists(client, table_name):
            return None

        table = client.open_table(table_name)
        return table.to_pandas()
    except Exception as exc:
        logger.warning("LanceDB %s: %s", log_context, exc)
        return None


# Function: _lancedb_row_text_metadata
def _lancedb_row_text_metadata(row, inc_id: str) -> dict:
    meta_obj = row.get("metadata", {}) or {}
    if hasattr(meta_obj, "to_dict"):
        meta_obj = meta_obj.to_dict()
    return {
        "source": meta_obj.get("source_name") or "servicenow_lancedb",
        "type": meta_obj.get("source_type") or "servicenow_incident",
        "incident_number": inc_id,
        "category": meta_obj.get("category") or "",
        "state": meta_obj.get("state") or "",
        "assignment_group": meta_obj.get("assignment_group") or "",
    }


# Function: _collect_lancedb_term_matches
def _collect_lancedb_term_matches(all_rows, term: str, base_score: float, seen_ids: set, results: list, k: int) -> bool:
    """Append matches for one term to results; returns True once results reach k."""
    term_low = term.lower()
    for _, row in all_rows.iterrows():
        chunk = str(row.get("text_chunk", "") or "").lower()
        if term_low not in chunk:
            continue
        inc_id = str(row.get("incident_id", "") or "")
        if inc_id in seen_ids:
            continue
        seen_ids.add(inc_id)
        metadata = _lancedb_row_text_metadata(row, inc_id)
        results.append((Document(page_content=str(row.get("text_chunk", "")), metadata=metadata), base_score))
        if len(results) >= k:
            return True
    return False


# Function: _scan_lancedb_rows_for_terms
def _scan_lancedb_rows_for_terms(all_rows, terms, k: int) -> List[Tuple[Document, float]]:
    """Scan LanceDB rows' text_chunk field for each term, one incident per hit."""
    results: list[Tuple[Document, float]] = []
    seen_ids: set[str] = set()

    for term, base_score in terms:
        if _collect_lancedb_term_matches(all_rows, term, base_score, seen_ids, results, k):
            break

    return results


# Function: _regex_signal_search_lancedb
def _regex_signal_search_lancedb(query: str, k: int = 6) -> List[Tuple[Document, float]]:
    """
    Regex/keyword signal search directly against LanceDB text_chunk field.
    Used when VECTOR_BACKEND is 'lancedb' or 'hybrid' to complement vector search.
    """
    terms = _extract_regex_signals(query)
    if not terms:
        return []

    all_rows = _fetch_lancedb_pandas_rows("regex search failed during table open")
    if all_rows is None:
        return []

    return _scan_lancedb_rows_for_terms(all_rows, terms, k)[:k]


# Function: _fetch_regex_term_matches
def _fetch_regex_term_matches(cur, term: str, score: float, k: int, has_trgm: bool) -> list:
    """Returns a list of (row_id, Document, blended_score) for one regex signal term."""
    matches: list = []
    if has_trgm:
        cur.execute(
            """
            SELECT id, document, metadata_json,
                   similarity(document, %s) AS trgm_score
            FROM vector_chunks
            WHERE collection_name = %s
              AND document %% %s
            ORDER BY trgm_score DESC
            LIMIT %s
            """,
            (term, VECTOR_COLLECTION, term, int(max(2, k))),
        )
        for row in cur.fetchall():
            trgm = float(row[3] or 0.0)
            blended = round(score * 0.75 + trgm * 0.25, 4)
            matches.append((row[0], Document(page_content=row[1] or "", metadata=row[2] or {}), blended))
    else:
        cur.execute(
            """
            SELECT id, document, metadata_json
            FROM vector_chunks
            WHERE collection_name = %s
              AND document ILIKE %s
            LIMIT %s
            """,
            (VECTOR_COLLECTION, f"%{term}%", int(max(2, k))),
        )
        for row in cur.fetchall():
            matches.append((row[0], Document(page_content=row[1] or "", metadata=row[2] or {}), float(score)))
    return matches


# Function: regex_signal_search
def regex_signal_search(
    query: str,
    provider: str = "ollama",
    k: int = 6,
) -> List[Tuple[Document, float]]:
    """
    Search the vector store using exact regex/key-parameter signals extracted from the query.
    Supports LanceDB (text scan), pgvector (ILIKE / pg_trgm), and hybrid backends.
    """
    del provider  # kept for call-site parity

    # For LanceDB backend: scan text_chunk field directly.
    if VECTOR_BACKEND in {"lancedb", "hybrid"}:
        lancedb_hits = _regex_signal_search_lancedb(query, k=k)
        logger.debug("regex_signal_search(lancedb): %d hits for query %.80s", len(lancedb_hits), query)
        if lancedb_hits:
            return lancedb_hits
        if VECTOR_BACKEND == "lancedb":
            return []
        # hybrid: also try pgvector below

    # Skip postgres when using Qdrant-only
    if VECTOR_BACKEND == "qdrant":
        return []

    terms = _extract_regex_signals(query)
    if not terms:
        return []
    has_trgm = _db_features().get("pg_trgm", False)

    results: list[Tuple[Document, float]] = []
    seen: set[str] = set()

    with get_connection() as conn:
        with conn.cursor() as cur:
            for term, score in terms:
                matches = _fetch_regex_term_matches(cur, term, score, k, has_trgm)
                if _merge_keyword_matches(matches, seen, results, k):
                    break
        conn.commit()

    return results[:k]


# Function: _build_lancedb_keyword_terms
def _build_lancedb_keyword_terms(query: str) -> list:
    """Extracts INC numbers, alphanumeric tokens and word terms for LanceDB keyword search."""
    inc_terms = [(t.upper(), 1.0) for t in re.findall(r"INC\d+", query, re.IGNORECASE)]
    alnum_terms = []
    seen_alnum: set[str] = set()
    for t in re.findall(r"\b(?=[A-Za-z0-9]{6,20}\b)(?=[A-Za-z0-9]*[A-Za-z])(?=[A-Za-z0-9]*\d)[A-Za-z0-9]+\b", query):
        if t.upper().startswith("INC"):
            continue
        key = t.lower()
        if key in seen_alnum:
            continue
        seen_alnum.add(key)
        alnum_terms.append((t, 0.90))
        if len(alnum_terms) >= 6:
            break
    word_terms = [
        (w, 0.75)
        for w in re.findall(r"\b[A-Za-z]{5,}\b", query)
        if w.lower() not in _KW_STOPWORDS
    ]
    return inc_terms + alnum_terms + word_terms[:4]


# Function: _keyword_search_lancedb
def _keyword_search_lancedb(query: str, k: int = 5) -> List[Tuple[Document, float]]:
    """
    BM25-style keyword search directly against LanceDB text_chunk field.
    Extracts INC numbers, SAP codes, alphanumeric tokens and word terms.
    """
    terms = _build_lancedb_keyword_terms(query)
    if not terms:
        return []

    all_rows = _fetch_lancedb_pandas_rows("keyword search failed")
    if all_rows is None:
        return []

    return _scan_lancedb_rows_for_terms(all_rows, terms, k)[:k]


# Function: keyword_search
def _extract_alnum_keyword_terms(query: str, cap: int = 8) -> list:
    alnum_terms = []
    seen_alnum: set[str] = set()
    for t in re.findall(r"\b(?=[A-Za-z0-9]{6,20}\b)(?=[A-Za-z0-9]*[A-Za-z])(?=[A-Za-z0-9]*\d)[A-Za-z0-9]+\b", query):
        if t.upper().startswith("INC"):
            continue
        key = t.lower()
        if key in seen_alnum:
            continue
        seen_alnum.add(key)
        alnum_terms.append((t, 0.95))
        if len(alnum_terms) >= cap:
            break
    return alnum_terms


# Function: _build_keyword_search_terms
def _build_keyword_search_terms(query: str) -> list:
    inc_terms = [(t, 1.0) for t in re.findall(r"INC\d+", query, re.IGNORECASE)]
    phrase_terms = [(p.strip(), 0.95) for p in re.findall(r'"([^"]{6,120})"', query) if p.strip()]
    solman_terms = [(t, 0.95) for t in re.findall(r"\b7\d{9}\b", query)]
    delivery_terms = [(t, 0.85) for t in re.findall(r"\b1\d{8,11}\b", query)]
    alnum_terms = _extract_alnum_keyword_terms(query)
    error_code_terms = [(t, 0.9) for t in re.findall(r"(?i)\berror\s*[:#-]?\s*(\d{3,6})\b", query)]
    word_terms = [
        (w, 0.75)
        for w in re.findall(r"\b[A-Za-z]{5,}\b", query)
        if w.lower() not in _KW_STOPWORDS
    ]
    return inc_terms + phrase_terms + solman_terms + delivery_terms + alnum_terms + error_code_terms + word_terms[:4]


# Function: _fetch_keyword_term_matches
def _fetch_keyword_term_matches(cur, term: str, score: float, k: int, has_trgm: bool) -> list:
    """Returns a list of (row_id, Document, blended_score) for one search term."""
    matches: list = []
    # Use pg_trgm similarity for richer scoring when the extension is available,
    # falling back to plain ILIKE if not.
    if has_trgm:
        cur.execute(
            """
            SELECT id, document, metadata_json,
                   similarity(document, %s) AS trgm_score
            FROM vector_chunks
            WHERE collection_name = %s
              AND document %% %s
            ORDER BY trgm_score DESC
            LIMIT %s
            """,
            (term, VECTOR_COLLECTION, term, int(k)),
        )
        for row in cur.fetchall():
            # Blend declared keyword score with trigram similarity
            trgm = float(row[3] or 0.0)
            blended = round(score * 0.7 + trgm * 0.3, 4)
            matches.append((row[0], Document(page_content=row[1] or "", metadata=row[2] or {}), blended))
    else:
        # pg_trgm not available — fall back to ILIKE
        cur.execute(
            """
            SELECT id, document, metadata_json
            FROM vector_chunks
            WHERE collection_name = %s
              AND document ILIKE %s
            LIMIT %s
            """,
            (VECTOR_COLLECTION, f"%{term}%", int(k)),
        )
        for row in cur.fetchall():
            matches.append((row[0], Document(page_content=row[1] or "", metadata=row[2] or {}), float(score)))
    return matches


# Function: _merge_keyword_matches
def _merge_keyword_matches(matches: list, seen: set, results: list, k: int) -> bool:
    """Append deduped matches to results; returns True once results reach k."""
    for rid, doc, blended in matches:
        if rid in seen:
            continue
        seen.add(rid)
        results.append((doc, blended))
        if len(results) >= k:
            return True
    return False


# Function: keyword_search
def keyword_search(
    query: str,
    provider: str = "ollama",
    k: int = 5,
) -> List[Tuple[Document, float]]:
    # For LanceDB backend: scan text_chunk field directly
    if VECTOR_BACKEND in {"lancedb", "hybrid"}:
        lancedb_hits = _keyword_search_lancedb(query, k=k)
        logger.debug("keyword_search(lancedb): %d hits for query %.80s", len(lancedb_hits), query)
        if lancedb_hits:
            return lancedb_hits
        if VECTOR_BACKEND == "lancedb":
            return []
        # hybrid: fall through to pgvector

    # Skip expensive postgres keyword search when using Qdrant-only mode
    if VECTOR_BACKEND == "qdrant":
        return []

    has_trgm = _db_features().get("pg_trgm", False)
    terms = _build_keyword_search_terms(query)
    if not terms:
        return []

    results: list[Tuple[Document, float]] = []
    seen: set[str] = set()

    with get_connection() as conn:
        with conn.cursor() as cur:
            for term, score in terms:
                matches = _fetch_keyword_term_matches(cur, term, score, k, has_trgm)
                if _merge_keyword_matches(matches, seen, results, k):
                    break
        conn.commit()

    return results[:k]

