# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Health check endpoint.
# Date: 2025-09-05
# ---------------------------------------------------------------------------
"""Health check endpoint."""
from __future__ import annotations

from fastapi import APIRouter, Request

from agents.config import get_settings
from agents.kg.client import get_kg_client
from agents.store.database import get_engine

router = APIRouter(tags=["health"])


# Function: health
@router.get("/health")
async def health(request: Request) -> dict:
    """Check connectivity to Postgres, Redis, and KG service."""
    deps: dict[str, dict] = {}

    # Postgres
    try:
        engine = get_engine()
        from sqlalchemy import text
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        deps["postgres"] = {"status": "healthy"}
    except Exception as exc:
        deps["postgres"] = {"status": "unhealthy", "error": str(exc)}

    # Redis
    try:
        redis_client = getattr(request.app.state, "redis", None)
        if redis_client:
            pong = await redis_client.ping()
            deps["redis"] = {"status": "healthy" if pong else "unhealthy"}
        else:
            deps["redis"] = {"status": "not_initialised"}
    except Exception as exc:
        deps["redis"] = {"status": "unhealthy", "error": str(exc)}

    # KG service
    try:
        kg = get_kg_client()
        ok = await kg.health()
        deps["kg_service"] = {"status": "healthy" if ok else "unhealthy"}
    except Exception as exc:
        deps["kg_service"] = {"status": "unhealthy", "error": str(exc)}

    overall = (
        "healthy"
        if all(v.get("status") == "healthy" for v in deps.values())
        else "degraded"
    )
    return {"status": overall, "dependencies": deps}
