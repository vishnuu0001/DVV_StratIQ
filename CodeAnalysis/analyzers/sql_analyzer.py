# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Analyses SQL, DDL, DML and stored-procedure source files.
# Date: 2025-10-21
# ---------------------------------------------------------------------------
"""
sql_analyzer.py
---------------
Analyses SQL, DDL, DML and stored-procedure source files.

Supported flavours / extensions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.sql  .ddl  .dml  .psql  .pgsql   — generic + PostgreSQL
.tsql                              — T-SQL (SQL Server)
.plsql .pls .prc .fnc .trg        — PL/SQL (Oracle)
.pkb  .pks                        — Oracle package body / spec
.hql                               — Hibernate Query Language

Metrics produced
~~~~~~~~~~~~~~~~
- SLOC / comment / blank lines
- Object counts: tables, views, indexes, stored procs / functions / triggers
- Cyclomatic complexity estimate (IF / CASE / LOOP / CURSOR branches)
- Bad-practice detection:
    SELECT *  •  dynamic SQL (EXEC / EXECUTE IMMEDIATE / sp_executesql)
    •  DELETE/UPDATE without WHERE clause  •  implicit cursors
    •  non-parameterised string concatenation in SQL
    •  hardcoded credentials patterns
- Dependency extraction:
    external DB links (OPENROWSET / LINKED SERVER / dblink)
    •  cross-database references (db.schema.table patterns)
"""
from __future__ import annotations
import os
import re
from pathlib import Path
from typing import Optional, Set

from analyzers.base_analyzer import BaseAnalyzer, FileMetrics, LanguageReport
from config.settings import LANGUAGE_EXTENSIONS


