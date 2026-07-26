# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Analyses JavaScript and TypeScript source files (.js .ts .jsx .tsx).
# Date: 2026-02-23
# ---------------------------------------------------------------------------
"""
javascript_analyzer.py
-----------------------
Analyses JavaScript and TypeScript source files (.js .ts .jsx .tsx).

Metrics produced
~~~~~~~~~~~~~~~~
- SLOC / comment / blank lines
- Cyclomatic complexity (branch pattern counting)
- Class, function, and arrow-function counts
- Long methods (>40 LOC estimate), deep nesting
- Magic numbers, TODO markers
- Bad-practice detection:
    console.log usage, var declarations, == vs ===, any type (TS),
    callback hell (deep nesting proxy), empty catch blocks
- Dependency extraction from package.json
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Optional, Set

from analyzers.base_analyzer import BaseAnalyzer, FileMetrics, LanguageReport
from config.settings import LANGUAGE_EXTENSIONS


class JavaScriptAnalyzer(BaseAnalyzer):
    """Analyser for JavaScript/TypeScript (.js .ts .jsx .tsx) source files."""

    EXTENSIONS = LANGUAGE_EXTENSIONS.get("javascript", {".js", ".ts", ".jsx", ".tsx"})

    _BRANCH = re.compile(
        r'\b(if|else\s+if|for|while|switch\s*\(|case\s+|catch|&&|\|\||'
        r'\?\s*\w|\?\?)\b'
    )
    # Named functions, arrow functions, method definitions
    _FUNC = re.compile(
        r'(?:function\s+\w+\s*\(|'          # function foo(
        r'(?:const|let|var)\s+\w+\s*=\s*(?:async\s*)?\([^)]*\)\s*=>|'  # const f = () =>
        r'(?:const|let|var)\s+\w+\s*=\s*(?:async\s*)?\w+\s*=>|'        # const f = x =>
        r'(?:public|private|protected|static|async)?\s+\w+\s*\([^)]{0,120}\)\s*\{)'  # method() {
    )
    _CLASS      = re.compile(r'\bclass\s+\w+')
    _CONSOLE    = re.compile(r'\bconsole\.(log|warn|error|debug|info)\s*\(')
    _VAR        = re.compile(r'\bvar\s+\w+')
    _LOOSE_EQ   = re.compile(r'(?<!=)==(?!=)|(?<!=)!=(?!=)')   # == or != not === !==
    _TS_ANY     = re.compile(r':\s*any\b')                      # TypeScript :any
    _EMPTY_CATCH = re.compile(r'catch\s*\([^)]*\)\s*\{\s*\}')

    # ── jQuery patterns ───────────────────────────────────────────────────────
    _JQUERY_GLOBAL  = re.compile(r'\bjQuery\s*[\(\.]|\$\s*[\(\.]', re.IGNORECASE)
    _JQUERY_AJAX    = re.compile(r'\$\.(?:ajax|get|post|getJSON|getScript|load)\s*\(', re.IGNORECASE)
    _JQUERY_DOM     = re.compile(
        r'\$\s*\(\s*["\'][^"\']{0,60}["\']\s*\)\.'
        r'(?:html|text|val|attr|prop|css|addClass|removeClass|toggleClass|'
        r'append|prepend|before|after|remove|hide|show|toggle|fade|slide|'
        r'on|off|click|submit|keyup|keydown|change|ready|each|find|filter|'
        r'closest|parent|children|siblings|first|last|eq|not|has)\s*\(',
        re.IGNORECASE
    )
    _JQUERY_IMPORT  = re.compile(
        r"require\s*\(\s*['\"]jquery['\"]|import\s+.*\s+from\s+['\"]jquery['\"]",
        re.IGNORECASE
    )

    # ── Bootstrap patterns ────────────────────────────────────────────────────
    _BOOTSTRAP_IMPORT = re.compile(
        r"require\s*\(\s*['\"]bootstrap['\"]|import\s+.*\s+from\s+['\"]bootstrap['\"]",
        re.IGNORECASE
    )
    _BOOTSTRAP_JS_API = re.compile(
        r"\b(?:bootstrap|Bootstrap)\s*\.\s*(?:Modal|Dropdown|Tooltip|Popover|"
        r"Collapse|Offcanvas|Toast|Alert|Button|Carousel|Tab|ScrollSpy)\b",
        re.IGNORECASE
    )
    _BOOTSTRAP_CLASS = re.compile(
        r'class\s*=\s*["\'][^"\']*\b(?:col-(?:xs|sm|md|lg|xl|xxl)-?\d*|'
        r'container(?:-fluid)?|row\b|navbar\b|btn\b|btn-|card\b|modal\b|'
        r'alert-|badge\b|carousel\b|collapse\b|dropdown\b|form-control\b|'
        r'input-group\b|nav\b|navbar-|table\b|table-)',
        re.IGNORECASE
    )

    # Function: language_name
    def language_name(self) -> str:
        return "JavaScript"

    # ──────────────────────────────────────────────────────────────────────────
    # Single-file analysis
    # ──────────────────────────────────────────────────────────────────────────

    # Function: _classify_js_line
    @staticmethod
    def _classify_js_line(stripped: str, fm: FileMetrics, state: dict) -> None:
        if "/*" in stripped and "*/" not in stripped:
            state["in_block"] = True
        if state["in_block"]:
            fm.comment_lines += 1
            if "*/" in stripped:
                state["in_block"] = False
            return
        if stripped.startswith("//") or stripped.startswith("*"):
            fm.comment_lines += 1
        else:
            fm.code_lines += 1

    # Function: _analyse_file
    def _analyse_file(self, path: Path) -> Optional[FileMetrics]:
        lines = self._read_lines(path)
        if not lines:
            return None

        fm = FileMetrics(path=path, language="JavaScript", total_lines=len(lines))
        source = "\n".join(lines)

        # Line classification (supports // and /* */ and <!-- HTML comments)
        state = {"in_block": False}
        for line in lines:
            stripped = line.strip()
            if not stripped:
                fm.blank_lines += 1
                continue
            self._classify_js_line(stripped, fm, state)

        fm.todo_comments = self._count_todo(lines)
        fm.magic_numbers = self._count_magic_numbers(lines)
        fm.commented_out_lines = self._count_commented_out_code(lines)
        fm.max_depth     = self._max_nesting_depth(lines)
        fm.deep_nesting  = self._deep_nesting_count(lines, threshold=4)

        # Strip block comments for complexity counting
        stripped_src = re.sub(r'/\*.*?\*/', '', source, flags=re.DOTALL)
        stripped_src = re.sub(r'//[^\n]*', '', stripped_src)

        fm.functions    = len(self._FUNC.findall(source))
        fm.classes      = len(self._CLASS.findall(source))
        fm.long_methods = self._count_long_methods(source)

        # Cyclomatic complexity: per-function average (comparable to radon output)
        raw_branches = len(self._BRANCH.findall(stripped_src))
        fm.cyclomatic = max(1, round((1 + raw_branches) / max(fm.functions, 1)))

        # Reuse duplicate_blocks for bad-practice signal
        fm.duplicate_blocks = (
            len(self._CONSOLE.findall(source))
            + len(self._VAR.findall(source))
            + len(self._LOOSE_EQ.findall(source))
            + len(self._TS_ANY.findall(source))
            + len(self._EMPTY_CATCH.findall(source))
        )

        # ── jQuery / Bootstrap signals ───────────────────────────────────────
        fm._jquery_global   = len(self._JQUERY_GLOBAL.findall(source))
        fm._jquery_ajax     = len(self._JQUERY_AJAX.findall(source))
        fm._jquery_dom      = len(self._JQUERY_DOM.findall(source))
        fm._jquery_import   = 1 if self._JQUERY_IMPORT.search(source) else 0
        fm._bootstrap_import= 1 if self._BOOTSTRAP_IMPORT.search(source) else 0
        fm._bootstrap_js    = len(self._BOOTSTRAP_JS_API.findall(source))

        return fm

    # ──────────────────────────────────────────────────────────────────────────
    # Repository-level augments
    # ──────────────────────────────────────────────────────────────────────────

    # Function: _report_ts_mix
    @staticmethod
    def _report_ts_mix(report: LanguageReport) -> None:
        # Note TypeScript file count in bad_practices summary
        ts_files = sum(1 for f in report.files
                       if str(f.path).endswith((".ts", ".tsx")))
        js_only = report.file_count - ts_files
        if ts_files and js_only:
            report.bad_practices.append(
                f"Mixed JS/TS project: {js_only} .js files + {ts_files} .ts files"
            )

    # Function: _report_jquery_bootstrap
    @staticmethod
    def _report_jquery_bootstrap(report: LanguageReport) -> None:
        # ── jQuery / Bootstrap reporting ─────────────────────────────────────
        jquery_files  = sum(1 for f in report.files if getattr(f, "_jquery_import", 0) or
                                                         getattr(f, "_jquery_global", 0) > 2)
        jquery_calls  = sum(getattr(f, "_jquery_global", 0) +
                            getattr(f, "_jquery_ajax", 0) +
                            getattr(f, "_jquery_dom", 0) for f in report.files)
        bootstrap_files = sum(1 for f in report.files if getattr(f, "_bootstrap_import", 0))

        if jquery_files > 0 or jquery_calls > 10:
            report.dependencies.add(f"jQuery ({jquery_files} file(s), ~{jquery_calls} call(s))")
            if jquery_calls > 50:
                report.bad_practices.append(
                    f"Heavy jQuery DOM manipulation detected ({jquery_calls} calls across "
                    f"{jquery_files} files) — consider migrating to React/Vue/Angular."
                )

        if bootstrap_files > 0:
            report.dependencies.add(f"Bootstrap ({bootstrap_files} file(s))")

    # Function: _check_pkg_jquery
    @staticmethod
    def _check_pkg_jquery(all_deps: dict, report: LanguageReport) -> None:
        if "jquery" not in all_deps:
            return
        v = all_deps["jquery"]
        report.dependencies.add(f"jQuery {v} (package.json)")
        if v.lstrip("^~").startswith(("1.", "2.")):
            report.bad_practices.append(
                f"jQuery {v} is outdated (< 3.0) — critical XSS/security fixes in v3+"
            )

    # Function: _check_pkg_bootstrap
    @staticmethod
    def _check_pkg_bootstrap(all_deps: dict, report: LanguageReport) -> None:
        if "bootstrap" not in all_deps:
            return
        v = all_deps["bootstrap"]
        report.dependencies.add(f"Bootstrap {v} (package.json)")
        if v.lstrip("^~").startswith(("2.", "3.")):
            report.bad_practices.append(
                f"Bootstrap {v} is outdated — Bootstrap 5 dropped jQuery dependency"
            )

    # Function: _scan_package_json_libs
    def _scan_package_json_libs(self, report: LanguageReport) -> None:
        # Check package.json for Bootstrap/jQuery versions
        for pkg_json_path in self.repo_path.rglob("package.json"):
            try:
                rel = pkg_json_path.relative_to(self.repo_path)
                if "node_modules" in rel.parts:
                    continue
                import json as _json
                data = _json.loads(pkg_json_path.read_text(encoding="utf-8", errors="replace"))
                all_deps = {}
                for section in ("dependencies", "devDependencies", "peerDependencies"):
                    all_deps.update(data.get(section, {}))
                self._check_pkg_jquery(all_deps, report)
                self._check_pkg_bootstrap(all_deps, report)
            except Exception:
                pass

    # Function: analyse
    def analyse(self) -> LanguageReport:
        report = super().analyse()
        total_smells = sum(f.duplicate_blocks for f in report.files)
        if total_smells:
            report.bad_practices.append(
                f"console.log / var / loose-eq / :any / empty-catch: {total_smells}"
            )
        self._report_ts_mix(report)
        self._report_jquery_bootstrap(report)
        self._scan_package_json_libs(report)

        return report

    # ──────────────────────────────────────────────────────────────────────────
    # Dependency extraction
    # ──────────────────────────────────────────────────────────────────────────

    # Function: _extract_dependencies
    def _extract_dependencies(self) -> Set[str]:
        deps: Set[str] = set()

        for pkg_json in self.repo_path.rglob("package.json"):
            # Skip node_modules to avoid enumerating thousands of nested pkgs
            try:
                rel = pkg_json.relative_to(self.repo_path)
                if "node_modules" in rel.parts:
                    continue
            except ValueError:
                continue
            try:
                data = json.loads(pkg_json.read_text(encoding="utf-8", errors="replace"))
            except Exception:
                continue
            for section in ("dependencies", "devDependencies", "peerDependencies"):
                for pkg in data.get(section, {}):
                    deps.add(pkg.lower())

        return deps

    # ──────────────────────────────────────────────────────────────────────────
    # Helpers
    # ──────────────────────────────────────────────────────────────────────────

    # Function: _count_long_methods
    @staticmethod
    def _count_long_methods(source: str, threshold: int = 40) -> int:
        """Estimate long functions by brace depth tracking."""
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
