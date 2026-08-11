# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Phase 1 acceptance (Requirements.MD §10): 'attempting to start Agent 2 via the API
# Date: 2025-11-16
# ---------------------------------------------------------------------------
"""Phase 1 acceptance (Requirements.MD §10): 'attempting to start Agent 2 via the API
while Gate 1 is PENDING returns 409.'"""
from __future__ import annotations

import json

import pytest
from fastapi import HTTPException

from traceforge.db.models import PipelineRun, Requirement, TestCase, TestPlan
from traceforge.orchestration.gates import assert_stage_unblocked, decide_gate, open_gate


# Function: test_extract_has_no_prerequisite_gate
async def test_extract_has_no_prerequisite_gate(session, project):
    await assert_stage_unblocked(session, project.id, "EXTRACT")  # must not raise


# Function: test_brd_blocked_when_no_extract_run_exists
async def test_brd_blocked_when_no_extract_run_exists(session, project):
    with pytest.raises(HTTPException) as exc_info:
        await assert_stage_unblocked(session, project.id, "BRD")
    assert exc_info.value.status_code == 409


# Function: test_brd_blocked_while_gate_1_pending
async def test_brd_blocked_while_gate_1_pending(session, project):
    run = PipelineRun(project_id=project.id, stage="EXTRACT", status="RUNNING")
    session.add(run)
    await session.flush()
    await open_gate(session, run)  # -> Gate PENDING, run -> AWAITING_APPROVAL
    await session.commit()

    with pytest.raises(HTTPException) as exc_info:
        await assert_stage_unblocked(session, project.id, "BRD")
    assert exc_info.value.status_code == 409
    assert "PENDING" in exc_info.value.detail


# Function: test_brd_unblocked_once_gate_1_approved
async def test_brd_unblocked_once_gate_1_approved(session, project):
    run = PipelineRun(project_id=project.id, stage="EXTRACT", status="RUNNING")
    session.add(run)
    await session.flush()
    gate = await open_gate(session, run)
    await session.commit()

    await decide_gate(session, gate, decision="APPROVED", rationale=None, item_decisions={}, decided_by="tester")
    await session.commit()

    await assert_stage_unblocked(session, project.id, "BRD")  # must not raise


async def test_render_uses_test_design_gate_when_no_cases_are_automation_ready(session, project):
    run = PipelineRun(project_id=project.id, stage="TEST_DESIGN", status="APPROVED")
    session.add(run)
    await session.flush()
    gate = await open_gate(session, run)
    gate.decision = "APPROVED_WITH_COMMENTS"
    run.status = "APPROVED"
    await session.flush()

    await assert_stage_unblocked(session, project.id, "RENDER")


async def test_script_generation_requires_an_approved_case(session, project):
    with pytest.raises(HTTPException) as exc_info:
        await assert_stage_unblocked(session, project.id, "SCRIPT_GEN")
    assert exc_info.value.status_code == 409
    assert "no approved test case" in exc_info.value.detail


async def test_script_generation_allows_placeholder_for_approved_ui_case(session, project):
    run = PipelineRun(project_id=project.id, stage="TEST_DESIGN", status="APPROVED")
    session.add(run)
    await session.flush()
    gate = await open_gate(session, run)
    gate.decision = "APPROVED"
    run.status = "APPROVED"
    requirement = Requirement(
        req_id="REQ-PLACEHOLDER", project_id=project.id, level="FUNCTIONAL",
        title="Placeholder outcome", statement="The system shall produce the reviewed outcome.",
        ears_pattern="UBIQUITOUS", ears_parts={}, acceptance_criteria=["The reviewed outcome is produced."],
        priority="MUST", ambiguity_score=0, ambiguity_flags=[], conflict_flags=[], status="APPROVED",
        content_hash="e" * 64,
    )
    session.add(requirement)
    await session.flush()
    session.add(TestCase(
        tc_id="TC-PLACEHOLDER", project_id=project.id, requirement_id=requirement.id,
        title="UI case awaiting bindings", test_type="POSITIVE", test_level="UI_E2E",
        preconditions=[], steps=[], gherkin='{"automation_status":"AUTOMATION_BLOCKED"}',
        priority="P1", status="APPROVED", upstream_req_hash=requirement.content_hash,
        content_hash="f" * 64, created_by_agent=True,
    ))
    await session.flush()

    await assert_stage_unblocked(session, project.id, "SCRIPT_GEN")


async def test_render_still_requires_script_gate_when_an_automation_ready_case_exists(
    session, project, monkeypatch,
):
    run = PipelineRun(project_id=project.id, stage="TEST_DESIGN", status="APPROVED")
    session.add(run)
    await session.flush()
    gate = await open_gate(session, run)
    gate.decision = "APPROVED"
    run.status = "APPROVED"
    monkeypatch.setattr("traceforge.orchestration.gates._is_automation_ready", lambda _: True)
    requirement = Requirement(
        req_id="REQ-READY", project_id=project.id, level="FUNCTIONAL", title="Ready outcome",
        statement="The system shall produce the ready outcome.", ears_pattern="UBIQUITOUS",
        ears_parts={}, acceptance_criteria=["The outcome is produced."], priority="MUST",
        ambiguity_score=0, ambiguity_flags=[], conflict_flags=[], status="APPROVED",
        content_hash="c" * 64,
    )
    session.add(requirement)
    await session.flush()
    session.add(TestCase(
        tc_id="TC-READY", project_id=project.id, requirement_id=requirement.id,
        title="Ready case", test_type="POSITIVE", test_level="UI_E2E", preconditions=[], steps=[],
        gherkin="{}", priority="P1", status="APPROVED", upstream_req_hash=requirement.content_hash,
        content_hash="d" * 64, created_by_agent=True,
    ))
    await session.flush()

    with pytest.raises(HTTPException) as exc_info:
        await assert_stage_unblocked(session, project.id, "RENDER")
    assert exc_info.value.status_code == 409
    assert "SCRIPT_GEN has not been run" in exc_info.value.detail


