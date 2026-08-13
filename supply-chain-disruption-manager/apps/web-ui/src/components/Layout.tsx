// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: supply-chain-disruption-manager — apps/web-ui/src/components (Layout.tsx)
// Date: 2025-09-06
// ---------------------------------------------------------------------------
import React, { useEffect, useState } from 'react'
import { Outlet } from 'react-router-dom'
import { Bell, Box, CircleHelp, Menu, Search, Settings, Wifi, WifiOff } from 'lucide-react'
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
    <span className="scm-header-clock">
      {time.toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' })}
    </span>
  )
}

// Function: Layout
export function Layout() {
  const { eventsPerMin, criticalCount, sseConnected } = useAppStore()
  useEventStream(getEventStreamURL(), () => {})
  const [portalUser, setPortalUser] = useState<PortalUser | null>(() => decodePortalUser(getPortalToken()))
  const [navCollapsed, setNavCollapsed] = useState(false)

  useEffect(() => {
    consumePortalTokenFromHash()
    setPortalUser(decodePortalUser(getPortalToken()))
  }, [])

  return (
    <div className="scm-azure-shell">
      {/* Header */}
      <header className="scm-azure-header">
        <button
          type="button"
          className="scm-header-icon"
          aria-label={navCollapsed ? 'Expand navigation' : 'Collapse navigation'}
          aria-expanded={!navCollapsed}
          onClick={() => setNavCollapsed((value) => !value)}
        >
          <Menu size={18} />
        </button>
        <div className="scm-header-brand">
          <span className="scm-header-brand-mark"><Box size={17} /></span>
          <span className="scm-header-suite">Strat-Aqorynth</span>
          <span className="scm-header-divider" />
          <span className="scm-header-product">Supply Chain Disruption Manager</span>
        </div>
        <div className="scm-header-search">
          <Search size={15} />
          <span>Search resources, incidents, and services</span>
          <kbd>/</kbd>
        </div>
        <div className="scm-header-telemetry">
          {sseConnected ? (
            <Wifi size={14} />
          ) : (
            <WifiOff size={14} />
          )}
          <span>{eventsPerMin.toFixed(1)} ev/min</span>
        </div>

        {criticalCount > 0 && (
          <div className="scm-header-critical">
            <div className="w-1.5 h-1.5 rounded-full bg-red-500 dot-blink" />
            <span className="text-xs font-mono text-red-400 tabular-nums">
              {criticalCount} critical
            </span>
          </div>
        )}

        <div className="scm-header-actions">
          <Clock />
          <button type="button" className="scm-header-icon" aria-label="Notifications"><Bell size={16} /></button>
          <button type="button" className="scm-header-icon" aria-label="Settings"><Settings size={16} /></button>
          <button type="button" className="scm-header-icon" aria-label="Help"><CircleHelp size={16} /></button>
          {portalUser?.username && (
            <span className="scm-header-user">{portalUser.username.slice(0, 1).toUpperCase()}</span>
          )}
          <button
            type="button"
            onClick={() => { window.location.href = getPortalHomeUrl() }}
            className="scm-header-link"
          >
            Portal Home
          </button>
          {portalUser?.role === 'admin' && (
            <button
              type="button"
              onClick={() => { window.location.href = getPortalAdminUrl() }}
              className="scm-header-link"
            >
              Admin Console
            </button>
          )}
          <button
            type="button"
            onClick={logoutFromPortal}
            className="scm-header-link scm-header-logout"
          >
            Logout
          </button>
        </div>
      </header>

      {/* Body */}
      <div className="scm-azure-body">
        <LeftRail collapsed={navCollapsed} />

        {/* Center */}
        <main className="scm-azure-main">
          <Outlet />
        </main>

        <RightInspector />
      </div>
    </div>
  )
}
