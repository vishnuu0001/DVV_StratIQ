# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Persist LLM provider settings (URL/credential fields encrypted) in DB.
# Date: 2026-07-24
# ---------------------------------------------------------------------------
"""Persist LLM provider settings (URL/credential fields encrypted) in DB.

Replaces the previous behavior of api/settings.py mutating backend.config
module globals in memory only (lost on restart, plaintext OpenAI key in a
Python global). Dual-writes SQLite or PostgreSQL, same convention as
sync_status_store.py.
"""
from __future__ import annotations

from datetime import datetime, timezone
import sqlite3
from pathlib import Path
from typing import Any, Dict

import backend.config as cfg
from backend.security.crypto import encrypt_value, decrypt_value
from backend.services.postgres_store import get_connection


SQLITE_DB_PATH = Path(cfg.BASE_DIR) / "llm_settings.db"


# Function: _use_sqlite
def _use_sqlite() -> bool:
    return cfg.DB_BACKEND not in {"postgres", "postgresql"}


# Function: _sqlite_connect
def _sqlite_connect() -> sqlite3.Connection:
    conn = sqlite3.connect(str(SQLITE_DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


# Function: ensure_schema
def ensure_schema() -> None:
    if _use_sqlite():
        with _sqlite_connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS llm_settings (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    llm_provider TEXT NOT NULL,
                    ollama_base_url_enc TEXT,
                    ollama_model TEXT,
                    openai_api_key_enc TEXT,
                    openai_model TEXT,
                    updated_at TEXT NOT NULL,
                    updated_by TEXT
                )
                """
            )
            conn.commit()
        return

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS llm_settings (
                    id SMALLINT PRIMARY KEY DEFAULT 1,
                    llm_provider TEXT NOT NULL,
                    ollama_base_url_enc TEXT,
                    ollama_model TEXT,
                    openai_api_key_enc TEXT,
                    openai_model TEXT,
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    updated_by TEXT
                )
                """
            )
        conn.commit()


# Function: _seed_from_env
def _seed_from_env() -> Dict[str, Any]:
    return {
        "llm_provider": cfg.LLM_PROVIDER,
        "ollama_base_url": cfg.OLLAMA_BASE_URL,
        "ollama_model": cfg.OLLAMA_MODEL,
        "openai_api_key": cfg.OPENAI_API_KEY,
        "openai_model": cfg.OPENAI_MODEL,
    }


# Function: get_llm_settings
def get_llm_settings() -> Dict[str, Any]:
    """Read persisted settings, decrypting URL/credential fields. Seeds the
    row from current .env-derived config on first call (nothing lost when
    this feature is first deployed)."""
    ensure_schema()

    if _use_sqlite():
        with _sqlite_connect() as conn:
            row = conn.execute(
                "SELECT llm_provider, ollama_base_url_enc, ollama_model, "
                "openai_api_key_enc, openai_model FROM llm_settings WHERE id = 1"
            ).fetchone()
        if row is None:
            seeded = _seed_from_env()
            save_llm_settings(**seeded, updated_by="seed")
            return seeded
        return {
            "llm_provider": row["llm_provider"],
            "ollama_base_url": decrypt_value(row["ollama_base_url_enc"]) or "",
            "ollama_model": row["ollama_model"] or "",
            "openai_api_key": decrypt_value(row["openai_api_key_enc"]) or "",
            "openai_model": row["openai_model"] or "",
        }

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT llm_provider, ollama_base_url_enc, ollama_model, "
                "openai_api_key_enc, openai_model FROM llm_settings WHERE id = 1"
            )
            row = cur.fetchone()
        conn.commit()

    if row is None:
        seeded = _seed_from_env()
        save_llm_settings(**seeded, updated_by="seed")
        return seeded
    return {
        "llm_provider": row[0],
        "ollama_base_url": decrypt_value(row[1]) or "",
        "ollama_model": row[2] or "",
        "openai_api_key": decrypt_value(row[3]) or "",
        "openai_model": row[4] or "",
    }


# Function: save_llm_settings
def save_llm_settings(
    *,
    llm_provider: str,
    ollama_base_url: str = "",
    ollama_model: str = "",
    openai_api_key: str = "",
    openai_model: str = "",
    updated_by: str = "settings_api",
) -> None:
    ensure_schema()
    now = datetime.now(tz=timezone.utc)
    ollama_base_url_enc = encrypt_value(ollama_base_url)
    openai_api_key_enc = encrypt_value(openai_api_key)

    if _use_sqlite():
        with _sqlite_connect() as conn:
            conn.execute(
                """
                INSERT INTO llm_settings(
                    id, llm_provider, ollama_base_url_enc, ollama_model,
                    openai_api_key_enc, openai_model, updated_at, updated_by
                )
                VALUES (1, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    llm_provider=excluded.llm_provider,
                    ollama_base_url_enc=excluded.ollama_base_url_enc,
                    ollama_model=excluded.ollama_model,
                    openai_api_key_enc=excluded.openai_api_key_enc,
                    openai_model=excluded.openai_model,
                    updated_at=excluded.updated_at,
                    updated_by=excluded.updated_by
                """,
                (
                    llm_provider,
                    ollama_base_url_enc,
                    ollama_model,
                    openai_api_key_enc,
                    openai_model,
                    now.isoformat(),
                    updated_by,
                ),
            )
            conn.commit()
        return

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO llm_settings(
                    id, llm_provider, ollama_base_url_enc, ollama_model,
                    openai_api_key_enc, openai_model, updated_at, updated_by
                )
                VALUES (1, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    llm_provider=EXCLUDED.llm_provider,
                    ollama_base_url_enc=EXCLUDED.ollama_base_url_enc,
                    ollama_model=EXCLUDED.ollama_model,
                    openai_api_key_enc=EXCLUDED.openai_api_key_enc,
                    openai_model=EXCLUDED.openai_model,
                    updated_at=EXCLUDED.updated_at,
                    updated_by=EXCLUDED.updated_by
                """,
                (
                    llm_provider,
                    ollama_base_url_enc,
                    ollama_model,
                    openai_api_key_enc,
                    openai_model,
                    now,
                    updated_by,
                ),
            )
        conn.commit()
