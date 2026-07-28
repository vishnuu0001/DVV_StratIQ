// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: InfraRationalization — frontend/src/components (AppHeader.jsx)
// Date: 2026-05-21
// ---------------------------------------------------------------------------
import { useContext } from 'react'
import { useNavigate } from 'react-router-dom'
import { Server, LogOut, Home, ArrowLeft, ScanSearch, ShieldCheck } from 'lucide-react'
import { AppContext } from '../App.jsx'
import { getPortalHomeUrl, logoutFromPortal } from '../api/client.js'

/**
 * Shared top navigation bar for all Infra Scan pages.
 *
 * Props:
 *   title      – main heading text
 *   subtitle   – optional secondary info shown below title
 *   backTo     – if provided, shows a ← back arrow button routing to this path
 *   rightSlot  – optional JSX rendered between the chip and Portal button (e.g. Export button)
 */
// Function: AppHeader
export default function AppHeader({ title, subtitle, backTo, rightSlot }) {
  const { user } = useContext(AppContext)
  const navigate = useNavigate()

  return (
    <header className="az-topbar flex-wrap">
      {/* ── Left: icon + labels ── */}
      <div className="flex items-center gap-3">
        {backTo && (
          <button
            onClick={() => navigate(backTo)}
            className="az-topbar-btn"
            aria-label="Back"
          >
            <ArrowLeft size={14} />
          </button>
        )}
        <div className="az-logo-mark">
          <Server size={15} />
        </div>
        <div className="min-w-0">
          <p className="az-topbar-eyebrow">Unified Modernization Suite</p>
          <p className="az-topbar-title truncate">{title}</p>
          {subtitle && (
            <p className="text-xs mt-0.5 truncate max-w-xs md:max-w-lg" style={{ color: '#c8c6c4' }}>{subtitle}</p>
          )}
        </div>
      </div>

      {/* ── Right: user info + nav buttons ── */}
      <div className="flex items-center gap-2 text-sm flex-wrap ml-auto">

        {/* Signed in as */}
        {user?.username && (
          <span className="az-topbar-user text-xs hidden sm:inline px-1">
            Signed in as <span className="font-medium" style={{ color: '#ffffff' }}>{user.username}</span>
          </span>
        )}

        {/* Chip */}
        <span className="az-topbar-chip hidden lg:inline-flex">
          <ScanSearch size={13} />
          Infra Scanner
        </span>

        {/* Extra slot (e.g. Export button on detail page) */}
        {rightSlot}

        {/* ← Dashboard (only on sub-pages) */}
        {backTo && backTo !== '/' && (
          <button onClick={() => navigate('/')} className="az-topbar-btn">
            <Home size={13} /> Dashboard
          </button>
        )}

        {/* Portal home */}
        <a href={getPortalHomeUrl()} className="az-topbar-btn">
          <Home size={13} /> Portal Home
        </a>

        {/* Admin Console (admin users only) */}
        {user?.role === 'admin' && (
          <a
            href={(() => { try { return new URL('/admin', getPortalHomeUrl()).href } catch { return '/admin' } })()}
            className="az-topbar-btn"
          >
            <ShieldCheck size={13} /> Admin Console
          </a>
        )}

        {/* Logout */}
        <button onClick={logoutFromPortal} className="az-topbar-btn">
          <LogOut size={13} /> Logout
        </button>
      </div>
    </header>
  )
}
