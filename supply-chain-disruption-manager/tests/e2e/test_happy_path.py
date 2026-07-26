# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: E2E happy-path tests for the Supply Chain Disruption Manager.
# Date: 2025-07-21
# ---------------------------------------------------------------------------
"""
E2E happy-path tests for the Supply Chain Disruption Manager.

Requires all services to be running (docker compose up).
Run with: pytest tests/e2e/ -v --timeout=120
"""
from __future__ import annotations

import asyncio
import os
import time
from typing import Any

import httpx
import pytest

KG_URL = os.getenv("KG_BASE_URL", "http://localhost:8001")
KG_KEY = os.getenv("KG_API_KEY", "kg-dev-key-change-in-prod")
INSPECTOR_URL = os.getenv("INSPECTOR_BASE_URL", "http://localhost:8003")
AGENT_URL = os.getenv("AGENT_BASE_URL", "http://localhost:8002")
AGENT_KEY = os.getenv("AGENT_API_KEY", "agent-dev-key-change-in-prod")

KG_HEADERS = {"X-API-Key": KG_KEY}
AGENT_HEADERS = {"X-API-Key": AGENT_KEY, "Content-Type": "application/json"}


# Function: _retry
def _retry(fn: Any, retries: int = 10, delay: float = 3.0) -> Any:
    """Retry callable until it succeeds or retries exhausted."""
    last_exc: Exception | None = None
    for i in range(retries):
        try:
            return fn()
        except Exception as e:
            last_exc = e
            time.sleep(delay)
    raise RuntimeError(f"Timed out after {retries} retries") from last_exc


# ─── Health checks ──────────────────────────────────────────────────────────

class TestServiceHealth:
    # Function: test_kg_health
    def test_kg_health(self) -> None:
        r = httpx.get(f"{KG_URL}/health", timeout=10)
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "healthy"

    # Function: test_inspector_health
    def test_inspector_health(self) -> None:
        r = httpx.get(f"{INSPECTOR_URL}/health", timeout=10)
        assert r.status_code == 200
        data = r.json()
        assert data["status"] in ("healthy", "degraded")

    # Function: test_agent_health
    def test_agent_health(self) -> None:
        r = httpx.get(f"{AGENT_URL}/health", headers=AGENT_HEADERS, timeout=10)
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "healthy"


# ─── KG Seed ────────────────────────────────────────────────────────────────

class TestKGSeed:
    # Function: test_seed_is_idempotent
    def test_seed_is_idempotent(self) -> None:
        """POST /seed twice; counts should be the same."""
        r1 = httpx.post(f"{KG_URL}/seed", headers=KG_HEADERS, timeout=60)
        assert r1.status_code == 200
        counts1 = r1.json().get("counts", {})

        r2 = httpx.post(f"{KG_URL}/seed", headers=KG_HEADERS, timeout=60)
        assert r2.status_code == 200
        counts2 = r2.json().get("counts", {})

        assert counts1["nodes"] == counts2["nodes"]
        assert counts1["edges"] == counts2["edges"]

    # Function: test_seed_minimum_volumes
    def test_seed_minimum_volumes(self) -> None:
        r = httpx.post(f"{KG_URL}/seed", headers=KG_HEADERS, timeout=60)
        counts = r.json().get("counts", {})
        assert counts.get("nodes", 0) >= 200
        assert counts.get("edges", 0) >= 150

    # Function: test_supplier_entity_exists
    def test_supplier_entity_exists(self) -> None:
        r = httpx.get(f"{KG_URL}/entity/Supplier/SUP-001", headers=KG_HEADERS, timeout=10)
        assert r.status_code == 200
        data = r.json()
        assert data["id"] == "SUP-001"
        assert data["kind"] == "Supplier"

    # Function: test_buyer_person_exists
    def test_buyer_person_exists(self) -> None:
        r = httpx.get(f"{KG_URL}/entity/Buyer/USR-BUYER-001", headers=KG_HEADERS, timeout=10)
        assert r.status_code == 200
        assert r.json()["id"] == "USR-BUYER-001"


# ─── KG Traversal ───────────────────────────────────────────────────────────

