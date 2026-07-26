# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Persistent, Git-independent governance for modernization projects.
# Date: 2025-11-03
# ---------------------------------------------------------------------------
"""Persistent, Git-independent governance for modernization projects.

The store deliberately uses only the Python standard library so an on-premises
installation has no database or cloud dependency.  Project artifacts are
immutable directories; mutable state lives in a small SQLite catalogue.
"""
from __future__ import annotations

import ast
import difflib
import hashlib
import json
import os
import re
import shutil
import sqlite3
import uuid
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

SKIP_DIRS = {".git", ".svn", "node_modules", "bin", "obj", "dist", "build", "target", "__pycache__", ".venv"}
TEXT_LIMIT = 2 * 1024 * 1024
WORKFLOW = ("Uploaded", "Analyzed", "Plan Generated", "Plan Reviewed", "Plan Approved",
            "Transformation Running", "Validation Running", "Review Required", "Approved", "Exported")
KINDS = {"source", "analysis", "plans", "contracts", "outputs", "validation", "approved", "exports", "overrides"}


# Function: utcnow
def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


# Function: _json
def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


# Function: _files
def _files(root: Path) -> Iterable[Path]:
    if not root.exists():
        return
    for path in root.rglob("*"):
        if path.is_file() and not any(part in SKIP_DIRS for part in path.relative_to(root).parts):
            yield path


