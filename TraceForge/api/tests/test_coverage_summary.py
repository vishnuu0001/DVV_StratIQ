import json
import uuid
from types import SimpleNamespace

from traceforge.routers.coverage import build_coverage_summary


def _requirement(*, level="FUNCTIONAL", acceptance_criteria=None):
    return SimpleNamespace(
        id=uuid.uuid4(), req_id="REQ-0001", title="Source-backed outcome",
        statement="The system shall retain the source-backed outcome.", level=level,
        acceptance_criteria=acceptance_criteria if acceptance_criteria is not None else ["The outcome is retained."],
    )


def _case(requirement, test_type, index, *, automation_status="AUTOMATION_BLOCKED"):
    metadata = {
        "automation_status": automation_status,
        "automation_blockers": ["Application bindings are not supplied"],
        "acceptance_criteria_mapped": [1] if index == 1 else [],
    }
    return SimpleNamespace(
        id=uuid.uuid4(), requirement_id=requirement.id,
        tc_id=f"TC-{index:04d}", title=f"{test_type} scenario {index}",
        test_type=test_type, test_level="UI_E2E", status="DRAFT",
        steps=[{"expected_result": "The outcome is retained."}],
        gherkin=json.dumps(metadata), content_hash=f"{index:064x}",
    )


def test_blocked_automation_does_not_erase_requirement_test_coverage():
    requirement = _requirement()
    information_gap = _requirement(level="ASSUMPTION", acceptance_criteria=[])
    information_gap.req_id = "REQ-0002"
    cases = (
        [_case(requirement, "POSITIVE", index) for index in range(1, 4)]
        + [_case(requirement, "NEGATIVE", index) for index in range(4, 6)]
        + [_case(requirement, "EDGE", 6)]
    )

    summary = build_coverage_summary([requirement, information_gap], cases, [])

    assert summary["total_requirements"] == 2
    assert summary["executable_requirements"] == 1
    assert summary["information_gap_requirements"] == 1
    assert summary["test_design_coverage_pct"] == 50.0
    assert summary["executable_test_design_coverage_pct"] == 100.0
    assert summary["automation_ready_test_cases"] == 0
    assert summary["automation_blocked_test_cases"] == 6
    assert summary["script_coverage_status"] == "NOT_APPLICABLE"
    assert summary["requirements"][0]["test_status"] == "TEST_DESIGNED"
    assert summary["requirements"][0]["automation_status"] == "AUTOMATION_BLOCKED"
    assert summary["requirements"][1]["test_status"] == "INFORMATION_GAP"
    assert summary["requirements"][1]["automation_status"] == "NOT_APPLICABLE"


def test_enriched_assumption_is_executable_and_not_excluded():
    enriched = _requirement(level="ASSUMPTION", acceptance_criteria=["The confirmed outcome is retained."])
    cases = [_case(enriched, "POSITIVE", 1)]

    summary = build_coverage_summary([enriched], cases, [])

    assert summary["executable_requirements"] == 1
    assert summary["information_gap_requirements"] == 0
    assert summary["requirements"][0]["testable"] is True


def test_source_driven_coverage_does_not_invent_negative_or_edge_obligations():
    requirement = _requirement()
    positive_case = _case(requirement, "POSITIVE", 1)

    summary = build_coverage_summary([requirement], [positive_case], [])

    assert summary["covered_requirements"] == 1
    assert summary["test_design_coverage_pct"] == 100.0
    assert summary["requirements"][0]["policy_gaps"] == []


def test_superseded_requirement_is_excluded_from_coverage_baseline():
    active = _requirement()
    active.status = "APPROVED"
    superseded = _requirement()
    superseded.req_id = "REQ-0002"
    superseded.status = "SUPERSEDED"
    cases = (
        [_case(active, "POSITIVE", index) for index in range(1, 4)]
        + [_case(active, "NEGATIVE", index) for index in range(4, 6)]
        + [_case(active, "EDGE", 6)]
    )

    summary = build_coverage_summary([active, superseded], cases, [])

    assert summary["total_requirements"] == 1
    assert summary["covered_requirements"] == 1
    assert summary["test_design_coverage_pct"] == 100.0
    assert [row["req_id"] for row in summary["requirements"]] == ["REQ-0001"]


def test_valid_current_script_counts_only_against_automation_ready_case():
    requirement = _requirement()
    cases = (
        [_case(requirement, "POSITIVE", index) for index in range(1, 4)]
        + [_case(requirement, "NEGATIVE", index) for index in range(4, 6)]
        + [_case(requirement, "EDGE", 6)]
    )
    ready_case = cases[0]
    ready_case.gherkin = json.dumps({
        "automation_status": "READY_FOR_UI_AUTOMATION",
        "acceptance_criteria_mapped": [1],
        "automation_context": {
            "base_url": "https://test.invalid", "auth": {"storage_state": "auth.json"},
            "locators": {"submit": "submit-button"}, "assertions": {"result": "visible"},
            "test_data_factory": {"factory": "createOutcome"}, "cleanup": {"factory": "deleteOutcome"},
        },
    })
    script = SimpleNamespace(
        test_case_id=ready_case.id, status="APPROVED", upstream_tc_hash=ready_case.content_hash,
    )

    summary = build_coverage_summary([requirement], cases, [script])

    assert summary["test_design_coverage_pct"] == 100.0
    assert summary["automation_ready_test_cases"] == 1
    assert summary["scripted_ready_test_cases"] == 1
    assert summary["script_coverage_pct"] == 100.0
    assert summary["requirements"][0]["automation_status"] == "SCRIPTED"
