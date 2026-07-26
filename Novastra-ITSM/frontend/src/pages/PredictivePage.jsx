// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: Novastra-ITSM — frontend/src/pages (PredictivePage.jsx)
// Date: 2026-07-01
// ---------------------------------------------------------------------------
import React, { useState, useEffect } from 'react'
import { TrendingUp, Plus, Trash2 } from 'lucide-react'
import api from '../services/api.js'
import TicketPicker from '../components/TicketPicker.jsx'
import { useTicket } from '../context/TicketContext.jsx'

const TABS = ['Incident Prediction', 'SLA Breach Risk', 'Change Risk', 'Anomaly Detection', 'ML Anomaly (Isolation Forest)', 'Predictive Maintenance']

const PRIORITY_OPTS = ['P1', 'P2', 'P3', 'P4']
const CHANGE_TYPES = ['standard', 'normal', 'emergency', 'expedited']
const HORIZONS = [7, 14, 30, 60, 90]

// ServiceNow priority â†’ P-code + SLA hours mapping
const SN_PRIORITY_MAP = {
  '1 - Critical': ['P1', 4],
  '2 - High':     ['P2', 8],
  '3 - Medium':   ['P3', 24],
  '4 - Low':      ['P4', 72],
}

const riskColor = r => ({ CRITICAL: 'text-red-400 bg-red-500/10 border-red-500/30', HIGH: 'text-orange-400 bg-orange-500/10 border-orange-500/30', MEDIUM: 'text-yellow-400 bg-yellow-500/10 border-yellow-500/30', LOW: 'text-green-400 bg-green-500/10 border-green-500/30' }[r] || 'text-gray-400 bg-gray-500/10 border-gray-500/30')
const sevColor = s => ({ CRITICAL: 'text-red-400', HIGH: 'text-orange-400', MEDIUM: 'text-yellow-400', LOW: 'text-blue-400' }[s] || 'text-gray-400')

