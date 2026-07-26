// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: supply-chain-disruption-manager — apps/web-ui/src/components (LeftRail.tsx)
// Date: 2026-06-15
// ---------------------------------------------------------------------------
import React, { useEffect, useState } from 'react'
import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard,
  Radio,
  Network,
  Siren,
  Bot,
  Plug,
  FileCode,
  RotateCcw,
  ChevronDown,
  ChevronRight,
} from 'lucide-react'
import { getKGHealth } from '../api/kg'
import { getInspectorHealth, getAdapters } from '../api/inspector'
import type { AdapterHealth } from '../api/inspector'
import { getAgentHealth } from '../api/agents'
import { ScenarioTrigger } from './ScenarioTrigger'

interface NavItem {
  to: string
  label: string
  icon: React.ReactNode
}

const NAV_ITEMS: NavItem[] = [
  { to: '/', label: 'Overview', icon: <LayoutDashboard size={15} /> },
  { to: '/signals', label: 'Signal Stream', icon: <Radio size={15} /> },
  { to: '/graph', label: 'Knowledge Graph', icon: <Network size={15} /> },
  { to: '/incidents', label: 'Incident Center', icon: <Siren size={15} /> },
  { to: '/agents', label: 'Agent Workbench', icon: <Bot size={15} /> },
  { to: '/adapters', label: 'Adapter Ops', icon: <Plug size={15} /> },
  { to: '/schemas', label: 'Schema Browser', icon: <FileCode size={15} /> },
  { to: '/replay', label: 'Replay / DLQ', icon: <RotateCcw size={15} /> },
]

interface ServiceStatus {
  name: string
  healthy: boolean
}

// Function: LeftRail
export function LeftRail() {
  const [services, setServices] = useState<ServiceStatus[]>([
    { name: 'KG', healthy: false },
    { name: 'Inspector', healthy: false },
    { name: 'Agents', healthy: false },
  ])
  const [adapters, setAdapters] = useState<AdapterHealth[]>([])
  const [scenariosOpen, setScenariosOpen] = useState(true)

  useEffect(() => {
    // Function: checkHealth
    async function checkHealth() {
      const results = await Promise.allSettled([
        getKGHealth(),
        getInspectorHealth(),
        getAgentHealth(),
      ])
      setServices([
        { name: 'KG', healthy: results[0].status === 'fulfilled' },
        { name: 'Inspector', healthy: results[1].status === 'fulfilled' },
        { name: 'Agents', healthy: results[2].status === 'fulfilled' },
      ])
    }
    // Function: loadAdapters
    async function loadAdapters() {
      try {
        const list = await getAdapters()
        setAdapters(list)
      } catch {
        // ignore
      }
    }
    void checkHealth()
    void loadAdapters()
    const interval = setInterval(() => {
      void checkHealth()
      void loadAdapters()
    }, 30000)
    return () => clearInterval(interval)
  }, [])

  return (
    <aside className="w-[220px] shrink-0 bg-surface border-r border-border flex flex-col overflow-hidden">
      {/* Brand */}
      <div className="px-4 py-3 border-b border-border">
        <div className="text-[11px] text-text-3 uppercase tracking-widest font-medium mb-0.5">
          Strat-Aqorynth
        </div>
        <div className="font-display text-sm text-text leading-tight">
          SC Disruption<br />Manager
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto py-2">
        <div className="px-2 space-y-0.5">
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === '/'}
              className={({ isActive }) =>
                `flex items-center gap-2.5 px-2.5 py-2 rounded text-sm transition-colors ${
                  isActive
                    ? 'bg-surface-3 text-text border border-border-hi'
                    : 'text-text-2 hover:text-text hover:bg-surface-2'
                }`
              }
            >
              <span className="shrink-0">{item.icon}</span>
              <span className="truncate">{item.label}</span>
            </NavLink>
          ))}
        </div>

        {/* Scenarios */}
        <div className="mt-4 px-2">
          <button
            onClick={() => setScenariosOpen(!scenariosOpen)}
            className="flex items-center justify-between w-full px-2 py-1.5 text-[11px] text-text-3 uppercase tracking-widest hover:text-text-2 transition-colors"
          >
            <span>Scenarios</span>
            {scenariosOpen ? <ChevronDown size={11} /> : <ChevronRight size={11} />}
          </button>
          {scenariosOpen && (
            <div className="mt-1">
              <ScenarioTrigger />
            </div>
          )}
        </div>

        {/* Adapters mini-list */}
        {adapters.length > 0 && (
          <div className="mt-4 px-2">
            <div className="px-2 py-1.5 text-[11px] text-text-3 uppercase tracking-widest">
              Adapters
            </div>
            <div className="space-y-1">
              {adapters.slice(0, 6).map((adapter) => (
                <div key={adapter.name} className="flex items-center gap-2 px-2 py-1">
                  <div
                    className={`w-1.5 h-1.5 rounded-full shrink-0 ${
                      adapter.status === 'healthy'
                        ? 'bg-green-400'
                        : adapter.status === 'degraded'
                        ? 'bg-amber-400'
                        : 'bg-red-500 dot-blink'
                    }`}
                  />
                  <span className="text-xs text-text-2 truncate">{adapter.name}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </nav>

      {/* Service status */}
      <div className="border-t border-border px-4 py-3 space-y-1.5">
        <div className="text-[10px] text-text-3 uppercase tracking-widest mb-2">Services</div>
        {services.map((svc) => (
          <div key={svc.name} className="flex items-center justify-between">
            <span className="text-xs text-text-2">{svc.name}</span>
            <div className="flex items-center gap-1.5">
              <div
                className={`w-1.5 h-1.5 rounded-full ${
                  svc.healthy ? 'bg-green-400' : 'bg-red-500 dot-blink'
                }`}
              />
              <span className={`text-[10px] font-mono ${svc.healthy ? 'text-green-400' : 'text-red-400'}`}>
                {svc.healthy ? 'UP' : 'DOWN'}
              </span>
            </div>
          </div>
        ))}
      </div>
    </aside>
  )
}
