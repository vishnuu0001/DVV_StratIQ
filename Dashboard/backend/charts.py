# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Matplotlib chart rendering for the AI-Powered Digital Operations Cockpit.
# Date: 2025-08-09
# ---------------------------------------------------------------------------
"""
Matplotlib chart rendering for the AI-Powered Digital Operations Cockpit.

All render_* functions return PNG bytes (io.BytesIO content).
Dark theme is applied consistently across all charts.
"""

import io
import logging
import textwrap
from typing import Any, Dict, List, Optional

import matplotlib
matplotlib.use("Agg")  # non-interactive backend – must be before pyplot import
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker
import matplotlib.font_manager as fm
import numpy as np

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# CJK font setup — must run before any figure is created
# ---------------------------------------------------------------------------

# Function: _setup_cjk_font
def _setup_cjk_font() -> None:
    """
    Configure Matplotlib to use a CJK-capable font so Japanese / Chinese /
    Korean characters in ServiceNow ticket data render correctly instead of
    appearing as empty boxes (tofu).

    Priority order (Windows):
      1. MS Gothic  — ships with all Windows editions, full JIS/CJK coverage
      2. Yu Gothic  — higher quality, available on Win 8.1+
      3. Meiryo     — common on enterprise Windows
    Falls back silently to DejaVu Sans (ASCII-only) if none are found.
    """
    _CJK_CANDIDATES = [
        ("MS Gothic",  "msgothic.ttc"),
        ("Yu Gothic",  "YuGothR.ttc"),
        ("Yu Gothic",  "YuGothic-Regular.ttf"),
        ("Meiryo",     "meiryo.ttc"),
        ("Meiryo",     "Meiryo.ttf"),
    ]
    import os
    win_fonts = r"C:\Windows\Fonts"
    for name, filename in _CJK_CANDIDATES:
        path = os.path.join(win_fonts, filename)
        if os.path.exists(path):
            try:
                fm.fontManager.addfont(path)
                plt.rcParams["font.family"] = name
                plt.rcParams["font.sans-serif"] = [name, "DejaVu Sans"]
                logger.info("CJK font configured: %s (%s)", name, path)
                return
            except Exception as exc:
                logger.debug("Could not load %s: %s", path, exc)
    logger.warning("No CJK font found — non-ASCII labels may render as tofu")


_setup_cjk_font()

# ---------------------------------------------------------------------------
# Theme constants  (light / report theme — matches executive screenshots)
# ---------------------------------------------------------------------------

DARK_BG = "#ffffff"       # page / figure background — white
SURFACE = "#f8fafc"       # axes background — slate-50
GRID_COLOR = "#e2e8f0"    # grid lines — slate-200
TEXT_COLOR = "#0f172a"    # primary text — slate-900
MUTED_TEXT = "#64748b"    # secondary labels — slate-500
ACCENT = "#2563eb"        # primary accent — blue-600

# Palette matching the report screenshots
COLORS = [
    "#3b82f6",  # blue-500
    "#22c55e",  # green-500
    "#ef4444",  # red-500
    "#f97316",  # orange-500
    "#8b5cf6",  # violet-500
    "#06b6d4",  # cyan-500
    "#eab308",  # yellow-500
    "#ec4899",  # pink-500
]

PRIORITY_COLORS = {
    "High": "#ef4444",
    "Medium": "#f97316",
    "Low": "#22c55e",
    "Monitor": "#94a3b8",
}


# Function: _apply_theme
def _apply_theme() -> None:
    """Apply the light report-style rcParams to every new figure."""
    plt.rcParams.update({
        "figure.facecolor": DARK_BG,      # white
        "axes.facecolor": SURFACE,         # slate-50
        "axes.edgecolor": GRID_COLOR,      # slate-200
        "axes.labelcolor": TEXT_COLOR,     # slate-900
        "xtick.color": MUTED_TEXT,         # slate-500
        "ytick.color": MUTED_TEXT,
        "text.color": TEXT_COLOR,
        "grid.color": GRID_COLOR,
        "grid.alpha": 0.6,
        "legend.facecolor": DARK_BG,
        "legend.edgecolor": GRID_COLOR,
        "legend.framealpha": 0.8,
        "font.size": 11,
        "axes.titlesize": 13,
        "axes.titlecolor": TEXT_COLOR,
        "axes.titleweight": "bold",
        "axes.labelsize": 11,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "legend.fontsize": 10,
        "axes.spines.top": False,
        "axes.spines.right": False,
    })


# Function: _fig_to_bytes
def _fig_to_bytes(fig: plt.Figure) -> bytes:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=140, bbox_inches="tight", facecolor=DARK_BG)
    plt.close(fig)
    buf.seek(0)
    return buf.read()


