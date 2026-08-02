// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: AppRationalization - frontend/src/components (TechnicalEvaluationCategorize.jsx)
// Date: 2026-08-02
// ---------------------------------------------------------------------------
import React, { useEffect, useMemo, useState } from 'react';
import { toast } from 'react-toastify';
import {
  clearTechnicalAssessmentData,
  enrichTechnicalEvaluationCategorizeTopic,
  getTechnicalEvaluationCategorizeDashboard,
  uploadTechnicalEvaluationCategorize,
} from '../services/api';

const TARGET_TOPIC = 'Harmonize Alarm Management Solutions';

// Function: TechnicalEvaluationCategorize
const TechnicalEvaluationCategorize = () => {
  const [file, setFile] = useState(null);
  const [busy, setBusy] = useState(false);
  const [enriching, setEnriching] = useState(false);
  const [search, setSearch] = useState('');
  const [selectedTopic, setSelectedTopic] = useState('');
  const [dashboard, setDashboard] = useState({
    items: [],
    topics: [],
    total: 0,
    import: null,
    highlighted_headers: [],
    headers: [],
  });

  // Function: chooseDefaultTopic
  const chooseDefaultTopic = (topics) => {
    if (!topics?.length) return '';
    const preferred = topics.find((topic) => topic === TARGET_TOPIC);
    return preferred || topics[0] || '';
  };

  // Function: loadDashboard
  const loadDashboard = async (topic, query = search) => {
    try {
      const response = await getTechnicalEvaluationCategorizeDashboard(topic || '', query || '');
      const data = response.data || {};
      setDashboard(data);
      if (!selectedTopic && data.topics?.length) {
        setSelectedTopic(chooseDefaultTopic(data.topics));
      }
    } catch (error) {
      toast.error(error.response?.data?.error || 'Unable to load Categorize dashboard');
    }
  };

  useEffect(() => {
    loadDashboard(selectedTopic, search); // eslint-disable-line react-hooks/exhaustive-deps
  }, [selectedTopic]);

  // Function: runImport
  const runImport = async () => {
    if (!file) return;
    setBusy(true);
    try {
      const response = await uploadTechnicalEvaluationCategorize(file);
      toast.success(`${response.data.import.row_count} rows imported`);
      const initial = await getTechnicalEvaluationCategorizeDashboard();
      const topics = initial.data?.topics || [];
      const topic = chooseDefaultTopic(topics);
      setDashboard(initial.data || { items: [], topics: [] });
      setSelectedTopic(topic);
      setFile(null);
      if (topic) {
        await runEnrichment(topic, true);
      }
    } catch (error) {
      toast.error(error.response?.data?.error || 'Import failed');
    } finally {
      setBusy(false);
    }
  };

  // Function: runEnrichment
  const runEnrichment = async (topic, silent = false) => {
    if (!topic) return;
    setEnriching(true);
    try {
      const response = await enrichTechnicalEvaluationCategorizeTopic(topic);
      setDashboard(response.data || dashboard);
      if (!silent) {
        toast.success('Market enrichment completed using Ollama');
      }
    } catch (error) {
      toast.error(error.response?.data?.error || 'Ollama enrichment failed');
    } finally {
      setEnriching(false);
    }
  };

  // Function: runClear
  const runClear = async () => {
    if (!window.confirm('Clear all Categorize data? This cannot be undone.')) return;
    setBusy(true);
    try {
      const response = await clearTechnicalAssessmentData('technical-evaluation-categorize');
      toast.success(`Cleared ${response.data.cleared_rows} row(s)`);
      setDashboard({ items: [], topics: [], total: 0, import: null, highlighted_headers: [], headers: [] });
      setSelectedTopic('');
    } catch (error) {
      toast.error(error.response?.data?.error || 'Clear failed');
    } finally {
      setBusy(false);
    }
  };

  const highlightedHeaders = dashboard.highlighted_headers || [];
  const items = dashboard.items || [];

  const totals = useMemo(() => {
    const products = new Set(items.map((item) => item.product).filter(Boolean));
    return {
      productCount: products.size,
      topicCount: (dashboard.topics || []).length,
      rowCount: items.length,
    };
  }, [items, dashboard.topics]);

  return (
    <div className="p-6 text-slate-100">
      <div className="mb-5">
        <p className="text-xs uppercase tracking-[0.2em] text-cyan-400">Technical Evaluation</p>
        <h1 className="text-2xl font-bold mt-1">Categorize</h1>
        <p className="text-sm text-slate-400 mt-1">
          Upload Business_applications_Categorized.xlsx, choose a categorization topic, and populate highlighted
          market columns using Ollama.
        </p>
      </div>

      <div className="rounded-xl border border-slate-700 bg-slate-900/70 p-5 mb-5">
        <p className="text-xs text-slate-400 mb-3">
          Expected workbook file: <span className="text-cyan-300">Business_applications_Categorized.xlsx</span>
        </p>
        <div className="flex flex-wrap items-center gap-3">
          <input
            type="file"
            accept=".xlsx"
            onChange={(event) => setFile(event.target.files?.[0] || null)}
            className="text-sm text-slate-300 file:mr-3 file:rounded-lg file:border-0 file:bg-slate-700 file:px-3 file:py-2 file:text-white"
          />
          <button
            disabled={!file || busy || enriching}
            onClick={runImport}
            className="portal-btn-primary px-4 py-2 rounded-lg disabled:opacity-40"
          >
            Upload Categorize Data
          </button>
          <button
            disabled={busy || enriching || !selectedTopic}
            onClick={() => runEnrichment(selectedTopic)}
            className="portal-btn-primary px-4 py-2 rounded-lg disabled:opacity-40"
          >
            {enriching ? 'Searching Global Market...' : 'Populate Highlighted Columns (Ollama)'}
          </button>
          <button
            disabled={busy || enriching || !dashboard.import}
            onClick={runClear}
            className="portal-btn-secondary px-4 py-2 rounded-lg disabled:opacity-40"
          >
            Clear Data
          </button>
        </div>

        {dashboard.import && (
          <p className="text-xs text-slate-500 mt-3">
            Latest import: {dashboard.import.source_filename} - {dashboard.import.row_count} rows -{' '}
            {new Date(dashboard.import.imported_at).toLocaleString()}
          </p>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-5">
        <div className="rounded-lg border border-slate-700 bg-slate-900/70 p-3">
          <p className="text-xs text-slate-400">Selected Topic Products</p>
          <p className="text-lg font-semibold text-white mt-1">{totals.productCount}</p>
        </div>
        <div className="rounded-lg border border-slate-700 bg-slate-900/70 p-3">
          <p className="text-xs text-slate-400">Available Topics</p>
          <p className="text-lg font-semibold text-white mt-1">{totals.topicCount}</p>
        </div>
        <div className="rounded-lg border border-slate-700 bg-slate-900/70 p-3">
          <p className="text-xs text-slate-400">Rows In View</p>
          <p className="text-lg font-semibold text-white mt-1">{totals.rowCount}</p>
        </div>
      </div>

      <div className="rounded-xl border border-slate-700 bg-slate-900/70 p-4 mb-4">
        <div className="flex flex-wrap items-center gap-3">
          <select
            value={selectedTopic}
            onChange={(event) => setSelectedTopic(event.target.value)}
            className="rounded-lg bg-slate-950 border border-slate-700 px-3 py-2 text-sm"
          >
            {!dashboard.topics?.length && <option value="">No topics available</option>}
            {dashboard.topics?.map((topic) => (
              <option key={topic} value={topic}>{topic}</option>
            ))}
          </select>
          <input
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Search product"
            className="w-80 max-w-full rounded-lg bg-slate-950 border border-slate-700 px-3 py-2 text-sm"
          />
          <button
            onClick={() => loadDashboard(selectedTopic, search)}
            className="portal-btn-secondary px-4 py-2 rounded-lg"
            disabled={busy || enriching}
          >
            Search
          </button>
        </div>
      </div>

      <div className="rounded-xl border border-slate-700 bg-slate-900/70 overflow-hidden">
        <div className="overflow-auto max-h-[62vh]">
          <table className="w-max min-w-full text-xs">
            <thead className="sticky top-0 bg-slate-800 text-slate-200">
              <tr>
                <th className="text-left px-3 py-3 whitespace-nowrap">Topic</th>
                <th className="text-left px-3 py-3 whitespace-nowrap">Product</th>
                <th className="text-left px-3 py-3 whitespace-nowrap">Size</th>
                {highlightedHeaders.map((header) => (
                  <th key={header} className="text-left px-3 py-3 whitespace-nowrap bg-yellow-300 text-slate-900">
                    {header}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {items.map((item) => (
                <tr key={item.id} className="border-t border-slate-800 hover:bg-slate-800/50">
                  <td className="px-3 py-3 min-w-[220px] text-white">{item.topic || '-'}</td>
                  <td className="px-3 py-3 min-w-[260px] text-cyan-200">{item.product || '-'}</td>
                  <td className="px-3 py-3 min-w-[140px] text-slate-300">{item.size || '-'}</td>
                  {highlightedHeaders.map((header) => {
                    const value =
                      item.enrichment_payload?.[header] ??
                      item.row_payload?.[header] ??
                      'Unknown';
                    return (
                      <td key={`${item.id}-${header}`} className="px-3 py-3 min-w-[240px] whitespace-normal break-words bg-yellow-100 text-slate-900">
                        {value || 'Unknown'}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
          {!items.length && (
            <div className="p-10 text-center text-slate-500">No categorized rows available. Upload the workbook to begin.</div>
          )}
        </div>
      </div>
    </div>
  );
};

export default TechnicalEvaluationCategorize;
