# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Modernization — services/modernizer (docs_generation.py)
# Date: 2026-06-26
# ---------------------------------------------------------------------------
from __future__ import annotations

import functools
import hashlib
import json
import logging
import os
import re
import tempfile
import textwrap
import time
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

from ._shared import _SRC_TRUNCATE_AT



# ─── Modernization Documentation Generator ────────────────────────────────────

# Function: _generate_modernization_docs
# Function: _gmd_parse_conv_log
def _gmd_parse_conv_log(converted_files: Dict[str, str]) -> List[dict]:
    import json as _json
    conv_log_raw = converted_files.get("ModernizedApp/.modernization/conversion_log.json", "[]")
    try:
        return _json.loads(conv_log_raw)
    except Exception:
        return []


# Function: _gmd_ap_dict
def _gmd_ap_dict(antipatterns: List[dict]) -> Dict[str, int]:
    ap_dict: Dict[str, int] = {}
    for ap in antipatterns:
        ap_dict[ap.get("type", "unknown")] = ap_dict.get(ap.get("type", "unknown"), 0) + 1
    return ap_dict


# Function: _gmd_check_llm
def _gmd_check_llm() -> tuple:
    from .prompt_pipeline import _safe_build_system_prompt
    llm_ok = False
    model = ""
    system = ""
    try:
        from services.llm import generate, check_status, pick_codegen_model
        info = check_status()
        llm_ok = info.get("available", False)
        model = pick_codegen_model() or ""  # fast VRAM-resident model, not the forced status default
        # Docs are prose, not source in any one profiled language — the
        # stack-neutral core alone (no language/framework/datastore profile)
        # is the right fit here.
        system = _safe_build_system_prompt([])
    except Exception:
        pass
    return llm_ok, model, system


# Function: _gmd_class_rows
def _gmd_class_rows(conv_log: List[dict]) -> List[str]:
    class_rows_list = []
    for entry in conv_log:
        kind = entry.get("type", "")
        if kind not in ("llm_converted", "template_annotated", "llm_failed", "config_preserved"):
            continue
        src  = entry.get("source", "")
        out  = entry.get("output", "")
        lang_label = entry.get("lang", "")
        cls_count  = entry.get("classes", "")
        cls_note   = f" ({cls_count} classes)" if cls_count else ""
        status = {
            "llm_converted":    f"✅ Converted{cls_note}",
            "template_annotated": "⚠️ Annotated (needs review)",
            "llm_failed":       "❌ Failed",
            "config_preserved": "📄 Config preserved",
        }.get(kind, kind)
        class_rows_list.append(f"| `{Path(src).name}` | `{lang_label}` | `{Path(out).name}` | {status} |")
    return class_rows_list


# Function: _gmd_dir_summary
def _gmd_dir_summary(conv_log: List[dict]) -> Dict[str, Dict[str, int]]:
    dir_summary: Dict[str, Dict[str, int]] = {}
    for entry in conv_log:
        src = entry.get("source", "")
        src_dir = str(Path(src).parent)
        d = dir_summary.setdefault(src_dir, {"total": 0, "converted": 0, "annotated": 0})
        d["total"] += 1
        if entry.get("type") == "llm_converted":
            d["converted"] += 1
        elif entry.get("type") == "template_annotated":
            d["annotated"] += 1
    return dir_summary


