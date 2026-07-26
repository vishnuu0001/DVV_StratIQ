# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: AI-powered legacy technology modernization advisor.
# Date: 2025-09-22
# ---------------------------------------------------------------------------
"""
ai_legacy_modernization.py
--------------------------
AI-powered legacy technology modernization advisor.

Focuses specifically on:
  - IBM mainframe stack (COBOL, JCL, CICS, VSAM, DB2 embedded SQL)
  - Classic Java EE (EJB, Struts 1/2, SOAP, WAS/WebSphere)
  - Legacy web stack (JSP scriptlets, jQuery DOM manipulation)
  - Legacy source management (PANVALET, ISPF)

Generates:
  - modernization_roadmap:   Phase-by-phase migration plan
  - technology_replacements: Old tech → recommended modern replacement
  - strangler_fig_candidates: Components safe to extract first
  - migration_risks:          Key risks and mitigation strategies
  - effort_estimate_months:   High-level total effort

Called from ai_analysis.py orchestrator.
"""
from __future__ import annotations

import logging
import re
from typing import Any, Dict, List

from .ollama_client import OllamaClient
from .ai_grounding import build_ground_truth, grounding_header, build_anti_hallucination_system_prompt

logger = logging.getLogger(__name__)

_SYSTEM_BASE = """\
You are a principal application modernization architect specializing in legacy enterprise
systems. You have deep expertise in:
- IBM mainframe (COBOL, JCL, CICS, VSAM, DB2 z/OS, PANVALET, ISPF)
- Classic Java EE (EJB, Struts 1/2, JSP scriptlets, SOAP/JAX-WS, WAS/WebSphere)
- Legacy web (jQuery spaghetti, Bootstrap 2/3, JSF)
- Modern replacements: Spring Boot, Quarkus, Kafka, PostgreSQL, React, containerization

You MUST only suggest modern replacements that are compatible with the detected legacy stack.
Do NOT recommend technologies incompatible with the detected languages.
Always return valid JSON and nothing else.
Limit ALL string values to 1-2 sentences.
Be specific about technology versions and migration steps."""

_PROMPT_TMPL = """\
Analyze the legacy technology stack for repository "{repo_name}" and produce a
prioritized modernization roadmap.

DETECTED LEGACY TECHNOLOGIES:
{legacy_tech_list}

MAINFRAME INDICATORS:
{mainframe_indicators}

JAVA EE INDICATORS:
{javaee_indicators}

WEB LEGACY INDICATORS:
{web_legacy_indicators}

CODE METRICS:
- Total SLOC: {sloc}
- Average cyclomatic complexity: {avg_cc:.1f}
- Bad practices count: {bad_count}
- Migration complexity score: {migration_score}/100 ({migration_category})

DEPENDENCY FINGERPRINT:
{fingerprint_summary}

Based on the above, provide a comprehensive modernization plan.

Return JSON with EXACTLY this structure:
{{
  "modernization_summary": "<2-3 sentences describing the overall modernization challenge>",
  "technology_replacements": [
    {{
      "legacy_tech":    "<exact legacy technology name>",
      "confidence":     <0.0-1.0>,
      "replacement":    "<recommended modern technology>",
      "rationale":      "<why this replacement>",
      "effort_months":  <number>,
      "risk":           "low|medium|high|very_high",
      "migration_pattern": "<strangler_fig|big_bang|parallel_run|api_facade>"
    }}
  ],
  "modernization_phases": [
    {{
      "phase":             <integer 1-5>,
      "title":             "<phase name>",
      "duration_months":   <integer>,
      "technologies":      ["<tech1>", "<tech2>"],
      "approach":          "<migration approach>",
      "success_criteria":  "<measurable outcome>"
    }}
  ],
  "strangler_fig_candidates": [
    {{
      "component":   "<component or layer name>",
      "rationale":   "<why good strangler fig candidate>",
      "priority":    "high|medium|low"
    }}
  ],
  "migration_risks": [
    {{
      "risk":        "<risk title>",
      "severity":    "critical|high|medium|low",
      "description": "<risk description>",
      "mitigation":  "<mitigation strategy>"
    }}
  ],
  "total_effort_months": <integer>,
  "recommended_team_size": <integer>,
  "quick_wins": ["<quick win action 1>", "<quick win action 2>", "<quick win action 3>"]
}}"""


