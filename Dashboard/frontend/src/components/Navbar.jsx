// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: Dashboard — frontend/src/components (Navbar.jsx)
// Date: 2026-01-02
// ---------------------------------------------------------------------------
import React, { useState } from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import {
  Activity,
  LayoutDashboard,
  Ticket,
  AlertTriangle,
  GitBranch,
  Cpu,
  Settings,
  RefreshCw,
  Clock,
  CheckCircle,
  XCircle,
  Zap,
  Target,
  Users,
  Inbox,
} from 'lucide-react'
import { syncData, invokeCriticalIncident } from '../api'
import { useDashboard } from '../context/DashboardContext'
import DateRangeFilter from './DateRangeFilter'

const navItems = [
  { label: 'Executive', path: '/dashboard', icon: LayoutDashboard, end: true },
  { label: 'Service Requests', path: '/dashboard/service-requests', icon: Ticket },
  { label: 'Incidents', path: '/dashboard/incidents', icon: AlertTriangle },
  { label: 'Changes', path: '/dashboard/changes', icon: GitBranch },
  { label: 'Automation', path: '/dashboard/automation', icon: Cpu },
  { label: 'SLA / KPIs', path: '/dashboard/sla-kpi', icon: Target },
  { label: 'Transformation', path: '/dashboard/transformation', icon: Zap },
  { label: 'Ad-hoc / Enhancements', path: '/dashboard/adhoc-enhancements', icon: Inbox },
  { label: 'People & Capacity', path: '/dashboard/people-capacity', icon: Users },
]

