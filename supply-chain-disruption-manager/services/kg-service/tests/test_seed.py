# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Tests for the /seed endpoint and idempotency.
# Date: 2026-05-07
# ---------------------------------------------------------------------------
"""Tests for the /seed endpoint and idempotency."""
from __future__ import annotations

import pytest
from httpx import AsyncClient


class TestSeed:
    # Function: test_seed_returns_202
    async def test_seed_returns_202(self, client: AsyncClient) -> None:
        resp = await client.post("/seed")
        assert resp.status_code == 202
        data = resp.json()
        assert data["status"] == "seeded"
        assert "stats" in data
        assert data["stats"]["nodes"] > 0
        assert data["stats"]["edges"] > 0

    # Function: test_seed_idempotent
    async def test_seed_idempotent(self, client: AsyncClient) -> None:
        """Call seed twice and verify node/edge counts are the same."""
        resp1 = await client.post("/seed")
        assert resp1.status_code == 202
        stats1 = resp1.json()["stats"]

        resp2 = await client.post("/seed")
        assert resp2.status_code == 202
        stats2 = resp2.json()["stats"]

        assert stats1["nodes"] == stats2["nodes"], "Node count changed on second seed"
        assert stats1["edges"] == stats2["edges"], "Edge count changed on second seed"

    # Function: test_seed_creates_suppliers
    async def test_seed_creates_suppliers(self, client: AsyncClient) -> None:
        await client.post("/seed")
        resp = await client.get("/entity/Supplier", params={"status": "ACTIVE", "limit": 10})
        assert resp.status_code == 200
        data = resp.json()
        supplier_ids = {s["id"] for s in data["items"]}
        assert "SUP-001" in supplier_ids
        assert "SUP-005" in supplier_ids

    # Function: test_seed_creates_people
    async def test_seed_creates_people(self, client: AsyncClient) -> None:
        await client.post("/seed")
        resp = await client.get("/entity/Person", params={"status": "ACTIVE", "limit": 10})
        assert resp.status_code == 200
        data = resp.json()
        person_ids = {p["id"] for p in data["items"]}
        assert "USR-BUYER-001" in person_ids
        assert "USR-SCM-001" in person_ids

    # Function: test_seed_creates_production_orders
    async def test_seed_creates_production_orders(self, client: AsyncClient) -> None:
        await client.post("/seed")
        resp = await client.get("/entity/ProductionOrder", params={"status": "ACTIVE", "limit": 20})
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] >= 1

    # Function: test_health_shows_nodes_after_seed
    async def test_health_shows_nodes_after_seed(self, client: AsyncClient) -> None:
        await client.post("/seed")
        resp = await client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["node_count"] > 50
        assert data["edge_count"] > 50
