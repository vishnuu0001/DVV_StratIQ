# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Codebase knowledge-graph extraction.
# Date: 2025-07-19
# ---------------------------------------------------------------------------
"""
services/knowledge_graph.py
----------------------------
Codebase knowledge-graph extraction.

Node types
~~~~~~~~~~
  module   – source file
  class    – class / interface / enum definition
  function – function or method

Edge types
~~~~~~~~~~
  contains  – module → class, module → function, class → function
  imports   – module → module / external package
  inherits  – class → class  (extends / implements)
  calls     – function → function  (intra-module best-effort)

Output schema
~~~~~~~~~~~~~
{
  "nodes": [{"id", "label", "type", "language", "file", "layer", "line"}],
  "edges": [{"from", "to",   "type"}],
  "clusters": {layer: [node_id, ...]},
  "stats":    {total_nodes, total_edges, files_scanned, node_types, languages, edge_types}
}

Performance notes
~~~~~~~~~~~~~~~~~
* os.walk with in-place dirnames pruning (dirnames[:] = [...]) prevents descent
  into node_modules/target/.venv etc. entirely — Path.rglob("*") would descend
  first, then post-hoc checks would have to visit every file.
* ThreadPoolExecutor over collected file list enables parallel extraction for
  large repos (8 workers saturate I/O without spawning too many threads).
"""
from __future__ import annotations

import ast
import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

_SKIP_DIRS: set[str] = {
    ".git", ".venv", "venv", "env", "node_modules", "__pycache__",
    "dist", "build", ".idea", ".vs", "vendor", "target",
}

_LAYER_HINTS: dict[str, list[str]] = {
    "controller": ["controller", "handler", "endpoint", "route", "rest", "view", "servlet"],
    "service":    ["service", "manager", "orchestrat", "usecase", "business", "facade"],
    "repository": ["repository", "repo", "dao", "store", "database", "db", "jpa", "crud"],
    "model":      ["model", "entity", "dto", "domain", "schema", "pojo", "record", "mapper"],
    "utility":    ["util", "helper", "common", "shared", "config", "constant", "utils", "exception", "security", "filter", "interceptor"],
    "test":       ["test", "spec", "__test__", "mock", "fixture"],
}


# Function: _classify_layer
def _classify_layer(parts: list[str]) -> str:
    joined = " ".join(parts).lower()
    for layer, hints in _LAYER_HINTS.items():
        if any(h in joined for h in hints):
            return layer
    return "other"


# ── Python extractor ──────────────────────────────────────────────────────────

class _PythonKGVisitor(ast.NodeVisitor):
    """AST visitor that emits knowledge-graph nodes/edges for a Python module."""

    # Function: __init__
    def __init__(self, module: str, mod_id: str, rel: Path, rel_str: str, nodes: list[dict], edges: list[tuple]):
        self._scope: list[str] = [module]
        self._class_stack: list[str] = []
        self.module = module
        self.mod_id = mod_id
        self.rel = rel
        self.rel_str = rel_str
        self.nodes = nodes
        self.edges = edges

    # Function: _sid
    def _sid(self) -> str:
        return ".".join(self._scope)

    # ── import tracking ──────────────────────────────────────────────────
    # Function: visit_Import
    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            tgt = alias.name.split(".")[0]
            self.edges.append((self.mod_id, tgt, "imports"))

    # Function: visit_ImportFrom
    def visit_ImportFrom(self, node: ast.ImportFrom):
        if node.module:
            tgt = node.module.split(".")[0]
            self.edges.append((self.mod_id, tgt, "imports"))

    # ── class ────────────────────────────────────────────────────────────
    # Function: visit_ClassDef
    def visit_ClassDef(self, node: ast.ClassDef):
        self._scope.append(node.name)
        cls_id    = self._sid()
        cls_layer = _classify_layer(list(self.rel.parts) + [node.name])
        self.nodes.append({"id": cls_id, "label": node.name, "type": "class",
                      "language": "python", "file": self.rel_str,
                      "layer": cls_layer, "line": node.lineno})
        self.edges.append((self.mod_id, cls_id, "contains"))

        for base in node.bases:
            if isinstance(base, ast.Name):
                self.edges.append((cls_id, f"{self.module}.{base.id}", "inherits"))
            elif isinstance(base, ast.Attribute):
                self.edges.append((cls_id, base.attr, "inherits"))

        self._class_stack.append(cls_id)
        self.generic_visit(node)
        self._class_stack.pop()
        self._scope.pop()

    # ── function / method ─────────────────────────────────────────────────
    # Function: visit_FunctionDef
    def visit_FunctionDef(self, node: ast.FunctionDef):
        self._scope.append(node.name)
        fn_id    = self._sid()
        fn_layer = _classify_layer(list(self.rel.parts) + self._scope)
        self.nodes.append({"id": fn_id, "label": node.name, "type": "function",
                      "language": "python", "file": self.rel_str,
                      "layer": fn_layer, "line": node.lineno})
        parent = self._class_stack[-1] if self._class_stack else self.mod_id
        self.edges.append((parent, fn_id, "contains"))

        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                callee = None
                if isinstance(child.func, ast.Attribute):
                    callee = child.func.attr
                elif isinstance(child.func, ast.Name):
                    callee = child.func.id
                if callee:
                    self.edges.append((fn_id, f"{self.module}.{callee}", "calls"))

        self.generic_visit(node)
        self._scope.pop()

    visit_AsyncFunctionDef = visit_FunctionDef


# Function: _extract_python
def _extract_python(path: Path, root: Path) -> tuple[list[dict], list[tuple]]:
    nodes: list[dict] = []
    edges: list[tuple] = []  # (from, to, type)

    try:
        source = path.read_text(encoding="utf-8", errors="ignore")
        tree   = ast.parse(source, str(path))
    except Exception:
        return nodes, edges

    rel      = path.relative_to(root)
    module   = ".".join(rel.with_suffix("").parts)
    rel_str  = str(rel).replace("\\", "/")
    layer    = _classify_layer(list(rel.parts))
    mod_id   = module

    nodes.append({"id": mod_id, "label": rel.name, "type": "module",
                  "language": "python", "file": rel_str, "layer": layer, "line": 1})

    _PythonKGVisitor(module, mod_id, rel, rel_str, nodes, edges).visit(tree)
    return nodes, edges


# ── Java extractor ────────────────────────────────────────────────────────────

