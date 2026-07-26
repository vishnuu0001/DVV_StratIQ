// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: OpportunityTracker — frontend/src/pages/wave (WaveTable.jsx)
// Date: 2026-01-30
// ---------------------------------------------------------------------------
import React, { useState } from 'react';
import { ChevronDown, ChevronRight, AlertTriangle } from 'lucide-react';

const MIGRATION_TYPE_BADGE = {
  'Functional Migration Only': 'bg-cyan-500/15 text-cyan-300 border-cyan-500/30',
  'Full Consolidation': 'bg-violet-500/15 text-violet-300 border-violet-500/30',
  'Data Migration Only': 'bg-amber-500/15 text-amber-300 border-amber-500/30',
  'N/A (Modernization Track)': 'bg-slate-500/15 text-slate-400 border-slate-500/30',
  'TBD (data gap)': 'bg-slate-500/15 text-slate-400 border-slate-500/30',
};

const DISPOSITION_BADGE = {
  Harmonization: 'bg-cyan-500/15 text-cyan-300 border-cyan-500/30',
  Modernization: 'bg-orange-500/15 text-orange-300 border-orange-500/30',
};

// Function: WaveTable
export default function WaveTable({ apps }) {
  const [expanded, setExpanded] = useState(() => new Set());

  // Function: toggle
  const toggle = (appId) => {
    setExpanded((prev) => {
      const next = new Set(prev);
      if (next.has(appId)) next.delete(appId); else next.add(appId);
      return next;
    });
  };

  if (!apps.length) {
    return <p className="text-sm text-slate-500 py-6 text-center">No applications in this view.</p>;
  }

  return (
    <div className="ot-table-wrap">
      <table className="ot-table">
        <thead>
          <tr>
            <th style={{ width: 28 }} />
            <th>App ID</th>
            <th>Application name</th>
            <th>Dept</th>
            <th>Disposition</th>
            <th>Migration type</th>
            <th>Data quality</th>
          </tr>
        </thead>
        <tbody>
          {apps.map((a) => {
            const isOpen = expanded.has(a.app_id);
            return (
              <React.Fragment key={a.app_id}>
                <tr className="cursor-pointer" onClick={() => toggle(a.app_id)}>
                  <td>{isOpen ? <ChevronDown size={14} /> : <ChevronRight size={14} />}</td>
                  <td className="font-mono text-xs">{a.app_id}</td>
                  <td>{a.app_name}</td>
                  <td>{a.dept}</td>
                  <td>
                    <span className={`text-[11px] px-2 py-0.5 rounded-full border ${DISPOSITION_BADGE[a.disposition] || ''}`}>
                      {a.disposition}{a.service_module ? ` · ${a.service_module}` : ''}
                    </span>
                  </td>
                  <td>
                    <span className={`text-[11px] px-2 py-0.5 rounded-full border ${MIGRATION_TYPE_BADGE[a.migration_type] || ''}`}>
                      {a.migration_type}
                    </span>
                  </td>
                  <td>
                    {a.data_quality_flag ? (
                      <span className="inline-flex items-center gap-1 text-amber-400 text-xs">
                        <AlertTriangle size={12} /> Flagged
                      </span>
                    ) : (
                      <span className="text-emerald-400 text-xs">Clean</span>
                    )}
                  </td>
                </tr>
                {isOpen && (
                  <tr>
                    <td colSpan={7} className="bg-slate-900/60">
                      <div className="p-4 space-y-3 text-xs text-slate-300 leading-relaxed">
                        <div>
                          <p className="text-slate-500 uppercase tracking-wide text-[10px] mb-1">Capabilities</p>
                          <p>{a.capabilities_raw || '—'}</p>
                        </div>
                        <div>
                          <p className="text-slate-500 uppercase tracking-wide text-[10px] mb-1">
                            Disposition rationale{a.modernization_trigger_category ? ` (trigger: ${a.modernization_trigger_category})` : ''}
                          </p>
                          <p>{a.disposition_rationale || '—'}</p>
                        </div>
                        <div>
                          <p className="text-slate-500 uppercase tracking-wide text-[10px] mb-1">Notes / assumptions</p>
                          <p>{a.notes_assumptions || '—'}</p>
                        </div>
                        <div>
                          <p className="text-slate-500 uppercase tracking-wide text-[10px] mb-1">Wave assignment rationale</p>
                          <p>{a.wave_assignment_rationale || '—'}</p>
                        </div>
                        {a.rejoins_wave && (
                          <div>
                            <p className="text-slate-500 uppercase tracking-wide text-[10px] mb-1">Remediation rejoin</p>
                            <p>Rejoins {a.rejoins_wave} — {a.rejoin_rationale}</p>
                          </div>
                        )}
                        <div className="grid grid-cols-3 gap-3 pt-2 border-t border-slate-800 text-[11px]">
                          <span><span className="text-slate-500">Business owner:</span> {a.business_owner || '—'}</span>
                          <span><span className="text-slate-500">IT owner:</span> {a.it_owner || '—'}</span>
                          <span><span className="text-slate-500">Capability tier:</span> {a.capability_tier || '—'}</span>
                        </div>
                      </div>
                    </td>
                  </tr>
                )}
              </React.Fragment>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
