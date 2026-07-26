# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: §5 Agent 1 'Additional passes' — Deduplication: 'cluster requirements by
#   embedding cosine > 0.92, merge, union their citations.' Previously only exact
#   content_hash matches were caught (see extractor.py's duplicates_skipped) — two
#   requirements worded differently but describing the same behaviour sailed straight
#   through, which is exactly what re-running Extract against the same corpus does
#   (documented as a known rough edge in PROGRESS.md until this pass).
# Date: 2026-07-24
# ---------------------------------------------------------------------------
"""Runs over DRAFT requirements only, right after extraction and before Gate 1 —
APPROVED/SUPERSEDED/REJECTED/SUSPECT requirements are never touched by this pass
(P4: nothing a human has already adjudicated gets silently merged away).

'Merge' never deletes a row (P5): the duplicate is marked SUPERSEDED with
merged_into_id pointing at the surviving canonical requirement, and its citations are
unioned onto the canonical requirement so nothing 'the model was shown but only wrote
under a different wording' is ever lost from the traceability spine.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from traceforge.agents.similarity import cosine_similarity
from traceforge.db.models import Requirement, SourceCitation
from traceforge.indexing.embedder import embed_texts

_SIMILARITY_THRESHOLD = 0.92


@dataclass
class DedupeSummary:
    merged_count: int = 0
    merges: list[dict] = field(default_factory=list)


# Function: deduplicate_requirements
async def deduplicate_requirements(session: AsyncSession, project_id: uuid.UUID) -> DedupeSummary:
    summary = DedupeSummary()
    result = await session.execute(
        select(Requirement)
        .where(Requirement.project_id == project_id, Requirement.status == "DRAFT")
        .order_by(Requirement.created_at, Requirement.req_id)
    )
    requirements = list(result.scalars().all())
    if len(requirements) < 2:
        return summary

    embeddings = await embed_texts([r.statement for r in requirements])
    merged_ids: set[uuid.UUID] = set()

    for i, canonical in enumerate(requirements):
        if canonical.id in merged_ids:
            continue
        for j in range(i + 1, len(requirements)):
            duplicate = requirements[j]
            if duplicate.id in merged_ids:
                continue
            if cosine_similarity(embeddings[i], embeddings[j]) < _SIMILARITY_THRESHOLD:
                continue
            await _merge_requirement(session, canonical, duplicate)
            merged_ids.add(duplicate.id)
            summary.merged_count += 1
            summary.merges.append({"canonical_req_id": canonical.req_id, "merged_req_id": duplicate.req_id})

    if summary.merged_count:
        await session.flush()
    return summary


# Function: _merge_requirement
async def _merge_requirement(session: AsyncSession, canonical: Requirement, duplicate: Requirement) -> None:
    """Union citations onto `canonical` (skipping chunks it already cites — the
    uq_citation_req_chunk constraint forbids a second edge to the same chunk), then
    supersede `duplicate` in place. Queries citations directly instead of the ORM
    relationship: both requirements were loaded via a plain select(), so
    `.citations` would trigger an async lazy-load and raise MissingGreenlet."""
    existing = await session.execute(select(SourceCitation.chunk_id).where(SourceCitation.requirement_id == canonical.id))
    existing_chunk_ids = set(existing.scalars().all())

    dup_citations = await session.execute(select(SourceCitation).where(SourceCitation.requirement_id == duplicate.id))
    for citation in dup_citations.scalars().all():
        if citation.chunk_id in existing_chunk_ids:
            continue
        session.add(SourceCitation(
            requirement_id=canonical.id, chunk_id=citation.chunk_id,
            relevance=citation.relevance, quoted_span=citation.quoted_span,
        ))
        existing_chunk_ids.add(citation.chunk_id)

    duplicate.status = "SUPERSEDED"
    duplicate.merged_into_id = canonical.id
