// ---------------------------------------------------------------------------
// Lab Robot — Windows App-style launcher for connected AI workspaces.
// ---------------------------------------------------------------------------
import { useMemo, useState } from 'react'

const APPS = [
  {
    id: 'claude',
    name: 'Claude Studio',
    vendor: 'Anthropic',
    description: 'Reason, write, analyze, and collaborate with Claude.',
    url: 'https://claude.ai/',
    accent: '#d97757',
    icon: 'claude',
  },
  {
    id: 'veo',
    name: 'Google Veo',
    vendor: 'Google Flow',
    description: 'Create and refine cinematic video with Veo in Google Flow.',
    url: 'https://labs.google/fx/tools/flow',
    accent: '#4285f4',
    icon: 'veo',
  },
  {
    id: 'copilot',
    name: 'Copilot',
    vendor: 'Microsoft',
    description: 'Use Microsoft Copilot for research and everyday AI assistance.',
    url: 'https://copilot.microsoft.com/',
    accent: '#7b61ff',
    icon: 'copilot',
  },
  {
    id: 'lab-robot',
    name: 'Lab Robot Control',
    vendor: 'Strat-Aqorynth',
    description: 'Open rack operations, simulation, orchestration, and AI Lab tools.',
    accent: '#0078d4',
    icon: 'robot',
    internal: true,
  },
]

function AppMark({ type }) {
  if (type === 'claude') {
    return <span className="winapp-mark-glyph">AI</span>
  }
  if (type === 'veo') {
    return (
      <svg viewBox="0 0 48 48" aria-hidden="true">
        <path fill="#4285F4" d="M24 5a19 19 0 0 0-13.4 5.5l7.1 7.1A9 9 0 0 1 33 24h10A19 19 0 0 0 24 5Z" />
        <path fill="#34A853" d="M43 24H33a9 9 0 0 1-15.3 6.4l-7.1 7.1A19 19 0 0 0 43 24Z" />
        <path fill="#FBBC05" d="M17.7 30.4A9 9 0 0 1 15 24H5a19 19 0 0 0 5.6 13.5l7.1-7.1Z" />
        <path fill="#EA4335" d="M15 24a9 9 0 0 1 2.7-6.4l-7.1-7.1A19 19 0 0 0 5 24h10Z" />
        <path fill="white" d="m21 17 10 7-10 7V17Z" />
      </svg>
    )
  }
  if (type === 'copilot') {
    return (
      <svg viewBox="0 0 48 48" fill="none" aria-hidden="true">
        <path d="M18 10c5-6 15-3 15 4 7-1 10 8 4 12 3 7-6 13-12 8-5 6-15 1-12-6-8-2-6-13 1-15-1-4 1-7 4-9Z" stroke="white" strokeWidth="4" />
        <path d="M15 29c5-9 13-14 22-14M12 20c9 0 17 5 22 14" stroke="white" strokeWidth="3" strokeLinecap="round" />
      </svg>
    )
  }
  return (
    <svg viewBox="0 0 48 48" fill="none" aria-hidden="true">
      <rect x="10" y="15" width="28" height="24" rx="7" stroke="white" strokeWidth="3" />
      <path d="M24 15V8m-5 0h10M16 27h.1M32 27h.1M18 34h12" stroke="white" strokeWidth="3" strokeLinecap="round" />
    </svg>
  )
}

