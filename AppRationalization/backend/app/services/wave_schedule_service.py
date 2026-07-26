# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Harmonization Wave Delivery Schedule calculator. A deterministic,
#        rule-based scaffold (matching the Mapping_Logic sheet of
#        BASF_Harmonization_Wave_Gantt_Schedule.xlsx: a fixed 7-stage wave
#        shape on a 3-week-sprint grid, a 13-week wave cadence, a complexity
#        ramp, quick wins pulled earliest, dependency ordering) is always
#        reviewed by Ollama (qwen3.5:9b) before being persisted — the rules
#        supply the scaffold and the safety net (every LLM suggestion is
#        validated before being applied), but the review step is mandatory,
#        so the result is never purely deterministic: identical Wave Inputs
#        can legitimately produce a different wave assignment run to run.
# Date: 2026-07-20
# ---------------------------------------------------------------------------
"""Harmonization Wave Delivery Schedule calculator — rule-based scaffold, always reviewed by Ollama."""
import logging
import math
import threading
from datetime import date, timedelta
from typing import Any, Dict, List, Optional

from app import db
from app.models.technical_assessment import WaveInput
from app.models.wave_schedule import WaveSchedule, WaveScheduleWave, WaveScheduleTask, WaveScheduleApp, WaveScheduleJob
from app.services.ollama_service import OllamaService
from app.services.technical_assessment_service import latest_import

logger = logging.getLogger(__name__)

SPRINT_WEEKS = 3
WAVE_CADENCE_WEEKS = 13          # wave N+1 starts 13 weeks after wave N
MAX_PROGRAM_MONTHS = 24
MIN_PROGRAM_MONTHS = 3
MAX_WAVES = MAX_PROGRAM_MONTHS // 3      # 8 — 13wk cadence ~= 3 months/wave
DEFAULT_COMPLEX_FROM_WAVE = 3
DEFAULT_VERY_COMPLEX_FROM_WAVE = 6

# Wave Planning always asks this specific model to review the rule-based
# scaffold — never falls back to the generic ranked-model list, so it's
# clear which model actually shaped a given run.
WAVE_PLANNING_MODEL = "qwen3.5:9b"
WAVE_PLANNING_TEMPERATURE = 0.8   # meaningfully above the app's usual 0.2 — real run-to-run variation, by design
# qwen3.5:9b is a "thinking" model, and on this host's shared 8GB vGPU the
# model only partially fits in VRAM (~4.8GB of its 6.6GB) — the rest runs on
# CPU. Measured directly: `think` left at its default (on) reliably failed —
# a 500 from Ollama on one run, 90-120s+ hangs with no response on others.
# `think=False` is not a style choice, it's the only configuration that
# returned successfully in testing on this hardware.
WAVE_PLANNING_THINK = False
# Even with thinking off, a single request covering the whole ~565-app
# portfolio (or even just 9 apps, once) failed to complete within 180s on
# this shared, partially-CPU-offloaded GPU — so the review is BATCHED: many
# small, independently-retryable Ollama calls run in a background thread
# (see start_wave_schedule_job), rather than one large call bounded by an
# HTTP request's timeout. A batch's own failure only costs that batch's
# apps their AI review (they keep the rule-based rationale) — it can't
# corrupt or block the rest of the schedule.
LLM_REVIEW_BATCH_SIZE = 6
LLM_REVIEW_BATCH_TIMEOUT_SECONDS = 60
LLM_REVIEW_BATCH_RETRIES = 1
WAVE_PLANNING_NUM_PREDICT = 2048
# Isolated the actual root cause by testing raw Ollama calls directly:
# num_ctx=8192 hung indefinitely (60s+, zero response) on EVERY call, even
# "Say OK" with no other content — while num_ctx=4096 consistently returned
# in 10-17s including a full JSON review. This is a hard ceiling for this
# model on this GPU's VRAM budget, not a prompt-size problem — do not raise
# this without re-testing directly against /api/generate first.
WAVE_PLANNING_NUM_CTX = 4096

# Per-app delivery pipeline within a wave: apps are round-robin assigned into
# parallel streams/lanes (not grouped by topic), sized so a lane holds about
# this many apps before the next lane opens — keeping the stagger roughly
# aligned with the wave's own 4-sprint internal shape (Assessment 1 sprint +
# Migration 2 sprints + Testing 1 sprint).
APPS_PER_LANE_TARGET = 4
# Program Increment (PI) = the wave number. Decommissioning has no rule in
# the underlying Mapping_Logic sheet, so it defaults to N waves after go-live
# — a placeholder convention, not a modeled business rule.
DEFAULT_DECOMMISSION_OFFSET_WAVES = 1

