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
export function LeftRail({ collapsed = false }: { collapsed?: boolean }) {
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
    <aside className={`scm-azure-nav${collapsed ? ' scm-azure-nav-collapsed' : ''}`}>
      {/* Brand */}
      <div className="scm-nav-heading">
        <div className="scm-nav-eyebrow">Operations workspace</div>
        <div className="scm-nav-title">SCM resources</div>
      </div>

      {/* Navigation */}
      <nav className="scm-nav-scroll">
        <div className="scm-nav-links">
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === '/'}
              title={collapsed ? item.label : undefined}
              className={({ isActive }) =>
                `scm-nav-link ${
                  isActive
                    ? 'scm-nav-link-active'
                    : ''
                }`
              }
            >
              <span className="scm-nav-icon">{item.icon}</span>
              <span className="truncate">{item.label}</span>
            </NavLink>
          ))}
        </div>

        {/* Scenarios */}
        <div className="scm-nav-section">
          <button
            onClick={() => setScenariosOpen(!scenariosOpen)}
            className="scm-nav-section-title"
          >
            <span>Scenarios</span>
            {scenariosOpen ? <ChevronDown size={11} /> : <ChevronRight size={11} />}
          </button>
          {scenariosOpen && (
            <div className="scm-nav-scenarios">
              <ScenarioTrigger />
            </div>
          )}
        </div>

        {/* Adapters mini-list */}
        {adapters.length > 0 && (
          <div className="scm-nav-section">
            <div className="scm-nav-section-title">
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
      <div className="scm-nav-services">
        <div className="scm-nav-section-title">Service health</div>
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