# Function: tree_checksum
def tree_checksum(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(_files(root), key=lambda p: p.as_posix().lower()):
        digest.update(path.relative_to(root).as_posix().encode())
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
    return digest.hexdigest()


# Function: _read
def _read(path: Path) -> str:
    if path.stat().st_size > TEXT_LIMIT:
        return ""
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


class ProjectStore:
    # Function: __init__
    def __init__(self, root: str | Path | None = None):
        self.root = Path(root or os.getenv("MODERNIZATION_PROJECTS_DIR") or Path(__file__).resolve().parents[1] / "data" / "projects").resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self.db_path = self.root / "catalog.sqlite3"
        self._initialize()

    # Function: _db
    def _db(self):
        db = sqlite3.connect(self.db_path, timeout=30)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys=ON")
        return db

    # Function: _initialize
    def _initialize(self):
        with self._db() as db:
            db.executescript("""
              CREATE TABLE IF NOT EXISTS projects (
                id TEXT PRIMARY KEY, name TEXT NOT NULL, owner TEXT NOT NULL, status TEXT NOT NULL,
                configuration TEXT NOT NULL, retention_days INTEGER NOT NULL DEFAULT 365,
                created_at TEXT NOT NULL, updated_at TEXT NOT NULL);
              CREATE TABLE IF NOT EXISTS snapshots (
                id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES projects(id), kind TEXT NOT NULL,
                version INTEGER NOT NULL, path TEXT NOT NULL, checksum TEXT NOT NULL, parent_id TEXT,
                metadata TEXT NOT NULL, status TEXT NOT NULL, approval_decision TEXT, locked INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL, created_by TEXT NOT NULL, UNIQUE(project_id, kind, version));
              CREATE TABLE IF NOT EXISTS file_reviews (
                snapshot_id TEXT NOT NULL REFERENCES snapshots(id), file_path TEXT NOT NULL,
                decision TEXT NOT NULL, comment TEXT NOT NULL, user TEXT NOT NULL, updated_at TEXT NOT NULL,
                PRIMARY KEY(snapshot_id, file_path));
            """)

    # Function: create_project
    def create_project(self, name: str, source: Path, user: str, configuration: dict | None = None,
                       retention_days: int = 365) -> dict:
        if not source.is_dir():
            raise ValueError("source_path must be an existing directory")
        with self._db() as db:
            sequence = db.execute("SELECT COUNT(*) + 1 FROM projects").fetchone()[0]
            project_id = f"APP-{sequence:03d}"
            while db.execute("SELECT 1 FROM projects WHERE id=?", (project_id,)).fetchone():
                sequence += 1; project_id = f"APP-{sequence:03d}"
            now = utcnow()
            db.execute("INSERT INTO projects VALUES (?,?,?,?,?,?,?,?)",
                       (project_id, name.strip(), user, "Uploaded", _json(configuration or {}), retention_days, now, now))
        self.add_directory_snapshot(project_id, "source", source, user,
                                    {"configuration": configuration or {}, "source_path": str(source)})
        return self.get_project(project_id)

    # Function: create_prompt_project
    def create_prompt_project(self, name: str, prompt: str, user: str, configuration: dict | None = None,
                              retention_days: int = 365) -> dict:
        """Create a governed greenfield project whose immutable source is a brief."""
        if not prompt.strip():
            raise ValueError("project_prompt is required for a new prompt-based project")
        with self._db() as db:
            sequence = db.execute("SELECT COUNT(*) + 1 FROM projects").fetchone()[0]
            project_id = f"APP-{sequence:03d}"
            while db.execute("SELECT 1 FROM projects WHERE id=?", (project_id,)).fetchone():
                sequence += 1; project_id = f"APP-{sequence:03d}"
            now = utcnow()
            db.execute("INSERT INTO projects VALUES (?,?,?,?,?,?,?,?)",
                       (project_id, name.strip(), user, "Uploaded", _json(configuration or {}), retention_days, now, now))
        self.add_json_snapshot(project_id, "source", {"project_prompt": prompt.strip()}, user,
                               {"configuration": configuration or {}, "source_type": "prompt"},
                               filename="project-brief.json")
        return self.get_project(project_id)

    # Function: list_projects
    def list_projects(self) -> list[dict]:
        with self._db() as db:
            return [self._project(row) for row in db.execute("SELECT * FROM projects ORDER BY created_at DESC")]

    # Function: get_project
    def get_project(self, project_id: str) -> dict:
        with self._db() as db:
            row = db.execute("SELECT * FROM projects WHERE id=?", (project_id,)).fetchone()
            if not row: raise KeyError(project_id)
            value = self._project(row)
            value["snapshots"] = [self._snapshot(s) for s in db.execute(
                "SELECT * FROM snapshots WHERE project_id=? ORDER BY created_at DESC", (project_id,))]
            return value

    # Function: _project
    @staticmethod
    def _project(row):
        value = dict(row); value["configuration"] = json.loads(value["configuration"]); return value

    # Function: _snapshot
    @staticmethod
    def _snapshot(row):
        value = dict(row); value["metadata"] = json.loads(value["metadata"]); value["locked"] = bool(value["locked"]); return value

    # Function: set_status
    def set_status(self, project_id: str, status: str, allowed_from: tuple[str, ...] | None = None):
        if status not in WORKFLOW: raise ValueError(f"Unknown workflow status: {status}")
        with self._db() as db:
            current = db.execute("SELECT status FROM projects WHERE id=?", (project_id,)).fetchone()
            if not current: raise KeyError(project_id)
            if allowed_from and current[0] not in allowed_from:
                raise ValueError(f"Cannot move from {current[0]} to {status}")
            db.execute("UPDATE projects SET status=?, updated_at=? WHERE id=?", (status, utcnow(), project_id))

    # Function: _next_version
    def _next_version(self, db, project_id, kind):
        return db.execute("SELECT COALESCE(MAX(version),0)+1 FROM snapshots WHERE project_id=? AND kind=?",
                          (project_id, kind)).fetchone()[0]

    # Function: add_directory_snapshot
    def add_directory_snapshot(self, project_id: str, kind: str, source: Path, user: str,
                               metadata: dict | None = None, parent_id: str | None = None) -> dict:
        if kind not in KINDS: raise ValueError(f"Unknown snapshot kind: {kind}")
        with self._db() as db:
            version = self._next_version(db, project_id, kind)
            snap_id = f"{kind.rstrip('s')}-{uuid.uuid4().hex[:12]}"
            destination = self.root / project_id / kind / f"v{version:03d}"
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(source, destination)
            return self._insert_snapshot(db, snap_id, project_id, kind, version, destination,
                                         tree_checksum(destination), user, metadata or {}, parent_id)

    # Function: add_json_snapshot
    def add_json_snapshot(self, project_id: str, kind: str, data: Any, user: str,
                          metadata: dict | None = None, parent_id: str | None = None,
                          filename: str = "artifact.json") -> dict:
        with self._db() as db:
            version = self._next_version(db, project_id, kind)
            snap_id = f"{kind.rstrip('s')}-{uuid.uuid4().hex[:12]}"
            destination = self.root / project_id / kind / f"v{version:03d}"
            destination.mkdir(parents=True, exist_ok=False)
            (destination / filename).write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
            return self._insert_snapshot(db, snap_id, project_id, kind, version, destination,
                                         tree_checksum(destination), user, metadata or {}, parent_id)

    # Function: add_output_snapshot
    def add_output_snapshot(self, project_id: str, output: dict[str, str], user: str,
                            metadata: dict | None = None, parent_id: str | None = None) -> dict:
        temp = self.root / project_id / ".staging" / uuid.uuid4().hex
        try:
            for name, content in output.items():
                if name.startswith("__"): continue
                path = (temp / name).resolve()
                if os.path.commonpath([str(temp.resolve()), str(path)]) != str(temp.resolve()): continue
                path.parent.mkdir(parents=True, exist_ok=True); path.write_text(str(content), encoding="utf-8")
            return self.add_directory_snapshot(project_id, "outputs", temp, user, metadata, parent_id)
        finally:
            shutil.rmtree(temp, ignore_errors=True)

    # Function: _insert_snapshot
    def _insert_snapshot(self, db, snap_id, project_id, kind, version, path, checksum, user, metadata, parent_id):
        project = db.execute("SELECT configuration FROM projects WHERE id=?", (project_id,)).fetchone()
        if not project: raise KeyError(project_id)
        meta = {"source_checksum": checksum, "configuration": json.loads(project[0]),
                "target_stack": metadata.get("target_stack"), "model": metadata.get("model"),
                "prompt_template_version": metadata.get("prompt_template_version"), **metadata}
        db.execute("INSERT INTO snapshots VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                   (snap_id, project_id, kind, version, str(path), checksum, parent_id, _json(meta),
                    "created", None, 0, utcnow(), user))
        row = db.execute("SELECT * FROM snapshots WHERE id=?", (snap_id,)).fetchone()
        return self._snapshot(row)

    # Function: get_snapshot
    def get_snapshot(self, project_id: str, snapshot_id: str) -> dict:
        with self._db() as db:
            row = db.execute("SELECT * FROM snapshots WHERE project_id=? AND id=?", (project_id, snapshot_id)).fetchone()
            if not row: raise KeyError(snapshot_id)
            return self._snapshot(row)

    # Function: update_plan
    def update_plan(self, project_id: str, snapshot_id: str, changes: dict, user: str) -> dict:
        old = self.get_snapshot(project_id, snapshot_id)
        if old["locked"]: raise ValueError("Approved plan is locked")
        plan = json.loads((Path(old["path"]) / "plan.json").read_text(encoding="utf-8"))
        for key in (
            "target_technologies", "excluded_modules", "manual_tasks",
            "risks_and_assumptions", "deployment_approach",
            "cutover_approach", "rollback_approach",
        ):
            if key in changes: plan[key] = changes[key]
        if isinstance(changes.get("target_architecture"), dict):
            plan["target_architecture"] = {
                **(plan.get("target_architecture") or {}),
                **changes["target_architecture"],
            }
        unresolved = []
        architecture = plan.get("target_architecture") or {}
        if not architecture.get("style"):
            unresolved.append("Target architecture style and component boundaries are not specified")
        if not plan.get("deployment_approach"):
            unresolved.append("Deployment platform and runtime topology are not specified")
        prompt_based = plan.get("plan_basis") == "approved-project-brief"
        if not prompt_based and not plan.get("cutover_approach"):
            unresolved.append("Cutover method, outage allowance, and reconciliation criteria require an owner decision")
        if not prompt_based and not plan.get("rollback_approach"):
            unresolved.append("Rollback trigger, recovery point, and recovery time objectives require an owner decision")
        resolved_task_prefixes = set()
        if architecture.get("style"):
            resolved_task_prefixes.add("Target architecture style")
        if plan.get("deployment_approach"):
            resolved_task_prefixes.add("Deployment platform")
        if plan.get("cutover_approach"):
            resolved_task_prefixes.add("Cutover method")
        if plan.get("rollback_approach"):
            resolved_task_prefixes.add("Rollback trigger")
        if prompt_based:
            resolved_task_prefixes.update(("Cutover method", "Rollback trigger"))
        unresolved.extend(
            task for task in plan.get("manual_tasks", [])
            if isinstance(task, str)
            and task not in unresolved
            and not any(task.startswith(prefix) for prefix in resolved_task_prefixes)
        )
        plan["unresolved_requirements"] = unresolved
        plan["ready_for_approval"] = not unresolved
        return self.add_json_snapshot(project_id, "plans", plan, user, {"revised_from": snapshot_id}, snapshot_id, "plan.json")

    # Function: decide
    def decide(self, project_id: str, snapshot_id: str, decision: str, user: str):
        if decision not in {"reviewed", "approved", "rejected"}: raise ValueError("Invalid decision")
        with self._db() as db:
            row = db.execute("SELECT kind,locked FROM snapshots WHERE project_id=? AND id=?", (project_id, snapshot_id)).fetchone()
            if not row: raise KeyError(snapshot_id)
            if row[1]: raise ValueError("Snapshot is locked")
            project_status = db.execute("SELECT status FROM projects WHERE id=?", (project_id,)).fetchone()[0]
            if row[0] == "plans" and decision == "approved" and project_status != "Plan Reviewed":
                raise ValueError("The plan must be marked reviewed before it can be approved")
            locked = int(decision == "approved" and row[0] in {"plans", "approved"})
            db.execute("UPDATE snapshots SET approval_decision=?, status=?, locked=? WHERE id=?",
                       (decision, decision, locked, snapshot_id))
            if row[0] == "plans" and decision == "approved":
                db.execute("UPDATE snapshots SET locked=1, status='locked' WHERE id=(SELECT id FROM snapshots WHERE project_id=? AND kind='contracts' ORDER BY created_at DESC LIMIT 1)", (project_id,))
        if row[0] == "plans": self.set_status(project_id, "Plan Approved" if decision == "approved" else "Plan Reviewed")
        return self.get_snapshot(project_id, snapshot_id)

    # Function: restore
    def restore(self, project_id: str, snapshot_id: str, user: str) -> dict:
        old = self.get_snapshot(project_id, snapshot_id)
        return self.add_directory_snapshot(project_id, old["kind"], Path(old["path"]), user,
                                           {"restored_from": snapshot_id}, snapshot_id)

    # Function: review_file
    def review_file(self, snapshot_id: str, file_path: str, decision: str, comment: str, user: str):
        if decision not in {"approved", "rejected", "pending"}: raise ValueError("Invalid file decision")
        with self._db() as db:
            db.execute("INSERT OR REPLACE INTO file_reviews VALUES (?,?,?,?,?,?)",
                       (snapshot_id, file_path, decision, comment, user, utcnow()))
        return {"snapshot_id": snapshot_id, "file_path": file_path, "decision": decision, "comment": comment}

    # Function: purge
    def purge(self, project_id: str) -> dict:
        project = self.get_project(project_id); cutoff = datetime.now(timezone.utc).timestamp() - project["retention_days"] * 86400
        removed = []
        with self._db() as db:
            rows = db.execute("SELECT * FROM snapshots WHERE project_id=? AND locked=0", (project_id,)).fetchall()
            for row in rows:
                if datetime.fromisoformat(row["created_at"]).timestamp() < cutoff:
                    shutil.rmtree(Path(row["path"]), ignore_errors=True); db.execute("DELETE FROM snapshots WHERE id=?", (row["id"],)); removed.append(row["id"])
        return {"removed": removed, "retained_locked": True}


