# ---------------------------------------------------------------------------
# Author: GitHub Copilot
# Scope: TraceForge — test designer hardening regressions
# Date: 2026-07-28
# ---------------------------------------------------------------------------
from __future__ import annotations

import json
import uuid
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
    _scenario_semantic_key,
    semantic_duplicate_test_case_groups,
    _requirements_without_test_cases,
    _sanitise_optional_metadata,
    _scenario_semantic_issues,
    _test_case_source_issues,
    repair_stored_execution_details,
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
    assert "source-grounded manual action" in prompt
    assert "never replace the business action with a blocker placeholder" in prompt
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
    assert "EXECUTION DETAIL BLOCKED" not in rendered
    assert "PENDING BUSINESS CONFIRMATION" not in rendered
    assert all(step.get("binding_status") == "SOURCE_READY" for step in cases[0].steps)
    assert cases[0].automation_status == "MANUAL_ONLY"


def test_fallback_negative_case_uses_source_rule_without_pending_outcomes():
    requirement = SimpleNamespace(
        req_id="REQ-19", title="BIO-Burden testing before shipment",
        statement="BIO-Burden testing must take 7-10 days before shipment.",
        acceptance_criteria=["BIO-Burden testing takes 7-10 days before shipment."],
        level="BUSINESS", priority="MUST",
    )
    cases = []

    _repair_missing_scenarios(requirement, cases, [("NEGATIVE", 1)])

    rendered = str(cases[0].steps)
    assert "7-10 days before shipment" in rendered
    assert "EXECUTION DETAIL BLOCKED" not in rendered
    assert "PENDING BUSINESS CONFIRMATION" not in rendered
    assert "violates the source-defined rule" in rendered


def test_fallback_does_not_invent_numbered_duplicates_to_meet_a_quota():
    requirement = SimpleNamespace(
        req_id="REQ-20", title="Quality release before shipment",
        statement="Material cannot ship until formal Quality Release is issued.",
        acceptance_criteria=["Material cannot ship until formal Quality Release is issued."],
        level="BUSINESS", priority="MUST",
    )
    cases = []

    repaired = _repair_missing_scenarios(requirement, cases, [("NEGATIVE", 3)])

    assert repaired == 1
    assert len(cases) == 1
    assert len({_scenario_semantic_key(case) for case in cases}) == 1


def test_persisted_duplicate_grouper_ignores_title_and_sequence_number():
    requirement_id = uuid.uuid4()
    steps = [{
        "step_no": 1,
        "action": "Attempt shipment before Quality Release.",
        "expected_result": "Shipment is blocked.",
        "test_data": "Material awaiting Quality Release",
    }]
    cases = [
        SimpleNamespace(
            tc_id=f"TC-000{index}", requirement_id=requirement_id,
            title=f"Scenario {index}", test_type="NEGATIVE" if index < 3 else "POSITIVE",
            gherkin="{}", preconditions=[], steps=steps,
        )
        for index in range(1, 4)
    ]

    groups = semantic_duplicate_test_case_groups(cases)

    assert [[case.tc_id for case in group] for group in groups] == [
        ["TC-0001", "TC-0002", "TC-0003"],
    ]


def test_execution_normalization_preserves_mapped_criterion():
    requirement = SimpleNamespace(
        req_id="REQ-21", statement="The platform validates an invoice.",
        acceptance_criteria=["A valid invoice is accepted.", "An invalid invoice is rejected."],
    )
    case = ExtractedTestCase(
        title="Reject invalid invoice", test_type="NEGATIVE",
        acceptance_criteria_mapped=[2], source_quote=requirement.statement,
        steps=[{
            "step_no": number, "action": "draft", "expected_result": "draft", "test_data": "draft",
        } for number in range(1, 5)],
    )

    _normalise_unsupported_execution_details(requirement, case)

    rendered = json.dumps(case.steps)
    assert "An invalid invoice is rejected." in rendered
    assert "A valid invoice is accepted." not in rendered


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
    assert all("IMPLEMENTATION BINDING PENDING" not in action for action in actions)
    assert all("PENDING BUSINESS CONFIRMATION" not in step["expected_result"] for step in case.steps)
    assert all(step["binding_status"] == "SOURCE_READY" for step in case.steps)
    assert case.automation_status == "MANUAL_ONLY"
    assert "Return all material back in stock" in actions[0]


def test_stored_blocked_case_repair_is_source_ready_and_idempotent():
    requirement = SimpleNamespace(
        req_id="REQ-20", title="BIO-Burden timing",
        statement="BIO-Burden testing must take 7-10 days before shipment.",
        acceptance_criteria=["BIO-Burden testing takes 7-10 days before shipment."],
    )
    case = SimpleNamespace(
        title="REQ-20 — BIO-Burden timing negative scenario", test_type="NEGATIVE",
        test_level="INTEGRATION", priority="P1", preconditions=[], version=1,
        steps=[{
            "step_no": 1,
            "action": "[EXECUTION DETAIL BLOCKED — transaction is unknown]",
            "expected_result": "[PENDING BUSINESS CONFIRMATION — result is unknown]",
        }],
        gherkin=json.dumps({"automation_status": "AUTOMATION_BLOCKED"}),
        content_hash="old",
    )

    assert repair_stored_execution_details(requirement, case) is True
    assert repair_stored_execution_details(requirement, case) is False
    assert case.version == 2
    assert "EXECUTION DETAIL BLOCKED" not in str(case.steps)
    assert "PENDING BUSINESS CONFIRMATION" not in str(case.steps)
    assert json.loads(case.gherkin)["automation_status"] == "MANUAL_ONLY"
    assert case.content_hash != "old"


def test_stored_non_ui_case_repairs_stale_automation_classification():
    requirement = SimpleNamespace(
        req_id="REQ-21", title="Return shipped material",
        statement="Already shipped material must be returned in full.",
        acceptance_criteria=["Already shipped material is returned in full."],
    )
    case = SimpleNamespace(
        title="Return shipped material", test_type="POSITIVE", test_level="UAT",
        priority="P1", preconditions=[], version=1,
        steps=[{
            "step_no": number, "action": requirement.statement,
            "expected_result": requirement.acceptance_criteria[0],
        } for number in range(1, 5)],
        gherkin=json.dumps({"automation_status": "AUTOMATION_BLOCKED", "ambiguities": []}),
        content_hash="old",
    )

    assert repair_stored_execution_details(requirement, case) is True
    assert json.loads(case.gherkin)["automation_status"] == "MANUAL_ONLY"
    assert repair_stored_execution_details(requirement, case) is False


def test_incremental_design_selects_only_requirements_without_cases():
    covered = SimpleNamespace(id=uuid.uuid4(), req_id="REQ-1")
    enriched = SimpleNamespace(id=uuid.uuid4(), req_id="REQ-2")

    selected = _requirements_without_test_cases([covered, enriched], {covered.id})

    assert selected == [enriched]


def test_playwright_emitter_keeps_integration_case_outside_playwright():
    case = SimpleNamespace(test_level="INTEGRATION")
    status, blockers = _verified_automation_status(
        case, {"automation_status": "READY_FOR_UI_AUTOMATION", "automation_context": {}},
    )

    assert status == "MANUAL_ONLY"
    assert blockers == []


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


def test_playwright_emitter_accepts_ui_cases_with_or_without_complete_contract():
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
    manual = SimpleNamespace(test_level="UAT", gherkin='{"automation_status":"MANUAL_ONLY"}')

    assert PlaywrightEmitter().can_handle(ready) is True
    assert PlaywrightEmitter().can_handle(blocked) is True
    assert PlaywrightEmitter().can_handle(manual) is True
