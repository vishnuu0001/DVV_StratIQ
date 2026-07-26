# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: MRP (Material Requirements Planning) tool mocks.
# Date: 2025-08-30
# ---------------------------------------------------------------------------
"""MRP (Material Requirements Planning) tool mocks."""
from __future__ import annotations

import asyncio


# Function: mrp_stock_query
async def mrp_stock_query(material_id: str) -> dict:
    """Query current stock levels from MRP/ERP."""
    await asyncio.sleep(0)
    return {
        "material_id": material_id,
        "on_hand_qty": 430,
        "unit": "KG",
        "in_transit_qty": 500,
        "reserved_qty": 200,
        "available_qty": 230,
        "safety_stock_qty": 150,
        "reorder_point": 200,
        "last_updated": "2026-06-27T06:00:00Z",
    }


# Function: mrp_safety_stock_check
async def mrp_safety_stock_check(material_id: str) -> dict:
    """Check if material is below safety stock level."""
    await asyncio.sleep(0)
    return {
        "material_id": material_id,
        "on_hand_qty": 430,
        "safety_stock_qty": 150,
        "safety_stock_days": 14,
        "below_safety_stock": False,
        "days_of_coverage": 23.0,
        "coverage_risk": "LOW",
    }


# Function: mrp_reorder_suggest
async def mrp_reorder_suggest(material_id: str, target_days: int) -> dict:
    """Suggest reorder quantity to cover target days."""
    await asyncio.sleep(0)
    daily_consumption = 18.7
    on_hand = 430
    suggested_qty = max(0, (target_days * daily_consumption) - on_hand)
    return {
        "material_id": material_id,
        "target_days": target_days,
        "suggested_order_qty": round(suggested_qty, 0),
        "unit": "KG",
        "recommended_supplier": "SUP-001",
        "estimated_lead_time_days": 14,
        "estimated_cost_usd": suggested_qty * 90.0,
        "urgency": "HIGH" if target_days <= 14 else "NORMAL",
    }


# Function: mrp_consumption_forecast
async def mrp_consumption_forecast(material_id: str, days: int = 30) -> dict:
    """Get consumption forecast for material."""
    await asyncio.sleep(0)
    daily_avg = 18.7
    return {
        "material_id": material_id,
        "forecast_days": days,
        "daily_avg_consumption": daily_avg,
        "total_forecast_qty": daily_avg * days,
        "unit": "KG",
        "peak_day": "2026-07-15",
        "peak_day_consumption": 35.0,
        "confidence": 0.82,
    }


# Function: mrp_production_plan_get
async def mrp_production_plan_get(plan_id: str) -> dict:
    """Get the active production plan."""
    await asyncio.sleep(0)
    return {
        "plan_id": plan_id,
        "period": "2026-Q3",
        "status": "ACTIVE",
        "total_orders": 45,
        "completed_orders": 12,
        "in_progress_orders": 5,
        "pending_orders": 28,
        "revenue_plan_usd": 1_250_000,
        "key_materials": ["MAT-RAW-001", "MAT-RAW-002", "MAT-COMP-005"],
        "critical_path_orders": ["PRD-2026-0081", "PRD-2026-0082", "PRD-2026-0090"],
    }


# Function: mrp_production_plan_revise
async def mrp_production_plan_revise(plan_id: str, changes: dict) -> dict:
    """Revise production plan based on material or capacity changes."""
    await asyncio.sleep(0)
    action = changes.get("action", "resequence")
    return {
        "plan_id": plan_id,
        "revision_applied": True,
        "action": action,
        "orders_rescheduled": 3,
        "orders_unaffected": 42,
        "revenue_at_risk_usd": 125_000,
        "capacity_utilization_pct": 88,
        "revised_at": "2026-06-27T10:00:00Z",
        "notes": f"Plan revised: {action}",
    }


# Function: mrp_demand_signal_get
async def mrp_demand_signal_get(sku_id: str) -> dict:
    """Get current demand signal / forecast for a SKU."""
    await asyncio.sleep(0)
    return {
        "sku_id": sku_id,
        "forecast_30d": 850,
        "forecast_60d": 1700,
        "forecast_90d": 2600,
        "actual_orders_open": 420,
        "forecast_vs_actual_variance_pct": 12.5,
        "demand_trend": "INCREASING",
        "last_updated": "2026-06-26T23:00:00Z",
    }
