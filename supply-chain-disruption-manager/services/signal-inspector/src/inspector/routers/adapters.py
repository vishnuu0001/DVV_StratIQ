# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: GET /adapters — list adapter health snapshots.
# Date: 2026-01-04
# ---------------------------------------------------------------------------
"""GET /adapters — list adapter health snapshots."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Request

router = APIRouter(tags=["adapters"])


# Function: list_adapters
@router.get("/adapters")
async def list_adapters(request: Request) -> dict[str, Any]:
    """Return health status for all configured adapters."""
    adapter_manager = request.app.state.adapter_manager
    healths = adapter_manager.get_all_health()
    return {
        "adapters": [h.model_dump() for h in healths],
        "count": len(healths),
    }
