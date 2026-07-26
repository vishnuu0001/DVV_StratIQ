# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: KPI engine for the AI-Powered Digital Operations Cockpit.
# Date: 2025-10-09
# ---------------------------------------------------------------------------
"""
KPI engine for the AI-Powered Digital Operations Cockpit.

All public functions accept pandas DataFrames produced by data_cache.py
and return plain Python dicts / lists suitable for JSON serialisation.
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------

# Function: _safe_mean
def _safe_mean(series: pd.Series) -> float:
    vals = series.dropna()
    return float(vals.mean()) if not vals.empty else 0.0


# Function: _safe_median
def _safe_median(series: pd.Series) -> float:
    vals = series.dropna()
    return float(vals.median()) if not vals.empty else 0.0


# Function: _safe_percentile
def _safe_percentile(series: pd.Series, p: float) -> float:
    vals = series.dropna()
    return float(np.percentile(vals, p)) if not vals.empty else 0.0


# Function: _period_label
def _period_label(period: Any) -> str:
    """Convert a pd.Period or string to a readable 'YYYY-MM' label."""
    try:
        return str(period)
    except Exception:
        return str(period)


# Function: _last_n_months
def _last_n_months(n: int) -> list[str]:
    """Return list of 'YYYY-MM' period strings for the last N calendar months."""
    now = datetime.now(tz=timezone.utc)
    periods = []
    for i in range(n - 1, -1, -1):
        dt = now - timedelta(days=30 * i)
        periods.append(f"{dt.year}-{dt.month:02d}")
    return periods


# ---------------------------------------------------------------------------
# 1. Summary KPIs
# ---------------------------------------------------------------------------

# Function: summary_kpis
def summary_kpis(
    incidents_df: pd.DataFrame,
    changes_df: pd.DataFrame,
    sr_df: pd.DataFrame,
) -> Dict[str, Any]:
    """High-level KPIs for the executive summary panel."""

    total_incidents = len(incidents_df)
    total_changes = len(changes_df)
    total_sr = len(sr_df)
    total_tickets = total_incidents + total_changes + total_sr

    # SLA compliance – incidents + SRs with made_sla == true/True/1/"true"
    # Function: _sla_pct
    def _sla_pct(df: pd.DataFrame) -> float:
        if df.empty or "made_sla" not in df.columns:
            return 0.0
        truthy = df["made_sla"].astype(str).str.lower().isin(["true", "1", "yes"])
        return round(float(truthy.mean()) * 100, 2)

    inc_sla = _sla_pct(incidents_df)
    sr_sla = _sla_pct(sr_df)
    sla_combined_pct = round((inc_sla + sr_sla) / 2, 2) if (total_incidents or total_sr) else 0.0

    # Average MTTR for resolved incidents
    avg_mttr = _safe_mean(incidents_df["resolution_hours"]) if "resolution_hours" in incidents_df.columns else 0.0

    # Average cycle time across all types
    cycle_hours: List[float] = []
    for df, col in [
        (incidents_df, "resolution_hours"),
        (changes_df, "implementation_hours"),
        (sr_df, "closure_hours"),
    ]:
        if col in df.columns:
            cycle_hours.extend(df[col].dropna().tolist())
    avg_cycle_time = round(float(np.mean(cycle_hours)), 2) if cycle_hours else 0.0

    # Emergency change percentage
    emergency_pct = 0.0
    if not changes_df.empty and "type" in changes_df.columns:
        emg = changes_df["type"].astype(str).str.lower().str.contains("emergency").sum()
        emergency_pct = round(float(emg / max(len(changes_df), 1)) * 100, 2)

    return {
        "total_tickets": total_tickets,
        "total_incidents": total_incidents,
        "total_changes": total_changes,
        "total_sr": total_sr,
        "by_type": {
            "Incident": total_incidents,
            "Change": total_changes,
            "ServiceRequest": total_sr,
        },
        "sla_compliance_pct": sla_combined_pct,
        "incident_sla_pct": inc_sla,
        "sr_sla_pct": sr_sla,
        "avg_mttr_hours": round(avg_mttr, 2),
        "avg_cycle_time_hours": avg_cycle_time,
        "emergency_change_pct": emergency_pct,
    }


# ---------------------------------------------------------------------------
# 2. Monthly Volume
# ---------------------------------------------------------------------------

# Function: monthly_volume
def monthly_volume(
    incidents_df: pd.DataFrame,
    changes_df: pd.DataFrame,
    sr_df: pd.DataFrame,
    months: int = 12,
) -> List[Dict[str, Any]]:
    """Per-month counts for the last *months* calendar months."""

    periods = _last_n_months(months)

    # Function: _counts
    def _counts(df: pd.DataFrame) -> Dict[str, int]:
        if df.empty or "month_year" not in df.columns:
            return {}
        counts = df["month_year"].astype(str).value_counts().to_dict()
        return counts

    inc_counts = _counts(incidents_df)
    chg_counts = _counts(changes_df)
    sr_counts = _counts(sr_df)

    result = []
    for p in periods:
        inc = inc_counts.get(p, 0)
        chg = chg_counts.get(p, 0)
        sr = sr_counts.get(p, 0)
        result.append({
            "month": p,
            "incidents": inc,
            "changes": chg,
            "service_requests": sr,
            "total": inc + chg + sr,
        })
    return result


# ---------------------------------------------------------------------------
# 3. Cycle Time Stats
# ---------------------------------------------------------------------------

# Function: cycle_time_stats
def cycle_time_stats(df: pd.DataFrame, duration_col: str) -> Dict[str, Any]:
    """Descriptive stats for a duration column (in hours)."""
    if df.empty or duration_col not in df.columns:
        return {"avg": 0.0, "median": 0.0, "p90": 0.0, "p95": 0.0}
    series = df[duration_col].dropna()
    if series.empty:
        return {"avg": 0.0, "median": 0.0, "p90": 0.0, "p95": 0.0}
    return {
        "avg": round(float(series.mean()), 2),
        "median": round(float(series.median()), 2),
        "p90": round(float(np.percentile(series, 90)), 2),
        "p95": round(float(np.percentile(series, 95)), 2),
    }


# ---------------------------------------------------------------------------
# 4. Incident MTTR Trend
# ---------------------------------------------------------------------------

# Function: incident_mttr_trend
def incident_mttr_trend(
    incidents_df: pd.DataFrame, months: int = 12
) -> List[Dict[str, Any]]:
    """Monthly MTTR statistics for incidents over the last N months."""
    periods = _last_n_months(months)

    if incidents_df.empty or "month_year" not in incidents_df.columns:
        return [
            {"month": p, "avg_mttr_hours": 0.0, "p50_hours": 0.0, "p90_hours": 0.0, "count": 0}
            for p in periods
        ]

    result = []
    for p in periods:
        subset = incidents_df[incidents_df["month_year"].astype(str) == p]
        if subset.empty or "resolution_hours" not in subset.columns:
            result.append({"month": p, "avg_mttr_hours": 0.0, "p50_hours": 0.0, "p90_hours": 0.0, "count": 0})
            continue
        rh = subset["resolution_hours"].dropna()
        result.append({
            "month": p,
            "avg_mttr_hours": round(float(rh.mean()), 2) if not rh.empty else 0.0,
            "p50_hours": round(float(rh.median()), 2) if not rh.empty else 0.0,
            "p90_hours": round(float(np.percentile(rh, 90)), 2) if not rh.empty else 0.0,
            "count": int(len(subset)),
        })
    return result


# ---------------------------------------------------------------------------
# 5. Application Hotspots
# ---------------------------------------------------------------------------

_UNKNOWN_VALUES = {"unknown", "", "nan", "none", "n/a", "not set", "-"}


# Function: application_hotspots
def application_hotspots(
    incidents_df: pd.DataFrame, top_n: int = 10
) -> List[Dict[str, Any]]:
    """Top N applications by incident count, with fallback columns to avoid 'Unknown'."""
    if incidents_df.empty:
        return []

    # Try each column in order; require meaningful (non-Unknown) values
    app_col = None
    for col in [
        "u_application_name", "business_service", "cmdb_ci",
        "assignment_group", "category", "subcategory",
    ]:
        if col not in incidents_df.columns:
            continue
        series = incidents_df[col].astype(str).str.strip()
        meaningful = series[~series.str.lower().isin(_UNKNOWN_VALUES)]
        if len(meaningful) >= max(1, len(incidents_df) * 0.05):
            app_col = col
            break

    if app_col is None:
        return []

    df = incidents_df.copy()
    df["_app"] = df[app_col].astype(str).str.strip()
    df = df[~df["_app"].str.lower().isin(_UNKNOWN_VALUES)]

    if df.empty:
        return []

    grouped = df.groupby("_app").agg(
        count=("_app", "size"),
        avg_mttr_hours=("resolution_hours", "mean") if "resolution_hours" in df.columns else ("_app", "size"),
    ).reset_index()

    if "resolution_hours" not in df.columns:
        grouped["avg_mttr_hours"] = 0.0

    grouped = grouped.sort_values("count", ascending=False).head(top_n)
    total = len(incidents_df)

    result = []
    for _, row in grouped.iterrows():
        result.append({
            "application": row["_app"],
            "count": int(row["count"]),
            "avg_mttr_hours": round(float(row["avg_mttr_hours"]) if pd.notna(row["avg_mttr_hours"]) else 0.0, 2),
            "pct_of_total": round(float(row["count"] / max(total, 1)) * 100, 2),
        })
    return result


# ---------------------------------------------------------------------------
# 6. Assignment Group Hotspots
# ---------------------------------------------------------------------------

# Function: assignment_group_hotspots
def assignment_group_hotspots(
    incidents_df: pd.DataFrame,
    changes_df: pd.DataFrame,
    sr_df: pd.DataFrame,
    top_n: int = 10,
) -> List[Dict[str, Any]]:
    """Top N assignment groups by combined ticket volume."""

    # Function: _group_counts
    def _group_counts(df: pd.DataFrame) -> Dict[str, int]:
        if df.empty or "assignment_group" not in df.columns:
            return {}
        counts = (
            df["assignment_group"]
            .astype(str)
            .str.strip()
            .value_counts()
            .to_dict()
        )
        return {k: v for k, v in counts.items() if k.lower() not in ("nan", "", "none")}

    inc_cnt = _group_counts(incidents_df)
    chg_cnt = _group_counts(changes_df)
    sr_cnt = _group_counts(sr_df)

    all_groups = set(inc_cnt) | set(chg_cnt) | set(sr_cnt)
    rows = []
    for grp in all_groups:
        inc = inc_cnt.get(grp, 0)
        chg = chg_cnt.get(grp, 0)
        sr = sr_cnt.get(grp, 0)
        rows.append({
            "group": grp,
            "incident_count": inc,
            "change_count": chg,
            "sr_count": sr,
            "total": inc + chg + sr,
        })

    rows.sort(key=lambda r: r["total"], reverse=True)
    return rows[:top_n]


# ---------------------------------------------------------------------------
# 7. Change Risk Summary
# ---------------------------------------------------------------------------

# Function: change_risk_summary
def change_risk_summary(changes_df: pd.DataFrame) -> Dict[str, Any]:
    """Change management risk and performance summary."""
    if changes_df.empty:
        return {
            "by_type": {"Normal": 0, "Standard": 0, "Emergency": 0},
            "emergency_pct": 0.0, "expedited_pct": 0.0, "rescheduled_pct": 0.0,
            "avg_impl_hours": 0.0, "implementation_success_pct": 0.0,
        }

    total = len(changes_df)

    # Function: _type_count
    def _type_count(keyword: str) -> int:
        if "type" not in changes_df.columns:
            return 0
        return int(changes_df["type"].astype(str).str.lower().str.contains(keyword).sum())

    normal_cnt = _type_count("normal")
    standard_cnt = _type_count("standard")
    emergency_cnt = _type_count("emergency")

    emergency_pct = round(emergency_cnt / max(total, 1) * 100, 2)

    # Expedited: changes where start_date < opened_at + 2 days (fast-tracked)
    expedited_pct = 0.0
    if "start_date" in changes_df.columns and "opened_at" in changes_df.columns:
        diff = (changes_df["start_date"] - changes_df["opened_at"]).dt.total_seconds() / 3600
        expedited_cnt = int((diff < 48).sum())
        expedited_pct = round(expedited_cnt / max(total, 1) * 100, 2)

    # Rescheduled: actual_start > start_date
    rescheduled_pct = 0.0
    if "actual_start" in changes_df.columns and "start_date" in changes_df.columns:
        rescheduled_cnt = int((changes_df["actual_start"] > changes_df["start_date"]).sum())
        rescheduled_pct = round(rescheduled_cnt / max(total, 1) * 100, 2)

    avg_impl_hours = 0.0
    if "implementation_hours" in changes_df.columns:
        avg_impl_hours = round(_safe_mean(changes_df["implementation_hours"]), 2)

    # Implementation success: u_implementation_result or close_code == "successful"
    success_pct = 0.0
    for col in ["u_implementation_result", "close_code", "review_status"]:
        if col in changes_df.columns:
            ok = changes_df[col].astype(str).str.lower().str.contains("success|complete|implemented", na=False)
            success_pct = round(float(ok.mean()) * 100, 2)
            break

    return {
        "by_type": {
            "Normal": normal_cnt,
            "Standard": standard_cnt,
            "Emergency": emergency_cnt,
        },
        "emergency_pct": emergency_pct,
        "expedited_pct": expedited_pct,
        "rescheduled_pct": rescheduled_pct,
        "avg_impl_hours": avg_impl_hours,
        "implementation_success_pct": success_pct,
    }


# ---------------------------------------------------------------------------
# 8. Change Volume Trend
# ---------------------------------------------------------------------------

# Function: change_volume_trend
def change_volume_trend(
    changes_df: pd.DataFrame, months: int = 12
) -> List[Dict[str, Any]]:
    """Monthly change counts broken down by Normal / Standard / Emergency."""
    periods = _last_n_months(months)

    if changes_df.empty:
        return [
            {"month": p, "normal": 0, "standard": 0, "emergency": 0, "total": 0}
            for p in periods
        ]

    df = changes_df.copy()
    if "month_year" not in df.columns:
        return [
            {"month": p, "normal": 0, "standard": 0, "emergency": 0, "total": 0}
            for p in periods
        ]

    df["_period"] = df["month_year"].astype(str)
    df["_type"] = df["type"].astype(str).str.lower() if "type" in df.columns else "normal"

    result = []
    for p in periods:
        sub = df[df["_period"] == p]
        normal = int(sub["_type"].str.contains("normal").sum()) if not sub.empty else 0
        standard = int(sub["_type"].str.contains("standard").sum()) if not sub.empty else 0
        emergency = int(sub["_type"].str.contains("emergency").sum()) if not sub.empty else 0
        total = len(sub)
        result.append({
            "month": p,
            "normal": normal,
            "standard": standard,
            "emergency": emergency,
            "total": total,
        })
    return result


# ---------------------------------------------------------------------------
# 9. SR / Inquiry Summary
# ---------------------------------------------------------------------------

# Function: sr_inquiry_summary
def sr_inquiry_summary(sr_df: pd.DataFrame) -> Dict[str, Any]:
    """Summary statistics for service requests and inquiries."""
    if sr_df.empty:
        return {
            "total": 0, "avg_closure_hours": 0.0, "median_closure_hours": 0.0,
            "top_categories": [], "backlog_count": 0,
        }

    total = len(sr_df)
    avg_closure = 0.0
    median_closure = 0.0
    if "closure_hours" in sr_df.columns:
        avg_closure = round(_safe_mean(sr_df["closure_hours"]), 2)
        median_closure = round(_safe_median(sr_df["closure_hours"]), 2)

    # Top categories
    top_cats: List[Dict[str, Any]] = []
    for col in ["u_request_category", "cat_item", "u_request_type"]:
        if col in sr_df.columns and sr_df[col].notna().any():
            cats = (
                sr_df[col]
                .astype(str)
                .str.strip()
                .value_counts()
                .head(10)
                .reset_index()
            )
            cats.columns = ["category", "count"]
            top_cats = cats.to_dict(orient="records")
            break

    # Backlog: tickets where state is not Closed/Resolved/Cancelled
    backlog_count = 0
    if "state" in sr_df.columns:
        closed_states = {"closed", "resolved", "cancelled", "4", "6", "7"}
        backlog_count = int(
            (~sr_df["state"].astype(str).str.lower().isin(closed_states)).sum()
        )

    return {
        "total": total,
        "avg_closure_hours": avg_closure,
        "median_closure_hours": median_closure,
        "top_categories": top_cats,
        "backlog_count": backlog_count,
    }


# ---------------------------------------------------------------------------
# 10. Ageing Analysis
# ---------------------------------------------------------------------------

# Function: ageing_analysis
def ageing_analysis(
    df: pd.DataFrame, date_col: str = "opened_at"
) -> Dict[str, int]:
    """
    Bucket open tickets by age since opening.
    Only considers tickets that appear to still be open
    (state not in closed/resolved/cancelled).
    """
    if df.empty or date_col not in df.columns:
        return {"lt_7d": 0, "7_30d": 0, "30_90d": 0, "gt_90d": 0}

    now = pd.Timestamp.now(tz="UTC")

    # Filter open tickets
    if "state" in df.columns:
        closed_states = {"closed", "resolved", "cancelled", "4", "6", "7"}
        open_df = df[~df["state"].astype(str).str.lower().isin(closed_states)].copy()
    else:
        open_df = df.copy()

    if open_df.empty:
        return {"lt_7d": 0, "7_30d": 0, "30_90d": 0, "gt_90d": 0}

    # Ensure the date column is timezone-aware
    ts = pd.to_datetime(open_df[date_col], errors="coerce", utc=True)
    age_days = (now - ts).dt.days

    return {
        "lt_7d": int((age_days < 7).sum()),
        "7_30d": int(((age_days >= 7) & (age_days < 30)).sum()),
        "30_90d": int(((age_days >= 30) & (age_days < 90)).sum()),
        "gt_90d": int((age_days >= 90).sum()),
    }


# ---------------------------------------------------------------------------
# 11. Priority Distribution
# ---------------------------------------------------------------------------

# Function: priority_distribution
def priority_distribution(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Count and percentage breakdown by priority."""
    if df.empty or "priority" not in df.columns:
        return []

    total = len(df)
    counts = df["priority"].astype(str).value_counts().reset_index()
    counts.columns = ["priority", "count"]
    result = []
    for _, row in counts.iterrows():
        result.append({
            "priority": row["priority"],
            "count": int(row["count"]),
            "pct": round(float(row["count"] / max(total, 1)) * 100, 2),
        })
    return result


