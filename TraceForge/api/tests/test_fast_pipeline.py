# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: TraceForge — api/tests (test_fast_pipeline.py)
# Date: 2026-04-08
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# Scope: TraceForge — optimized project-scale generation path
# ---------------------------------------------------------------------------
from __future__ import annotations

import time
from pathlib import Path

from sqlalchemy import select

from traceforge.agents.doc_author import BRD_DEFINITION, run_doc_author
from traceforge.agents.script_gen.runner import run_script_generator
from traceforge.agents.test_designer import run_test_designer
from traceforge.db.models import Chunk, Requirement, SourceCitation, SourceDocument
from traceforge.db.models import TestCase as TestCaseModel
from traceforge.db.models import TestScript as TestScriptModel


# Function: test_fast_pipeline_generates_tests_scripts_and_document_without_llm
async def test_fast_pipeline_generates_tests_scripts_and_document_without_llm(session, project):
    document = SourceDocument(
        project_id=project.id, source_type="UPLOAD", filename="performance.txt", blob_uri="/tmp/performance.txt",
        sha256="8" * 64, doc_class="AS_IS_DOC", status="INDEXED",
    )
    session.add(document)
    await session.flush()
    chunk = Chunk(
        source_document_id=document.id, project_id=project.id, ordinal=0,
        text="The platform shall validate and submit invoices.", token_count=8, locator={"section": "1"},
    )
    session.add(chunk)
    await session.flush()
    for index in range(5):
        requirement = Requirement(
            req_id=f"REQ-{index + 1:04d}", project_id=project.id, level="FUNCTIONAL",
            title=f"Validate invoice {index + 1}", statement=f"The platform shall validate invoice type {index + 1}.",
            ears_pattern="UBIQUITOUS", ears_parts={"system_name": "Platform"}, rationale="Source requirement",
            acceptance_criteria=[f"Invoice type {index + 1} is accepted when valid.", "Invalid input is rejected."],
            priority="MUST", ambiguity_score=0.0, ambiguity_flags=[], status="APPROVED",
            content_hash=f"{index + 1:064x}", version=1, created_by_agent=True,
        )
        session.add(requirement)
        await session.flush()
        session.add(SourceCitation(
            requirement_id=requirement.id, chunk_id=chunk.id, relevance=1.0,
            quoted_span="The platform shall validate and submit invoices.",
        ))
    await session.commit()

    started = time.perf_counter()
    design = await run_test_designer(session, project_id=project.id, pipeline_run_id=None)
    design_seconds = time.perf_counter() - started
    assert design.test_cases_created >= 15
    assert design_seconds < 5

    test_cases = list((await session.scalars(select(TestCaseModel).where(TestCaseModel.project_id == project.id))).all())
    for test_case in test_cases:
        test_case.status = "APPROVED"
    await session.commit()

    started = time.perf_counter()
    scripts = await run_script_generator(session, project_id=project.id, pipeline_run_id=None)
    script_seconds = time.perf_counter() - started
    assert scripts["scripts_created"] == len(test_cases) * 2
    assert script_seconds < 5
    generated_scripts = list((await session.scalars(
        select(TestScriptModel).where(TestScriptModel.project_id == project.id)
    )).all())
    assert len(generated_scripts) == len(test_cases) * 2
    assert all(script.compiles is True for script in generated_scripts)
    assert all("TODO_LOCATOR" not in script.code for script in generated_scripts)
    assert all("executeReviewedStep" in script.code for script in generated_scripts)

    # Regeneration updates the same logical scripts instead of appending duplicates.
    rerun = await run_script_generator(session, project_id=project.id, pipeline_run_id=None)
    assert rerun["scripts_inserted"] == 0
    assert rerun["scripts_updated"] == len(test_cases) * 2
    assert len(list((await session.scalars(
        select(TestScriptModel).where(TestScriptModel.project_id == project.id)
    )).all())) == len(test_cases) * 2

    started = time.perf_counter()
    artifact = await run_doc_author(session, project_id=project.id, definition=BRD_DEFINITION, pipeline_run_id=None)
    document_seconds = time.perf_counter() - started
    assert Path(artifact.blob_uri).exists()
    assert document_seconds < 5
    Path(artifact.blob_uri).unlink(missing_ok=True)
