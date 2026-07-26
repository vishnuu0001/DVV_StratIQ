// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: OpportunityTracker — frontend/src (App.jsx)
// Date: 2026-06-03
// ---------------------------------------------------------------------------
import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './contexts/AuthContext';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';

// Function: RequireAuth
function RequireAuth({ children }) {
  const { token, loading } = useAuth();
  if (loading) return <div className="min-h-screen bg-slate-950 flex items-center justify-center"><div className="w-8 h-8 rounded-full border-2 border-cyan-500 border-t-transparent animate-spin" /></div>;
  return token ? children : <Navigate to="login" replace />;
}

// Function: App
export default function App() {
  return (
    <Routes>
      <Route path="login" element={<LoginPage />} />
      <Route path="/*" element={<RequireAuth><DashboardPage /></RequireAuth>} />
      <Route index element={<Navigate to="dashboard" replace />} />
    </Routes>
  );
}