# Internal storage key for the portfolio-wide schedule (every Wave Input row,
# regardless of topic) — the only schedule the dashboard shows now that the
# topic switcher was removed. Distinct from any real topic string.
ALL_TOPICS_KEY = "__all__"
ALL_TOPICS_DISPLAY = "All Harmonization Topics"

# Stage offsets in days from a wave's start (0 = initiation begins).
_INITIATION_DAYS = 7                       # 1 week
_ASSESSMENT_DAYS = SPRINT_WEEKS * 7        # 21 days / 1 sprint
_MIGRATION_DAYS = SPRINT_WEEKS * 7 * 2     # 42 days / 2 sprints
_TESTING_DAYS = SPRINT_WEEKS * 7           # 21 days / 1 sprint
_STABILISATION_DAYS = SPRINT_WEEKS * 7     # 21 days / 1 sprint
_CUTOVER_OFFSET = _INITIATION_DAYS + _ASSESSMENT_DAYS + _MIGRATION_DAYS + _TESTING_DAYS   # day 91 (13wk)
_GATE_REVIEW_OFFSET = _CUTOVER_OFFSET + _STABILISATION_DAYS                               # day 112 (16wk)

_TIER_ORDER = ["simple", "medium", "complex", "very_complex"]
_TIER_LABELS = {"simple": "Simple", "medium": "Medium", "complex": "Complex", "very_complex": "Very Complex"}


# Function: _normalize_tier
def _normalize_tier(raw: Optional[str]) -> str:
    v = (raw or "").strip().lower()
    if "very" in v and "complex" in v:
        return "very_complex"
    if "complex" in v:
        return "complex"
    if "high" in v:
        return "complex"
    if "medium" in v or v == "med":
        return "medium"
    if "simple" in v or "low" in v or "small" in v:
        return "simple"
    return "simple"  # unrecognised/blank — least restrictive, schedules earliest


# Function: _min_wave_for_tier
def _min_wave_for_tier(tier: str, complex_from_wave: int, very_complex_from_wave: int) -> int:
    if tier == "very_complex":
        return very_complex_from_wave
    if tier == "complex":
        return complex_from_wave
    return 1


# Function: _permitted_complexity_label
def _permitted_complexity_label(wave_number: int, complex_from_wave: int, very_complex_from_wave: int) -> str:
    if wave_number < complex_from_wave:
        return "Simple + Medium only"
    if wave_number < very_complex_from_wave:
        return "Simple, Medium, Complex"
    return "All complexities incl. Very Complex"


# Function: _parse_dependencies
def _parse_dependencies(raw: Optional[str]) -> List[str]:
    if not raw:
        return []
    return [token.strip() for token in raw.replace(";", ",").split(",") if token.strip()]


# Function: _wave_start
def _wave_start(program_start: date, wave_number: int) -> date:
    return program_start + timedelta(weeks=WAVE_CADENCE_WEEKS * (wave_number - 1))


# Function: _assign_pipeline_positions
def _assign_pipeline_positions(wave_app_ids_ordered: List[str]) -> Dict[str, tuple]:
    """Round-robin apps (already in priority order) into lanes within a wave.

    Returns {app_id: (stream, position)} — both 1-based. A lane's Nth app is
    staggered N sprints into that lane's pipeline.
    """
    stream_count = max(1, math.ceil(len(wave_app_ids_ordered) / APPS_PER_LANE_TARGET))
    lane_counts = [0] * stream_count
    result: Dict[str, tuple] = {}
    for i, app_id in enumerate(wave_app_ids_ordered):
        lane = i % stream_count
        lane_counts[lane] += 1
        result[app_id] = (lane + 1, lane_counts[lane])
    return result


# Function: _pipeline_fields
def _pipeline_fields(position: int, wave_number: int, decommission_offset_waves: int) -> Dict[str, Any]:
    return {
        "assessment_sprint": position,
        "migration_sprint_start": position + 1,
        "migration_sprint_end": position + 2,
        "qa_uat_sprint": position + 3,
        "go_live_pi": f"PI{wave_number}",
        "stabilization_pi": f"PI{wave_number} (Stabilization)",
        "decommissioning_pi": f"PI{wave_number + decommission_offset_waves}",
    }


# Function: _app_payload
def _app_payload(r: WaveInput, assignment: Dict[str, int], tiers: Dict[str, str],
                  dependencies: Dict[str, List[str]]) -> Dict[str, Any]:
    return {
        "app_id": r.app_id, "application_name": r.application_name, "wave_number": assignment[r.app_id],
        "tshirt_size": r.tshirt_size, "complexity": r.complexity, "complexity_tier": tiers[r.app_id],
        "migration_type": r.migration_type, "quick_win": bool(r.quick_win), "change_impact": r.change_impact,
        "risk": r.risk, "dependencies": dependencies.get(r.app_id, []),
        "wave_eligibility_score": float(r.wave_eligibility_score) if r.wave_eligibility_score is not None else None,
    }


# Function: _chunk
def _chunk(items: List[Any], size: int) -> List[List[Any]]:
    return [items[i:i + size] for i in range(0, len(items), size)]


# Function: _call_ollama_wave_review_with_retries
def _call_ollama_wave_review_with_retries(apps_payload, scaffold_payload, constraints: Dict[str, Any]):
    review = None
    for _ in range(1 + LLM_REVIEW_BATCH_RETRIES):
        review = OllamaService.generate_wave_plan_review(
            apps_payload, scaffold_payload, constraints,
            preferred_model=WAVE_PLANNING_MODEL, temperature=WAVE_PLANNING_TEMPERATURE,
            num_ctx=WAVE_PLANNING_NUM_CTX, max_apps=LLM_REVIEW_BATCH_SIZE,
            timeout=LLM_REVIEW_BATCH_TIMEOUT_SECONDS, num_predict=WAVE_PLANNING_NUM_PREDICT,
            think=WAVE_PLANNING_THINK,
        )
        if review.get("available"):
            break
    return review


# Function: _process_review_batch
def _process_review_batch(batch_app_ids: List[str], by_app_id: Dict[str, WaveInput], assignment: Dict[str, int],
                           tiers: Dict[str, str], dependencies: Dict[str, List[str]], constraints: Dict[str, Any],
                           state: Dict[str, Any]) -> None:
    """Review one batch with Ollama; update `state` in place.

    `state` keys: accepted_rationale, wave_summaries_by_number, batch_summaries,
    model_used, batches_ok.
    """
    batch_apps = [by_app_id[aid] for aid in batch_app_ids]
    apps_payload = [_app_payload(r, assignment, tiers, dependencies) for r in batch_apps]
    scaffold_payload = [
        {"wave_number": w, "app_count": sum(1 for wn in assignment.values() if wn == w)}
        for w in {assignment[aid] for aid in batch_app_ids}
    ]
    review = _call_ollama_wave_review_with_retries(apps_payload, scaffold_payload, constraints)

    if review and review.get("available"):
        state["batches_ok"] += 1
        state["model_used"] = review.get("model_used") or state["model_used"]
        batch_eligible_ids = set(batch_app_ids)
        state["accepted_rationale"].update(
            _apply_llm_overrides(assignment, batch_eligible_ids, MAX_WAVES, dependencies, review)
        )
        for item in review.get("wave_summaries") or []:
            if isinstance(item, dict) and isinstance(item.get("wave_number"), int):
                state["wave_summaries_by_number"].setdefault(item["wave_number"], item)
        if review.get("overall_summary"):
            state["batch_summaries"].append(review["overall_summary"])
    elif review and review.get("model_used"):
        state["model_used"] = state["model_used"] or review.get("model_used")


# Function: _review_with_ollama_batched
def _review_with_ollama_batched(assignment: Dict[str, int], by_app_id: Dict[str, WaveInput],
                                 tiers: Dict[str, str], dependencies: Dict[str, List[str]],
                                 wave_count: int, constraints: Dict[str, Any],
                                 job=None) -> Dict[str, Any]:
    """Review the FULL wave-assigned portfolio in small batches (never a
    single request bounded by one HTTP call's timeout). Every batch is
    independent: a failed or slow batch only costs its own apps the AI
    review — they keep their rule-based rationale — and never blocks or
    corrupts the rest. Mutates *assignment* in place with any accepted
    reassignments, same contract as the old single-call `_apply_llm_overrides`.
    """
    batches: List[List[str]] = []
    for wave_number in range(1, wave_count + 1):
        wave_app_ids = [aid for aid, wn in assignment.items() if wn == wave_number]
        batches.extend(_chunk(wave_app_ids, LLM_REVIEW_BATCH_SIZE))

    if job is not None:
        job.batches_total = len(batches)
        job.batches_done = 0
        job.batches_llm_ok = 0
        db.session.commit()

    state: Dict[str, Any] = {
        "accepted_rationale": {},
        "wave_summaries_by_number": {},
        "batch_summaries": [],
        "model_used": None,
        "batches_ok": 0,
    }

    for batch_app_ids in batches:
        _process_review_batch(batch_app_ids, by_app_id, assignment, tiers, dependencies, constraints, state)
        if job is not None:
            job.batches_done += 1
            job.batches_llm_ok = state["batches_ok"]
            db.session.commit()

    batch_summaries = state["batch_summaries"]
    overall_summary = " ".join(batch_summaries[:3]) if batch_summaries else ""
    return {
        "available": state["batches_ok"] > 0,
        "model_used": state["model_used"],
        "accepted_rationale": state["accepted_rationale"],
        "wave_summaries_by_number": state["wave_summaries_by_number"],
        "overall_summary": overall_summary,
        "batches_total": len(batches),
        "batches_llm_ok": state["batches_ok"],
    }