_JAVA_IMPORT  = re.compile(r"import\s+([\w.]+)\s*;")
_JAVA_CLASS   = re.compile(
    r"(?:class|interface|enum)\s+(\w+)"
    r"(?:\s+extends\s+(\w+))?"
    r"(?:\s+implements\s+([\w,\s]+))?"
)
_JAVA_METHOD  = re.compile(
    r"(?:public|private|protected|static|final|void|synchronized)"
    r"\s+[\w<>\[\]]+\s+(\w+)\s*\("
)
_JAVA_CALL    = re.compile(r"(\w+)\s*\(")
_JAVA_SKIP_KW = {"if", "for", "while", "switch", "catch", "new", "return", "throw", "assert"}


# Function: _match_java_class
def _match_java_class(line: str, i: int, pkg: str, rel_str: str, layer: str, mod_id: str, nodes: list, edges: list) -> "tuple[str, str] | None":
    cm = _JAVA_CLASS.search(line)
    if not cm:
        return None
    class_name = cm.group(1)
    cls_id = f"{pkg}.{class_name}"
    nodes.append({"id": cls_id, "label": class_name, "type": "class",
                  "language": "java", "file": rel_str, "layer": layer, "line": i})
    edges.append((mod_id, cls_id, "contains"))
    if cm.group(2):
        edges.append((cls_id, f"{pkg}.{cm.group(2)}", "inherits"))
    if cm.group(3):
        for iface in cm.group(3).split(","):
            iface = iface.strip()
            if iface:
                edges.append((cls_id, iface, "inherits"))
    return class_name, cls_id


# Function: _match_java_method
def _match_java_method(
    line: str, i: int, pkg: str, class_name: str, cls_id: "str | None", mod_id: str,
    rel: Path, rel_str: str, nodes: list, edges: list,
) -> "str | None":
    mm = _JAVA_METHOD.search(line)
    if not (mm and class_name):
        return None
    fn_name = mm.group(1)
    fn_id   = f"{pkg}.{class_name}.{fn_name}"
    fn_layer = _classify_layer(list(rel.parts) + [class_name, fn_name])
    nodes.append({"id": fn_id, "label": fn_name, "type": "function",
                  "language": "java", "file": rel_str,
                  "layer": fn_layer, "line": i})
    parent = cls_id if cls_id else mod_id
    edges.append((parent, fn_id, "contains"))
    return fn_name


# Function: _track_java_method_calls
def _track_java_method_calls(line: str, pkg: str, class_name: str, in_method: str, edges: list) -> None:
    caller_id = f"{pkg}.{class_name}.{in_method}"
    for call in _JAVA_CALL.findall(line):
        if call not in _JAVA_SKIP_KW:
            edges.append((caller_id, f"{pkg}.{class_name}.{call}", "calls"))


# Function: _extract_java
def _extract_java(path: Path, root: Path) -> tuple[list[dict], list[tuple]]:
    nodes: list[dict] = []
    edges: list[tuple] = []

    try:
        source = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return nodes, edges

    rel     = path.relative_to(root)
    rel_str = str(rel).replace("\\", "/")
    pkg     = ".".join(rel.with_suffix("").parts)
    layer   = _classify_layer(list(rel.parts))
    mod_id  = pkg

    nodes.append({"id": mod_id, "label": rel.name, "type": "module",
                  "language": "java", "file": rel_str, "layer": layer, "line": 1})

    for m in _JAVA_IMPORT.finditer(source):
        tgt = m.group(1).split(".")[0]
        edges.append((mod_id, tgt, "imports"))

    class_name = ""
    cls_id: str | None = None
    brace_depth = 0
    in_method: str | None = None
    method_brace_start = 0

    for i, line in enumerate(source.splitlines(), 1):
        stripped = line.strip()
        brace_depth += stripped.count("{") - stripped.count("}")

        if stripped.startswith("//"):
            continue

        cls_match = _match_java_class(line, i, pkg, rel_str, layer, mod_id, nodes, edges)
        if cls_match:
            class_name, cls_id = cls_match

        fn_name_match = _match_java_method(line, i, pkg, class_name, cls_id, mod_id, rel, rel_str, nodes, edges)
        if fn_name_match:
            in_method = fn_name_match
            method_brace_start = brace_depth

        if in_method:
            _track_java_method_calls(line, pkg, class_name, in_method, edges)
            if brace_depth < method_brace_start:
                in_method = None

    return nodes, edges


# ── JavaScript / TypeScript extractor ─────────────────────────────────────────

_JS_IMPORT = re.compile(
    r"(?:import|require)\s*[({'\"]?\s*[\w,{}\s*]*\s*from\s*['\"]([\w./\-@]+)['\"]"
    r"|require\s*\(\s*['\"]([\w./\-@]+)['\"]\s*\)"
)
_JS_CLASS  = re.compile(
    r"(?:export\s+)?(?:default\s+)?class\s+(\w+)(?:\s+extends\s+(\w+))?"
)
_JS_FUNC   = re.compile(
    r"(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\("
    r"|(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>"
    r"|(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?function"
)
_JS_METHOD = re.compile(
    r"^\s*(?:async\s+)?(\w+)\s*\([^)]*\)\s*\{"
)
_JS_CALL   = re.compile(r"(\w+)\s*\(")
_JS_SKIP   = {"if", "for", "while", "switch", "catch", "return", "new",
              "import", "export", "class", "function", "const", "let", "var"}


# Function: _match_js_class
def _match_js_class(line: str, i: int, module: str, rel_str: str, layer: str, mod_id: str, nodes: list, edges: list) -> "str | None":
    cm = _JS_CLASS.search(line)
    if not cm:
        return None
    class_name = cm.group(1)
    cls_id = f"{module}.{class_name}"
    nodes.append({"id": cls_id, "label": class_name, "type": "class",
                  "language": "javascript", "file": rel_str, "layer": layer, "line": i})
    edges.append((mod_id, cls_id, "contains"))
    if cm.group(2):
        edges.append((cls_id, f"{module}.{cm.group(2)}", "inherits"))
    return cls_id


# Function: _match_js_function
def _match_js_function(
    line: str, i: int, module: str, rel: Path, rel_str: str,
    current_class: "str | None", mod_id: str, nodes: list, edges: list,
) -> None:
    fm = _JS_FUNC.search(line)
    if not fm:
        return
    fn_name = fm.group(1) or fm.group(2) or fm.group(3)
    if not fn_name or fn_name in _JS_SKIP:
        return
    fn_id = f"{module}.{fn_name}"
    fn_layer = _classify_layer(list(rel.parts) + [fn_name])
    nodes.append({"id": fn_id, "label": fn_name, "type": "function",
                  "language": "javascript", "file": rel_str,
                  "layer": fn_layer, "line": i})
    parent = current_class if current_class else mod_id
    edges.append((parent, fn_id, "contains"))


