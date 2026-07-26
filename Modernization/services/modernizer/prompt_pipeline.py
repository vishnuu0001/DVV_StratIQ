# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Modernization — services/modernizer (prompt_pipeline.py)
# Date: 2025-12-18
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



# Function: _required_prompt_baseline
def _required_prompt_baseline(
    target: dict,
    project_name: str,
    signals: Dict[str, Optional[str]],
    user_prompt: str = "",
) -> List[str]:
    """Files that may never be omitted from a generated runnable application.

    The LLM may add feature-specific files, but it cannot remove entry points,
    framework roots, contracts, deployment files, or tests from this baseline.
    """
    from .domain_generators.stack_signals import _detect_domain_requirements
    required: List[str] = []
    lang = target.get("language", "csharp")
    if signals.get("backend") and lang == "csharp":
        required.extend([
            "backend/Program.cs",
            "backend/appsettings.json",
            "backend/appsettings.Development.json",
            "backend/Dockerfile",
        ])
        if _detect_domain_requirements(user_prompt):
            required.extend([
                "backend/DTOs/TransferRequestDto.cs",
                "backend/DTOs/TransactionResponseDto.cs",
                "backend/Domain/TransferStatus.cs",
                "backend/Domain/TransferOutcome.cs",
                "backend/Entities/Account.cs",
                "backend/Entities/Transaction.cs",
                "backend/Repositories/ITransactionRepository.cs",
                "backend/Repositories/TransactionRepository.cs",
                "backend/Services/ITransactionService.cs",
                "backend/Services/TransactionService.cs",
                "backend/Controllers/TransactionsController.cs",
                "database/schema.sql",
                "tests/backend/TransactionServiceTests.cs",
            ])
    if signals.get("frontend") and "angular" in target.get("frontend_tech", "").lower():
        required.extend([
            "frontend/src/app/app.component.ts",
            "frontend/src/app/app.component.html",
            "frontend/src/app/app.module.ts",
            "frontend/src/app/app-routing.module.ts",
            "frontend/src/app/core/services/auth.service.ts",
            "frontend/src/environments/environment.ts",
            "frontend/src/environments/environment.production.ts",
            "frontend/src/styles.css",
            "frontend/tsconfig.app.json",
            "frontend/Dockerfile",
            "frontend/nginx.conf",
        ])
        if _detect_domain_requirements(user_prompt):
            required.extend([
                "frontend/src/app/core/models/transaction.model.ts",
                "frontend/src/app/core/services/transaction.service.ts",
                "frontend/src/app/features/transactions/transaction-list.component.ts",
                "frontend/src/app/features/transactions/transaction-list.component.html",
                "frontend/src/app/features/transactions/transaction-list.component.css",
                "frontend/src/app/features/transactions/transfer-form.component.ts",
                "frontend/src/app/features/transactions/transfer-form.component.html",
                "frontend/src/app/features/transactions/transfer-form.component.css",
                "tests/frontend/transaction.service.spec.ts",
            ])
    return list(dict.fromkeys(required))


# Section headers used by the planning call's structured output (Phase 0) and
# by MANIFEST_VALIDATION_PROMPT's corrected document (Phase 0.5) — kept in one
# place so both phases parse with the exact same rules. FILES must stay last:
# its capture group is the only one allowed to run to end-of-string, and every
# other header is used as a terminator for the section before it.
_PLAN_SECTION_HEADERS = [
    "CONTRACTS", "CROSS-CUTTING CONCERNS", "SHARED CONFIG SHAPES",
    "FOLDER TAXONOMY", "NAMESPACE MAP", "FILES",
]


# Function: _parse_file_list_lines
def _parse_file_list_lines(text: str) -> List[str]:
    """Extract plausible file paths from a FILES-section body, one per line.
    A real file path ends in an extension (or is one of the few well-known
    extensionless filenames) — rejects bare section headers / directory names
    the model sometimes emits (e.g. a lone "/Backend" line), since generating
    "content" for a file with no extension/type has no natural stopping point
    and burns a full per-file token budget without producing anything usable.
    Shared by the initial plan parse and the Phase 0.5 manifest-validation
    parse so both apply identical filtering."""
    from ._shared import _EXTENSIONLESS_FILENAMES
    result: List[str] = []
    for line in text.splitlines():
        candidate = line.strip().lstrip("-•* 0123456789.)").strip("'\"").lstrip("/")
        basename = candidate.rsplit("/", 1)[-1]
        has_ext = bool(re.match(r"^[\w\-./]+\.[A-Za-z0-9]{1,10}$", candidate))
        is_known_extensionless = basename in _EXTENSIONLESS_FILENAMES
        if candidate and (has_ext or is_known_extensionless):
            result.append(candidate)
    return result


# Function: _parse_plan_sections
def _parse_plan_sections(text: str) -> Dict[str, str]:
    """Split a 'HEADER:\\n...\\n\\nNEXT HEADER:\\n...' formatted LLM response
    into {header: body}. Order-independent (each section is captured up to
    whichever OTHER known header appears next, or end of string) and tolerant
    of missing sections (a 7B model reliably skips headers it has nothing to
    say for) — generalizes the CONTRACTS:/FILES: split this function used to
    do inline so Phase 0 (initial plan) and Phase 0.5 (manifest validation's
    corrected document) share one parser instead of duplicating the regex."""
    others = "|".join(re.escape(h) for h in _PLAN_SECTION_HEADERS)
    result: Dict[str, str] = {h: "" for h in _PLAN_SECTION_HEADERS}
    for header in _PLAN_SECTION_HEADERS:
        m = re.search(
            rf"(?is){re.escape(header)}:\s*(.*?)(?=\n\s*(?:{others}):|\Z)",
            text,
        )
        if m:
            result[header] = m.group(1).strip()
    return result


# Function: _safe_build_system_prompt
def _safe_build_system_prompt(profiles: List[str], persona_line: str = "") -> str:
    """build_system_prompt() wrapper that never crashes generation — an
    unmapped/unknown profile name (or an empty list) falls back to the
    stack-neutral CORE_SYSTEM_PROMPT alone rather than raising KeyError and
    aborting the whole file/job over a profile-mapping gap."""
    from services.llm import build_system_prompt, CORE_SYSTEM_PROMPT
    try:
        body = build_system_prompt(profiles) if profiles else CORE_SYSTEM_PROMPT
    except KeyError:
        body = CORE_SYSTEM_PROMPT
    return f"{persona_line}\n{body}" if persona_line else body


# Function: _declared_dependencies_text
def _declared_dependencies_text(output: Dict[str, str], max_chars_each: int = 1500) -> str:
    """Collect the content of any dependency manifest already generated
    (package.json / pom.xml / requirements.txt / *.csproj) for
    PER_FILE_USER_TEMPLATE's {declared_dependencies} slot — SYSTEM_PROMPT
    rule C4 forbids using an undeclared package, but the model can only obey
    that if it's shown what's actually declared. Manifest files are
    themselves LLM-planned/generated files, so this may be empty early in a
    run — that's expected, not an error."""
    parts = []
    for path, content in output.items():
        base = path.rsplit("/", 1)[-1]
        if base in ("package.json", "pom.xml", "requirements.txt") or base.endswith(".csproj"):
            parts.append(f"--- {path} ---\n{content[:max_chars_each]}")
    return "\n\n".join(parts) if parts else "(none declared yet)"


# Function: _contract_digest
def _contract_digest(output: Dict[str, str], max_files: int = 12, max_chars_each: int = 700) -> str:
    """Summarize already-generated contract-defining files so later files
    reference the exact same class/field/method/endpoint names instead of
    drifting — each file is otherwise generated independently. This is the
    only thing standing between a controller calling AddTransactionAsync and
    a service that only defines CreateTransactionAsync.

    Interface files are matched by the C# convention (I + capital letter,
    e.g. "ITransactionRepository.cs") — matching the literal substring
    "interface" against the filename (the previous approach) never matches
    that naming convention and silently included nothing for it.
    """
    # Function: _is_interface
    def _is_interface(base: str) -> bool:
        return len(base) > 1 and base[0] == "I" and base[1].isupper()

    contract_kw = ("model", "entity", "dto", "schema", "contract", ".sql")
    impl_kw     = ("service", "repository", "controller", "context", "endpoint")

    priority: List[tuple] = []
    secondary: List[tuple] = []
    for fname, content in output.items():
        base = fname.rsplit("/", 1)[-1]
        if base.endswith(".md"):
            continue
        low = base.lower()
        if _is_interface(base) or any(k in low for k in contract_kw):
            priority.append((fname, content))
        elif any(k in low for k in impl_kw):
            secondary.append((fname, content))

    picked = (priority + secondary)[:max_files]
    if not picked:
        return ""
    parts = [
        "\n\nPREVIOUSLY GENERATED FILES YOU MUST STAY CONSISTENT WITH "
        "(exact same class/field/endpoint names — do not rename or reshape them):"
    ]
    for fname, content in picked:
        parts.append(f"--- {fname} ---\n{content[:max_chars_each]}")
    return "\n".join(parts) + "\n"


# Function: _path_format_examples
def _path_format_examples(lang: str, is_full_stack: bool, frontend_tech: str = "") -> str:
    """Concrete folder-qualified path examples shown to the LLM during file
    planning — a 7B model reliably ignores a prose instruction like "use
    folder-qualified paths" but follows a worked example. The frontend
    examples MUST match the actual requested framework: showing a React
    ".tsx" example for a requested Angular frontend is exactly what caused
    the model to emit React components for an Angular request in practice —
    the concrete example outweighs the "Frontend: Angular" line above it.
    """
    backend_examples = {
        "csharp": [
            "Controllers/UserController.cs", "Services/IUserService.cs", "Services/UserService.cs",
            "Repositories/IUserRepository.cs", "Repositories/UserRepository.cs", "Models/User.cs",
        ],
        "java": [
            "src/main/java/com/app/controller/UserController.java",
            "src/main/java/com/app/service/UserService.java",
            "src/main/java/com/app/repository/UserRepository.java",
            "src/main/java/com/app/model/User.java",
        ],
        "python": [
            "app/routers/users.py", "app/services/user_service.py",
            "app/repositories/user_repository.py", "app/models/user.py",
        ],
        "typescript": ["src/components/UserList.tsx", "src/services/userService.ts", "src/api/client.ts"],
        "javascript": ["src/components/UserList.jsx", "src/services/userService.js"],
    }
    lines = backend_examples.get(lang, backend_examples["csharp"])
    if is_full_stack:
        fw = (frontend_tech or "").lower()
        prefix = "frontend/" if lang != "typescript" and lang != "javascript" else ""
        if "angular" in fw:
            lines = lines + [
                f"{prefix}src/app/features/user/user-list.component.ts",
                f"{prefix}src/app/features/user/user-list.component.html",
                f"{prefix}src/app/core/services/user.service.ts",
            ]
        elif "vue" in fw:
            lines = lines + [f"{prefix}src/components/UserList.vue", f"{prefix}src/services/userService.ts"]
        else:  # React, or unspecified — React is the safe default JSX example
            lines = lines + [f"{prefix}src/components/UserList.tsx", f"{prefix}src/services/userService.ts"]
    lines = lines + ["Dockerfile"]  # docker-compose.yml and k8s/*.yaml are generated separately
    return "\n".join(f"  {p}" for p in lines)


# Function: _ensure_modular_path
# Function: _emp_nested_path
def _emp_nested_path(fname: str, lang: str, is_full_stack: bool) -> str:
    if (is_full_stack and lang in ("csharp", "java", "python")
            and not fname.startswith(("frontend/", "backend/", "database/", "tests/", "k8s/"))
            and fname not in ("docker-compose.yml", "README.md")):
        return f"backend/{fname}"
    return fname


