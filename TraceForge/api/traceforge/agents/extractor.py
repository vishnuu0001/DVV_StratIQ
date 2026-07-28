# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: §5 Agent 1 — Requirement Extractor.
# Date: 2026-07-10
# ---------------------------------------------------------------------------
"""§5 Agent 1 — Requirement Extractor.

Retrieval strategy per spec: do NOT RAG-query for requirements (you'd miss coverage).
Sweep the entire corpus instead — every chunk of a source document, in document order,
batched (default 20 chunks/call). RAG is reserved for the later enrichment/conflict pass
(not implemented this phase — see PROGRESS.md for dedup/conflict-detection status).
"""
from __future__ import annotations

import hashlib
import json
import logging
import uuid
from collections.abc import Awaitable, Callable

from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from traceforge.agents.ambiguity import score_requirement
from traceforge.agents.base import batched, call_agent_llm
from traceforge.agents.ears import EARS_PATTERNS, EARS_REFERENCE
from traceforge.config import AGENT_BATCH_SIZE_CHUNKS, EXTRACT_MAX_TOKENS, EXTRACT_RAG_TOP_K
from traceforge.db.ids import allocate_next_id
from traceforge.db.models import Chunk, Requirement, SourceCitation
from traceforge.indexing.retriever import hybrid_search
from traceforge.llm.ollama import OllamaProvider

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """You are a senior business analyst extracting requirements from enterprise source material.

You will receive numbered source chunks. Extract every distinct requirement that the source
material states or clearly implies. Do not invent requirements. Do not extrapolate industry
best practice. If the source does not support it, it does not exist.

For each requirement:
- Write ONE atomic statement using exactly one EARS pattern (definitions below).
- Use the exact system name from the provided glossary. If no system can be resolved,
  set system_name to null - do NOT guess.
- Cite the chunk id(s) that support it and include the verbatim supporting span from each.
- Classify: level (BUSINESS|FUNCTIONAL|NON_FUNCTIONAL|CONSTRAINT|ASSUMPTION), priority
  (MUST|SHOULD|COULD|WONT — MoSCoW, only if the source signals it, else SHOULD).
- Write 3-8 detailed acceptance criteria, each independently verifiable.
- Preserve every explicit functional step, alternate path, validation, business rule,
  integration response, and error outcome present in the source as an acceptance criterion.
- When the source provides an ordered workflow, acceptance criteria must retain that
  sequence and the exact field names, states, messages, codes, and expected outcomes.
- If the source is ambiguous, DO NOT resolve the ambiguity yourself - transcribe it faithfully.
  The downstream scorer will flag it and a human will fix it.
- Be concise in the atomic statement, but do not compress away functional detail from
  acceptance criteria. Title <= 10 words, statement <= 45 words, rationale <= 30 words.
- Cite each supporting chunk at most once per requirement and quote only the shortest
  source span that proves the requirement. Do not repeat the same requirement in
  different wording.

EARS PATTERNS:
{ears_reference}

GLOSSARY:
{glossary}

Return JSON matching this schema, and nothing else:
{{"requirements": [{{
  "title": str, "statement": str,
  "ears_pattern": "UBIQUITOUS|EVENT_DRIVEN|STATE_DRIVEN|OPTIONAL_FEATURE|UNWANTED_BEHAVIOUR|COMPLEX",
  "ears_parts": {{"trigger": str|null, "precondition": str|null, "system_name": str|null, "system_response": str}},
  "level": "BUSINESS|FUNCTIONAL|NON_FUNCTIONAL|CONSTRAINT|ASSUMPTION",
  "priority": "MUST|SHOULD|COULD|WONT",
  "rationale": str,
  "acceptance_criteria": [str, ...],
  "citations": [{{"chunk_id": str, "quoted_span": str}}, ...]
}}]}}"""


class ExtractedCitation(BaseModel):
    chunk_id: str
    quoted_span: str


