# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Knowledge Graph API  extract entities and relationships from the vectorstore
# Date: 2026-04-14
# ---------------------------------------------------------------------------
"""
Knowledge Graph API  extract entities and relationships from the vectorstore
and return a graph structure for visualization.

Node types:   document, incident, solman, delivery, category
Edge types:   contains_incident, solman_ref, delivery_ref, categorized_as
"""
import logging
import re
from collections import defaultdict
from typing import Dict, List, Optional, Set

from fastapi import APIRouter, Depends

import backend.config as cfg
from backend.api.auth import get_current_user

router = APIRouter(prefix="/api/knowledge-graph", tags=["Knowledge Graph"])
logger = logging.getLogger(__name__)

# ””€ Entity patterns ””””””””””””””””””””””””””””””””””””””””””€
_INC_RE = re.compile(r'\b(INC\d+)\b', re.IGNORECASE)
_SOLMAN_RE = re.compile(r'SolManID#?\s*(\d{10,13})', re.IGNORECASE)
_DELIVERY_RE = re.compile(r'\b(1\d{8,11})\b')
_CATEGORY_RE = re.compile(
    r'\b(SAP|GR Reversal|NAFTA|reversal|transfer posting|delivery note|'
    r'purchase order|material document|goods receipt|goods issue|'
    r'batch management|warehouse|posting period|company code|fiscal year|'
    r'invoice|credit memo|debit memo|stock transfer)\b',
    re.IGNORECASE,
)

NODE_COLORS = {
    "document": "#3b82f6",   # blue
    "incident": "#f59e0b",   # amber
    "solman":   "#10b981",   # emerald
    "delivery": "#8b5cf6",   # violet
    "category": "#ef4444",   # red
}

MAX_NODES = 300


# Function: _load_documents_from_lancedb
def _load_documents_from_lancedb() -> tuple:
    documents_raw: List[str] = []
    metadatas_raw: List[dict] = []
    try:
        from backend.services.lancedb_store import lancedb_enabled, get_lancedb_client

        if not lancedb_enabled():
            return documents_raw, metadatas_raw

        client = get_lancedb_client()
        table_name = cfg.LANCEDB_TABLE

        try:
            table = client.open_table(table_name)
            records = table.search().to_list()

            for record in records:
                text_chunk = record.get("text_chunk", "")
                metadata_obj = record.get("metadata", {})

                documents_raw.append(text_chunk)
                metadatas_raw.append({
                    "source": metadata_obj.get("source_name", "lancedb"),
                    "type": metadata_obj.get("source_type", "servicenow_incident"),
                    "incident_number": record.get("incident_id", ""),
                    "category": metadata_obj.get("category", ""),
                })
        except Exception:
            # Table doesn't exist yet, fall back to empty
            logger.warning("LanceDB table '%s' not accessible, skipping", table_name)
    except Exception as exc:
        logger.warning("LanceDB access failed, falling back to PostgreSQL: %s", exc)
    return documents_raw, metadatas_raw


# Function: _load_documents_from_postgres
def _load_documents_from_postgres() -> tuple:
    from backend.rag.vectorstore import get_vectorstore
    vs = get_vectorstore(cfg.LLM_PROVIDER)
    documents_raw: List[str] = []
    metadatas_raw: List[dict] = []
    _BATCH = 500
    offset = 0
    while True:
        batch = vs._collection.get(
            include=["documents", "metadatas"],
            limit=_BATCH,
            offset=offset,
        )
        batch_docs = batch.get("documents") or []
        if not batch_docs:
            break
        documents_raw.extend(batch_docs)
        metadatas_raw.extend(batch.get("metadatas") or [])
        offset += len(batch_docs)
        if len(batch_docs) < _BATCH:
            break
    return documents_raw, metadatas_raw


# Function: _load_graph_documents
def _load_graph_documents() -> tuple:
    documents_raw: List[str] = []
    metadatas_raw: List[dict] = []

    # Read from LanceDB if enabled, otherwise PostgreSQL
    if cfg.VECTOR_BACKEND in {"lancedb", "hybrid"}:
        documents_raw, metadatas_raw = _load_documents_from_lancedb()

    # If LanceDB is disabled or failed, read from PostgreSQL
    if not documents_raw:
        documents_raw, metadatas_raw = _load_documents_from_postgres()

    logger.info("Knowledge graph: loaded %d chunks from %s", len(documents_raw), cfg.VECTOR_BACKEND)
    return documents_raw, metadatas_raw


