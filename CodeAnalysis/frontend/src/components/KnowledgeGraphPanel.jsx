// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: CodeAnalysis — frontend/src/components (KnowledgeGraphPanel.jsx)
// Date: 2026-05-21
// ---------------------------------------------------------------------------
import { useEffect, useRef, useState, useCallback, useMemo } from 'react'
import { Network, Loader2, AlertCircle, ZoomIn, ZoomOut, RotateCcw, Search, X } from 'lucide-react'
import { getKnowledgeGraph } from '../api/client.js'

// ── Visual config ─────────────────────────────────────────────────────────────
const TYPE_COLOR  = { module: '#6366f1', class: '#3b82f6', function: '#06b6d4' }
const TYPE_RADIUS = { module: 16, class: 11, function: 7 }

const EDGE_STROKE = {
  contains: 'rgba(71,85,105,0.58)',
  imports:  'rgba(180,83,9,0.72)',
  inherits: 'rgba(109,40,217,0.76)',
  calls:    'rgba(13,148,136,0.68)',
}
const EDGE_SOLID = { contains: '#64748b', imports: '#eab308', inherits: '#a855f7', calls: '#14b8a6' }

const LAYER_COLOR = {
  controller: '#f97316', service: '#22c55e', repository: '#f59e0b',
  model: '#3b82f6', utility: '#8b5cf6', test: '#ec4899', other: '#6b7280',
}
// ── Client-side layer classification (mirrors backend _LAYER_HINTS) ─────────
const _LAYER_HINTS = {
  controller: ['controller', 'handler', 'endpoint', 'route', 'rest', 'view', 'servlet'],
  service:    ['service', 'manager', 'orchestrat', 'usecase', 'business', 'facade'],
  repository: ['repository', 'repo', 'dao', 'store', 'database', 'db', 'jpa', 'crud'],
  model:      ['model', 'entity', 'dto', 'domain', 'schema', 'pojo', 'record', 'mapper'],
  utility:    ['util', 'helper', 'common', 'shared', 'config', 'constant', 'utils', 'exception', 'security', 'filter', 'interceptor'],
  test:       ['test', 'spec', '__test__', 'mock', 'fixture'],
}
// Function: classifyLayer
function classifyLayer(filePath) {
  const lower = filePath.toLowerCase()
  for (const [layer, hints] of Object.entries(_LAYER_HINTS)) {
    if (hints.some(h => lower.includes(h))) return layer
  }
  return 'other'
}
// ── Per-layer architectural intelligence ─────────────────────────────────────
const LAYER_INTEL = {
  controller: {
    desc: 'HTTP entry points — receive requests and delegate to the service layer.',
    rec:  (s) => s.byType.function > 25
      ? 'Large controller surface detected. Consider splitting by domain boundary to reduce per-controller responsibility.'
      : 'Controller surface is within healthy bounds.',
    advice: 'Controllers should only depend on Services — direct Repository calls indicate a layering violation.',
  },
  service: {
    desc: 'Business logic orchestration — coordinates use-cases and data access.',
    rec:  (s) => Object.values(s.outbound).reduce((a, b) => a + b, 0) > 25
      ? 'High outbound coupling detected. Some services may be doing too much — consider Facade or split patterns.'
      : 'Service coupling looks manageable.',
    advice: 'Services should depend on Repositories and Models only, not on Controllers.',
  },
  repository: {
    desc: 'Data access layer — queries, ORM mappings, persistence operations.',
    rec:  (s) => (s.inbound.controller || 0) > 0
      ? 'Repositories accessed directly from Controllers — route all data access through the Service layer.'
      : 'Good pattern: Repositories consumed only through the Service layer.',
    advice: 'Repositories should only depend on Models/Entities — never on Services or Controllers.',
  },
  model: {
    desc: 'Domain entities, DTOs, schemas — the data contract of the application.',
    rec:  (s) => s.byType.class > 30
      ? `${s.byType.class} model classes detected. Verify DTO/Entity separation to avoid mixing persistence and transport concerns.`
      : 'Model layer size looks appropriate.',
    advice: 'Models should be dependency-free — importing from Service or Controller layers is an anti-pattern.',
  },
  utility: {
    desc: 'Shared infrastructure — helpers, configs, exceptions, security filters.',
    rec:  (s) => Object.keys(s.inbound).length >= 3
      ? 'Utility layer depended on by 3+ layers. Document public contracts carefully to prevent hidden cross-layer coupling.'
      : 'Utility usage is moderate — no cross-cutting concerns detected.',
    advice: 'Utility classes should not import from business layers (Service/Controller).',
  },
  test: {
    desc: 'Test suite — unit, integration, and mock-based verification.',
    rec:  (s, tot) => {
      const prod  = tot - s.total
      const ratio = prod > 0 ? s.total / prod : 0
      return ratio < 0.25
        ? `Test-to-production ratio is ${(ratio * 100).toFixed(0)}%. Consider increasing test coverage.`
        : `Test-to-production ratio is ${(ratio * 100).toFixed(0)}% — healthy range.`
    },
    advice: 'Test files should never be imported by production code.',
  },
  other: {
    desc: 'Files without a clear architectural classification.',
    rec:  () => 'Review these files and assign them to appropriate layers to improve maintainability and traceability.',
    advice: 'Adopt naming conventions (e.g. *Controller, *Service, *Repository) so files are auto-classified.',
  },
}

