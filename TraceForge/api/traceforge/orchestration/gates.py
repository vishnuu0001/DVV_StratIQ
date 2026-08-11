# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: §6.1 state machine + P3 ('No downstream agent may execute until the upstream stage
# Date: 2026-06-20
# ---------------------------------------------------------------------------
"""§6.1 state machine + P3 ('No downstream agent may execute until the upstream stage
is APPROVED. Enforced in the orchestrator state machine, not the UI.'). This module is
the single authority the API and the worker both call before starting a stage — so a
request that bypasses the UI gets the same 409 the UI would have shown."""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from traceforge.agents.coverage_policy import check_coverage, requirement_is_executable
from traceforge.agents.script_gen.playwright import _parse_tc_metadata, _verified_automation_status
from traceforge.db.models import Gate, PipelineRun, Project, Requirement, TestCase, TestPlan, TestScript

# INGEST -> EXTRACT -[GATE 1]-> BRD -[GATE 2]-> TEST_DESIGN -[GATE 3]-> SCRIPT_GEN -[GATE 4]-> RENDER
PREREQUISITE_STAGE: dict[str, str] = {
    "BRD": "EXTRACT",
    "TEST_DESIGN": "BRD",
    "SCRIPT_GEN": "TEST_DESIGN",
    "RENDER": "SCRIPT_GEN",
}

GATE_ROLE_FOR_STAGE: dict[str, str] = {
    "EXTRACT": "BUSINESS_ANALYST",   # Gate 1
    "BRD": "ARCHITECT",              # Gate 2
    "TEST_DESIGN": "TEST_LEAD",      # Gate 3
    "SCRIPT_GEN": "CLIENT_REVIEWER", # Gate 4 (Reviewer)
}

_PASSING_DECISIONS = {"APPROVED", "APPROVED_WITH_COMMENTS"}


def _is_automation_ready(test_case: TestCase) -> bool:
    status, _ = _verified_automation_status(test_case, _parse_tc_metadata(test_case))
    return status == "READY_FOR_UI_AUTOMATION"


def _is_playwright_candidate(test_case: TestCase) -> bool:
    return True


# Function: assert_stage_unblocked
async def assert_stage_unblocked(session: AsyncSession, project_id: uuid.UUID, stage: str) -> None:
    """Raises HTTPException(409) if `stage` can't start yet — the Phase 1 acceptance
    test asserts exactly this for BRD while Gate 1 is PENDING."""
    prerequisite_stage = PREREQUISITE_STAGE.get(stage)
    if prerequisite_stage is None:
        return  # INGEST/EXTRACT have no upstream gate

    if stage in {"SCRIPT_GEN", "RENDER"}:
        approved_cases = list((await session.scalars(
            select(TestCase).where(
                TestCase.project_id == project_id,
                TestCase.status == "APPROVED",
            )
        )).all())
        has_automation_ready_case = any(_is_automation_ready(test_case) for test_case in approved_cases)
        has_playwright_candidate = any(_is_playwright_candidate(test_case) for test_case in approved_cases)
        if stage == "SCRIPT_GEN" and not has_playwright_candidate:
            raise HTTPException(
                status_code=409,
                detail="Cannot start SCRIPT_GEN: no approved test case is available for Playwright placeholder generation.",
            )
        if stage == "RENDER" and not has_automation_ready_case:
            prerequisite_stage = "TEST_DESIGN"

    result = await session.execute(
        select(PipelineRun).where(PipelineRun.project_id == project_id, PipelineRun.stage == prerequisite_stage)
        .order_by(PipelineRun.created_at.desc())
    )
    prior_run = result.scalars().first()
    if prior_run is None:
        raise HTTPException(status_code=409, detail=f"Cannot start {stage}: {prerequisite_stage} has not been run yet.")

    gate_result = await session.execute(select(Gate).where(Gate.pipeline_run_id == prior_run.id))
    gate = gate_result.scalars().first()
    if gate is None or gate.decision not in _PASSING_DECISIONS:
        decision = gate.decision if gate else "PENDING"
        raise HTTPException(
            status_code=409,
            detail=f"Cannot start {stage}: the {prerequisite_stage} gate is {decision}, not approved.",
        )


# Function: open_gate
async def open_gate(session: AsyncSession, pipeline_run: PipelineRun) -> Gate:
    required_role = GATE_ROLE_FOR_STAGE.get(pipeline_run.stage, "BUSINESS_ANALYST")
    gate = Gate(pipeline_run_id=pipeline_run.id, required_role=required_role, decision="PENDING", item_decisions={})
    session.add(gate)
    pipeline_run.status = "AWAITING_APPROVAL"
    await session.flush()
    return gate


