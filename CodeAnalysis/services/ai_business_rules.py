# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Extracts business rules from source code using LLM analysis of:
# Date: 2025-07-19
# ---------------------------------------------------------------------------
"""
services/ai_business_rules.py
------------------------------
Extracts business rules from source code using LLM analysis of:
  * Function/method names and their call relationships
  * Inline comments and TODO/FIXME annotations
  * Validation logic patterns — actual if/elif conditions extracted (L3)
  * Domain terminology in identifiers
  * Data validation, access control, and calculation patterns
"""
from __future__ import annotations

import logging
import os
import re
from pathlib import Path

from .ollama_client import OllamaClient
from .ai_grounding import build_ground_truth, grounding_header, build_anti_hallucination_system_prompt, validate_business_rules

logger = logging.getLogger(__name__)


# Function: _is_missing_symbol
def _is_missing_symbol(v) -> bool:
    s = str(v or "").strip().lower()
    return s in {"", "-", "--", "---", "_", "?", "unknown", "n/a", "none", "null"}


# Function: _symbol_from_file
def _symbol_from_file(file_path: str, idx: int = 0) -> str:
    stem = Path(str(file_path or "unknown")).stem or "unknown"
    safe = re.sub(r"[^A-Za-z0-9_]", "_", stem)
    return f"{safe}_fn_{idx + 1}"

_SKIP_DIRS = {
    ".git", ".venv", "venv", "node_modules", "__pycache__",
    "dist", "build", "target", "vendor",
}

_SYSTEM_BASE = """\
You are a business analyst with deep software engineering expertise.
Given code snippets, function signatures, AND actual conditional/validation logic
extracted from the codebase, you identify and articulate the underlying business
rules and domain logic encoded in the code at L2/L3 level.
You MUST only reference function names and file paths that appear in the code samples provided.
Do NOT invent function names, class names, or file paths not present in the data.
Be concise. Limit ALL string values to 1 sentence. Name every function.
Always return valid JSON and nothing else."""

_PROMPT_TMPL = """\
Extract business rules from this repository: "{repo_name}"
Domain hints from code: languages={languages}, layers={arch_layers}

FUNCTION SIGNATURES AND COMMENTS SAMPLED FROM THE CODEBASE:
{code_samples}

VALIDATION AND CONDITIONAL LOGIC EXTRACTED (L3 — actual conditions from code):
{validation_logic}

CLASS-LEVEL DOMAIN ENTITIES:
{class_entities}

TODO/FIXME ANNOTATIONS:
{todos}

Return a JSON object with deep L2/L3 business rule detail:
{{
  "domain": "<primary business domain of this application>",
  "summary": "<3-4 sentences describing what this system does and its key domain entities>",
  "business_rules": [
    {{
      "id": "BR-<three digit number>",
      "title": "<concise rule title>",
      "description": "<plain-English description of the rule>",
      "type": "<validation|calculation|workflow|access-control|integration|data-transform|constraint>",
      "confidence": "high|medium|low",
      "source_function": "<exact function name that implements this rule>",
      "source_file": "<relative file path>",
      "source_evidence": "<actual code condition or logic e.g. 'if amount > 10000: require_approval()'>",
      "affected_entities": ["<entity or concept names>"],
      "rule_condition": "<formal condition: WHEN <trigger> THEN <action> IF <constraint>>",
      "testable": <true|false>
    }}
  ],
  "validation_rules": [
    {{
      "field": "<field or parameter name being validated>",
      "function": "<function performing the validation>",
      "file": "<relative file path>",
      "constraint": "<the validation constraint>",
      "enforcement": "<client|server|both>"
    }}
  ],
  "key_entities": ["<main domain entities identified>"],
  "workflows": [
    {{
      "name": "<workflow name>",
      "trigger": "<what starts this workflow>",
      "steps": ["<ordered step descriptions naming actual functions>"],
      "terminal_states": ["<success or failure state names>"]
    }}
  ]
}}

Provide 4-5 business_rules and 1-2 workflows, name every function.
Return ONLY the JSON."""


_SAMPLE_EXTS = {".py", ".java", ".cs", ".js", ".ts", ".kt", ".rb"}


