# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Phase 1 acceptance (Requirements.MD §10): '100% of generated requirements have >=1
# Date: 2025-09-28
# ---------------------------------------------------------------------------
"""Phase 1 acceptance (Requirements.MD §10): '100% of generated requirements have >=1
citation with a resolvable locator, verified by an automated test. Zero exceptions.'"""
from __future__ import annotations

import uuid
from types import SimpleNamespace

import pytest
from sqlalchemy.exc import DBAPIError

from traceforge.agents.ambiguity import score_requirement
from traceforge.agents.extractor import ExtractedCitation, _valid_unique_citations
from traceforge.db.models import Chunk, Requirement, SourceCitation, SourceDocument
from traceforge.db.session import SessionLocal


# Function: _make_indexed_chunk
async def _make_indexed_chunk(session, project) -> Chunk:
    doc = SourceDocument(
        project_id=project.id, source_type="UPLOAD", filename="t.docx", blob_uri="/tmp/t.docx",
        sha256="0" * 64, doc_class="AS_IS_DOC", status="INDEXED",
    )
    session.add(doc)
    await session.flush()
    chunk = Chunk(
        source_document_id=doc.id, project_id=project.id, ordinal=0, text="The system shall do X.",
        token_count=6, locator={"section": "1", "char_start": 0, "char_end": 20},
    )
    session.add(chunk)
    await session.flush()
    return chunk


# Function: _bare_requirement
def _bare_requirement(project_id: uuid.UUID) -> Requirement:
    return Requirement(
        req_id=f"REQ-{uuid.uuid4().hex[:6]}", project_id=project_id, level="FUNCTIONAL",
        title="t", statement="The system shall do X.", ears_pattern="UBIQUITOUS",
        ears_parts={"system_name": "System"}, acceptance_criteria=["X happens"],
        priority="SHOULD", ambiguity_score=0.0, ambiguity_flags=[], status="DRAFT",
        content_hash="deadbeef", version=1, created_by_agent=True,
    )


# Function: test_requirement_without_citation_is_rejected_by_db
async def test_requirement_without_citation_is_rejected_by_db(project):
    """The DB-level half of P1: a transaction committing a Requirement with zero
    SourceCitation rows must fail (DEFERRABLE constraint trigger, not app logic).
    Uses its own throwaway session/connection — once a commit raises, the
    connection is left aborted and must not be reused (see SQLAlchemy docs on
    PendingRollbackError recovery); a fresh session on exit is simplest and safest."""
    async with SessionLocal() as isolated:
        isolated.add(_bare_requirement(project.id))
        with pytest.raises(DBAPIError, match="P1 violation"):
            await isolated.commit()


# Function: test_requirement_with_citation_commits_and_locator_resolves
async def test_requirement_with_citation_commits_and_locator_resolves(session, project):
    chunk = await _make_indexed_chunk(session, project)
    requirement = _bare_requirement(project.id)
    session.add(requirement)
    await session.flush()
    session.add(SourceCitation(requirement_id=requirement.id, chunk_id=chunk.id, relevance=1.0, quoted_span="The system shall do X."))
    await session.commit()  # must NOT raise

    await session.refresh(requirement)
    assert requirement.id is not None
    assert chunk.locator["section"] == "1"  # the locator that makes the citation resolvable in the UI


# Function: test_duplicate_model_citations_are_collapsed_per_chunk
async def test_duplicate_model_citations_are_collapsed_per_chunk():
    chunk = SimpleNamespace(id=uuid.uuid4(), text="The system shall do X.")
    citations = [
        ExtractedCitation(chunk_id=str(chunk.id), quoted_span="The system shall do X."),
        ExtractedCitation(chunk_id=str(chunk.id), quoted_span="shall do X"),
        ExtractedCitation(chunk_id=str(uuid.uuid4()), quoted_span="hallucinated"),
    ]

    valid = _valid_unique_citations(citations, {str(chunk.id): chunk})

    assert len(valid) == 1
    assert valid[0].chunk_id == str(chunk.id)


def test_paraphrased_citation_is_repaired_to_exact_source_sentence():
    chunk = SimpleNamespace(
        id=uuid.uuid4(),
        text=(
            "The FSC Credit Mix balance must be verified before order creation and maintained "
            "accurately through to invoicing. Any imbalance blocks certification."
        ),
    )
    citation = ExtractedCitation(
        chunk_id=str(chunk.id),
        quoted_span="Before order creation, the FSC Credit Mix balance must be verified.",
    )

    valid = _valid_unique_citations([citation], {str(chunk.id): chunk})

    assert len(valid) == 1
    assert valid[0].quoted_span == (
        "The FSC Credit Mix balance must be verified before order creation and maintained "
        "accurately through to invoicing."
    )


# Function: test_ambiguity_scorer_flags_vague_term_and_compound
async def test_ambiguity_scorer_flags_vague_term_and_compound():
    score, flags = score_requirement(
        "The system shall be quick and flexible.",
        {"system_name": "System", "system_response": "be quick and flexible"},
        "UBIQUITOUS",
    )
    codes = {f.code for f in flags}
    assert "VAGUE_TERM" in codes  # 'quick'/'flexible' are literal entries in AMBIGUITY_RULES's VAGUE_TERM regex
    assert "COMPOUND" in codes    # 'and' in the response clause
    assert score > 0.0


# Function: test_ambiguity_scorer_no_actor_when_system_name_missing
async def test_ambiguity_scorer_no_actor_when_system_name_missing():
    score, flags = score_requirement("The system shall do X.", {"system_name": None}, "UBIQUITOUS")
    assert any(f.code == "NO_ACTOR" for f in flags)


# Function: test_ambiguity_scorer_non_conformant_pattern
async def test_ambiguity_scorer_non_conformant_pattern():
    score, flags = score_requirement("This is not an EARS sentence at all.", {}, "SOMETHING_ELSE")
    assert any(f.code == "NON_CONFORMANT" for f in flags)
    assert score >= 0.3


# Function: test_ambiguity_scorer_skips_actor_and_ears_checks_for_assumptions
async def test_ambiguity_scorer_skips_actor_and_ears_checks_for_assumptions():
    """ASSUMPTION/CONSTRAINT-level statements describe external facts, not system
    behaviour — they can never have a <system> actor or fit an EARS pattern, so scoring
    them against those rules would flag every single one regardless of actual quality."""
    score, flags = score_requirement(
        "Third-party systems will provide required APIs within agreed timelines.",
        {"system_name": None}, "SOMETHING_ELSE", level="ASSUMPTION",
    )
    codes = {f.code for f in flags}
    assert "NO_ACTOR" not in codes
    assert "NON_CONFORMANT" not in codes
    assert score == 0.0
