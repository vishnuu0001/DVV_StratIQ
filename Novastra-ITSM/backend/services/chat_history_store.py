# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: PostgreSQL-backed chat history persistence with per-user retention cleanup.
# Date: 2025-11-11
# ---------------------------------------------------------------------------
"""PostgreSQL-backed chat history persistence with per-user retention cleanup."""
from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import backend.config as cfg
from backend.services.postgres_store import ensure_common_schema, get_connection


SQLITE_DB_PATH = Path(cfg.BASE_DIR) / "chat_history.db"

_SQL_DELETE_EXPIRED_SESSIONS = "DELETE FROM chat_sessions WHERE expires_at < ?"
_DEFAULT_TITLE = "New Chat"


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


# Function: _normalize_messages
def _normalize_messages(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    normalized: List[Dict[str, Any]] = []
    for msg in messages:
        role = str(msg.get("role", "")).strip().lower()
        if role not in {"human", "assistant"}:
            continue
        content = str(msg.get("content", "")).strip()
        if not content:
            continue
        normalized.append(
            {
                "role": role,
                "content": content,
                "sources": msg.get("sources") or [],
                "confidence": msg.get("confidence"),
                "context_used": bool(msg.get("context_used", False)),
            }
        )
    return normalized


# Function: _purge_expired
def _purge_expired(cur) -> int:
    cur.execute("DELETE FROM chat_sessions WHERE expires_at < NOW()")
    return int(cur.rowcount or 0)


# Function: ensure_schema
def ensure_schema() -> None:
    if _use_sqlite():
        with _sqlite_connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS chat_sessions (
                    session_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    provider TEXT NOT NULL,
                    chat_type TEXT NOT NULL DEFAULT 'general',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    expires_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS chat_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    sources_json TEXT,
                    confidence REAL,
                    context_used INTEGER,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(session_id) REFERENCES chat_sessions(session_id) ON DELETE CASCADE
                );
                """
            )
        return
    ensure_common_schema()


# Function: _attach_sqlite_session_messages
def _attach_sqlite_session_messages(conn, sessions: List[Dict[str, Any]]) -> None:
    for session in sessions:
        msgs = conn.execute(
            """
            SELECT role, content, sources_json, confidence, context_used, created_at
            FROM chat_messages
            WHERE session_id = ?
            ORDER BY id ASC
            """,
            (session["id"],),
        ).fetchall()
        session["messages"] = [
            {
                "role": m["role"],
                "content": m["content"],
                "sources": json.loads(m["sources_json"]) if m["sources_json"] else [],
                "confidence": m["confidence"],
                "context_used": bool(m["context_used"]) if m["context_used"] is not None else None,
                "created_at": m["created_at"],
            }
            for m in msgs
        ]


# Function: _list_sessions_sqlite
def _list_sessions_sqlite(user_id: str, include_messages: bool, limit: int) -> List[Dict[str, Any]]:
    now = _iso(_utc_now())
    with _sqlite_connect() as conn:
        conn.execute(_SQL_DELETE_EXPIRED_SESSIONS, (now,))
        rows = conn.execute(
            """
            SELECT session_id, user_id, title, provider, chat_type, created_at, updated_at, expires_at
            FROM chat_sessions
            WHERE user_id = ?
            ORDER BY updated_at DESC
            LIMIT ?
            """,
            (user_id, int(limit)),
        ).fetchall()
        sessions = [
            {
                "id": row["session_id"],
                "title": row["title"],
                "provider": row["provider"],
                "chat_type": row["chat_type"],
                "createdAt": row["created_at"],
                "updatedAt": row["updated_at"],
                "expiresAt": row["expires_at"],
                "messages": [],
            }
            for row in rows
        ]
        if include_messages:
            _attach_sqlite_session_messages(conn, sessions)
        conn.commit()
        return sessions


# Function: _attach_postgres_session_messages
def _attach_postgres_session_messages(cur, sessions: List[Dict[str, Any]]) -> None:
    for session in sessions:
        cur.execute(
            """
            SELECT role, content, sources_json, confidence, context_used, created_at
            FROM chat_messages
            WHERE session_id = %s
            ORDER BY id ASC
            """,
            (session["id"],),
        )
        msgs = cur.fetchall()
        session["messages"] = [
            {
                "role": m[0],
                "content": m[1],
                "sources": json.loads(m[2]) if m[2] else [],
                "confidence": m[3],
                "context_used": bool(m[4]) if m[4] is not None else None,
                "created_at": _iso(m[5]),
            }
            for m in msgs
        ]


# Function: _list_sessions_postgres
def _list_sessions_postgres(user_id: str, include_messages: bool, limit: int) -> List[Dict[str, Any]]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            _purge_expired(cur)
            cur.execute(
                """
                SELECT session_id, user_id, title, provider, chat_type, created_at, updated_at, expires_at
                FROM chat_sessions
                WHERE user_id = %s
                ORDER BY updated_at DESC
                LIMIT %s
                """,
                (user_id, int(limit)),
            )
            rows = cur.fetchall()

            sessions: List[Dict[str, Any]] = [
                {
                    "id": row[0],
                    "title": row[2],
                    "provider": row[3],
                    "chat_type": row[4],
                    "createdAt": _iso(row[5]),
                    "updatedAt": _iso(row[6]),
                    "expiresAt": _iso(row[7]),
                    "messages": [],
                }
                for row in rows
            ]

            if include_messages and sessions:
                _attach_postgres_session_messages(cur, sessions)

        conn.commit()
        return sessions


# Function: list_sessions
def list_sessions(user_id: str, include_messages: bool = True, limit: int = 100) -> List[Dict[str, Any]]:
    ensure_schema()
    if _use_sqlite():
        return _list_sessions_sqlite(user_id, include_messages, limit)
    return _list_sessions_postgres(user_id, include_messages, limit)


# Function: create_session
def create_session(user_id: str, title: str, provider: str, chat_type: str = "general") -> Dict[str, Any]:
    ensure_schema()
    now = _utc_now()
    expires = now + timedelta(days=cfg.CHAT_HISTORY_RETENTION_DAYS)
    session_id = str(uuid.uuid4())
    if _use_sqlite():
        with _sqlite_connect() as conn:
            conn.execute(_SQL_DELETE_EXPIRED_SESSIONS, (_iso(now),))
            conn.execute(
                """
                INSERT INTO chat_sessions(session_id, user_id, title, provider, chat_type, created_at, updated_at, expires_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session_id,
                    user_id,
                    title.strip()[:120] or _DEFAULT_TITLE,
                    provider.strip()[:40] or "ollama",
                    chat_type.strip()[:40] or "general",
                    _iso(now),
                    _iso(now),
                    _iso(expires),
                ),
            )
            conn.commit()
        return {
            "id": session_id,
            "title": title.strip()[:120] or _DEFAULT_TITLE,
            "provider": provider.strip()[:40] or "ollama",
            "chat_type": chat_type.strip()[:40] or "general",
            "createdAt": _iso(now),
            "updatedAt": _iso(now),
            "expiresAt": _iso(expires),
            "messages": [],
        }

    with get_connection() as conn:
        with conn.cursor() as cur:
            _purge_expired(cur)
            cur.execute(
                """
                INSERT INTO chat_sessions(session_id, user_id, title, provider, chat_type, created_at, updated_at, expires_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    session_id,
                    user_id,
                    title.strip()[:120] or _DEFAULT_TITLE,
                    provider.strip()[:40] or "ollama",
                    chat_type.strip()[:40] or "general",
                    now,
                    now,
                    expires,
                ),
            )
        conn.commit()

    return {
        "id": session_id,
        "title": title.strip()[:120] or _DEFAULT_TITLE,
        "provider": provider.strip()[:40] or "ollama",
        "chat_type": chat_type.strip()[:40] or "general",
        "createdAt": _iso(now),
        "updatedAt": _iso(now),
        "expiresAt": _iso(expires),
        "messages": [],
    }


# Function: _replace_session_messages_sqlite
def _replace_session_messages_sqlite(
    user_id: str, session_id: str, normalized: List[Dict[str, Any]], title: Optional[str], now, expires
) -> Optional[Dict[str, Any]]:
    with _sqlite_connect() as conn:
        conn.execute(_SQL_DELETE_EXPIRED_SESSIONS, (_iso(now),))
        row = conn.execute(
            "SELECT session_id, title, provider, chat_type, created_at FROM chat_sessions WHERE session_id = ? AND user_id = ?",
            (session_id, user_id),
        ).fetchone()
        if not row:
            conn.commit()
            return None
        next_title = (title.strip()[:120] if title and title.strip() else row["title"]) or _DEFAULT_TITLE
        conn.execute(
            "UPDATE chat_sessions SET title = ?, updated_at = ?, expires_at = ? WHERE session_id = ?",
            (next_title, _iso(now), _iso(expires), session_id),
        )
        conn.execute("DELETE FROM chat_messages WHERE session_id = ?", (session_id,))
        if normalized:
            conn.executemany(
                """
                INSERT INTO chat_messages(session_id, role, content, sources_json, confidence, context_used, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        session_id,
                        m["role"],
                        m["content"],
                        json.dumps(m["sources"], ensure_ascii=True),
                        m["confidence"] if m["confidence"] is None else float(m["confidence"]),
                        1 if m["context_used"] else 0,
                        _iso(now),
                    )
                    for m in normalized
                ],
            )
        conn.commit()
    return {
        "id": row["session_id"],
        "title": next_title,
        "provider": row["provider"],
        "chat_type": row["chat_type"],
        "createdAt": row["created_at"],
        "updatedAt": _iso(now),
        "expiresAt": _iso(expires),
        "messages": normalized,
    }