# Function: analyse_legacy_modernization
def analyse_legacy_modernization(
    repo_name: str,
    language_reports: list,
    ml_predictions: dict,
    health_score: float = 50.0,
    total_sloc: int = 0,
    progress_cb=None,
    model: str | None = None,
    client: "OllamaClient | None" = None,
) -> dict:
    """
    Run the legacy modernization AI analysis.

    Parameters
    ----------
    repo_name        : Repository/application name
    language_reports : List of LanguageReport objects from the analyzer pipeline
    ml_predictions   : MLPredictionResult dict (from ml_predictions.run())
    health_score     : Overall health score 0-100
    total_sloc       : Total source lines of code
    progress_cb      : Optional progress callback

    Returns
    -------
    dict with legacy modernization analysis fields.
    """
    if progress_cb:
        progress_cb(10, "Analysing legacy technology stack …")

    # Build legacy tech summary from language reports
    legacy_techs, mainframe_indicators, javaee_indicators, web_legacy = (
        _extract_legacy_signals(language_reports)
    )

    if not legacy_techs:
        return _empty_result("No legacy technologies detected in this repository.")

    if progress_cb:
        progress_cb(30, "Generating modernization roadmap via LLM …")

    # Build an analysis_result-like dict for grounding
    _analysis_result = {
        "repo_name": repo_name,
        "language_reports": language_reports,
        "total_sloc": total_sloc,
        "health": {"health": health_score},
        "debt": {},
        "languages_detected": [
            (r.get("language", "") if isinstance(r, dict) else getattr(r, "language", ""))
            for r in language_reports
        ],
    }
    gt = build_ground_truth(_analysis_result)
    _SYSTEM = build_anti_hallucination_system_prompt(_SYSTEM_BASE, gt)
    ground_block = grounding_header(gt)

    # Build fingerprint summary for prompt
    tech_fp = ml_predictions.get("tech_fingerprint", {})
    fingerprint_summary = "\n".join(
        f"  - {tech}: {conf:.0%} confidence"
        for tech, conf in sorted(tech_fp.items(), key=lambda x: -x[1])
    ) or "  (none detected)"

    migration_score = ml_predictions.get("migration_score", {})
    avg_cc    = _calc_avg_cc(language_reports)
    bad_count = sum(
        len(r.get("bad_practices", []) if isinstance(r, dict) else list(getattr(r, "bad_practices", [])))
        for r in language_reports
    )

    prompt = ground_block + "\n\n" + _PROMPT_TMPL.format(
        repo_name=repo_name,
        legacy_tech_list="\n".join(f"  - {t}" for t in legacy_techs) or "  (none)",
        mainframe_indicators="\n".join(f"  - {i}" for i in mainframe_indicators) or "  (none)",
        javaee_indicators="\n".join(f"  - {i}" for i in javaee_indicators) or "  (none)",
        web_legacy_indicators="\n".join(f"  - {i}" for i in web_legacy) or "  (none)",
        sloc=total_sloc,
        avg_cc=avg_cc,
        bad_count=bad_count,
        migration_score=migration_score.get("overall", 0),
        migration_category=migration_score.get("category", "unknown"),
        fingerprint_summary=fingerprint_summary,
    )

    try:
        # Use the shared client injected by the orchestrator so the global
        # _OLLAMA_LOCK is respected and we reuse the already-loaded model.
        _client = client or OllamaClient()
        data = _client.generate_json(
            prompt,
            model=model,
            system=_SYSTEM,
            max_tokens=600,
            num_ctx=5120,
            timeout=480,
            temperature=0.0,
        )
        if progress_cb:
            progress_cb(90, "Legacy modernization analysis complete.")
        data["_model_used"] = model or _client.best_available_model()
        return data
    except Exception as exc:
        logger.error("Legacy modernization LLM call failed: %s", exc)
        return _fallback_result(legacy_techs, migration_score)


# ─── Helpers ──────────────────────────────────────────────────────────────────

# Function: _r_get
def _r_get(r: Any, key: str, default: Any = None) -> Any:
    """Unified attribute/key access for both dataclass objects and dicts."""
    if isinstance(r, dict):
        return r.get(key, default)
    return getattr(r, key, default)


_MAINFRAME_KEYWORDS = {
    "cobol", "cics", "jcl", "vsam", "db2 (embedded sql)",
    "exec sql", "panvalet", "ispf", "rexx", "pli", "asm", "assembler",
}
_JAVAEE_KEYWORDS = {
    "ejb", "struts", "was", "ibm was", "ibm websphere", "soap",
    "jax-ws", "webservice",
}
_WEB_LEGACY_KEYWORDS = {
    "jquery", "bootstrap 2", "bootstrap 3", "jsp scriptlet",
    "jsf", "jsp", "struts (taglib)",
}