# Function: _style_axis
def _style_axis(ax: plt.Axes, grid: bool = True) -> None:
    ax.set_facecolor(SURFACE)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_edgecolor(GRID_COLOR)
    ax.spines["bottom"].set_edgecolor(GRID_COLOR)
    if grid:
        ax.grid(True, color=GRID_COLOR, alpha=0.6, linewidth=0.8)
    ax.tick_params(colors=MUTED_TEXT, labelsize=10)
    ax.title.set_color(TEXT_COLOR)
    ax.xaxis.label.set_color(TEXT_COLOR)
    ax.yaxis.label.set_color(TEXT_COLOR)


# Function: _short_label
def _short_label(label: str, max_len: int = 22) -> str:
    """Truncate long labels for axis readability."""
    return label if len(label) <= max_len else label[:max_len - 1] + "…"


# ---------------------------------------------------------------------------
# 1. Executive Montage (3x3 grid)
# ---------------------------------------------------------------------------

# Function: render_executive_montage
def render_executive_montage(
    summary_kpis: Dict[str, Any],
    monthly_volume: List[Dict[str, Any]],
    hotspots: List[Dict[str, Any]],
    mttr_trend: List[Dict[str, Any]],
) -> bytes:
    """
    3x3 montage figure (15x10 inches) with:
    [0,0] Donut: tickets by type
    [0,1] Line: monthly volume trend
    [0,2] Horizontal bar: top 8 application hotspots
    [1,0] Bar: cycle time by type
    [1,1] Line: incident MTTR trend
    [1,2] Horizontal bar: top 8 assignment groups  (derived from hotspots)
    [2,0] Bar: change type distribution
    [2,1] KPI cards text panel
    [2,2] Horizontal bar: top automation priorities derived from hotspots
    """
    _apply_theme()
    fig, axes = plt.subplots(3, 3, figsize=(20, 13))
    fig.patch.set_facecolor(DARK_BG)
    fig.suptitle(
        "Digital Operations Cockpit – Executive Overview",
        color=TEXT_COLOR, fontsize=14, fontweight="bold", y=0.98,
    )

    # ---- [0,0] Donut: tickets by type -----------------------------------
    ax = axes[0][0]
    by_type = summary_kpis.get("by_type", {})
    labels = [k for k, v in by_type.items() if v > 0]
    values = [v for v in by_type.values() if v > 0]
    if values:
        wedges, texts, autotexts = ax.pie(
            values,
            labels=None,
            colors=COLORS[:len(values)],
            autopct="%1.1f%%",
            startangle=90,
            wedgeprops=dict(width=0.55, edgecolor=DARK_BG, linewidth=1.5),
            pctdistance=0.75,
        )
        for at in autotexts:
            at.set_color(DARK_BG)
            at.set_fontsize(7)
        ax.legend(labels, loc="lower center", fontsize=7, framealpha=0,
                  labelcolor=TEXT_COLOR, ncol=len(labels))
    ax.set_title("Tickets by Type", color=TEXT_COLOR)
    _style_axis(ax, grid=False)

    # ---- [0,1] Line: monthly volume trend --------------------------------
    ax = axes[0][1]
    if monthly_volume:
        months = [d["month"] for d in monthly_volume]
        x = range(len(months))
        ax.plot(x, [d.get("incidents", 0) for d in monthly_volume],
                color=COLORS[0], marker="o", markersize=3, label="Incidents", linewidth=1.5)
        ax.plot(x, [d.get("changes", 0) for d in monthly_volume],
                color=COLORS[1], marker="s", markersize=3, label="Changes", linewidth=1.5)
        ax.plot(x, [d.get("service_requests", 0) for d in monthly_volume],
                color=COLORS[2], marker="^", markersize=3, label="SRs", linewidth=1.5)
        ax.set_xticks(list(x))
        ax.set_xticklabels([m[-5:] for m in months], rotation=45, ha="right", fontsize=7)
        ax.legend(fontsize=7, framealpha=0, labelcolor=TEXT_COLOR)
    ax.set_title("Monthly Volume Trend", color=TEXT_COLOR)
    _style_axis(ax)

    # ---- [0,2] Horizontal bar: top 8 application hotspots ---------------
    ax = axes[0][2]
    top8 = hotspots[:8]
    if top8:
        apps = [_short_label(h.get("application", "?")) for h in reversed(top8)]
        counts = [h.get("count", 0) for h in reversed(top8)]
        bars = ax.barh(apps, counts, color=COLORS[4], edgecolor=GRID_COLOR, linewidth=0.5)
        ax.bar_label(bars, fmt="%d", color=MUTED_TEXT, fontsize=7, padding=3)
    ax.set_title("Top Application Hotspots", color=TEXT_COLOR)
    _style_axis(ax)

    # ---- [1,0] Bar: cycle time by type -----------------------------------
    ax = axes[1][0]
    ct_labels = ["Incident\nMTTR", "Change\nImpl.", "SR\nClosure"]
    ct_values = [
        summary_kpis.get("avg_mttr_hours", 0),
        0.0,  # changes cycle time not in summary_kpis by default
        0.0,
    ]
    bars = ax.bar(ct_labels, ct_values, color=COLORS[:3], edgecolor=GRID_COLOR, linewidth=0.5)
    ax.bar_label(bars, fmt="%.1f h", color=TEXT_COLOR, fontsize=7, padding=3)
    ax.set_ylabel("Average Hours", color=TEXT_COLOR)
    ax.set_title("Avg Cycle Time by Type", color=TEXT_COLOR)
    _style_axis(ax)

    # ---- [1,1] Line: incident MTTR trend ---------------------------------
    ax = axes[1][1]
    if mttr_trend:
        months = [d["month"] for d in mttr_trend]
        x = range(len(months))
        avg_vals = [d.get("avg_mttr_hours", 0) for d in mttr_trend]
        p90_vals = [d.get("p90_hours", 0) for d in mttr_trend]
        ax.plot(x, avg_vals, color=COLORS[0], label="Avg MTTR", linewidth=1.5, marker="o", markersize=3)
        ax.plot(x, p90_vals, color=COLORS[4], label="P90 MTTR", linewidth=1.5, linestyle="--", marker="s", markersize=3)
        ax.set_xticks(list(x))
        ax.set_xticklabels([m[-5:] for m in months], rotation=45, ha="right", fontsize=7)
        ax.set_ylabel("Hours", color=TEXT_COLOR)
        ax.legend(fontsize=7, framealpha=0, labelcolor=TEXT_COLOR)
    ax.set_title("Incident MTTR Trend", color=TEXT_COLOR)
    _style_axis(ax)

    # ---- [1,2] Horizontal bar: assignment groups (from hotspots) ---------
    ax = axes[1][2]
    if top8:
        apps = [_short_label(h.get("application", "?")) for h in reversed(top8)]
        mttr_vals = [h.get("avg_mttr_hours", 0) for h in reversed(top8)]
        bars = ax.barh(apps, mttr_vals, color=COLORS[3], edgecolor=GRID_COLOR, linewidth=0.5)
        ax.bar_label(bars, fmt="%.1fh", color=MUTED_TEXT, fontsize=7, padding=3)
    ax.set_title("App Avg MTTR (hours)", color=TEXT_COLOR)
    _style_axis(ax)

    # ---- [2,0] Bar: change type distribution ----------------------------
    ax = axes[2][0]
    chg_by_type = summary_kpis.get("by_type", {})
    chg_labels = ["Normal", "Standard", "Emergency"]
    chg_values = [chg_by_type.get("Change", 0), 0, 0]  # simplified from summary
    bars = ax.bar(chg_labels, chg_values, color=COLORS[1:4], edgecolor=GRID_COLOR, linewidth=0.5)
    ax.bar_label(bars, fmt="%d", color=TEXT_COLOR, fontsize=7, padding=3)
    ax.set_title("Change Type Distribution", color=TEXT_COLOR)
    _style_axis(ax)

    # ---- [2,1] KPI text cards -------------------------------------------
    ax = axes[2][1]
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    kpi_items = [
        ("Total Tickets", f"{summary_kpis.get('total_tickets', 0):,}"),
        ("SLA Compliance", f"{summary_kpis.get('sla_compliance_pct', 0):.1f}%"),
        ("Avg MTTR", f"{summary_kpis.get('avg_mttr_hours', 0):.1f} hrs"),
        ("Emergency Changes", f"{summary_kpis.get('emergency_change_pct', 0):.1f}%"),
    ]
    for i, (label, value) in enumerate(kpi_items):
        y = 0.85 - i * 0.22
        ax.text(0.05, y, label, color=MUTED_TEXT, fontsize=8, va="top")
        ax.text(0.05, y - 0.10, value, color=ACCENT, fontsize=13, fontweight="bold", va="top")
    ax.set_title("Key Metrics", color=TEXT_COLOR)

    # ---- [2,2] Horizontal bar: automation opportunities -----------------
    ax = axes[2][2]
    if top8:
        apps = [_short_label(h.get("application", "?")) for h in reversed(top8[:6])]
        pcts = [h.get("pct_of_total", 0) for h in reversed(top8[:6])]
        bars = ax.barh(apps, pcts, color=COLORS[2], edgecolor=GRID_COLOR, linewidth=0.5)
        ax.bar_label(bars, fmt="%.1f%%", color=MUTED_TEXT, fontsize=7, padding=3)
    ax.set_title("Top Automation Priorities", color=TEXT_COLOR)
    _style_axis(ax)

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    return _fig_to_bytes(fig)


