# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: StratIQ Module Analysis — runs 9 analysis passes on a local folder:
# Date: 2025-08-02
# ---------------------------------------------------------------------------
"""
services/stratiq_analysis.py
-----------------------------
StratIQ Module Analysis — runs 9 analysis passes on a local folder:

  1. Technology Stack Detection     — 20+ framework/language signatures
  2. Architecture Pattern Recognition — MVC, n-tier, SOA, WebForms, batch, monolith
  3. Circular Dependency Detection   — import-graph cycle finder
  4. Dead Code Identification        — classes/functions never referenced externally
  5. Domain Dependency Graph         — inter-folder dependency edges
  6. Database Layer Analysis         — connection strings, ORMs, raw SQL, schema touches
  7. Code Metrics                    — LOC, complexity, god classes, hotspot files
  8. Anti-Pattern Detection          — credentials, SQL concat, tight coupling, god classes
  9. Effort Estimation               — COCOMO II-based modernisation effort

Performance design
------------------
* Files are read ONCE into a shared cache before the 9 passes begin.
  Previously each pass re-opened the same files from disk (up to 330 MB of
  redundant I/O per module × 12 modules ≈ 4 GB total).
* Passes 1-8 run concurrently on a ThreadPoolExecutor (they are all
  independent; only pass 9 depends on the outputs of 7 & 8).
* Cycle deduplication uses a frozenset instead of O(N²) linear scan.

Entry point: run_stratiq_module_analysis(module_path, module_name) → dict
"""
from __future__ import annotations

import ast
import json
import math
import os
import re
import sys
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

# ── Helpers ───────────────────────────────────────────────────────────────────

_SOURCE_EXTS = {
    ".py", ".js", ".jsx", ".ts", ".tsx",
    ".java", ".cs", ".go", ".rs", ".cpp", ".c", ".h",
    ".html", ".css", ".scss", ".xml", ".sql",
    ".vb", ".rb", ".php", ".kt", ".swift", ".dart",
}

_EXCLUDE_DIRS = {
    "node_modules", ".venv", "venv", "__pycache__", ".git",
    "dist", "build", ".next", ".nuxt", "vendor", "target", "bin", "obj",
    ".mypy_cache", "htmlcov", ".tox", "release", "debug",
}

# Maximum files to scan per module (prevent runaway I/O on huge repos).
_MAX_SCAN_FILES = 500


# Function: _iter_source_files
def _iter_source_files(root: Path) -> List[Path]:
    """Enumerate source files under *root*, pruning excluded directories early.

    Uses os.walk with in-place dirnames mutation so directories like
    node_modules / .venv are never descended into, eliminating the single
    biggest bottleneck for modules with large dependency trees (previously
    rglob visited every file before the exclude filter ran).
    """
    files: List[Path] = []
    for dirpath_str, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in _EXCLUDE_DIRS]
        dp = Path(dirpath_str)
        for fname in filenames:
            if Path(fname).suffix.lower() in _SOURCE_EXTS:
                files.append(dp / fname)
    return files


# Function: _read_safe
def _read_safe(path: Path, max_bytes: int = 200_000) -> str:
    try:
        raw = path.read_bytes()[:max_bytes]
        return raw.decode("utf-8", errors="replace")
    except Exception:
        return ""


# ── Shared file cache ─────────────────────────────────────────────────────────

# Function: _build_file_cache
def _build_file_cache(files: List[Path], max_files: int = _MAX_SCAN_FILES, max_bytes: int = 100_000) -> Dict[Path, str]:
    """Read up to *max_files* source files into an in-memory cache.

    All analysis passes receive this dict so each file is read from disk
    exactly once, regardless of how many passes reference it.
    """
    cache: Dict[Path, str] = {}
    for fp in files[:max_files]:
        cache[fp] = _read_safe(fp, max_bytes)
    return cache


# Function: _cached
def _cached(fp: Path, texts: Dict[Path, str], max_bytes: int = 100_000) -> str:
    """Return cached text for *fp*, falling back to a fresh read if missing."""
    if fp in texts:
        return texts[fp]
    return _read_safe(fp, max_bytes)


# ── 1. Technology Stack Detection ─────────────────────────────────────────────