# Function: _extract_js
def _extract_js(path: Path, root: Path) -> tuple[list[dict], list[tuple]]:
    nodes: list[dict] = []
    edges: list[tuple] = []

    try:
        source = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return nodes, edges

    rel     = path.relative_to(root)
    rel_str = str(rel).replace("\\", "/")
    module  = ".".join(rel.with_suffix("").parts)
    layer   = _classify_layer(list(rel.parts))
    mod_id  = module

    nodes.append({"id": mod_id, "label": rel.name, "type": "module",
                  "language": "javascript", "file": rel_str, "layer": layer, "line": 1})

    # Imports
    for m in _JS_IMPORT.finditer(source):
        imp = m.group(1) or m.group(2) or ""
        if not imp:
            continue
        tgt = imp.lstrip("./").split("/")[0].lstrip("@") if not imp.startswith(".") else imp
        edges.append((mod_id, tgt, "imports"))

    lines = source.splitlines()
    current_class: str | None = None

    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("//") or stripped.startswith("*"):
            continue

        # Classes
        cls_id = _match_js_class(line, i, module, rel_str, layer, mod_id, nodes, edges)
        if cls_id:
            current_class = cls_id
            continue

        # Top-level functions
        _match_js_function(line, i, module, rel, rel_str, current_class, mod_id, nodes, edges)

    return nodes, edges


# ── COBOL / Mainframe extractor ──────────────────────────────────────────────

_COBOL_PARA    = re.compile(r"^([A-Z0-9][A-Z0-9\-]*)\.\s*$", re.MULTILINE)
_COBOL_COPY    = re.compile(r"COPY\s+([\w-]+)", re.IGNORECASE)
_COBOL_CALL    = re.compile(r"CALL\s+['\"]([\w-]+)['\"]", re.IGNORECASE)
_COBOL_SECTION = re.compile(
    r"^\s{0,30}([A-Z0-9][A-Z0-9\-]*)\s+SECTION\.\s*$", re.MULTILINE | re.IGNORECASE
)
_COBOL_PROGRAM = re.compile(
    r"PROGRAM-ID\.?\s+([\w-]+)", re.IGNORECASE
)
_JCL_STEP      = re.compile(r"^//([\w@#$]+)\s+EXEC", re.MULTILINE)
_JCL_CALL      = re.compile(r"PGM=([\w@#$]+)", re.IGNORECASE)


_COBOL_SKIP_SECTIONS = {"DATA", "FILE", "WORKING-STORAGE", "LINKAGE",
                "PROCEDURE", "ENVIRONMENT", "CONFIGURATION",
                "INPUT-OUTPUT", "LOCAL-STORAGE"}

_COBOL_SKIP_PARAS = {"ELSE", "END", "STOP", "EXIT", "GOBACK",
                 "PROCEDURE", "DIVISION", "SECTION"}


# Function: _extract_cobol_sections
def _extract_cobol_sections(source: str, mod_id: str, rel: Path, rel_str: str, layer: str, nodes: list, edges: list) -> dict:
    # Sections → class-like grouping nodes
    sections_seen: dict[str, str] = {}   # name → id
    for m in _COBOL_SECTION.finditer(source):
        sec_name = m.group(1).upper()
        if sec_name in _COBOL_SKIP_SECTIONS:
            continue  # skip division-level keywords
        sec_id = f"{mod_id}.{sec_name}"
        sec_layer = _classify_layer(list(rel.parts) + [sec_name])
        # Find approximate line number
        line_no = source[:m.start()].count("\n") + 1
        nodes.append({"id": sec_id, "label": sec_name, "type": "class",
                      "language": "cobol", "file": rel_str,
                      "layer": sec_layer, "line": line_no})
        edges.append((mod_id, sec_id, "contains"))
        sections_seen[sec_name] = sec_id
    return sections_seen


# Function: _extract_cobol_paragraphs
def _extract_cobol_paragraphs(
    proc_src: str, proc_offset: int, source: str, mod_id: str, rel: Path,
    rel_str: str, sections_seen: dict, nodes: list, edges: list,
) -> None:
    paras_seen: set[str] = set()
    in_section: str | None = None
    for m in _COBOL_PARA.finditer(proc_src):
        para_name = m.group(1).upper()
        # Skip JCL-like keywords and common COBOL reserved words
        if para_name in _COBOL_SKIP_PARAS:
            continue
        if para_name in paras_seen:
            continue
        paras_seen.add(para_name)
        fn_id  = f"{mod_id}.{para_name}"
        fn_layer = _classify_layer(list(rel.parts) + [para_name])
        line_no  = source[:proc_offset + m.start()].count("\n") + 1
        nodes.append({"id": fn_id, "label": para_name, "type": "function",
                      "language": "cobol", "file": rel_str,
                      "layer": fn_layer, "line": line_no})
        parent = sections_seen.get(in_section, mod_id) if in_section else mod_id
        edges.append((parent, fn_id, "contains"))


# Function: _extract_cobol
def _extract_cobol(path: Path, root: Path) -> tuple[list[dict], list[tuple]]:
    """Extract module / paragraph / copy-book nodes for COBOL (.cbl/.cob/.cpy) files."""
    nodes: list[dict] = []
    edges: list[tuple] = []

    try:
        source = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return nodes, edges

    rel     = path.relative_to(root)
    rel_str = str(rel).replace("\\", "/")
    layer   = _classify_layer(list(rel.parts))

    # Derive module id from path (e.g. src.MYPROGRAM)
    mod_id = ".".join(rel.with_suffix("").parts)

    # Try to get the PROGRAM-ID name as the label
    pm = _COBOL_PROGRAM.search(source)
    label = pm.group(1) if pm else path.stem

    nodes.append({"id": mod_id, "label": label, "type": "module",
                  "language": "cobol", "file": rel_str, "layer": layer, "line": 1})

    # COPY statements → import edges
    for m in _COBOL_COPY.finditer(source):
        edges.append((mod_id, m.group(1).upper(), "imports"))

    sections_seen = _extract_cobol_sections(source, mod_id, rel, rel_str, layer, nodes, edges)

    # Paragraphs → function nodes (PROCEDURE DIVISION only: lines after first PROCEDURE DIVISION)
    proc_div_idx = source.upper().find("PROCEDURE DIVISION")
    proc_src = source[proc_div_idx:] if proc_div_idx >= 0 else source
    proc_offset = proc_div_idx if proc_div_idx >= 0 else 0

    _extract_cobol_paragraphs(proc_src, proc_offset, source, mod_id, rel, rel_str, sections_seen, nodes, edges)

    # CALL statements inside paragraphs (approximation: search nearby lines)
    for m in _COBOL_CALL.finditer(proc_src):
        callee = m.group(1).upper()
        # Attribute to module if we can't resolve to a specific paragraph
        edges.append((mod_id, callee, "calls"))

    return nodes, edges


