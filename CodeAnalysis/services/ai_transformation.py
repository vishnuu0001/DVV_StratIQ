# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: AI-powered application modernisation advisor — L2/L3 enriched.
# Date: 2026-04-02
# ---------------------------------------------------------------------------
"""
services/ai_transformation.py
------------------------------
AI-powered application modernisation advisor — L2/L3 enriched.

Covers:
  * Mainframe (COBOL/JCL) → Java / .NET / Cloud modernisation
  * Framework upgrade paths (Spring Boot 2→3, .NET 4.x→8, Angular 1→17 …)
  * Component / library replacement suggestions with version-specific migration notes
  * Database modernisation (Oracle → PostgreSQL / DynamoDB …)
  * Per-file modernisation actions
"""
from __future__ import annotations

import logging
import re

from .ollama_client import OllamaClient
from .ai_grounding import build_ground_truth, grounding_header, build_anti_hallucination_system_prompt, validate_transformation

logger = logging.getLogger(__name__)

_SYSTEM_BASE = """\
You are a principal application modernisation architect.
Given the current technology stack with EXACT version numbers and analysis metrics,
you produce a concise modernisation roadmap with per-framework migration steps,
version-specific breaking changes, and effort estimates.
You MUST only suggest technology replacements that are appropriate for the detected languages.
Do NOT recommend Node.js, React, or web frameworks for mainframe/COBOL codebases.
If a version number is not in the data, state 'version unknown' instead of inventing one.
Be concise. Limit ALL string values to 1 sentence. Always return valid JSON and nothing else."""

_PROMPT_TMPL = """\
Create a modernisation roadmap for repository "{repo_name}".

CURRENT TECHNOLOGY STACK (with versions where detected):
{tech_stack}

DEPENDENCIES WITH VERSIONS:
{dependencies}

HEALTH & DEBT:
- Health score: {health}/100 ({health_label})
- Technical debt: {debt} person-months
- Total SLOC: {sloc}
- Long-method percentage: {long_pct}%
- Top complex files: {top_files}

ARCHITECTURE:
{arch_summary}

OSS / SECURITY RISK:
- Vulnerable dependencies: {vuln_count}
- High-risk licenses: {license_risk_count}
- Vulnerable packages: {vuln_packages}

Based on the EXACT versions, provide:
1. Version-specific upgrade paths (e.g. "Spring Boot 2.7.x → 3.x requires Java 17 min, javax→jakarta migration")
2. Concrete replacement recommendations with file-level impact
3. Breaking changes specific to the detected versions

Return JSON:
{{
  "current_maturity": "<legacy|dated|modern|cloud-native>",
  "summary": "<4-5 sentences naming specific frameworks, versions, and the highest-value upgrades>",
  "transformation_paths": [
    {{
      "category": "<framework|language|database|messaging|cloud|security|testing>",
      "current": "<current technology AND version — e.g. Flask 1.1.2>",
      "recommended": "<replacement and target version — e.g. FastAPI 0.104>",
      "rationale": "<why this replacement adds value>",
      "version_breaking_changes": ["<specific breaking change from current to recommended version>"],
      "affected_file_patterns": ["<glob or path pattern of files needing changes>"],
      "effort_months": <number>,
      "risk": "low|medium|high",
      "value_score": <1-10>
    }}
  ],
  "modernisation_phases": [
    {{
      "phase": <integer>,
      "title": "<phase name>",
      "duration_months": <integer>,
      "items": ["<transformation_path.current values to tackle>"],
      "milestone": "<what you can demonstrate at end of phase>"
    }}
  ],
  "target_state": "<1-2 sentence target state description>",
  "total_effort_months": <integer>,
  "modernisation_score": <integer 0-100>
}}

Provide 3-4 transformation_paths and 2-3 modernisation_phases.
Return ONLY the JSON."""


# Function: _extract_dep_versions
def _extract_dep_versions(lang_reports: list[dict]) -> tuple[str, list[str]]:
    """
    Extract dependency names and attempt to parse version pins from language reports.
    Returns (dep_txt, vuln_packages_list).
    """
    all_deps: dict[str, str] = {}  # dep_name -> version_hint
    for lr in lang_reports:
        for dep in lr.get("dependencies", []):
            dep_str = str(dep).strip()
            # Try to parse pinned versions: dep==1.2.3 or dep>=1.0 or dep:1.0
            m = re.match(r"^([A-Za-z0-9_.\-]+)\s*[=><~^]+\s*([\d.]+)", dep_str)
            if m:
                all_deps[m.group(1)] = m.group(2)
            else:
                all_deps.setdefault(dep_str, "?")

    lines = []
    for name, ver in sorted(all_deps.items())[:45]:
        lines.append(f"  - {name}=={ver}" if ver != "?" else f"  - {name}")
    return "\n".join(lines) or "  none detected", list(all_deps.keys())[:10]