# Function: _is_valid_llm_override
def _is_valid_llm_override(app_id: str, wave_number: Any, eligible_ids: set, max_waves: int,
                            dependencies: Dict[str, List[str]], assignment: Dict[str, int]) -> bool:
    """True if a proposed (app_id, wave_number) override is safe to apply."""
    if app_id not in eligible_ids or not isinstance(wave_number, int):
        return False
    if not (1 <= wave_number <= max_waves):
        return False
    for dep_id in dependencies.get(app_id, []):
        dep_wave = assignment.get(dep_id)
        if dep_wave is not None and dep_wave >= wave_number:
            return False   # dependency must complete in a strictly earlier wave
    return True


# Function: _apply_llm_overrides
def _apply_llm_overrides(assignment: Dict[str, int], eligible_ids: set, max_waves: int,
                          dependencies: Dict[str, List[str]], review: Dict[str, Any]) -> Dict[str, str]:
    """Validate + apply Ollama-proposed wave re-assignments in place.

    Every suggestion is checked against the real app_id / wave-number space
    before being applied, so a malformed or hallucinated response degrades to
    the rule-based scaffold for that one app rather than corrupting the plan.
    Returns {app_id: rationale} for every accepted override.
    """
    accepted_rationale: Dict[str, str] = {}
    for item in review.get("wave_assignments") or []:
        if not isinstance(item, dict):
            continue
        app_id = str(item.get("app_id") or "").strip()
        wave_number = item.get("wave_number")
        if not _is_valid_llm_override(app_id, wave_number, eligible_ids, max_waves, dependencies, assignment):
            continue
        assignment[app_id] = wave_number
        rationale = item.get("rationale")
        if rationale:
            accepted_rationale[app_id] = str(rationale)
    return accepted_rationale


# Function: list_topics
def list_topics() -> List[str]:
    import_record = latest_import("wave_inputs")
    if not import_record:
        return []
    rows = (
        db.session.query(WaveInput.topic)
        .filter(WaveInput.import_id == import_record.id, WaveInput.topic.isnot(None))
        .distinct().order_by(WaveInput.topic).all()
    )
    return [r[0] for r in rows if r[0]]


# Function: latest_wave_schedule
def latest_wave_schedule(topic: str) -> Optional[WaveSchedule]:
    return WaveSchedule.query.filter_by(topic=topic).first()


