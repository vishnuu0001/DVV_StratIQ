# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Relational storage for AI-generated Harmonization wave plans.
# Date: 2026-07-20
# ---------------------------------------------------------------------------
"""Relational storage for AI-generated Harmonization wave plans."""
from datetime import datetime
from app import db


class WavePlan(db.Model):
    __tablename__ = "wave_plans"
    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String(500), nullable=False, index=True)
    complexity_scope = db.Column(db.String(100), nullable=False, default="Low,Medium")
    sprint_weeks = db.Column(db.Integer, nullable=False, default=3)
    cutover_frequency_months = db.Column(db.Integer, nullable=False, default=3)
    parallel_streams = db.Column(db.Integer, nullable=False, default=3)
    program_start = db.Column(db.Date, nullable=False)
    program_end = db.Column(db.Date, nullable=False)
    wave_count = db.Column(db.Integer, nullable=False, default=0)
    app_count = db.Column(db.Integer, nullable=False, default=0)
    deferred_high_complexity_count = db.Column(db.Integer, nullable=False, default=0)
    unscheduled_count = db.Column(db.Integer, nullable=False, default=0)
    model_used = db.Column(db.String(128))
    llm_available = db.Column(db.Boolean, default=False)
    summary = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    entries = db.relationship(
        "WavePlanEntry", backref="plan", cascade="all, delete-orphan",
        order_by="WavePlanEntry.wave_number, WavePlanEntry.sequence",
    )

    # Function: to_dict
    def to_dict(self, include_entries=True):
        result = {
            "id": self.id, "topic": self.topic,
            "complexity_scope": (self.complexity_scope or "").split(","),
            "sprint_weeks": self.sprint_weeks,
            "cutover_frequency_months": self.cutover_frequency_months,
            "parallel_streams": self.parallel_streams,
            "program_start": self.program_start.isoformat() if self.program_start else None,
            "program_end": self.program_end.isoformat() if self.program_end else None,
            "wave_count": self.wave_count, "app_count": self.app_count,
            "deferred_high_complexity_count": self.deferred_high_complexity_count,
            "unscheduled_count": self.unscheduled_count,
            "model_used": self.model_used, "llm_available": self.llm_available,
            "summary": self.summary,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
        if include_entries:
            waves = {}
            for entry in self.entries:
                waves.setdefault(entry.wave_number, []).append(entry.to_dict())
            result["waves"] = [
                {
                    "wave_number": wave_number,
                    "wave_name": items[0]["wave_name"],
                    "start_date": min(i["sprint_start"] for i in items if i["sprint_start"]) if any(i["sprint_start"] for i in items) else None,
                    "end_date": max(i["sprint_end"] for i in items if i["sprint_end"]) if any(i["sprint_end"] for i in items) else None,
                    "cutover_date": items[0]["cutover_date"],
                    "apps": items,
                }
                for wave_number, items in sorted(waves.items())
            ]
        return result


class WavePlanEntry(db.Model):
    __tablename__ = "wave_plan_entries"
    id = db.Column(db.Integer, primary_key=True)
    plan_id = db.Column(db.Integer, db.ForeignKey("wave_plans.id", ondelete="CASCADE"), nullable=False, index=True)
    wave_number = db.Column(db.Integer, nullable=False)
    wave_name = db.Column(db.String(100))
    sequence = db.Column(db.Integer, default=0)
    stream = db.Column(db.Integer, default=1)
    app_id = db.Column(db.String(64), nullable=False)
    application_name = db.Column(db.String(500))
    tshirt_size = db.Column(db.String(16))
    complexity = db.Column(db.String(50))
    migration_type = db.Column(db.String(100))
    quick_win = db.Column(db.Boolean, default=False)
    change_impact = db.Column(db.String(50))
    risk = db.Column(db.String(50))
    sprint_estimate = db.Column(db.Integer)
    dependencies = db.Column(db.Text)
    sprint_start = db.Column(db.Date)
    sprint_end = db.Column(db.Date)
    cutover_date = db.Column(db.Date)
    rationale = db.Column(db.Text)
    source = db.Column(db.String(16), default="heuristic")

    # Function: to_dict
    def to_dict(self):
        return {
            "id": self.id, "wave_number": self.wave_number, "wave_name": self.wave_name,
            "sequence": self.sequence, "stream": self.stream,
            "app_id": self.app_id, "application_name": self.application_name,
            "tshirt_size": self.tshirt_size, "complexity": self.complexity,
            "migration_type": self.migration_type, "quick_win": bool(self.quick_win),
            "change_impact": self.change_impact, "risk": self.risk,
            "sprint_estimate": self.sprint_estimate, "dependencies": self.dependencies,
            "sprint_start": self.sprint_start.isoformat() if self.sprint_start else None,
            "sprint_end": self.sprint_end.isoformat() if self.sprint_end else None,
            "cutover_date": self.cutover_date.isoformat() if self.cutover_date else None,
            "rationale": self.rationale, "source": self.source,
        }
