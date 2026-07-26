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
            {"name": "Kotlin Spring", "language": "kotlin"},
            "Orders", "qwen-test", "system", None, None,
        )

        self.assertEqual("OLLAMA::Demo/src/App.kt", files["Demo/src/App.kt"])
        self.assertEqual("OLLAMA::Demo/schema.sql", files["Demo/schema.sql"])
        self.assertEqual("OLLAMA::Demo/build.gradle.kts", files["Demo/build.gradle.kts"])
        self.assertEqual("documentation", files["Demo/README.md"])
        self.assertEqual(3, generated.call_count)
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
