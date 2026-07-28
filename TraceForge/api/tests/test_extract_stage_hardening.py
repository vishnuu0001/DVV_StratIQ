# ---------------------------------------------------------------------------
# Author: GitHub Copilot
# Scope: TraceForge — extraction worker hardening regressions
# Date: 2026-07-28
# ---------------------------------------------------------------------------
from __future__ import annotations

import re

from sqlalchemy import select

from traceforge.agents.extractor import ExtractSummary
from traceforge.db.models import Chunk, Gate, PipelineRun, Requirement, SourceDocument
from traceforge.agents.extractor import run_extractor
from traceforge.workers.tasks import run_extract_stage


# Function: test_extract_stage_fails_closed_without_throwing_on_json_parse_failure
async def test_extract_stage_fails_closed_without_throwing_on_json_parse_failure(session, project, monkeypatch):
    source_document = SourceDocument(
        project_id=project.id,
        source_type="UPLOAD",
        filename="requirements.txt",
        blob_uri="/tmp/requirements.txt",
        sha256="a" * 64,
        doc_class="AS_IS_DOC",
        status="INDEXED",
    )
    session.add(source_document)
    await session.flush()
    session.add(
        Chunk(
            source_document_id=source_document.id,
            project_id=project.id,
            ordinal=0,
            text="The platform shall validate invoices.",
            token_count=5,
            locator={},
        )
    )

    run = PipelineRun(project_id=project.id, stage="EXTRACT", status="QUEUED", stats={})
    session.add(run)
    await session.commit()

    async def fake_run_extractor(*args, **kwargs):
        return ExtractSummary(
            requirements_created=0,
            warnings=[
                "extractor: JSON parse failure on attempt 2: Expecting property name enclosed in double quotes: line 1 column 2 (char 1)",
            ],
        )

    monkeypatch.setattr("traceforge.workers.tasks.run_extractor", fake_run_extractor)

    result = await run_extract_stage(None, str(run.id))

    await session.refresh(run)
    gates = (await session.execute(select(Gate).where(Gate.pipeline_run_id == run.id))).scalars().all()

    assert result["status"] == "FAILED"
    assert "invalid JSON after retry" in result["error"]
    assert run.status == "FAILED"
    assert run.error == result["error"]
    assert run.stats["phase"] == "extraction_failed"
    assert gates == []


# Function: test_run_extractor_splits_large_failures_into_smaller_batches
async def test_run_extractor_splits_large_failures_into_smaller_batches(session, project, monkeypatch):
    source_document = SourceDocument(
        project_id=project.id,
        source_type="UPLOAD",
        filename="requirements.txt",
        blob_uri="/tmp/requirements.txt",
        sha256="b" * 64,
        doc_class="AS_IS_DOC",
        status="INDEXED",
    )
    session.add(source_document)
    await session.flush()

    chunks = []
    for ordinal in range(4):
        chunk = Chunk(
            source_document_id=source_document.id,
            project_id=project.id,
            ordinal=ordinal,
            text=f"Chunk {ordinal + 1}: the platform shall validate invoices.",
            token_count=7,
            locator={},
        )
        session.add(chunk)
        chunks.append(chunk)
    await session.flush()

    async def fake_augment_with_rag_chunks(session, project_id, batch, summary):
        return batch, {str(chunk.id): chunk for chunk in batch}

    async def fake_call_agent_llm(provider, session, *, agent_name, system, user, pipeline_run_id, max_tokens, progress=None):
        chunk_ids = re.findall(r"\[chunk_id=([^\]]+)\]", user)
        if len(chunk_ids) > 2:
            return None, ["extractor: JSON parse failure on attempt 2: Unterminated string starting at: line 1 column 2 (char 1)"]
        requirement = {
            "title": f"Validate invoices from {chunk_ids[0][:8]}",
            "statement": f"The platform shall validate invoices in batch {chunk_ids[0][:8]}.",
            "ears_pattern": "UBIQUITOUS",
            "ears_parts": {
                "trigger": None,
                "precondition": None,
                "system_name": "Platform",
                "system_response": "validate invoices",
            },
            "level": "FUNCTIONAL",
            "priority": "SHOULD",
            "rationale": f"Source requirement from {chunk_ids[0][:8]}",
            "acceptance_criteria": [f"Invoices are validated for {chunk_ids[0][:8]}."] ,
            "citations": [{"chunk_id": chunk_ids[0], "quoted_span": "validate invoices"}],
        }
        return {"requirements": [requirement]}, []

    monkeypatch.setattr("traceforge.agents.extractor._augment_with_rag_chunks", fake_augment_with_rag_chunks)
    monkeypatch.setattr("traceforge.agents.extractor.call_agent_llm", fake_call_agent_llm)

    summary = await run_extractor(
        session,
        project_id=project.id,
        chunks=chunks,
        glossary=[],
        pipeline_run_id=None,
    )

    requirements = (await session.execute(select(Requirement).where(Requirement.project_id == project.id))).scalars().all()

    assert summary.requirements_created == 2
    assert len(requirements) == 2
    assert any("splitting 4 chunks" in warning for warning in summary.warnings)