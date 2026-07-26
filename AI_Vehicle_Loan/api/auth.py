# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: AI_Vehicle_Loan — api (auth.py)
# Date: 2026-07-21
# ---------------------------------------------------------------------------
"""Shared-platform Bearer token verification — same v1.{payload}.{sig} HMAC
format used by every other Strat-Aqorynth module (ported from the canonical
SSDLC_Process_Assessment/backend/app/auth.py). No localhost-origin bypass —
this module never had one, so there's no legacy behavior to preserve."""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import time

AI_VEHICLE_LOAN_APP = "AI_VEHICLE_LOAN"


# Function: auth_required
def auth_required() -> bool:
    return os.getenv("AUTH_REQUIRED", "true").lower() in {"1", "true", "yes"}


# Function: token_secret
def token_secret() -> str:
    return os.getenv("AUTH_TOKEN_SECRET") or os.getenv("SECRET_KEY") or "change_me_jwt_secret_in_production"


# Function: b64url_decode
def b64url_decode(text: str) -> bytes:
    padding = "=" * ((4 - len(text) % 4) % 4)
    return base64.urlsafe_b64decode((text + padding).encode("ascii"))


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
    expected_signature = (
        base64.urlsafe_b64encode(
            hmac.new(token_secret().encode("utf-8"), payload_encoded.encode("utf-8"), hashlib.sha256).digest()
        )
        .rstrip(b"=")
        .decode("ascii")
    )
    if not hmac.compare_digest(expected_signature, parts[2]):
        raise ValueError("Invalid token signature")

    payload = json.loads(b64url_decode(payload_encoded).decode("utf-8"))
    if payload.get("typ") != "access":
        raise ValueError("Invalid token type")
    if int(payload.get("exp", 0)) <= int(time.time()):
        raise ValueError("Token expired")
    return payload
