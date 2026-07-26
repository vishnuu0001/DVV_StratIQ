// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: CodeAnalysis — frontend/src/components (ArchitectureLayerPanel.jsx)
// Date: 2025-10-01
// ---------------------------------------------------------------------------
import React, { useMemo, useState } from 'react'
import { motion } from 'framer-motion'
import { Layers, FileCode, ChevronDown, ChevronUp } from 'lucide-react'

const LAYER_META = {
  Presentation: {
    color:   '#6366f1',
    bg:      'bg-indigo-900/30',
    border:  'border-indigo-600/40',
    text:    'text-indigo-300',
    icon:    '🖥',
    desc:    'UI controllers, views, templates, HTTP handlers',
  },
  Coordination: {
    color:   '#f59e0b',
    bg:      'bg-amber-900/30',
    border:  'border-amber-600/40',
    text:    'text-amber-300',
    icon:    '⚙',
    desc:    'Business logic services, managers, orchestrators',
  },
  Services: {
    color:   '#10b981',
    bg:      'bg-emerald-900/30',
    border:  'border-emerald-600/40',
    text:    'text-emerald-300',
    icon:    '🔌',
    desc:    'API clients, gateways, integrations, adapters',
  },
  Persistence: {
    color:   '#3b82f6',
    bg:      'bg-blue-900/30',
    border:  'border-blue-600/40',
    text:    'text-blue-300',
    icon:    '🗄',
    desc:    'Repositories, ORMs, entities, migrations, DB models',
  },
  Other: {
    color:   '#6b7280',
    bg:      'bg-gray-800/30',
    border:  'border-gray-600/40',
    text:    'text-blue-400',
    icon:    '📄',
    desc:    'Utility, configuration, and other files',
  },
}

const LANG_COLORS = {
  Java: '#f97316', Python: '#3b82f6', '.NET': '#a855f7',
  JavaScript: '#f59e0b', TypeScript: '#06b6d4',
  Mainframe: '#9ca3af', Other: '#6b7280',
}

// Function: LayerBar
function LayerBar({ layer, maxFiles }) {
  const meta = LAYER_META[layer.name] || LAYER_META.Other
  const pct  = maxFiles > 0 ? (layer.file_count / maxFiles) * 100 : 0
  return (
    <div className={`rounded-xl border p-4 ${meta.bg} ${meta.border}`}>
      <div className="flex items-start justify-between mb-2">
        <div>
          <div className={`flex items-center gap-2 font-semibold text-sm ${meta.text}`}>
            <span>{meta.icon}</span>
            <span>{layer.name} Layer</span>
          </div>
          <div className="text-xs text-blue-500 mt-0.5">{meta.desc}</div>
        </div>
        <div className="text-right">
          <div className={`text-xl font-bold ${meta.text}`}>{layer.file_count}</div>
          <div className="text-xs text-blue-500">files ({layer.pct}%)</div>
        </div>
      </div>
      {/* Bar */}
      <div className="h-1.5 rounded-full bg-gray-800 mt-2">
        <motion.div
          className="h-full rounded-full"
          style={{ backgroundColor: meta.color }}
          initial={{ width: 0 }}
          animate={{ width: `${pct}%` }}
          transition={{ duration: 0.8, ease: 'easeOut' }}
        />
      </div>
      {/* Technologies */}
      {layer.technologies?.length > 0 && (
        <div className="flex gap-1.5 mt-2.5 flex-wrap">
          {layer.technologies.map(t => (
            <span key={t}
              className="px-1.5 py-0.5 rounded text-[10px] font-medium"
              style={{
                backgroundColor: (LANG_COLORS[t] || '#6b7280') + '30',
                color:           LANG_COLORS[t] || '#9ca3af',
                border:          `1px solid ${LANG_COLORS[t] || '#6b7280'}40`,
              }}>
              {t}
            </span>
          ))}
        </div>
      )}
      {/* SLOC */}
      <div className="text-xs text-blue-600 mt-1.5">
        {layer.sloc?.toLocaleString() || 0} SLOC
      </div>
    </div>
  )
}

