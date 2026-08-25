# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Master orchestrator for all Ollama-powered AI analysis services.
# Date: 2026-03-10
# ---------------------------------------------------------------------------
"""
services/ai_analysis.py
------------------------
Master orchestrator for all Ollama-powered AI analysis services.

Called from api/server.py.  Runs all (or selected) AI sub-analyses and
returns a unified AI intelligence report, stored as a job like the
regular analysis jobs.
"""
from __future__ import annotations

import concurrent.futures
import json
import logging
import time
from pathlib import Path
from typing import Any, Callable

# Single background thread used to build the call graph while the first LLM
# analysis is in flight.  Keep alive for the process lifetime so thread
# creation overhead is paid only once.
_CG_POOL      = concurrent.futures.ThreadPoolExecutor(max_workers=1, thread_name_prefix="call_graph")
# Parallel pool for independent analyses — 5 workers so all 5 non-cg-dependent
# analyses can preprocess (file-scan, radon, anti-pattern) concurrently while
# Ollama processes one LLM call at a time.  Saves 30-90 s of I/O overlap.
_PARALLEL_POOL = concurrent.futures.ThreadPoolExecutor(max_workers=5, thread_name_prefix="ai_parallel")

from .ollama_client    import OllamaClient
from .call_graph       import build_call_graph
from .ai_tech_debt import analyse_tech_debt, _gather_all_files, _validate_and_enrich
from .ai_cloud_blockers import analyse_cloud_blockers, _enrich_cloud_result
from .ai_microservices import analyse_microservices, _enrich_microservices_result
from .ai_business_rules import (
    analyse_business_rules,
    _enrich_business_rules,
    _extract_class_entities,
    _extract_validation_logic,
)
from .ai_transformation import analyse_transformation, _enrich_transformation_result
from .ai_code_level import (
    analyse_code_level,
    _collect_top_files,
    _enrich_result as _enrich_code_level_result,
    _extract_function_data,
    _scan_anti_patterns,
    _scan_class_signals,
    _scan_coupling,
)
from .ai_legacy_modernization import analyse_legacy_modernization, _fallback_result as _legacy_fallback

logger = logging.getLogger(__name__)

# Ordered list of analyses; each entry: (key, display_name, needs_repo_path, needs_call_graph)
_ANALYSES = [
    ("tech_debt",            "Tech Debt Intelligence",    False, False),
    ("cloud_blockers",       "Cloud Blocker Removal",     False, False),
    ("microservices",        "Microservices Candidates",  False, True),
    ("business_rules",       "Business Rules Extraction", True,  False),
    ("transformation",       "Modernisation Roadmap",     False, False),
    ("code_level",           "Code-Level Deep Scan",      True,  False),
    ("legacy_modernization", "Legacy Tech Modernization", False, False),
]

_TAB_KEYS = [
    "overview",
    "security",
    "cloud",
    "cloud_services",
    "co2",
    "green",
    "health_tech",
    "debt_detail",
    "architecture",
    "languages",
    "practices",
    "knowledge_graph",
    "legacy_tech",
    "ml_predictions",
]

_TAB_ANALYSIS_MAP: dict[str, list[str]] = {
    "overview": ["tech_debt", "cloud_blockers", "transformation", "microservices"],
    "security": ["cloud_blockers", "tech_debt", "transformation", "code_level"],
    "cloud": ["cloud_blockers", "transformation"],
    "cloud_services": ["cloud_blockers", "transformation"],
    "co2": ["transformation", "tech_debt"],
    "green": ["transformation", "tech_debt"],
    "health_tech": ["tech_debt", "transformation", "code_level"],
    "debt_detail": ["tech_debt", "transformation", "code_level"],
    "architecture": ["microservices", "transformation", "code_level"],
    "languages": ["tech_debt", "business_rules", "code_level"],
    "practices": ["tech_debt", "business_rules", "code_level"],
    "knowledge_graph": ["microservices", "business_rules", "transformation"],
    "legacy_tech": ["legacy_modernization", "transformation", "tech_debt"],
    "ml_predictions": ["tech_debt", "transformation", "code_level", "legacy_modernization"],
}


# Function: _as_list
def _as_list(value: Any) -> list:
    return value if isinstance(value, list) else []


# Function: _top_priority
def _top_priority(priorities: list[str]) -> str:
    rank = {"high": 3, "medium": 2, "low": 1}
    valid = [p for p in priorities if p in rank]
    if not valid:
        return "medium"
    return max(valid, key=lambda p: rank[p])


# Function: _dedupe
def _dedupe(items: list[str], limit: int = 4) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        if not item:
            continue
        key = item.strip()
        if not key:
            continue
        if key in seen:
            continue
        seen.add(key)
        out.append(key)
        if len(out) >= limit:
            break
    return out


# Function: _format_action_item
def _format_action_item(item: Any) -> str:
    """Normalize action-like payload items into user-friendly strings."""
    if isinstance(item, str):
        return item.strip()
    if not isinstance(item, dict):
        return str(item or "").strip()

    action = str(item.get("action") or item.get("title") or item.get("name") or "").strip()
    if not action:
        return ""

    file_name = str(item.get("file") or item.get("target") or "").strip()
    effort = item.get("effort_hours")
    if effort is None:
        effort = item.get("effort_days")
    if effort is None:
        effort = item.get("effort_weeks")

    details: list[str] = []
    if file_name and file_name.lower() != "multiple":
        details.append(file_name)
    if effort not in (None, ""):
        details.append(f"effort {effort}")

    return f"{action} ({'; '.join(details)})" if details else action


