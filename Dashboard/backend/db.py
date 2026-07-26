# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: PostgreSQL connection pool for encrypted settings persistence.
# Date: 2026-07-24
# ---------------------------------------------------------------------------
"""PostgreSQL connection pool for encrypted settings persistence.

Same psycopg + psycopg_pool pattern as Novastra-ITSM's
backend/services/postgres_store.py, so both modules share operational
conventions even though Dashboard previously had no DB access at all.
"""
from __future__ import annotations

from contextlib import contextmanager
from threading import Lock
import logging

from config import settings

_POOL_LOCK = Lock()
_POOL = None
logger = logging.getLogger(__name__)


# Function: get_connection
@contextmanager
def get_connection():
    try:
        import psycopg
    except Exception as exc:
        raise RuntimeError(
            "psycopg is required for PostgreSQL storage. Install backend requirements."
        ) from exc

    pool = _get_pool()
    if pool is not None:
        with pool.connection() as conn:
            yield conn
        return

    conn = psycopg.connect(settings.POSTGRES_DSN)
    try:
        yield conn
    finally:
        conn.close()


# Function: _get_pool
def _get_pool():
    global _POOL
    if _POOL is not None:
        return _POOL

    with _POOL_LOCK:
        if _POOL is not None:
            return _POOL
        try:
            from psycopg_pool import ConnectionPool

            _POOL = ConnectionPool(
                conninfo=settings.POSTGRES_DSN,
                # No floor at 1: with a bad/placeholder password, min_size>=1 makes the
                # pool's background worker retry-and-fail in a tight loop indefinitely
                # (observed in production as a warning every 1-2s) — min_size=0 means
                # it only opens a connection on demand, never proactively.
                min_size=max(0, int(settings.POSTGRES_POOL_MIN_SIZE)),
                max_size=max(2, int(settings.POSTGRES_POOL_MAX_SIZE)),
                timeout=float(settings.POSTGRES_POOL_TIMEOUT_SECONDS),
                kwargs={"autocommit": False},
                open=True,
            )
            logger.info(
                "PostgreSQL pool enabled (min=%s, max=%s)",
                settings.POSTGRES_POOL_MIN_SIZE,
                settings.POSTGRES_POOL_MAX_SIZE,
            )
        except Exception as exc:
            _POOL = None
            logger.info("PostgreSQL pool unavailable, using direct connections: %s", exc)
        return _POOL