# Function: _cascade_item_approval
async def _cascade_item_approval(
    session: AsyncSession,
    project_id: uuid.UUID,
    stage: str,
    item_decisions: dict,
    *,
    allow_blocked_test_design: bool = False,
) -> None:
    """A gate decision is what actually turns a batch of DRAFT items into APPROVED —
    spec §8.3's 'Bulk-approve, per-item reject with reason' — otherwise nothing
    downstream (Test Designer, Script Generator) ever finds an APPROVED row to work
    from. Scoped to the whole project's pending items for this stage (not just the
    specific run) — this build doesn't track a per-row pipeline_run_id, so a gate
    decision approves every DRAFT/IN_REVIEW item of the relevant kind for the
    project, honouring per-item REJECT overrides in item_decisions."""
    if stage == "EXTRACT":
        result = await session.execute(select(Requirement).where(Requirement.project_id == project_id, Requirement.status.in_(["DRAFT", "IN_REVIEW"])))
        rows = list(result.scalars().all())
        key_attr = "req_id"
    elif stage == "TEST_DESIGN":
        result = await session.execute(select(TestCase).where(TestCase.project_id == project_id, TestCase.status.in_(["DRAFT", "IN_REVIEW"])))
        rows = list(result.scalars().all())
        key_attr = "tc_id"
        plan_result = await session.execute(select(TestPlan).where(TestPlan.project_id == project_id, TestPlan.status.in_(["DRAFT", "IN_REVIEW"])))
        plans = list(plan_result.scalars().all())
    elif stage == "SCRIPT_GEN":
        result = await session.execute(select(TestScript).where(TestScript.project_id == project_id, TestScript.status.in_(["DRAFT", "IN_REVIEW"])))
        rows = list(result.scalars().all())
        key_attr = "ts_id"
    else:
        return

    for row in rows:
        item_id = getattr(row, key_attr)
        override = item_decisions.get(item_id)
        if override == "REJECT":
            row.status = "REJECTED"
        elif (
            stage == "TEST_DESIGN"
            and not allow_blocked_test_design
            and _has_unresolved_business_review(row)
        ):
            row.status = "IN_REVIEW"
        else:
            row.status = "APPROVED"
    if stage == "TEST_DESIGN":
        has_pending_cases = any(row.status == "IN_REVIEW" for row in rows)
        for plan in plans:
            plan.status = "IN_REVIEW" if has_pending_cases else "APPROVED"


def _has_unresolved_business_review(test_case: TestCase) -> bool:
    raw = test_case.gherkin or ""
    if not raw.lstrip().startswith("{"):
        return True
    try:
        metadata = json.loads(raw)
    except (TypeError, ValueError):
        return True
    if metadata.get("ambiguities"):
        return True
    assumptions = " ".join(str(value) for value in metadata.get("assumptions") or []).lower()
    return any(marker in assumptions for marker in ("pending", "review needed", "requires business owner review"))


# Function: _assert_actor_authorized
async def _assert_actor_authorized(
    session: AsyncSession, project_id: uuid.UUID, required_role: str, actor_role: str, actor_username: str,
) -> None:
    """P3 'Humans own the gates': a gate's `required_role` (spec §3.3) is otherwise
    just display metadata unless something actually checks the deciding user against
    it. Global 'admin' always bypasses (same convention as the auth-app-access check
    in main.py). Below that, enforcement is opt-in per project via
    config.gate_roles — a project that hasn't assigned anyone to `required_role`
    keeps the pre-hardening permissive behaviour (any authenticated user may decide),
    since forcing every project to configure personas before its gates are usable
    would break every existing single-tenant/demo deployment outright."""
    if actor_role == "admin":
        return
    project = await session.get(Project, project_id)
    gate_roles = (project.config.get("gate_roles") if project else None) or {}
    allowed_usernames = gate_roles.get(required_role)
    if not allowed_usernames:
        return
    if actor_username not in allowed_usernames:
        raise HTTPException(
            status_code=403,
            detail=f"This gate requires {required_role} ({', '.join(allowed_usernames)}) to decide.",
        )


