# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: TMS (Transportation Management System) tool mocks.
# Date: 2026-02-20
# ---------------------------------------------------------------------------
"""TMS (Transportation Management System) tool mocks."""
from __future__ import annotations

import asyncio


# Function: tms_shipment_get
async def tms_shipment_get(shipment_id: str) -> dict:
    """Fetch shipment details from TMS."""
    await asyncio.sleep(0)
    return {
        "shipment_id": shipment_id,
        "status": "IN_TRANSIT",
        "carrier": "DHL Express",
        "carrier_id": "CARRIER-DHL-001",
        "origin": "Shanghai, CN",
        "destination": "Central DC, Chicago IL",
        "mode": "SEA",
        "container_id": "CONT-20FT-8832",
        "weight_kg": 12500,
        "eta": "2026-07-15T18:00:00Z",
        "last_event": {"location": "Pacific Ocean", "timestamp": "2026-06-26T12:00:00Z", "status": "On route"},
    }


# Function: tms_shipment_reroute
async def tms_shipment_reroute(shipment_id: str, mode: str) -> dict:
    """Reroute a shipment to faster mode."""
    await asyncio.sleep(0)
    mode_etas = {"FASTEST": "2026-07-09T18:00:00Z", "AIR": "2026-07-05T12:00:00Z", "RAIL": "2026-07-12T08:00:00Z"}
    return {
        "shipment_id": shipment_id,
        "reroute_requested": True,
        "new_mode": mode,
        "estimated_new_eta": mode_etas.get(mode, "2026-07-10T12:00:00Z"),
        "cost_delta_usd": 3500 if mode == "AIR" else 800,
        "status": "REROUTE_PENDING",
    }


# Function: tms_carrier_book
async def tms_carrier_book(carrier_id: str, shipment_id: str, service: str) -> dict:
    """Book a carrier for a shipment."""
    await asyncio.sleep(0)
    return {
        "booking_id": f"BKG-{carrier_id}-{shipment_id[:8]}",
        "carrier_id": carrier_id,
        "shipment_id": shipment_id,
        "service": service,
        "confirmed": True,
        "pickup_date": "2026-06-28T09:00:00Z",
        "estimated_delivery": "2026-07-06T17:00:00Z",
        "cost_usd": 2800 if service == "EXPRESS" else 1200,
    }


# Function: tms_customs_status
async def tms_customs_status(shipment_id: str) -> dict:
    """Get customs hold status for a shipment."""
    await asyncio.sleep(0)
    return {
        "shipment_id": shipment_id,
        "status": "ON_HOLD",
        "hold_reason": "Missing HS code classification on 3 line items",
        "customs_office": "Los Angeles CBP",
        "hold_since": "2026-06-25T14:00:00Z",
        "documents_required": ["HS_CODE_FORM", "COMMERCIAL_INVOICE_REVISED"],
        "broker_assigned": "FastClear Customs LLC",
        "estimated_release": "2026-06-29T12:00:00Z",
    }


# Function: tms_eta_update
async def tms_eta_update(shipment_id: str, new_eta: str) -> dict:
    """Update the ETA of a shipment in TMS."""
    await asyncio.sleep(0)
    return {
        "shipment_id": shipment_id,
        "old_eta": "2026-07-15T18:00:00Z",
        "new_eta": new_eta,
        "updated": True,
        "notifications_sent": ["warehouse-manager@example.com", "planning@example.com"],
    }


# Function: tms_tracking_events
async def tms_tracking_events(shipment_id: str) -> list[dict]:
    """Get recent tracking events for a shipment."""
    await asyncio.sleep(0)
    return [
        {"timestamp": "2026-06-26T12:00:00Z", "location": "Pacific Ocean", "event": "En route"},
        {"timestamp": "2026-06-20T08:00:00Z", "location": "Shanghai Port", "event": "Departed"},
        {"timestamp": "2026-06-18T14:00:00Z", "location": "Shanghai Warehouse", "event": "Loaded"},
    ]
