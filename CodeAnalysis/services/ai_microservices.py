# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Microservices candidate identification using call-graph clustering and LLM reasoning.
# Date: 2026-06-26
# ---------------------------------------------------------------------------
"""
services/ai_microservices.py
-----------------------------
Microservices candidate identification using call-graph clustering and LLM reasoning.
L2/L3 enriched: actual function call chains, bounded context analysis, API contract suggestions.
"""
from __future__ import annotations

import logging
from collections import defaultdict

from .ollama_client import OllamaClient
from .ai_grounding import build_ground_truth, grounding_header, build_anti_hallucination_system_prompt, validate_microservices

logger = logging.getLogger(__name__)

_SYSTEM_BASE = """\
You are a microservices architect specialising in decomposing monolithic applications.
Given a detailed call-graph summary including actual function names, inter-layer edges,
and coupling counts, you identify cohesive service candidates with specific source files,
API contracts, and migration strategy.
You MUST base ALL recommendations exclusively on the GROUND TRUTH data provided.
Do NOT suggest technology stacks outside the provided valid options.
Be concise. Limit ALL string values to 1 sentence. Always return valid JSON and nothing else."""

_PROMPT_TMPL = """\
Identify microservices candidates for repository "{repo_name}".

CODEBASE OVERVIEW:
- Languages: {languages}
- Total functions: {total_functions}
- Total SLOC: {sloc}
- Architecture layers: {arch_summary}

CALL GRAPH CLUSTERS — Full function list per layer:
{cluster_summary}

TOP CALLED FUNCTIONS (L3 hot-paths):
{top_nodes}

INTER-LAYER COUPLING (calls crossing layer boundaries — high = tight coupling):
{inter_layer_edges}

CIRCULAR DEPENDENCY CANDIDATES (mutually calling function pairs):
{circular_hints}

Files per architectural layer:
{files_by_layer}

Based on cohesion, coupling, domain boundaries, and the call graph propose microservices.

Return JSON:
{{
  "decomposition_strategy": "<strangler-fig|big-bang|parallel-run>",
  "summary": "<3-4 sentence summary naming specific layers and functions that define boundaries>",
  "microservices": [
    {{
      "name": "<service name>",
      "responsibility": "<single, clear responsibility statement>",
      "source_layers": ["<layer names from the call graph>"],
      "source_files": ["<key relative file paths that belong to this service>"],
      "key_functions": ["<important function names from the call graph>"],
      "inbound_calls": <integer — how many functions call into this service>,
      "outbound_calls": <integer — how many external calls this service makes>,
      "current_tech": "<ACTUAL detected language(s) from GROUND TRUTH, e.g. COBOL, Java, Python>",
      "suggested_tech_stack": "<modernization target from VALID STACKS list in GROUND TRUTH only>",
      "api_type": "<REST|gRPC|event-driven|GraphQL>",
      "database_entities": ["<entity/table names that belong to this service>"],
      "estimated_size_kloc": <number>,
      "dependencies": ["<other service names it depends on>"],
      "migration_order": <integer starting at 1>
    }}
  ],
  "data_store_strategy": "<description of how to split/share databases per service>",
  "risks": ["<specific migration risk with file or function reference>"],
  "migration_timeline_weeks": <integer>
}}

Provide 2-3 microservices named after the domains they handle.
Return ONLY the JSON."""


# Function: _build_inter_layer_edges
def _build_inter_layer_edges(cg: dict, id_to_label: dict, id_to_layer: dict) -> str:
    """Compute cross-layer call counts and format as text."""
    cross_calls: dict[tuple[str, str], int] = defaultdict(int)
    for e in cg.get("edges", []):
        src_layer = id_to_layer.get(e.get("from", ""), "unknown")
        tgt_layer = id_to_layer.get(e.get("to", ""), "unknown")
        if src_layer != tgt_layer:
            cross_calls[(src_layer, tgt_layer)] += 1
    if not cross_calls:
        return "  (no inter-layer edges detected)"
    lines = []
    for (src, tgt), cnt in sorted(cross_calls.items(), key=lambda x: -x[1])[:10]:
        flag = " ← HIGH COUPLING" if cnt > 20 else ""
        lines.append(f"  {src} → {tgt}: {cnt} calls{flag}")
    return "\n".join(lines)


