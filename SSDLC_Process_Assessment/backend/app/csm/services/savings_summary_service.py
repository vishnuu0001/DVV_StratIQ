# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: SSDLC_Process_Assessment — backend/app/csm/services (savings_summary_service.py)
# Date: 2025-10-18
# ---------------------------------------------------------------------------
from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Dict, List

from app.csm.models.tower_model import TowerModelResult, TowerSavingsRow


# Function: _fmt_currency
def _fmt_currency(value: Decimal) -> str:
    millions = value / Decimal("1000000")
    return f"${millions.quantize(Decimal('0.001')).normalize()}M"


class SavingsSummaryService:
    """Produce high-level savings summary from tower model results."""

    # Function: summarise
    def summarise(self, result: TowerModelResult) -> Dict[str, Any]:
        totals = result.totals
        rows_data = []
        for row in result.rows:
            rows_data.append({
                "tower": row.tower,
                "current_annual_spend": str(row.current_annual_spend),
                "current_annual_spend_fmt": _fmt_currency(row.current_annual_spend),
                "vendor_count": row.current_vendor_count,
                "consolidation_scope_pct": str(row.consolidation_scope_pct),
                "addressable_spend": str(row.addressable_spend),
                "addressable_spend_fmt": _fmt_currency(row.addressable_spend),
                "gross_annual_savings": str(row.gross_annual_savings),
                "gross_annual_savings_fmt": _fmt_currency(row.gross_annual_savings),
                "transition_cost": str(row.transition_cost),
                "transition_cost_fmt": _fmt_currency(row.transition_cost),
                "net_year_1_savings": str(row.net_year_1_savings),
                "net_year_1_savings_fmt": _fmt_currency(row.net_year_1_savings),
                "run_rate_annual_savings": str(row.run_rate_annual_savings),
                "run_rate_annual_savings_fmt": _fmt_currency(row.run_rate_annual_savings),
            })

        roi_pct = Decimal("0")
        if totals.transition_cost and totals.transition_cost != Decimal("0"):
            roi_pct = (totals.net_year_1_savings / totals.transition_cost * 100).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )

        return {
            "rows": rows_data,
            "totals": {
                "current_annual_spend": str(totals.current_annual_spend),
                "current_annual_spend_fmt": _fmt_currency(totals.current_annual_spend),
                "addressable_spend": str(totals.addressable_spend),
                "addressable_spend_fmt": _fmt_currency(totals.addressable_spend),
                "gross_annual_savings": str(totals.gross_annual_savings),
                "gross_annual_savings_fmt": _fmt_currency(totals.gross_annual_savings),
                "transition_cost": str(totals.transition_cost),
                "transition_cost_fmt": _fmt_currency(totals.transition_cost),
                "net_year_1_savings": str(totals.net_year_1_savings),
                "net_year_1_savings_fmt": _fmt_currency(totals.net_year_1_savings),
                "run_rate_annual_savings": str(totals.run_rate_annual_savings),
                "run_rate_annual_savings_fmt": _fmt_currency(totals.run_rate_annual_savings),
                "roi_pct": str(roi_pct),
                "roi_pct_fmt": f"{roi_pct:.1f}%",
            },
            "calculation_audit": result.calculation_audit,
        }
