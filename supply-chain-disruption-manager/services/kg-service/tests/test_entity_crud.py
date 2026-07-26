# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Tests for entity CRUD operations.
# Date: 2026-04-09
# ---------------------------------------------------------------------------
"""Tests for entity CRUD operations."""
from __future__ import annotations

from datetime import datetime, timezone

import pytest
from httpx import AsyncClient


# Function: _now
def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


SUPPLIER_PAYLOAD = {
    "id": "TEST-SUP-001",
    "kind": "Supplier",
    "domain": "procurement",
    "created_at": _now(),
    "updated_at": _now(),
    "status": "ACTIVE",
    "metadata": {},
    "name": "Test Supplier One",
    "country": "US",
    "tier": 1,
    "lead_time_days": 14,
    "reliability_score": 0.95,
    "contract_id": "CTR-TEST-001",
}

PO_PAYLOAD = {
    "id": "TEST-PO-001",
    "kind": "PurchaseOrder",
    "domain": "procurement",
    "created_at": _now(),
    "updated_at": _now(),
    "status": "OPEN",
    "metadata": {},
    "supplier_id": "TEST-SUP-001",
    "buyer_id": "USR-TEST-001",
    "currency": "USD",
    "total_value": "5000.00",
    "expected_delivery": "2025-04-01",
}


class TestSupplierCRUD:
    # Function: test_create_supplier
    async def test_create_supplier(self, client: AsyncClient) -> None:
        resp = await client.post("/entity/Supplier", json=SUPPLIER_PAYLOAD)
        assert resp.status_code == 201
        data = resp.json()
        assert data["id"] == "TEST-SUP-001"
        assert data["kind"] == "Supplier"
        assert data["name"] == "Test Supplier One"

    # Function: test_get_supplier
    async def test_get_supplier(self, client: AsyncClient) -> None:
        # Ensure it exists first
        await client.post("/entity/Supplier", json=SUPPLIER_PAYLOAD)
        resp = await client.get("/entity/Supplier/TEST-SUP-001")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == "TEST-SUP-001"
        assert data["country"] == "US"

    # Function: test_patch_supplier
    async def test_patch_supplier(self, client: AsyncClient) -> None:
        await client.post("/entity/Supplier", json=SUPPLIER_PAYLOAD)
        resp = await client.patch(
            "/entity/Supplier/TEST-SUP-001",
            json={"reliability_score": 0.99, "lead_time_days": 10},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert float(data["reliability_score"]) == pytest.approx(0.99)

    # Function: test_soft_delete_supplier
    async def test_soft_delete_supplier(self, client: AsyncClient) -> None:
        await client.post("/entity/Supplier", json=SUPPLIER_PAYLOAD)
        resp = await client.delete("/entity/Supplier/TEST-SUP-001")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "DELETED"

    # Function: test_get_not_found
    async def test_get_not_found(self, client: AsyncClient) -> None:
        resp = await client.get("/entity/Supplier/DOES-NOT-EXIST")
        assert resp.status_code == 404

    # Function: test_list_entities
    async def test_list_entities(self, client: AsyncClient) -> None:
        # Re-create as ACTIVE for listing
        payload = {**SUPPLIER_PAYLOAD, "id": "TEST-SUP-LIST-001", "status": "ACTIVE"}
        await client.post("/entity/Supplier", json=payload)
        resp = await client.get("/entity/Supplier", params={"status": "ACTIVE", "limit": 10})
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data
        assert isinstance(data["items"], list)

    # Function: test_auth_required
    async def test_auth_required(self, unauthed_client: AsyncClient) -> None:
        resp = await unauthed_client.get("/entity/Supplier/TEST-SUP-001")
        assert resp.status_code == 401


class TestPurchaseOrderCRUD:
    # Function: test_create_po
    async def test_create_po(self, client: AsyncClient) -> None:
        # Ensure supplier exists
        await client.post("/entity/Supplier", json=SUPPLIER_PAYLOAD)
        resp = await client.post("/entity/PurchaseOrder", json=PO_PAYLOAD)
        assert resp.status_code == 201
        data = resp.json()
        assert data["id"] == "TEST-PO-001"
        assert data["status"] == "OPEN"

    # Function: test_get_po
    async def test_get_po(self, client: AsyncClient) -> None:
        await client.post("/entity/PurchaseOrder", json=PO_PAYLOAD)
        resp = await client.get("/entity/PurchaseOrder/TEST-PO-001")
        assert resp.status_code == 200
        data = resp.json()
        assert data["currency"] == "USD"

    # Function: test_patch_po_status
    async def test_patch_po_status(self, client: AsyncClient) -> None:
        await client.post("/entity/PurchaseOrder", json=PO_PAYLOAD)
        resp = await client.patch(
            "/entity/PurchaseOrder/TEST-PO-001",
            json={"status": "ACK"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ACK"

    # Function: test_cursor_pagination
    async def test_cursor_pagination(self, client: AsyncClient) -> None:
        # Create multiple POs
        for i in range(2, 5):
            payload = {
                **PO_PAYLOAD,
                "id": f"TEST-PO-00{i}",
                "status": "ACTIVE",
            }
            await client.post("/entity/PurchaseOrder", json=payload)

        resp = await client.get("/entity/PurchaseOrder", params={"status": "ACTIVE", "limit": 2})
        assert resp.status_code == 200
        data = resp.json()
        # If there are 2 items and limit=2, next_cursor should be set
        if data["count"] == 2:
            assert data["next_cursor"] is not None
