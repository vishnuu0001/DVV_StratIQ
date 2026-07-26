// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: Novastra-ITSM — frontend/src/pages (KnowledgeGraphPage.jsx)
// Date: 2025-07-21
// ---------------------------------------------------------------------------
import { useState, useEffect, useRef, useCallback, useMemo } from 'react'
import toast from 'react-hot-toast'
import { Network, RefreshCw, Loader2, ZoomIn, ZoomOut, Maximize2, Info, X } from 'lucide-react'
import { clsx } from 'clsx'
import { kgGetGraph } from '../services/api.js'

// ””€ Force simulation (pure JS, no d3) ””””””””””””””””””””””””€
// Function: runSimulation
function runSimulation(nodes, edges, width, height, onTick, onDone) {
  if (nodes.length === 0) { onDone([]); return () => {} }

  // Index nodes
  const idx = {}
  nodes.forEach((n, i) => { idx[n.id] = i })

  // Initial random positions
  const pos = nodes.map(() => ({
    x: width * 0.2 + Math.random() * width * 0.6,
    y: height * 0.2 + Math.random() * height * 0.6,
    vx: 0,
    vy: 0,
  }))

  let alpha = 1
  let rafId = null

  // Function: tick
  function tick() {
    const REPULSION     = 2800
    const LINK_DIST     = 90
    const LINK_STRENGTH = 0.25
    const CENTER_STR    = 0.015
    const DAMPING       = 0.82
    const cx = width / 2
    const cy = height / 2

    // Center gravity
    for (let i = 0; i < pos.length; i++) {
      pos[i].vx += (cx - pos[i].x) * CENTER_STR * alpha
      pos[i].vy += (cy - pos[i].y) * CENTER_STR * alpha
    }

    // Repulsion (Barnes-Hut approximation skipped; O(n²) fine for ‰¤300 nodes)
    for (let i = 0; i < pos.length; i++) {
      for (let j = i + 1; j < pos.length; j++) {
        const dx = pos[i].x - pos[j].x
        const dy = pos[i].y - pos[j].y
        const dist2 = dx * dx + dy * dy || 0.01
        const dist  = Math.sqrt(dist2)
        const force = (REPULSION * alpha) / dist2
        const fx    = (dx / dist) * force
        const fy    = (dy / dist) * force
        pos[i].vx += fx; pos[i].vy += fy
        pos[j].vx -= fx; pos[j].vy -= fy
      }
    }

    // Link attraction
    for (const e of edges) {
      const si = idx[e.source]
      const ti = idx[e.target]
      if (si === undefined || ti === undefined) continue
      const dx   = pos[ti].x - pos[si].x
      const dy   = pos[ti].y - pos[si].y
      const dist = Math.sqrt(dx * dx + dy * dy) || 1
      const diff = (dist - LINK_DIST) * LINK_STRENGTH * alpha
      const fx   = (dx / dist) * diff
      const fy   = (dy / dist) * diff
      pos[si].vx += fx; pos[si].vy += fy
      pos[ti].vx -= fx; pos[ti].vy -= fy
    }

    // Integrate + damp + clamp
    for (let i = 0; i < pos.length; i++) {
      pos[i].vx *= DAMPING
      pos[i].vy *= DAMPING
      pos[i].x  = Math.max(20, Math.min(width - 20,  pos[i].x + pos[i].vx))
      pos[i].y  = Math.max(20, Math.min(height - 20, pos[i].y + pos[i].vy))
    }

    alpha *= 0.99
    onTick(pos.map((p, i) => ({ id: nodes[i].id, x: p.x, y: p.y })))

    if (alpha > 0.01) {
      rafId = requestAnimationFrame(tick)
    } else {
      onDone(pos.map((p, i) => ({ id: nodes[i].id, x: p.x, y: p.y })))
    }
  }

  rafId = requestAnimationFrame(tick)
  return () => { if (rafId) cancelAnimationFrame(rafId) }
}

// ””€ Legend config ””””””””””””””””””””””””””””””””””””””””””””€
const LEGEND = [
  { type: 'document', color: '#3b82f6', label: 'Document' },
  { type: 'incident', color: '#f59e0b', label: 'Incident' },
  { type: 'solman',   color: '#10b981', label: 'SolManID' },
  { type: 'delivery', color: '#8b5cf6', label: 'Delivery Doc' },
  { type: 'category', color: '#ef4444', label: 'Category' },
]

