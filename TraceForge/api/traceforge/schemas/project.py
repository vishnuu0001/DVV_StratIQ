# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: TraceForge — api/traceforge/schemas (project.py)
# Date: 2026-05-19
# ---------------------------------------------------------------------------
from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProjectCreate(BaseModel):
    key: str
    name: str
    client_name: str | None = None
    config: dict = Field(default_factory=dict)


_VALID_GATE_ROLES = {"BUSINESS_ANALYST", "TEST_LEAD", "ARCHITECT", "CLIENT_REVIEWER"}


# Function: _validate_ambiguity_threshold
def _validate_ambiguity_threshold(value: dict) -> None:
    if "ambiguity_threshold" not in value:
        return
    threshold = value["ambiguity_threshold"]
    if not isinstance(threshold, (int, float)) or not 0 <= threshold <= 1:
        raise ValueError("ambiguity_threshold must be between 0 and 1")


# Function: _validate_coverage_policy
def _validate_coverage_policy(value: dict) -> None:
    if "coverage_policy" in value and value["coverage_policy"] not in {"DEFAULT", "STRICT", "REGULATED"}:
        raise ValueError("coverage_policy must be DEFAULT, STRICT, or REGULATED")


# Function: _validate_gate_roles
def _validate_gate_roles(value: dict) -> None:
    """§ Gate RBAC: project.config.gate_roles maps a GateRole persona to the
    usernames who hold it on this project — see orchestration/gates.py for
    enforcement. Left unset, a project keeps the permissive pre-hardening
    behaviour (any authenticated user may decide any gate)."""
    if "gate_roles" not in value:
        return
    gate_roles = value["gate_roles"]
    if not isinstance(gate_roles, dict):
        raise ValueError("gate_roles must be an object mapping role -> [usernames]")
    for role, usernames in gate_roles.items():
        if role not in _VALID_GATE_ROLES:
            raise ValueError(f"gate_roles key '{role}' is not a valid GateRole")
        if not isinstance(usernames, list) or not all(isinstance(u, str) for u in usernames):
            raise ValueError(f"gate_roles['{role}'] must be a list of usernames")


class ProjectConfigPatch(BaseModel):
    config: dict

    # Function: validate_governed_settings
    @field_validator("config")
    @classmethod
    def validate_governed_settings(cls, value: dict) -> dict:
        _validate_ambiguity_threshold(value)
        _validate_coverage_policy(value)
        _validate_gate_roles(value)
        return value


class StartFreshRequest(BaseModel):
    confirmation: str


class ProjectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    key: str
    name: str
    client_name: str | None
    status: str
    config: dict
    created_at: datetime
