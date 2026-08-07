# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: §5 Agent 1 'Additional passes' — Conflict detection: 'for each requirement,
#   RAG-retrieve semantically similar requirements from *other* source documents; if
#   the LLM judges them contradictory, emit a CONFLICT warning linking both REQ-IDs.'
# Date: 2026-07-24
# ---------------------------------------------------------------------------
from __future__ import annotations

from traceforge.agents.conflicts import detect_conflicts
from traceforge.db.models import Chunk, Requirement, SourceCitation, SourceDocument
from traceforge.llm.provider import LLMResponse

_STATEMENT_ID_REQUIRED = "The System shall require photo ID for withdrawals over $500."
_STATEMENT_ID_WAIVED = "The System shall waive ID checks for withdrawals under $1000."

_VECTORS = {
    _STATEMENT_ID_REQUIRED: [1.0, 0.0],
    _STATEMENT_ID_WAIVED: [0.8, 0.6],   # cosine 0.8 vs REQUIRED — in-band candidate similarity
}


# Function: fake_embed_texts
async def fake_embed_texts(texts: list[str]) -> list[list[float]]:
    return [_VECTORS[text] for text in texts]


# Function: _fake_generate_conflict
async def _fake_generate_conflict(self, system, user, *, temperature, max_tokens, json_mode=True, progress=None):
    return LLMResponse(
        text='{"conflicts": true, "explanation": "One requires ID, the other waives it for an overlapping amount."}',
        model="test-model", prompt_tokens=10, completion_tokens=8, latency_ms=1,
    )


# Function: _fake_generate_no_conflict
async def _fake_generate_no_conflict(self, system, user, *, temperature, max_tokens, json_mode=True, progress=None):
    return LLMResponse(text='{"conflicts": false, "explanation": ""}', model="test-model", prompt_tokens=5, completion_tokens=3, latency_ms=1)


# Function: _fake_generate_must_not_be_called
async def _fake_generate_must_not_be_called(self, system, user, *, temperature, max_tokens, json_mode=True, progress=None):
    raise AssertionError("LLM should never be called for a same-source-document candidate pair")


# Function: _make_doc_and_chunk
async def _make_doc_and_chunk(session, project, suffix: str, text: str) -> Chunk:
    doc = SourceDocument(
        project_id=project.id, source_type="UPLOAD", filename=f"doc-{suffix}.docx",
        blob_uri=f"/tmp/doc-{suffix}.docx", sha256=f"{suffix}" * 8, doc_class="AS_IS_DOC", status="INDEXED",
    )
    session.add(doc)
    await session.flush()
    chunk = Chunk(source_document_id=doc.id, project_id=project.id, ordinal=0, text=text, token_count=10, locator={})
    session.add(chunk)
    await session.flush()
    return chunk


# Function: _draft_requirement
def _draft_requirement(project_id, req_id: str, statement: str) -> Requirement:
    return Requirement(
        req_id=req_id, project_id=project_id, level="FUNCTIONAL", title=req_id,
        statement=statement, ears_pattern="UBIQUITOUS", ears_parts={"system_name": "System"},
        acceptance_criteria=["Checked"], priority="SHOULD", ambiguity_score=0.0,
        ambiguity_flags=[], status="DRAFT", content_hash=f"hash-{req_id}", version=1, created_by_agent=True,
    )


