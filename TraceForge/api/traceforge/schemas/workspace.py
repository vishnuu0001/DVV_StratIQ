# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: TraceForge — api/traceforge/schemas (workspace.py)
# Date: 2026-07-18
# ---------------------------------------------------------------------------
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class BaselineCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=4000)


class BaselineOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    name: str
    description: str | None
    snapshot: dict[str, Any]
    sha256: str
    created_by: str
    created_at: datetime


class ConnectorConfigUpsert(BaseModel):
    connector_type: str
    config: dict[str, Any] = Field(default_factory=dict)

    # Function: supported_connector
    @field_validator("connector_type")
    @classmethod
    def supported_connector(cls, value: str) -> str:
        normalized = value.strip().upper()
        if normalized not in {"SERVICENOW", "JIRA", "GITHUB"}:
            raise ValueError("connector_type must be SERVICENOW, JIRA, or GITHUB")
        return normalized

    # Function: reject_secrets
    @field_validator("config")
    @classmethod
    def reject_secrets(cls, value: dict[str, Any]) -> dict[str, Any]:
        secret_fragments = ("password", "secret", "token", "api_key", "credential")
        unsafe = [
            key for key in value
            if any(fragment in key.lower() for fragment in secret_fragments)
        ]
        if unsafe:
            raise ValueError(
                "Connector settings cannot store credentials: " + ", ".join(sorted(unsafe))
            )
        return value


class ConnectorConfigOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    connector_type: str
    config: dict[str, Any]
    created_at: datetime


class TemplateOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID | None
    kind: str
    filename: str
    section_map: dict[str, Any]


class ReviewOut(BaseModel):
    id: uuid.UUID
    run_id: uuid.UUID
    stage: str
    required_role: str
    decision: str
    decided_by: str | None
    decided_at: datetime | None
    rationale: str | None
    created_at: datetime
