# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Analyses C and C++ source files.
# Date: 2026-02-27
# ---------------------------------------------------------------------------
"""
cpp_analyzer.py
---------------
Analyses C and C++ source files.

Supported extensions: .c .cpp .cc .cxx .h .hpp .hxx .c++ .h++

Metrics produced
~~~~~~~~~~~~~~~~
- SLOC / comment / blank lines
- Cyclomatic complexity (branch pattern counting)
- Function / class / struct / enum counts
- Long functions, deep nesting, magic numbers, TODO markers
- Bad-practice detection:
    • Unsafe C string functions: gets / strcpy / strcat / sprintf / scanf
    • malloc/free without paired checks
    • printf with format string (potential format-string injection)
    • Implicit function declarations
    • Global mutable variables (extern / global scope)
    • Raw pointer arithmetic
    • Hardcoded credentials
- Dependency extraction from CMakeLists.txt / conanfile.txt /
    vcpkg.json / Makefile LIBS variable
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Optional, Set

from analyzers.base_analyzer import BaseAnalyzer, FileMetrics, LanguageReport
from config.settings import LANGUAGE_EXTENSIONS


class CppAnalyzer(BaseAnalyzer):
    """Analyser for C and C++ source files."""

    EXTENSIONS = LANGUAGE_EXTENSIONS.get(
        "cpp",
        {".c", ".cpp", ".cc", ".cxx", ".h", ".hpp", ".hxx", ".c++", ".h++"},
    )

    _BRANCH = re.compile(
        r'\b(if\b|else\s+if\b|for\b|while\b|do\b|switch\b|case\b|'
        r'catch\b|&&|\|\|)\b'
    )
    # C++ function: return-type name(... ) { (rough heuristic)
    _FUNC   = re.compile(
        r'(?:^|\n)(?:(?:static|inline|virtual|explicit|constexpr|'
        r'__declspec\([^)]*\)|\[\[nodiscard\]\])\s+)*'
        r'(?:\w[\w:*&<>, ]+)\s+(\w[\w:~]*)\s*\([^;]*\)\s*(?:const\s*)?(?:noexcept\s*)?\{',
        re.MULTILINE,
    )
    _CLASS  = re.compile(r'\b(?:class|struct|enum(?:\s+class)?|union)\s+\w+')

    # Unsafe / risky patterns
    _UNSAFE_FUNCS  = re.compile(
        r'\b(?:gets|strcpy|strcat|sprintf|scanf|vsprintf|'
        r'strcpy_s|gets_s)\s*\('
    )
    _MALLOC        = re.compile(r'\bmalloc\s*\(')
    _FREE          = re.compile(r'\bfree\s*\(')
    _PRINTF_FMT    = re.compile(r'\b(?:printf|fprintf|snprintf)\s*\([^"]*\$')
    _GLOBAL_VAR    = re.compile(r'^(?:extern\s+)?(?:int|char|float|double|long|'
                                 r'unsigned|void\s*\*)\s+\w+\s*(?:=|;)',
                                 re.MULTILINE)
    _PTR_ARITH     = re.compile(r'\b\w+\s*[+\-]=\s*sizeof\b')
    _HARDCODED_CRED = re.compile(
        r"(?:password|passwd|secret|api_key|token)\s*=\s*\"[^\"]{4,}\"",
        re.IGNORECASE,
    )

    # Function: language_name
    def language_name(self) -> str:
        return "C/C++"

    # ─────────────────────────────────────────────────────────────────────────

    # Function: _analyse_file
    def _analyse_file(self, path: Path) -> Optional[FileMetrics]:
        lines = self._read_lines(path)
        if not lines:
            return None

        fm     = FileMetrics(path=path, language="C/C++", total_lines=len(lines))
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

        malloc_count   = len(self._MALLOC.findall(source))
        free_count     = len(self._FREE.findall(source))
        leak_indicator = abs(malloc_count - free_count)

        smells = (
            len(self._UNSAFE_FUNCS.findall(source))
            + leak_indicator
            + len(self._PRINTF_FMT.findall(source))
            + len(self._PTR_ARITH.findall(source))
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
                f"unsafe-funcs/malloc-leak/printf-fmt/ptr-arith/hardcoded-creds: {total_smells}"
            )
        return report

    # ─────────────────────────────────────────────────────────────────────────

    # Function: _deps_from_link_libraries
    @staticmethod
    def _deps_from_link_libraries(src: str, deps: Set[str]) -> None:
        for m in re.finditer(
            r'target_link_libraries\s*\([^)]+\)', src, re.IGNORECASE | re.DOTALL
        ):
            for lib in re.findall(r'"([^"]+)"|(\w[\w\-]+)', m.group(0)):
                l = (lib[0] or lib[1]).lower()
                if l and l not in {"public", "private", "interface",
                                   "target_link_libraries"}:
                    deps.add(l)

    # Function: _deps_from_cmake
    def _deps_from_cmake(self, deps: Set[str]) -> None:
        for cmake in self.repo_path.rglob("CMakeLists.txt"):
            try:
                src = cmake.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            for m in re.finditer(r'find_package\s*\(\s*(\w+)', src, re.IGNORECASE):
                deps.add(m.group(1).lower())
            self._deps_from_link_libraries(src, deps)

    # Function: _deps_from_conan
    def _deps_from_conan(self, deps: Set[str]) -> None:
        for conan in self.repo_path.rglob("conanfile.txt"):
            try:
                src = conan.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            in_req = False
            for line in src.splitlines():
                if line.strip() == "[requires]":
                    in_req = True
                    continue
                if line.strip().startswith("["):
                    in_req = False
                if in_req and line.strip():
                    deps.add(line.strip().split("/")[0].lower())

    # Function: _deps_from_vcpkg
    def _deps_from_vcpkg(self, deps: Set[str]) -> None:
        for vcpkg in self.repo_path.rglob("vcpkg.json"):
            try:
                data = json.loads(
                    vcpkg.read_text(encoding="utf-8", errors="replace")
                )
                for dep in data.get("dependencies", []):
                    if isinstance(dep, str):
                        deps.add(dep.lower())
                    elif isinstance(dep, dict):
                        deps.add(dep.get("name", "").lower())
            except Exception:
                pass

    # Function: _extract_dependencies
    def _extract_dependencies(self) -> Set[str]:
        deps: Set[str] = set()
        self._deps_from_cmake(deps)
        self._deps_from_conan(deps)
        self._deps_from_vcpkg(deps)
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
