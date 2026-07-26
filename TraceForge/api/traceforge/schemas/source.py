# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: TraceForge — api/traceforge/schemas (source.py)
# Date: 2026-06-13
# ---------------------------------------------------------------------------
from __future__ import annotations

import uuid

from pydantic import BaseModel


class SourceOut(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    source_type: str
    connector_ref: dict
    filename: str
    doc_class: str
    status: str
    page_count: int | None
    parse_error: str | None

    class Config:
        from_attributes = True


class ChunkOut(BaseModel):
    id: uuid.UUID
    ordinal: int
    text: str
    token_count: int
    locator: dict

    class Config:
        from_attributes = True
