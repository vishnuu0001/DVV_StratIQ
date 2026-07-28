# ---------------------------------------------------------------------------
# Author: GitHub Copilot
# Scope: TraceForge — extraction worker hardening regressions
# Date: 2026-07-28
# ---------------------------------------------------------------------------
from __future__ import annotations

from sqlalchemy import select

from traceforge.agents.extractor import ExtractSummary
from traceforge.db.models import Chunk, Gate, PipelineRun, SourceDocument
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