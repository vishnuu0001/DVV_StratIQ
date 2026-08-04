// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: InfraRationalization — frontend/src/pages (ExecutionSupportPage.jsx)
// Date: 2025-09-18
// ---------------------------------------------------------------------------
import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Rocket, Cloud, Dna, Clock, Trash2, ChevronDown, ChevronRight,
} from 'lucide-react'
import toast from 'react-hot-toast'
import {
  Field,
  Input,
  Button,
  Badge,
  Text,
  tokens,
} from '@fluentui/react-components'
import AppHeader from '../components/AppHeader.jsx'
import {
  listExecutionRequests, createExecutionRequest, deleteExecutionRequest,
} from '../api/client.js'

const WORKFLOWS = [
  {
    type: 'appliance_deployment',
    icon: Rocket,
    title: 'Scanning Appliance Deployment',
    tagline: 'One-click, agentless discovery appliance into your network',
    description:
      'Deploys a scanning appliance into a customer network with secure connectivity back to this ' +
      'platform, so discovery can run agentlessly against bare metal, VMs, and private/air-gapped ' +
      'environments without installing anything on target systems.',
    notConnected:
      'Provisioning an appliance into a real customer network requires a live target environment and ' +
      'network/cloud credentials this deployment does not have. Submitting a request below records your ' +
      'requirements so this can be scoped and built against a real environment — it does not deploy anything.',
    fields: [
      { key: 'network_description', label: 'Target network description', placeholder: 'e.g. On-prem data center, 3 VLANs, ~400 hosts' },
      { key: 'connectivity_mode', label: 'Preferred connectivity mode', placeholder: 'e.g. Active In-Isolation (export-only) or Embedded Tools (in-firewall)' },
      { key: 'contact', label: 'Contact for scoping this', placeholder: 'Name / email' },
    ],
  },
  {
    type: 'landing_zone',
    icon: Cloud,
    title: 'Cloud Landing Zone Creation',
    tagline: 'Auto-provisioned Azure / AWS / GCP landing zone assets',
    description:
      'Automatically provisions baseline cloud landing-zone resources (networking, IAM boundaries, ' +
      'logging/monitoring baseline) for a migration target — beyond the IaC starter templates already ' +
      'available per-scan (see the Export menu on a scan\'s detail page), which generate reviewable ' +
      'Terraform/ARM/CloudFormation output but do not apply it.',
    notConnected:
      'Actually provisioning real landing-zone resources requires a real cloud account/subscription and ' +
      'credentials this deployment does not have — that step has to run against your own account, not ours. ' +
      'Submitting a request below records your target landing-zone requirements for scoping.',
    fields: [
      { key: 'target_cloud', label: 'Target cloud', placeholder: 'Azure / AWS / GCP / OCI' },
      { key: 'account_or_subscription', label: 'Target account/subscription (if known)', placeholder: 'e.g. Azure subscription name/ID' },
      { key: 'network_requirements', label: 'Network/compliance requirements', placeholder: 'e.g. CIDR ranges, required regions, compliance boundary' },
    ],
  },
  {
    type: 'app_dna_mapping',
    icon: Dna,
    title: 'Application DNA Mapping',
    tagline: 'Dynamic + static analysis of application components and dependencies',
    description:
      'Combines dynamic (runtime) tracing of live workloads with static code analysis to map application ' +
      'components, interfaces, and dependencies in detail — a deeper layer than this module\'s existing ' +
      'network-level dependency mapping (see the Dependencies tab on a scan\'s detail page).',
    notConnected:
      'Dynamic tracing requires instrumenting actually-running workloads in your environment, which this ' +
      'deployment has no access to. Static analysis of source code is already available via the separate ' +
      'CodeAnalysis module in this platform for repos you point it at — this workflow would combine the two. ' +
      'Submitting a request below records which applications/environments you\'d want this scoped against.',
    fields: [
      { key: 'application_name', label: 'Application(s) to map', placeholder: 'e.g. Order Management System' },
      { key: 'runtime_environment', label: 'Where it runs', placeholder: 'e.g. On-prem Kubernetes, 12 services' },
      { key: 'source_repo', label: 'Source repository (if applicable)', placeholder: 'e.g. https://github.com/org/repo' },
    ],
  },
]

