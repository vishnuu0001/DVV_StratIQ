# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Abstract base class that every language-specific analyser must implement.
# Date: 2025-10-04
# ---------------------------------------------------------------------------
"""
base_analyzer.py
----------------
Abstract base class that every language-specific analyser must implement.
Also provides shared helper utilities (file walker, comment-strip, etc.).
"""
from __future__ import annotations

import os
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set


@dataclass
class FileMetrics:
    """Line-level and structural metrics for a single source file."""
    path:               Path
    language:           str
    total_lines:        int  = 0
    code_lines:         int  = 0    # SLOC (non-blank, non-comment)
    comment_lines:      int  = 0
    blank_lines:        int  = 0
    cyclomatic:         int  = 1    # McCabe complexity
    cognitive:          int  = 0
    max_depth:          int  = 0    # max nesting depth
    functions:          int  = 0
    classes:            int  = 0
    long_methods:       int  = 0    # methods > 40 LOC
    deep_nesting:       int  = 0    # blocks nested > 4 levels
    duplicate_blocks:   int  = 0
    todo_comments:      int  = 0
    magic_numbers:      int  = 0
    commented_out_lines:int  = 0
    error:              Optional[str] = None


@dataclass
class LanguageReport:
    """Aggregated analysis results for all files in one language."""
    language:          str
    file_count:        int  = 0
    total_sloc:        int  = 0
    total_comments:    int  = 0
    avg_complexity:    float = 0.0
    max_complexity:    int   = 0
    total_functions:   int  = 0
    total_classes:     int  = 0
    long_methods_pct:  float = 0.0
    deep_nesting_pct:  float = 0.0
    comment_ratio:     float = 0.0    # comment lines / code lines
    commented_out_lines: int = 0
    commented_out_ratio: float = 0.0
    files:             List[FileMetrics] = field(default_factory=list)
    bad_practices:     List[str]         = field(default_factory=list)
    dependencies:      Set[str]          = field(default_factory=set)


