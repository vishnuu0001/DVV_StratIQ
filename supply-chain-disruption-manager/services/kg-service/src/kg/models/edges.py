# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Edge model.
# Date: 2025-11-27
# ---------------------------------------------------------------------------
"""Edge model."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class Edge(BaseModel):
    from_id: str
    to_id: str
    kind: Literal["flow", "owns", "meta"]
    verb: str
    properties: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