# ---------------------------------------------------------------------------
# 12. Leadership Insights Generator
# ---------------------------------------------------------------------------

# Function: _insight
def _insight(text: str, level: str = "info") -> Dict[str, str]:
    return {"text": text, "level": level}


# Function: _total_tickets_insight
def _total_tickets_insight(summary: Dict[str, Any]) -> Optional[Dict[str, str]]:
    total = summary.get("total_tickets", 0)
    if not total:
        return None
    return _insight(f"{total:,} total ITSM tickets managed across incidents, changes, and service requests.")


# Function: _sla_compliance_insight
def _sla_compliance_insight(summary: Dict[str, Any]) -> Optional[Dict[str, str]]:
    sla = summary.get("sla_compliance_pct", 0.0)
    if not sla:
        return None
    if sla >= 95:
        return _insight(f"SLA compliance at {sla:.1f}% — exceeds the 95% target.", "good")
    if sla >= 85:
        return _insight(f"SLA compliance at {sla:.1f}% — approaching threshold; monitor closely.", "warn")
    return _insight(f"SLA compliance at {sla:.1f}% — below target; immediate action required.", "critical")


# Function: _mttr_insight
def _mttr_insight(summary: Dict[str, Any]) -> Optional[Dict[str, str]]:
    mttr = summary.get("avg_mttr_hours", 0.0)
    if not mttr:
        return None
    if mttr < 24:
        return _insight(f"Average incident MTTR of {mttr:.1f}h — within the 24h target.", "good")
    if mttr < 72:
        return _insight(f"Average incident MTTR of {mttr:.1f}h — elevated; review resolution workflows.", "warn")
    return _insight(f"Average incident MTTR of {mttr:.1f}h — significantly above target; escalate.", "critical")


