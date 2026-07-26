# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: LLM-powered cloud migration blocker identification and remediation guidance.
# Date: 2026-06-05
# ---------------------------------------------------------------------------
"""
services/ai_cloud_blockers.py
------------------------------
LLM-powered cloud migration blocker identification and remediation guidance.
L2/L3 enriched: per-file blocker evidence, 12-factor violations, specific code patterns.
"""
from __future__ import annotations

import logging
import os
import re
from pathlib import Path

from .ollama_client import OllamaClient
from .ai_grounding import build_ground_truth, grounding_header, build_anti_hallucination_system_prompt

logger = logging.getLogger(__name__)

_SKIP_DIRS_CB = {
    ".git", ".venv", "venv", "env", "node_modules", "__pycache__",
    "dist", "build", "target", "vendor",
}

# Patterns that indicate specific cloud-readiness blockers at code level
_CLOUD_CODE_PATTERNS = [
    ("hardcoded_port",   r"""(?:port|PORT)\s*[=:]\s*(\d{2,5})(?!\s*#\s*default)""",               "Hardcoded port number"),
    ("hardcoded_ip",     r"""["']\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(?::\d+)?["']""",             "Hardcoded IP address"),
    ("hardcoded_path",   r"""["'](?:/[a-zA-Z0-9_.\-]+){2,}["']""",                                 "Hardcoded filesystem path"),
    ("env_credential",   r"""(?:password|passwd|secret|api_key|apikey|token)\s*=\s*["'][^"']{4,}["']""", "Hardcoded credential/secret"),
    ("local_file_store", r"""open\s*\(|file_path|FileStorage|local.*storage|/tmp/""",              "Local file storage (not cloud-native)"),
    ("global_state",     r"""^(?:global\s+\w+|\w+\s*=\s*\[\]\s*$|\w+\s*=\s*\{\}\s*$)""",         "Module-level mutable global state"),
    ("sync_sleep",       r"""\btime\.sleep\b|\bThread\.sleep\b|\bsleep\(\d""",                     "Blocking sleep (bad for containers)"),
    ("db_conn_string",   r"""(?:DB_URL|DATABASE_URL|connection_string|connect_str)\s*=\s*["'][^"']+["']""", "Hardcoded DB connection string"),
    ("missing_health",   r"""@app\.route.*health|/health|/ping|/ready|/liveness""",               "Health-check endpoint (PRESENT — booster)"),
    ("sys_exit",         r"""\bsys\.exit\b|\bSystem\.exit\b|\bprocess\.exit\b""",                 "Hard process exit (breaks container restart)"),
]

# Pre-compile all patterns once at import time to avoid recompilation on every scan call
_COMPILED_PATTERNS = [
    (ap_id, re.compile(pat, re.MULTILINE | re.IGNORECASE), desc)
    for ap_id, pat, desc in _CLOUD_CODE_PATTERNS
]

_SYSTEM_BASE = """\
You are a cloud migration architect with deep expertise in containerisation,
Kubernetes, 12-factor apps, and cloud-native patterns.
Given code analysis results WITH specific file-level evidence you identify precise
blockers at the file AND code-pattern level, and produce a concise migration roadmap.
You MUST only reference files and patterns that appear in the evidence data provided.
Do NOT invent file names, code patterns, or blockers not supported by the data.
Be concise. Limit ALL string values to 1 sentence. Always return valid JSON and nothing else."""

