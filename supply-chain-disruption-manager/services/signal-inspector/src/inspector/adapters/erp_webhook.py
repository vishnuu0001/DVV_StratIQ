# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: ERP webhook adapter with HMAC-SHA256 signature verification.
# Date: 2026-01-25
# ---------------------------------------------------------------------------
"""ERP webhook adapter with HMAC-SHA256 signature verification."""

from __future__ import annotations

import hashlib
import hmac
from datetime import datetime, timezone
from typing import Any

import structlog
from fastapi import HTTPException, Request

from inspector.adapters.base import BaseAdapter
from inspector.config import get_settings
from inspector.envelope import AdapterEvent

logger = structlog.get_logger(__name__)


class ErpWebhookAdapter(BaseAdapter):
    """Receives ERP events via signed webhook POST /ingest/erp_webhook."""

    name = "erp_webhook"

    # Function: verify_signature
    async def verify_signature(self, request: Request) -> bytes:
        """Verify X-Hub-Signature-256 header against raw body.

        Raises HTTP 401 on failure. Returns raw body bytes.
        """
        settings = get_settings()
        secret = settings.inspector_erp_hmac_secret.encode()

        raw_body = await request.body()

        signature_header = request.headers.get("X-Hub-Signature-256", "")
        if not signature_header.startswith("sha256="):
            raise HTTPException(status_code=401, detail="Missing or malformed X-Hub-Signature-256")

        mac = hmac.new(secret, raw_body, hashlib.sha256)
        expected = "sha256=" + mac.hexdigest()
        if not hmac.compare_digest(expected, signature_header):
            logger.warning("erp_webhook.signature_mismatch")
            raise HTTPException(status_code=401, detail="Invalid HMAC signature")

        return raw_body

    # Function: parse_body
    def parse_body(self, body: dict[str, Any]) -> AdapterEvent:
        """Convert ERP webhook body to AdapterEvent.

        Expected ERP body shape:
        {
            "event": "supplier.po.delayed",
            "event_id": "...",
            "timestamp": "...",
            "data": { ... }
        }
        """
        event_type = body.get("event") or body.get("event_type", "erp.unknown")
        source_event_id = body.get("event_id") or body.get("id")
        raw_ts = body.get("timestamp") or body.get("created_at")

        if isinstance(raw_ts, str):
            source_timestamp = datetime.fromisoformat(raw_ts.replace("Z", "+00:00"))
        else:
            source_timestamp = datetime.now(timezone.utc)

        payload = body.get("data") or body

        return AdapterEvent(
            raw_payload=payload,
            source_system="erp",
            source_event_id=str(source_event_id) if source_event_id else None,
            event_type=event_type,
            source_timestamp=source_timestamp,
            adapter_name=self.name,
        )
