# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Shared PostgreSQL connection and schema helpers for app storage.
# Date: 2026-06-29
# ---------------------------------------------------------------------------
"""Shared PostgreSQL connection and schema helpers for app storage."""
from __future__ import annotations

from contextlib import contextmanager
from threading import Lock
import logging

import backend.config as cfg


_SCHEMA_LOCK = Lock()
_SCHEMA_INITIALIZED = False
_POOL_LOCK = Lock()
_POOL = None
logger = logging.getLogger(__name__)


# Function: postgres_enabled
def postgres_enabled() -> bool:
    return cfg.DB_BACKEND in {"postgres", "postgresql"} and bool(cfg.POSTGRES_DSN.strip())


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

    conn = psycopg.connect(cfg.POSTGRES_DSN)
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
                conninfo=cfg.POSTGRES_DSN,
                min_size=max(1, int(cfg.POSTGRES_POOL_MIN_SIZE)),
                max_size=max(2, int(cfg.POSTGRES_POOL_MAX_SIZE)),
                timeout=float(cfg.POSTGRES_POOL_TIMEOUT_SECONDS),
                kwargs={"autocommit": False},
                open=True,
            )
            logger.info(
                "PostgreSQL pool enabled (min=%s, max=%s)",
                cfg.POSTGRES_POOL_MIN_SIZE,
                cfg.POSTGRES_POOL_MAX_SIZE,
            )
        except Exception as exc:
            _POOL = None
            logger.info("PostgreSQL pool unavailable, using direct connections: %s", exc)
        return _POOL


