# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Health check endpoint.
# Date: 2026-01-29
# ---------------------------------------------------------------------------
"""Health check endpoint."""
from __future__ import annotations

from fastapi import APIRouter

from kg.db import get_session
from kg.repositories.edge_repo import EdgeRepository
from kg.repositories.entity_repo import EntityRepository

router = APIRouter(tags=["health"])


# Function: health
@router.get("/health")
async def health() -> dict:
    """Check Neo4j connectivity and return node/edge counts."""
    async with get_session() as session:
        entity_repo = EntityRepository(session)
        edge_repo = EdgeRepository(session)
        node_count = await entity_repo.count_nodes()
        edge_count = await edge_repo.count_edges()
    return {
        "status": "ok",
        "neo4j": "connected",
        "node_count": node_count,
        "edge_count": edge_count,
    }
