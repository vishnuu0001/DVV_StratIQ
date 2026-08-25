// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: Modernization — frontend/src/pages (ProjectsPage.jsx)
// Date: 2026-07-14
// ---------------------------------------------------------------------------
import { useContext, useEffect, useMemo, useRef, useState } from 'react'
import toast from 'react-hot-toast'
import { Archive, CheckCircle2, ChevronRight, ClipboardList, Code2, Download, FileDiff, FolderKanban, FolderOpen, MessageSquareText, Play, RotateCcw, ScanSearch, ShieldCheck, Trash2, Upload, X, XCircle } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import Layout from '../components/Layout.jsx'
import { AppContext } from '../App.jsx'
import {
  analyzeProject, approveProjectRelease, compareSnapshots, createProject, decideProjectSnapshot, deleteProject,
  filterUploadFiles,
  generateProjectPlan, getComparisonExportUrl, getProject, getProjectJobs, getProjectQualityGate, getReleaseExportUrl, getSnapshotArtifact, getTargetStacks, getToolchainStatus, getToolchainInstallStatus, installToolchain,
  listProjects, purgeProjectSnapshots, restoreProjectSnapshot, reviseProjectPlan, startPromptAnalysis, submitProjectReview, transformProject,
  uploadFolder,
  validateProjectContracts,
} from '../api/client.js'

const FALLBACK_STACKS = [
  { id: 'dotnet8_blazor', engine_target: 'dotnet8_blazor', name: '.NET 8 Blazor Server + SQL Server', category: 'Csharp', native: true },
  { id: 'spring_boot_react', engine_target: 'spring_boot_react', name: 'Spring Boot + React + PostgreSQL', category: 'Java', native: true },
  { id: 'python_fastapi', engine_target: 'python_fastapi', name: 'FastAPI + SQLAlchemy + PostgreSQL', category: 'Python', native: true },
]
const STEPS = ['Uploaded', 'Analyzed', 'Plan Generated', 'Plan Reviewed', 'Plan Approved', 'Transformation Running', 'Validation Running', 'Review Required', 'Approved', 'Exported']
const TABS = ['Overview', 'Analysis', 'Plan', 'Contracts', 'Compare', 'Validation & Release', 'History']
const fieldClass = 'w-full rounded-sm border border-hairline bg-bg px-3 py-2.5 text-sm text-ink outline-none focus:border-gold/50'
const buttonClass = 'rounded-sm border border-hairline bg-white/[0.03] px-4 py-2 text-sm font-medium text-ink transition hover:bg-white/[0.08] disabled:cursor-not-allowed disabled:opacity-35'
const EMPTY_PLAN_EDIT = { excluded_modules: '', manual_tasks: '', risks_and_assumptions: '', target_technologies: '', architecture_style: '', deployment_approach: '', cutover_approach: '', rollback_approach: '', database: '', auth_approach: '' }

// Function: editablePlan
function editablePlan(plan = {}) {
  return {
    excluded_modules: (plan.excluded_modules || []).join('\n'),
    manual_tasks: (plan.manual_tasks || []).join('\n'),
    risks_and_assumptions: (plan.risks_and_assumptions || []).map(value => typeof value === 'string' ? value : JSON.stringify(value)).join('\n'),
    target_technologies: (plan.target_technologies || []).join(', '),
    architecture_style: plan.target_architecture?.style || '',
    deployment_approach: plan.deployment_approach || '',
    cutover_approach: plan.cutover_approach || '',
    rollback_approach: plan.rollback_approach || '',
    database: plan.target_architecture?.database || '',
    auth_approach: plan.auth_approach || '',
  }
}

// Function: Section
function Section({ title, children, action }) {
  return <section className="rounded-sm border border-hairline bg-surface p-5">
    <div className="mb-4 flex items-center justify-between gap-3"><h3 className="text-sm font-semibold text-ink">{title}</h3>{action}</div>{children}
  </section>
}

// Function: Value
function Value({ label, value }) {
  return <div className="min-w-0"><dt className="text-[11px] uppercase tracking-wide text-ink-faint">{label.replaceAll('_', ' ')}</dt><dd className="mt-1 min-w-0 break-words text-sm text-ink"><StructuredValue value={value} /></dd></div>
}

