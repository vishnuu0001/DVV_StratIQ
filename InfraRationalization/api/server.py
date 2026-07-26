# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: api/server.py
# Date: 2026-06-17
# ---------------------------------------------------------------------------
"""
api/server.py
InfraRationalization FastAPI backend.

Endpoints:
  GET    /api/health                  — liveness check
  GET    /api/auth/session            — validate JWT and return session info

  POST   /api/scans/start             — trigger a live infrastructure scan
  GET    /api/scans/jobs              — list in-memory scan jobs (running + recent)
  GET    /api/scans/jobs/{scan_id}    — get live scan job status
  GET    /api/scans/jobs/{scan_id}/stream — SSE real-time progress stream
  GET    /api/scans/jobs/{scan_id}/report — get completed scan report

  GET    /api/scans                   — list all saved (persisted) scans
  POST   /api/scans                   — save a new scan (JSON body, manual upload)
  GET    /api/scans/{scan_id}         — get scan by id
  DELETE /api/scans/{scan_id}        — delete scan
  GET    /api/template               — download empty JSON scan template

Serves React SPA (frontend/dist) on all non-/api paths.
Port: 8083
"""
from __future__ import annotations

import asyncio
import base64
import hashlib
import hmac
import json
import logging
import os
import queue
import time
import uuid
from datetime import datetime
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
except ImportError:
    pass

# Scanner imports (optional — disabled gracefully if deps not installed)
try:
    from scanner.orchestrator import Orchestrator
    from scanner.models import ScanTarget
    _ORCHESTRATOR: Orchestrator | None = None

    # Function: _get_orchestrator
    def _get_orchestrator() -> Orchestrator:
        global _ORCHESTRATOR
        if _ORCHESTRATOR is None:
            _ORCHESTRATOR = Orchestrator(reports_dir=str(_REPORTS_DIR_LAZY()))
        return _ORCHESTRATOR

    SCANNER_AVAILABLE = True
except Exception as _scan_import_err:
    logging.getLogger(__name__).warning(
        "Scanner not available: %s", _scan_import_err
    )
    SCANNER_AVAILABLE = False

    # Function: _get_orchestrator
    def _get_orchestrator():  # type: ignore[misc]
        raise HTTPException(status_code=503, detail="Scanner dependencies not installed")


# Function: _REPORTS_DIR_LAZY
def _REPORTS_DIR_LAZY() -> Path:
    return Path(__file__).resolve().parent.parent / "reports"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

INFRA_SCAN_APP = "INFRA_SCAN"
_INSECURE_DEFAULT_AUTH_SECRET = "change-this-auth-token-secret-in-production"

app = FastAPI(
    title="InfraRationalization API",
    description="Infrastructure feasibility analysis and cloud migration planning",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Serve React SPA ─────────────────────────────────────────────────────────
_DIST_DIR = Path(__file__).resolve().parent.parent / "frontend" / "dist"
if _DIST_DIR.exists():
    _assets_dir = _DIST_DIR / "assets"
    if _assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(_assets_dir)), name="assets")

    # Function: _favicon
    @app.get("/favicon.ico", include_in_schema=False)
    async def _favicon():
        ico = _DIST_DIR / "favicon.ico"
        return FileResponse(str(ico)) if ico.exists() else HTMLResponse("", status_code=204)

    # Function: _spa_or_error
    @app.exception_handler(StarletteHTTPException)
    async def _spa_or_error(request: Request, exc: StarletteHTTPException):
        if exc.status_code == 404 and not request.url.path.startswith("/api"):
            return FileResponse(str(_DIST_DIR / "index.html"))
        return JSONResponse({"detail": exc.detail}, status_code=exc.status_code)

    # Function: _index
    @app.get("/", include_in_schema=False)
    async def _index():
        return FileResponse(str(_DIST_DIR / "index.html"))


# ─── Scan report storage ──────────────────────────────────────────────────────
_REPORTS_DIR = Path(__file__).resolve().parent.parent / "reports"
_REPORTS_DIR.mkdir(exist_ok=True)


# ─── Auth helpers ─────────────────────────────────────────────────────────────
# Function: _auth_required
def _auth_required() -> bool:
    return os.getenv("AUTH_REQUIRED", "true").lower() in {"1", "true", "yes"}


# Function: _token_secret
def _token_secret() -> str:
    secret = (os.getenv("AUTH_TOKEN_SECRET") or "").strip()
    if secret and secret != _INSECURE_DEFAULT_AUTH_SECRET:
        return secret
    if _auth_required():
        allow_insecure = os.getenv("ALLOW_INSECURE_AUTH_SECRET", "false").lower() in {"1", "true", "yes"}
        if allow_insecure:
            logger.warning("Using insecure AUTH_TOKEN_SECRET because ALLOW_INSECURE_AUTH_SECRET=true")
            return _INSECURE_DEFAULT_AUTH_SECRET
        raise RuntimeError(
            "AUTH_TOKEN_SECRET must be set to a strong non-default value when AUTH_REQUIRED=true"
        )
    return _INSECURE_DEFAULT_AUTH_SECRET


# Function: _b64url_decode
def _b64url_decode(text: str) -> bytes:
    padding = "=" * ((4 - len(text) % 4) % 4)
    return base64.urlsafe_b64decode((text + padding).encode("ascii"))


# Function: _b64url_encode
def _b64url_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


# Function: _extract_bearer_token
def _extract_bearer_token(authorization_header: str) -> str | None:
    if not authorization_header:
        return None
    parts = authorization_header.split(" ", 1)
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None
    return parts[1].strip()


# Function: _decode_access_token
def _decode_access_token(token: str) -> dict:
    if not token:
        raise ValueError("Missing token")
    parts = token.split(".")
    if len(parts) != 3 or parts[0] != "v1":
        raise ValueError("Malformed token")
    payload_encoded = parts[1]
    expected_signature = _b64url_encode(
        hmac.new(
            _token_secret().encode("utf-8"),
            payload_encoded.encode("utf-8"),
            hashlib.sha256,
        ).digest()
    )
    if not hmac.compare_digest(expected_signature, parts[2]):
        raise ValueError("Invalid token signature")
    payload = json.loads(_b64url_decode(payload_encoded).decode("utf-8"))
    if payload.get("typ") != "access":
        raise ValueError("Invalid token type")
    exp = int(payload.get("exp", 0))
    if exp <= int(time.time()):
        raise ValueError("Token expired")
    return payload


# Function: enforce_auth
@app.middleware("http")
async def enforce_auth(request: Request, call_next):
    path = request.url.path
    public_paths = {"/api/health", "/docs", "/openapi.json", "/redoc"}
    if not _auth_required() or not path.startswith("/api") or path in public_paths:
        return await call_next(request)
    # EventSource (SSE) cannot send custom headers — accept token via query param
    auth_header = request.headers.get("Authorization", "")
    if not auth_header and path.endswith("/stream"):
        token_qp = request.query_params.get("token", "")
        if token_qp:
            auth_header = f"Bearer {token_qp}"
    token = _extract_bearer_token(auth_header)
    if not token:
        return JSONResponse(status_code=401, content={"error": "Authentication required"})
    try:
        payload = _decode_access_token(token)
    except ValueError as exc:
        return JSONResponse(status_code=401, content={"error": str(exc)})
    role = payload.get("role")
    apps = payload.get("apps") or []
    if role != "admin" and INFRA_SCAN_APP not in apps:
        return JSONResponse(
            status_code=403,
            content={"error": "Access denied for Infra Scan"},
        )
    request.state.auth = payload
    return await call_next(request)


# ─── API endpoints ────────────────────────────────────────────────────────────

# Function: health
@app.get("/api/health")
async def health():
    return {"status": "ok", "module": "InfraRationalization", "port": 8083}


# Function: get_session
@app.get("/api/auth/session")
async def get_session(request: Request):
    token = _extract_bearer_token(request.headers.get("Authorization", ""))
    if not token:
        return JSONResponse(status_code=401, content={"error": "No token"})
    try:
        payload = _decode_access_token(token)
    except ValueError as exc:
        return JSONResponse(status_code=401, content={"error": str(exc)})
    return {
        "authenticated": True,
        "user": {
            "username": payload.get("username") or payload.get("sub"),
            "role": payload.get("role"),
            "apps": payload.get("apps", []),
        },
    }


# ─── Scan index helpers ───────────────────────────────────────────────────────

# Function: _scan_index_path
def _scan_index_path() -> Path:
    return _REPORTS_DIR / "_index.json"