# Function: _find_circular_hints
def _find_circular_hints(cg: dict, id_to_label: dict) -> str:
    """Find pairs where A calls B and B calls A (simple circular hint)."""
    edges_set: set[tuple[str, str]] = set()
    for e in cg.get("edges", []):
        edges_set.add((e.get("from", ""), e.get("to", "")))
    circular: list[tuple[str, str]] = []
    seen: set[frozenset] = set()
    for (a, b) in edges_set:
        if (b, a) in edges_set:
            key = frozenset([a, b])
            if key not in seen:
                seen.add(key)
                la = id_to_label.get(a, a)
                lb = id_to_label.get(b, b)
                circular.append((la, lb))
    if not circular:
        return "  (no obvious circular dependencies detected)"
    lines = [f"  {la} <-> {lb}" for la, lb in circular[:8]]
    return "\n".join(lines)


# Function: _files_by_layer_fallback
def _files_by_layer_fallback(analysis_result: dict) -> str:
    """Fallback: group language report files by their layer guess."""
    lines = []
    for lr in analysis_result.get("language_reports", [])[:3]:
        files = [f["name"] for f in lr.get("files", [])[:5] if isinstance(f, dict)]
        if files:
            lines.append(f"  {lr['language']}: {', '.join(files)}")
    return "\n".join(lines) or "  (no file-layer data)"


# Function: _build_files_by_layer
def _build_files_by_layer(analysis_result: dict) -> str:
    """List source files grouped by their architectural layer."""
    arch = analysis_result.get("architecture", {}) or {}
    nodes = arch.get("nodes", []) or []
    if not nodes:
        return _files_by_layer_fallback(analysis_result)
    layer_files: dict[str, list[str]] = defaultdict(list)
    for node in nodes:
        layer = node.get("layer", "unknown")
        label = node.get("label", "")
        if label:
            layer_files[layer].append(label)
    lines = []
    for layer, files in sorted(layer_files.items()):
        sample = files[:6]
        lines.append(f"  [{layer}]: {', '.join(sample)}{' ...' if len(files) > 6 else ''}")
    return "\n".join(lines) or "  (no file-layer data)"


# Function: analyse_microservices
def analyse_microservices(
    analysis_result: dict,
    call_graph: dict | None = None,
    model: str | None = None,
    client: OllamaClient | None = None,
) -> dict:
    client = client or OllamaClient()
    cg     = call_graph or {}

    # ── Ground truth ─────────────────────────────────────────────────────────
    gt = build_ground_truth(analysis_result)
    _SYSTEM = build_anti_hallucination_system_prompt(_SYSTEM_BASE, gt)

    arch         = analysis_result.get("architecture", {}) or {}
    layer_counts = arch.get("layer_counts") or {}
    arch_txt     = ", ".join(f"{k}={v}" for k, v in layer_counts.items()) or "unknown"

    stats     = cg.get("stats", {})
    clusters  = cg.get("clusters", {})
    nodes     = cg.get("nodes", [])

    id_to_label = {n["id"]: n["label"] for n in nodes}
    id_to_layer = {n["id"]: n.get("layer", "unknown") for n in nodes}
    id_to_file  = {n["id"]: n.get("file", "") for n in nodes}

    # Full cluster summary with ALL function names (not just 5)
    cluster_lines = []
    for layer, ids in clusters.items():
        all_labels = [id_to_label.get(nid, nid) for nid in ids]
        sample     = all_labels[:5]  # Up to 5 function names per cluster
        suffix     = f" ... +{len(all_labels) - 5} more" if len(all_labels) > 5 else ""
        cluster_lines.append(f"  [{layer}] {len(ids)} functions — {', '.join(sample)}{suffix}")
    cluster_txt = "\n".join(cluster_lines) or "  (no call graph data — infer from file structure only)"

    # Top nodes (by incoming edge count) - L3 hot-paths
    edge_targets: dict[str, int] = {}
    for e in cg.get("edges", []):
        edge_targets[e["to"]] = edge_targets.get(e["to"], 0) + 1
    top = sorted(edge_targets.items(), key=lambda x: x[1], reverse=True)[:8]
    top_txt = "\n".join(
        f"  {id_to_label.get(nid, nid)} ({id_to_layer.get(nid,'?')} layer, called {cnt}x)"
        for nid, cnt in top
    ) or "  (no data)"

    # Inter-layer coupling analysis (L2/L3)
    inter_edge_txt = _build_inter_layer_edges(cg, id_to_label, id_to_layer)

    # Circular dependency hints (L3)
    circular_txt = _find_circular_hints(cg, id_to_label)

    # Files per layer
    files_by_layer_txt = _build_files_by_layer(analysis_result)

    # Prepend grounding header to prompt
    ground_block = grounding_header(gt)

    prompt = ground_block + "\n\n" + _PROMPT_TMPL.format(
        repo_name        = gt["repo_name"],
        languages        = ", ".join(gt["languages"]) or "unknown",
        total_functions  = stats.get("total_functions", "N/A"),
        sloc             = gt["total_sloc"],
        arch_summary     = arch_txt,
        cluster_summary  = cluster_txt,
        top_nodes        = top_txt,
        inter_layer_edges= inter_edge_txt,
        circular_hints   = circular_txt,
        files_by_layer   = files_by_layer_txt,
    )

    try:
        result = client.generate_json(prompt, model=model, system=_SYSTEM,
                                      max_tokens=600, num_ctx=5120, timeout=540)
        result["_model_used"] = model or client.best_available_model()
        result["_call_graph_available"] = bool(cg.get("nodes"))
        result = _enrich_microservices_result(result, cg, id_to_label, id_to_layer, id_to_file)
        # Post-process: fix hallucinated tech stacks and impossible values
        result = validate_microservices(result, gt)
        return result
    except Exception as exc:
        logger.error("ai_microservices failed: %s", exc)
        return {"error": str(exc), "summary": "AI analysis unavailable."}



