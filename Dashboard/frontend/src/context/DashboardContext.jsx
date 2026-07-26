// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: Dashboard — frontend/src/context (DashboardContext.jsx)
// Date: 2025-11-15
// ---------------------------------------------------------------------------
import React, { createContext, useContext, useState, useCallback, useEffect } from 'react'
import { getStatus, getCriticalAlerts } from '../api'

const DashboardContext = createContext(null)

// Function: DashboardProvider
export function DashboardProvider({ children }) {
  const [connected, setConnected] = useState(false)
  const [synced, setSynced] = useState(false)
  const [lastSynced, setLastSynced] = useState(null)
  const [recordCounts, setRecordCounts] = useState({})
  const [syncing, setSyncing] = useState(false)
  const [connecting, setConnecting] = useState(false)
  const [statusLoading, setStatusLoading] = useState(true)
  const [instanceUrl, setInstanceUrl] = useState('')
  const [username, setUsername] = useState('')
  const [connectionExpiresAt, setConnectionExpiresAt] = useState(null)

  // Date range filter — shared across all dashboard pages
  const [dateRange, setDateRange] = useState({ startDate: null, endDate: null, preset: 'all' })

  // Critical alerts — shared so Navbar Invoke and ExecutiveCockpit stay in sync
  const [criticalAlerts, setCriticalAlerts] = useState([])
  const [alertsLoading, setAlertsLoading] = useState(false)

  const refreshStatus = useCallback(async () => {
    try {
      const res = await getStatus()
      const data = res.data
      setConnected(data.connected === true)
      setSynced(data.synced === true)
      setConnectionExpiresAt(data.connection_expires_at || null)
      if (data.last_synced) setLastSynced(data.last_synced)
      if (data.record_counts) setRecordCounts(data.record_counts)
      if (data.instance_url) setInstanceUrl(data.instance_url)
      if (data.username) setUsername(data.username)
    } catch {
      setConnected(false)
      setSynced(false)
      setConnectionExpiresAt(null)
    } finally {
      setStatusLoading(false)
    }
  }, [])

  const refreshCriticalAlerts = useCallback(async () => {
    setAlertsLoading(true)
    try {
      const res = await getCriticalAlerts()
      setCriticalAlerts(res.data || [])
    } catch {
      /* silent — keep last known alerts */
    } finally {
      setAlertsLoading(false)
    }
  }, [])

  useEffect(() => {
    refreshStatus()
    refreshCriticalAlerts()
  }, [refreshStatus, refreshCriticalAlerts])

  useEffect(() => {
    const id = setInterval(refreshStatus, 15000)
    return () => clearInterval(id)
  }, [refreshStatus])

  // Poll critical alerts every 30 s
  useEffect(() => {
    const id = setInterval(refreshCriticalAlerts, 30000)
    return () => clearInterval(id)
  }, [refreshCriticalAlerts])

  const value = {
    connected,
    setConnected,
    synced,
    setSynced,
    lastSynced,
    setLastSynced,
    recordCounts,
    setRecordCounts,
    syncing,
    setSyncing,
    connecting,
    setConnecting,
    statusLoading,
    instanceUrl,
    setInstanceUrl,
    username,
    setUsername,
    connectionExpiresAt,
    refreshStatus,
    // Date range
    dateRange,
    setDateRange,
    // Critical alerts
    criticalAlerts,
    setCriticalAlerts,
    alertsLoading,
    refreshCriticalAlerts,
  }

  return (
    <DashboardContext.Provider value={value}>
      {children}
    </DashboardContext.Provider>
  )
}

// Function: useDashboard
export function useDashboard() {
  const ctx = useContext(DashboardContext)
  if (!ctx) throw new Error('useDashboard must be used within DashboardProvider')
  return ctx
}

export default DashboardContext
