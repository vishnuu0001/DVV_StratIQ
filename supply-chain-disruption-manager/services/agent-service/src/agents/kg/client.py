# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: KG Service HTTP client wrapper.
# Date: 2026-03-10
# ---------------------------------------------------------------------------
"""KG Service HTTP client wrapper."""
from __future__ import annotations

import structlog
import httpx

from agents.config import get_settings

log = structlog.get_logger(__name__)

_MOCK_GRAPH = {
    "nodes": [
        {"id": "SUP-001", "kind": "Supplier", "label": "Acme Metals", "domain": "supply"},
        {"id": "SUP-002", "kind": "Supplier", "label": "Global Plastics", "domain": "supply"},
        {"id": "MAT-RAW-001", "kind": "Material", "label": "Steel Coil", "domain": "material"},
        {"id": "MAT-RAW-002", "kind": "Material", "label": "ABS Resin", "domain": "material"},
        {"id": "PO-10001", "kind": "PurchaseOrder", "label": "PO-10001", "domain": "procurement"},
        {"id": "WH-001", "kind": "Warehouse", "label": "Central DC", "domain": "warehouse"},
        {"id": "WC-001", "kind": "WorkCenter", "label": "Assembly Line A", "domain": "production"},
        {"id": "SKU-PROD-001", "kind": "SKU", "label": "Widget A", "domain": "product"},
        {"id": "ROUTE-001", "kind": "ShipmentRoute", "label": "Supplier to DC", "domain": "logistics"},
        {"id": "SHIPMENT-001", "kind": "Shipment", "label": "SHP-2026-001", "domain": "logistics"},
        {"id": "ORD-2001", "kind": "SalesOrder", "label": "SO-2001", "domain": "demand"},
    ],
    "edges": [
        {"from": "SUP-001", "to": "MAT-RAW-001", "kind": "SUPPLIES"},
        {"from": "SUP-001", "to": "PO-10001", "kind": "HAS_PO"},
        {"from": "MAT-RAW-001", "to": "SKU-PROD-001", "kind": "USED_IN"},
        {"from": "PO-10001", "to": "SHIPMENT-001", "kind": "FULFILLED_BY"},
        {"from": "SHIPMENT-001", "to": "WH-001", "kind": "DESTINED_FOR"},
        {"from": "WH-001", "to": "WC-001", "kind": "SUPPLIES"},
        {"from": "WC-001", "to": "SKU-PROD-001", "kind": "PRODUCES"},
        {"from": "SKU-PROD-001", "to": "ORD-2001", "kind": "FULFILLS"},
    ],
}

_MOCK_OWNERS = {
    "SUP-001": [
        {"id": "USR-101", "name": "Alice Johnson", "role": "Procurement Manager", "email": "alice@example.com"},
        {"id": "USR-102", "name": "Bob Smith", "role": "Buyer", "email": "bob@example.com"},
    ],
    "WH-001": [
        {"id": "USR-201", "name": "Carol Lee", "role": "Warehouse Manager", "email": "carol@example.com"},
    ],
    "WC-001": [
        {"id": "USR-301", "name": "Dan Brown", "role": "Production Planner", "email": "dan@example.com"},
    ],
    "default": [
        {"id": "USR-001", "name": "Supply Chain Manager", "role": "SC Manager", "email": "sc@example.com"},
    ],
}


# Function: _expand_frontier
def _expand_frontier(
    frontier: list[str],
    visited: set[str],
    all_nodes: dict[str, dict],
    edges: list[dict],
    result_nodes: list[dict],
    result_edges: list[dict],
) -> list[str]:
    """Advance one BFS layer over the mock graph, mutating visited/result_* in place."""
    next_frontier: list[str] = []
    for node_id in frontier:
        if node_id in visited:
            continue
        visited.add(node_id)
        if node_id in all_nodes:
            result_nodes.append(all_nodes[node_id])
        for edge in edges:
            if edge["from"] == node_id and edge["to"] not in visited:
                result_edges.append(edge)
                next_frontier.append(edge["to"])
    return next_frontier


class KGClient:
    """HTTP client for the Knowledge Graph service."""

    # Function: __init__
    def __init__(self, base_url: str, api_key: str) -> None:
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            headers={"X-API-Key": api_key},
            timeout=10.0,
        )

    # Function: traverse
    async def traverse(
        self,
        root_id: str,
        edge_kinds: list[str] | None = None,
        direction: str = "outbound",
        max_depth: int = 6,
    ) -> dict:
        """Traverse the KG from root_id and return affected nodes/edges."""
        try:
            params: dict = {"direction": direction, "max_depth": max_depth}
            if edge_kinds:
                params["edge_kinds"] = ",".join(edge_kinds)
            resp = await self._client.get(f"/graph/traverse/{root_id}", params=params)
            resp.raise_for_status()
            return resp.json()
        except Exception as exc:
            log.warning("kg_traverse_failed", root_id=root_id, error=str(exc))
            return self._mock_traverse(root_id)

    # Function: get_owners
    async def get_owners(
        self, node_id: str, include_transitive: bool = True
    ) -> list[dict]:
        """Get owners/responsible parties for a node."""
        try:
            resp = await self._client.get(
                f"/graph/owners/{node_id}",
                params={"include_transitive": str(include_transitive).lower()},
            )
            resp.raise_for_status()
            return resp.json()
        except Exception as exc:
            log.warning("kg_owners_failed", node_id=node_id, error=str(exc))
            return _MOCK_OWNERS.get(node_id, _MOCK_OWNERS["default"])

    # Function: get_entity
    async def get_entity(self, kind: str, entity_id: str) -> dict | None:
        """Get a single entity by kind and ID."""
        try:
            resp = await self._client.get(f"/entities/{kind}/{entity_id}")
            if resp.status_code == 404:
                return None
            resp.raise_for_status()
            return resp.json()
        except Exception as exc:
            log.warning("kg_entity_failed", kind=kind, id=entity_id, error=str(exc))
            # Return mock entity
            for node in _MOCK_GRAPH["nodes"]:
                if node["id"] == entity_id and node["kind"] == kind:
                    return node
            return {"id": entity_id, "kind": kind, "label": entity_id}

    # Function: health
    async def health(self) -> bool:
        """Check KG service health."""
        try:
            resp = await self._client.get("/health", timeout=3.0)
            return resp.status_code == 200
        except Exception:
            return False

    # Function: close
    async def close(self) -> None:
        await self._client.aclose()

    # Function: _mock_traverse
    def _mock_traverse(self, root_id: str) -> dict:
        """Return a subset of the mock graph reachable from root_id."""
        visited: set[str] = set()
        frontier = [root_id]
        result_nodes = []
        result_edges = []

        all_nodes = {n["id"]: n for n in _MOCK_GRAPH["nodes"]}
        edges = _MOCK_GRAPH["edges"]

        for _ in range(6):
            frontier = _expand_frontier(frontier, visited, all_nodes, edges, result_nodes, result_edges)
            if not frontier:
                break

        return {"nodes": result_nodes, "edges": result_edges, "root_id": root_id}


_kg_client: KGClient | None = None


# Function: get_kg_client
def get_kg_client() -> KGClient:
    global _kg_client  # noqa: PLW0603
    if _kg_client is None:
        settings = get_settings()
        _kg_client = KGClient(settings.kg_base_url, settings.kg_api_key)
    return _kg_client
