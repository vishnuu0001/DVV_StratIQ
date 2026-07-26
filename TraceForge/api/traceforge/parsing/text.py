# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Plain-text and Markdown parsing for TraceForge source ingestion.
# Date: 2025-11-23
# ---------------------------------------------------------------------------
"""Plain-text and Markdown parsing for TraceForge source ingestion."""
from __future__ import annotations

import re
from pathlib import Path

from traceforge.parsing.common import ParsedBlock, ParsedDocument

_MARKDOWN_HEADING = re.compile(r"^\s{0,3}#{1,6}\s+(.+?)\s*#*\s*$")


# Function: parse_text
def parse_text(path: str) -> ParsedDocument:
    """Preserve paragraph boundaries and Markdown headings as chunking structure."""
    text = Path(path).read_text(encoding="utf-8", errors="replace")
    blocks: list[ParsedBlock] = []
    section = "Document"
    paragraph: list[str] = []
    paragraph_start = 0
    offset = 0

    # Function: flush
    def flush(end: int) -> None:
        nonlocal paragraph
        value = "\n".join(paragraph).strip()
        if value:
            blocks.append(ParsedBlock(value, section, paragraph_start, end))
        paragraph = []

    for line in text.splitlines(keepends=True):
        content = line.rstrip("\r\n")
        heading = _MARKDOWN_HEADING.match(content)
        if heading:
            flush(offset)
            section = heading.group(1).strip()
            blocks.append(ParsedBlock(content.strip(), section, offset, offset + len(content)))
        elif content.strip():
            if not paragraph:
                paragraph_start = offset
            paragraph.append(content)
        else:
            flush(offset)
        offset += len(line)

    flush(len(text))
    return ParsedDocument(blocks=blocks)
