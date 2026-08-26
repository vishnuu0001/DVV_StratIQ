// ---------------------------------------------------------------------------
// Scope: Upload, BRD, FSD, and knowledge-graph requirements workspace.
// ---------------------------------------------------------------------------
import { useEffect, useMemo, useRef, useState } from 'react'
import toast from 'react-hot-toast'
import { Activity, AlertTriangle, Boxes, Braces, Check, CheckCircle2, ChevronRight, Circle, Clock3, Cloud, Code2, Database, Download, FileCode2, FileText, FolderKanban, FolderOpen, GitBranch, Layers3, LoaderCircle, Minus, Network, Plus, Search, Server, ShieldCheck, Sparkles, Upload, Workflow } from 'lucide-react'
import { useLocation, useNavigate, useSearchParams } from 'react-router-dom'
import Layout from '../components/Layout.jsx'
import {
  createProject, downloadGeneratedAssets, downloadRequirementDocument, filterUploadFiles, generateRequirementDocument,
  getGeneratedAssets, getProject, getRequirementDocument, getRequirementGenerationJob, getSnapshotArtifact, listProjects, uploadFolder,
} from '../api/client.js'

const fieldClass = 'w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-blue-400 focus:ring-4 focus:ring-blue-500/10'
const TYPE_META = {
  brd: { title: 'Business Requirements Document', short: 'BRD', icon: FileText, description: 'Generate a detailed, evidence-grounded business requirements document from the uploaded project.' },
  fsd: { title: 'Functional Specification Document', short: 'FSD', icon: FileText, description: 'Translate source-code evidence into detailed functional behavior, interfaces, data rules, implementation specifications, and acceptance scenarios.' },
  knowledge_graph: { title: 'Business & Functional Requirements Knowledge Graph', short: 'Knowledge Graph', icon: Network, description: 'Use Ollama to connect business needs, actors, features, rules, data, integrations, and quality requirements.' },
}
const GRAPH_COLORS = {
  business: '#d9a72e', actor: '#60a5fa', feature: '#34d399', functional: '#22d3ee',
  data: '#a78bfa', integration: '#fb7185', rule: '#f59e0b', quality: '#94a3b8',
}

function projectLabel(project) {
  return `${project.id} · ${project.name}`
}

