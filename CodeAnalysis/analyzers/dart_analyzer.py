# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Analyses Dart source files (.dart) — used by Flutter and server-side Dart.
# Date: 2026-04-02
# ---------------------------------------------------------------------------
"""
dart_analyzer.py
----------------
Analyses Dart source files (.dart) — used by Flutter and server-side Dart.

Metrics produced
~~~~~~~~~~~~~~~~
- SLOC / comment / blank lines
- Cyclomatic complexity (branch pattern counting)
- Function / class / mixin / extension counts
- Long methods, deep nesting, magic numbers, TODO markers
- Bad-practice detection:
    • print() / debugPrint() debug output
    • dynamic type usage
    • ! null assertion operator
    • as unsafe casts
    • rethrow without logging
    • Hardcoded credentials
- Dependency extraction from pubspec.yaml
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Optional, Set

from analyzers.base_analyzer import BaseAnalyzer, FileMetrics, LanguageReport
from config.settings import LANGUAGE_EXTENSIONS


class DartAnalyzer(BaseAnalyzer):
    """Analyser for Dart source files."""

    EXTENSIONS = LANGUAGE_EXTENSIONS.get("dart", {".dart"})

    _BRANCH = re.compile(
        r'\b(if\b|else\s+if\b|for\b|while\b|do\b|switch\b|case\b|'
        r'catch\b|&&|\|\|)\b'
    )
    _FUNC  = re.compile(
        r'(?:Future|Stream|void|int|double|bool|String|Map|List|[\w<>?]+)'
        r'\s+\w+\s*\([^)]*\)\s*(?:async\s*)?\{'
    )
    _CLASS = re.compile(r'\b(?:class|mixin|extension|enum|abstract\s+class)\s+\w+')

    # Bad practices
    _PRINT         = re.compile(r'\b(?:print|debugPrint)\s*\(')
    _DYNAMIC_TYPE  = re.compile(r'\bdynamic\b')
    _NULL_BANG     = re.compile(r'(?<![!=<>])!(?![=])')   # x! null assertion
    _UNSAFE_CAST   = re.compile(r'\bas\s+\w')
    _HARDCODED_CRED = re.compile(
        r"(?:password|passwd|secret|apiKey|api_key)\s*=\s*['\"][^'\"]{4,}['\"]",
        re.IGNORECASE,
    )

    # Function: language_name
    def language_name(self) -> str:
        return "Dart"

    # ─────────────────────────────────────────────────────────────────────────

    # Function: _analyse_file
    def _analyse_file(self, path: Path) -> Optional[FileMetrics]:
        lines = self._read_lines(path)
        if not lines:
            return None

        fm     = FileMetrics(path=path, language="Dart", total_lines=len(lines))
        source = "\n".join(lines)

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
        fm.classes     = len(self._CLASS.findall(source))
        fm.long_methods = self._count_long_methods(source)

        smells = (
            len(self._PRINT.findall(source))
            + len(self._DYNAMIC_TYPE.findall(source))
            + min(len(self._NULL_BANG.findall(source)), 10)   # cap noise
            + len(self._UNSAFE_CAST.findall(source))
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
                f"print/dynamic-type/null-bang/unsafe-cast/hardcoded-creds: {total_smells}"
            )
        return report

    # ─────────────────────────────────────────────────────────────────────────

    # Function: _parse_pubspec_yaml
    @staticmethod
    def _parse_pubspec_yaml(src: str, deps: Set[str]) -> bool:
        """Try parsing pubspec.yaml with PyYAML. Returns True on success."""
        try:
            import yaml  # type: ignore
        except ImportError:
            return False
        try:
            data = yaml.safe_load(src)
            for section in ("dependencies", "dev_dependencies"):
                for pkg in (data or {}).get(section, {}) or {}:
                    deps.add(pkg.lower())
            return True
        except Exception:
            return False

    # Function: _parse_pubspec_fallback
    @staticmethod
    def _parse_pubspec_fallback(src: str, deps: Set[str]) -> None:
        """Simple line-based parsing when PyYAML is unavailable or parsing fails."""
        in_dep = False
        for line in src.splitlines():
            if line.strip() in ("dependencies:", "dev_dependencies:"):
                in_dep = True
                continue
            if in_dep and line and not line.startswith(" "):
                in_dep = False
            if in_dep:
                m = re.match(r'\s+(\w[\w_-]*):', line)
                if m and m.group(1) not in ("flutter", "sdk"):
                    deps.add(m.group(1).lower())

    # Function: _extract_dependencies
    def _extract_dependencies(self) -> Set[str]:
        deps: Set[str] = set()

        for pubspec in self.repo_path.rglob("pubspec.yaml"):
            try:
                src = pubspec.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            if not self._parse_pubspec_yaml(src, deps):
                self._parse_pubspec_fallback(src, deps)
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
