// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: Modernization — frontend/src/components (Sidebar.jsx)
// Date: 2025-08-21
// ---------------------------------------------------------------------------
import { BookOpenText, Boxes, ChevronDown, ChevronRight, FileText, FolderKanban, FolderUp, GitBranch, Home, Layers3, LogOut, Menu, Network, Orbit, ShieldCheck, WandSparkles, X } from 'lucide-react'
import { useContext, useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { AppContext } from '../App.jsx'
import { getPortalHomeUrl, logoutFromPortal } from '../api/client.js'

const NAV_LINKS = [
  { to: '/',         label: 'Modernization Home', icon: Home,           exact: true },
  { to: '/projects', label: 'Governed Projects',   icon: FolderKanban, exact: false },
  { to: '/analyze',  label: 'Quick Analysis',      icon: WandSparkles, exact: false },
  { to: '/jobs',     label: 'Transformation Jobs', icon: Layers3,      exact: false },
]

const REQUIREMENTS_LINKS = [
  { to: '/requirements/upload', label: 'Upload Projects', icon: FolderUp },
  { to: '/requirements/brd', label: 'BRD', icon: FileText },
  { to: '/requirements/fsd', label: 'FSD', icon: FileText },
  { to: '/requirements/knowledge-graph', label: 'Knowledge Graph', icon: Network },
  { to: '/requirements/architecture-review', label: 'Architecture Review', icon: GitBranch },
  { to: '/requirements/generated-assets', label: 'Generated Assets', icon: Boxes },
]

// Function: SidebarContent
function SidebarContent({ onClose }) {
  const { authUser, readOnly } = useContext(AppContext)
  const { pathname } = useLocation()
  const [requirementsOpen, setRequirementsOpen] = useState(() => pathname.startsWith('/requirements'))

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
      <Link to="/" onClick={onClose} className="flex items-center gap-3 px-5 pb-7 pt-6" aria-label="Modernization home">
        <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-blue-500 to-blue-700 text-white shadow-[0_10px_24px_rgba(0,120,212,0.24)]">
          <Orbit className="h-5 w-5" />
        </div>
        <div className="min-w-0">
          <p className="truncate text-[15px] font-bold leading-tight text-slate-900">Modernization</p>
          <p className="truncate text-[11px] leading-tight text-ink-faint">Studio · Strat-Aqorynth</p>
        </div>
      </Link>

      {/* Navigation */}
      <nav className="flex-1 space-y-1 overflow-y-auto px-3 pb-3">
        {NAV_LINKS.filter(({ to }) => to === '/').map(({ to, label, icon: Icon, exact }) => (
          <Link
            key={to}
            to={to}
            onClick={onClose}
            className={`flex items-center gap-3 rounded-xl px-3 py-3 text-[13px] font-medium transition-all ${
              isActive(to, exact)
                ? 'bg-blue-50 font-semibold text-blue-700'
                : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
            }`}
          >
            <Icon className="h-4 w-4 shrink-0" />
            {label}
          </Link>
        ))}
        <button
          type="button"
          aria-expanded={requirementsOpen}
          aria-controls="requirements-submenu"
          onClick={() => setRequirementsOpen(open => !open)}
          className={`flex items-center gap-3 rounded-xl px-3 py-3 text-[13px] font-semibold transition-all ${
            pathname.startsWith('/requirements') ? 'bg-blue-50 text-blue-700' : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
          } w-full text-left`}
        >
          <BookOpenText className="h-4 w-4 shrink-0" />
          <span className="flex-1 leading-5">Generate Requirements Documentation</span>
          {requirementsOpen ? <ChevronDown className="h-4 w-4 shrink-0" /> : <ChevronRight className="h-4 w-4 shrink-0" />}
        </button>
        <div id="requirements-submenu" hidden={!requirementsOpen} className="mb-3 ml-5 mt-1 space-y-1 border-l border-slate-200 pl-3">
          {REQUIREMENTS_LINKS.map(({ to, label, icon: Icon }) => (
            <Link
              key={to}
              to={to}
              onClick={onClose}
              className={`flex items-center gap-2.5 rounded-lg px-3 py-2.5 text-[12px] transition-all ${
                pathname === to ? 'bg-blue-600 font-semibold text-white shadow-sm' : 'text-slate-500 hover:bg-slate-100 hover:text-slate-900'
              }`}
            >
              <Icon className="h-3.5 w-3.5 shrink-0" />
              {label}
            </Link>
          ))}
        </div>
        {NAV_LINKS.filter(({ to }) => to !== '/').map(({ to, label, icon: Icon, exact }) => (
          <Link
            key={to}
            to={to}
            onClick={onClose}
            className={`flex items-center gap-3 rounded-xl px-3 py-3 text-[13px] font-medium transition-all ${
              isActive(to, exact)
                ? 'bg-blue-50 font-semibold text-blue-700'
                : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
            }`}
          >
            <Icon className="h-4 w-4 shrink-0" />
            {label}
          </Link>
        ))}
        {authUser?.role === 'admin' && !readOnly && (
          <a
            href={adminUrl}
            className="flex items-center gap-3 rounded-xl px-3 py-3 text-[13px] font-medium text-slate-600 transition-all hover:bg-slate-100 hover:text-slate-900"
          >
            <ShieldCheck className="h-4 w-4 shrink-0" />
            Admin Console
          </a>
        )}
      </nav>

      {/* User section */}
      <div className="border-t border-slate-200 px-4 py-4">
        {authUser && (
          <div className="mb-3 flex items-center gap-2.5 px-1">
            <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-white/20 to-white/5 text-[11px] font-bold text-ink">
              {(authUser.username || 'U').charAt(0).toUpperCase()}
            </div>
            <div className="min-w-0 flex-1">
              <p className="truncate text-[13px] font-semibold text-ink">{authUser.username}</p>
              <p className="text-[11px] text-ink-faint">{readOnly ? 'Read-only access' : 'Strat-Aqorynth Pro'}</p>
            </div>
          </div>
        )}
        <div className="flex gap-2">
          <a
            href={getPortalHomeUrl()}
            className="flex flex-1 items-center justify-center gap-1.5 rounded-sm border border-hairline bg-white/[0.03] px-3 py-1.5 text-[12px] font-medium text-ink-dim transition hover:bg-white/[0.07] hover:text-ink"
          >
            Portal
          </a>
          <button
            type="button"
            onClick={logoutFromPortal}
            className="flex flex-1 items-center justify-center gap-1.5 rounded-sm border border-hairline bg-white/[0.03] px-3 py-1.5 text-[12px] font-medium text-ink-dim transition hover:bg-white/[0.07] hover:text-ink"
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
        className={`fixed inset-y-0 left-0 z-50 flex w-[280px] shrink-0 flex-col border-r border-slate-200 bg-white transition-transform duration-200 lg:static lg:translate-x-0 ${
          open ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {open && (
          <button
            type="button"
            onClick={() => setOpen(false)}
            aria-label="Close menu"
            className="absolute right-3 top-3 z-10 flex h-7 w-7 items-center justify-center rounded-sm text-ink-muted hover:bg-white/10 lg:hidden"
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
        className="fixed left-4 top-4 z-30 flex h-9 w-9 items-center justify-center rounded-sm border border-hairline bg-surface/90 shadow-sm backdrop-blur-sm transition hover:bg-surface-hover lg:hidden"
      >
        <Menu className="h-4 w-4 text-ink-dim" />
      </button>
    </>
  )
}
