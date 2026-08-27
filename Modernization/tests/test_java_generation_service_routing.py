import tempfile
import unittest
from pathlib import Path

from api.server import _resolve_quick_analysis_target


class JavaGenerationServiceRoutingTests(unittest.TestCase):
    def test_legacy_quick_analysis_default_resolves_java_only_source_to_java(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "src" / "main" / "java" / "com" / "example" / "App.java"
            source.parent.mkdir(parents=True)
            source.write_text("package com.example; public class App {}", encoding="utf-8")

            self.assertEqual(
                "spring_boot",
                _resolve_quick_analysis_target(str(root), "aveva_mes"),
            )

    def test_explicit_target_is_never_overridden(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "App.java").write_text("public class App {}", encoding="utf-8")

            self.assertEqual(
                "dotnet_react",
                _resolve_quick_analysis_target(str(root), "dotnet_react"),
            )

    def test_mixed_java_and_dotnet_source_keeps_requested_default(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "App.java").write_text("public class App {}", encoding="utf-8")
            (root / "App.cs").write_text("public class App {}", encoding="utf-8")

            self.assertEqual(
                "aveva_mes",
                _resolve_quick_analysis_target(str(root), "aveva_mes"),
            )


if __name__ == "__main__":
    unittest.main()
