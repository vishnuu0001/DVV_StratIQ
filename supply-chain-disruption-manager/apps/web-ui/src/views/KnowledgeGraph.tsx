// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: supply-chain-disruption-manager — apps/web-ui/src/views (KnowledgeGraph.tsx)
// Date: 2025-10-05
// ---------------------------------------------------------------------------
import React, { useEffect, useRef, useState, useCallback, useMemo } from 'react'
import * as d3 from 'd3'
import { Search, RefreshCw, Maximize2 } from 'lucide-react'
import { useKGGraph } from '../hooks/useKGGraph'
import { useAppStore } from '../store/useAppStore'
import type { KGEntity, KGEdge } from '../api/kg'

const DOMAIN_COLORS: Record<string, string> = {
  procurement: '#f59e0b',
  logistics: '#a78bfa',
  warehouse: '#06b6d4',
  production: '#10b981',
  people: '#f43f5e',
  system: '#facc15',
  default: '#8b9bac',
}

// Function: domainColor
function domainColor(domain: string): string {
  const key = domain.toLowerCase()
  return DOMAIN_COLORS[key] ?? DOMAIN_COLORS['default']
}

const EDGE_KINDS = ['flow', 'meta', 'owns', 'all'] as const
type EdgeKindFilter = typeof EDGE_KINDS[number]

const SEARCH_FIELDS = [
  { label: 'All Fields', value: 'all' },
  { label: 'Node ID', value: 'id' },
  { label: 'Kind', value: 'kind' },
  { label: 'Domain', value: 'domain' },
  { label: 'Supplier ID', value: 'supplier_id' },
  { label: 'Buyer ID', value: 'buyer_id' },
  { label: 'Status', value: 'status' },
] as const
type SearchField = typeof SEARCH_FIELDS[number]['value']

// Function: nodeMatchesSearch
function nodeMatchesSearch(
  n: { id: string; kind: string; domain: string; properties: Record<string, unknown> },
  q: string,
  field: SearchField
): boolean {
  const lower = q.toLowerCase()
  switch (field) {
    case 'id': return n.id.toLowerCase().includes(lower)
    case 'kind': return n.kind.toLowerCase().includes(lower)
    case 'domain': return n.domain.toLowerCase().includes(lower)
    case 'supplier_id': return String(n.properties.supplier_id ?? '').toLowerCase().includes(lower)
    case 'buyer_id': return String(n.properties.buyer_id ?? '').toLowerCase().includes(lower)
    case 'status': return String(n.properties.status ?? '').toLowerCase().includes(lower)
    default:
      return (
        n.id.toLowerCase().includes(lower) ||
        n.kind.toLowerCase().includes(lower) ||
        n.domain.toLowerCase().includes(lower) ||
        Object.values(n.properties).some(
          (v) => v != null && typeof v !== 'object' && String(v).toLowerCase().includes(lower)
        )
      )
  }
}

interface D3Node extends d3.SimulationNodeDatum {
  id: string
  kind: string
  domain: string
  properties: Record<string, unknown>
  degree?: number
}

interface D3Link {
  source: string | D3Node
  target: string | D3Node
  kind: string
  verb: string
}

// Function: toD3
function toD3(nodes: KGEntity[], edges: KGEdge[]): { nodes: D3Node[]; links: D3Link[] } {
  const nodeMap = new Map<string, D3Node>()
  nodes.forEach((n) => nodeMap.set(n.id, { ...n, degree: 0 }))
  const links: D3Link[] = edges
    .filter((e) => nodeMap.has(e.from) && nodeMap.has(e.to))
    .map((e) => {
      const src = nodeMap.get(e.from)!
      const tgt = nodeMap.get(e.to)!
      src.degree = (src.degree ?? 0) + 1
      tgt.degree = (tgt.degree ?? 0) + 1
      return { source: e.from, target: e.to, kind: e.kind, verb: e.verb }
    })
  return { nodes: Array.from(nodeMap.values()), links }
}

// Function: nodeRadius
function nodeRadius(d: D3Node): number {
  return Math.min(4 + (d.degree ?? 0) * 1.5, 18)
}

// Function: buildFilteredEdges
function buildFilteredEdges(edges: KGEdge[], edgeFilter: EdgeKindFilter): KGEdge[] {
  return edgeFilter === 'all' ? edges : edges.filter((e) => e.kind === edgeFilter)
}

