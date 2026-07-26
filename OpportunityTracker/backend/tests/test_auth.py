# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: OpportunityTracker — backend/tests (test_auth.py)
# Date: 2026-05-20
# ---------------------------------------------------------------------------
import base64
import hashlib
import hmac
import json
import time
import unittest
from unittest.mock import patch

from fastapi import HTTPException

import auth


# Function: _portal_token
def _portal_token(payload: dict, secret: str) -> str:
    body = base64.urlsafe_b64encode(
        json.dumps(payload, separators=(",", ":")).encode()
    ).decode().rstrip("=")
    signature = base64.urlsafe_b64encode(
        hmac.new(secret.encode(), body.encode(), hashlib.sha256).digest()
    ).decode().rstrip("=")
    return f"v1.{body}.{signature}"


class OpportunityTrackerAuthTests(unittest.TestCase):
    # Function: test_existing_local_login_token_remains_valid
    def test_existing_local_login_token_remains_valid(self):
        token = auth.create_token("otadmin")
        self.assertEqual(auth._verify(token)["sub"], "otadmin")

    # Function: test_portal_admin_token_is_accepted
    def test_portal_admin_token_is_accepted(self):
        secret = "shared-auth-test-secret-with-sufficient-length"
        token = _portal_token(
            {
                "username": "portal-admin",
                "role": "admin",
                "apps": [],
                "typ": "access",
                "exp": int(time.time()) + 60,
            },
            secret,
        )
        with patch.object(auth, "PORTAL_AUTH_TOKEN_SECRET", secret):
            self.assertEqual(auth._verify(token)["username"], "portal-admin")

    # Function: test_portal_user_requires_opportunity_tracker_permission
    def test_portal_user_requires_opportunity_tracker_permission(self):
        secret = "shared-auth-test-secret-with-sufficient-length"
        base_payload = {
            "username": "portal-user",
            "role": "user",
            "typ": "access",
            "exp": int(time.time()) + 60,
        }
        allowed = _portal_token(
            {**base_payload, "apps": [auth.OPPORTUNITY_TRACKER_APP]},
            secret,
        )
        denied = _portal_token(
            {**base_payload, "apps": ["TRACEFORGE"]},
            secret,
        )
        with patch.object(auth, "PORTAL_AUTH_TOKEN_SECRET", secret):
            self.assertEqual(auth._verify(allowed)["username"], "portal-user")
            with self.assertRaises(HTTPException) as raised:
                auth._verify(denied)
            self.assertEqual(raised.exception.status_code, 403)

    # Function: test_expired_or_badly_signed_portal_token_is_rejected
    def test_expired_or_badly_signed_portal_token_is_rejected(self):
        secret = "shared-auth-test-secret-with-sufficient-length"
        expired = _portal_token(
            {
                "username": "portal-user",
                "role": "admin",
                "typ": "access",
                "exp": int(time.time()) - 1,
            },
            secret,
        )
        with patch.object(auth, "PORTAL_AUTH_TOKEN_SECRET", secret):
            with self.assertRaises(HTTPException) as expired_error:
                auth._verify(expired)
            self.assertEqual(expired_error.exception.status_code, 401)

            with self.assertRaises(HTTPException) as signature_error:
                auth._verify(f"{expired.rsplit('.', 1)[0]}.invalid")
            self.assertEqual(signature_error.exception.status_code, 401)


if __name__ == "__main__":
    unittest.main()