# Function: _load_index
def _load_index() -> list:
    p = _scan_index_path()
    if not p.exists():
        return []
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return []


# Function: _save_index
def _save_index(index: list) -> None:
    _scan_index_path().write_text(
        json.dumps(index, indent=2, default=str), encoding="utf-8"
    )


# Function: _scan_path
def _scan_path(scan_id: str) -> Path:
    return _REPORTS_DIR / f"{scan_id}.json"


# ─── Software inventory back-fill ─────────────────────────────────────────────

# Known port → application mapping (used to infer software from legacy reports
# that have workloads but empty installed_software lists)
_PORT_TO_SOFTWARE: dict[int, dict] = {
    3306:  {"name": "MySQL Server",              "vendor": "Oracle Corporation",                        "category": "db",         "license_type": "commercial"},
    3307:  {"name": "MySQL Server",              "vendor": "Oracle Corporation",                        "category": "db",         "license_type": "commercial"},
    5432:  {"name": "PostgreSQL Server",         "vendor": "PostgreSQL Global Development Group",       "category": "db",         "license_type": "open_source"},
    27017: {"name": "MongoDB Server",            "vendor": "MongoDB Inc.",                              "category": "db",         "license_type": "commercial"},
    6379:  {"name": "Redis Server",              "vendor": "Redis Labs",                                "category": "db",         "license_type": "open_source"},
    11211: {"name": "Memcached",                 "vendor": "Memcached Contributors",                    "category": "db",         "license_type": "open_source"},
    9200:  {"name": "Elasticsearch",             "vendor": "Elastic N.V.",                              "category": "db",         "license_type": "commercial"},
    9042:  {"name": "Apache Cassandra",          "vendor": "Apache Software Foundation",                "category": "db",         "license_type": "open_source"},
    8086:  {"name": "InfluxDB",                  "vendor": "InfluxData",                                "category": "db",         "license_type": "open_source"},
    5672:  {"name": "RabbitMQ",                  "vendor": "Pivotal Software",                          "category": "middleware",  "license_type": "open_source"},
    9092:  {"name": "Apache Kafka",              "vendor": "Apache Software Foundation",                "category": "middleware",  "license_type": "open_source"},
    2181:  {"name": "Apache ZooKeeper",          "vendor": "Apache Software Foundation",                "category": "middleware",  "license_type": "open_source"},
    8080:  {"name": "HTTP Application Server",   "vendor": "",                                          "category": "middleware",  "license_type": "unknown"},
    8443:  {"name": "HTTPS Application Server",  "vendor": "",                                          "category": "middleware",  "license_type": "unknown"},
    8005:  {"name": "Apache Tomcat",             "vendor": "Apache Software Foundation",                "category": "middleware",  "license_type": "open_source"},
    8009:  {"name": "Apache Tomcat",             "vendor": "Apache Software Foundation",                "category": "middleware",  "license_type": "open_source"},
    8161:  {"name": "Apache ActiveMQ",           "vendor": "Apache Software Foundation",                "category": "middleware",  "license_type": "open_source"},
    7001:  {"name": "Oracle WebLogic",           "vendor": "Oracle Corporation",                        "category": "middleware",  "license_type": "commercial"},
    9990:  {"name": "WildFly",                   "vendor": "Red Hat Inc.",                              "category": "middleware",  "license_type": "open_source"},
    8983:  {"name": "Apache Solr",               "vendor": "Apache Software Foundation",                "category": "db",         "license_type": "open_source"},
    2375:  {"name": "Docker Engine",             "vendor": "Docker Inc.",                               "category": "utility",    "license_type": "open_source"},
    2376:  {"name": "Docker Engine (TLS)",       "vendor": "Docker Inc.",                               "category": "utility",    "license_type": "open_source"},
    6443:  {"name": "Kubernetes API Server",     "vendor": "CNCF",                                      "category": "utility",    "license_type": "open_source"},
    2379:  {"name": "etcd",                      "vendor": "CNCF",                                      "category": "utility",    "license_type": "open_source"},
    8500:  {"name": "HashiCorp Consul",          "vendor": "HashiCorp",                                 "category": "middleware",  "license_type": "commercial"},
    8200:  {"name": "HashiCorp Vault",           "vendor": "HashiCorp",                                 "category": "security",   "license_type": "commercial"},
    9090:  {"name": "Prometheus",                "vendor": "CNCF",                                      "category": "utility",    "license_type": "open_source"},
    3000:  {"name": "Grafana",                   "vendor": "Grafana Labs",                              "category": "utility",    "license_type": "open_source"},
    5601:  {"name": "Kibana",                    "vendor": "Elastic N.V.",                              "category": "utility",    "license_type": "commercial"},
    8081:  {"name": "Sonatype Nexus",            "vendor": "Sonatype",                                  "category": "utility",    "license_type": "commercial"},
    9000:  {"name": "SonarQube",                 "vendor": "SonarSource",                               "category": "utility",    "license_type": "commercial"},
    7474:  {"name": "Neo4j",                     "vendor": "Neo4j Inc.",                                "category": "db",         "license_type": "commercial"},
    5984:  {"name": "CouchDB",                   "vendor": "Apache Software Foundation",                "category": "db",         "license_type": "open_source"},
    1433:  {"name": "Microsoft SQL Server",      "vendor": "Microsoft Corporation",                     "category": "db",         "license_type": "commercial"},
    1521:  {"name": "Oracle Database",           "vendor": "Oracle Corporation",                        "category": "db",         "license_type": "commercial"},
    50000: {"name": "IBM DB2",                   "vendor": "IBM",                                       "category": "db",         "license_type": "commercial"},
    10050: {"name": "Zabbix Agent",              "vendor": "Zabbix LLC",                                "category": "utility",    "license_type": "open_source"},
}

_WORKLOAD_NAME_TO_SOFTWARE: dict[str, dict] = {
    # workload component_type/name keyword → software info
    "mysql":          {"name": "MySQL Server",         "vendor": "Oracle Corporation",                  "category": "db",        "license_type": "commercial"},
    "mariadb":        {"name": "MariaDB Server",       "vendor": "MariaDB Corporation",                 "category": "db",        "license_type": "open_source"},
    "postgresql":     {"name": "PostgreSQL Server",    "vendor": "PostgreSQL Global Development Group", "category": "db",        "license_type": "open_source"},
    "postgres":       {"name": "PostgreSQL Server",    "vendor": "PostgreSQL Global Development Group", "category": "db",        "license_type": "open_source"},
    "mongodb":        {"name": "MongoDB Server",       "vendor": "MongoDB Inc.",                        "category": "db",        "license_type": "commercial"},
    "redis":          {"name": "Redis Server",         "vendor": "Redis Labs",                          "category": "db",        "license_type": "open_source"},
    "memcached":      {"name": "Memcached",            "vendor": "Memcached Contributors",              "category": "db",        "license_type": "open_source"},
    "mssql":          {"name": "Microsoft SQL Server", "vendor": "Microsoft Corporation",               "category": "db",        "license_type": "commercial"},
    "sqlserver":      {"name": "Microsoft SQL Server", "vendor": "Microsoft Corporation",               "category": "db",        "license_type": "commercial"},
    "oracle":         {"name": "Oracle Database",      "vendor": "Oracle Corporation",                  "category": "db",        "license_type": "commercial"},
    "elasticsearch":  {"name": "Elasticsearch",        "vendor": "Elastic N.V.",                        "category": "db",        "license_type": "commercial"},
    "cassandra":      {"name": "Apache Cassandra",     "vendor": "Apache Software Foundation",          "category": "db",        "license_type": "open_source"},
    "nginx":          {"name": "nginx",                "vendor": "NGINX Inc.",                          "category": "middleware", "license_type": "open_source"},
    "apache":         {"name": "Apache HTTP Server",   "vendor": "Apache Software Foundation",          "category": "middleware", "license_type": "open_source"},
    "httpd":          {"name": "Apache HTTP Server",   "vendor": "Apache Software Foundation",          "category": "middleware", "license_type": "open_source"},
    "iis":            {"name": "IIS Web Server",       "vendor": "Microsoft Corporation",               "category": "middleware", "license_type": "commercial"},
    "tomcat":         {"name": "Apache Tomcat",        "vendor": "Apache Software Foundation",          "category": "middleware", "license_type": "open_source"},
    "jboss":          {"name": "JBoss / WildFly",      "vendor": "Red Hat Inc.",                        "category": "middleware", "license_type": "open_source"},
    "wildfly":        {"name": "WildFly",              "vendor": "Red Hat Inc.",                        "category": "middleware", "license_type": "open_source"},
    "rabbitmq":       {"name": "RabbitMQ",             "vendor": "Pivotal Software",                    "category": "middleware", "license_type": "open_source"},
    "kafka":          {"name": "Apache Kafka",         "vendor": "Apache Software Foundation",          "category": "middleware", "license_type": "open_source"},
    "activemq":       {"name": "Apache ActiveMQ",      "vendor": "Apache Software Foundation",          "category": "middleware", "license_type": "open_source"},
    "zookeeper":      {"name": "Apache ZooKeeper",     "vendor": "Apache Software Foundation",          "category": "middleware", "license_type": "open_source"},
    "haproxy":        {"name": "HAProxy",              "vendor": "HAProxy Technologies",                "category": "middleware", "license_type": "open_source"},
    "docker":         {"name": "Docker Engine",        "vendor": "Docker Inc.",                         "category": "utility",   "license_type": "open_source"},
    "kubernetes":     {"name": "Kubernetes",           "vendor": "CNCF",                                "category": "utility",   "license_type": "open_source"},
    "grafana":        {"name": "Grafana",              "vendor": "Grafana Labs",                        "category": "utility",   "license_type": "open_source"},
    "prometheus":     {"name": "Prometheus",           "vendor": "CNCF",                                "category": "utility",   "license_type": "open_source"},
    "kibana":         {"name": "Kibana",               "vendor": "Elastic N.V.",                        "category": "utility",   "license_type": "commercial"},
    "jenkins":        {"name": "Jenkins",              "vendor": "Jenkins Project",                     "category": "utility",   "license_type": "open_source"},
    "openssh":        {"name": "OpenSSH Server",       "vendor": "OpenSSH",                             "category": "security",  "license_type": "open_source"},
}