function LegacyUploadProjects() {
  const navigate = useNavigate()
  const inputRef = useRef(null)
  const [files, setFiles] = useState([])
  const [folderName, setFolderName] = useState('')
  const [uploading, setUploading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [uploaded, setUploaded] = useState(null)
  const [projects, setProjects] = useState([])
  const [selectedProjectId, setSelectedProjectId] = useState('')

  const refresh = () => listProjects().then(result => setProjects(result.projects || []))
  useEffect(() => { refresh().catch(() => {}) }, [])

  const selectFolder = event => {
    const selected = filterUploadFiles(event.target.files)
    setFiles(selected)
    setUploaded(null)
    setProgress(0)
    setFolderName(selected[0]?.webkitRelativePath?.split('/')[0] || '')
  }

  const capture = async () => {
    if (!files.length) return
    setUploading(true)
    try {
      const result = await uploadFolder(files, setProgress)
      const project = await createProject({
        name: folderName || 'Requirements project', source_path: result.path, retention_days: 365,
        configuration: { origin_mode: 'existing_source', source_display_name: folderName, requirements_intake: true },
      })
      setUploaded({ ...result, project })
      setFiles([])
      if (inputRef.current) inputRef.current.value = ''
      await refresh()
      toast.success(`${project.id} captured for requirements documentation`)
    } catch (error) {
      toast.error(error?.response?.data?.detail || error.message || 'Project upload failed')
    } finally {
      setUploading(false)
    }
  }

  return <PageFrame title="Upload Projects" description="Capture a local project as an immutable source snapshot for requirements analysis.">
    <div className="grid gap-6 xl:grid-cols-[minmax(0,500px)_1fr]">
      <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-[0_12px_35px_rgba(15,23,42,0.06)]">
        <div className="mb-5"><span className="inline-flex rounded-full bg-blue-50 px-3 py-1 text-[10px] font-bold uppercase tracking-widest text-blue-700">New source</span><h2 className="mt-3 text-lg font-bold text-slate-900">Capture project folder</h2><p className="mt-1 text-sm leading-6 text-slate-500">Create a secure, immutable snapshot for AI-assisted requirements analysis.</p></div>
        <button type="button" disabled={uploading} onClick={() => inputRef.current?.click()} className={`${fieldClass} flex items-center gap-3 text-left disabled:opacity-50`}>
          <FolderOpen className="h-5 w-5 shrink-0 text-gold" />
          <span className={folderName ? 'text-ink' : 'text-ink-muted'}>{folderName ? `${folderName} · ${files.length} files selected` : 'Select a project folder from this computer…'}</span>
        </button>
        <input ref={inputRef} type="file" multiple className="hidden" onChange={selectFolder} {...{ webkitdirectory: '', directory: '' }} />
        <p className="mt-4 text-sm leading-6 text-ink-muted">Choose a folder from your computer. Files are securely copied into an immutable internal snapshot; your original folder is never modified.</p>
        {uploading && <div className="mt-4"><div className="h-1.5 overflow-hidden rounded-full bg-black/10"><div className="h-full bg-gold transition-all" style={{ width: `${Math.max(3, Math.round(progress * 100))}%` }} /></div><p className="mt-1 text-xs text-ink-muted">Uploading… {Math.round(progress * 100)}%</p></div>}
        <button type="button" onClick={capture} disabled={!files.length || uploading} className="mt-5 flex w-full items-center justify-center rounded-xl bg-blue-600 px-4 py-3 text-sm font-semibold text-white shadow-lg shadow-blue-600/20 transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-40">
          {uploading ? <LoaderCircle className="mr-2 h-4 w-4 animate-spin" /> : <Upload className="mr-2 h-4 w-4" />}Capture original source
        </button>
        {uploaded && <p className="mt-4 rounded-sm border border-emerald-500/25 bg-emerald-500/[0.05] p-3 text-sm text-emerald-300">{projectLabel(uploaded.project)} is ready · {uploaded.file_count} files captured.</p>}
      </section>
      <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-[0_12px_35px_rgba(15,23,42,0.06)]">
        <div className="flex items-start justify-between gap-4"><div><span className="inline-flex rounded-full bg-emerald-50 px-3 py-1 text-[10px] font-bold uppercase tracking-widest text-emerald-700">{projects.length} available</span><h2 className="mt-3 text-lg font-bold text-slate-900">Available projects</h2></div><FolderKanban className="h-6 w-6 text-slate-300" /></div>
        <p className="mt-1 text-xs text-ink-muted">Select a project, then choose the requirements artifact to generate.</p>
        <div className="mt-4 space-y-2">{projects.length ? projects.map(project => {
          const selected = selectedProjectId === project.id
          return <button type="button" key={project.id} aria-pressed={selected} onClick={() => setSelectedProjectId(project.id)} className={`flex w-full items-center gap-3 rounded-xl border p-4 text-left transition-all ${selected ? 'border-blue-400 bg-blue-50 shadow-sm ring-4 ring-blue-500/[0.06]' : 'border-slate-200 bg-white hover:-translate-y-0.5 hover:border-blue-200 hover:shadow-md'}`}>
            <FolderKanban className={`h-4 w-4 shrink-0 ${selected ? 'text-gold' : 'text-ink-muted'}`} />
            <div className="min-w-0 flex-1"><p className="truncate text-sm font-medium text-ink">{projectLabel(project)}</p><p className="mt-0.5 text-xs text-ink-muted">{project.status} · captured {new Date(project.created_at).toLocaleString()}</p></div>
            {selected ? <CheckCircle2 className="h-5 w-5 shrink-0 text-gold" /> : <ChevronRight className="h-4 w-4 shrink-0 text-ink-faint" />}
          </button>
        }) : <p className="text-sm text-ink-muted">No projects have been uploaded yet.</p>}</div>
        {selectedProjectId && <div className="mt-5 rounded-2xl border border-blue-200 bg-gradient-to-br from-blue-50 to-white p-5">
          <p className="text-xs font-semibold uppercase tracking-wide text-ink-faint">Selected project</p>
          <p className="mt-1 text-sm font-semibold text-ink">{projectLabel(projects.find(project => project.id === selectedProjectId))}</p>
          <div className="mt-4 grid gap-2 sm:grid-cols-3">
            <button type="button" onClick={() => navigate(`/requirements/brd?project=${encodeURIComponent(selectedProjectId)}`)} className="rounded-xl bg-blue-600 px-3 py-2.5 text-xs font-semibold text-white shadow-sm hover:bg-blue-700">Generate BRD</button>
            <button type="button" onClick={() => navigate(`/requirements/fsd?project=${encodeURIComponent(selectedProjectId)}`)} className="rounded-xl bg-blue-600 px-3 py-2.5 text-xs font-semibold text-white shadow-sm hover:bg-blue-700">Generate FSD</button>
            <button type="button" onClick={() => navigate(`/requirements/knowledge-graph?project=${encodeURIComponent(selectedProjectId)}`)} className="rounded-xl bg-slate-800 px-3 py-2.5 text-xs font-semibold text-white shadow-sm hover:bg-slate-900">Knowledge Graph</button>
          </div>
        </div>}
      </section>
    </div>
  </PageFrame>
}

const ANALYSIS_SCOPES = [
  { id: 'source', label: 'Source & configuration', icon: Code2 },
  { id: 'interfaces', label: 'APIs & interfaces', icon: Braces },
  { id: 'data', label: 'Data models & schemas', icon: Database },
  { id: 'rules', label: 'Business rules', icon: Workflow },
  { id: 'security', label: 'Security & dependencies', icon: ShieldCheck },
]

function fileKind(file) {
  const extension = file.name.split('.').pop()?.toUpperCase() || 'FILE'
  return extension.length > 8 ? 'SOURCE' : extension
}

function fileSize(bytes = 0) {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 ** 2) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / 1024 ** 2).toFixed(1)} MB`
}

function UploadProjects() {
  const navigate = useNavigate()
  const inputRef = useRef(null)
  const [files, setFiles] = useState([])
  const [folderName, setFolderName] = useState('')
  const [applicationName, setApplicationName] = useState('')
  const [applicationKey, setApplicationKey] = useState('')
  const [clientName, setClientName] = useState('')
  const [applicationOwner, setApplicationOwner] = useState('')
  const [businessUnit, setBusinessUnit] = useState('')
  const [businessCriticality, setBusinessCriticality] = useState('Medium')
  const [businessContext, setBusinessContext] = useState('')
  const [scope, setScope] = useState(ANALYSIS_SCOPES.map(item => item.id))
  const [uploading, setUploading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [uploaded, setUploaded] = useState(null)
  const [projects, setProjects] = useState([])
  const [selectedProjectId, setSelectedProjectId] = useState('')
  const refresh = () => listProjects().then(result => setProjects(result.projects || []))
  useEffect(() => { refresh().catch(() => {}) }, [])

  const selectFolder = event => {
    const selected = filterUploadFiles(event.target.files)
    const selectedFolder = selected[0]?.webkitRelativePath?.split('/')[0] || ''
    setFiles(selected); setFolderName(selectedFolder); setApplicationName(selectedFolder)
    setApplicationKey(current => current || selectedFolder.replace(/[^A-Za-z0-9]+/g, '-').replace(/^-|-$/g, '').toUpperCase().slice(0, 40))
    setUploaded(null); setProgress(0)
  }
  const clearFiles = () => {
    setFiles([]); setFolderName(''); setProgress(0)
    if (inputRef.current) inputRef.current.value = ''
  }
  const capture = async () => {
    if (!files.length) return
    setUploading(true)
    try {
      const result = await uploadFolder(files, setProgress)
      const project = await createProject({
        name: applicationName || folderName || 'Requirements project', source_path: result.path, retention_days: 365,
        configuration: {
          origin_mode: 'existing_source', source_display_name: folderName,
          application_name: applicationName || folderName, application_key: applicationKey,
          client_name: clientName, customer: clientName, application_owner: applicationOwner,
          business_unit: businessUnit, business_criticality: businessCriticality,
          description: businessContext, requirements_intake: true, requirements_analysis_scope: scope,
        },
      })
      setUploaded({ ...result, project }); clearFiles(); await refresh()
      setSelectedProjectId(project.id)
      toast.success(`${project.id} captured for requirements discovery`)
    } catch (error) { toast.error(error?.response?.data?.detail || error.message || 'Project upload failed') }
    finally { setUploading(false) }
  }
  const toggleScope = id => setScope(current => current.includes(id) ? current.filter(value => value !== id) : [...current, id])
  const selectedBytes = files.reduce((sum, file) => sum + file.size, 0)

  return <PageFrame title="Upload Legacy Assets" description="Upload source code and configuration, define the evidence scope, and prepare a governed project for AI requirements discovery." step={1}>
    <div className="grid gap-6 2xl:grid-cols-[minmax(0,1fr)_380px]">
      <section className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-[0_16px_45px_rgba(15,23,42,0.07)]">
        <div className="flex items-center justify-between gap-4 border-b border-slate-100 px-6 py-5">
          <div><p className="text-xs font-bold uppercase tracking-[0.14em] text-blue-600">Step 1 of 4</p><h2 className="mt-1 text-xl font-bold text-slate-950">Upload your legacy assets</h2><p className="mt-1 text-sm text-slate-500">Select the complete project so requirements can be traced to source evidence.</p></div>
          <div className="hidden rounded-2xl bg-blue-50 p-3 sm:block"><Upload className="h-6 w-6 text-blue-600" /></div>
        </div>
        <div className="p-6">
          <div className="mb-5 flex gap-2 border-b border-slate-200"><button type="button" className="border-b-2 border-blue-600 px-3 pb-3 text-xs font-bold text-blue-700">Source project</button><button type="button" className="px-3 pb-3 text-xs font-semibold text-slate-400" disabled>Repository import</button><button type="button" className="px-3 pb-3 text-xs font-semibold text-slate-400" disabled>Hybrid analysis</button></div>
          <button type="button" disabled={uploading} onClick={() => inputRef.current?.click()} className="group flex min-h-48 w-full flex-col items-center justify-center rounded-2xl border-2 border-dashed border-blue-300 bg-gradient-to-b from-blue-50/70 to-white p-7 text-center transition hover:border-blue-500 hover:bg-blue-50 disabled:opacity-50">
            <span className="flex h-14 w-14 items-center justify-center rounded-2xl bg-blue-600 text-white shadow-lg shadow-blue-600/20 transition group-hover:-translate-y-1"><Upload className="h-7 w-7" /></span>
            <span className="mt-4 text-base font-bold text-slate-900">{folderName || 'Drop a project folder here'}</span>
            <span className="mt-1 text-xs text-slate-500">{files.length ? `${files.length} files · ${fileSize(selectedBytes)}` : 'or browse this computer'}</span>
            <span className="mt-4 rounded-lg bg-white px-4 py-2 text-xs font-bold text-blue-700 shadow-sm ring-1 ring-blue-100">Browse files</span>
          </button>
          <input ref={inputRef} type="file" multiple className="hidden" onChange={selectFolder} {...{ webkitdirectory: '', directory: '' }} />

          {files.length > 0 && <div className="mt-6 overflow-hidden rounded-xl border border-slate-200">
            <div className="flex items-center justify-between bg-slate-50 px-4 py-3"><h3 className="text-xs font-bold uppercase tracking-wide text-slate-600">Selected assets ({files.length})</h3><button type="button" onClick={clearFiles} className="text-xs font-semibold text-slate-500 hover:text-rose-600">Clear</button></div>
            <div className="max-h-56 overflow-auto"><table className="w-full text-left text-xs"><thead className="sticky top-0 bg-white text-[10px] uppercase tracking-wide text-slate-400"><tr><th className="px-4 py-2 font-semibold">File</th><th className="px-4 py-2 font-semibold">Type</th><th className="px-4 py-2 font-semibold">Size</th><th className="px-4 py-2 font-semibold">Status</th></tr></thead><tbody className="divide-y divide-slate-100">{files.slice(0, 25).map((file, index) => <tr key={`${file.webkitRelativePath}-${index}`}><td className="max-w-[380px] truncate px-4 py-2.5 font-medium text-slate-700">{file.webkitRelativePath || file.name}</td><td className="px-4 py-2.5 text-slate-500">{fileKind(file)}</td><td className="px-4 py-2.5 text-slate-500">{fileSize(file.size)}</td><td className="px-4 py-2.5"><span className="inline-flex items-center gap-1 text-emerald-600"><CheckCircle2 className="h-3 w-3" />Ready</span></td></tr>)}</tbody></table></div>
            {files.length > 25 && <p className="border-t border-slate-100 px-4 py-2 text-[11px] text-slate-400">Showing 25 of {files.length} selected files</p>}
          </div>}

          <div className="mt-6 rounded-xl border border-slate-200 p-5">
            <div className="flex items-start justify-between gap-4"><div><h3 className="text-sm font-bold text-slate-900">Project identity & analysis configuration</h3><p className="mt-1 text-xs leading-5 text-slate-500">These canonical identifiers follow the project through governance, BRD, FSD, knowledge graph, architecture, and generated assets.</p></div><span className="rounded-full bg-blue-50 px-3 py-1 text-[10px] font-bold uppercase text-blue-700">Required metadata</span></div>
            <div className="mt-5 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              <label className="text-xs font-semibold text-slate-600">Client name <span className="text-rose-500">*</span><input required className={`${fieldClass} mt-2`} value={clientName} onChange={event => setClientName(event.target.value)} placeholder="e.g. Contoso Ltd" /></label>
              <label className="text-xs font-semibold text-slate-600">Application name <span className="text-rose-500">*</span><input required className={`${fieldClass} mt-2`} value={applicationName} onChange={event => setApplicationName(event.target.value)} placeholder="Detected from folder" /></label>
              <label className="text-xs font-semibold text-slate-600">Application key <span className="text-rose-500">*</span><input required className={`${fieldClass} mt-2 font-mono uppercase`} value={applicationKey} onChange={event => setApplicationKey(event.target.value.replace(/[^A-Za-z0-9-]/g, '').toUpperCase())} placeholder="CUSTOMER-PORTAL" /><span className="mt-1 block text-[10px] font-normal text-slate-400">Stable business key; the system also assigns an APP-### primary key.</span></label>
              <label className="text-xs font-semibold text-slate-600">Application owner<input className={`${fieldClass} mt-2`} value={applicationOwner} onChange={event => setApplicationOwner(event.target.value)} placeholder="Owner or product lead" /></label>
              <label className="text-xs font-semibold text-slate-600">Business unit<input className={`${fieldClass} mt-2`} value={businessUnit} onChange={event => setBusinessUnit(event.target.value)} placeholder="e.g. Retail Banking" /></label>
              <label className="text-xs font-semibold text-slate-600">Business criticality<select className={`${fieldClass} mt-2`} value={businessCriticality} onChange={event => setBusinessCriticality(event.target.value)}><option>Low</option><option>Medium</option><option>High</option><option>Mission critical</option></select></label>
            </div>
            <label className="mt-4 block text-xs font-semibold text-slate-600">Business context<textarea className={`${fieldClass} mt-2`} rows="3" value={businessContext} onChange={event => setBusinessContext(event.target.value)} placeholder="Business purpose, users, operating context, regulatory constraints, and expected outcomes" /></label>
            <div className="mt-5 flex items-center justify-between gap-4 rounded-xl border border-blue-100 bg-blue-50/60 p-4"><div><p className="text-[10px] font-bold uppercase tracking-wide text-blue-600">Canonical project identity</p><p className="mt-1 text-xs text-blue-900"><strong>Primary key:</strong> assigned during capture · <strong>Application key:</strong> {applicationKey || 'required'}</p></div><div className="text-right"><p className="text-[10px] font-bold uppercase tracking-wide text-blue-600">Analysis objective</p><p className="mt-1 text-xs font-semibold text-blue-900">Requirements discovery</p></div></div>
            <div className="mt-5 grid gap-2 sm:grid-cols-2 lg:grid-cols-3">{ANALYSIS_SCOPES.map(item => { const ScopeIcon = item.icon; const checked = scope.includes(item.id); return <button key={item.id} type="button" aria-pressed={checked} onClick={() => toggleScope(item.id)} className={`flex items-center gap-2 rounded-xl border p-3 text-left text-xs font-semibold transition ${checked ? 'border-blue-200 bg-blue-50 text-blue-800' : 'border-slate-200 text-slate-500 hover:bg-slate-50'}`}><span className={`flex h-5 w-5 items-center justify-center rounded-md ${checked ? 'bg-blue-600 text-white' : 'bg-slate-100'}`}>{checked ? <Check className="h-3 w-3" /> : <ScopeIcon className="h-3 w-3" />}</span>{item.label}</button> })}</div>
          </div>
          {uploading && <div className="mt-5 rounded-xl border border-blue-200 bg-blue-50 p-4"><div className="flex justify-between text-xs font-semibold text-blue-800"><span>Creating immutable project snapshot</span><span>{Math.round(progress * 100)}%</span></div><div className="mt-2 h-2 overflow-hidden rounded-full bg-blue-100"><div className="h-full rounded-full bg-blue-600 transition-all" style={{ width: `${Math.max(3, Math.round(progress * 100))}%` }} /></div></div>}
          {uploaded && <div className="mt-5 space-y-3"><p className="flex items-center gap-2 rounded-xl border border-emerald-200 bg-emerald-50 p-4 text-sm font-semibold text-emerald-800"><CheckCircle2 className="h-5 w-5" />{projectLabel(uploaded.project)} is ready · {uploaded.file_count} files captured.</p><ProjectIdentityBanner project={uploaded.project} /></div>}
          <div className="mt-6 flex justify-end"><button type="button" onClick={capture} disabled={!files.length || uploading || !scope.length || !clientName.trim() || !applicationName.trim() || !applicationKey.trim()} className="inline-flex items-center justify-center rounded-xl bg-blue-600 px-6 py-3 text-sm font-bold text-white shadow-lg shadow-blue-600/20 transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-40">{uploading ? <LoaderCircle className="mr-2 h-4 w-4 animate-spin" /> : <Sparkles className="mr-2 h-4 w-4" />}Capture & start discovery<ChevronRight className="ml-2 h-4 w-4" /></button></div>
        </div>
      </section>

      <aside className="space-y-6">
        <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-[0_12px_35px_rgba(15,23,42,0.05)]"><div className="flex items-center justify-between"><div><p className="text-[10px] font-bold uppercase tracking-[0.14em] text-emerald-600">Analysis scope</p><h2 className="mt-1 text-base font-bold text-slate-900">Evidence coverage</h2></div><ShieldCheck className="h-6 w-6 text-emerald-500" /></div><div className="mt-4 space-y-3">{ANALYSIS_SCOPES.map(item => <div key={item.id} className="flex items-center gap-3 text-xs text-slate-600"><CheckCircle2 className={`h-4 w-4 ${scope.includes(item.id) ? 'text-emerald-500' : 'text-slate-200'}`} /><span>{item.label}</span></div>)}</div><p className="mt-5 rounded-xl bg-amber-50 p-3 text-[11px] leading-5 text-amber-800">Include dependency manifests and schemas to improve traceability and document accuracy.</p></section>
        <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-[0_12px_35px_rgba(15,23,42,0.05)]">
          <div className="flex items-center justify-between gap-4"><div><p className="text-[10px] font-bold uppercase tracking-[0.14em] text-blue-600">{projects.length} available</p><h2 className="mt-1 text-base font-bold text-slate-900">Existing projects</h2></div><FolderKanban className="h-5 w-5 text-slate-300" /></div>
          <div className="mt-4 max-h-[420px] space-y-2 overflow-auto pr-1">{projects.length ? projects.map(project => { const selected = selectedProjectId === project.id; return <button type="button" key={project.id} aria-pressed={selected} onClick={() => setSelectedProjectId(project.id)} className={`flex w-full items-center gap-3 rounded-xl border p-3 text-left transition-all ${selected ? 'border-blue-400 bg-blue-50 shadow-sm ring-4 ring-blue-500/[0.06]' : 'border-slate-200 bg-white hover:border-blue-200 hover:shadow-sm'}`}><FolderKanban className={`h-4 w-4 shrink-0 ${selected ? 'text-blue-600' : 'text-slate-400'}`} /><div className="min-w-0 flex-1"><p className="truncate text-sm font-semibold text-slate-800">{projectLabel(project)}</p><p className="mt-0.5 truncate text-[11px] text-slate-500">{project.status} · {new Date(project.created_at).toLocaleDateString()}</p></div>{selected ? <CheckCircle2 className="h-5 w-5 shrink-0 text-blue-600" /> : <ChevronRight className="h-4 w-4 shrink-0 text-slate-300" />}</button> }) : <p className="text-sm text-slate-500">No projects have been uploaded yet.</p>}</div>
          {selectedProjectId && <div className="mt-4 rounded-xl border border-blue-200 bg-blue-50/60 p-4"><p className="text-[10px] font-bold uppercase tracking-wide text-blue-600">Continue with selected project</p><div className="mt-3 grid gap-2"><button type="button" onClick={() => navigate(`/requirements/brd?project=${encodeURIComponent(selectedProjectId)}`)} className="flex items-center justify-between rounded-lg bg-blue-600 px-3 py-2.5 text-xs font-semibold text-white shadow-sm hover:bg-blue-700"><span>Generate BRD</span><ChevronRight className="h-4 w-4" /></button><button type="button" onClick={() => navigate(`/requirements/fsd?project=${encodeURIComponent(selectedProjectId)}`)} className="flex items-center justify-between rounded-lg bg-white px-3 py-2.5 text-xs font-semibold text-blue-700 ring-1 ring-blue-200 hover:bg-blue-50"><span>Generate FSD</span><ChevronRight className="h-4 w-4" /></button><button type="button" onClick={() => navigate(`/requirements/knowledge-graph?project=${encodeURIComponent(selectedProjectId)}`)} className="flex items-center justify-between rounded-lg bg-white px-3 py-2.5 text-xs font-semibold text-slate-700 ring-1 ring-slate-200 hover:bg-slate-50"><span>Explore knowledge graph</span><ChevronRight className="h-4 w-4" /></button></div></div>}
        </section>
      </aside>
    </div>
  </PageFrame>
}

function architectureValue(value, fallback = 'To be confirmed') {
  if (Array.isArray(value)) return value.filter(Boolean).join(', ') || fallback
  if (value && typeof value === 'object') return Object.values(value).filter(item => typeof item === 'string').join(', ') || fallback
  return String(value || fallback)
}

function useProjectArtifact(kind) {
  const [searchParams, setSearchParams] = useSearchParams()
  const [projects, setProjects] = useState([])
  const [projectId, setProjectId] = useState('')
  const [project, setProject] = useState(null)
  const [artifact, setArtifact] = useState(null)
  const [loading, setLoading] = useState(false)
  useEffect(() => { listProjects().then(result => { const values = result.projects || []; const requested = searchParams.get('project'); setProjects(values); setProjectId(current => current || (values.some(item => item.id === requested) ? requested : values[0]?.id || '')) }).catch(() => toast.error('Could not load projects')) }, []) // eslint-disable-line react-hooks/exhaustive-deps
  useEffect(() => {
    setProject(null); setArtifact(null)
    if (!projectId) return
    setLoading(true)
    getProject(projectId).then(async value => {
      setProject(value)
      const snapshot = (value.snapshots || []).find(item => item.kind === kind)
      if (snapshot) setArtifact((await getSnapshotArtifact(projectId, snapshot.id)).artifact)
    }).catch(() => {}).finally(() => setLoading(false))
  }, [projectId, kind])
  const selectProject = value => { setProjectId(value); setSearchParams(value ? { project: value } : {}) }
  return { projects, projectId, project, artifact, loading, selectProject }
}

function RequirementsProjectPicker({ projects, projectId, onChange }) {
  return <label className="block text-xs font-semibold uppercase tracking-wide text-slate-500">Governed project<select className={`${fieldClass} mt-2`} value={projectId} onChange={event => onChange(event.target.value)}><option value="">Select a project</option>{projects.map(project => <option key={project.id} value={project.id}>{projectLabel(project)}</option>)}</select></label>
}

function ProjectIdentityBanner({ identity, project }) {
  const configuration = project?.configuration || {}
  const value = {
    project_id: identity?.project_id || project?.id,
    project_name: identity?.project_name || project?.name,
    application_key: identity?.application_key || configuration.application_key || configuration.project_key,
    client_name: identity?.client_name || configuration.client_name || configuration.customer,
    application_owner: identity?.application_owner || configuration.application_owner,
    business_unit: identity?.business_unit || configuration.business_unit,
  }
  if (!value.project_id) return null
  return <div className="grid gap-3 rounded-xl border border-blue-100 bg-gradient-to-r from-blue-50 to-white p-4 sm:grid-cols-2 xl:grid-cols-4"><div><p className="text-[9px] font-bold uppercase tracking-wider text-blue-500">Project primary key</p><p className="mt-1 font-mono text-xs font-bold text-blue-950">{value.project_id}</p></div><div><p className="text-[9px] font-bold uppercase tracking-wider text-blue-500">Project / application</p><p className="mt-1 truncate text-xs font-bold text-slate-800">{value.project_name} · {value.application_key || 'Key not captured'}</p></div><div><p className="text-[9px] font-bold uppercase tracking-wider text-blue-500">Client</p><p className="mt-1 truncate text-xs font-bold text-slate-800">{value.client_name || 'Not captured'}</p></div><div><p className="text-[9px] font-bold uppercase tracking-wider text-blue-500">Ownership</p><p className="mt-1 truncate text-xs font-bold text-slate-800">{[value.business_unit, value.application_owner].filter(Boolean).join(' · ') || 'Not captured'}</p></div></div>
}

function TargetArchitectureReview() {
  const navigate = useNavigate()
  const { projects, projectId, project, artifact: plan, loading, selectProject } = useProjectArtifact('plans')
  const architecture = plan?.target_architecture || {}
  const domains = (plan?.modules_and_domains || []).slice(0, 8)
  const services = (domains.length ? domains : ['Application']).slice(0, 4)
  const technologies = [...new Set([...(plan?.target_technologies || []), architecture.deployment].filter(Boolean))]
  const principles = [
    architecture.style && `Architecture: ${architectureValue(architecture.style)}`,
    'Domain-aligned service boundaries', 'API-first interface contracts',
    architecture.deployment && `Deployment: ${architectureValue(architecture.deployment)}`,
    plan?.security_changes?.length ? 'Security by design' : 'Least-privilege access controls',
    'Observable and independently scalable components',
  ].filter(Boolean)
  const interfaceCount = plan?.interfaces_affected?.length || 0

  return <PageFrame title="Target Architecture Review" description="Review the generated target topology, domain boundaries, technology choices, and engineering principles before forward engineering begins." step={4}>
    <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-[0_12px_35px_rgba(15,23,42,0.06)]"><RequirementsProjectPicker projects={projects} projectId={projectId} onChange={selectProject} /><div className="mt-4"><ProjectIdentityBanner project={project} /></div></section>
    {loading ? <div className="flex min-h-72 items-center justify-center"><LoaderCircle className="h-8 w-8 animate-spin text-blue-600" /></div> : !plan ? <section className="mt-6 rounded-2xl border border-dashed border-slate-300 bg-white py-20 text-center"><Boxes className="mx-auto h-10 w-10 text-slate-300" /><p className="mt-4 text-sm font-bold text-slate-700">Target architecture is not available yet</p><p className="mt-1 text-xs text-slate-500">Analyze this project and generate its governed modernization plan first.</p></section> : <>
      <div className="mt-6 flex items-center gap-3 rounded-xl border border-emerald-200 bg-emerald-50 p-4 text-sm font-semibold text-emerald-800"><CheckCircle2 className="h-5 w-5" />Requirements analysis complete. Review the target architecture before proceeding.</div>
      <div className="mt-6 grid gap-6 xl:grid-cols-[320px_minmax(0,1fr)]">
        <section className="rounded-2xl border border-slate-200 bg-white p-5"><p className="text-[10px] font-bold uppercase tracking-[0.14em] text-blue-600">Business domains identified · {domains.length}</p><div className="mt-4 space-y-2">{domains.length ? domains.map((domain, index) => <div key={String(domain)} className="flex items-start gap-3 rounded-xl border border-slate-100 bg-slate-50 p-3"><span className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-lg ${['bg-blue-100 text-blue-600', 'bg-violet-100 text-violet-600', 'bg-amber-100 text-amber-600', 'bg-emerald-100 text-emerald-600'][index % 4]}`}><Boxes className="h-4 w-4" /></span><div><p className="text-xs font-bold text-slate-800">{String(domain).split('/').pop()}</p><p className="mt-1 text-[10px] leading-4 text-slate-500">Bounded capability discovered from project structure</p></div></div>) : <p className="text-xs text-slate-500">The plan did not expose explicit domain modules.</p>}</div></section>
        <section className="rounded-2xl border border-slate-200 bg-white p-5"><div className="flex items-center justify-between"><div><p className="text-[10px] font-bold uppercase tracking-[0.14em] text-blue-600">High-level architecture</p><h2 className="mt-1 text-base font-bold text-slate-900">{architectureValue(architecture.style, 'Target application topology')}</h2></div><Network className="h-6 w-6 text-blue-500" /></div>
          <div className="mt-6 overflow-x-auto rounded-2xl border border-slate-100 bg-[radial-gradient(circle_at_center,#fff_0%,#f8fafc_100%)] p-6"><div className="mx-auto flex min-w-[620px] max-w-4xl flex-col items-center"><div className="rounded-xl border border-blue-200 bg-blue-50 px-6 py-3 text-center shadow-sm"><ShieldCheck className="mx-auto h-5 w-5 text-blue-600" /><p className="mt-1 text-xs font-bold text-blue-900">API Gateway / Experience Layer</p></div><div className="h-8 w-px bg-slate-300" /><div className="grid w-full grid-cols-4 gap-3">{services.map((service, index) => <div key={String(service)} className={`rounded-xl border p-3 text-center shadow-sm ${['border-blue-200 bg-blue-50', 'border-emerald-200 bg-emerald-50', 'border-amber-200 bg-amber-50', 'border-violet-200 bg-violet-50'][index]}`}><Server className="mx-auto h-5 w-5 text-slate-600" /><p className="mt-2 truncate text-[11px] font-bold text-slate-800">{String(service).split('/').pop()}</p><p className="mt-0.5 text-[9px] text-slate-500">Domain service</p></div>)}</div><div className="h-8 w-px bg-slate-300" /><div className="rounded-xl border border-violet-200 bg-violet-50 px-8 py-3 text-center"><Workflow className="mx-auto h-5 w-5 text-violet-600" /><p className="mt-1 text-xs font-bold text-violet-900">Integration & Event Layer</p></div><div className="h-8 w-px bg-slate-300" /><div className="rounded-xl border border-emerald-200 bg-emerald-50 px-8 py-3 text-center"><Database className="mx-auto h-5 w-5 text-emerald-600" /><p className="mt-1 text-xs font-bold text-emerald-900">{architectureValue(architecture.database, 'Managed persistence')}</p></div></div></div>
        </section>
      </div>
      <div className="mt-6 grid gap-6 lg:grid-cols-2"><section className="rounded-2xl border border-slate-200 bg-white p-5"><p className="text-[10px] font-bold uppercase tracking-[0.14em] text-violet-600">Technology stack</p><div className="mt-4 grid gap-2 sm:grid-cols-2">{technologies.map(value => <div key={String(value)} className="flex items-center gap-3 rounded-xl bg-slate-50 p-3 text-xs font-semibold text-slate-700"><Code2 className="h-4 w-4 text-violet-500" />{architectureValue(value)}</div>)}</div></section><section className="rounded-2xl border border-slate-200 bg-white p-5"><p className="text-[10px] font-bold uppercase tracking-[0.14em] text-emerald-600">Architecture principles</p><div className="mt-4 grid gap-2 sm:grid-cols-2">{principles.map(value => <div key={value} className="flex items-start gap-2 text-xs leading-5 text-slate-600"><CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-emerald-500" />{value}</div>)}</div></section></div>
      <section className="mt-6 rounded-2xl border border-slate-200 bg-white p-5"><p className="text-[10px] font-bold uppercase tracking-[0.14em] text-blue-600">Architecture coverage</p><div className="mt-4 grid grid-cols-2 gap-3 lg:grid-cols-4">{[['Domain modules', domains.length], ['Target technologies', technologies.length], ['Interfaces mapped', interfaceCount], ['Security controls', plan.security_changes?.length || 0]].map(([label, value]) => <div key={label} className="rounded-xl bg-slate-50 p-4 text-center"><p className="text-2xl font-bold text-blue-700">{value}</p><p className="mt-1 text-xs text-slate-500">{label}</p></div>)}</div><div className="mt-5 flex justify-end"><button type="button" onClick={() => navigate('/projects')} className="inline-flex items-center rounded-xl bg-blue-600 px-6 py-3 text-sm font-bold text-white shadow-lg shadow-blue-600/20 hover:bg-blue-700">Approve architecture & start forward engineering<ChevronRight className="ml-2 h-4 w-4" /></button></div></section>
    </>}
  </PageFrame>
}

