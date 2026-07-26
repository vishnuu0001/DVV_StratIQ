# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Seed data loading endpoint.
# Date: 2026-03-15
# ---------------------------------------------------------------------------
"""Seed data loading endpoint."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from kg.auth import require_api_key
from kg.config import get_settings
from kg.db import get_session
from kg.seed.factory import SeedFactory

router = APIRouter(tags=["seed"], dependencies=[Depends(require_api_key)])


# Function: load_seed
@router.post("/seed", status_code=202)
async def load_seed() -> dict:
    """Load the correlated seed dataset. Idempotent (uses MERGE)."""
    settings = get_settings()
    if not settings.kg_seed_enabled:
        raise HTTPException(
            status_code=403,
            detail={
                "type": "urn:kg:error:seed-disabled",
                "title": "Seed Disabled",
                "status": 403,
                "detail": "KG_SEED_ENABLED is false. Set it to true to allow seeding.",
            },
        )
    async with get_session() as session:
        factory = SeedFactory(session)
        stats = await factory.load()
    return {"status": "seeded", "stats": stats}
