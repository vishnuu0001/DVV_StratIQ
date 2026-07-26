// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: AI_Vehicle_Loan — frontend/src/components (ChatWidget.js)
// Date: 2026-04-25
// ---------------------------------------------------------------------------
import React, { useState } from 'react';
import { Bot, X, AlertCircle, Landmark, Loader2, Home, FileText, CheckCircle2, PenLine } from 'lucide-react';
import { useAuth } from '../AuthContext';

// Function: ChatWidget
const ChatWidget = ({ isOpen, setIsOpen, analysis }) => {
  const { resetSelection } = useAuth();
  const [step, setStep] = useState('selection'); // selection, signing, final
  const [selectedBank, setSelectedBank] = useState(null);

  if (!isOpen) return null;
  const isDeclined = analysis?.result?.status === "Declined";

  return (
    <div className="fixed bottom-6 right-6 w-[380px] h-[580px] bg-white rounded-[32px] shadow-2xl border border-gray-100 flex flex-col z-[100] animate-in slide-in-from-bottom-10 overflow-hidden">
      <div className="bg-brand p-5 flex justify-between items-center text-white">
        <div className="flex items-center gap-3"><Bot size={22} /><h3 className="font-extrabold text-sm uppercase">AI Decision Hub</h3></div>
        <button onClick={() => setIsOpen(false)} className="text-white"><X size={18} /></button>
      </div>

      <div className="flex-1 p-6 bg-gray-50/50 overflow-y-auto">
        {analysis?.status === 'analyzing' ? (
          <div className="flex flex-col items-center justify-center h-full gap-4">
            <Loader2 className="animate-spin text-brand" /><p className="text-xs font-black text-gray-400 uppercase">Analyzing Profile...</p>
          </div>
        ) : isDeclined ? (
          /* --- REJECTION --- */
          <div className="flex flex-col items-center justify-center h-full text-center space-y-6">
            <div className="w-16 h-16 bg-red-50 text-red-500 rounded-2xl flex items-center justify-center"><AlertCircle size={32} /></div>
            <p className="text-sm text-gray-500 font-medium">Sorry, your score of {analysis?.result?.credit_score} is below our threshold.</p>
            <button onClick={() => {setIsOpen(false); resetSelection();}} className="w-full py-4 bg-gray-900 text-white font-black rounded-2xl flex items-center justify-center gap-2"><Home size={18} /> Try Good Credit</button>
          </div>
        ) : step === 'selection' ? (
          /* --- COMPARISON --- */
          <div className="space-y-4">
             <p className="text-[10px] font-black text-gray-400 uppercase text-center">3 Prime Matches Found</p>
             {analysis.result?.lenders.map((bank, i) => (
               <div key={i} onClick={() => setSelectedBank(bank)} className={`p-4 rounded-2xl border-2 cursor-pointer ${selectedBank?.name === bank.name ? 'border-brand bg-brand/5' : 'bg-white border-transparent'}`}>
                 <div className="flex justify-between items-center">
                   <div><p className="text-sm font-black text-gray-900">{bank.name}</p><p className="text-xs font-bold text-brand">{bank.match} Match</p></div>
                   <div className="text-right"><p className="text-lg font-black">{bank.apr}</p><p className="text-[10px] font-bold text-gray-400 uppercase">APR</p></div>
                 </div>
               </div>
             ))}
             <button disabled={!selectedBank} onClick={() => setStep('signing')} className="w-full py-5 bg-gray-900 text-white font-black rounded-2xl disabled:opacity-20 mt-4">Continue with {selectedBank?.name || 'Lender'}</button>
          </div>
        ) : step === 'signing' ? (
          /* --- SIGNATURE STEP --- */
          <div className="flex flex-col h-full space-y-6 text-center">
            <PenLine className="mx-auto text-brand" size={48} />
            <h4 className="font-black text-lg">Digital Signature</h4>
            <div className="flex-1 bg-white border-2 border-dashed border-gray-200 rounded-2xl flex items-center justify-center text-gray-300 italic text-xs">Sign here with mouse</div>
            <button onClick={() => setStep('final')} className="w-full py-4 bg-brand text-white font-black rounded-2xl">Confirm Signature</button>
          </div>
        ) : (
          /* --- FINAL APPROVAL --- */
          <div className="flex flex-col items-center justify-center h-full text-center space-y-6">
            <CheckCircle2 size={64} className="text-brand" />
            <h4 className="text-2xl font-black text-gray-900">APPROVED</h4>
            <div className="bg-white p-4 rounded-2xl border border-gray-100 w-full flex items-center gap-4">
              <FileText className="text-brand" /><div className="text-left"><p className="text-xs font-black text-gray-900 italic underline">view_contract.pdf</p></div>
            </div>
            <button onClick={() => {setIsOpen(false); resetSelection();}} className="w-full py-4 bg-gray-900 text-white font-black rounded-2xl">Finish Simulation</button>
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatWidget;