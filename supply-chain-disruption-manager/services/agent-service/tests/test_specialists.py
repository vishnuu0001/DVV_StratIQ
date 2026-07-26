# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Tests for specialist agents — in-scope and out-of-scope briefs.
# Date: 2025-09-04
# ---------------------------------------------------------------------------
"""Tests for specialist agents — in-scope and out-of-scope briefs."""
from __future__ import annotations

import os
import pytest

os.environ["MOCK_AGENTS"] = "true"


# Function: _brief
def _brief(disruption_type: str, payload: dict | None = None) -> dict:
    return {
        "incident_id": "test-incident-uuid",
        "disruption_type": disruption_type,
        "severity": "high",
        "root_node_id": "SUP-001",
        "blast_radius": {"nodes": [], "edges": []},
        "owners": [],
        "plan": {},
        "source_event": {"payload": payload or {}},
    }


# ------------------------------------------------------------------ #
# Buyer                                                                #
# ------------------------------------------------------------------ #

class TestBuyerSpecialist:
    # Function: buyer
    @pytest.fixture
    def buyer(self):
        from agents.specialists.buyer import BuyerSpecialist
        return BuyerSpecialist()

    # Function: test_supplier_delay_in_scope
    @pytest.mark.asyncio
    async def test_supplier_delay_in_scope(self, buyer):
        resp = await buyer.run(_brief("supplier_delay", {"po_id": "PO-10001", "supplier_id": "SUP-001", "delay_days": 7}))
        assert resp.status in ("completed", "blocked")
        assert resp.agent_name == "buyer-agent"
        assert len(resp.actions_taken) > 0
        assert resp.confidence > 0

    # Function: test_scope_violation_for_shopfloor
    @pytest.mark.asyncio
    async def test_scope_violation_for_shopfloor(self, buyer):
        resp = await buyer.run(_brief("workcenter_stoppage", {}))
        assert resp.status == "scope_violation"

    # Function: test_scope_violation_for_short_pick
    @pytest.mark.asyncio
    async def test_scope_violation_for_short_pick(self, buyer):
        resp = await buyer.run(_brief("short_pick", {}))
        assert resp.status == "scope_violation"

    # Function: test_quality_rejection_in_scope
    @pytest.mark.asyncio
    async def test_quality_rejection_in_scope(self, buyer):
        resp = await buyer.run(_brief("quality_rejection", {"po_id": "PO-10001", "supplier_id": "SUP-001"}))
        assert resp.status in ("completed", "blocked")
        assert resp.requires_human_approval is True

    # Function: test_duration_ms_populated
    @pytest.mark.asyncio
    async def test_duration_ms_populated(self, buyer):
        resp = await buyer.run(_brief("supplier_delay", {"po_id": "PO-10001", "delay_days": 3}))
        assert resp.duration_ms >= 0


# ------------------------------------------------------------------ #
# Logistics                                                            #
# ------------------------------------------------------------------ #

class TestLogisticsSpecialist:
    # Function: logistics
    @pytest.fixture
    def logistics(self):
        from agents.specialists.logistics import LogisticsSpecialist
        return LogisticsSpecialist()

    # Function: test_logistics_delay_in_scope
    @pytest.mark.asyncio
    async def test_logistics_delay_in_scope(self, logistics):
        resp = await logistics.run(_brief("logistics_delay", {"shipment_id": "SHIPMENT-001", "delay_days": 5}))
        assert resp.status in ("completed", "blocked")
        assert resp.confidence > 0

    # Function: test_customs_hold_in_scope
    @pytest.mark.asyncio
    async def test_customs_hold_in_scope(self, logistics):
        resp = await logistics.run(_brief("customs_hold", {"shipment_id": "SHIPMENT-001"}))
        assert resp.status in ("completed", "blocked")

    # Function: test_scope_violation_for_quality
    @pytest.mark.asyncio
    async def test_scope_violation_for_quality(self, logistics):
        resp = await logistics.run(_brief("quality_rejection", {}))
        assert resp.status == "scope_violation"

    # Function: test_large_delay_requires_approval
    @pytest.mark.asyncio
    async def test_large_delay_requires_approval(self, logistics):
        resp = await logistics.run(_brief("logistics_delay", {"shipment_id": "SHIPMENT-001", "delay_days": 10}))
        assert resp.requires_human_approval is True