# Function: _extract_jcl
def _extract_jcl(path: Path, root: Path) -> tuple[list[dict], list[tuple]]:
    """Extract module and step nodes for JCL (.jcl) files."""
    nodes: list[dict] = []
    edges: list[tuple] = []

    try:
        source = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return nodes, edges

    rel     = path.relative_to(root)
    rel_str = str(rel).replace("\\", "/")
    layer   = _classify_layer(list(rel.parts))
    mod_id  = ".".join(rel.with_suffix("").parts)

    nodes.append({"id": mod_id, "label": path.stem, "type": "module",
                  "language": "jcl", "file": rel_str, "layer": layer, "line": 1})

    for m in _JCL_STEP.finditer(source):
        step_name = m.group(1).upper()
        step_id   = f"{mod_id}.{step_name}"
        line_no   = source[:m.start()].count("\n") + 1
        nodes.append({"id": step_id, "label": step_name, "type": "function",
                      "language": "jcl", "file": rel_str, "layer": layer, "line": line_no})
        edges.append((mod_id, step_id, "contains"))

    for m in _JCL_CALL.finditer(source):
        pgm = m.group(1).upper()
        edges.append((mod_id, pgm, "calls"))

    return nodes, edges


# ── Generic regex-based extractor (shared by many language families) ──────────

# Function: _generic_extract
def _generic_extract(
    path: Path,
    root: Path,
    language: str,
    *,
    import_pat: "re.Pattern | None" = None,
    import_group: int = 1,
    class_pat: "re.Pattern | None" = None,
    class_name_group: int = 1,
    inherits_group: "int | None" = None,
    func_pat: "re.Pattern | None" = None,
    func_name_group: int = 1,
    skip_func_kw: "set[str] | None" = None,
) -> "tuple[list[dict], list[tuple]]":
    """Shared regex extractor: module + optional classes + optional functions."""
    nodes: list[dict] = []
    edges: list[tuple] = []
    try:
        source = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return nodes, edges

    rel     = path.relative_to(root)
    rel_str = str(rel).replace("\\", "/")
    layer   = _classify_layer(list(rel.parts))
    mod_id  = ".".join(rel.with_suffix("").parts)

    nodes.append({"id": mod_id, "label": rel.name, "type": "module",
                  "language": language, "file": rel_str, "layer": layer, "line": 1})

    _generic_extract_imports(source, mod_id, import_pat, import_group, edges)

    skip_kw = skip_func_kw or set()
    last_cls_id = _generic_extract_classes(
        source, rel, rel_str, mod_id, language, class_pat, class_name_group, inherits_group, skip_kw, nodes, edges
    )
    _generic_extract_functions(
        source, rel, rel_str, mod_id, language, func_pat, func_name_group, skip_kw, last_cls_id, nodes, edges
    )

    return nodes, edges


# Function: _generic_extract_imports
def _generic_extract_imports(source: str, mod_id: str, import_pat: "re.Pattern | None", import_group: int, edges: list) -> None:
    if not import_pat:
        return
    for m in import_pat.finditer(source):
        try:
            tgt = m.group(import_group) or ""
        except IndexError:
            continue
        tgt = tgt.replace("\\", ".").replace("/", ".").split(".")[0].split("::")[0]
        if tgt:
            edges.append((mod_id, tgt, "imports"))


# Function: _link_class_inherits
def _link_class_inherits(m: "re.Match", cls_id: str, inherits_group: "int | None", edges: list) -> None:
    if inherits_group is None:
        return
    try:
        parent_cls = m.group(inherits_group) or ""
        if parent_cls.strip():
            edges.append((cls_id, parent_cls.strip(), "inherits"))
    except IndexError:
        pass


# Function: _generic_extract_classes
def _generic_extract_classes(
    source: str, rel: Path, rel_str: str, mod_id: str, language: str,
    class_pat: "re.Pattern | None", class_name_group: int, inherits_group: "int | None",
    skip_kw: set, nodes: list, edges: list,
) -> "str | None":
    last_cls_id: "str | None" = None
    if not class_pat:
        return last_cls_id
    for m in class_pat.finditer(source):
        try:
            cls_name = m.group(class_name_group) or ""
        except IndexError:
            continue
        if not cls_name or cls_name in skip_kw:
            continue
        cls_id    = f"{mod_id}.{cls_name}"
        line_no   = source[:m.start()].count("\n") + 1
        cls_layer = _classify_layer(list(rel.parts) + [cls_name])
        nodes.append({"id": cls_id, "label": cls_name, "type": "class",
                      "language": language, "file": rel_str,
                      "layer": cls_layer, "line": line_no})
        edges.append((mod_id, cls_id, "contains"))
        _link_class_inherits(m, cls_id, inherits_group, edges)
        last_cls_id = cls_id
    return last_cls_id


# Function: _generic_extract_functions
def _generic_extract_functions(
    source: str, rel: Path, rel_str: str, mod_id: str, language: str,
    func_pat: "re.Pattern | None", func_name_group: int, skip_kw: set,
    last_cls_id: "str | None", nodes: list, edges: list,
) -> None:
    if not func_pat:
        return
    for m in func_pat.finditer(source):
        try:
            fn_name = m.group(func_name_group) or ""
        except IndexError:
            continue
        if not fn_name or fn_name in skip_kw:
            continue
        fn_id    = f"{mod_id}.{fn_name}"
        line_no  = source[:m.start()].count("\n") + 1
        fn_layer = _classify_layer(list(rel.parts) + [fn_name])
        nodes.append({"id": fn_id, "label": fn_name, "type": "function",
                      "language": language, "file": rel_str,
                      "layer": fn_layer, "line": line_no})
        edges.append((last_cls_id or mod_id, fn_id, "contains"))


# ── .NET extractor (C# / VB.NET / F#) ────────────────────────────────────────

_CS_IMPORT = re.compile(r"^using\s+([\w.]+)\s*;", re.MULTILINE)
_CS_CLASS  = re.compile(
    r"\b(?:class|interface|enum|struct|record)\s+(\w+)(?:\s*:\s*([\w.]+))?",
    re.MULTILINE,
)
_CS_METHOD = re.compile(
    r"\b(?:public|private|protected|internal|static|override|virtual|async|abstract)"
    r"(?:\s+(?:public|private|protected|internal|static|override|virtual|async|abstract))*"
    r"\s+[\w<>\[\]?,\s]+\s+(\w+)\s*\(",
    re.MULTILINE,
)
_CS_SKIP   = {"if", "while", "for", "foreach", "switch", "catch", "using", "return",
              "new", "typeof", "nameof", "throw", "await"}

