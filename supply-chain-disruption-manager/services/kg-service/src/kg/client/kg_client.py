# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Async httpx-based client for the KG service.
# Date: 2025-09-16
# ---------------------------------------------------------------------------
"""Async httpx-based client for the KG service."""
from __future__ import annotations

from typing import Any

import httpx


class KGClient:
    """Async client for the KG (Knowledge Graph) service.

    Usage::

        async with KGClient("http://localhost:8001", api_key="dev-key") as client:
            entity = await client.get_entity("Supplier", "SUP-001")
    """

    # Function: __init__
    def __init__(self, base_url: str, api_key: str, timeout: float = 30.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._headers = {"X-API-Key": api_key, "Content-Type": "application/json"}
        self._timeout = timeout
        self._client: httpx.AsyncClient | None = None

    # Function: __aenter__
    async def __aenter__(self) -> "KGClient":
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            headers=self._headers,
            timeout=self._timeout,
        )
        return self

    # Function: __aexit__
    async def __aexit__(self, *args: Any) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None

    # Function: _get_client
    def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            raise RuntimeError("KGClient must be used as an async context manager")
        return self._client

    # Function: health
    async def health(self) -> dict[str, Any]:
        """Check KG service health."""
        resp = await self._get_client().get("/health")
        resp.raise_for_status()
        return resp.json()

    # Function: get_entity
    async def get_entity(self, kind: str, entity_id: str) -> dict[str, Any]:
        """Fetch a single entity by kind and ID."""
        resp = await self._get_client().get(f"/entity/{kind}/{entity_id}")
        resp.raise_for_status()
        return resp.json()

    # Function: create_entity
    async def create_entity(self, kind: str, body: dict[str, Any]) -> dict[str, Any]:
        """Create or upsert an entity."""
        resp = await self._get_client().post(f"/entity/{kind}", json=body)
        resp.raise_for_status()
        return resp.json()

    # Function: patch_entity
    async def patch_entity(self, kind: str, entity_id: str, updates: dict[str, Any]) -> dict[str, Any]:
        """Partially update an entity."""
        resp = await self._get_client().patch(f"/entity/{kind}/{entity_id}", json=updates)
        resp.raise_for_status()
        return resp.json()

    # Function: delete_entity
    async def delete_entity(self, kind: str, entity_id: str) -> dict[str, Any]:
        """Soft-delete an entity (sets status=DELETED)."""
        resp = await self._get_client().delete(f"/entity/{kind}/{entity_id}")
        resp.raise_for_status()
        return resp.json()

    # Function: list_entities
    async def list_entities(
        self,
        kind: str,
        status: str = "ACTIVE",
        limit: int = 50,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """List entities of a given kind with cursor pagination."""
        params: dict[str, Any] = {"status": status, "limit": limit}
        if cursor:
            params["cursor"] = cursor
        resp = await self._get_client().get(f"/entity/{kind}", params=params)
        resp.raise_for_status()
        return resp.json()

    # Function: create_edge
    async def create_edge(
        self,
        from_id: str,
        to_id: str,
        kind: str,
        verb: str,
        properties: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create or update an edge between two entities."""
        body: dict[str, Any] = {
            "from_id": from_id,
            "to_id": to_id,
            "kind": kind,
            "verb": verb,
        }
        if properties:
            body["properties"] = properties
        resp = await self._get_client().post("/edge", json=body)
        resp.raise_for_status()
        return resp.json()

    # Function: traverse
    async def traverse(
        self,
        root_id: str,
        edge_kinds: list[str] | None = None,
        direction: str = "outbound",
        max_depth: int = 6,
    ) -> dict[str, Any]:
        """Traverse the graph from a root node."""
        params: dict[str, Any] = {
            "root_id": root_id,
            "edge_kinds": ",".join(edge_kinds) if edge_kinds else "flow,meta",
            "direction": direction,
            "max_depth": max_depth,
        }
        resp = await self._get_client().get("/traverse", params=params)
        resp.raise_for_status()
        return resp.json()

    # Function: get_owners
    async def get_owners(
        self,
        node_id: str,
        include_transitive: bool = True,
    ) -> list[dict[str, Any]]:
        """Return Person nodes that own the given node."""
        params: dict[str, Any] = {
            "node_id": node_id,
            "include_transitive": str(include_transitive).lower(),
        }
        resp = await self._get_client().get("/owners", params=params)
        resp.raise_for_status()
        data = resp.json()
        return data.get("owners", data) if isinstance(data, dict) else data

    # Function: search
    async def search(
        self,
        query: str,
        kind: str | None = None,
        domain: str | None = None,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """Full-text search over entity text properties."""
        body: dict[str, Any] = {"query": query, "limit": limit}
        if kind:
            body["kind"] = kind
        if domain:
            body["domain"] = domain
        resp = await self._get_client().post("/search", json=body)
        resp.raise_for_status()
        data = resp.json()
        return data.get("results", data) if isinstance(data, dict) else data

    # Function: seed
    async def seed(self) -> dict[str, Any]:
        """Trigger loading of the seed dataset."""
        resp = await self._get_client().post("/seed")
        resp.raise_for_status()
        return resp.json()
