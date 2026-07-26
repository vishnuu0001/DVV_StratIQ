# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Tests for the ManualAdapter.
# Date: 2025-10-11
# ---------------------------------------------------------------------------
"""Tests for the ManualAdapter."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from inspector.adapters.manual import ManualAdapter
from inspector.envelope import AdapterEvent, CanonicalEvent


# Function: adapter
@pytest.fixture
def adapter() -> ManualAdapter:
    return ManualAdapter({"enabled": True})


class TestManualAdapterParseRequest:
    # Function: test_parses_adapter_event
    def test_parses_adapter_event(self, adapter: ManualAdapter) -> None:
        body = {
            "event_type": "supplier.po.delayed",
            "source_system": "erp",
            "source_event_id": "e-001",
            "source_timestamp": datetime.now(timezone.utc).isoformat(),
            "raw_payload": {
                "po_id": "PO-001",
                "supplier_id": "SUP-001",
                "delay_days": 3,
                "reason": "Port congestion",
            },
        }
        event, is_preformed = adapter.parse_request(body)
        assert isinstance(event, AdapterEvent)
        assert is_preformed is False
        assert event.event_type == "supplier.po.delayed"
        assert event.source_system == "erp"
        assert event.source_event_id == "e-001"

    # Function: test_parses_preformed_canonical_event
    def test_parses_preformed_canonical_event(self, adapter: ManualAdapter) -> None:
        body = {
            "schema_version": 1,
            "event_id": "01J0000000000000000000000A",
            "event_type": "supplier.po.delayed",
            "severity": "med",
            "source_system": "erp",
            "source_timestamp": datetime.now(timezone.utc).isoformat(),
            "ingested_at": datetime.now(timezone.utc).isoformat(),
            "payload": {"po_id": "PO-001", "supplier_id": "SUP-001", "delay_days": 3},
        }
        event, is_preformed = adapter.parse_request(body)
        assert isinstance(event, CanonicalEvent)
        assert is_preformed is True
        assert event.event_id == "01J0000000000000000000000A"

    # Function: test_adapter_event_defaults_source_system_to_manual
    def test_adapter_event_defaults_source_system_to_manual(
        self, adapter: ManualAdapter
    ) -> None:
        body = {
            "event_type": "demand.forecast.spike",
            "raw_payload": {"product_id": "PROD-1", "spike_pct": 30, "forecast_period": "2026-Q3"},
        }
        event, is_preformed = adapter.parse_request(body)
        assert isinstance(event, AdapterEvent)
        assert event.source_system == "manual"
        assert is_preformed is False

    # Function: test_adapter_event_uses_raw_payload_when_no_raw_payload_key
    def test_adapter_event_uses_raw_payload_when_no_raw_payload_key(
        self, adapter: ManualAdapter
    ) -> None:
        """If body has no 'raw_payload' key and no schema_version, treat whole body as payload."""
        body = {
            "event_type": "warehouse.qc.rejected",
            "source_system": "wms",
            "qc_id": "QC-001",
            "warehouse_id": "WH-1",
            "defect_rate": 0.12,
        }
        event, is_preformed = adapter.parse_request(body)
        assert isinstance(event, AdapterEvent)
        assert is_preformed is False
        # raw_payload should be the full body when no raw_payload key
        assert "defect_rate" in event.raw_payload or "event_type" in event.raw_payload

    # Function: test_records_health_event
    def test_records_health_event(self, adapter: ManualAdapter) -> None:
        adapter.record_event()
        health = adapter.get_health()
        assert health.events_last_5m == 1
        assert health.status == "healthy"
