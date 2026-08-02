# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: AI-assisted Harmonization wave plan generation (Ollama + deterministic
#        sprint/cutover scheduling) from Technical Assessment Wave Inputs.
# Date: 2026-07-20
# ---------------------------------------------------------------------------
"""AI-assisted Harmonization wave plan generation.

Scheduling is deterministic (T-shirt size -> sprint count, bin-packed into
quarterly waves capped at a 3-24 month program). The Ollama LLM is used only
to *review* the deterministic draft and propose validated refinements
(re-sequencing, per-wave themes) — every suggestion is checked against the
real app_id / wave-number space before being applied, so an unavailable or
malformed LLM response degrades gracefully to the deterministic schedule.
"""
import calendar
from datetime import date, timedelta
from typing import Any, Dict, List, Optional

from app import db
from app.models.technical_assessment import WaveInput
from app.models.wave_plan import WavePlan, WavePlanEntry
from app.services.ollama_service import OllamaService
from app.services.technical_assessment_service import latest_import

DEFAULT_COMPLEXITY_SCOPE = ["Low", "Medium"]
MIN_PROGRAM_MONTHS = 3
MAX_PROGRAM_MONTHS = 24
SPRINT_WEEKS = 3
CUTOVER_FREQUENCY_MONTHS = 3
DEFAULT_PARALLEL_STREAMS = 3

_TSHIRT_SPRINTS = {"XXS": 1, "XS": 1, "EXTRA SMALL": 1, "S": 1, "SMALL": 1,
                    "M": 2, "MEDIUM": 2, "L": 3, "LARGE": 3,
                    "XL": 4, "EXTRA LARGE": 4, "XXL": 4}


