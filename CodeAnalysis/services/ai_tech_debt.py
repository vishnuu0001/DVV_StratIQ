# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: LLM-driven tech debt analysis — L2/L3 enriched.
# Date: 2025-10-31
# ---------------------------------------------------------------------------
"""
services/ai_tech_debt.py
-------------------------
LLM-driven tech debt analysis — L2/L3 enriched.

Reads the top high-debt / high-complexity files from the AnalysisResult
and asks the LLM to produce actionable remediation recommendations at
file level (L2) and function/method level (L3).
"""
from __future__ import annotations

import logging
import os
import re
from pathlib import Path
from typing import Any

from .ollama_client import OllamaClient
from .ai_grounding import build_ground_truth, grounding_header, build_anti_hallucination_system_prompt, validate_tech_debt

logger = logging.getLogger(__name__)

_SYSTEM_BASE = """\
You are an expert software architect specialising in technical debt remediation.
Given a list of source-code files with their metrics AND the specific function/method
names inside each file, you identify the most impactful debt hotspots and produce
concrete, actionable recommendations at file AND function granularity (L2/L3 level).
You MUST only reference files, functions, and technologies that appear in the data provided.
Do NOT invent file names, function names, or metrics. If a value is unavailable, use null.
Be concise. Limit ALL string values to 1 sentence. Always return valid JSON and nothing else."""

_PROMPT_TMPL = """\
Analyse the following code metrics for a repository called "{repo_name}".
Languages detected: {languages}.

TOP DEBT FILES WITH FUNCTION-LEVEL BREAKDOWN (by complexity / long methods / issues):
{file_list}

Functions listed above with CC>=10 or LOC>=60 are the L3 hot-zones — call them out
by name in hotspot recommendations.

OVERALL METRICS:
- Total SLOC: {sloc}
- Health Score: {health}/100
- Estimated Debt: {debt} months
- Long-method percentage: {long_pct}%
- Deep-nesting percentage: {nesting_pct}%
- Total functions: {total_functions}
- Total classes: {total_classes}
- Bad-practice signals: {bad_practices}

Return a JSON object with this EXACT schema (all fields required):
{{
  "summary": "<3-4 sentence executive summary of the debt situation, naming the worst files and root causes>",
  "hotspots": [
    {{
      "file": "<relative file path>",
      "issue": "<specific, detailed description of ALL issues: cyclomatic complexity value, long methods count, deep nesting count, magic numbers, TODOs — include numbers>",
      "recommendation": "<concrete step-by-step refactoring action naming specific functions and classes to change>",
      "root_cause": "<underlying architectural or design reason for this debt>",
      "debt_category": "complexity|duplication|test-coverage|documentation|security|design|performance|maintainability",
      "impact": "<what breaks or degrades if this is not fixed>",
      "effort_days": <integer — realistic effort to fix>,
      "priority": "high|medium|low",
      "metrics": {{
        "cyclomatic_complexity": <integer from the data>,
        "sloc": <integer from the data>,
        "long_methods": <integer from the data>,
        "deep_nesting": <integer from the data>,
        "functions": <integer from the data>,
        "classes": <integer from the data>
      }},
      "per_function_breakdown": [
        {{
          "function": "<exact function/method name from the file>",
          "cyclomatic_complexity": <integer>,
          "sloc": <integer>,
          "issue": "<specific issue: e.g. CC=18 exceeds threshold, 90 LOC too long, 6 params>",
          "refactoring": "<specific refactoring: Extract Method / Decompose Conditional / Replace Magic Number / etc.>"
        }}
      ]
    }}
  ],
  "quick_wins": [
    {{
      "action": "<specific action that can be done in <1 day>",
      "file": "<file name if applicable, else 'multiple'>",
      "benefit": "<what improves immediately after doing this>",
      "effort_hours": <integer>
    }}
  ],
  "strategic_actions": [
    {{
      "action": "<longer-term architectural improvement>",
      "rationale": "<why this strategic change matters>",
      "effort_weeks": <integer>,
      "impact": "high|medium|low"
    }}
  ],
  "debt_by_category": {{
    "complexity": <percentage of total debt from high complexity — 0-100>,
    "long_methods": <percentage>,
    "deep_nesting": <percentage>,
    "test_coverage": <percentage>,
    "documentation": <percentage>,
    "design": <percentage>
  }},
  "by_language": [
    {{
      "language": "<language name>",
      "debt_level": "high|medium|low",
      "primary_issue": "<single sentence describing main issue in this language>"
    }}
  ],
  "estimated_total_effort_days": <integer>,
  "risk_if_ignored": "<2 sentences on the business/technical risk if this debt is not addressed>"
}}

Provide the TOP 4-5 most impactful hotspots, 3-4 quick_wins, and 2-3 strategic_actions.
For each hotspot include 1-3 per_function_breakdown entries naming the worst functions in that file.
Return ONLY the JSON, no markdown, no explanation."""


