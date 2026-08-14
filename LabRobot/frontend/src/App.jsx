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
import AILabCatalog from './components/AILabCatalog'
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
  {
    key: 'ai-lab',
    label: 'AI Lab',
    icon: 'M13 3L4 14h6l-1 7 9-11h-6l1-7z',
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
    <div className="min-h-screen bg-chrome-50 font-sans">
      {/* Azure Portal masthead — near-black, high-contrast white text */}
      <div className="bg-chrome-950 text-white sticky top-0 z-40">
        <div className="w-full pl-3 pr-4 h-12 flex items-center justify-between gap-3">
          <div className="flex items-center gap-3 min-w-0">
            <div className="w-8 h-8 rounded flex items-center justify-center shrink-0" style={{ background: '#0078D4' }}>
              <svg className="w-[18px] h-[18px] text-white" viewBox="0 0 24 24" fill="currentColor">
                <path d="M13 3L4 14h6l-1 7 9-11h-6l1-7z" />
              </svg>
            </div>
            <div className="min-w-0 leading-tight">
              <p className="text-[11px] font-semibold uppercase tracking-[0.14em] text-white/70 truncate">
                Unified Modernization Suite
              </p>
              <p className="text-sm font-semibold text-white truncate">Lab Robot Workspace</p>
            </div>
          </div>
          <div className="flex items-center gap-1 shrink-0">
            <a
              href={`${portalBaseUrl}/launch-modules`}
              className="px-3 h-8 flex items-center rounded text-sm font-medium text-white/90 hover:bg-white/10 hover:text-white transition-colors"
            >
              Portal Home
            </a>
            <a
              href={`${portalBaseUrl}/admin`}
              className="px-3 h-8 flex items-center rounded text-sm font-medium text-white/90 hover:bg-white/10 hover:text-white transition-colors"
            >
              Admin Console
            </a>
            <span className="mx-1 h-5 w-px bg-white/20" />
            <a
              href={`${portalBaseUrl}/login`}
              className="px-3 h-8 flex items-center rounded text-sm font-medium text-white/90 hover:bg-white/10 hover:text-white transition-colors"
            >
              Logout
            </a>
          </div>
        </div>
      </div>

      {/* Blade header — Azure Portal's resource-type "hero" banner: solid
          Communication Blue (#0078D4), the color most associated with the
          Azure brand, with white/light-blue text held to AA contrast. */}
      <header style={{ background: 'linear-gradient(135deg, #106EBE 0%, #0078D4 55%, #005A9E 100%)' }}>
        <div className="w-full px-6 pt-4 pb-3">
          <div className="flex items-start justify-between gap-4 flex-wrap">
            <div className="flex items-start gap-3 min-w-0">
              <div className="w-9 h-9 rounded flex items-center justify-center shrink-0 mt-0.5 bg-white">
                <svg className="w-5 h-5" style={{ color: '#0078D4' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.75}
                    d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
                </svg>
              </div>
              <div className="min-w-0">
                <p className="text-xs font-medium tracking-wide text-white/80">
                  Strat-Aqorynth &gt; Modules &gt; Lab Robot
                </p>
                <h1 className="text-[22px] font-semibold leading-snug text-white">
                  Lab Robot Management System
                </h1>
                <p className="text-sm mt-0.5 text-white/85">
                  Production · Quality · Intralogistics · Real-time Simulation
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              {activeTab === '3dview' && (
                <select
                  value={scenario}
                  onChange={(e) => setScenario(e.target.value)}
                  className="h-8 px-2.5 rounded text-sm font-medium bg-white border-none transition-colors focus:outline-none"
                  style={{ color: '#201F1E' }}
                >
                  <option value="mixed">Full Factory</option>
                  <option value="production">Production &amp; Assembly</option>
                  <option value="warehouse">Warehouse &amp; Intralogistics</option>
                  <option value="quality">Quality &amp; Inspection</option>
                </select>
              )}
            </div>
          </div>

          {/* Command bar */}
          <div className="mt-3 -mx-1 flex items-center gap-0.5 border-t border-white/20 pt-1.5">
            <button
              type="button"
              onClick={handleReset}
              disabled={resetting}
              className="flex items-center gap-1.5 px-2.5 h-8 rounded text-sm font-semibold transition-colors disabled:opacity-50 bg-white"
              style={{ color: '#A4262C' }}
              onMouseEnter={(e) => { e.currentTarget.style.background = '#FDE7E9' }}
              onMouseLeave={(e) => { e.currentTarget.style.background = '#FFFFFF' }}
            >
              {resetting ? (
                <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
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
      </header>

      {/* Pivot tabs */}
      <div className="bg-white border-b border-chrome-200 shadow-fluent">
        <div className="w-full px-6">
          <nav className="flex gap-1">
            {MODULE_TABS.map(({ key, label, icon }) => (
              <button
                key={key}
                type="button"
                onClick={() => setActiveTab(key)}
                className={`flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === key
                    ? 'border-azure-600 text-azure-700'
                    : 'border-transparent hover:text-chrome-900'
                }`}
                style={activeTab === key ? undefined : { color: '#605E5C' }}
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
        {activeTab === 'ai-lab' && <div className="p-6 h-full overflow-y-auto"><AILabCatalog key={resetKey} /></div>}
      </main>
    </div>
  )
}
