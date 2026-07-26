# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Analyses Rust source files (.rs).
# Date: 2025-11-21
# ---------------------------------------------------------------------------
"""
rust_analyzer.py
----------------
Analyses Rust source files (.rs).

Metrics produced
~~~~~~~~~~~~~~~~
- SLOC / comment / blank lines
- Cyclomatic complexity (branch pattern counting)
- Function (fn) / struct / enum / trait / impl counts
- Long functions, deep nesting, magic numbers, TODO markers
- Bad-practice detection:
    • unwrap() / expect() calls (panic on None/Err)
    • unsafe blocks
    • clone() overuse (may indicate ownership misuse)
    • TODO / unimplemented! / todo! macros
    • hardcoded secrets
- Dependency extraction from Cargo.toml
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Optional, Set

from analyzers.base_analyzer import BaseAnalyzer, FileMetrics, LanguageReport
from config.settings import LANGUAGE_EXTENSIONS


class RustAnalyzer(BaseAnalyzer):
    """Analyser for Rust source files."""

    EXTENSIONS = LANGUAGE_EXTENSIONS.get("rust", {".rs"})

    _BRANCH = re.compile(
        r'\b(if\b|else\s+if\b|match\b|for\b|while\b|loop\b|'
        r'&&|\|\|)\b'
    )
    _FN      = re.compile(r'\bfn\s+\w+\s*(?:<[^>]*>)?\s*\(')
    _STRUCT  = re.compile(r'\b(?:struct|enum|union)\s+\w+')
    _TRAIT   = re.compile(r'\btrait\s+\w+')
    _IMPL    = re.compile(r'\bimpl\b')

    # Bad practices
    _UNWRAP        = re.compile(r'\.(unwrap|expect)\s*\(')
    _UNSAFE        = re.compile(r'\bunsafe\s*\{')
    _CLONE         = re.compile(r'\.clone\s*\(\s*\)')
    _TODO_MACRO    = re.compile(r'\b(?:todo!|unimplemented!)\s*\(')
    _HARDCODED_CRED = re.compile(
        r"(?:password|passwd|secret|api_key|token)\s*=\s*\"[^\"]{4,}\"",
        re.IGNORECASE,
    )

    # Function: language_name
    def language_name(self) -> str:
        return "Rust"

    # ─────────────────────────────────────────────────────────────────────────

    # Function: _analyse_file
    def _analyse_file(self, path: Path) -> Optional[FileMetrics]:
        lines = self._read_lines(path)
        if not lines:
            return None

        fm     = FileMetrics(path=path, language="Rust", total_lines=len(lines))
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
        fm.functions   = len(self._FN.findall(source))
        fm.cyclomatic  = max(1, round((1 + len(self._BRANCH.findall(stripped_src))) / max(fm.functions, 1)))
        fm.classes     = (len(self._STRUCT.findall(source))
                          + len(self._TRAIT.findall(source))
                          + len(self._IMPL.findall(source)))
        fm.long_methods = self._count_long_methods(source)

        smells = (
            len(self._UNWRAP.findall(source))
            + len(self._UNSAFE.findall(source))
            + len(self._CLONE.findall(source))
            + len(self._TODO_MACRO.findall(source))
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
                f"unwrap/unsafe/excessive-clone/todo!/hardcoded-creds: {total_smells}"
            )
        return report

    # ─────────────────────────────────────────────────────────────────────────

    # Function: _parse_cargo_toml
    @staticmethod
    def _parse_cargo_toml(src: str, deps: Set[str]) -> None:
        in_deps = False
        for line in src.splitlines():
            stripped = line.strip()
            if stripped in ("[dependencies]", "[dev-dependencies]",
                            "[build-dependencies]"):
                in_deps = True
                continue
            if stripped.startswith("[") and stripped != "[dependencies]":
                in_deps = False
            if in_deps:
                m = re.match(r'^(\w[\w\-]*)[\s=]', stripped)
                if m:
                    deps.add(m.group(1).lower())

    # Function: _extract_dependencies
    def _extract_dependencies(self) -> Set[str]:
        deps: Set[str] = set()
        for cargo in self.repo_path.rglob("Cargo.toml"):
            try:
                src = cargo.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            self._parse_cargo_toml(src, deps)
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
