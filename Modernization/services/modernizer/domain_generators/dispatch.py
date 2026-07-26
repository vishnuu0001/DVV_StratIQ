# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Modernization — services/modernizer/domain_generators (dispatch.py)
# Date: 2025-09-09
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

_OLLAMA_SOURCE_SUFFIXES = {
    ".cs", ".java", ".kt", ".kts", ".ts", ".tsx", ".js", ".jsx", ".go",
    ".rs", ".php", ".dart", ".swift", ".scala", ".clj", ".r", ".jl", ".hs",
    ".lisp", ".rpgle", ".clle", ".sql", ".sh", ".py", ".html", ".css",
    ".c", ".cpp", ".cc", ".cxx", ".cob", ".cbl", ".rb",
    ".ex", ".exs", ".erl",
}


# Function: _ollama_generate_all_sources
def _ollama_generate_all_sources(
    files: Dict[str, str], target: dict, domain: str, model: str, system: str,
    on_step, on_validation,
    *, user_request: str = "", contracts: str = "", namespace_map: str = "",
    required_elements: str = "", file_manifest: str = "",
) -> None:
    """Regenerate every executable/source artifact through Ollama.

    Deterministic content is used only as an exact framework/file contract.
    It is never returned as application source without a successful validated
    Ollama response.
    """
    from .._shared import _TOKENS_DEFAULT, _adaptive_num_ctx
    from ..validation_orchestration import _generate_validated

    generated_paths = []
    for rel_path, contract in list(files.items()):
        if Path(rel_path).suffix.casefold() not in _OLLAMA_SOURCE_SUFFIXES:
            continue
        if on_step:
            on_step(f"[{domain}] Ollama generating {rel_path}…")
        project_contract = "\n\n".join(
            f"{heading}:\n{value.strip()}"
            for heading, value in (
                ("ORIGINAL USER REQUIREMENTS (authoritative; do not omit or weaken)", user_request),
                ("PROJECT CONTRACTS (authoritative across every file)", contracts),
                ("NAMESPACE / SYMBOL LOCATION MAP", namespace_map),
                ("CROSS-CUTTING REQUIRED ELEMENTS", required_elements),
                ("COMPLETE PROJECT FILE MANIFEST", file_manifest),
            )
            if value and value.strip()
        )
        prompt = (
            f"Generate the complete production-ready contents of {rel_path} for "
            f"{target.get('name', 'the selected target stack')}.\n"
            "The contract below defines required framework APIs, imports, public behavior, "
            "and integration points. Preserve those requirements, but implement the file "
            "fully and idiomatically. Do not emit markdown fences, prose, TODOs, placeholders, "
            "or comments claiming generation failed. This file is one part of a governed "
            "project: all types, endpoints, dependencies, events, configuration, security, "
            "observability, persistence, and tests must remain consistent with the project "
            "contracts. Never replace a requested production integration with an in-memory "
            "stub or illustrative implementation. Implement only the responsibility assigned "
            "to this exact path. Do not copy project-wide concerns into every file: bootstrap "
            "classes must not contain controller, Kafka listener/publisher, persistence, or "
            "test behavior when the manifest assigns those concerns elsewhere. Import only "
            "symbols actually used by this file.\n\n"
            f"{project_contract}\n\n"
            f"FILE CONTRACT:\n{contract}"
        )
        content, result, attempts = _generate_validated(
            prompt, model=model, system=system, max_tokens=_TOKENS_DEFAULT,
            num_ctx=_adaptive_num_ctx(len(prompt) + len(system), _TOKENS_DEFAULT),
            rel_path=rel_path, language=target.get("language", ""),
            on_attempt=(
                (lambda attempt, maximum, path=rel_path:
                    on_step(f"Ollama repairing {path} — attempt {attempt}/{maximum}…"))
                if on_step else None
            ),
        )
        files[rel_path] = content
        generated_paths.append(rel_path)
        if on_validation:
            on_validation(result, attempts)

    first_source = generated_paths[0] if generated_paths else next(iter(files), "ModernizedApp")
    project_root = first_source.replace("\\", "/").split("/", 1)[0] or "ModernizedApp"
    files[f"{project_root}/.strat-aqorynth/ollama-{domain.lower()}-provenance.json"] = json.dumps({
        "generator": "ollama",
        "model": model,
        "target": target.get("name"),
        "domain": domain,
        "source_files": generated_paths,
    }, indent=2)



