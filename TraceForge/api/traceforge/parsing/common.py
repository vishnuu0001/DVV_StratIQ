# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Canonical parsed-block shape every file parser (docx/pdf/xlsx) emits, so
# Date: 2025-09-19
# ---------------------------------------------------------------------------
"""Canonical parsed-block shape every file parser (docx/pdf/xlsx) emits, so
indexing/chunker.py can chunk any of them the same way. Superset of every parser's
locator fields — most are None for any given source type (spec §3.1's Chunk.locator
comment: 'page, section, char_start, char_end, sheet, row_range, file_path, line_range')."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ParsedBlock:
    text: str
    section_path: str
    char_start: int
    char_end: int
    page: int | None = None
    sheet: str | None = None
    row_range: list[int] | None = None


@dataclass
class ParsedDocument:
    blocks: list[ParsedBlock] = field(default_factory=list)
