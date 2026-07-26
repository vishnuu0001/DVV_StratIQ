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
from .ai_tech_debt     import analyse_tech_debt
from .ai_cloud_blockers import analyse_cloud_blockers
from .ai_microservices  import analyse_microservices
from .ai_business_rules import analyse_business_rules
from .ai_transformation import analyse_transformation
from .ai_code_level     import analyse_code_level
from .ai_legacy_modernization import analyse_legacy_modernization

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
    for future in concurrent.futures.as_completed(_dispatch, timeout=360):
        key = _dispatch[future]
        _progress(_names.get(key, key))
        try:
            report["analyses"][key] = future.result(timeout=300)
        except concurrent.futures.TimeoutError:
            logger.warning("%s analysis timed out after 300 s — skipping", key)
            report["analyses"][key] = {"error": "Analysis timed out after 300 s"}
        except Exception as exc:
            logger.error("%s analysis failed: %s", key, exc)
            report["analyses"][key] = {"error": str(exc)}


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

    run_keys = set(selected or [k for k, *_ in _ANALYSES])
    # call_graph build is a separate _progress() step when microservices runs, so add 1
    total    = len([k for k, *_ in _ANALYSES if k in run_keys]) + (1 if "microservices" in run_keys else 0)
    step     = 0

    # Function: _progress
    def _progress(name: str):
        nonlocal step
        step += 1
        if progress_callback:
            progress_callback(name, step, total)
        logger.info("[AI] Running %s (%d/%d) with model=%s", name, step, total, best_model)

    report: dict = {
        "ok":         True,
        "model_used": best_model,
        "repo_name":  analysis_result.get("repo_name", "unknown"),
        "timestamp":  time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "ollama_health": health,
        "analyses":   {},
    }

    # ── Build call graph in a background thread ───────────────────────────────
    _cg_future: concurrent.futures.Future | None = None
    cg: dict = {}
    if "microservices" in run_keys:
        _progress("call_graph")
        _cg_future = _CG_POOL.submit(build_call_graph, repo_path, 200)

    # ── Dispatch all non-call-graph-dependent analyses in parallel ────────────
    # Each service does significant CPU/IO preprocessing (file scanning, radon,
    # anti-pattern extraction) before issuing an LLM call.  Running 5 services
    # concurrently means that preprocessing overlaps with Ollama inference,
    # saving 30-90 s of wall time regardless of whether Ollama itself is serial.
    _names = {k: n for k, n, *_ in _ANALYSES}
    _dispatch = _dispatch_parallel_analyses(run_keys, analysis_result, repo_path, best_model, client)

    # ── Wait for call graph; once ready, queue microservices ─────────────────
    if _cg_future is not None:
        cg = _resolve_call_graph(_cg_future, report)
        if "microservices" in run_keys:
            _dispatch[_PARALLEL_POOL.submit(
                analyse_microservices, analysis_result, call_graph=cg, model=best_model, client=client
            )] = "microservices"

    # ── Collect results; report progress as each analysis completes ───────────
    _collect_dispatched_results(_dispatch, _names, _progress, report)

    try:
        report["tab_assessments"] = _generate_tab_assessments(
            analysis_result=analysis_result,
            analyses=report.get("analyses", {}),
            model=best_model,
            client=client,
        )
    except Exception as exc:
        logger.warning("tab_assessment synthesis failed: %s", exc)
        report["tab_assessments"] = _fallback_tab_assessments(report.get("analyses", {}))

    return report