function GeneratedAssetsRepository() {
  const [searchParams, setSearchParams] = useSearchParams()
  const [projects, setProjects] = useState([])
  const [projectId, setProjectId] = useState('')
  const [catalog, setCatalog] = useState(null)
  const [loading, setLoading] = useState(false)
  const [downloading, setDownloading] = useState(false)
  const [view, setView] = useState('repository')
  useEffect(() => { listProjects().then(result => { const values = result.projects || []; const requested = searchParams.get('project'); setProjects(values); setProjectId(values.some(item => item.id === requested) ? requested : values[0]?.id || '') }).catch(() => toast.error('Could not load projects')) }, []) // eslint-disable-line react-hooks/exhaustive-deps
  useEffect(() => { setCatalog(null); if (!projectId) return; setLoading(true); getGeneratedAssets(projectId).then(setCatalog).catch(() => {}).finally(() => setLoading(false)) }, [projectId])
  const selectProject = value => { setProjectId(value); setSearchParams(value ? { project: value } : {}) }
  const download = async () => { setDownloading(true); try { const blob = await downloadGeneratedAssets(projectId); const link = document.createElement('a'); link.href = URL.createObjectURL(blob); link.download = `${projectId}-generated-assets.zip`; link.click(); URL.revokeObjectURL(link.href) } catch (error) { toast.error(error?.response?.data?.detail || 'Could not download generated assets') } finally { setDownloading(false) } }
  const summary = catalog?.summary || {}
  const folders = [...new Set((catalog?.files || []).map(file => file.path.split('/')[0]).filter((value, index, values) => value && values.indexOf(value) === index))]
  return <PageFrame title="Generated Assets Repository" description="Inspect every forward-engineered source file, contract, database artifact, test, pipeline, and deployment asset from the governed output snapshot." step={6}>
    <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-[0_12px_35px_rgba(15,23,42,0.06)]"><RequirementsProjectPicker projects={projects} projectId={projectId} onChange={selectProject} />{catalog && <div className="mt-4"><ProjectIdentityBanner identity={catalog.project_identity} /></div>}</section>
    {loading ? <div className="flex min-h-72 items-center justify-center"><LoaderCircle className="h-8 w-8 animate-spin text-blue-600" /></div> : !catalog ? <section className="mt-6 rounded-2xl border border-dashed border-slate-300 bg-white py-20 text-center"><FolderKanban className="mx-auto h-10 w-10 text-slate-300" /><p className="mt-4 text-sm font-bold text-slate-700">No generated code is available yet</p><p className="mt-1 text-xs text-slate-500">Complete forward engineering for the selected project to populate this repository.</p></section> : <>
      <div className="mt-6 flex items-center gap-3 rounded-xl border border-emerald-200 bg-emerald-50 p-4 text-sm font-semibold text-emerald-800"><CheckCircle2 className="h-5 w-5" />Forward engineering completed. Generated assets are ready for review and download.</div>
      <div className="mt-6 grid grid-cols-2 gap-3 lg:grid-cols-5">{[['Generated files', summary.files, FileCode2], ['Lines of code', summary.lines, Code2], ['Database assets', summary.type_counts?.Database || 0, Database], ['Modules', summary.modules, Boxes], ['Pipelines', summary.type_counts?.['Pipeline / deployment'] || 0, Cloud]].map(([label, value, StatIcon]) => <div key={label} className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm"><StatIcon className="h-5 w-5 text-blue-600" /><p className="mt-3 text-2xl font-bold text-slate-900">{Number(value || 0).toLocaleString()}</p><p className="mt-1 text-xs text-slate-500">{label}</p></div>)}</div>
      <section className="mt-6 overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-[0_16px_45px_rgba(15,23,42,0.06)]"><div className="flex items-center justify-between border-b border-slate-200 px-5"><div className="flex"><button type="button" onClick={() => setView('repository')} className={`border-b-2 px-4 py-4 text-xs font-bold ${view === 'repository' ? 'border-blue-600 text-blue-700' : 'border-transparent text-slate-500'}`}>Repository view</button><button type="button" onClick={() => setView('catalog')} className={`border-b-2 px-4 py-4 text-xs font-bold ${view === 'catalog' ? 'border-blue-600 text-blue-700' : 'border-transparent text-slate-500'}`}>Artifact catalog</button></div><span className="text-[11px] text-slate-400">Snapshot v{catalog.snapshot?.version}</span></div>
        <div className="grid min-h-[440px] lg:grid-cols-[260px_minmax(0,1fr)]"><aside className="border-b border-slate-200 bg-slate-50 p-4 lg:border-b-0 lg:border-r"><p className="text-[10px] font-bold uppercase tracking-wide text-slate-400">{projectId}/</p><div className="mt-3 space-y-1">{folders.map(folder => <div key={folder} className="flex items-center gap-2 rounded-lg px-2 py-2 text-xs font-semibold text-slate-600"><FolderOpen className="h-4 w-4 text-blue-500" />{folder}/</div>)}</div></aside><div className="overflow-auto"><table className="w-full min-w-[720px] text-left text-xs"><thead className="sticky top-0 bg-slate-50 text-[10px] uppercase tracking-wide text-slate-400"><tr><th className="px-4 py-3 font-semibold">Name</th><th className="px-4 py-3 font-semibold">Type</th><th className="px-4 py-3 font-semibold">Size</th><th className="px-4 py-3 font-semibold">Lines</th><th className="px-4 py-3 font-semibold">Generated</th></tr></thead><tbody className="divide-y divide-slate-100">{(catalog.files || []).map(file => <tr key={file.path} className="hover:bg-blue-50/40"><td className="max-w-[420px] px-4 py-3"><div className="flex items-center gap-2"><FileCode2 className="h-4 w-4 shrink-0 text-blue-500" /><span className="truncate font-medium text-slate-700" title={file.path}>{view === 'catalog' ? file.name : file.path}</span></div></td><td className="px-4 py-3 text-slate-500">{file.type}</td><td className="px-4 py-3 text-slate-500">{fileSize(file.size)}</td><td className="px-4 py-3 text-slate-500">{file.lines.toLocaleString()}</td><td className="px-4 py-3 text-slate-500">{new Date(file.generated_at).toLocaleString()}</td></tr>)}</tbody></table></div></div>
        <div className="flex flex-wrap justify-end gap-3 border-t border-slate-200 bg-slate-50 px-5 py-4"><button type="button" disabled={downloading} onClick={download} className="inline-flex items-center rounded-xl bg-blue-600 px-5 py-2.5 text-xs font-bold text-white shadow-md shadow-blue-600/20 hover:bg-blue-700 disabled:opacity-50">{downloading ? <LoaderCircle className="mr-2 h-4 w-4 animate-spin" /> : <Download className="mr-2 h-4 w-4" />}Download complete package (ZIP)</button></div>
      </section>
    </>}
  </PageFrame>
}

function KnowledgeGraph({ graph }) {
  const [selected, setSelected] = useState(null)
  const [hovered, setHovered] = useState(null)
  const [activeType, setActiveType] = useState('all')
  const [zoom, setZoom] = useState(1)
  const nodes = (graph?.nodes || []).slice(0, 100)
  const visibleIds = new Set(nodes.map(node => String(node.id)))
  const edges = (graph?.edges || []).filter(edge => visibleIds.has(String(edge.source)) && visibleIds.has(String(edge.target)))
  const typeCounts = nodes.reduce((counts, node) => ({ ...counts, [node.type]: (counts[node.type] || 0) + 1 }), {})
  const selectedId = selected ? String(selected.id) : ''
  const connectedIds = new Set(selectedId ? edges.flatMap(edge => String(edge.source) === selectedId ? [String(edge.target)] : String(edge.target) === selectedId ? [String(edge.source)] : []) : [])
  const connectedEdges = selectedId ? edges.filter(edge => String(edge.source) === selectedId || String(edge.target) === selectedId) : []
  const positions = useMemo(() => Object.fromEntries(nodes.map((node, index) => {
    const ring = index < 14 ? 110 : index < 36 ? 205 : index < 66 ? 300 : 385
    const ringStart = index < 14 ? 0 : index < 36 ? 14 : index < 66 ? 36 : 66
    const ringCount = index < 14 ? Math.min(14, nodes.length) : index < 36 ? Math.min(22, nodes.length - 14) : index < 66 ? Math.min(30, nodes.length - 36) : Math.max(1, nodes.length - 66)
    const angle = ((index - ringStart) / ringCount) * Math.PI * 2 - Math.PI / 2
    return [String(node.id), { x: 450 + Math.cos(angle) * ring, y: 410 + Math.sin(angle) * ring }]
  })), [nodes])
  if (!nodes.length) return <p className="text-sm text-ink-muted">The generated graph has no nodes.</p>
  return <div className="space-y-5">
    <div className="grid gap-3 sm:grid-cols-3">
      <div className="rounded-2xl border border-slate-200 bg-gradient-to-br from-blue-50 to-white p-4"><div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-slate-500"><Network className="h-4 w-4 text-blue-600" />Entities</div><p className="mt-2 text-2xl font-bold text-slate-900">{nodes.length}</p></div>
      <div className="rounded-2xl border border-slate-200 bg-gradient-to-br from-violet-50 to-white p-4"><div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-slate-500"><GitBranch className="h-4 w-4 text-violet-600" />Relationships</div><p className="mt-2 text-2xl font-bold text-slate-900">{edges.length}</p></div>
      <div className="rounded-2xl border border-slate-200 bg-gradient-to-br from-emerald-50 to-white p-4"><div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-slate-500"><Sparkles className="h-4 w-4 text-emerald-600" />Requirement types</div><p className="mt-2 text-2xl font-bold text-slate-900">{Object.keys(typeCounts).length}</p></div>
    </div>

    <div className="flex flex-wrap gap-2">
      <button type="button" onClick={() => setActiveType('all')} className={`rounded-full border px-3 py-1.5 text-xs font-semibold transition ${activeType === 'all' ? 'border-blue-600 bg-blue-600 text-white' : 'border-slate-200 bg-white text-slate-600 hover:border-slate-300'}`}>All · {nodes.length}</button>
      {Object.entries(typeCounts).map(([type, count]) => <button type="button" key={type} onClick={() => setActiveType(type)} className={`inline-flex items-center gap-2 rounded-full border px-3 py-1.5 text-xs font-semibold capitalize transition ${activeType === type ? 'border-slate-700 bg-slate-800 text-white' : 'border-slate-200 bg-white text-slate-600 hover:border-slate-300'}`}><span className="h-2 w-2 rounded-full" style={{ background: GRAPH_COLORS[type] || '#94a3b8' }} />{type} · {count}</button>)}
    </div>

    <div className="grid overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-[0_18px_50px_rgba(15,23,42,0.08)] xl:grid-cols-[minmax(0,1fr)_320px]">
      <div className="relative h-[620px] min-w-0 overflow-hidden bg-[radial-gradient(circle_at_center,_#ffffff_0%,_#f8fafc_62%,_#eef4fb_100%)]">
        <div className="absolute right-4 top-4 z-10 flex items-center gap-1 rounded-xl border border-slate-200 bg-white/95 p-1.5 shadow-lg backdrop-blur">
          <button type="button" title="Zoom out" onClick={() => setZoom(value => Math.max(0.72, value - 0.12))} className="rounded-lg p-2 text-slate-600 hover:bg-slate-100"><Minus className="h-4 w-4" /></button>
          <span className="min-w-12 text-center text-[11px] font-semibold text-slate-500">{Math.round(zoom * 100)}%</span>
          <button type="button" title="Zoom in" onClick={() => setZoom(value => Math.min(1.5, value + 0.12))} className="rounded-lg p-2 text-slate-600 hover:bg-slate-100"><Plus className="h-4 w-4" /></button>
        </div>
        <div className="absolute left-4 top-4 z-10 rounded-full border border-blue-100 bg-white/90 px-3 py-1.5 text-[11px] font-medium text-slate-500 shadow-sm">Select a node to inspect its evidence and relationships</div>
        <svg viewBox="0 0 900 820" preserveAspectRatio="xMidYMid meet" className="h-full w-full" role="img" aria-label={graph.title || 'Requirements knowledge graph'}>
          <defs><pattern id="requirements-grid" width="32" height="32" patternUnits="userSpaceOnUse"><path d="M 32 0 L 0 0 0 32" fill="none" stroke="#cbd5e1" strokeOpacity="0.22" strokeWidth="1" /></pattern></defs>
          <rect width="900" height="820" fill="url(#requirements-grid)" />
          <g transform={`translate(450 410) scale(${zoom}) translate(-450 -410)`}>
            {edges.map((edge, index) => { const a = positions[String(edge.source)]; const b = positions[String(edge.target)]; const emphasized = selectedId && (String(edge.source) === selectedId || String(edge.target) === selectedId); return a && b ? <line key={`${edge.source}-${edge.target}-${index}`} x1={a.x} y1={a.y} x2={b.x} y2={b.y} stroke={emphasized ? '#2563eb' : '#94a3b8'} strokeOpacity={selectedId ? (emphasized ? 0.75 : 0.09) : 0.26} strokeWidth={emphasized ? 2.4 : 1.2} /> : null })}
            {nodes.map((node, index) => { const id = String(node.id); const point = positions[id]; const active = selectedId === id; const related = connectedIds.has(id); const hover = hovered === id; const typeVisible = activeType === 'all' || node.type === activeType; const faded = !typeVisible || (selectedId && !active && !related); const showLabel = active || hover || related || (index < 12 && !selectedId && activeType === 'all'); return <g key={id} onMouseEnter={() => setHovered(id)} onMouseLeave={() => setHovered(null)} onClick={() => setSelected(active ? null : node)} className="cursor-pointer" opacity={faded ? 0.16 : 1}>
              {(active || hover) && <circle cx={point.x} cy={point.y} r="24" fill={GRAPH_COLORS[node.type] || '#64748b'} fillOpacity="0.14" />}
              <circle cx={point.x} cy={point.y} r={active ? 15 : related || hover ? 13 : 10} fill={GRAPH_COLORS[node.type] || '#64748b'} stroke="#fff" strokeWidth="3" style={{ filter: active || hover ? 'drop-shadow(0 4px 8px rgba(15,23,42,.25))' : 'none' }} />
              {showLabel && <text x={point.x} y={point.y + (active ? 29 : 25)} fill="#334155" fontSize={active ? 12 : 10} fontWeight={active ? 700 : 600} textAnchor="middle" style={{ paintOrder: 'stroke', stroke: '#fff', strokeWidth: 4, strokeLinejoin: 'round' }}>{String(node.label || node.id).slice(0, 27)}</text>}
            </g> })}
          </g>
        </svg>
      </div>

      <aside className="border-t border-slate-200 bg-slate-50/80 p-5 xl:border-l xl:border-t-0">
        {selected ? <div>
          <div className="flex items-start justify-between gap-3"><div><span className="inline-flex items-center gap-2 rounded-full bg-white px-2.5 py-1 text-[10px] font-bold uppercase tracking-wider text-slate-600 shadow-sm"><span className="h-2 w-2 rounded-full" style={{ background: GRAPH_COLORS[selected.type] || '#94a3b8' }} />{selected.type}</span><h3 className="mt-3 text-lg font-bold leading-6 text-slate-900">{selected.label}</h3></div><button type="button" onClick={() => setSelected(null)} className="text-xs font-semibold text-blue-600 hover:text-blue-800">Clear</button></div>
          <p className="mt-3 text-sm leading-6 text-slate-600">{selected.description || 'No description was provided for this entity.'}</p>
          {selected.evidence_source_path && <div className="mt-4 rounded-xl border border-slate-200 bg-white p-3"><p className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Source evidence</p><p className="mt-1 break-all font-mono text-[11px] leading-5 text-slate-600">{selected.evidence_source_path}</p></div>}
          <div className="mt-5"><p className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Connected relationships · {connectedEdges.length}</p><div className="mt-2 space-y-2">{connectedEdges.slice(0, 10).map((edge, index) => { const otherId = String(edge.source) === selectedId ? String(edge.target) : String(edge.source); const other = nodes.find(node => String(node.id) === otherId); return <button type="button" key={`${otherId}-${index}`} onClick={() => other && setSelected(other)} className="w-full rounded-xl border border-slate-200 bg-white p-3 text-left transition hover:border-blue-300"><p className="text-[10px] font-semibold uppercase text-blue-600">{edge.relationship?.replaceAll('_', ' ')}</p><p className="mt-1 truncate text-xs font-semibold text-slate-800">{other?.label || otherId}</p></button> })}</div></div>
        </div> : <div>
          <span className="inline-flex rounded-full bg-blue-100 px-2.5 py-1 text-[10px] font-bold uppercase tracking-wider text-blue-700">Graph overview</span>
          <h3 className="mt-3 text-lg font-bold text-slate-900">Requirements intelligence</h3>
          <p className="mt-2 text-sm leading-6 text-slate-600">{graph.summary || 'Explore how business requirements, functional specifications, data, rules, actors, and integrations connect across the source project.'}</p>
          <div className="mt-5 border-t border-slate-200 pt-5"><p className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Key entities</p><div className="mt-2 space-y-1">{nodes.slice(0, 8).map(node => <button type="button" key={node.id} onClick={() => setSelected(node)} className="flex w-full items-center gap-2 rounded-lg px-2 py-2 text-left text-xs font-medium text-slate-700 hover:bg-white"><span className="h-2 w-2 rounded-full" style={{ background: GRAPH_COLORS[node.type] || '#94a3b8' }} /><span className="truncate">{node.label}</span></button>)}</div></div>
        </div>}
      </aside>
    </div>
  </div>
}

function plainMarkdown(value = '') {
  return value.replace(/\*\*|__|`|~~/g, '').replace(/\[([^\]]+)\]\([^)]*\)/g, '$1').trim()
}

function DocumentPreview({ content }) {
  const lines = String(content || '').split(/\r?\n/)
  const blocks = []
  let index = 0
  while (index < lines.length) {
    const line = lines[index].trim()
    if (!line) { index += 1; continue }
    if (line.startsWith('|') && line.endsWith('|')) {
      const rows = []
      while (index < lines.length && lines[index].trim().startsWith('|') && lines[index].trim().endsWith('|')) {
        rows.push(lines[index].trim().slice(1, -1).split('|').map(plainMarkdown)); index += 1
      }
      const dataRows = rows.filter(row => !row.every(cell => /^:?-{3,}:?$/.test(cell.replaceAll(' ', ''))))
      blocks.push(<div key={`table-${index}`} className="my-6 overflow-x-auto rounded-xl border border-slate-200"><table className="w-full border-collapse text-left text-sm"><thead className="bg-slate-50 text-xs uppercase tracking-wide text-slate-500"><tr>{dataRows[0]?.map((cell, cellIndex) => <th key={cellIndex} className="border-b border-slate-200 px-4 py-3 font-semibold">{cell}</th>)}</tr></thead><tbody className="divide-y divide-slate-100">{dataRows.slice(1).map((row, rowIndex) => <tr key={rowIndex} className="hover:bg-slate-50/70">{row.map((cell, cellIndex) => <td key={cellIndex} className="px-4 py-3 align-top leading-6 text-slate-600">{cell}</td>)}</tr>)}</tbody></table></div>)
      continue
    }
    const heading = line.match(/^(#{1,6})\s+(.+)$/)
    if (heading) {
      const text = plainMarkdown(heading[2])
      blocks.push(heading[1].length <= 2 ? <h2 key={index} className="mb-3 mt-8 border-b border-slate-200 pb-3 text-xl font-bold text-slate-900 first:mt-0">{text}</h2> : <h3 key={index} className="mb-2 mt-6 text-base font-bold text-slate-800">{text}</h3>)
    } else if (/^[-*+]\s+/.test(line)) {
      blocks.push(<div key={index} className="my-2 flex gap-3 text-sm leading-7 text-slate-600"><span className="mt-3 h-1.5 w-1.5 shrink-0 rounded-full bg-blue-500" /><span>{plainMarkdown(line.replace(/^[-*+]\s+/, ''))}</span></div>)
    } else if (/^\d+[.)]\s+/.test(line)) {
      const match = line.match(/^(\d+)[.)]\s+(.+)$/)
      blocks.push(<div key={index} className="my-3 flex gap-3 rounded-xl border border-slate-100 bg-slate-50/70 p-3 text-sm leading-7 text-slate-600"><span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-blue-100 text-xs font-bold text-blue-700">{match[1]}</span><span>{plainMarkdown(match[2])}</span></div>)
    } else if (!/^[-*_]{3,}$/.test(line)) {
      blocks.push(<p key={index} className="my-3 text-sm leading-7 text-slate-600">{plainMarkdown(line)}</p>)
    }
    index += 1
  }
  return <article className="mx-auto max-w-5xl rounded-2xl border border-slate-200 bg-white px-6 py-7 shadow-sm lg:px-10 lg:py-9">{blocks}</article>
}

const GENERATION_STAGES = [
  { label: 'Inventory source assets', icon: Search },
  { label: 'Build dependency graph', icon: GitBranch },
  { label: 'Discover business rules', icon: Workflow },
  { label: 'Trace features to evidence', icon: FileCode2 },
  { label: 'Generate document & traceability', icon: FileText },
]

function generationProgress(job) {
  if (!job) return 8
  if (job.status === 'completed') return 100
  if (job.status === 'queued') return 12
  if (Number.isFinite(Number(job.progress))) return Math.max(1, Math.min(100, Number(job.progress)))
  const message = String(job.message || '').toLowerCase()
  if (message.includes('streamed') || message.includes('draft')) {
    const characters = Number(message.match(/[\d,]+(?= characters)/)?.[0]?.replaceAll(',', '') || 0)
    return Math.min(92, 55 + Math.round(characters / 700))
  }
  return 38
}

function GenerationProgress({ job, documentName }) {
  const progress = generationProgress(job)
  const activeStage = progress < 20 ? 0 : progress < 40 ? 1 : progress < 55 ? 2 : progress < 76 ? 3 : 4
  return <section className="mt-6 overflow-hidden rounded-2xl border border-blue-200 bg-white shadow-[0_16px_45px_rgba(37,99,235,0.10)]">
    <div className="border-b border-slate-100 bg-gradient-to-r from-blue-50 to-white px-6 py-5"><div className="flex flex-wrap items-end justify-between gap-3"><div><div className="flex items-center gap-2 text-xs font-bold uppercase tracking-[0.14em] text-blue-600"><Activity className="h-4 w-4" />Reverse engineering in progress</div><h2 className="mt-2 text-lg font-bold text-slate-950">OpenSourceLLM is generating the {documentName}</h2></div><span className="text-3xl font-bold tracking-tight text-blue-700">{progress}%</span></div><div className="mt-4 h-2.5 overflow-hidden rounded-full bg-blue-100"><div className="h-full rounded-full bg-gradient-to-r from-emerald-500 to-blue-600 transition-all duration-700" style={{ width: `${progress}%` }} /></div></div>
    <div className="grid gap-6 p-6 lg:grid-cols-[minmax(0,1fr)_330px]">
      <div><h3 className="text-xs font-bold uppercase tracking-wide text-slate-500">Processing stages</h3><div className="mt-3 divide-y divide-slate-100 rounded-xl border border-slate-200">{GENERATION_STAGES.map((stage, index) => { const StageIcon = stage.icon; const complete = index < activeStage; const active = index === activeStage; return <div key={stage.label} className="flex items-center gap-3 px-4 py-3"><span className={`flex h-7 w-7 items-center justify-center rounded-full ${complete ? 'bg-emerald-100 text-emerald-600' : active ? 'bg-blue-100 text-blue-600' : 'bg-slate-100 text-slate-400'}`}>{complete ? <Check className="h-4 w-4" /> : active ? <LoaderCircle className="h-4 w-4 animate-spin" /> : <Circle className="h-3 w-3" />}</span><StageIcon className="h-4 w-4 text-slate-400" /><span className={`flex-1 text-sm font-semibold ${active ? 'text-blue-800' : 'text-slate-700'}`}>{stage.label}</span><span className={`text-[10px] font-bold uppercase ${complete ? 'text-emerald-600' : active ? 'text-blue-600' : 'text-slate-400'}`}>{complete ? 'Completed' : active ? 'In progress' : 'Pending'}</span></div> })}</div></div>
      <div className="rounded-xl border border-slate-200 bg-slate-50 p-4"><h3 className="text-xs font-bold uppercase tracking-wide text-slate-500">Live analysis feed</h3><div className="mt-4 flex gap-3"><span className="mt-0.5 h-2 w-2 shrink-0 animate-pulse rounded-full bg-blue-500" /><div><p className="text-sm font-semibold text-slate-800">{job?.message || 'Preparing source analysis'}</p><p className="mt-1 text-xs leading-5 text-slate-500">The project remains available while generation runs. Keep this page open to follow progress.</p></div></div><div className="mt-5 grid grid-cols-2 gap-2"><div className="rounded-lg bg-white p-3 ring-1 ring-slate-200"><Clock3 className="h-4 w-4 text-blue-500" /><p className="mt-2 text-[10px] font-bold uppercase text-slate-400">Status</p><p className="mt-1 text-xs font-semibold capitalize text-slate-700">{job?.status || 'Starting'}</p></div><div className="rounded-lg bg-white p-3 ring-1 ring-slate-200"><Sparkles className="h-4 w-4 text-violet-500" /><p className="mt-2 text-[10px] font-bold uppercase text-slate-400">Engine</p><p className="mt-1 text-xs font-semibold text-slate-700">OpenSourceLLM</p></div></div></div>
    </div>
  </section>
}

function documentMetrics(content = '') {
  return {
    requirements: (content.match(/\b(?:BR|FR|FS|NFR)-?\d+/gi) || []).length,
    evidence: (content.match(/[\w./\\-]+\.(?:java|py|js|jsx|ts|tsx|cs|xml|sql|json|ya?ml)\b/gi) || []).length,
    sections: (content.match(/^#{1,4}\s+/gm) || []).length,
    tables: (content.match(/^\|.+\|$/gm) || []).length,
  }
}

function ArtifactReview({ artifact, documentType }) {
  const [tab, setTab] = useState('overview')
  const metrics = documentMetrics(artifact.content)
  const tabs = ['overview', 'requirements', 'business rules', 'process flows', 'data model', 'traceability']
  return <div>
    <div className="mb-6 flex gap-1 overflow-x-auto border-b border-slate-200">{tabs.map(item => <button key={item} type="button" onClick={() => setTab(item)} className={`whitespace-nowrap border-b-2 px-4 py-3 text-xs font-semibold capitalize transition ${tab === item ? 'border-blue-600 text-blue-700' : 'border-transparent text-slate-500 hover:text-slate-800'}`}>{item}</button>)}</div>
    {tab === 'overview' && <div className="mb-6 grid gap-3 sm:grid-cols-2 xl:grid-cols-4"><div className="rounded-xl border border-blue-100 bg-blue-50/60 p-4"><FileText className="h-5 w-5 text-blue-600" /><p className="mt-3 text-2xl font-bold text-slate-900">{metrics.requirements}</p><p className="text-xs text-slate-500">Requirement references</p></div><div className="rounded-xl border border-emerald-100 bg-emerald-50/60 p-4"><FileCode2 className="h-5 w-5 text-emerald-600" /><p className="mt-3 text-2xl font-bold text-slate-900">{metrics.evidence}</p><p className="text-xs text-slate-500">Source citations</p></div><div className="rounded-xl border border-violet-100 bg-violet-50/60 p-4"><Layers3 className="h-5 w-5 text-violet-600" /><p className="mt-3 text-2xl font-bold text-slate-900">{metrics.sections}</p><p className="text-xs text-slate-500">Document sections</p></div><div className="rounded-xl border border-amber-100 bg-amber-50/60 p-4"><GitBranch className="h-5 w-5 text-amber-600" /><p className="mt-3 text-2xl font-bold text-slate-900">{metrics.tables}</p><p className="text-xs text-slate-500">Traceability rows</p></div></div>}
    {tab !== 'overview' && <div className="mb-5 flex items-start gap-3 rounded-xl border border-blue-100 bg-blue-50 p-4"><Sparkles className="mt-0.5 h-4 w-4 shrink-0 text-blue-600" /><p className="text-xs leading-5 text-blue-800">Reviewing <strong className="capitalize">{tab}</strong> within the complete source-grounded {documentType.toUpperCase()}. Use Download DOCX for formal review and distribution.</p></div>}
    <DocumentPreview content={artifact.content} />
  </div>
}

function DocumentWorkspace({ documentType }) {
  const [searchParams, setSearchParams] = useSearchParams()
  const meta = TYPE_META[documentType]
  const Icon = meta.icon
  const [projects, setProjects] = useState([])
  const [projectId, setProjectId] = useState('')
  const [artifact, setArtifact] = useState(null)
  const [snapshot, setSnapshot] = useState(null)
  const [loading, setLoading] = useState(false)
  const [generating, setGenerating] = useState(false)
  const [generationMessage, setGenerationMessage] = useState('')
  const [generationJob, setGenerationJob] = useState(null)
  const [generationError, setGenerationError] = useState('')
  const [downloading, setDownloading] = useState(false)

  useEffect(() => { listProjects().then(result => {
    const values = result.projects || []
    const requestedProject = searchParams.get('project')
    setProjects(values)
    setProjectId(current => current || (values.some(project => project.id === requestedProject) ? requestedProject : values[0]?.id || ''))
  }).catch(() => toast.error('Could not load projects')) }, []) // eslint-disable-line react-hooks/exhaustive-deps
  useEffect(() => {
    setArtifact(null); setSnapshot(null); setGenerationError(''); setGenerationJob(null)
    if (!projectId) return
    setLoading(true)
    getRequirementDocument(projectId, documentType).then(result => { setArtifact(result.artifact); setSnapshot(result.snapshot) }).catch(() => {}).finally(() => setLoading(false))
  }, [projectId, documentType])

  const generate = async () => {
    setGenerating(true)
    setGenerationError('')
    setGenerationMessage('Submitting requirements generation…')
    setGenerationJob({ status: 'queued', message: 'Preparing the governed source snapshot' })
    try {
      const queued = await generateRequirementDocument(projectId, documentType)
      let result = queued
      let consecutivePollFailures = 0
      setGenerationJob(result)
      while (result.status === 'queued' || result.status === 'running') {
        setGenerationMessage(result.message || 'Ollama is generating the requirements artifact…')
        await new Promise(resolve => setTimeout(resolve, 2000))
        try {
          result = await getRequirementGenerationJob(queued.job_id)
          consecutivePollFailures = 0
        } catch (pollError) {
          consecutivePollFailures += 1
          if (pollError?.response?.status === 404) throw new Error('Generation was interrupted because the backend restarted and the job status was lost. Please regenerate the document.')
          if (consecutivePollFailures >= 6) throw new Error('Generation status could not be reached after multiple retries. The backend may still be processing; wait briefly and regenerate if no document appears.')
          setGenerationJob(current => ({ ...current, message: `Connection interrupted; retrying status (${consecutivePollFailures}/6)…` }))
          await new Promise(resolve => setTimeout(resolve, 3000))
          continue
        }
        setGenerationJob(result)
      }
      if (result.status === 'failed') throw new Error(result.error || 'Requirements generation failed')
      if (result.status !== 'completed' || !result.artifact) throw new Error(`Generation ended with unexpected status: ${result.status || 'unknown'}`)
      setArtifact(result.artifact); setSnapshot(result.snapshot)
      toast.success(`${meta.short} generated successfully`)
    } catch (error) {
      const message = error?.response?.data?.detail || error.message || `${meta.short} generation failed`
      setGenerationError(message)
      toast.error(message, { duration: 10000 })
    }
    finally { setGenerating(false); setGenerationMessage('') }
  }

  const download = async () => {
    setDownloading(true)
    try {
      const blob = documentType === 'knowledge_graph'
        ? new Blob([JSON.stringify(artifact, null, 2)], { type: 'application/json' })
        : await downloadRequirementDocument(projectId, documentType)
      const extension = documentType === 'knowledge_graph' ? 'json' : 'docx'
      const link = document.createElement('a'); link.href = URL.createObjectURL(blob); link.download = `${projectId}-${documentType}.${extension}`; link.click(); URL.revokeObjectURL(link.href)
    } catch (error) { toast.error(error?.response?.data?.detail || `Could not download ${meta.short}`) }
    finally { setDownloading(false) }
  }

  const selectedProject = projects.find(project => project.id === projectId)

  return <PageFrame title={meta.title} description={meta.description} step={documentType === 'knowledge_graph' ? 3 : generating ? 2 : artifact ? 3 : 2}>
    <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-[0_12px_35px_rgba(15,23,42,0.06)]">
      <div className="flex flex-col gap-3 lg:flex-row lg:items-end">
        <label className="flex-1 text-xs font-semibold uppercase tracking-wide text-ink-faint">Uploaded project<select className={`${fieldClass} mt-2`} value={projectId} onChange={event => { const value = event.target.value; setProjectId(value); setSearchParams(value ? { project: value } : {}) }}><option value="">Select a project</option>{projects.map(project => <option key={project.id} value={project.id}>{projectLabel(project)}</option>)}</select></label>
        <button type="button" disabled={!projectId || generating} onClick={generate} className="inline-flex items-center justify-center rounded-xl bg-blue-600 px-5 py-3 text-sm font-semibold text-white shadow-lg shadow-blue-600/20 transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-40">{generating ? <LoaderCircle className="mr-2 h-4 w-4 animate-spin" /> : <Icon className="mr-2 h-4 w-4" />}{artifact ? `Regenerate ${meta.short}` : `Generate ${meta.short}`}</button>
        {artifact && <button type="button" disabled={downloading} onClick={download} className="inline-flex items-center justify-center rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm font-semibold text-slate-700 shadow-sm transition hover:border-slate-300 hover:bg-slate-50 disabled:opacity-40">{downloading ? <LoaderCircle className="mr-2 h-4 w-4 animate-spin" /> : <Download className="mr-2 h-4 w-4" />}Download {documentType === 'knowledge_graph' ? 'JSON' : 'DOCX'}</button>}
      </div>
    </section>
    {generating && <GenerationProgress job={generationJob || { message: generationMessage }} documentName={meta.short} />}
    {!generating && generationError && <section role="alert" className="mt-6 rounded-2xl border border-rose-200 bg-rose-50 p-5 text-rose-900 shadow-sm"><div className="flex items-start gap-3"><AlertTriangle className="mt-0.5 h-5 w-5 shrink-0 text-rose-600" /><div><h2 className="text-sm font-bold">{meta.short} generation did not complete</h2><p className="mt-1 break-words text-sm leading-6 text-rose-800">{generationError}</p><p className="mt-2 text-xs text-rose-700">The previous generated artifact, if any, has not been replaced. Use Generate {meta.short} to retry.</p></div></div></section>}
    <section className="mt-6 rounded-2xl border border-slate-200 bg-white p-6 shadow-[0_12px_35px_rgba(15,23,42,0.05)]">
      <div className="mb-6 flex flex-wrap items-center justify-between gap-3"><div><p className="text-[10px] font-bold uppercase tracking-widest text-blue-600">Generated artifact</p><h2 className="mt-1 text-lg font-bold text-slate-900">{artifact?.title || meta.title}</h2></div>{snapshot && <span className="rounded-full border border-slate-200 bg-slate-50 px-3 py-1.5 text-xs font-medium text-slate-500">Version {snapshot.version} · OpenSourceLLM</span>}</div>
      {(artifact || selectedProject) && <div className="mb-6"><ProjectIdentityBanner identity={artifact?.project_identity} project={selectedProject} /></div>}
      {loading ? <div className="flex min-h-52 items-center justify-center"><LoaderCircle className="h-7 w-7 animate-spin text-blue-600" /></div> : !artifact ? <div className="rounded-2xl border border-dashed border-slate-300 bg-slate-50/70 py-20 text-center"><div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-white shadow-sm"><Icon className="h-7 w-7 text-slate-400" /></div><p className="mt-4 text-sm font-semibold text-slate-700">No {meta.short} generated yet</p><p className="mt-1 text-xs text-slate-500">Select a project above and start generation.</p></div> : documentType === 'knowledge_graph' ? <KnowledgeGraph graph={artifact} /> : <ArtifactReview artifact={artifact} documentType={documentType} />}
    </section>
  </PageFrame>
}

function PageFrame({ title, description, children, step = 1 }) {
  const steps = ['Upload assets', 'AI discovery', 'Document review', 'Target architecture', 'Forward engineering', 'Generated assets']
  return <Layout><main className="min-h-full bg-[linear-gradient(180deg,#f8fafc_0%,#f5f7fa_100%)]"><div className="mx-auto w-full max-w-[1480px] px-5 py-8 lg:px-10 lg:py-10">
    <div className="mb-7 overflow-x-auto rounded-2xl border border-slate-200 bg-white px-4 py-3 shadow-sm"><div className="flex min-w-[620px] items-center">{steps.map((label, index) => { const number = index + 1; const complete = number < step; const active = number === step; return <div key={label} className="flex flex-1 items-center last:flex-none"><div className="flex items-center gap-2.5"><span className={`flex h-7 w-7 items-center justify-center rounded-lg text-xs font-bold ${complete ? 'bg-emerald-500 text-white' : active ? 'bg-blue-600 text-white shadow-md shadow-blue-600/20' : 'bg-slate-100 text-slate-400'}`}>{complete ? <Check className="h-4 w-4" /> : number}</span><span className={`text-xs font-semibold ${active ? 'text-blue-700' : complete ? 'text-slate-700' : 'text-slate-400'}`}>{label}</span></div>{index < steps.length - 1 && <div className={`mx-4 h-px flex-1 ${complete ? 'bg-emerald-300' : 'bg-slate-200'}`} />}</div> })}</div></div>
    <div className="mb-8"><span className="inline-flex items-center gap-2 rounded-full border border-blue-100 bg-blue-50 px-3 py-1 text-[10px] font-bold uppercase tracking-[0.16em] text-blue-700"><Sparkles className="h-3 w-3" />Requirements intelligence</span><h1 className="mt-4 text-3xl font-bold tracking-tight text-slate-950 lg:text-[34px]">{title}</h1><p className="mt-2 max-w-3xl text-sm leading-6 text-slate-500">{description}</p></div>{children}
  </div></main></Layout>
}

export default function RequirementsDocumentationPage() {
  const { pathname } = useLocation()
  if (pathname.endsWith('/upload')) return <UploadProjects />
  if (pathname.endsWith('/architecture-review')) return <TargetArchitectureReview />
  if (pathname.endsWith('/generated-assets')) return <GeneratedAssetsRepository />
  if (pathname.endsWith('/knowledge-graph')) return <DocumentWorkspace documentType="knowledge_graph" />
  return <DocumentWorkspace documentType={pathname.endsWith('/fsd') ? 'fsd' : 'brd'} />
}
