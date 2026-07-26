# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Detects "Green Deficiencies" -- algorithmic and resource-waste patterns that
# Date: 2025-12-26
# ---------------------------------------------------------------------------
"""
green_impact.py
---------------
Detects "Green Deficiencies" -- algorithmic and resource-waste patterns that
increase CPU / memory consumption and CO2 footprint.

Scanning strategy: line-by-line with a lightweight nesting-depth tracker.
This avoids catastrophic regex backtracking on large source files.

Deficiency categories (matching CAST Highlight "Portfolio Green Impact"):
  Algorithmic Costs (string concat in loops, instantiation in loops,
                     nested loops, func call in loop condition)
  Avoiding Failure  (empty catch blocks, broad exception catches)
  Resource Economy  (unclosed resources, heavy alloc in loops)
  Maintainability   (debug print statements)
  Security          (hardcoded credentials)
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Tuple

EFFORT_PER_100 = 0.25

@dataclass
class DeficiencyRule:
    key:       str
    category:  str
    label:     str
    languages: List[str]

_RULES: List[DeficiencyRule] = [
    DeficiencyRule("str_concat_loop",       "Algorithmic Costs",
                   "Avoid String concatenation in loops",
                   ["Java", "Python", ".NET", "JavaScript", "TypeScript"]),
    DeficiencyRule("inst_in_loop",          "Algorithmic Costs",
                   "Avoid instantiations inside loops",
                   ["Java", ".NET"]),
    DeficiencyRule("nested_loops",          "Algorithmic Costs",
                   "Avoid nested loops", ["*"]),
    DeficiencyRule("func_call_in_loop_cond","Algorithmic Costs",
                   "Avoid calling a function in a loop condition",
                   ["Java", ".NET", "JavaScript", "TypeScript"]),
    DeficiencyRule("comparison_to_0",       "Algorithmic Costs",
                   "Prefer comparison-to-0 in loop conditions",
                   ["Java", ".NET"]),
    DeficiencyRule("empty_catch",           "Avoiding Failure",
                   "Avoid empty catch blocks", ["*"]),
    DeficiencyRule("broad_catch",           "Avoiding Failure",
                   "Avoid catching broad Exception types",
                   ["Java", ".NET", "Python"]),
    DeficiencyRule("unclosed_resource",     "Resource Economy",
                   "Ensure resources are closed after use", ["Java", ".NET"]),
    DeficiencyRule("debug_print",           "Maintainability",
                   "Remove debug print/log statements", ["*"]),
    DeficiencyRule("hardcoded_creds",       "Security",
                   "Avoid hardcoded credentials/secrets", ["*"]),
]

_P: Dict[str, re.Pattern] = {
    "concat":    re.compile(r'\+=\s*["\']|String\s*\+\s*=|\bstr\s*\([^)]{0,80}\)\s*\+|\w+\s*\+=\s*\w+\s*\+\s*["\']'),
    "new_inst":  re.compile(r'\bnew\s+[A-Z]\w*\s*\('),
    "cmp0":      re.compile(r'for\s*\([^;]{0,60};\s*[^;]{0,60}\.(size|length|count)\s*\(\s*\)', re.I),
    "call_cond": re.compile(r'(?:while|for)\s*\([^)]{0,80}\w+\s*\([^)]{0,40}\)\s*[><=!]', re.I),
    "emp_catch": re.compile(r'\bcatch\s*\([^)]{0,80}\)\s*\{\s*\}'),
    "pass":      re.compile(r'^\s*pass\s*$'),
    "except":    re.compile(r'^\s*except\b'),
    "br_catch":  re.compile(r'\bcatch\s*\(\s*Exception\b|\bexcept\s*(Exception)?\s*:', re.I),
    "unclosed":  re.compile(r'\bnew\s+(?:FileInputStream|FileReader|BufferedReader|SqlConnection|StreamReader|StreamWriter|SqlCommand)\s*\('),
    # debug: Java sysout, JS console, C# Console, Python print() and logging.debug
    "debug":     re.compile(
        r'\bSystem\.out\.print|\bconsole\.log\s*\('
        r'|\bConsole\.Write(?:Line)?\s*\('
        r'|\bprint\s*\('
        r'|\blogging\.debug\s*\(|\blogger\.debug\s*\('
    ),
    "creds":     re.compile(
        r'(?:password|passwd|secret|api_key|apikey|token|auth_token|access_key|client_secret)'
        r'\s*[=:]\s*["\'][^"\'\ ]{4,100}["\']',
        re.I
    ),
    "for_kw":    re.compile(r'\bfor\s*[\(\[]|\bfor\s+\w+\s+in\s'),
    "while_kw":  re.compile(r'\bwhile\s*\('),
    # Python-indentation-based loop detection: captures indent prefix
    "py_for":    re.compile(r'^(\s*)(?:for\s+\w|async\s+for\s+\w|while\s+)'),
}


@dataclass
class GreenDeficiencySummary:
    rule_key:       str
    category:       str
    label:          str
    language:       str
    occurrences:    int
    effort_days:    float
    affected_files: int


@dataclass
class GreenImpactScore:
    total_occurrences:  int
    total_effort_days:  float
    green_score:        float
    risk_label:         str
    deficiencies:       List[GreenDeficiencySummary] = field(default_factory=list)
    category_totals:    Dict[str, int]               = field(default_factory=dict)


class GreenImpactCalculator:
    _SKIP_DIRS = {".git","node_modules","vendor","venv",".venv",
                  "target","bin","obj","__pycache__","dist","build"}

    _EXT_LANG: Dict[str, str] = {
        ".py":"Python", ".java":"Java", ".cs":".NET", ".vb":".NET",
        ".js":"JavaScript", ".ts":"TypeScript",
        ".jsx":"JavaScript", ".tsx":"TypeScript",
    }

    # Function: _aggregate_counts
    def _aggregate_counts(self, repo_path: Path) -> Dict[Tuple[str, str], dict]:
        agg: Dict[Tuple[str,str], dict] = {}
        for src in self._iter_files(repo_path):
            lang = self._EXT_LANG.get(src.suffix.lower())
            if not lang:
                continue
            try:
                lines = src.read_text(encoding="utf-8", errors="ignore").splitlines()
            except Exception:
                continue
            counts = self._scan_file(lines, lang)
            rel = str(src.relative_to(repo_path))
            for rk, cnt in counts.items():
                if cnt == 0:
                    continue
                k = (rk, lang)
                if k not in agg:
                    agg[k] = {"count": 0, "files": set()}
                agg[k]["count"] += cnt
                agg[k]["files"].add(rel)
        return agg

    # Function: _build_deficiency_rows
    def _build_deficiency_rows(self, agg: Dict[Tuple[str, str], dict]) -> Tuple[List["GreenDeficiencySummary"], Dict[str, int]]:
        rule_map = {r.key: r for r in _RULES}
        rows: List[GreenDeficiencySummary] = []
        cat_totals: Dict[str, int] = {}
        for (rk, lang), info in sorted(agg.items(), key=lambda x: -x[1]["count"]):
            rule = rule_map.get(rk)
            if not rule:
                continue
            cnt    = info["count"]
            effort = round(cnt / 100 * EFFORT_PER_100 * 100, 2)
            rows.append(GreenDeficiencySummary(
                rule_key=rk, category=rule.category, label=rule.label,
                language=lang, occurrences=cnt, effort_days=effort,
                affected_files=len(info["files"]),
            ))
            cat_totals[rule.category] = cat_totals.get(rule.category, 0) + cnt
        return rows, cat_totals

    # Function: _green_score
    @staticmethod
    def _green_score(total_occ: int) -> float:
        if total_occ == 0:
            return 95.0
        if total_occ < 50:
            return 85.0
        if total_occ < 200:
            return 70.0
        if total_occ < 500:
            return 60.0
        if total_occ < 1000:
            return 45.0
        if total_occ < 5000:
            return 30.0
        return max(10.0, 100.0 - total_occ / 200)

    # Function: _risk_label
    @staticmethod
    def _risk_label(gs: float) -> str:
        if gs >= 75:
            return "LOW"
        if gs >= 50:
            return "MEDIUM"
        if gs >= 25:
            return "HIGH"
        return "CRITICAL"

    # Function: calculate
    def calculate(self, repo_path: Path) -> GreenImpactScore:
        if repo_path is None or not repo_path.exists():
            return GreenImpactScore(
                total_occurrences=0, total_effort_days=0.0,
                green_score=0.0, risk_label="UNKNOWN",
            )
        agg = self._aggregate_counts(repo_path)
        rows, cat_totals = self._build_deficiency_rows(agg)

        total_occ    = sum(r.occurrences for r in rows)
        total_effort = round(sum(r.effort_days for r in rows), 2)

        gs = self._green_score(total_occ)
        risk = self._risk_label(gs)
        return GreenImpactScore(
            total_occurrences=total_occ, total_effort_days=total_effort,
            green_score=round(gs, 1), risk_label=risk,
            deficiencies=rows, category_totals=cat_totals,
        )

    # Function: _update_brace_loop_state
    @staticmethod
    def _update_brace_loop_state(line: str, open_braces: int, loop_depth: int, loop_at_depth: List[int]) -> Tuple[int, int, List[int]]:
        # Track nesting for Java/C#/JS/TS
        is_for_line = bool(_P["for_kw"].search(line) or _P["while_kw"].search(line))
        opens  = line.count("{")
        closes = line.count("}")
        if is_for_line and opens > closes:
            loop_at_depth.append(open_braces + opens - closes)
            loop_depth += 1
        else:
            new_depth = open_braces + opens - closes
            removed = [d for d in loop_at_depth if d > new_depth]
            loop_depth = max(0, loop_depth - len(removed))
            loop_at_depth = [d for d in loop_at_depth if d <= new_depth]
        open_braces = max(0, open_braces + opens - closes)
        return open_braces, loop_depth, loop_at_depth

    # Function: _update_python_loop_state
    @staticmethod
    def _update_python_loop_state(raw: str, loop_depth: int, py_loop_indents: List[int]) -> Tuple[int, List[int]]:
        # Indentation-based loop depth tracking
        if not raw.strip():
            return loop_depth, py_loop_indents  # skip blank lines
        indent = len(raw) - len(raw.lstrip())
        # Pop loops whose body has ended (current indent <= loop indent)
        py_loop_indents = [i for i in py_loop_indents if i < indent]
        loop_depth = len(py_loop_indents)
        # Detect loop start
        if _P["py_for"].match(raw):
            py_loop_indents.append(indent)
            loop_depth = len(py_loop_indents)
        return loop_depth, py_loop_indents

    # Function: _count_loop_signals
    @staticmethod
    def _count_loop_signals(line: str, raw: str, lang: str, loop_depth: int, counts: Dict[str, int]) -> None:
        # String concat in loop
        if loop_depth > 0 and _P["concat"].search(line):
            counts["str_concat_loop"] += 1
        # Instantiation in loop
        if loop_depth > 0 and _P["new_inst"].search(line):
            counts["inst_in_loop"] += 1
        # Nested loop
        if loop_depth > 0 and (_P["for_kw"].search(line) or _P["while_kw"].search(line)
                                or (lang == "Python" and _P["py_for"].match(raw))):
            counts["nested_loops"] += 1
        # Function call in loop condition
        if _P["call_cond"].search(line):
            counts["func_call_in_loop_cond"] += 1
        # Comparison to 0 in loop condition
        if _P["cmp0"].search(line):
            counts["comparison_to_0"] += 1

    # Function: _count_exception_signals
    @staticmethod
    def _count_exception_signals(line: str, raw: str, lang: str, prev_except: bool, counts: Dict[str, int]) -> bool:
        # Empty catch
        if _P["emp_catch"].search(line):
            counts["empty_catch"] += 1
        if lang == "Python":
            if _P["except"].match(raw):
                prev_except = True
            elif prev_except:
                if _P["pass"].match(raw):
                    counts["empty_catch"] += 1
                prev_except = False
            else:
                prev_except = False
        # Broad catch
        if _P["br_catch"].search(line):
            counts["broad_catch"] += 1
        return prev_except

    # Function: _count_misc_signals
    @staticmethod
    def _count_misc_signals(line: str, counts: Dict[str, int]) -> None:
        # Unclosed resource
        if _P["unclosed"].search(line):
            counts["unclosed_resource"] += 1
        # Debug print — skip comment lines
        stripped_for_debug = line.lstrip()
        if not stripped_for_debug.startswith(("//", "#", "*", "<!--")):
            if _P["debug"].search(line):
                counts["debug_print"] += 1
        # Hardcoded credentials
        if _P["creds"].search(line):
            counts["hardcoded_creds"] += 1

    # Function: _filter_counts_by_lang
    @staticmethod
    def _filter_counts_by_lang(counts: Dict[str, int], lang: str) -> Dict[str, int]:
        # Filter by language applicability
        final: Dict[str, int] = {}
        for rule in _RULES:
            if rule.languages == ["*"] or lang in rule.languages:
                final[rule.key] = counts.get(rule.key, 0)
        return final

    # Function: _scan_file
    def _scan_file(self, lines: List[str], lang: str) -> Dict[str, int]:
        counts = {r.key: 0 for r in _RULES}
        loop_depth    = 0
        open_braces   = 0
        loop_at_depth: List[int] = []
        prev_except   = False
        # Python: stack of (indent_level) for loop-start lines
        py_loop_indents: List[int] = []

        for raw in lines:
            line = raw.strip()

            if lang in ("Java", ".NET", "JavaScript", "TypeScript"):
                open_braces, loop_depth, loop_at_depth = self._update_brace_loop_state(
                    line, open_braces, loop_depth, loop_at_depth
                )
            elif lang == "Python":
                loop_depth, py_loop_indents = self._update_python_loop_state(
                    raw, loop_depth, py_loop_indents
                )

            self._count_loop_signals(line, raw, lang, loop_depth, counts)
            prev_except = self._count_exception_signals(line, raw, lang, prev_except, counts)
            self._count_misc_signals(line, counts)

        return self._filter_counts_by_lang(counts, lang)

    # Function: _iter_files
    def _iter_files(self, repo_path: Path, max_files: int = 1500):
        _MAX_BYTES = 500_000
        count = 0
        for dirpath, dirnames, filenames in os.walk(str(repo_path)):
            dirnames[:] = [d for d in dirnames if d not in self._SKIP_DIRS]
            dir_path = Path(dirpath)
            for fname in filenames:
                if count >= max_files:
                    return
                path = dir_path / fname
                if path.suffix.lower() not in self._EXT_LANG:
                    continue
                try:
                    if path.stat().st_size > _MAX_BYTES:
                        continue
                except OSError:
                    continue
                count += 1
                yield path
