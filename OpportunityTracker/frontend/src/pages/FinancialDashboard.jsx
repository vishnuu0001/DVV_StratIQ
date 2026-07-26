// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: OpportunityTracker — frontend/src/pages (FinancialDashboard.jsx)
// Date: 2026-07-15
// ---------------------------------------------------------------------------
import React, { useCallback, useEffect, useState } from 'react';
import {
  Bar, BarChart, CartesianGrid, Cell, Legend, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis,
} from 'recharts';
import { Target, DollarSign, TrendingDown, Sparkles, AlertTriangle, RefreshCw } from 'lucide-react';
import toast from 'react-hot-toast';
import { getFinancialSummary, startFinancialNarrative, pollFinancialNarrative } from '../services/api';

const COLORS = ['#22d3ee', '#818cf8', '#34d399', '#fbbf24', '#f87171', '#a78bfa'];

// Function: StatTile
function StatTile({ icon: Icon, label, value, color }) {
  return (
    <div className="ot-card px-5 py-4 flex items-center gap-4">
      <div className={`h-10 w-10 rounded-xl flex items-center justify-center shrink-0 ${color}`}>
        <Icon size={18} className="text-white" />
      </div>
      <div>
        <p className="text-xs text-slate-400 uppercase tracking-wider">{label}</p>
        <p className="text-xl font-bold text-white mt-0.5">${value.toFixed(2)}M</p>
      </div>
    </div>
  );
}

