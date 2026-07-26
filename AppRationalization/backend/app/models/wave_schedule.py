# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Relational storage for the deterministic Harmonization Wave
#        Delivery Schedule (WBS Gantt task list, wave summary, and per-app
#        wave assignment) calculated from Wave Inputs. Mirrors the structure
#        of the BASF_Harmonization_Wave_Gantt_Schedule.xlsx reference
#        workbook (Gantt_Schedule / Wave_Summary / Gantt_View sheets).
# Date: 2026-07-20
# ---------------------------------------------------------------------------
"""Relational storage for the deterministic Harmonization Wave Schedule."""
from datetime import datetime
from app import db


class WaveScheduleJob(db.Model):
    """Tracks one async "Predict Wave Planning" run — the Ollama review is
    batched (small, independently-retryable calls) and executed in a
    background thread, since a single request-scoped HTTP call can't reliably
    bound how long a shared, resource-constrained GPU takes to respond."""
    __tablename__ = "wave_schedule_jobs"
    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String(500))            # raw request topic — may be None (= all topics)
    status = db.Column(db.String(16), nullable=False, default="pending")  # pending|running|done|failed
    batches_total = db.Column(db.Integer, default=0)
    batches_done = db.Column(db.Integer, default=0)
    batches_llm_ok = db.Column(db.Integer, default=0)   # how many batches got a real Ollama response
    schedule_id = db.Column(db.Integer, db.ForeignKey("wave_schedules.id", ondelete="SET NULL"))
    error = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Function: to_dict
    def to_dict(self):
        return {
            "id": self.id, "topic": self.topic, "status": self.status,
            "batches_total": self.batches_total, "batches_done": self.batches_done,
            "batches_llm_ok": self.batches_llm_ok, "schedule_id": self.schedule_id,
            "error": self.error,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class WaveSchedule(db.Model):
    """One row per topic — always holds the latest calculated schedule."""
    __tablename__ = "wave_schedules"
    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String(500), nullable=False, unique=True, index=True)
    program_start = db.Column(db.Date, nullable=False)
    sprint_weeks = db.Column(db.Integer, nullable=False, default=3)
    wave_cadence_weeks = db.Column(db.Integer, nullable=False, default=13)
    max_waves = db.Column(db.Integer, nullable=False, default=8)
    complex_from_wave = db.Column(db.Integer, nullable=False, default=3)
    very_complex_from_wave = db.Column(db.Integer, nullable=False, default=6)
    source_import_id = db.Column(db.Integer)
    wave_count = db.Column(db.Integer, nullable=False, default=0)
    app_count = db.Column(db.Integer, nullable=False, default=0)
    deferred_count = db.Column(db.Integer, nullable=False, default=0)
    total_effort_hours = db.Column(db.Numeric(14, 2), nullable=False, default=0)
    program_end = db.Column(db.Date)
    calculated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    # Wave Planning always attempts an Ollama review of the rule-based
    # scaffold (never purely deterministic) — these record what happened on
    # this specific calculation, since the LLM's involvement (and therefore
    # the resulting wave assignment) can genuinely differ run to run.
    model_used = db.Column(db.String(128))
    llm_available = db.Column(db.Boolean, default=False)
    summary = db.Column(db.Text)

    waves = db.relationship("WaveScheduleWave", backref="schedule", cascade="all, delete-orphan",
                             order_by="WaveScheduleWave.wave_number")
    tasks = db.relationship("WaveScheduleTask", backref="schedule", cascade="all, delete-orphan",
                             order_by="WaveScheduleTask.wave_number, WaveScheduleTask.sequence")
    apps = db.relationship("WaveScheduleApp", backref="schedule", cascade="all, delete-orphan",
                            order_by="WaveScheduleApp.wave_number, WaveScheduleApp.app_id")

    # Function: to_dict
    def to_dict(self, include_detail=True):
        result = {
            "id": self.id, "topic": self.topic,
            "program_start": self.program_start.isoformat() if self.program_start else None,
            "program_end": self.program_end.isoformat() if self.program_end else None,
            "sprint_weeks": self.sprint_weeks, "wave_cadence_weeks": self.wave_cadence_weeks,
            "max_waves": self.max_waves, "complex_from_wave": self.complex_from_wave,
            "very_complex_from_wave": self.very_complex_from_wave,
            "wave_count": self.wave_count, "app_count": self.app_count,
            "deferred_count": self.deferred_count,
            "total_effort_hours": float(self.total_effort_hours or 0),
            "calculated_at": self.calculated_at.isoformat() if self.calculated_at else None,
            "model_used": self.model_used, "llm_available": bool(self.llm_available),
            "summary": self.summary,
        }
        if include_detail:
            result["waves"] = [w.to_dict() for w in self.waves]
            result["tasks"] = [t.to_dict() for t in self.tasks]
            result["apps"] = [a.to_dict() for a in self.apps]
        return result