# Function: _emp_is_frontend_file
def _emp_is_frontend_file(ext: str, lower: str) -> bool:
    frontend_exts = {".tsx", ".jsx", ".vue", ".html", ".css", ".scss"}
    return ext in frontend_exts or (
        ext == ".ts" and not any(k in lower for k in ("controller", "repository", "program", "startup"))
    )


# Function: _emp_frontend_path
def _emp_frontend_path(fname: str, lower: str, is_full_stack: bool) -> str:
    if any(k in lower for k in ("service", "client", "api")):
        folder = "src/services"
    elif any(k in lower for k in ("guard", "auth", "interceptor")):
        folder = "src/auth"
    elif any(k in lower for k in ("environment", "config")):
        folder = "src/environments"
    else:
        folder = "src/components"
    return f"{'frontend/' if is_full_stack else ''}{folder}/{fname}"


# Function: _emp_backend_path
def _emp_backend_path(fname: str, lower: str, ext: str, lang: str, is_full_stack: bool) -> str:
    if any(k in lower for k in ("test", "spec")):
        folder = "Tests"
    elif any(k in lower for k in ("controller", "endpoint", "route")):
        folder = "Controllers"
    elif any(k in lower for k in ("repository", "dao")):
        folder = "Repositories"
    elif "service" in lower:
        folder = "Services"
    elif any(k in lower for k in ("dbcontext", "connectionfactory", "dbconnection")):
        folder = "Data"
    elif any(k in lower for k in ("dto", "model", "entity", "schema", "response", "request")):
        folder = "Models"
    elif ext in (".json", ".yaml", ".yml", ".toml"):
        return f"{'backend/' if is_full_stack else ''}{fname}"
    else:
        return f"{'backend/' if is_full_stack else ''}{fname}"

    prefix = "backend/" if is_full_stack and lang in ("csharp", "java", "python") else ""
    return f"{prefix}{folder}/{fname}"


# Project-manifest / root-level files — never nested
_EMP_ROOT_NAMES = {
    "dockerfile", "docker-compose.yml", "docker-compose.yaml", ".env.example", ".env",
    "readme.md", "package.json", "package-lock.json", "tsconfig.json", "vite.config.ts",
    "angular.json", "pom.xml", "requirements.txt", "alembic.ini", "pyproject.toml",
}


# Function: _ensure_modular_path
def _ensure_modular_path(fname: str, lang: str, is_full_stack: bool, frontend_tech: str) -> str:
    """Backstop for when the LLM's file-planning step returns a bare filename
    instead of a folder-qualified path — infers a conventional subfolder from
    the filename so the output never collapses into one flat directory
    regardless of whether the model followed _path_format_examples."""
    fname = fname.strip().replace("\\", "/")
    if "/" in fname:
        return _emp_nested_path(fname, lang, is_full_stack)

    lower = fname.lower()
    ext = Path(fname).suffix.lower()

    if lower in _EMP_ROOT_NAMES or ext in (".csproj", ".sln"):
        return fname

    if _emp_is_frontend_file(ext, lower):
        return _emp_frontend_path(fname, lower, is_full_stack)

    return _emp_backend_path(fname, lower, ext, lang, is_full_stack)


# Function: _expand_manifest_path
def _expand_manifest_path(path: str, project_name: str) -> List[str]:
    """Expand compact path notation commonly used in prompt manifests."""
    path = path.strip().strip("`").replace("\\", "/")
    for marker, value in {
        "<Solution>": project_name,
        "<Project>": project_name,
        "<TestProject>": f"{project_name}.Tests",
    }.items():
        path = path.replace(marker, value)
    match = re.search(r"\{([^{}]+)\}", path)
    if not match:
        return [path]
    expanded: List[str] = []
    for item in match.group(1).split(","):
        expanded.extend(_expand_manifest_path(
            path[:match.start()] + item.strip() + path[match.end():], project_name
        ))
    return expanded


# Function: _eem_looks_like_file
def _eem_looks_like_file(expanded: str) -> bool:
    from ._shared import _EXTENSIONLESS_FILENAMES
    basename = expanded.rsplit("/", 1)[-1]
    return bool(re.match(r"^[\w.@+\-./]+\.[A-Za-z0-9]{1,12}$", expanded)) or basename in _EXTENSIONLESS_FILENAMES


# Function: _eem_process_manifest_line
def _eem_process_manifest_line(line: str, project_name: str) -> List[str]:
    parts = [
        p.strip()
        for p in re.split(r"(?:,\s+|\s+\+\s+)(?=[\w.<{])", line)
    ]
    files: List[str] = []
    inherited_dir = ""
    for part in parts:
        part = re.sub(r"\s+\([^)]*\)\s*$", "", part).strip()
        candidate = inherited_dir + part if "/" not in part and inherited_dir else part
        if "/" in part:
            inherited_dir = part.rsplit("/", 1)[0] + "/"
        for expanded in _expand_manifest_path(candidate, project_name):
            if _eem_looks_like_file(expanded):
                files.append(expanded.lstrip("/"))
    return files


# Function: _eem_resolve_delegated_files
def _eem_resolve_delegated_files(user_prompt: str, manifest_body: str, project_name: str) -> List[str]:
    """Some manifests intentionally delegate a large framework-specific list
    to an earlier "Emit ALL of these" paragraph. Resolve that reference
    rather than treating "frontend/ (full manifest ...)" as a directory."""
    delegated = re.search(
        r"(?ims)Emit\s+ALL\s+of\s+these.*?:(.*?)(?=^\s*-\s+\*\*|^\s*#{1,3}\s|\Z)",
        user_prompt,
    )
    if not (delegated and re.search(r"(?im)^\s*frontend/\s*\(", manifest_body)):
        return []
    files: List[str] = []
    for token in re.findall(r"`([^`\r\n]+)`", delegated.group(1)):
        for expanded in _expand_manifest_path(token.strip(), project_name):
            if not _eem_looks_like_file(expanded):
                continue
            path = expanded if expanded.startswith("frontend/") else f"frontend/{expanded}"
            files.append(path)
    return files


# Function: _extract_explicit_manifest
def _extract_explicit_manifest(user_prompt: str, project_name: str) -> List[str]:
    """Extract an authoritative FILE MANIFEST instead of rediscovering it."""
    from ._shared import _EXPLICIT_MANIFEST_LIMIT
    match = re.search(
        r"(?ims)^\s*#{0,3}\s*FILE MANIFEST\b[^\n]*\n(.*?)(?=^\s*---\s*$|^\s*#{1,3}\s|\Z)",
        user_prompt,
    )
    if not match:
        return []

    files: List[str] = []
    for raw_line in match.group(1).splitlines():
        line = raw_line.strip().lstrip("-* ").strip()
        if not line or "..." in line:
            continue
        files.extend(_eem_process_manifest_line(line, project_name))

    files.extend(_eem_resolve_delegated_files(user_prompt, match.group(1), project_name))
    return list(dict.fromkeys(files))[:_EXPLICIT_MANIFEST_LIMIT]


# Function: _pf_resolve_target
def _pf_resolve_target(user_prompt: str, target_stack: str, custom_stack_desc: str):
    """Resolve the target stack dict + detected-signal-derived facts. See
    generate_from_prompt for why detected signals override the preset."""
    from .domain_generators.stack_signals import _apply_stack_signals, _detect_domain_requirements, _detect_stack_signals, _stack_requirements_block
    from .scaffolds.money_transfer_demo import _money_transfer_contracts
    from .target_config import TARGET_STACKS, _infer_target_language
    if target_stack == "custom":
        inferred_stack = custom_stack_desc.strip() or user_prompt
        target = {
            "name":          custom_stack_desc.strip()[:120] or "Prompt-inferred custom stack",
            "backend_tech":  custom_stack_desc.strip() or "Infer from the requested file",
            "frontend_tech": "(as per specification)",
            "db_tech":       "(as per specification)",
            "db_target":     "postgres",
            "language":      _infer_target_language(inferred_stack),
            "llm_persona":   (
                f"a software modernization expert specializing in: {inferred_stack}. "
                "Generate production-ready code matching this exact tech stack."
            ),
        }
    else:
        target = TARGET_STACKS.get(target_stack, TARGET_STACKS["aveva_mes"])

    stack_signals = _detect_stack_signals(user_prompt)
    target        = _apply_stack_signals(target, stack_signals, target_stack)
    is_full_stack = bool(stack_signals["frontend"]) and bool(stack_signals["backend"])
    lang          = target.get("language", "csharp")
    stack_reqs    = (
        _stack_requirements_block(stack_signals, lang, target.get("frontend_tech", ""))
        + _detect_domain_requirements(user_prompt)
        + _money_transfer_contracts(user_prompt, stack_signals)
    )
    return target, stack_signals, is_full_stack, lang, stack_reqs


# Function: _pf_project_name
def _pf_project_name(user_prompt: str) -> str:
    """Derive a clean project name from the prompt's OBJECTIVE line (or first
    line, for a non-structured prompt) — see generate_from_prompt for why."""
    naming_source = user_prompt
    objective_match = re.search(
        r"(?ims)^\s*#{1,3}\s*OBJECTIVE\b[^\n]*\n(.*?)(?=^\s*#{1,3}\s|\Z)", user_prompt,
    )
    if objective_match and objective_match.group(1).strip():
        naming_source = objective_match.group(1).strip()
    first_line = naming_source.strip().splitlines()[0][:60]
    raw_name   = re.sub(r"[^\w]+", "_", first_line).strip("_") or "GeneratedApp"
    return "".join(w.capitalize() for w in raw_name.split("_"))[:32] or "GeneratedApp"


# Function: _pf_check_llm_availability
def _pf_check_llm_availability():
    """Return (llm_available, llm_model) — never raises."""
    try:
        from services.llm import check_status, pick_codegen_model
        llm_info  = check_status()
        llm_model = pick_codegen_model()  # fast VRAM-resident model, not the forced status default
        llm_available = llm_info.get("available", False) and bool(llm_model)
        return llm_available, llm_model
    except Exception:
        return False, None


# Function: _pf_record_file
def _pf_record_file(output: Dict[str, str], on_file, path: str, content: str) -> None:
    output[path] = content
    if on_file:
        try:
            on_file(path, content)
        except Exception:
            logger.exception("on_file callback failed for %s", path)


# Function: _pf_record_validation
def _pf_record_validation(validation_counts: dict, validation_files: List[dict], result, attempts: int) -> None:
    validation_counts["checked"] += 1
    validation_counts["passed"] += int(result.passed)
    validation_counts["failed"] += int(not result.passed)
    validation_counts["retried"] += int(attempts > 1)
    validation_counts["by_checker"][result.checker] = validation_counts["by_checker"].get(result.checker, 0) + 1
    strict = result.checker in {"compiler", "parser"}
    validation_counts["strict_checked"] = validation_counts.get("strict_checked", 0) + int(strict)
    validation_counts["strict_passed"] = validation_counts.get("strict_passed", 0) + int(strict and result.passed)
    validation_counts["advisory_checked"] = validation_counts.get("advisory_checked", 0) + int(not strict)
    if attempts > 1 or not result.passed:
        validation_files.append({
            "path": result.path, "language": result.language, "checker": result.checker,
            "passed": result.passed, "attempts": attempts, "diagnostics": result.diagnostics,
        })


