# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: SSDLC_Process_Assessment — backend/app (import_dbdata.py)
# Date: 2025-12-13
# ---------------------------------------------------------------------------
from __future__ import annotations

import re
import sqlite3
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

NS = {
    "a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "p": "http://schemas.openxmlformats.org/package/2006/relationships",
}


# Function: sanitize_column_name
def sanitize_column_name(value: str) -> str:
    sanitized = re.sub(r"[^a-z0-9]+", "_", value.strip().lower()).strip("_")
    if not sanitized:
        sanitized = "column"
    if sanitized[0].isdigit():
        sanitized = f"col_{sanitized}"
    return sanitized


# Function: shared_strings
def shared_strings(archive: zipfile.ZipFile) -> list[str]:
    if "xl/sharedStrings.xml" not in archive.namelist():
        return []
    root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
    return [
        "".join(node.text or "" for node in item.iterfind(".//a:t", NS))
        for item in root.findall("a:si", NS)
    ]


# Function: sheet_target
def sheet_target(archive: zipfile.ZipFile) -> str:
    workbook = ET.fromstring(archive.read("xl/workbook.xml"))
    rels = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
    rel_map = {rel.attrib["Id"]: rel.attrib["Target"] for rel in rels.findall("p:Relationship", NS)}
    first_sheet = workbook.find("a:sheets", NS)[0]
    rel_id = first_sheet.attrib["{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"]
    return f"xl/{rel_map[rel_id]}"


# Function: cell_value
def cell_value(cell: ET.Element, strings: list[str]) -> str | None:
    cell_type = cell.attrib.get("t")
    value_node = cell.find("a:v", NS)
    if cell_type == "s" and value_node is not None:
        return strings[int(value_node.text)]
    if cell_type == "inlineStr":
        return "".join(node.text or "" for node in cell.iterfind(".//a:t", NS))
    return value_node.text if value_node is not None else None


# Function: column_letters
def column_letters(cell_ref: str) -> str:
    match = re.match(r"([A-Z]+)", cell_ref)
    return match.group(1) if match else cell_ref


# Function: read_xlsx_rows
def read_xlsx_rows(xlsx_path: Path) -> list[dict[str, str | None]]:
    with zipfile.ZipFile(xlsx_path) as archive:
        strings = shared_strings(archive)
        worksheet = ET.fromstring(archive.read(sheet_target(archive)))
        rows = []
        for row in worksheet.findall(".//a:sheetData/a:row", NS):
            values = {}
            for cell in row.findall("a:c", NS):
                values[column_letters(cell.attrib["r"])] = cell_value(cell, strings)
            rows.append(values)
        return rows


# Function: import_workbook_to_sqlite
def import_workbook_to_sqlite(xlsx_path: Path, sqlite_path: Path) -> tuple[str, int]:
    rows = read_xlsx_rows(xlsx_path)
    if not rows:
        raise ValueError("Workbook is empty")

    header_row = rows[0]
    ordered_columns = sorted(header_row)
    headers = [header_row[column] or column for column in ordered_columns]
    column_names = [sanitize_column_name(header) for header in headers]

    table_name = sanitize_column_name(xlsx_path.stem)
    sqlite_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(sqlite_path)
    try:
        cursor = conn.cursor()
        cursor.execute(f'DROP TABLE IF EXISTS "{table_name}"')
        column_sql = ", ".join([f'"{name}" TEXT' for name in column_names])
        cursor.execute(
            f'''
            CREATE TABLE "{table_name}" (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_row INTEGER NOT NULL,
                {column_sql}
            )
            '''
        )

        insert_columns = ", ".join(['source_row'] + [f'"{name}"' for name in column_names])
        placeholders = ", ".join(["?"] * (len(column_names) + 1))
        insert_sql = f'INSERT INTO "{table_name}" ({insert_columns}) VALUES ({placeholders})'

        data_rows = rows[1:]
        for index, row in enumerate(data_rows, start=2):
            values = [row.get(column) for column in ordered_columns]
            cursor.execute(insert_sql, [index, *values])

        conn.commit()
        return table_name, len(data_rows)
    finally:
        conn.close()


# Function: main
def main() -> None:
    module_root = Path(__file__).resolve().parents[2]
    xlsx_path = module_root / "data" / "DBData.xlsx"
    sqlite_path = module_root / "data" / "DBData.sqlite"
    table_name, row_count = import_workbook_to_sqlite(xlsx_path, sqlite_path)
    print(f"Created {sqlite_path}")
    print(f"Loaded {row_count} rows into table '{table_name}'")


if __name__ == "__main__":
    main()
