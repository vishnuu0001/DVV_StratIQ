# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: AppRationalization — backend/app/services (auth_service.py)
# Date: 2026-01-20
# ---------------------------------------------------------------------------
import base64
import hashlib
import hmac
import json
import os
import re
import secrets
from datetime import datetime, timedelta

from sqlalchemy import func
from werkzeug.security import check_password_hash, generate_password_hash

from app import db
from app.models.auth import (
    AI_REMAN_CORE,
    AI_VEHICLE_LOAN,
    APP_RATIONALIZATION,
    CODE_ANALYSIS,
    DASHBOARD,
    INFRA_SCAN,
    INTUNE_AUTOMATION,
    NOVASTRA_ITSM,
    LAB_ROBOT,
    MICROSITE_DATA_ANALYSIS,
    MODERNIZATION,
    OPPORTUNITY_TRACKER,
    SSDLC_PROCESS_ASSESSMENT,
    SUPPLY_CHAIN_DISRUPTION_MANAGER,
    TOOL_ANALYSIS_QUALIFICATION,
    TRACEFORGE,
    SUPPORTED_APPS,
    User,
    UserAppPermission,
    UserSession,
)


class AuthService:
    DEFAULT_ADMIN_USERNAME = os.getenv("DEFAULT_ADMIN_USERNAME", "admin")
    DEFAULT_ADMIN_PASSWORD = os.getenv("DEFAULT_ADMIN_PASSWORD", "Admin@1234")
    _INSECURE_DEFAULT_AUTH_SECRET = "change-this-auth-token-secret-in-production"

    # Function: _token_secret
    @staticmethod
    def _token_secret():
        secret = (
            os.getenv("AUTH_TOKEN_SECRET")
            or os.getenv("SECRET_KEY")
            or AuthService._INSECURE_DEFAULT_AUTH_SECRET
        )

        if secret == AuthService._INSECURE_DEFAULT_AUTH_SECRET:
            allow_insecure = os.getenv("ALLOW_INSECURE_AUTH_SECRET", "false").lower() in {"1", "true", "yes"}
            if not allow_insecure:
                raise ValueError(
                    "AUTH_TOKEN_SECRET/SECRET_KEY is insecure. "
                    "Set a strong shared secret, or explicitly set ALLOW_INSECURE_AUTH_SECRET=true for non-production use."
                )

        return secret

    # Function: _token_ttl_seconds
    @staticmethod
    def _token_ttl_seconds():
        raw = os.getenv("AUTH_TOKEN_TTL_SECONDS", "28800")
        try:
            ttl = int(raw)
        except ValueError:
            ttl = 28800
        return max(ttl, 900)

    # Function: _b64url_encode
    @staticmethod
    def _b64url_encode(raw):
        return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")

    # Function: _b64url_decode
    @staticmethod
    def _b64url_decode(text):
        padding = "=" * ((4 - len(text) % 4) % 4)
        return base64.urlsafe_b64decode((text + padding).encode("ascii"))

    # Function: _sign
    @classmethod
    def _sign(cls, message):
        mac = hmac.new(cls._token_secret().encode("utf-8"), message.encode("utf-8"), hashlib.sha256)
        return cls._b64url_encode(mac.digest())

    # Function: _create_signed_token
    @classmethod
    def _create_signed_token(cls, payload):
        payload_json = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        payload_encoded = cls._b64url_encode(payload_json)
        signature = cls._sign(payload_encoded)
        return f"v1.{payload_encoded}.{signature}"

    # Function: _decode_signed_token
    @classmethod
    def _decode_signed_token(cls, token):
        if not token or not isinstance(token, str):
            raise ValueError("Missing token")

        parts = token.split(".")
        if len(parts) != 3 or parts[0] != "v1":
            raise ValueError("Malformed token")

        payload_encoded = parts[1]
        expected_signature = cls._sign(payload_encoded)
        if not hmac.compare_digest(expected_signature, parts[2]):
            raise ValueError("Invalid token signature")

        payload = json.loads(cls._b64url_decode(payload_encoded).decode("utf-8"))
        exp = int(payload.get("exp", 0))
        if exp <= int(datetime.utcnow().timestamp()):
            raise ValueError("Token expired")

        return payload

    # Function: extract_bearer_token
    @classmethod
    def extract_bearer_token(cls, authorization_header):
        if not authorization_header:
            return None
        parts = authorization_header.split(" ", 1)
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return None
        return parts[1].strip()

    # Function: get_user_apps
    @classmethod
    def get_user_apps(cls, user):
        app_set = {perm.app_key for perm in user.permissions if perm.app_key in SUPPORTED_APPS}
        if user.role == "admin":
            app_set |= SUPPORTED_APPS
        return sorted(app_set)

    # Function: serialize_user
    @classmethod
    def serialize_user(cls, user):
        apps = cls.get_user_apps(user)
        return {
            "id": user.id,
            "username": user.username,
            "role": user.role,
            "apps": apps,
            "oauth_provider": user.oauth_provider,
            "is_active": user.is_active,
            "can_manage_users": user.role == "admin",
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None,
        }

    # Function: validate_password_strength
    @staticmethod
    def validate_password_strength(password):
        if not password or len(password) < 8:
            return False, "Password must be at least 8 characters long"
        if not re.search(r"[A-Z]", password):
            return False, "Password must include at least one uppercase letter"
        if not re.search(r"[a-z]", password):
            return False, "Password must include at least one lowercase letter"
        if not re.search(r"[0-9]", password):
            return False, "Password must include at least one digit"
        if not re.search(r"[^A-Za-z0-9]", password):
            return False, "Password must include at least one special character"
        return True, None

    # Function: hash_password
    @staticmethod
    def hash_password(password):
        return generate_password_hash(password)

    # Function: set_user_permissions
    @classmethod
    def set_user_permissions(cls, user, apps):
        valid_apps = sorted({a for a in (apps or []) if a in SUPPORTED_APPS})
        if user.role == "admin":
            valid_apps = sorted(SUPPORTED_APPS)

        UserAppPermission.query.filter_by(user_id=user.id).delete()
        for app_key in valid_apps:
            db.session.add(UserAppPermission(user_id=user.id, app_key=app_key))

    # Function: ensure_default_admin
    @classmethod
    def ensure_default_admin(cls):
        admin = User.query.filter(func.lower(User.username) == cls.DEFAULT_ADMIN_USERNAME.lower()).first()
        if not admin:
            admin = User(
                username=cls.DEFAULT_ADMIN_USERNAME,
                password_hash=cls.hash_password(cls.DEFAULT_ADMIN_PASSWORD),
                role="admin",
                is_active=True,
            )
            db.session.add(admin)
            db.session.flush()
        elif not admin.password_hash:
            admin.password_hash = cls.hash_password(cls.DEFAULT_ADMIN_PASSWORD)

        admin.role = "admin"
        admin.is_active = True
        cls.set_user_permissions(admin, sorted(SUPPORTED_APPS))
        db.session.commit()

    # Function: create_user
    @classmethod
    def create_user(cls, username, password, role="user", apps=None):
        if not username:
            raise ValueError("Username is required")

        username = username.strip()
        existing = User.query.filter(func.lower(User.username) == username.lower()).first()
        if existing:
            raise ValueError("Username already exists")

        if role not in {"admin", "user"}:
            raise ValueError("Role must be either 'admin' or 'user'")

        valid_password, error = cls.validate_password_strength(password)
        if not valid_password:
            raise ValueError(error)

        user = User(
            username=username,
            password_hash=cls.hash_password(password),
            role=role,
            is_active=True,
        )
        db.session.add(user)
        db.session.flush()

        cls.set_user_permissions(user, apps or [APP_RATIONALIZATION])
        db.session.commit()
        return user

    # Function: update_user
    @classmethod
    def update_user(cls, user, role=None, is_active=None, apps=None, password=None):
        if role is not None:
            if role not in {"admin", "user"}:
                raise ValueError("Role must be either 'admin' or 'user'")
            user.role = role

        if is_active is not None:
            user.is_active = bool(is_active)

        if password:
            valid_password, error = cls.validate_password_strength(password)
            if not valid_password:
                raise ValueError(error)
            user.password_hash = cls.hash_password(password)

        if apps is not None:
            cls.set_user_permissions(user, apps)

        db.session.commit()
        return user

    # Function: delete_user
    @classmethod
    def delete_user(cls, user_to_delete, acting_user):
        if not user_to_delete:
            raise ValueError("User not found")

        if acting_user and user_to_delete.id == acting_user.id:
            raise ValueError("You cannot delete your own account")

        if user_to_delete.role == "admin":
            active_admins = User.query.filter_by(role="admin", is_active=True).count()
            if user_to_delete.is_active and active_admins <= 1:
                raise ValueError("Cannot delete the last active admin account")

        db.session.delete(user_to_delete)
        db.session.commit()

    # Function: _build_unique_username
    @classmethod
    def _build_unique_username(cls, preferred, provider):
        base = (preferred or "").strip()
        if not base:
            base = f"{provider}_user"

        candidate = re.sub(r"[^A-Za-z0-9._-]", "_", base)
        if not candidate:
            candidate = f"{provider}_user"

        suffix = 1
        unique = candidate
        while User.query.filter(func.lower(User.username) == unique.lower()).first():
            suffix += 1
            unique = f"{candidate}_{suffix}"
        return unique

    # Function: upsert_oauth_user
    @classmethod
    def upsert_oauth_user(cls, provider, subject, email=None, preferred_username=None):
        user = User.query.filter_by(oauth_provider=provider, oauth_subject=subject).first()
        if user:
            user.is_active = True
            db.session.commit()
            return user

        username_seed = preferred_username or email or f"{provider}_{subject}"
        username = cls._build_unique_username(username_seed, provider)

        user = User(
            username=username,
            password_hash=None,
            role="user",
            oauth_provider=provider,
            oauth_subject=subject,
            is_active=True,
        )
        db.session.add(user)
        db.session.flush()
        cls.set_user_permissions(user, [APP_RATIONALIZATION])
        db.session.commit()
        return user

    # Function: create_session
    @classmethod
    def create_session(cls, user, ip_address=None, user_agent=None):
        expires_at = datetime.utcnow() + timedelta(seconds=cls._token_ttl_seconds())
        session_id = secrets.token_urlsafe(48)

        session_row = UserSession(
            session_id=session_id,
            user_id=user.id,
            expires_at=expires_at,
            ip_address=ip_address,
            user_agent=(user_agent or "")[:512],
        )
        db.session.add(session_row)
        db.session.flush()

        token_payload = {
            "typ": "access",
            "uid": user.id,
            "sid": session_id,
            "username": user.username,
            "role": user.role,
            "apps": cls.get_user_apps(user),
            "iat": int(datetime.utcnow().timestamp()),
            "exp": int(expires_at.timestamp()),
        }
        token = cls._create_signed_token(token_payload)
        return session_row, token

    # Function: authenticate_local_user
    @classmethod
    def authenticate_local_user(cls, username, password, ip_address=None, user_agent=None):
        if not username or not password:
            return None, "Username and password are required"

        user = User.query.filter(func.lower(User.username) == username.strip().lower()).first()
        if not user or not user.password_hash:
            return None, "Invalid username or password"
        if not user.is_active:
            return None, "Your account is disabled. Contact administrator"
        if not check_password_hash(user.password_hash, password):
            return None, "Invalid username or password"

        session_row, token = cls.create_session(user, ip_address=ip_address, user_agent=user_agent)
        db.session.commit()

        return {
            "token": token,
            "expires_at": session_row.expires_at.isoformat(),
            "user": cls.serialize_user(user),
        }, None

    # Function: login_oauth_user
    @classmethod
    def login_oauth_user(cls, user, ip_address=None, user_agent=None):
        if not user.is_active:
            return None, "Your account is disabled. Contact administrator"

        session_row, token = cls.create_session(user, ip_address=ip_address, user_agent=user_agent)
        db.session.commit()

        return {
            "token": token,
            "expires_at": session_row.expires_at.isoformat(),
            "user": cls.serialize_user(user),
        }, None

    # Function: revoke_session
    @classmethod
    def revoke_session(cls, session_id):
        if not session_id:
            return
        session_row = UserSession.query.filter_by(session_id=session_id).first()
        if session_row and session_row.revoked_at is None:
            session_row.revoked_at = datetime.utcnow()
            db.session.commit()

    # Function: validate_access_token
    @classmethod
    def validate_access_token(cls, token, required_app=None, check_session=True):
        try:
            payload = cls._decode_signed_token(token)
        except ValueError as exc:
            return {"ok": False, "status": 401, "error": str(exc)}

        if payload.get("typ") != "access":
            return {"ok": False, "status": 401, "error": "Invalid token type"}

        user = User.query.get(payload.get("uid"))
        if not user or not user.is_active:
            return {"ok": False, "status": 401, "error": "User not found or disabled"}

        if check_session:
            sid = payload.get("sid")
            session_row = UserSession.query.filter_by(session_id=sid, user_id=user.id).first()
            if not session_row or not session_row.is_active:
                return {"ok": False, "status": 401, "error": "Session is no longer active"}

        apps = [app for app in payload.get("apps", []) if app in SUPPORTED_APPS]
        if user.role == "admin":
            apps = sorted(set(apps) | SUPPORTED_APPS)

        if required_app and user.role != "admin" and required_app not in apps:
            return {
                "ok": False,
                "status": 403,
                "error": f"Access denied for application '{required_app}'",
            }

        return {
            "ok": True,
            "status": 200,
            "user": user,
            "apps": apps,
            "payload": payload,
        }

    # Function: create_state_token
    @classmethod
    def create_state_token(cls, provider):
        payload = {
            "typ": "oauth_state",
            "provider": provider,
            "nonce": secrets.token_urlsafe(12),
            "iat": int(datetime.utcnow().timestamp()),
            "exp": int((datetime.utcnow() + timedelta(minutes=10)).timestamp()),
        }
        return cls._create_signed_token(payload)

    # Function: verify_state_token
    @classmethod
    def verify_state_token(cls, token, provider):
        payload = cls._decode_signed_token(token)
        if payload.get("typ") != "oauth_state":
            raise ValueError("Invalid state token type")
        if payload.get("provider") != provider:
            raise ValueError("OAuth state provider mismatch")
        return payload


