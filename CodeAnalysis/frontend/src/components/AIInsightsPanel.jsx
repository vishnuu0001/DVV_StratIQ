// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: * AIInsightsPanel.jsx
// Date: 2026-01-18
// ---------------------------------------------------------------------------
/**
 * AIInsightsPanel.jsx
 * --------------------
 * Master AI Analysis panel â€“ full-repo + per-module ML analysis.
 * Multi-select modules, run analysis for selected ones, view results via dropdown.
 */
import { useState, useEffect, useCallback } from 'react'
import { Brain, RefreshCw, AlertCircle, CheckCircle2, Layers, ChevronDown, ChevronUp, CheckSquare, Square } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import AITechDebtPanel         from './AITechDebtPanel'
import AICloudBlockersPanel    from './AICloudBlockersPanel'
import MicroservicesPanel      from './MicroservicesPanel'
import BusinessRulesPanel      from './BusinessRulesPanel'
import AITransformationPanel   from './AITransformationPanel'
import CodeLevelPanel          from './CodeLevelPanel'
import { getAiJob, startAiAnalysis, listStratAqorynthModules, startAnalysis, getJob } from '../api/client.js'

const TABS = [
  { key: 'tech_debt',      label: 'Tech Debt',        component: AITechDebtPanel,       prop: 'techDebt'      },
  { key: 'cloud_blockers', label: 'Cloud Migration',  component: AICloudBlockersPanel,  prop: 'cloudBlockers' },
  { key: 'microservices',  label: 'Microservices',    component: MicroservicesPanel,    prop: 'microservices' },
  { key: 'business_rules', label: 'Business Rules',   component: BusinessRulesPanel,    prop: 'businessRules' },
  { key: 'transformation', label: 'Modernisation',    component: AITransformationPanel, prop: 'transformation'},
  { key: 'code_level',     label: 'Code Level',        component: CodeLevelPanel,        prop: 'codeLevel'     },
]

const MODULE_COLORS = {
  AIPlayBook:          'bg-purple-100 text-purple-700 border-purple-300',
  AppRationalization:  'bg-blue-100 text-blue-700 border-blue-300',
  CodeAnalysis:        'bg-indigo-100 text-indigo-700 border-indigo-300',
  InfraRationalization:'bg-orange-100 text-orange-700 border-orange-300',
  'Novastra-ITSM':      'bg-teal-100 text-teal-700 border-teal-300',
  LabRobot:            'bg-green-100 text-green-700 border-green-300',
  Modernization:       'bg-pink-100 text-pink-700 border-pink-300',
}

