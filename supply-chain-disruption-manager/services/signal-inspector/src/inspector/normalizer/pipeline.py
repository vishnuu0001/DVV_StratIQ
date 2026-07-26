# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Full normalizer pipeline: validate -> dedupe -> enrich -> severity -> retag -> publish.
# Date: 2025-10-30
# ---------------------------------------------------------------------------
"""Full normalizer pipeline: validate -> dedupe -> enrich -> severity -> retag -> publish."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

import httpx
import structlog
from redis.asyncio import Redis
from ulid import ULID

from inspector.bus.redis_streams import RedisStreamsPublisher
from inspector.envelope import AdapterEvent, CanonicalEvent, PipelineResult
from inspector.normalizer import dedupe, enrich, publish, severity, validate

logger = structlog.get_logger(__name__)

# Map event_type -> (disruption stream suffix, domain stream)
_DISRUPTION_MAP: dict[str, tuple[str, str]] = {
    "supplier.po.delayed": ("supplier", "supplier"),
    "logistics.shipment.eta_changed": ("logistics", "logistics"),
    "logistics.customs.held": ("logistics", "logistics"),
    "warehouse.qc.rejected": ("warehouse", "warehouse"),
    "warehouse.grn.short": ("warehouse", "warehouse"),
    "warehouse.bin.exception": ("warehouse", "warehouse"),
    "production.issue.short_pick": ("production", "production"),
    "production.workcenter.stoppage": ("production", "production"),
    "demand.forecast.spike": ("demand", "demand"),
    "demand.order.changed": ("demand", "demand"),
}

# Additional disruption tags for quality events
_EXTRA_DISRUPTION_STREAMS: dict[str, list[str]] = {
    "warehouse.qc.rejected": ["disruption.quality"],
}

# Domain stream mapping for non-disruption events
_DOMAIN_MAP: dict[str, str] = {
    "supplier": "supplier",
    "logistics": "logistics",
    "warehouse": "warehouse",
    "production": "production",
    "demand": "demand",
}


# Function: _get_domain
def _get_domain(event_type: str) -> str:
    """Derive the top-level domain from event_type prefix."""
    prefix = event_type.split(".")[0]
    return prefix


# Function: _resolve_stream
def _resolve_stream(event_type: str, is_disruption: bool, disruption_suffix: str | None) -> str:
    """Determine the primary Redis stream name for an event."""
    if is_disruption and disruption_suffix:
        return f"disruption.{disruption_suffix}"
    domain = _get_domain(event_type)
    return domain


# Function: run_pipeline
async def run_pipeline(
    adapter_event: AdapterEvent,
    redis: Redis,
    publisher: RedisStreamsPublisher,
    http_client: httpx.AsyncClient,
    event_repo: Any | None = None,
    skip_validate: bool = False,
    skip_dedupe: bool = False,
    skip_enrich: bool = False,
) -> PipelineResult:
    """Execute the full 6-stage normalizer pipeline.

    Stages:
      1. validate  — JSON schema check
      2. dedupe    — Redis-based deduplication
      3. enrich    — KG entity resolution
      4. severity  — YAML rule matching
      5. retag     — disruption classification
      6. publish   — XADD to Redis stream

    Returns a PipelineResult with the outcome.
    """
    log = logger.bind(
        event_type=adapter_event.event_type,
        source_system=adapter_event.source_system,
        adapter=adapter_event.adapter_name,
    )

    # ── Stage 1: Validate ──────────────────────────────────────────────────
    validation_result = validate.validate_event(adapter_event) if not skip_validate else None
    validation_errors: list[str] = []
    validation_status = "skipped"

    if validation_result is not None:
        validation_errors = validation_result.errors
        if not validation_result.valid:
            log.warning("pipeline.validation_failed", errors=validation_errors)
            await publisher.publish_invalid(
                {
                    "event_type": adapter_event.event_type,
                    "source_system": adapter_event.source_system,
                    "adapter_name": adapter_event.adapter_name,
                    "raw_payload": json.dumps(adapter_event.raw_payload),
                    "validation_errors": json.dumps(validation_errors),
                },
                validation_errors,
            )
            return PipelineResult(
                skipped=True,
                skip_reason="validation_failed",
                validation_errors=validation_errors,
                publish_status="events.invalid",
            )
        validation_status = "valid"

    # ── Stage 2: Dedupe ────────────────────────────────────────────────────
    if not skip_dedupe:
        is_dup = await dedupe.is_duplicate(
            redis,
            adapter_event.source_system,
            adapter_event.source_event_id,
        )
        if is_dup:
            return PipelineResult(
                skipped=True,
                skip_reason="duplicate",
                publish_status="skipped",
            )

    # ── Stage 3: Enrich ────────────────────────────────────────────────────
    payload = dict(adapter_event.raw_payload)
    root_node_id: str | None = None

    if not skip_enrich:
        root_node_id, payload = await enrich.enrich_payload(payload, http_client)

    # ── Stage 4: Severity ──────────────────────────────────────────────────
    sev = severity.evaluate_severity(adapter_event.event_type, payload)

    # ── Stage 5: Retag ─────────────────────────────────────────────────────
    original_event_type = adapter_event.event_type
    disruption_info = _DISRUPTION_MAP.get(original_event_type)
    is_disruption = disruption_info is not None
    disruption_suffix: str | None = None

    if is_disruption and disruption_info:
        disruption_suffix, _ = disruption_info
        payload["_original_type"] = original_event_type

    stream_name = _resolve_stream(original_event_type, is_disruption, disruption_suffix)

    # Build CanonicalEvent
    canonical = CanonicalEvent(
        event_id=str(ULID()),
        source_system=adapter_event.source_system,
        source_event_id=adapter_event.source_event_id,
        event_type=original_event_type,
        severity=sev,
        source_timestamp=adapter_event.source_timestamp,
        ingested_at=datetime.now(timezone.utc),
        root_node_id=root_node_id,
        payload=payload,
        tags={"adapter": adapter_event.adapter_name},
    )

    # ── Stage 6: Publish ───────────────────────────────────────────────────
    publish_status = await publish.publish_event(publisher, canonical, stream_name)

    # Publish to extra streams if applicable
    extra_streams = _EXTRA_DISRUPTION_STREAMS.get(original_event_type, [])
    for extra_stream in extra_streams:
        await publish.publish_event(publisher, canonical, extra_stream)

    log.info(
        "pipeline.complete",
        event_id=canonical.event_id,
        severity=sev,
        stream=stream_name,
        publish_status=publish_status,
        is_disruption=is_disruption,
    )

    # Persist to database if repo provided
    if event_repo is not None:
        try:
            await event_repo.save(
                canonical,
                stream_name=stream_name,
                publish_status=publish_status,
                validation_status=validation_status,
                validation_errors=validation_errors,
            )
        except Exception:  # noqa: BLE001
            log.exception("pipeline.db_save_failed")

    return PipelineResult(
        canonical=canonical,
        stream_name=stream_name,
        publish_status=publish_status,
        validation_errors=validation_errors,
    )
