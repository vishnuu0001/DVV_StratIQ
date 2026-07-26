// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: OpportunityTracker — frontend/src/pages (OpportunityReport.jsx)
// Date: 2026-07-15
// ---------------------------------------------------------------------------
import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { createColumnHelper, flexRender, getCoreRowModel, useReactTable } from '@tanstack/react-table';
import { Edit2, Save, X, Trash2, RefreshCw, Download } from 'lucide-react';
import toast from 'react-hot-toast';
import * as XLSX from 'xlsx';
import api from '../services/api';
import { STAGES, STAGE_COLORS } from '../constants/stages';

const VALIDATION = ['Yes', 'No', 'Pending'];
// Matches the real values in the source data (Americas/Europe/APJ), plus a
// couple not yet seen but plausible for future manual entries.
const REGIONS = ['Americas', 'Europe', 'APJ', 'MEA', 'Global'];
const HYPERSCALERS = ['AWS', 'Azure', 'GCP', 'Multi-Cloud', 'None', 'Other'];
const SUB_VERTICALS = ['Automotive', 'Industrial Manufacturing', 'Process Manufacturing', 'A&D', 'Aero & Defense', 'Hi-Tech', 'Energy & Utilities', 'Other'];

// Column config drives both the TanStack column defs and the edit-cell renderers —
// same shape as the previous hand-rolled COLS array (key/label/width/type/options/commercial),
// just carried through TanStack's `meta` instead of being read directly off a plain array.
const COL_DEFS = [
  { key: 'region', label: 'Region', width: 100, type: 'select', options: REGIONS },
  { key: 'customer_group', label: 'Customer Group', width: 160, type: 'text' },
  { key: 'sub_vertical', label: 'Sub Vertical', width: 140, type: 'select', options: SUB_VERTICALS },
  { key: 'solution_offering', label: 'Solution/Offering', width: 160, type: 'text' },
  { key: 'so_coe_leader', label: 'SO/COE Leader', width: 130, type: 'text' },
  { key: 'crm_ref', label: 'CRM Ref #', width: 110, type: 'text' },
  { key: 'opportunity_name', label: 'Opportunity Name', width: 200, type: 'text' },
  { key: 'oppty_stage', label: 'Stage', width: 160, type: 'select', options: STAGES },
  { key: 'start_date', label: 'Start Date', width: 110, type: 'date' },
  { key: 'oppty_owner', label: 'Owner', width: 120, type: 'text' },
  { key: 'tcv_mn', label: 'TCV $Mn', width: 90, type: 'number', commercial: true },
  { key: 'q1_mn', label: "Q1'27 $Mn", width: 90, type: 'number', commercial: true },
  { key: 'q2_mn', label: "Q2'27 $Mn", width: 90, type: 'number', commercial: true },
  { key: 'q3_mn', label: "Q3'27 $Mn", width: 90, type: 'number', commercial: true },
  { key: 'q4_mn', label: "Q4'27 $Mn", width: 90, type: 'number', commercial: true },
  { key: 'fy27_mn', label: "FY'27 $Mn", width: 90, type: 'readonly', commercial: true },
  { key: 'remarks', label: 'Remarks', width: 180, type: 'text' },
  { key: 'hyperscaler', label: 'Hyperscaler', width: 100, type: 'select', options: HYPERSCALERS },
  { key: 'delivery_ibu', label: 'Delivery IBU', width: 110, type: 'text' },
  { key: 'delivery_ibu_leader', label: 'IBU Leader', width: 120, type: 'text' },
  { key: 'delivery_validation', label: 'Validation', width: 100, type: 'select', options: VALIDATION },
];

const columnHelper = createColumnHelper();

