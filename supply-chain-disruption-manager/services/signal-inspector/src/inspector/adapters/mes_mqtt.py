# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: MES MQTT adapter — subscribes to MQTT broker for machine event signals.
# Date: 2026-04-30
# ---------------------------------------------------------------------------
"""MES MQTT adapter — subscribes to MQTT broker for machine event signals."""

from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from typing import Any, Callable, Coroutine

import structlog

from inspector.adapters.base import BaseAdapter
from inspector.envelope import AdapterEvent

logger = structlog.get_logger(__name__)


class MesMqttAdapter(BaseAdapter):
    """Subscribes to MQTT topic sc/mes/# for production events.

    Requires the 'aiomqtt' optional dependency. If not installed the adapter
    will log a warning and disable itself.
    """

    name = "mes_mqtt"

    # Function: __init__
    def __init__(
        self,
        config: dict[str, Any],
        on_event: Callable[[AdapterEvent], Coroutine[Any, Any, None]],
    ) -> None:
        super().__init__(config)
        self._on_event = on_event
        self._broker: str = config.get("broker", "localhost")
        self._port: int = int(config.get("port", 1883))
        self._topic: str = config.get("topic", "sc/mes/#")
        self._task: asyncio.Task[None] | None = None
        self._running = False

    # Function: start
    async def start(self) -> None:
        if not self.enabled:
            return
        try:
            import aiomqtt  # noqa: F401
        except ImportError:
            logger.warning(
                "mes_mqtt.aiomqtt_not_installed",
                hint="pip install aiomqtt",
            )
            self._health.status = "error"
            self._health.message = "aiomqtt not installed"
            return

        self._running = True
        self._task = asyncio.create_task(self._subscribe_loop(), name="mes_mqtt")
        logger.info(
            "mes_mqtt.started",
            broker=self._broker,
            port=self._port,
            topic=self._topic,
        )

    # Function: stop
    async def stop(self) -> None:
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("mes_mqtt.stopped")

    # Function: _subscribe_loop
    async def _subscribe_loop(self) -> None:
        import aiomqtt

        while self._running:
            try:
                async with aiomqtt.Client(self._broker, port=self._port) as client:
                    self._health.status = "healthy"
                    await client.subscribe(self._topic)
                    async for message in client.messages:
                        if not self._running:
                            break
                        try:
                            body = json.loads(message.payload)
                            adapter_event = self._parse_message(str(message.topic), body)
                            await self._on_event(adapter_event)
                            self.record_event()
                        except Exception:  # noqa: BLE001
                            self.record_error("message parse error")
                            logger.exception("mes_mqtt.message_error")
            except Exception:  # noqa: BLE001
                self.record_error("connection lost")
                logger.exception("mes_mqtt.connection_error")
                if self._running:
                    await asyncio.sleep(5)

    # Function: _parse_message
    def _parse_message(self, topic: str, body: dict[str, Any]) -> AdapterEvent:
        # Map MQTT topic suffix to event type
        # e.g. sc/mes/production/stoppage -> production.workcenter.stoppage
        parts = topic.split("/")
        if len(parts) >= 4:
            domain = parts[2]
            subtype = parts[3]
            event_type = f"{domain}.workcenter.{subtype}" if domain == "production" else f"{domain}.{subtype}"
        else:
            event_type = body.get("event_type", "production.workcenter.stoppage")

        raw_ts = body.get("timestamp") or body.get("ts")
        if isinstance(raw_ts, str):
            source_timestamp = datetime.fromisoformat(raw_ts.replace("Z", "+00:00"))
        else:
            source_timestamp = datetime.now(timezone.utc)

        return AdapterEvent(
            raw_payload=body.get("payload", body),
            source_system="mes",
            source_event_id=body.get("message_id") or body.get("id"),
            event_type=event_type,
            source_timestamp=source_timestamp,
            adapter_name=self.name,
        )