_PROMPT_TMPL = """\
Analyse cloud-readiness data for repository "{repo_name}".

CLOUD-READY SCORE: {cloud_score}/100  (label: {cloud_label})

STATIC ANALYSIS BLOCKERS:
{blockers}

BOOSTERS (already cloud-ready practices):
{boosters}

FILE-LEVEL CLOUD BLOCKER EVIDENCE (L2/L3 — actual file names and code patterns found):
{file_evidence}

DEPENDENCY CLOUD RECOMMENDATIONS:
{recs}

ARCHITECTURE layers:
{arch_summary}

Produce a comprehensive JSON cloud-readiness report:
{{
  "migration_readiness": "<ready|needs_work|major_refactor|not_ready>",
  "summary": "<executive summary 3-4 sentences referencing specific files and patterns found>",
  "twelve_factor_compliance": {{
    "codebase": "pass|partial|fail",
    "dependencies": "pass|partial|fail",
    "config": "pass|partial|fail",
    "backing_services": "pass|partial|fail",
    "build_release_run": "pass|partial|fail",
    "processes": "pass|partial|fail",
    "port_binding": "pass|partial|fail",
    "concurrency": "pass|partial|fail",
    "disposability": "pass|partial|fail",
    "dev_prod_parity": "pass|partial|fail",
    "logs": "pass|partial|fail",
    "admin_processes": "pass|partial|fail",
    "overall_score": <integer 0-12>
  }},
  "blockers": [
    {{
      "title": "<blocker name>",
      "description": "<what this blocker means and why it prevents cloud migration>",
      "impacted_files": ["<exact relative file paths>"],
      "impacted_pattern": "<the code pattern that is problematic, e.g. 'port = 8080'>",
      "twelve_factor_violation": "<which of the 12 factors this violates, e.g. III: Config>",
      "remediation": "<concrete step-by-step fix — name the environment variable or config key to create>",
      "remediation_example": "<before: port=8080 | after: port=int(os.getenv('APP_PORT', 8080))>",
      "effort_days": <integer>,
      "severity": "critical|high|medium|low"
    }}
  ],
  "migration_phases": [
    {{
      "phase": <integer>,
      "title": "<phase name>",
      "tasks": ["<specific task with file names where applicable>"],
      "duration_weeks": <integer>,
      "deliverable": "<what is ready to deploy at end of phase>"
    }}
  ],
  "containerisation_strategy": "<1-2 sentence containerisation guidance for this tech stack>",
  "target_architecture": "<1-2 sentence target cloud architecture recommendation>"
}}

Provide 3-4 blockers and 2 migration phases. Return ONLY the JSON."""


_CLOUD_SOURCE_EXTS = {".py", ".java", ".cs", ".js", ".ts", ".go", ".rb", ".php", ".yml", ".yaml", ".env", ".properties", ".cfg", ".ini"}


# Function: _scan_file_for_cloud_patterns
def _scan_file_for_cloud_patterns(source: str, rel: str, evidence: dict) -> None:
    for ap_id, compiled, _desc in _COMPILED_PATTERNS:
        for m in compiled.finditer(source):
            snippet = m.group(0)[:60].strip().replace("\n", " ")
            evidence[ap_id].setdefault(rel, []).append(snippet)
            if len(evidence[ap_id].get(rel, [])) >= 3:
                break


# Function: _scan_dir_for_cloud_evidence
def _scan_dir_for_cloud_evidence(dir_path: Path, filenames: list, root: Path, evidence: dict, scanned: int) -> int:
    for fname in filenames:
        if scanned >= 60:
            break
        fpath = dir_path / fname
        if fpath.suffix.lower() not in _CLOUD_SOURCE_EXTS:
            continue
        try:
            rel = str(fpath.relative_to(root))
        except ValueError:
            rel = fpath.name
        try:
            source = fpath.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        scanned += 1
        _scan_file_for_cloud_patterns(source, rel, evidence)
    return scanned


# Function: _format_cloud_evidence_lines
def _format_cloud_evidence_lines(evidence: dict) -> list:
    lines: list[str] = []
    for ap_id, _compiled, desc in _COMPILED_PATTERNS:
        file_hits = evidence.get(ap_id, {})
        if not file_hits:
            continue
        total = sum(len(v) for v in file_hits.values())
        lines.append(f"  [{desc}] — {total} occurrence(s) across {len(file_hits)} file(s):")
        for f, snippets in list(file_hits.items())[:4]:
            s = snippets[0][:50] if snippets else ""
            lines.append(f"    {f}: `{s}`")
    return lines


# Function: _append_analyzer_bad_practices
def _append_analyzer_bad_practices(lines: list, analysis_result: dict) -> None:
    # Also include any bad_practices already detected by language analyzers
    for lr in analysis_result.get("language_reports", []):
        for bp in lr.get("bad_practices", [])[:5]:
            lines.append(f"  [Analyzer/{lr.get('language','?')}] {bp}")


# Function: _scan_cloud_evidence
def _scan_cloud_evidence(analysis_result: dict, repo_path: str) -> str:
    """
    Scan source files for specific cloud-blocker code patterns.
    Returns formatted string of file-level evidence for the LLM prompt.

    Uses os.walk with in-place dir pruning so _SKIP_DIRS_CB directories
    are never descended into.  Compiled patterns (_COMPILED_PATTERNS) are
    reused from module level — no per-call re.compile() overhead.
    """
    if not repo_path:
        return "  (no repo path — cannot perform file-level scan)"
    root = Path(repo_path)
    if not root.exists():
        return "  (repo path not found on disk)"

    # Build per-pattern → {file: [match_snippets]} evidence
    evidence: dict[str, dict[str, list[str]]] = {ap[0]: {} for ap in _CLOUD_CODE_PATTERNS}

    scanned = 0
    for dirpath, dirnames, filenames in os.walk(str(root)):
        # Prune skip dirs so os.walk never descends into them
        dirnames[:] = [d for d in dirnames if d not in _SKIP_DIRS_CB]
        dir_path = Path(dirpath)
        scanned = _scan_dir_for_cloud_evidence(dir_path, filenames, root, evidence, scanned)
        if scanned >= 60:
            break

    lines = _format_cloud_evidence_lines(evidence)
    _append_analyzer_bad_practices(lines, analysis_result)

    return "\n".join(lines) or "  (no cloud blocker patterns found in scanned files)"


