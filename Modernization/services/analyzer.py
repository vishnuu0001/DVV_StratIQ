# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: services/analyzer.py
# Date: 2025-10-19
# ---------------------------------------------------------------------------
"""
services/analyzer.py
Deep code analysis engine for legacy projects.

Detects:
  - Technology stack (ASP.NET, Java EE, Spring, VB6, COBOL, PHP, etc.)
  - Architecture patterns (WebForms, MVC, N-Tier, Monolith, SOA)
  - Database layer (Oracle, SQL Server, MySQL mappings, raw ADO, Hibernate, etc.)
  - Code metrics (file count, LOC, complexity indicators)
  - Oracle-specific SQL patterns
  - Hard-coded credentials or connection strings
  - Anti-patterns (God classes, deep coupling, magic strings)
  - Service boundaries (natural micro-service split points)
"""
from __future__ import annotations

import ast
import os
import re
from datetime import datetime, timezone
from collections import defaultdict
from pathlib import Path
from typing import Callable, Dict, List, Optional


# ─── Extension → language map ─────────────────────────────────────────────────
_LANG_MAP: Dict[str, str] = {
    ".cs":     "csharp",
    ".vb":     "visualbasic",
    ".aspx":   "aspnet-webforms",
    ".ascx":   "aspnet-webforms",
    ".master": "aspnet-webforms",
    ".cshtml": "aspnet-razor",
    ".vbhtml": "aspnet-razor",
    ".java":      "java",
    ".kt":        "kotlin",
    ".kts":       "kotlin",
    ".groovy":    "groovy",
    ".gradle":    "gradle",
    ".py":        "python",
    ".js":        "javascript",
    ".ts":        "typescript",
    ".jsx":       "javascript",
    ".tsx":       "typescript",
    ".php":       "php",
    ".rb":        "ruby",
    ".go":        "go",
    ".cpp":       "cpp",
    ".c":         "c",
    ".cbl":       "cobol",
    ".cob":       "cobol",
    ".f":         "fortran",
    ".for":       "fortran",
    ".f90":       "fortran",
    ".f95":       "fortran",
    ".pas":       "pascal",
    ".pp":        "pascal",
    ".dpr":       "pascal",
    ".pli":       "pli",
    ".pl1":       "pli",
    ".jcl":       "jcl",
    ".m":         "mumps",
    ".nsp":       "natural",
    ".nat":       "natural",
    ".p":         "progress4gl",
    ".adb":       "ada",
    ".ads":       "ada",
    ".ml":        "ocaml",
    ".mli":       "ocaml",
    ".pro":       "prolog",
    ".rpg":       "rpg",
    ".rpgle":     "rpg",
    ".sqlrpgle":  "rpg-sql",
    ".clp":       "ibmi-cl",
    ".clle":      "ibmi-cl",
    ".dds":       "ibmi-dds",
    ".pf":        "ibmi-dds",
    ".lf":        "ibmi-dds",
    ".dspf":      "ibmi-display-file",
    ".prtf":      "ibmi-printer-file",
    ".cpy":       "ibmi-copybook",
    ".pl":        "prolog",
    ".rs":        "rust",
    ".swift":     "swift",
    ".sql":       "sql",
    ".xml":       "xml",
    ".config":    "xml",
    ".json":      "json",
    ".yaml":      "yaml",
    ".yml":       "yaml",
    ".html":      "html",
    ".htm":       "html",
    ".css":       "css",
    ".scss":      "scss",
    ".bat":       "batch",
    ".ps1":       "powershell",
    ".sh":        "shell",
    ".properties": "properties",
    ".toml":      "toml",
}

# Extensions that contain executable source code
_CODE_EXTS = {".cs", ".vb", ".java", ".kt", ".kts", ".groovy",
              ".py", ".js", ".ts", ".jsx", ".tsx",
              ".php", ".rb", ".go", ".cpp", ".c", ".cbl", ".cob",
              ".f", ".for", ".f90", ".f95", ".pas", ".pp", ".dpr",
              ".pli", ".pl1", ".jcl", ".m", ".nsp", ".nat", ".p",
              ".adb", ".ads", ".ml", ".mli", ".pro", ".pl",
              ".rs", ".swift", ".aspx", ".ascx", ".cshtml", ".vbhtml", ".master",
              ".rpg", ".rpgle", ".sqlrpgle", ".clp", ".clle", ".dds", ".pf",
              ".lf", ".dspf", ".prtf", ".cpy"}

# Patterns that indicate technology stack
_TECH_PATTERNS = {
    "asp_net_webforms": [
        r"<%@ Page", r"<%@ Control", r"<%@ Master", r"System\.Web\.UI",
        r"CodeBehind=", r"CodeFile=", r"MasterPageFile=",
        r"<asp:", r"runat=['\"]server['\"]",
    ],
    "asp_net_mvc": [
        r"System\.Web\.Mvc", r"\[HttpGet\]", r"\[HttpPost\]",
        r"ActionResult", r"ViewBag\.", r"@Html\.",
    ],
    "asp_net_core": [
        r"Microsoft\.AspNetCore", r"IActionResult", r"WebApplication\.Create",
        r"builder\.Services\.", r"app\.MapGet\(",
    ],
    "oracle_db": [
        r"Oracle\.ManagedDataAccess", r"OracleConnection", r"OracleCommand",
        r"Oracle\.DataAccess", r"OracleDbType", r"OracleParameter",
        r"CONNECT.*ORCL", r"Host=.*Port=1521", r"Service=ORCL",
    ],
    "sql_server": [
        r"SqlConnection", r"SqlCommand", r"System\.Data\.SqlClient",
        r"Microsoft\.Data\.SqlClient", r"Data Source=.*Initial Catalog",
    ],
    "entity_framework": [
        r"DbContext", r"DbSet<", r"EntityFramework", r"\.Include\(",
        r"\.FirstOrDefault\(", r"\.ToList\(", r"\.AsQueryable\(",
    ],
    "ado_net_raw": [
        r"OracleDataAdapter", r"SqlDataAdapter", r"DataTable",
        r"DataRow", r"DataSet", r"ExecuteNonQuery|ExecuteReader|ExecuteScalar",
    ],
    "winforms": [r"System\.Windows\.Forms", r"Form1 : Form", r"InitializeComponent"],
    "wpf": [r"System\.Windows", r"<Window ", r"<UserControl ", r"DataContext="],
    # ── Java ecosystem ──────────────────────────────────────────────────────
    "java_standard": [
        r"public\s+(class|interface|enum|record)\s+\w+",
        r"^package\s+[\w\.]+\s*;",
        r"^import\s+java\.",
        r"public\s+static\s+void\s+main\s*\(",
    ],
    "java_modern": [
        r"\brecord\s+\w+\s*\(",
        r"\bsealed\s+(class|interface)\s+",
        r"\bpermits\s+\w+",
        r"instanceof\s+\w+\s+\w+",   # pattern-matching instanceof
        r"List\.of\s*\(",
        r"Map\.of\s*\(",
        r"Optional\.of\s*\(",
        r"switch\s*\([^)]+\)\s*\{[^}]*->",  # switch expressions
    ],
    "java_ee": [r"javax\.servlet", r"@javax", r"HttpServlet", r"ejb\.", r"@EJB",
                r"jakarta\.servlet", r"@jakarta\.ejb"],
    "spring": [
        r"@SpringBootApplication", r"@RestController", r"@Autowired",
        r"@Service\b", r"@Repository\b", r"springframework",
        r"@Component\b", r"@Configuration\b", r"@Bean\b",
        r"@RequestMapping", r"@GetMapping", r"@PostMapping",
        r"SpringApplication\.run",
    ],
    "jpa_hibernate": [
        r"@Entity\b", r"@Table\s*\(", r"@Column\b", r"@Id\b",
        r"jakarta\.persistence", r"javax\.persistence",
        r"JpaRepository", r"CrudRepository", r"EntityManager",
        r"@PersistenceContext", r"hibernate\.cfg", r"SessionFactory",
        r"@ManyToOne", r"@OneToMany", r"@ManyToMany", r"@OneToOne",
    ],
    "jdbc": [
        r"java\.sql\.Connection",
        r"DriverManager\.getConnection",
        r"PreparedStatement",
        r"java\.sql\.ResultSet",
        r"Connection\s+conn\s*=",
        r"jdbc:",
    ],
    "gradle_build": [
        r"apply\s+plugin:",
        r"implementation\s+['\"]com\.",
        r"sourceCompatibility\s*=",
        r"testImplementation\s+['\"]org\.junit",
        r"plugins\s*\{\s*id\s+['\"]java",
        r"compileJava\.",
    ],
    "maven_build": [
        r"<groupId>[\w\.]+</groupId>",
        r"<artifactId>[\w\-\.]+</artifactId>",
        r"<dependencies>",
        r"<build>",
    ],
    "junit": [
        r"@Test\b",
        r"import\s+org\.junit",
        r"import\s+org\.testng",
        r"Assertions\.",
        r"assertEquals\s*\(",
    ],
    "slf4j_logging": [
        r"import\s+org\.slf4j",
        r"LoggerFactory\.getLogger",
        r"import\s+org\.apache\.logging\.log4j",
        r"private\s+static\s+final\s+Logger",
    ],
    "kotlin_lang": [
        r"fun\s+\w+\s*\(",
        r"data\s+class\s+\w+",
        r"val\s+\w+\s*:",
        r"var\s+\w+\s*:",
        r"suspend\s+fun\s+",
        r"companion\s+object",
    ],
    # ── Legacy / Other ──────────────────────────────────────────────────────
    "hibernate": [r"@Entity", r"@Table\(", r"SessionFactory", r"hibernate\.cfg"],
    "jquery": [r"\$\(document\)\.ready", r"\.ajax\(", r"jquery"],
    "react": [r"import React", r"from ['\"]react['\"]", r"useState\(", r"useEffect\("],
    "angular": [r"@Component\(", r"@NgModule", r"from ['\"]@angular"],
    "ibmi_rpg": [
        r"(?im)^\s*\*\*FREE\b", r"(?im)^\s*CTL-OPT\b", r"(?im)^\s*DCL-(?:S|DS|PR|PI|PROC|F)\b",
        r"(?im)^.{5}[HFDCO]", r"(?i)\b(?:CHAIN|SETLL|READE|WRITE|UPDATE|EXFMT)\b",
    ],
    "ibmi_cl": [
        r"(?im)^\s*PGM\b", r"(?i)\bDCL\s+VAR\(", r"(?i)\b(?:CALL|SBMJOB|OVRDBF|MONMSG)\b",
    ],
    "ibmi_dds": [
        r"(?im)^\s*A\s+R\s+\w+", r"(?i)\b(?:PFILE|JFILE|REF|REFFLD|DSPATR|CF\d{2})\b",
    ],
    "db2_for_i": [
        r"(?i)\bEXEC\s+SQL\b", r"(?i)\bSET\s+OPTION\s+COMMIT\b",
        r"(?i)\b(?:RRN|DIGITS|%CHAR)\s*\(", r"(?i)\bQSYS2\.",
    ],
    "fortran_legacy": [
        r"(?im)^\s*(?:PROGRAM|MODULE|SUBROUTINE|FUNCTION)\b",
        r"(?im)^\s*(?:COMMON|EQUIVALENCE|NAMELIST|IMPLICIT)\b",
    ],
    "pascal_delphi": [
        r"(?im)^\s*(?:PROGRAM|UNIT|INTERFACE|IMPLEMENTATION)\b",
        r"(?i)\b(?:TForm|TDataModule|uses\s+SysUtils)\b",
    ],
    "enterprise_pli": [
        r"(?i)\bDCL\s+\d*\s+\w+.*(?:CHAR|FIXED|DECIMAL)\b",
        r"(?i)\b(?:PROC|PROCEDURE)\s+OPTIONS\s*\(",
    ],
    "zos_jcl": [
        r"(?m)^//[\w$#@]+\s+JOB\b", r"(?m)^//[\w$#@]+\s+EXEC\b",
        r"(?m)^//[\w$#@]+\s+DD\b",
    ],
    "mumps": [
        r"(?im)^\s*[A-Za-z%][\w%]*\s+.*\b(?:SET|KILL|NEW|WRITE|READ|GOTO|DO)\b",
        r"(?i)\^[A-Za-z%][\w%]*\s*\(",
    ],
    "software_ag_natural": [
        r"(?im)^\s*DEFINE\s+DATA\b", r"(?im)^\s*(?:FIND|READ|HISTOGRAM)\b",
        r"(?i)\bEND-(?:DEFINE|FIND|READ|TRANSACTION)\b",
    ],
    "openedge_abl": [
        r"(?im)^\s*DEFINE\s+(?:VARIABLE|BUFFER|TEMP-TABLE|QUERY)\b",
        r"(?im)^\s*(?:FOR EACH|FIND FIRST|CREATE|ASSIGN)\b",
    ],
    "ada_language": [
        r"(?im)^\s*(?:PACKAGE|PROCEDURE|FUNCTION)\s+(?:BODY\s+)?[\w.]+",
        r"(?i)\bBEGIN\b[\s\S]*\bEND\s+[\w.]*\s*;",
    ],
    "ocaml_language": [
        r"(?m)^\s*(?:let|module|type)\s+(?:rec\s+)?[\w']+",
        r"(?i)\bmatch\s+.+\s+with\b",
    ],
    "prolog_rules": [
        r"(?m)^\s*[a-z][\w]*\s*\([^)]*\)\s*:-",
        r"(?m)^\s*[a-z][\w]*\s*\([^)]*\)\s*\.",
    ],
}

# SQL patterns specific to Oracle
_ORACLE_SQL_PATTERNS = [
    (r"ROWNUM\s*[<>=]",          "Oracle ROWNUM pagination"),
    (r"SYSDATE",                  "Oracle SYSDATE"),
    (r"NVL\s*\(",                 "Oracle NVL function"),
    (r"DECODE\s*\(",              "Oracle DECODE function"),
    (r"SEQ_\w+\.NEXTVAL",         "Oracle sequence NEXTVAL"),
    (r"FROM\s+DUAL",              "Oracle DUAL table"),
    (r"CONNECT\s+BY",             "Oracle hierarchical query"),
    (r"MERGE\s+INTO",             "Oracle MERGE statement"),
    (r"VARCHAR2\s*\(",            "Oracle VARCHAR2 type"),
    (r"NUMBER\s*\([0-9,]+\)",     "Oracle NUMBER type"),
    (r"CLOB|BLOB|NCLOB",          "Oracle LOB types"),
    (r"EXECUTE\s+IMMEDIATE",      "Oracle dynamic SQL"),
    (r"DBMS_OUTPUT\.",            "Oracle DBMS_OUTPUT package"),
    (r"CREATE\s+OR\s+REPLACE\s+TRIGGER", "Oracle TRIGGER"),
    (r"CREATE\s+OR\s+REPLACE\s+PROCEDURE", "Oracle PROCEDURE"),
]

# Anti-patterns
_ANTIPATTERN_PATTERNS = {
    "hardcoded_password": [
        r"password\s*=\s*['\"][^'\"]{4,}['\"]",
        r"Password\s*=\s*['\"][^'\"]{4,}['\"]",
        r"pwd\s*=\s*['\"][^'\"]{3,}['\"]",
    ],
    "hardcoded_connection_string": [
        r"Host=.*Password=",
        r"Server=.*;.*Password=",
        r"Data Source=.*;.*Password=",
    ],
    "large_method": [],   # detected by LOC heuristic
    "magic_number": [
        r"(?<!\w)[0-9]{4,}(?!\w)",   # numbers > 999 not in comments
    ],
    "sql_concatenation": [
        r"[\"']\s*\+\s*\w",           # string + variable (potential SQL injection)
        r'"\s*SELECT.*"\s*\+',
        r'"UPDATE.*"\s*\+',
        r'"INSERT.*"\s*\+',
        r'"DELETE.*"\s*\+',
    ],
}

# Domain keywords → potential microservice boundaries
_DOMAIN_KEYWORDS = {
    "customer":    ["customer", "client", "person", "user", "account_holder"],
    "account":     ["account", "balance", "ledger"],
    "transaction": ["transaction", "transfer", "payment", "deposit", "withdrawal"],
    "reporting":   ["report", "statement", "export", "audit"],
    "auth":        ["login", "logout", "authenticate", "session", "token", "password"],
    "notification": ["email", "sms", "notification", "alert", "message"],
}


# ─── Public API ───────────────────────────────────────────────────────────────

# Function: analyze_project
def analyze_project(
    folder_path: str,
    on_progress: Optional[Callable[[str, int, str], None]] = None,
    target_stack: str = "aveva_mes",
) -> dict:
    """
    Perform deep analysis of a legacy project folder.
    Returns a structured analysis report dict.
    """

    # Function: progress
    def progress(phase: str, pct: int, msg: str):
        if on_progress:
            on_progress(phase, pct, msg)

    root = Path(folder_path)
    progress("scanning", 2, f"Scanning {root.name}...")

    # ── Step 1: Enumerate files ──────────────────────────────────────────────
    all_files = _enumerate_files(root)
    progress("scanning", 8, f"Found {len(all_files)} files")

    # ── Step 2: Language distribution ────────────────────────────────────────
    progress("languages", 12, "Detecting language distribution...")
    lang_dist = _language_distribution(all_files)

    # ── Step 3: Technology stack detection ───────────────────────────────────
    progress("techstack", 20, "Detecting technology stack...")
    tech_stack = _detect_tech_stack(all_files)

    # ── Step 4: Code metrics ─────────────────────────────────────────────────
    progress("metrics", 30, "Calculating code metrics...")
    metrics = _code_metrics(all_files, root)

    # ── Step 5: Oracle SQL patterns ───────────────────────────────────────────
    progress("database", 40, "Analysing database layer...")
    db_analysis = _database_analysis(all_files)

    # ── Step 6: Anti-patterns ────────────────────────────────────────────────
    progress("quality", 48, "Scanning for anti-patterns...")
    antipatterns = _detect_antipatterns(all_files)

    # ── Step 7: Domain / service boundary inference ──────────────────────────
    progress("domains", 50, "Inferring service boundaries...")
    domains = _infer_domains(all_files)
    # Ensure at least one domain so we always generate something
    if not domains:
        domains = {"core": {
            "file_count": len(all_files),
            "files":      [str(f) for f in all_files[:10]],
            "suggested_service": "CoreService",
        }}

    # ── Step 8: Architecture assessment ─────────────────────────────────────
    architecture = _assess_architecture(tech_stack, metrics, db_analysis, lang_dist)
    progress("architecture", 50, "Architecture assessment complete")

    # ── Step 9: Build source file index for LLM use ─────────────────────────
    source_index = _build_source_index(all_files, root)
    ibmi_analysis = _analyze_ibmi_sources(all_files, root)

    return {
        "folder_path":   folder_path,
        "analysed_at":   datetime.now(timezone.utc).isoformat(),
        "file_count":    len(all_files),
        "languages":     lang_dist,
        "tech_stack":    tech_stack,
        "metrics":       metrics,
        "database":      db_analysis,
        "antipatterns":  antipatterns,
        "domains":       domains,
        "architecture":  architecture,
        "source_index":  source_index,
        "ibmi":          ibmi_analysis,
        "modernization_targets": _build_targets(tech_stack, db_analysis, architecture, target_stack),
    }


# Function: _analyze_ibmi_sources
def _analyze_ibmi_sources(files: List[Path], root: Path) -> dict:
    """Extract IBM i program, file, copybook and job-control dependencies."""
    ibmi_exts = {".rpg", ".rpgle", ".sqlrpgle", ".clp", ".clle", ".dds",
                 ".pf", ".lf", ".dspf", ".prtf", ".cpy"}
    inventory = []
    calls, files_used, copybooks, indicators = set(), set(), set(), set()
    for path in files:
        ext = path.suffix.casefold()
        if ext not in ibmi_exts:
            continue
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        rel = path.relative_to(root).as_posix()
        procedures = re.findall(r"(?im)^\s*dcl-proc\s+([\w#$@]+)", content)
        procedures += re.findall(r"(?im)^\s*([\w#$@]+)\s+begsr\b", content)
        program_calls = re.findall(
            r"(?i)\b(?:CALLP?\s*\(?|CALL\s+PGM\s*\(|SBMJOB.*?PGM\s*\()['\"]?([\w#$@/]+)",
            content,
        )
        calls.update(value.upper() for value in program_calls)
        declared_files = re.findall(r"(?im)^\s*dcl-f\s+([\w#$@]+)", content)
        declared_files += re.findall(r"(?im)^.{5}F([\w#$@]+)", content)
        files_used.update(value.upper() for value in declared_files)
        includes = re.findall(r"(?im)^\s*/(?:COPY|INCLUDE)\s+([^\s]+)", content)
        copybooks.update(value.upper() for value in includes)
        indicators.update(value.upper() for value in re.findall(r"(?i)\*IN(?:\(\s*)?(\d{2}|LR|RT)", content))
        inventory.append({
            "path": rel,
            "kind": _LANG_MAP.get(ext, "ibmi"),
            "procedures": list(dict.fromkeys(procedures)),
            "calls": list(dict.fromkeys(program_calls)),
            "files": list(dict.fromkeys(declared_files)),
            "copybooks": list(dict.fromkeys(includes)),
        })
    return {
        "detected": bool(inventory),
        "source_files": len(inventory),
        "inventory": inventory,
        "program_calls": sorted(calls),
        "database_and_device_files": sorted(files_used),
        "copybooks": sorted(copybooks),
        "indicators": sorted(indicators),
    }


