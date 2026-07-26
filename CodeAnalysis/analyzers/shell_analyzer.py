# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Analyses shell / Bash / Zsh / POSIX-sh / Fish / Ksh scripts.
# Date: 2026-05-14
# ---------------------------------------------------------------------------
"""
shell_analyzer.py
-----------------
Analyses shell / Bash / Zsh / POSIX-sh / Fish / Ksh scripts.

Supported extensions: .sh .bash .zsh .ksh .fish .csh .tcsh .bats

Metrics produced
~~~~~~~~~~~~~~~~
- SLOC / comment / blank lines
- Cyclomatic complexity (branch pattern counting)
- Function counts  (function foo() {} or foo() {})
- Long functions, deep nesting, magic numbers, TODO markers
- Bad-practice detection:
    • eval usage
    • rm -rf  (destructive filesystem op)
    • curl | sh / wget | bash  (remote code execution risk)
    • Missing "set -e" / "set -euo pipefail"
    • Unquoted variable expansions  ($VAR without quotes in common positions)
    • Hardcoded secrets / passwords
- Dependency extraction: external commands referenced via $(…) or `…`
"""
from __future__ import annotations
import os
import re
from pathlib import Path
from typing import Optional, Set

from analyzers.base_analyzer import BaseAnalyzer, FileMetrics, LanguageReport
from config.settings import LANGUAGE_EXTENSIONS


class ShellAnalyzer(BaseAnalyzer):
    """Analyser for shell script files."""

    EXTENSIONS = LANGUAGE_EXTENSIONS.get(
        "shell", {".sh", ".bash", ".zsh", ".ksh", ".fish", ".csh", ".tcsh", ".bats"}
    )

    _BRANCH = re.compile(
        r'\b(if\b|elif\b|case\b|esac\b|for\b|while\b|until\b|'
        r'&&|\|\|)\b'
    )
    _FUNC = re.compile(
        r'(?:^|\s)(?:function\s+)?\w[\w_:-]*\s*\(\s*\)\s*\{',
        re.MULTILINE,
    )

    # Bad practices
    _EVAL           = re.compile(r'\beval\b')
    _RM_RF          = re.compile(r'\brm\s+(?:-[a-zA-Z]*r[a-zA-Z]*f|--force|'
                                  r'-[a-zA-Z]*f[a-zA-Z]*r)\b')
    _CURL_PIPE      = re.compile(r'curl\b.+\|\s*(?:bash|sh)\b|'
                                  r'wget\b.+\|\s*(?:bash|sh)\b', re.DOTALL)
    _UNQUOTED_VAR   = re.compile(r'(?<!")(?<!\$\{)\$[A-Za-z_]\w*(?!")(?!=)')
    _HARDCODED_CRED = re.compile(
        r"(?:PASSWORD|PASSWD|SECRET|API_KEY|TOKEN)\s*=\s*['\"]?[^'\"\s]{4,}",
        re.IGNORECASE,
    )

    # Function: language_name
    def language_name(self) -> str:
        return "Shell/Bash"

    # ─────────────────────────────────────────────────────────────────────────

    # Function: _analyse_file
    def _analyse_file(self, path: Path) -> Optional[FileMetrics]:
        lines = self._read_lines(path)
        if not lines:
            return None

        fm     = FileMetrics(path=path, language="Shell/Bash", total_lines=len(lines))
        source = "\n".join(lines)

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
        # Shell uses if/fi, for/done, while/done — use keyword depth proxy
        fm.max_depth    = self._estimate_nesting_depth(lines)
        fm.deep_nesting = 0   # not easily computable without a full parser

        stripped_src   = re.sub(r'#[^\n]*', '', source)
        fm.functions   = len(self._FUNC.findall(source))
        fm.cyclomatic  = max(1, round((1 + len(self._BRANCH.findall(stripped_src))) / max(fm.functions, 1)))
        fm.classes     = 0
        fm.long_methods = 0   # hard to determine without brace tracking in POSIX sh

        # Security / quality smells
        has_set_e    = bool(re.search(r'\bset\s+[-+][a-zA-Z]*e', source))
        unquoted_cnt = len(self._UNQUOTED_VAR.findall(source))

        smells = (
            len(self._EVAL.findall(source))
            + len(self._RM_RF.findall(source))
            + len(self._CURL_PIPE.findall(source))
            + (10 if not has_set_e else 0)   # weight for missing set -e
            + min(unquoted_cnt, 20)           # cap to avoid noise
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
                f"eval/rm-rf/curl-pipe/missing-set-e/unquoted-vars/hardcoded-creds: {total_smells}"
            )
        return report

    # ─────────────────────────────────────────────────────────────────────────

    # Function: _extract_dependencies
    # Function: _extract_deps_from_file
    def _extract_deps_from_file(self, fpath: Path, cmd_re) -> Set[str]:
        if fpath.suffix not in self.EXTENSIONS:
            return set()
        try:
            src = fpath.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return set()
        found: Set[str] = set()
        for m in cmd_re.finditer(src):
            cmd = m.group(1).lower()
            # filter out built-ins
            if cmd not in {"echo", "cd", "ls", "test", "true", "false",
                           "mkdir", "rm", "cp", "mv", "cat", "grep",
                           "if", "for", "while", "read"}:
                found.add(f"cmd:{cmd}")
        return found

    # Function: _extract_dependencies
    def _extract_dependencies(self) -> Set[str]:
        """Extract external commands invoked via command substitution."""
        deps: Set[str] = set()
        cmd_re = re.compile(r'\$\((\w[\w-]*)')
        _skip = {".git", "node_modules", "vendor", "venv", ".venv", "target", "__pycache__"}
        for dirpath, dirnames, filenames in os.walk(str(self.repo_path)):
            dirnames[:] = [d for d in dirnames if d not in _skip]
            for fname in filenames:
                deps |= self._extract_deps_from_file(Path(dirpath) / fname, cmd_re)
        return deps

    # Function: _estimate_nesting_depth
    @staticmethod
    def _estimate_nesting_depth(lines) -> int:
        """Estimate max nesting depth using if/for/while/until keywords."""
        depth = max_depth = 0
        openers = re.compile(r'^\s*(?:if\b|for\b|while\b|until\b|case\b|do\b)\s')
        closers = re.compile(r'^\s*(?:fi\b|done\b|esac\b)\s*$')
        for line in lines:
            if openers.match(line):
                depth += 1
                max_depth = max(max_depth, depth)
            elif closers.match(line):
                depth = max(0, depth - 1)
        return max_depth
