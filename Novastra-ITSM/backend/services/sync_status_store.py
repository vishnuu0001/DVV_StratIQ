# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Persist and evaluate vector DB sync freshness for chat gating (PostgreSQL).
# Date: 2026-03-11
# ---------------------------------------------------------------------------
"""Persist and evaluate vector DB sync freshness for chat gating (PostgreSQL)."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import sqlite3
from pathlib import Path
from typing import Any, Dict, Optional

import backend.config as cfg
from backend.services.postgres_store import ensure_common_schema, get_connection
from backend.rag.vectorstore import get_collection_stats


SQLITE_DB_PATH = Path(cfg.BASE_DIR) / "sync_status.db"


# Function: _use_sqlite
def _use_sqlite() -> bool:
    return cfg.DB_BACKEND not in {"postgres", "postgresql"}


# Function: _sqlite_connect
def _sqlite_connect() -> sqlite3.Connection:
    conn = sqlite3.connect(str(SQLITE_DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


# Function: _utc_now
def _utc_now() -> datetime:
    return datetime.now(tz=timezone.utc)


# Function: _iso
def _iso(ts: datetime) -> str:
    return ts.isoformat()


# Function: ensure_schema
def ensure_schema() -> None:
    if _use_sqlite():
        with _sqlite_connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS vector_sync_status (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    last_sync_at TEXT,
                    source_name TEXT,
                    tickets_fetched INTEGER,
                    chunks_indexed INTEGER,
                    updated_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                INSERT OR IGNORE INTO vector_sync_status(id, last_sync_at, source_name, tickets_fetched, chunks_indexed, updated_at)
                VALUES (1, NULL, NULL, 0, 0, ?)
                """,
                (_iso(_utc_now()),),
            )
            conn.commit()
        return
    ensure_common_schema()


# Function: record_sync
def record_sync(source_name: str, tickets_fetched: int, chunks_indexed: int) -> None:
    ensure_schema()
    now = _utc_now()
    if _use_sqlite():
        with _sqlite_connect() as conn:
            conn.execute(
                """
                UPDATE vector_sync_status
                SET last_sync_at = ?, source_name = ?, tickets_fetched = ?, chunks_indexed = ?, updated_at = ?
                WHERE id = 1
                """,
                (_iso(now), (source_name or "")[:255], int(tickets_fetched or 0), int(chunks_indexed or 0), _iso(now)),
            )
            conn.commit()
        return

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE vector_sync_status
                SET last_sync_at = %s, source_name = %s, tickets_fetched = %s, chunks_indexed = %s, updated_at = %s
                WHERE id = 1
                """,
                (
                    now,
                    (source_name or "")[:255],
                    int(tickets_fetched or 0),
                    int(chunks_indexed or 0),
                    now,
                ),
            )
        conn.commit()


# Function: _compute_sync_reason
def _compute_sync_reason(
    has_indexed_data: bool, last_sync_at: Optional[datetime], is_fresh: bool, max_age_hours: int
) -> Optional[str]:
    if not has_indexed_data:
        return "Vector DB has no indexed data."
    if not last_sync_at:
        return "No sync has been recorded yet."
    if not is_fresh:
        return f"Last sync is older than {max_age_hours} hours."
    return None


# Function: _parse_sqlite_last_sync
def _parse_sqlite_last_sync(row) -> Optional[datetime]:
    if not (row and row["last_sync_at"]):
        return None
    try:
        last_sync_at = datetime.fromisoformat(row["last_sync_at"])
    except ValueError:
        return None
    if last_sync_at.tzinfo is None:
        last_sync_at = last_sync_at.replace(tzinfo=timezone.utc)
    return last_sync_at


# Function: _get_sync_status_sqlite
def _get_sync_status_sqlite(max_age_hours: int) -> Dict[str, Any]:
    with _sqlite_connect() as conn:
        row = conn.execute(
            "SELECT last_sync_at, source_name, tickets_fetched, chunks_indexed, updated_at FROM vector_sync_status WHERE id = 1"
        ).fetchone()
        conn.commit()

    last_sync_at = _parse_sqlite_last_sync(row)
    total_chunks = int(row["chunks_indexed"] or 0) if row else 0
    now = _utc_now()
    hours_since_sync = (now - last_sync_at).total_seconds() / 3600.0 if last_sync_at else None
    is_fresh = bool(last_sync_at and (now - last_sync_at) <= timedelta(hours=max_age_hours))
    has_indexed_data = total_chunks > 0
    can_chat = bool(is_fresh and has_indexed_data)
    reason = _compute_sync_reason(has_indexed_data, last_sync_at, is_fresh, max_age_hours)
    return {
        "can_chat": can_chat,
        "requires_sync": not can_chat,
        "is_fresh": is_fresh,
        "max_age_hours": max_age_hours,
        "last_sync_at": _iso(last_sync_at) if last_sync_at else None,
        "hours_since_sync": round(hours_since_sync, 2) if hours_since_sync is not None else None,
        "has_indexed_data": has_indexed_data,
        "total_chunks": total_chunks,
        "source_name": row["source_name"] if row else None,
        "tickets_fetched": int(row["tickets_fetched"] or 0) if row else 0,
        "chunks_indexed": int(row["chunks_indexed"] or 0) if row else 0,
        "reason": reason,
    }


# Function: _get_postgres_total_chunks
def _get_postgres_total_chunks() -> int:
    try:
        stats = get_collection_stats(cfg.LLM_PROVIDER)
        return int(stats.get("total_chunks") or 0)
    except Exception:
        try:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT COUNT(*) FROM vector_chunks")
                    return int(cur.fetchone()[0] or 0)
        except Exception:
            return 0


# Function: _get_sync_status_postgres
def _get_sync_status_postgres(max_age_hours: int) -> Dict[str, Any]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT last_sync_at, source_name, tickets_fetched, chunks_indexed, updated_at FROM vector_sync_status WHERE id = 1"
            )
            row = cur.fetchone()
        conn.commit()

    last_sync_at: Optional[datetime] = row[0] if row else None
    if last_sync_at and last_sync_at.tzinfo is None:
        last_sync_at = last_sync_at.replace(tzinfo=timezone.utc)

    now = _utc_now()
    hours_since_sync: Optional[float] = None
    if last_sync_at is not None:
        hours_since_sync = (now - last_sync_at).total_seconds() / 3600.0

    total_chunks = _get_postgres_total_chunks()

    is_fresh = bool(last_sync_at and (now - last_sync_at) <= timedelta(hours=max_age_hours))
    has_indexed_data = total_chunks > 0
    can_chat = bool(is_fresh and has_indexed_data)
    reason = _compute_sync_reason(has_indexed_data, last_sync_at, is_fresh, max_age_hours)

    return {
        "can_chat": can_chat,
        "requires_sync": not can_chat,
        "is_fresh": is_fresh,
        "max_age_hours": max_age_hours,
        "last_sync_at": _iso(last_sync_at) if last_sync_at else None,
        "hours_since_sync": round(hours_since_sync, 2) if hours_since_sync is not None else None,
        "has_indexed_data": has_indexed_data,
        "total_chunks": total_chunks,
        "source_name": row[1] if row else None,
        "tickets_fetched": int(row[2] or 0) if row else 0,
        "chunks_indexed": int(row[3] or 0) if row else 0,
        "reason": reason,
    }


# Function: get_sync_status
def get_sync_status(max_age_hours: int = 168) -> Dict[str, Any]:
    ensure_schema()
    if _use_sqlite():
        return _get_sync_status_sqlite(max_age_hours)
    return _get_sync_status_postgres(max_age_hours)