# ---------------------------------------------------------------------------
# 2. Monthly Volume – stacked bar
# ---------------------------------------------------------------------------

# Function: render_monthly_volume
def render_monthly_volume(monthly_data: List[Dict[str, Any]]) -> bytes:
    _apply_theme()
    fig, ax = plt.subplots(figsize=(16, 7))
    fig.patch.set_facecolor(DARK_BG)

    if not monthly_data:
        ax.text(0.5, 0.5, "No data available", ha="center", va="center", color=MUTED_TEXT)
        ax.set_title("Monthly Ticket Volume", color=TEXT_COLOR)
        _style_axis(ax)
        return _fig_to_bytes(fig)

    months = [d["month"] for d in monthly_data]
    x = np.arange(len(months))
    width = 0.6

    inc = np.array([d.get("incidents", 0) for d in monthly_data])
    chg = np.array([d.get("changes", 0) for d in monthly_data])
    sr = np.array([d.get("service_requests", 0) for d in monthly_data])

    b1 = ax.bar(x, inc, width, label="Incidents", color=COLORS[0], edgecolor=DARK_BG, linewidth=0.5)
    b2 = ax.bar(x, chg, width, bottom=inc, label="Changes", color=COLORS[1], edgecolor=DARK_BG, linewidth=0.5)
    b3 = ax.bar(x, sr, width, bottom=inc + chg, label="Service Requests", color=COLORS[2], edgecolor=DARK_BG, linewidth=0.5)

    # Data labels: total on top + per-segment labels for segments ≥ 8% of bar height
    totals = inc + chg + sr
    max_total = float(totals.max()) if totals.max() > 0 else 1.0
    for xi, total, i_v, c_v, s_v in zip(x, totals, inc, chg, sr):
        if total > 0:
            ax.text(xi, total + max_total * 0.012, f"{int(total):,}",
                    ha="center", va="bottom", fontsize=7.5, color=TEXT_COLOR, fontweight="bold")
        min_pct = 0.08
        if i_v > 0 and i_v / total >= min_pct:
            ax.text(xi, i_v / 2, f"{int(i_v):,}", ha="center", va="center",
                    fontsize=6.5, color="white", fontweight="bold")
        if c_v > 0 and c_v / total >= min_pct:
            ax.text(xi, i_v + c_v / 2, f"{int(c_v):,}", ha="center", va="center",
                    fontsize=6.5, color="white", fontweight="bold")
        if s_v > 0 and s_v / total >= min_pct:
            ax.text(xi, i_v + c_v + s_v / 2, f"{int(s_v):,}", ha="center", va="center",
                    fontsize=6.5, color="white", fontweight="bold")

    ax.set_xticks(x)
    ax.set_xticklabels(months, rotation=45, ha="right", fontsize=8)
    ax.set_ylabel("Ticket Count", color=TEXT_COLOR)
    ax.set_title("Monthly Ticket Volume (Stacked)", color=TEXT_COLOR, fontsize=12, fontweight="bold")
    ax.legend(fontsize=8, framealpha=0, labelcolor=TEXT_COLOR)
    _style_axis(ax)
    plt.tight_layout()
    return _fig_to_bytes(fig)


