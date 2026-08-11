# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: §5 Agent 3 coverage policy — enforced deterministically before the gate opens, per
# Date: 2026-05-18
# ---------------------------------------------------------------------------
"""§5 Agent 3 coverage policy — enforced deterministically before the gate opens, per
spec: 'If the generated set fails the policy, the orchestrator automatically re-prompts
the agent with the specific gap ... before surfacing to the human. Do not present a
non-compliant set to a reviewer.'"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass

DEFAULT_POLICY = {
    # Evidence-backed coverage policy. Numeric volume targets create duplicate
    # scenarios when a requirement contains fewer independently testable rules.
    # - EDGE and BOUNDARY scenarios for quantitative/temporal limits
    # - SECURITY scenarios for authorization and role enforcement
    # - INTEGRATION scenarios for multi-component workflows and reconciliation
    # - END_TO_END scenarios for full business journeys
    "min_per_requirement": {
        "POSITIVE": 1,
        # Every executable rule also needs a controlled rejection/validation
        # path and a resilience/alternate-flow path.  These are test-design
        # probes, not new business requirements: generated expected outcomes
        # must remain bounded by the cited requirement and acceptance criteria.
        "NEGATIVE": 1,
        "EDGE": 1,
    },
    "acceptance_criteria_coverage": "EVERY_AC_MAPPED_WITH_DEDICATED_SCENARIO",
    "nfr_policy": "PERFORMANCE_OR_BOUNDARY_OR_EXPLICIT_WAIVER",
    "boundary_required_when": "requirement contains a numeric range, limit, quantity, or measurable constraint",
    "security_required_when": "requirement contains authorization, role, permission, or approval keyword",
    "integration_required_when": "requirement mentions inter-system flow, reconciliation, interface, or handoff",
}

_NEGATIVE_EVIDENCE_RE = re.compile(
    r"\b(block(?:ed|s|ing)?|prevent(?:ed|s|ing)?|reject(?:ed|s|ing)?|cannot|must not|"
    r"not allowed|den(?:y|ied)|invalid|imbalance|without|unless|failed?|unauthori[sz]ed|"
    r"returned? in full)\b",
    re.IGNORECASE,
)


def requirement_is_executable(requirement) -> bool:
    """A requirement becomes testable once business-confirmed outcomes exist.

    ASSUMPTION is provenance, not a permanent exclusion from Test Design.
    """
    return bool(getattr(requirement, "acceptance_criteria", None))


def minimum_scenarios_for_requirement(requirement, policy: dict = DEFAULT_POLICY) -> dict[str, int]:
    """Derive comprehensive test scenario requirements based on requirement characteristics.
    
    Analysis strategy:
    - POSITIVE: One baseline scenario; dedicated acceptance-criterion checks add
                independently observable scenarios where the evidence supports them
    - NEGATIVE: One scenario only when rejection/validation evidence is explicit
    - EDGE: +1 when retry, concurrency, interruption, or recovery behavior is explicit
    - BOUNDARY: +1 if requirement mentions numeric ranges, limits, quantities, or time bounds
    - SECURITY: +1 if requirement mentions authorization, roles, permissions, or approval flows
    - INTEGRATION: +1 if requirement mentions inter-system flows, reconciliation, interfaces, or handoffs
    - PERFORMANCE: +1 for non-functional performance requirements
    """
    minima = dict(policy.get("min_per_requirement", {"POSITIVE": 1}))
    evidence = " ".join([
        str(getattr(requirement, "title", "")),
        str(getattr(requirement, "statement", "")),
        *[str(value) for value in (getattr(requirement, "acceptance_criteria", None) or [])],
    ])
    evidence_lower = evidence.lower()
    
    # Explicit evidence can raise a project override, but the default baseline
    # already includes one negative validation probe for every executable rule.
    if _NEGATIVE_EVIDENCE_RE.search(evidence):
        minima["NEGATIVE"] = max(minima.get("NEGATIVE", 0), 1)
    
    # BOUNDARY: numeric ranges, limits, quantities, time bounds
    if _has_numeric_range(evidence):
        minima["BOUNDARY"] = minima.get("BOUNDARY", 0) + 1
    if any(w in evidence_lower for w in ("quantity", "amount", "threshold", "capacity", "duration", "timeout")):
        minima["BOUNDARY"] = minima.get("BOUNDARY", 0) + 1

    # EDGE: only when the source states a retry, concurrency, interruption, or recovery condition.
    if any(w in evidence_lower for w in (
        "retry", "duplicate", "partial", "interrupt", "concurrent", "simultaneous",
        "idempot", "recovery", "timeout",
    )):
        minima["EDGE"] = max(minima.get("EDGE", 0), 1)
    
    # SECURITY: authorization, roles, permissions, approval workflows
    if any(w in evidence_lower for w in ("role", "permission", "authorization", "authorization", "approve", 
                                         "unauthorized", "entitled", "access control", "restricted", "secur")):
        minima["NEGATIVE_SECURITY"] = minima.get("NEGATIVE_SECURITY", 0) + 1
    
    # PERFORMANCE: explicitly for non-functional requirements
    if requirement.level == "NON_FUNCTIONAL" and policy.get("nfr_policy", "PERFORMANCE_OR_BOUNDARY_OR_EXPLICIT_WAIVER") in ("PERFORMANCE_OR_BOUNDARY_OR_EXPLICIT_WAIVER", "PERFORMANCE_OR_EXPLICIT_WAIVER"):
        minima["PERFORMANCE"] = minima.get("PERFORMANCE", 0) + 1
    
    return minima

_NUMERIC_SPAN_RE = re.compile(r"\b\d[\d.]*\s*(?:-|to|and)\s*\d[\d.]*\b", re.IGNORECASE)
_NUMERIC_LIMIT_RE = re.compile(r"\b(?:max|maximum|min|minimum|limit)\b", re.IGNORECASE)


def _has_numeric_range(evidence: str) -> bool:
    return bool(_NUMERIC_SPAN_RE.search(evidence) or _NUMERIC_LIMIT_RE.search(evidence))


@dataclass
class CoverageGap:
    req_id: str
    description: str


def _metadata_value(test_case, key: str, default):
    direct = getattr(test_case, key, None)
    if direct is not None:
        return direct
    raw = getattr(test_case, "gherkin", None)
    if not isinstance(raw, str) or not raw.lstrip().startswith("{"):
        return default
    try:
        return json.loads(raw).get(key, default)
    except (TypeError, ValueError):
        return default


# Function: _ac_is_mapped
def _ac_is_mapped(
    ac_text: str,
    test_cases: list,
    *,
    criterion_number: int,
    dedicated: bool,
) -> bool:
    if dedicated:
        return any(
            _metadata_value(test_case, "acceptance_criteria_mapped", []) == [criterion_number]
            for test_case in test_cases
        )

    ac_lower = ac_text.lower()
    ac_keywords = set(re.findall(r"[a-z]{4,}", ac_lower))
    for tc in test_cases:
        for step in tc.steps or []:
            expected = str(step.get("expected_result", "")).lower()
            if ac_keywords and len(ac_keywords & set(re.findall(r"[a-z]{4,}", expected))) >= max(1, len(ac_keywords) // 3):
                return True
    return False


# Function: _count_test_types
def _count_test_types(test_cases: list) -> dict[str, int]:
    type_counts: dict[str, int] = {}
    for tc in test_cases:
        type_counts[tc.test_type] = type_counts.get(tc.test_type, 0) + 1
        # A security-negative scenario is also a valid negative scenario; retain
        # its specialist type while allowing it to satisfy the broader minimum.
        if tc.test_type == "NEGATIVE_SECURITY":
            type_counts["NEGATIVE"] = type_counts.get("NEGATIVE", 0) + 1
    return type_counts


# Function: _check_min_per_type
def _check_min_per_type(requirement, type_counts: dict, policy: dict) -> list[CoverageGap]:
    gaps: list[CoverageGap] = []
    for test_type, minimum in minimum_scenarios_for_requirement(requirement, policy).items():
        if type_counts.get(test_type, 0) < minimum:
            gaps.append(CoverageGap(
                requirement.req_id,
                f"{requirement.req_id} has {type_counts.get(test_type, 0)} {test_type} tests (requires >={minimum}).",
            ))
    return gaps


# Function: _check_ac_coverage
def _check_ac_coverage(requirement, test_cases: list, policy: dict) -> list[CoverageGap]:
    gaps: list[CoverageGap] = []
    coverage_mode = policy["acceptance_criteria_coverage"]
    if coverage_mode not in {
        "EVERY_AC_MAPPED",
        "EVERY_AC_MAPPED_WITH_DEDICATED_SCENARIO",
    }:
        return gaps
    for i, ac in enumerate(requirement.acceptance_criteria, start=1):
        if not _ac_is_mapped(
            ac,
            test_cases,
            criterion_number=i,
            dedicated=coverage_mode == "EVERY_AC_MAPPED_WITH_DEDICATED_SCENARIO",
        ):
            gaps.append(CoverageGap(requirement.req_id, f"{requirement.req_id} AC #{i} ('{ac[:60]}...') is not mapped to any test case's expected result."))
    return gaps


# Function: _check_nfr_policy
def _check_nfr_policy(requirement, test_cases: list, type_counts: dict, policy: dict) -> CoverageGap | None:
    if requirement.level != "NON_FUNCTIONAL" or policy["nfr_policy"] != "PERFORMANCE_OR_EXPLICIT_WAIVER":
        return None
    if type_counts.get("PERFORMANCE", 0) == 0 and not any("waive" in (tc.title or "").lower() for tc in test_cases):
        return CoverageGap(requirement.req_id, f"{requirement.req_id} is NON_FUNCTIONAL with no PERFORMANCE test and no explicit waiver.")
    return None


# Function: _check_boundary_policy
def _check_boundary_policy(requirement, type_counts: dict) -> list[CoverageGap]:
    """Require BOUNDARY tests when requirement contains quantitative constraints."""
    gaps: list[CoverageGap] = []
    if _has_numeric_range(requirement.statement) and type_counts.get("BOUNDARY", 0) == 0:
        gaps.append(CoverageGap(requirement.req_id, f"{requirement.req_id} contains a numeric range/limit but has no BOUNDARY test."))
    evidence_lower = (requirement.statement or "").lower()
    if any(w in evidence_lower for w in ("quantity", "amount", "threshold", "capacity", "duration", "timeout")) and type_counts.get("BOUNDARY", 0) == 0:
        gaps.append(CoverageGap(requirement.req_id, f"{requirement.req_id} specifies a quantitative constraint but has no BOUNDARY test."))
    return gaps


# Function: _check_security_policy
def _check_security_policy(requirement, type_counts: dict) -> list[CoverageGap]:
    """Require SECURITY tests when requirement involves authorization, roles, or permissions."""
    gaps: list[CoverageGap] = []
    evidence_lower = " ".join([
        str(getattr(requirement, "statement", "")),
        *[str(value) for value in (getattr(requirement, "acceptance_criteria", None) or [])],
    ]).lower()
    if any(w in evidence_lower for w in ("role", "permission", "authorization", "approve", "unauthorized", 
                                         "entitled", "access control", "restricted")) and type_counts.get("NEGATIVE_SECURITY", 0) == 0:
        gaps.append(CoverageGap(requirement.req_id, f"{requirement.req_id} involves authorization/roles but has no NEGATIVE_SECURITY test."))
    return gaps


# Function: _check_integration_policy
def _check_integration_policy(requirement, test_cases: list) -> list[CoverageGap]:
    """Require INTEGRATION tests when requirement involves inter-system flows or reconciliation."""
    gaps: list[CoverageGap] = []
    evidence_lower = " ".join([
        str(getattr(requirement, "statement", "")),
        *[str(value) for value in (getattr(requirement, "acceptance_criteria", None) or [])],
    ]).lower()
    has_integration_case = any(
        getattr(test_case, "test_level", "") == "INTEGRATION"
        or _metadata_value(test_case, "coverage_dimension", "")
        in {"INTEGRATION_HANDOFF", "RECONCILIATION", "END_TO_END"}
        for test_case in test_cases
    )
    if any(w in evidence_lower for w in ("reconcil", "integration", "interface", "handoff", "inter-system",
                                         "external system", "sync", "workflow")) and not has_integration_case:
        gaps.append(CoverageGap(requirement.req_id, f"{requirement.req_id} involves system integration but has no INTEGRATION test."))
    return gaps



# Function: check_coverage
def check_coverage(requirement, test_cases: list, policy: dict = DEFAULT_POLICY) -> list[CoverageGap]:
    type_counts = _count_test_types(test_cases)
    gaps: list[CoverageGap] = []
    gaps.extend(_check_min_per_type(requirement, type_counts, policy))
    gaps.extend(_check_ac_coverage(requirement, test_cases, policy))

    nfr_gap = _check_nfr_policy(requirement, test_cases, type_counts, policy)
    if nfr_gap:
        gaps.append(nfr_gap)

    gaps.extend(_check_boundary_policy(requirement, type_counts))
    gaps.extend(_check_security_policy(requirement, type_counts))
    gaps.extend(_check_integration_policy(requirement, test_cases))

    return gaps
