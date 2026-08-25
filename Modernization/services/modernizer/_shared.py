# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Modernization — services/modernizer (_shared.py)
# Date: 2025-11-18
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

_LLM_CACHE_DIR = Path(tempfile.gettempdir()) / "modernization_llm_cache"
try:
    _LLM_CACHE_DIR.mkdir(parents=True, exist_ok=True)
except OSError:
    pass

# Domain-level generation cache — stores entire _llm_gen_domain() output dict
_DOM_CACHE_DIR = _LLM_CACHE_DIR / "domains"
try:
    _DOM_CACHE_DIR.mkdir(parents=True, exist_ok=True)
except OSError:
    pass
# TTL for domain cache entries (default 24 h, override with env var)
_DOM_CACHE_TTL = int(os.getenv("MODERNIZATION_DOM_CACHE_TTL", str(24 * 3600)))

_DEFAULT_EXT_FOR_LANG = {
    "python": ".py", "csharp": ".cs", "java": ".java", "typescript": ".ts", "sql": ".sql",
    "javascript": ".js", "c": ".c", "cpp": ".cpp", "cobol": ".cob",
    "php": ".php", "ruby": ".rb", "go": ".go",
    "rust": ".rs", "swift": ".swift", "kotlin": ".kt", "shell": ".sh",
    "r": ".r", "scala": ".scala", "clojure": ".clj", "haskell": ".hs",
    "lisp": ".lisp", "elixir": ".ex", "dart": ".dart", "julia": ".jl",
    "hcl": ".tf", "protobuf": ".proto", "fortran": ".f90", "ada": ".adb",
    "pascal": ".pas", "erlang": ".erl", "ocaml": ".ml", "prolog": ".pl",
    "abap": ".abap", "pli": ".pli", "rpg": ".rpgle", "jcl": ".jcl",
    "mumps": ".m", "natural": ".nsp", "progress4gl": ".p", "apex": ".cls",
    "yaml": ".yaml", "json": ".json", "toml": ".toml", "xml": ".xml",
    "graphql": ".graphql", "dockerfile": ".dockerfile",
    "cloudformation": ".yaml", "kubernetes": ".yaml", "helm": ".yaml",
    "ansible": ".yaml", "github_actions": ".yaml", "jenkinsfile": ".jenkinsfile",
    "markdown": ".md",
}

# ─── Code-generation constants (replaces scattered magic numbers) ─────────────

# User-facing label for progress messages like "LLM (qwen3.5:9b): generating
# single complete file…" — shown as "LLM (Open Source)" instead of the raw
# Ollama model tag. This is cosmetic only: `llm_model` itself (the actual
# string passed to services.llm.generate()) is completely untouched
# everywhere else — only the text built for progress()/on_step() messages
# uses this label.
_LLM_DISPLAY_LABEL = "Open Source"

# LLM token budgets
_TOKENS_DEFAULT       = 4096
_TOKENS_LARGE         = 8192
_TOKENS_XLARGE        = 12_000
_TOKENS_COMPONENT     = 6_000
_TOKENS_MIGRATION     = 6_144

# Adaptive context window: chars-per-token estimate and safety margin
_CTX_SIZES            = (4096, 8192, 16_384, 32_768)
_CTX_SAFETY_MARGIN    = 512
_CTX_CHARS_PER_TOKEN  = 3

# Source content / reference-file size limits
_SRC_MAX_CHARS        = 14_000
_SRC_TRUNCATE_AT      = 12_000
_REF_FILE_MAX_CHARS   = 2_000
_REF_FILE_MIN_BYTES   = 300
_REF_FILE_MAX_BYTES   = 2_500

# Structure-extraction / string limits
_MAX_STRUCT_ITEMS     = 60
_MAX_STACK_NAME_LEN   = 120
_STRUCT_LINE_LONG     = 110
_STRUCT_LINE_SHORT    = 80
_STRUCT_LINE_MED      = 100

# Pagination / generation defaults
_DEFAULT_PAGE_SIZE    = 20
_DEFAULT_DOM_WORKERS  = 5
_DEFAULT_FILE_WORKERS = 5
_MAX_PLAN_FILES       = 18
_PLAN_PROMPT_MAX_TOKENS = 800
_EXPLICIT_MANIFEST_LIMIT = 160

# Legitimate filenames with no extension — allow-listed so the file-plan
# parser's "must have an extension" check (added to reject bare section
# headers like a lone "/Backend" line) doesn't also reject these.
_EXTENSIONLESS_FILENAMES = {
    "Dockerfile", "Makefile", "Procfile", "LICENSE", "Jenkinsfile",
    "Vagrantfile", "Rakefile", "Gemfile",
}