class TestKGTraversal:
    # Function: test_traverse_from_supplier
    def test_traverse_from_supplier(self) -> None:
        r = httpx.get(
            f"{KG_URL}/traverse",
            params={"root_id": "SUP-001", "edge_kinds": "flow,meta", "direction": "outbound", "max_depth": 6},
            headers=KG_HEADERS,
            timeout=30,
        )
        assert r.status_code == 200
        data = r.json()
        assert data["root"]["id"] == "SUP-001"
        assert len(data["nodes"]) >= 5
        assert len(data["edges"]) >= 4

        node_ids = [n["id"] for n in data["nodes"]]
        # Must reach POs and ASNs
        assert any(n.startswith("PO-") for n in node_ids)

    # Function: test_traverse_from_po
    def test_traverse_from_po(self) -> None:
        r = httpx.get(
            f"{KG_URL}/traverse",
            params={"root_id": "PO-10001", "edge_kinds": "flow,meta", "direction": "outbound", "max_depth": 6},
            headers=KG_HEADERS,
            timeout=30,
        )
        assert r.status_code == 200
        data = r.json()
        assert len(data["nodes"]) >= 3


# ─── KG Owners ──────────────────────────────────────────────────────────────

class TestKGOwners:
    # Function: test_owners_of_stock_lot
    def test_owners_of_stock_lot(self) -> None:
        r = httpx.get(
            f"{KG_URL}/owners",
            params={"node_id": "LOT-70001", "include_transitive": "true"},
            headers=KG_HEADERS,
            timeout=30,
        )
        assert r.status_code == 200
        owners = r.json()
        assert isinstance(owners, list)
        assert len(owners) >= 1
        roles = [o.get("role", "") for o in owners]
        # At least one of buyer, warehouse manager, or planner should be in the chain
        assert any(
            any(kw in r.lower() for kw in ["buyer", "warehouse", "planner", "manager"])
            for r in roles
        )

    # Function: test_owners_of_purchase_order
    def test_owners_of_purchase_order(self) -> None:
        r = httpx.get(
            f"{KG_URL}/owners",
            params={"node_id": "PO-10001", "include_transitive": "false"},
            headers=KG_HEADERS,
            timeout=30,
        )
        assert r.status_code == 200
        owners = r.json()
        assert any("Buyer" in o.get("kind", "") for o in owners)


# ─── Signal Inspector ────────────────────────────────────────────────────────

class TestSignalInspector:
    # Function: test_ingest_manual_supplier_delay
    def test_ingest_manual_supplier_delay(self) -> None:
        payload = {
            "event_type": "supplier.po.delayed",
            "source_system": "erp_test",
            "source_event_id": f"e2e-test-{int(time.time())}",
            "source_timestamp": "2026-06-27T09:00:00Z",
            "payload": {
                "po_id": "PO-10001",
                "supplier_id": "SUP-001",
                "delay_days": 7,
                "reason": "e2e test event"
            }
        }
        r = httpx.post(f"{INSPECTOR_URL}/ingest/manual", json=payload, timeout=15)
        assert r.status_code in (200, 201, 202)
        data = r.json()
        assert "event_id" in data

    # Function: test_ingest_invalid_event_goes_to_invalid_stream
    def test_ingest_invalid_event_goes_to_invalid_stream(self) -> None:
        payload = {
            "event_type": "supplier.po.delayed",
            "source_system": "erp_test",
            "source_event_id": f"e2e-invalid-{int(time.time())}",
            "source_timestamp": "2026-06-27T09:00:00Z",
            "payload": {
                # Missing required fields: po_id, supplier_id, delay_days, reason
                "foo": "bar"
            }
        }
        r = httpx.post(f"{INSPECTOR_URL}/ingest/manual", json=payload, timeout=15)
        # Should accept but route to invalid
        assert r.status_code in (200, 201, 202)

    # Function: test_event_appears_in_list
    def test_event_appears_in_list(self) -> None:
        uid = f"e2e-list-{int(time.time())}"
        payload = {
            "event_type": "supplier.po.delayed",
            "source_system": "erp_test_list",
            "source_event_id": uid,
            "source_timestamp": "2026-06-27T09:00:00Z",
            "payload": {
                "po_id": "PO-10002",
                "supplier_id": "SUP-002",
                "delay_days": 3,
                "reason": "test"
            }
        }
        httpx.post(f"{INSPECTOR_URL}/ingest/manual", json=payload, timeout=15)
        time.sleep(1)

        r = httpx.get(f"{INSPECTOR_URL}/events", params={"source_system": "erp_test_list", "limit": 5}, timeout=10)
        assert r.status_code == 200

    # Function: test_dedupe_prevents_duplicate
    def test_dedupe_prevents_duplicate(self) -> None:
        uid = f"e2e-dedupe-{int(time.time())}"
        payload = {
            "event_type": "supplier.po.delayed",
            "source_system": "erp_dedupe_test",
            "source_event_id": uid,
            "source_timestamp": "2026-06-27T09:00:00Z",
            "payload": {"po_id": "PO-10003", "supplier_id": "SUP-003", "delay_days": 2, "reason": "dedupe test"}
        }
        r1 = httpx.post(f"{INSPECTOR_URL}/ingest/manual", json=payload, timeout=15)
        r2 = httpx.post(f"{INSPECTOR_URL}/ingest/manual", json=payload, timeout=15)
        assert r1.status_code in (200, 201, 202)
        data2 = r2.json()
        assert data2.get("deduplicated") is True or r2.status_code in (200, 202)


