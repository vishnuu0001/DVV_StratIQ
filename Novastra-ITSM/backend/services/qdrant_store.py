# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Qdrant helpers for semantic search and vector indexing.
# Date: 2025-08-22
# ---------------------------------------------------------------------------
"""Qdrant helpers for semantic search and vector indexing."""
from __future__ import annotations

import logging
from functools import lru_cache
from typing import Any

import backend.config as cfg

logger = logging.getLogger(__name__)


class QdrantUnavailableError(RuntimeError):
    pass


# Function: qdrant_enabled
def qdrant_enabled() -> bool:
    return cfg.VECTOR_BACKEND in {"qdrant", "hybrid"} and bool((cfg.QDRANT_URL or "").strip())


# Function: get_qdrant_client
@lru_cache(maxsize=1)
def get_qdrant_client():
    if not qdrant_enabled():
        raise QdrantUnavailableError("Qdrant backend is disabled by configuration.")

    try:
        from qdrant_client import QdrantClient
    except Exception as exc:
        raise QdrantUnavailableError(
            "qdrant-client is not installed. Add qdrant-client to backend requirements."
        ) from exc

    return QdrantClient(
        url=cfg.QDRANT_URL,
        api_key=cfg.QDRANT_API_KEY or None,
        timeout=max(5.0, float(cfg.QDRANT_TIMEOUT_SECONDS)),
        prefer_grpc=bool(cfg.QDRANT_PREFER_GRPC),
    )


# Function: ensure_collection
def ensure_collection(vector_size: int) -> None:
    if vector_size <= 0:
        raise ValueError("vector_size must be greater than zero")

    client = get_qdrant_client()
    try:
        existing = client.get_collection(cfg.QDRANT_COLLECTION)
        configured_size = int(existing.config.params.vectors.size)
        if configured_size != int(vector_size):
            if cfg.QDRANT_RECREATE_COLLECTION:
                client.delete_collection(cfg.QDRANT_COLLECTION)
            else:
                raise RuntimeError(
                    f"Qdrant collection '{cfg.QDRANT_COLLECTION}' has vector size {configured_size}, "
                    f"expected {vector_size}. Enable QDRANT_RECREATE_COLLECTION=true to recreate."
                )
    except Exception:
        # create if missing or recreated above
        pass

    try:
        from qdrant_client.models import Distance, VectorParams

        client.create_collection(
            collection_name=cfg.QDRANT_COLLECTION,
            vectors_config=VectorParams(size=int(vector_size), distance=Distance.COSINE),
        )
        logger.info("Qdrant collection ready: %s (size=%s)", cfg.QDRANT_COLLECTION, vector_size)
    except Exception:
        # create_collection raises if collection already exists - safe to ignore
        pass


# Function: upsert_points
def upsert_points(points: list[dict[str, Any]]) -> int:
    if not points:
        return 0

    client = get_qdrant_client()

    try:
        from qdrant_client.models import PointStruct

        converted = [
            PointStruct(id=p["id"], vector=p["vector"], payload=p.get("payload") or {})
            for p in points
        ]
        
        # DEBUG: Log first point to verify payload
        if converted and logger.isEnabledFor(logging.DEBUG):
            first_pt = converted[0]
            logger.debug(
                "Upserting %d points. First point: id=%s, has_vector=%s, payload_keys=%s",
                len(converted),
                first_pt.id,
                bool(first_pt.vector),
                list(first_pt.payload.keys()) if first_pt.payload else "EMPTY"
            )
        
        client.upsert(collection_name=cfg.QDRANT_COLLECTION, points=converted)
    except Exception as exc:
        raise RuntimeError(f"Qdrant upsert failed: {exc}") from exc

    return len(points)


# Function: search_by_vector
def search_by_vector(vector: list[float], limit: int = 8) -> list[Any]:
    if not vector:
        return []

    client = get_qdrant_client()
    try:
        # Use query_points API (qdrant-client 1.x+)
        result = client.query_points(
            collection_name=cfg.QDRANT_COLLECTION,
            query=vector,
            limit=max(1, int(limit)),
            with_payload=True,
        )
        # query_points returns a QueryResponse object with .points attribute
        # Extract the list of ScoredPoint objects
        if hasattr(result, 'points'):
            return list(result.points) if result.points else []
        # Fallback: if result is a tuple/list, try to extract points
        elif isinstance(result, (tuple, list)) and len(result) > 1:
            return list(result[1]) if result[1] else []
        else:
            return list(result) if result else []
    except Exception as exc:
        raise RuntimeError(f"Qdrant search failed: {exc}") from exc


# Function: get_points_count
def get_points_count() -> int:
    if not qdrant_enabled():
        return 0

    try:
        client = get_qdrant_client()
        info = client.get_collection(cfg.QDRANT_COLLECTION)
        return int(info.points_count or 0)
    except Exception:
        return 0
