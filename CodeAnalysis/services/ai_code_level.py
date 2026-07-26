# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: L2/L3 deep code-level analysis.
# Date: 2025-10-11
# ---------------------------------------------------------------------------
"""
services/ai_code_level.py
--------------------------
L2/L3 deep code-level analysis.

Goes beyond file-level metrics to produce:
  * Per-function complexity breakdown (named functions, CC, LOC, parameters)
  * Anti-pattern detection at class/function level
    (God Class, Feature Envy, Long Parameter List, Shotgun Surgery, etc.)
  * Coupling & cohesion assessment per module/class
  * Code smell catalog with file + function references
  * Naming convention violations
  * Cross-file dependency chains
  * Dead-code indicators
  * Specific refactoring recommendations at function granularity
"""
from __future__ import annotations

import logging
import os
import re
from pathlib import Path
from typing import Any

from .ollama_client import OllamaClient
from .ai_grounding import build_ground_truth, grounding_header, build_anti_hallucination_system_prompt

logger = logging.getLogger(__name__)

_SKIP_DIRS = {
    ".git", ".venv", "venv", "env", "node_modules", "__pycache__",
    "dist", "build", "target", "vendor", ".tox", ".mypy_cache",
}

_SOURCE_EXTS = {
    ".py", ".java", ".cs", ".js", ".ts", ".jsx", ".tsx",
    ".kt", ".go", ".rb", ".php", ".scala", ".rs",
}

# Anti-pattern definitions: (id, display_name, regex_pattern, description)
_ANTI_PATTERNS = [
    ("god_class",      "God Class",            r"class\s+\w+[^{]*\{[^}]{3000,}",   "Excessively large class"),
    ("long_param",     "Long Parameter List",   r"def\s+\w+\s*\([^)]{80,}\)",        "Function with many parameters"),
    ("magic_num",      "Magic Numbers",         r"(?<!\w)(?<!\.)\d{2,}(?!\w)(?!\.)", "Hard-coded numeric literals"),
    ("dead_assign",    "Dead Assignment",       r"\b(\w+)\s*=\s*.+\n(?!.*\1)",       "Variable assigned but never used"),
    ("nested_cond",    "Deep Nesting",          r"if[^\n]*:\n(?:\s{4,8}[^\n]*\n){0,3}\s{8,}if[^\n]*:\n(?:\s{12,}[^\n]*\n){0,3}\s{12,}if", "Triple-nested conditionals"),
    ("print_debug",    "Debug Print",           r"\bprint\s*\(",                     "Debug print statement"),
    ("empty_except",   "Empty Exception",       r"except[^:]*:\s*\n\s*pass",         "Silently swallowed exception"),
    ("todo_fixme",     "TODO/FIXME",            r"#\s*(?:TODO|FIXME|HACK|XXX)\b",    "Unresolved technical debt marker"),
    ("hardcoded_url",  "Hardcoded URL",         r"https?://[a-zA-Z0-9./_-]{10,}",   "Hard-coded URL or endpoint"),
    ("mutable_default","Mutable Default Arg",   r"def\s+\w+\s*\([^)]*=\s*[\[{]",    "Mutable default argument"),
]

# Pre-compile anti-pattern regexes once at import time
_COMPILED_ANTI_PATTERNS = [(ap[0], re.compile(ap[2], re.MULTILINE)) for ap in _ANTI_PATTERNS]

_SYSTEM_BASE = """\
You are a senior code reviewer with deep expertise in code quality, design patterns,
and refactoring. Given function-level metrics and code samples you identify specific
L2/L3 code quality issues at the function and class level, named precisely.
You MUST only reference function names, class names, and file paths that appear in the data.
Do NOT invent function names or file paths not present in the provided function table.
Be concise. Limit ALL string values to 1 sentence. Return valid JSON and nothing else."""

