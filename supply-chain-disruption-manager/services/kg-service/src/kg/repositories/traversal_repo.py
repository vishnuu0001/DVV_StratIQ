# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Graph traversal and ownership queries.
# Date: 2025-09-13
# ---------------------------------------------------------------------------
"""Graph traversal and ownership queries."""
from __future__ import annotations

import json
from typing import Any

import structlog
from neo4j import AsyncSession

log = structlog.get_logger(__name__)


# Function: _node_to_dict
def _node_to_dict(node: Any, depth: int = 0) -> dict[str, Any]:
    props = dict(node)
    # Deserialise JSON string fields
    for field in ("components", "handling_units", "metadata"):
        if field in props and isinstance(props[field], str):
            props[field] = json.loads(props[field])
    return {
        "id": props.get("id", ""),
        "kind": props.get("kind", ""),
        "domain": props.get("domain", ""),
        "depth": depth,
        "properties": props,
    }


# Function: _arrow_pattern
def _arrow_pattern(direction: str, type_filter: str, max_depth: int) -> str:
    if direction == "outbound":
        return f"-[r:{type_filter}*1..{max_depth}]->"
    if direction == "inbound":
        return f"<-[r:{type_filter}*1..{max_depth}]-"
    return f"-[r:{type_filter}*1..{max_depth}]-"


# Function: _collect_path_nodes
def _collect_path_nodes(path: Any, root_id: str, seen_node_ids: set[str], nodes: list[dict[str, Any]]) -> None:
    for depth_idx, node in enumerate(path.nodes):
        node_id = dict(node).get("id", "")
        if node_id != root_id and node_id not in seen_node_ids:
            seen_node_ids.add(node_id)
            nodes.append(_node_to_dict(node, depth=depth_idx))


# Function: _collect_path_edges
def _collect_path_edges(path: Any, seen_edge_keys: set[tuple[str, str, str]], edges: list[dict[str, Any]]) -> None:
    for rel in path.relationships:
        start_id = dict(rel.start_node).get("id", "")
        end_id = dict(rel.end_node).get("id", "")
        rel_props = dict(rel)
        verb = rel_props.get("verb", rel.type.lower())
        kind = rel_props.get("kind", rel.type.lower())
        edge_key = (start_id, end_id, verb)
        if edge_key in seen_edge_keys:
            continue
        seen_edge_keys.add(edge_key)
        edge_props = rel_props.get("properties", "{}")
        if isinstance(edge_props, str):
            edge_props = json.loads(edge_props)
        edges.append({
            "from": start_id,
            "to": end_id,
            "kind": kind,
            "verb": verb,
            "properties": edge_props,
        })


class TraversalRepository:
    # Function: __init__
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # Function: traverse
    async def traverse(
        self,
        root_id: str,
        edge_kinds: list[str],
        direction: str,
        max_depth: int,
    ) -> dict[str, Any]:
        """BFS/DFS traversal from root node.

        Returns root, nodes (with depth), and edges.
        """
        # Neo4j relationship types are uppercase: FLOW, OWNS, META
        neo4j_types = [k.upper() for k in edge_kinds]
        type_filter = "|".join(neo4j_types) if neo4j_types else "FLOW|OWNS|META"
        path_pattern = _arrow_pattern(direction, type_filter, max_depth)

        # Fetch root node
        root_result = await self._session.run(
            "MATCH (n:Entity {id: $id}) RETURN n",
            id=root_id,
        )
        root_record = await root_result.single()
        if root_record is None:
            return {"root": None, "depth_reached": 0, "nodes": [], "edges": []}

        root_node = _node_to_dict(root_record["n"], depth=0)

        # Traverse paths
        cypher = f"""
        MATCH path = (root:Entity {{id: $root_id}}){path_pattern}(n:Entity)
        RETURN path LIMIT 500
        """
        result = await self._session.run(cypher, root_id=root_id)

        # Collect unique nodes and edges
        seen_node_ids: set[str] = {root_id}
        seen_edge_keys: set[tuple[str, str, str]] = set()
        nodes: list[dict[str, Any]] = []
        edges: list[dict[str, Any]] = []

        async for record in result:
            path = record["path"]
            _collect_path_nodes(path, root_id, seen_node_ids, nodes)
            _collect_path_edges(path, seen_edge_keys, edges)

        depth_reached = max((n["depth"] for n in nodes), default=0)

        return {
            "root": root_node,
            "depth_reached": depth_reached,
            "nodes": [root_node] + nodes,
            "edges": edges,
        }

    # Function: get_owners
    async def get_owners(
        self,
        node_id: str,
        include_transitive: bool,
    ) -> list[dict[str, Any]]:
        """Return Person nodes that own the given node (directly or transitively)."""
        owners: dict[str, dict[str, Any]] = {}

        # Direct owners: nodes connected via OWNS relationship
        direct_result = await self._session.run(
            """
            MATCH (target:Entity {id: $node_id})<-[r:OWNS]-(p:Entity)
            WHERE p.domain = 'people'
            RETURN p, r.verb AS verb
            """,
            node_id=node_id,
        )
        async for record in direct_result:
            p = dict(record["p"])
            p_id = p.get("id", "")
            if p_id not in owners:
                owners[p_id] = {**_node_to_dict(record["p"]), "ownership_verb": record["verb"], "ownership_type": "direct"}

        if include_transitive:
            # Find ancestors via flow/meta edges, then their owners via OWNS
            ancestor_result = await self._session.run(
                """
                MATCH path = (target:Entity {id: $node_id})<-[r:FLOW|META*1..10]-(ancestor:Entity)
                WITH DISTINCT ancestor
                MATCH (ancestor)<-[owns_rel:OWNS]-(p:Entity)
                WHERE p.domain = 'people'
                RETURN p, owns_rel.verb AS verb, ancestor.id AS ancestor_id
                """,
                node_id=node_id,
            )
            async for record in ancestor_result:
                p = dict(record["p"])
                p_id = p.get("id", "")
                if p_id not in owners:
                    owners[p_id] = {
                        **_node_to_dict(record["p"]),
                        "ownership_verb": record["verb"],
                        "ownership_type": "transitive",
                        "via_ancestor": record["ancestor_id"],
                    }

        return list(owners.values())
