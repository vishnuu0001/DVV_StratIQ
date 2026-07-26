# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: LabRobot — backend (visualizer.py)
# Date: 2026-05-20
# ---------------------------------------------------------------------------
import io
import matplotlib
matplotlib.use("Agg")  # non-interactive server backend — must be before pyplot
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

# ─── palette ─────────────────────────────────────────────────────────────────
CHEM_COLORS = [
    "#ef4444", "#f97316", "#eab308", "#22c55e", "#14b8a6",
    "#3b82f6", "#8b5cf6", "#ec4899", "#06b6d4", "#84cc16",
]
FRAME_COLOR   = "#38bdf8"   # neon-blue rack wire
FLOOR_COLOR   = "#1e3a5f"
FLOOR_EDGE    = "#334155"
FETCHED_COLOR = "#475569"
BG_COLOR      = "#0d1b2a"


# ─── geometry helpers ─────────────────────────────────────────────────────────

# Function: _faces
def _faces(x, y, z, dx, dy, dz):
    """Return the 6 face-vertex lists for a cuboid."""
    return [
        [[x,    y,    z   ], [x+dx, y,    z   ], [x+dx, y+dy, z   ], [x,    y+dy, z   ]],
        [[x,    y,    z+dz], [x+dx, y,    z+dz], [x+dx, y+dy, z+dz], [x,    y+dy, z+dz]],
        [[x,    y,    z   ], [x+dx, y,    z   ], [x+dx, y,    z+dz], [x,    y,    z+dz]],
        [[x,    y+dy, z   ], [x+dx, y+dy, z   ], [x+dx, y+dy, z+dz], [x,    y+dy, z+dz]],
        [[x,    y,    z   ], [x,    y+dy, z   ], [x,    y+dy, z+dz], [x,    y,    z+dz]],
        [[x+dx, y,    z   ], [x+dx, y+dy, z   ], [x+dx, y+dy, z+dz], [x+dx, y,    z+dz]],
    ]


# Function: _box
def _box(ax, x, y, z, dx, dy, dz, color, alpha, edge="#1a1a1a", lw=0.5):
    poly = Poly3DCollection(
        _faces(x, y, z, dx, dy, dz),
        alpha=alpha, facecolor=color, edgecolor=edge, linewidth=lw,
    )
    ax.add_collection3d(poly)


# Function: _rack_frame
def _rack_frame(ax, x0, y0, W, D, H):
    """Wire-frame rack with shelf dividers."""
    kw = dict(color=FRAME_COLOR, linewidth=1.4, alpha=0.9)
    kw_shelf = dict(color=FRAME_COLOR, linewidth=0.7, alpha=0.35, linestyle="--")
    corners = [(x0, y0), (x0+W, y0), (x0, y0+D), (x0+W, y0+D)]

    # 4 vertical pillars
    for cx, cy in corners:
        ax.plot([cx, cx], [cy, cy], [0, H], **kw)

    # bottom & top rectangles
    for z in (0, H):
        ax.plot([x0, x0+W], [y0,    y0   ], [z, z], **kw)
        ax.plot([x0, x0+W], [y0+D,  y0+D ], [z, z], **kw)
        ax.plot([x0, x0   ], [y0,   y0+D ], [z, z], **kw)
        ax.plot([x0+W, x0+W],[y0,   y0+D ], [z, z], **kw)

    # shelf dividers at 1/3 and 2/3 height
    for sh in (H/3, 2*H/3):
        ax.plot([x0, x0+W], [y0,   y0  ], [sh, sh], **kw_shelf)
        ax.plot([x0, x0+W], [y0+D, y0+D], [sh, sh], **kw_shelf)
        ax.plot([x0, x0   ], [y0,  y0+D], [sh, sh], **kw_shelf)
        ax.plot([x0+W,x0+W], [y0,  y0+D], [sh, sh], **kw_shelf)


# ─── layout constants ─────────────────────────────────────────────────────────
RACK_W, RACK_D, RACK_H = 2.1, 1.5, 4.2
COL_STRIDE = RACK_W + 0.85   # column spacing (x)
ROW_STRIDE = RACK_D + 1.6    # row spacing (y) — extra room for front labels
CHEM_H     = 0.72
CHEM_GAP   = 0.12
PAD        = 0.1


# ─── per-rack drawing helpers ─────────────────────────────────────────────────

# Function: _group_by_rack
def _group_by_rack(placements_data):
    rack_placements: dict[int, list] = {}
    for p in placements_data:
        rack_placements.setdefault(p["rack_id"], []).append(p)
    return rack_placements