# Function: semantic_index
def semantic_index(root: Path) -> dict:
    symbols, calls, imports, endpoints, database, configs, auth, jobs, integrations, tests = [], [], [], [], [], [], [], [], [], []
    hierarchy: dict[str, Any] = {"name": root.name, "modules": {}}
    definitions: dict[str, str] = {}
    for path in _files(root):
        rel = path.relative_to(root).as_posix(); text = _read(path)
        if not text: continue
        parts = rel.split("/"); module = parts[0] if len(parts) > 1 else "root"; package = "/".join(parts[:-1]) or "root"
        file_node = {"path": rel, "classes": [], "methods": []}
        hierarchy["modules"].setdefault(module, {"packages": {}})["packages"].setdefault(package, {"files": []})["files"].append(file_node)
        if path.suffix.lower() == ".py":
            try:
                tree = ast.parse(text)
                for node in ast.walk(tree):
                    if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                        kind = "class" if isinstance(node, ast.ClassDef) else "method"
                        item = {"name": node.name, "kind": kind, "file": rel, "line": node.lineno}
                        symbols.append(item); definitions[node.name] = rel; file_node["classes" if kind == "class" else "methods"].append(item)
                    elif isinstance(node, ast.Call):
                        name = getattr(node.func, "id", None) or getattr(node.func, "attr", None)
                        if name: calls.append({"caller_file": rel, "symbol": name, "line": node.lineno})
                    elif isinstance(node, (ast.Import, ast.ImportFrom)):
                        imports.append({"file": rel, "module": getattr(node, "module", None) or node.names[0].name})
            except SyntaxError: pass
        else:
            for match in re.finditer(r"(?m)^\s*(?:public\s+|private\s+|protected\s+|export\s+|abstract\s+)*(class|interface|enum|function)\s+(\w+)", text):
                item = {"name": match.group(2), "kind": match.group(1), "file": rel, "line": text.count("\n", 0, match.start()) + 1}
                symbols.append(item); definitions[item["name"]] = rel; file_node["classes"].append(item)
            for match in re.finditer(r"(?m)^\s*(?:import|using|require)\s*[('\"]*([^;'\")]+)", text): imports.append({"file": rel, "module": match.group(1).strip()})
        for pattern, method_group, route_group in [(r'@(app|router)\.(get|post|put|patch|delete)\(["\']([^"\']+)', 2, 3), (r'\[(HttpGet|HttpPost|HttpPut|HttpDelete).*?["\']([^"\']*)', 1, 2)]:
            for m in re.finditer(pattern, text, re.I): endpoints.append({"method": m.group(method_group).upper().replace("HTTP", ""), "route": m.group(route_group), "file": rel})
        if re.search(r"(?i)\b(select|insert|update|delete)\b.+\b(from|into|set)\b", text): database.append({"file": rel, "kind": "query"})
        for m in re.finditer(r"(?i)\b(?:exec(?:ute)?|call)\s+([\w.]+)", text): database.append({"file": rel, "kind": "stored_procedure", "name": m.group(1)})
        if re.search(r"(?i)(appsettings|connectionstring|process\.env|os\.getenv|configuration)", text): configs.append(rel)
        if re.search(r"(?i)(authorize|authentication|jwt|oauth|roles?)", text): auth.append(rel)
        if re.search(r"(?i)(cron|scheduled|quartz|hangfire|celery|backgroundservice)", text): jobs.append(rel)
        if re.search(r"https?://|HttpClient|requests\.|fetch\(", text): integrations.append(rel)
        if re.search(r"(?i)(^|/)(test|tests|spec)", rel): tests.append(rel)
    incoming = {c["symbol"] for c in calls}
    dead = [s for s in symbols if s["kind"] in {"method", "function"} and s["name"] not in incoming and not s["name"].startswith(("test", "_"))]
    graph: dict[str, set[str]] = defaultdict(set)
    for item in imports: graph[item["file"]].add(item["module"])
    cycles = _cycles(graph)
    return {"generated_at": utcnow(), "application": root.name, "hierarchy": hierarchy, "symbol_index": symbols,
            "call_graph": calls, "module_dependency_graph": {k: sorted(v) for k, v in graph.items()},
            "package_dependency_graph": {k: sorted(v) for k, v in graph.items()}, "class_interface_relationships": [],
            "api_endpoints": endpoints, "database_access": database, "configuration_inventory": sorted(set(configs)),
            "authentication_authorization_flow": sorted(set(auth)), "scheduled_jobs": sorted(set(jobs)),
            "external_integrations": sorted(set(integrations)), "test_to_code_mapping": _map_tests(tests, symbols),
            "dead_code_candidates": dead, "cyclic_dependencies": cycles}


