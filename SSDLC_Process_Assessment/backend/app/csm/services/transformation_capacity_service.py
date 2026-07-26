# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: SSDLC_Process_Assessment — backend/app/csm/services (transformation_capacity_service.py)
# Date: 2026-03-09
# ---------------------------------------------------------------------------
from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Dict, List

from app.csm.models.vendor_spend import VendorSpendRecord

OPTIMIZATION_SCENARIOS = [
    {"name": "Conservative", "optimization_rate": Decimal("0.05")},
    {"name": "Target",       "optimization_rate": Decimal("0.10")},
    {"name": "Aggressive",   "optimization_rate": Decimal("0.15")},
]

REINVESTMENT_ALLOCATIONS = [
    {"area": "Salesforce / Customer & Dealer 360",  "pct": Decimal("0.30")},
    {"area": "Data & AI / Fabric / Databricks",      "pct": Decimal("0.30")},
    {"area": "Automation / Process Engineering",     "pct": Decimal("0.20")},
    {"area": "Copilot / AI Productivity",            "pct": Decimal("0.10")},
    {"area": "Architecture / Governance / TBM",      "pct": Decimal("0.10")},
]


class TransformationCapacityService:
    """Calculate capacity for transformation investment created by vendor optimisation."""

    # Function: calculate
    def calculate(self, records: List[VendorSpendRecord]) -> Dict[str, Any]:
        third_party_spend = sum((r.annual_spend for r in records), Decimal("0"))

        scenarios = []
        for s_def in OPTIMIZATION_SCENARIOS:
            rate = s_def["optimization_rate"]
            capacity = (rate * third_party_spend).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            scenarios.append({
                "name": s_def["name"],
                "optimization_rate": str(rate),
                "optimization_rate_fmt": f"{(rate * 100).quantize(Decimal('0.0'))}%",
                "capacity_created": str(capacity),
                "capacity_created_fmt": f"${capacity / Decimal('1000000'):.2f}M",
                "reinvestment_pool": str(capacity),
                "reinvestment_pool_fmt": f"${capacity / Decimal('1000000'):.2f}M",
            })

        # Target scenario (index 1) drives reinvestment allocations
        target_capacity = (OPTIMIZATION_SCENARIOS[1]["optimization_rate"] * third_party_spend).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        allocations = []
        for alloc in REINVESTMENT_ALLOCATIONS:
            funding = (alloc["pct"] * target_capacity).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            allocations.append({
                "area": alloc["area"],
                "pct": str(alloc["pct"]),
                "pct_fmt": f"{(alloc['pct'] * 100).quantize(Decimal('0.0'))}%",
                "funding": str(funding),
                "funding_fmt": f"${funding / Decimal('1000000'):.2f}M",
            })

        audit: Dict[str, Any] = {
            "service": "TransformationCapacityService",
            "third_party_spend": str(third_party_spend),
            "formula": "capacity_created = optimization_rate × third_party_spend; allocation_funding = pct × target_capacity",
            "target_capacity": str(target_capacity),
        }

        return {
            "third_party_spend": str(third_party_spend),
            "third_party_spend_fmt": f"${third_party_spend / Decimal('1000000'):.1f}M",
            "scenarios": scenarios,
            "target_capacity": str(target_capacity),
            "target_capacity_fmt": f"${target_capacity / Decimal('1000000'):.2f}M",
            "reinvestment_allocations": allocations,
            "calculation_audit": audit,
        }
