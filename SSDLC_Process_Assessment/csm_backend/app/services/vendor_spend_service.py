# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: SSDLC_Process_Assessment — csm_backend/app/services (vendor_spend_service.py)
# Date: 2025-09-24
# ---------------------------------------------------------------------------
from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Dict, List

from app.models.vendor_spend import VendorSpendRecord, SpendBreakdown, VendorSpendSummary


class VendorSpendService:
    """Aggregate and summarise vendor spend records."""

    # Function: total_spend
    def total_spend(self, records: List[VendorSpendRecord]) -> Decimal:
        return sum((r.annual_spend for r in records), Decimal("0"))

    # Function: spend_by_tower
    def spend_by_tower(self, records: List[VendorSpendRecord]) -> Dict[str, Decimal]:
        result: Dict[str, Decimal] = {}
        for r in records:
            result[r.tower] = result.get(r.tower, Decimal("0")) + r.annual_spend
        return result

    # Function: spend_by_category
    def spend_by_category(self, records: List[VendorSpendRecord]) -> Dict[str, Decimal]:
        result: Dict[str, Decimal] = {}
        for r in records:
            result[r.spend_category] = result.get(r.spend_category, Decimal("0")) + r.annual_spend
        return result

    # Function: vendor_count_by_tower
    def vendor_count_by_tower(self, records: List[VendorSpendRecord]) -> Dict[str, int]:
        result: Dict[str, int] = {}
        for r in records:
            result[r.tower] = result.get(r.tower, 0) + 1
        return result

    # Function: talent_spend
    def talent_spend(self, records: List[VendorSpendRecord]) -> Decimal:
        return sum(
            (r.annual_spend for r in records if r.spend_category.strip().lower() == "talent"),
            Decimal("0"),
        )

    # Function: software_spend
    def software_spend(self, records: List[VendorSpendRecord]) -> Decimal:
        return sum(
            (r.annual_spend for r in records if r.spend_category.strip().lower() == "software"),
            Decimal("0"),
        )

    # Function: summarise
    def summarise(self, records: List[VendorSpendRecord]) -> VendorSpendSummary:
        total = self.total_spend(records)

        by_cat_raw = self.spend_by_category(records)
        by_tower_raw = self.spend_by_tower(records)

        # Function: build_breakdowns
        def build_breakdowns(mapping: Dict[str, Decimal]) -> List[SpendBreakdown]:
            items = []
            for name, spend in sorted(mapping.items(), key=lambda x: x[1], reverse=True):
                pct = (spend / total).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP) if total else Decimal("0")
                cat_count = sum(1 for r in records if r.spend_category == name or r.tower == name)
                items.append(SpendBreakdown(category=name, total_spend=spend, vendor_count=cat_count, pct_of_total=pct))
            return items

        by_cat_breakdowns = []
        for name, spend in sorted(by_cat_raw.items(), key=lambda x: x[1], reverse=True):
            pct = (spend / total).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP) if total else Decimal("0")
            count = sum(1 for r in records if r.spend_category == name)
            by_cat_breakdowns.append(SpendBreakdown(category=name, total_spend=spend, vendor_count=count, pct_of_total=pct))

        by_tower_breakdowns = []
        for name, spend in sorted(by_tower_raw.items(), key=lambda x: x[1], reverse=True):
            pct = (spend / total).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP) if total else Decimal("0")
            count = sum(1 for r in records if r.tower == name)
            by_tower_breakdowns.append(SpendBreakdown(category=name, total_spend=spend, vendor_count=count, pct_of_total=pct))

        unique_vendors = len({r.vendor for r in records})

        return VendorSpendSummary(
            total_spend=total,
            vendor_count=len(records),
            unique_vendors=unique_vendors,
            by_category=by_cat_breakdowns,
            by_tower=by_tower_breakdowns,
        )

    # Function: top_vendors
    def top_vendors(self, records: List[VendorSpendRecord], n: int = 10) -> List[Dict[str, Any]]:
        total = self.total_spend(records)
        aggregated: Dict[str, Decimal] = {}
        categories: Dict[str, str] = {}
        for r in records:
            aggregated[r.vendor] = aggregated.get(r.vendor, Decimal("0")) + r.annual_spend
            if r.vendor not in categories:
                categories[r.vendor] = r.spend_category
        sorted_vendors = sorted(aggregated.items(), key=lambda x: x[1], reverse=True)[:n]
        result = []
        for rank, (vendor, spend) in enumerate(sorted_vendors, 1):
            pct = (spend / total).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP) if total else Decimal("0")
            result.append({
                "rank": rank,
                "vendor": vendor,
                "annual_spend": str(spend),
                "pct_of_total": str(pct),
                "spend_category": categories.get(vendor, ""),
            })
        return result
