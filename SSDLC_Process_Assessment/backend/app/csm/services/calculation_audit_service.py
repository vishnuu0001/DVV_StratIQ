# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: SSDLC_Process_Assessment — backend/app/csm/services (calculation_audit_service.py)
# Date: 2026-01-03
# ---------------------------------------------------------------------------
from __future__ import annotations

from decimal import Decimal
from typing import Any, Dict, List

from app.csm.models.inputs import InputAssumptions, DerivedInputs
from app.csm.models.tower_model import TowerModelResult
from app.csm.models.vendor_spend import VendorSpendRecord


class CalculationAuditService:
    """Aggregate all service audits into a single calculation trace."""

    # Function: build_full_audit
    def build_full_audit(
        self,
        inputs: InputAssumptions,
        derived: DerivedInputs,
        vendor_records: List[VendorSpendRecord],
        tower_result: TowerModelResult,
        additional_audits: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        total_spend = sum((r.annual_spend for r in vendor_records), Decimal("0"))

        audit: Dict[str, Any] = {
            "summary": {
                "total_vendor_records": len(vendor_records),
                "total_third_party_spend": str(total_spend),
                "tower_count": len(tower_result.rows),
                "total_gross_savings": str(tower_result.totals.gross_annual_savings),
                "total_net_year_1_savings": str(tower_result.totals.net_year_1_savings),
            },
            "inputs": {
                "raw": {
                    "total_technology_spend": str(inputs.total_technology_spend),
                    "direct_tech_opex": str(inputs.direct_tech_opex),
                    "tech_capex": str(inputs.tech_capex),
                    "internal_labor_pct": str(inputs.internal_labor_pct),
                    "external_talent_labor_spend": str(inputs.external_talent_labor_spend),
                    "total_third_party_spend": str(inputs.total_third_party_spend),
                    "vendor_management_overhead_pct": str(inputs.vendor_management_overhead_pct),
                    "target_vendor_management_overhead_reduction_pct": str(
                        inputs.target_vendor_management_overhead_reduction_pct
                    ),
                    "default_rate_compression_pct": str(inputs.default_rate_compression_pct),
                    "default_productivity_improvement_pct": str(inputs.default_productivity_improvement_pct),
                    "default_transition_duration_months": str(inputs.default_transition_duration_months),
                    "scenario_name": inputs.scenario_name,
                    "one_time_transition_cost_pct": str(inputs.one_time_transition_cost_pct),
                },
                "derived": {
                    "calculated_internal_labor": str(derived.calculated_internal_labor),
                    "external_spend_pct_of_total_tech_spend": str(derived.external_spend_pct_of_total_tech_spend),
                    "talent_spend_pct_of_third_party_spend": str(derived.talent_spend_pct_of_third_party_spend),
                },
            },
            "tower_model": tower_result.calculation_audit,
            "tower_rows": [
                {
                    "tower": row.tower,
                    "current_annual_spend": str(row.current_annual_spend),
                    "addressable_spend": str(row.addressable_spend),
                    "gross_annual_savings": str(row.gross_annual_savings),
                    "transition_cost": str(row.transition_cost),
                    "net_year_1_savings": str(row.net_year_1_savings),
                    "audit": row.calculation_audit,
                }
                for row in tower_result.rows
            ],
        }

        if additional_audits:
            audit.update(additional_audits)

        return audit
