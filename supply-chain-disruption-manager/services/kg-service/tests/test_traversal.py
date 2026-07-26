# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Tests for the /traverse endpoint.
# Date: 2025-07-21
# ---------------------------------------------------------------------------
"""Tests for the /traverse endpoint."""
from __future__ import annotations

from datetime import datetime, timezone

import pytest
from httpx import AsyncClient


# Function: _now
def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


SUPPLIER = {
    "id": "TRAV-SUP-001",
    "kind": "Supplier",
    "domain": "procurement",
    "created_at": _now(),
    "updated_at": _now(),
    "status": "ACTIVE",
    "metadata": {},
    "name": "Traverse Test Supplier",
    "country": "DE",
    "tier": 1,
    "lead_time_days": 7,
    "reliability_score": 0.9,
}

PO = {
    "id": "TRAV-PO-001",
    "kind": "PurchaseOrder",
    "domain": "procurement",
    "created_at": _now(),
    "updated_at": _now(),
    "status": "OPEN",
    "metadata": {},
    "supplier_id": "TRAV-SUP-001",
    "buyer_id": "TRAV-USR-001",
    "currency": "EUR",
    "total_value": "3000.00",
    "expected_delivery": "2025-05-01",
}

ASN = {
    "id": "TRAV-ASN-001",
    "kind": "ASN",
    "domain": "logistics",
    "created_at": _now(),
    "updated_at": _now(),
    "status": "ACTIVE",
    "metadata": {},
    "po_id": "TRAV-PO-001",
    "carrier_id": "TRAV-CAR-001",
    "ship_date": _now(),
    "eta": _now(),
    "incoterm": "FOB",
    "handling_units": [],
}


# Function: _seed_traverse_graph
async def _seed_traverse_graph(client: AsyncClient) -> None:
    await client.post("/entity/Supplier", json=SUPPLIER)
    await client.post("/entity/PurchaseOrder", json=PO)
    await client.post("/entity/ASN", json=ASN)
    # Supplier -> PO
    await client.post("/edge", json={"from_id": "TRAV-SUP-001", "to_id": "TRAV-PO-001", "kind": "flow", "verb": "fulfills"})
    # PO -> ASN
    await client.post("/edge", json={"from_id": "TRAV-PO-001", "to_id": "TRAV-ASN-001", "kind": "flow", "verb": "triggers"})


class TestTraversal:
    # Function: test_traverse_outbound
    async def test_traverse_outbound(self, client: AsyncClient) -> None:
        await _seed_traverse_graph(client)
        resp = await client.get(
            "/traverse",
            params={"root_id": "TRAV-SUP-001", "edge_kinds": "flow", "direction": "outbound", "max_depth": 3},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["root"]["id"] == "TRAV-SUP-001"
        node_ids = {n["id"] for n in data["nodes"]}
        assert "TRAV-PO-001" in node_ids
        assert "TRAV-ASN-001" in node_ids

    # Function: test_traverse_inbound
    async def test_traverse_inbound(self, client: AsyncClient) -> None:
        await _seed_traverse_graph(client)
        resp = await client.get(
            "/traverse",
            params={"root_id": "TRAV-ASN-001", "edge_kinds": "flow", "direction": "inbound", "max_depth": 3},
        )
        assert resp.status_code == 200
        data = resp.json()
        node_ids = {n["id"] for n in data["nodes"]}
        assert "TRAV-PO-001" in node_ids

    # Function: test_traverse_not_found
    async def test_traverse_not_found(self, client: AsyncClient) -> None:
        resp = await client.get(
            "/traverse",
            params={"root_id": "DOES-NOT-EXIST", "edge_kinds": "flow"},
        )
        assert resp.status_code == 404

    # Function: test_traverse_invalid_direction
    async def test_traverse_invalid_direction(self, client: AsyncClient) -> None:
        resp = await client.get(
            "/traverse",
            params={"root_id": "TRAV-SUP-001", "direction": "sideways"},
        )
        assert resp.status_code == 422

    # Function: test_traverse_edges_present
    async def test_traverse_edges_present(self, client: AsyncClient) -> None:
        await _seed_traverse_graph(client)
        resp = await client.get(
            "/traverse",
            params={"root_id": "TRAV-SUP-001", "edge_kinds": "flow", "direction": "outbound", "max_depth": 3},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["edges"]) >= 1
        verbs = {e["verb"] for e in data["edges"]}
        assert "fulfills" in verbs
