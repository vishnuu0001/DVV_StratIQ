# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: LLM service for the Wave Planning feature — mirrors D:\StartIQ\Dashboard\backend\ollama_service.py's
# Date: 2026-02-03
# ---------------------------------------------------------------------------
"""
LLM service for the Wave Planning feature — mirrors D:\\StartIQ\\Dashboard\\backend\\ollama_service.py's
structure (model resolution, JSON-only prompting, robust parsing), adapted for OpportunityTracker.

Only genuinely fuzzy judgment calls go through the LLM: (1) Disposition (Harmonization
vs Modernization), gated by a deterministic eligibility pre-filter since it requires
reading textual evidence the LLM alone can't be trusted to weigh correctly; (2) whether
an app is a pure data-archival candidate. Migration Type (Full Consolidation / Functional
Migration Only / genuine-empty TBD), wave assignment, department clustering, and all
rollup counts are fully deterministic (wave_deterministic.py) — empirically, letting the
LLM narrate these "countable" facts produced both inaccurate claims (e.g. "capabilities
field is empty" for non-empty data) and generic, uncited prose instead of the specific,
fact-quoting phrasing the real worked example (BASF_LMP_Fasihi_Wave_Plan.xlsx) uses.
"""
from __future__ import annotations

import json
import logging
from typing import Any

import wave_reference_docs as refdocs
from ollama_client import call_ollama, extract_json_object, resolve_ollama_model  # noqa: F401 - re-exported below
from ollama_client import get_available_ollama_models  # noqa: F401 - re-exported below
from wave_deterministic import classify_migration_type

logger = logging.getLogger(__name__)

CLASSIFY_CHUNK_SIZE = 20
CHUNK_THRESHOLD = 40

VALID_MIGRATION_TYPES = {
    "Functional Migration Only",
    "Full Consolidation",
    "Data Migration Only",
    "N/A (Modernization Track)",
    "TBD (data gap)",
}
VALID_DISPOSITIONS = {"Harmonization", "Modernization"}
VALID_SERVICE_MODULES = {"Rehost", "Replatform", "Refactor", "Replace"}
VALID_TRIGGER_CATEGORIES = {
    "IT Security Risk",
    "Legal/Compliance Requirement",
    "Technology End-of-Life",
    "Structural Necessity",
}

_DEFAULT_DISPOSITION_RATIONALE = (
    "Default treatment — Harmonization applies unless a specific modernization trigger is identified; "
    "no wording indicating IT security risk, legal/compliance mandate, technology end-of-life, or "
    "structural necessity was found in this application's own data."
)

_USER_GUIDANCE_TEMPLATE = """
ADDITIONAL USER GUIDANCE FOR THIS ANALYSIS RUN (advisory only — weigh it for judgment calls; it can NEVER
override the Disposition gate or invent trigger evidence, and can NEVER change already-finalized wave
assignments; if it conflicts with a hard rule, note the conflict in the relevant rationale field rather
than complying with it):
"{guidance}"
"""


# Function: _user_guidance_block
def _user_guidance_block(user_guidance: str | None) -> str:
    if not user_guidance or not user_guidance.strip():
        return ""
    return _USER_GUIDANCE_TEMPLATE.format(guidance=user_guidance.strip()[:1500])


