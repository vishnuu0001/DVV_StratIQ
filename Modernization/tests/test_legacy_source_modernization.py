# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Modernization — tests (test_legacy_source_modernization.py)
# Date: 2025-09-22
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# Scope: Legacy enterprise source-to-modern-target modernization coverage.
# ---------------------------------------------------------------------------
import tempfile
import unittest
from pathlib import Path

from services.analyzer import _CODE_EXTS, _LANG_MAP, analyze_project
from services.modernizer._shared import _make_output_path
from services.modernizer.conversion_pipeline import (
    _CONVERTIBLE,
    _collect_source_files,
    _extract_file_structure,
    _stack_conversion_hints,
)


class LegacySourceModernizationTests(unittest.TestCase):
    # Function: test_all_requested_legacy_extensions_are_ingested
    def test_all_requested_legacy_extensions_are_ingested(self):
        expected = {
            ".f90": "fortran", ".pas": "pascal", ".pli": "pli",
            ".jcl": "jcl", ".m": "mumps", ".nsp": "natural",
            ".p": "progress4gl", ".adb": "ada", ".ml": "ocaml",
            ".pro": "prolog", ".rpgle": "rpg",
        }
        for extension, language in expected.items():
            with self.subTest(extension=extension):
                self.assertEqual(language, _LANG_MAP[extension])
                self.assertEqual(language, _CONVERTIBLE[extension])
                self.assertIn(extension, _CODE_EXTS)

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for extension in expected:
                (root / f"sample{extension}").write_text("legacy source\n", encoding="utf-8")
            self.assertEqual(set(expected), {path.suffix for path in _collect_source_files(directory)})

    # Function: test_structure_extraction_preserves_legacy_units
    def test_structure_extraction_preserves_legacy_units(self):
        cases = {
            "fortran": ("PROGRAM PAYROLL\nSUBROUTINE TAX", ("PAYROLL", "TAX")),
            "pascal": ("unit Orders;\nprocedure SaveOrder;", ("Orders", "SaveOrder")),
            "pli": ("PAY: PROCEDURE OPTIONS(MAIN);", ("PAY",)),
            "jcl": ("//PAYJOB JOB\n//STEP01 EXEC PGM=PAY\n//IN DD DSN=A", ("PAYJOB", "STEP01", "IN")),
            "ada": ("package body Payroll is\nprocedure Run is", ("Payroll", "Run")),
            "ocaml": ("module Ledger = struct\nlet post x = x", ("Ledger", "post")),
            "prolog": ("eligible(Person) :- employed(Person).", ("eligible",)),
        }
        for language, (source, names) in cases.items():
            with self.subTest(language=language):
                structure = _extract_file_structure(source, language)
                for name in names:
                    self.assertIn(name, structure)

    # Function: test_java_and_dotnet_prompts_receive_semantic_migration_rules
    def test_java_and_dotnet_prompts_receive_semantic_migration_rules(self):
        languages = (
            "fortran", "pascal", "pli", "jcl", "mumps",
            "natural", "progress4gl", "ada", "ocaml", "prolog",
        )
        for language in languages:
            for target in ("java", "csharp"):
                with self.subTest(language=language, target=target):
                    hints = _stack_conversion_hints(language, {"language": target})
                    self.assertIn("traceability map", hints)
                    self.assertIn("parity tests", hints)

    # Function: test_same_stem_legacy_sources_cannot_overwrite_each_other
    def test_same_stem_legacy_sources_cannot_overwrite_each_other(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            paths = [
                _make_output_path(root / "PAY.f90", root, "java", "Demo", "java_spring"),
                _make_output_path(root / "PAY.jcl", root, "java", "Demo", "java_spring"),
                _make_output_path(root / "PAY.pli", root, "java", "Demo", "java_spring"),
            ]
            self.assertEqual(len(paths), len(set(paths)))

    # Function: test_analyzer_identifies_legacy_technology
    def test_analyzer_identifies_legacy_technology(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "PAYROLL.f90").write_text(
                "PROGRAM PAYROLL\nIMPLICIT NONE\nEND PROGRAM PAYROLL\n",
                encoding="utf-8",
            )
            report = analyze_project(directory)
            self.assertIn("fortran_legacy", report["tech_stack"])
            self.assertEqual(1, report["file_count"])
            self.assertEqual(1, report["languages"]["fortran"]["files"])

    def test_java_text_is_not_misclassified_as_legacy_languages(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "Example.java").write_text(
                "package demo; public class Example { "
                "void write() {} Object read() { return null; } }\n",
                encoding="utf-8",
            )
            (root / "README.md").write_text(
                "PROGRAM PACKAGE FUNCTION WRITE READ GOTO DO BEGIN END\n",
                encoding="utf-8",
            )
            report = analyze_project(directory)
            for false_technology in (
                "ibmi_rpg", "fortran_legacy", "mumps", "ada_language", "prolog_rules",
            ):
                self.assertNotIn(false_technology, report["tech_stack"])
            self.assertEqual("Java Standard Application", report["architecture"]["pattern"])


if __name__ == "__main__":
    unittest.main()
