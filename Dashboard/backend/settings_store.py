# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Persist ServiceNow connection settings (URL/credentials encrypted) in Postgres.
# Date: 2026-07-24
# ---------------------------------------------------------------------------
"""Persist ServiceNow connection settings (URL/credentials encrypted) in Postgres.

Replaces GET /api/config previously echoing settings.SERVICENOW_* straight
from .env, including the password, in plaintext.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict

from db import get_connection
from security.crypto import encrypt_value, decrypt_value
from config import settings


# Function: ensure_schema
def ensure_schema() -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS dashboard_servicenow_settings (
                    id SMALLINT PRIMARY KEY DEFAULT 1,
                    url_enc TEXT,
                    username_enc TEXT,
                    password_enc TEXT,
                    verify_ssl BOOLEAN NOT NULL DEFAULT true,
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    updated_by TEXT
                )
                """
            )
        conn.commit()


# Function: _seed_from_env
def _seed_from_env() -> Dict[str, Any]:
    return {
        "url": settings.SERVICENOW_BASE_URL or "",
        "username": settings.SERVICENOW_USERNAME or "",
        "password": settings.SERVICENOW_PASSWORD or "",
        "verify_ssl": settings.SERVICENOW_VERIFY_SSL,
    }


# Function: get_servicenow_config
def get_servicenow_config() -> Dict[str, Any]:
    """Read persisted ServiceNow connection settings, decrypted. Seeds the row
    from current .env-derived config on first call."""
    ensure_schema()
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT url_enc, username_enc, password_enc, verify_ssl "
                "FROM dashboard_servicenow_settings WHERE id = 1"
            )
            row = cur.fetchone()
        conn.commit()

    if row is None:
        seeded = _seed_from_env()
        save_servicenow_config(**seeded, updated_by="seed")
        return seeded

    return {
        "url": decrypt_value(row[0]) or "",
        "username": decrypt_value(row[1]) or "",
        "password": decrypt_value(row[2]) or "",
        "verify_ssl": bool(row[3]),
    }


# Function: save_servicenow_config
def save_servicenow_config(
    *,
    url: str = "",
    username: str = "",
    password: str = "",
    verify_ssl: bool = True,
    updated_by: str = "connect_api",
) -> None:
    ensure_schema()
    now = datetime.now(tz=timezone.utc)
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO dashboard_servicenow_settings(
                    id, url_enc, username_enc, password_enc, verify_ssl, updated_at, updated_by
                )
                VALUES (1, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    url_enc=EXCLUDED.url_enc,
                    username_enc=EXCLUDED.username_enc,
                    password_enc=EXCLUDED.password_enc,
                    verify_ssl=EXCLUDED.verify_ssl,
                    updated_at=EXCLUDED.updated_at,
                    updated_by=EXCLUDED.updated_by
                """,
                (
                    encrypt_value(url),
                    encrypt_value(username),
                    encrypt_value(password),
                    bool(verify_ssl),
                    now,
                    updated_by,
                ),
            )
        conn.commit()