# ---------------------------------------------------------------------------
# 3. Incident MTTR – dual-axis (volume bars + MTTR line)
# ---------------------------------------------------------------------------

# Function: render_incident_mttr
def render_incident_mttr(mttr_trend: List[Dict[str, Any]]) -> bytes:
    _apply_theme()
    fig, ax1 = plt.subplots(figsize=(16, 7))
    fig.patch.set_facecolor(DARK_BG)
    ax2 = ax1.twinx()

    if not mttr_trend:
        ax1.text(0.5, 0.5, "No data available", ha="center", va="center", color=MUTED_TEXT)
        ax1.set_title("Incident MTTR Trend", color=TEXT_COLOR)
        _style_axis(ax1)
        return _fig_to_bytes(fig)

    months = [d["month"] for d in mttr_trend]
    x = np.arange(len(months))
    counts = [d.get("count", 0) for d in mttr_trend]
    avg_mttr = [d.get("avg_mttr_hours", 0) for d in mttr_trend]
    p90_mttr = [d.get("p90_hours", 0) for d in mttr_trend]

    # Volume bars on ax1
    bars = ax1.bar(x, counts, color=COLORS[0], alpha=0.4, label="Volume", edgecolor=DARK_BG, linewidth=0.5)
    ax1.set_ylabel("Incident Count", color=COLORS[0])
    ax1.tick_params(axis="y", colors=COLORS[0])
    # Data labels: count above each bar (skip zeros)
    max_cnt = max(counts) if counts else 1
    for xi, cnt in zip(x, counts):
        if cnt > 0:
            ax1.text(xi, cnt + max_cnt * 0.02, f"{cnt:,}",
                     ha="center", va="bottom", fontsize=7, color=COLORS[0], fontweight="bold")

    # MTTR lines on ax2
    ax2.plot(x, avg_mttr, color=COLORS[3], linewidth=2, marker="o", markersize=4, label="Avg MTTR")
    ax2.plot(x, p90_mttr, color=COLORS[4], linewidth=1.5, linestyle="--", marker="s", markersize=4, label="P90 MTTR")
    ax2.set_ylabel("MTTR (hours)", color=COLORS[3])
    ax2.tick_params(axis="y", colors=COLORS[3])
    ax2.set_facecolor(SURFACE)
    for spine in ax2.spines.values():
        spine.set_edgecolor(GRID_COLOR)
    # Data labels: avg MTTR value above each marker (non-zero only)
    max_mttr = max(avg_mttr) if avg_mttr else 1
    for xi, avg in zip(x, avg_mttr):
        if avg > 0:
            ax2.annotate(f"{avg:.1f}h", xy=(xi, avg), xytext=(0, 7),
                         textcoords="offset points", ha="center", fontsize=6.5, color=COLORS[3], fontweight="bold")

    ax1.set_xticks(x)
    ax1.set_xticklabels(months, rotation=45, ha="right", fontsize=8)
    ax1.set_title("Incident Volume & MTTR Trend", color=TEXT_COLOR, fontsize=12, fontweight="bold")

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, fontsize=8, framealpha=0, labelcolor=TEXT_COLOR)
    _style_axis(ax1)
    plt.tight_layout()
    return _fig_to_bytes(fig)


