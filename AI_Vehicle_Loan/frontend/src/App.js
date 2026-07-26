// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: AI_Vehicle_Loan — frontend/src (App.js)
// Date: 2025-08-22
// ---------------------------------------------------------------------------
import React, { useState } from 'react';
import apiClient from './apiClient';
import Navbar from './components/Navbar';
import Dashboard from './components/Dashboard';
import ChatWidget from './components/ChatWidget';
import LoanOptions from './components/LoanOptions';
import HowItWorks from './components/HowItWorks';
import Resources from './components/Resources';
import { AuthProvider, useAuth } from './AuthContext';

// Function: AppContent
function AppContent() {
  const { user, login, mockProfiles } = useAuth();
  const [selectedProfileId, setSelectedProfileId] = useState(null);
  const [view, setView] = useState('home'); // Controls the main content view
  const [analysisData, setAnalysisData] = useState(null);
  const [isChatOpen, setIsChatOpen] = useState(false);

  // Simulation Login Screen
  if (!user) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center p-6">
        <div className="bg-white p-12 rounded-[40px] shadow-2xl max-w-lg w-full text-center">
          <h1 className="text-3xl font-black mb-10 text-gray-900">Tech M<span className="text-brand"> Vehicle Loans</span></h1>
          <div className="space-y-4 mb-10">
            {mockProfiles.map(profile => (
              <label key={profile.id} className={`flex items-center gap-4 p-5 rounded-3xl border-2 transition-all cursor-pointer ${selectedProfileId === profile.id ? 'border-brand bg-brand/5' : 'border-gray-100'}`}>
                <input
                  type="checkbox"
                  checked={selectedProfileId === profile.id}
                  onChange={() => setSelectedProfileId(profile.id)}
                  className="w-6 h-6 accent-brand"
                />
                <span className="font-black text-gray-900">{profile.label}</span>
              </label>
            ))}
          </div>
          <button
            disabled={!selectedProfileId}
            onClick={() => login(selectedProfileId)}
            className="w-full py-5 bg-brand text-white font-black rounded-2xl shadow-xl disabled:opacity-30"
          >
            Enter Simulation
          </button>
        </div>
      </div>
    );
  }

  // Activity Logic: Pass user score to backend
  // Function: handleAnalyzeVehicle
  const handleAnalyzeVehicle = async (vehicle) => {
    setIsChatOpen(true);
    setAnalysisData({ status: 'analyzing', vehicle });
    try {
      const apiBase = process.env.REACT_APP_API_URL || '/api/vehicle-loan';
      const res = await apiClient.post(`${apiBase}/analyze-loan`, {
        vehicle_id: vehicle.id,
        user_score: user.score
      });
      setTimeout(() => setAnalysisData({ status: 'complete', vehicle, result: res.data }), 1200);
    } catch (e) {
      setAnalysisData({ status: 'error' });
    }
  };

  // View Router
  // Function: renderView
  const renderView = () => {
    switch (view) {
      case 'car-loans': return <LoanOptions setView={setView} />;
      case 'how-it-works': return <HowItWorks />;
      case 'resources': return <Resources />;
      default: return <Dashboard onAnalyze={handleAnalyzeVehicle} />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50/50 relative">
      {/* FIX: Explicitly passing setView and currentView as props */}
      <Navbar setView={setView} currentView={view} />

      <main className="pb-24">
        {renderView()}
      </main>

      <ChatWidget
        isOpen={isChatOpen}
        setIsOpen={setIsChatOpen}
        analysis={analysisData}
      />
    </div>
  );
}

// Function: App
export default function App() {
  return <AuthProvider><AppContent /></AuthProvider>;
}