_OS_NAME_TO_VENDOR: dict[str, str] = {
    "windows":   "Microsoft Corporation",
    "ubuntu":    "Canonical",
    "debian":    "Debian Project",
    "centos":    "CentOS Project",
    "red hat":   "Red Hat Inc.",
    "rhel":      "Red Hat Inc.",
    "fedora":    "Fedora Project",
    "suse":      "SUSE",
    "opensuse":  "openSUSE",
    "amazon":    "Amazon Web Services",
    "oracle":    "Oracle Corporation",
    "rocky":     "Rocky Enterprise Software Foundation",
    "almalinux": "AlmaLinux OS Foundation",
    "alpine":    "Alpine Linux",
    "arch":      "Arch Linux",
}


# Function: _eos_fields
def _eos_fields(name: str, version: str, software_eos: dict) -> dict:
    """Return is_eos, days_to_eos, validity_status for a given name+version."""
    from datetime import date as _date

    eos_date = ""
    if software_eos:
        try:
            from scanner.onprem import _lookup_eos_date  # type: ignore
            eos_date = _lookup_eos_date(name, version, software_eos)
        except Exception:
            pass
    is_eos, days, validity = False, 0, "current"
    if eos_date:
        try:
            eos_d = _date.fromisoformat(eos_date)
            today = _date.today()
            is_eos = eos_d < today
            days = (eos_d - today).days
            if is_eos:
                validity = "expired"
            elif days <= 180:
                validity = "expiring_soon"
        except ValueError:
            pass
    return {"eos_date": eos_date, "is_eos": is_eos, "days_to_eos": days, "validity_status": validity}


# Function: _make_sw
def _make_sw(info: dict, version: str, software_eos: dict) -> dict:
    entry = {
        "name":             info["name"],
        "version":          version,
        "vendor":           info.get("vendor", ""),
        "install_date":     "",
        "category":         info.get("category", "app"),
        "license_type":     info.get("license_type", "unknown"),
        "arch":             info.get("arch", ""),
        "install_location": info.get("install_location", ""),
        "source":           info.get("source", "inferred"),
    }
    entry.update(_eos_fields(info["name"], version, software_eos))
    return entry


# Function: _backfill_existing_software_validity
def _backfill_existing_software_validity(installed_software: list) -> None:
    """Already populated — just ensure validity_status is set on each entry."""
    for sw in installed_software:
        if "validity_status" not in sw:
            is_eos = sw.get("is_eos", False)
            days   = sw.get("days_to_eos", 0)
            sw["validity_status"] = (
                "expired"       if is_eos else
                "expiring_soon" if (sw.get("eos_date") and days <= 180) else
                "current"
            )


# Function: _add_os_software_entry
def _add_os_software_entry(srv: dict, add) -> None:
    """1. OS as a software entry."""
    os_name = srv.get("os_name") or srv.get("os_family", "")
    if not os_name:
        return
    os_lower = os_name.lower()
    vendor = next(
        (v for k, v in _OS_NAME_TO_VENDOR.items() if k in os_lower),
        "Linux" if "linux" in os_lower else ""
    )
    lic = "commercial" if "windows" in os_lower else "open_source"
    add({"name": os_name, "vendor": vendor, "category": "os", "license_type": lic},
        srv.get("os_version", ""))


# Function: _add_workload_name_software_entries
def _add_workload_name_software_entries(srv: dict, add) -> None:
    """2. Software from workloads by name."""
    for wl in srv.get("workloads", []):
        wl_name = (wl.get("name") or "").strip()
        wl_ver  = (wl.get("version") or "").strip()
        wl_lower = wl_name.lower().replace(" ", "").replace("-", "")
        matched = False
        for key, info in _WORKLOAD_NAME_TO_SOFTWARE.items():
            if key in wl_lower:
                add(info, wl_ver)
                matched = True
                break
        if not matched and wl_name:
            # Add the workload name as-is
            add({"name": wl_name, "vendor": "", "category": wl.get("component_type", "app"),
                 "license_type": "unknown"}, wl_ver)


# Function: _add_open_port_software_entries
def _add_open_port_software_entries(srv: dict, add) -> None:
    """3. Infer from open ports."""
    for port in srv.get("open_ports", []):
        try:
            p = int(port)
        except (ValueError, TypeError):
            continue
        if p in _PORT_TO_SOFTWARE:
            add(_PORT_TO_SOFTWARE[p])


# Function: _add_workload_port_software_entries
def _add_workload_port_software_entries(srv: dict, add) -> None:
    """4. Infer from listening port in interface/workload data."""
    for wl in srv.get("workloads", []):
        port = wl.get("port")
        if port:
            try:
                p = int(port)
                if p in _PORT_TO_SOFTWARE:
                    add(_PORT_TO_SOFTWARE[p])
            except (ValueError, TypeError):
                pass


# Function: _synthesize_server_software
def _synthesize_server_software(srv: dict, software_eos: dict) -> list:
    synthesised: list[dict] = []
    seen_names: set[str] = set()

    # Function: _add
    def _add(info: dict, version: str = "") -> None:
        key = info["name"].lower()
        if key in seen_names:
            return
        seen_names.add(key)
        synthesised.append(_make_sw(info, version, software_eos))

    _add_os_software_entry(srv, _add)
    _add_workload_name_software_entries(srv, _add)
    _add_open_port_software_entries(srv, _add)
    _add_workload_port_software_entries(srv, _add)

    return synthesised


# Function: _rebuild_software_inventory_section
def _rebuild_software_inventory_section(report: dict) -> None:
    """Rebuild software_inventory section from updated server list."""
    if not report.get("servers"):
        return

    all_sw: list[dict] = []
    seen_global: set[str] = set()
    for srv in report["servers"]:
        for sw in srv.get("installed_software", []):
            key = sw.get("name", "").lower()
            if key and key not in seen_global:
                seen_global.add(key)
                all_sw.append(sw)

    if not all_sw or "sections" not in report:
        return

    existing_inv = report["sections"].get("software_inventory", {}) or {}
    if not existing_inv.get("items"):
        report["sections"]["software_inventory"] = {
            "total_packages": len(all_sw),
            "eos_count":      sum(1 for s in all_sw if s.get("is_eos")),
            "expiring_count": sum(1 for s in all_sw if s.get("validity_status") == "expiring_soon"),
            "items":          all_sw,
            "support_period_label": "Synthesised from workload & port scan data",
            "vendor_distribution": {},
            "per_server_summary": [],
            "days_remaining": 0,
        }


