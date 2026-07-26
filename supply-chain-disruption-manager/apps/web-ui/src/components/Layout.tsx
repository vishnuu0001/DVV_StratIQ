// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: supply-chain-disruption-manager — apps/web-ui/src/components (Layout.tsx)
// Date: 2025-09-06
// ---------------------------------------------------------------------------
import React, { useEffect, useState } from 'react'
import { Outlet } from 'react-router-dom'
import { Wifi, WifiOff } from 'lucide-react'
import { LeftRail } from './LeftRail'
import { RightInspector } from './RightInspector'
import { useAppStore } from '../store/useAppStore'
import { getEventStreamURL } from '../api/inspector'
import { useEventStream } from '../hooks/useEventStream'
import {
  consumePortalTokenFromHash,
  decodePortalUser,
  getPortalAdminUrl,
  getPortalHomeUrl,
  getPortalToken,
  logoutFromPortal,
  type PortalUser,
} from '../lib/portalAuth'

// Function: Clock
function Clock() {
  const [time, setTime] = useState(() => new Date())
  useEffect(() => {
    const t = setInterval(() => setTime(new Date()), 1000)
    return () => clearInterval(t)
  }, [])
  return (
    <span className="font-mono text-xs text-text-3 tabular-nums">
      {time.toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' })}
    </span>
  )
}

// Function: Layout
export function Layout() {
  const { eventsPerMin, criticalCount, sseConnected } = useAppStore()
  useEventStream(getEventStreamURL(), () => {})
  const [portalUser, setPortalUser] = useState<PortalUser | null>(() => decodePortalUser(getPortalToken()))

  useEffect(() => {
    consumePortalTokenFromHash()
    setPortalUser(decodePortalUser(getPortalToken()))
  }, [])

  return (
    <div className="flex flex-col h-screen overflow-hidden">
      {/* Header */}
      <header className="h-16 shrink-0 bg-surface border-b border-border flex items-center px-4 gap-4 z-10">
        <div className="mr-2 hidden sm:block">
          <p className="text-[10px] uppercase tracking-[0.2em] text-cyan-400">Unified Modernization Suite</p>
          <p className="font-display text-base text-text leading-tight">Supply Chain Disruption Manager Workspace</p>
        </div>
        <div className="h-5 w-px bg-border hidden sm:block" />

        <div className="flex items-center gap-1.5">
          {sseConnected ? (
            <Wifi size={13} className="text-green-400" />
          ) : (
            <WifiOff size={13} className="text-text-3" />
          )}
          <span className="text-xs text-text-2 font-mono">
            {eventsPerMin.toFixed(1)} ev/min
          </span>
        </div>

        {criticalCount > 0 && (
          <div className="flex items-center gap-1.5 bg-red-500/10 border border-red-500/30 rounded px-2 py-1">
            <div className="w-1.5 h-1.5 rounded-full bg-red-500 dot-blink" />
            <span className="text-xs font-mono text-red-400 tabular-nums">
              {criticalCount} critical
            </span>
          </div>
        )}

        <div className="ml-auto flex items-center gap-3">
          <Clock />
          <div className="h-5 w-px bg-border hidden sm:block" />
          {portalUser?.username && (
            <span className="text-xs text-text-2 hidden sm:inline">{portalUser.username}</span>
          )}
          <button
            type="button"
            onClick={() => { window.location.href = getPortalHomeUrl() }}
            className="px-3 py-1.5 rounded-lg border border-border text-text-2 hover:bg-surface-2 text-xs font-medium"
          >
            Portal Home
          </button>
          {portalUser?.role === 'admin' && (
            <button
              type="button"
              onClick={() => { window.location.href = getPortalAdminUrl() }}
              className="px-3 py-1.5 rounded-lg border border-border text-text-2 hover:bg-surface-2 text-xs font-medium"
            >
              Admin Console
            </button>
          )}
          <button
            type="button"
            onClick={logoutFromPortal}
            className="px-3 py-1.5 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400 hover:bg-red-500/15 text-xs font-semibold"
          >
            Logout
          </button>
        </div>
      </header>

      {/* Body */}
      <div className="flex flex-1 overflow-hidden">
        <LeftRail />

        {/* Center */}
        <main className="flex-1 overflow-hidden bg-bg">
          <Outlet />
        </main>

        <RightInspector />
      </div>
    </div>
  )
}
