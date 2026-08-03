// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: AppRationalization — frontend/src/components (WavePlanning.jsx)
// Date: 2026-07-20
// ---------------------------------------------------------------------------
import React, { useMemo, useState } from 'react';
import { toast } from 'react-toastify';
import { Loader2, ChevronRight, Sparkles, X, Download } from 'lucide-react';
import { startWaveSchedulePrediction, getWaveScheduleJob, downloadWaveScheduleExport } from '../services/api';
import WaveScheduleGantt from './wave-plan/WaveScheduleGantt';
import WaveAppsDrilldown from './wave-plan/WaveAppsDrilldown';
import { formatDate } from './wave-plan/waveVisuals';
import { modelDisplayName } from '../utils/modelDisplay';

const TABS = [
  { key: 'gantt', label: 'Gantt Chart / Project Plan' },
  { key: 'plan', label: 'Wave Plan' },
  { key: 'summary', label: 'Wave Summary' },
  { key: 'tasks', label: 'Task List (WBS)' },
];

const PLAN_COLUMNS = [
  'Wave', 'Application Name', 'Assessment & Business Check Validation', 'Migration Type',
  'Migration Sprints', 'QA Sprints', 'UAT Sprints', 'Go-Live – Program Increment',
  'Stabilization', 'Decommissioning',
];

const SUMMARY_COLUMNS = [
  'Wave', 'Start', 'Cutover', 'Stabilisation Ends', 'Gate Review', 'Applications', 'Effort (hrs)',
  'Quick Wins', 'Topics', 'Simple', 'Medium', 'Complex', 'Very Complex', 'Permitted Complexity',
];

const TASK_COLUMNS = [
  'WBS', 'Task', 'Wave', 'Start', 'Finish', 'Duration (days)', 'Predecessor', 'Milestone', 'Applications', 'Effort (hrs)',
];

// Function: groupAppsByTopicFlat
const groupAppsByTopicFlat = (apps) => {
  const map = {};
  (apps || []).forEach((a) => {
    if (a.wave_number == null) return;
    const key = a.topic || 'Unspecified topic';
    (map[key] ||= []).push(a);
  });
  return Object.entries(map)
    .map(([topic, list]) => ({ topic, apps: list.sort((a, b) => (a.wave_number - b.wave_number) || a.app_id.localeCompare(b.app_id)) }))
    .sort((a, b) => b.apps.length - a.apps.length);
};

// Function: StatTile
const StatTile = ({ label, value }) => (
  <div className="wave-stat-card rounded-xl border border-slate-700 bg-slate-950/60 px-4 py-4">
    <p className="text-xs uppercase tracking-wider text-slate-500">{label}</p>
    <p className="text-2xl font-bold mt-1 text-white">{value}</p>
  </div>
);

// sessionStorage — not localStorage — so the predicted view survives
// navigating between pages but clears itself when the browser session ends,
// matching "persist the data till sessions are active".
const SESSION_KEY = 'wave_planning_schedule_v1';

// Function: loadPersistedSchedule
const loadPersistedSchedule = () => {
  try {
    const raw = sessionStorage.getItem(SESSION_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
};

// Function: PlanTopicGroup
const PlanTopicGroup = ({ group: g, expandedTopics, toggleTopic }) => {
  const key = `plan:${g.topic}`;
  const open = expandedTopics.has(key);
  return (
    <div className="border-b border-slate-800 last:border-b-0">
      <button type="button" onClick={() => toggleTopic(key)}
        className="w-full flex items-center justify-between gap-3 px-4 py-2.5 text-left hover:bg-slate-800/50">
        <span className="flex items-center gap-2 text-sm text-slate-200 min-w-0">
          <ChevronRight className={`w-3.5 h-3.5 shrink-0 text-cyan-400 transition-transform ${open ? 'rotate-90' : ''}`} />
          <span className="truncate font-medium">{g.topic}</span>
        </span>
        <span className="text-[11px] text-slate-500 whitespace-nowrap">{g.apps.length} application(s)</span>
      </button>
      {open && (
        <div className="overflow-x-auto">
          <table className="w-full text-xs">
            <thead className="bg-slate-800/60 text-slate-400">
              <tr>
                {PLAN_COLUMNS.map((h) => <th key={h} className="text-left pl-10 pr-3 py-2 font-medium whitespace-nowrap">{h}</th>)}
              </tr>
            </thead>
            <tbody>
              {g.apps.map((a) => (
                <tr key={a.app_id} className="border-t border-slate-800/80 hover:bg-slate-800/40">
                  <td className="pl-10 pr-3 py-2 whitespace-nowrap text-white font-medium">Wave {a.wave_number}</td>
                  <td className="pl-10 pr-3 py-2 whitespace-nowrap text-slate-300">{a.application_name || a.app_id}</td>
                  <td className="pl-10 pr-3 py-2 whitespace-nowrap text-slate-400">{a.assessment_sprint != null ? a.assessment_sprint : '—'}</td>
                  <td className="pl-10 pr-3 py-2 whitespace-nowrap text-slate-400">{a.migration_type || '—'}</td>
                  <td className="pl-10 pr-3 py-2 whitespace-nowrap text-slate-400">{a.migration_sprint_start != null ? `${a.migration_sprint_start}-${a.migration_sprint_end}` : '—'}</td>
                  <td className="pl-10 pr-3 py-2 whitespace-nowrap text-slate-400">{a.qa_uat_sprint ?? '—'}</td>
                  <td className="pl-10 pr-3 py-2 whitespace-nowrap text-slate-400">{a.qa_uat_sprint ?? '—'}</td>
                  <td className="pl-10 pr-3 py-2 whitespace-nowrap text-cyan-300">{a.go_live_pi || '—'}</td>
                  <td className="pl-10 pr-3 py-2 whitespace-nowrap text-slate-400">{a.stabilization_pi || '—'}</td>
                  <td className="pl-10 pr-3 py-2 whitespace-nowrap text-slate-400">{a.decommissioning_pi || '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

// Function: PlanTabContent
const PlanTabContent = ({ topicGroups, expandedTopics, toggleTopic }) => (
  <div className="rounded-xl border border-slate-700 bg-slate-900/70 overflow-hidden">
    <div className="p-3 border-b border-slate-700 text-xs text-slate-500">
      Topic-wise application delivery pipeline — click a topic (L2) to drill into its applications (L3).
      Program Increment (PI) = wave number; Decommissioning defaults to 1 wave after go-live.
    </div>
    <div className="overflow-auto max-h-[65vh]">
      {topicGroups.map((g) => (
        <PlanTopicGroup key={g.topic} group={g} expandedTopics={expandedTopics} toggleTopic={toggleTopic} />
      ))}
    </div>
  </div>
);

// Function: WaveRow
const WaveRow = ({ wave: w, open, onToggle, appsByWave, expandedTopics, toggleTopic }) => (
  <React.Fragment>
    <tr onClick={onToggle} className="border-t border-slate-800 hover:bg-slate-800/50 cursor-pointer select-none">
      <td className="px-3 py-2 font-semibold text-white whitespace-nowrap">
        <span className="flex items-center gap-1.5">
          <ChevronRight className={`w-3.5 h-3.5 text-cyan-400 transition-transform ${open ? 'rotate-90' : ''}`} />
          Wave {w.wave_number}
        </span>
      </td>
      <td className="px-3 py-2 whitespace-nowrap">{formatDate(w.start_date)}</td>
      <td className="px-3 py-2 whitespace-nowrap">{formatDate(w.cutover_date)}</td>
      <td className="px-3 py-2 whitespace-nowrap">{formatDate(w.stabilisation_end_date)}</td>
      <td className="px-3 py-2 whitespace-nowrap">{formatDate(w.gate_review_date)}</td>
      <td className="px-3 py-2 whitespace-nowrap">{w.application_count}</td>
      <td className="px-3 py-2 whitespace-nowrap">{Math.round(w.effort_hours).toLocaleString()}</td>
      <td className="px-3 py-2 whitespace-nowrap">{w.quick_win_count}</td>
      <td className="px-3 py-2 whitespace-nowrap">{w.topic_count}</td>
      <td className="px-3 py-2 whitespace-nowrap">{w.simple_count}</td>
      <td className="px-3 py-2 whitespace-nowrap">{w.medium_count}</td>
      <td className="px-3 py-2 whitespace-nowrap">{w.complex_count}</td>
      <td className="px-3 py-2 whitespace-nowrap">{w.very_complex_count}</td>
      <td className="px-3 py-2 whitespace-nowrap text-slate-400">{w.permitted_complexity}</td>
    </tr>
    {open && (
      <tr>
        <td colSpan={14} className="p-0">
          <WaveAppsDrilldown waveNumber={w.wave_number} apps={appsByWave[w.wave_number] || []}
            expandedTopics={expandedTopics} onToggleTopic={toggleTopic} />
        </td>
      </tr>
    )}
  </React.Fragment>
);

// Function: SummaryTabContent
const SummaryTabContent = ({ schedule, expandedWaves, toggleWave, appsByWave, expandedTopics, toggleTopic }) => (
  <div className="rounded-xl border border-slate-700 bg-slate-900/70 overflow-hidden">
    <div className="overflow-auto max-h-[65vh]">
      <table className="w-full text-xs">
        <thead className="sticky top-0 bg-slate-800 text-slate-300">
          <tr>
            {SUMMARY_COLUMNS.map((h) => (
              <th key={h} className="text-left px-3 py-2 whitespace-nowrap">{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {schedule.waves.map((w) => (
            <WaveRow key={w.wave_number} wave={w} open={expandedWaves.has(w.wave_number)}
              onToggle={() => toggleWave(w.wave_number)} appsByWave={appsByWave}
              expandedTopics={expandedTopics} toggleTopic={toggleTopic} />
          ))}
          <tr className="border-t border-slate-700 bg-slate-800/40 font-semibold text-white">
            <td className="px-3 py-2" colSpan={5}>TOTAL</td>
            <td className="px-3 py-2">{schedule.app_count}</td>
            <td className="px-3 py-2">{Math.round(schedule.total_effort_hours).toLocaleString()}</td>
            <td className="px-3 py-2" colSpan={7} />
          </tr>
        </tbody>
      </table>
    </div>
  </div>
);

// Function: TaskRow
const TaskRow = ({ task: t, open, onToggle, appsByWave, expandedTopics, toggleTopic }) => {
  if (t.task_type !== 'wave_header') {
    return (
      <tr className="border-t border-slate-800 hover:bg-slate-800/50">
        <td className="px-3 py-2 whitespace-nowrap">{t.wbs_code}</td>
        <td className="px-3 py-2 whitespace-nowrap" style={{ paddingLeft: 28 }}>{t.task_name}</td>
        <td className="px-3 py-2 whitespace-nowrap">{t.wave_number}</td>
        <td className="px-3 py-2 whitespace-nowrap">{formatDate(t.start_date)}</td>
        <td className="px-3 py-2 whitespace-nowrap">{formatDate(t.end_date)}</td>
        <td className="px-3 py-2 whitespace-nowrap">{t.duration_days}</td>
        <td className="px-3 py-2 whitespace-nowrap">{t.predecessor_wbs || '—'}</td>
        <td className="px-3 py-2 whitespace-nowrap">{t.is_milestone ? 'Yes' : ''}</td>
        <td className="px-3 py-2 whitespace-nowrap">{t.applications ?? ''}</td>
        <td className="px-3 py-2 whitespace-nowrap">{t.effort_hours != null ? Math.round(t.effort_hours).toLocaleString() : ''}</td>
      </tr>
    );
  }
  return (
    <React.Fragment>
      <tr onClick={onToggle}
        className="border-t border-slate-800 hover:bg-slate-800/50 bg-slate-800/30 font-semibold text-white cursor-pointer select-none">
        <td className="px-3 py-2 whitespace-nowrap">{t.wbs_code}</td>
        <td className="px-3 py-2 whitespace-nowrap" style={{ paddingLeft: 12 }}>
          <span className="flex items-center gap-1.5">
            <ChevronRight className={`w-3.5 h-3.5 text-cyan-400 transition-transform ${open ? 'rotate-90' : ''}`} />
            {t.task_name}
          </span>
        </td>
        <td className="px-3 py-2 whitespace-nowrap">{t.wave_number}</td>
        <td className="px-3 py-2 whitespace-nowrap">{formatDate(t.start_date)}</td>
        <td className="px-3 py-2 whitespace-nowrap">{formatDate(t.end_date)}</td>
        <td className="px-3 py-2 whitespace-nowrap">{t.duration_days}</td>
        <td className="px-3 py-2 whitespace-nowrap">{t.predecessor_wbs || '—'}</td>
        <td className="px-3 py-2 whitespace-nowrap">{t.is_milestone ? 'Yes' : ''}</td>
        <td className="px-3 py-2 whitespace-nowrap">{t.applications ?? ''}</td>
        <td className="px-3 py-2 whitespace-nowrap">{t.effort_hours != null ? Math.round(t.effort_hours).toLocaleString() : ''}</td>
      </tr>
      {open && (
        <tr>
          <td colSpan={10} className="p-0">
            <WaveAppsDrilldown waveNumber={t.wave_number} apps={appsByWave[t.wave_number] || []}
              expandedTopics={expandedTopics} onToggleTopic={toggleTopic} />
          </td>
        </tr>
      )}
    </React.Fragment>
  );
};

// Function: TasksTabContent
const TasksTabContent = ({ schedule, expandedWaves, toggleWave, appsByWave, expandedTopics, toggleTopic }) => (
  <div className="rounded-xl border border-slate-700 bg-slate-900/70 overflow-hidden">
    <div className="overflow-auto max-h-[65vh]">
      <table className="w-full text-xs">
        <thead className="sticky top-0 bg-slate-800 text-slate-300">
          <tr>
            {TASK_COLUMNS.map((h) => (
              <th key={h} className="text-left px-3 py-2 whitespace-nowrap">{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {schedule.tasks.map((t) => (
            <TaskRow key={t.wbs_code} task={t} open={expandedWaves.has(t.wave_number)}
              onToggle={() => toggleWave(t.wave_number)} appsByWave={appsByWave}
              expandedTopics={expandedTopics} toggleTopic={toggleTopic} />
          ))}
        </tbody>
      </table>
    </div>
  </div>
);

// Function: toggleSetMember
const toggleSetMember = (prevSet, value) => {
  const next = new Set(prevSet);
  if (next.has(value)) {
    next.delete(value);
  } else {
    next.add(value);
  }
  return next;
};

// Function: buildAppsByWave
const buildAppsByWave = (apps) => {
  const map = {};
  (apps || []).forEach((a) => {
    if (a.wave_number != null) (map[a.wave_number] ||= []).push(a);
  });
  return map;
};

// Function: sleep
const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

// Function: persistSchedule
const persistSchedule = (schedule) => {
  try { sessionStorage.setItem(SESSION_KEY, JSON.stringify(schedule)); } catch { /* storage full/unavailable — non-fatal */ }
};

// Function: pollWaveScheduleJob
// Polls until the job reaches a terminal status, reporting progress along the way.
// Function: pollWaveScheduleJob
const pollWaveScheduleJob = async (jobId, onProgress) => {
  // eslint-disable-next-line no-constant-condition
  while (true) {
    await sleep(3000);
    const jobResponse = await getWaveScheduleJob(jobId);
    const job = jobResponse.data;
    onProgress(job);
    if (job.status === 'done' || job.status === 'failed') {
      return job;
    }
  }
};

// Function: runWavePlanningPrediction
// Starts an async job (the batched Ollama review can take a while on this
// shared GPU) and polls it, rather than blocking on one long request.
// Function: runWavePlanningPrediction
const runWavePlanningPrediction = async ({ setHasStarted, setLoading, setProgress, setSchedule, setError }) => {
  setHasStarted(true);
  setLoading(true);
  setProgress(null);
  try {
    const startResponse = await startWaveSchedulePrediction();
    const jobId = startResponse.data.job_id;
    const job = await pollWaveScheduleJob(jobId, (j) => setProgress({
      batches_done: j.batches_done, batches_total: j.batches_total, batches_llm_ok: j.batches_llm_ok,
    }));

    if (job.status === 'done') {
      setSchedule(job.schedule);
      setError('');
      persistSchedule(job.schedule);
    } else {
      setSchedule(null);
      setError(job.error || 'Unable to calculate wave schedule');
      toast.error(job.error || 'Unable to calculate wave schedule');
    }
  } catch (err) {
    setSchedule(null);
    setError(err.response?.data?.error || 'Unable to calculate wave schedule');
    toast.error(err.response?.data?.error || 'Unable to calculate wave schedule');
  } finally {
    setLoading(false);
    setProgress(null);
  }
};

// Function: runExportSchedule
const runExportSchedule = async (scheduleId, setExporting) => {
  setExporting(true);
  try {
    await downloadWaveScheduleExport(scheduleId);
  } catch (err) {
    toast.error(err.response?.data?.error || 'Unable to export the wave schedule');
  } finally {
    setExporting(false);
  }
};

// Function: WavePlanningShell
const WavePlanningShell = ({ schedule, children }) => (
  <div className="wave-planning-ui min-h-full p-6 md:p-8 text-slate-100">
    <div className="mb-6 max-w-[1500px]">
      <p className="text-sm font-bold uppercase tracking-[0.18em] text-cyan-400">Technical Assessment</p>
      <h1 className="text-3xl font-bold mt-1">Wave Planning</h1>
      <p className="text-base text-slate-400 mt-2 leading-7">
        Harmonization wave delivery schedule — 3-week sprints, 13-week wave cadence, complexity ramp
        (Simple/Medium first, Complex from wave {schedule?.complex_from_wave ?? 3}, Very Complex from wave{' '}
        {schedule?.very_complex_from_wave ?? 6}). Every prediction is reviewed by OpenSource LLM on top of
        the rule-based scaffold, so re-predicting the same data can legitimately change the wave assignment.
      </p>
    </div>
    {children}
  </div>
);

// Function: StartPrompt
const StartPrompt = ({ onPredict, loading }) => (
  <div className="rounded-xl border border-slate-700 bg-slate-900/70 p-10 text-center">
    <p className="text-slate-400 mb-4">
      Upload the Business Validations and Wave Inputs workbooks first, then predict the wave delivery schedule.
    </p>
    <button onClick={onPredict} disabled={loading}
      className="portal-btn-primary inline-flex items-center gap-2 px-5 py-2.5 rounded-lg disabled:opacity-40">
      {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
      Predict Wave Planning
    </button>
  </div>
);

// Function: LoadingState
const LoadingState = ({ progress }) => (
  <p className="text-sm text-slate-400 flex items-center gap-2">
    <Loader2 className="w-4 h-4 animate-spin" />
    {progress && progress.batches_total
      ? `Reviewing with OpenSource LLM — batch ${progress.batches_done}/${progress.batches_total} (${progress.batches_llm_ok} succeeded)…`
      : 'Calculating rule-based scaffold…'}
  </p>
);

// Function: EmptyScheduleState
const EmptyScheduleState = ({ error, onRetry }) => (
  <div className="rounded-xl border border-slate-700 bg-slate-900/70 p-10 text-center text-slate-400">
    <p className="mb-4">{error || 'No Wave Inputs found. Upload the Wave_Plan_Input workbook on the Wave Inputs page first.'}</p>
    <button onClick={onRetry} className="portal-btn-secondary inline-flex items-center gap-2 px-4 py-2 rounded-lg text-sm">
      <Sparkles className="w-4 h-4" /> Retry
    </button>
  </div>
);

// Function: ScheduleToolbar
const ScheduleToolbar = ({ schedule, loading, exporting, onExport, onPredict, onClear }) => (
  <div className="flex justify-end gap-2 mb-3">
    {schedule.id && (
      <button onClick={onExport} disabled={exporting || loading}
        className="portal-btn-primary inline-flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs disabled:opacity-40">
        {exporting ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Download className="w-3.5 h-3.5" />}
        Download Excel Report
      </button>
    )}
    <button onClick={onPredict} disabled={loading}
      className="portal-btn-secondary inline-flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs disabled:opacity-40">
      {loading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Sparkles className="w-3.5 h-3.5" />}
      Re-predict
    </button>
    <button onClick={onClear} disabled={loading}
      className="portal-btn-secondary inline-flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs disabled:opacity-40">
      <X className="w-3.5 h-3.5" /> Clear
    </button>
  </div>
);

// Function: ScheduleStats
const ScheduleStats = ({ schedule }) => (
  <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 mb-5">
    <StatTile label="Waves" value={schedule.wave_count} />
    <StatTile label="Applications Scheduled" value={schedule.app_count} />
    <StatTile label="Deferred" value={schedule.deferred_count} />
    <StatTile label="Total Effort (hrs)" value={Math.round(schedule.total_effort_hours).toLocaleString()} />
    <StatTile label="Programme Start" value={formatDate(schedule.program_start)} />
    <StatTile label="Programme End" value={formatDate(schedule.program_end)} />
  </div>
);

// Function: LlmBanner
const LlmBanner = ({ schedule }) => (
  <div className={`wave-ai-banner rounded-xl border px-5 py-4 mb-6 flex items-start gap-3 text-sm leading-6 ${
    schedule.llm_available ? 'border-cyan-800 bg-cyan-950/30 text-cyan-200' : 'border-amber-800 bg-amber-950/30 text-amber-200'
  }`}>
    <Sparkles className="w-5 h-5 mt-0.5 shrink-0" />
    {schedule.llm_available
      ? <span>AI-reviewed by <strong>{modelDisplayName(schedule.model_used)}</strong>{schedule.summary ? ` — ${schedule.summary}` : ''}</span>
      : <span>Ollama was unavailable for this prediction — showing the rule-based scaffold only. Re-predict once Ollama is reachable.</span>}
  </div>
);

// Function: TabNav
const TabNav = ({ tab, setTab }) => (
  <div className="wave-tabs flex gap-1 mb-5 border-b border-slate-800 overflow-x-auto">
    {TABS.map((t) => (
      <button key={t.key} onClick={() => setTab(t.key)}
        className={`px-5 py-3 text-[15px] font-semibold border-b-[3px] -mb-px transition-colors whitespace-nowrap ${
          tab === t.key ? 'border-cyan-400 text-white' : 'border-transparent text-slate-400 hover:text-slate-200'
        }`}>
        {t.label}
      </button>
    ))}
  </div>
);

// Function: WavePlanning
const WavePlanning = () => {
  const [schedule, setSchedule] = useState(() => loadPersistedSchedule());
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(null); // { batches_done, batches_total, batches_llm_ok }
  const [hasStarted, setHasStarted] = useState(() => loadPersistedSchedule() !== null);
  const [exporting, setExporting] = useState(false);
  const [tab, setTab] = useState('gantt');
  const [expandedWaves, setExpandedWaves] = useState(new Set());
  const [expandedTopics, setExpandedTopics] = useState(new Set());

  // Function: toggleWave
  const toggleWave = (waveNumber) => setExpandedWaves((prev) => toggleSetMember(prev, waveNumber));
  // Function: toggleTopic
  const toggleTopic = (key) => setExpandedTopics((prev) => toggleSetMember(prev, key));

  const appsByWave = useMemo(() => buildAppsByWave(schedule?.apps), [schedule]);
  const topicGroups = useMemo(() => groupAppsByTopicFlat(schedule?.apps), [schedule]);

  // Function: predictWavePlanning
  const predictWavePlanning = () => runWavePlanningPrediction({
    setHasStarted, setLoading, setProgress, setSchedule, setError,
  });

  // Function: exportSchedule
  const exportSchedule = () => {
    if (!schedule?.id) return;
    runExportSchedule(schedule.id, setExporting);
  };

  // Function: clearPrediction
  const clearPrediction = () => {
    sessionStorage.removeItem(SESSION_KEY);
    setSchedule(null);
    setError('');
    setHasStarted(false);
    setExpandedWaves(new Set());
    setExpandedTopics(new Set());
    setTab('gantt');
  };

  if (!hasStarted) {
    return (
      <WavePlanningShell schedule={schedule}>
        <StartPrompt onPredict={predictWavePlanning} loading={loading} />
      </WavePlanningShell>
    );
  }

  if (loading) {
    return (
      <WavePlanningShell schedule={schedule}>
        <LoadingState progress={progress} />
      </WavePlanningShell>
    );
  }

  if (!schedule) {
    return (
      <WavePlanningShell schedule={schedule}>
        <EmptyScheduleState error={error} onRetry={predictWavePlanning} />
      </WavePlanningShell>
    );
  }

  return (
    <WavePlanningShell schedule={schedule}>
      <ScheduleToolbar schedule={schedule} loading={loading} exporting={exporting}
        onExport={exportSchedule} onPredict={predictWavePlanning} onClear={clearPrediction} />
      <ScheduleStats schedule={schedule} />
      <LlmBanner schedule={schedule} />
      <TabNav tab={tab} setTab={setTab} />

      {tab === 'gantt' && <WaveScheduleGantt schedule={schedule} />}

      {tab === 'plan' && (
        <PlanTabContent topicGroups={topicGroups} expandedTopics={expandedTopics} toggleTopic={toggleTopic} />
      )}

      {tab === 'summary' && (
        <SummaryTabContent schedule={schedule} expandedWaves={expandedWaves} toggleWave={toggleWave}
          appsByWave={appsByWave} expandedTopics={expandedTopics} toggleTopic={toggleTopic} />
      )}

      {tab === 'tasks' && (
        <TasksTabContent schedule={schedule} expandedWaves={expandedWaves} toggleWave={toggleWave}
          appsByWave={appsByWave} expandedTopics={expandedTopics} toggleTopic={toggleTopic} />
      )}
    </WavePlanningShell>
  );
};

export default WavePlanning;
