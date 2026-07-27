# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Modernization — build-runner fail-closed and extension coverage tests
# Date: 2026-07-23
# ---------------------------------------------------------------------------
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from services.build_runner import (
    _is_transient_toolchain_crash,
    _parse_angular_diagnostic,
    _parse_maven_diagnostic,
    _parse_parenthesized_diagnostic,
    _run_npm_subprocess_with_retry,
    run_build,
    toolchain_compatibility_error,
)


class BuildRunnerIntegrityTests(unittest.TestCase):
    # Function: test_diagnostic_parsers_preserve_paths_and_messages
    def test_diagnostic_parsers_preserve_paths_and_messages(self):
        self.assertEqual(
            (r"C:\work\Demo.cs", "12", "CS1002", "; expected"),
            _parse_parenthesized_diagnostic(
                r"C:\work\Demo.cs(12,7): error CS1002: ; expected [Demo.csproj]",
                "CS",
            ),
        )
        self.assertEqual(
            (r"C:\work\Demo.java", "';' expected"),
            _parse_maven_diagnostic(r"[ERROR] C:\work\Demo.java:[9,18] ';' expected"),
        )
        self.assertEqual(
            (r"C:\work\App.tsx", "TS1005", "')' expected."),
            _parse_angular_diagnostic(r"Error: C:\work\App.tsx:4:9 - error TS1005: ')' expected."),
        )

    # Function: test_transient_npm_crash_is_retried_and_recovers
    @patch("services.build_runner.time.sleep")
    @patch("services.build_runner.subprocess.run")
    def test_transient_npm_crash_is_retried_and_recovers(self, run, _sleep):
        crash = subprocess.CompletedProcess(
            args=["npm", "install"], returncode=1, stdout="",
            stderr="[low_level_alloc.cc : 554] RAW: Check new_pages != nullptr failed: VirtualAlloc failed",
        )
        success = subprocess.CompletedProcess(args=["npm", "install"], returncode=0, stdout="ok", stderr="")
        run.side_effect = [crash, success]

        result = _run_npm_subprocess_with_retry(
            ["npm", "install"], Path("."), 180, "<install>", "timed out",
        )

        self.assertEqual(0, result.returncode)
        self.assertEqual(2, run.call_count)
        _sleep.assert_called_once()

    # Function: test_transient_npm_crash_gives_up_after_max_retries
    @patch("services.build_runner.time.sleep")
    @patch("services.build_runner.subprocess.run")
    def test_transient_npm_crash_gives_up_after_max_retries(self, run, _sleep):
        crash = subprocess.CompletedProcess(
            args=["npm", "install"], returncode=1, stdout="",
            stderr="RAW: Check new_pages != nullptr failed: VirtualAlloc failed",
        )
        run.return_value = crash

        result = _run_npm_subprocess_with_retry(
            ["npm", "install"], Path("."), 180, "<install>", "timed out",
        )

        self.assertIs(crash, result)
        self.assertEqual(3, run.call_count)  # 1 initial attempt + 2 retries

    # Function: test_real_dependency_failure_is_not_retried
    @patch("services.build_runner.time.sleep")
    @patch("services.build_runner.subprocess.run")
    def test_real_dependency_failure_is_not_retried(self, run, _sleep):
        not_found = subprocess.CompletedProcess(
            args=["npm", "install"], returncode=1, stdout="",
            stderr="npm error 404 Not Found - GET https://registry.npmjs.org/nonexistent-package",
        )
        run.return_value = not_found

        result = _run_npm_subprocess_with_retry(
            ["npm", "install"], Path("."), 180, "<install>", "timed out",
        )

        self.assertIs(not_found, result)
        self.assertEqual(1, run.call_count)
        _sleep.assert_not_called()

    # Function: test_is_transient_toolchain_crash_ignores_successful_runs
    def test_is_transient_toolchain_crash_ignores_successful_runs(self):
        ok = subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr="VirtualAlloc failed")
        self.assertFalse(_is_transient_toolchain_crash(ok))

    # Function: test_missing_manifest_fails_strict_build
    def test_missing_manifest_fails_strict_build(self):
        with tempfile.TemporaryDirectory() as directory:
            result = run_build({"src/App.ts": "export const value = 1;\n"}, "typescript", Path(directory))
        self.assertFalse(result.passed)
        self.assertEqual("missing-manifest", result.checker)

    # Function: test_internal_build_error_fails_closed
    @patch("services.build_runner._materialize", side_effect=RuntimeError("boom"))
    def test_internal_build_error_fails_closed(self, _materialize):
        with tempfile.TemporaryDirectory() as directory:
            result = run_build({"main.py": "print('ok')\n"}, "python", Path(directory))
        self.assertFalse(result.passed)
        self.assertEqual("build-runner-error", result.checker)

    # Function: test_unknown_build_route_fails_closed
    def test_unknown_build_route_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            result = run_build({"source.unknown": "content\n"}, "unknown", Path(directory))
        self.assertFalse(result.passed)
        self.assertEqual("unsupported-build-route", result.checker)

    # Function: test_python_project_runs_generated_tests
    def test_python_project_runs_generated_tests(self):
        output = {
            "app/math_service.py": "def add(a: int, b: int) -> int:\n    return a + b\n",
            "tests/test_math_service.py": (
                "import unittest\n"
                "from app.math_service import add\n\n"
                "class MathTests(unittest.TestCase):\n"
                "    def test_add(self):\n"
                "        self.assertEqual(3, add(1, 2))\n"
            ),
        }
        with tempfile.TemporaryDirectory() as directory:
            result = run_build(output, "python", Path(directory))
        self.assertTrue(result.passed, result.errors_by_file)

    # Function: test_python_project_without_tests_fails_closed
    def test_python_project_without_tests_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            result = run_build({"app.py": "print('ok')\n"}, "python", Path(directory))
        self.assertFalse(result.passed)
        self.assertEqual("missing-tests", result.checker)

    # Function: test_csharp_marker_does_not_require_c_compiler
    @patch("services.build_runner._parser_compatibility_error", return_value=None)
    @patch("services.build_runner._java_compatibility_error", return_value=None)
    @patch("services.build_runner._dotnet_compatibility_error", return_value=None)
    @patch("services.build_runner._refresh_tool_paths")
    def test_csharp_marker_does_not_require_c_compiler(self, _refresh, _dotnet, _java, _parser):
        self.assertIsNone(toolchain_compatibility_error("language:csharp"))

    # Function: test_java_readiness_requires_javac_and_maven
    @patch("services.build_runner.installed_java_majors", return_value=[21])
    @patch("services.build_runner._refresh_tool_paths")
    @patch("services.build_runner.shutil.which")
    def test_java_readiness_requires_javac_and_maven(self, which, _refresh, _versions):
        which.side_effect = lambda command: {
            "java": "java.exe",
            "javac": None,
            "javac.cmd": None,
            "mvn": None,
            "mvn.cmd": None,
        }.get(command)
        error = toolchain_compatibility_error("Java 21 Spring Boot")
        self.assertIn("javac", error)
        self.assertIn("mvn", error)


if __name__ == "__main__":
    unittest.main()
