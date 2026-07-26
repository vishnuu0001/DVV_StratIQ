# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: TraceForge — api/traceforge/schemas (requirement.py)
# Date: 2025-10-11
# ---------------------------------------------------------------------------
from __future__ import annotations

import uuid

from pydantic import BaseModel


class CitationOut(BaseModel):
    id: uuid.UUID
    chunk_id: uuid.UUID
    relevance: float
    quoted_span: str
    locator: dict
    source_document_filename: str

    class Config:
        from_attributes = True


class RequirementOut(BaseModel):
    id: uuid.UUID
    req_id: str
    project_id: uuid.UUID
    level: str
    title: str
    statement: str
    ears_pattern: str
    ears_parts: dict
    rationale: str | None
    acceptance_criteria: list
    priority: str
    ambiguity_score: float
    ambiguity_flags: list
    status: str
    version: int
    created_by_agent: bool
    merged_into_id: uuid.UUID | None = None
    conflict_flags: list = []

    class Config:
        from_attributes = True


class RequirementDetailOut(RequirementOut):
    citations: list[CitationOut]


class RequirementPatchOut(RequirementOut):
    # Populated only when this edit triggered §6.2 suspect propagation.
    suspect_impact: dict | None = None


class RequirementPatch(BaseModel):
    title: str | None = None
    statement: str | None = None
    level: str | None = None
    priority: str | None = None
    acceptance_criteria: list[str] | None = None
    status: str | None = None
