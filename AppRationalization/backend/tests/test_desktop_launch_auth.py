import os
import unittest
from urllib.parse import parse_qs, urlparse

os.environ.setdefault("ALLOW_INSECURE_AUTH_SECRET", "true")

from app import create_app, db
from app.models.auth import APP_RATIONALIZATION, LAB_ROBOT
from app.services.auth_service import AuthService


class DesktopLaunchAuthTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.context = self.app.app_context()
        self.context.push()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.context.pop()

    def create_lab_user_and_session(self):
        user = AuthService.create_user(
            username="desktop-user",
            password="Desktop@1234",
            apps=[APP_RATIONALIZATION, LAB_ROBOT],
        )
        session, token = AuthService.create_session(user)
        db.session.commit()
        return user, session, token

    def test_ticket_is_single_use_and_keeps_parent_session(self):
        user, session, _ = self.create_lab_user_and_session()
        raw_ticket, _ = AuthService.create_desktop_launch_ticket(user, session.session_id, LAB_ROBOT)

        handoff, error = AuthService.exchange_desktop_launch_ticket(raw_ticket, LAB_ROBOT)
        self.assertIsNone(error)
        payload = AuthService._decode_signed_token(handoff["token"])
        self.assertEqual(session.session_id, payload["sid"])

        repeated, repeated_error = AuthService.exchange_desktop_launch_ticket(raw_ticket, LAB_ROBOT)
        self.assertIsNone(repeated)
        self.assertIn("already used", repeated_error)

    def test_revoked_parent_session_rejects_ticket(self):
        user, session, _ = self.create_lab_user_and_session()
        raw_ticket, _ = AuthService.create_desktop_launch_ticket(user, session.session_id, LAB_ROBOT)
        AuthService.revoke_session(session.session_id)

        handoff, error = AuthService.exchange_desktop_launch_ticket(raw_ticket, LAB_ROBOT)
        self.assertIsNone(handoff)
        self.assertEqual("Portal session is no longer active", error)

    def test_permission_changes_are_authoritative_for_existing_tokens(self):
        user, _, token = self.create_lab_user_and_session()
        AuthService.set_user_permissions(user, [APP_RATIONALIZATION])
        db.session.commit()

        result = AuthService.validate_access_token(token, required_app=LAB_ROBOT, check_session=True)
        self.assertFalse(result["ok"])
        self.assertEqual(403, result["status"])

    def test_authenticated_route_launches_and_public_exchange_redeems(self):
        _, _, token = self.create_lab_user_and_session()
        client = self.app.test_client()

        launch_response = client.post(
            "/api/auth/desktop-launch",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(201, launch_response.status_code)
        launch_uri = launch_response.get_json()["launch_uri"]
        self.assertEqual("labrobot", urlparse(launch_uri).scheme)
        ticket = parse_qs(urlparse(launch_uri).query)["ticket"][0]

        exchange_response = client.post(
            "/api/auth/desktop/exchange",
            json={"ticket": ticket},
        )
        self.assertEqual(200, exchange_response.status_code)
        self.assertTrue(exchange_response.get_json()["token"].startswith("v1."))


if __name__ == "__main__":
    unittest.main()
