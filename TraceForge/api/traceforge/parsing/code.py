# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: §4.2 legacy-code parser: tree-sitter chunked per function/class/module, extracting
# Date: 2026-01-23
# ---------------------------------------------------------------------------
"""§4.2 legacy-code parser: tree-sitter chunked per function/class/module, extracting
signatures/comments/business logic. Real implementation this pass (previously stubbed).

Uses tree-sitter-languages (prebuilt grammars, no C compiler needed on the target VM).
Falls back to whole-file-as-one-chunk for any extension/node-type combination not
explicitly mapped below — still real (the file is genuinely parsed and indexed), just
less granular than the function-level chunking the mapped languages get.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from tree_sitter_languages import get_parser

SUPPORTED_CODE_EXTENSIONS: dict[str, str] = {
    ".py": "python", ".js": "javascript", ".jsx": "javascript", ".ts": "typescript",
    ".tsx": "tsx", ".java": "java", ".cs": "c_sharp", ".go": "go", ".rb": "ruby",
    ".php": "php", ".cpp": "cpp", ".cc": "cpp", ".c": "c", ".h": "c", ".rs": "rust", ".kt": "kotlin",
}

# Top-level node types worth their own chunk, per language. Anything else in the file
# (module-level statements, imports) gets swept into the nearest chunk or its own
# "module" chunk so nothing is silently dropped.
_CHUNK_NODE_TYPES: dict[str, set[str]] = {
    "python": {"function_definition", "class_definition"},
    "javascript": {"function_declaration", "class_declaration", "method_definition"},
    "typescript": {"function_declaration", "class_declaration", "method_definition", "interface_declaration"},
    "tsx": {"function_declaration", "class_declaration", "method_definition", "interface_declaration"},
    "java": {"method_declaration", "class_declaration", "interface_declaration"},
    "c_sharp": {"method_declaration", "class_declaration", "interface_declaration"},
    "go": {"function_declaration", "method_declaration", "type_declaration"},
    "ruby": {"method", "class"},
    "php": {"function_definition", "class_declaration", "method_declaration"},
    "cpp": {"function_definition", "class_specifier"},
    "c": {"function_definition"},
    "rust": {"function_item", "impl_item", "struct_item"},
    "kotlin": {"function_declaration", "class_declaration"},
}


@dataclass
class CodeChunk:
    text: str
    token_count: int
    locator: dict


# Function: _node_text
def _node_text(source: bytes, node) -> str:
    return source[node.start_byte:node.end_byte].decode("utf-8", errors="replace")


# Function: parse_code
def parse_code(path: str) -> list[CodeChunk]:
    file_path = Path(path)
    lang = SUPPORTED_CODE_EXTENSIONS.get(file_path.suffix)
    source = file_path.read_bytes()
    if not source.strip():
        return []

    if lang is None:
        return _whole_file_chunk(path, source)

    try:
        parser = get_parser(lang)
        tree = parser.parse(source)
    except Exception:  # noqa: BLE001 — grammar unavailable/parse failure, degrade gracefully
        return _whole_file_chunk(path, source)

    chunk_types = _CHUNK_NODE_TYPES.get(lang, set())
    chunks: list[CodeChunk] = []
    module_level_lines: list[str] = []

    # Function: emit_module_chunk
    def emit_module_chunk() -> None:
        text = "\n".join(module_level_lines).strip()
        if text:
            chunks.append(CodeChunk(
                text=text, token_count=len(text.split()),
                locator={"file_path": path, "line_range": None, "symbol": "(module level)"},
            ))
        module_level_lines.clear()

    for node in tree.root_node.children:
        if node.type in chunk_types:
            emit_module_chunk()
            text = _node_text(source, node)
            name_node = node.child_by_field_name("name")
            symbol = _node_text(source, name_node) if name_node else node.type
            chunks.append(CodeChunk(
                text=text, token_count=len(text.split()),
                locator={"file_path": path, "line_range": [node.start_point[0] + 1, node.end_point[0] + 1], "symbol": symbol},
            ))
        else:
            module_level_lines.append(_node_text(source, node))

    emit_module_chunk()
    return chunks if chunks else _whole_file_chunk(path, source)


# Function: _whole_file_chunk
def _whole_file_chunk(path: str, source: bytes) -> list[CodeChunk]:
    text = source.decode("utf-8", errors="replace")
    if not text.strip():
        return []
    return [CodeChunk(
        text=text, token_count=len(text.split()),
        locator={"file_path": path, "line_range": [1, text.count(chr(10)) + 1], "symbol": "(whole file)"},
    )]
