# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Orchestrates the Wave Planning analysis job: deterministic parsing/wave-assignment
# Date: 2026-05-19
# ---------------------------------------------------------------------------
"""
Orchestrates the Wave Planning analysis job: deterministic parsing/wave-assignment
-> LLM classification -> LLM narrative generation -> persistence, with incremental
per-category status updates so polling clients see real progress.

create_job() does the fast, synchronous setup (called from the request handler).
run_analysis_job() does the slow work and is spawned in a background thread with
its own DB session (never share the request-scoped session across threads).
"""
from __future__ import annotations

import json
import logging
from collections import Counter, defaultdict
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from database import SessionLocal
from models_wave import AnalysisJob, DatasetRow, UploadedDataset, WaveApp, WaveCategorySummary
from wave_deterministic import (
    assign_quarters,
    assign_waves,
    capability_tier,
    cluster_departments,
    matches_specialized_capability,
    modernization_eligible,
    parse_capabilities,
)
from wave_llm_service import classify_apps, generate_classification_summary, resolve_ollama_model

logger = logging.getLogger(__name__)


# Function: _load_dataset_rows
def _load_dataset_rows(db: Session, dataset_id: int) -> list[dict]:
    rows = db.query(DatasetRow).filter(DatasetRow.dataset_id == dataset_id).order_by(DatasetRow.source_row_index).all()
    return [json.loads(r.data) for r in rows]


# Function: preview_categories
def preview_categories(db: Session, scope_dataset_id: int, categorization_dataset_id: int) -> list[dict]:
    """List categories available for analysis from an uploaded dataset pair, with app
    counts, so the frontend can offer a select-some-or-all picker before submitting."""
    scope_rows = _load_dataset_rows(db, scope_dataset_id)
    cat_rows = _load_dataset_rows(db, categorization_dataset_id)

    scope_by_name = {r["solution_approach"]: r for r in scope_rows}
    counts: dict[str, int] = {}
    for r in cat_rows:
        if r["category"]:
            counts[r["category"]] = counts.get(r["category"], 0) + 1

    out = []
    for category, count in sorted(counts.items()):
        out.append({
            "category": category,
            "app_count": count,
            "matched_in_scope": category in scope_by_name,
        })
    return out


# Function: create_job
def create_job(
    db: Session,
    scope_dataset_id: int,
    categorization_dataset_id: int,
    selected_categories: list[str] | None = None,
    user_guidance: str | None = None,
) -> tuple[AnalysisJob, list[str]]:
    """Fast synchronous setup: validate datasets, create the job + one pending
    WaveCategorySummary per selected category (or every category found in the data,
    if selected_categories is None/empty). Returns (job, unmatched_categories)."""
    scope_ds = db.query(UploadedDataset).get(scope_dataset_id)
    cat_ds = db.query(UploadedDataset).get(categorization_dataset_id)
    if not scope_ds or scope_ds.kind != "scope":
        raise ValueError(f"scope_dataset_id {scope_dataset_id} not found or not a scope dataset")
    if not cat_ds or cat_ds.kind != "categorization":
        raise ValueError(f"categorization_dataset_id {categorization_dataset_id} not found or not a categorization dataset")

    scope_rows = _load_dataset_rows(db, scope_dataset_id)
    cat_rows = _load_dataset_rows(db, categorization_dataset_id)

    scope_by_name = {r["solution_approach"]: r for r in scope_rows}
    all_categories = sorted({r["category"] for r in cat_rows if r["category"]})

    if selected_categories:
        selected_set = set(selected_categories)
        categories_in_data = [c for c in all_categories if c in selected_set]
        if not categories_in_data:
            raise ValueError("None of the selected categories were found in the uploaded categorization data.")
    else:
        categories_in_data = all_categories

    unmatched = [c for c in categories_in_data if c not in scope_by_name]

    job = AnalysisJob(
        status="pending",
        scope_dataset_id=scope_dataset_id,
        categorization_dataset_id=categorization_dataset_id,
        total_categories=len(categories_in_data),
        completed_categories=0,
        unmatched_categories=json.dumps(unmatched),
        user_guidance=user_guidance.strip()[:2000] if user_guidance and user_guidance.strip() else None,
    )
    db.add(job)
    db.flush()  # get job.id

    for category in categories_in_data:
        scope_info = scope_by_name.get(category, {})
        db.add(WaveCategorySummary(
            job_id=job.id,
            category=category,
            status="pending",
            description=scope_info.get("description", ""),
            estimated_app_count=scope_info.get("estimated_app_count", 0),
        ))

    db.commit()
    db.refresh(job)
    return job, unmatched