# Function: _pf_validate_final_output
def _pf_validate_final_output(output: Dict[str, str], language: str, dialect: str,
                              progress: Callable[[str, int, str], None]) -> tuple[dict, List[dict]]:
    """Revalidate the exact post-hardening files that will enter the build/release snapshot."""
    from services.validators import validate_file
    counts = {"checked": 0, "passed": 0, "failed": 0, "retried": 0, "by_checker": {},
              "strict_checked": 0, "strict_passed": 0, "advisory_checked": 0}
    failures: List[dict] = []
    items = [(path, content) for path, content in output.items() if isinstance(content, str)]
    for index, (path, content) in enumerate(items, 1):
        if index == 1 or index % 10 == 0:
            progress("validating", 97, f"Strict final validation {index}/{len(items)}")
        result = validate_file(path, content, language, dialect_hint=dialect)
        _pf_record_validation(counts, failures, result, 1)
    return counts, failures


# Function: _pf_progress_dispatch
def _pf_progress_dispatch(on_progress, phase: str, pct: int, msg: str) -> None:
    if on_progress:
        on_progress(phase, pct, msg)


# Function: _pf_try_single_file
def _pf_try_single_file(
    user_prompt: str, target: dict, lang: str, project_name: str, image_note: str,
    guide_block: str, stack_reqs: str, template_model: str, guide_text: str, images: list,
    llm_model: str, progress: Callable[[str, int, str], None],
) -> Optional[Tuple[Dict[str, str], dict]]:
    """Single-focused-file generation attempt. Returns (output, validation_summary)
    on success, or None to fall through to full project generation."""
    from ._shared import _DEFAULT_EXT_FOR_LANG, _streaming_progress_cb
    from .target_config import _stack_profiles_for
    from .validation_orchestration import _PROD_RULES_SINGLE_FILE, _generate_validated
    from services.llm import pick_compiler_repair_model
    single_model = pick_compiler_repair_model(llm_model) if lang == "cobol" else llm_model
    llm_model = single_model
    progress("llm", 20, f"LLM ({llm_model}): generating single complete file…")
    _system = _safe_build_system_prompt(
        _stack_profiles_for(lang, target),
        f"You are {target['llm_persona']} Generate one correct, concise, production-ready "
        "source file. Return source code only, with complete imports, validation, useful "
        "error handling, and no markdown fences or explanatory prose.",
    )
    generation_project_name = project_name[:30] if lang == "cobol" else project_name
    placeholder_policy = ""
    if lang == "cobol" and re.search(r"<[^>\r\n]+>", user_prompt):
        placeholder_policy = (
            "\nUNRESOLVED TEMPLATE POLICY: Replace every <...> placeholder with a coherent "
            "concrete demonstration value before writing source. Use PROGRAM-ID COBDEMO; choose "
            "internally consistent file names, organizations, LRECL layouts, testable business "
            "rules, totals, and return-code meanings. Do not emit angle-bracket placeholders. "
            "Prefer the smallest complete batch example satisfying every structural requirement.\n"
        )
    _single_prompt = (
        f"Target platform: {target['name']}\n"
        f"Backend: {target['backend_tech']}\n"
        f"Frontend: {target['frontend_tech']}\n"
        f"Database: {target['db_tech']}\n"
        f"Project / PROGRAM-ID seed: {generation_project_name}\n"
        f"User request:\n{user_prompt}{image_note}"
        f"{placeholder_policy}{guide_block}{stack_reqs}{template_model}\n\n"
        f"{_PROD_RULES_SINGLE_FILE}\n\n"
        "Generate ONE complete, self-contained, production-ready source file that fully "
        "implements the above request. Choose the single most appropriate file type "
        "(e.g. Python module, SQL script, Java class, React component, C# service class). "
        "For TypeScript, emit plain .ts syntax unless the request requires React/JSX; "
        "a React component must be valid TSX and must have balanced JSX tags and expressions. "
        "The file must be immediately runnable/compilable.\n"
        "Output ONLY the file contents. No markdown fences. No commentary. No explanations."
    )
    _single_max_tokens = 2048
    if lang == "cobol":
        # A production batch program commonly needs several SELECT/FD layouts,
        # validation paragraphs, control totals, and report output in one file.
        _single_max_tokens = 4096
    if len(user_prompt) > 1_500:
        _single_max_tokens = max(_single_max_tokens, 4096)
    if len(user_prompt) > 4_000 or guide_text or images:
        _single_max_tokens = max(_single_max_tokens, 6144)
    try:
        _on_tok = _streaming_progress_cb(
            progress, "llm", 20, 95, _single_max_tokens,
            f"LLM ({llm_model}): generating single complete file…",
        )

        _repair_on_tok = _streaming_progress_cb(
            progress, "fixing", 90, 98, _single_max_tokens,
            "LLM compiler repair in progress",
        )

        # Function: _single_on_attempt
        def _single_on_attempt(attempt: int, max_attempts: int) -> None:
            progress("fixing", 90, f"Validation failed — fixing (attempt {attempt}/{max_attempts})…")

        code, _single_result, _single_attempts = _generate_validated(
            _single_prompt, model=single_model, system=_system,
            max_tokens=_single_max_tokens, num_ctx=8192,
            on_token=_on_tok, on_repair_token=_repair_on_tok,
            rel_path=f"generated{_DEFAULT_EXT_FOR_LANG.get(lang, '.txt')}",
            language=lang, dialect=target.get("db_tech", ""),
            on_attempt=_single_on_attempt,
            max_attempts=5 if lang == "cobol" else 3,
            detect_language=True,
            think_initial=False if lang == "cobol" else None,
        )
        progress(
            "validating", 98,
            f"Validated ({_single_result.checker}): "
            f"{'pass' if _single_result.passed else 'FAIL'} after {_single_attempts} attempt(s)",
        )
        progress(
            "complete" if _single_result.passed else "validation_failed", 100,
            "Single file generation complete" if _single_result.passed
            else "Single file generated, but strict validation failed",
        )
        validation_summary = {
            "checked": 1, "passed": int(_single_result.passed), "failed": int(not _single_result.passed),
            "retried": int(_single_attempts > 1),
            "by_checker": {_single_result.checker: 1},
            "strict_checked": int(_single_result.checker in {"compiler", "parser"}),
            "strict_passed": int(
                _single_result.passed and _single_result.checker in {"compiler", "parser"}
            ),
            "advisory_checked": int(_single_result.checker not in {"compiler", "parser"}),
            "build": None,
            "files": [] if _single_result.passed else [{
                "path": _single_result.path, "language": _single_result.language,
                "checker": _single_result.checker, "passed": _single_result.passed,
                "attempts": _single_attempts, "diagnostics": _single_result.diagnostics,
            }],
        }
        return {"__single_file__": code}, validation_summary
    except Exception as exc:
        raise RuntimeError(f"Single-file generation could not complete: {exc}") from exc


# Function: _pf_single_file_attempt
def _pf_single_file_attempt(
    output_mode: str, llm_available: bool, llm_model: Optional[str], is_full_stack: bool,
    user_prompt: str, target: dict, lang: str, project_name: str, image_note: str,
    guide_block: str, stack_reqs: str, template_model: str, guide_text: str, images: list,
    progress: Callable[[str, int, str], None],
) -> Optional[Tuple[Dict[str, str], dict]]:
    """Guard + dispatch for single-file mode — see generate_from_prompt for why
    detected full-stack requests always fall through to the multi-file path."""
    if not (output_mode == "single_file" and llm_available and llm_model and not is_full_stack):
        return None
    return _pf_try_single_file(
        user_prompt, target, lang, project_name, image_note, guide_block, stack_reqs,
        template_model, guide_text, images, llm_model, progress,
    )


# Function: _pf_compute_plan_max_tokens
def _pf_compute_plan_max_tokens(is_full_stack: bool, contracts_request: str) -> int:
    from ._shared import _PLAN_PROMPT_MAX_TOKENS
    tokens = 1400 if is_full_stack else _PLAN_PROMPT_MAX_TOKENS
    if contracts_request:
        tokens += 1400  # room for CONTRACTS + 4 new structured sections on top of the file list
    return tokens


# Function: _pf_user_request_block
def _pf_user_request_block(user_prompt: str, image_note: str, explicit_manifest) -> str:
    if not explicit_manifest:
        return f"{user_prompt}{image_note}"
    return (
        "(full structured request supplied — see OBJECTIVE / CANONICAL CONTRACTS / "
        "HARD ACCEPTANCE CRITERIA / DEFECTS TO EXPLICITLY AVOID / AUTHORITATIVE OUTPUT "
        f"MANIFEST below){image_note}"
    )


# Function: _pf_build_scaffold_basenames
def _pf_build_scaffold_basenames(has_frontend: bool, has_backend: bool, lang: str) -> set:
    basenames = {"docker-compose.yml"}
    if has_frontend:
        basenames.update({
            "package.json", "angular.json", "tsconfig.json", "vite.config.ts", "index.html", "main.ts",
        })
    if has_backend and lang == "python":
        basenames.add("requirements.txt")
    return basenames


# Function: _pf_is_scaffold_duplicate
def _pf_is_scaffold_duplicate(
    f: str, project_name: str, output: Dict[str, str], pack_owned_dirs: tuple,
    scaffold_basenames: set, has_backend: bool, lang: str,
) -> bool:
    """True when `f` is already covered by deterministic scaffolding (Dockerfiles,
    nginx.conf, Program.cs, schema.sql, the money-transfer domain pack, or a
    project-manifest file) and must not be overwritten by an LLM-generated one."""
    if f"{project_name}/{f}" in output:
        return True
    if pack_owned_dirs and f.lower().startswith(pack_owned_dirs):
        return True
    base = f.rsplit("/", 1)[-1].lower()
    if base in scaffold_basenames or f.lower().startswith("k8s/"):
        return True
    return has_backend and lang == "csharp" and base.endswith(".csproj")


# Function: _pf_is_azure_auth
def _pf_is_azure_auth(stack_signals: dict) -> bool:
    return bool(stack_signals["auth"]) and any(
        k in stack_signals["auth"].lower() for k in ("entra", "azure ad")
    )


# Function: _pf_generate_infra_scaffold
def _pf_generate_infra_scaffold(
    lang: str, stack_signals: dict, project_name: str, has_backend: bool, has_frontend: bool,
    record: Callable[[str, str], None], progress: Callable[[str, int, str], None],
) -> None:
    from .build_artifacts import _docker_compose_prompt, _k8s_manifests_prompt
    if has_backend or has_frontend:
        record(f"{project_name}/docker-compose.yml", _docker_compose_prompt(
            project_name, has_backend, has_frontend, lang
        ))
    if stack_signals["deploy"] and (has_backend or has_frontend):
        progress("analyzing", 17, f"Generating {stack_signals['deploy']} manifests…")
        for fname, content in _k8s_manifests_prompt(project_name, has_backend, has_frontend).items():
            record(f"{project_name}/{fname}", content)


# Function: _pf_generate_manifests_and_dockerfiles
def _pf_generate_manifests_and_dockerfiles(
    target: dict, lang: str, project_name: str, has_backend: bool, has_frontend: bool,
    is_dapper: bool, is_azure_auth: bool, is_angular_frontend: bool,
    record: Callable[[str, str], None],
) -> None:
    from .build_artifacts import _angular_frontend_dockerfile, _backend_manifest_files, _dotnet_backend_dockerfile, _dotnet_tfm, _frontend_scaffold_files, _nginx_conf
    if has_backend:
        for fname, content in _backend_manifest_files(
            lang, project_name, target.get("backend_tech", ""), is_dapper, is_azure_auth
        ).items():
            record(f"{project_name}/{fname}", content)
    if has_frontend:
        for fname, content in _frontend_scaffold_files(
            target.get("frontend_tech", ""), project_name, is_azure_auth
        ).items():
            record(f"{project_name}/{fname}", content)

    if has_backend and lang == "csharp":
        record(f"{project_name}/backend/Dockerfile",
               _dotnet_backend_dockerfile(project_name, _dotnet_tfm(target.get("backend_tech", ""))))
    if is_angular_frontend:
        record(f"{project_name}/frontend/Dockerfile", _angular_frontend_dockerfile())
        record(f"{project_name}/frontend/nginx.conf", _nginx_conf())


