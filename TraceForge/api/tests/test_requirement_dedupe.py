# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: §5 Agent 1 'Additional passes' — Deduplication: 'cluster requirements by
#   embedding cosine > 0.92, merge, union their citations.'
# Date: 2026-07-24
# ---------------------------------------------------------------------------
from __future__ import annotations

from sqlalchemy import select

from traceforge.agents.dedupe import deduplicate_requirements
from traceforge.db.models import Chunk, Requirement, SourceCitation, SourceDocument


# Function: fake_embed_texts
async def fake_embed_texts(texts: list[str]) -> list[list[float]]:
    """Deterministic stand-in for the real Ollama embedding call: statements about
    validation cluster on one axis, statements about archiving on another, so the two
    'validate' requirements are near-identical (cosine 1.0) and the 'archive' one is
    orthogonal (cosine 0.0) — independent of any input ordering."""
    return [[1.0, 0.0, 0.0] if "validate" in text else [0.0, 1.0, 0.0] for text in texts]


# Function: _make_chunk
async def _make_chunk(session, project, ordinal: int, text: str) -> Chunk:
    doc = SourceDocument(
        project_id=project.id, source_type="UPLOAD", filename=f"doc{ordinal}.docx",
        blob_uri=f"/tmp/doc{ordinal}.docx", sha256=f"{ordinal}" * 64, doc_class="AS_IS_DOC", status="INDEXED",
    )
    session.add(doc)
    await session.flush()
    chunk = Chunk(
        source_document_id=doc.id, project_id=project.id, ordinal=0, text=text,
        token_count=10, locator={"section": str(ordinal)},
    )
    session.add(chunk)
    await session.flush()
    return chunk


# Function: _draft_requirement
def _draft_requirement(project_id, req_id: str, statement: str) -> Requirement:
    return Requirement(
        req_id=req_id, project_id=project_id, level="FUNCTIONAL", title=req_id,
        statement=statement, ears_pattern="UBIQUITOUS", ears_parts={"system_name": "System"},
        acceptance_criteria=["Order is validated"], priority="SHOULD", ambiguity_score=0.0,
        ambiguity_flags=[], status="DRAFT", content_hash=f"hash-{req_id}", version=1, created_by_agent=True,
    )


# Function: test_deduplicate_merges_near_identical_statements_and_unions_citations
async def test_deduplicate_merges_near_identical_statements_and_unions_citations(session, project, monkeypatch):
    monkeypatch.setattr("traceforge.agents.dedupe.embed_texts", fake_embed_texts)

    chunk_a = await _make_chunk(session, project, 1, "Orders must be validated quickly.")
    chunk_b = await _make_chunk(session, project, 2, "Orders must be validated within limits.")
    chunk_c = await _make_chunk(session, project, 3, "Completed orders are archived after 90 days.")

    req1 = _draft_requirement(project.id, "REQ-0001", "The System shall validate customer orders within 2 seconds.")
    req2 = _draft_requirement(project.id, "REQ-0002", "The System shall validate customer orders within two seconds.")
    req3 = _draft_requirement(project.id, "REQ-0003", "The System shall archive completed orders after 90 days.")
    session.add_all([req1, req2, req3])
    await session.flush()
    session.add(SourceCitation(requirement_id=req1.id, chunk_id=chunk_a.id, relevance=1.0, quoted_span="Orders must be validated quickly."))
    session.add(SourceCitation(requirement_id=req2.id, chunk_id=chunk_b.id, relevance=1.0, quoted_span="Orders must be validated within limits."))
    session.add(SourceCitation(requirement_id=req3.id, chunk_id=chunk_c.id, relevance=1.0, quoted_span="Completed orders are archived after 90 days."))
    await session.commit()

    summary = await deduplicate_requirements(session, project.id)
    await session.commit()

    assert summary.merged_count == 1
    assert summary.merges == [{"canonical_req_id": "REQ-0001", "merged_req_id": "REQ-0002"}]

    await session.refresh(req1)
    await session.refresh(req2)
    await session.refresh(req3)
    assert req1.status == "DRAFT"
    assert req2.status == "SUPERSEDED"
    assert req2.merged_into_id == req1.id
    assert req3.status == "DRAFT"  # not similar enough to either -> untouched
    assert req3.merged_into_id is None

    # Citations union onto the canonical requirement rather than being lost.
    result = await session.execute(select(SourceCitation.chunk_id).where(SourceCitation.requirement_id == req1.id))
    assert set(result.scalars().all()) == {chunk_a.id, chunk_b.id}

    # The superseded requirement's own citation rows are preserved, not deleted (P5).
    result = await session.execute(select(SourceCitation.chunk_id).where(SourceCitation.requirement_id == req2.id))
    assert set(result.scalars().all()) == {chunk_b.id}


# Function: test_deduplicate_leaves_approved_requirements_untouched
async def test_deduplicate_leaves_approved_requirements_untouched(session, project, monkeypatch):
    """P4: nothing a human has already adjudicated gets silently merged away — the
    pass only ever looks at DRAFT requirements."""
    monkeypatch.setattr("traceforge.agents.dedupe.embed_texts", fake_embed_texts)

    chunk = await _make_chunk(session, project, 1, "Orders must be validated quickly.")
    req1 = _draft_requirement(project.id, "REQ-0001", "The System shall validate customer orders within 2 seconds.")
    req1.status = "APPROVED"
    req2 = _draft_requirement(project.id, "REQ-0002", "The System shall validate customer orders within two seconds.")
    req2.status = "APPROVED"
    session.add_all([req1, req2])
    await session.flush()
    session.add(SourceCitation(requirement_id=req1.id, chunk_id=chunk.id, relevance=1.0, quoted_span="Orders must be validated quickly."))
    session.add(SourceCitation(requirement_id=req2.id, chunk_id=chunk.id, relevance=1.0, quoted_span="Orders must be validated quickly."))
    await session.commit()

    summary = await deduplicate_requirements(session, project.id)

    assert summary.merged_count == 0
    await session.refresh(req1)
    await session.refresh(req2)
    assert req1.status == "APPROVED"
    assert req2.status == "APPROVED"