// ── Force constants ───────────────────────────────────────────────────────────
const REPULSION = 1800
const SPRING_K  = 0.055
const REST_LEN  = 80
const GRAVITY   = 0.009
const DAMPING   = 0.82
const MAX_TICKS = 320
// Per-type display budget — ensures all 3 types are always present → edges exist
const BUDGET = { module: 60, class: 70, function: 70 }

// Function: drawEdges
function drawEdges(ctx, edges, nodeMap) {
  for (const e of edges) {
    const s = nodeMap[e.from], t = nodeMap[e.to]
    if (!s || !t) continue
    ctx.beginPath(); ctx.moveTo(s.x, s.y); ctx.lineTo(t.x, t.y)
    ctx.strokeStyle = EDGE_STROKE[e.type] || 'rgba(100,116,139,0.35)'
    ctx.lineWidth   = e.type === 'inherits' ? 1.8 : 1.0
    ctx.setLineDash(e.type === 'imports' ? [5, 3] : [])
    ctx.stroke()
  }
  ctx.setLineDash([])
}

// Function: drawNode
// Function: drawNodeCircle
function drawNodeCircle(ctx, nd, r, col, isSel, isHov) {
  if (isSel || isHov) {
    ctx.beginPath(); ctx.arc(nd.x, nd.y, r + 6, 0, Math.PI * 2)
    ctx.fillStyle = col + '30'; ctx.fill()
  }
  ctx.beginPath(); ctx.arc(nd.x, nd.y, r, 0, Math.PI * 2)
  ctx.fillStyle   = isSel ? '#fff' : col
  ctx.strokeStyle = isSel ? col : col + 'bb'
  ctx.lineWidth   = isSel ? 2.5 : 1.2
  ctx.fill(); ctx.stroke()
}

// Function: drawNodeLabel
function drawNodeLabel(ctx, nd, r, col, z, isSel) {
  // Show labels for modules/classes always; functions only when zoomed in enough
  if (nd.type === 'function' && z <= 0.8) return
  const fs = Math.max(8, Math.min(13, 11 / z))
  ctx.font      = `${nd.type === 'module' ? '600 ' : ''}${fs}px Inter,system-ui,sans-serif`
  ctx.textAlign = 'center'
  ctx.fillStyle = isSel ? col : (nd.type === 'module' ? '#172554' : '#334155')
  const lbl = nd.label.length > 20 ? nd.label.slice(0, 18) + '…' : nd.label
  ctx.fillText(lbl, nd.x, nd.y + r + 12 / z)
}

// Function: drawNode
function drawNode(ctx, nd, z, selId, hovId) {
  const r     = TYPE_RADIUS[nd.type] || 8
  const col   = TYPE_COLOR[nd.type]  || '#64748b'
  const isSel = nd.id === selId
  const isHov = nd.id === hovId

  drawNodeCircle(ctx, nd, r, col, isSel, isHov)
  drawNodeLabel(ctx, nd, r, col, z, isSel)
}

// Function: drawNodes
function drawNodes(ctx, nodes, z, selId, hovId) {
  for (const nd of nodes) drawNode(ctx, nd, z, selId, hovId)
}

