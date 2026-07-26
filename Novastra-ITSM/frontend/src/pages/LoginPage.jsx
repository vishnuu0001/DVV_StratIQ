// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: Novastra-ITSM — frontend/src/pages (LoginPage.jsx)
// Date: 2025-12-22
// ---------------------------------------------------------------------------
import { useEffect } from 'react'
import { useNavigate, useLocation, useSearchParams } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext.jsx'

const MODULE_HOME_ROUTE = '/ticket-analysis'
const PORTAL_LOGIN_URL = import.meta.env.VITE_PORTAL_LOGIN_URL || '/login'

// Novastra-ITSM has no login UI of its own — access is always
// granted through the central portal's session hand-off (see AuthContext's
// #authToken hash consumption, triggered by the "Open Novastra-ITSM"
// launcher). This route exists only to:
//   (a) finish an OAuth provider redirect that arrives with ?token=..., or
//   (b) send anyone who lands here directly back to the real portal login.
// Nothing renders here — there is no form, no credential prompt, no page.
// Function: LoginPage
export default function LoginPage() {
  const navigate = useNavigate()
  const location = useLocation()
  const [searchParams] = useSearchParams()
  const { loginWithToken, isAuthenticated, token } = useAuth()
  const from = location.state?.from?.pathname || MODULE_HOME_ROUTE

  useEffect(() => {
    const oauthToken = searchParams.get('token')
    if (oauthToken) {
      loginWithToken(oauthToken).then(() => navigate(from, { replace: true }))
      return
    }
    if (isAuthenticated && token) {
      navigate(from, { replace: true })
      return
    }
    window.location.href = PORTAL_LOGIN_URL
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  return null
}
