// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: AppRationalization — frontend/src/components (WavePlanCreation.jsx)
// Date: 2026-07-20
// ---------------------------------------------------------------------------
import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { toast } from 'react-toastify';
import { Loader2, Sparkles } from 'lucide-react';
import { getWavePlanTopics, generateWavePlan } from '../services/api';
import WaveGanttChart from './wave-plan/WaveGanttChart';
import { modelDisplayName } from '../utils/modelDisplay';

// Function: StatTile
const StatTile = ({ label, value, accent }) => (
  <div className="rounded-lg border border-slate-700 bg-slate-950/60 px-4 py-3">
    <p className="text-[10px] uppercase tracking-wider text-slate-500">{label}</p>
    <p className={`text-xl font-semibold mt-1 ${accent || 'text-white'}`}>{value}</p>
  </div>
);

// Function: WavePlanCreation
const WavePlanCreation = () => {
  const [topics, setTopics] = useState([]);
  const [topic, setTopic] = useState('');
  const [parallelStreams, setParallelStreams] = useState(3);
  const [programStart, setProgramStart] = useState(() => new Date().toISOString().slice(0, 10));
  const [busy, setBusy] = useState(false);
  const [loadingTopics, setLoadingTopics] = useState(true);
  const [plan, setPlan] = useState(null);

  useEffect(() => {
    (async () => {
      try {
        const response = await getWavePlanTopics();
        const items = response.data.topics || [];
        setTopics(items);
        const harmonization = items.find((t) => t.toLowerCase().includes('harmoniz'));
        setTopic(harmonization || items[0] || '');
      } catch (error) {
        toast.error(error.response?.data?.error || 'Unable to load Wave Input topics');
      } finally {
        setLoadingTopics(false);
      }
    })();
  }, []);

  // Function: runGenerate
  const runGenerate = async () => {
    if (!topic) return;
    setBusy(true);
    try {
      const response = await generateWavePlan({
        topic,
        complexity_scope: ['Low', 'Medium'],
        parallel_streams: Number(parallelStreams) || 3,
        program_start: programStart,
      });
      setPlan(response.data);
      toast.success(`Wave plan generated — ${response.data.wave_count} wave(s), ${response.data.app_count} application(s)`);
    } catch (error) {
      toast.error(error.response?.data?.error || 'Wave plan generation failed');
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="p-6 text-slate-100">
      <div className="mb-5">
        <p className="text-xs uppercase tracking-[0.2em] text-cyan-400">Capability Map</p>
        <h1 className="text-2xl font-bold mt-1">Wave Plan Creation</h1>
        <p className="text-sm text-slate-400 mt-1">
          AI-driven wave sequencing from the Wave Inputs table — 3-week sprints, cutover every 3 months,
          program spanning 3-24 months. Low and Medium complexity applications only; High complexity is
          deferred to a later stage.
        </p>
      </div>

      <div className="rounded-xl border border-slate-700 bg-slate-900/70 p-5 mb-5">
        {loadingTopics ? (
          <p className="text-sm text-slate-400 flex items-center gap-2"><Loader2 className="w-4 h-4 animate-spin" /> Loading topics…</p>
        ) : topics.length === 0 ? (
          <p className="text-sm text-slate-400">
            No Wave Inputs found. Upload the Wave_Plan_Input workbook on the{' '}
            <Link to="/app-rationalization/technical-assessment/wave-inputs" className="text-cyan-400 underline">Wave Inputs</Link> page first.
          </p>
        ) : (
          <div className="flex flex-wrap items-end gap-4">
            <div>
              <label className="block text-xs text-slate-400 mb-1">Topic</label>
              <select value={topic} onChange={(e) => setTopic(e.target.value)}
                className="rounded-lg bg-slate-950 border border-slate-700 px-3 py-2 text-sm min-w-[220px]">
                {topics.map((t) => <option key={t} value={t}>{t}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-xs text-slate-400 mb-1">Program Start</label>
              <input type="date" value={programStart} onChange={(e) => setProgramStart(e.target.value)}
                className="rounded-lg bg-slate-950 border border-slate-700 px-3 py-2 text-sm" />
            </div>
            <div>
              <label className="block text-xs text-slate-400 mb-1">Parallel Streams</label>
              <input type="number" min={1} max={10} value={parallelStreams}
                onChange={(e) => setParallelStreams(e.target.value)}
                className="rounded-lg bg-slate-950 border border-slate-700 px-3 py-2 text-sm w-24" />
            </div>
            <div className="flex items-center gap-2">
              <span className="text-[11px] px-2 py-1 rounded-full bg-emerald-500/15 text-emerald-300 border border-emerald-500/30">Low</span>
              <span className="text-[11px] px-2 py-1 rounded-full bg-amber-500/15 text-amber-300 border border-amber-500/30">Medium</span>
              <span className="text-[11px] px-2 py-1 rounded-full bg-slate-800 text-slate-500 border border-slate-700" title="Deferred to a later stage">High (deferred)</span>
            </div>
            <button disabled={busy || !topic} onClick={runGenerate}
              className="portal-btn-primary px-4 py-2 rounded-lg disabled:opacity-40 flex items-center gap-2">
              {busy ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
              {busy ? 'Generating…' : 'Generate Wave Plan'}
            </button>
          </div>
        )}
      </div>

      {plan && (
        <>
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 mb-5">
            <StatTile label="Waves" value={plan.wave_count} />
            <StatTile label="Applications Scheduled" value={plan.app_count} />
            <StatTile label="Deferred (High)" value={plan.deferred_high_complexity_count} accent="text-slate-400" />
            <StatTile label="Unscheduled" value={plan.unscheduled_count} accent={plan.unscheduled_count ? 'text-amber-400' : 'text-white'} />
            <StatTile label="Program Window" value={`${plan.program_start} → ${plan.program_end}`} />
            <StatTile label="Model" value={plan.llm_available ? modelDisplayName(plan.model_used) : 'Heuristic only'}
              accent={plan.llm_available ? 'text-cyan-300' : 'text-slate-400'} />
          </div>
          {plan.summary && (
            <div className="rounded-xl border border-slate-700 bg-slate-900/70 p-4 mb-5 text-sm text-slate-300">
              {plan.summary}
            </div>
          )}
          <WaveGanttChart plan={plan} />
        </>
      )}
    </div>
  );
};

export default WavePlanCreation;
