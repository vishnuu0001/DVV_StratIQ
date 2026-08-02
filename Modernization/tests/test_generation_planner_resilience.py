import json
import unittest
from unittest.mock import patch

from services.modernizer.prompt_pipeline import (
    _npm_dependency_declaration_diagnostics,
    _path_format_examples,
    _parse_file_list_lines,
    _pf_enforce_governed_generation_files,
    _pf_expand_generated_source_closure,
    _pf_harden_framework_closure,
    _pf_infer_sql_dialect_from_output,
    _pf_reconcile_governed_manifest,
    _pf_finalize_file_list,
    _pf_plan_file_bounds,
    _pf_run_plan_generation,
    _pf_validate_final_output,
    _required_prompt_baseline,
    _requires_java_maven_multi_module,
)
from services.modernizer.scaffolds.money_transfer_demo import (
    _money_transfer_frontend_files,
    _money_transfer_schema_sql,
)
from services.modernizer.build_artifacts import _frontend_scaffold_files
from services.modernizer.target_config import resolve_sql_dialect_hint
from services.modernizer.validation_orchestration import (
    _audit_generated_project,
    _reconcile_csharp_duplicate_types,
)
from services.validators import validate_file


class GenerationPlannerResilienceTests(unittest.TestCase):
    def test_csharp_duplicate_reconciliation_keeps_namespace_aligned_implementation(self):
        project = "CreateAFullStackSolutionForABank"
        canonical = f"{project}/backend/Repositories/TransactionRepository.cs"
        redundant = f"{project}/backend/Backend/DataAccess/TransactionRepository.cs"
        source = (
            "namespace CreateAFullStackSolutionForABank.Repositories;\n"
            "public class TransactionRepository : ITransactionRepository {}\n"
        )
        output = {canonical: source, redundant: source}

        reconciled = _reconcile_csharp_duplicate_types(output)

        self.assertEqual({redundant: canonical}, reconciled)
        self.assertIn("class TransactionRepository", output[canonical])
        self.assertNotIn("class TransactionRepository", output[redundant])
        self.assertEqual(
            [],
            _audit_generated_project(
                output,
                project,
                [
                    "backend/Repositories/TransactionRepository.cs",
                    "backend/Backend/DataAccess/TransactionRepository.cs",
                ],
            ),
        )

    def test_csharp_duplicate_reconciliation_preserves_partial_and_separate_namespaces(self):
        output = {
            "Demo/One.cs": "namespace Alpha;\npublic partial class Shared {}\n",
            "Demo/Two.cs": "namespace Alpha;\npublic partial class Shared {}\n",
            "Demo/Three.cs": "namespace Beta;\npublic class Shared {}\n",
        }

        self.assertEqual({}, _reconcile_csharp_duplicate_types(output))
        self.assertTrue(all("class Shared" in content for content in output.values()))

    def test_java_multi_module_request_gets_reactor_scale_without_monolith_baseline(self):
        prompt = (
            "Java 21 Spring Boot Maven multi-module build with separate Maven modules; "
            "order-service and inventory-service are independently deployable"
        )
        signals = {"backend": "Spring Boot", "frontend": "React"}
        target = {"language": "java"}

        self.assertTrue(_requires_java_maven_multi_module(prompt, "java"))
        self.assertEqual((60, 110), _pf_plan_file_bounds(True, 4, True))
        self.assertEqual([], _required_prompt_baseline(target, "Demo", signals, prompt))
        examples = _path_format_examples("java", True, "React", True)
        self.assertIn("backend/order-service/src/main/java", examples)

    def test_java_multi_module_finalization_does_not_flatten_service_roots(self):
        prompt = "Java Spring Boot Maven multi-module build; each service is independently deployable"
        source = "backend/order-service/src/main/java/com/acme/order/OrderService.java"
        result = _pf_finalize_file_list(
            [source], {"language": "java", "frontend_tech": "React"}, "Demo",
            True, 110, None, True, True, "java", {}, (),
            {"backend": "Spring Boot", "frontend": "React"}, prompt, True,
        )

        self.assertIn(source, result)
        self.assertIn(
            "backend/order-service/src/test/java/com/acme/order/OrderServiceTest.java",
            result,
        )
        self.assertNotIn(
            "backend/src/main/java/com/acme/order/OrderService.java",
            result,
        )

    def test_generated_source_closure_adds_local_contracts_but_not_foreign_entities(self):
        project = "Demo"
        auth = f"{project}/backend/auth-service"
        order = f"{project}/backend/order-service"
        product = f"{project}/backend/product-service"
        notification = f"{project}/backend/notification-service"
        output = {
            f"{auth}/src/main/java/com/app/auth/service/AuthService.java": (
                "package com.app.auth.service; public class AuthService {}"
            ),
            f"{auth}/src/main/java/com/app/auth/controller/AuthController.java": (
                "package com.app.auth.controller;\n"
                "import com.app.auth.dto.LoginRequest;\n"
                "class AuthController { AuthService service; LoginRequest request; }"
            ),
            f"{order}/src/main/java/com/app/order/entity/Order.java": (
                "package com.app.order.entity; public class Order {}"
            ),
            f"{notification}/src/main/java/com/app/notification/NotificationApplication.java": (
                "package com.app.notification; public class NotificationApplication {}"
            ),
            f"{product}/src/main/java/com/app/product/ProductService.java": (
                "package com.app.product;\nimport com.app.order.entity.Order;\n"
                "class ProductService { Order forbidden; ProductDto dto; }"
            ),
            f"{order}/src/main/java/com/app/order/service/OrderService.java": (
                "package com.app.order.service;\n"
                "import com.app.notification.event.InventoryUpdatedEvent;\n"
                "class OrderService { InventoryUpdatedEvent event; }"
            ),
            f"{project}/frontend/src/App.tsx": (
                "import AppRoutes from './routes/AppRoutes'; export default AppRoutes;"
            ),
        }

        added = _pf_expand_generated_source_closure(output, project)

        self.assertIn(
            f"{auth}/src/main/java/com/app/auth/dto/LoginRequest.java", added,
        )
        self.assertIn(
            f"{product}/src/main/java/com/app/product/dto/ProductDto.java", added,
        )
        self.assertNotIn(
            f"{product}/src/main/java/com/app/order/entity/Order.java", output,
        )
        local_event = (
            f"{order}/src/main/java/com/app/order/event/InventoryUpdatedEvent.java"
        )
        self.assertIn(local_event, added)
        self.assertIn(
            "import com.app.order.event.InventoryUpdatedEvent;",
            output[f"{order}/src/main/java/com/app/order/service/OrderService.java"],
        )
        self.assertIn(f"{project}/frontend/src/routes/AppRoutes.tsx", added)

    def test_money_transfer_schema_uses_detectable_sql_server_dialect(self):
        result = validate_file(
            "database/schema.sql", _money_transfer_schema_sql(), "sql", dialect_hint="postgres",
        )
        self.assertTrue(result.passed, result.diagnostics)

    def test_governance_replaces_mixed_sql_with_valid_sql_server_scripts(self):
        project = "CreateAFullStackSolutionForABank"
        output = {
            f"{project}/database/schema.sql": (
                "CREATE TABLE Accounts "
                "(Id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY);"
            ),
            f"{project}/backend/migrations/CreateTables.sql": "SELECT 1;",
        }

        protected = _pf_enforce_governed_generation_files(output, project, True, "mssql")

        for rel_path in (
            f"{project}/database/schema.sql",
            f"{project}/backend/migrations/CreateTables.sql",
        ):
            with self.subTest(path=rel_path):
                self.assertIn(rel_path, protected)
                result = validate_file(
                    rel_path, output[rel_path], "sql", dialect_hint="mssql",
                )
                self.assertTrue(result.passed, result.diagnostics)

    def test_machine_readable_database_target_wins_over_ambiguous_description(self):
        self.assertEqual(
            "mssql",
            resolve_sql_dialect_hint({
                "db_target": "mssql",
                "db_tech": "PostgreSQL / MS SQL (via API)",
            }),
        )

    def test_final_project_validation_forbids_implicit_ansi_sql(self):
        counts, failures = _pf_validate_final_output(
            {"Demo/database/schema.sql": "CREATE TABLE Accounts (Id INTEGER);"},
            "csharp",
            "",
            lambda *_args: None,
        )
        self.assertEqual(1, counts["failed"])
        self.assertEqual("UNCONFIGURED", failures[0]["dialect"])
        self.assertIn("generic ANSI fallback is prohibited", failures[0]["diagnostics"][0])

    def test_final_project_validation_records_normalized_sql_server_dialect(self):
        counts, failures = _pf_validate_final_output(
            {"Demo/database/schema.sql": "IF NOT EXISTS BROKEN TSQL"},
            "csharp",
            "mssql",
            lambda *_args: None,
        )
        self.assertEqual(1, counts["failed"])
        self.assertEqual("tsql", failures[0]["dialect"])
        self.assertIn("tsql parse error", failures[0]["diagnostics"][0].casefold())

    def test_azure_angular_pack_pins_ngmodule_entrypoint(self):
        files = _money_transfer_frontend_files(True)
        main = files["frontend/src/main.ts"]
        self.assertIn("platformBrowserDynamic", main)
        self.assertIn("./app/app.module", main)
        self.assertNotIn("route-config", main)

    def test_money_transfer_pack_removes_all_competing_feature_folder_variants(self):
        project = "CreateAFullStackSolutionForABank"
        competing_paths = (
            "frontend/src/app/features/transfer/transfer.component.ts",
            "frontend/src/app/features/transfers/transfer.component.ts",
            "frontend/src/app/features/money-transfer/transfer.component.ts",
        )
        output = {
            f"{project}/{path}": "export class CompetingTransferComponent {}"
            for path in competing_paths
        }

        protected = _pf_enforce_governed_generation_files(output, project, True, "mssql")

        for path in competing_paths:
            self.assertNotIn(f"{project}/{path}", output)
        canonical_path = (
            f"{project}/frontend/src/app/features/transactions/"
            "transfer-form.component.ts"
        )
        self.assertIn(canonical_path, output)
        self.assertIn(canonical_path, protected)

    def test_money_transfer_pack_removes_competing_msal_and_model_files(self):
        project = "CreateAFullStackSolutionForABank"
        competing_paths = (
            "frontend/src/app/auth/msal-auth.guard.ts",
            "frontend/src/app/auth/msal-interceptor.ts",
            "frontend/src/app/core/models/money-transfer.model.ts",
        )
        output = {
            f"{project}/{path}": "export class CompetingAuthOrModel {}"
            for path in competing_paths
        }

        _pf_enforce_governed_generation_files(output, project, True, "mssql")

        for path in competing_paths:
            self.assertNotIn(f"{project}/{path}", output)

    def test_angular_scaffold_avoids_node_typing_resolution_conflict(self):
        files = _frontend_scaffold_files("Angular 17", "Demo", True)
        package = json.loads(files["frontend/package.json"])
        tsconfig = json.loads(files["frontend/tsconfig.json"])

        self.assertNotIn("@types/node", package["devDependencies"])
        self.assertTrue(tsconfig["compilerOptions"]["skipLibCheck"])
        self.assertEqual([], tsconfig["compilerOptions"]["types"])

    def test_prebuild_hardening_repairs_legacy_angular_node_typings(self):
        output = {
            "Demo/frontend/package.json": json.dumps({
                "dependencies": {"@angular/core": "^17.0.0"},
                "devDependencies": {"@types/node": "20.11.30", "typescript": "5.2.2"},
            }),
            "Demo/frontend/tsconfig.json": json.dumps({
                "compilerOptions": {"moduleResolution": "bundler", "types": ["node"]},
            }),
        }

        _pf_harden_framework_closure(output)

        package = json.loads(output["Demo/frontend/package.json"])
        tsconfig = json.loads(output["Demo/frontend/tsconfig.json"])
        self.assertNotIn("@types/node", package["devDependencies"])
        self.assertNotIn("node", tsconfig["compilerOptions"]["types"])
        self.assertTrue(tsconfig["compilerOptions"]["skipLibCheck"])

    def test_frontend_black_box_test_uses_sibling_frontend_package_boundary(self):
        output = {
            "Demo/frontend/package.json": json.dumps({
                "dependencies": {"@angular/core": "^17.0.0"},
                "devDependencies": {"vitest": "^2.0.0"},
            }),
            "Demo/tests/frontend/app.spec.ts": (
                "import { signal } from '@angular/core';\n"
                "import { describe } from 'vitest';\n"
            ),
        }
        self.assertEqual([], _npm_dependency_declaration_diagnostics(output))

    def test_prebuild_hardening_closes_npgsql_in_owning_dotnet_project(self):
        output = {
            "Demo/backend/Demo.csproj": (
                '<Project Sdk="Microsoft.NET.Sdk.Web">\n'
                '  <PropertyGroup><TargetFramework>net8.0</TargetFramework></PropertyGroup>\n'
                '</Project>\n'
            ),
            "Demo/backend/Data/ConnectionFactory.cs": (
                "using Npgsql;\n"
                "public sealed class ConnectionFactory { "
                "public NpgsqlConnection Open() => new(\"Host=localhost\"); }\n"
            ),
            "Demo/worker/Worker.csproj": (
                '<Project Sdk="Microsoft.NET.Sdk.Worker">\n'
                '  <PropertyGroup><TargetFramework>net8.0</TargetFramework></PropertyGroup>\n'
                '</Project>\n'
            ),
            "Demo/worker/Worker.cs": "public sealed class Worker {}\n",
        }

        _pf_harden_framework_closure(output)
        _pf_harden_framework_closure(output)

        backend_project = output["Demo/backend/Demo.csproj"]
        self.assertEqual(1, backend_project.count('Include="Npgsql"'))
        self.assertNotIn("Npgsql", output["Demo/worker/Worker.csproj"])

    def test_prebuild_hardening_closes_use_npgsql_ef_provider(self):
        output = {
            "Demo/backend/Demo.csproj": (
                '<Project Sdk="Microsoft.NET.Sdk.Web">\n'
                '  <PropertyGroup><TargetFramework>net10.0</TargetFramework></PropertyGroup>\n'
                '</Project>\n'
            ),
            "Demo/backend/Program.cs": (
                "using Microsoft.EntityFrameworkCore;\n"
                "services.AddDbContext<AppDbContext>(o => o.UseNpgsql(connection));\n"
            ),
        }

        _pf_harden_framework_closure(output)

        project = output["Demo/backend/Demo.csproj"]
        self.assertIn('Include="Npgsql.EntityFrameworkCore.PostgreSQL" Version="10.0.0"', project)

    def test_accepts_json_objects_and_windows_paths(self):
        response = """```json
        {"files": [
          {"path": "backend\\\\Program.cs"},
          {"file_path": "frontend/src/app/app.component.ts"},
          ".github/workflows/ci.yml"
        ]}
        ```"""
        self.assertEqual(
            [
                "backend/Program.cs",
                "frontend/src/app/app.component.ts",
                ".github/workflows/ci.yml",
            ],
            _parse_file_list_lines(response),
        )

    def test_manifest_parser_rejects_member_expressions_as_file_paths(self):
        self.assertEqual(
            ["backend/Models/TransferRequest.cs"],
            _parse_file_list_lines(
                "backend/Models/TransferRequest.cs\nbackend/Models/request.Amount\n"
            ),
        )

    def test_generated_npgsql_provider_is_authoritative_for_sql_validation(self):
        output = {
            "Demo/backend/Demo.csproj": (
                '<Project><ItemGroup><PackageReference Include="Npgsql" '
                'Version="8.0.3" /></ItemGroup></Project>'
            ),
            "Demo/backend/Data/Connection.cs": "using Npgsql;\n",
            "Demo/database/schema.sql": "SELECT 1;\n",
        }
        self.assertEqual("postgres", _pf_infer_sql_dialect_from_output(output))

    def test_conflicting_generated_database_providers_do_not_guess_a_dialect(self):
        output = {
            "Demo/backend/Postgres.cs": "using Npgsql;\n",
            "Demo/backend/SqlServer.cs": "using Microsoft.Data.SqlClient;\n",
        }
        self.assertEqual("", _pf_infer_sql_dialect_from_output(output))

    def test_money_transfer_manifest_discards_superseded_model_taxonomy(self):
        output = {"Demo/backend/DTOs/TransferRequestDto.cs": "public class TransferRequestDto {}"}
        reconciled = _pf_reconcile_governed_manifest(
            ["backend/Backend/Models/TransferRequest.cs"], output, "Demo", True,
        )
        self.assertEqual([], reconciled)

    def test_recovers_complete_paths_from_truncated_json(self):
        response = (
            '{"files":[{"path":"backend/Program.cs"},'
            '{"path":"backend/Controllers/TransfersController.cs"},'
        )
        self.assertEqual(
            ["backend/Program.cs", "backend/Controllers/TransfersController.cs"],
            _parse_file_list_lines(response),
        )

    def test_rejects_unsafe_and_non_file_entries(self):
        response = """
        C:\\Windows\\system.ini
        /etc/passwd
        ../outside.py
        https://example.invalid/payload.py
        backend/Controllers
        backend/Program.cs
        """
        self.assertEqual(["backend/Program.cs"], _parse_file_list_lines(response))

    @patch("services.llm.generate", return_value="")
    def test_empty_llm_plan_uses_deterministic_baseline(self, _generate):
        progress_events = []
        result = _pf_run_plan_generation(
            "prompt", "", [], 100, 10, "model", "system",
            lambda phase, pct, message: progress_events.append((phase, pct, message)),
            ["backend/Program.cs", "backend/appsettings.json"],
        )
        self.assertEqual(
            ["backend/Program.cs", "backend/appsettings.json"],
            result[0],
        )
        self.assertTrue(any("deterministic baseline" in event[2] for event in progress_events))


if __name__ == "__main__":
    unittest.main()
