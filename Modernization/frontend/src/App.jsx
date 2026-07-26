// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: Modernization — frontend/src (App.jsx)
// Date: 2025-12-17
// ---------------------------------------------------------------------------
import { LockKeyhole, Orbit } from 'lucide-react'
import { useEffect, useState, createContext } from 'react'
import { Toaster } from 'react-hot-toast'
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import {
  clearPortalToken,
  consumePortalTokenFromHash,
  getPortalLoginUrl,
  getPortalToken,
  validateSession,
} from './api/client.js'
import AnalysisPage from './pages/AnalysisPage.jsx'
import JobsPage from './pages/JobsPage.jsx'
import JobDetailPage from './pages/JobDetailPage.jsx'
import ProjectsPage from './pages/ProjectsPage.jsx'

export const AppContext = createContext(null)

// Function: App
export default function App() {
  const [authReady, setAuthReady] = useState(false)
  const [authUser, setAuthUser] = useState(null)
  const [authError, setAuthError] = useState('')

  useEffect(() => {
    let active = true
    // Function: bootstrap
    const bootstrap = async () => {
      consumePortalTokenFromHash()
      const token = getPortalToken()
      if (!token) {
        if (active) {
          setAuthError('No active portal session. Open this module from the StratApp portal.')
          setAuthReady(true)
        }
        return
      }
      try {
        const session = await validateSession()
        if (active) setAuthUser(session.user)
      } catch (err) {
        const status = err?.response?.status
        if (status === 401 || status === 403) {
          clearPortalToken()
          if (active) {
            setAuthError(
              err?.response?.data?.error ||
                'Session expired or access denied for Modernization module.',
            )
          }
        } else if (active) {
          setAuthUser({ username: 'Portal user', role: 'user' })
        }
      } finally {
        if (active) setAuthReady(true)
      }
    }
    bootstrap()
    return () => {
      active = false
    }
  }, [])

  if (!authReady) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-bg px-6">
        <div className="w-full max-w-sm rounded-3xl border border-hairline bg-surface p-8 text-center shadow-sm">
          <div className="mx-auto mb-5 flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-gold to-gold-dim text-white shadow-[0_10px_30px_rgba(0,120,212,0.18)]">
            <Orbit className="h-6 w-6 animate-spin" />
          </div>
          <h2 className="font-display text-xl font-medium text-ink">Connecting to your workspace</h2>
          <p className="mt-2 text-sm leading-6 text-ink-muted">
            Authenticating your portal session and preparing the modernization studio.
          </p>
        </div>
      </div>
    )
  }

  if (authError) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-bg px-6">
        <div className="w-full max-w-sm rounded-3xl border border-hairline bg-surface p-8 text-center shadow-sm">
          <div className="mx-auto mb-5 flex h-14 w-14 items-center justify-center rounded-2xl bg-blue-500/10">
            <LockKeyhole className="h-6 w-6 text-blue-600" />
          </div>
          <h2 className="mb-2 font-display text-xl font-medium text-ink">Access Required</h2>
          <p className="mb-6 text-sm leading-6 text-ink-muted">{authError}</p>
          <a
            href={getPortalLoginUrl()}
            className="inline-flex items-center justify-center rounded-xl bg-gold px-6 py-3 text-sm font-semibold text-white transition hover:bg-gold-soft"
          >
            Go to Portal
          </a>
        </div>
      </div>
    )
  }

  return (
    <AppContext.Provider value={{ authUser }}>
      <BrowserRouter basename={import.meta.env.BASE_URL.replace(/\/$/, '')}>
        <Toaster
          position="top-right"
          toastOptions={{
            style: {
              background: '#ffffff',
              color: '#242424',
              border: '1px solid #d2d0ce',
              borderRadius: '14px',
              fontSize: '13px',
              fontFamily: "'Manrope', 'Segoe UI', system-ui, sans-serif",
            },
          }}
        />
        <Routes>
          <Route path="/" element={<Navigate to="/projects" replace />} />
          <Route path="/analyze" element={<AnalysisPage />} />
          <Route path="/jobs" element={<JobsPage />} />
          <Route path="/jobs/:jobId" element={<JobDetailPage />} />
          <Route path="/projects" element={<ProjectsPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AppContext.Provider>
  )
}
