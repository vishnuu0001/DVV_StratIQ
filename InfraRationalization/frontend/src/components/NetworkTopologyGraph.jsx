// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: * NetworkTopologyGraph.jsx
// Date: 2025-07-18
// ---------------------------------------------------------------------------
/**
 * NetworkTopologyGraph.jsx
 * Rack-based network topology visualizer.
 *
 * Layout:
 *  - One rack cabinet per subnet, arranged horizontally
 *  - Each server = one 1U row with OS colour strip, name, IP, util bar, risk dot
 *  - Internet node → Gateway diamonds → Rack connector lines
 *  - Compact and scales to many servers without overlapping nodes
 *  - Pan (drag) + Zoom (wheel), hover tooltip, click-to-select detail card
 */
import { useMemo, useState, useRef, useCallback } from 'react'

// ─── Rack layout constants ─────────────────────────────────────────────────────
const RACK_W     = 230   // rack cabinet width (px in SVG units)
const RACK_GAP   = 28    // horizontal gap between racks
const RU_H       = 36    // height per 1U server row
const RACK_HDR   = 52    // rack header (subnet label + server count)
const RACK_FTR   = 14    // rack footer (mounting rail detail)
const CANVAS_PAD = 48    // left/right canvas padding
const INET_R     = 22    // internet cloud node radius
const GW_S       = 14    // gateway diamond half-size
const TOP_Y      = 36    // top margin before internet node

// ─── Colour palettes ──────────────────────────────────────────────────────────
const RISK_COLOR = {
  critical: '#ef4444',
  high:     '#f97316',
  medium:   '#f59e0b',
  low:      '#22c55e',
  none:     '#3b82f6',
}

const OS_COLOR = {
  windows: '#3b82f6',
  linux:   '#10b981',
  unknown: '#6366f1',
}

const UTIL_COLOR = {
  underutilized: '#22c55e',
  moderate:      '#f59e0b',
  utilized:      '#ef4444',
  unknown:       '#475569',
}

// ─── Data builder — produces racks[] + gatewayIPs[] ───────────────────────────
// Function: buildRacks
function buildRacks(networkTopology, servers, intelligenceData) {
  const subnets   = networkTopology?.subnets    || []
  const allIfaces = networkTopology?.interfaces || []

  // Risk lookup: component name/IP → highest-priority failure prediction
  const riskByComp = {}
  for (const f of intelligenceData?.predicted_failures || []) {
    const comp = (f.component || '').split('/')[0]
    const cur  = riskByComp[comp]
    const pri  = { critical: 4, high: 3, medium: 2, low: 1, none: 0 }
    if (!cur || (pri[f.probability] || 0) > (pri[cur.probability] || 0)) {
      riskByComp[comp] = f
    }
  }

  // Server lookups by IP and name
  const srvByIp   = {}
  const srvByName = {}
  for (const s of servers) {
    const ip   = s.ip_address || s.ip || ''
    const name = s.server_name || s.name || ip
    if (ip)   srvByIp[ip]   = s
    if (name) srvByName[name] = s
  }

  // Build subnet list from topology, interfaces, or server list
  let subnetList = subnets
  if (!subnetList.length && allIfaces.length) {
    const snMap = {}
    for (const iface of allIfaces) {
      const key = iface.subnet || 'unknown'
      if (!snMap[key]) snMap[key] = { subnet: key, gateway: iface.gateway || '', hosts: [] }
      snMap[key].hosts.push({ server_name: iface.server, ip: iface.ip, mac: iface.mac || '' })
    }
    subnetList = Object.values(snMap)
  }
  if (!subnetList.length && servers.length) {
    subnetList = [{
      subnet:  'Local Network',
      gateway: '',
      hosts:   servers.map(s => ({
        server_name: s.server_name || s.name || s.ip_address || '',
        ip:          s.ip_address  || s.ip   || '',
        mac:         '',
      })),
    }]
  }

  // Unique gateway IPs
  const gwSet = new Set()
  for (const sn of subnetList) if (sn.gateway) gwSet.add(sn.gateway)
  const gatewayIPs = [...gwSet]

  // Build per-subnet rack objects
  const racks = subnetList.map(sn => ({
    subnet:  sn.subnet,
    gateway: sn.gateway || '',
    units:   (sn.hosts || []).map(h => {
      const srv   = srvByName[h.server_name] || srvByIp[h.ip] || {}
      const os    = (srv.os_family || srv.os || '').toLowerCase()
      const osFam = os.includes('win') ? 'windows' : os.includes('linux') ? 'linux' : 'unknown'
      const risk  = riskByComp[h.server_name] || riskByComp[h.ip] || null
      return {
        id:        h.ip || h.server_name,
        label:     h.server_name || h.ip || '—',
        ip:        h.ip || '',
        mac:       h.mac || '',
        os:        srv.os_name || srv.os || '',
        os_fam:    osFam,
        cpu:       srv.cpu_cores,
        ram:       srv.ram_gb,
        util:      srv.utilization_band || srv.utilization || 'unknown',
        workloads: srv.workloads || [],
        risk:      risk?.probability || 'none',
        risk_type: risk?.failure_type || '',
        subnet:    sn.subnet,
        gateway:   sn.gateway || '',
      }
    }),
  }))

  return { racks, gatewayIPs }
}

