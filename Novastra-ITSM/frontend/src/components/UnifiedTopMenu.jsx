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
    <header className="border-b border-sky-200/80 bg-sky-300/85 backdrop-blur sticky top-0 z-30 shrink-0">
      <div className="px-5 py-3 flex items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="grid h-10 w-10 place-items-center rounded-2xl bg-cyan-500 text-slate-950">
            <span className="text-lg font-black">▦</span>
          </div>
          <div>
            <p className="text-[11px] uppercase tracking-[0.25em] text-white">Unified Modernization Suite</p>
            <h2 className="text-slate-100 font-black text-xl leading-tight">{workspaceTitle}</h2>
          </div>
        </div>
        <div className="flex items-center gap-2 text-sm">
          {username && <span className="text-white hidden sm:inline">Signed in as {username}</span>}
          <span className="hidden rounded-full border border-white/45 bg-sky-400/35 px-4 py-2 text-xs font-black text-white lg:inline-flex">
            Dedicated launcher
          </span>
          <a
            href={portalHomeUrl}
            className="px-4 py-2 rounded-xl border border-white/45 bg-sky-400/35 text-white hover:bg-sky-400/55 text-sm font-bold transition-colors"
          >
            Portal Home
          </a>
          <a
            href={portalAdminUrl}
            className="px-4 py-2 rounded-xl border border-white/45 bg-sky-400/35 text-white hover:bg-sky-400/55 text-sm font-bold transition-colors hidden sm:inline-flex"
          >
            Admin Console
          </a>
          <button
            type="button"
            onClick={onLogout}
            className="px-4 py-2 rounded-xl border border-white/45 bg-sky-400/35 text-white hover:bg-sky-400/55 text-sm font-black transition-colors"
          >
            Logout
          </button>
        </div>
      </div>
    </header>
  )
}
