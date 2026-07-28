// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: Novastra-ITSM — frontend/src/components (UnifiedTopMenu.jsx)
// Date: 2025-09-20
// ---------------------------------------------------------------------------
// Function: UnifiedTopMenu
export default function UnifiedTopMenu({
  workspaceTitle,
  username,
  portalHomeUrl,
  portalAdminUrl,
  onLogout,
}) {
  return (
    <header className="az-topbar shrink-0">
      <div className="az-logo-mark">
        <span style={{ fontSize: 13, fontWeight: 700 }}>▦</span>
      </div>
      <div className="flex-1 min-w-0">
        <p className="az-topbar-eyebrow">Unified Modernization Suite</p>
        <p className="az-topbar-title truncate">{workspaceTitle}</p>
      </div>
      <div className="flex items-center gap-2 text-sm">
        {username && <span className="az-topbar-user hidden sm:inline">Signed in as {username}</span>}
        <span className="az-topbar-chip hidden lg:inline-flex">Dedicated launcher</span>
        <a href={portalHomeUrl} className="az-topbar-btn">Portal Home</a>
        <a href={portalAdminUrl} className="az-topbar-btn hidden sm:inline-flex">Admin Console</a>
        <button type="button" onClick={onLogout} className="az-topbar-btn">Logout</button>
      </div>
    </header>
  )
}
