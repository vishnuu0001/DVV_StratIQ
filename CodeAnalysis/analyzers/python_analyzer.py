# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Analyses Python source files using ``ast``, ``radon``, and ``bandit``.
# Date: 2026-04-06
# ---------------------------------------------------------------------------
"""
python_analyzer.py
------------------
Analyses Python source files using ``ast``, ``radon``, and ``bandit``.

Metrics produced
~~~~~~~~~~~~~~~~
- SLOC / comment / blank lines
- Cyclomatic & cognitive complexity (radon)
- Class & function counts (ast)
- Long methods, deep nesting, magic numbers, TODO markers
- Bandit security issues summary
- Dependency extraction from requirements*.txt / pyproject.toml / setup.*
"""
from __future__ import annotations

import ast
import json
import logging
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional, Set

from radon.complexity import cc_visit
from radon.metrics import mi_visit

from analyzers.base_analyzer import BaseAnalyzer, FileMetrics, LanguageReport
from config.settings import LANGUAGE_EXTENSIONS

logger = logging.getLogger(__name__)


class PythonAnalyzer(BaseAnalyzer):
    """Analyser for Python (.py) source files."""

    EXTENSIONS = LANGUAGE_EXTENSIONS["python"]

    # Function: language_name
    def language_name(self) -> str:
        return "Python"

    # ──────────────────────────────────────────────────────────────────────────
    # Single-file analysis
    # ──────────────────────────────────────────────────────────────────────────

    # Function: _analyse_file
    def _analyse_file(self, path: Path) -> Optional[FileMetrics]:
        lines = self._read_lines(path)
        if not lines:
            return None

        fm = FileMetrics(path=path, language="Python", total_lines=len(lines))

        # Line classification
        for line in lines:
            stripped = line.strip()
            if not stripped:
                fm.blank_lines += 1
            elif stripped.startswith("#"):
                fm.comment_lines += 1
            else:
                fm.code_lines += 1

        fm.todo_comments  = self._count_todo(lines)
        fm.magic_numbers  = self._count_magic_numbers(lines)
        fm.commented_out_lines = self._count_commented_out_code(lines)
        fm.max_depth      = self._max_nesting_depth(lines, ":", "")   # indentation proxy
        fm.deep_nesting   = self._deep_nesting_count_python(lines)

        # AST-based metrics
        source = path.read_text(encoding="utf-8", errors="replace")
        try:
            tree = ast.parse(source, filename=str(path))
            fm.functions = sum(
                1 for n in ast.walk(tree)
                if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
            )
            fm.classes = sum(
                1 for n in ast.walk(tree) if isinstance(n, ast.ClassDef)
            )
            # Long methods (> 40 lines)
            fm.long_methods = sum(
                1 for n in ast.walk(tree)
                if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                and hasattr(n, "end_lineno")
                and (n.end_lineno - n.lineno) > 40
            )
        except SyntaxError as exc:
            fm.error = f"AST parse error: {exc}"
            return fm

        # Cyclomatic complexity via radon
        try:
            blocks = cc_visit(source)
            if blocks:
                fm.cyclomatic = max(b.complexity for b in blocks)
        except Exception:   # noqa: BLE001
            pass

        # Maintainability Index via radon (0–100; invert to complementary)
        try:
            mi = mi_visit(source, multi=True)
            # MI < 65 → highly complex, map to higher cognitive score
            fm.cognitive = max(0, int(100 - mi))
        except Exception:   # noqa: BLE001
            pass

        return fm

    # ──────────────────────────────────────────────────────────────────────────
    # Repository-level analysis augments
    # ──────────────────────────────────────────────────────────────────────────

    # Function: analyse
    def analyse(self) -> LanguageReport:
        report = super().analyse()
        report = self._run_bandit(report)
        return report

    # Function: _run_bandit
    def _run_bandit(self, report: LanguageReport) -> LanguageReport:
        """Run bandit security scanner and append findings to bad_practices."""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "bandit", "-r", str(self.repo_path),
                 "-f", "json", "-q", "--exit-zero"],
                capture_output=True, text=True, timeout=120
            )
            data = json.loads(result.stdout or "{}")
            issues = data.get("results", [])
            high   = sum(1 for i in issues if i.get("issue_severity") == "HIGH")
            medium = sum(1 for i in issues if i.get("issue_severity") == "MEDIUM")
            low    = sum(1 for i in issues if i.get("issue_severity") == "LOW")
            if issues:
                report.bad_practices.append(
                    f"Bandit security issues – HIGH:{high} MED:{medium} LOW:{low}"
                )
        except Exception as exc:   # noqa: BLE001
            logger.debug("Bandit skipped: %s", exc)
        return report

    # ──────────────────────────────────────────────────────────────────────────
    # Dependency extraction
    # ──────────────────────────────────────────────────────────────────────────

    # Function: _extract_dependencies
    def _extract_dependencies(self) -> Set[str]:
        deps: Set[str] = set()

        # requirements*.txt
        for req_file in self.repo_path.rglob("requirements*.txt"):
            for line in self._read_lines(req_file):
                pkg = re.split(r"[>=<!;\[#]", line)[0].strip()
                if pkg:
                    deps.add(pkg.lower())

        # pyproject.toml (basic regex; avoids full TOML parse)
        for toml_file in self.repo_path.rglob("pyproject.toml"):
            src = toml_file.read_text(encoding="utf-8", errors="replace")
            for m in re.finditer(r'["\']([\w][\w\-\.]+)\s*[>=<!]', src):
                deps.add(m.group(1).lower())

        # setup.cfg / setup.py (heuristic)
        for setup in self.repo_path.rglob("setup.*"):
            if setup.suffix in (".py", ".cfg"):
                src = setup.read_text(encoding="utf-8", errors="replace")
                for m in re.finditer(r'["\']([A-Za-z][\w\-\.]+)[>=<!\["\']', src):
                    deps.add(m.group(1).lower())

        return deps

    # ──────────────────────────────────────────────────────────────────────────
    # Python-specific nesting depth (indentation-based)
    # ──────────────────────────────────────────────────────────────────────────

    # Function: _deep_nesting_count_python
    @staticmethod
    def _deep_nesting_count_python(lines: list, threshold: int = 4) -> int:
        """Count non-blank lines with indentation level > threshold (4-space units)."""
        count = 0
        for line in lines:
            stripped = line.lstrip()
            if not stripped:
                continue
            indent = len(line) - len(stripped)
            # 4 spaces per level
            if indent // 4 > threshold:
                count += 1
        return count
