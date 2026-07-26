// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: AppRationalization — frontend/src/components (TechnicalAssessmentData.jsx)
// Date: 2025-10-13
// ---------------------------------------------------------------------------
import React, { useEffect, useState } from 'react';
import { toast } from 'react-toastify';
import {
  clearTechnicalAssessmentData,
  getTechnicalAssessmentData,
  uploadTechnicalAssessment,
} from '../services/api';

const CONFIG = {
  'business-validations': {
    title: 'Business Validations',
    description: 'Review the categorized application inventory, capabilities, inconsistency flags and rationale.',
    source: 'Business_Applications sheet',
    columns: [
      ['application_number', 'Number'],
      ['name', 'Name'],
      ['categorization', 'Categorization'],
      ['application_family', 'Application family'],
      ['business_owner', 'Business owner'],
      ['department', 'Department'],
      ['olb_level_2', 'OLB Level 2'],
      ['it_application_owner', 'IT Application owner'],
      ['gd_segments', 'GD Segments'],
      ['department_2', 'Department2'],
      ['olb_level_23', 'OLB Level 23'],
      ['architecture_type', 'Architecture type'],
      ['platform_host', 'Platform Host'],
      ['application_type', 'Application type'],
      ['install_type', 'Install type'],
      ['capabilities', 'Capabilities'],
      ['inconsistency', 'Inconsistency'],
      ['rationale', 'Rationale'],
    ],
  },
  'wave-inputs': {
    title: 'Wave Inputs',
    description: 'Collect and review the application-level inputs used for harmonization wave planning.',
    source: 'Wave_Plan_Input sheet',
    columns: [
      ['app_id', 'App ID'],
      ['application_name', 'Application Name'],
      ['topic', 'Topic (Categorization)'],
      ['business_capability', 'Business Capability (from source col P)'],
      ['capability_confirmed', 'Capability Confirmed?'],
      ['business_rationale', 'Business Rationale'],
      ['disposition', 'Disposition'],
      ['target_platform', 'Target Platform'],
      ['migration_approach', 'Migration Approach'],
      ['migration_type', 'Migration Type'],
      ['tshirt_size', 'T-Shirt Size'],
      ['complexity', 'Complexity'],
      ['table_count', '# Tables'],
      ['data_volume_records', 'Data Volume (records)'],
      ['change_impact', 'Change Impact'],
      ['risk', 'Risk'],
      ['quick_win', 'Quick Win'],
      ['business_criticality', 'Business Criticality'],
      ['department', 'Department'],
      ['business_owner', 'Business Owner'],
      ['install_type', 'Install Type'],
      ['site_region', 'Site / Region'],
      ['dependencies', 'Dependencies (App IDs)'],
      ['dependency_readiness', 'Dependency Readiness'],
      ['earliest_start', 'Earliest Start'],
      ['latest_finish', 'Latest Finish'],
      ['regulatory_hold', 'Regulatory Hold?'],
      ['assessment_effort_hours', 'Assessment Effort (hrs)'],
      ['migration_effort_hours', 'Migration Effort (hrs)'],
      ['total_effort_hours', 'Total Effort (hrs)'],
      ['wave_eligibility_score', 'Wave Eligibility Score'],
      ['proposed_wave', 'Proposed Wave'],
      ['sme_owner', 'SME / Owner'],
      ['workshop_date', 'Workshop Date'],
      ['signoff_status', 'Sign-off Status'],
      ['comments', 'Comments'],
    ],
  },
};

