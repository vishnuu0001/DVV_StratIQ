// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: Microsite_Data_Analysis — src (App.jsx)
// Date: 2025-10-07
// ---------------------------------------------------------------------------
import { useState, useMemo, useEffect } from 'react';
import { createRoot } from 'react-dom/client';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, PieChart, Pie, Cell, Legend,
} from 'recharts';
import {
  BarChart3, SlidersHorizontal, Database, Building2,
  TrendingUp, Zap, Plus, Trash2, RefreshCw, ChevronRight,
  AlertTriangle, Map, Activity, LayoutGrid,
} from 'lucide-react';
import {
  defaultAssumptions, defaultVendorSpend, defaultTowers,
  defaultReinvestment, defaultRoadmap,
  TOWER_NAMES, ACTION_OPTIONS, STATUS_OPTIONS,
} from './data.js';
import {
  calculateTowerOutput, calculateScenarioTotals, calculateReinvestment,
  fmtM, fmtPct1,
} from './calculations.js';
import './styles.css';
import {
  getPortalHomeUrl, getPortalAdminUrl, consumePortalTokenFromHash,
  getPortalToken, decodePortalUser, logoutFromPortal,
} from './portalAuth.js';

// ── Constants ─────────────────────────────────────────────────────────────
const PALETTE = ['#06b6d4', '#6366f1', '#10b981', '#f59e0b', '#f43f5e', '#a855f7'];
const CHART_GRID = 'rgba(148,163,184,0.06)';
const TICK = { fill: '#475569', fontSize: 11 };
const AXIS_LINE = { stroke: '#1e293b' };

const SECTIONS = [
  { id: 'dashboard',    label: 'Executive Dashboard',            Icon: BarChart3,         phase: 'MVP' },
  { id: 'inputs',       label: 'Assumption Manager',             Icon: SlidersHorizontal, phase: 'MVP' },
  { id: 'vendor-spend', label: 'Vendor Spend Data Entry',        Icon: Database,          phase: 'MVP' },
  { id: 'tower-studio', label: 'Tower Consolidation Studio',     Icon: Building2,         phase: 'MVP' },
  { id: 'savings',      label: 'Savings / Capacity Summary',     Icon: TrendingUp,        phase: 'MVP' },
  { id: 'reinvest',     label: 'Transformation Capacity Engine', Icon: Zap,               phase: 'MVP' },
  { id: 'roadmap',      label: 'Transition Roadmap',             Icon: Map,               phase: 'MVP' },
];

const SECTION_META = {
  'dashboard':    { title: 'Executive Dashboard',            sub: 'High-level scenario overview — spend, capacity and savings at a glance' },
  'inputs':       { title: 'Assumption Manager',             sub: 'Adjust rate compression, productivity, overhead and transition cost parameters' },
  'vendor-spend': { title: 'Vendor Spend Data Entry',        sub: 'Current_Vendor_Spend register — source data powering all SUMIF / COUNTIF aggregations' },
  'tower-studio': { title: 'Tower Consolidation Studio',     sub: 'Configure scope % and action per tower; view the full calculation chain' },
  'savings':      { title: 'Savings / Capacity Summary',     sub: 'Aggregate savings waterfall — current → addressable → gross → net year-1' },
  'reinvest':     { title: 'Transformation Capacity Engine', sub: 'Allocate net year-1 capacity across strategic reinvestment areas' },
  'roadmap':      { title: 'Transition Roadmap',             sub: 'Exec6_Roadmap — milestones, owners and status tracking across six waves' },
};

// ── Persistence ───────────────────────────────────────────────────────────
// Function: num
function num(value, fallback = 0) {
  const next = Number(value);
  return Number.isFinite(next) ? next : fallback;
}

// Function: fixedNum
function fixedNum(value, digits = 2) {
  return +num(value).toFixed(digits);
}

// Function: load
function load(key, fallback) {
  try {
    const stored = JSON.parse(localStorage.getItem('mda_' + key));
    return stored ?? fallback;
  }
  catch { return fallback; }
}
// Function: save
function save(key, val) {
  try { localStorage.setItem('mda_' + key, JSON.stringify(val)); } catch {}
}

// Function: mergeObjectFallback
function mergeObjectFallback(stored, fallback) {
  return stored && typeof stored === 'object' && !Array.isArray(stored)
    ? { ...fallback, ...stored }
    : fallback;
}

// Function: mergeListFallback
function mergeListFallback(stored, fallback, key = 'id') {
  if (!Array.isArray(stored)) return fallback;
  const merged = fallback.map((base, index) => {
    const item = stored.find(s => s?.[key] === base[key]) ?? stored[index];
    return { ...base, ...(item && typeof item === 'object' ? item : {}) };
  });
  const extra = stored.filter(item => item?.[key] && !fallback.some(base => base[key] === item[key]));
  return [...merged, ...extra];
}

// ── Dark chart tooltip ────────────────────────────────────────────────────
// Function: DarkTip
function DarkTip({ active, payload, label }) {
  if (!active || !payload?.length) return null;
  return (
    <div className="chart-tooltip">
      <p style={{ fontSize: 11, color: '#64748b', marginBottom: 6 }}>{label}</p>
      {payload.map((p, i) => (
        <p key={i} style={{ color: p.fill || p.color, fontSize: 13, fontWeight: 700 }}>
          {p.name}: {typeof p.value === 'number' ? `$${Math.abs(p.value).toFixed(1)}M` : p.value}
        </p>
      ))}
    </div>
  );
}

