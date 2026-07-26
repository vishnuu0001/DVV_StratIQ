# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Feedback API — captures user ratings and comments on answers.
# Date: 2026-05-14
# ---------------------------------------------------------------------------
"""
Feedback API — captures user ratings and comments on answers.
Feedback is stored in a TinyDB JSON file and can be used to rank/improve results.
"""
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, HTTPException
from tinydb import TinyDB, Query

import backend.config as cfg
from backend.models.schemas import FeedbackRequest, FeedbackResponse

router = APIRouter(prefix="/api/feedback", tags=["Feedback"])
logger = logging.getLogger(__name__)

DB_PATH = Path(cfg.BASE_DIR) / "feedback_db.json"


# Function: _get_db
def _get_db() -> TinyDB:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return TinyDB(str(DB_PATH))


# Function: submit_feedback
@router.post("", response_model=FeedbackResponse)
async def submit_feedback(request: FeedbackRequest):
    """Save user feedback for a given answer."""
    feedback_id = str(uuid.uuid4())
    record = {
        "feedback_id": feedback_id,
        "session_id": request.session_id,
        "question": request.question,
        "answer": request.answer[:500],   # truncate for storage
        "rating": request.rating,
        "comment": request.comment or "",
        "sources": request.sources or [],
        "created_at": datetime.now(tz=timezone.utc).isoformat(),
    }
    db = _get_db()
    db.insert(record)
    logger.info("Feedback recorded: id=%s rating=%s", feedback_id, request.rating)
    return FeedbackResponse(feedback_id=feedback_id, message="Thank you for your feedback!")


# Function: get_all_feedback
@router.get("/all")
async def get_all_feedback(limit: int = 100):
    """Admin endpoint — retrieve all feedback records."""
    db = _get_db()
    records = db.all()
    # Sort by rating desc (best first)
    records.sort(key=lambda x: x.get("rating", 0), reverse=True)
    return {"feedback": records[:limit], "total": len(records)}


# Function: feedback_stats
@router.get("/stats")
async def feedback_stats():
    """Aggregate statistics — useful for ranking knowledge quality."""
    db = _get_db()
    all_records = db.all()
    if not all_records:
        return {"total": 0, "average_rating": None, "rating_distribution": {}}

    total = len(all_records)
    avg = sum(r.get("rating", 0) for r in all_records) / total
    dist: dict = {}
    for r in all_records:
        k = str(r.get("rating", "unknown"))
        dist[k] = dist.get(k, 0) + 1

    return {
        "total": total,
        "average_rating": round(avg, 2),
        "rating_distribution": dist,
    }