# Function: _cycles
def _cycles(graph: dict[str, set[str]]) -> list[list[str]]:
    result = []
    # Function: visit
    def visit(node, trail):
        if node in trail: result.append(trail[trail.index(node):] + [node]); return
        if len(trail) > 20: return
        for child in graph.get(node, ()): visit(child, trail + [node])
    for node in graph: visit(node, [])
    unique = {tuple(c) for c in result}; return [list(c) for c in sorted(unique)]


# Function: _map_tests
def _map_tests(tests, symbols):
    mapped = []
    for test in tests:
        stem = Path(test).stem.lower().replace("test_", "").replace("test", "")
        mapped.append({"test": test, "code": sorted({s["file"] for s in symbols if stem and stem in s["name"].lower()})})
    return mapped


def infer_prompt_requirements(prompt: str) -> dict:
    """Extract explicit governance facts from a prompt-created project's brief."""
    text = (prompt or "").casefold()
    inferred: dict = {}
    if any(term in text for term in ("event-driven", "event driven", "event-based")):
        inferred["architecture"] = (
            "Event-driven layered service: REST adapters, application/domain services, "
            "transactional persistence, outbox/event publishing, and infrastructure adapters"
        )
    elif "microservice" in text:
        inferred["architecture"] = "Microservices with explicit API and event boundaries"
    elif any(term in text for term in ("hexagonal", "ports and adapters", "clean architecture")):
        inferred["architecture"] = "Hexagonal ports-and-adapters architecture"

    databases = (
        ("postgres", "PostgreSQL"),
        ("mysql", "MySQL"),
        ("sql server", "Microsoft SQL Server"),
        ("oracle", "Oracle Database"),
        ("mongodb", "MongoDB"),
    )
    for term, label in databases:
        if term in text:
            data_access = []
            if "spring data jpa" in text or "jpa" in text:
                data_access.append("Spring Data JPA")
            if "flyway" in text:
                data_access.append("Flyway")
            inferred["database"] = " + ".join((label, *data_access))
            break

    auth = []
    if "oauth2" in text or "oauth 2" in text:
        auth.append("OAuth2")
    if "jwt" in text:
        auth.append("JWT bearer validation")
    roles = sorted(set(re.findall(r"\b(?:ADMIN|ORDER_USER|[A-Z][A-Z0-9_]{2,}_USER)\b", prompt or "")))
    if roles:
        auth.append("roles: " + ", ".join(roles))
    if auth:
        inferred["authorization"] = auth

    deployment = []
    if "docker" in text:
        deployment.append("Docker containers")
    if "docker-compose" in text or "docker compose" in text:
        deployment.append("Docker Compose for local orchestration")
    if "kubernetes" in text or "k8s" in text:
        deployment.append("Kubernetes")
    if deployment:
        inferred["deployment"] = "; ".join(dict.fromkeys(deployment))
    return inferred


