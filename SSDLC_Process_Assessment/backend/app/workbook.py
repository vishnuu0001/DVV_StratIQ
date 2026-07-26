# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: SSDLC_Process_Assessment — backend/app (workbook.py)
# Date: 2025-09-27
# ---------------------------------------------------------------------------
from __future__ import annotations

import re
import zipfile
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

NS = {
    "a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "p": "http://schemas.openxmlformats.org/package/2006/relationships",
    "x14": "http://schemas.microsoft.com/office/spreadsheetml/2009/9/main",
    "xm": "http://schemas.microsoft.com/office/excel/2006/main",
}

LEVELS = [
    {"key": "Early", "label": "Early (1)", "score": 1},
    {"key": "Emerging", "label": "Emerging (2)", "score": 2},
    {"key": "Mature", "label": "Mature (3)", "score": 3},
    {"key": "Fully Mature", "label": "Fully Mature (4)", "score": 4},
]

EDITABLE_TOWERS = {
    "huntsville-apps-ot": {"sheet": "Huntsville Apps OT_v2", "name": "Huntsville Apps OT"},
    "data-ai": {"sheet": "Data AI_v2", "name": "Data AI"},
    "infrastructure": {"sheet": "Infrastructure_v2", "name": "Infrastructure"},
}


class WorkbookTemplateLoader:
    # Function: __init__
    def __init__(self, workbook_path: Path):
        self.workbook_path = workbook_path

    # Function: load
    def load(self) -> dict[str, Any]:
        with zipfile.ZipFile(self.workbook_path) as archive:
            sheet_targets = self._sheet_targets(archive)
            shared_strings = self._shared_strings(archive)

            templates = {}
            for tower_key, meta in EDITABLE_TOWERS.items():
                templates[tower_key] = self._load_tower_sheet(
                    archive,
                    sheet_targets[meta["sheet"]],
                    tower_key=tower_key,
                    name=meta["name"],
                    sheet_name=meta["sheet"],
                    shared_strings=shared_strings,
                )

            applications_reference = self._load_tower_sheet(
                archive,
                sheet_targets["Applications_v2"],
                tower_key="applications-reference",
                name="Applications Reference",
                sheet_name="Applications_v2",
                shared_strings=shared_strings,
            )
            dashboard_template = self._load_dashboard_template(
                archive,
                sheet_targets["Executive Dashboard_v2"],
                shared_strings,
            )

        return {
            "levels": LEVELS,
            "editable_towers": templates,
            "applications_reference": applications_reference,
            "dashboard_template": dashboard_template,
        }

    # Function: _sheet_targets
    def _sheet_targets(self, archive: zipfile.ZipFile) -> dict[str, str]:
        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        rels = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        rel_map = {rel.attrib["Id"]: rel.attrib["Target"] for rel in rels.findall("p:Relationship", NS)}

        targets: dict[str, str] = {}
        for sheet in workbook.find("a:sheets", NS):
            rel_id = sheet.attrib["{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"]
            targets[sheet.attrib["name"]] = f"xl/{rel_map[rel_id]}"
        return targets

    # Function: _shared_strings
    def _shared_strings(self, archive: zipfile.ZipFile) -> list[str]:
        if "xl/sharedStrings.xml" not in archive.namelist():
            return []
        root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
        return [
            "".join(node.text or "" for node in item.iterfind(".//a:t", NS))
            for item in root.findall("a:si", NS)
        ]

    # Function: _cell_value
    def _cell_value(self, cell: ET.Element, shared_strings: list[str]) -> str | None:
        cell_type = cell.attrib.get("t")
        value_node = cell.find("a:v", NS)
        if cell_type == "s" and value_node is not None:
            return shared_strings[int(value_node.text)]
        if cell_type == "inlineStr":
            return "".join(node.text or "" for node in cell.iterfind(".//a:t", NS))
        return value_node.text if value_node is not None else None

    # Function: _worksheet_cells
    def _worksheet_cells(
        self,
        archive: zipfile.ZipFile,
        target: str,
        shared_strings: list[str],
    ) -> dict[str, str | None]:
        root = ET.fromstring(archive.read(target))
        return {
            cell.attrib["r"]: self._cell_value(cell, shared_strings)
            for cell in root.findall(".//a:c", NS)
        }

    # Function: _row_maturity_options
    @staticmethod
    def _row_maturity_options(cells: dict[str, str | None], row_number: int) -> list[dict[str, Any]]:
        return [
            {
                "key": level["key"],
                "label": level["label"],
                "score": level["score"],
                "description": cells.get(f"{column}{row_number}") or "",
            }
            for level, column in zip(LEVELS, ["D", "E", "F", "G"], strict=True)
        ]

    # Function: _build_response_row
    def _build_response_row(self, cells: dict[str, str | None], row_number: int) -> dict[str, Any]:
        return {
            "id": f"row-{row_number}",
            "rowNumber": row_number,
            "dimension": cells.get(f"A{row_number}") or "",
            "phase": cells.get(f"B{row_number}") or "",
            "question": cells.get(f"C{row_number}") or "",
            "maturityOptions": self._row_maturity_options(cells, row_number),
            "weight": int(float(cells.get(f"J{row_number}") or 0)),
            "selectedLevelKey": self._normalize_level_key(cells.get(f"H{row_number}")),
            "evidence": cells.get(f"L{row_number}") or "",
            "gapRecommendation": cells.get(f"M{row_number}") or "",
            "recommendationSource": "workbook" if cells.get(f"M{row_number}") else None,
            "recommendationModel": None,
        }

    # Function: _load_tower_responses
    def _load_tower_responses(self, cells: dict[str, str | None]) -> list[dict[str, Any]]:
        responses: list[dict[str, Any]] = []
        row_number = 6
        while cells.get(f"A{row_number}") and cells.get(f"J{row_number}"):
            responses.append(self._build_response_row(cells, row_number))
            row_number += 1
        return responses

    # Function: _collect_dimensions
    @staticmethod
    def _collect_dimensions(responses: list[dict[str, Any]]) -> list[str]:
        dimensions: list[str] = []
        for response in responses:
            if response["dimension"] not in dimensions:
                dimensions.append(response["dimension"])
        return dimensions

    # Function: _load_tower_sheet
    def _load_tower_sheet(
        self,
        archive: zipfile.ZipFile,
        target: str,
        tower_key: str,
        name: str,
        sheet_name: str,
        shared_strings: list[str],
    ) -> dict[str, Any]:
        cells = self._worksheet_cells(archive, target, shared_strings)
        responses = self._load_tower_responses(cells)

        return {
            "key": tower_key,
            "name": name,
            "sheetName": sheet_name,
            "description": cells.get("A1") or name,
            "instructions": cells.get("A2") or "",
            "responses": responses,
            "dimensions": self._collect_dimensions(responses),
        }

    # Function: _load_dashboard_template
    def _load_dashboard_template(
        self,
        archive: zipfile.ZipFile,
        target: str,
        shared_strings: list[str],
    ) -> dict[str, Any]:
        cells = self._worksheet_cells(archive, target, shared_strings)
        dimension_order = []
        row_number = 11
        while cells.get(f"A{row_number}"):
            dimension_order.append(cells[f"A{row_number}"])
            row_number += 1

        return {
            "dimensionOrder": dimension_order,
            "targetPct": int(float(cells.get("G5") or cells.get("G6") or cells.get("G7") or 80)),
        }

    # Function: _normalize_level_key
    def _normalize_level_key(self, value: str | None) -> str | None:
        if not value:
            return None
        cleaned = re.sub(r"\s+\(\d+\)$", "", value.strip())
        return cleaned if cleaned in {level["key"] for level in LEVELS} else None