# Function: _pf_generate_infra_and_manifest_scaffold
def _pf_generate_infra_and_manifest_scaffold(
    target: dict, lang: str, stack_signals: dict, project_name: str, has_backend: bool,
    has_frontend: bool, is_dapper: bool, is_azure_auth: bool, is_angular_frontend: bool,
    record: Callable[[str, str], None], progress: Callable[[str, int, str], None],
) -> None:
    _pf_generate_infra_scaffold(lang, stack_signals, project_name, has_backend, has_frontend, record, progress)
    _pf_generate_manifests_and_dockerfiles(
        target, lang, project_name, has_backend, has_frontend, is_dapper, is_azure_auth,
        is_angular_frontend, record,
    )


# Function: _pf_generate_money_transfer_pack
def _pf_generate_money_transfer_pack(
    project_name: str, lang: str, has_backend: bool, is_dapper: bool, is_angular_frontend: bool,
    is_azure_auth: bool, record: Callable[[str, str], None],
) -> tuple:
    """Only called when is_money_transfer is True — see _pf_generate_deterministic_scaffold."""
    from .scaffolds.money_transfer_demo import _money_transfer_backend_files, _money_transfer_frontend_files, _money_transfer_program_cs, _money_transfer_schema_sql
    pack_owned_dirs: tuple = ()
    if has_backend and lang == "csharp" and is_dapper:
        for fname, content in _money_transfer_backend_files(project_name).items():
            record(f"{project_name}/{fname}", content)
        record(f"{project_name}/backend/Program.cs", _money_transfer_program_cs(project_name))
        record(f"{project_name}/database/schema.sql", _money_transfer_schema_sql())
        pack_owned_dirs += (
            "backend/controllers/", "backend/services/", "backend/repositories/",
            "backend/domain/", "backend/dtos/", "backend/entities/",
        )
    if is_angular_frontend:
        for fname, content in _money_transfer_frontend_files(is_azure_auth).items():
            record(f"{project_name}/{fname}", content)
        pack_owned_dirs += ("frontend/src/app/core/services/",)
    return pack_owned_dirs


# Function: _pf_generate_deterministic_scaffold
def _pf_generate_deterministic_scaffold(
    target: dict, lang: str, stack_signals: dict, project_name: str,
    explicit_manifest, has_backend: bool, has_frontend: bool, is_money_transfer: bool,
    record: Callable[[str, str], None], progress: Callable[[str, int, str], None],
) -> tuple:
    """Deterministically-generated infra/manifest/domain-pack scaffolding — see
    generate_from_prompt for why these specific files are never left to the LLM.
    Returns the output-path-prefix tuple the money-transfer domain pack owns
    exclusively (empty when no such pack applies)."""
    if explicit_manifest:
        return ()

    is_dapper     = (stack_signals["orm"] or "").lower() == "dapper"
    is_azure_auth = _pf_is_azure_auth(stack_signals)
    is_angular_frontend = has_frontend and "angular" in target.get("frontend_tech", "").lower()

    _pf_generate_infra_and_manifest_scaffold(
        target, lang, stack_signals, project_name, has_backend, has_frontend,
        is_dapper, is_azure_auth, is_angular_frontend, record, progress,
    )

    if not is_money_transfer:
        return ()
    return _pf_generate_money_transfer_pack(
        project_name, lang, has_backend, is_dapper, is_angular_frontend, is_azure_auth, record,
    )


# Function: _pf_plan_file_bounds
def _pf_plan_file_bounds(is_full_stack: bool, layer_count: int):
    if is_full_stack:
        return 24, 45
    if layer_count >= 2:
        return 14, 24
    return 8, 14


# Function: _pf_plan_categories_text
def _pf_plan_categories_text(is_full_stack: bool, target: dict) -> str:
    if is_full_stack:
        return (
            "This is a FULL-STACK application — the file plan MUST cover BOTH sides as "
            "separate projects, not just the backend:\n"
            f"  BACKEND ({target['backend_tech']}): entry point/Program file, models/entities, "
            "repositories/data-access (using the specified ORM), service layer, API "
            "controllers/routes, DTOs, dependency-injection/config wiring, appsettings/config "
            "file, dependency manifest (.csproj/pom.xml/requirements.txt), auth middleware/JWT "
            "bearer validation, Dockerfile.\n"
            f"  FRONTEND ({target['frontend_tech']}): app bootstrap/module, routing, at least "
            "2-3 feature components/pages, an API service layer (HttpClient/fetch wrapper), an "
            "auth service + route guard + HTTP interceptor for the identity provider, "
            "environment config files, dependency manifest (package.json), Dockerfile.\n"
            "  DATABASE: schema/migration script for the tables this app needs.\n"
            "Do NOT include docker-compose.yml or any Kubernetes/k8s manifest in your file list — "
            "those are generated separately and are already provided.\n"
            "  Plus: .env.example and at least one automated test file per side."
        )
    return (
        "Include: models/entities, repositories/DAOs, service layer, API controllers/routes, "
        "DTOs/schemas, configuration files, dependency manifests (package.json/pom.xml/requirements.txt), "
        "database migration/schema, Dockerfile, and a test file.\n"
        "Do NOT include docker-compose.yml or any Kubernetes/k8s manifest in your file list — "
        "those are generated separately and are already provided."
    )


# Function: _pf_contracts_request_text
def _pf_contracts_request_text(is_money_transfer: bool) -> str:
    """For money-transfer requests, _money_transfer_contracts already pins exact,
    deterministic signatures — asking the LLM to also invent its own CONTRACTS
    section would be redundant/conflicting. Every other domain has no such pack."""
    if is_money_transfer:
        return ""
    return (
        "Before the file list, define the CONTRACTS every file must conform to — the shared "
        "types/interfaces/enums, the API routes (method + path + request/response shape), and "
        "the database table/column names this application needs. Signatures only, not full "
        "implementations. This is the single source of truth: every file generated afterward "
        "must reproduce these exact names — never invent a different name for the same thing "
        "in a later file.\n"
        "Also define, briefly: every cross-cutting concern the composition root must wire up "
        "(health/readiness endpoint path, CORS policy name + allowed origins, auth scheme, "
        "logging, error-handling middleware, required pipeline order); the exact nested shape "
        "of any shared settings/config object read on both client and server; the folder for "
        "each category of type (entities, DTOs, services, repositories, controllers — exactly "
        "one folder per category, no generic catch-all folder alongside a specific one); and "
        "the namespace/import path a consuming file must use for every type above.\n"
        "Output format — all sections, in this order:\n"
        "CONTRACTS:\n"
        "<concise type/interface/route/schema signatures>\n\n"
        "CROSS-CUTTING CONCERNS:\n"
        "<health/CORS/auth/logging/error-handling/pipeline order, each with its exact name>\n\n"
        "SHARED CONFIG SHAPES:\n"
        "<exact nested shape of any shared settings/config object>\n\n"
        "FOLDER TAXONOMY:\n"
        "<one folder per type category>\n\n"
        "NAMESPACE MAP:\n"
        "<type name -> namespace/import path, one per line>\n\n"
        "FILES:\n"
        "<the file list, one path per line>\n\n"
    )


# Function: _pf_build_plan_prompt
def _pf_build_plan_prompt(
    target: dict, user_prompt: str, image_note: str, guide_block: str, stack_reqs: str,
    template_model: str, contracts_request: str, plan_min_files: int, plan_max_files: int,
    plan_categories: str, path_examples: str, is_money_transfer: bool,
) -> str:
    return (
        f"Target platform: {target['name']}\n"
        f"Backend: {target['backend_tech']}\n"
        f"Frontend: {target['frontend_tech']}\n"
        f"Database: {target['db_tech']}\n"
        f"User request:\n{user_prompt}{image_note}"
        f"{guide_block}{stack_reqs}{template_model}\n\n"
        f"{contracts_request}"
        f"List the smallest complete set of {plan_min_files} to {plan_max_files} files needed to "
        "implement this request as a production-ready application. Do not add redundant layers "
        "or placeholder files.\n"
        f"{plan_categories}\n\n"
        "Every line MUST be a folder-qualified relative path that reflects a proper modular project "
        "layout (separate folders for models, repositories, services, controllers, config, tests, and — "
        "for full-stack — separate top-level folders per side). NEVER output a bare filename with no "
        "folder (e.g. \"UserController.cs\" is WRONG; \"Controllers/UserController.cs\" is correct).\n"
        f"Example correctly-formatted paths for this stack:\n{path_examples}\n"
        + ("Output one relative file path per line, nothing else. No explanations, no bullets, no numbering."
           if is_money_transfer else
           "In the FILES section, output one relative file path per line, nothing else — no explanations, "
           "no bullets, no numbering.")
    )


# Function: _pf_run_plan_generation
def _pf_run_plan_generation(
    plan_prompt: str, contracts_request: str, explicit_manifest, plan_max_tokens: int,
    plan_max_files: int, llm_model: str, system: str, progress: Callable[[str, int, str], None],
):
    """Step 1 of the LLM-authored plan: ask for the file list (+ CONTRACTS/
    CROSS-CUTTING/FOLDER TAXONOMY/NAMESPACE MAP sections when requested)."""
    from ._shared import _adaptive_num_ctx, _streaming_progress_cb
    from services.llm import generate
    file_list = list(explicit_manifest) if explicit_manifest else []
    synthesized_contracts = ""
    cross_cutting_text    = ""
    folder_taxonomy_text  = ""
    namespace_map_text    = ""
    try:
        plan_num_ctx = _adaptive_num_ctx(len(plan_prompt) + len(system), plan_max_tokens)
        _plan_on_tok = _streaming_progress_cb(
            progress, "llm", 25, 35, plan_max_tokens,
            f"LLM ({llm_model}): planning file structure…",
        )
        plan_text = "" if explicit_manifest else generate(
            plan_prompt, model=llm_model, system=system, max_tokens=plan_max_tokens,
            num_ctx=plan_num_ctx, on_token=_plan_on_tok,
        )
        files_text = plan_text
        if contracts_request:
            sections = _parse_plan_sections(plan_text)
            synthesized_contracts = sections["CONTRACTS"]
            if sections["SHARED CONFIG SHAPES"]:
                synthesized_contracts = (
                    f"{synthesized_contracts}\n\nSHARED CONFIG SHAPES:\n{sections['SHARED CONFIG SHAPES']}"
                ).strip()
            cross_cutting_text   = sections["CROSS-CUTTING CONCERNS"]
            folder_taxonomy_text = sections["FOLDER TAXONOMY"]
            namespace_map_text   = sections["NAMESPACE MAP"]
            if sections["FILES"]:
                files_text = sections["FILES"]
        file_list.extend(_parse_file_list_lines(files_text))
        if not explicit_manifest:
            file_list = file_list[:plan_max_files]
    except Exception as exc:
        raise RuntimeError(f"Generation planning failed: {exc}") from exc
    if not file_list:
        raise RuntimeError("Generation planning returned no valid file paths")
    return file_list, synthesized_contracts, cross_cutting_text, folder_taxonomy_text, namespace_map_text


