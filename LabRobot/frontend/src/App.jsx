// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: LabRobot — frontend/src (App.jsx)
// Date: 2025-12-02
// ---------------------------------------------------------------------------
import { useState, useCallback } from 'react'
import ScientistPanel from './components/ScientistPanel'
import LabAssistantPanel from './components/LabAssistantPanel'
import RackViewer3D from './components/RackViewer3D'
import FactoryOrchestration3D from './components/FactoryOrchestration3D'
import { resetAllPlacements } from './api'

const MODULE_TABS = [
  {
    key: 'scientist',
    label: 'Scientist View',
    icon: 'M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z',
  },
  {
    key: 'assistant',
    label: 'Lab Assistant',
    icon: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2',
  },
  {
    key: '3dview',
    label: '3D Rack View',
    icon: 'M21 7.5l-9-5.25L3 7.5m18 0l-9 5.25m9-5.25v9l-9 5.25M3 7.5l9 5.25M3 7.5v9l9 5.25m0-9v9',
  },
  {
    key: 'orchestration',
    label: 'Factory Orchestration',
    icon: 'M13 10V3L4 14h7v7l9-11h-7z',
  },
]

// Function: App
export default function App() {
  const [activeTab, setActiveTab] = useState('scientist')
  const [scenario, setScenario] = useState('warehouse')
  const [resetting, setResetting] = useState(false)
  const [resetKey, setResetKey] = useState(0)   // bump to force child re-mounts
  const [pendingCommand, setPendingCommand] = useState(null)

  const portalBaseUrl = ''

  const handleDispatchToViewer = useCallback((payload) => {
    setActiveTab('3dview')
    setPendingCommand({ commandId: `dispatch-${Date.now()}`, ...payload })
  }, [])

  const handleReset = useCallback(async () => {
    if (!window.confirm('Delete ALL placement data? This cannot be undone.')) return
    setResetting(true)
    try {
      await resetAllPlacements()
      setResetKey((k) => k + 1)   // remount panels so they re-fetch
    } catch (e) {
      alert('Reset failed: ' + (e?.response?.data?.detail ?? e.message))
    } finally {
      setResetting(false)
    }
  }, [])

  return (
    <div className="min-h-screen bg-slate-100">
      {/* Portal top menu */}
      <div className="bg-sky-300/85 text-white border-b border-sky-200/80 sticky top-0 z-40 backdrop-blur-sm">
        <div className="w-full px-6 py-2.5 flex items-center justify-between gap-3">
          <div>
            <p className="text-[11px] uppercase tracking-[0.2em] text-white">Unified Modernization Suite</p>
            <p className="text-sm font-semibold text-slate-100">Lab Robot Workspace</p>
          </div>
          <div className="flex items-center gap-2">
            <a
              href={`${portalBaseUrl}/launch-modules`}
              className="px-3 py-1.5 rounded-lg text-sm font-medium border border-white/45 bg-sky-400/35 text-white hover:bg-sky-400/55 transition-colors"
            >
              Portal Home
            </a>
            <a
              href={`${portalBaseUrl}/admin`}
              className="px-3 py-1.5 rounded-lg text-sm font-medium border border-white/45 bg-sky-400/35 text-white hover:bg-sky-400/55 transition-colors"
            >
              Admin Console
            </a>
            <a
              href={`${portalBaseUrl}/login`}
              className="px-3 py-1.5 rounded-lg text-sm font-semibold border border-white/45 bg-sky-400/35 text-white hover:bg-sky-400/55 transition-colors"
            >
              Logout
            </a>
          </div>
        </div>
      </div>

      {/* Header */}
      <header className="bg-blue-900 text-white shadow-lg">
        <div className="w-full px-6 py-4 flex items-center gap-4">
          <div className="w-10 h-10 bg-blue-700 rounded-lg flex items-center justify-center">
            <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
            </svg>
          </div>
          <div className="flex items-center justify-between w-full">
            <div>
              <h1 className="text-xl font-bold tracking-tight">Lab Robot Management System</h1>
              <p className="text-blue-300 text-xs">Production · Quality · Intralogistics · Real-time Simulation</p>
            </div>
            <div className="flex items-center gap-3">
              {activeTab === '3dview' && (
                <select
                  value={scenario}
                  onChange={(e) => setScenario(e.target.value)}
                  className="px-3 py-2 rounded-lg text-sm font-medium bg-blue-800 border border-blue-700 text-white hover:bg-blue-700 transition-colors"
                >
                  <option value="mixed">Full Factory</option>
                  <option value="production">Production & Assembly</option>
                  <option value="warehouse">Warehouse & Intralogistics</option>
                  <option value="quality">Quality & Inspection</option>
                </select>
              )}
              <button
                onClick={handleReset}
                disabled={resetting}
                className="flex items-center gap-2 bg-red-600 hover:bg-red-700 disabled:opacity-50 text-white text-sm font-semibold px-4 py-2 rounded-lg transition-colors"
              >
                {resetting ? (
                  <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
                  </svg>
                ) : (
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                      d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                )}
                {resetting ? 'Resetting…' : 'Reset All Data'}
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Tabs */}
      <div className="bg-white border-b border-gray-200 shadow-sm">
        <div className="w-full px-6">
          <nav className="flex gap-1">
            {MODULE_TABS.map(({ key, label, icon }) => (
              <button
                key={key}
                onClick={() => setActiveTab(key)}
                className={`flex items-center gap-2 px-5 py-3 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === key
                    ? 'border-blue-600 text-blue-700'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={icon} />
                </svg>
                {label}
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Content */}
      <main className="flex-1 w-full overflow-hidden">
        {activeTab === 'scientist' && <div className="p-6 h-full overflow-y-auto"><ScientistPanel key={resetKey} /></div>}
        {activeTab === 'assistant' && <div className="p-6 h-full overflow-y-auto"><LabAssistantPanel key={resetKey} onDispatch={handleDispatchToViewer} /></div>}
        {activeTab === '3dview'    && (
          <RackViewer3D
            key={resetKey}
            scenario={scenario}
            pendingCommand={pendingCommand}
            onCommandConsumed={() => setPendingCommand(null)}
          />
        )}
        {activeTab === 'orchestration' && <FactoryOrchestration3D key={resetKey} />}
      </main>
    </div>
  )
}
