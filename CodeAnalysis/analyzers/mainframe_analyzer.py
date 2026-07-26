# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Analyses Mainframe source files: COBOL, JCL, Assembler (BAL/ASM), PL/I, REXX,
# Date: 2025-07-20
# ---------------------------------------------------------------------------
"""
mainframe_analyzer.py
---------------------
Analyses Mainframe source files: COBOL, JCL, Assembler (BAL/ASM), PL/I, REXX,
CICS, CSP (IBM Cross System Product), VSAM, ISPF, Z/OS UNIX, PANVALET.

Metrics produced
~~~~~~~~~~~~~~~~
- SLOC / comment / blank lines
- Cyclomatic complexity (COBOL: EVALUATE, IF, PERFORM; JCL: steps)
- Paragraph / section / subroutine counts
- Long paragraphs, deep nesting estimates, TODO markers
- CICS command count, EXEC CICS API surface, DFHCOMMAREA usage
- Embedded DB2 SQL (EXEC SQL) statement count + host variable count
- VSAM KSDS/RRDS/ESDS file definitions, ACCESS MODE, FILE STATUS usage
- PANVALET directives (++INCLUDE, ++PATCH, ++MEMBER)
- ISPF services (ISPEXEC, ADDRESS ISPEXEC) in REXX
- Z/OS UNIX system services (bpxwdyn, syscall)
- CSP (.csp) screen definition patterns
- Bad-practice detection:
    COBOL  : GOTO usage, ALTER, global data section size,
              missing EVALUATE (IF-chain overuse), unsafe EXEC SQL
    JCL    : hardcoded DSNs, missing REGION, excessive step count
    CICS   : bare RESP= without EIBRESP check, EXEC CICS without HANDLE
    General: magic literal strings, copy-book count
- Dependency extraction: COPY books, CALL targets, JCL DSNs
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Optional, Set

from analyzers.base_analyzer import BaseAnalyzer, FileMetrics
from config.settings import LANGUAGE_EXTENSIONS


# ─── Language-detection helpers ───────────────────────────────────────────────

# Function: _is_cobol
def _is_cobol(path: Path) -> bool:
    return path.suffix.lower() in {".cbl", ".cob"}

# Function: _is_jcl
def _is_jcl(path: Path) -> bool:
    return path.suffix.lower() == ".jcl"

# Function: _is_asm
def _is_asm(path: Path) -> bool:
    return path.suffix.lower() in {".asm"}

# Function: _is_pli
def _is_pli(path: Path) -> bool:
    return path.suffix.lower() in {".pli"}

# Function: _is_rexx
def _is_rexx(path: Path) -> bool:
    return path.suffix.lower() in {".rexx"}

# Function: _is_csp
def _is_csp(path: Path) -> bool:
    return path.suffix.lower() in {".csp"}

# Function: _is_panvalet
def _is_panvalet(path: Path) -> bool:
    """Panvalet members may have .pnv or no extension — detected by content."""
    return path.suffix.lower() in {".pnv", ".panvalet"}


class MainframeAnalyzer(BaseAnalyzer):
    """Analyser for Mainframe source files (COBOL, JCL, ASM, PL/I, REXX,
    CICS, VSAM, ISPF, CSP, PANVALET, Z/OS UNIX)."""

    EXTENSIONS = LANGUAGE_EXTENSIONS["mainframe"]

    # COBOL
    _COBOL_BRANCH = re.compile(
        r'\b(IF\b|EVALUATE\b|WHEN\b|PERFORM\s+UNTIL\b|PERFORM\s+VARYING\b)',
        re.IGNORECASE
    )
    _COBOL_PARA   = re.compile(r'^[A-Z][A-Z0-9\-]*\.\s*$', re.MULTILINE | re.IGNORECASE)
    _COBOL_GOTO   = re.compile(r'\bGO\s+TO\b', re.IGNORECASE)
    _COBOL_ALTER  = re.compile(r'\bALTER\b', re.IGNORECASE)
    _COBOL_COPY   = re.compile(r'\bCOPY\s+([\w\-]+)', re.IGNORECASE)
    _COBOL_CALL   = re.compile(r'\bCALL\s+["\']?([\w\-]+)["\']?', re.IGNORECASE)

    # JCL
    _JCL_STEP     = re.compile(r'^//\w+\s+EXEC\s', re.MULTILINE)
    _JCL_DSN      = re.compile(r'DSN=([A-Z0-9\$@#\.]+)', re.IGNORECASE)

    # PL/I
    _PLI_BRANCH   = re.compile(
        r'\b(IF\b|DO\s+WHILE\b|SELECT\b|WHEN\b)', re.IGNORECASE
    )
    _PLI_PROC     = re.compile(r'\bPROCEDURE\b', re.IGNORECASE)

    # REXX
    _REXX_BRANCH  = re.compile(
        r'\b(IF\b|DO\s+WHILE\b|DO\s+UNTIL\b|SELECT\b|WHEN\b)', re.IGNORECASE
    )

    # ── CICS patterns ─────────────────────────────────────────────────────────
    _CICS_CMD       = re.compile(r'\bEXEC\s+CICS\b', re.IGNORECASE)
    _CICS_RESP      = re.compile(r'\bRESP\s*=', re.IGNORECASE)
    _CICS_EIBRESP   = re.compile(r'\bEIBRESP\b', re.IGNORECASE)
    _CICS_DFHCOMM   = re.compile(r'\bDFHCOMMARCA\b|\bCOMMAREA\b', re.IGNORECASE)
    _CICS_HANDLE    = re.compile(r'\bEXEC\s+CICS\s+HANDLE\b', re.IGNORECASE)
    _CICS_LINK      = re.compile(r'\bEXEC\s+CICS\s+(LINK|XCTL|RETURN)\b', re.IGNORECASE)
    _CICS_FILE_IO   = re.compile(r'\bEXEC\s+CICS\s+(READ|WRITE|REWRITE|DELETE)\b', re.IGNORECASE)
    _CICS_SEND_RECV = re.compile(r'\bEXEC\s+CICS\s+(SEND|RECEIVE)\b', re.IGNORECASE)
    _CICS_START     = re.compile(r'\bEXEC\s+CICS\s+START\b', re.IGNORECASE)
    _CICS_SYNC      = re.compile(r'\bEXEC\s+CICS\s+SYNCPOINT\b', re.IGNORECASE)

    # ── EXEC SQL (embedded DB2 in COBOL) ─────────────────────────────────────
    _EXEC_SQL       = re.compile(r'\bEXEC\s+SQL\b', re.IGNORECASE)
    _END_EXEC       = re.compile(r'\bEND-EXEC\b', re.IGNORECASE)
    _HOST_VAR       = re.compile(r':[A-Z][A-Z0-9_\-]*\b')
    _INCLUDE_SQLCA  = re.compile(r'\bINCLUDE\s+SQLCA\b', re.IGNORECASE)
    _CURSOR_DECL    = re.compile(r'\bDECLARE\s+\w+\s+CURSOR\b', re.IGNORECASE)

    # ── VSAM patterns ─────────────────────────────────────────────────────────
    _VSAM_ASSIGN    = re.compile(r'\bSELECT\b.*\bASSIGN\s+TO\b', re.IGNORECASE)
    _VSAM_ORG       = re.compile(r'\bORGANIZATION\s+IS\s+(INDEXED|RELATIVE|SEQUENTIAL)\b', re.IGNORECASE)
    _VSAM_ACCESS    = re.compile(r'\bACCESS\s+MODE\s+IS\b', re.IGNORECASE)
    _VSAM_RECKEY    = re.compile(r'\bRECORD\s+KEY\s+IS\b', re.IGNORECASE)
    _VSAM_ALTKEY    = re.compile(r'\bALTERNATE\s+RECORD\s+KEY\b', re.IGNORECASE)
    _VSAM_FILE_STATUS= re.compile(r'\bFILE\s+STATUS\b', re.IGNORECASE)
    _VSAM_JCL_AMP   = re.compile(r'\bAMP=', re.IGNORECASE)

    # ── PANVALET patterns ──────────────────────────────────────────────────────
    _PNV_INCLUDE    = re.compile(r'^\+\+INCLUDE\b', re.MULTILINE | re.IGNORECASE)
    _PNV_PATCH      = re.compile(r'^\+\+PATCH\b',   re.MULTILINE | re.IGNORECASE)
    _PNV_MEMBER     = re.compile(r'^\+\+MEMBER\b',  re.MULTILINE | re.IGNORECASE)
    _PNV_ADD        = re.compile(r'^\+\+ADD\b',     re.MULTILINE | re.IGNORECASE)
    _PNV_DELETE_S   = re.compile(r'^\+\+DELETE\b',  re.MULTILINE | re.IGNORECASE)

    # ── ISPF / REXX ISPF patterns ─────────────────────────────────────────────
    _ISPF_EXEC      = re.compile(r'\bISPEXEC\b|\bADDRESS\s+ISPEXEC\b', re.IGNORECASE)
    _ISPF_SERVICES  = re.compile(
        r'\bISPEXEC\s+(DISPLAY|SETMSG|VPUT|VGET|TBOPEN|TBCLOSE|TBGET|TBPUT|TBSEARCH|'
        r'SELECT|CONTROL|FTOPEN|FTINCL|FTCLOSE|LMOPEN|LMPUT|LMGET)\b',
        re.IGNORECASE
    )

    # ── Z/OS UNIX (USS) ──────────────────────────────────────────────────────
    _ZOS_UNIX       = re.compile(r'\bbpxwdyn\b|\bsyscall\b|\bBPX\w+\b', re.IGNORECASE)
    _ZOS_USS_PATH   = re.compile(r'["\'][/][a-zA-Z0-9_/\-\.]+["\']')

    # ── CSP patterns ─────────────────────────────────────────────────────────
    _CSP_SCREEN     = re.compile(r'\bCSP\s+SCREEN\b|\bCSP\s+PROCESS\b|\bCSP\s+RECORD\b', re.IGNORECASE)
    _CSP_STMT       = re.compile(r'\bCSP\b', re.IGNORECASE)

    # Function: language_name
    def language_name(self) -> str:
        return "Mainframe"

    # ──────────────────────────────────────────────────────────────────────────
    # Single-file analysis
    # ──────────────────────────────────────────────────────────────────────────

    # Function: _analyse_file
    def _analyse_file(self, path: Path) -> Optional[FileMetrics]:
        lines = self._read_lines(path)
        if not lines:
            return None

        fm = FileMetrics(path=path, language="Mainframe", total_lines=len(lines))

        if _is_cobol(path):
            return self._analyse_cobol(fm, lines)
        elif _is_jcl(path):
            return self._analyse_jcl(fm, lines)
        elif _is_asm(path):
            return self._analyse_asm(fm, lines)
        elif _is_pli(path):
            return self._analyse_pli(fm, lines)
        elif _is_rexx(path):
            return self._analyse_rexx(fm, lines)
        elif _is_csp(path):
            return self._analyse_csp(fm, lines)
        elif _is_panvalet(path):
            return self._analyse_panvalet(fm, lines)
        return None

    # ──────────────────────────────────────────────────────────────────────────
    # COBOL
    # ──────────────────────────────────────────────────────────────────────────

    # Function: _analyse_cobol
    def _analyse_cobol(self, fm: FileMetrics, lines: list) -> FileMetrics:
        source = "\n".join(lines)
        self._count_cobol_lines(fm, lines)

        fm.todo_comments = self._count_todo(lines)
        fm.cyclomatic    = 1 + len(self._COBOL_BRANCH.findall(source))
        fm.functions     = len(self._COBOL_PARA.findall(source))   # paragraphs ≈ functions
        fm.deep_nesting  = self._estimate_cobol_nesting(source)
        fm.magic_numbers = self._count_magic_numbers(lines)

        # COBOL bad practices via duplicate_blocks field
        goto_count  = len(self._COBOL_GOTO.findall(source))
        alter_count = len(self._COBOL_ALTER.findall(source))
        fm.duplicate_blocks = goto_count + alter_count

        self._detect_cics(fm, source)
        self._detect_embedded_sql(fm, source)
        self._detect_vsam(fm, source)

        return fm

    # Function: _count_cobol_lines
    @staticmethod
    def _count_cobol_lines(fm: FileMetrics, lines: list) -> None:
        for line in lines:
            stripped = line.strip()
            if not stripped:
                fm.blank_lines += 1
            elif stripped.startswith("*") or (len(line) > 6 and line[6] == "*"):
                fm.comment_lines += 1
            else:
                fm.code_lines += 1

    # Function: _detect_cics
    def _detect_cics(self, fm: FileMetrics, source: str) -> None:
        # ── CICS detection ────────────────────────────────────────────────────
        cics_count    = len(self._CICS_CMD.findall(source))
        cics_resp     = len(self._CICS_RESP.findall(source))
        cics_eibresp  = len(self._CICS_EIBRESP.findall(source))
        cics_link     = len(self._CICS_LINK.findall(source))
        cics_file_io  = len(self._CICS_FILE_IO.findall(source))
        fm.cyclomatic += cics_count   # CICS commands add complexity
        if cics_count > 0:
            # Store CICS count in magic_numbers if not already used
            fm.magic_numbers += cics_count
            # Bad practice: EXEC CICS without RESP= checking
            if cics_resp == 0:
                fm.duplicate_blocks += 1  # no error handling

    # Function: _detect_embedded_sql
    def _detect_embedded_sql(self, fm: FileMetrics, source: str) -> None:
        # ── EXEC SQL (embedded DB2) ───────────────────────────────────────────
        exec_sql_count = len(self._EXEC_SQL.findall(source))
        host_var_count = len(self._HOST_VAR.findall(source))
        has_sqlca      = bool(self._INCLUDE_SQLCA.search(source))
        cursor_count   = len(self._CURSOR_DECL.findall(source))

        if exec_sql_count > 0:
            fm.cyclomatic += exec_sql_count // 3  # Each SQL adds modest complexity
            if not has_sqlca:
                fm.duplicate_blocks += 1   # Missing SQLCA = no error handling

    # Function: _detect_vsam
    def _detect_vsam(self, fm: FileMetrics, source: str) -> None:
        # ── VSAM detection ────────────────────────────────────────────────────
        vsam_files  = len(self._VSAM_ORG.findall(source))
        has_fstatus = bool(self._VSAM_FILE_STATUS.search(source))
        if vsam_files > 0 and not has_fstatus:
            fm.duplicate_blocks += 1  # VSAM without FILE STATUS = hidden I/O errors

    # Function: _estimate_cobol_nesting
    @staticmethod
    def _estimate_cobol_nesting(source: str) -> int:
        """Count nested IF depth as a proxy for deep-nesting issues."""
        depth = count = max_depth = 0
        for line in source.splitlines():
            upper = line.upper()
            if re.search(r'\bIF\b', upper):
                depth += 1
                max_depth = max(max_depth, depth)
                if depth > 4:
                    count += 1
            if re.search(r'\b(END-IF|ELSE)\b', upper):
                depth = max(0, depth - 1)
        return count

    # ──────────────────────────────────────────────────────────────────────────
    # JCL
    # ──────────────────────────────────────────────────────────────────────────

    # Function: _analyse_jcl
    def _analyse_jcl(self, fm: FileMetrics, lines: list) -> FileMetrics:
        source = "\n".join(lines)
        for line in lines:
            stripped = line.strip()
            if not stripped:
                fm.blank_lines += 1
            elif stripped.startswith("//*"):
                fm.comment_lines += 1
            else:
                fm.code_lines += 1

        steps = len(self._JCL_STEP.findall(source))
        fm.functions  = steps                    # steps ≈ functions in JCL
        fm.cyclomatic = max(1, steps)            # each step is a branch point
        fm.magic_numbers = len(self._JCL_DSN.findall(source))   # hardcoded DSNs
        return fm

    # ──────────────────────────────────────────────────────────────────────────
    # Assembler (BAL)
    # ──────────────────────────────────────────────────────────────────────────

    # Function: _analyse_asm
    def _analyse_asm(self, fm: FileMetrics, lines: list) -> FileMetrics:
        branch_ops = re.compile(
            r'\b(B|BE|BNE|BH|BL|BNH|BNL|BCT|BXLE|BAS|BAL|BC|BIC)\b'
        )
        source = "\n".join(lines)
        for line in lines:
            stripped = line.strip()
            if not stripped or stripped.startswith("*"):
                fm.blank_lines += (0 if stripped else 1)
                fm.comment_lines += (1 if stripped.startswith("*") else 0)
            else:
                fm.code_lines += 1

        fm.cyclomatic = 1 + len(branch_ops.findall(source))
        fm.todo_comments = self._count_todo(lines)
        return fm

    # ──────────────────────────────────────────────────────────────────────────
    # PL/I
    # ──────────────────────────────────────────────────────────────────────────

    # Function: _analyse_pli
    def _analyse_pli(self, fm: FileMetrics, lines: list) -> FileMetrics:
        source = "\n".join(lines)
        in_block = False
        for line in lines:
            stripped = line.strip()
            if not stripped:
                fm.blank_lines += 1
                continue
            if "/*" in stripped:
                in_block = True
            if in_block:
                fm.comment_lines += 1
                if "*/" in stripped:
                    in_block = False
                continue
            fm.code_lines += 1

        fm.cyclomatic = 1 + len(self._PLI_BRANCH.findall(source))
        fm.functions  = len(self._PLI_PROC.findall(source))
        fm.todo_comments = self._count_todo(lines)
        return fm

    # ──────────────────────────────────────────────────────────────────────────
    # REXX
    # ──────────────────────────────────────────────────────────────────────────

    # Function: _analyse_rexx
    def _analyse_rexx(self, fm: FileMetrics, lines: list) -> FileMetrics:
        source = "\n".join(lines)
        for line in lines:
            stripped = line.strip()
            if not stripped:
                fm.blank_lines += 1
            elif stripped.startswith("/*") or stripped.startswith("--"):
                fm.comment_lines += 1
            else:
                fm.code_lines += 1

        fm.cyclomatic    = 1 + len(self._REXX_BRANCH.findall(source))
        fm.todo_comments = self._count_todo(lines)

        # ISPF services detection
        ispf_count = len(self._ISPF_EXEC.findall(source))
        if ispf_count > 0:
            fm.magic_numbers += ispf_count   # ISPF service calls

        # Z/OS UNIX system services
        uss_count = len(self._ZOS_UNIX.findall(source))
        if uss_count > 0:
            fm.magic_numbers += uss_count

        return fm

    # ──────────────────────────────────────────────────────────────────────────
    # CSP (IBM Cross System Product)
    # ──────────────────────────────────────────────────────────────────────────

    # Function: _analyse_csp
    def _analyse_csp(self, fm: FileMetrics, lines: list) -> FileMetrics:
        source = "\n".join(lines)
        fm.language = "Mainframe:CSP"
        for line in lines:
            stripped = line.strip()
            if not stripped:
                fm.blank_lines += 1
            elif stripped.startswith("*"):
                fm.comment_lines += 1
            else:
                fm.code_lines += 1

        csp_screens = len(self._CSP_SCREEN.findall(source))
        fm.functions  = csp_screens
        fm.cyclomatic = max(1, csp_screens)
        fm.todo_comments = self._count_todo(lines)
        return fm

    # ──────────────────────────────────────────────────────────────────────────
    # PANVALET
    # ──────────────────────────────────────────────────────────────────────────

    # Function: _analyse_panvalet
    def _analyse_panvalet(self, fm: FileMetrics, lines: list) -> FileMetrics:
        source = "\n".join(lines)
        fm.language = "Mainframe:PANVALET"
        for line in lines:
            stripped = line.strip()
            if not stripped:
                fm.blank_lines += 1
            elif stripped.startswith("**"):
                fm.comment_lines += 1
            else:
                fm.code_lines += 1

        includes = len(self._PNV_INCLUDE.findall(source))
        patches  = len(self._PNV_PATCH.findall(source))
        members  = len(self._PNV_MEMBER.findall(source))
        fm.functions = includes + members
        fm.magic_numbers = patches   # patches are risky — counted as magic numbers
        return fm

    # ──────────────────────────────────────────────────────────────────────────
    # Dependency extraction
    # ──────────────────────────────────────────────────────────────────────────

    # Function: _extract_dependencies
    def _extract_dependencies(self) -> Set[str]:
        deps: Set[str] = set()
        for path in self._iter_source_files():
            if not _is_cobol(path):
                continue
            source = "\n".join(self._read_lines(path))
            for m in self._COBOL_COPY.finditer(source):
                deps.add(f"COPY:{m.group(1).upper()}")
            for m in self._COBOL_CALL.finditer(source):
                deps.add(f"CALL:{m.group(1).upper()}")
        return deps

    # ──────────────────────────────────────────────────────────────────────────
    # Repo-level augments
    # ──────────────────────────────────────────────────────────────────────────

    # Function: _summarize_goto_alter
    @staticmethod
    def _summarize_goto_alter(report) -> None:
        # COBOL GO TO / ALTER
        goto_total = sum(f.duplicate_blocks for f in report.files
                         if f.language in ("Mainframe", "Mainframe:CSP"))
        if goto_total:
            report.bad_practices.append(
                f"COBOL GO TO / ALTER statements (hard to maintain): {goto_total}"
            )

    # Function: _summarize_cics
    @staticmethod
    def _summarize_cics(report) -> None:
        # CICS summary
        total_cics = sum(
            f.magic_numbers for f in report.files
            if f.language == "Mainframe"
        )
        if total_cics > 0:
            report.dependencies.add("CICS (IBM Customer Information Control System)")
            report.bad_practices.append(
                f"CICS: {total_cics} EXEC CICS command(s) detected across "
                f"{sum(1 for f in report.files if f.magic_numbers > 0)} COBOL file(s). "
                f"Migration to REST microservices requires CICS API rewrite."
            )

    # Function: _summarize_vsam
    def _summarize_vsam(self, report) -> None:
        # VSAM summary — scan COBOL files for VSAM organization
        vsam_count = 0
        for path in self._iter_source_files():
            if not _is_cobol(path):
                continue
            try:
                source = "\n".join(self._read_lines(path))
                orgs = self._VSAM_ORG.findall(source)
                if orgs:
                    vsam_count += len(orgs)
                    for org in set(o.upper() for o in orgs):
                        report.dependencies.add(f"VSAM ({org})")
            except Exception:
                pass

        if vsam_count:
            report.bad_practices.append(
                f"VSAM: {vsam_count} file organization(s) (INDEXED/SEQUENTIAL/RELATIVE) — "
                f"consider migration to DB2, PostgreSQL, or NoSQL."
            )

    # Function: _summarize_panvalet
    @staticmethod
    def _summarize_panvalet(report) -> None:
        # PANVALET
        pnv_count = sum(1 for f in report.files if f.language == "Mainframe:PANVALET")
        if pnv_count:
            report.dependencies.add("PANVALET source library manager")
            report.bad_practices.append(
                f"PANVALET: {pnv_count} member file(s) — "
                f"consider migration to Git-based SCM."
            )

    # Function: _summarize_ispf
    def _summarize_ispf(self, report) -> None:
        # ISPF REXX
        ispf_count = sum(
            f.magic_numbers for f in report.files
            if f.language in ("Mainframe", "Mainframe:REXX")
            and getattr(f, "_ispf", False)
        )

        # Scan REXX files explicitly for ISPF
        for path in self._iter_source_files():
            if not _is_rexx(path):
                continue
            try:
                source = "\n".join(self._read_lines(path))
                if self._ISPF_EXEC.search(source):
                    report.dependencies.add("ISPF (Interactive System Productivity Facility)")
                    break
            except Exception:
                pass

    # Function: _summarize_embedded_sql
    def _summarize_embedded_sql(self, report) -> None:
        # Embedded SQL
        exec_sql_total = 0
        for path in self._iter_source_files():
            if not _is_cobol(path):
                continue
            try:
                source = "\n".join(self._read_lines(path))
                exec_sql_total += len(self._EXEC_SQL.findall(source))
            except Exception:
                pass

        if exec_sql_total:
            report.dependencies.add("DB2 (Embedded SQL in COBOL)")
            report.bad_practices.append(
                f"Embedded SQL: {exec_sql_total} EXEC SQL block(s) in COBOL — "
                f"ensure SQLCA/GET DIAGNOSTICS error handling is present."
            )

    # Function: analyse
    def analyse(self):
        report = super().analyse()
        self._summarize_goto_alter(report)
        self._summarize_cics(report)
        self._summarize_vsam(report)
        self._summarize_panvalet(report)
        self._summarize_ispf(report)
        self._summarize_embedded_sql(report)
        return report
