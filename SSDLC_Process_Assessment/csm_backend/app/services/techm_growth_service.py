# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: SSDLC_Process_Assessment — csm_backend/app/services (techm_growth_service.py)
# Date: 2026-05-21
# ---------------------------------------------------------------------------
from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Dict, List

from app.models.vendor_spend import VendorSpendRecord

OPPORTUNITY_AREAS = [
    {"area": "Salesforce Transformation",           "low": Decimal("3000000"), "high": Decimal("5000000")},
    {"area": "Data & AI / Fabric Implementation",   "low": Decimal("2000000"), "high": Decimal("4000000")},
    {"area": "Automation / Process Engineering",    "low": Decimal("1000000"), "high": Decimal("2000000")},
    {"area": "Managed Services Expansion",          "low": Decimal("2000000"), "high": Decimal("4000000")},
    {"area": "Application Consolidation",           "low": Decimal("2000000"), "high": Decimal("5000000")},
]

SCENARIO_TARGETS = [
    {"name": "Current Baseline",  "year_1_target": None},          # filled from data
    {"name": "Target Case",       "year_1_target": Decimal("10000000")},
    {"name": "Stretch Case",      "year_1_target": Decimal("15000000")},
    {"name": "Aggressive Case",   "year_1_target": Decimal("20000000")},
]


class TechMGrowthService:
    """Calculate Tech Mahindra growth scenarios and opportunity areas."""

    # Function: calculate
    def calculate(self, records: List[VendorSpendRecord]) -> Dict[str, Any]:
        current_techm_spend = sum(
            r.annual_spend for r in records
            if "tech mahindra" in r.vendor.lower() or r.vendor.strip().lower() == "techmahindra"
        ) or Decimal("0")

        scenarios = []
        for s_def in SCENARIO_TARGETS:
            target = s_def["year_1_target"] if s_def["year_1_target"] is not None else current_techm_spend
            incremental = target - current_techm_spend
            growth_pct = (
                (incremental / current_techm_spend).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
                if current_techm_spend
                else Decimal("0")
            )
            quarterly_run_rate = (target / 4).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

            scenarios.append({
                "name": s_def["name"],
                "year_1_target": str(target),
                "year_1_target_fmt": f"${target / Decimal('1000000'):.1f}M",
                "incremental_growth": str(incremental),
                "incremental_growth_fmt": f"${incremental / Decimal('1000000'):.1f}M",
                "growth_pct": str(growth_pct),
                "growth_pct_fmt": f"{(growth_pct * 100).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)}%",
                "quarterly_run_rate": str(quarterly_run_rate),
                "quarterly_run_rate_fmt": f"${quarterly_run_rate / Decimal('1000000'):.2f}M",
            })

        opportunity_areas = []
        for opp in OPPORTUNITY_AREAS:
            expected = ((opp["low"] + opp["high"]) / 2).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            opportunity_areas.append({
                "area": opp["area"],
                "low": str(opp["low"]),
                "high": str(opp["high"]),
                "expected": str(expected),
                "low_fmt": f"${opp['low'] / Decimal('1000000'):.1f}M",
                "high_fmt": f"${opp['high'] / Decimal('1000000'):.1f}M",
                "expected_fmt": f"${expected / Decimal('1000000'):.1f}M",
            })

        total_opportunity_low = sum(opp["low"] for opp in OPPORTUNITY_AREAS)
        total_opportunity_high = sum(opp["high"] for opp in OPPORTUNITY_AREAS)
        total_opportunity_expected = ((total_opportunity_low + total_opportunity_high) / 2).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        audit: Dict[str, Any] = {
            "service": "TechMGrowthService",
            "current_techm_spend": str(current_techm_spend),
            "formula": "incremental_growth = year_1_target - current_techm_spend; growth_pct = incremental_growth / current_techm_spend; quarterly_run_rate = year_1_target / 4",
        }

        return {
            "current_techm_spend": str(current_techm_spend),
            "current_techm_spend_fmt": f"${current_techm_spend / Decimal('1000000'):.1f}M",
            "scenarios": scenarios,
            "opportunity_areas": opportunity_areas,
            "total_opportunity_low": str(total_opportunity_low),
            "total_opportunity_high": str(total_opportunity_high),
            "total_opportunity_expected": str(total_opportunity_expected),
            "calculation_audit": audit,
        }
