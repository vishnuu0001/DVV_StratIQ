# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Stage 2: Deduplication using Redis with 24-hour TTL.
# Date: 2025-11-21
# ---------------------------------------------------------------------------
"""Stage 2: Deduplication using Redis with 24-hour TTL."""

from __future__ import annotations

import structlog
from redis.asyncio import Redis

logger = structlog.get_logger(__name__)

DEDUPE_TTL_SECONDS = 86_400  # 24 hours
DEDUPE_KEY_PREFIX = "inspector:dedupe"


# Function: is_duplicate
async def is_duplicate(
    redis: Redis,
    source_system: str,
    source_event_id: str | None,
) -> bool:
    """Return True if this event has already been processed.

    If source_event_id is None, deduplication is skipped (returns False).
    Sets the dedupe key with 24h TTL on first encounter.
    """
    if not source_event_id:
        return False

    key = f"{DEDUPE_KEY_PREFIX}:{source_system}:{source_event_id}"

    # SET NX (only if not exists) — returns True if set, False if already existed
    was_set = await redis.set(key, "1", ex=DEDUPE_TTL_SECONDS, nx=True)

    if not was_set:
        logger.info(
            "dedupe.duplicate_skipped",
            source_system=source_system,
            source_event_id=source_event_id,
            key=key,
        )
        return True

    return False