# Function: _detect_frontend_framework
def _detect_frontend_framework(frontend_tech: str) -> Optional[str]:
    """Map a frontend_tech string to the _llm_domain_typescript framework
    label. Was previously keyed off target['db_target'] (always "postgres"
    for react_ts/angular_ts/vue3 — a stale key that never matched any of
    the three, so every preset silently fell back to "React", including
    Angular and Vue), which is why selecting Angular still produced React
    code. Reading frontend_tech directly is correct for every preset and
    for the auto-detected overrides from _apply_stack_signals.
    """
    low = (frontend_tech or "").lower()
    if "angular" in low:
        return "Angular"
    if "vue" in low:
        return "Vue 3"
    if "react" in low:
        return "React"
    return None


# Function: _dispatch_backend_generation
def _dispatch_backend_generation(
    lang, files, domain, root_ns, domain_tables, antipatterns,
    context, prod_rules, source_sec, guide_sec,
    model, system, tables, target, on_step, generate, on_validation,
) -> None:
    from .csharp import _llm_domain_csharp
    from .go import _llm_domain_go
    from .java import _llm_domain_java
    from .python_gen import _llm_domain_python
    from .typescript import _llm_domain_typescript
    if lang == "java":
        _llm_domain_java(
            files, domain, root_ns, domain_tables, antipatterns,
            context, prod_rules, source_sec, guide_sec,
            model, system, tables, target, on_step, generate, on_validation,
        )
    elif lang in ("typescript", "javascript"):
        fw = _detect_frontend_framework(target.get("frontend_tech", "")) or "React"
        _llm_domain_typescript(
            files, domain, root_ns, domain_tables,
            context, prod_rules, source_sec, guide_sec,
            model, system, fw, target, on_step, generate, on_validation,
        )
    elif lang == "go":
        _llm_domain_go(
            files, domain, root_ns, domain_tables,
            context, prod_rules, target.get("backend_tech", ""),
            model, system, tables, on_step, generate, on_validation,
        )
    elif lang == "python":
        _llm_domain_python(
            files, domain, root_ns, domain_tables,
            context, prod_rules,
            model, system, tables, on_step, generate, on_validation,
        )
    elif lang == "csharp":
        _llm_domain_csharp(
            files, domain, root_ns, domain_tables, antipatterns,
            context, prod_rules, source_sec,
            model, system, tables, target, on_step, generate, on_validation,
        )
    else:
        # Do not silently emit C# for a guided non-C# target.  A deterministic
        # language-correct vertical slice is preferable to cross-language output
        # and remains available when the local model is offline.
        from ..scaffolds.polyglot import generate_polyglot_project
        files.update(generate_polyglot_project(lang, root_ns, domain, target))


# Function: _maybe_generate_frontend
def _maybe_generate_frontend(
    lang, target, files, domain, root_ns, domain_tables,
    context, prod_rules, source_sec, guide_sec,
    model, system, on_step, generate, on_validation,
) -> None:
    # A backend language choice (csharp/java/python) says nothing about the
    # frontend framework — "Angular frontend + .NET backend" is a common,
    # valid combination that the old per-language dispatch above couldn't
    # express (lang picks exactly one branch). lang in ("typescript",
    # "javascript") already generated its own frontend in
    # _dispatch_backend_generation and must not be duplicated here.
    from .typescript import _llm_domain_typescript
    from ..scaffolds.csharp import _gen_aveva_js_module, _gen_frontend
    if lang in ("typescript", "javascript"):
        return
    fw = _detect_frontend_framework(target.get("frontend_tech", ""))
    if fw:
        if on_step:
            on_step(f"[{domain}] Generating {fw} frontend…")
        _llm_domain_typescript(
            files, domain, root_ns, domain_tables,
            context, prod_rules, source_sec, guide_sec,
            model, system, fw, target, on_step, generate, on_validation,
        )
    elif lang == "csharp":
        if target.get("name", "").startswith("AVEVA"):
            _gen_aveva_js_module(files, root_ns, domain)
        else:
            _gen_frontend(files, root_ns, domain)


