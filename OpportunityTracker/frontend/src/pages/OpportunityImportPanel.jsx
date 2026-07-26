// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: OpportunityTracker — frontend/src/pages (OpportunityImportPanel.jsx)
// Date: 2026-07-15
// ---------------------------------------------------------------------------
import React, { useRef, useState } from 'react';
import { UploadCloud, FileSpreadsheet, CheckCircle2, AlertTriangle } from 'lucide-react';
import toast from 'react-hot-toast';
import { importOpportunities } from '../services/api';

// Function: OpportunityImportPanel
export default function OpportunityImportPanel({ onImported }) {
  const inputRef = useRef(null);
  const [uploading, setUploading] = useState(false);
  const [lastResult, setLastResult] = useState(null);

  // Function: handleFile
  const handleFile = async (file) => {
    setUploading(true);
    setLastResult(null);
    try {
      const { data } = await importOpportunities(file);
      setLastResult(data);
      toast.success(`Imported: ${data.created} created, ${data.updated} updated`);
      onImported?.();
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Import failed — check the file matches the FY 27 Plan Tracker template.');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="max-w-2xl space-y-5">
      <div className="ot-card p-5 flex flex-col gap-3">
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-xl bg-cyan-600 flex items-center justify-center shrink-0">
            <FileSpreadsheet size={18} className="text-white" />
          </div>
          <div>
            <p className="text-sm font-semibold text-white">FY 27 Plan Tracker Workbook</p>
            <p className="text-xs text-slate-400">
              Upload MFG CTO_Oppty Tracker.xlsx — only the &quot;FY 27 Plan Tracker&quot; sheet is imported.
              Existing opportunities are matched by CRM Ref # (if real) or Opportunity Name + Customer
              Group, and updated in place — safe to re-upload after the source workbook changes.
            </p>
          </div>
        </div>

        <input
          ref={inputRef}
          type="file"
          accept=".xlsx"
          className="hidden"
          onChange={(e) => {
            const file = e.target.files?.[0];
            if (file) handleFile(file);
            e.target.value = '';
          }}
        />
        <button
          type="button"
          className="ot-btn-primary text-sm px-4 py-2.5 justify-center"
          disabled={uploading}
          onClick={() => inputRef.current?.click()}
        >
          <UploadCloud size={16} />
          {uploading ? 'Importing…' : 'Upload .xlsx'}
        </button>
      </div>

      {lastResult && (
        <div className="ot-card p-5 space-y-2">
          <div className="flex items-center gap-2 text-sm text-emerald-400">
            <CheckCircle2 size={16} />
            <span>{lastResult.created} created, {lastResult.updated} updated</span>
          </div>
          {lastResult.warnings?.length > 0 && (
            <div className="space-y-1">
              {lastResult.warnings.map((w, i) => (
                <div key={i} className="flex items-start gap-2 text-xs text-amber-400 bg-amber-500/10 border border-amber-500/25 rounded-lg px-3 py-2">
                  <AlertTriangle size={13} className="shrink-0 mt-0.5" />
                  <span>{w}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