_PROMPT_TMPL = """\
Perform a deep L2/L3 code-level analysis for repository "{repo_name}".

LANGUAGES: {languages}
TOTAL SLOC: {sloc}

PER-FUNCTION METRICS (top {n_functions} most complex functions):
{function_table}

ANTI-PATTERNS DETECTED BY STATIC SCAN (file → occurrence count):
{anti_pattern_hits}

CLASS-LEVEL SIGNALS:
{class_signals}

IMPORTS AND COUPLING SIGNALS (files with most external imports):
{coupling_signals}

Produce a comprehensive L2/L3 code-level analysis JSON:
{{
  "summary": "<3-4 sentences naming the worst functions, classes, and patterns>",
  "per_function_issues": [
    {{
      "function": "<exact function/method name>",
      "file": "<relative file path>",
      "class": "<enclosing class name or null>",
      "language": "<language>",
      "cyclomatic_complexity": <integer>,
      "sloc": <integer>,
      "parameter_count": <integer>,
      "issues": ["<specific issue with detail — e.g. 'CC=18 exceeds threshold of 10'>"],
      "anti_patterns": ["<anti-pattern names present in this function>"],
      "refactoring_action": "<specific refactoring: Extract Method, Decompose Conditional, Replace Magic Number, etc.>",
      "renamed_to": "<suggested rename if naming is poor, else null>",
      "priority": "high|medium|low",
      "estimated_effort_hours": <integer>
    }}
  ],
  "class_analysis": [
    {{
      "class": "<exact class name>",
      "file": "<relative file path>",
      "language": "<language>",
      "method_count": <integer>,
      "sloc": <integer>,
      "anti_patterns": ["<God Class|Data Class|Feature Envy|Inappropriate Intimacy|etc.>"],
      "responsibilities": ["<single responsibility the class seems to handle>"],
      "coupling_score": "high|medium|low",
      "cohesion_score": "high|medium|low",
      "recommendation": "<concrete restructuring advice — e.g. 'Split into UserValidator + UserRepository'>",
      "effort_days": <integer>
    }}
  ],
  "anti_pattern_catalog": [
    {{
      "pattern": "<anti-pattern name>",
      "category": "complexity|coupling|naming|error-handling|security|maintainability|performance",
      "occurrences": <integer>,
      "affected_files": ["<file path>"],
      "worst_offender": "<function or class name with highest occurrence>",
      "remediation": "<specific fix action>",
      "severity": "critical|high|medium|low"
    }}
  ],
  "coupling_analysis": {{
    "tightly_coupled_pairs": [
      {{
        "module_a": "<file or class A>",
        "module_b": "<file or class B>",
        "coupling_type": "content|common|control|stamp|data|message",
        "decoupling_approach": "<interface, event, DI, etc.>"
      }}
    ]
  }},
  "naming_violations": [
    {{
      "name": "<actual identifier name>",
      "file": "<file path>",
      "type": "function|class|variable|constant",
      "suggested_name": "<better name>"
    }}
  ],
  "l3_refactoring_plan": [
    {{
      "step": <integer>,
      "title": "<refactoring name>",
      "target": "<specific function/class to refactor>",
      "file": "<file path>",
      "technique": "<Extract Method|Move Method|Replace Conditional with Polymorphism|etc.>",
      "effort_hours": <integer>,
      "risk": "low|medium|high"
    }}
  ],
  "quality_gates_recommended": [
    {{
      "gate": "<CI/CD quality gate name>",
      "metric": "<metric to enforce>",
      "threshold": "<threshold value>",
      "enforcement": "block|warn"
    }}
  ],
  "code_smell_score": <integer 0-100 — 100 = no smells>,
  "maintainability_index": <integer 0-100>
}}

Provide:
- Top 6-8 per_function_issues (worst functions by complexity/issues)
- Top 3-4 class_analysis entries
- 4-5 anti_pattern_catalog entries
- 2-3 coupling pairs
- Top 3 naming_violations
- 4-5 steps in l3_refactoring_plan
- 3-4 quality_gates_recommended

Return ONLY the JSON."""


# Function: _find_file_on_disk
def _find_file_on_disk(root: Path, fname: str) -> Path | None:
    fpath = root / fname if not Path(fname).is_absolute() else Path(fname)
    if fpath.exists():
        return fpath
    target_name = Path(fname).name
    for wdirpath, wdirnames, wfilenames in os.walk(str(root)):
        wdirnames[:] = [d for d in wdirnames if d not in _SKIP_DIRS]
        if target_name in wfilenames:
            return Path(wdirpath) / target_name
    return None


# Function: _extract_functions_from_file
def _extract_functions_from_file(root: Path, finfo: dict) -> list[dict]:
    fname = finfo.get("name", "")
    fpath = _find_file_on_disk(root, fname)
    if not fpath or not fpath.exists():
        return []

    lang = finfo.get("_lang", _detect_lang(fpath))
    rel  = str(fpath.relative_to(root)) if root in fpath.parents or fpath.parent == root else fname

    try:
        source = fpath.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return []

    file_cc   = finfo.get("complexity", 1)
    file_sloc = finfo.get("sloc", 0)

    # Python: use radon for per-function CC
    if lang == "Python":
        return _extract_python_functions(source, rel, file_cc)
    return _extract_generic_functions(source, rel, lang, file_cc, file_sloc)


# Function: _extract_function_data
def _extract_function_data(repo_path: str, top_files: list[dict], max_functions: int = 20) -> list[dict]:
    """
    Extract per-function metrics from the top-debt files.
    Uses radon for Python, regex patterns for other languages.
    Returns list of {function, file, class, language, sloc, parameter_count, cc, issues}.
    """
    if not repo_path:
        return []
    root = Path(repo_path)
    if not root.exists():
        return []

    functions: list[dict] = []
    seen_files: set[str] = set()

    # Limit to top-debt files
    for finfo in top_files[:25]:
        if len(functions) >= max_functions:
            break
        fname = finfo.get("name", "")
        if fname in seen_files:
            continue
        seen_files.add(fname)
        functions.extend(_extract_functions_from_file(root, finfo))

    return functions[:max_functions]


# Function: _detect_lang
def _detect_lang(path: Path) -> str:
    ext_map = {
        ".py": "Python", ".java": "Java", ".cs": "C#", ".js": "JavaScript",
        ".ts": "TypeScript", ".jsx": "JavaScript", ".tsx": "TypeScript",
        ".kt": "Kotlin", ".go": "Go", ".rb": "Ruby", ".php": "PHP",
        ".scala": "Scala", ".rs": "Rust",
    }
    return ext_map.get(path.suffix.lower(), "Unknown")