# Function: _generate_modernization_docs
def _generate_modernization_docs(
    folder_path: str,
    analysis: dict,
    target: dict,
    root_ns: str,
    converted_files: Dict[str, str],
    on_progress: Optional[Callable[[str, int, str], None]] = None,
    guide_text: str = "",
) -> Dict[str, str]:
    """
    Generate comprehensive modernization documentation:
    - MODERNIZATION_REPORT.md  : Executive summary + change log
    - ARCHITECTURE_CHANGES.md  : Before/after architecture comparison
    - CLASS_MIGRATION_MAP.md   : Class-by-class migration table
    - API_CHANGES.md           : API surface changes
    """
    docs: Dict[str, str] = {}
    arch       = analysis.get("architecture", {})
    tech_stack = analysis.get("tech_stack", {})
    metrics    = analysis.get("metrics", {})
    domains    = analysis.get("domains", {})
    db_info    = analysis.get("database", {})
    lang_dist  = analysis.get("languages", {})
    antipatterns = analysis.get("antipatterns", [])

    stack_name  = target.get("name", "Unknown")
    be_tech     = target.get("backend_tech", "")
    fe_tech     = target.get("frontend_tech", "")
    db_tech     = target.get("db_tech", "")

    # ── Try LLM for enriched documentation ────────────────────────────────
    llm_ok, model, system = _gmd_check_llm()

    guide_sec = _guide_section(guide_text)

    # Collect conversion log
    conv_log: List[dict] = _gmd_parse_conv_log(converted_files)

    llm_converted   = [e for e in conv_log if e.get("type") == "llm_converted"]
    tmpl_annotated  = [e for e in conv_log if e.get("type") == "template_annotated"]
    config_kept     = [e for e in conv_log if e.get("type") == "config_preserved"]
    failed          = [e for e in conv_log if e.get("type") == "llm_failed"]

    # ── MODERNIZATION_REPORT.md ────────────────────────────────────────────
    if on_progress:
        on_progress("docs", 87, "Generating modernization report...")

    src_pattern    = arch.get("pattern", "Legacy Application")
    src_era        = arch.get("era", "Unknown")
    src_db         = arch.get("database", "Unknown")
    src_complexity = arch.get("complexity", "unknown")
    total_loc      = metrics.get("total_loc", 0)
    class_count    = metrics.get("class_count", 0)
    method_count   = metrics.get("method_count", 0)
    build_system   = arch.get("build_system", "")

    # Language distribution table
    lang_rows = "\n".join(
        f"| {l} | {v.get('files', 0)} | {v.get('lines', 0):,} |"
        for l, v in sorted(lang_dist.items(), key=lambda x: -x[1].get("lines", 0))
    )

    # Detected technologies
    tech_rows = "\n".join(
        f"| `{t}` | {v.get('file_count', 0)} files |"
        for t, v in sorted(tech_stack.items(), key=lambda x: -x[1].get("file_count", 0))
    ) or "| (none detected) | |"

    # Anti-patterns
    ap_dict = _gmd_ap_dict(antipatterns)
    ap_rows = "\n".join(f"| `{k}` | {v} occurrences |" for k, v in ap_dict.items()) or "| none detected | |"

    # Domains
    domain_rows = "\n".join(
        f"| `{d}` | {v.get('file_count', 0)} files | `{v.get('suggested_service', '')}` |"
        for d, v in domains.items()
    )

    # File conversion summary
    total_files = len(conv_log)

    report = f"""# Modernization Report

**Project:** `{Path(folder_path).name}`  
**Analysis Date:** {analysis.get('analysed_at', 'N/A')}  
**Target Stack:** {stack_name}

---

## Executive Summary

| Metric | Value |
|--------|-------|
| Source Architecture | {src_pattern} |
| Source Era | {src_era} |
| Source Database | {src_db} |
| Build System | {build_system or 'N/A'} |
| Complexity | {src_complexity} |
| Total LOC | {total_loc:,} |
| Total Classes | {class_count} |
| Total Methods | {method_count} |
| Total Files Analysed | {analysis.get('file_count', 0)} |
| Source Files Converted | {total_files} |
| LLM-Converted Files | {len(llm_converted)} |
| Template-Annotated Files | {len(tmpl_annotated)} |
| Config/Resource Files | {len(config_kept)} |
| Failed Conversions | {len(failed)} |

---

## Source Language Distribution

| Language | Files | Lines |
|----------|-------|-------|
{lang_rows}

---

## Detected Technologies

| Technology | Coverage |
|------------|----------|
{tech_rows}

---

## Anti-Patterns Detected & Fixed

| Anti-Pattern | Count |
|--------------|-------|
{ap_rows}

---

## Inferred Domains / Microservices

| Domain | Files | Suggested Service |
|--------|-------|-------------------|
{domain_rows}

---

## Target Architecture

| Layer | Technology |
|-------|------------|
| Backend | {be_tech} |
| Frontend | {fe_tech} |
| Database | {db_tech} |
| Root Package | `{root_ns}` |

---

## Files Converted

### LLM-Converted ({len(llm_converted)} files)
{"".join(f"- `{e['source']}` → `{e['output']}`\\n" for e in llm_converted) or "_None_"}

### Template-Annotated (require manual review — {len(tmpl_annotated)} files)
{"".join(f"- `{e['source']}` → `{e['output']}`\\n" for e in tmpl_annotated) or "_None_"}

### Config / Resource Files Preserved ({len(config_kept)} files)
{"".join(f"- `{e['source']}`\\n" for e in config_kept) or "_None_"}

### Failed Conversions ({len(failed)} files)
{"".join(f"- `{e['source']}`: {e.get('error', '')}\\n" for e in failed) or "_None_"}

---

## Key Migration Actions

{_migration_action_list(src_db, arch, tech_stack, target)}
"""

    docs["ModernizedApp/MODERNIZATION_REPORT.md"] = report

    # ── ARCHITECTURE_CHANGES.md ────────────────────────────────────────────
    if on_progress:
        on_progress("docs", 89, "Generating architecture changes document...")

    src_tree = _build_folder_tree(folder_path, max_depth=4, max_files_per_dir=6)
    out_tree = _build_output_tree(converted_files)

    arc_doc = f"""# Architecture Changes

## Source Project Structure

```
{src_tree}
```

## Modernized Output Structure

```
{out_tree}
```

## Architectural Comparison

| Aspect | Before ({src_pattern}) | After ({stack_name}) |
|--------|------------------------|---------------------|
| Runtime | {arch.get("era", "Legacy")} | Latest LTS |
| Build | {arch.get("build_system", "N/A")} | Updated Maven/Gradle/npm |
| Database | {arch.get("database", "Unknown")} | {target.get("db_tech", "N/A")} |
| Backend | {", ".join(list(tech_stack.keys())[:3])} | {target.get("backend_tech", "N/A")} |
| Frontend | {target.get("frontend_tech", "N/A")} | {target.get("frontend_tech", "N/A")} |
| Complexity | {arch.get("complexity", "unknown")} | Decomposed microservices |

## Key Structural Changes

{_structural_changes(arch, target, tech_stack)}

## Package / Namespace Mapping

| Legacy Package | Modernized Package |
|----------------|-------------------|
{_package_mapping_table(conv_log, root_ns)}
"""
    docs["ModernizedApp/ARCHITECTURE_CHANGES.md"] = arc_doc

    # ── CLASS_MIGRATION_MAP.md ─────────────────────────────────────────────
    if on_progress:
        on_progress("docs", 91, "Generating class migration map...")

    src_lang_dist = analysis.get("languages", {})
    primary_src_lang = (max(src_lang_dist, key=lambda k: src_lang_dist[k].get("lines", 0))
                        if src_lang_dist else "unknown")

    class_rows_list = _gmd_class_rows(conv_log)
    dir_summary = _gmd_dir_summary(conv_log)

    dir_rows = "\n".join(
        f"| `{ddir}` | {v['total']} | {v['converted']} | {v['annotated']} |"
        for ddir, v in sorted(dir_summary.items())
    ) or "| (none) | | | |"

    class_doc = f"""# Class & File Migration Map

## Directory-Level Summary

| Directory | Total Files | LLM Converted | Annotated |
|-----------|------------|--------------|-----------|
{dir_rows}

---

## File-Level Migration Details

| Source File | Language | Modernized File | Status |
|-------------|----------|-----------------|--------|
{chr(10).join(class_rows_list) or "| (no files) | | | |"}

---

## Legend

| Symbol | Meaning |
|--------|---------|
| ✅ Converted | File fully converted by AI — production-ready code |
| ⚠️ Annotated (needs review) | LLM unavailable — original preserved with migration guidance |
| ❌ Failed | Conversion attempted but failed — original preserved |
| 📄 Config preserved | Config/resource file migrated with header annotation |

---

## How to Review Converted Code

1. Open each `✅ Converted` file and verify the business logic matches the source
2. Run unit tests after adding dependencies to `pom.xml` / `build.gradle` / project file
3. For each `⚠️ Annotated` file: read the migration guidance header and complete the conversion
4. Check `MODERNIZATION_REPORT.md` for anti-pattern fixes that were applied
"""
    docs["ModernizedApp/CLASS_MIGRATION_MAP.md"] = class_doc

    # ── API_CHANGES.md ─────────────────────────────────────────────────────
    if on_progress:
        on_progress("docs", 93, "Generating API changes document...")

    api_doc = f"""# API Changes

## Source API Style

{_source_api_style(arch, tech_stack)}

## Modernized API Style

{_target_api_style(target)}

## Endpoint Naming Convention

| Before | After |
|--------|-------|
| Legacy controller/servlet mapping | REST resource: `/api/{{resource}}` |
| GET parameters in query string | `?page=0&size=20&search=` |
| Non-standard error responses | RFC 7807 `ProblemDetail` responses |
| Session-based auth | Stateless JWT Bearer token |

## Database Access Changes

| Before | After |
|--------|-------|
| {_db_before(tech_stack, src_db)} | {db_tech} |
| Raw SQL / string concatenation | Parameterised queries / ORM |
| No connection pooling | HikariCP / built-in pool |
| Hardcoded credentials | Environment variable injection |

## Anti-Pattern Fixes Applied

{_antipattern_fix_table(ap_dict, target)}
"""
    docs["ModernizedApp/API_CHANGES.md"] = api_doc

    return docs


