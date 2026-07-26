# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Analyses PHP source files (.php .phtml .php3 .php4 .php5 .php7).
# Date: 2025-10-19
# ---------------------------------------------------------------------------
"""
php_analyzer.py
---------------
Analyses PHP source files (.php .phtml .php3 .php4 .php5 .php7).

Metrics produced
~~~~~~~~~~~~~~~~
- SLOC / comment / blank lines
- Cyclomatic complexity (branch pattern counting)
- Function / class / interface / trait counts
- Long methods, deep nesting, magic numbers, TODO markers
- Bad-practice detection:
    • echo / var_dump / print_r debug output
    • mysql_* deprecated functions
    • eval() usage
    • extract() / $$variable variable variables
    • error_reporting(0) suppression
    • hardcoded credentials
    • SQL string concatenation (injection risk indicator)
- Dependency extraction from composer.json
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Optional, Set

from analyzers.base_analyzer import BaseAnalyzer, FileMetrics, LanguageReport
from config.settings import LANGUAGE_EXTENSIONS


class PHPAnalyzer(BaseAnalyzer):
    """Analyser for PHP source files."""

    EXTENSIONS = LANGUAGE_EXTENSIONS.get(
        "php", {".php", ".phtml", ".php3", ".php4", ".php5", ".php7"}
    )

    _BRANCH = re.compile(
        r'\b(if\b|elseif\b|else\s+if\b|for\b|foreach\b|while\b|'
        r'switch\b|case\b|catch\b|&&|\|\|)\b'
    )
    _FUNC   = re.compile(r'\bfunction\s+\w+\s*\(')
    _CLASS  = re.compile(r'\b(?:class|interface|trait|abstract\s+class|enum)\s+\w+')

    # Bad practices
    _DEBUG_PRINT   = re.compile(r'\b(?:echo\s|var_dump\s*\(|print_r\s*\(|print\s)\b')
    _MYSQL_OLD     = re.compile(r'\bmysql_\w+\s*\(')
    _EVAL          = re.compile(r'\beval\s*\(')
    _EXTRACT       = re.compile(r'\bextract\s*\(')
    _VAR_VAR       = re.compile(r'\$\$\w+')
    _ERR_SUPPRESS  = re.compile(r'\berror_reporting\s*\(\s*0\s*\)')
    _SQL_CONCAT    = re.compile(r'(?:SELECT|INSERT|UPDATE|DELETE).*?\.\s*\$', re.IGNORECASE)
    _HARDCODED_CRED = re.compile(
        r"(?:password|passwd|secret|api_key)\s*=\s*[\"'][^\"']{4,}[\"']",
        re.IGNORECASE,
    )

    # Function: language_name
    def language_name(self) -> str:
        return "PHP"

    # ─────────────────────────────────────────────────────────────────────────

    # Function: _analyse_file
    # Function: _classify_lines
    def _classify_lines(self, lines: list, fm: FileMetrics) -> None:
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
            if stripped.startswith("//") or stripped.startswith("#"):
                fm.comment_lines += 1
            else:
                fm.code_lines += 1

    # Function: _analyse_file
    def _analyse_file(self, path: Path) -> Optional[FileMetrics]:
        lines = self._read_lines(path)
        if not lines:
            return None

        fm     = FileMetrics(path=path, language="PHP", total_lines=len(lines))
        source = "\n".join(lines)

        self._classify_lines(lines, fm)

        fm.todo_comments = self._count_todo(lines)
        fm.magic_numbers = self._count_magic_numbers(lines)
        fm.max_depth     = self._max_nesting_depth(lines)
        fm.deep_nesting  = self._deep_nesting_count(lines, threshold=4)

        stripped_src = re.sub(r'//[^\n]*', '', source)
        stripped_src = re.sub(r'/\*.*?\*/', '', stripped_src, flags=re.DOTALL)
        fm.functions   = len(self._FUNC.findall(source))
        fm.cyclomatic  = max(1, round((1 + len(self._BRANCH.findall(stripped_src))) / max(fm.functions, 1)))
        fm.classes     = len(self._CLASS.findall(source))
        fm.long_methods = self._count_long_methods(source)

        smells = (
            len(self._DEBUG_PRINT.findall(source))
            + len(self._MYSQL_OLD.findall(source))
            + len(self._EVAL.findall(source))
            + len(self._EXTRACT.findall(source))
            + len(self._VAR_VAR.findall(source))
            + len(self._ERR_SUPPRESS.findall(source))
            + len(self._SQL_CONCAT.findall(source))
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
                f"echo-debug/mysql_*/eval/extract/var-var/err-suppress/sql-concat/creds: {total_smells}"
            )
        return report

    # ─────────────────────────────────────────────────────────────────────────

    # Function: _extract_dependencies
    # Function: _composer_deps
    @staticmethod
    def _composer_deps(composer: Path, repo_path: Path) -> Set[str]:
        try:
            rel = composer.relative_to(repo_path)
            if "vendor" in rel.parts:
                return set()
        except ValueError:
            return set()
        try:
            data = json.loads(composer.read_text(encoding="utf-8", errors="replace"))
        except Exception:
            return set()
        deps: Set[str] = set()
        for section in ("require", "require-dev"):
            for pkg in data.get(section, {}):
                if pkg != "php":
                    deps.add(pkg.lower())
        return deps

    # Function: _extract_dependencies
    def _extract_dependencies(self) -> Set[str]:
        deps: Set[str] = set()
        for composer in self.repo_path.rglob("composer.json"):
            deps |= self._composer_deps(composer, self.repo_path)
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
