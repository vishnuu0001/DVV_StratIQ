# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Harmonization Wave Plan generation APIs (Ollama-assisted).
# Date: 2026-07-20
# ---------------------------------------------------------------------------
"""Harmonization Wave Plan generation APIs (Ollama-assisted)."""
from flask import Blueprint, current_app, jsonify, request
from app import db
from app.services.wave_plan_service import generate_wave_plan, latest_wave_plan, list_topics

wave_plan_bp = Blueprint("wave_plan", __name__, url_prefix="/api/wave-plan")


# Function: topics
@wave_plan_bp.get("/topics")
def topics():
    return jsonify({"topics": list_topics()})


# Function: generate
@wave_plan_bp.post("/generate")
def generate():
    body = request.get_json(silent=True) or {}
    topic = str(body.get("topic") or "").strip()
    complexity_scope = body.get("complexity_scope")
    parallel_streams = body.get("parallel_streams")
    program_start = body.get("program_start")
    try:
        plan = generate_wave_plan(
            topic=topic, complexity_scope=complexity_scope,
            parallel_streams=parallel_streams or 3, program_start=program_start,
        )
        return jsonify(plan), 201
    except ValueError as exc:
        db.session.rollback()
        return jsonify({"error": str(exc)}), 422
    except Exception as exc:
        db.session.rollback()
        current_app.logger.exception("Wave plan generation failed")
        return jsonify({"error": f"Wave plan generation failed: {exc}"}), 500


# Function: latest
@wave_plan_bp.get("/latest")
def latest():
    topic = request.args.get("topic")
    plan = latest_wave_plan(topic)
    if not plan:
        return jsonify(None)
    return jsonify(plan.to_dict())