# Function: _pf_validate_manifest_for_duplicates
def _pf_validate_manifest_for_duplicates(
    file_list, synthesized_contracts: str, cross_cutting_text: str, folder_taxonomy_text: str,
    namespace_map_text: str, contracts_request: str, explicit_manifest, plan_max_tokens: int,
    plan_max_files: int, llm_model: str, system: str, progress: Callable[[str, int, str], None],
):
    """Phase 0.5 — prune duplicate types/parallel folder taxonomies/redundant
    components from an LLM-authored plan before any file is generated. Only
    meaningful for an LLM-authored plan (skipped for explicit manifests and
    money-transfer, where contracts are deterministically pinned)."""
    from ._shared import _adaptive_num_ctx, _streaming_progress_cb
    if not (contracts_request and file_list and not explicit_manifest):
        return file_list, synthesized_contracts, cross_cutting_text, folder_taxonomy_text, namespace_map_text
    try:
        from services.llm import MANIFEST_VALIDATION_PROMPT, generate
        contract_document = (
            f"CONTRACTS:\n{synthesized_contracts}\n\n"
            f"CROSS-CUTTING CONCERNS:\n{cross_cutting_text}\n\n"
            f"FOLDER TAXONOMY:\n{folder_taxonomy_text}\n\n"
            f"NAMESPACE MAP:\n{namespace_map_text}\n\n"
            "FILES:\n" + "\n".join(file_list)
        )
        validation_prompt = MANIFEST_VALIDATION_PROMPT.format(contract_document=contract_document)
        val_num_ctx = _adaptive_num_ctx(len(validation_prompt) + len(system), plan_max_tokens)
        _val_on_tok = _streaming_progress_cb(
            progress, "llm", 35, 38, plan_max_tokens,
            f"LLM ({llm_model}): validating file manifest for duplicates…",
        )
        corrected = generate(
            validation_prompt, model=llm_model, system=system, max_tokens=plan_max_tokens,
            num_ctx=val_num_ctx, on_token=_val_on_tok,
        )
        corrected_sections = _parse_plan_sections(corrected)
        new_file_list = _parse_file_list_lines(corrected_sections["FILES"])
        # Never let this step regress a working plan into an empty one — a model
        # that ignores the corrected-document format leaves the pre-validation
        # plan untouched instead of erasing it. Same for each individual section.
        if new_file_list:
            file_list = new_file_list[:plan_max_files]
            synthesized_contracts = corrected_sections["CONTRACTS"] or synthesized_contracts
            cross_cutting_text    = corrected_sections["CROSS-CUTTING CONCERNS"] or cross_cutting_text
            folder_taxonomy_text  = corrected_sections["FOLDER TAXONOMY"] or folder_taxonomy_text
            namespace_map_text    = corrected_sections["NAMESPACE MAP"] or namespace_map_text
    except Exception:
        pass  # keep the pre-validation plan — never block the job on this step
    return file_list, synthesized_contracts, cross_cutting_text, folder_taxonomy_text, namespace_map_text


# Function: _pf_finalize_file_list
def _pf_finalize_file_list(
    file_list, target: dict, project_name: str, is_full_stack: bool, plan_max_files: int,
    explicit_manifest, has_backend: bool, has_frontend: bool, lang: str, output: Dict[str, str],
    pack_owned_dirs: tuple, stack_signals: dict, user_prompt: str,
):
    from .validation_orchestration import _generation_priority, _prune_plan_for_baseline
    if not file_list:
        raise RuntimeError("Approved generation plan contains no files")

    if not explicit_manifest:
        scaffold_basenames = _pf_build_scaffold_basenames(has_frontend, has_backend, lang)
        file_list = [f for f in file_list if not _pf_is_scaffold_duplicate(
            f, project_name, output, pack_owned_dirs, scaffold_basenames, has_backend, lang
        )]
        required_baseline = _required_prompt_baseline(target, project_name, stack_signals, user_prompt)
        required_baseline = [f for f in required_baseline if f"{project_name}/{f}" not in output]
        file_list = _prune_plan_for_baseline(file_list, required_baseline)
        file_list = list(dict.fromkeys(file_list + required_baseline))
        file_list = [_ensure_modular_path(f, lang, is_full_stack, target.get("frontend_tech", "")) for f in file_list]
        file_list = list(dict.fromkeys(file_list))

    return sorted(file_list, key=_generation_priority)


# Function: _pf_file_max_tokens
def _pf_file_max_tokens(fname: str) -> int:
    from ._shared import _TOKENS_COMPONENT, _TOKENS_DEFAULT, _TOKENS_MIGRATION
    lower_name = fname.lower()
    if lower_name.endswith((".json", ".yaml", ".yml", ".toml", ".env", ".md")):
        return 1536
    if any(part in lower_name for part in ("model", "entity", "dto", "schema", "config")):
        return _TOKENS_DEFAULT
    if any(part in lower_name for part in ("test", "spec", "migration")):
        return _TOKENS_MIGRATION
    return _TOKENS_COMPONENT


# Function: _pf_generate_and_record_file
def _pf_generate_and_record_file(
    fname: str, idx: int, total: int, project_name: str, target: dict, lang: str, llm_model: str,
    system: str, synthesized_contracts: str, namespace_map_text: str, required_elements_text: str,
    file_manifest: str, user_request_block: str, guide_block: str, stack_reqs: str, template_model: str,
    requirements_assessment: str, output: Dict[str, str], record: Callable[[str, str], None],
    record_validation, progress: Callable[[str, int, str], None], user_prompt: str,
) -> None:
    from ._shared import _adaptive_num_ctx, _streaming_progress_cb
    from .validation_orchestration import _PROD_RULES_INLINE, _generate_validated
    from services.llm import PER_FILE_USER_TEMPLATE
    pct_start = 35 + int((idx / max(total, 1)) * 60)
    pct_end   = min(95, 35 + int(((idx + 1) / max(total, 1)) * 60))
    progress("llm", pct_start, f"LLM: generating {fname}…")
    file_prompt = PER_FILE_USER_TEMPLATE.format(
        target_path=fname,
        file_purpose=(
            "Part of the file plan above; implement per its role in the manifest, the "
            "CONTRACTS, and the FOLDER TAXONOMY / NAMESPACE MAP under REQUIRED ELEMENTS below."
        ),
        stack_and_versions=(
            f"{target['name']} — Backend: {target['backend_tech']} | "
            f"Frontend: {target['frontend_tech']} | Database: {target['db_tech']}"
        ),
        contracts=synthesized_contracts or "(none defined)",
        existing_files=_contract_digest(output) or "(none yet — this is one of the first files)",
        namespace_map=namespace_map_text or "(not supplied)",
        declared_dependencies=_declared_dependencies_text(output),
        api_reference_snippets="(none supplied)",
        required_elements=required_elements_text or "(none)",
        requirements=(
            f"Project: {project_name}\n"
            f"Full file plan:\n{file_manifest}\n\n"
            f"User request:\n{user_request_block}"
            f"{guide_block}{stack_reqs}{template_model}{requirements_assessment}\n\n"
            f"{_PROD_RULES_INLINE}\n\n"
            "This file must work in conjunction with the other files listed above.\n"
            "TYPE OWNERSHIP RULE: define only the types assigned to this exact file. If an enum, "
            "class, interface, record, DTO, or model has its own file in the manifest, reference "
            "that type and do not redefine it here. Interface files must not contain implementation "
            "classes, and implementation files must not redeclare their interfaces."
        ),
    )
    file_max_tokens = _pf_file_max_tokens(fname)
    file_num_ctx = _adaptive_num_ctx(len(file_prompt), file_max_tokens)
    try:
        _on_tok = _streaming_progress_cb(
            progress, "llm", pct_start, pct_end, file_max_tokens, f"LLM: generating {fname}…",
        )

        # Function: _file_on_attempt
        def _file_on_attempt(attempt: int, max_attempts: int, _fname=fname, _pct=pct_end) -> None:
            progress("fixing", _pct, f"Validation failed for {_fname} — fixing (attempt {attempt}/{max_attempts})…")

        content, _result, _attempts = _generate_validated(
            file_prompt, model=llm_model, system=system,
            max_tokens=file_max_tokens, num_ctx=file_num_ctx, on_token=_on_tok,
            rel_path=f"{project_name}/{fname}", language=lang, dialect=target.get("db_tech", ""),
            on_attempt=_file_on_attempt,
        )
        progress(
            "validating", pct_end,
            f"Validated {fname} ({_result.checker}): {'pass' if _result.passed else 'FAIL'}",
        )
        record_validation(_result, _attempts)
        record(f"{project_name}/{fname}", content)
    except Exception as exc:
        raise RuntimeError(f"Generation failed for {fname}: {exc}") from exc


# Function: _pf_generate_project_files_llm
def _pf_generate_project_files_llm(
    file_list, project_name: str, target: dict, lang: str, llm_model: str, system: str,
    synthesized_contracts: str, namespace_map_text: str, required_elements_text: str,
    file_manifest: str, user_request_block: str, guide_block: str, stack_reqs: str,
    template_model: str, requirements_assessment: str, output: Dict[str, str],
    record: Callable[[str, str], None], record_validation, progress: Callable[[str, int, str], None],
    user_prompt: str,
) -> None:
    """Step 2 — generate each planned file with full production context."""
    total = len(file_list)
    for idx, fname in enumerate(file_list):
        _pf_generate_and_record_file(
            fname, idx, total, project_name, target, lang, llm_model, system,
            synthesized_contracts, namespace_map_text, required_elements_text, file_manifest,
            user_request_block, guide_block, stack_reqs, template_model, requirements_assessment,
            output, record, record_validation, progress, user_prompt,
        )


# Function: _pf_generate_project_files_template
def _pf_generate_project_files_template(
    target: dict, project_name: str, user_prompt: str, is_full_stack: bool, has_backend: bool,
    has_frontend: bool, lang: str, output: Dict[str, str], pack_owned_dirs: tuple,
    record: Callable[[str, str], None], progress: Callable[[str, int, str], None],
):
    """Template fallback used when the LLM is unavailable — embeds the prompt as
    a guidance comment per file. Returns the final (post-scaffold-filter) file list."""
    from .build_artifacts import _default_frontend_file_list
    from .scaffolds.single_file_templates import _template_from_prompt
    progress("generating", 25, "Generating templates (LLM offline — run: ollama pull qwen2.5-coder:7b)…")
    file_list = _default_file_list(target, project_name)
    if is_full_stack:
        file_list = file_list + _default_frontend_file_list(target["frontend_tech"], project_name)
    scaffold_basenames = _pf_build_scaffold_basenames(has_frontend, has_backend, lang)
    file_list = [
        f for f in file_list
        if not _pf_is_scaffold_duplicate(f, project_name, output, pack_owned_dirs, scaffold_basenames, has_backend, lang)
    ]
    total = len(file_list)
    for idx, fname in enumerate(file_list):
        pct = 30 + int((idx / max(total, 1)) * 65)
        progress("generating", pct, f"Generating {fname}…")
        record(f"{project_name}/{fname}", _template_from_prompt(fname, user_prompt, target, project_name))
    return file_list


# Function: _pf_repair_build_round
def _pf_repair_build_round(
    fixable: dict, round_num: int, max_rounds: int, output: Dict[str, str],
    synthesized_contracts: str, namespace_map_text: str, llm_model: str, system: str,
    progress: Callable[[str, int, str], None],
) -> None:
    from ._shared import _TOKENS_COMPONENT, _adaptive_num_ctx
    from .validation_orchestration import _clean_generated_content
    from services.llm import REPAIR_PROMPT, generate
    for _path, _errors in fixable.items():
        progress(
            "repairing", 92,
            f"Fixing {_path} — build round {round_num}/{max_rounds} ({len(_errors)} error(s))…",
        )
        identifiers = set(re.findall(r"'([A-Za-z_]\w*)'", "\n".join(_errors)))
        related = []
        for candidate_path, candidate_content in output.items():
            if candidate_path == _path or not isinstance(candidate_content, str):
                continue
            if any(re.search(rf"\b{re.escape(identifier)}\b", candidate_content) for identifier in identifiers):
                related.append(f"FILE: {candidate_path}\n{candidate_content[:6000]}")
            if len(related) >= 8:
                break
        _repair_prompt = REPAIR_PROMPT.format(
            target_path=_path, current_contents=output.get(_path, ""),
            build_errors="\n".join(_errors), contracts=synthesized_contracts or "(none defined)",
            namespace_map=namespace_map_text or "(not supplied)",
            api_reference_snippets="\n\n".join(related) or "(none supplied)",
        )
        _repair_num_ctx = _adaptive_num_ctx(len(_repair_prompt) + len(system), _TOKENS_COMPONENT)
        try:
            _fixed = generate(
                _repair_prompt, model=llm_model, system=system,
                max_tokens=_TOKENS_COMPONENT, num_ctx=_repair_num_ctx,
            )
            output[_path] = _clean_generated_content(_fixed)
        except Exception:
            pass  # keep the pre-repair content for this file, still try the rest


