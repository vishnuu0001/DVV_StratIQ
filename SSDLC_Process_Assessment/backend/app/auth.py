# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: SSDLC_Process_Assessment — backend/app (auth.py)
# Date: 2026-07-09
# ---------------------------------------------------------------------------
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import time

from fastapi import Request

SSDLC_APP = "SSDLC_PROCESS_ASSESSMENT"


# Function: auth_required
def auth_required() -> bool:
    return os.getenv("AUTH_REQUIRED", "true").lower() in {"1", "true", "yes"}


# Function: allow_local_auth_bypass
def allow_local_auth_bypass() -> bool:
    bypass_requested = os.getenv("ALLOW_LOCAL_AUTH_BYPASS", "false").lower() in {"1", "true", "yes"}
    local_runtime = os.getenv("STRATIQ_RUNTIME_MODE", "").lower() in {"development", "local", "test"}
    # Production IIS reverse-proxy traffic also has a loopback TCP peer. Requiring
    # an explicit local runtime mode prevents a stale launcher setting from
    # turning that production proxy path into an authentication bypass.
    return bypass_requested and local_runtime


# Function: is_local_origin
def is_local_origin(request: Request) -> bool:
    # Only trust the verified TCP peer address — the `Origin` header is
    # client-supplied and trivially spoofable by any non-browser HTTP client
    # reaching this port, so it must never be part of a bypass decision.
    host = request.client.host if request.client else ""
    return host in {"127.0.0.1", "::1", "localhost"}


# Function: token_secret
def token_secret() -> str:
    return os.getenv("AUTH_TOKEN_SECRET") or os.getenv("JWT_SECRET") or "change_me_jwt_secret_in_production"


# Function: b64url_decode
def b64url_decode(text: str) -> bytes:
    padding = "=" * ((4 - len(text) % 4) % 4)
    return base64.urlsafe_b64decode((text + padding).encode("ascii"))


# Function: b64url_encode
def b64url_encode(raw: bytes) -> str:
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
    expected_signature = b64url_encode(
        hmac.new(token_secret().encode("utf-8"), payload_encoded.encode("utf-8"), hashlib.sha256).digest()
    )
    if not hmac.compare_digest(expected_signature, parts[2]):
        raise ValueError("Invalid token signature")

    payload = json.loads(b64url_decode(payload_encoded).decode("utf-8"))
    if payload.get("typ") != "access":
        raise ValueError("Invalid token type")
    if int(payload.get("exp", 0)) <= int(time.time()):
        raise ValueError("Token expired")
    return payload