# Function: _extract_python_functions
def _extract_python_functions(source: str, rel_path: str, file_cc: int) -> list[dict]:
    """Extract per-function data from Python source using radon + AST."""
    fns: list[dict] = []
    try:
        from radon.complexity import cc_visit  # type: ignore
        blocks = cc_visit(source)
        for b in sorted(blocks, key=lambda x: x.complexity, reverse=True)[:8]:
            params = _count_python_params(source, b.name)
            fns.append({
                "function":   b.name,
                "file":       rel_path,
                "class":      b.classname if hasattr(b, "classname") else None,
                "language":   "Python",
                "cc":         b.complexity,
                "sloc":       getattr(b, "endline", 0) - getattr(b, "lineno", 0),
                "parameter_count": params,
            })
    except Exception:
        # Fallback: regex extraction
        for m in re.finditer(r"^\s*(?:async\s+)?def\s+(\w+)\s*\(([^)]*)\)", source, re.MULTILINE):
            params = len([p.strip() for p in m.group(2).split(",") if p.strip() and p.strip() != "self" and p.strip() != "cls"])
            fns.append({
                "function":   m.group(1),
                "file":       rel_path,
                "class":      None,
                "language":   "Python",
                "cc":         file_cc,
                "sloc":       30,
                "parameter_count": params,
            })
            if len(fns) >= 6:
                break
    return fns


# Function: _count_python_params
def _count_python_params(source: str, func_name: str) -> int:
    """Count non-self/cls parameters of a named Python function."""
    m = re.search(rf"def\s+{re.escape(func_name)}\s*\(([^)]*)\)", source)
    if not m:
        return 0
    raw = m.group(1)
    params = [p.strip().split(":")[0].strip().split("=")[0].strip()
              for p in raw.split(",") if p.strip()]
    return sum(1 for p in params if p not in ("self", "cls", "*", "**", ""))


# Function: _match_to_fn_dict
def _match_to_fn_dict(m: "re.Match", rel_path: str, lang: str, file_cc: int, file_sloc: int) -> dict | None:
    grps = [g for g in m.groups() if g]
    if not grps:
        return None
    func_name = grps[0]
    if func_name in {"if", "for", "while", "switch", "catch", "return"}:
        return None
    param_str = grps[1] if len(grps) > 1 else ""
    params    = len([p for p in param_str.split(",") if p.strip()])
    return {
        "function":        func_name,
        "file":            rel_path,
        "class":           None,
        "language":        lang,
        "cc":              file_cc,
        "sloc":            file_sloc // max(1, 5),
        "parameter_count": params,
    }


# Function: _extract_generic_functions
def _extract_generic_functions(source: str, rel_path: str, lang: str, file_cc: int, file_sloc: int) -> list[dict]:
    """Extract function signatures via regex for non-Python languages."""
    patterns = [
        # Java/Kotlin/C# — public/private method declarations
        r"(?:public|private|protected|static|override|async)\s+(?:\w+[\[\]<>?]*\s+)?(\w+)\s*\(([^)]*)\)\s*(?:throws\s+\w+\s*)?[{:]",
        # Go functions
        r"^func\s+(?:\(\w+\s+\*?\w+\)\s+)?(\w+)\s*\(([^)]*)\)",
        # JavaScript/TypeScript
        r"(?:function\s+(\w+)\s*\(([^)]*)\)|(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?(?:function\s*)?\(([^)]*)\)\s*(?:=>)?)",
        # Ruby
        r"^\s*def\s+(\w+)(?:\(([^)]*)\))?",
    ]
    fns: list[dict] = []
    for pat in patterns:
        for m in re.finditer(pat, source, re.MULTILINE):
            fn = _match_to_fn_dict(m, rel_path, lang, file_cc, file_sloc)
            if fn:
                fns.append(fn)
            if len(fns) >= 8:
                break
        if fns:
            break
    return fns


# Function: _safe_rel_path
def _safe_rel_path(fpath: Path, root: Path) -> str:
    try:
        return str(fpath.relative_to(root))
    except ValueError:
        return fpath.name


# Function: _read_source_safe
def _read_source_safe(fpath: Path) -> str | None:
    try:
        return fpath.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return None


# Function: _count_anti_pattern_hits
def _count_anti_pattern_hits(source: str, compiled: list, rel: str, results: dict[str, dict[str, int]]) -> None:
    for ap_id, pat in compiled:
        count = len(pat.findall(source))
        if count > 0:
            results[ap_id][rel] = results[ap_id].get(rel, 0) + count


# Function: _scan_dir_for_anti_patterns
def _scan_dir_for_anti_patterns(
    dir_path: Path, filenames: list, root: Path, target_names: set,
    compiled: list, results: dict[str, dict[str, int]], scanned: int,
) -> int:
    for fname in filenames:
        if scanned >= 50:
            break
        fpath = dir_path / fname
        if fpath.suffix.lower() not in _SOURCE_EXTS:
            continue
        rel = _safe_rel_path(fpath, root)
        # Always scan top-debt files, sample other files
        if rel not in target_names and scanned > 20:
            continue
        source = _read_source_safe(fpath)
        if source is None:
            continue
        scanned += 1
        _count_anti_pattern_hits(source, compiled, rel, results)
    return scanned


# Function: _scan_anti_patterns
def _scan_anti_patterns(repo_path: str, top_files: list[dict]) -> dict[str, dict[str, int]]:
    """
    Scan source files for anti-pattern occurrences.
    Returns {pattern_id: {file_path: count}}.
    """
    results: dict[str, dict[str, int]] = {ap[0]: {} for ap in _ANTI_PATTERNS}
    if not repo_path:
        return results
    root = Path(repo_path)
    if not root.exists():
        return results

    # Use module-level pre-compiled patterns (no per-call re.compile overhead)
    compiled = _COMPILED_ANTI_PATTERNS

    # Scan to-debt files + a few others
    target_names = {finfo.get("name", "") for finfo in top_files[:20]}
    scanned = 0
    for dirpath, dirnames, filenames in os.walk(str(root)):
        dirnames[:] = [d for d in dirnames if d not in _SKIP_DIRS]
        if scanned >= 50:
            break
        dir_path = Path(dirpath)
        scanned = _scan_dir_for_anti_patterns(dir_path, filenames, root, target_names, compiled, results, scanned)

    return results