_VB_IMPORT = re.compile(r"^Imports\s+([\w.]+)", re.MULTILINE | re.IGNORECASE)
_VB_CLASS  = re.compile(
    r"\b(?:Class|Interface|Enum|Structure|Module)\s+(\w+)", re.MULTILINE | re.IGNORECASE
)
_VB_FUNC   = re.compile(r"\b(?:Sub|Function)\s+(\w+)\s*\(", re.MULTILINE | re.IGNORECASE)

_FS_IMPORT = re.compile(r"^open\s+([\w.]+)", re.MULTILINE)
_FS_TYPE   = re.compile(r"^type\s+(\w+)", re.MULTILINE)
_FS_LET    = re.compile(r"^let\s+(?:rec\s+)?(\w+)\s*[\(=]", re.MULTILINE)


# Function: _extract_dotnet
def _extract_dotnet(path: Path, root: Path) -> "tuple[list[dict], list[tuple]]":
    ext = path.suffix.lower()
    if ext == ".vb":
        return _generic_extract(path, root, "dotnet",
                                import_pat=_VB_IMPORT,
                                class_pat=_VB_CLASS,
                                func_pat=_VB_FUNC)
    if ext == ".fs":
        return _generic_extract(path, root, "dotnet",
                                import_pat=_FS_IMPORT,
                                class_pat=_FS_TYPE,
                                func_pat=_FS_LET)
    # .cs default
    return _generic_extract(path, root, "dotnet",
                            import_pat=_CS_IMPORT,
                            class_pat=_CS_CLASS, inherits_group=2,
                            func_pat=_CS_METHOD, skip_func_kw=_CS_SKIP)


# ── Go extractor ──────────────────────────────────────────────────────────────

_GO_IMPORT_BLOCK = re.compile(r'import\s*\(\s*(.*?)\s*\)', re.DOTALL)
_GO_IMPORT_ITEM  = re.compile(r'"([\w./\-]+)"')
_GO_IMPORT_SINGLE = re.compile(r'^import\s+"([\w./\-]+)"', re.MULTILINE)
_GO_TYPE         = re.compile(r'^type\s+(\w+)\s+(?:struct|interface)', re.MULTILINE)
_GO_FUNC         = re.compile(r'^func\s+(?:\([^)]*\)\s+)?(\w+)\s*[(\[]', re.MULTILINE)
_GO_SKIP         = {"init", "main"}


# Function: _extract_go
def _extract_go(path: Path, root: Path) -> "tuple[list[dict], list[tuple]]":
    nodes: list[dict] = []
    edges: list[tuple] = []
    try:
        source = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return nodes, edges

    rel     = path.relative_to(root)
    rel_str = str(rel).replace("\\", "/")
    layer   = _classify_layer(list(rel.parts))
    mod_id  = ".".join(rel.with_suffix("").parts)

    nodes.append({"id": mod_id, "label": rel.name, "type": "module",
                  "language": "go", "file": rel_str, "layer": layer, "line": 1})

    # Import blocks
    for block in _GO_IMPORT_BLOCK.finditer(source):
        for imp in _GO_IMPORT_ITEM.finditer(block.group(1)):
            pkg = imp.group(1).split("/")[-1]
            edges.append((mod_id, pkg, "imports"))
    for m in _GO_IMPORT_SINGLE.finditer(source):
        pkg = m.group(1).split("/")[-1]
        edges.append((mod_id, pkg, "imports"))

    # Types
    last_type_id: "str | None" = None
    for m in _GO_TYPE.finditer(source):
        type_name = m.group(1)
        type_id   = f"{mod_id}.{type_name}"
        line_no   = source[:m.start()].count("\n") + 1
        nodes.append({"id": type_id, "label": type_name, "type": "class",
                      "language": "go", "file": rel_str,
                      "layer": _classify_layer(list(rel.parts) + [type_name]),
                      "line": line_no})
        edges.append((mod_id, type_id, "contains"))
        last_type_id = type_id

    # Functions / methods
    for m in _GO_FUNC.finditer(source):
        fn_name = m.group(1)
        if fn_name in _GO_SKIP:
            continue
        fn_id   = f"{mod_id}.{fn_name}"
        line_no = source[:m.start()].count("\n") + 1
        nodes.append({"id": fn_id, "label": fn_name, "type": "function",
                      "language": "go", "file": rel_str,
                      "layer": _classify_layer(list(rel.parts) + [fn_name]),
                      "line": line_no})
        edges.append((mod_id, fn_id, "contains"))

    return nodes, edges


# ── Rust extractor ────────────────────────────────────────────────────────────

_RS_USE    = re.compile(r"^use\s+([\w:]+)", re.MULTILINE)
_RS_STRUCT = re.compile(r"\b(?:struct|enum|union|trait)\s+(\w+)", re.MULTILINE)
_RS_FN     = re.compile(r"\bfn\s+(\w+)\s*(?:<[^>]*>)?\s*\(", re.MULTILINE)
_RS_SKIP   = {"main", "new", "default", "fmt", "from", "into", "drop"}


# Function: _extract_rust
def _extract_rust(path: Path, root: Path) -> "tuple[list[dict], list[tuple]]":
    return _generic_extract(path, root, "rust",
                            import_pat=_RS_USE, import_group=1,
                            class_pat=_RS_STRUCT,
                            func_pat=_RS_FN, skip_func_kw=_RS_SKIP)


# ── Kotlin extractor ──────────────────────────────────────────────────────────

_KT_IMPORT = re.compile(r"^import\s+([\w.]+)", re.MULTILINE)
_KT_CLASS  = re.compile(
    r"\b(?:data\s+class|sealed\s+class|abstract\s+class|open\s+class|"
    r"enum\s+class|class|interface|object)\s+(\w+)",
    re.MULTILINE,
)
_KT_FUN    = re.compile(r"\bfun\s+(\w+)\s*\(", re.MULTILINE)
_KT_SKIP   = {"main", "apply", "also", "let", "run", "with"}


# Function: _extract_kotlin
def _extract_kotlin(path: Path, root: Path) -> "tuple[list[dict], list[tuple]]":
    return _generic_extract(path, root, "kotlin",
                            import_pat=_KT_IMPORT,
                            class_pat=_KT_CLASS,
                            func_pat=_KT_FUN, skip_func_kw=_KT_SKIP)


# ── Scala extractor ───────────────────────────────────────────────────────────

