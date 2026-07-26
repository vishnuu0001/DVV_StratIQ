# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Coverage dashboard — real this pass (depends on TestCase/TestScript, both real now).
# Date: 2026-06-06
# ---------------------------------------------------------------------------
"""Coverage dashboard — real this pass (depends on TestCase/TestScript, both real now)."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from traceforge.auth import current_user
from traceforge.db.models import LLMCall, PipelineRun, Requirement, TestCase, TestScript
from traceforge.db.session import get_session

router = APIRouter(prefix="/api/v1", tags=["coverage"])


# Function: get_coverage
@router.get("/projects/{project_id}/coverage")
async def get_coverage(project_id: uuid.UUID, session: AsyncSession = Depends(get_session), user: dict = Depends(current_user)):
    requirements = (await session.execute(
        select(Requirement.id, Requirement.level).where(Requirement.project_id == project_id)
    )).all()
    test_cases = (await session.execute(
        select(TestCase.id, TestCase.requirement_id, TestCase.test_type).where(TestCase.project_id == project_id)
    )).all()
    script_case_ids = set((await session.scalars(
        select(TestScript.test_case_id).where(TestScript.project_id == project_id).distinct()
    )).all())

    tc_by_req: dict[uuid.UUID, list[TestCase]] = {}
    for tc in test_cases:
        tc_by_req.setdefault(tc.requirement_id, []).append(tc)

    by_level: dict[str, dict] = {}
    covered = 0
    for req in requirements:
        level_stats = by_level.setdefault(req.level, {"total": 0, "covered": 0})
        level_stats["total"] += 1
        req_tcs = tc_by_req.get(req.id, [])
        has_negative = any(tc.test_type == "NEGATIVE" for tc in req_tcs)
        has_script = any(tc.id in script_case_ids for tc in req_tcs)
        is_covered = bool(req_tcs) and has_negative and has_script
        if is_covered:
            level_stats["covered"] += 1
            covered += 1

    return {
        "total_requirements": len(requirements), "covered_requirements": covered,
        "coverage_pct": round(100 * covered / len(requirements), 1) if requirements else 0,
        "by_level": by_level, "total_test_cases": len(test_cases),
        "total_scripts": await session.scalar(select(func.count()).select_from(TestScript).where(TestScript.project_id == project_id)) or 0,
    }


# Function: get_gaps
@router.get("/projects/{project_id}/gaps")
async def get_gaps(project_id: uuid.UUID, session: AsyncSession = Depends(get_session), user: dict = Depends(current_user)):
    requirements = list((await session.execute(select(Requirement).where(Requirement.project_id == project_id))).scalars().all())
    test_cases = list((await session.execute(select(TestCase).where(TestCase.project_id == project_id))).scalars().all())
    tc_by_req: dict[uuid.UUID, list[TestCase]] = {}
    for tc in test_cases:
        tc_by_req.setdefault(tc.requirement_id, []).append(tc)

    gaps = []
    for req in requirements:
        req_tcs = tc_by_req.get(req.id, [])
        reasons = []
        if not req_tcs:
            reasons.append("NO TESTS")
        elif not any(tc.test_type == "NEGATIVE" for tc in req_tcs):
            reasons.append("NO NEGATIVE")
        if reasons:
            gaps.append({"req_id": req.req_id, "title": req.title, "reasons": reasons})
    return {"gaps": gaps, "count": len(gaps)}


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