# Function: _scan_lines_for_samples
def _scan_lines_for_samples(text: str, rel: str, sig_lines: list, todo_lines: list, sig_pat, todo_pat, collected_chars: int, max_chars: int) -> int:
    for line in text.splitlines():
        sm = sig_pat.search(line)
        if sm:
            sig_lines.append(f"  [{rel}] {line.strip()[:120]}")
            collected_chars += len(sig_lines[-1])
            if collected_chars >= max_chars:
                break
        tm = todo_pat.search(line)
        if tm:
            todo_lines.append(f"  [{rel}] {tm.group(0)[:120]}")
    return collected_chars


# Function: _scan_docstrings_for_samples
def _scan_docstrings_for_samples(text: str, sig_lines: list, doc_pat, collected_chars: int) -> int:
    # Docstrings / block comments
    for dm in doc_pat.findall(text):
        fragment = next((d for d in dm if d.strip()), None)
        if fragment:
            sig_lines.append(f"  [doc] {fragment.strip()[:120]}")
            collected_chars += len(sig_lines[-1])
    return collected_chars


# Function: _process_file_for_samples
def _process_file_for_samples(
    fpath: Path, root: Path, sig_lines: list, todo_lines: list,
    sig_pat, doc_pat, todo_pat, collected_chars: int, max_chars: int,
) -> int:
    if fpath.suffix.lower() not in _SAMPLE_EXTS:
        return collected_chars
    try:
        rel_parts = fpath.relative_to(root).parts
    except ValueError:
        return collected_chars
    try:
        text = fpath.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return collected_chars

    rel = "/".join(rel_parts)
    collected_chars = _scan_lines_for_samples(text, rel, sig_lines, todo_lines, sig_pat, todo_pat, collected_chars, max_chars)
    collected_chars = _scan_docstrings_for_samples(text, sig_lines, doc_pat, collected_chars)
    return collected_chars


# Function: _collect_code_samples
def _collect_code_samples(repo_path: str, max_chars: int = 1500) -> tuple[str, str]:
    """Scan source files for function signatures, docstrings, and comments."""
    if not repo_path:
        return "", ""
    root = Path(repo_path)
    if not root.exists():
        return "", ""
    sig_lines: list[str] = []
    todo_lines: list[str] = []

    _SIG_PAT  = re.compile(r"(def |function |public |private |protected )(.{0,120})")
    _DOC_PAT  = re.compile(r'"""(.{0,200}?)"""|\'\'\'(.{0,200}?)\'\'\'|/\*\*(.{0,200}?)\*/', re.DOTALL)
    _TODO_PAT = re.compile(r"(?i)(TODO|FIXME|HACK|XXX|NOTE):?\s*(.{0,120})")

    collected_chars = 0

    for dirpath, dirnames, filenames in os.walk(str(root)):
        dirnames[:] = [d for d in dirnames if d not in _SKIP_DIRS]
        if collected_chars >= max_chars:
            break
        dir_path = Path(dirpath)
        for fname in filenames:
            if collected_chars >= max_chars:
                break
            fpath = dir_path / fname
            collected_chars = _process_file_for_samples(
                fpath, root, sig_lines, todo_lines, _SIG_PAT, _DOC_PAT, _TODO_PAT, collected_chars, max_chars
            )

    return (
        "\n".join(sig_lines[:60]) or "  (no signatures found)",
        "\n".join(todo_lines[:20])  or "  (no TODOs found)",
    )


# Function: _scan_file_for_conditions
def _scan_file_for_conditions(source: str, rel: str, cond_pat, value_pat, conditions: list, max_conditions: int) -> None:
    # Find the enclosing function name for context
    func_name: str = "?"
    for line in source.splitlines():
        m_fn = re.match(r"^\s*(?:async\s+)?def\s+(\w+)", line)
        if m_fn:
            func_name = m_fn.group(1)
        m_cond = cond_pat.match(line)
        if m_cond and value_pat.search(line):
            cond = line.strip()[:100]
            conditions.append(f"  [{rel}::{func_name}] {cond}")
            if len(conditions) >= max_conditions:
                break


