// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: AppRationalization — frontend/src/components/wave-plan (WaveScheduleGantt.jsx)
// Date: 2026-07-20
// ---------------------------------------------------------------------------
// Stage-segmented Harmonization Wave Delivery Gantt — mirrors the
// Gantt_View sheet of BASF_Harmonization_Wave_Gantt_Schedule.xlsx: each wave
// bar is five contiguous stage segments (Initiation/Assessment/Migration/
// Testing/Stabilisation) plus two milestone markers (Cutover, Gate Review),
// with phase bands across the top showing where each complexity tier enters
// the programme (matching the reference "Simple+Medium / +Complex /
// +Very Complex" roadmap image).
import React from 'react';
import { formatDate, formatDateShort } from './waveVisuals';

const LABEL_WIDTH = 96;
const ROW_HEIGHT = 44;
const BAR_HEIGHT = 22;
const EDGE_PADDING_DAYS = 10;

const STAGE_COLORS = {
  initiation: '#9DC3E6',
  assessment: '#2E75B6',
  migration: '#1F4E79',
  testing: '#548235',
  stabilisation: '#A9D18E',
};
const STAGE_LABELS = {
  initiation: 'Wave Initiation',
  assessment: 'Assessment',
  migration: 'Migration',
  testing: 'Testing & Validation',
  stabilisation: 'Stabilisation / Hypercare',
};
const CUTOVER_COLOR = '#f59e0b';
const GATE_REVIEW_COLOR = '#eab308';

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

// Function: phaseBands
const phaseBands = (schedule) => {
  const { waves, complex_from_wave: complexFrom, very_complex_from_wave: veryComplexFrom } = schedule;
  if (!waves.length) return [];
  const byNumber = Object.fromEntries(waves.map((w) => [w.wave_number, w]));
  const lastWave = waves[waves.length - 1].wave_number;
  const bands = [];
  const phase1End = Math.min(complexFrom - 1, lastWave);
  if (phase1End >= 1 && byNumber[1]) {
    bands.push({ label: 'Simple + Medium', start: byNumber[1].start_date, end: (byNumber[phase1End] || byNumber[1]).gate_review_date });
  }
  if (complexFrom <= lastWave) {
    const phase2End = Math.min(veryComplexFrom - 1, lastWave);
    if (byNumber[complexFrom]) {
      bands.push({ label: '+ Complex', start: byNumber[complexFrom].start_date, end: (byNumber[phase2End] || byNumber[complexFrom]).gate_review_date });
    }
  }
  if (veryComplexFrom <= lastWave && byNumber[veryComplexFrom]) {
    bands.push({ label: '+ Very Complex', start: byNumber[veryComplexFrom].start_date, end: byNumber[lastWave].gate_review_date });
  }
  return bands;
};

