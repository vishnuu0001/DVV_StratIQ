// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: OpportunityTracker — frontend/src/pages/wave (WaveUploadPanel.jsx)
// Date: 2026-05-12
// ---------------------------------------------------------------------------
import React, { useEffect, useRef, useState } from 'react';
import { UploadCloud, FileSpreadsheet, PlayCircle, CheckCircle2, AlertTriangle, X } from 'lucide-react';
import toast from 'react-hot-toast';
import {
  listWaveDatasets,
  uploadScopeDataset,
  uploadCategorizationDataset,
  deleteWaveDataset,
  previewWaveCategories,
  submitWaveAnalysis,
} from '../../services/api';

// Function: UploadSlot
function UploadSlot({ title, hint, dataset, uploading, clearing, onFile, onClear }) {
  const inputRef = useRef(null);
  return (
    <div className="ot-card p-5 flex flex-col gap-3">
      <div className="flex items-center gap-3">
        <div className="h-10 w-10 rounded-xl bg-cyan-600 flex items-center justify-center shrink-0">
          <FileSpreadsheet size={18} className="text-white" />
        </div>
        <div>
          <p className="text-sm font-semibold text-white">{title}</p>
          <p className="text-xs text-slate-400">{hint}</p>
        </div>
      </div>

      {dataset ? (
        <div className="flex items-center gap-2 text-xs text-emerald-400 bg-emerald-500/10 border border-emerald-500/25 rounded-lg px-3 py-2">
          <CheckCircle2 size={14} className="shrink-0" />
          <span className="truncate flex-1">{dataset.filename}</span>
          <span className="text-slate-400 shrink-0">· {dataset.row_count} rows</span>
          <button
            type="button"
            title="Clear this file"
            className="shrink-0 text-emerald-400 hover:text-red-400 transition-colors"
            disabled={clearing}
            onClick={onClear}
          >
            <X size={14} />
          </button>
        </div>
      ) : (
        <p className="text-xs text-slate-500">No file uploaded yet.</p>
      )}

      <input
        ref={inputRef}
        type="file"
        accept=".xlsx"
        className="hidden"
        onChange={(e) => {
          const file = e.target.files?.[0];
          if (file) onFile(file);
          e.target.value = '';
        }}
      />
      <button
        type="button"
        className="ot-btn-secondary text-xs px-3 py-2 justify-center"
        disabled={uploading}
        onClick={() => inputRef.current?.click()}
      >
        <UploadCloud size={14} />
        {uploading ? 'Uploading…' : dataset ? 'Replace file' : 'Upload .xlsx'}
      </button>
    </div>
  );
}

