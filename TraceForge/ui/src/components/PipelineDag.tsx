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

const STATUS_STYLE: Record<string, { bg: string; border: string; text: string; labelText: string }> = {
  idle: { bg: '#ffffff', border: '#edebe9', text: '#605e5c', labelText: '#242424' },
  QUEUED: { bg: '#ffffff', border: '#c8c6c4', text: '#605e5c', labelText: '#242424' },
  RUNNING: { bg: '#eff6fc', border: '#0078d4', text: '#0078d4', labelText: '#242424' },
  AWAITING_APPROVAL: { bg: '#fff4ce', border: '#ca5010', text: '#ca5010', labelText: '#242424' },
  APPROVED: { bg: '#dff6dd', border: '#107c10', text: '#107c10', labelText: '#242424' },
  REJECTED: { bg: '#fdf3f4', border: '#a4262c', text: '#a4262c', labelText: '#242424' },
  FAILED: { bg: '#fdf3f4', border: '#a4262c', text: '#a4262c', labelText: '#242424' },
}

// Function: StageNode
function StageNode({ data }: { data: { label: string; status: string } }) {
  const style = STATUS_STYLE[data.status] || STATUS_STYLE.idle
  return (
    <div style={{ background: style.bg, border: `1.5px solid ${style.border}`, borderRadius: 2, padding: '10px 16px', minWidth: 120, textAlign: 'center' }}>
      <Handle type="target" position={Position.Left} style={{ opacity: 0 }} />
      <div style={{ fontSize: 13, fontWeight: 600, color: style.labelText }}>{data.label}</div>
      <div style={{ fontSize: 11, color: style.text, marginTop: 3 }}>{data.status === 'idle' ? 'idle' : data.status}</div>
      <Handle type="source" position={Position.Right} style={{ opacity: 0 }} />
    </div>
  )
}

// Function: GateNode
function GateNode({ data }: { data: { label: string; blocking: boolean } }) {
  return (
    <div style={{
      width: 44, height: 44, transform: 'rotate(45deg)',
      background: data.blocking ? '#fdf3f4' : '#dff6dd',
      border: `2px solid ${data.blocking ? '#a4262c' : '#107c10'}`,
      display: 'flex', alignItems: 'center', justifyContent: 'center',
    }}>
      <Handle type="target" position={Position.Left} style={{ opacity: 0 }} />
      <span style={{ transform: 'rotate(-45deg)', fontSize: 9, color: data.blocking ? '#a4262c' : '#107c10', fontWeight: 700 }}>{data.label}</span>
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
      if (i > 0) edges.push({ id: `e-${STAGES[i - 1]}-${stage}`, source: STAGES[i - 1], target: stage, style: { stroke: '#c8c6c4' } })
      x += gap

      const gateLabel = GATE_AFTER[stage]
      if (gateLabel) {
        const blocking = run?.status === 'AWAITING_APPROVAL'
        const gateId = `gate-${stage}`
        nodes.push({ id: gateId, type: 'gate', position: { x, y: 68 }, data: { label: gateLabel.replace('Gate ', 'G'), blocking }, draggable: false })
        edges.push({ id: `e-${stage}-${gateId}`, source: stage, target: gateId, style: { stroke: blocking ? '#a4262c' : '#c8c6c4' } })
        x += 80
      }
    })
    return { nodes, edges }
  }, [runs])

  return (
    <div style={{ height: 200, background: '#ffffff', border: '1px solid #edebe9', borderRadius: 2 }} className="overflow-hidden">
      <ReactFlow
        nodes={nodes} edges={edges} nodeTypes={nodeTypes} fitView proOptions={{ hideAttribution: true }}
        nodesDraggable={false} nodesConnectable={false} elementsSelectable={false} zoomOnScroll={false} panOnDrag={false}
        onNodeClick={(_, node) => { if (node.type === 'gate' && onGateClick) onGateClick(node.id.replace('gate-', '')) }}
      >
        <Background color="#edebe9" gap={16} />
      </ReactFlow>
    </div>
  )
}
