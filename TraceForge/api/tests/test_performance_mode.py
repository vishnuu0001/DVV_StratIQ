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
from traceforge.agents.script_gen.base import deterministic_script_body
from traceforge.agents.test_designer import _fast_test_level


# Function: test_fast_section_is_grounded_in_requirement_ids
def test_fast_section_is_grounded_in_requirement_ids():
    project = SimpleNamespace(name="ACE")
    requirements = [SimpleNamespace(req_id="REQ-0001", level="BUSINESS", statement="The system shall validate invoices.")]
    spec = SectionSpec("context", "Business Context", "GENERATED", max_words=100, prompt_hint="Business objectives.")

    body = _fast_section_prose(spec, project, requirements)

    assert "REQ-0001" in body
    assert "validate invoices" in body


# Function: test_deterministic_script_body_emits_executable_step
def test_deterministic_script_body_emits_executable_step():
    test_case = SimpleNamespace(steps=[{
        "step_no": 1, "action": "Submit the invoice", "expected_result": "Invoice is accepted", "test_data": "INV-100",
    }])

    body = deterministic_script_body("playwright", test_case)

    assert "Submit the invoice" in body
    assert "Invoice is accepted" in body
    assert "executeReviewedStep(page" in body
    assert "TODO_LOCATOR" not in body


# Function: test_fast_test_level_avoids_embedding_or_llm_lookup
def test_fast_test_level_avoids_embedding_or_llm_lookup():
    requirement = SimpleNamespace(title="API contract", statement="The service shall integrate with billing.", level="FUNCTIONAL")

    assert _fast_test_level(requirement) == "INTEGRATION"
