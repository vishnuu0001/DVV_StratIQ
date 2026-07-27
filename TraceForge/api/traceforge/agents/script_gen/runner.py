# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Generate or regenerate one script per approved test-case/framework pair.
# Date: 2026-03-15
# ---------------------------------------------------------------------------
"""Generate or regenerate one script per approved test-case/framework pair."""
from __future__ import annotations

import uuid
from collections.abc import Awaitable, Callable

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from traceforge.agents.script_gen.playwright import PlaywrightEmitter
from traceforge.agents.script_gen.validation import validate_typescript
from traceforge.db.ids import allocate_next_id
from traceforge.db.models import Requirement, SourceCitation, TestCase, TestScript
from traceforge.llm.ollama import OllamaProvider

_EMITTERS = [PlaywrightEmitter()]


# Function: _sources_label
def _sources_label(requirement: Requirement, citations: list[SourceCitation]) -> str:
    if not citations:
        return "(no source citation available)"
    first = citations[0]
    return f"{requirement.req_id} citation ({first.quoted_span[:60]}...)"


# Function: _build_citations_map
def _build_citations_map(citation_rows) -> dict[uuid.UUID, list[SourceCitation]]:
    citations_by_requirement: dict[uuid.UUID, list[SourceCitation]] = {}
    for citation in citation_rows:
        citations_by_requirement.setdefault(citation.requirement_id, []).append(citation)
    return citations_by_requirement


# Function: _dedupe_existing_scripts
def _dedupe_existing_scripts(
    existing_rows: list[TestScript],
) -> tuple[dict[tuple[uuid.UUID, str], TestScript], list[TestScript]]:
    """Keep the newest legacy row for each pair and remove append-only duplicates."""
    existing_by_key: dict[tuple[uuid.UUID, str], TestScript] = {}
    duplicate_rows: list[TestScript] = []
    for script in existing_rows:
        key = (script.test_case_id, script.target)
        if key in existing_by_key:
            duplicate_rows.append(script)
        else:
            existing_by_key[key] = script
    return existing_by_key, duplicate_rows


# Function: _generate_script_for_emitter
async def _generate_script_for_emitter(
    session: AsyncSession, provider, emitter, test_case, requirement, base_ctx,
    existing_by_key, project_id: uuid.UUID, pipeline_run_id: uuid.UUID | None,
) -> tuple[bool, str | None]:
    """Generates (or regenerates) one script for one test-case/emitter pair.
    Returns (inserted, warning) so the caller can tally counts and messages."""
    existing = existing_by_key.get((test_case.id, emitter.target))
    ctx = {**base_ctx, "previous_code": existing.code if existing else None}
    code, file_path, page_objects = await emitter.generate(
        session, provider, test_case, requirement, ctx, pipeline_run_id,
    )

    # Ollama authors every body, so validate every generated script independently.
    compiles, validation_output = await validate_typescript(code)

    if existing:
        existing.code = code
        existing.file_path = file_path
        existing.page_objects = page_objects
        existing.compiles = compiles
        existing.validation_output = validation_output
        existing.status = "DRAFT"
        existing.upstream_tc_hash = test_case.content_hash
        existing.version += 1
        script = existing
        inserted = False
    else:
        script = TestScript(
            ts_id=await allocate_next_id(session, project_id, "TS"), project_id=project_id,
            test_case_id=test_case.id, target=emitter.target, language="typescript", code=code,
            file_path=file_path, page_objects=page_objects, compiles=compiles,
            validation_output=validation_output, status="DRAFT",
            upstream_tc_hash=test_case.content_hash, version=1,
        )
        session.add(script)
        inserted = True

    warning = None
    if compiles is False:
        warning = f"{script.ts_id} ({emitter.target}) failed validation: {validation_output[:200]}"
    return inserted, warning


# Function: _process_test_case
async def _process_test_case(
    session: AsyncSession, provider, test_case, requirement, citations_by_requirement,
    existing_by_key, project_id: uuid.UUID, pipeline_run_id: uuid.UUID | None,
    warnings: list[str],
) -> tuple[int, int, int]:
    """Runs every applicable emitter for one test case. Returns (generated, inserted, updated) deltas."""
    citations = citations_by_requirement.get(requirement.id, [])
    base_ctx = {"sources_label": _sources_label(requirement, citations)}
    generated = inserted = updated = 0

    for emitter in _EMITTERS:
        if not emitter.can_handle(test_case):
            continue
        was_inserted, warning = await _generate_script_for_emitter(
            session, provider, emitter, test_case, requirement, base_ctx,
            existing_by_key, project_id, pipeline_run_id,
        )
        generated += 1
        if was_inserted:
            inserted += 1
        else:
            updated += 1
        if warning:
            warnings.append(warning)

    return generated, inserted, updated


# Function: run_script_generator
async def run_script_generator(
    session: AsyncSession, *, project_id: uuid.UUID, pipeline_run_id: uuid.UUID | None,
    progress: Callable[[int, int, int], Awaitable[None]] | None = None,
) -> dict:
    test_cases = list((await session.scalars(
        select(TestCase)
        .where(TestCase.project_id == project_id, TestCase.status == "APPROVED")
        .order_by(TestCase.tc_id)
    )).all())
    if not test_cases:
        raise ValueError("No APPROVED test cases - nothing to generate scripts for.")

    provider = OllamaProvider()
    requirement_ids = {tc.requirement_id for tc in test_cases}
    requirements = {
        req.id: req for req in (await session.scalars(
            select(Requirement).where(Requirement.id.in_(requirement_ids))
        )).all()
    }
    citation_rows = (await session.scalars(
        select(SourceCitation).where(SourceCitation.requirement_id.in_(requirement_ids))
    )).all()
    citations_by_requirement = _build_citations_map(citation_rows)

    existing_rows = list((await session.scalars(
        select(TestScript)
        .where(TestScript.project_id == project_id)
        .order_by(TestScript.ts_id.desc())
    )).all())
    legacy_rows = [script for script in existing_rows if script.target != "PLAYWRIGHT_TS"]
    playwright_rows = [script for script in existing_rows if script.target == "PLAYWRIGHT_TS"]
    existing_by_key, duplicate_rows = _dedupe_existing_scripts(playwright_rows)
    for obsolete in [*legacy_rows, *duplicate_rows]:
        await session.delete(obsolete)

    generated = inserted = updated = 0
    warnings: list[str] = []
    for index, test_case in enumerate(test_cases, start=1):
        requirement = requirements.get(test_case.requirement_id)
        if requirement is None:
            warnings.append(f"{test_case.tc_id}: linked requirement was not found")
            continue

        gen_delta, ins_delta, upd_delta = await _process_test_case(
            session, provider, test_case, requirement, citations_by_requirement,
            existing_by_key, project_id, pipeline_run_id, warnings,
        )
        generated += gen_delta
        inserted += ins_delta
        updated += upd_delta

        if index % 25 == 0 or index == len(test_cases):
            await session.commit()
            if progress:
                await progress(index, len(test_cases), generated)

    return {
        "scripts_created": generated,
        "scripts_inserted": inserted,
        "scripts_updated": updated,
        "duplicates_removed": len(duplicate_rows),
        "legacy_scripts_removed": len(legacy_rows),
        "warnings": warnings,
    }
