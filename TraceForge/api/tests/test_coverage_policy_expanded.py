from types import SimpleNamespace

from traceforge.agents.coverage_policy import DEFAULT_POLICY, check_coverage


def _case(test_type: str):
    return SimpleNamespace(test_type=test_type, steps=[{"expected_result": "approved outcome"}], title=test_type)


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


def test_evidence_first_policy_accepts_one_independent_core_case_per_type():
    assert check_coverage(_requirement(), [_case("POSITIVE"), _case("NEGATIVE"), _case("EDGE")]) == []


def test_negative_case_is_required_only_when_requirement_contains_negative_evidence():
    requirement = _requirement()
    requirement.statement = "The system blocks submission when approval is missing."

    gaps = check_coverage(requirement, [_case("POSITIVE")])

    assert any("NEGATIVE tests" in gap.description for gap in gaps)