# Function: test_detect_conflicts_flags_cross_document_pair_symmetrically
async def test_detect_conflicts_flags_cross_document_pair_symmetrically(session, project, monkeypatch):
    monkeypatch.setattr("traceforge.agents.conflicts.embed_texts", fake_embed_texts)
    monkeypatch.setattr("traceforge.llm.ollama.OllamaProvider.generate", _fake_generate_conflict)

    chunk_1 = await _make_doc_and_chunk(session, project, "1", "ID required over $500.")
    chunk_2 = await _make_doc_and_chunk(session, project, "2", "ID waived under $1000.")

    req1 = _draft_requirement(project.id, "REQ-0001", _STATEMENT_ID_REQUIRED)
    req2 = _draft_requirement(project.id, "REQ-0002", _STATEMENT_ID_WAIVED)
    session.add_all([req1, req2])
    await session.flush()
    session.add(SourceCitation(requirement_id=req1.id, chunk_id=chunk_1.id, relevance=1.0, quoted_span="ID required over $500."))
    session.add(SourceCitation(requirement_id=req2.id, chunk_id=chunk_2.id, relevance=1.0, quoted_span="ID waived under $1000."))
    await session.commit()

    summary = await detect_conflicts(session, project.id, pipeline_run_id=None)

    assert summary.conflicts_found == 1
    assert summary.pairs == [{
        "req_a": "REQ-0001", "req_b": "REQ-0002",
        "explanation": "One requires ID, the other waives it for an overlapping amount.",
    }]

    await session.refresh(req1)
    await session.refresh(req2)
    assert req1.conflict_flags == [{
        "conflicting_req_id": "REQ-0002",
        "explanation": "One requires ID, the other waives it for an overlapping amount.",
    }]
    assert req2.conflict_flags == [{
        "conflicting_req_id": "REQ-0001",
        "explanation": "One requires ID, the other waives it for an overlapping amount.",
    }]


# Function: test_detect_conflicts_does_not_flag_when_llm_finds_no_contradiction
async def test_detect_conflicts_does_not_flag_when_llm_finds_no_contradiction(session, project, monkeypatch):
    monkeypatch.setattr("traceforge.agents.conflicts.embed_texts", fake_embed_texts)
    monkeypatch.setattr("traceforge.llm.ollama.OllamaProvider.generate", _fake_generate_no_conflict)

    chunk_1 = await _make_doc_and_chunk(session, project, "3", "ID required over $500.")
    chunk_2 = await _make_doc_and_chunk(session, project, "4", "ID waived under $1000.")
    req1 = _draft_requirement(project.id, "REQ-0001", _STATEMENT_ID_REQUIRED)
    req2 = _draft_requirement(project.id, "REQ-0002", _STATEMENT_ID_WAIVED)
    session.add_all([req1, req2])
    await session.flush()
    session.add(SourceCitation(requirement_id=req1.id, chunk_id=chunk_1.id, relevance=1.0, quoted_span="ID required over $500."))
    session.add(SourceCitation(requirement_id=req2.id, chunk_id=chunk_2.id, relevance=1.0, quoted_span="ID waived under $1000."))
    await session.commit()

    summary = await detect_conflicts(session, project.id, pipeline_run_id=None)

    assert summary.conflicts_found == 0
    await session.refresh(req1)
    await session.refresh(req2)
    assert req1.conflict_flags == []
    assert req2.conflict_flags == []


# Function: test_detect_conflicts_ignores_same_document_candidates
async def test_detect_conflicts_checks_same_document_candidates(session, project, monkeypatch):
    """spec: candidates must come from *other* source documents — two requirements
    with an in-band similarity (the same pair of statements/vectors the cross-document
    test proves gets checked) are never sent to the LLM when they cite the same
    document instead of different ones."""
    monkeypatch.setattr("traceforge.agents.conflicts.embed_texts", fake_embed_texts)
    monkeypatch.setattr("traceforge.llm.ollama.OllamaProvider.generate", _fake_generate_conflict)

    chunk = await _make_doc_and_chunk(session, project, "5", "ID required over $500, waived under $1000.")
    req1 = _draft_requirement(project.id, "REQ-0001", _STATEMENT_ID_REQUIRED)
    req2 = _draft_requirement(project.id, "REQ-0002", _STATEMENT_ID_WAIVED)
    session.add_all([req1, req2])
    await session.flush()
    session.add(SourceCitation(requirement_id=req1.id, chunk_id=chunk.id, relevance=1.0, quoted_span="ID required over $500."))
    session.add(SourceCitation(requirement_id=req2.id, chunk_id=chunk.id, relevance=1.0, quoted_span="waived under $1000."))
    await session.commit()

    summary = await detect_conflicts(session, project.id, pipeline_run_id=None)

    assert summary.pairs_checked == 1
    assert summary.conflicts_found == 1