# Function: generate_plan
def generate_plan(analysis: dict, index: dict, target_stack: str, excluded: list[str] | None = None) -> dict:
    modules = sorted(index.get("hierarchy", {}).get("modules", {}))
    inferred = infer_prompt_requirements(analysis.get("project_prompt") or "")
    requested = {
        **inferred,
        **{
            key: value for key, value in (analysis.get("requested_target") or {}).items()
            if value not in (None, "", [], {})
        },
    }
    is_greenfield = analysis.get("project_type") == "greenfield"
    excluded = excluded or []
    database_objects = index.get("database_access", [])
    detected_auth = index.get("authentication_authorization_flow", [])
    auth_flows = (
        list(requested.get("authorization", []))
        if is_greenfield and requested.get("authorization")
        else list(dict.fromkeys(list(detected_auth) + list(requested.get("authorization", []))))
    )
    tests = index.get("test_to_code_mapping", [])
    architecture = requested.get("architecture")
    deployment = requested.get("deployment")
    unresolved = []
    if not architecture:
        unresolved.append("Target architecture style and component boundaries are not specified")
    if not deployment:
        unresolved.append("Deployment platform and runtime topology are not specified")
    if is_greenfield and not requested.get("database"):
        unresolved.append("Persistence requirements and database choice are not specified")
    if is_greenfield and not auth_flows:
        unresolved.append("Authentication and authorization requirements are not specified")
    if not modules and not is_greenfield:
        unresolved.append("No source modules were discovered; transformation scope cannot be established")
    operational_decisions = [
        "Cutover method, outage allowance, and reconciliation criteria require an owner decision",
        "Rollback trigger, recovery point, and recovery time objectives require an owner decision",
    ]
    # Prompt-created projects may be generated and technically validated before
    # release-management owners choose rollout/RPO/RTO policy. Those decisions
    # remain visible manual tasks but are not false code-generation blockers.
    if not is_greenfield:
        unresolved.extend(operational_decisions)
    risks = []
    if index.get("cyclic_dependencies"):
        risks.append({"type": "cyclic_dependencies", "evidence": index["cyclic_dependencies"]})
    if index.get("dead_code_candidates"):
        risks.append({"type": "dead_code_candidates", "evidence": index["dead_code_candidates"]})
    return {
        "schema_version": 2,
        "plan_basis": "analyzed-source-evidence" if not is_greenfield else "approved-project-brief",
        "current_state_architecture": analysis.get("summary", analysis.get("architecture", {})),
        "target_architecture": {
            "stack": target_stack,
            "style": architecture,
            "runtime": requested.get("runtime"),
            "frontend": requested.get("frontend"),
            "backend": requested.get("framework"),
            "database": requested.get("database"),
            "deployment": deployment,
        },
        "source_technologies": analysis.get("tech_stack", analysis.get("technologies", [])),
        "target_technologies": [value for value in (
            target_stack, requested.get("runtime"), requested.get("framework"),
            requested.get("frontend"), requested.get("database"),
        ) if value],
        "modules_and_domains": modules,
        "excluded_modules": excluded,
        "transformation_sequence": [module for module in modules if module not in excluded],
        "database_conversion_approach": {
            "required": bool(database_objects or requested.get("database")),
            "source_objects": database_objects,
            "target": requested.get("database"),
        },
        "interfaces_affected": index.get("api_endpoints", []),
        "dependencies_affected": index.get("module_dependency_graph", {}),
        "security_changes": auth_flows,
        "configuration_changes": index.get("configuration_inventory", []),
        "testing_approach": {
            "existing_test_mapping": tests,
            "required_release_gates": [
                "strict per-file compiler/parser validation",
                "registered whole-project build or artifact validation",
                "contract validation",
                "credential scan",
            ],
        },
        "deployment_approach": deployment,
        "cutover_approach": None,
        "rollback_approach": None,
        "risks_and_assumptions": risks,
        "unsupported_constructs": [],
        "manual_tasks": list(dict.fromkeys(
            unresolved if is_greenfield else unresolved + operational_decisions
        )),
        "unresolved_requirements": list(unresolved),
        "ready_for_approval": not unresolved,
        "generated_at": utcnow(),
    }


