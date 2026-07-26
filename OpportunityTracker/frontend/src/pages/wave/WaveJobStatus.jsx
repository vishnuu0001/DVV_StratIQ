// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: OpportunityTracker — frontend/src/pages/wave (WaveJobStatus.jsx)
// Date: 2025-10-30
// ---------------------------------------------------------------------------
import React from 'react';
import { Loader2, CheckCircle2, XCircle, Clock } from 'lucide-react';

const STATUS_ICON = {
  pending: <Clock size={12} className="text-slate-500" />,
  running: <Loader2 size={12} className="text-cyan-400 animate-spin" />,
  done: <CheckCircle2 size={12} className="text-emerald-400" />,
  failed: <XCircle size={12} className="text-red-400" />,
};

// Function: WaveJobStatus
export default function WaveJobStatus({ job }) {
  if (!job) return null;
  const pct = job.total_categories ? Math.round((job.completed_categories / job.total_categories) * 100) : 0;

  return (
    <div className="ot-card p-5 space-y-4">
      <div className="flex items-center justify-between">
        <p className="text-sm font-semibold text-white">
          Analyzing {job.total_categories} categories
          {job.llm_model && <span className="text-slate-500 font-normal"> · {job.llm_model}</span>}
        </p>
        <span className="text-xs font-mono text-cyan-400">{job.completed_categories}/{job.total_categories}</span>
      </div>

      <div className="h-2 rounded-full bg-slate-800 overflow-hidden">
        <div className="h-full bg-gradient-to-r from-cyan-500 to-violet-500 transition-all" style={{ width: `${pct}%` }} />
      </div>

      <div className="grid sm:grid-cols-2 gap-1.5 max-h-64 overflow-y-auto pr-1">
        {job.categories.map((c) => (
          <div key={c.category} className="flex items-center gap-2 text-xs px-2.5 py-1.5 rounded-lg bg-slate-900/60 min-w-0">
            {STATUS_ICON[c.status] || STATUS_ICON.pending}
            <span className="min-w-0 flex-1">
              <span className="block truncate text-slate-300" title={c.category}>{c.category}</span>
              {c.status === 'running' && c.current_step && (
                <span className="block truncate text-[10px] text-cyan-400/80">{c.current_step}</span>
              )}
              {c.status === 'failed' && c.error_message && (
                <span className="block truncate text-[10px] text-red-400" title={c.error_message}>{c.error_message}</span>
              )}
            </span>
          </div>
        ))}
      </div>

      {job.status === 'failed' && job.error_message && (
        <p className="text-xs text-red-400">{job.error_message}</p>
      )}
    </div>
  );
}