# Function: _assign_chemical_colors
def _assign_chemical_colors(placements_data):
    """Assign a stable color to each chemical id."""
    chem_color: dict[int, str] = {}
    _ci = 0
    for p in placements_data:
        cid = p["chemical_id"]
        if cid not in chem_color:
            chem_color[cid] = CHEM_COLORS[_ci % len(CHEM_COLORS)]
            _ci += 1
    return chem_color


# Function: _draw_rack_chemicals
def _draw_rack_chemicals(ax, x0, y0, chems, chem_color):
    """Draw the stacked chemical boxes for one rack; return its manifest lines."""
    lines = []
    for slot_i, placement in enumerate(chems):
        cz = slot_i * (CHEM_H + CHEM_GAP)
        if cz + CHEM_H > RACK_H - PAD:
            break  # rack visually full

        placed = placement["status"] == "Placed"
        if placed:
            color = chem_color.get(placement["chemical_id"], "#888")
            alpha, edge_c, lw, mark = 0.88, "#ffffff", 0.7, "●"
        else:
            color, alpha, edge_c, lw, mark = FETCHED_COLOR, 0.25, "#64748b", 0.4, "○"

        _box(ax,
             x0 + PAD, y0 + PAD, cz,
             RACK_W - 2*PAD, RACK_D - 2*PAD, CHEM_H,
             color, alpha, edge_c, lw)

        name = placement["chemical"]["name"]
        if len(name) > 18:
            name = name[:16] + "…"
        lines.append((placement["chemical"]["barcode"], name, mark, placed))
    return lines


# Function: _draw_rack
def _draw_rack(ax, x0, y0, rack, rack_placements, chem_color):
    """Draw one rack's floor/frame/labels/chemicals; return manifest lines or None."""
    _box(ax, x0, y0, -0.06, RACK_W, RACK_D, 0.06,
         FLOOR_COLOR, 0.95, FLOOR_EDGE, 0.6)

    _rack_frame(ax, x0, y0, RACK_W, RACK_D, RACK_H)

    ax.text(x0 + RACK_W/2, y0 + RACK_D/2, RACK_H + 0.18,
            rack["barcode"],
            ha="center", va="bottom", fontsize=7.5,
            color="#7dd3fc", fontweight="bold")
    ax.text(x0 + RACK_W/2, y0 + RACK_D/2, RACK_H,
            rack["name"],
            ha="center", va="top", fontsize=5.5, color="#94a3b8")

    chems = rack_placements.get(rack["id"], [])
    lines = _draw_rack_chemicals(ax, x0, y0, chems, chem_color)
    return lines if chems else None


# Function: _draw_scientist_label
def _draw_scientist_label(ax, y0, scientist):
    mid_x = (3 * COL_STRIDE - 0.85) / 2
    ax.text(mid_x, y0 + RACK_D/2, -0.75,
            f"{scientist['name']}  ({scientist['code']})",
            ha="center", va="top", fontsize=10,
            color="#e2e8f0", fontweight="bold", style="italic")


# ─── axis / legend / manifest-panel helpers ───────────────────────────────────

# Function: _style_axes
def _style_axes(ax, total_x, total_y):
    ax.set_xlim(-0.6, total_x)
    ax.set_ylim(-0.4, total_y)
    ax.set_zlim(-0.2, RACK_H + 1.2)

    ax.tick_params(axis="x", labelsize=0, colors="#1e293b")
    ax.tick_params(axis="y", labelsize=0, colors="#1e293b")
    ax.tick_params(axis="z", labelsize=7,  colors="#64748b")
    ax.set_zticks([0, RACK_H/3, 2*RACK_H/3, RACK_H])
    ax.set_zticklabels(["Base", "L1", "L2", "Top"], color="#64748b", fontsize=7)

    for spine in (ax.xaxis, ax.yaxis, ax.zaxis):
        spine.pane.fill = False
        spine.pane.set_edgecolor("#1e293b")

    ax.grid(True, color="#1e293b", linewidth=0.4)
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.set_zlabel("Level", color="#64748b", fontsize=8, labelpad=8)
    ax.view_init(elev=28, azim=-48)


# Function: _draw_rack_manifest_lines
def _draw_rack_manifest_lines(fig, rack_bc, lines, fig_y_top, bi, rack_block_h, panel_left):
    fig_y = fig_y_top - 0.025 - bi * rack_block_h
    fig.text(panel_left + 0.01, fig_y,
             rack_bc,
             color="#38bdf8", fontsize=8, fontweight="bold",
             va="top", ha="left", transform=fig.transFigure,
             fontfamily="monospace")
    line_h = 0.018
    for li, (bc, name, mark, placed) in enumerate(lines):
        fig_y_line = fig_y - 0.022 - li * line_h
        color = "#94dd94" if placed else "#94a3b8"
        fig.text(panel_left + 0.012, fig_y_line,
                 f"{mark} {bc}  {name}",
                 color=color, fontsize=7.5, va="top", ha="left",
                 transform=fig.transFigure,
                 fontfamily="monospace")