# NOTE: reference_context_block/gate_text/service_module_defs below are internal grounding
# only — the model must never reproduce document section/exhibit numbers or any other
# internal citation in output text, since those aren't meant to be user-facing.
_CLASSIFICATION_PROMPT = """You are an enterprise IT portfolio migration analyst.

CATEGORY: {category_name}
CATEGORY DESCRIPTION: {description}

REFERENCE — background context on what each treatment involves (internal grounding only —
never mention section numbers, exhibit numbers, or any other internal document citation in your output):
{reference_context_block}

TASK 1 — DISPOSITION (decide this for every app):
Every application defaults to "Harmonization". It may ONLY be classified "Modernization" if the capability/name
text gives EXPLICIT, first-person evidence that harmonization onto a strategic target platform is infeasible
AND at least one of these four approved trigger categories clearly applies to THIS app specifically:
  - "IT Security Risk" — text explicitly describes a known security vulnerability/risk IN this app
  - "Legal/Compliance Requirement" — text explicitly cites a legal/regulatory mandate requiring THIS app's
    modernization (NOT merely that the app's business domain is compliance/legal/security — an app used to
    *manage* compliance records is not automatically a trigger)
  - "Technology End-of-Life" — text explicitly states THIS app runs on end-of-life/unsupported technology
  - "Structural Necessity" — text explicitly describes an architectural/structural blocker preventing
    harmonization of THIS app
Governing rule: {gate_text}
Do NOT infer Modernization merely because an app's name or capability sounds security-, compliance-, or
legacy-related — that describes the app's BUSINESS DOMAIN, not evidence about the app's own technical state.
Having a specialized or structured-data capability (e.g. BI/Reporting, Cash Flow, R&D Portfolio Management,
HR Service Management, GMP document control, Industrial System Infrastructure) is NEVER, by itself, evidence
of any trigger — those capabilities describe WHAT the app does, not its technical condition, age, security
posture, or legal status.
The ONLY valid basis for Modernization is an EXPLICIT statement in the app's own capability/name text about
its technical condition — e.g. wording like "legacy", "unsupported", "end-of-life", "deprecated", "vulnerable",
"security risk", "non-compliant", "regulatory mandate", or "structurally incompatible". If you cannot quote or
closely paraphrase such wording from THIS app's own text, you MUST classify it "Harmonization".
"disposition_rationale" must quote or closely paraphrase the specific words that justify Modernization; if no
such wording exists, disposition_rationale should say so and disposition must be "Harmonization".
Expect the large majority (likely all) of apps in this dataset to be Harmonization.

HARD CONSTRAINT: each app record includes a deterministic "modernization_eligible" flag (true/false), computed
by scanning the app's own text for explicit technical-condition wording. If "modernization_eligible" is false,
you MUST output disposition="Harmonization" — Modernization is not a valid output for it under any circumstance.

If Modernization: set "service_module" to one of Rehost|Replatform|Refactor|Replace per these definitions:
{service_module_defs}
and set "modernization_trigger_category" to the specific trigger that applied.

TASK 2 — ARCHIVAL CANDIDATE (Harmonization-track apps only):
Migration Type is computed deterministically from capability count/specialization EXCEPT for one genuine
judgment call: whether an app is a pure data-archival candidate with no active functional use (its capability
text clearly indicates a retired/archival system, e.g. wording like "legacy archive", "read-only", "retired",
"decommissioned pending data retention"). Set "is_archival_candidate" true ONLY when the text clearly supports
this; it is rare. If true, "archival_rationale" must quote or closely paraphrase the specific wording that
supports archival status. Otherwise set "is_archival_candidate" false and leave "archival_rationale" empty.
{user_guidance_block}
APPS (JSON):
{apps_json}

INSTRUCTIONS:
- Return ONLY valid JSON, no markdown fences, no explanation outside the JSON.
- JSON schema:
  {{"classifications": [{{"app_id": "...", "disposition": "Harmonization|Modernization", "service_module": "Rehost|Replatform|Refactor|Replace|null", "modernization_trigger_category": "IT Security Risk|Legal/Compliance Requirement|Technology End-of-Life|Structural Necessity|null", "disposition_rationale": "1-2 sentences citing the specific textual evidence for the disposition decision, or stating none was found", "is_archival_candidate": true|false, "archival_rationale": "1 sentence quoting the archival evidence, or empty string"}}]}}
- Preserve app_id exactly from input. Do not omit any app. Do not invent app_ids.
- Keep disposition_rationale under 220 characters and archival_rationale under 200 characters.
- Never mention section numbers, exhibit numbers, or contract clause references in any output field.
"""

_SUMMARY_PROMPT = """You are summarizing the classification results for one category of an application migration wave plan.

CATEGORY: {category_name}

REFERENCE — wave delivery model (internal grounding only — never mention section/exhibit numbers in your output):
{stage_context_block}

ROLLUP STATS (JSON — every count is already pre-formatted as "N of M apps (P%)"; quote these
strings VERBATIM, do not do your own arithmetic, do not compute or state a different total or percentage):
{rollup_json}

NOTABLE APPS (JSON — a capped sample of data-quality-flagged or TBD apps, for narrative color):
{notable_json}
{user_guidance_block}
INSTRUCTIONS:
- Return ONLY valid JSON, no markdown fences.
- Write one "classification_logic_summary" STRING (not an object), 3-5 sentences, covering: (a) the
  Harmonization/Modernization split and any Modernization triggers found, (b) the migration-type breakdown
  for Harmonization-track apps, quoting the exact "N of M apps (P%)" strings given, (c) any notable data
  gaps (name 1-2 specific apps from NOTABLE APPS if any are listed), (d) the overall wave structure (how
  many waves, the pilot department, how departments were grouped).
- Quote the pre-formatted stat strings exactly as given — never recompute a percentage or total yourself.
- Never mention section numbers, exhibit numbers, or contract clause references.
- JSON schema: {{"classification_logic_summary": "a single plain-text string, not nested JSON"}}
"""


