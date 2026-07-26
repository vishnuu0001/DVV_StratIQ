# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Graph traversal endpoint.
# Date: 2026-02-18
# ---------------------------------------------------------------------------
"""Graph traversal endpoint."""
from __future__ import annotations

from typing import Annotated, Any

import structlog
from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse

from kg.auth import require_api_key
from kg.db import get_session
from kg.repositories.traversal_repo import TraversalRepository

log = structlog.get_logger(__name__)

router = APIRouter(tags=["traverse"], dependencies=[Depends(require_api_key)])


# Function: traverse
@router.get("/traverse")
async def traverse(
    root_id: Annotated[str, Query(description="ID of the root entity")],
    edge_kinds: Annotated[str, Query(description="Comma-separated edge kinds: flow,owns,meta")] = "flow,meta",
    direction: Annotated[str, Query(description="outbound | inbound | both")] = "outbound",
    max_depth: Annotated[int, Query(ge=1, le=10)] = 6,
) -> Any:
    kinds = [k.strip() for k in edge_kinds.split(",") if k.strip()]
    if direction not in ("outbound", "inbound", "both"):
        return JSONResponse(
            status_code=422,
            content={
                "type": "urn:kg:error:validation-error",
                "title": "Validation Error",
                "status": 422,
                "detail": "direction must be one of: outbound, inbound, both",
            },
            media_type="application/problem+json",
        )
    async with get_session() as session:
        repo = TraversalRepository(session)
        result = await repo.traverse(root_id, kinds, direction, max_depth)
    if result["root"] is None:
        return JSONResponse(
            status_code=404,
            content={
                "type": "urn:kg:error:not-found",
                "title": "Not Found",
                "status": 404,
                "detail": f"Root entity id={root_id} not found",
            },
            media_type="application/problem+json",
        )
    return result
