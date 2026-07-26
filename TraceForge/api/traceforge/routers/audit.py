# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: TraceForge — api/traceforge/routers (audit.py)
# Date: 2026-02-23
# ---------------------------------------------------------------------------
from __future__ import annotations

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from traceforge.auth import current_user
from traceforge.db.models import AuditEvent
from traceforge.db.session import get_session

router = APIRouter(prefix="/api/v1", tags=["audit"])


class AuditEventOut(BaseModel):
    id: uuid.UUID
    actor: str
    action: str
    entity_type: str
    entity_id: str
    before: dict | None
    after: dict | None
    at: datetime

    class Config:
        from_attributes = True


# Function: get_audit_trail
@router.get("/projects/{project_id}/audit", response_model=list[AuditEventOut])
async def get_audit_trail(
    project_id: uuid.UUID,
    entity_type: str | None = None,
    entity_id: str | None = None,
    session: AsyncSession = Depends(get_session),
    user: dict = Depends(current_user),
):
    stmt = select(AuditEvent).where(AuditEvent.project_id == project_id)
    if entity_type:
        stmt = stmt.where(AuditEvent.entity_type == entity_type)
    if entity_id:
        stmt = stmt.where(AuditEvent.entity_id == entity_id)
    stmt = stmt.order_by(AuditEvent.at.desc()).limit(500)
    result = await session.execute(stmt)
    return list(result.scalars().all())
