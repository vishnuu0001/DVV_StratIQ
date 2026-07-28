# ---------------------------------------------------------------------------
# Author: GitHub Copilot
# Scope: TraceForge — test designer hardening regressions
# Date: 2026-07-28
# ---------------------------------------------------------------------------
from __future__ import annotations

from types import SimpleNamespace

from traceforge.agents.test_designer import (
    _TC_SYSTEM_PROMPT,
    _build_acceptance_criterion_steps,
    _build_edge_steps,
    _build_negative_steps,
    _build_positive_steps,
    _build_test_case_definitions,
)


# Function: test_prompt_requires_business_flow_and_persistence_detail
async def test_prompt_requires_business_flow_and_persistence_detail():
    prompt = _TC_SYSTEM_PROMPT.lower()

    assert "make the matrix read like a real test plan" in prompt
    assert "primary end-to-end flow" in prompt
    assert "alternate valid business flow" in prompt
    assert "persistence/downstream reconciliation" in prompt
    assert "no partial side effects" in prompt


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
    assert "audit history" in positive_steps[-1]["action"].lower()
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
