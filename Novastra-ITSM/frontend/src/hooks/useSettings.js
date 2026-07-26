// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: Novastra-ITSM — frontend/src/hooks (useSettings.js)
// Date: 2025-07-30
// ---------------------------------------------------------------------------
import { useState, useEffect } from 'react'
import { getSettings } from '../services/api.js'

/**
 * Shared hook — loads and caches LLM settings from the server.
 * Components that need the current provider can use this.
 */
// Function: useSettings
export function useSettings() {
  const [settings, setSettings] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    getSettings()
      .then(({ data }) => setSettings(data))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  return { settings, loading, error }
}
