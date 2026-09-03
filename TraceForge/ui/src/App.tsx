// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: TraceForge — ui/src (App.tsx)
// Date: 2025-07-18
// ---------------------------------------------------------------------------
import { useEffect, useRef, useState } from 'react'
import { Navigate, Route, Routes } from 'react-router-dom'
import OverviewPage from './pages/OverviewPage'
import SourcesPage from './pages/SourcesPage'
import ConnectorsPage from './pages/ConnectorsPage'
import RequirementsPage from './pages/RequirementsPage'
import QualityPage from './pages/QualityPage'
import DocumentsPage from './pages/DocumentsPage'
import TestCasesPage from './pages/TestCasesPage'
import ScriptsPage from './pages/ScriptsPage'
import CoveragePage from './pages/CoveragePage'
import TraceabilityPage from './pages/TraceabilityPage'
import ImpactAnalysisPage from './pages/ImpactAnalysisPage'
import BaselinesPage from './pages/BaselinesPage'
import ReviewsPage from './pages/ReviewsPage'
import ArtifactsPage from './pages/ArtifactsPage'
import EvidencePacksPage from './pages/EvidencePacksPage'
import AuditPage from './pages/AuditPage'
import TemplatesPage from './pages/TemplatesPage'
import IntegrationsPage from './pages/IntegrationsPage'
import ProjectSettingsPage from './pages/ProjectSettingsPage'
import ProjectSwitcher from './components/ProjectSwitcher'
import GroupedNavigation, { type NavigationGroup } from './components/GroupedNavigation'
import {
  decodePortalUser,
  getPortalAdminUrl,
  getPortalHomeUrl,
  getPortalToken,
  logoutFromPortal,
  type PortalUser,
} from './lib/portalAuth'

const NAV_GROUPS: NavigationGroup[] = [
  {
    label: 'Discovery',
    items: [
      { to: '/discovery/sources', label: 'Sources' },
      { to: '/discovery/connectors', label: 'Connectors' },
    ],
  },
  {
    label: 'Requirements',
    items: [
      { to: '/requirements/register', label: 'Requirement Register' },
      { to: '/requirements/quality', label: 'Quality & Conflicts' },
    ],
  },
  {
    label: 'Specifications',
    items: [
      { to: '/specifications/brd', label: 'BRD' },
      { to: '/specifications/srs-frs', label: 'SRS / FRS' },
      { to: '/specifications/functional-design', label: 'Functional Design' },
      { to: '/specifications/architecture', label: 'Architecture & Design' },
    ],
  },
  {
    label: 'Verification',
    items: [
      { to: '/verification/test-plan', label: 'Test Plan' },
      { to: '/verification/test-cases', label: 'Test Cases' },
      { to: '/verification/test-scripts', label: 'Test Scripts' },
      { to: '/verification/coverage', label: 'Coverage' },
    ],
  },
  {
    label: 'Traceability',
    items: [
      { to: '/traceability/explorer', label: 'Traceability Explorer' },
      { to: '/traceability/impact', label: 'Impact Analysis' },
      { to: '/traceability/baselines', label: 'Baselines' },
    ],
  },
  {
    label: 'Governance',
    items: [
      { to: '/governance/reviews', label: 'Reviews & Approvals' },
      { to: '/governance/artifacts', label: 'Artifacts' },
      { to: '/governance/evidence', label: 'Evidence Packs' },
      { to: '/governance/audit', label: 'Audit Trail' },
    ],
  },
  {
    label: 'Settings',
    items: [
      { to: '/settings/templates', label: 'Templates' },
      { to: '/settings/integrations', label: 'Integrations' },
      { to: '/settings/project', label: 'Project Settings' },
    ],
  },
]

const READ_ONLY_USERNAMES = new Set(['vishnuu', 'prasanna', 'siva'])

