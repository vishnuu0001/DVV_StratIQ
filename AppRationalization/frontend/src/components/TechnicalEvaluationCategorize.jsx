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
  updateTechnicalEvaluationValidation,
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
const TechnicalEvaluationCategorize = ({ mode = 'categorize' }) => {
  const isValidate = mode === 'validate';
  const [file, setFile] = useState(null);
  const [busy, setBusy] = useState(false);
  const [enriching, setEnriching] = useState(false);
  const [savingCell, setSavingCell] = useState('');
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
      const enrichedDashboard = response.data || dashboard;
      setDashboard(enrichedDashboard);
      if (!silent) {
        const run = enrichedDashboard.enrichment_run;
        toast.success(
          run
            ? `${run.rows_updated} products enriched across ${run.capabilities.length} capabilities`
            : 'Market enrichment completed using Ollama'
        );
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

  // Function: updateValidation
  const updateValidation = async (item, updates, cellKey) => {
    setSavingCell(cellKey);
    try {
      const response = await updateTechnicalEvaluationValidation(item.id, updates);
      const updatedItem = response.data?.item;
      if (updatedItem) {
        setDashboard((current) => ({
          ...current,
          items: (current.items || []).map((row) => row.id === updatedItem.id ? updatedItem : row),
        }));
      }
    } catch (error) {
      toast.error(error.response?.data?.error || 'Unable to save validation change');
    } finally {
      setSavingCell('');
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
    <div className="technical-evaluation-page">
      <div className="te-page-header">
        <p className="text-xs uppercase tracking-[0.2em] text-cyan-400">Technical Evaluation</p>
        <h1 className="text-2xl font-bold mt-1">{isValidate ? 'Validate' : 'Categorize'}</h1>
        <p className="text-sm text-slate-400 mt-1">
          {isValidate
            ? 'Review the discovered capability matrix and validate Size, Capabilities, and Product Type. Changes save directly to the current matrix.'
            : 'Upload Business_applications_Categorized.xlsx, select a topic, then let global market retrieval and Ollama discover the comparison capabilities and validate every product.'}
        </p>
      </div>

      {!isValidate && <div className="te-panel te-upload-panel">
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
            className="az-btn az-btn-primary"
          >
            Upload Categorize Data
          </button>
          <button
            disabled={busy || enriching || !selectedTopic || !dashboard.market_search?.configured}
            onClick={() => runEnrichment(selectedTopic)}
            className="az-btn az-btn-primary"
          >
            {enriching ? 'Searching and Validating Products...' : 'Discover & Validate Capability Matrix'}
          </button>
          <button
            disabled={busy || enriching || !dashboard.import}
            onClick={runClear}
            className="az-btn az-btn-secondary"
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
      </div>}

      {isValidate && (
        <div className="te-validation-banner">
          <strong>Editable validation dashboard</strong>
          <span>Select a value in any Size, Capability, or Product Type cell. Each change is saved immediately.</span>
        </div>
      )}

      {dashboard.enrichment_run && (
        <div className="te-enrichment-summary" role="status">
          <div>
            <strong>Capability matrix refreshed</strong>
            <span>
              {dashboard.enrichment_run.rows_updated} products validated using{' '}
              {dashboard.enrichment_run.evidence_count} market evidence result(s).
            </span>
          </div>
          <div className="te-summary-tags">
            {(dashboard.enrichment_run.capabilities || []).map((capability) => (
              <span key={capability} className="az-tag">{capability}</span>
            ))}
          </div>
          {(dashboard.enrichment_run.added_headers?.length > 0 || dashboard.enrichment_run.removed_headers?.length > 0) && (
            <p className="te-change-note">
              {dashboard.enrichment_run.added_headers?.length > 0
                ? `Added: ${dashboard.enrichment_run.added_headers.join(', ')}. `
                : ''}
              {dashboard.enrichment_run.removed_headers?.length > 0
                ? `Removed: ${dashboard.enrichment_run.removed_headers.join(', ')}.`
                : ''}
            </p>
          )}
        </div>
      )}

      <div className="te-stat-grid">
        <div className="az-stat-card">
          <p className="text-xs text-slate-400">Selected Topic Products</p>
          <p className="text-lg font-semibold text-white mt-1">{totals.productCount}</p>
        </div>
        <div className="az-stat-card">
          <p className="text-xs text-slate-400">Available Topics</p>
          <p className="text-lg font-semibold text-white mt-1">{totals.topicCount}</p>
        </div>
        <div className="az-stat-card">
          <p className="text-xs text-slate-400">Rows In View</p>
          <p className="text-lg font-semibold text-white mt-1">{totals.rowCount}</p>
        </div>
      </div>

      <div className="te-panel te-filter-panel">
        <div className="flex flex-wrap items-center gap-3">
          <select
            value={selectedTopic}
            onChange={(event) => {
              setSelectedTopic(event.target.value);
              setSearch('');
            }}
            className="az-field te-topic-select"
          >
            {((dashboard.topics || []).length ? dashboard.topics : [selectedTopic]).map((topic) => (
              <option key={topic} value={topic}>{topic}</option>
            ))}
          </select>
          <input
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Search product"
            className="az-field te-search-field"
          />
          <button
            onClick={() => loadDashboard(search)}
            className="az-btn az-btn-secondary"
            disabled={busy || enriching}
          >
            Search
          </button>
        </div>
      </div>

      <div className="te-table-panel">
        {items.length > 0 && highlightedHeaders.length === 0 && (
          <div className="border-b border-amber-700/50 bg-amber-950/40 px-4 py-3 text-sm text-amber-200">
            No discovered capability matrix exists for this topic yet. Run "Discover &amp; Validate Capability Matrix" in Categorize first.
          </div>
        )}
        {dashboard.import && !dashboard.market_search?.configured && (
          <p className="text-xs text-amber-300 mt-3">
            Global market search is not configured. Set MARKET_SEARCH_URL to an approved search provider before
            product names can be researched and validated.
          </p>
        )}
        <div className="overflow-auto max-h-[62vh]">
          <table className="te-matrix-table">
            <thead>
              <tr>
                <th rowSpan={2} className="text-left px-3 py-3 whitespace-nowrap align-middle">Topic</th>
                <th rowSpan={2} className="text-left px-3 py-3 whitespace-nowrap align-middle">Product</th>
                <th rowSpan={2} className="text-left px-3 py-3 whitespace-nowrap align-middle">Size</th>
                {capabilityHeaders.length > 0 && (
                  <th colSpan={capabilityHeaders.length} className="te-matrix-group-heading">
                    Capabilities
                  </th>
                )}
                {productTypeHeaders.length > 0 && (
                  <th colSpan={productTypeHeaders.length} className="te-matrix-group-heading">
                    Product Type
                  </th>
                )}
              </tr>
              <tr>
                {highlightedHeaders.map((header) => (
                  <th key={header} className="te-matrix-capability-heading">
                    {header}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {items.map((item, index) => {
                const showTopic = index === 0 || items[index - 1]?.topic !== item.topic;
                return (
                <tr key={item.id}>
                  <td className="te-topic-cell">{showTopic ? (item.topic || '-') : ''}</td>
                  <td className="te-product-cell">{item.product || '-'}</td>
                  <td className="te-size-cell">
                    {isValidate ? (
                      <select
                        className="te-edit-select te-size-edit"
                        value={item.size || ''}
                        disabled={Boolean(savingCell)}
                        onChange={(event) => updateValidation(
                          item,
                          { size: event.target.value },
                          `${item.id}-size`
                        )}
                        aria-label={`Validate size for ${item.product}`}
                      >
                        {['XXS', 'XS', 'S', 'M', 'L', 'XL', 'XXL'].map((size) => (
                          <option key={size} value={size}>{size}</option>
                        ))}
                      </select>
                    ) : (
                      <span className="te-size-badge">{item.size || '-'}</span>
                    )}
                    {item.size_source && (
                      <small>
                        {item.size_source === 'validated'
                          ? 'Validated'
                          : item.size_source === 'wave_inputs'
                            ? 'Wave Inputs'
                            : item.size_source === 'categorize_workbook'
                              ? 'Workbook'
                              : 'Calculated'}
                      </small>
                    )}
                  </td>
                  {highlightedHeaders.map((header) => {
                    const enrichedValue = item.enrichment_payload?.[header];
                    const value = normalizeMatrixDisplayValue(header, enrichedValue);
                    const displayValue = value;
                    const badgeClass = `te-value-badge te-value-${value.toLowerCase()}`;
                    const options = productTypeHeaders.includes(header)
                      ? ['COTS', 'Custom', 'Hybrid', 'Unknown']
                      : ['Yes', 'No', 'Partial', 'Unknown'];
                    return (
                      <td key={`${item.id}-${header}`} className="te-matrix-value-cell">
                        {isValidate ? (
                          <select
                            className={`te-edit-select ${badgeClass}`}
                            value={displayValue}
                            disabled={Boolean(savingCell)}
                            onChange={(event) => updateValidation(
                              item,
                              { values: { [header]: event.target.value } },
                              `${item.id}-${header}`
                            )}
                            aria-label={`Validate ${header} for ${item.product}`}
                          >
                            {options.map((option) => <option key={option} value={option}>{option}</option>)}
                          </select>
                        ) : (
                          <span className={badgeClass}>{displayValue}</span>
                        )}
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
