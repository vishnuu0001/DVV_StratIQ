// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: supply-chain-disruption-manager — apps/web-ui/src/api (kg.ts)
// Date: 2026-02-01
// ---------------------------------------------------------------------------
const KG_URL = import.meta.env.VITE_KG_API_URL || '/api/kg'
const KG_KEY = import.meta.env.VITE_KG_API_KEY || 'kg-dev-key-change-in-prod'

export interface KGEntity {
  id: string
  kind: string
  domain: string
  depth?: number
  properties: Record<string, unknown>
}

export interface KGEdge {
  from: string
  to: string
  kind: string
  verb: string
  properties: Record<string, unknown>
}

export interface TraverseResult {
  root: KGEntity
  depth_reached: number
  nodes: KGEntity[]
  edges: KGEdge[]
}

export interface Owner {
  id: string
  kind: string
  name: string
  role: string
  email: string
}

export interface KGHealth {
  status: string
  node_count: number
  edge_count: number
}

// Function: headers
function headers(): HeadersInit {
  return { 'X-API-Key': KG_KEY, 'Content-Type': 'application/json' }
}

// Function: asRecord
function asRecord(value: unknown): Record<string, unknown> {
  return value && typeof value === 'object' && !Array.isArray(value) ? value as Record<string, unknown> : {}
}

// Function: normalizeEntity
function normalizeEntity(value: unknown): KGEntity {
  const entity = asRecord(value)
  const props = asRecord(entity.properties)
  const properties = Object.keys(props).length > 0 ? props : entity

  return {
    id: String(entity.id ?? ''),
    kind: String(entity.kind ?? ''),
    domain: String(entity.domain ?? ''),
    depth: typeof entity.depth === 'number' ? entity.depth : undefined,
    properties,
  }
}

// Function: normalizeEntities
function normalizeEntities(value: unknown): KGEntity[] {
  if (Array.isArray(value)) return value.map(normalizeEntity)
  const payload = asRecord(value)
  const items = payload.items ?? payload.results ?? payload.entities ?? payload.nodes
  return Array.isArray(items) ? items.map(normalizeEntity) : []
}

// Function: traverseKG
export async function traverseKG(
  rootId: string,
  edgeKinds: string[] = ['flow', 'meta'],
  maxDepth = 6
): Promise<TraverseResult> {
  const r = await fetch(
    `${KG_URL}/traverse?root_id=${encodeURIComponent(rootId)}&edge_kinds=${edgeKinds.join(',')}&direction=outbound&max_depth=${maxDepth}`,
    { headers: headers() }
  )
  if (!r.ok) throw new Error(`KG traverse failed: ${r.status}`)
  const payload = await r.json()
  return {
    ...payload,
    root: normalizeEntity(payload.root),
    nodes: normalizeEntities(payload.nodes),
    edges: Array.isArray(payload.edges) ? payload.edges : [],
  } as TraverseResult
}

// Function: getOwners
export async function getOwners(nodeId: string): Promise<Owner[]> {
  const r = await fetch(`${KG_URL}/nodes/${encodeURIComponent(nodeId)}/owners`, { headers: headers() })
  if (!r.ok) throw new Error(`KG getOwners failed: ${r.status}`)
  const payload = await r.json()
  const owners = Array.isArray(payload) ? payload : asRecord(payload).owners
  return Array.isArray(owners) ? owners as Owner[] : []
}

// Function: searchKG
export async function searchKG(query: string, kind?: string): Promise<KGEntity[]> {
  const params = new URLSearchParams({ q: query })
  if (kind) params.set('kind', kind)
  const r = await fetch(`${KG_URL}/search?${params.toString()}`, { headers: headers() })
  if (!r.ok) throw new Error(`KG search failed: ${r.status}`)
  return normalizeEntities(await r.json())
}

// Function: getKGHealth
export async function getKGHealth(): Promise<KGHealth> {
  const r = await fetch(`${KG_URL}/health`, { headers: headers() })
  if (!r.ok) throw new Error(`KG health failed: ${r.status}`)
  return r.json() as Promise<KGHealth>
}

// Function: listEntities
export async function listEntities(kind: string, limit = 50): Promise<KGEntity[]> {
  const r = await fetch(`${KG_URL}/entities?kind=${encodeURIComponent(kind)}&limit=${limit}`, { headers: headers() })
  if (!r.ok) throw new Error(`KG listEntities failed: ${r.status}`)
  return normalizeEntities(await r.json())
}

// Function: getNode
export async function getNode(nodeId: string): Promise<KGEntity> {
  const r = await fetch(`${KG_URL}/nodes/${encodeURIComponent(nodeId)}`, { headers: headers() })
  if (!r.ok) throw new Error(`KG getNode failed: ${r.status}`)
  return normalizeEntity(await r.json())
}
