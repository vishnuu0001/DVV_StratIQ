# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: SSDLC_Process_Assessment — csm_backend/app/services (vendor_landscape_service.py)
# Date: 2026-04-20
# ---------------------------------------------------------------------------
from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Dict, List

from app.models.vendor_spend import VendorSpendRecord


class VendorLandscapeService:
    """Analyse vendor landscape: signals, treatment, share."""

    # Function: _consolidation_signal
    def _consolidation_signal(self, annual_spend: Decimal) -> str:
        if annual_spend > Decimal("5000000"):
            return "High"
        elif annual_spend > Decimal("1000000"):
            return "Medium"
        return "Low"

    # Function: _strategic_relevance
    def _strategic_relevance(self, spend_category: str) -> str:
        cat = spend_category.strip().lower()
        if cat in ("software", "data"):
            return "Platform / Data"
        return "Labor / Services"

    # Function: _recommended_treatment
    def _recommended_treatment(self, signal: str) -> str:
        if signal == "High":
            return "Strategic review"
        elif signal == "Medium":
            return "Rationalize / bundle"
        return "Long-tail consolidation"

    # Function: analyse
    def analyse(self, records: List[VendorSpendRecord]) -> List[Dict[str, Any]]:
        total_spend = sum((r.annual_spend for r in records), Decimal("0"))

        # Aggregate by vendor
        vendor_spend: Dict[str, Decimal] = {}
        vendor_category: Dict[str, str] = {}
        vendor_tower: Dict[str, str] = {}
        for r in records:
            vendor_spend[r.vendor] = vendor_spend.get(r.vendor, Decimal("0")) + r.annual_spend
            if r.vendor not in vendor_category:
                vendor_category[r.vendor] = r.spend_category
                vendor_tower[r.vendor] = r.tower

        # Rank by spend descending
        sorted_vendors = sorted(vendor_spend.items(), key=lambda x: x[1], reverse=True)
        all_spends = [spend for _, spend in sorted_vendors]

        result = []
        for rank, (vendor, spend) in enumerate(sorted_vendors, 1):
            share = (spend / total_spend).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP) if total_spend else Decimal("0")
            signal = self._consolidation_signal(spend)
            relevance = self._strategic_relevance(vendor_category.get(vendor, ""))
            treatment = self._recommended_treatment(signal)

            result.append({
                "rank": rank,
                "vendor": vendor,
                "annual_spend": str(spend),
                "annual_spend_fmt": f"${spend / Decimal('1000000'):.2f}M",
                "share_of_third_party_spend": str(share),
                "share_pct_fmt": f"{(share * 100).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)}%",
                "spend_category": vendor_category.get(vendor, ""),
                "tower": vendor_tower.get(vendor, ""),
                "consolidation_signal": signal,
                "strategic_relevance": relevance,
                "recommended_treatment": treatment,
            })

        audit: Dict[str, Any] = {
            "service": "VendorLandscapeService",
            "total_vendors": len(result),
            "total_spend": str(total_spend),
            "signal_distribution": {
                "High": sum(1 for r in result if r["consolidation_signal"] == "High"),
                "Medium": sum(1 for r in result if r["consolidation_signal"] == "Medium"),
                "Low": sum(1 for r in result if r["consolidation_signal"] == "Low"),
            },
        }

        return result, audit
