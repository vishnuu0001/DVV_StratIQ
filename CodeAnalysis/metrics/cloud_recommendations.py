# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Maps detected technologies, frameworks, and patterns to specific
# Date: 2026-03-02
# ---------------------------------------------------------------------------
"""
cloud_recommendations.py
------------------------
Maps detected technologies, frameworks, and patterns to specific
Azure cloud services — replicating the CAST Highlight
"Cloud Service Recommendation Summary" view.

Each recommendation maps:
  language/framework/pattern → Azure service → category

Output contains categories:
  Security & Identity, Container, Integration, Storage,
  Databases, AI + Machine Learning, Web, Compute, Analytics
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Set
import re

# ─── Category constants ────────────────────────────────────────────────────────
CAT_SECURITY    = "Security & Identity"
CAT_CONTAINER   = "Container"
CAT_INTEGRATION = "Integration"
CAT_STORAGE     = "Storage"
CAT_DATABASE    = "Databases"
CAT_AI          = "AI + Machine Learning"
CAT_WEB         = "Web"
CAT_COMPUTE     = "Compute"
CAT_ANALYTICS   = "Analytics"

# ─── Rule table ───────────────────────────────────────────────────────────────
@dataclass
class _MapRule:
    trigger_languages:  List[str]       # language names ("*" = any)
    trigger_patterns:   List[str]       # dependency/import names (lowercase substring)
    trigger_file_pats:  List[str]       # filenames (e.g. Dockerfile)
    azure_service:      str
    category:           str
    reason:             str             # short explanation


_RULES: List[_MapRule] = [
    # ── Containers ──────────────────────────────────────────────────────────
    _MapRule(["*"], [], ["Dockerfile", "docker-compose"],
             "Azure Kubernetes Service (AKS)", CAT_CONTAINER,
             "Container images detected in repo"),
    _MapRule(["*"], [], ["Dockerfile", "docker-compose"],
             "Azure Red Hat OpenShift", CAT_CONTAINER,
             "Container deployment alternative"),
    _MapRule(["*"], [], ["Dockerfile", "docker-compose"],
             "Azure Container Apps", CAT_CONTAINER,
             "Serverless container hosting"),

    # ── Databases ────────────────────────────────────────────────────────────
    _MapRule(["Python", "Java", ".NET"],
             ["psycopg2", "postgresql", "pg-", "spring-data-jpa", "entityframework",
              "npgsql", "hibernate", "jdbc:postgresql"],
             [],
             "Azure Database for PostgreSQL", CAT_DATABASE,
             "PostgreSQL driver/ORM dependency detected"),
    _MapRule(["Python", "Java", ".NET"],
             ["redis", "jedis", "stackexchange.redis", "aioredis"],
             [],
             "Azure Cache for Redis", CAT_DATABASE,
             "Redis cache dependency detected"),
    _MapRule(["Python", "Java", ".NET"],
             ["pymongo", "mongodb", "spring-data-mongodb", "mongoclient"],
             [],
             "Azure Cosmos DB", CAT_DATABASE,
             "MongoDB driver detected — Cosmos DB supports MongoDB API"),
    _MapRule(["Python", "Java", ".NET"],
             ["pymongo", "mongodb"],
             [],
             "MongoDB Atlas on Azure", CAT_DATABASE,
             "MongoDB Atlas alternative"),
    _MapRule(["Python", "Java", ".NET"],
             ["mysql", "mysqlconnector", "spring-data-mysql", "jdbc:mysql"],
             [],
             "Azure Database for MySQL", CAT_DATABASE,
             "MySQL driver/ORM dependency detected"),
    _MapRule(["Python", "Java", ".NET"],
             ["mssql", "sqlserver", "system.data.sqlclient", "microsoft.data.sqlclient"],
             [],
             "Azure SQL Database", CAT_DATABASE,
             "SQL Server driver detected"),

    # ── Storage ──────────────────────────────────────────────────────────────
    _MapRule(["*"],
             ["azure-storage", "boto3", "s3", "blobserviceclient", "azure.storage"],
             ["azure-storage", "s3"],
             "Azure Storage", CAT_STORAGE,
             "Object/blob storage usage detected"),

    # ── Integration / Messaging ───────────────────────────────────────────────
    _MapRule(["*"],
             ["kafka", "spring-kafka", "confluent-kafka"],
             [],
             "Azure Event Hubs", CAT_INTEGRATION,
             "Apache Kafka dependency — event hubs supports Kafka protocol"),
    _MapRule(["*"],
             ["rabbitmq", "amqp", "pika", "spring-amqp"],
             [],
             "Azure Service Bus", CAT_INTEGRATION,
             "Message broker dependency detected"),
    _MapRule(["*"],
             ["eventgrid", "azure-eventgrid", "event-grid"],
             [],
             "Azure Event Grid", CAT_INTEGRATION,
             "Event-driven integration pattern"),

    # ── AI / ML ───────────────────────────────────────────────────────────────
    _MapRule(["Python"],
             ["scikit-learn", "sklearn", "xgboost", "lightgbm", "catboost",
              "tensorflow", "keras", "torch", "pytorch"],
             [],
             "Azure Machine Learning", CAT_AI,
             "ML framework detected — train/deploy on Azure ML"),
    _MapRule(["Python", "JavaScript", "TypeScript"],
             ["openai", "langchain", "llm", "gpt", "embeddings"],
             [],
             "Azure OpenAI Service", CAT_AI,
             "OpenAI/LLM library detected"),
    _MapRule(["Python", "Java", ".NET"],
             ["elasticsearch", "opensearch", "elastic"],
             [],
             "Azure Elastic Search", CAT_AI,
             "Search engine dependency detected"),

    # ── Compute ──────────────────────────────────────────────────────────────
    _MapRule(["*"], [],
             ["Jenkinsfile", "azure-pipelines.yml", ".github/workflows",
              "bitbucket-pipelines.yml"],
             "Azure Batch", CAT_COMPUTE,
             "CI/CD pipeline files suggest batch compute workloads"),
    _MapRule(["Java", "Python", ".NET", "JavaScript"],
             ["spring-boot", "fastapi", "django", "flask", "express",
              "asp.net", "dotnet", "quarkus"],
             [],
             "Azure App Service", CAT_COMPUTE,
             "Web application framework detected"),
    _MapRule(["*"], [],
             [],
             "Azure infrastructure as a service (IaaS)", CAT_COMPUTE,
             "General compute workload detected"),

    # ── Web ──────────────────────────────────────────────────────────────────
    _MapRule(["JavaScript", "TypeScript"],
             ["signalr", "@microsoft/signalr", "socket.io", "ws"],
             [],
             "Azure Web PubSub", CAT_WEB,
             "Real-time messaging library detected"),

    # ── Security ─────────────────────────────────────────────────────────────
    _MapRule(["*"],
             ["azure-identity", "msal", "adal", "keyvault",
              "azure.keyvault", "azure-keyvault"],
             [],
             "Azure Key Vault", CAT_SECURITY,
             "Azure identity/key vault SDK detected"),

    # ── Analytics ────────────────────────────────────────────────────────────
    _MapRule(["Python", "Java"],
             ["pyspark", "spark", "hadoop", "databricks"],
             [],
             "Microsoft Fabric", CAT_ANALYTICS,
             "Big data framework detected"),
    _MapRule(["Python", "Java", ".NET"],
             ["azure-datalake", "adls", "datalake"],
             [],
             "Azure Data Lake Analytics", CAT_ANALYTICS,
             "Data lake SDK detected"),
]


# ─── Result types ──────────────────────────────────────────────────────────────

@dataclass
class CloudServiceEntry:
    service:  str
    category: str
    reason:   str
    count:    int = 1      # number of apps/repos that trigger this service


@dataclass
class CloudRecommendationReport:
    by_category:        Dict[str, List[CloudServiceEntry]]  # category → services
    total_services:     int
    detected_triggers:  List[str]       # what triggered recommendations


# ─── Calculator ───────────────────────────────────────────────────────────────

class CloudRecommendationCalculator:
    """
    Given repo_path + detected languages + dependency names, returns
    a CloudRecommendationReport mapping technologies to Azure services.
    """

    _SKIP_DIRS = {
        ".git", "node_modules", "vendor", "venv", ".venv",
        "target", "bin", "obj", "__pycache__", "dist", "build",
    }

    # Function: calculate
    def calculate(
        self,
        repo_path: Path,
        languages: List[str],
        dependencies: Set[str],
    ) -> CloudRecommendationReport:
        """
        Parameters
        ----------
        repo_path    : Local checkout
        languages    : Detected language names (Python, Java, etc.)
        dependencies : All dependency names collected by language analysers
        """
        if repo_path is None or not repo_path.exists():
            return CloudRecommendationReport(
                by_category={}, total_services=0, detected_triggers=[],
            )
        deps_lower   = {d.lower() for d in dependencies}
        deps_lower  |= self._scan_content_imports(repo_path)
        files_present = self._scan_file_markers(repo_path)

        matched, triggers_found = self._match_cloud_rules(languages, deps_lower, files_present)
        ordered = self._group_cloud_services(matched)

        return CloudRecommendationReport(
            by_category=ordered,
            total_services=len(matched),
            detected_triggers=sorted(triggers_found),
        )

    # Function: _rule_lang_matches
    @staticmethod
    def _rule_lang_matches(rule: "_MapRule", languages: "List[str]") -> bool:
        return (
            rule.trigger_languages == ["*"]
            or any(l in rule.trigger_languages for l in languages)
        )

    # Function: _apply_rule
    @staticmethod
    def _apply_rule(
        rule: "_MapRule",
        languages: "List[str]",
        deps_lower: "Set[str]",
        files_present: "List[str]",
        matched: "Dict[str, CloudServiceEntry]",
        triggers_found: "Set[str]",
    ) -> None:
        dep_match = any(
            pat in dep for dep in deps_lower for pat in rule.trigger_patterns
        )
        file_match = any(
            marker.lower() in fp.lower()
            for fp in files_present
            for marker in rule.trigger_file_pats
        )
        no_trigger_rule = (
            not rule.trigger_patterns and not rule.trigger_file_pats
            and len(languages) > 0
        )
        if not (dep_match or file_match or no_trigger_rule):
            return
        if rule.azure_service in matched:
            return
        matched[rule.azure_service] = CloudServiceEntry(
            service=rule.azure_service,
            category=rule.category,
            reason=rule.reason,
            count=1,
        )
        if dep_match:
            triggers_found.add(f"dep:{rule.trigger_patterns[0] if rule.trigger_patterns else '?'}")
        if file_match:
            triggers_found.add(f"file:{rule.trigger_file_pats[0] if rule.trigger_file_pats else '?'}")

    # Function: _match_cloud_rules
    def _match_cloud_rules(
        self,
        languages: "List[str]",
        deps_lower: "Set[str]",
        files_present: "List[str]",
    ) -> "tuple[Dict[str, CloudServiceEntry], Set[str]]":
        matched: Dict[str, CloudServiceEntry] = {}
        triggers_found: Set[str] = set()

        for rule in _RULES:
            if not self._rule_lang_matches(rule, languages):
                continue
            self._apply_rule(rule, languages, deps_lower, files_present, matched, triggers_found)

        return matched, triggers_found

    # Function: _group_cloud_services
    def _group_cloud_services(
        self, matched: "Dict[str, CloudServiceEntry]"
    ) -> "Dict[str, List[CloudServiceEntry]]":
        cat_order = [CAT_SECURITY, CAT_CONTAINER, CAT_INTEGRATION, CAT_STORAGE,
                     CAT_DATABASE, CAT_AI, CAT_WEB, CAT_COMPUTE, CAT_ANALYTICS]
        by_cat: Dict[str, List[CloudServiceEntry]] = {}
        for entry in matched.values():
            by_cat.setdefault(entry.category, []).append(entry)

        ordered: Dict[str, List[CloudServiceEntry]] = {}
        for cat in cat_order:
            if cat in by_cat:
                ordered[cat] = sorted(by_cat[cat], key=lambda e: e.service)
        for cat in by_cat:
            if cat not in ordered:
                ordered[cat] = sorted(by_cat[cat], key=lambda e: e.service)
        return ordered


    _PY_IMPORT   = re.compile(r'^\s*(?:import|from)\s+([\w]+)', re.MULTILINE)
    _JAVA_IMPORT = re.compile(r'^\s*import\s+([\w]+(?:\.[\w]+)*)\s*;', re.MULTILINE)
    _JS_REQUIRE  = re.compile(r"""(?:import\s+.*?from|require\s*\()\s*['"]([^'"@./][^'"]*?)['"]""")
    _CS_USING    = re.compile(r'^\s*using\s+([\w]+(?:\.[\w]+)*)\s*;', re.MULTILINE)

    # Function: _extract_imports_from_text
    @classmethod
    def _extract_imports_from_text(cls, ext: str, text: str, found: Set[str]) -> None:
        if ext == ".py":
            for m in cls._PY_IMPORT.finditer(text):
                found.add(m.group(1).lower())
        elif ext == ".java":
            for m in cls._JAVA_IMPORT.finditer(text):
                found.add(m.group(1).split(".")[0].lower())
        elif ext in (".js", ".ts", ".jsx", ".tsx"):
            for m in cls._JS_REQUIRE.finditer(text):
                found.add(m.group(1).split("/")[0].lower())
        elif ext == ".cs":
            for m in cls._CS_USING.finditer(text):
                found.add(m.group(1).split(".")[0].lower())

    # Function: _scan_dir_imports
    def _scan_dir_imports(self, dir_path: Path, filenames: List[str], source_exts: Set[str],
                           found: Set[str], count: int) -> int:
        for fname in filenames:
            if count > 500:
                break
            path = dir_path / fname
            if path.suffix not in source_exts:
                continue
            count += 1
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")[:6000]
            except Exception:
                continue
            self._extract_imports_from_text(path.suffix.lower(), text, found)
        return count

    # Function: _scan_content_imports
    def _scan_content_imports(self, repo_path: Path) -> Set[str]:
        """
        Scan source files for import statements and extract package names.
        Returns a lowercase set of all imported top-level package names.
        This augments explicit dependency files so frameworks used in code
        are always detected even when manifest files are incomplete.
        """
        source_exts = {".py", ".java", ".cs", ".js", ".ts", ".jsx", ".tsx"}
        found: Set[str] = set()
        count = 0  # Limit files scanned for performance

        for dirpath, dirnames, filenames in os.walk(str(repo_path)):
            dirnames[:] = [d for d in dirnames if d not in self._SKIP_DIRS]
            count = self._scan_dir_imports(Path(dirpath), filenames, source_exts, found, count)
            if count > 500:
                break

        return found

    # Function: _scan_file_markers
    def _scan_file_markers(self, repo_path: Path) -> List[str]:
        """Collect relevant filenames (not content) for file-marker rules."""
        results: List[str] = []
        count = 0
        for dirpath, dirnames, filenames in os.walk(str(repo_path)):
            dirnames[:] = [d for d in dirnames if d not in self._SKIP_DIRS]
            dir_path = Path(dirpath)
            for fname in filenames:
                if count > 5000:
                    break
                try:
                    rel = str((dir_path / fname).relative_to(repo_path)).replace("\\", "/")
                except ValueError:
                    rel = fname
                results.append(rel)
                count += 1
            if count > 5000:
                break
        return results
