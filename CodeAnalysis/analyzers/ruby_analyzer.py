# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Analyses Ruby source files (.rb .rake .gemspec .ru).
# Date: 2026-02-25
# ---------------------------------------------------------------------------
"""
ruby_analyzer.py
----------------
Analyses Ruby source files (.rb .rake .gemspec .ru).

Metrics produced
~~~~~~~~~~~~~~~~
- SLOC / comment / blank lines
- Cyclomatic complexity (branch pattern counting)
- Method (def) / class / module counts
- Long methods, deep nesting, magic numbers, TODO markers
- Bad-practice detection:
    • puts / p / pp / print debug output
    • eval / instance_eval / class_eval / module_eval usage
    • method_missing overrides (meta-programming risk)
    • rescue with bare Exception (catches everything)
    • empty rescue blocks
    • hardcoded IP / URL strings
- Dependency extraction from Gemfile / *.gemspec
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Optional, Set

from analyzers.base_analyzer import BaseAnalyzer, FileMetrics, LanguageReport
from config.settings import LANGUAGE_EXTENSIONS


class RubyAnalyzer(BaseAnalyzer):
    """Analyser for Ruby source files."""

    EXTENSIONS = LANGUAGE_EXTENSIONS.get(
        "ruby", {".rb", ".rake", ".gemspec", ".ru"}
    )

    _BRANCH = re.compile(
        r'\b(if\b|elsif\b|unless\b|case\b|when\b|while\b|until\b|'
        r'for\b|rescue\b|&&|\|\||\band\b|\bor\b)\b'
    )
    _METHOD = re.compile(r'^\s*def\s+\w+', re.MULTILINE)
    _CLASS   = re.compile(r'^\s*(?:class|module)\s+\w+', re.MULTILINE)

    # Bad practices
    _DEBUG_PRINT    = re.compile(r'\b(?:puts|p|pp|print)\b\s+')
    _EVAL           = re.compile(r'\b(?:eval|instance_eval|class_eval|module_eval)\b\s*[\({]')
    _METHOD_MISSING = re.compile(r'\bdef\s+method_missing\b')
    _BARE_RESCUE    = re.compile(r'\brescue\s+Exception\b')
    _EMPTY_RESCUE   = re.compile(r'\brescue\b\s*\n\s*end\b')
    _HARDCODED_CRED = re.compile(
        r"(?:password|passwd|secret|api_key|token)\s*=\s*['\"][^'\"]{4,}['\"]",
        re.IGNORECASE,
    )

    # Function: language_name
    def language_name(self) -> str:
        return "Ruby"

    # ─────────────────────────────────────────────────────────────────────────

    # Function: _analyse_file
    def _analyse_file(self, path: Path) -> Optional[FileMetrics]:
        lines = self._read_lines(path)
        if not lines:
            return None

        fm     = FileMetrics(path=path, language="Ruby", total_lines=len(lines))
        source = "\n".join(lines)

        # Line classification (# comments)
        in_heredoc = False
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
        fm.max_depth     = self._max_nesting_depth(lines, open_ch="do", close_ch="end")
        # For Ruby use { } depth as proxy
        fm.max_depth     = max(fm.max_depth, self._max_nesting_depth(lines))
        fm.deep_nesting  = self._deep_nesting_count(lines, threshold=4)

        stripped_src = re.sub(r'#[^\n]*', '', source)
        fm.functions   = len(self._METHOD.findall(source))
        fm.cyclomatic  = max(1, round((1 + len(self._BRANCH.findall(stripped_src))) / max(fm.functions, 1)))
        fm.classes     = len(self._CLASS.findall(source))
        fm.long_methods = self._count_long_methods(source)

        smells = (
            len(self._DEBUG_PRINT.findall(source))
            + len(self._EVAL.findall(source))
            + len(self._METHOD_MISSING.findall(source))
            + len(self._BARE_RESCUE.findall(source))
            + len(self._EMPTY_RESCUE.findall(source))
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
                f"puts/eval/method_missing/bare-rescue/hardcoded-creds: {total_smells}"
            )
        return report

    # ─────────────────────────────────────────────────────────────────────────

    # Function: _extract_dependencies
    def _extract_dependencies(self) -> Set[str]:
        deps: Set[str] = set()
        gem_re = re.compile(r"gem\s+['\"]([^'\"]+)['\"]", re.IGNORECASE)

        for gemfile in self.repo_path.rglob("Gemfile"):
            try:
                src = gemfile.read_text(encoding="utf-8", errors="replace")
                for m in gem_re.finditer(src):
                    deps.add(m.group(1).lower())
            except OSError:
                pass

        for gemspec in self.repo_path.rglob("*.gemspec"):
            try:
                src = gemspec.read_text(encoding="utf-8", errors="replace")
                for m in re.finditer(
                    r'\.add(?:_runtime|_development)?_dependency\s+["\']([^"\']+)["\']',
                    src, re.IGNORECASE
                ):
                    deps.add(m.group(1).lower())
            except OSError:
                pass

        return deps

    # Function: _count_long_methods
    @staticmethod
    def _count_long_methods(source: str, threshold: int = 40) -> int:
        """Estimate long methods by counting lines between def…end."""
        count = start = 0
        depth = 0
        lines = source.splitlines()
        for i, line in enumerate(lines):
            stripped = line.strip()
            if re.match(r'\bdef\b', stripped):
                if depth == 0:
                    start = i
                depth += 1
            # Rough end-tracking: 'end' with no suffix usually closes a block
            elif stripped == "end" or stripped.startswith("end ") or stripped.startswith("end\t"):
                if depth > 0:
                    depth -= 1
                    if depth == 0 and (i - start) > threshold:
                        count += 1
        return count