# Function: _prep_apps_for_llm
def _prep_apps_for_llm(apps: list[dict]) -> list[dict]:
    prepped = []
    for a in apps:
        caps = parse_capabilities(a["capabilities_raw"])
        hint, term = matches_specialized_capability(caps)
        mod_eligible, mod_phrase = modernization_eligible(a["app_name"], a["capabilities_raw"])
        prepped.append({
            "app_id": a["app_id"],
            "app_name": a["app_name"],
            "capabilities": caps,
            "capability_count": len(caps),
            "specialized_capability_hint": hint,
            "modernization_eligible": mod_eligible,
        })
    return prepped


# Function: _process_category
def _process_category(db: Session, job: AnalysisJob, category: str, apps: list[dict], model: str) -> None:
    cat_summary = db.query(WaveCategorySummary).filter_by(job_id=job.id, category=category).first()
    cat_summary.status = "running"
    db.commit()

    # Function: report_step
    def report_step(step_text: str) -> None:
        cat_summary.current_step = step_text
        db.commit()

    try:
        # 1. Deterministic: wave assignment + quarters + capability tiers.
        report_step(f"Preparing {len(apps)} applications…")
        wave_map = assign_waves(apps)
        dept_counts = cluster_departments(apps)
        dept_stats = [
            {"dept": d, "clean_count": c, "rank": i + 1}
            for i, (d, c) in enumerate(sorted(dept_counts.items(), key=lambda kv: kv[1], reverse=True))
        ]

        # 2. LLM: disposition (Harmonization/Modernization) + archival judgment. Migration
        # Type itself is computed deterministically inside classify_apps (see wave_llm_service).
        apps_for_llm = _prep_apps_for_llm(apps)
        classifications = classify_apps(
            category, cat_summary.description, apps_for_llm, model,
            user_guidance=job.user_guidance, on_progress=report_step,
        )
        classification_counts = Counter(v["migration_type"] for v in classifications.values())
        disposition_counts = Counter(v["disposition"] for v in classifications.values())

        # 3. LLM: one category-level narrative summary (holistic synthesis is a reasonable
        # LLM task; per-app rationale is NOT — see wave_deterministic.assign_waves' wave_reason).
        report_step("Writing category summary…")
        total_apps = len(apps)

        # Function: _pct_label
        def _pct_label(n: int) -> str:
            pct = round(100 * n / total_apps) if total_apps else 0
            return f"{n} of {total_apps} apps ({pct}%)"

        # Pre-formatted "N of M (P%)" strings, not raw counts — the LLM does not need to
        # (and empirically cannot reliably) do this arithmetic itself; it only quotes these.
        rollup_stats = {
            "total_apps": total_apps,
            "wave_count": len({wave_map[a["app_id"]]["wave"] for a in apps}),
            "pilot_department": next(
                (a["dept"] for a in apps if wave_map[a["app_id"]]["wave"] == "Wave 0 (Pilot)"), None,
            ),
            "data_quality_issues": _pct_label(sum(1 for a in apps if a["data_quality_flag"])),
            **{k: _pct_label(v) for k, v in classification_counts.items()},
            **{f"disposition_{k.lower()}": _pct_label(v) for k, v in disposition_counts.items()},
        }
        notable_apps = [
            {"app_id": a["app_id"], "app_name": a["app_name"], "dept": a["dept"], "reason": "data quality flag"}
            for a in apps if a["data_quality_flag"]
        ][:5] or [
            {"app_id": a["app_id"], "app_name": a["app_name"], "dept": a["dept"], "reason": "TBD migration type"}
            for a in apps if classifications.get(a["app_id"], {}).get("migration_type") == "TBD (data gap)"
        ][:5]
        logic_summary = generate_classification_summary(
            category, rollup_stats, notable_apps, model, user_guidance=job.user_guidance,
        )
        report_step("Saving results…")

        # 4. Persist WaveApp rows.
        timelines = []
        for a in apps:
            wave_info = wave_map[a["app_id"]]
            quarters = assign_quarters(wave_info["wave"])
            timelines.append(quarters["stream2_assessment"])
            caps = parse_capabilities(a["capabilities_raw"])
            _, matched_term = matches_specialized_capability(caps)
            classification = classifications.get(a["app_id"], {
                "disposition": "Harmonization", "service_module": None, "modernization_trigger_category": None,
                "disposition_rationale": "", "migration_type": "TBD (data gap)", "notes_assumptions": "",
            })

            db.add(WaveApp(
                job_id=job.id,
                category_summary_id=cat_summary.id,
                category=category,
                app_id=a["app_id"],
                app_name=a["app_name"],
                dept=a["dept"],
                dept_full=a["dept_full"],
                dept2=a["dept2"],
                business_owner=a["business_owner"],
                it_owner=a["it_owner"],
                # Cleaned, comma-joined capability names — drop the source data's trailing
                # "(Provides)," verbosity, which is a raw-extract artifact, not user-facing content.
                capabilities_raw=", ".join(caps) if caps else a["capabilities_raw"],
                capability_count=len(caps),
                capability_tier=capability_tier(len(caps)),
                matched_specialized_capability=bool(matched_term),
                matched_specialized_term=matched_term,
                data_quality_flag=a["data_quality_flag"],
                remediation_required=a["data_quality_flag"],
                migration_type=classification["migration_type"],
                disposition=classification["disposition"],
                service_module=classification["service_module"],
                modernization_trigger_category=classification["modernization_trigger_category"],
                disposition_rationale=classification["disposition_rationale"],
                wave=wave_info["wave"],
                change_management="TBD - pending designation",
                decommissioning="Yes - source app decommissioned after migration" if not a["data_quality_flag"] else "TBD - pending remediation",
                stream2_assessment=quarters["stream2_assessment"],
                stream3_execution=quarters["stream3_execution"],
                ams_transition_start=quarters["ams_transition_start"],
                notes_assumptions=classification["notes_assumptions"],
                wave_assignment_rationale=wave_info["wave_reason"],
                rejoins_wave=wave_info["rejoins_wave"],
                rejoin_rationale=wave_info["rejoin_rationale"],
            ))

        cat_summary.status = "done"
        cat_summary.current_step = None
        cat_summary.actual_app_count = len(apps)
        cat_summary.timeline_start = min(timelines) if timelines else None
        cat_summary.timeline_end = max(
            (assign_quarters(w["wave"])["ams_transition_start"] for w in wave_map.values()), default=None,
        )
        cat_summary.classification_logic_notes = logic_summary
        db.commit()

    except Exception as exc:
        db.rollback()
        cat_summary.status = "failed"
        cat_summary.current_step = None
        cat_summary.error_message = str(exc)[:1000]
        db.commit()
        logger.exception("Category '%s' failed in job %d", category, job.id)

    job.completed_categories += 1
    db.commit()