# Function: generate_contracts
def generate_contracts(index: dict, target_stack: str) -> dict:
    symbols = index.get("symbol_index", [])
    models = sorted({s["name"] for s in symbols if s["kind"] in {"class", "interface"}})
    routes = index.get("api_endpoints", [])
    contracts = {"schema_version": 1, "target_stack": target_stack, "domain_models": models,
                 "dtos": [m for m in models if m.lower().endswith(("dto", "request", "response"))],
                 "interfaces": [s["name"] for s in symbols if s["kind"] == "interface"], "api_contracts": routes,
                 "route_definitions": routes, "database_schema": index.get("database_access", []),
                 "events_and_messages": [m for m in models if m.lower().endswith(("event", "message"))],
                 "error_model": {"fields": ["code", "message", "details", "traceId"]},
                 "authentication_model": index.get("authentication_authorization_flow", []),
                 "configuration_keys": index.get("configuration_inventory", []), "dependency_versions": {},
                 "namespace_package_mapping": {}, "created_at": utcnow()}
    contracts["checksum"] = hashlib.sha256(_json(contracts).encode()).hexdigest()
    return contracts


# Function: validate_contracts
def validate_contracts(contracts: dict) -> dict:
    errors, warnings = [], []
    models = contracts.get("domain_models", [])
    for duplicate in sorted({x for x in models if models.count(x) > 1}): errors.append(f"Type is defined more than once: {duplicate}")
    seen = set()
    for route in contracts.get("route_definitions", []):
        key = (route.get("method"), route.get("route"))
        if key in seen: errors.append(f"Conflicting route: {key[0]} {key[1]}")
        seen.add(key)
    if not contracts.get("interfaces"): warnings.append("No explicit interfaces were discovered")
    if not contracts.get("database_schema"): warnings.append("No database schema or access contracts were discovered")
    if not contracts.get("route_definitions"): warnings.append("No API route contracts were discovered")
    checks = {
        "unique_types": not any("Type is defined more than once" in error for error in errors),
        "route_conflicts": not any("route" in error for error in errors),
        "interface_implementations": "not_evaluated",
        "dto_consistency": "not_evaluated",
        "client_api_alignment": "not_evaluated",
        "database_model_alignment": "not_evaluated",
        "dependency_compatibility": (
            "not_evaluated" if not contracts.get("dependency_versions") else "declared_not_built"
        ),
    }
    return {"valid": not errors, "errors": errors, "warnings": warnings,
            "checks": checks}


