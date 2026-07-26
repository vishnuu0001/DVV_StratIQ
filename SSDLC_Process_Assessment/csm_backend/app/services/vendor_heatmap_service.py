# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: SSDLC_Process_Assessment — csm_backend/app/services (vendor_heatmap_service.py)
# Date: 2026-06-25
# ---------------------------------------------------------------------------
from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Dict, List

from app.models.vendor_spend import VendorSpendRecord

# Static heatmap parameters per tower
TOWER_HEATMAP_PARAMS: Dict[str, Dict[str, int]] = {
    "Applications":            {"strategic_importance": 5, "complexity": 5},
    "Infrastructure":          {"strategic_importance": 4, "complexity": 4},
    "Data & AI":               {"strategic_importance": 5, "complexity": 5},
    "Workplace/Productivity":  {"strategic_importance": 4, "complexity": 3},
    "Cross-Tower Labor":       {"strategic_importance": 4, "complexity": 4},
    "Other":                   {"strategic_importance": 2, "complexity": 4},
}

DEFAULT_TOWER_HEATMAP_PARAMS = {"strategic_importance": 3, "complexity": 3}


class VendorHeatmapService:
    """Calculate consolidation priority scores and RAG status per tower."""

    # Function: calculate_score
    def calculate_score(
        self,
        spend: Decimal,
        vendor_count: int,
        strategic_importance: int,
        complexity: int,
    ) -> Decimal:
        score = (
            (spend / Decimal("1000000")) * Decimal("0.4")
            + Decimal(str(vendor_count)) * Decimal("0.3")
            + Decimal(str(strategic_importance)) * Decimal("0.15")
            + Decimal(str(complexity)) * Decimal("0.15")
        )
        return score.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    # Function: rag_status
    def rag_status(self, score: Decimal) -> str:
        if score >= Decimal("8"):
            return "Red"
        elif score >= Decimal("5"):
            return "Amber"
        return "Green"

    # Function: calculate
    def calculate(self, records: List[VendorSpendRecord]) -> Dict[str, Any]:
        # Group spend & counts by tower
        tower_spend: Dict[str, Decimal] = {}
        tower_count: Dict[str, int] = {}
        for r in records:
            tower_spend[r.tower] = tower_spend.get(r.tower, Decimal("0")) + r.annual_spend
            tower_count[r.tower] = tower_count.get(r.tower, 0) + 1

        heatmap_rows = []
        for tower_name in sorted(tower_spend.keys()):
            spend = tower_spend[tower_name]
            count = tower_count.get(tower_name, 0)
            params = TOWER_HEATMAP_PARAMS.get(tower_name, DEFAULT_TOWER_HEATMAP_PARAMS)
            strategic_importance = params["strategic_importance"]
            complexity = params["complexity"]

            score = self.calculate_score(spend, count, strategic_importance, complexity)
            rag = self.rag_status(score)

            heatmap_rows.append({
                "tower": tower_name,
                "annual_spend": str(spend),
                "annual_spend_fmt": f"${spend / Decimal('1000000'):.1f}M",
                "vendor_count": count,
                "strategic_importance": strategic_importance,
                "complexity": complexity,
                "consolidation_priority_score": str(score),
                "rag_status": rag,
                "score_breakdown": {
                    "spend_component": str((spend / Decimal("1000000") * Decimal("0.4")).quantize(Decimal("0.01"))),
                    "count_component": str((Decimal(str(count)) * Decimal("0.3")).quantize(Decimal("0.01"))),
                    "strategic_component": str((Decimal(str(strategic_importance)) * Decimal("0.15")).quantize(Decimal("0.01"))),
                    "complexity_component": str((Decimal(str(complexity)) * Decimal("0.15")).quantize(Decimal("0.01"))),
                },
            })

        # Sort by score descending
        heatmap_rows.sort(key=lambda x: Decimal(x["consolidation_priority_score"]), reverse=True)

        audit: Dict[str, Any] = {
            "service": "VendorHeatmapService",
            "formula": "score = (spend_M × 0.4) + (vendor_count × 0.3) + (strategic_importance × 0.15) + (complexity × 0.15)",
            "rag_thresholds": {"Red": "score >= 8", "Amber": "score >= 5", "Green": "score < 5"},
        }

        return {
            "heatmap": heatmap_rows,
            "rag_summary": {
                "Red": sum(1 for r in heatmap_rows if r["rag_status"] == "Red"),
                "Amber": sum(1 for r in heatmap_rows if r["rag_status"] == "Amber"),
                "Green": sum(1 for r in heatmap_rows if r["rag_status"] == "Green"),
            },
            "calculation_audit": audit,
        }
