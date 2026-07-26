# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: SQLAlchemy async engine and session factory.
# Date: 2026-01-23
# ---------------------------------------------------------------------------
"""SQLAlchemy async engine and session factory."""
from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

import structlog
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from agents.config import get_settings

log = structlog.get_logger(__name__)

_engine = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


class Base(DeclarativeBase):
    pass


# Function: init_db
async def init_db() -> None:
    """Initialise async engine and create tables."""
    global _engine, _session_factory  # noqa: PLW0603
    settings = get_settings()

    _engine = create_async_engine(
        settings.postgres_url,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
        echo=settings.debug,
    )
    _session_factory = async_sessionmaker(
        _engine, class_=AsyncSession, expire_on_commit=False
    )
    from agents.store import models  # noqa: F401

    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    log.info("database_connected", url=settings.postgres_url.split("@")[-1])


# Function: close_db
async def close_db() -> None:
    global _engine  # noqa: PLW0603
    if _engine is not None:
        await _engine.dispose()
        _engine = None
        log.info("database_disconnected")


# Function: get_engine
def get_engine():
    if _engine is None:
        raise RuntimeError("Database not initialised. Call init_db() first.")
    return _engine


# Function: get_session_factory
def get_session_factory() -> async_sessionmaker[AsyncSession]:
    if _session_factory is None:
        raise RuntimeError("Database not initialised. Call init_db() first.")
    return _session_factory


# Function: get_session
@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async database session."""
    factory = get_session_factory()
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
