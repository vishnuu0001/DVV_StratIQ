# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Modernization — services/modernizer (validation_orchestration.py)
# Date: 2026-06-09
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



# Function: _requirements_assessment
def _requirements_assessment(user_prompt: str, manifest: List[str]) -> str:
    """Keep contracts and acceptance criteria prominent in every file call."""
    sections = []
    for heading in ("OBJECTIVE", "CANONICAL CONTRACTS", "HARD ACCEPTANCE CRITERIA",
                    "DEFECTS TO EXPLICITLY AVOID"):
        # Two-step: find the heading and how many '#' it uses, THEN stop only
        # at another heading of the same or shallower depth. A single-step
        # "stop at any #{1,3} heading" lookahead stops at the section's own
        # "### Entities" / "### DTOs" / ... subheadings (CANONICAL CONTRACTS
        # is entirely organized as ### subsections), capturing nothing for
        # exactly the section the whole exercise revolves around.
        start = re.search(rf"(?im)^\s*(#{{1,3}})\s*{re.escape(heading)}\b[^\n]*\n", user_prompt)
        if not start:
            continue
        level = len(start.group(1))
        rest = user_prompt[start.end():]
        stop = re.search(rf"(?im)^\s*#{{1,{level}}}\s", rest)
        body = (rest[:stop.start()] if stop else rest).strip()
        if body:
            sections.append(f"{heading}:\n{body}")
    if manifest:
        sections.append("AUTHORITATIVE OUTPUT MANIFEST:\n" +
                        "\n".join(f"- {path}" for path in manifest))
    return ("\n\nDETAILED REQUIREMENTS ASSESSMENT (authoritative; self-check against it "
            "before returning the file):\n" + "\n\n".join(sections)) if sections else ""


# Function: _generation_template
def _generation_template(
    user_prompt: str,
    target: dict,
    signals: Dict[str, Optional[str]],
    manifest: List[str],
) -> str:
    """General template model supplied to planning and every generation call."""
    layers = [
        f"frontend={target.get('frontend_tech')}",
        f"backend={target.get('backend_tech')}",
        f"data={target.get('db_tech')}",
    ]
    for key in ("auth", "orm", "deploy", "db"):
        if signals.get(key):
            layers.append(f"{key}={signals[key]}")
    manifest_policy = (
        "The supplied manifest is authoritative: emit every listed file exactly once."
        if manifest else
        "Derive the smallest complete manifest, including entry points, configuration, "
        "dependency manifests, feature code, tests, and deployment assets."
    )
    return (
        "\n\nGENERATION TEMPLATE MODEL (mandatory for every technology stack):\n"
        "1. Requirements: preserve explicit versions, constraints, endpoints, and acceptance criteria.\n"
        "2. Architecture: use separate presentation, application/service, domain/model, data-access, "
        "configuration, test, and deployment concerns where the selected stack supports them.\n"
        "3. Contracts first: define each public type once; implementations and tests may call only "
        "members present on the corresponding interface/type with identical names and arity.\n"
        "4. Bootstrap completeness: include every framework entry point/root module and register every "
        "dependency, authentication scheme, route, middleware, health endpoint, and configuration source.\n"
        "5. Cross-file closure: every local import/reference and every configured asset/path must exist "
        "in the output; no duplicate types, placeholders, TODOs, omitted bodies, or markdown fences.\n"
        "6. Operational consistency: Docker contexts, ports, probes, service names, configuration keys, "
        "and deployment selectors must agree end-to-end.\n"
        "7. Verification: self-check compilation-facing contracts, imports, manifests, and prohibited "
        "patterns before returning each file.\n"
        f"Resolved stack: {'; '.join(layers)}.\n"
        f"Manifest policy: {manifest_policy}"
    )


# Function: _audit_generated_project
def _audit_generated_project(
    output: Dict[str, str],
    project_name: str,
    expected_files: List[str],
) -> List[str]:
    """Cross-file structural checks that need the whole project at once (missing
    manifest files, duplicate C# type declarations across files). Per-file checks
    (empty file, markdown fence, placeholder/TODO text) are covered earlier, per
    file, by services/validators.py's validate_file — every LLM-generated file
    already went through that before landing in `output`."""
    issues: List[str] = []
    expected_keys = {f"{project_name}/{path}" for path in expected_files}
    actual_keys = set(output)
    for missing in sorted(expected_keys - actual_keys):
        issues.append(f"missing required file: {missing}")

    type_owners: Dict[str, str] = {}
    for path, content in output.items():
        if not isinstance(content, str) or not content.strip() or not path.lower().endswith(".cs"):
            continue
        for kind, name in re.findall(
            r"\b(?:public\s+)?(?:sealed\s+|abstract\s+|partial\s+)*"
            r"(class|interface|record|enum)\s+([A-Za-z_]\w*)",
            content,
        ):
            key = f"{kind}:{name}"
            owner = type_owners.get(key)
            if owner and owner != path and "partial class" not in content:
                issues.append(f"duplicate {kind} {name}: {owner} and {path}")
            else:
                type_owners[key] = path
    return issues


