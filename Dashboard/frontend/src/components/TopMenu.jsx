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
    <header className="az-topbar">

      {/* ── Left: Icon & Branding ── */}
      <div className="az-logo-mark">
        <LayoutDashboard size={15} />
      </div>
      <div className="flex-1 min-w-0">
        <p className="az-topbar-eyebrow">Unified Modernization Suite</p>
        <p className="az-topbar-title truncate">{title}</p>
        {subtitle && (
          <p className="text-xs mt-0.5 truncate max-w-xs md:max-w-lg" style={{ color: '#c8c6c4' }}>{subtitle}</p>
        )}
      </div>

      {/* ── Right: Navigation (Desktop) ── */}
      <div className="hidden md:flex items-center gap-2 text-sm flex-wrap">
        {user?.username && (
          <span className="az-topbar-user text-xs px-2">
            Signed in as <span className="font-medium" style={{ color: '#ffffff' }}>{user.username}</span>
          </span>
        )}

        <span className="az-topbar-chip">
          <LayoutDashboard size={13} />
          Dashboard
        </span>

        <button onClick={handlePortal} className="az-topbar-btn">
          <Home size={13} /> Portal Home
        </button>

        {user?.role === 'admin' && (
          <button onClick={handleAdminConsole} className="az-topbar-btn">
            <ShieldCheck size={13} /> Admin Console
          </button>
        )}

        <button onClick={handleLogout} className="az-topbar-btn">
          <LogOut size={13} /> Logout
        </button>
      </div>

      {/* ── Mobile Menu Button ── */}
      <button
        onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
        className="md:hidden az-topbar-btn"
        aria-label="Toggle menu"
      >
        {mobileMenuOpen ? <X size={16} /> : <Menu size={16} />}
      </button>

      {/* ── Mobile Menu ── */}
      {mobileMenuOpen && (
        <div className="md:hidden absolute top-full left-0 right-0 border-t px-4 py-3 flex flex-col gap-2" style={{ background: '#1b1a19', borderColor: 'rgba(255,255,255,0.08)' }}>
          {user?.username && (
            <p className="text-xs px-2 py-1" style={{ color: '#d2d0ce' }}>
              Signed in as <span className="font-medium" style={{ color: '#ffffff' }}>{user.username}</span>
            </p>
          )}
          <button
            onClick={() => { handlePortal(); setMobileMenuOpen(false) }}
            className="az-topbar-btn justify-start"
          >
            <Home size={16} /> Portal Home
          </button>
          {user?.role === 'admin' && (
            <button
              onClick={() => { handleAdminConsole(); setMobileMenuOpen(false) }}
              className="az-topbar-btn justify-start"
            >
              <ShieldCheck size={16} /> Admin Console
            </button>
          )}
          <button
            onClick={() => { handleLogout(); setMobileMenuOpen(false) }}
            className="az-topbar-btn justify-start"
          >
            <LogOut size={16} /> Logout
          </button>
        </div>
      )}
    </header>
  )
}
