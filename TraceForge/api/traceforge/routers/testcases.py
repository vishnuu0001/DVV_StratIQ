# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: §5 Agent 3 (Test Designer) output — real this pass.
# Date: 2026-02-18
# ---------------------------------------------------------------------------
"""§5 Agent 3 (Test Designer) output — real this pass."""
from __future__ import annotations

import hashlib
import io
import json
import re
import uuid

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from traceforge.agents.test_case_excel_generator import format_test_case_workbook
from traceforge.agents.test_plan_docx_generator import generate_test_plan_docx
from traceforge.auth import current_user
from traceforge.db.models import AuditEvent, Project, Requirement, TestCase, TestPlan
from traceforge.db.session import get_session
from traceforge.agents.script_gen.playwright import _parse_tc_metadata, _verified_automation_status
from traceforge.schemas.testcase import AutomationProfileApply, TestCaseOut, TestCasePatch, TestPlanOut

router = APIRouter(prefix="/api/v1", tags=["testcases"])


def _safe_filename(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "-", value).strip("-") or "traceforge"


def _download_response(content: bytes, *, media_type: str, filename: str) -> Response:
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def _test_case_content_hash(test_case: TestCase) -> str:
    payload = {
        "title": test_case.title,
        "test_type": test_case.test_type,
        "test_level": test_case.test_level,
        "preconditions": test_case.preconditions,
        "steps": test_case.steps,
        "priority": test_case.priority,
        "metadata": test_case.gherkin,
        "upstream_req_hash": test_case.upstream_req_hash,
    }
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
    ).hexdigest()


def _automation_profile_blockers(test_case: TestCase, body: AutomationProfileApply) -> list[str]:
    if test_case.test_level != "UI_E2E":
        return [f"{test_case.test_level} requires a matching non-UI runner."]
    if any(
        "[EXECUTION DETAIL BLOCKED" in str(step.get("action", ""))
        or "[PENDING BUSINESS CONFIRMATION" in str(step.get("expected_result", ""))
        for step in (test_case.steps or [])
    ):
        return ["Resolve all blocked and pending execution steps before automation."]
    missing_actions = sum(
        not str(body.locators.get(str(step.get("action", "")).strip(), "")).strip()
        for step in (test_case.steps or [])
    )
    missing_assertions = sum(
        not str(body.assertions.get(str(step.get("expected_result", "")).strip(), "")).strip()
        for step in (test_case.steps or [])
    )
    reasons = []
    if missing_actions:
        reasons.append(f"Missing locator bindings for {missing_actions} reviewed action(s).")
    if missing_assertions:
        reasons.append(f"Missing assertion bindings for {missing_assertions} expected result(s).")
    return reasons


def _plan_markdown(project: Project, plan: TestPlan) -> str:
    criteria = plan.entry_exit_criteria or {}
    schedule = plan.schedule or {}

    def bullets(values) -> str:
        return "\n".join(f"- {value}" for value in (values or [])) or "- Not specified"

    rich_sections = [
        ("Objectives", schedule.get("objectives")),
        ("In Scope", schedule.get("in_scope")),
        ("Out of Scope", schedule.get("out_of_scope")),
        ("Process and Requirement Coverage", schedule.get("process_stages")),
        ("Coverage Model", schedule.get("coverage_model")),
        ("Test Levels", schedule.get("test_levels")),
        ("Test Types", schedule.get("test_types")),
        ("Test Data Strategy", schedule.get("test_data_strategy")),
        ("Role and Access Strategy", schedule.get("role_strategy")),
        ("Environment Strategy", schedule.get("environment_strategy")),
        ("Automation Strategy", schedule.get("automation_strategy")),
        ("Defect Management", schedule.get("defect_management")),
        ("Risks", schedule.get("risks")),
        ("Dependencies", schedule.get("dependencies")),
        ("Assumptions and Decisions Required", schedule.get("assumptions")),
        ("Deliverables", schedule.get("deliverables")),
    ]
    rich_markdown = "".join(
        f"## {heading}\n\n{bullets(values)}\n\n" for heading, values in rich_sections
    )
    return (
        f"# {plan.title}\n\n"
        f"**Project:** {project.key} — {project.name}  \n"
        f"**Status:** {plan.status}  \n"
        f"**Version:** {plan.version}\n\n"
        f"## Scope\n\n{plan.scope}\n\n"
        f"## Strategy\n\n{plan.strategy}\n\n"
        f"## Environments\n\n{bullets(plan.environments)}\n\n"
        f"## Schedule\n\n{bullets(schedule.get('phases', []))}\n\n"
        f"{rich_markdown}"
        f"## Entry Criteria\n\n{bullets(criteria.get('entry', []))}\n\n"
        f"## Exit Criteria\n\n{bullets(criteria.get('exit', []))}\n"
        f"\n## Suspension Criteria\n\n{bullets(criteria.get('suspension', []))}\n"
        f"\n## Resumption Criteria\n\n{bullets(criteria.get('resumption', []))}\n"
    )