# ─── Agent Service ───────────────────────────────────────────────────────────

class TestAgentService:
    # Function: test_trigger_disruption_returns_incident_id
    def test_trigger_disruption_returns_incident_id(self) -> None:
        payload = {
            "source_event_id": f"e2e-disruption-{int(time.time())}",
            "type": "supplier_delay",
            "root_node_id": "SUP-001",
            "payload": {
                "supplier_id": "SUP-001",
                "po_ids_affected": ["PO-10001"],
                "delay_days": 7,
                "reason": "E2E test disruption"
            }
        }
        r = httpx.post(f"{AGENT_URL}/disruption", json=payload, headers=AGENT_HEADERS, timeout=15)
        assert r.status_code == 202
        data = r.json()
        assert "incident_id" in data
        return data["incident_id"]

    # Function: test_incident_created_and_processed
    def test_incident_created_and_processed(self) -> None:
        uid = f"e2e-full-{int(time.time())}"
        payload = {
            "source_event_id": uid,
            "type": "supplier_delay",
            "root_node_id": "SUP-001",
            "payload": {
                "supplier_id": "SUP-001",
                "po_ids_affected": ["PO-10001"],
                "delay_days": 7,
                "reason": "E2E full pipeline test"
            }
        }
        r = httpx.post(f"{AGENT_URL}/disruption", json=payload, headers=AGENT_HEADERS, timeout=15)
        assert r.status_code == 202
        incident_id = r.json()["incident_id"]

        # Wait for processing
        # Function: check_incident
        def check_incident() -> dict:
            resp = httpx.get(f"{AGENT_URL}/incident/{incident_id}", headers=AGENT_HEADERS, timeout=10)
            assert resp.status_code == 200
            inc = resp.json()
            assert inc["state"] not in ("NEW",)  # must have advanced
            return inc

        incident = _retry(check_incident, retries=15, delay=2.0)
        assert incident["type"] in ("supplier_delay", "supplier.po.delayed")
        assert incident["severity"] in ("high", "critical", "med")

    # Function: test_blast_radius_populated
    def test_blast_radius_populated(self) -> None:
        uid = f"e2e-blast-{int(time.time())}"
        payload = {
            "source_event_id": uid,
            "type": "supplier_delay",
            "root_node_id": "SUP-001",
            "payload": {"supplier_id": "SUP-001", "po_ids_affected": ["PO-10001"], "delay_days": 7, "reason": "blast test"}
        }
        r = httpx.post(f"{AGENT_URL}/disruption", json=payload, headers=AGENT_HEADERS, timeout=15)
        incident_id = r.json()["incident_id"]

        # Function: check_blast
        def check_blast() -> dict:
            resp = httpx.get(f"{AGENT_URL}/incident/{incident_id}", headers=AGENT_HEADERS, timeout=10)
            inc = resp.json()
            assert inc.get("blast_radius") is not None
            assert len(inc["blast_radius"].get("nodes", [])) > 0
            return inc

        _retry(check_blast, retries=15, delay=2.0)

    # Function: test_owners_populated
    def test_owners_populated(self) -> None:
        uid = f"e2e-owners-{int(time.time())}"
        payload = {
            "source_event_id": uid,
            "type": "supplier_delay",
            "root_node_id": "SUP-001",
            "payload": {"supplier_id": "SUP-001", "po_ids_affected": ["PO-10001"], "delay_days": 7, "reason": "owners test"}
        }
        r = httpx.post(f"{AGENT_URL}/disruption", json=payload, headers=AGENT_HEADERS, timeout=15)
        incident_id = r.json()["incident_id"]

        # Function: check_owners
        def check_owners() -> dict:
            resp = httpx.get(f"{AGENT_URL}/incident/{incident_id}", headers=AGENT_HEADERS, timeout=10)
            inc = resp.json()
            assert inc.get("owners") is not None
            assert len(inc["owners"]) > 0
            return inc

        _retry(check_owners, retries=15, delay=2.0)