# Function: _backfill_software_inventory
def _backfill_software_inventory(report: dict) -> dict:
    """
    For any server in the report that has empty installed_software but has
    workloads or OS info, synthesise software entries so the dashboard always
    shows meaningful data regardless of scan age.
    Mutates and returns the report dict.
    """
    # Try to load EOS table from report_builder
    try:
        from scanner.report_builder import _SOFTWARE_EOS  # type: ignore
    except Exception:
        _SOFTWARE_EOS = {}

    for srv in report.get("servers", []):
        if srv.get("installed_software"):
            _backfill_existing_software_validity(srv["installed_software"])
            continue

        synthesised = _synthesize_server_software(srv, _SOFTWARE_EOS)
        if synthesised:
            srv["installed_software"] = synthesised

    _rebuild_software_inventory_section(report)

    return report


# ─── Scan CRUD ────────────────────────────────────────────────────────────────

# Function: list_scans
@app.get("/api/scans")
async def list_scans():
    return {"scans": _load_index()}


# Function: create_scan
@app.post("/api/scans")
async def create_scan(request: Request):
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")
    scan_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    scan_data = {**body, "scan_id": scan_id, "created_at": now}
    _scan_path(scan_id).write_text(
        json.dumps(scan_data, indent=2, default=str), encoding="utf-8"
    )
    index = _load_index()
    index.insert(0, {
        "scan_id": scan_id,
        "created_at": now,
        "report_name": body.get("report_name", "Untitled Scan"),
        "source_environment": body.get("source_environment", "Unknown"),
        "target_cloud": body.get("target_cloud", "Unknown"),
        "total_servers": body.get("summary", {}).get("total_servers", 0),
    })
    _save_index(index)
    return {"scan_id": scan_id, "created_at": now}


# Function: list_scan_jobs_early
@app.get("/api/scans/jobs")
async def list_scan_jobs_early():
    """List all in-memory scan jobs (running, pending, recently completed)."""
    if not SCANNER_AVAILABLE:
        return {"jobs": []}
    orch = _get_orchestrator()
    return {"jobs": orch.list_jobs()}


# Function: delete_scan_job
@app.delete("/api/scans/jobs/{scan_id}")
async def delete_scan_job(scan_id: str):
    """Remove a completed/failed job from the in-memory orchestrator store."""
    if not SCANNER_AVAILABLE:
        raise HTTPException(status_code=503, detail="Scanner not available")
    orch = _get_orchestrator()
    removed = orch.remove_job(scan_id)
    if not removed:
        raise HTTPException(status_code=404, detail=f"Job {scan_id} not found")
    return {"deleted": True}


# Function: get_scan
@app.get("/api/scans/{scan_id}")
async def get_scan(scan_id: str):
    p = _scan_path(scan_id)
    if not p.exists():
        raise HTTPException(status_code=404, detail="Scan not found")
    report = json.loads(p.read_text(encoding="utf-8"))
    return _backfill_software_inventory(report)


# Function: delete_scan
@app.delete("/api/scans/{scan_id}")
async def delete_scan(scan_id: str):
    p = _scan_path(scan_id)
    if not p.exists():
        raise HTTPException(status_code=404, detail="Scan not found")
    p.unlink()
    _save_index([s for s in _load_index() if s["scan_id"] != scan_id])
    return {"deleted": True}


_SCAN_TEMPLATE = {
    "report_name": "My Infrastructure Assessment",
    "source_environment": "OnPrem",
    "target_cloud": "Azure",
    "region": "East US",
    "summary": {
        "total_servers": 12,
        "os_count": 4,
        "storage_tb": 2.84,
        "utilization_breakdown": {"underutilized": 10, "moderate": 2, "utilized": 0},
        "server_type": "Virtual",
        "boot_type": "BIOS",
        "ip_distribution_note": "25% of Servers assigned with Private IP & ISP IP.",
    },
    "cloud_readiness": {
        "cloud_ready": 12,
        "cloud_ready_with_effort": 0,
        "lift_and_shift": 2,
        "smart_shift": 0,
        "smart_shift_with_effort": 10,
        "paas_shift": 0,
        "paas_shift_with_effort": 0,
    },
    "capacity_planning": {
        "equivalence_match": {
            "total_servers": 12,
            "total_cpu_cores": 86,
            "total_ram_gb": 344,
            "total_disk_tb": 2.84,
        },
        "best_match": {
            "total_servers": 12,
            "total_cpu_cores": 40,
            "total_ram_gb": 120,
            "total_disk_tb": 2.84,
        },
    },
    "servers": [
        {
            "ip": "10.10.43.40",
            "name": "qaanalyser-FS",
            "os": "Ubuntu 24.04.2 LTS",
            "cpu_cores": 8,
            "ram_gb": 32,
            "disk_gb": 240,
            "utilization": "underutilized",
            "migration_strategy": "smart_shift_effort",
            "migration_recommendation": "OS Ubuntu 24.04.2 LTS not available in Cloud. Recommend Ubuntu 22.04 LTS.",
            "workloads": ["ApacheTomcat 9.0.102"],
        }
    ],
    "pricing_plans": [
        {
            "plan_name": "Pay As You Go",
            "equivalence_match_total_per_month": 1841,
            "best_match_total_per_month": 856,
            "flavors": [
                {
                    "cloud_name": "OnPrem",
                    "flavor_name": "PowerEdge_R6615_8X32",
                    "os_name": "Red Hat 9.6",
                    "flavor_family": "General Purpose",
                    "ram_gb": 32,
                    "cpu_cores": 8,
                    "equivalence_servers": 3,
                    "equivalence_cost_per_month": 513.66,
                    "best_servers": 0,
                    "best_cost_per_month": 0.0,
                }
            ],
        }
    ],
    "workload_consolidation": [
        {
            "workload_name": "MySQL",
            "current_server_count": 4,
            "recommended_server_count": 1,
            "instances": [
                {
                    "server_ip": "10.10.43.41",
                    "server_name": "qaanalyser-db",
                    "version": "MySQL 8.4.5",
                    "location": "/usr/sbin",
                }
            ],
        }
    ],
    "eos_advisories": {
        "operating_systems": [
            {
                "server_ip": "10.10.43.44",
                "server_name": "tesmaasqa-FS",
                "os": "Red Hat Enterprise Linux 9.6",
                "end_of_support": "2032-05-31",
                "end_of_extended_support": "2035-05-31",
                "migration_advisory": "Migrate to Red Hat Enterprise Linux 9.3 using Smart Migration with Service Effort.",
            }
        ],
        "workloads": [
            {
                "server_name": "TESTMAASQA-214",
                "server_ip": "10.10.43.43",
                "workload": "ApacheTomcat 9.0.109",
                "location": "D:\\MaaS\\Tomcat04-Common",
                "end_of_support": "2027-03-31",
                "end_of_extended_support": None,
            }
        ],
    },
}


# Function: get_template
@app.get("/api/template")
async def get_template():
    return JSONResponse(
        content=_SCAN_TEMPLATE,
        headers={"Content-Disposition": 'attachment; filename="infra_scan_template.json"'},
    )


# ─── Live Scanner Endpoints ───────────────────────────────────────────────────

# Function: get_scan_target_candidates
@app.get("/api/scan-target/candidates")
async def get_scan_target_candidates():
    """
    Lists CIDR ranges actually reachable from wherever this backend process is
    running, so the "New Scan" form can offer a real target instead of a
    misleading generic default. On-prem discovery is network-level (nmap/socket
    sweep) — it can only ever see hosts on a network this process can route to.
    """
    import ipaddress as _ipaddress

    candidates = []
    try:
        import psutil
        for iface_name, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                if addr.family.name != "AF_INET" or not addr.netmask:
                    continue
                if addr.address.startswith("127."):
                    continue
                try:
                    network = _ipaddress.IPv4Network(
                        f"{addr.address}/{addr.netmask}", strict=False
                    )
                except ValueError:
                    continue
                candidates.append({
                    "interface": iface_name,
                    "local_ip": addr.address,
                    "cidr": str(network),
                })
    except ImportError:
        pass

    return {"candidates": candidates}


