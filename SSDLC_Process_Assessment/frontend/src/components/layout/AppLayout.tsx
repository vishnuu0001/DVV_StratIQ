// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: SSDLC_Process_Assessment — frontend/src/components/layout (AppLayout.tsx)
// Date: 2025-07-19
// ---------------------------------------------------------------------------
import { useEffect, useState } from 'react'
import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { useQueryClient } from '@tanstack/react-query'
import {
  TrendingUp,
  Upload,
  LayoutDashboard,
  BarChart2,
  Users,
  Grid,
  Zap,
  RefreshCw,
  GitBranch,
  CheckCircle,
  AlertCircle,
  XCircle,
  type LucideIcon,
} from 'lucide-react'
import { useWorkbook } from '../../context/WorkbookContext'
import {
  consumePortalTokenFromHash,
  decodePortalUser,
  getPortalAdminUrl,
  getPortalHomeUrl,
  getPortalToken,
  logoutFromPortal,
  type PortalUser,
} from '../../lib/portalAuth'

interface NavItem {
  to: string
  icon: LucideIcon
  label: string
}

const navItems: NavItem[] = [
  { to: '/', icon: Upload, label: 'Upload' },
  { to: '/dashboard', icon: LayoutDashboard, label: 'Executive Dashboard' },
  { to: '/tower-model', icon: BarChart2, label: 'Tower Model' },
  { to: '/vendor-landscape', icon: Users, label: 'Vendor Landscape' },
  { to: '/heatmap', icon: Grid, label: 'Heatmap' },
  { to: '/techm-growth', icon: Zap, label: 'Portfolio Growth' },
  { to: '/transformation-capacity', icon: RefreshCw, label: 'Transformation Capacity' },
  { to: '/operating-model', icon: GitBranch, label: 'Operating Model' },
]

// Function: AppLayout
export default function AppLayout() {
  const { workbookId, clearWorkbook } = useWorkbook()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [portalUser, setPortalUser] = useState<PortalUser | null>(() => decodePortalUser(getPortalToken()))

  useEffect(() => {
    consumePortalTokenFromHash()
    setPortalUser(decodePortalUser(getPortalToken()))
  }, [])

  // Function: handleClearWorkbook
  function handleClearWorkbook() {
    clearWorkbook()
    queryClient.clear()
    navigate('/')
  }

  return (
    <div className="flex h-screen overflow-hidden bg-navy-900">
      {/* Sidebar */}
      <aside className="flex flex-col w-64 shrink-0 bg-navy-800 border-r border-navy-700">
        {/* Brand */}
        <div className="flex items-center gap-3 px-6 py-5 border-b border-navy-700">
          <div className="flex items-center justify-center w-9 h-9 bg-accent-blue/20 rounded-lg">
            <TrendingUp size={20} className="text-accent-blue" />
          </div>
          <div>
            <div className="text-sm font-bold text-slate-100 leading-tight">CSM Dashboard</div>
            <div className="text-xs text-slate-500">Consolidation Savings</div>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto py-4 px-3 space-y-0.5">
          {navItems.map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-all duration-150 ${
                  isActive
                    ? 'bg-accent-blue/15 text-accent-blue font-medium'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-navy-700'
                }`
              }
            >
              {({ isActive }) => (
                <>
                  <Icon size={16} className={isActive ? 'text-accent-blue' : 'text-slate-500'} />
                  <span>{label}</span>
                </>
              )}
            </NavLink>
          ))}
        </nav>

        {/* Workbook status */}
        <div className="px-4 py-4 border-t border-navy-700">
          {workbookId ? (
            <div className="space-y-2">
              <div className="flex items-center gap-2 px-3 py-2.5 bg-accent-green/10 border border-accent-green/20 rounded-lg">
                <CheckCircle size={14} className="text-accent-green shrink-0" />
                <div className="min-w-0">
                <div className="text-xs font-medium text-accent-green">Workbook Loaded</div>
                <div className="text-xs text-slate-500 truncate font-mono">{workbookId.slice(0, 12)}…</div>
                </div>
              </div>
              <button
                type="button"
                onClick={handleClearWorkbook}
                className="flex w-full items-center justify-center gap-2 rounded-lg border border-accent-red/30 bg-accent-red/10 px-3 py-2 text-xs font-semibold text-accent-red transition-colors hover:bg-accent-red/15"
              >
                <XCircle size={14} />
                Clear Workbook
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-2 px-3 py-2.5 bg-accent-amber/10 border border-accent-amber/20 rounded-lg">
              <AlertCircle size={14} className="text-accent-amber shrink-0" />
              <div>
                <div className="text-xs font-medium text-accent-amber">No Workbook</div>
                <div className="text-xs text-slate-500">Upload to begin</div>
              </div>
            </div>
          )}
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-y-auto">
        <header className="sticky top-0 z-30 border-b border-sky-200/80 bg-sky-300/85 backdrop-blur-xl">
          <div className="px-6 py-3 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
            <div>
              <p className="text-[11px] uppercase tracking-[0.2em] text-white">Unified Modernization Suite</p>
              <h2 className="text-slate-100 font-semibold">SSDLC Process Assessment Workspace</h2>
            </div>
            <div className="flex items-center gap-2 text-sm">
              {portalUser?.username && <span className="text-white text-xs">{portalUser.username}</span>}
              <button
                type="button"
                onClick={() => { window.location.href = getPortalHomeUrl() }}
                className="px-3 py-1.5 rounded-lg border border-white/45 bg-sky-400/35 text-white hover:bg-sky-400/55 text-xs font-medium"
              >
                Portal Home
              </button>
              {portalUser?.role === 'admin' && (
                <button
                  type="button"
                  onClick={() => { window.location.href = getPortalAdminUrl() }}
                  className="px-3 py-1.5 rounded-lg border border-white/45 bg-sky-400/35 text-white hover:bg-sky-400/55 text-xs font-medium"
                >
                  Admin Console
                </button>
              )}
              <button
                type="button"
                onClick={logoutFromPortal}
                className="px-3 py-1.5 rounded-lg border border-white/45 bg-sky-400/35 text-white hover:bg-sky-400/55 text-xs font-semibold"
              >
                Logout
              </button>
            </div>
          </div>
        </header>
        <Outlet />
      </main>
    </div>
  )
}
