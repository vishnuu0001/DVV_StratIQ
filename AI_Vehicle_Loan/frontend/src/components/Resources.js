// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: AI_Vehicle_Loan — frontend/src/components (Resources.js)
// Date: 2026-02-25
// ---------------------------------------------------------------------------
import React from 'react';

// Function: Resources
const Resources = () => {
  return (
    <div className="container mx-auto px-6 py-16 max-w-4xl animate-in fade-in duration-700">
      <h1 className="text-4xl font-black mb-10">Resource <span className="text-brand">Center.</span></h1>
      <div className="space-y-4">
        <details className="group bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
          <summary className="p-6 font-bold text-lg cursor-pointer list-none flex justify-between items-center group-open:bg-gray-50">
            What is a real-time AI assessment? <span className="text-brand group-open:rotate-180 transition-transform">▼</span>
          </summary>
          <div className="p-6 text-gray-600 border-t border-gray-50 font-medium">It's a simulated process where we analyze your digital profile against lending criteria instantly.</div>
        </details>
      </div>
    </div>
  );
};

export default Resources;