# ─── Internal helpers ─────────────────────────────────────────────────────────

# Function: _enumerate_files
def _enumerate_files(root: Path) -> List[Path]:
    skip_dirs = {".git", ".vs", ".vscode", "bin", "obj", "node_modules",
                 "__pycache__", ".venv", "venv", "env", "dist", "build",
                 "target", "out", "packages", ".nuget", "TestResults",
                 ".gradle", ".idea", "coverage", ".next", ".nuxt",
                 ".mvn", ".svn", ".hg"}
    files = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in skip_dirs]
        for fname in filenames:
            files.append(Path(dirpath) / fname)
    return files


# Function: _language_distribution
def _language_distribution(files: List[Path]) -> Dict[str, dict]:
    dist: Dict[str, dict] = defaultdict(lambda: {"files": 0, "lines": 0})
    for f in files:
        lang = _LANG_MAP.get(f.suffix.lower())
        if not lang:
            continue
        dist[lang]["files"] += 1
        try:
            text = f.read_text(encoding="utf-8", errors="ignore")
            dist[lang]["lines"] += text.count("\n") + 1
        except OSError:
            pass
    return dict(dist)


# Function: _detect_tech_stack
# Function: _read_cached
def _read_cached(p: Path, text_cache: Dict[Path, str]) -> str:
    if p not in text_cache:
        try:
            text_cache[p] = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            text_cache[p] = ""
    return text_cache[p]


# Function: _find_tech_matches
def _find_tech_matches(files: List[Path], patterns: List[str], text_cache: Dict[Path, str]) -> list:
    matches = []
    for p in files:
        content = _read_cached(p, text_cache)
        for pattern in patterns:
            if re.search(pattern, content, re.IGNORECASE | re.MULTILINE):
                rel_path = str(p)
                if rel_path not in matches:
                    matches.append(rel_path)
                break
    return matches


# Function: _detect_tech_stack
def _detect_tech_stack(files: List[Path]) -> Dict[str, dict]:
    text_cache: Dict[Path, str] = {}
    detected: Dict[str, dict] = {}

    for tech, patterns in _TECH_PATTERNS.items():
        matches = _find_tech_matches(files, patterns, text_cache)
        if matches:
            detected[tech] = {
                "detected":    True,
                "file_count":  len(matches),
                "sample_files": matches[:5],
            }

    return detected


# ─── Code metric regex patterns (compiled once) ──────────────────────────────
_CS_CLASS_RE     = re.compile(r"^\s*(public|private|protected|internal)?\s*(class|interface|enum)\s+(\w+)", re.M)
_CS_METHOD_RE    = re.compile(r"^\s*(public|private|protected|internal|static|virtual|override|async)[\w\s<>, \[\]]+\s+(\w+)\s*\(", re.M)
_NS_RE           = re.compile(r"namespace\s+([\w\.]+)", re.M)
_JAVA_CLASS_RE   = re.compile(r"^\s*(?:public|protected|private)?\s*(?:abstract\s+|final\s+|static\s+)*(?:class|interface|enum|record)\s+(\w+)", re.M)
_JAVA_METHOD_RE  = re.compile(r"^\s*(?:public|protected|private|static|final|synchronized|default)[\w\s<>,@\[\]]+\s+(\w+)\s*\([^)]*\)\s*(?:throws\s+[\w,\s]+)?\s*(?:\{|;)", re.M)
_JAVA_PACKAGE_RE = re.compile(r"^package\s+([\w\.]+)\s*;", re.M)
_KOTLIN_FUN_RE   = re.compile(r"^\s*(?:suspend\s+)?fun\s+(\w+)\s*\(", re.M)
_KOTLIN_CLASS_RE = re.compile(r"^\s*(?:data\s+|sealed\s+|open\s+|abstract\s+)?(?:class|interface|object)\s+(\w+)", re.M)
_KOTLIN_PKG_RE   = re.compile(r"^package\s+([\w\.]+)", re.M)


