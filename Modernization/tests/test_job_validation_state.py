# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Modernization — tests (test_job_validation_state.py)
# Date: 2025-10-22
# ---------------------------------------------------------------------------
import unittest
from types import SimpleNamespace

from fastapi import HTTPException

from api.server import app, _failed_strict_validation, _require_admin, _single_file_failed_validation


class SingleFileValidationStateTests(unittest.TestCase):
    # Function: test_unresolved_cobol_template_is_rejected_before_generation
    # Function: test_passed_single_file_is_not_failed
    def test_passed_single_file_is_not_failed(self):
        self.assertFalse(_single_file_failed_validation(
            {"__single_file__": "print('ok')"}, {"failed": 0},
        ))

    # Function: test_failed_single_file_is_failed
    def test_failed_single_file_is_failed(self):
        self.assertTrue(_single_file_failed_validation(
            {"__single_file__": "invalid"}, {"failed": 1},
        ))

    # Function: test_project_validation_does_not_use_single_file_state
    def test_project_validation_does_not_use_single_file_state(self):
        self.assertFalse(_single_file_failed_validation(
            {"src/app.py": "invalid"}, {"failed": 1},
        ))

    # Function: test_project_build_failure_is_terminal_validation_failure
    def test_project_build_failure_is_terminal_validation_failure(self):
        validation = {
            "failed": 0, "strict_checked": 2,
            "build": {"passed": False, "checker": "c-build"},
        }
        self.assertTrue(_failed_strict_validation(validation, True))

    # Function: test_project_requires_whole_output_validation
    def test_project_requires_whole_output_validation(self):
        self.assertTrue(_failed_strict_validation(
            {"failed": 0, "strict_checked": 2, "build": None}, True,
        ))

    # Function: test_explicit_production_readiness_failure_is_terminal
    def test_explicit_production_readiness_failure_is_terminal(self):
        self.assertTrue(_failed_strict_validation(
            {
                "failed": 0,
                "strict_checked": 3,
                "production_ready": False,
                "build": {"passed": True, "checker": "maven"},
            },
            True,
        ))

    # Function: test_project_deletion_requires_server_side_admin_role
    def test_project_deletion_requires_server_side_admin_role(self):
        non_admin_request = SimpleNamespace(
            state=SimpleNamespace(auth={"sub": "user@example.test", "role": "user"}),
        )
        with self.assertRaises(HTTPException) as denied:
            _require_admin(non_admin_request, "delete governed projects")
        self.assertEqual(403, denied.exception.status_code)
        self.assertIn("delete governed projects", denied.exception.detail)

        admin_request = SimpleNamespace(
            state=SimpleNamespace(auth={"sub": "admin@example.test", "role": "admin"}),
        )
        self.assertIsNone(_require_admin(admin_request, "delete governed projects"))

    # Function: test_proxy_compatible_delete_route_is_registered
    def test_proxy_compatible_delete_route_is_registered(self):
        methods = {
            method
            for route in app.routes
            if getattr(route, "path", None) == "/api/projects/{project_id}/delete"
            for method in (getattr(route, "methods", None) or set())
        }
        self.assertEqual({"POST"}, methods)


if __name__ == "__main__":
    unittest.main()