// Function: FinancialDashboard
export default function FinancialDashboard({ refreshKey }) {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [guidance, setGuidance] = useState('');
  const [narrativeJob, setNarrativeJob] = useState(null);
  const [generating, setGenerating] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const { data } = await getFinancialSummary();
      setSummary(data);
    } catch {
      toast.error('Failed to load the financial summary.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load, refreshKey]);

  // Function: generateInsights
  const generateInsights = async () => {
    setGenerating(true);
    setNarrativeJob(null);
    try {
      const { data } = await startFinancialNarrative(guidance);
      const final = await pollFinancialNarrative(data.job_id, setNarrativeJob);
      setNarrativeJob(final);
      if (final.status === 'failed') {
        toast.error(final.error_message || 'Narrative generation failed.');
      }
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Could not generate insights.');
    } finally {
      setGenerating(false);
    }
  };

  if (loading || !summary) {
    return (
      <div className="h-40 flex items-center justify-center text-slate-500">
        <span className="w-6 h-6 rounded-full border-2 border-cyan-500 border-t-transparent animate-spin mr-3" />
        Loading financial summary…
      </div>
    );
  }

  const attainmentPie = [
    { name: 'Actual (Closed/Won)', value: summary.actual_fy27_mn },
    { name: 'Gap', value: Math.max(summary.gap_fy27_mn, 0) },
  ];

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <p className="text-sm text-slate-400">
          {summary.opportunity_count} opportunities · {summary.closed_won_count} closed/won · {summary.attainment_pct}% of target attained
        </p>
        <button onClick={load} className="ot-btn-secondary text-xs px-3 py-1.5">
          <RefreshCw size={13} className={loading ? 'animate-spin' : ''} /> Refresh
        </button>
      </div>

      {/* Stat tiles */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <StatTile icon={Target} label="Target FY'27" value={summary.target_fy27_mn} color="bg-violet-600" />
        <StatTile icon={DollarSign} label="Actual (Closed/Won)" value={summary.actual_fy27_mn} color="bg-emerald-600" />
        <StatTile icon={TrendingDown} label="Gap" value={summary.gap_fy27_mn} color="bg-red-600" />
      </div>

      {summary.data_quality?.blank_stage_count > 0 && (
        <div className="flex items-start gap-2 text-xs text-amber-400 bg-amber-500/10 border border-amber-500/25 rounded-lg px-4 py-3">
          <AlertTriangle size={14} className="shrink-0 mt-0.5" />
          <span>
            {summary.data_quality.blank_stage_count} opportunit{summary.data_quality.blank_stage_count === 1 ? 'y has' : 'ies have'} no
            Oppty Stage recorded — they still count toward the Target but can&rsquo;t count toward Actual until staged.
          </span>
        </div>
      )}

      {/* Breakdown charts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="ot-card p-5">
          <p className="text-sm font-semibold text-white mb-3">Target vs Actual</p>
          <ResponsiveContainer width="100%" height={220}>
            <PieChart>
              <Pie data={attainmentPie} dataKey="value" nameKey="name" innerRadius={50} outerRadius={80} paddingAngle={2}>
                {attainmentPie.map((_, i) => <Cell key={i} fill={i === 0 ? '#34d399' : '#f87171'} />)}
              </Pie>
              <Tooltip formatter={(v) => `$${Number(v).toFixed(2)}M`} />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="ot-card p-5">
          <p className="text-sm font-semibold text-white mb-3">By Region</p>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={summary.by_region}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="key" tick={{ fill: '#94a3b8', fontSize: 11 }} />
              <YAxis tick={{ fill: '#94a3b8', fontSize: 11 }} />
              <Tooltip formatter={(v) => `$${Number(v).toFixed(2)}M`} contentStyle={{ background: '#0f172a', border: '1px solid #334155' }} />
              <Bar dataKey="actual_fy27_mn" name="Actual" fill="#34d399" stackId="a" />
              <Bar dataKey="gap_fy27_mn" name="Gap" fill="#f87171" stackId="a" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="ot-card p-5">
          <p className="text-sm font-semibold text-white mb-3">By Stage</p>
          <ResponsiveContainer width="100%" height={220}>
            <PieChart>
              <Pie data={summary.by_stage} dataKey="target_fy27_mn" nameKey="key" outerRadius={80} label={(d) => d.key}>
                {summary.by_stage.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
              </Pie>
              <Tooltip formatter={(v) => `$${Number(v).toFixed(2)}M`} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Gap closure plan */}
      <div className="ot-card p-5">
        <p className="text-sm font-semibold text-white mb-1">
          Gap Closure Plan — {summary.deals_needed_to_close_gap} deal{summary.deals_needed_to_close_gap === 1 ? '' : 's'} needed to close the gap
        </p>
        <p className="text-xs text-slate-500 mb-3">Open deals ranked by stage maturity, then value — closest-to-closing first.</p>
        {summary.gap_closure_plan.length === 0 ? (
          <p className="text-sm text-slate-500">No open deals available, or the gap is already closed.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="ot-table">
              <thead>
                <tr>
                  <th>Opportunity</th>
                  <th>Customer</th>
                  <th>Stage</th>
                  <th className="commercial">FY&apos;27 $Mn</th>
                  <th className="commercial">Running Total</th>
                </tr>
              </thead>
              <tbody>
                {summary.gap_closure_plan.map((d) => (
                  <tr key={d.id}>
                    <td>{d.opportunity_name}</td>
                    <td>{d.customer_group}</td>
                    <td className="text-xs text-slate-400">{d.oppty_stage}</td>
                    <td className="font-mono text-cyan-200">{d.fy27_mn.toFixed(2)}</td>
                    <td className="font-mono text-slate-300">{d.running_total_fy27_mn.toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Ollama insights */}
      <div className="ot-card p-5 space-y-3">
        <div className="flex items-center justify-between">
          <p className="text-sm font-semibold text-white flex items-center gap-2">
            <Sparkles size={15} className="text-cyan-400" /> Ollama Gap Analysis
          </p>
        </div>
        <textarea
          className="ot-input w-full text-xs resize-y min-h-[60px]"
          placeholder="Optional guidance for this analysis, e.g. 'Focus on Europe' or 'Emphasize deals with an assigned owner.'"
          value={guidance}
          onChange={(e) => setGuidance(e.target.value)}
        />
        <button
          type="button"
          className="ot-btn-primary text-sm px-4 py-2.5"
          disabled={generating}
          onClick={generateInsights}
        >
          <Sparkles size={16} />
          {generating ? (narrativeJob?.status === 'running' ? 'Generating…' : 'Starting…') : 'Generate Insights'}
        </button>

        {narrativeJob?.status === 'done' && narrativeJob.narrative_text && (
          <div className="mt-2 p-4 rounded-lg bg-slate-900/60 border border-slate-800 text-sm text-slate-200 leading-relaxed">
            {narrativeJob.narrative_text}
            {narrativeJob.llm_model && (
              <p className="mt-2 text-[11px] text-slate-500">Generated by {narrativeJob.llm_model}</p>
            )}
          </div>
        )}
        {narrativeJob?.status === 'failed' && (
          <div className="mt-2 p-4 rounded-lg bg-red-500/10 border border-red-500/25 text-sm text-red-300">
            {narrativeJob.error_message || 'Narrative generation failed.'}
          </div>
        )}
      </div>
    </div>
  );
}