// Function: formatLastSynced
function formatLastSynced(ts) {
  if (!ts) return 'Never'
  try {
    const d = new Date(ts)
    const now = new Date()
    const diffMs = now - d
    const diffMins = Math.floor(diffMs / 60000)
    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins}m ago`
    const diffHrs = Math.floor(diffMins / 60)
    if (diffHrs < 24) return `${diffHrs}h ago`
    return d.toLocaleDateString()
  } catch {
    return ts
  }
}

// Function: Navbar
export default function Navbar() {
  const navigate = useNavigate()
  const {
    connected, synced, lastSynced, syncing, setSyncing, setSynced, setLastSynced,
    setRecordCounts, refreshStatus, refreshCriticalAlerts,
  } = useDashboard()
  const [syncError, setSyncError] = useState(false)
  const [invoking, setInvoking] = useState(false)
  const [invokeSuccess, setInvokeSuccess] = useState(false)

  // Function: handleSyncNow
  async function handleSyncNow() {
    if (!connected || syncing) return
    setSyncing(true)
    setSyncError(false)
    try {
      const res = await syncData()
      if (res.data?.record_counts) setRecordCounts(res.data.record_counts)
      setSynced(true)
      setLastSynced(new Date().toISOString())
      await refreshStatus()
      // Refresh alerts so the ticker stays current after a manual sync
      await refreshCriticalAlerts()
    } catch {
      setSyncError(true)
    } finally {
      setSyncing(false)
    }
  }

  // Function: handleInvoke
  async function handleInvoke() {
    if (invoking) return
    setInvoking(true)
    setInvokeSuccess(false)
    try {
      await invokeCriticalIncident()
      setInvokeSuccess(true)
      // Immediately refresh critical alerts — do NOT do a full sync
      // (a full sync would reload from SN, potentially overwriting the new incident
      //  before it propagates through ServiceNow's API)
      await refreshCriticalAlerts()
      setTimeout(() => setInvokeSuccess(false), 4000)
    } catch {
      // silent — the incident may still have been created
    } finally {
      setInvoking(false)
    }
  }

  return (
    <header className="sticky top-0 z-50 glass border-b border-slate-600/20 shadow-elevation-3">
      <div className="px-4 lg:px-6">
        <div className="flex items-center h-16 gap-4">

          {/* Brand */}
          <div className="flex items-center gap-2.5 shrink-0">
            <div className="p-2 rounded-lg gradient-bg-primary">
              <Activity className="w-5 h-5 text-white" />
            </div>
            <div className="hidden sm:block">
              <p className="text-sm font-bold text-white leading-tight">Digital Operations Cockpit</p>
              <p className="text-[10px] text-slate-400 leading-tight">AI-Powered ITSM Intelligence</p>
            </div>
          </div>
          <div className="w-px h-6 bg-slate-600/30 shrink-0 hidden sm:block" />

          {/* Nav tabs */}
          <nav className="flex items-center gap-0.5 flex-1 overflow-x-auto">
            {navItems.map(({ label, path, icon: Icon, end }) => (
              <NavLink
                key={path}
                to={path}
                end={end}
                className={({ isActive }) =>
                  `flex items-center gap-1.5 px-3 py-2 rounded-lg text-xs font-medium whitespace-nowrap transition-colors ${
                    isActive
                      ? 'bg-primary-500/20 text-accent-cyan border border-primary-500/30 font-semibold shadow-glow-sm'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-700/30'
                  }`
                }
              >
                <Icon className="w-3.5 h-3.5" />
                <span className="hidden md:inline">{label}</span>
              </NavLink>
            ))}
          </nav>

          {/* Right controls */}
          <div className="flex items-center gap-2.5 shrink-0">
            {/* Sync status */}
            <div className="hidden lg:flex items-center gap-1.5 text-xs text-slate-400 bg-slate-700/20 px-3 py-1.5 rounded-lg">
              {synced ? (
                <>
                  <CheckCircle className="w-3.5 h-3.5 text-accent-emerald" />
                  <span className="text-slate-400/80">
                    <Clock className="w-3 h-3 inline mr-1" />
                    {formatLastSynced(lastSynced)}
                  </span>
                </>
              ) : (
                <>
                  <XCircle className="w-3.5 h-3.5 text-accent-rose" />
                  <span>Not synced</span>
                </>
              )}
              {syncError && <span className="text-accent-rose ml-1">Sync failed</span>}
            </div>

            {/* Settings */}
            <button
              onClick={() => navigate('/connect')}
              className="p-2 rounded-lg text-slate-400 hover:text-slate-300 hover:bg-slate-700/30 transition-colors"
              title="Connection Settings"
            >
              <Settings className="w-4 h-4" />
            </button>

            {/* Invoke critical incident */}
            <button
              onClick={handleInvoke}
              disabled={invoking}
              title="Invoke a high-critical incident into ServiceNow"
              className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg border transition-all disabled:opacity-50 disabled:cursor-not-allowed ${
                invokeSuccess
                  ? 'gradient-bg-success text-white border-accent-emerald/50 shadow-glow-sm'
                  : 'gradient-bg-danger text-white border-accent-rose/50 shadow-glow-md hover:shadow-glow-lg'
              }`}
            >
              <Zap className={`w-3.5 h-3.5 ${invoking ? 'animate-pulse' : ''}`} />
              <span className="hidden sm:inline">
                {invoking ? 'Invoking…' : invokeSuccess ? 'Invoked!' : 'Invoke'}
              </span>
            </button>

            {/* Sync Now */}
            <button
              onClick={handleSyncNow}
              disabled={!connected || syncing}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-700/30 hover:bg-slate-700/50 disabled:opacity-40 disabled:cursor-not-allowed text-slate-200 hover:text-white text-xs font-medium rounded-lg border border-slate-600/30 transition-all hover:shadow-elevation-1"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${syncing ? 'animate-spin' : ''}`} />
              <span className="hidden sm:inline">{syncing ? 'Syncing...' : 'Sync Now'}</span>
            </button>
          </div>
        </div>

        {/* ── Date Range Filter bar ── */}
        <div className="flex items-center gap-3 py-1.5 border-t border-slate-600/20">
          <span className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider shrink-0 hidden sm:block">Filter Period</span>
          <DateRangeFilter />
        </div>
      </div>
    </header>
  )
}
