# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: SSDLC_Process_Assessment — backend/app/csm/services (operating_model_service.py)
# Date: 2026-05-20
# ---------------------------------------------------------------------------
from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Dict, List

from app.csm.models.inputs import InputAssumptions
from app.csm.models.vendor_spend import VendorSpendRecord


class OperatingModelService:
    """Analyse the operating model implications of vendor consolidation."""

    # Function: analyse
    def analyse(
        self,
        records: List[VendorSpendRecord],
        inputs: InputAssumptions,
    ) -> Dict[str, Any]:
        total_spend = sum((r.annual_spend for r in records), Decimal("0"))
        talent_spend = sum(
            r.annual_spend for r in records if r.spend_category.strip().lower() == "talent"
        ) or Decimal("0")
        software_spend = sum(
            r.annual_spend for r in records if r.spend_category.strip().lower() == "software"
        ) or Decimal("0")
        data_spend = sum(
            r.annual_spend for r in records if r.spend_category.strip().lower() == "data"
        ) or Decimal("0")

        internal_labor = (inputs.total_technology_spend * inputs.internal_labor_pct).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        vendor_overhead_cost = (total_spend * inputs.vendor_management_overhead_pct).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        potential_overhead_reduction = (
            vendor_overhead_cost * inputs.target_vendor_management_overhead_reduction_pct
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        # Span of control estimate: unique vendors
        unique_vendors = len({r.vendor for r in records})

        talent_pct = (talent_spend / total_spend).quantize(Decimal("0.0001")) if total_spend else Decimal("0")

        recommendations = []
        if talent_pct > Decimal("0.50"):
            recommendations.append({
                "area": "Talent Consolidation",
                "finding": f"Talent spend ({talent_pct * 100:.1f}% of total) is above 50% threshold.",
                "action": "Consolidate to 2-3 preferred staffing vendors with volume discounts and SLA commitments.",
            })
        if unique_vendors > 20:
            recommendations.append({
                "area": "Vendor Rationalisation",
                "finding": f"{unique_vendors} unique vendors creates high management overhead.",
                "action": "Target reduction to <15 strategic vendors over 18 months.",
            })
        recommendations.append({
            "area": "Vendor Management Overhead",
            "finding": f"Current overhead at {inputs.vendor_management_overhead_pct * 100}% = ${vendor_overhead_cost / Decimal('1000000'):.1f}M.",
            "action": f"Reduce by {inputs.target_vendor_management_overhead_reduction_pct * 100:.0f}%, saving ${potential_overhead_reduction / Decimal('1000000'):.2f}M annually.",
        })

        return {
            "total_technology_spend": str(inputs.total_technology_spend),
            "internal_labor_spend": str(internal_labor),
            "total_third_party_spend": str(total_spend),
            "talent_spend": str(talent_spend),
            "software_spend": str(software_spend),
            "data_spend": str(data_spend),
            "talent_pct_of_third_party": str(talent_pct),
            "vendor_management_overhead_cost": str(vendor_overhead_cost),
            "potential_overhead_reduction": str(potential_overhead_reduction),
            "unique_vendor_count": unique_vendors,
            "recommendations": recommendations,
            "calculation_audit": {
                "service": "OperatingModelService",
                "internal_labor": f"total_technology_spend × internal_labor_pct = {inputs.total_technology_spend} × {inputs.internal_labor_pct}",
                "vendor_overhead": f"total_spend × vendor_management_overhead_pct = {total_spend} × {inputs.vendor_management_overhead_pct}",
            },
        }