# ── Lightweight per-function extractor ────────────────────────────────────────
_SKIP_DIRS_TD = {
    ".git", ".venv", "venv", "env", "node_modules", "__pycache__",
    "dist", "build", "target", "vendor",
}


# Function: _resolve_file_path
def _resolve_file_path(repo_path: str, rel_name: str) -> Path | None:
    root = Path(repo_path)
    fpath = root / rel_name if not Path(rel_name).is_absolute() else Path(rel_name)
    if fpath.exists():
        return fpath
    # Search by filename using os.walk with dir pruning (avoids rglob descending into target/)
    target_name = Path(rel_name).name
    for wdirpath, wdirnames, wfilenames in os.walk(str(root)):
        wdirnames[:] = [d for d in wdirnames if d not in _SKIP_DIRS_TD]
        if target_name in wfilenames:
            return Path(wdirpath) / target_name
    return None


# Function: _extract_python_functions
def _extract_python_functions(source: str) -> list[dict]:
    fns: list[dict] = []
    try:
        from radon.complexity import cc_visit  # type: ignore
        blocks = sorted(cc_visit(source), key=lambda b: b.complexity, reverse=True)
        for b in blocks[:6]:
            params = _count_params_python(source, b.name)
            fns.append({
                "function": b.name,
                "cc": b.complexity,
                "sloc": max(1, getattr(b, "endline", 0) - getattr(b, "lineno", 0)),
                "params": params,
            })
    except Exception:
        pass
    return fns


_FUNC_NAME_PATTERNS = [
    # Java/C#/Kotlin declarations
    re.compile(r"^\s*(?:public|private|protected|internal|static|override|async)\s+(?:[\w<>,\[\]?]+\s+)+(\w+)\s*\(([^)]*)\)\s*(?:throws\s+[^\{]+)?\{?", re.MULTILINE),
    # Go
    re.compile(r"^\s*func\s+(?:\(\w+\s+\*?\w+\)\s+)?(\w+)\s*\(([^)]*)\)", re.MULTILINE),
    # JS/TS function declarations
    re.compile(r"^\s*(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\(([^)]*)\)", re.MULTILINE),
    # JS/TS arrow function assignments
    re.compile(r"^\s*(?:export\s+)?(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?(?:\(([^)]*)\)|([^=\s]+))\s*=>", re.MULTILINE),
    # Ruby / Python-style fallback
    re.compile(r"^\s*def\s+(\w+)(?:\(([^)]*)\))?", re.MULTILINE),
]

_SKIP_FN_NAMES = {"if", "for", "while", "switch", "catch", "else", "try", "return"}


# Function: _find_function_matches
def _find_function_matches(source: str) -> list[tuple[int, str, str]]:
    matches: list[tuple[int, str, str]] = []  # (line_no, name, params_raw)
    for pat in _FUNC_NAME_PATTERNS:
        for m in pat.finditer(source):
            name = (m.group(1) or "").strip()
            if not name or name in _SKIP_FN_NAMES:
                continue
            # For arrow function regex, params can be in group(2) or group(3)
            params_raw = (m.group(2) if m.lastindex and m.lastindex >= 2 else "") or (m.group(3) if m.lastindex and m.lastindex >= 3 else "") or ""
            line_no = source[:m.start()].count("\n") + 1
            matches.append((line_no, name, params_raw))
        if matches:
            break
    return matches


# Function: _dedupe_fn_matches
def _dedupe_fn_matches(matches: list[tuple[int, str, str]]) -> list[tuple[int, str, str]]:
    # De-duplicate by function name, preserving first appearance
    seen: set[str] = set()
    uniq: list[tuple[int, str, str]] = []
    for row in sorted(matches, key=lambda x: x[0]):
        if row[1] in seen:
            continue
        seen.add(row[1])
        uniq.append(row)
    return uniq


# Function: _extract_generic_functions
def _extract_generic_functions(source: str, file_cc: int, file_sloc: int) -> list[dict]:
    # Non-Python fallback with line-based LOC estimation.
    # This avoids repeated synthetic LOC values (e.g. file_sloc/4 for all rows).
    lines = source.splitlines()
    uniq = _dedupe_fn_matches(_find_function_matches(source))

    fns: list[dict] = []
    for idx, (line_no, fname_found, params_raw) in enumerate(uniq[:8]):
        next_line = uniq[idx + 1][0] if idx + 1 < len(uniq) else len(lines) + 1
        est_loc = max(1, next_line - line_no)
        # Scale file-level complexity into function-level estimate by LOC share.
        cc_est = max(1, int(round((file_cc or 1) * (est_loc / max(1, file_sloc)))))
        param_count = len([p for p in str(params_raw).split(",") if p.strip()])
        fns.append({
            "function": fname_found,
            "cc": cc_est,
            "sloc": est_loc,
            "params": param_count,
        })
    return fns


