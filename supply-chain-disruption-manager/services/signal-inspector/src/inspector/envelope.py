# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Canonical event envelope and adapter event models.
# Date: 2026-07-08
# ---------------------------------------------------------------------------
"""Canonical event envelope and adapter event models."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field
from ulid import ULID


SeverityLevel = Literal["info", "low", "med", "high", "critical"]


class CanonicalEvent(BaseModel):
    """The central integration contract for all supply-chain events."""

    event_id: str = Field(default_factory=lambda: str(ULID()))
    schema_version: int = 1
    correlation_id: str | None = None
    event_type: str
    severity: SeverityLevel = "info"
    source_system: str
    source_event_id: str | None = None
    ingested_at: datetime = Field(default_factory=datetime.utcnow)
    source_timestamp: datetime
    root_node_id: str | None = None
    related_node_ids: list[str] = Field(default_factory=list)
    payload: dict[str, Any]
    tags: dict[str, str] = Field(default_factory=dict)

    model_config = {"populate_by_name": True}


class AdapterEvent(BaseModel):
    """Raw event received from any adapter before normalization."""

    raw_payload: dict[str, Any]
    source_system: str
    source_event_id: str | None = None
    event_type: str
    source_timestamp: datetime
    adapter_name: str


class ValidationResult(BaseModel):
    valid: bool
    errors: list[str] = Field(default_factory=list)


class PipelineResult(BaseModel):
    """Outcome of running an AdapterEvent through the normalizer pipeline."""

    canonical: CanonicalEvent | None = None
    skipped: bool = False
    skip_reason: str | None = None
    validation_errors: list[str] = Field(default_factory=list)
    stream_name: str | None = None
    publish_status: str = "pending"