# Function: _summarise_tech_debt
def _summarise_tech_debt(payload: dict, summary: str) -> dict:
    hotspots = _as_list(payload.get("hotspots"))
    drivers = [
        str(h.get("issue") or h.get("file") or "").strip()
        for h in hotspots[:8]
        if isinstance(h, dict)
    ]
    actions = []
    for x in _as_list(payload.get("quick_wins")) + _as_list(payload.get("strategic_actions")):
        formatted = _format_action_item(x)
        if formatted:
            actions.append(formatted)
    actions.extend(
        str(h.get("recommendation") or "").strip()
        for h in hotspots[:8]
        if isinstance(h, dict)
    )
    hotspot_priorities = [
        str(h.get("priority") or "").lower().strip()
        for h in hotspots
        if isinstance(h, dict)
    ]
    priority = _top_priority(hotspot_priorities)
    return {
        "summary": summary,
        "priority": priority,
        "confidence": 78,
        "drivers": _dedupe(drivers),
        "recommended_actions": _dedupe(actions),
    }


# Function: _summarise_cloud_blockers
def _summarise_cloud_blockers(payload: dict, summary: str) -> dict:
    blockers = _as_list(payload.get("blockers"))
    drivers = [
        str(b.get("title") or b.get("description") or "").strip()
        for b in blockers[:8]
        if isinstance(b, dict)
    ]
    actions = [
        str(b.get("remediation") or "").strip()
        for b in blockers[:8]
        if isinstance(b, dict)
    ]
    for ph in _as_list(payload.get("migration_phases"))[:3]:
        if not isinstance(ph, dict):
            continue
        actions.extend(str(t).strip() for t in _as_list(ph.get("tasks"))[:2])
    readiness = str(payload.get("migration_readiness") or "").lower().strip()
    severity = [
        str(b.get("severity") or "").lower().strip()
        for b in blockers
        if isinstance(b, dict)
    ]
    if readiness in {"major_refactor", "not_ready"} or any(s in {"critical", "high"} for s in severity):
        priority = "high"
    elif readiness == "ready":
        priority = "low"
    else:
        priority = "medium"
    return {
        "summary": summary,
        "priority": priority,
        "confidence": 80,
        "drivers": _dedupe(drivers),
        "recommended_actions": _dedupe(actions),
    }


# Function: _summarise_microservices
def _summarise_microservices(payload: dict, summary: str) -> dict:
    services = _as_list(payload.get("microservices"))
    risks = _as_list(payload.get("risks"))
    drivers = [
        str(s.get("responsibility") or s.get("name") or "").strip()
        for s in services[:8]
        if isinstance(s, dict)
    ]
    actions = [
        str(s.get("name") or "").strip()
        for s in sorted(
            [s for s in services if isinstance(s, dict)],
            key=lambda d: int(d.get("migration_order") or 9999),
        )[:5]
    ]
    actions.extend(str(r).strip() for r in risks[:3])
    priority = "high" if len(risks) >= 3 else ("low" if len(risks) == 0 else "medium")
    return {
        "summary": summary,
        "priority": priority,
        "confidence": 74,
        "drivers": _dedupe(drivers),
        "recommended_actions": _dedupe(actions),
    }