# Function: _emergency_change_insight
def _emergency_change_insight(summary: Dict[str, Any]) -> Optional[Dict[str, str]]:
    emg_pct = summary.get("emergency_change_pct", 0.0)
    if not emg_pct:
        return None
    if emg_pct < 5:
        return _insight(f"Emergency changes at {emg_pct:.1f}% — well-controlled change governance.", "good")
    if emg_pct < 15:
        return _insight(f"Emergency changes at {emg_pct:.1f}% — review CAB authorisation frequency.", "warn")
    return _insight(f"Emergency changes at {emg_pct:.1f}% — high risk; strengthen change governance.", "critical")


# Function: _executive_insights
def _executive_insights(summary: Dict[str, Any]) -> List[Dict[str, str]]:
    builders = (
        _total_tickets_insight,
        _sla_compliance_insight,
        _mttr_insight,
        _emergency_change_insight,
    )
    return [item for item in (build(summary) for build in builders) if item]


# Function: _incident_total_insight
def _incident_total_insight(inc_summary: Dict[str, Any]) -> Optional[Dict[str, str]]:
    inc_total = inc_summary.get("total_incidents", 0)
    if not inc_total:
        return None
    return _insight(f"{inc_total:,} incidents recorded in the analysis period.")


# Function: _incident_sla_insight
def _incident_sla_insight(inc_summary: Dict[str, Any]) -> Optional[Dict[str, str]]:
    inc_sla = inc_summary.get("incident_sla_pct", 0.0)
    if not inc_sla:
        return None
    level = "good" if inc_sla >= 95 else ("warn" if inc_sla >= 85 else "critical")
    return _insight(f"Incident SLA compliance: {inc_sla:.1f}%.", level)