# Function: _extract_class_signals_from_source
def _extract_class_signals_from_source(source: str, rel: str, class_pat: "re.Pattern", method_pat: "re.Pattern") -> list[dict]:
    rows: list[dict] = []
    for cm in class_pat.finditer(source):
        class_name   = cm.group(1)
        start        = cm.start()
        segment      = source[start: start + 6000]  # scan next 6000 chars
        method_count = len(method_pat.findall(segment))
        approx_sloc  = segment.count("\n")
        rows.append({
            "class":        class_name,
            "file":         rel,
            "method_count": method_count,
            "approx_sloc":  approx_sloc,
        })
    return rows


# Function: _scan_dir_for_class_signals
def _scan_dir_for_class_signals(
    dir_path: Path, filenames: list, root: Path, top_names: set,
    class_pat: "re.Pattern", method_pat: "re.Pattern", signals: list[dict],
) -> None:
    for fname in filenames:
        fpath = dir_path / fname
        if not fpath.is_file() or fpath.suffix.lower() not in _SOURCE_EXTS:
            continue
        rel = _safe_rel_path(fpath, root)
        if rel not in top_names:
            continue
        source = _read_source_safe(fpath)
        if source is None:
            continue
        signals.extend(_extract_class_signals_from_source(source, rel, class_pat, method_pat))
        if len(signals) >= 20:
            break


# Function: _scan_class_signals
def _scan_class_signals(repo_path: str, top_files: list[dict]) -> list[dict]:
    """
    Detect class-level signals: method count, LOC per class — God Class indicators.
    Returns list of {class_name, file, method_count, approx_sloc}.
    """
    signals: list[dict] = []
    if not repo_path:
        return signals
    root = Path(repo_path)
    if not root.exists():
        return signals

    class_pat  = re.compile(r"^class\s+(\w+)[\s:(]", re.MULTILINE)
    method_pat = re.compile(r"^\s{4,}(?:def\s+\w+|public\s+\w+\s+\w+\s*\(|function\s+\w+)", re.MULTILINE)

    top_names = {finfo.get("name", "") for finfo in top_files[:15]}

    for dirpath, dirnames, filenames in os.walk(str(root)):
        dirnames[:] = [d for d in dirnames if d not in _SKIP_DIRS]
        dir_path = Path(dirpath)
        _scan_dir_for_class_signals(dir_path, filenames, root, top_names, class_pat, method_pat, signals)
        if len(signals) >= 20:
            break

    return signals


# Function: _collect_imports
def _collect_imports(source: str, import_pats: list) -> set:
    imports: set[str] = set()
    for pat in import_pats:
        for m in pat.finditer(source):
            imports.add(m.group(1).strip())
    return imports


# Function: _scan_dir_for_coupling
def _scan_dir_for_coupling(dir_path: Path, filenames: list, root: Path, top_names: set, import_pats: list, coupling: list) -> None:
    for fname in filenames:
        fpath = dir_path / fname
        if not fpath.is_file() or fpath.suffix.lower() not in _SOURCE_EXTS:
            continue
        rel = _safe_rel_path(fpath, root)
        if rel not in top_names:
            continue
        source = _read_source_safe(fpath)
        if source is None:
            continue
        imports = _collect_imports(source, import_pats)
        if imports:
            coupling.append({
                "file":             rel,
                "import_count":     len(imports),
                "imported_modules": sorted(imports)[:15],
            })


# Function: _scan_coupling
def _scan_coupling(repo_path: str, top_files: list[dict]) -> list[dict]:
    """
    Detect high fan-out files (many imports = tight coupling indicator).
    Returns list of {file, import_count, imported_modules}.
    """
    coupling: list[dict] = []
    if not repo_path:
        return coupling
    root = Path(repo_path)
    if not root.exists():
        return coupling

    import_pats = [
        re.compile(r"^import\s+([\w.]+)", re.MULTILINE),
        re.compile(r"^from\s+([\w.]+)\s+import", re.MULTILINE),
        re.compile(r"^require\s*\(?['\"]([^'\"]+)['\"]", re.MULTILINE),
        re.compile(r"^using\s+([\w.]+);", re.MULTILINE),
    ]
    top_names = {finfo.get("name", "") for finfo in top_files[:20]}

    for dirpath, dirnames, filenames in os.walk(str(root)):
        dirnames[:] = [d for d in dirnames if d not in _SKIP_DIRS]
        dir_path = Path(dirpath)
        _scan_dir_for_coupling(dir_path, filenames, root, top_names, import_pats, coupling)
    coupling.sort(key=lambda x: x["import_count"], reverse=True)
    return coupling[:10]


