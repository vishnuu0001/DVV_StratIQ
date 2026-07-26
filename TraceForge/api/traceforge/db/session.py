# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Async SQLAlchemy engine/session lifecycle.
# Date: 2026-03-30
# ---------------------------------------------------------------------------
"""Async SQLAlchemy engine/session lifecycle."""
from __future__ import annotations

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from traceforge.config import DATABASE_URL

engine = create_async_engine(DATABASE_URL, pool_size=10, max_overflow=10)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


# Function: get_session
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session
