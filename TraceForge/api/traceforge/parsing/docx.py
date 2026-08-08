# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: §4.2 .docx parser: walk paragraphs + tables, retain heading hierarchy.
# Date: 2026-06-06
# ---------------------------------------------------------------------------
"""§4.2 .docx parser: walk paragraphs + tables, retain heading hierarchy.
python-docx exposes no real page boundaries (that's a rendering-time concept), so the
locator granularity here is section heading + char offsets, per the spec's own
'page (approx)' note for this format."""
from __future__ import annotations

from docx import Document
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P
from docx.table import Table
from docx.text.paragraph import Paragraph

from traceforge.parsing.common import ParsedBlock, ParsedDocument

_HEADING_STYLES = {f"Heading {i}" for i in range(1, 7)}


# Function: _current_section
def _current_section(heading_stack: list[str]) -> str:
    return " > ".join(heading_stack) if heading_stack else "(document start)"


# Function: _emit
def _emit(blocks: list[ParsedBlock], heading_stack: list[str], cursor: int, text: str) -> int:
    text = text.strip()
    if not text:
        return cursor
    start = cursor
    end = start + len(text)
    blocks.append(ParsedBlock(text=text, section_path=_current_section(heading_stack), char_start=start, char_end=end))
    return end + 1  # +1 for the implicit paragraph break


# Function: _process_paragraph
def _process_paragraph(blocks: list[ParsedBlock], heading_stack: list[str], cursor: int, para) -> int:
    style_name = (para.style.name if para.style else "") or ""
    text = para.text.strip()
    if not text:
        return cursor
    if style_name in _HEADING_STYLES:
        level = int(style_name.split()[-1])
        heading_stack[:] = heading_stack[: level - 1]
        heading_stack.append(text)
    elif style_name.startswith("List"):
        # Retain the structural signal used by extraction completeness checks.
        # Word list glyphs are numbering properties and are absent from para.text.
        text = f"• {text}"
    return _emit(blocks, heading_stack, cursor, text)


# Function: _process_table
def _process_table(blocks: list[ParsedBlock], heading_stack: list[str], cursor: int, table) -> int:
    for row in table.rows:
        cells = [" ".join(cell.text.split()) for cell in row.cells]
        row_text = " | ".join(cell for cell in cells if cell)
        if row_text:
            cursor = _emit(blocks, heading_stack, cursor, row_text)  # never split a table row (spec §4.3)
    return cursor


# Function: parse_docx
def parse_docx(path: str) -> ParsedDocument:
    doc = Document(path)
    blocks: list[ParsedBlock] = []
    heading_stack: list[str] = []
    cursor = 0

    # Walk the underlying body once. Iterating ``paragraphs`` and ``tables``
    # separately moves every table to the end and corrupts interleaved context.
    for child in doc.element.body.iterchildren():
        if isinstance(child, CT_P):
            cursor = _process_paragraph(blocks, heading_stack, cursor, Paragraph(child, doc))
        elif isinstance(child, CT_Tbl):
            cursor = _process_table(blocks, heading_stack, cursor, Table(child, doc))

    return ParsedDocument(blocks=blocks)