# Function: _clean_generated_content
def _clean_generated_content(content: str) -> str:
    """Remove response-format artifacts that make valid source uncompilable."""
    text = (content or "").strip()
    fenced = re.fullmatch(r"```(?:[\w.+-]+)?\s*\n(.*?)\n```", text, re.DOTALL)
    if fenced:
        text = fenced.group(1).strip()
    return text + ("\n" if text else "")


# Function: _single_file_extension
def _single_file_extension(language: str, content: str) -> str:
    """Choose the compiler-facing extension for standalone generated source.

    TypeScript decides whether JSX grammar is legal from the filename. Passing a
    React component to tsc as ``generated.ts`` produces a misleading cascade of
    TS1xxx parse errors (often beginning with TS1161), even when the source is
    otherwise valid TSX.
    """
    from ._shared import _DEFAULT_EXT_FOR_LANG
    language = (language or "").lower()
    if language not in {"typescript", "javascript"}:
        return _DEFAULT_EXT_FOR_LANG.get(language, ".txt")

    from services.validators import _contains_jsx
    has_jsx = _contains_jsx(content)
    if language == "typescript":
        return ".tsx" if has_jsx else ".ts"
    return ".jsx" if has_jsx else ".js"


# Function: _generate_validated
def _generate_validated(
    prompt: str,
    *,
    model: str,
    system: str,
    max_tokens: int,
    num_ctx: int,
    rel_path: str,
    language: str,
    dialect: str = "",
    on_token: Optional[Callable[[str], None]] = None,
    on_repair_token: Optional[Callable[[str], None]] = None,
    on_attempt: Optional[Callable[[int, int], None]] = None,
    max_attempts: int = 3,
    detect_language: bool = False,
    think_initial: Optional[bool] = None,
) -> Tuple[str, "ValidationResult", int]:
    """
    Generate one file's content, then syntax-validate it (see services/validators.py)
    and retry with the diagnostics fed back to the model on failure, up to
    max_attempts total. Never raises on exhausted retries — returns the last
    attempt with result.passed=False so callers can report it without failing
    the whole job (same "report, don't discard" philosophy as _audit_generated_project).
    generate() exceptions (e.g. Ollama unreachable) propagate unchanged — this
    only changes what happens to successfully-returned-but-bad content.
    `dialect` is only used for language="sql" (pass the target's db_tech string
    so sqlglot parses against the right SQL dialect).
    """
    from ._shared import _adaptive_num_ctx
    from services.llm import generate, pick_compiler_repair_model
    from services.validators import _infer_sql_dialect, _resolve_sql_dialect, validate_file

    content = _clean_generated_content(
        generate(prompt, model=model, system=system, max_tokens=max_tokens, num_ctx=num_ctx,
                 on_token=on_token, think=think_initial)
    )
    validation_language = _detect_single_file_language(content, language) if detect_language else language
    validation_path = (
        f"generated{_single_file_extension(validation_language, content)}"
        if detect_language else rel_path
    )
    result = validate_file(validation_path, content, validation_language, dialect_hint=dialect)
    attempt = 1
    repair_model = pick_compiler_repair_model(model) if language == "cobol" else model
    cobol_fixed = language == "cobol" and any(
        token in (dialect or "").lower() for token in ("ibm", "db2", "z/os", "zos", "enterprise cobol")
    )

    while not result.passed and attempt < max_attempts:
        attempt += 1
        if on_attempt:
            on_attempt(attempt, max_attempts)
        diagnostics_block = "\n".join(f"- {d}" for d in result.diagnostics) or "- (no specific diagnostics)"
        language_repair_rules = ""
        if validation_language in {"typescript", "javascript"}:
            language_repair_rules = (
                "\nTypeScript/JavaScript compiler rules: Preserve JSX only when the requested "
                "file is a React/JSX component; standalone TypeScript logic must not contain JSX. "
                "Balance every JSX opening/closing tag, brace, parenthesis, bracket, string, "
                "template literal, and regular-expression delimiter. Do not write HTML markup "
                "outside a JSX expression. Return one complete source file, never a markdown "
                "fence or a filename header.\n"
            )
        if validation_language == "java":
            language_repair_rules = (
                "\nJava/Spring Boot 3 repair rules: use jakarta.* rather than legacy javax.* "
                "enterprise APIs. Controllers declare request inputs directly on method "
                "parameters. If Idempotency-Key is required, use exactly "
                '`@RequestHeader(name = "Idempotency-Key") String idempotencyKey` in the '
                "mapped controller method and pass that value to the service; do not use "
                "HttpServletRequest, RequestContextHolder, ServletRequestAttributes, or a "
                "local header-name string as a substitute. Use constructor injection and "
                "typed exceptions handled by @RestControllerAdvice. A controller depends on "
                "an application service only: it must not access repositories or Kafka/event "
                "publishers directly. DTOs, records, enums, and status types belong in their "
                "own manifest files, never as private nested controller classes. Add every "
                "required java.util/java.time/java.math import explicitly.\n"
            )
        if validation_language == "sql":
            effective_sql_dialect = (
                _resolve_sql_dialect(dialect) or _infer_sql_dialect(content) or "ANSI"
            )
            language_repair_rules = (
                f"\nSQL validation rules: The authoritative dialect is "
                f"{effective_sql_dialect}. Preserve that one dialect and do not mix "
                "PostgreSQL PL/pgSQL, Oracle PL/SQL, T-SQL, or MySQL procedural syntax. "
                "For stored routines, use the delimiter, block syntax, exception syntax, "
                "and parameter conventions of the selected dialect. Procedure/function "
                "parameters must have names distinct from table columns. Qualify columns "
                "with table aliases in predicates; never emit a tautology such as "
                "`WHERE username = username`. Return one complete executable SQL file "
                "without markdown fences or prose.\n"
            )
        if validation_language == "cobol":
            format_rule = (
                "Return IBM Enterprise COBOL fixed-format source: columns 1-6 blank; column 7 "
                "indicator only; Area A columns 8-11; Area B columns 12-72; no tabs or text "
                "after column 72; do not emit >>SOURCE FORMAT FREE."
                if cobol_fixed else
                "Return portable GnuCOBOL source beginning with `>>SOURCE FORMAT FREE`."
            )
            language_repair_rules = (
                f"\nCOBOL compiler rules: {format_rule} Remove the entire CONFIGURATION SECTION unless it is "
                "functionally required. Never emit CRT., OPERATING-SYSTEM., "
                "USER-IDENTIFICATION., IBM-370 declarations, or an empty SPECIAL-NAMES paragraph. "
                "For sequential files, ENVIRONMENT DIVISION should proceed directly to "
                "INPUT-OUTPUT SECTION and FILE-CONTROL. Every SELECT must have a matching "
                "FD and 01 record. Put FILE STATUS on SELECT and test the PIC XX status in "
                "separate IF statements after I/O. OPEN and CLOSE do not support ON ERROR; "
                "READ uses AT END / NOT AT END / END-READ and does not support ON ERROR; "
                "DISPLAY does not support WITH STATUS. Do not put a period inside an inline "
                "PERFORM before END-PERFORM, and never GO TO a SECTION.\n"
            )
        if validation_language == "cobol":
            fix_prompt = (
                "Rewrite this complete COBOL file so GnuCOBOL accepts it. The compiler errors "
                "are authoritative. You may rewrite any invalid paragraph; do not preserve "
                "syntax named by an error.\n\n"
                f"COMPILER ERRORS:\n{diagnostics_block}\n"
                f"{language_repair_rules}\n"
                "MANDATORY REPLACEMENTS:\n"
                "- Replace `DISPLAY message WITH STATUS status-name` with "
                "`DISPLAY message status-name`.\n"
                "- OPEN and CLOSE take the SELECT logical file name, never a quoted filename.\n"
                "- WRITE takes the FD record name, never a filename.\n"
                "- Every SELECT logical name must match an FD logical name.\n"
                "- PROGRAM-ID must be 30 characters or fewer.\n"
                "- Quote literal filenames in ASSIGN; never emit an unquoted dotted filename.\n"
                "- Omit ACCESS MODE for sequential files and do not put RECORDING MODE on SELECT.\n"
                "- Preserve a complete source file through PROCEDURE DIVISION and STOP RUN.\n"
                "- Return the entire corrected file, not a patch.\n\n"
                f"CURRENT FILE:\n{content}\n\n"
                "Output raw COBOL only. No markdown or explanation."
            )
        else:
            fix_prompt = (
                f"{prompt}\n\n"
                "--- PREVIOUS ATTEMPT FAILED VALIDATION ---\n"
                f"Validator: {result.checker}\n"
                f"Issues found:\n{diagnostics_block}\n\n"
                f"{language_repair_rules}\n"
                "--- PREVIOUS ATTEMPT CONTENT ---\n"
                f"{content}\n\n"
                "Fix ONLY the reported issues. Keep all other names, structure, and logic unchanged. "
                "Output the COMPLETE corrected file content only. No markdown fences. No commentary."
            )
        fix_num_ctx = _adaptive_num_ctx(len(fix_prompt), max_tokens)
        if validation_language == "cobol":
            fix_num_ctx = min(fix_num_ctx, 8192)
        content = _clean_generated_content(
            generate(fix_prompt, model=repair_model, system=system, max_tokens=max_tokens,
                     num_ctx=fix_num_ctx, on_token=on_repair_token or on_token,
                     think=False if validation_language == "cobol" else None)
        )
        validation_language = _detect_single_file_language(content, validation_language) if detect_language else language
        validation_path = (
            f"generated{_single_file_extension(validation_language, content)}"
            if detect_language else rel_path
        )
        result = validate_file(validation_path, content, validation_language, dialect_hint=dialect)

    return content, result, attempt


