// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: Novastra-ITSM — frontend/src/components (UnifiedTopMenu.jsx)
// Date: 2025-09-20
// ---------------------------------------------------------------------------
import { Bell, CircleHelp, Grid3X3, Search, Settings } from 'lucide-react'

// Function: UnifiedTopMenu
export default function UnifiedTopMenu({
  workspaceTitle,
  username,
  portalHomeUrl,
  portalAdminUrl,
  onLogout,
  readOnly = false,
}) {
  return (
    <header className="az-topbar shrink-0">
      <a href={portalHomeUrl} className="az-portal-launcher" aria-label="Open Unified Modernization Suite home">
        <Grid3X3 size={18} />
      </a>
      <div className="az-suite-name hidden md:block">Unified Modernization Suite</div>
      <div className="az-topbar-divider hidden md:block" />
      <div className="az-workspace-name min-w-0">
        <p className="az-topbar-title truncate">{workspaceTitle}</p>
      </div>

      <label className="az-global-search hidden lg:flex">
        <Search size={15} />
        <input type="search" aria-label="Search Novastra workspace" placeholder="Search resources, tickets, and services" />
      </label>

      <div className="az-topbar-actions">
        <button type="button" className="az-icon-btn hidden sm:inline-flex" title="Notifications" aria-label="Notifications">
          <Bell size={16} />
        </button>
        {!readOnly && portalAdminUrl && (
          <a href={portalAdminUrl} className="az-icon-btn hidden sm:inline-flex" title="Admin Console" aria-label="Admin Console">
            <Settings size={16} />
          </a>
        )}
        <a href={portalHomeUrl} className="az-icon-btn hidden sm:inline-flex" title="Portal Home" aria-label="Portal Home">
          <CircleHelp size={16} />
        </a>
        <div className="az-account-block">
          <span className="az-account-copy hidden md:block">
            <strong>{username || 'User'}</strong>
            <small>{readOnly ? 'Read-only access' : 'Novastra ITSM'}</small>
          </span>
          <span className="az-account-avatar">{(username || 'U').slice(0, 1).toUpperCase()}</span>
        </div>
        <button type="button" onClick={onLogout} className="az-topbar-btn">Sign out</button>
      </div>
    </header>
  )
}
