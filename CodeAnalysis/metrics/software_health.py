# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Computes the three Software Health sub-scores and their composite:
# Date: 2025-12-29
# ---------------------------------------------------------------------------
"""
software_health.py
------------------
Computes the three Software Health sub-scores and their composite:

    Software Health = 0.40 × Resiliency + 0.35 × Agility + 0.25 × Elegance

All scores are in the range [0, 100].

Definitions
~~~~~~~~~~~
Resiliency  – absence of code patterns that compromise reliability or security
              (empty catches, deep nesting, cyclomatic complexity spikes, TODO/FIXME)
Agility     – how easily the software can adapt to change
              (long-method ratio, duplication proxy, comment ratio, class cohesion)
Elegance    – simplicity and maintainability
              (avg complexity, magic-number density, SLOC per file, bad-practice count)
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List

from analyzers.base_analyzer import LanguageReport
from config.settings import HEALTH_WEIGHTS


@dataclass
class HealthScore:
    resiliency:     float
    agility:        float
    elegance:       float
    health:         float          # weighted composite
    risk_label:     str            # CRITICAL / HIGH RISK / FAIR / GOOD / EXCELLENT
    summary:        List[str]      = None   # human-readable findings

    # Function: __post_init__
    def __post_init__(self):
        if self.summary is None:
            self.summary = []


class SoftwareHealthCalculator:
    """
    Derives health scores from one or more :class:`LanguageReport` objects.
    """

    # Penalty thresholds
    HIGH_COMPLEXITY   = 10     # cyclomatic above this is HIGH risk
    MEDIUM_COMPLEXITY = 5
    COMMENT_MIN_RATIO = 0.10   # below this is under-commented
    COMMENT_MAX_RATIO = 0.40   # above this may signal dead code
    LONG_METHOD_BAD   = 20.0   # % of long methods above this → bad
    DEEP_NEST_BAD     = 5.0    # % of deeply-nested lines above this → bad
    MAGIC_NB_BAD      = 50     # magic numbers per 1k SLOC above this → bad
    TODO_BAD          = 10     # TODO per 1k SLOC above this → bad

    # Function: _aggregate_metrics
    @staticmethod
    def _aggregate_metrics(reports: List[LanguageReport]) -> dict:
        total_sloc     = sum(r.total_sloc      for r in reports) or 1
        avg_complexity = (
            sum(r.avg_complexity * r.total_sloc for r in reports) / total_sloc
        )
        long_meth_pct  = (
            sum(r.long_methods_pct * r.total_sloc for r in reports) / total_sloc
        )
        deep_nest_pct  = (
            sum(r.deep_nesting_pct * r.total_sloc for r in reports) / total_sloc
        )
        comment_ratio  = (
            sum(r.comment_ratio * r.total_sloc for r in reports) / total_sloc
        )
        total_files    = sum(r.file_count for r in reports) or 1
        bad_practice_hits = sum(len(r.bad_practices) for r in reports)

        # ── Magic numbers & TODOs per 1k SLOC ─────────────────────────────────
        magic_per_kloc = (
            sum(
                sum(f.magic_numbers for f in r.files) for r in reports
            ) / total_sloc * 1000
        )
        todo_per_kloc = (
            sum(
                sum(f.todo_comments for f in r.files) for r in reports
            ) / total_sloc * 1000
        )
        return {
            "total_sloc": total_sloc, "avg_complexity": avg_complexity,
            "long_meth_pct": long_meth_pct, "deep_nest_pct": deep_nest_pct,
            "comment_ratio": comment_ratio, "total_files": total_files,
            "bad_practice_hits": bad_practice_hits,
            "magic_per_kloc": magic_per_kloc, "todo_per_kloc": todo_per_kloc,
        }

    # Function: _score_resiliency
    def _score_resiliency(self, m: dict) -> float:
        res = 100.0
        if m["avg_complexity"] >= self.HIGH_COMPLEXITY:
            res -= 30
        elif m["avg_complexity"] >= self.MEDIUM_COMPLEXITY:
            res -= 15
        if m["deep_nest_pct"] > self.DEEP_NEST_BAD:
            res -= 20
        if m["todo_per_kloc"] > self.TODO_BAD:
            res -= 10
        res -= min(20, m["bad_practice_hits"] * 2)   # each bad-practice group −2
        return max(0.0, min(100.0, res))

    # Function: _score_agility
    def _score_agility(self, m: dict) -> float:
        agi = 100.0
        if m["long_meth_pct"] > self.LONG_METHOD_BAD:
            agi -= 25
        elif m["long_meth_pct"] > 10:
            agi -= 12
        # Comment ratio affects refactorability
        if m["comment_ratio"] < self.COMMENT_MIN_RATIO:
            agi -= 15
        elif m["comment_ratio"] > self.COMMENT_MAX_RATIO:
            agi -= 5
        agi -= min(20, m["bad_practice_hits"] * 1.5)
        return max(0.0, min(100.0, agi))

    # Function: _score_elegance
    def _score_elegance(self, m: dict) -> float:
        ele = 100.0
        if m["magic_per_kloc"] > self.MAGIC_NB_BAD:
            ele -= 20
        elif m["magic_per_kloc"] > 25:
            ele -= 10
        if m["avg_complexity"] > self.HIGH_COMPLEXITY:
            ele -= 15
        # Penalise very large files
        avg_sloc_per_file = m["total_sloc"] / m["total_files"]
        if avg_sloc_per_file > 500:
            ele -= 15
        elif avg_sloc_per_file > 300:
            ele -= 7
        ele -= min(15, m["bad_practice_hits"])
        return max(0.0, min(100.0, ele))

    # Function: _risk_label
    @staticmethod
    def _risk_label(health: float) -> str:
        if health >= 90:
            return "EXCELLENT"
        if health >= 75:
            return "GOOD"
        if health >= 60:
            return "FAIR"
        if health >= 40:
            return "HIGH RISK"
        return "CRITICAL"

    # Function: _build_findings
    def _build_findings(self, m: dict, reports: List[LanguageReport]) -> List[str]:
        findings: List[str] = []
        if m["avg_complexity"] >= self.HIGH_COMPLEXITY:
            findings.append(f"High average cyclomatic complexity ({m['avg_complexity']:.1f})")
        if m["long_meth_pct"] > self.LONG_METHOD_BAD:
            findings.append(f"High proportion of long methods ({m['long_meth_pct']:.1f}%)")
        if m["deep_nest_pct"] > self.DEEP_NEST_BAD:
            findings.append(f"Excessive deep nesting ({m['deep_nest_pct']:.1f}% of lines)")
        if m["magic_per_kloc"] > self.MAGIC_NB_BAD:
            findings.append(f"High magic-number density ({m['magic_per_kloc']:.0f}/kLOC)")
        if m["comment_ratio"] < self.COMMENT_MIN_RATIO:
            findings.append(f"Under-commented code (ratio={m['comment_ratio']:.2f})")
        for r in reports:
            findings.extend(r.bad_practices)
        return findings

    # Function: calculate
    def calculate(self, reports: List[LanguageReport]) -> HealthScore:
        """Aggregate all language reports into a single HealthScore."""
        m = self._aggregate_metrics(reports)

        resiliency = self._score_resiliency(m)
        agility    = self._score_agility(m)
        elegance   = self._score_elegance(m)

        # ── Composite ─────────────────────────────────────────────────────────
        health = (
            HEALTH_WEIGHTS["resiliency"] * resiliency
            + HEALTH_WEIGHTS["agility"]  * agility
            + HEALTH_WEIGHTS["elegance"] * elegance
        )

        label = self._risk_label(health)
        findings = self._build_findings(m, reports)

        return HealthScore(
            resiliency = round(resiliency, 1),
            agility    = round(agility, 1),
            elegance   = round(elegance, 1),
            health     = round(health, 1),
            risk_label = label,
            summary    = findings,
        )

    # Function: calculate_per_language
    def calculate_per_language(
        self, reports: List[LanguageReport]
    ) -> List[dict]:
        """
        Return a list of dicts, one per language, each containing
        resiliency / agility / elegance / health scores.
        Used for the "Software Health per Technology" polar chart.
        """
        result = []
        for r in reports:
            if r.file_count == 0:
                continue
            hs = self.calculate([r])
            result.append({
                "language":   r.language,
                "resiliency": hs.resiliency,
                "agility":    hs.agility,
                "elegance":   hs.elegance,
                "health":     hs.health,
                "risk_label": hs.risk_label,
                "sloc":       r.total_sloc,
                "files":      r.file_count,
            })
        # Sort by SLOC descending so primary language is first
        result.sort(key=lambda x: x["sloc"], reverse=True)
        return result