# Function: _add_edge
def _add_edge(edges: List[dict], edge_set: Set[tuple], src_id: str, tgt_id: str, edge_type: str) -> None:
    key = (src_id, tgt_id, edge_type)
    if key not in edge_set:
        edge_set.add(key)
        edges.append({"source": src_id, "target": tgt_id, "type": edge_type})


# Function: _upsert_node
def _upsert_node(nodes: Dict[str, dict], node_id: str, label: str, node_type: str, size: int = 10) -> None:
    if node_id not in nodes:
        nodes[node_id] = {
            "id": node_id,
            "label": label,
            "type": node_type,
            "color": NODE_COLORS.get(node_type, "#94a3b8"),
            "size": size,
        }


# Function: _process_graph_document
def _process_graph_document(
    content: str, meta: dict, nodes: Dict[str, dict], edges: List[dict], edge_set: Set[tuple]
) -> None:
    src = meta.get("source", "unknown")

    # Document node  derive short label from file name
    short_label = src.split("/")[-1].split("\\")[-1]
    _upsert_node(nodes, src, short_label, "document", size=14)

    # INC numbers
    for inc in _INC_RE.findall(content):
        inc_id = inc.upper()
        _upsert_node(nodes, inc_id, inc_id, "incident", size=12)
        _add_edge(edges, edge_set, src, inc_id, "contains_incident")

    # SolManIDs
    for sid in _SOLMAN_RE.findall(content):
        sid_id = f"SM_{sid}"
        _upsert_node(nodes, sid_id, f"SolMan {sid}", "solman", size=11)
        _add_edge(edges, edge_set, src, sid_id, "solman_ref")

    # Delivery / document numbers (long SAP numeric IDs)
    for dnum in _DELIVERY_RE.findall(content):
        dnum_id = f"DEL_{dnum}"
        _upsert_node(nodes, dnum_id, f"Doc {dnum}", "delivery", size=10)
        _add_edge(edges, edge_set, src, dnum_id, "delivery_ref")

    # SAP categories  cap to 3 per chunk to avoid noise
    cats_seen: Set[str] = set()
    for cat in _CATEGORY_RE.findall(content):
        cat_norm = cat.strip().lower().replace(" ", "_")
        if cat_norm in cats_seen or len(cats_seen) >= 3:
            continue
        cats_seen.add(cat_norm)
        cat_id = f"CAT_{cat_norm}"
        _upsert_node(nodes, cat_id, cat.strip().title(), "category", size=10)
        _add_edge(edges, edge_set, src, cat_id, "categorized_as")


# Function: _build_graph_nodes_and_edges
def _build_graph_nodes_and_edges(documents_raw: List[str], metadatas_raw: List[dict]) -> tuple:
    nodes: Dict[str, dict] = {}
    edges: List[dict] = []
    edge_set: Set[tuple] = set()

    for content, meta in zip(documents_raw, metadatas_raw):
        if not content or not meta:
            continue
        _process_graph_document(content, meta, nodes, edges, edge_set)

    return nodes, edges


# Function: _finalize_graph_nodes
def _finalize_graph_nodes(nodes: Dict[str, dict], edges: List[dict]) -> tuple:
    # ””€ Scale document node size by edge degree ”””””””””””””””€
    degree: Dict[str, int] = defaultdict(int)
    for edge in edges:
        degree[edge["source"]] += 1
    for nid, count in degree.items():
        if nid in nodes and nodes[nid]["type"] == "document":
            nodes[nid]["size"] = min(12 + count, 28)

    node_list = list(nodes.values())

    # ””€ Cap to MAX_NODES for frontend performance ”””””””””””””€
    if len(node_list) > MAX_NODES:
        doc_nodes = [n for n in node_list if n["type"] == "document"]
        other_nodes = sorted(
            [n for n in node_list if n["type"] != "document"],
            key=lambda n: degree.get(n["id"], 0),
            reverse=True,
        )
        kept_ids = {n["id"] for n in doc_nodes + other_nodes[: MAX_NODES - len(doc_nodes)]}
        node_list = [n for n in node_list if n["id"] in kept_ids]
        edges = [e for e in edges if e["source"] in kept_ids and e["target"] in kept_ids]

    return node_list, edges