// Function: WaveUploadPanel
export default function WaveUploadPanel({ onJobStarted }) {
  const [scopeDataset, setScopeDataset] = useState(null);
  const [categorizationDataset, setCategorizationDataset] = useState(null);
  const [uploadingScope, setUploadingScope] = useState(false);
  const [uploadingCategorization, setUploadingCategorization] = useState(false);
  const [clearingScope, setClearingScope] = useState(false);
  const [clearingCategorization, setClearingCategorization] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const [previews, setPreviews] = useState(null);
  const [loadingPreviews, setLoadingPreviews] = useState(false);
  const [selected, setSelected] = useState(() => new Set());
  const [userGuidance, setUserGuidance] = useState('');
  const GUIDANCE_MAX = 2000;

  useEffect(() => {
    listWaveDatasets()
      .then(({ data }) => {
        const latestScope = data.find((d) => d.kind === 'scope');
        const latestCategorization = data.find((d) => d.kind === 'categorization');
        if (latestScope) setScopeDataset(latestScope);
        if (latestCategorization) setCategorizationDataset(latestCategorization);
      })
      .catch(() => {});
  }, []);

  useEffect(() => {
    if (!scopeDataset || !categorizationDataset) {
      setPreviews(null);
      return;
    }
    setLoadingPreviews(true);
    previewWaveCategories(scopeDataset.id, categorizationDataset.id)
      .then(({ data }) => {
        setPreviews(data);
        setSelected(new Set(data.map((c) => c.category))); // default: all selected
      })
      .catch(() => toast.error('Could not load categories from the uploaded files.'))
      .finally(() => setLoadingPreviews(false));
  }, [scopeDataset, categorizationDataset]);

  // Function: handleScopeFile
  const handleScopeFile = async (file) => {
    setUploadingScope(true);
    try {
      const { data } = await uploadScopeDataset(file);
      setScopeDataset(data);
      toast.success(`Application Scope List uploaded (${data.row_count} categories)`);
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Upload failed — check the file matches the expected template.');
    } finally {
      setUploadingScope(false);
    }
  };

  // Function: handleCategorizationFile
  const handleCategorizationFile = async (file) => {
    setUploadingCategorization(true);
    try {
      const { data } = await uploadCategorizationDataset(file);
      setCategorizationDataset(data);
      toast.success(`Business Categorization uploaded (${data.row_count} apps)`);
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Upload failed — check the file matches the expected template.');
    } finally {
      setUploadingCategorization(false);
    }
  };

  // Function: handleClearScope
  const handleClearScope = async () => {
    if (!scopeDataset) return;
    setClearingScope(true);
    try {
      await deleteWaveDataset(scopeDataset.id);
      setScopeDataset(null);
      toast.success('Application Scope file cleared.');
    } catch {
      toast.error('Could not clear the file.');
    } finally {
      setClearingScope(false);
    }
  };

  // Function: handleClearCategorization
  const handleClearCategorization = async () => {
    if (!categorizationDataset) return;
    setClearingCategorization(true);
    try {
      await deleteWaveDataset(categorizationDataset.id);
      setCategorizationDataset(null);
      toast.success('Business Categorization file cleared.');
    } catch {
      toast.error('Could not clear the file.');
    } finally {
      setClearingCategorization(false);
    }
  };

  // Function: toggleCategory
  const toggleCategory = (category) => {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(category)) next.delete(category); else next.add(category);
      return next;
    });
  };

  const allSelected = previews && selected.size === previews.length && previews.length > 0;
  // Function: toggleSelectAll
  const toggleSelectAll = () => {
    if (!previews) return;
    setSelected(allSelected ? new Set() : new Set(previews.map((c) => c.category)));
  };

  // Function: runAnalysis
  const runAnalysis = async () => {
    if (!scopeDataset || !categorizationDataset || selected.size === 0) return;
    setSubmitting(true);
    try {
      const { data } = await submitWaveAnalysis(scopeDataset.id, categorizationDataset.id, Array.from(selected), userGuidance);
      if (data.unmatched_categories?.length) {
        toast(`${data.unmatched_categories.length} selected categorization value(s) had no matching Solution Approach — they'll be skipped.`, { icon: '⚠️' });
      }
      toast.success(`Analysis started for ${data.total_categories} categories`);
      onJobStarted(data.job_id);
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Could not start analysis.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-5">
      <div className="grid sm:grid-cols-2 gap-4">
        <UploadSlot
          title="Application Scope"
          hint="Template: Application Scope List.xlsx (Solution Approach categories)"
          dataset={scopeDataset}
          uploading={uploadingScope}
          clearing={clearingScope}
          onFile={handleScopeFile}
          onClear={handleClearScope}
        />
        <UploadSlot
          title="Business Categorization"
          hint="Template: BusinessApplication_Categorized.xlsx (per-app inventory)"
          dataset={categorizationDataset}
          uploading={uploadingCategorization}
          clearing={clearingCategorization}
          onFile={handleCategorizationFile}
          onClear={handleClearCategorization}
        />
      </div>

      {loadingPreviews && <p className="text-sm text-slate-500">Reading categories from the uploaded files…</p>}

      {previews && previews.length > 0 && (
        <div className="ot-card p-5 space-y-3">
          <div className="flex items-center justify-between">
            <p className="text-sm font-semibold text-white">
              Select categories to analyze ({selected.size}/{previews.length})
            </p>
            <button type="button" className="ot-btn-secondary text-xs px-3 py-1.5" onClick={toggleSelectAll}>
              {allSelected ? 'Deselect all' : 'Select all'}
            </button>
          </div>

          <div className="grid sm:grid-cols-2 gap-1.5 max-h-80 overflow-y-auto pr-1">
            {previews.map((c) => (
              <label
                key={c.category}
                className="flex items-start gap-2.5 px-3 py-2 rounded-lg bg-slate-900/60 cursor-pointer hover:bg-slate-900"
              >
                <input
                  type="checkbox"
                  className="mt-0.5"
                  checked={selected.has(c.category)}
                  onChange={() => toggleCategory(c.category)}
                />
                <span className="min-w-0">
                  <span className="block text-xs text-slate-200 truncate" title={c.category}>{c.category}</span>
                  <span className="block text-[11px] text-slate-500">
                    {c.app_count} apps
                    {!c.matched_in_scope && (
                      <span className="inline-flex items-center gap-1 text-amber-400 ml-1">
                        <AlertTriangle size={10} /> no scope match
                      </span>
                    )}
                  </span>
                </span>
              </label>
            ))}
          </div>
        </div>
      )}

      {previews && previews.length > 0 && (
        <div className="ot-card p-5 space-y-2">
          <div className="flex items-center justify-between">
            <label htmlFor="wave-user-guidance" className="text-sm font-semibold text-white">
              Guidance for this analysis (optional)
            </label>
            <span className="text-[11px] text-slate-500">{userGuidance.length}/{GUIDANCE_MAX}</span>
          </div>
          <textarea
            id="wave-user-guidance"
            className="ot-input w-full text-xs resize-y min-h-[70px]"
            placeholder="e.g. 'Treat Wave 0 apps as higher priority for change management' or 'Flag anything touching SAP for closer review.' Advisory only — this can steer judgment calls but can never override the Modernization gate or change already-finalized wave assignments."
            maxLength={GUIDANCE_MAX}
            value={userGuidance}
            onChange={(e) => setUserGuidance(e.target.value)}
          />
        </div>
      )}

      <button
        type="button"
        className="ot-btn-primary text-sm px-4 py-2.5"
        disabled={!scopeDataset || !categorizationDataset || selected.size === 0 || submitting}
        onClick={runAnalysis}
      >
        <PlayCircle size={16} />
        {submitting ? 'Starting…' : `Run Wave Planning Analysis (${selected.size} selected)`}
      </button>
    </div>
  );
}
