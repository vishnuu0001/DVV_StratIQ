# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: 'Reset the whole pipeline for this project' — deletes PipelineRun/Gate/LLMCall
# Date: 2026-04-04
# ---------------------------------------------------------------------------
"""'Reset the whole pipeline for this project' — deletes PipelineRun/Gate/LLMCall
history so every stage shows idle again, but must never touch what the pipeline
actually produced (Requirement/Artifact/TestPlan rows and their approval statuses)."""
from __future__ import annotations

from sqlalchemy import select

from traceforge.db.models import AuditEvent, Artifact, Chunk, Gate, LLMCall, PipelineRun, SourceDocument
from traceforge.db.models import TestPlan as TestPlanModel
from traceforge.db.models import TestPlanCitation as TestPlanCitationModel
from traceforge.orchestration.gates import open_gate
from traceforge.orchestration.reset import clear_project_data, reset_pipeline


# Function: test_reset_deletes_runs_gates_and_llm_calls
async def test_reset_deletes_runs_gates_and_llm_calls(session, project):
    run = PipelineRun(project_id=project.id, stage="EXTRACT", status="RUNNING")
    session.add(run)
    await session.flush()
    await open_gate(session, run)
    session.add(LLMCall(pipeline_run_id=run.id, agent_name="x", model="m"))
    await session.commit()

    deleted = await reset_pipeline(session, project.id, actor="tester")
    await session.commit()

    assert deleted == 1
    assert (await session.execute(select(PipelineRun).where(PipelineRun.project_id == project.id))).scalars().all() == []
    assert (await session.execute(select(Gate).where(Gate.pipeline_run_id == run.id))).scalars().all() == []
    assert (await session.execute(select(LLMCall).where(LLMCall.pipeline_run_id == run.id))).scalars().all() == []


# Function: test_reset_preserves_artifacts_and_test_plans_but_unlinks_run
async def test_reset_preserves_artifacts_and_test_plans_but_unlinks_run(session, project):
    run = PipelineRun(project_id=project.id, stage="BRD", status="APPROVED")
    session.add(run)
    await session.flush()
    artifact = Artifact(
        project_id=project.id, pipeline_run_id=run.id, kind="BRD_DOCX", filename="BRD.docx",
        blob_uri="/tmp/BRD.docx", sha256="1" * 64, version=1,
    )
    plan = TestPlanModel(
        project_id=project.id, pipeline_run_id=run.id, title="t", scope="s", strategy="s",
        environments=[], schedule={}, entry_exit_criteria={}, status="DRAFT", version=1,
    )
    session.add_all([artifact, plan])
    await session.flush()

    # P1 applies to TestPlan too — needs >=1 citation before commit.
    doc = SourceDocument(
        project_id=project.id, source_type="UPLOAD", filename="t.docx", blob_uri="/tmp/t.docx",
        sha256="2" * 64, doc_class="AS_IS_DOC", status="INDEXED",
    )
    session.add(doc)
    await session.flush()
    chunk = Chunk(source_document_id=doc.id, project_id=project.id, ordinal=0, text="shall do X.", token_count=3, locator={})
    session.add(chunk)
    await session.flush()
    session.add(TestPlanCitationModel(test_plan_id=plan.id, chunk_id=chunk.id, relevance=1.0, quoted_span="shall do X."))

    await session.commit()
    await session.refresh(artifact)
    await session.refresh(plan)

    await reset_pipeline(session, project.id, actor="tester")
    await session.commit()

    await session.refresh(artifact)
    await session.refresh(plan)
    assert artifact.pipeline_run_id is None
    assert plan.pipeline_run_id is None
    # Rows themselves survive — reset must never delete what the pipeline produced.
    assert (await session.get(Artifact, artifact.id)) is not None
    assert (await session.get(TestPlanModel, plan.id)) is not None


# Function: test_start_fresh_deletes_project_data_but_preserves_project_and_audit
async def test_start_fresh_deletes_project_data_but_preserves_project_and_audit(session, project):
    run = PipelineRun(project_id=project.id, stage="EXTRACT", status="RUNNING")
    session.add(run)
    await session.flush()
    await open_gate(session, run)
    session.add(LLMCall(pipeline_run_id=run.id, agent_name="x", model="m"))

    doc = SourceDocument(
        project_id=project.id, source_type="UPLOAD", filename="fresh.docx", blob_uri="/tmp/fresh.docx",
        sha256="3" * 64, doc_class="AS_IS_DOC", status="INDEXED",
    )
    session.add(doc)
    await session.flush()
    session.add(Chunk(source_document_id=doc.id, project_id=project.id, ordinal=0, text="source", token_count=1, locator={}))
    session.add(Artifact(
        project_id=project.id, pipeline_run_id=run.id, kind="BRD_DOCX", filename="BRD.docx",
        blob_uri="/tmp/BRD.docx", sha256="4" * 64, version=1,
    ))
    await session.commit()

    counts = await clear_project_data(session, project.id, actor="tester")
    await session.commit()

    assert counts["sources"] == 1
    assert counts["artifacts"] == 1
    assert (await session.get(type(project), project.id)) is not None
    assert (await session.execute(select(SourceDocument).where(SourceDocument.project_id == project.id))).scalars().all() == []
    assert (await session.execute(select(PipelineRun).where(PipelineRun.project_id == project.id))).scalars().all() == []
    assert (await session.execute(select(Artifact).where(Artifact.project_id == project.id))).scalars().all() == []
    audit = (await session.execute(select(AuditEvent).where(
        AuditEvent.project_id == project.id, AuditEvent.action == "PROJECT_STARTED_FRESH"
    ))).scalars().first()
    assert audit is not None
