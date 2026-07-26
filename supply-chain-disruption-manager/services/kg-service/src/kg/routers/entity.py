# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Entity CRUD endpoints.
# Date: 2025-11-16
# ---------------------------------------------------------------------------
"""Entity CRUD endpoints."""
from __future__ import annotations

from typing import Annotated, Any

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse

from kg.auth import require_api_key
from kg.db import get_session
from kg.repositories.entity_repo import EntityRepository

log = structlog.get_logger(__name__)

router = APIRouter(prefix="/entity", tags=["entity"], dependencies=[Depends(require_api_key)])


# Function: _problem_response
def _problem_response(status: int, title: str, detail: str) -> JSONResponse:
    return JSONResponse(
        status_code=status,
        content={"type": f"urn:kg:error:{title.lower().replace(' ', '-')}", "title": title, "status": status, "detail": detail},
        media_type="application/problem+json",
    )


# Function: get_entity
@router.get("/{kind}/{id}")
async def get_entity(kind: str, id: str) -> Any:
    async with get_session() as session:
        repo = EntityRepository(session)
        entity = await repo.get_by_kind_and_id(kind, id)
    if entity is None:
        return _problem_response(404, "Not Found", f"Entity kind={kind} id={id} not found")
    return entity


# Function: create_entity
@router.post("/{kind}", status_code=201)
async def create_entity(kind: str, body: dict[str, Any]) -> Any:
    body["kind"] = kind
    async with get_session() as session:
        repo = EntityRepository(session)
        result = await repo.upsert(body)
    return result


# Function: patch_entity
@router.patch("/{kind}/{id}")
async def patch_entity(kind: str, id: str, body: dict[str, Any]) -> Any:
    async with get_session() as session:
        repo = EntityRepository(session)
        result = await repo.patch(kind, id, body)
    if result is None:
        return _problem_response(404, "Not Found", f"Entity kind={kind} id={id} not found")
    return result


# Function: delete_entity
@router.delete("/{kind}/{id}")
async def delete_entity(kind: str, id: str) -> Any:
    async with get_session() as session:
        repo = EntityRepository(session)
        result = await repo.soft_delete(kind, id)
    if result is None:
        return _problem_response(404, "Not Found", f"Entity kind={kind} id={id} not found")
    return result


# Function: list_entities
@router.get("/{kind}")
async def list_entities(
    kind: str,
    status: Annotated[str, Query()] = "ACTIVE",
    limit: Annotated[int, Query(ge=1, le=500)] = 50,
    cursor: Annotated[str | None, Query()] = None,
) -> Any:
    async with get_session() as session:
        repo = EntityRepository(session)
        items, next_cursor = await repo.list_by_kind(kind, status=status, limit=limit, cursor=cursor)
    return {
        "items": items,
        "next_cursor": next_cursor,
        "count": len(items),
    }
