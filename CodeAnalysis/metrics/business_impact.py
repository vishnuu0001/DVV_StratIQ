# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Measures the business criticality of an application (0–100).
# Date: 2026-03-24
# ---------------------------------------------------------------------------
"""
business_impact.py
------------------
Measures the business criticality of an application (0–100).

Scoring Factors
~~~~~~~~~~~~~~~
Factor                  Weight  Source
----------------------  ------  -----------------------------------------
User Volume             25 %    survey / default
Release Frequency       20 %    repo releases + commits per year
Revenue Impact          20 %    survey / default
Application Age Risk    15 %    repo creation date + tech age
Operational Exposure    10 %    open issues, stars, forks
Integration Breadth     10 %    dependency count

Survey fields can be provided manually to override defaults when running
via the CLI / config file.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional


@dataclass
class BusinessImpactScore:
    total:                float   # 0–100  (higher = more critical)
    user_volume_score:    float
    release_freq_score:   float
    revenue_score:        float
    age_risk_score:       float
    operational_score:    float
    integration_score:    float
    risk_label:           str     # LOW / MEDIUM / HIGH / CRITICAL


class BusinessImpactCalculator:
    """
    Computes Business Impact Index from repo metadata and optional survey data.
    """

    # Function: calculate
    def calculate(
        self,
        repo_meta=None,           # Optional[RepoMetadata]
        users:          int   = 100,
        revenue_usd:    float = 0.0,
        releases_year:  Optional[int] = None,
        dependency_count: int = 0,
    ) -> BusinessImpactScore:

        # ── User Volume (0-100) ───────────────────────────────────────────────
        # Log scale: 1 user → 0, 1M users → 100
        users = max(1, users)
        uv_score = min(100.0, math.log10(users) / 6.0 * 100)

        # ── Release Frequency (0-100) ─────────────────────────────────────────
        if releases_year is None and repo_meta:
            releases_year = repo_meta.releases
        releases_year = releases_year or 1
        # 52+ releases/year (weekly) = 100
        rf_score = min(100.0, releases_year / 52.0 * 100)

        # ── Revenue Impact (0-100) ────────────────────────────────────────────
        # $0 → 0, $100M+ → 100  (log scale)
        if revenue_usd <= 0:
            rev_score = 10.0   # minimal assumed impact
        else:
            rev_score = min(100.0, math.log10(revenue_usd + 1) / 8.0 * 100)

        # ── Application Age Risk (0-100) ──────────────────────────────────────
        # Older, less-active repos score higher (more risk)
        age_score = 0.0
        if repo_meta:
            days_stale = repo_meta.last_commit_days
            age_score  = min(100.0, days_stale / 730.0 * 100)   # 2 yrs = score 100

        # ── Operational Exposure (0-100) ──────────────────────────────────────
        op_score = 0.0
        if repo_meta:
            stars  = repo_meta.stars
            issues = repo_meta.open_issues
            forks  = repo_meta.forks
            op_score = min(100.0,
                (math.log10(stars + 1) / 4.0 * 40)
                + (math.log10(issues + 1) / 3.0 * 40)
                + (math.log10(forks + 1) / 3.0 * 20)
            )

        # ── Integration Breadth (0-100) ───────────────────────────────────────
        int_score = min(100.0, dependency_count / 50.0 * 100)

        # ── Weighted Total ────────────────────────────────────────────────────
        total = (
            0.25 * uv_score
            + 0.20 * rf_score
            + 0.20 * rev_score
            + 0.15 * age_score
            + 0.10 * op_score
            + 0.10 * int_score
        )

        label = (
            "CRITICAL" if total >= 80 else
            "HIGH"     if total >= 60 else
            "MEDIUM"   if total >= 40 else
            "LOW"
        )

        return BusinessImpactScore(
            total               = round(total, 1),
            user_volume_score   = round(uv_score, 1),
            release_freq_score  = round(rf_score, 1),
            revenue_score       = round(rev_score, 1),
            age_risk_score      = round(age_score, 1),
            operational_score   = round(op_score, 1),
            integration_score   = round(int_score, 1),
            risk_label          = label,
        )
