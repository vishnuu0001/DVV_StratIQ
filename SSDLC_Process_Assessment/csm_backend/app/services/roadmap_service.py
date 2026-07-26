# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: SSDLC_Process_Assessment — csm_backend/app/services (roadmap_service.py)
# Date: 2025-09-29
# ---------------------------------------------------------------------------
from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Dict, List

from app.models.inputs import InputAssumptions
from app.models.tower_model import TowerModelResult


class RoadmapService:
    """Generate a phased consolidation roadmap from tower model results."""

    # Function: generate
    def generate(
        self,
        tower_result: TowerModelResult,
        inputs: InputAssumptions,
    ) -> Dict[str, Any]:
        rows = [r for r in tower_result.rows if r.tower != "TOTAL"]
        duration_months = int(inputs.default_transition_duration_months)

        # Sort towers by gross savings descending → Phase 1 gets highest-value towers first
        sorted_rows = sorted(rows, key=lambda r: r.gross_annual_savings, reverse=True)

        phase1 = sorted_rows[:2]  # Months 1-6
        phase2 = sorted_rows[2:4]  # Months 7-12
        phase3 = sorted_rows[4:]  # Months 13-18

        # Function: _phase_dict
        def _phase_dict(phase_rows: list, phase_num: int, start_m: int, end_m: int) -> Dict[str, Any]:
            gross = sum(r.gross_annual_savings for r in phase_rows) or Decimal("0")
            tc = sum(r.transition_cost for r in phase_rows) or Decimal("0")
            net = gross - tc
            return {
                "phase": phase_num,
                "label": f"Phase {phase_num}: Months {start_m}-{end_m}",
                "towers": [r.tower for r in phase_rows],
                "gross_savings": str(gross),
                "gross_savings_fmt": f"${gross / Decimal('1000000'):.2f}M",
                "transition_cost": str(tc),
                "transition_cost_fmt": f"${tc / Decimal('1000000'):.2f}M",
                "net_savings": str(net),
                "net_savings_fmt": f"${net / Decimal('1000000'):.2f}M",
                "activities": _phase_activities(phase_rows, phase_num),
            }

        # Function: _phase_activities
        def _phase_activities(phase_rows: list, phase_num: int) -> List[str]:
            base = {
                1: ["Vendor assessment & RFP for priority towers", "Preferred vendor selection", "Contract renegotiation launch"],
                2: ["Transition execution for Phase 1 towers", "Onboarding new preferred vendors", "Performance baseline establishment"],
                3: ["Full consolidation for remaining towers", "Contract terminations", "Steady-state governance model"],
            }
            activities = list(base.get(phase_num, []))
            for r in phase_rows:
                activities.append(f"Consolidate {r.tower} tower ({r.current_vendor_count} vendors → preferred model)")
            return activities

        phases = [
            _phase_dict(phase1, 1, 1, 6),
            _phase_dict(phase2, 2, 7, 12),
            _phase_dict(phase3, 3, 13, 18),
        ]

        milestones = [
            {"month": 1,  "milestone": "Programme kickoff & governance established"},
            {"month": 3,  "milestone": "Vendor RFPs issued for Phase 1 towers"},
            {"month": 6,  "milestone": "Phase 1 preferred vendors contracted"},
            {"month": 9,  "milestone": "Phase 1 consolidation complete; Phase 2 underway"},
            {"month": 12, "milestone": "Phase 2 complete; Year-1 savings realised"},
            {"month": 18, "milestone": "Full consolidation complete; run-rate savings active"},
        ]

        totals = tower_result.totals
        return {
            "phases": phases,
            "milestones": milestones,
            "total_duration_months": 18,
            "total_gross_savings": str(totals.gross_annual_savings),
            "total_transition_cost": str(totals.transition_cost),
            "total_net_year_1": str(totals.net_year_1_savings),
            "calculation_audit": {
                "service": "RoadmapService",
                "prioritisation": "Towers sorted by gross_annual_savings descending; top 2 in Phase 1, next 2 in Phase 2, remainder in Phase 3.",
            },
        }