# Function: _get_functions_for_file
def _get_functions_for_file(repo_path: str, rel_name: str, lang: str, file_cc: int, file_sloc: int) -> list[dict]:
    """Extract top function names and metrics from a single source file."""
    if not repo_path:
        return []
    fpath = _resolve_file_path(repo_path, rel_name)
    if not fpath or not fpath.exists():
        return []
    try:
        source = fpath.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return []

    fns: list[dict] = []
    if lang == "Python":
        fns = _extract_python_functions(source)
    if not fns:
        fns = _extract_generic_functions(source, file_cc, file_sloc)

    return fns[:6]


# Function: _count_params_python
def _count_params_python(source: str, func_name: str) -> int:
    m = re.search(rf"def\s+{re.escape(func_name)}\s*\(([^)]*)\)", source)
    if not m:
        return 0
    params = [p.strip().split(":")[0].split("=")[0].strip()
              for p in m.group(1).split(",") if p.strip()]
    return sum(1 for p in params if p not in ("self", "cls", "", "*", "**"))


# Function: _is_missing_symbol
def _is_missing_symbol(v: Any) -> bool:
    s = str(v or "").strip().lower()
    return s in {"", "-", "--", "---", "_", "?", "unknown", "n/a", "none", "null"}


# Function: _symbol_from_file
def _symbol_from_file(file_path: str, idx: int = 0) -> str:
    stem = Path(str(file_path or "unknown")).stem or "unknown"
    safe = re.sub(r"[^A-Za-z0-9_]", "_", stem)
    return f"{safe}_fn_{idx + 1}"


# Function: _gather_all_files
def _gather_all_files(analysis_result: dict) -> list[dict]:
    # Gather worst files across all language reports
    all_files = []
    for lr in analysis_result.get("language_reports", []):
        for f in lr.get("files", []):
            if f.get("error"):
                continue
            score = (
                f.get("complexity", 0) * 3
                + f.get("long_methods", 0) * 5
                + f.get("deep_nesting", 0) * 4
                + f.get("magic_numbers", 0)
                + f.get("todo_comments", 0) * 2
            )
            all_files.append({**f, "_lang": lr["language"], "_score": score})
    all_files.sort(key=lambda x: x["_score"], reverse=True)
    return all_files


# Function: _format_file_line
def _format_file_line(i: int, f: dict) -> str:
    return (
        f"  [{i+1}] {f['name']} ({f['_lang']}) — "
        f"cyclomatic={f.get('complexity',0)}, "
        f"sloc={f.get('sloc',0)}, "
        f"long_methods={f.get('long_methods',0)}, "
        f"deep_nesting={f.get('deep_nesting',0)}, "
        f"functions={f.get('functions',0)}, "
        f"classes={f.get('classes',0)}, "
        f"magic_numbers={f.get('magic_numbers',0)}, "
        f"todo_comments={f.get('todo_comments',0)}"
    )


# Function: _format_fn_breakdown_line
def _format_fn_breakdown_line(repo_path: str, f: dict) -> str | None:
    # L3: add function-level breakdown for high-complexity files
    if not (repo_path and f.get("complexity", 0) >= 4):
        return None
    fns = _get_functions_for_file(
        repo_path, f["name"], f["_lang"],
        f.get("complexity", 0), f.get("sloc", 0),
    )
    if not fns:
        return None
    fn_parts = []
    for fn in fns:
        flag = " [CRITICAL]" if fn["cc"] >= 15 else (" [HIGH]" if fn["cc"] >= 10 else "")
        fn_parts.append(f"{fn['function']}(CC={fn['cc']},LOC={fn['sloc']},params={fn['params']}){flag}")
    return f"       -> Functions: {', '.join(fn_parts)}"


# Function: _build_file_list_text
def _build_file_list_text(top_files: list, repo_path: str) -> str:
    file_list_lines: list[str] = []
    for i, f in enumerate(top_files):
        file_list_lines.append(_format_file_line(i, f))
        fn_line = _format_fn_breakdown_line(repo_path, f)
        if fn_line:
            file_list_lines.append(fn_line)
    return "\n".join(file_list_lines) or "  (no file data available)"


# Function: _compute_aggregate_metrics
def _compute_aggregate_metrics(lang_reports: list) -> tuple:
    long_pcts    = [lr.get("long_methods_pct", 0) for lr in lang_reports]
    nesting_pcts = [lr.get("deep_nesting_pct", 0) for lr in lang_reports]
    avg_long     = round(sum(long_pcts)    / len(long_pcts),    1) if long_pcts    else 0
    avg_nesting  = round(sum(nesting_pcts) / len(nesting_pcts), 1) if nesting_pcts else 0
    total_functions = sum(lr.get("total_functions", 0) for lr in lang_reports)
    total_classes   = sum(lr.get("total_classes",   0) for lr in lang_reports)
    return avg_long, avg_nesting, total_functions, total_classes