# How often (in streamed tokens) a streaming generate() call reports
# incremental progress — high enough to avoid flooding the SSE queue,
# low enough that the bar visibly moves during a multi-minute call.
_STREAM_PROGRESS_EVERY_TOKENS = 8

# Per-call wall-clock ceiling for targeted single-file repair/closure LLM
# calls (compiler-error repair, cross-module boundary rewrites, missing-
# contract closure files) — deliberately smaller than a full first-draft
# generation, since these calls rewrite one already-modest file rather than
# author a new project from scratch. Env-overridable for slower hardware.
_REPAIR_CALL_MAX_SECONDS = float(os.getenv("MODERNIZATION_REPAIR_CALL_MAX_SECONDS", "300"))

# One aggregate wall-clock budget for a Java file's initial draft plus any
# syntax-repair attempts.  This is intentionally Java-specific: the regression
# came from Java files multiplying the transport retry ceiling by the validator
# retry count (up to 3 x 3 calls), while other language pipelines retain their
# established timeout behavior.
_JAVA_FILE_GENERATION_MAX_SECONDS = float(
    os.getenv("MODERNIZATION_JAVA_FILE_GENERATION_MAX_SECONDS", "300")
)

# Round budget for the initial per-file generation wave, where individual
# `generate()` calls are deliberately left uncapped (a first-draft file can
# legitimately be large and slow on modest hardware). This is a pure safety
# net: generous enough to never trip on a real, working generation, but
# still finite so the round — and the job — always reaches closure even if
# one file's call genuinely never returns.
_WAVE_ROUND_BUDGET_SECONDS = float(os.getenv("MODERNIZATION_WAVE_ROUND_BUDGET_SECONDS", "1800"))


