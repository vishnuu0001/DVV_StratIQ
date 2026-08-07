# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Arq job bodies. Run inside the TraceForge-Worker process (see workers/arq_worker.py),
# Date: 2025-09-30
# ---------------------------------------------------------------------------
"""Arq job bodies. Run inside the TraceForge-Worker process (see workers/arq_worker.py),
never inside the FastAPI/uvicorn process — Requirements.MD §2: 'Agent runs are
long-lived. They must NOT live inside the IIS worker process.'"""
from __future__ import annotations

import asyncio
import math
import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy import delete, func, select

from traceforge.agents.conflicts import detect_conflicts
from traceforge.agents.dedupe import deduplicate_requirements
from traceforge.agents.doc_author import (
    BRD_DEFINITION, FRD_DEFINITION, FSD_DEFINITION, SOLUTION_DOC_DEFINITION,
    run_doc_author,
)
from traceforge.agents.extractor import run_extractor
from traceforge.agents.renderer.evidence_pack import build_evidence_pack
from traceforge.agents.renderer.rtm_xlsx import render_rtm_xlsx
from traceforge.agents.script_gen.runner import run_script_generator
from traceforge.agents.test_designer import run_test_designer
from traceforge.config import AGENT_BATCH_SIZE_CHUNKS, STORAGE_DIR
from traceforge.connectors import github as github_connector
from traceforge.connectors import jira as jira_connector
from traceforge.connectors import servicenow as servicenow_connector
from traceforge.db.models import AuditEvent, Artifact, Chunk, Project, PipelineRun, Requirement, SourceDocument
from traceforge.db.session import SessionLocal
from traceforge.indexing.chunker import chunk_document
from traceforge.indexing.embedder import embed_texts
from traceforge.orchestration.gates import assert_stage_unblocked, open_gate
from traceforge.parsing.code import SUPPORTED_CODE_EXTENSIONS, parse_code
from traceforge.parsing.docx import parse_docx
from traceforge.parsing.pdf import parse_pdf
from traceforge.parsing.text import parse_text
from traceforge.parsing.xlsx import parse_xlsx

logger = logging.getLogger(__name__)

_STRUCTURED_PARSERS = {
    ".docx": parse_docx,
    ".pdf": parse_pdf,
    ".xlsx": parse_xlsx,
    ".md": parse_text,
    ".txt": parse_text,
}


# Function: ingest_source
async def ingest_source(ctx, source_document_id: str) -> dict:
    """Parse -> structure-aware chunk -> embed -> index (spec §4). docx/pdf/xlsx go
    through the shared structure-aware chunker; code files are already chunked at
    function/class granularity by tree-sitter and skip that step."""
    async with SessionLocal() as session:
        doc = await session.get(SourceDocument, uuid.UUID(source_document_id))
        if doc is None:
            return {"error": "source document not found"}

        doc.status = "PARSING"
        await session.commit()

        try:
            suffix = "." + doc.filename.rsplit(".", 1)[-1].lower() if "." in doc.filename else ""

            if suffix in SUPPORTED_CODE_EXTENSIONS:
                doc_chunks = await asyncio.to_thread(parse_code, doc.blob_uri)
            elif suffix in _STRUCTURED_PARSERS:
                parsed = await asyncio.to_thread(_STRUCTURED_PARSERS[suffix], doc.blob_uri)
                doc_chunks = await asyncio.to_thread(chunk_document, parsed)
            else:
                raise NotImplementedError(
                    f"No parser for '{suffix}' files (got '{doc.filename}'). "
                    f"docx/pdf/xlsx/code are implemented — see TraceForge/PROGRESS.md for the rest."
                )

            if not doc_chunks:
                raise ValueError("Parser produced zero chunks — is the document empty?")

            embeddings = await embed_texts([c.text for c in doc_chunks])

            # Rebuild/retry is idempotent: replace the prior vector rows instead of
            # violating uq_chunk_source_ordinal or leaving stale embeddings behind.
            await session.execute(delete(Chunk).where(Chunk.source_document_id == doc.id))

            for ordinal, (doc_chunk, embedding) in enumerate(zip(doc_chunks, embeddings)):
                session.add(
                    Chunk(
                        source_document_id=doc.id,
                        project_id=doc.project_id,
                        ordinal=getattr(doc_chunk, "ordinal", ordinal),
                        text=doc_chunk.text,
                        token_count=doc_chunk.token_count,
                        locator=doc_chunk.locator,
                        embedding=embedding,
                        chunk_metadata={"doc_class": doc.doc_class},
                    )
                )

            doc.status = "INDEXED"
            doc.ingested_at = datetime.now(timezone.utc)
            doc.page_count = None
            doc.parse_error = None
            await session.commit()
            return {"status": "INDEXED", "chunks": len(doc_chunks)}

        except Exception as exc:  # noqa: BLE001 — must record the failure, not crash the worker
            logger.exception("ingest_source failed for %s", source_document_id)
            message = f"{type(exc).__name__}: {exc}" if str(exc) else type(exc).__name__
            await session.rollback()  # a failed flush/commit leaves the session's transaction
            # aborted (Postgres refuses further statements on it) — must roll back before the
            # FAILED-status write below, or that write itself raises PendingRollbackError and
            # the run/doc silently never leaves its in-progress status.
            doc.status = "FAILED"
            doc.parse_error = message
            await session.commit()
            return {"status": "FAILED", "error": message}