_SC_IMPORT = re.compile(r"^import\s+([\w.]+)", re.MULTILINE)
_SC_CLASS  = re.compile(
    r"\b(?:case\s+class|abstract\s+class|sealed\s+class|class|object|trait|case\s+object)\s+(\w+)",
    re.MULTILINE,
)
_SC_DEF    = re.compile(r"\bdef\s+(\w+)\s*[(\[]", re.MULTILINE)
_SC_SKIP   = {"apply", "unapply", "main", "toString", "hashCode", "equals"}


# Function: _extract_scala
def _extract_scala(path: Path, root: Path) -> "tuple[list[dict], list[tuple]]":
    return _generic_extract(path, root, "scala",
                            import_pat=_SC_IMPORT,
                            class_pat=_SC_CLASS,
                            func_pat=_SC_DEF, skip_func_kw=_SC_SKIP)


# ── Ruby extractor ────────────────────────────────────────────────────────────

_RB_REQUIRE = re.compile(r"require(?:_relative)?\s+['\"]([^'\"]+)['\"]", re.MULTILINE)
_RB_CLASS   = re.compile(r"^(?:class|module)\s+(\w+)", re.MULTILINE)
_RB_DEF     = re.compile(r"^\s*def\s+(?:self\.)?(\w+)", re.MULTILINE)
_RB_SKIP    = {"initialize", "new"}


# Function: _extract_ruby
def _extract_ruby(path: Path, root: Path) -> "tuple[list[dict], list[tuple]]":
    return _generic_extract(path, root, "ruby",
                            import_pat=_RB_REQUIRE,
                            class_pat=_RB_CLASS,
                            func_pat=_RB_DEF, skip_func_kw=_RB_SKIP)


# ── PHP extractor ─────────────────────────────────────────────────────────────

_PHP_USE   = re.compile(r"^use\s+([\w\\]+)", re.MULTILINE)
_PHP_CLASS = re.compile(
    r"\b(?:class|interface|trait|abstract\s+class|enum)\s+(\w+)"
    r"(?:\s+extends\s+(\w+))?",
    re.MULTILINE,
)
_PHP_FUNC  = re.compile(r"function\s+(\w+)\s*\(", re.MULTILINE)
_PHP_SKIP  = {"__construct", "__destruct", "__toString", "__get", "__set",
              "if", "while", "for", "foreach", "switch"}


# Function: _extract_php
def _extract_php(path: Path, root: Path) -> "tuple[list[dict], list[tuple]]":
    return _generic_extract(path, root, "php",
                            import_pat=_PHP_USE,
                            class_pat=_PHP_CLASS, inherits_group=2,
                            func_pat=_PHP_FUNC, skip_func_kw=_PHP_SKIP)


# ── C / C++ extractor ─────────────────────────────────────────────────────────

_CPP_INCLUDE = re.compile(r'^#include\s*[<"]([\w./\-]+)[>"]', re.MULTILINE)
_CPP_CLASS   = re.compile(r'\b(?:class|struct|union)\s+(\w+)\s*[:{]', re.MULTILINE)
_CPP_FUNC    = re.compile(
    r'^(?:[\w:*&<>\[\]\s]+?\s+)?(\w+)\s*\([^)]*\)\s*(?:const\s*)?(?:noexcept\s*)?'
    r'(?:override\s*)?(?:final\s*)?\s*\{',
    re.MULTILINE,
)
_CPP_SKIP    = {"if", "while", "for", "switch", "catch", "do", "else",
                "main", "return", "new", "delete", "sizeof"}


# Function: _extract_cpp
def _extract_cpp(path: Path, root: Path) -> "tuple[list[dict], list[tuple]]":
    return _generic_extract(path, root, "cpp",
                            import_pat=_CPP_INCLUDE,
                            class_pat=_CPP_CLASS,
                            func_pat=_CPP_FUNC, skip_func_kw=_CPP_SKIP)


# ── Shell extractor ───────────────────────────────────────────────────────────

_SH_SOURCE = re.compile(r'^(?:source|\.\s+)([\w./\-]+)', re.MULTILINE)
_SH_FUNC   = re.compile(r'^(?:function\s+(\w+)\s*\{|(\w+)\s*\(\s*\)\s*\{)', re.MULTILINE)


# Function: _extract_shell
def _extract_shell(path: Path, root: Path) -> "tuple[list[dict], list[tuple]]":
    nodes: list[dict] = []
    edges: list[tuple] = []
    try:
        source = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return nodes, edges

    rel     = path.relative_to(root)
    rel_str = str(rel).replace("\\", "/")
    layer   = _classify_layer(list(rel.parts))
    mod_id  = ".".join(rel.with_suffix("").parts)

    nodes.append({"id": mod_id, "label": rel.name, "type": "module",
                  "language": "shell", "file": rel_str, "layer": layer, "line": 1})

    for m in _SH_SOURCE.finditer(source):
        src = Path(m.group(1)).stem
        edges.append((mod_id, src, "imports"))

    for m in _SH_FUNC.finditer(source):
        fn_name = m.group(1) or m.group(2) or ""
        if not fn_name:
            continue
        fn_id   = f"{mod_id}.{fn_name}"
        line_no = source[:m.start()].count("\n") + 1
        nodes.append({"id": fn_id, "label": fn_name, "type": "function",
                      "language": "shell", "file": rel_str,
                      "layer": _classify_layer(list(rel.parts) + [fn_name]),
                      "line": line_no})
        edges.append((mod_id, fn_id, "contains"))

    return nodes, edges


# ── R extractor ───────────────────────────────────────────────────────────────

_R_LIBRARY = re.compile(r'(?:library|require)\s*\(\s*["\']?(\w+)["\']?\s*\)', re.MULTILINE)
_R_CLASS   = re.compile(r'setClass\s*\(\s*["\'](\w+)["\']', re.MULTILINE)
_R_FUNC    = re.compile(r'^(\w+)\s*<-\s*function\s*\(', re.MULTILINE)


# Function: _extract_r
def _extract_r(path: Path, root: Path) -> "tuple[list[dict], list[tuple]]":
    return _generic_extract(path, root, "r",
                            import_pat=_R_LIBRARY,
                            class_pat=_R_CLASS,
                            func_pat=_R_FUNC)


# ── Dart extractor ────────────────────────────────────────────────────────────

_DART_IMPORT = re.compile(r"import\s+['\"]([^'\"]+)['\"]", re.MULTILINE)
_DART_CLASS  = re.compile(
    r"\b(?:abstract\s+class|class|mixin|enum|extension)\s+(\w+)", re.MULTILINE
)
_DART_FUNC   = re.compile(
    r"(?:void|Future|Stream|[\w<>\[\]]+)\s+(\w+)\s*\([^)]*\)\s*(?:async\s*)?\{",
    re.MULTILINE,
)
_DART_SKIP   = {"if", "while", "for", "switch", "catch", "build", "main"}


