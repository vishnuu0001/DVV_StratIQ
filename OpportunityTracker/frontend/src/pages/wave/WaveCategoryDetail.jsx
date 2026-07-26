// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: OpportunityTracker — frontend/src/pages/wave (WaveCategoryDetail.jsx)
// Date: 2025-11-11
// ---------------------------------------------------------------------------
import React, { useEffect, useState } from 'react';
import {
  ArrowLeft, Download, Layers, AlertTriangle, Calendar, FileText, ChevronDown, ChevronRight,
} from 'lucide-react';
import toast from 'react-hot-toast';
import {
  BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend,
} from 'recharts';
import {
  getWaveCategory, listWaves, listWaveApps, getWaveRemediation, getWaveGantt, downloadWaveExport,
} from '../../services/api';
import WaveTable from './WaveTable';
import WaveGanttChart from './WaveGanttChart';

const MIGRATION_COLORS = {
  'Functional Migration Only': '#22d3ee',
  'Full Consolidation': '#a78bfa',
  'Data Migration Only': '#fbbf24',
  'TBD (data gap)': '#64748b',
};

const DISPOSITION_COLORS = {
  Harmonization: '#22d3ee',
  Modernization: '#fb923c',
};

// Function: StatCard
function StatCard({ label, value, color }) {
  return (
    <div className="ot-card px-4 py-3">
      <p className="text-[10px] uppercase tracking-wider text-slate-500">{label}</p>
      <p className={`text-xl font-bold mt-0.5 ${color || 'text-white'}`}>{value}</p>
    </div>
  );
}