# Function: _top_complex_files
def _top_complex_files(analysis_result: dict, n: int = 5) -> str:
    """Return a short string listing the top-N most complex files."""
    all_files = []
    for lr in analysis_result.get("language_reports", []):
        for f in lr.get("files", []):
            if not f.get("error"):
                score = f.get("complexity", 0) * 3 + f.get("long_methods", 0) * 5
                all_files.append((f.get("name", "?"), lr.get("language", ""), score))
    all_files.sort(key=lambda x: -x[2])
    return ", ".join(f"{n_}({l})" for n_, l, _ in all_files[:n]) or "none"


# Function: _build_tech_stack_txt
def _build_tech_stack_txt(lang_reports: list) -> str:
    """Build tech stack string with file counts, SLOC, and top dependency hints."""
    stack_lines = []
    for lr in lang_reports:
        lang = lr.get("language", "?")
        deps = list(lr.get("dependencies", []))
        # Try to detect framework version from deps
        framework_hints = [d for d in deps[:5] if len(d) > 2]
        stack_lines.append(
            f"  {lang}: {lr.get('file_count',0)} files, {lr.get('total_sloc',0)} SLOC"
            + (f" — key deps: {', '.join(framework_hints[:3])}" if framework_hints else "")
        )
    return "\n".join(stack_lines) or "  unknown"


# Function: analyse_transformation
def analyse_transformation(
    analysis_result: dict,
    model: str | None = None,
    client: OllamaClient | None = None,
) -> dict:
    client = client or OllamaClient()

    # ── Ground truth ───────────────────────────────────────────────────
    gt = build_ground_truth(analysis_result)
    _SYSTEM = build_anti_hallucination_system_prompt(_SYSTEM_BASE, gt)

    lang_reports = analysis_result.get("language_reports", [])
    health_obj   = analysis_result.get("health", {}) or {}
    debt_obj     = analysis_result.get("debt",   {}) or {}
    oss_obj      = analysis_result.get("oss",    {}) or {}

    tech_stack_txt = _build_tech_stack_txt(lang_reports)

    # Extract deps with versions
    dep_txt, _all_dep_names = _extract_dep_versions(lang_reports)
    top_files_txt = _top_complex_files(analysis_result)

    # Long method pct
    long_pcts = [lr.get("long_methods_pct", 0) for lr in lang_reports]
    avg_long  = round(sum(long_pcts) / len(long_pcts), 1) if long_pcts else 0

    # OSS risk
    oss_details  = oss_obj.get("details") or []
    vuln_count   = sum(1 for d in oss_details if d.get("vulnerable"))
    risk_count   = sum(1 for d in oss_details if d.get("license_risk") in {"high", "viral"})
    vuln_pkgs    = [d.get("name", "?") for d in oss_details if d.get("vulnerable")][:8]

    arch     = analysis_result.get("architecture", {}) or {}
    arch_txt = ", ".join(f"{k}={v}" for k, v in (arch.get("layer_counts") or {}).items()) or "N/A"

    # Prepend grounding header
    ground_block = grounding_header(gt)

    prompt = ground_block + "\n\n" + _PROMPT_TMPL.format(
        repo_name         = gt["repo_name"],
        tech_stack        = tech_stack_txt,
        dependencies      = dep_txt,
        health            = gt["health_score"],
        health_label      = (analysis_result.get("health") or {}).get("risk_label", "unknown"),
        debt              = round(gt["debt_months"], 1),
        sloc              = gt["total_sloc"],
        long_pct          = avg_long,
        top_files         = top_files_txt,
        arch_summary      = arch_txt,
        vuln_count        = vuln_count,
        license_risk_count = risk_count,
        vuln_packages     = ", ".join(vuln_pkgs) or "none",
    )

    try:
        # Reduced max_tokens from 900 → 700 to avoid timeouts
        # timeout=540 for token generation headroom
        result = client.generate_json(prompt, model=model, system=_SYSTEM,
                                      max_tokens=700, num_ctx=5120, timeout=540)
        result["_model_used"] = model or client.best_available_model()
        result = _enrich_transformation_result(result, analysis_result)
        # Post-process: fix hallucinated stacks
        result = validate_transformation(result, gt)
        return result
    except Exception as exc:
        logger.error("ai_transformation failed: %s", exc)
        return {"error": str(exc), "summary": "AI analysis unavailable."}



