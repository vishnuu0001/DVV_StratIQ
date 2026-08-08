# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: TraceForge — api/tests (test_performance_mode.py)
# Date: 2026-04-25
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# Scope: TraceForge — optimized deterministic generation paths
# ---------------------------------------------------------------------------
from __future__ import annotations

from types import SimpleNamespace

from traceforge.agents.doc_author import SectionSpec, _fast_section_prose
from traceforge.agents.coverage_policy import check_coverage
from traceforge.agents.script_gen.base import _validate_playwright_body
from traceforge.agents.test_designer import (
    ExtractedTestCase,
    _detect_and_assign_process_area,
    _generate_category_batch,
    _repair_acceptance_coverage,
    _repair_missing_scenarios,
)


# Function: test_fast_section_is_grounded_in_requirement_ids
def test_fast_section_is_grounded_in_requirement_ids():
    project = SimpleNamespace(name="ACE")
    requirements = [SimpleNamespace(req_id="REQ-0001", level="BUSINESS", statement="The system shall validate invoices.")]
    spec = SectionSpec("context", "Business Context", "GENERATED", max_words=100, prompt_hint="Business objectives.")

    body = _fast_section_prose(spec, project, requirements)

    assert "REQ-0001" in body
    assert "validate invoices" in body


# Function: test_playwright_llm_body_requires_reviewed_step_runtime
def test_playwright_llm_body_requires_reviewed_step_runtime():
    safe_body = (
        "await test.step('Submit invoice', async () => {\n"
        "  await executeReviewedStep(page, { action: 'Submit', expected: 'Accepted', "
        "data: 'INV-100', scenario: 'Invoice' });\n"
        "});"
    )

    assert _validate_playwright_body(safe_body, expected_steps=1) == ""
    assert "direct page calls" in _validate_playwright_body(
        safe_body + "\nawait page.click('#invented');", expected_steps=1,
    )
    assert "expected 2" in _validate_playwright_body(safe_body, expected_steps=2)


def test_process_area_detection_returns_business_domain():
    evidence = "The FSC balance is reconciled after outbound dispatch."

    assert _detect_and_assign_process_area(evidence) == "FSC Accounting"


async def test_category_retry_retains_all_scenarios_beyond_minimum(monkeypatch):
    returned_cases = [
        ExtractedTestCase(
            title=f"Distinct positive scenario {index}",
            test_type="POSITIVE",
            steps=[
                {
                    "step_no": step_number,
                    "action": "[EXECUTION DETAIL BLOCKED - source binding required]",
                    "expected_result": "The source-supported outcome is achieved.",
                    "test_data": "Use source-approved data.",
                }
                for step_number in range(1, 5)
            ],
        )
        for index in range(1, 4)
    ]

    async def fake_call_agent_llm(*args, **kwargs):
        return {"test_cases": [{}, {}, {}]}, []

    def fake_validate(*args, **kwargs):
        return returned_cases, []

    monkeypatch.setattr("traceforge.agents.test_designer.call_agent_llm", fake_call_agent_llm)
    monkeypatch.setattr("traceforge.agents.test_designer._validate_test_case_items", fake_validate)

    generated, diagnostics = await _generate_category_batch(
        None,
        None,
        None,
        SimpleNamespace(),
        None,
        system="source-grounded prompt",
        test_type="POSITIVE",
        minimum=1,
        seen_scenarios=set(),
        project_source_evidence="source evidence",
    )

    assert len(generated) == 3
    assert diagnostics == []


def test_acceptance_coverage_repair_uses_approved_criterion():
    requirement = SimpleNamespace(
        req_id="REQ-0002",
        acceptance_criteria=["The UI displays the documented missing-certificate error."],
        level="FUNCTIONAL",
        statement="The system validates the certificate.",
    )
    scenario_types = ("POSITIVE", "POSITIVE", "POSITIVE", "NEGATIVE", "NEGATIVE", "NEGATIVE", "EDGE", "EDGE")
    cases = [
        ExtractedTestCase(
            title=f"Distinct scenario {index}",
            test_type=test_type,
            test_level="UI_E2E",
            steps=[
                {
                    "step_no": step_no,
                    "action": f"Execute checkpoint {step_no}",
                    "expected_result": "The reviewed workflow state is visible.",
                    "test_data": "Use isolated test data.",
                }
                for step_no in range(1, 5)
            ],
        )
        for index, test_type in enumerate(scenario_types, start=1)
    ]

    assert any("AC #1" in gap.description for gap in check_coverage(requirement, cases))
    assert _repair_acceptance_coverage(requirement, cases) == 1
    assert not check_coverage(requirement, cases)
    assert any(
        step["expected_result"] == requirement.acceptance_criteria[0]
        for case in cases
        for step in case.steps
    )


def test_missing_scenario_repair_survives_truncated_ollama_category():
    requirement = SimpleNamespace(
        req_id="REQ-0001",
        title="Verify FSC credit mix",
        acceptance_criteria=["The FSC balance is verified before finalization."],
        level="FUNCTIONAL",
        statement="The system verifies FSC balance.",
        priority="MUST",
    )
    existing_types = ("POSITIVE", "POSITIVE", "POSITIVE", "NEGATIVE", "NEGATIVE")
    cases = [
        ExtractedTestCase(
            title=f"Existing Ollama scenario {index}",
            test_type=test_type,
            test_level="UI_E2E",
            steps=[
                {
                    "step_no": step_no,
                    "action": f"Execute checkpoint {step_no}",
                    "expected_result": "The reviewed workflow state is visible.",
                    "test_data": "Use isolated test data.",
                }
                for step_no in range(1, 5)
            ],
        )
        for index, test_type in enumerate(existing_types, start=1)
    ]

    repaired = _repair_missing_scenarios(
        requirement, cases, [("POSITIVE", 3), ("NEGATIVE", 3), ("EDGE", 2)],
    )

    assert repaired == 3
    assert _repair_acceptance_coverage(requirement, cases) == 1
    assert not check_coverage(requirement, cases)
    assert sum(case.test_type == "EDGE" for case in cases) == 2