class UIWorkbookLoader:
    # Function: __init__
    def __init__(self, workbook_path: Path):
        self.workbook_path = workbook_path

    # Function: load
    def load(self) -> dict[str, list[str]]:
        with zipfile.ZipFile(self.workbook_path) as archive:
            sheet_targets = self._sheet_targets(archive)
            shared_strings = self._shared_strings(archive)
            validations = self._ui_validations(
                archive,
                target=sheet_targets["UI"],
            )

            return {
                "applications": self._range_values(archive, sheet_targets, shared_strings, validations.get("A3")),
                "dimensions": self._range_values(archive, sheet_targets, shared_strings, validations.get("B3")),
                "phases": self._range_values(archive, sheet_targets, shared_strings, validations.get("C3")),
                "questions": self._range_values(archive, sheet_targets, shared_strings, validations.get("D3")),
                "currentStates": self._range_values(archive, sheet_targets, shared_strings, validations.get("E3")),
            }

    # Function: _sheet_targets
    def _sheet_targets(self, archive: zipfile.ZipFile) -> dict[str, str]:
        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        rels = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        rel_map = {rel.attrib["Id"]: rel.attrib["Target"] for rel in rels.findall("p:Relationship", NS)}

        targets: dict[str, str] = {}
        for sheet in workbook.find("a:sheets", NS):
            rel_id = sheet.attrib["{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"]
            targets[sheet.attrib["name"]] = f"xl/{rel_map[rel_id]}"
        return targets

    # Function: _shared_strings
    def _shared_strings(self, archive: zipfile.ZipFile) -> list[str]:
        if "xl/sharedStrings.xml" not in archive.namelist():
            return []
        root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
        return [
            "".join(node.text or "" for node in item.iterfind(".//a:t", NS))
            for item in root.findall("a:si", NS)
        ]

    # Function: _ui_validations
    def _ui_validations(self, archive: zipfile.ZipFile, target: str) -> dict[str, str]:
        root = ET.fromstring(archive.read(target))
        validations: dict[str, str] = {}
        for node in root.findall(".//x14:dataValidation", NS):
            formula = node.find("x14:formula1/xm:f", NS)
            sqref = node.find("xm:sqref", NS)
            if formula is None or sqref is None or not sqref.text:
                continue
            validations[sqref.text.strip()] = formula.text.strip()
        return validations

    # Function: _range_values
    def _range_values(
        self,
        archive: zipfile.ZipFile,
        sheet_targets: dict[str, str],
        shared_strings: list[str],
        formula: str | None,
    ) -> list[str]:
        if not formula:
            return []

        match = re.fullmatch(r"'?([^']+)'?!\$(\w+)\$(\d+):\$(\w+)\$(\d+)", formula)
        if not match:
            return []

        sheet_name, start_col, start_row, end_col, end_row = match.groups()
        cells = self._worksheet_cells(archive, sheet_targets[sheet_name], shared_strings)
        values: list[str] = []
        for col_index in range(self._col_to_int(start_col), self._col_to_int(end_col) + 1):
            for row_index in range(int(start_row), int(end_row) + 1):
                ref = f"{self._int_to_col(col_index)}{row_index}"
                value = (cells.get(ref) or "").strip()
                if value and value not in values:
                    values.append(value)
        return values

    # Function: _worksheet_cells
    def _worksheet_cells(
        self,
        archive: zipfile.ZipFile,
        target: str,
        shared_strings: list[str],
    ) -> dict[str, str]:
        root = ET.fromstring(archive.read(target))
        cells: dict[str, str] = {}
        for cell in root.findall(".//a:c", NS):
            ref = cell.attrib["r"]
            cell_type = cell.attrib.get("t")
            value_node = cell.find("a:v", NS)
            if cell_type == "s" and value_node is not None:
                value = shared_strings[int(value_node.text)]
            elif cell_type == "inlineStr":
                value = "".join(node.text or "" for node in cell.iterfind(".//a:t", NS))
            else:
                value = value_node.text if value_node is not None else ""
            cells[ref] = value or ""
        return cells

    # Function: _col_to_int
    def _col_to_int(self, col_ref: str) -> int:
        value = 0
        for char in col_ref:
            value = (value * 26) + (ord(char.upper()) - 64)
        return value

    # Function: _int_to_col
    def _int_to_col(self, index: int) -> str:
        result = []
        while index > 0:
            index, remainder = divmod(index - 1, 26)
            result.append(chr(65 + remainder))
        return "".join(reversed(result))
