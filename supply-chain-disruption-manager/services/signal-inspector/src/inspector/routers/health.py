# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: GET /health — liveness and readiness probe.
# Date: 2026-01-17
# ---------------------------------------------------------------------------
"""GET /health — liveness and readiness probe."""

from __future__ import annotations

from datetime import datetime, timezone

import structlog
from fastapi import APIRouter, Request
from pydantic import BaseModel

from inspector.store.database import ping_db

logger = structlog.get_logger(__name__)

router = APIRouter(tags=["health"])


class ComponentHealth(BaseModel):
    status: str
    message: str = ""


class HealthResponse(BaseModel):
    status: str  # "ok" | "degraded" | "error"
    ts: datetime
    components: dict[str, ComponentHealth]
    adapters: list[dict]


# Function: health_check
@router.get("/health", response_model=HealthResponse)
async def health_check(request: Request) -> HealthResponse:
    """Check Redis, Postgres, and adapter health."""
    components: dict[str, ComponentHealth] = {}

    # ── Redis check ────────────────────────────────────────────────────────
    redis = request.app.state.redis
    try:
        ok = await redis.ping()
        components["redis"] = ComponentHealth(
            status="ok" if ok else "error",
            message="" if ok else "ping returned False",
        )
    except Exception as exc:  # noqa: BLE001
        components["redis"] = ComponentHealth(status="error", message=str(exc))

    # ── Postgres check ─────────────────────────────────────────────────────
    try:
        db_ok = await ping_db()
        components["postgres"] = ComponentHealth(
            status="ok" if db_ok else "error"
        )
    except Exception as exc:  # noqa: BLE001
        components["postgres"] = ComponentHealth(status="error", message=str(exc))

    # ── Adapter summary ────────────────────────────────────────────────────
    adapter_manager = request.app.state.adapter_manager
    adapter_healths = adapter_manager.get_all_health()
    adapters_out = [h.model_dump() for h in adapter_healths]

    overall = "ok"
    if any(c.status == "error" for c in components.values()):
        overall = "error"
    elif any(c.status == "degraded" for c in components.values()):
        overall = "degraded"

    return HealthResponse(
        status=overall,
        ts=datetime.now(timezone.utc),
        components=components,
        adapters=adapters_out,
    )