# Function: test_gate_rejection_requires_rationale
async def test_gate_rejection_requires_rationale(session, project):
    run = PipelineRun(project_id=project.id, stage="EXTRACT", status="RUNNING")
    session.add(run)
    await session.flush()
    gate = await open_gate(session, run)
    await session.commit()

    with pytest.raises(HTTPException) as exc_info:
        await decide_gate(session, gate, decision="REJECTED", rationale=None, item_decisions={}, decided_by="tester")
    assert exc_info.value.status_code == 422


async def test_approval_with_comments_requires_rationale(session, project):
    run = PipelineRun(project_id=project.id, stage="TEST_DESIGN", status="RUNNING")
    session.add(run)
    await session.flush()
    gate = await open_gate(session, run)

    with pytest.raises(HTTPException) as exc_info:
        await decide_gate(
            session, gate, decision="APPROVED_WITH_COMMENTS", rationale=None,
            item_decisions={}, decided_by="test-lead",
        )

    assert exc_info.value.status_code == 422
    assert "rationale" in exc_info.value.detail


async def test_test_design_approval_blocks_unresolved_information_gaps(session, project):
    assumption = Requirement(
        req_id="REQ-GAP", project_id=project.id, level="ASSUMPTION",
        title="Create Sales Order", statement="Create Sales Order",
        ears_pattern="NON_CONFORMANT", ears_parts={}, acceptance_criteria=[],
        priority="MUST", ambiguity_score=1, ambiguity_flags=[], conflict_flags=[],
        status="APPROVED", content_hash="e" * 64,
    )
    run = PipelineRun(project_id=project.id, stage="TEST_DESIGN", status="RUNNING")
    session.add_all([assumption, run])
    await session.flush()
    gate = await open_gate(session, run)

    with pytest.raises(HTTPException) as exc_info:
        await decide_gate(
            session, gate, decision="APPROVED", rationale=None,
            item_decisions={}, decided_by="test-lead",
        )

    assert exc_info.value.status_code == 409
    assert "REQ-GAP" in exc_info.value.detail
    assert "acceptance criteria" in exc_info.value.detail


async def test_approval_with_comments_accepts_blocked_cases_as_reviewed_assets(
    session, project, monkeypatch,
):
    requirement = Requirement(
        req_id="REQ-0001", project_id=project.id, level="FUNCTIONAL",
        title="Source-backed outcome", statement="The system shall produce the approved outcome.",
        ears_pattern="UBIQUITOUS", ears_parts={}, acceptance_criteria=["The approved outcome is produced."],
        priority="MUST", ambiguity_score=0, ambiguity_flags=[], conflict_flags=[], status="APPROVED",
        content_hash="a" * 64,
    )
    session.add(requirement)
    await session.flush()
    test_case = TestCase(
        tc_id="TC-0001", project_id=project.id, requirement_id=requirement.id,
        title="Blocked source-grounded scenario", test_type="POSITIVE", test_level="UI_E2E",
        preconditions=[], steps=[{
            "step_no": 1,
            "action": "[EXECUTION DETAIL BLOCKED — application binding required]",
            "expected_result": "The approved outcome is produced.",
        }],
        gherkin=json.dumps({
            "automation_status": "AUTOMATION_BLOCKED",
            "automation_blockers": ["Application binding required"],
            "ambiguities": ["Execution role is not supplied"],
            "assumptions": [],
        }),
        priority="P1", status="DRAFT", upstream_req_hash=requirement.content_hash,
        content_hash="b" * 64, created_by_agent=True,
    )
    plan = TestPlan(
        project_id=project.id, title="Test Plan", scope="Approved scope", strategy="Risk based",
        environments=[], schedule={}, entry_exit_criteria={}, status="DRAFT",
    )
    run = PipelineRun(project_id=project.id, stage="TEST_DESIGN", status="RUNNING")
    session.add_all([test_case, plan, run])
    await session.flush()
    plan.pipeline_run_id = run.id
    gate = await open_gate(session, run)
    monkeypatch.setattr("traceforge.orchestration.gates.check_coverage", lambda requirement, cases: [])

    gate = await decide_gate(
        session, gate, decision="APPROVED_WITH_COMMENTS",
        rationale="Test Design accepted; automation remains blocked pending application bindings.",
        item_decisions={}, decided_by="test-lead",
    )

    assert gate.decision == "APPROVED_WITH_COMMENTS"
    assert test_case.status == "APPROVED"
    assert json.loads(test_case.gherkin)["automation_status"] == "AUTOMATION_BLOCKED"
    assert plan.status == "APPROVED"
