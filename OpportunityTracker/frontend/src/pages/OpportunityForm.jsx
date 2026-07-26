// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: OpportunityTracker — frontend/src/pages (OpportunityForm.jsx)
// Date: 2025-07-22
// ---------------------------------------------------------------------------
import React, { useState } from 'react';
import { Plus, X, ChevronDown, DollarSign } from 'lucide-react';
import toast from 'react-hot-toast';
import api from '../services/api';
import { STAGES } from '../constants/stages';

const VALIDATION = ['Yes', 'No', 'Pending'];
// Matches the real casing used in the imported FY27 Plan Tracker data
// (Americas/Europe/APJ) — kept consistent so the region breakdown never
// silently fragments into duplicate buckets differing only by case.
const REGIONS = ['Americas', 'Europe', 'APJ', 'MEA', 'Global'];
const SUB_VERTICALS = ['Automotive', 'Industrial Manufacturing', 'Process Manufacturing', 'A&D', 'Aero & Defense', 'Hi-Tech', 'Energy & Utilities', 'Other'];
const HYPERSCALERS = ['AWS', 'Azure', 'GCP', 'Multi-Cloud', 'None', 'Other'];

const EMPTY = {
  region: '', customer_group: '', sub_vertical: '', solution_offering: '',
  so_coe_leader: '', crm_ref: '', opportunity_name: '', oppty_stage: '',
  start_date: '', oppty_owner: '', tcv_mn: '', q1_mn: '', q2_mn: '', q3_mn: '', q4_mn: '',
  remarks: '', hyperscaler: '', delivery_ibu: '', delivery_ibu_leader: '', delivery_validation: 'No',
};

// Function: Field
function Field({ label, children, required }) {
  return (
    <div>
      <label className="ot-label">{label}{required && <span className="text-red-400 ml-0.5">*</span>}</label>
      {children}
    </div>
  );
}

// Function: Input
function Input({ ...props }) {
  return <input className="ot-input" {...props} />;
}

// Function: Select
function Select({ options, ...props }) {
  return (
    <div className="relative">
      <select className="ot-select pr-8" {...props}>
        <option value="">— Select —</option>
        {options.map((o) => <option key={o} value={o}>{o}</option>)}
      </select>
      <ChevronDown size={14} className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 pointer-events-none" />
    </div>
  );
}

