# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Configuration and settings for CodeAnalysis platform.
# Date: 2026-01-25
# ---------------------------------------------------------------------------
"""
Configuration and settings for CodeAnalysis platform.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ─── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR   = Path(__file__).resolve().parent.parent
CLONE_DIR  = BASE_DIR / "cloned_repos"
REPORT_DIR = BASE_DIR / "output_reports"
TEMPLATE_DIR = BASE_DIR / "reports" / "templates"
UPLOAD_DIR = BASE_DIR / "uploaded_repos"

CLONE_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# ─── Local-folder upload limits (analyse-from-zip) ───────────────────────────
# The browser can't send an arbitrary folder directly, so the frontend zips it
# client-side and uploads the archive. These caps bound both plain large
# uploads and zip-bomb-style abuse (a tiny archive that decompresses to a huge
# size/file count) before any extraction work is done.
MAX_UPLOAD_ZIP_BYTES       = 300 * 1024 * 1024   # 300 MB compressed upload
MAX_UPLOAD_EXTRACTED_BYTES = 1024 * 1024 * 1024  # 1 GB decompressed
MAX_UPLOAD_FILE_COUNT      = 20_000              # generous headroom over the analyzer's own 15k file cap

# ─── GitHub ───────────────────────────────────────────────────────────────────
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

# ─── Language Support ─────────────────────────────────────────────────────────
LANGUAGE_EXTENSIONS = {
    # ── Legacy / Enterprise ──────────────────────────────────────────────────
    "java":        {".java"},
    "dotnet":      {".cs", ".vb", ".fs", ".csproj", ".vbproj", ".sln"},
    "python":      {".py"},
    "javascript":  {".js", ".ts", ".jsx", ".tsx", ".mjs", ".cjs"},
    "mainframe":   {".cbl", ".cob", ".CBL", ".COB", ".jcl", ".JCL",
                    ".asm", ".ASM", ".pli", ".PLI", ".rexx", ".REXX",
                    ".csp",                    # IBM Cross System Product
                    ".pnv", ".panvalet"},       # PANVALET source library

    # ── Enterprise Java / Web ─────────────────────────────────────────────────
    "jsp":         {".jsp", ".jspx", ".jspf", ".tag", ".tagx"},
    "was":         {".xml", ".java", ".properties"},   # IBM WAS/Liberty descriptors + Java

    # ── Database / SQL (all flavours) ────────────────────────────────────────
    "sql":         {".sql", ".ddl", ".dml", ".psql", ".pgsql", ".hql",
                    ".tsql", ".plsql", ".pls", ".prc", ".fnc", ".trg",
                    ".pkb", ".pks"},          # Oracle PL/SQL package body/spec
    "db2":         {".db2", ".dclgen", ".sqc", ".sqb", ".sqlj", ".bnd"},

    # ── Modern backend languages ─────────────────────────────────────────────
    "go":          {".go"},
    "rust":        {".rs"},
    "kotlin":      {".kt", ".kts"},
    "scala":       {".scala", ".sc"},
    "ruby":        {".rb", ".rake", ".gemspec", ".ru"},
    "php":         {".php", ".phtml", ".php3", ".php4", ".php5", ".php7"},

    # ── Systems programming ──────────────────────────────────────────────────
    "cpp":         {".c", ".cpp", ".cc", ".cxx", ".h", ".hpp", ".hxx",
                    ".c++", ".h++"},

    # ── Scripting / DevOps ───────────────────────────────────────────────────
    "shell":       {".sh", ".bash", ".zsh", ".ksh", ".fish", ".csh",
                    ".tcsh", ".bats"},        # .bats = Bash test files

    # ── Data / Analytics ─────────────────────────────────────────────────────
    "r":           {".r", ".R", ".Rmd", ".Rmarkdown"},
    "dart":        {".dart"},

    # ── JVM extras ───────────────────────────────────────────────────────────
    "groovy":      {".groovy", ".gvy", ".gradle", ".jenkinsfile"},
}

# ─── Metric Weights ───────────────────────────────────────────────────────────
# Software Health sub-scores (must sum to 1.0)
HEALTH_WEIGHTS = {
    "resiliency": 0.40,
    "agility":    0.35,
    "elegance":   0.25,
}

# Technical Debt – COCOMO II constants
COCOMO_A         = 2.94   # effort multiplier
COCOMO_B         = 0.91   # scale factor exponent
AVG_SALARY_MONTH = 8_000  # USD per FTE per month for cost estimation
WORK_HOURS_MONTH = 152    # billable hours per month

# Cloud Maturity – scoring criteria weights
CLOUD_WEIGHTS = {
    "stateless_design":      0.20,
    "containerization":      0.20,
    "api_surface":           0.15,
    "config_externalization": 0.15,
    "logging_observability": 0.15,
    "ci_cd_artifacts":       0.15,
}

# ─── Thresholds for risk classification ───────────────────────────────────────
RISK_THRESHOLDS = {
    "health_critical": 40,
    "health_poor":     60,
    "health_fair":     75,
    "health_good":     90,
    "debt_critical_months": 24,
    "cloud_low":  40,
    "cloud_mid":  70,
}

# ─── Open-Source Safety ───────────────────────────────────────────────────────
MAX_DEPENDENCY_AGE_YEARS = 3     # flag if no update in N years
ALLOWED_LICENSES = {
    "MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause",
    "ISC", "LGPL-2.1", "MPL-2.0", "0BSD",
}

# ─── Business Impact defaults ─────────────────────────────────────────────────
DEFAULT_USERS        = 100
DEFAULT_RELEASE_FREQ = 12   # releases per year
DEFAULT_REVENUE_IMPACT = 0  # USD per year