# Function: _format_function_table
def _format_function_table(functions: list[dict]) -> str:
    """Format function data as a readable table for the LLM prompt."""
    if not functions:
        return "  (no function-level data available)"
    lines = []
    for f in functions:
        issues_hints = []
        cc = f.get("cc", 0)
        if cc >= 15:
            issues_hints.append(f"CC={cc} CRITICAL")
        elif cc >= 10:
            issues_hints.append(f"CC={cc} HIGH")
        elif cc > 5:
            issues_hints.append(f"CC={cc}")
        params = f.get("parameter_count", 0)
        if params >= 5:
            issues_hints.append(f"{params} params")
        sloc = f.get("sloc", 0)
        if sloc >= 60:
            issues_hints.append(f"LOC={sloc} LONG")
        cls_str = f"[{f['class']}::" if f.get("class") else "["
        lines.append(
            f"  {cls_str}{f['function']}]  ({f['language']}, {f['file']})  "
            f"CC={cc}, LOC={sloc}, params={params}  →  {', '.join(issues_hints) or 'OK'}"
        )
    return "\n".join(lines)


# Function: _format_anti_patterns
def _format_anti_patterns(hits: dict[str, dict[str, int]]) -> str:
    """Format anti-pattern hits for the LLM prompt."""
    lines = []
    for ap in _ANTI_PATTERNS:
        ap_id, name = ap[0], ap[1]
        file_hits = hits.get(ap_id, {})
        if not file_hits:
            continue
        total = sum(file_hits.values())
        worst_file = max(file_hits, key=file_hits.get)
        lines.append(
            f"  [{name}] total={total}  worst: {worst_file} ({file_hits[worst_file]}x)"
        )
    return "\n".join(lines) or "  (no anti-patterns detected by static scan)"


# Function: _format_class_signals
def _format_class_signals(signals: list[dict]) -> str:
    if not signals:
        return "  (no class data)"
    lines = []
    for s in sorted(signals, key=lambda x: x.get("method_count", 0), reverse=True)[:10]:
        flag = " ← GOD CLASS CANDIDATE" if s.get("method_count", 0) > 15 else ""
        lines.append(
            f"  {s['class']} ({s['file']}) — {s['method_count']} methods, ~{s['approx_sloc']} LOC{flag}"
        )
    return "\n".join(lines)


# Function: _format_coupling
def _format_coupling(coupling: list[dict]) -> str:
    if not coupling:
        return "  (no coupling data)"
    lines = []
    for c in coupling[:8]:
        mods = ", ".join(c["imported_modules"][:6])
        lines.append(
            f"  {c['file']} — {c['import_count']} imports  ({mods}{'…' if len(c['imported_modules']) > 6 else ''})"
        )
    return "\n".join(lines)


# Function: _collect_top_files
def _collect_top_files(analysis_result: dict) -> list[dict]:
    all_files: list[dict] = []
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
    return all_files[:10]


# Function: analyse_code_level
def analyse_code_level(
    analysis_result: dict,
    repo_path: str,
    model: str | None = None,
    client: OllamaClient | None = None,
    max_functions: int = 20,
) -> dict:
    """
    Perform L2/L3 deep code-level analysis.

    Parameters
    ----------
    analysis_result : dict
        Serialised AnalysisResult from the regular pipeline.
    repo_path : str
        Absolute path to the local repository.
    model : str | None
        Ollama model id. None = auto-select.
    client : OllamaClient | None
        Pre-built client (for DI / testing).
    max_functions : int
        Maximum functions to include in the prompt.

    Returns
    -------
    dict – L2/L3 code-level analysis report
    """
    client = client or OllamaClient()

    # ── Ground truth ──────────────────────────────────────────────────
    gt = build_ground_truth(analysis_result)
    _SYSTEM = build_anti_hallucination_system_prompt(_SYSTEM_BASE, gt)

    top_files = _collect_top_files(analysis_result)

    # ── Extract function-level data ───────────────────────────────────────────
    functions = _extract_function_data(repo_path, top_files, max_functions)

    # ── Anti-pattern scan ─────────────────────────────────────────────────────
    anti_hits = _scan_anti_patterns(repo_path, top_files)

    # ── Class-level signals ───────────────────────────────────────────────────
    class_signals = _scan_class_signals(repo_path, top_files)

    # ── Coupling analysis ─────────────────────────────────────────────────────
    coupling = _scan_coupling(repo_path, top_files)

    # ── Build prompt ──────────────────────────────────────────────────────────
    ground_block = grounding_header(gt)

    prompt = ground_block + "\n\n" + _PROMPT_TMPL.format(
        repo_name       = gt["repo_name"],
        languages       = ", ".join(gt["languages"]),
        sloc            = gt["total_sloc"],
        n_functions     = len(functions),
        function_table  = _format_function_table(functions),
        anti_pattern_hits= _format_anti_patterns(anti_hits),
        class_signals   = _format_class_signals(class_signals),
        coupling_signals = _format_coupling(coupling),
    )

    try:
        result = client.generate_json(
            prompt, model=model, system=_SYSTEM,
            max_tokens=700, num_ctx=5120,
            timeout=540,
        )
        result["_model_used"] = model or client.best_available_model()
        # Back-fill computed data so numbers are always accurate
        result = _enrich_result(result, functions, anti_hits, class_signals, coupling, analysis_result)
        return result
    except Exception as exc:
        logger.error("ai_code_level failed: %s", exc)
        return {
            "error": str(exc),
            "summary": "Code-level analysis unavailable — check Ollama connectivity.",
        }


# Function: _clean_name
def _clean_name(v: Any) -> str:
    s = str(v or "").strip()
    if not s or s in {"-", "--", "---", "_", "?", "unknown", "Unknown", "N/A", "n/a"}:
        return ""
    return s