# Function: _draw_scientist_manifest_block
def _draw_scientist_manifest_block(fig, scientist, row_entries, row_i, row_height, panel_left):
    fig_y_top = 0.94 - row_i * row_height
    fig.text(panel_left, fig_y_top,
             f"{scientist['name']}  ({scientist['code']})",
             color="#e2e8f0", fontsize=8.5, fontweight="bold",
             va="top", ha="left", transform=fig.transFigure)

    rack_block_h = (row_height * 0.85) / 3   # height per rack block
    racks_sorted = sorted(row_entries, key=lambda t: t[0])
    for bi, (_col_i, rack_bc, lines) in enumerate(racks_sorted):
        _draw_rack_manifest_lines(fig, rack_bc, lines, fig_y_top, bi, rack_block_h, panel_left)


# Function: _draw_manifest_panel
def _draw_manifest_panel(fig, rack_manifests, scientists_data, n_sci):
    """Right-side 2D manifest panel; grouped by scientist row, then rack column."""
    if not rack_manifests:
        return

    row_height = 0.88 / n_sci  # fraction of figure height per scientist row

    fig.text(0.72, 0.97, "Rack Contents", color="#7dd3fc",
             fontsize=10, fontweight="bold", va="top", ha="left",
             transform=fig.transFigure)

    by_row: dict = {}
    for row_i, col_i, rack_bc, lines in rack_manifests:
        by_row.setdefault(row_i, []).append((col_i, rack_bc, lines))

    panel_left = 0.72
    for row_i in sorted(by_row):
        _draw_scientist_manifest_block(
            fig, scientists_data[row_i], by_row[row_i], row_i, row_height, panel_left)


# Function: _draw_legend
def _draw_legend(ax):
    from matplotlib.patches import Patch
    legend_handles = [
        Patch(facecolor="#22c55e", alpha=0.88, edgecolor="white",   label="Placed"),
        Patch(facecolor=FETCHED_COLOR, alpha=0.25, edgecolor="#94a3b8", label="Fetched"),
        Patch(facecolor=FLOOR_COLOR,   alpha=0.95, edgecolor=FLOOR_EDGE, label="Empty rack"),
    ]
    ax.legend(handles=legend_handles, loc="upper left",
              facecolor="#1e293b", edgecolor="#334155",
              labelcolor="#e2e8f0", fontsize=8, framealpha=0.9)


# Function: _export_png
def _export_png(fig):
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=130, bbox_inches="tight",
                facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)
    buf.seek(0)
    return buf.read()


# ─── main generator ──────────────────────────────────────────────────────────

# Function: generate_rack_image
def generate_rack_image(scientists_data: list, placements_data: list) -> bytes:
    """
    scientists_data : list of dicts  {id, name, code, racks:[{id,barcode,name}]}
    placements_data : list of dicts  {id, rack_id, chemical_id, status,
                                      chemical:{barcode, name}}
    Returns PNG bytes.
    """
    rack_placements = _group_by_rack(placements_data)
    chem_color = _assign_chemical_colors(placements_data)

    n_sci = len(scientists_data)
    fig_h = max(8, 6 * n_sci)
    fig = plt.figure(figsize=(18, fig_h))
    fig.patch.set_facecolor(BG_COLOR)

    ax = fig.add_axes([0.0, 0.03, 0.70, 0.92], projection="3d")
    ax.set_facecolor(BG_COLOR)

    # will be populated during loop for right-side 2D panel
    rack_manifests: list = []  # list of (row_i, col_i, rack_barcode, lines)

    for row_i, scientist in enumerate(scientists_data):
        y0 = row_i * ROW_STRIDE

        for col_i, rack in enumerate(scientist["racks"]):
            x0 = col_i * COL_STRIDE
            lines = _draw_rack(ax, x0, y0, rack, rack_placements, chem_color)
            if lines is not None:
                rack_manifests.append((row_i, col_i, rack["barcode"], lines))

        _draw_scientist_label(ax, y0, scientist)

    total_x = 3 * COL_STRIDE
    total_y = max(n_sci * ROW_STRIDE, ROW_STRIDE)
    _style_axes(ax, total_x, total_y)

    _draw_manifest_panel(fig, rack_manifests, scientists_data, n_sci)

    if n_sci == 1:
        title = f"Virtual Rack  —  {scientists_data[0]['name']}"
    else:
        title = "Virtual Rack 3D View  —  Lab Chemical Management"
    fig.suptitle(title, color="#f8fafc", fontsize=14, fontweight="bold", y=0.99)

    _draw_legend(ax)

    return _export_png(fig)
