# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: MES (Manufacturing Execution System) tool mocks.
# Date: 2026-05-21
# ---------------------------------------------------------------------------
"""MES (Manufacturing Execution System) tool mocks."""
from __future__ import annotations

import asyncio
import uuid


# Function: mes_workcenter_status
async def mes_workcenter_status(workcenter_id: str) -> dict:
    """Get current status of a work center."""
    await asyncio.sleep(0)
    return {
        "workcenter_id": workcenter_id,
        "status": "STOPPED",
        "current_order": "PRD-2026-0081",
        "operator": "OP-042",
        "shift": "DAY",
        "uptime_pct_today": 45.0,
        "last_stoppage": "2026-06-27T07:30:00Z",
        "stoppage_reason": "equipment_failure",
        "maintenance_ticket": "MNT-20260627-001",
    }


# Function: mes_production_order_get
async def mes_production_order_get(prod_order_id: str) -> dict:
    """Fetch production order details from MES."""
    await asyncio.sleep(0)
    return {
        "prod_order_id": prod_order_id,
        "sku_id": "SKU-PROD-001",
        "description": "Widget A Assembly",
        "required_qty": 200,
        "completed_qty": 0,
        "status": "IN_PROCESS",
        "workcenter_id": "WC-001",
        "planned_start": "2026-06-27T06:00:00Z",
        "planned_end": "2026-06-27T22:00:00Z",
        "bom_items": [
            {"material_id": "MAT-RAW-001", "required_qty": 400, "unit": "KG"},
            {"material_id": "MAT-RAW-002", "required_qty": 100, "unit": "KG"},
        ],
    }


# Function: mes_workcenter_assign
async def mes_workcenter_assign(prod_order_id: str, workcenter_id: str) -> dict:
    """Reassign a production order to a different work center."""
    await asyncio.sleep(0)
    return {
        "prod_order_id": prod_order_id,
        "new_workcenter_id": workcenter_id,
        "old_workcenter_id": "WC-001",
        "reassigned": True,
        "reassigned_at": "2026-06-27T08:00:00Z",
        "setup_time_minutes": 45,
        "new_planned_start": "2026-06-27T09:00:00Z",
    }


# Function: mes_downtime_log
async def mes_downtime_log(
    workcenter_id: str,
    reason: str,
    duration: str = "ongoing",
) -> dict:
    """Log a downtime event for a work center."""
    await asyncio.sleep(0)
    downtime_id = f"DT-{str(uuid.uuid4())[:8].upper()}"
    return {
        "downtime_id": downtime_id,
        "workcenter_id": workcenter_id,
        "reason": reason,
        "duration": duration,
        "logged_at": "2026-06-27T07:30:00Z",
        "maintenance_notified": True,
        "estimated_recovery_minutes": 180,
    }


# Function: mes_capacity_check
async def mes_capacity_check(workcenter_ids: list[str], prod_order_id: str) -> dict:
    """Check available capacity across work centers."""
    await asyncio.sleep(0)
    results = {}
    for wc_id in workcenter_ids:
        results[wc_id] = {
            "utilization_pct": 65 if wc_id == "WC-002" else 82,
            "available_hours_today": 6 if wc_id == "WC-002" else 2,
            "can_fit_order": wc_id == "WC-002",
        }
    return {
        "prod_order_id": prod_order_id,
        "capacity_available": True,
        "recommended_workcenter": "WC-002",
        "workcenter_analysis": results,
    }


# Function: mes_shift_get
async def mes_shift_get(workcenter_id: str, date: str) -> dict:
    """Get shift schedule for a work center."""
    await asyncio.sleep(0)
    return {
        "workcenter_id": workcenter_id,
        "date": date,
        "shifts": [
            {"shift_id": "DAY", "start": "06:00", "end": "14:00", "capacity_hrs": 8, "operator_count": 3},
            {"shift_id": "EVENING", "start": "14:00", "end": "22:00", "capacity_hrs": 8, "operator_count": 2},
            {"shift_id": "NIGHT", "start": "22:00", "end": "06:00", "capacity_hrs": 8, "operator_count": 1},
        ],
    }