// ─── 1U Server row ────────────────────────────────────────────────────────────
// Function: RackUnit
function RackUnit({ unit, y, selected, onHover, onClick }) {
  const osC    = OS_COLOR[unit.os_fam]   || '#6366f1'
  const riskC  = RISK_COLOR[unit.risk]   || RISK_COLOR.none
  const utilC  = UTIL_COLOR[unit.util]   || UTIL_COLOR.unknown
  const isCrit = unit.risk === 'critical' || unit.risk === 'high'

  const ROW_W  = RACK_W - 20   // inner row width (10px margin each side)
  const STRIP  = 7             // left OS-colour strip width
  const LX     = STRIP + 8    // label start x
  const MAX_UTIL_W = 22        // utilisation bar max width

  const utilW =
    unit.util === 'utilized'      ? MAX_UTIL_W :
    unit.util === 'moderate'      ? Math.round(MAX_UTIL_W * 0.55) :
    unit.util === 'underutilized' ? Math.round(MAX_UTIL_W * 0.25) : 0

  return (
    <g transform={`translate(10, ${y})`}
       onMouseEnter={(e) => onHover(unit, e)}
       onMouseLeave={() => onHover(null)}
       onClick={() => onClick(unit)}
       className="cursor-pointer">

      {/* Row background */}
      <rect x={0} y={1} width={ROW_W} height={RU_H - 3}
            rx={3}
            fill={selected ? '#1e2535' : '#111827'}
            stroke={selected ? osC : '#1e293b'}
            strokeWidth={selected ? 1.5 : 1} />

      {/* OS colour strip (left edge) */}
      <rect x={0} y={1} width={STRIP} height={RU_H - 3} rx={3} fill={osC} opacity={0.85} />
      <rect x={3} y={1} width={STRIP - 3} height={RU_H - 3} fill={osC} opacity={0.85} />

      {/* Server name */}
      <text x={LX} y={16} fontSize={9.5} fill="#e2e8f0" fontFamily="monospace"
            style={{ pointerEvents: 'none', userSelect: 'none' }}>
        {unit.label.length > 18 ? unit.label.slice(0, 17) + '…' : unit.label}
      </text>

      {/* IP address */}
      <text x={LX} y={27} fontSize={7.5} fill="#4b5563" fontFamily="monospace"
            style={{ pointerEvents: 'none', userSelect: 'none' }}>
        {unit.ip}
      </text>

      {/* Utilisation bar (right area) */}
      <rect x={ROW_W - MAX_UTIL_W - 22} y={10} width={MAX_UTIL_W} height={4}
            rx={2} fill="#1e293b" />
      {utilW > 0 && (
        <rect x={ROW_W - MAX_UTIL_W - 22} y={10} width={utilW} height={4}
              rx={2} fill={utilC} opacity={0.85} />
      )}

      {/* Risk indicator dot */}
      {unit.risk !== 'none' && (
        <circle cx={ROW_W - 9} cy={(RU_H - 2) / 2} r={5}
                fill={riskC} stroke="#0f1117" strokeWidth={1.5}>
          {isCrit && (
            <animate attributeName="opacity" values="1;0.3;1"
                     dur="1.4s" repeatCount="indefinite" />
          )}
        </circle>
      )}
    </g>
  )
}

