# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: POST /ingest/{adapter} — route incoming events to the correct adapter.
# Date: 2026-06-14
# ---------------------------------------------------------------------------
"""POST /ingest/{adapter} — route incoming events to the correct adapter."""

from __future__ import annotations

import json
from typing import Any

import structlog
from fastapi import APIRouter, HTTPException, Request, Response

from inspector.envelope import AdapterEvent, CanonicalEvent
from inspector.normalizer import pipeline, publish
from inspector.store.database import get_session_factory
from inspector.store.event_repo import EventRepo

logger = structlog.get_logger(__name__)

router = APIRouter(tags=["ingest"])


# Function: _run_pipeline
async def _run_pipeline(
    request: Request,
    adapter_event: AdapterEvent,
) -> dict[str, Any]:
    """Run normalizer pipeline and return summary dict."""
    redis = request.app.state.redis
    publisher = request.app.state.publisher
    http_client = request.app.state.http_client

    factory = get_session_factory()
    async with factory() as session:
        repo = EventRepo(session)
        result = await pipeline.run_pipeline(
            adapter_event=adapter_event,
            redis=redis,
            publisher=publisher,
            http_client=http_client,
            event_repo=repo,
        )
        await session.commit()

    return {
        "accepted": not result.skipped,
        "skip_reason": result.skip_reason,
        "event_id": result.canonical.event_id if result.canonical else None,
        "stream": result.stream_name,
        "publish_status": result.publish_status,
        "validation_errors": result.validation_errors,
    }


# Function: ingest_manual
@router.post("/ingest/manual")
async def ingest_manual(request: Request) -> dict[str, Any]:
    """Accept a manual event: either an AdapterEvent dict or a pre-formed CanonicalEvent."""
    adapter_manager = request.app.state.adapter_manager
    manual_adapter = adapter_manager.get("manual")
    if not manual_adapter:
        raise HTTPException(status_code=503, detail="manual adapter not enabled")

    body = await request.json()
    event, is_preformed = manual_adapter.parse_request(body)
    manual_adapter.record_event()

    if is_preformed:
        # Pre-formed CanonicalEvent: skip validate/dedupe/enrich
        assert isinstance(event, CanonicalEvent)
        redis = request.app.state.redis
        publisher = request.app.state.publisher
        http_client = request.app.state.http_client

        # Determine stream
        from inspector.normalizer.pipeline import _DISRUPTION_MAP, _get_domain
        disruption = _DISRUPTION_MAP.get(event.event_type)
        if disruption:
            stream_name = f"disruption.{disruption[0]}"
        else:
            stream_name = _get_domain(event.event_type)

        pub_status = await publish.publish_event(publisher, event, stream_name)

        factory = get_session_factory()
        async with factory() as session:
            repo = EventRepo(session)
            await repo.save(
                event,
                stream_name=stream_name,
                publish_status=pub_status,
                validation_status="skipped_preformed",
            )
            await session.commit()

        return {
            "accepted": True,
            "event_id": event.event_id,
            "stream": stream_name,
            "publish_status": pub_status,
            "preformed": True,
        }

    assert isinstance(event, AdapterEvent)
    return await _run_pipeline(request, event)


# Function: ingest_erp_webhook
@router.post("/ingest/erp_webhook")
async def ingest_erp_webhook(request: Request) -> dict[str, Any]:
    """Receive ERP webhook with HMAC-SHA256 signature verification."""
    adapter_manager = request.app.state.adapter_manager
    erp_adapter = adapter_manager.get("erp_webhook")
    if not erp_adapter:
        raise HTTPException(status_code=503, detail="erp_webhook adapter not enabled")

    raw_body = await erp_adapter.verify_signature(request)
    body = json.loads(raw_body)
    adapter_event = erp_adapter.parse_body(body)
    erp_adapter.record_event()

    return await _run_pipeline(request, adapter_event)


# Function: ingest_tms_webhook
@router.post("/ingest/tms_webhook")
async def ingest_tms_webhook(request: Request) -> dict[str, Any]:
    """Receive TMS webhook events."""
    adapter_manager = request.app.state.adapter_manager
    tms_adapter = adapter_manager.get("tms_webhook")
    if not tms_adapter:
        raise HTTPException(status_code=503, detail="tms_webhook adapter not enabled")

    body = await request.json()
    adapter_event = tms_adapter.parse_body(body)
    tms_adapter.record_event()

    return await _run_pipeline(request, adapter_event)
