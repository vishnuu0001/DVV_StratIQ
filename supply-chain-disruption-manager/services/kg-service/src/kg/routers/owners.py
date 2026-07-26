# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Ownership resolution endpoint.
# Date: 2026-05-26
# ---------------------------------------------------------------------------
"""Ownership resolution endpoint."""
from __future__ import annotations

from typing import Annotated, Any

import structlog
from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse

from kg.auth import require_api_key
from kg.db import get_session
from kg.repositories.traversal_repo import TraversalRepository

log = structlog.get_logger(__name__)

router = APIRouter(tags=["owners"], dependencies=[Depends(require_api_key)])


# Function: get_owners
@router.get("/owners")
async def get_owners(
    node_id: Annotated[str, Query(description="ID of the target entity")],
    include_transitive: Annotated[bool, Query(description="Traverse flow/meta edges to find ancestor owners")] = True,
) -> Any:
    async with get_session() as session:
        repo = TraversalRepository(session)
        owners = await repo.get_owners(node_id, include_transitive)
    return {"node_id": node_id, "owners": owners, "count": len(owners)}
