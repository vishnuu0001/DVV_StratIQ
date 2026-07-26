# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Modernization — tests (test_governance_integrity.py)
# Date: 2025-09-24
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# Scope: Evidence-backed governance plan and honest contract checks
# ---------------------------------------------------------------------------
import unittest
import tempfile
from pathlib import Path

from services.governance import ProjectStore, generate_plan, infer_prompt_requirements, validate_contracts


class GovernanceIntegrityTests(unittest.TestCase):
    # Function: test_plan_exposes_unresolved_operational_decisions
    def test_plan_exposes_unresolved_operational_decisions(self):
        plan = generate_plan(
            {
                "project_type": "legacy",
                "summary": {"architecture": "monolith"},
                "requested_target": {
                    "architecture": None,
                    "deployment": None,
                    "database": "PostgreSQL",
                },
            },
            {
                "hierarchy": {"modules": {"billing": {}}},
                "database_access": [{"file": "billing.sql"}],
                "authentication_authorization_flow": ["OAuth"],
            },
            "Java 21 Spring Boot",
        )
        self.assertFalse(plan["ready_for_approval"])
        self.assertTrue(plan["unresolved_requirements"])
        self.assertIsNone(plan["target_architecture"]["style"])
        self.assertIsNone(plan["deployment_approach"])

    # Function: test_contract_validator_never_claims_unperformed_alignment
    def test_contract_validator_never_claims_unperformed_alignment(self):
        result = validate_contracts({
            "domain_models": ["Account"],
            "interfaces": ["AccountService"],
            "route_definitions": [],
            "database_schema": [],
            "dependency_versions": {},
        })
        self.assertEqual("not_evaluated", result["checks"]["client_api_alignment"])
        self.assertEqual("not_evaluated", result["checks"]["dependency_compatibility"])

    # Function: test_prompt_brief_resolves_explicit_generation_requirements
    def test_prompt_brief_resolves_explicit_generation_requirements(self):
        prompt = (
            "Create a Java 21 Spring Boot 3 order service using an event-driven architecture. "
            "Use PostgreSQL with Spring Data JPA and Flyway. Include OAuth2/JWT authorization "
            "with ADMIN and ORDER_USER roles. Provide Dockerfiles, docker-compose.yml, and "
            "Kubernetes manifests."
        )
        inferred = infer_prompt_requirements(prompt)
        self.assertIn("Event-driven", inferred["architecture"])
        self.assertEqual("PostgreSQL + Spring Data JPA + Flyway", inferred["database"])
        self.assertIn("OAuth2", inferred["authorization"])
        self.assertIn("Kubernetes", inferred["deployment"])

        plan = generate_plan(
            {
                "project_type": "greenfield",
                "project_prompt": prompt,
                "requested_target": {
                    "framework": "Spring Boot 3",
                    "runtime": "Java 21",
                    "architecture": "",
                    "database": "",
                    "deployment": "",
                },
            },
            {"hierarchy": {"modules": {}}, "authentication_authorization_flow": []},
            "java21_spring",
        )
        self.assertTrue(plan["ready_for_approval"], plan["unresolved_requirements"])
        self.assertEqual([], plan["unresolved_requirements"])
        self.assertEqual([], plan["manual_tasks"])
        self.assertIn("JWT bearer validation", plan["security_changes"])

    # Function: test_prompt_project_uses_inferred_facts_and_non_blocking_defaults
    def test_prompt_project_uses_inferred_facts_and_non_blocking_defaults(self):
        prompt = (
            "Create a Full Stack Banking Application with Angular as Frontend and dotnet 10 "
            "as backend, deployed to AKS, using Azure Entra ID B2B. Utilize Dapper as ORM."
        )
        inferred = infer_prompt_requirements(prompt)
        self.assertEqual("Angular", inferred["frontend"])
        self.assertEqual(".NET 10", inferred["runtime"])
        self.assertIn("AKS", inferred["deployment"])
        self.assertIn("Entra ID", " ".join(inferred["authorization"]))
        self.assertIn("Dapper", inferred["database"])

        plan = generate_plan(
            {
                "project_type": "greenfield",
                "project_prompt": prompt,
                "requested_target": {},
            },
            {"hierarchy": {"modules": {}}, "authentication_authorization_flow": []},
            "custom",
        )
        self.assertTrue(plan["ready_for_approval"], plan["unresolved_requirements"])
        self.assertEqual([], plan["unresolved_requirements"])
        self.assertEqual([], plan["manual_tasks"])
        self.assertIn("Angular", plan["target_architecture"]["frontend"])
        self.assertIn("AKS", plan["deployment_approach"])

    # Function: test_delete_project_removes_catalog_and_quarantines_snapshots
    def test_delete_project_removes_catalog_and_quarantines_snapshots(self):
        with tempfile.TemporaryDirectory() as directory:
            store = ProjectStore(Path(directory) / "projects")
            project = store.create_prompt_project(
                "Disposable", "Create a small test project", "admin@example.test",
            )
            result = store.delete_project(project["id"], "admin@example.test")
            self.assertTrue(result["deleted"])
            self.assertEqual([], store.list_projects())
            self.assertFalse((store.root / project["id"]).exists())
            self.assertTrue(any((store.root / ".trash").iterdir()))
            with self.assertRaises(KeyError):
                store.get_project(project["id"])


if __name__ == "__main__":
    unittest.main()
