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
from services.modernizer.build_artifacts import (
    _backend_manifest_files,
    _reconcile_java_generation_output,
)
from services.modernizer.scaffolds.csharp import _gen_service
from services.modernizer.scaffolds.polyglot import generate_polyglot_project


class GenerationMatrixAccuracyTests(unittest.TestCase):
    # Function: test_java_generation_owns_single_module_maven_contract
    def test_java_generation_owns_single_module_maven_contract(self):
        files = _backend_manifest_files(
            "java", "InventoryService", "Java 21 Spring Boot 3",
            is_dapper=False, is_azure_auth=False, db_target="postgres",
        )
        self.assertEqual(["backend/pom.xml"], list(files))
        pom = files["backend/pom.xml"]
        self.assertIn("<java.version>21</java.version>", pom)
        self.assertIn("spring-boot-starter-data-jpa", pom)
        self.assertIn("spring-boot-starter-oauth2-resource-server", pom)
        self.assertIn("spring-cloud-starter-openfeign", pom)
        self.assertIn("software.amazon.awssdk", pom)
        self.assertNotIn("<modules>", pom)
        self.assertNotIn("<module>", pom)

    # Function: test_java_reconciliation_removes_rogue_reactor_and_closes_frontend_imports
    def test_java_reconciliation_removes_rogue_reactor_and_closes_frontend_imports(self):
        output = {
            "Inventory/backend/pom.xml": _backend_manifest_files(
                "java", "Inventory", "Java 21 Spring Boot 3", False, False,
            )["backend/pom.xml"],
            "Inventory/pom.xml": (
                "<project><modules>"
                "<module>backend/domain-a-inventory</module>"
                "<module>backend/src/main/java/com/modernize/orders</module>"
                "</modules></project>"
            ),
            "Inventory/frontend/package.json": (
                '{"dependencies":{"react":"^18.2.0"},"devDependencies":{}}'
            ),
            "Inventory/frontend/src/App.tsx": (
                "import axios from 'axios';\n"
                "import { QueryClient } from '@tanstack/react-query';\n"
                "import local from './local';\n"
            ),
        }
        _reconcile_java_generation_output(output, "Inventory")
        self.assertNotIn("Inventory/pom.xml", output)
        package = __import__("json").loads(output["Inventory/frontend/package.json"])
        self.assertIn("axios", package["dependencies"])
        self.assertIn("@tanstack/react-query", package["dependencies"])
        self.assertNotIn(".", package["dependencies"])

    # Function: test_java_reconciliation_flattens_modules_and_repairs_type_ownership
    def test_java_reconciliation_flattens_modules_and_repairs_type_ownership(self):
        output = {
            "Inventory/backend/pom.xml": _backend_manifest_files(
                "java", "Inventory", "Java 21 Spring Boot 3", False, False,
            )["backend/pom.xml"],
            "Inventory/backend/inventory-service/src/main/java/com/inventory/dto/ProductDto.java": (
                "package com.inventory.dto;\npublic record ProductDto(String id) {}\n"
            ),
            "Inventory/backend/src/main/java/com/modernize/InventoryController.java": (
                "package com.modernize;\n"
                "import com.wrong.api.ProductDto;\n"
                "public class InventoryController { ProductDto product; }\n"
            ),
            "Inventory/frontend/package.json": '{"dependencies":{},"devDependencies":{}}',
            "Inventory/frontend/src/main.tsx": (
                "import './index.css';\nexport const ready = true;\n"
            ),
        }
        _reconcile_java_generation_output(output, "Inventory")
        flattened = (
            "Inventory/backend/src/main/java/com/inventory/dto/ProductDto.java"
        )
        self.assertIn(flattened, output)
        self.assertNotIn(
            "Inventory/backend/inventory-service/src/main/java/com/inventory/dto/ProductDto.java",
            output,
        )
        controller = output[
            "Inventory/backend/src/main/java/com/modernize/InventoryController.java"
        ]
        self.assertIn("import com.inventory.dto.ProductDto;", controller)
        self.assertIn("Inventory/frontend/src/index.css", output)

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