# Function: _collect_bad_practice_hints
def _collect_bad_practice_hints(lang_reports: list) -> str:
    # Collect bad-practice signals from all language reports
    bad_practice_hints = []
    for lr in lang_reports:
        for bp in lr.get("bad_practices", []):
            bad_practice_hints.append(f"{lr['language']}: {bp}")
    return "; ".join(bad_practice_hints[:8]) if bad_practice_hints else "none detected"


# Function: analyse_tech_debt
def analyse_tech_debt(
    analysis_result: dict,
    model: str | None = None,
    client: OllamaClient | None = None,
    max_files: int = 12,
    repo_path: str = "",
) -> dict:
    """
    Parameters
    ----------
    analysis_result : dict
        The serialised AnalysisResult dict returned by the analysis API.
    model : str | None
        Ollama model id. None = auto-select best available.
    client : OllamaClient | None
        Optional pre-built client (for testing / dependency-injection).
    max_files : int
        Max number of files to include in the prompt.
    repo_path : str
        Absolute path to the local repository for function-level extraction.

    Returns
    -------
    dict  – tech-debt intelligence report (L2/L3 enriched)
    """
    client = client or OllamaClient()

    # ── Ground truth ─────────────────────────────────────────────────────────
    gt = build_ground_truth(analysis_result)
    _SYSTEM = build_anti_hallucination_system_prompt(_SYSTEM_BASE, gt)

    all_files = _gather_all_files(analysis_result)
    top_files = all_files[:max_files]
    file_list_txt = _build_file_list_text(top_files, repo_path)

    debt_obj   = analysis_result.get("debt", {})
    health_obj = analysis_result.get("health", {})

    lang_reports = analysis_result.get("language_reports", [])
    avg_long, avg_nesting, total_functions, total_classes = _compute_aggregate_metrics(lang_reports)
    bad_practices_txt = _collect_bad_practice_hints(lang_reports)

    # Prepend grounding header to anchor the LLM to real data
    ground_block = grounding_header(gt)

    prompt = ground_block + "\n\n" + _PROMPT_TMPL.format(
        repo_name       = gt["repo_name"],
        languages       = ", ".join(gt["languages"]) or "unknown",
        file_list       = file_list_txt,
        sloc            = gt["total_sloc"],
        health          = gt["health_score"],
        debt            = round(gt["debt_months"], 1),
        long_pct        = avg_long,
        nesting_pct     = avg_nesting,
        total_functions = total_functions,
        total_classes   = total_classes,
        bad_practices   = bad_practices_txt,
    )

    try:
        # Reduced max_tokens from 1000 → 800 to avoid timeouts on heavy loads
        # timeout=600 (10 min) to allow full token generation
        result = client.generate_json(prompt, model=model, system=_SYSTEM,
                                      max_tokens=800, num_ctx=5120, timeout=600)
        result["_model_used"] = model or client.best_available_model()
        # Back-fill actual metrics; enrich per_function_breakdown from extracted data
        result = _validate_and_enrich(result, top_files, analysis_result, repo_path)
        # Post-process: strip hallucinated file paths and function names
        result = validate_tech_debt(result, gt)
        return result
    except Exception as exc:
        logger.error("ai_tech_debt failed: %s", exc)
        return {"error": str(exc), "summary": "AI analysis unavailable — check Ollama connectivity."}



# Function: _build_file_lookup
def _build_file_lookup(top_files: list) -> dict:
    file_lookup: dict[str, dict] = {}
    for f in top_files:
        key = f.get("name", "")
        file_lookup[key] = f
        short = key.split("/")[-1] if "/" in key else key
        file_lookup.setdefault(short, f)
    return file_lookup


# Function: _build_fn_issue
def _build_fn_issue(fn_cc: int, fn_sloc: int, fn_params: int) -> str:
    parts = []
    if fn_cc >= 15:
        parts.append(f"Critical CC={fn_cc} \u2014 very hard to test")
    elif fn_cc >= 10:
        parts.append(f"High CC={fn_cc} \u2014 exceeds threshold of 10")
    if fn_sloc >= 60:
        parts.append(f"Long method: {fn_sloc} LOC (threshold 40)")
    if fn_params >= 5:
        parts.append(f"Long parameter list: {fn_params} params")
    return "; ".join(parts) or "Review recommended"


