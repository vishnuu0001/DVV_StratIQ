# ---------------------------------------------------------------------------
# Author: GitHub Copilot
# Scope: TraceForge — test designer hardening regressions
# Date: 2026-07-28
# ---------------------------------------------------------------------------
from __future__ import annotations

import json
from types import SimpleNamespace

from traceforge.agents.test_designer import (
    ExtractedTestCase,
    _TC_SYSTEM_PROMPT,
    _build_acceptance_criterion_steps,
    _build_edge_steps,
    _build_negative_steps,
    _build_positive_steps,
    _build_test_case_definitions,
    _enforce_automation_readiness,
    _outline_source_issues,
    _normalise_unsupported_execution_details,
    _repair_missing_scenarios,
    _sanitise_optional_metadata,
    _scenario_semantic_issues,
    _test_case_source_issues,
    ScenarioOutline,
)
from traceforge.agents.script_gen.playwright import PlaywrightEmitter, _verified_automation_status
from traceforge.orchestration.gates import _has_unresolved_business_review


def test_optional_metadata_cannot_introduce_unreferenced_systems_roles_or_cleanup():
    requirement = SimpleNamespace(
        req_id="REQ-1", statement="The service validates the request.",
        acceptance_criteria=["The request is validated."], citations=[],
    )
    case = ExtractedTestCase(
        title="Validate request successfully", objective="Validate the request",
        test_type="POSITIVE", systems_involved=["Invented ERP"],
        required_roles=["Invented Manager"], cleanup_instructions=["Delete ledger posting"],
        automation_context={"base_url": "https://invented.invalid"},
        steps=[
            {"step_no": number, "action": "[EXECUTION DETAIL BLOCKED — action missing]",
             "expected_result": "The request is validated.", "test_data": "The request"}
            for number in range(1, 5)
        ],
    )

    _sanitise_optional_metadata(requirement, case)

    assert case.systems_involved == []
    assert case.required_roles == []
    assert case.cleanup_instructions == []
    assert case.automation_context == {}


def test_positive_success_intent_rejects_only_negative_expected_results():
    case = ExtractedTestCase(
        title="Successful approval", objective="Generate and approve the release successfully",
        test_type="POSITIVE",
        steps=[
            {"step_no": number, "action": "review", "test_data": "source",
             "expected_result": "The release is not approved while the result is pending."}
            for number in range(1, 5)
        ],
    )

    assert _scenario_semantic_issues(case)


# Function: test_prompt_requires_business_flow_and_persistence_detail
async def test_prompt_requires_business_flow_and_persistence_detail():
    prompt = _TC_SYSTEM_PROMPT.lower()

    assert "only authoritative source" in prompt
    assert "never silently resolve contradictions" in prompt
    assert "execution detail blocked" in prompt
    assert "never approved" in prompt
    assert "shared-state safety" in prompt


# Function: test_positive_negative_and_edge_steps_are_business_detailed
async def test_positive_negative_and_edge_steps_are_business_detailed():
    requirement = SimpleNamespace(
        title="Credit limit validation",
        statement="The application shall reject credit requests above 100000.",
        acceptance_criteria=[
            "Requests above 100000 are rejected.",
            "Requests at 100000 are accepted.",
        ],
        ears_parts={"trigger": "Submit request", "precondition": "User is authenticated"},
        priority="MUST",
    )

    positive_steps = _build_positive_steps(requirement, requirement.acceptance_criteria, "Submit request")
    negative_steps = _build_negative_steps(requirement, requirement.acceptance_criteria)
    edge_steps = _build_edge_steps(requirement, requirement.acceptance_criteria, "Submit request")
    acceptance_steps = _build_acceptance_criterion_steps(requirement, requirement.acceptance_criteria[0], 1, negative=True)

    assert len(positive_steps) == 5
    assert len(negative_steps) == 5
    assert len(edge_steps) == 5
    assert len(acceptance_steps) == 5
    assert "audit trail location" in positive_steps[-1]["action"].lower()
    assert "no partial commit" in negative_steps[1]["expected_result"].lower()
    assert "retry" in edge_steps[1]["action"].lower()
    assert "no prohibited state change" in acceptance_steps[4]["expected_result"].lower()


# Function: test_trigger_rules_expand_boundary_security_and_performance_cases
async def test_trigger_rules_expand_boundary_security_and_performance_cases():
    requirement = SimpleNamespace(
        title="Access and limit enforcement",
        statement="The service shall reject values above 10 and restrict tenant access.",
        acceptance_criteria=["Values above 10 are rejected.", "Cross-tenant access is blocked."],
        level="NON_FUNCTIONAL",
        priority="P2",
    )

    definitions = _build_test_case_definitions(requirement, requirement.acceptance_criteria, "Submit")
    types = [definition[0] for definition in definitions]

    assert "BOUNDARY" in types
    assert "NEGATIVE_SECURITY" in types
    assert "PERFORMANCE" in types


def test_ready_label_is_rejected_without_concrete_contract():
    case = ExtractedTestCase(
        title="Create customer order",
        objective="Create an order through the supplied UI",
        test_type="POSITIVE",
        test_level="UI_E2E",
        automation_status="READY_FOR_UI_AUTOMATION",
        steps=[
            {"step_no": number, "action": f"Use reviewed control {number}",
             "expected_result": "Reviewed state is visible", "test_data": "source value"}
            for number in range(1, 5)
        ],
    )

    _enforce_automation_readiness(case)

    assert case.automation_status == "AUTOMATION_BLOCKED"
    assert "locators" in case.automation_blockers[-1]


