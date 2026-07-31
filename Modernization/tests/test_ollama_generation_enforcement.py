# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Modernization — tests (test_ollama_generation_enforcement.py)
# Date: 2026-02-01
# ---------------------------------------------------------------------------
import json
import unittest
from unittest.mock import patch

from services.modernizer.domain_generators.dispatch import (
    _ollama_generate_all_sources,
    _llm_gen_domain,
)
from services.validators import ValidationResult


class OllamaGenerationEnforcementTests(unittest.TestCase):
    # Function: test_every_executable_source_is_reauthored_by_validated_ollama_call
    @patch("services.modernizer.validation_orchestration._generate_validated")
    def test_every_executable_source_is_reauthored_by_validated_ollama_call(self, generated):
        generated.side_effect = lambda prompt, **kwargs: (
            f"OLLAMA::{kwargs['rel_path']}",
            ValidationResult(kwargs["rel_path"], kwargs["language"], "compiler", True, []),
            1,
        )
        files = {
            "Demo/src/App.kt": "deterministic Kotlin contract",
            "Demo/schema.sql": "deterministic SQL contract",
            "Demo/build.gradle.kts": "deterministic build metadata",
            "Demo/README.md": "documentation",
        }

        _ollama_generate_all_sources(
            files,
            {
                "name": "Kotlin Spring",
                "language": "kotlin",
                "db_target": "postgres",
                "db_tech": "PostgreSQL 16",
            },
            "Orders", "qwen-test", "system", None, None,
        )

        self.assertEqual("OLLAMA::Demo/src/App.kt", files["Demo/src/App.kt"])
        self.assertEqual("OLLAMA::Demo/schema.sql", files["Demo/schema.sql"])
        self.assertEqual("OLLAMA::Demo/build.gradle.kts", files["Demo/build.gradle.kts"])
        self.assertEqual("documentation", files["Demo/README.md"])
        self.assertEqual(3, generated.call_count)
        self.assertTrue(all(call.kwargs["dialect"] == "postgres" for call in generated.call_args_list))
        provenance = json.loads(files["Demo/.strat-aqorynth/ollama-orders-provenance.json"])
        self.assertEqual("ollama", provenance["generator"])
        self.assertEqual("qwen-test", provenance["model"])
        self.assertEqual(3, len(provenance["source_files"]))

    # Function: test_final_generation_pass_propagates_project_contract
    @patch("services.modernizer.validation_orchestration._generate_validated")
    def test_final_generation_pass_propagates_project_contract(self, generated):
        generated.return_value = (
            "class App {}",
            ValidationResult("Demo/App.java", "java", "compiler", True, []),
            1,
        )
        files = {"Demo/App.java": "controller file contract"}
        _ollama_generate_all_sources(
            files,
            {"name": "Spring Boot 3", "language": "java"},
            "Orders", "qwen-test", "system", None, None,
            user_request="Publish OrderCreated to Kafka",
            contracts="POST /api/orders returns OrderResponse",
            namespace_map="OrderResponse -> demo.api.OrderResponse",
            required_elements="OAuth2 JWT and Flyway",
            file_manifest="Demo/App.java\nDemo/pom.xml",
        )
        prompt = generated.call_args.args[0]
        self.assertIn("ORIGINAL USER REQUIREMENTS", prompt)
        self.assertIn("Publish OrderCreated to Kafka", prompt)
        self.assertIn("PROJECT CONTRACTS", prompt)
        self.assertIn("demo.api.OrderResponse", prompt)
        self.assertIn("OAuth2 JWT and Flyway", prompt)
        self.assertIn("Demo/pom.xml", prompt)
        self.assertIn("Implement only the responsibility assigned", prompt)
        self.assertIn("bootstrap classes must not contain controller", prompt)

    @patch("services.modernizer.validation_orchestration._generate_validated")
    def test_java_fullstack_sources_use_their_actual_frontend_language(self, generated):
        generated.side_effect = lambda prompt, **kwargs: (
            "generated",
            ValidationResult(kwargs["rel_path"], kwargs["language"], "compiler", True, []),
            1,
        )
        files = {
            "Demo/backend/src/main/java/com/app/App.java": "class App {}",
            "Demo/frontend/store/authStore.ts": "export const value = true;",
            "Demo/frontend/src/App.tsx": "export default function App() { return null; }",
        }

        _ollama_generate_all_sources(
            files, {"name": "React + Spring Boot", "language": "java"},
            "Demo", "qwen-test", "system", None, None,
        )

        languages = {
            call.kwargs["rel_path"]: call.kwargs["language"]
            for call in generated.call_args_list
        }
        self.assertEqual("java", languages["Demo/backend/src/main/java/com/app/App.java"])
        self.assertEqual("typescript", languages["Demo/frontend/store/authStore.ts"])
        self.assertEqual("typescript", languages["Demo/frontend/src/App.tsx"])

    @patch("services.modernizer.validation_orchestration._generate_validated")
    def test_sql_server_dialect_is_authoritative_during_ollama_generation(self, generated):
        generated.return_value = (
            "SELECT SYSUTCDATETIME();",
            ValidationResult("Demo/schema.sql", "sql", "compiler", True, []),
            1,
        )
        files = {"Demo/schema.sql": "CREATE TABLE Accounts (Id INT);"}

        _ollama_generate_all_sources(
            files,
            {
                "name": ".NET + SQL Server",
                "language": "csharp",
                "db_target": "mssql",
                "db_tech": "Microsoft SQL Server 2022 + EF Core 8",
            },
            "Payments", "qwen-test", "system", None, None,
        )

        self.assertEqual("tsql", generated.call_args.kwargs["dialect"])
        self.assertIn("AUTHORITATIVE SQL DIALECT: tsql", generated.call_args.args[0])

    def test_sql_generation_fails_closed_without_database_dialect(self):
        with self.assertRaisesRegex(ValueError, "authoritative relational db_target"):
            _ollama_generate_all_sources(
                {"Demo/schema.sql": "CREATE TABLE Accounts (Id INT);"},
                {"name": "Unconfigured", "language": "csharp"},
                "Payments", "qwen-test", "system", None, None,
            )

    # Function: test_domain_generation_fails_closed_when_ollama_is_unavailable
    @patch("services.llm.check_status", return_value={"available": False})
    def test_domain_generation_fails_closed_when_ollama_is_unavailable(self, _status):
        with self.assertRaisesRegex(RuntimeError, "Ollama code generation is required"):
            _llm_gen_domain(
                "Orders",
                {
                    "name": "Kotlin Spring",
                    "language": "kotlin",
                    "backend_tech": "Spring Boot",
                    "frontend_tech": "REST API",
                    "db_tech": "PostgreSQL",
                    "db_target": "postgres",
                },
                {},
                "Demo",
                [],
            )


if __name__ == "__main__":
    unittest.main()
