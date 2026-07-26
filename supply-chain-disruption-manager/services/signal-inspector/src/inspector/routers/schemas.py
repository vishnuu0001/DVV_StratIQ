# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: GET /schemas, GET /schemas/{event_type} — serve JSON schemas.
# Date: 2026-03-25
# ---------------------------------------------------------------------------
"""GET /schemas, GET /schemas/{event_type} — serve JSON schemas."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException

from inspector.config import get_settings

router = APIRouter(tags=["schemas"])


# Function: _schema_dir
def _schema_dir() -> Path:
    return get_settings().schemas_dir


# Function: list_schemas
@router.get("/schemas")
async def list_schemas() -> dict[str, Any]:
    """List all available event type schemas."""
    schema_dir = _schema_dir()
    schemas = []
    for path in sorted(schema_dir.glob("*.json")):
        event_type = path.stem  # filename without .json
        schemas.append(
            {
                "event_type": event_type,
                "file": path.name,
            }
        )
    return {"schemas": schemas, "count": len(schemas)}


# Function: get_schema
@router.get("/schemas/{event_type:path}")
async def get_schema(event_type: str) -> dict[str, Any]:
    """Return the JSON schema for a specific event type.

    event_type uses dot notation: supplier.po.delayed
    """
    schema_dir = _schema_dir()
    schema_path = schema_dir / f"{event_type}.json"

    if not schema_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"No schema found for event type '{event_type}'",
        )

    with schema_path.open("r", encoding="utf-8") as fh:
        return json.load(fh)
