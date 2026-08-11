# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Coverage dashboard — real this pass (depends on TestCase/TestScript, both real now).
# Date: 2026-06-06
# ---------------------------------------------------------------------------
"""One authoritative coverage model for dashboards, gaps, and traceability."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from traceforge.agents.coverage_policy import check_coverage, requirement_is_executable
from traceforge.agents.script_gen.playwright import _parse_tc_metadata, _verified_automation_status
from traceforge.auth import current_user
from traceforge.db.models import LLMCall, PipelineRun, Requirement, TestCase, TestScript
from traceforge.db.session import get_session

router = APIRouter(prefix="/api/v1", tags=["coverage"])


def _percentage(numerator: int, denominator: int) -> float:
    return round(100 * numerator / denominator, 1) if denominator else 0.0


def _is_testable(requirement: Requirement) -> bool:
    return requirement_is_executable(requirement)


def _is_automation_ready(test_case: TestCase) -> bool:
    status, _ = _verified_automation_status(test_case, _parse_tc_metadata(test_case))
    return status == "READY_FOR_UI_AUTOMATION"


def _test_design_status(testable: bool, policy_compliant: bool, test_count: int) -> str:
    if not testable:
        return "INFORMATION_GAP"
    if policy_compliant:
        return "TEST_DESIGNED"
    return "POLICY_GAPS" if test_count else "NO_TESTS"


def _automation_status(
    testable: bool, ready_count: int, script_count: int, manual_count: int, test_count: int,
) -> str:
    if not testable:
        return "NOT_APPLICABLE"
    if ready_count == 0:
        return "MANUAL_ONLY" if manual_count == test_count and manual_count else "AUTOMATION_BLOCKED"
    if script_count >= ready_count:
        return "SCRIPTED"
    return "PARTIALLY_SCRIPTED" if script_count else "READY_FOR_SCRIPT"


def _requirement_coverage_row(
    requirement: Requirement,
    requirement_cases: list[TestCase],
    ready_ids: set[uuid.UUID],
    valid_script_case_ids: set[uuid.UUID],
    reviewed_ids: set[uuid.UUID],
    manual_ids: set[uuid.UUID],
) -> dict:
    case_ids = {test_case.id for test_case in requirement_cases}
    testable = _is_testable(requirement)
    policy_gaps = check_coverage(requirement, requirement_cases) if testable else []
    policy_compliant = testable and not policy_gaps
    ready_count = len(case_ids & ready_ids)
    script_count = len(case_ids & valid_script_case_ids)
    reviewed_count = len(case_ids & reviewed_ids)
    manual_count = len(case_ids & manual_ids)
    return {
        "requirement_id": str(requirement.id),
        "req_id": requirement.req_id,
        "title": requirement.title,
        "statement": requirement.statement,
        "level": requirement.level,
        "testable": testable,
        "test_status": _test_design_status(testable, policy_compliant, len(requirement_cases)),
        "policy_compliant": policy_compliant,
        "policy_gaps": [gap.description for gap in policy_gaps],
        "test_count": len(requirement_cases),
        "reviewed_test_count": reviewed_count,
        "automation_ready_count": ready_count,
        "automation_blocked_count": max(0, len(requirement_cases) - ready_count - manual_count),
        "manual_test_count": manual_count,
        "script_count": script_count,
        "automation_status": _automation_status(
            testable, ready_count, script_count, manual_count, len(requirement_cases),
        ),
    }


def _coverage_by_level(rows: list[dict]) -> dict[str, dict]:
    by_level: dict[str, dict] = {}
    for row in rows:
        stats = by_level.setdefault(row["level"], {
            "total": 0, "executable": 0, "test_covered": 0, "information_gaps": 0,
        })
        stats["total"] += 1
        if row["testable"]:
            stats["executable"] += 1
            stats["test_covered"] += int(row["policy_compliant"])
        else:
            stats["information_gaps"] += 1
    return by_level


def build_coverage_summary(
    requirements: list[Requirement],
    test_cases: list[TestCase],
    scripts: list[TestScript],
) -> dict:
    """Keep test design, human review, and automation coverage independent."""
    requirements = [
        requirement for requirement in requirements
        if getattr(requirement, "status", "APPROVED") not in {"SUPERSEDED", "REJECTED"}
    ]
    active_requirement_ids = {requirement.id for requirement in requirements}
    test_cases = [
        test_case for test_case in test_cases
        if test_case.requirement_id in active_requirement_ids
    ]
    cases_by_requirement: dict[uuid.UUID, list[TestCase]] = {}
    cases_by_id = {test_case.id: test_case for test_case in test_cases}
    for test_case in test_cases:
        cases_by_requirement.setdefault(test_case.requirement_id, []).append(test_case)

    valid_script_case_ids = {
        script.test_case_id
        for script in scripts
        if script.status not in {"REJECTED", "SUSPECT"}
        and script.test_case_id in cases_by_id
        and script.upstream_tc_hash == cases_by_id[script.test_case_id].content_hash
    }
    ready_ids = {test_case.id for test_case in test_cases if _is_automation_ready(test_case)}
    manual_ids = {
        test_case.id for test_case in test_cases
        if _parse_tc_metadata(test_case).get("automation_status") == "MANUAL_ONLY"
    }
    reviewed_ids = {test_case.id for test_case in test_cases if test_case.status == "APPROVED"}

    rows = [
        _requirement_coverage_row(
            requirement,
            cases_by_requirement.get(requirement.id, []),
            ready_ids,
            valid_script_case_ids,
            reviewed_ids,
            manual_ids,
        )
        for requirement in requirements
    ]
    by_level = _coverage_by_level(rows)
    covered_requirements = sum(row["policy_compliant"] for row in rows)
    executable_requirements = sum(row["testable"] for row in rows)
    information_gap_requirements = len(rows) - executable_requirements

    scripted_ready_cases = len(ready_ids & valid_script_case_ids)
    stale_scripts = sum(
        script.status == "SUSPECT"
        or script.test_case_id not in cases_by_id
        or script.upstream_tc_hash != cases_by_id[script.test_case_id].content_hash
        for script in scripts
    )
    return {
        "total_requirements": len(requirements),
        "covered_requirements": covered_requirements,
        "coverage_pct": _percentage(covered_requirements, len(requirements)),
        "by_level": by_level,
        "total_test_cases": len(test_cases),
        "total_scripts": len(scripts),
        "executable_requirements": executable_requirements,
        "information_gap_requirements": information_gap_requirements,
        "test_design_coverage_pct": _percentage(covered_requirements, len(requirements)),
        "executable_test_design_coverage_pct": _percentage(covered_requirements, executable_requirements),
        "reviewed_test_cases": len(reviewed_ids),
        "test_review_pct": _percentage(len(reviewed_ids), len(test_cases)),
        "automation_ready_test_cases": len(ready_ids),
        "automation_blocked_test_cases": len(test_cases) - len(ready_ids) - len(manual_ids),
        "manual_test_cases": len(manual_ids),
        "automation_eligibility_pct": _percentage(len(ready_ids), len(test_cases)),
        "scripted_ready_test_cases": scripted_ready_cases,
        "script_coverage_pct": _percentage(scripted_ready_cases, len(ready_ids)),
        "script_coverage_status": "NOT_APPLICABLE" if not ready_ids else "MEASURED",
        "stale_scripts": stale_scripts,
        "requirements": rows,
    }


async def _coverage_data(session: AsyncSession, project_id: uuid.UUID) -> dict:
    requirements = list((await session.scalars(
        select(Requirement).where(
            Requirement.project_id == project_id,
            Requirement.status.notin_(["SUPERSEDED", "REJECTED"]),
        ).order_by(Requirement.req_id)
    )).all())
    test_cases = list((await session.scalars(
        select(TestCase).where(TestCase.project_id == project_id).order_by(TestCase.tc_id)
    )).all())
    scripts = list((await session.scalars(
        select(TestScript).where(TestScript.project_id == project_id).order_by(TestScript.ts_id)
    )).all())
    return build_coverage_summary(requirements, test_cases, scripts)


# Function: get_coverage
@router.get("/projects/{project_id}/coverage")
async def get_coverage(project_id: uuid.UUID, session: AsyncSession = Depends(get_session), user: dict = Depends(current_user)):
    return await _coverage_data(session, project_id)


# Function: get_gaps
@router.get("/projects/{project_id}/gaps")
async def get_gaps(project_id: uuid.UUID, session: AsyncSession = Depends(get_session), user: dict = Depends(current_user)):
    coverage = await _coverage_data(session, project_id)
    gaps = [
        {
            "req_id": row["req_id"], "title": row["title"],
            "category": "TEST_DESIGN", "reasons": row["policy_gaps"] or [row["test_status"]],
        }
        for row in coverage["requirements"]
        if row["testable"] and not row["policy_compliant"]
    ]
    information_gaps = [
        {"req_id": row["req_id"], "title": row["title"], "category": "INFORMATION_GAP"}
        for row in coverage["requirements"]
        if not row["testable"]
    ]
    return {
        "gaps": gaps,
        "count": len(gaps),
        "information_gaps": information_gaps,
        "information_gap_count": len(information_gaps),
    }


# Function: get_costs
@router.get("/projects/{project_id}/costs")
async def get_costs(project_id: uuid.UUID, session: AsyncSession = Depends(get_session), user: dict = Depends(current_user)):
    # LLMCall has no direct project_id column (only pipeline_run_id) — join through PipelineRun.
    result = await session.execute(
        select(LLMCall.agent_name, func.count(LLMCall.id), func.sum(LLMCall.prompt_tokens), func.sum(LLMCall.completion_tokens), func.sum(LLMCall.cost_usd))
        .join(PipelineRun, LLMCall.pipeline_run_id == PipelineRun.id)
        .where(PipelineRun.project_id == project_id)
        .group_by(LLMCall.agent_name)
    )
    rows = result.all()
    return {
        "by_agent": [{"agent": r[0], "calls": r[1], "prompt_tokens": r[2] or 0, "completion_tokens": r[3] or 0, "cost_usd": float(r[4] or 0)} for r in rows],
        "note": "cost_usd is 0 for local Ollama calls — no metered API cost. Budget hard-stops are Phase 4.",
    }