# Function: list_testcases
@router.get("/projects/{project_id}/testcases", response_model=list[TestCaseOut])
async def list_testcases(
    project_id: uuid.UUID, requirement_id: uuid.UUID | None = None, test_type: str | None = None, status: str | None = None,
    session: AsyncSession = Depends(get_session), user: dict = Depends(current_user),
):
    stmt = select(TestCase).where(TestCase.project_id == project_id)
    if requirement_id:
        stmt = stmt.where(TestCase.requirement_id == requirement_id)
    if test_type:
        stmt = stmt.where(TestCase.test_type == test_type)
    if status:
        stmt = stmt.where(TestCase.status == status)
    result = await session.execute(stmt.order_by(TestCase.tc_id))
    return list(result.scalars().all())


# Function: get_test_plan
@router.get("/projects/{project_id}/test-plan", response_model=TestPlanOut | None)
async def get_test_plan(project_id: uuid.UUID, session: AsyncSession = Depends(get_session), user: dict = Depends(current_user)):
    result = await session.execute(select(TestPlan).where(TestPlan.project_id == project_id).order_by(TestPlan.created_at.desc()))
    plan = result.scalars().first()
    # An absent plan is normal before TEST_DESIGN runs. JSON null keeps that
    # expected empty state from appearing as a failed request in the browser.
    return plan


@router.get("/projects/{project_id}/test-plan/download")
async def download_test_plan(
    project_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    user: dict = Depends(current_user),
):
    project = await session.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    plan = await session.scalar(
        select(TestPlan).where(TestPlan.project_id == project_id).order_by(TestPlan.created_at.desc()).limit(1)
    )
    if plan is None:
        raise HTTPException(status_code=404, detail="No Test Plan is available to download.")
    filename = f"{_safe_filename(project.key)}-test-plan-v{plan.version}.md"
    return _download_response(
        _plan_markdown(project, plan).encode("utf-8"),
        media_type="text/markdown; charset=utf-8",
        filename=filename,
    )


@router.get("/projects/{project_id}/testcases/download")
async def download_test_cases(
    project_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    user: dict = Depends(current_user),
):
    project = await session.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if there are any test cases
    test_case_count = await session.scalar(
        select(func.count(TestCase.id)).where(TestCase.project_id == project_id)
    )
    if not test_case_count:
        raise HTTPException(status_code=404, detail="No Test Cases are available to download.")
    
    # Generate comprehensive workbook with all sheets
    workbook_bytes = await format_test_case_workbook(session, str(project_id))
    
    filename = f"{_safe_filename(project.key)}-test-cases.xlsx"
    return _download_response(
        workbook_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=filename,
    )


@router.post("/projects/{project_id}/testcases/automation-profile")
async def apply_automation_profile(
    project_id: uuid.UUID,
    body: AutomationProfileApply,
    session: AsyncSession = Depends(get_session),
    user: dict = Depends(current_user),
):
    """Apply non-secret Playwright bindings to explicitly selected reviewed UI cases."""
    test_cases = list((await session.scalars(
        select(TestCase).where(
            TestCase.project_id == project_id,
            TestCase.id.in_(body.test_case_ids),
        ).order_by(TestCase.tc_id)
    )).all())
    if len(test_cases) != len(set(body.test_case_ids)):
        raise HTTPException(status_code=404, detail="One or more selected test cases do not exist in this project.")

    profile = {
        "base_url": str(body.base_url),
        "auth": {"method": body.auth_method},
        "locators": body.locators,
        "assertions": body.assertions,
        "test_data_factory": {"contract": body.test_data_factory},
        "cleanup": {"contract": body.cleanup},
        "worker_isolation": body.worker_isolation,
    }
    ready: list[str] = []
    blocked: list[dict] = []
    for test_case in test_cases:
        reasons = _automation_profile_blockers(test_case, body)
        if reasons:
            blocked.append({"tc_id": test_case.tc_id, "reasons": reasons})
            continue
        metadata = _parse_tc_metadata(test_case)
        metadata["automation_status"] = "READY_FOR_UI_AUTOMATION"
        metadata["automation_context"] = profile
        metadata["parallel_safe"] = body.worker_isolation
        metadata["automation_blockers"] = []
        verified_status, reasons = _verified_automation_status(test_case, metadata)
        if verified_status != "READY_FOR_UI_AUTOMATION":
            blocked.append({"tc_id": test_case.tc_id, "reasons": reasons})
            continue
        test_case.gherkin = json.dumps(metadata, ensure_ascii=False)
        test_case.content_hash = _test_case_content_hash(test_case)
        test_case.created_by_agent = False
        test_case.version += 1
        ready.append(test_case.tc_id)

    session.add(AuditEvent(
        project_id=project_id,
        actor=user.get("username", "unknown"),
        action="AUTOMATION_PROFILE_APPLIED",
        entity_type="TestCase",
        entity_id=str(project_id),
        before=None,
        after={
            "selected": len(body.test_case_ids),
            "ready": ready,
            "blocked": blocked,
            "base_url": str(body.base_url),
            "auth_method": body.auth_method,
            "worker_isolation": body.worker_isolation,
        },
    ))
    await session.commit()
    return {"selected": len(body.test_case_ids), "ready": ready, "blocked": blocked}


