# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Neo4j async driver lifecycle and session helpers.
# Date: 2026-06-27
# ---------------------------------------------------------------------------
"""Neo4j async driver lifecycle and session helpers."""
from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

import structlog
from neo4j import AsyncDriver, AsyncGraphDatabase, AsyncSession

from kg.config import get_settings

log = structlog.get_logger(__name__)

_driver: AsyncDriver | None = None

_CONSTRAINTS = [
    "CREATE CONSTRAINT entity_id_unique IF NOT EXISTS FOR (n:Entity) REQUIRE n.id IS UNIQUE",
    "CREATE INDEX entity_kind IF NOT EXISTS FOR (n:Entity) ON (n.kind)",
    "CREATE INDEX entity_domain IF NOT EXISTS FOR (n:Entity) ON (n.domain)",
    "CREATE INDEX entity_status IF NOT EXISTS FOR (n:Entity) ON (n.status)",
]


# Function: init_driver
async def init_driver() -> None:
    """Initialise the Neo4j async driver and apply schema constraints."""
    global _driver  # noqa: PLW0603
    settings = get_settings()
    _driver = AsyncGraphDatabase.driver(
        settings.neo4j_uri,
        auth=(settings.neo4j_user, settings.neo4j_password),
    )
    await _driver.verify_connectivity()
    log.info("neo4j_connected", uri=settings.neo4j_uri)

    async with _driver.session() as session:
        for cypher in _CONSTRAINTS:
            await session.run(cypher)
    log.info("neo4j_schema_applied")


# Function: close_driver
async def close_driver() -> None:
    """Close the Neo4j driver."""
    global _driver  # noqa: PLW0603
    if _driver is not None:
        await _driver.close()
        _driver = None
        log.info("neo4j_disconnected")


# Function: get_driver
def get_driver() -> AsyncDriver:
    if _driver is None:
        raise RuntimeError("Neo4j driver not initialised. Call init_driver() first.")
    return _driver


# Function: get_session
@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Context manager that yields an async Neo4j session."""
    driver = get_driver()
    async with driver.session() as session:
        yield session