# Function: _count_file_code_symbols
def _count_file_code_symbols(content: str, ext: str, namespaces: set) -> tuple:
    classes = methods = 0
    if ext == ".cs":
        classes = len(_CS_CLASS_RE.findall(content))
        methods = len(_CS_METHOD_RE.findall(content))
        for m in _NS_RE.finditer(content):
            namespaces.add(m.group(1))
    elif ext == ".java":
        classes = len(_JAVA_CLASS_RE.findall(content))
        methods = len(_JAVA_METHOD_RE.findall(content))
        for m in _JAVA_PACKAGE_RE.finditer(content):
            namespaces.add(m.group(1))
    elif ext in (".kt", ".kts"):
        classes = len(_KOTLIN_CLASS_RE.findall(content))
        methods = len(_KOTLIN_FUN_RE.findall(content))
        for m in _KOTLIN_PKG_RE.finditer(content):
            namespaces.add(m.group(1))
    return classes, methods


# Function: _code_metrics
def _code_metrics(files: List[Path], root: Path) -> dict:
    total_loc    = 0
    total_blank  = 0
    total_comment = 0
    class_count  = 0
    method_count = 0
    max_file_loc = 0
    large_files  = []
    namespaces: set = set()

    for f in files:
        if f.suffix.lower() not in _CODE_EXTS:
            continue
        try:
            content = f.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue

        lines   = content.splitlines()
        loc     = len(lines)
        blank   = sum(1 for l in lines if not l.strip())
        comment = sum(1 for l in lines if l.strip().startswith(("//", "#", "<!--", "/*", "*", "'")))

        total_loc     += loc
        total_blank   += blank
        total_comment += comment
        max_file_loc   = max(max_file_loc, loc)

        if loc > 300:
            large_files.append({"file": str(f), "loc": loc})

        cls, mth = _count_file_code_symbols(content, f.suffix.lower(), namespaces)
        class_count  += cls
        method_count += mth

    return {
        "total_loc":          total_loc,
        "total_blank_lines":  total_blank,
        "total_comment_lines": total_comment,
        "comment_ratio":      round(total_comment / max(total_loc, 1), 3),
        "max_file_loc":       max_file_loc,
        "class_count":        class_count,
        "method_count":       method_count,
        "namespaces":         sorted(namespaces),
        "large_files":        sorted(large_files, key=lambda x: -x["loc"])[:10],
    }


# Function: _database_analysis
# Function: _scan_file_for_db_patterns
def _scan_file_for_db_patterns(f: Path, content: str, table_re, jpa_table_re, jpa_entity_re, jdbc_url_re,
                                oracle_patterns_found: list, table_names: set, connection_strings: list) -> int:
    """Scan one file's content for DB-related patterns, mutating the shared
    collections in place. Returns 1 if the file contains raw-SQL execution
    calls, else 0 (caller accumulates into raw_sql_count)."""
    for pattern, label in _ORACLE_SQL_PATTERNS:
        if re.search(pattern, content, re.IGNORECASE):
            if label not in oracle_patterns_found:
                oracle_patterns_found.append(label)

    for m in table_re.finditer(content):
        table_names.add((m.group(1) or "").rstrip(".") + m.group(2).upper())

    # Extract JPA-annotated table names
    for m in jpa_table_re.finditer(content):
        table_names.add(m.group(1).upper())
    for m in jpa_entity_re.finditer(content):
        # Convert CamelCase to UPPER_SNAKE for default JPA table name
        entity = m.group(1)
        snake = re.sub(r"(?<!^)(?=[A-Z])", "_", entity).upper()
        table_names.add(snake)

    is_raw_sql = bool(re.search(
        r"ExecuteReader|ExecuteNonQuery|ExecuteScalar|OracleCommand"
        r"|prepareStatement|createQuery|createNativeQuery", content,
    ))

    # C#/.NET connection strings
    for m in re.finditer(r"connectionString['\"\s]*=\s*['\"]([^'\"]+)['\"]", content, re.I):
        cs = m.group(1)
        if len(cs) > 10:
            connection_strings.append({"file": str(f), "value": cs[:80] + "..."})

    # Java JDBC URLs (spring.datasource.url=jdbc:...)
    for m in jdbc_url_re.finditer(content):
        cs = m.group(0)
        connection_strings.append({"file": str(f), "value": cs[:80]})

    return 1 if is_raw_sql else 0


# Function: _database_analysis
def _database_analysis(files: List[Path]) -> dict:
    oracle_patterns_found = []
    connection_strings    = []
    table_names: set      = set()
    raw_sql_count         = 0

    table_re = re.compile(
        r"(?:FROM|INTO|UPDATE|JOIN)\s+([A-Z_]+\.)?([A-Z][A-Z0-9_]{2,})",
        re.IGNORECASE,
    )
    # JPA: @Table(name="foo")  or  @Table("foo")
    jpa_table_re  = re.compile(r'@Table\s*\(\s*(?:name\s*=\s*)?["\']([^"\']+)["\']', re.IGNORECASE)
    # JPA: @Entity ... class FooBar → table might be "foo_bar"
    jpa_entity_re = re.compile(r'@Entity\b.{0,200}?(?:class|record)\s+(\w+)', re.DOTALL | re.IGNORECASE)
    # Hibernate: @Table without name parameter — class name is table
    # JDBC URL pattern
    jdbc_url_re   = re.compile(r'jdbc:(\w+)://[^\s"\']+', re.IGNORECASE)

    for f in files:
        if f.suffix.lower() not in _CODE_EXTS | {".sql", ".config", ".xml", ".properties", ".yml", ".yaml"}:
            continue
        try:
            content = f.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue

        raw_sql_count += _scan_file_for_db_patterns(
            f, content, table_re, jpa_table_re, jpa_entity_re, jdbc_url_re,
            oracle_patterns_found, table_names, connection_strings,
        )

    # Remove generic SQL keywords that aren't real table names
    _sql_noise = {"SELECT", "WHERE", "FROM", "JOIN", "INTO", "UPDATE", "TABLE",
                  "INDEX", "VIEW", "DATABASE", "SCHEMA", "SET", "VALUES",
                  "NULL", "NOT", "AND", "OR", "AS", "ON", "BY", "DESC", "ASC"}
    table_names -= _sql_noise

    return {
        "oracle_patterns":    oracle_patterns_found,
        "table_names":        sorted(t for t in table_names if len(t) >= 3),
        "raw_sql_files":      raw_sql_count,
        "connection_strings": connection_strings[:5],
        "orm_detected":       False,  # enriched by tech_stack check
    }