# Function: _pf_enforce_governed_generation_files
def _pf_enforce_governed_generation_files(output: Dict[str, str], project_name: str, is_money_transfer: bool) -> set[str]:
    """Restore canonical pack files and return paths the LLM may never rewrite."""
    from .scaffolds.money_transfer_demo import _money_transfer_backend_files, _money_transfer_frontend_files, _money_transfer_program_cs, _money_transfer_schema_sql
    if not is_money_transfer:
        return set()
    prefix = f"{project_name}/"
    canonical = {prefix + path: content for path, content in _money_transfer_backend_files(project_name).items()}
    canonical[prefix + "backend/Program.cs"] = _money_transfer_program_cs(project_name)
    canonical[prefix + "database/schema.sql"] = _money_transfer_schema_sql()
    has_frontend = any("/frontend/" in path for path in output)
    for path, content in _money_transfer_frontend_files(True).items():
        key = prefix + path
        if has_frontend and (not path.endswith("auth.service.ts") or key in output):
            canonical[key] = content
    owned_dirs = tuple(prefix + value for value in (
        "backend/Controllers/", "backend/Services/", "backend/Repositories/",
        "backend/Domain/", "backend/DTOs/", "backend/Entities/",
        "frontend/src/app/core/guards/", "frontend/src/app/core/interceptors/",
        "frontend/src/app/features/transactions/",
    ))
    for path in list(output):
        if path.startswith(owned_dirs) and path not in canonical:
            del output[path]
    canonical_types = set()
    for content in canonical.values():
        canonical_types.update(re.findall(r"\b(?:class|interface|record|enum)\s+([A-Za-z_]\w*)", content))
    for path, content in list(output.items()):
        if path in canonical or not path.lower().endswith(".cs") or not isinstance(content, str):
            continue
        declarations = set(re.findall(
            r"\b(?:public\s+)?(?:sealed\s+|abstract\s+|partial\s+)*(?:class|interface|record|enum)\s+([A-Za-z_]\w*)",
            content,
        ))
        if declarations and declarations.issubset(canonical_types):
            del output[path]
    output.update(canonical)
    return set(canonical)


# Function: _pf_reconcile_governed_manifest
def _pf_reconcile_governed_manifest(file_list: List[str], output: Dict[str, str], project_name: str,
                                    is_money_transfer: bool) -> List[str]:
    """Remove only superseded pack-owned plan entries; retain all other missing-file auditing."""
    if not is_money_transfer:
        return file_list
    owned = ("backend/controllers/", "backend/services/", "backend/repositories/", "backend/domain/",
             "backend/dtos/", "backend/entities/", "frontend/src/app/core/guards/",
             "frontend/src/app/core/interceptors/", "frontend/src/app/features/transactions/")
    reconciled = []
    for path in file_list:
        relative = path.removeprefix(f"{project_name}/")
        key = f"{project_name}/{relative}"
        if relative.lower().startswith(owned) and key not in output:
            continue
        reconciled.append(relative)
    return reconciled


# Function: _pf_harden_framework_closure
def _pf_harden_framework_closure(output: Dict[str, str]) -> None:
    """Make generated framework manifests and local asset references closed before build."""
    for path, content in list(output.items()):
        if "/frontend/" in path and Path(path).name.startswith("tsconfig") and path.endswith(".json"):
            try:
                data = json.loads(content)
                data.setdefault("compilerOptions", {})["baseUrl"] = "."
                configured_types = data["compilerOptions"].get("types")
                if isinstance(configured_types, list):
                    data["compilerOptions"]["types"] = [value for value in configured_types if value != "msal-browser"]
                output[path] = json.dumps(data, indent=2) + "\n"
            except (TypeError, ValueError):
                pass
    for path, content in list(output.items()):
        if not path.endswith((".ts", ".tsx")) or not isinstance(content, str):
            continue
        parent = Path(path).parent
        frontend_marker = "/frontend/"
        if frontend_marker in path:
            frontend_root = path.split(frontend_marker, 1)[0] + "/frontend/"
            # Function: _relative_local_import
            def _relative_local_import(match):
                target = frontend_root + match.group(2)
                relative = os.path.relpath(target, parent.as_posix()).replace("\\", "/")
                if not relative.startswith("."):
                    relative = "./" + relative
                return match.group(1) + relative + match.group(3)
            content = re.sub(r"((?:from\s+|import\s*)['\"])(src/[^'\"]+)(['\"])", _relative_local_import, content)
            output[path] = content
        references = re.findall(r"(?:templateUrl|styleUrl)\s*:\s*['\"]([^'\"]+)['\"]", content)
        for group in re.findall(r"styleUrls\s*:\s*\[([^\]]*)\]", content, re.DOTALL):
            references.extend(re.findall(r"['\"]([^'\"]+)['\"]", group))
        for reference in references:
            target = (parent / reference).as_posix()
            if target in output:
                continue
            if target.endswith((".css", ".scss", ".sass", ".less")):
                output[target] = "/* Component styles intentionally start empty. */\n"
            elif target.endswith(".html"):
                output[target] = "<div></div>\n"


# Function: _pf_run_build_and_repair
def _pf_run_build_and_repair(
    output: Dict[str, str], project_name: str, lang: str, is_money_transfer: bool,
    output_mode: str, synthesized_contracts: str, namespace_map_text: str, llm_model: str,
    system: str, progress: Callable[[str, int, str], None],
):
    """Phase 2 — real build + repair. C#/Java/TypeScript only (the stacks with a
    real installed compiler — see services/build_runner.py). Skipped for
    money-transfer's pre-pinned pack and for single-file mode."""
    if output_mode != "project":
        return None
    try:
        import shutil as _shutil
        from services.build_runner import PROJECT_BUILD_LANGUAGES, BuildResult, run_build

        if lang not in PROJECT_BUILD_LANGUAGES:
            return BuildResult(
                False,
                "unsupported-build-route",
                {"<build>": [f"No strict project validation route is registered for language={lang!r}"]},
            )

        _build_tmp = Path(tempfile.mkdtemp(prefix="modernization_build_"))
        protected_paths = _pf_enforce_governed_generation_files(output, project_name, is_money_transfer)
        _pf_harden_framework_closure(output)
        progress("building", 90, f"Building project ({lang})…")
        build_result = run_build(output, lang, _build_tmp)

        _MAX_REPAIR_ROUNDS = 5
        for _round in range(1, _MAX_REPAIR_ROUNDS + 1):
            if build_result.passed:
                break
            # Synthetic keys like "<build>"/"<install>" mean a project-level
            # failure with no single file to blame — nothing left to repair.
            _fixable = {p: e for p, e in build_result.errors_by_file.items() if p in output and p not in protected_paths}
            if not _fixable:
                break
            _pf_repair_build_round(
                _fixable, _round, _MAX_REPAIR_ROUNDS, output, synthesized_contracts,
                namespace_map_text, llm_model, system, progress,
            )
            _pf_enforce_governed_generation_files(output, project_name, is_money_transfer)
            _pf_harden_framework_closure(output)
            build_result = run_build(output, lang, _build_tmp)

        _build_status = "passed" if build_result.passed else "still failing"
        progress(
            "build-complete", 96,
            f"Build {_build_status} ({build_result.checker})"
            + ("" if build_result.passed
               else f" after {_MAX_REPAIR_ROUNDS} repair round(s)"),
        )
        _shutil.rmtree(_build_tmp, ignore_errors=True)
        return build_result
    except Exception as exc:
        logger.warning("Phase 2 build/repair failed for %s: %s", project_name, exc)
        from services.build_runner import BuildResult
        return BuildResult(
            False,
            "build-runner-error",
            {"<build>": [f"Project validation could not complete: {exc}"]},
        )


# Function: _pf_apply_generation_audit
def _pf_apply_generation_audit(
    output: Dict[str, str], project_name: str, file_list, validation_files: List[dict], build_result,
) -> None:
    """Report (don't discard): ships whatever generated successfully and flags
    the specific problems in a companion file, rather than erasing an
    otherwise-good multi-file result over one flaky file — see
    generate_from_prompt's original inline comment for the full rationale."""
    from .validation_orchestration import _audit_generated_project
    audit_issues = _audit_generated_project(output, project_name, file_list)
    build_failed = bool(build_result) and not build_result.passed
    if not (audit_issues or validation_files or build_failed):
        return
    sections = []
    if audit_issues:
        preview = "\n".join(f"- {issue}" for issue in audit_issues)
        sections.append(
            "## Structural audit\n\n"
            "Every other file in this download passed the same checks (no markdown "
            "fences, no empty files, no duplicate type definitions, no missing "
            "manifest files) — review and fix these specific files before "
            f"building/deploying.\n\n{preview}\n"
        )
    if validation_files:
        val_lines = [
            f"- {f['path']} ({f['checker']}, "
            f"{'still FAILING' if not f['passed'] else 'fixed on retry'} after {f['attempts']} attempt(s)): "
            f"{'; '.join(f['diagnostics']) or '(no diagnostics)'}"
            for f in validation_files
        ]
        sections.append(
            "## Per-file validation\n\n"
            "Files that failed syntax validation at least once (see services/validators.py). "
            "Entries marked \"fixed on retry\" now pass; \"still FAILING\" exhausted retries and "
            "are shipped as the best available attempt.\n\n" + "\n".join(val_lines) + "\n"
        )
    if build_failed:
        build_lines = [
            f"- {path} ({build_result.checker}): {'; '.join(errs)}"
            for path, errs in build_result.errors_by_file.items()
        ]
        sections.append(
            "## Real build\n\n"
            f"`{build_result.checker}` still fails after the repair loop's retry rounds — "
            "shipped as the best available attempt.\n\n" + "\n".join(build_lines) + "\n"
        )
    output[f"{project_name}/_GENERATION_AUDIT.md"] = "# Generation Audit\n\n" + "\n".join(sections)
    if audit_issues:
        logger.warning(
            "Project %s has %d structural audit issue(s): %s",
            project_name, len(audit_issues), "; ".join(audit_issues[:5]),
        )


# Function: _pf_merge_to_single_file
def _pf_merge_to_single_file(output: Dict[str, str]) -> str:
    sep = "=" * 72
    sections = [
        f"// {sep}\n// FILE: {fpath}\n// {sep}\n\n{content}"
        for fpath, content in sorted(output.items())
        if not fpath.endswith(".md")
    ]
    return "\n\n\n".join(sections) or "// No code generated"