_FRAMEWORK_SIGS: List[Tuple[str, str, List[str]]] = [
    # (category, name, patterns)
    ("Frontend",   "React",           ["from 'react'", 'from "react"', "import React"]),
    ("Frontend",   "Angular",         ["@angular/core", "@Component({", "@NgModule("]),
    ("Frontend",   "Vue",             ["from 'vue'", 'from "vue"', "createApp(", "defineComponent("]),
    ("Frontend",   "Svelte",          [".svelte", "<script lang="]),
    ("Frontend",   "jQuery",          ["jquery", "$(document)", "$.ajax("]),
    ("Frontend",   "Bootstrap",       ["bootstrap.min.css", "class=\"container", "class=\"row"]),
    ("Backend",    "ASP.NET WebForms", ["<%@ Page", "System.Web.UI", "CodeBehind=", "Inherits="]),
    ("Backend",    "ASP.NET MVC",     ["System.Web.Mvc", "ControllerBase", "[HttpGet]", "[HttpPost]"]),
    ("Backend",    "ASP.NET Core",    ["Microsoft.AspNetCore", "WebApplication.CreateBuilder", "app.MapGet("]),
    ("Backend",    "Spring Boot",     ["@SpringBootApplication", "spring-boot-starter", "@RestController"]),
    ("Backend",    "Spring MVC",      ["@Controller", "DispatcherServlet", "ModelAndView"]),
    ("Backend",    "Java EE",         ["@EJB", "@Stateless", "@Stateful", "@MessageDriven", "javax.ejb"]),
    ("Backend",    "Django",          ["from django", "INSTALLED_APPS", "urlpatterns", "models.Model"]),
    ("Backend",    "FastAPI",         ["from fastapi", "FastAPI()", "@app.get(", "@router.post("]),
    ("Backend",    "Flask",           ["from flask", "Flask(__name__)", "@app.route("]),
    ("Backend",    "Express.js",      ["require('express')", 'require("express")', "app.use(", "app.listen("]),
    ("Backend",    "NestJS",          ["@nestjs/core", "@Module({", "@Injectable(", "@Controller("]),
    ("Backend",    "Laravel",         ["Illuminate\\", "artisan", "Eloquent"]),
    ("Backend",    "Rails",           ["ActiveRecord::", "ActionController::", "config/routes.rb"]),
    ("Database",   "Entity Framework",["DbContext", "OnModelCreating", "DbSet<", "Microsoft.EntityFrameworkCore"]),
    ("Database",   "Hibernate",       ["@Entity", "SessionFactory", "HibernameTemplate", "javax.persistence"]),
    ("Database",   "SQLAlchemy",      ["from sqlalchemy", "declarative_base()", "Column(", "sessionmaker("]),
    ("Database",   "ADO.NET",         ["SqlConnection", "SqlCommand", "OleDbConnection", "System.Data.SqlClient"]),
    ("Database",   "Oracle ODP.NET",  ["Oracle.DataAccess", "OracleConnection", "OracleCommand"]),
    ("Database",   "Mongoose",        ["require('mongoose')", 'require("mongoose")', "mongoose.model("]),
    ("Infra",      "Docker",          ["FROM ", "EXPOSE ", "docker-compose", "dockerfile"]),
    ("Infra",      "Kubernetes",      ["apiVersion:", "kind: Deployment", "kind: Service", "kubectl"]),
    ("Infra",      "Terraform",       ["resource \"", "provider \"", "terraform {"]),
    ("Testing",    "JUnit",           ["@Test", "org.junit", "assertEquals(", "assertThat("]),
    ("Testing",    "pytest",          ["import pytest", "def test_", "@pytest.fixture"]),
    ("Testing",    "Jest",            ["describe(", "it(", "expect(", "jest.mock("]),
    ("SOA/Batch",  "WCF",             ["ServiceContract", "OperationContract", "System.ServiceModel"]),
    ("SOA/Batch",  "SOAP",            ["<wsdl:", "SOAPAction", "System.Web.Services"]),
    ("SOA/Batch",  "Spring Batch",    ["@EnableBatchProcessing", "ItemProcessor", "JobBuilderFactory"]),
]


# Function: detect_tech_stack
def detect_tech_stack(files: List[Path], texts: Dict[Path, str] | None = None) -> dict:
    _texts = texts or {}
    lang_map = {
        ".py": "Python", ".js": "JavaScript", ".jsx": "JavaScript",
        ".ts": "TypeScript", ".tsx": "TypeScript",
        ".java": "Java", ".cs": "C#", ".go": "Go",
        ".rs": "Rust", ".cpp": "C++", ".c": "C",
        ".vb": "VB.NET", ".rb": "Ruby", ".php": "PHP",
        ".kt": "Kotlin", ".swift": "Swift",
    }

    languages: Set[str] = set()
    for fp in files:
        lang = lang_map.get(fp.suffix.lower())
        if lang:
            languages.add(lang)

    # Use cached texts (capped at _MAX_SCAN_FILES).  Previously this function
    # read every file in the module, causing 2700+ reads for large modules.
    content_list: List[str] = [_cached(fp, _texts) for fp in files[:_MAX_SCAN_FILES]]

    detected: Dict[str, List[str]] = defaultdict(list)
    for category, name, patterns in _FRAMEWORK_SIGS:
        for content in content_list:
            if any(p in content for p in patterns):
                if name not in detected[category]:
                    detected[category].append(name)
                break

    return {
        "languages":        sorted(languages),
        "frameworks":       dict(detected),
        "total_frameworks": sum(len(v) for v in detected.values()),
    }


# ── 2. Architecture Pattern Recognition ───────────────────────────────────────

_ARCH_PATTERNS: List[Tuple[str, str, List[str]]] = [
    ("MVC",          "Model-View-Controller",  ["controllers/", "controller.", "views/", "models/", "Controller.cs", "@Controller"]),
    ("n-tier",       "N-Tier Layered",         ["data/", "business/", "presentation/", "dal/", "bll/", "ui/", "services/", "repositories/"]),
    ("WebForms",     "ASP.NET WebForms",       [".aspx", "code-behind", "CodeBehind=", "<%@ Page"]),
    ("SOA",          "Service-Oriented",       ["services/", "service.java", "iservice", "WCF", "SOAP", "ServiceContract"]),
    ("Microservices","Microservices",           ["api-gateway", "docker-compose", "kubernetes", "SERVICE_", "grpc"]),
    ("Batch",        "Batch Processing",       ["batch/", "job/", "scheduler", "cron", "@Scheduled", "ItemProcessor"]),
    ("Monolith",     "Monolithic",             []),  # detected by absence and size
    ("CQRS",         "CQRS",                   ["commands/", "queries/", "ICommand", "IQuery", "CommandHandler"]),
    ("Event",        "Event-Driven",           ["events/", "EventBus", "IEventHandler", "publisher", "subscriber"]),
    ("Repository",   "Repository Pattern",     ["IRepository", "Repository.cs", "repository/", "repos/"]),
]


# Function: _match_arch_patterns
def _match_arch_patterns(all_paths: List[str], all_text_lower: str) -> list:
    detected = []
    for key, label, patterns in _ARCH_PATTERNS:
        if key == "Monolith":
            continue
        for p in patterns:
            if any(p.lower() in path for path in all_paths) or p.lower() in all_text_lower:
                detected.append({"key": key, "label": label})
                break
    return detected