# Function: run_extract_stage
async def run_extract_stage(ctx, pipeline_run_id: str) -> dict:
    """Agent 1 sweep for every INDEXED chunk in the project (spec §5 Agent 1:
    'sweep the entire corpus', not a RAG query)."""
    async with SessionLocal() as session:
        run = await session.get(PipelineRun, uuid.UUID(pipeline_run_id))
        if run is None:
            return {"error": "pipeline run not found"}

        run.status = "RUNNING"
        run.started_at = datetime.now(timezone.utc)
        await session.commit()

        try:
            await assert_stage_unblocked(session, run.project_id, "EXTRACT")

            result = await session.execute(
                select(Chunk)
                .join(SourceDocument, Chunk.source_document_id == SourceDocument.id)
                .where(Chunk.project_id == run.project_id, SourceDocument.status == "INDEXED")
                .order_by(SourceDocument.ingested_at, Chunk.ordinal)
            )
            chunks = list(result.scalars().all())
            if not chunks:
                raise ValueError("No indexed source chunks are available for extraction.")
            all_chunks_count = len(chunks)
            prior_run = await session.scalar(
                select(PipelineRun)
                .where(
                    PipelineRun.project_id == run.project_id, PipelineRun.stage == "EXTRACT",
                    PipelineRun.id != run.id, PipelineRun.status == "FAILED",
                )
                .order_by(PipelineRun.created_at.desc()).limit(1)
            )
            resume_from = min(
                int((prior_run.stats or {}).get("chunks_processed", 0)) if prior_run else 0,
                all_chunks_count,
            )
            chunks = chunks[resume_from:]
            project = await session.get(Project, run.project_id)
            glossary = (project.config.get("glossary", []) if project else [])
            existing_requirement_count = await session.scalar(
                select(func.count()).select_from(Requirement).where(Requirement.project_id == run.project_id)
            ) or 0

            # Function: report_progress
            async def report_progress(batch: int, total: int, summary, phase: str, response_chunks: int = 0) -> None:
                run.stats = {
                    "phase": phase,
                    "batch_current": batch,
                    "batch_total": total,
                    "chunks_total": all_chunks_count,
                    "chunks_processed": min(all_chunks_count, resume_from + summary.chunks_processed),
                    "items_generated": existing_requirement_count + summary.requirements_created,
                    "rejected_no_citation": summary.requirements_rejected_no_citation,
                    "rejected_unsupported": summary.requirements_rejected_unsupported,
                    "duplicates_skipped": summary.duplicates_skipped,
                    "rag_chunks_retrieved": summary.rag_chunks_retrieved,
                    "compact_retries_used": summary.compact_retries_used,
                    "deterministic_fallback_used": summary.deterministic_fallback_used,
                    "warnings_count": len(summary.warnings),
                    "response_chunks": summary.response_chunks_received,
                    "resumed_from_chunk": resume_from,
                }
                await session.commit()

            summary = await run_extractor(
                session, project_id=run.project_id, chunks=chunks, glossary=glossary,
                pipeline_run_id=run.id, progress=report_progress,
            )

            # §5 Agent 1 'Additional passes' — dedup near-duplicates (embedding cosine
            # > 0.92) then flag cross-document conflicts, both over the DRAFT batch this
            # run just created, before the gate opens for BA review.
            parse_failures = [
                warning for warning in summary.warnings
                if "JSON parse failure" in warning
            ]
            if summary.requirements_created == 0:
                total_requirements_after_extract = await session.scalar(
                    select(func.count()).select_from(Requirement).where(Requirement.project_id == run.project_id)
                ) or 0
                if total_requirements_after_extract == 0:
                    reason = (
                        f"invalid JSON after retry: {parse_failures[-1]}" if parse_failures
                        else "every model item failed citation or source-grounding validation"
                    )
                    message = f"Extraction produced no grounded requirements: {reason}"
                    logger.error("run_extract_stage failed closed for %s: %s", pipeline_run_id, message)
                    run.stats = {
                        **run.stats,
                        "phase": "extraction_failed",
                        "warnings": summary.warnings,
                        "items_generated_this_run": 0,
                        "rejected_no_citation": summary.requirements_rejected_no_citation,
                        "rejected_unsupported": summary.requirements_rejected_unsupported,
                        "duplicates_skipped": summary.duplicates_skipped,
                        "rag_chunks_retrieved": summary.rag_chunks_retrieved,
                        "compact_retries_used": summary.compact_retries_used,
                        "deterministic_fallback_used": summary.deterministic_fallback_used,
                        "response_chunks": summary.response_chunks_received,
                        "chunks_processed": min(all_chunks_count, resume_from + summary.chunks_processed),
                    }
                    run.status = "FAILED"
                    run.error = message
                    run.finished_at = datetime.now(timezone.utc)
                    await session.commit()
                    return {"status": "FAILED", "error": message}
                summary.warnings.append(
                    "extractor: JSON parse failures occurred, but existing requirements were preserved; continuing pipeline"
                )

            run.stats = {**run.stats, "phase": "deduplicating"}
            await session.commit()
            dedupe_summary = await deduplicate_requirements(session, run.project_id)

            run.stats = {**run.stats, "phase": "detecting_conflicts"}
            await session.commit()
            conflict_summary = await detect_conflicts(session, run.project_id, run.id)
            await session.commit()

            total_requirements = await session.scalar(
                select(func.count()).select_from(Requirement).where(Requirement.project_id == run.project_id)
            )
            run.stats = {
                "items_generated": total_requirements or 0,
                "items_generated_this_run": summary.requirements_created,
                "chunks_processed": all_chunks_count,
                "chunks_total": all_chunks_count,
                "resumed_from_chunk": resume_from,
                "rejected_no_citation": summary.requirements_rejected_no_citation,
                "rejected_unsupported": summary.requirements_rejected_unsupported,
                "duplicates_skipped": summary.duplicates_skipped,
                "rag_chunks_retrieved": summary.rag_chunks_retrieved,
                "compact_retries_used": summary.compact_retries_used,
                "deterministic_fallback_used": summary.deterministic_fallback_used,
                "response_chunks": summary.response_chunks_received,
                "chunks_processed_this_run": summary.chunks_processed,
                "warnings": summary.warnings + conflict_summary.warnings,
                "dedup_merged_count": dedupe_summary.merged_count,
                "dedup_merges": dedupe_summary.merges,
                "conflicts_found": conflict_summary.conflicts_found,
                "conflict_pairs": conflict_summary.pairs,
            }
            run.finished_at = datetime.now(timezone.utc)
            await open_gate(session, run)  # -> AWAITING_APPROVAL, opens Gate 1
            await session.commit()
            return {"status": "AWAITING_APPROVAL", "requirements_created": summary.requirements_created}

        except asyncio.CancelledError:
            logger.error("run_extract_stage timed out or was cancelled for %s", pipeline_run_id)
            await session.rollback()
            run.status = "FAILED"
            run.error = "Extraction timed out or the worker was restarted. The run can be started again safely."
            run.finished_at = datetime.now(timezone.utc)
            await session.commit()
            raise
        except Exception as exc:  # noqa: BLE001
            logger.exception("run_extract_stage failed for %s", pipeline_run_id)
            message = f"{type(exc).__name__}: {exc}" if str(exc) else type(exc).__name__
            await session.rollback()  # see ingest_source's except block for why this is required
            run.status = "FAILED"
            run.error = message
            run.finished_at = datetime.now(timezone.utc)
            await session.commit()
            return {"status": "FAILED", "error": message}