# Function: _scan_keyword_matches
def _scan_keyword_matches(items: list, keywords: set, out: list, cap_len: int = 120) -> None:
    for item in items:
        item_lower = item.lower()
        for kw in keywords:
            if kw in item_lower and item not in out:
                out.append(item[:cap_len])
                break


# Function: _scan_java_ee_indicators
def _scan_java_ee_indicators(
    bad_practices: list, dependencies: list, legacy_techs: list, javaee_indicators: list, keywords: set,
) -> None:
    items = bad_practices + [str(d) for d in dependencies]
    for item in items:
        item_lower = item.lower()
        for kw in keywords:
            if kw in item_lower and item not in javaee_indicators:
                javaee_indicators.append(item[:120])
                legacy_techs.append(item[:60])
                break


# Function: _process_language_report
def _process_language_report(r: Any, legacy_techs: list, mainframe_indicators: list, javaee_indicators: list, web_legacy: list) -> None:
    language = _r_get(r, "language", "")
    lang = language.lower()

    bad_practices  = list(_r_get(r, "bad_practices", []) or [])
    dependencies   = list(_r_get(r, "dependencies", []) or [])

    # Mainframe languages
    if lang in ("mainframe", "db2/udb"):
        legacy_techs.append(language)
        _scan_keyword_matches(bad_practices + [str(d) for d in dependencies], _MAINFRAME_KEYWORDS, mainframe_indicators)

    # Java EE
    if lang == "java":
        _scan_java_ee_indicators(bad_practices, dependencies, legacy_techs, javaee_indicators, _JAVAEE_KEYWORDS)

    # IBM WAS specific
    if lang == "ibm was":
        legacy_techs.append(language)
        for bp in bad_practices:
            javaee_indicators.append(bp[:120])

    # JSP
    if lang == "jsp":
        legacy_techs.append("JSP/JSPX")
        for bp in bad_practices:
            web_legacy.append(bp[:120])

    # JavaScript web legacy
    if lang == "javascript":
        _scan_keyword_matches(bad_practices + [str(d) for d in dependencies], _WEB_LEGACY_KEYWORDS, web_legacy)


# Function: _extract_legacy_signals
def _extract_legacy_signals(
    language_reports: list,
) -> tuple:
    """
    Extract structured legacy signals from language reports.
    Handles both dataclass objects (direct analyzer output) and dicts
    (serialised analysis_result from the API / orchestrator).
    Returns (legacy_techs, mainframe_list, javaee_list, web_list).
    """
    legacy_techs:        List[str] = []
    mainframe_indicators: List[str] = []
    javaee_indicators:    List[str] = []
    web_legacy:           List[str] = []

    for r in language_reports:
        file_count = _r_get(r, "file_count", 0)
        if file_count == 0:
            continue
        _process_language_report(r, legacy_techs, mainframe_indicators, javaee_indicators, web_legacy)

    # Deduplicate
    legacy_techs = list(dict.fromkeys(legacy_techs))
    mainframe_indicators = mainframe_indicators[:15]
    javaee_indicators    = javaee_indicators[:15]
    web_legacy           = web_legacy[:10]

    return legacy_techs, mainframe_indicators, javaee_indicators, web_legacy


# Function: _calc_avg_cc
def _calc_avg_cc(language_reports: list) -> float:
    ccs = [
        _r_get(r, "avg_complexity", 1.0)
        for r in language_reports
        if _r_get(r, "file_count", 0) > 0
    ]
    return sum(ccs) / len(ccs) if ccs else 1.0


# Function: _parse_json
def _parse_json(raw: str) -> dict:
    """Extract JSON from LLM output, handling markdown code blocks."""
    raw = raw.strip()
    # Strip ```json ... ``` fencing
    m = re.search(r'```(?:json)?\s*([\s\S]+?)\s*```', raw)
    if m:
        raw = m.group(1)
    import json
    return json.loads(raw)


# Function: _empty_result
def _empty_result(reason: str) -> dict:
    return {
        "modernization_summary": reason,
        "technology_replacements": [],
        "modernization_phases": [],
        "strangler_fig_candidates": [],
        "migration_risks": [],
        "total_effort_months": 0,
        "recommended_team_size": 0,
        "quick_wins": [],
    }