# Function: transformation_context
def transformation_context(index: dict, current_file: str, contracts: dict, decisions: list | None = None) -> dict:
    calls = [x for x in index.get("call_graph", []) if x.get("caller_file") == current_file]
    names = {x["symbol"] for x in calls}
    refs = [x for x in index.get("symbol_index", []) if x["name"] in names]
    test_maps = [x for x in index.get("test_to_code_mapping", []) if current_file in x.get("code", [])]
    return {"current_file": current_file, "referenced_interfaces_and_services": refs, "called_services": calls,
            "models_and_dtos": contracts.get("domain_models", []) + contracts.get("dtos", []),
            "configuration": index.get("configuration_inventory", []), "database_objects": index.get("database_access", []),
            "related_tests": test_maps, "shared_utilities": [s for s in index.get("symbol_index", []) if "util" in s["file"].lower()],
            "target_architecture_decisions": decisions or [], "canonical_contract_checksum": contracts.get("checksum")}


# Function: compare_directories
def compare_directories(left: Path, right: Path, search: str = "", change_type: str = "") -> dict:
    left_names = {p.relative_to(left).as_posix() for p in _files(left)}; right_names = {p.relative_to(right).as_posix() for p in _files(right)}
    changes = []
    for name in sorted(left_names | right_names):
        old = _read(left / name) if name in left_names else ""; new = _read(right / name) if name in right_names else ""
        status = "added" if name not in left_names else "removed" if name not in right_names else "modified" if old != new else "unchanged"
        if status == "unchanged": continue
        classification = classify_change(name, old, new)
        diff = "\n".join(difflib.unified_diff(old.splitlines(), new.splitlines(), fromfile=f"a/{name}", tofile=f"b/{name}", lineterm=""))
        if search and search.lower() not in (name + diff).lower(): continue
        if change_type and classification != change_type: continue
        changes.append({"path": name, "status": status, "classification": classification, "diff": diff,
                        "side_by_side": list(difflib.ndiff(old.splitlines(), new.splitlines()))})
    return {"summary": {k: sum(c["status"] == k for c in changes) for k in ("added", "modified", "removed")}, "files": changes}


