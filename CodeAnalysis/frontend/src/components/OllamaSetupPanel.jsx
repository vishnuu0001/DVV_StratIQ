// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: * OllamaSetupPanel.jsx
// Date: 2025-12-24
// ---------------------------------------------------------------------------
/**
 * OllamaSetupPanel.jsx
 * -------------------
 * Manage Ollama connectivity and model installation.
 */
import { useEffect, useState, useCallback } from 'react'
import { Server, Download, CheckCircle, XCircle, Cpu, RefreshCw, ChevronRight } from 'lucide-react'
import { motion } from 'framer-motion'
import { getAiHealth, getAiJob, pullAiModel } from '../api/client.js'
import { modelDisplayName } from '../modelDisplay.js'

// Function: Badge
function Badge({ label, color }) {
  const cls = {
    green:  'bg-green-100 text-green-800',
    red:    'bg-red-100 text-red-800',
    yellow: 'bg-yellow-100 text-yellow-800',
    blue:   'bg-blue-100 text-blue-800',
    gray:   'bg-gray-100 text-blue-600',
  }[color] || 'bg-gray-100 text-blue-600'
  return <span className={`px-2 py-0.5 rounded text-xs font-semibold ${cls}`}>{label}</span>
}

// Function: OllamaSetupPanel
export default function OllamaSetupPanel({ onModelReady }) {
  const [health,   setHealth]   = useState(null)
  const [loading,  setLoading]  = useState(true)
  const [pulling,  setPulling]  = useState({})   // { model_id: { pct, message } }
  const [pollIds,  setPollIds]  = useState({})   // { model_id: job_id }

  const refresh = useCallback(async () => {
    setLoading(true)
    try {
      const d = await getAiHealth()
      setHealth(d)
      if (onModelReady && d.best_model) onModelReady(d.best_model)
    } catch {
      setHealth(null)
    } finally {
      setLoading(false)
    }
  }, [onModelReady])

  useEffect(() => { refresh() }, [refresh])

  // Poll pull jobs
  useEffect(() => {
    if (!Object.keys(pollIds).length) return
    const id = setInterval(async () => {
      for (const [mid, jobId] of Object.entries(pollIds)) {
        try {
          const d = await getAiJob(jobId)
          if (d.status === 'done') {
            setPulling(p => { const x = { ...p }; delete x[mid]; return x })
            setPollIds(p => { const x = { ...p }; delete x[mid]; return x })
            refresh()
          } else if (d.status === 'error') {
            setPulling(p => ({ ...p, [mid]: { pct: 0, message: `Error: ${d.message}` } }))
            setPollIds(p => { const x = { ...p }; delete x[mid]; return x })
          } else {
            setPulling(p => ({ ...p, [mid]: { pct: d.progress || 0, message: d.message || 'Downloading…' } }))
          }
        } catch { /* ignore */ }
      }
    }, 1500)
    return () => clearInterval(id)
  }, [pollIds, refresh])

  // Function: pullModel
  const pullModel = async (modelId) => {
    setPulling(p => ({ ...p, [modelId]: { pct: 0, message: 'Starting download…' } }))
    const d = await pullAiModel(modelId)
    setPollIds(p => ({ ...p, [modelId]: d.job_id }))
  }

  const ollamaOk  = health?.ollama?.ok
  const models    = health?.models || []
  const bestModel = health?.best_model

  return (
    <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">

      {/* Ollama connection card */}
      <div className="bg-white rounded-2xl shadow p-6 space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Server size={20} className="text-indigo-600" />
            <h2 className="text-lg font-semibold text-blue-800">Ollama Connection</h2>
          </div>
          <button onClick={refresh} className="flex items-center gap-1 text-xs text-blue-500 hover:text-indigo-600 transition">
            <RefreshCw size={13} className={loading ? 'animate-spin' : ''} /> Refresh
          </button>
        </div>

        {loading ? (
          <p className="text-sm text-blue-400 animate-pulse">Checking Ollama…</p>
        ) : ollamaOk ? (
          <div className="flex flex-wrap gap-3 items-center">
            <CheckCircle size={18} className="text-green-500" />
            <span className="text-sm text-green-700 font-medium">Connected — {health.ollama.host}</span>
            <Badge label={`v${health.ollama.version}`} color="green" />
            {bestModel && <Badge label={`Best model: ${modelDisplayName(bestModel)}`} color="blue" />}
          </div>
        ) : (
          <div className="space-y-2">
            <div className="flex items-center gap-2 text-red-600 text-sm font-medium">
              <XCircle size={18} /> Ollama not reachable
            </div>
            <p className="text-xs text-blue-500">
              Make sure Ollama is running: <code className="bg-gray-100 px-1 rounded">ollama serve</code>
            </p>
            {health?.ollama?.error && (
              <p className="text-xs text-red-400">{health.ollama.error}</p>
            )}
          </div>
        )}
      </div>

      {/* Model list */}
      <div className="bg-white rounded-2xl shadow p-6 space-y-4">
        <div className="flex items-center gap-3">
          <Cpu size={20} className="text-indigo-600" />
          <h2 className="text-lg font-semibold text-blue-800">Recommended Models</h2>
        </div>
        <p className="text-xs text-blue-500">
          Pull <strong>DeepSeek-Coder 6.7B</strong>, the default model for code analysis and
          optimized AI predictions. Other installed models remain available as fallbacks.
        </p>

        <div className="space-y-3">
          {(health?.recommended || models).map(m => {
            const pullState = pulling[m.id]
            const installed = m.installed
            const isBest    = m.id === bestModel || (bestModel && bestModel.startsWith(m.id?.split(':')[0]))
            return (
              <div key={m.id} className={`rounded-xl border p-4 flex items-start gap-4 transition ${installed ? 'border-green-200 bg-green-50' : 'border-gray-200'}`}>
                <div className="flex-1 min-w-0">
                  <div className="flex flex-wrap items-center gap-2 mb-1">
                    <span className="font-semibold text-sm text-blue-800">{modelDisplayName(m.name || m.id)}</span>
                    {installed && <Badge label="Installed" color="green" />}
                    {isBest    && <Badge label="Active"    color="blue"  />}
                    {m.size    && <Badge label={m.size}    color="gray"  />}
                  </div>
                  <p className="text-xs text-blue-500">{m.desc}</p>
                  {pullState && (
                    <div className="mt-2 space-y-1">
                      <div className="flex justify-between text-xs text-blue-500">
                        <span>{pullState.message}</span>
                        <span>{pullState.pct}%</span>
                      </div>
                      <div className="h-1.5 bg-gray-200 rounded-full">
                        <div className="h-1.5 bg-indigo-500 rounded-full transition-all" style={{ width: `${pullState.pct}%` }} />
                      </div>
                    </div>
                  )}
                </div>
                {!installed && !pullState && ollamaOk && (
                  <button
                    onClick={() => pullModel(m.id)}
                    className="flex items-center gap-1 text-xs font-semibold text-blue-300 bg-indigo-600 hover:bg-indigo-700 px-3 py-1.5 rounded-lg whitespace-nowrap"
                  >
                    <Download size={12} /> Pull
                  </button>
                )}
                {installed && (
                  <CheckCircle size={20} className="text-green-500 shrink-0 mt-0.5" />
                )}
              </div>
            )
          })}
        </div>
      </div>

      {/* Quick usage tip */}
      <div className="bg-indigo-50 border border-indigo-100 rounded-2xl p-5 flex gap-3">
        <ChevronRight size={18} className="text-indigo-500 mt-0.5 shrink-0" />
        <div className="text-sm text-indigo-800">
          <strong>Next:</strong> Once a model is installed, go to the <strong>AI Analysis</strong> tab
          to run AI-powered tech debt, microservices decomposition, cloud migration, business rule
          extraction, modernisation roadmap, and test-data generation.
        </div>
      </div>
    </motion.div>
  )
}