# Function: start_scan
@app.post("/api/scans/start")
async def start_scan(request: Request):
    """
    Trigger a live network / cloud infrastructure scan.

    Body (all optional depending on provider):
      provider            : "onprem" | "aws" | "azure" | "gcp" | "multi"
      report_name         : str
      network_range       : "10.0.0.0/24"   (onprem)
      ssh_username        : str
      ssh_password        : str
      ssh_key_path        : str
      winrm_username      : str
      winrm_password      : str
      aws_access_key_id   : str
      aws_secret_access_key: str
      aws_regions         : ["us-east-1", ...]
      azure_tenant_id     : str
      azure_client_id     : str
      azure_client_secret : str
      azure_subscription_id: str
      gcp_project_id      : str
      gcp_service_account_json: str  (JSON string)
      gcp_regions         : ["us-central1", ...]
      deep_scan           : bool  (default true)
      port_scan           : bool  (default true)
      timeout_seconds     : int   (default 30)
    """
    if not SCANNER_AVAILABLE:
        raise HTTPException(status_code=503, detail="Scanner dependencies not installed")
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    provider = body.get("provider", "onprem")
    report_name = body.get("report_name", f"Scan {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}")

    target = ScanTarget(
        provider=provider,
        network_range=body.get("network_range", ""),
        ssh_username=body.get("ssh_username", ""),
        ssh_password=body.get("ssh_password", ""),
        ssh_key_path=body.get("ssh_key_path", ""),
        winrm_username=body.get("winrm_username", ""),
        winrm_password=body.get("winrm_password", ""),
        aws_access_key_id=body.get("aws_access_key_id", ""),
        aws_secret_access_key=body.get("aws_secret_access_key", ""),
        aws_regions=body.get("aws_regions") or ["us-east-1"],
        azure_tenant_id=body.get("azure_tenant_id", ""),
        azure_client_id=body.get("azure_client_id", ""),
        azure_client_secret=body.get("azure_client_secret", ""),
        azure_subscription_id=body.get("azure_subscription_id", ""),
        gcp_project_id=body.get("gcp_project_id", ""),
        gcp_service_account_json=body.get("gcp_service_account_json", ""),
        gcp_regions=body.get("gcp_regions") or ["us-central1"],
        deep_scan=body.get("deep_scan", True),
        port_scan=body.get("port_scan", True),
        timeout_seconds=int(body.get("timeout_seconds", 30)),
    )

    orch = _get_orchestrator()
    scan_id = orch.start_scan(target, report_name)
    return {"scan_id": scan_id, "report_name": report_name, "status": "pending"}


# Function: list_scan_jobs
@app.get("/api/scans/jobs")
async def list_scan_jobs():
    """List all in-memory scan jobs (running, pending, recently completed)."""
    if not SCANNER_AVAILABLE:
        return {"jobs": []}
    orch = _get_orchestrator()
    return {"jobs": orch.list_jobs()}


# Function: get_scan_job
@app.get("/api/scans/jobs/{scan_id}")
async def get_scan_job(scan_id: str):
    """Get live status of a scan job."""
    if not SCANNER_AVAILABLE:
        raise HTTPException(status_code=503, detail="Scanner not available")
    orch = _get_orchestrator()
    status = orch.get_status(scan_id)
    if not status:
        raise HTTPException(status_code=404, detail="Scan job not found")
    return status


# Function: _sse_event_generator
async def _sse_event_generator(orch, scan_id: str, event_queue: queue.Queue, on_event):
    try:
        while True:
            try:
                data = event_queue.get_nowait()
                yield f"data: {data}\n\n"
                parsed = json.loads(data)
                if parsed.get("progress", 0) >= 100:
                    break
            except queue.Empty:
                job_status = orch.get_status(scan_id)
                if job_status and job_status["status"] in ("completed", "failed"):
                    final = json.dumps({
                        "progress": 100 if job_status["status"] == "completed" else 0,
                        "message": job_status.get("progress_message", ""),
                        "status": job_status["status"],
                        "error": job_status.get("error"),
                    })
                    yield f"data: {final}\n\n"
                    break
                yield ": keepalive\n\n"
                await asyncio.sleep(0.5)
    finally:
        orch.unsubscribe_progress(scan_id, on_event)


