# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Authentication API backed by SQLite users and signed portal tokens.
# Date: 2025-07-31
# ---------------------------------------------------------------------------
"""
Authentication API backed by SQLite users and signed portal tokens.
"""
import base64
import hashlib
import hmac
import json
import logging
import os
import secrets
import sqlite3
import time
from pathlib import Path
from typing import Optional

import bcrypt as _bcrypt
import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

import backend.config as cfg

router = APIRouter(prefix="/api/auth", tags=["Auth"])
logger = logging.getLogger(__name__)
bearer_scheme = HTTPBearer(auto_error=False)

AUTH_DB_PATH = Path(cfg.BASE_DIR) / "portal_auth.sqlite3"
TOKEN_TTL_SECONDS = int(getattr(cfg, "JWT_EXPIRE_SECONDS", 86400))
DEFAULT_APPS = [
    "APP_RATIONALIZATION",
    "CODE_ANALYSIS",
    "INFRA_SCAN",
    "MODERNIZATION",
    "AI_PLAYBOOK",
    "NOVASTRA_ITSM",
    "LAB_ROBOT",
    "HOSPITAL_MANAGEMENT_SYSTEM",
    "IMAGE_VISION",
    "ROBOT_AUTOMATION",
    "TOOL_ANALYSIS_QUALIFICATION",
    "DASHBOARD",
    "INTUNE_AUTOMATION",
]

_SQL_INSERT_USER_APP = "INSERT OR IGNORE INTO user_apps (user_id, app_id) VALUES (?, ?)"
_SQL_SELECT_USER_BY_ID = "SELECT * FROM users WHERE id = ?"
_MSG_PASSWORD_TOO_SHORT = "Password must be at least 8 characters"


