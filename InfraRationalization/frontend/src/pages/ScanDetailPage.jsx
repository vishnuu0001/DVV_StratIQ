// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: InfraRationalization — frontend/src/pages (ScanDetailPage.jsx)
// Date: 2026-03-15
// ---------------------------------------------------------------------------
import { useState, useEffect, Fragment } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  BarChart, Bar, PieChart, Pie, Cell, Tooltip, Legend,
  ResponsiveContainer, XAxis, YAxis, CartesianGrid,
} from 'recharts'
import {
  Download, Server, ChevronDown, ChevronUp, ChevronRight,
  Leaf, Package, AlertTriangle, Network, Shield, Trash2, Brain,
  DollarSign, GitMerge, ShieldAlert, Wrench, Cpu, Activity,
  FileSpreadsheet, FileText, Presentation, TableProperties, Code2,
} from 'lucide-react'
import toast from 'react-hot-toast'
import {
  getScan, getScanReport,
  getTcoAnalysis, getDependencyMap, getSecurityAnalysis,
  getDecommissionCandidates, getHypervisorAnalysis, getBcdrAnalysis,
  downloadExport, downloadIac,
} from '../api/client.js'
import AppHeader from '../components/AppHeader.jsx'
import ChatPanel from '../components/ChatPanel.jsx'

// ””€ Helpers ””””””””””””””””””””””””””””””””””””””””””””””””””””””””””””””””””€

const MIGRATION_LABELS = {
  lift_and_shift:      'Lift & Shift',
  smart_shift:         'Smart Shift',
  smart_shift_effort:  'Smart Shift (Effort)',
  paas:                'PaaS',
  paas_shift:          'PaaS',
  paas_effort:         'PaaS (Effort)',
  paas_shift_effort:   'PaaS (Effort)',
  decommission:        'Decommission',
}

const MIGRATION_BADGE = {
  lift_and_shift:     'bg-emerald-950/60 text-emerald-300 border-emerald-700/40',
  smart_shift:        'bg-blue-950/60 text-blue-300 border-blue-700/40',
  smart_shift_effort: 'bg-amber-950/60 text-amber-300 border-amber-700/40',
  paas:               'bg-purple-950/60 text-purple-300 border-purple-700/40',
  paas_shift:         'bg-purple-950/60 text-purple-300 border-purple-700/40',
  paas_effort:        'bg-slate-800 text-slate-300 border-slate-600/40',
  paas_shift_effort:  'bg-slate-800 text-slate-300 border-slate-600/40',
  decommission:       'bg-red-950/60 text-red-300 border-red-700/40',
}

const CHART_TOOLTIP_STYLE = {
  background: '#1a1d26',
  border: '1px solid #2a2d3e',
  borderRadius: '8px',
  color: '#e2e8f0',
  fontSize: '12px',
}

/**
 * Build old-style summary from cloud_assessment (new scanner format).
 */
// Function: buildSummaryFromCloudAssessment
function buildSummaryFromCloudAssessment(ca) {
  return {
    total_servers: ca.total_servers || 0,
    os_count: Object.keys(ca.os_distribution || {}).length,
    storage_tb: ca.total_storage_tb || 0,
    utilization_breakdown: {
      underutilized: ca.utilization_distribution?.underutilized || ca.utilization_distribution?.unknown || 0,
      moderate:      ca.utilization_distribution?.moderate || 0,
      utilized:      ca.utilization_distribution?.utilized || 0,
    },
    server_type: Object.keys(ca.server_type_distribution || {})[0] || 'Virtual',
    boot_type:   Object.keys(ca.boot_type_distribution || {})[0] || 'BIOS',
    ip_distribution_note: `${ca.total_ram_gb || 0} GB RAM total · ${ca.total_cpu_cores || 0} vCPUs`,
    os_distribution: ca.os_distribution,
  }
}

/**
 * Normalize a single server — handle both old field names and new aliases.
 */
// Function: normalizeServerCore
function normalizeServerCore(srv) {
  return {
    ip:                 srv.ip_address || srv.server_ip,
    name:               srv.server_name,
    os:                 srv.os_name || srv.operating_system,
    cpu_cores:          srv.cpu_cores,
    ram_gb:             (srv.ram_gb != null ? srv.ram_gb : srv.memory_gb),
    disk_gb:            srv.total_storage_gb || srv.internal_storage_gb,
    utilization:        srv.utilization_band,
    migration_strategy: srv.migration_strategy,
    workloads:          (srv.workloads || []).map(w => `${w.name}${w.version ? ' ' + w.version : ''}`),
    cloud_provider:     srv.cloud_provider,
    region:             srv.region,
    instance_type:      srv.instance_type,
    interfaces:         srv.interfaces || [],
    disks:              srv.disks || [],
    workloads_raw:      srv.workloads || [],
    installed_software: srv.installed_software || [],
    cpu_util_pct:       srv.cpu_util_pct,
    ram_util_pct:       srv.ram_util_pct,
    disk_util_pct:      srv.disk_util_pct,
  }
}

// Function: normalizeServerStorageAndOs
function normalizeServerStorageAndOs(srv) {
  return {
    virtualization_state:      srv.virtualization_state || '',
    virtualization_attributes: srv.virtualization_attributes || {},
    compute_hardware_arch:     srv.compute_hardware_arch || srv.architecture || '',
    install_type:       srv.install_type || '',
    boot_type:          srv.boot_type || '',
    internal_storage_gb: srv.internal_storage_gb,
    external_storage_gb: srv.external_storage_gb,
    storage_type:       srv.storage_type || '',
    db_engine:          srv.db_engine || '',
    db_storage_gb:      srv.db_storage_gb,
    flash_storage_used: srv.flash_storage_used,
    os_family:          srv.os_family || '',
    os_version:         srv.os_version || '',
    os_end_of_support:  srv.os_end_of_support || '',
    hostname:           srv.hostname || '',
  }
}

// Function: normalizeServerNetworkAndHa
function normalizeServerNetworkAndHa(srv) {
  return {
    cloud_suitability:  srv.cloud_suitability || '',
    ha_dr_requirements: srv.ha_dr_requirements || '',
    rto_requirements:   srv.rto_requirements || '',
    rpo_requirements:   srv.rpo_requirements || '',
    arp_neighbors:      srv.arp_neighbors || [],
    routes:             srv.routes || [],
  }
}

// Function: normalizeServer
function normalizeServer(srv) {
  return {
    ...normalizeServerCore(srv),
    ...normalizeServerStorageAndOs(srv),
    ...normalizeServerNetworkAndHa(srv),
  }
}

/**
 * Normalize workload consolidation entry (new format uses 'workload' not 'workload_name' etc).
 */
// Function: normalizeWorkloadConsolidation
function normalizeWorkloadConsolidation(w) {
  return {
    cloud_name:             w.cloud_name || 'OnPrem',
    workload_name:          w.workload,
    current_server_count:   w.current_vm_count,
    no_of_workload_components: w.no_of_workload_components ?? w.current_vm_count,
    recommended_server_count: w.recommended_vm_count,
    instances:              w.instances || (w.servers || []).map(name => ({ cloud_name: w.cloud_name || 'OnPrem', server_name: name, server_ip: '', workload_name: w.workload, version: '', location: '' })),
    recommendation_note:    w.recommendation,
  }
}

// Function: normalizeEosOs
function normalizeEosOs(e) {
  return {
    server_name:            e.server_name,
    server_ip:              e.ip_address,
    os:                     e.os_name,
    end_of_support:         e.end_of_support,
    end_of_extended_support: e.extended_support,
    migration_advisory:     e.migration_advisory,
  }
}

// Function: normalizeEosWorkload
function normalizeEosWorkload(e) {
  return {
    server_name:  e.server_name,
    server_ip:    e.ip_address,
    workload:     `${e.workload} ${e.version || ''}`.trim(),
    location:     e.location || '',
    end_of_support: e.end_of_support,
    end_of_extended_support: e.extended_support || null,
  }
}

// Function: buildCloudReadiness
function buildCloudReadiness(cr) {
  return {
    cloud_ready:                 cr.cloud_ready || 0,
    cloud_ready_with_effort:     cr.cloud_ready_with_effort || 0,
    lift_and_shift:              cr.lift_and_shift || 0,
    smart_shift:                 cr.smart_shift || 0,
    smart_shift_with_effort:     cr.smart_shift_with_effort || 0,
    paas_shift:                  cr.paas_shift || 0,
    paas_shift_with_effort:      cr.paas_shift_with_effort || 0,
    decommission:                cr.decommission || 0,
  }
}

// Function: buildExtraReportSectionsA
function buildExtraReportSectionsA(s) {
  return {
    pricing_plans: s.pricing_plans || null,
    dedicated_host_capacity: s.dedicated_host_capacity?.hosts?.length > 0 ? s.dedicated_host_capacity : null,
    vmware_openstack_capacity: s.vmware_openstack_capacity || null,
    network_summary: s.network_summary || null,
    paas_recommendations: s.paas_recommendations || null,
    storage_recommendation: s.storage_recommendation || null,
    kubernetes_recommendation: s.kubernetes_recommendation || null,
    sustainability: s.sustainability ? {
      ...s.sustainability,
      per_server: s.sustainability.per_server || [],
    } : null,
  }
}

// Function: buildExtraReportSectionsB
function buildExtraReportSectionsB(s, ca, cr) {
  return {
    vm_flavors: s.vm_flavors || null,
    cloud_resources_recommendation: s.cloud_resources_recommendation || null,
    cloud_readiness_details: cr.details || [],
    network_topology: s.network_topology ? {
      ...s.network_topology,
      network_utilization: s.network_topology.network_utilization || [],
    } : null,
    workload_components: ca.workload_components || null,
    software_inventory: s.software_inventory || null,
  }
}

// Function: buildExtraReportSections
function buildExtraReportSections(s, ca, cr) {
  return {
    ...buildExtraReportSectionsA(s),
    ...buildExtraReportSectionsB(s, ca, cr),
  }
}

/**
 * Normalize scanner report (new format) OR legacy JSON upload (old format)
 * into a single unified shape for rendering.
 */
// Function: normalizeReport
function normalizeReport(raw) {
  // New scanner format has `sections` key
  if (raw.sections) {
    const s = raw.sections
    const ca = s.cloud_assessment || {}
    const cr = s.cloud_readiness || {}
    const cp = s.capacity_planning || {}

    const summary = buildSummaryFromCloudAssessment(ca)
    const servers = (raw.servers || []).map(normalizeServer)
    const wl_consolidation = (s.workload_consolidation || []).map(normalizeWorkloadConsolidation)
    const eos_os = (s.eos_advisory_os || []).map(normalizeEosOs)
    const eos_wl = (s.eos_advisory_workload || []).map(normalizeEosWorkload)

    return {
      _newFormat: true,
      report_name:     raw.report_name,
      source_environment: raw.provider || '',
      target_cloud:    '',
      region:          '',
      summary,
      cloud_readiness: buildCloudReadiness(cr),
      capacity_planning: cp,
      servers,
      workload_consolidation: wl_consolidation,
      eos_advisories: { operating_systems: eos_os, workloads: eos_wl },
      ...buildExtraReportSections(s, ca, cr),
    }
  }

  // Legacy format  return as-is (old JSON upload)
  return { _newFormat: false, ...raw }
}

// ””€ UI Components ”””””””””””””””””””””””””””””””””””””””””””””””””””””””””””””€

// Function: StatCard
function StatCard({ label, value, sub, ring = 'border-slate-700' }) {
  return (
    <div className={`glass p-5 border ${ring}`}>
      <p className="text-xs text-slate-400 uppercase tracking-wide mb-1">{label}</p>
      <p className="text-3xl font-bold text-white">{value}</p>
      {sub && <p className="text-xs text-slate-500 mt-1">{sub}</p>}
    </div>
  )
}

// Function: Section
function Section({ title, children, defaultOpen = true, icon }) {
  const [open, setOpen] = useState(defaultOpen)
  return (
    <div className="glass overflow-hidden">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between px-6 py-4 text-left hover:bg-surface-hover transition-colors"
      >
        <h3 className="font-semibold text-white flex items-center gap-2">
          {icon && <span className="text-slate-400">{icon}</span>}
          {title}
        </h3>
        {open
          ? <ChevronUp size={15} className="text-slate-500 shrink-0" />
          : <ChevronDown size={15} className="text-slate-500 shrink-0" />
        }
      </button>
      {open && <div className="px-6 pb-6">{children}</div>}
    </div>
  )
}

// Function: EOSBadge
function EOSBadge({ date }) {
  if (!date) return <span className="text-slate-600 text-xs"></span>
  const diff = Math.floor((new Date(date) - Date.now()) / 86400000)
  if (diff < 0)
    return <span className="text-xs px-2 py-0.5 rounded-full bg-red-950/60 text-red-300 border border-red-700/40">š  Expired {date}</span>
  if (diff < 365)
    return <span className="text-xs px-2 py-0.5 rounded-full bg-amber-950/60 text-amber-300 border border-amber-700/40">š¡ {date}</span>
  return <span className="text-xs text-slate-400">{date}</span>
}

// Function: SupportPeriodBadge
function SupportPeriodBadge({ status, label }) {
  if (status === 'expired')
    return <span className="inline-flex items-center gap-1 text-xs px-2 py-0.5 rounded-full bg-red-950/60 text-red-300 border border-red-700/40 whitespace-nowrap">&#x26A0; {label || 'Expired'}</span>
  if (status === 'expiring_soon')
    return <span className="inline-flex items-center gap-1 text-xs px-2 py-0.5 rounded-full bg-amber-950/60 text-amber-300 border border-amber-700/40 whitespace-nowrap">&#x26A1; {label || 'Expiring Soon'}</span>
  if (label && label !== 'No EOS data')
    return <span className="inline-flex items-center gap-1 text-xs px-2 py-0.5 rounded-full bg-emerald-950/60 text-emerald-300 border border-emerald-700/40 whitespace-nowrap">&#x2713; {label}</span>
  return <span className="text-xs text-slate-500">{label || 'No data'}</span>
}

// Function: CategoryBadge
function CategoryBadge({ cat }) {
  const map = {
    db:         'bg-blue-950/60 text-blue-300',
    runtime:    'bg-emerald-950/60 text-emerald-300',
    security:   'bg-amber-950/60 text-amber-300',
    middleware: 'bg-purple-950/60 text-purple-300',
    os:         'bg-slate-700 text-slate-200',
    utility:    'bg-cyan-950/60 text-cyan-300',
  }
  return (
    <span className={`px-1.5 py-0.5 rounded text-xs capitalize ${map[cat] || 'bg-slate-700 text-slate-400'}`}>
      {cat || 'other'}
    </span>
  )
}

// Function: SoftwareEosProgress
function SoftwareEosProgress({ item }) {
  if (!item.eos_date) return null
  return (
    <div className="p-3 rounded-lg bg-surface-hover border border-surface-border">
      <p className="text-xs text-slate-400 mb-1">Days Until End of Support</p>
      {item.is_eos
        ? <p className="text-red-300 font-bold">{Math.abs(item.days_to_eos || 0)} days overdue</p>
        : <p className="text-emerald-300 font-bold">{item.days_to_eos || 0} days remaining</p>
      }
      <div className="mt-2 h-2 rounded-full bg-slate-700 overflow-hidden">
        <div className={`h-full rounded-full ${
          item.is_eos ? 'bg-red-500' :
          item.days_to_eos <= 180 ? 'bg-amber-500' : 'bg-emerald-500'
        }`} style={{ width: `${item.is_eos ? 100 : Math.min(100, Math.max(5, (item.days_to_eos / 1095) * 100))}%` }} />
      </div>
    </div>
  )
}

// Function: SoftwareRecommendations
function SoftwareRecommendations({ status }) {
  if (status === 'expired') {
    return (
      <ul className="space-y-1 text-xs text-red-200">
        <li>&#x2022; Immediately plan upgrade or replacement of this software</li>
        <li>&#x2022; Check for known CVEs \u2014 no security patches are being released</li>
        <li>&#x2022; Evaluate vendor migration guides for upgrade path</li>
      </ul>
    )
  }
  if (status === 'expiring_soon') {
    return (
      <ul className="space-y-1 text-xs text-amber-200">
        <li>&#x2022; Schedule upgrade within the next support window</li>
        <li>&#x2022; Review release notes for the next major version</li>
        <li>&#x2022; Test compatibility in staging environment</li>
      </ul>
    )
  }
  return <p className="text-xs text-emerald-300">Software is within active support period. Monitor vendor announcements for future EOS notices.</p>
}

// Function: SoftwareDetailPanel
function SoftwareDetailPanel({ item, onClose }) {
  if (!item) return null
  const statusColor = item.validity_status === 'expired' ? 'red' :
                      item.validity_status === 'expiring_soon' ? 'amber' : 'emerald'
  return (
    <div className="fixed inset-0 z-50 flex justify-end" onClick={onClose}>
      <div className="w-full max-w-md h-full bg-[#0f1623] border-l border-surface-border shadow-2xl overflow-y-auto"
           onClick={e => e.stopPropagation()}>
        <div className="flex items-center justify-between px-5 py-4 border-b border-surface-border sticky top-0 bg-[#0f1623] z-10">
          <h3 className="font-semibold text-white text-base font-mono">{item.name}</h3>
          <button onClick={onClose} className="text-slate-400 hover:text-white text-xl leading-none">&#x00D7;</button>
        </div>
        <div className="px-5 py-5 space-y-4 text-sm">
          <div className={`p-3 rounded-lg bg-${statusColor}-950/20 border border-${statusColor}-800/30`}>
            <p className="text-xs text-slate-400 mb-1">Support Period</p>
            <SupportPeriodBadge status={item.validity_status} label={item.support_period_label} />
          </div>
          <div className="grid grid-cols-2 gap-3">
            {[
              ['Version', item.version || '\u2014'],
              ['Vendor', item.vendor || '\u2014'],
              ['Server', item.server_name || '\u2014'],
              ['Server IP', item.server_ip || '\u2014'],
              ['Install Date', item.install_date || '\u2014'],
              ['EOS Date', item.eos_date || 'Not tracked'],
              ['Category', item.category || '\u2014'],
              ['License', item.license_type || '\u2014'],
            ].map(([label, value]) => (
              <div key={label}>
                <p className="text-xs text-slate-500 mb-0.5">{label}</p>
                <p className="text-slate-200 font-mono text-xs break-all">{value}</p>
              </div>
            ))}
          </div>
          <SoftwareEosProgress item={item} />
          <div className="p-3 rounded-lg bg-surface-hover border border-surface-border">
            <p className="text-xs text-slate-400 mb-1.5">Recommendations</p>
            <SoftwareRecommendations status={item.validity_status} />
          </div>
        </div>
      </div>
    </div>
  )
}


// ””€ Main page ”””””””””””””””””””””””””””””””””””””””””””””””””””””””””””””””””€

// Function: filterSoftwareItems
function filterSoftwareItems(items, filters) {
  const { statusFilter, licenseFilter, categoryFilter, serverFilter, search } = filters
  return items.filter(sw => {
    if (statusFilter && sw.validity_status !== statusFilter) return false
    if (licenseFilter && sw.license_type !== licenseFilter) return false
    if (categoryFilter && sw.category !== categoryFilter) return false
    if (serverFilter && sw.server_ip !== serverFilter) return false
    if (search) {
      const q = search.toLowerCase()
      if (!sw.name?.toLowerCase().includes(q) &&
          !sw.vendor?.toLowerCase().includes(q) &&
          !sw.server_name?.toLowerCase().includes(q) &&
          !sw.version?.toLowerCase().includes(q)) return false
    }
    return true
  })
}

