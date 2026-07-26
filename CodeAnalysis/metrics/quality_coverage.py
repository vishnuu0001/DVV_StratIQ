# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: CAST-style quality coverage model combining code quality and vulnerability signals.
# Date: 2025-09-26
# ---------------------------------------------------------------------------
"""
quality_coverage.py
-------------------
CAST-style quality coverage model combining code quality and vulnerability signals.

Dimensions (0-100)
~~~~~~~~~~~~~~~~~~
- robustness
- efficiency
- security
- changeability
- transferability
- green

Also emits:
- tqi_score_4 (ISO-like 1..4 scale)
- top critical rule violations
- vulnerability age matrix
- comment/code health summary
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from analyzers.base_analyzer import LanguageReport
from metrics.open_source_safety import OpenSourceSafetyScore
from metrics.software_health import HealthScore
from metrics.technical_debt import TechnicalDebtScore
from metrics.green_impact import GreenImpactScore


@dataclass
class QualityCoverageScore:
    robustness: float
    efficiency: float
    security: float
    changeability: float
    transferability: float
    green: float
    total: float
    tqi_score_4: float
    risk_label: str

    critical_violations: int
    violation_density_per_kloc: float
    comment_ratio_pct: float
    commented_out_ratio_pct: float

    top_critical_rules: List[Dict] = field(default_factory=list)
    vulnerability_age_matrix: Dict[str, Dict[str, int]] = field(default_factory=dict)


class QualityCoverageCalculator:
    """Compute CAST-like quality dimensions and supporting risk summaries."""

    # Function: calculate
    def calculate(
        self,
        language_reports: List[LanguageReport],
        health: HealthScore,
        debt: TechnicalDebtScore,
        oss: OpenSourceSafetyScore,
        green_impact: GreenImpactScore | None = None,
    ) -> QualityCoverageScore:
        total_sloc = sum(r.total_sloc for r in language_reports) or 1

        long_methods = sum(sum(f.long_methods for f in r.files) for r in language_reports)
        deep_nesting = sum(sum(f.deep_nesting for f in r.files) for r in language_reports)
        high_cc_files = sum(sum(1 for f in r.files if (f.cyclomatic or 0) >= 15) for r in language_reports)
        very_high_cc_files = sum(sum(1 for f in r.files if (f.cyclomatic or 0) >= 25) for r in language_reports)
        todo_count = sum(sum(f.todo_comments for f in r.files) for r in language_reports)
        magic_numbers = sum(sum(f.magic_numbers for f in r.files) for r in language_reports)
        commented_out = sum(sum(f.commented_out_lines for f in r.files) for r in language_reports)
        comment_lines = sum(r.total_comments for r in language_reports)

        dep_count = max(oss.dependency_count, 1)
        cve_critical = oss.cve_critical
        cve_high = oss.cve_high
        cve_medium = oss.cve_medium

        # ── Dimension scores (0-100) ─────────────────────────────────────────
        robustness = health.resiliency

        eff_penalty = min(35.0, debt.debt_ratio * 0.55) + min(25.0, long_methods * 0.2)
        efficiency = max(0.0, 100.0 - eff_penalty)

        sev_weighted = cve_critical * 10 + cve_high * 5 + cve_medium * 2
        sec_penalty = min(80.0, (sev_weighted / dep_count) * 10)
        security = max(0.0, 100.0 - sec_penalty)

        ch_penalty = min(30.0, long_methods * 0.25) + min(25.0, deep_nesting * 0.15) + min(20.0, todo_count * 0.25)
        changeability = max(0.0, 100.0 - ch_penalty)

        comment_ratio = (comment_lines / total_sloc) * 100
        commented_out_ratio = (commented_out / total_sloc) * 100
        transferability = 100.0
        if comment_ratio < 8:
            transferability -= 25
        elif comment_ratio < 12:
            transferability -= 10
        if commented_out_ratio > 2:
            transferability -= 20
        elif commented_out_ratio > 1:
            transferability -= 10
        transferability -= min(20.0, magic_numbers * 0.05)
        transferability = max(0.0, transferability)

        green = green_impact.green_score if green_impact else 55.0

        total = (
            0.22 * robustness
            + 0.16 * efficiency
            + 0.22 * security
            + 0.16 * changeability
            + 0.14 * transferability
            + 0.10 * green
        )

        # Map 0-100 to 1-4 scale (higher is better), matching the style in CAST slides.
        tqi_score_4 = 1.0 + (max(0.0, min(100.0, total)) / 100.0) * 3.0

        if total >= 80:
            risk = "LOW"
        elif total >= 65:
            risk = "MEDIUM"
        elif total >= 50:
            risk = "HIGH"
        else:
            risk = "VERY_HIGH"

        critical_violations = (
            very_high_cc_files
            + cve_critical * 3
            + cve_high * 2
            + max(0, oss.vulnerable_count - cve_critical - cve_high)
            + int(long_methods * 0.2)
        )
        violation_density = critical_violations / (total_sloc / 1000.0)

        top_rules = [
            {
                "rule": "Very high cyclomatic complexity (CC >= 25)",
                "count": very_high_cc_files,
                "severity": "high",
                "category": "robustness",
            },
            {
                "rule": "High cyclomatic complexity (CC >= 15)",
                "count": max(0, high_cc_files - very_high_cc_files),
                "severity": "medium",
                "category": "efficiency",
            },
            {
                "rule": "Long methods (>40 LOC)",
                "count": long_methods,
                "severity": "medium",
                "category": "changeability",
            },
            {
                "rule": "Deep nesting (>4 levels)",
                "count": deep_nesting,
                "severity": "medium",
                "category": "changeability",
            },
            {
                "rule": "Critical OSS vulnerabilities",
                "count": cve_critical,
                "severity": "critical",
                "category": "security",
            },
            {
                "rule": "High OSS vulnerabilities",
                "count": cve_high,
                "severity": "high",
                "category": "security",
            },
            {
                "rule": "Commented-out code",
                "count": commented_out,
                "severity": "medium",
                "category": "transferability",
            },
        ]
        top_rules = [r for r in top_rules if r["count"] > 0]
        top_rules.sort(key=lambda r: r["count"], reverse=True)

        age_matrix = self._build_age_matrix(oss)

        return QualityCoverageScore(
            robustness=round(robustness, 1),
            efficiency=round(efficiency, 1),
            security=round(security, 1),
            changeability=round(changeability, 1),
            transferability=round(transferability, 1),
            green=round(green, 1),
            total=round(total, 1),
            tqi_score_4=round(tqi_score_4, 2),
            risk_label=risk,
            critical_violations=int(critical_violations),
            violation_density_per_kloc=round(violation_density, 2),
            comment_ratio_pct=round(comment_ratio, 2),
            commented_out_ratio_pct=round(commented_out_ratio, 2),
            top_critical_rules=top_rules[:8],
            vulnerability_age_matrix=age_matrix,
        )

    # Function: _build_age_matrix
    @staticmethod
    def _build_age_matrix(oss: OpenSourceSafetyScore) -> Dict[str, Dict[str, int]]:
        matrix = {
            ">3y": {"critical": 0, "high": 0, "medium": 0, "low": 0},
            "2-3y": {"critical": 0, "high": 0, "medium": 0, "low": 0},
            "1-2y": {"critical": 0, "high": 0, "medium": 0, "low": 0},
            "<1y": {"critical": 0, "high": 0, "medium": 0, "low": 0},
        }

        for dep in (oss.details or []):
            age = dep.age_years or 0
            sev = (dep.cve_severity or "LOW").lower()
            sev = sev if sev in {"critical", "high", "medium", "low"} else "low"

            if age > 3:
                bucket = ">3y"
            elif age >= 2:
                bucket = "2-3y"
            elif age >= 1:
                bucket = "1-2y"
            else:
                bucket = "<1y"

            if dep.vulnerable:
                matrix[bucket][sev] += max(1, dep.vuln_count or 1)

        return matrix
