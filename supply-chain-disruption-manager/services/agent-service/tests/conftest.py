# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Test fixtures: in-memory SQLite DB, mock Redis, mock KG client.
# Date: 2026-01-22
# ---------------------------------------------------------------------------
"""Test fixtures: in-memory SQLite DB, mock Redis, mock KG client."""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from agents.store.database import Base
from agents.store.models import IncidentState


# ------------------------------------------------------------------ #
# Event loop                                                           #
# ------------------------------------------------------------------ #

# Function: event_loop
@pytest.fixture(scope="session")
def event_loop():
    """Use a session-scoped event loop."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# ------------------------------------------------------------------ #
# In-memory SQLite DB                                                  #
# ------------------------------------------------------------------ #

# Function: async_engine
@pytest.fixture(scope="session")
async def async_engine():
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        connect_args={"check_same_thread": False},
    )
    async with engine.begin() as conn:
        # SQLite doesn't have gen_random_uuid() — patch for tests
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


# Function: db_session
@pytest.fixture
async def db_session(async_engine) -> AsyncGenerator[AsyncSession, None]:
    factory = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        yield session
        await session.rollback()


# ------------------------------------------------------------------ #
# Incident repo fixture                                                #
# ------------------------------------------------------------------ #

# Function: incident_repo
@pytest.fixture
async def incident_repo(db_session):
    from agents.store.incident_repo import IncidentRepo
    return IncidentRepo(db_session)


# ------------------------------------------------------------------ #
# Seed incident fixture                                                #
# ------------------------------------------------------------------ #

# Function: seed_incident
@pytest.fixture
async def seed_incident(incident_repo, db_session):
    """Create a pre-seeded incident in NEW state."""
    import uuid
    from agents.store.models import Incident

    incident = Incident(
        id=str(uuid.uuid4()),
        source_event_id="evt-test-001",
        state=IncidentState.NEW.value,
        type="supplier_delay",
        severity="high",
        confidence=0.95,
        root_node_id="SUP-001",
        specialist_runs=[],
        human_decisions=[],
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db_session.add(incident)
    await db_session.flush()
    return incident


# ------------------------------------------------------------------ #
# Mock KG client                                                       #
# ------------------------------------------------------------------ #

# Function: mock_kg_client
@pytest.fixture
def mock_kg_client():
    client = AsyncMock()
    client.traverse.return_value = {
        "nodes": [
            {"id": "SUP-001", "kind": "Supplier", "domain": "supply"},
            {"id": "MAT-RAW-001", "kind": "Material", "domain": "material"},
            {"id": "PO-10001", "kind": "PurchaseOrder", "domain": "procurement"},
        ],
        "edges": [
            {"from": "SUP-001", "to": "MAT-RAW-001", "kind": "SUPPLIES"},
        ],
    }
    client.get_owners.return_value = [
        {"id": "USR-101", "name": "Alice Johnson", "role": "Procurement Manager"},
    ]
    client.health.return_value = True
    return client


# ------------------------------------------------------------------ #
# Mock Redis                                                           #
# ------------------------------------------------------------------ #

# Function: mock_redis
@pytest.fixture
def mock_redis():
    redis = AsyncMock()
    redis.xadd.return_value = "1234567890-0"
    redis.ping.return_value = True
    return redis


# ------------------------------------------------------------------ #
# Standard disruption event                                            #
# ------------------------------------------------------------------ #

# Function: supplier_delay_event
@pytest.fixture
def supplier_delay_event() -> dict:
    return {
        "source_event_id": "evt-sup-delay-001",
        "event_type": "supplier.po.delayed",
        "disruption_type": "supplier_delay",
        "source_system": "erp_sap",
        "root_node_id": "SUP-001",
        "payload": {
            "supplier_id": "SUP-001",
            "po_id": "PO-10001",
            "delay_days": 7,
            "reason": "raw material shortage",
            "new_eta": "2026-07-22",
        },
    }


# Function: customs_hold_event
@pytest.fixture
def customs_hold_event() -> dict:
    return {
        "source_event_id": "evt-customs-001",
        "event_type": "logistics.customs.held",
        "disruption_type": "customs_hold",
        "source_system": "tms_oracle",
        "root_node_id": "SHIPMENT-001",
        "payload": {
            "shipment_id": "SHIPMENT-001",
            "hold_reason": "Missing HS code",
            "customs_office": "LA CBP",
        },
    }


# Function: qc_reject_event
@pytest.fixture
def qc_reject_event() -> dict:
    return {
        "source_event_id": "evt-qc-001",
        "event_type": "warehouse.qc.rejected",
        "disruption_type": "quality_rejection",
        "source_system": "qms_sap",
        "root_node_id": "WH-001",
        "payload": {
            "batch_id": "BATCH-2026-001",
            "material_id": "MAT-RAW-001",
            "supplier_id": "SUP-001",
            "qty_rejected": 200,
            "rejection_reason": "dimensional out of spec",
        },
    }


# Function: short_pick_event
@pytest.fixture
def short_pick_event() -> dict:
    return {
        "source_event_id": "evt-shortpick-001",
        "event_type": "production.issue.short_pick",
        "disruption_type": "short_pick",
        "source_system": "mes",
        "root_node_id": "WC-001",
        "payload": {
            "production_order_id": "PRD-2026-0081",
            "sku_id": "SKU-PROD-001",
            "short_qty": 50,
            "workcenter_id": "WC-001",
        },
    }


# Function: demand_spike_event
@pytest.fixture
def demand_spike_event() -> dict:
    return {
        "source_event_id": "evt-demand-001",
        "event_type": "demand.forecast.spike",
        "disruption_type": "demand_spike",
        "source_system": "demand_planning",
        "root_node_id": "SKU-PROD-001",
        "payload": {
            "sku_id": "SKU-PROD-001",
            "forecast_uplift_pct": 35,
            "trigger": "promotional_campaign",
        },
    }