# Function: _extract_dart
def _extract_dart(path: Path, root: Path) -> "tuple[list[dict], list[tuple]]":
    return _generic_extract(path, root, "dart",
                            import_pat=_DART_IMPORT,
                            class_pat=_DART_CLASS,
                            func_pat=_DART_FUNC, skip_func_kw=_DART_SKIP)


# ── Groovy extractor ──────────────────────────────────────────────────────────

_GROOVY_IMPORT = re.compile(r"^import\s+([\w.*]+)", re.MULTILINE)
_GROOVY_CLASS  = re.compile(
    r"\b(?:class|interface|enum|trait|abstract\s+class)\s+(\w+)", re.MULTILINE
)
_GROOVY_FUNC   = re.compile(
    r"\b(?:def|void|String|int|boolean|List|Map)\s+(\w+)\s*\(", re.MULTILINE
)
_GROOVY_SKIP   = {"if", "while", "for", "switch", "catch", "return", "new",
                  "import", "class", "def"}


# Function: _extract_groovy
def _extract_groovy(path: Path, root: Path) -> "tuple[list[dict], list[tuple]]":
    return _generic_extract(path, root, "groovy",
                            import_pat=_GROOVY_IMPORT,
                            class_pat=_GROOVY_CLASS,
                            func_pat=_GROOVY_FUNC, skip_func_kw=_GROOVY_SKIP)


# ── SQL / DB2 extractor ───────────────────────────────────────────────────────

_SQL_CREATE = re.compile(
    r"CREATE\s+(?:OR\s+REPLACE\s+)?(?:TABLE|VIEW|FUNCTION|PROCEDURE|TRIGGER|"
    r"INDEX|SEQUENCE|PACKAGE\s+BODY|PACKAGE|TYPE)\s+(?:[\w.]+\.)?(\w+)",
    re.IGNORECASE | re.MULTILINE,
)
_SQL_EXEC   = re.compile(r"(?:CALL|EXEC(?:UTE)?)\s+(?:[\w.]+\.)?(\w+)\s*\(",
                         re.IGNORECASE | re.MULTILINE)


# Function: _extract_sql
def _extract_sql(path: Path, root: Path, language: str = "sql") -> "tuple[list[dict], list[tuple]]":
    nodes: list[dict] = []
    edges: list[tuple] = []
    try:
        source = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return nodes, edges

    rel     = path.relative_to(root)
    rel_str = str(rel).replace("\\", "/")
    layer   = _classify_layer(list(rel.parts))
    mod_id  = ".".join(rel.with_suffix("").parts)

    nodes.append({"id": mod_id, "label": rel.name, "type": "module",
                  "language": language, "file": rel_str, "layer": layer, "line": 1})

    for m in _SQL_CREATE.finditer(source):
        obj_name = m.group(1)
        obj_id   = f"{mod_id}.{obj_name}"
        line_no  = source[:m.start()].count("\n") + 1
        # Table/View → class node; function/procedure → function node
        stmt_upper = source[m.start():m.start() + 30].upper()
        obj_type = "class" if any(kw in stmt_upper for kw in ("TABLE", "VIEW", "TYPE")) else "function"
        nodes.append({"id": obj_id, "label": obj_name, "type": obj_type,
                      "language": language, "file": rel_str,
                      "layer": _classify_layer(list(rel.parts) + [obj_name]),
                      "line": line_no})
        edges.append((mod_id, obj_id, "contains"))

    for m in _SQL_EXEC.finditer(source):
        callee = m.group(1)
        edges.append((mod_id, callee, "calls"))

    return nodes, edges


# ── JSP extractor (reuse JS) ──────────────────────────────────────────────────

# Function: _extract_jsp
def _extract_jsp(path: Path, root: Path) -> "tuple[list[dict], list[tuple]]":
    """JSP files: extract Java scriptlets and JS functions; reuse JS extractor."""
    nodes, edges = _extract_js(path, root)
    # Relabel language
    for nd in nodes:
        nd["language"] = "jsp"
    return nodes, edges


# ── Public API ────────────────────────────────────────────────────────────────

_EXT_MAP: dict[str, str] = {
    # Python
    ".py":      "python",
    # Java
    ".java":    "java",
    # JavaScript / TypeScript
    ".js":      "javascript",
    ".ts":      "javascript",
    ".jsx":     "javascript",
    ".tsx":     "javascript",
    ".mjs":     "javascript",
    ".cjs":     "javascript",
    # .NET
    ".cs":      "dotnet",
    ".vb":      "dotnet",
    ".fs":      "dotnet",
    # Go
    ".go":      "go",
    # Rust
    ".rs":      "rust",
    # Kotlin
    ".kt":      "kotlin",
    ".kts":     "kotlin",
    # Scala
    ".scala":   "scala",
    ".sc":      "scala",
    # Ruby
    ".rb":      "ruby",
    ".rake":    "ruby",
    ".gemspec": "ruby",
    ".ru":      "ruby",
    # PHP
    ".php":     "php",
    ".phtml":   "php",
    ".php3":    "php",
    ".php4":    "php",
    ".php5":    "php",
    ".php7":    "php",
    # C / C++
    ".c":       "cpp",
    ".cpp":     "cpp",
    ".cc":      "cpp",
    ".cxx":     "cpp",
    ".h":       "cpp",
    ".hpp":     "cpp",
    ".hxx":     "cpp",
    # Shell
    ".sh":      "shell",
    ".bash":    "shell",
    ".zsh":     "shell",
    ".ksh":     "shell",
    ".fish":    "shell",
    ".csh":     "shell",
    ".tcsh":    "shell",
    ".bats":    "shell",
    # R
    ".r":       "r",
    ".R":       "r",
    ".rmd":     "r",
    # Dart
    ".dart":    "dart",
    # Groovy / Gradle
    ".groovy":  "groovy",
    ".gvy":     "groovy",
    ".gradle":  "groovy",
    # SQL / DB2
    ".sql":     "sql",
    ".ddl":     "sql",
    ".dml":     "sql",
    ".psql":    "sql",
    ".pgsql":   "sql",
    ".hql":     "sql",
    ".tsql":    "sql",
    ".plsql":   "sql",
    ".pls":     "sql",
    ".prc":     "sql",
    ".fnc":     "sql",
    ".trg":     "sql",
    ".pkb":     "sql",
    ".pks":     "sql",
    ".db2":     "sql",
    ".dclgen":  "sql",
    ".sqc":     "sql",
    ".sqb":     "sql",
    ".sqlj":    "sql",
    ".bnd":     "sql",
    # JSP
    ".jsp":     "jsp",
    ".jspx":    "jsp",
    ".jspf":    "jsp",
    ".tag":     "jsp",
    ".tagx":    "jsp",
    # Mainframe / COBOL (case-insensitive handled via .lower() in _process)
    ".cbl":     "cobol",
    ".cob":     "cobol",
    ".cpy":     "cobol",
    ".jcl":     "jcl",
    ".asm":     "cobol",
    ".pli":     "cobol",
    ".rexx":    "cobol",
    ".rex":     "cobol",
    ".csp":     "cobol",
    ".pnv":     "cobol",
    ".panvalet":"cobol",
}


