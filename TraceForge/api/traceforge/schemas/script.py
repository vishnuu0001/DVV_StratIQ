# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: TraceForge — api/traceforge/schemas (script.py)
# Date: 2025-12-30
# ---------------------------------------------------------------------------
from __future__ import annotations

import uuid

from pydantic import BaseModel


class TestScriptOut(BaseModel):
    id: uuid.UUID
    ts_id: str
    project_id: uuid.UUID
    test_case_id: uuid.UUID
    target: str
    language: str
    code: str
    file_path: str
    compiles: bool | None
    validation_output: str | None
    status: str
    version: int

    class Config:
        from_attributes = True


class TestScriptPatch(BaseModel):
    code: str | None = None
    status: str | None = None


class ArtifactOut(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    kind: str
    filename: str
    sha256: str
    version: int
    stale: bool
    requirement_ids: list

    class Config:
        from_attributes = True
