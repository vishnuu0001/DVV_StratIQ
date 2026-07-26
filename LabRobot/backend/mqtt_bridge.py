# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: LabRobot — backend (mqtt_bridge.py)
# Date: 2026-05-17
# ---------------------------------------------------------------------------
import json
import logging
import os
import time
from typing import Callable, Optional

from database import SessionLocal
from robot_service import CommandQueueService

logger = logging.getLogger(__name__)

try:
    import paho.mqtt.client as mqtt
except Exception:  # pragma: no cover - optional dependency guard
    mqtt = None


class BackendMqttBridge:
    """MQTT bridge: persists ack events and can publish dispatched commands."""

    # Function: __init__
    def __init__(self):
        self.enabled = mqtt is not None
        self.host = os.getenv("LABROBOT_MQTT_HOST", "localhost")
        self.port = int(os.getenv("LABROBOT_MQTT_PORT", "1883"))
        self.ack_topic = os.getenv("LABROBOT_MQTT_ACK_TOPIC", "labrobot/ack")
        self.ingress_topic = os.getenv("LABROBOT_MQTT_INGRESS_TOPIC", "labrobot/commands/incoming")
        self.command_topic = os.getenv("LABROBOT_MQTT_COMMAND_TOPIC", "labrobot/commands")
        self.client_id = os.getenv("LABROBOT_MQTT_CLIENT_ID", "labrobot-backend-bridge")
        self.client: Optional["mqtt.Client"] = None
        self._on_command_finished: Optional[Callable[[str], None]] = None

    # Function: set_on_command_finished
    def set_on_command_finished(self, callback: Callable[[str], None]) -> None:
        self._on_command_finished = callback

    # Function: start
    def start(self) -> None:
        if not self.enabled:
            logger.warning("paho-mqtt not installed; MQTT bridge disabled")
            return

        self.client = mqtt.Client(client_id=self.client_id)
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message

        try:
            self.client.connect(self.host, self.port, keepalive=30)
            self.client.loop_start()
            logger.info("MQTT bridge started on %s:%s", self.host, self.port)
        except Exception as exc:  # pragma: no cover - runtime env issue
            logger.exception("Failed to start MQTT bridge: %s", exc)

    # Function: stop
    def stop(self) -> None:
        if not self.client:
            return
        self.client.loop_stop()
        self.client.disconnect()
        self.client = None

    # Function: publish_command
    def publish_command(self, payload: dict) -> None:
        if not self.client:
            return
        try:
            self.client.publish(self.command_topic, json.dumps(payload), qos=0)
        except Exception as exc:  # pragma: no cover
            logger.exception("Failed to publish command to MQTT: %s", exc)

    # Function: _on_connect
    def _on_connect(self, client, _userdata, _flags, rc):
        if rc != 0:
            logger.error("MQTT bridge failed to connect: rc=%s", rc)
            return
        client.subscribe(self.ack_topic, qos=0)
        client.subscribe(self.ingress_topic, qos=0)
        logger.info("MQTT bridge subscribed to %s and %s", self.ack_topic, self.ingress_topic)

    # Function: _on_message
    def _on_message(self, _client, _userdata, msg):
        try:
            payload = json.loads(msg.payload.decode("utf-8"))
        except Exception:
            logger.warning("Ignoring non-JSON ack payload")
            return

        db = SessionLocal()
        try:
            if msg.topic == self.ack_topic:
                CommandQueueService.persist_ack(db, msg.topic, payload)
                command = CommandQueueService.apply_ack_to_command(db, payload)
                if command and command.status in {"completed", "failed"} and self._on_command_finished:
                    self._on_command_finished(command.robot_id)
            elif msg.topic == self.ingress_topic:
                command_data = {
                    "command_id": payload.get("commandId") or payload.get("command_id") or f"mqtt-{int(time.time() * 1000)}",
                    "robot_id": payload.get("robotId") or payload.get("robot_id") or "AMR-001",
                    "command_type": payload.get("command") or payload.get("command_type") or "PICK_AND_PLACE",
                    "rack_id": payload.get("rackId") or payload.get("rack_id"),
                    "item_id": payload.get("itemId") or payload.get("item_id"),
                    "conveyor_id": payload.get("conveyorId") or payload.get("conveyor_id"),
                    "priority": payload.get("priority", 1),
                    "payload": payload,
                    "source": "mqtt",
                }

                CommandQueueService.enqueue_command(db, command_data)
                next_cmd = CommandQueueService.dispatch_if_idle(db, command_data["robot_id"])
                if next_cmd:
                    dispatch_payload = {
                        "command": next_cmd.command_type,
                        "commandId": next_cmd.command_id,
                        "robotId": next_cmd.robot_id,
                        "rackId": next_cmd.rack_id,
                        "itemId": next_cmd.item_id,
                        "conveyorId": next_cmd.conveyor_id,
                        **(next_cmd.payload or {}),
                    }
                    self.publish_command(dispatch_payload)
        except Exception as exc:  # pragma: no cover
            logger.exception("Failed processing MQTT ack payload: %s", exc)
        finally:
            db.close()
