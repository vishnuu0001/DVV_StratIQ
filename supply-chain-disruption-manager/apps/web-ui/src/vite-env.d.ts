/// <reference types="vite/client" />
// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: supply-chain-disruption-manager — apps/web-ui/src (vite-env.d.ts)
// Date: 2025-11-01
// ---------------------------------------------------------------------------

interface ImportMetaEnv {
  readonly VITE_KG_API_URL: string
  readonly VITE_KG_API_KEY: string
  readonly VITE_INSPECTOR_API_URL: string
  readonly VITE_INSPECTOR_API_KEY: string
  readonly VITE_AGENT_API_URL: string
  readonly VITE_AGENT_API_KEY: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