# Function: comparison_html
def comparison_html(comparison: dict) -> str:
    import html
    rows = []
    for item in comparison["files"]:
        rows.append(f"<h2>{html.escape(item['path'])} <small>{html.escape(item['classification'])}</small></h2>"
                    f"<pre>{html.escape(item['diff'])}</pre>")
    return ("<!doctype html><meta charset='utf-8'><title>Modernization comparison</title>"
            "<style>body{font:14px system-ui;margin:32px}pre{background:#111;color:#eee;padding:16px;overflow:auto}"
            "small{color:#666;font-weight:normal}</style><h1>Modernization comparison</h1>" + "".join(rows))


# Function: comparison_pdf
def comparison_pdf(comparison: dict) -> bytes:
    """Create a dependency-free, text-only PDF suitable for audit exports."""
    lines = ["Modernization comparison"]
    for item in comparison["files"]:
        lines.extend([f"{item['status'].upper()}: {item['path']} [{item['classification']}]", *item["diff"].splitlines()[:80], ""])
    pages = [lines[i:i + 48] for i in range(0, len(lines), 48)] or [[]]
    objects = [b"<< /Type /Catalog /Pages 2 0 R >>", b""]
    page_ids, content_ids = [], []
    for page in pages:
        page_ids.append(len(objects) + 1); objects.append(b"")
        content_ids.append(len(objects) + 1)
        commands = ["BT /F1 8 Tf 36 806 Td"]
        for line in page:
            safe = line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
            commands.append(f"({safe[:150]}) Tj 0 -15 Td")
        commands.append("ET"); stream = "\n".join(commands).encode("latin-1", "replace")
        objects.append(b"<< /Length %d >>\nstream\n" % len(stream) + stream + b"\nendstream")
    font_id = len(objects) + 1; objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Courier >>")
    kids = " ".join(f"{item} 0 R" for item in page_ids)
    objects[1] = f"<< /Type /Pages /Kids [{kids}] /Count {len(page_ids)} >>".encode()
    for page_id, content_id in zip(page_ids, content_ids):
        objects[page_id - 1] = (f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "
                                  f"/Resources << /Font << /F1 {font_id} 0 R >> >> /Contents {content_id} 0 R >>").encode()
    result = bytearray(b"%PDF-1.4\n"); offsets = [0]
    for number, obj in enumerate(objects, 1): offsets.append(len(result)); result.extend(f"{number} 0 obj\n".encode() + obj + b"\nendobj\n")
    xref = len(result); result.extend(f"xref\n0 {len(objects)+1}\n0000000000 65535 f \n".encode())
    for offset in offsets[1:]: result.extend(f"{offset:010d} 00000 n \n".encode())
    result.extend(f"trailer << /Size {len(objects)+1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF".encode())
    return bytes(result)


# Function: classify_change
def classify_change(name: str, old: str, new: str) -> str:
    sample = (name + "\n" + old + "\n" + new).lower()
    checks = [("Security change", ("auth", "jwt", "oauth", "password")), ("Database change", ("sql", "entity", "schema", "migration")),
              ("API change", ("controller", "route", "endpoint", "api/")), ("Dependency change", ("package.json", ".csproj", "pom.xml", "requirements")),
              ("Configuration change", ("config", ".env", "settings")), ("Framework conversion", ("framework", "react", "spring", "asp.net"))]
    for label, words in checks:
        if any(word in sample for word in words): return label
    if old and not new: return "Deleted functionality"
    if new and not old: return "New functionality"
    return "Syntax modernization" if Path(name).suffix in {".py", ".cs", ".java", ".js", ".ts"} else "Manual review required"
