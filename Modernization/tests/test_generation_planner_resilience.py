import unittest
from unittest.mock import patch

from services.modernizer.prompt_pipeline import (
    _parse_file_list_lines,
    _pf_run_plan_generation,
)


class GenerationPlannerResilienceTests(unittest.TestCase):
    def test_accepts_json_objects_and_windows_paths(self):
        response = """```json
        {"files": [
          {"path": "backend\\\\Program.cs"},
          {"file_path": "frontend/src/app/app.component.ts"},
          ".github/workflows/ci.yml"
        ]}
        ```"""
        self.assertEqual(
            [
                "backend/Program.cs",
                "frontend/src/app/app.component.ts",
                ".github/workflows/ci.yml",
            ],
            _parse_file_list_lines(response),
        )

    def test_recovers_complete_paths_from_truncated_json(self):
        response = (
            '{"files":[{"path":"backend/Program.cs"},'
            '{"path":"backend/Controllers/TransfersController.cs"},'
        )
        self.assertEqual(
            ["backend/Program.cs", "backend/Controllers/TransfersController.cs"],
            _parse_file_list_lines(response),
        )

    def test_rejects_unsafe_and_non_file_entries(self):
        response = """
        C:\\Windows\\system.ini
        /etc/passwd
        ../outside.py
        https://example.invalid/payload.py
        backend/Controllers
        backend/Program.cs
        """
        self.assertEqual(["backend/Program.cs"], _parse_file_list_lines(response))

    @patch("services.llm.generate", return_value="")
    def test_empty_llm_plan_uses_deterministic_baseline(self, _generate):
        progress_events = []
        result = _pf_run_plan_generation(
            "prompt", "", [], 100, 10, "model", "system",
            lambda phase, pct, message: progress_events.append((phase, pct, message)),
            ["backend/Program.cs", "backend/appsettings.json"],
        )
        self.assertEqual(
            ["backend/Program.cs", "backend/appsettings.json"],
            result[0],
        )
        self.assertTrue(any("deterministic baseline" in event[2] for event in progress_events))


if __name__ == "__main__":
    unittest.main()
