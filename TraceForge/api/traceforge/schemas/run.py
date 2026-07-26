# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: TraceForge — api/traceforge/schemas (run.py)
# Date: 2026-02-17
# ---------------------------------------------------------------------------
from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RunCreate(BaseModel):
    stage: str
    scope: dict = Field(default_factory=dict)


class RunOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    stage: str
    status: str
    stats: dict
    error: str | None
    started_at: datetime | None
    finished_at: datetime | None
    created_at: datetime

class GateDecideRequest(BaseModel):
    decision: str
    rationale: str | None = None
    item_decisions: dict = Field(default_factory=dict)


class GateOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    pipeline_run_id: uuid.UUID
    required_role: str
    decision: str
    decided_by: str | None
    rationale: str | None
    item_decisions: dict
    auto_approve: bool