# Function: _scan_dir_for_conditions
def _scan_dir_for_conditions(
    dir_path: Path, filenames: list, root: Path, cond_pat, value_pat,
    conditions: list, max_conditions: int, scanned: int,
) -> int:
    for fname in filenames:
        if scanned >= 40 or len(conditions) >= max_conditions:
            break
        fpath = dir_path / fname
        if fpath.suffix.lower() not in _SAMPLE_EXTS:
            continue
        try:
            rel_parts = fpath.relative_to(root).parts
        except ValueError:
            continue
        try:
            source = fpath.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        scanned += 1
        rel = "/".join(rel_parts)
        _scan_file_for_conditions(source, rel, cond_pat, value_pat, conditions, max_conditions)
    return scanned


# Function: _extract_validation_logic
def _extract_validation_logic(repo_path: str, max_conditions: int = 20) -> str:
    """
    Extract actual if-condition lines that look like business rule enforcement.
    Focuses on: comparisons with domain values, raise/return statements, assert statements.
    Returns formatted string for the LLM prompt.
    """
    if not repo_path:
        return "  (no repo path)"
    root = Path(repo_path)
    if not root.exists():
        return "  (repo path not found)"

    # Patterns that signal business logic / validation
    _COND_PAT = re.compile(
        r"^\s*(?:if|elif|assert|raise|return)\s+.{10,120}$",
        re.MULTILINE
    )
    _VALUE_PAT = re.compile(
        r"(?:>\s*\d|<\s*\d|==\s*['\"]|!=\s*['\"]|in\s+\[|not\s+in\s+|is\s+None|is\s+not\s+None"
        r"|raise\s+\w+Error|assert\s+\w|forbidden|unauthorized|invalid|required|must\s+be"
        r"|minimum|maximum|max_length|min_value|max_value)",
        re.IGNORECASE
    )

    conditions: list[str] = []
    scanned = 0
    for dirpath, dirnames, filenames in os.walk(str(root)):
        dirnames[:] = [d for d in dirnames if d not in _SKIP_DIRS]
        if scanned >= 40 or len(conditions) >= max_conditions:
            break
        dir_path = Path(dirpath)
        scanned = _scan_dir_for_conditions(dir_path, filenames, root, _COND_PAT, _VALUE_PAT, conditions, max_conditions, scanned)

    return "\n".join(conditions[:max_conditions]) or "  (no validation logic extracted)"


_ENTITY_EXTS = {".py", ".java", ".cs", ".kt"}
_ENTITY_SKIP_NAMES = {"Base", "Meta", "Config", "Test", "Abstract"}


# Function: _scan_file_for_entities
def _scan_file_for_entities(source: str, rel: str, class_pat, entities: dict) -> None:
    for m in class_pat.finditer(source):
        name = m.group(1) or m.group(2) or ""
        if name and name not in _ENTITY_SKIP_NAMES:
            entities[name] = rel


# Function: _scan_dir_for_entities
def _scan_dir_for_entities(dir_path: Path, filenames: list, root: Path, class_pat, entities: dict) -> None:
    for fname in filenames:
        if len(entities) >= 30:
            break
        fpath = dir_path / fname
        if fpath.suffix.lower() not in _ENTITY_EXTS:
            continue
        try:
            rel_parts = fpath.relative_to(root).parts
        except ValueError:
            continue
        try:
            source = fpath.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        rel = "/".join(rel_parts)
        _scan_file_for_entities(source, rel, class_pat, entities)


# Function: _extract_class_entities
def _extract_class_entities(repo_path: str) -> str:
    """Extract class names as domain entity candidates."""
    if not repo_path:
        return "  (no repo path)"
    root = Path(repo_path)
    if not root.exists():
        return "  (not found)"
    _CLASS_PAT = re.compile(r"(?:^class\s+(\w+)|public\s+class\s+(\w+))", re.MULTILINE)
    entities: dict[str, str] = {}
    for dirpath, dirnames, filenames in os.walk(str(root)):
        dirnames[:] = [d for d in dirnames if d not in _SKIP_DIRS]
        if len(entities) >= 30:
            break
        dir_path = Path(dirpath)
        _scan_dir_for_entities(dir_path, filenames, root, _CLASS_PAT, entities)
    lines = [f"  {cls} ({file})" for cls, file in list(entities.items())[:25]]
    return "\n".join(lines) or "  (no classes found)"


