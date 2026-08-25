# ---------------------------------------------------------------------------
# Scope: Ollama-backed requirements documentation for governed projects.
# ---------------------------------------------------------------------------
"""Generate BRD, FSD, and knowledge-graph artifacts from immutable source."""
from __future__ import annotations

import json
import io
import re
from pathlib import Path
from typing import Any, Callable, Optional

from services import llm
from services.governance import semantic_index

CONTEXT_LIMIT = 36_000
EVIDENCE_LIMIT = 14_000
DOCUMENT_TYPES = {"brd", "fsd", "knowledge_graph"}
REQUIREMENTS_PREFERRED_MODELS = (
    "deepseek-coder:6.7b", "qwen2.5-coder:7b", "qwen3.5:9b", "qwen2.5-coder:3b",
)

_DOCUMENT_INSTRUCTIONS = {
    "brd": """Create a detailed Business Requirements Document in Markdown. Include executive
summary and a Document Control / Project Identity table containing the supplied Project ID,
Project Name, Application Key, Client Name, Application Owner, Business Unit, and Criticality.
Include business context, objectives, scope/non-scope, stakeholders/personas, current-state
findings, business capabilities, numbered business requirements with rationale and priority,
business rules, process flows, data needs, integrations, compliance/security, assumptions,
dependencies, risks, measurable success criteria, acceptance criteria, and a traceability table.
Clearly label inferred statements and open questions; never invent certainty.""",
    "fsd": """Create a detailed Functional Specification Document in Markdown. Specify how the
observed system works and what an implementation must provide. Begin with a Document Control /
Project Identity table containing the supplied Project ID, Project Name, Application Key, Client
Name, Application Owner, Business Unit, and Criticality. Include purpose, source-evidence
coverage, system context, actors, functional decomposition, numbered functional specifications,
use cases with preconditions/main flow/alternatives/postconditions, workflows, screen and component
behavior, APIs and interface contracts, data entities/fields/validation/state transitions,
authorization, business rules, algorithms, error handling, notifications, reporting, auditability,
integrations, configuration, batch/background processing, non-functional specifications, acceptance
scenarios, and a BR-to-FS traceability matrix. Cite relevant source paths for every major capability.
Clearly distinguish observed behavior, justified inference, and open questions.""",
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
        manifest.append({"path": relative, "bytes": size})
        if path.suffix.lower() not in _EVIDENCE_EXTENSIONS or size > 1_000_000:
            continue
        try:
            content = path.read_text(encoding="utf-8", errors="replace").strip()
        except OSError:
            continue
        if not content:
            continue
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
        excerpts.append({"path": path.relative_to(root).as_posix(), "excerpt": excerpt})
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
    try:
        return json.loads((Path(snapshot["path"]) / "artifact.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _project_context(project: dict, source_path: str | Path) -> str:
    index = semantic_index(Path(source_path))
    manifest, excerpts = _source_evidence(source_path)
    project_context: dict[str, Any] = {
        "project": {
            "id": project.get("id"),
            "name": project.get("name"),
            "configuration": project.get("configuration", {}),
        },
        "project_identity": _project_identity(project),
        "coverage": {
            "source_files_discovered": len(manifest),
            "source_files_with_excerpts": len(excerpts),
            "instruction": "Cite source paths and never claim behavior unsupported by supplied evidence.",
        },
    }
    sections = (
        json.dumps(project_context, ensure_ascii=False, indent=2, default=str),
        '"source_manifest":\n' + json.dumps(manifest, ensure_ascii=False, separators=(",", ":"), default=str)[:5_000],
        '"governed_analysis":\n' + json.dumps(_governed_analysis(project), ensure_ascii=False, separators=(",", ":"), default=str)[:5_000],
        '"source_evidence_excerpts":\n' + json.dumps(excerpts, ensure_ascii=False, separators=(",", ":"), default=str)[:14_000],
        '"source_semantic_index":\n' + json.dumps(index, ensure_ascii=False, separators=(",", ":"), default=str)[:8_000],
    )
    rendered = "\n\n".join(sections)
    return rendered[:CONTEXT_LIMIT]


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
    instruction = _GRAPH_INSTRUCTIONS if document_type == "knowledge_graph" else _DOCUMENT_INSTRUCTIONS[document_type]
    prompt = f"""Analyze the governed project evidence below and follow the requested output contract.

PROJECT EVIDENCE:
{_project_context(project, source_path)}

OUTPUT CONTRACT:
{instruction}
"""
    model = _requirements_model()
    if not model:
        raise RuntimeError("Ollama is unavailable or no supported model is installed")
    output = llm.generate(
        prompt, model=model,
        system="You are a senior business analyst and requirements architect. Ground every result in supplied evidence.",
        on_token=on_token, max_tokens=4096, num_ctx=16384, max_seconds=360,
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
        if len(output.strip()) < 2_500:
            output = llm.generate(
                prompt + "\n\nQUALITY RETRY: The previous document was too brief. Produce the complete detailed specification, evidence citations, numbered requirements, scenarios, and traceability requested above.",
                model=model,
                system="You are a senior business analyst and requirements architect. Produce a comprehensive document grounded only in supplied evidence.",
                on_token=on_token, max_tokens=4096, num_ctx=16384, max_seconds=360,
            )
        content = output.strip()
        if identity["project_id"] not in content or "Document Control / Project Identity" not in content:
            content = _identity_markdown(identity) + content
        artifact = {"title": "Business Requirements Document" if document_type == "brd" else "Functional Specification Document", "content": content}
    artifact["document_type"] = document_type
    artifact["model"] = model
    artifact["project_identity"] = identity
    return artifact


def _word_text(markdown: str) -> str:
    """Remove common inline Markdown markers while preserving their text."""
    value = re.sub(r"!\[([^]]*)\]\([^)]*\)", r"\1", markdown)
    value = re.sub(r"\[([^]]+)\]\([^)]*\)", r"\1", value)
    value = re.sub(r"(\*\*|__|`|~~)", "", value)
    return value.strip()


def _add_markdown_table(document, lines: list[str]) -> None:
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
            if row_index == 0:
                for run in cell.paragraphs[0].runs:
                    run.bold = True
    document.add_paragraph()


def _add_markdown_content(document, content: str, title: str) -> None:
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
            document.add_paragraph(_word_text(bullet.group(1)), style="List Bullet")
        elif numbered:
            document.add_paragraph(_word_text(numbered.group(1)), style="List Number")
        elif re.fullmatch(r"[-*_]{3,}", stripped):
            document.add_paragraph()
        else:
            document.add_paragraph(_word_text(stripped))
        index += 1


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
    normal.font.name = "Aptos"
    normal.font.size = Pt(10.5)
    normal.paragraph_format.space_after = Pt(6)

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
        ("Generated By", "OpenSourceLLM"),
    )
    metadata = document.add_table(rows=len(values), cols=2)
    metadata.style = "Light Shading Accent 1"
    for row, (label, value) in zip(metadata.rows, values):
        row.cells[0].text = label
        row.cells[1].text = value
        row.cells[0].paragraphs[0].runs[0].bold = True
    document.add_paragraph()
    _add_markdown_content(document, str(artifact.get("content") or ""), title)

    footer = section.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    footer.add_run("Generated by Modernization Studio · Strat-Aqorynth").italic = True
    stream = io.BytesIO()
    document.save(stream)
    return stream.getvalue()