# Function: ensure_common_schema
def ensure_common_schema(force: bool = False) -> None:
    global _SCHEMA_INITIALIZED

    if _SCHEMA_INITIALIZED and not force:
        return

    with _SCHEMA_LOCK:
        if _SCHEMA_INITIALIZED and not force:
            return

    try:
        import psycopg
    except Exception:
        psycopg = None

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS chat_sessions (
                    session_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    provider TEXT NOT NULL,
                    chat_type TEXT NOT NULL DEFAULT 'general',
                    created_at TIMESTAMPTZ NOT NULL,
                    updated_at TIMESTAMPTZ NOT NULL,
                    expires_at TIMESTAMPTZ NOT NULL
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS chat_messages (
                    id BIGSERIAL PRIMARY KEY,
                    session_id TEXT NOT NULL REFERENCES chat_sessions(session_id) ON DELETE CASCADE,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    sources_json TEXT,
                    confidence DOUBLE PRECISION,
                    context_used BOOLEAN,
                    created_at TIMESTAMPTZ NOT NULL
                )
                """
            )
            cur.execute("CREATE INDEX IF NOT EXISTS idx_chat_sessions_user ON chat_sessions(user_id)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_chat_sessions_expires ON chat_sessions(expires_at)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_chat_sessions_updated ON chat_sessions(updated_at)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_chat_messages_session ON chat_messages(session_id, created_at)")

            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS vector_sync_status (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    last_sync_at TIMESTAMPTZ,
                    source_name TEXT,
                    tickets_fetched INTEGER,
                    chunks_indexed INTEGER,
                    updated_at TIMESTAMPTZ NOT NULL
                )
                """
            )
            cur.execute(
                """
                INSERT INTO vector_sync_status(id, last_sync_at, source_name, tickets_fetched, chunks_indexed, updated_at)
                VALUES (1, NULL, NULL, 0, 0, NOW())
                ON CONFLICT (id) DO NOTHING
                """
            )

            # Enable pgvector and keep runtime vectors in PostgreSQL.
            try:
                cur.execute(
                    """
                    CREATE EXTENSION IF NOT EXISTS vector
                    """
                )
            except Exception as exc:
                if psycopg is not None and isinstance(exc, psycopg.errors.FeatureNotSupported):
                    raise RuntimeError(
                        "pgvector extension is not installed on the PostgreSQL server. "
                        "Install pgvector for this Postgres instance, then run: CREATE EXTENSION vector;"
                    ) from exc
                raise
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS vector_chunks (
                    id TEXT PRIMARY KEY,
                    collection_name TEXT NOT NULL,
                    source TEXT NOT NULL DEFAULT '',
                    document TEXT,
                    metadata_json JSONB,
                    embedding VECTOR(768),
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
                """
            )
            # Migrate untyped VECTOR column to VECTOR(768) for HNSW index support.
            # ALTER TYPE is a no-op if the column already has the correct type.
            try:
                cur.execute("SAVEPOINT before_alter_col")
                cur.execute(
                    "ALTER TABLE vector_chunks ALTER COLUMN embedding TYPE VECTOR(768)"
                )
                cur.execute("RELEASE SAVEPOINT before_alter_col")
            except Exception as _alter_err:
                cur.execute("ROLLBACK TO SAVEPOINT before_alter_col")
                import logging as _lg
                _lg.getLogger(__name__).debug("embedding column type already correct: %s", _alter_err)
            cur.execute(
                "CREATE INDEX IF NOT EXISTS idx_vector_chunks_collection ON vector_chunks(collection_name)"
            )
            cur.execute(
                "CREATE INDEX IF NOT EXISTS idx_vector_chunks_source ON vector_chunks(source)"
            )
            cur.execute(
                "CREATE INDEX IF NOT EXISTS idx_vector_chunks_collection_source ON vector_chunks(collection_name, source)"
            )
            cur.execute(
                "CREATE INDEX IF NOT EXISTS idx_vector_chunks_meta_incident_number ON vector_chunks ((metadata_json->>'incident_number'))"
            )
            cur.execute(
                "CREATE INDEX IF NOT EXISTS idx_vector_chunks_metadata_gin ON vector_chunks USING gin (metadata_json)"
            )
            # ── HNSW approximate nearest-neighbour index (pgvector) ───────────
            # m=16, ef_construction=128 gives ~97% recall on 100k-1M vectors.
            # Silently skipped if the column has no fixed dimension or pgvector < 0.5.
            for _idx_sql in [
                (
                    "CREATE INDEX IF NOT EXISTS idx_vector_chunks_hnsw "
                    "ON vector_chunks USING hnsw (embedding vector_cosine_ops) "
                    "WITH (m = 16, ef_construction = 128)"
                ),
                # ── pg_trgm for O(log N) ILIKE keyword searches ───────────────
                "CREATE EXTENSION IF NOT EXISTS pg_trgm",
                (
                    "CREATE INDEX IF NOT EXISTS idx_vector_chunks_doc_trgm "
                    "ON vector_chunks USING gin (document gin_trgm_ops)"
                ),
            ]:
                try:
                    cur.execute("SAVEPOINT before_optional_idx")
                    cur.execute(_idx_sql)
                    cur.execute("RELEASE SAVEPOINT before_optional_idx")
                except Exception as _idx_err:
                    cur.execute("ROLLBACK TO SAVEPOINT before_optional_idx")
                    import logging as _lg
                    _lg.getLogger(__name__).warning(
                        "Optional index skipped (%s…): %s", _idx_sql[:55], _idx_err
                    )

            # Legacy migration table kept for compatibility with earlier phase-1 migration.
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS vector_chunks_pg (
                    id TEXT PRIMARY KEY,
                    collection_name TEXT NOT NULL,
                    document TEXT,
                    metadata_json TEXT,
                    embedding DOUBLE PRECISION[],
                    migrated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
                """
            )
            cur.execute(
                "CREATE INDEX IF NOT EXISTS idx_vector_chunks_pg_collection ON vector_chunks_pg(collection_name)"
            )

            # ── Modernized ServiceNow operational schema ───────────────────
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS sn_sync_logs (
                    id BIGSERIAL PRIMARY KEY,
                    source_name TEXT NOT NULL,
                    sync_started_at TIMESTAMPTZ NOT NULL,
                    sync_completed_at TIMESTAMPTZ,
                    status TEXT NOT NULL,
                    incidents_count INTEGER NOT NULL DEFAULT 0,
                    requests_count INTEGER NOT NULL DEFAULT 0,
                    kb_count INTEGER NOT NULL DEFAULT 0,
                    qdrant_points_indexed INTEGER NOT NULL DEFAULT 0,
                    details_json JSONB,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS sn_incidents (
                    incident_id TEXT PRIMARY KEY,
                    number TEXT,
                    short_description TEXT,
                    description TEXT,
                    category TEXT,
                    subcategory TEXT,
                    state TEXT,
                    priority TEXT,
                    assignment_group TEXT,
                    assigned_to TEXT,
                    opened_at TEXT,
                    resolved_at TEXT,
                    closed_at TEXT,
                    close_notes TEXT,
                    work_notes TEXT,
                    source_name TEXT,
                    raw_json JSONB,
                    last_synced_at TIMESTAMPTZ NOT NULL,
                    sync_log_id BIGINT REFERENCES sn_sync_logs(id)
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS sn_requests (
                    request_id TEXT PRIMARY KEY,
                    number TEXT,
                    short_description TEXT,
                    description TEXT,
                    state TEXT,
                    assignment_group TEXT,
                    assigned_to TEXT,
                    source_name TEXT,
                    raw_json JSONB,
                    last_synced_at TIMESTAMPTZ NOT NULL,
                    sync_log_id BIGINT REFERENCES sn_sync_logs(id)
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS sn_kb_articles (
                    article_id TEXT PRIMARY KEY,
                    number TEXT,
                    title TEXT,
                    content TEXT,
                    category TEXT,
                    state TEXT,
                    source_name TEXT,
                    raw_json JSONB,
                    last_synced_at TIMESTAMPTZ NOT NULL,
                    sync_log_id BIGINT REFERENCES sn_sync_logs(id)
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS sn_user_metadata (
                    user_name TEXT PRIMARY KEY,
                    last_seen_at TIMESTAMPTZ NOT NULL
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS sn_group_metadata (
                    group_name TEXT PRIMARY KEY,
                    last_seen_at TIMESTAMPTZ NOT NULL
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS sn_category_metadata (
                    category_name TEXT PRIMARY KEY,
                    last_seen_at TIMESTAMPTZ NOT NULL
                )
                """
            )
            cur.execute("CREATE INDEX IF NOT EXISTS idx_sn_incidents_number ON sn_incidents(number)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_sn_incidents_sync_log_id ON sn_incidents(sync_log_id)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_sn_sync_logs_status ON sn_sync_logs(status, created_at DESC)")
        conn.commit()

    _SCHEMA_INITIALIZED = True