@router.get("/projects/{project_id}/test-plan/download-docx")
async def download_test_plan_docx(
    project_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    user: dict = Depends(current_user),
):
    """Download comprehensive test plan as DOCX document."""
    project = await session.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    
    plan = await session.scalar(
        select(TestPlan).where(TestPlan.project_id == project_id).order_by(TestPlan.created_at.desc()).limit(1)
    )
    if plan is None:
        raise HTTPException(status_code=404, detail="No Test Plan is available to download.")
    
    # Generate comprehensive DOCX document
    docx_path = await generate_test_plan_docx(session, project_id=project_id, test_plan=plan, pipeline_run_id=None)
    
    filename = f"{_safe_filename(project.key)}_Test_Plan_v{plan.version}.docx"
    with open(docx_path, "rb") as f:
        content = f.read()
    
    return _download_response(
        content,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=filename,
    )


# Function: patch_testcase
@router.patch("/testcases/{tc_id}", response_model=TestCaseOut)
async def patch_testcase(tc_id: uuid.UUID, body: TestCasePatch, session: AsyncSession = Depends(get_session), user: dict = Depends(current_user)):
    tc = await session.get(TestCase, tc_id)
    if not tc:
        raise HTTPException(status_code=404, detail="Test case not found")
    before = {"status": tc.status, "title": tc.title}
    updates = body.model_dump(exclude_unset=True)
    review_metadata = updates.pop("review_metadata", None)
    audit_updates: dict = dict(updates)
    if review_metadata is not None:
        try:
            metadata = json.loads(tc.gherkin or "{}") if (tc.gherkin or "").lstrip().startswith("{") else {}
        except (TypeError, ValueError):
            metadata = {}
        existing_ambiguities = [str(value) for value in metadata.get("ambiguities") or []]
        existing_assumptions = [str(value) for value in metadata.get("assumptions") or []]
        resolution = str(review_metadata.get("resolution") or "").strip()
        if (existing_ambiguities or existing_assumptions) and not resolution:
            raise HTTPException(
                status_code=422,
                detail="A documented resolution is required before clearing ambiguity or assumption metadata.",
            )
        for key in ("systems_involved", "required_roles", "cleanup_instructions"):
            values = review_metadata.get(key)
            if not isinstance(values, list) or not any(str(value).strip() for value in values):
                raise HTTPException(status_code=422, detail=f"{key} must contain at least one confirmed value.")
            metadata[key] = [str(value).strip() for value in values if str(value).strip()]
        if resolution:
            decisions = list(metadata.get("review_decisions") or [])
            decisions.append({
                "resolved_by": user.get("username", "unknown"),
                "resolution": resolution,
                "ambiguities": existing_ambiguities,
                "assumptions": existing_assumptions,
            })
            metadata["review_decisions"] = decisions
            metadata["ambiguities"] = []
            metadata["assumptions"] = []
        tc.gherkin = json.dumps(metadata, ensure_ascii=False)
        tc.created_by_agent = False
        tc.version += 1
        audit_updates["review_metadata"] = review_metadata
    for field, value in updates.items():
        setattr(tc, field, value)
    if "steps" in updates or "title" in updates:
        tc.created_by_agent = False
        tc.version += 1
    if review_metadata is not None or "steps" in updates or "title" in updates:
        tc.content_hash = _test_case_content_hash(tc)
    session.add(AuditEvent(project_id=tc.project_id, actor=user.get("username", "unknown"), action="TESTCASE_EDITED",
                            entity_type="TestCase", entity_id=str(tc.id), before=before, after=audit_updates))
    await session.commit()
    await session.refresh(tc)
    return tc
