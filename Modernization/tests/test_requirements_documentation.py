from unittest.mock import patch

import pytest

from io import BytesIO

from docx import Document

from services.requirements_documentation import (
    _extract_json, _project_context, build_requirement_docx, generate_requirement_artifact,
)


def test_extract_json_keeps_only_edges_with_declared_nodes():
    graph = _extract_json('''```json
    {"title":"Project", "nodes":[{"id":"need","label":"Need"},{"id":"feature","label":"Feature"}],
     "edges":[{"source":"need","target":"feature","relationship":"enables"},
              {"source":"missing","target":"feature","relationship":"enables"}]}
    ```''')
    assert len(graph["edges"]) == 1
    assert graph["edges"][0]["source"] == "need"


@patch("services.requirements_documentation._project_context", return_value="project evidence")
@patch("services.requirements_documentation.llm.generate", return_value="# Business Requirements\n\nBR-001")
@patch("services.requirements_documentation._requirements_model", return_value="test-model")
def test_generate_brd_returns_versionable_artifact(_model, _generate, _context):
    artifact = generate_requirement_artifact("brd", {
        "id": "APP-001", "name": "Orders",
        "configuration": {"application_key": "ORDERS", "client_name": "Contoso"},
    }, ".")
    assert artifact["document_type"] == "brd"
    assert artifact["model"] == "test-model"
    assert "BR-001" in artifact["content"]
    assert artifact["project_identity"]["project_id"] == "APP-001"
    assert artifact["project_identity"]["application_key"] == "ORDERS"
    assert artifact["project_identity"]["client_name"] == "Contoso"


def test_rejects_unknown_document_type():
    with pytest.raises(ValueError, match="Unsupported"):
        generate_requirement_artifact("unknown", {}, ".")


def test_build_requirement_docx_creates_native_word_structures():
    content = """# Functional Specification Document

## Functional Specifications
1. **FS-001:** The system shall export Word documents.

| ID | Requirement |
| --- | --- |
| FS-001 | Export DOCX |
"""
    raw = build_requirement_docx(
        {"document_type": "fsd", "title": "Functional Specification Document", "content": content, "model": "test-model"},
        {"id": "APP-004", "name": "Example Project", "configuration": {
            "application_key": "EXAMPLE", "client_name": "Contoso", "application_owner": "Jane Doe",
        }},
    )
    assert raw.startswith(b"PK")
    document = Document(BytesIO(raw))
    assert any("FS-001" in paragraph.text for paragraph in document.paragraphs)
    assert any("Export DOCX" in cell.text for table in document.tables for row in table.rows for cell in row.cells)
    table_text = [cell.text for table in document.tables for row in table.rows for cell in row.cells]
    assert "Project Primary Key" in table_text and "APP-004" in table_text
    assert "Application Key" in table_text and "EXAMPLE" in table_text
    assert "Client Name" in table_text and "Contoso" in table_text


def test_project_context_covers_manifest_semantics_and_source_evidence(tmp_path):
    (tmp_path / "README.md").write_text("Order processing business workflow", encoding="utf-8")
    source = tmp_path / "OrderService.py"
    source.write_text("def submit_order(order_id):\n    return order_id\n", encoding="utf-8")
    context = _project_context({"id": "APP-001", "name": "Orders", "snapshots": []}, tmp_path)
    assert '"source_files_discovered": 2' in context
    assert '"path":"OrderService.py"' in context
    assert "submit_order" in context
    assert "Order processing business workflow" in context
