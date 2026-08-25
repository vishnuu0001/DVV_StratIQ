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

_DOCUMENT_INSTRUCTIONS = {
    "brd": """Create a production-grade Business Requirements Document in Markdown. It must be
detailed enough for executive approval, product planning, solution design, and acceptance testing.
Include: Document Control / Project Identity; Executive Summary; Business Context and Objectives;
Scope and Explicit Exclusions; Stakeholders and Personas; Current-State Assessment; Business
Capabilities; numbered Business Requirements (BR-###) with statement, rationale, priority,
stakeholder, acceptance measure, dependencies, and evidence; Business Rules (RULE-###); end-to-end
Process Flows including alternatives and exceptions; Data Requirements; Integrations; Security,
Privacy, Compliance and Audit; Reporting; Non-functional Business Expectations; Assumptions,
Dependencies, Constraints, Risks and Mitigations; Measurable Success Criteria; Acceptance Criteria;
Open Questions; and a requirement-to-source Traceability Matrix. Cover every capability found in
the evidence, not only a top-N sample. Every requirement and major assertion must cite one or more
Evidence IDs and source paths. Mark each statement Observed, Justified Inference, or Open Question.
Do not invent certainty, stakeholders, SLAs, or behavior unsupported by evidence.""",
    "fsd": """Create a production-grade Functional Specification Document in Markdown. It must be
detailed enough for engineering implementation, test design, security review, operations, and
release approval. Include: Document Control / Project Identity; Purpose; Source-Evidence Coverage;
System Context and Architecture; Actors, Roles and Authorization; Functional Decomposition;
numbered Functional Specifications (FS-###) with inputs, processing, outputs, validations, errors,
state changes, dependencies, acceptance criteria, and evidence; detailed Use Cases with
preconditions/main flow/alternatives/exceptions/postconditions; Workflows; Screen and Component
Behavior; APIs and Interface Contracts including methods, schemas, status/error behavior and
idempotency where evidenced; Data Model with entities, fields, keys, relationships, validation,
retention and state transitions; Business Rules and Algorithms; Error Handling and Recovery;
Notifications; Reporting; Auditability and Observability; Integrations; Configuration; Batch and
Background Processing; Security and Privacy; Performance, Scalability, Availability and other
non-functional specifications; Deployment and Operational Considerations; Acceptance Scenarios;
Open Questions; and BR-to-FS-to-source Traceability. Cover every implementation capability found
in the evidence, not only a top-N sample. Every specification and major assertion must cite one or
more Evidence IDs and source paths. Mark each statement Observed, Justified Inference, or Open
Question. Do not invent contracts, field semantics, SLAs, or behavior unsupported by evidence.""",
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
    ".php", ".rb", ".c", ".cpp", ".h", ".hpp", ".sql", ".graphql", ".xml",
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
}


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
        entry["coverage"] = "content-inspected"
        name = path.name.lower()
        priority = 0 if name.startswith(("readme", "requirement", "spec", "pom.", "package.", "build.")) else 1
        candidates.append((priority, path, content))

    excerpts: list[dict] = []
    remaining = EVIDENCE_LIMIT
    ordered = sorted(candidates, key=lambda item: (item[0], item[1].as_posix().lower()))
    # Give every readable source file evidence coverage before enriching the
    # most informative documentation, configuration, and implementation files.
    coverage_size = max(180, min(900, EVIDENCE_LIMIT // max(1, len(ordered))))
    for _, path, content in ordered:
        if remaining <= 0:
            break
        excerpt = content[:min(coverage_size, remaining)]
        relative = path.relative_to(root).as_posix()
        manifest_entry = next(item for item in manifest if item["path"] == relative)
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
            extra = content[consumed:consumed + min(2600, remaining)]
            by_path[relative]["excerpt"] += extra
            remaining -= len(extra)
    return manifest, excerpts


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
    for item in items:
        candidate = json.dumps({"items": selected + [item]}, ensure_ascii=False, separators=(",", ":"), default=str)
        if len(candidate) > limit:
            break
        selected.append(item)
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
    lines = [
        "## Authoritative Source Coverage Register", "",
        f"This register accounts for **{summary['source_files_discovered']}** discovered project files: **{summary['source_files_content_inspected']}** content-inspected and **{summary['source_files_inventory_only']}** inventory-only. Known text volume is **{summary['known_source_lines']:,} lines**. Inventory-only entries are recorded for completeness but were not used to infer behavior.",
        "", "| Evidence ID | Source path | Type | Lines | Bytes | Detected declarations / signals | Coverage |",
        "| --- | --- | --- | ---: | ---: | --- | --- |",
    ]
    for item in manifest:
        lines.append("| " + " | ".join(_escape_markdown_cell(value) for value in (
            item.get("evidence_id"), item.get("path"), item.get("type"), item.get("lines"),
            item.get("bytes"), ", ".join(item.get("symbols") or []) or "No declaration detected",
            item.get("coverage"),
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


def _document_quality_issues(content: str, document_type: str, manifest: list[dict]) -> list[str]:
    lowered = content.lower()
    issues: list[str] = []
    if len(content.split()) < 1_200:
        issues.append("document has fewer than 1,200 words")
    missing = ["/".join(group) for group in _REQUIRED_SECTION_TERMS[document_type] if not any(term in lowered for term in group)]
    if missing:
        issues.append("missing sections: " + ", ".join(missing))
    prefix = "BR" if document_type == "brd" else "FS"
    identifiers = set(re.findall(rf"\b{prefix}-\d{{2,4}}\b", content, flags=re.IGNORECASE))
    minimum = min(20, max(6, len(manifest) // 12))
    if len(identifiers) < minimum:
        issues.append(f"only {len(identifiers)} distinct {prefix} identifiers; expected at least {minimum}")
    readable = [item for item in manifest if item.get("coverage") == "content-inspected"]
    evidence_ids = set(re.findall(r"\bSRC-\d{4}\b", content, flags=re.IGNORECASE))
    if readable and len(evidence_ids) < min(5, len(readable)):
        issues.append("insufficient Evidence ID citations")
    return issues


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


def generate_requirement_artifact(
    document_type: str, project: dict, source_path: str | Path,
    on_token: Optional[Callable[[str], None]] = None,
) -> dict:
    """Generate one requirements artifact using the configured local Ollama model."""
    if document_type not in DOCUMENT_TYPES:
        raise ValueError(f"Unsupported requirements document type: {document_type}")
    manifest, excerpts = _source_evidence(source_path)
    instruction = _GRAPH_INSTRUCTIONS if document_type == "knowledge_graph" else _DOCUMENT_INSTRUCTIONS[document_type]
    prompt = f"""Analyze the governed project evidence below and follow the requested output contract.

PROJECT EVIDENCE:
{_project_context(project, source_path, manifest, excerpts)}

OUTPUT CONTRACT:
{instruction}

QUALITY RULES:
- Treat the supplied evidence register as the coverage boundary; do not silently omit capabilities.
- Use concise tables where they improve traceability, but explain behavior and rationale in full prose.
- Cite evidence as `SRC-#### — path/to/file` so findings remain auditable.
- Never claim an inventory-only file was content-inspected.
"""
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
        quality_issues = _document_quality_issues(output, document_type, manifest)
        if quality_issues:
            revised = llm.generate(
                prompt + "\n\nQUALITY RETRY: Replace the previous draft with a complete document. Correct these objective gaps: "
                + "; ".join(quality_issues) + ". Preserve grounded detail and the full required structure.",
                model=model,
                system="You are a senior business analyst and requirements architect. Produce a comprehensive document grounded only in supplied evidence.",
                on_token=on_token, max_tokens=DOCUMENT_MAX_TOKENS,
                num_ctx=DOCUMENT_CONTEXT_TOKENS, max_seconds=600,
            )
            revised_issues = _document_quality_issues(revised, document_type, manifest)
            if len(revised_issues) < len(quality_issues) or len(revised.strip()) > len(output.strip()):
                output = revised
        content = output.strip()
        if identity["project_id"] not in content or "Document Control / Project Identity" not in content:
            content = _identity_markdown(identity) + content
        content = content.rstrip() + "\n\n" + _coverage_appendix(manifest)
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
