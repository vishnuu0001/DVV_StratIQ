import json
from types import SimpleNamespace

from traceforge.agents.coverage_policy import DEFAULT_POLICY, check_coverage


def _case(test_type: str):
    return SimpleNamespace(
        test_type=test_type,
        steps=[{"expected_result": "approved outcome"}],
        title=test_type,
        acceptance_criteria_mapped=[],
    )


def _requirement():
    return SimpleNamespace(
        req_id="REQ-0001",
        acceptance_criteria=[],
        level="FUNCTIONAL",
        statement="The approved outcome is retained.",
    )


def test_default_policy_uses_evidence_first_minimums():
    assert DEFAULT_POLICY["min_per_requirement"] == {"POSITIVE": 1}


def test_expanded_policy_accepts_security_negative_toward_negative_minimum():
    cases = (
        [_case("POSITIVE") for _ in range(3)]
        + [_case("NEGATIVE") for _ in range(2)]
        + [_case("NEGATIVE_SECURITY")]
        + [_case("EDGE") for _ in range(2)]
    )
    assert check_coverage(_requirement(), cases) == []


def test_expanded_policy_rejects_one_independent_core_case_per_type():
    gaps = check_coverage(_requirement(), [_case("NEGATIVE"), _case("EDGE")])

    assert any("POSITIVE tests" in gap.description for gap in gaps)
    assert not any("NEGATIVE tests" in gap.description for gap in gaps)
    assert not any("EDGE tests" in gap.description for gap in gaps)


def test_negative_case_is_required_for_every_executable_requirement():
    requirement = _requirement()
    requirement.statement = "The system blocks submission when approval is missing."

    gaps = check_coverage(requirement, [_case("POSITIVE")])

    assert any("NEGATIVE tests" in gap.description for gap in gaps)


def test_edge_case_is_not_required_without_source_evidence():
    gaps = check_coverage(_requirement(), [_case("POSITIVE"), _case("NEGATIVE")])

    assert not any("EDGE tests" in gap.description for gap in gaps)


def test_edge_case_is_required_when_retry_behavior_is_explicit():
    requirement = _requirement()
    requirement.statement = "The system retries an interrupted submission without creating a duplicate."
    cases = (
        [_case("POSITIVE") for _ in range(3)]
        + [_case("NEGATIVE") for _ in range(2)]
        + [_case("NEGATIVE_SECURITY")]
    )

    gaps = check_coverage(requirement, cases)

    assert any("EDGE tests" in gap.description for gap in gaps)


def test_dedicated_ac_policy_rejects_one_case_mapped_to_multiple_criteria():
    requirement = _requirement()
    requirement.acceptance_criteria = ["First approved outcome", "Second approved outcome"]
    cases = [_case("POSITIVE"), _case("NEGATIVE"), _case("EDGE")]
    cases[0].acceptance_criteria_mapped = [1, 2]

    gaps = check_coverage(requirement, cases)

    assert any("AC #1" in gap.description for gap in gaps)
    assert any("AC #2" in gap.description for gap in gaps)


def test_dedicated_ac_policy_accepts_one_distinct_case_per_criterion():
    requirement = _requirement()
    requirement.acceptance_criteria = ["First approved outcome", "Second approved outcome"]
    cases = (
        [_case("POSITIVE") for _ in range(2)]
        + [_case("NEGATIVE")]
        + [_case("NEGATIVE_SECURITY"), _case("EDGE")]
    )
    cases[0].acceptance_criteria_mapped = [1]
    cases[1].acceptance_criteria_mapped = [2]

    assert check_coverage(requirement, cases) == []


def test_dedicated_ac_policy_reads_mapping_from_persisted_metadata():
    requirement = _requirement()
    requirement.acceptance_criteria = ["First approved outcome"]
    cases = (
        [_case("POSITIVE")]
        + [_case("NEGATIVE")]
        + [_case("NEGATIVE_SECURITY")]
        + [_case("EDGE")]
    )
    del cases[0].acceptance_criteria_mapped
    cases[0].gherkin = json.dumps({"acceptance_criteria_mapped": [1]})

    assert check_coverage(requirement, cases) == []
