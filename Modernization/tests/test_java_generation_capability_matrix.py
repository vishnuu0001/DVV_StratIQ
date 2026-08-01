import unittest
import xml.etree.ElementTree as ET

from services.modernizer.build_artifacts import (
    _backend_manifest_files,
    _reconcile_java_generation_output,
)
from services.modernizer.domain_generators.stack_signals import _detect_stack_signals
from services.modernizer.prompt_pipeline import _pf_generate_infra_scaffold, _pf_resolve_target
from services.modernizer.scaffolds.java import _gen_java_scaffold


class JavaGenerationCapabilityMatrixTests(unittest.TestCase):
    def _pom(self, framework: str, database: str) -> str:
        pom = _backend_manifest_files(
            "java", "CapabilityApp", f"Java 21 {framework}", False, False,
            db_target=database,
        )["backend/pom.xml"]
        ET.fromstring(pom)
        return pom

    def test_framework_and_database_dependency_matrix(self):
        spring_postgres = self._pom("Spring Boot 3", "postgres")
        self.assertIn("spring-boot-starter-parent", spring_postgres)
        self.assertIn("spring-boot-starter-data-jpa", spring_postgres)
        self.assertIn("flyway-database-postgresql", spring_postgres)
        self.assertIn("<artifactId>postgresql</artifactId>", spring_postgres)

        spring_mongo = self._pom("Spring Boot 3", "mongodb")
        self.assertIn("spring-boot-starter-data-mongodb", spring_mongo)
        self.assertNotIn("spring-boot-starter-data-jpa", spring_mongo)
        self.assertNotIn("<artifactId>postgresql</artifactId>", spring_mongo)
        self.assertNotIn("spring-ai-bom", spring_mongo)

        spring_mongo_vector = self._pom("Spring Boot 3 + Spring AI", "mongodb-vector")
        self.assertIn("spring-boot-starter-data-mongodb", spring_mongo_vector)
        self.assertIn("spring-ai-starter-vector-store-mongodb-atlas", spring_mongo_vector)

        spring_vector = self._pom("Spring Boot 3 + Spring AI", "pgvector")
        self.assertIn("spring-ai-bom", spring_vector)
        self.assertIn("spring-ai-starter-vector-store-pgvector", spring_vector)

        quarkus_mysql = self._pom("Quarkus", "mysql")
        self.assertIn("quarkus-bom", quarkus_mysql)
        self.assertIn("quarkus-jdbc-mysql", quarkus_mysql)
        self.assertNotIn("spring-boot-starter-parent", quarkus_mysql)

        micronaut_oracle = self._pom("Micronaut", "oracle")
        self.assertIn("micronaut-parent", micronaut_oracle)
        self.assertIn("ojdbc11", micronaut_oracle)
        self.assertNotIn("spring-boot-starter-parent", micronaut_oracle)

        jakarta_db2 = self._pom("Jakarta EE 10", "db2")
        self.assertIn("jakarta.jakartaee-api", jakarta_db2)
        self.assertIn("<packaging>war</packaging>", jakarta_db2)
        self.assertIn("<artifactId>jcc</artifactId>", jakarta_db2)

    def test_stack_signal_matrix_is_machine_readable(self):
        cases = {
            "Quarkus service on OpenShift with Oracle": ("quarkus", "oracle", "kubernetes"),
            "legacy Java EE application backed by DB2": ("jakarta", "db2", None),
            "Spring Boot RAG API using PGVector on EKS": ("spring", "pgvector", "kubernetes"),
            "Micronaut API using MongoDB in Docker": ("micronaut", "mongodb", "container"),
        }
        for prompt, expected in cases.items():
            with self.subTest(prompt=prompt):
                signals = _detect_stack_signals(prompt)
                self.assertEqual(expected, (
                    signals["java_framework"], signals["db_target"],
                    signals["deployment_kind"],
                ))

    def test_reconciliation_preserves_non_spring_framework(self):
        output = {
            "Demo/backend/src/main/java/com/app/GreetingResource.java": (
                "import jakarta.ws.rs.GET; import io.quarkus.runtime.Quarkus; class GreetingResource {}"
            ),
        }
        _reconcile_java_generation_output(
            output, "Demo", {"backend_tech": "Quarkus", "db_target": "mysql"},
        )
        pom = output["Demo/backend/pom.xml"]
        self.assertIn("quarkus-jdbc-mysql", pom)
        self.assertNotIn("spring-boot-starter-parent", pom)

    def test_fallback_scaffold_uses_shared_capability_resolver(self):
        output = {}
        _gen_java_scaffold(output, "Demo", "Orders", [], "Quarkus", "mysql")
        pom = output["ModernizedApp/services/orders-service/pom.xml"]
        self.assertIn("quarkus-jdbc-mysql", pom)
        self.assertNotIn("<artifactId>postgresql</artifactId>", pom)

        mongo_output = {}
        _gen_java_scaffold(mongo_output, "Demo", "Catalog", [], "Spring Boot 3", "mongodb")
        mongo_root = "ModernizedApp/services/catalog-service"
        self.assertIn("spring-boot-starter-data-mongodb", mongo_output[f"{mongo_root}/pom.xml"])
        self.assertIn("MongoRepository", next(
            content for path, content in mongo_output.items() if path.endswith("CatalogRepository.java")
        ))
        self.assertIn("MONGODB_URI", mongo_output[f"{mongo_root}/src/main/resources/application.yml"])

        micronaut_output = {}
        _gen_java_scaffold(micronaut_output, "Demo", "Billing", [], "Micronaut", "oracle")
        self.assertIn("Dialect.ORACLE", next(
            content for path, content in micronaut_output.items() if path.endswith("BillingRepository.java")
        ))

    def test_kubernetes_is_generated_only_for_kubernetes_targets(self):
        def generated(signals):
            files = {}
            _pf_generate_infra_scaffold(
                "java", signals, "Demo", True, False, files.__setitem__,
                lambda *_: None,
            )
            return files

        docker_files = generated({"deployment_kind": "container", "deploy": "Docker"})
        self.assertIn("Demo/docker-compose.yml", docker_files)
        self.assertFalse(any("k8s/" in path for path in docker_files))

        k8s_files = generated({"deployment_kind": "kubernetes", "deploy": "Kubernetes"})
        self.assertTrue(any("k8s/" in path for path in k8s_files))

    def test_java_microservices_preset_carries_platform_capability(self):
        target, signals, _, language, _ = _pf_resolve_target(
            "Generate an order platform", "java_microservices", "",
        )
        self.assertEqual("java", language)
        self.assertEqual("kubernetes", signals["deployment_kind"])
        self.assertEqual("postgres", target["db_target"])

    def test_reactor_gateway_is_reactive_and_does_not_invent_eureka(self):
        project = "Demo"
        base = f"{project}/backend/api-gateway/src/main/java/com/app/gateway"
        output = {
            f"{base}/GatewayApplication.java": (
                "package com.app.gateway;\nimport org.springframework.cloud.client.discovery.EnableDiscoveryClient;\n"
                "@EnableDiscoveryClient public class GatewayApplication {}\n"
            ),
            f"{base}/config/GatewayConfig.java": (
                "package com.app.gateway.config;\n"
                "import org.springframework.context.annotation.Bean;\n"
                "import org.springframework.security.config.annotation.web.reactive.EnableWebFluxSecurity;\n"
                "import org.springframework.security.web.server.SecurityWebFilterChain;\n"
                "@EnableWebFluxSecurity public class GatewayConfig {\n"
                "@Bean public SecurityWebFilterChain chain(SecurityWebFilterChain chain) { return chain; }\n}\n"
            ),
            f"{project}/backend/auth-service/src/main/java/com/app/auth/AuthApplication.java": (
                "package com.app.auth; public class AuthApplication {}"
            ),
        }
        _reconcile_java_generation_output(output, project, {
            "backend_tech": "Java 21 Spring Cloud Gateway; AWS Service Connect; No Eureka",
            "db_target": "postgres",
        })
        pom = output[f"{project}/backend/api-gateway/pom.xml"]
        self.assertIn("spring-cloud-starter-gateway", pom)
        self.assertIn("spring-boot-starter-webflux", pom)
        self.assertNotIn("spring-boot-starter-web</artifactId>", pom)
        self.assertNotIn("EnableDiscoveryClient", output[f"{base}/GatewayApplication.java"])

    def test_java_closure_removes_framework_shadow_and_aligns_records(self):
        project = "Demo"
        root = f"{project}/backend/order-service/src/main/java/com/app/order"
        output = {
            f"{root}/service/LoggerFactory.java": "package com.app.order.service; public class LoggerFactory {}",
            f"{root}/dto/ItemRequest.java": "package com.app.order.dto; public record ItemRequest(Long productId, int quantity) {}",
            f"{root}/dto/ItemView.java": "package com.app.order.dto; public record ItemView(Long productId, int quantity) {}",
            f"{root}/service/OrderService.java": (
                "package com.app.order.service; import com.app.order.service.LoggerFactory; "
                "import com.app.order.dto.*; import java.util.List; class OrderService { "
                "void run(List<ItemRequest> items) { for (ItemRequest item : items) { int q=item.getQuantity(); } } "
                "ItemView view(ItemRequest item) { return new ItemView().setProductId(item.productId()).setQuantity(item.quantity()); }}"
            ),
        }
        _reconcile_java_generation_output(output, project, {"backend_tech": "Spring Boot", "db_target": "postgres"})
        self.assertFalse(any(path.endswith("LoggerFactory.java") for path in output))
        service = next(value for path, value in output.items() if path.endswith("OrderService.java"))
        self.assertIn("item.quantity()", service)
        item_view = next(value for path, value in output.items() if path.endswith("ItemView.java"))
        self.assertIn("class ItemView", item_view)
        self.assertIn("ItemView setQuantity", item_view)
        self.assertNotIn("com.app.order.service.LoggerFactory", service)

    def test_java_closure_repairs_truncated_test_and_jsx_extension(self):
        project = "Demo"
        output = {
            f"{project}/backend/app/src/test/java/com/app/AppTest.java": (
                "package com.app; class AppTest { @Test void good() {} "
                "@Test void truncated() { call("
            ),
            f"{project}/frontend/src/hooks/useAuth.ts": (
                "export function Page() { return (<div>ready</div>); }"
            ),
        }
        _reconcile_java_generation_output(output, project, {"backend_tech": "Spring Boot", "db_target": "postgres"})
        test = next(value for path, value in output.items() if path.endswith("AppTest.java"))
        self.assertNotIn("truncated", test)
        self.assertEqual(test.count("{"), test.count("}"))
        self.assertIn(f"{project}/frontend/src/hooks/useAuth.tsx", output)
        self.assertNotIn(f"{project}/frontend/src/hooks/useAuth.ts", output)


if __name__ == "__main__":
    unittest.main()
