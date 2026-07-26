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

import re
from dataclasses import dataclass

DEFAULT_POLICY = {
    "min_per_requirement": {"POSITIVE": 1, "NEGATIVE": 1, "EDGE": 1},
    "acceptance_criteria_coverage": "EVERY_AC_MAPPED",
    "nfr_policy": "PERFORMANCE_OR_EXPLICIT_WAIVER",
    "boundary_required_when": "requirement contains a numeric range or limit",
}

_NUMERIC_RANGE_RE = re.compile(r"\b(\d+(\.\d+)?\s*(-|to|and)\s*\d+(\.\d+)?|\bmax(imum)?\b|\bmin(imum)?\b|\blimit\b)", re.IGNORECASE)


@dataclass
class CoverageGap:
    req_id: str
    description: str


# Function: _ac_is_mapped
def _ac_is_mapped(ac_text: str, test_cases: list) -> bool:
    ac_lower = ac_text.lower()
    ac_keywords = {w for w in re.findall(r"[a-z]{4,}", ac_lower)}
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
    return type_counts


# Function: _check_min_per_type
def _check_min_per_type(requirement, type_counts: dict, policy: dict) -> list[CoverageGap]:
    gaps: list[CoverageGap] = []
    for test_type, minimum in policy["min_per_requirement"].items():
        if type_counts.get(test_type, 0) < minimum:
            gaps.append(CoverageGap(requirement.req_id, f"{requirement.req_id} has no {test_type} test (requires >={minimum})."))
    return gaps


# Function: _check_ac_coverage
def _check_ac_coverage(requirement, test_cases: list, policy: dict) -> list[CoverageGap]:
    gaps: list[CoverageGap] = []
    if policy["acceptance_criteria_coverage"] != "EVERY_AC_MAPPED":
        return gaps
    for i, ac in enumerate(requirement.acceptance_criteria, start=1):
        if not _ac_is_mapped(ac, test_cases):
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
def _check_boundary_policy(requirement, type_counts: dict) -> CoverageGap | None:
    if _NUMERIC_RANGE_RE.search(requirement.statement) and type_counts.get("BOUNDARY", 0) == 0:
        return CoverageGap(requirement.req_id, f"{requirement.req_id} contains a numeric range/limit but has no BOUNDARY test.")
    return None


# Function: check_coverage
def check_coverage(requirement, test_cases: list, policy: dict = DEFAULT_POLICY) -> list[CoverageGap]:
    type_counts = _count_test_types(test_cases)
    gaps: list[CoverageGap] = []
    gaps.extend(_check_min_per_type(requirement, type_counts, policy))
    gaps.extend(_check_ac_coverage(requirement, test_cases, policy))

    nfr_gap = _check_nfr_policy(requirement, test_cases, type_counts, policy)
    if nfr_gap:
        gaps.append(nfr_gap)

    boundary_gap = _check_boundary_policy(requirement, type_counts)
    if boundary_gap:
        gaps.append(boundary_gap)

    return gaps
