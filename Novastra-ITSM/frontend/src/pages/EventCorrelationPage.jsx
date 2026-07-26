// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: Novastra-ITSM — frontend/src/pages (EventCorrelationPage.jsx)
// Date: 2026-01-02
// ---------------------------------------------------------------------------
import React, { useState } from 'react'
import { GitBranch, AlertTriangle, Clock } from 'lucide-react'
import api from '../services/api.js'

const TABS = ['Correlate Events', 'Build Timeline', 'Blast Radius']

const SAMPLE_EVENTS = JSON.stringify([
  { id: 'EV-001', timestamp: '2024-01-15T09:00:00', type: 'Alert', ci: 'DB-PROD-01', service: 'OrderDB', message: 'High CPU usage 92%', severity: 'HIGH' },
  { id: 'EV-002', timestamp: '2024-01-15T09:02:00', type: 'Alert', ci: 'APP-PROD-02', service: 'OrderAPI', message: 'DB connection timeout', severity: 'CRITICAL' },
  { id: 'EV-003', timestamp: '2024-01-15T09:03:00', type: 'Incident', ci: 'APP-PROD-02', service: 'OrderAPI', message: 'Service unavailable', severity: 'CRITICAL' },
  { id: 'EV-004', timestamp: '2024-01-15T09:04:00', type: 'Alert', ci: 'LB-PROD-01', service: 'LoadBalancer', message: 'Backend unhealthy', severity: 'HIGH' },
  { id: 'EV-005', timestamp: '2024-01-15T09:15:00', type: 'Alert', ci: 'NET-CORE-01', service: 'Network', message: 'Packet loss detected', severity: 'MEDIUM' },
], null, 2)

const sevColor = s => ({ CRITICAL: 'text-red-400', HIGH: 'text-orange-400', MEDIUM: 'text-yellow-400', LOW: 'text-blue-400' }[s] || 'text-gray-400')
const blastColor = s => ({ CRITICAL: 'bg-red-500/10 border-red-500/30 text-red-400', HIGH: 'bg-orange-500/10 border-orange-500/30 text-orange-400', MEDIUM: 'bg-yellow-500/10 border-yellow-500/30 text-yellow-400', LOW: 'bg-blue-500/10 border-blue-500/30 text-blue-400' }[s] || 'bg-gray-500/10 border-gray-500/30 text-gray-400')

