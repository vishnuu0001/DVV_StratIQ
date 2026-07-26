// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: Novastra-ITSM — frontend/src/pages (DashboardPage.jsx)
// Date: 2026-06-14
// ---------------------------------------------------------------------------
import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Search, RefreshCw, MessageSquare, Calendar, Tag, AlertCircle, CheckCircle, Clock, XCircle, Edit2, Save, X as XIcon, Filter } from 'lucide-react'
import { getDashboardIncidents, getDashboardStats, getDashboardFilterOptions, updateDashboardIncident } from '../services/api.js'
import { toast } from 'react-hot-toast'

// Function: DashboardPage
export default function DashboardPage() {
  const navigate = useNavigate()
  const [incidents, setIncidents] = useState([])
  const [stats, setStats] = useState(null)
  const [filterOptions, setFilterOptions] = useState({ states: [], assigned_to: [] })
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [stateFilter, setStateFilter] = useState('')
  const [assignedToFilter, setAssignedToFilter] = useState('')
  const [page, setPage] = useState(0)
  const [total, setTotal] = useState(0)
  const [limit] = useState(50)
  const [refreshing, setRefreshing] = useState(false)
  const [editingRow, setEditingRow] = useState(null)
  const [editValues, setEditValues] = useState({})
  const [saving, setSaving] = useState(false)

  // Function: loadIncidents
  const loadIncidents = async (searchText = '', pageNum = 0, state = '', assignedTo = '') => {
    try {
      setLoading(true)
      const params = {
        limit,
        offset: pageNum * limit,
      }
      if (searchText) params.search = searchText
      if (state) params.state = state
      if (assignedTo) params.assigned_to = assignedTo
      
      const { data } = await getDashboardIncidents(params)
      setIncidents(data.incidents || [])
      setTotal(data.total || 0)
      setPage(pageNum)
    } catch (error) {
      console.error('Failed to load incidents:', error)
      toast.error('Failed to load incidents')
    } finally {
      setLoading(false)
    }
  }

  // Function: loadStats
  const loadStats = async () => {
    try {
      const { data } = await getDashboardStats()
      setStats(data)
    } catch (error) {
      console.error('Failed to load stats:', error)
    }
  }

  // Function: loadFilterOptions
  const loadFilterOptions = async () => {
    try {
      const { data } = await getDashboardFilterOptions()
      setFilterOptions(data)
    } catch (error) {
      console.error('Failed to load filter options:', error)
    }
  }

  useEffect(() => {
    loadIncidents()
    loadStats()
    loadFilterOptions()
  }, [])

  // Function: handleSearch
  const handleSearch = (e) => {
    e.preventDefault()
    loadIncidents(searchTerm, 0, stateFilter, assignedToFilter)
  }

  // Function: handleFilterChange
  const handleFilterChange = () => {
    loadIncidents(searchTerm, 0, stateFilter, assignedToFilter)
  }

  // Function: handleRefresh
  const handleRefresh = async () => {
    setRefreshing(true)
    await Promise.all([
      loadIncidents(searchTerm, page, stateFilter, assignedToFilter),
      loadStats(),
      loadFilterOptions()
    ])
    setRefreshing(false)
    toast.success('Dashboard refreshed')
  }

  // Function: handleSelectIncident
  const handleSelectIncident = (incident) => {
    const chatMessage = `Ask about synced incidents: ${incident.number}\n\nIncident Number: ${incident.number}\nShort Description: ${incident.short_description}\nDescription: ${incident.description}\nCategory: ${incident.category || 'N/A'}\nState: ${incident.state || 'N/A'}\nPriority: ${incident.priority || 'N/A'}\nAssigned To: ${incident.assigned_to || 'N/A'}`
    
    navigate('/ticket-analysis', {
      state: {
        preloadedMessage: chatMessage,
        incidentNumber: incident.number,
      },
    })
  }

  // Function: handleEdit
  const handleEdit = (incident) => {
    setEditingRow(incident.incident_id)
    setEditValues({
      assigned_to: incident.assigned_to || '',
      state: incident.state || '',
      close_notes: incident.close_notes || ''
    })
  }

  // Function: handleCancelEdit
  const handleCancelEdit = () => {
    setEditingRow(null)
    setEditValues({})
  }

  // Function: handleSaveEdit
  const handleSaveEdit = async (incidentNumber) => {
    try {
      setSaving(true)
      const updateData = {
        incident_number: incidentNumber,
        assigned_to: editValues.assigned_to,
        state: editValues.state,
        close_notes: editValues.close_notes,
        sync_to_servicenow: true
      }
      
      const { data } = await updateDashboardIncident(incidentNumber, updateData)
      
      if (data.success) {
        toast.success(data.servicenow_synced 
          ? 'Updated and synced to ServiceNow!' 
          : 'Updated locally!')
        
        // Refresh incidents
        await loadIncidents(searchTerm, page, stateFilter, assignedToFilter)
        setEditingRow(null)
        setEditValues({})
      } else {
        toast.error('Update failed')
      }
    } catch (error) {
      console.error('Failed to update incident:', error)
      toast.error('Failed to update incident')
    } finally {
      setSaving(false)
    }
  }

  // Exact-match against the dashboard's fixed 5-value taxonomy (see backend
  // operational_ingestion.CANONICAL_STATES) — substring matching previously mis-colored
  // "Re-Opened" the same as "Open" since the former contains the latter as a substring.
  const STATE_STYLES = {
    'Open': { color: 'text-yellow-400', icon: AlertCircle },
    'In-Progress': { color: 'text-blue-400', icon: Clock },
    'Pending Clarifications': { color: 'text-orange-400', icon: Clock },
    'Closed': { color: 'text-green-400', icon: CheckCircle },
    'Re-Opened': { color: 'text-purple-400', icon: AlertCircle },
  }

  // Function: getStateColor
  const getStateColor = (state) => (STATE_STYLES[state] || { color: 'text-gray-400' }).color

  // Function: getStateIcon
  const getStateIcon = (state) => {
    const Icon = (STATE_STYLES[state] || { icon: XCircle }).icon
    return <Icon className="w-4 h-4" />
  }

  const totalPages = Math.ceil(total / limit)

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 text-white">
      <div className="max-w-[1600px] mx-auto p-6 space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-sm font-bold bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">
              Incident Dashboard
            </h1>
            <p className="text-[10px] text-gray-400 mt-1">
              View and analyze all synced ServiceNow tickets
            </p>
          </div>
          <button
            onClick={handleRefresh}
            disabled={refreshing}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>

        {/* Stats Cards */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-lg p-4">
              <div className="text-gray-400 text-xs">Total Incidents</div>
              <div className="text-2xl font-bold text-cyan-400 mt-1">
                {stats.total_incidents?.toLocaleString() || 0}
              </div>
            </div>

            {stats.by_state && stats.by_state.length > 0 && (
              <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-lg p-4">
                <div className="text-gray-400 text-xs flex items-center gap-2">
                  <CheckCircle className="w-4 h-4 text-green-400" />
                  {stats.by_state[0]?.state || 'N/A'}
                </div>
                <div className="text-2xl font-bold text-green-400 mt-1">
                  {stats.by_state[0]?.count?.toLocaleString() || 0}
                </div>
              </div>
            )}

            {stats.by_category && stats.by_category.length > 0 && (
              <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-lg p-4">
                <div className="text-gray-400 text-xs">Top Category</div>
                <div className="text-xs font-semibold text-blue-400 mt-1 truncate">
                  {stats.by_category[0]?.category || 'N/A'}
                </div>
                <div className="text-xs text-gray-400 mt-1">
                  {stats.by_category[0]?.count?.toLocaleString() || 0} incidents
                </div>
              </div>
            )}

            {stats.by_source && stats.by_source.length > 0 && (
              <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-lg p-4">
                <div className="text-gray-400 text-xs">Latest Sync</div>
                <div className="text-xs font-semibold text-purple-400 mt-1 truncate">
                  {stats.by_source[0]?.source?.split('_')[2] || 'N/A'}
                </div>
                <div className="text-xs text-gray-400 mt-1">
                  {stats.by_source[0]?.count?.toLocaleString() || 0} tickets
                </div>
              </div>
            )}
          </div>
        )}

        {/* Search and Filters */}
        <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-lg p-4 space-y-3">
          <form onSubmit={handleSearch} className="flex gap-2">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search by incident number, description, category, state, assigned to, or resolution..."
                className="w-full pl-10 pr-4 py-3 bg-slate-900/50 border border-slate-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500 text-white placeholder-gray-400"
              />
            </div>
            <button
              type="submit"
              className="px-6 py-3 bg-cyan-600 hover:bg-cyan-700 rounded-lg transition-colors font-semibold"
            >
              Search
            </button>
          </form>

          <div className="flex gap-3 items-center">
            <Filter className="w-5 h-5 text-gray-400" />
            <select
              value={stateFilter}
              onChange={(e) => {
                setStateFilter(e.target.value)
                setTimeout(() => handleFilterChange(), 0)
              }}
              className="px-4 py-2 bg-slate-900/50 border border-slate-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500 text-white"
            >
              <option value="">All States</option>
              {filterOptions.states.map(state => (
                <option key={state} value={state}>{state}</option>
              ))}
            </select>

            <select
              value={assignedToFilter}
              onChange={(e) => {
                setAssignedToFilter(e.target.value)
                setTimeout(() => handleFilterChange(), 0)
              }}
              className="px-4 py-2 bg-slate-900/50 border border-slate-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500 text-white"
            >
              <option value="">All Assignees</option>
              {filterOptions.assigned_to.map(assignee => (
                <option key={assignee} value={assignee}>{assignee || '(Unassigned)'}</option>
              ))}
            </select>

            {(stateFilter || assignedToFilter) && (
              <button
                onClick={() => {
                  setStateFilter('')
                  setAssignedToFilter('')
                  loadIncidents(searchTerm, 0, '', '')
                }}
                className="px-3 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg transition-colors text-sm"
              >
                Clear Filters
              </button>
            )}
          </div>
        </div>

        {/* Incidents Table */}
        <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-lg overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-slate-900/50 border-b border-slate-700">
                <tr>
                  <th className="text-left p-4 text-gray-400 font-semibold">Incident</th>
                  <th className="text-left p-4 text-gray-400 font-semibold">Description</th>
                  <th className="text-left p-4 text-gray-400 font-semibold">Assigned To</th>
                  <th className="text-left p-4 text-gray-400 font-semibold">State</th>
                  <th className="text-left p-4 text-gray-400 font-semibold">Resolution</th>
                  <th className="text-left p-4 text-gray-400 font-semibold">Priority</th>
                  <th className="text-left p-4 text-gray-400 font-semibold">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-700">
                {loading ? (
                  <tr>
                    <td colSpan="7" className="p-8 text-center text-gray-400">
                      <div className="flex items-center justify-center gap-2">
                        <RefreshCw className="w-5 h-5 animate-spin" />
                        Loading incidents...
                      </div>
                    </td>
                  </tr>
                ) : incidents.length === 0 ? (
                  <tr>
                    <td colSpan="7" className="p-8 text-center text-gray-400">
                      No incidents found. Try running "One-time Sync Tickets" first.
                    </td>
                  </tr>
                ) : (
                  incidents.map((incident) => {
                    const isEditing = editingRow === incident.incident_id
                    
                    return (
                      <tr
                        key={incident.incident_id}
                        className={`hover:bg-slate-700/30 transition-colors ${isEditing ? 'bg-slate-700/50' : ''}`}
                      >
                        <td className="p-4">
                          <div className="font-mono text-cyan-400 font-semibold">
                            {incident.number}
                          </div>
                          <div className="text-xs text-gray-500 mt-1 flex items-center gap-1">
                            <Calendar className="w-3 h-3" />
                            {incident.opened_at || 'N/A'}
                          </div>
                        </td>
                        <td className="p-4 max-w-md">
                          <div className="text-white font-medium truncate">
                            {incident.short_description || 'No description'}
                          </div>
                          <div className="text-sm text-gray-400 truncate mt-1">
                            {incident.description?.substring(0, 100) || ''}
                          </div>
                        </td>
                        <td className="p-4">
                          {isEditing ? (
                            <input
                              type="text"
                              value={editValues.assigned_to}
                              onChange={(e) => setEditValues({ ...editValues, assigned_to: e.target.value })}
                              className="w-full px-2 py-1 bg-slate-900 border border-slate-600 rounded text-sm focus:outline-none focus:ring-2 focus:ring-cyan-500"
                              placeholder="Assignee"
                            />
                          ) : (
                            <span className="text-sm text-purple-300">
                              {incident.assigned_to || '(Unassigned)'}
                            </span>
                          )}
                        </td>
                        <td className="p-4">
                          {isEditing ? (
                            <select
                              value={editValues.state}
                              onChange={(e) => setEditValues({ ...editValues, state: e.target.value })}
                              className="w-full px-2 py-1 bg-slate-900 border border-slate-600 rounded text-sm focus:outline-none focus:ring-2 focus:ring-cyan-500"
                            >
                              <option value="">Select State</option>
                              {filterOptions.states.map(state => (
                                <option key={state} value={state}>{state}</option>
                              ))}
                            </select>
                          ) : (
                            <div className={`flex items-center gap-2 ${getStateColor(incident.state)}`}>
                              {getStateIcon(incident.state)}
                              <span className="font-medium">
                                {incident.state || 'N/A'}
                              </span>
                            </div>
                          )}
                        </td>
                        <td className="p-4 max-w-xs">
                          {isEditing ? (
                            <textarea
                              value={editValues.close_notes}
                              onChange={(e) => setEditValues({ ...editValues, close_notes: e.target.value })}
                              rows={2}
                              className="w-full px-2 py-1 bg-slate-900 border border-slate-600 rounded text-sm focus:outline-none focus:ring-2 focus:ring-cyan-500"
                              placeholder="Resolution notes..."
                            />
                          ) : (
                            <div className="text-sm text-gray-300 truncate">
                              {incident.close_notes || '(No resolution)'}
                            </div>
                          )}
                        </td>
                        <td className="p-4">
                          <span className="px-2 py-1 bg-orange-500/20 text-orange-300 rounded text-sm font-semibold">
                            {incident.priority || 'N/A'}
                          </span>
                        </td>
                        <td className="p-4">
                          <div className="flex items-center gap-2">
                            {isEditing ? (
                              <>
                                <button
                                  onClick={() => handleSaveEdit(incident.number)}
                                  disabled={saving}
                                  className="flex items-center gap-1 px-3 py-1.5 bg-green-600 hover:bg-green-700 rounded-lg transition-colors text-sm font-semibold disabled:opacity-50"
                                >
                                  <Save className="w-4 h-4" />
                                  Save
                                </button>
                                <button
                                  onClick={handleCancelEdit}
                                  disabled={saving}
                                  className="flex items-center gap-1 px-3 py-1.5 bg-gray-600 hover:bg-gray-700 rounded-lg transition-colors text-sm font-semibold"
                                >
                                  <XIcon className="w-4 h-4" />
                                  Cancel
                                </button>
                              </>
                            ) : (
                              <>
                                <button
                                  onClick={() => handleEdit(incident)}
                                  className="flex items-center gap-1 px-3 py-1.5 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors text-sm font-semibold"
                                >
                                  <Edit2 className="w-4 h-4" />
                                  Edit
                                </button>
                                <button
                                  onClick={() => handleSelectIncident(incident)}
                                  className="flex items-center gap-1 px-3 py-1.5 bg-cyan-600 hover:bg-cyan-700 rounded-lg transition-colors text-sm font-semibold"
                                >
                                  <MessageSquare className="w-4 h-4" />
                                  Chat
                                </button>
                              </>
                            )}
                          </div>
                        </td>
                      </tr>
                    )
                  })
                )}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          {!loading && totalPages > 1 && (
            <div className="flex items-center justify-between p-4 border-t border-slate-700">
              <div className="text-sm text-gray-400">
                Showing {page * limit + 1}-{Math.min((page + 1) * limit, total)} of {total} incidents
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => loadIncidents(searchTerm, page - 1, stateFilter, assignedToFilter)}
                  disabled={page === 0}
                  className="px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Previous
                </button>
                <div className="text-sm text-gray-400">
                  Page {page + 1} of {totalPages}
                </div>
                <button
                  onClick={() => loadIncidents(searchTerm, page + 1, stateFilter, assignedToFilter)}
                  disabled={page >= totalPages - 1}
                  className="px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Next
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