# Function: _detect_single_file_language
def _detect_single_file_language(content: str, requested_language: str) -> str:
    """Route standalone output through the shared, content-aware detector."""
    from services.validators import detect_source_language
    return detect_source_language(content, requested_language)


# Function: _generation_priority
def _generation_priority(path: str) -> tuple:
    """Generate contracts before their implementations and callers."""
    low = path.lower()
    if any(x in low for x in ("/entities/", "/models/", "/dtos/", "/domain/")):
        rank = 0
    elif low.endswith((".csproj", ".sln", "package.json", "angular.json", "tsconfig.json")):
        rank = 1
    elif any(x in low for x in ("repository", "service")) and "test" not in low:
        rank = 2 if re.search(r"/i[a-z]+(?:repository|service)", low) else 3
    elif any(x in low for x in ("controller", "component", "program.cs", "app.module")):
        rank = 4
    elif "test" in low or ".spec." in low:
        rank = 6
    else:
        rank = 5
    return rank, low


# Function: _prune_plan_for_baseline
def _prune_plan_for_baseline(
    planned: List[str],
    baseline: List[str],
) -> List[str]:
    """Remove model-proposed aliases that would duplicate baseline-owned types."""
    baseline_lower = {path.lower() for path in baseline}
    baseline_basenames = {Path(path).name.lower() for path in baseline}
    baseline_stems = {Path(path).stem.lower().lstrip("i") for path in baseline}
    baseline_has_tests = any(
        "test" in path.lower() or ".spec." in path.lower() for path in baseline
    )
    result: List[str] = []
    for path in planned:
        low = path.lower()
        base = Path(path).name.lower()
        stem = Path(path).stem.lower().lstrip("i")
        if low in baseline_lower or base in baseline_basenames:
            continue
        # Models/DTOs/entities and interfaces frequently get proposed twice in
        # different folders or with accidental names such as IIRepository.
        if stem in baseline_stems and any(
            marker in low
            for marker in ("/model", "/entit", "/dto", "repository", "service")
        ):
            continue
        if baseline_has_tests and ("test" in low or ".spec." in low):
            continue
        result.append(path)
    return result


