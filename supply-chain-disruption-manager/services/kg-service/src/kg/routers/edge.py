# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Edge creation endpoint.
# Date: 2025-12-02
# ---------------------------------------------------------------------------
"""Edge creation endpoint."""
from __future__ import annotations

from typing import Any

import structlog
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

from kg.auth import require_api_key
from kg.db import get_session
from kg.repositories.edge_repo import EdgeRepository

log = structlog.get_logger(__name__)

router = APIRouter(tags=["edge"], dependencies=[Depends(require_api_key)])


# Function: create_edge
@router.post("/edge", status_code=201)
async def create_edge(body: dict[str, Any]) -> Any:
    """Create or update an edge between two existing entities."""
    required = {"from_id", "to_id", "kind", "verb"}
    missing = required - set(body.keys())
    if missing:
        return JSONResponse(
            status_code=422,
            content={
                "type": "urn:kg:error:validation-error",
                "title": "Validation Error",
                "status": 422,
                "detail": f"Missing required fields: {sorted(missing)}",
            },
            media_type="application/problem+json",
        )
    try:
        async with get_session() as session:
            repo = EdgeRepository(session)
            result = await repo.upsert(body)
        return result
    except ValueError as exc:
        return JSONResponse(
            status_code=404,
            content={
                "type": "urn:kg:error:not-found",
                "title": "Not Found",
                "status": 404,
                "detail": str(exc),
            },
            media_type="application/problem+json",
        )
