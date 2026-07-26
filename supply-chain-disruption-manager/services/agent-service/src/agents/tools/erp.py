# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: ERP tool mocks — purchase orders, supplier contacts, alternates.
# Date: 2026-03-06
# ---------------------------------------------------------------------------
"""ERP tool mocks — purchase orders, supplier contacts, alternates."""
from __future__ import annotations

import asyncio


# Function: erp_po_get
async def erp_po_get(po_id: str) -> dict:
    """Fetch PO details from ERP."""
    await asyncio.sleep(0)  # simulate async I/O
    return {
        "po_id": po_id,
        "status": "OPEN",
        "supplier_id": "SUP-001",
        "total_value": 45000.00,
        "currency": "USD",
        "created_date": "2026-05-01",
        "expected_delivery": "2026-07-15",
        "lines": [
            {
                "line_id": f"{po_id}-1",
                "material_id": "MAT-RAW-001",
                "description": "Steel Coil Grade A",
                "qty": 500,
                "unit": "KG",
                "unit_price": 90.0,
            }
        ],
    }


# Function: erp_po_update_status
async def erp_po_update_status(po_id: str, new_status: str, reason: str) -> dict:
    """Update PO status in ERP."""
    await asyncio.sleep(0)
    return {
        "po_id": po_id,
        "old_status": "OPEN",
        "new_status": new_status,
        "reason": reason,
        "updated": True,
        "updated_by": "agent-service",
        "updated_at": "2026-06-27T00:00:00Z",
    }


# Function: erp_po_create
async def erp_po_create(
    supplier_id: str,
    material_id: str,
    qty: float,
    unit_price: float,
    required_by: str,
) -> dict:
    """Create emergency PO in ERP."""
    await asyncio.sleep(0)
    import uuid
    new_po_id = f"PO-EMER-{str(uuid.uuid4())[:8].upper()}"
    return {
        "po_id": new_po_id,
        "supplier_id": supplier_id,
        "material_id": material_id,
        "qty": qty,
        "unit_price": unit_price,
        "total_value": qty * unit_price,
        "required_by": required_by,
        "status": "DRAFT",
        "created": True,
    }


# Function: supplier_contact
async def supplier_contact(supplier_id: str, channel: str, message: str) -> dict:
    """Send communication to supplier."""
    await asyncio.sleep(0)
    return {
        "supplier_id": supplier_id,
        "channel": channel,
        "message_preview": message[:100],
        "sent": True,
        "reference": f"MSG-{supplier_id}-{channel.upper()}-001",
        "sent_at": "2026-06-27T00:00:00Z",
    }


# Function: sourcing_alternates
async def sourcing_alternates(material_id: str) -> dict:
    """Find alternate suppliers for a material."""
    await asyncio.sleep(0)
    return {
        "material_id": material_id,
        "alternates": [
            {
                "supplier_id": "SUP-003",
                "supplier_name": "FastMetals Ltd",
                "lead_time_days": 14,
                "unit_price": 92.50,
                "availability": "confirmed",
                "moq": 200,
                "currency": "USD",
            },
            {
                "supplier_id": "SUP-005",
                "supplier_name": "Global Raw Materials",
                "lead_time_days": 21,
                "unit_price": 88.00,
                "availability": "tentative",
                "moq": 500,
                "currency": "USD",
            },
        ],
    }


# Function: erp_grn_get
async def erp_grn_get(grn_id: str) -> dict:
    """Fetch Goods Receipt Note from ERP."""
    await asyncio.sleep(0)
    return {
        "grn_id": grn_id,
        "po_id": "PO-10001",
        "received_qty": 450,
        "expected_qty": 500,
        "short_qty": 50,
        "material_id": "MAT-RAW-001",
        "received_at": "2026-06-27T08:00:00Z",
        "status": "SHORT",
    }