# Function: _is_missing_symbol
def _is_missing_symbol(v) -> bool:
    s = str(v or "").strip().lower()
    return s in {"", "-", "--", "---", "_", "?", "unknown", "n/a", "none", "null"}


# Function: _build_layer_data_indices
def _build_layer_data_indices(cg: dict, id_to_label: dict, id_to_layer: dict, id_to_file: dict) -> tuple:
    """Build layer->functions, layer->files, inbound count, outbound count lookups."""
    layer_functions: dict[str, list[str]] = defaultdict(list)
    layer_files: dict[str, list[str]] = defaultdict(list)
    for nid, label in id_to_label.items():
        layer = id_to_layer.get(nid, "unknown")
        file_name = id_to_file.get(nid, "")
        if not _is_missing_symbol(label):
            layer_functions[layer].append(str(label).strip())
        if not _is_missing_symbol(file_name):
            layer_files[layer].append(str(file_name).strip())
    for layer in list(layer_functions.keys()):
        layer_functions[layer] = sorted(dict.fromkeys(layer_functions[layer]))
    for layer in list(layer_files.keys()):
        layer_files[layer] = sorted(dict.fromkeys(layer_files[layer]))

    layer_inbound: dict[str, int] = defaultdict(int)
    layer_outbound: dict[str, int] = defaultdict(int)
    for e in cg.get("edges", []):
        src_layer = id_to_layer.get(e.get("from", ""), "")
        tgt_layer = id_to_layer.get(e.get("to", ""), "")
        if src_layer:
            layer_outbound[src_layer] += 1
        if tgt_layer:
            layer_inbound[tgt_layer] += 1

    return layer_functions, layer_files, layer_inbound, layer_outbound


# Function: _fill_service_call_counts
def _fill_service_call_counts(svc: dict, src_layers: list, layer_inbound: dict, layer_outbound: dict) -> None:
    if not src_layers:
        return
    tot_in  = sum(layer_inbound.get(l, 0) for l in src_layers)
    tot_out = sum(layer_outbound.get(l, 0) for l in src_layers)
    if not svc.get("inbound_calls"):
        svc["inbound_calls"] = tot_in
    if not svc.get("outbound_calls"):
        svc["outbound_calls"] = tot_out


# Function: _fill_service_key_functions
def _fill_service_key_functions(svc: dict, src_layers: list, layer_functions: dict) -> None:
    kf = [str(x).strip() for x in (svc.get("key_functions") or []) if not _is_missing_symbol(x)]
    if not kf and src_layers:
        for l in src_layers:
            kf.extend(layer_functions.get(l, [])[:4])
    svc["key_functions"] = list(dict.fromkeys([x for x in kf if not _is_missing_symbol(x)]))[:8]


# Function: _fill_service_source_files
def _fill_service_source_files(svc: dict, src_layers: list, layer_files: dict) -> None:
    sf = [str(x).strip() for x in (svc.get("source_files") or []) if not _is_missing_symbol(x)]
    if not sf and src_layers:
        for l in src_layers:
            sf.extend(layer_files.get(l, [])[:4])
    svc["source_files"] = list(dict.fromkeys([x for x in sf if not _is_missing_symbol(x)]))[:8]


