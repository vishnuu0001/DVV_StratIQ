# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: §4.3 Chunking: structure-aware, not fixed-size. Splits on heading boundaries,
# Date: 2026-04-27
# ---------------------------------------------------------------------------
"""§4.3 Chunking: structure-aware, not fixed-size. Splits on heading boundaries,
targets 400-800 tokens, 80-token overlap, never splits a table row (a table row is
always emitted as one ParsedBlock by the docx parser, so 'never split a block' gives
us that property for free)."""
from __future__ import annotations

from dataclasses import dataclass

import tiktoken

from traceforge.config import CHUNK_OVERLAP_TOKENS, CHUNK_TARGET_TOKENS
from traceforge.parsing.common import ParsedBlock, ParsedDocument

_ENCODING = tiktoken.get_encoding("cl100k_base")


# Function: count_tokens
def count_tokens(text: str) -> int:
    return len(_ENCODING.encode(text))


@dataclass
class DocChunk:
    ordinal: int
    text: str
    token_count: int
    locator: dict


# Function: chunk_document
def chunk_document(parsed: ParsedDocument) -> list[DocChunk]:
    chunks: list[DocChunk] = []
    buffer: list[ParsedBlock] = []
    buffer_tokens = 0

    # Function: flush
    def flush() -> None:
        nonlocal buffer, buffer_tokens
        if not buffer:
            return
        text = "\n".join(b.text for b in buffer)
        chunks.append(
            DocChunk(
                ordinal=len(chunks),
                text=text,
                token_count=count_tokens(text),
                locator={
                    "section": buffer[0].section_path,
                    "char_start": buffer[0].char_start,
                    "char_end": buffer[-1].char_end,
                    "page": buffer[0].page,
                    "sheet": buffer[0].sheet,
                    "row_range": buffer[0].row_range,
                    "file_path": None,
                    "line_range": None,
                },
            )
        )
        # Carry the trailing ~CHUNK_OVERLAP_TOKENS worth of blocks into the next chunk
        overlap: list[ParsedBlock] = []
        overlap_tokens = 0
        for block in reversed(buffer):
            block_tokens = count_tokens(block.text)
            if overlap_tokens + block_tokens > CHUNK_OVERLAP_TOKENS and overlap:
                break
            overlap.insert(0, block)
            overlap_tokens += block_tokens
        buffer = overlap
        buffer_tokens = overlap_tokens

    for block in parsed.blocks:
        block_tokens = count_tokens(block.text)
        section_changed = buffer and buffer[-1].section_path != block.section_path
        would_overflow = buffer_tokens + block_tokens > CHUNK_TARGET_TOKENS

        if buffer and (would_overflow or (section_changed and buffer_tokens >= CHUNK_TARGET_TOKENS // 2)):
            flush()

        buffer.append(block)
        buffer_tokens += block_tokens

    flush()
    return [c for c in chunks if c.text.strip()]