# Function: _build_wave_tasks
def _build_wave_tasks(wave_number: int, start: date, applications: int, effort_hours: float,
                       prev_assessment_wbs: Optional[str]) -> List[Dict[str, Any]]:
    """Return the WBS row set for one wave — a header row + the 7 fixed stages."""
    initiation_end = start + timedelta(days=_INITIATION_DAYS)
    assessment_end = start + timedelta(days=_INITIATION_DAYS + _ASSESSMENT_DAYS)
    migration_end = start + timedelta(days=_INITIATION_DAYS + _ASSESSMENT_DAYS + _MIGRATION_DAYS)
    cutover = start + timedelta(days=_CUTOVER_OFFSET)
    stabilisation_end = cutover + timedelta(days=_STABILISATION_DAYS)
    gate_review = start + timedelta(days=_GATE_REVIEW_OFFSET)

    wbs = f"1.{wave_number}"
    rows = [
        {"wbs_code": wbs, "sequence": 0, "task_name": f"WAVE {wave_number}", "task_type": "wave_header",
         "level": 2, "start_date": start, "end_date": gate_review,
         "duration_days": (gate_review - start).days, "is_milestone": False,
         "predecessor_wbs": prev_assessment_wbs, "applications": applications, "effort_hours": effort_hours},
        {"wbs_code": f"{wbs}.1", "sequence": 1, "task_name": "Wave Initiation", "task_type": "initiation",
         "level": 3, "start_date": start, "end_date": initiation_end,
         "duration_days": _INITIATION_DAYS, "is_milestone": False, "predecessor_wbs": None,
         "applications": None, "effort_hours": None},
        {"wbs_code": f"{wbs}.2", "sequence": 2, "task_name": "Assessment - Target State (1 sprint)",
         "task_type": "assessment", "level": 3, "start_date": initiation_end, "end_date": assessment_end,
         "duration_days": _ASSESSMENT_DAYS, "is_milestone": False, "predecessor_wbs": f"{wbs}.1",
         "applications": None, "effort_hours": None},
        {"wbs_code": f"{wbs}.3", "sequence": 3, "task_name": "Migration (2 sprints)", "task_type": "migration",
         "level": 3, "start_date": assessment_end, "end_date": migration_end,
         "duration_days": _MIGRATION_DAYS, "is_milestone": False, "predecessor_wbs": f"{wbs}.2",
         "applications": applications, "effort_hours": effort_hours},
        {"wbs_code": f"{wbs}.4", "sequence": 4, "task_name": "Testing & Validation (1 sprint)",
         "task_type": "testing", "level": 3, "start_date": migration_end, "end_date": cutover,
         "duration_days": _TESTING_DAYS, "is_milestone": False, "predecessor_wbs": f"{wbs}.3",
         "applications": None, "effort_hours": None},
        {"wbs_code": f"{wbs}.5", "sequence": 5, "task_name": f"CUTOVER — Wave {wave_number} Go-Live",
         "task_type": "cutover", "level": 3, "start_date": cutover, "end_date": cutover,
         "duration_days": 0, "is_milestone": True, "predecessor_wbs": f"{wbs}.4",
         "applications": applications, "effort_hours": None},
        {"wbs_code": f"{wbs}.6", "sequence": 6, "task_name": "Stabilisation / Hypercare (1 sprint)",
         "task_type": "stabilisation", "level": 3, "start_date": cutover, "end_date": stabilisation_end,
         "duration_days": _STABILISATION_DAYS, "is_milestone": False, "predecessor_wbs": f"{wbs}.5",
         "applications": None, "effort_hours": None},
        {"wbs_code": f"{wbs}.7", "sequence": 7, "task_name": f"Gate Review — Wave {wave_number} Acceptance",
         "task_type": "gate_review", "level": 3, "start_date": stabilisation_end, "end_date": gate_review,
         "duration_days": 0, "is_milestone": True, "predecessor_wbs": f"{wbs}.6",
         "applications": None, "effort_hours": None},
    ]
    return rows


# Function: _load_wave_input_rows
def _load_wave_input_rows(topic: Optional[str]):
    """Fetch the latest Wave Input rows in scope for schedule recalculation.

    Returns (import_record, rows, is_all, storage_topic).
    """
    is_all = not topic or topic == ALL_TOPICS_KEY

    import_record = latest_import("wave_inputs")
    if not import_record:
        raise ValueError("No Wave Inputs have been imported yet — upload the Wave_Plan_Input workbook first")

    query = WaveInput.query.filter(WaveInput.import_id == import_record.id)
    if not is_all:
        query = query.filter(WaveInput.topic.ilike(f"%{topic}%"))
    rows = query.all()
    if not rows:
        raise ValueError("No Wave Input rows found" if is_all else f"No Wave Input rows found for topic '{topic}'")

    storage_topic = ALL_TOPICS_KEY if is_all else topic
    return import_record, rows, is_all, storage_topic


# Function: _earliest_wave_for_row
def _earliest_wave_for_row(row: WaveInput, tier: str, dependencies, assignment: Dict[str, int],
                            complex_from_wave: int, very_complex_from_wave: int) -> int:
    earliest = _min_wave_for_tier(tier, complex_from_wave, very_complex_from_wave)
    for dep_id in dependencies.get(row.app_id, []):
        dep_wave = assignment.get(dep_id)
        if dep_wave is not None:
            earliest = max(earliest, dep_wave + 1)  # strictly earlier wave for the dependency
    return earliest


# Function: _place_app_in_wave
def _place_app_in_wave(app_id: str, earliest: int, used_capacity: Dict[int, int], capacity: int,
                        assignment: Dict[str, int]) -> bool:
    """Try to place app_id in the earliest wave (>= `earliest`) with spare capacity. Returns True if placed."""
    for wave in range(earliest, MAX_WAVES + 1):
        if used_capacity[wave] < capacity:
            assignment[app_id] = wave
            used_capacity[wave] += 1
            return True
    return False