# Function: _detect_antipatterns
def _detect_antipatterns(files: List[Path]) -> List[dict]:
    issues = []
    for f in files:
        if f.suffix.lower() not in _CODE_EXTS:
            continue
        try:
            content = f.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue

        for atype, patterns in _ANTIPATTERN_PATTERNS.items():
            for pattern in patterns:
                for m in re.finditer(pattern, content, re.IGNORECASE):
                    issues.append({
                        "type": atype,
                        "file": str(f),
                        "line": content[:m.start()].count("\n") + 1,
                        "snippet": m.group(0)[:80],
                    })
                    break  # one instance per file per type

    return issues[:50]  # cap to avoid huge responses


# Function: _infer_from_java_packages
def _infer_from_java_packages(java_files: List[Path], domains: Dict[str, dict]) -> None:
    package_re = re.compile(r"^package\s+([\w\.]+)\s*;", re.M)
    pkg_classes: Dict[str, List[str]] = defaultdict(list)
    for f in java_files:
        try:
            txt = f.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for m in package_re.finditer(txt):
            parts = m.group(1).split(".")
            skip_set = {"com", "org", "net", "io", "edu", "gov", "co",
                        "main", "test", "util", "utils", "common",
                        "base", "core", "model", "dto", "entity", "config"}
            meaningful = [p for p in parts if p not in skip_set and len(p) > 2]
            if meaningful:
                domain_key = meaningful[0].lower()
                pkg_classes[domain_key].append(str(f))
    for pkg_domain, pkg_files in pkg_classes.items():
        if pkg_domain not in domains:
            domains[pkg_domain] = {
                "file_count": len(pkg_files),
                "files":      pkg_files[:10],
                "suggested_service": f"{pkg_domain.capitalize()}Service",
            }


# Function: _infer_from_dir_structure
# Function: _collect_src_roots
def _collect_src_roots(files: List[Path]) -> list:
    src_roots = []
    for f in files:
        parts = f.parts
        for i, part in enumerate(parts):
            if part in ("src", "source", "sources", "main", "examples",
                        "jep-examples", "app", "modules"):
                candidate = Path(*parts[:i+2]) if i + 1 < len(parts) else None
                if candidate:
                    src_roots.append(candidate.name)
    return src_roots


# Function: _register_dir_domain
def _register_dir_domain(sroot: str, files: List[Path], domains: Dict[str, dict]) -> None:
    sroot_lower = sroot.lower().replace("-", "_").replace(" ", "_")
    if sroot_lower in ("src", "main", "test", "java", "kotlin", "resources", "webapp", "META-INF"):
        return
    if sroot_lower in domains:
        return
    related = [str(f) for f in files if sroot in str(f)][:10]
    if not related:
        return
    domains[sroot_lower] = {
        "file_count": len(related),
        "files":      related,
        "suggested_service": f"{sroot_lower.capitalize()}Service",
    }


# Function: _infer_from_dir_structure
def _infer_from_dir_structure(files: List[Path], domains: Dict[str, dict]) -> None:
    src_roots = _collect_src_roots(files)
    for sroot in set(src_roots):
        _register_dir_domain(sroot, files, domains)


# Function: _infer_domains
def _infer_domains(files: List[Path]) -> Dict[str, dict]:
    domains: Dict[str, dict] = {}

    # 1. Keyword-based detection (file name matching)
    for domain, keywords in _DOMAIN_KEYWORDS.items():
        matched_files = []
        for f in files:
            name_lower = f.stem.lower()
            if any(kw in name_lower for kw in keywords):
                matched_files.append(str(f))
        if matched_files:
            domains[domain] = {
                "file_count": len(matched_files),
                "files":      matched_files[:10],
                "suggested_service": f"{domain.capitalize()}Service",
            }

    # 2. Java/Kotlin package-based domain inference
    java_files = [f for f in files if f.suffix.lower() in (".java", ".kt", ".kts")]
    if java_files:
        _infer_from_java_packages(java_files, domains)

    # 3. Directory structure fallback
    if not domains:
        _infer_from_dir_structure(files, domains)

    return domains