# Function: _llm_gen_domain
def _llm_gen_domain(
    domain: str,
    target: dict,
    analysis: dict,
    root_ns: str,
    tables: List[str],
    guide_text: str = "",
    model: Optional[str] = None,
    on_step: Optional[Callable[[str], None]] = None,
    on_validation: Optional[Callable[[object, int], None]] = None,
) -> Dict[str, str]:
    """Call LLM to generate core service code for one domain. Falls back to templates."""

    # ── Domain-level result cache (content-addressed, TTL=24h by default) ────
    from ..conversion_pipeline import _dom_cache_key, _load_dom_cache, _save_dom_cache
    from ..docs_generation import _guide_section, _source_section
    from ..prompt_pipeline import _safe_build_system_prompt
    from ..target_config import _stack_profiles_for
    _cache_key = _dom_cache_key(domain, target, root_ns, tables, analysis)
    _cached = _load_dom_cache(_cache_key)
    if _cached:
        logger.info("Domain cache HIT: %s / %s (skipping LLM)", domain, target.get("name", ""))
        return _cached

    try:
        from services.llm import generate, check_status, pick_codegen_model
        if not model:
            llm_info = check_status()
            if not llm_info.get("available"):
                raise RuntimeError("LLM not available")
            model = pick_codegen_model()  # fast VRAM-resident model, not the forced status default
            if not model:
                raise RuntimeError("No code-generation model available")
    except Exception as exc:
        raise RuntimeError(
            "Ollama code generation is required and no usable model is available"
        ) from exc

    lang         = target.get("language", "csharp")
    stack_name   = target["name"]
    persona      = target.get("llm_persona", f"a {stack_name} expert")
    arch         = analysis.get("architecture", {})
    folder_path  = analysis.get("folder_path", "")
    source       = arch.get("pattern", "Legacy application")
    techs        = ", ".join(arch.get("detected_techs", []) or ["unknown"])
    loc          = arch.get("total_loc", 0)
    antipatterns = [i["type"] for i in analysis.get("antipatterns", [])[:5]]
    domain_tables = [t for t in tables if domain.lower() in t.lower()] or tables[:3]

    guide_sec  = _guide_section(guide_text)
    source_sec = _source_section(folder_path, lang, domain)

    context = (
        f"Source project: {source} | Technologies: {techs} | LOC: {loc:,}\n"
        f"Domain: {domain} | Relevant tables: {', '.join(domain_tables) or 'N/A'}\n"
        f"Anti-patterns to fix: {', '.join(antipatterns) or 'none detected'}\n"
        f"Target: {stack_name}"
    )
    prod_rules = (
        "PRODUCTION CODE RULES (mandatory):\n"
        "- COMPLETE implementation of every method \u2014 no empty bodies, no TODOs, no stubs\n"
        "- Full error handling with specific exception types and meaningful messages\n"
        "- Input validation on all public API entry points\n"
        "- Structured logging (info on success, warn on not-found, error on exceptions)\n"
        "- All configuration (DB URL, credentials, ports) from environment variables\n"
        "- Proper HTTP status codes: 200 OK, 201 Created, 204 No Content, 400 Bad Request, "
        "404 Not Found, 409 Conflict, 500 Internal Server Error\n"
        "- No hardcoded credentials or connection strings anywhere in the code"
    )
    system = _safe_build_system_prompt(_stack_profiles_for(lang, target), f"You are {persona}.")

    from ..scaffolds.polyglot import generate_polyglot_project
    files: Dict[str, str] = generate_polyglot_project(lang, root_ns, domain, target)
    stack_text = f"{target.get('name', '')} {target.get('backend_tech', '')}".casefold()
    is_special_typescript = lang == "typescript" and any(
        value in stack_text for value in ("nestjs", "next.js")
    )

    if not is_special_typescript:
        _dispatch_backend_generation(
            lang, files, domain, root_ns, domain_tables, antipatterns,
            context, prod_rules, source_sec, guide_sec,
            model, system, tables, target, on_step, generate, on_validation,
        )
        _maybe_generate_frontend(
            lang, target, files, domain, root_ns, domain_tables,
            context, prod_rules, source_sec, guide_sec,
            model, system, on_step, generate, on_validation,
        )

    _ollama_generate_all_sources(
        files, target, domain, model, system, on_step, on_validation,
        user_request="\n\n".join(part for part in (context, prod_rules, source_sec, guide_sec) if part),
        required_elements=prod_rules,
        file_manifest="\n".join(sorted(files)),
    )

    # ── Persist to domain cache so repeat runs skip all LLM calls ────────────
    _save_dom_cache(_cache_key, files)
    return files  # end _llm_gen_domain
