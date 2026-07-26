# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: TMS (Transport Management System) webhook adapter.
# Date: 2025-10-22
# ---------------------------------------------------------------------------
"""TMS (Transport Management System) webhook adapter."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import structlog

from inspector.adapters.base import BaseAdapter
from inspector.envelope import AdapterEvent

logger = structlog.get_logger(__name__)

# Map TMS event codes to canonical event types
_TMS_EVENT_MAP: dict[str, str] = {
    "SHIPMENT_IN_TRANSIT": "logistics.shipment.in_transit",
    "ETA_UPDATED": "logistics.shipment.eta_changed",
    "CUSTOMS_HOLD": "logistics.customs.held",
    "CUSTOMS_CLEARED": "logistics.customs.cleared",
    "SHIPMENT_DISPATCHED": "supplier.shipment.dispatched",
}


class TmsWebhookAdapter(BaseAdapter):
    """Receives TMS events via webhook POST /ingest/tms_webhook."""

    name = "tms_webhook"

    # Function: parse_body
    def parse_body(self, body: dict[str, Any]) -> AdapterEvent:
        """Convert TMS webhook body to AdapterEvent.

        Expected TMS body shape:
        {
            "event_code": "ETA_UPDATED",
            "message_id": "...",
            "occurred_at": "...",
            "payload": { ... }
        }
        """
        raw_event_code = body.get("event_code", "")
        event_type = _TMS_EVENT_MAP.get(raw_event_code, f"logistics.{raw_event_code.lower()}")
        source_event_id = body.get("message_id") or body.get("id")

        raw_ts = body.get("occurred_at") or body.get("timestamp")
        if isinstance(raw_ts, str):
            source_timestamp = datetime.fromisoformat(raw_ts.replace("Z", "+00:00"))
        else:
            source_timestamp = datetime.now(timezone.utc)

        payload = body.get("payload") or body

        return AdapterEvent(
            raw_payload=payload,
            source_system="tms",
            source_event_id=str(source_event_id) if source_event_id else None,
            event_type=event_type,
            source_timestamp=source_timestamp,
            adapter_name=self.name,
        )
