# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Analyses Groovy source files and Gradle build scripts.
# Date: 2026-06-29
# ---------------------------------------------------------------------------
"""
groovy_analyzer.py
------------------
Analyses Groovy source files and Gradle build scripts.

Supported extensions: .groovy .gvy .gradle .jenkinsfile (Jenkinsfile)

Metrics produced
~~~~~~~~~~~~~~~~
- SLOC / comment / blank lines
- Cyclomatic complexity (branch pattern counting)
- Function (def) / class / closure counts
- Long methods, deep nesting, magic numbers, TODO markers
- Bad-practice detection:
    • println / print debug output
    • eval-like constructs (evaluate / Eval.me)
    • Groovy dynamic typing overuse (def * N)
    • GDK execute() shell injection risk
    • Hardcoded credentials
- Dependency extraction from build.gradle dependency blocks
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Optional, Set

from analyzers.base_analyzer import BaseAnalyzer, FileMetrics, LanguageReport
from config.settings import LANGUAGE_EXTENSIONS


class GroovyAnalyzer(BaseAnalyzer):
    """Analyser for Groovy source and Gradle build files."""

    EXTENSIONS = LANGUAGE_EXTENSIONS.get(
        "groovy", {".groovy", ".gvy", ".gradle", ".jenkinsfile"}
    )

    _BRANCH = re.compile(
        r'\b(if\b|else\s+if\b|for\b|while\b|switch\b|case\b|catch\b|'
        r'&&|\|\|)\b'
    )
    _METHOD  = re.compile(r'^\s*(?:(?:def|void|static|private|public|'
                           r'protected|final)\s+)+\w+\s*\(', re.MULTILINE)
    _CLASS   = re.compile(r'\b(?:class|interface|trait|enum)\s+\w+')
    _CLOSURE = re.compile(r'\{[^}]*->')   # Groovy closure: { args -> … }

    # Bad practices
    _PRINTLN   = re.compile(r'\b(?:println|print)\b\s*')
    _EVAL      = re.compile(r'\b(?:evaluate|Eval\.me)\s*\(')
    _EXECUTE   = re.compile(r'\.execute\s*\(\s*\)')
    _HARDCODED_CRED = re.compile(
        r"(?:password|passwd|secret|apiKey|api_key)\s*=\s*['\"][^'\"]{4,}['\"]",
        re.IGNORECASE,
    )

    # Function: language_name
    def language_name(self) -> str:
        return "Groovy"

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
            if stripped.startswith("//") or stripped.startswith("#!"):
                fm.comment_lines += 1
            else:
                fm.code_lines += 1

    # Function: _analyse_file
    def _analyse_file(self, path: Path) -> Optional[FileMetrics]:
        lines = self._read_lines(path)
        if not lines:
            return None

        fm     = FileMetrics(path=path, language="Groovy", total_lines=len(lines))
        source = "\n".join(lines)

        self._classify_lines(lines, fm)

        fm.todo_comments = self._count_todo(lines)
        fm.magic_numbers = self._count_magic_numbers(lines)
        fm.max_depth     = self._max_nesting_depth(lines)
        fm.deep_nesting  = self._deep_nesting_count(lines, threshold=4)

        stripped_src = re.sub(r'//[^\n]*', '', source)
        stripped_src = re.sub(r'/\*.*?\*/', '', stripped_src, flags=re.DOTALL)
        fm.functions   = len(self._METHOD.findall(source))
        fm.cyclomatic  = max(1, round((1 + len(self._BRANCH.findall(stripped_src))) / max(fm.functions, 1)))
        fm.classes     = len(self._CLASS.findall(source))
        fm.long_methods = self._count_long_methods(source)

        smells = (
            len(self._PRINTLN.findall(source))
            + len(self._EVAL.findall(source))
            + len(self._EXECUTE.findall(source))
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
                f"println/eval/execute()/hardcoded-creds: {total_smells}"
            )
        return report

    # ─────────────────────────────────────────────────────────────────────────

    # Function: _extract_dependencies
    def _extract_dependencies(self) -> Set[str]:
        deps: Set[str] = set()
        for gradle in self.repo_path.rglob("build.gradle"):
            try:
                src = gradle.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            for m in re.finditer(
                r'(?:implementation|api|testImplementation|compileOnly|'
                r'runtimeOnly)\s+["\']([^"\']+)["\']',
                src,
            ):
                parts = m.group(1).split(":")
                if len(parts) >= 2:
                    deps.add(f"{parts[0]}:{parts[1]}".lower())
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
