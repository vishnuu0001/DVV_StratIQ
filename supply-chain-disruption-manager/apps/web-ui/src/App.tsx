// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: supply-chain-disruption-manager — apps/web-ui/src (App.tsx)
// Date: 2025-09-16
// ---------------------------------------------------------------------------
import React from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Layout } from './components/Layout'
import { Overview } from './views/Overview'
import { SignalStream } from './views/SignalStream'
import { KnowledgeGraph } from './views/KnowledgeGraph'
import { IncidentCenter } from './views/IncidentCenter'
import { AgentWorkbench } from './views/AgentWorkbench'
import { AdapterOps } from './views/AdapterOps'
import { SchemaBrowser } from './views/SchemaBrowser'
import { ReplayDLQ } from './views/ReplayDLQ'

// Function: App
export default function App() {
  return (
    <BrowserRouter basename={import.meta.env.BASE_URL}>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Overview />} />
          <Route path="signals" element={<SignalStream />} />
          <Route path="graph" element={<KnowledgeGraph />} />
          <Route path="incidents" element={<IncidentCenter />} />
          <Route path="agents" element={<AgentWorkbench />} />
          <Route path="adapters" element={<AdapterOps />} />
          <Route path="schemas" element={<SchemaBrowser />} />
          <Route path="replay" element={<ReplayDLQ />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
