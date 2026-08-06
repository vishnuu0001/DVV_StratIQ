# ---------------------------------------------------------------------------
# Author: GitHub Copilot
# Scope: TraceForge — test designer hardening regressions
# Date: 2026-07-28
# ---------------------------------------------------------------------------
from __future__ import annotations

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
    _repair_missing_scenarios,
)
from traceforge.agents.script_gen.playwright import _verified_automation_status
from traceforge.orchestration.gates import _has_unresolved_business_review


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
