// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: AI_Vehicle_Loan — frontend/src/components (Dashboard.js)
// Date: 2025-10-06
// ---------------------------------------------------------------------------
import React, { useEffect, useState } from 'react';
import apiClient from '../apiClient';
import VehicleCard from './VehicleCard';
import { BadgeCheck, TrendingUp, Users, Loader2 } from 'lucide-react';

// Function: Dashboard
const Dashboard = ({ onAnalyze }) => {
  const [vehicles, setVehicles] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Function: fetchData
    const fetchData = async () => {
      const apiBase = process.env.REACT_APP_API_URL || '/api/vehicle-loan';
      try {
        const [vRes, sRes] = await Promise.all([
          apiClient.get(`${apiBase}/vehicles`),
          apiClient.get(`${apiBase}/stats`)
        ]);
        setVehicles(vRes.data);
        setStats(sRes.data);
      } catch (e) {
        console.error("Fetch error", e);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) return <div className="h-96 flex items-center justify-center"><Loader2 className="animate-spin text-brand h-10 w-10"/></div>;

  return (
    <div className="container mx-auto px-6 py-10">
      {/* Real-time Stats Header */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
        <div className="bg-white p-6 rounded-3xl shadow-sm border border-gray-100 flex items-center gap-4">
          <div className="p-3 bg-brand/10 text-brand rounded-2xl"><BadgeCheck size={24}/></div>
          <div><p className="text-xs font-bold text-gray-400 uppercase">Approvals Today</p><p className="text-2xl font-black">{stats?.todays_approvals}</p></div>
        </div>
        <div className="bg-white p-6 rounded-3xl shadow-sm border border-gray-100 flex items-center gap-4">
          <div className="p-3 bg-blue-50 text-blue-600 rounded-2xl"><TrendingUp size={24}/></div>
          <div><p className="text-xs font-bold text-gray-400 uppercase">Current Avg Rate</p><p className="text-2xl font-black">{stats?.average_rate}</p></div>
        </div>
        <div className="bg-white p-6 rounded-3xl shadow-sm border border-gray-100 flex items-center gap-4">
          <div className="p-3 bg-purple-50 text-purple-600 rounded-2xl"><Users size={24}/></div>
          <div><p className="text-xs font-bold text-gray-400 uppercase">Live Assessments</p><p className="text-2xl font-black">{stats?.active_users}</p></div>
        </div>
      </div>

      <h2 className="text-3xl font-black mb-8">Featured <span className="text-brand">Inventory.</span></h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        {vehicles.map(v => (
          <VehicleCard
            key={v.id}
            vehicle={v}
            onAnalyze={onAnalyze} // Passing prop down to fix error
          />
        ))}
      </div>
    </div>
  );
};

export default Dashboard;