# ── Documentation helpers ─────────────────────────────────────────────────────

# Function: _migration_action_list
def _migration_action_list(src_db: str, arch: dict, tech_stack: dict, target: dict) -> str:
    items = []
    lang = target.get("language", "java")
    if "oracle_db" in tech_stack:
        items += ["- Replace Oracle sequences/triggers with IDENTITY columns",
                  "- Replace VARCHAR2 → VARCHAR/NVARCHAR",
                  "- Replace NVL() → COALESCE()",
                  "- Replace SYSDATE → CURRENT_TIMESTAMP",
                  "- Replace ROWNUM pagination → LIMIT/OFFSET or pageable"]
    if "jpa_hibernate" in tech_stack or "hibernate" in tech_stack:
        items.append("- Update JPA/Hibernate entity annotations to Jakarta Persistence 3")
    if "jdbc" in tech_stack:
        items.append("- Replace raw JDBC with repository pattern (Spring Data / JPA)")
    if "asp_net_webforms" in tech_stack:
        items += ["- Replace code-behind classes with MVC controllers",
                  "- Replace WebForms controls with Razor/Blazor components"]
    if lang == "java":
        items += ["- Update `javax.*` imports to `jakarta.*`",
                  "- Replace `@Autowired` field injection with constructor injection",
                  "- Update Spring Boot parent to `3.x`",
                  "- Replace `Optional.get()` calls with `.orElseThrow()`",
                  "- Enable Java 21 virtual threads where applicable"]
    if not items:
        items = ["- Review each converted file for correctness",
                 "- Add unit tests for all service classes",
                 "- Configure environment variables for all secrets"]
    return "\n".join(items)


