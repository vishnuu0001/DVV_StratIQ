// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: Dashboard — frontend/src (App.jsx)
// Date: 2026-02-22
// ---------------------------------------------------------------------------
import React, { useEffect } from 'react'
import { Routes, Route, Navigate, useNavigate, Outlet } from 'react-router-dom'
import { DashboardProvider, useDashboard } from './context/DashboardContext'
import ConnectionPanel from './components/ConnectionPanel'
import ServiceNowLogin from './pages/ServiceNowLogin'
import TopMenu from './components/TopMenu'
import Navbar from './components/Navbar'
import ExecutiveCockpit from './pages/ExecutiveCockpit'
import ServiceRequests from './pages/ServiceRequests'
import IncidentCommand from './pages/IncidentCommand'
import ChangeRisk from './pages/ChangeRisk'
import AutomationMining from './pages/AutomationMining'
import SLAKPIDashboard from './pages/SLAKPIDashboard'
import TransformationAutomationDashboard from './pages/TransformationAutomationDashboard'
import AdHocEnhancementDashboard from './pages/AdHocEnhancementDashboard'
import PeopleCapacityDashboard from './pages/PeopleCapacityDashboard'

// Function: RootRedirect
function RootRedirect() {
  const { connected, synced, statusLoading } = useDashboard()
  if (statusLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-navy-950 via-navy-900 to-navy-800">
        <div className="flex flex-col items-center gap-4">
          <div className="w-10 h-10 border-2 border-accent-cyan border-t-transparent rounded-full animate-spin shadow-glow-md" />
          <p className="text-slate-400 text-sm">Loading dashboard...</p>
        </div>
      </div>
    )
  }
  if (connected && synced) return <Navigate to="/dashboard" replace />
  return <Navigate to="/connect" replace />
}

// Function: DashboardLayout
function DashboardLayout() {
  const { connected, synced, statusLoading } = useDashboard()
  const navigate = useNavigate()

  useEffect(() => {
    if (!statusLoading && (!connected || !synced)) {
      navigate('/connect', { replace: true })
    }
  }, [connected, synced, statusLoading, navigate])

  if (statusLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-navy-950 via-navy-900 to-navy-800">
        <div className="w-10 h-10 border-2 border-accent-cyan border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-navy-950 via-navy-900 to-navy-800 flex flex-col">
      <TopMenu />
      <Navbar />
      <main className="flex-1 overflow-auto">
        <Outlet />
      </main>
    </div>
  )
}

// Function: AppRoutes
function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<RootRedirect />} />
      <Route path="/login" element={<ServiceNowLogin />} />
      <Route path="/connect" element={<ConnectionPanel />} />
      <Route path="/dashboard" element={<DashboardLayout />}>
        <Route index element={<ExecutiveCockpit />} />
        <Route path="service-requests" element={<ServiceRequests />} />
        <Route path="incidents" element={<IncidentCommand />} />
        <Route path="changes" element={<ChangeRisk />} />
        <Route path="automation" element={<AutomationMining />} />
        <Route path="sla-kpi" element={<SLAKPIDashboard />} />
        <Route path="transformation" element={<TransformationAutomationDashboard />} />
        <Route path="adhoc-enhancements" element={<AdHocEnhancementDashboard />} />
        <Route path="people-capacity" element={<PeopleCapacityDashboard />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

// Function: App
export default function App() {
  return (
    <DashboardProvider>
      <AppRoutes />
    </DashboardProvider>
  )
}