# Function: _assign_apps_to_waves
def _assign_apps_to_waves(rows: List[WaveInput], complex_from_wave: int, very_complex_from_wave: int):
    """Greedy wave assignment: tier eligibility, dependency ordering, quick-win
    priority, per-wave capacity. Returns
    (assignment, deferred_reason, tiers, dependencies, capacity).
    """
    capacity = max(1, math.ceil(len(rows) / MAX_WAVES))
    dependencies = {r.app_id: _parse_dependencies(r.dependencies) for r in rows}
    tiers = {r.app_id: _normalize_tier(r.complexity) for r in rows}

    # Function: sort_key
    def sort_key(r: WaveInput):
        tier = tiers[r.app_id]
        min_wave = _min_wave_for_tier(tier, complex_from_wave, very_complex_from_wave)
        score = float(r.wave_eligibility_score) if r.wave_eligibility_score is not None else -1.0
        return (0 if r.quick_win else 1, min_wave, -score, r.app_id)

    ordered = sorted(rows, key=sort_key)

    assignment: Dict[str, int] = {}
    deferred_reason: Dict[str, str] = {}
    used_capacity = {w: 0 for w in range(1, MAX_WAVES + 1)}

    for row in ordered:
        tier = tiers[row.app_id]
        earliest = _earliest_wave_for_row(
            row, tier, dependencies, assignment, complex_from_wave, very_complex_from_wave
        )
        placed = _place_app_in_wave(row.app_id, earliest, used_capacity, capacity, assignment)
        if not placed:
            deferred_reason[row.app_id] = f"No capacity within the {MAX_WAVES}-wave / {MAX_PROGRAM_MONTHS}-month program ceiling"

    return assignment, deferred_reason, tiers, dependencies, capacity


# Function: _delete_existing_wave_schedule
def _delete_existing_wave_schedule(storage_topic: str) -> None:
    """Replace any previous schedule for this topic.

    Delete child rows explicitly first — SQLite does not enforce
    ON DELETE CASCADE by default, so a bare parent delete would orphan them.
    """
    existing = WaveSchedule.query.filter_by(topic=storage_topic).first()
    if not existing:
        return
    WaveScheduleApp.query.filter_by(schedule_id=existing.id).delete(synchronize_session=False)
    WaveScheduleTask.query.filter_by(schedule_id=existing.id).delete(synchronize_session=False)
    WaveScheduleWave.query.filter_by(schedule_id=existing.id).delete(synchronize_session=False)
    db.session.delete(existing)
    db.session.flush()


# Function: _default_app_rationale
def _default_app_rationale(r) -> str:
    bits = [f"{r.tshirt_size or 'Unsized'} / {r.complexity or 'unspecified complexity'}"]
    if r.quick_win:
        bits.append("quick win")
    if r.migration_type:
        bits.append(r.migration_type)
    return ", ".join(bits)


# Function: _persist_wave_apps
def _persist_wave_apps(schedule, wave_number, wave_app_ids, by_app_id, tiers, accepted_rationale,
                        wave_summary, decommission_offset_waves) -> None:
    lanes = _assign_pipeline_positions(wave_app_ids)
    for aid in wave_app_ids:
        r = by_app_id[aid]
        stream, position = lanes[aid]
        rationale = accepted_rationale.get(aid) or wave_summary.get("rationale") or _default_app_rationale(r)
        db.session.add(WaveScheduleApp(
            schedule_id=schedule.id, wave_number=wave_number, app_id=r.app_id,
            application_name=r.application_name, topic=r.topic, complexity=r.complexity,
            complexity_tier=tiers[r.app_id], tshirt_size=r.tshirt_size, migration_type=r.migration_type,
            quick_win=bool(r.quick_win), effort_hours=r.total_effort_hours, dependencies=r.dependencies,
            rationale=rationale, source="llm" if aid in accepted_rationale else "heuristic",
            stream=stream, **_pipeline_fields(position, wave_number, decommission_offset_waves),
        ))


# Function: _persist_wave
def _persist_wave(schedule, wave_number, assignment, by_app_id, tiers, start_date, accepted_rationale,
                   wave_summaries_by_number, decommission_offset_waves, prev_assessment_wbs,
                   complex_from_wave, very_complex_from_wave):
    """Persist one wave's WaveScheduleWave/Task/App rows.

    Returns (gate_review_date, next_prev_assessment_wbs).
    """
    wave_app_ids = [aid for aid, wn in assignment.items() if wn == wave_number]
    wave_rows = [by_app_id[aid] for aid in wave_app_ids]
    wstart = _wave_start(start_date, wave_number)
    cutover = wstart + timedelta(days=_CUTOVER_OFFSET)
    stab_end = cutover + timedelta(days=_STABILISATION_DAYS)
    gate_review = wstart + timedelta(days=_GATE_REVIEW_OFFSET)
    applications = len(wave_rows)
    effort_hours = sum(float(r.total_effort_hours or 0) for r in wave_rows)
    tier_counts = {t: 0 for t in _TIER_ORDER}
    for r in wave_rows:
        tier_counts[tiers[r.app_id]] += 1

    wave_summary = wave_summaries_by_number.get(wave_number, {})
    db.session.add(WaveScheduleWave(
        schedule_id=schedule.id, wave_number=wave_number, start_date=wstart, cutover_date=cutover,
        stabilisation_end_date=stab_end, gate_review_date=gate_review, application_count=applications,
        effort_hours=effort_hours, quick_win_count=sum(1 for r in wave_rows if r.quick_win),
        topic_count=len({r.topic for r in wave_rows if r.topic}),
        simple_count=tier_counts["simple"], medium_count=tier_counts["medium"],
        complex_count=tier_counts["complex"], very_complex_count=tier_counts["very_complex"],
        permitted_complexity=_permitted_complexity_label(wave_number, complex_from_wave, very_complex_from_wave),
        theme=wave_summary.get("theme"), rationale=wave_summary.get("rationale"),
    ))

    for task in _build_wave_tasks(wave_number, wstart, applications, effort_hours, prev_assessment_wbs):
        db.session.add(WaveScheduleTask(schedule_id=schedule.id, wave_number=wave_number, **task))
    next_prev_assessment_wbs = f"1.{wave_number}.2"

    _persist_wave_apps(
        schedule, wave_number, wave_app_ids, by_app_id, tiers, accepted_rationale,
        wave_summary, decommission_offset_waves,
    )

    return gate_review, next_prev_assessment_wbs


