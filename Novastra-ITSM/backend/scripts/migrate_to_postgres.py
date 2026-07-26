# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Migrate SQLite + legacy vector data into PostgreSQL runtime tables.
# Date: 2025-12-02
# ---------------------------------------------------------------------------
"""Migrate SQLite + legacy vector data into PostgreSQL runtime tables.

Usage:
    python -m backend.scripts.migrate_to_postgres
    python -m backend.scripts.migrate_to_postgres --skip-chat --skip-sync --skip-vectors
"""
from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path

import backend.config as cfg
from backend.services.postgres_store import ensure_common_schema, get_connection


# Function: migrate_chat_history
def migrate_chat_history() -> tuple[int, int]:
    src = Path(cfg.BASE_DIR) / "chat_history.db"
    if not src.exists():
        return 0, 0

    sessions = 0
    messages = 0

    with sqlite3.connect(str(src)) as sconn:
        sconn.row_factory = sqlite3.Row
        session_rows = sconn.execute(
            "SELECT session_id, user_id, title, provider, chat_type, created_at, updated_at, expires_at FROM chat_sessions"
        ).fetchall()
        message_rows = sconn.execute(
            "SELECT session_id, role, content, sources_json, confidence, context_used, created_at FROM chat_messages ORDER BY id ASC"
        ).fetchall()

    with get_connection() as pconn:
        with pconn.cursor() as cur:
            for row in session_rows:
                cur.execute(
                    """
                    INSERT INTO chat_sessions(session_id, user_id, title, provider, chat_type, created_at, updated_at, expires_at)
                    VALUES (%s, %s, %s, %s, %s, %s::timestamptz, %s::timestamptz, %s::timestamptz)
                    ON CONFLICT (session_id) DO UPDATE
                    SET user_id = EXCLUDED.user_id,
                        title = EXCLUDED.title,
                        provider = EXCLUDED.provider,
                        chat_type = EXCLUDED.chat_type,
                        created_at = EXCLUDED.created_at,
                        updated_at = EXCLUDED.updated_at,
                        expires_at = EXCLUDED.expires_at
                    """,
                    (
                        row["session_id"],
                        row["user_id"],
                        row["title"],
                        row["provider"],
                        row["chat_type"],
                        row["created_at"],
                        row["updated_at"],
                        row["expires_at"],
                    ),
                )
                sessions += 1

            # Replace message rows for migrated sessions to avoid duplicates.
            migrated_session_ids = [r["session_id"] for r in session_rows]
            if migrated_session_ids:
                cur.execute("DELETE FROM chat_messages WHERE session_id = ANY(%s)", (migrated_session_ids,))

            for row in message_rows:
                cur.execute(
                    """
                    INSERT INTO chat_messages(session_id, role, content, sources_json, confidence, context_used, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s::timestamptz)
                    """,
                    (
                        row["session_id"],
                        row["role"],
                        row["content"],
                        row["sources_json"],
                        row["confidence"],
                        bool(row["context_used"]) if row["context_used"] is not None else None,
                        row["created_at"],
                    ),
                )
                messages += 1
        pconn.commit()

    return sessions, messages


# Function: migrate_sync_status
def migrate_sync_status() -> bool:
    src = Path(cfg.BASE_DIR) / "sync_status.db"
    if not src.exists():
        return False

    with sqlite3.connect(str(src)) as sconn:
        sconn.row_factory = sqlite3.Row
        row = sconn.execute(
            "SELECT last_sync_at, source_name, tickets_fetched, chunks_indexed, updated_at FROM vector_sync_status WHERE id = 1"
        ).fetchone()

    if not row:
        return False

    with get_connection() as pconn:
        with pconn.cursor() as cur:
            cur.execute(
                """
                UPDATE vector_sync_status
                SET last_sync_at = %s::timestamptz,
                    source_name = %s,
                    tickets_fetched = %s,
                    chunks_indexed = %s,
                    updated_at = COALESCE(%s::timestamptz, NOW())
                WHERE id = 1
                """,
                (
                    row["last_sync_at"],
                    row["source_name"],
                    int(row["tickets_fetched"] or 0),
                    int(row["chunks_indexed"] or 0),
                    row["updated_at"],
                ),
            )
        pconn.commit()

    return True


# Function: _to_vector_literal
def _to_vector_literal(values: list[float]) -> str:
    return "[" + ",".join(f"{float(v):.8f}" for v in values) + "]"


# Function: migrate_vectors
def migrate_vectors() -> int:
    """Move vectors from legacy table vector_chunks_pg to runtime table vector_chunks."""
    migrated = 0
    with get_connection() as pconn:
        with pconn.cursor() as cur:
            cur.execute("SELECT id, collection_name, document, metadata_json, embedding FROM vector_chunks_pg")
            rows = cur.fetchall()
            for row in rows:
                chunk_id, collection_name, document, metadata_json, embedding = row
                embedding_list = [float(x) for x in (embedding or [])]
                if not embedding_list:
                    continue
                source = ""
                try:
                    parsed_meta = json.loads(metadata_json) if metadata_json else {}
                    source = str(parsed_meta.get("source", "") or "")
                except Exception:
                    parsed_meta = {}
                cur.execute(
                    """
                    INSERT INTO vector_chunks(id, collection_name, source, document, metadata_json, embedding, updated_at)
                    VALUES (%s, %s, %s, %s, %s::jsonb, %s::vector, NOW())
                    ON CONFLICT (id) DO UPDATE
                    SET collection_name = EXCLUDED.collection_name,
                        source = EXCLUDED.source,
                        document = EXCLUDED.document,
                        metadata_json = EXCLUDED.metadata_json,
                        embedding = EXCLUDED.embedding,
                        updated_at = NOW()
                    """,
                    (
                        chunk_id,
                        collection_name or cfg.VECTOR_COLLECTION,
                        source,
                        document,
                        json.dumps(parsed_meta, ensure_ascii=True),
                        _to_vector_literal(embedding_list),
                    ),
                )
                migrated += 1
        pconn.commit()
    return migrated


# Function: main
def main() -> None:
    parser = argparse.ArgumentParser(description="Migrate SQLite and legacy vector data into PostgreSQL")
    parser.add_argument("--skip-chat", action="store_true")
    parser.add_argument("--skip-sync", action="store_true")
    parser.add_argument("--skip-vectors", action="store_true")
    args = parser.parse_args()

    ensure_common_schema()

    if not args.skip_chat:
        sessions, messages = migrate_chat_history()
        print(f"chat_history: sessions={sessions}, messages={messages}")

    if not args.skip_sync:
        ok = migrate_sync_status()
        print(f"sync_status: migrated={ok}")

    if not args.skip_vectors:
        vector_count = migrate_vectors()
        print(f"vectors: migrated_chunks={vector_count}")

    print("Migration to PostgreSQL completed.")


if __name__ == "__main__":
    main()
