# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: §5 Agent 3 (Test Designer) output — real this pass.
# Date: 2026-02-18
# ---------------------------------------------------------------------------
"""§5 Agent 3 (Test Designer) output — real this pass."""
from __future__ import annotations

import io
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
from traceforge.schemas.testcase import TestCaseOut, TestCasePatch, TestPlanOut

router = APIRouter(prefix="/api/v1", tags=["testcases"])


def _safe_filename(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "-", value).strip("-") or "traceforge"


def _download_response(content: bytes, *, media_type: str, filename: str) -> Response:
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def _plan_markdown(project: Project, plan: TestPlan) -> str:
    criteria = plan.entry_exit_criteria or {}
    schedule = plan.schedule or {}

    def bullets(values) -> str:
        return "\n".join(f"- {value}" for value in (values or [])) or "- Not specified"

    return (
        f"# {plan.title}\n\n"
        f"**Project:** {project.key} — {project.name}  \n"
        f"**Status:** {plan.status}  \n"
        f"**Version:** {plan.version}\n\n"
        f"## Scope\n\n{plan.scope}\n\n"
        f"## Strategy\n\n{plan.strategy}\n\n"
        f"## Environments\n\n{bullets(plan.environments)}\n\n"
        f"## Schedule\n\n{bullets(schedule.get('phases', []))}\n\n"
        f"## Entry Criteria\n\n{bullets(criteria.get('entry', []))}\n\n"
        f"## Exit Criteria\n\n{bullets(criteria.get('exit', []))}\n"
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
    for field, value in updates.items():
        setattr(tc, field, value)
    if "steps" in updates or "title" in updates:
        tc.created_by_agent = False
        tc.version += 1
    session.add(AuditEvent(project_id=tc.project_id, actor=user.get("username", "unknown"), action="TESTCASE_EDITED",
                            entity_type="TestCase", entity_id=str(tc.id), before=before, after=updates))
    await session.commit()
    await session.refresh(tc)
    return tc