// Function: sortSoftwareItems
function sortSoftwareItems(items, sortKey, sortDir) {
  return [...items].sort((a, b) => {
    let av = a[sortKey] ?? '', bv = b[sortKey] ?? ''
    if (typeof av === 'boolean') av = av ? 0 : 1
    if (typeof bv === 'boolean') bv = bv ? 0 : 1
    const cmp = String(av).localeCompare(String(bv), undefined, { numeric: true })
    return sortDir === 'asc' ? cmp : -cmp
  })
}

// Function: WorkloadComponentsSection
function WorkloadComponentsSection({ workload_components }) {
  if (!(workload_components && (workload_components.total > 0))) return null
  return (
    <Section title="Workload Components Distribution">
      <div className="grid sm:grid-cols-3 gap-4 mb-5">
        {[
          { label: 'Total Workloads',  value: workload_components.total,       color: 'blue' },
          { label: 'Major Workloads',  value: workload_components.major_count, color: 'purple' },
          { label: 'Other Workloads',  value: workload_components.other_count, color: 'slate' },
        ].map(({ label, value, color }) => (
          <div key={label} className={`p-4 rounded-xl bg-${color}-950/20 border border-${color}-800/30`}>
            <p className="text-xs text-slate-400">{label}</p>
            <p className={`text-2xl font-bold text-${color}-300`}>{value ?? 0}</p>
          </div>
        ))}
      </div>
      {workload_components.distribution && Object.keys(workload_components.distribution).length > 0 && (
        <div className="space-y-2">
          <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-2">Distribution</p>
          {Object.entries(workload_components.distribution)
            .sort(([, a], [, b]) => b - a)
            .map(([name, count], i) => {
              const pct = workload_components.total > 0
                ? Math.round((count / workload_components.total) * 100)
                : 0
              const colors = ['#3b82f6','#8b5cf6','#10b981','#f59e0b','#6366f1','#ef4444','#64748b']
              return (
                <div key={name} className="flex items-center gap-3">
                  <span className="text-slate-300 text-xs w-40 truncate">{name}</span>
                  <div className="flex-1 bg-surface-hover rounded-full h-2">
                    <div
                      className="h-2 rounded-full transition-all"
                      style={{ width: `${pct}%`, background: colors[i % colors.length] }}
                    />
                  </div>
                  <span className="text-xs text-slate-400 w-12 text-right">{count} ({pct}%)</span>
                </div>
              )
            })}
        </div>
      )}
    </Section>
  )
}

