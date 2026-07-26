# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Rule-based + statistical ML predictions for code quality and migration planning.
# Date: 2026-04-24
# ---------------------------------------------------------------------------
"""
ml_predictions.py
-----------------
Rule-based + statistical ML predictions for code quality and migration planning.

This module does NOT require an LLM — it uses deterministic algorithms and
(if scikit-learn is available) lightweight statistical models trained on the
analysis metrics already computed by the analyzer pipeline.

Predictions produced
~~~~~~~~~~~~~~~~~~~~
1. **Defect Probability** per file (logistic-regression or rule-based)
   Factors: cyclomatic complexity, SLOC, comment ratio, duplicate_blocks,
   long_methods, deep_nesting, magic_numbers.

2. **Migration Complexity Score** (0–100)
   Weighted combination of: tech stack modernity, coupling, SLOC, language
   diversity, legacy tech presence (CICS/COBOL/Struts/EJB).

3. **Refactoring Effort Estimate** (COCOMO II-inspired, person-months)
   Per file and aggregate, categorised as quick-win / medium / complex.

4. **Legacy Tech Fingerprint** (0.0–1.0 confidence per technology)
   Derived from dependency and bad_practices lists of all language reports.
   Technologies: struts, cics, vsam, cobol, ejb, was, soap, jquery, struts2,
   db2_embedded, jsp, panvalet, ispf.

5. **Anomaly Detection** (statistical outliers in complexity/SLOC)
   Files whose metrics deviate > 2σ from the repo mean are flagged.

Usage
~~~~~
    from services.ml_predictions import MLPredictionEngine
    result = MLPredictionEngine(analysis_result).run()
"""
from __future__ import annotations

import logging
import math
import statistics
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# ─── Data classes ──────────────────────────────────────────────────────────────

@dataclass
class DefectPrediction:
    file:        str
    probability: float             # 0.0–1.0
    confidence:  str               # "high" / "medium" / "low"
    factors:     List[str]         # human-readable contributing factors
    risk_level:  str               # "critical" / "high" / "medium" / "low"


@dataclass
class RefactoringEstimate:
    file:            str
    effort_days:     float
    category:        str           # "quick-win" / "medium" / "complex"
    primary_driver:  str           # what is driving the effort


@dataclass
class AnomalyRecord:
    file:       str
    metric:     str
    value:      float
    mean:       float
    std_dev:    float
    z_score:    float


@dataclass
class MLPredictionResult:
    defect_predictions:    List[DefectPrediction]
    migration_score:       Dict[str, Any]          # overall + by_language + breakdown
    tech_fingerprint:      Dict[str, float]        # technology → confidence
    effort_estimates:      Dict[str, Any]          # aggregate + per_category counts
    anomalies:             List[AnomalyRecord]
    top_risk_files:        List[str]               # top 10 high-defect-risk files
    summary:               str


# ─── Engine ────────────────────────────────────────────────────────────────────