// Function: NodeGrid
function NodeGrid({ nodes, activeLayer }) {
  const [page, setPage] = useState(0)
  const PAGE = 60

  const filtered = useMemo(() =>
    activeLayer === 'All'
      ? nodes
      : nodes.filter(n => n.layer === activeLayer),
    [nodes, activeLayer]
  )

  const pages   = Math.ceil(filtered.length / PAGE)
  const visible = filtered.slice(page * PAGE, (page + 1) * PAGE)

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <span className="text-xs text-blue-500">{filtered.length} files</span>
        {pages > 1 && (
          <div className="flex gap-2 items-center">
            <button
              disabled={page === 0}
              onClick={() => setPage(p => p - 1)}
              className="text-xs text-blue-400 hover:text-blue-300 disabled:text-blue-600"
            >
              <ChevronUp size={14} />
            </button>
            <span className="text-xs text-blue-500">{page + 1}/{pages}</span>
            <button
              disabled={page >= pages - 1}
              onClick={() => setPage(p => p + 1)}
              className="text-xs text-blue-400 hover:text-blue-300 disabled:text-blue-600"
            >
              <ChevronDown size={14} />
            </button>
          </div>
        )}
      </div>
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-1.5 max-h-72 overflow-y-auto">
        {visible.map((n, i) => {
          const meta   = LAYER_META[n.layer] || LAYER_META.Other
          const lcolor = LANG_COLORS[n.language] || '#6b7280'
          return (
            <motion.div
              key={i}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: i * 0.005 }}
              className={`px-2 py-1 rounded-lg border text-[10px] truncate flex items-center gap-1.5
                ${meta.bg} ${meta.border} hover:opacity-80 transition-opacity cursor-default`}
              title={`${n.name} · ${n.layer} · ${n.language} · ${n.sloc} SLOC`}
            >
              <span className="w-1.5 h-1.5 rounded-full flex-shrink-0"
                    style={{ backgroundColor: lcolor }} />
              <span className="truncate text-blue-300">{n.name}</span>
            </motion.div>
          )
        })}
      </div>
    </div>
  )
}