# Function: _fallback_result
def _fallback_result(legacy_techs: List[str], migration_score: Dict) -> dict:
    """Rule-based fallback when LLM is unavailable."""
    overall = migration_score.get("overall", 0)
    replacements = []
    for tech in legacy_techs:
        tl = tech.lower()
        if "cobol" in tl:
            replacements.append({
                "legacy_tech": tech, "confidence": 0.9,
                "replacement": "Java Spring Boot or Kotlin microservices",
                "rationale": "COBOL modernization reduces mainframe licensing costs.",
                "effort_months": 18, "risk": "high",
                "migration_pattern": "strangler_fig"
            })
        elif "cics" in tl:
            replacements.append({
                "legacy_tech": tech, "confidence": 0.85,
                "replacement": "REST microservices on Kubernetes",
                "rationale": "CICS transaction programs map well to REST endpoints.",
                "effort_months": 12, "risk": "high",
                "migration_pattern": "api_facade"
            })
        elif "ejb" in tl:
            replacements.append({
                "legacy_tech": tech, "confidence": 0.8,
                "replacement": "Spring Boot CDI beans or Quarkus",
                "rationale": "EJBs add container overhead; CDI beans are lighter.",
                "effort_months": 6, "risk": "medium",
                "migration_pattern": "strangler_fig"
            })
        elif "struts" in tl:
            replacements.append({
                "legacy_tech": tech, "confidence": 0.9,
                "replacement": "Spring MVC or React + REST API",
                "rationale": "Struts 1 is EOL with known CVEs; Spring MVC is the natural successor.",
                "effort_months": 8, "risk": "medium",
                "migration_pattern": "strangler_fig"
            })
        elif "soap" in tl:
            replacements.append({
                "legacy_tech": tech, "confidence": 0.75,
                "replacement": "REST/OpenAPI or gRPC",
                "rationale": "SOAP is verbose and tool-heavy; REST reduces integration friction.",
                "effort_months": 4, "risk": "low",
                "migration_pattern": "api_facade"
            })
        elif "jquery" in tl:
            replacements.append({
                "legacy_tech": tech, "confidence": 0.7,
                "replacement": "React, Vue, or vanilla ES2022+",
                "rationale": "jQuery DOM manipulation is slow vs virtual DOM frameworks.",
                "effort_months": 3, "risk": "low",
                "migration_pattern": "strangler_fig"
            })

    effort = sum(r["effort_months"] for r in replacements)
    return {
        "modernization_summary": (
            f"Repository contains {len(legacy_techs)} legacy technology(ies) with "
            f"migration complexity {migration_score.get('category','unknown').upper()} "
            f"({overall}/100). Estimated total migration effort: {effort} months."
        ),
        "technology_replacements": replacements,
        "modernization_phases": [
            {"phase": 1, "title": "Foundation & Quick Wins", "duration_months": 3,
             "technologies": [r["legacy_tech"] for r in replacements if r["risk"] == "low"],
             "approach": "api_facade", "success_criteria": "All low-risk services behind REST APIs"},
            {"phase": 2, "title": "Core Migration", "duration_months": 12,
             "technologies": [r["legacy_tech"] for r in replacements if r["risk"] in ("medium","high")],
             "approach": "strangler_fig", "success_criteria": "50% of business logic migrated"},
            {"phase": 3, "title": "Decommission Legacy", "duration_months": 6,
             "technologies": [r["legacy_tech"] for r in replacements],
             "approach": "big_bang", "success_criteria": "Legacy systems decommissioned"},
        ],
        "strangler_fig_candidates": [
            {"component": r["legacy_tech"], "rationale": r["rationale"], "priority": "high"}
            for r in replacements[:3]
        ],
        "migration_risks": [
            {"risk": "Data migration complexity", "severity": "high",
             "description": "Legacy data formats require transformation pipelines.",
             "mitigation": "Build parallel data migration tooling with validation gates."},
            {"risk": "Business continuity", "severity": "critical",
             "description": "Zero downtime required during migration.",
             "mitigation": "Use strangler fig pattern with feature flags."},
        ],
        "total_effort_months": max(effort, 1),
        "recommended_team_size": max(3, min(12, len(legacy_techs) * 2)),
        "quick_wins": [
            "Add REST API facade over SOAP endpoints",
            "Replace jQuery with fetch() API for AJAX calls",
            "Containerize existing Spring Boot services",
        ],
    }
