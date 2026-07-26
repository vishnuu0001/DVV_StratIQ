# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Modernization — tests (test_governance_integrity.py)
# Date: 2025-09-24
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# Scope: Evidence-backed governance plan and honest contract checks
# ---------------------------------------------------------------------------
import unittest

from services.governance import generate_plan, validate_contracts


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


if __name__ == "__main__":
    unittest.main()
