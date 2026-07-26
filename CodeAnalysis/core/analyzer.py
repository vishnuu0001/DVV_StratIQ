# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Central orchestrator: given a local repository path and metadata, it:
# Date: 2026-03-27
# ---------------------------------------------------------------------------
"""
analyzer.py
-----------
Central orchestrator: given a local repository path and metadata, it:

1. Selects the appropriate language analyser(s) based on detected extensions
2. Runs each analyser to collect LanguageReport objects
3. Feeds all reports into the five metric calculators
4. Bundles everything into an AnalysisResult dataclass
"""
from __future__ import annotations

import logging
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from analyzers.dotnet_analyzer    import DotNetAnalyzer
from analyzers.java_analyzer      import JavaAnalyzer
from analyzers.javascript_analyzer import JavaScriptAnalyzer
from analyzers.mainframe_analyzer import MainframeAnalyzer
from analyzers.python_analyzer    import PythonAnalyzer
# ── New language analyzers ────────────────────────────────────────────────────
from analyzers.sql_analyzer       import SQLAnalyzer
from analyzers.go_analyzer        import GoAnalyzer
from analyzers.rust_analyzer      import RustAnalyzer
from analyzers.kotlin_analyzer    import KotlinAnalyzer
from analyzers.scala_analyzer     import ScalaAnalyzer
from analyzers.ruby_analyzer      import RubyAnalyzer
from analyzers.php_analyzer       import PHPAnalyzer
from analyzers.cpp_analyzer       import CppAnalyzer
from analyzers.shell_analyzer     import ShellAnalyzer
from analyzers.groovy_analyzer    import GroovyAnalyzer
from analyzers.r_analyzer         import RAnalyzer
from analyzers.dart_analyzer      import DartAnalyzer
# ── Enterprise / Legacy analyzers ────────────────────────────────────────────
from analyzers.jsp_analyzer       import JSPAnalyzer
from analyzers.was_analyzer       import WASAnalyzer
from analyzers.db2_analyzer       import DB2Analyzer
from analyzers.base_analyzer      import LanguageReport
from core.github_fetcher          import RepoMetadata
from metrics.business_impact          import BusinessImpactCalculator, BusinessImpactScore
from metrics.cloud_maturity           import CloudMaturityCalculator, CloudMaturityScore
from metrics.co2_reduction            import Co2ReductionCalculator, Co2ReductionScore
from metrics.open_source_safety       import OpenSourceSafetyCalculator, OpenSourceSafetyScore
from metrics.software_health          import SoftwareHealthCalculator, HealthScore
from metrics.technical_debt           import TechnicalDebtCalculator, TechnicalDebtScore
from metrics.green_impact             import GreenImpactCalculator, GreenImpactScore
from metrics.quality_coverage         import QualityCoverageCalculator, QualityCoverageScore
from metrics.architecture_layers      import ArchitectureLayerAnalyzer, ArchitectureReport
from metrics.cloud_recommendations    import CloudRecommendationCalculator, CloudRecommendationReport
from config.settings                  import LANGUAGE_EXTENSIONS

logger = logging.getLogger(__name__)


@dataclass
class AnalysisResult:
    """Full analysis result for one repository."""
    repo_name:          str
    repo_url:           str
    total_sloc:         int
    total_files:        int
    languages_detected: List[str]
    language_reports:   List[LanguageReport]
    health:             HealthScore
    debt:               TechnicalDebtScore
    cloud:              CloudMaturityScore
    oss:                OpenSourceSafetyScore
    impact:             BusinessImpactScore
    co2:                Co2ReductionScore
    # ── New deeper analysis fields ─────────────────────────────────────────
    green_impact:       Optional[GreenImpactScore]          = None
    architecture:       Optional[ArchitectureReport]        = None
    cloud_recommendations: Optional[CloudRecommendationReport] = None
    health_per_language: Optional[List[dict]]               = None
    quality_coverage: Optional[QualityCoverageScore]        = None
    # ── ML & Legacy modernization fields ──────────────────────────────────
    ml_predictions:     Optional[dict]                      = None
    legacy_modernization: Optional[dict]                    = None


