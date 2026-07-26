# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: OpportunityTracker — backend/routers (wave_analysis.py)
# Date: 2026-05-18
# ---------------------------------------------------------------------------
import json
import os
import threading
import uuid
from datetime import datetime, timezone

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy import func
from sqlalchemy.orm import Session

from auth import get_current_user
from database import get_db
from models_wave import AnalysisJob, DatasetRow, UploadedDataset, WaveApp, WaveCategorySummary
from schemas_wave import (
    AnalysisSubmitRequest,
    AnalysisSubmitResponse,
    CategoryPreviewOut,
    CategoryStatusOut,
    CategorySummaryOut,
    DatasetOut,
    GanttRowOut,
    JobStatusOut,
    WaveAppOut,
    WaveSummaryOut,
)
from wave_deterministic import assign_quarters, parse_categorization_file, parse_scope_file
from wave_job_runner import create_job, preview_categories, run_analysis_job

router = APIRouter(tags=["wave-analysis"])

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

REMEDIATION_PROCESS_TEXT = (
    "This table details applications flagged for data remediation. Each app carries a data-quality "
    "inconsistency in the source data, indicating metadata discrepancies requiring resolution before "
    "migration can proceed.\n\n"
    "REMEDIATION PROCESS:\n"
    "1. Root Cause Analysis — application owners and data administrators identify the specific "
    "inconsistency (e.g. missing capability data, ownership conflicts, incorrect classification).\n"
    "2. Data Correction — fix identified issues directly in the source system; update the data extract "
    "to reflect corrections.\n"
    "3. Re-validation — the assessment team confirms data integrity and assigns/confirms the Migration "
    "Type classification.\n"
    "4. Wave Re-assignment — once validated, apps rejoin their designated wave cohort (see 'Rejoins wave' "
    "column).\n\n"
    "TIMELINE: Remediation runs in parallel with the pilot wave. Apps must complete steps 1-3 before "
    "their target wave's Assessment phase begins, otherwise they shift to the next available wave cycle."
)


# Function: _save_upload
def _save_upload(file: UploadFile, kind: str) -> str:
    ext = os.path.splitext(file.filename or "")[1] or ".xlsx"
    unique_name = f"{kind}_{uuid.uuid4().hex}{ext}"
    dest = os.path.join(UPLOAD_DIR, unique_name)
    with open(dest, "wb") as f:
        f.write(file.file.read())
    return dest


# Function: upload_scope_dataset
@router.post("/wave/datasets/scope", response_model=DatasetOut)
def upload_scope_dataset(file: UploadFile = File(...), db: Session = Depends(get_db), _=Depends(get_current_user)):
    dest = _save_upload(file, "scope")
    try:
        rows = parse_scope_file(dest)
    except Exception as exc:
        os.remove(dest)
        raise HTTPException(status_code=422, detail=f"File does not match the Application Scope List template: {exc}")

    dataset = UploadedDataset(kind="scope", filename=file.filename, file_path=dest, row_count=len(rows))
    db.add(dataset)
    db.flush()
    for i, r in enumerate(rows):
        db.add(DatasetRow(dataset_id=dataset.id, source_row_index=i, data=json.dumps(r)))
    db.commit()
    db.refresh(dataset)
    return dataset


# Function: upload_categorization_dataset
@router.post("/wave/datasets/categorization", response_model=DatasetOut)
def upload_categorization_dataset(file: UploadFile = File(...), db: Session = Depends(get_db), _=Depends(get_current_user)):
    dest = _save_upload(file, "categorization")
    try:
        rows = parse_categorization_file(dest)
    except Exception as exc:
        os.remove(dest)
        raise HTTPException(status_code=422, detail=f"File does not match the Business Categorization template: {exc}")

    dataset = UploadedDataset(kind="categorization", filename=file.filename, file_path=dest, row_count=len(rows))
    db.add(dataset)
    db.flush()
    for r in rows:
        db.add(DatasetRow(dataset_id=dataset.id, source_row_index=r["source_row_index"], data=json.dumps(r)))
    db.commit()
    db.refresh(dataset)
    return dataset


