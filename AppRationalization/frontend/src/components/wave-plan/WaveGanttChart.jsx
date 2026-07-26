// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: AppRationalization — frontend/src/components/wave-plan (WaveGanttChart.jsx)
// Date: 2026-07-20
// ---------------------------------------------------------------------------
import React, { useMemo, useState } from 'react';
import { TSHIRT_RAMP, tshirtColor, statusColor, formatDate, formatDateShort } from './waveVisuals';

const LABEL_WIDTH = 240;
const ROW_HEIGHT = 34;
const BAR_HEIGHT = 20;
const EDGE_PADDING_DAYS = 5;

// Function: toDate
const toDate = (iso) => new Date(`${iso}T00:00:00`);
// Function: diffDays
const diffDays = (a, b) => Math.round((toDate(b) - toDate(a)) / 86400000);
// Function: addDays
const addDays = (iso, days) => {
  const d = toDate(iso);
  d.setDate(d.getDate() + days);
  return d.toISOString().slice(0, 10);
};

// Function: Badge — icon (colored dot) + plain-ink text, never colored text.
const Badge = ({ color, children }) => (
  <span className="inline-flex items-center gap-1.5 rounded-full bg-slate-800/80 px-2 py-0.5 text-[10px] font-medium text-slate-300">
    <span className="w-1.5 h-1.5 rounded-full shrink-0" style={{ backgroundColor: color }} />
    {children}
  </span>
);