# Function: _round_budget_seconds
def _round_budget_seconds(item_count: int, workers: int, call_budget_seconds: float,
                           margin_seconds: float = 60.0) -> float:
    """Worst-case wall-clock budget for a parallel round of bounded LLM calls.

    `workers` process `item_count` items in ceil(item_count / workers)
    sequential batches; if every call in the round took the full per-call
    ceiling, the round would take that many batches times the ceiling. Adding
    a fixed margin absorbs prompt-build/progress overhead so the round budget
    itself is never the tight constraint — `call_budget_seconds` already is.
    """
    if item_count <= 0 or workers <= 0:
        return margin_seconds
    batches = -(-item_count // workers)  # ceil division without importing math
    return batches * call_budget_seconds + margin_seconds


# Function: _run_bounded_round
def _run_bounded_round(executor, futures: dict, *, round_budget_seconds: float, label: str):
    """Wait for a parallel batch of futures without ever blocking indefinitely.

    A ThreadPoolExecutor used as a context manager joins every submitted
    thread on `__exit__`, and `as_completed()` with no timeout waits forever
    for the slowest future. Together those mean a single LLM call that hangs
    — or is merely far slower than the rest of the batch — blocks the entire
    round, and therefore the whole generation job, from ever reaching
    completion. This bounds the wait explicitly: whatever hasn't finished
    within `round_budget_seconds` is abandoned (its thread may still be
    running in the background — Python cannot forcibly kill it — but nothing
    waits on it any longer) so the caller can move on and the job can still
    close out.

    `futures` maps each submitted future to a caller-defined key (typically a
    file path). Returns `(done, timed_out)`:
      - `done`: the subset of `futures` that finished within budget. Callers
        still call `.result()` on each to get the value or raised exception.
      - `timed_out`: {key: message} for every future abandoned past budget.
    """
    from concurrent.futures import wait as _wait
    done, not_done = _wait(futures, timeout=max(1.0, round_budget_seconds))
    # shutdown(wait=False) does not block on stragglers still running in the
    # executor's threads — only on submitting no further work to it.
    executor.shutdown(wait=False, cancel_futures=True)
    timed_out = {}
    if not_done:
        keys = sorted(str(futures[f]) for f in not_done)
        logger.error(
            "%s: %d/%d worker(s) exceeded the %.0fs round budget and were "
            "abandoned so the job can still reach completion: %s",
            label, len(not_done), len(futures), round_budget_seconds,
            ", ".join(keys[:8]),
        )
        for f in not_done:
            timed_out[futures[f]] = (
                f"{label} exceeded the {round_budget_seconds:.0f}s round budget "
                "and was abandoned; prior content was kept"
            )
    return {f: futures[f] for f in done}, timed_out


# Function: _streaming_progress_cb
def _streaming_progress_cb(progress_fn, phase: str, pct_start: int, pct_end: int,
                            max_tokens: int, label: str):
    """Build an on_token callback that moves the progress bar smoothly from
    pct_start to pct_end as a single LLM call streams its response, instead
    of the bar sitting frozen at pct_start for the entire call.

    Interpolates by estimated output size (chars generated so far vs. the
    call's max_tokens budget, using the codebase's own ~3-chars/token
    estimate) — an approximation, since the model may stop well short of
    max_tokens, but it turns a frozen bar into a moving one.
    """
    state = {"chars": 0, "tokens": 0}
    target_chars = max(max_tokens * _CTX_CHARS_PER_TOKEN, 1)

    # Function: _on_token
    def _on_token(token: str) -> None:
        state["chars"] += len(token)
        state["tokens"] += 1
        if state["tokens"] % _STREAM_PROGRESS_EVERY_TOKENS != 0:
            return
        frac = min(0.97, state["chars"] / target_chars)  # reserve the last stretch for completion
        pct = pct_start + int(frac * (pct_end - pct_start))
        estimated_tokens = max(1, state["chars"] // _CTX_CHARS_PER_TOKEN)
        progress_fn(
            phase,
            min(max(pct, pct_start + 1), pct_end),
            f"{label} ({estimated_tokens:,} tokens generated)",
        )

    return _on_token


# ─── Performance helpers ──────────────────────────────────────────────────────

# Function: _adaptive_num_ctx
def _adaptive_num_ctx(prompt_chars: int, max_output_tokens: int = _TOKENS_DEFAULT) -> int:
    """
    Return the smallest Ollama context window that fits the request.
    Smaller windows load the KV cache faster and speed up generation.
    Rule of thumb: ~3 chars per token in source code.
    """
    needed = (prompt_chars // _CTX_CHARS_PER_TOKEN) + max_output_tokens + _CTX_SAFETY_MARGIN
    for ctx in _CTX_SIZES:
        if ctx >= needed:
            return ctx
    return 32768


# Function: _adaptive_max_tokens
def _adaptive_max_tokens(src_content: str, src_lang: str, tgt_lang: str) -> int:
    """
    Estimate conservative output token budget from source size.
    Avoids allocating an 8192-token budget for a 30-line DTO.
    """
    lines = src_content.count('\n') + 1
    # C# is ~20% more verbose than Java; Python/TS similar to source
    verbosity = 1.25 if tgt_lang == "csharp" else 1.1
    # ~15 tokens per source line is a reasonable estimate
    est = int(lines * 15 * verbosity)
    # Clamp: never below 1024 (handles boilerplate) or above _TOKENS_LARGE
    return max(1024, min(_TOKENS_LARGE, est + _CTX_SAFETY_MARGIN))


# ─── Path / namespace helpers ────────────────────────────────────────────────

# Function: _component_to_pascal
def _component_to_pascal(s: str) -> str:
    """Convert a Java package component or hyphenated folder name to PascalCase."""
    return "".join(w.capitalize() for w in re.split(r"[-_]+", s) if w)


_ORG_PREFIXES = {
    "com", "org", "net", "io", "edu", "gov", "co",
    "one", "de", "uk", "fr", "be", "nl", "cn", "jp",
}


# Function: _derive_root_namespace
def _derive_root_namespace(namespaces: List[str], folder_path: str = "") -> str:
    """
    Derive the C# root namespace from a list of Java package declarations.
    Finds the dominant prefix (merging short TLD-style first-level words with
    the next component) and returns it in PascalCase.
    e.g.  ["one.microproject.proxy", "one.microproject.files"] → "OneMicroproject"
          ["itx.examples.records"]                             → "Itx"
    """
    from collections import Counter
    prefix_counts: "Counter[str]" = Counter()
    for ns in namespaces:
        parts_ns = [p for p in ns.split(".") if p]
        if not parts_ns:
            continue
        if parts_ns[0].lower() in _ORG_PREFIXES and len(parts_ns) > 1:
            # Merge first two: "one" + "microproject" → "OneMicroproject"
            key = parts_ns[0].capitalize() + parts_ns[1].capitalize()
        else:
            key = parts_ns[0].capitalize()
        prefix_counts[key] += 1

    if not prefix_counts:
        name = Path(folder_path).name if folder_path else "App"
        return "".join(w.capitalize() for w in re.split(r"[-_\s]+", name) if w) or "App"

    return prefix_counts.most_common(1)[0][0]


# Function: _make_csharp_output_rel
def _make_csharp_output_rel(stripped: List[str], preserve_ext: bool, tgt_ext: str) -> str:
    # PascalCase each directory component — preserves Java package hierarchy
    # and avoids collisions when multiple sub-modules have same filename (e.g. Main.java)
    pascal_dirs = [_component_to_pascal(p) for p in stripped[:-1]]
    if preserve_ext:
        return "ModernizedApp/src/" + "/".join(pascal_dirs + [stripped[-1]])
    return "ModernizedApp/src/" + "/".join(
        pascal_dirs + [Path(stripped[-1]).stem + tgt_ext]
    )


# Function: _make_output_path
def _make_output_path(
    src_path: Path,
    folder_root: Path,
    target_lang: str,
    root_ns: str,
    target_stack: str,
) -> str:
    """
    Map a source file path to its output path inside ModernizedApp/.
    Preserves the directory structure mirrored under the appropriate service layout.
    """
    from .conversion_pipeline import _target_ext_for_lang
    try:
        rel = src_path.relative_to(folder_root)
    except ValueError:
        rel = Path(src_path.name)

    parts = list(rel.parts)
    src_ext = src_path.suffix.lower()
    tgt_ext = _target_ext_for_lang(target_lang)
    # IBM i projects commonly reuse the same member name across RPG, CL, PF,
    # LF and DSPF source files. A blind extension swap would overwrite all of
    # them as e.g. ORDER.java. Preserve the source role in the modern filename.
    ibmi_roles = {
        ".rpg": "RpgProgram", ".rpgle": "RpgProgram", ".sqlrpgle": "SqlRpgProgram",
        ".clp": "ClProgram", ".clle": "ClProgram", ".dds": "DdsSchema",
        ".pf": "PhysicalFile", ".lf": "LogicalFile", ".dspf": "DisplayFile",
        ".prtf": "PrinterFile", ".cpy": "Copybook",
    }
    legacy_roles = {
        ".cob": "CobolProgram", ".cbl": "CobolProgram",
        ".f": "FortranUnit", ".for": "FortranUnit", ".f90": "FortranUnit",
        ".f95": "FortranUnit", ".pas": "PascalUnit", ".pp": "PascalUnit",
        ".dpr": "DelphiProgram", ".pli": "PliProgram", ".pl1": "PliProgram",
        ".jcl": "JclJob", ".m": "MumpsRoutine", ".nsp": "NaturalProgram",
        ".nat": "NaturalProgram", ".p": "AblProgram", ".adb": "AdaBody",
        ".ads": "AdaSpec", ".ml": "OcamlModule", ".mli": "OcamlInterface",
        ".pro": "PrologRules", ".pl": "PrologRules",
    }
    source_roles = {**ibmi_roles, **legacy_roles}
    if src_ext in source_roles and parts:
        source_name = Path(parts[-1])
        parts[-1] = f"{source_name.stem}{source_roles[src_ext]}{src_ext}"
    # Config/resource files keep their original extension (not converted to .java/.cs etc.)
    _config_exts = {".xml", ".yaml", ".yml", ".properties", ".json", ".toml",
                    ".html", ".htm", ".css", ".md", ".txt", ".sql"}
    preserve_ext = src_ext in _config_exts

    if target_lang == "java":
        stripped = _strip_source_root(parts)
        out_rel  = "ModernizedApp/src/main/java/" + "/".join(stripped)
        out_rel  = out_rel if preserve_ext else _swap_ext(out_rel, tgt_ext)
    elif target_lang == "csharp":
        stripped = _strip_source_root(parts)
        out_rel = _make_csharp_output_rel(stripped, preserve_ext, tgt_ext)
    elif target_lang == "sql":
        out_rel = "ModernizedApp/Database/" + "/".join(parts)
    else:
        # Covers typescript/javascript/python and any other target — all use
        # the same flat "ModernizedApp/src/<mirrored path>" layout.
        stripped = _strip_source_root(parts)
        out_rel  = "ModernizedApp/src/" + "/".join(stripped)
        out_rel  = out_rel if preserve_ext else _swap_ext(out_rel, tgt_ext)

    return out_rel


# Function: _strip_source_root
def _strip_source_root(parts: List[str]) -> List[str]:
    """
    Remove common source root prefixes (src/main/java, src/, etc.).
    Searches the ENTIRE path so multi-module projects like
    `examples/entropy-demo/src/main/java/com/...` are stripped to `com/...`.
    """
    prefixes = [
        ["src", "main", "java"],
        ["src", "main", "kotlin"],
        ["src", "main", "groovy"],
        ["src", "main"],
        ["src", "test", "java"],
        ["src", "test", "kotlin"],
        ["src", "test"],
        ["src"],
        ["source"],
        ["sources"],
        ["main"],
        ["app"],
    ]
    lower = [p.lower() for p in parts]
    # Longest-match first: search anywhere in the path
    for prefix in prefixes:
        plen = len(prefix)
        for i in range(len(lower) - plen + 1):
            if lower[i:i + plen] == prefix:
                tail = parts[i + plen:]
                if tail:  # don't strip everything
                    return tail
    return parts


# Function: _swap_ext
def _swap_ext(path_str: str, new_ext: str) -> str:
    p = Path(path_str)
    return str(p.with_suffix(new_ext))