# Function: _summarise_business_rules
def _summarise_business_rules(payload: dict, summary: str) -> dict:
    rules = _as_list(payload.get("business_rules"))
    workflows = _as_list(payload.get("workflows"))
    drivers = [
        str(r.get("title") or r.get("description") or "").strip()
        for r in rules[:8]
        if isinstance(r, dict)
    ]
    actions: list[str] = []
    for wf in workflows[:3]:
        if not isinstance(wf, dict):
            continue
        actions.extend(str(step).strip() for step in _as_list(wf.get("steps"))[:2])
    confidence_levels = [
        str(r.get("confidence") or "").lower().strip()
        for r in rules
        if isinstance(r, dict)
    ]
    priority = "medium"
    if confidence_levels and confidence_levels.count("low") > max(1, len(confidence_levels) // 3):
        priority = "high"
    return {
        "summary": summary,
        "priority": priority,
        "confidence": 72,
        "drivers": _dedupe(drivers),
        "recommended_actions": _dedupe(actions),
    }


# Function: _summarise_transformation
def _summarise_transformation(payload: dict, summary: str) -> dict:
    paths = _as_list(payload.get("transformation_paths"))
    phases = _as_list(payload.get("modernisation_phases"))
    drivers = [
        f"{p.get('current', '?')} -> {p.get('recommended', '?')}"
        for p in paths[:8]
        if isinstance(p, dict)
    ]
    actions: list[str] = []
    for p in paths[:4]:
        if not isinstance(p, dict):
            continue
        actions.extend(str(step).strip() for step in _as_list(p.get("steps"))[:2])
    for ph in phases[:2]:
        if not isinstance(ph, dict):
            continue
        actions.extend(str(i).strip() for i in _as_list(ph.get("items"))[:2])
    maturity = str(payload.get("current_maturity") or "").lower().strip()
    if maturity == "legacy":
        priority = "high"
    elif maturity in {"modern", "cloud-native"}:
        priority = "low"
    else:
        priority = "medium"
    return {
        "summary": summary,
        "priority": priority,
        "confidence": 77,
        "drivers": _dedupe(drivers),
        "recommended_actions": _dedupe(actions),
    }


# Function: _summarise_code_level
def _summarise_code_level(payload: dict, summary: str) -> dict:
    per_fn = _as_list(payload.get("per_function_issues"))
    catalog = _as_list(payload.get("anti_pattern_catalog"))

    # Function: _ok_symbol
    def _ok_symbol(v: str) -> bool:
        s = str(v or "").strip().lower()
        return s not in {"", "-", "--", "---", "_", "?", "unknown", "n/a", "none", "null"}

    drivers = [
        f"{i.get('function')} ({i.get('file')}): {', '.join(_as_list(i.get('issues'))[:1])}"
        for i in per_fn[:6]
        if isinstance(i, dict) and _ok_symbol(i.get("function")) and _ok_symbol(i.get("file"))
    ]
    actions = [
        str(i.get("refactoring_action") or "").strip()
        for i in per_fn[:4]
        if isinstance(i, dict)
    ]
    actions.extend(
        str(c.get("remediation") or "").strip()
        for c in catalog[:3]
        if isinstance(c, dict)
    )
    smell_score = payload.get("code_smell_score", 50)
    try:
        smell_score = int(smell_score)
    except Exception:
        smell_score = 50
    priority = "high" if smell_score < 40 else ("medium" if smell_score < 65 else "low")
    return {
        "summary": summary,
        "priority": priority,
        "confidence": 80,
        "drivers": _dedupe(drivers),
        "recommended_actions": _dedupe(actions),
    }


# Function: _summarise_analysis
def _summarise_analysis(analysis_key: str, payload: dict) -> dict:
    if not isinstance(payload, dict) or payload.get("error"):
        return {}

    summary = str(payload.get("summary") or "").strip()
    summarizers: dict[str, Callable[[dict, str], dict]] = {
        "tech_debt": _summarise_tech_debt,
        "cloud_blockers": _summarise_cloud_blockers,
        "microservices": _summarise_microservices,
        "business_rules": _summarise_business_rules,
        "transformation": _summarise_transformation,
        "code_level": _summarise_code_level,
    }
    summarizer = summarizers.get(analysis_key)
    if not summarizer:
        return {}
    return summarizer(payload, summary)


# Function: _fallback_tab_assessments
def _fallback_tab_assessments(analyses: dict) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for tab_key in _TAB_KEYS:
        keys = _TAB_ANALYSIS_MAP.get(tab_key, [])
        parts = [_summarise_analysis(k, analyses.get(k, {})) for k in keys]
        parts = [p for p in parts if p]

        if not parts:
            out[tab_key] = {
                "summary": "LLM inputs not available yet for this tab.",
                "priority": "medium",
                "confidence": 40,
                "drivers": [],
                "recommended_actions": [],
                "sources": keys,
            }
            continue

        summary_parts = [str(p.get("summary") or "").strip() for p in parts if p.get("summary")]
        merged_summary = " ".join(summary_parts[:2]).strip() or "AI synthesis available for this tab."

        drivers = _dedupe([d for p in parts for d in _as_list(p.get("drivers"))], limit=4)
        actions = _dedupe([a for p in parts for a in _as_list(p.get("recommended_actions"))], limit=4)
        priorities = [str(p.get("priority") or "medium").lower() for p in parts]
        confidences = [int(p.get("confidence", 70)) for p in parts if isinstance(p.get("confidence"), int)]

        out[tab_key] = {
            "summary": merged_summary,
            "priority": _top_priority(priorities),
            "confidence": max(35, min(98, int(sum(confidences) / len(confidences)) if confidences else 70)),
            "drivers": drivers,
            "recommended_actions": actions,
            "sources": [k for k in keys if analyses.get(k)],
        }
    return out



# Function: _build_analysis_snapshot
def _build_analysis_snapshot(analysis_result: dict, analyses: dict) -> dict:
    """Build a compact snapshot for the tab-assessment LLM prompt."""
    _health = analysis_result.get("health") or {}
    _debt   = analysis_result.get("debt")   or {}
    _cloud  = analysis_result.get("cloud")  or {}
    _oss    = analysis_result.get("oss")    or {}
    _co2    = analysis_result.get("co2")    or {}
    _arch   = analysis_result.get("architecture") or {}
    return {
        "repo_name": analysis_result.get("repo_name"),
        "languages": analysis_result.get("languages_detected", []),
        "sloc":      analysis_result.get("total_sloc", 0),
        "health": {
            "score":      _health.get("health", _health.get("score", 0)),
            "risk_label": _health.get("risk_label", "unknown"),
        },
        "debt": {
            "debt_months": _debt.get("debt_months", _debt.get("total_debt_months", 0)),
            "debt_usd":    _debt.get("debt_usd", 0),
        },
        "cloud_score":    _cloud.get("total"),
        "oss_vulnerable": _oss.get("vulnerable_count"),
        "co2_annual_kg":  _co2.get("annual_kg"),
        "arch_layers":    list((_arch.get("layer_counts") or {}).keys()),
        "analyses_summary": {
            k: _summarise_analysis(k, v)
            for k, v in analyses.items()
            if isinstance(v, dict) and not v.get("error")
        },
        "tab_keys": _TAB_KEYS,
    }


# Function: _merge_tab_assessment
def _merge_tab_assessment(raw_item, base: dict) -> dict:
    item = raw_item if isinstance(raw_item, dict) else {}

    priority = str(item.get("priority") or base.get("priority") or "medium").lower().strip()
    if priority not in {"high", "medium", "low"}:
        priority = str(base.get("priority") or "medium")

    try:
        confidence = int(float(item.get("confidence", base.get("confidence", 70))))
    except Exception:
        confidence = int(base.get("confidence", 70))
    confidence = max(20, min(100, confidence))

    summary = str(item.get("summary") or base.get("summary") or "").strip()
    drivers = _dedupe([str(x).strip() for x in _as_list(item.get("drivers"))], limit=4)
    actions = _dedupe([str(x).strip() for x in _as_list(item.get("recommended_actions"))], limit=4)
    sources = _dedupe([str(x).strip() for x in _as_list(item.get("sources"))], limit=5)

    return {
        "summary": summary or str(base.get("summary") or "AI-driven assessment available."),
        "priority": priority,
        "confidence": confidence,
        "drivers": drivers or _as_list(base.get("drivers"))[:4],
        "recommended_actions": actions or _as_list(base.get("recommended_actions"))[:4],
        "sources": sources or _as_list(base.get("sources")),
    }


# Function: _generate_tab_assessments
def _generate_tab_assessments(
    analysis_result: dict,
    analyses: dict,
    model: str,
    client: OllamaClient,
) -> dict[str, dict]:
    fallback = _fallback_tab_assessments(analyses)

    snapshot = _build_analysis_snapshot(analysis_result, analyses)

    prompt = (
        "Create tab-level machine-learning assessments for an engineering dashboard.\n"
        "Each tab must include:\n"
        "summary (string), priority (high|medium|low), confidence (0-100 integer),\n"
        "drivers (array of 1-4 concise signals), recommended_actions (array of 1-4 concrete actions),\n"
        "sources (array of analysis keys used).\n"
        "Return ONLY a JSON object keyed by these tabs exactly: "
        + ", ".join(_TAB_KEYS)
        + "\n\n"
        "Use this analysis snapshot:\n"
        + json.dumps(snapshot, ensure_ascii=True)
    )

    system = (
        "You are a principal ML assessment engine for software portfolio analytics. "
        "Ground every tab assessment in the provided metrics and AI analysis outputs. "
        "Be extremely concise. Limit ALL string values to 1 sentence. "
        "Do not invent unsupported facts. Return strict JSON only."
    )

    # num_ctx=4096 fits prompt (~1k tokens) + response (~900 tokens) within
    # the 12 GB VRAM budget alongside qwen2.5:7b (~9 GB model).
    # timeout=540 to allow for token generation on heavy loads (540s = 9 min)
    raw = client.generate_json(prompt, model=model, system=system,
                               max_tokens=800, num_ctx=4096, timeout=540)
    if not isinstance(raw, dict):
        return fallback

    out: dict[str, dict] = {}
    for tab_key in _TAB_KEYS:
        out[tab_key] = _merge_tab_assessment(raw.get(tab_key), fallback.get(tab_key, {}))

    return out


# Function: _dispatch_parallel_analyses
def _dispatch_parallel_analyses(
    run_keys: set, analysis_result: dict, repo_path: str, best_model: str, client: OllamaClient,
) -> dict:
    """Submit each independent, non-call-graph-dependent analysis to the pool."""
    _dispatch: dict["concurrent.futures.Future[dict]", str] = {}

    if "tech_debt" in run_keys:
        _dispatch[_PARALLEL_POOL.submit(
            analyse_tech_debt, analysis_result, model=best_model, client=client, repo_path=repo_path
        )] = "tech_debt"

    if "cloud_blockers" in run_keys:
        _dispatch[_PARALLEL_POOL.submit(
            analyse_cloud_blockers, analysis_result, model=best_model, client=client, repo_path=repo_path
        )] = "cloud_blockers"

    if "transformation" in run_keys:
        _dispatch[_PARALLEL_POOL.submit(
            analyse_transformation, analysis_result, model=best_model, client=client
        )] = "transformation"

    if "business_rules" in run_keys:
        _dispatch[_PARALLEL_POOL.submit(
            analyse_business_rules, analysis_result, repo_path, model=best_model, client=client
        )] = "business_rules"

    if "code_level" in run_keys:
        _dispatch[_PARALLEL_POOL.submit(
            analyse_code_level, analysis_result, repo_path=repo_path, model=best_model, client=client
        )] = "code_level"

    if "legacy_modernization" in run_keys:
        _dispatch[_PARALLEL_POOL.submit(
            analyse_legacy_modernization,
            analysis_result.get("repo_name", "unknown"),
            analysis_result.get("language_reports", []),
            analysis_result.get("ml_predictions") or {},
            health_score=float((analysis_result.get("health") or {}).get("health", 50)),
            total_sloc=int(analysis_result.get("total_sloc", 0)),
            model=best_model,
            client=client,
        )] = "legacy_modernization"

    return _dispatch


# Function: _resolve_call_graph
def _resolve_call_graph(_cg_future, report: dict) -> dict:
    """Wait (with a hard cap) for the background call-graph build to finish."""
    try:
        cg = _cg_future.result(timeout=90)  # 90 s hard cap — never block forever
        report["call_graph_stats"] = cg.get("stats", {})
        return cg
    except concurrent.futures.TimeoutError:
        logger.warning("call_graph timed out after 90 s — proceeding without it")
        try:
            _cg_future.cancel()
        except Exception:
            pass
        return {}
    except Exception as exc:
        logger.error("call_graph error: %s", exc)
        return {}


# Function: _collect_dispatched_results
def _collect_dispatched_results(_dispatch: dict, _names: dict, _progress, report: dict) -> None:
    """Collect every dispatched analysis without a contradictory global timeout.

    Each Ollama request already owns an explicit 480-600 second timeout and the
    Ollama client serializes inference calls.  A 360 second timeout around the
    entire group therefore expired before even the first large-model request
    completed, raising ``N (of N) futures unfinished`` and discarding every
    result.  Waiting for FIRST_COMPLETED preserves partial results and lets each
    request enforce its own bounded timeout.
    """
    pending = set(_dispatch)
    while pending:
        completed, pending = concurrent.futures.wait(
            pending, timeout=30, return_when=concurrent.futures.FIRST_COMPLETED,
        )
        if not completed:
            logger.info("AI analysis is still running (%d task(s) pending)", len(pending))
            continue
        for future in completed:
            key = _dispatch[future]
            _progress(_names.get(key, key))
            try:
                report["analyses"][key] = future.result()
            except Exception as exc:
                logger.error("%s analysis failed: %s", key, exc)
                report["analyses"][key] = {"error": str(exc)}


def _short_path(value: Any) -> str:
    """Remove deployment-specific absolute prefixes from evidence paths."""
    text = str(value or "").replace("\\", "/")
    markers = ("/extracted/", "/uploaded_repos/")
    for marker in markers:
        if marker in text:
            text = text.split(marker, 1)[1]
            if marker == "/uploaded_repos/" and "/" in text:
                text = text.split("/", 1)[1]
    return text or "unknown"


def _compact_prediction_evidence(analysis_result: dict) -> dict:
    """Return a small, scanner-grounded payload for one batched LLM request."""
    health = analysis_result.get("health") or {}
    debt = analysis_result.get("debt") or {}
    cloud = analysis_result.get("cloud") or {}
    architecture = analysis_result.get("architecture") or {}
    ml = analysis_result.get("ml_predictions") or {}
    language_reports = analysis_result.get("language_reports") or []
    defect_predictions = ml.get("defect_predictions") or []
    nodes = architecture.get("nodes") or []
    return {
        "repository": analysis_result.get("repo_name", "unknown"),
        "languages": analysis_result.get("languages_detected") or [],
        "sloc": analysis_result.get("total_sloc", 0),
        "health": {
            "score": health.get("health", health.get("score", 0)),
            "risk": health.get("risk_label", "unknown"),
            "findings": _as_list(health.get("summary"))[:12],
        },
        "debt": {
            "months": debt.get("debt_months", 0),
            "ratio": debt.get("debt_ratio", 0),
            "risk": debt.get("risk_label", "unknown"),
        },
        "cloud": {
            "score": cloud.get("total", cloud.get("score", 0)),
            "blockers": _as_list(cloud.get("blockers"))[:10],
            "boosters": _as_list(cloud.get("boosters"))[:6],
        },
        "architecture_layers": architecture.get("layer_counts") or {},
        "source_files": [_short_path(node.get("name")) for node in nodes[:30] if isinstance(node, dict)],
        "bad_practices": _dedupe([
            str(item)
            for report in language_reports if isinstance(report, dict)
            for item in _as_list(report.get("bad_practices"))
        ], limit=16),
        "top_risk_files": [
            {
                "file": _short_path(item.get("file")),
                "risk": item.get("risk_level", "medium"),
                "probability": item.get("probability", 0),
                "factors": _as_list(item.get("factors"))[:4],
            }
            for item in defect_predictions[:10] if isinstance(item, dict)
        ],
        "migration": ml.get("migration_score") or {},
    }


def _generate_prediction_narratives(
    analysis_result: dict, run_keys: set[str], model: str, client: OllamaClient,
) -> dict:
    """Generate every narrative in one bounded inference instead of 7 serial calls."""
    keys = [key for key, *_ in _ANALYSES if key in run_keys]
    prompt = (
        "Create concise, evidence-grounded software modernization predictions. "
        "Return ONLY JSON keyed by: " + ", ".join(keys) + ". "
        "Every key must contain summary (one sentence) and top_actions (array of at most 3 short actions). "
        "Do not invent files, frameworks, metrics, or business behavior.\n\nEvidence:\n"
        + json.dumps(_compact_prediction_evidence(analysis_result), ensure_ascii=True)
    )
    system = (
        "You are a principal software modernization analyst. Base every statement on the supplied "
        "static-analysis evidence. Be concise and return strict JSON only."
    )
    result = client.generate_json(
        prompt, model=model, system=system, max_tokens=420, num_ctx=4096,
        timeout=180, max_attempts=1,
    )
    return result if isinstance(result, dict) else {}


def _narrative(narratives: dict, key: str, fallback: str) -> tuple[str, list[str]]:
    value = narratives.get(key) if isinstance(narratives, dict) else None
    value = value if isinstance(value, dict) else {}
    summary = str(value.get("summary") or fallback).strip()
    actions = [str(item).strip() for item in _as_list(value.get("top_actions")) if str(item).strip()]
    return summary, actions[:3]


def _risk_hotspots(analysis_result: dict) -> list[dict]:
    ml = analysis_result.get("ml_predictions") or {}
    effort_rows = (ml.get("effort_estimates") or {}).get("top_complex_files") or []
    effort = {_short_path(row.get("file")): row.get("effort_days", 0) for row in effort_rows if isinstance(row, dict)}
    hotspots = []
    for item in _as_list(ml.get("defect_predictions"))[:10]:
        if not isinstance(item, dict):
            continue
        file_name = _short_path(item.get("file"))
        factors = [str(x) for x in _as_list(item.get("factors"))]
        hotspots.append({
            "file": file_name,
            "issue": "; ".join(factors) or "Elevated defect probability",
            "recommendation": "Refactor the measured risk drivers and add focused regression tests.",
            "priority": "high" if item.get("risk_level") in {"critical", "high"} else "medium",
            "effort_days": effort.get(file_name, 0),
            "metrics": {"defect_probability": item.get("probability", 0)},
        })
    return hotspots


def _candidate_services(analysis_result: dict) -> list[dict]:
    nodes = (analysis_result.get("architecture") or {}).get("nodes") or []
    candidates: list[dict] = []
    seen: set[str] = set()
    for node in nodes:
        if not isinstance(node, dict):
            continue
        file_name = _short_path(node.get("name"))
        stem = Path(file_name).stem
        lowered = stem.lower()
        if not any(token in lowered for token in ("service", "action", "controller", "processor")):
            continue
        name = stem.removesuffix("Service").removesuffix("Action").removesuffix("Controller") or stem
        if name.lower() in seen:
            continue
        seen.add(name.lower())
        candidates.append({
            "name": f"{name} Service",
            "responsibility": f"Isolate the behavior currently implemented by {stem}.",
            "source_files": [file_name],
            "migration_order": len(candidates) + 1,
            "effort_weeks": 2,
            "dependencies": [],
        })
        if len(candidates) >= 6:
            break
    return candidates


def _business_rules_from_files(analysis_result: dict) -> list[dict]:
    nodes = (analysis_result.get("architecture") or {}).get("nodes") or []
    rules = []
    for node in nodes:
        if not isinstance(node, dict):
            continue
        file_name = _short_path(node.get("name"))
        stem = Path(file_name).stem
        if not any(token in stem.lower() for token in ("service", "action", "form", "constant")):
            continue
        rules.append({
            "id": f"BR-{len(rules) + 1:03d}",
            "title": f"Preserve {stem} behavior",
            "description": f"Modernization must preserve the request, validation, and state-transition behavior owned by {stem}.",
            "type": "behavior-preservation",
            "confidence": "medium",
            "source_function": stem,
            "source_file": file_name,
            "source_evidence": f"Source component {stem} was classified in the application architecture.",
            "rule_condition": f"WHEN a flow reaches {stem} THEN preserve its observable inputs, outputs, validations, and side effects.",
            "affected_entities": [stem.removesuffix("Service").removesuffix("Action").removesuffix("Form")],
            "testable": True,
            "priority": "medium",
        })
        if len(rules) >= 8:
            break
    return rules


def _filter_business_source_evidence(text: str) -> str:
    """Exclude bundled/vendor JavaScript and unresolved symbols from rule evidence."""
    excluded = ("jquery", ".min.", "node_modules", "vendor/", "vendor\\")
    lines = []
    for line in str(text or "").splitlines():
        lowered = line.lower()
        if any(token in lowered for token in excluded):
            continue
        if "::?]" in line or "::unknown]" in lowered:
            continue
        lines.append(line)
    return "\n".join(lines)


def _build_fast_analyses(analysis_result: dict, narratives: dict, run_keys: set[str], model: str) -> dict:
    """Combine one LLM batch with deterministic scanner evidence for complete UI payloads."""
    ml = analysis_result.get("ml_predictions") or {}
    cloud = analysis_result.get("cloud") or {}
    debt = analysis_result.get("debt") or {}
    health = analysis_result.get("health") or {}
    hotspots = _risk_hotspots(analysis_result)
    services = _candidate_services(analysis_result)
    rules = _business_rules_from_files(analysis_result)
    outputs: dict[str, dict] = {}

    summary, actions = _narrative(narratives, "tech_debt", "Static analysis identified prioritized technical-debt hotspots.")
    outputs["tech_debt"] = {
        "summary": summary, "hotspots": hotspots,
        "quick_wins": actions or ["Add regression tests around the highest-risk files."],
        "strategic_actions": actions, "estimated_total_effort_days": round(float(debt.get("debt_months", 0)) * 22),
        "risk_if_ignored": f"Current technical-debt risk is {debt.get('risk_label', 'unknown')}.", "_model_used": model,
    }

    summary, actions = _narrative(narratives, "cloud_blockers", "Cloud readiness is constrained by the detected deployment and state-management blockers.")
    blockers = [{
        "title": str(item), "description": f"Detected by static analysis: {item}", "severity": "high",
        "remediation": actions[index % len(actions)] if actions else "Address the detected blocker before migration.",
        "impacted_files": [], "effort_days": 2,
    } for index, item in enumerate(_as_list(cloud.get("blockers"))[:8])]
    outputs["cloud_blockers"] = {
        "summary": summary, "blockers": blockers, "quick_wins": actions,
        "migration_readiness": "major_refactor" if float(cloud.get("total", 0) or 0) < 40 else "partial_refactor",
        "migration_phases": [{"name": "Remove blockers", "tasks": actions, "duration_weeks": max(1, len(blockers))}],
        "_model_used": model,
    }

    summary, actions = _narrative(narratives, "microservices", "Architecture evidence identifies candidate service boundaries for incremental extraction.")
    outputs["microservices"] = {
        "summary": summary, "microservices": services, "risks": actions,
        "decomposition_strategy": "strangler-pattern", "data_store_strategy": "Separate data ownership incrementally.",
        "migration_timeline_weeks": max(4, len(services) * 2), "_model_used": model,
    }

    summary, actions = _narrative(narratives, "business_rules", "Source structure identifies behavior that must remain traceable during modernization.")
    outputs["business_rules"] = {
        "summary": summary, "domain": analysis_result.get("repo_name", "Application"),
        "business_rules": rules, "workflows": [],
        "key_entities": [Path(_short_path(n.get("name"))).stem for n in ((analysis_result.get("architecture") or {}).get("nodes") or [])[:10] if isinstance(n, dict)],
        "recommended_actions": actions, "_model_used": model,
    }

    summary, actions = _narrative(narratives, "transformation", "Modernize the measured legacy and cloud-readiness constraints in controlled phases.")
    legacy_signals = (ml.get("migration_score") or {}).get("legacy_signals") or {}
    paths = []
    if legacy_signals.get("struts"):
        paths.append({"current": "Struts", "recommended": "Spring Boot", "steps": actions or ["Extract controller behavior", "Introduce tested REST endpoints"], "risk": "high", "value_score": 9, "effort_months": 3})
    if legacy_signals.get("jquery_heavy"):
        paths.append({"current": "jQuery UI", "recommended": "Modern component UI", "steps": actions or ["Create a component migration inventory"], "risk": "medium", "value_score": 8, "effort_months": 2})
    if not paths:
        paths.append({"current": "Current stack", "recommended": "Supported cloud-ready stack", "steps": actions, "risk": "medium", "value_score": 7, "effort_months": 2})
    outputs["transformation"] = {
        "summary": summary, "transformation_paths": paths,
        "modernisation_phases": [{"name": "Stabilize and modernize", "items": actions, "duration_months": sum(p["effort_months"] for p in paths)}],
        "current_maturity": "legacy" if legacy_signals else "transitional", "target_state": "Tested, observable, cloud-ready services", "_model_used": model,
    }

    summary, actions = _narrative(narratives, "code_level", "Defect-risk predictions prioritize the code requiring detailed refactoring.")
    outputs["code_level"] = {
        "summary": summary, "code_smell_score": round(float(health.get("health", 0) or 0)),
        "maintainability_index": round(float(health.get("health", 0) or 0)),
        "per_function_issues": [{"file": h["file"], "function": "file-level", "issues": [h["issue"]], "refactoring_action": h["recommendation"], "cc": 0} for h in hotspots],
        "anti_pattern_catalog": [{"name": str(item), "remediation": actions[0] if actions else "Refactor and verify with tests."} for item in _as_list(health.get("summary"))[:8]],
        "l3_refactoring_plan": [{"title": action, "priority": "high", "effort_hours": 8} for action in actions],
        "quality_gates_recommended": [], "_model_used": model,
    }

    summary, actions = _narrative(narratives, "legacy_modernization", str(ml.get("summary") or "Legacy technology modernization priorities were calculated from source evidence."))
    outputs["legacy_modernization"] = {
        "summary": summary, "migration_score": ml.get("migration_score") or {},
        "recommendations": actions, "top_risk_files": [_short_path(x) for x in _as_list(ml.get("top_risk_files"))[:10]],
        "_model_used": model,
    }
    return {key: value for key, value in outputs.items() if key in run_keys}


def _enrich_prediction_sections(
    analyses: dict, analysis_result: dict, repo_path: str, model: str,
) -> dict:
    """Apply the existing source scanners and L2/L3 enrichers without extra LLM calls."""
    if "tech_debt" in analyses:
        try:
            probability_by_file = {
                _short_path(item.get("file")): item.get("probability", 0)
                for item in _as_list((analysis_result.get("ml_predictions") or {}).get("defect_predictions"))
                if isinstance(item, dict)
            }
            tech = analyses["tech_debt"]
            tech["hotspots"] = []
            tech = _validate_and_enrich(tech, _gather_all_files(analysis_result)[:12], analysis_result, repo_path)
            for hotspot in _as_list(tech.get("hotspots")):
                if not isinstance(hotspot, dict):
                    continue
                probability = probability_by_file.get(_short_path(hotspot.get("file")))
                if probability:
                    hotspot.setdefault("metrics", {})["defect_probability"] = probability
                    hotspot["prediction_confidence"] = round(float(probability) * 100)
            analyses["tech_debt"] = tech
        except Exception:
            logger.exception("source-level tech-debt enrichment failed")

    if "cloud_blockers" in analyses:
        try:
            cloud = analyses["cloud_blockers"]
            cloud["migration_phases"] = [
                {
                    "phase": 1, "title": "Cloud foundation and externalized configuration", "duration_weeks": 2,
                    "tasks": ["Externalize runtime configuration and secrets", "Add structured health and readiness endpoints"],
                    "success_criteria": ["No environment-specific configuration remains in source", "Health probes pass in staging"],
                },
                {
                    "phase": 2, "title": "Containerization and delivery automation", "duration_weeks": 3,
                    "tasks": ["Create a hardened multi-stage container build", "Add CI quality, security, and deployment gates"],
                    "success_criteria": ["Immutable image is reproducibly built", "Deployment rollback is automated"],
                },
                {
                    "phase": 3, "title": "Scale and resilience validation", "duration_weeks": 2,
                    "tasks": ["Remove in-process state", "Run horizontal scaling and failure-recovery tests"],
                    "success_criteria": ["Multiple replicas serve traffic safely", "Recovery objectives are demonstrated"],
                },
            ]
            analyses["cloud_blockers"] = _enrich_cloud_result(cloud, analysis_result, repo_path)
        except Exception:
            logger.exception("source-level cloud enrichment failed")

    if "business_rules" in analyses and repo_path:
        try:
            validation_logic = _filter_business_source_evidence(_extract_validation_logic(repo_path))
            class_entities = _extract_class_entities(repo_path)
            business = analyses["business_rules"]
            analyses["business_rules"] = _enrich_business_rules(
                business, analysis_result, validation_logic, class_entities,
            )
        except Exception:
            logger.exception("source-level business-rule enrichment failed")

    if "transformation" in analyses:
        try:
            transformation = analyses["transformation"]
            for path in _as_list(transformation.get("transformation_paths")):
                if not isinstance(path, dict):
                    continue
                current = str(path.get("current") or "current stack")
                path.setdefault("rationale", f"Replace unsupported or high-friction {current} capabilities using incremental, test-protected migration.")
                path.setdefault("migration_steps", _as_list(path.get("steps")))
                path.setdefault("version_breaking_changes", ["API and lifecycle behavior must be regression-tested before cutover"])
                path.setdefault("affected_file_patterns", [f"**/*{current.lower().replace(' ', '*')}*"])
                path.setdefault("business_benefits", ["Reduced change failure risk", "Faster supported releases", "Improved observability"])
            transformation["modernisation_phases"] = []
            transformation["roi_narrative"] = "Sequence stabilization before framework replacement so measurable risk declines before major cutovers."
            analyses["transformation"] = _enrich_transformation_result(transformation, analysis_result)
        except Exception:
            logger.exception("source-level transformation enrichment failed")

    if "microservices" in analyses and repo_path:
        try:
            call_graph = build_call_graph(repo_path, 200)
            nodes = call_graph.get("nodes") or []
            id_to_label = {node["id"]: node.get("label", "") for node in nodes if isinstance(node, dict) and node.get("id")}
            id_to_layer = {node["id"]: node.get("layer", "unknown") for node in nodes if isinstance(node, dict) and node.get("id")}
            id_to_file = {node["id"]: node.get("file", "") for node in nodes if isinstance(node, dict) and node.get("id")}
            micro = analyses["microservices"]
            micro["_call_graph_available"] = bool(nodes)
            analyses["microservices"] = _enrich_microservices_result(
                micro, call_graph, id_to_label, id_to_layer, id_to_file,
            )
        except Exception:
            logger.exception("call-graph microservices enrichment failed")

    if "code_level" in analyses and repo_path:
        try:
            top_files = _collect_top_files(analysis_result)
            functions = _extract_function_data(repo_path, top_files, 30)
            anti_hits = _scan_anti_patterns(repo_path, top_files)
            class_signals = _scan_class_signals(repo_path, top_files)
            coupling = _scan_coupling(repo_path, top_files)
            code_level = analyses["code_level"]
            for field in (
                "per_function_issues", "anti_pattern_catalog", "class_analysis", "l3_refactoring_plan",
                "quality_gates_recommended", "naming_violations", "dead_code_indicators",
            ):
                code_level[field] = []
            code_level["coupling_analysis"] = {}
            analyses["code_level"] = _enrich_code_level_result(
                code_level, functions, anti_hits, class_signals, coupling, analysis_result,
            )
        except Exception:
            logger.exception("source-level code enrichment failed")

    if "legacy_modernization" in analyses:
        try:
            ml = analysis_result.get("ml_predictions") or {}
            fingerprint = ml.get("tech_fingerprint") or {}
            legacy_techs = [str(key) for key, value in fingerprint.items() if float(value or 0) > 0]
            fallback = _legacy_fallback(legacy_techs, ml.get("migration_score") or {})
            fallback.update({
                "summary": analyses["legacy_modernization"].get("summary"),
                "migration_score": ml.get("migration_score") or {},
                "top_risk_files": analyses["legacy_modernization"].get("top_risk_files") or [],
                "_model_used": model,
            })
            analyses["legacy_modernization"] = fallback
        except Exception:
            logger.exception("legacy-modernization enrichment failed")

    return analyses


# Function: run_ai_analysis
def run_ai_analysis(
    analysis_result: dict,
    repo_path: str,
    model: str | None = None,
    progress_callback: Callable[[str, int, int], None] | None = None,
    selected: list[str] | None = None,
) -> dict:
    """
    Run all (or selected) AI analyses and return a combined report.

    Parameters
    ----------
    analysis_result : dict
        Serialised AnalysisResult from the regular code analysis pipeline.
    repo_path : str
        Path to the local repository on disk.
    model : str | None
        Ollama model id. None = auto-select.
    progress_callback : callable | None
        Called with (step_name, current_step, total_steps) for progress tracking.
    selected : list[str] | None
        Keys of analyses to run (see _ANALYSES above). None = all.

    Returns
    -------
    dict – unified AI intelligence report
    """
    client = OllamaClient()
    health = client.health()

    if not health.get("ok"):
        return {
            "ok": False,
            "error": f"Ollama not reachable at {health['host']}: {health.get('error')}",
            "ollama_health": health,
        }

    best_model = model or client.best_available_model()
    if not best_model:
        return {
            "ok": False,
            "error": "No suitable model installed. Please pull codellama:13b, deepseek-coder:6.7b, or llama3.1:8b.",
            "ollama_health": health,
        }
    prediction_model = model or client.fast_prediction_model() or best_model

    run_keys = set(selected or [k for k, *_ in _ANALYSES])
    # One bounded Ollama batch plus deterministic enrichment of every requested
    # prediction section replaces seven serial generations and one synthesis call.
    total    = len([k for k, *_ in _ANALYSES if k in run_keys]) + 1
    step     = 0

    # Function: _progress
    def _progress(name: str):
        nonlocal step
        step += 1
        if progress_callback:
            progress_callback(name, step, total)
        logger.info("[AI] Running %s (%d/%d) with model=%s", name, step, total, prediction_model)

    report: dict = {
        "ok":         True,
        "model_used": prediction_model,
        "repo_name":  analysis_result.get("repo_name", "unknown"),
        "timestamp":  time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "ollama_health": health,
        "analyses":   {},
    }

    # Generate all narratives in one inference and enrich from scanner evidence.
    _names = {k: n for k, n, *_ in _ANALYSES}
    _progress("Optimized prediction batch")
    try:
        narratives = _generate_prediction_narratives(analysis_result, run_keys, prediction_model, client)
    except Exception as exc:
        logger.warning("optimized prediction narrative failed; using scanner evidence: %s", exc)
        narratives = {}

    report["analyses"] = _build_fast_analyses(
        analysis_result=analysis_result,
        narratives=narratives,
        run_keys=run_keys,
        model=prediction_model,
    )
    report["analyses"] = _enrich_prediction_sections(
        analyses=report["analyses"],
        analysis_result=analysis_result,
        repo_path=repo_path,
        model=prediction_model,
    )
    for key, *_ in _ANALYSES:
        if key in run_keys:
            _progress(_names.get(key, key))

    # Dashboard assessments are an evidence-preserving local projection. A
    # second LLM synthesis added several minutes but introduced no new evidence.
    report["tab_assessments"] = _fallback_tab_assessments(report["analyses"])
    return report
