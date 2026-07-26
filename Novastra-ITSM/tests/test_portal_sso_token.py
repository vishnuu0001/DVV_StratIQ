# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Novastra-ITSM — tests (test_portal_sso_token.py)
# Date: 2026-03-27
# ---------------------------------------------------------------------------
import unittest

import backend.config as cfg
from backend.api import auth


class PortalSsoTokenTests(unittest.TestCase):
    # Function: test_portal_token_uses_portal_secret_not_local_session_secret
    def test_portal_token_uses_portal_secret_not_local_session_secret(self):
        original_local = cfg.JWT_SECRET
        original_portal = cfg.PORTAL_AUTH_TOKEN_SECRET
        try:
            cfg.JWT_SECRET = "portal-test-secret"
            portal_token = auth._create_token(
                "portal-user",
                "portal-user",
                "user",
                ["NOVASTRA_ITSM"],
            )

            cfg.JWT_SECRET = "novastra-local-test-secret"
            cfg.PORTAL_AUTH_TOKEN_SECRET = "portal-test-secret"

            payload = auth._decode_token(
                portal_token,
                auth._portal_token_secret(),
            )
            self.assertEqual(payload["username"], "portal-user")
            with self.assertRaisesRegex(ValueError, "Invalid token signature"):
                auth._decode_token(portal_token)
        finally:
            cfg.JWT_SECRET = original_local
            cfg.PORTAL_AUTH_TOKEN_SECRET = original_portal


if __name__ == "__main__":
    unittest.main()
