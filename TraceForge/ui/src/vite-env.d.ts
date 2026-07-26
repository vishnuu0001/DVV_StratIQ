/// <reference types="vite/client" />
// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: TraceForge — ui/src (vite-env.d.ts)
// Date: 2026-05-13
// ---------------------------------------------------------------------------

interface ImportMetaEnv {
  readonly VITE_TF_API_URL?: string
  readonly VITE_PORTAL_HOME_URL?: string
  readonly VITE_PORTAL_LOGIN_URL?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
