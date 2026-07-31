// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: CodeAnalysis — frontend/src (App.jsx)
// Date: 2025-09-08
// ---------------------------------------------------------------------------
import { useState, useCallback, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import toast from 'react-hot-toast'
import LandingPage from './components/LandingPage.jsx'
import ProgressOverlay from './components/ProgressOverlay.jsx'
import Dashboard from './components/Dashboard.jsx'
import {
  clearPortalToken,
  consumePortalTokenFromHash,
  getPortalHomeUrl,
  getPortalLoginUrl,
  getPortalToken,
  logoutFromPortal,
  pollJob,
  startAnalysis,
  startPortfolio,
  validateSession,
} from './api/client.js'

const VIEW = { LANDING: 'landing', LOADING: 'loading', DASHBOARD: 'dashboard' }

// Function: App
export default function App() {
  const [authReady, setAuthReady]   = useState(false)
  const [authUser, setAuthUser]     = useState(null)
  const [authError, setAuthError]   = useState('')
  const [view, setView]           = useState(VIEW.LANDING)
  const [job, setJob]             = useState(null)       // { progress, message }
  const [result, setResult]       = useState(null)       // analysis result
  const [portfolio, setPortfolio] = useState(null)       // array of results
  const [jobId, setJobId]         = useState(null)       // completed analysis job id (for AI features)
  const [analysisId, setAnalysisId] = useState(0)        // bumped on each new run → forces Dashboard remount
  const activePollRef = useRef(null)                     // cancel token for in-flight poll

  useEffect(() => {
    let active = true

    // Function: bootstrapAuth
    const bootstrapAuth = async () => {
      consumePortalTokenFromHash()
      const token = getPortalToken()
      const isLocalhost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'

      if (!token) {
        // Allow standalone access from localhost (dev mode)
        if (isLocalhost) {
          if (!active) {
            return
          }
          setAuthUser({ id: 'dev-user', name: 'Developer' })
          setAuthReady(true)
          return
        }
        
        if (!active) {
          return
        }
        setAuthError('No active portal session found. Open this module from the Application Rationalization portal.')
        setAuthReady(true)
        return
      }

      try {
        const session = await validateSession()
        if (!active) {
          return
        }
        setAuthUser(session.user)
      } catch (err) {
        clearPortalToken()
        if (!active) {
          return
        }
        setAuthError(err?.response?.data?.error || 'Session expired or permission denied for Code Analysis.')
      } finally {
        if (active) {
          setAuthReady(true)
        }
      }
    }

    bootstrapAuth()
    return () => {
      active = false
    }
  }, [])

  const handleAnalyse = useCallback(async (payload) => {
    // Cancel any in-flight poll from a previous run
    if (activePollRef.current) {
      activePollRef.current.cancel()
      activePollRef.current = null
    }

    // Immediately purge stale data so no old result bleeds through
    setResult(null)
    setPortfolio(null)
    setJob({ progress: 2, message: 'Submitting job…' })
    setView(VIEW.LOADING)

    try {
      let jobId
      if (payload.type === 'uploaded') {
        // UploadFolderPicker already zipped, uploaded, and started the job
        // itself (so its own progress UI stays visible during that phase) —
        // here we just take over polling exactly like every other analysis type.
        jobId = payload.jobId
      } else if (payload.type === 'portfolio') {
        const r = await startPortfolio({ org: payload.org, limit: payload.limit || 20 })
        jobId = r.job_id
      } else {
        const r = await startAnalysis({
          repo:    payload.repo    || null,
          local:   payload.local   || null,
          users:   payload.users   || 100,
          revenue: payload.revenue || 0,
        })
        jobId = r.job_id
      }

      const poller = pollJob(jobId, (j) => setJob({ progress: j.progress, message: j.message }))
      activePollRef.current = poller
      const done = await poller.promise
      activePollRef.current = null

      if (payload.type === 'portfolio') {
        setPortfolio(done.results || [])
        setResult(null)
      } else {
        setResult(done.result)
        setPortfolio(null)
      }
      setJobId(jobId)
      setAnalysisId(id => id + 1)   // force Dashboard remount → resets all internal tab/drill state
      setView(VIEW.DASHBOARD)
      toast.success('Analysis complete!')
    } catch (err) {
      activePollRef.current = null
      // Only show error if this wasn't a user-initiated cancellation
      if (err.message !== 'cancelled') {
        toast.error(err.message || 'Analysis failed')
      }
      setView(VIEW.LANDING)
    }
  }, [])

  // Function: handleBack
  const handleBack = () => {
    // Cancel poll if user navigates back mid-analysis
    if (activePollRef.current) {
      activePollRef.current.cancel()
      activePollRef.current = null
    }
    setView(VIEW.LANDING)
    setResult(null)
    setPortfolio(null)
  }

  // Function: handlePortalLogout
  const handlePortalLogout = async () => {
    await logoutFromPortal()
    window.location.href = getPortalLoginUrl()
  }

  if (!authReady) {
    return (
      <div className="min-h-screen bg-slate-50 text-slate-800 flex items-center justify-center">
        <div className="px-6 py-4 rounded-xl border border-slate-200 bg-white">
          Validating portal session...
        </div>
      </div>
    )
  }

  if (authError) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-sky-50 to-cyan-50 text-slate-800 flex items-center justify-center p-5">
        <div className="w-full max-w-xl rounded-2xl border border-slate-200 bg-white p-8 shadow-2xl">
          <p className="text-xs uppercase tracking-[0.2em] text-sky-600">Access Control</p>
          <h1 className="mt-2 text-2xl font-semibold">Code Analysis session required</h1>
          <p className="mt-4 text-sm text-slate-600 leading-6">{authError}</p>
          <div className="mt-6 flex gap-3">
            <button
              type="button"
              onClick={() => {
                window.location.href = getPortalLoginUrl()
              }}
              className="px-4 py-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-blue-300 text-sm"
            >
              Go to Portal Login
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="ca-app min-h-screen">
      <header className="az-topbar">
        <div className="az-logo-mark">
          <span style={{ fontSize: 12, fontWeight: 700 }}>{'</>'}</span>
        </div>
        <div className="flex-1 min-w-0 flex items-center gap-4">
          <div>
            <p className="az-topbar-eyebrow">Unified Modernization Suite</p>
            <p className="az-topbar-title">Code Analysis Workspace</p>
          </div>
          {/* Nav links */}
          <nav className="hidden sm:flex items-center gap-1.5 ml-2">
            <button
              type="button"
              onClick={() => handleBack()}
              data-active={view === VIEW.LANDING}
              className="az-topbar-btn"
            >
              New Analysis
            </button>
            <button
              type="button"
              disabled={!result && !portfolio}
              onClick={() => (result || portfolio) && setView(VIEW.DASHBOARD)}
              data-active={view === VIEW.DASHBOARD}
              className="az-topbar-btn"
            >
              Results
            </button>
            <button type="button" disabled={view === VIEW.LOADING} className="az-topbar-btn">
              History
            </button>
          </nav>
        </div>
        <span className="az-topbar-user">{authUser?.username}</span>
        <button
          type="button"
          onClick={() => {
            window.location.href = getPortalHomeUrl()
          }}
          className="az-topbar-btn"
        >
          Portal Home
        </button>
        {authUser?.role === 'admin' && (
          <button
            type="button"
            onClick={() => {
              try {
                window.location.href = new URL('/admin', getPortalHomeUrl()).href
              } catch {
                window.location.href = '/admin'
              }
            }}
            className="az-topbar-btn"
          >
            Admin Console
          </button>
        )}
        <button type="button" onClick={handlePortalLogout} className="az-topbar-btn">
          Logout
        </button>
      </header>

      <AnimatePresence mode="wait">
        {view === VIEW.LANDING && (
          <motion.div
            key="landing"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0, scale: 0.97 }}
            transition={{ duration: 0.3 }}
          >
            <LandingPage onAnalyse={handleAnalyse} />
          </motion.div>
        )}

        {view === VIEW.LOADING && (
          <motion.div
            key="loading"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
          >
            <ProgressOverlay job={job} />
          </motion.div>
        )}

        {view === VIEW.DASHBOARD && (
          <motion.div
            key="dashboard"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.4 }}
          >
            <Dashboard
              key={analysisId}
              result={result}
              portfolio={portfolio}
              jobId={jobId}
              onBack={handleBack}
            />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