# Function: _build_source_index
def _build_source_index(files: List[Path], root: Path) -> Dict[str, str]:
    """
    Build a lightweight index of source file paths → first 120 chars of content.
    Used by the modernizer to know what source files exist without loading all content.
    Returns at most 200 entries.
    """
    index: Dict[str, str] = {}
    for f in files:
        if f.suffix.lower() not in _CODE_EXTS:
            continue
        try:
            rel = str(f.relative_to(root))
        except ValueError:
            rel = f.name
        try:
            preview = f.read_text(encoding="utf-8", errors="ignore")[:120].replace("\n", " ")
        except OSError:
            preview = ""
        index[rel] = preview
        if len(index) >= 200:
            break
    return index


# Function: _detect_arch_pattern
def _detect_arch_pattern(detected_techs: list, lang_dist: dict) -> tuple:
    if "ibmi_rpg" in detected_techs or "ibmi_cl" in detected_techs:
        return "IBM i / AS400 RPG application", "RPG III/IV through current IBM i"
    if "asp_net_webforms" in detected_techs:
        return "ASP.NET WebForms (Monolith)", "2003-2012"
    if "asp_net_mvc" in detected_techs:
        return "ASP.NET MVC (Monolith)", "2009-2016"
    if "asp_net_core" in detected_techs:
        return "ASP.NET Core (Microservices / API)", "2016-present"
    if "spring" in detected_techs:
        return "Spring Boot Application", "2014-present"
    if "java_ee" in detected_techs:
        return "Java EE / Jakarta EE (Monolith)", "1999-2020"
    if "java_modern" in detected_techs:
        return "Modern Java Application (Java 17+)", "2021-present"
    if "java_standard" in detected_techs or "java" in lang_dist:
        return "Java Standard Application", "2000-present"
    if "kotlin_lang" in detected_techs:
        return "Kotlin Application", "2017-present"
    return "Unknown / Custom", "Unknown"


# Function: _detect_db_tech
def _detect_db_tech(detected_techs: list) -> str:
    if "db2_for_i" in detected_techs or "ibmi_dds" in detected_techs:
        return "Db2 for i / DDS"
    if "oracle_db" in detected_techs:
        return "Oracle"
    if "sql_server" in detected_techs:
        return "SQL Server"
    if "jpa_hibernate" in detected_techs or "hibernate" in detected_techs:
        return "Relational DB via JPA/Hibernate"
    if "jdbc" in detected_techs:
        return "Relational DB via JDBC"
    if "entity_framework" in detected_techs:
        return "SQL Server via EF Core"
    return "Unknown"


# Function: _assess_architecture
def _assess_architecture(
    tech_stack: dict,
    metrics: dict,
    db_analysis: dict,
    lang_dist: dict,
) -> dict:
    detected_techs = list(tech_stack.keys())
    pattern, era = _detect_arch_pattern(detected_techs, lang_dist)
    db_tech = _detect_db_tech(detected_techs)

    build_system = ""
    if "gradle_build" in detected_techs:
        build_system = "Gradle"
    elif "maven_build" in detected_techs:
        build_system = "Maven"

    complexity = "high" if metrics["total_loc"] > 20000 else \
                 "medium" if metrics["total_loc"] > 5000 else "low"

    return {
        "pattern":          pattern,
        "era":              era,
        "database":         db_tech,
        "complexity":       complexity,
        "total_loc":        metrics["total_loc"],
        "detected_techs":   detected_techs,
        "tier_count":       _guess_tiers(tech_stack, lang_dist),
        "build_system":     build_system,
    }


# Function: _guess_tiers
def _guess_tiers(tech_stack: dict, lang_dist: dict) -> int:
    tiers = 1
    has_frontend = any(t in tech_stack for t in ["jquery", "react", "angular"])
    has_backend  = any(t in tech_stack for t in ["asp_net_webforms", "asp_net_mvc",
                                                  "asp_net_core", "spring", "java_ee",
                                                  "java_standard", "kotlin_lang"])
    has_db       = any(t in tech_stack for t in ["oracle_db", "sql_server",
                                                  "entity_framework", "ado_net_raw",
                                                  "jdbc", "jpa_hibernate", "hibernate"])
    if has_frontend: tiers += 1
    if has_backend:  tiers += 1
    if has_db:       tiers += 1
    return max(tiers, 1)


# Function: _build_targets
def _build_targets(tech_stack: dict, db_analysis: dict, architecture: dict, target_stack: str = "aveva_mes") -> dict:
    try:
        from services.modernizer import TARGET_STACKS
        stack = TARGET_STACKS.get(target_stack, TARGET_STACKS["aveva_mes"])
    except Exception:
        stack = {
            "frontend_tech": "JavaScript modules (MES UI architecture)",
            "backend_tech":  ".NET 8 Minimal API (MES architecture)",
            "db_tech":       "Microsoft SQL Server 2022 + EF Core 8",
            "db_target":     "mssql",
        }

    db_target = stack.get("db_target", "mssql")
    to_db_label = {
        "mssql":   "MS SQL Server",
        "postgres": "PostgreSQL",
        "mongodb": "MongoDB",
    }.get(db_target, db_target.upper())

    return {
        "frontend": stack.get("frontend_tech", "(see stack)"),
        "backend":  stack.get("backend_tech",  "(see stack)"),
        "database": stack.get("db_tech",        "(see stack)"),
        "migration": {
            "from_db":      architecture.get("database", "Unknown"),
            "to_db":        to_db_label,
            "tables_found": db_analysis.get("table_names", []),
            "oracle_constructs_to_migrate": db_analysis.get("oracle_patterns", []),
        },
    }