class ExtractedRequirement(BaseModel):
    title: str
    statement: str
    ears_pattern: str
    ears_parts: dict = Field(default_factory=dict)
    level: str
    priority: str = "SHOULD"
    rationale: str | None = None
    acceptance_criteria: list[str] = Field(default_factory=list)
    citations: list[ExtractedCitation] = Field(default_factory=list)


class ExtractSummary(BaseModel):
    requirements_created: int = 0
    requirements_rejected_no_citation: int = 0
    duplicates_skipped: int = 0
    rag_chunks_retrieved: int = 0
    warnings: list[str] = Field(default_factory=list)


# Function: _content_hash
def _content_hash(statement: str, acceptance_criteria: list[str]) -> str:
    payload = json.dumps({"statement": statement, "acceptance_criteria": acceptance_criteria}, sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


# Function: _format_chunks_for_prompt
def _format_chunks_for_prompt(chunks: list[Chunk]) -> str:
    return "\n\n".join(f"[chunk_id={c.id}]\n{c.text}" for c in chunks)


# Function: _valid_unique_citations
def _valid_unique_citations(
    citations: list[ExtractedCitation], chunk_by_id: dict[str, Chunk],
) -> list[ExtractedCitation]:
    """Keep one citation per source chunk. Models can legitimately quote multiple
    spans from the same chunk, but the traceability schema has one edge per
    requirement/chunk pair and rejects duplicate edges."""
    unique: dict[str, ExtractedCitation] = {}
    for citation in citations:
        if citation.chunk_id in chunk_by_id and citation.chunk_id not in unique:
            unique[citation.chunk_id] = citation
    return list(unique.values())


# Function: _augment_with_rag_chunks
async def _augment_with_rag_chunks(
    session: AsyncSession, project_id: uuid.UUID, batch: list[Chunk], summary: ExtractSummary,
) -> tuple[list[Chunk], dict[str, Chunk]]:
    """Preserve the full-corpus sweep for completeness, then enrich each map batch
    with hybrid pgvector/BM25 context. This supplies cross-document supporting
    details without allowing RAG ranking to hide any source chunk from extraction."""
    rag_query = " ".join(c.text[:500] for c in batch)[:2000]
    rag_chunks = await hybrid_search(session, project_id, rag_query, top_k=EXTRACT_RAG_TOP_K)
    prompt_chunks = list(batch)
    seen_ids = {c.id for c in prompt_chunks}
    for chunk in rag_chunks:
        if chunk.id not in seen_ids:
            prompt_chunks.append(chunk)
            seen_ids.add(chunk.id)
            summary.rag_chunks_retrieved += 1
    chunk_by_id = {str(c.id): c for c in prompt_chunks}
    return prompt_chunks, chunk_by_id


# Function: _process_extracted_item
async def _process_extracted_item(
    raw: dict,
    chunk_by_id: dict[str, Chunk],
    session: AsyncSession,
    project_id: uuid.UUID,
    summary: ExtractSummary,
) -> None:
    try:
        extracted = ExtractedRequirement.model_validate(raw)
    except Exception as exc:  # noqa: BLE001 — one bad item must not drop the whole batch
        summary.warnings.append(f"extractor: skipped malformed item: {exc}")
        return

    # P1 API-level validator: citations must be non-empty AND reference chunks
    # actually shown to the model in this batch (never trust a hallucinated id).
    valid_citations = _valid_unique_citations(extracted.citations, chunk_by_id)
    if not valid_citations:
        summary.requirements_rejected_no_citation += 1
        summary.warnings.append(f"extractor: rejected '{extracted.title}' — no resolvable citation")
        return

    ambiguity_score, flags = score_requirement(
        extracted.statement, extracted.ears_parts, extracted.ears_pattern, level=extracted.level,
    )
    content_hash = _content_hash(extracted.statement, extracted.acceptance_criteria)
    existing = await session.scalar(
        select(Requirement.id).where(
            Requirement.project_id == project_id,
            Requirement.content_hash == content_hash,
        ).limit(1)
    )
    if existing:
        summary.duplicates_skipped += 1
        return
    req_id = await allocate_next_id(session, project_id, "REQ")

    requirement = Requirement(
        req_id=req_id,
        project_id=project_id,
        level=extracted.level,
        title=extracted.title,
        statement=extracted.statement,
        ears_pattern=extracted.ears_pattern if extracted.ears_pattern in EARS_PATTERNS else "NON_CONFORMANT",
        ears_parts=extracted.ears_parts,
        rationale=extracted.rationale,
        acceptance_criteria=extracted.acceptance_criteria,
        priority=extracted.priority,
        ambiguity_score=ambiguity_score,
        ambiguity_flags=[f.__dict__ for f in flags],
        status="DRAFT",
        content_hash=content_hash,
        version=1,
        created_by_agent=True,
    )
    session.add(requirement)
    await session.flush()  # assigns requirement.id, needed for the citation FK below

    for citation in valid_citations:
        chunk = chunk_by_id[citation.chunk_id]
        session.add(
            SourceCitation(
                requirement_id=requirement.id,
                chunk_id=chunk.id,
                relevance=1.0,
                quoted_span=citation.quoted_span,
            )
        )
    summary.requirements_created += 1


# Function: run_extractor
async def run_extractor(
    session: AsyncSession,
    *,
    project_id: uuid.UUID,
    chunks: list[Chunk],
    glossary: list[str],
    pipeline_run_id: uuid.UUID | None,
    progress: Callable[[int, int, ExtractSummary, str, int], Awaitable[None]] | None = None,
) -> ExtractSummary:
    """Sweeps `chunks` (already ordered by source document, then ordinal) in batches,
    persisting one Requirement + >=1 SourceCitation per extracted item inside a single
    transaction per batch (so the P1 DEFERRABLE constraint trigger sees both halves
    before commit). Requirements with zero valid citations are rejected outright — the
    API-level half of P1's 'DB constraint + API validator' enforcement."""
    provider = OllamaProvider()
    summary = ExtractSummary()
    glossary_text = ", ".join(glossary) if glossary else "(none extracted yet)"

    batches = list(batched(chunks, AGENT_BATCH_SIZE_CHUNKS))
    total_batches = len(batches)

    async def process_batch(batch: list[Chunk], batch_number: int, emit_progress: bool = True) -> None:
        if emit_progress and progress:
            await progress(batch_number, total_batches, summary, "generating", 0)

        prompt_chunks, chunk_by_id = await _augment_with_rag_chunks(session, project_id, batch, summary)
        system = _SYSTEM_PROMPT.format(ears_reference=EARS_REFERENCE, glossary=glossary_text)
        user = _format_chunks_for_prompt(prompt_chunks)

        # Function: stream_progress
        async def stream_progress(response_chunks: int) -> None:
            if emit_progress and progress:
                await progress(batch_number, total_batches, summary, "streaming", response_chunks)

        parsed, warnings = await call_agent_llm(
            provider, session, agent_name="extractor", system=system, user=user, pipeline_run_id=pipeline_run_id,
            max_tokens=EXTRACT_MAX_TOKENS, progress=stream_progress,
        )
        summary.warnings.extend(warnings)
        if parsed is None:
            if len(batch) > 1:
                split_at = max(1, len(batch) // 2)
                summary.warnings.append(
                    f"extractor: splitting {len(batch)} chunks into {split_at} + {len(batch) - split_at} after JSON failure"
                )
                await process_batch(batch[:split_at], batch_number, emit_progress=False)
                await process_batch(batch[split_at:], batch_number, emit_progress=False)
                if emit_progress and progress:
                    await progress(batch_number, total_batches, summary, "completed", 0)
            return

        raw_items = parsed.get("requirements", []) if isinstance(parsed, dict) else []
        for raw in raw_items:
            await _process_extracted_item(raw, chunk_by_id, session, project_id, summary)

        await session.commit()  # commits the batch — this is where trg_requirement_has_citation fires
        if emit_progress and progress:
            await progress(batch_number, total_batches, summary, "completed", 0)

    for batch_number, batch in enumerate(batches, start=1):
        await process_batch(batch, batch_number)

    return summary