# Function: _add_months
def _add_months(start: date, months: int) -> date:
    """Add *months* calendar months to *start*, clamping the day-of-month."""
    total = start.month - 1 + months
    year = start.year + total // 12
    month = total % 12 + 1
    day = min(start.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


# Function: _sprint_estimate
def _sprint_estimate(row: WaveInput) -> int:
    size = (row.tshirt_size or "").strip().upper()
    if size in _TSHIRT_SPRINTS:
        return _TSHIRT_SPRINTS[size]
    hours = float(row.total_effort_hours) if row.total_effort_hours is not None else None
    if hours is not None:
        if hours <= 80:
            return 1
        if hours <= 160:
            return 2
        if hours <= 240:
            return 3
        return 4
    return 2


# Function: _parse_dependencies
def _parse_dependencies(raw: Optional[str]) -> List[str]:
    if not raw:
        return []
    return [token.strip() for token in raw.replace(";", ",").split(",") if token.strip()]


# Function: list_topics
def list_topics() -> List[str]:
    """Distinct Wave Input topics available for wave-plan generation."""
    import_record = latest_import("wave_inputs")
    if not import_record:
        return []
    rows = (
        db.session.query(WaveInput.topic)
        .filter(WaveInput.import_id == import_record.id, WaveInput.topic.isnot(None))
        .distinct()
        .order_by(WaveInput.topic)
        .all()
    )
    return [r[0] for r in rows if r[0]]


# Function: latest_wave_plan
def latest_wave_plan(topic: Optional[str] = None) -> Optional[WavePlan]:
    query = WavePlan.query
    if topic:
        query = query.filter(WavePlan.topic == topic)
    return query.order_by(WavePlan.created_at.desc(), WavePlan.id.desc()).first()


# Function: _build_scaffold
# Function: _earliest_wave_for_deps
def _earliest_wave_for_deps(row: WaveInput, assignment: Dict[str, int], by_app_id: dict) -> int:
    earliest = 1
    for dep_id in _parse_dependencies(row.dependencies):
        dep_wave = assignment.get(dep_id)
        if dep_wave is not None:
            earliest = max(earliest, dep_wave)
        elif dep_id in by_app_id and dep_id not in assignment:
            # Dependency is in scope but not yet placed (processed later in
            # this pass) — best-effort: leave earliest as-is, LLM review or
            # a future regeneration can tighten sequencing further.
            pass
    return earliest


# Function: _place_in_wave
def _place_in_wave(row: WaveInput, estimate: int, earliest: int, max_waves: int,
                    used_capacity: Dict[int, int], wave_capacity: int, assignment: Dict[str, int]) -> bool:
    for wave in range(earliest, max_waves + 1):
        if used_capacity[wave] + estimate <= wave_capacity:
            assignment[row.app_id] = wave
            used_capacity[wave] += estimate
            return True
    return False


# Function: _build_scaffold
def _build_scaffold(eligible: List[WaveInput], max_waves: int, wave_capacity: int):
    """Greedy, dependency-aware bin-pack of eligible apps into waves 1..max_waves.

    Returns (assignment: {app_id: wave_number}, unscheduled: [WaveInput]).
    """
    by_app_id = {row.app_id: row for row in eligible}
    ordered = sorted(
        eligible,
        key=lambda r: (
            0 if r.quick_win else 1,
            -(float(r.wave_eligibility_score) if r.wave_eligibility_score is not None else -1.0),
            _sprint_estimate(r),
        ),
    )
    assignment: Dict[str, int] = {}
    used_capacity: Dict[int, int] = {w: 0 for w in range(1, max_waves + 1)}
    unscheduled: List[WaveInput] = []

    for row in ordered:
        estimate = _sprint_estimate(row)
        earliest = _earliest_wave_for_deps(row, assignment, by_app_id)
        placed = _place_in_wave(row, estimate, earliest, max_waves, used_capacity, wave_capacity, assignment)
        if not placed:
            unscheduled.append(row)

    return assignment, unscheduled


# Function: _parse_override_item
def _parse_override_item(item, eligible_ids: set, max_waves: int) -> Optional[tuple]:
    if not isinstance(item, dict):
        return None
    app_id = str(item.get("app_id") or "").strip()
    wave_number = item.get("wave_number")
    if app_id not in eligible_ids or not isinstance(wave_number, int):
        return None
    if not (1 <= wave_number <= max_waves):
        return None
    return app_id, wave_number


# Function: _deps_satisfied
def _deps_satisfied(app_id: str, wave_number: int, assignment: Dict[str, int], dependencies: Dict[str, List[str]]) -> bool:
    for dep_id in dependencies.get(app_id, []):
        dep_wave = assignment.get(dep_id)
        if dep_wave is not None and dep_wave > wave_number:
            return False
    return True


# Function: _apply_llm_overrides
def _apply_llm_overrides(assignment: Dict[str, int], eligible_ids: set, max_waves: int,
                          dependencies: Dict[str, List[str]], review: Dict[str, Any]) -> Dict[str, str]:
    """Validate + apply LLM-proposed wave re-assignments in place.

    Returns {app_id: rationale} for every accepted override.
    """
    accepted_rationale: Dict[str, str] = {}
    for item in review.get("wave_assignments") or []:
        parsed = _parse_override_item(item, eligible_ids, max_waves)
        if parsed is None:
            continue
        app_id, wave_number = parsed
        if not _deps_satisfied(app_id, wave_number, assignment, dependencies):
            continue
        assignment[app_id] = wave_number
        rationale = item.get("rationale")
        if rationale:
            accepted_rationale[app_id] = str(rationale)
    return accepted_rationale


# Function: _schedule_dates
def _schedule_dates(eligible: List[WaveInput], assignment: Dict[str, int], program_start: date,
                     parallel_streams: int):
    """Second pass: within each wave, lane-pack apps to concrete sprint dates."""
    by_wave: Dict[int, List[WaveInput]] = {}
    for row in eligible:
        wave_number = assignment.get(row.app_id)
        if wave_number is None:
            continue
        by_wave.setdefault(wave_number, []).append(row)

    schedule: Dict[str, Dict[str, Any]] = {}
    for wave_number, rows in by_wave.items():
        wave_start = _add_months(program_start, (wave_number - 1) * CUTOVER_FREQUENCY_MONTHS)
        wave_end = _add_months(program_start, wave_number * CUTOVER_FREQUENCY_MONTHS) - timedelta(days=1)
        lanes = [wave_start for _ in range(max(1, parallel_streams))]
        rows_sorted = sorted(rows, key=lambda r: (0 if r.quick_win else 1, r.app_id))
        for row in rows_sorted:
            lane_idx = min(range(len(lanes)), key=lambda i: lanes[i])
            sprint_start = lanes[lane_idx]
            estimate = _sprint_estimate(row)
            sprint_end = sprint_start + timedelta(weeks=SPRINT_WEEKS * estimate) - timedelta(days=1)
            lanes[lane_idx] = sprint_end + timedelta(days=1)
            schedule[row.app_id] = {
                "wave_number": wave_number,
                "stream": lane_idx + 1,
                "sprint_start": min(sprint_start, wave_end),
                "sprint_end": min(sprint_end, wave_end),
                "cutover_date": wave_end,
            }
    return schedule


# Function: generate_wave_plan
# Function: _resolve_wave_scope
def _resolve_wave_scope(topic: str, complexity_scope: Optional[List[str]]):
    if not topic:
        raise ValueError("A topic (e.g. 'Harmonization') is required")

    import_record = latest_import("wave_inputs")
    if not import_record:
        raise ValueError("No Wave Inputs have been imported yet — upload the Wave_Plan_Input workbook first")

    scope = [c.strip().lower() for c in (complexity_scope or DEFAULT_COMPLEXITY_SCOPE) if c.strip()]
    if not scope:
        scope = [c.lower() for c in DEFAULT_COMPLEXITY_SCOPE]
    return import_record, scope


# Function: _load_eligible_wave_rows
def _load_eligible_wave_rows(import_record, topic: str, scope: List[str]):
    rows = (
        WaveInput.query.filter(WaveInput.import_id == import_record.id, WaveInput.topic.ilike(f"%{topic}%"))
        .all()
    )
    if not rows:
        raise ValueError(f"No Wave Input rows found for topic '{topic}'")

    eligible = [r for r in rows if (r.complexity or "").strip().lower() in scope]
    deferred_high = [r for r in rows if (r.complexity or "").strip().lower() not in scope]
    if not eligible:
        raise ValueError(
            f"No applications in scope '{', '.join(scope)}' complexity for topic '{topic}' "
            f"({len(deferred_high)} deferred)"
        )
    return eligible, deferred_high


# Function: _entry_rationale
def _entry_rationale(row, wave_number, app_id, accepted_rationale, wave_summaries_by_number) -> str:
    rationale = accepted_rationale.get(app_id) or wave_summaries_by_number.get(wave_number, {}).get("rationale")
    if rationale:
        return rationale
    bits = [f"{row.tshirt_size or 'Unsized'} ({_sprint_estimate(row)} sprint(s))"]
    if row.quick_win:
        bits.append("quick win")
    if row.migration_type:
        bits.append(row.migration_type)
    return ", ".join(bits)


# Function: _persist_wave_plan_entries
def _persist_wave_plan_entries(plan, eligible, used_waves, assignment, schedule, wave_summaries_by_number, accepted_rationale) -> None:
    by_app_id = {row.app_id: row for row in eligible}
    for wave_number in used_waves:
        theme = wave_summaries_by_number.get(wave_number, {}).get("theme")
        wave_name = theme or f"Wave {wave_number}"
        wave_apps = sorted(
            [aid for aid, wn in assignment.items() if wn == wave_number],
            key=lambda aid: (schedule[aid]["stream"], schedule[aid]["sprint_start"]),
        )
        for sequence, app_id in enumerate(wave_apps, start=1):
            row = by_app_id[app_id]
            sched = schedule[app_id]
            rationale = _entry_rationale(row, wave_number, app_id, accepted_rationale, wave_summaries_by_number)
            db.session.add(WavePlanEntry(
                plan_id=plan.id, wave_number=wave_number, wave_name=wave_name, sequence=sequence,
                stream=sched["stream"], app_id=row.app_id, application_name=row.application_name,
                tshirt_size=row.tshirt_size, complexity=row.complexity, migration_type=row.migration_type,
                quick_win=bool(row.quick_win), change_impact=row.change_impact, risk=row.risk,
                sprint_estimate=_sprint_estimate(row), dependencies=row.dependencies,
                sprint_start=sched["sprint_start"], sprint_end=sched["sprint_end"],
                cutover_date=sched["cutover_date"], rationale=rationale,
                source="llm" if app_id in accepted_rationale else "heuristic",
            ))


# Function: generate_wave_plan
def generate_wave_plan(topic: str, complexity_scope: Optional[List[str]] = None,
                        parallel_streams: int = DEFAULT_PARALLEL_STREAMS,
                        program_start: Optional[str] = None) -> Dict[str, Any]:
    """Generate (and persist) a Harmonization wave plan for *topic*.

    Deterministic T-shirt-size bin-packing produces the draft schedule;
    Ollama reviews it for sequencing refinements. Only Low/Medium complexity
    apps are scheduled — High complexity apps are deferred to a later stage
    per the harmonization roadmap, matching the 3-24 month / 3-week sprint /
    quarterly cutover program shape.
    """
    import_record, scope = _resolve_wave_scope(topic, complexity_scope)
    parallel_streams = max(1, min(int(parallel_streams or DEFAULT_PARALLEL_STREAMS), 10))

    eligible, deferred_high = _load_eligible_wave_rows(import_record, topic, scope)

    start_date = date.fromisoformat(program_start) if program_start else date.today()
    max_waves = MAX_PROGRAM_MONTHS // CUTOVER_FREQUENCY_MONTHS
    sprints_per_wave = max(1, (CUTOVER_FREQUENCY_MONTHS * 4) // SPRINT_WEEKS)
    wave_capacity = sprints_per_wave * parallel_streams

    assignment, unscheduled = _build_scaffold(eligible, max_waves, wave_capacity)
    dependencies = {row.app_id: _parse_dependencies(row.dependencies) for row in eligible}

    scaffold_payload = [
        {"wave_number": w, "app_ids": [aid for aid, wn in assignment.items() if wn == w]}
        for w in sorted({wn for wn in assignment.values()})
    ]
    apps_payload = [
        {
            "app_id": row.app_id, "application_name": row.application_name,
            "tshirt_size": row.tshirt_size, "complexity": row.complexity,
            "migration_type": row.migration_type, "quick_win": bool(row.quick_win),
            "change_impact": row.change_impact, "risk": row.risk,
            "dependencies": dependencies.get(row.app_id, []),
            "wave_eligibility_score": float(row.wave_eligibility_score) if row.wave_eligibility_score is not None else None,
        }
        for row in eligible if row.app_id in assignment
    ]
    constraints = {
        "sprint_weeks": SPRINT_WEEKS, "cutover_frequency_months": CUTOVER_FREQUENCY_MONTHS,
        "max_waves": max_waves, "parallel_streams": parallel_streams,
        "program_bounds_months": [MIN_PROGRAM_MONTHS, MAX_PROGRAM_MONTHS],
    }

    review = OllamaService.generate_wave_plan_review(apps_payload, scaffold_payload, constraints)
    eligible_ids = set(assignment.keys())
    accepted_rationale = _apply_llm_overrides(assignment, eligible_ids, max_waves, dependencies, review) \
        if review.get("available") else {}

    schedule = _schedule_dates(eligible, assignment, start_date, parallel_streams)

    wave_summaries_by_number = {
        item.get("wave_number"): item
        for item in (review.get("wave_summaries") or [])
        if isinstance(item, dict) and isinstance(item.get("wave_number"), int)
    }

    # ── Replace any previous plan for this topic ───────────────────────────
    # SQLite does not enforce ON DELETE CASCADE by default, so the child
    # WavePlanEntry rows must be deleted explicitly — otherwise they are
    # orphaned and get silently "adopted" by the next plan when SQLite
    # reuses the freed WavePlan.id.
    old_plan_ids = [pid for (pid,) in db.session.query(WavePlan.id).filter(WavePlan.topic == topic).all()]
    if old_plan_ids:
        WavePlanEntry.query.filter(WavePlanEntry.plan_id.in_(old_plan_ids)).delete(synchronize_session=False)
        WavePlan.query.filter(WavePlan.id.in_(old_plan_ids)).delete(synchronize_session=False)
    db.session.flush()

    used_waves = sorted({wn for wn in assignment.values()})
    program_end = max((schedule[aid]["cutover_date"] for aid in schedule), default=start_date)

    plan = WavePlan(
        topic=topic, complexity_scope=",".join(complexity_scope or DEFAULT_COMPLEXITY_SCOPE),
        sprint_weeks=SPRINT_WEEKS, cutover_frequency_months=CUTOVER_FREQUENCY_MONTHS,
        parallel_streams=parallel_streams, program_start=start_date, program_end=program_end,
        wave_count=len(used_waves), app_count=len(schedule),
        deferred_high_complexity_count=len(deferred_high), unscheduled_count=len(unscheduled),
        model_used=review.get("model_used"), llm_available=bool(review.get("available")),
        summary=review.get("overall_summary") or (
            f"{len(schedule)} applications sequenced across {len(used_waves)} wave(s) "
            f"({CUTOVER_FREQUENCY_MONTHS}-month cutover cadence, {SPRINT_WEEKS}-week sprints). "
            f"{len(deferred_high)} High complexity application(s) deferred to a later stage."
        ),
    )
    db.session.add(plan)
    db.session.flush()

    _persist_wave_plan_entries(plan, eligible, used_waves, assignment, schedule, wave_summaries_by_number, accepted_rationale)

    db.session.commit()
    return plan.to_dict()