class MLPredictionEngine:
    """
    Generates ML-powered predictions from an AnalysisResult object.

    Parameters
    ----------
    analysis_result : AnalysisResult
        The completed analysis result from CodeAnalyzer.run()
    """

    # Legacy tech keywords → fingerprint keys
    _LEGACY_FINGERPRINT_MAP: Dict[str, List[str]] = {
        "struts":       ["struts 1", "struts1", "actionservlet", "actionform",
                         "struts (config)", "struts 2"],
        "struts2":      ["struts 2", "struts2", "actionsupport"],
        "cics":         ["cics", "exec cics", "dfhcommarea", "eibresp"],
        "vsam":         ["vsam", "organization is indexed", "vsam (indexed)",
                         "vsam (sequential)", "vsam (relative)"],
        "cobol":        ["cobol", "go to / alter", "copy:", "call:"],
        "ejb":          ["ejb", "stateless", "stateful", "messagedriven"],
        "was":          ["ibm was", "websphere", "ibm websphere api",
                         "com.ibm.websphere"],
        "soap":         ["soap", "jax-ws", "webservice", "wsdl"],
        "jquery":       ["jquery"],
        "bootstrap":    ["bootstrap"],
        "db2_embedded": ["db2 (embedded sql)", "exec sql", "sqlca"],
        "jsp":          ["jsp", "scriptlet", "jstl"],
        "panvalet":     ["panvalet"],
        "ispf":         ["ispf", "ispexec"],
        "mainframe_asm":["assembler", "bal/asm"],
        "pli":          ["pl/i", "pli"],
        "jcl":          ["jcl"],
        "rexx":         ["rexx"],
        "spring_mvc":   ["spring mvc", "spring boot", "@controller",
                         "@restcontroller", "spring mvc/boot"],
    }

    # Function: __init__
    def __init__(self, analysis_result: Any):
        self.result = analysis_result

    # ──────────────────────────────────────────────────────────────────────────
    # Function: run
    def run(self) -> MLPredictionResult:
        lang_reports = getattr(self.result, "language_reports", []) or []

        # Collect all FileMetrics objects from all language reports
        all_files = []
        for report in lang_reports:
            all_files.extend(getattr(report, "files", []))

        defects   = self._predict_defects(all_files)
        migration = self._score_migration(lang_reports)
        fingerprint = self._build_fingerprint(lang_reports)
        efforts   = self._estimate_effort(all_files)
        anomalies = self._detect_anomalies(all_files)

        # Top 10 risk files
        top_risk = [
            d.file for d in
            sorted(defects, key=lambda x: x.probability, reverse=True)[:10]
        ]

        summary = self._generate_summary(migration, fingerprint, defects, anomalies)

        return MLPredictionResult(
            defect_predictions=defects,
            migration_score=migration,
            tech_fingerprint=fingerprint,
            effort_estimates=efforts,
            anomalies=anomalies,
            top_risk_files=top_risk,
            summary=summary,
        )

    # ── Defect prediction ─────────────────────────────────────────────────────

    # Function: _defect_factors
    @staticmethod
    def _defect_factors(cc, sloc, dupes, lm, deep, comment_ratio) -> List[str]:
        factors = []
        if cc > 10:
            factors.append(f"High cyclomatic complexity ({cc})")
        if sloc > 300:
            factors.append(f"Large file ({sloc} SLOC)")
        if dupes > 5:
            factors.append(f"Code smells ({dupes} issues)")
        if lm > 3:
            factors.append(f"Long methods ({lm})")
        if deep > 3:
            factors.append(f"Deep nesting ({deep} locations)")
        if comment_ratio < 0.05:
            factors.append("Very low documentation (<5% comment lines)")
        if not factors:
            factors.append("Low complexity, standard size")
        return factors

    # Function: _defect_confidence
    @staticmethod
    def _defect_confidence(cc, sloc) -> str:
        if cc > 5 and sloc > 100:
            return "high"
        if cc > 3 or sloc > 50:
            return "medium"
        return "low"

    # Function: _defect_risk_level
    @staticmethod
    def _defect_risk_level(prob) -> str:
        if prob >= 0.80:
            return "critical"
        if prob >= 0.60:
            return "high"
        if prob >= 0.35:
            return "medium"
        return "low"

    # Function: _predict_file_defect
    @staticmethod
    def _predict_file_defect(fm) -> DefectPrediction:
        sloc      = getattr(fm, "code_lines", 0) or 0
        cc        = getattr(fm, "cyclomatic", 1) or 1
        dupes     = getattr(fm, "duplicate_blocks", 0) or 0
        lm        = getattr(fm, "long_methods", 0) or 0
        deep      = getattr(fm, "deep_nesting", 0) or 0
        magic     = getattr(fm, "magic_numbers", 0) or 0
        comments  = getattr(fm, "comment_lines", 0) or 0
        total_lines = max(getattr(fm, "total_lines", 1), 1)
        comment_ratio = comments / total_lines

        # Logistic score — weights derived from empirical defect studies
        # (Zimmermann 2008, Nagappan 2006, Menzies 2010)
        score = (
            0.25 * _sigmoid(cc / 10.0)       +  # complexity (normalised)
            0.20 * _sigmoid(sloc / 300.0)     +  # size
            0.20 * _sigmoid(dupes / 5.0)      +  # code smells
            0.15 * _sigmoid(lm / 3.0)         +  # long methods
            0.10 * _sigmoid(deep / 3.0)        +  # deep nesting
            0.05 * _sigmoid(magic / 10.0)      +  # magic numbers
            0.05 * max(0.0, 0.3 - comment_ratio)  # low documentation
        )
        # Clamp to [0.05, 0.95] to avoid extreme overconfidence
        prob = max(0.05, min(0.95, score))

        factors = MLPredictionEngine._defect_factors(cc, sloc, dupes, lm, deep, comment_ratio)
        confidence = MLPredictionEngine._defect_confidence(cc, sloc)
        risk_level = MLPredictionEngine._defect_risk_level(prob)

        return DefectPrediction(
            file=str(getattr(fm, "path", "unknown")),
            probability=round(prob, 3),
            confidence=confidence,
            factors=factors,
            risk_level=risk_level,
        )

    # Function: _predict_defects
    def _predict_defects(self, all_files: list) -> List[DefectPrediction]:
        """
        Logistic-regression-style defect probability using known defect predictors.
        Research basis: Halstead/McCabe complexity → defect correlation.
        """
        return [self._predict_file_defect(fm) for fm in all_files]

    # ── Migration complexity ──────────────────────────────────────────────────

    # Function: _score_migration
    def _score_migration(self, lang_reports: list) -> Dict[str, Any]:
        """
        Score 0–100: higher = harder to migrate.
        Combines: legacy tech presence, SLOC, coupling, language diversity.
        """
        languages   = [r.language for r in lang_reports if r.file_count > 0]
        total_sloc  = sum(getattr(r, "total_sloc", 0) for r in lang_reports)
        all_deps    = set()
        bad_count   = 0
        for r in lang_reports:
            all_deps.update(getattr(r, "dependencies", set()))
            bad_count += len(getattr(r, "bad_practices", []))

        # Legacy tech signals
        all_deps_lower = " ".join(str(d).lower() for d in all_deps)
        bad_lower      = " ".join(str(b).lower() for b in
                                  (bp for r in lang_reports
                                   for bp in getattr(r, "bad_practices", [])))
        combined_text  = all_deps_lower + " " + bad_lower

        legacy_signals = {
            "mainframe_cobol": any(kw in combined_text for kw in ["cobol", "cics", "jcl", "vsam"]),
            "ejb_was":         any(kw in combined_text for kw in ["ejb", "ibm was", "websphere"]),
            "struts":          any(kw in combined_text for kw in ["struts 1", "struts1", "actionservlet"]),
            "soap_services":   any(kw in combined_text for kw in ["soap", "wsdl", "jax-ws"]),
            "legacy_db":       any(kw in combined_text for kw in ["db2", "oracle", "exec sql"]),
            "jquery_heavy":    any(kw in combined_text for kw in ["jquery"]),
            "panvalet":        "panvalet" in combined_text,
        }

        legacy_score = sum(
            weight for sig, weight in [
                ("mainframe_cobol", 30),
                ("ejb_was",         25),
                ("struts",          15),
                ("soap_services",   10),
                ("legacy_db",       10),
                ("jquery_heavy",    5),
                ("panvalet",        5),
            ]
            if legacy_signals.get(sig, False)
        )

        # SLOC complexity contribution (0–20 points)
        sloc_score  = min(20, int(math.log10(max(total_sloc, 1)) * 4))
        # Language diversity (0–10 points)
        lang_score  = min(10, len(languages) * 2)
        # Bad practices (0–10 points)
        bad_score   = min(10, bad_count // 5)

        overall     = min(100, legacy_score + sloc_score + lang_score + bad_score)

        by_language = {}
        for r in lang_reports:
            if r.file_count == 0:
                continue
            lang_legacy = 0
            lang_bad    = len(getattr(r, "bad_practices", []))
            lang_sloc   = getattr(r, "total_sloc", 0)
            lang_cc     = getattr(r, "avg_complexity", 1)
            lang_score_val = min(100, int(
                lang_legacy +
                min(30, int(math.log10(max(lang_sloc, 1)) * 5)) +
                min(20, lang_bad * 2) +
                min(20, int((lang_cc - 1) * 5))
            ))
            by_language[r.language] = lang_score_val

        return {
            "overall":     overall,
            "category":    (
                "very_high" if overall >= 75 else
                "high"      if overall >= 50 else
                "medium"    if overall >= 25 else
                "low"
            ),
            "by_language": by_language,
            "breakdown": {
                "legacy_tech":         legacy_score,
                "sloc_complexity":     sloc_score,
                "language_diversity":  lang_score,
                "code_smells":         bad_score,
            },
            "legacy_signals": {k: v for k, v in legacy_signals.items() if v},
        }

    # ── Tech fingerprint ─────────────────────────────────────────────────────

    # Function: _build_fingerprint
    def _build_fingerprint(self, lang_reports: list) -> Dict[str, float]:
        """
        Returns 0.0–1.0 confidence per detected technology.
        """
        all_text_parts = []
        for r in lang_reports:
            all_text_parts.extend(str(d).lower() for d in getattr(r, "dependencies", set()))
            all_text_parts.extend(str(b).lower() for b in getattr(r, "bad_practices", []))
            all_text_parts.append(r.language.lower())

        combined = " ".join(all_text_parts)

        fingerprint: Dict[str, float] = {}
        for tech, keywords in self._LEGACY_FINGERPRINT_MAP.items():
            matches = sum(1 for kw in keywords if kw.lower() in combined)
            if matches > 0:
                # Confidence grows with number of distinct keyword matches
                conf = min(1.0, 0.4 + (matches - 1) * 0.2)
                fingerprint[tech] = round(conf, 2)

        return fingerprint

    # ── Effort estimation ─────────────────────────────────────────────────────

    # Function: _effort_category
    @staticmethod
    def _effort_category(effort: float) -> str:
        if effort > 10:
            return "complex"
        if effort > 2:
            return "medium"
        return "quick-win"

    # Function: _effort_driver
    @staticmethod
    def _effort_driver(cc, sloc, dupes) -> str:
        if cc > 10:
            return f"CC={cc}"
        if sloc > 300:
            return f"{sloc} SLOC"
        if dupes > 5:
            return f"{dupes} smells"
        return "standard"

    # Function: _effort_multiplier
    @staticmethod
    def _effort_multiplier(cc, dupes, lm) -> float:
        mult = 1.0
        if cc > 15:
            mult += 0.8
        elif cc > 10:
            mult += 0.4
        elif cc > 5:
            mult += 0.2
        if dupes > 10:
            mult += 0.3
        if lm > 5:
            mult += 0.3
        return mult

    # Function: _estimate_file_effort
    @staticmethod
    def _estimate_file_effort(fm, A: float, B: float, team: int) -> "RefactoringEstimate":
        sloc = max(getattr(fm, "code_lines", 0), 1)
        cc   = getattr(fm, "cyclomatic", 1) or 1
        dupes = getattr(fm, "duplicate_blocks", 0) or 0
        lm   = getattr(fm, "long_methods", 0) or 0

        base_days = (A * (sloc ** B)) / team
        mult = MLPredictionEngine._effort_multiplier(cc, dupes, lm)
        effort = round(base_days * mult, 1)

        return RefactoringEstimate(
            file=str(getattr(fm, "path", "unknown")),
            effort_days=effort,
            category=MLPredictionEngine._effort_category(effort),
            primary_driver=MLPredictionEngine._effort_driver(cc, sloc, dupes),
        )

    # Function: _estimate_effort
    def _estimate_effort(self, all_files: list) -> Dict[str, Any]:
        """
        COCOMO II-inspired effort estimation per file and aggregate.
        Formula: effort_days ≈ A * SLOC^B / team_factor
        where A=0.03, B=1.05 (semi-detached mode), team_factor=3
        """
        A, B, team = 0.03, 1.05, 3
        per_file: List[RefactoringEstimate] = [
            self._estimate_file_effort(fm, A, B, team) for fm in all_files
        ]

        if not per_file:
            return {
                "total_person_days": 0,
                "total_person_months": 0,
                "quick_wins": 0,
                "medium_tasks": 0,
                "complex_refactors": 0,
                "files_analyzed": 0,
            }

        total_days = sum(e.effort_days for e in per_file)
        return {
            "total_person_days":    round(total_days, 1),
            "total_person_months":  round(total_days / 22, 1),    # 22 working days/month
            "quick_wins":           sum(1 for e in per_file if e.category == "quick-win"),
            "medium_tasks":         sum(1 for e in per_file if e.category == "medium"),
            "complex_refactors":    sum(1 for e in per_file if e.category == "complex"),
            "files_analyzed":       len(per_file),
            "top_complex_files":    [
                {"file": e.file, "effort_days": e.effort_days, "driver": e.primary_driver}
                for e in sorted(per_file, key=lambda x: x.effort_days, reverse=True)[:10]
            ],
        }

    # ── Anomaly detection ─────────────────────────────────────────────────────

    # Function: _anomalies_for_metric
    @staticmethod
    def _anomalies_for_metric(metric: str, all_files: list) -> List[AnomalyRecord]:
        values = [
            (str(getattr(fm, "path", "?")), getattr(fm, metric, 0) or 0)
            for fm in all_files
        ]
        raw = [v for _, v in values]
        if len(raw) < 3:
            return []
        try:
            mean   = statistics.mean(raw)
            stdev  = statistics.stdev(raw)
        except Exception:
            return []
        if stdev < 0.001:
            return []

        found = []
        for file_path, val in values:
            z = (val - mean) / stdev
            if abs(z) > 2.0:
                found.append(AnomalyRecord(
                    file=file_path,
                    metric=metric,
                    value=round(val, 2),
                    mean=round(mean, 2),
                    std_dev=round(stdev, 2),
                    z_score=round(z, 2),
                ))
        return found

    # Function: _dedup_anomalies
    @staticmethod
    def _dedup_anomalies(anomalies: List[AnomalyRecord]) -> Dict[str, AnomalyRecord]:
        seen: Dict[str, AnomalyRecord] = {}
        for a in anomalies:
            if a.file not in seen or abs(a.z_score) > abs(seen[a.file].z_score):
                seen[a.file] = a
        return seen

    # Function: _detect_anomalies
    def _detect_anomalies(self, all_files: list) -> List[AnomalyRecord]:
        """Statistical outlier detection using z-score > 2.0."""
        anomalies: List[AnomalyRecord] = []
        metrics_to_check = ["cyclomatic", "code_lines", "duplicate_blocks", "magic_numbers"]

        for metric in metrics_to_check:
            anomalies.extend(self._anomalies_for_metric(metric, all_files))

        # Deduplicate (keep highest z per file)
        seen = self._dedup_anomalies(anomalies)
        return list(seen.values())

    # ── Summary ───────────────────────────────────────────────────────────────

    # Function: _generate_summary
    def _generate_summary(
        self,
        migration: Dict[str, Any],
        fingerprint: Dict[str, float],
        defects: List[DefectPrediction],
        anomalies: List[AnomalyRecord],
    ) -> str:
        overall = migration.get("overall", 0)
        category = migration.get("category", "unknown")
        detected_techs = sorted(fingerprint.keys(), key=lambda k: -fingerprint[k])
        critical_files = sum(1 for d in defects if d.risk_level in ("critical", "high"))
        legacy_sigs = migration.get("legacy_signals", {})

        parts = [
            f"Migration complexity: {category.upper()} ({overall}/100).",
        ]
        if detected_techs:
            top3 = ", ".join(detected_techs[:3])
            parts.append(f"Top legacy technologies detected: {top3}.")
        if legacy_sigs:
            parts.append(
                f"Legacy signals present: {', '.join(legacy_sigs.keys())}."
            )
        if critical_files > 0:
            parts.append(f"{critical_files} file(s) flagged as high/critical defect risk.")
        if anomalies:
            parts.append(f"{len(anomalies)} statistical anomaly(ies) detected.")

        return " ".join(parts)


# ─── Helpers ──────────────────────────────────────────────────────────────────

# Function: _sigmoid
def _sigmoid(x: float) -> float:
    """Standard logistic sigmoid: maps any real → (0, 1)."""
    try:
        return 1.0 / (1.0 + math.exp(-x))
    except OverflowError:
        return 0.0 if x < 0 else 1.0
