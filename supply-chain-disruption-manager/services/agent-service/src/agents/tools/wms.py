# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: WMS (Warehouse Management System) tool mocks.
# Date: 2026-01-15
# ---------------------------------------------------------------------------
"""WMS (Warehouse Management System) tool mocks."""
from __future__ import annotations

import asyncio
import uuid


# Function: wms_bin_query
async def wms_bin_query(material_id: str) -> dict:
    """Query bin locations and stock for a material."""
    await asyncio.sleep(0)
    return {
        "material_id": material_id,
        "warehouse_id": "WH-001",
        "bins": [
            {"bin_id": "BIN-A01-03", "zone": "A", "qty": 150, "uom": "KG", "reserved_qty": 50},
            {"bin_id": "BIN-A02-07", "zone": "A", "qty": 200, "uom": "KG", "reserved_qty": 0},
            {"bin_id": "BIN-B04-01", "zone": "B", "qty": 80, "uom": "KG", "reserved_qty": 0},
        ],
        "total_qty": 430,
        "available_qty": 380,
    }


# Function: wms_grn_create
async def wms_grn_create(
    po_id: str,
    material_id: str,
    received_qty: float,
    expected_qty: float,
    notes: str = "",
) -> dict:
    """Create a Goods Receipt Note in WMS."""
    await asyncio.sleep(0)
    grn_id = f"GRN-{str(uuid.uuid4())[:8].upper()}"
    return {
        "grn_id": grn_id,
        "po_id": po_id,
        "material_id": material_id,
        "received_qty": received_qty,
        "expected_qty": expected_qty,
        "short_qty": max(0, expected_qty - received_qty),
        "status": "POSTED" if received_qty >= expected_qty else "SHORT",
        "notes": notes,
        "created_at": "2026-06-27T10:00:00Z",
    }


# Function: wms_inventory_reserve
async def wms_inventory_reserve(sku_id: str, qty: float, order_id: str) -> dict:
    """Reserve inventory for a production or sales order."""
    await asyncio.sleep(0)
    return {
        "sku_id": sku_id,
        "order_id": order_id,
        "requested_qty": qty,
        "reserved_qty": qty,
        "reservation_id": f"RES-{order_id}-{str(uuid.uuid4())[:6].upper()}",
        "status": "CONFIRMED",
        "reserved_at": "2026-06-27T10:00:00Z",
    }


# Function: wms_putaway_suggest
async def wms_putaway_suggest(material_id: str, qty: float) -> dict:
    """Get putaway bin suggestion for received material."""
    await asyncio.sleep(0)
    return {
        "material_id": material_id,
        "qty": qty,
        "suggested_bin": "BIN-A01-04",
        "zone": "A",
        "reason": "Nearest empty bin in same zone as existing stock",
        "alternative_bins": ["BIN-A02-08", "BIN-C01-02"],
    }


# Function: wms_transfer_order_create
async def wms_transfer_order_create(
    from_location: str,
    to_location: str,
    material_id: str,
    qty: float,
) -> dict:
    """Create an inter-DC transfer order."""
    await asyncio.sleep(0)
    to_id = f"TO-{str(uuid.uuid4())[:8].upper()}"
    return {
        "transfer_order_id": to_id,
        "from_location": from_location,
        "to_location": to_location,
        "material_id": material_id,
        "qty": qty,
        "status": "CREATED",
        "expected_arrival": "2026-06-28T17:00:00Z",
        "transport_mode": "INTERNAL_TRUCK",
    }


# Function: wms_pick_confirm
async def wms_pick_confirm(pick_list_id: str, picked_qty: float) -> dict:
    """Confirm pick from a pick list."""
    await asyncio.sleep(0)
    return {
        "pick_list_id": pick_list_id,
        "picked_qty": picked_qty,
        "status": "CONFIRMED",
        "confirmed_at": "2026-06-27T11:00:00Z",
    }
