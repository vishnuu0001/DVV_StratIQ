import unittest

from services.modernizer.prompt_pipeline import (
    _requirement_coverage_diagnostics,
    _requires_multi_file_project,
)


class RequirementCoverageTests(unittest.TestCase):
    def test_distributed_spring_request_cannot_use_single_file(self):
        prompt = (
            "Build a Spring Boot order API with PostgreSQL and Flyway, publish Kafka events, "
            "use OAuth2 JWT, add tests, Dockerfiles, Kubernetes and GitHub Actions."
        )
        self.assertTrue(_requires_multi_file_project(prompt))

    def test_bootstrap_only_project_fails_original_contract_coverage(self):
        prompt = (
            "Spring Boot REST endpoints with PostgreSQL and Flyway. Publish Kafka events. "
            "Use OAuth2 JWT. Add unit and integration tests, Dockerfile and GitHub Actions."
        )
        output = {
            "Orders/src/main/java/com/modernize/orders/OrderApplication.java": (
                "@SpringBootApplication class OrderApplication {}"
            ),
        }
        diagnostics = _requirement_coverage_diagnostics(output, prompt, "java")
        joined = "\n".join(diagnostics)
        self.assertIn("dependency manifest", joined)
        self.assertIn("REST operations", joined)
        self.assertIn("Flyway", joined)
        self.assertIn("Kafka", joined)
        self.assertIn("OAuth2", joined)
        self.assertIn("test suites", joined)
        self.assertIn("Dockerfile", joined)
        self.assertIn("GitHub Actions", joined)


if __name__ == "__main__":
    unittest.main()
