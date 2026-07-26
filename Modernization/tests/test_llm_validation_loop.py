# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Modernization — tests (test_llm_validation_loop.py)
# Date: 2026-01-17
# ---------------------------------------------------------------------------
import unittest
from unittest.mock import patch

from services.modernizer import (
    _detect_domain_requirements,
    generate_from_prompt,
    _generate_validated,
    _unresolved_requirement_placeholders,
)
from services.modernizer import _single_file_extension
from services.validators import ValidationResult


class LlmValidationLoopTests(unittest.TestCase):
    # Function: test_requirement_placeholders_are_distinguished_from_html
    def test_requirement_placeholders_are_distinguished_from_html(self):
        prompt = "PROGRAM-ID <PROGRAM-ID>; render <div class=\"app\">ok</div>; input <file name and LRECL>"
        self.assertEqual(
            ["<PROGRAM-ID>", "<file name and LRECL>"],
            _unresolved_requirement_placeholders(prompt),
        )

    # Function: test_generic_ledger_name_does_not_enable_money_transfer_pack
    def test_generic_ledger_name_does_not_enable_money_transfer_pack(self):
        self.assertEqual(
            "",
            _detect_domain_requirements(
                "Build HealthLedger with entries containing descriptions and amount_cents"
            ),
        )
        self.assertIn(
            "ATOMIC",
            _detect_domain_requirements(
                "Build a bank account money transfer API that debits and credits balances"
            ),
        )

    # Function: test_file_only_language_cannot_claim_project_readiness
    def test_rust_has_a_dependency_aware_project_route(self):
        from services.build_runner import PRODUCTION_PROJECT_BUILD_LANGUAGES
        from services.modernizer.scaffolds.polyglot import generate_polyglot_project

        self.assertIn("rust", PRODUCTION_PROJECT_BUILD_LANGUAGES)
        files = generate_polyglot_project("rust", "Demo", "Orders", {})
        self.assertTrue(any(path.endswith("Cargo.toml") for path in files))
        self.assertTrue(any(path.endswith(".rs") for path in files))

    # Function: test_single_file_extension_uses_tsx_for_react_jsx
    def test_single_file_extension_uses_tsx_for_react_jsx(self):
        source = (
            "import React from 'react';\n"
            "export default function App() {\n"
            "  return (<main><h1>Hello</h1></main>);\n"
            "}\n"
        )
        self.assertEqual(".tsx", _single_file_extension("typescript", source))

    # Function: test_single_file_extension_keeps_plain_typescript_as_ts
    def test_single_file_extension_keeps_plain_typescript_as_ts(self):
        source = "export const add = (left: number, right: number): number => left + right;\n"
        self.assertEqual(".ts", _single_file_extension("typescript", source))

    # Function: test_cobol_is_generated_then_repaired_by_llm_from_compiler_diagnostics
    @patch("services.validators.validate_file")
    @patch("services.llm.generate")
    @patch("services.llm.pick_compiler_repair_model", return_value="strong-repair-model")
    def test_cobol_is_generated_then_repaired_by_llm_from_compiler_diagnostics(
        self, pick_repair_model, generate, validate
    ):
        generate.side_effect = ["invalid cobol", ">>SOURCE FORMAT FREE\nIDENTIFICATION DIVISION.\n"]
        validate.side_effect = [
            ValidationResult("generated.cob", "cobol", "compiler", False, ["missing FD INPUT-FILE"]),
            ValidationResult("generated.cob", "cobol", "compiler", True, []),
        ]

        content, result, attempts = _generate_validated(
            "Generate a COBOL flat-file reader",
            model="test-model",
            system="portable GnuCOBOL",
            max_tokens=512,
            num_ctx=2048,
            rel_path="generated.cob",
            language="cobol",
            max_attempts=5,
        )

        self.assertTrue(result.passed)
        self.assertEqual(2, attempts)
        self.assertEqual(2, generate.call_count)
        self.assertEqual(2, validate.call_count)
        pick_repair_model.assert_called_once_with("test-model")
        self.assertEqual("strong-repair-model", generate.call_args.kwargs["model"])
        self.assertIs(False, generate.call_args.kwargs["think"])
        self.assertIn("missing FD INPUT-FILE", generate.call_args.args[0])
        self.assertIn("COBOL compiler rules", generate.call_args.args[0])
        self.assertIn("MANDATORY REPLACEMENTS", generate.call_args.args[0])
        self.assertIn(">>SOURCE FORMAT FREE", content)


if __name__ == "__main__":
    unittest.main()
