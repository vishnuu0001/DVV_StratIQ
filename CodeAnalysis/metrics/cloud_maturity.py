# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Rates applications on their readiness for cloud deployment (0–100).
# Date: 2026-02-20
# ---------------------------------------------------------------------------
"""
cloud_maturity.py
-----------------
Rates applications on their readiness for cloud deployment (0–100).

Scoring Dimensions
~~~~~~~~~~~~~~~~~~
1. Stateless Design          (20 pts) – absence of local file I/O, in-process sessions
2. Containerization          (20 pts) – Dockerfile, docker-compose, .devcontainer
3. API Surface               (15 pts) – REST endpoint patterns, OpenAPI spec
4. Config Externalisation    (15 pts) – env-var usage, no hardcoded connection strings
5. Logging & Observability   (15 pts) – structured logging, health-check endpoints
6. CI/CD Artifacts           (15 pts) – GitHub Actions, Jenkinsfile, Azure Pipelines

Each dimension produces a 0–1 score; weights from settings.py are applied.
Repo metadata (topics, has_dockerfile, has_kubernetes) from GitHubFetcher
augments the file-scan results.
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from config.settings import CLOUD_WEIGHTS


@dataclass
class CloudMaturityScore:
    total:                   float           # 0–100
    stateless_design:        float           # 0–100
    containerization:        float           # 0–100
    api_surface:             float           # 0–100
    config_externalization:  float           # 0–100
    logging_observability:   float           # 0–100
    ci_cd_artifacts:         float           # 0–100
    risk_label:              str             # LOW / MEDIUM / HIGH
    # CloudReady breakdown (mirrors CAST Highlight)
    cloud_ready_scan:        float = 0.0    # code-scan sub-score
    boosters_score:          float = 0.0
    blockers_score:          float = 0.0
    roadblocks_count:        int   = 0
    boosters:  List[str] = field(default_factory=list)  # positive signals
    blockers:  List[str] = field(default_factory=list)  # migration obstacles
    findings:  List[str] = field(default_factory=list)


class CloudMaturityCalculator:
    """
    Analyses a cloned repository's file tree and optional RepoMetadata
    to produce a CloudMaturityScore.
    """

    # Patterns for each dimension
    _STATEFUL_IO       = re.compile(
        r'\b(open\s*\(|FileWriter|FileReader|fopen|StreamWriter|'
        r'File\.WriteAll|os\.path|shutil\.copy|Files\.write)\b'
    )
    _SESSION_STORE     = re.compile(
        r'\b(HttpSession|session\[|request\.session|InMemoryCache)\b',
        re.IGNORECASE
    )
    _API_PATTERNS      = re.compile(
        r'(@GetMapping|@PostMapping|@RestController|@app\.route|'
        r'\[HttpGet\]|\[HttpPost\]|app\.get\(|router\.get\(|'
        r'swagger|openapi)',
        re.IGNORECASE
    )
    _ENV_VAR           = re.compile(
        r'\b(os\.environ|os\.getenv|Environment\.GetEnvironmentVariable|'
        r'System\.getenv|process\.env|dotenv|ConfigurationManager)\b',
        re.IGNORECASE
    )
    _HARDCODED_CONN    = re.compile(
        r'(Server=|Data Source=|jdbc:mysql|jdbc:postgresql|'
        r'mongodb://|redis://|amqp://)',
        re.IGNORECASE
    )
    _LOGGING           = re.compile(
        r'\b(logging\.|logger\.|log\.|LogFactory|ILogger|'
        r'structlog|loguru|winston|serilog)\b',
        re.IGNORECASE
    )
    _HEALTH_CHECK      = re.compile(
        r'(/health|/readiness|/liveness|healthcheck|MapHealthChecks)',
        re.IGNORECASE
    )
    _CI_FILES          = {
        ".github/workflows", "Jenkinsfile", "azure-pipelines.yml",
        ".circleci", ".travis.yml", "gitlab-ci.yml",
        "bitbucket-pipelines.yml", "circle.yml"
    }

    # Function: _risk_label
    @staticmethod
    def _risk_label(total: float) -> str:
        if total >= 70:
            return "HIGH"
        if total >= 40:
            return "MEDIUM"
        return "LOW"

    # Function: _compute_findings
    @staticmethod
    def _compute_findings(
        stateless_score: float, stateful_hits: int, session_hits: int,
        container_score: float, api_score: float, conn_hits: int, ci_score: float,
    ) -> "List[str]":
        findings: List[str] = []
        if stateless_score < 50:
            findings.append(f"Stateful I/O / session patterns detected ({stateful_hits + session_hits} hits)")
        if container_score < 40:
            findings.append("No Dockerfile or docker-compose found")
        if api_score < 20:
            findings.append("No REST API framework patterns detected")
        if conn_hits:
            findings.append(f"Hardcoded connection strings found ({conn_hits})")
        if ci_score < 40:
            findings.append("No CI/CD pipeline configuration found")
        return findings

    # Function: _compute_boosters
    @staticmethod
    def _compute_boosters(
        has_docker: bool, has_compose: bool, has_k8s: bool, env_hits: int,
        api_hits: int, log_hits: int, health_hits: int, ci_score: float,
    ) -> "List[str]":
        boosters: List[str] = []
        if has_docker:
            boosters.append("Dockerfile present – container-ready (+)")
        if has_compose:
            boosters.append("docker-compose found – orchestration-ready (+)")
        if has_k8s:
            boosters.append("Kubernetes manifests detected – K8s-ready (+)")
        if env_hits > 0:
            boosters.append(f"Environment variable usage ({env_hits} hits) – 12-factor config (+)")
        if api_hits > 0:
            boosters.append(f"REST/API framework patterns ({api_hits} hits) – cloud-native APIs (+)")
        if log_hits > 0:
            boosters.append(f"Structured logging present ({log_hits} refs) – observability (+)")
        if health_hits > 0:
            boosters.append(f"Health-check endpoints detected ({health_hits}) – readiness probes (+)")
        if ci_score >= 70:
            boosters.append("CI/CD pipeline configured – automated deployment (+)")
        return boosters

    # Function: _compute_blockers
    @staticmethod
    def _compute_blockers(
        conn_hits: int, stateful_hits: int, session_hits: int,
        container_score: float, ci_score: float,
    ) -> "List[str]":
        blockers: List[str] = []
        if conn_hits > 0:
            blockers.append(f"Hardcoded connection strings ({conn_hits}) – blocks IaC migration")
        if stateful_hits > 5:
            blockers.append(f"Excessive local file I/O ({stateful_hits} hits) – stateful design")
        if session_hits > 3:
            blockers.append(f"In-process session storage ({session_hits} hits) – not horizontally scalable")
        if container_score == 0:
            blockers.append("No containerization artifacts – manual deployment required")
        if ci_score == 0:
            blockers.append("No CI/CD configuration – manual release process")
        return blockers

    # Function: calculate
    def calculate(
        self,
        repo_path: Path,
        repo_meta=None,    # Optional[RepoMetadata]
    ) -> CloudMaturityScore:

        if repo_path is None or not repo_path.exists():
            return CloudMaturityScore(
                total=0.0, stateless_design=0.0, containerization=0.0,
                api_surface=0.0, config_externalization=0.0,
                logging_observability=0.0, ci_cd_artifacts=0.0,
                risk_label="HIGH",
            )

        source_files = list(self._iter_code_files(repo_path))
        all_source   = self._concat_sources(source_files)

        # ── 1. Stateless Design ───────────────────────────────────────────────
        stateful_hits  = len(self._STATEFUL_IO.findall(all_source))
        session_hits   = len(self._SESSION_STORE.findall(all_source))
        penalty        = min(100, (stateful_hits + session_hits) * 5)
        stateless_score = max(0.0, 100.0 - penalty)

        # ── 2. Containerization ───────────────────────────────────────────────
        has_docker     = (repo_path / "Dockerfile").exists()
        has_compose    = any(repo_path.rglob("docker-compose*.yml"))
        has_k8s        = any(repo_path.rglob("*.yaml"))  and \
                         any(repo_path.rglob("*deployment*"))
        if repo_meta:
            has_docker = has_docker or repo_meta.has_dockerfile
            has_k8s    = has_k8s    or repo_meta.has_kubernetes
        container_score  = 40.0 * has_docker + 30.0 * has_compose + 30.0 * has_k8s

        # ── 3. API Surface ────────────────────────────────────────────────────
        api_hits       = len(self._API_PATTERNS.findall(all_source))
        api_score      = min(100.0, api_hits * 10)

        # ── 4. Config Externalisation ─────────────────────────────────────────
        env_hits      = len(self._ENV_VAR.findall(all_source))
        conn_hits     = len(self._HARDCODED_CONN.findall(all_source))
        config_score  = min(100.0, env_hits * 8) - min(50.0, conn_hits * 10)
        config_score  = max(0.0, config_score)

        # ── 5. Logging & Observability ────────────────────────────────────────
        log_hits      = len(self._LOGGING.findall(all_source))
        health_hits   = len(self._HEALTH_CHECK.findall(all_source))
        log_score     = min(70.0, log_hits * 5) + min(30.0, health_hits * 10)

        # ── 6. CI/CD Artifacts ────────────────────────────────────────────────
        ci_score      = self._detect_cicd(repo_path, repo_meta)

        # ── Weighted Total ────────────────────────────────────────────────────
        total = (
            CLOUD_WEIGHTS["stateless_design"]        * stateless_score
            + CLOUD_WEIGHTS["containerization"]      * container_score
            + CLOUD_WEIGHTS["api_surface"]           * api_score
            + CLOUD_WEIGHTS["config_externalization"]* config_score
            + CLOUD_WEIGHTS["logging_observability"] * log_score
            + CLOUD_WEIGHTS["ci_cd_artifacts"]       * ci_score
        )

        label = self._risk_label(total)

        findings = self._compute_findings(
            stateless_score, stateful_hits, session_hits, container_score, api_score, conn_hits, ci_score
        )

        # ── CloudReady Boosters / Blockers ──────────────────────────────────
        boosters = self._compute_boosters(
            has_docker, has_compose, has_k8s, env_hits, api_hits, log_hits, health_hits, ci_score
        )
        blockers = self._compute_blockers(
            conn_hits, stateful_hits, session_hits, container_score, ci_score
        )

        roadblocks_count = len(blockers)
        boosters_score   = min(100.0, len(boosters) * 12.5)
        blockers_score   = min(100.0, roadblocks_count * 20.0)
        cloud_ready_scan = max(0.0, total - blockers_score * 0.25)

        return CloudMaturityScore(
            total                  = round(total, 1),
            stateless_design       = round(stateless_score, 1),
            containerization       = round(container_score, 1),
            api_surface            = round(api_score, 1),
            config_externalization = round(config_score, 1),
            logging_observability  = round(log_score, 1),
            ci_cd_artifacts        = round(ci_score, 1),
            risk_label             = label,
            cloud_ready_scan       = round(cloud_ready_scan, 1),
            boosters_score         = round(boosters_score, 1),
            blockers_score         = round(blockers_score, 1),
            roadblocks_count       = roadblocks_count,
            boosters               = boosters,
            blockers               = blockers,
            findings               = findings,
        )

    # ──────────────────────────────────────────────────────────────────────────
    # Helpers
    # ──────────────────────────────────────────────────────────────────────────

    # Function: _iter_code_files
    @staticmethod
    def _iter_code_files(repo_path: Path, max_files: int = 1000):
        skip = {".git", "node_modules", "vendor", "venv", ".venv",
                "target", "bin", "obj", "__pycache__"}
        exts = {".py", ".java", ".cs", ".ts", ".js", ".yaml",
                ".yml", ".cbl", ".cob", ".xml", ".json"}
        _MAX_BYTES = 500_000
        count = 0
        for dirpath, dirnames, filenames in os.walk(str(repo_path)):
            dirnames[:] = [d for d in dirnames if d not in skip]
            dir_path = Path(dirpath)
            for fname in filenames:
                if count >= max_files:
                    return
                p = dir_path / fname
                if p.suffix not in exts:
                    continue
                try:
                    if p.stat().st_size > _MAX_BYTES:
                        continue
                except OSError:
                    continue
                count += 1
                yield p

    # Function: _concat_sources
    @staticmethod
    def _concat_sources(files) -> str:
        chunks: List[str] = []
        total_chars = 0
        _MAX_TOTAL = 200_000   # read at most ~200 KB of source for maturity heuristics
        for f in files:
            if total_chars >= _MAX_TOTAL:
                break
            try:
                text = f.read_text(encoding="utf-8", errors="replace")[:4000]
                chunks.append(text)
                total_chars += len(text)
            except OSError:
                pass
        return "\n".join(chunks)

    # Function: _detect_cicd
    def _detect_cicd(self, repo_path: Path, repo_meta=None) -> float:
        score = 0.0
        for ci_indicator in self._CI_FILES:
            # Check as file or directory
            if (repo_path / ci_indicator).exists():
                score = 100.0
                break
        if repo_meta and repo_meta.has_ci:
            score = max(score, 70.0)
        return score
