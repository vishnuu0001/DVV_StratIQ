# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Static call-graph extraction from source code using lightweight regex/AST.
# Date: 2025-12-21
# ---------------------------------------------------------------------------
"""
services/call_graph.py
-----------------------
Static call-graph extraction from source code using lightweight regex/AST.

Supported languages: Python (AST), Java (regex), JavaScript/TypeScript (regex)

Output schema
~~~~~~~~~~~~~
{
  "nodes": [{"id": "pkg.ClassName.method", "label": "method", "language": "python", ...}],
  "edges": [{"from": "caller_id", "to": "callee_id"}],
  "clusters": {<layer>: [node_id, ...]},
  "stats": {"total_functions": N, "total_calls": M}
}
"""
from __future__ import annotations

import ast
import logging
import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import NamedTuple

logger = logging.getLogger(__name__)

_SKIP_DIRS = {
    ".git", ".venv", "venv", "env", "node_modules", "__pycache__",
    "dist", "build", ".idea", ".vs", "vendor", "target",
}

# Layer classification heuristic based on path/class name
_LAYER_HINTS = {
    "controller": ["controller", "handler", "endpoint", "route", "rest", "api"],
    "service":    ["service", "manager", "orchestrat", "usecase", "business"],
    "repository": ["repository", "repo", "dao", "store", "database", "db", "jpa", "crud"],
    "model":      ["model", "entity", "dto", "domain", "schema", "pojo", "record"],
    "utility":    ["util", "helper", "common", "shared", "config", "constant"],
    "test":       ["test", "spec", "__test__"],
}


class CallNode(NamedTuple):
    node_id:  str
    label:    str
    language: str
    file:     str
    layer:    str
    line:     int


# Function: _classify_layer
def _classify_layer(parts: list[str]) -> str:
    joined = " ".join(parts).lower()
    for layer, hints in _LAYER_HINTS.items():
        if any(h in joined for h in hints):
            return layer
    return "other"


# ── Python extractor ─────────────────────────────────────────────────────────

class _PythonCallVisitor(ast.NodeVisitor):
    """Walks a module's AST, recording function/method nodes and their call edges."""

    # Function: __init__
    def __init__(self, module: str, rel_parts: tuple, rel_str: str,
                 nodes: "list[CallNode]", edges: "list[tuple[str, str]]"):
        self._scope: list[str] = [module]
        self._module   = module
        self._rel_parts = rel_parts
        self._rel_str   = rel_str
        self._nodes = nodes
        self._edges = edges

    # Function: _scope_id
    def _scope_id(self): return ".".join(self._scope)

    # Function: visit_ClassDef
    def visit_ClassDef(self, node: ast.ClassDef):
        self._scope.append(node.name)
        self.generic_visit(node)
        self._scope.pop()

    # Function: visit_FunctionDef
    def visit_FunctionDef(self, node: ast.FunctionDef):
        self._scope.append(node.name)
        fn_id = self._scope_id()
        layer = _classify_layer(list(self._rel_parts) + self._scope)
        self._nodes.append(CallNode(fn_id, node.name, "python", self._rel_str, layer, node.lineno))

        # Collect calls made inside the function
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                callee = None
                if isinstance(child.func, ast.Attribute):
                    callee = child.func.attr
                elif isinstance(child.func, ast.Name):
                    callee = child.func.id
                if callee:
                    # Try to resolve within same module
                    candidate = f"{self._module}.{callee}"
                    self._edges.append((fn_id, candidate))
        self.generic_visit(node)
        self._scope.pop()

    visit_AsyncFunctionDef = visit_FunctionDef


# Function: _extract_python
def _extract_python(path: Path, root: Path) -> tuple[list[CallNode], list[tuple[str, str]]]:
    nodes: list[CallNode] = []
    edges: list[tuple[str, str]] = []
    try:
        source = path.read_text(encoding="utf-8", errors="ignore")
        tree   = ast.parse(source, filename=str(path))
    except Exception:
        return nodes, edges

    rel      = path.relative_to(root)
    module   = ".".join(rel.with_suffix("").parts)
    rel_str  = str(rel).replace("\\", "/")

    _PythonCallVisitor(module, rel.parts, rel_str, nodes, edges).visit(tree)
    return nodes, edges


# ── Java extractor ────────────────────────────────────────────────────────────

_JAVA_CLASS  = re.compile(r"(?:class|interface|enum)\s+(\w+)")
_JAVA_METHOD = re.compile(r"(?:public|private|protected|static|final|void|synchronized)\s+[\w<>\[\]]+\s+(\w+)\s*\(")
_JAVA_CALL   = re.compile(r"(\w+)\s*\(")

