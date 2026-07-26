# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Stage 1: JSON Schema validation of event payload.
# Date: 2026-01-12
# ---------------------------------------------------------------------------
"""Stage 1: JSON Schema validation of event payload."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import jsonschema
import structlog

from inspector.config import get_settings
from inspector.envelope import AdapterEvent, ValidationResult

logger = structlog.get_logger(__name__)

_schema_cache: dict[str, dict[str, Any]] = {}


# Function: _load_schema
def _load_schema(event_type: str) -> dict[str, Any] | None:
    """Load and cache JSON schema for an event type. Returns None if not found."""
    if event_type in _schema_cache:
        return _schema_cache[event_type]

    settings = get_settings()
    schema_path: Path = settings.schemas_dir / f"{event_type}.json"

    if not schema_path.exists():
        logger.warning("validate.schema_not_found", event_type=event_type)
        return None

    with schema_path.open("r", encoding="utf-8") as fh:
        schema = json.load(fh)

    _schema_cache[event_type] = schema
    return schema


# Function: validate_event
def validate_event(adapter_event: AdapterEvent) -> ValidationResult:
    """Validate adapter_event.raw_payload against its JSON schema.

    Returns ValidationResult(valid=True) if schema not found (pass-with-warning).
    Returns ValidationResult(valid=False, errors=[...]) on schema violations.
    """
    schema = _load_schema(adapter_event.event_type)

    if schema is None:
        # No schema registered — pass through with a warning
        return ValidationResult(valid=True, errors=[])

    validator = jsonschema.Draft202012Validator(schema)
    errors = [
        f"{'.'.join(str(p) for p in err.absolute_path) or '$'}: {err.message}"
        for err in validator.iter_errors(adapter_event.raw_payload)
    ]

    if errors:
        logger.info(
            "validate.invalid",
            event_type=adapter_event.event_type,
            source_system=adapter_event.source_system,
            error_count=len(errors),
        )
        return ValidationResult(valid=False, errors=errors)

    return ValidationResult(valid=True, errors=[])