# Function: stream_scan_progress
@app.get("/api/scans/jobs/{scan_id}/stream")
async def stream_scan_progress(scan_id: str, request: Request, token: str = ""):
    """
    Server-Sent Events stream for real-time scan progress.
    Accepts auth token via query param (?token=...) for EventSource compatibility.

    Sends: text/event-stream
      data: {"progress": 42, "message": "Scanning 10.0.0.5..."}
    """
    if not SCANNER_AVAILABLE:
        raise HTTPException(status_code=503, detail="Scanner not available")

    # Support token via query string for EventSource (which can't set headers)
    auth_header = request.headers.get("Authorization", "")
    if not auth_header and token:
        auth_header = f"Bearer {token}"
    if _auth_required() and auth_header:
        try:
            _decode_access_token(_extract_bearer_token(auth_header) or "")
        except ValueError as exc:
            raise HTTPException(status_code=401, detail=str(exc))

    orch = _get_orchestrator()
    status = orch.get_status(scan_id)
    if not status:
        raise HTTPException(status_code=404, detail="Scan job not found")

    event_queue: queue.Queue = queue.Queue(maxsize=200)

    # Function: on_event
    def on_event(data: str) -> None:
        try:
            event_queue.put_nowait(data)
        except queue.Full:
            pass

    orch.subscribe_progress(scan_id, on_event)

    return StreamingResponse(
        _sse_event_generator(orch, scan_id, event_queue, on_event),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


# Function: get_scan_report
@app.get("/api/scans/jobs/{scan_id}/report")
async def get_scan_report(scan_id: str):
    """Return the completed scan report JSON."""
    if not SCANNER_AVAILABLE:
        raise HTTPException(status_code=503, detail="Scanner not available")
    orch = _get_orchestrator()
    report = orch.get_report(scan_id)
    if not report:
        # Maybe it's a persisted scan (manual upload)
        p = _scan_path(scan_id)
        if p.exists():
            report = json.loads(p.read_text(encoding="utf-8"))
        else:
            raise HTTPException(status_code=404, detail="Report not found")
    return _backfill_software_inventory(report)


# ─── DB-backed scan endpoints ─────────────────────────────────────────────────
# These endpoints read/write directly from the SQLite database (infra_scans.db).
# All completed live scans are automatically persisted by the orchestrator.
# Manual uploads via POST /api/scans also write to DB.

# Function: _get_db_session
def _get_db_session():
    """Get a SQLAlchemy session, initialising DB tables if needed."""
    try:
        from db.database import SessionLocal, init_db
        init_db()
        return SessionLocal()
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Database unavailable: {exc}")


# Function: db_list_scans
@app.get("/api/db/scans")
async def db_list_scans(
    limit: int = 50,
    offset: int = 0,
    provider: str | None = None,
    status: str | None = None,
):
    """List all scans stored in the database with optional filtering."""
    db = _get_db_session()
    try:
        from db.models import InfraScan
        q = db.query(InfraScan)
        if provider:
            q = q.filter(InfraScan.provider == provider)
        if status:
            q = q.filter(InfraScan.status == status)
        total = q.count()
        scans = q.order_by(InfraScan.created_at.desc()).offset(offset).limit(limit).all()
        return {
            "total": total,
            "offset": offset,
            "limit": limit,
            "scans": [s.to_dict() for s in scans],
        }
    finally:
        db.close()


# Function: db_get_scan
@app.get("/api/db/scans/{scan_id}")
async def db_get_scan(scan_id: str):
    """Get a single scan header from the database."""
    db = _get_db_session()
    try:
        from db.models import InfraScan
        scan = db.get(InfraScan, scan_id)
        if not scan:
            raise HTTPException(status_code=404, detail="Scan not found in database")
        return scan.to_dict()
    finally:
        db.close()


# Function: db_get_scan_report
@app.get("/api/db/scans/{scan_id}/report")
async def db_get_scan_report(scan_id: str):
    """Return the full report JSON stored inside the DB for a scan."""
    db = _get_db_session()
    try:
        from db.models import InfraScan
        scan = db.get(InfraScan, scan_id)
        if not scan:
            raise HTTPException(status_code=404, detail="Scan not found in database")
        if not scan.report_json:
            raise HTTPException(status_code=404, detail="No report JSON stored for this scan")
        return json.loads(scan.report_json)
    finally:
        db.close()


# Function: db_get_scan_servers
@app.get("/api/db/scans/{scan_id}/servers")
async def db_get_scan_servers(
    scan_id: str,
    limit: int = 200,
    offset: int = 0,
    cloud_suitability: str | None = None,
    server_type: str | None = None,
    environment: str | None = None,
    os_family: str | None = None,
):
    """
    Return all servers for a scan from the database.
    Supports filtering by cloud_suitability, server_type, environment, os_family.
    """
    db = _get_db_session()
    try:
        from db.models import InfraServer
        q = db.query(InfraServer).filter(InfraServer.scan_id == scan_id)
        if cloud_suitability:
            q = q.filter(InfraServer.cloud_suitability == cloud_suitability)
        if server_type:
            q = q.filter(InfraServer.server_type == server_type)
        if environment:
            q = q.filter(InfraServer.environment == environment)
        if os_family:
            q = q.filter(InfraServer.os_family == os_family)
        total = q.count()
        servers = q.offset(offset).limit(limit).all()
        return {
            "scan_id": scan_id,
            "total": total,
            "offset": offset,
            "limit": limit,
            "servers": [s.to_dict() for s in servers],
        }
    finally:
        db.close()


# Function: db_get_server
@app.get("/api/db/servers/{server_db_id}")
async def db_get_server(server_db_id: int):
    """Get a single server record by its database ID."""
    db = _get_db_session()
    try:
        from db.models import InfraServer
        server = db.get(InfraServer, server_db_id)
        if not server:
            raise HTTPException(status_code=404, detail="Server record not found")
        return server.to_dict()
    finally:
        db.close()


# Function: db_update_server
@app.patch("/api/db/servers/{server_db_id}")
async def db_update_server(server_db_id: int, request: Request):
    """
    Update rationalization fields for a server record.
    Accepts a JSON body with any subset of the rationalization columns.
    Useful for manually filling in BusinessOwner, PlatformHost, environment,
    HA/DR requirements, etc. that cannot be auto-detected.
    """
    db = _get_db_session()
    try:
        from db.models import InfraServer
        server = db.get(InfraServer, server_db_id)
        if not server:
            raise HTTPException(status_code=404, detail="Server record not found")
        try:
            body = await request.json()
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid JSON body")

        # Allowed editable fields
        editable = {
            "environment", "business_owner", "platform_host", "install_type",
            "application_stability", "cpu_requirement", "memory_requirement",
            "mainframe_dependency", "desktop_dependency",
            "app_os_cloud_suitability", "db_cloud_readiness",
            "middleware_cloud_readiness", "app_hardware_dependency",
            "app_cots_vs_non_cots", "cloud_suitability",
            "volume_external_dependencies", "app_load_predictability",
            "financially_optimizable", "distributed_architecture",
            "latency_requirements", "ubiquitous_access",
            "no_production_environments", "no_non_production_environments",
            "ha_dr_requirements", "rto_requirements", "rpo_requirements",
            "deployment_geography", "virtualization_state",
            "virtualization_attributes",
        }
        updated_fields = []
        for field, value in body.items():
            if field in editable:
                if field == "virtualization_attributes" and isinstance(value, dict):
                    import json as _json
                    value = _json.dumps(value)
                setattr(server, field, value)
                updated_fields.append(field)
        db.commit()
        db.refresh(server)
        return {"updated": updated_fields, "server": server.to_dict()}
    finally:
        db.close()


# Function: db_delete_scan
@app.delete("/api/db/scans/{scan_id}")
async def db_delete_scan(scan_id: str):
    """
    Delete a scan and ALL its server records from the database.
    Also removes the JSON report file from disk if present.
    """
    db = _get_db_session()
    try:
        from db.models import InfraScan
        scan = db.get(InfraScan, scan_id)
        if not scan:
            raise HTTPException(status_code=404, detail="Scan not found in database")
        db.delete(scan)   # cascade will delete all InfraServer rows too
        db.commit()
        # Also clean up disk report
        report_file = _REPORTS_DIR / f"{scan_id}.json"
        if report_file.exists():
            report_file.unlink()
        # Update file-based index
        _save_index([s for s in _load_index() if s.get("scan_id") != scan_id])
        return {"deleted": True, "scan_id": scan_id}
    finally:
        db.close()


# Function: db_delete_server
@app.delete("/api/db/servers/{server_db_id}")
async def db_delete_server(server_db_id: int):
    """Delete a single server record from the database."""
    db = _get_db_session()
    try:
        from db.models import InfraServer
        server = db.get(InfraServer, server_db_id)
        if not server:
            raise HTTPException(status_code=404, detail="Server record not found")
        db.delete(server)
        db.commit()
        return {"deleted": True, "id": server_db_id}
    finally:
        db.close()


# Function: db_stats
@app.get("/api/db/stats")
async def db_stats():
    """Return aggregate statistics from the database."""
    db = _get_db_session()
    try:
        from db.models import InfraScan, InfraServer
        from sqlalchemy import func as sqlfunc
        total_scans   = db.query(sqlfunc.count(InfraScan.scan_id)).scalar()
        total_servers = db.query(sqlfunc.count(InfraServer.id)).scalar()
        by_status     = dict(
            db.query(InfraScan.status, sqlfunc.count(InfraScan.scan_id))
              .group_by(InfraScan.status).all()
        )
        by_cloud_suitability = dict(
            db.query(InfraServer.cloud_suitability, sqlfunc.count(InfraServer.id))
              .group_by(InfraServer.cloud_suitability).all()
        )
        by_server_type = dict(
            db.query(InfraServer.server_type, sqlfunc.count(InfraServer.id))
              .group_by(InfraServer.server_type).all()
        )
        by_environment = dict(
            db.query(InfraServer.environment, sqlfunc.count(InfraServer.id))
              .group_by(InfraServer.environment).all()
        )
        return {
            "total_scans":              total_scans,
            "total_servers":            total_servers,
            "scans_by_status":          by_status,
            "servers_by_cloud_suitability": by_cloud_suitability,
            "servers_by_type":          by_server_type,
            "servers_by_environment":   by_environment,
        }
    finally:
        db.close()


# ─── LLM Intelligence ────────────────────────────────────────────────────────

try:
    import sys as _sys
    _sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from services.llm_intelligence import analyze_infrastructure_failures, get_model_info as _llm_model_info
    _LLM_AVAILABLE = True
except Exception as _llm_err:
    logger.warning("LLM intelligence service not available: %s", _llm_err)
    _LLM_AVAILABLE = False

    # Function: _llm_model_info
    def _llm_model_info():  # type: ignore[misc]
        return {"available": False, "inference_type": "heuristic", "model": None,
                "message": "LLM service module failed to load."}

    # Function: analyze_infrastructure_failures
    def analyze_infrastructure_failures(scan_report):  # type: ignore[misc]
        try:
            from services.llm_intelligence import _heuristic_analysis
            return _heuristic_analysis(scan_report)
        except Exception:
            return {"risk_score": 0, "risk_level": "Unknown",
                    "executive_summary": "Analysis unavailable.",
                    "predicted_failures": [], "root_causes": [],
                    "preventive_measures": [], "topology_risks": {},
                    "model_used": "unavailable"}


# Function: intelligence_status
@app.get("/api/intelligence/status")
async def intelligence_status():
    """Return current LLM model availability and GPU status."""
    return _llm_model_info()


# Function: run_intelligence_analysis
@app.post("/api/intelligence/analyze/{scan_id}")
async def run_intelligence_analysis(scan_id: str):
    """
    Run GPU-accelerated LLM failure prediction for a saved scan.
    Caches the result as <scan_id>_intelligence.json.
    """
    p = _scan_path(scan_id)
    if not p.exists():
        raise HTTPException(status_code=404, detail="Scan not found")
    scan_report = json.loads(p.read_text(encoding="utf-8"))

    try:
        analysis = analyze_infrastructure_failures(scan_report)
    except Exception as exc:
        logger.error("Intelligence analysis failed for %s: %s", scan_id, exc)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {exc}")

    # Cache alongside the scan report
    cache_path = _REPORTS_DIR / f"{scan_id}_intelligence.json"
    cache_path.write_text(json.dumps(analysis, indent=2, default=str), encoding="utf-8")
    return analysis


# Function: get_intelligence_analysis
@app.get("/api/intelligence/analyze/{scan_id}")
async def get_intelligence_analysis(scan_id: str):
    """Return cached LLM analysis. Returns 404 if not yet run."""
    cache_path = _REPORTS_DIR / f"{scan_id}_intelligence.json"
    if not cache_path.exists():
        raise HTTPException(status_code=404, detail="No analysis cached yet. POST to run.")
    return json.loads(cache_path.read_text(encoding="utf-8"))


# Function: chat_with_report
@app.post("/api/scans/{scan_id}/chat")
async def chat_with_report(scan_id: str, request: Request):
    """
    "Chat with your report" — ask a plain-language question about one scan.
    Body: {"message": str, "history": [{"role": "user"|"assistant", "content": str}, ...]}
    The conversation history is passed by the client (not stored server-side)
    since a scan report has no existing concept of a persisted chat session —
    this keeps the endpoint stateless and simple, matching the rest of this
    API's request/response style.
    """
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    message = (body.get("message") or "").strip()
    if not message:
        raise HTTPException(status_code=400, detail="'message' is required")
    history = body.get("history") or []

    report = _load_report(scan_id)
    from services.report_chat import chat_about_report
    # Ollama's HTTP call is synchronous/blocking (same client used by
    # services/llm_intelligence.py) — run it in a worker thread so a slow
    # (up to ~2 min) model response doesn't stall the event loop for every
    # other concurrent request this API is serving.
    result = await asyncio.to_thread(chat_about_report, report, history, message)
    return result


# ─── PDF OCR Infrastructure Analysis ─────────────────────────────────────────

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"

try:
    from scanner.pdf_scanner import scan_data_directory, build_pdf_scan_report, PDFScanResult, scan_pdf
    _PDF_SCANNER_AVAILABLE = True
except Exception as _pdf_import_err:
    logger.warning("PDF scanner not available: %s", _pdf_import_err)
    _PDF_SCANNER_AVAILABLE = False


# Function: list_data_pdfs
@app.get("/api/data/pdfs")
async def list_data_pdfs():
    """List all PDF files available in the data directory."""
    if not _DATA_DIR.exists():
        return {"pdfs": [], "data_dir": str(_DATA_DIR)}

    pdfs = []
    for pdf_path in sorted(_DATA_DIR.rglob("*.pdf")):
        stat = pdf_path.stat()
        pdfs.append({
            "filename": pdf_path.name,
            "relative_path": str(pdf_path.relative_to(_DATA_DIR)),
            "size_bytes": stat.st_size,
            "size_kb": round(stat.st_size / 1024, 1),
            "modified": datetime.utcfromtimestamp(stat.st_mtime).isoformat(),
        })
    return {"pdfs": pdfs, "total": len(pdfs), "data_dir": str(_DATA_DIR)}


# Function: scan_pdfs
@app.post("/api/scans/pdf")
async def scan_pdfs():
    """
    Run deep OCR analysis on all PDF documents in the data/ directory.

    Performs:
      1. Native text extraction (pdfplumber) + OCR fallback (pytesseract)
      2. Provider detection: On-Premises / Azure / AWS / GCP
      3. Feature extraction: all services, specs, network, security, HA/DR, compliance
      4. Mapping to DiscoveredServer infrastructure models
      5. Saves report to reports/ and scan index

    Returns a full consolidated report with:
      - detected_providers
      - servers (mapped DiscoveredServer objects)
      - pdf_documents (per-file feature extraction details)
      - top_services_mentioned
      - summary
    """
    if not _PDF_SCANNER_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="PDF scanner not available. Install: pdfplumber, pdf2image, pytesseract",
        )
    if not _DATA_DIR.exists():
        raise HTTPException(status_code=404, detail=f"Data directory not found: {_DATA_DIR}")

    pdf_files = list(_DATA_DIR.rglob("*.pdf"))
    if not pdf_files:
        raise HTTPException(status_code=404, detail="No PDF files found in data directory")

    try:
        loop = asyncio.get_event_loop()
        results: list[PDFScanResult] = await loop.run_in_executor(
            None,
            lambda: scan_data_directory(_DATA_DIR),
        )
    except Exception as exc:
        logger.error("PDF scan failed: %s", exc)
        raise HTTPException(status_code=500, detail=f"PDF scan failed: {exc}")

    _scan_id, report = _persist_pdf_scan_report(results)

    return report


