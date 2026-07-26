// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: supply-chain-disruption-manager — apps/web-ui/src/components (RightInspector.tsx)
// Date: 2026-03-03
// ---------------------------------------------------------------------------
import React, { useState } from 'react'
import { X, RotateCcw, CheckCircle, XCircle, ExternalLink, User } from 'lucide-react'
import { useAppStore } from '../store/useAppStore'
import { JsonViewer } from './JsonViewer'
import { SeverityBadge } from './SeverityBadge'
import { replayEvent } from '../api/inspector'
import { approveIncident, rejectIncident } from '../api/agents'
import type { Owner } from '../api/kg'
import { getOwners } from '../api/kg'

// Function: formatTs
function formatTs(ts: string): string {
  try {
    return new Date(ts).toLocaleString('en-US', {
      month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false,
    })
  } catch {
    return ts
  }
}

// Function: Row
function Row({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="flex gap-2 py-1.5 border-b border-border/50 last:border-0">
      <span className="text-xs text-text-3 w-28 shrink-0">{label}</span>
      <span className="text-xs text-text-2 break-all">{children}</span>
    </div>
  )
}

// Function: RightInspector
export function RightInspector() {
  const { selectedEvent, selectedIncident, selectedNode, rightPanelOpen, closeRightPanel } = useAppStore()
  const selectIncident = useAppStore((s) => s.selectIncident)

  const [replaying, setReplaying] = useState(false)
  const [replayDone, setReplayDone] = useState(false)
  const [approving, setApproving] = useState(false)
  const [approveReason, setApproveReason] = useState('')
  const [owners, setOwners] = useState<Owner[]>([])
  const [ownersLoaded, setOwnersLoaded] = useState(false)

  React.useEffect(() => {
    setOwnersLoaded(false)
    setOwners([])
    if (selectedNode) {
      getOwners(selectedNode.id)
        .then((o) => { setOwners(o); setOwnersLoaded(true) })
        .catch(() => setOwnersLoaded(true))
    }
  }, [selectedNode])

  if (!rightPanelOpen) return null

  return (
    <aside className="w-[380px] shrink-0 bg-surface border-l border-border flex flex-col overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-border">
        <span className="text-sm font-medium text-text">
          {selectedEvent ? 'Event Inspector' : selectedIncident ? 'Incident Detail' : 'Node Properties'}
        </span>
        <button
          onClick={closeRightPanel}
          className="p-1 rounded hover:bg-surface-2 text-text-3 hover:text-text transition-colors"
        >
          <X size={16} />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto">
        {/* Event panel */}
        {selectedEvent && (
          <div className="p-4 space-y-4">
            <div className="flex items-start justify-between gap-2">
              <div>
                <div className="font-mono text-xs text-text-3 mb-1">{selectedEvent.event_id}</div>
                <div className="text-sm font-medium">{selectedEvent.event_type}</div>
              </div>
              <SeverityBadge severity={selectedEvent.severity} />
            </div>

            <div className="space-y-0">
              <Row label="Source">{selectedEvent.source_system}</Row>
              <Row label="Ingested">{formatTs(selectedEvent.ingested_at)}</Row>
              <Row label="Source TS">{formatTs(selectedEvent.source_timestamp)}</Row>
              {selectedEvent.root_node_id && (
                <Row label="Root Node">
                  <span className="font-mono">{selectedEvent.root_node_id}</span>
                </Row>
              )}
              {Object.keys(selectedEvent.tags).length > 0 && (
                <Row label="Tags">
                  <div className="flex flex-wrap gap-1">
                    {Object.entries(selectedEvent.tags).map(([k, v]) => (
                      <span key={k} className="text-[10px] font-mono bg-surface-2 border border-border px-1 py-0.5 rounded">
                        {k}={v}
                      </span>
                    ))}
                  </div>
                </Row>
              )}
            </div>

            <div>
              <div className="text-xs text-text-3 mb-2 uppercase tracking-wider">Payload</div>
              <JsonViewer data={selectedEvent.payload} />
            </div>

            <button
              onClick={async () => {
                setReplaying(true)
                try {
                  await replayEvent(selectedEvent.event_id)
                  setReplayDone(true)
                  setTimeout(() => setReplayDone(false), 2500)
                } catch {
                  // ignore
                } finally {
                  setReplaying(false)
                }
              }}
              disabled={replaying}
              className="flex items-center gap-2 w-full justify-center py-2 rounded border border-border hover:border-border-hi hover:bg-surface-2 transition-colors text-sm disabled:opacity-50"
            >
              {replayDone ? (
                <><CheckCircle size={14} className="text-green-400" /> Replayed</>
              ) : (
                <><RotateCcw size={14} className={replaying ? 'animate-spin' : ''} /> Replay Event</>
              )}
            </button>
          </div>
        )}

        {/* Incident panel */}
        {selectedIncident && (
          <div className="p-4 space-y-4">
            <div className="flex items-start justify-between gap-2">
              <div>
                <div className="font-mono text-xs text-text-3 mb-1">{selectedIncident.id}</div>
                <div className="text-sm font-medium">{selectedIncident.type.replace(/_/g, ' ')}</div>
              </div>
              <SeverityBadge severity={selectedIncident.severity} />
            </div>

            <div className="space-y-0">
              <Row label="State">
                <span className={`font-mono uppercase text-xs ${
                  selectedIncident.state === 'RESOLVED' ? 'text-green-400' :
                  selectedIncident.state === 'AWAITING_APPROVAL' ? 'text-yellow-300' :
                  selectedIncident.state === 'FAILED' ? 'text-red-400' : 'text-text-2'
                }`}>{selectedIncident.state}</span>
              </Row>
              <Row label="Confidence">
                <span className="font-mono">{(selectedIncident.confidence * 100).toFixed(0)}%</span>
              </Row>
              <Row label="Root Node">
                <span className="font-mono">{selectedIncident.root_node_id}</span>
              </Row>
              <Row label="Created">{formatTs(selectedIncident.created_at)}</Row>
              {selectedIncident.resolved_at && (
                <Row label="Resolved">{formatTs(selectedIncident.resolved_at)}</Row>
              )}
            </div>

            {selectedIncident.final_summary && (
              <div>
                <div className="text-xs text-text-3 mb-1 uppercase tracking-wider">Summary</div>
                <p className="text-xs text-text-2 leading-relaxed">{selectedIncident.final_summary}</p>
              </div>
            )}

            {selectedIncident.owners.length > 0 && (
              <div>
                <div className="text-xs text-text-3 mb-2 uppercase tracking-wider">Owners</div>
                <div className="space-y-1.5">
                  {selectedIncident.owners.map((owner) => (
                    <div key={owner.id} className="flex items-center gap-2 bg-surface-2 rounded px-2 py-1.5">
                      <User size={12} className="text-text-3 shrink-0" />
                      <div>
                        <div className="text-xs font-medium">{owner.name}</div>
                        <div className="text-[10px] text-text-3">{owner.role} · {owner.email}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {selectedIncident.state === 'AWAITING_APPROVAL' && (
              <div className="space-y-2">
                <div className="text-xs text-text-3 uppercase tracking-wider">Decision Required</div>
                <textarea
                  value={approveReason}
                  onChange={(e) => setApproveReason(e.target.value)}
                  placeholder="Reason / notes…"
                  className="w-full bg-surface-2 border border-border rounded px-3 py-2 text-xs text-text placeholder-text-3 resize-none focus:outline-none focus:border-border-hi"
                  rows={2}
                />
                <div className="flex gap-2">
                  <button
                    disabled={approving}
                    onClick={async () => {
                      setApproving(true)
                      try {
                        const updated = await approveIncident(selectedIncident.id, approveReason || 'Approved', 'operator')
                        selectIncident(updated)
                      } catch {
                        // ignore
                      } finally {
                        setApproving(false)
                      }
                    }}
                    className="flex-1 flex items-center justify-center gap-1.5 py-2 rounded bg-green-500/20 border border-green-500/30 text-green-400 hover:bg-green-500/30 text-xs font-medium transition-colors disabled:opacity-50"
                  >
                    <CheckCircle size={13} /> Approve
                  </button>
                  <button
                    disabled={approving}
                    onClick={async () => {
                      setApproving(true)
                      try {
                        const updated = await rejectIncident(selectedIncident.id, approveReason || 'Rejected', 'operator')
                        selectIncident(updated)
                      } catch {
                        // ignore
                      } finally {
                        setApproving(false)
                      }
                    }}
                    className="flex-1 flex items-center justify-center gap-1.5 py-2 rounded bg-red-500/20 border border-red-500/30 text-red-400 hover:bg-red-500/30 text-xs font-medium transition-colors disabled:opacity-50"
                  >
                    <XCircle size={13} /> Reject
                  </button>
                </div>
              </div>
            )}

            {selectedIncident.plan && (
              <div>
                <div className="text-xs text-text-3 mb-2 uppercase tracking-wider">Orchestrator Plan</div>
                <JsonViewer data={selectedIncident.plan} collapsed />
              </div>
            )}
          </div>
        )}

        {/* Node panel */}
        {selectedNode && (
          <div className="p-4 space-y-4">
            <div>
              <div className="font-mono text-xs text-text-3 mb-1">{selectedNode.id}</div>
              <div className="text-sm font-medium">{selectedNode.kind}</div>
              <div className="text-xs text-text-3 mt-0.5">{selectedNode.domain}</div>
            </div>

            <div>
              <div className="text-xs text-text-3 mb-2 uppercase tracking-wider">Properties</div>
              <JsonViewer data={selectedNode.properties} />
            </div>

            {ownersLoaded && owners.length > 0 && (
              <div>
                <div className="text-xs text-text-3 mb-2 uppercase tracking-wider">Owners</div>
                <div className="space-y-1.5">
                  {owners.map((owner) => (
                    <div key={owner.id} className="flex items-center gap-2 bg-surface-2 rounded px-2 py-1.5">
                      <User size={12} className="text-text-3 shrink-0" />
                      <div>
                        <div className="text-xs font-medium">{owner.name}</div>
                        <div className="text-[10px] text-text-3">{owner.role}</div>
                        <a
                          href={`mailto:${owner.email}`}
                          className="text-[10px] text-cyan-400 hover:underline flex items-center gap-0.5"
                        >
                          {owner.email} <ExternalLink size={9} />
                        </a>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </aside>
  )
}
