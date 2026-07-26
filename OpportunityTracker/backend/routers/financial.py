# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: OpportunityTracker — backend/routers (financial.py)
# Date: 2026-07-15
# ---------------------------------------------------------------------------
"""
Financial Dashboard Blueprint
Endpoints:
  GET  /api/financial-summary                      – Target/Actual/Gap, recomputed fresh every call
  POST /api/financial-summary/narrative             – start an Ollama gap-analysis narrative job
  GET  /api/financial-summary/narrative/{job_id}    – poll job status/result
"""
import threading

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from auth import get_current_user
from database import get_db
from financial_llm_service import run_financial_narrative_job
from financial_summary_service import compute_financial_summary
from models import FinancialNarrativeJob
from schemas import (
    FinancialSummaryOut,
    NarrativeJobOut,
    NarrativeStartRequest,
    NarrativeStartResponse,
)

router = APIRouter(tags=["financial"])


# Function: get_financial_summary
@router.get("/financial-summary", response_model=FinancialSummaryOut)
def get_financial_summary(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return compute_financial_summary(db)


# Function: start_financial_narrative
@router.post("/financial-summary/narrative", response_model=NarrativeStartResponse)
def start_financial_narrative(
    req: NarrativeStartRequest, db: Session = Depends(get_db), _=Depends(get_current_user),
):
    job = FinancialNarrativeJob(status="pending")
    db.add(job)
    db.commit()
    db.refresh(job)

    thread = threading.Thread(
        target=run_financial_narrative_job, args=(job.id, req.user_guidance), daemon=True,
    )
    thread.start()

    return NarrativeStartResponse(job_id=job.id, status=job.status)


# Function: get_financial_narrative_job
@router.get("/financial-summary/narrative/{job_id}", response_model=NarrativeJobOut)
def get_financial_narrative_job(job_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    job = db.query(FinancialNarrativeJob).get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Narrative job not found.")
    return NarrativeJobOut(
        job_id=job.id,
        status=job.status,
        llm_model=job.llm_model,
        narrative_text=job.narrative_text,
        error_message=job.error_message,
        created_at=job.created_at,
        completed_at=job.completed_at,
    )
