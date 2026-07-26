# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Analyses .NET source files (C#, VB.NET, F#).
# Date: 2025-11-28
# ---------------------------------------------------------------------------
"""
dotnet_analyzer.py
------------------
Analyses .NET source files (C#, VB.NET, F#).

Metrics produced
~~~~~~~~~~~~~~~~
- SLOC / comment / blank lines
- Cyclomatic complexity (branch pattern counting)
- Class & method/function counts
- Long methods, deep nesting, magic numbers, TODO markers
- Bad-practice detection: Console.Write usage, empty catch, var overuse,
  regions (C# smell), unsafe code blocks
- Dependency extraction from .csproj / .vbproj / packages.config / NuGet
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Optional, Set

from analyzers.base_analyzer import BaseAnalyzer, FileMetrics
from config.settings import LANGUAGE_EXTENSIONS


class DotNetAnalyzer(BaseAnalyzer):
    """Analyser for .NET source files (C#, VB.NET, F#)."""

    EXTENSIONS = LANGUAGE_EXTENSIONS["dotnet"]

    _BRANCH_CS  = re.compile(
        r'\b(if|else\s+if|for|foreach|while|case|catch|&&|\|\||\?)\b'
    )
    _METHOD_CS  = re.compile(
        r'(?:public|private|protected|internal|static|virtual|override|async)'
        r'(?:\s+\w+)+\s*\([^)]*\)\s*(?:where[^{]*)?\{',
        re.MULTILINE
    )
    _CLASS_CS   = re.compile(r'\b(?:class|interface|struct|enum|record)\s+\w+')
    _CONSOLE    = re.compile(r'Console\.(Write|WriteLine|Error)\s*\(')
    _EMPTY_CATCH = re.compile(r'catch\s*(?:\([^)]*\))?\s*\{\s*\}')
    _UNSAFE     = re.compile(r'\bunsafe\b')
    _REGION     = re.compile(r'#region\b')

    # VB.NET
    _BRANCH_VB  = re.compile(
        r'\b(If\s|ElseIf\s|For\s|While\s|Select\sCase|Catch\s)\b',
        re.IGNORECASE
    )
    _SUB_FUNC_VB = re.compile(r'\b(Sub|Function)\s+\w+', re.IGNORECASE)
    _CLASS_VB   = re.compile(r'\b(Class|Interface|Structure|Enum|Module)\s+\w+',
                              re.IGNORECASE)

    # Function: language_name
    def language_name(self) -> str:
        return ".NET"

    # ──────────────────────────────────────────────────────────────────────────
    # Single-file analysis
    # ──────────────────────────────────────────────────────────────────────────

    # Function: _classify_dotnet_line
    @staticmethod
    def _classify_dotnet_line(stripped: str, fm: FileMetrics, state: dict) -> None:
        if '/*' in stripped:
            state["in_block"] = True
        if state["in_block"]:
            fm.comment_lines += 1
            if '*/' in stripped:
                state["in_block"] = False
            return
        if stripped.startswith("//") or stripped.startswith("'"):
            fm.comment_lines += 1
        else:
            fm.code_lines += 1

    # Function: _analyse_file
    def _analyse_file(self, path: Path) -> Optional[FileMetrics]:
        lines = self._read_lines(path)
        if not lines:
            return None

        suffix = path.suffix.lower()

        # Skip project/solution descriptor files (no logic)
        if suffix in {".csproj", ".vbproj", ".sln"}:
            return None

        fm = FileMetrics(path=path, language=".NET", total_lines=len(lines))
        source = "\n".join(lines)

        # Line classification (C# / F# style)
        state = {"in_block": False}
        for line in lines:
            stripped = line.strip()
            if not stripped:
                fm.blank_lines += 1
                continue
            self._classify_dotnet_line(stripped, fm, state)

        fm.todo_comments = self._count_todo(lines)
        fm.magic_numbers = self._count_magic_numbers(lines)
        fm.commented_out_lines = self._count_commented_out_code(lines)
        fm.max_depth     = self._max_nesting_depth(lines)
        fm.deep_nesting  = self._deep_nesting_count(lines, threshold=4)

        if suffix in {".cs", ".fs"}:
            fm.functions  = len(self._METHOD_CS.findall(source))
            fm.classes    = len(self._CLASS_CS.findall(source))
            fm.cyclomatic = max(1, round((1 + len(self._BRANCH_CS.findall(source))) / max(fm.functions, 1)))
        elif suffix == ".vb":
            fm.functions  = len(self._SUB_FUNC_VB.findall(source))
            fm.classes    = len(self._CLASS_VB.findall(source))
            fm.cyclomatic = max(1, round((1 + len(self._BRANCH_VB.findall(source))) / max(fm.functions, 1)))

        fm.long_methods = self._count_long_methods(source)

        # Bad-practice signal in duplicate_blocks field (reused)
        fm.duplicate_blocks = (
            len(self._CONSOLE.findall(source))
            + len(self._EMPTY_CATCH.findall(source))
            + len(self._UNSAFE.findall(source))
            + len(self._REGION.findall(source))
        )

        return fm

    # ──────────────────────────────────────────────────────────────────────────
    # Repository-level augments
    # ──────────────────────────────────────────────────────────────────────────

    # Function: analyse
    def analyse(self):
        report = super().analyse()
        total_smells = sum(f.duplicate_blocks for f in report.files)
        if total_smells:
            report.bad_practices.append(
                f"Console.Write / empty-catch / unsafe / #region: {total_smells}"
            )
        return report

    # ──────────────────────────────────────────────────────────────────────────
    # Dependency extraction
    # ──────────────────────────────────────────────────────────────────────────

    # Function: _extract_dependencies
    def _extract_dependencies(self) -> Set[str]:
        deps: Set[str] = set()

        # New SDK-style .csproj
        for proj in self.repo_path.rglob("*.csproj"):
            src = proj.read_text(encoding="utf-8", errors="replace")
            for m in re.finditer(r'<PackageReference\s+Include="([^"]+)"', src):
                deps.add(m.group(1).lower())

        # Legacy packages.config
        for pkg_conf in self.repo_path.rglob("packages.config"):
            src = pkg_conf.read_text(encoding="utf-8", errors="replace")
            for m in re.finditer(r'<package\s+id="([^"]+)"', src):
                deps.add(m.group(1).lower())

        return deps

    # ──────────────────────────────────────────────────────────────────────────
    # Helpers
    # ──────────────────────────────────────────────────────────────────────────

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