# Function: _build_folder_tree
# Function: _bft_walk
def _bft_walk(path: Path, prefix: str, depth: int, max_depth: int, max_files_per_dir: int, skip: set, lines: List[str]) -> None:
    if depth > max_depth:
        return
    try:
        entries = sorted(path.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
    except PermissionError:
        return
    dirs        = [e for e in entries if e.is_dir()  and e.name not in skip]
    files       = [e for e in entries if e.is_file()]
    shown_files = files[:max_files_per_dir]
    omitted     = len(files) - len(shown_files)
    all_entries = dirs + shown_files
    for i, entry in enumerate(all_entries):
        is_last   = (i == len(all_entries) - 1) and omitted == 0
        connector = "└── " if is_last else "├── "
        child_pfx = prefix + ("    " if is_last else "│   ")
        if entry.is_dir():
            lines.append(f"{prefix}{connector}{entry.name}/")
            _bft_walk(entry, child_pfx, depth + 1, max_depth, max_files_per_dir, skip, lines)
        else:
            size = entry.stat().st_size
            lines.append(f"{prefix}{connector}{entry.name}  ({size:,} B)")
    if omitted > 0:
        lines.append(f"{prefix}└── ... ({omitted} more files)")


# Function: _build_folder_tree
def _build_folder_tree(folder_path: str, max_depth: int = 5, max_files_per_dir: int = 8) -> str:
    """Build an ASCII folder tree for the given path."""
    root = Path(folder_path)
    if not root.exists():
        return "(folder not found)"
    lines: List[str] = [root.name + "/"]
    _SKIP = {".git", "__pycache__", ".idea", ".gradle", "node_modules",
             ".venv", "venv", "dist", "build", "target", "out", ".vs",
             "bin", "obj", ".mvn", "coverage", "TestResults"}

    _bft_walk(root, "", 0, max_depth, max_files_per_dir, _SKIP, lines)
    return "\n".join(lines)


# Function: _build_output_tree
# Function: _boft_build_tree
def _boft_build_tree(all_paths: List[str], converted_files: Dict[str, str]) -> dict:
    tree: dict = {}
    for p in all_paths:
        parts = Path(p).parts
        node = tree
        for part in parts[:-1]:
            node = node.setdefault(part, {})
        fname = parts[-1]
        node[fname] = len(converted_files[p])  # leaf = byte count
    return tree


# Function: _boft_render
def _boft_render(node: dict, prefix: str, lines2: List[str]) -> None:
    entries = sorted(node.items(), key=lambda x: (isinstance(x[1], dict), x[0].lower()))
    for i, (name, value) in enumerate(entries):
        is_last   = i == len(entries) - 1
        connector = "└── " if is_last else "├── "
        child_pfx = prefix + ("    " if is_last else "│   ")
        if isinstance(value, dict):
            lines2.append(f"{prefix}{connector}{name}/")
            _boft_render(value, child_pfx, lines2)
        else:
            lines2.append(f"{prefix}{connector}{name}  ({value:,} B)")


# Function: _build_output_tree
def _build_output_tree(converted_files: Dict[str, str]) -> str:
    """Build an ASCII folder tree from the converted output file paths."""
    # Build tree from all output paths
    all_paths = sorted(
        [k for k in converted_files.keys()
         if not k.endswith("conversion_log.json")]
    )
    tree = _boft_build_tree(all_paths, converted_files)

    lines2: List[str] = []
    if tree:
        root_name = next(iter(tree))
        lines2.append(root_name + "/")
        _boft_render(tree[root_name], "", lines2)
    return "\n".join(lines2) if lines2 else "(no files generated)"


# Function: _ascii_arch_before
def _ascii_arch_before(arch: dict, tech_stack: dict, lang_dist: dict) -> str:
    pattern = arch.get("pattern", "Legacy Application")
    db      = arch.get("database", "Unknown DB")
    langs   = ", ".join(list(lang_dist.keys())[:4])
    return (
        f"  ┌─────────────────────────────┐\n"
        f"  │  {pattern:<27}│\n"
        f"  │  Languages: {langs:<15}│\n"
        f"  │  Database:  {db:<15}│\n"
        f"  │  LOC:       {arch.get('total_loc', 0):<15,}│\n"
        f"  └─────────────────────────────┘"
    )


# Function: _ascii_arch_after
def _ascii_arch_after(target: dict) -> str:
    name = target.get("name", "Modern Stack")
    be   = target.get("backend_tech", "")[:27]
    fe   = target.get("frontend_tech", "")[:27]
    db   = target.get("db_tech", "")[:27]
    return (
        f"  ┌─────────────────────────────┐\n"
        f"  │  {name:<27}│\n"
        f"  │  Backend:  {be:<17}│\n"
        f"  │  Frontend: {fe:<17}│\n"
        f"  │  Database: {db:<17}│\n"
        f"  └─────────────────────────────┘"
    )


# Function: _structural_changes
def _structural_changes(arch: dict, target: dict, tech_stack: dict) -> str:
    changes = []
    src = arch.get("pattern", "")
    tgt = target.get("name", "")
    if "WebForms" in src:
        changes.append("- **Presentation layer**: WebForms ASPX/code-behind → MVC Controllers + Views")
    if "Spring Boot" in tgt or "spring" in tech_stack:
        changes.append("- **Dependency injection**: Field @Autowired → Constructor injection")
        changes.append("- **Packaging**: Fat JAR with embedded Tomcat")
        changes.append("- **Configuration**: application.properties → application.yml with profiles")
    if "JPA" in tgt or "jpa_hibernate" in tech_stack:
        changes.append("- **Database access**: JDBC/raw SQL → Spring Data JPA repositories")
    changes.append("- **Error handling**: Centralised `@ControllerAdvice` / `ExceptionHandler`")
    changes.append("- **Logging**: SLF4J + Logback (structured JSON in production)")
    changes.append("- **Build**: Updated to latest Gradle/Maven wrapper with dependency locking")
    return "\n".join(changes) if changes else "- See CLASS_MIGRATION_MAP.md for file-level details"


# Function: _package_mapping_table
def _package_mapping_table(conv_log: List[dict], root_ns: str) -> str:
    seen: Dict[str, str] = {}
    for entry in conv_log:
        src = entry.get("source", "")
        out = entry.get("output", "")
        # extract package-level dirs
        src_pkg = "/".join(Path(src).parts[:3])
        out_pkg = "/".join(Path(out).parts[:4])
        if src_pkg not in seen:
            seen[src_pkg] = out_pkg
    rows = [f"| `{k}` | `{v}` |" for k, v in list(seen.items())[:20]]
    return "\n".join(rows) or "| (packages not detected) | |"


# Function: _source_api_style
def _source_api_style(arch: dict, tech_stack: dict) -> str:
    if "asp_net_webforms" in tech_stack:
        return "ASP.NET WebForms — code-behind page model, ViewState, postbacks"
    if "asp_net_mvc" in tech_stack:
        return "ASP.NET MVC — ActionResult controllers, Razor views"
    if "spring" in tech_stack:
        return "Spring MVC — `@Controller`/`@RestController` with `@RequestMapping`"
    if "java_ee" in tech_stack:
        return "Java EE Servlets or EJB Remote interfaces"
    if "java_standard" in tech_stack:
        return "Plain Java classes / command-line / no web framework"
    return arch.get("pattern", "Legacy API style")


# Function: _target_api_style
def _target_api_style(target: dict) -> str:
    lang = target.get("language", "java")
    name = target.get("name", "")
    if lang == "java":
        return ("Spring Boot 3 REST API — `@RestController`, `@GetMapping`/`@PostMapping`, "
                "Spring Data JPA repositories, paginated responses")
    if lang == "csharp":
        return "ASP.NET Core 8 Minimal API — `MapGet`/`MapPost`, EF Core DbContext, TypedResults"
    if lang == "python":
        return "FastAPI async endpoints — Pydantic v2 schemas, SQLAlchemy 2, Alembic migrations"
    if lang in ("typescript", "javascript"):
        return f"{name} — REST client, TypeScript interfaces, paginated fetch hooks"
    return f"{name} REST API"


# Function: _db_before
def _db_before(tech_stack: dict, src_db: str) -> str:
    if "oracle_db" in tech_stack:
        return "Oracle DB via OracleDataAdapter/OracleCommand"
    if "jdbc" in tech_stack:
        return "JDBC raw queries"
    if "jpa_hibernate" in tech_stack:
        return "Hibernate/JPA (legacy version)"
    if "ado_net_raw" in tech_stack:
        return "ADO.NET DataAdapter/DataSet"
    return src_db or "Unknown DB access"


# Function: _antipattern_fix_table
def _antipattern_fix_table(ap_dict: Dict[str, int], target: dict) -> str:
    fix_map = {
        "hardcoded_password":          "→ Environment variable / secrets manager",
        "hardcoded_connection_string":  "→ Environment variable / connection factory",
        "sql_concatenation":            "→ Parameterised queries / ORM repository",
        "magic_number":                 "→ Named constants / enums",
        "large_method":                 "→ Decomposed into focused service methods",
    }
    rows = []
    for ap, count in ap_dict.items():
        fix = fix_map.get(ap, "→ Refactored in modernized code")
        rows.append(f"| `{ap}` ({count}×) | {fix} |")
    if not rows:
        return "_No anti-patterns detected._"
    header = "| Anti-Pattern | Fix Applied |\n|---|---|\n"
    return header + "\n".join(rows)


# ─── Guide text helper ───────────────────────────────────────────────────────

# Function: _guide_section
def _guide_section(guide_text: str) -> str:
    """Return a formatted guide/reference documentation block for LLM prompts."""
    if not guide_text or not guide_text.strip():
        return ""
    snippet = guide_text.strip()[:20000]
    return (
        "\n\nREFERENCE DOCUMENTATION / GUIDE PROVIDED BY USER:\n"
        "Use the following specification to ensure accurate naming, business logic, field names,\n"
        "domain rules, and API design. ALL generated code MUST align precisely with this guide.\n"
        "---\n"
        f"{snippet}\n"
        "---\n"
        "End of reference guide. Align every class, method, field name, and API endpoint\n"
        "with the conventions and requirements stated above.\n"
    )


# ─── Source file reader (feeds actual code into LLM prompts) ─────────────────

# Function: _read_source_files
# Function: _rsf_relevance
def _rsf_relevance(p: Path, domain_lower: str) -> int:
    name = p.stem.lower()
    path_str = str(p).lower()
    score = 0
    if domain_lower in name:
        score += 10
    if domain_lower in path_str:
        score += 5
    # Prefer non-test files
    if "test" in name or "test" in path_str:
        score -= 3
    return score


# Function: _rsf_collect_files
def _rsf_collect_files(root: Path, exts: List[str], skip_dirs: set) -> List[Path]:
    source_files: List[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in skip_dirs]
        for fname in filenames:
            p = Path(dirpath) / fname
            if p.suffix.lower() in exts:
                source_files.append(p)
    return source_files


# Function: _rsf_read_one
def _rsf_read_one(f: Path, root: Path, remaining: int) -> Optional[str]:
    try:
        content = f.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return None
    try:
        rel_path = f.relative_to(root)
    except ValueError:
        rel_path = f.name
    if len(content) > remaining:
        content = content[:remaining] + "\n// ... (truncated for context window)"
    header = f"// ════ SOURCE FILE: {rel_path} ════"
    return f"{header}\n{content}"


# Function: _rsf_build_sections
def _rsf_build_sections(ranked: List[Path], root: Path, max_chars: int) -> List[str]:
    sections: List[str] = []
    total = 0
    for f in ranked:
        if total >= max_chars:
            break
        section = _rsf_read_one(f, root, max_chars - total)
        if section is None:
            continue
        sections.append(section)
        total += len(section)
    return sections


# Function: _read_source_files
def _read_source_files(
    folder_path: str,
    lang: str,
    domain: str,
    max_chars: int = _SRC_TRUNCATE_AT,
) -> str:
    """
    Read actual source files from the legacy project folder that are relevant
    to the given domain. Returns a combined string of file contents capped at
    max_chars, with file path headers so the LLM knows where each snippet came from.
    """
    if not folder_path:
        return ""
    root = Path(folder_path)
    if not root.exists():
        return ""

    ext_map: Dict[str, List[str]] = {
        "java":       [".java", ".kt"],
        "csharp":     [".cs"],
        "python":     [".py"],
        "typescript": [".ts", ".tsx"],
        "javascript": [".js", ".jsx"],
        "sql":        [".sql"],
    }
    ibmi_source_exts = [
        ".rpg", ".rpgle", ".sqlrpgle", ".clp", ".clle", ".dds",
        ".pf", ".lf", ".dspf", ".prtf", ".cpy",
    ]
    # `lang` is the target language. IBM i inputs must remain visible whether
    # the selected target is Java, .NET, Python, Go, or another stack.
    exts = list(dict.fromkeys(ext_map.get(lang, [".java", ".cs", ".py"]) + ibmi_source_exts))

    skip_dirs = {".git", "bin", "obj", "node_modules", "__pycache__",
                 ".venv", "venv", "dist", "build", "target", "out",
                 ".gradle", ".idea", "coverage", ".next"}

    source_files = _rsf_collect_files(root, exts, skip_dirs)
    if not source_files:
        return ""

    domain_lower = domain.lower()
    ranked = sorted(source_files, key=lambda p: _rsf_relevance(p, domain_lower), reverse=True)
    sections = _rsf_build_sections(ranked, root, max_chars)
    return "\n\n".join(sections)


# Function: _source_section
def _source_section(folder_path: str, lang: str, domain: str) -> str:
    """Return the source section block to inject into an LLM prompt."""
    code = _read_source_files(folder_path, lang, domain)
    if not code.strip():
        return ""
    return (
        "\n\nACTUAL SOURCE CODE TO MODERNIZE:\n"
        "The following are REAL source files from the legacy project. "
        "Your modernized output MUST faithfully transform this actual code — "
        "preserve all business logic, class names, method names, and field names "
        "while upgrading to the target technology stack. "
        "Do NOT generate generic boilerplate that ignores this source.\n"
        "─────────────────────────────────────────────────────────────\n"
        f"{code}\n"
        "─────────────────────────────────────────────────────────────\n"
    )