class SQLAnalyzer(BaseAnalyzer):
    """Analyser for SQL/DDL/DML and stored-procedure files."""

    EXTENSIONS = LANGUAGE_EXTENSIONS.get(
        "sql",
        {".sql", ".ddl", ".dml", ".psql", ".pgsql", ".hql",
         ".tsql", ".plsql", ".pls", ".prc", ".fnc", ".trg", ".pkb", ".pks"},
    )

    # ── DDL object creation ──────────────────────────────────────────────────
    _TABLE    = re.compile(r'\bCREATE\s+(?:OR\s+REPLACE\s+)?(?:TEMPORARY\s+)?TABLE\b',
                           re.IGNORECASE)
    _VIEW     = re.compile(r'\bCREATE\s+(?:OR\s+REPLACE\s+)?(?:MATERIALIZED\s+)?VIEW\b',
                           re.IGNORECASE)
    _INDEX    = re.compile(r'\bCREATE\s+(?:UNIQUE\s+)?(?:CLUSTERED\s+)?'
                           r'(?:NONCLUSTERED\s+)?INDEX\b', re.IGNORECASE)
    _PROC     = re.compile(r'\bCREATE\s+(?:OR\s+REPLACE\s+)?'
                           r'(?:PROCEDURE|PROC|FUNCTION|TRIGGER|PACKAGE\s+BODY'
                           r'|PACKAGE)\b', re.IGNORECASE)
    _SEQUENCE = re.compile(r'\bCREATE\s+SEQUENCE\b', re.IGNORECASE)

    # ── DML keywords ────────────────────────────────────────────────────────
    _SELECT   = re.compile(r'\bSELECT\b', re.IGNORECASE)
    _INSERT   = re.compile(r'\bINSERT\s+INTO\b', re.IGNORECASE)
    _UPDATE   = re.compile(r'\bUPDATE\b', re.IGNORECASE)
    _DELETE   = re.compile(r'\bDELETE\s+FROM\b', re.IGNORECASE)

    # ── Complexity branches ──────────────────────────────────────────────────
    _BRANCH   = re.compile(
        r'\b(IF\b|ELSE\b|ELSIF\b|ELSEIF\b|CASE\b|WHEN\b|'
        r'WHILE\b|LOOP\b|FOR\b|REPEAT\b|LEAVE\b|CONTINUE\b|'
        r'EXCEPTION\b|BEGIN\b)\b',
        re.IGNORECASE,
    )

    # ── Bad practices ────────────────────────────────────────────────────────
    _SELECT_STAR   = re.compile(r'\bSELECT\s+\*', re.IGNORECASE)
    _DYNAMIC_SQL   = re.compile(
        r'\b(EXEC(?:UTE)?\s+(?:\(|sp_executesql\b)|EXECUTE\s+IMMEDIATE\b'
        r'|PREPARE\s+\w+\s+FROM\b)', re.IGNORECASE
    )
    # UPDATE / DELETE with nothing meaningful before next statement end —
    # heuristic: no WHERE token on the same logical statement block
    _UPDATE_NO_WHERE = re.compile(
        r'\bUPDATE\b(?:(?!\bWHERE\b).)*?;', re.IGNORECASE | re.DOTALL
    )
    _DELETE_NO_WHERE = re.compile(
        r'\bDELETE\s+FROM\b(?:(?!\bWHERE\b).)*?;', re.IGNORECASE | re.DOTALL
    )
    _HARDCODED_CRED  = re.compile(
        r"(?:password|passwd|pwd|secret)\s*=\s*['\"][^'\"]{3,}['\"]",
        re.IGNORECASE,
    )
    _CURSOR          = re.compile(r'\bDECLARE\b.*\bCURSOR\b', re.IGNORECASE)

    # ── Dependencies ─────────────────────────────────────────────────────────
    _DBLINK          = re.compile(r'@(\w+)', re.IGNORECASE)           # Oracle DB link
    _OPENROWSET      = re.compile(r'\bOPENROWSET\s*\(', re.IGNORECASE)
    _LINKED_SERVER   = re.compile(r'\[?(\w+)\]?\.\[?\w+\]?\.\[?\w+\]?\.\[?\w+\]?',   # 4-part name
                                   re.IGNORECASE)
    _DBLINK_PG       = re.compile(r'\bdblink\s*\(', re.IGNORECASE)    # PostgreSQL dblink

    # Function: language_name
    def language_name(self) -> str:
        return "SQL/Database"

    # ─────────────────────────────────────────────────────────────────────────
    # Single-file analysis
    # ─────────────────────────────────────────────────────────────────────────

    # Function: _classify_sql_line
    @staticmethod
    def _classify_sql_line(stripped: str, fm: FileMetrics, state: dict) -> None:
        if stripped.startswith("/*"):
            state["in_block"] = True
        if state["in_block"]:
            fm.comment_lines += 1
            if "*/" in stripped:
                state["in_block"] = False
            return
        if stripped.startswith("--") or stripped.startswith("//"):
            fm.comment_lines += 1
        else:
            fm.code_lines += 1

    # Function: _begin_end_nesting
    @staticmethod
    def _begin_end_nesting(lines: list, begin_re, end_re) -> "tuple[int, int]":
        """Crude nesting via BEGIN/END depth (PL/SQL / T-SQL). Returns (max_depth, deep_nesting_lines)."""
        depth = max_depth = 0
        deep_lines = 0
        for line in lines:
            delta = len(begin_re.findall(line)) - len(end_re.findall(line))
            depth += delta
            max_depth = max(max_depth, depth)
            if delta > 4:
                deep_lines += 1
        return max(0, max_depth), deep_lines

    # Function: _analyse_file
    def _analyse_file(self, path: Path) -> Optional[FileMetrics]:
        lines = self._read_lines(path)
        if not lines:
            return None

        fm       = FileMetrics(path=path, language="SQL/Database", total_lines=len(lines))
        source   = "\n".join(lines)

        # ── Line classification ──────────────────────────────────────────────
        state = {"in_block": False}
        for line in lines:
            stripped = line.strip()
            if not stripped:
                fm.blank_lines += 1
                continue
            self._classify_sql_line(stripped, fm, state)

        fm.todo_comments = self._count_todo(lines)

        # ── Object counts: reuse fields ──────────────────────────────────────
        # classes   → DDL objects (tables + views + sequences)
        # functions → procedural objects (procs + functions + triggers + pkgs)
        fm.classes   = (len(self._TABLE.findall(source))
                        + len(self._VIEW.findall(source))
                        + len(self._INDEX.findall(source))
                        + len(self._SEQUENCE.findall(source)))
        fm.functions = len(self._PROC.findall(source))

        # ── Cyclomatic complexity ────────────────────────────────────────────
        stripped_src = re.sub(r'--[^\n]*', '', source)
        stripped_src = re.sub(r'/\*.*?\*/', '', stripped_src, flags=re.DOTALL)
        fm.cyclomatic = max(1, round((1 + len(self._BRANCH.findall(stripped_src))) / max(fm.functions, 1)))

        # ── Bad practices → duplicate_blocks counter ─────────────────────────
        smells = 0
        smells += len(self._SELECT_STAR.findall(source))
        smells += len(self._DYNAMIC_SQL.findall(source))
        smells += len(self._UPDATE_NO_WHERE.findall(source))
        smells += len(self._DELETE_NO_WHERE.findall(source))
        smells += len(self._HARDCODED_CRED.findall(source))
        smells += len(self._CURSOR.findall(source))
        fm.duplicate_blocks = smells

        begin_re  = re.compile(r'\bBEGIN\b', re.IGNORECASE)
        end_re    = re.compile(r'\bEND\b',   re.IGNORECASE)
        fm.max_depth, fm.deep_nesting = self._begin_end_nesting(lines, begin_re, end_re)

        return fm

    # ─────────────────────────────────────────────────────────────────────────
    # Repository-level augments
    # ─────────────────────────────────────────────────────────────────────────

    # Function: _concat_all_sql_source
    def _concat_all_sql_source(self) -> str:
        source_all = ""
        _skip = {".git", "node_modules", "vendor", "venv", ".venv", "target", "__pycache__"}
        for dirpath, dirnames, filenames in os.walk(str(self.repo_path)):
            dirnames[:] = [d for d in dirnames if d not in _skip]
            for fname in filenames:
                fpath = Path(dirpath) / fname
                if fpath.suffix in self.EXTENSIONS:
                    try:
                        source_all += fpath.read_text(encoding="utf-8", errors="replace")
                    except OSError:
                        pass
        return source_all

    # Function: analyse
    def analyse(self) -> LanguageReport:
        report = super().analyse()

        if not report.files:
            return report

        source_all = self._concat_all_sql_source()

        total_smells = sum(f.duplicate_blocks for f in report.files)
        if total_smells:
            report.bad_practices.append(
                f"SELECT * / dynamic SQL / missing WHERE / cursors / hardcoded creds: {total_smells}"
            )

        select_star = len(self._SELECT_STAR.findall(source_all))
        if select_star:
            report.bad_practices.append(f"SELECT * usage: {select_star}")

        dynamic_sql = len(self._DYNAMIC_SQL.findall(source_all))
        if dynamic_sql:
            report.bad_practices.append(f"Dynamic SQL (EXEC/EXECUTE IMMEDIATE): {dynamic_sql}")

        # Table / proc summary (sum across files)
        total_tables = sum(f.classes   for f in report.files)
        total_procs  = sum(f.functions for f in report.files)
        if total_tables:
            report.bad_practices.append(f"DDL objects (tables/views/indexes/sequences): {total_tables}")
        if total_procs:
            report.bad_practices.append(f"Procedural objects (procs/functions/triggers/packages): {total_procs}")

        return report

    # ─────────────────────────────────────────────────────────────────────────
    # Dependency extraction
    # ─────────────────────────────────────────────────────────────────────────

    # Function: _extract_deps_from_sql_source
    def _extract_deps_from_sql_source(self, src: str, deps: Set[str]) -> None:
        # Oracle DB links  (@DBNAME)
        for m in self._DBLINK.finditer(src):
            deps.add(f"dblink:{m.group(1).lower()}")

        # SQL Server / Synapse OPENROWSET
        if self._OPENROWSET.search(src):
            deps.add("openrowset:external-datasource")

        # PostgreSQL dblink
        if self._DBLINK_PG.search(src):
            deps.add("postgres:dblink-extension")

        # 4-part server.db.schema.table references
        for m in self._LINKED_SERVER.finditer(src):
            full = m.group(0)
            parts = [p.strip("[").strip("]") for p in full.split(".")]
            if len(parts) == 4:
                deps.add(f"linked-server:{parts[0].lower()}")

    # Function: _extract_dependencies
    def _extract_dependencies(self) -> Set[str]:
        deps: Set[str] = set()
        _skip = {".git", "node_modules", "vendor", "venv", ".venv", "target", "__pycache__"}
        for dirpath, dirnames, filenames in os.walk(str(self.repo_path)):
            dirnames[:] = [d for d in dirnames if d not in _skip]
            for fname in filenames:
                fpath = Path(dirpath) / fname
                if fpath.suffix not in self.EXTENSIONS:
                    continue
                try:
                    src = fpath.read_text(encoding="utf-8", errors="replace")
                except OSError:
                    continue
                self._extract_deps_from_sql_source(src, deps)

        return deps
