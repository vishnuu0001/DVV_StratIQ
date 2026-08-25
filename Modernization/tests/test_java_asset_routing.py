# ---------------------------------------------------------------------------
# Scope: Java-only legacy asset routing and compiler-repair eligibility.
# ---------------------------------------------------------------------------
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest.mock import patch

from services.modernizer._shared import _make_output_path
from services.modernizer.conversion_pipeline import _caf_convert_one_file
from services.modernizer.prompt_pipeline import (
    _pf_java_repair_candidates,
    _pf_repair_build_round,
)


class JavaAssetPathRoutingTests(unittest.TestCase):
    def test_java_sources_resources_and_browser_assets_use_distinct_roots(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            cases = {
                root / "src/main/java/com/example/Order.java":
                    "ModernizedApp/src/main/java/com/example/Order.java",
                root / "TransportationSetup/WEB-INF/web.xml":
                    "ModernizedApp/src/main/resources/TransportationSetup/WEB-INF/web.xml",
                root / "TransportationSetup/javascript/jquery.min.js":
                    "ModernizedApp/frontend/public/legacy/TransportationSetup/javascript/jquery.min.js",
                root / "TransportationSetup/styles/site.css":
                    "ModernizedApp/frontend/public/legacy/TransportationSetup/styles/site.css",
            }
            for source, expected in cases.items():
                with self.subTest(source=source):
                    actual = _make_output_path(source, root, "java", "Demo", "spring_boot")
                    self.assertEqual(actual.replace("\\", "/"), expected)

    def test_non_java_path_contract_is_unchanged(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "src/assets/site.js"
            actual = _make_output_path(source, root, "csharp", "Demo", "dotnet")
            self.assertEqual(actual.replace("\\", "/"), "ModernizedApp/src/Assets/site.cs")


class JavaLegacyBrowserPreservationTests(unittest.TestCase):
    def test_browser_asset_is_preserved_without_calling_ollama(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "TransportationSetup/javascript/jquery.min.js"
            source.parent.mkdir(parents=True)
            original = "!function(a){a.legacy=true}(window);"
            source.write_text(original, encoding="utf-8")

            with patch(
                "services.modernizer.conversion_pipeline._caf_convert_with_llm",
                side_effect=AssertionError("browser assets must not invoke Ollama"),
            ):
                output_path, content, log_entry = _caf_convert_one_file(
                    source, root, "Demo", "spring_boot", "java",
                    {"name": "Spring Boot", "language": "java"}, {}, True,
                    "test-model", "java-system", "", {}, set(), {".js"}, {}, None,
                )

        self.assertEqual(content, original)
        self.assertTrue(output_path.endswith("/jquery.min.js"))
        self.assertEqual(log_entry["type"], "config_preserved")
        self.assertEqual(log_entry["asset_kind"], "legacy_frontend")

    def test_java_resource_is_preserved_without_invalid_migration_prefix(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "WEB-INF/web.xml"
            source.parent.mkdir(parents=True)
            original = '<?xml version="1.0" encoding="UTF-8"?>\n<web-app/>\n'
            source.write_text(original, encoding="utf-8")

            output_path, content, log_entry = _caf_convert_one_file(
                source, root, "Demo", "spring_boot", "java",
                {"name": "Spring Boot", "language": "java"}, {}, True,
                "test-model", "java-system", "", {}, {".xml"}, set(), {}, None,
            )

        self.assertEqual(content, original)
        self.assertIn("/src/main/resources/", output_path.replace("\\", "/"))
        self.assertEqual(log_entry["type"], "config_preserved")


class JavaCompilerRepairCandidateTests(unittest.TestCase):
    def test_only_genuine_java_and_generated_frontend_sources_are_repaired(self):
        fixable = {
            "ModernizedApp/src/main/java/com/example/App.java": ["cannot find symbol"],
            "ModernizedApp/frontend/src/App.tsx": ["TS2304: missing"],
            "ModernizedApp/Database/schema_postgres.sql": ["parser error"],
            "ModernizedApp/gateway/application.yml": ["invalid config"],
            "ModernizedApp/src/main/java/Legacy/javascript/jquery.min.java": ["illegal start"],
        }
        candidates, ignored = _pf_java_repair_candidates(fixable)

        self.assertEqual(
            set(candidates),
            {
                "ModernizedApp/src/main/java/com/example/App.java",
                "ModernizedApp/frontend/src/App.tsx",
            },
        )
        self.assertEqual(set(ignored), set(fixable) - set(candidates))

    def test_java_repair_defaults_to_one_ollama_worker(self):
        active = 0
        max_active = 0
        lock = threading.Lock()

        def generate(_prompt, **_kwargs):
            nonlocal active, max_active
            with lock:
                active += 1
                max_active = max(max_active, active)
            time.sleep(0.02)
            with lock:
                active -= 1
            return "public class Fixed {}"

        fixable = {
            "Demo/First.java": ["cannot find symbol"],
            "Demo/Second.java": ["cannot find symbol"],
        }
        output = {path: "public class Broken {}" for path in fixable}
        with patch("services.llm.generate", side_effect=generate), \
                patch.dict("os.environ", {}, clear=False):
            import os
            previous = os.environ.pop("MODERNIZATION_JAVA_REPAIR_WORKERS", None)
            try:
                _pf_repair_build_round(
                    fixable, 1, 2, output, "", "", "test-model", "system",
                    lambda *_args: None, language="java",
                )
            finally:
                if previous is not None:
                    os.environ["MODERNIZATION_JAVA_REPAIR_WORKERS"] = previous

        self.assertEqual(max_active, 1)


if __name__ == "__main__":
    unittest.main()
