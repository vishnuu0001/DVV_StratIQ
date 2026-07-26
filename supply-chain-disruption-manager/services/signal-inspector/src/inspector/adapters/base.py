# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Base adapter class and health tracking.
# Date: 2025-11-20
# ---------------------------------------------------------------------------
"""Base adapter class and health tracking."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any

import structlog
from pydantic import BaseModel

logger = structlog.get_logger(__name__)


class AdapterHealth(BaseModel):
    """Health snapshot for an adapter."""

    adapter_name: str
    enabled: bool = True
    status: str = "unknown"  # "healthy" | "degraded" | "error" | "unknown" | "disabled"
    last_event_at: datetime | None = None
    events_last_5m: int = 0
    error_rate_5m: float = 0.0
    message: str = ""
    config: dict[str, Any] = {}


class BaseAdapter:
    """Base class for all signal adapters."""

    name: str = "base"

    # Function: __init__
    def __init__(self, config: dict[str, Any]) -> None:
        self.config = config
        self.enabled: bool = config.get("enabled", False)
        self._health = AdapterHealth(
            adapter_name=self.name,
            enabled=self.enabled,
            status="disabled" if not self.enabled else "unknown",
            config=config,
        )
        self._event_timestamps: list[datetime] = []
        self._error_count_5m: int = 0
        self._total_count_5m: int = 0

    # Function: get_health
    def get_health(self) -> AdapterHealth:
        """Return current health snapshot."""
        self._prune_timestamps()
        self._health.events_last_5m = len(self._event_timestamps)
        if self._total_count_5m > 0:
            self._health.error_rate_5m = self._error_count_5m / self._total_count_5m
        return self._health

    # Function: record_event
    def record_event(self) -> None:
        """Record a successfully processed event."""
        now = datetime.now(timezone.utc)
        self._event_timestamps.append(now)
        self._health.last_event_at = now
        self._total_count_5m += 1
        self._health.status = "healthy"

    # Function: record_error
    def record_error(self, message: str = "") -> None:
        """Record a processing error."""
        self._error_count_5m += 1
        self._total_count_5m += 1
        self._health.status = "degraded"
        if message:
            self._health.message = message

    # Function: _prune_timestamps
    def _prune_timestamps(self) -> None:
        """Remove timestamps older than 5 minutes."""
        cutoff = datetime.now(timezone.utc).timestamp() - 300
        self._event_timestamps = [
            ts for ts in self._event_timestamps if ts.timestamp() > cutoff
        ]

    # Function: start
    async def start(self) -> None:
        """Start the adapter (override for poll/subscribe adapters)."""

    # Function: stop
    async def stop(self) -> None:
        """Stop the adapter (override for poll/subscribe adapters)."""