_LAYER_KEYWORDS = {
    "Presentation": ["controller", "view", "ui", "web", "frontend", "page", "screen"],
    "Business":     ["service", "business", "logic", "handler", "manager", "usecase"],
    "Data":         ["repository", "dao", "data", "db", "model", "entity", "schema"],
    "Infra":        ["infra", "config", "util", "helper", "common", "middleware"],
}


# Function: _compute_layers
def _compute_layers(all_paths: List[str]) -> list:
    layers = []
    for layer, kws in _LAYER_KEYWORDS.items():
        count = sum(1 for p in all_paths if any(k in p for k in kws))
        if count > 0:
            layers.append({"layer": layer, "file_count": count})
    return layers


# Function: detect_architecture_patterns
def detect_architecture_patterns(
    files: List[Path], root: Path,
    texts: Dict[Path, str] | None = None,
) -> dict:
    _texts = texts or {}
    all_paths = [str(fp.relative_to(root)).lower().replace("\\", "/") for fp in files]

    # Build combined text from cached reads — avoids re-opening each file.
    sample = files[:200]
    all_text = "\n".join(_cached(fp, _texts, 30_000) for fp in sample)

    detected = _match_arch_patterns(all_paths, all_text.lower())

    service_like = {"SOA", "Microservices", "Event"}
    if len(files) > 50 and not any(d["key"] in service_like for d in detected):
        detected.append({"key": "Monolith", "label": "Monolithic Architecture"})

    layers = _compute_layers(all_paths)

    return {
        "detected_patterns": detected,
        "layers":            layers,
        "primary_pattern":   detected[0]["label"] if detected else "Unknown",
    }


# ── 3. Circular Dependency Detection ─────────────────────────────────────────

_PY_IMPORT_RE  = re.compile(r'^(?:from\s+([\w.]+)\s+import|import\s+([\w.,\s]+))', re.MULTILINE)
_JS_IMPORT_RE  = re.compile(r'(?:import\s+.*?from\s+["\']([^"\']+)["\']|require\(["\']([^"\']+)["\']\))')
_JAVA_IMPORT_RE= re.compile(r'^import\s+([\w.]+);', re.MULTILINE)
_CS_IMPORT_RE  = re.compile(r'^using\s+([\w.]+);', re.MULTILINE)


# Function: _extract_py_imports
def _extract_py_imports(text: str) -> List[str]:
    imports = []
    for m in _PY_IMPORT_RE.finditer(text):
        mod = (m.group(1) or m.group(2) or "").split(",")[0].strip()
        if mod:
            imports.append(mod.split(".")[0])
    return imports


# Function: _extract_js_imports
def _extract_js_imports(text: str) -> List[str]:
    imports = []
    for m in _JS_IMPORT_RE.finditer(text):
        mod = (m.group(1) or m.group(2) or "").strip()
        if mod and not mod.startswith("."):
            continue
        if mod:
            imports.append(mod)
    return imports


# Function: _extract_java_imports
def _extract_java_imports(text: str) -> List[str]:
    return [m.group(1).rsplit(".", 1)[0] for m in _JAVA_IMPORT_RE.finditer(text)]


# Function: _extract_cs_imports
def _extract_cs_imports(text: str) -> List[str]:
    return [m.group(1) for m in _CS_IMPORT_RE.finditer(text)]


# Function: _extract_imports
def _extract_imports(fp: Path, text: str) -> List[str]:
    ext = fp.suffix.lower()
    if ext == ".py":
        return _extract_py_imports(text)
    if ext in (".js", ".jsx", ".ts", ".tsx"):
        return _extract_js_imports(text)
    if ext == ".java":
        return _extract_java_imports(text)
    if ext == ".cs":
        return _extract_cs_imports(text)
    return []


# Function: _expand_cycle_node
def _expand_cycle_node(
    node: str, path: List[str], on_stack: Set[str],
    graph: Dict[str, Set[str]], visited: Set[str],
    seen_keys: Set[frozenset], cycles: List[List[str]], stack: list,
) -> None:
    for neighbour in graph.get(node, set()):
        if neighbour in on_stack:
            idx = path.index(neighbour)
            cycle = path[idx:] + [neighbour]
            key = frozenset(cycle)
            if key not in seen_keys:
                seen_keys.add(key)
                cycles.append(cycle)
        elif neighbour not in visited:
            stack.append((neighbour, path + [neighbour], on_stack | {neighbour}))


# Function: _find_cycles
def _find_cycles(graph: Dict[str, Set[str]]) -> List[List[str]]:
    """Detect cycles with iterative DFS.

    Uses a frozenset for O(1) cycle deduplication instead of the previous
    O(N²) ``any(tuple(sorted(c)) == key for c in cycles)`` scan.
    Iterative traversal avoids Python's default recursion limit.
    """
    visited: Set[str] = set()
    cycles: List[List[str]] = []
    seen_keys: Set[frozenset] = set()

    for start in list(graph.keys()):
        if start in visited or len(cycles) >= 20:
            break
        # Stack items: (node, path_list, on_stack_set)
        stack = [(start, [start], {start})]
        while stack and len(cycles) < 20:
            node, path, on_stack = stack.pop()
            visited.add(node)
            _expand_cycle_node(node, path, on_stack, graph, visited, seen_keys, cycles, stack)

    return cycles


# Function: _build_module_map
def _build_module_map(files: List[Path], root: Path) -> Dict[str, str]:
    module_map: Dict[str, str] = {}
    for fp in files:
        rel = str(fp.relative_to(root)).replace("\\", "/")
        mod_name = rel.replace("/", ".").rsplit(".", 1)[0]
        module_map[mod_name] = rel
    return module_map


# Function: _link_import_to_graph
def _link_import_to_graph(imp: str, src_mod: str, rel: str, module_map: Dict[str, str], graph: Dict[str, Set[str]]) -> None:
    for known_mod in module_map:
        if known_mod.endswith(imp) or known_mod.endswith("." + imp):
            graph[src_mod].add(known_mod)
            break
    if imp.startswith("."):
        parent = Path(rel).parent
        resolved = str((parent / imp).resolve()).replace("\\", "/")
        for known in module_map.values():
            if resolved in known or known in resolved:
                graph[src_mod].add(known.replace("/", ".").rsplit(".", 1)[0])


