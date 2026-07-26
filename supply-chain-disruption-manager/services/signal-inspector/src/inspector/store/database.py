# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: SQLAlchemy async engine and session factory.
# Date: 2025-09-24
# ---------------------------------------------------------------------------
"""SQLAlchemy async engine and session factory."""

from __future__ import annotations

from collections.abc import AsyncGenerator

import structlog
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from inspector.config import get_settings

logger = structlog.get_logger(__name__)

_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


# Function: get_engine
def get_engine() -> AsyncEngine:
    global _engine
    if _engine is None:
        settings = get_settings()
        _engine = create_async_engine(
            settings.postgres_url,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            echo=settings.debug,
        )
    return _engine


# Function: get_session_factory
def get_session_factory() -> async_sessionmaker[AsyncSession]:
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(
            get_engine(),
            expire_on_commit=False,
            class_=AsyncSession,
        )
    return _session_factory


# Function: ensure_schema
async def ensure_schema() -> None:
    """Create local development tables when migrations have not been run."""
    from inspector.store.models import Base

    async with get_engine().begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# Function: get_db_session
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency: yields an AsyncSession."""
    factory = get_session_factory()
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# Function: ping_db
async def ping_db() -> bool:
    """Return True if the database is reachable."""
    from sqlalchemy import text

    try:
        async with get_session_factory()() as session:
            await session.execute(text("SELECT 1"))
        return True
    except Exception:  # noqa: BLE001
        return False


# Function: close_engine
async def close_engine() -> None:
    global _engine
    if _engine:
        await _engine.dispose()
        _engine = None