# ------------------------------------------------------------------ #
# Warehouse                                                            #
# ------------------------------------------------------------------ #

class TestWarehouseSpecialist:
    # Function: warehouse
    @pytest.fixture
    def warehouse(self):
        from agents.specialists.warehouse import WarehouseSpecialist
        return WarehouseSpecialist()

    # Function: test_grn_shortage_in_scope
    @pytest.mark.asyncio
    async def test_grn_shortage_in_scope(self, warehouse):
        resp = await warehouse.run(_brief("grn_shortage", {"material_id": "MAT-RAW-001", "short_qty": 50}))
        assert resp.status in ("completed", "blocked")
        assert len(resp.actions_taken) > 0

    # Function: test_short_pick_in_scope
    @pytest.mark.asyncio
    async def test_short_pick_in_scope(self, warehouse):
        resp = await warehouse.run(_brief("short_pick", {"sku_id": "SKU-PROD-001", "short_qty": 30}))
        assert resp.status in ("completed", "blocked")

    # Function: test_scope_violation_for_customs
    @pytest.mark.asyncio
    async def test_scope_violation_for_customs(self, warehouse):
        resp = await warehouse.run(_brief("customs_hold", {}))
        assert resp.status == "scope_violation"

    # Function: test_scope_violation_for_demand_change
    @pytest.mark.asyncio
    async def test_scope_violation_for_demand_change(self, warehouse):
        resp = await warehouse.run(_brief("demand_change", {}))
        assert resp.status == "scope_violation"


# ------------------------------------------------------------------ #
# Quality                                                              #
# ------------------------------------------------------------------ #

class TestQualitySpecialist:
    # Function: quality
    @pytest.fixture
    def quality(self):
        from agents.specialists.quality import QualitySpecialist
        return QualitySpecialist()

    # Function: test_quality_rejection_in_scope
    @pytest.mark.asyncio
    async def test_quality_rejection_in_scope(self, quality):
        resp = await quality.run(_brief(
            "quality_rejection",
            {
                "batch_id": "BATCH-001",
                "material_id": "MAT-RAW-001",
                "supplier_id": "SUP-001",
                "qty_rejected": 200,
                "rejection_reason": "out of spec",
            },
        ))
        assert resp.status in ("completed", "blocked")
        assert resp.requires_human_approval is True
        assert len(resp.irreversible_actions) > 0

    # Function: test_scope_violation_for_logistics
    @pytest.mark.asyncio
    async def test_scope_violation_for_logistics(self, quality):
        resp = await quality.run(_brief("logistics_delay", {}))
        assert resp.status == "scope_violation"

    # Function: test_scope_violation_for_demand_spike
    @pytest.mark.asyncio
    async def test_scope_violation_for_demand_spike(self, quality):
        resp = await quality.run(_brief("demand_spike", {}))
        assert resp.status == "scope_violation"


# ------------------------------------------------------------------ #
# Inventory                                                            #
# ------------------------------------------------------------------ #

class TestInventorySpecialist:
    # Function: inventory
    @pytest.fixture
    def inventory(self):
        from agents.specialists.inventory import InventorySpecialist
        return InventorySpecialist()

    # Function: test_supplier_delay_in_scope
    @pytest.mark.asyncio
    async def test_supplier_delay_in_scope(self, inventory):
        resp = await inventory.run(_brief("supplier_delay", {"material_id": "MAT-RAW-001", "delay_days": 7}))
        assert resp.status in ("completed", "blocked")
        assert resp.confidence > 0.5

    # Function: test_demand_spike_in_scope
    @pytest.mark.asyncio
    async def test_demand_spike_in_scope(self, inventory):
        resp = await inventory.run(_brief("demand_spike", {"material_id": "MAT-RAW-001"}))
        assert resp.status in ("completed", "blocked")

    # Function: test_scope_violation_for_workcenter
    @pytest.mark.asyncio
    async def test_scope_violation_for_workcenter(self, inventory):
        resp = await inventory.run(_brief("workcenter_stoppage", {}))
        assert resp.status == "scope_violation"

    # Function: test_scope_violation_for_customs
    @pytest.mark.asyncio
    async def test_scope_violation_for_customs(self, inventory):
        resp = await inventory.run(_brief("customs_hold", {}))
        assert resp.status == "scope_violation"