class BaseAnalyzer(ABC):
    """
    Abstract code analyser.

    Sub-classes operate on a local repo directory; call :meth:`analyse` to
    receive a :class:`LanguageReport`.
    """

    # Set of file extensions this analyser handles
    EXTENSIONS: Set[str] = set()

    # Function: __init__
    def __init__(self, repo_path: Path):
        self.repo_path = repo_path

    # ──────────────────────────────────────────────────────────────────────────
    # Public
    # ──────────────────────────────────────────────────────────────────────────

    # Function: analyse
    def analyse(self) -> LanguageReport:
        """Walk the repo, analyse every matching file, return an aggregated report."""
        files = list(self._iter_source_files())
        report = LanguageReport(language=self.language_name())

        if not files:
            return report

        file_metrics_list: List[FileMetrics] = []
        for path in files:
            fm = self._analyse_file(path)
            if fm:
                file_metrics_list.append(fm)

        report = self._aggregate(file_metrics_list)
        report.dependencies = self._extract_dependencies()
        return report

    # ──────────────────────────────────────────────────────────────────────────
    # Abstract contract
    # ──────────────────────────────────────────────────────────────────────────

    # Function: language_name
    @abstractmethod
    def language_name(self) -> str:
        """Human-readable language name."""

    # Function: _analyse_file
    @abstractmethod
    def _analyse_file(self, path: Path) -> Optional[FileMetrics]:
        """Analyse a single source file and return its metrics."""

    # Function: _extract_dependencies
    @abstractmethod
    def _extract_dependencies(self) -> Set[str]:
        """
        Return a set of third-party dependency identifiers found in the repo
        (e.g. Maven artifact IDs, NuGet package names, pip package names).
        """

    # ──────────────────────────────────────────────────────────────────────────
    # Shared helpers
    # ──────────────────────────────────────────────────────────────────────────

    # Function: _keep_source_dir
    def _keep_source_dir(self, d: str, skip: set, skip_suffixes: set, build_dirs: set, sql_exts: set) -> bool:
        if d in skip:
            return False
        if any(d.endswith(f".{suffix}") for suffix in skip_suffixes):
            return False
        if d in build_dirs and not (self.EXTENSIONS & sql_exts):
            return False
        return True

    # Function: _is_eligible_source_file
    @staticmethod
    def _is_eligible_source_file(path: Path, extensions: set, max_bytes: int) -> bool:
        if path.suffix not in extensions:
            return False
        try:
            if path.stat().st_size > max_bytes:
                return False
        except OSError:
            return False
        return True

    # Function: _iter_source_files
    def _iter_source_files(self, max_files: int = 15000):
        """Yield all source files matching ``EXTENSIONS`` (skips .git / vendor).

        Uses relative-path parts so that workspace-level directories like
        ``cloned_repos`` in the absolute path never accidentally filter out
        files inside a cloned repository.

        Parameters
        ----------
        max_files:
            Hard cap on number of files yielded.  Set to 15 000 to allow
            thorough scanning of large monorepos while still guarding against
            runaway analysis.
        """
        # Directories that are never source — must be exact folder-name matches
        # so that legitimate top-level folders (e.g. "build" in a Go project
        # that is the main package) are not affected when they are the repo root
        # itself, only when they appear as *child* directories.
        skip = {
            ".git", "node_modules", "vendor", "venv", ".venv",
            "target", "__pycache__", ".mypy_cache", ".pytest_cache",
            ".tox", ".eggs",
            # build artefact dirs — keep "dist" only for non-SQL extensions
        }
        # Directories ending with .egg-info (generated by setuptools)
        skip_suffixes = {"egg-info"}
        
        # Separate set for dirs that may contain generated code for most langs
        # but are still scanned for SQL / DDL (schema migrations live there)
        build_dirs = {"dist", "build", "bin", "obj", "out", "release", "debug", ".next", ".nuxt", ".cache"}

        # SQL-adjacent extensions where build/dist directories are valid sources
        _SQL_EXTS = {".sql", ".ddl", ".dml", ".psql", ".pgsql", ".hql",
                     ".tsql", ".plsql", ".pls"}

        _MAX_BYTES = 2_000_000   # 2 MB — skip minified / generated blobs
        count = 0
        for dirpath, dirnames, filenames in os.walk(str(self.repo_path)):
            # Prune hard-skip dirs in place so os.walk never descends into them.
            # Also prune build_dirs unless caller uses SQL extensions
            # (SQL migrations may live under build/dist, but we prune them for
            # non-SQL analyzers to avoid scanning generated code).
            dirnames[:] = [
                d for d in dirnames
                if self._keep_source_dir(d, skip, skip_suffixes, build_dirs, _SQL_EXTS)
            ]
            dir_path = Path(dirpath)
            for fname in filenames:
                if count >= max_files:
                    return
                path = dir_path / fname
                if not self._is_eligible_source_file(path, self.EXTENSIONS, _MAX_BYTES):
                    continue
                count += 1
                yield path

    # Function: _read_lines
    @staticmethod
    def _read_lines(path: Path) -> List[str]:
        """Read file lines safely, trying UTF-8 then latin-1."""
        for enc in ("utf-8", "latin-1"):
            try:
                return path.read_text(encoding=enc).splitlines()
            except (UnicodeDecodeError, OSError):
                continue
        return []

    # Function: _count_magic_numbers
    @staticmethod
    def _count_magic_numbers(lines: List[str]) -> int:
        """Count numeric literals that are not 0, 1, or −1 (simplified heuristic)."""
        pattern = re.compile(r'\b(?!0\b|1\b|-1\b)\d{2,}\b')
        return sum(len(pattern.findall(line)) for line in lines)

    # Function: _count_todo
    @staticmethod
    def _count_todo(lines: List[str]) -> int:
        """Count lines containing TODO / FIXME / HACK / XXX."""
        pattern = re.compile(r'\b(TODO|FIXME|HACK|XXX)\b', re.IGNORECASE)
        return sum(1 for line in lines if pattern.search(line))

    # Function: _count_commented_out_code
    @staticmethod
    def _count_commented_out_code(lines: List[str]) -> int:
        """Estimate commented-out code lines (disabled statements in comments)."""
        # Heuristic: comment-prefixed lines containing common code tokens.
        code_like = re.compile(
            r'(\bif\b|\bfor\b|\bwhile\b|\breturn\b|\bclass\b|\bdef\b|\bfunction\b|\bpublic\b|\bprivate\b|\bSELECT\b|\{\s*$|;\s*$|=)',
            re.IGNORECASE,
        )
        comment_prefix = re.compile(r'^\s*(#|//|\*|--|/\*|\*/|\'\'\')')

        count = 0
        for line in lines:
            if not comment_prefix.search(line):
                continue
            # Strip common comment markers before testing for code-like patterns.
            stripped = re.sub(r'^\s*(#|//|\*|--|/\*+|\*/+|\'\'\')\s*', '', line)
            if len(stripped) < 6:
                continue
            if code_like.search(stripped):
                count += 1
        return count

    # Function: _max_nesting_depth
    @staticmethod
    def _max_nesting_depth(lines: List[str],
                           open_ch: str = "{",
                           close_ch: str = "}") -> int:
        """Estimate maximum nesting depth by counting bracket depth per line."""
        depth = max_depth = 0
        for line in lines:
            depth += line.count(open_ch) - line.count(close_ch)
            max_depth = max(max_depth, depth)
        return max(0, max_depth)

    # Function: _deep_nesting_count
    @staticmethod
    def _deep_nesting_count(lines: List[str],
                            threshold: int = 4,
                            open_ch: str = "{",
                            close_ch: str = "}") -> int:
        """Count lines where nesting depth exceeds threshold."""
        depth = count = 0
        for line in lines:
            depth += line.count(open_ch) - line.count(close_ch)
            if depth > threshold:
                count += 1
        return count

    # ──────────────────────────────────────────────────────────────────────────
    # Aggregation
    # ──────────────────────────────────────────────────────────────────────────

    # Function: _aggregate
    def _aggregate(self, file_metrics: List[FileMetrics]) -> LanguageReport:
        report = LanguageReport(language=self.language_name())
        if not file_metrics:
            return report

        report.files       = file_metrics
        report.file_count  = len(file_metrics)
        report.total_sloc  = sum(f.code_lines   for f in file_metrics)
        report.total_comments = sum(f.comment_lines for f in file_metrics)
        report.total_functions = sum(f.functions    for f in file_metrics)
        report.total_classes   = sum(f.classes      for f in file_metrics)
        report.commented_out_lines = sum(f.commented_out_lines for f in file_metrics)

        complexities  = [f.cyclomatic for f in file_metrics]
        report.avg_complexity = sum(complexities) / len(complexities)
        report.max_complexity = max(complexities)

        total_methods = report.total_functions or 1
        report.long_methods_pct = (
            sum(f.long_methods for f in file_metrics) / total_methods * 100
        )
        report.deep_nesting_pct = (
            sum(f.deep_nesting for f in file_metrics) / report.total_sloc * 100
            if report.total_sloc else 0
        )
        comment_lines = sum(f.comment_lines for f in file_metrics)
        report.comment_ratio = (
            comment_lines / report.total_sloc if report.total_sloc else 0
        )
        report.commented_out_ratio = (
            report.commented_out_lines / report.total_sloc if report.total_sloc else 0
        )

        report.bad_practices = self._collect_bad_practice_fingerprints(file_metrics)
        return report

    # Function: _collect_bad_practice_fingerprints
    @staticmethod
    def _collect_bad_practice_fingerprints(file_metrics: List[FileMetrics]) -> List[str]:
        bad: Dict[str, int] = {}
        for fm in file_metrics:
            if fm.commented_out_lines:
                bad["Commented-out code"] = bad.get("Commented-out code", 0) + fm.commented_out_lines
            if fm.long_methods:
                bad["Long methods (>40 LOC)"] = bad.get("Long methods (>40 LOC)", 0) + fm.long_methods
            if fm.deep_nesting:
                bad["Deep nesting (>4 levels)"] = bad.get("Deep nesting (>4 levels)", 0) + fm.deep_nesting
            if fm.magic_numbers:
                bad["Magic numbers"] = bad.get("Magic numbers", 0) + fm.magic_numbers
            if fm.todo_comments:
                bad["TODO/FIXME markers"] = bad.get("TODO/FIXME markers", 0) + fm.todo_comments
        return [f"{k}: {v}" for k, v in sorted(bad.items())]