// ─── Rack cabinet ─────────────────────────────────────────────────────────────
// Function: Rack
function Rack({ rack, x, y, selectedId, onHover, onClick }) {
  const rackH = RACK_HDR + rack.units.length * RU_H + RACK_FTR

  return (
    <g transform={`translate(${x}, ${y})`}>

      {/* Outer shell */}
      <rect x={0} y={0} width={RACK_W} height={rackH}
            rx={6} fill="#0c0f1a" stroke="#374151" strokeWidth={2} />

      {/* Header bar */}
      <rect x={0} y={0} width={RACK_W} height={RACK_HDR}
            rx={6} fill="#111827" />
      <rect x={0} y={RACK_HDR - 1} width={RACK_W} height={2} fill="#1e293b" />

      {/* Mounting screws — cosmetic detail */}
      {[10, RACK_W - 10].map(sx => (
        <circle key={sx} cx={sx} cy={RACK_HDR / 2} r={4.5}
                fill="#0c0f1a" stroke="#374151" strokeWidth={1.5} />
      ))}

      {/* Subnet label */}
      <text x={RACK_W / 2} y={20} textAnchor="middle" fontSize={9.5}
            fill="#94a3b8" fontFamily="monospace"
            style={{ userSelect: 'none' }}>
        {rack.subnet.length > 28 ? rack.subnet.slice(0, 27) + '…' : rack.subnet}
      </text>

      {/* Server count + gateway sub-label */}
      <text x={RACK_W / 2} y={34} textAnchor="middle" fontSize={7.5}
            fill="#374151" fontFamily="monospace"
            style={{ userSelect: 'none' }}>
        {rack.units.length}U{rack.gateway ? `  ·  GW ${rack.gateway}` : ''}
      </text>

      {/* Unit index numbers (left gutter) */}
      {rack.units.map((_, i) => (
        <text key={i}
              x={7} y={RACK_HDR + i * RU_H + RU_H / 2 + 4}
              fontSize={6.5} fill="#1e293b" textAnchor="middle"
              fontFamily="monospace" style={{ userSelect: 'none' }}>
          {String(i + 1).padStart(2, '0')}
        </text>
      ))}

      {/* Server rows */}
      {rack.units.map((u, i) => (
        <RackUnit
          key={u.id}
          unit={u}
          y={RACK_HDR + i * RU_H}
          selected={selectedId === u.id}
          onHover={onHover}
          onClick={onClick}
        />
      ))}

      {/* Footer rail */}
      <rect x={0} y={rackH - RACK_FTR} width={RACK_W} height={RACK_FTR}
            fill="#111827" />
      <rect x={0} y={rackH - RACK_FTR} width={RACK_W} height={1} fill="#1e293b" />
      {[18, 36, RACK_W - 36, RACK_W - 18].map(sx => (
        <rect key={sx} x={sx - 7} y={rackH - RACK_FTR + 3}
              width={14} height={7} rx={2} fill="#1e293b" />
      ))}
    </g>
  )
}

// ─── Tooltip ──────────────────────────────────────────────────────────────────
// Function: Tooltip
function Tooltip({ node }) {
  if (!node) return null
  const lines = []
  if (node.ip)                              lines.push(['IP',      node.ip])
  if (node.mac)                             lines.push(['MAC',     node.mac])
  if (node.os)                              lines.push(['OS',      node.os])
  if (node.cpu)                             lines.push(['CPU',     `${node.cpu} cores`])
  if (node.ram)                             lines.push(['RAM',     `${node.ram} GB`])
  if (node.util && node.util !== 'unknown') lines.push(['Util',    node.util])
  if (node.risk && node.risk !== 'none')    lines.push(['Risk',    node.risk])
  if (node.subnet)                          lines.push(['Subnet',  node.subnet])
  if (node.risk_type)                       lines.push(['Failure', node.risk_type.replace(/_/g, ' ')])

  return (
    <div className="pointer-events-none fixed z-50 max-w-xs"
         style={{ left: node._sx + 16, top: node._sy - 8 }}>
      <div className="bg-surface-card border border-surface-border rounded-xl shadow-2xl p-3 text-xs">
        <p className="font-semibold text-white mb-1.5 font-mono">{node.label}</p>
        {lines.map(([k, v]) => (
          <div key={k} className="flex gap-2">
            <span className="text-slate-500 w-14 shrink-0">{k}</span>
            <span className="text-slate-300 font-mono truncate">{v}</span>
          </div>
        ))}
        {node.workloads?.length > 0 && (
          <div className="flex gap-2 mt-1">
            <span className="text-slate-500 w-14 shrink-0">Services</span>
            <span className="text-emerald-300 truncate">
              {node.workloads.map(w => typeof w === 'string' ? w : w.name || '').join(', ')}
            </span>
          </div>
        )}
      </div>
    </div>
  )
}