# Function: _scan_pdf_via_executor
async def _scan_pdf_via_executor(pdf_path):
    """Run scan_pdf() in a thread executor, capturing its progress messages."""
    # Function: _do_scan
    def _do_scan():
        msgs = []

        # Function: cb
        def cb(msg):
            msgs.append(msg)

        result = scan_pdf(pdf_path, progress_cb=cb)
        return result, msgs

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _do_scan)


# Function: _persist_pdf_scan_report
def _persist_pdf_scan_report(results):
    """Build the consolidated PDF scan report, save it, and update the scan index."""
    report = build_pdf_scan_report(results)
    scan_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    report["scan_id"] = scan_id
    report["created_at"] = now
    report["report_name"] = f"PDF OCR Analysis — {now[:10]}"
    report["source_environment"] = "PDF Document Analysis"
    report["target_cloud"] = ", ".join(report.get("detected_providers", [])).upper() or "Unknown"

    _scan_path(scan_id).write_text(
        json.dumps(report, indent=2, default=str), encoding="utf-8"
    )
    index = _load_index()
    index.insert(0, {
        "scan_id": scan_id,
        "created_at": now,
        "report_name": report["report_name"],
        "source_environment": report["source_environment"],
        "target_cloud": report["target_cloud"],
        "total_servers": report.get("total_servers_extracted", 0),
        "scan_type": "pdf_ocr",
        "documents_scanned": report.get("documents_scanned", 0),
        "detected_providers": report.get("detected_providers", []),
    })
    _save_index(index)

    return scan_id, report


# Function: _validate_sse_bearer_token
def _validate_sse_bearer_token(auth_header: str) -> None:
    if _auth_required() and auth_header:
        try:
            _decode_access_token(_extract_bearer_token(auth_header) or "")
        except ValueError as exc:
            raise HTTPException(status_code=401, detail=str(exc))


# Function: _format_pdf_file_result_events
def _format_pdf_file_result_events(pdf_path, idx: int, total: int, result, msgs) -> list:
    events = []
    for msg in msgs[-3:]:  # last few messages to avoid flooding
        events.append(f"data: {json.dumps({'type': 'progress', 'message': msg, 'current': idx + 1, 'total': total, 'phase': 'analysis'})}\n\n")

    if result.error:
        events.append(f"data: {json.dumps({'type': 'file_warning', 'message': f'{pdf_path.name}: {result.error}', 'current': idx + 1, 'total': total})}\n\n")
    else:
        providers_str = ", ".join(result.detected_providers).upper()
        services_count = sum(len(f.get("found_services", [])) for f in result.features_by_provider.values())
        events.append(f"data: {json.dumps({'type': 'file_done', 'message': f'{pdf_path.name}: detected {providers_str} — {services_count} services, {len(result.servers)} server(s)', 'current': idx + 1, 'total': total})}\n\n")

    return events


