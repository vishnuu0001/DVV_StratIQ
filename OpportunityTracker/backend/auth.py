# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: OpportunityTracker — backend (auth.py)
# Date: 2026-03-30
# ---------------------------------------------------------------------------
import os
import hmac
import hashlib
import base64
import json
import time
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

JWT_SECRET = os.getenv("OT_JWT_SECRET", "ot-secret-change-in-prod-2024")
PORTAL_AUTH_TOKEN_SECRET = (
    os.getenv("AUTH_TOKEN_SECRET")
    or os.getenv("PORTAL_AUTH_TOKEN_SECRET")
    or "change_me_jwt_secret_in_production"
)
TOKEN_TTL = 86400
PORTAL_TOKEN_PREFIX = "v1"
LOCAL_TOKEN_PREFIX = "ot1"
OPPORTUNITY_TRACKER_APP = "OPPORTUNITY_TRACKER"

# Exactly one admin account for this module.
ADMIN_USERNAME = os.getenv("OT_ADMIN_USERNAME", "otadmin")
ADMIN_PASSWORD = os.getenv("OT_ADMIN_PASSWORD", "StratIQ@OT")

_bearer = HTTPBearer(auto_error=False)


# Function: _sign
def _sign(payload: dict) -> str:
    body = base64.urlsafe_b64encode(json.dumps(payload, separators=(",", ":")).encode()).decode().rstrip("=")
    sig = hmac.new(JWT_SECRET.encode(), body.encode(), hashlib.sha256).hexdigest()
    return f"{LOCAL_TOKEN_PREFIX}.{body}.{sig}"


# Function: _decode_body
def _decode_body(body: str) -> dict:
    padding = "=" * ((4 - len(body) % 4) % 4)
    return json.loads(base64.urlsafe_b64decode((body + padding).encode()).decode())


# Function: _verify_local_token
def _verify_local_token(body: str, signature: str) -> dict:
    expected = hmac.new(JWT_SECRET.encode(), body.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(signature, expected):
        raise ValueError("Invalid local token signature")
    return _decode_body(body)


# Function: _verify_portal_token
def _verify_portal_token(body: str, signature: str) -> dict:
    expected = base64.urlsafe_b64encode(
        hmac.new(
            PORTAL_AUTH_TOKEN_SECRET.encode(),
            body.encode(),
            hashlib.sha256,
        ).digest()
    ).decode().rstrip("=")
    if not hmac.compare_digest(signature, expected):
        raise ValueError("Invalid portal token signature")

    payload = _decode_body(body)
    if payload.get("typ") != "access":
        raise ValueError("Invalid portal token type")
    if payload.get("role") != "admin" and OPPORTUNITY_TRACKER_APP not in (payload.get("apps") or []):
        raise HTTPException(status_code=403, detail="Access denied for Opportunity Tracker.")
    return payload


# Function: _verify
def _verify(token: str) -> dict:
    try:
        prefix, body, sig = token.split(".")
        if prefix == LOCAL_TOKEN_PREFIX:
            payload = _verify_local_token(body, sig)
        elif prefix == PORTAL_TOKEN_PREFIX:
            payload = _verify_portal_token(body, sig)
        else:
            raise ValueError("Unsupported token type")
        if int(payload.get("exp", 0)) <= int(time.time()):
            raise ValueError("Token expired")
        return payload
    except HTTPException:
        raise
    except (ValueError, TypeError, json.JSONDecodeError):
        raise HTTPException(status_code=401, detail="Invalid or expired token.") from None


# Function: create_token
def create_token(username: str) -> str:
    return _sign({"sub": username, "role": "admin", "exp": int(time.time()) + TOKEN_TTL})


# Function: authenticate
def authenticate(username: str, password: str) -> dict:
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        return {"username": username, "role": "admin"}
    raise HTTPException(status_code=401, detail="Invalid credentials.")


# Function: get_current_user
def get_current_user(creds: HTTPAuthorizationCredentials = Security(_bearer)) -> dict:
    if not creds:
        raise HTTPException(status_code=401, detail="Not authenticated.")
    return _verify(creds.credentials)
