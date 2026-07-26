// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: TraceForge — ui/src (App.tsx)
// Date: 2025-07-18
// ---------------------------------------------------------------------------
import { useState } from 'react'
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

// Function: App
export default function App() {
  const [portalUser] = useState<PortalUser | null>(() => decodePortalUser(getPortalToken()))

  return (
    <div className="flex h-screen bg-gray-950 text-gray-100">
      <aside className="w-56 border-r border-white/10 flex flex-col shrink-0">
        <div className="p-4 border-b border-white/10">
          <h1 className="text-sm font-bold text-white">TraceForge</h1>
          <p className="text-[10px] text-gray-500">AI-assisted SDLC artifact factory</p>
        </div>
        <ProjectSwitcher />
        <GroupedNavigation overview={{ to: '/', label: 'Overview', end: true }} groups={NAV_GROUPS} />
      </aside>
      <div className="flex-1 flex flex-col overflow-hidden">
        <header className="sticky top-0 z-30 border-b border-sky-200/80 bg-sky-300/85 backdrop-blur-xl shrink-0">
          <div className="px-6 py-3 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
            <div>
              <p className="text-[11px] uppercase tracking-[0.2em] text-white">Unified Modernization Suite</p>
              <h2 className="text-gray-100 font-semibold">TraceForge Workspace</h2>
            </div>
            <div className="flex items-center gap-2 text-sm">
              {portalUser?.username && <span className="text-white text-xs">{portalUser.username}</span>}
              <button
                type="button"
                onClick={() => { window.location.href = getPortalHomeUrl() }}
                className="px-3 py-1.5 rounded-lg border border-white/45 bg-sky-400/35 text-white hover:bg-sky-400/55 text-xs font-medium"
              >
                Portal Home
              </button>
              {portalUser?.role === 'admin' && (
                <button
                  type="button"
                  onClick={() => { window.location.href = getPortalAdminUrl() }}
                  className="px-3 py-1.5 rounded-lg border border-white/45 bg-sky-400/35 text-white hover:bg-sky-400/55 text-xs font-medium"
                >
                  Admin Console
                </button>
              )}
              <button
                type="button"
                onClick={logoutFromPortal}
                className="px-3 py-1.5 rounded-lg border border-white/45 bg-sky-400/35 text-white hover:bg-sky-400/55 text-xs font-semibold"
              >
                Logout
              </button>
            </div>
          </div>
        </header>
        <main className="flex-1 overflow-y-auto">
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
