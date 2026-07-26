# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Deterministic parsing and wave-assignment logic for the Wave Planning feature.
# Date: 2025-10-18
# ---------------------------------------------------------------------------
"""
Deterministic parsing and wave-assignment logic for the Wave Planning feature.

Everything here is fully deterministic (no LLM) so it can be validated directly
against the real BASF_LMP_Fasihi_Wave_Plan.xlsx worked example. Reverse-engineered
from that example's actual "Wave Assignment (2)" answer key and rationale text
(not just its prose "Classification Logic" summary, which turned out to describe
the general principle but not the exact bin-packing behavior actually used):

  - Departments large enough on their own (>= SOLO_WAVE_THRESHOLD clean apps)
    become a dedicated wave, largest first.
  - Remaining departments are greedily bundled (largest-remaining-first) into
    "balanced" waves targeting ~TARGET_WAVE_SIZE apps each.
  - Whatever is left after that becomes a final long-tail wave.
  - One additional small-to-medium department is hand-picked as "Wave 0 (Pilot)"
    ahead of everything else - in the real example this read as a judgment call
    ("mixed complexity, ideal for validating migration approach"), not a pure
    size rule, so this picks the smallest department within a sensible band
    rather than claiming to exactly reproduce BASF's specific historical choice.
  - Apps flagged as data-quality issues (Inconsistency=True) are pulled into a
    remediation track; once "fixed" they rejoin their original department's wave
    if it's still open, otherwise they roll forward into the next open wave.

This will not byte-for-byte reproduce every small-department pairing from the
historical Fasihi example (which likely reflects org-chart context not present
in this flat dataset), but reproduces the overall structure faithfully: solo
waves for large depts, a pilot, balanced bundling for mid-size depts, and a
long-tail wave for the smallest ones.
"""
from __future__ import annotations

import re
from typing import Any

import pandas as pd

SOLO_WAVE_THRESHOLD = 9          # clean-app count at/above which a dept gets its own wave
TARGET_WAVE_SIZE = 12            # bin-packing target size for bundled waves
PILOT_MIN_SIZE = 3               # pilot dept must have at least this many clean apps
PILOT_MAX_SIZE = 6               # ...and no more than this many (small, low-risk)
PILOT_TARGET_SIZE = 4            # preferred pilot size within that band
BASE_QUARTER = (2026, 4)         # (year, quarter) that Wave 0 / remediation starts in

_SPECIALIZED_CAPABILITY_TERMS = [
    "hr service management",
    "gmp document control",
    "gmp doc control",
    "r&d portfolio",
    "r&d competencies",
    "research and development portfolio",
    "bi/reporting",
    "business intelligence",
    "reporting",
    "cash flow",
    "industrial system infrastructure",
]

_SIMPLE_CAPABILITY_TERMS = ["communicate internally", "communicate externally"]


# ── Excel parsing ────────────────────────────────────────────────────────────

