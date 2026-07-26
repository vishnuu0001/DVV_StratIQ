# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: WMS polling adapter — periodically polls WMS REST API for new events.
# Date: 2026-02-21
# ---------------------------------------------------------------------------
"""WMS polling adapter — periodically polls WMS REST API for new events."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any, Callable, Coroutine

import httpx
import structlog

from inspector.adapters.base import BaseAdapter
from inspector.envelope import AdapterEvent

logger = structlog.get_logger(__name__)


class WmsPollAdapter(BaseAdapter):
    """Polls WMS REST endpoint on a configurable interval."""

    name = "wms_poll"

    # Function: __init__
    def __init__(
        self,
        config: dict[str, Any],
        on_event: Callable[[AdapterEvent], Coroutine[Any, Any, None]],
    ) -> None:
        super().__init__(config)
        self._on_event = on_event
        self._task: asyncio.Task[None] | None = None
        self._http: httpx.AsyncClient | None = None
        self._running = False
        self._poll_url: str = config.get("poll_url", "")
        self._interval: int = int(config.get("poll_interval_seconds", 30))
        self._last_seen_id: str | None = None

    # Function: start
    async def start(self) -> None:
        if not self.enabled or not self._poll_url:
            logger.info("wms_poll.disabled_or_no_url")
            return
        self._running = True
        self._http = httpx.AsyncClient()
        self._task = asyncio.create_task(self._poll_loop(), name="wms_poll")
        logger.info("wms_poll.started", url=self._poll_url, interval=self._interval)

    # Function: stop
    async def stop(self) -> None:
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        if self._http:
            await self._http.aclose()
        logger.info("wms_poll.stopped")

    # Function: _poll_loop
    async def _poll_loop(self) -> None:
        while self._running:
            try:
                await self._do_poll()
            except Exception:  # noqa: BLE001
                self.record_error("poll error")
                logger.exception("wms_poll.error")
            await asyncio.sleep(self._interval)

    # Function: _do_poll
    async def _do_poll(self) -> None:
        if self._http is None:
            return

        params: dict[str, Any] = {}
        if self._last_seen_id:
            params["after_id"] = self._last_seen_id

        resp = await self._http.get(self._poll_url, params=params, timeout=10.0)
        resp.raise_for_status()
        events: list[dict[str, Any]] = resp.json().get("events", [])

        for item in events:
            adapter_event = self._parse_item(item)
            await self._on_event(adapter_event)
            self.record_event()
            if item.get("id"):
                self._last_seen_id = str(item["id"])

        if events:
            logger.info("wms_poll.fetched", count=len(events))

    # Function: _parse_item
    def _parse_item(self, item: dict[str, Any]) -> AdapterEvent:
        raw_ts = item.get("timestamp") or item.get("created_at")
        if isinstance(raw_ts, str):
            source_timestamp = datetime.fromisoformat(raw_ts.replace("Z", "+00:00"))
        else:
            source_timestamp = datetime.now(timezone.utc)

        event_type_raw = item.get("event_type", "warehouse.grn.received")
        return AdapterEvent(
            raw_payload=item.get("payload", item),
            source_system="wms",
            source_event_id=str(item["id"]) if item.get("id") else None,
            event_type=event_type_raw,
            source_timestamp=source_timestamp,
            adapter_name=self.name,
        )
