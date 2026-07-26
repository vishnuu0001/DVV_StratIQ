// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: SSDLC_Process_Assessment — frontend/src (App.tsx)
// Date: 2025-09-07
// ---------------------------------------------------------------------------
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { WorkbookProvider } from './context/WorkbookContext'
import AppLayout from './components/layout/AppLayout'
import UploadPage from './pages/UploadPage'
import DashboardPage from './pages/DashboardPage'
import TowerModelPage from './pages/TowerModelPage'
import VendorLandscapePage from './pages/VendorLandscapePage'
import HeatmapPage from './pages/HeatmapPage'
import TechMGrowthPage from './pages/TechMGrowthPage'
import TransformationCapacityPage from './pages/TransformationCapacityPage'
import OperatingModelPage from './pages/OperatingModelPage'
import NotFoundPage from './pages/NotFoundPage'

// Function: App
export default function App() {
  return (
    <WorkbookProvider>
      <BrowserRouter basename="/ssdlc">
        <Routes>
          <Route element={<AppLayout />}>
            <Route path="/" element={<UploadPage />} />
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/tower-model" element={<TowerModelPage />} />
            <Route path="/vendor-landscape" element={<VendorLandscapePage />} />
            <Route path="/heatmap" element={<HeatmapPage />} />
            <Route path="/techm-growth" element={<TechMGrowthPage />} />
            <Route path="/transformation-capacity" element={<TransformationCapacityPage />} />
            <Route path="/operating-model" element={<OperatingModelPage />} />
            <Route path="/404" element={<NotFoundPage />} />
            <Route path="*" element={<Navigate to="/404" replace />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </WorkbookProvider>
  )
}