# Language → extractor dispatch. Branches are mutually exclusive (single lang
# lookup, no fallthrough); "sql" is wrapped since it needs an extra arg.
_EXTRACTOR_DISPATCH = {
    "python":     _extract_python,
    "java":       _extract_java,
    "javascript": _extract_js,
    "dotnet":     _extract_dotnet,
    "go":         _extract_go,
    "rust":       _extract_rust,
    "kotlin":     _extract_kotlin,
    "scala":      _extract_scala,
    "ruby":       _extract_ruby,
    "php":        _extract_php,
    "cpp":        _extract_cpp,
    "shell":      _extract_shell,
    "r":          _extract_r,
    "dart":       _extract_dart,
    "groovy":     _extract_groovy,
    "sql":        lambda fpath, root: _extract_sql(fpath, root, "sql"),
    "jsp":        _extract_jsp,
    "cobol":      _extract_cobol,
    "jcl":        _extract_jcl,
}


# Function: _collect_candidate_files
def _collect_candidate_files(root: Path, max_files: int, languages: "list[str] | None") -> "list[Path]":
    # ── Phase 1: collect candidate file paths (no I/O per file) ───────────
    candidate_files: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(str(root)):
        # Prune skip dirs IN PLACE so os.walk won't descend into them
        dirnames[:] = [d for d in dirnames if d not in _SKIP_DIRS]
        dir_path = Path(dirpath)
        for fname in filenames:
            fpath = dir_path / fname
            lang = _EXT_MAP.get(fpath.suffix.lower())
            if not lang:
                continue
            if languages and lang not in languages:
                continue
            candidate_files.append(fpath)
            if len(candidate_files) >= max_files:
                break
        if len(candidate_files) >= max_files:
            break
    return candidate_files


# Function: _extract_all_files
def _extract_all_files(candidate_files: "list[Path]", root: Path) -> "tuple[list[dict], list[tuple], int]":
    # ── Phase 2: extract nodes/edges in parallel ──────────────────────────
    all_nodes: list[dict] = []
    all_edges: list[tuple] = []
    file_count = 0

    # Function: _process
    def _process(fpath: Path) -> tuple[list[dict], list[tuple]]:
        lang = _EXT_MAP.get(fpath.suffix.lower()) or _EXT_MAP.get(fpath.suffix)
        extractor = _EXTRACTOR_DISPATCH.get(lang)
        if extractor:
            return extractor(fpath, root)
        return [], []

    with ThreadPoolExecutor(max_workers=8, thread_name_prefix="kg_extract") as pool:
        futures = {pool.submit(_process, f): f for f in candidate_files}
        for fut in as_completed(futures):
            try:
                n, e = fut.result()
            except Exception:
                continue
            all_nodes.extend(n)
            all_edges.extend(e)
            file_count += 1

    return all_nodes, all_edges, file_count


# Function: _dedupe_nodes_and_edges
def _dedupe_nodes_and_edges(all_nodes: "list[dict]", all_edges: "list[tuple]") -> "tuple[list[dict], list[tuple]]":
    # Deduplicate nodes
    seen_ids: set[str] = set()
    unique_nodes: list[dict] = []
    for nd in all_nodes:
        if nd["id"] not in seen_ids:
            seen_ids.add(nd["id"])
            unique_nodes.append(nd)

    # Only keep edges whose source is a known node id
    valid_edges = [e for e in all_edges if e[0] in seen_ids]
    return unique_nodes, valid_edges


# Function: _cluster_by_layer
def _cluster_by_layer(unique_nodes: "list[dict]") -> "dict[str, list[str]]":
    clusters: dict[str, list[str]] = {}
    for nd in unique_nodes:
        clusters.setdefault(nd["layer"], []).append(nd["id"])
    return clusters


# Function: _compute_kg_stats
def _compute_kg_stats(unique_nodes: "list[dict]", valid_edges: "list[tuple]") -> "tuple[dict, dict, dict]":
    type_counts: dict[str, int] = {}
    lang_counts: dict[str, int] = {}
    for nd in unique_nodes:
        type_counts[nd["type"]]     = type_counts.get(nd["type"], 0) + 1
        lang_counts[nd["language"]] = lang_counts.get(nd["language"], 0) + 1

    edge_type_counts: dict[str, int] = {}
    for e in valid_edges:
        edge_type_counts[e[2]] = edge_type_counts.get(e[2], 0) + 1

    return type_counts, lang_counts, edge_type_counts


# Function: build_knowledge_graph
def build_knowledge_graph(
    repo_path: str,
    max_files: int = 300,
    languages: list[str] | None = None,
) -> dict:
    """Walk *repo_path* and build a rich knowledge graph.

    Uses os.walk with in-place dirnames pruning so _SKIP_DIRS directories
    (target/, node_modules/, .venv/, …) are never descended into.
    File processing is parallelised over ThreadPoolExecutor(8 workers).
    """
    root = Path(repo_path)

    candidate_files = _collect_candidate_files(root, max_files, languages)
    all_nodes, all_edges, file_count = _extract_all_files(candidate_files, root)
    unique_nodes, valid_edges = _dedupe_nodes_and_edges(all_nodes, all_edges)
    clusters = _cluster_by_layer(unique_nodes)
    type_counts, lang_counts, edge_type_counts = _compute_kg_stats(unique_nodes, valid_edges)

    return {
        "nodes": [
            {
                "id":       nd["id"],
                "label":    nd["label"],
                "type":     nd["type"],
                "language": nd["language"],
                "file":     nd["file"],
                "layer":    nd["layer"],
                "line":     nd["line"],
            }
            for nd in unique_nodes
        ],
        "edges": [
            {"from": e[0], "to": e[1], "type": e[2]}
            for e in valid_edges
        ],
        "clusters": clusters,
        "stats": {
            "total_nodes":   len(unique_nodes),
            "total_edges":   len(valid_edges),
            "files_scanned": file_count,
            "node_types":    type_counts,
            "languages":     lang_counts,
            "edge_types":    edge_type_counts,
        },
    }