// Function: computeConnectedIds
function computeConnectedIds(id: string, links: D3Link[]): Set<string> {
  const connectedIds = new Set<string>([id])
  links.forEach((l) => {
    const src = (l.source as D3Node).id
    const tgt = (l.target as D3Node).id
    if (src === id) connectedIds.add(tgt)
    if (tgt === id) connectedIds.add(src)
  })
  return connectedIds
}

// Function: highlightNode
function highlightNode(
  id: string,
  links: D3Link[],
  nodeGroup: d3.Selection<SVGGElement, D3Node, SVGGElement, unknown>,
  linkEl: d3.Selection<SVGLineElement, D3Link, SVGGElement, unknown>
) {
  const connectedIds = computeConnectedIds(id, links)

  nodeGroup.selectAll<SVGCircleElement, D3Node>('circle')
    .attr('opacity', (d) => connectedIds.has(d.id) ? 1 : 0.2)
    .attr('stroke-width', (d) => d.id === id ? 2.5 : 1.5)

  linkEl
    .attr('opacity', (l) => {
      const src = (l.source as D3Node).id
      const tgt = (l.target as D3Node).id
      return src === id || tgt === id ? 1 : 0.1
    })
    .attr('stroke', (l) => {
      const src = (l.source as D3Node).id
      const tgt = (l.target as D3Node).id
      return src === id || tgt === id ? '#38bdf8' : '#2a3440'
    })
}

// Function: applyBlastRadius
function applyBlastRadius(
  blastNodeIds: Set<string>,
  nodeGroup: d3.Selection<SVGGElement, D3Node, SVGGElement, unknown>,
  linkEl: d3.Selection<SVGLineElement, D3Link, SVGGElement, unknown>
) {
  const hasBlast = blastNodeIds.size > 0
  if (!hasBlast) {
    nodeGroup.selectAll<SVGCircleElement, D3Node>('circle').attr('opacity', 1)
    linkEl.attr('opacity', 0.7).attr('stroke', '#2a3440')
    return
  }
  nodeGroup.selectAll<SVGCircleElement, D3Node>('circle')
    .attr('opacity', (d) => blastNodeIds.has(d.id) ? 1 : 0.15)
    .attr('stroke', (d) => blastNodeIds.has(d.id) ? '#f59e0b' : domainColor(d.domain))
  linkEl.attr('opacity', (l) => {
    const src = (l.source as D3Node).id
    const tgt = (l.target as D3Node).id
    return blastNodeIds.has(src) && blastNodeIds.has(tgt) ? 0.9 : 0.1
  })
}

// Function: applySearchHighlight
function applySearchHighlight(
  nodes: D3Node[],
  nodeGroup: d3.Selection<SVGGElement, D3Node, SVGGElement, unknown>,
  search: string,
  searchField: SearchField
) {
  if (!search.trim()) return
  const matchedIds = new Set(
    nodes.filter((n) => nodeMatchesSearch(n, search, searchField)).map((n) => n.id)
  )
  nodeGroup.selectAll<SVGCircleElement, D3Node>('circle')
    .attr('stroke', (d) => matchedIds.has(d.id) ? '#38bdf8' : domainColor(d.domain))
    .attr('stroke-width', (d) => matchedIds.has(d.id) ? 3 : 1.5)
    .attr('opacity', (d) => matchedIds.has(d.id) ? 1 : 0.3)
}

// Function: appendArrowheadMarker
function appendArrowheadMarker(svg: d3.Selection<SVGSVGElement, unknown, null, undefined>) {
  svg.append('defs').append('marker')
    .attr('id', 'arrowhead')
    .attr('viewBox', '0 -5 10 10')
    .attr('refX', 18)
    .attr('refY', 0)
    .attr('markerWidth', 6)
    .attr('markerHeight', 6)
    .attr('orient', 'auto')
    .append('path')
    .attr('d', 'M0,-5L10,0L0,5')
    .attr('fill', '#3a4654')
}