// Function: App
export default function App() {
  const [portalUser] = useState<PortalUser | null>(() => decodePortalUser(getPortalToken()))
  const workspaceRef = useRef<HTMLDivElement | null>(null)
  const readOnly = Boolean(portalUser?.read_only) ||
    READ_ONLY_USERNAMES.has(String(portalUser?.username || '').trim().toLowerCase())

  useEffect(() => {
    const root = workspaceRef.current
    if (!root || !readOnly) return undefined

    const disableOperations = () => {
      root.querySelectorAll<HTMLButtonElement | HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>(
        'button, input, textarea, select',
      ).forEach((control) => {
        const label = (control.textContent || '').trim()
        const isViewControl = Boolean(
          control.closest('header') ||
          control.closest('nav') ||
          (control.tagName === 'SELECT' && control.closest('.az-project-switcher')) ||
          control.hasAttribute('data-read-only-allow') ||
          control.getAttribute('aria-expanded') !== null ||
          control.getAttribute('aria-pressed') !== null ||
          (/text-left/.test(control.className) && !/(create|edit|configure|approve|reject|delete|reset|run|generate)/i.test(label)) ||
          /^(view|open|show|close|previous|next|back)\b/i.test(label)
        )
        if (!isViewControl) {
          if (!control.disabled) control.disabled = true
          control.setAttribute('aria-disabled', 'true')
          control.title ||= 'Disabled: this account has read-only access'
        }
      })
    }

    disableOperations()
    const observer = new MutationObserver(disableOperations)
    observer.observe(root, { attributes: true, attributeFilter: ['disabled'], childList: true, subtree: true })
    return () => observer.disconnect()
  }, [readOnly])

  return (
    <div ref={workspaceRef} data-read-only={readOnly ? 'true' : 'false'} className="az-shell">
      <aside className="az-side-nav">
        <div className="az-side-nav-header">
          <h1 className="az-side-nav-brand">TraceForge</h1>
          <p className="az-side-nav-sub">AI-assisted SDLC artifact factory</p>
        </div>
        <ProjectSwitcher />
        <GroupedNavigation overview={{ to: '/', label: 'Overview', end: true }} groups={NAV_GROUPS} />
      </aside>
      <div className="flex-1 flex flex-col overflow-hidden">
        <header className="az-topbar">
          <div className="flex-1 min-w-0">
            <p className="az-topbar-eyebrow">Unified Modernization Suite</p>
            <p className="az-topbar-title">TraceForge Workspace</p>
          </div>
          <div className="flex items-center gap-2 text-sm">
            {portalUser?.username && <span className="az-topbar-user text-xs">{portalUser.username}</span>}
            <button type="button" onClick={() => { window.location.href = getPortalHomeUrl() }} className="az-topbar-btn">
              Portal Home
            </button>
            {portalUser?.role === 'admin' && !readOnly && (
              <button type="button" onClick={() => { window.location.href = getPortalAdminUrl() }} className="az-topbar-btn">
                Admin Console
              </button>
            )}
            <button type="button" onClick={logoutFromPortal} className="az-topbar-btn">
              Logout
            </button>
          </div>
        </header>
        {readOnly && (
          <div className="az-read-only-banner" role="status">
            Enhancement is in Progress. Once done, the full features will be enabled
          </div>
        )}
        <main className="az-main flex-1 overflow-y-auto">
          <Routes>
            <Route path="/" element={<OverviewPage />} />
            <Route path="/discovery/sources" element={<SourcesPage />} />
            <Route path="/discovery/connectors" element={<ConnectorsPage />} />
            <Route path="/requirements/register" element={<RequirementsPage />} />
            <Route path="/requirements/quality" element={<QualityPage />} />
            <Route path="/specifications/brd" element={<DocumentsPage title="Business Requirements Document" kinds={['BRD_DOCX']} />} />
            <Route path="/specifications/srs-frs" element={<DocumentsPage title="Software / Functional Requirements Specification" kinds={['FRD_DOCX']} />} />
            <Route path="/specifications/functional-design" element={<DocumentsPage title="Functional Design Specification" kinds={['FSD_DOCX']} />} />
            <Route path="/specifications/architecture" element={<DocumentsPage title="Architecture & Solution Design" kinds={['SOLUTION_DOC_DOCX']} />} />
            <Route path="/verification/test-plan" element={<TestCasesPage />} />
            <Route path="/verification/test-cases" element={<TestCasesPage />} />
            <Route path="/verification/test-scripts" element={<ScriptsPage />} />
            <Route path="/verification/coverage" element={<CoveragePage />} />
            <Route path="/traceability/explorer" element={<TraceabilityPage />} />
            <Route path="/traceability/impact" element={<ImpactAnalysisPage />} />
            <Route path="/traceability/baselines" element={<BaselinesPage />} />
            <Route path="/governance/reviews" element={<ReviewsPage />} />
            <Route path="/governance/artifacts" element={<ArtifactsPage />} />
            <Route path="/governance/evidence" element={<EvidencePacksPage />} />
            <Route path="/governance/audit" element={<AuditPage />} />
            <Route path="/settings/templates" element={<TemplatesPage />} />
            <Route path="/settings/integrations" element={<IntegrationsPage />} />
            <Route path="/settings/project" element={<ProjectSettingsPage />} />

            <Route path="/sources" element={<Navigate to="/discovery/sources" replace />} />
            <Route path="/requirements" element={<Navigate to="/requirements/register" replace />} />
            <Route path="/brd" element={<Navigate to="/specifications/brd" replace />} />
            <Route path="/testcases" element={<Navigate to="/verification/test-cases" replace />} />
            <Route path="/scripts" element={<Navigate to="/verification/test-scripts" replace />} />
            <Route path="/traceability" element={<Navigate to="/traceability/explorer" replace />} />
            <Route path="/artifacts" element={<Navigate to="/governance/artifacts" replace />} />
            <Route path="/audit" element={<Navigate to="/governance/audit" replace />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>
      </div>
    </div>
  )
}
