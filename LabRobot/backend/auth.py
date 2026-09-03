# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: LabRobot — backend (auth.py)
# Date: 2026-07-21
# ---------------------------------------------------------------------------
"""Shared-platform Bearer token verification — same v1.{payload}.{sig} HMAC
format used by every other Strat-Aqorynth module (ported from the canonical
SSDLC_Process_Assessment/backend/app/auth.py). Unlike that module's copy,
this one has no localhost-origin bypass — LabRobot never had one, so there's
no legacy behavior to preserve, and that bypass mechanism is itself a known
weak point elsewhere on the platform."""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import time

import requests

LABROBOT_APP = "LAB_ROBOT"
# How long past its `exp` a token may still be renewed via /api/auth/refresh
# (main.py) instead of forcing a full re-login through the Portal — mirrors
# Modernization/api/server.py's _REFRESH_GRACE_SECONDS.
REFRESH_GRACE_SECONDS = int(os.getenv("AUTH_REFRESH_GRACE_SECONDS", str(60 * 60)))


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


# Function: decode_token_for_refresh
def decode_token_for_refresh(token: str) -> dict:
    """Same signature check as decode_access_token, but tolerates an `exp`
    that has already passed as long as it's within REFRESH_GRACE_SECONDS —
    the caller already proved they held a legitimately-issued session by
    presenting a token whose HMAC signature checks out; expiry alone isn't
    grounds to make them log in again mid-session."""
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
    if int(payload.get("exp", 0)) <= int(time.time()) - REFRESH_GRACE_SECONDS:
        raise ValueError("Token too old to refresh; sign in again")
    return payload


# Function: issue_access_token
def issue_access_token(payload: dict) -> tuple[str, int]:
    """Reissues a fresh access token for the same identity/role/apps."""
    ttl_seconds = int(os.getenv("AUTH_TOKEN_TTL_SECONDS", str(8 * 60 * 60)))
    exp = int(time.time()) + ttl_seconds
    new_payload = {
        "typ": "access",
        "sub": payload.get("sub"),
        "role": payload.get("role"),
        "apps": payload.get("apps") or [],
        "exp": exp,
    }
    payload_b64 = base64.urlsafe_b64encode(json.dumps(new_payload).encode("utf-8")).rstrip(b"=").decode("ascii")
    signature = (
        base64.urlsafe_b64encode(
            hmac.new(token_secret().encode("utf-8"), payload_b64.encode("utf-8"), hashlib.sha256).digest()
        )
        .rstrip(b"=")
        .decode("ascii")
    )
    return f"v1.{payload_b64}.{signature}", exp


def validate_portal_session(token: str) -> dict:
    """Validate identity, session state, and current rights with the portal.

    This check deliberately fails closed. A locally valid signature is not
    sufficient because the central portal may have revoked the session,
    disabled the user, or changed their application rights.
    """
    validation_url = os.getenv(
        "PORTAL_AUTH_SESSION_URL",
        "https://strat-iq.azurewebsites.net/api/auth/session",
    ).strip()
    timeout_seconds = float(os.getenv("PORTAL_AUTH_TIMEOUT_SECONDS", "5"))
    try:
        response = requests.get(
            validation_url,
            headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
            timeout=max(1.0, min(timeout_seconds, 15.0)),
        )
    except requests.RequestException as exc:
        raise ValueError("Central portal session validation is unavailable") from exc

    if response.status_code == 403:
        raise PermissionError("Access denied by the central portal")
    if response.status_code != 200:
        raise ValueError("Portal session is no longer active")

    data = response.json()
    user = data.get("user") or {}
    if not user.get("is_active", True):
        raise ValueError("Portal user is disabled")
    return data