class CodeAnalyzer:
    """
    Orchestrates the end-to-end analysis pipeline for a single repository.

    Parameters
    ----------
    repo_path  : Local path to the cloned repository
    repo_meta  : Optional RepoMetadata from GitHubFetcher
    users      : Estimated user count (survey field for Business Impact)
    revenue    : Estimated annual revenue impact in USD
    """

    _ANALYZERS = {
        # ── Original five ────────────────────────────────────────────────────
        "python":     PythonAnalyzer,
        "java":       JavaAnalyzer,
        "dotnet":     DotNetAnalyzer,
        "javascript": JavaScriptAnalyzer,
        "mainframe":  MainframeAnalyzer,
        # ── Database / SQL ───────────────────────────────────────────────────
        "sql":        SQLAnalyzer,
        "db2":        DB2Analyzer,
        # ── Enterprise Java / Web ────────────────────────────────────────────
        "jsp":        JSPAnalyzer,
        "was":        WASAnalyzer,
        # ── Modern backend ───────────────────────────────────────────────────
        "go":         GoAnalyzer,
        "rust":       RustAnalyzer,
        "kotlin":     KotlinAnalyzer,
        "scala":      ScalaAnalyzer,
        "ruby":       RubyAnalyzer,
        "php":        PHPAnalyzer,
        # ── Systems programming ──────────────────────────────────────────────
        "cpp":        CppAnalyzer,
        # ── Scripting / DevOps ───────────────────────────────────────────────
        "shell":      ShellAnalyzer,
        "groovy":     GroovyAnalyzer,
        # ── Data / Mobile ────────────────────────────────────────────────────
        "r":          RAnalyzer,
        "dart":       DartAnalyzer,
    }

    # Function: __init__
    def __init__(
        self,
        repo_path:  Path,
        repo_meta:  Optional[RepoMetadata] = None,
        users:      int   = 100,
        revenue:    float = 0.0,
    ):
        self.repo_path = repo_path
        self.repo_meta = repo_meta
        self.users     = users
        self.revenue   = revenue

    # ──────────────────────────────────────────────────────────────────────────
    # Public entry point
    # ──────────────────────────────────────────────────────────────────────────

    # Function: _run_language_analyzers
    def _run_language_analyzers(self, detected: List[str], _pb) -> List[LanguageReport]:
        """Step 2: run every detected language analyser in parallel."""
        lang_reports: List[LanguageReport] = []

        # Function: _run_lang
        def _run_lang(lang: str) -> LanguageReport | None:
            analyzer_cls = self._ANALYZERS[lang]
            logger.info("Running %s analyser …", lang)
            try:
                report = analyzer_cls(self.repo_path).analyse()
                if report.file_count > 0:
                    logger.info(
                        "  → %s: %d files, %d SLOC, avg CC=%.1f",
                        lang, report.file_count, report.total_sloc, report.avg_complexity
                    )
                    return report
            except Exception as exc:
                logger.error("Analyser %s failed: %s", lang, exc)
            return None

        with ThreadPoolExecutor(max_workers=min(len(detected) or 1, 5)) as pool:
            futures = {pool.submit(_run_lang, lang): lang for lang in detected}
            done_count = 0
            for fut in as_completed(futures):
                result_report = fut.result()
                if result_report is not None:
                    lang_reports.append(result_report)
                done_count += 1
                pct = 12 + int(done_count / max(len(detected), 1) * 28)
                langs_done = ", ".join(futures[f] for f in futures if f.done())
                _pb(pct, f"Parsed {done_count}/{len(detected)} language(s) …")

        return lang_reports

    # Function: _collect_language_deps
    @staticmethod
    def _collect_language_deps(lang_reports: List[LanguageReport]) -> "tuple[set, set, set, set]":
        """Collect all dependencies across languages, bucketed by ecosystem."""
        py_deps  = set()
        jv_deps  = set()
        dn_deps  = set()
        js_deps  = set()
        for r in lang_reports:
            if r.language == "Python":
                py_deps |= r.dependencies
            elif r.language == "Java":
                jv_deps |= r.dependencies
            elif r.language == ".NET":
                dn_deps |= r.dependencies
            elif r.language in ("JavaScript", "JavaScript/TypeScript"):
                js_deps |= r.dependencies
        return py_deps, jv_deps, dn_deps, js_deps

    # Function: _run_deep_analyses
    def _run_deep_analyses(self, lang_reports: List[LanguageReport]):
        """Step 5: green impact, architecture, cloud-service and per-language health, in parallel."""
        all_deps_set: set = set()
        for r in lang_reports:
            all_deps_set |= r.dependencies

        # Function: _run_green
        def _run_green():        return GreenImpactCalculator().calculate(self.repo_path)
        # Function: _run_arch
        def _run_arch():         return ArchitectureLayerAnalyzer().analyse(self.repo_path)
        # Function: _run_cloud_recs
        def _run_cloud_recs():   return CloudRecommendationCalculator().calculate(
                                     repo_path=self.repo_path,
                                     languages=[r.language for r in lang_reports],
                                     dependencies=all_deps_set)
        # Function: _run_health_lang
        def _run_health_lang():  return SoftwareHealthCalculator().calculate_per_language(lang_reports)

        green_impact = architecture = cloud_recs = health_per_lang = None
        with ThreadPoolExecutor(max_workers=4) as pool:
            f_green   = pool.submit(_run_green)
            f_arch    = pool.submit(_run_arch)
            f_crecs   = pool.submit(_run_cloud_recs)
            f_hperlang = pool.submit(_run_health_lang)
            try: green_impact    = f_green.result(timeout=120)
            except Exception as e: logger.error("green_impact failed: %s", e)
            try: architecture    = f_arch.result(timeout=120)
            except Exception as e: logger.error("architecture failed: %s", e)
            try: cloud_recs      = f_crecs.result(timeout=120)
            except Exception as e: logger.error("cloud_recs failed: %s", e)
            try: health_per_lang = f_hperlang.result(timeout=60)
            except Exception as e: logger.error("health_per_lang failed: %s", e)

        return green_impact, architecture, cloud_recs, health_per_lang

    # Function: _run_ml_predictions
    @staticmethod
    def _run_ml_predictions(lang_reports: List[LanguageReport], _pb):
        """Step 6: rule-based/statistical ML predictions over the collected language reports."""
        try:
            from services.ml_predictions import MLPredictionEngine

            class _ResultProxy:
                language_reports = lang_reports

            ml_preds_obj = MLPredictionEngine(_ResultProxy()).run()
            ml_preds = {
                "defect_predictions": [
                    {
                        "file":        d.file,
                        "probability": d.probability,
                        "confidence":  d.confidence,
                        "factors":     d.factors,
                        "risk_level":  d.risk_level,
                    }
                    for d in ml_preds_obj.defect_predictions[:50]  # cap at 50 for payload
                ],
                "migration_score":  ml_preds_obj.migration_score,
                "tech_fingerprint": ml_preds_obj.tech_fingerprint,
                "effort_estimates": ml_preds_obj.effort_estimates,
                "anomalies": [
                    {
                        "file":    a.file,
                        "metric":  a.metric,
                        "value":   a.value,
                        "z_score": a.z_score,
                    }
                    for a in ml_preds_obj.anomalies[:20]
                ],
                "top_risk_files": ml_preds_obj.top_risk_files,
                "summary":        ml_preds_obj.summary,
            }
            _pb(95, "ML predictions complete.")
            return ml_preds
        except Exception as exc:
            logger.error("ML predictions failed: %s", exc)
            return None

    # Function: run
    def run(self, progress_cb=None) -> AnalysisResult:
        """
        Execute the full analysis pipeline and return an AnalysisResult.

        Parameters
        ----------
        progress_cb : callable(pct: int, message: str) | None
            Optional callback invoked at each pipeline stage with
            (percent_complete, human_readable_message).
        """
        # Function: _pb
        def _pb(pct: int, msg: str):
            logger.info("[%d%%] %s", pct, msg)
            if progress_cb:
                progress_cb(pct, msg)

        _pb(5, "Scanning repository structure …")

        # ── Step 1: Detect which languages are present ─────────────────
        detected = self._detect_languages()
        logger.info("Detected languages: %s", detected)

        if not detected:
            logger.warning("No supported source files found in %s", self.repo_path)

        _pb(12, f"Languages detected: {', '.join(detected) or 'none'} — parsing files …")

        # ── Step 2: Run language analysers IN PARALLEL ────────────────────────
        lang_reports = self._run_language_analyzers(detected, _pb)

        _pb(42, "Calculating software health & technical debt …")
        # ── Step 3: Metrics ─────────────────────────────────────
        health = SoftwareHealthCalculator().calculate(lang_reports) \
                 if lang_reports else _empty_health()

        debt   = TechnicalDebtCalculator().calculate(lang_reports, health.health) \
                 if lang_reports else _empty_debt()

        _pb(48, "Evaluating cloud readiness …")
        cloud  = CloudMaturityCalculator().calculate(self.repo_path, self.repo_meta)

        # CO₂ reduction potential
        total_sloc_val = sum(r.total_sloc for r in lang_reports)
        co2 = Co2ReductionCalculator().calculate(
            total_sloc  = total_sloc_val,
            cloud_score = cloud.total,
        )

        # Collect all dependencies across languages
        py_deps, jv_deps, dn_deps, js_deps = self._collect_language_deps(lang_reports)

        _pb(54, f"Auditing {len(py_deps)+len(js_deps)} open-source dependencies …")
        oss = OpenSourceSafetyCalculator().calculate(
            python_deps=py_deps,
            java_deps=jv_deps,
            dotnet_deps=dn_deps,
            repo_path=self.repo_path,
            js_deps=js_deps,
        )

        _pb(62, "Calculating business impact …")
        impact  = BusinessImpactCalculator().calculate(
            repo_meta        = self.repo_meta,
            users            = self.users,
            revenue_usd      = self.revenue,
            dependency_count = len(py_deps) + len(jv_deps) + len(dn_deps) + len(js_deps),
        )

        # ── Step 4: Bundle result ─────────────────────────────────────────
        repo_name = (
            self.repo_meta.full_name
            if self.repo_meta
            else self.repo_path.name
        )
        repo_url = (
            self.repo_meta.url
            if self.repo_meta
            else ""
        )

        _pb(68, "Running green impact, architecture & cloud-service analysis in parallel …")
        # ── Step 5: Deep analyses IN PARALLEL ───────────────────────────────
        green_impact, architecture, cloud_recs, health_per_lang = self._run_deep_analyses(lang_reports)

        _pb(92, "Compiling final report …")

        quality_coverage = QualityCoverageCalculator().calculate(
            language_reports=lang_reports,
            health=health,
            debt=debt,
            oss=oss,
            green_impact=green_impact,
        )

        # ── Step 6: ML predictions ──────────────────────────────────────────
        ml_preds = self._run_ml_predictions(lang_reports, _pb)

        return AnalysisResult(
            repo_name             = repo_name,
            repo_url              = repo_url,
            total_sloc            = sum(r.total_sloc  for r in lang_reports),
            total_files           = sum(r.file_count  for r in lang_reports),
            languages_detected    = [r.language for r in lang_reports],
            language_reports      = lang_reports,
            health                = health,
            debt                  = debt,
            cloud                 = cloud,
            oss                   = oss,
            impact                = impact,
            co2                   = co2,
            green_impact          = green_impact,
            architecture          = architecture,
            cloud_recommendations = cloud_recs,
            health_per_language   = health_per_lang,
            quality_coverage      = quality_coverage,
            ml_predictions        = ml_preds,
            legacy_modernization  = None,   # populated by AI analysis job
        )

    # ──────────────────────────────────────────────────────────────────────────
    # Language detection
    # ──────────────────────────────────────────────────────────────────────────

    # Function: _detect_languages
    def _detect_languages(self) -> List[str]:
        """
        Walk the repo and return a list of detected language keys whose file
        extensions are present.

        Uses os.walk with in-place dirnames pruning so skip directories
        (node_modules, target, .venv, …) are never descended into, avoiding the
        performance penalty of Path.rglob("*") which visits every node first.
        """
        if self.repo_path is None or not self.repo_path.exists():
            logger.warning("_detect_languages: repo_path is None or missing (%s)", self.repo_path)
            return []

        found_exts: Dict[str, bool] = {lang: False for lang in self._ANALYZERS}
        skip = {".git", "node_modules", "vendor", "venv", ".venv",
                "target", "bin", "obj", "__pycache__"}

        for dirpath, dirnames, filenames in os.walk(str(self.repo_path)):
            # Prune skip dirs IN PLACE — os.walk will not descend into them
            dirnames[:] = [d for d in dirnames if d not in skip]
            for fname in filenames:
                suffix = os.path.splitext(fname)[1]
                for lang, exts in LANGUAGE_EXTENSIONS.items():
                    if suffix in exts:
                        found_exts[lang] = True

        return [lang for lang, present in found_exts.items() if present]


# ── Fallback factories for empty repos ────────────────────────────────────────

# Function: _empty_health
def _empty_health():
    from metrics.software_health import HealthScore
    return HealthScore(
        resiliency=0, agility=0, elegance=0,
        health=0, risk_label="CRITICAL", summary=["No source files found"]
    )


# Function: _empty_debt
def _empty_debt():
    from metrics.technical_debt import TechnicalDebtScore
    return TechnicalDebtScore(
        total_sloc=0, total_ksloc=0, estimated_effort=0,
        debt_months=0, debt_ftes=0, debt_usd=0,
        debt_ratio=0, density=0, risk_label="LOW"
    )