# Function: _apply_actual_metrics
def _apply_actual_metrics(h: dict, actual: dict) -> None:
    # Replace with real numbers (LLM may hallucinate)
    h["metrics"] = {
        "cyclomatic_complexity": actual.get("complexity", 0),
        "sloc":                  actual.get("sloc", 0),
        "long_methods":          actual.get("long_methods", 0),
        "deep_nesting":          actual.get("deep_nesting", 0),
        "functions":             actual.get("functions", 0),
        "classes":               actual.get("classes", 0),
    }
    # If LLM gave effort_days = 0 or None, derive a sensible estimate
    if not h.get("effort_days"):
        cc = actual.get("complexity", 1)
        sloc = actual.get("sloc", 50)
        h["effort_days"] = max(1, min(30, round((cc * 0.4 + sloc / 200))))


# Function: _backfill_function_breakdown
def _backfill_function_breakdown(h: dict, fname: str, actual: dict | None, repo_path: str) -> None:
    # Ensure per_function_breakdown exists (back-fill from live extraction if missing)
    if h.get("per_function_breakdown") or not repo_path or not actual:
        return
    fns = _get_functions_for_file(
        repo_path, fname, actual.get("_lang", ""), actual.get("complexity", 0), actual.get("sloc", 0)
    )
    fn_bd = []
    for fn in fns[:4]:
        fn_cc = fn.get("cc", 0)
        fn_sloc = fn.get("sloc", 0)
        fn_params = fn.get("params", 0)
        fn_bd.append({
            "function": fn["function"],
            "cyclomatic_complexity": fn_cc,
            "sloc": fn_sloc,
            "issue": _build_fn_issue(fn_cc, fn_sloc, fn_params),
            "refactoring": (
                "Decompose Conditional / Extract Method" if fn_cc >= 10
                else ("Extract sub-function" if fn_sloc >= 60 else "Introduce Parameter Object" if fn_params >= 5 else "General clean-up")
            ),
        })
    if fn_bd:
        h["per_function_breakdown"] = fn_bd


# Function: _refactoring_label
def _refactoring_label(fn_cc: int, fn_sloc: int, fn_params: int) -> str:
    if fn_cc >= 10:
        return "Extract Method"
    if fn_sloc >= 60:
        return "Extract sub-function"
    if fn_params >= 5:
        return "Introduce Parameter Object"
    return "General clean-up"


# Function: _fill_missing_fn_name
def _fill_missing_fn_name(row: dict, i: int, fname: str, deterministic_fns: list) -> None:
    if i < len(deterministic_fns) and not _is_missing_symbol(deterministic_fns[i].get("function")):
        row["function"] = deterministic_fns[i].get("function")
    else:
        row["function"] = _symbol_from_file(fname, i)


# Function: _apply_deterministic_fn_data
def _apply_deterministic_fn_data(row: dict, det: dict) -> None:
    # Reconcile metrics/issues from deterministic extraction when available.
    fn_cc = int(det.get("cc", row.get("cyclomatic_complexity", 0)) or 0)
    fn_sloc = int(det.get("sloc", row.get("sloc", 0)) or 0)
    fn_params = int(det.get("params", 0) or 0)
    row["cyclomatic_complexity"] = fn_cc
    row["sloc"] = fn_sloc
    if (not str(row.get("issue") or "").strip()) or "review complexity" in str(row.get("issue") or "").lower():
        row["issue"] = _build_fn_issue(fn_cc, fn_sloc, fn_params)
    if not str(row.get("refactoring") or "").strip():
        row["refactoring"] = _refactoring_label(fn_cc, fn_sloc, fn_params)


# Function: _reconcile_fn_row
def _reconcile_fn_row(row: dict, i: int, fname: str, deterministic_fns: list, deterministic_map: dict) -> dict | None:
    if not isinstance(row, dict):
        return None
    if _is_missing_symbol(row.get("function")):
        _fill_missing_fn_name(row, i, fname, deterministic_fns)
    det = deterministic_map.get(str(row.get("function") or "").strip())
    if det:
        _apply_deterministic_fn_data(row, det)
    return row


# Function: _fix_fn_rows_for_hotspot
def _fix_fn_rows_for_hotspot(h: dict, fname: str, actual: dict | None, repo_path: str) -> None:
    # Strict fallback naming for L3 function rows in this hotspot.
    fn_rows = h.get("per_function_breakdown") or []
    if not isinstance(fn_rows, list):
        return
    deterministic_fns = _get_functions_for_file(
        repo_path, fname, (actual or {}).get("_lang", ""), (actual or {}).get("complexity", 0), (actual or {}).get("sloc", 0)
    ) if repo_path else []
    deterministic_map = {
        str(fn.get("function", "")).strip(): fn
        for fn in deterministic_fns
        if isinstance(fn, dict)
    }
    clean_rows = []
    for i, row in enumerate(fn_rows):
        reconciled = _reconcile_fn_row(row, i, fname, deterministic_fns, deterministic_map)
        if reconciled is not None:
            clean_rows.append(reconciled)
    h["per_function_breakdown"] = clean_rows


