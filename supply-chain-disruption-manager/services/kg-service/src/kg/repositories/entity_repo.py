# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: CRUD operations for Entity nodes in Neo4j.
# Date: 2026-03-06
# ---------------------------------------------------------------------------
"""CRUD operations for Entity nodes in Neo4j."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

import structlog
from neo4j import AsyncSession

log = structlog.get_logger(__name__)

# Fields whose values are stored as JSON strings in Neo4j
_JSON_FIELDS = {"components", "handling_units", "metadata"}


# Function: _serialise_for_neo4j
def _serialise_for_neo4j(data: dict[str, Any]) -> dict[str, Any]:
    """Convert Python types to Neo4j-compatible flat properties."""
    result: dict[str, Any] = {}
    for k, v in data.items():
        if k in _JSON_FIELDS:
            result[k] = json.dumps(v)
        elif hasattr(v, "isoformat"):
            result[k] = v.isoformat()
        elif isinstance(v, list):
            result[k] = json.dumps(v)
        else:
            # Decimal -> str for storage; Neo4j driver handles int/float/str/bool
            result[k] = str(v) if hasattr(v, "__round__") and not isinstance(v, (int, float, bool)) else v
    return result


# Function: _deserialise_from_neo4j
def _deserialise_from_neo4j(props: dict[str, Any]) -> dict[str, Any]:
    """Convert flat Neo4j properties back to Python types."""
    result = dict(props)
    for field in _JSON_FIELDS:
        if field in result and isinstance(result[field], str):
            result[field] = json.loads(result[field])
    return result


class EntityRepository:
    # Function: __init__
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # Function: upsert
    async def upsert(self, entity: dict[str, Any]) -> dict[str, Any]:
        """MERGE entity by id, SET all properties."""
        kind = entity["kind"]
        props = _serialise_for_neo4j(entity)
        cypher = f"""
        MERGE (n:Entity {{id: $id}})
        SET n:{kind}
        SET n += $props
        RETURN n
        """
        result = await self._session.run(cypher, id=entity["id"], props=props)
        record = await result.single()
        if record is None:
            raise RuntimeError(f"Upsert failed for id={entity['id']}")
        return _deserialise_from_neo4j(dict(record["n"]))

    # Function: get_by_id
    async def get_by_id(self, entity_id: str) -> dict[str, Any] | None:
        """Fetch a single entity by id."""
        result = await self._session.run(
            "MATCH (n:Entity {id: $id}) RETURN n",
            id=entity_id,
        )
        record = await result.single()
        if record is None:
            return None
        return _deserialise_from_neo4j(dict(record["n"]))

    # Function: get_by_kind_and_id
    async def get_by_kind_and_id(self, kind: str, entity_id: str) -> dict[str, Any] | None:
        """Fetch entity ensuring it matches the given kind."""
        result = await self._session.run(
            "MATCH (n:Entity {id: $id, kind: $kind}) RETURN n",
            id=entity_id,
            kind=kind,
        )
        record = await result.single()
        if record is None:
            return None
        return _deserialise_from_neo4j(dict(record["n"]))

    # Function: patch
    async def patch(self, kind: str, entity_id: str, updates: dict[str, Any]) -> dict[str, Any] | None:
        """Partial update of entity properties."""
        updates["updated_at"] = datetime.now(timezone.utc).isoformat()
        props = _serialise_for_neo4j(updates)
        result = await self._session.run(
            """
            MATCH (n:Entity {id: $id, kind: $kind})
            SET n += $props
            RETURN n
            """,
            id=entity_id,
            kind=kind,
            props=props,
        )
        record = await result.single()
        if record is None:
            return None
        return _deserialise_from_neo4j(dict(record["n"]))

    # Function: soft_delete
    async def soft_delete(self, kind: str, entity_id: str) -> dict[str, Any] | None:
        """Set status=DELETED on entity."""
        result = await self._session.run(
            """
            MATCH (n:Entity {id: $id, kind: $kind})
            SET n.status = 'DELETED', n.updated_at = $ts
            RETURN n
            """,
            id=entity_id,
            kind=kind,
            ts=datetime.now(timezone.utc).isoformat(),
        )
        record = await result.single()
        if record is None:
            return None
        return _deserialise_from_neo4j(dict(record["n"]))

    # Function: list_by_kind
    async def list_by_kind(
        self,
        kind: str,
        status: str = "ACTIVE",
        limit: int = 50,
        cursor: str | None = None,
    ) -> tuple[list[dict[str, Any]], str | None]:
        """Return a page of entities with cursor-based pagination."""
        if cursor:
            result = await self._session.run(
                """
                MATCH (n:Entity {kind: $kind, status: $status})
                WHERE n.id > $cursor
                RETURN n ORDER BY n.id LIMIT $limit
                """,
                kind=kind,
                status=status,
                cursor=cursor,
                limit=limit,
            )
        else:
            result = await self._session.run(
                """
                MATCH (n:Entity {kind: $kind, status: $status})
                RETURN n ORDER BY n.id LIMIT $limit
                """,
                kind=kind,
                status=status,
                limit=limit,
            )
        records = await result.data()
        items = [_deserialise_from_neo4j(dict(r["n"])) for r in records]
        next_cursor = items[-1]["id"] if len(items) == limit else None
        return items, next_cursor

    # Function: count_nodes
    async def count_nodes(self) -> int:
        result = await self._session.run("MATCH (n:Entity) RETURN count(n) AS cnt")
        record = await result.single()
        return int(record["cnt"]) if record else 0

    # Function: search
    async def search(
        self,
        query: str,
        kind: str | None,
        domain: str | None,
        limit: int,
    ) -> list[dict[str, Any]]:
        """Full-text CONTAINS search over id, name, description."""
        filters = []
        params: dict[str, Any] = {"q": query, "limit": limit}
        if kind:
            filters.append("n.kind = $kind")
            params["kind"] = kind
        if domain:
            filters.append("n.domain = $domain")
            params["domain"] = domain

        where_clause = "WHERE " + " AND ".join(filters) if filters else ""
        cypher = f"""
        MATCH (n:Entity)
        {where_clause}
        {"AND" if filters else "WHERE"} (
            toLower(n.id) CONTAINS toLower($q)
            OR (n.name IS NOT NULL AND toLower(n.name) CONTAINS toLower($q))
            OR (n.description IS NOT NULL AND toLower(n.description) CONTAINS toLower($q))
        )
        RETURN n LIMIT $limit
        """
        # Fix double WHERE if no kind/domain filters
        if not filters:
            cypher = """
        MATCH (n:Entity)
        WHERE (
            toLower(n.id) CONTAINS toLower($q)
            OR (n.name IS NOT NULL AND toLower(n.name) CONTAINS toLower($q))
            OR (n.description IS NOT NULL AND toLower(n.description) CONTAINS toLower($q))
        )
        RETURN n LIMIT $limit
        """
        else:
            cypher = f"""
        MATCH (n:Entity)
        WHERE {" AND ".join(filters)}
        AND (
            toLower(n.id) CONTAINS toLower($q)
            OR (n.name IS NOT NULL AND toLower(n.name) CONTAINS toLower($q))
            OR (n.description IS NOT NULL AND toLower(n.description) CONTAINS toLower($q))
        )
        RETURN n LIMIT $limit
        """
        result = await self._session.run(cypher, **params)
        records = await result.data()
        return [_deserialise_from_neo4j(dict(r["n"])) for r in records]