// ””€ Main component ”””””””””””””””””””””””””””””””””””””””””””€
// Function: KnowledgeGraphPage
export default function KnowledgeGraphPage() {
  const containerRef = useRef(null)
  const [dimensions, setDimensions]   = useState({ w: 800, h: 600 })
  const [graphData, setGraphData]     = useState(null)
  const [positions, setPositions]     = useState([])
  const [loading, setLoading]         = useState(false)
  const [simRunning, setSimRunning]   = useState(false)
  const [selectedNode, setSelectedNode] = useState(null)
  const [transform, setTransform]     = useState({ x: 0, y: 0, scale: 1 })
  const [dragging, setDragging]       = useState(false)
  const [dragStart, setDragStart]     = useState(null)
  const [filter, setFilter]           = useState('all')
  const stopSimRef = useRef(null)

  // Track SVG container size
  useEffect(() => {
    const el = containerRef.current
    if (!el) return
    const ro = new ResizeObserver(() => {
      const r = el.getBoundingClientRect()
      setDimensions({ w: r.width || 800, h: r.height || 600 })
    })
    ro.observe(el)
    return () => ro.disconnect()
  }, [])

  const fetchGraph = useCallback(async () => {
    setLoading(true)
    if (stopSimRef.current) { stopSimRef.current(); stopSimRef.current = null }
    try {
      const { data } = await kgGetGraph()
      setGraphData(data)
      setPositions([])
      setSelectedNode(null)
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to load knowledge graph')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { fetchGraph() }, [fetchGraph])

  // Start simulation when data + dimensions are ready
  useEffect(() => {
    if (!graphData?.nodes?.length || !dimensions.w) return
    if (stopSimRef.current) stopSimRef.current()

    setSimRunning(true)
    const stop = runSimulation(
      graphData.nodes,
      graphData.edges,
      dimensions.w,
      dimensions.h,
      (pts) => setPositions(pts),
      (pts) => { setPositions(pts); setSimRunning(false) },
    )
    stopSimRef.current = stop
    return () => stop()
  }, [graphData, dimensions])

  // Build position lookup map
  const posMap = useMemo(() => {
    const m = {}
    positions.forEach((p) => { m[p.id] = p })
    return m
  }, [positions])

  // Filtered nodes
  const visibleNodes = useMemo(() => {
    if (!graphData?.nodes) return []
    return filter === 'all' ? graphData.nodes : graphData.nodes.filter((n) => n.type === filter)
  }, [graphData, filter])

  const visibleNodeIds = useMemo(() => new Set(visibleNodes.map((n) => n.id)), [visibleNodes])

  const visibleEdges = useMemo(() => {
    if (!graphData?.edges) return []
    return graphData.edges.filter((e) => visibleNodeIds.has(e.source) && visibleNodeIds.has(e.target))
  }, [graphData, visibleNodeIds])

  // Pan handlers
  // Function: handleMouseDown
  const handleMouseDown = (e) => {
    if (e.button !== 0) return
    setDragging(true)
    setDragStart({ x: e.clientX - transform.x, y: e.clientY - transform.y })
  }
  // Function: handleMouseMove
  const handleMouseMove = (e) => {
    if (!dragging || !dragStart) return
    setTransform((p) => ({ ...p, x: e.clientX - dragStart.x, y: e.clientY - dragStart.y }))
  }
  // Function: handleMouseUp
  const handleMouseUp = () => { setDragging(false); setDragStart(null) }

  // Zoom
  // Function: handleWheel
  const handleWheel = (e) => {
    e.preventDefault()
    const factor = e.deltaY < 0 ? 1.1 : 0.9
    setTransform((p) => ({ ...p, scale: Math.max(0.2, Math.min(4, p.scale * factor)) }))
  }
  // Function: zoom
  const zoom = (delta) =>
    setTransform((p) => ({ ...p, scale: Math.max(0.2, Math.min(4, p.scale + delta)) }))
  // Function: resetView
  const resetView = () => setTransform({ x: 0, y: 0, scale: 1 })

  const stats = graphData?.stats || {}

  return (
    <div className="flex-1 flex flex-col overflow-hidden bg-gray-950">

      {/* ””€ Toolbar ””””””””””””””””””””””””””””””””””””””””””””€ */}
      <div className="flex-shrink-0 flex items-center gap-3 px-4 py-3 border-b border-white/10 bg-gray-900">
        <Network size={18} className="text-blue-400" />
        <h1 className="text-sm font-bold text-white">Knowledge Graph</h1>
        {simRunning && (
          <span className="flex items-center gap-1.5 text-xs text-blue-400">
            <Loader2 size={12} className="animate-spin" /> Simulating€¦
          </span>
        )}

        {/* Stats pills */}
        <div className="flex items-center gap-2 ml-2">
          {[
            { label: 'Docs',       val: stats.documents,  color: 'bg-blue-600/20 text-blue-400' },
            { label: 'Incidents',  val: stats.incidents,  color: 'bg-amber-600/20 text-amber-400' },
            { label: 'SolMan',     val: stats.solman_refs, color: 'bg-emerald-600/20 text-emerald-400' },
            { label: 'Categories', val: stats.categories,  color: 'bg-red-600/20 text-red-400' },
          ].filter((s) => s.val > 0).map((s) => (
            <span key={s.label} className={clsx('text-[11px] px-2 py-0.5 rounded-full font-medium', s.color)}>
              {s.val} {s.label}
            </span>
          ))}
        </div>

        {/* Filter */}
        <div className="ml-auto flex items-center gap-2">
          <span className="text-xs text-gray-500">Filter:</span>
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="text-xs bg-gray-800 border border-white/10 text-white rounded-lg px-2 py-1 focus:outline-none"
          >
            <option value="all">All types</option>
            {LEGEND.map((l) => (
              <option key={l.type} value={l.type}>{l.label}</option>
            ))}
          </select>

          {/* Zoom controls */}
          <button onClick={() => zoom(0.15)} className="p-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-gray-400 hover:text-white transition">
            <ZoomIn size={14} />
          </button>
          <button onClick={() => zoom(-0.15)} className="p-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-gray-400 hover:text-white transition">
            <ZoomOut size={14} />
          </button>
          <button onClick={resetView} className="p-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-gray-400 hover:text-white transition" title="Reset view">
            <Maximize2 size={14} />
          </button>
          <button
            onClick={fetchGraph}
            disabled={loading}
            className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white text-xs font-medium transition"
          >
            <RefreshCw size={12} className={loading ? 'animate-spin' : ''} />
            Refresh
          </button>
        </div>
      </div>

      <div className="flex flex-1 overflow-hidden">

        {/* ””€ SVG canvas ”””””””””””””””””””””””””””””””””””””€ */}
        <div
          ref={containerRef}
          className={clsx('flex-1 overflow-hidden relative', dragging ? 'cursor-grabbing' : 'cursor-grab')}
          onMouseDown={handleMouseDown}
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
          onMouseLeave={handleMouseUp}
          onWheel={handleWheel}
        >
          {loading && (
            <div className="absolute inset-0 flex items-center justify-center bg-gray-950/70 z-10">
              <Loader2 size={28} className="animate-spin text-blue-400" />
            </div>
          )}

          {!loading && graphData?.nodes?.length === 0 && (
            <div className="absolute inset-0 flex flex-col items-center justify-center text-gray-600">
              <Network size={40} className="mb-3" />
              <p className="font-medium text-gray-400">No graph data available</p>
              <p className="text-sm mt-1">Index some documents first via Admin or Data Sources.</p>
            </div>
          )}

          <svg
            width={dimensions.w}
            height={dimensions.h}
            className="absolute inset-0"
            style={{ background: 'transparent' }}
          >
            <g transform={`translate(${transform.x},${transform.y}) scale(${transform.scale})`}>

              {/* Edges */}
              {visibleEdges.map((e, i) => {
                const sp = posMap[e.source]
                const tp = posMap[e.target]
                if (!sp || !tp) return null
                return (
                  <line
                    key={i}
                    x1={sp.x} y1={sp.y}
                    x2={tp.x} y2={tp.y}
                    stroke="rgba(255,255,255,0.08)"
                    strokeWidth={1}
                  />
                )
              })}

              {/* Nodes */}
              {visibleNodes.map((node) => {
                const p = posMap[node.id]
                if (!p) return null
                const isSelected = selectedNode?.id === node.id
                const r = node.size || 10
                return (
                  <g
                    key={node.id}
                    transform={`translate(${p.x},${p.y})`}
                    onClick={(ev) => { ev.stopPropagation(); setSelectedNode(node) }}
                    style={{ cursor: 'pointer' }}
                  >
                    <circle
                      r={r}
                      fill={node.color}
                      fillOpacity={0.85}
                      stroke={isSelected ? 'white' : node.color}
                      strokeWidth={isSelected ? 2.5 : 0.5}
                      strokeOpacity={isSelected ? 1 : 0.4}
                    />
                    {r >= 10 && (
                      <text
                        textAnchor="middle"
                        dy={r + 11}
                        fontSize={9}
                        fill="rgba(255,255,255,0.65)"
                        pointerEvents="none"
                        style={{ userSelect: 'none' }}
                      >
                        {node.label.length > 18 ? node.label.slice(0, 17) + '€¦' : node.label}
                      </text>
                    )}
                  </g>
                )
              })}
            </g>
          </svg>
        </div>

        {/* ””€ Right panel ””””””””””””””””””””””””””””””””””””€ */}
        <div className="w-56 flex-shrink-0 bg-gray-900 border-l border-white/10 flex flex-col">

          {/* Legend */}
          <div className="p-4 border-b border-white/10">
            <p className="text-[11px] font-semibold text-gray-500 uppercase tracking-wider mb-2">Legend</p>
            {LEGEND.map((l) => (
              <div key={l.type} className="flex items-center gap-2 mb-1.5">
                <span
                  className="w-3 h-3 rounded-full shrink-0"
                  style={{ background: l.color }}
                />
                <span className="text-xs text-gray-400">{l.label}</span>
              </div>
            ))}
          </div>

          {/* Summary stats */}
          <div className="p-4 border-b border-white/10">
            <p className="text-[11px] font-semibold text-gray-500 uppercase tracking-wider mb-2">Summary</p>
            <dl className="space-y-1 text-xs">
              <div className="flex justify-between"><dt className="text-gray-500">Nodes</dt><dd className="text-white font-mono">{stats.total_nodes || 0}</dd></div>
              <div className="flex justify-between"><dt className="text-gray-500">Edges</dt><dd className="text-white font-mono">{stats.total_edges || 0}</dd></div>
            </dl>
          </div>

          {/* Selected node details */}
          <div className="flex-1 overflow-y-auto p-4">
            {selectedNode ? (
              <div>
                <div className="flex items-center justify-between mb-2">
                  <p className="text-[11px] font-semibold text-gray-500 uppercase tracking-wider">Selected</p>
                  <button onClick={() => setSelectedNode(null)} className="text-gray-600 hover:text-gray-300">
                    <X size={13} />
                  </button>
                </div>
                <div
                  className="w-5 h-5 rounded-full mb-2"
                  style={{ background: selectedNode.color }}
                />
                <p className="text-xs font-semibold text-white break-all mb-1">{selectedNode.label}</p>
                <p className="text-[11px] text-gray-500 capitalize mb-3">{selectedNode.type}</p>

                {/* Connected nodes */}
                {(() => {
                  const connections = (graphData?.edges || [])
                    .filter((e) => e.source === selectedNode.id || e.target === selectedNode.id)
                    .map((e) => {
                      const otherId = e.source === selectedNode.id ? e.target : e.source
                      return graphData.nodes.find((n) => n.id === otherId)
                    })
                    .filter(Boolean)

                  if (connections.length === 0) return null
                  return (
                    <div>
                      <p className="text-[10px] font-semibold text-gray-600 uppercase tracking-wide mb-1.5">
                        Connections ({connections.length})
                      </p>
                      <div className="space-y-1">
                        {connections.slice(0, 10).map((n) => (
                          <button
                            key={n.id}
                            onClick={() => setSelectedNode(n)}
                            className="w-full flex items-center gap-2 text-left rounded-lg px-2 py-1.5 hover:bg-white/5 transition"
                          >
                            <span
                              className="w-2.5 h-2.5 rounded-full shrink-0"
                              style={{ background: n.color }}
                            />
                            <span className="text-xs text-gray-400 truncate">{n.label}</span>
                          </button>
                        ))}
                        {connections.length > 10 && (
                          <p className="text-[10px] text-gray-600 px-2">
                            +{connections.length - 10} more
                          </p>
                        )}
                      </div>
                    </div>
                  )
                })()}
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center h-full text-gray-600 text-center px-3">
                <Info size={22} className="mb-2 opacity-40" />
                <p className="text-xs">Click a node to see details and connections.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
