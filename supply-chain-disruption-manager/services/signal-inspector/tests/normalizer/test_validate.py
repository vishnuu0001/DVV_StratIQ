# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Tests for the validation stage.
# Date: 2025-11-02
# ---------------------------------------------------------------------------
"""Tests for the validation stage."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from inspector.envelope import AdapterEvent
from inspector.normalizer.validate import validate_event


# Function: _make_event
def _make_event(event_type: str, payload: dict) -> AdapterEvent:
    return AdapterEvent(
        raw_payload=payload,
        source_system="test",
        event_type=event_type,
        source_timestamp=datetime.now(timezone.utc),
        adapter_name="test",
    )


class TestValidateEvent:
    # Function: test_valid_supplier_po_delayed
    def test_valid_supplier_po_delayed(self) -> None:
        event = _make_event(
            "supplier.po.delayed",
            {
                "po_id": "PO-001",
                "supplier_id": "SUP-001",
                "delay_days": 5,
                "reason": "Port congestion",
            },
        )
        result = validate_event(event)
        assert result.valid is True
        assert result.errors == []

    # Function: test_invalid_supplier_po_delayed_missing_required
    def test_invalid_supplier_po_delayed_missing_required(self) -> None:
        event = _make_event(
            "supplier.po.delayed",
            {
                "po_id": "PO-001",
                # missing supplier_id, delay_days, reason
            },
        )
        result = validate_event(event)
        assert result.valid is False
        assert len(result.errors) > 0

    # Function: test_invalid_delay_days_below_minimum
    def test_invalid_delay_days_below_minimum(self) -> None:
        event = _make_event(
            "supplier.po.delayed",
            {
                "po_id": "PO-001",
                "supplier_id": "SUP-001",
                "delay_days": 0,  # minimum is 1
                "reason": "Some reason",
            },
        )
        result = validate_event(event)
        assert result.valid is False

    # Function: test_unknown_event_type_passes_with_no_schema
    def test_unknown_event_type_passes_with_no_schema(self) -> None:
        event = _make_event(
            "unknown.event.type",
            {"some_field": "value"},
        )
        result = validate_event(event)
        # No schema -> pass through
        assert result.valid is True

    # Function: test_valid_warehouse_qc_rejected
    def test_valid_warehouse_qc_rejected(self) -> None:
        event = _make_event(
            "warehouse.qc.rejected",
            {
                "qc_id": "QC-001",
                "warehouse_id": "WH-1",
                "defect_rate": 0.08,
            },
        )
        result = validate_event(event)
        assert result.valid is True

    # Function: test_invalid_defect_rate_above_max
    def test_invalid_defect_rate_above_max(self) -> None:
        event = _make_event(
            "warehouse.qc.rejected",
            {
                "qc_id": "QC-001",
                "warehouse_id": "WH-1",
                "defect_rate": 1.5,  # max is 1
            },
        )
        result = validate_event(event)
        assert result.valid is False

    # Function: test_valid_demand_forecast_spike
    def test_valid_demand_forecast_spike(self) -> None:
        event = _make_event(
            "demand.forecast.spike",
            {
                "product_id": "PROD-1",
                "spike_pct": 45.0,
                "forecast_period": "2026-Q3",
            },
        )
        result = validate_event(event)
        assert result.valid is True
