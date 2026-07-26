# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: SSDLC_Process_Assessment — backend/app/csm/services (executive_dashboard_service.py)
# Date: 2026-05-23
# ---------------------------------------------------------------------------
from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Dict, List

from app.csm.models.dashboard import (
    ExecutiveDashboardKpis,
    ExecutiveStoryBullet,
    DashboardResponse,
)
from app.csm.models.inputs import InputAssumptions
from app.csm.models.tower_model import TowerModelResult, TowerSavingsRow
from app.csm.models.vendor_spend import VendorSpendRecord


# Function: format_currency_compact
def format_currency_compact(value: Decimal) -> str:
    millions = value / Decimal("1000000")
    return f"${millions.quantize(Decimal('0.001')).normalize()}M"


# Function: format_pct
def format_pct(value: Decimal) -> str:
    return f"{(value * 100).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)}%"


class ExecutiveDashboardService:
    """Build executive dashboard KPIs and narrative from tower model results."""

    # Function: build
    def build(
        self,
        workbook_id: str,
        vendor_records: List[VendorSpendRecord],
        tower_result: TowerModelResult,
        inputs: InputAssumptions,
        validation: List[str],
    ) -> DashboardResponse:
        totals = tower_result.totals

        total_third_party_spend = sum((r.annual_spend for r in vendor_records), Decimal("0"))
        external_talent_spend = sum(
            (r.annual_spend for r in vendor_records if r.spend_category.strip().lower() == "talent"),
            Decimal("0"),
        )

        addressable_spend = totals.addressable_spend
        gross_annual_capacity = totals.gross_annual_savings
        transition_cost = totals.transition_cost
        net_year_1 = totals.net_year_1_savings
        run_rate = totals.run_rate_annual_savings

        roi_pct = Decimal("0")
        if transition_cost and transition_cost != Decimal("0"):
            roi_pct = (net_year_1 / transition_cost).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)

        kpis = ExecutiveDashboardKpis(
            total_third_party_spend=total_third_party_spend,
            total_third_party_spend_fmt=format_currency_compact(total_third_party_spend),
            external_talent_spend=external_talent_spend,
            external_talent_spend_fmt=format_currency_compact(external_talent_spend),
            addressable_spend=addressable_spend,
            addressable_spend_fmt=format_currency_compact(addressable_spend),
            gross_annual_capacity=gross_annual_capacity,
            gross_annual_capacity_fmt=format_currency_compact(gross_annual_capacity),
            transition_cost=transition_cost,
            transition_cost_fmt=format_currency_compact(transition_cost),
            net_year_1_savings=net_year_1,
            net_year_1_savings_fmt=format_currency_compact(net_year_1),
            run_rate_annual_savings=run_rate,
            run_rate_annual_savings_fmt=format_currency_compact(run_rate),
            roi_pct=roi_pct,
            roi_pct_fmt=format_pct(roi_pct),
        )

        # Tower summary table
        tower_summary = []
        for row in tower_result.rows:
            tower_summary.append({
                "tower": row.tower,
                "current_annual_spend": str(row.current_annual_spend),
                "current_annual_spend_fmt": format_currency_compact(row.current_annual_spend),
                "vendor_count": row.current_vendor_count,
                "consolidation_scope_pct": str(row.consolidation_scope_pct),
                "addressable_spend": str(row.addressable_spend),
                "addressable_spend_fmt": format_currency_compact(row.addressable_spend),
                "gross_annual_savings": str(row.gross_annual_savings),
                "gross_annual_savings_fmt": format_currency_compact(row.gross_annual_savings),
                "transition_cost": str(row.transition_cost),
                "transition_cost_fmt": format_currency_compact(row.transition_cost),
                "net_year_1_savings": str(row.net_year_1_savings),
                "net_year_1_savings_fmt": format_currency_compact(row.net_year_1_savings),
                "run_rate_annual_savings": str(row.run_rate_annual_savings),
            })

        # Spend by category
        cat_totals: Dict[str, Decimal] = {}
        for r in vendor_records:
            cat_totals[r.spend_category] = cat_totals.get(r.spend_category, Decimal("0")) + r.annual_spend
        spend_by_cat = []
        for cat, spend in sorted(cat_totals.items(), key=lambda x: x[1], reverse=True):
            pct = (spend / total_third_party_spend).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP) if total_third_party_spend else Decimal("0")
            spend_by_cat.append({
                "category": cat,
                "total_spend": str(spend),
                "total_spend_fmt": format_currency_compact(spend),
                "pct_of_total": str(pct),
                "pct_of_total_fmt": format_pct(pct),
            })

        # Top vendors
        vendor_agg: Dict[str, Decimal] = {}
        vendor_cat: Dict[str, str] = {}
        for r in vendor_records:
            vendor_agg[r.vendor] = vendor_agg.get(r.vendor, Decimal("0")) + r.annual_spend
            if r.vendor not in vendor_cat:
                vendor_cat[r.vendor] = r.spend_category
        top_vendors = []
        for rank, (vendor, spend) in enumerate(
            sorted(vendor_agg.items(), key=lambda x: x[1], reverse=True)[:10], 1
        ):
            pct = (spend / total_third_party_spend).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP) if total_third_party_spend else Decimal("0")
            top_vendors.append({
                "rank": rank,
                "vendor": vendor,
                "annual_spend": str(spend),
                "annual_spend_fmt": format_currency_compact(spend),
                "pct_of_total": str(pct),
                "pct_of_total_fmt": format_pct(pct),
                "spend_category": vendor_cat.get(vendor, ""),
            })

        executive_story = self._build_story(kpis, totals, total_third_party_spend)

        audit: Dict[str, Any] = {
            "service": "ExecutiveDashboardService",
            "formulas": [
                {
                    "name": "total_third_party_spend",
                    "expression": "sum(r.annual_spend for r in vendor_records)",
                    "result": str(total_third_party_spend),
                },
                {
                    "name": "external_talent_spend",
                    "expression": "sum(r.annual_spend for r in vendor_records if r.spend_category == 'Talent')",
                    "result": str(external_talent_spend),
                },
                {
                    "name": "addressable_spend",
                    "expression": "sum(row.addressable_spend for row in tower_rows)",
                    "result": str(addressable_spend),
                },
                {
                    "name": "gross_annual_capacity",
                    "expression": "sum(row.gross_annual_savings for row in tower_rows)",
                    "result": str(gross_annual_capacity),
                },
                {
                    "name": "transition_cost",
                    "expression": "sum(row.transition_cost for row in tower_rows)",
                    "result": str(transition_cost),
                },
                {
                    "name": "net_year_1_savings",
                    "expression": "gross_annual_capacity - transition_cost",
                    "result": str(net_year_1),
                },
                {
                    "name": "roi_pct",
                    "expression": "net_year_1_savings / transition_cost",
                    "result": str(roi_pct),
                },
            ],
        }

        return DashboardResponse(
            workbook_id=workbook_id,
            kpis=kpis,
            tower_summary=tower_summary,
            spend_by_category=spend_by_cat,
            top_vendors=top_vendors,
            executive_story=executive_story,
            calculation_audit=audit,
            validation=validation,
        )

    # Function: _build_story
    def _build_story(
        self,
        kpis: ExecutiveDashboardKpis,
        totals: TowerSavingsRow,
        total_third_party_spend: Decimal,
    ) -> List[ExecutiveStoryBullet]:
        addressable_pct = Decimal("0")
        if total_third_party_spend:
            addressable_pct = (kpis.addressable_spend / total_third_party_spend * 100).quantize(
                Decimal("0.1"), rounding=ROUND_HALF_UP
            )

        return [
            ExecutiveStoryBullet(
                bullet=f"Total third-party technology spend is {kpis.total_third_party_spend_fmt}, "
                       f"of which {addressable_pct}% ({kpis.addressable_spend_fmt}) is addressable through consolidation.",
                category="spend",
            ),
            ExecutiveStoryBullet(
                bullet=f"Vendor consolidation can unlock {kpis.gross_annual_capacity_fmt} in gross annual savings "
                       f"across {totals.current_vendor_count} vendor relationships.",
                category="savings",
            ),
            ExecutiveStoryBullet(
                bullet=f"After one-time transition investment of {kpis.transition_cost_fmt}, "
                       f"net Year-1 savings total {kpis.net_year_1_savings_fmt}.",
                category="transition",
            ),
            ExecutiveStoryBullet(
                bullet=f"Run-rate annual savings of {kpis.run_rate_annual_savings_fmt} represent "
                       f"ongoing capacity for strategic reinvestment.",
                category="run_rate",
            ),
            ExecutiveStoryBullet(
                bullet=f"Talent/labor vendors represent {kpis.external_talent_spend_fmt} "
                       f"({(kpis.external_talent_spend / total_third_party_spend * 100).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP) if total_third_party_spend else 0}%) "
                       f"of third-party spend — a primary consolidation target.",
                category="talent",
            ),
        ]