# Function: _add_file_imports_to_graph
def _add_file_imports_to_graph(
    fp: Path, texts: Dict[Path, str], root: Path, module_map: Dict[str, str], graph: Dict[str, Set[str]],
) -> None:
    text = _cached(fp, texts, 60_000)
    rel = str(fp.relative_to(root)).replace("\\", "/")
    src_mod = rel.replace("/", ".").rsplit(".", 1)[0]
    imports = _extract_imports(fp, text)
    for imp in imports:
        _link_import_to_graph(imp, src_mod, rel, module_map, graph)


# Function: detect_circular_dependencies
def detect_circular_dependencies(
    files: List[Path], root: Path,
    texts: Dict[Path, str] | None = None,
) -> dict:
    _texts = texts or {}
    graph: Dict[str, Set[str]] = defaultdict(set)
    module_map = _build_module_map(files, root)

    for fp in files[:300]:
        _add_file_imports_to_graph(fp, _texts, root, module_map, graph)

    cycles = _find_cycles(dict(graph))
    return {
        "cycles":     cycles[:20],
        "cycle_count": len(cycles),
        "risk_label": "HIGH" if len(cycles) > 5 else ("MEDIUM" if len(cycles) > 0 else "LOW"),
    }


# ── 4. Dead Code Identification ───────────────────────────────────────────────

_PY_CLASS_RE   = re.compile(r'^class\s+(\w+)', re.MULTILINE)
_PY_FUNC_RE    = re.compile(r'^def\s+(\w+)', re.MULTILINE)
_JS_CLASS_RE   = re.compile(r'\bclass\s+(\w+)', re.MULTILINE)
_JS_FUNC_RE    = re.compile(r'(?:function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?(?:function|\())', re.MULTILINE)
_JAVA_CLASS_RE = re.compile(r'\bclass\s+(\w+)', re.MULTILINE)
_CS_CLASS_RE   = re.compile(r'\bclass\s+(\w+)', re.MULTILINE)


# Function: _extract_defined_symbols
def _extract_defined_symbols(fp: Path, text: str) -> Set[str]:
    ext = fp.suffix.lower()
    symbols: Set[str] = set()
    if ext == ".py":
        symbols.update(m.group(1) for m in _PY_CLASS_RE.finditer(text))
        symbols.update(m.group(1) for m in _PY_FUNC_RE.finditer(text)
                       if not m.group(1).startswith("_"))
    elif ext in (".js", ".jsx", ".ts", ".tsx"):
        symbols.update(m.group(1) for m in _JS_CLASS_RE.finditer(text))
        for m in _JS_FUNC_RE.finditer(text):
            s = m.group(1) or m.group(2)
            if s:
                symbols.add(s)
    elif ext == ".java":
        symbols.update(m.group(1) for m in _JAVA_CLASS_RE.finditer(text))
    elif ext == ".cs":
        symbols.update(m.group(1) for m in _CS_CLASS_RE.finditer(text))
    return symbols


# Function: _collect_file_symbols
def _collect_file_symbols(sample: List[Path], texts: Dict[Path, str]) -> Tuple[List[str], Dict[str, Set[str]]]:
    cached_texts: List[str] = []
    file_symbols: Dict[str, Set[str]] = {}
    for fp in sample:
        text = _cached(fp, texts, 80_000)
        cached_texts.append(text)
        syms = _extract_defined_symbols(fp, text)
        if syms:
            file_symbols[str(fp)] = syms
    return cached_texts, file_symbols


# Function: _compute_word_freq
def _compute_word_freq(cached_texts: List[str]) -> Dict[str, int]:
    # O(N) word-frequency pass — avoids O(symbols × total_chars) blowup.
    combined = "\n".join(cached_texts)
    word_freq: Dict[str, int] = defaultdict(int)
    for m in re.finditer(r'\b\w+\b', combined):
        word_freq[m.group()] += 1
    return word_freq


# Function: _find_dead_symbols
def _find_dead_symbols(file_symbols: Dict[str, Set[str]], word_freq: Dict[str, int]) -> List[dict]:
    dead: List[dict] = []
    for fp_str, syms in file_symbols.items():
        for sym in syms:
            if word_freq.get(sym, 0) <= 1:
                dead.append({"symbol": sym, "file": Path(fp_str).name})
                if len(dead) >= 50:
                    break
        if len(dead) >= 50:
            break
    return dead


# Function: identify_dead_code
def identify_dead_code(
    files: List[Path],
    texts: Dict[Path, str] | None = None,
) -> dict:
    _texts = texts or {}
    sample = files[:300]
    cached_texts, file_symbols = _collect_file_symbols(sample, _texts)
    word_freq = _compute_word_freq(cached_texts)
    dead = _find_dead_symbols(file_symbols, word_freq)

    return {
        "unreferenced_symbols": dead,
        "count":      len(dead),
        "risk_label": "HIGH" if len(dead) > 20 else ("MEDIUM" if len(dead) > 5 else "LOW"),
    }


# ── 5. Domain Dependency Graph ────────────────────────────────────────────────

# Function: _domain_for_file
def _domain_for_file(fp: Path, root: Path) -> str:
    try:
        parts = fp.relative_to(root).parts
        return parts[0] if len(parts) > 1 else "_root"
    except Exception:
        return "_root"


