// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: TraceForge — ui/src/components (PipelineDag.tsx)
// Date: 2026-03-18
// ---------------------------------------------------------------------------
import { useMemo } from 'react'
import ReactFlow, { Background, Handle, Position, type Edge, type Node } from 'reactflow'
import 'reactflow/dist/style.css'
import type { PipelineRun } from '../api/types'

const STAGES = ['INGEST', 'EXTRACT', 'BRD', 'TEST_DESIGN', 'SCRIPT_GEN', 'RENDER']
const GATE_AFTER: Record<string, string> = { EXTRACT: 'Gate 1', BRD: 'Gate 2', TEST_DESIGN: 'Gate 3', SCRIPT_GEN: 'Gate 4' }

const STATUS_STYLE: Record<string, { bg: string; border: string; text: string }> = {
  idle: { bg: '#111827', border: '#374151', text: '#6b7280' },
  QUEUED: { bg: '#1f2937', border: '#4b5563', text: '#d1d5db' },
  RUNNING: { bg: '#1e3a8a', border: '#3b82f6', text: '#93c5fd' },
  AWAITING_APPROVAL: { bg: '#78350f', border: '#f59e0b', text: '#fcd34d' },
  APPROVED: { bg: '#064e3b', border: '#10b981', text: '#6ee7b7' },
  REJECTED: { bg: '#7f1d1d', border: '#ef4444', text: '#fca5a5' },
  FAILED: { bg: '#7f1d1d', border: '#ef4444', text: '#fca5a5' },
}

// Function: StageNode
function StageNode({ data }: { data: { label: string; status: string } }) {
  const style = STATUS_STYLE[data.status] || STATUS_STYLE.idle
  return (
    <div style={{ background: style.bg, border: `1.5px solid ${style.border}`, borderRadius: 10, padding: '10px 16px', minWidth: 120, textAlign: 'center' }}>
      <Handle type="target" position={Position.Left} style={{ opacity: 0 }} />
      <div style={{ fontSize: 11, fontWeight: 600, color: '#e5e7eb' }}>{data.label}</div>
      <div style={{ fontSize: 9, color: style.text, marginTop: 2 }}>{data.status === 'idle' ? 'idle' : data.status}</div>
      <Handle type="source" position={Position.Right} style={{ opacity: 0 }} />
    </div>
  )
}

// Function: GateNode
function GateNode({ data }: { data: { label: string; blocking: boolean } }) {
  return (
    <div style={{
      width: 44, height: 44, transform: 'rotate(45deg)',
      background: data.blocking ? '#7f1d1d' : '#064e3b',
      border: `2px solid ${data.blocking ? '#ef4444' : '#10b981'}`,
      display: 'flex', alignItems: 'center', justifyContent: 'center',
    }}>
      <Handle type="target" position={Position.Left} style={{ opacity: 0 }} />
      <span style={{ transform: 'rotate(-45deg)', fontSize: 8, color: data.blocking ? '#fca5a5' : '#6ee7b7', fontWeight: 700 }}>{data.label}</span>
      <Handle type="source" position={Position.Right} style={{ opacity: 0 }} />
    </div>
  )
}

const nodeTypes = { stage: StageNode, gate: GateNode }

// Function: PipelineDag
export default function PipelineDag({ runs, onGateClick }: { runs: PipelineRun[]; onGateClick?: (stage: string) => void }) {
  const latestByStage: Record<string, PipelineRun> = {}
  for (const run of runs) {
    if (!latestByStage[run.stage] || run.created_at > latestByStage[run.stage].created_at) latestByStage[run.stage] = run
  }

  const { nodes, edges } = useMemo(() => {
    const nodes: Node[] = []
    const edges: Edge[] = []
    let x = 0
    const gap = 160

    STAGES.forEach((stage, i) => {
      const run = latestByStage[stage]
      nodes.push({ id: stage, type: 'stage', position: { x, y: 60 }, data: { label: stage.replace('_', ' '), status: run?.status || 'idle' }, draggable: false })
      if (i > 0) edges.push({ id: `e-${STAGES[i - 1]}-${stage}`, source: STAGES[i - 1], target: stage, style: { stroke: '#374151' } })
      x += gap

      const gateLabel = GATE_AFTER[stage]
      if (gateLabel) {
        const blocking = run?.status === 'AWAITING_APPROVAL'
        const gateId = `gate-${stage}`
        nodes.push({ id: gateId, type: 'gate', position: { x, y: 68 }, data: { label: gateLabel.replace('Gate ', 'G'), blocking }, draggable: false })
        edges.push({ id: `e-${stage}-${gateId}`, source: stage, target: gateId, style: { stroke: blocking ? '#ef4444' : '#374151' } })
        x += 80
      }
    })
    return { nodes, edges }
  }, [runs])

  return (
    <div style={{ height: 200 }} className="bg-gray-900 border border-white/10 rounded-lg overflow-hidden">
      <ReactFlow
        nodes={nodes} edges={edges} nodeTypes={nodeTypes} fitView proOptions={{ hideAttribution: true }}
        nodesDraggable={false} nodesConnectable={false} elementsSelectable={false} zoomOnScroll={false} panOnDrag={false}
        onNodeClick={(_, node) => { if (node.type === 'gate' && onGateClick) onGateClick(node.id.replace('gate-', '')) }}
      >
        <Background color="#1f2937" gap={16} />
      </ReactFlow>
    </div>
  )
}