# Function: run_analysis_job
def run_analysis_job(job_id: int) -> None:
    db = SessionLocal()
    try:
        job = db.query(AnalysisJob).get(job_id)
        if not job:
            logger.error("run_analysis_job: job %d not found", job_id)
            return

        job.status = "running"
        job.started_at = datetime.now(timezone.utc)
        db.commit()

        cat_rows = _load_dataset_rows(db, job.categorization_dataset_id)
        by_category: dict[str, list[dict]] = defaultdict(list)
        for r in cat_rows:
            if r["category"]:
                by_category[r["category"]].append(r)

        model = resolve_ollama_model()
        job.llm_model = model
        db.commit()

        summaries = db.query(WaveCategorySummary).filter_by(job_id=job_id).all()
        for cat_summary in summaries:
            apps = by_category.get(cat_summary.category, [])
            if not apps:
                cat_summary.status = "failed"
                cat_summary.error_message = "No app rows found for this category in the uploaded categorization file."
                db.commit()
                job.completed_categories += 1
                db.commit()
                continue
            _process_category(db, job, cat_summary.category, apps, model)

        succeeded = db.query(WaveCategorySummary).filter_by(job_id=job_id, status="done").count()
        job.status = "done" if succeeded > 0 else "failed"
        if succeeded == 0:
            job.error_message = "All categories failed — see per-category error_message for details."
        job.completed_at = datetime.now(timezone.utc)
        db.commit()

    except Exception as exc:
        logger.exception("run_analysis_job %d crashed", job_id)
        try:
            job = db.query(AnalysisJob).get(job_id)
            if job:
                job.status = "failed"
                job.error_message = str(exc)[:1000]
                job.completed_at = datetime.now(timezone.utc)
                db.commit()
        except Exception:
            pass
    finally:
        db.close()