// Function: StructuredValue
function StructuredValue({ value }) {
  if (value == null || value === '') return <span className="text-ink-muted">Not identified</span>
  if (typeof value === 'string' || typeof value === 'number' || typeof value === 'boolean') return <span className="whitespace-pre-wrap leading-6">{String(value)}</span>
  if (Array.isArray(value)) {
    if (!value.length) return <span className="text-ink-muted">None identified</span>
    return <ul className="space-y-1.5">{value.map((item, index) => <li key={index} className="flex gap-2"><span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-gold/70" /><div className="min-w-0 flex-1"><StructuredValue value={item} /></div></li>)}</ul>
  }
  return <dl className="min-w-0 space-y-3">{Object.entries(value).map(([key, nested]) => <Value key={key} label={key} value={nested} />)}</dl>
}

// Function: ObjectGrid
function ObjectGrid({ value, empty = 'No information identified.' }) {
  if (value == null || value === '' || (Array.isArray(value) && !value.length) || (typeof value === 'object' && !Array.isArray(value) && !Object.keys(value).length)) return <p className="text-sm text-ink-muted">{empty}</p>
  if (typeof value !== 'object') return <div className="rounded-sm border border-hairline bg-bg p-4 text-sm text-ink"><StructuredValue value={value} /></div>
  if (Array.isArray(value)) return <div className="space-y-2">{value.map((item, i) => <div key={i} className="rounded-sm border border-hairline bg-bg p-3 text-sm text-ink"><StructuredValue value={item} /></div>)}</div>
  return <dl className="grid min-w-0 gap-4 2xl:grid-cols-2">{Object.entries(value).map(([k, v]) => <Value key={k} label={k} value={v} />)}</dl>
}

// Function: ValidationResults
function ValidationResults({ value }) {
  if (!value) return <p className="text-sm text-ink-muted">Transformation validation has not completed.</p>
  const build = value.build
  const errors = Object.entries(build?.remaining_errors || {})
  return <div className="space-y-5">
    <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
      {[['Checked', value.checked], ['Passed', value.passed], ['Failed', value.failed], ['Retried', value.retried]].map(([label, count]) =>
        <div key={label} className="rounded-sm border border-hairline bg-bg p-4"><p className="text-[11px] uppercase text-ink-faint">{label}</p><p className="mt-1 text-2xl font-semibold text-ink">{count ?? 0}</p></div>)}
    </div>
    <div className="grid gap-3 sm:grid-cols-2">
      <div className="rounded-sm border border-emerald-500/20 bg-emerald-500/[0.04] p-3"><p className="text-[11px] uppercase text-ink-faint">Strict compiler/parser checks</p><p className="mt-1 text-sm font-semibold text-emerald-300">{value.strict_passed ?? 0} / {value.strict_checked ?? 0} passed</p></div>
      <div className="rounded-sm border border-hairline bg-bg p-3"><p className="text-[11px] uppercase text-ink-faint">Advisory document checks</p><p className="mt-1 text-sm text-ink-muted">{value.advisory_checked ?? 0} checked · never substitutes for compilation</p></div>
    </div>
    <div className={`rounded-sm border p-4 ${build?.passed ? 'border-emerald-500/25 bg-emerald-500/[0.04]' : 'border-red-500/25 bg-red-500/[0.04]'}`}>
      <div className="flex flex-wrap items-center justify-between gap-2">
        <p className="text-sm font-semibold text-ink">Whole-project production build</p>
        <span className={`text-xs font-semibold ${build?.passed ? 'text-emerald-300' : 'text-red-300'}`}>{build ? (build.passed ? 'PASSED' : 'FAILED') : 'NOT RUN'}</span>
      </div>
      {build?.checker && <p className="mt-1 text-xs text-ink-muted">Checker: {build.checker}</p>}
    </div>
    {!!errors.length && <div className="space-y-3">
      <h4 className="text-xs font-semibold uppercase tracking-wide text-red-300">Remaining errors ({errors.length} groups)</h4>
      {errors.map(([path, diagnostics]) => <div key={path} className="min-w-0 rounded-sm border border-red-500/20 bg-bg p-4">
        <p className="break-all font-mono text-xs font-semibold text-gold">{path === '<build>' ? 'Project / toolchain' : path === '<dependency-compatibility>' ? 'Dependency compatibility' : path}</p>
        <ul className="mt-3 space-y-2">{diagnostics.map((diagnostic, index) => <li key={index} className="flex min-w-0 gap-2 text-sm text-ink-muted"><span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-red-400" /><pre className="min-w-0 flex-1 whitespace-pre-wrap break-words font-mono text-xs leading-5">{diagnostic}</pre></li>)}</ul>
      </div>)}
    </div>}
    {!!value.files?.length && <Section title="File validation details"><ObjectGrid value={value.files} /></Section>}
  </div>
}

// Function: ProjectsPage
export default function ProjectsPage() {
  const navigate = useNavigate()
  const { authUser } = useContext(AppContext)
  const [projects, setProjects] = useState([]); const [selected, setSelected] = useState(null)
  const [tab, setTab] = useState('Overview'); const [busy, setBusy] = useState(false)
  const [uploadedSourceLabel, setUploadedSourceLabel] = useState('')
  const [uploadingSource, setUploadingSource] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const sourceFolderInputRef = useRef(null)
  const [form, setForm] = useState({ origin_mode: 'existing_source', name: '', source_path: '', project_prompt: '', customer: '', application_key: '', application_owner: '', business_unit: '', business_criticality: 'Medium', target_stack: 'dotnet8_blazor', custom_stack_name: '', retention_days: 365, description: '', language: '', framework: '', runtime: '', frontend: '', database: '', architecture: '', deployment: '', dependency_versions: '', custom_instructions: '' })
  const [stacks, setStacks] = useState(FALLBACK_STACKS)
  const [artifacts, setArtifacts] = useState({}); const [planEdit, setPlanEdit] = useState(EMPTY_PLAN_EDIT)
  const [left, setLeft] = useState(''); const [right, setRight] = useState(''); const [comparison, setComparison] = useState(null); const [contractResult, setContractResult] = useState(null)
  const [activeJob, setActiveJob] = useState(null)
  const [reviewFeedback, setReviewFeedback] = useState('')
  const [qualityGate, setQualityGate] = useState(null)
  const [toolchains, setToolchains] = useState(null)
  const [installingTool, setInstallingTool] = useState('')
  const [deletingProject, setDeletingProject] = useState('')

  // Function: latest
  const latest = (kind) => selected?.snapshots?.find(item => item.kind === kind)
  const eligibleSnapshots = selected?.snapshots?.filter(s => ['source', 'outputs', 'approved'].includes(s.kind)) || []
  const stepIndex = Math.max(0, STEPS.indexOf(selected?.status))

  // Function: refresh
  const refresh = async (id, preserveTab = true) => {
    const result = await listProjects(); setProjects(result.projects || [])
    if (id || selected?.id) { const project = await getProject(id || selected.id); setSelected(project); if (!preserveTab) setTab('Overview'); return project }
  }
  // Function: removeProject
  const removeProject = async (project) => {
    if (!window.confirm(`Delete ${project.id} · ${project.name}? Its snapshots and generated outputs will be removed from the governed workspace.`)) return
    setDeletingProject(project.id)
    try {
      await deleteProject(project.id)
      const result = await listProjects()
      setProjects(result.projects || [])
      if (selected?.id === project.id) {
        setSelected(null); setArtifacts({}); setComparison(null); setActiveJob(null); setTab('Overview')
      }
      toast.success(`${project.id} deleted`)
    } catch (error) {
      toast.error(error?.response?.data?.detail || error.message)
    } finally {
      setDeletingProject('')
    }
  }
  useEffect(() => { refresh().catch(() => toast.error('Could not load governed projects')); getTargetStacks().then(data => setStacks([...(data.stacks || []), { id: 'custom', engine_target: 'custom', name: 'Define my own technology stack', category: 'Custom', native: false }])).catch(() => {}); getToolchainStatus().then(setToolchains).catch(() => {}) }, []) // eslint-disable-line react-hooks/exhaustive-deps
  useEffect(() => {
    if (!selected?.id) { setActiveJob(null); return undefined }
    let cancelled = false
    // Function: poll
    const poll = async () => {
      try {
        const sourcePath = latest('source')?.path || ''
        const result = await getProjectJobs(selected.id, sourcePath)
        if (!cancelled) setActiveJob(result.jobs?.[0] || null)
        if (!cancelled && result.jobs?.[0]?.status === 'completed' && selected.status === 'Transformation Running') {
          setSelected(await getProject(selected.id))
        }
      } catch { /* project history remains available if polling is interrupted */ }
    }
    poll()
    const timer = window.setInterval(poll, selected.status === 'Transformation Running' ? 2000 : 10000)
    return () => { cancelled = true; window.clearInterval(timer) }
  }, [selected?.id, selected?.status])

  const selectedStack = form.target_stack === 'custom'
    ? { id: 'custom', engine_target: 'custom', name: form.custom_stack_name || 'Custom technology stack', category: 'Custom', native: false }
    : stacks.find(stack => stack.id === form.target_stack) || stacks[0]
  const isCustomStack = selectedStack?.engine_target === 'custom'
  const requiresCustomStackDefinition = selectedStack?.id === 'custom' && form.origin_mode === 'existing_source'
  // Function: chooseLocalSourceFolder
  const chooseLocalSourceFolder = () => sourceFolderInputRef.current?.click()
  // Function: handleLocalSourceFolder
  const handleLocalSourceFolder = async (event) => {
    const rawFiles = Array.from(event.target.files || [])
    event.target.value = ''
    if (!rawFiles.length) return
    const files = filterUploadFiles(rawFiles)
    if (!files.length) {
      toast.error('That folder only contains excluded files (node_modules, .git, build output, …)')
      return
    }
    const folderName = (rawFiles[0].webkitRelativePath || '').split('/')[0] || 'Selected folder'
    setUploadingSource(true); setUploadProgress(0)
    try {
      const uploaded = await uploadFolder(files, setUploadProgress)
      setForm(current => ({
        ...current,
        name: current.name || folderName,
        source_path: uploaded.path,
      }))
      setUploadedSourceLabel(`${folderName} · ${uploaded.file_count} files ready`)
      toast.success(`${folderName} uploaded securely`)
    } catch (error) {
      toast.error(error?.response?.data?.detail || error.message || 'Folder upload failed')
    } finally {
      setUploadingSource(false)
    }
  }
  // Function: clearLocalSourceFolder
  const clearLocalSourceFolder = () => {
    setUploadedSourceLabel('')
    setForm(current => ({ ...current, source_path: '' }))
  }
  // Function: installPrerequisite
  const installPrerequisite = async (toolId) => {
    setInstallingTool(toolId)
    try {
      const started = await installToolchain(toolId)
      if (started.status !== 'completed' && started.job_id) {
        let result = started
        while (['queued', 'running'].includes(result.status)) {
          await new Promise(resolve => window.setTimeout(resolve, 2000))
          result = await getToolchainInstallStatus(started.job_id)
        }
        if (result.status !== 'completed') throw new Error(result.message || 'Installation failed')
      }
      setToolchains(await getToolchainStatus())
      toast.success('Prerequisite installed and readiness rechecked')
    } catch (error) { toast.error(error?.response?.data?.detail || error.message) }
    finally { setInstallingTool('') }
  }
  // Function: customStackDescription
  const customStackDescription = () => {
    const values = selectedStack && selectedStack.id !== 'custom'
      ? [`Preset: ${selectedStack.name}`, `Language: ${selectedStack.language || ''}`, `Backend: ${selectedStack.backend || ''}`, `Frontend: ${selectedStack.frontend || ''}`, `Database: ${selectedStack.database || ''}`]
      : [form.custom_stack_name && `Custom stack name: ${form.custom_stack_name}`]
    values.push(form.language && `Language: ${form.language}`, form.framework && `Framework/backend: ${form.framework}`,
      form.runtime && `Runtime/version: ${form.runtime}`, form.frontend && `Frontend: ${form.frontend}`,
      form.database && `Database/data access: ${form.database}`, form.architecture && `Architecture: ${form.architecture}`,
      form.deployment && `Deployment: ${form.deployment}`, form.dependency_versions && `Dependency versions: ${form.dependency_versions}`,
      form.custom_instructions && `Requirements: ${form.custom_instructions}`)
    return values.filter(Boolean).join('; ')
  }

  // Function: submitCreation
  const submitCreation = async (event) => {
    event.preventDefault()
    if (selectedStack?.available === false) {
      toast.error(selectedStack.blocked_reason || 'This target is not strictly validatable on the current build host')
      return
    }
    if (form.origin_mode !== 'single_file' && selectedStack?.project_ready === false) {
      toast.error('This target currently has strict single-file validation, but no production-grade whole-project dependency/build route on this host')
      return
    }
    setBusy(true)
    try {
      if (form.origin_mode === 'single_file') {
        const result = await startPromptAnalysis(
          form.project_prompt.trim(), [], selectedStack?.engine_target || form.target_stack,
          isCustomStack ? customStackDescription() : '', 'single_file',
        )
        toast.success('Single-file generation started')
        navigate(`/jobs/${result.job_id}`)
        return
      }
      const payload = { name: form.name, source_path: form.origin_mode === 'existing_source' ? form.source_path : undefined, project_prompt: form.origin_mode === 'prompt' ? form.project_prompt : undefined, retention_days: Number(form.retention_days), configuration: { origin_mode: form.origin_mode, source_display_name: form.origin_mode === 'existing_source' ? uploadedSourceLabel.split(' · ')[0] : '', project_prompt: form.origin_mode === 'prompt' ? form.project_prompt : '', application_name: form.name, application_key: form.application_key, client_name: form.customer, customer: form.customer, application_owner: form.application_owner, business_unit: form.business_unit, business_criticality: form.business_criticality, target_stack: form.target_stack, target_stack_name: form.target_stack === 'custom' ? (form.custom_stack_name || (form.origin_mode === 'prompt' ? 'Inferred from project prompt' : '')) : selectedStack?.name, engine_target: selectedStack?.engine_target || form.target_stack, custom_stack_desc: isCustomStack ? customStackDescription() : '', language: form.language || selectedStack?.language, framework: form.framework || selectedStack?.backend, runtime: form.runtime, frontend: form.frontend || selectedStack?.frontend, database: form.database || selectedStack?.database, architecture: form.architecture, deployment: form.deployment, dependency_versions: form.dependency_versions, custom_instructions: form.custom_instructions, description: form.description } }
      const project = await createProject(payload); await refresh(project.id, false)
      toast.success(form.origin_mode === 'prompt' ? `${project.id} project brief captured` : `${project.id} source captured`)
    } catch (error) { toast.error(error?.response?.data?.detail || error.message) }
    finally { setBusy(false) }
  }

  // Function: execute
  const execute = async (operation, message, nextTab) => {
    setBusy(true)
    try { const result = await operation(); await refresh(selected?.id); if (nextTab) setTab(nextTab); toast.success(message); return result }
    catch (error) { toast.error(error?.response?.data?.detail || error.message) }
    finally { setBusy(false) }
  }
  // Function: generatePlanFromAnalysis
  const generatePlanFromAnalysis = () => execute(
    () => generateProjectPlan(
      selected.id,
      selected.configuration?.engine_target || selected.configuration?.target_stack || form.target_stack,
      selected.configuration?.custom_stack_desc || '',
    ),
    'Plan and canonical contracts generated',
    'Plan',
  )
  // Function: planRevisionPayload
  const planRevisionPayload = decisionsConfirmed => ({
    target_technologies: String(planEdit.target_technologies || '').split(',').map(value => value.trim()).filter(Boolean),
    target_architecture: {
      style: String(planEdit.architecture_style || '').trim(),
      database: String(planEdit.database || '').trim(),
    },
    deployment_approach: String(planEdit.deployment_approach || '').trim(),
    auth_approach: String(planEdit.auth_approach || '').trim(),
    cutover_approach: String(planEdit.cutover_approach || '').trim(),
    rollback_approach: String(planEdit.rollback_approach || '').trim(),
    excluded_modules: String(planEdit.excluded_modules || '').split('\n').map(value => value.trim()).filter(Boolean),
    risks_and_assumptions: String(planEdit.risks_and_assumptions || '').split('\n').map(value => value.trim()).filter(Boolean),
    manual_tasks: String(planEdit.manual_tasks || '').split('\n').map(value => value.trim()).filter(Boolean),
    decisions_confirmed: decisionsConfirmed,
  })

  // Function: loadArtifact
  const loadArtifact = async (kind) => {
    const snapshot = latest(kind); if (!snapshot) return
    if (artifacts[snapshot.id]) return artifacts[snapshot.id]
    try {
      const result = await getSnapshotArtifact(selected.id, snapshot.id)
      setArtifacts(old => ({ ...old, [snapshot.id]: result.artifact }))
      if (kind === 'plans') {
        setPlanEdit(editablePlan(result.artifact))
      }
      return result.artifact
    } catch (error) { toast.error(error?.response?.data?.detail || error.message) }
  }
  useEffect(() => { if (tab === 'Analysis') loadArtifact('analysis'); if (tab === 'Plan') loadArtifact('plans'); if (tab === 'Contracts') loadArtifact('contracts'); if (tab === 'Validation & Release') { loadArtifact('validation'); const output = latest('outputs'); if (output) getProjectQualityGate(selected.id, output.id).then(setQualityGate).catch(() => setQualityGate(null)) } }, [tab, selected?.id, selected?.snapshots?.[0]?.id]) // eslint-disable-line react-hooks/exhaustive-deps

  const analysisArtifact = latest('analysis') ? artifacts[latest('analysis').id] : null
  const plan = latest('plans') ? artifacts[latest('plans').id] : null
  const contracts = latest('contracts') ? artifacts[latest('contracts').id] : null
  const validation = latest('validation') ? artifacts[latest('validation').id] : null
  const semantic = analysisArtifact?.semantic_index
  const analysisDisplay = analysisArtifact?.analysis ? {
    ...analysisArtifact.analysis,
    folder_path: selected?.configuration?.source_display_name || 'Governed source snapshot (internal path hidden)',
  } : null
  const isPromptProject = selected?.configuration?.origin_mode === 'prompt'
  const displayedPlan = plan ? {
    ...plan,
    current_state_architecture: selected?.configuration?.origin_mode === 'prompt' && typeof plan.current_state_architecture !== 'object'
      ? { project_origin: 'Greenfield application from governed prompt', business_context: plan.current_state_architecture, current_architecture: 'No existing architecture; the approved brief is the baseline.' }
      : plan.current_state_architecture,
    target_architecture: { ...(plan.target_architecture || {}), ...Object.fromEntries(Object.entries({
      target_name: selected?.configuration?.target_stack_name,
      language: selected?.configuration?.language, framework: selected?.configuration?.framework,
      runtime: selected?.configuration?.runtime, frontend: selected?.configuration?.frontend,
      database: selected?.configuration?.database, style: selected?.configuration?.architecture,
      deployment: selected?.configuration?.deployment,
    }).filter(([, value]) => value !== undefined && value !== null && value !== '')) },
    source_technologies: plan.source_technologies?.length ? plan.source_technologies
      : selected?.configuration?.origin_mode === 'prompt' ? ['Greenfield – no legacy source technology stack'] : plan.source_technologies,
  } : null
  const snapshotCounts = useMemo(() => (selected?.snapshots || []).reduce((a, s) => ({ ...a, [s.kind]: (a[s.kind] || 0) + 1 }), {}), [selected])

  return <Layout><main className="mx-auto max-w-[1500px] p-5 lg:p-8">
    <div className="mb-7"><h1 className="text-2xl font-semibold text-ink">Governed projects</h1><p className="mt-2 text-sm text-ink-muted">Plan, transform, review and release modernization work with a complete audit trail.</p></div>
    <div className="grid gap-5 xl:grid-cols-[350px_minmax(0,1fr)]">
      <aside className="space-y-4">
        <Section title="Create project or code">
          <form className="space-y-3" onSubmit={submitCreation}>
            <div className="grid grid-cols-3 rounded-sm border border-hairline bg-bg p-1">
              <button type="button" onClick={() => setForm({ ...form, origin_mode: 'existing_source' })} className={`rounded-sm px-3 py-2 text-xs font-semibold ${form.origin_mode === 'existing_source' ? 'bg-gold text-bg' : 'text-ink-muted'}`}>Modernize existing</button>
              <button type="button" onClick={() => setForm({ ...form, origin_mode: 'prompt' })} className={`rounded-sm px-3 py-2 text-xs font-semibold ${form.origin_mode === 'prompt' ? 'bg-gold text-bg' : 'text-ink-muted'}`}>Full project</button>
              <button type="button" onClick={() => setForm({ ...form, origin_mode: 'single_file' })} className={`rounded-sm px-3 py-2 text-xs font-semibold ${form.origin_mode === 'single_file' ? 'bg-gold text-bg' : 'text-ink-muted'}`}>Single file</button>
            </div>
            {form.origin_mode !== 'single_file' && <><input required className={fieldClass} placeholder="Project name *" value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} />
              <textarea className={fieldClass} rows="2" placeholder="Business purpose and scope" value={form.description} onChange={e => setForm({ ...form, description: e.target.value })} />
              <div className="grid grid-cols-2 gap-2"><input className={fieldClass} placeholder="Client name" value={form.customer} onChange={e => setForm({ ...form, customer: e.target.value })} /><input className={fieldClass} placeholder="Application key (auto if blank)" value={form.application_key} onChange={e => setForm({ ...form, application_key: e.target.value.replace(/[^A-Za-z0-9-]/g, '').toUpperCase() })} /></div>
              <div className="grid grid-cols-2 gap-2"><input className={fieldClass} placeholder="Application owner" value={form.application_owner} onChange={e => setForm({ ...form, application_owner: e.target.value })} /><input className={fieldClass} placeholder="Business unit" value={form.business_unit} onChange={e => setForm({ ...form, business_unit: e.target.value })} /></div>
              <div className="grid grid-cols-2 gap-2"><select className={fieldClass} value={form.business_criticality} onChange={e => setForm({ ...form, business_criticality: e.target.value })}><option>Low</option><option>Medium</option><option>High</option><option>Mission critical</option></select><input type="number" min="1" className={fieldClass} title="Retention days" value={form.retention_days} onChange={e => setForm({ ...form, retention_days: e.target.value })} /></div></>}
            <label className="block text-[11px] uppercase tracking-wide text-ink-faint">Target technology stack
              <div className="mt-2 flex gap-2">
                <select className={fieldClass} value={form.target_stack} onChange={e => setForm({ ...form, target_stack: e.target.value })}>
                  <option value="custom">＋ Custom technology stack — enter my own</option>
                  {[...new Set(stacks.filter(s => s.id !== 'custom').map(s => s.category))].map(category => <optgroup key={category} label={category}>{stacks.filter(s => s.id !== 'custom' && s.category === category).map(stack => <option key={stack.id} value={stack.id}>{stack.name}{stack.native ? ' · Engine native' : ' · Guided'}{stack.available === false ? ' · Prerequisite required' : stack.project_ready === false ? ' · Single-file validation only' : stack.full_generation === false ? ' · Validation only, no full-project generation yet' : ''}</option>)}</optgroup>)}
                </select>
                {form.target_stack !== 'custom' && <button type="button" className="shrink-0 rounded-sm border border-gold/30 bg-gold/[0.06] px-3 text-xs font-semibold text-gold hover:bg-gold/[0.12]" onClick={() => setForm({ ...form, target_stack: 'custom' })}>Custom entry</button>}
              </div>
            </label>
            {selectedStack?.available === false && <p className="rounded-sm border border-amber-500/25 bg-amber-500/[0.05] px-3 py-2 text-[11px] leading-5 text-amber-200">{selectedStack.blocked_reason}. The stack remains listed for planning visibility, but generation is blocked until strict validation is available.</p>}
            {selectedStack?.available !== false && selectedStack?.project_ready === false && form.origin_mode !== 'single_file' && <p className="rounded-sm border border-amber-500/25 bg-amber-500/[0.05] px-3 py-2 text-[11px] leading-5 text-amber-200">This host can strictly validate individual {selectedStack.language} files, but it has no registered dependency-aware whole-project build route for this stack. Use Single file or select a project-ready stack.</p>}
            {toolchains && <details className={`rounded-sm border p-3 ${toolchains.ready ? 'border-emerald-500/20 bg-emerald-500/[0.04]' : 'border-amber-500/20 bg-amber-500/[0.04]'}`}>
              <summary className="cursor-pointer list-none">
              <p className="text-xs font-semibold text-ink">Build prerequisites {toolchains.ready ? 'ready' : 'need attention'}</p>
              <p className="mt-1 text-[11px] leading-5 text-ink-muted">.NET SDKs: {toolchains.tools?.dotnet?.versions?.join(', ') || 'missing'} · Node/npm: {toolchains.tools?.npm?.ready ? 'ready' : 'missing'} · Java/JVM build: {toolchains.tools?.java?.ready && (toolchains.tools?.maven?.ready || toolchains.tools?.gradle?.ready) ? 'ready' : 'missing'} · Python: {toolchains.tools?.python?.ready ? 'ready' : 'missing'} · Go: {toolchains.tools?.go?.ready ? 'ready' : 'missing'} · PHP/Ruby: {toolchains.tools?.php?.ready && toolchains.tools?.ruby?.ready ? 'ready' : 'missing'} · C/C++: {toolchains.tools?.c?.ready && toolchains.tools?.cpp?.ready ? 'ready' : 'missing'} · COBOL: {toolchains.tools?.cobol?.ready ? 'ready' : 'missing'}</p>
              </summary>
              <div className="mt-3 space-y-2 border-t border-hairline pt-3">
                {(toolchains.catalog || []).map(item => <div key={item.id} className="flex items-center justify-between gap-3 rounded-sm bg-bg px-3 py-2">
                  <div><p className="text-xs text-ink">{item.name}</p><p className={`text-[10px] ${item.installed ? 'text-emerald-300' : 'text-amber-300'}`}>{item.installed ? 'Installed and detected' : 'Missing'}</p></div>
                  {!item.installed && item.installable && authUser?.role === 'admin' && <button type="button" disabled={!!installingTool} onClick={() => installPrerequisite(item.id)} className="rounded-sm border border-gold/30 px-3 py-1.5 text-[11px] font-semibold text-gold disabled:opacity-40">{installingTool === item.id ? 'Installing…' : 'Install'}</button>}
                  {!item.installed && authUser?.role !== 'admin' && <span className="text-[10px] text-ink-faint">Administrator installation required</span>}
                  {!item.installed && !item.installable && authUser?.role === 'admin' && <span className="text-[10px] text-ink-faint">Manual server installation required</span>}
                </div>)}
              </div>
            </details>}
            {isCustomStack && <div className="space-y-3 rounded-sm border border-gold/20 bg-gold/[0.03] p-3">
              <div><p className="text-xs font-semibold text-gold">Custom stack overrides</p><p className="mt-1 text-[11px] text-ink-faint">{form.origin_mode === 'prompt' ? 'Optional. Leave these fields blank to infer the complete technology stack from your project prompt.' : 'Define the target stack for the existing source, or add constraints that override inferred values.'}</p></div>
              {selectedStack?.id === 'custom' && <input required={requiresCustomStackDefinition} className={fieldClass} placeholder={requiresCustomStackDefinition ? 'Custom stack name * (e.g. Go 1.23 + Svelte 5 + CockroachDB)' : 'Custom stack name (optional — inferred from prompt)'} value={form.custom_stack_name} onChange={e => setForm({ ...form, custom_stack_name: e.target.value })} />}
              <div className="grid grid-cols-2 gap-2"><input required={requiresCustomStackDefinition} className={fieldClass} placeholder={requiresCustomStackDefinition ? 'Language *' : 'Language (optional)'} value={form.language} onChange={e => setForm({ ...form, language: e.target.value })} /><input required={requiresCustomStackDefinition} className={fieldClass} placeholder={requiresCustomStackDefinition ? 'Framework / backend *' : 'Framework / backend (optional)'} value={form.framework} onChange={e => setForm({ ...form, framework: e.target.value })} /></div>
              <div className="grid grid-cols-2 gap-2"><input className={fieldClass} placeholder="Runtime and version" value={form.runtime} onChange={e => setForm({ ...form, runtime: e.target.value })} /><input className={fieldClass} placeholder="Frontend technology" value={form.frontend} onChange={e => setForm({ ...form, frontend: e.target.value })} /></div>
              <div className="grid grid-cols-2 gap-2"><input className={fieldClass} placeholder="Database / data access" value={form.database} onChange={e => setForm({ ...form, database: e.target.value })} /><input className={fieldClass} placeholder="Architecture style" value={form.architecture} onChange={e => setForm({ ...form, architecture: e.target.value })} /></div>
              <input className={fieldClass} placeholder="Deployment (VM, Docker, Kubernetes, IIS...)" value={form.deployment} onChange={e => setForm({ ...form, deployment: e.target.value })} />
              <textarea className={fieldClass} rows="2" placeholder="Required dependency and platform versions" value={form.dependency_versions} onChange={e => setForm({ ...form, dependency_versions: e.target.value })} />
              <textarea className={fieldClass} rows="3" placeholder="Coding standards, libraries, constraints and additional instructions" value={form.custom_instructions} onChange={e => setForm({ ...form, custom_instructions: e.target.value })} />
            </div>}
            {form.origin_mode === 'existing_source' ? <>
              <input ref={sourceFolderInputRef} type="file" webkitdirectory="" directory="" multiple onChange={handleLocalSourceFolder} className="hidden" />
              <div className="flex gap-2">
                <button type="button" disabled={uploadingSource} onClick={chooseLocalSourceFolder} className={`${fieldClass} flex min-w-0 items-center gap-2 text-left disabled:opacity-50`}>
                  <FolderOpen className="h-4 w-4 shrink-0 text-gold" />
                  <span className={`min-w-0 flex-1 truncate ${uploadedSourceLabel ? 'text-ink' : 'text-ink-faint'}`}>{uploadedSourceLabel || 'Select a project folder from this computer *'}</span>
                </button>
                {uploadedSourceLabel && !uploadingSource && <button type="button" title="Clear selected folder" className={buttonClass} onClick={clearLocalSourceFolder}><X className="h-4 w-4" /></button>}
              </div>
              {uploadingSource && <div><div className="h-1.5 overflow-hidden rounded-full bg-black/10"><div className="h-full bg-gold transition-all" style={{ width: `${Math.max(3, Math.round(uploadProgress * 100))}%` }} /></div><p className="mt-1 text-[11px] text-ink-muted"><Upload className="mr-1 inline h-3 w-3" />Uploading local folder… {Math.round(uploadProgress * 100)}%</p></div>}
              <p className="text-[11px] leading-4 text-ink-faint">Choose a folder from your computer. Files are securely copied into an immutable internal snapshot; your original folder is never modified.</p>
            </> : <>
              <textarea required rows="8" className={fieldClass} placeholder={form.origin_mode === 'single_file' ? 'Describe one complete file to generate: file type/name, purpose, inputs, outputs, dependencies, error handling and acceptance criteria *' : 'Describe the application to build: users, business capabilities, screens, APIs, data model, integrations, security, reports, tests and acceptance criteria *'} value={form.project_prompt} onChange={e => setForm({ ...form, project_prompt: e.target.value })} />
              <p className="text-[11px] leading-4 text-ink-faint">{form.origin_mode === 'single_file' ? 'Generates one complete file with strict syntax validation. If the prompt explicitly requires a full-stack application, generation safely expands to a project.' : 'No source folder is needed. This brief becomes the immutable original-source snapshot and follows the same plan and approval controls.'}</p>
            </>}
            <button disabled={busy || uploadingSource || (form.origin_mode === 'existing_source' && !form.source_path)} className="w-full rounded-sm bg-gold px-4 py-2.5 text-sm font-semibold text-bg disabled:opacity-40">{form.origin_mode === 'single_file' ? <Code2 className="mr-2 inline h-4 w-4" /> : <Archive className="mr-2 inline h-4 w-4" />}{form.origin_mode === 'single_file' ? 'Generate single file' : form.origin_mode === 'prompt' ? 'Create governed project' : 'Capture original source'}</button>
          </form>
        </Section>
        <div className="space-y-2">{projects.map(project => <div key={project.id} className="relative">
          <button onClick={async () => { setArtifacts({}); setComparison(null); await refresh(project.id, false) }} className={`w-full rounded-sm border p-4 pr-12 text-left transition ${selected?.id === project.id ? 'border-gold/50 bg-gold/[0.06]' : 'border-hairline bg-surface hover:bg-surface-hover'}`}><div className="flex items-center gap-2 text-sm font-semibold text-ink"><FolderKanban className="h-4 w-4 text-gold" />{project.id} · {project.name}</div><div className="mt-2 flex justify-between text-xs text-ink-muted"><span>{project.status}</span><ChevronRight className="h-4 w-4" /></div></button>
          {authUser?.role === 'admin' && <button type="button" disabled={deletingProject === project.id} title={`Delete ${project.id}`} aria-label={`Delete ${project.id}`} onClick={() => removeProject(project)} className="absolute right-3 top-3 rounded-sm border border-red-500/20 bg-red-500/[0.06] p-2 text-red-300 transition hover:bg-red-500/[0.14] disabled:opacity-40"><Trash2 className="h-4 w-4" /></button>}
        </div>)}</div>
      </aside>

      <section className="min-w-0 rounded-sm border border-hairline bg-surface">
        {!selected ? <div className="flex min-h-[440px] items-center justify-center p-10 text-center"><div><FolderKanban className="mx-auto mb-4 h-10 w-10 text-ink-faint" /><p className="text-sm text-ink-muted">Create or select a project to open the governed workspace.</p></div></div> : <>
          <header className="border-b border-hairline p-5"><div className="flex flex-wrap items-start justify-between gap-4"><div><h2 className="text-xl font-semibold text-ink">{selected.name}</h2><p className="mt-1 text-xs text-ink-muted">{selected.id} · Owner {selected.owner} · Retain {selected.retention_days} days</p></div><div className="flex flex-wrap items-center gap-3"><span className="rounded-full border border-gold/20 bg-gold/10 px-3 py-1 text-xs font-semibold text-gold">{selected.status}</span>{selected.status === 'Plan Approved' && <button disabled={busy} onClick={async () => { const result = await execute(() => transformProject(selected.id), 'Transformation job started'); if (result?.job_id) navigate(`/jobs/${result.job_id}`) }} className="rounded-sm bg-gold px-4 py-2 text-sm font-semibold text-bg shadow-[0_8px_24px_rgba(227,178,60,0.2)] transition hover:bg-gold-soft disabled:opacity-40"><Play className="mr-2 inline h-4 w-4" />Execute Transformation</button>}{selected.status === 'Review Required' && <><button onClick={() => setTab('Validation & Release')} className={buttonClass}><MessageSquareText className="mr-2 inline h-4 w-4" />Review Output</button>{activeJob?.status === 'validation_failed' && latest('plans')?.approval_decision === 'approved' && <button disabled={busy} onClick={async () => { const result = await execute(() => transformProject(selected.id), 'Transformation retry started'); if (result?.job_id) navigate(`/jobs/${result.job_id}`) }} className="rounded-sm bg-gold px-4 py-2 text-sm font-semibold text-bg disabled:opacity-40"><RotateCcw className="mr-2 inline h-4 w-4" />Retry Transformation</button>}</>}</div></div>
            <div className="mt-5 flex overflow-x-auto pb-1">{STEPS.map((step, i) => <div key={step} className="flex min-w-[100px] flex-1 items-center"><span className={`flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-[10px] font-bold ${i <= stepIndex ? 'bg-gold text-bg' : 'bg-white/[0.06] text-ink-faint'}`}>{i + 1}</span><span className={`ml-2 text-[10px] ${i <= stepIndex ? 'text-ink' : 'text-ink-faint'}`}>{step}</span>{i < STEPS.length - 1 && <span className={`mx-2 h-px flex-1 ${i < stepIndex ? 'bg-gold' : 'bg-hairline'}`} />}</div>)}</div>
          </header>
          <nav className="flex overflow-x-auto border-b border-hairline px-3">{TABS.map(item => <button key={item} onClick={() => setTab(item)} className={`whitespace-nowrap border-b-2 px-4 py-3 text-xs font-medium ${tab === item ? 'border-gold text-gold' : 'border-transparent text-ink-muted hover:text-ink'}`}>{item}</button>)}</nav>
          {selected.status === 'Transformation Running' && <div className="border-b border-hairline bg-gold/[0.035] px-5 py-4"><div className="flex flex-wrap items-center justify-between gap-4"><div className="min-w-[260px] flex-1"><div className="mb-2 flex items-center justify-between gap-3"><p className="text-sm font-semibold text-ink">Transformation in progress</p><span className="text-sm font-semibold text-gold">{activeJob?.progress || 0}%</span></div><div className="h-2 overflow-hidden rounded-full bg-white/[0.07]"><div className="h-full rounded-full bg-gold transition-all duration-500" style={{ width: `${activeJob?.progress || 0}%` }} /></div><p className="mt-2 text-xs capitalize text-ink-muted">{activeJob?.phase?.replaceAll('_', ' ') || 'Starting transformation'}{activeJob?.target_stack ? ` · ${activeJob.target_stack}` : ''}</p></div>{activeJob?.job_id && <button onClick={() => navigate(`/jobs/${activeJob.job_id}`)} className="rounded-sm bg-gold px-4 py-2 text-sm font-semibold text-bg"><Play className="mr-2 inline h-4 w-4" />View Live Progress</button>}</div></div>}
          <div className="space-y-5 p-5">
            {tab === 'Overview' && <>
              <div className="grid gap-3 md:grid-cols-4">{[['Source snapshots', snapshotCounts.source || 0], ['Analysis versions', snapshotCounts.analysis || 0], ['Output runs', snapshotCounts.outputs || 0], ['Approved releases', snapshotCounts.approved || 0]].map(([label, value]) => <div key={label} className="rounded-sm border border-hairline bg-bg p-4"><p className="text-2xl font-semibold text-ink">{value}</p><p className="mt-1 text-xs text-ink-muted">{label}</p></div>)}</div>
              <Section title="Project configuration"><ObjectGrid value={selected.configuration} /></Section>
              <Section title="Next governed action"><div className="flex flex-wrap gap-3">
                <button disabled={busy || selected.status !== 'Uploaded'} onClick={() => execute(() => analyzeProject(selected.id, selected.configuration?.engine_target || selected.configuration?.target_stack || form.target_stack, selected.configuration?.custom_stack_desc || ''), 'Semantic analysis captured', 'Analysis')} className={buttonClass}><ScanSearch className="mr-2 inline h-4 w-4" />Analyze repository</button>
                <button disabled={busy || !latest('analysis')} onClick={generatePlanFromAnalysis} className={buttonClass}><ClipboardList className="mr-2 inline h-4 w-4" />Generate plan</button>
                <button disabled={busy || !latest('plans') || latest('plans')?.locked} onClick={() => execute(() => decideProjectSnapshot(selected.id, latest('plans').id, selected.status === 'Plan Reviewed' ? 'approved' : 'reviewed'), selected.status === 'Plan Reviewed' ? 'Plan approved and locked' : 'Plan marked as reviewed', 'Plan')} className={buttonClass}><CheckCircle2 className="mr-2 inline h-4 w-4" />{selected.status === 'Plan Reviewed' ? 'Approve plan' : 'Complete plan review'}</button>
                <button disabled={busy || selected.status !== 'Plan Approved'} onClick={() => execute(() => transformProject(selected.id), 'Transformation job started', 'History')} className="rounded-sm bg-gold px-4 py-2 text-sm font-semibold text-bg disabled:opacity-35"><Play className="mr-2 inline h-4 w-4" />Run transformation</button>
              </div></Section>
            </>}

            {tab === 'Analysis' && <>{!semantic ? <p className="text-sm text-ink-muted">Run repository analysis to populate this section.</p> : <div className="overflow-hidden rounded-sm border border-hairline bg-bg">
              <div className="flex flex-wrap items-center justify-between gap-3 border-b border-hairline bg-surface px-4 py-3">
                <div><p className="text-sm font-semibold text-ink">Repository analysis</p><p className="mt-0.5 text-[11px] text-ink-muted">Review the complete results in the scrollable frame below.</p></div>
                <button disabled={busy || !latest('analysis')} onClick={generatePlanFromAnalysis} className="shrink-0 rounded-sm bg-gold px-4 py-2 text-sm font-semibold text-bg disabled:opacity-40"><ClipboardList className="mr-2 inline h-4 w-4" />{busy ? 'Generating…' : 'Generate Plan'}</button>
              </div>
              <div className="max-h-[68vh] space-y-5 overflow-y-auto overscroll-contain p-4">
                <div className="grid gap-3 md:grid-cols-4">{[['Symbols', semantic.symbol_index?.length], ['API endpoints', semantic.api_endpoints?.length], ['DB operations', semantic.database_access?.length], ['Dependency cycles', semantic.cyclic_dependencies?.length]].map(([l, v]) => <div key={l} className="rounded-sm border border-hairline bg-surface p-4"><p className="text-xl font-semibold text-ink">{v || 0}</p><p className="text-xs text-ink-muted">{l}</p></div>)}</div>
                <div className="grid min-w-0 gap-5 2xl:grid-cols-2"><Section title="Technology and architecture"><ObjectGrid value={analysisDisplay} /></Section><Section title="Module hierarchy"><ObjectGrid value={semantic.hierarchy?.modules} /></Section><Section title="API endpoint inventory"><ObjectGrid value={semantic.api_endpoints} /></Section><Section title="Database and stored procedures"><ObjectGrid value={semantic.database_access} /></Section><Section title="Security and configuration"><ObjectGrid value={{ authentication_authorization_flow: semantic.authentication_authorization_flow, configuration_inventory: semantic.configuration_inventory }} /></Section><Section title="Quality findings"><ObjectGrid value={{ cyclic_dependencies: semantic.cyclic_dependencies, dead_code_candidates: semantic.dead_code_candidates, test_to_code_mapping: semantic.test_to_code_mapping }} /></Section></div>
              </div>
            </div>}</>}

            {tab === 'Plan' && <>{!plan ? <p className="text-sm text-ink-muted">Generate a plan after analysis.</p> : <>
              <div className="grid gap-5 lg:grid-cols-2">{Object.entries(displayedPlan).filter(([k]) => ![
                'excluded_modules', 'manual_tasks', 'risks_and_assumptions', 'target_technologies', 'auth_approach',
                'proposed_decisions', 'confirmation_status', 'decisions_confirmed', 'ready_for_approval',
                'unresolved_requirements', 'schema_version', 'generated_at',
                ...(isPromptProject ? [
                  'cutover_approach', 'rollback_approach', 'unsupported_constructs',
                ] : []),
              ].includes(k)).map(([k, v]) => <Section key={k} title={k.replaceAll('_', ' ')}><ObjectGrid value={v} /></Section>)}</div>
              {!isPromptProject && plan.proposed_decisions?.length > 0 && <Section title="Proposed decisions — confirmation requested" action={<span className={`rounded-full px-2.5 py-1 text-[10px] font-semibold ${plan.confirmation_status === 'CONFIRMED' ? 'bg-emerald-500/10 text-emerald-700' : 'bg-amber-500/10 text-amber-700'}`}>{plan.confirmation_status === 'CONFIRMED' ? 'Confirmed' : 'Pending confirmation'}</span>}>
                <p className="mb-4 text-xs leading-5 text-ink-muted">These values were populated from the selected To Be Architecture. They are working development defaults, not blockers. Review or edit them below, then confirm.</p>
                <div className="grid gap-3 md:grid-cols-2">{plan.proposed_decisions.map(decision => <div key={decision.key} className="rounded-sm border border-amber-500/20 bg-amber-500/[0.04] p-3"><p className="text-[11px] font-semibold uppercase tracking-wide text-ink-faint">{decision.label}</p><p className="mt-2 text-sm leading-6 text-ink">{decision.value}</p></div>)}</div>
              </Section>}
              <Section title="Review and revise before approval" action={latest('plans')?.locked && <span className="text-xs text-emerald-400">Approved and locked</span>}><div className="grid gap-4 md:grid-cols-2">
                <label className="text-xs text-ink-muted">Target technologies<input disabled={latest('plans')?.locked} className={`${fieldClass} mt-2`} value={planEdit.target_technologies} onChange={e => setPlanEdit({ ...planEdit, target_technologies: e.target.value })} /></label>
                <label className="text-xs text-ink-muted">Architecture style and boundaries<input disabled={latest('plans')?.locked} className={`${fieldClass} mt-2`} value={planEdit.architecture_style} onChange={e => setPlanEdit({ ...planEdit, architecture_style: e.target.value })} /></label>
                <label className="text-xs text-ink-muted">Deployment platform and topology<textarea disabled={latest('plans')?.locked} rows="3" className={`${fieldClass} mt-2`} value={planEdit.deployment_approach} onChange={e => setPlanEdit({ ...planEdit, deployment_approach: e.target.value })} /></label>
                <label className="text-xs text-ink-muted">Persistence and database choice<input disabled={latest('plans')?.locked} className={`${fieldClass} mt-2`} value={planEdit.database} onChange={e => setPlanEdit({ ...planEdit, database: e.target.value })} /></label>
                <label className="text-xs text-ink-muted">Authentication and authorization approach<textarea disabled={latest('plans')?.locked} rows="3" className={`${fieldClass} mt-2`} value={planEdit.auth_approach} onChange={e => setPlanEdit({ ...planEdit, auth_approach: e.target.value })} /></label>
                {!isPromptProject && <label className="text-xs text-ink-muted">Cutover, outage, and reconciliation criteria<textarea disabled={latest('plans')?.locked} rows="3" className={`${fieldClass} mt-2`} value={planEdit.cutover_approach} onChange={e => setPlanEdit({ ...planEdit, cutover_approach: e.target.value })} /></label>}
                {!isPromptProject && <label className="text-xs text-ink-muted">Rollback triggers, RPO, and RTO<textarea disabled={latest('plans')?.locked} rows="3" className={`${fieldClass} mt-2`} value={planEdit.rollback_approach} onChange={e => setPlanEdit({ ...planEdit, rollback_approach: e.target.value })} /></label>}
                <label className="text-xs text-ink-muted">Excluded modules<textarea disabled={latest('plans')?.locked} rows="3" className={`${fieldClass} mt-2`} value={planEdit.excluded_modules} onChange={e => setPlanEdit({ ...planEdit, excluded_modules: e.target.value })} /></label>
                <label className="text-xs text-ink-muted">Risks and assumptions<textarea disabled={latest('plans')?.locked} rows="3" className={`${fieldClass} mt-2`} value={planEdit.risks_and_assumptions} onChange={e => setPlanEdit({ ...planEdit, risks_and_assumptions: e.target.value })} /></label>
                {(!isPromptProject || planEdit.manual_tasks) && <label className="text-xs text-ink-muted">Unresolved manual tasks<textarea disabled={latest('plans')?.locked} rows="3" className={`${fieldClass} mt-2`} value={planEdit.manual_tasks} onChange={e => setPlanEdit({ ...planEdit, manual_tasks: e.target.value })} /></label>}
              </div>
                {!latest('plans')?.locked && <div className="mt-4 flex flex-wrap gap-3"><button className={buttonClass} onClick={() => execute(() => reviseProjectPlan(selected.id, latest('plans').id, planRevisionPayload(false)), 'Plan draft saved; proposed decisions remain pending confirmation', 'Plan')}>Save revision</button>{!isPromptProject && plan.confirmation_status !== 'CONFIRMED' && <button className="rounded-sm border border-emerald-600/30 bg-emerald-600 px-4 py-2 text-sm font-semibold text-white" onClick={() => execute(() => reviseProjectPlan(selected.id, latest('plans').id, planRevisionPayload(true)), 'Proposed To Be Architecture decisions confirmed', 'Plan')}>Confirm proposed decisions</button>}<button className="rounded-sm bg-gold px-4 py-2 text-sm font-semibold text-bg" onClick={() => execute(() => decideProjectSnapshot(selected.id, latest('plans').id, selected.status === 'Plan Reviewed' ? 'approved' : 'reviewed'), selected.status === 'Plan Reviewed' ? 'Plan approved and locked' : 'Plan review completed', selected.status === 'Plan Reviewed' ? 'Contracts' : 'Plan')}>{selected.status === 'Plan Reviewed' ? 'Approve and lock' : 'Mark review complete'}</button></div>}
              </Section>
            </>}</>}

            {tab === 'Contracts' && <>{!contracts ? <p className="text-sm text-ink-muted">Canonical contracts are generated with the modernization plan.</p> : <><div className="grid gap-5 lg:grid-cols-2">{Object.entries(contracts).filter(([k]) => !['checksum', 'created_at'].includes(k)).map(([k, v]) => <Section key={k} title={k.replaceAll('_', ' ')}><ObjectGrid value={v} /></Section>)}</div><Section title="Contract integrity" action={<button className={buttonClass} onClick={async () => { try { setContractResult(await validateProjectContracts(selected.id)) } catch (e) { toast.error(e?.response?.data?.detail || e.message) } }}><ShieldCheck className="mr-2 inline h-4 w-4" />Validate contracts</button>}><p className="mb-3 break-all font-mono text-xs text-ink-muted">Locked checksum: {contracts.checksum}</p>{contractResult && <ObjectGrid value={contractResult} />}</Section></>}</>}

            {tab === 'Compare' && <><Section title="Select two runs or releases"><div className="grid gap-3 md:grid-cols-[1fr_1fr_auto]"><select className={fieldClass} value={left} onChange={e => setLeft(e.target.value)}><option value="">Base snapshot</option>{eligibleSnapshots.map(s => <option key={s.id} value={s.id}>{s.kind} v{s.version} · {s.id}</option>)}</select><select className={fieldClass} value={right} onChange={e => setRight(e.target.value)}><option value="">Current snapshot</option>{eligibleSnapshots.map(s => <option key={s.id} value={s.id}>{s.kind} v{s.version} · {s.id}</option>)}</select><button disabled={!left || !right} className={buttonClass} onClick={async () => { try { setComparison(await compareSnapshots(selected.id, left, right)) } catch (e) { toast.error(e?.response?.data?.detail || e.message) } }}><FileDiff className="mr-2 inline h-4 w-4" />Compare</button></div></Section>{comparison && <><div className="flex flex-wrap items-center gap-3"><span className="text-sm text-ink-muted">Added {comparison.summary.added} · Modified {comparison.summary.modified} · Removed {comparison.summary.removed}</span><a className={buttonClass} href={getComparisonExportUrl(selected.id, left, right, 'html')}>Export HTML</a><a className={buttonClass} href={getComparisonExportUrl(selected.id, left, right, 'pdf')}>Export PDF</a></div>{comparison.files.map(file => <details key={file.path} className="rounded-sm border border-hairline bg-bg"><summary className="cursor-pointer p-3 text-xs font-semibold text-ink">{file.status.toUpperCase()} · {file.path} <span className="ml-2 text-gold">{file.classification}</span></summary><pre className="max-h-[500px] overflow-auto border-t border-hairline p-4 text-[11px] text-ink-muted">{file.diff}</pre></details>)}</>}</>}

            {tab === 'Validation & Release' && <>
              <Section title="Validation results"><ValidationResults value={validation} /></Section>
              <Section title="Release quality gate">{qualityGate ? <div className="space-y-4"><div className={`rounded-sm border p-4 ${qualityGate.passed ? 'border-emerald-500/25 bg-emerald-500/[0.05]' : 'border-red-500/25 bg-red-500/[0.05]'}`}><p className={`text-sm font-semibold ${qualityGate.passed ? 'text-emerald-300' : 'text-red-300'}`}>{qualityGate.passed ? 'All mandatory release checks passed' : 'Release is blocked'}</p></div><ObjectGrid value={qualityGate.checks} />{qualityGate.blockers?.length > 0 && <div><p className="mb-2 text-xs font-semibold uppercase text-red-300">Blocking issues</p><ObjectGrid value={qualityGate.blockers} /></div>}{qualityGate.warnings?.length > 0 && <div><p className="mb-2 text-xs font-semibold uppercase text-amber-300">Warnings</p><ObjectGrid value={qualityGate.warnings} /></div>}</div> : <p className="text-sm text-ink-muted">Quality gate will be evaluated when validation completes.</p>}</Section>
              <Section title="Output review and release decision"><div className="space-y-4">
                {latest('outputs') && <div className="rounded-sm border border-hairline bg-bg p-4">
                  <div className="mb-4 flex flex-wrap items-center justify-between gap-3"><div><p className="text-sm font-semibold text-ink">Output run v{latest('outputs').version}</p><p className="font-mono text-[11px] text-ink-faint">{latest('outputs').checksum}</p></div><span className="text-xs text-ink-muted">{latest('outputs').approval_decision || 'Pending review'}</span></div>
                  <label className="block text-xs text-ink-muted">Review feedback<textarea rows="5" className={`${fieldClass} mt-2`} placeholder="Describe rejected behavior, required corrections, affected files, acceptance criteria and expected outcome." value={reviewFeedback} onChange={e => setReviewFeedback(e.target.value)} /></label>
                  <div className="mt-4 flex flex-wrap gap-3">
                    <button disabled={busy || !qualityGate?.passed || latest('outputs').approval_decision === 'rejected'} title={!qualityGate?.passed ? 'Resolve all release quality-gate blockers before approval' : 'Approve this output'} className="rounded-sm bg-emerald-500 px-4 py-2 text-sm font-semibold text-white disabled:opacity-35" onClick={() => execute(() => approveProjectRelease(selected.id, latest('outputs').id, reviewFeedback || 'Approved through governed workspace'), 'Release approved and locked', 'Validation & Release')}><CheckCircle2 className="mr-2 inline h-4 w-4" />Approve Release</button>
                    <button disabled={busy || !reviewFeedback.trim()} className="rounded-sm bg-gold px-4 py-2 text-sm font-semibold text-bg disabled:opacity-35" onClick={async () => { const reviewed = await execute(() => submitProjectReview(selected.id, latest('outputs').id, 'corrections_requested', reviewFeedback), 'Corrections recorded'); if (reviewed) { const job = await execute(() => transformProject(selected.id), 'Correction run started'); if (job?.job_id) navigate(`/jobs/${job.job_id}`) } }}><RotateCcw className="mr-2 inline h-4 w-4" />Request Corrections & Re-run</button>
                    <button disabled={busy || !reviewFeedback.trim()} className="rounded-sm border border-red-500/30 bg-red-500/[0.06] px-4 py-2 text-sm font-semibold text-red-300 disabled:opacity-35" onClick={() => execute(() => submitProjectReview(selected.id, latest('outputs').id, 'rejected', reviewFeedback), 'Output rejected and feedback recorded', 'Validation & Release')}><XCircle className="mr-2 inline h-4 w-4" />Reject Output</button>
                  </div>
                  <p className="mt-3 text-[11px] leading-5 text-ink-faint">Feedback is saved as an immutable review snapshot. Correction requests are injected into the next generation run together with the locked contracts.</p>
                </div>}
                {(selected.snapshots || []).filter(s => s.kind === 'approved').map(release => <div key={release.id} className="flex items-center justify-between rounded-sm border border-emerald-500/20 bg-emerald-500/[0.04] p-3"><span className="text-sm text-emerald-300">Locked release v{release.version}</span><a className={buttonClass} href={getReleaseExportUrl(selected.id, release.id)}><Download className="mr-2 inline h-4 w-4" />Export ZIP</a></div>)}
              </div></Section>
            </>}

            {tab === 'History' && <><Section title="Immutable snapshot history" action={<button className={buttonClass} onClick={() => execute(() => purgeProjectSnapshots(selected.id), 'Retention policy applied', 'History')}>Apply retention policy</button>}><div className="overflow-x-auto"><table className="w-full text-left text-xs"><thead className="text-ink-faint"><tr><th className="p-3">Type</th><th className="p-3">Version / ID</th><th className="p-3">Created</th><th className="p-3">Checksum</th><th className="p-3">Decision</th><th className="p-3">Action</th></tr></thead><tbody>{selected.snapshots?.map(s => <tr key={s.id} className="border-t border-hairline"><td className="p-3 font-semibold uppercase text-gold">{s.kind}</td><td className="p-3 text-ink">v{String(s.version).padStart(3, '0')}<br/><span className="text-ink-faint">{s.id}</span></td><td className="p-3 text-ink-muted">{new Date(s.created_at).toLocaleString()}</td><td className="p-3 font-mono text-ink-faint">{s.checksum.slice(0, 12)}…</td><td className="p-3 text-ink-muted">{s.locked ? 'Locked' : s.approval_decision || s.status}</td><td className="p-3"><button disabled={s.locked} title="Create a new snapshot restored from this version" onClick={() => execute(() => restoreProjectSnapshot(selected.id, s.id), 'Snapshot restored as a new version', 'History')} className="text-ink-muted hover:text-gold disabled:opacity-25"><RotateCcw className="h-4 w-4" /></button></td></tr>)}</tbody></table></div></Section></>}
          </div>
        </>}
      </section>
    </div>
  </main></Layout>
}
