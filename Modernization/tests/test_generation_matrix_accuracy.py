# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Modernization — tests (test_generation_matrix_accuracy.py)
# Date: 2026-02-25
# ---------------------------------------------------------------------------
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from api.server import _STACK_LANGUAGE_TOOL
from services.build_runner import BuildResult, run_build
from services.modernizer.scaffolds.csharp import _gen_service
from services.modernizer.scaffolds.polyglot import generate_polyglot_project


class GenerationMatrixAccuracyTests(unittest.TestCase):
    # Function: test_framework_scaffolds_contain_the_selected_framework
    def test_framework_scaffolds_contain_the_selected_framework(self):
        cases = {
            ("c", "C17", "C17", "CLI"): ("C_STANDARD 17", "health_status"),
            ("cpp", "C++23", "C++23", "CLI"): ("CXX_STANDARD 23", "string_view"),
            ("cobol", "COBOL", "GnuCOBOL", "batch"): ("IDENTIFICATION DIVISION", "-std=ibm"),
            ("typescript", "NestJS", "NestJS", "React"): ("@nestjs/core", "nest-cli.json"),
            ("typescript", "React Native", "NestJS", "React Native 0.86"): ("react-native", "App.tsx"),
            ("typescript", "Next.js", "Next.js API routes", "Next.js App Router"): ("next build", "schema.prisma"),
            ("kotlin", "Spring", "Spring Boot", "REST API"): ("spring-boot-starter-web", "@SpringBootApplication"),
            ("kotlin", "Ktor", "Ktor", "REST API"): ("ktor-server-netty", "embeddedServer"),
            ("rust", "Axum", "Rust + Axum", "React"): ("axum", "Cargo.toml"),
            ("php", "Laravel", "PHP 8 + Laravel", "Vue"): ("laravel/framework", "bootstrap/app.php"),
            ("ruby", "Rails", "Ruby 3 + Rails", "React"): ("rails/all", "health_controller.rb"),
            ("dart", "Flutter", ".NET 8 Web API", "Flutter"): ("flutter_test", "Backend.csproj"),
            ("dart", "Dart server", "Dart 3.12 + Shelf", "REST API"): ("shelf_router", "server.dart"),
            ("elixir", "Phoenix", "Phoenix 1.8.9", "REST API"): ("phoenix, \"~> 1.8.9\"", "mix.exs"),
            ("erlang", "OTP 29", "Erlang/OTP 29", "Service"): ("-behaviour(application)", "rebar.config"),
            ("swift", "Vapor", "Vapor", "REST API"): ("vapor/vapor", 'app.get("health")'),
            ("scala", "Play", "Play Framework", "REST API"): ("PlayScala", "conf/routes"),
            ("clojure", "Ring", "Ring / Reitit", "REST API"): ("ring/ring-core", "reitit-ring"),
            ("r", "Shiny", "R 4.x", "Shiny"): ("shinyApp", "DESCRIPTION"),
            ("haskell", "Servant", "Servant", "REST API"): ("servant-server", "Main.hs"),
            ("lisp", "Common Lisp", "ANSI Common Lisp", "CLI"): ("asdf:defsystem", "main.lisp"),
            ("rpg", "AS/400", "ILE RPG", "5250"): ("crtbnrpg", "iproj.json"),
        }
        for (language, name, backend, frontend), expected in cases.items():
            with self.subTest(language=language, framework=name):
                files = generate_polyglot_project(
                    language, "Demo", "Orders",
                    {"name": name, "backend_tech": backend, "frontend_tech": frontend},
                )
                searchable = ("\n".join(files) + "\n" + "\n".join(files.values())).casefold()
                for token in expected:
                    self.assertIn(token.casefold(), searchable)

    # Function: test_composite_presets_emit_strict_spa_projects
    def test_composite_presets_emit_strict_spa_projects(self):
        cases = (
            ("rust", "Rust + Axum", "React + TypeScript", "main.tsx"),
            ("php", "PHP 8 + Laravel", "Vue 3 + TypeScript", "main.ts"),
            ("ruby", "Ruby 3 + Rails", "React + TypeScript", "main.tsx"),
        )
        for language, backend, frontend, entrypoint in cases:
            with self.subTest(language=language):
                files = generate_polyglot_project(
                    language, "Demo", "Orders",
                    {"name": f"{backend} {frontend}", "backend_tech": backend, "frontend_tech": frontend},
                )
                self.assertIn("ModernizedApp/frontend/package.json", files)
                self.assertTrue(any(path.endswith(entrypoint) for path in files))
                self.assertIn('"strict":true', files["ModernizedApp/frontend/tsconfig.json"])

    # Function: test_postgres_dotnet_uses_npgsql_not_sql_server
    def test_postgres_dotnet_uses_npgsql_not_sql_server(self):
        files = {}
        _gen_service(files, "Demo", "Orders", [], db_target="postgres")
        combined = "\n".join(files.values())
        self.assertIn("Npgsql.EntityFrameworkCore.PostgreSQL", combined)
        self.assertIn("UseNpgsql", combined)
        self.assertNotIn("UseSqlServer", combined)

    # Function: test_framework_readiness_requires_package_build_tools
    def test_framework_readiness_requires_package_build_tools(self):
        self.assertEqual("php+composer", _STACK_LANGUAGE_TOOL["php"])
        self.assertEqual("rust+rust_package_manager", _STACK_LANGUAGE_TOOL["rust"])
        self.assertEqual("kotlin+gradle", _STACK_LANGUAGE_TOOL["kotlin"])
        self.assertEqual("scala+sbt", _STACK_LANGUAGE_TOOL["scala"])
        self.assertEqual("haskell+haskell_build", _STACK_LANGUAGE_TOOL["haskell"])
        self.assertEqual("ruby+bundler", _STACK_LANGUAGE_TOOL["ruby"])
        self.assertEqual("java+maven", _STACK_LANGUAGE_TOOL["clojure"])
        self.assertEqual("elixir+mix", _STACK_LANGUAGE_TOOL["elixir"])

    # Function: test_project_builds_dispatch_to_framework_tools
    def test_project_builds_dispatch_to_framework_tools(self):
        expected = {
            "rust": "cargo", "kotlin": "gradle", "swift": "swift",
            "scala": "sbt", "r": "Rscript",
            "julia": "julia", "haskell": "cabal", "lisp": "sbcl",
            "shell": "bash",
        }
        with tempfile.TemporaryDirectory() as directory:
            for language, tool in expected.items():
                with self.subTest(language=language), patch(
                    "services.build_runner._run_manifest_build",
                    return_value=BuildResult(True, f"{tool}-build"),
                ) as mocked, patch("services.build_runner._which", return_value=None):
                    run_build({}, language, Path(directory) / language)
                    self.assertEqual(tool, mocked.call_args.args[1])


if __name__ == "__main__":
    unittest.main()
