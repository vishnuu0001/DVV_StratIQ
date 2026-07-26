// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: AppRationalization — frontend/src/components/wave-plan (WaveAppsDrilldown.jsx)
// Date: 2026-07-20
// ---------------------------------------------------------------------------
// Shared L2 (Topic) / L3 (Application) drill-down, embedded under an
// expanded wave row in both the Wave Summary and Task List (WBS) tabs.
import React, { useMemo } from 'react';
import { ChevronRight } from 'lucide-react';
import { tierColor } from './waveVisuals';

const APP_COLUMNS = [
  'App ID', 'Application', 'Complexity', 'T-Shirt', 'Migration Type', 'Quick Win', 'Effort (hrs)', 'Dependencies',
  'Assessment Sprint', 'Migration Sprints', 'QA/UAT Sprint', 'Go-Live PI', 'Stabilization', 'Decommissioning',
];

// Function: groupByTopic
const groupByTopic = (apps) => {
  const map = {};
  apps.forEach((a) => {
    const key = a.topic || 'Unspecified topic';
    if (!map[key]) {
      map[key] = { topic: key, apps: [], effort: 0, quickWins: 0, simple: 0, medium: 0, complex: 0, veryComplex: 0 };
    }
    const g = map[key];
    g.apps.push(a);
    g.effort += a.effort_hours || 0;
    if (a.quick_win) g.quickWins += 1;
    if (a.complexity_tier === 'simple') g.simple += 1;
    else if (a.complexity_tier === 'medium') g.medium += 1;
    else if (a.complexity_tier === 'complex') g.complex += 1;
    else if (a.complexity_tier === 'very_complex') g.veryComplex += 1;
  });
  return Object.values(map).sort((a, b) => b.apps.length - a.apps.length);
};

// Function: WaveAppsDrilldown
// L2 = topic groups within the wave, L3 = individual applications within a topic.
// Function: WaveAppsDrilldown
const WaveAppsDrilldown = ({ waveNumber, apps, expandedTopics, onToggleTopic }) => {
  const topics = useMemo(() => groupByTopic(apps || []), [apps]);

  if (!topics.length) {
    return <div className="px-6 py-3 text-[11px] text-slate-500">No applications in this wave.</div>;
  }

  return (
    <div className="bg-slate-950/60">
      {topics.map((g) => {
        const key = `${waveNumber}:${g.topic}`;
        const open = expandedTopics.has(key);
        return (
          <div key={key} className="border-b border-slate-900 last:border-b-0">
            <button type="button" onClick={() => onToggleTopic(key)}
              className="w-full flex items-center justify-between gap-3 px-6 py-2 text-left hover:bg-slate-900/60">
              <span className="flex items-center gap-2 text-xs text-slate-200 min-w-0">
                <ChevronRight className={`w-3.5 h-3.5 shrink-0 text-cyan-400 transition-transform ${open ? 'rotate-90' : ''}`} />
                <span className="truncate">{g.topic}</span>
              </span>
              <span className="text-[11px] text-slate-500 whitespace-nowrap">
                {g.apps.length} app(s) · {Math.round(g.effort).toLocaleString()} hrs · {g.quickWins} quick win(s) ·
                {' '}S {g.simple} / M {g.medium} / C {g.complex} / VC {g.veryComplex}
              </span>
            </button>
            {open && (
              <div className="overflow-x-auto">
                <table className="w-full text-[11px]">
                  <thead className="text-slate-500">
                    <tr>
                      {APP_COLUMNS.map((h) => <th key={h} className="text-left pl-12 pr-3 py-1.5 font-medium whitespace-nowrap">{h}</th>)}
                    </tr>
                  </thead>
                  <tbody>
                    {g.apps.map((a) => (
                      <tr key={a.app_id} className="border-t border-slate-900/80 hover:bg-slate-900/40">
                        <td className="pl-12 pr-3 py-1.5 whitespace-nowrap text-slate-300">{a.app_id}</td>
                        <td className="pl-12 pr-3 py-1.5 whitespace-nowrap text-slate-300">{a.application_name || '—'}</td>
                        <td className="pl-12 pr-3 py-1.5 whitespace-nowrap">
                          <span className="inline-flex items-center gap-1.5">
                            <span className="w-1.5 h-1.5 rounded-full shrink-0" style={{ backgroundColor: tierColor(a.complexity_tier) }} />
                            {a.complexity || '—'}
                          </span>
                        </td>
                        <td className="pl-12 pr-3 py-1.5 whitespace-nowrap text-slate-400">{a.tshirt_size || '—'}</td>
                        <td className="pl-12 pr-3 py-1.5 whitespace-nowrap text-slate-400">{a.migration_type || '—'}</td>
                        <td className="pl-12 pr-3 py-1.5 whitespace-nowrap text-amber-400">{a.quick_win ? '★' : ''}</td>
                        <td className="pl-12 pr-3 py-1.5 whitespace-nowrap text-slate-400">{a.effort_hours != null ? Math.round(a.effort_hours).toLocaleString() : '—'}</td>
                        <td className="pl-12 pr-3 py-1.5 whitespace-nowrap text-slate-400">{a.dependencies || '—'}</td>
                        <td className="pl-12 pr-3 py-1.5 whitespace-nowrap text-slate-400">{a.assessment_sprint != null ? `Sprint ${a.assessment_sprint}` : '—'}</td>
                        <td className="pl-12 pr-3 py-1.5 whitespace-nowrap text-slate-400">{a.migration_sprint_start != null ? `Sprint ${a.migration_sprint_start}-${a.migration_sprint_end}` : '—'}</td>
                        <td className="pl-12 pr-3 py-1.5 whitespace-nowrap text-slate-400">{a.qa_uat_sprint != null ? `Sprint ${a.qa_uat_sprint}` : '—'}</td>
                        <td className="pl-12 pr-3 py-1.5 whitespace-nowrap text-cyan-300">{a.go_live_pi || '—'}</td>
                        <td className="pl-12 pr-3 py-1.5 whitespace-nowrap text-slate-400">{a.stabilization_pi || '—'}</td>
                        <td className="pl-12 pr-3 py-1.5 whitespace-nowrap text-slate-400">{a.decommissioning_pi || '—'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
};

export default WaveAppsDrilldown;
