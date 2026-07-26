# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Full-text search endpoint.
# Date: 2025-10-18
# ---------------------------------------------------------------------------
"""Full-text search endpoint."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from kg.auth import require_api_key
from kg.db import get_session
from kg.repositories.entity_repo import EntityRepository

router = APIRouter(tags=["search"], dependencies=[Depends(require_api_key)])


class SearchRequest(BaseModel):
    query: str
    kind: str | None = None
    domain: str | None = None
    limit: int = Field(default=20, ge=1, le=200)


# Function: search
@router.post("/search")
async def search(body: SearchRequest) -> Any:
    async with get_session() as session:
        repo = EntityRepository(session)
        results = await repo.search(body.query, body.kind, body.domain, body.limit)
    return {"results": results, "count": len(results)}
