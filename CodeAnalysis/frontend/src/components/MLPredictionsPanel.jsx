// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: * MLPredictionsPanel.jsx
// Date: 2026-02-22
// ---------------------------------------------------------------------------
/**
 * MLPredictionsPanel.jsx
 * ----------------------
 * Displays ML-generated predictions:
 *   • Migration Complexity Score (gauge 0-100)
 *   • Technology Fingerprint (confidence bars)
 *   • Top Risk Files (defect probability table)
 *   • Effort Estimation summary
 *   • Statistical Anomalies (outlier files)
 *
 * Data source: result.ml_predictions (from AnalysisResult.ml_predictions)
 */
import { useMemo } from 'react'
import {
  BarChart, Bar, Cell, XAxis, YAxis, Tooltip, ResponsiveContainer,
  RadialBarChart, RadialBar, PolarAngleAxis,
} from 'recharts'

// ── Colour helpers ────────────────────────────────────────────────────────────
// Function: riskBadge
const riskBadge = (level) => {
  const map = {
    critical: 'bg-red-500/20 text-red-300 border-red-400/40',
    high:     'bg-amber-500/20 text-amber-300 border-amber-400/40',
    medium:   'bg-yellow-500/15 text-yellow-300 border-yellow-400/30',
    low:      'bg-emerald-500/15 text-emerald-300 border-emerald-400/30',
  }
  return map[level] ?? map.medium
}

// Function: gaugeColor
const gaugeColor = (score) => {
  if (score >= 75) return '#ef4444'
  if (score >= 50) return '#f59e0b'
  if (score >= 25) return '#eab308'
  return '#10b981'
}

// ── Empty state ───────────────────────────────────────────────────────────────
// Function: EmptyState
function EmptyState({ message }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-slate-500 gap-3">
      <span className="text-4xl opacity-30">🤖</span>
      <p className="text-sm">{message ?? 'Insufficient data for ML predictions.'}</p>
      <p className="text-xs opacity-70">Re-run analysis on a codebase with more files to generate predictions.</p>
    </div>
  )
}

