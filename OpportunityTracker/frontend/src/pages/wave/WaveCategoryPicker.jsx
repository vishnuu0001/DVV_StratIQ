// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: OpportunityTracker — frontend/src/pages/wave (WaveCategoryPicker.jsx)
// Date: 2026-02-25
// ---------------------------------------------------------------------------
import React from 'react';
import { Layers, AlertTriangle, ChevronRight, XCircle } from 'lucide-react';

// Function: WaveCategoryPicker
export default function WaveCategoryPicker({ categories, onSelect }) {
  return (
    <div className="grid sm:grid-cols-2 xl:grid-cols-3 gap-4">
      {categories.map((c) => (
        <button
          key={c.category}
          type="button"
          onClick={() => c.status === 'done' && onSelect(c.category)}
          disabled={c.status !== 'done'}
          className="ot-card p-5 text-left flex flex-col gap-3 hover:border-cyan-500/40 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <div className="flex items-start justify-between gap-2">
            <div className="h-9 w-9 rounded-xl bg-violet-600/90 flex items-center justify-center shrink-0">
              <Layers size={16} className="text-white" />
            </div>
            {c.status === 'failed' ? (
              <XCircle size={16} className="text-red-400 shrink-0" />
            ) : (
              <ChevronRight size={16} className="text-slate-500 shrink-0" />
            )}
          </div>
          <div>
            <p className="text-sm font-semibold text-white leading-snug">{c.category}</p>
          </div>

          {c.status === 'failed' ? (
            <p className="text-xs text-red-400">{c.error_message || 'Analysis failed for this category.'}</p>
          ) : (
            <div className="grid grid-cols-3 gap-2 text-center mt-1">
              <div>
                <p className="text-lg font-bold text-cyan-400">{c.actual_app_count}</p>
                <p className="text-[10px] uppercase text-slate-500">Apps</p>
              </div>
              <div>
                <p className="text-lg font-bold text-violet-400">{c.wave_count}</p>
                <p className="text-[10px] uppercase text-slate-500">Waves</p>
              </div>
              <div className="flex flex-col items-center">
                <p className={`text-lg font-bold ${c.data_quality_issues ? 'text-amber-400' : 'text-emerald-400'}`}>
                  {c.data_quality_issues}
                </p>
                <p className="text-[10px] uppercase text-slate-500 flex items-center gap-0.5">
                  {c.data_quality_issues > 0 && <AlertTriangle size={9} />} Flags
                </p>
              </div>
            </div>
          )}

          {c.timeline_start && (
            <p className="text-[11px] text-slate-500 border-t border-slate-800 pt-2 mt-1">
              {c.timeline_start} → {c.timeline_end}
            </p>
          )}
        </button>
      ))}
    </div>
  );
}