# Function: _build_domain_edges
def _build_domain_edges(domains: Dict[str, List[Path]], texts: Dict[Path, str]) -> Set[Tuple[str, str]]:
    edges_set: Set[Tuple[str, str]] = set()
    domain_keywords: Dict[str, List[str]] = {
        d: [fp.stem.lower() for fp in flist[:20]]
        for d, flist in domains.items()
    }

    for src_domain, src_files in list(domains.items())[:50]:
        for fp in src_files[:20]:
            text = _cached(fp, texts, 30_000).lower()
            for tgt_domain, kws in domain_keywords.items():
                if tgt_domain == src_domain:
                    continue
                if any(kw in text for kw in kws if len(kw) > 3):
                    edges_set.add((src_domain, tgt_domain))
    return edges_set


# Function: build_domain_graph
def build_domain_graph(
    files: List[Path], root: Path,
    texts: Dict[Path, str] | None = None,
) -> dict:
    _texts = texts or {}
    domains: Dict[str, List[Path]] = defaultdict(list)
    for fp in files:
        domain = _domain_for_file(fp, root)
        if domain not in _EXCLUDE_DIRS:
            domains[domain].append(fp)

    nodes = [{"id": d, "label": d, "file_count": len(fs)} for d, fs in domains.items()]
    edges_set = _build_domain_edges(domains, _texts)
    edges = [{"source": s, "target": t} for s, t in edges_set]
    return {"nodes": nodes, "edges": edges}


# ── 6. Database Layer Analysis ────────────────────────────────────────────────

_DB_PATTERNS = [
    ("Connection String",   r'(?:connectionString|connection_string|connStr|conn_str)\s*[=:]\s*["\'][^"\']{10,}["\']'),
    ("Hardcoded DB Host",   r'(?:Server|Data Source|Host)\s*=\s*[\w\-.]+(?:\.\w+)+'),
    ("Raw SQL Query",       r'(?:SELECT|INSERT|UPDATE|DELETE|CREATE|ALTER|DROP)\s+\w+'),
    ("SQL Concatenation",   r'(?:\"SELECT |"INSERT |"UPDATE |"DELETE ).*?\+'),
    ("ADO.NET",             r'(?:SqlConnection|OleDbConnection|OdbcConnection|SqlCommand|SqlDataReader)'),
    ("Oracle Pattern",      r'(?:OracleConnection|OracleCommand|Oracle\.DataAccess|ODP\.NET)'),
    ("Oracle SQL",          r'(?:ROWNUM|NVL\(|DECODE\(|SYSDATE|dual|v\$session)'),
    ("Connection Pool",     r'(?:pooling\s*=\s*true|Max\s*Pool\s*Size|Min\s*Pool\s*Size)'),
    ("ORM Entity",          r'(?:@Entity|@Table|@Column|DbSet<|[Mm]odel\.py|models\.py)'),
    ("Schema Migration",    r'(?:migrate|migration|schema_version|flyway|liquibase|alembic)'),
]

_DB_COMPILED = [(label, re.compile(pat, re.IGNORECASE)) for label, pat in _DB_PATTERNS]

_ORM_SIGS = [
    ("Entity Framework", ["DbContext", "DbSet<", "OnModelCreating"]),
    ("Hibernate",        ["@Entity", "SessionFactory", "HibernameTemplate"]),
    ("SQLAlchemy",       ["declarative_base", "Column(", "sessionmaker"]),
    ("Django ORM",       ["models.Model", "ForeignKey(", "CharField("]),
    ("Sequelize",        ["sequelize.define", "DataTypes.", "belongsTo("]),
    ("TypeORM",          ["@Entity()", "@Column()", "getRepository("]),
    ("Mongoose",         ["mongoose.model", "Schema(", "mongoose.connect"]),
    ("ADO.NET Raw",      ["SqlConnection", "SqlCommand", "ExecuteReader"]),
]


# Function: _scan_db_patterns_in_file
def _scan_db_patterns_in_file(
    text: str, fname: str, detected_patterns: Dict[str, int],
    connection_strings: List[str], raw_sql_files: List[str],
) -> bool:
    is_db_file = False
    for label, compiled_pat in _DB_COMPILED:
        matches = compiled_pat.findall(text)
        if matches:
            detected_patterns[label] += len(matches)
            is_db_file = True
            if label == "Connection String":
                connection_strings.extend(
                    [m[:80] + "…" if len(m) > 80 else m for m in matches[:3]]
                )
            if label == "Raw SQL Query":
                raw_sql_files.append(fname)
    return is_db_file


# Function: _scan_orms_in_file
def _scan_orms_in_file(text: str, detected_orms: List[str], db_techs: Set[str]) -> None:
    for orm_name, orm_sigs in _ORM_SIGS:
        if orm_name not in detected_orms and any(s in text for s in orm_sigs):
            detected_orms.append(orm_name)
            db_techs.add(orm_name)


# Function: _detect_db_techs_from_text
def _detect_db_techs_from_text(tl: str, db_techs: Set[str]) -> None:
    if "oracle" in tl or "rownum" in tl:
        db_techs.add("Oracle DB")
    if "mysql" in tl:
        db_techs.add("MySQL")
    if "postgresql" in tl or "psycopg" in tl:
        db_techs.add("PostgreSQL")
    if "sqlite" in tl:
        db_techs.add("SQLite")
    if "mongodb" in tl:
        db_techs.add("MongoDB")
    if "redis" in tl:
        db_techs.add("Redis")
    if "cassandra" in tl:
        db_techs.add("Cassandra")
    if "sql server" in tl or "mssql" in tl:
        db_techs.add("SQL Server")