# Function: _incident_cycle_time_insight
def _incident_cycle_time_insight(incident_data: Dict[str, Any]) -> Optional[Dict[str, str]]:
    inc_ct = incident_data.get("cycle_time", {})
    inc_avg = inc_ct.get("avg", 0.0)
    if not inc_avg:
        return None
    inc_p90 = inc_ct.get("p90", 0.0)
    level = "good" if inc_avg < 24 else ("warn" if inc_avg < 72 else "critical")
    return _insight(f"Mean time to resolve: {inc_avg:.1f}h (P90: {inc_p90:.1f}h).", level)


# Function: _incident_priority_insight
def _incident_priority_insight(incident_data: Dict[str, Any]) -> Optional[Dict[str, str]]:
    prio_dist = incident_data.get("priority_dist", [])
    high_keywords = {"1 - critical", "2 - high", "high", "critical", "1", "2"}
    high_items = [p for p in prio_dist if str(p.get("priority", "")).lower() in high_keywords]
    if not high_items:
        return None
    high_count = sum(p.get("count", 0) for p in high_items)
    high_pct = sum(p.get("pct", 0.0) for p in high_items)
    level = "warn" if high_pct > 30 else "info"
    return _insight(f"{high_pct:.1f}% of incidents are high/critical priority ({high_count:,} tickets).", level)


# Function: _incident_hotspot_insight
def _incident_hotspot_insight(hotspots: List[Dict[str, Any]]) -> Optional[Dict[str, str]]:
    if not hotspots:
        return None
    top = hotspots[0]
    app_name = top.get("application", "Unknown")
    app_count = top.get("count", 0)
    app_pct = top.get("pct_of_total", 0.0)
    app_mttr = top.get("avg_mttr_hours", 0.0)
    level = "warn" if app_pct > 20 else "info"
    return _insight(
        f"Top hotspot: '{app_name}' — {app_count:,} incidents ({app_pct:.1f}% of total"
        + (f", avg MTTR {app_mttr:.1f}h" if app_mttr else "") + ").", level
    )


