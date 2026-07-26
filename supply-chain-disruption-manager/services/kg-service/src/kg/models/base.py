# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Base entity model shared by all domain models.
# Date: 2026-01-19
# ---------------------------------------------------------------------------
"""Base entity model shared by all domain models."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class BaseEntity(BaseModel):
    id: str
    kind: str
    domain: str
    created_at: datetime
    updated_at: datetime
    status: Literal["ACTIVE", "INACTIVE", "DELETED"] = "ACTIVE"
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config = {"populate_by_name": True}
