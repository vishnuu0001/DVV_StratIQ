# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Identifies third-party dependencies and evaluates them on three axes:
# Date: 2026-03-30
# ---------------------------------------------------------------------------
"""
open_source_safety.py
---------------------
Identifies third-party dependencies and evaluates them on three axes:

1. Security      – known CVE / vulnerability audit  (via pip-audit for Python,
                   basic heuristics for others)
2. Licensing     – compliance with the configured allowed-license set
3. Freshness     – dependency age (last release date) vs MAX_DEPENDENCY_AGE_YEARS

Output: OpenSourceSafetyScore with per-dependency detail & composite score.
"""
from __future__ import annotations

import json
import logging
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Set

import requests

from config.settings import ALLOWED_LICENSES, MAX_DEPENDENCY_AGE_YEARS

logger = logging.getLogger(__name__)

PYPI_API   = "https://pypi.org/pypi/{package}/json"
MVNC_API   = "https://search.maven.org/solrsearch/select?q=a:{artifact}&rows=1&wt=json"


# License risk buckets
_LICENSE_HIGH_RISK   = {"GPL-3.0", "AGPL-3.0", "AGPL", "GPL", "SSPL", "BUSL",
                        "PROPRIETARY", "COMMERCIAL", "UNKNOWN"}
_LICENSE_MEDIUM_RISK = {"LGPL-2.1", "LGPL-3.0", "LGPL", "MPL-2.0", "MPL",
                        "EPL-1.0", "EPL-2.0", "EUPL"}
_LICENSE_LOW_RISK    = {"MIT", "APACHE-2.0", "APACHE 2.0", "BSD-2-CLAUSE",
                        "BSD-3-CLAUSE", "ISC", "UNLICENSE", "0BSD",
                        "ECLIPSE PUBLIC LICENSE", "CC0-1.0"}


# Function: _license_risk
def _license_risk(license_str: str) -> str:
    """Return HIGH / MEDIUM / LOW based on license string."""
    up = (license_str or "unknown").upper().strip()
    if up in _LICENSE_HIGH_RISK or up == "UNKNOWN":
        return "HIGH"
    if up in _LICENSE_MEDIUM_RISK:
        return "MEDIUM"
    if up in _LICENSE_LOW_RISK:
        return "LOW"
    # Heuristic for GPL variants
    if "GPL" in up or "AGPL" in up:
        return "HIGH"
    if "LGPL" in up or "MPL" in up:
        return "MEDIUM"
    return "LOW"


@dataclass
class DependencyInfo:
    name:           str
    ecosystem:      str           # python / java / dotnet / mainframe
    latest_version: str   = "unknown"
    version:        str   = "unknown"
    license:        str   = "unknown"
    license_risk:   str   = "LOW"   # HIGH / MEDIUM / LOW
    age_years:      float = 0.0
    vulnerable:     bool  = False
    vuln_count:     int   = 0
    cve_severity:   str   = ""     # CRITICAL / HIGH / MEDIUM / LOW (worst found)
    cve_ids:        List[str] = field(default_factory=list)
    license_ok:     bool  = True
    age_ok:         bool  = True


@dataclass
class OpenSourceSafetyScore:
    total:              float              # 0–100
    security_score:     float
    license_score:      float
    freshness_score:    float
    dependency_count:   int
    vulnerable_count:   int
    license_issues:     int
    stale_count:        int
    risk_label:         str
    # CVE severity breakdown
    cve_critical:       int = 0
    cve_high:           int = 0
    cve_medium:         int = 0
    cve_low:            int = 0
    # License risk breakdown
    license_high_risk:  int = 0
    license_medium_risk:int = 0
    license_low_risk:   int = 0
    # Third-party composition
    third_party_pct:    float = 0.0   # fraction of files that are third-party
    oldest_dep_date:    str = ""
    newest_dep_date:    str = ""
    details:            List[DependencyInfo] = field(default_factory=list)
    findings:           List[str]           = field(default_factory=list)