# Function: _normalize_transform_path
def _normalize_transform_path(tp: dict) -> None:
    """Ensure a single transformation_path dict has required schema fields."""
    if not tp.get("migration_steps"):
        tp["migration_steps"] = []
    if not tp.get("steps"):
        tp["steps"] = tp.get("migration_steps") or []
    if not tp.get("version_breaking_changes"):
        tp["version_breaking_changes"] = []
    if not tp.get("affected_file_patterns"):
        tp["affected_file_patterns"] = []
    if not tp.get("risk"):
        tp["risk"] = "medium"
    try:
        score = int(float(tp.get("value_score", 0)))
    except Exception:
        score = 0
    tp["value_score"] = max(1, min(10, score if score else 6))
    if not tp.get("effort_months"):
        tp["effort_months"] = {
            "low": 1,
            "medium": 2,
            "high": 3,
        }.get(str(tp.get("risk", "medium")).lower(), 2)


# Function: _normalize_transform_paths
def _normalize_transform_paths(paths: list) -> list:
    """Ensure each transformation_path has required schema fields."""
    for tp in paths:
        if not isinstance(tp, dict):
            continue
        _normalize_transform_path(tp)
    return paths


# Function: _build_transform_phases
def _build_transform_phases(result: dict, paths: list) -> dict:
    """Ensure modernisation_phases are populated (build fallback if needed)."""
    phases = result.get("modernisation_phases") or []
    for ph in phases:
        if isinstance(ph, dict) and not ph.get("success_criteria"):
            ph["success_criteria"] = ["All items in phase deployed to staging"]

    if not phases and paths:
        first = [p.get("current", "unknown") for p in paths[:2] if isinstance(p, dict)]
        second = [p.get("current", "unknown") for p in paths[2:] if isinstance(p, dict)]
        phases = [
            {
                "phase": 1,
                "title": "Initial Framework Upgrades",
                "duration_months": 2,
                "items": first or ["Core dependency upgrades"],
                "milestone": "Runtime and framework baselines upgraded",
                "success_criteria": ["Core services pass regression tests"],
            },
            {
                "phase": 2,
                "title": "Platform and Architecture Modernisation",
                "duration_months": 3,
                "items": second or first[:1],
                "milestone": "Target-state architecture ready for rollout",
                "success_criteria": ["Deployment pipeline stable for target stack"],
            },
        ]
    result["modernisation_phases"] = phases
    return result


# Function: _build_transform_l3_drilldown
def _build_transform_l3_drilldown(analysis_result: dict, paths: list) -> dict:
    """Build the l3_drilldown surface data for UI/modals."""
    return {
        "top_complex_files": [
            f.get("name")
            for lr in (analysis_result.get("language_reports") or [])
            for f in (lr.get("files") or [])
            if isinstance(f, dict) and not f.get("error")
        ][:20],
        "paths_with_breaking_changes": [
            {
                "current": p.get("current"),
                "recommended": p.get("recommended"),
                "breaking_changes": p.get("version_breaking_changes") or [],
                "file_patterns": p.get("affected_file_patterns") or [],
            }
            for p in paths if isinstance(p, dict)
        ],
    }


# Function: _enrich_transformation_result
def _enrich_transformation_result(result: dict, analysis_result: dict) -> dict:
    """Ensure minimum schema fields and enrich with computed data."""
    paths = result.get("transformation_paths") or []
    result["transformation_paths"] = _normalize_transform_paths(paths)

    # Ensure security_upgrades present
    if not result.get("security_upgrades"):
        oss_obj = analysis_result.get("oss", {}) or {}
        oss_details = oss_obj.get("details") or []
        result["security_upgrades"] = [
            {
                "package": d.get("name", "?"),
                "vulnerability": "Known vulnerability — check OSS scan report",
                "upgrade_to": "latest stable",
                "effort_hours": 2,
            }
            for d in oss_details
            if d.get("vulnerable")
        ][:8]

    # Ensure modernisation_score present
    if not result.get("modernisation_score"):
        health_obj = analysis_result.get("health", {}) or {}
        h = health_obj.get("health", health_obj.get("score", 50)) if isinstance(health_obj, dict) else 50
        result["modernisation_score"] = max(15, min(85, int(h * 0.9)))

    result = _build_transform_phases(result, paths)

    path_effort = sum(int(float(p.get("effort_months", 0) or 0)) for p in paths if isinstance(p, dict))
    phase_effort = sum(int(float(ph.get("duration_months", 0) or 0)) for ph in (result.get("modernisation_phases") or []) if isinstance(ph, dict))
    if not result.get("total_effort_months"):
        result["total_effort_months"] = max(path_effort, phase_effort, 1)

    result["l3_drilldown"] = _build_transform_l3_drilldown(analysis_result, paths)

    return result