# Function: list_datasets
@router.get("/wave/datasets", response_model=list[DatasetOut])
def list_datasets(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(UploadedDataset).order_by(UploadedDataset.uploaded_at.desc()).all()


# Function: delete_dataset
@router.delete("/wave/datasets/{dataset_id}", status_code=204)
def delete_dataset(dataset_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    dataset = db.query(UploadedDataset).get(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found.")
    if os.path.exists(dataset.file_path):
        os.remove(dataset.file_path)
    db.query(DatasetRow).filter_by(dataset_id=dataset_id).delete()
    db.delete(dataset)
    db.commit()


# Function: preview_analysis_categories
@router.get("/wave/analysis/preview-categories", response_model=list[CategoryPreviewOut])
def preview_analysis_categories(
    scope_dataset_id: int, categorization_dataset_id: int,
    db: Session = Depends(get_db), _=Depends(get_current_user),
):
    return preview_categories(db, scope_dataset_id, categorization_dataset_id)


# Function: submit_analysis
@router.post("/wave/analysis", response_model=AnalysisSubmitResponse)
def submit_analysis(req: AnalysisSubmitRequest, db: Session = Depends(get_db), _=Depends(get_current_user)):
    try:
        job, unmatched = create_job(
            db, req.scope_dataset_id, req.categorization_dataset_id, req.categories, req.user_guidance,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    thread = threading.Thread(target=run_analysis_job, args=(job.id,), daemon=True)
    thread.start()

    return AnalysisSubmitResponse(
        job_id=job.id, status=job.status, total_categories=job.total_categories, unmatched_categories=unmatched,
    )


# Function: get_job_status
@router.get("/wave/analysis/{job_id}", response_model=JobStatusOut)
def get_job_status(job_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    job = db.query(AnalysisJob).get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    summaries = db.query(WaveCategorySummary).filter_by(job_id=job_id).all()
    return JobStatusOut(
        job_id=job.id,
        status=job.status,
        total_categories=job.total_categories,
        completed_categories=job.completed_categories,
        llm_model=job.llm_model,
        error_message=job.error_message,
        categories=[
            CategoryStatusOut(category=s.category, status=s.status, current_step=s.current_step, error_message=s.error_message)
            for s in summaries
        ],
    )


# Function: _category_rollup
def _category_rollup(db: Session, job_id: int, category: str) -> dict:
    apps_q = db.query(WaveApp).filter_by(job_id=job_id, category=category)
    total = apps_q.count()
    dq = apps_q.filter(WaveApp.data_quality_flag.is_(True)).count()
    func_only = apps_q.filter(WaveApp.migration_type == "Functional Migration Only").count()
    full_con = apps_q.filter(WaveApp.migration_type == "Full Consolidation").count()
    data_only = apps_q.filter(WaveApp.migration_type == "Data Migration Only").count()
    tbd = apps_q.filter(WaveApp.migration_type == "TBD (data gap)").count()
    wave_count = db.query(WaveApp.wave).filter_by(job_id=job_id, category=category).distinct().count()
    harmonization_count = apps_q.filter(WaveApp.disposition == "Harmonization").count()
    modernization_count = apps_q.filter(WaveApp.disposition == "Modernization").count()
    return {
        "actual_app_count": total, "data_quality_issues": dq,
        "functional_migration_only": func_only, "full_consolidation": full_con,
        "data_migration_only": data_only, "tbd_count": tbd, "wave_count": wave_count,
        "harmonization_count": harmonization_count, "modernization_count": modernization_count,
    }


# Function: list_categories
@router.get("/wave/analysis/{job_id}/categories", response_model=list[CategorySummaryOut])
def list_categories(job_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    summaries = db.query(WaveCategorySummary).filter_by(job_id=job_id).order_by(WaveCategorySummary.category).all()
    out = []
    for s in summaries:
        rollup = _category_rollup(db, job_id, s.category)
        out.append(CategorySummaryOut(
            category=s.category, status=s.status, error_message=s.error_message,
            description=s.description, estimated_app_count=s.estimated_app_count,
            timeline_start=s.timeline_start, timeline_end=s.timeline_end,
            classification_logic_notes=s.classification_logic_notes,
            **rollup,
        ))
    return out


# Function: get_waves
@router.get("/wave/analysis/{job_id}/categories/{category:path}/waves", response_model=list[WaveSummaryOut])
def get_waves(job_id: int, category: str, db: Session = Depends(get_db), _=Depends(get_current_user)):
    apps = db.query(WaveApp).filter_by(job_id=job_id, category=category).all()
    if not apps:
        return []

    by_wave: dict[str, list[WaveApp]] = {}
    for a in apps:
        by_wave.setdefault(a.wave, []).append(a)

    # Function: wave_sort_key
    def wave_sort_key(w: str):
        import re
        m = re.search(r"(\d+)", w)
        return int(m.group(1)) if m else 999

    out = []
    for wave in sorted(by_wave.keys(), key=wave_sort_key):
        wave_apps = by_wave[wave]
        depts = {}
        for a in wave_apps:
            depts[a.dept] = depts.get(a.dept, 0) + 1
        primary_depts = ", ".join(f"{d} ({c})" for d, c in sorted(depts.items(), key=lambda kv: -kv[1])[:3])
        # Prefer a non-remediation-rejoin app's rationale as the wave-level summary — it
        # describes the wave's actual formation logic (pilot/solo-dept/bundle), whereas a
        # rejoin's rationale is a one-off exception that misrepresents the wave as a whole
        # when most of its apps aren't rejoins.
        sequencing_rationale = next(
            (a.wave_assignment_rationale for a in wave_apps if a.wave_assignment_rationale and not a.rejoins_wave),
            next((a.wave_assignment_rationale for a in wave_apps if a.wave_assignment_rationale), ""),
        )

        out.append(WaveSummaryOut(
            wave=wave,
            app_count=len(wave_apps),
            data_quality_flags=sum(1 for a in wave_apps if a.data_quality_flag),
            functional_migration_only=sum(1 for a in wave_apps if a.migration_type == "Functional Migration Only"),
            full_consolidation=sum(1 for a in wave_apps if a.migration_type == "Full Consolidation"),
            data_migration_only=sum(1 for a in wave_apps if a.migration_type == "Data Migration Only"),
            tbd_count=sum(1 for a in wave_apps if a.migration_type == "TBD (data gap)"),
            harmonization_count=sum(1 for a in wave_apps if a.disposition == "Harmonization"),
            modernization_count=sum(1 for a in wave_apps if a.disposition == "Modernization"),
            stream2_assessment=wave_apps[0].stream2_assessment,
            stream3_execution=wave_apps[0].stream3_execution,
            ams_transition_start=wave_apps[0].ams_transition_start,
            primary_departments=primary_depts,
            sequencing_rationale=sequencing_rationale,
        ))
    return out


# Function: get_wave_apps
@router.get("/wave/analysis/{job_id}/categories/{category:path}/waves/{wave}/apps", response_model=list[WaveAppOut])
def get_wave_apps(job_id: int, category: str, wave: str, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(WaveApp).filter_by(job_id=job_id, category=category, wave=wave).order_by(WaveApp.app_id).all()


# Function: get_remediation
@router.get("/wave/analysis/{job_id}/categories/{category:path}/remediation")
def get_remediation(job_id: int, category: str, db: Session = Depends(get_db), _=Depends(get_current_user)):
    apps = db.query(WaveApp).filter_by(job_id=job_id, category=category, data_quality_flag=True).order_by(WaveApp.app_id).all()
    return {
        "process_notes": REMEDIATION_PROCESS_TEXT,
        "apps": [WaveAppOut.model_validate(a).model_dump() for a in apps],
    }


# Function: get_gantt
@router.get("/wave/analysis/{job_id}/categories/{category:path}/gantt", response_model=list[GanttRowOut])
def get_gantt(job_id: int, category: str, db: Session = Depends(get_db), _=Depends(get_current_user)):
    waves = get_waves(job_id, category, db)
    out = []
    phase_labels = ["Assess.", "Migr.", "Test/CO", "AMS", "Steady"]
    for w in waves:
        out.append(GanttRowOut(
            label=f"{w.wave} - {w.primary_departments}, {w.app_count} apps",
            app_count=w.app_count,
            start_quarter=w.stream2_assessment or "",
            phases=phase_labels,
        ))
    return out


# Function: get_category
@router.get("/wave/analysis/{job_id}/categories/{category:path}", response_model=CategorySummaryOut)
def get_category(job_id: int, category: str, db: Session = Depends(get_db), _=Depends(get_current_user)):
    s = db.query(WaveCategorySummary).filter_by(job_id=job_id, category=category).first()
    if not s:
        raise HTTPException(status_code=404, detail="Category not found in this job.")
    rollup = _category_rollup(db, job_id, category)
    return CategorySummaryOut(
        category=s.category, status=s.status, error_message=s.error_message,
        description=s.description, estimated_app_count=s.estimated_app_count,
        timeline_start=s.timeline_start, timeline_end=s.timeline_end,
        classification_logic_notes=s.classification_logic_notes,
        **rollup,
    )


# Function: export_category
@router.get("/wave/analysis/{job_id}/export")
def export_category(job_id: int, category: str, db: Session = Depends(get_db), _=Depends(get_current_user)):
    from wave_export import build_workbook
    from fastapi.responses import StreamingResponse

    job = db.query(AnalysisJob).get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    summary = db.query(WaveCategorySummary).filter_by(job_id=job_id, category=category).first()
    if not summary:
        raise HTTPException(status_code=404, detail="Category not found in this job.")

    buffer = build_workbook(db, job_id, category)
    safe_name = "".join(c if c.isalnum() or c in " -_" else "_" for c in category)[:60]
    filename = f"WavePlan_{safe_name}_{datetime.now(timezone.utc).strftime('%Y%m%d')}.xlsx"
    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# Function: delete_job
@router.delete("/wave/analysis/{job_id}", status_code=204)
def delete_job(job_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    job = db.query(AnalysisJob).get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    db.query(WaveApp).filter_by(job_id=job_id).delete()
    db.query(WaveCategorySummary).filter_by(job_id=job_id).delete()
    db.delete(job)
    db.commit()