export default function WindowsAppWorkspace({ onOpenLabRobot }) {
  const [query, setQuery] = useState('')
  const [activeApp, setActiveApp] = useState(null)
  const [favoriteIds, setFavoriteIds] = useState(new Set(['claude', 'veo', 'copilot']))

  const visibleApps = useMemo(() => {
    const needle = query.trim().toLowerCase()
    if (!needle) return APPS
    return APPS.filter((app) => `${app.name} ${app.vendor} ${app.description}`.toLowerCase().includes(needle))
  }, [query])

  const launch = (app) => {
    if (app.internal) {
      onOpenLabRobot()
      return
    }
    // These providers reject third-party iframe ancestors through CSP.
    // Top-level navigation keeps the experience in the current app window
    // without attempting to bypass the providers' security policy.
    window.open(app.url, '_top')
  }

  const toggleFavorite = (event, appId) => {
    event.stopPropagation()
    setFavoriteIds((current) => {
      const next = new Set(current)
      if (next.has(appId)) next.delete(appId)
      else next.add(appId)
      return next
    })
  }

  return (
    <div className="winapp-shell">
      <header className="winapp-topbar">
        <button type="button" className="winapp-waffle" aria-label="Application menu">
          {Array.from({ length: 9 }).map((_, index) => <span key={index} />)}
        </button>
        <div className="winapp-brand-mark">SA</div>
        <div className="winapp-title">Windows App</div>
        <div className="winapp-top-actions">
          <button type="button" title="Notifications">♧</button>
          <button type="button" title="Help">?</button>
          <button type="button" title="Settings">⚙</button>
          <span className="winapp-avatar">LR</span>
        </div>
      </header>

      <div className="winapp-body">
        <aside className="winapp-rail">
          <button type="button" className="winapp-rail-item" title="Favorites"><span>☆</span><small>Favorites</small></button>
          <button type="button" className="winapp-rail-item active" title="Apps"><span>▦</span><small>Apps</small></button>
          <div className="winapp-rail-spacer" />
          <a href="/launch-modules" className="winapp-rail-item" title="Portal home"><span>⌂</span><small>Portal</small></a>
        </aside>

        <main className="winapp-main">
          {false && activeApp ? (
            <section className="winapp-viewer" aria-label={`${activeApp.name} embedded workspace`}>
              <div className="winapp-viewer-bar">
                <button type="button" onClick={() => setActiveApp(null)} className="winapp-back">←</button>
                <div className="winapp-mini-mark" style={{ background: activeApp.accent }}><AppMark type={activeApp.icon} /></div>
                <div className="winapp-viewer-copy">
                  <strong>{activeApp.name}</strong>
                  <span>{activeApp.url}</span>
                </div>
                <a href={activeApp.url} target="_blank" rel="noreferrer" className="winapp-external">Open in browser ↗</a>
                <button type="button" onClick={() => setActiveApp(null)} className="winapp-close" aria-label="Close app">×</button>
              </div>
              <div className="winapp-frame-note">
                Sign in with the provider when prompted. If embedded access is blocked by the provider, use “Open in browser”.
              </div>
              <iframe
                key={activeApp.id}
                className="winapp-frame"
                src={activeApp.url}
                title={activeApp.name}
                allow="camera; microphone; clipboard-read; clipboard-write; fullscreen; autoplay"
                referrerPolicy="strict-origin-when-cross-origin"
              />
            </section>
          ) : (
            <section className="winapp-catalog">
              <div className="winapp-heading-row">
                <div>
                  <p className="winapp-eyebrow">STRAT-AQORYNTH AI WORKSPACES</p>
                  <h1>Apps</h1>
                  <p>Launch AI studios and lab operations from one managed workspace.</p>
                </div>
                <label className="winapp-search">
                  <span>⌕</span>
                  <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search" aria-label="Search apps" />
                </label>
              </div>

              <div className="winapp-filter-row">
                <button type="button" className="selected">All</button>
                <button type="button">Type⌄</button>
                <span className="winapp-sort">A-Z⌄　│　☷　<span>▦</span></span>
              </div>

              <div className="winapp-group-title"><span>⌄</span> AI &amp; Automation</div>
              <div className="winapp-grid">
                {visibleApps.map((app) => (
                  <article
                    key={app.id}
                    className="winapp-card"
                    role="button"
                    tabIndex={0}
                    onClick={() => launch(app)}
                    onKeyDown={(event) => {
                      if (event.key === 'Enter' || event.key === ' ') {
                        event.preventDefault()
                        launch(app)
                      }
                    }}
                  >
                    <div className="winapp-card-visual" style={{ '--app-accent': app.accent }}>
                      <span className="winapp-status">Available</span>
                      <button
                        type="button"
                        className={`winapp-favorite ${favoriteIds.has(app.id) ? 'selected' : ''}`}
                        onClick={(event) => toggleFavorite(event, app.id)}
                        aria-label={`${favoriteIds.has(app.id) ? 'Remove' : 'Add'} ${app.name} favorite`}
                      >★</button>
                      <div className="winapp-app-mark"><AppMark type={app.icon} /></div>
                      <div className="winapp-orbit one" /><div className="winapp-orbit two" />
                    </div>
                    <div className="winapp-card-copy">
                      <strong>{app.name}</strong>
                      <span>{app.vendor}</span>
                      <p>{app.description}</p>
                      <div className="winapp-card-footer"><span className="winapp-online-dot" /> Ready <b>Launch ↗</b></div>
                    </div>
                  </article>
                ))}
              </div>
              {!visibleApps.length && <div className="winapp-empty">No apps match “{query}”.</div>}
            </section>
          )}
        </main>
      </div>
    </div>
  )
}
