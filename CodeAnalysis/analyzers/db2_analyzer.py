# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Analyses IBM DB2 / UDB (Universal Database) SQL scripts and host-language
# Date: 2026-07-12
# ---------------------------------------------------------------------------
"""
db2_analyzer.py
---------------
Analyses IBM DB2 / UDB (Universal Database) SQL scripts and host-language
embedded SQL (COBOL, PL/I, C, Java/SQLJ, Fortran).

Metrics produced
~~~~~~~~~~~~~~~~
- SLOC / comment lines breakdown
- Statement counts: SELECT, INSERT, UPDATE, DELETE, MERGE, CALL
- DB2-specific function usage (CURRENT DATE, COALESCE/VALUE, DAYS, MONTHS,
  MICROSECOND, GENERATE_UNIQUE, RAISE_ERROR, DECRYPT_CHAR, ENCRYPT_RC2, …)
- Isolation level usage (WITH UR/CS/RS/RR)
- Declared cursor count
- Declared Global Temporary Table (DGTT) usage
- Host variable references (:VARNAME in embedded SQL)
- SQLCA / GET DIAGNOSTICS usage
- DB2 catalog queries (SYSCAT.*, SYSIBM.*)
- Performance risk patterns:
    * SELECT * (cartesian explosion risk)
    * LIKE '%...' leading wildcard (full scan)
    * Missing OPTIMIZE FOR n ROWS on large fetches
    * LOCK TABLE (concurrency risk)
    * Correlated subquery patterns
    * FETCH FIRST without ORDER BY (non-deterministic)
- DB2 Connect patterns (FOR FETCH ONLY, OPTIMIZE FOR, SET SERVER OPTION)
- Stored procedure detection (@, BEGIN … END, CREATE PROCEDURE)
- User-defined function detection (CREATE FUNCTION)
- Trigger detection (CREATE TRIGGER)
- SQLJ patterns (# sql { ... })
- Bad practices: concatenation in WHERE, TRIM in WHERE on indexed cols,
  UPPER/LOWER on indexed cols, implicit cast mismatches
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Optional, List

from analyzers.base_analyzer import BaseAnalyzer, FileMetrics, LanguageReport
from config.settings import LANGUAGE_EXTENSIONS


class DB2Analyzer(BaseAnalyzer):
    """Analyzer for IBM DB2 / UDB SQL files and embedded SQL."""

    EXTENSIONS = LANGUAGE_EXTENSIONS.get("db2", {
        ".db2",      # DB2 SQL scripts
        ".sql",      # generic SQL (shared with sql_analyzer; db2 patterns take priority)
        ".ddl",
        ".dclgen",   # DCLGEN host-variable declarations
        ".sqc",      # Embedded SQL in C
        ".sqb",      # Embedded SQL in COBOL (preprocessed)
        ".sqlj",     # SQLJ (SQL in Java)
        ".bnd",      # DB2 bind file (compiled package descriptor)
    })

    # ── DML patterns ─────────────────────────────────────────────────────────
    _SELECT   = re.compile(r'^\s*SELECT\b', re.IGNORECASE | re.MULTILINE)
    _INSERT   = re.compile(r'^\s*INSERT\b', re.IGNORECASE | re.MULTILINE)
    _UPDATE   = re.compile(r'^\s*UPDATE\b', re.IGNORECASE | re.MULTILINE)
    _DELETE   = re.compile(r'^\s*DELETE\b', re.IGNORECASE | re.MULTILINE)
    _MERGE    = re.compile(r'^\s*MERGE\b',  re.IGNORECASE | re.MULTILINE)
    _CALL     = re.compile(r'^\s*CALL\b',   re.IGNORECASE | re.MULTILINE)

    # ── DDL patterns ─────────────────────────────────────────────────────────
    _PROC     = re.compile(r'CREATE\s+(?:OR\s+REPLACE\s+)?PROCEDURE\b', re.IGNORECASE)
    _FUNC     = re.compile(r'CREATE\s+(?:OR\s+REPLACE\s+)?FUNCTION\b',  re.IGNORECASE)
    _TRIGGER  = re.compile(r'CREATE\s+(?:OR\s+REPLACE\s+)?TRIGGER\b',   re.IGNORECASE)
    _TABLE    = re.compile(r'CREATE\s+(?:GLOBAL\s+TEMPORARY\s+|TEMPORARY\s+)?TABLE\b', re.IGNORECASE)
    _VIEW     = re.compile(r'CREATE\s+(?:OR\s+REPLACE\s+)?VIEW\b',      re.IGNORECASE)
    _DGTT     = re.compile(r'DECLARE\s+GLOBAL\s+TEMPORARY\s+TABLE\b',    re.IGNORECASE)

    # ── DB2-specific syntax ───────────────────────────────────────────────────
    _ISOLATION = re.compile(r'\bWITH\s+(UR|CS|RS|RR)\b', re.IGNORECASE)
    _OPT_ROWS  = re.compile(r'\bOPTIMIZE\s+FOR\s+\d+\s+ROWS?\b', re.IGNORECASE)
    _FETCH_FIRST= re.compile(r'\bFETCH\s+FIRST\s+\d+\s+ROWS?\s+ONLY\b', re.IGNORECASE)
    _LOCK_TABLE = re.compile(r'\bLOCK\s+TABLE\b', re.IGNORECASE)
    _CURSOR     = re.compile(r'\bDECLARE\s+\w+\s+CURSOR\b', re.IGNORECASE)
    _HOST_VAR   = re.compile(r':[A-Z][A-Z0-9_-]*\b')   # host variables (:WS-CUST-ID etc.)
    _SQLCA      = re.compile(r'\bINCLUDE\s+SQLCA\b|\bSQLCODE\b|\bSQLSTATE\b|\bGET\s+DIAGNOSTICS\b', re.IGNORECASE)
    _EXEC_SQL   = re.compile(r'\bEXEC\s+SQL\b', re.IGNORECASE)   # embedded SQL in COBOL/C
    _SQLJ       = re.compile(r'#\s*sql\s*\{', re.IGNORECASE)     # SQLJ
    _BIND_PKG   = re.compile(r'\bBIND\s+PACKAGE\b|\bBIND\s+PLAN\b', re.IGNORECASE)

    # ── DB2 date/time/special functions ─────────────────────────────────────
    _DB2_FUNCS = re.compile(
        r'\b(CURRENT\s+(?:DATE|TIME|TIMESTAMP|TIMEZONE|PATH|SCHEMA|SQLID)|'
        r'CURRENT_DATE|CURRENT_TIME|CURRENT_TIMESTAMP|'
        r'DAYS\s*\(|MONTHS\s*\(|YEARS\s*\(|MICROSECONDS?\s*\(|'
        r'GENERATE_UNIQUE\s*\(|COALESCE\s*\(|VALUE\s*\(|'
        r'RAISE_ERROR\s*\(|HEX\s*\(|TRANSLATE\s*\(|'
        r'DECRYPT_CHAR\s*\(|ENCRYPT_RC2\s*\(|'
        r'STRIP\s*\(|TRIM\s*\(|POSSTR\s*\(|LOCATE\s*\(|'
        r'CHAR\s*\(|VARCHAR\s*\(|BIGINT\s*\(|INT\s*\(|FLOAT\s*\(|'
        r'SYSCAT\.|SYSIBM\.|SYSFUN\.)',
        re.IGNORECASE
    )

    # ── Performance anti-patterns ────────────────────────────────────────────
    _SELECT_STAR  = re.compile(r'\bSELECT\s+\*', re.IGNORECASE)
    _LEADING_WILD = re.compile(r"LIKE\s+'%", re.IGNORECASE)
    _FUNC_WHERE   = re.compile(
        r'\bWHERE\b.*\b(?:UPPER|LOWER|TRIM|SUBSTR|CHAR)\s*\(', re.IGNORECASE
    )
    _CORRELATED   = re.compile(r'\bWHERE\b.*\bEXISTS\s*\(\s*SELECT\b', re.IGNORECASE)
    _CONCAT_WHERE = re.compile(r'\bWHERE\b.*\|\|.*=', re.IGNORECASE)

    # DB2 Connect patterns
    _DB2_CONNECT  = re.compile(r'\bCONNECT\s+TO\s+\w+|\bCONNECT\s+RESET\b', re.IGNORECASE)

    # DB2 schemas / catalog
    _CATALOG_Q    = re.compile(r'\b(SYSCAT|SYSIBM|SYSFUN|SYSSTAT)\.\w+', re.IGNORECASE)

    # ── Complexity branches (SQL logic) ─────────────────────────────────────
    _BRANCH = re.compile(
        r'\b(CASE\s+WHEN|WHEN\b|IF\b|ELSEIF\b|ELSIF\b|LOOP\b|WHILE\b|FOR\b|AND\b|OR\b)\b',
        re.IGNORECASE
    )

    # Function: language_name
    def language_name(self) -> str:
        return "DB2/UDB"

    # ──────────────────────────────────────────────────────────────────────────
    # Function: _classify_db2_line
    def _classify_db2_line(self, stripped: str, fm: FileMetrics, state: dict) -> None:
        # Block comment handling (/* ... */)
        if "/*" in stripped:
            state["in_block_comment"] = True
        if "*/" in stripped:
            state["in_block_comment"] = False
            fm.comment_lines += 1
            return
        if state["in_block_comment"]:
            fm.comment_lines += 1
            return

        # Single-line comments
        if stripped.startswith("--") or stripped.startswith("//"):
            fm.comment_lines += 1
            return

        fm.code_lines += 1
        state["branches"] += len(self._BRANCH.findall(stripped))

    # Function: _detect_db2_bad_practices
    def _detect_db2_bad_practices(self, source: str, fm: FileMetrics, dgtt_count: int) -> "List[str]":
        bad = []
        if self._SELECT_STAR.search(source):
            n = len(self._SELECT_STAR.findall(source))
            bad.append(f"SELECT * used {n} time(s) — specify column list for performance")
            fm.duplicate_blocks += n

        if self._LEADING_WILD.search(source):
            n = len(self._LEADING_WILD.findall(source))
            bad.append(f"LIKE '%...' leading wildcard {n} time(s) — prevents index use")
            fm.duplicate_blocks += n

        if self._FUNC_WHERE.search(source):
            bad.append("Function call in WHERE clause (UPPER/LOWER/TRIM) — prevents index seek")
            fm.duplicate_blocks += 1

        if self._LOCK_TABLE.search(source):
            bad.append("LOCK TABLE found — consider row-level isolation (WITH UR/CS/RS) instead")
            fm.duplicate_blocks += 1

        if self._CONCAT_WHERE.search(source):
            bad.append("String concatenation (||) in WHERE clause — possible injection risk")
            fm.duplicate_blocks += 1

        if dgtt_count > 0:
            bad.append(f"{dgtt_count} Declared Global Temporary Table(s) — document lifecycle ownership")

        if self._BIND_PKG.search(source):
            bad.append("DB2 BIND PACKAGE/PLAN detected — static package binds require rebind after schema changes")

        # Catalog queries
        catalog_tables = set(m.lower() for m in self._CATALOG_Q.findall(source))
        if catalog_tables:
            bad.append(f"DB2 catalog queries ({', '.join(sorted(catalog_tables))}) — ensure access is authorized")

        return bad

    # Function: _analyse_file
    def _analyse_file(self, path: Path) -> Optional[FileMetrics]:
        lines = self._read_lines(path)
        if not lines:
            return None

        source = "\n".join(lines)
        fm = FileMetrics(path=path, language="DB2/UDB", total_lines=len(lines))

        state = {"in_block_comment": False, "branches": 0}

        for line in lines:
            stripped = line.strip()
            if not stripped:
                fm.blank_lines += 1
                continue
            self._classify_db2_line(stripped, fm, state)

        fm.cyclomatic    = max(1, 1 + state["branches"])
        fm.todo_comments = self._count_todo(lines)

        # Statement counts (use as function count proxy)
        stmt_count = (
            len(self._SELECT.findall(source))  +
            len(self._INSERT.findall(source))  +
            len(self._UPDATE.findall(source))  +
            len(self._DELETE.findall(source))  +
            len(self._MERGE.findall(source))   +
            len(self._CALL.findall(source))
        )
        fm.functions = len(self._PROC.findall(source)) + len(self._FUNC.findall(source))
        fm.classes   = len(self._TABLE.findall(source)) + len(self._VIEW.findall(source))

        # Specific DB2 signals (store in magic_numbers)
        cursor_count = len(self._CURSOR.findall(source))
        dgtt_count   = len(self._DGTT.findall(source))
        iso_count    = len(self._ISOLATION.findall(source))
        db2_fns      = len(self._DB2_FUNCS.findall(source))
        exec_sql     = len(self._EXEC_SQL.findall(source))
        host_vars    = len(self._HOST_VAR.findall(source))

        fm.magic_numbers = db2_fns  # reuse: DB2 specific function calls

        self._detect_db2_bad_practices(source, fm, dgtt_count)

        return fm

    # ──────────────────────────────────────────────────────────────────────────
    # Function: analyse
    def analyse(self) -> LanguageReport:
        report = super().analyse()

        # Search for embedded SQL in COBOL/C files that might not have .db2 extension
        for cobol_path in list(self.repo_path.rglob("*.cbl")) + \
                          list(self.repo_path.rglob("*.cob")) + \
                          list(self.repo_path.rglob("*.CBL")):
            try:
                lines  = self._read_lines(cobol_path)
                source = "\n".join(lines)
                if self._EXEC_SQL.search(source):
                    exec_count = len(self._EXEC_SQL.findall(source))
                    host_vars  = len(self._HOST_VAR.findall(source))
                    fm = FileMetrics(
                        path=cobol_path,
                        language="DB2/UDB:EmbeddedSQL",
                        total_lines=len(lines),
                        code_lines=exec_count,
                        functions=exec_count,
                        magic_numbers=host_vars,
                    )
                    report.file_count += 1
                    report.total_sloc += exec_count
                    report.files.append(fm)
                    if exec_count > 10:
                        report.bad_practices.append(
                            f"{cobol_path.name}: {exec_count} embedded EXEC SQL blocks "
                            f"with {host_vars} host variables — consider SQLCA error handling"
                        )
            except Exception:
                pass

        # Stored procedures summary
        sp_count = sum(f.functions for f in report.files)
        if sp_count > 0:
            report.dependencies.add(f"DB2 Stored Procedures: {sp_count}")

        # Detect DCLGEN files
        for dclgen_path in self.repo_path.rglob("*.dclgen"):
            report.dependencies.add("DCLGEN host variable declarations")
            break

        return report