# Function: generate_from_prompt
def generate_from_prompt(
    user_prompt: str,
    target_stack: str = "aveva_mes",
    images_data: Optional[List] = None,
    on_progress: Optional[Callable[[str, int, str], None]] = None,
    custom_stack_desc: str = "",
    guide_text: str = "",
    output_mode: str = "project",
    on_file: Optional[Callable[[str, str], None]] = None,
) -> Tuple[Dict[str, str], dict]:
    """
    Generate modernized code files from a natural-language prompt
    with optional screenshot/image and reference guide attachments.

    Returns (output, validation_summary): output maps relative output file
    paths to file contents; validation_summary reports per-file syntax
    validation results (see services/validators.py) — {checked, passed,
    failed, retried, by_checker, files: [...]} where files only lists
    entries that needed a retry or are still failing.

    on_file, if given, is called (path, content) immediately as each file is
    produced — this lets the caller persist partial results as they land
    rather than only after the whole (potentially many-minutes-long,
    many-file) call returns. On this box the backend process gets killed by
    something outside the app roughly every 3-5 minutes under load, which is
    often shorter than a full multi-file generation — without this, a job
    interrupted mid-run loses every file it had already finished.
    """
    from .docs_generation import _guide_section
    from .domain_generators.stack_signals import _detect_domain_requirements
    from .target_config import _stack_profiles_for
    from .validation_orchestration import _generation_template, _requirements_assessment
    unresolved = _unresolved_requirement_placeholders(user_prompt)
    if unresolved:
        preview = ", ".join(unresolved[:8])
        raise ValueError(
            "The specification contains unresolved requirement placeholders: "
            f"{preview}. Supply concrete values before generation; the governed "
            "workflow will not invent business requirements."
        )
    progress = functools.partial(_pf_progress_dispatch, on_progress)

    target, stack_signals, is_full_stack, lang, stack_reqs = _pf_resolve_target(
        user_prompt, target_stack, custom_stack_desc
    )
    from services.build_runner import PRODUCTION_PROJECT_BUILD_LANGUAGES, toolchain_compatibility_error
    if output_mode == "project" and lang not in PRODUCTION_PROJECT_BUILD_LANGUAGES:
        raise RuntimeError(
            f"Target {lang!r} has strict file validation but no dependency-aware "
            "production project build route. Use single-file mode or configure "
            "a supported project build adapter."
        )
    compatibility_error = toolchain_compatibility_error(
        " ".join((
            custom_stack_desc,
            target.get("name", ""),
            f"language:{target.get('language', '')}",
            target.get("backend_tech", ""),
            target.get("frontend_tech", ""),
            target.get("db_tech", ""),
        ))
    )
    if compatibility_error:
        raise RuntimeError(compatibility_error)

    images      = images_data or []
    image_note  = f"\n[User attached {len(images)} screenshot(s) for context]" if images else ""
    guide_block = _guide_section(guide_text)

    project_name = _pf_project_name(user_prompt)
    explicit_manifest = _extract_explicit_manifest(user_prompt, project_name)
    requirements_assessment = _requirements_assessment(user_prompt, explicit_manifest)
    template_model = _generation_template(
        user_prompt, target, stack_signals, explicit_manifest
    )
    # When an explicit structured manifest was extracted, requirements_assessment
    # already carries the OBJECTIVE/CANONICAL CONTRACTS/HARD ACCEPTANCE CRITERIA/
    # DEFECTS/MANIFEST sections in focused form — re-embedding the full raw
    # prompt on top of that in every one of dozens of per-file calls is pure
    # duplication that, for a large exemplar-style prompt, forces every call
    # into the largest context tier purely from prompt-processing overhead —
    # exactly the kind of slowdown that caused the earlier "stuck" report at a
    # fraction of this prompt's size.
    user_request_block = _pf_user_request_block(user_prompt, image_note, explicit_manifest)

    output: Dict[str, str] = {}
    _record = functools.partial(_pf_record_file, output, on_file)

    # Per-file syntax-validation results, accumulated as the per-file LLM loop
    # runs (see _generate_validated). Only LLM-generated files go through
    # this — deterministic scaffolding never calls _record_validation.
    _validation_counts = {"checked": 0, "passed": 0, "failed": 0, "retried": 0, "by_checker": {}}
    _validation_files: List[dict] = []
    _record_validation = functools.partial(_pf_record_validation, _validation_counts, _validation_files)

    progress("analyzing", 5, "Parsing prompt requirements…")

    llm_available, llm_model = _pf_check_llm_availability()
    if not llm_available or not llm_model:
        raise RuntimeError(
            "Code generation requires an available code-generation model. "
            "The governed workflow does not emit generic offline templates. "
            "Start Ollama and install an approved code model before retrying."
        )

    # ── Single-file mode: one focused LLM call → directly copyable code ────
    # Skipped for detected full-stack requests (frontend + backend both named)
    # since a real full-stack app cannot fit in one file — those fall through
    # to the multi-file project path below instead of being truncated.
    _single_file_result = _pf_single_file_attempt(
        output_mode, llm_available, llm_model, is_full_stack, user_prompt, target, lang,
        project_name, image_note, guide_block, stack_reqs, template_model, guide_text, images,
        progress,
    )
    if _single_file_result is not None:
        return _single_file_result

    progress("analyzing", 15, "Building generation plan…")

    if not explicit_manifest:
        _record(f"{project_name}/README.md", _prompt_readme(user_prompt, target, project_name, len(images)))

    # Infra scaffolding is generated deterministically, not by the LLM —
    # docker-compose.yml and Kubernetes manifests are exactly the files where
    # an LLM generating one file at a time produces internally-inconsistent
    # output (Service targetPort not matching container port, Secret key
    # names not matching what the Deployment references, compose build
    # contexts that don't resolve from the file's own location, ...). These
    # are added to `output` up front so the per-file loop below never
    # generates them at all (see the file_list filter further down).
    has_backend   = bool(stack_signals["backend"])
    has_frontend  = bool(stack_signals["frontend"])
    is_money_transfer = bool(_detect_domain_requirements(user_prompt))
    pack_owned_dirs = _pf_generate_deterministic_scaffold(
        target, lang, stack_signals, project_name, explicit_manifest,
        has_backend, has_frontend, is_money_transfer, _record, progress,
    )

    if llm_available and llm_model:
        system = _safe_build_system_prompt(
            _stack_profiles_for(lang, target),
            f"You are {target['llm_persona']} Produce concise, production-ready code only. "
            "Every file must compile, contain complete implementations and imports, validate public "
            "inputs, use structured logging and useful error handling, read secrets from environment "
            "variables, and remain consistent with the supplied file manifest. Never output markdown "
            "fences, prose, TODOs, placeholders, or duplicate code.",
        )

        # Step 1 — ask LLM to produce a comprehensive file list. The range scales
        # with how many architectural layers were detected — a generic single-
        # service request stays cheap (8-14 files), but a real full-stack ask
        # (separate frontend + backend + auth + infra) needs far more files
        # than that to actually be complete, so a fixed 14-file cap silently
        # dropped whole layers (the frontend, the k8s manifests, ...).
        layer_count = sum(bool(v) for v in (
            stack_signals["frontend"], stack_signals["backend"],
            stack_signals["auth"], stack_signals["deploy"],
        ))
        plan_min_files, plan_max_files = _pf_plan_file_bounds(is_full_stack, layer_count)
        path_examples     = _path_format_examples(lang, is_full_stack, target.get("frontend_tech", ""))
        plan_categories    = _pf_plan_categories_text(is_full_stack, target)
        contracts_request  = _pf_contracts_request_text(is_money_transfer)
        plan_prompt = _pf_build_plan_prompt(
            target, user_prompt, image_note, guide_block, stack_reqs, template_model,
            contracts_request, plan_min_files, plan_max_files, plan_categories, path_examples,
            is_money_transfer,
        )
        progress("llm", 25, f"LLM ({llm_model}): planning file structure…")
        plan_max_tokens = _pf_compute_plan_max_tokens(is_full_stack, contracts_request)

        file_list, synthesized_contracts, cross_cutting_text, folder_taxonomy_text, namespace_map_text = (
            _pf_run_plan_generation(
                plan_prompt, contracts_request, explicit_manifest, plan_max_tokens, plan_max_files,
                llm_model, system, progress,
            )
        )
        file_list, synthesized_contracts, cross_cutting_text, folder_taxonomy_text, namespace_map_text = (
            _pf_validate_manifest_for_duplicates(
                file_list, synthesized_contracts, cross_cutting_text, folder_taxonomy_text,
                namespace_map_text, contracts_request, explicit_manifest, plan_max_tokens,
                plan_max_files, llm_model, system, progress,
            )
        )

        # Feeds PER_FILE_USER_TEMPLATE's {required_elements} slot (Phase 1) —
        # cross-cutting concerns and folder taxonomy are both "things every
        # relevant file must respect," just at different granularity, so they
        # travel together as one slot rather than inventing a template slot
        # PER_FILE_USER_TEMPLATE doesn't have.
        required_elements_text = "\n\n".join(
            f"{label}:\n{text}" for label, text in (
                ("CROSS-CUTTING CONCERNS", cross_cutting_text),
                ("FOLDER TAXONOMY", folder_taxonomy_text),
            ) if text
        )

        file_list = _pf_finalize_file_list(
            file_list, target, project_name, is_full_stack, plan_max_files, explicit_manifest,
            has_backend, has_frontend, lang, output, pack_owned_dirs, stack_signals, user_prompt,
        )
        file_manifest = "\n".join(f"  {f}" for f in file_list)

        _pf_generate_project_files_llm(
            file_list, project_name, target, lang, llm_model, system, synthesized_contracts,
            namespace_map_text, required_elements_text, file_manifest, user_request_block,
            guide_block, stack_reqs, template_model, requirements_assessment, output,
            _record, _record_validation, progress, user_prompt,
        )
    else:  # guarded above; this prevents a future fail-open regression
        raise RuntimeError("Code-generation model became unavailable before planning")

    # Scaffolds define cross-file contracts and build metadata, but executable
    # source must always be authored through Ollama. This final pass includes
    # bootstrap/demo-pack files omitted from the planning loop.
    from .domain_generators.dispatch import _ollama_generate_all_sources
    _ollama_generate_all_sources(
        output, target, project_name, llm_model, system,
        lambda message: progress("llm", 82, message),
        _record_validation,
    )

    # ── Phase 2: real build + repair ────────────────────────────────────────
    # C#/Java/TypeScript only — these are the stacks with a real, installed
    # compiler that can resolve the whole project's dependency graph (see
    # services/build_runner.py). Python/SQL have no comparable "build"
    # concept and already got a real per-file syntax check in Phase 1
    # (validators.py). Skipped for money-transfer's pre-pinned deterministic
    # pack (no LLM-authored contracts/namespace-map to repair against) and
    # for single-file mode (nothing to "build" as a project).
    build_result = _pf_run_build_and_repair(
        output, project_name, lang, is_money_transfer, output_mode, synthesized_contracts,
        namespace_map_text, llm_model, system, progress,
    )

    _validation_counts, _validation_files = _pf_validate_final_output(
        output, lang, target.get("db_tech", ""), progress,
    )

    file_list = _pf_reconcile_governed_manifest(
        file_list, output, project_name, is_money_transfer,
    )

    _pf_apply_generation_audit(output, project_name, file_list, _validation_files, build_result)

    validation_summary = {
        **_validation_counts,
        "files": _validation_files,
        "build": None if build_result is None else {
            "passed": build_result.passed,
            "checker": build_result.checker,
            "remaining_errors": {} if build_result.passed else build_result.errors_by_file,
        },
    }

    generation_passed = (
        _validation_counts.get("failed", 0) == 0
        and (build_result is None or build_result.passed)
    )
    progress(
        "complete" if generation_passed else "validation_failed",
        100,
        "Code generation and strict validation complete"
        if generation_passed else
        "Generated output retained, but strict validation failed",
    )
    # is_full_stack always takes the multi-file path even if single_file was
    # requested (see the guard above) — a real full-stack app cannot be
    # merged into one file without losing entire layers.
    if output_mode == "single_file" and not is_full_stack:
        return {"__single_file__": _pf_merge_to_single_file(output)}, validation_summary
    return output, validation_summary


