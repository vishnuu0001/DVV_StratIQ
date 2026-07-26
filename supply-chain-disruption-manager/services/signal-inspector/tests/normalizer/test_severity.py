# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Tests for the severity evaluator.
# Date: 2026-03-01
# ---------------------------------------------------------------------------
"""Tests for the severity evaluator."""

from __future__ import annotations

import pytest

from inspector.normalizer.severity import evaluate_severity


class TestEvaluateSeverity:
    # ── supplier.po.delayed ────────────────────────────────────────────────

    # Function: test_po_delayed_high_at_7_days
    def test_po_delayed_high_at_7_days(self) -> None:
        result = evaluate_severity("supplier.po.delayed", {"delay_days": 7})
        assert result == "high"

    # Function: test_po_delayed_high_above_7_days
    def test_po_delayed_high_above_7_days(self) -> None:
        result = evaluate_severity("supplier.po.delayed", {"delay_days": 10})
        assert result == "high"

    # Function: test_po_delayed_med_at_3_days
    def test_po_delayed_med_at_3_days(self) -> None:
        result = evaluate_severity("supplier.po.delayed", {"delay_days": 3})
        assert result == "med"

    # Function: test_po_delayed_med_at_6_days
    def test_po_delayed_med_at_6_days(self) -> None:
        result = evaluate_severity("supplier.po.delayed", {"delay_days": 6})
        assert result == "med"

    # Function: test_po_delayed_low_at_1_day
    def test_po_delayed_low_at_1_day(self) -> None:
        result = evaluate_severity("supplier.po.delayed", {"delay_days": 1})
        assert result == "low"

    # Function: test_po_delayed_low_at_2_days
    def test_po_delayed_low_at_2_days(self) -> None:
        result = evaluate_severity("supplier.po.delayed", {"delay_days": 2})
        assert result == "low"

    # ── warehouse.qc.rejected ──────────────────────────────────────────────

    # Function: test_qc_rejected_critical
    def test_qc_rejected_critical(self) -> None:
        result = evaluate_severity("warehouse.qc.rejected", {"defect_rate": 0.12})
        assert result == "critical"

    # Function: test_qc_rejected_high_at_threshold
    def test_qc_rejected_high_at_threshold(self) -> None:
        result = evaluate_severity("warehouse.qc.rejected", {"defect_rate": 0.05})
        assert result == "high"

    # Function: test_qc_rejected_high_between_thresholds
    def test_qc_rejected_high_between_thresholds(self) -> None:
        result = evaluate_severity("warehouse.qc.rejected", {"defect_rate": 0.07})
        assert result == "high"

    # Function: test_qc_rejected_med
    def test_qc_rejected_med(self) -> None:
        result = evaluate_severity("warehouse.qc.rejected", {"defect_rate": 0.02})
        assert result == "med"

    # ── logistics.customs.held ─────────────────────────────────────────────

    # Function: test_customs_held_high
    def test_customs_held_high(self) -> None:
        result = evaluate_severity("logistics.customs.held", {"dwell_days": 6})
        assert result == "high"

    # Function: test_customs_held_med
    def test_customs_held_med(self) -> None:
        result = evaluate_severity("logistics.customs.held", {"dwell_days": 2})
        assert result == "med"

    # ── production ────────────────────────────────────────────────────────

    # Function: test_short_pick_always_high
    def test_short_pick_always_high(self) -> None:
        result = evaluate_severity("production.issue.short_pick", {})
        assert result == "high"

    # Function: test_workcenter_stoppage_always_critical
    def test_workcenter_stoppage_always_critical(self) -> None:
        result = evaluate_severity("production.workcenter.stoppage", {})
        assert result == "critical"

    # ── demand.forecast.spike ─────────────────────────────────────────────

    # Function: test_forecast_spike_high
    def test_forecast_spike_high(self) -> None:
        result = evaluate_severity("demand.forecast.spike", {"spike_pct": 60})
        assert result == "high"

    # Function: test_forecast_spike_med
    def test_forecast_spike_med(self) -> None:
        result = evaluate_severity("demand.forecast.spike", {"spike_pct": 25})
        assert result == "med"

    # Function: test_forecast_spike_low
    def test_forecast_spike_low(self) -> None:
        result = evaluate_severity("demand.forecast.spike", {"spike_pct": 10})
        assert result == "low"

    # ── logistics.shipment.eta_changed ────────────────────────────────────

    # Function: test_eta_changed_high
    def test_eta_changed_high(self) -> None:
        result = evaluate_severity("logistics.shipment.eta_changed", {"delay_days": 7})
        assert result == "high"

    # Function: test_eta_changed_med
    def test_eta_changed_med(self) -> None:
        result = evaluate_severity("logistics.shipment.eta_changed", {"delay_days": 3})
        assert result == "med"

    # Function: test_eta_changed_low
    def test_eta_changed_low(self) -> None:
        result = evaluate_severity("logistics.shipment.eta_changed", {"delay_days": 1})
        assert result == "low"

    # ── warehouse.grn.short ───────────────────────────────────────────────

    # Function: test_grn_short_high
    def test_grn_short_high(self) -> None:
        result = evaluate_severity("warehouse.grn.short", {"short_pct": 0.25})
        assert result == "high"

    # Function: test_grn_short_med
    def test_grn_short_med(self) -> None:
        result = evaluate_severity("warehouse.grn.short", {"short_pct": 0.1})
        assert result == "med"

    # ── unknown event type ────────────────────────────────────────────────

    # Function: test_unknown_event_type_defaults_info
    def test_unknown_event_type_defaults_info(self) -> None:
        result = evaluate_severity("some.unknown.event", {"value": 999})
        assert result == "info"

    # ── missing payload field ─────────────────────────────────────────────

    # Function: test_missing_field_falls_through_to_default
    def test_missing_field_falls_through_to_default(self) -> None:
        result = evaluate_severity("supplier.po.delayed", {})
        assert result == "low"  # default condition