# Function: _persist_deferred_apps
def _persist_deferred_apps(schedule, deferred_reason, by_app_id, tiers) -> None:
    for aid, reason in deferred_reason.items():
        r = by_app_id[aid]
        db.session.add(WaveScheduleApp(
            schedule_id=schedule.id, wave_number=None, app_id=r.app_id, application_name=r.application_name,
            topic=r.topic, complexity=r.complexity, complexity_tier=tiers[r.app_id], tshirt_size=r.tshirt_size,
            migration_type=r.migration_type, quick_win=bool(r.quick_win), effort_hours=r.total_effort_hours,
            dependencies=r.dependencies, deferred_reason=reason,
        ))


# Function: recalculate_wave_schedule
def recalculate_wave_schedule(topic: Optional[str] = None, program_start: Optional[str] = None,
                               complex_from_wave: int = DEFAULT_COMPLEX_FROM_WAVE,
                               very_complex_from_wave: int = DEFAULT_VERY_COMPLEX_FROM_WAVE,
                               decommission_offset_waves: int = DEFAULT_DECOMMISSION_OFFSET_WAVES,
                               job=None) -> Dict[str, Any]:
    """Recalculate (and persist) the wave schedule from current Wave Inputs.

    When *topic* is omitted (or ``ALL_TOPICS_KEY``), every Wave Input row in
    the latest import is scheduled together as one portfolio-wide programme —
    this is what the dashboard shows. Pass a specific topic string to scope
    the schedule to just that topic instead (still supported for API callers,
    just no longer exposed in the UI).

    Builds a rule-based scaffold, then always sends it to Ollama
    (WAVE_PLANNING_MODEL) for review — never skipped, so this is never
    purely deterministic. Safe to call on every Wave Inputs import and on
    every dashboard read; the persisted schedule reflects whatever the most
    recent call produced, not necessarily the same result as the last one.
    """
    import_record, rows, is_all, storage_topic = _load_wave_input_rows(topic)

    start_date = date.fromisoformat(program_start) if program_start else date.today()
    complex_from_wave = max(1, int(complex_from_wave or DEFAULT_COMPLEX_FROM_WAVE))
    very_complex_from_wave = max(complex_from_wave, int(very_complex_from_wave or DEFAULT_VERY_COMPLEX_FROM_WAVE))

    assignment, deferred_reason, tiers, dependencies, capacity = _assign_apps_to_waves(
        rows, complex_from_wave, very_complex_from_wave
    )

    by_app_id = {r.app_id: r for r in rows}
    wave_count = max(assignment.values()) if assignment else 0

    # ── Ollama review — mandatory, never skipped, so the result is never
    # purely deterministic. Batched (see _review_with_ollama_batched): every
    # wave-assigned app gets reviewed across many small, independent calls
    # instead of one call bounded by an HTTP request's timeout. Every
    # suggestion is validated against the real app/wave space before being
    # applied, so a bad batch degrades to the scaffold for just its own apps
    # rather than corrupting the plan or blocking the rest. ─────────────────
    constraints = {
        "sprint_weeks": SPRINT_WEEKS, "wave_cadence_weeks": WAVE_CADENCE_WEEKS, "max_waves": MAX_WAVES,
        "wave_count": wave_count, "complex_from_wave": complex_from_wave,
        "very_complex_from_wave": very_complex_from_wave,
        "program_bounds_months": [MIN_PROGRAM_MONTHS, MAX_PROGRAM_MONTHS],
    }
    review = _review_with_ollama_batched(assignment, by_app_id, tiers, dependencies, wave_count, constraints, job=job)
    accepted_rationale = review["accepted_rationale"]
    wave_count = max(assignment.values()) if assignment else 0   # an override may have opened a later wave
    wave_summaries_by_number = review["wave_summaries_by_number"]

    _delete_existing_wave_schedule(storage_topic)

    total_effort = sum(float(r.total_effort_hours or 0) for r in rows if r.app_id in assignment)
    schedule = WaveSchedule(
        topic=storage_topic, program_start=start_date, sprint_weeks=SPRINT_WEEKS,
        wave_cadence_weeks=WAVE_CADENCE_WEEKS, max_waves=MAX_WAVES,
        complex_from_wave=complex_from_wave, very_complex_from_wave=very_complex_from_wave,
        source_import_id=import_record.id, wave_count=wave_count, app_count=len(assignment),
        deferred_count=len(deferred_reason), total_effort_hours=total_effort, program_end=None,
        model_used=review.get("model_used"), llm_available=bool(review.get("available")),
        summary=review.get("overall_summary") or None,
    )
    db.session.add(schedule)
    db.session.flush()

    prev_assessment_wbs = None
    program_end = None
    for wave_number in range(1, wave_count + 1):
        gate_review, prev_assessment_wbs = _persist_wave(
            schedule, wave_number, assignment, by_app_id, tiers, start_date, accepted_rationale,
            wave_summaries_by_number, decommission_offset_waves, prev_assessment_wbs,
            complex_from_wave, very_complex_from_wave,
        )
        program_end = gate_review

    _persist_deferred_apps(schedule, deferred_reason, by_app_id, tiers)

    schedule.program_end = program_end
    db.session.commit()
    result = schedule.to_dict()
    if is_all:
        result["topic"] = ALL_TOPICS_DISPLAY
    return result