# Function: _record_connector_failure
async def _record_connector_failure(project_id: uuid.UUID, connector: str, message: str) -> None:
    async with SessionLocal() as session:
        session.add(AuditEvent(
            project_id=project_id, actor=f"connector:{connector}", action="CONNECTOR_INGEST_FAILED",
            entity_type="SourceDocument", entity_id=str(project_id), after={"error": message},
        ))
        await session.commit()


# Function: ingest_servicenow_task
async def ingest_servicenow_task(
    ctx, project_id: str, base_url: str, username: str, password: str,
    tables: list[str], window_months: int, verify_ssl: bool,
) -> dict:
    async with SessionLocal() as session:
        try:
            counts = await servicenow_connector.ingest_servicenow(
                session, uuid.UUID(project_id), base_url=base_url, username=username, password=password,
                tables=tables, window_months=window_months, verify_ssl=verify_ssl,
            )
            return {"status": "completed", "counts": counts}
        except Exception as exc:  # noqa: BLE001
            logger.exception("ingest_servicenow_task failed for project %s", project_id)
            message = f"{type(exc).__name__}: {exc}" if str(exc) else type(exc).__name__
            await _record_connector_failure(uuid.UUID(project_id), "servicenow", message)
            return {"status": "FAILED", "error": message}


# Function: ingest_jira_task
async def ingest_jira_task(ctx, project_id: str, base_url: str, email: str, api_token: str, jql: str, max_results: int) -> dict:
    async with SessionLocal() as session:
        try:
            count = await jira_connector.ingest_jira(
                session, uuid.UUID(project_id), base_url=base_url, email=email, api_token=api_token,
                jql=jql, max_results=max_results,
            )
            return {"status": "completed", "issues_ingested": count}
        except Exception as exc:  # noqa: BLE001
            logger.exception("ingest_jira_task failed for project %s", project_id)
            message = f"{type(exc).__name__}: {exc}" if str(exc) else type(exc).__name__
            await _record_connector_failure(uuid.UUID(project_id), "jira", message)
            return {"status": "FAILED", "error": message}


