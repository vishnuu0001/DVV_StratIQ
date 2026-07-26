# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Phase 1 acceptance (Requirements.MD §10): 'attempting to start Agent 2 via the API
# Date: 2025-11-16
# ---------------------------------------------------------------------------
"""Phase 1 acceptance (Requirements.MD §10): 'attempting to start Agent 2 via the API
while Gate 1 is PENDING returns 409.'"""
from __future__ import annotations

import pytest
from fastapi import HTTPException

from traceforge.db.models import Gate, PipelineRun
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
