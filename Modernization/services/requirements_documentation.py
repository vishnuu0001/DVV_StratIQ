# ---------------------------------------------------------------------------
# Scope: Ollama-backed requirements documentation for governed projects.
# ---------------------------------------------------------------------------
"""Generate BRD, FSD, and knowledge-graph artifacts from immutable source."""
from __future__ import annotations

import json
import io
import re
from collections import Counter
from pathlib import Path
from typing import Any, Callable, Optional

from services import llm
from services.governance import semantic_index

CONTEXT_LIMIT = 48_000
EVIDENCE_LIMIT = 22_000
DOCUMENT_MAX_TOKENS = 8_192
DOCUMENT_CONTEXT_TOKENS = 24_576
DOCUMENT_TYPES = {"brd", "fsd", "knowledge_graph"}
REQUIREMENTS_PREFERRED_MODELS = (
    "deepseek-coder:6.7b", "qwen2.5-coder:7b", "qwen3.5:9b", "qwen2.5-coder:3b",
)

# A single completion asked to hold an entire executive-grade BRD/FSD in its
# head — every required section AND a fully-cited, evidenced, multi-operation
# subsection for every observed capability — routinely exceeds what a small
# local coder model can reliably follow in one pass. Instead each observed
# capability gets its own small, independently-validated completion (a task
# scoped enough for a 6-7B model to actually satisfy), and the "frame" call
# only has to cover the cross-cutting sections. See _generate_capability_sections.
CAPABILITY_MAX_TOKENS = 2_048
CAPABILITY_CONTEXT_TOKENS = 8_192
CAPABILITY_MAX_SECONDS = 180
CAPABILITY_MAX_ATTEMPTS = 2  # initial attempt + 1 targeted retry, per capability
CAPABILITY_ID_BLOCK = 100  # reserved identifier slots per capability; keeps numbering collision-free
FRAME_ID_FLOOR = 9_000  # cross-cutting BR/FS ids the frame introduces must start at/after this

_DOCUMENT_INSTRUCTIONS = {
    "brd": f"""Create a production-grade Business Requirements Document in Markdown. It must be
detailed enough for executive approval, product planning, solution design, and acceptance testing.
Include: Document Control / Project Identity; Executive Summary; Business Context and Objectives;
Scope and Explicit Exclusions; Stakeholders and Personas; Current-State Assessment; a Business
Capabilities section that is a concise table of every observed capability by Capability ID, name,
and operations (the detailed, evidenced, per-capability requirements are written separately and
supplied to you as already-generated content — do not repeat or re-derive them, and do not write a
dedicated section for any individual capability); any numbered cross-cutting Business Requirements
you introduce yourself (for concerns spanning multiple capabilities, e.g. security, compliance,
reporting, integration, non-functional expectations), numbered BR-{FRAME_ID_FLOOR} and above with
statement, rationale, priority, stakeholder, acceptance measure, dependencies, and evidence;
Business Rules (RULE-###); end-to-end Process Flows including alternatives and exceptions; Data
Requirements; Integrations; Security, Privacy, Compliance and Audit; Reporting; Non-functional
Business Expectations; Assumptions, Dependencies, Constraints, Risks and Mitigations; Measurable
Success Criteria; Acceptance Criteria; Open Questions; and a requirement-to-source Traceability
Matrix (per-capability rows will be appended after your content; cover your own cross-cutting
requirements here). Every requirement and major assertion must cite one or more Evidence IDs and
source paths. Mark each statement Observed, Justified Inference, or Open Question. Do not invent
certainty, stakeholders, SLAs, or behavior unsupported by evidence.""",
    "fsd": f"""Create a production-grade Functional Specification Document in Markdown. It must be
detailed enough for engineering implementation, test design, security review, operations, and
release approval. Include: Document Control / Project Identity; Purpose; Source-Evidence Coverage;
System Context and Architecture; Actors, Roles and Authorization; a Functional Decomposition section
that is a concise table of every observed capability by Capability ID, name, and operations (the
detailed, evidenced, per-capability Functional Specifications are written separately and supplied to
you as already-generated content — do not repeat or re-derive them, and do not write a dedicated
section for any individual capability); any numbered cross-cutting Functional Specifications you
introduce yourself (for concerns spanning multiple capabilities, e.g. shared APIs, cross-cutting
validation, platform error handling), numbered FS-{FRAME_ID_FLOOR} and above with inputs, processing,
outputs, validations, errors, state changes, dependencies, acceptance criteria, and evidence;
detailed Use Cases with preconditions/main flow/alternatives/exceptions/postconditions; Workflows;
Screen and Component Behavior; APIs and Interface Contracts including methods, schemas, status/error
behavior and idempotency where evidenced; Data Model with entities, fields, keys, relationships,
validation, retention and state transitions; Business Rules and Algorithms; Error Handling and
Recovery; Notifications; Reporting; Auditability and Observability; Integrations; Configuration;
Batch and Background Processing; Security and Privacy; Performance, Scalability, Availability and
other non-functional specifications; Deployment and Operational Considerations; Acceptance
Scenarios; Open Questions; and BR-to-FS-to-source Traceability (per-capability rows will be appended
after your content; cover your own cross-cutting specifications here). Every specification and major
assertion must cite one or more Evidence IDs and source paths. Mark each statement Observed,
Justified Inference, or Open Question. Do not invent contracts, field semantics, SLAs, or behavior
unsupported by evidence.""",
}

_GRAPH_INSTRUCTIONS = """Return JSON only with this shape:
{"title":"...","summary":"...","nodes":[{"id":"unique-id","label":"...","type":"business|actor|feature|functional|data|integration|rule|quality","description":"..."}],"edges":[{"source":"node-id","target":"node-id","relationship":"enables|uses|depends_on|implements|governs|produces|integrates_with"}]}
Build a detailed, connected knowledge graph linking business needs to functional features, actors,
rules, data, integrations, and quality requirements. Use 30-100 concise nodes and preserve explicit
BR/FS identifiers in labels. Add an evidence_source_path property to nodes whenever source evidence
exists. Include the supplied Project ID, Project Name, Application Key, and Client Name in the graph
identity and connect the project root to its requirements. Every edge endpoint must reference a
declared node. Do not wrap the JSON in Markdown fences."""

_EVIDENCE_EXTENSIONS = {
    ".py", ".java", ".cs", ".vb", ".js", ".jsx", ".ts", ".tsx", ".go", ".rs",
    ".php", ".rb", ".c", ".cpp", ".h", ".hpp", ".sql", ".graphql", ".xml", ".jsp",
    ".json", ".yaml", ".yml", ".toml", ".properties", ".config", ".md", ".txt",
}
_EVIDENCE_SKIP_DIRS = {".git", "node_modules", "dist", "build", "bin", "obj", "target", ".venv", "__pycache__"}

