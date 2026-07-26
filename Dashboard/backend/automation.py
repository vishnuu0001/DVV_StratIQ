# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Automation Opportunity Scoring Model.
# Date: 2026-02-11
# ---------------------------------------------------------------------------
"""
Automation Opportunity Scoring Model.

Analyses incident, change, and SR data to identify ticket categories
that are strong candidates for automation based on:
  - Volume       (0-30 pts)
  - Repetition   (0-20 pts)  – similarity of short_descriptions
  - Cycle time   (0-20 pts)  – lower cycle time = easier to automate
  - Load         (0-15 pts)  – assignment group load concentration
  - Complexity   (0-10 pts)  – derived from priority
  - Ageing       (0-5 pts)   – presence of stale open tickets
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class AutomationCandidate:
    category: str
    work_type: str                   # Incident / Change / ServiceRequest
    ticket_count: int
    repetition_score: float          # ratio of unique descriptions / total (0-1, lower = more repetitive)
    avg_cycle_time_hours: float
    assignment_group: str
    volume_score: float              # 0-30
    repetition_weight: float         # 0-20
    cycle_time_score: float          # 0-20
    load_score: float                # 0-15
    complexity_score: float          # 0-10
    ageing_score: float              # 0-5
    total_score: float               # 0-100
    priority: str                    # High / Medium / Low / Monitor
    estimated_hours_saved_monthly: float


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

# Function: _get_category_col
def _get_category_col(df: pd.DataFrame) -> Optional[str]:
    """Return the first usable category-like column name found in df."""
    for col in ["category", "subcategory", "u_request_category", "cat_item", "u_request_type", "type"]:
        if col in df.columns and df[col].notna().any():
            return col
    return None


# Function: _get_cycle_col
def _get_cycle_col(df: pd.DataFrame, work_type: str) -> Optional[str]:
    mapping = {
        "Incident": "resolution_hours",
        "Change": "implementation_hours",
        "ServiceRequest": "closure_hours",
    }
    col = mapping.get(work_type)
    return col if col and col in df.columns else None


# Function: _classify_priority
def _classify_priority(total_score: float) -> str:
    if total_score >= 70:
        return "High"
    if total_score >= 50:
        return "Medium"
    if total_score >= 30:
        return "Low"
    return "Monitor"


# Function: _volume_score
def _volume_score(count: int, global_max_count: int) -> float:
    return (count / max(global_max_count, 1)) * 30


# Function: _repetition_score
def _repetition_score(group: pd.DataFrame, count: int) -> tuple:
    """Return (repetition_ratio, repetition_weight)."""
    if "short_description" in group.columns:
        unique_descs = group["short_description"].dropna().astype(str).nunique()
        repetition_ratio = unique_descs / max(count, 1)
    else:
        repetition_ratio = 0.5  # unknown – assume medium repetition

    if repetition_ratio < 0.3:
        repetition_weight = 20.0   # high repetition
    elif repetition_ratio <= 0.6:
        repetition_weight = 10.0   # medium repetition
    else:
        repetition_weight = 5.0    # low repetition

    return repetition_ratio, repetition_weight


# Function: _cycle_time_score
def _cycle_time_score(group: pd.DataFrame, cycle_col: Optional[str]) -> tuple:
    """Return (avg_cycle, cycle_time_score)."""
    if cycle_col and cycle_col in group.columns:
        cycle_vals = group[cycle_col].dropna()
        avg_cycle = float(cycle_vals.mean()) if not cycle_vals.empty else 0.0
    else:
        avg_cycle = 0.0

    if avg_cycle > 72:
        cycle_time_score = 5.0    # complex, low automation suitability
    elif avg_cycle >= 24:
        cycle_time_score = 15.0   # medium
    else:
        cycle_time_score = 20.0   # short cycle = easy to automate

    return avg_cycle, cycle_time_score


# Function: _load_score
def _load_score(group: pd.DataFrame, global_max_group_count: int) -> tuple:
    """Return (dominant_group, group_count, load_score)."""
    dominant_group = "Unknown"
    group_count = 0
    if "assignment_group" in group.columns:
        ag_counts = group["assignment_group"].astype(str).value_counts()
        if not ag_counts.empty:
            dominant_group = ag_counts.index[0]
            group_count = int(ag_counts.iloc[0])
    load_score = (group_count / max(global_max_group_count, 1)) * 15
    return dominant_group, group_count, load_score


# Function: _complexity_score
def _complexity_score(group: pd.DataFrame) -> float:
    if "priority" not in group.columns:
        return 5.0  # default

    pri_vals = group["priority"].dropna().astype(str)
    # Extract leading numeric character
    num_pris = pri_vals.str.extract(r"(\d)")[0].dropna().astype(float)
    if num_pris.empty:
        return 5.0

    avg_pri = float(num_pris.mean())
    if avg_pri <= 2:
        return 5.0   # high priority = complex
    return 10.0      # capped at 10 per spec


# Function: _ageing_score
def _ageing_score(group: pd.DataFrame, now: pd.Timestamp) -> float:
    date_col = "opened_at"
    if date_col not in group.columns:
        return 0.0
    ts = pd.to_datetime(group[date_col], errors="coerce", utc=True)
    age_days = (now - ts).dt.days.dropna()
    return 5.0 if (age_days >= 30).any() else 0.0


# Function: _build_candidate
def _build_candidate(
    cat_str: str,
    work_type: str,
    group: pd.DataFrame,
    cycle_col: Optional[str],
    now: pd.Timestamp,
    global_max_count: int,
    global_max_group_count: int,
) -> Dict[str, Any]:
    count = len(group)
    volume_score = _volume_score(count, global_max_count)
    repetition_ratio, repetition_weight = _repetition_score(group, count)
    avg_cycle, cycle_time_score = _cycle_time_score(group, cycle_col)
    dominant_group, _group_count, load_score = _load_score(group, global_max_group_count)
    complexity_score = _complexity_score(group)
    ageing_score = _ageing_score(group, now)

    total_score = volume_score + repetition_weight + cycle_time_score + load_score + complexity_score + ageing_score
    total_score = min(total_score, 100.0)
    estimated_hours_saved_monthly = count * avg_cycle * 0.6

    return {
        "category": cat_str,
        "work_type": work_type,
        "ticket_count": count,
        "repetition_score": round(repetition_ratio, 4),
        "avg_cycle_time_hours": round(avg_cycle, 2),
        "assignment_group": dominant_group,
        "volume_score": round(volume_score, 2),
        "repetition_weight": round(repetition_weight, 2),
        "cycle_time_score": round(cycle_time_score, 2),
        "load_score": round(load_score, 2),
        "complexity_score": round(complexity_score, 2),
        "ageing_score": round(ageing_score, 2),
        "total_score": round(total_score, 2),
        "priority": _classify_priority(total_score),
        "estimated_hours_saved_monthly": round(estimated_hours_saved_monthly, 2),
    }


# Function: _score_candidates_for_df
def _score_candidates_for_df(
    df: pd.DataFrame,
    work_type: str,
    global_max_count: int,
    global_max_group_count: int,
) -> List[Dict[str, Any]]:
    """Build raw candidate dicts for a single DataFrame (one work-type)."""
    if df.empty:
        return []

    cat_col = _get_category_col(df)
    if cat_col is None:
        return []

    cycle_col = _get_cycle_col(df, work_type)
    now = pd.Timestamp.now(tz="UTC")

    candidates = []
    for cat, group in df.groupby(cat_col):
        cat_str = str(cat).strip()
        if cat_str.lower() in ("nan", "", "none"):
            continue
        candidates.append(_build_candidate(
            cat_str, work_type, group, cycle_col, now, global_max_count, global_max_group_count
        ))

    return candidates


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

# Function: score_automation_candidates
def score_automation_candidates(
    incidents_df: pd.DataFrame,
    changes_df: pd.DataFrame,
    sr_df: pd.DataFrame,
    top_n: int = 20,
) -> List[AutomationCandidate]:
    """
    Score all ticket categories across Incidents, Changes, and SRs for
    automation suitability. Returns the top_n candidates sorted by total_score.
    """

    # Compute global maxima for normalisation across all work-types
    # Function: _max_cat_count
    def _max_cat_count(df: pd.DataFrame) -> int:
        cat_col = _get_category_col(df)
        if cat_col is None or df.empty:
            return 1
        return int(df.groupby(cat_col).size().max())

    # Function: _max_group_count
    def _max_group_count(df: pd.DataFrame) -> int:
        if df.empty or "assignment_group" not in df.columns:
            return 1
        return int(df["assignment_group"].value_counts().max())

    all_counts = [
        _max_cat_count(incidents_df),
        _max_cat_count(changes_df),
        _max_cat_count(sr_df),
    ]
    all_group_counts = [
        _max_group_count(incidents_df),
        _max_group_count(changes_df),
        _max_group_count(sr_df),
    ]
    global_max_count = max(all_counts) if any(c > 0 for c in all_counts) else 1
    global_max_group_count = max(all_group_counts) if any(c > 0 for c in all_group_counts) else 1

    raw: List[Dict[str, Any]] = []
    raw.extend(_score_candidates_for_df(incidents_df, "Incident", global_max_count, global_max_group_count))
    raw.extend(_score_candidates_for_df(changes_df, "Change", global_max_count, global_max_group_count))
    raw.extend(_score_candidates_for_df(sr_df, "ServiceRequest", global_max_count, global_max_group_count))

    # Sort descending by total_score, take top_n
    raw.sort(key=lambda r: r["total_score"], reverse=True)
    raw = raw[:top_n]

    return [AutomationCandidate(**r) for r in raw]