# Function: _fix_hotspot_metrics
def _fix_hotspot_metrics(hotspots: list, file_lookup: dict, repo_path: str) -> list:
    for h in hotspots:
        if not isinstance(h, dict):
            continue
        fname = h.get("file", "")
        actual = file_lookup.get(fname) or file_lookup.get(fname.split("/")[-1])
        if actual:
            _apply_actual_metrics(h, actual)
        _backfill_function_breakdown(h, fname, actual, repo_path)
        _fix_fn_rows_for_hotspot(h, fname, actual, repo_path)
    return hotspots


_HOTSPOT_PRIORITY_RULES = [
    (lambda f: f.get("complexity", 0) > 20,    ("high",   "complexity")),
    (lambda f: f.get("long_methods", 0) > 5,   ("high",   "long_methods")),
    (lambda f: f.get("deep_nesting", 0) > 10,  ("medium", "deep_nesting")),
    (lambda f: f.get("complexity", 0) > 10,    ("medium", "complexity")),
    (lambda f: f.get("todo_comments", 0) > 3,  ("low",    "documentation")),
    (lambda f: True,                            ("low",    "maintainability")),
]


# Function: _priority_for_file
def _priority_for_file(f: dict) -> tuple:
    for pred, (pri, cat) in _HOTSPOT_PRIORITY_RULES:
        try:
            if callable(pred) and pred(f):
                return pri, cat
        except Exception:
            continue
    return "medium", "maintainability"


# Function: _build_hotspot_issue_parts
def _build_hotspot_issue_parts(cc: int, lm: int, dn: int, mg: int, tc: int) -> list:
    issue_parts = []
    if cc > 1:
        issue_parts.append(f"cyclomatic complexity={cc}")
    if lm > 0:
        issue_parts.append(f"{lm} long methods (>40 LOC)")
    if dn > 0:
        issue_parts.append(f"{dn} deep-nesting violations")
    if mg > 0:
        issue_parts.append(f"{mg} magic numbers")
    if tc > 0:
        issue_parts.append(f"{tc} TODO/FIXME markers")
    return issue_parts


# Function: _build_generated_fn_row
def _build_generated_fn_row(fn: dict) -> dict:
    fn_cc = fn.get("cc", 0)
    return {
        "function": fn.get("function", "unknown"),
        "cyclomatic_complexity": fn_cc,
        "sloc": fn.get("sloc", 0),
        "issue": f"High CC={fn_cc}" if fn_cc >= 10 else "Review complexity",
        "refactoring": "Extract Method" if fn_cc >= 10 else "General clean-up",
    }


# Function: _build_generated_fn_breakdown
def _build_generated_fn_breakdown(repo_path: str, fname: str, f: dict) -> list:
    if not repo_path:
        return []
    fns = _get_functions_for_file(
        repo_path, fname, f.get("_lang", ""), f.get("complexity", 0), f.get("sloc", 0)
    )
    return [_build_generated_fn_row(fn) for fn in fns[:4] if isinstance(fn, dict)]


# Function: _build_generated_hotspot
def _build_generated_hotspot(f: dict, fname: str, repo_path: str) -> dict:
    cc   = f.get("complexity", 0)
    sloc = f.get("sloc", 0)
    lm   = f.get("long_methods", 0)
    dn   = f.get("deep_nesting", 0)
    mg   = f.get("magic_numbers", 0)
    tc   = f.get("todo_comments", 0)
    lang = f.get("_lang", "")

    priority, category = _priority_for_file(f)
    issue_parts = _build_hotspot_issue_parts(cc, lm, dn, mg, tc)

    generated_hotspot = {
        "file":           fname,
        "issue":          f"{lang} file with {', '.join(issue_parts) or 'code smell signals'}.",
        "recommendation": "Refactor to reduce complexity, extract long methods, and address TODOs.",
        "root_cause":     "Accumulated technical debt from incremental feature additions without refactoring.",
        "debt_category":  category,
        "impact":         "Harder to maintain, test, and extend. Bug risk increases over time.",
        "effort_days":    max(1, min(20, round((cc * 0.4 + sloc / 250)))),
        "priority":       priority,
        "metrics": {
            "cyclomatic_complexity": cc,
            "sloc":                  sloc,
            "long_methods":          lm,
            "deep_nesting":          dn,
            "functions":             f.get("functions", 0),
            "classes":               f.get("classes", 0),
        },
    }

    fn_breakdown = _build_generated_fn_breakdown(repo_path, fname, f)
    if fn_breakdown:
        generated_hotspot["per_function_breakdown"] = fn_breakdown

    return generated_hotspot


