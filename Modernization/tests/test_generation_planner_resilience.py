import unittest
from unittest.mock import patch

from services.modernizer.prompt_pipeline import (
    _parse_file_list_lines,
    _pf_run_plan_generation,
    _pf_validate_final_output,
)
from services.modernizer.scaffolds.money_transfer_demo import (
    _money_transfer_frontend_files,
    _money_transfer_schema_sql,
)
from services.modernizer.target_config import resolve_sql_dialect_hint
from services.validators import validate_file


class GenerationPlannerResilienceTests(unittest.TestCase):
    def test_money_transfer_schema_uses_detectable_sql_server_dialect(self):
        result = validate_file("database/schema.sql", _money_transfer_schema_sql(), "sql")
        self.assertTrue(result.passed, result.diagnostics)

    def test_machine_readable_database_target_wins_over_ambiguous_description(self):
        self.assertEqual(
            "mssql",
            resolve_sql_dialect_hint({
                "db_target": "mssql",
                "db_tech": "PostgreSQL / MS SQL (via API)",
            }),
        )

    def test_final_project_validation_forbids_implicit_ansi_sql(self):
        counts, failures = _pf_validate_final_output(
            {"Demo/database/schema.sql": "CREATE TABLE Accounts (Id INTEGER);"},
            "csharp",
            "",
            lambda *_args: None,
        )
        self.assertEqual(1, counts["failed"])
        self.assertEqual("UNCONFIGURED", failures[0]["dialect"])
        self.assertIn("generic ANSI fallback is prohibited", failures[0]["diagnostics"][0])

    def test_final_project_validation_records_normalized_sql_server_dialect(self):
        counts, failures = _pf_validate_final_output(
            {"Demo/database/schema.sql": "IF NOT EXISTS BROKEN TSQL"},
            "csharp",
            "mssql",
            lambda *_args: None,
        )
        self.assertEqual(1, counts["failed"])
        self.assertEqual("tsql", failures[0]["dialect"])
        self.assertIn("tsql parse error", failures[0]["diagnostics"][0].casefold())

    def test_azure_angular_pack_pins_ngmodule_entrypoint(self):
        files = _money_transfer_frontend_files(True)
        main = files["frontend/src/main.ts"]
        self.assertIn("platformBrowserDynamic", main)
        self.assertIn("./app/app.module", main)
        self.assertNotIn("route-config", main)

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