// Function: WaveScheduleGantt
const WaveScheduleGantt = ({ schedule }) => {
  if (!schedule || !schedule.waves?.length) {
    return (
      <div className="rounded-xl border border-slate-700 bg-slate-900/70 p-10 text-center text-slate-500">
        No wave schedule calculated yet.
      </div>
    );
  }

  const displayStart = addDays(schedule.program_start, -EDGE_PADDING_DAYS);
  const displayEnd = addDays(schedule.program_end, EDGE_PADDING_DAYS);
  const totalDays = Math.max(1, diffDays(displayStart, displayEnd));
  // Function: pct
  const pct = (iso) => Math.min(100, Math.max(0, (diffDays(displayStart, iso) / totalDays) * 100));

  const months = [];
  const cursor = toDate(displayStart);
  cursor.setDate(1);
  while (cursor.toISOString().slice(0, 10) <= displayEnd) {
    const iso = cursor.toISOString().slice(0, 10);
    if (iso >= displayStart) months.push({ iso, label: cursor.toLocaleDateString(undefined, { month: 'short', year: '2-digit' }), pct: pct(iso) });
    cursor.setMonth(cursor.getMonth() + 1);
  }

  const bands = phaseBands(schedule);
  const tasksByWave = {};
  schedule.tasks.forEach((t) => { (tasksByWave[t.wave_number] ||= []).push(t); });

  return (
    <div className="wave-gantt rounded-xl border border-slate-700 bg-slate-900/70 overflow-hidden">
      <div className="flex flex-wrap items-center gap-4 p-4 border-b border-slate-700">
        {Object.entries(STAGE_LABELS).map(([key, label]) => (
          <span key={key} className="inline-flex items-center gap-1.5 text-xs font-medium text-slate-300">
            <span className="w-3 h-3 rounded-sm shrink-0" style={{ backgroundColor: STAGE_COLORS[key] }} />
            {label}
          </span>
        ))}
        <span className="inline-flex items-center gap-1.5 text-xs font-medium text-slate-300">
          <span className="inline-block w-0 h-0 border-l-[5px] border-l-transparent border-r-[5px] border-r-transparent border-b-[8px]" style={{ borderBottomColor: CUTOVER_COLOR }} />
          Cutover
        </span>
        <span className="inline-flex items-center gap-1.5 text-xs font-medium text-slate-300">
          <span className="w-2.5 h-2.5 rotate-45 shrink-0" style={{ backgroundColor: GATE_REVIEW_COLOR }} />
          Gate Review
        </span>
      </div>

      <div className="overflow-x-auto">
        <div style={{ minWidth: 760 }}>
          {/* Phase bands */}
          <div className="flex border-b border-slate-800">
            <div style={{ width: LABEL_WIDTH }} className="shrink-0" />
            <div className="relative flex-1 h-9">
              {bands.map((b) => (
                <div key={b.label} className="absolute top-2 text-center text-xs font-semibold text-slate-300 -translate-x-1/2"
                  style={{ left: `${(pct(b.start) + pct(b.end)) / 2}%` }}>
                  {b.label}
                </div>
              ))}
              {bands.slice(1).map((b) => (
                <div key={`sep-${b.label}`} className="absolute top-0 bottom-0 border-l border-dashed border-slate-600"
                  style={{ left: `${pct(b.start)}%` }} />
              ))}
            </div>
          </div>

          {/* Ruler */}
          <div className="flex border-b border-slate-800">
            <div style={{ width: LABEL_WIDTH }} className="shrink-0 px-2 py-2 text-xs font-semibold uppercase tracking-wider text-slate-500">Wave</div>
            <div className="relative flex-1 h-7">
              {months.map((m) => (
                <div key={m.iso} className="absolute top-0 h-full border-l border-slate-800/80 pl-1 text-xs text-slate-500" style={{ left: `${m.pct}%` }}>
                  {m.label}
                </div>
              ))}
            </div>
          </div>

          {/* Body */}
          <div className="relative">
            <div className="absolute top-0 bottom-0 pointer-events-none" style={{ left: LABEL_WIDTH, right: 0 }}>
              {bands.slice(1).map((b) => (
                <div key={`gridsep-${b.label}`} className="absolute top-0 bottom-0 border-l border-dashed border-slate-700/70" style={{ left: `${pct(b.start)}%` }} />
              ))}
            </div>

            {schedule.waves.map((w) => {
              const stages = (tasksByWave[w.wave_number] || []).filter((t) => STAGE_COLORS[t.task_type]);
              const cutoverTask = (tasksByWave[w.wave_number] || []).find((t) => t.task_type === 'cutover');
              const gateTask = (tasksByWave[w.wave_number] || []).find((t) => t.task_type === 'gate_review');
              const barLeft = pct(w.start_date);
              const barRight = pct(w.gate_review_date);
              return (
                <div key={w.wave_number} className="relative flex items-center border-t border-slate-800/60 hover:bg-slate-800/30" style={{ height: ROW_HEIGHT }}>
                  <div style={{ width: LABEL_WIDTH }} className="shrink-0 px-2">
                    <p className="text-xs font-semibold text-white">Wave {w.wave_number}</p>
                    <p className="text-xs text-slate-500">{w.application_count} apps</p>
                  </div>
                  <div className="relative flex-1 h-full">
                    <div tabIndex={0} className="group absolute rounded overflow-hidden outline-none focus:ring-2 focus:ring-cyan-400 flex"
                      style={{ left: `${barLeft}%`, width: `${Math.max(barRight - barLeft, 1)}%`, top: (ROW_HEIGHT - BAR_HEIGHT) / 2, height: BAR_HEIGHT }}>
                      {stages.map((s) => {
                        const segLeft = ((pct(s.start_date) - barLeft) / (barRight - barLeft)) * 100;
                        const segWidth = ((pct(s.end_date) - pct(s.start_date)) / (barRight - barLeft)) * 100;
                        return (
                          <div key={s.wbs_code} className="absolute top-0 bottom-0" style={{ left: `${segLeft}%`, width: `${segWidth}%`, backgroundColor: STAGE_COLORS[s.task_type] }} />
                        );
                      })}
                      <div className="wave-tooltip pointer-events-none absolute z-20 hidden group-hover:block group-focus:block bottom-full left-0 mb-2 w-80 rounded-lg border border-slate-700 bg-slate-950 p-4 text-xs shadow-xl">
                        <p className="text-sm font-semibold text-white">Wave {w.wave_number}</p>
                        <p className="text-slate-400 mt-1">{w.permitted_complexity}</p>
                        <p className="text-slate-400">Start {formatDate(w.start_date)} · Cutover {formatDate(w.cutover_date)} · Gate Review {formatDate(w.gate_review_date)}</p>
                        <p className="text-slate-400">{w.application_count} apps · {Math.round(w.effort_hours).toLocaleString()} hrs · {w.quick_win_count} quick win(s)</p>
                        <p className="text-slate-400">S {w.simple_count} · M {w.medium_count} · C {w.complex_count} · VC {w.very_complex_count}</p>
                      </div>
                    </div>
                    {cutoverTask && (
                      <div className="absolute" style={{ left: `${pct(cutoverTask.start_date)}%`, top: (ROW_HEIGHT - BAR_HEIGHT) / 2 - 9, transform: 'translateX(-50%)' }} title={`Cutover — ${formatDateShort(cutoverTask.start_date)}`}>
                        <div className="w-0 h-0 border-l-[6px] border-l-transparent border-r-[6px] border-r-transparent border-b-[9px]" style={{ borderBottomColor: CUTOVER_COLOR }} />
                      </div>
                    )}
                    {gateTask && (
                      <div className="absolute w-2.5 h-2.5 rotate-45" style={{ left: `${pct(gateTask.start_date)}%`, top: (ROW_HEIGHT - BAR_HEIGHT) / 2 + BAR_HEIGHT / 2 - 5, transform: 'translateX(-50%) rotate(45deg)', backgroundColor: GATE_REVIEW_COLOR }}
                        title={`Gate Review — ${formatDateShort(gateTask.start_date)}`} />
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};

export default WaveScheduleGantt;
