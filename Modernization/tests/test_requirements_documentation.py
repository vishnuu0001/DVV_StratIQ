from unittest.mock import patch

import pytest

from io import BytesIO

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn

from services.requirements_documentation import (
    _capability_section, _document_quality_issues, _extract_json, _functional_capability_inventory,
    _governed_analysis, _project_context, _source_evidence, build_requirement_docx,
    generate_requirement_artifact,
)


def test_extract_json_keeps_only_edges_with_declared_nodes():
    graph = _extract_json('''```json
    {"title":"Project", "nodes":[{"id":"need","label":"Need"},{"id":"feature","label":"Feature"}],
     "edges":[{"source":"need","target":"feature","relationship":"enables"},
              {"source":"missing","target":"feature","relationship":"enables"}]}
    ```''')
    assert len(graph["edges"]) == 1
    assert graph["edges"][0]["source"] == "need"


@patch("services.requirements_documentation._document_quality_issues", return_value=[])
@patch("services.requirements_documentation._source_evidence", return_value=([{
    "evidence_id": "SRC-0001", "path": "OrderService.java", "type": "Java", "bytes": 100,
    "lines": 5, "symbols": ["OrderService"], "coverage": "content-inspected",
}], [{"evidence_id": "SRC-0001", "path": "OrderService.java", "excerpt": "class OrderService {}"}]))
@patch("services.requirements_documentation._project_context", return_value="project evidence")
@patch("services.requirements_documentation.llm.generate", return_value="# Business Requirements\n\nBR-001")
@patch("services.requirements_documentation._requirements_model", return_value="test-model")
def test_generate_brd_returns_versionable_artifact(_model, _generate, _context, _evidence, _quality):
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
    assert "Authoritative Source Coverage Register" in artifact["content"]
    assert "Evidence-Grounded Current Functional Scope" in artifact["content"]
    assert "OrderService.java" in artifact["content"]
    assert artifact["source_coverage"]["source_files_content_inspected"] == 1


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
    assert document.styles["Normal"].font.name == "Aptos"
    fonts = document.styles["Normal"].element.get_or_add_rPr().rFonts
    assert fonts.get(qn("w:ascii")) == "Aptos"
    fs_paragraph = next(paragraph for paragraph in document.paragraphs if "FS-001" in paragraph.text)
    assert fs_paragraph.alignment == WD_ALIGN_PARAGRAPH.JUSTIFY
    assert "Document Status" in table_text


def test_project_context_covers_manifest_semantics_and_source_evidence(tmp_path):
    (tmp_path / "README.md").write_text("Order processing business workflow", encoding="utf-8")
    source = tmp_path / "OrderService.py"
    source.write_text("def submit_order(order_id):\n    return order_id\n", encoding="utf-8")
    context = _project_context({"id": "APP-001", "name": "Orders", "snapshots": []}, tmp_path)
    assert '"source_files_discovered": 2' in context
    assert '"path":"OrderService.py"' in context
    assert "submit_order" in context
    assert "Order processing business workflow" in context
    assert "SRC-0001" in context and "SRC-0002" in context


def test_governed_analysis_loads_snapshot_artifact(tmp_path):
    snapshot = tmp_path / "analysis" / "v001"
    snapshot.mkdir(parents=True)
    (snapshot / "artifact.json").write_text('{"capabilities":["Order capture"]}', encoding="utf-8")
    analysis = _governed_analysis({"snapshots": [{"kind": "analysis", "path": str(snapshot)}]})
    assert analysis == {"capabilities": ["Order capture"]}


def test_capability_inventory_requires_cross_layer_evidence_and_finds_crud(tmp_path):
    files = {
        "app/action/CarrierSetupAction.java": "class CarrierSetupAction { void addCarrier(){} void deleteCarrier(){} }",
        "app/services/CarrierSetupService.java": "class CarrierSetupService { void updateCarrier(){} void searchCarrierList(){} }",
        "app/action/LocationIndexAction.java": "class LocationIndexAction { void saveLocation(){} void deleteLocation(){} }",
        "app/services/LocationInformationService.java": "class LocationInformationService { void updateLocation(){} void getLocationDetails(){} }",
        "app/pages/footer.jsp": "<button>Export</button>",
    }
    for relative, content in files.items():
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    manifest, _ = _source_evidence(tmp_path)
    capabilities = _functional_capability_inventory(manifest)
    assert [item["name"] for item in capabilities] == ["Carrier Setup", "Location Setup"]
    assert {"Add", "Modify", "Delete", "View / Search / List"}.issubset(capabilities[0]["operations"])
    assert not any(item["name"] == "Footer Setup" for item in capabilities)


def test_quality_gate_rejects_refusal_and_missing_observed_capability():
    capabilities = [{"name": "Carrier Setup", "operations": ["Add", "Delete"]}]
    issues = _document_quality_issues(
        "I'm sorry, but I am unable to generate a comprehensive document. Here is a general outline.",
        "brd", [], capabilities,
    )
    assert "model refusal or generic template response" in issues
    assert "missing observed capability: Carrier Setup" in issues


def test_quality_gate_requires_operations_and_evidence_inside_each_capability_section():
    capabilities = [
        {
            "name": "Carrier Setup", "operations": ["Add", "Delete"],
            "evidence_ids": ["SRC-0001"],
        },
        {
            "name": "Location Setup", "operations": ["Modify", "View / Search / List"],
            "evidence_ids": ["SRC-0002"],
        },
    ]
    content = """## Carrier Setup
Add a carrier. [SRC-0001 — CarrierSetupAction.java]

## Location Setup
Modify, delete, and view locations. [SRC-0002 — LocationAction.java]
""" + (" scope acceptance traceability security workflow data integration risk " * 250)
    issues = _document_quality_issues(content, "brd", [], capabilities)
    assert "Carrier Setup is missing operations: Delete" in issues
    assert "Location Setup is missing operations: Modify" not in issues
    assert _capability_section(content, "Carrier Setup").strip().endswith("CarrierSetupAction.java]")


def test_quality_gate_rejects_capability_mentioned_only_in_summary():
    issues = _document_quality_issues(
        ("Carrier Setup supports add and delete. SRC-0001. " * 300),
        "brd", [], [{
            "name": "Carrier Setup", "operations": ["Add", "Delete"],
            "evidence_ids": ["SRC-0001"],
        }],
    )
    assert "missing dedicated capability section: Carrier Setup" in issues