# Function: analyse_business_rules
def analyse_business_rules(
    analysis_result: dict,
    repo_path: str,
    model: str | None = None,
    client: OllamaClient | None = None,
) -> dict:
    client = client or OllamaClient()

    # ── Ground truth ──────────────────────────────────────────────────
    gt = build_ground_truth(analysis_result)
    _SYSTEM = build_anti_hallucination_system_prompt(_SYSTEM_BASE, gt)

    arch   = analysis_result.get("architecture", {}) or {}
    layers = list((arch.get("layer_counts") or {}).keys())

    code_samples, todos = _collect_code_samples(repo_path)
    validation_logic    = _extract_validation_logic(repo_path)
    class_entities      = _extract_class_entities(repo_path)

    ground_block = grounding_header(gt)

    prompt = ground_block + "\n\n" + _PROMPT_TMPL.format(
        repo_name        = gt["repo_name"],
        languages        = ", ".join(gt["languages"]),
        arch_layers      = ", ".join(layers) or "unknown",
        code_samples     = code_samples,
        validation_logic = validation_logic,
        class_entities   = class_entities,
        todos            = todos,
    )

    try:
        # Reduced max_tokens from 900 → 700 to avoid timeouts
        # timeout=540 for token generation headroom
        result = client.generate_json(prompt, model=model, system=_SYSTEM,
                                      max_tokens=700, num_ctx=5120, timeout=540)
        result["_model_used"] = model or client.best_available_model()
        result = _enrich_business_rules(result, analysis_result, validation_logic, class_entities)
        result = validate_business_rules(result, gt)
        return result
    except Exception as exc:
        logger.error("ai_business_rules failed: %s", exc)
        return {"error": str(exc), "summary": "AI analysis unavailable."}



# Function: _parse_validation_evidence
def _parse_validation_evidence(validation_logic_txt: str) -> tuple[list, list]:
    """Parse validation evidence lines into structured list and function name pool."""
    parsed_validations: list[dict] = []
    for ln in (validation_logic_txt or "").splitlines():
        ln = ln.strip()
        if not ln.startswith("[") or "]" not in ln:
            continue
        head, cond = ln[1:].split("]", 1)
        cond = cond.strip()
        if "::" in head:
            file_name, fn = head.split("::", 1)
        else:
            file_name, fn = head, "unknown"
        parsed_validations.append({
            "file": file_name.strip(),
            "function": fn.strip() or "unknown",
            "constraint": cond or "Validation condition",
        })
    validation_fn_pool = [
        v.get("function")
        for v in parsed_validations
        if isinstance(v, dict) and not _is_br_missing_symbol(v.get("function"))
    ]
    return parsed_validations, validation_fn_pool


# Function: _is_br_missing_symbol
def _is_br_missing_symbol(v) -> bool:
    s = str(v or "").strip().lower()
    return s in {"", "-", "--", "---", "_", "?", "unknown", "n/a", "none", "null"}


# Function: _symbol_from_br_file
def _symbol_from_br_file(file_path: str, idx: int) -> str:
    stem = Path(str(file_path or "unknown")).stem or "unknown"
    safe = re.sub(r"[^A-Za-z0-9_]", "_", stem)
    return f"{safe}_rule_fn_{idx + 1}"


# Function: _fill_default_rule_fields
def _fill_default_rule_fields(rule: dict) -> None:
    if not rule.get("source_function"):
        rule["source_function"] = rule.get("source_evidence", "").split("(")[0].strip()[:50] or ""
    if "testable" not in rule:
        rule["testable"] = rule.get("confidence", "medium") in ("high", "medium")
    if not rule.get("rule_condition"):
        rule["rule_condition"] = f"WHEN relevant input THEN {rule.get('title', 'apply rule')} IF {rule.get('description', 'condition met')[:60]}"


# Function: _backfill_rule_source_from_validation
def _backfill_rule_source_from_validation(rule: dict, parsed_validations: list) -> None:
    fn = str(rule.get("source_function") or "").strip()
    match = next((v for v in parsed_validations if v.get("function") == fn), None)
    if not rule.get("source_file"):
        rule["source_file"] = (match or {}).get("file", "unknown")
    if not rule.get("source_evidence"):
        rule["source_evidence"] = (match or {}).get("constraint", "Rule inferred from source code")