// Function: attachZoom
function attachZoom(
  svg: d3.Selection<SVGSVGElement, unknown, null, undefined>,
  g: d3.Selection<SVGGElement, unknown, null, undefined>
) {
  const zoom = d3.zoom<SVGSVGElement, unknown>()
    .scaleExtent([0.1, 4])
    .on('zoom', (event: d3.D3ZoomEvent<SVGSVGElement, unknown>) => {
      g.attr('transform', event.transform.toString())
    })
  svg.call(zoom)
}

// Function: createForceSimulation
function createForceSimulation(
  nodes: D3Node[],
  links: D3Link[],
  width: number,
  height: number
): d3.Simulation<D3Node, D3Link> {
  return d3.forceSimulation<D3Node>(nodes)
    .force('link', d3.forceLink<D3Node, D3Link>(links).id((d) => d.id).distance(80))
    .force('charge', d3.forceManyBody().strength(-200))
    .force('center', d3.forceCenter(width / 2, height / 2))
    .force('collide', d3.forceCollide<D3Node>().radius((d) => nodeRadius(d) + 4))
}

// Function: attachNodeDrag
function attachNodeDrag(
  nodeGroup: d3.Selection<SVGGElement, D3Node, SVGGElement, unknown>,
  sim: d3.Simulation<D3Node, D3Link>
) {
  nodeGroup.call(
    d3.drag<SVGGElement, D3Node>()
      .on('start', (event, d) => {
        if (!event.active) sim.alphaTarget(0.3).restart()
        d.fx = d.x
        d.fy = d.y
      })
      .on('drag', (event, d) => {
        d.fx = event.x
        d.fy = event.y
      })
      .on('end', (event, d) => {
        if (!event.active) sim.alphaTarget(0)
        d.fx = null
        d.fy = null
      })
  )
}

interface NodeEventHandlers {
  tooltipRef: React.RefObject<HTMLDivElement>
  containerRef: React.RefObject<HTMLDivElement>
  selectNode: (n: { id: string; kind: string; domain: string; properties: Record<string, unknown> }) => void
  expandNode: (id: string) => Promise<unknown>
  onNodeClick: (id: string) => void
}

// Function: attachNodeInteractionEvents
function attachNodeInteractionEvents(
  nodeGroup: d3.Selection<SVGGElement, D3Node, SVGGElement, unknown>,
  handlers: NodeEventHandlers
) {
  const { tooltipRef, containerRef, selectNode, expandNode, onNodeClick } = handlers
  nodeGroup
    .on('click', (_event, d) => {
      selectNode({ id: d.id, kind: d.kind, domain: d.domain, properties: d.properties })
      void expandNode(d.id)
      onNodeClick(d.id)
    })
    .on('mouseover', (event: MouseEvent, d) => {
      if (tooltipRef.current) {
        tooltipRef.current.style.display = 'block'
        tooltipRef.current.style.left = `${(event as MouseEvent & { layerX: number }).layerX + 12}px`
        tooltipRef.current.style.top = `${(event as MouseEvent & { layerY: number }).layerY + 12}px`
        tooltipRef.current.textContent = `${d.id} (${d.kind}) · ${d.domain}`
      }
    })
    .on('mousemove', (event: MouseEvent) => {
      if (tooltipRef.current) {
        const rect = containerRef.current?.getBoundingClientRect()
        if (rect) {
          tooltipRef.current.style.left = `${event.clientX - rect.left + 12}px`
          tooltipRef.current.style.top = `${event.clientY - rect.top + 12}px`
        }
      }
    })
    .on('mouseout', () => {
      if (tooltipRef.current) tooltipRef.current.style.display = 'none'
    })
}

// Function: renderNodeShapes
function renderNodeShapes(nodeGroup: d3.Selection<SVGGElement, D3Node, SVGGElement, unknown>) {
  nodeGroup.append('circle')
    .attr('r', (d) => nodeRadius(d))
    .attr('fill', (d) => `${domainColor(d.domain)}22`)
    .attr('stroke', (d) => domainColor(d.domain))
    .attr('stroke-width', 1.5)

  nodeGroup.append('text')
    .attr('dy', (d) => nodeRadius(d) + 10)
    .attr('text-anchor', 'middle')
    .attr('font-size', '9px')
    .attr('fill', '#8b9bac')
    .text((d) => d.id.length > 12 ? d.id.slice(0, 12) + '…' : d.id)
}

