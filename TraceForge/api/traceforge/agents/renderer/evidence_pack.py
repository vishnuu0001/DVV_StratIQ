# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: §5.3 Agent 5 — Test Evidence Pack (ZIP). Structure adapted from the spec: pytest/karate
# Date: 2025-12-08
# ---------------------------------------------------------------------------
"""§5.3 Agent 5 — Test Evidence Pack (ZIP). Structure adapted from the spec: pytest/karate
folders replaced with playwright/selenium (the two emitters this build actually has),
and BRD/FSD/SolutionDoc all included (new document types this pass)."""
from __future__ import annotations

import hashlib
import json
import uuid
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from traceforge.db.models import Artifact, Project, SourceDocument, TestScript
from traceforge.llm.ollama import OllamaProvider


# Function: _add_file
def _add_file(zf: zipfile.ZipFile, manifest: dict, arcname: str, data: bytes | None = None, src_path: str | None = None) -> None:
    if src_path:
        data = Path(src_path).read_bytes()
    if data is None:
        return
    zf.writestr(arcname, data)
    manifest["files"].append({"path": arcname, "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)})


# Function: _script_subdir
def _script_subdir(target: str) -> str:
    if target == "PLAYWRIGHT_TS":
        return "playwright"
    if target == "SELENIUM_TS":
        return "selenium"
    return target.lower()


# Function: _add_document_artifacts
def _add_document_artifacts(zf: zipfile.ZipFile, manifest: dict, latest_by_kind: dict, project_key: str, version: str) -> None:
    for prefix, kind in [("01_BRD", "BRD_DOCX"), ("01a_SRS_FRS", "FRD_DOCX"), ("01b_FSD", "FSD_DOCX"), ("01c_SolutionDoc", "SOLUTION_DOC_DOCX"),
                          ("01d_TestPlan", "TEST_PLAN_DOCX"), ("02_RTM", "RTM_XLSX")]:
        artifact = latest_by_kind.get(kind)
        if artifact:
            _add_file(zf, manifest, f"{prefix}_{project_key}_{version}{Path(artifact.filename).suffix}", src_path=artifact.blob_uri)


# Function: _add_test_scripts
def _add_test_scripts(zf: zipfile.ZipFile, manifest: dict, scripts: list, project_key: str) -> None:
    for script in scripts:
        subdir = _script_subdir(script.target)
        _add_file(zf, manifest, f"04_scripts/{subdir}/{script.file_path.split('/')[-1]}", data=script.code.encode())

    if scripts:
        _add_file(zf, manifest, "04_scripts/playwright/package.json", data=json.dumps({
            "name": f"{project_key}-tests", "devDependencies": {"@playwright/test": "*", "typescript": "*"},
        }, indent=2).encode())
        _add_file(zf, manifest, "04_scripts/playwright/playwright.config.ts",
                  data=b"import { defineConfig } from '@playwright/test';\nexport default defineConfig({ testDir: './' });\n")


# Function: build_evidence_pack
async def build_evidence_pack(session: AsyncSession, project_id: uuid.UUID, output_path: str, version: str = "v1") -> None:
    project = await session.get(Project, project_id)
    if project is None:
        raise ValueError(f"project {project_id} not found")

    artifacts = list((await session.execute(
        select(Artifact).where(Artifact.project_id == project_id).order_by(Artifact.generated_at.desc())
    )).scalars().all())
    latest_by_kind: dict[str, Artifact] = {}
    for artifact in artifacts:
        latest_by_kind.setdefault(artifact.kind, artifact)

    scripts = list((await session.execute(select(TestScript).where(TestScript.project_id == project_id))).scalars().all())
    sources = list((await session.execute(
        select(SourceDocument).where(SourceDocument.project_id == project_id, SourceDocument.deleted_at.is_(None))
    )).scalars().all())

    manifest: dict = {
        "project_key": project.key, "generated_at": datetime.now(timezone.utc).isoformat(),
        "model": OllamaProvider().model, "files": [],
    }

    output_path_obj = Path(output_path)
    output_path_obj.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        _add_document_artifacts(zf, manifest, latest_by_kind, project.key, version)
        _add_test_scripts(zf, manifest, scripts, project.key)

        source_index_rows = "\n".join(f"{s.filename}\t{s.sha256}\t{s.ingested_at}\t{s.status}" for s in sources)
        _add_file(zf, manifest, "05_source_index.tsv", data=("filename\tsha256\tingested_at\tstatus\n" + source_index_rows).encode())

        audit_note = "See the Audit sheet in the RTM workbook for the full append-only trail."
        _add_file(zf, manifest, "06_audit_trail.txt", data=audit_note.encode())

        # MANIFEST.json is written last so it can include every other file's hash —
        # it does not (and cannot) include its own hash.
        zf.writestr("MANIFEST.json", json.dumps(manifest, indent=2))
