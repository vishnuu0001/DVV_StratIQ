// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: Novastra-ITSM — frontend/src/pages (CMDBPage.jsx)
// Date: 2025-11-04
// ---------------------------------------------------------------------------
import React, { useEffect, useState } from 'react'
import { Database, RefreshCw } from 'lucide-react'
import api from '../services/api.js'

const TABS = ['Natural Language Query', 'Relationship Discovery', 'License Optimization']
const inputCls = 'w-full bg-gray-800 border border-white/10 rounded-lg px-3 py-2 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-blue-500'

// Function: CMDBPage
export default function CMDBPage() {
  const [tab, setTab] = useState(TABS[0])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)
  const [status, setStatus] = useState({ ready: false, counts: {}, total_records: 0 })
  const [connection, setConnection] = useState({ base_url: '', username: '', password: '', limit_per_table: 2000, verify_ssl: false })
  const [query, setQuery] = useState('Show all incidents related to Outlook')
  const [page, setPage] = useState(1)

  // Function: loadStatus
  const loadStatus = async () => {
    try { setStatus((await api.get('/cmdb/status')).data) } catch { /* handled by auth shell */ }
  }
  // Function: loadDefaultConnection
  const loadDefaultConnection = async () => {
    try {
      const { data } = await api.get('/cmdb/default-connection')
      if (data.configured) {
        setConnection((prev) => ({
          ...prev,
          base_url: prev.base_url || data.base_url,
          username: prev.username || data.username,
          password: prev.password || data.password,
          verify_ssl: data.verify_ssl,
        }))
      }
    } catch { /* no server-side default configured */ }
  }
  useEffect(() => { loadStatus(); loadDefaultConnection() }, [])

  // Function: run
  const run = async (endpoint, payload = {}) => {
    setLoading(true); setError('')
    try {
      // CMDB ingestion authenticates separately with ServiceNow. An upstream
      // credential failure must remain on this page and must never clear the
      // user's valid Strat-Aqorynth portal session.
      const response = await api.post(endpoint, payload, { timeout: 180000, skipAuthRedirect: endpoint === '/cmdb/ingest' })
      setResult(response.data)
      return response.data
    } catch (e) {
      setError(e.response?.data?.detail || e.message || 'Request failed')
      return null
    } finally { setLoading(false) }
  }

  // Function: ingest
  const ingest = async () => {
    if (!connection.base_url || !connection.username || !connection.password) {
      setError('ServiceNow URL, username, and password/token are required.')
      return
    }
    const data = await run('/cmdb/ingest', connection)
    if (data) {
      setStatus(data)
      if (data.status === 'failed') {
        setError(data.errors?.[data.failed_entity] || `ServiceNow synchronization failed for ${data.failed_table || 'a required table'}.`)
      } else if (data.status === 'partial') {
        const details = Object.entries(data.errors || {}).map(([name, message]) => `${name}: ${message}`).join(' | ')
        setError(`CMDB synchronization completed partially. ${details}`)
      }
    }
  }

  // Function: runQuery
  const runQuery = async (nextPage = 1) => {
    setPage(nextPage)
    await run('/cmdb/nl-query', { query, page: nextPage, page_size: 50 })
  }

  const counts = Object.entries(status.counts || {})
  const records = result?.sample_results || []
  const columns = records.length ? Object.keys(records[0]).slice(0, 8) : []

  return (
    <div className="flex-1 overflow-y-auto bg-gray-950 p-6 space-y-6">
      <div className="flex items-center gap-3">
        <Database size={22} className="text-blue-400" />
        <div><h1 className="text-sm font-semibold text-white">CMDB Intelligence</h1>
          <p className="text-xs text-gray-400">Validated queries over synchronized ServiceNow CMDB, ITSM, asset, and license data</p></div>
      </div>

      <section className="bg-gray-900 border border-white/10 rounded-xl p-5 space-y-4">
        <div className="flex items-center justify-between">
          <div><h2 className="text-sm font-semibold text-white">ServiceNow CMDB Sync</h2>
            <p className="text-xs text-gray-500">Credentials are used for this request only and are not stored.</p></div>
          <span className={`text-xs px-2 py-1 rounded ${status.ready ? 'bg-green-500/20 text-green-300' : 'bg-yellow-500/20 text-yellow-300'}`}>
            {status.ready ? `${status.total_records} records ready` : 'Not synchronized'}
          </span>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-2">
          <input className={inputCls} placeholder="https://instance.service-now.com" value={connection.base_url} onChange={e => setConnection(v => ({ ...v, base_url: e.target.value }))} />
          <input className={inputCls} placeholder="Username" value={connection.username} onChange={e => setConnection(v => ({ ...v, username: e.target.value }))} />
          <input className={inputCls} type="password" placeholder="Password / API token" value={connection.password} onChange={e => setConnection(v => ({ ...v, password: e.target.value }))} />
          <button onClick={ingest} disabled={loading} className="bg-blue-600 hover:bg-blue-500 disabled:opacity-50 rounded-lg text-xs text-white font-medium flex items-center justify-center gap-2">
            <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />{loading ? 'Synchronizing...' : 'Sync CMDB Data'}
          </button>
        </div>
        {counts.length > 0 && <div className="flex flex-wrap gap-2">{counts.map(([name, count]) => <span key={name} className="text-xs bg-gray-800 px-2 py-1 rounded text-gray-300">{name}: {count}</span>)}</div>}
      </section>

      <div className="flex gap-1 bg-gray-900 rounded-lg p-1 w-fit">{TABS.map(name =>
        <button key={name} onClick={() => { setTab(name); setResult(null); setError('') }} className={`px-3 py-1.5 rounded text-xs ${tab === name ? 'bg-blue-600 text-white' : 'text-gray-400'}`}>{name}</button>)}</div>

      <section className="bg-gray-900 border border-white/10 rounded-xl p-5 space-y-4">
        {tab === TABS[0] && <>
          <label className="text-xs text-gray-400">Natural Language Query</label>
          <textarea className={inputCls} rows={3} value={query} onChange={e => setQuery(e.target.value)} />
          <button onClick={() => runQuery(1)} disabled={loading || !status.ready || !query.trim()} className="px-4 py-2 bg-blue-600 disabled:opacity-50 rounded text-xs text-white">{loading ? 'Executing...' : 'Run Validated Query'}</button>
          {result?.structured_query && <pre className="bg-gray-800 rounded p-3 text-xs text-green-300 overflow-x-auto">{JSON.stringify(result.structured_query, null, 2)}</pre>}
          {result && <p className="text-sm text-gray-300">{result.explanation} Exact matches: <b>{result.estimated_record_count}</b></p>}
          {records.length > 0 && <div className="overflow-x-auto"><table className="w-full text-xs"><thead><tr>{columns.map(c => <th key={c} className="text-left text-gray-500 p-2">{c}</th>)}</tr></thead><tbody>{records.map((row, i) => <tr key={i} className="border-t border-white/5">{columns.map(c => <td key={c} className="text-gray-300 p-2 max-w-xs truncate">{typeof row[c] === 'object' ? JSON.stringify(row[c]) : String(row[c] ?? '')}</td>)}</tr>)}</tbody></table></div>}
          {result?.result_page?.pages > 1 && <div className="flex gap-2"><button disabled={page <= 1} onClick={() => runQuery(page - 1)} className="text-xs text-blue-300 disabled:opacity-30">Previous</button><span className="text-xs text-gray-500">Page {page} of {result.result_page.pages}</span><button disabled={page >= result.result_page.pages} onClick={() => runQuery(page + 1)} className="text-xs text-blue-300 disabled:opacity-30">Next</button></div>}
        </>}

        {tab === TABS[1] && <>
          <p className="text-sm text-gray-300">Analyse synchronized <code>cmdb_rel_ci</code>, incidents, and changes.</p>
          <button onClick={() => run('/cmdb/discover-relationships')} disabled={loading || !status.ready} className="px-4 py-2 bg-blue-600 disabled:opacity-50 rounded text-xs text-white">Discover Relationships</button>
          {result && <><p className="text-xs text-gray-400">Authoritative relationships: {result.authoritative_relationship_count} · incidents with CIs: {Object.keys(result.incident_counts_by_ci || {}).length}</p>
            {(result.suggested_relationships || []).slice(0, 100).map((r, i) => <div key={i} className="bg-gray-800 p-3 rounded text-xs text-gray-200">{r.source_ci} → <span className="text-blue-300">{r.relationship_type}</span> → {r.target_ci}</div>)}</>}
        </>}

        {tab === TABS[2] && <>
          <p className="text-sm text-gray-300">Calculate reclaim opportunities from synchronized license entitlements, allocations, and unit costs.</p>
          <button onClick={() => run('/cmdb/license-analysis', { page: 1, page_size: 50 })} disabled={loading || !status.ready} className="px-4 py-2 bg-blue-600 disabled:opacity-50 rounded text-xs text-white">Analyse Synchronized Licenses</button>
          {result && <><div className="bg-green-500/10 border border-green-500/30 p-4 rounded"><p className="text-xs text-gray-400">Measured annual saving opportunity</p><p className="text-2xl text-green-400 font-bold">${result.total_annual_saving_usd?.toLocaleString()}</p></div>
            <p className="text-xs text-gray-400">Assets: {result.asset_count} · licenses: {result.license_count}</p>
            {(result.opportunities || []).map((o, i) => <div key={i} className="grid grid-cols-4 gap-2 bg-gray-800 p-3 rounded text-xs"><span className="text-white">{o.product}</span><span>{o.active_users}/{o.licensed_seats} allocated</span><span>{o.reclaim_seats} reclaim</span><span className="text-green-400">${o.annual_saving_estimate_usd?.toLocaleString()}</span></div>)}</>}
        </>}
      </section>
      {error && <div className="bg-red-500/10 border border-red-500/30 rounded p-4 text-red-300 text-sm">{error}</div>}
    </div>
  )
}