// Function: CellEditor
function CellEditor({ col, value, onChange }) {
  if (col.type === 'readonly') {
    return <span className="text-cyan-300 font-semibold">{Number(value || 0).toFixed(2)}</span>;
  }
  if (col.type === 'select') {
    return (
      <select className="ot-cell-input" value={value || ''} onChange={(e) => onChange(e.target.value)}>
        <option value="">—</option>
        {(col.options || []).map((o) => <option key={o} value={o}>{o}</option>)}
      </select>
    );
  }
  if (col.type === 'number') {
    return (
      <input
        className="ot-cell-input text-right"
        type="number" min="0" step="0.01"
        value={value ?? ''}
        onChange={(e) => onChange(e.target.value)}
        style={{ width: col.width - 16 }}
      />
    );
  }
  return (
    <input
      className="ot-cell-input"
      type={col.type === 'date' ? 'date' : 'text'}
      value={value ?? ''}
      onChange={(e) => onChange(e.target.value)}
      style={{ width: col.width - 16 }}
    />
  );
}

// Function: CellDisplay
function CellDisplay({ col, value }) {
  if (col.type === 'number' || col.type === 'readonly') {
    const num = Number(value || 0);
    return (
      <span className={`font-mono ${col.commercial ? 'text-cyan-200' : 'text-slate-200'}`}>
        {num.toFixed(2)}
      </span>
    );
  }
  if (col.key === 'oppty_stage') {
    const cls = STAGE_COLORS[value] || 'bg-slate-500/20 text-slate-300 border-slate-500/30';
    return <span className={`ot-badge border text-[10px] ${cls}`}>{value || 'Unspecified'}</span>;
  }
  return <span className="truncate max-w-[200px] block" title={value}>{value || <span className="text-slate-600">—</span>}</span>;
}

// Function: fmtMn
function fmtMn(v) { return v ? Number(v).toFixed(2) : '0.00'; }

