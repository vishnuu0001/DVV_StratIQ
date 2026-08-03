// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: AppRationalization - frontend/src/components (TechnicalEvaluationCategorize.jsx)
// Date: 2026-08-02
// ---------------------------------------------------------------------------
import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { toast } from 'react-toastify';
import * as XLSX from 'xlsx';
import {
  clearTechnicalAssessmentData,
  enrichTechnicalEvaluationCategorizeTopic,
  getTechnicalEvaluationCategorizeDashboard,
  uploadTechnicalEvaluationCategorize,
  updateTechnicalEvaluationValidation,
} from '../services/api';

const TECHNICAL_EVALUATION_TOPIC = 'Harmonize Maintenance Management Systems';

// Function: excelSafeValue
// Prevent values originating in an uploaded workbook from becoming formulas
// when the generated report is opened in Excel.
const excelSafeValue = (value) => {
  const text = String(value ?? '').trim();
  return /^[=+\-@]/.test(text) ? `'${text}` : text;
};

// Function: sizeSourceLabel
const sizeSourceLabel = (source) => ({
  validated: 'Validated',
  wave_inputs: 'Wave Inputs',
  categorize_workbook: 'Categorize Workbook',
  calculated: 'Calculated',
}[source] || (source ? String(source) : ''));

// Function: normalizeMatrixDisplayValue
const normalizeMatrixDisplayValue = (header, value) => {
  const text = String(value ?? '').trim();
  const isProductType = ['product type', 'cots', 'custom'].some((token) =>
    String(header || '').toLowerCase().includes(token)
  );
  if (!text) return isProductType ? 'Unknown' : 'No';
  const lower = text.toLowerCase();

  if (isProductType) {
    if (lower.includes('hybrid')) return 'Hybrid';
    if (lower.includes('cots') || lower.includes('available in market')) return 'COTS';
    if (lower.includes('custom')) return 'Custom';
    return 'Unknown';
  }

  if (['yes', 'y', 'x', 'true', 'supported', 'available'].includes(lower)) return 'Yes';
  if (['no', 'n', 'false', 'unsupported', 'unavailable'].includes(lower)) return 'No';
  if (lower.includes('partial') || lower.includes('limited')) return 'Partial';
  if (lower.includes('unknown') || lower === 'n/a') return 'No';

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
  const [appliedSearch, setAppliedSearch] = useState('');
  const [selectedTopic, setSelectedTopic] = useState(TECHNICAL_EVALUATION_TOPIC);
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
      setAppliedSearch(query || '');
    } catch (error) {
      toast.error(error.response?.data?.error || 'Unable to load Categorize dashboard');
    }
  }, [selectedTopic]);

  useEffect(() => {
    loadDashboard();
  }, [loadDashboard]);

  useEffect(() => {
    const topics = dashboard.topics || [];
    const approvedTopic = topics.find(
      (topic) => String(topic).trim().toLowerCase() === TECHNICAL_EVALUATION_TOPIC.toLowerCase()
    );
    if (approvedTopic && approvedTopic !== selectedTopic) {
      setSelectedTopic(approvedTopic);
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
      const topicToEnrich = availableTopics.find(
        (topic) => String(topic).trim().toLowerCase() === TECHNICAL_EVALUATION_TOPIC.toLowerCase()
      );
      setDashboard(initialData);
      setAppliedSearch('');
      if (topicToEnrich) setSelectedTopic(topicToEnrich);
      setFile(null);
      if (topicToEnrich && initialData.market_search?.configured) {
        await runEnrichment(topicToEnrich, true);
      } else if (!topicToEnrich) {
        throw new Error(`Uploaded workbook does not contain '${TECHNICAL_EVALUATION_TOPIC}'`);
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
      setAppliedSearch('');
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
      setAppliedSearch('');
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

  // Function: downloadExcelReport
  const downloadExcelReport = () => {
    if (!items.length) {
      toast.info('No dashboard rows are available to export');
      return;
    }

    try {
      const exportedAt = new Date();
      const matrixHeaders = [
        'Topic', 'Product', 'Size', 'Size Source',
        ...capabilityHeaders,
        ...productTypeHeaders,
      ];
      const matrixRows = items.map((item) => [
        excelSafeValue(item.topic),
        excelSafeValue(item.product),
        excelSafeValue(item.size || '-'),
        excelSafeValue(sizeSourceLabel(item.size_source)),
        ...capabilityHeaders.map((header) => excelSafeValue(
          normalizeMatrixDisplayValue(header, item.enrichment_payload?.[header])
        )),
        ...productTypeHeaders.map((header) => excelSafeValue(
          normalizeMatrixDisplayValue(header, item.enrichment_payload?.[header])
        )),
      ]);

      const matrixSheet = XLSX.utils.aoa_to_sheet([matrixHeaders, ...matrixRows]);
      matrixSheet['!autofilter'] = { ref: `A1:${XLSX.utils.encode_col(matrixHeaders.length - 1)}${matrixRows.length + 1}` };
      matrixSheet['!cols'] = matrixHeaders.map((header, index) => ({
        wch: Math.min(
          48,
          Math.max(
            index === 1 ? 28 : 14,
            String(header).length + 2,
            ...matrixRows.map((row) => String(row[index] ?? '').length + 2)
          )
        ),
      }));

      const summaryRows = [
        ['Technical Evaluation Capability Matrix Report'],
        [],
        ['Topic', excelSafeValue(selectedTopic)],
        ['Report Mode', isValidate ? 'Validate' : 'Categorize'],
        ['Exported At', exportedAt.toLocaleString()],
        ['Source Workbook', excelSafeValue(dashboard.import?.source_filename || '')],
        ['Imported At', dashboard.import?.imported_at
          ? new Date(dashboard.import.imported_at).toLocaleString()
          : ''],
        ['Applied Product Filter', excelSafeValue(appliedSearch || 'None')],
        ['Products In Report', totals.productCount],
        ['Rows In Report', items.length],
        ['Capability Columns', capabilityHeaders.length],
        ['Product Type Columns', productTypeHeaders.length],
        [],
        ['Capabilities'],
        ...capabilityHeaders.map((header) => [excelSafeValue(header)]),
        [],
        ['Product Type Columns'],
        ...productTypeHeaders.map((header) => [excelSafeValue(header)]),
      ];
      const summarySheet = XLSX.utils.aoa_to_sheet(summaryRows);
      summarySheet['!cols'] = [{ wch: 30 }, { wch: 64 }];
      summarySheet['!merges'] = [XLSX.utils.decode_range('A1:B1')];

      const workbook = XLSX.utils.book_new();
      XLSX.utils.book_append_sheet(workbook, summarySheet, 'Report Summary');
      XLSX.utils.book_append_sheet(workbook, matrixSheet, 'Capability Matrix');
      workbook.Props = {
        Title: `${selectedTopic} Capability Matrix`,
        Subject: 'Technical Evaluation Dashboard Report',
        Author: 'App Rationalization Platform',
        CreatedDate: exportedAt,
      };

      const date = exportedAt.toISOString().slice(0, 10).replace(/-/g, '');
      const topicSlug = selectedTopic.replace(/[^a-z0-9]+/gi, '_').replace(/^_+|_+$/g, '').slice(0, 80);
      XLSX.writeFile(workbook, `Capability_Matrix_${topicSlug}_${date}.xlsx`, { compression: true });
      toast.success(`Excel report downloaded with ${items.length} product row(s)`);
    } catch (error) {
      toast.error(`Unable to create Excel report: ${error.message || 'Unknown error'}`);
    }
  };

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
          <button
            onClick={downloadExcelReport}
            className="az-btn az-btn-primary"
            disabled={busy || enriching || !items.length}
            title="Download the current dashboard as an Excel workbook"
          >
            Download Excel Report
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
                      : ['Yes', 'No', 'Partial'];
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