# Function: _connect
def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(AUTH_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# Function: _hash_password
def _hash_password(plain: str) -> str:
    return _bcrypt.hashpw(plain.encode("utf-8"), _bcrypt.gensalt()).decode("utf-8")


# Function: _verify_password
def _verify_password(plain: str, hashed: str) -> bool:
    try:
        return _bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False


# Function: _b64url_encode
def _b64url_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


# Function: _b64url_decode
def _b64url_decode(text: str) -> bytes:
    padding = "=" * ((4 - len(text) % 4) % 4)
    return base64.urlsafe_b64decode((text + padding).encode("ascii"))


# Function: _token_secret
def _token_secret() -> str:
    return getattr(cfg, "JWT_SECRET", "change_me_jwt_secret_in_production")


# Function: _portal_token_secret
def _portal_token_secret() -> str:
    return getattr(cfg, "PORTAL_AUTH_TOKEN_SECRET", _token_secret())


# Function: _create_token
def _create_token(user_id: str, username: str, role: str, apps: list[str] | None = None) -> str:
    now = int(time.time())
    payload = {
        "typ": "access",
        "uid": user_id,
        "sub": user_id,
        "username": username,
        "role": role,
        "apps": apps or [],
        "iat": now,
        "exp": now + TOKEN_TTL_SECONDS,
    }
    payload_encoded = _b64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signature = _b64url_encode(
        hmac.new(_token_secret().encode("utf-8"), payload_encoded.encode("utf-8"), hashlib.sha256).digest()
    )
    return f"v1.{payload_encoded}.{signature}"


# Function: _decode_token
def _decode_token(token: str, secret: str | None = None) -> dict:
    parts = token.split(".")
    if len(parts) != 3 or parts[0] != "v1":
        raise ValueError("Malformed token")
    payload_encoded = parts[1]
    expected = _b64url_encode(
        hmac.new(
            (secret or _token_secret()).encode("utf-8"),
            payload_encoded.encode("utf-8"),
            hashlib.sha256,
        ).digest()
    )
    if not hmac.compare_digest(expected, parts[2]):
        raise ValueError("Invalid token signature")
    payload = json.loads(_b64url_decode(payload_encoded).decode("utf-8"))
    if payload.get("typ") != "access":
        raise ValueError("Invalid token type")
    if int(payload.get("exp", 0)) <= int(time.time()):
        raise ValueError("Token expired")
    return payload


# Function: _row_to_user
def _row_to_user(row: sqlite3.Row | None) -> dict | None:
    if not row:
        return None
    return {
        "id": row["id"],
        "username": row["username"],
        "email": row["email"] or "",
        "password_hash": row["password_hash"] or "",
        "role": row["role"] or "user",
        "display_name": row["display_name"] or row["username"],
        "avatar_url": row["avatar_url"],
        "provider": row["provider"] or "local",
        "is_active": bool(row["is_active"]),
        "created_at": row["created_at"],
    }


# Function: _user_public
def _user_public(user: dict) -> dict:
    return {
        "id": user["id"],
        "username": user["username"],
        "email": user.get("email", ""),
        "display_name": user.get("display_name") or user["username"],
        "role": user.get("role", "user"),
        "avatar_url": user.get("avatar_url"),
        "provider": user.get("provider", "local"),
        "is_active": bool(user.get("is_active", True)),
        "apps": _get_user_apps(user["id"]),
    }


# Function: _ensure_schema
def _ensure_schema() -> None:
    with _connect() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE,
                password_hash TEXT,
                role TEXT NOT NULL DEFAULT 'user',
                display_name TEXT,
                avatar_url TEXT,
                provider TEXT NOT NULL DEFAULT 'local',
                is_active INTEGER NOT NULL DEFAULT 1,
                created_at REAL NOT NULL
            );
            CREATE TABLE IF NOT EXISTS user_apps (
                user_id TEXT NOT NULL,
                app_id TEXT NOT NULL,
                PRIMARY KEY (user_id, app_id),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS sessions (
                token_hash TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                created_at REAL NOT NULL,
                expires_at REAL NOT NULL,
                revoked_at REAL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
            """
        )
        admin = conn.execute("SELECT * FROM users WHERE lower(username) = lower(?)", ("admin",)).fetchone()
        password_hash = _hash_password("Admin@1234")
        if admin:
            conn.execute(
                """
                UPDATE users
                SET password_hash = ?, role = 'admin', display_name = 'admin', is_active = 1, provider = 'local'
                WHERE id = ?
                """,
                (password_hash, admin["id"]),
            )
            admin_id = admin["id"]
        else:
            admin_id = "user_admin"
            conn.execute(
                """
                INSERT INTO users (id, username, email, password_hash, role, display_name, provider, is_active, created_at)
                VALUES (?, 'admin', 'admin@portal.local', ?, 'admin', 'admin', 'local', 1, ?)
                """,
                (admin_id, password_hash, time.time()),
            )
        conn.executemany(
            _SQL_INSERT_USER_APP,
            [(admin_id, app_id) for app_id in DEFAULT_APPS],
        )
        conn.commit()


# Function: _get_user_by_id
def _get_user_by_id(user_id: str) -> dict | None:
    _ensure_schema()
    with _connect() as conn:
        return _row_to_user(conn.execute(_SQL_SELECT_USER_BY_ID, (user_id,)).fetchone())


# Function: _get_user_apps
def _get_user_apps(user_id: str) -> list[str]:
    _ensure_schema()
    with _connect() as conn:
        rows = conn.execute("SELECT app_id FROM user_apps WHERE user_id = ? ORDER BY app_id", (user_id,)).fetchall()
        return [row["app_id"] for row in rows]


# Function: _store_session
def _store_session(token: str, user_id: str, expires_at: int) -> None:
    digest = hashlib.sha256(token.encode("utf-8")).hexdigest()
    with _connect() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO sessions (token_hash, user_id, created_at, expires_at, revoked_at) VALUES (?, ?, ?, ?, NULL)",
            (digest, user_id, time.time(), float(expires_at)),
        )
        conn.commit()


# Function: _revoke_session
def _revoke_session(token: str) -> None:
    digest = hashlib.sha256(token.encode("utf-8")).hexdigest()
    with _connect() as conn:
        conn.execute("UPDATE sessions SET revoked_at = ? WHERE token_hash = ?", (time.time(), digest))
        conn.commit()


# Function: _is_session_active
def _is_session_active(token: str) -> bool:
    digest = hashlib.sha256(token.encode("utf-8")).hexdigest()
    with _connect() as conn:
        row = conn.execute("SELECT expires_at, revoked_at FROM sessions WHERE token_hash = ?", (digest,)).fetchone()
    return bool(row and not row["revoked_at"] and float(row["expires_at"]) > time.time())


# Function: _extract_token
def _extract_token(credentials: Optional[HTTPAuthorizationCredentials]) -> str | None:
    return credentials.credentials if credentials else None


# Function: get_current_user
def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> dict:
    token = _extract_token(credentials)
    if not token:
        # Only trust the verified TCP peer address — the `Origin` header is
        # client-supplied and trivially spoofable by any non-browser HTTP
        # client reaching this port. The storage backend choice (sqlite vs.
        # postgres) is likewise never a valid signal for "skip auth" — it
        # accidentally made every sqlite-backed deployment unauthenticated
        # regardless of ALLOW_LOCAL_AUTH_BYPASS, so it's been removed here;
        # only ALLOW_LOCAL_AUTH_BYPASS gates the bypass now.
        host = request.client.host if request.client else ""
        local_host = host in {"127.0.0.1", "::1", "localhost"}
        local_bypass = os.getenv("ALLOW_LOCAL_AUTH_BYPASS", "false").lower() in {"1", "true", "yes"}
        if local_bypass and local_host:
            _ensure_schema()
            user = _get_user_by_id("user_admin")
            if user:
                return user
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        payload = _decode_token(token)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid or expired token: {exc}") from exc
    if not _is_session_active(token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired")
    user = _get_user_by_id(payload["uid"])
    if not user or not user.get("is_active"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")
    return user


# Function: require_admin
def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    display_name: Optional[str] = None


class PortalSSORequest(BaseModel):
    portal_token: str


class AdminCreateUserRequest(BaseModel):
    username: str
    password: str
    role: str = "user"
    apps: list[str] = []


class AdminUpdateUserRequest(BaseModel):
    role: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None
    apps: Optional[list[str]] = None


# Function: login
@router.post("/login")
async def login(req: LoginRequest):
    _ensure_schema()
    with _connect() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE lower(username) = lower(?) AND provider = 'local'",
            (req.username,),
        ).fetchone()
    user = _row_to_user(row)
    if not user or not user["is_active"] or not _verify_password(req.password, user.get("password_hash", "")):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    apps = _get_user_apps(user["id"])
    token = _create_token(user["id"], user["username"], user.get("role", "user"), apps)
    _store_session(token, user["id"], _decode_token(token)["exp"])
    return {"access_token": token, "token_type": "bearer", "user": _user_public(user)}


# Function: register
@router.post("/register")
async def register(req: RegisterRequest):
    _ensure_schema()
    if len(req.password) < 8:
        raise HTTPException(status_code=400, detail=_MSG_PASSWORD_TOO_SHORT)
    user_id = f"user_{int(time.time())}_{secrets.token_hex(4)}"
    try:
        with _connect() as conn:
            conn.execute(
                """
                INSERT INTO users (id, username, email, password_hash, role, display_name, provider, is_active, created_at)
                VALUES (?, ?, ?, ?, 'user', ?, 'local', 1, ?)
                """,
                (user_id, req.username, req.email, _hash_password(req.password), req.display_name or req.username, time.time()),
            )
            conn.execute("INSERT INTO user_apps (user_id, app_id) VALUES (?, ?)", (user_id, "NOVASTRA_ITSM"))
            conn.commit()
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=400, detail="Username or email already exists") from exc
    user = _get_user_by_id(user_id)
    token = _create_token(user_id, req.username, "user", _get_user_apps(user_id))
    _store_session(token, user_id, _decode_token(token)["exp"])
    return {"access_token": token, "token_type": "bearer", "user": _user_public(user)}


# Function: get_me
@router.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    return _user_public(current_user)


# Function: session
@router.get("/session")
async def session(current_user: dict = Depends(get_current_user)):
    return {"authenticated": True, "user": _user_public(current_user), "expires_at": None}


# Function: logout
@router.post("/logout")
async def logout(credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme)):
    token = _extract_token(credentials)
    if token:
        _revoke_session(token)
    return {"status": "ok"}


# Function: admin_list_users
@router.get("/admin/users")
async def admin_list_users(current_user: dict = Depends(require_admin)):
    _ensure_schema()
    with _connect() as conn:
        rows = conn.execute("SELECT * FROM users ORDER BY created_at").fetchall()
    users = [_user_public(_row_to_user(row)) for row in rows]
    return {"users": users, "applications": DEFAULT_APPS}


# Function: admin_create_user
@router.post("/admin/users")
async def admin_create_user(req: AdminCreateUserRequest, current_user: dict = Depends(require_admin)):
    _ensure_schema()
    if len(req.password) < 8:
        raise HTTPException(status_code=400, detail=_MSG_PASSWORD_TOO_SHORT)
    role = "admin" if req.role == "admin" else "user"
    user_id = f"user_{int(time.time())}_{secrets.token_hex(4)}"
    app_ids = req.apps or ["NOVASTRA_ITSM"]
    try:
        with _connect() as conn:
            conn.execute(
                """
                INSERT INTO users (id, username, email, password_hash, role, display_name, provider, is_active, created_at)
                VALUES (?, ?, ?, ?, ?, ?, 'local', 1, ?)
                """,
                (
                    user_id,
                    req.username,
                    f"{req.username}@portal.local",
                    _hash_password(req.password),
                    role,
                    req.username,
                    time.time(),
                ),
            )
            conn.executemany(
                _SQL_INSERT_USER_APP,
                [(user_id, app_id) for app_id in app_ids if app_id in DEFAULT_APPS],
            )
            conn.commit()
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=400, detail="Username already exists") from exc
    return {"user": _user_public(_get_user_by_id(user_id))}


# Function: admin_update_user
@router.put("/admin/users/{user_id}")
async def admin_update_user(user_id: str, req: AdminUpdateUserRequest, current_user: dict = Depends(require_admin)):
    _ensure_schema()
    user = _get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    role = req.role if req.role in {"admin", "user"} else None
    with _connect() as conn:
        if role is not None:
            conn.execute("UPDATE users SET role = ? WHERE id = ?", (role, user_id))
        if req.is_active is not None:
            conn.execute("UPDATE users SET is_active = ? WHERE id = ?", (1 if req.is_active else 0, user_id))
        if req.password:
            if len(req.password) < 8:
                raise HTTPException(status_code=400, detail=_MSG_PASSWORD_TOO_SHORT)
            conn.execute("UPDATE users SET password_hash = ? WHERE id = ?", (_hash_password(req.password), user_id))
        if req.apps is not None:
            conn.execute("DELETE FROM user_apps WHERE user_id = ?", (user_id,))
            conn.executemany(
                _SQL_INSERT_USER_APP,
                [(user_id, app_id) for app_id in req.apps if app_id in DEFAULT_APPS],
            )
        conn.commit()
    return {"user": _user_public(_get_user_by_id(user_id))}


# Function: admin_delete_user
@router.delete("/admin/users/{user_id}")
async def admin_delete_user(user_id: str, current_user: dict = Depends(require_admin)):
    if user_id == current_user["id"]:
        raise HTTPException(status_code=400, detail="You cannot delete your own user")
    _ensure_schema()
    with _connect() as conn:
        conn.execute("DELETE FROM user_apps WHERE user_id = ?", (user_id,))
        conn.execute("DELETE FROM sessions WHERE user_id = ?", (user_id,))
        deleted = conn.execute("DELETE FROM users WHERE id = ?", (user_id,)).rowcount
        conn.commit()
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    return {"status": "deleted"}


# Function: get_oauth_providers
@router.get("/oauth/providers")
async def get_oauth_providers():
    return {
        "providers": [
            {"id": "github", "name": "GitHub", "enabled": bool(cfg.GITHUB_CLIENT_ID), "icon": "github"},
            {"id": "google", "name": "Google", "enabled": bool(cfg.GOOGLE_CLIENT_ID), "icon": "google"},
        ]
    }


# Function: github_oauth
@router.get("/github")
async def github_oauth():
    if not cfg.GITHUB_CLIENT_ID:
        raise HTTPException(status_code=501, detail="GitHub OAuth is not configured")
    state = secrets.token_hex(16)
    redirect_uri = f"{cfg.APP_BASE_URL}/api/auth/github/callback"
    return RedirectResponse(
        url=(
            "https://github.com/login/oauth/authorize"
            f"?client_id={cfg.GITHUB_CLIENT_ID}&redirect_uri={redirect_uri}&scope=user:email&state={state}"
        )
    )


# Function: github_callback
@router.get("/github/callback")
async def github_callback(code: str, state: Optional[str] = None):
    if not cfg.GITHUB_CLIENT_ID or not cfg.GITHUB_CLIENT_SECRET:
        raise HTTPException(status_code=501, detail="GitHub OAuth is not configured")
    async with httpx.AsyncClient() as client:
        token_resp = await client.post(
            "https://github.com/login/oauth/access_token",
            json={"client_id": cfg.GITHUB_CLIENT_ID, "client_secret": cfg.GITHUB_CLIENT_SECRET, "code": code},
            headers={"Accept": "application/json"},
        )
        gh_token = token_resp.json().get("access_token")
        if not gh_token:
            raise HTTPException(status_code=400, detail="GitHub OAuth token exchange failed")
        gh_user = (await client.get("https://api.github.com/user", headers={"Authorization": f"Bearer {gh_token}"})).json()
    user = _upsert_oauth_user(f"github_{gh_user['id']}", gh_user["login"], gh_user.get("email", ""), gh_user.get("name"), gh_user.get("avatar_url"), "github")
    token = _create_token(user["id"], user["username"], user.get("role", "user"), _get_user_apps(user["id"]))
    _store_session(token, user["id"], _decode_token(token)["exp"])
    return RedirectResponse(url=f"{_get_frontend_url()}/auth/callback?token={token}")


# Function: google_oauth
@router.get("/google")
async def google_oauth():
    if not cfg.GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=501, detail="Google OAuth is not configured")
    state = secrets.token_hex(16)
    redirect_uri = f"{cfg.APP_BASE_URL}/api/auth/google/callback"
    return RedirectResponse(
        url=(
            "https://accounts.google.com/o/oauth2/v2/auth"
            f"?client_id={cfg.GOOGLE_CLIENT_ID}&redirect_uri={redirect_uri}&response_type=code"
            f"&scope=openid%20email%20profile&state={state}"
        )
    )


# Function: google_callback
@router.get("/google/callback")
async def google_callback(code: str, state: Optional[str] = None):
    if not cfg.GOOGLE_CLIENT_ID or not cfg.GOOGLE_CLIENT_SECRET:
        raise HTTPException(status_code=501, detail="Google OAuth is not configured")
    redirect_uri = f"{cfg.APP_BASE_URL}/api/auth/google/callback"
    async with httpx.AsyncClient() as client:
        token_resp = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": cfg.GOOGLE_CLIENT_ID,
                "client_secret": cfg.GOOGLE_CLIENT_SECRET,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code",
            },
        )
        g_token = token_resp.json().get("access_token")
        if not g_token:
            raise HTTPException(status_code=400, detail="Google OAuth token exchange failed")
        g_user = (await client.get("https://www.googleapis.com/oauth2/v2/userinfo", headers={"Authorization": f"Bearer {g_token}"})).json()
    username = (g_user.get("email") or "").split("@")[0] or f"user_{g_user['id']}"
    user = _upsert_oauth_user(f"google_{g_user['id']}", username, g_user.get("email", ""), g_user.get("name"), g_user.get("picture"), "google")
    token = _create_token(user["id"], user["username"], user.get("role", "user"), _get_user_apps(user["id"]))
    _store_session(token, user["id"], _decode_token(token)["exp"])
    return RedirectResponse(url=f"{_get_frontend_url()}/auth/callback?token={token}")


# Function: _upsert_oauth_user
def _upsert_oauth_user(user_id: str, username: str, email: str, display_name: str | None, avatar_url: str | None, provider: str) -> dict:
    _ensure_schema()
    with _connect() as conn:
        row = conn.execute(_SQL_SELECT_USER_BY_ID, (user_id,)).fetchone()
        if not row:
            conn.execute(
                """
                INSERT INTO users (id, username, email, password_hash, role, display_name, avatar_url, provider, is_active, created_at)
                VALUES (?, ?, ?, '', 'user', ?, ?, ?, 1, ?)
                """,
                (user_id, username, email or f"{username}@{provider}.local", display_name or username, avatar_url, provider, time.time()),
            )
            conn.execute(_SQL_INSERT_USER_APP, (user_id, "NOVASTRA_ITSM"))
            conn.commit()
        return _row_to_user(conn.execute(_SQL_SELECT_USER_BY_ID, (user_id,)).fetchone())


# Function: _upsert_portal_user
def _upsert_portal_user(username: str, role: str | None, display_name: str | None = None) -> dict:
    """Provision or refresh a Novastra-ITSM-local user for a CENTRAL PORTAL session.

    Looked up by username (not the portal's numeric uid) because the two
    services use incompatible id spaces: the portal's User.id is an integer
    primary key, Novastra-ITSM's users.id is text. Role is re-synced on every SSO
    exchange so a portal admin doesn't stay stuck as a Novastra-ITSM "user" after their
    very first login.
    """
    _ensure_schema()
    with _connect() as conn:
        row = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        if row:
            conn.execute(
                "UPDATE users SET role = ?, is_active = 1 WHERE id = ?",
                (role or row["role"], row["id"]),
            )
            conn.execute(
                _SQL_INSERT_USER_APP,
                (row["id"], "NOVASTRA_ITSM"),
            )
            conn.commit()
            return _row_to_user(conn.execute(_SQL_SELECT_USER_BY_ID, (row["id"],)).fetchone())

        user_id = f"portal_{username}"
        conn.execute(
            """
            INSERT INTO users (id, username, email, password_hash, role, display_name, provider, is_active, created_at)
            VALUES (?, ?, ?, '', ?, ?, 'portal', 1, ?)
            """,
            (user_id, username, f"{username}@portal.local", role or "user", display_name or username, time.time()),
        )
        conn.execute(
            _SQL_INSERT_USER_APP,
            (user_id, "NOVASTRA_ITSM"),
        )
        conn.commit()
        return _row_to_user(conn.execute(_SQL_SELECT_USER_BY_ID, (user_id,)).fetchone())


# Function: _get_frontend_url
def _get_frontend_url() -> str:
    base = cfg.APP_BASE_URL
    if ":8086" in base:
        return base.replace(":8086", ":5177")
    if ":8000" in base:
        return base.replace(":8000", ":5177")
    return base


PORTAL_API_URL = "unused-local"


# Function: portal_sso
@router.post("/portal-sso")
async def portal_sso(req: PortalSSORequest):
    """Exchange a token issued by the CENTRAL portal (AppRationalization) for
    a Novastra-ITSM-local session — this is what lets "Open Novastra-ITSM" land
    a user directly on the workspace with no second login screen.

    Trusts the portal token's HMAC signature + expiry (already verified by
    _decode_token; both services share the same secret) instead of checking
    Novastra-ITSM's own local `sessions` table — a portal-issued token is never written
    there, since that table only ever gets rows from Novastra-ITSM's own login/oauth/
    portal-sso flows, so requiring it would always 401 a real portal token.
    """
    try:
        payload = _decode_token(req.portal_token, _portal_token_secret())
        username = payload.get("username")
        if not username:
            raise HTTPException(status_code=401, detail="Portal token missing username")

        role = payload.get("role")
        apps = payload.get("apps") or []
        if role != "admin" and "NOVASTRA_ITSM" not in apps:
            raise HTTPException(status_code=403, detail="Access denied for Novastra-ITSM")

        user = _upsert_portal_user(username, role, payload.get("display_name"))
        token = _create_token(user["id"], user["username"], user.get("role", "user"), _get_user_apps(user["id"]))
        _store_session(token, user["id"], _decode_token(token)["exp"])
        return {"access_token": token, "token_type": "bearer", "user": _user_public(user)}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=401, detail=f"Portal session validation failed: {exc}") from exc