// Function: AIInsightsPanel
export default function AIInsightsPanel({ jobId, scanJobId, bestModel, onReportChange }) {
  // â”€â”€ Module selector state â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
  const [modules,         setModules]         = useState([])
  const [modulesLoading,  setModulesLoading]  = useState(true)
  const [selectedModules, setSelectedModules] = useState(new Set())
  const [showModulePanel, setShowModulePanel] = useState(false)
  const [moduleResults,   setModuleResults]   = useState({})  // { name: { scanJobId, scanState, aiJobId, aiState } }
  const [viewingModule,   setViewingModule]   = useState(null)
  const [moduleActiveTab, setModuleActiveTab] = useState('tech_debt')
  const [runningAnalysis, setRunningAnalysis] = useState(false)

  const updateModuleResult = useCallback((name, update) => {
    setModuleResults(prev => ({ ...prev, [name]: { ...(prev[name] || {}), ...update } }))
  }, [])

  // Load module list on mount
  useEffect(() => {
    setModulesLoading(true)
    listStratAqorynthModules(scanJobId || jobId)
      .then(d => {
        const mods = d.modules || []
        setModules(mods)

        // Evict stale localStorage entries for modules no longer in the current workspace
        const currentNames = new Set(mods.map(m => m.name))
        for (let i = localStorage.length - 1; i >= 0; i--) {
          const key = localStorage.key(i)
          if (!key) continue
          const match = key.match(/^module_(ai|scan)_(.+)$/)
          if (match && !currentNames.has(match[2])) {
            localStorage.removeItem(key)
          }
        }

        // Restore cached results from localStorage only for modules in the current workspace
        const cached = {}
        for (const mod of mods) {
          const aiCache   = localStorage.getItem(`module_ai_${mod.name}`)
          const scanCache = localStorage.getItem(`module_scan_${mod.name}`)
          if (aiCache || scanCache) {
            cached[mod.name] = {}
            if (scanCache) {
              try { const p = JSON.parse(scanCache); cached[mod.name].scanJobId = p.job_id; cached[mod.name].scanState = p.state } catch {}
            }
            if (aiCache) {
              try { cached[mod.name].aiState = JSON.parse(aiCache) } catch {}
            }
          }
        }
        setModuleResults(cached)
        // Auto-select first done module for viewing
        const doneNames = Object.entries(cached)
          .filter(([, r]) => r.aiState?.status === 'done')
          .map(([n]) => n)
        if (doneNames.length > 0) setViewingModule(doneNames[0])
      })
      .catch(() => {})
      .finally(() => setModulesLoading(false))
  }, [scanJobId, jobId])

  // â”€â”€ Multi-module selection â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
  // Function: toggleModule
  const toggleModule = (name) => {
    setSelectedModules(prev => {
      const next = new Set(prev)
      next.has(name) ? next.delete(name) : next.add(name)
      return next
    })
  }
  // Function: selectAll
  const selectAll   = () => setSelectedModules(new Set(modules.filter(m => m.exists).map(m => m.name)))
  // Function: deselectAll
  const deselectAll = () => setSelectedModules(new Set())

  // â”€â”€ Run analysis for selected modules â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
  // Function: runSelectedModules
  const runSelectedModules = async () => {
    if (selectedModules.size === 0) return
    setRunningAnalysis(true)
    const modList = [...selectedModules]
      .map(name => modules.find(m => m.name === name))
      .filter(Boolean)

    // Phase 1: Scan all selected modules in parallel
    const scanJobIds = {}
    await Promise.all(modList.map(async mod => {
      updateModuleResult(mod.name, {
        scanState: { status: 'running', progress: 5, message: 'Starting scanâ€¦' },
        aiState: null,
      })
      try {
        const res = await startAnalysis({ local: mod.path, users: 100, revenue: 0 })
        scanJobIds[mod.name] = res.job_id
        updateModuleResult(mod.name, { scanJobId: res.job_id })
        for (let i = 0; i < 240; i++) {
          await new Promise(r => setTimeout(r, 3000))
          const state = await getJob(res.job_id)
          updateModuleResult(mod.name, { scanState: state })
          if (state.status === 'done' || state.status === 'error') break
        }
        try {
          localStorage.setItem(`module_scan_${mod.name}`, JSON.stringify({ job_id: res.job_id, state: { status: 'done', progress: 100 } }))
        } catch {}
      } catch (e) {
        updateModuleResult(mod.name, {
          scanState: { status: 'error', message: e?.response?.data?.detail || e.message },
        })
      }
    }))

    // Phase 2: Run AI analysis in parallel (async mode for all modules simultaneously)
    await Promise.all(modList.map(async mod => {
      const sJobId = scanJobIds[mod.name]
      if (!sJobId) return
      updateModuleResult(mod.name, { aiState: { status: 'queued', progress: 0, message: 'Queuedâ€¦' } })
      try {
        const aiRes = await startAiAnalysis({ job_id: sJobId, model: bestModel || null })
        if (aiRes.ai_job_id) {
          updateModuleResult(mod.name, { aiJobId: aiRes.ai_job_id })
          let finalState = null
          for (let i = 0; i < 360; i++) {
            await new Promise(r => setTimeout(r, 3000))
            const state = await getAiJob(aiRes.ai_job_id)
            updateModuleResult(mod.name, { aiState: state })
            if (state.status === 'done' || state.status === 'error') { finalState = state; break }
          }
          if (finalState?.status === 'done') {
            try { localStorage.setItem(`module_ai_${mod.name}`, JSON.stringify(finalState)) } catch {}
            setViewingModule(prev => prev || mod.name)
          }
        }
      } catch (e) {
        updateModuleResult(mod.name, { aiState: { status: 'error', message: e?.response?.data?.detail || e.message } })
      }
    }))
    setRunningAnalysis(false)
  }

  // â”€â”€ Wire selected module AI result â†’ Dashboard tabs â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
  useEffect(() => {
    if (!onReportChange) return
    const result = viewingModule ? moduleResults[viewingModule]?.aiState?.result : null
    onReportChange(result || null)
  }, [viewingModule, moduleResults, onReportChange])

  // â”€â”€ Derived values â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
  const doneModules = Object.entries(moduleResults)
    .filter(([, r]) => r.aiState?.status === 'done')
    .map(([name]) => name)

  const anyModuleRunning = Object.values(moduleResults).some(
    r => r.scanState?.status === 'running' || r.aiState?.status === 'running' || r.aiState?.status === 'queued'
  )

  const viewingResult = viewingModule ? moduleResults[viewingModule] : null
  const viewAiData    = viewingResult?.aiState?.result
  const viewAnalyses  = viewAiData?.analyses || {}

  return (
    <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">

      {/* â”€â”€ Module Selector Panel â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ */}
      <div className="bg-white rounded-2xl shadow p-5">
        <button
          onClick={() => setShowModulePanel(v => !v)}
          className="w-full flex items-center justify-between"
        >
          <div className="flex items-center gap-3">
            <Layers size={20} className="text-indigo-500" />
            <div className="text-left">
              <h3 className="text-base font-bold text-blue-800">Strat-Aqorynth Module Analysis</h3>
              <p className="text-xs text-blue-400 mt-0.5">
                Analyse each module independently â€” {modules.length} module{modules.length !== 1 ? 's' : ''} Â· Full codebase coverage
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {selectedModules.size > 0 && (
              <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-indigo-100 text-indigo-700 border border-indigo-300">
                {selectedModules.size} selected
              </span>
            )}
            {doneModules.length > 0 && (
              <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-green-100 text-green-700 border border-green-300">
                {doneModules.length} analysed
              </span>
            )}
            {showModulePanel
              ? <ChevronUp size={16} className="text-blue-400" />
              : <ChevronDown size={16} className="text-blue-400" />
            }
          </div>
        </button>

        <AnimatePresence>
          {showModulePanel && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: 0.2 }}
              className="overflow-hidden"
            >
              <div className="mt-4 pt-4 border-t border-gray-100 space-y-4">

                {/* Loading spinner */}
                {modulesLoading && (
                  <div className="flex items-center justify-center gap-2 text-sm text-blue-500 py-6">
                    <RefreshCw size={16} className="animate-spin" />
                    <span>Loading modulesâ€¦</span>
                  </div>
                )}

                {/* Module grid */}
                {!modulesLoading && modules.length > 0 && (
                  <>
                    {/* Controls row */}
                    <div className="flex items-center justify-between">
                      <p className="text-xs text-blue-500 font-medium">Select modules to analyse:</p>
                      <div className="flex gap-2">
                        <button
                          onClick={selectAll}
                          className="text-xs text-indigo-600 hover:text-indigo-800 font-medium px-2.5 py-1 rounded-lg border border-indigo-200 hover:bg-indigo-50 transition"
                        >
                          Select All
                        </button>
                        <button
                          onClick={deselectAll}
                          className="text-xs text-gray-500 hover:text-gray-700 font-medium px-2.5 py-1 rounded-lg border border-gray-200 hover:bg-gray-50 transition"
                        >
                          Clear
                        </button>
                      </div>
                    </div>

                    {/* Module cards */}
                    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-2">
                      {modules.map(mod => {
                        const isSelected   = selectedModules.has(mod.name)
                        const modResult    = moduleResults[mod.name] || {}
                        const scanStatus   = modResult.scanState?.status
                        const aiStatus     = modResult.aiState?.status
                        const isModDone    = aiStatus === 'done'
                        const isModRunning = scanStatus === 'running' || aiStatus === 'running' || aiStatus === 'queued'
                        const colorClass   = MODULE_COLORS[mod.name] || 'bg-gray-100 text-gray-700 border-gray-300'

                        return (
                          <button
                            key={mod.name}
                            onClick={() => mod.exists && toggleModule(mod.name)}
                            disabled={!mod.exists}
                            className={`relative flex flex-col items-start gap-1 p-3 rounded-xl border-2 text-left transition-all ${
                              !mod.exists
                                ? 'border-gray-100 bg-gray-50 opacity-40 cursor-not-allowed'
                                : isSelected
                                  ? `${colorClass} ring-2 ring-offset-1 ring-indigo-400`
                                  : 'border-gray-200 hover:border-indigo-300 hover:bg-indigo-50/40 bg-white'
                            }`}
                          >
                            <div className="flex items-center gap-1.5 w-full">
                              {isSelected
                                ? <CheckSquare size={13} className="text-indigo-600 shrink-0" />
                                : <Square size={13} className="text-gray-300 shrink-0" />
                              }
                              <span className="text-xs font-semibold truncate flex-1">{mod.name}</span>
                              {isModRunning && <RefreshCw size={11} className="animate-spin text-blue-500 shrink-0" />}
                              {!isModRunning && isModDone && <CheckCircle2 size={11} className="text-green-500 shrink-0" />}
                            </div>
                            <span className="text-[10px] text-gray-400 pl-5">
                              {mod.file_count?.toLocaleString()} files
                            </span>
                            {isModRunning && (
                              <span className="text-[9px] text-blue-500 pl-5 animate-pulse">
                                {aiStatus === 'queued' ? 'Queuedâ€¦' : aiStatus === 'running' ? 'AI runningâ€¦' : 'Scanningâ€¦'}
                              </span>
                            )}
                          </button>
                        )
                      })}
                    </div>

                    {/* Run Analysis button row */}
                    <div className="flex items-center justify-between pt-2 border-t border-gray-100">
                      <p className="text-xs text-blue-400">
                        {selectedModules.size === 0
                          ? 'Select one or more modules above to run ML analysis'
                          : `${selectedModules.size} module${selectedModules.size > 1 ? 's' : ''} selected â€” scan + AI analysis will run`
                        }
                      </p>
                      <button
                        onClick={runSelectedModules}
                        disabled={selectedModules.size === 0 || runningAnalysis || anyModuleRunning}
                        className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed text-white text-sm font-semibold px-5 py-2 rounded-xl transition"
                      >
                        {runningAnalysis || anyModuleRunning
                          ? <><RefreshCw size={14} className="animate-spin" />Running Analysisâ€¦</>
                          : <><Brain size={14} />Run Analysis{selectedModules.size > 0 ? ` (${selectedModules.size})` : ''}</>
                        }
                      </button>
                    </div>
                  </>
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* â”€â”€ Module Analysis Results Viewer â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ */}
      {doneModules.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white rounded-2xl shadow p-6 space-y-4"
        >
          {/* Header row with module dropdown */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div className="flex items-center gap-3">
              <Brain size={20} className="text-indigo-500" />
              <div>
                <p className="text-sm font-bold text-blue-800">Module Analysis Results</p>
                <p className="text-xs text-blue-400 mt-0.5">{doneModules.length} module{doneModules.length > 1 ? 's' : ''} analysed</p>
              </div>
            </div>

            {/* Module selector dropdown */}
            <div className="flex items-center gap-2">
              <label className="text-xs text-blue-400 whitespace-nowrap">View analysis for:</label>
              <select
                value={viewingModule || ''}
                onChange={e => setViewingModule(e.target.value)}
                className="text-sm border border-gray-200 rounded-lg px-3 py-1.5 bg-white text-blue-800 focus:outline-none focus:ring-2 focus:ring-indigo-400"
              >
                {doneModules.map(name => (
                  <option key={name} value={name}>{name}</option>
                ))}
              </select>
            </div>
          </div>

          {viewingModule && viewAiData && (
            <>
              {/* Meta row */}
              <div className="flex flex-wrap gap-3 text-xs text-blue-500 pb-2 border-b border-gray-100">
                <span className={`px-2.5 py-0.5 rounded-full border font-bold ${MODULE_COLORS[viewingModule] || 'bg-gray-100 text-gray-700 border-gray-300'}`}>
                  {viewingModule}
                </span>
                <span className="flex items-center gap-1"><CheckCircle2 size={12} className="text-green-500"/>AI complete</span>
                <span>Model: <strong>{viewAiData.model_used}</strong></span>
                {viewAiData.repo_name && <span>Repo: <strong>{viewAiData.repo_name}</strong></span>}
                {viewAiData.call_graph_stats && (
                  <span><strong>{viewAiData.call_graph_stats.total_functions}</strong> functions mapped</span>
                )}
              </div>

              {/* Sub-tabs */}
              <div className="flex flex-wrap gap-2">
                {TABS.map(t => {
                  const data = viewAnalyses[t.key]
                  const ok   = data && !data.error
                  return (
                    <button
                      key={t.key}
                      onClick={() => setModuleActiveTab(t.key)}
                      className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium transition border ${
                        moduleActiveTab === t.key
                          ? 'bg-indigo-600 text-white border-indigo-600'
                          : 'bg-white text-blue-600 border-gray-200 hover:border-indigo-300'
                      }`}
                    >
                      {t.label}
                      {data && (ok
                        ? <CheckCircle2 size={12} className={moduleActiveTab === t.key ? 'text-indigo-200' : 'text-green-500'}/>
                        : <AlertCircle  size={12} className={moduleActiveTab === t.key ? 'text-indigo-200' : 'text-red-400'}/>
                      )}
                    </button>
                  )
                })}
              </div>

              {/* Tab content */}
              {TABS.map(t => {
                if (moduleActiveTab !== t.key) return null
                const Comp = t.component
                const data = viewAnalyses[t.key]
                if (!data) return (
                  <div key={t.key} className="bg-gray-50 rounded-2xl p-8 text-center text-blue-400 text-sm">
                    No data returned for this analysis.
                  </div>
                )
                return <Comp key={t.key} data={data} />
              })}
            </>
          )}
        </motion.div>
      )}

    </motion.div>
  )
}