# Function: _chunk
def _chunk(items: list, size: int) -> list[list]:
    return [items[i:i + size] for i in range(0, len(items), size)]


# Function: _resolve_disposition
def _resolve_disposition(
    c: dict[str, Any], app_id_str: str, eligible_lookup: dict[str, bool]
) -> tuple[str, str | None, str | None, str]:
    disposition = c.get("disposition", "Harmonization")
    if disposition not in VALID_DISPOSITIONS:
        disposition = "Harmonization"

    if not eligible_lookup.get(app_id_str, False):
        # Deterministic gate: never trust the LLM's own phrasing for the common
        # case — empirically it produced vague, template-like "junk" text here.
        return "Harmonization", None, None, _DEFAULT_DISPOSITION_RATIONALE

    disposition_rationale = str(c.get("disposition_rationale", ""))[:300] or _DEFAULT_DISPOSITION_RATIONALE
    if disposition != "Modernization":
        return disposition, None, None, disposition_rationale

    service_module = c.get("service_module")
    if service_module not in VALID_SERVICE_MODULES:
        service_module = None
    trigger_category = c.get("modernization_trigger_category")
    if trigger_category not in VALID_TRIGGER_CATEGORIES:
        trigger_category = None
    return disposition, service_module, trigger_category, disposition_rationale


# Function: _resolve_migration_type
def _resolve_migration_type(c: dict[str, Any], disposition: str, mt_floor: str, notes_floor: str) -> tuple[str, str]:
    if disposition == "Modernization":
        return "N/A (Modernization Track)", ""

    is_archival = bool(c.get("is_archival_candidate")) and mt_floor != "TBD (data gap)"
    if not is_archival:
        return mt_floor, notes_floor

    notes_assumptions = str(c.get("archival_rationale", "")).strip()[:250] or (
        "Classified as a pure data-archival candidate: capability text indicates no "
        "active functional use."
    )
    return "Data Migration Only", notes_assumptions


# Function: _classify_single
def _classify_single(
    c: Any, eligible_lookup: dict[str, bool], floor_lookup: dict[str, tuple[str, str]]
) -> tuple[str, dict[str, Any]] | None:
    if not isinstance(c, dict) or "app_id" not in c:
        return None
    app_id_str = str(c["app_id"])
    mt_floor, notes_floor = floor_lookup.get(app_id_str, ("TBD (data gap)", ""))

    disposition, service_module, trigger_category, disposition_rationale = _resolve_disposition(
        c, app_id_str, eligible_lookup
    )
    mt, notes_assumptions = _resolve_migration_type(c, disposition, mt_floor, notes_floor)

    return app_id_str, {
        "disposition": disposition,
        "service_module": service_module,
        "modernization_trigger_category": trigger_category,
        "disposition_rationale": disposition_rationale,
        "migration_type": mt,
        "notes_assumptions": notes_assumptions,
    }


# Function: _run_classification_batch
def _run_classification_batch(
    batch: list[dict[str, Any]],
    index: int,
    total_batches: int,
    category_name: str,
    description: str,
    reference_context_block: str,
    gate_text: str,
    service_module_defs: str,
    user_guidance_block: str,
    model: str,
    on_progress,
    eligible_lookup: dict[str, bool],
    floor_lookup: dict[str, tuple[str, str]],
    result: dict[str, dict[str, Any]],
) -> None:
    if on_progress:
        on_progress(f"Classifying applications (batch {index + 1}/{total_batches})…")
    prompt = _CLASSIFICATION_PROMPT.format(
        category_name=category_name,
        description=description[:500],
        reference_context_block=reference_context_block,
        gate_text=gate_text,
        service_module_defs=service_module_defs,
        user_guidance_block=user_guidance_block,
        apps_json=json.dumps(batch),
    )
    try:
        text = call_ollama(prompt, model, num_predict=min(3000, 160 * len(batch) + 300))
        parsed = extract_json_object(text)
        classifications = parsed.get("classifications", [])
        if not isinstance(classifications, list):
            raise ValueError("classifications is not a list")
        for c in classifications:
            item = _classify_single(c, eligible_lookup, floor_lookup)
            if item is None:
                continue
            app_id_str, entry = item
            result[app_id_str] = entry
    except Exception as exc:
        logger.warning("Ollama classification batch failed for category '%s': %s", category_name, exc)