# Function: analyze_database_layer
def analyze_database_layer(
    files: List[Path],
    texts: Dict[Path, str] | None = None,
) -> dict:
    _texts = texts or {}
    db_files: List[str] = []
    connection_strings: List[str] = []
    raw_sql_files: List[str] = []
    detected_patterns: Dict[str, int] = defaultdict(int)
    detected_orms: List[str] = []
    db_techs: Set[str] = set()

    for fp in files[:500]:
        text = _cached(fp, _texts)
        fname = fp.name

        is_db_file = _scan_db_patterns_in_file(text, fname, detected_patterns, connection_strings, raw_sql_files)
        if is_db_file:
            db_files.append(fname)

        _scan_orms_in_file(text, detected_orms, db_techs)
        _detect_db_techs_from_text(text.lower(), db_techs)

    sql_concat_count = detected_patterns.get("SQL Concatenation", 0)
    return {
        "db_files":                    list(set(db_files))[:30],
        "db_file_count":               len(set(db_files)),
        "connection_strings_found":    len(connection_strings),
        "connection_string_samples":   connection_strings[:5],
        "raw_sql_files":               list(set(raw_sql_files))[:20],
        "raw_sql_file_count":          len(set(raw_sql_files)),
        "sql_concatenation_count":     sql_concat_count,
        "orms_detected":               detected_orms,
        "db_technologies":             sorted(db_techs),
        "pattern_counts":              dict(detected_patterns),
        "risk_label": "HIGH" if sql_concat_count > 5 else ("MEDIUM" if len(db_files) > 0 else "LOW"),
    }


# ── 7. Code Metrics ───────────────────────────────────────────────────────────

_CC_PATTERNS = [
    re.compile(r'\bif\b',    re.IGNORECASE),
    re.compile(r'\belif\b',  re.IGNORECASE),
    re.compile(r'\belse\b',  re.IGNORECASE),
    re.compile(r'\bfor\b',   re.IGNORECASE),
    re.compile(r'\bwhile\b', re.IGNORECASE),
    re.compile(r'\bcase\b',  re.IGNORECASE),
    re.compile(r'\bcatch\b', re.IGNORECASE),
    re.compile(r'\b&&\b'),
    re.compile(r'\|\|'),
]
_METRICS_METHOD_RE = re.compile(r'\bdef\s+\w+|\bpublic\s+\w+\s+\w+\s*\(', re.MULTILINE)


# Function: _lang_class_func_counts
def _lang_class_func_counts(ext: str, text: str) -> Tuple[list, int]:
    if ext == ".py":
        cls_list = _PY_CLASS_RE.findall(text)
        funcs    = len(_PY_FUNC_RE.findall(text))
    elif ext in (".js", ".jsx", ".ts", ".tsx"):
        cls_list = _JS_CLASS_RE.findall(text)
        funcs    = len(re.findall(r'\bfunction\s+\w+', text))
    elif ext == ".java":
        cls_list = _JAVA_CLASS_RE.findall(text)
        funcs    = len(re.findall(r'\b(?:public|private|protected)\s+\w+\s+\w+\s*\(', text))
    elif ext == ".cs":
        cls_list = _CS_CLASS_RE.findall(text)
        funcs    = len(re.findall(r'\b(?:public|private|protected|internal)\s+\w+\s+\w+\s*\(', text))
    else:
        cls_list = []
        funcs    = 0
    return cls_list, funcs


# Function: _detect_god_classes_in_file
def _detect_god_classes_in_file(ext: str, cls_list: list, text: str, sloc: int, fname: str, god_classes: List[str]) -> None:
    if ext in (".py", ".java", ".cs") and cls_list and len(god_classes) < 40:
        method_count = len(_METRICS_METHOD_RE.findall(text))
        if method_count > 15 or sloc > 300:
            for cls in cls_list:
                god_classes.append(f"{cls} ({fname})")


# Function: _process_file_metrics
def _process_file_metrics(fp: Path, text: str, god_classes: List[str], file_metrics: List[dict]) -> dict:
    lines = text.splitlines()
    code_lines = [l for l in lines if l.strip() and not l.strip().startswith(("#", "//", "/*", "*", "'''", '"""'))]
    sloc = len(code_lines)

    ext = fp.suffix.lower()
    cls_list, funcs = _lang_class_func_counts(ext, text)

    cc = 1 + sum(len(p.findall(text)) for p in _CC_PATTERNS)
    counted = sloc > 0
    if counted:
        file_metrics.append({
            "name":       fp.name,
            "sloc":       sloc,
            "classes":    len(cls_list),
            "functions":  funcs,
            "complexity": cc,
        })

    _detect_god_classes_in_file(ext, cls_list, text, sloc, fp.name, god_classes)

    return {
        "sloc": sloc,
        "lines": len(lines),
        "functions": funcs,
        "classes": len(cls_list),
        "cc": cc,
        "counted": counted,
    }


# Function: compute_code_metrics
def compute_code_metrics(
    files: List[Path],
    texts: Dict[Path, str] | None = None,
) -> dict:
    _texts = texts or {}
    total_sloc = 0
    total_lines = 0
    total_functions = 0
    total_classes = 0
    complexity_sum = 0
    complexity_count = 0
    file_metrics: List[dict] = []
    god_classes: List[str] = []

    for fp in files[:500]:
        text = _cached(fp, _texts)
        stats = _process_file_metrics(fp, text, god_classes, file_metrics)
        total_sloc      += stats["sloc"]
        total_lines     += stats["lines"]
        total_classes   += stats["classes"]
        total_functions += stats["functions"]
        if stats["counted"]:
            complexity_sum   += stats["cc"]
            complexity_count += 1

    file_metrics.sort(key=lambda x: x["complexity"], reverse=True)
    hotspots = file_metrics[:10]

    avg_cc = complexity_sum / complexity_count if complexity_count > 0 else 0
    return {
        "total_sloc":           total_sloc,
        "total_lines":          total_lines,
        "total_files":          len(files),
        "total_functions":      total_functions,
        "total_classes":        total_classes,
        "avg_complexity":       round(avg_cc, 1),
        "hotspot_files":        hotspots,
        "god_classes":          list(set(god_classes))[:20],
        "maintainability_index": round(
            max(0, 171 - 5.2 * math.log(avg_cc + 1) - 0.23 * avg_cc
                     - 16.2 * math.log(total_sloc / max(1, len(files)) + 1)), 1
        ),
    }