// Function: OpportunityForm
export default function OpportunityForm({ onCreated }) {
  const [form, setForm] = useState(EMPTY);
  const [loading, setLoading] = useState(false);

  // Function: set
  const set = (k, v) => setForm((f) => ({ ...f, [k]: v }));
  const fy27 = [form.q1_mn, form.q2_mn, form.q3_mn, form.q4_mn].reduce((s, v) => s + (parseFloat(v) || 0), 0);

  // Function: submit
  const submit = async (e) => {
    e.preventDefault();
    if (!form.opportunity_name.trim()) { toast.error('Opportunity Name is required.'); return; }
    setLoading(true);
    try {
      const payload = {
        ...form,
        tcv_mn: parseFloat(form.tcv_mn) || 0,
        q1_mn: parseFloat(form.q1_mn) || 0,
        q2_mn: parseFloat(form.q2_mn) || 0,
        q3_mn: parseFloat(form.q3_mn) || 0,
        q4_mn: parseFloat(form.q4_mn) || 0,
      };
      const { data } = await api.post('opportunities', payload);
      toast.success('Opportunity created successfully.');
      setForm(EMPTY);
      onCreated?.(data);
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Failed to create opportunity.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={submit} className="space-y-8">

      {/* Section 1 — Account & Opportunity */}
      <div className="ot-card p-6 space-y-5">
        <h3 className="text-sm font-bold uppercase tracking-wider text-cyan-400 flex items-center gap-2">
          <span className="h-5 w-5 rounded-md bg-cyan-500/20 flex items-center justify-center text-[11px]">1</span>
          Account &amp; Opportunity Info
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          <Field label="Region">
            <Select options={REGIONS} value={form.region} onChange={(e) => set('region', e.target.value)} />
          </Field>
          <Field label="Customer Group">
            <Input value={form.customer_group} onChange={(e) => set('customer_group', e.target.value)} placeholder="e.g. Ford Motor Company" />
          </Field>
          <Field label="Sub Vertical">
            <Select options={SUB_VERTICALS} value={form.sub_vertical} onChange={(e) => set('sub_vertical', e.target.value)} />
          </Field>
          <Field label="Opportunity Name" required>
            <Input value={form.opportunity_name} onChange={(e) => set('opportunity_name', e.target.value)} placeholder="Opportunity title" required />
          </Field>
          <Field label="CRM Ref #">
            <Input value={form.crm_ref} onChange={(e) => set('crm_ref', e.target.value)} placeholder="CRM-2027-XXXXX" />
          </Field>
          <Field label="Opportunity Stage">
            <Select options={STAGES} value={form.oppty_stage} onChange={(e) => set('oppty_stage', e.target.value)} />
          </Field>
          <Field label="Start Date">
            <Input type="date" value={form.start_date} onChange={(e) => set('start_date', e.target.value)} />
          </Field>
          <Field label="Opportunity Owner">
            <Input value={form.oppty_owner} onChange={(e) => set('oppty_owner', e.target.value)} placeholder="Owner name" />
          </Field>
        </div>
      </div>

      {/* Section 2 — Solution & Leadership */}
      <div className="ot-card p-6 space-y-5">
        <h3 className="text-sm font-bold uppercase tracking-wider text-violet-400 flex items-center gap-2">
          <span className="h-5 w-5 rounded-md bg-violet-500/20 flex items-center justify-center text-[11px]">2</span>
          Solution &amp; Delivery
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          <Field label="Solution / Offering">
            <Input value={form.solution_offering} onChange={(e) => set('solution_offering', e.target.value)} placeholder="e.g. Cloud Migration, AIOps" />
          </Field>
          <Field label="SO / COE Leader">
            <Input value={form.so_coe_leader} onChange={(e) => set('so_coe_leader', e.target.value)} placeholder="Leader name" />
          </Field>
          <Field label="Hyperscaler">
            <Select options={HYPERSCALERS} value={form.hyperscaler} onChange={(e) => set('hyperscaler', e.target.value)} />
          </Field>
          <Field label="Delivery IBU">
            <Input value={form.delivery_ibu} onChange={(e) => set('delivery_ibu', e.target.value)} placeholder="e.g. ESV / SISWEF" />
          </Field>
          <Field label="Delivery IBU Leader">
            <Input value={form.delivery_ibu_leader} onChange={(e) => set('delivery_ibu_leader', e.target.value)} placeholder="IBU Leader name" />
          </Field>
          <Field label="Delivery Validation">
            <Select options={VALIDATION} value={form.delivery_validation} onChange={(e) => set('delivery_validation', e.target.value)} />
          </Field>
        </div>
      </div>

      {/* Section 3 — Commercial Values */}
      <div className="ot-card p-6 space-y-5">
        <h3 className="text-sm font-bold uppercase tracking-wider text-emerald-400 flex items-center gap-2">
          <span className="h-5 w-5 rounded-md bg-emerald-500/20 flex items-center justify-center text-[11px]">3</span>
          Commercial Values <span className="text-slate-500 font-normal normal-case tracking-normal text-xs">($ Mn)</span>
        </h3>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-5">
          {[
            { key: 'tcv_mn', label: 'TCV $ Mn' },
            { key: 'q1_mn', label: "Q1'27 $ Mn" },
            { key: 'q2_mn', label: "Q2'27 $ Mn" },
            { key: 'q3_mn', label: "Q3'27 $ Mn" },
            { key: 'q4_mn', label: "Q4'27 $ Mn" },
          ].map(({ key, label }) => (
            <Field key={key} label={label}>
              <div className="relative">
                <DollarSign size={12} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
                <Input
                  type="number"
                  min="0"
                  step="0.01"
                  className="ot-input pl-6"
                  value={form[key]}
                  onChange={(e) => set(key, e.target.value)}
                  placeholder="0.00"
                />
              </div>
            </Field>
          ))}
          <Field label="FY'27 $ Mn (Auto)">
            <div className="ot-input bg-slate-900/50 text-cyan-300 font-bold cursor-not-allowed flex items-center gap-1">
              <DollarSign size={12} className="text-slate-500" />
              {fy27.toFixed(2)}
            </div>
          </Field>
        </div>
      </div>

      {/* Section 4 — Remarks */}
      <div className="ot-card p-6 space-y-4">
        <h3 className="text-sm font-bold uppercase tracking-wider text-amber-400 flex items-center gap-2">
          <span className="h-5 w-5 rounded-md bg-amber-500/20 flex items-center justify-center text-[11px]">4</span>
          Remarks
        </h3>
        <textarea
          className="ot-input resize-none h-24"
          value={form.remarks}
          onChange={(e) => set('remarks', e.target.value)}
          placeholder="Notes, context, next steps…"
        />
      </div>

      {/* Actions */}
      <div className="flex items-center justify-end gap-3 pt-2">
        <button type="button" onClick={() => setForm(EMPTY)} className="ot-btn-secondary">
          <X size={15} /> Clear Form
        </button>
        <button type="submit" disabled={loading} className="ot-btn-primary px-6 py-2.5">
          {loading ? <span className="w-4 h-4 rounded-full border-2 border-white border-t-transparent animate-spin" /> : <Plus size={15} />}
          {loading ? 'Saving…' : 'Save Opportunity'}
        </button>
      </div>
    </form>
  );
}