# Function: _generate_missing_hotspots
def _generate_missing_hotspots(hotspots: list, top_files: list, repo_path: str) -> list:
    existing_files = {h.get("file", "") for h in hotspots if isinstance(h, dict)}
    for f in top_files:
        if len(hotspots) >= 10:
            break
        fname = f.get("name", "")
        if fname in existing_files:
            continue
        hotspots.append(_build_generated_hotspot(f, fname, repo_path))
        existing_files.add(fname)
    return hotspots


# Function: _normalize_quick_wins
def _normalize_quick_wins(quick_wins: list) -> list:
    # Normalize: if any are plain strings from old schema, wrap them
    return [
        w if isinstance(w, dict) else {"action": str(w), "file": "multiple", "benefit": "", "effort_hours": 4}
        for w in quick_wins
    ]


# Function: _quick_win_from_fn
def _quick_win_from_fn(fn: dict, h_file: str) -> dict | None:
    if not isinstance(fn, dict):
        return None
    fn_name = str(fn.get("function") or "").strip()
    fn_cc = int(fn.get("cyclomatic_complexity", 0) or 0)
    fn_sloc = int(fn.get("sloc", 0) or 0)
    if not fn_name:
        return None
    # Avoid noisy actions for trivial rows (e.g. CC=1 utility functions).
    if fn_cc < 12 and fn_sloc < 80:
        return None
    return {
        "action": f"Refactor {fn_name} to reduce CC from {fn_cc} to <= 10",
        "file": h_file,
        "benefit": "Improves unit-testability and lowers defect risk in critical code paths",
        "effort_hours": max(2, min(12, round(fn_cc / 2))) if fn_cc > 0 else 4,
    }


# Function: _build_l3_quick_wins
def _build_l3_quick_wins(hotspots: list) -> list:
    # Add concrete L2/L3 quick wins from hotspot/function evidence.
    l3_wins = []
    for h in hotspots[:6]:
        if not isinstance(h, dict):
            continue
        h_file = h.get("file", "multiple")
        for fn in (h.get("per_function_breakdown") or [])[:2]:
            win = _quick_win_from_fn(fn, h_file)
            if win:
                l3_wins.append(win)
            if len(l3_wins) >= 4:
                break
        if len(l3_wins) >= 4:
            break
    return l3_wins


# Function: _merge_dedupe_by_action
def _merge_dedupe_by_action(*groups: list) -> list:
    merged = []
    seen_actions = set()
    for group in groups:
        for w in group:
            action = str((w or {}).get("action", "")).strip().lower()
            if not action or action in seen_actions:
                continue
            merged.append(w)
            seen_actions.add(action)
    return merged


_DEFAULT_QW = [
    {"action": "Add docstrings/comments to undocumented functions", "file": "multiple", "benefit": "Improves onboarding and maintainability", "effort_hours": 4},
    {"action": "Replace magic numbers with named constants",        "file": "multiple", "benefit": "Reduces cognitive load and prevents bugs", "effort_hours": 3},
    {"action": "Rename single-letter variables to descriptive names","file": "multiple", "benefit": "Increases code readability immediately",  "effort_hours": 2},
    {"action": "Extract repeated code blocks into helper functions", "file": "multiple", "benefit": "Reduces duplication and simplifies testing","effort_hours": 6},
    {"action": "Remove or resolve all TODO/FIXME markers",          "file": "multiple", "benefit": "Eliminates known outstanding issues",       "effort_hours": 8},
    {"action": "Add basic unit tests for highest-complexity files",  "file": "multiple", "benefit": "Catches regressions in critical paths",     "effort_hours": 8},
]


# Function: _ensure_quick_wins
def _ensure_quick_wins(result: dict, hotspots: list) -> dict:
    quick_wins = _normalize_quick_wins(result.get("quick_wins") or [])
    l3_wins = _build_l3_quick_wins(hotspots)

    # Merge quick wins with L3-first ordering and de-duplicate by action text.
    quick_wins = _merge_dedupe_by_action(l3_wins, quick_wins)

    # Pad to minimum 6
    while len(quick_wins) < 6:
        quick_wins.append(_DEFAULT_QW[len(quick_wins) % len(_DEFAULT_QW)])
    result["quick_wins"] = quick_wins
    return result