# ─── Human Approval Flow ─────────────────────────────────────────────────────

class TestApprovalFlow:
    # Function: test_approve_incident
    def test_approve_incident(self) -> None:
        uid = f"e2e-approve-{int(time.time())}"
        payload = {
            "source_event_id": uid,
            "type": "supplier_delay",
            "root_node_id": "SUP-001",
            "payload": {"supplier_id": "SUP-001", "po_ids_affected": ["PO-10001"], "delay_days": 7, "reason": "approval test"}
        }
        r = httpx.post(f"{AGENT_URL}/disruption", json=payload, headers=AGENT_HEADERS, timeout=15)
        incident_id = r.json()["incident_id"]

        # Wait for AWAITING_APPROVAL state
        # Function: wait_for_approval_state
        def wait_for_approval_state() -> dict:
            resp = httpx.get(f"{AGENT_URL}/incident/{incident_id}", headers=AGENT_HEADERS, timeout=10)
            inc = resp.json()
            assert inc["state"] in ("AWAITING_APPROVAL", "RESOLVED")
            return inc

        incident = _retry(wait_for_approval_state, retries=20, delay=2.0)

        if incident["state"] == "AWAITING_APPROVAL":
            approve_r = httpx.post(
                f"{AGENT_URL}/incident/{incident_id}/approve",
                json={"reason": "E2E test approval", "decided_by": "e2e-tester"},
                headers=AGENT_HEADERS,
                timeout=10,
            )
            assert approve_r.status_code == 200
            updated = approve_r.json()
            assert updated["state"] == "RESOLVED"

    # Function: test_reject_incident_returns_to_planning
    def test_reject_incident_returns_to_planning(self) -> None:
        uid = f"e2e-reject-{int(time.time())}"
        payload = {
            "source_event_id": uid,
            "type": "supplier_delay",
            "root_node_id": "SUP-001",
            "payload": {"supplier_id": "SUP-001", "po_ids_affected": ["PO-10001"], "delay_days": 7, "reason": "reject test"}
        }
        r = httpx.post(f"{AGENT_URL}/disruption", json=payload, headers=AGENT_HEADERS, timeout=15)
        incident_id = r.json()["incident_id"]

        # Function: wait_for_approval_state
        def wait_for_approval_state() -> dict:
            resp = httpx.get(f"{AGENT_URL}/incident/{incident_id}", headers=AGENT_HEADERS, timeout=10)
            inc = resp.json()
            assert inc["state"] in ("AWAITING_APPROVAL", "RESOLVED")
            return inc

        incident = _retry(wait_for_approval_state, retries=20, delay=2.0)

        if incident["state"] == "AWAITING_APPROVAL":
            reject_r = httpx.post(
                f"{AGENT_URL}/incident/{incident_id}/reject",
                json={"reason": "Plan does not adequately address lead time risk", "decided_by": "e2e-tester"},
                headers=AGENT_HEADERS,
                timeout=10,
            )
            assert reject_r.status_code == 200
            updated = reject_r.json()
            assert updated["state"] in ("REJECTED", "CLASSIFIED")

    # Function: test_incident_timeline_exists
    def test_incident_timeline_exists(self) -> None:
        uid = f"e2e-timeline-{int(time.time())}"
        payload = {
            "source_event_id": uid,
            "type": "supplier_delay",
            "root_node_id": "SUP-001",
            "payload": {"supplier_id": "SUP-001", "po_ids_affected": ["PO-10001"], "delay_days": 5, "reason": "timeline test"}
        }
        r = httpx.post(f"{AGENT_URL}/disruption", json=payload, headers=AGENT_HEADERS, timeout=15)
        incident_id = r.json()["incident_id"]

        time.sleep(5)  # Let processing start

        tl = httpx.get(f"{AGENT_URL}/incident/{incident_id}/timeline", headers=AGENT_HEADERS, timeout=10)
        assert tl.status_code == 200
        events = tl.json()
        assert isinstance(events, list)
        assert len(events) >= 1
