# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Analyses Kotlin source files (.kt .kts).
# Date: 2026-01-05
# ---------------------------------------------------------------------------
"""
kotlin_analyzer.py
------------------
Analyses Kotlin source files (.kt .kts).

Metrics produced
~~~~~~~~~~~~~~~~
- SLOC / comment / blank lines
- Cyclomatic complexity (branch pattern counting)
- Function (fun) / class / object / interface / data class counts
- Long functions, deep nesting, magic numbers, TODO markers
- Bad-practice detection:
    • !! (null-assertion operator — KotlinNullPointerException risk)
    • runBlocking / Thread.sleep in non-test code (coroutine blocking)
    • GlobalScope usage
    • System.out.println / println debug output
    • TODO() / FIXME placeholders
    • hardcoded credentials
- Dependency extraction from build.gradle / build.gradle.kts / pom.xml
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Optional, Set

from analyzers.base_analyzer import BaseAnalyzer, FileMetrics, LanguageReport
from config.settings import LANGUAGE_EXTENSIONS


class KotlinAnalyzer(BaseAnalyzer):
    """Analyser for Kotlin source files."""

    EXTENSIONS = LANGUAGE_EXTENSIONS.get("kotlin", {".kt", ".kts"})

    _BRANCH = re.compile(
        r'\b(if\b|else\s+if\b|when\b|for\b|while\b|do\b|catch\b|'
        r'&&|\|\|)\b'
    )
    _FUN      = re.compile(r'^\s*(?:(?:private|public|protected|internal|'
                            r'override|suspend|inline|open|abstract|final)\s+)*'
                            r'fun\s+\w+', re.MULTILINE)
    _CLASS    = re.compile(r'\b(?:class|object|interface|data\s+class|'
                            r'sealed\s+class|enum\s+class|abstract\s+class)\s+\w+')

    # Bad practices
    _NULL_BANG     = re.compile(r'!!')
    _RUN_BLOCKING  = re.compile(r'\b(?:runBlocking|Thread\.sleep)\b\s*[\({]')
    _GLOBAL_SCOPE  = re.compile(r'\bGlobalScope\s*\.')
    _PRINTLN       = re.compile(r'\b(?:println|print)\s*\(')
    _TODO_FN       = re.compile(r'\bTODO\s*\(')
    _HARDCODED_CRED = re.compile(
        r"(?:password|passwd|secret|apiKey|api_key|token)\s*=\s*\"[^\"]{4,}\"",
        re.IGNORECASE,
    )

    # Function: language_name
    def language_name(self) -> str:
        return "Kotlin"

    # ─────────────────────────────────────────────────────────────────────────

    # Function: _analyse_file
    def _analyse_file(self, path: Path) -> Optional[FileMetrics]:
        lines = self._read_lines(path)
        if not lines:
            return None

        fm     = FileMetrics(path=path, language="Kotlin", total_lines=len(lines))
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
        fm.functions   = len(self._FUN.findall(source))
        fm.cyclomatic  = max(1, round((1 + len(self._BRANCH.findall(stripped_src))) / max(fm.functions, 1)))
        fm.classes     = len(self._CLASS.findall(source))
        fm.long_methods = self._count_long_methods(source)

        smells = (
            len(self._NULL_BANG.findall(source))
            + len(self._RUN_BLOCKING.findall(source))
            + len(self._GLOBAL_SCOPE.findall(source))
            + len(self._PRINTLN.findall(source))
            + len(self._TODO_FN.findall(source))
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
                f"!!/runBlocking/GlobalScope/println/TODO()/hardcoded-creds: {total_smells}"
            )
        return report

    # ─────────────────────────────────────────────────────────────────────────

    # Function: _extract_dependencies
    def _extract_dependencies(self) -> Set[str]:
        deps: Set[str] = set()

        # Gradle (Groovy and Kotlin DSL)
        for gradle in list(self.repo_path.rglob("build.gradle"))  \
                    + list(self.repo_path.rglob("build.gradle.kts")):
            try:
                src = gradle.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            for m in re.finditer(
                r'(?:implementation|api|testImplementation|'
                r'compileOnly|runtimeOnly)\s*["\']([^"\']+)["\']',
                src,
            ):
                parts = m.group(1).split(":")
                if len(parts) >= 2:
                    deps.add(f"{parts[0]}:{parts[1]}".lower())

        # Maven pom.xml
        for pom in self.repo_path.rglob("pom.xml"):
            try:
                src = pom.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            for gid, aid in re.findall(
                r'<groupId>([^<]+)</groupId>\s*<artifactId>([^<]+)</artifactId>', src
            ):
                deps.add(f"{gid.lower()}:{aid.lower()}")

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