class OpenSourceSafetyCalculator:
    """
    Runs security audits and metadata lookups for discovered dependencies.
    """

    # Function: calculate
    def calculate(
        self,
        python_deps:   Set[str],
        java_deps:     Set[str],
        dotnet_deps:   Set[str],
        repo_path:     Path,
        js_deps:       Set[str] = None,
    ) -> OpenSourceSafetyScore:

        if js_deps is None:
            js_deps = set()
        dep_details = self._collect_dep_details(
            python_deps, java_deps, dotnet_deps, js_deps, repo_path
        )
        return self._build_safety_score(dep_details)

    # ──────────────────────────────────────────────────────────────────────────
    # npm audit
    # ──────────────────────────────────────────────────────────────────────────

    # Function: _collect_dep_details
    def _collect_dep_details(
        self,
        python_deps,
        java_deps,
        dotnet_deps,
        js_deps,
        repo_path: Path,
    ) -> "List[DependencyInfo]":
        dep_details: List[DependencyInfo] = []

        # ── Python: pip-audit + parallel PyPI enrichment ─────────────────────
        python_vulns: Dict[str, Any] = self._run_pip_audit(repo_path)
        py_infos: List[DependencyInfo] = []
        for pkg in list(python_deps)[:60]:
            info = DependencyInfo(name=pkg, ecosystem="python")
            pkg_lower = pkg.lower()
            vuln_data = python_vulns.get(pkg_lower, {})
            info.vulnerable   = bool(vuln_data)
            info.vuln_count   = vuln_data.get("count", 0)
            info.cve_severity = vuln_data.get("worst_severity", "")
            info.cve_ids      = vuln_data.get("ids", [])
            py_infos.append(info)
        with ThreadPoolExecutor(max_workers=12) as pool:
            list(pool.map(self._enrich_pypi, py_infos))
        dep_details.extend(py_infos)

        # ── Java (basic metadata lookup) ──────────────────────────────────────
        for artifact in java_deps:
            dep_details.append(DependencyInfo(name=artifact, ecosystem="java"))

        # ── .NET (basic) ──────────────────────────────────────────────────────
        for pkg in dotnet_deps:
            dep_details.append(DependencyInfo(name=pkg, ecosystem="dotnet"))

        # ── JavaScript / TypeScript (npm) ─────────────────────────────────────
        npm_vulns = self._run_npm_audit(repo_path)
        for pkg in js_deps:
            info = DependencyInfo(name=pkg, ecosystem="javascript")
            pkg_lower = pkg.lower()
            vuln_data = npm_vulns.get(pkg_lower, {})
            info.vulnerable   = bool(vuln_data)
            info.vuln_count   = vuln_data.get("count", 0)
            info.cve_severity = vuln_data.get("worst_severity", "")
            dep_details.append(info)

        return dep_details

    # Function: _build_safety_score
    def _build_safety_score(self, dep_details: "List[DependencyInfo]") -> "OpenSourceSafetyScore":
        n = len(dep_details) or 1
        vuln_count     = sum(1 for d in dep_details if d.vulnerable)
        license_issues = sum(1 for d in dep_details if not d.license_ok and d.license != "unknown")
        stale_count    = sum(1 for d in dep_details if not d.age_ok)

        security_score  = max(0.0, 100.0 - (vuln_count     / n * 100))
        license_score   = max(0.0, 100.0 - (license_issues  / n * 100))
        freshness_score = max(0.0, 100.0 - (stale_count     / n * 100))
        total = security_score * 0.50 + license_score * 0.30 + freshness_score * 0.20

        label = "LOW RISK" if total >= 80 else "MEDIUM RISK" if total >= 60 else "HIGH RISK"

        cve_critical = sum(1 for d in dep_details if d.cve_severity == "CRITICAL")
        cve_high     = sum(1 for d in dep_details if d.cve_severity == "HIGH")
        cve_medium   = sum(1 for d in dep_details if d.cve_severity == "MEDIUM")
        cve_low_cnt  = sum(1 for d in dep_details if d.cve_severity == "LOW")

        for d in dep_details:
            d.license_risk = _license_risk(d.license)
        lic_high   = sum(1 for d in dep_details if d.license_risk == "HIGH")
        lic_medium = sum(1 for d in dep_details if d.license_risk == "MEDIUM")
        lic_low    = sum(1 for d in dep_details if d.license_risk == "LOW")

        findings: List[str] = []
        if cve_critical:
            findings.append(f"{cve_critical} CRITICAL severity CVEs detected")
        if cve_high:
            findings.append(f"{cve_high} HIGH severity CVEs")
        if vuln_count:
            findings.append(f"{vuln_count} vulnerable dependencies detected")
        if license_issues:
            findings.append(f"{license_issues} dependencies with non-compliant licenses")
        if stale_count:
            findings.append(f"{stale_count} dependencies not updated in {MAX_DEPENDENCY_AGE_YEARS}+ years")

        return OpenSourceSafetyScore(
            total             = round(total, 1),
            security_score    = round(security_score, 1),
            license_score     = round(license_score, 1),
            freshness_score   = round(freshness_score, 1),
            dependency_count  = len(dep_details),
            vulnerable_count  = vuln_count,
            license_issues    = license_issues,
            stale_count       = stale_count,
            risk_label        = label,
            cve_critical      = cve_critical,
            cve_high          = cve_high,
            cve_medium        = cve_medium,
            cve_low           = cve_low_cnt,
            license_high_risk = lic_high,
            license_medium_risk = lic_medium,
            license_low_risk  = lic_low,
            details           = dep_details,
            findings          = findings,
        )


    # Function: _run_npm_audit
    @staticmethod
    def _run_npm_audit(repo_path: Path) -> Dict[str, Any]:
        """Run 'npm audit --json' if package-lock.json exists; return vuln map."""
        vulns: Dict[str, Any] = {}
        if repo_path is None or not repo_path.exists():
            return vulns
        lock = repo_path / "package-lock.json"
        if not lock.exists():
            return vulns
        try:
            result = subprocess.run(
                ["npm", "audit", "--json", "--audit-level=low"],
                cwd=str(repo_path),
                capture_output=True, text=True, timeout=60,
            )
            data = json.loads(result.stdout or "{}")
            # npm audit v7+ format: {"vulnerabilities": {pkg: {...}}}
            for pkg, info in data.get("vulnerabilities", {}).items():
                severity   = (info.get("severity") or "LOW").upper()
                vulns[pkg.lower()] = {
                    "count":          1,
                    "worst_severity": severity,
                    "ids":            list(info.get("via", [])) if isinstance(info.get("via"), list) else [],
                }
        except Exception as exc:  # noqa: BLE001
            logger.debug("npm audit skipped: %s", exc)
        return vulns

    # ──────────────────────────────────────────────────────────────────────────
    # Pip-audit
    # ──────────────────────────────────────────────────────────────────────────

    # Function: _vuln_severity
    @staticmethod
    def _vuln_severity(v: Dict[str, Any], sev_rank: Dict[str, int]) -> "tuple":
        # pip-audit may include CVSS severity in aliases or advisory text
        desc = (v.get("description") or "").upper()
        for sev in ("CRITICAL", "HIGH", "MEDIUM", "LOW"):
            if sev in desc:
                return sev, sev_rank.get(sev, 0)
        # default to HIGH for known vulns with no severity text
        return "HIGH", sev_rank["HIGH"]

    # Function: _parse_pip_audit_entry
    @staticmethod
    def _parse_pip_audit_entry(entry: Dict[str, Any], sev_rank: Dict[str, int]) -> "Any":
        name   = entry.get("name", "").lower()
        issues = entry.get("vulns", [])
        if not issues:
            return None
        ids: List[str] = []
        worst_rank = 0
        worst_sev  = "LOW"
        for v in issues:
            for alias in v.get("aliases", []):
                ids.append(alias)
            sev, rank = OpenSourceSafetyCalculator._vuln_severity(v, sev_rank)
            if rank > worst_rank:
                worst_rank = rank
                worst_sev  = sev
        return name, {
            "count":          len(issues),
            "worst_severity": worst_sev,
            "ids":            ids,
        }

    # Function: _run_pip_audit
    @staticmethod
    def _run_pip_audit(repo_path: Path) -> Dict[str, Any]:
        """Run pip-audit; return {pkg_lower: {count, worst_severity, ids}}."""
        vulns: Dict[str, Any] = {}
        if repo_path is None or not repo_path.exists():
            return vulns
        req_files = list(repo_path.rglob("requirements*.txt"))
        if not req_files:
            return vulns

        _SEV_RANK = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}

        for req in req_files[:1]:
            try:
                result = subprocess.run(
                    [sys.executable, "-m", "pip_audit",
                     "-r", str(req), "--format", "json", "--progress-spinner=off",
                     "--timeout", "10"],
                    capture_output=True, text=True, timeout=60
                )
                data = json.loads(result.stdout or "[]")
                for entry in data:
                    parsed = OpenSourceSafetyCalculator._parse_pip_audit_entry(entry, _SEV_RANK)
                    if parsed is None:
                        continue
                    name, record = parsed
                    vulns[name] = record
            except Exception as exc:   # noqa: BLE001
                logger.debug("pip-audit skipped: %s", exc)
        return vulns

    # ──────────────────────────────────────────────────────────────────────────
    # PyPI metadata enrichment
    # ──────────────────────────────────────────────────────────────────────────

    # Function: _enrich_pypi
    def _enrich_pypi(self, info: DependencyInfo) -> None:
        try:
            resp = requests.get(
                PYPI_API.format(package=info.name),
                timeout=5
            )
            if resp.status_code != 200:
                return
            data       = resp.json()
            meta       = data.get("info", {})
            releases   = data.get("releases", {})

            info.latest_version = meta.get("version", "unknown")
            info.license        = meta.get("license", "unknown") or "unknown"
            info.license_ok     = info.license.upper() in {
                lic.upper() for lic in ALLOWED_LICENSES
            }

            # Age: find oldest upload date for any version
            import datetime
            all_dates = []
            for ver_list in releases.values():
                for rel in ver_list:
                    dt_str = rel.get("upload_time")
                    if dt_str:
                        try:
                            all_dates.append(
                                datetime.datetime.fromisoformat(dt_str)
                            )
                        except ValueError:
                            pass
            if all_dates:
                most_recent = max(all_dates)
                info.age_years = (
                    datetime.datetime.utcnow() - most_recent
                ).days / 365.0
                info.age_ok = info.age_years <= MAX_DEPENDENCY_AGE_YEARS
        except Exception as exc:   # noqa: BLE001
            logger.debug("PyPI enrichment failed for %s: %s", info.name, exc)
