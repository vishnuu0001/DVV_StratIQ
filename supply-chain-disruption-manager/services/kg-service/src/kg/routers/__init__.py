# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Routers package.
# Date: 2026-02-23
# ---------------------------------------------------------------------------
"""Routers package."""
from kg.routers.edge import router as edge_router
from kg.routers.compat import router as compat_router
from kg.routers.entity import router as entity_router
from kg.routers.health import router as health_router
from kg.routers.owners import router as owners_router
from kg.routers.search import router as search_router
from kg.routers.seed import router as seed_router
from kg.routers.traverse import router as traverse_router

__all__ = [
    "health_router",
    "compat_router",
    "entity_router",
    "edge_router",
    "traverse_router",
    "owners_router",
    "search_router",
    "seed_router",
]
