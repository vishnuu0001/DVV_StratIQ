// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: OpportunityTracker — frontend/src/pages/wave (WaveGanttChart.jsx)
// Date: 2025-11-11
// ---------------------------------------------------------------------------
import React, { useMemo } from 'react';

const PHASE_COLOR = {
  'Remed.': 'bg-amber-500/70',
  'Assess.': 'bg-cyan-500/70',
  'Migr.': 'bg-violet-500/70',
  'Test/CO': 'bg-blue-500/70',
  'AMS': 'bg-emerald-500/70',
  'Steady': 'bg-slate-600/70',
};

// Function: WaveGanttChart
export default function WaveGanttChart({ rows }) {
  const quarters = useMemo(() => {
    const all = new Set();
    rows.forEach((r) => {
      const idx = quarterIndex(r.start_quarter);
      r.phases.forEach((_, i) => all.add(idx + i));
    });
    return Array.from(all).sort((a, b) => a - b);
  }, [rows]);

  if (!rows.length) {
    return <p className="text-sm text-slate-500 py-6 text-center">No timeline data available.</p>;
  }

  return (
    <div className="ot-table-wrap">
      <div className="min-w-[720px]">
        <div className="grid text-[11px] text-slate-500 mb-2" style={{ gridTemplateColumns: `220px 60px repeat(${quarters.length}, 1fr)` }}>
          <div>Wave / Phase</div>
          <div className="text-center">Apps</div>
          {quarters.map((q) => (
            <div key={q} className="text-center font-mono">{quarterLabel(q)}</div>
          ))}
        </div>
        {rows.map((r) => {
          const startIdx = quarterIndex(r.start_quarter);
          return (
            <div key={r.label} className="grid items-center py-1.5 border-t border-slate-800/60" style={{ gridTemplateColumns: `220px 60px repeat(${quarters.length}, 1fr)` }}>
              <div className="text-xs text-slate-300 truncate pr-2" title={r.label}>{r.label}</div>
              <div className="text-xs text-center text-slate-400">{r.app_count}</div>
              {quarters.map((q) => {
                const phaseIdx = q - startIdx;
                const phase = phaseIdx >= 0 && phaseIdx < r.phases.length ? r.phases[phaseIdx] : null;
                return (
                  <div key={q} className="px-0.5">
                    {phase && (
                      <div className={`text-[10px] text-white text-center rounded py-0.5 ${PHASE_COLOR[phase] || 'bg-slate-600/70'}`}>
                        {phase}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          );
        })}
      </div>
    </div>
  );
}

// Function: quarterIndex
function quarterIndex(q) {
  const m = /Q(\d) (\d+)/.exec(q || '');
  if (!m) return 0;
  return parseInt(m[2], 10) * 4 + (parseInt(m[1], 10) - 1);
}

// Function: quarterLabel
function quarterLabel(idx) {
  const y = Math.floor(idx / 4);
  const q = (idx % 4) + 1;
  return `Q${q} ${y}`;
}
