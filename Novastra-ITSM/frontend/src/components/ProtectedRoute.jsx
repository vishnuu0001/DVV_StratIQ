// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: Novastra-ITSM — frontend/src/components (ProtectedRoute.jsx)
// Date: 2025-07-31
// ---------------------------------------------------------------------------
import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext.jsx'

// Function: ProtectedRoute
export default function ProtectedRoute({ children }) {
  const { isAuthenticated, checkingSso } = useAuth()
  const location = useLocation()

  // A #authToken= from the portal launcher is still being exchanged for a
  // local session — wait rather than redirecting, or the exchange gets
  // wiped out by the URL rewrite that redirecting to /login performs (see
  // the comment on AuthContext's checkingSso state for why).
  if (checkingSso) {
    return (
      <div className="flex h-screen items-center justify-center bg-slate-950 text-sm text-slate-400">
        Signing you in…
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }
  return children
}