// Function: ArchitectureLayerPanel
export default function ArchitectureLayerPanel({ architecture }) {
  const [activeLayer, setActiveLayer] = useState('All')

  if (!architecture?.has_data) {
    return (
      <div className="py-16 text-center text-blue-500">
        <Layers size={32} className="mx-auto mb-3 opacity-40" />
        <p>Architecture layer data not available. Re-run analysis to generate layer diagram.</p>
      </div>
    )
  }

  const { layers = [], nodes = [], total_files, layer_counts, layer_sloc = {} } = architecture
  const maxFiles = Math.max(...layers.map(l => l.file_count), 1)
  const layerNames = ['All', ...layers.map(l => l.name)]

  // Compute pie data
  const definedLayers = layers.filter(l => l.name !== 'Other')

  return (
    <div className="space-y-6">
      {/* Summary */}
      <div className="flex flex-wrap items-center gap-3">
        <div className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gray-900/60 border border-surface-border">
          <FileCode size={14} className="text-indigo-400" />
          <span className="text-xs text-blue-500">Total Classified</span>
          <span className="text-sm font-bold text-blue-300">{total_files.toLocaleString()} files</span>
        </div>
        {definedLayers.map(l => {
          const meta = LAYER_META[l.name] || LAYER_META.Other
          return (
            <div key={l.name} className={`flex items-center gap-2 px-3 py-1.5 rounded-xl border text-xs ${meta.bg} ${meta.border} ${meta.text}`}>
              <span>{meta.icon}</span>
              <span>{l.name}</span>
              <span className="font-bold">{l.file_count}</span>
            </div>
          )
        })}
      </div>

      {/* Layer Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
        {layers.map((l, i) => (
          <motion.div
            key={l.name}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.06 }}
          >
            <LayerBar layer={l} maxFiles={maxFiles} />
          </motion.div>
        ))}
      </div>

      {/* Node browser */}
      <div className="rounded-xl border border-surface-border p-4 bg-gray-900/30">
        <div className="flex items-center gap-3 mb-3">
          <span className="text-sm font-semibold text-blue-200">File Layer Map</span>
          <div className="flex gap-1.5 flex-wrap">
            {layerNames.map(ln => {
              const meta = LAYER_META[ln] || { text: 'text-blue-400', bg: 'bg-gray-800', border: 'border-gray-700' }
              const isActive = activeLayer === ln
              return (
                <button
                  key={ln}
                  onClick={() => setActiveLayer(ln)}
                  className={`px-2 py-0.5 rounded text-[10px] font-medium border transition-all
                    ${isActive ? `${meta.bg} ${meta.border} ${meta.text}` : 'bg-transparent border-gray-700 text-blue-500 hover:text-gray-300'}`}
                >
                  {ln}
                  {ln !== 'All' && layer_counts[ln] > 0 && (
                    <span className="ml-1 opacity-60">({layer_counts[ln]})</span>
                  )}
                </button>
              )
            })}
          </div>
        </div>
        <NodeGrid nodes={nodes} activeLayer={activeLayer} />
      </div>

      {/* ── SLOC distribution per layer ──────────────────────────────────── */}
      {layer_sloc && Object.keys(layer_sloc).length > 0 && (
        <div className="rounded-xl border border-surface-border overflow-hidden">
          <div className="px-4 py-3 bg-gray-900/60 border-b border-surface-border text-sm font-semibold text-blue-200">
            SLOC Distribution by Layer
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead className="bg-gray-900/40">
                <tr>
                  <th className="px-4 py-2.5 text-left text-blue-500 font-medium">Layer</th>
                  <th className="px-4 py-2.5 text-left text-blue-500 font-medium">Description</th>
                  <th className="px-3 py-2.5 text-right text-blue-500 font-medium">Files</th>
                  <th className="px-3 py-2.5 text-right text-blue-500 font-medium">SLOC</th>
                  <th className="px-3 py-2.5 text-right text-blue-500 font-medium">SLOC %</th>
                  <th className="px-3 py-2.5 text-right text-blue-500 font-medium">File %</th>
                  <th className="px-3 py-2.5 text-left text-blue-500 font-medium" style={{ minWidth: 120 }}>Distribution</th>
                  <th className="px-4 py-2.5 text-left text-blue-500 font-medium">Technologies</th>
                </tr>
              </thead>
              <tbody>
                {(() => {
                  const totalSloc  = Object.values(layer_sloc).reduce((s, v) => s + (v ?? 0), 0) || 1
                  const totalFiles = layers.reduce((s, l) => s + l.file_count, 0) || 1
                  return layers.map((l, i) => {
                    const meta    = LAYER_META[l.name] || LAYER_META.Other
                    const sloc    = layer_sloc[l.name] ?? l.sloc ?? 0
                    const slocPct = ((sloc / totalSloc) * 100).toFixed(1)
                    const filePct = ((l.file_count / totalFiles) * 100).toFixed(1)
                    const barPct  = Math.round((sloc / totalSloc) * 100)
                    return (
                      <tr key={l.name} className="border-b border-surface-border/50 hover:bg-gray-800/20">
                        <td className="px-4 py-2.5">
                          <div className={`flex items-center gap-2 font-semibold ${meta.text}`}>
                            <span>{meta.icon}</span>
                            <span>{l.name}</span>
                          </div>
                        </td>
                        <td className="px-4 py-2.5 text-blue-600 max-w-[200px] truncate" title={meta.desc}>
                          {meta.desc}
                        </td>
                        <td className="px-3 py-2.5 text-right font-mono text-blue-400">{l.file_count.toLocaleString()}</td>
                        <td className="px-3 py-2.5 text-right font-mono text-blue-300 font-semibold">{sloc.toLocaleString()}</td>
                        <td className="px-3 py-2.5 text-right font-mono font-semibold" style={{ color: meta.color }}>
                          {slocPct}%
                        </td>
                        <td className="px-3 py-2.5 text-right font-mono text-blue-400">{filePct}%</td>
                        <td className="px-3 py-2.5">
                          <div className="h-2 w-28 rounded-full bg-gray-800 overflow-hidden">
                            <div className="h-full rounded-full transition-all"
                                 style={{ width: `${barPct}%`, backgroundColor: meta.color }} />
                          </div>
                        </td>
                        <td className="px-4 py-2.5">
                          <div className="flex flex-wrap gap-1">
                            {(l.technologies || []).map(t => (
                              <span key={t} className="text-[10px] px-1.5 py-0.5 rounded font-mono"
                                style={{ color: meta.color, background: meta.color + '20', border: `1px solid ${meta.color}30` }}>
                                {t}
                              </span>
                            ))}
                          </div>
                        </td>
                      </tr>
                    )
                  })
                })()}
              </tbody>
              <tfoot>
                <tr className="border-t border-surface-border bg-gray-900/40">
                  <td className="px-4 py-2.5 text-xs font-semibold text-blue-300">Total</td>
                  <td className="px-4 py-2.5" />
                  <td className="px-3 py-2.5 text-right font-mono font-bold text-blue-300">
                    {layers.reduce((s, l) => s + l.file_count, 0).toLocaleString()}
                  </td>
                  <td className="px-3 py-2.5 text-right font-mono font-bold text-blue-300">
                    {Object.values(layer_sloc).reduce((s, v) => s + (v ?? 0), 0).toLocaleString()}
                  </td>
                  <td className="px-3 py-2.5 text-right font-mono font-bold text-blue-300">100%</td>
                  <td colSpan={3} />
                </tr>
              </tfoot>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