# Function: _fill_missing_rule_source_function
def _fill_missing_rule_source_function(rule: dict, idx: int, parsed_validations: list, validation_fn_pool: list) -> None:
    if not _is_br_missing_symbol(rule.get("source_function")):
        return
    sf = str(rule.get("source_file") or "").strip()
    match = next((v for v in parsed_validations if str(v.get("file", "")).strip() == sf and not _is_br_missing_symbol(v.get("function"))), None)
    if match:
        rule["source_function"] = match.get("function")
    elif validation_fn_pool:
        rule["source_function"] = validation_fn_pool[idx % len(validation_fn_pool)]
    else:
        rule["source_function"] = _symbol_from_br_file(sf or "unknown", idx)


# Function: _normalize_one_rule
def _normalize_one_rule(rule: dict, idx: int, parsed_validations: list, validation_fn_pool: list) -> None:
    _fill_default_rule_fields(rule)
    _backfill_rule_source_from_validation(rule, parsed_validations)
    if not isinstance(rule.get("affected_entities"), list):
        rule["affected_entities"] = []
    _fill_missing_rule_source_function(rule, idx, parsed_validations, validation_fn_pool)


# Function: _normalize_business_rules
def _normalize_business_rules(rules: list, parsed_validations: list, validation_fn_pool: list) -> list:
    """Normalise each business rule: fill in missing source_function, testable, rule_condition etc."""
    for idx, rule in enumerate(rules):
        if not isinstance(rule, dict):
            continue
        _normalize_one_rule(rule, idx, parsed_validations, validation_fn_pool)
    return rules


# Function: _fix_workflow_step
def _fix_workflow_step(step, wi: int, si: int, validation_fn_pool: list) -> str:
    txt = str(step or "").strip()
    if _is_br_missing_symbol(txt) or "unknown" in txt.lower() or txt.lower() == "rule":
        if validation_fn_pool:
            fn_name = validation_fn_pool[(wi + si) % len(validation_fn_pool)]
            txt = f"Evaluate {fn_name}"
        else:
            txt = f"Evaluate {_symbol_from_br_file('workflow', wi + si)}"
    return txt


# Function: _normalize_one_workflow
def _normalize_one_workflow(wf, wi: int, validation_fn_pool: list) -> None:
    if not isinstance(wf, dict):
        return
    if not wf.get("terminal_states"):
        wf["terminal_states"] = ["success", "failure"]
    steps = wf.get("steps") or []
    if isinstance(steps, list):
        wf["steps"] = [_fix_workflow_step(step, wi, si, validation_fn_pool) for si, step in enumerate(steps)]


# Function: _default_br_workflow
def _default_br_workflow(rules: list) -> dict:
    return {
        "name": "Primary rule execution flow",
        "trigger": "Incoming request or processing event",
        "steps": [
            f"Evaluate {r.get('source_function','rule')} in {r.get('source_file','unknown')}"
            for r in rules[:5]
        ],
        "terminal_states": ["success", "failure"],
    }


# Function: _ensure_br_workflows
def _ensure_br_workflows(result: dict, rules: list, validation_fn_pool: list) -> dict:
    """Ensure workflows are structured and non-empty."""
    workflows = result.get("workflows") or []
    for wi, wf in enumerate(workflows):
        _normalize_one_workflow(wf, wi, validation_fn_pool)
    if not workflows and rules:
        workflows = [_default_br_workflow(rules)]
    result["workflows"] = workflows
    return result


# Function: _ensure_br_key_entities
def _ensure_br_key_entities(result: dict, class_entities_txt: str) -> dict:
    """Ensure key_entities present from class extraction fallback."""
    entities = result.get("key_entities") or []
    if not entities:
        parsed_entities = []
        for line in (class_entities_txt or "").splitlines():
            line = line.strip()
            if not line:
                continue
            parts = line.split("(", 1)
            name = parts[0].strip()
            if name:
                parsed_entities.append(name)
        result["key_entities"] = parsed_entities[:12]
    return result


# Function: _enrich_business_rules
_DEFAULT_BR_ENFORCEMENT_LIMIT = 6


# Function: _build_deterministic_rule
def _build_deterministic_rule(pv: dict, seed: int) -> dict:
    return {
        "id": f"BR-{seed:03d}",
        "title": f"Validation in {pv['function']}",
        "description": "Input or state validation enforced in code path.",
        "type": "validation",
        "confidence": "high",
        "source_function": pv["function"],
        "source_file": pv["file"],
        "source_evidence": pv["constraint"],
        "affected_entities": [],
        "rule_condition": f"WHEN request reaches {pv['function']} THEN enforce '{pv['constraint']}'",
        "testable": True,
    }