# ---------------------------------------------------------------------------
# 4. Application Hotspots – horizontal Pareto
# ---------------------------------------------------------------------------

# Function: render_application_hotspots
def render_application_hotspots(
    hotspots_data: List[Dict[str, Any]], title: str = "Top Application Hotspots"
) -> bytes:
    _apply_theme()
    fig, ax = plt.subplots(figsize=(14, 9))
    fig.patch.set_facecolor(DARK_BG)

    if not hotspots_data:
        ax.text(0.5, 0.5, "No data available", ha="center", va="center", color=MUTED_TEXT)
        ax.set_title(title, color=TEXT_COLOR)
        _style_axis(ax)
        return _fig_to_bytes(fig)

    apps = [_short_label(h.get("application", "?")) for h in reversed(hotspots_data)]
    counts = [h.get("count", 0) for h in reversed(hotspots_data)]
    pcts = [h.get("pct_of_total", 0) for h in reversed(hotspots_data)]

    # Color gradient by index
    bar_colors = [COLORS[i % len(COLORS)] for i in range(len(apps))]
    bars = ax.barh(apps, counts, color=bar_colors, edgecolor=DARK_BG, linewidth=0.5)

    for bar, pct in zip(bars, pcts):
        ax.text(
            bar.get_width() + max(counts) * 0.01,
            bar.get_y() + bar.get_height() / 2,
            f"{bar.get_width():.0f} ({pct:.1f}%)",
            va="center", ha="left", color=MUTED_TEXT, fontsize=8,
        )

    # Pareto cumulative line on secondary axis
    ax2 = ax.twiny()
    running_pct = np.cumsum(list(reversed(pcts)))
    y_pos = np.arange(len(apps))
    ax2.plot(running_pct, y_pos, color=COLORS[3], linewidth=1.5, linestyle="--", marker="D", markersize=4)
    ax2.set_xlabel("Cumulative %", color=COLORS[3])
    ax2.tick_params(axis="x", colors=COLORS[3])
    ax2.set_xlim(0, 105)
    ax2.set_facecolor(SURFACE)
    for spine in ax2.spines.values():
        spine.set_edgecolor(GRID_COLOR)

    ax.set_xlabel("Ticket Count", color=TEXT_COLOR)
    ax.set_title(title, color=TEXT_COLOR, fontsize=12, fontweight="bold")
    _style_axis(ax)
    plt.tight_layout()
    return _fig_to_bytes(fig)


# ---------------------------------------------------------------------------
# 5. Change Risk – 2x2 subplot
# ---------------------------------------------------------------------------

