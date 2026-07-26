# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Shared pytest fixtures for signal-inspector tests.
# Date: 2025-07-18
# ---------------------------------------------------------------------------
"""Shared pytest fixtures for signal-inspector tests."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio
from redis.asyncio import Redis

from inspector.bus.redis_streams import RedisStreamsPublisher
from inspector.envelope import AdapterEvent, CanonicalEvent
from inspector.normalizer.severity import reload_rules


# Function: event_loop_policy
@pytest.fixture(scope="session")
def event_loop_policy():
    return asyncio.DefaultEventLoopPolicy()


# Function: sample_adapter_event
@pytest.fixture
def sample_adapter_event() -> AdapterEvent:
    return AdapterEvent(
        raw_payload={
            "po_id": "PO-001",
            "supplier_id": "SUP-001",
            "delay_days": 5,
            "reason": "Manufacturing delay",
            "new_eta": "2026-07-15",
        },
        source_system="erp",
        source_event_id="erp-evt-001",
        event_type="supplier.po.delayed",
        source_timestamp=datetime.now(timezone.utc),
        adapter_name="erp_webhook",
    )


# Function: sample_canonical_event
@pytest.fixture
def sample_canonical_event() -> CanonicalEvent:
    return CanonicalEvent(
        source_system="erp",
        source_event_id="erp-evt-001",
        event_type="supplier.po.delayed",
        severity="med",
        source_timestamp=datetime.now(timezone.utc),
        payload={
            "po_id": "PO-001",
            "supplier_id": "SUP-001",
            "delay_days": 5,
            "reason": "Manufacturing delay",
        },
    )


# Function: mock_redis
@pytest.fixture
def mock_redis() -> AsyncMock:
    """Async mock Redis client."""
    redis = AsyncMock(spec=Redis)
    redis.ping.return_value = True
    redis.set.return_value = True  # SET NX returns True = was set (new key)
    redis.xadd.return_value = b"1-0"
    return redis


# Function: mock_publisher
@pytest.fixture
def mock_publisher(mock_redis: AsyncMock) -> RedisStreamsPublisher:
    return RedisStreamsPublisher(mock_redis)


# Function: reset_severity_rules
@pytest.fixture(autouse=True)
def reset_severity_rules():
    """Reset severity rules cache between tests."""
    reload_rules()
    yield
    reload_rules()