# ---------------------------------------------------------------------------
# generate_from_prompt helpers — extracted phases of the prompt→project
# pipeline. Split out so each phase is independently readable/testable and
# to keep generate_from_prompt itself a thin sequence of phase calls.
# ---------------------------------------------------------------------------

_PROD_RULES_SINGLE_FILE = (
    "PRODUCTION CODE RULES (mandatory):\n"
    "- Complete implementation — no empty bodies, no TODO/FIXME stubs\n"
    "- All imports/package declarations at top of file\n"
    "- Full error handling with logging\n"
    "- Input validation on all public entry points\n"
    "- Configuration from environment variables, never hardcoded\n"
    "- No markdown fences (```) in the output"
)

_PROD_RULES_INLINE = (
    "PRODUCTION CODE RULES (mandatory for every file generated):\n"
    "- Complete implementation of every method — no empty bodies, no TODO/FIXME stubs\n"
    "- All imports, using statements, package declarations included\n"
    "- Full error handling: exceptions caught, logged, and re-raised or HTTP-mapped\n"
    "- Input validation on all public entry points\n"
    "- Structured logging in service/controller layers\n"
    "- Configuration (DB URLs, secrets, ports) from environment variables, never hardcoded\n"
    "- Async/await patterns where the framework supports them\n"
    "- No markdown code fences (```) in the output\n"
    "CONSISTENCY (this is where multi-file generation usually fails):\n"
    "- Never create a second file, type, or endpoint that does the same job as one already in "
    "the file plan, and never use a near-duplicate/typo-variant name for the same thing\n"
    "- Names must match across layers exactly: a route a client calls must exist on the server "
    "at that exact path; a call to X.Y(a, b) requires method Y on type X with that exact arity\n"
    "- Use only APIs, methods, and overloads that actually exist in the stated library versions. "
    "If unsure whether an API exists, use the standard documented one — never invent a method "
    "name, parameter, or overload\n"
    "- Keep names, casing, and serialization consistent end to end (e.g. if the API returns "
    "camelCase JSON, the client models are camelCase)\n"
    "- Handle the real edge cases the task implies (empty input, not-found, concurrency/atomicity, "
    "failure/rollback) — not just the happy path"
)
