// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: Modernization — frontend/src/components (Sidebar.jsx)
// Date: 2025-08-21
// ---------------------------------------------------------------------------
import { FolderKanban, Layers3, LogOut, Menu, Orbit, ShieldCheck, WandSparkles, X } from 'lucide-react'
import { useContext, useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { AppContext } from '../App.jsx'
import { getPortalHomeUrl, logoutFromPortal } from '../api/client.js'

const NAV_LINKS = [
  { to: '/projects', label: 'Governed Projects',   icon: FolderKanban, exact: false },
  { to: '/analyze',  label: 'Quick Analysis',      icon: WandSparkles, exact: false },
  { to: '/jobs',     label: 'Transformation Jobs', icon: Layers3,      exact: false },
]

// Function: SidebarContent
function SidebarContent({ onClose }) {
  const { authUser } = useContext(AppContext)
  const { pathname } = useLocation()

  // Function: isActive
  const isActive = (to, exact) => (exact ? pathname === to : pathname.startsWith(to))

  // Function: adminUrl
  const adminUrl = (() => {
    try { return new URL('/admin', getPortalHomeUrl()).href }
    catch { return '/admin' }
  })()

  return (
    <div className="flex h-full flex-col overflow-hidden">
      {/* Logo */}
      <div className="flex items-center gap-3 px-4 pb-5 pt-5">
        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-gold to-gold-dim text-bg shadow-[0_6px_20px_rgba(227,178,60,0.25)]">
          <Orbit className="h-5 w-5" />
        </div>
        <div className="min-w-0">
          <p className="truncate font-display text-[15px] font-medium leading-tight text-ink">Modernization</p>
          <p className="truncate text-[11px] leading-tight text-ink-faint">Studio · StratIQ</p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-0.5 overflow-y-auto px-3 pb-2">
        {NAV_LINKS.map(({ to, label, icon: Icon, exact }) => (
          <Link
            key={to}
            to={to}
            onClick={onClose}
            className={`flex items-center gap-3 rounded-xl px-3 py-2.5 text-[13px] font-medium transition-colors ${
              isActive(to, exact)
                ? 'bg-white/[0.08] text-ink'
                : 'text-ink-muted hover:bg-white/[0.04] hover:text-ink'
            }`}
          >
            <Icon className="h-4 w-4 shrink-0" />
            {label}
          </Link>
        ))}
        {authUser?.role === 'admin' && (
          <a
            href={adminUrl}
            className="flex items-center gap-3 rounded-xl px-3 py-2.5 text-[13px] font-medium text-ink-muted transition-colors hover:bg-white/[0.04] hover:text-ink"
          >
            <ShieldCheck className="h-4 w-4 shrink-0" />
            Admin Console
          </a>
        )}
      </nav>

      {/* User section */}
      <div className="border-t border-hairline px-3 py-4">
        {authUser && (
          <div className="mb-3 flex items-center gap-2.5 px-1">
            <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-white/20 to-white/5 text-[11px] font-bold text-ink">
              {(authUser.username || 'U').charAt(0).toUpperCase()}
            </div>
            <div className="min-w-0 flex-1">
              <p className="truncate text-[13px] font-semibold text-ink">{authUser.username}</p>
              <p className="text-[11px] text-ink-faint">StratIQ Pro</p>
            </div>
          </div>
        )}
        <div className="flex gap-2">
          <a
            href={getPortalHomeUrl()}
            className="flex flex-1 items-center justify-center gap-1.5 rounded-lg border border-hairline bg-white/[0.03] px-3 py-1.5 text-[12px] font-medium text-ink-dim transition hover:bg-white/[0.07] hover:text-ink"
          >
            Portal
          </a>
          <button
            type="button"
            onClick={logoutFromPortal}
            className="flex flex-1 items-center justify-center gap-1.5 rounded-lg border border-hairline bg-white/[0.03] px-3 py-1.5 text-[12px] font-medium text-ink-dim transition hover:bg-white/[0.07] hover:text-ink"
          >
            <LogOut className="h-3 w-3" />
            Logout
          </button>
        </div>
      </div>
    </div>
  )
}

// Function: Sidebar
export default function Sidebar() {
  const [open, setOpen] = useState(false)

  return (
    <>
      {/* Mobile backdrop */}
      <div
        className={`fixed inset-0 z-40 bg-black/50 backdrop-blur-sm transition-opacity duration-200 lg:hidden ${
          open ? 'opacity-100' : 'pointer-events-none opacity-0'
        }`}
        onClick={() => setOpen(false)}
      />

      {/* Sidebar panel — fixed on mobile, static (flex item) on desktop */}
      <aside
        className={`fixed inset-y-0 left-0 z-50 flex w-64 shrink-0 flex-col border-r border-hairline bg-bg-sidebar transition-transform duration-200 lg:static lg:translate-x-0 ${
          open ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {open && (
          <button
            type="button"
            onClick={() => setOpen(false)}
            aria-label="Close menu"
            className="absolute right-3 top-3 z-10 flex h-7 w-7 items-center justify-center rounded-lg text-ink-muted hover:bg-white/10 lg:hidden"
          >
            <X className="h-4 w-4" />
          </button>
        )}
        <SidebarContent onClose={() => setOpen(false)} />
      </aside>

      {/* Mobile toggle — floats over content */}
      <button
        type="button"
        onClick={() => setOpen(true)}
        aria-label="Open menu"
        className="fixed left-4 top-4 z-30 flex h-9 w-9 items-center justify-center rounded-xl border border-hairline bg-surface/90 shadow-sm backdrop-blur-sm transition hover:bg-surface-hover lg:hidden"
      >
        <Menu className="h-4 w-4 text-ink-dim" />
      </button>
    </>
  )
}
