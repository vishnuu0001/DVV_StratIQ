// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: supply-chain-disruption-manager — apps/web-ui/src/components (ScenarioTrigger.tsx)
// Date: 2026-06-02
// ---------------------------------------------------------------------------
import React, { useState } from 'react'
import { Zap, Loader2, CheckCircle, XCircle } from 'lucide-react'
import { triggerDisruption } from '../api/agents'
import { ingestManual } from '../api/inspector'

interface Scenario {
  id: string
  label: string
  color: string
  action: () => Promise<unknown>
}

const SCENARIOS: Scenario[] = [
  {
    id: 'supplier-delay',
    label: 'Supplier Delay',
    color: 'text-amber-400 border-amber-500/30 hover:bg-amber-500/10',
    action: () =>
      triggerDisruption({
        source_event_id: 'demo-001',
        type: 'supplier_delay',
        root_node_id: 'SUP-001',
        payload: {
          supplier_id: 'SUP-001',
          po_ids_affected: ['PO-10001'],
          delay_days: 7,
          reason: 'Raw material shortage',
        },
      }),
  },
  {
    id: 'eta-slip',
    label: 'ETA Slip',
    color: 'text-purple-400 border-purple-500/30 hover:bg-purple-500/10',
    action: () =>
      ingestManual({
        event_type: 'logistics.shipment.eta_changed',
        source_system: 'logistics-adapter',
        severity: 'high',
        root_node_id: 'SHP-30007',
        payload: {
          shipment_id: 'SHP-30007',
          old_eta: new Date(Date.now() + 86400000).toISOString(),
          new_eta: new Date(Date.now() + 259200000).toISOString(),
          delay_hours: 48,
          reason: 'Port congestion',
        },
        tags: { domain: 'logistics', scenario: 'demo' },
      }),
  },
  {
    id: 'qc-reject',
    label: 'QC Reject',
    color: 'text-cyan-400 border-cyan-500/30 hover:bg-cyan-500/10',
    action: () =>
      ingestManual({
        event_type: 'warehouse.qc.rejected',
        source_system: 'warehouse-adapter',
        severity: 'high',
        root_node_id: 'MAT-RAW-004',
        payload: {
          batch_id: 'BATCH-2023',
          material_id: 'MAT-RAW-004',
          rejection_reason: 'Dimensional tolerance exceeded',
          quantity_rejected: 500,
          warehouse_id: 'WH-001',
        },
        tags: { domain: 'warehouse', scenario: 'demo' },
      }),
  },
  {
    id: 'customs-hold',
    label: 'Customs Hold',
    color: 'text-rose-400 border-rose-500/30 hover:bg-rose-500/10',
    action: () =>
      ingestManual({
        event_type: 'logistics.customs.held',
        source_system: 'logistics-adapter',
        severity: 'critical',
        root_node_id: 'SHP-30003',
        payload: {
          shipment_id: 'SHP-30003',
          hold_reason: 'Documentation incomplete',
          hold_duration_days: 5,
          customs_office: 'LAX',
        },
        tags: { domain: 'logistics', scenario: 'demo' },
      }),
  },
  {
    id: 'short-pick',
    label: 'Short Pick',
    color: 'text-emerald-400 border-emerald-500/30 hover:bg-emerald-500/10',
    action: () =>
      ingestManual({
        event_type: 'production.issue.short_pick',
        source_system: 'warehouse-adapter',
        severity: 'med',
        root_node_id: 'PRD-80002',
        payload: {
          production_order_id: 'PRD-80002',
          material_id: 'MAT-RAW-002',
          required_qty: 1000,
          available_qty: 650,
          shortfall_qty: 350,
        },
        tags: { domain: 'production', scenario: 'demo' },
      }),
  },
  {
    id: 'demand-spike',
    label: 'Demand Spike',
    color: 'text-yellow-300 border-yellow-400/30 hover:bg-yellow-400/10',
    action: () =>
      ingestManual({
        event_type: 'demand.forecast.spike',
        source_system: 'demand-adapter',
        severity: 'high',
        root_node_id: 'MAT-FG-002',
        payload: {
          material_id: 'MAT-FG-002',
          forecast_delta_pct: 145,
          period: 'next_30_days',
          trigger: 'viral_social_media',
        },
        tags: { domain: 'procurement', scenario: 'demo' },
      }),
  },
]

interface ScenarioButtonProps {
  scenario: Scenario
}

// Function: ScenarioButton
function ScenarioButton({ scenario }: ScenarioButtonProps) {
  const [state, setState] = useState<'idle' | 'loading' | 'success' | 'error'>('idle')

  // Function: handleClick
  async function handleClick() {
    setState('loading')
    try {
      await scenario.action()
      setState('success')
      setTimeout(() => setState('idle'), 2500)
    } catch {
      setState('error')
      setTimeout(() => setState('idle'), 2500)
    }
  }

  return (
    <button
      onClick={() => void handleClick()}
      disabled={state === 'loading'}
      className={`w-full text-left text-xs px-2.5 py-1.5 rounded border transition-colors font-medium flex items-center justify-between gap-1 ${scenario.color} bg-transparent`}
    >
      <span className="truncate">{scenario.label}</span>
      {state === 'idle' && <Zap size={11} className="opacity-60 shrink-0" />}
      {state === 'loading' && <Loader2 size={11} className="animate-spin shrink-0" />}
      {state === 'success' && <CheckCircle size={11} className="text-green-400 shrink-0" />}
      {state === 'error' && <XCircle size={11} className="text-red-400 shrink-0" />}
    </button>
  )
}

// Function: ScenarioTrigger
export function ScenarioTrigger() {
  return (
    <div className="space-y-1.5">
      {SCENARIOS.map((s) => (
        <ScenarioButton key={s.id} scenario={s} />
      ))}
    </div>
  )
}
