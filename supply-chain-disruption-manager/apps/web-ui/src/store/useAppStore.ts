// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: supply-chain-disruption-manager — apps/web-ui/src/store (useAppStore.ts)
// Date: 2026-03-17
// ---------------------------------------------------------------------------
import { create } from 'zustand'
import type { CanonicalEvent } from '../api/inspector'
import type { Incident } from '../api/agents'
import type { KGEntity } from '../api/kg'

interface BlastRadiusData {
  nodes: Array<{ id: string; kind: string; domain: string; properties: Record<string, unknown> }>
  edges: Array<{ from: string; to: string; kind: string; verb: string }>
}

interface AppState {
  selectedEvent: CanonicalEvent | null
  selectedIncident: Incident | null
  selectedNode: KGEntity | null
  rightPanelOpen: boolean
  activeBlastRadius: BlastRadiusData | null
  liveEventCount: number
  eventsPerMin: number
  criticalCount: number
  openApprovals: number
  sseConnected: boolean
  // actions
  selectEvent: (e: CanonicalEvent | null) => void
  selectIncident: (i: Incident | null) => void
  selectNode: (n: KGEntity | null) => void
  setBlastRadius: (r: BlastRadiusData | null) => void
  incrementEventCount: () => void
  setEventsPerMin: (n: number) => void
  setCriticalCount: (n: number) => void
  setOpenApprovals: (n: number) => void
  setSseConnected: (b: boolean) => void
  closeRightPanel: () => void
}

export const useAppStore = create<AppState>((set) => ({
  selectedEvent: null,
  selectedIncident: null,
  selectedNode: null,
  rightPanelOpen: false,
  activeBlastRadius: null,
  liveEventCount: 0,
  eventsPerMin: 0,
  criticalCount: 0,
  openApprovals: 0,
  sseConnected: false,

  selectEvent: (e) =>
    set({
      selectedEvent: e,
      selectedIncident: null,
      selectedNode: null,
      rightPanelOpen: e !== null,
    }),

  selectIncident: (i) =>
    set({
      selectedIncident: i,
      selectedEvent: null,
      selectedNode: null,
      rightPanelOpen: i !== null,
      activeBlastRadius: i?.blast_radius ?? null,
    }),

  selectNode: (n) =>
    set({
      selectedNode: n,
      selectedEvent: null,
      selectedIncident: null,
      rightPanelOpen: n !== null,
    }),

  setBlastRadius: (r) => set({ activeBlastRadius: r }),

  incrementEventCount: () =>
    set((state) => ({ liveEventCount: state.liveEventCount + 1 })),

  setEventsPerMin: (n) => set({ eventsPerMin: n }),
  setCriticalCount: (n) => set({ criticalCount: n }),
  setOpenApprovals: (n) => set({ openApprovals: n }),
  setSseConnected: (b) => set({ sseConnected: b }),

  closeRightPanel: () =>
    set({
      rightPanelOpen: false,
      selectedEvent: null,
      selectedIncident: null,
      selectedNode: null,
    }),
}))
