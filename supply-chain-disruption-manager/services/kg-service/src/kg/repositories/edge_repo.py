# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Edge CRUD operations in Neo4j.
# Date: 2026-04-24
# ---------------------------------------------------------------------------
"""Edge CRUD operations in Neo4j."""
from __future__ import annotations

import json
from typing import Any

import structlog
from neo4j import AsyncSession

log = structlog.get_logger(__name__)


class EdgeRepository:
    # Function: __init__
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # Function: upsert
    async def upsert(self, edge: dict[str, Any]) -> dict[str, Any]:
        """MERGE edge between two entities.

        Neo4j relationship type is the uppercase kind (FLOW/OWNS/META).
        The verb and other properties are stored as relationship properties.
        """
        rel_type = edge["kind"].upper()
        props = {
            "kind": edge["kind"],
            "verb": edge["verb"],
            "properties": json.dumps(edge.get("properties", {})),
            "created_at": edge.get("created_at", "").isoformat() if hasattr(edge.get("created_at"), "isoformat") else str(edge.get("created_at", "")),
            "updated_at": edge.get("updated_at", "").isoformat() if hasattr(edge.get("updated_at"), "isoformat") else str(edge.get("updated_at", "")),
        }
        cypher = f"""
        MATCH (a:Entity {{id: $from_id}})
        MATCH (b:Entity {{id: $to_id}})
        MERGE (a)-[r:{rel_type} {{verb: $verb}}]->(b)
        SET r += $props
        RETURN r, a.id AS from_id, b.id AS to_id
        """
        result = await self._session.run(
            cypher,
            from_id=edge["from_id"],
            to_id=edge["to_id"],
            verb=edge["verb"],
            props=props,
        )
        record = await result.single()
        if record is None:
            raise ValueError(
                f"Could not create edge: from={edge['from_id']} to={edge['to_id']} "
                f"kind={edge['kind']} verb={edge['verb']}. Check both nodes exist."
            )
        rel_props = dict(record["r"])
        rel_props["from_id"] = record["from_id"]
        rel_props["to_id"] = record["to_id"]
        if "properties" in rel_props and isinstance(rel_props["properties"], str):
            rel_props["properties"] = json.loads(rel_props["properties"])
        return rel_props

    # Function: count_edges
    async def count_edges(self) -> int:
        result = await self._session.run("MATCH ()-[r]->() RETURN count(r) AS cnt")
        record = await result.single()
        return int(record["cnt"]) if record else 0