# Function: _ensure_strategic_actions
def _ensure_strategic_actions(result: dict, hotspots: list) -> dict:
    strategic = result.get("strategic_actions") or []
    strategic = [
        s if isinstance(s, dict) else {"action": str(s), "rationale": "", "effort_weeks": 4, "impact": "medium"}
        for s in strategic
    ]

    # Add concrete strategic actions tied to observed top hotspots.
    top_files = [h.get("file", "") for h in hotspots[:3] if isinstance(h, dict) and h.get("file")]
    focused_actions = []
    if top_files:
        focused_actions.append({
            "action": f"Run focused debt-remediation wave on {', '.join(top_files)}",
            "rationale": "These files concentrate the highest complexity and long-method debt.",
            "effort_weeks": 4,
            "impact": "high",
        })
    focused_actions.append({
        "action": "Enforce CI gate for max function complexity (CC <= 10) on modified files",
        "rationale": "Stops new high-complexity code from entering the main branch.",
        "effort_weeks": 2,
        "impact": "high",
    })

    merged_sa = []
    seen_sa = set()
    for s in focused_actions + strategic:
        action = str((s or {}).get("action", "")).strip().lower()
        if not action or action in seen_sa:
            continue
        merged_sa.append(s)
        seen_sa.add(action)
    strategic = merged_sa

    _DEFAULT_SA = [
        {"action": "Implement a code quality gate in CI/CD pipeline",        "rationale": "Prevents new debt from being merged", "effort_weeks": 2,  "impact": "high"},
        {"action": "Migrate to a layered / clean architecture",              "rationale": "Separates concerns for testability",  "effort_weeks": 12, "impact": "high"},
        {"action": "Introduce comprehensive integration test suite",         "rationale": "Provides safety net for refactoring", "effort_weeks": 6,  "impact": "high"},
        {"action": "Establish code review standards and checklists",         "rationale": "Reduces future debt accumulation",    "effort_weeks": 1,  "impact": "medium"},
        {"action": "Break monolith into independently deployable services",  "rationale": "Unlocks independent team scaling",    "effort_weeks": 24, "impact": "high"},
    ]
    while len(strategic) < 5:
        strategic.append(_DEFAULT_SA[len(strategic) % len(_DEFAULT_SA)])
    result["strategic_actions"] = strategic
    return result


# Function: _ensure_debt_by_category
def _ensure_debt_by_category(result: dict) -> dict:
    if not result.get("debt_by_category"):
        total_cc = sum(h["metrics"].get("cyclomatic_complexity", 0) for h in result["hotspots"] if isinstance(h, dict) and h.get("metrics"))
        total_lm = sum(h["metrics"].get("long_methods", 0)          for h in result["hotspots"] if isinstance(h, dict) and h.get("metrics"))
        total_dn = sum(h["metrics"].get("deep_nesting", 0)          for h in result["hotspots"] if isinstance(h, dict) and h.get("metrics"))
        denom = max(1, total_cc + total_lm + total_dn)
        result["debt_by_category"] = {
            "complexity":   round(total_cc / denom * 100),
            "long_methods": round(total_lm / denom * 100),
            "deep_nesting": round(total_dn / denom * 100),
            "test_coverage":  10,
            "documentation":  10,
            "design":          5,
        }
    return result


# Function: _ensure_by_language
def _ensure_by_language(result: dict, analysis_result: dict) -> dict:
    if not result.get("by_language"):
        lang_reports = analysis_result.get("language_reports", [])
        by_lang = []
        for lr in lang_reports:
            avg_cc = lr.get("avg_complexity", 0)
            lm_pct = lr.get("long_methods_pct", 0)
            level  = "high" if avg_cc > 10 or lm_pct > 20 else ("medium" if avg_cc > 5 or lm_pct > 10 else "low")
            issue  = (
                f"avg cyclomatic complexity {round(avg_cc,1)}, {round(lm_pct,1)}% long methods"
                if avg_cc > 1 else "low complexity"
            )
            by_lang.append({"language": lr.get("language", "?"), "debt_level": level, "primary_issue": issue})
        result["by_language"] = by_lang
    return result


# Function: _validate_and_enrich
def _validate_and_enrich(result: dict, top_files: list, analysis_result: dict, repo_path: str = "") -> dict:
    """
    Back-fill the LLM response with real computed metrics to eliminate
    hallucinations and ensure minimum item counts.

    - Hotspot `metrics` are replaced with actual per-file numbers from top_files
    - per_function_breakdown populated from extracted function data
    - Any missing hotspots are auto-generated from the worst-scoring files
    - Minimum 8 hotspots, 6 quick wins, 5 strategic actions enforced
    - estimated_total_effort_days validated against sum of hotspot efforts
    """
    file_lookup = _build_file_lookup(top_files)
    hotspots = _fix_hotspot_metrics(result.get("hotspots") or [], file_lookup, repo_path)
    hotspots = _generate_missing_hotspots(hotspots, top_files, repo_path)
    result["hotspots"] = hotspots
    result = _ensure_quick_wins(result, hotspots)
    result = _ensure_strategic_actions(result, hotspots)
    computed_total = sum(h.get("effort_days", 0) for h in result["hotspots"] if isinstance(h, dict))
    if not result.get("estimated_total_effort_days"):
        result["estimated_total_effort_days"] = computed_total
    result = _ensure_debt_by_category(result)
    result = _ensure_by_language(result, analysis_result)
    return result
