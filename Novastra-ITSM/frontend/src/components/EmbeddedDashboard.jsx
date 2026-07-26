// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: Novastra-ITSM — frontend/src/components (EmbeddedDashboard.jsx)
// Date: 2025-07-24
// ---------------------------------------------------------------------------
import { useState, useEffect } from 'react'
import { Search, RefreshCw, MessageSquare, Calendar, Filter, Edit2, Save, X as XIcon, ChevronLeft, ChevronRight, Database, AlertCircle } from 'lucide-react'
import { getDashboardIncidents, getDashboardFilterOptions, updateDashboardIncident } from '../services/api.js'
import { toast } from 'react-hot-toast'

// Matches the backend's fixed 5-value state taxonomy — see
// backend/services/operational_ingestion.py's CANONICAL_STATES / normalize_state().
const STATE_STYLES = {
  'Open':                    'bg-amber-500/15 text-amber-300 ring-1 ring-amber-500/30',
  'In-Progress':             'bg-blue-500/15 text-blue-300 ring-1 ring-blue-500/30',
  'Pending Clarifications':  'bg-orange-500/15 text-orange-300 ring-1 ring-orange-500/30',
  'Closed':                  'bg-emerald-500/15 text-emerald-300 ring-1 ring-emerald-500/30',
  'Re-Opened':               'bg-violet-500/15 text-violet-300 ring-1 ring-violet-500/30',
}