// ── Status badge ──────────────────────────────────────────────────────────
// Function: StatusBadge
function StatusBadge({ status }) {
  const cls = { 'In Progress': 'b-cyan', 'Complete': 'b-emerald', 'At Risk': 'b-rose', 'Pending': 'b-slate' }[status] || 'b-slate';
  return <span className={`badge ${cls}`}>{status}</span>;
}

// ── KPI card ──────────────────────────────────────────────────────────────
// Function: KpiCard
function KpiCard({ label, value, note, accent }) {
  return (
    <div className="kpi-card">
      <div className="kpi-accent" style={{ background: accent }} />
      <div className="kpi-label">{label}</div>
      <div className="kpi-value">{value}</div>
      <div className="kpi-note">{note}</div>
    </div>
  );
}

// ══════════════════════════════════════════════════════════════════════════
// Section 1 — Executive Dashboard
// ══════════════════════════════════════════════════════════════════════════
// Function: ExecutiveDashboard
function ExecutiveDashboard({ towerOutputs, totals }) {
  const addrPct = totals.currentSpend > 0 ? totals.addressableSpend / totals.currentSpend : 0;

  const kpis = [
    { label: 'Total Current Spend',   value: fmtM(totals.currentSpend),        note: `${totals.vendorCount} active vendors`,        accent: 'linear-gradient(90deg,#3b82f6,#1d4ed8)' },
    { label: 'Addressable Spend',     value: fmtM(totals.addressableSpend),     note: `${fmtPct1(addrPct)} of current spend`,        accent: 'linear-gradient(90deg,#0891b2,#0e7490)' },
    { label: 'Gross Annual Capacity', value: fmtM(totals.grossAnnualCapacity),  note: 'Pre-transition savings pool',                 accent: 'linear-gradient(90deg,#06b6d4,#22d3ee)' },
    { label: 'Transition Cost',       value: fmtM(totals.transitionCost),       note: 'One-time investment year 1',                  accent: 'linear-gradient(90deg,#f43f5e,#e11d48)' },
    { label: 'Net Year-1 Capacity',   value: fmtM(totals.netYear1Capacity),     note: 'Available for reinvestment',                  accent: 'linear-gradient(90deg,#10b981,#059669)' },
  ];

  const towerBarData = towerOutputs.map(t => ({
    name: t.name.split(' / ')[0].replace('Cross-Tower ', 'X-Tower '),
    'Current Spend':   fixedNum(t.currentSpend),
    'Addressable':     fixedNum(t.addressableSpend),
    'Net Capacity':    fixedNum(t.netYear1Capacity),
  }));

  const leverData = [
    { name: 'Efficiency Savings', value: fixedNum(totals.efficiencySavings),  fill: '#10b981' },
    { name: 'Rate Savings',       value: fixedNum(totals.rateSavings),        fill: '#06b6d4' },
    { name: 'Vendor Mgmt',        value: fixedNum(totals.vendorMgmtSavings),  fill: '#6366f1' },
  ];

  return (
    <>
      <div className="kpi-grid" style={{ marginBottom: 20 }}>
        {kpis.map(k => <KpiCard key={k.label} {...k} />)}
      </div>
      <div className="g-2">
        <div className="card">
          <div className="card-title"><div className="card-icon"><BarChart3 size={14} color="#06b6d4" /></div>Tower Spend Overview</div>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={towerBarData} barGap={2} barCategoryGap="30%">
              <CartesianGrid strokeDasharray="3 3" stroke={CHART_GRID} vertical={false} />
              <XAxis dataKey="name" tick={TICK} axisLine={AXIS_LINE} tickLine={false} />
              <YAxis tick={TICK} axisLine={false} tickLine={false} tickFormatter={v => `$${v}M`} />
              <Tooltip content={<DarkTip />} cursor={{ fill: 'rgba(255,255,255,0.03)' }} />
              <Legend iconType="circle" iconSize={8} wrapperStyle={{ color: '#64748b', fontSize: 12 }} />
              <Bar dataKey="Current Spend" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              <Bar dataKey="Addressable"   fill="#06b6d4" radius={[4, 4, 0, 0]} />
              <Bar dataKey="Net Capacity"  fill="#10b981" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="card">
          <div className="card-title"><div className="card-icon"><TrendingUp size={14} color="#10b981" /></div>Gross Capacity — Savings Levers</div>
          <ResponsiveContainer width="100%" height={130}>
            <BarChart data={leverData} layout="vertical" barCategoryGap="35%">
              <CartesianGrid strokeDasharray="3 3" stroke={CHART_GRID} horizontal={false} />
              <XAxis type="number" tick={TICK} axisLine={false} tickLine={false} tickFormatter={v => `$${v}M`} />
              <YAxis type="category" dataKey="name" tick={{ fill: '#475569', fontSize: 11 }} axisLine={false} tickLine={false} width={110} />
              <Tooltip content={<DarkTip />} cursor={{ fill: 'rgba(255,255,255,0.03)' }} />
              <Bar dataKey="value" name="Savings" radius={[0, 4, 4, 0]}>
                {leverData.map((e, i) => <Cell key={i} fill={e.fill} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: 8, marginTop: 14 }}>
            {leverData.map(s => (
              <div key={s.name} style={{ background: 'rgba(255,255,255,0.03)', borderRadius: 10, padding: '10px 12px', borderTop: `2px solid ${s.fill}` }}>
                <div style={{ fontSize: 16, fontWeight: 900, color: s.fill }}>{fmtM(s.value)}</div>
                <div style={{ fontSize: 10.5, color: '#64748b', marginTop: 2 }}>{s.name}</div>
              </div>
            ))}
          </div>
          <div className="note-box">
            <strong>Gross Capacity {fmtM(totals.grossAnnualCapacity)}</strong> — after one-time transition investment of {fmtM(totals.transitionCost)}, yields <strong>Net Year-1 Capacity of {fmtM(totals.netYear1Capacity)}</strong> for strategic reinvestment.
          </div>
        </div>
      </div>
    </>
  );
}