# Function: _build_cloud_recs_txt
def _build_cloud_recs_txt(cloud_recs: dict) -> str:
    # Top cloud service recommendations
    recs_list = []
    for svc in (cloud_recs.get("recommendations") or [])[:10]:
        if isinstance(svc, dict):
            recs_list.append(f"  • {svc.get('service','?')}: {svc.get('reason','')}")
    return "\n".join(recs_list) or "  (no service recommendations)"


# Function: analyse_cloud_blockers
def analyse_cloud_blockers(
    analysis_result: dict,
    model: str | None = None,
    client: OllamaClient | None = None,
    repo_path: str = "",
) -> dict:
    client = client or OllamaClient()

    # ── Ground truth ──────────────────────────────────────────────────
    gt = build_ground_truth(analysis_result)
    _SYSTEM = build_anti_hallucination_system_prompt(_SYSTEM_BASE, gt)

    cloud = analysis_result.get("cloud", {}) or {}
    cloud_recs = analysis_result.get("cloud_recommendations", {}) or {}
    arch   = analysis_result.get("architecture", {}) or {}

    blockers_txt = "\n".join(f"  - {b}" for b in (cloud.get("blockers") or [])[:20]) or "  none detected"
    boosters_txt = "\n".join(f"  + {b}" for b in (cloud.get("boosters") or [])[:15]) or "  none detected"

    # File-level cloud blocker evidence (L2/L3)
    file_evidence = _scan_cloud_evidence(analysis_result, repo_path)

    recs_txt = _build_cloud_recs_txt(cloud_recs)

    # Architecture summary
    layer_counts = arch.get("layer_counts") or {}
    arch_txt = ", ".join(f"{k}={v}" for k, v in layer_counts.items()) or "unknown"

    ground_block = grounding_header(gt)

    prompt = ground_block + "\n\n" + _PROMPT_TMPL.format(
        repo_name    = gt["repo_name"],
        cloud_score  = round((cloud.get("total") or cloud.get("score") or 0), 1),
        cloud_label  = cloud.get("label", "unknown"),
        blockers     = blockers_txt,
        boosters     = boosters_txt,
        file_evidence= file_evidence,
        recs         = recs_txt,
        arch_summary  = arch_txt,
    )

    try:
        result = client.generate_json(prompt, model=model, system=_SYSTEM,
                                      max_tokens=600, num_ctx=5120, timeout=540)
        result["_model_used"] = model or client.best_available_model()
        result = _enrich_cloud_result(result, analysis_result, repo_path)
        return result
    except Exception as exc:
        logger.error("ai_cloud_blockers failed: %s", exc)
        return {"error": str(exc), "summary": "AI analysis unavailable."}



# Function: _norm_cb_severity
def _norm_cb_severity(v: str) -> str:
    s = str(v or "").lower().strip()
    if s in {"critical", "high", "medium", "low"}:
        return s
    return "medium"


# Function: _default_cloud_blocker
def _default_cloud_blocker(b) -> dict:
    return {
        "title": str(b),
        "description": f"Detected by static analysis: {b}",
        "impacted_files": [],
        "impacted_pattern": "",
        "twelve_factor_violation": "III: Config",
        "remediation": "Move hardcoded values to environment variables",
        "remediation_example": "Before: value='hardcoded' | After: value=os.getenv('VALUE_NAME')",
        "effort_days": 1,
        "severity": "medium",
    }


# Function: _normalize_one_cloud_blocker
def _normalize_one_cloud_blocker(b: dict) -> None:
    b["severity"] = _norm_cb_severity(b.get("severity"))
    if not isinstance(b.get("impacted_files"), list):
        b["impacted_files"] = []
    pattern = str(b.get("impacted_pattern") or "").strip()
    if pattern and not b.get("impacted_files_pattern"):
        b["impacted_files_pattern"] = pattern
    if not b.get("effort_days"):
        b["effort_days"] = {
            "critical": 3,
            "high": 2,
            "medium": 1,
            "low": 1,
        }.get(b["severity"], 1)
    b.setdefault("l3_evidence", {
        "impacted_files": b.get("impacted_files", []),
        "pattern": b.get("impacted_pattern") or "",
        "example_fix": b.get("remediation_example") or "",
    })


