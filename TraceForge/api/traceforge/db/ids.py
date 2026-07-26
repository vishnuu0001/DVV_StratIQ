# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: P5: deterministic, stable, never-reused IDs (REQ-0001, TC-0001, TS-0001).
# Date: 2026-05-16
# ---------------------------------------------------------------------------
"""P5: deterministic, stable, never-reused IDs (REQ-0001, TC-0001, TS-0001)."""
from __future__ import annotations

import uuid

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


# Function: allocate_next_id
async def allocate_next_id(session: AsyncSession, project_id: uuid.UUID, prefix: str, width: int = 4) -> str:
    """Atomically increments the per-(project, prefix) counter and returns e.g. 'REQ-0001'.
    Uses an upsert so the first call for a given (project, prefix) initialises at 1."""
    result = await session.execute(
        text(
            """
            INSERT INTO id_sequence (project_id, prefix, next_value)
            VALUES (:project_id, :prefix, 1)
            ON CONFLICT (project_id, prefix)
            DO UPDATE SET next_value = id_sequence.next_value + 1
            RETURNING next_value
            """
        ),
        {"project_id": str(project_id), "prefix": prefix},
    )
    next_value = result.scalar_one()
    return f"{prefix}-{next_value:0{width}d}"
