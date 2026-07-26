# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Qdrant persistence layer for critical/high ServiceNow incidents.
# Date: 2026-04-16
# ---------------------------------------------------------------------------
"""
Qdrant persistence layer for critical/high ServiceNow incidents.

Uses Qdrant purely as a document store (1-D dummy vector) — no semantic
search is performed.  This ensures critical incidents survive backend
restarts and are available immediately on startup without a full re-sync.
"""

import hashlib
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, PointStruct, VectorParams, Filter, FieldCondition, MatchValue
    _QDRANT_AVAILABLE = True
except ImportError:
    _QDRANT_AVAILABLE = False
    logger.warning("qdrant-client not installed — critical alert persistence disabled")


# Function: _number_to_point_id
def _number_to_point_id(number: str) -> int:
    """Convert an incident number to a stable positive int64 Qdrant point ID."""
    return abs(int(hashlib.sha256(number.encode()).hexdigest()[:15], 16))


class CriticalAlertStore:
    """
    Persist and retrieve critical/high ServiceNow incidents via Qdrant.

    Thread-safe; all public methods catch and log exceptions so callers
    never need to handle Qdrant errors themselves.
    """

    _VECTOR_DIM = 1  # dummy dimension — we use Qdrant as a key-value store

    # Function: __init__
    def __init__(self, url: str, collection: str, timeout: int = 10) -> None:
        self._collection = collection
        self._client: Optional[Any] = None

        if not _QDRANT_AVAILABLE:
            return

        try:
            self._client = QdrantClient(url=url, timeout=timeout)
            self._ensure_collection()
            logger.info(
                "CriticalAlertStore connected: %s  collection=%s", url, collection
            )
        except Exception as exc:
            logger.warning(
                "CriticalAlertStore: Qdrant unavailable (%s) — persistence disabled", exc
            )
            self._client = None

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    # Function: _ensure_collection
    def _ensure_collection(self) -> None:
        if not self._client:
            return
        try:
            existing = {c.name for c in self._client.get_collections().collections}
            if self._collection not in existing:
                self._client.create_collection(
                    collection_name=self._collection,
                    vectors_config=VectorParams(
                        size=self._VECTOR_DIM, distance=Distance.COSINE
                    ),
                )
                logger.info("Created Qdrant collection: %s", self._collection)
        except Exception as exc:
            logger.warning("Could not ensure Qdrant collection '%s': %s", self._collection, exc)
            self._client = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    # Function: available
    @property
    def available(self) -> bool:
        return self._client is not None

    # Function: upsert
    def upsert(self, incident: Dict[str, Any]) -> bool:
        """Persist a single incident record.  Returns True on success."""
        if not self._client:
            return False
        try:
            point_id = _number_to_point_id(incident["number"])
            # Sanitise payload — convert any non-serialisable values to str
            payload = {k: (str(v) if not isinstance(v, (str, int, float, bool, type(None))) else v)
                       for k, v in incident.items()}
            self._client.upsert(
                collection_name=self._collection,
                points=[PointStruct(id=point_id, vector=[1.0], payload=payload)],
            )
            logger.debug("Qdrant upsert OK: %s (id=%d)", incident["number"], point_id)
            return True
        except Exception as exc:
            logger.warning("Qdrant upsert failed for %s: %s", incident.get("number"), exc)
            return False

    # Function: load_all
    def load_all(self) -> List[Dict[str, Any]]:
        """Return all persisted incident payloads."""
        if not self._client:
            return []
        results: List[Dict[str, Any]] = []
        try:
            offset = None
            while True:
                batch, offset = self._client.scroll(
                    collection_name=self._collection,
                    limit=200,
                    offset=offset,
                    with_payload=True,
                    with_vectors=False,
                )
                results.extend(p.payload for p in batch)
                if offset is None:
                    break
        except Exception as exc:
            logger.warning("Qdrant load_all failed: %s", exc)
        return results

    # Function: delete
    def delete(self, number: str) -> bool:
        """Remove a persisted incident by its number."""
        if not self._client:
            return False
        try:
            point_id = _number_to_point_id(number)
            self._client.delete(
                collection_name=self._collection,
                points_selector=[point_id],
            )
            return True
        except Exception as exc:
            logger.warning("Qdrant delete failed for %s: %s", number, exc)
            return False

    # Function: mark_resolved
    def mark_resolved(self, number: str) -> bool:
        """Update the state of a persisted incident to 'resolved'."""
        if not self._client:
            return False
        try:
            point_id = _number_to_point_id(number)
            self._client.set_payload(
                collection_name=self._collection,
                payload={"state": "6 - Resolved", "_resolved": True},
                points=[point_id],
            )
            return True
        except Exception as exc:
            logger.warning("Qdrant mark_resolved failed for %s: %s", number, exc)
            return False