// Function: TechnicalAssessmentData
const TechnicalAssessmentData = ({ dataset }) => {
  const config = CONFIG[dataset];
  const [data, setData] = useState({ items: [], total: 0, import: null });
  const [file, setFile] = useState(null);
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [busy, setBusy] = useState(false);

  // Function: refresh
  const refresh = async () => {
    try {
      const response = await getTechnicalAssessmentData(dataset, page, 25, search);
      setData(response.data);
    } catch (error) {
      toast.error(error.response?.data?.error || 'Unable to load Technical Assessment data');
    }
  };
  useEffect(() => { refresh(); }, [dataset, page, search]); // eslint-disable-line react-hooks/exhaustive-deps

  // Function: runImport
  const runImport = async (sourceFile) => {
    setBusy(true);
    try {
      const response = await uploadTechnicalAssessment(dataset, sourceFile);
      toast.success(`${response.data.import.row_count} rows imported`);
      setFile(null);
      setPage(1);
      await refresh();
    } catch (error) {
      toast.error(error.response?.data?.error || 'Import failed');
    } finally {
      setBusy(false);
    }
  };

  // Function: runClear
  const runClear = async () => {
    if (!window.confirm(`Clear all ${config.title} data? This cannot be undone.`)) return;
    setBusy(true);
    try {
      const response = await clearTechnicalAssessmentData(dataset);
      toast.success(`Cleared ${response.data.cleared_rows} row(s)`);
      setPage(1);
      await refresh();
    } catch (error) {
      toast.error(error.response?.data?.error || 'Clear failed');
    } finally {
      setBusy(false);
    }
  };
  const pages = Math.max(1, Math.ceil(data.total / 25));

  return (
    <div className="p-6 text-slate-100">
      <div className="mb-5">
        <p className="text-xs uppercase tracking-[0.2em] text-cyan-400">Technical Assessment</p>
        <h1 className="text-2xl font-bold mt-1">{config.title}</h1>
        <p className="text-sm text-slate-400 mt-1">{config.description}</p>
      </div>
      <div className="rounded-xl border border-slate-700 bg-slate-900/70 p-5 mb-5">
        <p className="text-xs text-slate-400 mb-3">Expected workbook data: <span className="text-cyan-300">{config.source}</span></p>
        <div className="flex flex-wrap items-center gap-3">
          <input type="file" accept=".xlsx" onChange={(event) => setFile(event.target.files?.[0] || null)}
            className="text-sm text-slate-300 file:mr-3 file:rounded-lg file:border-0 file:bg-slate-700 file:px-3 file:py-2 file:text-white" />
          <button disabled={!file || busy} onClick={() => runImport(file)}
            className="portal-btn-primary px-4 py-2 rounded-lg disabled:opacity-40">Upload Workbook</button>
          <button disabled={busy || !data.import} onClick={runClear}
            className="portal-btn-secondary px-4 py-2 rounded-lg disabled:opacity-40">Clear Data</button>
        </div>
        {data.import && <p className="text-xs text-slate-500 mt-3">
          Latest import: {data.import.source_filename} · {data.import.row_count} rows · {new Date(data.import.imported_at).toLocaleString()}
        </p>}
      </div>
      <div className="rounded-xl border border-slate-700 bg-slate-900/70 overflow-hidden">
        <div className="p-4 flex justify-between items-center border-b border-slate-700">
          <input value={search} onChange={(event) => { setSearch(event.target.value); setPage(1); }}
            placeholder="Search applications or topics" className="w-80 max-w-full rounded-lg bg-slate-950 border border-slate-700 px-3 py-2 text-sm" />
          <span className="text-xs text-slate-400">{data.total} records</span>
        </div>
        <div className="overflow-auto max-h-[58vh]">
          <table className="w-max min-w-full text-xs">
            <thead className="sticky top-0 bg-slate-800 text-slate-300">
              <tr>{config.columns.map(([, label]) => <th key={label} className="text-left px-3 py-3 whitespace-nowrap">{label}</th>)}</tr>
            </thead>
            <tbody>{data.items.map((row) => (
              <tr key={row.id} className="border-t border-slate-800 hover:bg-slate-800/50">
                {config.columns.map(([key]) => <td key={key} className="px-3 py-3 min-w-[160px] max-w-sm whitespace-normal break-words" title={String(row[key] ?? '')}>
                  {typeof row[key] === 'boolean' ? (row[key] ? 'Yes' : 'No') : (row[key] ?? '—')}
                </td>)}
              </tr>
            ))}</tbody>
          </table>
          {!data.items.length && <div className="p-10 text-center text-slate-500">No data imported yet.</div>}
        </div>
        <div className="p-3 flex justify-end items-center gap-3 border-t border-slate-700 text-xs">
          <button disabled={page <= 1} onClick={() => setPage(page - 1)}>Previous</button>
          <span>Page {page} of {pages}</span>
          <button disabled={page >= pages} onClick={() => setPage(page + 1)}>Next</button>
        </div>
      </div>
    </div>
  );
};
export default TechnicalAssessmentData;