// Function: attachSimulationTick
function attachSimulationTick(
  sim: d3.Simulation<D3Node, D3Link>,
  linkEl: d3.Selection<SVGLineElement, D3Link, SVGGElement, unknown>,
  nodeGroup: d3.Selection<SVGGElement, D3Node, SVGGElement, unknown>
) {
  sim.on('tick', () => {
    linkEl
      .attr('x1', (d) => (d.source as D3Node).x ?? 0)
      .attr('y1', (d) => (d.source as D3Node).y ?? 0)
      .attr('x2', (d) => (d.target as D3Node).x ?? 0)
      .attr('y2', (d) => (d.target as D3Node).y ?? 0)

    nodeGroup.attr('transform', (d) => `translate(${d.x ?? 0},${d.y ?? 0})`)
  })
}

const SEARCH_PLACEHOLDERS: Record<SearchField, string> = {
  all: 'Search nodes…',
  id: 'e.g. PO-10019…',
  kind: 'e.g. PurchaseOrder…',
  domain: 'e.g. procurement…',
  supplier_id: 'e.g. SUP-004…',
  buyer_id: 'e.g. USR-BUYER-001…',
  status: 'e.g. OPEN…',
}

// Function: KnowledgeGraph
export function KnowledgeGraph() {
  const { graph, loading, error, reload, expandNode } = useKGGraph()
  const { activeBlastRadius, selectedNode } = useAppStore()
  const selectNode = useAppStore((s) => s.selectNode)

  const svgRef = useRef<SVGSVGElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)
  const tooltipRef = useRef<HTMLDivElement>(null)
  const simRef = useRef<d3.Simulation<D3Node, D3Link> | null>(null)

  const [search, setSearch] = useState('')
  const [searchField, setSearchField] = useState<SearchField>('all')
  const [edgeFilter, setEdgeFilter] = useState<EdgeKindFilter>('all')

  const matchedCount = useMemo(() => {
    if (!search.trim()) return null
    return graph.nodes.filter((n) => nodeMatchesSearch(n, search, searchField)).length
  }, [search, searchField, graph.nodes])

  const blastNodeIds = useRef<Set<string>>(new Set())
  useEffect(() => {
    blastNodeIds.current = new Set(
      activeBlastRadius?.nodes.map((n) => n.id) ?? []
    )
  }, [activeBlastRadius])

  const renderGraph = useCallback(() => {
    if (!svgRef.current || !containerRef.current) return

    const { width, height } = containerRef.current.getBoundingClientRect()
    const svg = d3.select(svgRef.current)
    svg.selectAll('*').remove()
    svg.attr('width', width).attr('height', height)

    const filteredEdges = buildFilteredEdges(graph.edges, edgeFilter)
    const { nodes, links } = toD3(graph.nodes, filteredEdges)
    if (nodes.length === 0) return

    const g = svg.append('g')
    attachZoom(svg, g)
    appendArrowheadMarker(svg)

    const sim = createForceSimulation(nodes, links, width, height)
    simRef.current = sim

    const linkEl = g.append('g')
      .selectAll<SVGLineElement, D3Link>('line')
      .data(links)
      .join('line')
      .attr('class', 'kg-link')
      .attr('stroke', '#2a3440')
      .attr('stroke-width', 1.5)
      .attr('marker-end', 'url(#arrowhead)')
      .attr('opacity', 0.7)

    const nodeGroup = g.append('g')
      .selectAll<SVGGElement, D3Node>('g')
      .data(nodes)
      .join('g')
      .attr('class', 'kg-node')

    attachNodeDrag(nodeGroup, sim)
    attachNodeInteractionEvents(nodeGroup, {
      tooltipRef,
      containerRef,
      selectNode,
      expandNode,
      onNodeClick: (id) => highlightNode(id, links, nodeGroup, linkEl),
    })

    renderNodeShapes(nodeGroup)

    applySearchHighlight(nodes, nodeGroup, search, searchField)
    applyBlastRadius(blastNodeIds.current, nodeGroup, linkEl)

    attachSimulationTick(sim, linkEl, nodeGroup)

    return () => sim.stop()
  }, [graph, edgeFilter, search, searchField, expandNode, selectNode])

  useEffect(() => {
    const cleanup = renderGraph()
    return () => {
      cleanup?.()
      simRef.current?.stop()
    }
  }, [renderGraph])

  useEffect(() => {
    const obs = new ResizeObserver(() => renderGraph())
    if (containerRef.current) obs.observe(containerRef.current)
    return () => obs.disconnect()
  }, [renderGraph])

  return (
    <div className="flex flex-col h-full overflow-hidden">
      {/* Controls */}
      <div className="px-4 py-3 border-b border-border bg-surface flex items-center gap-3 flex-wrap">
        <div className="flex items-center gap-1.5">
          <div className="relative">
            <Search size={13} className="absolute left-2 top-1/2 -translate-y-1/2 text-text-3" />
            <input
              type="text"
              placeholder={SEARCH_PLACEHOLDERS[searchField]}
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="bg-surface-2 border border-border rounded pl-7 pr-3 py-1 text-xs text-text-2 placeholder-text-3 focus:outline-none focus:border-border-hi w-44"
            />
          </div>
          <select
            value={searchField}
            onChange={(e) => setSearchField(e.target.value as SearchField)}
            className="bg-surface-2 border border-border rounded px-2 py-1 text-xs text-text-2 focus:outline-none focus:border-border-hi cursor-pointer"
          >
            {SEARCH_FIELDS.map((f) => (
              <option key={f.value} value={f.value}>{f.label}</option>
            ))}
          </select>
          {matchedCount !== null && (
            <span className="text-xs font-mono whitespace-nowrap">
              <span className={matchedCount > 0 ? 'text-cyan-400' : 'text-red-400'}>
                {matchedCount}
              </span>
              <span className="text-text-3"> match{matchedCount !== 1 ? 'es' : ''}</span>
            </span>
          )}
        </div>

        <div className="flex items-center gap-1">
          {EDGE_KINDS.map((kind) => (
            <button
              key={kind}
              onClick={() => setEdgeFilter(kind)}
              className={`px-2.5 py-1 rounded text-xs font-mono transition-colors ${
                edgeFilter === kind
                  ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30'
                  : 'text-text-3 border border-border hover:text-text'
              }`}
            >
              {kind}
            </button>
          ))}
        </div>

        <div className="ml-auto flex items-center gap-2 text-xs text-text-3">
          <span className="font-mono">{graph.nodes.length} nodes · {graph.edges.length} edges</span>
          <button
            onClick={() => void reload()}
            className="p-1.5 rounded border border-border hover:border-border-hi text-text-3 hover:text-text transition-colors"
          >
            <RefreshCw size={13} className={loading ? 'animate-spin' : ''} />
          </button>
        </div>
      </div>

      {/* Legend */}
      <div className="px-4 py-1.5 border-b border-border bg-surface/50 flex items-center gap-4 overflow-x-auto">
        {Object.entries(DOMAIN_COLORS).filter(([k]) => k !== 'default').map(([domain, color]) => (
          <div key={domain} className="flex items-center gap-1.5 shrink-0">
            <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: color }} />
            <span className="text-[10px] text-text-3 capitalize">{domain}</span>
          </div>
        ))}
      </div>

      {/* Graph container */}
      <div ref={containerRef} className="flex-1 relative overflow-hidden">
        {error && (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-center text-text-3 space-y-2">
              <Maximize2 size={32} className="mx-auto opacity-30" />
              <div className="text-sm">Connect KG service to visualize graph</div>
              <div className="text-xs font-mono text-red-400/70">{error}</div>
            </div>
          </div>
        )}
        {loading && graph.nodes.length === 0 && !error && (
          <div className="absolute inset-0 flex items-center justify-center text-text-3 text-sm">
            Loading graph…
          </div>
        )}
        <svg ref={svgRef} className="w-full h-full" />
        <div ref={tooltipRef} className="kg-tooltip" style={{ display: 'none', position: 'absolute' }} />

        {/* Selected node indicator */}
        {selectedNode && (
          <div className="absolute bottom-4 left-4 bg-surface border border-border rounded px-3 py-2 text-xs">
            <span className="text-text-3">Selected: </span>
            <span className="font-mono text-cyan-400">{selectedNode.id}</span>
            <span className="text-text-3"> · {selectedNode.kind}</span>
          </div>
        )}
      </div>
    </div>
  )
}