# Function: _render_change_type_donut
def _render_change_type_donut(ax, by_type: Dict[str, Any]) -> None:
    labels = [k for k, v in by_type.items() if v > 0]
    values = [v for v in by_type.values() if v > 0]
    if values:
        wedge_colors = [COLORS[0], COLORS[2], COLORS[4]][:len(values)]
        wedges, texts, autotexts = ax.pie(
            values, labels=None, colors=wedge_colors,
            autopct="%1.1f%%", startangle=90,
            wedgeprops=dict(width=0.55, edgecolor=DARK_BG, linewidth=1.5),
            pctdistance=0.75,
        )
        for at in autotexts:
            at.set_color(DARK_BG)
            at.set_fontsize(7)
        ax.legend(labels, loc="lower center", fontsize=7, framealpha=0, labelcolor=TEXT_COLOR)
    ax.set_title("Change Type Split", color=TEXT_COLOR)
    _style_axis(ax, grid=False)


# Function: _render_monthly_change_volume
def _render_monthly_change_volume(ax, change_volume: List[Dict[str, Any]]) -> None:
    if change_volume:
        months = [d["month"] for d in change_volume]
        x = np.arange(len(months))
        norm = np.array([d.get("normal", 0) for d in change_volume])
        std = np.array([d.get("standard", 0) for d in change_volume])
        emg = np.array([d.get("emergency", 0) for d in change_volume])
        ax.bar(x, norm, label="Normal", color=COLORS[0], edgecolor=DARK_BG, linewidth=0.4)
        ax.bar(x, std, bottom=norm, label="Standard", color=COLORS[2], edgecolor=DARK_BG, linewidth=0.4)
        ax.bar(x, emg, bottom=norm + std, label="Emergency", color=COLORS[4], edgecolor=DARK_BG, linewidth=0.4)
        # Data labels: total on top of each stacked change bar
        chg_totals = norm + std + emg
        max_chg = float(chg_totals.max()) if chg_totals.max() > 0 else 1.0
        for xi, total in zip(x, chg_totals):
            if total > 0:
                ax.text(xi, total + max_chg * 0.02, f"{int(total):,}",
                        ha="center", va="bottom", fontsize=6.5, color=TEXT_COLOR, fontweight="bold")
        ax.set_xticks(x)
        ax.set_xticklabels([m[-5:] for m in months], rotation=45, ha="right", fontsize=7)
        ax.legend(fontsize=7, framealpha=0, labelcolor=TEXT_COLOR)
    ax.set_title("Monthly Change Volume", color=TEXT_COLOR)
    _style_axis(ax)


# Function: _render_change_kpi_panel
def _render_change_kpi_panel(ax, changes_summary: Dict[str, Any]) -> None:
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    metrics = [
        ("Emergency Change %", f"{changes_summary.get('emergency_pct', 0):.1f}%"),
        ("Expedited Change %", f"{changes_summary.get('expedited_pct', 0):.1f}%"),
        ("Rescheduled %", f"{changes_summary.get('rescheduled_pct', 0):.1f}%"),
        ("Avg Impl. Time", f"{changes_summary.get('avg_impl_hours', 0):.1f} hrs"),
        ("Success Rate", f"{changes_summary.get('implementation_success_pct', 0):.1f}%"),
    ]
    for i, (lbl, val) in enumerate(metrics):
        y = 0.90 - i * 0.18
        ax.text(0.05, y, lbl, color=MUTED_TEXT, fontsize=8, va="top")
        color = COLORS[4] if "Emergency" in lbl and float(val.replace("%", "")) > 20 else ACCENT
        ax.text(0.55, y, val, color=color, fontsize=10, fontweight="bold", va="top")
    ax.set_title("Change KPIs", color=TEXT_COLOR)


# Function: _render_change_type_bar
def _render_change_type_bar(ax, by_type: Dict[str, Any]) -> None:
    type_labels = list(by_type.keys())
    type_values = list(by_type.values())
    if type_values:
        bar_colors = [COLORS[0], COLORS[2], COLORS[4]][:len(type_labels)]
        bars = ax.barh(type_labels, type_values, color=bar_colors, edgecolor=DARK_BG, linewidth=0.5)
        ax.bar_label(bars, fmt="%d", color=TEXT_COLOR, fontsize=8, padding=3)
    ax.set_title("Changes by Type (Count)", color=TEXT_COLOR)
    _style_axis(ax)


# Function: render_change_risk
def render_change_risk(
    changes_summary: Dict[str, Any],
    change_volume: List[Dict[str, Any]],
) -> bytes:
    _apply_theme()
    fig, axes = plt.subplots(2, 2, figsize=(14, 9))
    fig.patch.set_facecolor(DARK_BG)
    fig.suptitle("Change Management Risk Dashboard", color=TEXT_COLOR, fontsize=13, fontweight="bold")

    by_type = changes_summary.get("by_type", {"Normal": 0, "Standard": 0, "Emergency": 0})

    _render_change_type_donut(axes[0][0], by_type)
    _render_monthly_change_volume(axes[0][1], change_volume)
    _render_change_kpi_panel(axes[1][0], changes_summary)
    _render_change_type_bar(axes[1][1], by_type)

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    return _fig_to_bytes(fig)