# Function: _generate_deterministic_rules
def _generate_deterministic_rules(rules: list, parsed_validations: list) -> list:
    # L3 fallback: if rules are too few, generate deterministic rules from validation extraction
    if len(rules) >= 4 or not parsed_validations:
        return rules
    existing_keys = {f"{r.get('source_file','')}::{r.get('source_function','')}" for r in rules if isinstance(r, dict)}
    seed = len(rules) + 1
    for pv in parsed_validations:
        key = f"{pv['file']}::{pv['function']}"
        if key in existing_keys:
            continue
        rules.append(_build_deterministic_rule(pv, seed))
        seed += 1
        if len(rules) >= _DEFAULT_BR_ENFORCEMENT_LIMIT:
            break
    return rules


# Function: _ensure_br_validation_rules
def _ensure_br_validation_rules(result: dict, parsed_validations: list) -> None:
    # Ensure validation_rules present
    if not result.get("validation_rules"):
        result["validation_rules"] = [
            {
                "field": "derived",
                "function": v["function"],
                "file": v["file"],
                "constraint": v["constraint"],
                "enforcement": "server",
            }
            for v in parsed_validations[:8]
        ]


# Function: _fix_one_validation_rule_function
def _fix_one_validation_rule_function(vr: dict, i: int, parsed_validations: list, validation_fn_pool: list) -> None:
    if not _is_missing_symbol(vr.get("function")):
        return
    file_name = str(vr.get("file") or "").strip()
    match = next((v for v in parsed_validations if str(v.get("file", "")).strip() == file_name and not _is_missing_symbol(v.get("function"))), None)
    if match:
        vr["function"] = match.get("function")
    elif validation_fn_pool:
        vr["function"] = validation_fn_pool[i % len(validation_fn_pool)]
    else:
        vr["function"] = _symbol_from_file(file_name or "unknown", i)


# Function: _fix_validation_rule_functions
def _fix_validation_rule_functions(v_rules: list, parsed_validations: list, validation_fn_pool: list) -> list:
    # Strict fallback naming for validation_rules.function
    for i, vr in enumerate(v_rules):
        if not isinstance(vr, dict):
            continue
        _fix_one_validation_rule_function(vr, i, parsed_validations, validation_fn_pool)
    return v_rules


# Function: _build_br_kpi
def _build_br_kpi(result: dict) -> dict:
    return {
        "rules": len(result.get("business_rules") or []),
        "workflows": len(result.get("workflows") or []),
        "entities": len(result.get("key_entities") or []),
        "high_confidence_rules": len([
            r for r in (result.get("business_rules") or [])
            if isinstance(r, dict) and str(r.get("confidence", "")).lower() == "high"
        ]),
    }


# Function: _enrich_business_rules
def _enrich_business_rules(result: dict, analysis_result: dict, validation_logic_txt: str, class_entities_txt: str) -> dict:
    """Ensure minimum required fields in the business rules result."""
    parsed_validations, validation_fn_pool = _parse_validation_evidence(validation_logic_txt)

    # Normalise business_rules — ensure each has source_function and testable
    rules = result.get("business_rules") or []
    rules = _normalize_business_rules(rules, parsed_validations, validation_fn_pool)
    rules = _generate_deterministic_rules(rules, parsed_validations)

    result["business_rules"] = rules

    _ensure_br_validation_rules(result, parsed_validations)

    v_rules = result.get("validation_rules") or []
    v_rules = _fix_validation_rule_functions(v_rules, parsed_validations, validation_fn_pool)
    result["validation_rules"] = v_rules

    # Ensure access_control_rules present
    if not result.get("access_control_rules"):
        result["access_control_rules"] = []

    # Ensure calculations present
    if not result.get("calculations"):
        result["calculations"] = []

    result = _ensure_br_workflows(result, rules, validation_fn_pool)
    result = _ensure_br_key_entities(result, class_entities_txt)

    # KPI block for stable dashboard counts
    result["kpi"] = _build_br_kpi(result)

    return result