# ── 8. Anti-Pattern Detection ─────────────────────────────────────────────────

_ANTIPATTERN_COMPILED: List[Tuple[str, Optional[re.Pattern], str]] = [
    ("Hardcoded Credential",
     re.compile(r'(?:password|passwd|secret|api_key|apikey|token)\s*=\s*["\'][^"\']{4,}["\']', re.IGNORECASE),
     "CRITICAL"),
    ("Hardcoded IP Address",
     re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}:\d{2,5}\b'),
     "HIGH"),
    ("SQL Concatenation",
     re.compile(r'(?:"SELECT |"INSERT |"UPDATE |"DELETE ).*?\+'),
     "HIGH"),
    ("Empty Catch Block",
     re.compile(r'(?:catch\s*\([^)]*\)\s*\{\s*\}|except\s*(?:\w+\s*)?:\s*pass)'),
     "MEDIUM"),
    ("TODO / FIXME Comment",
     re.compile(r'(?:#|//|/\*)\s*(?:TODO|FIXME|HACK|XXX)'),
     "LOW"),
    ("Magic Number",
     re.compile(r'(?<!\w)(?!0\b|1\b|2\b|-1\b)\d{3,}(?!\w)'),
     "LOW"),
    ("Deep Nesting (5+)",
     re.compile(r'^[ \t]{20,}(?:if|for|while)\b', re.MULTILINE),
     "MEDIUM"),
    ("Commented-Out Code",
     re.compile(r'(?:#|//)\s+(?:if|for|while|def|class|return|var|const|let)\s'),
     "LOW"),
]
_GOD_CLASS_METHOD_RE = re.compile(r'\bdef\s+\w+|\bpublic\s+(?:static\s+)?\w+\s+\w+\s*\(', re.MULTILINE)


# Function: _scan_antipatterns_in_file
def _scan_antipatterns_in_file(text: str, fname: str, findings: Dict[str, List[dict]]) -> None:
    for label, pattern, severity in _ANTIPATTERN_COMPILED:
        try:
            matches = pattern.findall(text)
            if matches:
                findings[label].append({
                    "file":     fname,
                    "count":    len(matches),
                    "severity": severity,
                })
        except re.error:
            pass

    method_count = len(_GOD_CLASS_METHOD_RE.findall(text))
    if method_count > 20:
        findings["God Class (>20 methods)"].append({
            "file":     fname,
            "count":    method_count,
            "severity": "MEDIUM",
        })


# Function: _summarize_antipattern_findings
def _summarize_antipattern_findings(findings: Dict[str, List[dict]]) -> list:
    summary = []
    for label, hits in findings.items():
        severity = hits[0]["severity"] if hits else "LOW"
        summary.append({
            "pattern":        label,
            "severity":       severity,
            "affected_files": len(hits),
            "total_count":    sum(h["count"] for h in hits),
            "top_files":      [h["file"] for h in sorted(hits, key=lambda x: -x["count"])[:5]],
        })
    summary.sort(key=lambda x: {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}.get(x["severity"], 4))
    return summary


# Function: detect_anti_patterns
def detect_anti_patterns(
    files: List[Path],
    texts: Dict[Path, str] | None = None,
) -> dict:
    _texts = texts or {}
    findings: Dict[str, List[dict]] = defaultdict(list)

    for fp in files[:200]:
        text = _cached(fp, _texts, 60_000)
        _scan_antipatterns_in_file(text, fp.name, findings)

    summary = _summarize_antipattern_findings(findings)
    total_critical = sum(1 for s in summary if s["severity"] == "CRITICAL")
    total_high     = sum(1 for s in summary if s["severity"] == "HIGH")

    return {
        "patterns":       summary,
        "total_patterns": len(summary),
        "critical_count": total_critical,
        "high_count":     total_high,
        "risk_label":     "CRITICAL" if total_critical > 0 else ("HIGH" if total_high > 0 else "MEDIUM"),
    }


# ── 9. Effort Estimation ──────────────────────────────────────────────────────

_COCOMO_A = 2.94
_COCOMO_B = 0.91
_AVG_SALARY_MONTH      = 10_000
_MODERNIZATION_ACCELERATION = 12.0


# Function: estimate_effort
def estimate_effort(code_metrics: dict, anti_patterns: dict, circular_deps: dict) -> dict:
    sloc  = code_metrics.get("total_sloc", 0)
    ksloc = max(sloc / 1_000, 0.01)

    base_effort = _COCOMO_A * (ksloc ** _COCOMO_B)

    em = 1.0
    if anti_patterns.get("risk_label") == "CRITICAL":
        em *= 1.35
    elif anti_patterns.get("risk_label") == "HIGH":
        em *= 1.20
    elif anti_patterns.get("risk_label") == "MEDIUM":
        em *= 1.10

    if circular_deps.get("cycle_count", 0) > 5:
        em *= 1.20
    elif circular_deps.get("cycle_count", 0) > 0:
        em *= 1.10

    god_class_count = len(code_metrics.get("god_classes", []))
    if god_class_count > 5:
        em *= 1.15

    remediation_effort   = base_effort * em
    debt_usd             = remediation_effort * _AVG_SALARY_MONTH
    accelerated_effort   = remediation_effort / _MODERNIZATION_ACCELERATION

    risk = "LOW"
    if remediation_effort > 24:
        risk = "CRITICAL"
    elif remediation_effort > 12:
        risk = "HIGH"
    elif remediation_effort > 3:
        risk = "MEDIUM"

    total_files  = code_metrics.get("total_files", 0)
    quick_wins   = max(1, int(total_files * 0.30))
    medium_work  = max(1, int(total_files * 0.50))
    complex_work = max(0, total_files - quick_wins - medium_work)

    return {
        "total_sloc":                  sloc,
        "estimated_effort_months":     round(remediation_effort, 1),
        "debt_usd":                    round(debt_usd),
        "modernization_effort_months": round(accelerated_effort, 1),
        "effort_multiplier":           round(em, 2),
        "risk_label":                  risk,
        "acceleration_factor":         f"{_MODERNIZATION_ACCELERATION:.0f}×",
        "quick_wins_files":            quick_wins,
        "medium_work_files":           medium_work,
        "complex_work_files":          complex_work,
        "benchmark_note": (
            f"Modernisation effort estimated at {accelerated_effort:.1f} months "
            f"with {_MODERNIZATION_ACCELERATION:.0f}× AI acceleration."
        ),
    }