// Function: WaveCategoryDetail
export default function WaveCategoryDetail({ jobId, category, onBack }) {
  const [summary, setSummary] = useState(null);
  const [waves, setWaves] = useState([]);
  const [view, setView] = useState('waves'); // waves | timeline | remediation | logic
  const [expandedWave, setExpandedWave] = useState(null);
  const [waveApps, setWaveApps] = useState({});
  const [remediation, setRemediation] = useState(null);
  const [gantt, setGantt] = useState([]);
  const [downloading, setDownloading] = useState(false);

  useEffect(() => {
    getWaveCategory(jobId, category).then(({ data }) => setSummary(data));
    listWaves(jobId, category).then(({ data }) => setWaves(data));
  }, [jobId, category]);

  // Function: toggleWave
  const toggleWave = async (wave) => {
    if (expandedWave === wave) {
      setExpandedWave(null);
      return;
    }
    setExpandedWave(wave);
    if (!waveApps[wave]) {
      const { data } = await listWaveApps(jobId, category, wave);
      setWaveApps((prev) => ({ ...prev, [wave]: data }));
    }
  };

  // Function: loadRemediation
  const loadRemediation = async () => {
    setView('remediation');
    if (!remediation) {
      const { data } = await getWaveRemediation(jobId, category);
      setRemediation(data);
    }
  };

  // Function: loadGantt
  const loadGantt = async () => {
    setView('timeline');
    if (!gantt.length) {
      const { data } = await getWaveGantt(jobId, category);
      setGantt(data);
    }
  };

  // Function: handleDownload
  const handleDownload = async () => {
    setDownloading(true);
    try {
      await downloadWaveExport(jobId, category);
    } catch {
      toast.error('Download failed.');
    } finally {
      setDownloading(false);
    }
  };

  if (!summary) return <p className="text-sm text-slate-500">Loading category…</p>;

  const migrationMix = [
    { name: 'Functional Migration Only', value: summary.functional_migration_only },
    { name: 'Full Consolidation', value: summary.full_consolidation },
    { name: 'Data Migration Only', value: summary.data_migration_only },
    { name: 'TBD (data gap)', value: summary.tbd_count },
  ].filter((d) => d.value > 0);

  const dispositionMix = [
    { name: 'Harmonization', value: summary.harmonization_count },
    { name: 'Modernization', value: summary.modernization_count },
  ].filter((d) => d.value > 0);

  const waveDistribution = waves.map((w) => ({
    wave: w.wave,
    'Functional Migr. Only': w.functional_migration_only,
    'Full Consolidation': w.full_consolidation,
    'Data Migration Only': w.data_migration_only,
    'TBD': w.tbd_count,
  }));

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between gap-3">
        <button type="button" onClick={onBack} className="ot-btn-secondary text-xs px-3 py-1.5">
          <ArrowLeft size={13} /> All categories
        </button>
        <button type="button" onClick={handleDownload} disabled={downloading} className="ot-btn-primary text-xs px-3 py-1.5">
          <Download size={13} /> {downloading ? 'Preparing…' : 'Download Wave Plan (.xlsx)'}
        </button>
      </div>

      <div>
        <p className="text-lg font-bold text-white">{category}</p>
        <p className="text-sm text-slate-400 mt-1">{summary.description}</p>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-9 gap-3">
        <StatCard label="Total Apps" value={summary.actual_app_count} />
        <StatCard label="Waves" value={summary.wave_count} color="text-violet-400" />
        <StatCard label="Harmonization" value={summary.harmonization_count} color="text-cyan-400" />
        <StatCard label="Modernization" value={summary.modernization_count} color={summary.modernization_count ? 'text-orange-400' : 'text-slate-500'} />
        <StatCard label="Data Quality Issues" value={summary.data_quality_issues} color={summary.data_quality_issues ? 'text-amber-400' : 'text-emerald-400'} />
        <StatCard label="Func. Migration Only" value={summary.functional_migration_only} color="text-cyan-400" />
        <StatCard label="Full Consolidation" value={summary.full_consolidation} color="text-violet-400" />
        <StatCard label="TBD (Data Gap)" value={summary.tbd_count} color="text-slate-400" />
        <StatCard label="Timeline" value={`${summary.timeline_start || '—'} → ${summary.timeline_end || '—'}`} />
      </div>

      {waves.length > 0 && (
        <div className="grid lg:grid-cols-3 gap-4">
          <div className="ot-card p-4">
            <p className="text-xs font-semibold text-slate-300 mb-3">App count per wave, by migration type</p>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={waveDistribution}>
                <XAxis dataKey="wave" tick={{ fontSize: 10, fill: '#94a3b8' }} />
                <YAxis tick={{ fontSize: 10, fill: '#94a3b8' }} allowDecimals={false} />
                <Tooltip contentStyle={{ background: '#0f172a', border: '1px solid #334155', fontSize: 12 }} />
                <Legend wrapperStyle={{ fontSize: 11 }} />
                <Bar dataKey="Functional Migr. Only" stackId="a" fill={MIGRATION_COLORS['Functional Migration Only']} />
                <Bar dataKey="Full Consolidation" stackId="a" fill={MIGRATION_COLORS['Full Consolidation']} />
                <Bar dataKey="Data Migration Only" stackId="a" fill={MIGRATION_COLORS['Data Migration Only']} />
                <Bar dataKey="TBD" stackId="a" fill={MIGRATION_COLORS['TBD (data gap)']} />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="ot-card p-4">
            <p className="text-xs font-semibold text-slate-300 mb-3">Migration type mix (category-wide)</p>
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie data={migrationMix} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80} label={(d) => d.value}>
                  {migrationMix.map((entry) => (
                    <Cell key={entry.name} fill={MIGRATION_COLORS[entry.name]} />
                  ))}
                </Pie>
                <Legend wrapperStyle={{ fontSize: 11 }} />
                <Tooltip contentStyle={{ background: '#0f172a', border: '1px solid #334155', fontSize: 12 }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="ot-card p-4">
            <p className="text-xs font-semibold text-slate-300 mb-3">Disposition mix (Harmonization vs Modernization)</p>
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie data={dispositionMix} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80} label={(d) => d.value}>
                  {dispositionMix.map((entry) => (
                    <Cell key={entry.name} fill={DISPOSITION_COLORS[entry.name]} />
                  ))}
                </Pie>
                <Legend wrapperStyle={{ fontSize: 11 }} />
                <Tooltip contentStyle={{ background: '#0f172a', border: '1px solid #334155', fontSize: 12 }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      <div className="flex items-center gap-1 border-b border-slate-800">
        {[
          { id: 'waves', label: 'Wave Assignment', icon: Layers },
          { id: 'timeline', label: 'Timeline', icon: Calendar, onClick: loadGantt },
          { id: 'remediation', label: 'Data Remediation', icon: AlertTriangle, onClick: loadRemediation },
          { id: 'logic', label: 'Classification Logic', icon: FileText },
        ].map(({ id, label, icon: Icon, onClick }) => (
          <button
            key={id}
            onClick={() => (onClick ? onClick() : setView(id))}
            className={`flex items-center gap-2 px-4 py-2.5 text-xs font-semibold border-b-2 transition-colors ${
              view === id ? 'border-cyan-500 text-cyan-400' : 'border-transparent text-slate-500 hover:text-slate-300'
            }`}
          >
            <Icon size={13} /> {label}
          </button>
        ))}
      </div>

      {view === 'waves' && (
        <div className="space-y-3">
          {waves.map((w) => (
            <div key={w.wave} className="ot-card overflow-hidden">
              <button
                type="button"
                onClick={() => toggleWave(w.wave)}
                className="w-full flex items-center justify-between px-5 py-3.5 text-left"
              >
                <div className="flex items-center gap-3">
                  {expandedWave === w.wave ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
                  <div>
                    <p className="text-sm font-semibold text-white">{w.wave}</p>
                    <p className="text-xs text-slate-500">{w.primary_departments}</p>
                  </div>
                </div>
                <div className="flex items-center gap-4 text-xs text-slate-400">
                  <span>{w.app_count} apps</span>
                  {w.data_quality_flags > 0 && (
                    <span className="text-amber-400 flex items-center gap-1"><AlertTriangle size={11} /> {w.data_quality_flags}</span>
                  )}
                  <span className="font-mono text-slate-500">{w.stream2_assessment}</span>
                </div>
              </button>
              {expandedWave === w.wave && (
                <div className="border-t border-slate-800 p-4 space-y-3">
                  {w.sequencing_rationale && (
                    <p className="text-xs text-slate-400 italic">{w.sequencing_rationale}</p>
                  )}
                  {waveApps[w.wave] ? <WaveTable apps={waveApps[w.wave]} /> : <p className="text-xs text-slate-500">Loading…</p>}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {view === 'timeline' && <WaveGanttChart rows={gantt} />}

      {view === 'remediation' && remediation && (
        <div className="space-y-4">
          <div className="ot-card p-4 text-xs text-slate-300 whitespace-pre-line leading-relaxed">
            {remediation.process_notes}
          </div>
          <WaveTable apps={remediation.apps} />
        </div>
      )}

      {view === 'logic' && (
        <div className="ot-card p-5 text-sm text-slate-300 leading-relaxed whitespace-pre-line">
          {summary.classification_logic_notes || 'No narrative available for this category.'}
        </div>
      )}
    </div>
  );
}
