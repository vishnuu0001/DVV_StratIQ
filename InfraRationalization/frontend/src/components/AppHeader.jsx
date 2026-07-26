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
    <header className="sticky top-0 z-30 border-b border-sky-200/80 bg-sky-300/85 backdrop-blur-xl">
      <div className="max-w-7xl mx-auto px-5 py-4 flex flex-col md:flex-row md:items-center md:justify-between gap-3 flex-wrap">

        {/* ── Left: icon + labels ── */}
        <div className="flex items-center gap-3">
          {backTo && (
            <button
              onClick={() => navigate(backTo)}
              className="btn-ghost p-2 rounded-xl shrink-0"
              aria-label="Back"
            >
              <ArrowLeft size={17} />
            </button>
          )}
          <div className="h-11 w-11 rounded-2xl bg-gradient-brand flex items-center justify-center shadow-lg shadow-emerald-950/40 shrink-0">
            <Server size={20} className="text-white" />
          </div>
          <div>
            <p className="text-xs font-semibold text-white uppercase tracking-widest">Unified Modernization Suite</p>
            <h1 className="text-xl font-semibold text-white leading-tight">{title}</h1>
            {subtitle && (
              <p className="text-xs text-sky-50 mt-0.5 truncate max-w-xs md:max-w-lg">{subtitle}</p>
            )}
          </div>
        </div>

        {/* ── Right: user info + nav buttons ── */}
        <div className="flex items-center gap-2 text-sm flex-wrap">

          {/* Signed in as */}
          {user?.username && (
            <span className="text-white text-xs hidden sm:inline px-1">
              Signed in as <span className="text-white font-medium">{user.username}</span>
            </span>
          )}

          {/* Chip */}
          <span className="hidden lg:inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full border border-white/45 bg-sky-400/35 text-white text-xs font-medium">
            <ScanSearch size={13} />
            Infra Scanner
          </span>

          {/* Extra slot (e.g. Export button on detail page) */}
          {rightSlot}

          {/* ← Dashboard (only on sub-pages) */}
          {backTo && backTo !== '/' && (
            <button
              onClick={() => navigate('/')}
              className="px-3 py-2 text-xs rounded-xl flex items-center gap-1.5 border border-white/45 bg-sky-400/35 text-white hover:bg-sky-400/55 transition-colors"
            >
              <Home size={13} /> Dashboard
            </button>
          )}

          {/* Portal home */}
          <a
            href={getPortalHomeUrl()}
            className="px-3 py-2 text-xs rounded-xl flex items-center gap-1.5 border border-white/45 bg-sky-400/35 text-white hover:bg-sky-400/55 transition-colors"
          >
            <Home size={13} /> Portal Home
          </a>

          {/* Admin Console (admin users only) */}
          {user?.role === 'admin' && (
            <a
              href={(() => { try { return new URL('/admin', getPortalHomeUrl()).href } catch { return '/admin' } })()}
              className="px-3 py-2 text-xs rounded-xl flex items-center gap-1.5 border border-white/45 bg-sky-400/35 text-white hover:bg-sky-400/55 transition-colors"
            >
              <ShieldCheck size={13} /> Admin Console
            </a>
          )}

          {/* Logout */}
          <button
            onClick={logoutFromPortal}
            className="px-3 py-2 text-xs rounded-xl flex items-center gap-1.5 font-medium border border-white/45 bg-sky-400/35 text-white hover:bg-sky-400/55 transition-colors"
          >
            <LogOut size={13} /> Logout
          </button>
        </div>
      </div>
    </header>
  )
}