# Function: recalculate_all_topics
def recalculate_all_topics(topics: Optional[List[str]] = None) -> None:
    """Recalculate the portfolio-wide schedule, plus every per-topic schedule.

    Called after every Wave Inputs import so the stored schedule table can
    never drift from the source data. The portfolio-wide (all-topics)
    schedule is what the dashboard shows; per-topic schedules are kept too
    for API callers that still want to scope by topic. Failures for one
    topic (e.g. no eligible rows) are swallowed — they simply leave that
    topic without a schedule rather than blocking the import.
    """
    try:
        recalculate_wave_schedule(None)
    except ValueError:
        pass
    for topic in (topics if topics is not None else list_topics()):
        try:
            recalculate_wave_schedule(topic)
        except ValueError:
            continue


# ---------------------------------------------------------------------------
# Async job orchestration — "Predict Wave Planning" runs in a background
# thread so the batched Ollama review (potentially many small calls, each
# independently slow on this shared GPU) is never bounded by one HTTP
# request's timeout. The frontend starts a job, then polls its status.
# ---------------------------------------------------------------------------

# Function: _run_wave_schedule_job
def _run_wave_schedule_job(flask_app, job_id: int, topic: Optional[str], kwargs: Dict[str, Any]) -> None:
    with flask_app.app_context():
        job = WaveScheduleJob.query.get(job_id)
        if job is None:
            return
        job.status = "running"
        db.session.commit()
        try:
            result = recalculate_wave_schedule(topic=topic, job=job, **kwargs)
            job.status = "done"
            job.schedule_id = result["id"]
            db.session.commit()
        except ValueError as exc:
            job.status = "failed"
            job.error = str(exc)
            db.session.commit()
        except Exception as exc:
            logger.exception("Wave schedule job %s failed", job_id)
            job.status = "failed"
            job.error = f"Wave schedule calculation failed: {exc}"
            db.session.commit()


# Function: start_wave_schedule_job
def start_wave_schedule_job(flask_app, topic: Optional[str] = None, **kwargs: Any) -> int:
    """Create a WaveScheduleJob and start its background thread. Returns the job id immediately."""
    job = WaveScheduleJob(topic=topic, status="pending")
    db.session.add(job)
    db.session.commit()
    thread = threading.Thread(
        target=_run_wave_schedule_job, args=(flask_app, job.id, topic, kwargs), daemon=True,
    )
    thread.start()
    return job.id


# Function: get_wave_schedule_job
def get_wave_schedule_job(job_id: int) -> Optional[Dict[str, Any]]:
    job = WaveScheduleJob.query.get(job_id)
    if job is None:
        return None
    result = job.to_dict()
    if job.status == "done" and job.schedule_id:
        schedule = WaveSchedule.query.get(job.schedule_id)
        if schedule:
            result["schedule"] = schedule.to_dict()
    return result
