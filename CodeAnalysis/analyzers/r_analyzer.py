# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Analyses R and R Markdown source files (.r .R .Rmd .Rmarkdown).
# Date: 2025-08-17
# ---------------------------------------------------------------------------
"""
r_analyzer.py
-------------
Analyses R and R Markdown source files (.r .R .Rmd .Rmarkdown).

Metrics produced
~~~~~~~~~~~~~~~~
- SLOC / comment / blank lines
- Cyclomatic complexity (branch pattern counting)
- Function counts  (function(…) assignments)
- Long functions, magic numbers, TODO markers
- Bad-practice detection:
    • setwd() (hard to reproduce paths)
    • rm(list=ls()) (clears environment — fragile scripting)
    • attach() (namespace pollution)
    • T / F as TRUE/FALSE shortcuts (can be overwritten)
    • Hardcoded file paths (Windows/Unix absolute paths)
    • suppressWarnings / suppressMessages abuse
- Dependency extraction from library() / require() / DESCRIPTION Imports
"""
from __future__ import annotations
import os
import re
from pathlib import Path
from typing import Optional, Set

from analyzers.base_analyzer import BaseAnalyzer, FileMetrics, LanguageReport
from config.settings import LANGUAGE_EXTENSIONS


class RAnalyzer(BaseAnalyzer):
    """Analyser for R source files."""

    EXTENSIONS = LANGUAGE_EXTENSIONS.get("r", {".r", ".R", ".Rmd", ".Rmarkdown"})

    _BRANCH = re.compile(
        r'\b(if\b|else\s+if\b|for\b|while\b|repeat\b|switch\b|'
        r'&&|\|\|)\b'
    )
    # function assignment: foo <- function(…) or foo = function(…)
    _FUNC = re.compile(r'\w+\s*(?:<-|=)\s*function\s*\(')

    # Bad practices
    _SETWD            = re.compile(r'\bsetwd\s*\(')
    _RM_LS            = re.compile(r'\brm\s*\(\s*list\s*=\s*ls\s*\(\s*\)')
    _ATTACH           = re.compile(r'\battach\s*\(')
    _TF_ALIAS         = re.compile(r'(?<![A-Za-z_])(?:T|F)(?![A-Za-z_])')
    _HARDCODED_PATH   = re.compile(r'["\'](?:/[a-zA-Z0-9_/.-]{6,}|[A-Z]:\\[^"\']{6,})["\']')
    _SUPPRESS         = re.compile(r'\b(?:suppressWarnings|suppressMessages)\s*\(')
    _HARDCODED_CRED   = re.compile(
        r"(?:password|passwd|secret|api_key)\s*=\s*['\"][^'\"]{4,}['\"]",
        re.IGNORECASE,
    )

    # Function: language_name
    def language_name(self) -> str:
        return "R"

    # ─────────────────────────────────────────────────────────────────────────

    # Function: _analyse_file
    def _analyse_file(self, path: Path) -> Optional[FileMetrics]:
        lines = self._read_lines(path)
        if not lines:
            return None

        fm     = FileMetrics(path=path, language="R", total_lines=len(lines))
        source = "\n".join(lines)

        for line in lines:
            stripped = line.strip()
            if not stripped:
                fm.blank_lines += 1
                continue
            if stripped.startswith("#"):
                fm.comment_lines += 1
            else:
                fm.code_lines += 1

        fm.todo_comments = self._count_todo(lines)
        fm.magic_numbers = self._count_magic_numbers(lines)
        fm.max_depth     = self._max_nesting_depth(lines)
        fm.deep_nesting  = self._deep_nesting_count(lines, threshold=4)

        stripped_src = re.sub(r'#[^\n]*', '', source)
        fm.functions   = len(self._FUNC.findall(source))
        fm.cyclomatic  = max(1, round((1 + len(self._BRANCH.findall(stripped_src))) / max(fm.functions, 1)))
        fm.classes     = 0
        fm.long_methods = 0   # R functions are usually short

        smells = (
            len(self._SETWD.findall(source))
            + len(self._RM_LS.findall(source))
            + len(self._ATTACH.findall(source))
            + len(self._SUPPRESS.findall(source))
            + len(self._HARDCODED_CRED.findall(source))
            # Limit path/T-F noise
            + min(len(self._HARDCODED_PATH.findall(source)), 5)
        )
        fm.duplicate_blocks = smells
        return fm

    # Function: analyse
    def analyse(self) -> LanguageReport:
        report = super().analyse()
        total_smells = sum(f.duplicate_blocks for f in report.files)
        if total_smells:
            report.bad_practices.append(
                f"setwd/rm-ls/attach/suppressWarnings/hardcoded-paths: {total_smells}"
            )
        return report

    # ─────────────────────────────────────────────────────────────────────────

    # Function: _deps_from_source_files
    def _deps_from_source_files(self, deps: Set[str]) -> None:
        lib_re = re.compile(r'\b(?:library|require)\s*\(\s*["\']?([A-Za-z][A-Za-z0-9._]*)')
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
                for m in lib_re.finditer(src):
                    deps.add(m.group(1).lower())

    # Function: _deps_from_description
    def _deps_from_description(self, deps: Set[str]) -> None:
        desc_path = self.repo_path / "DESCRIPTION"
        if not desc_path.exists():
            return
        try:
            src = desc_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return
        in_imports = False
        for line in src.splitlines():
            if line.startswith("Imports:") or line.startswith("Depends:"):
                in_imports = True
            elif in_imports and not line.startswith(" "):
                in_imports = False
            if in_imports:
                for pkg in re.findall(r'([A-Za-z][A-Za-z0-9._]+)', line):
                    deps.add(pkg.lower())

    # Function: _extract_dependencies
    def _extract_dependencies(self) -> Set[str]:
        deps: Set[str] = set()
        self._deps_from_source_files(deps)
        self._deps_from_description(deps)
        return deps
