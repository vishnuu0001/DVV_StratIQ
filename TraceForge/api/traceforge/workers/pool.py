# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Arq connection pool used by the FastAPI process to enqueue jobs onto the worker
# Date: 2026-06-21
# ---------------------------------------------------------------------------
"""Arq connection pool used by the FastAPI process to enqueue jobs onto the worker
(see workers/arq_worker.py — a separate, watchdog-managed process; long-running agent
runs must never execute inside the IIS/uvicorn worker per Requirements.MD §2 Infra table)."""
from __future__ import annotations

from arq import create_pool
from arq.connections import ArqRedis, RedisSettings

from traceforge.config import REDIS_URL

_pool: ArqRedis | None = None


# Function: get_arq_pool
async def get_arq_pool() -> ArqRedis:
    global _pool
    if _pool is None:
        _pool = await create_pool(RedisSettings.from_dsn(REDIS_URL))
    return _pool
