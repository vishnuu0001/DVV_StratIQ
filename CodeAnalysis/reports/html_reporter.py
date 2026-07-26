# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Generates a self-contained HTML dashboard using Jinja2 + inline CSS/JS.
# Date: 2026-03-06
# ---------------------------------------------------------------------------
"""
html_reporter.py
----------------
Generates a self-contained HTML dashboard using Jinja2 + inline CSS/JS.
No external CDN required – Chart.js is bundled inline (data-URI).
"""
from __future__ import annotations

import dataclasses
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from jinja2 import Environment, BaseLoader, select_autoescape

# ─── Embedded Jinja2 template ─────────────────────────────────────────────────
_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <title>CodeAnalysis Report – {{ repo_name }}</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
  <style>
    *{box-sizing:border-box;margin:0;padding:0}
    body{font-family:'Segoe UI',sans-serif;background:#0f1117;color:#e0e0e0;padding:20px}
    h1{font-size:1.8rem;margin-bottom:4px;color:#61dafb}
    .sub{color:#888;font-size:.9rem;margin-bottom:24px}
    .grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:16px;margin-bottom:24px}
    .card{background:#1a1d26;border-radius:10px;padding:20px;border:1px solid #2a2d3e}
    .card h2{font-size:1rem;color:#61dafb;margin-bottom:12px;text-transform:uppercase;letter-spacing:.05em}
    .score{font-size:2.8rem;font-weight:700;line-height:1}
    .label{display:inline-block;padding:3px 10px;border-radius:20px;font-size:.75rem;margin-top:6px;font-weight:600}
    .EXCELLENT,.GOOD,.LOW,.LOW.RISK{background:#0d4a2d;color:#4ade80}
    .FAIR,.MEDIUM,.MEDIUM.RISK{background:#432d00;color:#fb923c}
    .POOR,.HIGH,.HIGH.RISK,.CRITICAL{background:#4a0d0d;color:#f87171}
    .bar-wrap{margin-top:10px}
    .bar-label{font-size:.8rem;color:#aaa;display:flex;justify-content:space-between}
    .bar-bg{background:#2a2d3e;border-radius:6px;height:8px;margin:3px 0 10px}
    .bar-fill{height:8px;border-radius:6px;background:linear-gradient(90deg,#3b82f6,#06b6d4)}
    .findings{margin-top:12px}
    .finding-item{font-size:.8rem;color:#f87171;margin-bottom:4px;padding-left:12px;position:relative}
    .finding-item::before{content:"⚠";position:absolute;left:0}
    .chart-wrap{background:#1a1d26;border-radius:10px;padding:20px;border:1px solid #2a2d3e;margin-bottom:24px}
    .lang-table{width:100%;border-collapse:collapse;margin-top:8px;font-size:.85rem}
    .lang-table th{text-align:left;color:#888;padding:6px 8px;border-bottom:1px solid #2a2d3e}
    .lang-table td{padding:6px 8px;border-bottom:1px solid #1e2132}
    .dep-pill{display:inline-block;background:#1e2132;border-radius:4px;padding:2px 8px;
              margin:2px;font-size:.75rem;font-family:monospace}
    footer{text-align:center;color:#444;font-size:.75rem;margin-top:32px}
  </style>
</head>
<body>
  <h1>&#128202; CodeAnalysis Report</h1>
  <div class="sub">
    Repository: <strong>{{ repo_name }}</strong> &nbsp;|&nbsp;
    {{ total_sloc | int }} SLOC across {{ file_count }} files &nbsp;|&nbsp;
    Generated: {{ generated }}
  </div>

  <!-- Score cards row -->
  <div class="grid">

    <!-- Software Health -->
    <div class="card">
      <h2>&#129309; Software Health</h2>
      <div class="score">{{ health.health }}
        <span style="font-size:1rem;color:#888">/ 100</span></div>
      <span class="label {{ health.risk_label }}">{{ health.risk_label }}</span>
      <div class="bar-wrap">
        <div class="bar-label"><span>Resiliency</span><span>{{ health.resiliency }}</span></div>
        <div class="bar-bg"><div class="bar-fill" style="width:{{ health.resiliency }}%"></div></div>
        <div class="bar-label"><span>Agility</span><span>{{ health.agility }}</span></div>
        <div class="bar-bg"><div class="bar-fill" style="width:{{ health.agility }}%"></div></div>
        <div class="bar-label"><span>Elegance</span><span>{{ health.elegance }}</span></div>
        <div class="bar-bg"><div class="bar-fill" style="width:{{ health.elegance }}%"></div></div>
      </div>
      {% if health.summary %}
      <div class="findings">
        {% for f in health.summary[:5] %}
        <div class="finding-item">{{ f }}</div>
        {% endfor %}
      </div>
      {% endif %}
    </div>

    <!-- Technical Debt -->
    <div class="card">
      <h2>&#128184; Technical Debt</h2>
      <div class="score">{{ debt.debt_months }}
        <span style="font-size:1rem;color:#888">PM</span></div>
      <span class="label {{ debt.risk_label }}">{{ debt.risk_label }}</span>
      <div class="bar-wrap" style="margin-top:14px">
        <div class="bar-label"><span>Debt Ratio</span><span>{{ debt.debt_ratio }}%</span></div>
        <div class="bar-bg"><div class="bar-fill" style="width:{{ debt.debt_ratio }}%"></div></div>
      </div>
      <div style="margin-top:12px;font-size:.83rem;color:#aaa">
        <div>KSLOC: <strong>{{ debt.total_ksloc }}</strong></div>
        <div>FTEs needed: <strong>{{ debt.debt_ftes }}</strong></div>
        <div>Est. cost: <strong>${{ "{:,.0f}".format(debt.debt_usd) }}</strong></div>
        <div>Density: <strong>{{ debt.density }} PM/kLOC</strong></div>
      </div>
    </div>

    <!-- Cloud Maturity -->
    <div class="card">
      <h2>&#9928; Cloud Maturity</h2>
      <div class="score">{{ cloud.total }}
        <span style="font-size:1rem;color:#888">/ 100</span></div>
      <span class="label {{ cloud.risk_label }}">{{ cloud.risk_label }}</span>
      <div class="bar-wrap">
        <div class="bar-label"><span>Stateless Design</span><span>{{ cloud.stateless_design }}</span></div>
        <div class="bar-bg"><div class="bar-fill" style="width:{{ cloud.stateless_design }}%"></div></div>
        <div class="bar-label"><span>Containerization</span><span>{{ cloud.containerization }}</span></div>
        <div class="bar-bg"><div class="bar-fill" style="width:{{ cloud.containerization }}%"></div></div>
        <div class="bar-label"><span>API Surface</span><span>{{ cloud.api_surface }}</span></div>
        <div class="bar-bg"><div class="bar-fill" style="width:{{ cloud.api_surface }}%"></div></div>
        <div class="bar-label"><span>Config Extern.</span><span>{{ cloud.config_externalization }}</span></div>
        <div class="bar-bg"><div class="bar-fill" style="width:{{ cloud.config_externalization }}%"></div></div>
        <div class="bar-label"><span>Logging/Obs.</span><span>{{ cloud.logging_observability }}</span></div>
        <div class="bar-bg"><div class="bar-fill" style="width:{{ cloud.logging_observability }}%"></div></div>
        <div class="bar-label"><span>CI/CD</span><span>{{ cloud.ci_cd_artifacts }}</span></div>
        <div class="bar-bg"><div class="bar-fill" style="width:{{ cloud.ci_cd_artifacts }}%"></div></div>
      </div>
    </div>

    <!-- OSS Safety -->
    <div class="card">
      <h2>&#128274; Open Source Safety</h2>
      <div class="score">{{ oss.total }}
        <span style="font-size:1rem;color:#888">/ 100</span></div>
      <span class="label {{ oss.risk_label | replace(' ', '') }}">{{ oss.risk_label }}</span>
      <div style="margin-top:12px;font-size:.83rem;color:#aaa">
        <div>Dependencies: <strong>{{ oss.dependency_count }}</strong></div>
        <div>Vulnerable: <strong style="color:#f87171">{{ oss.vulnerable_count }}</strong></div>
        <div>License issues: <strong style="color:#fb923c">{{ oss.license_issues }}</strong></div>
        <div>Stale packages: <strong>{{ oss.stale_count }}</strong></div>
      </div>
      {% if oss.findings %}
      <div class="findings" style="margin-top:10px">
        {% for f in oss.findings %}<div class="finding-item">{{ f }}</div>{% endfor %}
      </div>
      {% endif %}
    </div>

    <!-- Business Impact -->
    <div class="card">
      <h2>&#128200; Business Impact</h2>
      <div class="score">{{ impact.total }}
        <span style="font-size:1rem;color:#888">/ 100</span></div>
      <span class="label {{ impact.risk_label }}">{{ impact.risk_label }}</span>
      <div class="bar-wrap">
        <div class="bar-label"><span>User Volume</span><span>{{ impact.user_volume_score }}</span></div>
        <div class="bar-bg"><div class="bar-fill" style="width:{{ impact.user_volume_score }}%"></div></div>
        <div class="bar-label"><span>Release Freq.</span><span>{{ impact.release_freq_score }}</span></div>
        <div class="bar-bg"><div class="bar-fill" style="width:{{ impact.release_freq_score }}%"></div></div>
        <div class="bar-label"><span>Revenue Impact</span><span>{{ impact.revenue_score }}</span></div>
        <div class="bar-bg"><div class="bar-fill" style="width:{{ impact.revenue_score }}%"></div></div>
        <div class="bar-label"><span>Age Risk</span><span>{{ impact.age_risk_score }}</span></div>
        <div class="bar-bg"><div class="bar-fill" style="width:{{ impact.age_risk_score }}%"></div></div>
      </div>
    </div>

  </div><!-- /grid -->

  <!-- Radar chart + Language breakdown -->
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:24px">
    <div class="chart-wrap">
      <h2 style="font-size:1rem;color:#61dafb;margin-bottom:12px;text-transform:uppercase">
        &#127919; Portfolio Radar
      </h2>
      <canvas id="radarChart" height="260"></canvas>
    </div>
    <div class="chart-wrap">
      <h2 style="font-size:1rem;color:#61dafb;margin-bottom:12px;text-transform:uppercase">
        &#128196; Language Breakdown
      </h2>
      <canvas id="langChart" height="260"></canvas>
    </div>
  </div>

  <!-- Language detail table -->
  <div class="chart-wrap">
    <h2 style="font-size:1rem;color:#61dafb;margin-bottom:12px;text-transform:uppercase">
      &#128295; Language Details
    </h2>
    <table class="lang-table">
      <thead>
        <tr>
          <th>Language</th><th>Files</th><th>SLOC</th>
          <th>Avg Complexity</th><th>Max Complexity</th>
          <th>Functions</th><th>Classes</th>
          <th>Long Methods %</th><th>Deep Nesting %</th>
          <th>Comment Ratio</th>
        </tr>
      </thead>
      <tbody>
        {% for r in lang_reports %}
        <tr>
          <td><strong>{{ r.language }}</strong></td>
          <td>{{ r.file_count }}</td>
          <td>{{ r.total_sloc }}</td>
          <td>{{ "%.1f"|format(r.avg_complexity) }}</td>
          <td>{{ r.max_complexity }}</td>
          <td>{{ r.total_functions }}</td>
          <td>{{ r.total_classes }}</td>
          <td>{{ "%.1f"|format(r.long_methods_pct) }}%</td>
          <td>{{ "%.1f"|format(r.deep_nesting_pct) }}%</td>
          <td>{{ "%.2f"|format(r.comment_ratio) }}</td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
  </div>

  <script>
  const radarData = {
    labels:['Health','Debt (inv)','Cloud','OSS Safety','Biz Impact'],
    datasets:[{
      label:'Scores',
      data:[{{ health.health }}, {{ 100 - debt.debt_ratio }},
            {{ cloud.total }}, {{ oss.total }}, {{ impact.total }}],
      backgroundColor:'rgba(97,218,251,0.15)',
      borderColor:'#61dafb',
      pointBackgroundColor:'#61dafb'
    }]
  };
  new Chart(document.getElementById('radarChart'),{
    type:'radar',
    data:radarData,
    options:{scales:{r:{min:0,max:100,grid:{color:'#2a2d3e'},
    ticks:{color:'#888',backdropColor:'transparent'},
    pointLabels:{color:'#aaa'}}},
    plugins:{legend:{display:false}}}
  });

  const langLabels = [{% for r in lang_reports %}"{{ r.language }}"{% if not loop.last %},{% endif %}{% endfor %}];
  const langSloc   = [{% for r in lang_reports %}{{ r.total_sloc }}{% if not loop.last %},{% endif %}{% endfor %}];
  const palette    = ['#61dafb','#4ade80','#fb923c','#a78bfa','#f472b6'];
  new Chart(document.getElementById('langChart'),{
    type:'doughnut',
    data:{labels:langLabels,datasets:[{data:langSloc,
      backgroundColor:palette.slice(0,langLabels.length),borderWidth:0}]},
    options:{plugins:{legend:{labels:{color:'#aaa'}}}}
  });
  </script>

  <footer>
    Generated by <strong>CodeAnalysis v1.0.0</strong> &mdash; {{ generated }}
  </footer>
</body>
</html>
"""


# Function: _default
def _default(obj: Any) -> Any:
    if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
        return dataclasses.asdict(obj)
    if isinstance(obj, Path):
        return str(obj)
    if isinstance(obj, set):
        return sorted(obj)
    raise TypeError(f"Not serialisable: {type(obj)}")


# Function: write_html
def write_html(result, output_dir: Path) -> Path:
    """
    Render the HTML dashboard and write it to *output_dir*.

    Returns the path to the written HTML file.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    safe_name = result.repo_name.replace("/", "_").replace("\\", "_")
    ts        = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path  = output_dir / f"{safe_name}_{ts}_report.html"

    env      = Environment(loader=BaseLoader(), autoescape=select_autoescape(["html", "xml"]))
    template = env.from_string(_TEMPLATE)

    html = template.render(
        repo_name    = result.repo_name,
        total_sloc   = result.total_sloc,
        file_count   = result.total_files,
        generated    = datetime.now().strftime("%Y-%m-%d %H:%M"),
        health       = result.health,
        debt         = result.debt,
        cloud        = result.cloud,
        oss          = result.oss,
        impact       = result.impact,
        lang_reports = result.language_reports,
    )

    out_path.write_text(html, encoding="utf-8")
    return out_path
