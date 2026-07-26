// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: supply-chain-disruption-manager — apps/web-ui/src/views (SchemaBrowser.tsx)
// Date: 2025-08-18
// ---------------------------------------------------------------------------
import React, { useEffect, useState } from 'react'
import { FileCode, RefreshCw } from 'lucide-react'
import { getSchemas, getSchema, listEvents } from '../api/inspector'
import type { SchemaEntry, CanonicalEvent } from '../api/inspector'
import { JsonViewer } from '../components/JsonViewer'
import { SeverityBadge } from '../components/SeverityBadge'

// Function: formatTs
function formatTs(ts: string): string {
  try {
    return new Date(ts).toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' })
  } catch {
    return ts
  }
}

// Function: SchemaBrowser
export function SchemaBrowser() {
  const [schemas, setSchemas] = useState<SchemaEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedType, setSelectedType] = useState<string | null>(null)
  const [schemaDetail, setSchemaDetail] = useState<object | null>(null)
  const [schemaLoading, setSchemaLoading] = useState(false)
  const [recentEvents, setRecentEvents] = useState<CanonicalEvent[]>([])

  // Function: loadSchemas
  async function loadSchemas() {
    setLoading(true)
    try {
      const data = await getSchemas()
      setSchemas(data)
    } catch {
      setSchemas([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void loadSchemas()
  }, [])

  useEffect(() => {
    if (!selectedType) return
    setSchemaLoading(true)
    setSchemaDetail(null)
    setRecentEvents([])
    Promise.allSettled([
      getSchema(selectedType),
      listEvents({ event_type: selectedType, limit: 5 }),
    ]).then(([schemaResult, evResult]) => {
      if (schemaResult.status === 'fulfilled') setSchemaDetail(schemaResult.value)
      if (evResult.status === 'fulfilled') setRecentEvents(evResult.value.items)
    }).finally(() => setSchemaLoading(false))
  }, [selectedType])

  return (
    <div className="flex h-full overflow-hidden">
      {/* Left: schema list */}
      <div className="w-64 shrink-0 border-r border-border flex flex-col overflow-hidden bg-surface">
        <div className="p-3 border-b border-border flex items-center justify-between">
          <span className="text-xs text-text-3 uppercase tracking-wider">Event Types</span>
          <button
            onClick={() => void loadSchemas()}
            className="p-1 rounded hover:bg-surface-2 text-text-3"
          >
            <RefreshCw size={12} className={loading ? 'animate-spin' : ''} />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto divide-y divide-border/30">
          {loading ? (
            <div className="p-4 text-center text-text-3 text-xs">Loading schemas…</div>
          ) : schemas.length === 0 ? (
            <div className="p-4 text-center text-text-3 text-xs">
              No schemas found.<br />Connect Inspector service.
            </div>
          ) : (
            schemas.map((schema) => (
              <button
                key={schema.event_type}
                onClick={() => setSelectedType(schema.event_type)}
                className={`w-full text-left px-3 py-2.5 hover:bg-surface-2 transition-colors ${
                  selectedType === schema.event_type ? 'bg-surface-2 border-l-2 border-l-cyan-400' : ''
                }`}
              >
                <div className="text-xs text-text truncate">{schema.event_type}</div>
                <div className="flex items-center justify-between mt-0.5">
                  <span className="text-[10px] text-text-3 font-mono">v{schema.version}</span>
                  <span className="text-[10px] text-text-3 font-mono">{schema.recent_count} recent</span>
                </div>
              </button>
            ))
          )}
        </div>
      </div>

      {/* Right: schema detail */}
      <div className="flex-1 overflow-hidden flex flex-col bg-bg">
        {!selectedType ? (
          <div className="flex items-center justify-center h-full text-text-3 text-sm">
            <div className="text-center space-y-2">
              <FileCode size={32} className="mx-auto opacity-30" />
              <div>Select an event type to view its schema</div>
            </div>
          </div>
        ) : (
          <div className="flex-1 overflow-y-auto p-6 space-y-6">
            <div>
              <h2 className="text-base font-medium text-text">{selectedType}</h2>
              <p className="text-xs text-text-3 mt-0.5">JSON Schema definition</p>
            </div>

            {schemaLoading ? (
              <div className="text-text-3 text-sm">Loading schema…</div>
            ) : (
              <>
                {schemaDetail && (
                  <div>
                    <div className="text-xs text-text-3 mb-2 uppercase tracking-wider">Schema</div>
                    <JsonViewer data={schemaDetail} />
                  </div>
                )}

                {!schemaDetail && (
                  <div className="bg-surface border border-border rounded p-4 text-text-3 text-sm">
                    Schema definition not available from backend.
                  </div>
                )}

                {/* Recent events */}
                <div>
                  <div className="text-xs text-text-3 mb-2 uppercase tracking-wider">
                    Recent Events ({recentEvents.length})
                  </div>
                  {recentEvents.length === 0 ? (
                    <div className="text-xs text-text-3">No recent events of this type</div>
                  ) : (
                    <div className="bg-surface border border-border rounded overflow-hidden">
                      <div className="divide-y divide-border/50">
                        {recentEvents.map((evt) => (
                          <div key={evt.event_id} className="px-4 py-3">
                            <div className="flex items-center justify-between gap-2 mb-1">
                              <span className="font-mono text-xs text-text-3">{evt.event_id}</span>
                              <SeverityBadge severity={evt.severity} />
                            </div>
                            <div className="flex items-center justify-between gap-2">
                              <span className="text-xs text-text-2">{evt.source_system}</span>
                              <span className="font-mono text-[10px] text-text-3">{formatTs(evt.ingested_at)}</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