# Function: _replace_session_messages_postgres
def _replace_session_messages_postgres(
    user_id: str, session_id: str, normalized: List[Dict[str, Any]], title: Optional[str], now, expires
) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            _purge_expired(cur)
            cur.execute(
                "SELECT session_id, title, provider, chat_type, created_at FROM chat_sessions WHERE session_id = %s AND user_id = %s",
                (session_id, user_id),
            )
            row = cur.fetchone()
            if not row:
                conn.commit()
                return None

            next_title = (title.strip()[:120] if title and title.strip() else row[1]) or _DEFAULT_TITLE

            cur.execute(
                "UPDATE chat_sessions SET title = %s, updated_at = %s, expires_at = %s WHERE session_id = %s",
                (next_title, now, expires, session_id),
            )
            cur.execute("DELETE FROM chat_messages WHERE session_id = %s", (session_id,))

            if normalized:
                cur.executemany(
                    """
                    INSERT INTO chat_messages(session_id, role, content, sources_json, confidence, context_used, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    [
                        (
                            session_id,
                            m["role"],
                            m["content"],
                            json.dumps(m["sources"], ensure_ascii=True),
                            m["confidence"] if m["confidence"] is None else float(m["confidence"]),
                            bool(m["context_used"]),
                            now,
                        )
                        for m in normalized
                    ],
                )
        conn.commit()

    return {
        "id": row[0],
        "title": next_title,
        "provider": row[2],
        "chat_type": row[3],
        "createdAt": _iso(row[4]),
        "updatedAt": _iso(now),
        "expiresAt": _iso(expires),
        "messages": normalized,
    }


# Function: replace_session_messages
def replace_session_messages(
    user_id: str,
    session_id: str,
    messages: List[Dict[str, Any]],
    title: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    ensure_schema()
    normalized = _normalize_messages(messages)
    now = _utc_now()
    expires = now + timedelta(days=cfg.CHAT_HISTORY_RETENTION_DAYS)
    if _use_sqlite():
        return _replace_session_messages_sqlite(user_id, session_id, normalized, title, now, expires)
    return _replace_session_messages_postgres(user_id, session_id, normalized, title, now, expires)


# Function: delete_session
def delete_session(user_id: str, session_id: str) -> bool:
    ensure_schema()
    if _use_sqlite():
        with _sqlite_connect() as conn:
            cur = conn.execute("DELETE FROM chat_sessions WHERE session_id = ? AND user_id = ?", (session_id, user_id))
            deleted = bool(cur.rowcount)
            conn.commit()
            return deleted

    with get_connection() as conn:
        with conn.cursor() as cur:
            _purge_expired(cur)
            cur.execute("DELETE FROM chat_sessions WHERE session_id = %s AND user_id = %s", (session_id, user_id))
            deleted = bool(cur.rowcount)
        conn.commit()
        return deleted