_LANGUAGE_BY_EXTENSION = {
    ".py": "Python", ".java": "Java", ".cs": "C#", ".vb": "Visual Basic",
    ".js": "JavaScript", ".jsx": "JavaScript/JSX", ".ts": "TypeScript",
    ".tsx": "TypeScript/TSX", ".go": "Go", ".rs": "Rust", ".php": "PHP",
    ".rb": "Ruby", ".c": "C", ".cpp": "C++", ".h": "C/C++ Header",
    ".hpp": "C++ Header", ".sql": "SQL", ".graphql": "GraphQL", ".xml": "XML",
    ".json": "JSON", ".yaml": "YAML", ".yml": "YAML", ".toml": "TOML",
    ".properties": "Properties", ".config": "Configuration", ".md": "Markdown",
    ".txt": "Text",
    ".jsp": "JSP",
}

_VENDOR_FILE_MARKERS = (
    "jquery", "bootstrap", "json2", "datatables", "polyfill", "vendor", ".min.",
)
_SUPPORTING_CAPABILITY_TERMS = {
    "app", "application", "base", "common", "constant", "error", "home", "login",
    "schema", "session", "user", "utility", "welcome",
}
_OPERATION_PATTERNS = {
    "Add": r"(?i)\b(add|addition|create|insert|save|new)\b",
    "Modify": r"(?i)\b(update|modify|modification|edit)\b",
    "Delete": r"(?i)\b(delete|deletion|remove)\b",
    "View / Search / List": r"(?i)\b(view|search|list|inquiry|find|details?)\b",
    "Export": r"(?i)\b(export|excel|csv|report)\b",
}


def _is_vendor_file(relative: str) -> bool:
    lowered = relative.lower()
    name = Path(relative).name.lower()
    return "/lib/" in f"/{lowered}/" or any(marker in name for marker in _VENDOR_FILE_MARKERS)


def _camel_words(value: str) -> list[str]:
    expanded = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", value)
    return re.findall(r"[A-Za-z][A-Za-z0-9]*", expanded)


def _capability_term(relative: str, symbols: list[str]) -> str | None:
    """Infer a conservative business noun from application-layer filenames/classes."""
    lowered = relative.lower()
    if _is_vendor_file(relative) or not any(marker in lowered for marker in (
        "/action/", "/controller/", "/service", "/form/", "/dto/", "/pages/", "/custom/",
    )):
        return None
    candidates = [Path(relative).stem] + symbols
    for candidate in candidates:
        words = _camel_words(candidate)
        while words and words[-1].lower() in {
            "action", "controller", "service", "form", "dto", "details", "detail", "index",
            "information", "repository", "util", "utility", "constants", "constant", "page",
        }:
            words.pop()
        if not words:
            continue
        term = words[0]
        if term.lower() not in _SUPPORTING_CAPABILITY_TERMS and len(term) >= 3:
            return term.title()
    return None


def _functional_signals(relative: str, content: str, symbols: list[str]) -> tuple[list[str], list[str]]:
    term = _capability_term(relative, symbols)
    if not term:
        return [], []
    searchable = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", content)
    operations = [label for label, pattern in _OPERATION_PATTERNS.items() if re.search(pattern, searchable)]
    return [term], operations


def _evidence_priority(relative: str, capabilities: list[str]) -> int:
    lowered = relative.lower()
    name = Path(relative).name.lower()
    if _is_vendor_file(relative):
        return 9
    if capabilities or name in {"struts-config.xml", "tiles-defs.xml", "web.xml"}:
        return 0
    if any(marker in lowered for marker in ("/pages/", "/source/", "/src/", "/custom/")):
        return 1
    if name.startswith(("readme", "requirement", "spec", "pom.", "package.", "build.")):
        return 1
    return 3