// Function: KnowledgeGraphPanel
export default function KnowledgeGraphPanel({ jobId }) {
  // ── Refs (mutable, not React state) ────────────────────────────────────────
  const canvasRef  = useRef(null)
  const nodesRef   = useRef([])
  const edgesRef   = useRef([])
  const nodeMapRef = useRef({})
  const rafRef     = useRef(null)
  const panRef     = useRef({ x: 0, y: 0 })
  const zoomRef    = useRef(1)
  const dragRef    = useRef({ active: false, x: 0, y: 0, moved: false })
  const tickRef    = useRef(0)

  // ── React state ─────────────────────────────────────────────────────────────
  const hovIdRef = useRef(null)   // keep in ref so render loop reads latest without re-render

  const [data, setData]           = useState(null)
  const [loading, setLoading]     = useState(false)
  const [error, setError]         = useState(null)
  const [selected, setSelected]   = useState(null)
  const [hoverId, setHoverId]     = useState(null)
  const [dispCnt, setDispCnt]     = useState({ nodes: 0, edges: 0 })
  const [typeVis, setTypeVis]     = useState(() => new Set(['module','class','function']))
  const [edgeVis, setEdgeVis]     = useState(() => new Set(['contains','imports','inherits','calls']))
  const [layerFlt, setLayerFlt]   = useState(null)
  const [query, setQuery]         = useState('')

  // ── Fetch ──────────────────────────────────────────────────────────────────
  const load = useCallback(async () => {
    if (!jobId) return
    setLoading(true); setError(null)
    try {
      const raw = await getKnowledgeGraph(jobId, 400)
      // Re-classify layers client-side — server may have stale classification
      const nodes = raw.nodes.map(n => ({ ...n, layer: classifyLayer(n.file) }))
      const clusters = {}
      nodes.forEach(n => { (clusters[n.layer] = clusters[n.layer] || []).push(n.id) })
      setData({ ...raw, nodes, clusters })
    } catch (e) {
      setError(e.response?.data?.detail || e.response?.data?.error || e.message)
    } finally {
      setLoading(false)
    }
  }, [jobId])

  // ── Auto-load on mount / jobId change ─────────────────────────────────────
  useEffect(() => { load() }, [load])

  // ── Build simulation ───────────────────────────────────────────────────────
  useEffect(() => {
    if (!data) return
    if (rafRef.current) cancelAnimationFrame(rafRef.current)

    // Filter
    let display = data.nodes.filter(n =>
      typeVis.has(n.type) &&
      (!layerFlt || n.layer === layerFlt) &&
      (!query || n.label.toLowerCase().includes(query.toLowerCase()) ||
                 n.id.toLowerCase().includes(query.toLowerCase()))
    )

    // Balanced cap per type — ensures classes + functions are always present so edges exist
    const byType = { module: [], class: [], function: [] }
    display.forEach(n => byType[n.type]?.push(n))
    display = [
      ...byType.module.slice(0, BUDGET.module),
      ...byType.class.slice(0, BUDGET.class),
      ...byType.function.slice(0, BUDGET.function),
    ]

    // Place nodes on a circle — read CSS size from canvas
    const canvas = canvasRef.current
    const W = canvas ? canvas.clientWidth  : 880
    const H = canvas ? canvas.clientHeight : 560
    const cx = W / 2, cy = H / 2
    const total = display.length || 1
    const r0    = Math.min(W, H) * 0.33

    const simNodes = display.map((nd, i) => ({
      ...nd,
      x: cx + r0 * Math.cos((2 * Math.PI * i) / total) + (Math.random() - 0.5) * 28,
      y: cy + r0 * Math.sin((2 * Math.PI * i) / total) + (Math.random() - 0.5) * 28,
      vx: 0, vy: 0,
    }))
    const nodeMap = {}
    simNodes.forEach(n => { nodeMap[n.id] = n })

    // Keep edges where BOTH endpoints are in the displayed set
    const vis = new Set(simNodes.map(n => n.id))
    const simEdges = data.edges
      .filter(e => vis.has(e.from) && vis.has(e.to) && edgeVis.has(e.type))
      .slice(0, 3000)

    nodesRef.current   = simNodes
    edgesRef.current   = simEdges
    nodeMapRef.current = nodeMap
    tickRef.current    = 0
    panRef.current     = { x: 0, y: 0 }
    zoomRef.current    = 1
    setDispCnt({ nodes: simNodes.length, edges: simEdges.length })
    setSelected(null)

    startLoop()
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [data, typeVis, edgeVis, layerFlt, query])

  // ── Force loop ─────────────────────────────────────────────────────────────
  // Function: startLoop
  const startLoop = () => {
    const canvas = canvasRef.current
    if (!canvas) return
    // Function: step
    const step = () => {
      if (tickRef.current < MAX_TICKS) { applyForces(); tickRef.current++ }
      render(canvas)
      rafRef.current = requestAnimationFrame(step)
    }
    rafRef.current = requestAnimationFrame(step)
  }

  // Function: applyForces
  const applyForces = () => {
    const ns = nodesRef.current
    const es = edgesRef.current
    const nm = nodeMapRef.current
    const canvas = canvasRef.current
    const cx = (canvas ? canvas.clientWidth  : 880) / 2
    const cy = (canvas ? canvas.clientHeight : 560) / 2

    // O(n²) repulsion — cap to first 150 nodes for performance
    const cap = Math.min(ns.length, 150)
    for (let i = 0; i < cap; i++) {
      for (let j = i + 1; j < cap; j++) {
        const a = ns[i], b = ns[j]
        const dx = b.x - a.x || 0.01
        const dy = b.y - a.y || 0.01
        const d2 = dx*dx + dy*dy + 0.1
        const d  = Math.sqrt(d2)
        const f  = REPULSION / d2
        a.vx -= f*dx/d; a.vy -= f*dy/d
        b.vx += f*dx/d; b.vy += f*dy/d
      }
    }

    for (const e of es) {
      const s = nm[e.from], t = nm[e.to]
      if (!s || !t) continue
      const dx = t.x - s.x, dy = t.y - s.y
      const d  = Math.sqrt(dx*dx + dy*dy) + 0.1
      const f  = SPRING_K * (d - REST_LEN)
      s.vx += f*dx/d; s.vy += f*dy/d
      t.vx -= f*dx/d; t.vy -= f*dy/d
    }

    for (const n of ns) {
      n.vx += (cx - n.x) * GRAVITY
      n.vy += (cy - n.y) * GRAVITY
      n.vx *= DAMPING; n.vy *= DAMPING
      n.x  += n.vx;    n.y  += n.vy
    }
  }

  // ── Canvas render — DPR-aware ──────────────────────────────────────────────
  // Function: render
  const render = (canvas) => {
    const dpr = window.devicePixelRatio || 1
    const csW = canvas.clientWidth
    const csH = canvas.clientHeight
    // Sync physical pixel buffer to CSS size × dpr
    if (canvas.width !== Math.round(csW * dpr) || canvas.height !== Math.round(csH * dpr)) {
      canvas.width  = Math.round(csW * dpr)
      canvas.height = Math.round(csH * dpr)
    }
    const ctx = canvas.getContext('2d')
    const z   = zoomRef.current
    const p   = panRef.current
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    ctx.save()
    // Scale by dpr so drawing coords stay in CSS-pixel space
    ctx.scale(dpr, dpr)
    ctx.translate(p.x, p.y)
    ctx.scale(z, z)

    drawEdges(ctx, edgesRef.current, nodeMapRef.current)

    const selId = selected?.id
    const hovId = hovIdRef.current
    drawNodes(ctx, nodesRef.current, z, selId, hovId)
    ctx.restore()
  }

  // ── Non-passive wheel zoom (React's synthetic onWheel is passive by default) ─
  useEffect(() => {
    const canvas = canvasRef.current; if (!canvas) return
    // Function: handler
    const handler = (e) => {
      e.preventDefault()
      zoomRef.current = Math.max(0.1, Math.min(6, zoomRef.current * (e.deltaY < 0 ? 1.12 : 0.89)))
    }
    canvas.addEventListener('wheel', handler, { passive: false })
    return () => canvas.removeEventListener('wheel', handler)
  }, [])

  // ── Resize canvas via ResizeObserver ───────────────────────────────────────
  useEffect(() => {
    const canvas = canvasRef.current; if (!canvas) return
    // Initial size set is deferred one frame to ensure CSS layout is done
    const dpr = window.devicePixelRatio || 1
    // Function: sync
    const sync = () => {
      canvas.width  = Math.round(canvas.clientWidth  * dpr)
      canvas.height = Math.round(canvas.clientHeight * dpr)
    }
    const obs = new ResizeObserver(sync)
    obs.observe(canvas)
    requestAnimationFrame(sync)
    return () => obs.disconnect()
  }, [])

  useEffect(() => () => { if (rafRef.current) cancelAnimationFrame(rafRef.current) }, [])

  // ── Mouse → world ─────────────────────────────────────────────────────────
  // Function: toWorld
  const toWorld = (canvas, ex, ey) => ({
    x: (ex - canvas.getBoundingClientRect().left - panRef.current.x) / zoomRef.current,
    y: (ey - canvas.getBoundingClientRect().top  - panRef.current.y) / zoomRef.current,
  })

  // Function: hitTest
  const hitTest = (wx, wy) =>
    nodesRef.current.find(n => {
      const r = (TYPE_RADIUS[n.type] || 8) + 5
      return (n.x - wx)**2 + (n.y - wy)**2 <= r*r
    }) ?? null

  const onMouseDown = e => {
    dragRef.current = { active: true, x: e.clientX, y: e.clientY, moved: false }
  }
  const onMouseMove = e => {
    const canvas = canvasRef.current; if (!canvas) return
    if (dragRef.current.active) {
      const dx = e.clientX - dragRef.current.x
      const dy = e.clientY - dragRef.current.y
      if (Math.abs(dx) + Math.abs(dy) > 2) dragRef.current.moved = true
      panRef.current = { x: panRef.current.x + dx, y: panRef.current.y + dy }
      dragRef.current = { ...dragRef.current, x: e.clientX, y: e.clientY }
      return
    }
    const { x: wx, y: wy } = toWorld(canvas, e.clientX, e.clientY)
    const hit = hitTest(wx, wy)
    hovIdRef.current = hit?.id ?? null
    setHoverId(hit?.id ?? null)
    canvas.style.cursor = hit ? 'pointer' : 'grab'
  }
  const onMouseUp = e => {
    const moved = dragRef.current.moved
    dragRef.current = { active: false, x: 0, y: 0, moved: false }
    if (!moved) {
      const canvas = canvasRef.current; if (!canvas) return
      const { x: wx, y: wy } = toWorld(canvas, e.clientX, e.clientY)
      setSelected(hitTest(wx, wy))
    }
  }

  // ── Computed ───────────────────────────────────────────────────────────────
  const stats  = data?.stats
  const layers = Object.keys(LAYER_COLOR)

  // Function: toggleSet
  const toggleSet = (setter, key) =>
    setter(prev => { const s = new Set(prev); s.has(key) ? s.delete(key) : s.add(key); return s })

  const connections = selected
    ? edgesRef.current
        .filter(e => e.from === selected.id || e.to === selected.id)
        .slice(0, 14)
        .map(e => ({
          dir: e.from === selected.id ? '→' : '←',
          type: e.type,
          id: e.from === selected.id ? e.to : e.from,
        }))
    : []

  // ── Layer statistics (cross-layer relationship analysis) ──────────────────
  const layerStats = useMemo(() => {
    if (!data || !layerFlt) return null
    const layerNodes = data.nodes.filter(n => n.layer === layerFlt)
    const layerIds   = new Set(layerNodes.map(n => n.id))

    // O(n) id→layer lookup
    const idToLayer = {}
    data.nodes.forEach(n => { idToLayer[n.id] = n.layer })

    const byType   = { module: 0, class: 0, function: 0 }
    layerNodes.forEach(n => { if (n.type in byType) byType[n.type]++ })

    const outbound = {}  // this layer → other layer
    const inbound  = {}  // other layer → this layer
    const connCount = {} // node id → total connections
    data.edges.forEach(e => {
      const fl = idToLayer[e.from], tl = idToLayer[e.to]
      if (!fl || !tl) return
      if (fl === layerFlt && tl !== layerFlt) outbound[tl] = (outbound[tl] || 0) + 1
      if (tl === layerFlt && fl !== layerFlt) inbound[fl]  = (inbound[fl]  || 0) + 1
      if (layerIds.has(e.from)) connCount[e.from] = (connCount[e.from] || 0) + 1
      if (layerIds.has(e.to))   connCount[e.to]   = (connCount[e.to]   || 0) + 1
    })

    const topNodes = layerNodes
      .map(n => ({ ...n, connections: connCount[n.id] || 0 }))
      .sort((a, b) => b.connections - a.connections)
      .slice(0, 5)

    return { total: layerNodes.length, byType, outbound, inbound, topNodes }
  }, [data, layerFlt])

  // ── Render UI ──────────────────────────────────────────────────────────────
  return (
    <div className="ca-knowledge-graph space-y-4">

      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div>
          <h2 className="text-lg font-semibold text-blue-300 flex items-center gap-2">
            <Network size={18} className="text-brand-cyan" />
            Codebase Knowledge Graph
          </h2>
          <p className="text-xs text-blue-400 mt-0.5">
            Force-directed map of modules, classes and functions — scroll to zoom, drag to pan, click a node to inspect
          </p>
        </div>
        {!data && !loading && (
          <button onClick={load} className="btn-primary text-xs px-4 py-2 flex-shrink-0">
            Generate Graph
          </button>
        )}
        {data && (
          <button onClick={load} className="btn-secondary text-xs px-4 py-2 flex-shrink-0">
            Refresh
          </button>
        )}
      </div>

      {/* Loading */}
      {loading && (
        <div className="flex flex-col items-center justify-center py-24 gap-3 text-blue-400">
          <Loader2 size={32} className="animate-spin text-brand-cyan" />
          <p className="text-sm">Building knowledge graph — scanning source files…</p>
        </div>
      )}

      {/* Error */}
      {error && !loading && (
        <div className="flex items-center gap-3 p-4 rounded-xl bg-red-900/20 border border-red-700/40 text-red-400 text-sm">
          <AlertCircle size={16} className="flex-shrink-0" />
          <span className="flex-1">{error}</span>
          <button onClick={load} className="text-xs underline opacity-75 hover:opacity-100">Retry</button>
        </div>
      )}

      {/* Stats row */}
      {stats && (
        <div className="grid grid-cols-3 sm:grid-cols-6 gap-3">
          {[
            { label: 'Nodes',     val: stats.total_nodes },
            { label: 'Edges',     val: stats.total_edges },
            { label: 'Files',     val: stats.files_scanned },
            { label: 'Modules',   val: stats.node_types?.module   ?? 0, col: TYPE_COLOR.module },
            { label: 'Classes',   val: stats.node_types?.class    ?? 0, col: TYPE_COLOR.class },
            { label: 'Functions', val: stats.node_types?.function ?? 0, col: TYPE_COLOR.function },
          ].map(s => (
            <div key={s.label} className="bg-surface-card border border-surface-border rounded-xl px-3 py-3 text-center">
              <div className="text-xl font-bold" style={{ color: s.col || '#172554' }}>
                {(s.val ?? 0).toLocaleString()}
              </div>
              <div className="text-xs text-blue-400 mt-0.5">{s.label}</div>
            </div>
          ))}
        </div>
      )}

      {/* Main graph + sidebar */}
      {data && (
        <div className="flex gap-4">

          {/* ── Left sidebar ─────────────────────────────────────────────── */}
          <div className="w-52 flex-shrink-0 space-y-3">

            {/* Search */}
            <Panel label="Search">
              <div className="flex items-center gap-2 bg-gray-800 rounded-lg px-2.5">
                <Search size={11} className="text-blue-500 flex-shrink-0" />
                <input
                  value={query}
                  onChange={e => setQuery(e.target.value)}
                  placeholder="node name…"
                  className="bg-transparent text-xs text-blue-300 placeholder-gray-500 outline-none py-1.5 flex-1 min-w-0"
                />
                {query && (
                  <button onClick={() => setQuery('')}>
                    <X size={11} className="text-blue-500 hover:text-white" />
                  </button>
                )}
              </div>
            </Panel>

            {/* Node types */}
            <Panel label="Node Types">
              {['module','class','function'].map(t => (
                <ToggleRow
                  key={t}
                  label={t}
                  count={data.stats.node_types?.[t] ?? 0}
                  active={typeVis.has(t)}
                  color={TYPE_COLOR[t]}
                  onClick={() => toggleSet(setTypeVis, t)}
                />
              ))}
            </Panel>

            {/* Edge types */}
            <Panel label="Edge Types">
              {['contains','imports','inherits','calls'].map(t => (
                <ToggleRow
                  key={t}
                  label={t}
                  count={data.stats.edge_types?.[t] ?? 0}
                  active={edgeVis.has(t)}
                  color={EDGE_SOLID[t]}
                  onClick={() => toggleSet(setEdgeVis, t)}
                  dash={t === 'imports'}
                  isEdge
                />
              ))}
            </Panel>

            {/* Layer filter */}
            <Panel label="Layer">
              <button
                onClick={() => setLayerFlt(null)}
                className={`w-full text-left text-xs px-2 py-1 rounded transition-colors ${
                  !layerFlt ? 'bg-brand-cyan/20 text-brand-cyan' : 'text-blue-400 hover:text-white'
                }`}
              >
                All layers
              </button>
              {layers.map(l => (
                <button
                  key={l}
                  onClick={() => setLayerFlt(l === layerFlt ? null : l)}
                  className={`w-full flex items-center gap-2 text-left text-xs px-2 py-1 rounded transition-colors ${
                    layerFlt === l ? 'bg-orange-500/20 text-orange-400' : 'text-blue-400 hover:text-white'
                  }`}
                >
                  <span className="w-2 h-2 rounded-full flex-shrink-0"
                        style={{ background: LAYER_COLOR[l] || '#6b7280' }} />
                  {l}
                  <span className="ml-auto text-[10px] text-blue-500">
                    {data.clusters?.[l]?.length ?? data.nodes.filter(n => n.layer === l).length}
                  </span>
                </button>
              ))}
            </Panel>

            {/* View controls */}
            <Panel label="View">
              <div className="flex gap-1.5">
                {[
                  { icon: ZoomIn,    fn: () => { zoomRef.current = Math.min(5, zoomRef.current * 1.25) } },
                  { icon: ZoomOut,   fn: () => { zoomRef.current = Math.max(0.12, zoomRef.current * 0.8) } },
                  { icon: RotateCcw, fn: () => { panRef.current = { x:0, y:0 }; zoomRef.current = 1 } },
                ].map(({ icon: Icon, fn }, i) => (
                  <button key={i} onClick={fn}
                    className="flex-1 flex items-center justify-center bg-gray-800 hover:bg-gray-700
                               rounded-lg py-1.5 transition-colors">
                    <Icon size={13} className="text-blue-300" />
                  </button>
                ))}
              </div>
              <p className="text-[10px] text-blue-500 text-center mt-1">scroll=zoom · drag=pan</p>
            </Panel>

            {/* Legend */}
            <Panel label="Legend">
              <div className="space-y-1.5">
                {Object.entries(TYPE_COLOR).map(([t, c]) => (
                  <div key={t} className="flex items-center gap-2">
                    <span className="w-3 h-3 rounded-full" style={{background:c}} />
                    <span className="text-xs text-blue-400 capitalize">{t}</span>
                  </div>
                ))}
              </div>
              <div className="border-t border-surface-border pt-2 mt-2 space-y-1.5">
                {Object.entries(EDGE_SOLID).map(([t, c]) => (
                  <div key={t} className="flex items-center gap-2">
                    <svg width="18" height="8">
                      <line x1="0" y1="4" x2="18" y2="4" stroke={c} strokeWidth="1.5"
                            strokeDasharray={t === 'imports' ? '4,3' : 'none'} />
                    </svg>
                    <span className="text-xs text-blue-400 capitalize">{t}</span>
                  </div>
                ))}
              </div>
            </Panel>
          </div>

          {/* ── Canvas + detail ───────────────────────────────────────────── */}
          <div className="flex-1 flex flex-col gap-4 min-w-0">

            {/* Canvas */}
            <div className="ca-graph-canvas relative rounded-xl overflow-hidden border border-surface-border bg-gray-900"
                 style={{ height: '560px' }}>
              <canvas
                ref={canvasRef}
                style={{ width: '100%', height: '100%', display: 'block', cursor: 'grab' }}
                onMouseDown={onMouseDown}
                onMouseMove={onMouseMove}
                onMouseUp={onMouseUp}
                onMouseLeave={() => {
                  dragRef.current = { active: false, x: 0, y: 0, moved: false }
                  hovIdRef.current = null
                  setHoverId(null)
                }}
              />

              {/* Badge */}
              <div className="absolute top-3 right-3 text-[10px] text-blue-500 bg-gray-900/80
                              border border-surface-border rounded-lg px-2.5 py-1 pointer-events-none">
                {dispCnt.nodes} nodes · {dispCnt.edges} edges
              </div>

              {/* Hover tooltip */}
              {hoverId && (() => {
                const nd = nodeMapRef.current[hoverId]
                return nd ? (
                  <div className="ca-graph-tooltip absolute bottom-3 left-3 bg-gray-900/95 border border-surface-border
                                  rounded-xl px-3 py-2.5 text-xs space-y-0.5 pointer-events-none max-w-xs">
                    <div className="font-semibold text-blue-300 flex items-center gap-2">
                      <span className="w-2 h-2 rounded-full" style={{ background: TYPE_COLOR[nd.type] }} />
                      {nd.label}
                    </div>
                    <div className="text-blue-400">{nd.type} · {nd.layer} · {nd.language}</div>
                    <div className="text-blue-500 font-mono text-[10px] truncate">{nd.file}</div>
                  </div>
                ) : null
              })()}
            </div>

            {/* Selected node detail */}
            {selected && (
              <div className="bg-surface-card border border-surface-border rounded-xl p-4 space-y-3">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3 min-w-0">
                    <span className="w-3.5 h-3.5 rounded-full flex-shrink-0"
                          style={{ background: TYPE_COLOR[selected.type] || '#64748b' }} />
                    <div className="min-w-0">
                      <div className="text-sm font-semibold text-blue-300">{selected.label}</div>
                      <div className="text-[11px] text-blue-400 font-mono mt-0.5 truncate">{selected.id}</div>
                    </div>
                  </div>
                  <button onClick={() => setSelected(null)} className="flex-shrink-0 ml-2">
                    <X size={14} className="text-blue-500 hover:text-white" />
                  </button>
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs">
                  {[
                    { k: 'Type',     v: selected.type     },
                    { k: 'Layer',    v: selected.layer    },
                    { k: 'Language', v: selected.language },
                    { k: 'Line №',   v: selected.line     },
                  ].map(({ k, v }) => (
                    <div key={k} className="bg-gray-800 rounded-lg px-3 py-2">
                      <div className="text-blue-500 mb-0.5">{k}</div>
                      <div className="text-blue-300 font-medium capitalize">{v}</div>
                    </div>
                  ))}
                </div>

                <div className="text-[11px] text-blue-400 bg-gray-800 rounded-lg px-3 py-2 font-mono">
                  {selected.file}{selected.line ? `:${selected.line}` : ''}
                </div>

                {connections.length > 0 && (
                  <div>
                    <p className="text-xs text-blue-500 mb-2">Connections ({connections.length})</p>
                    <div className="flex flex-wrap gap-1.5">
                      {connections.map((c, i) => (
                        <button
                          key={i}
                          onClick={() => setSelected(nodeMapRef.current[c.id] ?? null)}
                          className="flex items-center gap-1.5 text-[11px] bg-gray-800 hover:bg-gray-700
                                     rounded-lg px-2.5 py-1 text-blue-300 transition-colors"
                        >
                          <span className="text-blue-500 font-mono">{c.dir}</span>
                          <span className="w-1.5 h-1.5 rounded-full"
                                style={{ background: EDGE_SOLID[c.type] }} />
                          <span className="text-blue-400 italic">{c.type}</span>
                          <span className="text-blue-300">{c.id.split('.').pop()}</span>
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}

      {/* ── Layer Inference Panel ─────────────────────────────────────────── */}
      {data && layerFlt && layerStats && (() => {
        const intel  = LAYER_INTEL[layerFlt] || LAYER_INTEL.other
        const totAll = data.stats?.total_nodes || 0
        return (
          <div className="bg-surface-card border border-surface-border rounded-xl p-5 space-y-4">
            {/* Header */}
            <div className="flex items-start gap-3">
              <span className="w-3 h-3 mt-1.5 rounded-full flex-shrink-0"
                    style={{ background: LAYER_COLOR[layerFlt] }} />
              <div className="flex-1 min-w-0">
                <h3 className="text-sm font-semibold text-blue-300 capitalize">
                  {layerFlt} Layer — Architectural Inference
                </h3>
                <p className="text-xs text-blue-500 mt-0.5">{intel.desc}</p>
              </div>
              <span className="text-xs text-blue-500 flex-shrink-0">{layerStats.total} nodes</span>
            </div>

            {/* Breakdown by type */}
            <div className="grid grid-cols-3 gap-3">
              {[
                ['Modules',   layerStats.byType.module,   TYPE_COLOR.module  ],
                ['Classes',   layerStats.byType.class,    TYPE_COLOR.class   ],
                ['Functions', layerStats.byType.function, TYPE_COLOR.function],
              ].map(([label, cnt, col]) => (
                <div key={label} className="bg-gray-800 rounded-lg px-3 py-2.5 text-center">
                  <div className="text-xl font-bold" style={{ color: col }}>{cnt}</div>
                  <div className="text-[11px] text-blue-400 mt-0.5">{label}</div>
                </div>
              ))}
            </div>

            {/* Cross-layer dependency map */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-xs font-medium text-blue-400 mb-2">⬆ Outbound dependencies</p>
                {Object.keys(layerStats.outbound).length === 0
                  ? <p className="text-xs text-blue-600 italic">No outbound deps</p>
                  : Object.entries(layerStats.outbound)
                      .sort((a, b) => b[1] - a[1])
                      .map(([lay, cnt]) => (
                        <div key={lay} className="flex items-center gap-2 text-xs py-0.5">
                          <span className="w-2 h-2 rounded-full flex-shrink-0"
                                style={{ background: LAYER_COLOR[lay] || '#6b7280' }} />
                          <span className="text-blue-300 capitalize">{lay}</span>
                          <span className="ml-auto text-blue-500">{cnt} edges</span>
                        </div>
                      ))}
              </div>
              <div>
                <p className="text-xs font-medium text-blue-400 mb-2">⬇ Inbound dependencies</p>
                {Object.keys(layerStats.inbound).length === 0
                  ? <p className="text-xs text-blue-600 italic">No inbound deps</p>
                  : Object.entries(layerStats.inbound)
                      .sort((a, b) => b[1] - a[1])
                      .map(([lay, cnt]) => (
                        <div key={lay} className="flex items-center gap-2 text-xs py-0.5">
                          <span className="w-2 h-2 rounded-full flex-shrink-0"
                                style={{ background: LAYER_COLOR[lay] || '#6b7280' }} />
                          <span className="text-blue-300 capitalize">{lay}</span>
                          <span className="ml-auto text-blue-500">{cnt} edges</span>
                        </div>
                      ))}
              </div>
            </div>

            {/* Top connected nodes — clickable to highlight */}
            {layerStats.topNodes.length > 0 && (
              <div>
                <p className="text-xs font-medium text-blue-400 mb-2">Top Connected Nodes</p>
                <div className="space-y-1">
                  {layerStats.topNodes.map((n, i) => (
                    <button
                      key={n.id}
                      onClick={() => setSelected(nodeMapRef.current[n.id] ?? null)}
                      className="w-full flex items-center gap-2 text-xs px-2 py-1.5 rounded-lg
                                 hover:bg-gray-800 transition-colors text-left"
                    >
                      <span className="text-blue-600 w-4 text-right flex-shrink-0">{i + 1}.</span>
                      <span className="w-2 h-2 rounded-full flex-shrink-0"
                            style={{ background: TYPE_COLOR[n.type] || '#64748b' }} />
                      <span className="text-blue-300 font-medium flex-1 truncate">{n.label}</span>
                      <span className="text-blue-500 capitalize italic">{n.type}</span>
                      <span className="text-blue-600 ml-2 flex-shrink-0">{n.connections} conn</span>
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Architectural inference box */}
            <div className="bg-indigo-950/40 border border-indigo-700/30 rounded-xl px-4 py-3 space-y-2">
              <p className="text-xs font-semibold text-indigo-300">Analysis</p>
              <p className="text-xs text-indigo-300">{intel.rec(layerStats, totAll)}</p>
              <p className="text-[11px] text-indigo-400/80 border-t border-indigo-700/20 pt-2">
                {intel.advice}
              </p>
            </div>
          </div>
        )
      })()}
    </div>
  )
}

// ── Sub-components ────────────────────────────────────────────────────────────

// Function: Panel
function Panel({ label, children }) {
  return (
    <div className="bg-surface-card border border-surface-border rounded-xl p-3 space-y-2">
      <p className="text-[10px] font-semibold text-blue-400 uppercase tracking-wider">{label}</p>
      {children}
    </div>
  )
}

// Function: ToggleRow
function ToggleRow({ label, count, active, color, onClick, dash, isEdge }) {
  return (
    <button onClick={onClick} className="w-full flex items-center gap-2 text-left">
      {isEdge ? (
        <svg width="18" height="10" className="flex-shrink-0">
          <line x1="0" y1="5" x2="18" y2="5"
                stroke={active ? color : '#374151'}
                strokeWidth="1.5"
                strokeDasharray={dash ? '4,3' : 'none'} />
        </svg>
      ) : (
        <span className="w-3 h-3 rounded-full flex-shrink-0 border"
              style={{ background: active ? color : 'transparent', borderColor: color }} />
      )}
      <span className={`text-xs capitalize ${active ? 'text-blue-200' : 'text-blue-500'}`}>{label}</span>
      <span className="ml-auto text-[10px] text-blue-500">{count}</span>
    </button>
  )
}