# Function: parse_scope_file
def parse_scope_file(path: str) -> list[dict[str, Any]]:
    """Parse "Application Scope List.xlsx"-shaped file, sheet 'Lead', header row 3 (index 2)."""
    df = pd.read_excel(path, sheet_name="Lead", header=2)
    required = ["SolutionApproach", "Application Name", "CMDB Line Items (estimation)", "Description", "Lead"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Application Scope List: missing expected column(s): {missing}")

    df = df.dropna(subset=["SolutionApproach"])
    # Function: clean
    def clean(value: Any) -> str:
        return str(value).strip() if pd.notna(value) else ""

    rows = []
    for _, r in df.iterrows():
        rows.append({
            "solution_approach": clean(r["SolutionApproach"]),
            "application_name": clean(r.get("Application Name")),
            "estimated_app_count": int(r["CMDB Line Items (estimation)"]) if pd.notna(r.get("CMDB Line Items (estimation)")) else 0,
            "description": clean(r.get("Description")),
            # Lead (owner name) intentionally not extracted/stored — not needed by this
            # feature and the source data for it is inconsistent (blank/placeholder values).
        })
    return rows


# Function: parse_categorization_file
def parse_categorization_file(path: str) -> list[dict[str, Any]]:
    """Parse "BusinessApplication_Categorized.xlsx"-shaped file, sheet 'Apps from customer'.

    pandas auto-disambiguates the duplicate Department/OLB Level 2 columns as
    'Department'/'Department.1' and 'OLB Level 2'/'OLB Level 2.1'. Confirmed via
    direct inspection: the FIRST OLB Level 2 (business-owner side) is the field
    that matches the Dept (OLB L2) values used throughout the real wave plan.
    """
    df = pd.read_excel(path, sheet_name="Apps from customer", header=0)
    required = ["Number", "Name", "Categorization", "OLB Level 2", "Capabilities", "Inconsistency"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"BusinessApplication_Categorized: missing expected column(s): {missing}")

    # Function: clean
    def clean(value: Any) -> str:
        return str(value).strip() if pd.notna(value) else ""

    rows = []
    for idx, r in df.iterrows():
        if pd.isna(r.get("Number")):
            continue
        rows.append({
            "source_row_index": int(idx),
            "app_id": clean(r["Number"]),
            "app_name": clean(r.get("Name")),
            "category": clean(r.get("Categorization")),
            "dept": clean(r.get("OLB Level 2")),
            "dept_full": clean(r.get("Department")),
            "dept2": clean(r.get("OLB Level 2.1")),
            "business_owner": clean(r.get("Business owner")),
            "it_owner": clean(r.get("IT Application owner")),
            "architecture_type": clean(r.get("Architecture type")),
            "capabilities_raw": clean(r.get("Capabilities")),
            "data_quality_flag": bool(r.get("Inconsistency")) if pd.notna(r.get("Inconsistency")) else False,
        })
    return rows


# ── Capability parsing ───────────────────────────────────────────────────────

# Function: parse_capabilities
def parse_capabilities(raw: str) -> list[str]:
    """'Provide Piping Engineering (Provides), Provide X (Provides), ' -> ['Piping Engineering', 'X']"""
    if not raw or not raw.strip():
        return []
    parts = [p.strip() for p in raw.split(",")]
    cleaned = []
    for p in parts:
        if not p:
            continue
        p = re.sub(r"\(Provides\)\s*$", "", p).strip()
        p = re.sub(r"^Provide\s+", "", p, flags=re.IGNORECASE).strip()
        if p:
            cleaned.append(p)
    return cleaned


# Function: capability_tier
def capability_tier(count: int) -> str:
    return "Simple" if count <= 1 else "Complex"


# Function: matches_specialized_capability
def matches_specialized_capability(capabilities: list[str]) -> tuple[bool, str | None]:
    for cap in capabilities:
        low = cap.lower()
        for term in _SPECIALIZED_CAPABILITY_TERMS:
            if term in low:
                return True, cap
    return False, None


# Function: is_simple_communication_capability
def is_simple_communication_capability(capabilities: list[str]) -> bool:
    if len(capabilities) != 1:
        return False
    low = capabilities[0].lower()
    return any(term in low for term in _SIMPLE_CAPABILITY_TERMS)


# Function: classify_migration_type
def classify_migration_type(capabilities: list[str]) -> tuple[str, str]:
    """Deterministic Migration Type classification + accompanying notes/assumptions
    text, phrased to match the real BASF worked example's own "Notes / assumptions"
    column (see BASF_LMP_Fasihi_Wave_Plan.xlsx). Full Consolidation, Functional
    Migration Only, and genuine-empty TBD are fully determined by capability
    count/specialization — there is no fuzzy judgment call here, so this is never
    left to the LLM (empirically, llama3.1:8b was unreliable at this: it both
    hallucinated "empty/unparseable" for non-empty capability lists and produced
    generic, uncited narrative text instead of quoting the actual capability names).
    The only genuine judgment left to the LLM is whether an app is a pure archival
    candidate (Data Migration Only), which requires reading intent, not counting."""
    if not capabilities:
        return (
            "TBD (data gap)",
            "Capabilities field is empty; migration type cannot be determined from available data.",
        )

    hint, term = matches_specialized_capability(capabilities)
    n = len(capabilities)

    if hint:
        if n == 1:
            return (
                "Full Consolidation",
                f"Migration type: single structured-data capability ('{term}') -> classified Full "
                "Consolidation (structured records need data + functional migration).",
            )
        return (
            "Full Consolidation",
            f"Migration type: {n} capabilities including specialized/structured-data capability "
            f"('{term}') -> classified Full Consolidation (structured records require both data and "
            "functional migration).",
        )
    if n >= 3:
        cap_list = ", ".join(f"'{c}'" for c in capabilities[:4])
        return (
            "Full Consolidation",
            f"Migration type: {n} capabilities ({cap_list}) -> classified Full Consolidation "
            "(multiple capabilities require both data and functional migration).",
        )
    if n == 1:
        return (
            "Functional Migration Only",
            f"Migration type: single capability ('{capabilities[0]}') -> classified Functional "
            "Migration Only (content/process migrates, minimal data transformation expected).",
        )
    return (
        "Functional Migration Only",
        f"Migration type: 2 capabilities ('{capabilities[0]}', '{capabilities[1]}'), neither "
        "specialized -> classified Functional Migration Only (process/config migration, minimal "
        "data transformation expected).",
    )


# Function: _ordinal
def _ordinal(n: int) -> str:
    if 10 <= n % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


# Function: _quarter_label
def _quarter_label(year: int, q: int) -> str:
    return f"Q{q} {year}"


# Deterministic NECESSARY (not sufficient) pre-condition for Modernization eligibility.
# Empirically required: prompting llama3.1:8b to only invoke Modernization on explicit
# textual evidence was NOT reliable on its own — it repeatedly rationalized Modernization
# for apps with a "specialized capability" (BI, Cash Flow, R&D Portfolio, etc.), literally
# citing "specialized capability hint is true" as its justification despite an explicit
# instruction that capability complexity is never trigger evidence. Narrow, word-boundary
# phrases describing an app's own technical/legal condition (verified to produce zero hits
# across the full 416-row dataset, i.e. matches the real 0/70 Modernization ground truth)
# gate which apps the LLM is even allowed to consider for Modernization; ineligible apps are
# hard-defaulted to Harmonization in wave_llm_service.py regardless of what the LLM outputs.
_MODERNIZATION_TRIGGER_PATTERN = re.compile(
    r"\blegacy\b|\bend[- ]of[- ]life\b|\beol\b|\bunsupported\b|\bdeprecated\b|\bvulnerab\w*\b|"
    r"\bsecurity risk\b|\bsecurity vulnerabilit\w*\b|\bnon-?compliant\b|\bregulatory mandate\b|"
    r"\bsunset\b|\bobsolete\b|\bout[- ]of[- ]support\b|\bstructurally incompatible\b|"
    r"\bcannot be (?:harmonized|migrated|consolidated)\b",
    re.IGNORECASE,
)


# Function: modernization_eligible
def modernization_eligible(app_name: str, capabilities_raw: str) -> tuple[bool, str | None]:
    """Returns (eligible, matched_phrase). Only apps whose OWN name/capability text contains
    explicit technical-condition language are even offered to the LLM as Modernization
    candidates — see _MODERNIZATION_TRIGGER_PATTERN's comment for why this gate is necessary."""
    text = f"{app_name or ''} {capabilities_raw or ''}"
    m = _MODERNIZATION_TRIGGER_PATTERN.search(text)
    return (True, m.group(0)) if m else (False, None)


# ── Department clustering & wave assignment ──────────────────────────────────

# Function: cluster_departments
def cluster_departments(apps: list[dict[str, Any]]) -> dict[str, int]:
    """dept -> count of CLEAN (non-flagged) apps in that dept."""
    counts: dict[str, int] = {}
    for a in apps:
        if a["data_quality_flag"]:
            continue
        d = a["dept"] or "Unassigned"
        counts[d] = counts.get(d, 0) + 1
    return counts


# Function: _select_pilot_dept
def _select_pilot_dept(sorted_depts: list[tuple[str, int]]) -> str:
    # 1. Pilot: a small-to-medium dept, closest to PILOT_TARGET_SIZE (a deliberate
    # "low-risk, meaningful enough to validate the process" pick), within
    # [PILOT_MIN_SIZE, PILOT_MAX_SIZE], else closest to that target overall.
    pilot_candidates = [(d, c) for d, c in sorted_depts if PILOT_MIN_SIZE <= c <= PILOT_MAX_SIZE]
    if not pilot_candidates:
        pilot_candidates = sorted_depts
    return min(pilot_candidates, key=lambda kv: (abs(kv[1] - PILOT_TARGET_SIZE), kv[0]))[0]


# Function: _assign_solo_waves
def _assign_solo_waves(
    remaining: dict[str, int], dept_rank: dict[str, int],
    dept_to_wave: dict[str, str], dept_reason: dict[str, str], wave_num: int,
) -> int:
    # 2. Solo waves for large depts, largest first.
    for d, c in sorted(remaining.items(), key=lambda kv: kv[1], reverse=True):
        if c < SOLO_WAVE_THRESHOLD:
            continue
        dept_to_wave[d] = f"Wave {wave_num}"
        prior = "immediately after pilot" if wave_num == 1 else f"following Wave {wave_num - 1}"
        dept_reason[d] = (
            f"Dept {d} is the {_ordinal(dept_rank[d])} largest department ({c} apps); forms "
            f"dedicated wave {prior}"
        )
        wave_num += 1
        del remaining[d]
    return wave_num


# Function: _bin_pack_bundles
def _bin_pack_bundles(remaining: dict[str, int]) -> list[list[str]]:
    # 3. Bin-pack the rest (largest-remaining-first) into balanced waves ~TARGET_WAVE_SIZE.
    left = sorted(remaining.items(), key=lambda kv: kv[1], reverse=True)
    bundles: list[list[str]] = []
    current_bundle: list[str] = []
    current_size = 0
    for d, c in left:
        if current_bundle and current_size + c > TARGET_WAVE_SIZE * 1.25:
            bundles.append(current_bundle)
            current_bundle = []
            current_size = 0
        current_bundle.append(d)
        current_size += c
        if current_size >= TARGET_WAVE_SIZE:
            bundles.append(current_bundle)
            current_bundle = []
            current_size = 0
    if current_bundle:
        bundles.append(current_bundle)
    return bundles


# Function: _assign_bundle_waves
def _assign_bundle_waves(
    bundles: list[list[str]], dept_counts: dict[str, int],
    dept_to_wave: dict[str, str], dept_reason: dict[str, str], wave_num: int,
) -> int:
    # Last bundle (smallest leftovers) becomes the long-tail wave if there's more than one bundle.
    for bundle in bundles:
        for d in bundle:
            dept_to_wave[d] = f"Wave {wave_num}"
            others = [x for x in bundle if x != d]
            if others:
                dept_reason[d] = (
                    f"Dept {d} ({dept_counts[d]} apps) combined with {', '.join(others)} to form "
                    f"balanced wave of ~{TARGET_WAVE_SIZE} apps"
                )
            else:
                dept_reason[d] = f"Dept {d} ({dept_counts[d]} apps) forms Wave {wave_num} (long-tail grouping)"
        wave_num += 1
    return wave_num


# Function: _build_app_wave_result
def _build_app_wave_result(
    a: dict[str, Any], dept_to_wave: dict[str, str], dept_rank: dict[str, int],
    dept_counts: dict[str, int], dept_reason: dict[str, str], wave_to_depts: dict[str, list[str]],
    wave_order: list[str], remediation_quarter: str,
) -> dict[str, Any]:
    d = a["dept"] or "Unassigned"
    own_wave = dept_to_wave.get(d, wave_order[-1])
    rank = dept_rank.get(d, len(dept_rank) + 1)
    clean_count = dept_counts.get(d, 0)
    base_reason = dept_reason.get(d, f"Dept {d} grouped into {own_wave}")

    if not a["data_quality_flag"]:
        return {
            "wave": own_wave, "rejoins_wave": None, "rejoin_rationale": None,
            "dept_clean_count": clean_count, "dept_rank": rank, "is_remediation_rejoin": False,
            "wave_reason": base_reason,
        }

    # Flagged apps: rejoin their own dept's wave, unless that wave is the
    # pilot (closes fastest) - then roll forward into Wave 1.
    if own_wave == "Wave 0 (Pilot)":
        rejoin = "Wave 1"
        dest_depts = wave_to_depts.get(rejoin, [])
        dest_label = ", ".join(dest_depts) if dest_depts else rejoin
        rationale = (
            f"Data remediation required ({remediation_quarter}); {d} pilot completes before "
            f"remediation, so this app shifts to {rejoin} with {dest_label} cluster."
        )
    else:
        rejoin = own_wave
        rationale = (
            f"Data remediation required ({remediation_quarter}); rejoins {d}'s own wave "
            f"({rejoin}) once resolved."
        )
    return {
        "wave": rejoin, "rejoins_wave": rejoin, "rejoin_rationale": rationale,
        "dept_clean_count": clean_count, "dept_rank": rank, "is_remediation_rejoin": True,
        "wave_reason": rationale,
    }


# Function: assign_waves
def assign_waves(apps: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """
    Returns {app_id: {"wave": ..., "rejoins_wave": ..., "rejoin_rationale": ...,
                       "dept_clean_count": ..., "dept_rank": ..., "is_remediation_rejoin": bool,
                       "wave_reason": ...}}

    "wave_reason" is a fully deterministic, fact-cited explanation of why this app
    landed in its wave (pilot selection / solo large-dept wave / bin-packed bundle /
    remediation rejoin), phrased to match the real worked example's own Wave
    Assignment Rationale column — this is never left to the LLM to narrate, since
    every fact in it (dept sizes, rank, bundle membership, thresholds) is already
    known exactly by this function; a summarizing LLM only ever reproduced these
    facts vaguely or generically.
    """
    dept_counts = cluster_departments(apps)
    if not dept_counts:
        return {a["app_id"]: {"wave": "Wave 1", "rejoins_wave": None, "rejoin_rationale": None,
                               "dept_clean_count": 0, "dept_rank": 0, "is_remediation_rejoin": False,
                               "wave_reason": "No clean-department data available; defaulted to Wave 1."}
                for a in apps}

    sorted_depts = sorted(dept_counts.items(), key=lambda kv: kv[1], reverse=True)
    dept_rank = {d: i + 1 for i, (d, _) in enumerate(sorted_depts)}

    remaining = dict(sorted_depts)

    pilot_dept = _select_pilot_dept(sorted_depts)
    pilot_count = dept_counts[pilot_dept]
    del remaining[pilot_dept]

    dept_to_wave: dict[str, str] = {pilot_dept: "Wave 0 (Pilot)"}
    dept_reason: dict[str, str] = {
        pilot_dept: (
            f"Dept {pilot_dept} selected as pilot: {pilot_count} apps, mixed complexity, ideal for "
            "validating migration approach before scaling"
        )
    }

    wave_num = _assign_solo_waves(remaining, dept_rank, dept_to_wave, dept_reason, 1)

    bundles = _bin_pack_bundles(remaining)
    wave_num = _assign_bundle_waves(bundles, dept_counts, dept_to_wave, dept_reason, wave_num)

    wave_to_depts: dict[str, list[str]] = {}
    for d, w in dept_to_wave.items():
        wave_to_depts.setdefault(w, []).append(d)
    remediation_quarter = _quarter_label(*BASE_QUARTER)

    # 4. Assign each app; handle remediation rejoin logic.
    wave_order = ["Wave 0 (Pilot)"] + [f"Wave {i}" for i in range(1, wave_num)]
    return {
        a["app_id"]: _build_app_wave_result(
            a, dept_to_wave, dept_rank, dept_counts, dept_reason, wave_to_depts, wave_order, remediation_quarter
        )
        for a in apps
    }


# Function: assign_quarters
def assign_quarters(wave: str) -> dict[str, str]:
    """Deterministic quarter offsets: each wave index shifts start by one quarter,
    phases are Assessment -> Migration -> Test/Cutover -> AMS -> Steady (one q each)."""
    m = re.search(r"Wave (\d+)", wave)
    idx = int(m.group(1)) if m else 0
    year, q = BASE_QUARTER
    start_q_index = (year * 4 + (q - 1)) + idx  # +1 quarter per wave index
    stream2_index = start_q_index
    stream3_index = start_q_index + 1
    ams_index = start_q_index + 2

    # Function: fmt
    def fmt(qi: int) -> str:
        y, qq = divmod(qi, 4)
        return f"Q{qq + 1} {y}"

    return {
        "stream2_assessment": fmt(stream2_index),
        "stream3_execution": fmt(stream3_index),
        "ams_transition_start": fmt(ams_index),
    }