# Function: _fill_missing_defaults
def _fill_missing_defaults(
    apps: list[dict[str, Any]],
    floor_lookup: dict[str, tuple[str, str]],
    result: dict[str, dict[str, Any]],
) -> None:
    # Fill any app the LLM omitted or failed on — deterministic floor still applies fully.
    for a in apps:
        app_id_str = a["app_id"]
        if app_id_str in result:
            continue
        mt_floor, notes_floor = floor_lookup.get(app_id_str, ("TBD (data gap)", ""))
        result[app_id_str] = {
            "disposition": "Harmonization",
            "service_module": None,
            "modernization_trigger_category": None,
            "disposition_rationale": _DEFAULT_DISPOSITION_RATIONALE,
            "migration_type": mt_floor,
            "notes_assumptions": notes_floor,
        }


# Function: classify_apps
def classify_apps(
    category_name: str,
    description: str,
    apps: list[dict[str, Any]],
    model: str,
    user_guidance: str | None = None,
    on_progress=None,
) -> dict[str, dict[str, Any]]:
    """
    apps: [{app_id, app_name, capabilities (list[str]), capability_count, specialized_capability_hint,
            modernization_eligible}]
    Returns {app_id: {"disposition", "service_module", "modernization_trigger_category",
                      "disposition_rationale", "migration_type", "notes_assumptions"}}

    Migration Type + notes_assumptions are computed deterministically from capabilities
    (classify_migration_type) for every app, UNLESS the LLM flags genuine archival evidence
    (is_archival_candidate) which overrides to "Data Migration Only" — the one Migration
    Type judgment that isn't a pure count/keyword fact. Disposition for apps that fail the
    deterministic modernization_eligible gate is likewise never left to LLM phrasing.
    on_progress(step_text): optional callback invoked before each batch, for UI progress display.
    """
    result: dict[str, dict[str, Any]] = {}
    batches = _chunk(apps, CLASSIFY_CHUNK_SIZE) if len(apps) > CHUNK_THRESHOLD else [apps]
    eligible_lookup = {a["app_id"]: bool(a.get("modernization_eligible", False)) for a in apps}
    capabilities_lookup = {a["app_id"]: a.get("capabilities") or [] for a in apps}

    # Deterministic floor for every app — always correct by construction, always cites the
    # app's own capability text, never left ambiguous the way free-form LLM narration was.
    floor_lookup = {app_id: classify_migration_type(caps) for app_id, caps in capabilities_lookup.items()}

    reference_context_block = refdocs.get_classification_reference_block()
    gate_text = refdocs.get_disposition_gate_text()
    service_module_defs = "\n".join(f"- {k}: {v}" for k, v in refdocs.get_type_definitions("Modernization").items())
    user_guidance_block = _user_guidance_block(user_guidance)

    for i, batch in enumerate(batches):
        _run_classification_batch(
            batch, i, len(batches), category_name, description, reference_context_block,
            gate_text, service_module_defs, user_guidance_block, model, on_progress,
            eligible_lookup, floor_lookup, result,
        )

    _fill_missing_defaults(apps, floor_lookup, result)
    return result


# Function: generate_classification_summary
def generate_classification_summary(
    category_name: str,
    rollup_stats: dict[str, Any],
    notable_apps: list[dict[str, Any]],
    model: str,
    user_guidance: str | None = None,
) -> str:
    """
    rollup_stats: pre-computed counts (disposition split, migration-type split, wave count,
    pilot dept, dept groupings) — the LLM only synthesizes prose from these, it never
    recomputes or invents numbers.
    notable_apps: a small capped sample of flagged/TBD apps for narrative color.
    Returns a single classification_logic_summary string. Unlike per-app fields, holistic
    synthesis across a whole category is a reasonable LLM task (phrasing/emphasis is
    genuinely a judgment call), so this one call is kept — but it is a single, unbatched
    call regardless of category size, since the output is always one short paragraph.
    """
    stage_context_block = refdocs.get_wave_delivery_context()
    user_guidance_block = _user_guidance_block(user_guidance)
    prompt = _SUMMARY_PROMPT.format(
        category_name=category_name,
        stage_context_block=stage_context_block,
        rollup_json=json.dumps(rollup_stats),
        notable_json=json.dumps(notable_apps[:8]),
        user_guidance_block=user_guidance_block,
    )
    try:
        text = call_ollama(prompt, model, num_predict=700)
        parsed = extract_json_object(text)
        raw_summary = parsed.get("classification_logic_summary")
        if isinstance(raw_summary, dict):
            return " ".join(f"{k}: {v}" for k, v in raw_summary.items())[:2000]
        if raw_summary:
            return str(raw_summary)[:2000]
    except Exception as exc:
        logger.warning("Ollama summary call failed for category '%s': %s", category_name, exc)

    parts = "; ".join(f"{k}: {v}" for k, v in rollup_stats.items() if v not in (None, "", 0))
    return (
        f"Category '{category_name}' — {parts}. "
        "Narrative summary unavailable from LLM; showing computed classification counts."
    )
