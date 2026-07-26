# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Repositories package.
# Date: 2026-07-04
# ---------------------------------------------------------------------------
"""Repositories package."""
from kg.repositories.edge_repo import EdgeRepository
from kg.repositories.entity_repo import EntityRepository
from kg.repositories.traversal_repo import TraversalRepository

__all__ = ["EntityRepository", "EdgeRepository", "TraversalRepository"]