# Function: _process_java_line
def _process_java_line(
    i: int, line: str, pkg: str, class_name: str, rel_parts: tuple, rel_str: str,
    state: dict, nodes: "list[CallNode]", edges: "list[tuple[str, str]]",
) -> None:
    state["brace_depth"] += line.count("{") - line.count("}")
    mm = _JAVA_METHOD.search(line)
    if mm and not line.strip().startswith("//"):
        state["in_method"] = mm.group(1)
        state["method_brace_start"] = state["brace_depth"]
        fn_id = f"{pkg}.{class_name}.{state['in_method']}" if class_name else f"{pkg}.{state['in_method']}"
        layer = _classify_layer(list(rel_parts) + [class_name, state["in_method"]])
        nodes.append(CallNode(fn_id, state["in_method"], "java", rel_str, layer, i))

    if not state["in_method"]:
        return

    caller_id = f"{pkg}.{class_name}.{state['in_method']}" if class_name else f"{pkg}.{state['in_method']}"
    for cm_ in _JAVA_CALL.findall(line):
        if cm_ not in {"if", "for", "while", "switch", "catch", "new", "return"}:
            edges.append((caller_id, f"{pkg}.{class_name}.{cm_}"))
    if state["brace_depth"] < state["method_brace_start"]:
        state["in_method"] = None


# Function: _extract_java
def _extract_java(path: Path, root: Path) -> tuple[list[CallNode], list[tuple[str, str]]]:
    nodes: list[CallNode] = []
    edges: list[tuple[str, str]] = []
    try:
        source = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return nodes, edges

    rel     = path.relative_to(root)
    rel_str = str(rel).replace("\\", "/")
    pkg     = ".".join(rel.with_suffix("").parts)

    class_name = ""
    cm = _JAVA_CLASS.search(source)
    if cm:
        class_name = cm.group(1)

    state = {"in_method": None, "brace_depth": 0, "method_brace_start": 0}
    for i, line in enumerate(source.splitlines(), 1):
        _process_java_line(i, line, pkg, class_name, rel.parts, rel_str, state, nodes, edges)

    return nodes, edges


# ── JavaScript / TypeScript extractor ────────────────────────────────────────

_JS_FUNC  = re.compile(r"(?:function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?\(|(?:async\s+)?(\w+)\s*\([^)]*\)\s*\{)")
_JS_CALL  = re.compile(r"(\w+)\s*\(")

# Function: _detect_js_functions
def _detect_js_functions(source: str, rel_parts: tuple, rel_str: str, module: str, nodes: "list[CallNode]") -> None:
    for i, line in enumerate(source.splitlines(), 1):
        m = _JS_FUNC.search(line)
        if not m:
            continue
        fn_name = m.group(1) or m.group(2) or m.group(3)
        if fn_name and fn_name not in {"if", "for", "while", "switch"}:
            fn_id = f"{module}.{fn_name}"
            layer = _classify_layer(list(rel_parts) + [fn_name])
            nodes.append(CallNode(fn_id, fn_name, "javascript", rel_str, layer, i))


# Function: _detect_js_calls
def _detect_js_calls(source: str, nodes: "list[CallNode]", edges: "list[tuple[str, str]]") -> None:
    # Simple call detection (file-level, not scoped for speed)
    if not nodes:
        return
    fn_ids = {n.label: n.node_id for n in nodes}
    for line in source.splitlines():
        for call in _JS_CALL.findall(line):
            if call in fn_ids and call not in {"if", "for", "while"}:
                # Attribute the call to the nearest preceding function
                # (simplified: use first node as caller context)
                edges.append((nodes[0].node_id, fn_ids[call]))


# Function: _extract_js
def _extract_js(path: Path, root: Path) -> tuple[list[CallNode], list[tuple[str, str]]]:
    nodes: list[CallNode] = []
    edges: list[tuple[str, str]] = []
    try:
        source = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return nodes, edges

    rel     = path.relative_to(root)
    rel_str = str(rel).replace("\\", "/")
    module  = ".".join(rel.with_suffix("").parts)

    _detect_js_functions(source, rel.parts, rel_str, module, nodes)
    _detect_js_calls(source, nodes, edges)

    return nodes, edges


# ── Public API ────────────────────────────────────────────────────────────────