# ── Project Marker Detection ───────────────────────────────────────────────────

_PROJECT_MARKERS = [
    "package.json", "requirements.txt", "setup.py", "pyproject.toml",
    "pom.xml", "build.gradle", "build.gradle.kts",
    "Cargo.toml", "go.mod", "composer.json", "Gemfile",
    "*.csproj", "*.sln", "*.vbproj", "CMakeLists.txt",
    "Makefile", "Dockerfile", "docker-compose.yml", "docker-compose.yaml",
]


# Function: is_separate_project
def is_separate_project(path: Path) -> bool:
    for marker in _PROJECT_MARKERS:
        if "*" in marker:
            if list(path.glob(marker)):
                return True
        else:
            if (path / marker).exists():
                return True
    root_sources = [f for f in path.iterdir() if f.is_file() and f.suffix.lower() in _SOURCE_EXTS]
    return len(root_sources) >= 5


# ── Main entry point ──────────────────────────────────────────────────────────

# Function: run_stratiq_module_analysis
def run_stratiq_module_analysis(
    module_path: str,
    module_name: str,
    on_progress=None,
) -> dict:
    """
    Run all 9 StratIQ analyses on a single module folder.

    Performance path
    ~~~~~~~~~~~~~~~~
    1. Discover all source files (rglob).
    2. Read up to 500 files ONCE into an in-memory cache.
    3. Run passes 1-8 concurrently on a 6-worker thread pool — each pass
       receives the same cache and performs no additional disk I/O.
    4. Compute effort (pass 9) from the metric outputs of passes 7 & 8.

    Wall-clock time is dominated by the slowest parallel pass rather than
    the sum of all passes, and repeated disk I/O is eliminated entirely.
    """
    root = Path(module_path)
    if not root.exists() or not root.is_dir():
        return {"error": f"Path not found: {module_path}", "module_name": module_name}

    # Function: _progress
    def _progress(phase: str, pct: int, msg: str):
        if on_progress:
            on_progress(phase, pct, msg)

    # ── Phase 0: File discovery ───────────────────────────────────────────────
    _progress("scanning", 5, f"Scanning {module_name}…")
    files = _iter_source_files(root)

    # ── Phase 1: Read files once into shared cache ────────────────────────────
    _progress("reading", 12, f"Reading {min(len(files), _MAX_SCAN_FILES)} source files…")
    texts = _build_file_cache(files)

    # ── Phase 2: Run 8 independent passes in parallel ─────────────────────────
    _progress("analyzing", 20, "Running parallel analysis passes…")

    _WORKERS = min(6, max(1, len(files) // 20 + 1))  # scale workers with module size

    futures: Dict = {}
    with ThreadPoolExecutor(max_workers=_WORKERS, thread_name_prefix="stratiq") as pool:
        futures["tech_stack"]   = pool.submit(detect_tech_stack,              files, texts)
        futures["architecture"] = pool.submit(detect_architecture_patterns,   files, root, texts)
        futures["circular_deps"]= pool.submit(detect_circular_dependencies,   files, root, texts)
        futures["dead_code"]    = pool.submit(identify_dead_code,             files, texts)
        futures["domain_graph"] = pool.submit(build_domain_graph,             files, root, texts)
        futures["db_analysis"]  = pool.submit(analyze_database_layer,         files, texts)
        futures["code_metrics"] = pool.submit(compute_code_metrics,           files, texts)
        futures["anti_patterns"]= pool.submit(detect_anti_patterns,           files, texts)

        # Report progress as each pass completes
        _pass_progress = {
            "tech_stack":    (30, "Technology stack detected"),
            "architecture":  (40, "Architecture patterns recognised"),
            "circular_deps": (50, "Circular dependencies analysed"),
            "dead_code":     (58, "Dead code identified"),
            "domain_graph":  (65, "Domain dependency graph built"),
            "db_analysis":   (73, "Database layer analysed"),
            "code_metrics":  (81, "Code metrics computed"),
            "anti_patterns": (89, "Anti-patterns detected"),
        }
        results: Dict = {}
        for key, fut in futures.items():
            try:
                results[key] = fut.result(timeout=120)
            except Exception as exc:
                import logging
                logging.getLogger(__name__).warning(
                    "Pass '%s' failed for %s: %s", key, module_name, exc
                )
                results[key] = {}
            pct, msg = _pass_progress.get(key, (80, key))
            _progress(key, pct, msg + "…")

    # ── Phase 3: Effort estimation (depends on metrics + anti-patterns) ───────
    _progress("effort", 95, "Estimating modernisation effort…")
    effort = estimate_effort(
        results.get("code_metrics", {}),
        results.get("anti_patterns", {}),
        results.get("circular_deps", {}),
    )

    _progress("done", 100, f"{module_name} complete")

    return {
        "module_name":   module_name,
        "module_path":   module_path,
        "file_count":    len(files),
        "tech_stack":    results.get("tech_stack",    {}),
        "architecture":  results.get("architecture",  {}),
        "circular_deps": results.get("circular_deps", {}),
        "dead_code":     results.get("dead_code",     {}),
        "domain_graph":  results.get("domain_graph",  {}),
        "db_analysis":   results.get("db_analysis",   {}),
        "code_metrics":  results.get("code_metrics",  {}),
        "anti_patterns": results.get("anti_patterns", {}),
        "effort":        effort,
    }
