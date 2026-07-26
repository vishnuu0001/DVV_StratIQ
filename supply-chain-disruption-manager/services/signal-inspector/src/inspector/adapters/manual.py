# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Manual adapter — accepts AdapterEvent or pre-formed CanonicalEvent via REST.
# Date: 2025-09-19
# ---------------------------------------------------------------------------
"""Manual adapter — accepts AdapterEvent or pre-formed CanonicalEvent via REST."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import structlog

from inspector.adapters.base import BaseAdapter
from inspector.envelope import AdapterEvent, CanonicalEvent

logger = structlog.get_logger(__name__)


class ManualAdapter(BaseAdapter):
    """Accepts events posted directly to POST /ingest/manual."""

    name = "manual"

    # Function: parse_request
    def parse_request(self, body: dict[str, Any]) -> tuple[AdapterEvent | CanonicalEvent, bool]:
        """Parse request body.

        If 'schema_version' is present the body is treated as a pre-formed
        CanonicalEvent and the validate/dedupe/enrich stages are skipped.

        Otherwise it is parsed as an AdapterEvent and all pipeline stages run.

        Returns (event, is_preformed).
        """
        if "schema_version" in body:
            # Pre-formed canonical event
            canonical = CanonicalEvent.model_validate(body)
            logger.info(
                "manual.preformed_event",
                event_id=canonical.event_id,
                event_type=canonical.event_type,
            )
            return canonical, True

        # Raw AdapterEvent
        now = datetime.now(timezone.utc)
        raw_payload = body.get("raw_payload", body.get("payload", body))
        adapter_event = AdapterEvent(
            raw_payload=raw_payload,
            source_system=body.get("source_system", "manual"),
            source_event_id=body.get("source_event_id"),
            event_type=body["event_type"],
            source_timestamp=body.get("source_timestamp", now),
            adapter_name="manual",
        )
        logger.info(
            "manual.adapter_event",
            event_type=adapter_event.event_type,
            source_system=adapter_event.source_system,
        )
        return adapter_event, False