// Function: OpportunityReport
export default function OpportunityReport({ refreshKey }) {
  const [rows, setRows] = useState([]);
  const [editMap, setEditMap] = useState({});     // id -> draft object
  const [saving, setSaving] = useState({});       // id -> bool
  const [deleting, setDeleting] = useState({});
  const [loading, setLoading] = useState(true);
  const [filterStage, setFilterStage] = useState('');
  const [filterRegion, setFilterRegion] = useState('');

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const { data } = await api.get('opportunities');
      setRows(data);
    } catch { toast.error('Failed to load opportunities.'); }
    finally { setLoading(false); }
  }, []);

  useEffect(() => { load(); }, [load, refreshKey]);

  // Function: startEdit
  const startEdit = (row) => setEditMap((m) => ({ ...m, [row.id]: { ...row } }));
  // Function: cancelEdit
  const cancelEdit = (id) => setEditMap((m) => { const n = { ...m }; delete n[id]; return n; });
  // Function: setDraftField
  const setDraftField = (id, key, value) =>
    setEditMap((m) => ({ ...m, [id]: { ...m[id], [key]: value } }));

  // Function: saveRow
  const saveRow = async (id) => {
    const draft = editMap[id];
    setSaving((s) => ({ ...s, [id]: true }));
    try {
      const payload = {
        ...draft,
        tcv_mn: parseFloat(draft.tcv_mn) || 0,
        q1_mn: parseFloat(draft.q1_mn) || 0,
        q2_mn: parseFloat(draft.q2_mn) || 0,
        q3_mn: parseFloat(draft.q3_mn) || 0,
        q4_mn: parseFloat(draft.q4_mn) || 0,
        fy27_mn: undefined,
        created_at: undefined,
        updated_at: undefined,
      };
      const { data } = await api.put(`opportunities/${id}`, payload);
      setRows((r) => r.map((row) => (row.id === id ? data : row)));
      cancelEdit(id);
      toast.success('Saved.');
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Save failed.');
    } finally {
      setSaving((s) => ({ ...s, [id]: false }));
    }
  };

  // Function: deleteRow
  const deleteRow = async (id) => {
    if (!window.confirm('Delete this opportunity?')) return;
    setDeleting((d) => ({ ...d, [id]: true }));
    try {
      await api.delete(`opportunities/${id}`);
      setRows((r) => r.filter((row) => row.id !== id));
      cancelEdit(id);
      toast.success('Deleted.');
    } catch { toast.error('Delete failed.'); }
    finally { setDeleting((d) => ({ ...d, [id]: false })); }
  };

  // Filter
  const visible = useMemo(() => rows.filter((r) => {
    if (filterStage && r.oppty_stage !== filterStage) return false;
    if (filterRegion && r.region !== filterRegion) return false;
    return true;
  }), [rows, filterStage, filterRegion]);

  // Column totals for commercial columns
  const totals = useMemo(() => COL_DEFS.reduce((acc, col) => {
    if (col.commercial) {
      acc[col.key] = visible.reduce((s, r) => s + (Number(r[col.key]) || 0), 0);
    }
    return acc;
  }, {}), [visible]);

  // TanStack column defs — one accessor column per COL_DEFS entry, plus id/actions.
  // meta carries the same {type, options, commercial} the CellEditor/CellDisplay
  // renderers switch on; editMap/saveRow/deleteRow state is unchanged from before —
  // TanStack only replaces the raw <table> JSX, not the edit-state model.
  const columns = useMemo(() => [
    columnHelper.accessor('id', {
      header: '#',
      size: 36,
      cell: (info) => <span className="text-slate-500 text-xs font-mono">{info.getValue()}</span>,
    }),
    ...COL_DEFS.map((col) => columnHelper.accessor(col.key, {
      header: col.label,
      size: col.width,
      meta: col,
    })),
  ], []);

  const table = useReactTable({
    data: visible,
    columns,
    getCoreRowModel: getCoreRowModel(),
  });

  // Excel export
  // Function: exportXlsx
  const exportXlsx = () => {
    const exportData = visible.map((r) => ({
      '#': r.id,
      Region: r.region,
      'Customer Group': r.customer_group,
      'Sub Vertical': r.sub_vertical,
      'Solution/Offering': r.solution_offering,
      'SO/COE Leader': r.so_coe_leader,
      'CRM Ref #': r.crm_ref,
      'Opportunity Name': r.opportunity_name,
      Stage: r.oppty_stage,
      'Start Date': r.start_date,
      Owner: r.oppty_owner,
      'TCV $Mn': r.tcv_mn,
      "Q1'27 $Mn": r.q1_mn,
      "Q2'27 $Mn": r.q2_mn,
      "Q3'27 $Mn": r.q3_mn,
      "Q4'27 $Mn": r.q4_mn,
      "FY'27 $Mn": r.fy27_mn,
      Remarks: r.remarks,
      Hyperscaler: r.hyperscaler,
      'Delivery IBU': r.delivery_ibu,
      'IBU Leader': r.delivery_ibu_leader,
      Validation: r.delivery_validation,
    }));
    const ws = XLSX.utils.json_to_sheet(exportData);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'Opportunities');
    XLSX.writeFile(wb, `OpportunityTracker_${new Date().toISOString().slice(0, 10)}.xlsx`);
  };

  return (
    <div className="space-y-5">
      {/* Toolbar */}
      <div className="flex flex-wrap items-center gap-3">
        <select
          className="ot-select text-sm w-48"
          value={filterStage}
          onChange={(e) => setFilterStage(e.target.value)}
        >
          <option value="">All Stages</option>
          {STAGES.map((s) => <option key={s} value={s}>{s}</option>)}
        </select>
        <select
          className="ot-select text-sm w-40"
          value={filterRegion}
          onChange={(e) => setFilterRegion(e.target.value)}
        >
          <option value="">All Regions</option>
          {REGIONS.map((r) => <option key={r} value={r}>{r}</option>)}
        </select>
        <div className="flex-1" />
        <span className="text-xs text-slate-500">{visible.length} record{visible.length !== 1 ? 's' : ''}</span>
        <button onClick={load} className="ot-btn-secondary text-xs px-3 py-1.5">
          <RefreshCw size={13} className={loading ? 'animate-spin' : ''} /> Refresh
        </button>
        <button onClick={exportXlsx} className="ot-btn-secondary text-xs px-3 py-1.5">
          <Download size={13} /> Export XLSX
        </button>
      </div>

      {loading ? (
        <div className="h-40 flex items-center justify-center text-slate-500">
          <span className="w-6 h-6 rounded-full border-2 border-cyan-500 border-t-transparent animate-spin mr-3" />
          Loading opportunities…
        </div>
      ) : visible.length === 0 ? (
        <div className="ot-card p-16 text-center text-slate-500">
          <p className="text-lg font-semibold text-slate-400 mb-2">No opportunities found</p>
          <p className="text-sm">Add one using the &ldquo;New Opportunity&rdquo; tab, or import the FY27 Plan Tracker workbook.</p>
        </div>
      ) : (
        <div className="ot-table-wrap">
          <table className="ot-table">
            <thead>
              {table.getHeaderGroups().map((headerGroup) => (
                <tr key={headerGroup.id}>
                  {headerGroup.headers.map((header) => {
                    const meta = header.column.columnDef.meta;
                    return (
                      <th
                        key={header.id}
                        className={meta?.commercial ? 'commercial' : ''}
                        style={{ minWidth: header.getSize() }}
                      >
                        {flexRender(header.column.columnDef.header, header.getContext())}
                      </th>
                    );
                  })}
                  <th style={{ width: 100 }}>Actions</th>
                </tr>
              ))}
            </thead>
            <tbody>
              {table.getRowModel().rows.map((tableRow) => {
                const row = tableRow.original;
                const isEditing = !!editMap[row.id];
                const draft = editMap[row.id] || row;
                const isSaving = saving[row.id];
                const isDeleting = deleting[row.id];

                return (
                  <tr key={row.id} className={isEditing ? 'bg-slate-800/50' : ''}>
                    {tableRow.getVisibleCells().map((cell) => {
                      const col = cell.column.columnDef.meta;
                      if (!col) {
                        // the leading '#' id column has no meta — render as-is
                        return (
                          <td key={cell.id} style={{ width: 36 }}>
                            {flexRender(cell.column.columnDef.cell, cell.getContext())}
                          </td>
                        );
                      }
                      return (
                        <td key={cell.id} style={{ minWidth: col.width }}>
                          {isEditing && col.type !== 'readonly'
                            ? <CellEditor col={col} value={draft[col.key]} onChange={(v) => setDraftField(row.id, col.key, v)} />
                            : <CellDisplay col={col} value={col.key === 'fy27_mn' ? row.fy27_mn : row[col.key]} />
                          }
                        </td>
                      );
                    })}
                    <td>
                      <div className="flex items-center gap-1">
                        {isEditing ? (
                          <>
                            <button onClick={() => saveRow(row.id)} disabled={isSaving} className="ot-btn-success">
                              {isSaving ? <span className="w-3 h-3 rounded-full border border-emerald-400 border-t-transparent animate-spin" /> : <Save size={12} />}
                              Save
                            </button>
                            <button onClick={() => cancelEdit(row.id)} className="ot-btn-secondary text-xs px-2 py-1">
                              <X size={12} />
                            </button>
                          </>
                        ) : (
                          <>
                            <button onClick={() => startEdit(row)} className="ot-btn-secondary text-xs px-2 py-1.5">
                              <Edit2 size={12} />
                            </button>
                            <button onClick={() => deleteRow(row.id)} disabled={isDeleting} className="ot-btn-danger">
                              {isDeleting ? <span className="w-3 h-3 rounded-full border border-red-400 border-t-transparent animate-spin" /> : <Trash2 size={12} />}
                            </button>
                          </>
                        )}
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
            {/* Totals footer */}
            <tfoot>
              <tr>
                <td className="label" colSpan={11 + 1}>TOTALS</td>
                {COL_DEFS.filter((c) => c.commercial).map((col) => (
                  <td key={col.key} className="text-right font-mono">
                    {fmtMn(totals[col.key])}
                  </td>
                ))}
                <td colSpan={5} />
                <td />
              </tr>
            </tfoot>
          </table>
        </div>
      )}
    </div>
  );
}