# ---------------------------------------------------------------------------
# 6. Automation Quadrant – scatter plot
# ---------------------------------------------------------------------------

# Function: render_automation_quadrant
def render_automation_quadrant(candidates: List[Any]) -> bytes:
    """
    Scatter plot: x=ticket_count, y=avg_cycle_time_hours,
    bubble size proportional to total_score, colour by priority.
    Annotates the top 10 candidates by name.
    """
    _apply_theme()
    fig, ax = plt.subplots(figsize=(14, 9))
    fig.patch.set_facecolor(DARK_BG)

    if not candidates:
        ax.text(0.5, 0.5, "No automation candidates available",
                ha="center", va="center", color=MUTED_TEXT, transform=ax.transAxes)
        ax.set_title("Automation Opportunity Quadrant", color=TEXT_COLOR)
        _style_axis(ax)
        return _fig_to_bytes(fig)

    # Group by priority for legend
    priority_groups: Dict[str, list] = {"High": [], "Medium": [], "Low": [], "Monitor": []}
    for c in candidates:
        p = getattr(c, "priority", "Monitor")
        priority_groups.setdefault(p, []).append(c)

    # Draw quadrant lines
    all_x = [getattr(c, "ticket_count", 0) for c in candidates]
    all_y = [getattr(c, "avg_cycle_time_hours", 0) for c in candidates]
    if all_x and all_y:
        med_x = float(np.median(all_x))
        med_y = float(np.median(all_y))
        ax.axvline(med_x, color=GRID_COLOR, linewidth=1, linestyle="--", alpha=0.6)
        ax.axhline(med_y, color=GRID_COLOR, linewidth=1, linestyle="--", alpha=0.6)
        # Quadrant labels
        ax_xlim = ax.get_xlim()
        ax_ylim = ax.get_ylim()
        ax.text(max(all_x) * 0.75, max(all_y) * 0.9, "High Vol\nHigh Complexity",
                color=MUTED_TEXT, fontsize=7, ha="center", alpha=0.6)
        ax.text(max(all_x) * 0.75, max(all_y) * 0.05, "High Vol\nLow Complexity",
                color=MUTED_TEXT, fontsize=7, ha="center", alpha=0.6)

    for priority, group in priority_groups.items():
        if not group:
            continue
        x_vals = [getattr(c, "ticket_count", 0) for c in group]
        y_vals = [getattr(c, "avg_cycle_time_hours", 0) for c in group]
        sizes = [max(getattr(c, "total_score", 10) * 5, 40) for c in group]
        ax.scatter(
            x_vals, y_vals, s=sizes,
            color=PRIORITY_COLORS.get(priority, MUTED_TEXT),
            alpha=0.8, edgecolors=DARK_BG, linewidth=0.8,
            label=priority, zorder=3,
        )

    # Annotate top 10 with smart positioning to avoid overlap
    sorted_candidates = sorted(candidates, key=lambda c: getattr(c, "total_score", 0), reverse=True)
    for i, c in enumerate(sorted_candidates[:10]):
        x = getattr(c, "ticket_count", 0)
        y = getattr(c, "avg_cycle_time_hours", 0)
        label = _short_label(getattr(c, "category", "?"), 16)
        
        # Alternate positioning: even indices go right, odd go left/above
        if i % 2 == 0:
            xytext = (12, 8)
            ha = "left"
        else:
            xytext = (-12, 12)
            ha = "right"
        
        ax.annotate(
            label,
            xy=(x, y),
            xytext=xytext,
            textcoords="offset points",
            fontsize=8,
            color=TEXT_COLOR,
            alpha=0.9,
            ha=ha,
            bbox=dict(
                boxstyle="round,pad=0.3",
                facecolor=SURFACE,
                edgecolor=GRID_COLOR,
                alpha=0.7,
                linewidth=0.5,
            ),
            arrowprops=dict(
                arrowstyle="->",
                color=MUTED_TEXT,
                lw=0.5,
                alpha=0.6,
            ),
        )

    ax.set_xlabel("Ticket Volume (Count)", color=TEXT_COLOR)
    ax.set_ylabel("Avg Cycle Time (hours)", color=TEXT_COLOR)
    ax.set_title("Automation Opportunity Quadrant", color=TEXT_COLOR, fontsize=12, fontweight="bold")
    ax.legend(title="Priority", fontsize=8, framealpha=0.1, labelcolor=TEXT_COLOR,
              title_fontsize=8, facecolor=SURFACE, edgecolor=GRID_COLOR)
    _style_axis(ax)
    plt.tight_layout()
    return _fig_to_bytes(fig)


# ---------------------------------------------------------------------------
# 7. SR Productivity – 2x2 subplot
# ---------------------------------------------------------------------------

