// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: AI_Vehicle_Loan — frontend/src/components (LoanOptions.js)
// Date: 2026-01-20
// ---------------------------------------------------------------------------
import React from 'react';
import { ChevronRight, Zap, Shield } from 'lucide-react';

// Function: LoanOptions
const LoanOptions = ({ setView }) => {
  return (
    <div className="container mx-auto px-6 py-16 animate-in fade-in duration-700">
      <h1 className="text-5xl font-black text-gray-900 mb-4">Car <span className="text-brand">Loans.</span></h1>
      <p className="text-gray-500 mb-12 font-medium max-w-2xl">Tailored financing for new, used, and electric vehicles with real-time AI approval.</p>
      <div className="grid md:grid-cols-2 gap-8">
        <div className="bg-white p-8 rounded-[32px] border border-gray-100 shadow-xl flex flex-col justify-between">
          <div>
            <div className="w-12 h-12 bg-brand/10 rounded-xl flex items-center justify-center mb-6 text-brand"><Zap /></div>
            <h3 className="text-2xl font-black mb-2">New Car Finance</h3>
            <p className="text-brand font-bold text-lg mb-4">Rates from 4.99% p.a.</p>
            <p className="text-gray-500 font-medium mb-8">Fixed rates for brand new vehicles with instant pre-approval.</p>
          </div>
          <button onClick={() => setView('home')} className="flex items-center justify-between w-full p-4 bg-gray-900 text-white rounded-2xl font-bold hover:bg-black transition-colors">
            Explore Inventory <ChevronRight />
          </button>
        </div>
        <div className="bg-white p-8 rounded-[32px] border border-gray-100 shadow-xl flex flex-col justify-between">
          <div>
            <div className="w-12 h-12 bg-blue-50 rounded-xl flex items-center justify-center mb-6 text-blue-600"><Shield /></div>
            <h3 className="text-2xl font-black mb-2">Used Car Finance</h3>
            <p className="text-blue-600 font-bold text-lg mb-4">Rates from 6.75% p.a.</p>
            <p className="text-gray-500 font-medium mb-8">Competitive financing for vehicles up to 10 years old.</p>
          </div>
          <button onClick={() => setView('home')} className="flex items-center justify-between w-full p-4 bg-gray-900 text-white rounded-2xl font-bold hover:bg-black transition-colors">
            Explore Inventory <ChevronRight />
          </button>
        </div>
      </div>
    </div>
  );
};

export default LoanOptions;