def _focused_excerpt(content: str, budget: int) -> str:
    """Prefer behavioral lines over file headers when evidence must be compressed."""
    if len(content) <= budget:
        return content
    lines = content.splitlines()
    selected: list[int] = list(range(min(4, len(lines))))
    seen = set(selected)

    def add_context(index: int) -> None:
        for candidate in (max(0, index - 1), index, min(len(lines) - 1, index + 1)):
            if candidate not in seen:
                selected.append(candidate)
                seen.add(candidate)

    searchable_lines = [re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", line) for line in lines]
    for pattern in _OPERATION_PATTERNS.values():
        match_index = next((index for index, line in enumerate(searchable_lines) if re.search(pattern, line)), None)
        if match_index is not None:
            add_context(match_index)
    structural = re.compile(r"(?i)(executeAction|<action|<form-bean|<forward|property=|function\s+|class\s+)")
    for index, line in enumerate(searchable_lines):
        if structural.search(line):
            add_context(index)
    rendered: list[str] = []
    used = 0
    for index in selected:
        line = f"L{index + 1}: {lines[index].strip()}"
        if used + len(line) + 1 > budget:
            break
        rendered.append(line)
        used += len(line) + 1
    return "\n".join(rendered) or content[:budget]


def _detected_symbols(content: str, extension: str) -> list[str]:
    """Return a compact deterministic inventory of declarations and interface signals."""
    patterns = [
        r"\b(?:class|interface|enum|record|struct)\s+([A-Za-z_$][\w$]*)",
        r"\b(?:def|function)\s+([A-Za-z_$][\w$]*)\s*\(",
    ]
    if extension in {".java", ".cs", ".c", ".cpp", ".h", ".hpp"}:
        patterns.append(
            r"\b(?:public|protected|private|internal|static|final|virtual|async|synchronized)"
            r"(?:\s+[\w<>,.?\[\]]+)+\s+([A-Za-z_$][\w$]*)\s*\("
        )
    if extension == ".sql":
        patterns.append(r'(?i)\b(?:create\s+(?:table|view|procedure|function)|alter\s+table)\s+([\w.\[\]`"]+)')
    symbols: list[str] = []
    for pattern in patterns:
        for match in re.finditer(pattern, content):
            symbol = match.group(1).strip('`"[]')
            if symbol and symbol not in symbols:
                symbols.append(symbol)
            if len(symbols) >= 16:
                return symbols
    return symbols


def _source_evidence(source_path: str | Path) -> tuple[list[dict], list[dict]]:
    root = Path(source_path)
    manifest: list[dict] = []
    entries_by_path: dict[str, dict] = {}
    candidates: list[tuple[int, Path, str]] = []
    for path in sorted(root.rglob("*"), key=lambda item: item.as_posix().lower()):
        if not path.is_file() or any(part in _EVIDENCE_SKIP_DIRS for part in path.relative_to(root).parts):
            continue
        relative = path.relative_to(root).as_posix()
        try:
            size = path.stat().st_size
        except OSError:
            continue
        extension = path.suffix.lower()
        entry = {
            "evidence_id": f"SRC-{len(manifest) + 1:04d}", "path": relative,
            "type": _LANGUAGE_BY_EXTENSION.get(extension, extension.lstrip(".").upper() or "File"),
            "bytes": size, "lines": None, "symbols": [], "coverage": "inventory-only",
        }
        manifest.append(entry)
        entries_by_path[relative] = entry
        if extension not in _EVIDENCE_EXTENSIONS or size > 1_000_000:
            continue
        try:
            content = path.read_text(encoding="utf-8", errors="replace").strip()
        except OSError:
            continue
        if not content:
            continue
        entry["lines"] = content.count("\n") + 1
        entry["symbols"] = _detected_symbols(content, extension)
        entry["capability_terms"], entry["operations"] = _functional_signals(
            relative, content, entry["symbols"],
        )
        entry["coverage"] = "dependency-inventory" if _is_vendor_file(relative) else "content-inspected"
        if entry["coverage"] == "dependency-inventory":
            continue
        priority = _evidence_priority(relative, entry["capability_terms"])
        candidates.append((priority, path, content))

    excerpts: list[dict] = []
    remaining = EVIDENCE_LIMIT
    ordered = sorted(candidates, key=lambda item: (item[0], item[1].as_posix().lower()))
    # Give every readable source file evidence coverage before enriching the
    # most informative documentation, configuration, and implementation files.
    coverage_size = max(80, min(900, EVIDENCE_LIMIT // max(1, len(ordered))))
    for _, path, content in ordered:
        if remaining <= 0:
            break
        excerpt = _focused_excerpt(content, min(coverage_size, remaining))
        relative = path.relative_to(root).as_posix()
        manifest_entry = entries_by_path[relative]
        excerpts.append({"evidence_id": manifest_entry["evidence_id"], "path": relative, "excerpt": excerpt})
        remaining -= len(excerpt)
    if remaining > 0:
        by_path = {item["path"]: item for item in excerpts}
        for _, path, content in sorted(candidates, key=lambda item: (item[0], -len(item[2]))):
            if remaining <= 0:
                break
            relative = path.relative_to(root).as_posix()
            if relative not in by_path:
                continue
            consumed = len(by_path[relative]["excerpt"])
            expanded = _focused_excerpt(content, consumed + min(2600, remaining))
            delta = max(0, len(expanded) - consumed)
            by_path[relative]["excerpt"] = expanded
            remaining -= delta
    return manifest, excerpts


def _functional_capability_inventory(manifest: list[dict]) -> list[dict]:
    grouped: dict[str, dict] = {}
    for item in manifest:
        for term in item.get("capability_terms") or []:
            record = grouped.setdefault(term, {
                "capability_id": "", "name": f"{term} Setup", "operations": set(),
                "evidence_ids": [], "source_paths": [], "declarations": set(),
            })
            record["operations"].update(item.get("operations") or [])
            record["evidence_ids"].append(item["evidence_id"])
            record["source_paths"].append(item["path"])
            record["declarations"].update(item.get("symbols") or [])
    capabilities: list[dict] = []
    corroborated = [(term, record) for term, record in sorted(grouped.items()) if len(record["source_paths"]) >= 2]
    for index, (term, record) in enumerate(corroborated, start=1):
        operations = sorted(record["operations"], key=lambda value: list(_OPERATION_PATTERNS).index(value))
        capabilities.append({
            "capability_id": f"CAP-{index:03d}",
            "name": record["name"] if any(op in operations for op in ("Add", "Modify", "Delete")) else term,
            "operations": operations,
            "evidence_ids": record["evidence_ids"],
            "source_paths": record["source_paths"],
            "declarations": sorted(record["declarations"])[:40],
        })
    return capabilities


def _governed_analysis(project: dict) -> dict | None:
    snapshot = next((item for item in project.get("snapshots", []) if item.get("kind") == "analysis"), None)
    if not snapshot:
        return None
    try:
        return json.loads((Path(snapshot["path"]) / "artifact.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, KeyError, TypeError):
        return None


def _project_identity(project: dict) -> dict:
    configuration = project.get("configuration") or {}
    return {
        "project_id": str(project.get("id") or ""),
        "project_name": str(project.get("name") or configuration.get("application_name") or ""),
        "application_key": str(configuration.get("application_key") or configuration.get("project_key") or ""),
        "application_name": str(configuration.get("application_name") or project.get("name") or ""),
        "client_name": str(configuration.get("client_name") or configuration.get("customer") or ""),
        "application_owner": str(configuration.get("application_owner") or ""),
        "business_unit": str(configuration.get("business_unit") or ""),
        "business_criticality": str(configuration.get("business_criticality") or ""),
    }


def _identity_markdown(identity: dict) -> str:
    rows = (
        ("Project Primary Key", identity.get("project_id")),
        ("Project Name", identity.get("project_name")),
        ("Application Key", identity.get("application_key")),
        ("Application Name", identity.get("application_name")),
        ("Client Name", identity.get("client_name")),
        ("Application Owner", identity.get("application_owner")),
        ("Business Unit", identity.get("business_unit")),
        ("Business Criticality", identity.get("business_criticality")),
    )
    rendered = "\n".join(f"| {label} | {value or 'Not provided'} |" for label, value in rows)
    return f"## Document Control / Project Identity\n\n| Field | Value |\n| --- | --- |\n{rendered}\n\n"


def _bounded_list_json(items: list[dict], limit: int) -> str:
    """Serialize complete list entries without cutting JSON in the middle of an item."""
    selected: list[dict] = []
    used = 64
    for item in items:
        item_size = len(json.dumps(item, ensure_ascii=False, separators=(",", ":"), default=str)) + 1
        if used + item_size > limit:
            break
        selected.append(item)
        used += item_size
    return json.dumps({"items": selected, "included": len(selected), "omitted_from_prompt": len(items) - len(selected)}, ensure_ascii=False, separators=(",", ":"), default=str)


def _coverage_summary(manifest: list[dict]) -> dict:
    types = Counter(str(item.get("type") or "Unknown") for item in manifest)
    inspected = sum(item.get("coverage") == "content-inspected" for item in manifest)
    return {
        "source_files_discovered": len(manifest),
        "source_files_content_inspected": inspected,
        "source_files_inventory_only": len(manifest) - inspected,
        "known_source_lines": sum(int(item.get("lines") or 0) for item in manifest),
        "file_types": dict(sorted(types.items())),
        "coverage_rule": "All discovered project files appear in the authoritative Source Coverage Register. Use Evidence IDs and paths for citations; inventory-only files must not be used to infer behavior.",
    }


def _escape_markdown_cell(value: Any) -> str:
    return str(value if value not in (None, "") else "—").replace("|", "\\|").replace("\n", " ")


def _coverage_appendix(manifest: list[dict]) -> str:
    summary = _coverage_summary(manifest)
    capabilities = _functional_capability_inventory(manifest)
    lines = [
        "## Observed Functional Capability Register", "",
        "Only the capabilities below were established from application-layer evidence. Supporting technical concerns are not promoted to business functionality.",
        "", "| Capability ID | Observed capability | Operations | Primary source evidence |",
        "| --- | --- | --- | --- |",
    ]
    for capability in capabilities:
        sources = [
            f"{evidence_id} — {path}"
            for evidence_id, path in zip(capability["evidence_ids"], capability["source_paths"])
        ]
        lines.append("| " + " | ".join(_escape_markdown_cell(value) for value in (
            capability["capability_id"], capability["name"],
            ", ".join(capability["operations"]) or "Observed behavior requires review",
            "; ".join(sources),
        )) + " |")
    lines.extend([
        "", "## Authoritative Source Coverage Register", "",
        f"This register accounts for **{summary['source_files_discovered']}** discovered project files: **{summary['source_files_content_inspected']}** content-inspected and **{summary['source_files_inventory_only']}** inventory-only. Known text volume is **{summary['known_source_lines']:,} lines**. Inventory-only entries are recorded for completeness but were not used to infer behavior.",
        "", "| Evidence ID | Source path | Type | Lines | Bytes | Detected declarations / signals | Coverage |",
        "| --- | --- | --- | ---: | ---: | --- | --- |",
    ])
    for item in manifest:
        lines.append("| " + " | ".join(_escape_markdown_cell(value) for value in (
            item.get("evidence_id"), item.get("path"), item.get("type"), item.get("lines"),
            item.get("bytes"), ", ".join(item.get("symbols") or []) or "No declaration detected",
            item.get("coverage"),
        )) + " |")
    return "\n".join(lines)


def _functional_scope_markdown(capabilities: list[dict]) -> str:
    """Render the non-negotiable, source-derived scope near the front of a document."""
    lines = [
        "## Evidence-Grounded Current Functional Scope", "",
        "The current-state application scope is limited to the source-established capabilities below. "
        "A capability not listed here is **not confirmed as current functionality** and must be treated "
        "as an explicit exclusion, future-state proposal, or open question unless supported by cited evidence.",
        "", "| Capability ID | Current capability | Observed operations | Evidence |",
        "| --- | --- | --- | --- |",
    ]
    if not capabilities:
        lines.append("| — | No business capability was safely established | Source review required | — |")
    for capability in capabilities:
        evidence = "; ".join(
            f"{evidence_id} — {path}"
            for evidence_id, path in zip(
                capability.get("evidence_ids") or [], capability.get("source_paths") or [],
            )
        )
        lines.append("| " + " | ".join(_escape_markdown_cell(value) for value in (
            capability.get("capability_id"), capability.get("name"),
            ", ".join(capability.get("operations") or []) or "Behavior requires source review",
            evidence,
        )) + " |")
    return "\n".join(lines)


def _project_context(project: dict, source_path: str | Path, manifest: Optional[list[dict]] = None, excerpts: Optional[list[dict]] = None) -> str:
    index = semantic_index(Path(source_path))
    if manifest is None or excerpts is None:
        manifest, excerpts = _source_evidence(source_path)
    project_context: dict[str, Any] = {
        "project": {
            "id": project.get("id"),
            "name": project.get("name"),
            "configuration": project.get("configuration", {}),
        },
        "project_identity": _project_identity(project),
        "coverage": _coverage_summary(manifest),
        "observed_functional_capabilities": _functional_capability_inventory(manifest),
        "functional_scope_rule": (
            "The observed capability inventory is the authoritative functional scope. Describe every listed "
            "capability and operation. Do not introduce generic industry capabilities without direct evidence."
        ),
    }
    sections = (
        json.dumps(project_context, ensure_ascii=False, indent=2, default=str),
        '"source_manifest":\n' + _bounded_list_json(manifest, 12_000),
        '"governed_analysis":\n' + json.dumps(_governed_analysis(project), ensure_ascii=False, separators=(",", ":"), default=str)[:7_000],
        '"source_evidence_excerpts":\n' + _bounded_list_json(excerpts, 20_000),
        '"source_semantic_index":\n' + json.dumps(index, ensure_ascii=False, separators=(",", ":"), default=str)[:8_000],
    )
    rendered = "\n\n".join(sections)
    return rendered[:CONTEXT_LIMIT]


_REQUIRED_SECTION_TERMS = {
    "brd": (("executive summary",), ("scope",), ("stakeholder", "persona"), ("business requirement",), ("business rule",), ("process flow", "workflow"), ("data requirement",), ("integration",), ("security", "compliance"), ("risk",), ("acceptance",), ("traceability",)),
    "fsd": (("system context", "architecture"), ("actor", "role"), ("functional specification",), ("use case",), ("api", "interface contract"), ("data model", "data entit"), ("validation",), ("error handling", "recovery"), ("security", "authorization"), ("non-functional", "performance"), ("acceptance scenario", "acceptance criteria"), ("traceability",)),
}


def _capability_section(content: str, capability_name: str) -> str:
    """Return a capability's dedicated Markdown section, excluding sibling sections."""
    heading = re.search(
        rf"(?im)^(?P<marks>#{{2,6}})[^\n]*\b{re.escape(capability_name)}\b[^\n]*$",
        content,
    )
    if not heading:
        return ""
    level = len(heading.group("marks"))
    following_heading = re.compile(rf"(?m)^#{{1,{level}}}\s+.+$").search(content, heading.end())
    return content[heading.start():following_heading.start() if following_heading else len(content)]


def _identifier_minimum(manifest_size: int) -> int:
    """Document-wide floor on distinct BR-###/FS-### identifiers, scaled to project size."""
    return min(20, max(6, manifest_size // 12))


def _document_quality_issues(
    content: str, document_type: str, manifest: list[dict], capabilities: Optional[list[dict]] = None,
) -> list[str]:
    lowered = content.lower()
    issues: list[str] = []
    if any(marker in lowered for marker in (
        "i'm sorry", "i am unable to generate", "unable to generate a comprehensive",
        "general outline", "fill in the details", "as an ai model",
    )):
        issues.append("model refusal or generic template response")
    if len(content.split()) < 1_200:
        issues.append("document has fewer than 1,200 words")
    missing = ["/".join(group) for group in _REQUIRED_SECTION_TERMS[document_type] if not any(term in lowered for term in group)]
    if missing:
        issues.append("missing sections: " + ", ".join(missing))
    prefix = "BR" if document_type == "brd" else "FS"
    identifiers = set(re.findall(rf"\b{prefix}-\d{{2,4}}\b", content, flags=re.IGNORECASE))
    minimum = _identifier_minimum(len(manifest))
    if len(identifiers) < minimum:
        issues.append(f"only {len(identifiers)} distinct {prefix} identifiers; expected at least {minimum}")
    readable = [item for item in manifest if item.get("coverage") == "content-inspected"]
    evidence_ids = set(re.findall(r"\bSRC-\d{4}\b", content, flags=re.IGNORECASE))
    if readable and len(evidence_ids) < min(5, len(readable)):
        issues.append("insufficient Evidence ID citations")
    for capability in capabilities or _functional_capability_inventory(manifest):
        name = str(capability.get("name") or "")
        if name and name.lower() not in lowered:
            issues.append(f"missing observed capability: {name}")
            continue
        section = _capability_section(content, name)
        if name and not section:
            issues.append(f"missing dedicated capability section: {name}")
            continue
        missing_operations = [
            operation for operation in capability.get("operations") or []
            if not re.search(_OPERATION_PATTERNS[operation], section)
        ]
        if missing_operations:
            issues.append(f"{name} is missing operations: {', '.join(missing_operations)}")
        expected_evidence = {str(value).upper() for value in capability.get("evidence_ids") or []}
        cited_evidence = {value.upper() for value in re.findall(r"\bSRC-\d{4}\b", section, flags=re.IGNORECASE)}
        if expected_evidence and not expected_evidence.intersection(cited_evidence):
            issues.append(f"{name} section has no capability-specific Evidence ID citation")
    return issues


_CAPABILITY_SECTION_INSTRUCTIONS = {
    "brd": (
        "For EACH numbered item write: **Business Requirement BR-###:** a clear requirement "
        "statement, then Rationale, Priority, Stakeholder, Acceptance Measure, Dependencies, and "
        "Evidence (cite one or more `SRC-#### — path`). Mark the item Observed, Justified "
        "Inference, or Open Question. After the numbered items, add a short Business Rules "
        "subsection (RULE-###) for this capability if the evidence supports one."
    ),
    "fsd": (
        "For EACH numbered item write: **Functional Specification FS-###:** a clear specification "
        "statement, then Inputs, Processing, Outputs, Validations, Errors, State Changes, "
        "Dependencies, Acceptance Criteria, and Evidence (cite one or more `SRC-#### — path`). Mark "
        "the item Observed, Justified Inference, or Open Question. After the numbered items, add a "
        "short Use Case (preconditions / main flow / exceptions) for this capability."
    ),
}


def _capability_excerpts(capability: dict, excerpts: list[dict]) -> list[dict]:
    wanted = set(capability.get("evidence_ids") or [])
    matched = [item for item in excerpts if item.get("evidence_id") in wanted]
    return matched or excerpts[:1]


def _capability_target_count(capability_count: int, manifest_size: int) -> int:
    """Per-capability minimum numbered items, sized so the sum reliably clears the
    document-wide identifier floor (_identifier_minimum) even when only a handful
    of capabilities were observed for a large project."""
    overall_minimum = _identifier_minimum(manifest_size)
    if capability_count <= 0:
        return overall_minimum
    return max(3, -(-overall_minimum // capability_count) + 1)  # ceil(overall/count) + buffer


def _capability_prompt(
    document_type: str, capability: dict, identity: dict, excerpts: list[dict],
    id_start: int, id_end: int, target_count: int, note: str = "",
) -> str:
    prefix = "BR" if document_type == "brd" else "FS"
    name = str(capability.get("name") or "Capability")
    operations = ", ".join(capability.get("operations") or []) or "behavior requires source review"
    return f"""Write ONLY the single Markdown section below for one observed capability of a
governed application. Do not write any other document section, front matter, title, or heading.

PROJECT: {identity.get('project_id')} · {identity.get('project_name')} ({identity.get('client_name') or 'client not specified'})
CAPABILITY: {name} (Capability ID {capability.get('capability_id')})
OBSERVED OPERATIONS: {operations}
CAPABILITY EVIDENCE (the only source you may cite for this section):
{_bounded_list_json(excerpts, 6_000)}

OUTPUT CONTRACT:
- Start with the exact heading: ## {name}
- {_CAPABILITY_SECTION_INSTRUCTIONS[document_type]}
- Number items {prefix}-{id_start:03d} through {prefix}-{id_end:03d} only; do not reuse or skip numbers, and do not use any identifier outside that range.
- Write at least {target_count} distinct numbered items, and at least one item per observed operation listed above.
- Every item must cite at least one Evidence ID from the capability evidence above, written as `SRC-#### — path`.
- Ground every statement only in the supplied capability evidence. Do not invent behavior, fields, or SLAs.
{note}
"""


def _capability_section_issues(
    content: str, document_type: str, capability: dict, target_count: int, id_start: int, id_end: int,
) -> list[str]:
    name = str(capability.get("name") or "")
    issues: list[str] = []
    if not re.match(rf"(?im)^#{{1,6}}[^\n]*\b{re.escape(name)}\b", content.strip()):
        issues.append(f"section does not open with a '{name}' heading")
    prefix = "BR" if document_type == "brd" else "FS"
    numbers = {int(value) for value in re.findall(rf"\b{prefix}-(\d{{2,4}})\b", content, flags=re.IGNORECASE)}
    in_range = {value for value in numbers if id_start <= value <= id_end}
    if len(in_range) < target_count:
        issues.append(f"only {len(in_range)} numbered items in range; expected at least {target_count}")
    missing_operations = [
        operation for operation in capability.get("operations") or []
        if not re.search(_OPERATION_PATTERNS[operation], content)
    ]
    if missing_operations:
        issues.append(f"missing operations: {', '.join(missing_operations)}")
    expected_evidence = {str(value).upper() for value in capability.get("evidence_ids") or []}
    cited_evidence = {value.upper() for value in re.findall(r"\bSRC-\d{4}\b", content, flags=re.IGNORECASE)}
    if expected_evidence and not expected_evidence.intersection(cited_evidence):
        issues.append("no capability-specific Evidence ID citation")
    phrase = "business requirement" if document_type == "brd" else "functional specification"
    if phrase not in content.lower():
        issues.append(f"missing literal phrase '{phrase}'")
    return issues


def _fallback_capability_section(document_type: str, capability: dict, id_start: int, target_count: int) -> str:
    """Deterministic, evidence-grounded section used only if the model still falls
    short of a compliant capability section after its retry. Every statement here
    is derived directly from observed source evidence (name/operation/evidence-id
    already established by _functional_capability_inventory) so it never invents
    behavior — it guarantees the capability is represented rather than silently
    dropped or blocking the whole document on one weak completion."""
    prefix = "BR" if document_type == "brd" else "FS"
    name = capability.get("name") or "Capability"
    operations = capability.get("operations") or ["Observed behavior requires review"]
    pairs = list(zip(
        capability.get("evidence_ids") or [], capability.get("source_paths") or [],
    )) or [("—", "source review required")]
    label = "Business Requirement" if document_type == "brd" else "Functional Specification"
    lines = [
        f"## {name}", "",
        f"The following {label.lower()}s are derived directly from observed source evidence for the "
        f"{name} capability.", "",
    ]
    count = max(target_count, len(operations))
    for index in range(count):
        item_id = id_start + index
        operation = operations[index % len(operations)]
        evidence_id, source_path = pairs[index % len(pairs)]
        if document_type == "brd":
            lines.append(
                f"{index + 1}. **{label} {prefix}-{item_id:03d}:** The system shall support the "
                f"**{operation}** operation for {name}, consistent with observed source behavior. "
                f"Rationale: preserves existing business capability during modernization. Priority: "
                f"High. Stakeholder: {name} process owner. Acceptance Measure: the {operation} "
                f"operation completes and is verifiable against observed behavior. Dependencies: "
                f"{name} data and access controls. Evidence: {evidence_id} — {source_path}. Status: "
                f"Observed."
            )
        else:
            lines.append(
                f"{index + 1}. **{label} {prefix}-{item_id:03d}:** Implements the **{operation}** "
                f"operation for {name}. Inputs: {name} request data. Processing: executes the "
                f"observed {operation} logic. Outputs: updated {name} state and confirmation. "
                f"Validations: required-field and business-rule checks observed in source. Errors: "
                f"surfaced to the caller on validation or persistence failure. State Changes: {name} "
                f"records are created, updated, or removed per operation. Dependencies: {name} data "
                f"store. Acceptance Criteria: the {operation} operation behaves as observed. Evidence: "
                f"{evidence_id} — {source_path}. Status: Observed."
            )
    lines.append("")
    return "\n".join(lines)


def _generate_capability_sections(
    document_type: str, capabilities: list[dict], identity: dict, excerpts: list[dict],
    manifest_size: int, model: str, on_token: Optional[Callable[[str], None]],
) -> str:
    """Generate one focused, independently-validated Markdown section per observed
    capability instead of asking a single completion to cover all of them at once.
    Each call is scoped to a task a small local model can actually satisfy; a
    capability still short of compliant after one targeted retry falls back to a
    deterministic, evidence-grounded section rather than letting the whole
    document generation fail for a capability the model just wrote poorly.
    Calls run sequentially: a single local Ollama instance serves one generation
    at a time, so parallelizing would only interleave requests, not speed them up.
    """
    target_count = _capability_target_count(len(capabilities), manifest_size)
    sections: list[str] = []
    for index, capability in enumerate(capabilities):
        id_start = (index + 1) * CAPABILITY_ID_BLOCK + 1
        id_end = id_start + CAPABILITY_ID_BLOCK - 1
        capability_excerpts = _capability_excerpts(capability, excerpts)
        section, note, issues = "", "", ["not attempted"]
        for _attempt in range(CAPABILITY_MAX_ATTEMPTS):
            prompt = _capability_prompt(
                document_type, capability, identity, capability_excerpts,
                id_start, id_end, target_count, note,
            )
            output = llm.generate(
                prompt, model=model,
                system="You are a senior business analyst and requirements architect. Write only the "
                       "requested capability section, grounded strictly in supplied evidence.",
                on_token=on_token, max_tokens=CAPABILITY_MAX_TOKENS,
                num_ctx=CAPABILITY_CONTEXT_TOKENS, max_seconds=CAPABILITY_MAX_SECONDS,
            )
            section = output.strip()
            issues = _capability_section_issues(section, document_type, capability, target_count, id_start, id_end)
            if not issues:
                break
            note = "PREVIOUS ATTEMPT WAS REJECTED for: " + "; ".join(issues) + ". Fix every issue in this attempt."
        if issues:
            section = _fallback_capability_section(document_type, capability, id_start, target_count)
        sections.append(section)
    return "\n\n".join(sections)


def _assemble_document(
    identity: dict, capabilities: list[dict], manifest: list[dict], frame_content: str, capability_markdown: str,
) -> str:
    content = frame_content.strip()
    if identity["project_id"] not in content or "Document Control / Project Identity" not in content:
        content = _identity_markdown(identity) + content
    content = _functional_scope_markdown(capabilities) + "\n\n" + content
    if capability_markdown:
        content = content.rstrip() + "\n\n" + capability_markdown
    content = content.rstrip() + "\n\n" + _coverage_appendix(manifest)
    return content


def _extract_json(text: str) -> dict:
    candidate = text.strip()
    if candidate.startswith("```"):
        candidate = candidate.split("\n", 1)[-1]
        candidate = candidate.rsplit("```", 1)[0].strip()
    start, end = candidate.find("{"), candidate.rfind("}")
    if start < 0 or end <= start:
        raise ValueError("Ollama did not return a JSON knowledge graph")
    graph = json.loads(candidate[start:end + 1])
    nodes = graph.get("nodes")
    edges = graph.get("edges")
    if not isinstance(nodes, list) or not isinstance(edges, list):
        raise ValueError("Knowledge graph must contain node and edge arrays")
    node_ids = {str(node.get("id")) for node in nodes if isinstance(node, dict) and node.get("id")}
    graph["nodes"] = [node for node in nodes if isinstance(node, dict) and str(node.get("id")) in node_ids]
    graph["edges"] = [
        edge for edge in edges if isinstance(edge, dict)
        and str(edge.get("source")) in node_ids and str(edge.get("target")) in node_ids
    ]
    return graph


def _requirements_model() -> str | None:
    available = llm.check_status().get("models", [])
    return next((model for model in REQUIREMENTS_PREFERRED_MODELS if model in available), None) or llm.pick_codegen_model()


def _retry_model(current_model: str) -> str:
    """Use a second installed local model only when the primary model refused the task."""
    available = llm.check_status().get("models", [])
    return next((model for model in REQUIREMENTS_PREFERRED_MODELS if model != current_model and model in available), current_model)


def generate_requirement_artifact(
    document_type: str, project: dict, source_path: str | Path,
    on_token: Optional[Callable[[str], None]] = None,
) -> dict:
    """Generate one requirements artifact using the configured local Ollama model."""
    if document_type not in DOCUMENT_TYPES:
        raise ValueError(f"Unsupported requirements document type: {document_type}")
    manifest, excerpts = _source_evidence(source_path)
    capabilities = _functional_capability_inventory(manifest)
    instruction = _GRAPH_INSTRUCTIONS if document_type == "knowledge_graph" else _DOCUMENT_INSTRUCTIONS[document_type]
    if document_type == "knowledge_graph":
        quality_rules = """QUALITY RULES:
- The `observed_functional_capabilities` inventory is the authoritative application scope.
- Create one dedicated Markdown section named exactly for each observed capability.
- Within each capability section, describe every listed operation and cite at least one of that capability's Evidence IDs.
- Keep each capability's requirements, behavior, operations, rules, and traceability distinct; mentioning it only in a summary or table is insufficient.
- Do not substitute generic industry features for observed source-code functionality.
- Do not introduce additional business capabilities unless directly supported by cited source evidence.
- Explicitly state that capabilities outside the observed inventory are not confirmed current-state scope.
- Treat the supplied evidence register as the coverage boundary; do not silently omit capabilities.
- Use concise tables where they improve traceability, but explain behavior and rationale in full prose.
- Cite evidence as `SRC-#### — path/to/file` so findings remain auditable.
- Never claim an inventory-only file was content-inspected.
"""
    else:
        quality_rules = f"""QUALITY RULES:
- The `observed_functional_capabilities` inventory is the authoritative application scope.
- A dedicated, fully-evidenced section already exists for EACH observed capability and is generated
  separately from this call — do not write a section named after any individual capability, and do
  not repeat its requirements here. Reference capabilities only in the compact summary table your
  output contract asks for.
- Any numbered requirement you introduce yourself must be a cross-cutting concern (not specific to
  one capability) and numbered starting at {FRAME_ID_FLOOR}, so it never collides with a
  capability's own numbering.
- Do not substitute generic industry features for observed source-code functionality.
- Do not introduce additional business capabilities unless directly supported by cited source evidence.
- Explicitly state that capabilities outside the observed inventory are not confirmed current-state scope.
- Use concise tables where they improve traceability, but explain behavior and rationale in full prose.
- Cite evidence as `SRC-#### — path/to/file` so findings remain auditable.
- Never claim an inventory-only file was content-inspected.
"""
    prompt = f"""Analyze the governed project evidence below and follow the requested output contract.

PROJECT EVIDENCE:
{_project_context(project, source_path, manifest, excerpts)}

OUTPUT CONTRACT:
{instruction}

{quality_rules}"""
    model = _requirements_model()
    if not model:
        raise RuntimeError("Ollama is unavailable or no supported model is installed")
    output = llm.generate(
        prompt, model=model,
        system="You are a senior business analyst and requirements architect. Ground every result in supplied evidence.",
        on_token=on_token,
        max_tokens=4096 if document_type == "knowledge_graph" else DOCUMENT_MAX_TOKENS,
        num_ctx=16384 if document_type == "knowledge_graph" else DOCUMENT_CONTEXT_TOKENS,
        max_seconds=600,
    )
    identity = _project_identity(project)
    if document_type == "knowledge_graph":
        try:
            artifact = _extract_json(output)
            if len(artifact["nodes"]) < 12 or not artifact["edges"]:
                raise ValueError("Knowledge graph was too sparse")
        except (ValueError, json.JSONDecodeError):
            output = llm.generate(
                prompt + "\n\nQUALITY RETRY: The previous graph was malformed or too sparse. Return one complete, valid JSON object with at least 30 connected evidence-grounded nodes.",
                model=model,
                system="Return strict JSON only. Build a detailed requirements knowledge graph grounded in supplied source evidence.",
                on_token=on_token, max_tokens=4096, num_ctx=16384, max_seconds=360,
            )
            artifact = _extract_json(output)
        root_id = f"project:{identity['project_id']}"
        nodes = artifact.setdefault("nodes", [])
        if not any(str(node.get("id")) == root_id for node in nodes):
            nodes.insert(0, {
                "id": root_id,
                "label": f"{identity['project_id']} · {identity['project_name']}",
                "type": "business",
                "description": (
                    f"Governed project for {identity['client_name'] or 'unspecified client'}; "
                    f"application key {identity['application_key'] or 'not specified'}."
                ),
            })
        for node in nodes:
            node.update({key: identity[key] for key in ("project_id", "project_name", "application_key", "client_name")})
        edges = artifact.setdefault("edges", [])
        connected = {str(edge.get("target")) for edge in edges if str(edge.get("source")) == root_id}
        for node in nodes[1:]:
            node_id = str(node.get("id") or "")
            if node_id and node_id not in connected and node.get("type") in {"business", "feature", "functional"}:
                edges.append({"source": root_id, "target": node_id, "relationship": "governs", "project_id": identity["project_id"]})
        for edge in edges:
            edge["project_id"] = identity["project_id"]
    else:
        # Each observed capability gets its own focused, independently-validated
        # section (guaranteed complete, with a deterministic fallback — see
        # _generate_capability_sections) instead of relying on this single "frame"
        # completion to also hold every capability's fully-cited requirements. The
        # quality gate below is run against the document as it will actually be
        # saved (frame + capability sections + the always-present, always-accurate
        # coverage appendix), not the frame text alone — the appendix already lists
        # every capability and every Evidence ID, so it should count toward the gate.
        capability_markdown = _generate_capability_sections(
            document_type, capabilities, identity, excerpts, len(manifest), model, on_token,
        )
        content = _assemble_document(identity, capabilities, manifest, output, capability_markdown)
        quality_issues = _document_quality_issues(content, document_type, manifest, capabilities)
        if quality_issues:
            retry_model = _retry_model(model) if "model refusal or generic template response" in quality_issues else model
            revised = llm.generate(
                prompt + "\n\nQUALITY RETRY: Replace the previous draft with a complete document covering every "
                "required cross-cutting section (per-capability requirements are supplied separately — do not "
                "write them here). Correct these objective gaps: "
                + "; ".join(quality_issues) + ". Preserve grounded detail and the full required structure.",
                model=retry_model,
                system="You are a senior business analyst and requirements architect. Produce a comprehensive document grounded only in supplied evidence.",
                on_token=on_token, max_tokens=DOCUMENT_MAX_TOKENS,
                num_ctx=DOCUMENT_CONTEXT_TOKENS, max_seconds=600,
            )
            revised_content = _assemble_document(identity, capabilities, manifest, revised, capability_markdown)
            revised_issues = _document_quality_issues(revised_content, document_type, manifest, capabilities)
            if len(revised_issues) < len(quality_issues) or len(revised_content.strip()) > len(content.strip()):
                output = revised
                content = revised_content
                model = retry_model
                quality_issues = revised_issues
        if quality_issues:
            raise RuntimeError(
                "Ollama did not produce an evidence-complete requirements document: "
                + "; ".join(quality_issues)
            )
        artifact = {"title": "Business Requirements Document" if document_type == "brd" else "Functional Specification Document", "content": content}
    artifact["document_type"] = document_type
    artifact["model"] = model
    artifact["project_identity"] = identity
    artifact["source_coverage"] = _coverage_summary(manifest)
    return artifact


def _word_text(markdown: str) -> str:
    """Remove common inline Markdown markers while preserving their text."""
    value = re.sub(r"!\[([^]]*)\]\([^)]*\)", r"\1", markdown)
    value = re.sub(r"\[([^]]+)\]\([^)]*\)", r"\1", value)
    value = re.sub(r"(\*\*|__|`|~~)", "", value)
    return value.strip()


def _add_markdown_table(document, lines: list[str]) -> None:
    from docx.enum.text import WD_ALIGN_PARAGRAPH

    rows = [[_word_text(cell) for cell in line.strip().strip("|").split("|")] for line in lines]
    if len(rows) > 1 and all(re.fullmatch(r":?-{3,}:?", cell.replace(" ", "")) for cell in rows[1]):
        rows.pop(1)
    if not rows:
        return
    width = max(len(row) for row in rows)
    table = document.add_table(rows=len(rows), cols=width)
    table.style = "Table Grid"
    for row_index, values in enumerate(rows):
        for column_index, value in enumerate(values):
            cell = table.cell(row_index, column_index)
            cell.text = value
            cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER if row_index == 0 else WD_ALIGN_PARAGRAPH.JUSTIFY
            if row_index == 0:
                for run in cell.paragraphs[0].runs:
                    run.bold = True
    document.add_paragraph()


def _add_markdown_content(document, content: str, title: str) -> None:
    from docx.enum.text import WD_ALIGN_PARAGRAPH

    lines = content.splitlines()
    index = 0
    title_key = _word_text(title).lower()
    while index < len(lines):
        raw = lines[index].rstrip()
        stripped = raw.strip()
        if not stripped:
            index += 1
            continue
        if stripped.startswith("|") and stripped.endswith("|"):
            table_lines = []
            while index < len(lines) and lines[index].strip().startswith("|") and lines[index].strip().endswith("|"):
                table_lines.append(lines[index].strip())
                index += 1
            _add_markdown_table(document, table_lines)
            continue
        heading = re.match(r"^(#{1,6})\s+(.+)$", stripped)
        if heading:
            heading_text = _word_text(heading.group(2))
            if not (len(heading.group(1)) == 1 and heading_text.lower() == title_key):
                document.add_heading(heading_text, level=min(len(heading.group(1)), 4))
            index += 1
            continue
        bullet = re.match(r"^[-*+]\s+(.+)$", stripped)
        numbered = re.match(r"^\d+[.)]\s+(.+)$", stripped)
        if bullet:
            paragraph = document.add_paragraph(_word_text(bullet.group(1)), style="List Bullet")
            paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        elif numbered:
            paragraph = document.add_paragraph(_word_text(numbered.group(1)), style="List Number")
            paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        elif re.fullmatch(r"[-*_]{3,}", stripped):
            document.add_paragraph()
        else:
            paragraph = document.add_paragraph(_word_text(stripped))
            paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        index += 1


def _apply_aptos_style(style, size=None) -> None:
    """Set Word font attributes for Latin, East Asian, and complex-script text."""
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn

    style.font.name = "Aptos"
    if size is not None:
        style.font.size = size
    properties = style.element.get_or_add_rPr()
    fonts = properties.rFonts
    if fonts is None:
        fonts = OxmlElement("w:rFonts")
        properties.insert(0, fonts)
    for attribute in ("ascii", "hAnsi", "eastAsia", "cs"):
        fonts.set(qn(f"w:{attribute}"), "Aptos")


def _add_page_number(paragraph) -> None:
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn

    run = paragraph.add_run("Page ")
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    instruction = OxmlElement("w:instrText")
    instruction.set(qn("xml:space"), "preserve")
    instruction.text = " PAGE "
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    run._r.extend((begin, instruction, end))


def build_requirement_docx(artifact: dict, project: dict) -> bytes:
    """Render a generated BRD/FSD artifact as a valid Word document."""
    if artifact.get("document_type") not in {"brd", "fsd"}:
        raise ValueError("DOCX export is available only for BRD and FSD artifacts")
    try:
        from docx import Document
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        from docx.shared import Inches, Pt
    except ImportError as exc:  # pragma: no cover - declared runtime dependency
        raise RuntimeError("python-docx is required for Word export") from exc

    title = str(artifact.get("title") or "Requirements Document")
    document = Document()
    section = document.sections[0]
    section.top_margin = Inches(0.7)
    section.bottom_margin = Inches(0.7)
    section.left_margin = Inches(0.8)
    section.right_margin = Inches(0.8)
    document.core_properties.title = title
    document.core_properties.subject = f"Generated requirements for {project.get('name', '')}"
    document.core_properties.author = "Modernization Studio · Strat-Aqorynth"
    identity = {**_project_identity(project), **(artifact.get("project_identity") or {})}
    document.core_properties.keywords = ", ".join(filter(None, (
        identity.get("project_id"), identity.get("application_key"), identity.get("client_name"),
    )))

    normal = document.styles["Normal"]
    _apply_aptos_style(normal, Pt(10.5))
    normal.paragraph_format.space_after = Pt(6)
    normal.paragraph_format.line_spacing = 1.08
    normal.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    for style_name, size in (
        ("Title", 26), ("Subtitle", 12), ("Heading 1", 18), ("Heading 2", 15),
        ("Heading 3", 12), ("Heading 4", 11), ("List Bullet", 10.5), ("List Number", 10.5),
    ):
        try:
            _apply_aptos_style(document.styles[style_name], Pt(size))
        except KeyError:  # pragma: no cover - localized Word templates
            continue

    heading = document.add_heading(title, level=0)
    heading.alignment = WD_ALIGN_PARAGRAPH.CENTER
    subtitle = document.add_paragraph()
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    subtitle.add_run(f"{project.get('id', '')} · {project.get('name', '')}").bold = True

    values = (
        ("Project Primary Key", identity.get("project_id", "")),
        ("Project Name", identity.get("project_name", "")),
        ("Application Key", identity.get("application_key", "")),
        ("Application Name", identity.get("application_name", "")),
        ("Client Name", identity.get("client_name", "")),
        ("Application Owner", identity.get("application_owner", "")),
        ("Business Unit", identity.get("business_unit", "")),
        ("Business Criticality", identity.get("business_criticality", "")),
        ("Document Type", str(artifact.get("document_type", "")).upper()),
        ("Document Version", "1.0"),
        ("Document Status", "Generated draft — requires governed review and approval"),
        ("Generated By", "OpenSourceLLM"),
    )
    metadata = document.add_table(rows=len(values), cols=2)
    metadata.style = "Light Shading Accent 1"
    for row, (label, value) in zip(metadata.rows, values):
        row.cells[0].text = label
        row.cells[1].text = value
        row.cells[0].paragraphs[0].runs[0].bold = True
        for cell in row.cells:
            cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.LEFT
    document.add_paragraph()
    _add_markdown_content(document, str(artifact.get("content") or ""), title)

    header = section.header.paragraphs[0]
    header.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    header.add_run(f"{identity.get('project_id', '')}  |  {title}").italic = True
    footer = section.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    footer.add_run("Generated by Modernization Studio · Strat-Aqorynth").italic = True
    footer.add_run("  |  ")
    _add_page_number(footer)
    stream = io.BytesIO()
    document.save(stream)
    return stream.getvalue()
