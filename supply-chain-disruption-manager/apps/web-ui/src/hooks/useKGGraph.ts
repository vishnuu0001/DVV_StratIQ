// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: supply-chain-disruption-manager — apps/web-ui/src/hooks (useKGGraph.ts)
// Date: 2026-01-05
// ---------------------------------------------------------------------------
import { useState, useEffect, useCallback } from 'react'
import { traverseKG, listEntities } from '../api/kg'
import type { KGEntity, KGEdge } from '../api/kg'

export interface GraphData {
  nodes: KGEntity[]
  edges: KGEdge[]
}

const ROOT_KINDS = ['Supplier', 'PurchaseOrder', 'Warehouse', 'Shipment', 'ProductionOrder', 'Material']

// Function: useKGGraph
export function useKGGraph() {
  const [graph, setGraph] = useState<GraphData>({ nodes: [], edges: [] })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const loadGraph = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const nodeMap = new Map<string, KGEntity>()
      const edgeSet = new Set<string>()
      const edges: KGEdge[] = []

      const discoveredRoots: KGEntity[] = []
      for (const kind of ROOT_KINDS) {
        try {
          const entities = await listEntities(kind, 8)
          entities.forEach((n) => {
            nodeMap.set(n.id, n)
            discoveredRoots.push(n)
          })
        } catch {
          // ignore unavailable kinds
        }
      }

      for (const root of discoveredRoots.slice(0, 8)) {
        try {
          const result = await traverseKG(root.id, ['flow', 'meta', 'owns'], 3)
          result.nodes.forEach((n) => nodeMap.set(n.id, n))
          result.edges.forEach((e) => {
            const key = `${e.from}->${e.to}:${e.kind}`
            if (!edgeSet.has(key)) {
              edgeSet.add(key)
              edges.push(e)
            }
          })
        } catch {
          // ignore individual node failures
        }
      }

      if (nodeMap.size === 0) {
        for (const kind of ROOT_KINDS) {
          try {
            const entities = await listEntities(kind, 20)
            entities.forEach((n) => nodeMap.set(n.id, n))
          } catch {
            // ignore
          }
        }
      }

      setGraph({ nodes: Array.from(nodeMap.values()), edges })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load graph')
    } finally {
      setLoading(false)
    }
  }, [])

  const expandNode = useCallback(async (nodeId: string) => {
    try {
      const result = await traverseKG(nodeId, ['flow', 'meta', 'owns'], 2)
      setGraph((prev) => {
        const nodeMap = new Map(prev.nodes.map((n) => [n.id, n]))
        const edgeSet = new Set(prev.edges.map((e) => `${e.from}->${e.to}:${e.kind}`))
        const newEdges = [...prev.edges]

        result.nodes.forEach((n) => nodeMap.set(n.id, n))
        result.edges.forEach((e) => {
          const key = `${e.from}->${e.to}:${e.kind}`
          if (!edgeSet.has(key)) {
            edgeSet.add(key)
            newEdges.push(e)
          }
        })

        return { nodes: Array.from(nodeMap.values()), edges: newEdges }
      })
    } catch {
      // ignore expansion failures
    }
  }, [])

  useEffect(() => {
    void loadGraph()
  }, [loadGraph])

  return { graph, loading, error, reload: loadGraph, expandNode }
}
