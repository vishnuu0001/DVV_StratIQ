# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Disruption event classifier — deterministic mock or LLM-backed.
# Date: 2025-12-12
# ---------------------------------------------------------------------------
"""Disruption event classifier — deterministic mock or LLM-backed."""
from __future__ import annotations

import structlog

from agents.config import get_settings
from agents.llm.ollama_client import chat as ollama_chat

log = structlog.get_logger(__name__)

# Maps canonical event_type -> disruption category
DISRUPTION_TYPE_MAP: dict[str, str] = {
    "supplier.po.delayed": "supplier_delay",
    "supplier.shipment.dispatched": "supplier_shipment",
    "logistics.shipment.eta_changed": "logistics_delay",
    "logistics.customs.held": "customs_hold",
    "warehouse.qc.rejected": "quality_rejection",
    "warehouse.grn.short": "grn_shortage",
    "warehouse.bin.exception": "warehouse_exception",
    "production.issue.short_pick": "short_pick",
    "production.workcenter.stoppage": "workcenter_stoppage",
    "demand.forecast.spike": "demand_spike",
    "demand.order.changed": "demand_change",
}

SEVERITY_MAP: dict[str, str] = {
    "supplier_delay": "high",
    "supplier_shipment": "medium",
    "logistics_delay": "medium",
    "customs_hold": "high",
    "quality_rejection": "critical",
    "grn_shortage": "high",
    "warehouse_exception": "medium",
    "short_pick": "high",
    "workcenter_stoppage": "critical",
    "demand_spike": "high",
    "demand_change": "medium",
}

CONFIDENCE_MAP: dict[str, float] = {
    "supplier_delay": 0.95,
    "supplier_shipment": 0.90,
    "logistics_delay": 0.88,
    "customs_hold": 0.92,
    "quality_rejection": 0.97,
    "grn_shortage": 0.93,
    "warehouse_exception": 0.85,
    "short_pick": 0.91,
    "workcenter_stoppage": 0.96,
    "demand_spike": 0.82,
    "demand_change": 0.80,
}


class ClassificationResult:
    # Function: __init__
    def __init__(self, disruption_type: str, severity: str, confidence: float) -> None:
        self.disruption_type = disruption_type
        self.severity = severity
        self.confidence = confidence

    # Function: to_dict
    def to_dict(self) -> dict:
        return {
            "type": self.disruption_type,
            "severity": self.severity,
            "confidence": self.confidence,
        }


class Classifier:
    """Classifies a disruption event into type/severity/confidence."""

    # Function: __init__
    def __init__(self) -> None:
        self._settings = get_settings()

    # Function: classify
    async def classify(self, event: dict) -> ClassificationResult:
        """Classify the event. Uses mock or LLM depending on config."""
        if self._settings.use_mock:
            return self._mock_classify(event)
        return await self._llm_classify(event)

    # Function: _mock_classify
    def _mock_classify(self, event: dict) -> ClassificationResult:
        event_type = event.get("event_type", "")
        # Support both "type" and "event_type" fields
        if not event_type:
            event_type = event.get("type", "")

        disruption_type = DISRUPTION_TYPE_MAP.get(event_type)

        if not disruption_type:
            # If already classified (e.g. from POST /disruption), use it directly
            disruption_type = event.get("disruption_type") or event.get("type", "unknown")
            if disruption_type not in SEVERITY_MAP:
                disruption_type = "supplier_delay"  # safe default

        severity = SEVERITY_MAP.get(disruption_type, "medium")
        confidence = CONFIDENCE_MAP.get(disruption_type, 0.75)

        # Escalate severity if delay is severe
        payload = event.get("payload", {})
        delay_days = payload.get("delay_days", 0)
        if isinstance(delay_days, (int, float)) and delay_days >= 14:
            severity = "critical"

        log.info(
            "classified_event",
            event_type=event_type,
            disruption_type=disruption_type,
            severity=severity,
            confidence=confidence,
        )
        return ClassificationResult(disruption_type, severity, confidence)

    # Function: _llm_classify
    async def _llm_classify(self, event: dict) -> ClassificationResult:
        """Use the local Ollama model to classify the event."""
        try:
            import json

            prompt = f"""Classify this supply chain disruption event.

Event: {json.dumps(event, indent=2)}

Respond ONLY with valid JSON:
{{
  "type": "<disruption_type>",
  "severity": "<low|medium|high|critical>",
  "confidence": <0.0-1.0>
}}

Valid disruption types: {list(DISRUPTION_TYPE_MAP.values())}
"""
            result = await ollama_chat(
                base_url=self._settings.ollama_base_url,
                model=self._settings.orchestrator_model,
                system="You are a supply chain disruption classifier. Respond with JSON only.",
                user=prompt,
                max_tokens=256,
            )
            import re
            match = re.search(r"\{.*\}", result.text, re.DOTALL)
            if match:
                data = json.loads(match.group())
                return ClassificationResult(
                    data.get("type", "unknown"),
                    data.get("severity", "medium"),
                    float(data.get("confidence", 0.8)),
                )
        except Exception as exc:
            log.warning("llm_classify_failed", error=str(exc))

        # Fallback to mock
        return self._mock_classify(event)