// Function: EventCorrelationPage
export default function EventCorrelationPage() {
  const [tab, setTab] = useState('Correlate Events')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')

  // Correlate tab
  const [eventsJson, setEventsJson] = useState(SAMPLE_EVENTS)
  const [windowMins, setWindowMins] = useState(15)
  const [detectStorms, setDetectStorms] = useState(true)

  // Timeline tab
  const [tlEventsJson, setTlEventsJson] = useState(SAMPLE_EVENTS)
  const [incidentId, setIncidentId] = useState('')

  // Blast radius tab
  const [rootCi, setRootCi] = useState('DB-PROD-01')
  const [relJson, setRelJson] = useState(JSON.stringify([
    { source: 'DB-PROD-01', target: 'APP-PROD-02', type: 'depends_on' },
    { source: 'APP-PROD-02', target: 'LB-PROD-01', type: 'depends_on' },
  ], null, 2))
  const [recentEvJson, setRecentEvJson] = useState(SAMPLE_EVENTS)

  const inputCls = 'w-full bg-gray-800 border border-white/10 rounded-lg px-3 py-1.5 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-blue-500'
  const labelCls = 'block text-xs font-medium text-gray-400 mb-1'

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

  // Function: handleCorrelate
  const handleCorrelate = () => {
    let events
    try { events = JSON.parse(eventsJson) } catch { setError('Invalid JSON for events'); return }
    call('/events/correlate', { events, window_minutes: windowMins, detect_storms: detectStorms })
  }

  // Function: handleTimeline
  const handleTimeline = () => {
    let events
    try { events = JSON.parse(tlEventsJson) } catch { setError('Invalid JSON for events'); return }
    call('/events/timeline', { events, incident_id: incidentId })
  }

  // Function: handleBlast
  const handleBlast = () => {
    let relationships, recent_events
    try { relationships = JSON.parse(relJson) } catch { setError('Invalid JSON for relationships'); return }
    try { recent_events = JSON.parse(recentEvJson) } catch { setError('Invalid JSON for recent events'); return }
    call('/events/impact-blast-radius', { root_ci: rootCi, relationships, recent_events })
  }

  return (
    <div className="flex flex-col h-full bg-gray-950 text-white overflow-hidden">
      <div className="px-6 pt-5 pb-4 border-b border-white/10 shrink-0">
        <div className="flex items-center gap-3 mb-1">
          <GitBranch size={20} className="text-purple-400" />
          <h1 className="text-sm font-semibold">Event Correlation</h1>
        </div>
        <p className="text-xs text-gray-400">Temporal correlation, event storms, causal chains, and blast radius analysis</p>
        <div className="flex gap-1 mt-4">
          {TABS.map(t => (
            <button key={t} onClick={() => { setTab(t); setResult(null); setError('') }}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${tab === t ? 'bg-purple-600 text-white' : 'text-gray-400 hover:text-white hover:bg-white/10'}`}>
              {t}
            </button>
          ))}
        </div>
      </div>

      <div className="flex-1 overflow-y-auto px-6 py-5">
        {error && <div className="mb-4 p-3 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400 text-sm">{error}</div>}

        {tab === 'Correlate Events' && (
          <div className="grid grid-cols-2 gap-6">
            <div className="space-y-4">
              <div>
                <label className={labelCls}>Events JSON (array of event objects)</label>
                <textarea value={eventsJson} onChange={e => setEventsJson(e.target.value)}
                  rows={14} className={`${inputCls} font-mono text-xs`} />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className={labelCls}>Time Window (minutes)</label>
                  <input type="number" value={windowMins} onChange={e => setWindowMins(+e.target.value)} min={1} max={120}
                    className={inputCls} />
                </div>
                <div className="flex items-center gap-2 mt-5">
                  <input type="checkbox" checked={detectStorms} onChange={e => setDetectStorms(e.target.checked)}
                    className="w-4 h-4 rounded accent-purple-500" />
                  <label className="text-sm text-gray-300">Detect Event Storms</label>
                </div>
              </div>
              <button onClick={handleCorrelate} disabled={loading}
                className="w-full py-2.5 rounded-xl bg-purple-600 hover:bg-purple-700 disabled:opacity-50 text-sm font-semibold transition-colors">
                {loading ? 'Correlating...' : 'Correlate Events'}
              </button>
            </div>

            <div>
              {result && (
                <div className="space-y-4">
                  <div className="grid grid-cols-3 gap-2">
                    {[['Total Events', result.total_events], ['Correlations', result.correlations?.length], ['Storms', result.storms?.length]].map(([k, v]) => (
                      <div key={k} className="bg-gray-800 rounded-xl p-3 text-center">
                        <p className="text-2xl font-bold text-purple-400">{v ?? 0}</p>
                        <p className="text-xs text-gray-400 mt-0.5">{k}</p>
                      </div>
                    ))}
                  </div>

                  {result.narrative && (
                    <div className="bg-gray-800 rounded-xl p-3">
                      <p className="text-xs text-gray-400 mb-1">Analysis</p>
                      <p className="text-sm text-gray-200">{result.narrative}</p>
                    </div>
                  )}

                  {result.correlations?.length > 0 && (
                    <div className="bg-gray-800 rounded-xl p-3">
                      <p className="text-xs font-semibold text-gray-400 mb-2 uppercase tracking-wide">Correlation Groups</p>
                      <div className="space-y-2">
                        {result.correlations.map((c, i) => (
                          <div key={i} className="bg-gray-700/50 rounded-lg p-2.5">
                            <div className="flex items-center justify-between mb-1">
                              <span className="text-xs font-mono text-purple-300">{c.group_id}</span>
                              <span className={`text-xs font-medium ${sevColor(c.peak_severity)}`}>{c.peak_severity}</span>
                            </div>
                            <p className="text-xs text-gray-300">{c.event_count} events Â· {c.timespan_minutes}min span</p>
                            <p className="text-xs text-gray-400 mt-0.5">CIs: {c.affected_cis?.join(', ')}</p>
                            <p className="text-xs text-gray-400">{c.likely_root_cause}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {result.storms?.length > 0 && (
                    <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-3">
                      <p className="text-xs font-semibold text-red-400 mb-2 uppercase tracking-wide flex items-center gap-1">
                        <AlertTriangle size={12} /> Event Storms Detected
                      </p>
                      {result.storms.map((s, i) => (
                        <div key={i} className="bg-red-500/10 rounded-lg p-2 mb-1.5">
                          <p className="text-xs font-mono text-red-300">{s.storm_id}: {s.event_count} events</p>
                          <p className="text-xs text-gray-400">CIs: {s.cis?.join(', ')}</p>
                        </div>
                      ))}
                    </div>
                  )}

                  {result.hotspot_cis?.length > 0 && (
                    <div className="bg-gray-800 rounded-xl p-3">
                      <p className="text-xs font-semibold text-gray-400 mb-2 uppercase tracking-wide">Hot-spot CIs</p>
                      {result.hotspot_cis.map((h, i) => (
                        <div key={i} className="flex justify-between text-xs py-0.5">
                          <span className="text-gray-300 font-mono">{h.ci}</span>
                          <span className="text-orange-400 font-medium">{h.event_count} events</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
              {!result && !loading && <div className="flex items-center justify-center h-40 text-gray-500 text-sm">Run correlation to see results</div>}
            </div>
          </div>
        )}

        {tab === 'Build Timeline' && (
          <div className="grid grid-cols-2 gap-6">
            <div className="space-y-4">
              <div>
                <label className={labelCls}>Incident ID (optional)</label>
                <input value={incidentId} onChange={e => setIncidentId(e.target.value)} placeholder="INC0001234" className={inputCls} />
              </div>
              <div>
                <label className={labelCls}>Events JSON</label>
                <textarea value={tlEventsJson} onChange={e => setTlEventsJson(e.target.value)} rows={14} className={`${inputCls} font-mono text-xs`} />
              </div>
              <button onClick={handleTimeline} disabled={loading}
                className="w-full py-2.5 rounded-xl bg-purple-600 hover:bg-purple-700 disabled:opacity-50 text-sm font-semibold transition-colors">
                {loading ? 'Building...' : 'Build Timeline'}
              </button>
            </div>

            <div>
              {result?.timeline && (
                <div className="space-y-2">
                  <div className="flex gap-4 text-sm text-gray-400 mb-2">
                    <span>{result.total_events} events</span>
                    <span>|</span>
                    <span>{result.timespan_minutes} min span</span>
                  </div>
                  <div className="relative pl-4 border-l border-purple-500/30 space-y-3">
                    {result.timeline.map((ev, i) => (
                      <div key={i} className="relative">
                        <div className="absolute -left-[1.45rem] top-1 w-2.5 h-2.5 rounded-full border-2 border-purple-500 bg-gray-950" />
                        <div className={`bg-gray-800 rounded-xl p-3 ${ev.marker === 'CRITICAL' ? 'border border-red-500/40' : ''}`}>
                          <div className="flex items-center justify-between mb-0.5">
                            <div className="flex items-center gap-2">
                              <Clock size={11} className="text-gray-500" />
                              <span className="text-[10px] text-gray-400 font-mono">{ev.timestamp}</span>
                              <span className="text-[10px] font-mono bg-gray-700 px-1.5 rounded text-gray-300">{ev.type}</span>
                            </div>
                            <span className={`text-xs font-medium ${sevColor(ev.severity)}`}>{ev.severity}</span>
                          </div>
                          <p className="text-xs text-gray-200 mt-0.5">{ev.message}</p>
                          <p className="text-[10px] text-gray-500 mt-0.5">CI: {ev.ci} Â· Service: {ev.service}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              {!result && !loading && <div className="flex items-center justify-center h-40 text-gray-500 text-sm">Build a timeline to see results</div>}
            </div>
          </div>
        )}

        {tab === 'Blast Radius' && (
          <div className="grid grid-cols-2 gap-6">
            <div className="space-y-4">
              <div>
                <label className={labelCls}>Root CI</label>
                <input value={rootCi} onChange={e => setRootCi(e.target.value)} placeholder="DB-PROD-01" className={inputCls} />
              </div>
              <div>
                <label className={labelCls}>CMDB Relationships JSON</label>
                <textarea value={relJson} onChange={e => setRelJson(e.target.value)} rows={5} className={`${inputCls} font-mono text-xs`} />
              </div>
              <div>
                <label className={labelCls}>Recent Events JSON</label>
                <textarea value={recentEvJson} onChange={e => setRecentEvJson(e.target.value)} rows={7} className={`${inputCls} font-mono text-xs`} />
              </div>
              <button onClick={handleBlast} disabled={loading}
                className="w-full py-2.5 rounded-xl bg-purple-600 hover:bg-purple-700 disabled:opacity-50 text-sm font-semibold transition-colors">
                {loading ? 'Analyzing...' : 'Analyze Blast Radius'}
              </button>
            </div>

            <div>
              {result && (
                <div className="space-y-4">
                  <div className={`border rounded-2xl p-5 ${blastColor(result.blast_level)}`}>
                    <p className="text-xs uppercase tracking-wide mb-1 opacity-70">Blast Level</p>
                    <p className="text-3xl font-bold">{result.blast_level}</p>
                    <p className="text-sm mt-1 opacity-80">Score: {result.blast_score}</p>
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <div className="bg-gray-800 rounded-xl p-3 text-center">
                      <p className="text-2xl font-bold text-purple-400">{result.affected_ci_count}</p>
                      <p className="text-xs text-gray-400">Affected CIs</p>
                    </div>
                    <div className="bg-gray-800 rounded-xl p-3 text-center">
                      <p className="text-2xl font-bold text-orange-400">{result.recent_events_on_affected_cis}</p>
                      <p className="text-xs text-gray-400">Active Events</p>
                    </div>
                  </div>
                  <div className="bg-gray-800 rounded-xl p-3">
                    <p className="text-xs text-gray-400 mb-1">Summary</p>
                    <p className="text-sm text-gray-200">{result.summary}</p>
                  </div>
                  {result.directly_affected_cis?.length > 0 && (
                    <div className="bg-gray-800 rounded-xl p-3">
                      <p className="text-xs font-semibold text-gray-400 mb-2 uppercase tracking-wide">Affected CIs</p>
                      <div className="flex flex-wrap gap-1.5">
                        {result.directly_affected_cis.map((ci, i) => (
                          <span key={i} className="px-2 py-1 bg-gray-700 rounded-lg text-xs text-gray-200 font-mono">{ci}</span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
              {!result && !loading && <div className="flex items-center justify-center h-40 text-gray-500 text-sm">Analyze a CI to see blast radius</div>}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
