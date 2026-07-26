# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Symmetric encryption for settings values (URLs/credentials) at rest.
# Date: 2026-07-24
# ---------------------------------------------------------------------------
"""Symmetric encryption for settings values (URLs/credentials) at rest."""
from __future__ import annotations

import os
from functools import lru_cache
from typing import Optional

from cryptography.fernet import Fernet, InvalidToken


# Function: _get_fernet
@lru_cache(maxsize=1)
def _get_fernet() -> Fernet:
    key = os.getenv("SETTINGS_ENCRYPTION_KEY", "").strip()
    if not key:
        raise RuntimeError(
            "SETTINGS_ENCRYPTION_KEY is not set. Generate one with: "
            'python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())" '
            "and add it to backend/.env before starting the service."
        )
    try:
        return Fernet(key.encode())
    except Exception as exc:
        raise RuntimeError("SETTINGS_ENCRYPTION_KEY is not a valid Fernet key.") from exc


# Function: encrypt_value
def encrypt_value(plain: Optional[str]) -> Optional[str]:
    if not plain:
        return None
    return _get_fernet().encrypt(plain.encode()).decode()


# Function: decrypt_value
def decrypt_value(token: Optional[str]) -> Optional[str]:
    if not token:
        return None
    try:
        return _get_fernet().decrypt(token.encode()).decode()
    except InvalidToken as exc:
        raise RuntimeError(
            "Failed to decrypt a stored settings value — SETTINGS_ENCRYPTION_KEY may be wrong or changed."
        ) from exc
