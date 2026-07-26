# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Compatibility endpoints used by the local React UI.
# Date: 2026-01-28
# ---------------------------------------------------------------------------
"""Compatibility endpoints used by the local React UI."""
from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse

from kg.auth import require_api_key
from kg.db import get_session
from kg.repositories.entity_repo import EntityRepository
from kg.repositories.traversal_repo import TraversalRepository

router = APIRouter(tags=["ui-compat"], dependencies=[Depends(require_api_key)])


# Function: _problem_response
def _problem_response(status: int, title: str, detail: str) -> JSONResponse:
    return JSONResponse(
        status_code=status,
        content={
            "type": f"urn:kg:error:{title.lower().replace(' ', '-')}",
            "title": title,
            "status": status,
            "detail": detail,
        },
        media_type="application/problem+json",
    )


# Function: list_entities_compat
@router.get("/entities")
async def list_entities_compat(
    kind: Annotated[str, Query(description="Entity kind to list")],
    status: Annotated[str, Query()] = "ACTIVE",
    limit: Annotated[int, Query(ge=1, le=500)] = 50,
    cursor: Annotated[str | None, Query()] = None,
) -> list[dict[str, Any]]:
    async with get_session() as session:
        repo = EntityRepository(session)
        items, _ = await repo.list_by_kind(kind, status=status, limit=limit, cursor=cursor)
    return items


# Function: get_node_compat
@router.get("/nodes/{node_id}")
async def get_node_compat(node_id: str) -> Any:
    async with get_session() as session:
        repo = EntityRepository(session)
        entity = await repo.get_by_id(node_id)
    if entity is None:
        return _problem_response(404, "Not Found", f"Entity id={node_id} not found")
    return entity


# Function: get_node_owners_compat
@router.get("/nodes/{node_id}/owners")
async def get_node_owners_compat(
    node_id: str,
    include_transitive: Annotated[bool, Query(description="Include owners inherited through upstream graph nodes")] = True,
) -> list[dict[str, Any]]:
    async with get_session() as session:
        repo = TraversalRepository(session)
        owners = await repo.get_owners(node_id, include_transitive)
    return owners


# Function: search_compat
@router.get("/search")
async def search_compat(
    q: Annotated[str, Query(description="Search query")],
    kind: Annotated[str | None, Query()] = None,
    domain: Annotated[str | None, Query()] = None,
    limit: Annotated[int, Query(ge=1, le=200)] = 20,
) -> list[dict[str, Any]]:
    async with get_session() as session:
        repo = EntityRepository(session)
        return await repo.search(q, kind, domain, limit)
