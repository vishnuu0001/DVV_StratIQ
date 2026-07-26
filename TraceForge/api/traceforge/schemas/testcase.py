# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: TraceForge — api/traceforge/schemas (testcase.py)
# Date: 2025-10-30
# ---------------------------------------------------------------------------
from __future__ import annotations

import uuid

from pydantic import BaseModel, ConfigDict


class TestPlanOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    scope: str
    strategy: str
    environments: list
    schedule: dict
    entry_exit_criteria: dict
    status: str
    version: int

class TestCaseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tc_id: str
    project_id: uuid.UUID
    requirement_id: uuid.UUID
    title: str
    test_type: str
    test_level: str
    preconditions: list
    steps: list
    gherkin: str | None
    priority: str
    status: str
    version: int
    created_by_agent: bool

class TestCasePatch(BaseModel):
    title: str | None = None
    test_type: str | None = None
    test_level: str | None = None
    priority: str | None = None
    steps: list | None = None
    status: str | None = None