// ─── Main export ──────────────────────────────────────────────────────────────
// Function: NetworkTopologyGraph
export default function NetworkTopologyGraph({ networkTopology, servers, intelligenceData }) {
  const [transform, setTransform] = useState({ tx: 0, ty: 0, scale: 1 })
  const [hoveredNode, setHoveredNode] = useState(null)
  const [selectedNode, setSelectedNode] = useState(null)
  const isDragging = useRef(false)
  const dragOrigin = useRef({ x: 0, y: 0 })
  const svgRef     = useRef(null)

  const { racks, gatewayIPs } = useMemo(
    () => buildRacks(networkTopology, servers || [], intelligenceData),
    [networkTopology, servers, intelligenceData],
  )

  // ── Layout calculations ────────────────────────────────────────────────────
  const numRacks   = racks.length
  const maxUnits   = racks.reduce((m, r) => Math.max(m, r.units.length), 0)
  const maxRackH   = RACK_HDR + maxUnits * RU_H + RACK_FTR

  const CANVAS_W   = Math.max(860, numRacks * (RACK_W + RACK_GAP) + CANVAS_PAD * 2)
  const INET_Y     = TOP_Y + INET_R
  const GW_Y       = INET_Y + INET_R + 24
  const RACK_Y     = GW_Y + GW_S * 2 + 28
  const CANVAS_H   = RACK_Y + maxRackH + 40

  // Centre racks horizontally
  const totalW     = numRacks * RACK_W + Math.max(0, numRacks - 1) * RACK_GAP
  const startX     = (CANVAS_W - totalW) / 2
  const rackXs     = racks.map((_, i) => startX + i * (RACK_W + RACK_GAP))

  // Gateway x-positions (spread evenly under internet node)
  const gwSpacing  = Math.max(110, totalW / Math.max(1, gatewayIPs.length))
  const gwXs       = gatewayIPs.map((_, i) =>
    CANVAS_W / 2 + (i - (gatewayIPs.length - 1) / 2) * gwSpacing
  )

  // ── Pan / Zoom ─────────────────────────────────────────────────────────────
  const handleMouseDown = useCallback((e) => {
    if (e.button !== 0) return
    isDragging.current = true
    dragOrigin.current = { x: e.clientX - transform.tx, y: e.clientY - transform.ty }
    e.currentTarget.style.cursor = 'grabbing'
  }, [transform])

  const handleMouseMove = useCallback((e) => {
    if (!isDragging.current) return
    setTransform(prev => ({
      ...prev,
      tx: e.clientX - dragOrigin.current.x,
      ty: e.clientY - dragOrigin.current.y,
    }))
  }, [])

  const handleMouseUp = useCallback((e) => {
    isDragging.current = false
    if (e.currentTarget) e.currentTarget.style.cursor = 'grab'
  }, [])

  const handleWheel = useCallback((e) => {
    e.preventDefault()
    const f = e.deltaY < 0 ? 1.12 : 0.9
    setTransform(prev => ({
      ...prev,
      scale: Math.min(3.5, Math.max(0.2, prev.scale * f)),
    }))
  }, [])

  // Function: handleReset
  const handleReset = () => setTransform({ tx: 0, ty: 0, scale: 1 })

  const handleHover = useCallback((unit, e) => {
    if (!unit) { setHoveredNode(null); return }
    setHoveredNode({ ...unit, _sx: e.clientX, _sy: e.clientY })
  }, [])

  const totalServers = racks.reduce((n, r) => n + r.units.length, 0)

  const canvasH = Math.min(640, Math.max(400, RACK_Y + maxRackH + 60))

  return (
    <div className="relative w-full select-none">

      {/* Legend */}
      <div className="absolute top-3 left-3 z-10 bg-surface-card/90 border border-surface-border
                      rounded-xl p-3 text-xs space-y-1 backdrop-blur">
        <p className="text-slate-400 font-semibold mb-1.5">Risk Level</p>
        {[
          { c: RISK_COLOR.critical, l: 'Critical' },
          { c: RISK_COLOR.high,     l: 'High' },
          { c: RISK_COLOR.medium,   l: 'Medium' },
          { c: RISK_COLOR.low,      l: 'Low' },
          { c: RISK_COLOR.none,     l: 'No Risk' },
        ].map(({ c, l }) => (
          <div key={l} className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full shrink-0" style={{ background: c }} />
            <span className="text-slate-300">{l}</span>
          </div>
        ))}
        <hr className="border-surface-border my-1.5" />
        <div className="flex items-center gap-2">
          <span className="w-3 h-3 rounded-sm shrink-0" style={{ background: OS_COLOR.linux }} />
          <span className="text-slate-300">Linux</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-3 h-3 rounded-sm shrink-0" style={{ background: OS_COLOR.windows }} />
          <span className="text-slate-300">Windows</span>
        </div>
        <hr className="border-surface-border my-1.5" />
        <div className="flex items-center gap-2">
          <div className="w-6 h-0 border-t-2 border-blue-500 shrink-0" />
          <span className="text-slate-300">L3 Route</span>
        </div>
      </div>

      {/* Reset button */}
      <div className="absolute top-3 right-3 z-10">
        <button onClick={handleReset}
                className="px-2.5 py-1.5 rounded-lg bg-surface-card border border-surface-border
                           text-xs text-slate-300 hover:text-white hover:bg-surface-hover transition-colors">
          Reset View
        </button>
      </div>

      {/* Status bar */}
      <div className="absolute bottom-3 left-3 z-10 text-xs text-slate-500 font-mono">
        {totalServers} server{totalServers !== 1 ? 's' : ''} ·{' '}
        {racks.length} rack{racks.length !== 1 ? 's' : ''} ·{' '}
        {gatewayIPs.length} gateway{gatewayIPs.length !== 1 ? 's' : ''}
      </div>

      {/* SVG Canvas */}
      <div className="rounded-xl overflow-hidden border border-surface-border bg-surface"
           style={{ height: canvasH }}>
        <svg
          ref={svgRef}
          width="100%" height="100%"
          viewBox={`0 0 ${CANVAS_W} ${CANVAS_H}`}
          style={{ cursor: 'grab' }}
          onMouseDown={handleMouseDown}
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
          onMouseLeave={handleMouseUp}
          onWheel={handleWheel}
        >
          <defs>
            <pattern id="rack-grid" width={40} height={40} patternUnits="userSpaceOnUse">
              <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#12151f" strokeWidth={0.6} />
            </pattern>
          </defs>
          <rect width={CANVAS_W} height={CANVAS_H} fill="url(#rack-grid)" />

          <g transform={`translate(${transform.tx},${transform.ty}) scale(${transform.scale})`}>

            {/* ── Internet node ── */}
            <g transform={`translate(${CANVAS_W / 2}, ${INET_Y})`}>
              <circle r={INET_R} fill="#0c0f1a" stroke="#3b82f6" strokeWidth={2} />
              <circle r={INET_R - 4} fill="none" stroke="#3b82f630"
                      strokeWidth={1} strokeDasharray="4 3" />
              <text textAnchor="middle" dy={4} fontSize={12} fill="#93c5fd">🌐</text>
              <text textAnchor="middle" dy={INET_R + 14} fontSize={9}
                    fill="#475569" fontFamily="monospace">Internet</text>
            </g>

            {/* ── Gateway diamonds ── */}
            {gatewayIPs.map((gwIp, i) => {
              const gwX = gwXs[i]
              const gwY = GW_Y + GW_S
              return (
                <g key={gwIp} transform={`translate(${gwX}, ${gwY})`}>
                  {/* Internet → gateway line */}
                  <line
                    x1={CANVAS_W / 2 - gwX} y1={INET_Y + INET_R - gwY}
                    x2={0} y2={0}
                    stroke="#6366f1" strokeWidth={1.5} strokeDasharray="6 3" opacity={0.5}
                  />
                  <polygon
                    points={`0,${-GW_S} ${GW_S},0 0,${GW_S} ${-GW_S},0`}
                    fill="#111827" stroke="#f59e0b" strokeWidth={1.5}
                  />
                  <text textAnchor="middle" dy={GW_S + 13} fontSize={8}
                        fill="#94a3b8" fontFamily="monospace">{gwIp}</text>
                </g>
              )
            })}

            {/* ── Gateway → Rack connector lines ── */}
            {racks.map((rack, ri) => {
              const rx  = rackXs[ri] + RACK_W / 2
              const ry  = RACK_Y
              const gwIdx = gatewayIPs.indexOf(rack.gateway)

              if (gwIdx < 0 && gatewayIPs.length === 0) {
                // No gateways at all — connect directly from internet
                return (
                  <line key={`conn_${ri}`}
                        x1={CANVAS_W / 2} y1={INET_Y + INET_R}
                        x2={rx} y2={ry}
                        stroke="#3b82f6" strokeWidth={1.2}
                        strokeDasharray="6 3" opacity={0.35} />
                )
              }
              if (gwIdx < 0) return null
              const gwX = gwXs[gwIdx]
              const gwY = GW_Y + GW_S * 2
              return (
                <line key={`conn_${ri}`}
                      x1={gwX} y1={gwY}
                      x2={rx}  y2={ry}
                      stroke="#3b82f6" strokeWidth={1.2}
                      strokeDasharray="5 3" opacity={0.4} />
              )
            })}

            {/* ── Racks ── */}
            {racks.map((rack, ri) => (
              <Rack
                key={rack.subnet + ri}
                rack={rack}
                x={rackXs[ri]}
                y={RACK_Y}
                selectedId={selectedNode?.id}
                onHover={handleHover}
                onClick={(unit) =>
                  setSelectedNode(prev => prev?.id === unit.id ? null : unit)
                }
              />
            ))}

          </g>
        </svg>
      </div>

      {/* Tooltip */}
      <Tooltip node={hoveredNode} />

      {/* Selected server detail card */}
      {selectedNode && (
        <div className="mt-3 p-4 rounded-xl bg-surface-card border border-surface-border text-xs">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <span className="inline-block w-3 h-3 rounded-sm"
                    style={{ background: OS_COLOR[selectedNode.os_fam] || '#6366f1' }} />
              <p className="font-semibold text-white font-mono text-sm">{selectedNode.label}</p>
            </div>
            <button onClick={() => setSelectedNode(null)}
                    className="text-slate-500 hover:text-white text-lg leading-none">×</button>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-x-6 gap-y-1.5">
            {[
              ['IP',          selectedNode.ip],
              ['MAC',         selectedNode.mac],
              ['OS',          selectedNode.os],
              ['CPU Cores',   selectedNode.cpu],
              ['RAM',         selectedNode.ram ? `${selectedNode.ram} GB` : null],
              ['Utilization', selectedNode.util],
              ['Subnet',      selectedNode.subnet],
              ['Gateway',     selectedNode.gateway],
            ].filter(([, v]) => v).map(([k, v]) => (
              <div key={k}>
                <span className="text-slate-500">{k}: </span>
                <span className="text-slate-200 font-mono">{v}</span>
              </div>
            ))}
          </div>
          {selectedNode.workloads?.length > 0 && (
            <div className="mt-2 flex flex-wrap gap-1.5">
              {selectedNode.workloads.map((w, i) => (
                <span key={i} className="px-2 py-0.5 rounded-full bg-emerald-950/60
                                         text-emerald-300 text-xs">
                  {typeof w === 'string' ? w : w.name || ''}
                </span>
              ))}
            </div>
          )}
          {selectedNode.risk !== 'none' && (
            <div className="mt-2 p-2 rounded-lg bg-red-950/20 border border-red-800/30">
              <span className="text-red-400 font-medium capitalize">{selectedNode.risk} risk: </span>
              <span className="text-slate-400">{selectedNode.risk_type.replace(/_/g, ' ')}</span>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
