# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Estimates Technical Debt using an enhanced COCOMO II-inspired model.
# Date: 2026-07-06
# ---------------------------------------------------------------------------
"""
technical_debt.py
-----------------
Estimates Technical Debt using an enhanced COCOMO II-inspired model.

COCOMO II Basic Equation
~~~~~~~~~~~~~~~~~~~~~~~~
    Effort (person-months) = A × (KSLOC)^B × ∏ EMi

Where:
    A              = 2.94  (calibration constant)
    B              = 0.91  (scale-factor exponent for organic projects)
    KSLOC          = thousands of SLOC
    EMi            = Effort Multipliers (complexity, reliability, …)

Technical Debt Definition
~~~~~~~~~~~~~~~~~~~~~~~~~
The *remediation effort* is the fraction of estimated maintenance effort
that would be required to bring the codebase to a healthy state.  This
fraction is derived from the Software Health score.

Output
~~~~~~
    debt_months    – estimated FTE-months of remediation work
    debt_ftes      – full-time equivalents required
    debt_usd       – estimated cost in USD
    debt_ratio     – remediation effort / total estimated maint. effort (%)
    density        – debt_months per 1k SLOC
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List

from analyzers.base_analyzer import LanguageReport
from config.settings import (
    AVG_SALARY_MONTH,
    COCOMO_A,
    COCOMO_B,
    WORK_HOURS_MONTH,
)


@dataclass
class TechnicalDebtScore:
    total_sloc:       int
    total_ksloc:      float
    estimated_effort: float    # total maint. effort (person-months)
    debt_months:      float    # remediation effort (person-months)
    debt_ftes:        float    # FTEs needed for remediation
    debt_usd:         float    # estimated USD cost
    debt_ratio:       float    # debt / effort  (0-100 %)
    density:          float    # debt months per 1k SLOC
    risk_label:       str      # LOW / MEDIUM / HIGH / CRITICAL


class TechnicalDebtCalculator:
    """
    Calculates technical debt from language reports and a health score.

    Parameters
    ----------
    health_score : float
        Composite Software Health score (0–100).  Low health → high debt fraction.
    """

    # Effort Multipliers indexed to avg cyclomatic complexity
    # Source: COCOMO II EM table (simplified)
    _EM_COMPLEXITY = {   # (threshold, multiplier)
        (0,   3):  0.73,
        (3,   7):  1.00,
        (7,   15): 1.17,
        (15,  25): 1.34,
        (25,  50): 1.74,
        (50, 999): 2.36,
    }

    # Function: calculate
    def calculate(
        self,
        reports: List[LanguageReport],
        health_score: float,
    ) -> TechnicalDebtScore:

        total_sloc = sum(r.total_sloc for r in reports)
        ksloc      = total_sloc / 1000.0 or 0.001

        avg_complexity = (
            sum(r.avg_complexity * r.total_sloc for r in reports)
            / total_sloc
        ) if total_sloc else 1.0

        # Effort Multiplier from complexity
        em = 1.0
        for (lo, hi), mult in self._EM_COMPLEXITY.items():
            if lo <= avg_complexity < hi:
                em = mult
                break

        # Reliability EM (derived from health → proxy for defect density)
        reliability_em = self._reliability_em(health_score)

        # Base COCOMO II effort
        total_effort = COCOMO_A * math.pow(ksloc, COCOMO_B) * em * reliability_em

        # Debt fraction: codebase at full health → 5% overhead;
        # each point below 100 adds proportional debt burden
        debt_fraction = max(0.0, (100.0 - health_score)) / 100.0 * 0.80 + 0.05
        debt_months   = total_effort * debt_fraction

        debt_ftes = debt_months / 12.0          # 1 FTE = 12 person-months / year
        debt_usd  = debt_months * AVG_SALARY_MONTH

        debt_ratio = (debt_months / total_effort * 100) if total_effort else 0
        density    = (debt_months / ksloc) if ksloc else 0

        if debt_ratio <= 5:
            risk = "LOW"
        elif debt_ratio <= 20:
            risk = "MEDIUM"
        elif debt_ratio <= 40:
            risk = "HIGH"
        else:
            risk = "CRITICAL"

        return TechnicalDebtScore(
            total_sloc       = total_sloc,
            total_ksloc      = round(ksloc, 2),
            estimated_effort = round(total_effort, 1),
            debt_months      = round(debt_months, 1),
            debt_ftes        = round(debt_ftes, 2),
            debt_usd         = round(debt_usd, 0),
            debt_ratio       = round(debt_ratio, 1),
            density          = round(density, 3),
            risk_label       = risk,
        )

    # Function: _reliability_em
    @staticmethod
    def _reliability_em(health: float) -> float:
        """Map health score to a COCOMO reliability effort multiplier."""
        if health >= 90:  return 0.75   # Very High reliability (low defect rate)
        if health >= 75:  return 1.00   # High
        if health >= 60:  return 1.15   # Nominal
        if health >= 40:  return 1.40   # Low
        return 1.65                     # Very Low
