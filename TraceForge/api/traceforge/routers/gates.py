# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: TraceForge — api/traceforge/routers (gates.py)
# Date: 2025-07-31
# ---------------------------------------------------------------------------
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from traceforge.auth import current_user
from traceforge.db.models import AuditEvent, Gate, PipelineRun
from traceforge.db.session import get_session
from traceforge.orchestration.gates import decide_gate
from traceforge.schemas.run import GateDecideRequest, GateOut

router = APIRouter(prefix="/api/v1", tags=["gates"])


# Function: get_gate
@router.get("/runs/{run_id}/gate", response_model=GateOut)
async def get_gate(run_id: uuid.UUID, session: AsyncSession = Depends(get_session), user: dict = Depends(current_user)):
    result = await session.execute(select(Gate).where(Gate.pipeline_run_id == run_id))
    gate = result.scalars().first()
    if not gate:
        raise HTTPException(status_code=404, detail="No gate open for this run")
    return gate


# Function: decide_run_gate
@router.post("/runs/{run_id}/gate/decide", response_model=GateOut)
async def decide_run_gate(run_id: uuid.UUID, body: GateDecideRequest, session: AsyncSession = Depends(get_session), user: dict = Depends(current_user)):
    result = await session.execute(select(Gate).where(Gate.pipeline_run_id == run_id))
    gate = result.scalars().first()
    if not gate:
        raise HTTPException(status_code=404, detail="No gate open for this run")

    before = {"decision": gate.decision}
    gate = await decide_gate(
        session, gate, decision=body.decision, rationale=body.rationale,
        item_decisions=body.item_decisions, decided_by=user.get("username", "unknown"),
        actor_role=user.get("role", "user"),
    )

    run = await session.get(PipelineRun, gate.pipeline_run_id)
    if run:
        session.add(AuditEvent(project_id=run.project_id, actor=user.get("username", "unknown"), action="GATE_DECIDED",
                                entity_type="Gate", entity_id=str(gate.id), before=before, after={"decision": gate.decision}))
    await session.commit()
    await session.refresh(gate)
    return gate