# Function: scan_pdfs_stream
@app.post("/api/scans/pdf/stream")
async def scan_pdfs_stream(request: Request):
    """
    SSE streaming version of the PDF OCR scan — provides real-time progress.

    Sends text/event-stream events:
      {"type": "start",    "message": "...", "total": N}
      {"type": "progress", "message": "...", "current": i, "total": N}
      {"type": "complete", "scan_id": "...", "report": {...}}
      {"type": "error",    "message": "..."}
    """
    if not _PDF_SCANNER_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="PDF scanner not available. Install: pdfplumber, pdf2image, pytesseract",
        )
    if not _DATA_DIR.exists():
        raise HTTPException(status_code=404, detail="Data directory not found")

    # Support token via query string for EventSource
    auth_header = request.headers.get("Authorization", "")
    if not auth_header:
        token_qp = request.query_params.get("token", "")
        if token_qp:
            auth_header = f"Bearer {token_qp}"
    _validate_sse_bearer_token(auth_header)

    # Function: _generate
    async def _generate():
        pdf_files = list(_DATA_DIR.rglob("*.pdf"))
        if not pdf_files:
            yield f"data: {json.dumps({'type': 'error', 'message': 'No PDF files found in data directory'})}\n\n"
            return

        total = len(pdf_files)
        yield f"data: {json.dumps({'type': 'start', 'message': f'Starting OCR analysis of {total} PDF(s)', 'total': total})}\n\n"

        results: list[PDFScanResult] = []

        for idx, pdf_path in enumerate(sorted(pdf_files)):
            yield f"data: {json.dumps({'type': 'progress', 'message': f'Scanning {pdf_path.name}…', 'current': idx + 1, 'total': total, 'phase': 'extraction'})}\n\n"

            result, msgs = await _scan_pdf_via_executor(pdf_path)
            results.append(result)

            for event in _format_pdf_file_result_events(pdf_path, idx, total, result, msgs):
                yield event

        yield f"data: {json.dumps({'type': 'progress', 'message': 'Building consolidated report…', 'current': total, 'total': total, 'phase': 'report'})}\n\n"

        scan_id, report = _persist_pdf_scan_report(results)

        yield f"data: {json.dumps({'type': 'complete', 'scan_id': scan_id, 'report': report})}\n\n"

    return StreamingResponse(
        _generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# ─── Analysis endpoints (new features) ───────────────────────────────────────

# Function: _load_report
def _load_report(scan_id: str) -> dict:
    """Load a saved scan report by ID, with software backfill."""
    p = _scan_path(scan_id)
    if not p.exists():
        raise HTTPException(status_code=404, detail=f"Scan {scan_id} not found")
    report = json.loads(p.read_text(encoding="utf-8"))
    return _backfill_software_inventory(report)


# Function: get_tco_analysis
@app.get("/api/scans/{scan_id}/tco")
async def get_tco_analysis(scan_id: str):
    """Financial TCO & Cloud Cost Comparison with right-sizing recommendations."""
    from services.tco_rightsizing import analyze_tco
    report = _load_report(scan_id)
    return analyze_tco(report)


# Function: get_pricing_status
@app.get("/api/pricing/status")
async def get_pricing_status():
    """
    Per-provider pricing freshness (live/cached-live/static) without
    triggering a new fetch — read-only, always fast. Drives the "Pricing:
    live (2h ago)" / "Pricing: static table" badge in the TCO tab so cost
    figures are never shown without their real provenance.
    """
    from services.live_pricing import get_pricing_freshness
    return get_pricing_freshness()


# Function: refresh_pricing
@app.post("/api/pricing/refresh")
async def refresh_pricing():
    """
    Force a live re-fetch from all four providers' public pricing APIs,
    ignoring the 24h cache. In an air-gapped/regulated deployment with no
    outbound connectivity, every provider will simply report "unavailable"
    here — that's an expected, non-error outcome (see live_pricing.py).
    """
    from services.live_pricing import refresh_all
    return refresh_all()


# Function: get_dependency_map
@app.get("/api/scans/{scan_id}/dependencies")
async def get_dependency_map(scan_id: str):
    """Application dependency mapping and migration wave planning."""
    from services.dependency_migration import build_dependency_map
    report = _load_report(scan_id)
    return build_dependency_map(report)


# Function: get_security_analysis
@app.get("/api/scans/{scan_id}/security")
async def get_security_analysis(scan_id: str):
    """Security & compliance posture (CVE, CIS benchmark, protocol risks)."""
    from services.security_compliance import analyze_security
    report = _load_report(scan_id)
    return analyze_security(report)


# Function: get_decommission_candidates
@app.get("/api/scans/{scan_id}/decommission")
async def get_decommission_candidates(scan_id: str):
    """Decommissioning candidate identification."""
    from services.decommission import identify_decommission_candidates
    report = _load_report(scan_id)
    return identify_decommission_candidates(report)


# Function: get_hypervisor_analysis
@app.get("/api/scans/{scan_id}/hypervisor")
async def get_hypervisor_analysis(scan_id: str):
    """Hypervisor & virtualization consolidation analysis."""
    from services.hypervisor_consolidation import analyze_hypervisor_consolidation
    report = _load_report(scan_id)
    return analyze_hypervisor_consolidation(report)


# Function: get_bcdr_analysis
@app.get("/api/scans/{scan_id}/bcdr")
async def get_bcdr_analysis(scan_id: str):
    """Disaster recovery & BCDR gap analysis."""
    from services.bcdr_analysis import analyze_bcdr
    report = _load_report(scan_id)
    return analyze_bcdr(report)


# Function: export_excel
@app.get("/api/scans/{scan_id}/export/excel")
async def export_excel(scan_id: str):
    """Download full asset register as Excel (.xlsx)."""
    from services.export_reports import export_excel as _export_excel
    report = _load_report(scan_id)
    try:
        data = _export_excel(report)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    filename = f"infra_report_{scan_id}.xlsx"
    return StreamingResponse(
        iter([data]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# Function: export_cmdb_csv
@app.get("/api/scans/{scan_id}/export/csv")
async def export_cmdb_csv(scan_id: str):
    """Download ServiceNow CMDB-compatible CSV."""
    from services.export_reports import export_cmdb_csv as _export_csv
    report = _load_report(scan_id)
    data = _export_csv(report)
    filename = f"cmdb_export_{scan_id}.csv"
    return StreamingResponse(
        iter([data]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# Function: export_pdf
@app.get("/api/scans/{scan_id}/export/pdf")
async def export_pdf(scan_id: str):
    """Download executive summary PDF."""
    from services.export_reports import export_pdf as _export_pdf
    report = _load_report(scan_id)
    try:
        data = _export_pdf(report)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    filename = f"infra_report_{scan_id}.pdf"
    return StreamingResponse(
        iter([data]),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# Function: export_pptx
@app.get("/api/scans/{scan_id}/export/pptx")
async def export_pptx(scan_id: str):
    """Download executive PowerPoint slide deck."""
    from services.export_reports import export_pptx as _export_pptx
    report = _load_report(scan_id)
    try:
        data = _export_pptx(report)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    filename = f"infra_report_{scan_id}.pptx"
    return StreamingResponse(
        iter([data]),
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# Function: _execution_requests_path
def _execution_requests_path() -> Path:
    return _REPORTS_DIR / "_execution_requests.json"


# Function: _load_execution_requests
def _load_execution_requests() -> list:
    p = _execution_requests_path()
    if not p.exists():
        return []
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return []


# Function: _save_execution_requests
def _save_execution_requests(requests_list: list) -> None:
    _execution_requests_path().write_text(
        json.dumps(requests_list, indent=2, default=str), encoding="utf-8"
    )


_EXECUTION_REQUEST_TYPES = {"appliance_deployment", "landing_zone", "app_dna_mapping"}


# Function: list_execution_requests
@app.get("/api/execution-requests")
async def list_execution_requests():
    """
    List submitted requests for the not-yet-connected execution-support
    workflows (scanning appliance deployment, cloud landing zone creation,
    application DNA mapping). These capture real user requirements/interest
    for when those integrations exist — they are NOT simulated/fake progress,
    and nothing here provisions real infrastructure.
    """
    return {"requests": _load_execution_requests()}


# Function: create_execution_request
@app.post("/api/execution-requests")
async def create_execution_request(request: Request):
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    req_type = body.get("request_type")
    if req_type not in _EXECUTION_REQUEST_TYPES:
        raise HTTPException(status_code=400, detail=f"request_type must be one of {sorted(_EXECUTION_REQUEST_TYPES)}")

    record = {
        "id": str(uuid.uuid4()),
        "request_type": req_type,
        "details": body.get("details") or {},
        "submitted_at": datetime.utcnow().isoformat(),
        "status": "pending",   # always "pending" — there is no live integration to advance this
    }
    requests_list = _load_execution_requests()
    requests_list.insert(0, record)
    _save_execution_requests(requests_list)
    return record


# Function: delete_execution_request
@app.delete("/api/execution-requests/{request_id}")
async def delete_execution_request(request_id: str):
    requests_list = _load_execution_requests()
    filtered = [r for r in requests_list if r["id"] != request_id]
    if len(filtered) == len(requests_list):
        raise HTTPException(status_code=404, detail="Request not found")
    _save_execution_requests(filtered)
    return {"status": "deleted"}


# Function: export_iac
@app.get("/api/scans/{scan_id}/iac")
async def export_iac(scan_id: str, provider: str = "azure", format: str = "terraform"):
    """
    Download an Infrastructure-as-Code STARTER TEMPLATE (Terraform / ARM /
    CloudFormation) mapping this scan's servers to target-cloud VM resources.
    Output only — placeholders for network/credentials are left for the
    operator to fill in; nothing is provisioned by generating this file.
    """
    from services.iac_generator import generate_iac
    report = _load_report(scan_id)
    try:
        content, media_type = generate_iac(report, provider, format)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    ext = {"terraform": "tf", "arm": "json", "cloudformation": "json"}.get(format.lower(), "txt")
    filename = f"infra_iac_{scan_id}_{provider.lower()}.{ext}"
    return StreamingResponse(
        iter([content.encode("utf-8")]),
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


if __name__ == "__main__":
    import os
    uvicorn.run("api.server:app", host=os.getenv("HOST", "127.0.0.1"), port=8083, reload=True)

