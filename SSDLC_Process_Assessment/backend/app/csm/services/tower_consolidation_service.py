# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: SSDLC_Process_Assessment — backend/app/csm/services (tower_consolidation_service.py)
# Date: 2025-12-05
# ---------------------------------------------------------------------------
from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Dict, List, Optional

from app.csm.models.inputs import InputAssumptions
from app.csm.models.tower_model import TowerParam, TowerSavingsRow, TowerModelResult, DEFAULT_TOWER_PARAMS
from app.csm.models.vendor_spend import VendorSpendRecord


class TowerConsolidationService:
    """Calculate tower-level consolidation savings."""

    # Function: calculate_tower_row
    def calculate_tower_row(
        self,
        tower_name: str,
        consolidation_scope_pct: Decimal,
        vendor_records: List[VendorSpendRecord],
        inputs: InputAssumptions,
        recommended_action: str = "",
        notes: str = "",
    ) -> TowerSavingsRow:
        # Current spend & vendor count for this tower
        current_annual_spend = sum(
            r.annual_spend for r in vendor_records if r.tower == tower_name
        ) or Decimal("0")
        current_vendor_count = len([r for r in vendor_records if r.tower == tower_name])

        # Addressable spend
        addressable_spend = (current_annual_spend * consolidation_scope_pct).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        # Savings components
        productivity_savings = (addressable_spend * inputs.default_productivity_improvement_pct).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        rate_savings = (addressable_spend * inputs.default_rate_compression_pct).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        vendor_mgmt_overhead_savings = (
            addressable_spend
            * inputs.vendor_management_overhead_pct
            * inputs.target_vendor_management_overhead_reduction_pct
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        gross_annual_savings = (productivity_savings + rate_savings + vendor_mgmt_overhead_savings).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        transition_cost = (addressable_spend * inputs.one_time_transition_cost_pct).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        net_year_1_savings = (gross_annual_savings - transition_cost).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        run_rate_annual_savings = gross_annual_savings

        audit: Dict[str, Any] = {
            "tower": tower_name,
            "formulas": [
                {
                    "name": "addressable_spend",
                    "expression": "current_annual_spend × consolidation_scope_pct",
                    "inputs": {
                        "current_annual_spend": str(current_annual_spend),
                        "consolidation_scope_pct": str(consolidation_scope_pct),
                    },
                    "result": str(addressable_spend),
                },
                {
                    "name": "productivity_savings",
                    "expression": "addressable_spend × default_productivity_improvement_pct",
                    "inputs": {
                        "addressable_spend": str(addressable_spend),
                        "default_productivity_improvement_pct": str(inputs.default_productivity_improvement_pct),
                    },
                    "result": str(productivity_savings),
                },
                {
                    "name": "rate_savings",
                    "expression": "addressable_spend × default_rate_compression_pct",
                    "inputs": {
                        "addressable_spend": str(addressable_spend),
                        "default_rate_compression_pct": str(inputs.default_rate_compression_pct),
                    },
                    "result": str(rate_savings),
                },
                {
                    "name": "vendor_mgmt_overhead_savings",
                    "expression": "addressable_spend × vendor_management_overhead_pct × target_vendor_management_overhead_reduction_pct",
                    "inputs": {
                        "addressable_spend": str(addressable_spend),
                        "vendor_management_overhead_pct": str(inputs.vendor_management_overhead_pct),
                        "target_vendor_management_overhead_reduction_pct": str(
                            inputs.target_vendor_management_overhead_reduction_pct
                        ),
                    },
                    "result": str(vendor_mgmt_overhead_savings),
                },
                {
                    "name": "gross_annual_savings",
                    "expression": "productivity_savings + rate_savings + vendor_mgmt_overhead_savings",
                    "inputs": {
                        "productivity_savings": str(productivity_savings),
                        "rate_savings": str(rate_savings),
                        "vendor_mgmt_overhead_savings": str(vendor_mgmt_overhead_savings),
                    },
                    "result": str(gross_annual_savings),
                },
                {
                    "name": "transition_cost",
                    "expression": "addressable_spend × one_time_transition_cost_pct",
                    "inputs": {
                        "addressable_spend": str(addressable_spend),
                        "one_time_transition_cost_pct": str(inputs.one_time_transition_cost_pct),
                    },
                    "result": str(transition_cost),
                },
                {
                    "name": "net_year_1_savings",
                    "expression": "gross_annual_savings - transition_cost",
                    "inputs": {
                        "gross_annual_savings": str(gross_annual_savings),
                        "transition_cost": str(transition_cost),
                    },
                    "result": str(net_year_1_savings),
                },
            ],
        }

        return TowerSavingsRow(
            tower=tower_name,
            current_annual_spend=current_annual_spend,
            current_vendor_count=current_vendor_count,
            consolidation_scope_pct=consolidation_scope_pct,
            addressable_spend=addressable_spend,
            productivity_savings=productivity_savings,
            rate_savings=rate_savings,
            vendor_mgmt_overhead_savings=vendor_mgmt_overhead_savings,
            gross_annual_savings=gross_annual_savings,
            transition_cost=transition_cost,
            net_year_1_savings=net_year_1_savings,
            run_rate_annual_savings=run_rate_annual_savings,
            calculation_audit=audit,
        )

    # Function: calculate_model
    def calculate_model(
        self,
        vendor_records: List[VendorSpendRecord],
        inputs: InputAssumptions,
        tower_params: Optional[List[TowerParam]] = None,
    ) -> TowerModelResult:
        if tower_params is None:
            tower_params = DEFAULT_TOWER_PARAMS

        rows: List[TowerSavingsRow] = []
        for param in tower_params:
            row = self.calculate_tower_row(
                tower_name=param.tower,
                consolidation_scope_pct=param.consolidation_scope_pct,
                vendor_records=vendor_records,
                inputs=inputs,
                recommended_action=param.recommended_action,
                notes=param.notes,
            )
            rows.append(row)

        # Compute totals row
        totals = self._compute_totals(rows)

        audit: Dict[str, Any] = {
            "service": "TowerConsolidationService",
            "tower_count": len(rows),
            "total_current_spend": str(totals.current_annual_spend),
            "total_addressable_spend": str(totals.addressable_spend),
            "total_gross_savings": str(totals.gross_annual_savings),
            "total_transition_cost": str(totals.transition_cost),
            "total_net_year_1": str(totals.net_year_1_savings),
            "effective_gross_rate_formula": "gross / addressable",
            "effective_gross_rate": str(
                (totals.gross_annual_savings / totals.addressable_spend).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
                if totals.addressable_spend
                else Decimal("0")
            ),
            "parameters_used": {
                "default_productivity_improvement_pct": str(inputs.default_productivity_improvement_pct),
                "default_rate_compression_pct": str(inputs.default_rate_compression_pct),
                "vendor_management_overhead_pct": str(inputs.vendor_management_overhead_pct),
                "target_vendor_management_overhead_reduction_pct": str(
                    inputs.target_vendor_management_overhead_reduction_pct
                ),
                "one_time_transition_cost_pct": str(inputs.one_time_transition_cost_pct),
            },
        }

        return TowerModelResult(rows=rows, totals=totals, calculation_audit=audit)

    # Function: _compute_totals
    def _compute_totals(self, rows: List[TowerSavingsRow]) -> TowerSavingsRow:
        # Function: _sum
        def _sum(attr: str) -> Decimal:
            return sum((getattr(r, attr) for r in rows), Decimal("0"))

        total_spend = _sum("current_annual_spend")
        total_addressable = _sum("addressable_spend")
        effective_scope = (
            (total_addressable / total_spend).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
            if total_spend
            else Decimal("0")
        )

        return TowerSavingsRow(
            tower="TOTAL",
            current_annual_spend=total_spend,
            current_vendor_count=sum(r.current_vendor_count for r in rows),
            consolidation_scope_pct=effective_scope,
            addressable_spend=total_addressable,
            productivity_savings=_sum("productivity_savings"),
            rate_savings=_sum("rate_savings"),
            vendor_mgmt_overhead_savings=_sum("vendor_mgmt_overhead_savings"),
            gross_annual_savings=_sum("gross_annual_savings"),
            transition_cost=_sum("transition_cost"),
            net_year_1_savings=_sum("net_year_1_savings"),
            run_rate_annual_savings=_sum("run_rate_annual_savings"),
        )

    # Function: calculate_with_overrides
    def calculate_with_overrides(
        self,
        vendor_records: List[VendorSpendRecord],
        inputs: InputAssumptions,
        tower_params: List[TowerParam],
        rate_compression_pct: Decimal,
        productivity_improvement_pct: Decimal,
        transition_cost_pct: Decimal,
        tower_scope_overrides: Dict[str, Decimal],
    ) -> TowerModelResult:
        """Calculate tower model with scenario overrides."""
        # Build a modified inputs object
        modified_inputs = inputs.model_copy(update={
            "default_rate_compression_pct": rate_compression_pct,
            "default_productivity_improvement_pct": productivity_improvement_pct,
            "one_time_transition_cost_pct": transition_cost_pct,
        })

        # Apply tower scope overrides
        modified_params = []
        for param in tower_params:
            override = tower_scope_overrides.get(param.tower)
            if override is not None:
                modified_params.append(param.model_copy(update={"consolidation_scope_pct": override}))
            else:
                modified_params.append(param)

        return self.calculate_model(vendor_records, modified_inputs, modified_params)
