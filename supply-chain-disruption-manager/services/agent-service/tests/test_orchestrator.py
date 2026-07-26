# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Tests for classifier, planner, and orchestrator pipeline in mock mode.
# Date: 2025-10-14
# ---------------------------------------------------------------------------
"""Tests for classifier, planner, and orchestrator pipeline in mock mode."""
from __future__ import annotations

import os
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

# Force mock mode for all tests
os.environ["MOCK_AGENTS"] = "true"


class TestClassifier:
    """Test the deterministic mock classifier."""

    # Function: classifier
    @pytest.fixture
    def classifier(self):
        from agents.orchestrator.classifier import Classifier
        return Classifier()

    # Function: test_supplier_po_delayed
    @pytest.mark.asyncio
    async def test_supplier_po_delayed(self, classifier):
        result = await classifier.classify({"event_type": "supplier.po.delayed", "payload": {}})
        assert result.disruption_type == "supplier_delay"
        assert result.severity == "high"
        assert result.confidence > 0.9

    # Function: test_customs_hold
    @pytest.mark.asyncio
    async def test_customs_hold(self, classifier):
        result = await classifier.classify({"event_type": "logistics.customs.held", "payload": {}})
        assert result.disruption_type == "customs_hold"
        assert result.severity == "high"

    # Function: test_qc_rejection
    @pytest.mark.asyncio
    async def test_qc_rejection(self, classifier):
        result = await classifier.classify({"event_type": "warehouse.qc.rejected", "payload": {}})
        assert result.disruption_type == "quality_rejection"
        assert result.severity == "critical"

    # Function: test_demand_spike
    @pytest.mark.asyncio
    async def test_demand_spike(self, classifier):
        result = await classifier.classify({"event_type": "demand.forecast.spike", "payload": {}})
        assert result.disruption_type == "demand_spike"

    # Function: test_workcenter_stoppage
    @pytest.mark.asyncio
    async def test_workcenter_stoppage(self, classifier):
        result = await classifier.classify({"event_type": "production.workcenter.stoppage", "payload": {}})
        assert result.disruption_type == "workcenter_stoppage"
        assert result.severity == "critical"

    # Function: test_long_delay_escalates_to_critical
    @pytest.mark.asyncio
    async def test_long_delay_escalates_to_critical(self, classifier):
        result = await classifier.classify({
            "event_type": "supplier.po.delayed",
            "payload": {"delay_days": 15},
        })
        assert result.severity == "critical"

    # Function: test_all_event_types_resolve
    @pytest.mark.asyncio
    async def test_all_event_types_resolve(self, classifier):
        from agents.orchestrator.classifier import DISRUPTION_TYPE_MAP
        for event_type in DISRUPTION_TYPE_MAP:
            result = await classifier.classify({"event_type": event_type, "payload": {}})
            assert result.disruption_type is not None
            assert result.severity in ("low", "medium", "high", "critical")
            assert 0.0 <= result.confidence <= 1.0

    # Function: test_unknown_event_type_returns_safe_default
    @pytest.mark.asyncio
    async def test_unknown_event_type_returns_safe_default(self, classifier):
        result = await classifier.classify({"event_type": "unknown.totally.random", "payload": {}})
        assert result.disruption_type is not None  # should not raise


