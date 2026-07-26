# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Ollama narrative generation for the financial gap-analysis dashboard.
# Date: 2026-07-15
# ---------------------------------------------------------------------------
"""Ollama narrative generation for the financial gap-analysis dashboard.

Follows wave_llm_service.py's design philosophy exactly: Ollama only narrates
numbers that were already computed deterministically in Python
(financial_summary_service.py) — it never computes or restates its own
arithmetic. Letting an LLM compute sums/percentages has empirically produced
hallucinated output in this module's other LLM feature (Wave Planning); the
same risk applies here, so the prompt instructs the model to quote the given
figures verbatim.

Single, unbatched call (the whole summary is already small — nothing to
chunk). Run as a background job + poll, not synchronously: OLLAMA_TIMEOUT_SECONDS
is already configured at 120s in this module for exactly this class of call on
shared/constrained GPU hardware, and blocking a request for up to 2 minutes
risks proxy/browser timeouts — mirrors wave_analysis.py's
threading.Thread(..., daemon=True) + wave_job_runner.py's "open a new DB
session per thread, never share the request-scoped session" rule."""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone

from database import SessionLocal
from config import OLLAMA_MODEL
from models import FinancialNarrativeJob
from ollama_client import call_ollama, extract_json_object, resolve_ollama_model

logger = logging.getLogger(__name__)

_NARRATIVE_PROMPT = """You are a sales operations analyst reviewing a manufacturing CTO pipeline's FY27 plan attainment.

FINANCIAL SUMMARY (JSON — every number is already computed; quote these figures VERBATIM,
do NOT recompute, re-sum, or restate a different total or percentage anywhere in your output):
{summary_json}
{user_guidance_block}
INSTRUCTIONS:
- Return ONLY valid JSON, no markdown fences, no explanation outside the JSON.
- The ONLY percentage you may state is the given "attainment_pct" figure, quoted verbatim. Do NOT compute
  ANY other percentage, ratio, or share (e.g. "X% of the gap", "Y% of opportunities") — a prior run computed
  such figures itself and got them wrong every time. Express every other comparison in dollar terms only
  (e.g. "the Americas region accounts for $2.33M of the $4.005M gap"), never as a derived percentage.
- Write one "narrative" STRING (not an object), 4-7 sentences, covering:
  (a) the Target vs Actual attainment (quoting attainment_pct exactly) and the size of the Gap, quoting the given dollar figures exactly;
  (b) which region(s)/stage(s) are driving the gap, using the by_region/by_stage breakdowns given, in dollar terms only;
  (c) any notable data-quality gaps worth flagging — if data_quality.blank_stage_count or any other
      data_quality count is nonzero, you MUST mention it explicitly, naming the count;
  (d) a concrete recommendation of which open opportunities (from gap_closure_plan) should be
      prioritized to close the gap, naming 2-4 specific deals by opportunity_name and customer_group.
- Never invent a number, opportunity, customer, or region that is not present in the JSON above.
- JSON schema: {{"narrative": "a single plain-text string, not nested JSON"}}
"""

_USER_GUIDANCE_TEMPLATE = """
ADDITIONAL USER GUIDANCE FOR THIS ANALYSIS RUN (advisory only — can shape emphasis/framing, but can
NEVER change the underlying numbers or invent evidence not present in the summary above):
"{guidance}"
"""


# Function: _user_guidance_block
def _user_guidance_block(user_guidance: str | None) -> str:
    if not user_guidance or not user_guidance.strip():
        return ""
    return _USER_GUIDANCE_TEMPLATE.format(guidance=user_guidance.strip()[:1500])


# Function: generate_financial_narrative
def generate_financial_narrative(summary: dict, model: str, user_guidance: str | None = None) -> str:
    prompt = _NARRATIVE_PROMPT.format(
        summary_json=json.dumps(summary),
        user_guidance_block=_user_guidance_block(user_guidance),
    )
    text = call_ollama(prompt, model, num_predict=900)
    parsed = extract_json_object(text)
    narrative = parsed.get("narrative")
    if isinstance(narrative, dict):
        return " ".join(f"{k}: {v}" for k, v in narrative.items())[:3000]
    if narrative:
        return str(narrative)[:3000]
    raise ValueError("Ollama response did not contain a 'narrative' field")


# Function: run_financial_narrative_job
def run_financial_narrative_job(job_id: int, user_guidance: str | None = None) -> None:
    """Background-thread entry point — opens its own DB session, never shares
    the request-scoped session across threads (same rule as wave_job_runner.py)."""
    from financial_summary_service import compute_financial_summary

    db = SessionLocal()
    try:
        job = db.query(FinancialNarrativeJob).get(job_id)
        if not job:
            return

        job.status = "running"
        db.commit()

        try:
            summary = compute_financial_summary(db)
            job.summary_snapshot = json.dumps(summary)
            db.commit()

            model = resolve_ollama_model(OLLAMA_MODEL)
            job.llm_model = model
            db.commit()

            narrative = generate_financial_narrative(summary, model, user_guidance=user_guidance)
            job.narrative_text = narrative
            job.status = "done"
            job.completed_at = datetime.now(timezone.utc)
            db.commit()
        except Exception as exc:
            db.rollback()
            job.status = "failed"
            job.error_message = str(exc)[:1000]
            job.completed_at = datetime.now(timezone.utc)
            db.commit()
            logger.exception("Financial narrative job %d failed", job_id)

    except Exception:
        logger.exception("run_financial_narrative_job %d crashed", job_id)
        try:
            job = db.query(FinancialNarrativeJob).get(job_id)
            if job:
                job.status = "failed"
                job.error_message = "Unexpected error — see server logs."
                job.completed_at = datetime.now(timezone.utc)
                db.commit()
        except Exception:
            pass
    finally:
        db.close()