# Function: ingest_github_task
async def ingest_github_task(ctx, project_id: str, repo_url: str, token: str | None, ref: str | None) -> dict:
    async with SessionLocal() as session:
        try:
            count = await github_connector.ingest_github_repo(session, uuid.UUID(project_id), repo_url=repo_url, token=token, ref=ref)
            return {"status": "completed", "chunks_ingested": count}
        except Exception as exc:  # noqa: BLE001
            logger.exception("ingest_github_task failed for project %s", project_id)
            message = f"{type(exc).__name__}: {exc}" if str(exc) else type(exc).__name__
            await _record_connector_failure(uuid.UUID(project_id), "github", message)
            return {"status": "FAILED", "error": message}


# Function: _run_stage
async def _run_stage(pipeline_run_id: str, stage: str, work) -> dict:
    """Shared run-lifecycle wrapper: RUNNING -> (work) -> AWAITING_APPROVAL/gate, or FAILED."""
    async with SessionLocal() as session:
        run = await session.get(PipelineRun, uuid.UUID(pipeline_run_id))
        if run is None:
            return {"error": "pipeline run not found"}
        run.status = "RUNNING"
        run.started_at = datetime.now(timezone.utc)
        await session.commit()

        try:
            await assert_stage_unblocked(session, run.project_id, stage)
            stats = await work(session, run)
            run.stats = stats
            run.finished_at = datetime.now(timezone.utc)
            await open_gate(session, run)
            await session.commit()
            return {"status": "AWAITING_APPROVAL", **stats}
        except asyncio.CancelledError:
            await session.rollback()
            run.status = "FAILED"
            run.error = "Stopped by user. Completed work remains available."
            run.finished_at = datetime.now(timezone.utc)
            await session.commit()
            raise
        except Exception as exc:  # noqa: BLE001
            logger.exception("%s stage failed for run %s", stage, pipeline_run_id)
            message = f"{type(exc).__name__}: {exc}" if str(exc) else type(exc).__name__
            await session.rollback()  # see ingest_source's except block for why this is required
            run.status = "FAILED"
            run.error = message
            run.finished_at = datetime.now(timezone.utc)
            await session.commit()
            return {"status": "FAILED", "error": message}


# Function: run_brd_stage
async def run_brd_stage(ctx, pipeline_run_id: str) -> dict:
    """BRD stage fans out to three agents (BRD/FSD/SolutionDoc) under one Gate 2 —
    all three are generated from the same approved-requirements input, so one review
    pass covers all three rather than three sequential gate stops."""
    # Function: work
    async def work(session, run):
        artifacts = []
        definitions = (
            BRD_DEFINITION, FRD_DEFINITION, FSD_DEFINITION, SOLUTION_DOC_DEFINITION,
        )
        for index, definition in enumerate(definitions, start=1):
            run.stats = {
                "phase": "generating_documents", "document_current": index,
                "document_total": len(definitions), "document_kind": definition.doc_kind,
                "artifacts_generated": artifacts,
            }
            await session.commit()
            artifact = await run_doc_author(session, project_id=run.project_id, definition=definition, pipeline_run_id=run.id)
            artifacts.append(artifact.filename)
        return {"artifacts_generated": artifacts}

    return await _run_stage(pipeline_run_id, "BRD", work)