def test_grounding_rejects_invented_status_and_timing_linkage():
    requirement = SimpleNamespace(
        statement="Return full stock and reverse the invoice.",
        acceptance_criteria=["Full stock is returned.", "The invoice is reversed."],
        citations=[],
    )
    case = ExtractedTestCase(
        title="Full return reconciliation",
        objective="Validate the documented full return",
        test_type="POSITIVE",
        steps=[
            {
                "step_no": number,
                "action": "[EXECUTION DETAIL BLOCKED — transaction metadata not supplied]",
                "expected_result": "Stock returns to available status after the BIO-Burden period.",
                "test_data": "Full stock and invoice",
            }
            for number in range(1, 5)
        ],
    )

    issues = _test_case_source_issues(requirement, case)

    assert any("unsupported fact token" in issue for issue in issues) is False
    assert any("unsupported implementation terms" in issue and "available" in issue for issue in issues)
    assert any("unsupported implementation terms" in issue and "status" in issue for issue in issues)


def test_fallback_preserves_full_source_evidence_and_never_uses_generic_ui_steps():
    requirement = SimpleNamespace(
        req_id="REQ-17", title="Combined production configuration",
        statement="The order contains 16 twin reels and 1 single reel for grade ZX-42.",
        acceptance_criteria=["All 17 reel objects reconcile to the same order."],
        level="BUSINESS", priority="MUST",
    )
    cases = []

    _repair_missing_scenarios(requirement, cases, [("POSITIVE", 1)])

    rendered = str(cases[0].steps)
    assert "16 twin reels and 1 single reel" in rendered
    assert "ZX-42" in rendered
    assert "Observe the UI response" not in rendered
    assert "Reload the record" not in rendered


def test_missing_application_bindings_do_not_erase_business_actions():
    requirement = SimpleNamespace(
        req_id="REQ-18", title="Return complete shipment",
        statement="The system shall return all material back in stock.",
        acceptance_criteria=["Return all material back in stock"], citations=[],
    )
    case = ExtractedTestCase(
        title="Return all shipped material", objective="Return all material",
        test_type="POSITIVE", source_quote="Return all material back in stock",
        steps=[
            {"step_no": number, "action": "draft", "expected_result": "draft", "test_data": "draft"}
            for number in range(1, 5)
        ],
    )

    _normalise_unsupported_execution_details(requirement, case)

    actions = [step["action"] for step in case.steps]
    assert len(set(actions)) == 4
    assert all("IMPLEMENTATION BINDING PENDING" in action for action in actions)
    assert all(step["binding_status"] == "PENDING" for step in case.steps)
    assert "Return all material back in stock" in actions[0]


def test_playwright_emitter_blocks_non_ui_case_without_hybrid_contract():
    case = SimpleNamespace(test_level="INTEGRATION")
    status, blockers = _verified_automation_status(
        case, {"automation_status": "READY_FOR_UI_AUTOMATION", "automation_context": {}},
    )

    assert status == "AUTOMATION_BLOCKED"
    assert "matching API/integration runner" in blockers[0]


def test_unresolved_ambiguity_prevents_test_case_approval():
    unresolved = SimpleNamespace(gherkin='{"ambiguities":["Confirm source unit"],"assumptions":[]}')
    reviewed = SimpleNamespace(gherkin='{"ambiguities":[],"assumptions":[]}')

    assert _has_unresolved_business_review(unresolved) is True
    assert _has_unresolved_business_review(reviewed) is False


def test_required_quantity_is_not_reinterpreted_as_maximum_boundary():
    requirement = SimpleNamespace(
        statement="Produce exactly 16 paired items and 1 single item.",
        acceptance_criteria=[], citations=[],
    )
    outline = ScenarioOutline(
        title="Maximum allowed paired items",
        test_type="EDGE",
        objective="Validate maximum of 16",
        test_data="16 items",
        source_quote="Produce exactly 16 paired items and 1 single item.",
    )

    assert any("unsupported boundary" in issue for issue in _outline_source_issues(requirement, outline))


def test_outline_rejects_invented_numbers_and_currency():
    requirement = SimpleNamespace(
        statement="Maintain the certified balance in source-confirmed units.",
        acceptance_criteria=[], citations=[],
    )
    outline = ScenarioOutline(
        title="Maintain certified balance",
        test_type="POSITIVE",
        objective="Allocate $10000 from the balance",
        test_data="Truck 12345",
        source_quote="Maintain the certified balance in source-confirmed units.",
    )

    issues = _outline_source_issues(requirement, outline)
    assert any("numeric values" in issue for issue in issues)
    assert any("monetary unit" in issue for issue in issues)


def test_playwright_emitter_accepts_only_complete_reviewed_ui_contract():
    complete = {
        "automation_status": "READY_FOR_UI_AUTOMATION",
        "automation_context": {
            "base_url": "https://test.invalid", "auth": {"storage_state": "role.json"},
            "locators": {"Submit": "[data-testid=submit]"},
            "assertions": {"Saved": "[data-testid=status]"},
            "test_data_factory": {"endpoint": "/setup"}, "cleanup": {"endpoint": "/cleanup"},
        },
    }
    ready = SimpleNamespace(test_level="UI_E2E", gherkin=json.dumps(complete))
    blocked = SimpleNamespace(test_level="UI_E2E", gherkin='{"automation_status":"READY_FOR_UI_AUTOMATION"}')

    assert PlaywrightEmitter().can_handle(ready) is True
    assert PlaywrightEmitter().can_handle(blocked) is False
