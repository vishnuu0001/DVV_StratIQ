// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: Dashboard — frontend/src/components (ConnectionPanel.jsx)
// Date: 2025-10-29
// ---------------------------------------------------------------------------
import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Server,
  Link,
  Unlink,
  RefreshCw,
  Database,
  CheckCircle,
  XCircle,
  AlertCircle,
  ArrowRight,
  Eye,
  EyeOff,
  Activity,
} from 'lucide-react'
import { connect, syncData, disconnect, getConfig } from '../api'
import { useDashboard } from '../context/DashboardContext'

// Function: TopBar
function TopBar({ statusColor, statusBg, statusText, StatusIcon }) {
  return (
    <div className="border-b border-navy-700 bg-navy-800/80 backdrop-blur px-6 py-4">
      <div className="max-w-5xl mx-auto flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-cyan-500/10 border border-cyan-500/20">
            <Activity className="w-5 h-5 text-accent-cyan" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-white leading-tight">Digital Operations Cockpit</h1>
            <p className="text-xs text-slate-400">AI-Powered ITSM Intelligence</p>
          </div>
        </div>
        <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full border text-sm font-medium ${statusBg} ${statusColor}`}>
          <StatusIcon className="w-4 h-4" />
          {statusText}
        </div>
      </div>
    </div>
  )
}

// Function: HeaderCard
function HeaderCard({ connected, connectionExpiresAt }) {
  return (
    <div className="rounded-xl border border-navy-700 bg-navy-800 p-6">
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="p-3 rounded-xl bg-indigo-500/10 border border-indigo-500/20">
            <Server className="w-6 h-6 text-accent-indigo" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-white">ServiceNow / JIRA Connection</h2>
            <p className="text-slate-400 text-sm mt-0.5">
              Connection retained for 5 minutes unless disconnected
              {connected && connectionExpiresAt
                ? ` — expires ${new Date(connectionExpiresAt).toLocaleTimeString()}`
                : ''}
            </p>
          </div>
        </div>
        <div className="text-right text-xs text-slate-400 max-w-xs leading-relaxed bg-navy-700/50 rounded-lg px-3 py-2 border border-navy-600">
          <AlertCircle className="w-3.5 h-3.5 inline mr-1 text-accent-amber" />
          Sync is optional while vector DB is fresh (&lt;12h). Older than 12h requires a fresh sync.
        </div>
      </div>
    </div>
  )
}

// Function: ConnectionForm
function ConnectionForm({
  provider, setProvider, authType, setAuthType, url, setUrl, user, setUser,
  password, setPassword, showPassword, setShowPassword,
  connecting, syncing, connected, handleConnect, handleDisconnect,
}) {
  let connectButtonLabel = 'Connect'
  if (connecting) connectButtonLabel = 'Connecting...'
  else if (syncing) connectButtonLabel = 'Loading data...'

  return (
    <div className="rounded-xl border border-navy-700 bg-navy-800 p-6 space-y-5">
      <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-2">
        <Link className="w-4 h-4 text-accent-cyan" />
        Connection Settings
      </h3>

      <div className="grid grid-cols-3 gap-4">
        <div className="space-y-1.5">
          <label htmlFor="conn-provider" className="text-xs font-medium text-slate-400 uppercase tracking-wide">Provider</label>
          <select
            id="conn-provider"
            value={provider}
            onChange={(e) => setProvider(e.target.value)}
            className="w-full bg-navy-900 border border-navy-600 rounded-lg px-3 py-2.5 text-sm text-white focus:outline-none focus:border-accent-cyan focus:ring-1 focus:ring-accent-cyan/30 cursor-pointer"
          >
            <option value="ServiceNow">ServiceNow</option>
            <option value="JIRA">JIRA</option>
          </select>
        </div>

        <div className="space-y-1.5">
          <label htmlFor="conn-auth-type" className="text-xs font-medium text-slate-400 uppercase tracking-wide">Auth Type</label>
          <select
            id="conn-auth-type"
            value={authType}
            onChange={(e) => setAuthType(e.target.value)}
            className="w-full bg-navy-900 border border-navy-600 rounded-lg px-3 py-2.5 text-sm text-white focus:outline-none focus:border-accent-cyan focus:ring-1 focus:ring-accent-cyan/30 cursor-pointer"
          >
            <option value="basic">Basic (username + password/token)</option>
            <option value="oauth2">OAuth2</option>
          </select>
        </div>

        <div className="space-y-1.5">
          <label htmlFor="conn-instance-url" className="text-xs font-medium text-slate-400 uppercase tracking-wide">Instance Base URL</label>
          <input
            id="conn-instance-url"
            type="text"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://your-instance.service-now.com"
            className="w-full bg-navy-900 border border-navy-600 rounded-lg px-3 py-2.5 text-sm text-white placeholder-slate-600 focus:outline-none focus:border-accent-cyan focus:ring-1 focus:ring-accent-cyan/30"
          />
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-1.5">
          <label className="text-xs font-medium text-slate-400 uppercase tracking-wide">
            {provider === 'JIRA' ? 'Email' : 'Username'}
          </label>
          <input
            type="text"
            value={user}
            onChange={(e) => setUser(e.target.value)}
            placeholder={provider === 'JIRA' ? 'you@company.com' : 'admin'}
            className="w-full bg-navy-900 border border-navy-600 rounded-lg px-3 py-2.5 text-sm text-white placeholder-slate-600 focus:outline-none focus:border-accent-cyan focus:ring-1 focus:ring-accent-cyan/30"
          />
        </div>

        <div className="space-y-1.5">
          <label className="text-xs font-medium text-slate-400 uppercase tracking-wide">
            {authType === 'basic' ? 'Password / API Token' : 'OAuth2 Token'}
          </label>
          <div className="relative">
            <input
              type={showPassword ? 'text' : 'password'}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className="w-full bg-navy-900 border border-navy-600 rounded-lg px-3 py-2.5 pr-10 text-sm text-white placeholder-slate-600 focus:outline-none focus:border-accent-cyan focus:ring-1 focus:ring-accent-cyan/30"
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300 transition-colors"
            >
              {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
            </button>
          </div>
        </div>
      </div>

      <div className="flex items-center justify-end gap-3 pt-2 border-t border-navy-700">
        <button
          onClick={handleConnect}
          disabled={connecting || syncing}
          className="flex items-center gap-2 px-4 py-2.5 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 disabled:cursor-not-allowed text-white text-sm font-medium rounded-lg transition-colors"
        >
          {(connecting || syncing) ? (
            <RefreshCw className="w-4 h-4 animate-spin" />
          ) : (
            <Link className="w-4 h-4" />
          )}
          {connectButtonLabel}
        </button>

        <button
          onClick={handleDisconnect}
          disabled={!connected}
          className="flex items-center gap-2 px-4 py-2.5 bg-transparent hover:bg-rose-900/30 border border-rose-700/60 hover:border-rose-600 disabled:opacity-30 disabled:cursor-not-allowed text-rose-400 hover:text-rose-300 text-sm font-medium rounded-lg transition-colors"
        >
          <Unlink className="w-4 h-4" />
          Disconnect
        </button>
      </div>
    </div>
  )
}

// Function: StatusAlerts
function StatusAlerts({ syncing, syncProgress, error, success }) {
  return (
    <>
      {syncing && syncProgress && (
        <div className="rounded-xl border border-blue-700/50 bg-blue-900/20 px-5 py-3 flex items-center gap-3">
          <RefreshCw className="w-4 h-4 text-accent-cyan animate-spin shrink-0" />
          <p className="text-sm text-blue-300">{syncProgress}</p>
        </div>
      )}

      {error && (
        <div className="rounded-xl border border-rose-700/50 bg-rose-900/20 px-5 py-3 flex items-center gap-3">
          <XCircle className="w-4 h-4 text-accent-rose shrink-0" />
          <p className="text-sm text-rose-300">{error}</p>
        </div>
      )}

      {success && (
        <div className="rounded-xl border border-emerald-700/50 bg-emerald-900/20 px-5 py-3 flex items-center gap-3">
          <CheckCircle className="w-4 h-4 text-accent-emerald shrink-0" />
          <p className="text-sm text-emerald-300">{success}</p>
        </div>
      )}
    </>
  )
}

// Function: RecordCountsPanel
function RecordCountsPanel({ recordEntries }) {
  if (recordEntries.length === 0) return null
  return (
    <div className="rounded-xl border border-navy-700 bg-navy-800 p-5">
      <h3 className="text-sm font-semibold text-slate-300 mb-4 flex items-center gap-2">
        <Database className="w-4 h-4 text-accent-indigo" />
        Synced Records
      </h3>
      <div className="grid grid-cols-3 gap-3">
        {recordEntries.map(([key, val]) => (
          <div
            key={key}
            className="bg-navy-900/80 rounded-lg border border-navy-600 px-4 py-3 text-center"
          >
            <p className="text-2xl font-bold text-white">{typeof val === 'number' ? val.toLocaleString() : val}</p>
            <p className="text-xs text-slate-400 mt-0.5 capitalize">{key.replaceAll('_', ' ')}</p>
          </div>
        ))}
      </div>
    </div>
  )
}

// Function: DashboardCTA
function DashboardCTA({ connected, synced, handleGoToDashboard }) {
  if (!(connected && synced)) return null
  return (
    <div className="rounded-xl border border-cyan-700/40 bg-cyan-900/15 p-5 flex items-center justify-between">
      <div>
        <p className="text-white font-semibold">Ready to explore your data</p>
        <p className="text-slate-400 text-sm mt-0.5">All tickets synced. Open the dashboard to see insights.</p>
      </div>
      <button
        onClick={handleGoToDashboard}
        className="flex items-center gap-2 px-5 py-2.5 bg-accent-cyan text-navy-950 font-semibold text-sm rounded-lg hover:bg-cyan-300 transition-colors"
      >
        Go to Dashboard
        <ArrowRight className="w-4 h-4" />
      </button>
    </div>
  )
}

// Function: ConnectionPanel
export default function ConnectionPanel() {
  const navigate = useNavigate()
  const {
    connected,
    setConnected,
    synced,
    setSynced,
    setLastSynced,
    recordCounts,
    setRecordCounts,
    syncing,
    setSyncing,
    connecting,
    setConnecting,
    instanceUrl,
    username,
    connectionExpiresAt,
    refreshStatus,
  } = useDashboard()

  const [provider, setProvider] = useState('ServiceNow')
  const [authType, setAuthType] = useState('basic')
  const [url, setUrl] = useState('')
  const [user, setUser] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [syncProgress, setSyncProgress] = useState('')

  useEffect(() => {
    getConfig()
      .then((res) => {
        const { url: cfgUrl, username: cfgUser, password: cfgPwd } = res.data
        if (cfgUrl) setUrl(cfgUrl)
        if (cfgUser) setUser(cfgUser)
        if (cfgPwd) setPassword(cfgPwd)
      })
      .catch(() => {})
  }, [])

  useEffect(() => {
    if (instanceUrl) setUrl(instanceUrl)
    if (username) setUser(username)
  }, [instanceUrl, username])

  const statusColor = connected ? 'text-accent-emerald' : 'text-accent-rose'
  const statusBg = connected ? 'bg-emerald-900/30 border-emerald-700/50' : 'bg-rose-900/30 border-rose-700/50'
  const statusText = connected ? 'Connected' : 'Disconnected'
  const StatusIcon = connected ? CheckCircle : XCircle

  // Function: handleConnect
  async function handleConnect() {
    if (!url.trim() || !user.trim() || !password.trim()) {
      setError('Please fill in Instance URL, Username, and Password.')
      return
    }
    setError('')
    setSuccess('')
    setConnecting(true)
    try {
      await connect({ url: url.trim(), username: user.trim(), password, verify_ssl: false })
      await refreshStatus()
      // Auto-sync immediately after connecting so dashboard data is ready
      setSyncing(true)
      setSyncProgress('Connected — loading data from ServiceNow...')
      try {
        const res = await syncData({ url: url.trim(), username: user.trim(), password, verify_ssl: false })
        const data = res.data
        if (data.record_counts) setRecordCounts(data.record_counts)
        setSynced(true)
        setLastSynced(new Date().toISOString())
        await refreshStatus()
        navigate('/dashboard')
      } catch (syncErr) {
        setError(syncErr.response?.data?.detail || syncErr.message || 'Sync failed after connect.')
      } finally {
        setSyncProgress('')
        setSyncing(false)
      }
    } catch (e) {
      setError(e.response?.data?.detail || e.message || 'Connection failed.')
    } finally {
      setConnecting(false)
    }
  }

  // Function: handleDisconnect
  async function handleDisconnect() {
    setError('')
    setSuccess('')
    try {
      await disconnect()
      setConnected(false)
      setSynced(false)
      setRecordCounts({})
      setSuccess('Disconnected.')
      await refreshStatus()
    } catch (e) {
      setError(e.response?.data?.detail || e.message || 'Disconnect failed.')
    }
  }

  // Function: handleGoToDashboard
  function handleGoToDashboard() {
    navigate('/dashboard')
  }

  const recordEntries = Object.entries(recordCounts)

  return (
    <div className="min-h-screen bg-navy-950 flex flex-col">
      <TopBar statusColor={statusColor} statusBg={statusBg} statusText={statusText} StatusIcon={StatusIcon} />

      <div className="flex-1 flex items-start justify-center px-4 py-10">
        <div className="w-full max-w-3xl space-y-6">
          <HeaderCard connected={connected} connectionExpiresAt={connectionExpiresAt} />

          <ConnectionForm
            provider={provider}
            setProvider={setProvider}
            authType={authType}
            setAuthType={setAuthType}
            url={url}
            setUrl={setUrl}
            user={user}
            setUser={setUser}
            password={password}
            setPassword={setPassword}
            showPassword={showPassword}
            setShowPassword={setShowPassword}
            connecting={connecting}
            syncing={syncing}
            connected={connected}
            handleConnect={handleConnect}
            handleDisconnect={handleDisconnect}
          />

          <StatusAlerts syncing={syncing} syncProgress={syncProgress} error={error} success={success} />

          <RecordCountsPanel recordEntries={recordEntries} />

          <DashboardCTA connected={connected} synced={synced} handleGoToDashboard={handleGoToDashboard} />
        </div>
      </div>
    </div>
  )
}
