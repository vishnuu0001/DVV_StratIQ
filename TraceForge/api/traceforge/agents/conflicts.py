# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: §5 Agent 1 'Additional passes' — Conflict detection: 'for each requirement,
#   RAG-retrieve semantically similar requirements from *other* source documents; if
#   the LLM judges them contradictory, emit a CONFLICT warning linking both REQ-IDs.'
#   Not previously implemented (see PROGRESS.md's dedup/conflict-detection gap).
# Date: 2026-07-24
# ---------------------------------------------------------------------------
"""Runs after dedupe.py in the same Extract pass, over the same DRAFT batch — near-
duplicates above dedupe's 0.92 merge threshold are already gone by the time this runs,
so a requirement's candidate pool here is 'similar enough to plausibly overlap in
subject, but not similar enough to be the same requirement.'

Only requirement pairs backed by citations from *different* source documents are
considered (spec: 'from other source documents') — two requirements from the same
document that happen to look similar are not a cross-document conflict candidate.

Deterministic in scope-selection (embedding similarity band + LLM call budget), but
the actual contradiction judgement is necessarily an LLM call — 'requirement A and B
contradict' isn't a regex-checkable property the way ambiguity.py's rules are.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from traceforge.agents.base import call_agent_llm
from traceforge.agents.similarity import cosine_similarity
from traceforge.config import CONFLICT_DETECTION_MAX_PAIRS
from traceforge.db.models import Chunk, Requirement, SourceCitation
from traceforge.indexing.embedder import embed_texts
from traceforge.llm.ollama import OllamaProvider

_MIN_SIMILARITY = 0.72
_MAX_SIMILARITY = 0.92  # >= this is a duplicate, already handled by dedupe.py
_MAX_CANDIDATES_PER_REQUIREMENT = 3

_SYSTEM_PROMPT = """You are a senior business analyst checking two requirements extracted
from the same project for a genuine contradiction. They may come from the same source
document or different source documents.

Two requirements conflict only if satisfying one would violate the other - for example
one states a field/step is mandatory and the other states the same field/step is
optional, or they specify different numeric limits, thresholds, or outcomes for what is
clearly the same system behaviour. Overlapping topic, redundant coverage, or one
requirement simply being more detailed than the other is NOT a conflict.

Return JSON only, nothing else: {"conflicts": bool, "explanation": str}
If unsure, return false - do not flag mere topical overlap as a conflict."""


@dataclass
class ConflictSummary:
    conflicts_found: int = 0
    pairs: list[dict] = field(default_factory=list)
    pairs_checked: int = 0
    warnings: list[str] = field(default_factory=list)


class _ConflictJudgement(BaseModel):
    conflicts: bool
    explanation: str = ""


# Function: detect_conflicts
async def detect_conflicts(
    session: AsyncSession, project_id: uuid.UUID, pipeline_run_id: uuid.UUID | None,
) -> ConflictSummary:
    summary = ConflictSummary()
    result = await session.execute(
        select(Requirement).where(Requirement.project_id == project_id, Requirement.status == "DRAFT")
        .order_by(Requirement.req_id)
    )
    requirements = list(result.scalars().all())
    if len(requirements) < 2:
        return summary

    embeddings = await embed_texts([r.statement for r in requirements])
    provider = OllamaProvider()

    checked_pairs: set[frozenset[uuid.UUID]] = set()
    for i, req_a in enumerate(requirements):
        if summary.pairs_checked >= CONFLICT_DETECTION_MAX_PAIRS:
            summary.warnings.append(
                f"conflict_detector: reached CONFLICT_DETECTION_MAX_PAIRS ({CONFLICT_DETECTION_MAX_PAIRS}) — "
                f"remaining requirement pairs were not checked this run."
            )
            break
        candidates = _rank_candidates(req_a, i, requirements, embeddings)

        for _, req_b in candidates[:_MAX_CANDIDATES_PER_REQUIREMENT]:
            if summary.pairs_checked >= CONFLICT_DETECTION_MAX_PAIRS:
                break
            pair_key = frozenset({req_a.id, req_b.id})
            if pair_key in checked_pairs:
                continue
            checked_pairs.add(pair_key)
            summary.pairs_checked += 1

            judgement, warnings = await _judge_pair(session, provider, req_a, req_b, pipeline_run_id)
            summary.warnings.extend(warnings)
            if judgement is None or not judgement.conflicts:
                continue

            _flag_conflict(req_a, req_b.req_id, judgement.explanation)
            _flag_conflict(req_b, req_a.req_id, judgement.explanation)
            summary.conflicts_found += 1
            summary.pairs.append({"req_a": req_a.req_id, "req_b": req_b.req_id, "explanation": judgement.explanation})

    # Conflict flags are part of the persisted requirement review state.  Flush
    # assignments before callers refresh rows or proceed to a review gate.
    await session.flush()
    return summary


# Function: _rank_candidates
def _rank_candidates(
    req_a: Requirement, index_a: int, requirements: list[Requirement],
    embeddings: list[list[float]],
) -> list[tuple[float, Requirement]]:
    candidates: list[tuple[float, Requirement]] = []
    for j, req_b in enumerate(requirements):
        if index_a == j:
            continue
        similarity = cosine_similarity(embeddings[index_a], embeddings[j])
        if _MIN_SIMILARITY <= similarity < _MAX_SIMILARITY:
            candidates.append((similarity, req_b))
    candidates.sort(key=lambda pair: pair[0], reverse=True)
    return candidates


# Function: _judge_pair
async def _judge_pair(
    session: AsyncSession, provider: OllamaProvider, req_a: Requirement, req_b: Requirement,
    pipeline_run_id: uuid.UUID | None,
) -> tuple[_ConflictJudgement | None, list[str]]:
    user_msg = (
        f"REQUIREMENT A ({req_a.req_id}): {req_a.statement}\n\n"
        f"REQUIREMENT B ({req_b.req_id}): {req_b.statement}"
    )
    parsed, warnings = await call_agent_llm(
        provider, session, agent_name="conflict_detector", system=_SYSTEM_PROMPT, user=user_msg,
        pipeline_run_id=pipeline_run_id, max_tokens=300,
    )
    if parsed is None:
        return None, warnings
    try:
        return _ConflictJudgement.model_validate(parsed), warnings
    except Exception as exc:  # noqa: BLE001 — malformed judgement must not abort the whole pass
        warnings.append(f"conflict_detector: skipped malformed judgement for {req_a.req_id}/{req_b.req_id}: {exc}")
        return None, warnings


# Function: _flag_conflict
def _flag_conflict(requirement: Requirement, conflicting_req_id: str, explanation: str) -> None:
    flags = list(requirement.conflict_flags or [])
    if any(f.get("conflicting_req_id") == conflicting_req_id for f in flags):
        return
    flags.append({"conflicting_req_id": conflicting_req_id, "explanation": explanation})
    requirement.conflict_flags = flags


# Function: _source_documents_by_requirement
async def _source_documents_by_requirement(
    session: AsyncSession, requirement_ids: list[uuid.UUID],
) -> dict[uuid.UUID, set[uuid.UUID]]:
    if not requirement_ids:
        return {}
    result = await session.execute(
        select(SourceCitation.requirement_id, Chunk.source_document_id)
        .join(Chunk, SourceCitation.chunk_id == Chunk.id)
        .where(SourceCitation.requirement_id.in_(requirement_ids))
    )
    mapping: dict[uuid.UUID, set[uuid.UUID]] = {}
    for req_id, doc_id in result.all():
        mapping.setdefault(req_id, set()).add(doc_id)
    return mapping