// ══════════════════════════════════════════════════════════════════════════
// Section 2 — Assumption Manager
// ══════════════════════════════════════════════════════════════════════════
const SLIDERS = [
  { key: 'rateCompressionPct',    label: 'Rate Compression %',         min: 0, max: 30, step: 1   },
  { key: 'productivityPct',       label: 'Productivity Improvement %', min: 0, max: 30, step: 1   },
  { key: 'vendorMgmtOverheadPct', label: 'Vendor Mgmt Overhead %',     min: 0, max: 10, step: 0.5 },
  { key: 'overheadReductionPct',  label: 'Overhead Reduction %',       min: 0, max: 80, step: 5   },
  { key: 'transitionCostPct',     label: 'Transition Cost %',          min: 0, max: 20, step: 1   },
];

// Function: AssumptionManager
function AssumptionManager({ assumptions, setAssumptions, towerOutputs }) {
  // Function: handle
  function handle(key, raw) {
    const next = { ...assumptions, [key]: Number(raw) / 100 };
    setAssumptions(next);
    save('assumptions', next);
  }
  // Function: reset
  function reset() { setAssumptions(defaultAssumptions); save('assumptions', defaultAssumptions); }

  return (
    <div className="g-12" style={{ alignItems: 'start' }}>
      <div className="card">
        <div className="card-hdr">
          <div className="card-title"><div className="card-icon"><SlidersHorizontal size={14} color="#6366f1" /></div>Scenario Assumptions</div>
          <button className="btn btn-ghost" onClick={reset}><RefreshCw size={13} />Reset</button>
        </div>
        {SLIDERS.map(s => {
          const dispVal = (num(assumptions[s.key]) * 100).toFixed(s.step < 1 ? 1 : 0);
          return (
            <div key={s.key} className="slider-group">
              <div className="slider-hdr">
                <span className="slider-label">{s.label}</span>
                <span className="slider-val">{dispVal}%</span>
              </div>
              <input
                type="range" min={s.min} max={s.max} step={s.step}
                value={dispVal}
                onChange={e => handle(s.key, e.target.value)}
                style={{ accentColor: '#06b6d4' }}
              />
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 10, color: '#334155', marginTop: 2 }}>
                <span>{s.min}%</span><span>{s.max}%</span>
              </div>
            </div>
          );
        })}
      </div>

      <div className="card">
        <div className="card-title"><div className="card-icon"><TrendingUp size={14} color="#10b981" /></div>Live Scenario Preview</div>
        <div className="tbl-wrap">
          <table className="tbl">
            <thead>
              <tr>
                <th>Tower</th><th>Addressable</th><th>Efficiency</th>
                <th>Rate</th><th>VM Savings</th><th>Gross</th><th>Net Yr 1</th>
              </tr>
            </thead>
            <tbody>
              {towerOutputs.map(t => (
                <tr key={t.id}>
                  <td><strong>{t.name.split(' / ')[0]}</strong></td>
                  <td className="hi">{fmtM(t.addressableSpend)}</td>
                  <td className="pos">{fmtM(t.efficiencySavings)}</td>
                  <td className="pos">{fmtM(t.rateSavings)}</td>
                  <td className="pos">{fmtM(t.vendorMgmtSavings)}</td>
                  <td style={{ color: '#22d3ee', fontWeight: 700 }}>{fmtM(t.grossAnnualCapacity)}</td>
                  <td className="pos">{fmtM(t.netYear1Capacity)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: 8, marginTop: 14, padding: '12px 14px', background: 'rgba(6,182,212,0.04)', borderRadius: 10, border: '1px solid rgba(6,182,212,0.1)' }}>
          {SLIDERS.map(s => (
            <div key={s.key} style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 15, fontWeight: 900, color: '#38bdf8' }}>
                {(num(assumptions[s.key]) * 100).toFixed(s.step < 1 ? 1 : 0)}%
              </div>
              <div style={{ fontSize: 10, color: '#475569', marginTop: 2 }}>
                {s.label.split(' ').slice(0, 2).join(' ')}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// ══════════════════════════════════════════════════════════════════════════
// Section 3 — Vendor Spend Data Entry
// ══════════════════════════════════════════════════════════════════════════
const BLANK = { tower: '', vendor: '', category: '', annualSpend: '', contractDate: '' };

// Function: VendorSpendEntry
function VendorSpendEntry({ vendorSpend, setVendorSpend }) {
  const [filter, setFilter] = useState('All');
  const [newRow, setNewRow] = useState(BLANK);
  const [nextId, setNextId] = useState(() => Math.max(0, ...defaultVendorSpend.map(v => v.id)) + 1);

  const towerSummary = useMemo(() =>
    TOWER_NAMES.map(name => {
      const rows = vendorSpend.filter(v => v.tower === name);
      return { name, spend: rows.reduce((s, v) => s + (Number(v.annualSpend) || 0), 0), count: rows.length };
    }),
    [vendorSpend]
  );

  const visible = filter === 'All' ? vendorSpend : vendorSpend.filter(v => v.tower === filter);

  // Function: addRow
  function addRow() {
    if (!newRow.tower || !newRow.vendor || !newRow.annualSpend) return;
    const next = [...vendorSpend, { ...newRow, id: nextId, annualSpend: Number(newRow.annualSpend) }];
    setVendorSpend(next); save('vendorSpend', next);
    setNextId(p => p + 1); setNewRow(BLANK);
  }
  // Function: del
  function del(id) {
    const next = vendorSpend.filter(v => v.id !== id);
    setVendorSpend(next); save('vendorSpend', next);
  }
  // Function: reset
  function reset() {
    setVendorSpend(defaultVendorSpend); save('vendorSpend', defaultVendorSpend);
    setNextId(Math.max(0, ...defaultVendorSpend.map(v => v.id)) + 1);
  }

  return (
    <>
      {/* Tower Summary — SUMIF equivalent */}
      <div className="card" style={{ marginBottom: 16 }}>
        <div className="card-title" style={{ marginBottom: 14 }}>
          <div className="card-icon"><Activity size={14} color="#06b6d4" /></div>
          Tower Spend Aggregation (SUMIF / COUNTIF)
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(6,1fr)', gap: 10 }}>
          {towerSummary.map((t, i) => (
            <div key={t.name} style={{ background: 'rgba(255,255,255,0.025)', borderRadius: 10, padding: '12px 14px', textAlign: 'center', borderTop: `2px solid ${PALETTE[i % PALETTE.length]}` }}>
              <div style={{ fontSize: 17, fontWeight: 900, color: PALETTE[i % PALETTE.length] }}>{fmtM(t.spend)}</div>
              <div style={{ fontSize: 9.5, color: '#64748b', marginTop: 3, textTransform: 'uppercase', letterSpacing: '0.07em' }}>
                {t.name.split(' / ')[0].replace('Cross-Tower ', 'X-Tower ')}
              </div>
              <div style={{ fontSize: 11, color: '#475569', marginTop: 2 }}>{t.count} vendors</div>
            </div>
          ))}
        </div>
      </div>

      {/* Vendor Table */}
      <div className="card">
        <div className="action-bar">
          <div className="card-title" style={{ margin: 0, flex: 1 }}>
            <div className="card-icon"><Database size={14} color="#06b6d4" /></div>
            Vendor Spend Register
          </div>
          <select className="inp inp-sm" style={{ width: 190 }} value={filter} onChange={e => setFilter(e.target.value)}>
            <option value="All">All Towers</option>
            {TOWER_NAMES.map(n => <option key={n} value={n}>{n}</option>)}
          </select>
          <button className="btn btn-ghost" onClick={reset}><RefreshCw size={12} />Reset</button>
        </div>
        <div className="tbl-wrap">
          <table className="tbl">
            <thead>
              <tr>
                <th style={{ width: 36 }}>#</th>
                <th>Tower</th><th>Vendor</th><th>Category</th>
                <th>Annual Spend</th><th>Contract Date</th><th style={{ width: 60 }}></th>
              </tr>
            </thead>
            <tbody>
              {visible.map((v, i) => (
                <tr key={v.id}>
                  <td style={{ color: '#334155' }}>{i + 1}</td>
                  <td><span className="badge b-cyan" style={{ fontSize: 10 }}>{v.tower.split(' / ')[0]}</span></td>
                  <td><strong>{v.vendor}</strong></td>
                  <td>{v.category}</td>
                  <td className="hi">{fmtM(v.annualSpend)}</td>
                  <td style={{ color: '#64748b' }}>{v.contractDate}</td>
                  <td><button className="btn btn-danger" onClick={() => del(v.id)}><Trash2 size={12} /></button></td>
                </tr>
              ))}
              {/* Add row */}
              <tr style={{ background: 'rgba(6,182,212,0.02)' }}>
                <td style={{ color: '#334155' }}>+</td>
                <td>
                  <select className="inp inp-sm" value={newRow.tower} onChange={e => setNewRow(p => ({ ...p, tower: e.target.value }))}>
                    <option value="">Tower…</option>
                    {TOWER_NAMES.map(n => <option key={n} value={n}>{n}</option>)}
                  </select>
                </td>
                <td><input className="inp inp-sm" placeholder="Vendor name" value={newRow.vendor} onChange={e => setNewRow(p => ({ ...p, vendor: e.target.value }))} /></td>
                <td><input className="inp inp-sm" placeholder="Category" value={newRow.category} onChange={e => setNewRow(p => ({ ...p, category: e.target.value }))} /></td>
                <td>
                  <input className="inp inp-sm" type="number" placeholder="0.00" min="0" step="0.1"
                    value={newRow.annualSpend} style={{ width: 80 }}
                    onChange={e => setNewRow(p => ({ ...p, annualSpend: e.target.value }))} />
                </td>
                <td>
                  <input className="inp inp-sm" placeholder="YYYY-MM" style={{ width: 90 }}
                    value={newRow.contractDate}
                    onChange={e => setNewRow(p => ({ ...p, contractDate: e.target.value }))} />
                </td>
                <td>
                  <button className="btn btn-primary" onClick={addRow} style={{ padding: '5px 10px' }}>
                    <Plus size={13} />Add
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <p className="text-muted" style={{ marginTop: 10 }}>
          Showing {visible.length} of {vendorSpend.length} rows. Tower totals update live across Dashboard, Studio, and Summary.
        </p>
      </div>
    </>
  );
}

// ══════════════════════════════════════════════════════════════════════════
// Section 4 — Tower Consolidation Studio
// ══════════════════════════════════════════════════════════════════════════
// Function: TowerConsolidationStudio
function TowerConsolidationStudio({ towers, setTowers, towerOutputs }) {
  // Function: update
  function update(id, field, val) {
    const next = towers.map(t =>
      t.id === id ? { ...t, [field]: field === 'consolidationScopePct' ? Number(val) / 100 : val } : t
    );
    setTowers(next); save('towers', next);
  }
  // Function: reset
  function reset() { setTowers(defaultTowers); save('towers', defaultTowers); }

  const foot = {
    currentSpend:        towerOutputs.reduce((s, t) => s + t.currentSpend, 0),
    vendorCount:         towerOutputs.reduce((s, t) => s + t.vendorCount, 0),
    addressableSpend:    towerOutputs.reduce((s, t) => s + t.addressableSpend, 0),
    efficiencySavings:   towerOutputs.reduce((s, t) => s + t.efficiencySavings, 0),
    rateSavings:         towerOutputs.reduce((s, t) => s + t.rateSavings, 0),
    vendorMgmtSavings:   towerOutputs.reduce((s, t) => s + t.vendorMgmtSavings, 0),
    grossAnnualCapacity: towerOutputs.reduce((s, t) => s + t.grossAnnualCapacity, 0),
    transitionCost:      towerOutputs.reduce((s, t) => s + t.transitionCost, 0),
    netYear1Capacity:    towerOutputs.reduce((s, t) => s + t.netYear1Capacity, 0),
  };

  return (
    <div className="card">
      <div className="action-bar">
        <div className="card-title" style={{ margin: 0, flex: 1 }}>
          <div className="card-icon"><Building2 size={14} color="#f59e0b" /></div>
          Tower Consolidation Model — Full Calculation Chain
        </div>
        <button className="btn btn-ghost" onClick={reset}><RefreshCw size={12} />Reset Scopes</button>
      </div>
      <div className="tbl-wrap">
        <table className="tbl">
          <thead>
            <tr>
              <th>Tower</th><th>Action</th><th>Scope %</th>
              <th>Current Spend</th><th>Vendors</th><th>Addressable</th>
              <th>Efficiency</th><th>Rate</th><th>VM Savings</th>
              <th>Gross Capacity</th><th>Transition</th><th>Net Year 1</th>
            </tr>
          </thead>
          <tbody>
            {towerOutputs.map(t => (
              <tr key={t.id}>
                <td><strong>{t.name}</strong></td>
                <td>
                  <select className="inp inp-sm" style={{ width: 115 }} value={t.action}
                    onChange={e => update(t.id, 'action', e.target.value)}>
                    {ACTION_OPTIONS.map(a => <option key={a} value={a}>{a}</option>)}
                  </select>
                </td>
                <td>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
                    <input type="number" min="0" max="100" step="5" className="inp inp-sm"
                      style={{ width: 58 }}
                      value={Math.round(t.consolidationScopePct * 100)}
                      onChange={e => update(t.id, 'consolidationScopePct', e.target.value)} />
                    <span style={{ color: '#64748b', fontSize: 12 }}>%</span>
                  </div>
                </td>
                <td className="hi">{fmtM(t.currentSpend)}</td>
                <td>{t.vendorCount}</td>
                <td className="hi">{fmtM(t.addressableSpend)}</td>
                <td className="pos">{fmtM(t.efficiencySavings)}</td>
                <td className="pos">{fmtM(t.rateSavings)}</td>
                <td className="pos">{fmtM(t.vendorMgmtSavings)}</td>
                <td style={{ color: '#22d3ee', fontWeight: 700 }}>{fmtM(t.grossAnnualCapacity)}</td>
                <td className="neg">{fmtM(t.transitionCost)}</td>
                <td className="pos">{fmtM(t.netYear1Capacity)}</td>
              </tr>
            ))}
          </tbody>
          <tfoot>
            <tr style={{ borderTop: '1px solid rgba(6,182,212,0.2)' }}>
              <td colSpan={3}><strong style={{ color: '#f1f5f9' }}>TOTAL</strong></td>
              <td className="hi"><strong>{fmtM(foot.currentSpend)}</strong></td>
              <td><strong>{foot.vendorCount}</strong></td>
              <td className="hi"><strong>{fmtM(foot.addressableSpend)}</strong></td>
              <td className="pos"><strong>{fmtM(foot.efficiencySavings)}</strong></td>
              <td className="pos"><strong>{fmtM(foot.rateSavings)}</strong></td>
              <td className="pos"><strong>{fmtM(foot.vendorMgmtSavings)}</strong></td>
              <td style={{ color: '#22d3ee', fontWeight: 800 }}>{fmtM(foot.grossAnnualCapacity)}</td>
              <td className="neg"><strong>{fmtM(foot.transitionCost)}</strong></td>
              <td className="pos"><strong>{fmtM(foot.netYear1Capacity)}</strong></td>
            </tr>
          </tfoot>
        </table>
      </div>
    </div>
  );
}

// ══════════════════════════════════════════════════════════════════════════
// Section 5 — Savings / Capacity Summary
// ══════════════════════════════════════════════════════════════════════════
// Function: SavingsCapacitySummary
function SavingsCapacitySummary({ totals }) {
  const strip = [
    { label: 'Total Current Spend',   value: fmtM(totals.currentSpend),        color: '#3b82f6' },
    { label: 'Addressable Spend',     value: fmtM(totals.addressableSpend),    color: '#0891b2' },
    { label: 'Gross Annual Capacity', value: fmtM(totals.grossAnnualCapacity), color: '#22d3ee' },
    { label: 'Transition Cost',       value: fmtM(totals.transitionCost),      color: '#f43f5e' },
    { label: 'Net Year-1 Capacity',   value: fmtM(totals.netYear1Capacity),    color: '#10b981' },
  ];

  const compareData = [
    { name: 'Current Spend',   value: fixedNum(totals.currentSpend),        fill: '#3b82f6' },
    { name: 'Addressable',     value: fixedNum(totals.addressableSpend),    fill: '#0891b2' },
    { name: 'Gross Capacity',  value: fixedNum(totals.grossAnnualCapacity), fill: '#22d3ee' },
    { name: 'Net Year 1',      value: fixedNum(totals.netYear1Capacity),    fill: '#10b981' },
  ];

  const leverData = [
    { name: 'Efficiency Savings', value: fixedNum(totals.efficiencySavings), fill: '#10b981' },
    { name: 'Rate Savings',       value: fixedNum(totals.rateSavings),       fill: '#06b6d4' },
    { name: 'Vendor Mgmt',        value: fixedNum(totals.vendorMgmtSavings), fill: '#6366f1' },
    { name: 'Transition Cost',    value: fixedNum(totals.transitionCost),    fill: '#f43f5e' },
  ];

  return (
    <>
      <div className="summary-strip" style={{ gridTemplateColumns: 'repeat(5,1fr)', marginBottom: 20 }}>
        {strip.map(c => (
          <div key={c.label} className="s-cell" style={{ borderTop: `2px solid ${c.color}` }}>
            <div className="s-value" style={{ color: c.color }}>{c.value}</div>
            <div className="s-label">{c.label}</div>
          </div>
        ))}
      </div>
      <div className="g-2">
        <div className="card">
          <div className="card-title"><div className="card-icon"><BarChart3 size={14} color="#06b6d4" /></div>Spend vs Capacity Comparison</div>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={compareData} barCategoryGap="40%">
              <CartesianGrid strokeDasharray="3 3" stroke={CHART_GRID} vertical={false} />
              <XAxis dataKey="name" tick={TICK} axisLine={AXIS_LINE} tickLine={false} />
              <YAxis tick={TICK} axisLine={false} tickLine={false} tickFormatter={v => `$${v}M`} />
              <Tooltip content={<DarkTip />} cursor={{ fill: 'rgba(255,255,255,0.03)' }} />
              <Bar dataKey="value" name="Value" radius={[4, 4, 0, 0]}>
                {compareData.map((e, i) => <Cell key={i} fill={e.fill} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="card">
          <div className="card-title"><div className="card-icon"><TrendingUp size={14} color="#10b981" /></div>Savings Lever Breakdown</div>
          <ResponsiveContainer width="100%" height={180}>
            <BarChart data={leverData} barCategoryGap="35%">
              <CartesianGrid strokeDasharray="3 3" stroke={CHART_GRID} vertical={false} />
              <XAxis dataKey="name" tick={{ fill: '#475569', fontSize: 10 }} axisLine={AXIS_LINE} tickLine={false} />
              <YAxis tick={TICK} axisLine={false} tickLine={false} tickFormatter={v => `$${v}M`} />
              <Tooltip content={<DarkTip />} cursor={{ fill: 'rgba(255,255,255,0.03)' }} />
              <Bar dataKey="value" name="Value ($M)" radius={[4, 4, 0, 0]}>
                {leverData.map((e, i) => <Cell key={i} fill={e.fill} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
          <div style={{ marginTop: 12, padding: '12px 14px', background: 'rgba(255,255,255,0.025)', borderRadius: 10 }}>
            {leverData.slice(0, 3).map(l => (
              <div key={l.name} style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
                <span style={{ color: l.fill, fontSize: 12, fontWeight: 600 }}>{l.name}</span>
                <span style={{ color: l.fill, fontSize: 13, fontWeight: 900 }}>{fmtM(l.value)}</span>
              </div>
            ))}
            <div style={{ borderTop: '1px solid rgba(148,163,184,0.08)', paddingTop: 8, marginTop: 4, display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: '#f87171', fontSize: 12 }}>Transition Cost (deducted)</span>
              <span style={{ color: '#f87171', fontWeight: 900 }}>−{fmtM(totals.transitionCost)}</span>
            </div>
            <div style={{ borderTop: '1px solid rgba(6,182,212,0.2)', paddingTop: 8, marginTop: 4, display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: '#22d3ee', fontSize: 13, fontWeight: 700 }}>Net Year-1 Capacity</span>
              <span style={{ color: '#22d3ee', fontSize: 16, fontWeight: 900 }}>{fmtM(totals.netYear1Capacity)}</span>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

// ══════════════════════════════════════════════════════════════════════════
// Section 6 — Transformation Capacity Engine
// ══════════════════════════════════════════════════════════════════════════
// Function: TransformationCapacityEngine
function TransformationCapacityEngine({ reinvestment, setReinvestment, totals }) {
  const pool = totals.netYear1Capacity;
  const totalAlloc = reinvestment.reduce((s, r) => s + r.allocationPct, 0);
  const isBalanced = Math.abs(totalAlloc - 1) < 0.001;

  const withFunding = useMemo(() => calculateReinvestment(reinvestment, pool), [reinvestment, pool]);

  const pieData = withFunding.map((r, i) => ({
    name: r.area.split(' / ')[0],
    value: fixedNum(r.fundingAmount),
    fill: PALETTE[i % PALETTE.length],
  }));

  // Function: updateAlloc
  function updateAlloc(id, pct) {
    const next = reinvestment.map(r => r.id === id ? { ...r, allocationPct: Number(pct) / 100 } : r);
    setReinvestment(next); save('reinvestment', next);
  }
  // Function: reset
  function reset() { setReinvestment(defaultReinvestment); save('reinvestment', defaultReinvestment); }

  return (
    <div className="g-21" style={{ alignItems: 'start' }}>
      <div className="card">
        <div className="card-hdr">
          <div className="card-title"><div className="card-icon"><Zap size={14} color="#f59e0b" /></div>Reinvestment Allocation</div>
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: 22, fontWeight: 900, color: '#10b981' }}>{fmtM(pool)}</div>
            <div style={{ fontSize: 11, color: '#475569' }}>Net Year-1 Pool</div>
          </div>
        </div>

        {!isBalanced && (
          <div style={{ display: 'flex', gap: 8, padding: '10px 14px', background: 'rgba(245,158,11,0.07)', border: '1px solid rgba(245,158,11,0.18)', borderRadius: 10, marginBottom: 14, fontSize: 12.5, color: '#fbbf24', alignItems: 'center' }}>
            <AlertTriangle size={15} />
            Allocation is {fmtPct1(totalAlloc)} — must sum to 100%. Adjust levers below.
          </div>
        )}

        <div className="tbl-wrap">
          <table className="tbl">
            <thead>
              <tr><th>Strategic Area</th><th>Allocation %</th><th>Funding ($M)</th></tr>
            </thead>
            <tbody>
              {withFunding.map((r, i) => (
                <tr key={r.id}>
                  <td><strong style={{ color: PALETTE[i % PALETTE.length] }}>{r.area}</strong></td>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <input type="range" min="0" max="100" step="5"
                        value={Math.round(r.allocationPct * 100)}
                        onChange={e => updateAlloc(r.id, e.target.value)}
                        style={{ width: 100, accentColor: PALETTE[i % PALETTE.length] }} />
                      <span style={{ color: PALETTE[i % PALETTE.length], fontWeight: 800, minWidth: 38, textAlign: 'right' }}>
                        {Math.round(r.allocationPct * 100)}%
                      </span>
                    </div>
                  </td>
                  <td style={{ color: PALETTE[i % PALETTE.length], fontWeight: 800 }}>{fmtM(r.fundingAmount)}</td>
                </tr>
              ))}
            </tbody>
            <tfoot>
              <tr>
                <td style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <strong>TOTAL</strong>
                  <button className="btn btn-ghost" style={{ padding: '3px 8px', fontSize: 11 }} onClick={reset}><RefreshCw size={11} />Reset</button>
                </td>
                <td><strong style={{ color: isBalanced ? '#34d399' : '#fbbf24' }}>{fmtPct1(totalAlloc)}</strong></td>
                <td><strong style={{ color: '#22d3ee' }}>{fmtM(withFunding.reduce((s, r) => s + r.fundingAmount, 0))}</strong></td>
              </tr>
            </tfoot>
          </table>
        </div>
      </div>

      <div className="card">
        <div className="card-title"><div className="card-icon"><Zap size={14} color="#a855f7" /></div>Capacity Allocation Mix</div>
        <ResponsiveContainer width="100%" height={200}>
          <PieChart>
            <Pie data={pieData} cx="50%" cy="50%" outerRadius={80} dataKey="value" nameKey="name"
              label={({ percent }) => `${(num(percent) * 100).toFixed(0)}%`} labelLine={false}>
              {pieData.map((e, i) => <Cell key={i} fill={e.fill} />)}
            </Pie>
            <Tooltip content={<DarkTip />} />
          </PieChart>
        </ResponsiveContainer>
        <div style={{ marginTop: 8 }}>
          {pieData.map((p, i) => (
            <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
              <div style={{ width: 10, height: 10, borderRadius: 3, background: p.fill, flexShrink: 0 }} />
              <span style={{ fontSize: 12, color: '#94a3b8', flex: 1 }}>{p.name}</span>
              <span style={{ fontSize: 13, fontWeight: 700, color: p.fill }}>{fmtM(p.value)}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// ══════════════════════════════════════════════════════════════════════════
// Section 7 — Transition Roadmap
// ══════════════════════════════════════════════════════════════════════════
// Function: TransitionRoadmap
function TransitionRoadmap({ roadmap, setRoadmap }) {
  // Function: updStatus
  function updStatus(id, status) {
    const next = roadmap.map(r => r.id === id ? { ...r, status } : r);
    setRoadmap(next); save('roadmap', next);
  }
  // Function: updOwner
  function updOwner(id, owner) {
    const next = roadmap.map(r => r.id === id ? { ...r, owner } : r);
    setRoadmap(next); save('roadmap', next);
  }
  // Function: reset
  function reset() { setRoadmap(defaultRoadmap); save('roadmap', defaultRoadmap); }

  const counts = {
    complete:   roadmap.filter(r => r.status === 'Complete').length,
    inProgress: roadmap.filter(r => r.status === 'In Progress').length,
    atRisk:     roadmap.filter(r => r.status === 'At Risk').length,
    pending:    roadmap.filter(r => r.status === 'Pending').length,
  };

  return (
    <div className="card">
      <div className="card-hdr">
        <div className="card-title"><div className="card-icon"><Map size={14} color="#a855f7" /></div>Transition Roadmap</div>
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
          <span className="badge b-emerald">{counts.complete} Complete</span>
          <span className="badge b-cyan">{counts.inProgress} In Progress</span>
          {counts.atRisk > 0 && <span className="badge b-rose">{counts.atRisk} At Risk</span>}
          <span className="badge b-slate">{counts.pending} Pending</span>
          <button className="btn btn-ghost" style={{ padding: '3px 9px', fontSize: 11 }} onClick={reset}><RefreshCw size={11} /></button>
        </div>
      </div>
      <div style={{ overflowX: 'auto' }}>
        {roadmap.map((r, idx) => (
          <div key={r.id} className="roadmap-row">
            <div>
              <div className="horizon-label">{r.horizon}</div>
              <div style={{ fontSize: 10, color: '#334155', marginTop: 2 }}>Wave {idx + 1}</div>
            </div>
            <div>
              <div style={{ fontSize: 13, fontWeight: 700, color: '#f1f5f9', marginBottom: 6 }}>{r.milestone}</div>
              <StatusBadge status={r.status} />
            </div>
            <div style={{ fontSize: 12, color: '#94a3b8', lineHeight: 1.6 }}>{r.actions}</div>
            <div>
              <input className="inp inp-sm" value={r.owner} placeholder="Owner"
                onChange={e => updOwner(r.id, e.target.value)} />
            </div>
            <div>
              <select className="inp inp-sm" value={r.status} onChange={e => updStatus(r.id, e.target.value)}>
                {STATUS_OPTIONS.map(s => <option key={s} value={s}>{s}</option>)}
              </select>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// ══════════════════════════════════════════════════════════════════════════
// Sidebar
// ══════════════════════════════════════════════════════════════════════════
// Function: Sidebar
function Sidebar({ active, setActive }) {
  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="brand-row">
          <div className="brand-icon">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
            </svg>
          </div>
          <span className="brand-name">TowerIQ</span>
        </div>
        <div className="brand-sub">IT Consolidation Studio</div>
      </div>
      <nav className="nav">
        <div className="nav-section">Modules</div>
        {SECTIONS.map(s => (
          <button key={s.id} className={`nav-btn ${active === s.id ? 'active' : ''}`}
            onClick={() => setActive(s.id)}>
            <s.Icon size={15} style={{ flexShrink: 0, opacity: active === s.id ? 1 : 0.65 }} />
            {s.label}
            {active === s.id && <ChevronRight size={13} style={{ marginLeft: 'auto' }} />}
          </button>
        ))}
      </nav>
      <div className="sidebar-foot">
        <div>StratIQ · Data Analysis Studio</div>
        <div style={{ color: '#1e293b', marginTop: 4 }}>All data stored locally</div>
      </div>
    </aside>
  );
}

// ══════════════════════════════════════════════════════════════════════════
// App root
// ══════════════════════════════════════════════════════════════════════════
// Function: App
function App() {
  const [portalUser, setPortalUser] = useState(() => decodePortalUser(getPortalToken()));

  useEffect(() => {
    consumePortalTokenFromHash();
    setPortalUser(decodePortalUser(getPortalToken()));
  }, []);

  const [active,       setActive]      = useState('dashboard');
  const [assumptions,  setAssumptions] = useState(() => mergeObjectFallback(load('assumptions', defaultAssumptions), defaultAssumptions));
  const [vendorSpend,  setVendorSpend] = useState(() => mergeListFallback(load('vendorSpend', defaultVendorSpend), defaultVendorSpend));
  const [towers,       setTowers]      = useState(() => mergeListFallback(load('towers', defaultTowers), defaultTowers));
  const [reinvestment, setReinvestment]= useState(() => mergeListFallback(load('reinvestment', defaultReinvestment), defaultReinvestment));
  const [roadmap,      setRoadmap]     = useState(() => mergeListFallback(load('roadmap', defaultRoadmap), defaultRoadmap));

  const towerOutputs = useMemo(
    () => towers.map(t => calculateTowerOutput(t, vendorSpend, assumptions)),
    [towers, vendorSpend, assumptions]
  );
  const totals = useMemo(() => calculateScenarioTotals(towerOutputs), [towerOutputs]);

  const meta = SECTION_META[active] || {};

  // Function: renderPage
  function renderPage() {
    switch (active) {
      case 'dashboard':    return <ExecutiveDashboard towerOutputs={towerOutputs} totals={totals} />;
      case 'inputs':       return <AssumptionManager assumptions={assumptions} setAssumptions={setAssumptions} towerOutputs={towerOutputs} />;
      case 'vendor-spend': return <VendorSpendEntry vendorSpend={vendorSpend} setVendorSpend={setVendorSpend} />;
      case 'tower-studio': return <TowerConsolidationStudio towers={towers} setTowers={setTowers} towerOutputs={towerOutputs} />;
      case 'savings':      return <SavingsCapacitySummary totals={totals} />;
      case 'reinvest':     return <TransformationCapacityEngine reinvestment={reinvestment} setReinvestment={setReinvestment} totals={totals} />;
      case 'roadmap':      return <TransitionRoadmap roadmap={roadmap} setRoadmap={setRoadmap} />;
      default:             return null;
    }
  }

  return (
    <div className="app">
      <Sidebar active={active} setActive={setActive} />
      <main>
        <div className="topbar">
          <div>
            <div className="topbar-eyebrow">Unified Modernization Suite</div>
            <div className="topbar-title">{meta.title}</div>
            <div className="topbar-sub">{meta.sub}</div>
          </div>
          <div className="topbar-actions">
            <div className="topbar-chip">Net Yr-1 Capacity: {fmtM(totals.netYear1Capacity)}</div>
            {portalUser?.username && <span className="topbar-user">{portalUser.username}</span>}
            <button type="button" className="topbar-btn" onClick={() => { window.location.href = getPortalHomeUrl(); }}>Portal Home</button>
            {portalUser?.role === 'admin' && (
              <button type="button" className="topbar-btn" onClick={() => { window.location.href = getPortalAdminUrl(); }}>Admin Console</button>
            )}
            <button type="button" className="topbar-btn" onClick={logoutFromPortal}>Logout</button>
          </div>
        </div>
        <div className="page">{renderPage()}</div>
      </main>
    </div>
  );
}

createRoot(document.getElementById('root')).render(<App />);
