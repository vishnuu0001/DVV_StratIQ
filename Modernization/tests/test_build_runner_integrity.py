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
    _NPM_BUILD_TIMEOUT,
    _is_transient_toolchain_crash,
    _parse_angular_diagnostic,
    _parse_maven_diagnostic,
    _parse_maven_project_diagnostic,
    _parse_parenthesized_diagnostic,
    _vite_manifest_errors,
    _which,
    _npm_compile,
    _run_npm_subprocess_with_retry,
    _run_maven_build,
    run_build,
    toolchain_compatibility_error,
)


class BuildRunnerIntegrityTests(unittest.TestCase):
    # Function: test_npm_compile_uses_dedicated_frontend_build_timeout
    @patch("services.build_runner._run_npm_subprocess_with_retry", return_value=object())
    def test_npm_compile_uses_dedicated_frontend_build_timeout(self, run_retry):
        project_dir = Path("C:/tmp/frontend")

        _npm_compile(project_dir, "ng build")

        run_retry.assert_called_once_with(
            unittest.mock.ANY,
            project_dir,
            _NPM_BUILD_TIMEOUT,
            "<build>",
            f"frontend build timed out after {_NPM_BUILD_TIMEOUT}s",
        )

    # Function: test_which_falls_back_to_preferred_java_home_when_path_missing
    @patch("services.build_runner.find_executable", return_value=None)
    @patch("services.build_runner._preferred_java_home", return_value=Path("C:/Java/jdk-21"))
    @patch("pathlib.Path.is_file", return_value=True)
    def test_which_falls_back_to_preferred_java_home_when_path_missing(self, _is_file, _java_home, _find):
        resolved = _which("javac")
        normalized = str(resolved).replace("\\", "/").lower()
        self.assertTrue(normalized.endswith("java/jdk-21/bin/javac.exe"))

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

    # Function: test_maven_missing_module_is_attributed_to_parent_pom
    def test_maven_missing_module_is_attributed_to_parent_pom(self):
        line = (
            r"[ERROR] Child module C:\tmp\App\backend\domain-a-inventory\pom.xml "
            r"of C:\tmp\App\pom.xml does not exist"
        )
        parsed = _parse_maven_project_diagnostic(line)
        self.assertEqual(r"C:\tmp\App\pom.xml", parsed[0])
        self.assertIn("backend", parsed[1])

    # Function: test_vite_unresolved_import_is_attributed_to_package_manifest
    def test_vite_unresolved_import_is_attributed_to_package_manifest(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            package = root / "App" / "frontend" / "package.json"
            package.parent.mkdir(parents=True)
            errors = _vite_manifest_errors(
                '[vite]: Rollup failed to resolve import "axios" from "src/api.ts".',
                package,
                root,
            )
        self.assertEqual(["App/frontend/package.json"], list(errors))
        self.assertIn("axios", errors["App/frontend/package.json"][0])

    # Function: test_vite_local_alias_failure_is_attributed_to_importer
    def test_vite_local_alias_failure_is_attributed_to_importer(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            package = root / "App" / "frontend" / "package.json"
            importer = root / "App" / "frontend" / "src" / "App.tsx"
            importer.parent.mkdir(parents=True)
            errors = _vite_manifest_errors(
                f'[vite]: Rollup failed to resolve import "@/components/Card" from "{importer}".',
                package,
                root,
            )
        self.assertEqual(["App/frontend/src/App.tsx"], list(errors))
        self.assertIn("@/components/Card", errors["App/frontend/src/App.tsx"][0])

    # Function: test_vite_could_not_resolve_local_asset_is_attributed_to_importer
    def test_vite_could_not_resolve_local_asset_is_attributed_to_importer(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            package = root / "App" / "frontend" / "package.json"
            errors = _vite_manifest_errors(
                'Could not resolve "./index.css" from "src/main.tsx"',
                package,
                root,
            )
        self.assertEqual(["App/frontend/src/main.tsx"], list(errors))
        self.assertIn("./index.css", errors["App/frontend/src/main.tsx"][0])

    # Function: test_maven_build_uses_writable_service_repository
    @patch("services.build_runner._preferred_java_home", return_value=None)
    @patch("services.build_runner.subprocess.run")
    @patch("services.build_runner._MVN_PATH", "mvn.cmd")
    def test_maven_build_uses_writable_service_repository(self, run, _java_home):
        run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="", stderr="",
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "pom.xml").write_text("<project/>", encoding="utf-8")
            result = _run_maven_build(root)
        self.assertTrue(result.passed)
        command = run.call_args.args[0]
        self.assertTrue(any(arg.startswith("-Dmaven.repo.local=") for arg in command))

    # Function: test_maven_symbol_details_are_preserved_for_repair
    @patch("services.build_runner._preferred_java_home", return_value=None)
    @patch("services.build_runner.subprocess.run")
    @patch("services.build_runner._MVN_PATH", "mvn.cmd")
    def test_maven_symbol_details_are_preserved_for_repair(self, run, _java_home):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "src" / "main" / "java" / "Demo.java"
            source.parent.mkdir(parents=True)
            source.write_text("class Demo {}", encoding="utf-8")
            (root / "pom.xml").write_text("<project/>", encoding="utf-8")
            run.return_value = subprocess.CompletedProcess(
                args=[], returncode=1,
                stdout=(
                    f"[ERROR] {source}:[5,12] cannot find symbol\n"
                    "[ERROR]   symbol: class ProductDto\n"
                    "[ERROR]   location: class Demo\n"
                ),
                stderr="",
            )
            result = _run_maven_build(root)
        diagnostics = result.errors_by_file["src/main/java/Demo.java"][0]
        self.assertIn("symbol: class ProductDto", diagnostics)
        self.assertIn("location: class Demo", diagnostics)

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

    # Function: test_java_readiness_reports_missing_javac
    @patch("services.build_runner.installed_java_majors", return_value=[21])
    @patch("services.build_runner._refresh_tool_paths")
    @patch("services.build_runner._command_usable", return_value=False)
    def test_java_readiness_reports_missing_javac(self, _usable, _refresh, _versions):
        error = toolchain_compatibility_error("Java 21 Spring Boot")
        self.assertIn("javac", error)

    # Function: test_java_readiness_reports_missing_jvm_build_tool
    @patch("services.build_runner.installed_java_majors", return_value=[21])
    @patch("services.build_runner._refresh_tool_paths")
    @patch("services.build_runner._command_usable")
    def test_java_readiness_reports_missing_jvm_build_tool(self, usable, _refresh, _versions):
        usable.side_effect = lambda command: command == "javac"
        error = toolchain_compatibility_error("Java 21 Spring Boot")
        self.assertIn("mvn/gradle", error)

    # Function: test_java_project_build_uses_maven_when_pom_exists
    @patch("services.build_runner._run_maven_build")
    @patch("services.build_runner._run_manifest_build")
    def test_java_project_build_uses_maven_when_pom_exists(self, manifest_build, maven_build):
        from services.build_runner import BuildResult, _run_java_project_build
        maven_build.return_value = BuildResult(True, "maven", raw_output="ok")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "demo").mkdir(parents=True, exist_ok=True)
            (root / "demo" / "pom.xml").write_text("<project/>\n", encoding="utf-8")
            result = _run_java_project_build(root)
        self.assertTrue(result.passed)
        maven_build.assert_called_once()
        manifest_build.assert_not_called()

    # Function: test_java_project_build_uses_gradle_when_gradle_manifest_exists
    @patch("services.build_runner._run_maven_build")
    @patch("services.build_runner._run_manifest_build")
    def test_java_project_build_uses_gradle_when_gradle_manifest_exists(self, manifest_build, maven_build):
        from services.build_runner import BuildResult, _run_java_project_build
        manifest_build.return_value = BuildResult(True, "gradle-build", raw_output="ok")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "demo").mkdir(parents=True, exist_ok=True)
            (root / "demo" / "build.gradle.kts").write_text("plugins { java }\n", encoding="utf-8")
            result = _run_java_project_build(root)
        self.assertTrue(result.passed)
        manifest_build.assert_called_once()
        maven_build.assert_not_called()


if __name__ == "__main__":
    unittest.main()