class TestPlanner:
    """Test the response planner."""

    # Function: planner
    @pytest.fixture
    def planner(self):
        from agents.orchestrator.planner import Planner
        return Planner()

    # Function: test_supplier_delay_dispatches_buyer
    def test_supplier_delay_dispatches_buyer(self, planner):
        plan = planner.compose(
            "supplier_delay", "high", {"nodes": [], "edges": []}, []
        )
        assert "buyer" in plan.specialists

    # Function: test_supplier_delay_requires_human_approval
    def test_supplier_delay_requires_human_approval(self, planner):
        plan = planner.compose(
            "supplier_delay", "high", {"nodes": [], "edges": []}, []
        )
        assert plan.requires_human_approval is True

    # Function: test_quality_rejection_dispatches_quality_and_buyer
    def test_quality_rejection_dispatches_quality_and_buyer(self, planner):
        plan = planner.compose(
            "quality_rejection", "critical", {"nodes": [], "edges": []}, []
        )
        assert "quality" in plan.specialists
        assert "buyer" in plan.specialists

    # Function: test_critical_severity_triggers_approval
    def test_critical_severity_triggers_approval(self, planner):
        plan = planner.compose(
            "logistics_delay", "critical", {"nodes": [], "edges": []}, []
        )
        # logistics_delay is False by default but critical overrides
        assert plan.requires_human_approval is True

    # Function: test_demand_spike_no_approval_by_default
    def test_demand_spike_no_approval_by_default(self, planner):
        plan = planner.compose(
            "demand_spike", "high", {"nodes": [], "edges": []}, []
        )
        assert plan.requires_human_approval is False

    # Function: test_plan_includes_disruption_type
    def test_plan_includes_disruption_type(self, planner):
        plan = planner.compose("customs_hold", "high", {"nodes": [], "edges": []}, [])
        d = plan.to_dict()
        assert d["disruption_type"] == "customs_hold"
        assert "specialists" in d

    # Function: test_rejection_context_stored_in_plan
    def test_rejection_context_stored_in_plan(self, planner):
        plan = planner.compose(
            "supplier_delay", "high", {"nodes": [], "edges": []}, [],
            rejection_context="Cost too high"
        )
        assert plan.context.get("rejection_context") == "Cost too high"
        assert plan.context.get("replanning") is True


class TestOrchestratorMock:
    """Test orchestrator in mock mode against a live-ish DB."""

    # Function: test_handle_event_creates_incident
    @pytest.mark.asyncio
    async def test_handle_event_creates_incident(
        self, supplier_delay_event, mock_kg_client, mock_redis
    ):
        """End-to-end mock run should produce an incident_id."""
        with patch("agents.orchestrator.agent.get_kg_client", return_value=mock_kg_client), \
             patch("agents.store.database.get_session") as mock_get_session, \
             patch("agents.store.database.get_session") as mock_gs:

            # Use in-memory approach: just test the orchestrator doesn't error
            # with mock session
            from agents.orchestrator.agent import Orchestrator

            mock_session = AsyncMock()
            mock_repo = AsyncMock()
            mock_incident = MagicMock()
            mock_incident.id = "test-incident-uuid"
            mock_incident.type = "supplier_delay"
            mock_incident.severity = "high"
            mock_incident.state = "IN_PROGRESS"
            mock_incident.plan = {
                "specialists": ["buyer", "logistics"],
                "disruption_type": "supplier_delay",
                "requires_human_approval": True,
                "context": {},
            }
            mock_incident.blast_radius = {"nodes": [], "edges": []}
            mock_incident.owners = []

            mock_repo.create.return_value = mock_incident
            mock_repo.get.return_value = mock_incident
            mock_repo.update_classification = AsyncMock()
            mock_repo.transition = AsyncMock(return_value=mock_incident)
            mock_repo.update_blast_radius = AsyncMock()
            mock_repo.update_plan = AsyncMock()
            mock_repo.create_agent_run = AsyncMock(return_value=MagicMock(id="run-uuid-1"))
            mock_repo.complete_agent_run = AsyncMock()
            mock_repo.update_final_summary = AsyncMock()
            mock_repo.write_outbox = AsyncMock()

            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=False)
            mock_session.flush = AsyncMock()

            with patch("agents.store.database.get_session", return_value=mock_session), \
                 patch("agents.store.incident_repo.get_repo", return_value=mock_repo):
                orch = Orchestrator(redis_client=mock_redis)
                incident_id = await orch.handle_event(supplier_delay_event)
                assert incident_id == "test-incident-uuid"


class TestClassifierToDict:
    # Function: test_classification_result_to_dict
    def test_classification_result_to_dict(self):
        from agents.orchestrator.classifier import ClassificationResult
        cr = ClassificationResult("supplier_delay", "high", 0.95)
        d = cr.to_dict()
        assert d["type"] == "supplier_delay"
        assert d["severity"] == "high"
        assert d["confidence"] == 0.95

    # Function: test_plan_to_dict
    def test_plan_to_dict(self):
        from agents.orchestrator.planner import ResponsePlan
        plan = ResponsePlan("supplier_delay", ["buyer", "logistics"], True, {"severity": "high"})
        d = plan.to_dict()
        assert d["specialists"] == ["buyer", "logistics"]
        assert d["requires_human_approval"] is True