# ------------------------------------------------------------------ #
# Planning                                                             #
# ------------------------------------------------------------------ #

class TestPlanningSpecialist:
    # Function: planning
    @pytest.fixture
    def planning(self):
        from agents.specialists.planning import PlanningSpecialist
        return PlanningSpecialist()

    # Function: test_supplier_delay_in_scope
    @pytest.mark.asyncio
    async def test_supplier_delay_in_scope(self, planning):
        resp = await planning.run(_brief("supplier_delay", {"material_id": "MAT-RAW-001", "delay_days": 7}))
        assert resp.status in ("completed", "blocked")

    # Function: test_demand_spike_in_scope
    @pytest.mark.asyncio
    async def test_demand_spike_in_scope(self, planning):
        resp = await planning.run(_brief("demand_spike", {"uplift_pct": 25}))
        assert resp.status in ("completed", "blocked")

    # Function: test_scope_violation_for_customs
    @pytest.mark.asyncio
    async def test_scope_violation_for_customs(self, planning):
        resp = await planning.run(_brief("customs_hold", {}))
        assert resp.status == "scope_violation"

    # Function: test_scope_violation_for_grn_shortage
    @pytest.mark.asyncio
    async def test_scope_violation_for_grn_shortage(self, planning):
        resp = await planning.run(_brief("grn_shortage", {}))
        assert resp.status == "scope_violation"


# ------------------------------------------------------------------ #
# Shopfloor                                                            #
# ------------------------------------------------------------------ #

class TestShopfloorSpecialist:
    # Function: shopfloor
    @pytest.fixture
    def shopfloor(self):
        from agents.specialists.shopfloor import ShopfloorSpecialist
        return ShopfloorSpecialist()

    # Function: test_workcenter_stoppage_in_scope
    @pytest.mark.asyncio
    async def test_workcenter_stoppage_in_scope(self, shopfloor):
        resp = await shopfloor.run(_brief("workcenter_stoppage", {
            "workcenter_id": "WC-001",
            "reason": "equipment_failure",
            "production_order_id": "PRD-2026-0081",
        }))
        assert resp.status in ("completed", "blocked")
        assert resp.requires_human_approval is True

    # Function: test_short_pick_in_scope
    @pytest.mark.asyncio
    async def test_short_pick_in_scope(self, shopfloor):
        resp = await shopfloor.run(_brief("short_pick", {
            "production_order_id": "PRD-2026-0081",
            "short_qty": 50,
        }))
        assert resp.status in ("completed", "blocked")

    # Function: test_scope_violation_for_supplier_delay
    @pytest.mark.asyncio
    async def test_scope_violation_for_supplier_delay(self, shopfloor):
        resp = await shopfloor.run(_brief("supplier_delay", {}))
        assert resp.status == "scope_violation"

    # Function: test_scope_violation_for_customs
    @pytest.mark.asyncio
    async def test_scope_violation_for_customs(self, shopfloor):
        resp = await shopfloor.run(_brief("customs_hold", {}))
        assert resp.status == "scope_violation"

    # Function: test_scope_violation_for_quality
    @pytest.mark.asyncio
    async def test_scope_violation_for_quality(self, shopfloor):
        resp = await shopfloor.run(_brief("quality_rejection", {}))
        assert resp.status == "scope_violation"


# ------------------------------------------------------------------ #
# Response model validation                                            #
# ------------------------------------------------------------------ #

class TestSpecialistResponseModel:
    # Function: test_defaults
    def test_defaults(self):
        from agents.specialists.base import SpecialistResponse
        resp = SpecialistResponse(agent_name="test", status="completed")
        assert resp.actions_taken == []
        assert resp.blockers == []
        assert resp.irreversible_actions == []
        assert resp.token_input == 0
        assert resp.token_output == 0
        assert resp.cost_usd == 0.0

    # Function: test_invalid_status_rejected
    def test_invalid_status_rejected(self):
        from agents.specialists.base import SpecialistResponse
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            SpecialistResponse(agent_name="test", status="bad_status")
