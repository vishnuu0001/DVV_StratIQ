# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Shared Strat-Aqorynth auth: validates the same v1.{payload}.{sig} HMAC token every other
# Date: 2025-07-29
# ---------------------------------------------------------------------------
"""Shared Strat-Aqorynth auth: validates the same v1.{payload}.{sig} HMAC token every other
module uses (see SSDLC_Process_Assessment/backend/app/auth.py, Novastra-ITSM's
JWT_SECRET handling). No Entra ID / OIDC in this deployment."""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time

from fastapi import Request

from traceforge.config import ALLOW_LOCAL_AUTH_BYPASS, AUTH_REQUIRED, AUTH_TOKEN_SECRET, TRACEFORGE_APP


# Function: auth_required
def auth_required() -> bool:
    return AUTH_REQUIRED


# Function: allow_local_auth_bypass
def allow_local_auth_bypass() -> bool:
    return ALLOW_LOCAL_AUTH_BYPASS


# Function: is_local_origin
def is_local_origin(request: Request) -> bool:
    # Only trust the verified TCP peer address — the `Origin` header is
    # client-supplied and trivially spoofable by any non-browser HTTP client
    # reaching this port, so it must never be part of a bypass decision.
    host = request.client.host if request.client else ""
    return host in {"127.0.0.1", "::1", "localhost"}


# Function: _b64url_decode
def _b64url_decode(text: str) -> bytes:
    padding = "=" * ((4 - len(text) % 4) % 4)
    return base64.urlsafe_b64decode((text + padding).encode("ascii"))


# Function: _b64url_encode
def _b64url_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


# Function: extract_bearer_token
def extract_bearer_token(authorization_header: str) -> str | None:
    if not authorization_header:
        return None
    parts = authorization_header.split(" ", 1)
    return parts[1].strip() if len(parts) == 2 and parts[0].lower() == "bearer" else None


# Function: decode_access_token
def decode_access_token(token: str) -> dict:
    parts = token.split(".")
    if len(parts) != 3 or parts[0] != "v1":
        raise ValueError("Malformed token")

    payload_encoded = parts[1]
    expected_signature = _b64url_encode(
        hmac.new(AUTH_TOKEN_SECRET.encode("utf-8"), payload_encoded.encode("utf-8"), hashlib.sha256).digest()
    )
    if not hmac.compare_digest(expected_signature, parts[2]):
        raise ValueError("Invalid token signature")

    payload = json.loads(_b64url_decode(payload_encoded).decode("utf-8"))
    if payload.get("typ") != "access":
        raise ValueError("Invalid token type")
    if int(payload.get("exp", 0)) <= int(time.time()):
        raise ValueError("Token expired")
    return payload


# Function: current_user
def current_user(request: Request) -> dict:
    """FastAPI dependency: returns the auth payload set by the enforce_auth middleware."""
    auth = getattr(request.state, "auth", None)
    return auth or {"uid": 0, "username": "local-admin", "role": "admin", "apps": [TRACEFORGE_APP]}