# Function: _normalize_cloud_blockers
def _normalize_cloud_blockers(blockers: list, cloud: dict) -> list:
    """Ensure blockers list is populated and each entry has normalized schema."""
    if not blockers:
        for b in (cloud.get("blockers") or [])[:5]:
            blockers.append(_default_cloud_blocker(b))

    for b in blockers:
        if not isinstance(b, dict):
            continue
        _normalize_one_cloud_blocker(b)
    return blockers


# Function: _ensure_twelve_factor
def _ensure_twelve_factor(result: dict, cloud: dict) -> dict:
    """Ensure twelve_factor_compliance block is present."""
    if not result.get("twelve_factor_compliance"):
        score = int(round((cloud.get("total") or cloud.get("score") or 0) / 100 * 12))
        result["twelve_factor_compliance"] = {
            "codebase": "pass",
            "dependencies": "pass" if score >= 8 else "partial",
            "config": "fail" if score < 6 else "partial",
            "backing_services": "partial",
            "build_release_run": "partial",
            "processes": "partial",
            "port_binding": "pass" if score >= 6 else "fail",
            "concurrency": "partial",
            "disposability": "partial",
            "dev_prod_parity": "partial",
            "logs": "partial",
            "admin_processes": "partial",
            "overall_score": score,
        }
    return result


# Function: _ensure_container_strategy
def _ensure_container_strategy(result: dict, analysis_result: dict) -> dict:
    """Ensure containerisation_strategy is a structured dict."""
    if not isinstance(result.get("containerisation_strategy"), dict):
        cs = result.get("containerisation_strategy", "")
        result["containerisation_strategy"] = {
            "guidance": str(cs) if cs else "Add Dockerfile with multi-stage build",
            "base_image": "python:3.11-slim" if "python" in " ".join(analysis_result.get("languages_detected", [])).lower() else "openjdk:17-slim",
            "multi_stage": True,
            "health_check_path": "/health",
            "env_vars_to_externalise": [],
            "volumes_needed": [],
        }
    return result


# Function: _ensure_k8s_readiness
def _ensure_k8s_readiness(result: dict, blockers: list) -> dict:
    """Ensure kubernetes_readiness block is present."""
    if not result.get("kubernetes_readiness"):
        result["kubernetes_readiness"] = {
            "stateless": "partial",
            "config_via_env": "fail" if blockers else "pass",
            "graceful_shutdown": "partial",
            "resource_limits": "not_set",
            "recommendations": [
                "Add graceful SIGTERM handler",
                "Define resource requests and limits in Deployment",
                "Add liveness and readiness probes",
            ],
        }
    return result


# Function: _enrich_cloud_result
def _enrich_cloud_result(result: dict, analysis_result: dict, repo_path: str) -> dict:
    """Ensure minimum required fields and enrich with computed data."""
    cloud = analysis_result.get("cloud", {}) or {}

    blockers = _normalize_cloud_blockers(result.get("blockers") or [], cloud)
    result["blockers"] = blockers

    # Derive deterministic migration readiness from static score and blocker severity
    static_score = float(cloud.get("total") or cloud.get("score") or 0)
    critical = sum(1 for b in blockers if isinstance(b, dict) and b.get("severity") == "critical")
    high = sum(1 for b in blockers if isinstance(b, dict) and b.get("severity") == "high")
    if critical > 0 or static_score < 30:
        result["migration_readiness"] = "not_ready"
    elif high >= 2 or static_score < 50:
        result["migration_readiness"] = "major_refactor"
    elif static_score < 70:
        result["migration_readiness"] = "needs_work"
    else:
        result["migration_readiness"] = "ready"

    result = _ensure_twelve_factor(result, cloud)
    result = _ensure_container_strategy(result, analysis_result)

    if not result.get("files_requiring_changes"):
        result["files_requiring_changes"] = []

    result = _ensure_k8s_readiness(result, blockers)

    result["kpi"] = {
        "critical_blockers": critical,
        "high_blockers": high,
        "total_blockers": len([b for b in blockers if isinstance(b, dict)]),
        "estimated_days": sum(int(b.get("effort_days", 0) or 0) for b in blockers if isinstance(b, dict)),
        "static_cloud_score": round(static_score, 1),
    }

    return result
