# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: §6.2 suspect-link propagation acceptance test: 'edit an approved requirement ->
# Date: 2026-02-28
# ---------------------------------------------------------------------------
"""§6.2 suspect-link propagation acceptance test: 'edit an approved requirement ->
exactly the affected TCs and TSs become SUSPECT, nothing is deleted, the impact banner
reports the correct counts.'"""
from __future__ import annotations

import uuid

from traceforge.db.models import Artifact, Chunk, Requirement, SourceCitation, SourceDocument
from traceforge.db.models import TestCase as TestCaseModel
from traceforge.db.models import TestScript as TestScriptModel
from traceforge.orchestration.suspect import get_requirement_impact, propagate_suspect


# Function: _make_approved_requirement_with_chain
async def _make_approved_requirement_with_chain(session, project):
    doc = SourceDocument(
        project_id=project.id, source_type="UPLOAD", filename="t.docx", blob_uri="/tmp/t.docx",
        sha256="1" * 64, doc_class="AS_IS_DOC", status="INDEXED",
    )
    session.add(doc)
    await session.flush()
    chunk = Chunk(source_document_id=doc.id, project_id=project.id, ordinal=0, text="shall do X.", token_count=3, locator={})
    session.add(chunk)
    await session.flush()

    requirement = Requirement(
        req_id=f"REQ-{uuid.uuid4().hex[:6]}", project_id=project.id, level="FUNCTIONAL", title="t",
        statement="The system shall do X.", ears_pattern="UBIQUITOUS", ears_parts={"system_name": "System"},
        acceptance_criteria=["X happens"], priority="SHOULD", ambiguity_score=0.0, ambiguity_flags=[],
        status="APPROVED", content_hash="hash-v1", version=1, created_by_agent=True,
    )
    session.add(requirement)
    await session.flush()
    session.add(SourceCitation(requirement_id=requirement.id, chunk_id=chunk.id, relevance=1.0, quoted_span="shall do X."))
    await session.commit()
    await session.refresh(requirement)

    test_case = TestCaseModel(
        tc_id=f"TC-{uuid.uuid4().hex[:6]}", project_id=project.id, requirement_id=requirement.id, title="verify X",
        test_type="POSITIVE", test_level="UI_E2E", preconditions=[], steps=[], priority="P2",
        status="APPROVED", upstream_req_hash="hash-v1", content_hash="tc-hash", version=1, created_by_agent=True,
    )
    session.add(test_case)
    await session.flush()

    test_script = TestScriptModel(
        ts_id=f"TS-{uuid.uuid4().hex[:6]}", project_id=project.id, test_case_id=test_case.id, target="PLAYWRIGHT_TS",
        language="typescript", code="test('x', async () => {})", file_path="tests/x.spec.ts",
        status="APPROVED", upstream_tc_hash="tc-hash", version=1,
    )
    session.add(test_script)

    artifact = Artifact(
        project_id=project.id, kind="BRD_DOCX", filename="BRD.docx", blob_uri="/tmp/BRD.docx",
        sha256="2" * 64, version=1, requirement_ids=[requirement.req_id], stale=False,
    )
    session.add(artifact)
    await session.commit()
    await session.refresh(test_case)
    await session.refresh(test_script)
    await session.refresh(artifact)
    return requirement, test_case, test_script, artifact


# Function: test_propagate_suspect_cascades_and_never_deletes
async def test_propagate_suspect_cascades_and_never_deletes(session, project):
    requirement, test_case, test_script, artifact = await _make_approved_requirement_with_chain(session, project)

    # Simulate the edit endpoint's content_hash bump (spec: editing changes the hash).
    requirement.content_hash = "hash-v2"
    requirement.version += 1
    await session.flush()

    impact = await propagate_suspect(session, requirement, actor="tester")
    await session.commit()

    assert impact["suspect_test_case_count"] == 1
    assert impact["suspect_script_count"] == 1
    assert impact["stale_artifact_count"] == 1

    await session.refresh(test_case)
    await session.refresh(test_script)
    await session.refresh(artifact)
    assert test_case.status == "SUSPECT"
    assert test_script.status == "SUSPECT"
    assert artifact.stale is True

    # Nothing was deleted — all three rows still exist and are fetchable.
    assert (await session.get(TestCaseModel, test_case.id)) is not None
    assert (await session.get(TestScriptModel, test_script.id)) is not None
    assert (await session.get(Artifact, artifact.id)) is not None


# Function: test_propagate_suspect_is_idempotent_when_hash_unchanged
async def test_propagate_suspect_is_idempotent_when_hash_unchanged(session, project):
    requirement, test_case, test_script, artifact = await _make_approved_requirement_with_chain(session, project)

    # No content_hash change this time — upstream_req_hash still matches.
    impact = await propagate_suspect(session, requirement, actor="tester")
    await session.commit()

    assert impact["suspect_test_case_count"] == 0
    assert impact["suspect_script_count"] == 0


# Function: test_get_requirement_impact_is_read_only_preview
async def test_get_requirement_impact_is_read_only_preview(session, project):
    requirement, test_case, test_script, artifact = await _make_approved_requirement_with_chain(session, project)

    impact = await get_requirement_impact(session, requirement)

    assert test_case.tc_id in impact["test_cases_affected"]
    assert test_script.ts_id in impact["test_scripts_affected"]
    assert artifact.filename in impact["artifacts_affected"]

    # Read-only: statuses must be unchanged by merely previewing impact.
    await session.refresh(test_case)
    await session.refresh(test_script)
    assert test_case.status == "APPROVED"
    assert test_script.status == "APPROVED"
