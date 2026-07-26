# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Harmonization Wave Delivery Schedule APIs — deterministic, always
#        recalculated fresh from current Wave Inputs on read.
# Date: 2026-07-20
# ---------------------------------------------------------------------------
"""Harmonization Wave Delivery Schedule APIs."""
from flask import Blueprint, current_app, jsonify, request, send_file
from app import db
from app.models.wave_schedule import WaveSchedule
from app.services.wave_schedule_export_service import build_wave_schedule_workbook
from app.services.wave_schedule_service import (
    get_wave_schedule_job, list_topics, recalculate_wave_schedule, start_wave_schedule_job,
)

wave_schedule_bp = Blueprint("wave_schedule", __name__, url_prefix="/api/wave-schedule")


# Function: topics
@wave_schedule_bp.get("/topics")
def topics():
    return jsonify({"topics": list_topics()})


# Function: dashboard
@wave_schedule_bp.get("")
def dashboard():
    """Always recomputes from the current Wave Inputs before returning —
    the dashboard can never show a schedule that has drifted from the data.

    Omit ``topic`` (the normal case — the dashboard has no topic switcher)
    to schedule every application across every topic together as one
    portfolio-wide programme."""
    topic = request.args.get("topic") or None
    program_start = request.args.get("program_start")
    complex_from_wave = request.args.get("complex_from_wave", type=int)
    very_complex_from_wave = request.args.get("very_complex_from_wave", type=int)
    decommission_offset_waves = request.args.get("decommission_offset_waves", type=int)
    try:
        kwargs = {"topic": topic, "program_start": program_start}
        if complex_from_wave:
            kwargs["complex_from_wave"] = complex_from_wave
        if very_complex_from_wave:
            kwargs["very_complex_from_wave"] = very_complex_from_wave
        if decommission_offset_waves is not None:
            kwargs["decommission_offset_waves"] = decommission_offset_waves
        schedule = recalculate_wave_schedule(**kwargs)
        return jsonify(schedule)
    except ValueError as exc:
        db.session.rollback()
        return jsonify({"error": str(exc)}), 422
    except Exception as exc:
        db.session.rollback()
        current_app.logger.exception("Wave schedule calculation failed")
        return jsonify({"error": f"Wave schedule calculation failed: {exc}"}), 500


# Function: predict
@wave_schedule_bp.post("/predict")
def predict():
    """Start an async "Predict Wave Planning" run — the batched Ollama
    review can take a while on this shared GPU, so this returns a job id
    immediately instead of blocking the request. Poll GET /predict/<job_id>."""
    body = request.get_json(silent=True) or {}
    topic = (body.get("topic") or None)
    kwargs = {}
    if body.get("program_start"):
        kwargs["program_start"] = body["program_start"]
    if body.get("complex_from_wave"):
        kwargs["complex_from_wave"] = int(body["complex_from_wave"])
    if body.get("very_complex_from_wave"):
        kwargs["very_complex_from_wave"] = int(body["very_complex_from_wave"])
    if body.get("decommission_offset_waves") is not None:
        kwargs["decommission_offset_waves"] = int(body["decommission_offset_waves"])
    try:
        job_id = start_wave_schedule_job(current_app._get_current_object(), topic=topic, **kwargs)
        return jsonify({"job_id": job_id}), 202
    except Exception as exc:
        db.session.rollback()
        current_app.logger.exception("Failed to start wave schedule job")
        return jsonify({"error": f"Failed to start prediction: {exc}"}), 500


# Function: predict_status
@wave_schedule_bp.get("/predict/<int:job_id>")
def predict_status(job_id):
    job = get_wave_schedule_job(job_id)
    if job is None:
        return jsonify({"error": "Job not found"}), 404
    return jsonify(job)


# Function: export
@wave_schedule_bp.get("/export/<int:schedule_id>")
def export(schedule_id):
    """Formatted .xlsx export of a calculated wave schedule — only ever
    called with a schedule_id that came from a *successfully completed*
    prediction, so no separate readiness check is needed here."""
    schedule = WaveSchedule.query.get(schedule_id)
    if schedule is None:
        return jsonify({"error": "Wave schedule not found"}), 404
    try:
        buffer = build_wave_schedule_workbook(schedule)
        topic_slug = "".join(c if c.isalnum() else "_" for c in (schedule.topic or "wave_schedule"))[:60]
        filename = f"Wave_Plan_{topic_slug}_{schedule.calculated_at.strftime('%Y%m%d')}.xlsx"
        return send_file(
            buffer, as_attachment=True, download_name=filename,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    except Exception as exc:
        current_app.logger.exception("Wave schedule export failed")
        return jsonify({"error": f"Export failed: {exc}"}), 500
