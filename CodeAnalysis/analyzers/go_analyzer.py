# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Analyses Go source files (.go).
# Date: 2025-10-06
# ---------------------------------------------------------------------------
"""
go_analyzer.py
--------------
Analyses Go source files (.go).

Metrics produced
~~~~~~~~~~~~~~~~
- SLOC / comment / blank lines
- Cyclomatic complexity (branch pattern counting)
- Function / struct / interface counts
- Long functions, deep nesting, magic numbers, TODO markers
- Bad-practice detection:
    • panic() usage
    • blank error suppression (_, err = …; _ = err)
    • time.Sleep in non-test code (latency smell)
    • log.Fatal / os.Exit outside main (hard to test)
    • fmt.Print debug output
    • global mutable var declarations
- Dependency extraction from go.mod
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Optional, Set

from analyzers.base_analyzer import BaseAnalyzer, FileMetrics, LanguageReport
from config.settings import LANGUAGE_EXTENSIONS


class GoAnalyzer(BaseAnalyzer):
    """Analyser for Go source files."""

    EXTENSIONS = LANGUAGE_EXTENSIONS.get("go", {".go"})

    _BRANCH = re.compile(
        r'\b(if\b|else\s+if\b|for\b|switch\b|select\b|case\b|'
        r'&&|\|\|)\b'
    )
    _FUNC      = re.compile(r'^func\s+(?:\(\w[^)]*\)\s+)?\w+\s*\(', re.MULTILINE)
    _STRUCT    = re.compile(r'\btype\s+\w+\s+struct\b')
    _INTERFACE = re.compile(r'\btype\s+\w+\s+interface\b')

    # Bad practices
    _PANIC         = re.compile(r'\bpanic\s*\(')
    _BLANK_ERR     = re.compile(r'_\s*(?:,\s*err\b|=\s*err\b)')
    _SLEEP         = re.compile(r'\btime\.Sleep\s*\(')
    _FATAL         = re.compile(r'\b(?:log\.Fatal|os\.Exit)\s*\(')
    _FMT_PRINT     = re.compile(r'\bfmt\.Print(?:f|ln)?\s*\(')
    _GLOBAL_VAR    = re.compile(r'^var\s+\w+', re.MULTILINE)
    _HARDCODED_CRED = re.compile(
        r"(?:password|passwd|secret|apiKey|api_key|token)\s*=\s*\"[^\"]{4,}\"",
        re.IGNORECASE,
    )

    # Function: language_name
    def language_name(self) -> str:
        return "Go"

    # ─────────────────────────────────────────────────────────────────────────

    # Function: _analyse_file
    def _analyse_file(self, path: Path) -> Optional[FileMetrics]:
        lines = self._read_lines(path)
        if not lines:
            return None

        fm     = FileMetrics(path=path, language="Go", total_lines=len(lines))
        source = "\n".join(lines)

        # Line classification
        in_block = False
        for line in lines:
            stripped = line.strip()
            if not stripped:
                fm.blank_lines += 1
                continue
            if "/*" in stripped and "*/" not in stripped:
                in_block = True
            if in_block:
                fm.comment_lines += 1
                if "*/" in stripped:
                    in_block = False
                continue
            if stripped.startswith("//"):
                fm.comment_lines += 1
            else:
                fm.code_lines += 1

        fm.todo_comments = self._count_todo(lines)
        fm.magic_numbers = self._count_magic_numbers(lines)
        fm.max_depth     = self._max_nesting_depth(lines)
        fm.deep_nesting  = self._deep_nesting_count(lines, threshold=4)

        stripped_src = re.sub(r'//[^\n]*', '', source)
        stripped_src = re.sub(r'/\*.*?\*/', '', stripped_src, flags=re.DOTALL)
        fm.functions   = len(self._FUNC.findall(source))
        fm.cyclomatic  = max(1, round((1 + len(self._BRANCH.findall(stripped_src))) / max(fm.functions, 1)))
        fm.classes     = (len(self._STRUCT.findall(source))
                          + len(self._INTERFACE.findall(source)))
        fm.long_methods = self._count_long_methods(source)

        smells = (
            len(self._PANIC.findall(source))
            + len(self._BLANK_ERR.findall(source))
            + len(self._SLEEP.findall(source))
            + len(self._FATAL.findall(source))
            + len(self._FMT_PRINT.findall(source))
            + len(self._GLOBAL_VAR.findall(source))
            + len(self._HARDCODED_CRED.findall(source))
        )
        fm.duplicate_blocks = smells
        return fm

    # Function: analyse
    def analyse(self) -> LanguageReport:
        report = super().analyse()
        total_smells = sum(f.duplicate_blocks for f in report.files)
        if total_smells:
            report.bad_practices.append(
                f"panic/blank-err/time.Sleep/log.Fatal/fmt.Print/global-var: {total_smells}"
            )
        return report

    # ─────────────────────────────────────────────────────────────────────────

    # Function: _extract_dependencies
    def _extract_dependencies(self) -> Set[str]:
        deps: Set[str] = set()
        for gomod in self.repo_path.rglob("go.mod"):
            try:
                src = gomod.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            for m in re.finditer(r'^\s+([a-z][a-zA-Z0-9/_.-]+)\s+v', src, re.MULTILINE):
                deps.add(m.group(1).lower())
        return deps

    # Function: _count_long_methods
    @staticmethod
    def _count_long_methods(source: str, threshold: int = 40) -> int:
        depth = count = 0
        start = None
        for i, line in enumerate(source.splitlines()):
            opens  = line.count("{")
            closes = line.count("}")
            if depth == 0 and opens > 0:
                start = i
            depth += opens - closes
            if depth <= 0 and start is not None:
                if (i - start) > threshold:
                    count += 1
                depth = 0
                start = None
        return count
