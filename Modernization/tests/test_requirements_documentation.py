import re

from unittest.mock import patch

import pytest

from io import BytesIO

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn

from services.requirements_documentation import (
    _capability_section, _capability_section_issues, _capability_target_count, _document_quality_issues,
    _extract_json, _fallback_capability_section, _fallback_frame_content, _functional_capability_inventory,
    _generate_capability_sections, _governed_analysis, _project_context, _safe_generate, _source_evidence,
    build_requirement_docx, generate_requirement_artifact,
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


def test_capability_target_count_scales_to_clear_the_document_wide_identifier_floor():
    # Mirrors the reported failure: a 180-file project with only 2 observed
    # capabilities has a document-wide floor of 15 distinct BR ids, so each
    # capability must supply enough on its own that two of them clear it.
    assert _capability_target_count(2, 180) == 9
    assert _capability_target_count(0, 180) == 15
    assert _capability_target_count(6, 12) == 3  # never below the 3-item floor


def test_fallback_capability_section_is_always_gate_compliant():
    """The deterministic fallback (used only once a model completion still falls
    short after its retry) must always satisfy the same per-capability checks the
    quality gate applies to model-written sections — it's the coverage guarantee."""
    capability = {
        "name": "Carrier Setup", "operations": ["Add", "Modify", "Delete", "View / Search / List"],
        "evidence_ids": ["SRC-0001", "SRC-0002"],
        "source_paths": ["CarrierSetupAction.java", "CarrierSetupService.java"],
    }
    section = _fallback_capability_section("brd", capability, id_start=101, target_count=9)
    assert not _capability_section_issues(section, "brd", capability, target_count=9, id_start=101, id_end=200)


def test_generate_capability_sections_falls_back_when_model_never_complies():
    """Even a model that ignores the capability prompt entirely (returns junk on
    both the initial attempt and the retry) must not cause a capability to be
    dropped from the document — it must land the deterministic fallback instead."""
    capabilities = [
        {"name": "Carrier Setup", "operations": ["Add", "Delete"], "evidence_ids": ["SRC-0001"], "source_paths": ["Carrier.java"]},
        {"name": "Location Setup", "operations": ["Modify"], "evidence_ids": ["SRC-0002"], "source_paths": ["Location.java"]},
    ]
    identity = {"project_id": "APP-001", "project_name": "Orders", "client_name": "Contoso"}
    target_count = _capability_target_count(len(capabilities), 180)
    with patch("services.requirements_documentation.llm.generate", return_value="not a compliant section"):
        markdown = _generate_capability_sections(
            "brd", capabilities, identity, [], manifest_size=180, model="test-model", on_token=None,
        )
    for index, capability in enumerate(capabilities):
        id_start = (index + 1) * 100 + 1
        section = _capability_section(markdown, capability["name"])
        assert section, f"{capability['name']} section missing entirely"
        assert not _capability_section_issues(
            section, "brd", capability, target_count=target_count, id_start=id_start, id_end=id_start + 99,
        )


_FRAME_STUB = """# Business Requirements Document

## Executive Summary
Modernization scope summary for the governed application.

## Scope
In scope: observed capabilities. Out of scope: unobserved industry features.

## Stakeholders and Personas
Transportation operations stakeholders own this capability set.

## Business Rules
RULE-001: Carrier and location records must be uniquely keyed.

## Process Flow
End-to-end workflow spans intake, validation, and persistence.

## Data Requirements
Carrier and location entities require key, name, and status fields.

## Integrations
No external integrations were observed beyond internal services.

## Security and Compliance
Access is restricted to authorized transportation setup users.

## Risks
Risk: incomplete legacy validation logic. Mitigation: source-grounded review.

## Acceptance Criteria
Each capability's operations must behave as observed in source.

## Traceability Matrix
Per-capability requirement rows are appended after this section.
"""


def _transportation_setup_manifest():
    """A 180-file manifest with exactly the Carrier Setup / Location Setup shape
    of the originally reported project, so tests can reproduce its exact
    document-wide identifier floor (15) without hitting the real filesystem."""
    capability_entries = [
        {"evidence_id": "SRC-0001", "path": "app/action/CarrierSetupAction.java", "type": "Java",
         "bytes": 100, "lines": 20, "symbols": ["CarrierSetupAction"], "coverage": "content-inspected",
         "capability_terms": ["Carrier"], "operations": ["Add", "Delete"]},
        {"evidence_id": "SRC-0002", "path": "app/services/CarrierSetupService.java", "type": "Java",
         "bytes": 100, "lines": 20, "symbols": ["CarrierSetupService"], "coverage": "content-inspected",
         "capability_terms": ["Carrier"], "operations": ["Modify", "View / Search / List"]},
        {"evidence_id": "SRC-0003", "path": "app/action/LocationIndexAction.java", "type": "Java",
         "bytes": 100, "lines": 20, "symbols": ["LocationIndexAction"], "coverage": "content-inspected",
         "capability_terms": ["Location"], "operations": ["Add", "Delete"]},
        {"evidence_id": "SRC-0004", "path": "app/services/LocationInformationService.java", "type": "Java",
         "bytes": 100, "lines": 20, "symbols": ["LocationInformationService"], "coverage": "content-inspected",
         "capability_terms": ["Location"], "operations": ["Modify", "View / Search / List"]},
    ]
    filler = [
        {"evidence_id": f"SRC-{9000 + i:04d}", "path": f"filler/File{i}.txt", "type": "Text",
         "bytes": 10, "lines": 1, "symbols": [], "coverage": "inventory-only"}
        for i in range(176)
    ]
    manifest = capability_entries + filler  # 180 files, matching the reported project's manifest size
    excerpts = [{"evidence_id": item["evidence_id"], "path": item["path"], "excerpt": item["symbols"][0]} for item in capability_entries]
    return manifest, excerpts


def test_generate_requirement_artifact_succeeds_end_to_end_for_the_reported_scenario():
    """Reproduces the exact reported failure shape — a 180-file project with only
    Carrier Setup and Location Setup as observed capabilities, needing >=15 distinct
    BR ids — using a frame completion that covers only the cross-cutting sections
    (as the new prompt asks) and a capability model that never writes a compliant
    section. Generation must still succeed, with both capabilities fully covered."""
    manifest, excerpts = _transportation_setup_manifest()

    with patch("services.requirements_documentation._source_evidence", return_value=(manifest, excerpts)), \
         patch("services.requirements_documentation._project_context", return_value="project evidence"), \
         patch("services.requirements_documentation._requirements_model", return_value="test-model"), \
         patch("services.requirements_documentation.llm.generate", return_value=_FRAME_STUB):
        artifact = generate_requirement_artifact("brd", {
            "id": "APP-002", "name": "TransportationSetup",
            "configuration": {"application_key": "TRANSPORT", "client_name": "Contoso"},
        }, ".")

    content = artifact["content"]
    assert "## Carrier Setup" in content
    assert "## Location Setup" in content
    identifiers = set(re.findall(r"\bBR-\d{2,4}\b", content))
    assert len(identifiers) >= 15
    issues = _document_quality_issues(content, "brd", manifest, _functional_capability_inventory(manifest))
    assert issues == []


def test_safe_generate_converts_a_timeout_into_an_empty_result():
    """A single slow/failed completion must not blow up the whole multi-call
    pipeline — _safe_generate is what lets the frame and each capability call
    fail independently without aborting already-validated work elsewhere."""
    with patch(
        "services.requirements_documentation.llm.generate",
        side_effect=TimeoutError("Ollama generation exceeded the 600s per-file budget"),
    ):
        assert _safe_generate("frame", prompt="x", model="test-model") == ""


def test_fallback_frame_content_is_gate_compliant_and_flagged_for_review():
    manifest, _ = _transportation_setup_manifest()
    capabilities = _functional_capability_inventory(manifest)
    identity = {"project_id": "APP-002", "project_name": "TransportationSetup", "client_name": "Contoso"}
    frame = _fallback_frame_content("brd", identity, capabilities, manifest)
    assert "Automated Narrative Generation Notice" in frame
    issues = _document_quality_issues(frame, "brd", [], [])  # required-section-terms coverage in isolation
    assert not any(issue.startswith("missing sections") for issue in issues)


def test_generate_requirement_artifact_survives_every_ollama_call_timing_out():
    """The hardened failure mode: Ollama is reachable (a model is configured)
    but every single completion — the frame's two attempts and every capability
    attempt — times out. Generation must still produce a complete, gate-passing
    document via the deterministic fallbacks instead of raising."""
    manifest, excerpts = _transportation_setup_manifest()

    with patch("services.requirements_documentation._source_evidence", return_value=(manifest, excerpts)), \
         patch("services.requirements_documentation._project_context", return_value="project evidence"), \
         patch("services.requirements_documentation._requirements_model", return_value="test-model"), \
         patch(
             "services.requirements_documentation.llm.generate",
             side_effect=TimeoutError("Ollama generation exceeded the 600s per-file budget"),
         ):
        artifact = generate_requirement_artifact("brd", {
            "id": "APP-003", "name": "TransportationSetup",
            "configuration": {"application_key": "TRANSPORT", "client_name": "Contoso"},
        }, ".")

    content = artifact["content"]
    assert "## Carrier Setup" in content
    assert "## Location Setup" in content
    assert "Automated Narrative Generation Notice" in content
    identifiers = set(re.findall(r"\bBR-\d{2,4}\b", content))
    assert len(identifiers) >= 15
    issues = _document_quality_issues(content, "brd", manifest, _functional_capability_inventory(manifest))
    assert issues == []
