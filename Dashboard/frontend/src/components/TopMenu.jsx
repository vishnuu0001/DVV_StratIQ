// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: Dashboard — frontend/src/components (TopMenu.jsx)
// Date: 2025-09-26
// ---------------------------------------------------------------------------
import React, { useState, useEffect } from 'react'
import { LayoutDashboard, LogOut, Home, ShieldCheck, Menu, X } from 'lucide-react'

const PORTAL_HOME_URL = import.meta.env.VITE_PORTAL_HOME_URL || '/launch-modules'
const PORTAL_ADMIN_URL = import.meta.env.VITE_PORTAL_ADMIN_URL || '/admin'
const DASHBOARD_BASE_URL = import.meta.env.BASE_URL.replace(/\/$/, '') || ''

/**
 * Top menu bar for Dashboard Module
 * Displays module branding, title, and navigation controls
 */
// Function: TopMenu
export default function TopMenu({ title = 'Dashboard Workspace', subtitle = 'AI-Powered ITSM Intelligence' }) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [user, setUser] = useState(null)

  // Get user info from localStorage or session
  useEffect(() => {
    try {
      const userStr = localStorage.getItem('user')
      if (userStr) {
        setUser(JSON.parse(userStr))
      }
    } catch (err) {
      console.error('Error loading user:', err)
    }
  }, [])

  // Function: handleLogout
  const handleLogout = () => {
    // Clear localStorage and redirect to login/root
    localStorage.removeItem('user')
    localStorage.removeItem('token')
    window.location.href = `${DASHBOARD_BASE_URL}/connect`
  }

  // Function: handlePortal
  const handlePortal = () => {
    // Navigate to Launch Modules portal
    window.location.href = PORTAL_HOME_URL
  }

  // Function: handleAdminConsole
  const handleAdminConsole = () => {
    // Navigate to Admin Console
    window.location.href = PORTAL_ADMIN_URL
  }

  return (
    <header className="sticky top-0 z-50 border-b border-sky-200/80 bg-sky-300/85 backdrop-blur-xl">
      <div className="max-w-7xl mx-auto px-4 lg:px-6 py-3 flex items-center justify-between gap-4">

        {/* ── Left: Icon & Branding ── */}
        <div className="flex items-center gap-3 flex-1">
          <div className="h-11 w-11 rounded-2xl bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-blue-950/30 shrink-0">
            <LayoutDashboard size={22} className="text-white" />
          </div>
          <div className="hidden sm:block">
            <p className="text-[11px] uppercase tracking-[0.2em] text-white">Unified Modernization Suite</p>
            <h1 className="text-lg font-bold text-white leading-tight">{title}</h1>
            {subtitle && (
              <p className="text-xs text-slate-400 mt-0.5 truncate max-w-xs md:max-w-lg">{subtitle}</p>
            )}
          </div>
          <div className="sm:hidden">
            <p className="text-[11px] uppercase tracking-[0.2em] text-white">Unified Modernization Suite</p>
            <h2 className="text-sm font-bold text-white">{title}</h2>
          </div>
        </div>

        {/* ── Right: Navigation (Desktop) ── */}
        <div className="hidden md:flex items-center gap-2 text-sm flex-wrap">
          {/* Signed in as */}
          {user?.username && (
            <span className="text-white text-xs px-2 py-1 border-r border-white/45">
              Signed in as <span className="text-white font-medium">{user.username}</span>
            </span>
          )}

          {/* Infra Scanner Chip */}
          <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full border border-white/45 bg-sky-400/35 text-white text-xs font-medium">
            <LayoutDashboard size={13} />
            Dashboard
          </span>

          {/* Portal */}
          <button
            onClick={handlePortal}
            className="px-3 py-1.5 text-xs rounded-lg border border-white/45 bg-sky-400/35 flex items-center gap-1.5 text-white hover:bg-sky-400/55 transition-colors font-medium"
          >
            <Home size={13} /> Portal Home
          </button>

          {/* Admin Console (show for admin users) */}
          {user?.role === 'admin' && (
            <button
              onClick={handleAdminConsole}
              className="px-3 py-1.5 text-xs rounded-lg border border-white/45 bg-sky-400/35 flex items-center gap-1.5 text-white hover:bg-sky-400/55 transition-colors font-medium"
            >
              <ShieldCheck size={13} /> Admin Console
            </button>
          )}

          {/* Logout */}
          <button
            onClick={handleLogout}
            className="px-3 py-1.5 text-xs rounded-lg border border-white/45 bg-sky-400/35 text-white hover:bg-sky-400/55 flex items-center gap-1.5 font-semibold transition-colors"
          >
            <LogOut size={13} /> Logout
          </button>
        </div>

        {/* ── Mobile Menu Button ── */}
        <button
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          className="md:hidden p-2 rounded-lg hover:bg-sky-400/55 transition-colors text-white"
          aria-label="Toggle menu"
        >
          {mobileMenuOpen ? <X size={20} /> : <Menu size={20} />}
        </button>
      </div>

      {/* ── Mobile Menu ── */}
      {mobileMenuOpen && (
        <div className="md:hidden border-t border-white/45 bg-sky-300/90 px-4 py-3 flex flex-col gap-2">
          {user?.username && (
            <p className="text-xs text-white px-2 py-1">
              Signed in as <span className="font-medium text-white">{user.username}</span>
            </p>
          )}
          <button
            onClick={() => {
              handlePortal()
              setMobileMenuOpen(false)
            }}
            className="w-full text-left px-3 py-2 text-sm rounded-lg border border-white/45 bg-sky-400/35 flex items-center gap-2 text-white hover:bg-sky-400/55 transition-colors"
          >
            <Home size={16} /> Portal Home
          </button>
          {user?.role === 'admin' && (
            <button
              onClick={() => {
                handleAdminConsole()
                setMobileMenuOpen(false)
              }}
              className="w-full text-left px-3 py-2 text-sm rounded-lg border border-white/45 bg-sky-400/35 flex items-center gap-2 text-white hover:bg-sky-400/55 transition-colors"
            >
              <ShieldCheck size={16} /> Admin Console
            </button>
          )}
          <button
            onClick={() => {
              handleLogout()
              setMobileMenuOpen(false)
            }}
            className="w-full text-left px-3 py-2 text-sm rounded-lg flex items-center gap-2 font-semibold border border-white/45 bg-sky-400/35 text-white hover:bg-sky-400/55 transition-colors"
          >
            <LogOut size={16} /> Logout
          </button>
        </div>
      )}
    </header>
  )
}