# Function: get_knowledge_graph
@router.get("")
async def get_knowledge_graph(current_user: dict = Depends(get_current_user)):
    """
    Build a knowledge graph from all chunks in the vectorstore (LanceDB or PostgreSQL).

    Returns:
        nodes: list of {id, label, type, color, size}
        edges: list of {source, target, type}
        stats: summary counts
    """
    try:
        documents_raw, metadatas_raw = _load_graph_documents()
    except Exception as exc:
        logger.error("Knowledge graph: failed to read vectorstore: %s", exc)
        return {"nodes": [], "edges": [], "stats": {"error": str(exc)}}

    nodes, edges = _build_graph_nodes_and_edges(documents_raw, metadatas_raw)
    node_list, edges = _finalize_graph_nodes(nodes, edges)

    type_counts: Dict[str, int] = defaultdict(int)
    for n in node_list:
        type_counts[n["type"]] += 1

    return {
        "nodes": node_list,
        "edges": edges,
        "stats": {
            "total_nodes": len(node_list),
            "total_edges": len(edges),
            "documents": type_counts.get("document", 0),
            "incidents": type_counts.get("incident", 0),
            "solman_refs": type_counts.get("solman", 0),
            "deliveries": type_counts.get("delivery", 0),
            "categories": type_counts.get("category", 0),
        },
    }


# Function: _get_graph_stats_from_lancedb
def _get_graph_stats_from_lancedb() -> Optional[dict]:
    try:
        from backend.services.lancedb_store import lancedb_enabled, get_lancedb_client

        if not lancedb_enabled():
            return None

        client = get_lancedb_client()
        table_name = cfg.LANCEDB_TABLE

        try:
            table = client.open_table(table_name)
            records = table.search().to_list()
            total_chunks = len(records)

            sources = set()
            for record in records:
                metadata_obj = record.get("metadata", {})
                src = metadata_obj.get("source_name", "lancedb")
                if src:
                    sources.add(src)

            logger.info("Knowledge graph stats from LanceDB: %d chunks, %d sources", total_chunks, len(sources))
            return {
                "total_chunks": total_chunks,
                "unique_documents": len(sources),
                "backend": "lancedb",
            }
        except Exception as e:
            logger.warning("LanceDB table not accessible: %s", e)
    except Exception as exc:
        logger.warning("LanceDB access failed in stats: %s", exc)
    return None


# Function: _get_graph_stats_from_postgres
def _get_graph_stats_from_postgres() -> dict:
    from backend.rag.vectorstore import get_vectorstore
    vs = get_vectorstore(cfg.LLM_PROVIDER)
    result = vs._collection.get(include=["metadatas"])
    metadatas = result.get("metadatas", [])
    sources = {m.get("source", "") for m in metadatas if m}

    logger.info("Knowledge graph stats from PostgreSQL: %d chunks, %d sources", len(metadatas), len(sources))
    return {
        "total_chunks": len(metadatas),
        "unique_documents": len(sources),
        "backend": "postgresql",
    }


# Function: get_graph_stats
@router.get("/stats")
async def get_graph_stats(current_user: dict = Depends(get_current_user)):
    """Quick stats without returning the full graph (fast endpoint for dashboard widgets)."""
    try:
        # Get stats from LanceDB if enabled
        if cfg.VECTOR_BACKEND in {"lancedb", "hybrid"}:
            lancedb_stats = _get_graph_stats_from_lancedb()
            if lancedb_stats is not None:
                return lancedb_stats

        # Fall back to PostgreSQL
        return _get_graph_stats_from_postgres()
    except Exception as exc:
        logger.error("Knowledge graph stats: %s", exc)
        return {"error": str(exc)}