# Function: _class_from_file
def _class_from_file(classes_by_file: dict, file_name: str, idx: int) -> str:
    cands = classes_by_file.get(str(file_name or "").strip(), [])
    if cands:
        return cands[idx % len(cands)]
    stem = Path(str(file_name or "unknown")).stem or "unknown"
    safe = re.sub(r"[^A-Za-z0-9_]", "_", stem)
    return f"{safe}_Class_{idx + 1}"


# Function: _build_classes_by_file
def _build_classes_by_file(class_signals: list[dict]) -> dict[str, list[str]]:
    classes_by_file: dict[str, list[str]] = {}
    for cs in class_signals:
        if not isinstance(cs, dict):
            continue
        file_name = str(cs.get("file") or "").strip()
        cls_name = _clean_name(cs.get("class"))
        if not file_name or not cls_name:
            continue
        classes_by_file.setdefault(file_name, []).append(cls_name)
    return classes_by_file


# Function: _normalize_per_fn_item
def _normalize_per_fn_item(item: dict, func_lookup: dict, classes_by_file: dict) -> None:
    # Normalize alias fields from varied LLM schemas before enrichment
    item["function"] = _clean_name(item.get("function") or item.get("name") or item.get("target"))
    if not item.get("file"):
        item["file"] = item.get("module") or item.get("path") or ""
    actual = func_lookup.get(item.get("function", "")) if item.get("function") else None
    if actual:
        item["cyclomatic_complexity"] = actual.get("cc", item.get("cyclomatic_complexity", 0))
        item["sloc"]                  = actual.get("sloc", item.get("sloc", 0))
        item["parameter_count"]       = actual.get("parameter_count", item.get("parameter_count", 0))
        if not item.get("class"):
            item["class"] = actual.get("class")
        if not item.get("file"):
            item["file"] = actual.get("file", "")
    # UI compatibility aliases
    if item.get("cc") is None:
        item["cc"] = item.get("cyclomatic_complexity", 0)
    # Normalize issues into a list for consistent rendering
    if not isinstance(item.get("issues"), list):
        issue_txt = str(item.get("issue") or "").strip()
        item["issues"] = [issue_txt] if issue_txt else []
    if _clean_name(item.get("class")) == "":
        item["class"] = _class_from_file(classes_by_file, item.get("file", ""), 0)


# Function: _dedupe_per_fn
def _dedupe_per_fn(per_fn: list[dict]) -> list[dict]:
    # Remove invalid rows (blank function names), then de-duplicate by (function, file)
    filtered_per_fn: list[dict] = []
    seen_pairs: set[tuple[str, str]] = set()
    for item in per_fn:
        fn_name = _clean_name(item.get("function"))
        file_name = str(item.get("file") or "").strip()
        if not fn_name:
            continue
        key = (fn_name.lower(), file_name.lower())
        if key in seen_pairs:
            continue
        seen_pairs.add(key)
        item["function"] = fn_name
        filtered_per_fn.append(item)
    return filtered_per_fn


# Function: _build_synth_fn_issues
def _build_synth_fn_issues(fn: dict, cc: int, params: int) -> list[str]:
    issues = []
    if cc >= 10:
        issues.append(f"High cyclomatic complexity CC={cc} (threshold 10)")
    if cc >= 15:
        issues.append("Critical complexity — unit testing near impossible")
    if params >= 5:
        issues.append(f"Long parameter list ({params} params) — violates clean code principles")
    if fn.get("sloc", 0) >= 60:
        issues.append(f"Long method ({fn['sloc']} LOC) — should be < 40 LOC")
    return issues


