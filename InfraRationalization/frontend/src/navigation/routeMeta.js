// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: InfraRationalization — frontend/src/navigation (routeMeta.js)
// Date: 2026-08-04
// ---------------------------------------------------------------------------
import {
  HomeRegular,
  ScanRegular,
  RocketRegular,
  DocumentRegular,
} from '@fluentui/react-icons'

// Drives both Sidebar (sidebar: true entries) and Breadcrumb (all entries).
// Param routes (":scanId") are drill-in only, reached from Dashboard — they
// intentionally have no icon/sidebar entry.
export const ROUTES = [
  { path: '/', icon: HomeRegular, label: 'Dashboard', sidebar: true },
  { path: '/new-scan', icon: ScanRegular, label: 'New Scan', sidebar: true },
  { path: '/execution-support', icon: RocketRegular, label: 'Execution Support', sidebar: true },
  { path: '/pdf-analysis', icon: DocumentRegular, label: 'PDF Analysis', sidebar: true },
  { path: '/scans/progress/:scanId', label: 'Scan Progress' },
  { path: '/scans/:scanId', label: 'Scan Detail' },
  { path: '/scans/:scanId/intelligence', label: 'Network Intelligence' },
]

// Function: matchRoute
// Resolves a live pathname (e.g. "/scans/abc123") against ROUTES' path
// patterns (e.g. "/scans/:scanId"), for breadcrumb label lookup.
export function matchRoute(pathname) {
  const segments = pathname.split('/').filter(Boolean)
  return ROUTES.find((route) => {
    const routeSegments = route.path.split('/').filter(Boolean)
    if (routeSegments.length !== segments.length) return false
    return routeSegments.every((seg, i) => seg.startsWith(':') || seg === segments[i])
  })
}