_EXT_MAP: dict[str, str] = {
    ".py":  "python",
    ".java": "java",
    ".js":  "javascript",
    ".ts":  "javascript",
    ".jsx": "javascript",
    ".tsx": "javascript",
}


# Function: _process_one_file
def _process_one_file(fpath: Path, root: Path, lang: str) -> tuple[list[CallNode], list[tuple[str, str]]]:
    """Extract nodes and edges from a single file.  Safe to call from threads —
    each extractor is a pure function with no shared mutable state.
    ast.parse() releases the GIL so multiple threads can parse in parallel.
    """
    if lang == "python":
        return _extract_python(fpath, root)
    elif lang == "java":
        return _extract_java(fpath, root)
    else:
        return _extract_js(fpath, root)



# Function: _collect_eligible_files
def _collect_eligible_files(
    root: Path, max_files: int, languages: "list[str] | None"
) -> "list[tuple[Path, Path, str]]":
    """Walk root and collect (path, root, lang) tuples up to max_files."""
    eligible: list[tuple[Path, Path, str]] = []
    for dirpath, dirnames, filenames in os.walk(str(root)):
        if len(eligible) >= max_files:
            break
        dirnames[:] = [d for d in dirnames if d not in _SKIP_DIRS]
        dir_path = Path(dirpath)
        for fname in filenames:
            if len(eligible) >= max_files:
                break
            fpath = dir_path / fname
            lang = _EXT_MAP.get(fpath.suffix.lower())
            if not lang:
                continue
            if languages and lang not in languages:
                continue
            eligible.append((fpath, root, lang))
    return eligible


# Function: _build_call_graph_dict
def _build_call_graph_dict(
    all_nodes: "list[CallNode]",
    all_edges: "list[tuple[str, str]]",
    file_count: int,
) -> dict:
    """Deduplicate nodes/edges, build cluster map, and return the result dict."""
    seen_ids: set[str] = set()
    unique_nodes = []
    for nd in all_nodes:
        if nd.node_id not in seen_ids:
            seen_ids.add(nd.node_id)
            unique_nodes.append(nd)

    known_ids = {n.node_id for n in unique_nodes}
    valid_edges = [e for e in all_edges if e[0] in known_ids]

    clusters: dict[str, list[str]] = {}
    for nd in unique_nodes:
        clusters.setdefault(nd.layer, []).append(nd.node_id)

    return {
        "nodes": [
            {
                "id":       nd.node_id,
                "label":    nd.label,
                "language": nd.language,
                "file":     nd.file,
                "layer":    nd.layer,
                "line":     nd.line,
            }
            for nd in unique_nodes
        ],
        "edges": [
            {"from": e[0], "to": e[1]}
            for e in valid_edges
        ],
        "clusters": clusters,
        "stats": {
            "total_functions": len(unique_nodes),
            "total_calls":     len(valid_edges),
            "files_scanned":   file_count,
        },
    }


# Function: build_call_graph
def build_call_graph(
    repo_path: str,
    max_files: int = 300,
    languages: list[str] | None = None,
) -> dict:
    """
    Walk *repo_path*, extract call graph and return a JSON-serialisable dict.

    Parameters
    ----------
    repo_path : str
        Root of the repository to scan.
    max_files : int
        Cap on files processed (keeps it fast; default 300).
    languages : list[str] | None
        Restrict to these language names. None = all supported.

    Notes
    -----
    File discovery and parsing run in a ThreadPoolExecutor (up to 8 workers).
    ast.parse() is a C extension that releases the GIL, and file I/O is
    inherently I/O-bound, so parallel extraction gives a significant speedup
    on repos with many source files without adding memory pressure.
    """
    root = Path(repo_path)
    if not root.exists():
        return {"nodes": [], "edges": [], "error": f"Path not found: {repo_path}"}

    eligible = _collect_eligible_files(root, max_files, languages)

    all_nodes: list[CallNode]        = []
    all_edges: list[tuple[str, str]] = []
    workers = min(8, len(eligible) or 1)

    with ThreadPoolExecutor(max_workers=workers, thread_name_prefix="cg") as pool:
        futures = {
            pool.submit(_process_one_file, fp, rt, lg): (fp, lg)
            for fp, rt, lg in eligible
        }
        for fut in as_completed(futures):
            try:
                nodes, edges = fut.result()
                all_nodes.extend(nodes)
                all_edges.extend(edges)
            except Exception as exc:
                fpath_info = futures[fut][0]
                logger.debug("call_graph: skipped %s — %s", fpath_info, exc)

    return _build_call_graph_dict(all_nodes, all_edges, len(eligible))
