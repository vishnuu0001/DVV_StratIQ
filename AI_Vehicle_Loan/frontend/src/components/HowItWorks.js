// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: AI_Vehicle_Loan — frontend/src/components (HowItWorks.js)
// Date: 2026-06-08
// ---------------------------------------------------------------------------
import React from 'react';
import { MousePointer2, Cpu, CheckCircle } from 'lucide-react';

// Function: HowItWorks
const HowItWorks = () => {
  return (
    <div className="container mx-auto px-6 py-16 animate-in slide-in-from-bottom-5 duration-700">
      <h1 className="text-5xl font-black mb-16 text-center">How <span className="text-brand">It Works.</span></h1>
      <div className="grid md:grid-cols-3 gap-12">
        <div className="text-center">
          <div className="w-20 h-20 bg-brand/10 text-brand rounded-3xl flex items-center justify-center mx-auto mb-6"><MousePointer2 size={32}/></div>
          <h3 className="text-xl font-bold mb-3">1. Select Vehicle</h3>
          <p className="text-gray-500 font-medium text-sm">Browse our live inventory and click the green arrow for any car.</p>
        </div>
        <div className="text-center">
          <div className="w-20 h-20 bg-brand/10 text-brand rounded-3xl flex items-center justify-center mx-auto mb-6"><Cpu size={32}/></div>
          <h3 className="text-xl font-bold mb-3">2. AI Assessment</h3>
          <p className="text-gray-500 font-medium text-sm">Our agent simulates a credit check and matches your intent via Vector Search.</p>
        </div>
        <div className="text-center">
          <div className="w-20 h-20 bg-brand/10 text-brand rounded-3xl flex items-center justify-center mx-auto mb-6"><CheckCircle size={32}/></div>
          <h3 className="text-xl font-bold mb-3">3. Instant Decision</h3>
          <p className="text-gray-500 font-medium text-sm">View your pre-approval status and APR in the bottom-right chat window.</p>
        </div>
      </div>
    </div>
  );
};

export default HowItWorks;