// Function: VmwareOpenstackCapacitySection
function VmwareOpenstackCapacitySection({ vmware_openstack_capacity }) {
  if (!(vmware_openstack_capacity && (vmware_openstack_capacity.host_count > 0 || vmware_openstack_capacity.node_count > 0))) return null
  return (
    <Section title="VMware / Private Cloud Capacity Planning" defaultOpen={false}>
      <div className="p-5 rounded-xl bg-purple-950/20 border border-purple-700/30">
        <p className="text-sm font-semibold text-purple-200 mb-4">{vmware_openstack_capacity.type}</p>
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-5">
          {[
            { label: vmware_openstack_capacity.host_count != null ? 'Hosts Required' : 'Nodes Required',
              value: vmware_openstack_capacity.host_count ?? vmware_openstack_capacity.node_count,
              color: 'purple' },
            { label: 'Total vCPUs', value: vmware_openstack_capacity.total_cpu, color: 'blue' },
            { label: 'Total RAM (GB)', value: vmware_openstack_capacity.total_ram_gb, color: 'indigo' },
            { label: 'Total Storage (TB)', value: vmware_openstack_capacity.total_storage_tb, color: 'slate' },
          ].map(({ label, value, color }) => (
            <div key={label} className={`p-3 rounded-xl bg-${color}-950/30 border border-${color}-800/30`}>
              <p className="text-xs text-slate-400">{label}</p>
              <p className={`text-xl font-bold text-${color}-300`}>{value ?? '—'}</p>
            </div>
          ))}
        </div>
        {/* AVS pricing tiers */}
        {(vmware_openstack_capacity.payg_month != null) && (
          <div className="overflow-x-auto">
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-2">Pricing by Commitment</p>
            <table className="w-full text-xs">
              <thead>
                <tr className="text-slate-400 border-b border-surface-border">
                  {['Plan','Cost / Host / Month','Total / Month'].map(h => (
                    <th key={h} className="text-left py-2 pr-4 font-medium">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {[
                  { plan: 'Pay As You Go', key: 'payg_month' },
                  { plan: '1-Year Reserved', key: '1yr_month' },
                  { plan: '3-Year Reserved', key: '3yr_month' },
                  { plan: '5-Year Reserved', key: '5yr_month' },
                ].filter(({ key }) => vmware_openstack_capacity[key] != null).map(({ plan, key }) => {
                  const hostCost = vmware_openstack_capacity[key]
                  const hosts = vmware_openstack_capacity.host_count || 1
                  return (
                    <tr key={plan} className="border-b border-surface-border/40 hover:bg-surface-hover">
                      <td className="py-1.5 pr-4 text-slate-300">{plan}</td>
                      <td className="py-1.5 pr-4 text-white">${(hostCost || 0).toLocaleString()}</td>
                      <td className="py-1.5 text-emerald-300 font-semibold">${((hostCost || 0) * hosts).toLocaleString()}</td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        )}
        {vmware_openstack_capacity.note && (
          <p className="text-xs text-slate-500 mt-3 italic">{vmware_openstack_capacity.note}</p>
        )}
      </div>
    </Section>
  )
}

// Function: CloudResourcesRecommendationSection
function CloudResourcesRecommendationSection({ cloud_resources_recommendation }) {
  if (!cloud_resources_recommendation) return null
  return (
    <Section title="Cloud Resources Recommendation" defaultOpen={true}>
      <div className="flex gap-4 mb-5">
        <div className="p-4 rounded-xl bg-blue-950/20 border border-blue-800/30">
          <p className="text-xs text-slate-400">Total Servers</p>
          <p className="text-2xl font-bold text-blue-300">{cloud_resources_recommendation.total_servers}</p>
        </div>
      </div>

      {/* Flavor summary table */}
      {cloud_resources_recommendation.flavors?.length > 0 && (
        <div className="overflow-x-auto mb-5">
          <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-2">Flavor Summary</p>
          <table className="w-full text-xs">
            <thead>
              <tr className="text-slate-400 border-b border-surface-border">
                {['Flavor','OS','Specs','Equiv. Servers','Best Servers'].map(h => (
                  <th key={h} className="text-left py-2 pr-3 font-medium whitespace-nowrap">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {cloud_resources_recommendation.flavors.map((f, i) => (
                <tr key={i} className="border-b border-surface-border/40 hover:bg-surface-hover">
                  <td className="py-1.5 pr-3 font-mono text-white text-xs">{f.flavor_name}</td>
                  <td className="py-1.5 pr-3 text-slate-400 max-w-xs truncate">{f.os_name}</td>
                  <td className="py-1.5 pr-3 text-slate-400">{f.ram_gb}GB · {f.cpu_cores}C</td>
                  <td className="py-1.5 pr-3 text-blue-300">{f.equivalence_servers}</td>
                  <td className="py-1.5 text-emerald-300">{f.best_servers}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Per-server recommendation */}
      {cloud_resources_recommendation.per_server?.length > 0 && (
        <div className="overflow-x-auto">
          <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-2">Per-Server Recommendations</p>
          <table className="w-full text-xs">
            <thead>
              <tr className="text-slate-400 border-b border-surface-border">
                {['Server','Equiv. Flavor','Best Flavor'].map(h => (
                  <th key={h} className="text-left py-2 pr-3 font-medium whitespace-nowrap">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {cloud_resources_recommendation.per_server.map((ps, i) => (
                <tr key={i} className="border-b border-surface-border/40 hover:bg-surface-hover">
                  <td className="py-1.5 pr-3 text-white font-medium">{ps.server_name}</td>
                  <td className="py-1.5 pr-3 font-mono text-blue-300">{ps.equiv_flavor}</td>
                  <td className="py-1.5 font-mono text-emerald-300">{ps.best_flavor}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {cloud_resources_recommendation.notes && (
        <p className="text-xs text-slate-500 mt-4 italic">{cloud_resources_recommendation.notes}</p>
      )}
    </Section>
  )
}

// Function: PricingPlansSection
function PricingPlansSection({ pricing_plans, activePlan, setActivePlan, currentPlan }) {
  if (!(pricing_plans?.length > 0)) return null
  return (
    <Section title="Cloud Pricing Recommendations">
      <div className="flex gap-2 mb-5 flex-wrap">
        {pricing_plans.map((plan, i) => (
          <button key={i} onClick={() => setActivePlan(i)}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
              activePlan === i ? 'bg-brand-blue text-white' : 'bg-surface-hover text-slate-400 hover:text-white'
            }`}>
            {plan.plan_name}
          </button>
        ))}
      </div>
      {currentPlan && (
        <>
          <div className="grid sm:grid-cols-2 gap-4 mb-5">
            <div className="p-4 rounded-xl bg-blue-950/30 border border-blue-700/30">
              <p className="text-xs text-slate-400 mb-1">Equivalence Match / month</p>
              <p className="text-2xl font-bold text-white">
                ${(currentPlan.equivalence_match?.total_cost_month || 0).toLocaleString()}
                <span className="text-sm text-slate-400 font-normal ml-1">/mo</span>
              </p>
              <p className="text-xs text-slate-500 mt-1">{currentPlan.equivalence_match?.total_servers || 0} servers</p>
            </div>
            <div className="p-4 rounded-xl bg-emerald-950/30 border border-emerald-700/30">
              <p className="text-xs text-slate-400 mb-1">Best Match / month</p>
              <p className="text-2xl font-bold text-white">
                ${(currentPlan.best_match?.total_cost_month || 0).toLocaleString()}
                <span className="text-sm text-slate-400 font-normal ml-1">/mo</span>
              </p>
              <p className="text-xs text-slate-500 mt-1">{currentPlan.best_match?.total_servers || 0} servers</p>
            </div>
          </div>
          {currentPlan.equivalence_match?.rows?.length > 0 && (
            <div className="mb-4">
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-2">Equivalence Match</p>
              <div className="overflow-x-auto">
                <table className="w-full text-xs">
                  <thead>
                    <tr className="border-b border-surface-border text-slate-400">
                      {['Cloud','Flavor','OS','Family','Specs','Servers','Cost/Server','Total/mo'].map(h => (
                        <th key={h} className="text-left py-2 pr-3 font-medium whitespace-nowrap">{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {currentPlan.equivalence_match.rows.map((r, i) => (
                      <tr key={i} className="border-b border-surface-border/40 hover:bg-surface-hover">
                        <td className="py-1.5 pr-3 text-slate-300">{r.cloud_name}</td>
                        <td className="py-1.5 pr-3 text-white font-mono text-xs">{r.flavor_name}</td>
                        <td className="py-1.5 pr-3 text-slate-400 max-w-xs truncate">{r.os_name}</td>
                        <td className="py-1.5 pr-3 text-slate-400">{r.flavor_family}</td>
                        <td className="py-1.5 pr-3 text-slate-400">{r.ram_gb}GB · {r.cpu_cores}C</td>
                        <td className="py-1.5 pr-3 text-blue-300 font-semibold">{r.no_of_servers}</td>
                        <td className="py-1.5 pr-3 text-slate-300">${(r.cost_per_month || 0).toFixed(2)}</td>
                        <td className="py-1.5 text-blue-200 font-semibold">${(r.total_cost_month || 0).toFixed(2)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
          {currentPlan.best_match?.rows?.length > 0 && (
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-2">Best Match (Right-sized)</p>
              <div className="overflow-x-auto">
                <table className="w-full text-xs">
                  <thead>
                    <tr className="border-b border-surface-border text-slate-400">
                      {['Cloud','Flavor','OS','Family','Specs','Servers','Cost/Server','Total/mo'].map(h => (
                        <th key={h} className="text-left py-2 pr-3 font-medium whitespace-nowrap">{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {currentPlan.best_match.rows.map((r, i) => (
                      <tr key={i} className="border-b border-surface-border/40 hover:bg-surface-hover">
                        <td className="py-1.5 pr-3 text-slate-300">{r.cloud_name}</td>
                        <td className="py-1.5 pr-3 text-white font-mono text-xs">{r.flavor_name}</td>
                        <td className="py-1.5 pr-3 text-slate-400 max-w-xs truncate">{r.os_name}</td>
                        <td className="py-1.5 pr-3 text-slate-400">{r.flavor_family}</td>
                        <td className="py-1.5 pr-3 text-slate-400">{r.ram_gb}GB · {r.cpu_cores}C</td>
                        <td className="py-1.5 pr-3 text-emerald-300 font-semibold">{r.no_of_servers}</td>
                        <td className="py-1.5 pr-3 text-slate-300">${(r.cost_per_month || 0).toFixed(2)}</td>
                        <td className="py-1.5 text-emerald-200 font-semibold">${(r.total_cost_month || 0).toFixed(2)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              {currentPlan.best_match.note && (
                <p className="text-xs text-slate-500 mt-2 italic">{currentPlan.best_match.note}</p>
              )}
            </div>
          )}
        </>
      )}
    </Section>
  )
}

// Function: DedicatedHostCapacitySection
function DedicatedHostCapacitySection({ dedicated_host_capacity }) {
  if (!(dedicated_host_capacity?.hosts?.length > 0)) return null
  return (
    <Section title={`Dedicated Host Capacity Planning (${dedicated_host_capacity.total_hosts} hosts)`} defaultOpen={false}>
      <p className="text-xs text-slate-500 mb-4">
        {dedicated_host_capacity.provider} — servers grouped by workload family onto dedicated hosts.
        Each row shows per-host resource usage, OS/DB licence counts, and monthly PAYG cost.
      </p>
      <div className="space-y-3">
        {dedicated_host_capacity.hosts.map((host, i) => (
          <div key={i} className="border border-surface-border rounded-xl overflow-hidden">
            <div className="flex items-center gap-4 px-4 py-3 bg-surface-hover">
              <div className="h-8 w-8 rounded-lg bg-indigo-900/50 flex items-center justify-center shrink-0">
                <Server size={14} className="text-indigo-300" />
              </div>
              <div className="flex-1">
                <p className="font-semibold text-white text-sm">{host.host_name} — {host.vm_series}</p>
                <p className="text-xs text-slate-400 mt-0.5">{host.flavor_family} · {host.server_count} VMs</p>
              </div>
              <div className="hidden sm:grid grid-cols-4 gap-4 text-xs text-right">
                <div>
                  <p className="text-slate-500">CPU</p>
                  <p className="text-white font-semibold">{host.host_cpu_used_cores}/{host.host_cpu_total_cores}C <span className="text-slate-400">({host.host_cpu_used_pct}%)</span></p>
                </div>
                <div>
                  <p className="text-slate-500">RAM</p>
                  <p className="text-white font-semibold">{host.host_ram_used_gb}/{host.host_ram_total_gb} GB</p>
                </div>
                <div>
                  <p className="text-slate-500">OS Lic</p>
                  <p className="text-amber-300 font-semibold">{host.os_license_count}</p>
                </div>
                <div>
                  <p className="text-slate-500">PAYG/mo</p>
                  <p className="text-emerald-300 font-semibold">${(host.payg_cost_month || 0).toLocaleString()}</p>
                </div>
              </div>
            </div>
            {host.servers?.length > 0 && (
              <div className="overflow-x-auto">
                <table className="w-full text-xs">
                  <thead>
                    <tr className="text-slate-500 border-b border-surface-border">
                      {['Server','IP','OS','Flavor','Specs','Storage Tier','OS Lic','DB Lic','PAYG/mo'].map(h => (
                        <th key={h} className="text-left py-1.5 pr-3 px-2 font-medium whitespace-nowrap">{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {host.servers.map((srv, j) => (
                      <tr key={j} className="border-b border-surface-border/30 hover:bg-surface-hover">
                        <td className="py-1.5 pr-3 px-2 text-slate-300 truncate max-w-32">{srv.server_name}</td>
                        <td className="py-1.5 pr-3 font-mono text-slate-400">{srv.server_ip}</td>
                        <td className="py-1.5 pr-3 text-slate-400 truncate max-w-28">{srv.os_name}</td>
                        <td className="py-1.5 pr-3 font-mono text-blue-300 text-xs">{srv.flavor_name}</td>
                        <td className="py-1.5 pr-3 text-slate-400">{srv.ram_gb}GB · {srv.cpu_cores}C</td>
                        <td className="py-1.5 pr-3 text-slate-300">{srv.storage_type}</td>
                        <td className="py-1.5 pr-3 text-center">
                          {srv.os_license_count > 0
                            ? <span className="px-1.5 py-0.5 rounded bg-amber-950/60 text-amber-300">{srv.os_license_count}</span>
                            : <span className="text-slate-600">—</span>}
                        </td>
                        <td className="py-1.5 pr-3 text-center">
                          {srv.db_license_count > 0
                            ? <span className="px-1.5 py-0.5 rounded bg-red-950/60 text-red-300">{srv.db_license_count}</span>
                            : <span className="text-slate-600">—</span>}
                        </td>
                        <td className="py-1.5 text-emerald-300 font-semibold">${(srv.payg_cost_month || 0).toFixed(2)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        ))}
      </div>
    </Section>
  )
}

// Function: NetworkTopologySection
function NetworkTopologySection({ network_topology, isOnPrem }) {
  if (!(network_topology && (network_topology.subnets?.length > 0 || network_topology.interfaces?.length > 0))) return null
  return (
    <Section
      title={`Network Topology — L2/L3 (${network_topology.total_subnets || 0} subnet${(network_topology.total_subnets || 0) !== 1 ? 's' : ''})`}
      icon={<Network size={16} />}
      defaultOpen={isOnPrem}
    >
      {/* Subnet cards */}
      {network_topology.subnets?.filter(sn => sn.subnet !== 'unknown').length > 0 && (
        <div className="mb-6">
          <p className="text-sm font-semibold text-slate-300 mb-3">Discovered Subnets</p>
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {network_topology.subnets.filter(sn => sn.subnet !== 'unknown').map((sn, i) => (
              <div key={i} className="p-4 rounded-xl bg-surface-hover border border-surface-border">
                <p className="text-sm font-mono font-semibold text-emerald-300">{sn.subnet}</p>
                {sn.gateway && (
                  <p className="text-xs text-slate-400 mt-1">GW: <span className="font-mono text-slate-300">{sn.gateway}</span></p>
                )}
                <p className="text-xs text-slate-500 mt-1">{sn.host_count} host{sn.host_count !== 1 ? 's' : ''}</p>
                {sn.hosts.map((h, j) => (
                  <p key={j} className="text-xs truncate mt-0.5">
                    <span className="font-mono text-slate-400">{h.ip}</span>
                    {h.mac && <span className="font-mono text-slate-600"> · {h.mac}</span>}
                    <span className="text-slate-600"> {h.server_name}</span>
                  </p>
                ))}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Interface inventory */}
      {network_topology.interfaces?.length > 0 && (
        <div className="mb-6">
          <p className="text-sm font-semibold text-slate-300 mb-3">Host Interface Inventory — L2 / L3 ({network_topology.interfaces.length})</p>
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead>
                <tr className="text-slate-400 border-b border-surface-border">
                  {['Server','Interface','IP Address','MAC Address','Subnet','Gateway','VLAN','Speed','Duplex','State','MTU','Type'].map(h => (
                    <th key={h} className="text-left py-2 pr-3 font-medium whitespace-nowrap">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {network_topology.interfaces.map((iface, i) => (
                  <tr key={i} className="border-b border-surface-border/40 hover:bg-surface-hover">
                    <td className="py-1.5 pr-3 text-white font-medium">{iface.server}</td>
                    <td className="py-1.5 pr-3 font-mono text-slate-400">{iface.interface}</td>
                    <td className="py-1.5 pr-3 font-mono text-emerald-300">{iface.ip || '—'}</td>
                    <td className="py-1.5 pr-3 font-mono text-blue-300">{iface.mac || '—'}</td>
                    <td className="py-1.5 pr-3 font-mono text-slate-400">{iface.subnet || '—'}</td>
                    <td className="py-1.5 pr-3 font-mono text-amber-300">{iface.gateway || '—'}</td>
                    <td className="py-1.5 pr-3">
                      {iface.vlan
                        ? <span className="px-1.5 py-0.5 rounded bg-amber-950/60 text-amber-300 text-xs">{iface.vlan}</span>
                        : <span className="text-slate-600">—</span>}
                    </td>
                    <td className="py-1.5 pr-3 text-slate-400">
                      {iface.bandwidth_mbps > 0
                        ? (iface.bandwidth_mbps >= 1000 ? `${iface.bandwidth_mbps / 1000}G` : `${iface.bandwidth_mbps}M`)
                        : '—'}
                    </td>
                    <td className="py-1.5 pr-3 text-slate-400">{iface.duplex || '—'}</td>
                    <td className="py-1.5 pr-3">
                      {iface.link_state === 'up'
                        ? <span className="px-1.5 py-0.5 rounded bg-emerald-950/60 text-emerald-300 text-xs">up</span>
                        : iface.link_state === 'down'
                          ? <span className="px-1.5 py-0.5 rounded bg-red-950/60 text-red-400 text-xs">down</span>
                          : <span className="text-slate-600">—</span>}
                    </td>
                    <td className="py-1.5 pr-3 text-slate-400">{iface.mtu > 0 ? iface.mtu : '—'}</td>
                    <td className="py-1.5">
                      <span className={`text-xs px-1.5 py-0.5 rounded ${
                        iface.type === 'public' ? 'bg-emerald-950/60 text-emerald-300' : 'bg-slate-700 text-slate-300'
                      }`}>{iface.type || 'private'}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* ARP / L2 neighbor table */}
      {network_topology.arp_table?.length > 0 && (
        <div className="mb-6">
          <p className="text-sm font-semibold text-slate-300 mb-3">L2 ARP / Neighbor Table ({network_topology.arp_table.length} entries)</p>
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead>
                <tr className="text-slate-400 border-b border-surface-border">
                  {['IP Address','MAC Address','Seen From','Interface','State'].map(h => (
                    <th key={h} className="text-left py-2 pr-4 font-medium">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {network_topology.arp_table.map((entry, i) => (
                  <tr key={i} className="border-b border-surface-border/40 hover:bg-surface-hover">
                    <td className="py-1.5 pr-4 font-mono text-emerald-300">{entry.ip}</td>
                    <td className="py-1.5 pr-4 font-mono text-blue-300">{entry.mac}</td>
                    <td className="py-1.5 pr-4 text-slate-300">{entry.seen_from}</td>
                    <td className="py-1.5 pr-4 font-mono text-slate-500">{entry.interface || '—'}</td>
                    <td className="py-1.5 text-slate-500">{entry.type || 'dynamic'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* L3 routing table */}
      {network_topology.routes?.length > 0 && (
        <div>
          <p className="text-sm font-semibold text-slate-300 mb-3">L3 Routing Table ({network_topology.routes.length} routes)</p>
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead>
                <tr className="text-slate-400 border-b border-surface-border">
                  {['Server','Destination','Gateway','Interface','Metric'].map(h => (
                    <th key={h} className="text-left py-2 pr-4 font-medium">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {network_topology.routes.map((r, i) => (
                  <tr key={i} className="border-b border-surface-border/40 hover:bg-surface-hover">
                    <td className="py-1.5 pr-4 text-slate-300">{r.server}</td>
                    <td className="py-1.5 pr-4 font-mono text-blue-300">{r.destination}</td>
                    <td className="py-1.5 pr-4 font-mono text-amber-300">{r.gateway || '—'}</td>
                    <td className="py-1.5 pr-4 font-mono text-slate-500">{r.interface || '—'}</td>
                    <td className="py-1.5 text-slate-500">{r.metric ?? '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Network Utilization */}
      {network_topology.network_utilization?.length > 0 && (
        <div>
          <p className="text-sm font-semibold text-slate-300 mb-3">
            Network Utilization — Inbound / Outbound Summary
          </p>
          <div className="overflow-x-auto mb-2">
            <table className="w-full text-xs">
              <thead>
                <tr className="text-slate-400 border-b border-surface-border">
                  {['Server','IP','Inbound MB/mo','Outbound MB/mo'].map(h => (
                    <th key={h} className="text-left py-2 pr-4 font-medium whitespace-nowrap">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {network_topology.network_utilization.map((nu, i) => (
                  <tr key={i} className="border-b border-surface-border/40 hover:bg-surface-hover">
                    <td className="py-1.5 pr-4 text-white font-medium">{nu.server_name}</td>
                    <td className="py-1.5 pr-4 font-mono text-slate-400">{nu.server_ip}</td>
                    <td className="py-1.5 pr-4 text-blue-300">{(nu.inbound_mb_month || 0).toLocaleString()}</td>
                    <td className="py-1.5 text-emerald-300">{(nu.outbound_mb_month || 0).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="text-xs text-slate-500 italic">
            Note: OnPrem intra-datacenter data transfer is free. Figures are estimates based on workload type.
            Cloud egress charges may apply post-migration.
          </p>
        </div>
      )}
    </Section>
  )
}

// Function: StorageRecommendationSection
function StorageRecommendationSection({ storage_recommendation, isOnPrem }) {
  if (!storage_recommendation) return null
  return (
    <Section
      title={isOnPrem ? 'Storage Inventory' : 'Storage Recommendations'}
      defaultOpen={isOnPrem}
    >
      <div className="grid sm:grid-cols-3 gap-4 mb-5">
        {[
          { label: 'Total Storage', value: `${storage_recommendation.total_storage_tb ?? storage_recommendation.total_storage_tb ?? 0} TB`, color: 'blue' },
          { label: 'Est. Total Cost/Month', value: storage_recommendation.total_cost_month != null ? `$${storage_recommendation.total_cost_month.toLocaleString()}` : '—', color: 'emerald' },
          { label: 'Storage Tiers', value: storage_recommendation.tiers?.length ?? (storage_recommendation.hdd_storage_tb != null ? 2 : 0), color: 'amber' },
        ].map(({ label, value, color }) => (
          <div key={label} className={`p-4 rounded-xl bg-${color}-950/20 border border-${color}-800/30`}>
            <p className="text-xs text-slate-400">{label}</p>
            <p className={`text-2xl font-bold text-${color}-300`}>{value}</p>
          </div>
        ))}
      </div>

      {/* New format: tiers table */}
      {storage_recommendation.tiers?.length > 0 && (
        <div className="overflow-x-auto mb-5">
          <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-2">Storage Tier Breakdown</p>
          <table className="w-full text-xs">
            <thead>
              <tr className="text-slate-400 border-b border-surface-border">
                {['Cloud','Storage Type','Specification','Disks','Total GB','Proposed GB','IOPS','MB/s','Cost/mo'].map(h => (
                  <th key={h} className="text-left py-2 pr-3 font-medium whitespace-nowrap">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {storage_recommendation.tiers.map((t, i) => (
                <tr key={i} className="border-b border-surface-border/40 hover:bg-surface-hover">
                  <td className="py-1.5 pr-3 text-slate-400">{t.cloud_name}</td>
                  <td className="py-1.5 pr-3 text-white font-medium">{t.type_of_storage}</td>
                  <td className="py-1.5 pr-3 text-slate-400 text-xs">{t.specification}</td>
                  <td className="py-1.5 pr-3 text-blue-300 font-semibold">{t.no_of_disks}</td>
                  <td className="py-1.5 pr-3 text-slate-300">{(t.total_storage_gb || 0).toFixed(0)}</td>
                  <td className="py-1.5 pr-3 text-slate-300">{t.proposed_storage_gb}</td>
                  <td className="py-1.5 pr-3 text-amber-300">{t.iops?.toLocaleString() || '—'}</td>
                  <td className="py-1.5 pr-3 text-indigo-300">{t.throughput_mbps || '—'}</td>
                  <td className="py-1.5 text-emerald-300 font-semibold">${(t.total_cost_month || 0).toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Legacy format: recommendations list */}
      {!storage_recommendation.tiers && storage_recommendation.recommendations?.length > 0 && (
        <div className="space-y-3">
          {storage_recommendation.recommendations.map((r, i) => (
            <div key={i} className="flex items-start gap-3 p-3 rounded-lg bg-surface-hover">
              <div className="shrink-0 mt-0.5 h-6 w-6 rounded bg-blue-900/50 flex items-center justify-center">
                <span className="text-blue-300 text-xs font-bold">{i + 1}</span>
              </div>
              <div>
                <p className="text-sm font-medium text-white">{r.type}</p>
                <p className="text-xs text-slate-400">{r.target} · {r.applicable_tb} TB applicable</p>
                <p className="text-xs text-slate-500 mt-0.5">{r.notes}</p>
              </div>
            </div>
          ))}
        </div>
      )}

      {storage_recommendation.notes && (
        <p className="text-xs text-slate-500 mt-3 italic">{storage_recommendation.notes}</p>
      )}
    </Section>
  )
}

// Function: PaginationBar
function PaginationBar({ page, totalPages, pageSize, pageSizeOptions = [10, 25, 50, 100], onPage, onPageSize, total, label = 'items' }) {
  const start = total === 0 ? 0 : (page - 1) * pageSize + 1
  const end = Math.min(page * pageSize, total)
  const range = []
  for (let p = Math.max(1, page - 2); p <= Math.min(totalPages, page + 2); p++) range.push(p)
  return (
    <div className="flex items-center justify-between mt-3 pt-3 border-t border-surface-border text-xs">
      <div className="flex items-center gap-2 text-slate-500">
        <span>{total > 0 ? `${start}–${end} of ${total} ${label}` : `0 ${label}`}</span>
        <span>·</span>
        <span>Per page:</span>
        <select
          value={pageSize}
          onChange={e => { onPageSize(Number(e.target.value)); onPage(1) }}
          className="bg-surface-hover border border-surface-border text-slate-300 rounded px-1.5 py-0.5"
        >
          {pageSizeOptions.map(s => <option key={s} value={s}>{s}</option>)}
        </select>
      </div>
      <div className="flex items-center gap-0.5">
        <button disabled={page === 1} onClick={() => onPage(1)} className="px-1.5 py-0.5 rounded hover:bg-surface-hover disabled:opacity-30 text-slate-400">«</button>
        <button disabled={page === 1} onClick={() => onPage(page - 1)} className="px-1.5 py-0.5 rounded hover:bg-surface-hover disabled:opacity-30 text-slate-400">‹</button>
        {range.map(p => (
          <button key={p} onClick={() => onPage(p)} className={`px-2 py-0.5 rounded ${p === page ? 'bg-brand-green text-white' : 'hover:bg-surface-hover text-slate-400'}`}>{p}</button>
        ))}
        <button disabled={page === totalPages} onClick={() => onPage(page + 1)} className="px-1.5 py-0.5 rounded hover:bg-surface-hover disabled:opacity-30 text-slate-400">›</button>
        <button disabled={page === totalPages} onClick={() => onPage(totalPages)} className="px-1.5 py-0.5 rounded hover:bg-surface-hover disabled:opacity-30 text-slate-400">»</button>
      </div>
    </div>
  )
}

// Function: ScanDetailPage
export default function ScanDetailPage() {
  const { scanId } = useParams()
  const navigate = useNavigate()
  const [scan, setScan] = useState(null)
  const [loading, setLoading] = useState(true)
  const [activePlan, setActivePlan] = useState(0)
  const [expandedServers, setExpandedServers] = useState(new Set())
  // Pagination state for top-level sections
  const [vmFlavorsPage, setVmFlavorsPage] = useState(1)
  const [vmFlavorsPageSize, setVmFlavorsPageSize] = useState(12)
  const [topPkgPage, setTopPkgPage] = useState(1)
  const [topPkgPageSize, setTopPkgPageSize] = useState(25)
  const [swAdvisoryPage, setSwAdvisoryPage] = useState(1)
  const [swAdvisoryPageSize, setSwAdvisoryPageSize] = useState(25)
  // Software inventory interactive controls
  const [swStatusFilter, setSwStatusFilter] = useState(null)       // null | 'expired' | 'expiring_soon' | 'current'
  const [swLicenseFilter, setSwLicenseFilter] = useState(null)     // null | 'commercial' | 'open_source' | 'unknown'
  const [swCategoryFilter, setSwCategoryFilter] = useState(null)   // null | category string
  const [swServerFilter, setSwServerFilter] = useState(null)       // null | server_ip
  const [swSearch, setSwSearch] = useState('')
  const [swAllPage, setSwAllPage] = useState(1)
  const [swAllPageSize, setSwAllPageSize] = useState(25)
  const [swSortKey, setSwSortKey] = useState('validity_status')
  const [swSortDir, setSwSortDir] = useState('asc')
  const [selectedSoftware, setSelectedSoftware] = useState(null)   // detail panel
  const [swServerOpen, setSwServerOpen] = useState(false)          // per-server accordion
  // Per-server pagination: { [idx]: { arpPage, arpPageSize, routesPage, routesPageSize, swPage, swPageSize } }
  const [srvPag, setSrvPag] = useState({})
  // Function: getSP
  const getSP = (i, key, def) => srvPag[i]?.[key] ?? def
  // Function: setSP
  const setSP = (i, key, val) => setSrvPag(prev => ({ ...prev, [i]: { ...prev[i], [key]: val } }))

  // ── Analysis tabs state ──────────────────────────────────────────────────
  const [analysisTab, setAnalysisTab] = useState(null)  // null | 'tco' | 'dependencies' | 'security' | 'decommission' | 'hypervisor' | 'bcdr'
  const [analysisData, setAnalysisData] = useState({})
  const [showChatDrawer, setShowChatDrawer] = useState(false)
  const [analysisLoading, setAnalysisLoading] = useState(false)
  const [analysisError, setAnalysisError] = useState(null)

  const ANALYSIS_TABS = [
    { id: 'tco',          label: 'TCO & Cost',     icon: DollarSign,  fn: getTcoAnalysis },
    { id: 'dependencies', label: 'Dependencies',   icon: GitMerge,    fn: getDependencyMap },
    { id: 'security',     label: 'Security',       icon: ShieldAlert, fn: getSecurityAnalysis },
    { id: 'decommission', label: 'Decommission',   icon: Trash2,      fn: getDecommissionCandidates },
    { id: 'hypervisor',   label: 'Hypervisor',     icon: Cpu,         fn: getHypervisorAnalysis },
    { id: 'bcdr',         label: 'BCDR',           icon: Activity,    fn: getBcdrAnalysis },
  ]

  // Function: loadAnalysis
  const loadAnalysis = async (tabId) => {
    if (analysisData[tabId]) { setAnalysisTab(tabId); return }
    setAnalysisLoading(true)
    setAnalysisError(null)
    setAnalysisTab(tabId)
    try {
      const tabDef = ANALYSIS_TABS.find(t => t.id === tabId)
      const result = await tabDef.fn(scanId)
      setAnalysisData(prev => ({ ...prev, [tabId]: result }))
    } catch (err) {
      setAnalysisError(err?.response?.data?.detail || err.message || 'Analysis failed')
    } finally {
      setAnalysisLoading(false)
    }
  }
  // Function: toggleServer
  const toggleServer = (i) => setExpandedServers(prev => {
    const next = new Set(prev)
    if (next.has(i)) next.delete(i); else next.add(i)
    return next
  })

  useEffect(() => {
    // Function: load
    const load = async () => {
      try {
        // Try scanner job report first (live scan), then fall back to persisted scan
        let raw
        try {
          raw = await getScanReport(scanId)
        } catch {
          raw = await getScan(scanId)
        }
        setScan(normalizeReport(raw))
      } catch {
        toast.error('Failed to load scan')
        navigate('/')
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [scanId])

  // Function: handleExport
  const handleExport = () => {
    const blob = new Blob([JSON.stringify(scan, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${(scan.report_name || 'infra_scan').replace(/\s+/g, '_')}.json`
    a.click()
    URL.revokeObjectURL(url)
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-surface flex items-center justify-center">
        <div className="inline-block h-10 w-10 animate-spin rounded-full border-4 border-brand-green border-r-transparent" />
      </div>
    )
  }

  if (!scan) return null

  const {
    summary, cloud_readiness, capacity_planning,
    servers, pricing_plans, workload_consolidation, eos_advisories,
    paas_recommendations, storage_recommendation, kubernetes_recommendation,
    sustainability, vm_flavors, cloud_resources_recommendation,
    cloud_readiness_details, network_topology,
    source_environment, workload_components, software_inventory,
    dedicated_host_capacity, vmware_openstack_capacity, network_summary,
  } = scan

  const isOnPrem = source_environment?.toLowerCase() === 'onprem'

  const migrationChartData = [
    { name: 'Lift & Shift',    value: cloud_readiness?.lift_and_shift || 0,            fill: '#10b981' },
    { name: 'Smart Shift',     value: cloud_readiness?.smart_shift || 0,                fill: '#3b82f6' },
    { name: 'Smart (Effort)',  value: cloud_readiness?.smart_shift_with_effort || 0,    fill: '#f59e0b' },
    { name: 'PaaS',            value: cloud_readiness?.paas_shift || 0,                 fill: '#8b5cf6' },
    { name: 'PaaS (Effort)',   value: cloud_readiness?.paas_shift_with_effort || 0,     fill: '#6366f1' },
    { name: 'Decommission',    value: cloud_readiness?.decommission || 0,               fill: '#ef4444' },
  ].filter(d => d.value > 0)

  const utilizationData = [
    { name: 'Underutilized', value: summary?.utilization_breakdown?.underutilized || 0, fill: '#f59e0b' },
    { name: 'Moderate',      value: summary?.utilization_breakdown?.moderate || 0,      fill: '#3b82f6' },
    { name: 'Utilized',      value: summary?.utilization_breakdown?.utilized || 0,      fill: '#10b981' },
    { name: 'Unknown',       value: summary?.utilization_breakdown?.unknown || 0,       fill: '#64748b' },
  ].filter(d => d.value > 0)

  const osChartData = summary?.os_distribution
    ? Object.entries(summary.os_distribution).map(([name, value], i) => ({
        name, value,
        fill: ['#3b82f6', '#f59e0b', '#10b981', '#8b5cf6', '#64748b'][i % 5],
      }))
    : []

  const capacityBarData = [
    { name: 'CPU Cores',
      'Equivalence Match': capacity_planning?.equivalence_match?.total_cpu_cores || 0,
      'Best Match':         capacity_planning?.best_match?.total_cpu_cores || 0 },
    { name: 'RAM (GB)',
      'Equivalence Match': capacity_planning?.equivalence_match?.total_ram_gb || 0,
      'Best Match':         capacity_planning?.best_match?.total_ram_gb || 0 },
  ]

  const currentPlan = pricing_plans?.[activePlan]

  const headerSubtitle = [
    scan.source_environment || 'Infrastructure Scan',
    scan.target_cloud && `-> ${scan.target_cloud}`,
    scan.region && `* ${scan.region}`,
  ].filter(Boolean).join(' ')

  return (
    <div className="min-h-screen bg-surface">
      <AppHeader
        title={scan.report_name}
        subtitle={headerSubtitle}
        backTo="/"
        rightSlot={
          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowChatDrawer(true)}
              className="flex items-center gap-1.5 px-3 py-2 rounded-lg text-xs font-semibold
                         bg-brand-green/20 border border-emerald-600/50 text-emerald-300
                         hover:bg-brand-green/30 hover:text-white transition-colors">
              <Brain size={13} /> Ask AI About This Report
            </button>
            <button
              onClick={() => navigate(`/scans/${scanId}/intelligence`)}
              className="flex items-center gap-1.5 px-3 py-2 rounded-lg text-xs font-medium
                         bg-brand-indigo/20 border border-indigo-700/40 text-indigo-300
                         hover:bg-brand-indigo/30 hover:text-white transition-colors">
              <Brain size={13} /> Network Intelligence
            </button>
            {/* Export downloads */}
            <div className="relative group">
              <button className="flex items-center gap-1.5 px-3 py-2 rounded-lg text-xs font-medium
                                 bg-slate-800 border border-slate-700 text-slate-300
                                 hover:bg-slate-700 hover:text-white transition-colors">
                <Download size={13} /> Export <ChevronDown size={11} />
              </button>
              <div className="absolute right-0 top-full mt-1 w-44 bg-slate-900 border border-slate-700
                              rounded-lg shadow-xl z-50 hidden group-hover:block">
                <button onClick={() => downloadExport(scanId, 'excel')}
                        className="flex items-center gap-2 w-full px-3 py-2 text-xs text-slate-300 hover:bg-slate-800 hover:text-white">
                  <FileSpreadsheet size={12} /> Excel (.xlsx)
                </button>
                <button onClick={() => downloadExport(scanId, 'pdf')}
                        className="flex items-center gap-2 w-full px-3 py-2 text-xs text-slate-300 hover:bg-slate-800 hover:text-white">
                  <FileText size={12} /> PDF Report
                </button>
                <button onClick={() => downloadExport(scanId, 'pptx')}
                        className="flex items-center gap-2 w-full px-3 py-2 text-xs text-slate-300 hover:bg-slate-800 hover:text-white">
                  <Presentation size={12} /> PowerPoint
                </button>
                <button onClick={() => downloadExport(scanId, 'csv')}
                        className="flex items-center gap-2 w-full px-3 py-2 text-xs text-slate-300 hover:bg-slate-800 hover:text-white">
                  <TableProperties size={12} /> CMDB CSV
                </button>
                <hr className="border-slate-700 my-1" />
                <div className="px-3 py-1 text-[10px] font-semibold text-slate-500 uppercase tracking-wide">
                  IaC Starter Templates
                </div>
                {['azure', 'aws', 'gcp', 'oci'].map((p) => (
                  <button key={p} onClick={() => downloadIac(scanId, p, 'terraform')}
                          className="flex items-center gap-2 w-full px-3 py-2 text-xs text-slate-300 hover:bg-slate-800 hover:text-white">
                    <Code2 size={12} /> Terraform ({p.toUpperCase()})
                  </button>
                ))}
                <button onClick={() => downloadIac(scanId, 'azure', 'arm')}
                        className="flex items-center gap-2 w-full px-3 py-2 text-xs text-slate-300 hover:bg-slate-800 hover:text-white">
                  <Code2 size={12} /> ARM Template
                </button>
                <button onClick={() => downloadIac(scanId, 'aws', 'cloudformation')}
                        className="flex items-center gap-2 w-full px-3 py-2 text-xs text-slate-300 hover:bg-slate-800 hover:text-white">
                  <Code2 size={12} /> CloudFormation
                </button>
                <hr className="border-slate-700 my-1" />
                <button onClick={handleExport}
                        className="flex items-center gap-2 w-full px-3 py-2 text-xs text-slate-300 hover:bg-slate-800 hover:text-white">
                  <Download size={12} /> Raw JSON
                </button>
              </div>
            </div>
          </div>
        }
      />

      <main className="max-w-7xl mx-auto px-5 py-8 space-y-5">

        {/* Summary cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <StatCard
            label="Total Servers"
            value={summary?.total_servers ?? 0}
            sub={`${summary?.server_type || 'Virtual'} · ${summary?.boot_type || 'BIOS'}`}
            ring="border-blue-800/30"
          />
          <StatCard
            label="OS Families"
            value={summary?.os_count ?? 0}
            sub={summary?.ip_distribution_note || ''}
            ring="border-purple-800/30"
          />
          <StatCard
            label="Storage"
            value={`${summary?.storage_tb ?? 0} TB`}
            sub="Total disk size"
            ring="border-emerald-800/30"
          />
          <StatCard
            label="Cloud Ready"
            value={`${cloud_readiness?.cloud_ready ?? 0}/${summary?.total_servers ?? 0}`}
            sub={cloud_readiness?.cloud_ready_with_effort
              ? `+${cloud_readiness.cloud_ready_with_effort} with effort`
              : 'Ready for migration'}
            ring="border-amber-800/30"
          />
        </div>

        {/* Charts row */}
        <div className="grid md:grid-cols-2 gap-5">
          <Section title="Migration Strategy Breakdown">
            {migrationChartData.length > 0 ? (
              <ResponsiveContainer width="100%" height={220}>
                <PieChart>
                  <Pie data={migrationChartData} cx="50%" cy="50%" outerRadius={85}
                    dataKey="value" label={({ name, value }) => `${name}: ${value}`} labelLine={false}>
                    {migrationChartData.map((e, i) => <Cell key={i} fill={e.fill} />)}
                  </Pie>
                  <Tooltip contentStyle={CHART_TOOLTIP_STYLE} formatter={v => [`${v} servers`, '']} />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <p className="text-slate-500 text-sm py-12 text-center">No migration strategy data</p>
            )}
            <div className="mt-3 grid grid-cols-2 gap-x-4 gap-y-1 text-xs border-t border-surface-border pt-3">
              {[
                { label: 'Cloud Ready',          value: cloud_readiness?.cloud_ready,             color: 'text-emerald-400' },
                { label: 'Ready w/ Effort',      value: cloud_readiness?.cloud_ready_with_effort, color: 'text-teal-400' },
                { label: 'Lift & Shift',         value: cloud_readiness?.lift_and_shift,          color: 'text-green-400' },
                { label: 'Smart Shift',          value: cloud_readiness?.smart_shift,             color: 'text-blue-400' },
                { label: 'Smart Shift (Effort)', value: cloud_readiness?.smart_shift_with_effort, color: 'text-amber-400' },
                { label: 'PaaS Shift',           value: cloud_readiness?.paas_shift,              color: 'text-purple-400' },
                { label: 'PaaS (Effort)',        value: cloud_readiness?.paas_shift_with_effort,  color: 'text-indigo-400' },
                { label: 'Decommission',         value: cloud_readiness?.decommission,            color: 'text-red-400' },
              ].map(({ label, value, color }) => (
                <div key={label} className="flex justify-between py-0.5">
                  <span className="text-slate-400">{label}</span>
                  <span className={`font-semibold ${color}`}>{value ?? 0}</span>
                </div>
              ))}
            </div>
          </Section>

          <Section title="Server Utilization">
            {utilizationData.length > 0 ? (
              <ResponsiveContainer width="100%" height={220}>
                <PieChart>
                  <Pie data={utilizationData} cx="50%" cy="50%" outerRadius={85}
                    dataKey="value" label={({ name, value }) => `${name}: ${value}`} labelLine={false}>
                    {utilizationData.map((e, i) => <Cell key={i} fill={e.fill} />)}
                  </Pie>
                  <Tooltip contentStyle={CHART_TOOLTIP_STYLE} />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <p className="text-slate-500 text-sm py-12 text-center">No utilization data</p>
            )}
          </Section>
        </div>

        {/* OS Distribution */}
        {osChartData.length > 0 && (
          <Section title="OS Distribution">
            <div className="grid md:grid-cols-2 gap-6">
              <ResponsiveContainer width="100%" height={200}>
                <PieChart>
                  <Pie data={osChartData} cx="50%" cy="50%" outerRadius={80}
                    dataKey="value" label={({ name, value }) => `${name}: ${value}`} labelLine={false}>
                    {osChartData.map((e, i) => <Cell key={i} fill={e.fill} />)}
                  </Pie>
                  <Tooltip contentStyle={CHART_TOOLTIP_STYLE} />
                </PieChart>
              </ResponsiveContainer>
              <div className="space-y-2">
                {osChartData.map(({ name, value, fill }) => (
                  <div key={name} className="flex items-center justify-between text-sm">
                    <div className="flex items-center gap-2">
                      <span className="inline-block w-3 h-3 rounded-full" style={{ background: fill }} />
                      <span className="text-slate-300">{name}</span>
                    </div>
                    <span className="font-semibold text-white">{value}</span>
                  </div>
                ))}
              </div>
            </div>
          </Section>
        )}

        {/* Workload Components Distribution */}
        <WorkloadComponentsSection workload_components={workload_components} />

        {/* Capacity Planning */}
        <Section title="Capacity Planning — Equivalence vs Best Match">
          <div className="grid md:grid-cols-2 gap-6">
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={capacityBarData} margin={{ top: 5, right: 5, bottom: 5, left: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#2a2d3e" />
                <XAxis dataKey="name" tick={{ fill: '#94a3b8', fontSize: 11 }} />
                <YAxis tick={{ fill: '#94a3b8', fontSize: 11 }} />
                <Tooltip contentStyle={CHART_TOOLTIP_STYLE} />
                <Legend wrapperStyle={{ fontSize: '12px', color: '#94a3b8' }} />
                <Bar dataKey="Equivalence Match" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                <Bar dataKey="Best Match" fill="#10b981" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
            <div className="space-y-3">
              {[
                { key: 'equivalence_match', label: 'Equivalence Match', color: 'blue' },
                { key: 'best_match', label: 'Best Match', color: 'emerald' },
              ].map(({ key, label, color }) => (
                <div key={key} className={`p-4 rounded-xl border border-${color}-800/30 bg-${color}-950/20`}>
                  <p className={`text-xs font-semibold text-${color}-400 uppercase tracking-wide mb-2`}>{label}</p>
                  <div className="grid grid-cols-2 gap-y-1 text-xs">
                    {[
                      ['Servers',   capacity_planning?.[key]?.total_servers],
                      ['CPU Cores', capacity_planning?.[key]?.total_cpu_cores],
                      ['RAM',       `${capacity_planning?.[key]?.total_ram_gb ?? '—'} GB`],
                      ['Disk',      `${capacity_planning?.[key]?.total_disk_tb ?? '—'} TB`],
                      ...(capacity_planning?.[key]?.estimated_saving_pct && key === 'best_match'
                        ? [] : []),
                    ].map(([lbl, val]) => (
                      <Fragment key={lbl}>
                        <span className="text-slate-400">{lbl}</span>
                        <span className="text-white font-semibold">{val ?? '—'}</span>
                      </Fragment>
                    ))}
                  </div>
                  {key === 'best_match' && capacity_planning?.[key]?.estimated_saving_pct && (
                    <p className="text-xs text-emerald-400 mt-2 font-medium">
                      ~{capacity_planning[key].estimated_saving_pct}% estimated saving
                    </p>
                  )}
                </div>
              ))}
            </div>
          </div>
        </Section>

        {/* Pricing Plans */}
        <PricingPlansSection
          pricing_plans={pricing_plans}
          activePlan={activePlan}
          setActivePlan={setActivePlan}
          currentPlan={currentPlan}
        />

        {/* Dedicated Host Capacity Planning */}
        <DedicatedHostCapacitySection dedicated_host_capacity={dedicated_host_capacity} />

        {/* VMware / OpenStack Capacity Planning */}
        <VmwareOpenstackCapacitySection vmware_openstack_capacity={vmware_openstack_capacity} />

        {/* VM Flavors */}
        {vm_flavors?.flavors?.length > 0 && (
          <Section title={`VM Size Profiles Discovered (${vm_flavors.flavors.length})`}>
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
              {vm_flavors.flavors.slice((vmFlavorsPage-1)*vmFlavorsPageSize, vmFlavorsPage*vmFlavorsPageSize).map((f, i) => (
                <div key={i} className="p-4 rounded-xl bg-surface-hover border border-surface-border">
                  <p className="text-sm font-medium text-white">{f.flavor}</p>
                  <p className="text-xs text-slate-400 mt-1">{f.count} server{f.count !== 1 ? 's' : ''}</p>
                  {f.servers?.length > 0 && (
                    <p className="text-xs text-slate-500 mt-1 truncate">{f.servers.join(', ')}</p>
                  )}
                </div>
              ))}
            </div>
            <PaginationBar
              page={vmFlavorsPage}
              totalPages={Math.max(1, Math.ceil(vm_flavors.flavors.length / vmFlavorsPageSize))}
              pageSize={vmFlavorsPageSize}
              pageSizeOptions={[6, 12, 24, 48]}
              onPage={setVmFlavorsPage}
              onPageSize={v => { setVmFlavorsPageSize(v); setVmFlavorsPage(1) }}
              total={vm_flavors.flavors.length}
              label="profiles"
            />
          </Section>
        )}

        {/* Cloud Resources Recommendation */}
        <CloudResourcesRecommendationSection cloud_resources_recommendation={cloud_resources_recommendation} />

        {/* PaaS Recommendations */}
        {(paas_recommendations?.items?.length > 0 || paas_recommendations?.length > 0) && (
          <Section title="PaaS Migration Candidates" icon={<Package size={16} />}>
            {/* New format: object with items + consolidation_summary */}
            {paas_recommendations?.items ? (
              <>
                <div className="grid sm:grid-cols-3 gap-4 mb-5">
                  <div className="p-4 rounded-xl bg-purple-950/20 border border-purple-800/30">
                    <p className="text-xs text-slate-400">Total PaaS Services</p>
                    <p className="text-2xl font-bold text-purple-300">{paas_recommendations.total_paas_services}</p>
                  </div>
                  <div className="p-4 rounded-xl bg-blue-950/20 border border-blue-800/30">
                    <p className="text-xs text-slate-400">Est. Total Cost/Month</p>
                    <p className="text-2xl font-bold text-blue-300">${(paas_recommendations.estimated_total_cost_month || 0).toLocaleString()}</p>
                  </div>
                  <div className="p-4 rounded-xl bg-emerald-950/20 border border-emerald-800/30">
                    <p className="text-xs text-slate-400">Consolidation Opportunities</p>
                    <p className="text-2xl font-bold text-emerald-300">{paas_recommendations.consolidation_summary?.length || 0}</p>
                  </div>
                </div>
                <div className="overflow-x-auto mb-5">
                  <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-2">PaaS Recommendation Table</p>
                  <table className="w-full text-xs">
                    <thead>
                      <tr className="text-slate-400 border-b border-surface-border">
                        {['Cloud','Server','IP','Workload','Type','PaaS Service','Configuration','Cost/mo'].map(h => (
                          <th key={h} className="text-left py-2 pr-3 font-medium whitespace-nowrap">{h}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {paas_recommendations.items.map((r, i) => (
                        <tr key={i} className="border-b border-surface-border/40 hover:bg-surface-hover">
                          <td className="py-1.5 pr-3 text-slate-400">{r.cloud_name}</td>
                          <td className="py-1.5 pr-3 text-white font-medium truncate max-w-24">{r.server_name}</td>
                          <td className="py-1.5 pr-3 font-mono text-slate-400">{r.server_ip}</td>
                          <td className="py-1.5 pr-3 text-purple-300">{r.workload_name}{r.workload_version ? ` ${r.workload_version}` : ''}</td>
                          <td className="py-1.5 pr-3">
                            <span className={`px-1.5 py-0.5 rounded text-xs ${
                              r.workload_type === 'db'    ? 'bg-blue-950/60 text-blue-300' :
                              r.workload_type === 'web'   ? 'bg-purple-950/60 text-purple-300' :
                              r.workload_type === 'cache' ? 'bg-amber-950/60 text-amber-300' :
                              r.workload_type === 'queue' ? 'bg-indigo-950/60 text-indigo-300' :
                              'bg-slate-700 text-slate-300'
                            }`}>{r.workload_type || 'app'}</span>
                          </td>
                          <td className="py-1.5 pr-3 text-slate-300">{r.paas_service}</td>
                          <td className="py-1.5 pr-3 text-slate-400 text-xs truncate max-w-40">{r.paas_configuration || r.paas_tier}</td>
                          <td className="py-1.5 text-emerald-300 font-semibold">${(r.cost_per_month || 0).toFixed(2)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                {paas_recommendations.consolidation_summary?.length > 0 && (
                  <div>
                    <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-2">Consolidation Summary</p>
                    <div className="space-y-2">
                      {paas_recommendations.consolidation_summary.map((cs, i) => (
                        <div key={i} className="p-3 rounded-lg bg-surface-hover text-xs">
                          <span className="text-purple-300 font-semibold">{cs.workload_name}</span>
                          <span className="text-slate-400 mx-2">→</span>
                          <span className="text-white">{cs.paas_service}</span>
                          <span className="text-slate-500 ml-3">{cs.recommendation}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </>
            ) : (
              /* Legacy array format */
              <div className="overflow-x-auto">
                <table className="w-full text-xs">
                  <thead>
                    <tr className="text-slate-400 border-b border-surface-border">
                      {['Server','IP','Workload','Version','PaaS Target','Benefit'].map(h => (
                        <th key={h} className="text-left py-2 pr-4 font-medium">{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {paas_recommendations.map((r, i) => (
                      <tr key={i} className="border-b border-surface-border/40 hover:bg-surface-hover">
                        <td className="py-2 pr-4 text-white font-medium">{r.server}</td>
                        <td className="py-2 pr-4 font-mono text-slate-400">{r.ip}</td>
                        <td className="py-2 pr-4 text-purple-300">{r.workload}</td>
                        <td className="py-2 pr-4 text-slate-400">{r.version || '—'}</td>
                        <td className="py-2 pr-4 text-slate-300 max-w-xs">{r.paas_target}</td>
                        <td className="py-2 text-slate-500">{r.benefit}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </Section>
        )}

        {/* Server Inventory */}
        {servers?.length > 0 && (
          <Section title={`Server Inventory (${servers.length})`} defaultOpen={false}>
            <div className="space-y-1.5">
              {servers.map((srv, i) => {
                const isExpanded = expandedServers.has(i)
                return (
                  <div key={i} className="border border-surface-border rounded-xl overflow-hidden">
                    {/* Summary row */}
                    <button
                      onClick={() => toggleServer(i)}
                      className="w-full flex items-center gap-3 px-4 py-3 hover:bg-surface-hover text-left"
                    >
                      <ChevronRight size={13} className={`shrink-0 text-slate-500 transition-transform duration-150 ${isExpanded ? 'rotate-90' : ''}`} />
                      <span className="font-mono text-xs text-slate-400 w-32 shrink-0 truncate">{srv.ip}</span>
                      <span className="font-semibold text-white text-sm flex-1 truncate">
                        {srv.name}
                        {srv.cloud_provider && <span className="ml-2 text-xs text-slate-500 font-normal">[{srv.cloud_provider}{srv.region ? ` · ${srv.region}` : ''}]</span>}
                      </span>
                      <span className="text-xs text-slate-400 hidden md:block w-52 truncate">{srv.os}</span>
                      <span className="text-xs text-slate-500 hidden lg:block w-24 shrink-0">
                        {srv.cpu_cores ? `${srv.cpu_cores}C` : '—'} · {srv.ram_gb > 0 ? `${srv.ram_gb}GB` : '—'}
                      </span>
                      <span className={`text-xs px-2 py-0.5 rounded-full shrink-0 ${
                        srv.utilization === 'underutilized' ? 'bg-amber-950/60 text-amber-300' :
                        srv.utilization === 'moderate'      ? 'bg-blue-950/60 text-blue-300' :
                        srv.utilization === 'utilized'      ? 'bg-emerald-950/60 text-emerald-300' :
                                                               'bg-slate-700 text-slate-400'
                      }`}>{srv.utilization || 'unknown'}</span>
                      <span className={`text-xs px-2 py-0.5 rounded-full border shrink-0 ${MIGRATION_BADGE[srv.migration_strategy] || 'bg-slate-800 text-slate-300 border-slate-600/40'}`}>
                        {MIGRATION_LABELS[srv.migration_strategy] || srv.migration_strategy || '—'}
                      </span>
                      {srv.installed_software?.filter(sw => sw.is_eos).length > 0 && (
                        <span className="text-xs px-2 py-0.5 rounded-full shrink-0 bg-red-950/60 text-red-300 border border-red-700/40">
                          {srv.installed_software.filter(sw => sw.is_eos).length} EOS pkgs
                        </span>
                      )}
                    </button>

                    {/* Expanded deep-scan detail panel */}
                    {isExpanded && (
                      <div className="border-t border-surface-border bg-slate-900/40 px-5 py-5 space-y-5">

                        {/* OS & System */}
                        <div>
                          <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-2">OS &amp; System</p>
                          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-x-6 gap-y-1.5 text-xs">
                            {[
                              ['OS', srv.os],
                              ['OS Family', srv.os_family],
                              ['OS Version', srv.os_version],
                              ['Hostname', srv.hostname],
                              ['Architecture', srv.compute_hardware_arch],
                              ['Boot Type', srv.boot_type],
                              ['Virtualization', srv.virtualization_state],
                              ['Hypervisor', srv.virtualization_attributes?.hypervisor],
                              ['Install Type', srv.install_type],
                              ['Instance Type', srv.instance_type],
                              ['CPU Util', srv.cpu_util_pct >= 0 ? `${srv.cpu_util_pct}%` : null],
                              ['RAM Util', srv.ram_util_pct >= 0 ? `${srv.ram_util_pct}%` : null],
                            ].filter(([, v]) => v).map(([label, val]) => (
                              <div key={label} className="flex gap-1.5">
                                <span className="text-slate-500 shrink-0">{label}:</span>
                                <span className="text-slate-200 truncate">{val}</span>
                              </div>
                            ))}
                          </div>
                          {srv.os_end_of_support && (
                            <p className="text-xs mt-2">
                              <span className="text-slate-500">OS End of Support: </span>
                              <EOSBadge date={srv.os_end_of_support} />
                            </p>
                          )}
                        </div>

                        {/* Network Interfaces — L2 + L3 */}
                        {srv.interfaces?.length > 0 && (
                          <div>
                            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-2">
                              Network Interfaces — L2 / L3 ({srv.interfaces.length})
                            </p>
                            <div className="overflow-x-auto">
                              <table className="w-full text-xs">
                                <thead>
                                  <tr className="text-slate-500 border-b border-surface-border">
                                    {['Interface','IP Address','MAC Address','Subnet','Gateway','VLAN','Speed','Duplex','State','MTU','Type'].map(h => (
                                      <th key={h} className="text-left py-1.5 pr-3 font-medium">{h}</th>
                                    ))}
                                  </tr>
                                </thead>
                                <tbody>
                                  {srv.interfaces.map((iface, j) => (
                                    <tr key={j} className="border-b border-surface-border/30">
                                      <td className="py-1.5 pr-3 font-mono text-slate-400">{iface.interface_name}</td>
                                      <td className="py-1.5 pr-3 font-mono text-emerald-300">{iface.ip_address || '—'}</td>
                                      <td className="py-1.5 pr-3 font-mono text-blue-300">{iface.mac_address || '—'}</td>
                                      <td className="py-1.5 pr-3 font-mono text-slate-400">{iface.subnet || '—'}</td>
                                      <td className="py-1.5 pr-3 font-mono text-amber-300">{iface.gateway || '—'}</td>
                                      <td className="py-1.5 pr-3">
                                        {iface.vlan_id
                                          ? <span className="px-1.5 py-0.5 rounded bg-amber-950/60 text-amber-300">{iface.vlan_id}</span>
                                          : <span className="text-slate-600">—</span>}
                                      </td>
                                      <td className="py-1.5 pr-3 text-slate-400">
                                        {iface.bandwidth_mbps > 0 ? `${iface.bandwidth_mbps >= 1000 ? `${iface.bandwidth_mbps/1000}G` : `${iface.bandwidth_mbps}M`}` : '—'}
                                      </td>
                                      <td className="py-1.5 pr-3 text-slate-400">
                                        {iface.duplex ? iface.duplex : '—'}
                                      </td>
                                      <td className="py-1.5 pr-3">
                                        {iface.link_state === 'up'
                                          ? <span className="px-1.5 py-0.5 rounded bg-emerald-950/60 text-emerald-300">up</span>
                                          : iface.link_state === 'down'
                                            ? <span className="px-1.5 py-0.5 rounded bg-red-950/60 text-red-400">down</span>
                                            : <span className="text-slate-600">—</span>}
                                      </td>
                                      <td className="py-1.5 pr-3 text-slate-400">
                                        {iface.mtu > 0 ? iface.mtu : '—'}
                                      </td>
                                      <td className="py-1.5">
                                        <span className={`px-1.5 py-0.5 rounded text-xs ${iface.ip_type === 'public' ? 'bg-emerald-950/60 text-emerald-300' : 'bg-slate-700 text-slate-300'}`}>
                                          {iface.ip_type || 'private'}
                                        </span>
                                      </td>
                                    </tr>
                                  ))}
                                </tbody>
                              </table>
                            </div>

                            {/* L2 ARP Neighbors inline */}
                            {srv.arp_neighbors?.length > 0 && (
                              <div className="mt-3">
                                <p className="text-xs font-medium text-slate-500 mb-1.5">
                                  L2 ARP Neighbors ({srv.arp_neighbors.length})
                                </p>
                                <div className="overflow-x-auto">
                                  <table className="w-full text-xs">
                                    <thead>
                                      <tr className="text-slate-500 border-b border-surface-border">
                                        {['IP Address','MAC Address','Interface','State'].map(h => (
                                          <th key={h} className="text-left py-1.5 pr-4 font-medium">{h}</th>
                                        ))}
                                      </tr>
                                    </thead>
                                    <tbody>
                                      {srv.arp_neighbors.slice((getSP(i,'arpPage',1)-1)*getSP(i,'arpPageSize',25), getSP(i,'arpPage',1)*getSP(i,'arpPageSize',25)).map((nb, j) => (
                                        <tr key={j} className="border-b border-surface-border/30 hover:bg-surface-hover">
                                          <td className="py-1.5 pr-4 font-mono text-emerald-300">{nb.ip}</td>
                                          <td className="py-1.5 pr-4 font-mono text-blue-300">{nb.mac}</td>
                                          <td className="py-1.5 pr-4 font-mono text-slate-400">{nb.interface || '—'}</td>
                                          <td className="py-1.5 text-slate-500">{nb.type || '—'}</td>
                                        </tr>
                                      ))}
                                    </tbody>
                                  </table>
                                  <PaginationBar
                                    page={getSP(i,'arpPage',1)}
                                    totalPages={Math.max(1,Math.ceil(srv.arp_neighbors.length/getSP(i,'arpPageSize',25)))}
                                    pageSize={getSP(i,'arpPageSize',25)}
                                    pageSizeOptions={[10,25,50,100]}
                                    onPage={p=>setSP(i,'arpPage',p)}
                                    onPageSize={s=>{setSP(i,'arpPageSize',s);setSP(i,'arpPage',1)}}
                                    total={srv.arp_neighbors.length}
                                    label="neighbors"
                                  />
                                </div>
                              </div>
                            )}

                            {/* L3 Routes inline */}
                            {srv.routes?.length > 0 && (
                              <div className="mt-3">
                                <p className="text-xs font-medium text-slate-500 mb-1.5">
                                  L3 Routing Table ({srv.routes.length})
                                </p>
                                <div className="overflow-x-auto">
                                  <table className="w-full text-xs">
                                    <thead>
                                      <tr className="text-slate-500 border-b border-surface-border">
                                        {['Destination','Gateway','Interface','Metric'].map(h => (
                                          <th key={h} className="text-left py-1.5 pr-4 font-medium">{h}</th>
                                        ))}
                                      </tr>
                                    </thead>
                                    <tbody>
                                      {srv.routes.slice((getSP(i,'routesPage',1)-1)*getSP(i,'routesPageSize',25), getSP(i,'routesPage',1)*getSP(i,'routesPageSize',25)).map((r, j) => (
                                        <tr key={j} className="border-b border-surface-border/30 hover:bg-surface-hover">
                                          <td className="py-1.5 pr-4 font-mono text-blue-300">{r.destination}</td>
                                          <td className="py-1.5 pr-4 font-mono text-amber-300">{r.gateway || '—'}</td>
                                          <td className="py-1.5 pr-4 font-mono text-slate-400">{r.interface || '—'}</td>
                                          <td className="py-1.5 text-slate-500">{r.metric ?? '—'}</td>
                                        </tr>
                                      ))}
                                    </tbody>
                                  </table>
                                  <PaginationBar
                                    page={getSP(i,'routesPage',1)}
                                    totalPages={Math.max(1,Math.ceil(srv.routes.length/getSP(i,'routesPageSize',25)))}
                                    pageSize={getSP(i,'routesPageSize',25)}
                                    pageSizeOptions={[10,25,50,100]}
                                    onPage={p=>setSP(i,'routesPage',p)}
                                    onPageSize={s=>{setSP(i,'routesPageSize',s);setSP(i,'routesPage',1)}}
                                    total={srv.routes.length}
                                    label="routes"
                                  />
                                </div>
                              </div>
                            )}
                          </div>
                        )}

                        {/* Storage */}
                        <div>
                          <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-2">Storage</p>
                          <div className="grid grid-cols-2 sm:grid-cols-4 gap-x-6 gap-y-1.5 text-xs mb-3">
                            {[
                              ['Total', srv.disk_gb ? `${srv.disk_gb} GB` : null],
                              ['Internal', srv.internal_storage_gb > 0 ? `${srv.internal_storage_gb} GB` : null],
                              ['External', srv.external_storage_gb > 0 ? `${srv.external_storage_gb} GB` : null],
                              ['Type', srv.storage_type],
                              ['Flash', srv.flash_storage_used ? 'Yes' : null],
                              ['DB Storage', srv.db_storage_gb > 0 ? `${srv.db_storage_gb} GB` : null],
                              ['DB Engine', srv.db_engine],
                            ].filter(([, v]) => v).map(([label, val]) => (
                              <div key={label} className="flex gap-1.5">
                                <span className="text-slate-500 shrink-0">{label}:</span>
                                <span className="text-slate-200">{val}</span>
                              </div>
                            ))}
                          </div>
                          {srv.disks?.length > 0 && (
                            <div className="overflow-x-auto">
                              <table className="w-full text-xs">
                                <thead>
                                  <tr className="text-slate-500 border-b border-surface-border">
                                    {['Mount Point','Size (GB)','Used (GB)','Disk Type'].map(h => (
                                      <th key={h} className="text-left py-1.5 pr-4 font-medium">{h}</th>
                                    ))}
                                  </tr>
                                </thead>
                                <tbody>
                                  {srv.disks.map((d, j) => (
                                    <tr key={j} className="border-b border-surface-border/30">
                                      <td className="py-1.5 pr-4 font-mono text-slate-300">{d.mount_point}</td>
                                      <td className="py-1.5 pr-4 text-slate-200">{d.size_gb}</td>
                                      <td className="py-1.5 pr-4 text-slate-200">
                                        {d.used_gb}
                                        {d.size_gb > 0 && (
                                          <span className="ml-2 text-slate-500">({Math.round(d.used_gb / d.size_gb * 100)}%)</span>
                                        )}
                                      </td>
                                      <td className="py-1.5">
                                        <span className={`px-1.5 py-0.5 rounded text-xs ${
                                          d.disk_type === 'SSD' || d.disk_type === 'NVMe' ? 'bg-emerald-950/60 text-emerald-300' :
                                          d.disk_type === 'HDD' ? 'bg-amber-950/60 text-amber-300' :
                                          'bg-slate-700 text-slate-300'}`}>{d.disk_type || '—'}</span>
                                      </td>
                                    </tr>
                                  ))}
                                </tbody>
                              </table>
                            </div>
                          )}
                        </div>

                        {/* Workloads (detailed) */}
                        {srv.workloads_raw?.length > 0 && (
                          <div>
                            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-2">
                              Detected Workloads ({srv.workloads_raw.length})
                            </p>
                            <div className="overflow-x-auto">
                              <table className="w-full text-xs">
                                <thead>
                                  <tr className="text-slate-500 border-b border-surface-border">
                                    {['Name','Version','Type','Port','Location','Status'].map(h => (
                                      <th key={h} className="text-left py-1.5 pr-4 font-medium">{h}</th>
                                    ))}
                                  </tr>
                                </thead>
                                <tbody>
                                  {srv.workloads_raw.map((w, j) => (
                                    <tr key={j} className="border-b border-surface-border/30">
                                      <td className="py-1.5 pr-4 text-white font-medium">{w.name}</td>
                                      <td className="py-1.5 pr-4 text-slate-400">{w.version || '—'}</td>
                                      <td className="py-1.5 pr-4">
                                        <span className={`px-1.5 py-0.5 rounded text-xs ${
                                          w.component_type === 'db'    ? 'bg-blue-950/60 text-blue-300' :
                                          w.component_type === 'web'   ? 'bg-purple-950/60 text-purple-300' :
                                          w.component_type === 'app'   ? 'bg-emerald-950/60 text-emerald-300' :
                                          w.component_type === 'cache' ? 'bg-amber-950/60 text-amber-300' :
                                          w.component_type === 'queue' ? 'bg-indigo-950/60 text-indigo-300' :
                                          'bg-slate-700 text-slate-300'}`}>{w.component_type || '—'}</span>
                                      </td>
                                      <td className="py-1.5 pr-4 font-mono text-slate-400">{w.port || '—'}</td>
                                      <td className="py-1.5 pr-4 text-slate-500 max-w-xs truncate">{w.location || '—'}</td>
                                      <td className="py-1.5 text-emerald-400 text-xs">{w.status || 'running'}</td>
                                    </tr>
                                  ))}
                                </tbody>
                              </table>
                            </div>
                          </div>
                        )}

                        {/* Installed Software Inventory */}
                        {srv.installed_software?.length > 0 && (() => {
                          const eosCount = srv.installed_software.filter(sw => sw.is_eos).length
                          const expCount = srv.installed_software.filter(sw => sw.validity_status === 'expiring_soon').length
                          const okCount  = srv.installed_software.length - eosCount - expCount
                          const eosPct   = Math.round((eosCount / srv.installed_software.length) * 100)
                          const expPct   = Math.round((expCount / srv.installed_software.length) * 100)
                          const okPct    = Math.max(0, 100 - eosPct - expPct)
                          return (
                            <div>
                              <div className="flex items-center justify-between mb-2">
                                <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide">
                                  Installed Software ({srv.installed_software.length} packages)
                                </p>
                                <div className="flex items-center gap-2 text-xs">
                                  {eosCount > 0 && <span className="px-1.5 py-0.5 rounded bg-red-950/60 text-red-300 border border-red-700/40">{eosCount} expired</span>}
                                  {expCount > 0 && <span className="px-1.5 py-0.5 rounded bg-amber-950/60 text-amber-300 border border-amber-700/40">{expCount} expiring</span>}
                                  <span className="px-1.5 py-0.5 rounded bg-emerald-950/60 text-emerald-300 border border-emerald-700/40">{okCount} active</span>
                                </div>
                              </div>
                              {/* Support period mini-bar */}
                              <div className="flex h-2 rounded-full overflow-hidden mb-3 gap-px">
                                {eosPct > 0 && <div className="bg-red-500" style={{ width: `${eosPct}%` }} title={`${eosCount} expired`} />}
                                {expPct > 0 && <div className="bg-amber-500" style={{ width: `${expPct}%` }} title={`${expCount} expiring soon`} />}
                                {okPct  > 0 && <div className="bg-emerald-600" style={{ width: `${okPct}%` }} title={`${okCount} active`} />}
                              </div>
                              <div className="overflow-x-auto">
                                <table className="w-full text-xs">
                                  <thead>
                                    <tr className="text-slate-500 border-b border-surface-border">
                                      {['Package','Version','Vendor','Category','License','Support Period'].map(h => (
                                        <th key={h} className="text-left py-1.5 pr-3 font-medium whitespace-nowrap">{h}</th>
                                      ))}
                                    </tr>
                                  </thead>
                                  <tbody>
                                    {srv.installed_software.slice((getSP(i,'swPage',1)-1)*getSP(i,'swPageSize',50), getSP(i,'swPage',1)*getSP(i,'swPageSize',50)).map((sw, j) => (
                                      <tr
                                        key={j}
                                        onClick={() => setSelectedSoftware({ ...sw, server_name: srv.server_name, server_ip: srv.ip_address })}
                                        className={`border-b border-surface-border/30 cursor-pointer hover:bg-surface-hover transition-colors ${
                                          sw.is_eos ? 'bg-red-950/10' :
                                          sw.validity_status === 'expiring_soon' ? 'bg-amber-950/5' : ''
                                        }`}
                                      >
                                        <td className="py-1.5 pr-3 font-mono text-white">{sw.name}</td>
                                        <td className="py-1.5 pr-3 text-slate-400 font-mono">{sw.version || '\u2014'}</td>
                                        <td className="py-1.5 pr-3 text-slate-500 truncate max-w-32">{sw.vendor || '\u2014'}</td>
                                        <td className="py-1.5 pr-3"><CategoryBadge cat={sw.category} /></td>
                                        <td className="py-1.5 pr-3">
                                          <span className={`px-1.5 py-0.5 rounded text-xs ${
                                            sw.license_type === 'commercial'  ? 'bg-orange-950/60 text-orange-300' :
                                            sw.license_type === 'open_source' ? 'bg-purple-950/60 text-purple-300' :
                                            'bg-slate-700 text-slate-400'
                                          }`}>{sw.license_type || 'unknown'}</span>
                                        </td>
                                        <td className="py-1.5">
                                          <SupportPeriodBadge status={sw.validity_status} label={
                                            sw.support_period_label ||
                                            (sw.is_eos ? `Expired ${Math.abs(sw.days_to_eos || 0)}d ago` :
                                             sw.validity_status === 'expiring_soon' ? `${sw.days_to_eos}d left` :
                                             sw.eos_date ? `Active` : 'No data')
                                          } />
                                        </td>
                                      </tr>
                                    ))}
                                  </tbody>
                                </table>
                                <PaginationBar
                                  page={getSP(i,'swPage',1)}
                                  totalPages={Math.max(1,Math.ceil(srv.installed_software.length/getSP(i,'swPageSize',50)))}
                                  pageSize={getSP(i,'swPageSize',50)}
                                  pageSizeOptions={[25,50,100]}
                                  onPage={p=>setSP(i,'swPage',p)}
                                  onPageSize={s=>{setSP(i,'swPageSize',s);setSP(i,'swPage',1)}}
                                  total={srv.installed_software.length}
                                  label="packages"
                                />
                              </div>
                            </div>
                          )
                        })()}

                        {/* Empty-state for installed software when not populated */}
                        {!(srv.installed_software?.length > 0) && (
                          <div className="text-xs text-slate-500 py-2 border border-dashed border-surface-border rounded px-3 flex items-center gap-2">
                            <svg className="w-3.5 h-3.5 text-slate-600 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
                            No software inventory detected — provide SSH or WinRM credentials when starting a scan for deep package discovery.
                          </div>
                        )}

                        {/* Cloud Assessment */}
                        {(srv.cloud_suitability || srv.ha_dr_requirements) && (
                          <div>
                            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-2">Cloud Assessment</p>
                            <div className="grid grid-cols-2 sm:grid-cols-4 gap-x-6 gap-y-1.5 text-xs">
                              {[
                                ['Cloud Suitability', srv.cloud_suitability],
                                ['HA / DR', srv.ha_dr_requirements],
                                ['RTO', srv.rto_requirements],
                                ['RPO', srv.rpo_requirements],
                              ].filter(([, v]) => v).map(([label, val]) => (
                                <div key={label} className="flex gap-1.5">
                                  <span className="text-slate-500 shrink-0">{label}:</span>
                                  <span className="text-slate-200">{val}</span>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}

                      </div>
                    )}
                  </div>
                )
              })}
            </div>
          </Section>
        )}

        {/* Decommission Candidates */}
        {cloud_readiness_details?.filter(d => d.migration_strategy === 'decommission').length > 0 && (
          <Section title="Decommission Candidates" icon={<Trash2 size={16} />} defaultOpen={true}>
            <p className="text-xs text-slate-500 mb-4">
              Servers classified for decommissioning: EOL operating system, no active workloads, and under-utilized.
              Review and confirm before any action.
            </p>
            <div className="overflow-x-auto">
              <table className="w-full text-xs">
                <thead>
                  <tr className="text-slate-400 border-b border-surface-border">
                    {['Server','IP','OS','CPU','RAM','Utilization','Recommendation'].map(h => (
                      <th key={h} className="text-left py-2 pr-4 font-medium">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {cloud_readiness_details.filter(d => d.migration_strategy === 'decommission').map((d, i) => (
                    <tr key={i} className="border-b border-surface-border/40 hover:bg-surface-hover bg-red-950/5">
                      <td className="py-2 pr-4 text-white font-medium">{d.server_name}</td>
                      <td className="py-2 pr-4 font-mono text-slate-400">{d.server_ip}</td>
                      <td className="py-2 pr-4 text-slate-300">{d.os}</td>
                      <td className="py-2 pr-4 text-slate-400">{d.cpu_cores ? `${d.cpu_cores}C` : '—'}</td>
                      <td className="py-2 pr-4 text-slate-400">{d.ram_gb ? `${d.ram_gb} GB` : '—'}</td>
                      <td className="py-2 pr-4">
                        <span className="px-1.5 py-0.5 rounded text-xs bg-red-950/60 text-red-300">Underutilized</span>
                      </td>
                      <td className="py-2 text-slate-500 max-w-xs leading-relaxed">{d.recommendation}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Section>
        )}

        {/* Software Inventory (Aggregate) */}
        {software_inventory && software_inventory.total_packages > 0 && (
          <Section title={`Software & Application Inventory \u2014 ${software_inventory.unique_packages} Unique Packages`} icon={<Shield size={16} />} defaultOpen={false}>
            {/* Detail panel */}
            <SoftwareDetailPanel item={selectedSoftware} onClose={() => setSelectedSoftware(null)} />

            {/* Clickable stat filter cards */}
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 mb-4">
              {[
                { key: null,           label: 'All Packages',   value: software_inventory.total_packages,      color: 'blue'    },
                { key: 'expired',      label: 'EOS / Expired',  value: software_inventory.eos_count,           color: 'red'     },
                { key: 'expiring_soon',label: 'Expiring Soon',  value: software_inventory.expiring_soon_count, color: 'amber'   },
                { key: 'current',      label: 'Active',         value: (software_inventory.total_packages || 0) - (software_inventory.eos_count || 0) - (software_inventory.expiring_soon_count || 0), color: 'emerald' },
                { key: '_commercial',  label: 'Commercial',     value: software_inventory.commercial_count,    color: 'orange'  },
                { key: '_open_source', label: 'Open Source',    value: software_inventory.open_source_count,   color: 'purple'  },
              ].map(({ key, label, value, color }) => {
                const isActive = key === null ? swStatusFilter === null && swLicenseFilter === null
                              : key.startsWith('_') ? swLicenseFilter === key.slice(1)
                              : swStatusFilter === key
                return (
                  <button
                    key={label}
                    onClick={() => {
                      if (key === null) { setSwStatusFilter(null); setSwLicenseFilter(null) }
                      else if (key.startsWith('_')) { setSwLicenseFilter(isActive ? null : key.slice(1)); setSwStatusFilter(null) }
                      else { setSwStatusFilter(isActive ? null : key); setSwLicenseFilter(null) }
                      setSwAllPage(1)
                    }}
                    className={`p-3 rounded-xl border text-left transition-all ${
                      isActive
                        ? `bg-${color}-900/50 border-${color}-600/60 ring-1 ring-${color}-500/40`
                        : `bg-${color}-950/20 border-${color}-800/30 hover:bg-${color}-950/40`
                    }`}
                  >
                    <p className="text-xs text-slate-400">{label}</p>
                    <p className={`text-xl font-bold text-${color}-300`}>{value ?? 0}</p>
                    {isActive && <p className="text-xs text-slate-500 mt-0.5">&#x2713; Filtered</p>}
                  </button>
                )
              })}
            </div>

            {/* Search + Category filter */}
            <div className="flex flex-wrap gap-2 mb-4">
              <input
                type="text"
                placeholder="Search packages, vendors, servers..."
                value={swSearch}
                onChange={e => { setSwSearch(e.target.value); setSwAllPage(1) }}
                className="flex-1 min-w-48 bg-surface-hover border border-surface-border rounded-lg px-3 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-brand-green"
              />
              <select
                value={swCategoryFilter || ''}
                onChange={e => { setSwCategoryFilter(e.target.value || null); setSwAllPage(1) }}
                className="bg-surface-hover border border-surface-border text-slate-300 rounded-lg px-2.5 py-1.5 text-xs"
              >
                <option value="">All Categories</option>
                {Object.keys(software_inventory.category_distribution || {}).sort().map(cat => (
                  <option key={cat} value={cat}>{cat}</option>
                ))}
              </select>
              <select
                value={swServerFilter || ''}
                onChange={e => { setSwServerFilter(e.target.value || null); setSwAllPage(1) }}
                className="bg-surface-hover border border-surface-border text-slate-300 rounded-lg px-2.5 py-1.5 text-xs"
              >
                <option value="">All Servers</option>
                {[...new Set((software_inventory.items || []).map(x => x.server_ip).filter(Boolean))].map(ip => {
                  const name = (software_inventory.items || []).find(x => x.server_ip === ip)?.server_name || ip
                  return <option key={ip} value={ip}>{name} ({ip})</option>
                })}
              </select>
              {(swStatusFilter || swLicenseFilter || swCategoryFilter || swServerFilter || swSearch) && (
                <button
                  onClick={() => { setSwStatusFilter(null); setSwLicenseFilter(null); setSwCategoryFilter(null); setSwServerFilter(null); setSwSearch(''); setSwAllPage(1) }}
                  className="px-3 py-1.5 rounded-lg bg-red-950/30 border border-red-800/30 text-red-300 text-xs hover:bg-red-950/50"
                >
                  Clear Filters
                </button>
              )}
            </div>

            {/* Main interactive software table */}
            {(() => {
              const items = software_inventory.items || []
              const filtered = sortSoftwareItems(
                filterSoftwareItems(items, {
                  statusFilter: swStatusFilter,
                  licenseFilter: swLicenseFilter,
                  categoryFilter: swCategoryFilter,
                  serverFilter: swServerFilter,
                  search: swSearch,
                }),
                swSortKey, swSortDir
              )
              const totalFiltered = filtered.length
              const paged = filtered.slice((swAllPage - 1) * swAllPageSize, swAllPage * swAllPageSize)
              // Function: sortHeader
              const sortHeader = (key, label) => (
                <th key={key}
                    className="text-left py-2 pr-3 font-medium cursor-pointer select-none hover:text-slate-200 group"
                    onClick={() => { if (swSortKey === key) setSwSortDir(d => d === 'asc' ? 'desc' : 'asc'); else { setSwSortKey(key); setSwSortDir('asc') } }}>
                  {label}
                  <span className="ml-1 opacity-40 group-hover:opacity-80">
                    {swSortKey === key ? (swSortDir === 'asc' ? '\u25B2' : '\u25BC') : '\u25B4'}
                  </span>
                </th>
              )
              return (
                <div>
                  <p className="text-xs text-slate-500 mb-2">
                    {totalFiltered} package{totalFiltered !== 1 ? 's' : ''} found
                    {(swStatusFilter || swLicenseFilter || swCategoryFilter || swServerFilter || swSearch) ? ' (filtered)' : ''}
                    {' '}&mdash; click any row for details
                  </p>
                  <div className="overflow-x-auto">
                    <table className="w-full text-xs">
                      <thead>
                        <tr className="text-slate-400 border-b border-surface-border">
                          {sortHeader('name',             'Package')}
                          {sortHeader('version',          'Version')}
                          {sortHeader('vendor',           'Vendor')}
                          {sortHeader('server_name',      'Server')}
                          {sortHeader('category',         'Category')}
                          {sortHeader('license_type',     'License')}
                          {sortHeader('eos_date',         'EOS Date')}
                          {sortHeader('validity_status',  'Support Status')}
                        </tr>
                      </thead>
                      <tbody>
                        {paged.map((sw, i) => (
                          <tr
                            key={i}
                            onClick={() => setSelectedSoftware(sw)}
                            className={`border-b border-surface-border/40 cursor-pointer transition-colors hover:bg-surface-hover ${
                              sw.is_eos ? 'bg-red-950/10' :
                              sw.validity_status === 'expiring_soon' ? 'bg-amber-950/5' : ''
                            }`}
                          >
                            <td className="py-1.5 pr-3 font-mono text-slate-200 font-medium">{sw.name}</td>
                            <td className="py-1.5 pr-3 text-slate-400 font-mono">{sw.version || '\u2014'}</td>
                            <td className="py-1.5 pr-3 text-slate-400 truncate max-w-32">{sw.vendor || '\u2014'}</td>
                            <td className="py-1.5 pr-3 text-white">{sw.server_name}</td>
                            <td className="py-1.5 pr-3"><CategoryBadge cat={sw.category} /></td>
                            <td className="py-1.5 pr-3">
                              <span className={`px-1.5 py-0.5 rounded text-xs ${
                                sw.license_type === 'commercial'   ? 'bg-orange-950/60 text-orange-300' :
                                sw.license_type === 'open_source'  ? 'bg-purple-950/60 text-purple-300' :
                                'bg-slate-700 text-slate-400'
                              }`}>{sw.license_type || 'unknown'}</span>
                            </td>
                            <td className="py-1.5 pr-3 font-mono text-slate-400">{sw.eos_date || '\u2014'}</td>
                            <td className="py-1.5">
                              <SupportPeriodBadge status={sw.validity_status} label={
                                sw.validity_status === 'expired' ? `Expired ${Math.abs(sw.days_to_eos || 0)}d ago` :
                                sw.validity_status === 'expiring_soon' ? `${sw.days_to_eos}d left` :
                                sw.eos_date ? `Active` : 'No data'
                              } />
                            </td>
                          </tr>
                        ))}
                        {paged.length === 0 && (
                          <tr><td colSpan={8} className="py-6 text-center text-slate-500">No packages match the current filters</td></tr>
                        )}
                      </tbody>
                    </table>
                  </div>
                  <PaginationBar
                    page={swAllPage}
                    totalPages={Math.max(1, Math.ceil(totalFiltered / swAllPageSize))}
                    pageSize={swAllPageSize}
                    pageSizeOptions={[25, 50, 100, 250]}
                    onPage={setSwAllPage}
                    onPageSize={v => { setSwAllPageSize(v); setSwAllPage(1) }}
                    total={totalFiltered}
                    label="packages"
                  />
                </div>
              )
            })()}

            {/* Distribution charts + Per-server breakdown */}
            <div className="grid md:grid-cols-2 gap-5 mt-5">
              {/* Category distribution */}
              {software_inventory.category_distribution && Object.keys(software_inventory.category_distribution).length > 0 && (
                <div>
                  <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-2">Category Distribution</p>
                  <div className="space-y-1.5">
                    {Object.entries(software_inventory.category_distribution)
                      .sort(([, a], [, b]) => b - a)
                      .map(([name, count], i) => {
                        const total = software_inventory.total_packages || 1
                        const pct = Math.round((count / total) * 100)
                        const colors = ['#3b82f6','#8b5cf6','#10b981','#f59e0b','#6366f1','#ef4444','#06b6d4','#64748b']
                        const isActive = swCategoryFilter === name
                        return (
                          <button
                            key={name}
                            onClick={() => { setSwCategoryFilter(isActive ? null : name); setSwAllPage(1) }}
                            className={`w-full flex items-center gap-2 text-left rounded px-1.5 py-0.5 transition-colors ${isActive ? 'bg-surface-hover' : 'hover:bg-surface-hover/50'}`}
                          >
                            <span className="text-slate-300 text-xs w-24 truncate capitalize">{name}</span>
                            <div className="flex-1 bg-surface-hover rounded-full h-1.5">
                              <div className="h-1.5 rounded-full transition-all" style={{ width: `${pct}%`, background: colors[i % colors.length] }} />
                            </div>
                            <span className="text-xs text-slate-500 w-16 text-right shrink-0">{count} ({pct}%)</span>
                          </button>
                        )
                      })}
                  </div>
                </div>
              )}

              {/* Per-server breakdown */}
              {software_inventory.per_server_summary?.length > 0 && (
                <div>
                  <button
                    onClick={() => setSwServerOpen(o => !o)}
                    className="w-full flex items-center justify-between text-xs font-semibold text-slate-400 uppercase tracking-wide mb-2 hover:text-slate-300"
                  >
                    <span>Per-Server Software Breakdown</span>
                    <span>{swServerOpen ? '\u25B2' : '\u25BC'}</span>
                  </button>
                  {swServerOpen && (
                    <div className="space-y-2">
                      {software_inventory.per_server_summary.map((srv, i) => {
                        const eosPct = srv.total > 0 ? Math.round((srv.eos_count / srv.total) * 100) : 0
                        const expPct = srv.total > 0 ? Math.round((srv.expiring_count / srv.total) * 100) : 0
                        const okPct  = Math.max(0, 100 - eosPct - expPct)
                        return (
                          <button
                            key={i}
                            onClick={() => { setSwServerFilter(swServerFilter === srv.server_ip ? null : srv.server_ip); setSwAllPage(1) }}
                            className={`w-full p-2.5 rounded-lg border text-left transition-colors ${
                              swServerFilter === srv.server_ip
                                ? 'bg-surface-hover border-brand-green/40'
                                : 'bg-surface-hover/40 border-surface-border hover:bg-surface-hover'
                            }`}
                          >
                            <div className="flex items-center justify-between mb-1.5">
                              <span className="text-xs font-medium text-white truncate">{srv.server_name}</span>
                              <span className="text-xs text-slate-500 shrink-0 ml-2">{srv.total} pkgs</span>
                            </div>
                            <div className="flex h-1.5 rounded-full overflow-hidden gap-px">
                              {eosPct > 0 && <div className="bg-red-500" style={{ width: `${eosPct}%` }} />}
                              {expPct > 0 && <div className="bg-amber-500" style={{ width: `${expPct}%` }} />}
                              {okPct  > 0 && <div className="bg-emerald-600" style={{ width: `${okPct}%` }} />}
                            </div>
                            <div className="flex gap-3 mt-1 text-xs text-slate-500">
                              {srv.eos_count > 0 && <span className="text-red-400">{srv.eos_count} expired</span>}
                              {srv.expiring_count > 0 && <span className="text-amber-400">{srv.expiring_count} expiring</span>}
                              <span className="text-emerald-400">{srv.total - srv.eos_count - srv.expiring_count} active</span>
                            </div>
                          </button>
                        )
                      })}
                    </div>
                  )}
                </div>
              )}
            </div>
          </Section>
        )}

        {/* Workload Consolidation */}
        {workload_consolidation?.length > 0 && (
          <Section title="Workload Components Consolidation Recommendation">
            {/* Summary table */}
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-2">
              Workload Consolidation Recommendation
            </p>
            <div className="overflow-x-auto mb-6">
              <table className="w-full text-xs">
                <thead>
                  <tr className="text-slate-400 border-b border-surface-border">
                    {['Cloud Name','Workload Components Name','No. of Servers','No. of Workload Components','Recommendation'].map(h => (
                      <th key={h} className="text-left py-2 pr-4 font-medium whitespace-nowrap">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {workload_consolidation.map((wl, i) => (
                    <tr key={i} className="border-b border-surface-border/40 hover:bg-surface-hover">
                      <td className="py-2 pr-4 text-slate-300">{wl.cloud_name}</td>
                      <td className="py-2 pr-4 text-white font-medium">{wl.workload_name}</td>
                      <td className="py-2 pr-4 text-center text-amber-300 font-semibold">{wl.current_server_count}</td>
                      <td className="py-2 pr-4 text-center text-blue-300 font-semibold">{wl.no_of_workload_components}</td>
                      <td className="py-2 text-slate-400 max-w-xs leading-relaxed">{wl.recommendation_note}</td>
                    </tr>
                  ))}
                  <tr className="border-t border-surface-border font-semibold">
                    <td className="py-2 pr-4 text-slate-400" colSpan={2}>Total</td>
                    <td className="py-2 pr-4 text-center text-amber-300">
                      {workload_consolidation.reduce((s, w) => s + (w.current_server_count || 0), 0)}
                    </td>
                    <td className="py-2 pr-4 text-center text-blue-300">
                      {workload_consolidation.reduce((s, w) => s + (w.no_of_workload_components || 0), 0)}
                    </td>
                    <td />
                  </tr>
                </tbody>
              </table>
            </div>

            {/* Servers detail table */}
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-2">
              Workload Consolidation Recommendation Servers
            </p>
            <div className="overflow-x-auto">
              <table className="w-full text-xs">
                <thead>
                  <tr className="text-slate-400 border-b border-surface-border">
                    {['Cloud Name','Server IP','Server Name','Workload Name','Location'].map(h => (
                      <th key={h} className="text-left py-2 pr-4 font-medium whitespace-nowrap">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {workload_consolidation.flatMap((wl) =>
                    (wl.instances || []).map((inst, j) => (
                      <tr key={`${wl.workload_name}-${j}`} className="border-b border-surface-border/30 hover:bg-surface-hover">
                        <td className="py-1.5 pr-4 text-slate-300">{inst.cloud_name || wl.cloud_name}</td>
                        <td className="py-1.5 pr-4 font-mono text-slate-400">{inst.server_ip || '—'}</td>
                        <td className="py-1.5 pr-4 text-white font-medium">{inst.server_name}</td>
                        <td className="py-1.5 pr-4 text-blue-300">{inst.workload_name || wl.workload_name}{inst.version ? ` ${inst.version}` : ''}</td>
                        <td className="py-1.5 font-mono text-slate-500">{inst.location || '—'}</td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </Section>
        )}

        {/* Network Summary (estimated data utilisation per server) */}
        {network_summary?.length > 0 && (
          <Section title="Network Data Utilisation Summary" icon={<Network size={16} />} defaultOpen={false}>
            <div className="overflow-x-auto mb-3">
              <table className="w-full text-xs">
                <thead>
                  <tr className="text-slate-400 border-b border-surface-border">
                    {['Server','IP Address','Inbound MB/month','Outbound MB/month','Note'].map(h => (
                      <th key={h} className="text-left py-2 pr-4 font-medium whitespace-nowrap">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {network_summary.map((ns, i) => (
                    <tr key={i} className="border-b border-surface-border/40 hover:bg-surface-hover">
                      <td className="py-1.5 pr-4 text-white font-medium">{ns.server_name}</td>
                      <td className="py-1.5 pr-4 font-mono text-slate-400">{ns.server_ip}</td>
                      <td className="py-1.5 pr-4 text-blue-300">{(ns.inbound_mb_month || 0).toLocaleString()} MB</td>
                      <td className="py-1.5 pr-4 text-emerald-300">{(ns.outbound_mb_month || 0).toLocaleString()} MB</td>
                      <td className="py-1.5 text-slate-500 text-xs italic">{ns.note}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <p className="text-xs text-slate-500 italic">
              OnPrem intra-datacenter data transfer is free. Cloud egress charges apply post-migration.
              Figures are estimated from workload type; upload monitoring data for precise values.
            </p>
          </Section>
        )}

        {/* Network Topology L2/L3 */}
        <NetworkTopologySection network_topology={network_topology} isOnPrem={isOnPrem} />

        {/* Storage Recommendation */}
        {storage_recommendation && (
          <Section
            title={isOnPrem ? 'Storage Inventory' : 'Storage Recommendations'}
            defaultOpen={isOnPrem}
          >
            <div className="grid sm:grid-cols-3 gap-4 mb-5">
              {[
                { label: 'Total Storage', value: `${storage_recommendation.total_storage_tb ?? storage_recommendation.total_storage_tb ?? 0} TB`, color: 'blue' },
                { label: 'Est. Total Cost/Month', value: storage_recommendation.total_cost_month != null ? `$${storage_recommendation.total_cost_month.toLocaleString()}` : '—', color: 'emerald' },
                { label: 'Storage Tiers', value: storage_recommendation.tiers?.length ?? (storage_recommendation.hdd_storage_tb != null ? 2 : 0), color: 'amber' },
              ].map(({ label, value, color }) => (
                <div key={label} className={`p-4 rounded-xl bg-${color}-950/20 border border-${color}-800/30`}>
                  <p className="text-xs text-slate-400">{label}</p>
                  <p className={`text-2xl font-bold text-${color}-300`}>{value}</p>
                </div>
              ))}
            </div>

            {/* New format: tiers table */}
            {storage_recommendation.tiers?.length > 0 && (
              <div className="overflow-x-auto mb-5">
                <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-2">Storage Tier Breakdown</p>
                <table className="w-full text-xs">
                  <thead>
                    <tr className="text-slate-400 border-b border-surface-border">
                      {['Cloud','Storage Type','Specification','Disks','Total GB','Proposed GB','IOPS','MB/s','Cost/mo'].map(h => (
                        <th key={h} className="text-left py-2 pr-3 font-medium whitespace-nowrap">{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {storage_recommendation.tiers.map((t, i) => (
                      <tr key={i} className="border-b border-surface-border/40 hover:bg-surface-hover">
                        <td className="py-1.5 pr-3 text-slate-400">{t.cloud_name}</td>
                        <td className="py-1.5 pr-3 text-white font-medium">{t.type_of_storage}</td>
                        <td className="py-1.5 pr-3 text-slate-400 text-xs">{t.specification}</td>
                        <td className="py-1.5 pr-3 text-blue-300 font-semibold">{t.no_of_disks}</td>
                        <td className="py-1.5 pr-3 text-slate-300">{(t.total_storage_gb || 0).toFixed(0)}</td>
                        <td className="py-1.5 pr-3 text-slate-300">{t.proposed_storage_gb}</td>
                        <td className="py-1.5 pr-3 text-amber-300">{t.iops?.toLocaleString() || '—'}</td>
                        <td className="py-1.5 pr-3 text-indigo-300">{t.throughput_mbps || '—'}</td>
                        <td className="py-1.5 text-emerald-300 font-semibold">${(t.total_cost_month || 0).toFixed(2)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            {/* Legacy format: recommendations list */}
            {!storage_recommendation.tiers && storage_recommendation.recommendations?.length > 0 && (
              <div className="space-y-3">
                {storage_recommendation.recommendations.map((r, i) => (
                  <div key={i} className="flex items-start gap-3 p-3 rounded-lg bg-surface-hover">
                    <div className="shrink-0 mt-0.5 h-6 w-6 rounded bg-blue-900/50 flex items-center justify-center">
                      <span className="text-blue-300 text-xs font-bold">{i + 1}</span>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-white">{r.type}</p>
                      <p className="text-xs text-slate-400">{r.target} · {r.applicable_tb} TB applicable</p>
                      <p className="text-xs text-slate-500 mt-0.5">{r.notes}</p>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {storage_recommendation.notes && (
              <p className="text-xs text-slate-500 mt-3 italic">{storage_recommendation.notes}</p>
            )}
          </Section>
        )}

        {/* Kubernetes */}
        {kubernetes_recommendation?.containerization_candidates > 0 && (
          <Section title="Kubernetes / Containerization Opportunities" defaultOpen={false}>
            <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-5">
              <StatCard label="Container Candidates" value={kubernetes_recommendation.containerization_candidates} />
              <StatCard label="Total Cost/Month" value={`$${(kubernetes_recommendation.total_cost_month || 0).toLocaleString()}`} sub="PAYG" />
              <StatCard label="Total Cost 1yr" value={`$${(kubernetes_recommendation.total_cost_1yr || 0).toLocaleString()}`} sub="~25% reserved" />
              <StatCard label="Total Cost 3yr" value={`$${(kubernetes_recommendation.total_cost_3yr || 0).toLocaleString()}`} sub="~40% reserved" />
            </div>

            {/* Cluster summaries */}
            {kubernetes_recommendation.clusters?.length > 0 && (
              <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3 mb-5">
                {kubernetes_recommendation.clusters.map((cl, i) => (
                  <div key={i} className="p-4 rounded-xl bg-surface-hover border border-surface-border">
                    <p className="text-sm font-semibold text-white">{cl.cluster_name}</p>
                    <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-xs mt-2">
                      <span className="text-slate-400">Nodes</span><span className="text-white font-semibold">{cl.node_count}</span>
                      <span className="text-slate-400">Pods</span><span className="text-white font-semibold">{cl.pod_count}</span>
                      <span className="text-slate-400">Cost/mo</span><span className="text-emerald-300 font-semibold">${(cl.total_cost_month || 0).toLocaleString()}</span>
                      <span className="text-slate-400">1-yr</span><span className="text-blue-300 font-semibold">${(cl.total_cost_1yr || 0).toLocaleString()}</span>
                      <span className="text-slate-400">3-yr</span><span className="text-indigo-300 font-semibold">${(cl.total_cost_3yr || 0).toLocaleString()}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Per-pod table */}
            {kubernetes_recommendation.pods?.length > 0 && (
              <div className="overflow-x-auto">
                <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-2">Per-Pod Recommendations</p>
                <table className="w-full text-xs">
                  <thead>
                    <tr className="text-slate-400 border-b border-surface-border">
                      {['Cluster','Node','Pod','Workload','Server','Node Flavor','CPU','Mem','Cost/mo','1-yr','3-yr'].map(h => (
                        <th key={h} className="text-left py-2 pr-3 font-medium whitespace-nowrap">{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {kubernetes_recommendation.pods.map((p, i) => (
                      <tr key={i} className="border-b border-surface-border/40 hover:bg-surface-hover">
                        <td className="py-1.5 pr-3 text-blue-300">{p.cluster_name}</td>
                        <td className="py-1.5 pr-3 text-slate-400">{p.node_name}</td>
                        <td className="py-1.5 pr-3 font-mono text-slate-300 text-xs">{p.pod_name}</td>
                        <td className="py-1.5 pr-3 text-purple-300">{p.target_workload}</td>
                        <td className="py-1.5 pr-3 text-slate-400 truncate max-w-24">{p.target_server_name || p.target_server_ip}</td>
                        <td className="py-1.5 pr-3 font-mono text-white text-xs">{p.node_flavor_name}</td>
                        <td className="py-1.5 pr-3 text-slate-400">{p.node_cpu_cores}C</td>
                        <td className="py-1.5 pr-3 text-slate-400">{p.node_ram_gb}GB</td>
                        <td className="py-1.5 pr-3 text-emerald-300 font-semibold">${(p.cost_per_month || 0).toFixed(2)}</td>
                        <td className="py-1.5 pr-3 text-blue-300">${(p.cost_1yr || 0).toLocaleString()}</td>
                        <td className="py-1.5 text-indigo-300">${(p.cost_3yr || 0).toLocaleString()}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            {kubernetes_recommendation.notes && (
              <p className="text-xs text-slate-500 mt-4 italic">{kubernetes_recommendation.notes}</p>
            )}
          </Section>
        )}

        {/* Sustainability */}
        {sustainability && (
          <Section title="Sustainability & CO₂ Reduction" icon={<Leaf size={16} />} defaultOpen={false}>

            {/* Summary provider card (matches PDF top box) */}
            <div className="flex flex-wrap gap-4 mb-6">
              <div className="p-4 rounded-xl bg-surface-hover border border-surface-border min-w-[220px]">
                <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-2">OnPrem · Equivalence Match</p>
                <div className="space-y-1 text-xs">
                  <div className="flex justify-between gap-6">
                    <span className="text-slate-400">Servers</span>
                    <span className="text-white font-semibold">{sustainability.server_count ?? sustainability.per_server?.length ?? 0}</span>
                  </div>
                  <div className="flex justify-between gap-6">
                    <span className="text-slate-400">Power</span>
                    <span className="text-amber-300 font-semibold">{sustainability.total_power_kw_month} kW/month</span>
                  </div>
                  <div className="flex justify-between gap-6">
                    <span className="text-slate-400">CO₂ Emissions</span>
                    <span className="text-emerald-300 font-semibold">{sustainability.total_co2_mt_month} MT/month</span>
                  </div>
                </div>
              </div>
              <div className="flex flex-col gap-1 p-4 rounded-xl bg-surface-hover border border-surface-border text-xs min-w-[180px]">
                <p className="text-slate-400 font-semibold">Annual Savings (Cloud)</p>
                <span className="text-blue-300">{(sustainability.annual_power_saving_kwh || 0).toLocaleString()} kWh/year power</span>
                <span className="text-emerald-300">{sustainability.annual_co2_saving_mt} MT CO₂/year</span>
              </div>
            </div>

            {/* Bar charts — power and CO₂ by utilization band */}
            {sustainability.usage_band_distribution && (() => {
              const dist = sustainability.usage_band_distribution
              const bands = [
                { key: 'underutilized', label: 'USAGE UPTO 25%', powerColor: '#3b82f6', co2Color: '#22c55e' },
                { key: 'moderate',      label: 'USAGE UPTO 50%', powerColor: '#93c5fd', co2Color: '#86efac' },
                { key: 'utilized',      label: 'USAGE UPTO 75%', powerColor: '#1d4ed8', co2Color: '#15803d' },
              ].filter(b => (dist[b.key] || 0) > 0)
              const maxCount = Math.max(...bands.map(b => dist[b.key] || 0), 1)
              const BAR_H = 100
              return (
                <div className="grid sm:grid-cols-2 gap-6 mb-6">
                  {[
                    { title: 'POWER CONSUMPTION PER MONTH (KILOWATTS)', colorKey: 'powerColor' },
                    { title: 'CO₂ EMISSION PER MONTH (METRIC TONS)', colorKey: 'co2Color' },
                  ].map(({ title, colorKey }) => (
                    <div key={title} className="p-4 rounded-xl bg-surface-hover border border-surface-border">
                      <p className="text-xs font-semibold text-slate-300 text-center mb-3">{title}</p>
                      <div className="flex items-end gap-4 justify-center" style={{ height: BAR_H + 40 }}>
                        {bands.map(b => {
                          const count = dist[b.key] || 0
                          const barH = Math.max(4, Math.round((count / maxCount) * BAR_H))
                          return (
                            <div key={b.key} className="flex flex-col items-center gap-1">
                              <span className="text-xs font-bold" style={{ color: b[colorKey] }}>{count}</span>
                              <div style={{ width: 36, height: barH, background: b[colorKey], borderRadius: 3 }} />
                              <span className="text-slate-500 text-center" style={{ fontSize: 9, maxWidth: 60 }}>{b.label}</span>
                            </div>
                          )
                        })}
                      </div>
                      {/* Legend */}
                      <div className="flex flex-wrap gap-2 mt-2 justify-center">
                        {bands.map(b => (
                          <div key={b.key} className="flex items-center gap-1 text-slate-400" style={{ fontSize: 9 }}>
                            <span style={{ display:'inline-block', width:10, height:10, background: b[colorKey], borderRadius:2 }} />
                            {b.label} ({dist[b.key] || 0})
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              )
            })()}

            {/* Per-server CO₂ table */}
            {sustainability.per_server?.length > 0 && (
              <div className="overflow-x-auto">
                <table className="w-full text-xs">
                  <thead>
                    <tr className="text-slate-400 border-b border-surface-border">
                      <th className="text-left py-2 pr-3 font-medium whitespace-nowrap">Server IP</th>
                      <th className="text-left py-2 pr-3 font-medium whitespace-nowrap">Server Name</th>
                      <th className="text-left py-2 pr-3 font-medium whitespace-nowrap">Config Match</th>
                      <th className="text-left py-2 pr-3 font-medium whitespace-nowrap">Flavor Details</th>
                      <th className="text-left py-2 pr-3 font-medium whitespace-nowrap">Power kW/mo</th>
                      <th className="text-center py-2 pr-3 font-medium whitespace-nowrap">CO₂ @25%</th>
                      <th className="text-center py-2 pr-3 font-medium whitespace-nowrap">CO₂ @50%</th>
                      <th className="text-center py-2 pr-3 font-medium whitespace-nowrap">CO₂ @75%</th>
                      <th className="text-center py-2 font-medium whitespace-nowrap">CO₂ @100%</th>
                    </tr>
                  </thead>
                  <tbody>
                    {sustainability.per_server.map((ps, i) => {
                      const band = ps.utilization_band || 'underutilized'
                      const activeCols = { underutilized: 0, moderate: 1, utilized: 2 }
                      const activeIdx = activeCols[band] ?? 0
                      const co2Vals = [ps.co2_mt_25pct, ps.co2_mt_50pct, ps.co2_mt_75pct, ps.co2_mt_100pct]
                      return (
                        <tr key={i} className="border-b border-surface-border/40 hover:bg-surface-hover">
                          <td className="py-1.5 pr-3 font-mono text-slate-400">{ps.server_ip}</td>
                          <td className="py-1.5 pr-3 text-white font-medium">{ps.server_name}</td>
                          <td className="py-1.5 pr-3 text-slate-300">{ps.configuration_match}</td>
                          <td className="py-1.5 pr-3 font-mono text-slate-400 text-xs max-w-[180px] truncate" title={ps.flavor_details}>
                            {ps.flavor_details?.split('\n')[0]?.replace('Name: ', '') || ps.flavor_details}
                          </td>
                          <td className="py-1.5 pr-3 text-amber-300 font-semibold">{ps.power_kw_month}</td>
                          {co2Vals.map((v, ci) => (
                            <td key={ci} className={`py-1.5 pr-3 text-center font-semibold rounded ${
                              ci === activeIdx
                                ? 'bg-emerald-900/60 text-emerald-300 ring-1 ring-emerald-500/50'
                                : 'text-slate-400'
                            }`}>
                              {v?.toFixed(2)}
                            </td>
                          ))}
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>
            )}

            {sustainability.notes && (
              <p className="text-xs text-slate-500 mt-4">{sustainability.notes}</p>
            )}
          </Section>
        )}

        {/* EOS Advisories */}
        {(eos_advisories?.operating_systems?.length > 0 || eos_advisories?.workloads?.length > 0) && (
          <Section title="End of Support Advisories" icon={<AlertTriangle size={16} />}>
            {eos_advisories.operating_systems?.length > 0 && (
              <div className="mb-6">
                <p className="text-sm font-semibold text-slate-300 mb-4">
                  Operating Systems ({eos_advisories.operating_systems.length})
                </p>

                {/* OS Distribution + EOL Year charts */}
                {(() => {
                  // Build OS count map
                  const osCounts = {}
                  const eolYearCounts = {}
                  for (const item of eos_advisories.operating_systems) {
                    const os = item.os || item.os_name || 'Unknown'
                    osCounts[os] = (osCounts[os] || 0) + 1
                    const yr = item.end_of_support?.slice(0, 4)
                    if (yr) eolYearCounts[yr] = (eolYearCounts[yr] || 0) + 1
                  }
                  const osEntries = Object.entries(osCounts).sort((a,b) => b[1]-a[1])
                  const eolEntries = Object.entries(eolYearCounts).sort((a,b) => a[0].localeCompare(b[0]))
                  const maxOs = Math.max(...osEntries.map(([,v]) => v), 1)
                  const maxEol = Math.max(...eolEntries.map(([,v]) => v), 1)
                  const OS_COLORS = ['#3b82f6','#10b981','#6366f1','#f59e0b','#ef4444','#8b5cf6','#06b6d4']
                  const BAR_H = 90
                  return (
                    <div className="grid sm:grid-cols-2 gap-4 mb-5">
                      {/* OS Distribution */}
                      <div className="p-4 rounded-xl bg-surface-hover border border-surface-border">
                        <p className="text-xs font-semibold text-slate-300 text-center mb-3">Operating System Distribution</p>
                        <div className="flex items-end gap-3 justify-center" style={{ height: BAR_H + 32 }}>
                          {osEntries.map(([os, count], i) => {
                            const barH = Math.max(4, Math.round((count / maxOs) * BAR_H))
                            const color = OS_COLORS[i % OS_COLORS.length]
                            return (
                              <div key={os} className="flex flex-col items-center gap-1 min-w-0">
                                <span className="text-xs font-bold" style={{ color }}>{count}</span>
                                <div style={{ width: 28, height: barH, background: color, borderRadius: 3 }} />
                                <span className="text-slate-500 text-center truncate w-full" style={{ fontSize: 8, maxWidth: 70 }} title={os}>{os}</span>
                              </div>
                            )
                          })}
                        </div>
                      </div>

                      {/* EOL Year Distribution */}
                      <div className="p-4 rounded-xl bg-surface-hover border border-surface-border">
                        <p className="text-xs font-semibold text-slate-300 text-center mb-3">End of Life by Year</p>
                        <div className="flex items-end gap-4 justify-center" style={{ height: BAR_H + 32 }}>
                          {eolEntries.map(([yr, count], i) => {
                            const barH = Math.max(4, Math.round((count / maxEol) * BAR_H))
                            return (
                              <div key={yr} className="flex flex-col items-center gap-1">
                                <span className="text-xs font-bold text-blue-300">{count}</span>
                                <div style={{ width: 32, height: barH, background: '#3b82f6', borderRadius: 3 }} />
                                <span className="text-slate-500" style={{ fontSize: 9 }}>EOL {yr}</span>
                              </div>
                            )
                          })}
                        </div>
                        {/* Legend */}
                        <div className="flex flex-wrap gap-2 mt-1 justify-center">
                          {eolEntries.map(([yr, count]) => (
                            <span key={yr} className="text-slate-400" style={{ fontSize: 9 }}>
                              EOL on {yr} ({count})
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>
                  )
                })()}

                {/* Legend badges */}
                <div className="flex flex-wrap gap-3 mb-3">
                  <div className="flex items-center gap-1.5 text-xs text-slate-400">
                    <span className="w-3 h-3 rounded-sm bg-red-600 inline-block" />
                    This server has reached its end of support period.
                  </div>
                  <div className="flex items-center gap-1.5 text-xs text-slate-400">
                    <span className="w-3 h-3 rounded-sm bg-amber-500/70 inline-block" />
                    This server is nearing the end of its support period.
                  </div>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full text-xs">
                    <thead>
                      <tr className="text-slate-400 border-b border-surface-border">
                        {['Server IP','Server Name','Operating System','End of Support','End of Extended Support','Migration Advisory'].map(h => (
                          <th key={h} className="text-left py-2 pr-4 font-medium whitespace-nowrap">{h}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {eos_advisories.operating_systems.map((item, i) => (
                        <tr key={i} className={`border-b border-surface-border/40 hover:bg-surface-hover ${
                          item.is_eos ? 'bg-red-950/10' : ''
                        }`}>
                          <td className="py-2 pr-4 font-mono text-slate-400">{item.server_ip || '—'}</td>
                          <td className="py-2 pr-4 text-white font-medium">{item.server_name}</td>
                          <td className="py-2 pr-4 text-slate-300">{item.os || item.os_name}</td>
                          <td className="py-2 pr-4"><EOSBadge date={item.end_of_support} /></td>
                          <td className="py-2 pr-4"><EOSBadge date={item.end_of_extended_support} /></td>
                          <td className="py-2 text-slate-400 max-w-xs leading-relaxed">{item.migration_advisory}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {eos_advisories.workloads?.length > 0 && (
              <div>
                <p className="text-sm font-semibold text-slate-300 mb-3">
                  Workloads ({eos_advisories.workloads.length})
                </p>
                <div className="overflow-x-auto">
                  <table className="w-full text-xs">
                    <thead>
                      <tr className="text-slate-400 border-b border-surface-border">
                        {['Server','IP','Workload','Location','End of Support','Extended EOS'].map(h => (
                          <th key={h} className="text-left py-2 pr-4 font-medium">{h}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {eos_advisories.workloads.map((item, i) => (
                        <tr key={i} className="border-b border-surface-border/40 hover:bg-surface-hover">
                          <td className="py-2 pr-4 text-white font-medium">{item.server_name}</td>
                          <td className="py-2 pr-4 font-mono text-slate-400">{item.server_ip || '—'}</td>
                          <td className="py-2 pr-4 text-slate-300">{item.workload}</td>
                          <td className="py-2 pr-4 font-mono text-slate-500">{item.location || '—'}</td>
                          <td className="py-2 pr-4"><EOSBadge date={item.end_of_support} /></td>
                          <td className="py-2"><EOSBadge date={item.end_of_extended_support} /></td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </Section>
        )}

        {/* ── Advanced Analysis Tabs ─────────────────────────────────── */}
        <div className="rounded-xl border border-slate-700/50 bg-slate-900/50 overflow-hidden">
          <div className="flex items-center gap-1 px-4 pt-4 pb-0 border-b border-slate-700/40 overflow-x-auto">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wide mr-3 whitespace-nowrap">Advanced Analysis</span>
            {ANALYSIS_TABS.map(tab => {
              const Icon = tab.icon
              const active = analysisTab === tab.id
              return (
                <button
                  key={tab.id}
                  onClick={() => analysisTab === tab.id ? setAnalysisTab(null) : loadAnalysis(tab.id)}
                  className={`flex items-center gap-1.5 px-3 py-2 text-xs font-medium border-b-2 whitespace-nowrap transition-colors ${
                    active
                      ? 'border-brand-green text-brand-green'
                      : 'border-transparent text-slate-400 hover:text-slate-200'
                  }`}>
                  <Icon size={12} />{tab.label}
                </button>
              )
            })}
          </div>

          {analysisTab && (
            <div className="p-5">
              {analysisLoading && (
                <div className="flex items-center justify-center py-12">
                  <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-brand-green border-r-transparent" />
                  <span className="ml-3 text-sm text-slate-400">Running analysis…</span>
                </div>
              )}
              {analysisError && (
                <div className="p-4 bg-red-950/40 border border-red-700/40 rounded-lg text-sm text-red-300">
                  {analysisError}
                </div>
              )}
              {!analysisLoading && !analysisError && analysisData[analysisTab] && (
                <AnalysisPanel tab={analysisTab} data={analysisData[analysisTab]} />
              )}
            </div>
          )}
        </div>

      </main>

      {showChatDrawer && (
        <div className="fixed inset-0 z-50 flex justify-end bg-black/50" onClick={() => setShowChatDrawer(false)}>
          <div className="w-full max-w-lg h-full bg-[#0f1623] border-l border-surface-border shadow-2xl flex flex-col"
               onClick={e => e.stopPropagation()}>
            <div className="flex items-center justify-between px-5 py-4 border-b border-surface-border shrink-0">
              <div className="flex items-center gap-2">
                <Brain size={16} className="text-brand-green" />
                <h3 className="font-semibold text-white text-sm">Ask AI About This Report</h3>
              </div>
              <button onClick={() => setShowChatDrawer(false)} className="text-slate-400 hover:text-white text-xl leading-none">&#x00D7;</button>
            </div>
            <div className="flex-1 overflow-y-auto p-5">
              <ChatPanel scanId={scanId} />
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

// ══════════════════════════════════════════════════════════════════════════════
// Analysis Panels
// ══════════════════════════════════════════════════════════════════════════════

// Function: AnalysisPanel
function AnalysisPanel({ tab, data }) {
  switch (tab) {
    case 'tco':          return <TcoPanel data={data} />
    case 'dependencies': return <DependenciesPanel data={data} />
    case 'security':     return <SecurityPanel data={data} />
    case 'decommission': return <DecommissionPanel data={data} />
    case 'hypervisor':   return <HypervisorPanel data={data} />
    case 'bcdr':         return <BcdrPanel data={data} />
    default: return null
  }
}

// Function: $
const $ = (n) => n != null ? `$${Number(n).toLocaleString()}` : '—'
// Function: pct
const pct = (n) => n != null ? `${Math.round(n)}%` : '—'

// Function: StatBadge
function StatBadge({ label, value, color = 'text-brand-green' }) {
  return (
    <div className="flex flex-col items-center bg-slate-800/60 rounded-xl p-4 border border-slate-700/30">
      <span className={`text-2xl font-bold ${color}`}>{value}</span>
      <span className="text-xs text-slate-400 mt-1 text-center">{label}</span>
    </div>
  )
}

// ── TCO & Right-sizing ────────────────────────────────────────────────────────
// Function: TcoPanel
function TcoPanel({ data }) {
  const s = data.summary || {}
  const results = data.server_results || []
  return (
    <div className="space-y-5">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <StatBadge label="On-Prem Monthly" value={$(s.total_onprem_cost)} />
        <StatBadge label="Est. Cloud Savings" value={$(s.total_cloud_savings)} color="text-emerald-400" />
        <StatBadge label="3-yr On-Prem TCO" value={$(s.tco_onprem_3yr_usd)} color="text-amber-400" />
        <StatBadge label="3-yr Cloud TCO" value={$(s.tco_cloud_3yr_usd)} color="text-blue-400" />
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-xs">
          <thead>
            <tr className="border-b border-slate-700/50 text-slate-400">
              <th className="text-left py-2 pr-3">Server</th>
              <th className="text-right py-2 pr-3">Current vCPU</th>
              <th className="text-right py-2 pr-3">Right-Sized CPU</th>
              <th className="text-right py-2 pr-3">On-Prem/mo</th>
              <th className="text-right py-2 pr-3">Cloud/mo</th>
              <th className="text-right py-2">Monthly Saving</th>
            </tr>
          </thead>
          <tbody>
            {results.map((r, i) => (
              <tr key={i} className="border-b border-slate-800/40 hover:bg-slate-800/30">
                <td className="py-1.5 pr-3 font-medium text-slate-200">{r.server_name}</td>
                <td className="py-1.5 pr-3 text-right">{r.original_cpu ?? '—'}</td>
                <td className="py-1.5 pr-3 text-right text-emerald-400">{r.right_sized_cpu ?? '—'}</td>
                <td className="py-1.5 pr-3 text-right">{$(r.onprem_monthly_cost)}</td>
                <td className="py-1.5 pr-3 text-right">{$(r.cloud_monthly_cost)}</td>
                <td className={`py-1.5 text-right font-semibold ${
                  (r.monthly_savings ?? 0) > 0 ? 'text-emerald-400' : 'text-slate-400'
                }`}>{$(r.monthly_savings)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

// ── Dependency Mapping ────────────────────────────────────────────────────────
// Function: DependenciesPanel
function DependenciesPanel({ data }) {
  const wavePlan = data.wave_plan || []
  const summary  = data.summary  || {}
  return (
    <div className="space-y-5">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <StatBadge label="Total Nodes" value={data.nodes?.length ?? 0} />
        <StatBadge label="Dependencies" value={data.edges?.length ?? 0} color="text-blue-400" />
        <StatBadge label="Migration Waves" value={summary.total_waves ?? wavePlan.length} color="text-purple-400" />
        <StatBadge label="High-Effort Servers" value={summary.high_effort_servers ?? 0} color="text-amber-400" />
      </div>
      <div className="space-y-3">
        {wavePlan.map(wave => (
          <div key={wave.wave} className="rounded-lg border border-slate-700/40 bg-slate-800/30 p-4">
            <div className="flex items-center gap-2 mb-2">
              <span className="px-2 py-0.5 rounded-full text-xs font-bold bg-brand-green/20 text-brand-green border border-brand-green/30">
                Wave {wave.wave}
              </span>
              <span className="text-xs text-slate-400">{wave.rationale}</span>
              <span className="ml-auto text-xs text-slate-500">{wave.servers?.length ?? 0} servers</span>
            </div>
            <div className="flex flex-wrap gap-1.5">
              {(wave.servers || []).map((s, i) => (
                <span key={i} className="px-2 py-0.5 bg-slate-700/60 rounded text-xs text-slate-300">{s}</span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

// ── Security & Compliance ─────────────────────────────────────────────────────
// Function: SecurityPanel
function SecurityPanel({ data }) {
  const s       = data.summary || {}
  const results = data.server_results || []
  const RISK_COLOR = { critical: 'text-red-400', high: 'text-orange-400', medium: 'text-amber-400', low: 'text-green-400' }
  return (
    <div className="space-y-5">
      <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
        <StatBadge label="Critical Risk Servers" value={s.critical_risk_servers ?? 0} color="text-red-400" />
        <StatBadge label="Total CVE Findings" value={s.total_cve_findings ?? 0} color="text-orange-400" />
        <StatBadge label="Avg CIS Score" value={pct(s.avg_cis_score)} color="text-blue-400" />
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-xs">
          <thead>
            <tr className="border-b border-slate-700/50 text-slate-400">
              <th className="text-left py-2 pr-3">Server</th>
              <th className="text-center py-2 pr-3">Risk</th>
              <th className="text-center py-2 pr-3">CVEs</th>
              <th className="text-center py-2 pr-3">CIS Score</th>
              <th className="text-left py-2">Top Issues</th>
            </tr>
          </thead>
          <tbody>
            {results.map((r, i) => (
              <tr key={i} className="border-b border-slate-800/40 hover:bg-slate-800/30">
                <td className="py-1.5 pr-3 font-medium text-slate-200">{r.server_name}</td>
                <td className={`py-1.5 pr-3 text-center font-bold ${RISK_COLOR[r.risk_level] || 'text-slate-400'}`}>
                  {(r.risk_level || '').toUpperCase()}
                </td>
                <td className="py-1.5 pr-3 text-center">{r.cve_findings?.length ?? 0}</td>
                <td className="py-1.5 pr-3 text-center">{pct(r.cis_score)}</td>
                <td className="py-1.5 text-slate-400 truncate max-w-xs">
                  {(r.protocol_risks || []).slice(0, 2).map(p => p.protocol).join(', ')}
                  {(r.cve_findings || []).slice(0, 1).map(c => c.cve_id).join(', ')}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

// ── Decommission Candidates ───────────────────────────────────────────────────
// Function: DecommissionPanel
function DecommissionPanel({ data }) {
  const s          = data.summary       || {}
  const candidates = data.candidates    || []
  const orphaned   = data.orphaned_resources || []
  const duplicates = data.duplicate_services || []
  return (
    <div className="space-y-5">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <StatBadge label="Decommission Candidates" value={s.total_decommission_candidates ?? candidates.length} color="text-red-400" />
        <StatBadge label="Zombie Servers" value={s.zombie_servers ?? 0} color="text-orange-400" />
        <StatBadge label="Orphaned Resources" value={s.orphaned_resource_servers ?? orphaned.length} color="text-amber-400" />
        <StatBadge label="Duplicate Services" value={duplicates.length} color="text-purple-400" />
      </div>
      {candidates.length > 0 && (
        <div>
          <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-2">Decommission Candidates</p>
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead>
                <tr className="border-b border-slate-700/50 text-slate-400">
                  <th className="text-left py-2 pr-3">Server</th>
                  <th className="text-left py-2 pr-3">Reason</th>
                  <th className="text-left py-2">Recommendation</th>
                </tr>
              </thead>
              <tbody>
                {candidates.map((c, i) => (
                  <tr key={i} className="border-b border-slate-800/40 hover:bg-slate-800/30">
                    <td className="py-1.5 pr-3 font-medium text-slate-200">{c.server_name}</td>
                    <td className="py-1.5 pr-3 text-slate-400">{(c.reasons || []).join('; ')}</td>
                    <td className="py-1.5 text-slate-400">{c.recommendation}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}

// ── Hypervisor Consolidation ──────────────────────────────────────────────────
// Function: HypervisorPanel
function HypervisorPanel({ data }) {
  const s       = data.summary           || {}
  const global  = data.global_consolidation || {}
  const sprawl  = data.vm_sprawl         || []
  const clusters = data.clusters         || []
  return (
    <div className="space-y-5">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <StatBadge label="Virtual Machines" value={s.virtual_count ?? 0} />
        <StatBadge label="Physical Hosts" value={s.physical_count ?? 0} color="text-blue-400" />
        <StatBadge label="Hosts to Eliminate" value={global.hosts_to_eliminate ?? 0} color="text-emerald-400" />
        <StatBadge label="Monthly Savings" value={$(global.estimated_monthly_savings_usd)} color="text-amber-400" />
      </div>
      {s.message && (
        <div className="p-4 bg-slate-800/40 rounded-lg text-sm text-slate-400">{s.message}</div>
      )}
      {clusters.length > 0 && (
        <div>
          <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-2">Cluster Analysis</p>
          {clusters.map((cl, i) => (
            <div key={i} className="mb-3 p-4 bg-slate-800/30 rounded-lg border border-slate-700/30">
              <div className="flex items-center justify-between mb-2">
                <span className="font-medium text-slate-200 text-sm">{cl.cluster_name}</span>
                <span className="text-xs text-slate-400">{cl.vm_count} VMs</span>
              </div>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs text-slate-400">
                <span>Current hosts: <b className="text-slate-200">{cl.consolidation?.current_estimated_hosts}</b></span>
                <span>Recommended: <b className="text-emerald-400">{cl.consolidation?.recommended_hosts}</b></span>
                <span>Eliminate: <b className="text-amber-400">{cl.consolidation?.hosts_to_eliminate}</b></span>
                <span>Saving/mo: <b className="text-emerald-400">{$(cl.consolidation?.estimated_monthly_savings_usd)}</b></span>
              </div>
            </div>
          ))}
        </div>
      )}
      {sprawl.length > 0 && (
        <div>
          <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-2">VM Sprawl (Stopped VMs)</p>
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead>
                <tr className="border-b border-slate-700/50 text-slate-400">
                  <th className="text-left py-2 pr-3">Server</th>
                  <th className="text-left py-2 pr-3">Power State</th>
                  <th className="text-left py-2">Recommendation</th>
                </tr>
              </thead>
              <tbody>
                {sprawl.map((vm, i) => (
                  <tr key={i} className="border-b border-slate-800/40">
                    <td className="py-1.5 pr-3 font-medium text-slate-200">{vm.server_name}</td>
                    <td className="py-1.5 pr-3 text-orange-400">{vm.power_state}</td>
                    <td className="py-1.5 text-slate-400">{vm.recommendation}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}

// ── BCDR Gap Analysis ─────────────────────────────────────────────────────────
// Function: BcdrPanel
function BcdrPanel({ data }) {
  const s      = data.summary          || {}
  const spofs  = data.spof_servers     || []
  const noBackup = data.servers_no_backup || []
  const rtoGaps  = data.rto_gap_servers || []
  const results  = data.server_results  || []

  const GRADE_COLOR = { A: 'text-emerald-400', B: 'text-green-400', C: 'text-amber-400', D: 'text-orange-400', F: 'text-red-400' }
  return (
    <div className="space-y-5">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <StatBadge label="SPOF Servers" value={s.spof_count ?? 0} color="text-red-400" />
        <StatBadge label="No Backup Agent" value={s.no_backup_agent_count ?? 0} color="text-orange-400" />
        <StatBadge label="RTO Gaps" value={s.rto_gap_count ?? 0} color="text-amber-400" />
        <StatBadge label="Avg Readiness" value={pct(s.avg_readiness_score)} color="text-blue-400" />
      </div>
      {spofs.length > 0 && (
        <div className="p-4 bg-red-950/30 border border-red-700/30 rounded-lg">
          <p className="text-xs font-semibold text-red-400 uppercase tracking-wide mb-2">⚠ Single Points of Failure</p>
          {spofs.map((sp, i) => (
            <div key={i} className="text-xs text-red-300 mb-1">
              <b>{sp.server_name}</b> — {(sp.reasons || []).join(' · ')}
            </div>
          ))}
        </div>
      )}
      <div className="overflow-x-auto">
        <table className="w-full text-xs">
          <thead>
            <tr className="border-b border-slate-700/50 text-slate-400">
              <th className="text-left py-2 pr-3">Server</th>
              <th className="text-center py-2 pr-3">Readiness</th>
              <th className="text-center py-2 pr-3">Backup</th>
              <th className="text-center py-2 pr-3">SPOF</th>
              <th className="text-left py-2">RTO / RPO</th>
            </tr>
          </thead>
          <tbody>
            {results.map((r, i) => (
              <tr key={i} className="border-b border-slate-800/40 hover:bg-slate-800/30">
                <td className="py-1.5 pr-3 font-medium text-slate-200">{r.server_name}</td>
                <td className={`py-1.5 pr-3 text-center font-bold ${
                  GRADE_COLOR[r.readiness_score?.grade] || 'text-slate-400'
                }`}>{r.readiness_score?.grade} ({r.readiness_score?.score})</td>
                <td className={`py-1.5 pr-3 text-center ${
                  r.has_backup_agent ? 'text-emerald-400' : 'text-red-400'
                }`}>{r.has_backup_agent ? '✓' : '✗'}</td>
                <td className={`py-1.5 pr-3 text-center ${
                  r.is_spof ? 'text-red-400 font-bold' : 'text-slate-500'
                }`}>{r.is_spof ? 'SPOF' : '—'}</td>
                <td className="py-1.5 text-slate-400">{r.rto_requirements} / {r.rpo_requirements}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

