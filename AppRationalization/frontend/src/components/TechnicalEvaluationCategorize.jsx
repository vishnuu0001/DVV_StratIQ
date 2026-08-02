// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: AppRationalization - frontend/src/components (TechnicalEvaluationCategorize.jsx)
// Date: 2026-08-02
// ---------------------------------------------------------------------------
import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { toast } from 'react-toastify';
import {
  clearTechnicalAssessmentData,
  enrichTechnicalEvaluationCategorizeTopic,
  getTechnicalEvaluationCategorizeDashboard,
  uploadTechnicalEvaluationCategorize,
} from '../services/api';

// Function: normalizeMatrixDisplayValue
const normalizeMatrixDisplayValue = (header, value) => {
  const text = String(value ?? '').trim();
  if (!text) return 'Unknown';
  const lower = text.toLowerCase();
  const isProductType = ['product type', 'cots', 'custom'].some((token) =>
    String(header || '').toLowerCase().includes(token)
  );

  if (isProductType) {
    if (lower.includes('hybrid')) return 'Hybrid';
    if (lower.includes('cots') || lower.includes('available in market')) return 'COTS';
    if (lower.includes('custom')) return 'Custom';
    return 'Unknown';
  }

  if (['yes', 'y', 'x', 'true', 'supported', 'available'].includes(lower)) return 'Yes';
  if (['no', 'n', 'false', 'unsupported', 'unavailable'].includes(lower)) return 'No';
  if (lower.includes('partial') || lower.includes('limited')) return 'Partial';
  if (lower.includes('unknown') || lower === 'n/a') return 'Unknown';

  return text;
};

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

  // Function: loadDashboard
  const loadDashboard = useCallback(async (query = '', topic = selectedTopic) => {
    try {
      const response = await getTechnicalEvaluationCategorizeDashboard(topic, query || '');
      const data = response.data || {};
      setDashboard(data);
    } catch (error) {
      toast.error(error.response?.data?.error || 'Unable to load Categorize dashboard');
    }
  }, [selectedTopic]);

  useEffect(() => {
    loadDashboard();
  }, [loadDashboard]);

  useEffect(() => {
    const topics = dashboard.topics || [];
    if (topics.length && !topics.includes(selectedTopic)) {
      setSelectedTopic(topics[0]);
    }
  }, [dashboard.topics, selectedTopic]);

  // Function: runImport
  const runImport = async () => {
    if (!file) return;
    setBusy(true);
    try {
      const response = await uploadTechnicalEvaluationCategorize(file);
      toast.success(`${response.data.import.row_count} rows imported`);
      const initial = await getTechnicalEvaluationCategorizeDashboard();
      const initialData = initial.data || { items: [], topics: [] };
      const availableTopics = initialData.topics || [];
      const topicToEnrich = availableTopics.includes(selectedTopic)
        ? selectedTopic
        : availableTopics[0];
      setDashboard(initialData);
      if (topicToEnrich) setSelectedTopic(topicToEnrich);
      setFile(null);
      if (topicToEnrich && initialData.market_search?.configured) {
        await runEnrichment(topicToEnrich, true);
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
      setDashboard({
        items: [], topics: [], total: 0, import: null, highlighted_headers: [],
        capability_headers: [], product_type_headers: [], headers: [],
      });
    } catch (error) {
      toast.error(error.response?.data?.error || 'Clear failed');
    } finally {
      setBusy(false);
    }
  };

  const capabilityHeaders = useMemo(() => dashboard.capability_headers || [], [dashboard.capability_headers]);
  const productTypeHeaders = useMemo(() => dashboard.product_type_headers || [], [dashboard.product_type_headers]);
  const highlightedHeaders = useMemo(
    () => [...capabilityHeaders, ...productTypeHeaders],
    [capabilityHeaders, productTypeHeaders]
  );
  const items = useMemo(() => dashboard.items || [], [dashboard.items]);

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
          Upload Business_applications_Categorized.xlsx, select a topic, then let global market retrieval and Ollama
          discover the comparison capabilities and validate every product.
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
            disabled={busy || enriching || !selectedTopic || !dashboard.market_search?.configured}
            onClick={() => runEnrichment(selectedTopic)}
            className="portal-btn-primary px-4 py-2 rounded-lg disabled:opacity-40"
          >
            {enriching ? 'Searching and Validating Products...' : 'Discover & Validate Capability Matrix'}
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
            onChange={(event) => {
              setSelectedTopic(event.target.value);
              setSearch('');
            }}
            className="rounded-lg bg-slate-950 border border-slate-700 px-3 py-2 text-sm text-cyan-300 min-w-[320px]"
          >
            {((dashboard.topics || []).length ? dashboard.topics : [selectedTopic]).map((topic) => (
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
            onClick={() => loadDashboard(search)}
            className="portal-btn-secondary px-4 py-2 rounded-lg"
            disabled={busy || enriching}
          >
            Search
          </button>
        </div>
      </div>

      <div className="rounded-xl border border-slate-700 bg-slate-900/70 overflow-hidden">
        {items.length > 0 && highlightedHeaders.length === 0 && (
          <div className="border-b border-amber-700/50 bg-amber-950/40 px-4 py-3 text-sm text-amber-200">
            No validated capability matrix exists for this topic yet. Run "Discover &amp; Validate Capability Matrix".
          </div>
        )}
        {dashboard.import && !dashboard.market_search?.configured && (
          <p className="text-xs text-amber-300 mt-3">
            Global market search is not configured. Set MARKET_SEARCH_URL to an approved search provider before
            product names can be researched and validated.
          </p>
        )}
        <div className="overflow-auto max-h-[62vh]">
          <table className="w-max min-w-full text-xs">
            <thead className="sticky top-0 bg-slate-800 text-slate-200">
              <tr>
                <th rowSpan={2} className="text-left px-3 py-3 whitespace-nowrap align-middle">Topic</th>
                <th rowSpan={2} className="text-left px-3 py-3 whitespace-nowrap align-middle">Product</th>
                <th rowSpan={2} className="text-left px-3 py-3 whitespace-nowrap align-middle">Size</th>
                {capabilityHeaders.length > 0 && (
                  <th colSpan={capabilityHeaders.length} className="text-center px-3 py-2 bg-cyan-600 text-white">
                    Capabilities
                  </th>
                )}
                {productTypeHeaders.length > 0 && (
                  <th colSpan={productTypeHeaders.length} className="text-center px-3 py-2 bg-cyan-600 text-white">
                    Product Type
                  </th>
                )}
              </tr>
              <tr>
                {highlightedHeaders.map((header) => (
                  <th key={header} className="text-left px-3 py-3 whitespace-nowrap bg-yellow-300 text-slate-900">
                    {header}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {items.map((item, index) => {
                const showTopic = index === 0 || items[index - 1]?.topic !== item.topic;
                return (
                <tr key={item.id} className="border-t border-slate-800 hover:bg-slate-800/50">
                  <td className="px-3 py-3 min-w-[220px] text-white">{showTopic ? (item.topic || '-') : ''}</td>
                  <td className="px-3 py-3 min-w-[260px] text-cyan-200">{item.product || '-'}</td>
                  <td className="px-3 py-3 min-w-[140px] text-slate-300">{item.size || '-'}</td>
                  {highlightedHeaders.map((header) => {
                    const enrichedValue = item.enrichment_payload?.[header];
                    const value = normalizeMatrixDisplayValue(header, enrichedValue);
                    const isProductType = productTypeHeaders.includes(header);
                    const displayValue = isProductType
                      ? value
                      : value === 'Yes' ? 'X' : value === 'No' ? '' : value === 'Partial' ? '~' : '?';
                    return (
                      <td key={`${item.id}-${header}`} className="px-3 py-3 min-w-[180px] text-center whitespace-normal break-words bg-yellow-100 text-slate-900">
                        {displayValue}
                      </td>
                    );
                  })}
                </tr>
                );
              })}
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