// ── Main component ─────────────────────────────────────────────────────────────
// Function: MLPredictionsPanel
export default function MLPredictionsPanel({ result }) {
  const ml = result?.ml_predictions

  if (!ml) return <EmptyState message="No ML predictions available for this analysis." />

  const {
    migration_score,
    tech_fingerprint,
    defect_predictions = [],
    effort_estimates,
    anomalies = [],
    summary,
  } = ml

  return (
    <div className="space-y-6">

      {/* Summary headline */}
      {summary && (
        <div className="rounded-xl border border-cyan-500/30 bg-cyan-500/8 p-4 text-sm text-cyan-100">
          <strong className="text-cyan-300">ML Summary: </strong>{summary}
        </div>
      )}

      {/* Top row: Migration gauge + Effort summary */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <MigrationGauge migrationScore={migration_score} />
        <EffortSummary effort={effort_estimates} />
      </div>

      {/* Tech Fingerprint */}
      {tech_fingerprint && Object.keys(tech_fingerprint).length > 0 && (
        <TechFingerprintChart fingerprint={tech_fingerprint} />
      )}

      {/* Top Risk Files */}
      {defect_predictions.length > 0 && (
        <TopRiskFiles predictions={defect_predictions} />
      )}

      {/* Anomalies */}
      {anomalies.length > 0 && (
        <AnomalyList anomalies={anomalies} />
      )}
    </div>
  )
}

// ── Migration Complexity Gauge ────────────────────────────────────────────────
// Function: MigrationGauge
function MigrationGauge({ migrationScore }) {
  if (!migrationScore) {
    return (
      <div className="rounded-xl border border-slate-700/50 bg-slate-800/30 p-4">
        <h3 className="text-sm font-semibold text-slate-300 mb-2">Migration Complexity</h3>
        <EmptyState message="No migration score computed." />
      </div>
    )
  }

  const score = migrationScore.overall ?? 0
  const category = migrationScore.category ?? 'unknown'
  const color = gaugeColor(score)

  const gaugeData = [{ name: 'score', value: score, fill: color }]

  return (
    <div className="rounded-xl border border-slate-700/50 bg-slate-800/30 p-4 space-y-3">
      <h3 className="text-sm font-semibold text-slate-300">Migration Complexity Score</h3>

      <div className="flex items-center gap-4">
        <div style={{ width: 120, height: 120 }}>
          <ResponsiveContainer width="100%" height="100%">
            <RadialBarChart
              cx="50%" cy="50%"
              innerRadius="60%" outerRadius="100%"
              startAngle={225} endAngle={-45}
              data={gaugeData}
            >
              <PolarAngleAxis type="number" domain={[0, 100]} angleAxisId={0} tick={false} />
              <RadialBar dataKey="value" cornerRadius={6} background={{ fill: '#1e293b' }} />
            </RadialBarChart>
          </ResponsiveContainer>
        </div>

        <div className="space-y-1">
          <p className="text-3xl font-bold" style={{ color }}>{score}</p>
          <p className="text-xs text-slate-400 uppercase tracking-wide">{category}</p>
          {Object.keys(migrationScore.legacy_signals ?? {}).slice(0, 4).map((s, i) => (
            <p key={i} className="text-[11px] text-slate-400">• {s.replace(/_/g, ' ')}</p>
          ))}
        </div>
      </div>

      {/* By-language breakdown */}
      {migrationScore.by_language && Object.keys(migrationScore.by_language).length > 0 && (
        <div>
          <p className="text-[11px] text-slate-500 mb-1">Per Language</p>
          <div className="flex flex-wrap gap-1">
            {Object.entries(migrationScore.by_language).map(([lang, val]) => (
              <span
                key={lang}
                className="text-[10px] px-1.5 py-0.5 rounded border border-slate-600/40 bg-slate-700/40 text-slate-300"
              >
                {lang}: {val}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

// ── Effort Summary ────────────────────────────────────────────────────────────
// Function: EffortSummary
function EffortSummary({ effort }) {
  if (!effort) return (
    <div className="rounded-xl border border-slate-700/50 bg-slate-800/30 p-4">
      <h3 className="text-sm font-semibold text-slate-300 mb-2">Effort Estimation</h3>
      <EmptyState message="No effort data." />
    </div>
  )

  return (
    <div className="rounded-xl border border-slate-700/50 bg-slate-800/30 p-4 space-y-3">
      <h3 className="text-sm font-semibold text-slate-300">Effort Estimation (COCOMO II)</h3>

      <div className="grid grid-cols-2 gap-2">
        <div className="rounded-lg border border-emerald-500/30 bg-emerald-500/8 p-2 text-center">
          <p className="text-lg font-bold text-emerald-300">{effort.quick_wins ?? 0}</p>
          <p className="text-[10px] text-emerald-400">Quick Wins</p>
          <p className="text-[9px] text-slate-500">(&lt;2 person-days)</p>
        </div>
        <div className="rounded-lg border border-yellow-500/30 bg-yellow-500/8 p-2 text-center">
          <p className="text-lg font-bold text-yellow-300">{effort.medium ?? 0}</p>
          <p className="text-[10px] text-yellow-400">Medium Tasks</p>
          <p className="text-[9px] text-slate-500">(2-10 days)</p>
        </div>
        <div className="rounded-lg border border-red-500/30 bg-red-500/8 p-2 text-center">
          <p className="text-lg font-bold text-red-300">{effort.complex ?? 0}</p>
          <p className="text-[10px] text-red-400">Complex Tasks</p>
          <p className="text-[9px] text-slate-500">(&gt;10 days)</p>
        </div>
        <div className="rounded-lg border border-cyan-500/30 bg-cyan-500/8 p-2 text-center">
          <p className="text-lg font-bold text-cyan-300">
            {effort.total_person_months != null
              ? effort.total_person_months.toFixed(1)
              : (effort.total_person_days != null
                  ? (effort.total_person_days / 22).toFixed(1)
                  : '—')}
          </p>
          <p className="text-[10px] text-cyan-400">Person-Months</p>
          <p className="text-[9px] text-slate-500">(total est.)</p>
        </div>
      </div>
    </div>
  )
}

// ── Technology Fingerprint ────────────────────────────────────────────────────
// Function: TechFingerprintChart
function TechFingerprintChart({ fingerprint }) {
  const data = useMemo(() => {
    return Object.entries(fingerprint)
      .filter(([, v]) => typeof v === 'object' && v !== null && v.detected)
      .sort((a, b) => (b[1].confidence ?? 0) - (a[1].confidence ?? 0))
      .slice(0, 12)
      .map(([tech, v]) => ({
        tech,
        confidence: Math.round((v.confidence ?? 0) * 100),
        evidence: v.evidence ?? 0,
      }))
  }, [fingerprint])

  if (data.length === 0) return null

  return (
    <div className="rounded-xl border border-slate-700/50 bg-slate-800/30 p-4 space-y-3">
      <h3 className="text-sm font-semibold text-slate-300">Technology Fingerprint</h3>
      <ResponsiveContainer width="100%" height={data.length * 28 + 20}>
        <BarChart data={data} layout="vertical" margin={{ left: 120, right: 20 }}>
          <XAxis type="number" domain={[0, 100]} tick={{ fill: '#94a3b8', fontSize: 10 }} />
          <YAxis dataKey="tech" type="category" width={115} tick={{ fill: '#cbd5e1', fontSize: 11 }} />
          <Tooltip
            formatter={(v) => [`${v}%`, 'Confidence']}
            contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: 8, fontSize: 11 }}
          />
          <Bar dataKey="confidence" radius={4}>
            {data.map((entry, i) => (
              <Cell key={i} fill={entry.confidence >= 80 ? '#ef4444' : entry.confidence >= 60 ? '#f59e0b' : '#3b82f6'} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

// ── Top Risk Files ────────────────────────────────────────────────────────────
// Function: TopRiskFiles
function TopRiskFiles({ predictions }) {
  const top = useMemo(() =>
    [...predictions]
      .sort((a, b) => (b.probability ?? 0) - (a.probability ?? 0))
      .slice(0, 20)
  , [predictions])

  return (
    <div className="rounded-xl border border-slate-700/50 bg-slate-800/30 p-4 space-y-3">
      <h3 className="text-sm font-semibold text-slate-300">
        Top Risk Files — Defect Probability ({top.length} shown)
      </h3>
      <div className="overflow-x-auto">
        <table className="w-full text-xs">
          <thead>
            <tr className="border-b border-slate-700/50 text-slate-400">
              <th className="text-left py-1.5 pr-3 font-medium">File</th>
              <th className="text-right pr-3 font-medium">Probability</th>
              <th className="text-center pr-3 font-medium">Risk</th>
              <th className="text-left font-medium">Top Factors</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60">
            {top.map((pred, i) => (
              <tr key={i} className="hover:bg-slate-700/20 transition-colors">
                <td className="py-1.5 pr-3 text-slate-300 font-mono truncate max-w-[220px]" title={pred.file}>
                  {pred.file?.split(/[\\/]/).pop() ?? pred.file}
                </td>
                <td className="py-1.5 pr-3 text-right font-semibold" style={{
                  color: pred.probability >= 0.7 ? '#ef4444' : pred.probability >= 0.4 ? '#f59e0b' : '#10b981'
                }}>
                  {((pred.probability ?? 0) * 100).toFixed(0)}%
                </td>
                <td className="py-1.5 pr-3 text-center">
                  <span className={`px-1.5 py-0.5 rounded-full border text-[9px] font-bold uppercase ${riskBadge(pred.risk_level)}`}>
                    {pred.risk_level ?? '—'}
                  </span>
                </td>
                <td className="py-1.5 text-slate-400 truncate max-w-[180px]">
                  {(pred.factors ?? []).slice(0, 2).join(', ')}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

// ── Anomaly List ──────────────────────────────────────────────────────────────
// Function: AnomalyList
function AnomalyList({ anomalies }) {
  return (
    <div className="rounded-xl border border-amber-500/30 bg-amber-500/5 p-4 space-y-3">
      <h3 className="text-sm font-semibold text-amber-300">
        Statistical Anomalies ({anomalies.length} detected)
      </h3>
      <div className="divide-y divide-amber-900/30 max-h-64 overflow-y-auto">
        {anomalies.map((a, i) => (
          <div key={i} className="flex items-start gap-3 py-2 text-xs">
            <span className="shrink-0 font-mono text-[10px] text-amber-400/70 mt-0.5 w-14">
              z={a.z_score?.toFixed(1) ?? '?'}
            </span>
            <span className="text-amber-200 font-mono truncate max-w-[200px]" title={a.file}>
              {a.file?.split(/[\\/]/).pop() ?? a.file}
            </span>
            <span className="text-amber-400/70 shrink-0">{a.metric}</span>
            <span className="ml-auto text-amber-300 shrink-0">{a.value?.toLocaleString()}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