// Function: PredictivePage
export default function PredictivePage() {
  const { activeTicket } = useTicket()
  const [tab, setTab] = useState('Incident Prediction')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')

  // Incident prediction
  const [incJson, setIncJson] = useState('')
  const [horizon, setHorizon] = useState(30)

  // SLA
  const [slaTickets, setSlaTickets] = useState([{ id: '', priority: 'P3', created_at: '', sla_hours: 24, current_status: 'Open', age_hours: 0 }])

  // Change
  const [chgTitle, setChgTitle] = useState('')
  const [chgDesc, setChgDesc] = useState('')
  const [chgCIs, setChgCIs] = useState('')
  const [chgDate, setChgDate] = useState('')
  const [chgType, setChgType] = useState('standard')

  // Anomaly
  const [anomMode, setAnomMode] = useState('manual')
  const [anomJson, setAnomJson] = useState('')
  const [anomMetrics, setAnomMetrics] = useState([{ metric_name: '', value: '', baseline: '', timestamp: '' }])

  // â”€â”€ Wire active ticket â†’ SLA tab â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
  useEffect(() => {
    if (!activeTicket) return
    const [pCode, slaHrs] = SN_PRIORITY_MAP[activeTicket.priority] || ['P3', 24]
    setSlaTickets([{
      id: activeTicket.number || '',
      priority: pCode,
      created_at: activeTicket.opened_at || '',
      sla_hours: slaHrs,
      current_status: activeTicket.state || 'Open',
      age_hours: activeTicket.age_hours || 0,
    }])
    // Also seed incident prediction JSON with this ticket
    setIncJson(JSON.stringify([{
      date: (activeTicket.opened_at || '').slice(0, 10),
      category: activeTicket.category || '',
      ci: activeTicket.cmdb_ci || '',
      description: activeTicket.short_description || '',
    }], null, 2))
    // Change Risk: the incident itself is a reasonable starting point for a
    // remediation change — title/description/affected CI carry over directly.
    setChgTitle(activeTicket.short_description || '')
    setChgDesc(activeTicket.description || '')
    setChgCIs(activeTicket.cmdb_ci || '')
  }, [activeTicket])

  const inputCls = 'w-full bg-gray-800 border border-white/10 rounded-lg px-3 py-1.5 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-blue-500'
  const labelCls = 'block text-xs font-medium text-gray-400 mb-1'
  const selectCls = `${inputCls}`

  // Function: call
  const call = async (endpoint, payload) => {
    setLoading(true); setError(''); setResult(null)
    try {
      const { data } = await api.post(endpoint, payload, { timeout: 0 })
      setResult(data)
    } catch (e) {
      setError(e.response?.data?.detail || e.message || 'Request failed')
    } finally { setLoading(false) }
  }

  // Function: addSla
  const addSla = () => setSlaTickets(t => [...t, { id: '', priority: 'P3', created_at: '', sla_hours: 24, current_status: 'Open', age_hours: 0 }])
  const removeSla = i => setSlaTickets(t => t.filter((_, idx) => idx !== i))
  // Function: updateSla
  const updateSla = (i, k, v) => setSlaTickets(t => t.map((row, idx) => idx === i ? { ...row, [k]: v } : row))

  // Function: addAnomRow
  const addAnomRow = () => setAnomMetrics(m => [...m, { metric_name: '', value: '', baseline: '', timestamp: '' }])
  const removeAnomRow = i => setAnomMetrics(m => m.filter((_, idx) => idx !== i))
  // Function: updateAnomRow
  const updateAnomRow = (i, k, v) => setAnomMetrics(m => m.map((row, idx) => idx === i ? { ...row, [k]: v } : row))

  return (
    <div className="flex-1 overflow-y-auto bg-gray-950 p-6 space-y-4">
      <div className="flex items-center gap-3">
        <TrendingUp size={22} className="text-blue-400" />
        <div>
          <h1 className="text-sm font-semibold text-white">Predictive Analytics & AIOps</h1>
          <p className="text-xs text-gray-400">Incident prediction, SLA risk, change assessment, anomaly detection</p>
        </div>
      </div>

      <TicketPicker />

      <div className="flex flex-wrap gap-1 bg-gray-900 rounded-lg p-1 w-fit">
        {TABS.map(t => (
          <button key={t} onClick={() => { setTab(t); setResult(null); setError('') }}
            className={`px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${tab === t ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-white'}`}>
            {t}
          </button>
        ))}
      </div>

      {tab === 'Incident Prediction' && (
        <div className="bg-gray-900 rounded-xl border border-white/10 p-5 space-y-4">
          <div><label className={labelCls}>Historical Incidents JSON (array of {`{date, category, ci, description}`})</label><textarea className={inputCls} rows={6} value={incJson} onChange={e => setIncJson(e.target.value)} placeholder='[{"date": "2026-06-01", "category": "Network", "ci": "ROUTER-01", "description": "Link flap"}]' /></div>
          <div>
            <label className={labelCls}>Prediction Horizon: {horizon} days</label>
            <input type="range" min={7} max={90} step={1} value={horizon} onChange={e => setHorizon(Number(e.target.value))} className="w-full accent-blue-500" />
            <div className="flex justify-between text-xs text-gray-500 mt-1">{HORIZONS.map(h => <span key={h}>{h}d</span>)}</div>
          </div>
          <button onClick={() => { try { call('/predictive/incident-prediction', { historical_incidents: JSON.parse(incJson || '[]'), prediction_horizon_days: horizon }) } catch { setError('Invalid JSON') } }}
            disabled={loading} className="px-4 py-2 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white text-xs font-medium rounded-lg transition-colors">
            {loading ? 'Predicting...' : 'Predict Incidents'}
          </button>
          {result && (
            <div className="space-y-3">
              {result.risk_summary && <div className="bg-gray-800 rounded-lg p-3 text-sm text-gray-200">{result.risk_summary}</div>}
              {result.predictions?.map((p, i) => (
                <div key={i} className={`rounded-lg p-3 border ${riskColor(p.probability > 0.7 ? 'HIGH' : p.probability > 0.4 ? 'MEDIUM' : 'LOW')}`}>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm font-medium text-white">{p.category}</span>
                    <span className="text-xs text-gray-400">{Math.round(p.probability * 100)}% probability</span>
                  </div>
                  <p className="text-xs text-gray-400">CI: {p.ci} Â· {p.predicted_date_range}</p>
                  <p className="text-xs text-gray-300 mt-1">{p.preventive_action}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {tab === 'SLA Breach Risk' && (
        <div className="bg-gray-900 rounded-xl border border-white/10 p-5 space-y-4">
          <div className="flex items-center justify-between"><label className={labelCls}>Tickets</label><button onClick={addSla} className="text-xs text-blue-400 flex items-center gap-1"><Plus size={12} />Add</button></div>
          {slaTickets.map((t, i) => (
            <div key={i} className="grid grid-cols-6 gap-2 items-start">
              <input className={inputCls} value={t.id} onChange={e => updateSla(i, 'id', e.target.value)} placeholder="ID" />
              <select className={selectCls} value={t.priority} onChange={e => updateSla(i, 'priority', e.target.value)}>{PRIORITY_OPTS.map(p => <option key={p}>{p}</option>)}</select>
              <input className={inputCls} type="number" value={t.sla_hours} onChange={e => updateSla(i, 'sla_hours', Number(e.target.value))} placeholder="SLA hrs" />
              <input className={inputCls} type="number" value={t.age_hours} onChange={e => updateSla(i, 'age_hours', Number(e.target.value))} placeholder="Age hrs" />
              <input className={inputCls} value={t.current_status} onChange={e => updateSla(i, 'current_status', e.target.value)} placeholder="Status" />
              <button onClick={() => removeSla(i)} className="text-red-400 hover:text-red-300 mt-2"><Trash2 size={14} /></button>
            </div>
          ))}
          <button onClick={() => call('/predictive/sla-breach', { tickets: slaTickets })}
            disabled={loading} className="px-4 py-2 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white text-xs font-medium rounded-lg transition-colors">
            {loading ? 'Scoring...' : 'Score SLA Risk'}
          </button>
          {result && (
            <div className="space-y-3">
              <p className="text-sm text-gray-400">{result.at_risk_count} ticket(s) at high/critical risk</p>
              {result.scored_tickets?.map((t, i) => (
                <div key={i} className={`rounded-lg p-3 border ${riskColor(t.risk_level)}`}>
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-white">Ticket {t.id}</span>
                    <span className={`text-xs font-bold ${sevColor(t.risk_level)}`}>{t.risk_level}</span>
                  </div>
                  <p className="text-xs text-gray-400 mt-1">Breach probability: {Math.round(t.breach_probability * 100)}% Â· {t.hours_remaining}h remaining</p>
                  <p className="text-xs text-gray-300 mt-0.5">{t.recommended_action}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {tab === 'Change Risk' && (
        <div className="bg-gray-900 rounded-xl border border-white/10 p-5 space-y-4">
          <div><label className={labelCls}>Change Title</label><input className={inputCls} value={chgTitle} onChange={e => setChgTitle(e.target.value)} placeholder="e.g. SAP kernel upgrade â€” Production" /></div>
          <div><label className={labelCls}>Description</label><textarea className={inputCls} rows={3} value={chgDesc} onChange={e => setChgDesc(e.target.value)} placeholder="Describe what the change does..." /></div>
          <div className="grid grid-cols-2 gap-4">
            <div><label className={labelCls}>Affected CIs (comma-separated)</label><input className={inputCls} value={chgCIs} onChange={e => setChgCIs(e.target.value)} placeholder="SAP-PROD-01, DB-PROD-02" /></div>
            <div><label className={labelCls}>Planned Date/Time</label><input className={inputCls} type="datetime-local" value={chgDate} onChange={e => setChgDate(e.target.value)} /></div>
          </div>
          <div><label className={labelCls}>Change Type</label><select className={selectCls} value={chgType} onChange={e => setChgType(e.target.value)}>{CHANGE_TYPES.map(t => <option key={t}>{t}</option>)}</select></div>
          <button onClick={() => call('/predictive/change-risk', { change_title: chgTitle, change_description: chgDesc, affected_cis: chgCIs.split(',').map(c => c.trim()).filter(Boolean), planned_datetime: chgDate, change_type: chgType })}
            disabled={loading || !chgTitle} className="px-4 py-2 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white text-xs font-medium rounded-lg transition-colors">
            {loading ? 'Assessing...' : 'Assess Risk'}
          </button>
          {result && (
            <div className="mt-4 space-y-4">
              <div className="flex items-center gap-6">
                <div className={`text-4xl font-bold ${result.risk_level === 'CRITICAL' ? 'text-red-400' : result.risk_level === 'HIGH' ? 'text-orange-400' : result.risk_level === 'MEDIUM' ? 'text-yellow-400' : 'text-green-400'}`}>{result.risk_level}</div>
                <div><p className="text-xs text-gray-400">Risk Score</p><p className="text-2xl font-bold text-white">{Math.round((result.risk_score || 0) * 100)}%</p></div>
                <div><p className="text-xs text-gray-400">Recommendation</p><p className="text-sm font-semibold text-white">{result.approval_recommendation}</p></div>
              </div>
              {result.impact_summary && <div className="bg-gray-800 rounded-lg p-3"><p className="text-xs text-gray-400 mb-1">Impact</p><p className="text-sm text-gray-200">{result.impact_summary}</p></div>}
              {result.concerns?.length > 0 && <div className="bg-gray-800 rounded-lg p-3"><p className="text-xs text-gray-400 mb-2">Concerns</p><ul className="space-y-1">{result.concerns.map((c, i) => <li key={i} className="text-sm text-red-300 flex gap-2"><span>âš </span>{c}</li>)}</ul></div>}
              {result.recommendations?.length > 0 && <div className="bg-gray-800 rounded-lg p-3"><p className="text-xs text-gray-400 mb-2">Recommendations</p><ul className="space-y-1">{result.recommendations.map((r, i) => <li key={i} className="text-sm text-blue-300 flex gap-2"><span>â†’</span>{r}</li>)}</ul></div>}
            </div>
          )}
        </div>
      )}

      {tab === 'Anomaly Detection' && (
        <div className="bg-gray-900 rounded-xl border border-white/10 p-5 space-y-4">
          <div className="flex gap-2 mb-2">
            {['manual', 'json'].map(m => (
              <button key={m} onClick={() => setAnomMode(m)} className={`px-3 py-1 rounded text-xs font-medium transition-colors ${anomMode === m ? 'bg-gray-700 text-white' : 'text-gray-500 hover:text-gray-300'}`}>{m === 'manual' ? 'Manual Entry' : 'Paste JSON'}</button>
            ))}
          </div>
          {anomMode === 'json' ? (
            <div><label className={labelCls}>Metrics JSON (array of {`{timestamp, metric_name, value, baseline}`})</label><textarea className={inputCls} rows={8} value={anomJson} onChange={e => setAnomJson(e.target.value)} placeholder='[{"timestamp": "2026-06-18T10:00:00Z", "metric_name": "CPU%", "value": 95.0, "baseline": 45.0}]' /></div>
          ) : (
            <div className="space-y-2">
              <div className="flex items-center justify-between"><label className={labelCls}>Metrics</label><button onClick={addAnomRow} className="text-xs text-blue-400 flex items-center gap-1"><Plus size={12} />Add</button></div>
              {anomMetrics.map((m, i) => (
                <div key={i} className="grid grid-cols-5 gap-2 items-start">
                  <input className={inputCls} value={m.metric_name} onChange={e => updateAnomRow(i, 'metric_name', e.target.value)} placeholder="Metric name (e.g. CPU%)" />
                  <input className={inputCls} type="number" value={m.value} onChange={e => updateAnomRow(i, 'value', e.target.value)} placeholder="Value" />
                  <input className={inputCls} type="number" value={m.baseline} onChange={e => updateAnomRow(i, 'baseline', e.target.value)} placeholder="Baseline" />
                  <input className={inputCls} value={m.timestamp} onChange={e => updateAnomRow(i, 'timestamp', e.target.value)} placeholder="Timestamp" />
                  <button onClick={() => removeAnomRow(i)} className="text-red-400 hover:text-red-300 mt-2"><Trash2 size={14} /></button>
                </div>
              ))}
            </div>
          )}
          <button onClick={() => {
            let metrics
            if (anomMode === 'json') {
              try { metrics = JSON.parse(anomJson || '[]') } catch { setError('Invalid JSON'); return }
            } else {
              metrics = anomMetrics
                .filter(m => m.metric_name.trim() && m.value !== '')
                .map(m => ({
                  metric_name: m.metric_name,
                  value: Number(m.value),
                  baseline: m.baseline === '' ? undefined : Number(m.baseline),
                  timestamp: m.timestamp || undefined,
                }))
              if (metrics.length === 0) { setError('Add at least one metric with a name and value'); return }
            }
            call('/predictive/anomaly-detect', { metrics })
          }}
            disabled={loading} className="px-4 py-2 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white text-xs font-medium rounded-lg transition-colors">
            {loading ? 'Detecting...' : 'Detect Anomalies'}
          </button>
          {result && (
            <div className="space-y-3">
              {result.narrative && <div className="bg-gray-800 rounded-lg p-3 text-sm text-gray-200">{result.narrative}</div>}
              {result.anomalies?.length === 0 && <p className="text-sm text-green-400">No anomalies detected.</p>}
              {result.anomalies?.map((a, i) => (
                <div key={i} className={`rounded-lg p-3 border ${riskColor(a.severity)}`}>
                  <div className="flex items-center justify-between"><span className="text-sm font-medium text-white">{a.metric_name}</span><span className={`text-xs font-bold ${sevColor(a.severity)}`}>{a.severity}</span></div>
                  <p className="text-xs text-gray-400 mt-1">{a.timestamp}</p>
                  <p className="text-xs text-gray-300 mt-0.5">Value: {a.value} vs baseline {a.baseline} ({a.deviation_pct}% deviation)</p>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {tab === 'ML Anomaly (Isolation Forest)' && (
        <div className="bg-gray-900 rounded-xl border border-white/10 p-5 space-y-4">
          <p className="text-xs text-gray-400">Uses scikit-learn Isolation Forest for statistically rigorous anomaly detection on multi-dimensional metric data.</p>
          <div><label className={labelCls}>Data Points JSON (array of objects with numeric fields)</label>
            <textarea className={inputCls} rows={8} defaultValue={JSON.stringify([
              { timestamp: '2026-06-18T09:00:00', value: 45.2, response_ms: 120 },
              { timestamp: '2026-06-18T09:05:00', value: 46.1, response_ms: 125 },
              { timestamp: '2026-06-18T09:10:00', value: 92.7, response_ms: 4800 },
              { timestamp: '2026-06-18T09:15:00', value: 44.9, response_ms: 118 },
              { timestamp: '2026-06-18T09:20:00', value: 45.5, response_ms: 122 },
            ], null, 2)} id="ml-anomaly-input" />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div><label className={labelCls}>Feature Fields (comma-separated)</label><input className={inputCls} id="ml-feature-fields" defaultValue="value,response_ms" /></div>
            <div><label className={labelCls}>Contamination Rate (0.01-0.5)</label><input type="number" className={inputCls} id="ml-contamination" defaultValue={0.1} min={0.01} max={0.5} step={0.01} /></div>
          </div>
          <button onClick={() => {
            try {
              const dp = JSON.parse(document.getElementById('ml-anomaly-input').value || '[]')
              const ff = document.getElementById('ml-feature-fields').value.split(',').map(s => s.trim())
              const c = parseFloat(document.getElementById('ml-contamination').value || '0.1')
              call('/predictive/ml-anomaly', { data_points: dp, feature_fields: ff, contamination: c })
            } catch { setError('Invalid JSON for data points') }
          }} disabled={loading} className="px-4 py-2 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white text-xs font-medium rounded-lg transition-colors">
            {loading ? 'Running Isolation Forest...' : 'Run ML Anomaly Detection'}
          </button>
          {result && (
            <div className="space-y-3">
              <div className="flex gap-4 text-sm">
                <span className="text-gray-400">{result.total_points} data points</span>
                <span className="text-orange-400 font-medium">{result.anomalies_detected} anomalies</span>
                <span className="text-gray-500">Algorithm: {result.algorithm}</span>
              </div>
              {result.anomalies?.map((a, i) => (
                <div key={i} className={`rounded-lg p-3 border ${riskColor(a.severity)}`}>
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-white">Data Point #{a.index}</span>
                    <span className={`text-xs font-bold ${sevColor(a.severity)}`}>{a.severity}</span>
                  </div>
                  <p className="text-xs text-gray-400 mt-1">{a.timestamp}</p>
                  <p className="text-xs text-gray-300 mt-0.5">Score: {a.anomaly_score} | Features: {JSON.stringify(a.features)}</p>
                </div>
              ))}
              {result.anomalies_detected === 0 && <p className="text-sm text-green-400">No anomalies detected by Isolation Forest.</p>}
            </div>
          )}
        </div>
      )}

      {tab === 'Predictive Maintenance' && (
        <div className="bg-gray-900 rounded-xl border border-white/10 p-5 space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div><label className={labelCls}>Asset ID</label><input className={inputCls} id="pm-asset-id" defaultValue="SRV-PROD-01" /></div>
            <div><label className={labelCls}>Asset Type</label>
              <select className={selectCls} id="pm-asset-type">
                {['server', 'database', 'network_device', 'storage', 'application', 'vm'].map(t => <option key={t}>{t}</option>)}
              </select>
            </div>
            <div><label className={labelCls}>Age (days)</label><input type="number" className={inputCls} id="pm-age" defaultValue={730} /></div>
          </div>
          <div>
            <p className="text-xs font-medium text-gray-400 mb-2">Metrics</p>
            <div className="grid grid-cols-3 gap-2">
              {[['cpu_utilization_pct','CPU %','82'],['memory_utilization_pct','Memory %','71'],['disk_utilization_pct','Disk %','88'],['error_rate_per_hour','Errors/hr','3.5'],['uptime_pct_30d','Uptime 30d %','99.2']].map(([id, lbl, def]) => (
                <div key={id}><label className={labelCls}>{lbl}</label><input type="number" className={inputCls} id={`pm-${id}`} defaultValue={def} step="0.1" /></div>
              ))}
            </div>
          </div>
          <div><label className={labelCls}>Incident History JSON (optional)</label>
            <textarea className={inputCls} rows={4} id="pm-history" defaultValue={JSON.stringify([
              { date: '2026-05-10', type: 'hardware_fault', resolution_hours: 3 },
              { date: '2026-04-22', type: 'memory_error', resolution_hours: 1.5 },
            ], null, 2)} />
          </div>
          <button onClick={() => {
            try {
              const history = JSON.parse(document.getElementById('pm-history').value || '[]')
              call('/predictive/predictive-maintenance', {
                asset_id: document.getElementById('pm-asset-id').value,
                asset_type: document.getElementById('pm-asset-type').value,
                age_days: parseFloat(document.getElementById('pm-age').value || '0'),
                metrics: {
                  cpu_utilization_pct: parseFloat(document.getElementById('pm-cpu_utilization_pct').value || '0'),
                  memory_utilization_pct: parseFloat(document.getElementById('pm-memory_utilization_pct').value || '0'),
                  disk_utilization_pct: parseFloat(document.getElementById('pm-disk_utilization_pct').value || '0'),
                  error_rate_per_hour: parseFloat(document.getElementById('pm-error_rate_per_hour').value || '0'),
                  uptime_pct_30d: parseFloat(document.getElementById('pm-uptime_pct_30d').value || '100'),
                },
                incident_history: history,
              })
            } catch { setError('Invalid JSON for incident history') }
          }} disabled={loading} className="px-4 py-2 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white text-xs font-medium rounded-lg transition-colors">
            {loading ? 'Analyzing...' : 'Predict Maintenance Need'}
          </button>
          {result && (
            <div className="space-y-3">
              <div className="flex items-center gap-6">
                <div className={`text-4xl font-bold ${result.risk_level === 'CRITICAL' ? 'text-red-400' : result.risk_level === 'HIGH' ? 'text-orange-400' : result.risk_level === 'MEDIUM' ? 'text-yellow-400' : 'text-green-400'}`}>{result.risk_level}</div>
                <div><p className="text-xs text-gray-400">Failure Probability</p><p className="text-2xl font-bold text-white">{Math.round((result.failure_probability || 0) * 100)}%</p></div>
                <div><p className="text-xs text-gray-400">Predicted MTTR</p><p className="text-sm font-bold text-white">{result.predicted_mttr_hours}h</p></div>
              </div>
              {result.maintenance_window_recommendation && <div className="bg-gray-800 rounded-lg p-3"><p className="text-xs text-gray-400 mb-1">Recommendation</p><p className="text-sm text-gray-200">{result.maintenance_window_recommendation}</p></div>}
              {result.maintenance_actions?.length > 0 && <div className="bg-gray-800 rounded-lg p-3"><p className="text-xs text-gray-400 mb-2">Actions Required</p><ul className="space-y-1">{result.maintenance_actions.map((a, i) => <li key={i} className="text-sm text-yellow-300 flex gap-2"><span></span>{a}</li>)}</ul></div>}
            </div>
          )}
        </div>
      )}

      {error && <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-4 text-red-300 text-sm">{error}</div>}
    </div>
  )
}