# Function: _incident_insights
def _incident_insights(incident_data: Dict[str, Any], hotspots: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    inc_summary = incident_data.get("summary", {})
    candidates = [
        _incident_total_insight(inc_summary),
        _incident_sla_insight(inc_summary),
        _incident_cycle_time_insight(incident_data),
        _incident_priority_insight(incident_data),
        _incident_hotspot_insight(hotspots),
    ]
    return [item for item in candidates if item]


# Function: _change_emergency_insight
def _change_emergency_insight(chg_risk: Dict[str, Any]) -> Optional[Dict[str, str]]:
    chg_emg = chg_risk.get("emergency_pct", 0.0)
    if not chg_emg:
        return None
    level = "good" if chg_emg < 5 else ("warn" if chg_emg < 15 else "critical")
    return _insight(f"Emergency changes: {chg_emg:.1f}% of total change volume.", level)


# Function: _change_success_insight
def _change_success_insight(chg_risk: Dict[str, Any]) -> Optional[Dict[str, str]]:
    success = chg_risk.get("implementation_success_pct", 0.0)
    if not success:
        return None
    level = "good" if success >= 90 else ("warn" if success >= 75 else "critical")
    return _insight(f"Change implementation success rate: {success:.1f}%.", level)


# Function: _change_avg_impl_insight
def _change_avg_impl_insight(chg_risk: Dict[str, Any]) -> Optional[Dict[str, str]]:
    avg_impl = chg_risk.get("avg_impl_hours", 0.0)
    if not avg_impl:
        return None
    return _insight(f"Average change implementation time: {avg_impl:.1f}h.")


# Function: _change_p90_insight
def _change_p90_insight(chg_ct: Dict[str, Any]) -> Optional[Dict[str, str]]:
    chg_p90 = chg_ct.get("p90", 0.0)
    if not chg_p90:
        return None
    return _insight(f"P90 cycle time: {chg_p90:.1f}h — 90% of changes complete within this window.")


# Function: _change_mix_insight
def _change_mix_insight(chg_risk: Dict[str, Any]) -> Optional[Dict[str, str]]:
    by_type = chg_risk.get("by_type", {})
    if not by_type:
        return None
    total_chg = sum(by_type.values())
    if not total_chg:
        return None
    parts = [f"{k}: {v:,} ({v / total_chg * 100:.1f}%)" for k, v in by_type.items() if v > 0]
    return _insight(f"Change mix — {', '.join(parts)}.")


# Function: _change_insights
def _change_insights(change_data: Dict[str, Any]) -> List[Dict[str, str]]:
    chg_risk = change_data.get("risk", {})
    chg_ct = change_data.get("cycle_time", {})
    candidates = [
        _change_emergency_insight(chg_risk),
        _change_success_insight(chg_risk),
        _change_avg_impl_insight(chg_risk),
        _change_p90_insight(chg_ct),
        _change_mix_insight(chg_risk),
    ]
    return [item for item in candidates if item]


# Function: _service_request_insights
def _service_request_insights(sr_data: Dict[str, Any]) -> List[Dict[str, str]]:
    service_requests: List[Dict[str, str]] = []
    sr_sum = sr_data.get("summary", {})
    sr_total = sr_sum.get("total", 0)
    sr_backlog = sr_sum.get("backlog_count", 0)
    if sr_total:
        backlog_pct = sr_backlog / max(sr_total, 1) * 100
        level = "warn" if backlog_pct > 30 else ("critical" if backlog_pct > 50 else "info")
        service_requests.append(_insight(
            f"{sr_total:,} service requests total; {sr_backlog:,} open ({backlog_pct:.1f}% backlog).", level
        ))

    sr_avg = sr_sum.get("avg_closure_hours", 0.0)
    sr_med = sr_sum.get("median_closure_hours", 0.0)
    if sr_avg:
        level = "good" if sr_avg < 48 else ("warn" if sr_avg < 120 else "critical")
        service_requests.append(_insight(
            f"Avg closure time: {sr_avg:.1f}h (median: {sr_med:.1f}h).", level
        ))

    top_cats = sr_sum.get("top_categories", [])
    if top_cats and sr_total:
        top_cat = top_cats[0]
        cat_name = top_cat.get("category", "Unknown")
        cat_count = top_cat.get("count", 0)
        cat_pct = cat_count / max(sr_total, 1) * 100
        service_requests.append(_insight(
            f"Top SR category: '{cat_name}' — {cat_count:,} tickets ({cat_pct:.1f}% of total)."
        ))

    return service_requests


# Function: generate_leadership_insights
def generate_leadership_insights(
    summary: Dict[str, Any],
    incident_data: Dict[str, Any],
    change_data: Dict[str, Any],
    sr_data: Dict[str, Any],
    hotspots: List[Dict[str, Any]],
) -> Dict[str, List[Dict[str, str]]]:
    """
    Generate colour-coded leadership insight bullets per domain.
    Returns {"executive": [...], "incidents": [...], "changes": [...], "service_requests": [...]}
    Each item: {"text": str, "level": "good"|"warn"|"critical"|"info"}
    """
    return {
        "executive": _executive_insights(summary),
        "incidents": _incident_insights(incident_data, hotspots),
        "changes": _change_insights(change_data),
        "service_requests": _service_request_insights(sr_data),
    }


# ---------------------------------------------------------------------------
# 13. Repeat Incidents Analysis
# ---------------------------------------------------------------------------

# Function: _build_repeat_groups
def _build_repeat_groups(incidents_df: pd.DataFrame) -> Dict[str, int]:
    repeat_groups = {}
    if "short_description" in incidents_df.columns:
        desc_counts = incidents_df["short_description"].astype(str).value_counts()
        repeat_groups = desc_counts[desc_counts > 1].to_dict()

    if "category" in incidents_df.columns and "subcategory" in incidents_df.columns:
        cat_sub = (incidents_df["category"].astype(str) + " | " +
                   incidents_df["subcategory"].astype(str)).value_counts()
        for key, count in cat_sub[cat_sub > 1].items():
            if key not in repeat_groups:
                repeat_groups[key] = count

    return repeat_groups


# Function: _top_repeat_problems
def _top_repeat_problems(incidents_df: pd.DataFrame, repeat_groups: Dict[str, int]) -> List[Dict[str, Any]]:
    top_repeats = []
    has_desc_col = "short_description" in incidents_df.columns
    for desc, count in sorted(repeat_groups.items(), key=lambda x: x[1], reverse=True)[:10]:
        subset = incidents_df[incidents_df["short_description"].astype(str) == desc] if has_desc_col else pd.DataFrame()
        avg_mttr = 0.0
        if not subset.empty and "resolution_hours" in subset.columns:
            avg_mttr = round(_safe_mean(subset["resolution_hours"]), 2)

        top_repeats.append({
            "description": str(desc)[:100],
            "occurrences": int(count),
            "avg_mttr_hours": avg_mttr
        })
    return top_repeats


# Function: _repeat_incidents_for_month
def _repeat_incidents_for_month(subset: pd.DataFrame) -> int:
    desc_counts = subset["short_description"].astype(str).value_counts()
    repeats = desc_counts[desc_counts > 1].to_dict()
    return sum(count - 1 for count in repeats.values())


# Function: _repeat_trend_by_month
def _repeat_trend_by_month(incidents_df: pd.DataFrame) -> List[Dict[str, Any]]:
    repeat_trend = []
    if "month_year" not in incidents_df.columns:
        return repeat_trend

    for p in _last_n_months(6):
        subset = incidents_df[incidents_df["month_year"].astype(str) == p]
        if subset.empty:
            continue
        repeat_trend.append({
            "month": p,
            "repeat_incidents": _repeat_incidents_for_month(subset),
            "total_incidents": len(subset)
        })
    return repeat_trend


# Function: repeat_incidents_analysis
def repeat_incidents_analysis(incidents_df: pd.DataFrame) -> Dict[str, Any]:
    """Identify and analyze repeat incidents and recurring problems."""
    if incidents_df.empty:
        return {
            "total_incidents": 0,
            "repeat_incidents": 0,
            "repeat_pct": 0.0,
            "top_repeats": [],
            "repeat_trend": []
        }

    total = len(incidents_df)
    repeat_groups = _build_repeat_groups(incidents_df)
    repeat_count = sum(c - 1 for c in repeat_groups.values())
    repeat_pct = round(repeat_count / max(total, 1) * 100, 2) if total > 0 else 0.0

    return {
        "total_incidents": total,
        "repeat_incidents": repeat_count,
        "repeat_pct": repeat_pct,
        "top_repeats": _top_repeat_problems(incidents_df, repeat_groups),
        "repeat_trend": _repeat_trend_by_month(incidents_df)
    }


# ---------------------------------------------------------------------------
# 14. RCA & Ownership Tracking
# ---------------------------------------------------------------------------

# Function: rca_ownership_analysis
def rca_ownership_analysis(incidents_df: pd.DataFrame) -> Dict[str, Any]:
    """Root Cause Analysis and ownership metrics."""
    if incidents_df.empty:
        return {
            "rca_identified_pct": 0.0,
            "rca_identified_count": 0,
            "top_root_causes": [],
            "ownership_distribution": [],
            "rca_closure_time_avg": 0.0
        }
    
    total = len(incidents_df)
    
    # Count incidents with RCA
    rca_count = 0
    root_causes = {}
    if "cause" in incidents_df.columns or "root_cause" in incidents_df.columns:
        rca_col = "root_cause" if "root_cause" in incidents_df.columns else "cause"
        rca_count = int((incidents_df[rca_col].notna() & 
                        (incidents_df[rca_col].astype(str).str.lower() != "unknown")).sum())
        
        # Top root causes
        root_cause_counts = (incidents_df[rca_col].astype(str)
                            .value_counts()
                            .head(10)
                            .to_dict())
        root_causes = root_cause_counts
    
    rca_pct = round(rca_count / max(total, 1) * 100, 2)
    
    # Top root causes
    top_root_causes = [
        {
            "cause": str(k)[:100],
            "count": int(v),
            "pct": round(v / max(total, 1) * 100, 2)
        }
        for k, v in sorted(root_causes.items(), key=lambda x: x[1], reverse=True)[:8]
    ]
    
    # Ownership distribution
    ownership_dist = []
    if "assigned_to" in incidents_df.columns:
        assigned_counts = incidents_df["assigned_to"].astype(str).value_counts().head(10)
        for assigned, count in assigned_counts.items():
            if assigned.lower() not in ("nan", "unknown", ""):
                ownership_dist.append({
                    "assigned_to": str(assigned)[:50],
                    "count": int(count),
                    "pct": round(count / max(total, 1) * 100, 2)
                })
    
    # Average closure time for incidents with RCA vs without
    rca_closure_time = 0.0
    if "resolution_hours" in incidents_df.columns and "root_cause" in incidents_df.columns:
        rca_df = incidents_df[incidents_df["root_cause"].notna()]
        if not rca_df.empty:
            rca_closure_time = round(_safe_mean(rca_df["resolution_hours"]), 2)
    
    return {
        "rca_identified_pct": rca_pct,
        "rca_identified_count": rca_count,
        "top_root_causes": top_root_causes,
        "ownership_distribution": ownership_dist,
        "rca_closure_time_avg": rca_closure_time
    }


# ---------------------------------------------------------------------------
# 15. Preventive Maintenance & Planned Changes
# ---------------------------------------------------------------------------

# Function: preventive_maintenance_analysis
def preventive_maintenance_analysis(changes_df: pd.DataFrame) -> Dict[str, Any]:
    """Analyze planned vs executed maintenance and preventive actions."""
    if changes_df.empty:
        return {
            "total_changes": 0,
            "planned_maintenance": 0,
            "preventive_maintenance": 0,
            "emergency_changes": 0,
            "maintenance_execution_rate": 0.0,
            "missed_preventive": 0,
            "automation_coverage_pct": 0.0
        }
    
    total = len(changes_df)
    
    # Identify maintenance changes
    planned_maint = 0
    preventive_maint = 0
    emergency = 0
    
    if "type" in changes_df.columns:
        planned_maint = int(changes_df["type"].astype(str).str.lower().str.contains("planned|maintenance", na=False).sum())
        preventive_maint = int(changes_df["type"].astype(str).str.lower().str.contains("preventive", na=False).sum())
        emergency = int(changes_df["type"].astype(str).str.lower().str.contains("emergency", na=False).sum())
    
    if "category" in changes_df.columns:
        if planned_maint == 0:
            planned_maint = int(changes_df["category"].astype(str).str.lower().str.contains("maintenance", na=False).sum())
    
    # Execution rate - changes that completed successfully
    execution_rate = 0.0
    if "state" in changes_df.columns:
        completed_states = {"completed", "closed", "successful", "implemented"}
        completed = int(changes_df["state"].astype(str).str.lower().isin(completed_states).sum())
        execution_rate = round(completed / max(total, 1) * 100, 2)
    
    # Missed preventive actions - changes scheduled but not completed
    missed_preventive = 0
    if "start_date" in changes_df.columns and "actual_start" in changes_df.columns:
        now = pd.Timestamp.now(tz="UTC")
        overdue = changes_df[(changes_df["start_date"] < now) & 
                            (changes_df["actual_start"].isna() | (changes_df["actual_start"] > changes_df["start_date"]))]
        missed_preventive = len(overdue)
    
    # Automation coverage - changes with automated implementation
    automation_pct = 0.0
    if "u_automation_flag" in changes_df.columns:
        automated = int(changes_df["u_automation_flag"].astype(str).str.lower().isin(["true", "yes", "1"]).sum())
        automation_pct = round(automated / max(total, 1) * 100, 2)
    
    return {
        "total_changes": total,
        "planned_maintenance": planned_maint,
        "preventive_maintenance": preventive_maint,
        "emergency_changes": emergency,
        "maintenance_execution_rate": execution_rate,
        "missed_preventive": missed_preventive,
        "automation_coverage_pct": automation_pct
    }


# ---------------------------------------------------------------------------
# 16. Ad-hoc Work vs BAU Analysis
# ---------------------------------------------------------------------------

# Function: adhoc_vs_bau_analysis
def adhoc_vs_bau_analysis(sr_df: pd.DataFrame, incidents_df: pd.DataFrame) -> Dict[str, Any]:
    """Analyze ad-hoc / enhancement work vs BAU (Business as Usual)."""
    if sr_df.empty and incidents_df.empty:
        return {
            "total_tickets": 0,
            "bau_count": 0,
            "adhoc_count": 0,
            "enhancement_count": 0,
            "bau_pct": 0.0,
            "adhoc_pct": 0.0,
            "enhancement_pct": 0.0,
            "aging_alerts": []
        }
    
    total_sr = len(sr_df)
    total_inc = len(incidents_df)
    total = total_sr + total_inc
    
    # Categorize service requests
    bau_count = 0
    adhoc_count = 0
    enhancement_count = 0
    
    if not sr_df.empty and "u_request_type" in sr_df.columns:
        bau_count = int(sr_df["u_request_type"].astype(str).str.lower().str.contains("standard|incident", na=False).sum())
        adhoc_count = int(sr_df["u_request_type"].astype(str).str.lower().str.contains("adhoc|ad-hoc|unplanned", na=False).sum())
        enhancement_count = int(sr_df["u_request_type"].astype(str).str.lower().str.contains("enhancement|improvement", na=False).sum())
    
    # Fallback to category if type not available
    if bau_count == 0 and not sr_df.empty and "category" in sr_df.columns:
        bau_count = int(sr_df["category"].astype(str).str.lower().str.contains("standard|incident", na=False).sum())
        adhoc_count = int(sr_df["category"].astype(str).str.lower().str.contains("adhoc|ad-hoc", na=False).sum())
        enhancement_count = int(sr_df["category"].astype(str).str.lower().str.contains("enhancement", na=False).sum())
    
    # Include incidents in ad-hoc
    adhoc_count += total_inc
    
    bau_pct = round(bau_count / max(total, 1) * 100, 2)
    adhoc_pct = round(adhoc_count / max(total, 1) * 100, 2)
    enhancement_pct = round(enhancement_count / max(total, 1) * 100, 2)
    
    # Aging alerts - work items aging beyond thresholds
    aging_alerts = []
    age_analysis_sr = ageing_analysis(sr_df)
    age_analysis_inc = ageing_analysis(incidents_df)
    
    if age_analysis_sr.get("30_90d", 0) > 0:
        aging_alerts.append({
            "severity": "warning",
            "message": f"⚠ {age_analysis_sr['30_90d']} service requests aging 30-90 days"
        })
    if age_analysis_sr.get("gt_90d", 0) > 0:
        aging_alerts.append({
            "severity": "critical",
            "message": f"🔴 {age_analysis_sr['gt_90d']} service requests exceeding 90 days!"
        })
    if age_analysis_inc.get("gt_90d", 0) > 0:
        aging_alerts.append({
            "severity": "critical",
            "message": f"🔴 {age_analysis_inc['gt_90d']} incidents exceeding 90 days!"
        })
    
    return {
        "total_tickets": total,
        "bau_count": bau_count,
        "adhoc_count": adhoc_count,
        "enhancement_count": enhancement_count,
        "bau_pct": bau_pct,
        "adhoc_pct": adhoc_pct,
        "enhancement_pct": enhancement_pct,
        "aging_alerts": aging_alerts
    }


# ---------------------------------------------------------------------------
# 17. SLA Breach Risk Analysis
# ---------------------------------------------------------------------------

# Function: _sla_breached_rows
def _sla_breached_rows(df: pd.DataFrame) -> List[Dict[str, Any]]:
    rows = []
    for _, row in df.iterrows():
        if "made_sla" in row:
            breached = not (str(row["made_sla"]).lower() in ["true", "1", "yes"])
            rows.append({"breached": breached, "month": row.get("month_year")})
    return rows


# Function: _sla_breach_trend
def _sla_breach_trend(combined_df: pd.DataFrame, periods: List[str]) -> List[Dict[str, Any]]:
    breach_trend = []
    if combined_df.empty or "month" not in combined_df.columns:
        return breach_trend

    for p in periods:
        subset = combined_df[combined_df["month"].astype(str) == p]
        if subset.empty:
            continue
        breach_trend.append({
            "month": p,
            "breach_pct": round(subset["breached"].astype(bool).mean() * 100, 2),
            "count": len(subset)
        })
    return breach_trend


# Function: _count_incident_risk_and_breach
def _count_incident_risk_and_breach(incidents_df: pd.DataFrame) -> tuple:
    at_risk = 0
    breached = 0
    for _, row in incidents_df.iterrows():
        # Simple heuristic: high priority tickets aging more than 8h are at risk
        if "resolution_hours" in row and "priority" in row:
            if row["resolution_hours"] > 8 and str(row["priority"]) in ["1", "2", "High", "Critical"]:
                at_risk += 1
        made_sla = row.get("made_sla")
        if made_sla and str(made_sla).lower() in ["false", "0", "no"]:
            breached += 1
    return at_risk, breached


# Function: _count_sr_risk_and_breach
def _count_sr_risk_and_breach(sr_df: pd.DataFrame) -> tuple:
    at_risk = 0
    breached = 0
    for _, row in sr_df.iterrows():
        if "closure_hours" in row and row["closure_hours"] > 24:
            at_risk += 1
        made_sla = row.get("made_sla")
        if made_sla and str(made_sla).lower() in ["false", "0", "no"]:
            breached += 1
    return at_risk, breached


# Function: _sla_trajectory
def _sla_trajectory(breach_trend: List[Dict[str, Any]]) -> str:
    if len(breach_trend) <= 2:
        return "stable"
    recent = breach_trend[-1]["breach_pct"]
    previous = breach_trend[-2]["breach_pct"]
    if recent > previous + 5:
        return "deteriorating"
    if recent < previous - 5:
        return "improving"
    return "stable"


# Function: sla_breach_risk_analysis
def sla_breach_risk_analysis(
    incidents_df: pd.DataFrame,
    sr_df: pd.DataFrame,
    months: int = 12
) -> Dict[str, Any]:
    """Analyze SLA breach trends and risk indicators."""
    if incidents_df.empty and sr_df.empty:
        return {
            "current_breach_risk_pct": 0.0,
            "breach_trend": [],
            "at_risk_tickets": 0,
            "breached_tickets": 0,
            "trajectory": "stable"
        }

    periods = _last_n_months(months)
    combined_df = pd.DataFrame(_sla_breached_rows(incidents_df) + _sla_breached_rows(sr_df))
    breach_trend = _sla_breach_trend(combined_df, periods)
    current_breach = round((combined_df["breached"].astype(bool).mean() * 100), 2) if not combined_df.empty else 0.0

    inc_at_risk, inc_breached = _count_incident_risk_and_breach(incidents_df)
    sr_at_risk, sr_breached = _count_sr_risk_and_breach(sr_df)

    return {
        "current_breach_risk_pct": current_breach,
        "breach_trend": breach_trend,
        "at_risk_tickets": inc_at_risk + sr_at_risk,
        "breached_tickets": inc_breached + sr_breached,
        "trajectory": _sla_trajectory(breach_trend)
    }


# ---------------------------------------------------------------------------
# 18. Transformation & Automation KPIs
# ---------------------------------------------------------------------------

# Function: _count_automated_tickets
def _count_automated_tickets(changes_df: pd.DataFrame, sr_df: pd.DataFrame) -> int:
    automated_count = 0
    for _, row in changes_df.iterrows():
        if "u_automation_flag" in row and str(row["u_automation_flag"]).lower() in ["true", "yes", "1"]:
            automated_count += 1
    for _, row in sr_df.iterrows():
        if "u_automated" in row and str(row["u_automated"]).lower() in ["true", "yes", "1"]:
            automated_count += 1
    return automated_count


# Function: _incident_deflection_pct
def _incident_deflection_pct(incidents_df: pd.DataFrame, sr_df: pd.DataFrame) -> float:
    if sr_df.empty or len(incidents_df) == 0:
        return 0.0
    # Higher SR:incident ratio = better deflection
    ratio = len(sr_df) / max(len(incidents_df), 1)
    return min(100.0, round((ratio / (ratio + 1)) * 100, 2))


# Function: _effort_reduction_pct
def _effort_reduction_pct(automated_count: int, total_tickets: int) -> float:
    if automated_count <= 0:
        return 0.0
    # Automated items typically resolve in <2h vs manual ~12h average
    automated_time = 2.0 * automated_count
    manual_time = 12.0 * (total_tickets - automated_count)
    total_possible_time = 12.0 * total_tickets
    actual_time = automated_time + manual_time
    return round(((total_possible_time - actual_time) / total_possible_time) * 100, 2)


# Function: _cost_takeout_estimate
def _cost_takeout_estimate(automated_count: int) -> float:
    # Rough: $200/day / 8 hours per hour saved, hours saved per automated ticket = 12h - 2h
    cost_per_hour = 25
    hour_savings = (12.0 - 2.0) * automated_count
    return round((hour_savings * cost_per_hour) / 1000, 1)  # In $1000s


# Function: _automation_opportunities
def _automation_opportunities(sr_df: pd.DataFrame) -> List[Dict[str, Any]]:
    opportunities = []
    if sr_df.empty or "u_request_type" not in sr_df.columns:
        return opportunities

    top_types = sr_df["u_request_type"].astype(str).value_counts().head(5)
    for sr_type, count in top_types.items():
        if str(sr_type).lower() not in ("nan", "unknown", ""):
            opportunities.append({
                "type": str(sr_type)[:60],
                "count": int(count),
                "automation_potential": "High" if count > 10 else "Medium"
            })
    return opportunities


# Function: transformation_kpis
def transformation_kpis(
    incidents_df: pd.DataFrame,
    changes_df: pd.DataFrame,
    sr_df: pd.DataFrame
) -> Dict[str, Any]:
    """Track transformation metrics: automation %, effort reduction, deflection."""
    if incidents_df.empty and changes_df.empty and sr_df.empty:
        return {
            "automation_pct": 0.0,
            "incident_deflection_pct": 0.0,
            "effort_reduction_pct": 0.0,
            "cost_takeout_estimate": 0.0,
            "automation_opportunities": []
        }

    total_tickets = len(incidents_df) + len(changes_df) + len(sr_df)
    automated_count = _count_automated_tickets(changes_df, sr_df)

    return {
        "automation_pct": round(automated_count / max(total_tickets, 1) * 100, 2),
        "incident_deflection_pct": _incident_deflection_pct(incidents_df, sr_df),
        "effort_reduction_pct": _effort_reduction_pct(automated_count, total_tickets),
        "cost_takeout_estimate": _cost_takeout_estimate(automated_count),
        "automation_opportunities": _automation_opportunities(sr_df)
    }


# ---------------------------------------------------------------------------
# 19. People & Capacity Dashboard
# ---------------------------------------------------------------------------

# Function: _collect_teams
def _collect_teams(incidents_df: pd.DataFrame, changes_df: pd.DataFrame, sr_df: pd.DataFrame) -> set:
    teams = set()
    col = "assignment_group"
    if col in incidents_df.columns:
        teams.update(incidents_df[col].astype(str).unique())
    if col in changes_df.columns:
        teams.update(changes_df[col].astype(str).unique())
    if col in sr_df.columns:
        teams.update(sr_df[col].astype(str).unique())
    return {t for t in teams if str(t).lower() not in ("nan", "unknown", "")}


# Function: _teams_for_df
def _teams_for_df(df: pd.DataFrame, ticket_type: str) -> List[Dict[str, str]]:
    entries = []
    for _, row in df.iterrows():
        if "assignment_group" not in row:
            continue
        team = str(row["assignment_group"])
        if team.lower() not in ("nan", "unknown", ""):
            entries.append({"team": team, "type": ticket_type})
    return entries


# Function: _workload_summary
def _workload_summary(workload_dist: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    team_stats = {}
    for item in workload_dist:
        team = item["team"]
        if team not in team_stats:
            team_stats[team] = {"Incident": 0, "Change": 0, "ServiceRequest": 0, "total": 0}
        team_stats[team][item["type"]] += 1
        team_stats[team]["total"] += 1

    return [
        {
            "team": team,
            "total_tickets": stats["total"],
            "incidents": stats["Incident"],
            "changes": stats["Change"],
            "service_requests": stats["ServiceRequest"]
        }
        for team, stats in sorted(team_stats.items(), key=lambda x: x[1]["total"], reverse=True)[:10]
    ]


# Function: _rebadged_resource_count
def _rebadged_resource_count(incidents_df: pd.DataFrame) -> int:
    if "assignment_group" not in incidents_df.columns:
        return 0
    rebadged_count = 0
    for _, row in incidents_df.iterrows():
        if "assigned_to" in row and str(row["assigned_to"]).lower() not in ("nan", ""):
            rebadged_count += 1 if str(row["assigned_to"]).lower().find("contract") >= 0 else 0
    return rebadged_count


# Function: people_capacity_metrics
def people_capacity_metrics(
    incidents_df: pd.DataFrame,
    changes_df: pd.DataFrame,
    sr_df: pd.DataFrame
) -> Dict[str, Any]:
    """Track team capacity, workload distribution, and resource utilization."""
    if incidents_df.empty and changes_df.empty and sr_df.empty:
        return {
            "total_staff_estimated": 0,
            "tickets_per_person": 0.0,
            "team_workload_distribution": [],
            "capacity_utilization_pct": 0.0,
            "rebadged_resources": 0,
            "avg_team_size": 0
        }

    num_teams = len(_collect_teams(incidents_df, changes_df, sr_df))

    # Estimate staff (rough: 1 person per team for capacity calculation)
    estimated_staff = max(num_teams, 1)
    total_tickets = len(incidents_df) + len(changes_df) + len(sr_df)
    tickets_per_person = round(total_tickets / max(estimated_staff, 1), 2)

    workload_dist = (
        _teams_for_df(incidents_df, "Incident")
        + _teams_for_df(changes_df, "Change")
        + _teams_for_df(sr_df, "ServiceRequest")
    )
    workload_summary = _workload_summary(workload_dist)

    # Capacity utilization (rough: <30% is underutilized, 30-70% optimal, >70% overutilized)
    optimal_capacity = 50  # tickets per person per month
    actual_capacity = tickets_per_person / 30  # per day
    capacity_util = min(100.0, round((actual_capacity / optimal_capacity) * 100, 2))

    return {
        "total_staff_estimated": estimated_staff,
        "tickets_per_person": tickets_per_person,
        "team_workload_distribution": workload_summary,
        "capacity_utilization_pct": capacity_util,
        "rebadged_resources": _rebadged_resource_count(incidents_df),
        "avg_team_size": num_teams
    }
