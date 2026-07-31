# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Modernization — tests (test_generation_matrix_accuracy.py)
# Date: 2026-02-25
# ---------------------------------------------------------------------------
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import patch

from api.server import _STACK_LANGUAGE_TOOL
from services.build_runner import BuildResult, run_build
from services.modernizer.build_artifacts import (
    _backend_manifest_files,
    _reconcile_java_generation_output,
)
from services.modernizer.prompt_pipeline import (
    _pf_attribute_java_frontend_build_errors,
    _pf_build_error_identifiers,
    _pf_run_build_and_repair,
)
from services.validators import validate_file
from services.modernizer.scaffolds.csharp import _gen_service
from services.modernizer.scaffolds.polyglot import generate_polyglot_project


class GenerationMatrixAccuracyTests(unittest.TestCase):
    # Function: test_java_repair_context_extracts_maven_provider_symbols
    def test_java_repair_context_extracts_maven_provider_symbols(self):
        identifiers = _pf_build_error_identifiers([
            "cannot find symbol — symbol: method getAllProducts() "
            "— location: variable productService of type com.inventory.service.ProductService",
            "no suitable constructor found for Order(java.lang.String)",
        ])
        self.assertIn("getAllProducts", identifiers)
        self.assertIn("ProductService", identifiers)
        self.assertIn("Order", identifiers)

        constructor_identifiers = _pf_build_error_identifiers([
            "constructor User in class com.app.auth.entity.User cannot be applied to given types;",
            "incompatible types: com.app.product.entity.Product cannot be converted to "
            "java.util.Optional<com.app.product.entity.Product>",
        ])
        self.assertIn("User", constructor_identifiers)
        self.assertIn("Product", constructor_identifiers)
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
                "import { ReactQueryDevtools } from '@tanstack/react-query-devtools';\n"
                "import local from './local';\n"
            ),
            "Inventory/backend/src/main/java/com/inventory/SecurityConfig.java": (
                "import org.springframework.security.oauth2.server.resource.authentication."
                "JwtGrantedAuthoritiesConverter;\n"
                "class SecurityConfig { void configure() { "
                "JwtGrantedAuthoritiesConverter converter = "
                "new JwtGrantedAuthoritiesConverter(); "
                'converter.setClaimName("roles"); } }\n'
            ),
        }
        _reconcile_java_generation_output(output, "Inventory")
        self.assertNotIn("Inventory/pom.xml", output)
        package = __import__("json").loads(output["Inventory/frontend/package.json"])
        self.assertIn("axios", package["dependencies"])
        self.assertIn("@tanstack/react-query", package["dependencies"])
        self.assertIn("@tanstack/react-query-devtools", package["dependencies"])
        self.assertNotIn(".", package["dependencies"])
        security_config = output[
            "Inventory/backend/src/main/java/com/inventory/SecurityConfig.java"
        ]
        self.assertIn('converter.setAuthoritiesClaimName("roles")', security_config)
        self.assertNotIn("setClaimName", security_config)

    # Function: test_java_reconciliation_flattens_modules_and_repairs_type_ownership
    def test_java_reconciliation_flattens_modules_and_repairs_type_ownership(self):
        output = {
            "Inventory/backend/pom.xml": _backend_manifest_files(
                "java", "Inventory", "Java 21 Spring Boot 3", False, False,
            )["backend/pom.xml"],
            "Inventory/backend/inventory-service/src/main/java/com/inventory/dto/ProductDto.java": (
                "package com.inventory.dto;\npublic record ProductDto(String id) {}\n"
            ),
            "Inventory/backend/src/main/java/com/inventory/domain/Order.java": (
                "package com.inventory.domain;\n"
                "public class Order { public enum OrderStatus { CREATED } }\n"
            ),
            "Inventory/backend/src/main/java/com/modernize/InventoryController.java": (
                "package com.modernize;\n"
                "import com.wrong.api.ProductDto;\n"
                "import com.wrong.OrderStatus;\n"
                "public class InventoryController { "
                "ProductDto product; com.legacy.model.ProductDto qualified; "
                "OrderStatus status; RestTemplate client; }\n"
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
        self.assertIn("com.inventory.dto.ProductDto qualified", controller)
        self.assertIn(
            "import com.inventory.domain.Order.OrderStatus;",
            controller,
        )
        self.assertIn(
            "import org.springframework.web.client.RestTemplate;",
            controller,
        )
        self.assertIn("Inventory/frontend/src/index.css", output)

    def test_explicit_java_modules_are_preserved_as_a_maven_reactor(self):
        output = {
            "Inventory/backend/pom.xml": _backend_manifest_files(
                "java", "Inventory", "Java 21 Spring Boot 3", False, False,
            )["backend/pom.xml"],
            "Inventory/backend/product-service/src/main/java/com/inventory/product/ProductDto.java": (
                "package com.inventory.product;\npublic record ProductDto(Long id) {}\n"
            ),
            "Inventory/backend/order-service/src/main/java/com/inventory/order/OrderService.java": (
                "package com.inventory.order;\n"
                "import com.wrong.ProductDto;\n"
                "public class OrderService { ProductDto product; }\n"
            ),
        }

        _reconcile_java_generation_output(output, "Inventory")

        reactor = output["Inventory/backend/pom.xml"]
        ET.fromstring(reactor)
        self.assertTrue(reactor.startswith("<?xml"))
        self.assertIn("<packaging>pom</packaging>", reactor)
        self.assertIn("<module>order-service</module>", reactor)
        self.assertIn("<module>product-service</module>", reactor)
        self.assertIn("Inventory/backend/order-service/pom.xml", output)
        self.assertIn("Inventory/backend/product-service/pom.xml", output)
        order_path = (
            "Inventory/backend/order-service/src/main/java/"
            "com/inventory/order/OrderService.java"
        )
        self.assertIn(order_path, output)
        self.assertNotIn(
            "Inventory/backend/src/main/java/com/inventory/order/OrderService.java",
            output,
        )
        # Reconciliation must never turn a wire boundary into a Java source
        # dependency on another independently deployable module.
        self.assertIn("import com.wrong.ProductDto;", output[order_path])

    def test_java_reactor_adds_same_module_imports_and_repairs_validation_imports(self):
        output = {
            "Demo/backend/auth-service/src/main/java/com/app/auth/service/AuthService.java": (
                "package com.app.auth.service; public class AuthService {}"
            ),
            "Demo/backend/auth-service/src/main/java/com/app/auth/controller/AuthController.java": (
                "package com.app.auth.controller;\n"
                "public class AuthController { AuthService service; Map<String, Object> result; "
                "@jakarta.validation.DecimalMin(\"0.01\") String amount; }\n"
            ),
            "Demo/backend/order-service/src/main/java/com/app/order/OrderApplication.java": (
                "package com.app.order; public class OrderApplication {}"
            ),
        }

        _reconcile_java_generation_output(output, "Demo")

        controller = output[
            "Demo/backend/auth-service/src/main/java/com/app/auth/controller/AuthController.java"
        ]
        self.assertIn("import com.app.auth.service.AuthService;", controller)
        self.assertIn("import java.util.Map;", controller)
        self.assertIn("jakarta.validation.constraints.DecimalMin", controller)

    def test_java_reactor_closes_service_infra_filter_and_frontend_exports(self):
        output = {
            "Demo/backend/api-gateway/src/main/java/com/app/JwtFilter.java": (
                "package com.app;\nimport org.springframework.stereotype.Component;\n"
                "public class JwtFilter extends Component { "
                "void doFilterInternal() { Claims c = Jwts.parser().build().parseSignedClaims(\"x\").getPayload(); "
                "byte[] key = Base64Utils.decode(EnvironmentVariables.getSecret(\"JWT_SECRET\")); } }\n"
            ),
            "Demo/backend/auth-service/src/main/java/com/app/AuthApplication.java": (
                "package com.app; public class AuthApplication {}\n"
            ),
            "Demo/frontend/package.json": '{"dependencies":{},"devDependencies":{}}',
            "Demo/frontend/src/App.tsx": "import apiClient from './apiClient'; export { apiClient };\n",
            "Demo/frontend/src/apiClient.ts": "export const apiClient = {};\n",
            "Demo/backend/auth-service/src/test/java/com/app/AuthTest.java": (
                "package com.app; class AuthTest { String text = \"bad\u0081text\"; }\n"
            ),
        }

        _reconcile_java_generation_output(output, "Demo")

        for module in ("api-gateway", "auth-service"):
            self.assertIn(f"Demo/backend/{module}/Dockerfile", output)
            self.assertIn(
                f"Demo/backend/{module}/src/main/resources/application.yml", output,
            )
        jwt_filter = output["Demo/backend/api-gateway/src/main/java/com/app/JwtFilter.java"]
        self.assertIn("extends OncePerRequestFilter", jwt_filter)
        self.assertIn("import io.jsonwebtoken.Claims;", jwt_filter)
        self.assertIn("import io.jsonwebtoken.Jwts;", jwt_filter)
        self.assertIn("Base64.getDecoder().decode", jwt_filter)
        gateway_pom = output["Demo/backend/api-gateway/pom.xml"]
        self.assertIn("<artifactId>jjwt-api</artifactId>", gateway_pom)
        self.assertIn("<artifactId>jjwt-impl</artifactId>", gateway_pom)
        self.assertIn("export default apiClient", output["Demo/frontend/src/apiClient.ts"])
        self.assertNotIn("\u0081", output[
            "Demo/backend/auth-service/src/test/java/com/app/AuthTest.java"
        ])

    def test_java_reconciliation_uses_declared_record_and_repository_contracts(self):
        output = {
            "Demo/backend/notification-service/src/main/java/com/app/notification/repository/NotificationRepository.java": (
                "package com.app.notification.repository;\n"
                "import java.util.List; import org.springframework.data.domain.Pageable;\n"
                "public interface NotificationRepository {\n"
                "List<Notification> findByOrderId(Long id, Pageable pageable);\n}\n"
            ),
            "Demo/backend/notification-service/src/main/java/com/app/notification/service/NotificationService.java": (
                "package com.app.notification.service;\n"
                "public class NotificationService { NotificationRepository repository; "
                "Object find(Long id, Pageable p) { return repository.findByOrderId(id, p).getContent(); } }\n"
            ),
            "Demo/backend/product-service/src/main/java/com/app/product/repository/ProductRepository.java": (
                "package com.app.product.repository;\n"
                "import java.util.List; import org.springframework.data.domain.Pageable;\n"
                "public interface ProductRepository {\n"
                "List<Product> findByPriceBetween(Double min, Double max, Pageable pageable);\n}\n"
            ),
            "Demo/backend/product-service/src/main/java/com/app/product/dto/InventoryStatusResponse.java": (
                "package com.app.product.dto;\n"
                "public record InventoryStatusResponse(Long id, String name) {}\n"
            ),
            "Demo/backend/product-service/src/main/java/com/app/product/service/ProductService.java": (
                "package com.app.product.service;\n"
                "public class ProductService { ProductRepository repository; "
                "Object status(Long id) { return InventoryStatusResponse.of(id, \"item\"); } "
                "Object range() { return repository.findByPriceBetween(1.0, 2.0); } }\n"
            ),
        }

        _reconcile_java_generation_output(output, "Demo")

        notification = output[
            "Demo/backend/notification-service/src/main/java/com/app/notification/service/NotificationService.java"
        ]
        product = output[
            "Demo/backend/product-service/src/main/java/com/app/product/service/ProductService.java"
        ]
        self.assertNotIn(".getContent()", notification)
        self.assertIn('new InventoryStatusResponse(id, "item")', product)
        self.assertIn("findByPriceBetween(1.0, 2.0, Pageable.unpaged())", product)
        self.assertIn("import org.springframework.data.domain.Pageable;", product)

    def test_java_test_validator_does_not_treat_test_fixtures_as_field_injection(self):
        result = validate_file(
            "Demo/backend/auth-service/src/test/java/com/app/AuthControllerTest.java",
            """package com.app;
import static org.assertj.core.api.Assertions.assertThat;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
@WebMvcTest class AuthControllerTest {
  @Autowired private Object mockMvc;
  void check() { assertThat(mockMvc).isNotNull(); }
}
""",
            "java",
        )
        self.assertTrue(result.passed, result.diagnostics)

    def test_java_build_repair_rolls_back_a_worse_compiler_state(self):
        path = "Demo/backend/src/main/java/com/app/Broken.java"
        original = "package com.app; public class Broken { Missing value; }\n"
        output = {path: original}
        initial = BuildResult(False, "maven", {path: ["cannot find symbol"]})
        worse = BuildResult(False, "maven", {path: ["reached end of file while parsing"]})
        accepted = BuildResult(True, "maven", {})

        def corrupt(_fixable, _round, _maximum, files, *_args, **_kwargs):
            files[path] = "package com.app; public class Broken {\n"

        with patch("services.build_runner.run_build", side_effect=[initial, worse, accepted]), \
                patch(
                    "services.modernizer.prompt_pipeline._pf_repair_build_round",
                    side_effect=corrupt,
                ):
            result = _pf_run_build_and_repair(
                output, "Demo", "java", False, "project", "", "", "model", "postgres",
                "system", lambda *_args: None,
            )

        self.assertTrue(result.passed)
        self.assertEqual(original, output[path])

    def test_java_fullstack_attributes_esbuild_syntax_error_to_source(self):
        path = "Demo/frontend/store/authStore.ts"
        result = BuildResult(
            False,
            "maven+npm-build",
            {"<build>": ["vite failed"]},
            "C:/Windows/Temp/build/Demo/frontend/store/authStore.ts:51:41\n"
            'Expected ")" but found "=>"\n',
        )

        _pf_attribute_java_frontend_build_errors(result, {path: "broken"})

        self.assertNotIn("<build>", result.errors_by_file)
        self.assertIn(path, result.errors_by_file)
        self.assertIn("Expected", result.errors_by_file[path][0])

    def test_java_build_repair_recloses_new_project_references(self):
        service_path = "Demo/backend/auth-service/src/main/java/com/app/auth/service/AuthService.java"
        exception_path = (
            "Demo/backend/auth-service/src/main/java/com/app/auth/exception/"
            "InvalidCredentialsException.java"
        )
        output = {
            service_path: (
                "package com.app.auth.service;\n"
                "import com.app.auth.exception.InvalidCredentialsException;\n"
                "public class AuthService { InvalidCredentialsException error; }\n"
            ),
            "Demo/backend/product-service/src/main/java/com/app/product/ProductApplication.java": (
                "package com.app.product; public class ProductApplication {}\n"
            ),
        }
        initial = BuildResult(False, "maven", {service_path: [
            "package com.app.auth.exception does not exist"
        ]})
        passed = BuildResult(True, "maven", {})

        def generate_closure(files, *_args, exclude_paths=None, **_kwargs):
            for path in set(files).difference(exclude_paths or set()):
                if path.endswith("InvalidCredentialsException.java"):
                    files[path] = (
                        "package com.app.auth.exception;\n"
                        "public class InvalidCredentialsException extends RuntimeException {}\n"
                    )

        with patch("services.build_runner.run_build", side_effect=[initial, passed]), \
                patch("services.modernizer.prompt_pipeline._pf_repair_build_round"), \
                patch(
                    "services.modernizer.domain_generators.dispatch._ollama_generate_all_sources",
                    side_effect=generate_closure,
                ):
            result = _pf_run_build_and_repair(
                output, "Demo", "java", False, "project", "", "", "model", "postgres",
                "system", lambda *_args: None,
                target={"name": "Spring Boot", "language": "java"},
            )

        self.assertTrue(result.passed, result.errors_by_file)
        self.assertIn(exception_path, output)

    # Function: test_java_reconciliation_reasserts_canonical_pom
    def test_java_reconciliation_reasserts_canonical_pom(self):
        output = {
            "Inventory/backend/pom.xml": (
                "<project><properties><java.version>17</java.version></properties>"
                "<modules><module>src/main/java</module></modules></project>"
            ),
        }
        _reconcile_java_generation_output(output, "Inventory")
        pom = output["Inventory/backend/pom.xml"]
        self.assertIn("<java.version>17</java.version>", pom)
        self.assertIn("spring-cloud-starter-openfeign", pom)
        self.assertNotIn("<modules>", pom)

    def test_java_reconciliation_closes_import_dependencies_and_source_contracts(self):
        output = {
            "Inventory/backend/src/main/java/com/modernize/WrongName.java": (
                "package com.modernize;\n"
                "import javax.validation.Valid;\n"
                "import org.springframework.web.reactive.function.client.WebClient;\n"
                "import io.github.resilience4j.retry.annotation.Retry;\n"
                "import com.google.protobuf.Message;\n"
                "import software.amazon.awssdk.services.dynamodb.DynamoDbClient;\n"
                "public class IntegrationGateway { "
                "@Valid WebClient web; Retry retry; Message message; DynamoDbClient dynamo; }\n"
            ),
        }
        _reconcile_java_generation_output(output, "Inventory")
        source_path = (
            "Inventory/backend/src/main/java/com/modernize/IntegrationGateway.java"
        )
        self.assertIn(source_path, output)
        self.assertNotIn(
            "Inventory/backend/src/main/java/com/modernize/WrongName.java",
            output,
        )
        self.assertIn("import jakarta.validation.Valid;", output[source_path])
        pom = output["Inventory/backend/pom.xml"]
        self.assertTrue(pom.startswith("<?xml"), repr(pom[:30]))
        ET.fromstring(pom)
        self.assertIn("spring-boot-starter-webflux", pom)
        self.assertIn("resilience4j-spring-boot3", pom)
        self.assertIn("protobuf-java", pom)
        self.assertIn("<artifactId>dynamodb</artifactId>", pom)

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