# Function: run_test_design_stage
async def run_test_design_stage(ctx, pipeline_run_id: str) -> dict:
    # Function: work
    async def work(session, run):
        # Function: report_progress
        async def report_progress(completed: int, total: int, created: int) -> None:
            run.stats = {
                "phase": "designing_tests", "requirements_completed": completed,
                "requirements_total": total, "test_cases_created": created,
            }
            await session.commit()

        summary = await run_test_designer(
            session, project_id=run.project_id, pipeline_run_id=run.id, progress=report_progress,
        )
        return {"test_plan_id": str(summary.test_plan_id) if summary.test_plan_id else None,
                "test_cases_created": summary.test_cases_created, "warnings": summary.warnings}

    return await _run_stage(pipeline_run_id, "TEST_DESIGN", work)


# Function: run_script_gen_stage
async def run_script_gen_stage(ctx, pipeline_run_id: str) -> dict:
    # Function: work
    async def work(session, run):
        # Function: report_progress
        async def report_progress(completed: int, total: int, created: int) -> None:
            run.stats = {
                "phase": "generating_scripts", "test_cases_completed": completed,
                "test_cases_total": total, "scripts_created": created,
            }
            await session.commit()

        return await run_script_generator(
            session, project_id=run.project_id, pipeline_run_id=run.id, progress=report_progress,
        )

    return await _run_stage(pipeline_run_id, "SCRIPT_GEN", work)


# Function: run_render_stage
async def run_render_stage(ctx, pipeline_run_id: str) -> dict:
    """RENDER is the terminal stage (RENDER -> DONE in the spec's state machine) — no
    gate after it, just marks the run APPROVED once the artifacts are written."""
    async with SessionLocal() as session:
        run = await session.get(PipelineRun, uuid.UUID(pipeline_run_id))
        if run is None:
            return {"error": "pipeline run not found"}
        run.status = "RUNNING"
        run.started_at = datetime.now(timezone.utc)
        await session.commit()

        try:
            await assert_stage_unblocked(session, run.project_id, "RENDER")
            project = await session.get(Project, run.project_id)
            artifacts_dir = STORAGE_DIR / str(run.project_id) / "artifacts"
            artifacts_dir.mkdir(parents=True, exist_ok=True)

            rtm_path = artifacts_dir / f"RTM_{project.key}_v1.xlsx"
            await render_rtm_xlsx(session, run.project_id, str(rtm_path))
            import hashlib
            rtm_artifact = Artifact(
                project_id=run.project_id, pipeline_run_id=run.id, kind="RTM_XLSX",
                filename=rtm_path.name, blob_uri=str(rtm_path),
                sha256=hashlib.sha256(rtm_path.read_bytes()).hexdigest(), version=1,
            )
            session.add(rtm_artifact)
            await session.flush()

            pack_path = artifacts_dir / f"evidence_pack_{project.key}_v1.zip"
            await build_evidence_pack(session, run.project_id, str(pack_path))
            pack_artifact = Artifact(
                project_id=run.project_id, pipeline_run_id=run.id, kind="TEST_PACK_ZIP",
                filename=pack_path.name, blob_uri=str(pack_path),
                sha256=hashlib.sha256(pack_path.read_bytes()).hexdigest(), version=1,
            )
            session.add(pack_artifact)

            run.stats = {"rtm": rtm_path.name, "evidence_pack": pack_path.name}
            run.status = "APPROVED"
            run.finished_at = datetime.now(timezone.utc)
            await session.commit()
            return {"status": "APPROVED", **run.stats}
        except Exception as exc:  # noqa: BLE001
            logger.exception("RENDER stage failed for run %s", pipeline_run_id)
            message = f"{type(exc).__name__}: {exc}" if str(exc) else type(exc).__name__
            await session.rollback()  # see ingest_source's except block for why this is required
            run.status = "FAILED"
            run.error = message
            run.finished_at = datetime.now(timezone.utc)
            await session.commit()
            return {"status": "FAILED", "error": message}