# Function: _build_synth_per_fn_entry
def _build_synth_per_fn_entry(fn: dict) -> dict:
    cc = fn.get("cc", 0)
    params = fn.get("parameter_count", 0)
    issues = _build_synth_fn_issues(fn, cc, params)
    return {
        "function":             fn.get("function", ""),
        "file":                 fn.get("file", ""),
        "class":                fn.get("class"),
        "language":             fn.get("language", ""),
        "cyclomatic_complexity": cc,
        "cc":                   cc,
        "sloc":                 fn.get("sloc", 0),
        "parameter_count":      params,
        "issues":               issues or ["Code quality review recommended"],
        "anti_patterns":        [],
        "refactoring_action":   "Decompose into smaller, single-purpose functions",
        "renamed_to":           None,
        "priority":             "high" if cc >= 15 else ("medium" if cc >= 10 else "low"),
        "estimated_effort_hours": max(2, cc // 3),
    }


# Function: _fill_missing_per_fn
def _fill_missing_per_fn(per_fn: list[dict], functions: list[dict]) -> list[dict]:
    # Ensure minimum 8 per-function entries
    existing_fns = {i.get("function", "") for i in per_fn if isinstance(i, dict)}
    for fn in functions:
        if len(per_fn) >= 12:
            break
        fname = fn.get("function", "")
        if fname in existing_fns:
            continue
        per_fn.append(_build_synth_per_fn_entry(fn))
        existing_fns.add(fname)
    return per_fn


# Function: _backfill_per_function_issues
def _backfill_per_function_issues(
    result: dict,
    functions: list[dict],
    class_signals: list[dict],
) -> None:
    func_lookup = {f["function"]: f for f in functions if isinstance(f, dict) and f.get("function")}
    classes_by_file = _build_classes_by_file(class_signals)

    raw_per_fn = result.get("per_function_issues") or []
    per_fn = [i for i in raw_per_fn if isinstance(i, dict)]
    for item in per_fn:
        _normalize_per_fn_item(item, func_lookup, classes_by_file)

    per_fn = _dedupe_per_fn(per_fn)
    per_fn = _fill_missing_per_fn(per_fn, functions)
    per_fn.sort(key=lambda i: int(i.get("cc") or i.get("cyclomatic_complexity") or 0), reverse=True)
    result["per_function_issues"] = per_fn[:12]


# Function: _backfill_anti_pattern_catalog
def _backfill_anti_pattern_catalog(result: dict, anti_hits: dict[str, dict[str, int]]) -> None:
    existing_patterns = {
        i.get("pattern", "").lower()
        for i in (result.get("anti_pattern_catalog") or [])
        if isinstance(i, dict)
    }
    catalog = result.get("anti_pattern_catalog") or []
    for ap in _ANTI_PATTERNS:
        ap_id, name, _, desc = ap
        file_hits = anti_hits.get(ap_id, {})
        total = sum(file_hits.values())
        if total == 0 or name.lower() in existing_patterns:
            continue
        worst = max(file_hits, key=file_hits.get) if file_hits else ""
        catalog.append({
            "pattern":       name,
            "category":      _ap_category(ap_id),
            "occurrences":   total,
            "affected_files": list(file_hits.keys())[:5],
            "worst_offender": worst,
            "remediation":   _ap_remediation(ap_id),
            "severity":      "high" if total > 20 else ("medium" if total > 5 else "low"),
        })
        existing_patterns.add(name.lower())
    result["anti_pattern_catalog"] = catalog


# Function: _backfill_coupling_analysis
def _backfill_coupling_analysis(result: dict, coupling: list[dict]) -> None:
    ca = result.get("coupling_analysis")
    if not isinstance(ca, dict):
        ca = {}
    tcp = ca.get("tightly_coupled_pairs") or []
    norm_tcp = []
    for p in tcp:
        if not isinstance(p, dict):
            continue
        norm_tcp.append({
            "from": p.get("from") or p.get("module_a") or p.get("a") or "unknown",
            "to": p.get("to") or p.get("module_b") or p.get("b") or "unknown",
            "reason": p.get("reason") or p.get("coupling_type") or "Tight coupling detected",
        })
    ca["tightly_coupled_pairs"] = norm_tcp
    if not ca.get("fanout_hotspots") and coupling:
        ca["fanout_hotspots"] = [
            {
                "file":             c["file"],
                "import_count":     c["import_count"],
                "imports":          c["import_count"],
                "imported_modules": c["imported_modules"][:8],
                "risk":             "High fan-out increases coupling and makes tests harder to write" if c["import_count"] > 10 else "Moderate coupling",
            }
            for c in coupling[:5]
        ]
    if not ca.get("tightly_coupled_pairs"):
        ca["tightly_coupled_pairs"] = []
    result["coupling_analysis"] = ca


# Function: _build_class_entry
def _build_class_entry(cs: dict) -> dict:
    mc = cs.get("method_count", 0)
    return {
        "class":          cs["class"],
        "class_name":     cs["class"],
        "file":           cs["file"],
        "language":       "Unknown",
        "method_count":   mc,
        "sloc":           cs.get("approx_sloc", 0),
        "anti_patterns":  ["God Class"] if mc > 15 else [],
        "responsibilities": ["Multiple (review needed)"],
        "coupling_score": "high" if mc > 15 else "medium",
        "cohesion_score": "low" if mc > 15 else "medium",
        "recommendation": "Break into smaller, focused classes following SRP" if mc > 10 else "Review for cohesion",
        "effort_days":    max(1, mc // 5),
    }


# Function: _normalize_class_entry
def _normalize_class_entry(cls: dict, classes_by_file: dict) -> None:
    if not cls.get("class_name"):
        cls["class_name"] = cls.get("class") or "UnknownClass"
    if _clean_name(cls.get("class_name")) == "":
        cls["class_name"] = _class_from_file(classes_by_file, cls.get("file", ""), 0)
    if _clean_name(cls.get("class")) == "":
        cls["class"] = cls.get("class_name")


# Function: _backfill_class_analysis
def _backfill_class_analysis(result: dict, class_signals: list[dict]) -> None:
    classes_by_file = _build_classes_by_file(class_signals)

    cls_analysis = result.get("class_analysis") or []
    existing_classes = {i.get("class", "") for i in cls_analysis if isinstance(i, dict)}
    for cs in class_signals:
        if cs["class"] in existing_classes:
            continue
        if len(cls_analysis) >= 8:
            break
        cls_analysis.append(_build_class_entry(cs))
        existing_classes.add(cs["class"])
    for cls in cls_analysis:
        if isinstance(cls, dict):
            _normalize_class_entry(cls, classes_by_file)
    result["class_analysis"] = cls_analysis


# Function: _default_quality_gates
def _default_quality_gates() -> list[dict]:
    return [
        {"gate": "Cyclomatic Complexity",   "metric": "max CC per function",      "threshold": "10",  "enforcement": "block", "priority": "high", "rationale": "Prevent untestable functions"},
        {"gate": "Method Length",           "metric": "max lines per function",   "threshold": "40",  "enforcement": "block", "priority": "high", "rationale": "Enforce decomposition"},
        {"gate": "Parameter Count",         "metric": "max parameters per method","threshold": "4",   "enforcement": "warn", "priority": "medium", "rationale": "Reduce API complexity"},
        {"gate": "Code Comment Ratio",      "metric": "comment lines / code lines","threshold": "15%", "enforcement": "warn", "priority": "low", "rationale": "Improve maintainability"},
        {"gate": "Test Coverage",           "metric": "line coverage",            "threshold": "70%", "enforcement": "block", "priority": "high", "rationale": "Guard refactoring safety"},
    ]


# Function: _normalize_naming_violations
def _normalize_naming_violations(naming: list) -> list:
    for n in naming:
        if not isinstance(n, dict):
            continue
        if not n.get("suggestion") and n.get("suggested_name"):
            n["suggestion"] = n.get("suggested_name")
        if not n.get("violation") and n.get("type"):
            n["violation"] = f"{n.get('type')} naming issue"
    return naming


# Function: _build_default_refactoring_plan
def _build_default_refactoring_plan(per_function_issues: list) -> list:
    plan = []
    for idx, fn in enumerate(per_function_issues[:6], start=1):
        if not isinstance(fn, dict):
            continue
        plan.append({
            "step": idx,
            "title": f"Refactor {fn.get('function', 'function')}",
            "target": fn.get("function", ""),
            "target_function": fn.get("function", ""),
            "file": fn.get("file", ""),
            "technique": fn.get("refactoring_action", "Extract Method"),
            "effort_hours": fn.get("estimated_effort_hours", 4),
            "priority": fn.get("priority", "medium"),
            "description": "; ".join((fn.get("issues") or [])[:2]) or "Refactor to reduce complexity",
        })
    return plan


# Function: _build_dead_code_indicators
def _build_dead_code_indicators(anti_hits: dict[str, dict[str, int]]) -> list:
    dead_hits = anti_hits.get("dead_assign", {}) or {}
    return [
        {
            "function": "possible_dead_assignment",
            "file": file_name,
            "reason": f"{count} dead-assignment pattern hit(s)",
        }
        for file_name, count in list(dead_hits.items())[:8]
    ]


# Function: _backfill_kpis_and_plan
def _backfill_kpis_and_plan(
    result: dict,
    analysis_result: dict | None,
    anti_hits: dict[str, dict[str, int]],
) -> None:
    if not result.get("quality_gates_recommended"):
        result["quality_gates_recommended"] = _default_quality_gates()

    result["naming_violations"] = _normalize_naming_violations(result.get("naming_violations") or [])

    plan = result.get("l3_refactoring_plan") or []
    if not plan:
        plan = _build_default_refactoring_plan(result.get("per_function_issues", []))
    result["l3_refactoring_plan"] = plan

    if not result.get("dead_code_indicators"):
        result["dead_code_indicators"] = _build_dead_code_indicators(anti_hits)

    if not result.get("code_smell_score"):
        total_issues = sum(
            len(i.get("issues", [])) for i in result["per_function_issues"] if isinstance(i, dict)
        )
        result["code_smell_score"] = max(10, min(95, 100 - total_issues * 4))
    if not result.get("maintainability_index"):
        health = (analysis_result or {}).get("health", {})
        result["maintainability_index"] = int(
            health.get("health", health.get("score", 50)) if isinstance(health, dict) else 50
        )


# Function: _enrich_result
def _enrich_result(
    result: dict,
    functions: list[dict],
    anti_hits: dict[str, dict[str, int]],
    class_signals: list[dict],
    coupling: list[dict],
    analysis_result: dict | None = None,
) -> dict:
    """
    Back-fill computed metrics into the LLM result to prevent hallucinations
    and ensure minimum item counts in every array field.
    """
    _backfill_per_function_issues(result, functions, class_signals)
    _backfill_anti_pattern_catalog(result, anti_hits)
    _backfill_coupling_analysis(result, coupling)
    _backfill_class_analysis(result, class_signals)
    _backfill_kpis_and_plan(result, analysis_result, anti_hits)
    return result


# Function: _ap_category
def _ap_category(ap_id: str) -> str:
    mapping = {
        "god_class":    "complexity",
        "long_param":   "maintainability",
        "magic_num":    "maintainability",
        "dead_assign":  "maintainability",
        "nested_cond":  "complexity",
        "print_debug":  "security",
        "empty_except": "error-handling",
        "todo_fixme":   "maintainability",
        "hardcoded_url":"security",
        "mutable_default": "security",
    }
    return mapping.get(ap_id, "maintainability")


# Function: _ap_remediation
def _ap_remediation(ap_id: str) -> str:
    mapping = {
        "god_class":    "Apply Single Responsibility Principle — decompose into focused sub-classes",
        "long_param":   "Introduce Parameter Object or Builder pattern",
        "magic_num":    "Extract to named constants (const/final/static readonly)",
        "dead_assign":  "Review and remove unused variable assignments",
        "nested_cond":  "Apply Extract Method or Replace Nested Conditional with Guard Clauses",
        "print_debug":  "Remove debug prints; use structured logging with log levels",
        "empty_except": "Log or re-raise exceptions; never swallow silently",
        "todo_fixme":   "Resolve or create tracked issue tickets; remove markers",
        "hardcoded_url":"Extract to environment variables or config files",
        "mutable_default": "Use None as default and initialise inside function body",
    }
    return mapping.get(ap_id, "Review and refactor according to clean code principles")