# Function: _unresolved_requirement_placeholders
def _unresolved_requirement_placeholders(prompt: str) -> List[str]:
    """Detect specification placeholders without mistaking HTML tags or common
    one-letter generic type parameters for missing requirements."""
    html_tags = {
        "a", "body", "button", "div", "form", "head", "html", "img", "input",
        "label", "li", "link", "main", "meta", "p", "script", "section",
        "span", "style", "table", "tbody", "td", "th", "thead", "title", "tr", "ul",
    }
    found = []
    for match in re.finditer(r"<([^>\r\n]{1,120})>", prompt or ""):
        value = match.group(1).strip()
        tag = value.lstrip("/").split(None, 1)[0].casefold()
        if tag in html_tags or "=" in value or len(value) == 1:
            continue
        looks_unresolved = (
            "..." in value
            or any(char.isspace() for char in value)
            or (value.upper() == value and bool(re.search(r"[A-Z]", value)))
        )
        if looks_unresolved:
            found.append(match.group(0))
    return list(dict.fromkeys(found))


# Function: _prompt_readme
def _prompt_readme(user_prompt: str, target: dict, project_name: str, image_count: int) -> str:
    img_note = f"\n- User attached **{image_count} screenshot(s)** as additional context." if image_count else ""
    return textwrap.dedent(f"""\
        # {project_name} — Prompt-Driven Generation

        ## Request
        > {user_prompt[:500]}
        {img_note}

        ## Target Platform: {target["name"]}
        | Layer | Technology |
        |---|---|
        | Frontend | {target["frontend_tech"]} |
        | Backend | {target["backend_tech"]} |
        | Database | {target["db_tech"]} |

        ## LLM Used
        Model: qwen2.5-coder (via Ollama — runs locally on your GPU)
        Setup: `ollama pull qwen2.5-coder:7b`

        ## Getting Started
        Review the generated files and adjust names / namespaces as needed.
    """)


# Function: _default_file_list
def _default_file_list(target: dict, project_name: str) -> List[str]:
    """Return a sensible default set of output filenames for the given target."""
    lang = target.get("language", "csharp")
    ns   = project_name
    if lang == "java":
        return [
            f"src/main/java/{ns}/Application.java",
            f"src/main/java/{ns}/model/{ns}Entity.java",
            f"src/main/java/{ns}/repository/{ns}Repository.java",
            f"src/main/java/{ns}/service/{ns}Service.java",
            f"src/main/java/{ns}/controller/{ns}Controller.java",
            "src/main/resources/application.yml",
            "pom.xml",
        ]
    elif lang in ("typescript", "javascript"):
        return [
            "src/App.tsx",
            f"src/components/{ns}Panel.tsx",
            f"src/services/{ns}Service.ts",
            "src/api/client.ts",
            "package.json",
            "tsconfig.json",
            "vite.config.ts",
        ]
    elif lang == "sql":
        return [
            "Database/schema.sql",
            "Database/stored_procedures.sql",
            "Database/migration_notes.md",
        ]
    elif lang == "python":
        return [
            "app/__init__.py",
            "app/main.py",
            f"app/models/{ns.lower()}.py",
            f"app/schemas/{ns.lower()}.py",
            f"app/routers/{ns.lower()}.py",
            "app/database.py",
            "app/config.py",
            "alembic.ini",
            "requirements.txt",
            "Dockerfile",
        ]
    else:  # csharp (default)
        return [
            f"Services/{ns}Service/{ns}Service.csproj",
            f"Services/{ns}Service/Program.cs",
            f"Services/{ns}Service/Models/{ns}.cs",
            f"Services/{ns}Service/Repositories/I{ns}Repository.cs",
            f"Services/{ns}Service/Repositories/{ns}Repository.cs",
            f"Services/{ns}Service/Services/I{ns}Service.cs",
            f"Services/{ns}Service/Services/{ns}Service.cs",
            f"Services/{ns}Service/Controllers/{ns}Controller.cs",
            "Database/schema_mssql.sql",
        ]



# ─── README ───────────────────────────────────────────────────────────────────
# Function: _readme
def _readme(analysis: dict, root_ns: str, target: dict | None = None) -> str:
    from .target_config import TARGET_STACKS
    arch  = analysis.get("architecture", {})
    techs = ", ".join(arch.get("detected_techs", []))
    loc   = arch.get("total_loc", 0)
    if target is None:
        target = TARGET_STACKS["aveva_mes"]
    return textwrap.dedent(f"""\
        # {root_ns} — Modernization Report

        ## Source Project Analysis
        | Property | Value |
        |---|---|
        | Architecture pattern | {arch.get("pattern", "Unknown")} |
        | Era | {arch.get("era", "Unknown")} |
        | Source database | {arch.get("database", "Unknown")} |
        | Detected technologies | {techs} |
        | Total lines of code | {loc:,} |
        | Complexity | {arch.get("complexity", "Unknown")} |

        ## Target Modernization Stack: {target["name"]}
        | Layer | Technology |
        |---|---|
        | Frontend | {target["frontend_tech"]} |
        | Backend | {target["backend_tech"]} |
        | Database | {target["db_tech"]} |
        | Container | Docker / docker-compose |

        ## LLM Used for Code Generation
        Model: qwen2.5-coder:7b (via Ollama — local, runs on NVIDIA A10-8Q)
        Recommended pull command: `ollama pull qwen2.5-coder:7b`

        ## Getting Started
        See individual service READMEs under `ModernizedApp/Services/` for setup instructions.
        See `Database/migration_notes.md` for database migration steps.

        ## Generated Services
        Each domain is an independent microservice.
    """)


# ─── PostgreSQL schema ────────────────────────────────────────────────────────
# Function: _postgres_schema
def _postgres_schema(tables: List[str], oracle_pats: List[str]) -> str:
    lines = [
        "-- PostgreSQL 16 schema — generated from Oracle/SQL Server analysis\n",
        "-- Review column types and constraints before applying to production.\n\n",
        "CREATE EXTENSION IF NOT EXISTS pgcrypto;\n\n",
    ]
    if not tables:
        tables = ["CUSTOMERS", "ACCOUNTS", "TRANSACTIONS", "AUDIT_LOG"]  # type: ignore[assignment]
    for table in tables:
        name = table.upper().replace("BANKING_USER.", "")
        snake = name.lower()
        lines.append(
            f"CREATE TABLE IF NOT EXISTS {snake} (\n"
            f"    id          SERIAL PRIMARY KEY,\n"
            f"    name        VARCHAR(100) NOT NULL,\n"
            f"    is_active   BOOLEAN NOT NULL DEFAULT TRUE,\n"
            f"    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),\n"
            f"    updated_at  TIMESTAMPTZ\n"
            f");\n\n"
        )
    lines.append(
        "-- Oracle → PostgreSQL key conversions applied:\n"
        "-- VARCHAR2(n) → VARCHAR(n)\n"
        "-- NUMBER(p,s) → NUMERIC(p,s)\n"
        "-- DATE        → TIMESTAMPTZ\n"
        "-- SYSDATE     → NOW()\n"
        "-- NVL(a,b)    → COALESCE(a,b)\n"
        "-- ROWNUM      → ROW_NUMBER() OVER (ORDER BY ...)\n"
        "-- SEQUENCE    → SERIAL / GENERATED ALWAYS AS IDENTITY\n"
    )
    return "".join(lines)


# Function: _migration_notes_pg
def _migration_notes_pg(oracle_pats: List[str]) -> str:
    mappings = {
        "Oracle ROWNUM pagination":   "`ROW_NUMBER() OVER (ORDER BY ...)` or `LIMIT / OFFSET`",
        "Oracle SYSDATE":             "`NOW()` or `CURRENT_TIMESTAMP`",
        "Oracle NVL function":        "`COALESCE(a, b)`",
        "Oracle DECODE function":     "`CASE WHEN ... THEN ... ELSE ... END`",
        "Oracle sequence NEXTVAL":    "`GENERATED ALWAYS AS IDENTITY` or `SERIAL`",
        "Oracle DUAL table":          "Remove `FROM DUAL` — use bare `SELECT <expr>`",
        "Oracle hierarchical query":  "Recursive CTE: `WITH RECURSIVE ... AS ( SELECT ... UNION ALL ... )`",
        "Oracle MERGE statement":     "`INSERT ... ON CONFLICT DO UPDATE` (upsert)",
        "Oracle VARCHAR2 type":       "`VARCHAR(n)` or `TEXT`",
        "Oracle NUMBER type":         "`NUMERIC(p,s)` or `INTEGER` / `BIGINT`",
        "Oracle LOB types":           "`TEXT` (CLOB) / `BYTEA` (BLOB)",
        "Oracle dynamic SQL":         "`EXECUTE format('...', $1)` in PL/pgSQL",
        "Oracle DBMS_OUTPUT package": "Use `RAISE NOTICE` in PL/pgSQL",
        "Oracle TRIGGER":             "PostgreSQL triggers use `CREATE TRIGGER` + `CREATE FUNCTION ... RETURNS TRIGGER`",
        "Oracle PROCEDURE":           "`CREATE OR REPLACE PROCEDURE ... LANGUAGE plpgsql`",
    }
    lines = ["# Oracle → PostgreSQL Migration Notes\n\n## Detected Constructs\n"]
    for pat in (oracle_pats or []):
        lines.append(f"- **{pat}**: {mappings.get(pat, 'Review manually')}\n")
    if not oracle_pats:
        lines.append("_No Oracle-specific constructs detected._\n")
    return "".join(lines)


# ─── MongoDB schema ────────────────────────────────────────────────────────────
# Function: _mongodb_schema
def _mongodb_schema(tables: List[str]) -> str:
    if not tables:
        tables = ["Customer", "Account", "Transaction"]  # type: ignore[assignment]
    schemas = ["// MongoDB 7 Mongoose schemas — generated from relational analysis\n",
               "const { Schema, model } = require('mongoose');\n\n"]
    for table in tables:
        name = table.upper().replace("BANKING_USER.", "").capitalize().rstrip("S") + "s"
        schemas.append(textwrap.dedent(f"""\
            const {name[:-1]}Schema = new Schema({{
              name:      {{ type: String, required: true, trim: true }},
              isActive:  {{ type: Boolean, default: true }},
              createdAt: {{ type: Date, default: Date.now }},
              updatedAt: {{ type: Date }},
            }}, {{ timestamps: true }});

            const {name[:-1]} = model('{name[:-1]}', {name[:-1]}Schema);

        """))
    schemas.append("module.exports = { " + ", ".join(
        t.upper().replace("BANKING_USER.", "").capitalize().rstrip("S") + "s"[:-1]
        for t in tables
    ) + " };\n")
    return "".join(schemas)


# Function: _migration_notes_mongo
def _migration_notes_mongo(oracle_pats: List[str]) -> str:
    return textwrap.dedent("""\
        # Oracle → MongoDB Migration Notes

        ## Relational → Document Model Strategy
        - One-to-many relationships: **embed** small child documents; **reference** large collections
        - Replace JOIN queries with $lookup aggregation pipeline stages
        - Replace sequences/identity with MongoDB ObjectId (_id)
        - Replace stored procedures with application-layer logic or MongoDB aggregations
        - Transactions supported in MongoDB 4+ with replica sets (use session.withTransaction())

        ## Type Mappings
        | Oracle | MongoDB |
        |--------|---------|
        | VARCHAR2 | String |
        | NUMBER   | Number |
        | DATE     | Date   |
        | CLOB     | String |
        | BLOB     | Binary |
        | BOOLEAN  | Boolean|
    """)