// Function: WaveGanttChart
const WaveGanttChart = ({ plan }) => {
  const [view, setView] = useState('gantt');

  const timeline = useMemo(() => {
    if (!plan?.program_start || !plan?.program_end) return null;
    const displayStart = addDays(plan.program_start, -EDGE_PADDING_DAYS);
    const displayEnd = addDays(plan.program_end, EDGE_PADDING_DAYS);
    const totalDays = Math.max(1, diffDays(displayStart, displayEnd));
    // Function: pct
    const pct = (iso) => {
      if (!iso) return 0;
      return Math.min(100, Math.max(0, (diffDays(displayStart, iso) / totalDays) * 100));
    };

    const months = [];
    const cursor = toDate(displayStart);
    cursor.setDate(1);
    while (cursor.toISOString().slice(0, 10) <= displayEnd) {
      const iso = cursor.toISOString().slice(0, 10);
      if (iso >= displayStart) {
        months.push({ iso, label: cursor.toLocaleDateString(undefined, { month: 'short', year: 'numeric' }), pct: pct(iso) });
      }
      cursor.setMonth(cursor.getMonth() + 1);
    }

    const sprints = [];
    let sprintCursor = plan.program_start;
    while (sprintCursor <= plan.program_end) {
      sprints.push(pct(sprintCursor));
      sprintCursor = addDays(sprintCursor, plan.sprint_weeks * 7);
    }

    const cutovers = [...new Set(plan.waves.map((w) => w.cutover_date).filter(Boolean))]
      .map((iso) => ({ iso, pct: pct(iso) }));

    const todayIso = new Date().toISOString().slice(0, 10);
    const today = todayIso >= displayStart && todayIso <= displayEnd ? pct(todayIso) : null;

    return { pct, months, sprints, cutovers, today };
  }, [plan]);

  if (!plan || !plan.waves?.length || !timeline) {
    return (
      <div className="rounded-xl border border-slate-700 bg-slate-900/70 p-10 text-center text-slate-500">
        No wave plan generated yet.
      </div>
    );
  }

  return (
    <div className="rounded-xl border border-slate-700 bg-slate-900/70 overflow-hidden">
      {/* Header: legend + table toggle */}
      <div className="flex flex-wrap items-center justify-between gap-3 p-4 border-b border-slate-700">
        <div className="flex flex-wrap items-center gap-4">
          <span className="text-xs text-slate-400">T-Shirt Size</span>
          <div className="flex items-center gap-3">
            {Object.entries(TSHIRT_RAMP).map(([size, color]) => (
              <span key={size} className="inline-flex items-center gap-1.5 text-[11px] text-slate-300">
                <span className="w-3 h-3 rounded-sm shrink-0" style={{ backgroundColor: color }} />
                {size}
              </span>
            ))}
          </div>
          <span className="inline-flex items-center gap-1.5 text-[11px] text-slate-300">
            <span className="w-3 h-0 border-t-2 border-dashed border-cyan-400" /> Cutover
          </span>
          <span className="inline-flex items-center gap-1.5 text-[11px] text-slate-300">
            <span className="w-3 h-0 border-t-2 border-dashed border-amber-400" /> Today
          </span>
        </div>
        <div className="flex rounded-lg border border-slate-700 overflow-hidden text-xs">
          <button onClick={() => setView('gantt')}
            className={`px-3 py-1.5 ${view === 'gantt' ? 'bg-cyan-600 text-white' : 'bg-slate-900 text-slate-400 hover:text-white'}`}>
            Gantt
          </button>
          <button onClick={() => setView('table')}
            className={`px-3 py-1.5 ${view === 'table' ? 'bg-cyan-600 text-white' : 'bg-slate-900 text-slate-400 hover:text-white'}`}>
            Table
          </button>
        </div>
      </div>

      {view === 'table' ? (
        <div className="overflow-auto max-h-[65vh]">
          <table className="w-full text-xs">
            <thead className="sticky top-0 bg-slate-800 text-slate-300">
              <tr>
                {['Wave', 'App ID', 'Application', 'T-Shirt', 'Complexity', 'Risk', 'Sprint Start', 'Sprint End', 'Cutover', 'Rationale'].map((h) => (
                  <th key={h} className="text-left px-3 py-2 whitespace-nowrap">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {plan.waves.flatMap((wave) => wave.apps.map((app) => (
                <tr key={app.id} className="border-t border-slate-800 hover:bg-slate-800/50">
                  <td className="px-3 py-2 whitespace-nowrap">{wave.wave_name || `Wave ${wave.wave_number}`}</td>
                  <td className="px-3 py-2 whitespace-nowrap">{app.app_id}</td>
                  <td className="px-3 py-2 whitespace-nowrap">{app.application_name}{app.quick_win ? ' ★' : ''}</td>
                  <td className="px-3 py-2 whitespace-nowrap">{app.tshirt_size || '—'}</td>
                  <td className="px-3 py-2 whitespace-nowrap">{app.complexity || '—'}</td>
                  <td className="px-3 py-2 whitespace-nowrap">{app.risk || '—'}</td>
                  <td className="px-3 py-2 whitespace-nowrap">{formatDate(app.sprint_start)}</td>
                  <td className="px-3 py-2 whitespace-nowrap">{formatDate(app.sprint_end)}</td>
                  <td className="px-3 py-2 whitespace-nowrap">{formatDate(app.cutover_date)}</td>
                  <td className="px-3 py-2 min-w-[220px] max-w-sm whitespace-normal text-slate-400">{app.rationale}</td>
                </tr>
              )))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <div style={{ minWidth: 720 }}>
            {/* Ruler */}
            <div className="flex border-b border-slate-800">
              <div style={{ width: LABEL_WIDTH }} className="shrink-0 px-3 py-2 text-[10px] uppercase tracking-wider text-slate-500">
                Wave / Application
              </div>
              <div className="relative flex-1 h-8">
                {timeline.months.map((m) => (
                  <div key={m.iso} className="absolute top-0 h-full border-l border-slate-800/80 pl-1.5 text-[10px] text-slate-500"
                    style={{ left: `${m.pct}%` }}>
                    {m.label}
                  </div>
                ))}
              </div>
            </div>

            {/* Body */}
            <div className="relative">
              {/* Gridline overlay — aligned to the same left offset as every row's track */}
              <div className="absolute top-0 bottom-0 pointer-events-none" style={{ left: LABEL_WIDTH, right: 0 }}>
                {timeline.sprints.map((p, i) => (
                  <div key={`sprint-${i}`} className="absolute top-0 bottom-0 border-l border-slate-800/60" style={{ left: `${p}%` }} />
                ))}
                {timeline.cutovers.map((c) => (
                  <div key={`cutover-${c.iso}`} className="absolute top-0 bottom-0 border-l-2 border-dashed border-cyan-400/50"
                    style={{ left: `${c.pct}%` }} />
                ))}
                {timeline.today !== null && (
                  <div className="absolute top-0 bottom-0 border-l-2 border-dashed border-amber-400/70" style={{ left: `${timeline.today}%` }} />
                )}
              </div>

              {plan.waves.map((wave) => (
                <div key={wave.wave_number}>
                  {/* Wave header row */}
                  <div className="relative flex items-center bg-slate-800/40" style={{ height: ROW_HEIGHT }}>
                    <div style={{ width: LABEL_WIDTH }} className="shrink-0 px-3 text-xs font-semibold text-cyan-300 truncate">
                      {wave.wave_name || `Wave ${wave.wave_number}`}
                    </div>
                    <div className="flex-1 px-3 text-[11px] text-slate-400 truncate">
                      {formatDateShort(wave.start_date)} – {formatDateShort(wave.end_date)} · cutover {formatDateShort(wave.cutover_date)} · {wave.apps.length} app(s)
                    </div>
                  </div>

                  {/* App rows */}
                  {wave.apps.map((app) => {
                    const left = timeline.pct(app.sprint_start);
                    const right = timeline.pct(app.sprint_end);
                    const width = Math.max(right - left, 1.2);
                    return (
                      <div key={app.id} className="relative flex items-center border-t border-slate-800/60 hover:bg-slate-800/30"
                        style={{ height: ROW_HEIGHT }}>
                        <div style={{ width: LABEL_WIDTH }} className="shrink-0 px-3 flex items-center gap-1.5 min-w-0">
                          <span className="text-xs text-slate-200 truncate">{app.application_name || app.app_id}</span>
                          {app.quick_win && <span className="text-amber-400 shrink-0" title="Quick win">★</span>}
                        </div>
                        <div className="relative flex-1 h-full">
                          <div tabIndex={0} className="group absolute rounded outline-none focus:ring-2 focus:ring-cyan-400"
                            style={{
                              left: `${left}%`, width: `${width}%`, top: (ROW_HEIGHT - BAR_HEIGHT) / 2, height: BAR_HEIGHT,
                              backgroundColor: tshirtColor(app.tshirt_size),
                            }}>
                            <div className="pointer-events-none absolute z-20 hidden group-hover:block group-focus:block bottom-full left-0 mb-2 w-64 rounded-lg border border-slate-700 bg-slate-950 p-3 text-[11px] shadow-xl">
                              <p className="text-sm font-semibold text-white truncate">{app.application_name} <span className="text-slate-500">({app.app_id})</span></p>
                              <div className="mt-1.5 flex flex-wrap gap-1.5">
                                <Badge color={tshirtColor(app.tshirt_size)}>{app.tshirt_size || 'Unsized'}</Badge>
                                <Badge color={statusColor(app.complexity)}>Complexity: {app.complexity || '—'}</Badge>
                                <Badge color={statusColor(app.risk)}>Risk: {app.risk || '—'}</Badge>
                              </div>
                              <p className="mt-2 text-slate-400">Sprint: {formatDate(app.sprint_start)} → {formatDate(app.sprint_end)}</p>
                              <p className="text-slate-400">Cutover: {formatDate(app.cutover_date)}</p>
                              {app.migration_type && <p className="text-slate-400">Migration: {app.migration_type}</p>}
                              {app.rationale && <p className="mt-1.5 text-slate-300 border-t border-slate-800 pt-1.5">{app.rationale}</p>}
                            </div>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default WaveGanttChart;