# Function: _enrich_service_entry
def _enrich_service_entry(svc: dict, layer_functions: dict, layer_files: dict,
                           layer_inbound: dict, layer_outbound: dict) -> None:
    """Enrich a single microservice dict in-place with computed call counts and fallback fields."""
    svc.setdefault("name", "UnnamedService")
    svc.setdefault("responsibility", "Service boundary to be refined from domain signals")
    svc.setdefault("api_type", "REST")
    svc.setdefault("migration_order", 999)

    src_layers = svc.get("source_layers") or []
    _fill_service_call_counts(svc, src_layers, layer_inbound, layer_outbound)

    svc.setdefault("suggested_api_contracts", [])
    svc.setdefault("source_files", [])
    svc.setdefault("database_entities", [])

    _fill_service_key_functions(svc, src_layers, layer_functions)
    _fill_service_source_files(svc, src_layers, layer_files)

    if svc.get("estimated_size_kloc") in (None, "", 0):
        kf_count = len(svc.get("key_functions") or [])
        sf_count = len(svc.get("source_files") or [])
        svc["estimated_size_kloc"] = round(max(0.8, kf_count * 0.06 + sf_count * 0.12), 1)


# Function: _build_fallback_phases
def _build_fallback_phases(services: list) -> list:
    """Build deterministic modernisation_phases from services list."""
    ordered = sorted(
        [s for s in services if isinstance(s, dict)],
        key=lambda s: int(s.get("migration_order") or 999),
    )
    if not ordered:
        return []
    p1_items = [s.get("name", "Service") for s in ordered[: max(1, len(ordered)//2)]]
    p2_items = [s.get("name", "Service") for s in ordered[max(1, len(ordered)//2):]]
    return [
        {
            "phase": 1,
            "title": "Extract first bounded contexts",
            "items": p1_items,
            "duration_months": 2,
            "milestone": "First service set deployed behind API gateway",
        },
        {
            "phase": 2,
            "title": "Complete decomposition and traffic split",
            "items": p2_items or p1_items[:1],
            "duration_months": 2,
            "milestone": "Legacy monolith endpoints routed to services",
        },
    ]


# Function: _ensure_shared_components
def _ensure_shared_components(result: dict) -> None:
    # Ensure shared_components is list of dicts
    shared = result.get("shared_components") or []
    if shared and isinstance(shared[0], str):
        result["shared_components"] = [
            {"name": s, "type": "utility", "used_by": [], "reason": "Shared utility component"}
            for s in shared
        ]


# Function: _ensure_risks
def _ensure_risks(result: dict) -> None:
    if not result.get("risks"):
        result["risks"] = [
            "Database coupling — multiple services may share the same schema",
            "Distributed transaction complexity when decomposing tightly-coupled layers",
            "Service discovery and network latency overhead vs monolith",
        ]


# Function: _ensure_modernisation_phases
def _ensure_modernisation_phases(result: dict, services: list) -> None:
    # Ensure modernisation_phases exists (panel depends on it)
    phases = result.get("modernisation_phases") or []
    if not phases:
        phases = _build_fallback_phases(services)
    result["modernisation_phases"] = phases


# Function: _build_microservices_l3_drilldown
def _build_microservices_l3_drilldown(cg: dict, id_to_label: dict, id_to_layer: dict) -> dict:
    # L3 drilldown bundle for modal/debug views
    incoming_by_node: dict[str, int] = defaultdict(int)
    for e in cg.get("edges", []):
        tgt = e.get("to", "")
        if tgt:
            incoming_by_node[tgt] += 1

    return {
        "call_graph_stats": cg.get("stats", {}),
        "top_called_functions": [
            {
                "function": (id_to_label.get(nid, "") or str(nid).split(".")[-1]),
                "layer": id_to_layer.get(nid, "unknown"),
                "incoming_calls": cnt,
            }
            for nid, cnt in sorted(incoming_by_node.items(), key=lambda x: -x[1])[:12]
            if not _is_missing_symbol(id_to_label.get(nid, "") or str(nid).split(".")[-1])
        ],
        "cross_layer_edges": len([1 for e in cg.get("edges", []) if id_to_layer.get(e.get("from", ""), "") != id_to_layer.get(e.get("to", ""), "")]),
    }


# Function: _enrich_microservices_result
def _enrich_microservices_result(result: dict, cg: dict, id_to_label: dict, id_to_layer: dict, id_to_file: dict) -> dict:
    """Back-fill computed edge counts, ensure minimum schema fields."""
    services = result.get("microservices") or []

    layer_functions, layer_files, layer_inbound, layer_outbound = _build_layer_data_indices(
        cg, id_to_label, id_to_layer, id_to_file
    )
    for svc in services:
        if not isinstance(svc, dict):
            continue
        _enrich_service_entry(svc, layer_functions, layer_files, layer_inbound, layer_outbound)

    result["microservices"] = services

    # Ensure circular_dependencies exists
    if not result.get("circular_dependencies"):
        result["circular_dependencies"] = []

    _ensure_shared_components(result)
    _ensure_risks(result)
    _ensure_modernisation_phases(result, services)

    result["l3_drilldown"] = _build_microservices_l3_drilldown(cg, id_to_label, id_to_layer)

    return result