# Function: render_sr_productivity
def render_sr_productivity(
    sr_summary: Dict[str, Any],
    monthly_sr: List[Dict[str, Any]],
) -> bytes:
    _apply_theme()
    fig, axes = plt.subplots(2, 2, figsize=(14, 9))
    fig.patch.set_facecolor(DARK_BG)
    fig.suptitle("Service Request Productivity Dashboard", color=TEXT_COLOR, fontsize=13, fontweight="bold")

    # ---- [0,0] Bar: monthly SR trend ------------------------------------
    ax = axes[0][0]
    if monthly_sr:
        months = [d["month"] for d in monthly_sr]
        x = np.arange(len(months))
        sr_counts = [d.get("service_requests", 0) for d in monthly_sr]
        bars = ax.bar(x, sr_counts, color=COLORS[2], edgecolor=DARK_BG, linewidth=0.5)
        # Data labels on each SR bar
        max_sr = max(sr_counts) if sr_counts else 1
        for xi, cnt in zip(x, sr_counts):
            if cnt > 0:
                ax.text(xi, cnt + max_sr * 0.02, f"{cnt:,}",
                        ha="center", va="bottom", fontsize=7, color=TEXT_COLOR, fontweight="bold")
        ax.set_xticks(x)
        ax.set_xticklabels([m[-5:] for m in months], rotation=45, ha="right", fontsize=7)
        ax.set_ylabel("SR Count", color=TEXT_COLOR)
        # Moving average overlay
        if len(sr_counts) >= 3:
            ma = np.convolve(sr_counts, np.ones(3) / 3, mode="valid")
            ax.plot(np.arange(2, len(sr_counts)), ma, color=COLORS[3],
                    linewidth=1.5, linestyle="--", label="3-mo MA")
            ax.legend(fontsize=7, framealpha=0, labelcolor=TEXT_COLOR)
    ax.set_title("Monthly Service Request Volume", color=TEXT_COLOR)
    _style_axis(ax)

    # ---- [0,1] Horizontal bar: top categories ---------------------------
    ax = axes[0][1]
    top_cats = sr_summary.get("top_categories", [])
    if top_cats:
        cat_labels = [_short_label(str(c.get("category", "?"))) for c in reversed(top_cats[:8])]
        cat_counts = [c.get("count", 0) for c in reversed(top_cats[:8])]
        bar_colors = [COLORS[i % len(COLORS)] for i in range(len(cat_labels))]
        bars = ax.barh(cat_labels, cat_counts, color=bar_colors, edgecolor=DARK_BG, linewidth=0.5)
        ax.bar_label(bars, fmt="%d", color=MUTED_TEXT, fontsize=7, padding=3)
    ax.set_title("Top SR Categories", color=TEXT_COLOR)
    _style_axis(ax)

    # ---- [1,0] Bar: ageing analysis -------------------------------------
    ax = axes[1][0]
    ageing = sr_summary.get("ageing", {"lt_7d": 0, "7_30d": 0, "30_90d": 0, "gt_90d": 0})
    age_labels = ["< 7 days", "7-30 days", "30-90 days", "> 90 days"]
    age_values = [
        ageing.get("lt_7d", 0),
        ageing.get("7_30d", 0),
        ageing.get("30_90d", 0),
        ageing.get("gt_90d", 0),
    ]
    age_colors = [COLORS[2], COLORS[3], COLORS[4], COLORS[4]]
    bars = ax.bar(age_labels, age_values, color=age_colors, edgecolor=DARK_BG, linewidth=0.5)
    ax.bar_label(bars, fmt="%d", color=TEXT_COLOR, fontsize=8, padding=3)
    ax.set_ylabel("Open SR Count", color=TEXT_COLOR)
    ax.set_title("Open SR Ageing Buckets", color=TEXT_COLOR)
    _style_axis(ax)

    # ---- [1,1] KPI panel ------------------------------------------------
    ax = axes[1][1]
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    kpis = [
        ("Total SRs", f"{sr_summary.get('total', 0):,}"),
        ("Backlog (Open)", f"{sr_summary.get('backlog_count', 0):,}"),
        ("Avg Closure Time", f"{sr_summary.get('avg_closure_hours', 0):.1f} hrs"),
        ("Median Closure Time", f"{sr_summary.get('median_closure_hours', 0):.1f} hrs"),
    ]
    for i, (lbl, val) in enumerate(kpis):
        y = 0.88 - i * 0.22
        ax.text(0.05, y, lbl, color=MUTED_TEXT, fontsize=8, va="top")
        ax.text(0.05, y - 0.10, val, color=ACCENT, fontsize=13, fontweight="bold", va="top")
    ax.set_title("SR KPIs", color=TEXT_COLOR)

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    return _fig_to_bytes(fig)
