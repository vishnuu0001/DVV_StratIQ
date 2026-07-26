# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Analyses Scala source files (.scala .sc).
# Date: 2026-05-30
# ---------------------------------------------------------------------------
"""
scala_analyzer.py
-----------------
Analyses Scala source files (.scala .sc).

Metrics produced
~~~~~~~~~~~~~~~~
- SLOC / comment / blank lines
- Cyclomatic complexity (branch pattern counting)
- Function (def) / class / object / trait / case class counts
- Long methods, deep nesting, magic numbers, TODO markers
- Bad-practice detection:
    • var declarations (mutable state)
    • null usage (prefer Option)
    • asInstanceOf (unsafe cast)
    • throw new without typed error hierarchy
    • System.out.println / println debug output
    • blocking Await.result / Await.ready calls
    • hardcoded credentials
- Dependency extraction from build.sbt / project/Dependencies.scala
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Optional, Set

from analyzers.base_analyzer import BaseAnalyzer, FileMetrics, LanguageReport
from config.settings import LANGUAGE_EXTENSIONS


class ScalaAnalyzer(BaseAnalyzer):
    """Analyser for Scala source files."""

    EXTENSIONS = LANGUAGE_EXTENSIONS.get("scala", {".scala", ".sc"})

    _BRANCH = re.compile(
        r'\b(if\b|else\s+if\b|match\b|case\b|for\b|while\b|do\b|catch\b|'
        r'&&|\|\|)\b'
    )
    _DEF    = re.compile(r'^\s*(?:(?:private|protected|override|final|'
                          r'abstract|implicit|lazy)\s+)*def\s+\w+', re.MULTILINE)
    _CLASS  = re.compile(r'\b(?:class|object|trait|case\s+class|'
                          r'abstract\s+class|sealed\s+class|sealed\s+trait)\s+\w+')

    # Bad practices
    _VAR         = re.compile(r'^\s*var\s+\w+', re.MULTILINE)
    _NULL_KW     = re.compile(r'\bnull\b')
    _CAST        = re.compile(r'\.asInstanceOf\s*\[')
    _THROW       = re.compile(r'\bthrow\s+new\b')
    _PRINTLN     = re.compile(r'\b(?:println|print)\s*\(')
    _AWAIT_BLOCK = re.compile(r'\bAwait\s*\.\s*(?:result|ready)\s*\(')
    _HARDCODED_CRED = re.compile(
        r"(?:password|passwd|secret|apiKey)\s*=\s*\"[^\"]{4,}\"",
        re.IGNORECASE,
    )

    # Function: language_name
    def language_name(self) -> str:
        return "Scala"

    # ─────────────────────────────────────────────────────────────────────────

    # Function: _analyse_file
    def _analyse_file(self, path: Path) -> Optional[FileMetrics]:
        lines = self._read_lines(path)
        if not lines:
            return None

        fm     = FileMetrics(path=path, language="Scala", total_lines=len(lines))
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
        fm.functions   = len(self._DEF.findall(source))
        fm.cyclomatic  = max(1, round((1 + len(self._BRANCH.findall(stripped_src))) / max(fm.functions, 1)))
        fm.classes     = len(self._CLASS.findall(source))
        fm.long_methods = self._count_long_methods(source)

        smells = (
            len(self._VAR.findall(source))
            + len(self._NULL_KW.findall(source))
            + len(self._CAST.findall(source))
            + len(self._THROW.findall(source))
            + len(self._PRINTLN.findall(source))
            + len(self._AWAIT_BLOCK.findall(source))
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
                f"var/null/asInstanceOf/Await-block/println/hardcoded-creds: {total_smells}"
            )
        return report

    # ─────────────────────────────────────────────────────────────────────────

    # Function: _extract_dependencies
    def _extract_dependencies(self) -> Set[str]:
        deps: Set[str] = set()
        lib_re = re.compile(
            r'"([^"]+)"\s*%%?\s*"([^"]+)"\s*%'
        )
        for sbt in list(self.repo_path.rglob("build.sbt")) \
                 + list(self.repo_path.rglob("*.sbt")):
            try:
                src = sbt.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            for org, name in lib_re.findall(src):
                deps.add(f"{org.lower()}:{name.lower()}")
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