# Function: decide_gate
async def decide_gate(
    session: AsyncSession,
    gate: Gate,
    *,
    decision: str,
    rationale: str | None,
    item_decisions: dict,
    decided_by: str,
    actor_role: str = "admin",
) -> Gate:
    if decision == "REJECTED" and not rationale:
        raise HTTPException(status_code=422, detail="rationale is MANDATORY when rejecting a gate.")
    if decision == "APPROVED_WITH_COMMENTS" and not (rationale or "").strip():
        raise HTTPException(
            status_code=422,
            detail="rationale is MANDATORY when approving a gate with comments.",
        )

    result = await session.execute(select(PipelineRun).where(PipelineRun.id == gate.pipeline_run_id))
    pipeline_run = result.scalar_one()

    await _assert_actor_authorized(session, pipeline_run.project_id, gate.required_role, actor_role, decided_by)
    if pipeline_run.stage == "EXTRACT" and decision in _PASSING_DECISIONS:
        unresolved_requirements = list((await session.scalars(
            select(Requirement).where(
                Requirement.project_id == pipeline_run.project_id,
                Requirement.status.in_(["DRAFT", "IN_REVIEW"]),
            )
        )).all())
        conflicting = [requirement.req_id for requirement in unresolved_requirements if requirement.conflict_flags]
        if conflicting:
            preview = ", ".join(conflicting[:10])
            suffix = "..." if len(conflicting) > 10 else ""
            raise HTTPException(
                status_code=409,
                detail=(
                    f"Cannot approve Extract: {len(conflicting)} requirement(s) contain unresolved "
                    f"source contradictions ({preview}{suffix}). Resolve the source decision first."
                ),
            )
    if pipeline_run.stage == "TEST_DESIGN" and decision in _PASSING_DECISIONS:
        approved_requirements = list((await session.scalars(
            select(Requirement).where(
                Requirement.project_id == pipeline_run.project_id,
                Requirement.status == "APPROVED",
            )
        )).all())
        testable_requirements = [
            requirement for requirement in approved_requirements
            if requirement_is_executable(requirement)
        ]
        unresolved_requirements = [
            requirement for requirement in approved_requirements
            if not requirement_is_executable(requirement)
        ]
        if unresolved_requirements:
            preview = ", ".join(requirement.req_id for requirement in unresolved_requirements[:10])
            suffix = "..." if len(unresolved_requirements) > 10 else ""
            raise HTTPException(
                status_code=409,
                detail=(
                    f"Cannot approve Test Design: {len(unresolved_requirements)} unresolved information "
                    f"gap(s) require confirmed outcomes and acceptance criteria ({preview}{suffix})."
                ),
            )
        pending_cases = list((await session.scalars(
            select(TestCase).where(
                TestCase.project_id == pipeline_run.project_id,
                TestCase.status.in_(["DRAFT", "IN_REVIEW"]),
            )
        )).all())
        cases_by_requirement: dict[uuid.UUID, list[TestCase]] = {}
        for case in pending_cases:
            cases_by_requirement.setdefault(case.requirement_id, []).append(case)
        coverage_gaps = [
            gap.description
            for requirement in testable_requirements
            for gap in check_coverage(requirement, cases_by_requirement.get(requirement.id, []))
        ]
        if coverage_gaps:
            preview = "; ".join(coverage_gaps[:5])
            suffix = "..." if len(coverage_gaps) > 5 else ""
            raise HTTPException(
                status_code=409,
                detail=(
                    f"Cannot approve Test Design: evidence-first coverage policy has {len(coverage_gaps)} gap(s). "
                    f"{preview}{suffix}"
                ),
            )
        unresolved_ids = [case.tc_id for case in pending_cases if _has_unresolved_business_review(case)]
        if unresolved_ids and decision != "APPROVED_WITH_COMMENTS":
            preview = ", ".join(unresolved_ids[:10])
            suffix = "..." if len(unresolved_ids) > 10 else ""
            raise HTTPException(
                status_code=409,
                detail=(
                    f"Cannot approve Test Design: {len(unresolved_ids)} case(s) still contain unresolved "
                    f"business-review items ({preview}{suffix}). Resolve their ambiguity/assumption metadata first."
                ),
            )

    gate.decision = decision
    gate.rationale = rationale
    gate.item_decisions = item_decisions or {}
    gate.decided_by = decided_by
    gate.decided_at = datetime.now(timezone.utc)

    pipeline_run.status = "APPROVED" if decision in _PASSING_DECISIONS else "REJECTED"

    if decision in _PASSING_DECISIONS:
        await _cascade_item_approval(
            session,
            pipeline_run.project_id,
            pipeline_run.stage,
            gate.item_decisions,
            allow_blocked_test_design=(
                pipeline_run.stage == "TEST_DESIGN" and decision == "APPROVED_WITH_COMMENTS"
            ),
        )

    await session.flush()
    return gate
