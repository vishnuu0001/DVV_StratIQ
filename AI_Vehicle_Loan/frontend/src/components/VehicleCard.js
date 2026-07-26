// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: AI_Vehicle_Loan — frontend/src/components (VehicleCard.js)
// Date: 2025-10-06
// ---------------------------------------------------------------------------
import React from 'react';
import { Tag } from 'lucide-react';

// Function: VehicleCard
const VehicleCard = ({ vehicle, onAnalyze }) => {
  return (
    <div className="bg-white rounded-[32px] shadow-lg border border-gray-50 p-3 group transition-all hover:shadow-2xl hover:-translate-y-1">
      {/* Top Section: Image & Category */}
      <div className="relative h-48 rounded-[24px] overflow-hidden mb-5">
        <img src={vehicle.image} alt={vehicle.model} className="w-full h-full object-cover" />
        <div className="absolute top-3 right-3 bg-white/90 backdrop-blur px-4 py-1.5 rounded-full text-[10px] font-black tracking-widest text-gray-800 uppercase shadow-sm">
          {vehicle.type}
        </div>
      </div>

      {/* Content Section */}
      <div className="px-3 pb-3">
        <div className="text-brand font-bold text-xs mb-1 uppercase tracking-tighter">{vehicle.make}</div>
        <h3 className="text-2xl font-extrabold text-gray-900 mb-4">{vehicle.model}</h3>

        {/* Semantic Tags */}
        <div className="flex gap-2 mb-8 flex-wrap">
          {vehicle.tags.map(tag => (
            <span key={tag} className="flex items-center gap-1 bg-brand/5 text-brand text-[9px] font-black px-2.5 py-1.5 rounded-lg uppercase tracking-tight">
              <Tag size={10} className="stroke-[3px]" /> {tag}
            </span>
          ))}
        </div>

        {/* Action Bar */}
        <div className="flex items-center justify-between border-t border-gray-100 pt-5 mt-2">
          <div>
            <div className="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-0.5">Est. Price</div>
            <div className="text-2xl font-black text-gray-900">${vehicle.price.toLocaleString()}</div>
          </div>

          {/* THE SIMULATION BUTTON */}
          <button
            onClick={() => onAnalyze(vehicle)} // Executes the simulation in App.js
            className="w-14 h-14 bg-brand text-white rounded-full flex items-center justify-center hover:scale-110 active:scale-95 transition-all shadow-xl shadow-brand/30"
            title="Analyze Loan Eligibility"
          >
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="m9 18 6-6-6-6"/>
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
};

export default VehicleCard;