AUTH_APP_NAME_MAP = {
    "app-rationalization": APP_RATIONALIZATION,
    "code-analysis": CODE_ANALYSIS,
    "infra-scan": INFRA_SCAN,
    "infra-rationalization": INFRA_SCAN,
    "novastra-itsm": NOVASTRA_ITSM,
    "dashboard": DASHBOARD,
    "digital-operations-cockpit": DASHBOARD,
    "intune-automation": INTUNE_AUTOMATION,
    "intuneautomation": INTUNE_AUTOMATION,
    "tool-analysis-qualification": TOOL_ANALYSIS_QUALIFICATION,
    "tools-analysis-qualification": TOOL_ANALYSIS_QUALIFICATION,
    "tool-analysis": TOOL_ANALYSIS_QUALIFICATION,
    "ssdlc-process-assessment": SSDLC_PROCESS_ASSESSMENT,
    "ssdlc-assessment": SSDLC_PROCESS_ASSESSMENT,
    "ssdlc": SSDLC_PROCESS_ASSESSMENT,
    "microsite-data-analysis": MICROSITE_DATA_ANALYSIS,
    "data-analysis-studio": MICROSITE_DATA_ANALYSIS,
    "mda": MICROSITE_DATA_ANALYSIS,
    "ai-reman-core": AI_REMAN_CORE,
    "reman": AI_REMAN_CORE,
    "ai-vehicle-loan": AI_VEHICLE_LOAN,
    "vehicle-loan": AI_VEHICLE_LOAN,
    "modernization": MODERNIZATION,
    "modernization-studio": MODERNIZATION,
    "lab-robot": LAB_ROBOT,
    "opportunity-tracker": OPPORTUNITY_TRACKER,
    "ot": OPPORTUNITY_TRACKER,
    "supply-chain-disruption-manager": SUPPLY_CHAIN_DISRUPTION_MANAGER,
    "supply-chain-disruption": SUPPLY_CHAIN_DISRUPTION_MANAGER,
    "scm": SUPPLY_CHAIN_DISRUPTION_MANAGER,
    "traceforge": TRACEFORGE,
    "tf": TRACEFORGE,
}
