# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: §5 Agent 3 (Test Designer) output — real this pass.
# Date: 2026-02-18
# ---------------------------------------------------------------------------
"""§5 Agent 3 (Test Designer) output — real this pass."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from traceforge.auth import current_user
from traceforge.db.models import AuditEvent, TestCase, TestPlan
from traceforge.db.session import get_session
from traceforge.schemas.testcase import TestCaseOut, TestCasePatch, TestPlanOut

router = APIRouter(prefix="/api/v1", tags=["testcases"])


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