class WaveScheduleWave(db.Model):
    """One row per wave — mirrors the Wave_Summary sheet."""
    __tablename__ = "wave_schedule_waves"
    id = db.Column(db.Integer, primary_key=True)
    schedule_id = db.Column(db.Integer, db.ForeignKey("wave_schedules.id", ondelete="CASCADE"), nullable=False, index=True)
    wave_number = db.Column(db.Integer, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    cutover_date = db.Column(db.Date, nullable=False)
    stabilisation_end_date = db.Column(db.Date, nullable=False)
    gate_review_date = db.Column(db.Date, nullable=False)
    application_count = db.Column(db.Integer, nullable=False, default=0)
    effort_hours = db.Column(db.Numeric(14, 2), nullable=False, default=0)
    quick_win_count = db.Column(db.Integer, nullable=False, default=0)
    topic_count = db.Column(db.Integer, nullable=False, default=0)
    simple_count = db.Column(db.Integer, nullable=False, default=0)
    medium_count = db.Column(db.Integer, nullable=False, default=0)
    complex_count = db.Column(db.Integer, nullable=False, default=0)
    very_complex_count = db.Column(db.Integer, nullable=False, default=0)
    permitted_complexity = db.Column(db.String(100))
    theme = db.Column(db.String(200))    # Ollama-generated theme for this wave, when available
    rationale = db.Column(db.Text)       # Ollama-generated rationale for this wave, when available

    # Function: to_dict
    def to_dict(self):
        return {
            "wave_number": self.wave_number,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "cutover_date": self.cutover_date.isoformat() if self.cutover_date else None,
            "stabilisation_end_date": self.stabilisation_end_date.isoformat() if self.stabilisation_end_date else None,
            "gate_review_date": self.gate_review_date.isoformat() if self.gate_review_date else None,
            "application_count": self.application_count, "effort_hours": float(self.effort_hours or 0),
            "quick_win_count": self.quick_win_count, "topic_count": self.topic_count,
            "simple_count": self.simple_count, "medium_count": self.medium_count,
            "complex_count": self.complex_count, "very_complex_count": self.very_complex_count,
            "permitted_complexity": self.permitted_complexity,
            "theme": self.theme, "rationale": self.rationale,
        }


class WaveScheduleTask(db.Model):
    """One row per WBS task — mirrors the Gantt_Schedule sheet's task list."""
    __tablename__ = "wave_schedule_tasks"
    id = db.Column(db.Integer, primary_key=True)
    schedule_id = db.Column(db.Integer, db.ForeignKey("wave_schedules.id", ondelete="CASCADE"), nullable=False, index=True)
    wave_number = db.Column(db.Integer, nullable=False)
    wbs_code = db.Column(db.String(20))
    sequence = db.Column(db.Integer, default=0)
    task_name = db.Column(db.String(200), nullable=False)
    task_type = db.Column(db.String(30), nullable=False)  # initiation|assessment|migration|testing|cutover|stabilisation|gate_review
    level = db.Column(db.Integer, nullable=False, default=3)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    duration_days = db.Column(db.Integer, nullable=False, default=0)
    is_milestone = db.Column(db.Boolean, nullable=False, default=False)
    predecessor_wbs = db.Column(db.String(20))
    applications = db.Column(db.Integer)
    effort_hours = db.Column(db.Numeric(14, 2))

    # Function: to_dict
    def to_dict(self):
        return {
            "wave_number": self.wave_number, "wbs_code": self.wbs_code, "sequence": self.sequence,
            "task_name": self.task_name, "task_type": self.task_type, "level": self.level,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "duration_days": self.duration_days, "is_milestone": bool(self.is_milestone),
            "predecessor_wbs": self.predecessor_wbs,
            "applications": self.applications,
            "effort_hours": float(self.effort_hours) if self.effort_hours is not None else None,
        }


class WaveScheduleApp(db.Model):
    """One row per scheduled application — the per-app wave assignment detail."""
    __tablename__ = "wave_schedule_apps"
    id = db.Column(db.Integer, primary_key=True)
    schedule_id = db.Column(db.Integer, db.ForeignKey("wave_schedules.id", ondelete="CASCADE"), nullable=False, index=True)
    wave_number = db.Column(db.Integer)  # NULL when deferred (didn't fit within max_waves)
    app_id = db.Column(db.String(64), nullable=False)
    application_name = db.Column(db.String(500))
    topic = db.Column(db.String(500))
    complexity = db.Column(db.String(50))
    complexity_tier = db.Column(db.String(20))  # normalized: simple|medium|complex|very_complex
    tshirt_size = db.Column(db.String(16))
    migration_type = db.Column(db.String(100))
    quick_win = db.Column(db.Boolean, default=False)
    effort_hours = db.Column(db.Numeric(14, 2))
    dependencies = db.Column(db.Text)
    deferred_reason = db.Column(db.String(200))
    rationale = db.Column(db.Text)       # why this app is in this wave — Ollama's, or a heuristic fallback
    source = db.Column(db.String(16), default="heuristic")  # "heuristic" | "llm" — did Ollama move this app?

    # Per-app delivery pipeline position within its wave — apps are round-robin
    # assigned into parallel delivery streams/lanes; a lane's Nth app is
    # staggered N sprints into that lane's pipeline (Assessment=N,
    # Migration=N+1..N+2, QA/UAT=N+3), reflecting limited concurrent delivery
    # capacity within a single wave rather than every app starting together.
    stream = db.Column(db.Integer)
    assessment_sprint = db.Column(db.Integer)
    migration_sprint_start = db.Column(db.Integer)
    migration_sprint_end = db.Column(db.Integer)
    qa_uat_sprint = db.Column(db.Integer)
    # Go-Live/Stabilization/Decommissioning "Program Increment" labels — PI is
    # simply the wave number; decommissioning defaults to N waves after
    # go-live (configurable), since neither concept exists in the underlying
    # wave-sequencing rules and this is a placeholder convention.
    go_live_pi = db.Column(db.String(20))
    stabilization_pi = db.Column(db.String(40))
    decommissioning_pi = db.Column(db.String(20))

    # Function: to_dict
    def to_dict(self):
        return {
            "wave_number": self.wave_number, "app_id": self.app_id,
            "application_name": self.application_name, "topic": self.topic,
            "complexity": self.complexity, "complexity_tier": self.complexity_tier,
            "tshirt_size": self.tshirt_size, "migration_type": self.migration_type,
            "quick_win": bool(self.quick_win),
            "effort_hours": float(self.effort_hours) if self.effort_hours is not None else None,
            "dependencies": self.dependencies, "deferred_reason": self.deferred_reason,
            "rationale": self.rationale, "source": self.source,
            "stream": self.stream, "assessment_sprint": self.assessment_sprint,
            "migration_sprint_start": self.migration_sprint_start,
            "migration_sprint_end": self.migration_sprint_end, "qa_uat_sprint": self.qa_uat_sprint,
            "go_live_pi": self.go_live_pi, "stabilization_pi": self.stabilization_pi,
            "decommissioning_pi": self.decommissioning_pi,
        }