// Function: WorkflowCard
function WorkflowCard({ workflow, requests, onSubmit, onDelete }) {
  const [expanded, setExpanded] = useState(false)
  const [form, setForm] = useState({})
  const [submitting, setSubmitting] = useState(false)
  const Icon = workflow.icon
  const myRequests = requests.filter(r => r.request_type === workflow.type)

  // Function: submit
  const submit = async () => {
    setSubmitting(true)
    try {
      await onSubmit(workflow.type, form)
      setForm({})
      toast.success('Request recorded.')
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Failed to submit request.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="rounded-xl border border-slate-700/50 bg-slate-900/50 overflow-hidden">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center gap-3 p-5 text-left hover:bg-slate-800/30 transition-colors"
      >
        <div className="w-10 h-10 rounded-xl bg-brand-green/10 flex items-center justify-center shrink-0">
          <Icon size={18} className="text-brand-green" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <p className="text-sm font-semibold text-white">{workflow.title}</p>
            <span className="px-2 py-0.5 rounded-full text-[10px] font-medium bg-amber-950/40 text-amber-300 border border-amber-700/30">
              Not yet connected to live infrastructure
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-0.5">{workflow.tagline}</p>
        </div>
        {myRequests.length > 0 && (
          <span className="text-xs text-slate-400 shrink-0">{myRequests.length} request{myRequests.length === 1 ? '' : 's'}</span>
        )}
        {expanded ? <ChevronDown size={16} className="text-slate-500 shrink-0" /> : <ChevronRight size={16} className="text-slate-500 shrink-0" />}
      </button>

      {expanded && (
        <div className="px-5 pb-5 space-y-4 border-t border-slate-800 pt-4">
          <p className="text-xs text-slate-400 leading-relaxed">{workflow.description}</p>
          <div className="p-3 rounded-lg bg-amber-950/20 border border-amber-800/30 text-xs text-amber-200 leading-relaxed">
            {workflow.notConnected}
          </div>

          <div className="space-y-2.5">
            {workflow.fields.map(f => (
              <Field key={f.key} label={f.label}>
                <Input
                  value={form[f.key] || ''}
                  onChange={(_, data) => setForm(prev => ({ ...prev, [f.key]: data.value }))}
                  placeholder={f.placeholder}
                />
              </Field>
            ))}
            <Button appearance="primary" onClick={submit} disabled={submitting}>
              {submitting ? 'Submitting…' : 'Submit requirement'}
            </Button>
          </div>

          {myRequests.length > 0 && (
            <div className="space-y-2 pt-2">
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide">Submitted requests</p>
              {myRequests.map(r => (
                <div key={r.id} className="flex items-start justify-between gap-3 p-3 rounded-lg bg-slate-900/40 border border-slate-800">
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-1.5 text-[11px] text-slate-500">
                      <Clock size={11} />
                      {new Date(r.submitted_at).toLocaleString()}
                      <span className="px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 ml-1">{r.status}</span>
                    </div>
                    <div className="mt-1 space-y-0.5">
                      {Object.entries(r.details || {}).filter(([, v]) => v).map(([k, v]) => (
                        <p key={k} className="text-xs text-slate-300">
                          <span className="text-slate-500">{k.replace(/_/g, ' ')}:</span> {v}
                        </p>
                      ))}
                    </div>
                  </div>
                  <button
                    onClick={() => onDelete(r.id)}
                    className="text-slate-500 hover:text-red-400 transition-colors shrink-0"
                    title="Remove"
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

// Function: ExecutionSupportPage
export default function ExecutionSupportPage() {
  const navigate = useNavigate()
  const [requests, setRequests] = useState([])
  const [loading, setLoading] = useState(true)

  // Function: load
  const load = async () => {
    try {
      const data = await listExecutionRequests()
      setRequests(data.requests || [])
    } catch {
      // non-fatal — page still works for submitting new requests
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  // Function: handleSubmit
  const handleSubmit = async (type, details) => {
    await createExecutionRequest(type, details)
    await load()
  }

  // Function: handleDelete
  const handleDelete = async (id) => {
    await deleteExecutionRequest(id)
    await load()
  }

  return (
    <div className="min-h-screen bg-surface">
      <AppHeader
        title="Execution Support"
        subtitle="Appliance deployment, landing zones, and application DNA mapping"
        backTo="/"
      />
      <main className="max-w-4xl mx-auto px-5 py-8 space-y-5">
        <div>
          <h2 className="text-xl font-semibold text-white">Execution & Provisioning Workflows</h2>
          <p className="text-slate-400 text-sm mt-1 max-w-2xl">
            These three workflows need a real target environment and/or cloud credentials to actually do
            anything — they're not simulated here. Each card explains exactly what's connected today and
            lets you record your requirements for when it is.
          </p>
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-16">
            <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-brand-green border-r-transparent" />
          </div>
        ) : (
          <div className="space-y-3">
            {WORKFLOWS.map(w => (
              <WorkflowCard
                key={w.type}
                workflow={w}
                requests={requests}
                onSubmit={handleSubmit}
                onDelete={handleDelete}
              />
            ))}
          </div>
        )}
      </main>
    </div>
  )
}