// Function: StateBadge
function StateBadge({ state }) {
  const cls = STATE_STYLES[state] || 'bg-slate-600/30 text-slate-300 ring-1 ring-slate-600/40'
  return (
    <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide ${cls}`}>
      {state || 'N/A'}
    </span>
  )
}

// Function: AssigneePill
function AssigneePill({ name }) {
  if (!name) return <span className="text-[10px] text-slate-500 italic">(Unassigned)</span>
  const initials = name.split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase()
  return (
    <div className="flex items-center gap-1.5">
      <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-violet-500/20 text-[9px] font-bold text-violet-300 ring-1 ring-violet-500/30">
        {initials}
      </span>
      <span className="text-[10px] text-violet-300 truncate max-w-[80px]">{name}</span>
    </div>
  )
}

// Function: SkeletonRow
function SkeletonRow() {
  return (
    <tr>
      {[40, 160, 72, 56, 140, 80].map((w, i) => (
        <td key={i} className="px-3 py-3">
          <div className="h-3 animate-pulse rounded bg-slate-700/60" style={{ width: w }} />
          {i === 0 && <div className="mt-1.5 h-2 w-24 animate-pulse rounded bg-slate-700/40" />}
        </td>
      ))}
    </tr>
  )
}

// Function: EmbeddedDashboard
export default function EmbeddedDashboard({ onSelectIncident, isConnected }) {
  const [incidents, setIncidents] = useState([])
  const [filterOptions, setFilterOptions] = useState({ states: [], assigned_to: [] })
  const [loading, setLoading] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [stateFilter, setStateFilter] = useState('')
  const [assignedToFilter, setAssignedToFilter] = useState('')
  const [page, setPage] = useState(0)
  const [total, setTotal] = useState(0)
  const [limit] = useState(25)
  const [editingRow, setEditingRow] = useState(null)
  const [editValues, setEditValues] = useState({})
  const [saving, setSaving] = useState(false)
  const [refreshing, setRefreshing] = useState(false)

  // Function: loadIncidents
  const loadIncidents = async (searchText = '', pageNum = 0, state = '', assignedTo = '') => {
    if (!isConnected) return
    try {
      setLoading(true)
      const params = { limit, offset: pageNum * limit }
      if (searchText) params.search = searchText
      if (state) params.state = state
      if (assignedTo) params.assigned_to = assignedTo
      const { data } = await getDashboardIncidents(params)
      setIncidents(data.incidents || [])
      setTotal(data.total || 0)
      setPage(pageNum)
    } catch {
      toast.error('Failed to load dashboard incidents')
    } finally {
      setLoading(false)
    }
  }

  // Function: loadFilterOptions
  const loadFilterOptions = async () => {
    if (!isConnected) return
    try {
      const { data } = await getDashboardFilterOptions()
      setFilterOptions(data)
    } catch { /* silent */ }
  }

  useEffect(() => {
    if (isConnected) { loadIncidents(); loadFilterOptions() }
  }, [isConnected])

  // Function: handleSearch
  const handleSearch = (e) => { e.preventDefault(); loadIncidents(searchTerm, 0, stateFilter, assignedToFilter) }

  // Function: handleRefresh
  const handleRefresh = async () => {
    setRefreshing(true)
    await Promise.all([loadIncidents(searchTerm, page, stateFilter, assignedToFilter), loadFilterOptions()])
    setRefreshing(false)
    toast.success('Dashboard refreshed')
  }

  // Function: handleEdit
  const handleEdit = (incident) => {
    setEditingRow(incident.incident_id)
    setEditValues({ assigned_to: incident.assigned_to || '', state: incident.state || '', close_notes: incident.close_notes || '' })
  }

  // Function: handleSaveEdit
  const handleSaveEdit = async (incidentNumber) => {
    try {
      setSaving(true)
      const { data } = await updateDashboardIncident(incidentNumber, { incident_number: incidentNumber, ...editValues, sync_to_servicenow: true })
      if (data.success) {
        toast.success(data.servicenow_synced ? 'Synced to ServiceNow!' : 'Updated locally!')
        await loadIncidents(searchTerm, page, stateFilter, assignedToFilter)
        setEditingRow(null); setEditValues({})
      } else { toast.error('Update failed') }
    } catch { toast.error('Failed to update incident') }
    finally { setSaving(false) }
  }

  const totalPages = Math.ceil(total / limit)
  const hasFilters = stateFilter || assignedToFilter

  if (!isConnected) return null

  const inpCls = 'w-full bg-slate-900/60 border border-slate-700/60 rounded-lg px-3 py-1.5 text-[11px] text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500/60 focus:ring-1 focus:ring-cyan-500/30 transition'
  const selCls = 'bg-slate-900/60 border border-slate-700/60 rounded-lg px-3 py-1.5 text-[11px] text-slate-200 focus:outline-none focus:border-cyan-500/60 focus:ring-1 focus:ring-cyan-500/30 transition appearance-none pr-7'

  return (
    <section className="relative overflow-hidden rounded-2xl border border-slate-700/50 bg-gradient-to-b from-slate-900 to-[#080f1e] shadow-2xl">
      {/* top accent bar */}
      <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-cyan-500/60 to-transparent" />

      {/* Header */}
      <div className="flex items-center justify-between gap-4 px-5 py-4 border-b border-slate-800/70">
        <div className="flex items-center gap-3">
          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-cyan-500/10 ring-1 ring-cyan-500/30">
            <Database size={14} className="text-cyan-400" />
          </div>
          <div>
            <h2 className="text-xs font-black uppercase tracking-widest text-slate-100">Synced Incidents Dashboard</h2>
            <p className="text-[10px] text-slate-500 mt-0.5">View and manage all synced ServiceNow tickets</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5 rounded-full border border-slate-700/60 bg-slate-800/50 px-3 py-1">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
            <span className="text-[10px] font-semibold tabular-nums text-slate-300">{total.toLocaleString()} tickets</span>
          </div>
          <button
            onClick={handleRefresh}
            className="inline-flex items-center gap-1.5 rounded-lg border border-slate-700/60 bg-slate-800/40 px-3 py-1.5 text-[11px] font-semibold text-slate-300 hover:border-cyan-500/40 hover:bg-slate-700/50 hover:text-cyan-300 transition-all"
          >
            <RefreshCw size={11} className={refreshing ? 'animate-spin' : ''} />
            Refresh
          </button>
        </div>
      </div>

      {/* Search + Filter bar */}
      <div className="flex flex-wrap items-center gap-2 px-5 py-3 border-b border-slate-800/50 bg-slate-900/20">
        <form onSubmit={handleSearch} className="flex flex-1 min-w-48 gap-2">
          <div className="relative flex-1">
            <Search size={12} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
            <input
              type="text"
              value={searchTerm}
              onChange={e => setSearchTerm(e.target.value)}
              placeholder="Search incidents..."
              className="w-full bg-slate-900/60 border border-slate-700/60 rounded-lg pl-8 pr-3 py-1.5 text-[11px] text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500/60 focus:ring-1 focus:ring-cyan-500/30 transition"
            />
          </div>
          <button type="submit"
            className="px-4 py-1.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white text-[11px] font-semibold transition-colors">
            Search
          </button>
        </form>

        <div className="flex items-center gap-2">
          <Filter size={11} className="text-slate-500 shrink-0" />
          <div className="relative">
            <select value={stateFilter} onChange={e => { setStateFilter(e.target.value); setTimeout(() => loadIncidents(searchTerm, 0, e.target.value, assignedToFilter), 0) }} className={selCls}>
              <option value="">All States</option>
              {filterOptions.states.map(s => <option key={s} value={s}>{s}</option>)}
            </select>
            <ChevronRight size={10} className="pointer-events-none absolute right-2 top-1/2 -translate-y-1/2 rotate-90 text-slate-400" />
          </div>
          <div className="relative">
            <select value={assignedToFilter} onChange={e => { setAssignedToFilter(e.target.value); setTimeout(() => loadIncidents(searchTerm, 0, stateFilter, e.target.value), 0) }} className={selCls}>
              <option value="">All Assignees</option>
              {filterOptions.assigned_to.map(a => <option key={a} value={a}>{a || '(Unassigned)'}</option>)}
            </select>
            <ChevronRight size={10} className="pointer-events-none absolute right-2 top-1/2 -translate-y-1/2 rotate-90 text-slate-400" />
          </div>
          {hasFilters && (
            <button onClick={() => { setStateFilter(''); setAssignedToFilter(''); loadIncidents(searchTerm, 0, '', '') }}
              className="flex items-center gap-1 rounded-lg bg-slate-700/50 px-2.5 py-1.5 text-[10px] font-semibold text-slate-300 hover:bg-slate-700 transition">
              <XIcon size={9} /> Clear
            </button>
          )}
        </div>
      </div>

      {/* Table */}
      <div className="overflow-hidden">
        <div className="max-h-[420px] overflow-y-auto overflow-x-auto scrollbar-thin scrollbar-track-transparent scrollbar-thumb-slate-700">
          <table className="w-full min-w-[720px] border-collapse">
            <thead className="sticky top-0 z-10">
              <tr className="bg-slate-900/95 backdrop-blur-sm border-b border-slate-800">
                {['Incident', 'Description', 'Assigned', 'State', 'Resolution', 'Actions'].map(col => (
                  <th key={col} className="px-3 py-2.5 text-left text-[10px] font-black uppercase tracking-widest text-slate-500">
                    {col}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {loading
                ? Array.from({ length: 6 }).map((_, i) => <SkeletonRow key={i} />)
                : incidents.length === 0
                  ? (
                    <tr>
                      <td colSpan="6" className="py-12 text-center">
                        <AlertCircle size={20} className="mx-auto mb-2 text-slate-600" />
                        <p className="text-[11px] text-slate-500">No incidents found</p>
                      </td>
                    </tr>
                  )
                  : incidents.map((incident, idx) => {
                    const isEditing = editingRow === incident.incident_id
                    return (
                      <tr key={incident.incident_id}
                        className={`group border-b border-slate-800/50 transition-colors
                          ${idx % 2 === 0 ? 'bg-transparent' : 'bg-slate-900/25'}
                          ${isEditing ? 'bg-cyan-950/20 border-cyan-900/30' : 'hover:bg-slate-800/30'}`}
                      >
                        {/* Incident # */}
                        <td className="px-3 py-2.5 whitespace-nowrap">
                          <span className="font-mono text-[11px] font-bold text-cyan-400 group-hover:text-cyan-300 transition-colors">
                            {incident.number}
                          </span>
                          <div className="mt-0.5 flex items-center gap-1 text-[9px] text-slate-600">
                            <Calendar size={9} />
                            {incident.opened_at || 'N/A'}
                          </div>
                        </td>

                        {/* Description */}
                        <td className="px-3 py-2.5 max-w-[200px]">
                          <p className="truncate text-[11px] text-slate-300" title={incident.short_description}>
                            {incident.short_description || 'No description'}
                          </p>
                        </td>

                        {/* Assigned */}
                        <td className="px-3 py-2.5 whitespace-nowrap">
                          {isEditing ? (
                            <input type="text" value={editValues.assigned_to} onChange={e => setEditValues({ ...editValues, assigned_to: e.target.value })}
                              className={inpCls} placeholder="Assignee" />
                          ) : (
                            <AssigneePill name={incident.assigned_to} />
                          )}
                        </td>

                        {/* State */}
                        <td className="px-3 py-2.5 whitespace-nowrap">
                          {isEditing ? (
                            <select value={editValues.state} onChange={e => setEditValues({ ...editValues, state: e.target.value })} className={selCls}>
                              <option value="">Select State</option>
                              {filterOptions.states.map(s => <option key={s} value={s}>{s}</option>)}
                            </select>
                          ) : (
                            <StateBadge state={incident.state} />
                          )}
                        </td>

                        {/* Resolution */}
                        <td className="px-3 py-2.5 max-w-[200px]">
                          {isEditing ? (
                            <input value={editValues.close_notes} onChange={e => setEditValues({ ...editValues, close_notes: e.target.value })}
                              className={inpCls} placeholder="Resolution notes..." />
                          ) : (
                            <p className="truncate text-[10px] text-slate-400" title={incident.close_notes}>
                              {incident.close_notes || <span className="italic text-slate-600">(No resolution)</span>}
                            </p>
                          )}
                        </td>

                        {/* Actions */}
                        <td className="px-3 py-2.5 whitespace-nowrap">
                          <div className="flex items-center gap-1.5">
                            {isEditing ? (
                              <>
                                <button onClick={() => handleSaveEdit(incident.number)} disabled={saving}
                                  className="inline-flex items-center gap-1 rounded-lg bg-emerald-600 hover:bg-emerald-500 px-2.5 py-1 text-[10px] font-semibold text-white disabled:opacity-40 transition">
                                  <Save size={10} />{saving ? 'Saving…' : 'Save'}
                                </button>
                                <button onClick={() => { setEditingRow(null); setEditValues({}) }} disabled={saving}
                                  className="inline-flex items-center gap-1 rounded-lg bg-slate-700 hover:bg-slate-600 px-2 py-1 text-[10px] text-slate-300 transition">
                                  <XIcon size={10} />
                                </button>
                              </>
                            ) : (
                              <>
                                <button onClick={() => handleEdit(incident)}
                                  className="inline-flex items-center gap-1 rounded-lg border border-slate-600/60 bg-slate-800/60 hover:border-blue-500/50 hover:bg-blue-600/10 hover:text-blue-300 px-2.5 py-1 text-[10px] font-semibold text-slate-300 transition-all">
                                  <Edit2 size={10} />Edit
                                </button>
                                <button onClick={() => onSelectIncident(incident)}
                                  className="inline-flex items-center gap-1 rounded-lg bg-cyan-600 hover:bg-cyan-500 px-2.5 py-1 text-[10px] font-semibold text-white shadow-sm shadow-cyan-900/40 transition-colors">
                                  <MessageSquare size={10} />Chat
                                </button>
                              </>
                            )}
                          </div>
                        </td>
                      </tr>
                    )
                  })
              }
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {!loading && totalPages > 1 && (
          <div className="flex items-center justify-between gap-3 border-t border-slate-800/60 bg-slate-900/40 px-5 py-2.5">
            <span className="text-[10px] text-slate-500 tabular-nums">
              {(page * limit + 1).toLocaleString()}–{Math.min((page + 1) * limit, total).toLocaleString()} of <span className="font-semibold text-slate-300">{total.toLocaleString()}</span>
            </span>
            <div className="flex items-center gap-1.5">
              <button onClick={() => loadIncidents(searchTerm, page - 1, stateFilter, assignedToFilter)}
                disabled={page === 0}
                className="flex items-center gap-1 rounded-lg border border-slate-700/60 bg-slate-800/40 px-2.5 py-1 text-[10px] font-semibold text-slate-300 hover:border-slate-600 hover:bg-slate-700/50 disabled:opacity-30 disabled:cursor-not-allowed transition">
                <ChevronLeft size={11} /> Prev
              </button>
              <div className="rounded-lg bg-slate-800/60 px-3 py-1 text-[10px] font-bold tabular-nums text-slate-200">
                {page + 1} / {totalPages}
              </div>
              <button onClick={() => loadIncidents(searchTerm, page + 1, stateFilter, assignedToFilter)}
                disabled={page >= totalPages - 1}
                className="flex items-center gap-1 rounded-lg border border-slate-700/60 bg-slate-800/40 px-2.5 py-1 text-[10px] font-semibold text-slate-300 hover:border-slate-600 hover:bg-slate-700/50 disabled:opacity-30 disabled:cursor-not-allowed transition">
                Next <ChevronRight size={11} />
              </button>
            </div>
          </div>
        )}
      </div>
    </section>
  )
}
