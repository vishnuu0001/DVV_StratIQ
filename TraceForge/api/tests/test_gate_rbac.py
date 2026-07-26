# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Gate RBAC hardening — Gate.required_role (spec §3.3) is enforced against the
#   deciding user's role/project persona instead of only being display metadata.
# Date: 2026-07-24
# ---------------------------------------------------------------------------
"""Covers: global 'admin' always bypasses; an unconfigured project keeps the
pre-hardening permissive behaviour; once a project assigns config.gate_roles, only
the assigned username(s) (or admin) may decide that gate."""
from __future__ import annotations

import pytest
from fastapi import HTTPException

from traceforge.db.models import Gate, PipelineRun
from traceforge.orchestration.gates import decide_gate, open_gate


# Function: _open_test_design_gate
async def _open_test_design_gate(session, project) -> Gate:
    run = PipelineRun(project_id=project.id, stage="TEST_DESIGN", status="RUNNING")
    session.add(run)
    await session.flush()
    gate = await open_gate(session, run)  # required_role -> TEST_LEAD
    await session.commit()
    return gate


# Function: test_admin_bypasses_gate_role_check_even_when_configured
async def test_admin_bypasses_gate_role_check_even_when_configured(session, project):
    project.config = {"gate_roles": {"TEST_LEAD": ["alice"]}}
    await session.commit()
    gate = await _open_test_design_gate(session, project)

    gate = await decide_gate(
        session, gate, decision="APPROVED", rationale=None, item_decisions={},
        decided_by="random-admin", actor_role="admin",
    )
    await session.commit()  # release the flush's row lock before the project fixture's teardown runs
    assert gate.decision == "APPROVED"


# Function: test_unconfigured_project_permits_any_authenticated_user
async def test_unconfigured_project_permits_any_authenticated_user(session, project):
    """No config.gate_roles set for this project -> pre-hardening permissive
    behaviour, so existing single-tenant/demo deployments aren't broken outright."""
    gate = await _open_test_design_gate(session, project)

    gate = await decide_gate(
        session, gate, decision="APPROVED", rationale=None, item_decisions={},
        decided_by="anyone", actor_role="user",
    )
    await session.commit()  # release the flush's row lock before the project fixture's teardown runs
    assert gate.decision == "APPROVED"


# Function: test_configured_project_rejects_wrong_persona
async def test_configured_project_rejects_wrong_persona(session, project):
    project.config = {"gate_roles": {"TEST_LEAD": ["alice"]}}
    await session.commit()
    gate = await _open_test_design_gate(session, project)

    with pytest.raises(HTTPException) as exc_info:
        await decide_gate(
            session, gate, decision="APPROVED", rationale=None, item_decisions={},
            decided_by="bob", actor_role="user",
        )
    assert exc_info.value.status_code == 403


# Function: test_configured_project_allows_assigned_persona
async def test_configured_project_allows_assigned_persona(session, project):
    project.config = {"gate_roles": {"TEST_LEAD": ["alice"]}}
    await session.commit()
    gate = await _open_test_design_gate(session, project)

    gate = await decide_gate(
        session, gate, decision="APPROVED", rationale=None, item_decisions={},
        decided_by="alice", actor_role="user",
    )
    await session.commit()  # release the flush's row lock before the project fixture's teardown runs
    assert gate.decision == "APPROVED"


# Function: test_configured_project_ignores_roles_for_other_stages
async def test_configured_project_ignores_roles_for_other_stages(session, project):
    """gate_roles is keyed by GateRole, not by stage name directly, but only the
    role relevant to *this* gate's required_role should ever gate the decision —
    assigning TEST_LEAD must not restrict a BUSINESS_ANALYST (Gate 1) decision."""
    project.config = {"gate_roles": {"TEST_LEAD": ["alice"]}}
    await session.commit()

    run = PipelineRun(project_id=project.id, stage="EXTRACT", status="RUNNING")
    session.add(run)
    await session.flush()
    gate = await open_gate(session, run)  # required_role -> BUSINESS_ANALYST
    await session.commit()

    gate = await decide_gate(
        session, gate, decision="APPROVED", rationale=None, item_decisions={},
        decided_by="carol", actor_role="user",
    )
    await session.commit()  # release the flush's row lock before the project fixture's teardown runs
    assert gate.decision == "APPROVED"
