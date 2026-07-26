// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: InfraRationalization — frontend/src/pages (PdfAnalysisPage.jsx)
// Date: 2026-02-20
// ---------------------------------------------------------------------------
import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  ArrowLeft, FileText, ScanLine, CheckCircle, AlertCircle,
  Cloud, Server, Database, Shield, Activity, ChevronDown, ChevronRight,
  Layers, Globe, Lock, Cpu, HardDrive
} from 'lucide-react'
import toast from 'react-hot-toast'
import { listDataPdfs, getPdfStreamUrl, getPortalToken } from '../api/client.js'
import AppHeader from '../components/AppHeader.jsx'

const PROVIDER_LABELS = {
  azure: { label: 'Azure', color: 'text-blue-400', bg: 'bg-blue-900/30', border: 'border-blue-700' },
  aws:   { label: 'AWS',   color: 'text-yellow-400', bg: 'bg-yellow-900/30', border: 'border-yellow-700' },
  gcp:   { label: 'GCP',   color: 'text-green-400',  bg: 'bg-green-900/30',  border: 'border-green-700' },
  onprem:{ label: 'On-Premises', color: 'text-purple-400', bg: 'bg-purple-900/30', border: 'border-purple-700' },
}

// Function: ProviderBadge
const ProviderBadge = ({ provider }) => {
  const cfg = PROVIDER_LABELS[provider?.toLowerCase()] || { label: provider, color: 'text-slate-400', bg: 'bg-slate-800', border: 'border-slate-600' }
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${cfg.bg} ${cfg.color} border ${cfg.border}`}>
      {cfg.label}
    </span>
  )
}

// Function: ProgressEvent
const ProgressEvent = ({ event }) => {
  const icon = {
    start:        <ScanLine className="w-4 h-4 text-emerald-400" />,
    progress:     <Activity className="w-4 h-4 text-blue-400 animate-pulse" />,
    file_done:    <CheckCircle className="w-4 h-4 text-emerald-400" />,
    file_warning: <AlertCircle className="w-4 h-4 text-yellow-400" />,
    complete:     <CheckCircle className="w-4 h-4 text-emerald-400" />,
    error:        <AlertCircle className="w-4 h-4 text-red-400" />,
  }[event.type] || <Activity className="w-4 h-4 text-slate-400" />

  return (
    <div className="flex items-start gap-2 py-1 border-b border-slate-800 last:border-0">
      <span className="mt-0.5 shrink-0">{icon}</span>
      <span className={`text-xs ${event.type === 'error' ? 'text-red-300' : event.type === 'file_warning' ? 'text-yellow-300' : 'text-slate-300'}`}>
        {event.message}
      </span>
      {(event.current != null && event.total != null) && (
        <span className="ml-auto text-xs text-slate-500 shrink-0">
          {event.current}/{event.total}
        </span>
      )}
    </div>
  )
}

// Function: ServicePill
const ServicePill = ({ name }) => (
  <span className="inline-block px-2 py-0.5 bg-slate-700 text-slate-300 rounded text-xs mr-1 mb-1">{name}</span>
)

// Function: CollapsibleSection
const CollapsibleSection = ({ title, icon: Icon, count, children, defaultOpen = false }) => {
  const [open, setOpen] = useState(defaultOpen)
  return (
    <div className="border border-slate-700 rounded-lg overflow-hidden">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center gap-2 px-4 py-3 bg-slate-800 hover:bg-slate-750 text-left"
      >
        {Icon && <Icon className="w-4 h-4 text-emerald-400" />}
        <span className="text-sm font-medium text-white flex-1">{title}</span>
        {count != null && (
          <span className="text-xs bg-slate-700 text-slate-300 px-2 py-0.5 rounded">{count}</span>
        )}
        {open ? <ChevronDown className="w-4 h-4 text-slate-400" /> : <ChevronRight className="w-4 h-4 text-slate-400" />}
      </button>
      {open && <div className="p-4 bg-slate-900">{children}</div>}
    </div>
  )
}

// Function: ServerCard
const ServerCard = ({ server, idx }) => (
  <div className="bg-slate-800 border border-slate-700 rounded-lg p-4 space-y-2">
    <div className="flex items-center justify-between">
      <div className="flex items-center gap-2">
        <Server className="w-4 h-4 text-emerald-400" />
        <span className="text-sm font-semibold text-white">{server.server_name || `Server ${idx + 1}`}</span>
      </div>
      <ProviderBadge provider={server.cloud_provider} />
    </div>

    <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-xs text-slate-400">
      {server.ip_address && <div><span className="text-slate-500">IP:</span> {server.ip_address}</div>}
      {server.region    && <div><span className="text-slate-500">Region:</span> {server.region}</div>}
      {server.cpu_cores > 0 && <div><span className="text-slate-500">CPU:</span> {server.cpu_cores} cores</div>}
      {server.ram_gb    > 0 && <div><span className="text-slate-500">RAM:</span> {server.ram_gb} GB</div>}
      {server.os_name   && <div className="col-span-2"><span className="text-slate-500">OS:</span> {server.os_name}</div>}
      {server.instance_type && <div className="col-span-2"><span className="text-slate-500">Instance:</span> {server.instance_type}</div>}
      {server.environment && <div><span className="text-slate-500">Env:</span> {server.environment}</div>}
      {server.migration_strategy && (
        <div className="col-span-2">
          <span className="text-slate-500">Migration:</span>{' '}
          <span className="text-emerald-400">{server.migration_strategy.replace(/_/g, ' ')}</span>
        </div>
      )}
    </div>

    {server.workloads?.length > 0 && (
      <div className="flex flex-wrap gap-1 pt-1">
        {server.workloads.map((wl, wi) => (
          <span key={wi} className="text-xs bg-slate-700 text-slate-300 px-2 py-0.5 rounded">
            {wl.name}
          </span>
        ))}
      </div>
    )}
  </div>
)

// Function: ProviderFeaturesPanel
const ProviderFeaturesPanel = ({ provider, features }) => {
  const specs = features.raw_specs || {}
  const services = features.found_services || []
  const security = features.security_compliance || []
  const hadr = features.ha_dr_mentions || []
  const cfg = PROVIDER_LABELS[provider] || { label: provider, color: 'text-slate-400', bg: '', border: 'border-slate-700' }

  return (
    <div className={`border ${cfg.border} rounded-lg p-4 space-y-4`}>
      <h4 className={`text-sm font-semibold ${cfg.color} uppercase tracking-wide`}>{cfg.label} Features</h4>

      {services.length > 0 && (
        <div>
          <p className="text-xs text-slate-500 mb-2">Services & Components ({services.length})</p>
          <div className="flex flex-wrap">
            {services.map((s, i) => <ServicePill key={i} name={s} />)}
          </div>
        </div>
      )}

      {(specs.subnets?.length > 0 || specs.cidr_blocks?.length > 0) && (
        <div>
          <p className="text-xs text-slate-500 mb-1">Network / Subnets</p>
          <div className="flex flex-wrap">
            {[...(specs.subnets || []), ...(specs.cidr_blocks || [])].filter((v, i, a) => a.indexOf(v) === i).map((s, i) => (
              <ServicePill key={i} name={s} />
            ))}
          </div>
        </div>
      )}

      {specs.regions?.length > 0 && (
        <div>
          <p className="text-xs text-slate-500 mb-1">Regions</p>
          <div className="flex flex-wrap">
            {specs.regions.map((r, i) => <ServicePill key={i} name={r} />)}
          </div>
        </div>
      )}

      {specs.storage_tiers?.length > 0 && (
        <div>
          <p className="text-xs text-slate-500 mb-1">Storage Tiers</p>
          <div className="flex flex-wrap">
            {specs.storage_tiers.map((s, i) => <ServicePill key={i} name={s} />)}
          </div>
        </div>
      )}

      {security.length > 0 && (
        <div>
          <p className="text-xs text-slate-500 mb-1">Security & Compliance</p>
          <div className="flex flex-wrap">
            {security.map((s, i) => (
              <span key={i} className="inline-block px-2 py-0.5 bg-red-900/30 text-red-300 border border-red-800 rounded text-xs mr-1 mb-1">{s}</span>
            ))}
          </div>
        </div>
      )}

      {hadr.length > 0 && (
        <div>
          <p className="text-xs text-slate-500 mb-1">HA / DR</p>
          <div className="flex flex-wrap">
            {[...new Set(hadr)].map((s, i) => (
              <span key={i} className="inline-block px-2 py-0.5 bg-emerald-900/30 text-emerald-300 border border-emerald-800 rounded text-xs mr-1 mb-1">{s}</span>
            ))}
          </div>
        </div>
      )}

      {specs.azure_vm_skus?.length > 0 && (
        <div>
          <p className="text-xs text-slate-500 mb-1">Azure VM SKUs</p>
          <div className="flex flex-wrap">
            {specs.azure_vm_skus.map((s, i) => <ServicePill key={i} name={s} />)}
          </div>
        </div>
      )}
      {specs.aws_instance_types?.length > 0 && (
        <div>
          <p className="text-xs text-slate-500 mb-1">AWS Instance Types</p>
          <div className="flex flex-wrap">
            {specs.aws_instance_types.map((s, i) => <ServicePill key={i} name={s} />)}
          </div>
        </div>
      )}
      {specs.gcp_machine_types?.length > 0 && (
        <div>
          <p className="text-xs text-slate-500 mb-1">GCP Machine Types</p>
          <div className="flex flex-wrap">
            {specs.gcp_machine_types.map((s, i) => <ServicePill key={i} name={s} />)}
          </div>
        </div>
      )}

      <div className="grid grid-cols-3 gap-3 text-xs">
        {specs.cpu_values?.length > 0 && (
          <div className="bg-slate-800 rounded p-2 text-center">
            <div className="text-slate-400 mb-0.5">CPU (cores)</div>
            <div className="text-white font-semibold">{Math.max(...specs.cpu_values)}</div>
          </div>
        )}
        {specs.ram_gb_values?.length > 0 && (
          <div className="bg-slate-800 rounded p-2 text-center">
            <div className="text-slate-400 mb-0.5">Max RAM (GB)</div>
            <div className="text-white font-semibold">{Math.max(...specs.ram_gb_values)}</div>
          </div>
        )}
        {specs.server_count_mentions?.length > 0 && (
          <div className="bg-slate-800 rounded p-2 text-center">
            <div className="text-slate-400 mb-0.5">Server Count</div>
            <div className="text-white font-semibold">{Math.max(...specs.server_count_mentions)}</div>
          </div>
        )}
      </div>
    </div>
  )
}

// Function: PdfAnalysisPage
export default function PdfAnalysisPage() {
  const navigate = useNavigate()
  const [pdfs, setPdfs] = useState([])
  const [loadingPdfs, setLoadingPdfs] = useState(true)
  const [scanning, setScanning] = useState(false)
  const [events, setEvents] = useState([])
  const [report, setReport] = useState(null)
  const [progress, setProgress] = useState(0)
  const [progressTotal, setProgressTotal] = useState(0)
  const logRef = useRef(null)

  useEffect(() => {
    listDataPdfs()
      .then(data => setPdfs(data.pdfs || []))
      .catch(() => toast.error('Could not list PDF files'))
      .finally(() => setLoadingPdfs(false))
  }, [])

  useEffect(() => {
    if (logRef.current) {
      logRef.current.scrollTop = logRef.current.scrollHeight
    }
  }, [events])

  // Function: handleStartScan
  const handleStartScan = () => {
    if (scanning) return
    setScanning(true)
    setEvents([])
    setReport(null)
    setProgress(0)

    const token = getPortalToken()
    const url = `${getPdfStreamUrl()}${token ? `?token=${encodeURIComponent(token)}` : ''}`
    const es = new EventSource(url)

    es.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data)
        setEvents(prev => [...prev, data])

        if (data.type === 'start' && data.total) {
          setProgressTotal(data.total)
        }
        if (data.current != null && data.total != null) {
          setProgress(Math.round((data.current / data.total) * 100))
        }
        if (data.type === 'complete') {
          setReport(data.report)
          setProgress(100)
          setScanning(false)
          es.close()
          toast.success('PDF OCR analysis complete!')
        }
        if (data.type === 'error') {
          setScanning(false)
          es.close()
          toast.error(data.message || 'Scan failed')
        }
      } catch (_) {}
    }

    es.onerror = () => {
      setScanning(false)
      es.close()
      toast.error('Connection lost during scan')
    }
  }

  const providerColors = {
    azure: 'text-blue-400',
    aws: 'text-yellow-400',
    gcp: 'text-green-400',
    onprem: 'text-purple-400',
  }

  return (
    <div className="min-h-screen bg-surface text-white flex flex-col">
      <AppHeader />
      <div className="flex-1 max-w-6xl mx-auto w-full p-6 space-y-6">

        {/* Header */}
        <div className="flex items-center gap-4">
          <button
            onClick={() => navigate('/')}
            className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 transition-colors"
          >
            <ArrowLeft className="w-4 h-4 text-slate-300" />
          </button>
          <div>
            <h1 className="text-xl font-bold text-white">PDF Infrastructure Analysis</h1>
            <p className="text-sm text-slate-400 mt-0.5">
              Deep OCR evaluation of infrastructure documents — detects cloud provider and extracts all features
            </p>
          </div>
        </div>

        {/* PDF file list */}
        <div className="glass rounded-xl p-5">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <FileText className="w-5 h-5 text-emerald-400" />
              <h2 className="text-sm font-semibold text-white">Documents in data/ directory</h2>
            </div>
            {!loadingPdfs && (
              <span className="text-xs text-slate-400">{pdfs.length} PDF(s) found</span>
            )}
          </div>

          {loadingPdfs ? (
            <div className="text-sm text-slate-400 animate-pulse">Loading…</div>
          ) : pdfs.length === 0 ? (
            <div className="text-sm text-slate-400">No PDF files found in the data/ directory.</div>
          ) : (
            <div className="space-y-2">
              {pdfs.map((pdf, i) => (
                <div key={i} className="flex items-center justify-between bg-slate-800 rounded-lg px-4 py-2">
                  <div className="flex items-center gap-3">
                    <FileText className="w-4 h-4 text-slate-400" />
                    <span className="text-sm text-white">{pdf.filename}</span>
                  </div>
                  <div className="flex items-center gap-4 text-xs text-slate-400">
                    <span>{pdf.size_kb} KB</span>
                    <span>{pdf.modified?.slice(0, 10)}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Start scan button */}
        <div className="flex items-center gap-4">
          <button
            onClick={handleStartScan}
            disabled={scanning || pdfs.length === 0}
            className="flex items-center gap-2 px-6 py-3 bg-emerald-600 hover:bg-emerald-500 disabled:bg-slate-700 disabled:cursor-not-allowed text-white text-sm font-semibold rounded-xl transition-colors"
          >
            <ScanLine className="w-4 h-4" />
            {scanning ? 'Scanning…' : 'Run PDF OCR Analysis'}
          </button>
          {scanning && (
            <div className="flex items-center gap-3 flex-1">
              <div className="flex-1 bg-slate-800 rounded-full h-2 overflow-hidden">
                <div
                  className="h-full bg-emerald-500 transition-all duration-300"
                  style={{ width: `${progress}%` }}
                />
              </div>
              <span className="text-xs text-slate-400 w-10">{progress}%</span>
            </div>
          )}
        </div>

        {/* Progress log */}
        {events.length > 0 && (
          <div className="glass rounded-xl p-4">
            <div className="flex items-center gap-2 mb-3">
              <Activity className="w-4 h-4 text-emerald-400" />
              <h3 className="text-sm font-semibold text-white">Scan Progress</h3>
            </div>
            <div
              ref={logRef}
              className="max-h-52 overflow-y-auto space-y-0.5 font-mono"
            >
              {events.map((ev, i) => (
                <ProgressEvent key={i} event={ev} />
              ))}
            </div>
          </div>
        )}

        {/* Results */}
        {report && (
          <div className="space-y-5">
            {/* Summary cards */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="glass rounded-xl p-4 text-center">
                <div className="text-2xl font-bold text-emerald-400">{report.documents_scanned}</div>
                <div className="text-xs text-slate-400 mt-1">Documents Scanned</div>
              </div>
              <div className="glass rounded-xl p-4 text-center">
                <div className="text-2xl font-bold text-blue-400">{report.detected_providers?.length || 0}</div>
                <div className="text-xs text-slate-400 mt-1">Providers Detected</div>
              </div>
              <div className="glass rounded-xl p-4 text-center">
                <div className="text-2xl font-bold text-purple-400">{report.total_servers_extracted}</div>
                <div className="text-xs text-slate-400 mt-1">Servers Extracted</div>
              </div>
              <div className="glass rounded-xl p-4 text-center">
                <div className="text-2xl font-bold text-yellow-400">{report.summary?.total_services_identified || 0}</div>
                <div className="text-xs text-slate-400 mt-1">Services Identified</div>
              </div>
            </div>

            {/* Detected providers */}
            {report.detected_providers?.length > 0 && (
              <div className="glass rounded-xl p-4">
                <h3 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
                  <Globe className="w-4 h-4 text-emerald-400" />
                  Detected Providers
                </h3>
                <div className="flex flex-wrap gap-2">
                  {report.detected_providers.map((p, i) => (
                    <ProviderBadge key={i} provider={p} />
                  ))}
                </div>
              </div>
            )}

            {/* Per-document breakdown */}
            {report.pdf_documents?.length > 0 && (
              <CollapsibleSection
                title="Document Analysis Details"
                icon={FileText}
                count={report.pdf_documents.length}
                defaultOpen
              >
                <div className="space-y-6">
                  {report.pdf_documents.map((doc, di) => (
                    <div key={di} className="space-y-3">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <FileText className="w-4 h-4 text-slate-400" />
                          <span className="text-sm font-semibold text-white">{doc.pdf_name}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="text-xs text-slate-500">{doc.page_count} pages · {(doc.total_chars / 1000).toFixed(1)}K chars · {doc.extraction_method}</span>
                          {doc.error && <AlertCircle className="w-4 h-4 text-yellow-400" title={doc.error} />}
                        </div>
                      </div>

                      <div className="flex flex-wrap gap-1 mb-2">
                        {doc.detected_providers?.map((p, pi) => <ProviderBadge key={pi} provider={p} />)}
                      </div>

                      {doc.features_by_provider && Object.entries(doc.features_by_provider).map(([prov, feats]) => (
                        <ProviderFeaturesPanel key={prov} provider={prov} features={feats} />
                      ))}

                      {doc.error && (
                        <div className="text-xs text-yellow-300 bg-yellow-900/20 border border-yellow-800 rounded p-2">
                          Warning: {doc.error}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </CollapsibleSection>
            )}

            {/* Extracted servers */}
            {report.servers?.length > 0 && (
              <CollapsibleSection
                title="Extracted Server Records"
                icon={Server}
                count={report.servers.length}
                defaultOpen
              >
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {report.servers.map((srv, si) => (
                    <ServerCard key={si} server={srv} idx={si} />
                  ))}
                </div>
              </CollapsibleSection>
            )}

            {/* Top services */}
            {report.top_services_mentioned?.length > 0 && (
              <CollapsibleSection
                title="Top Services & Features Mentioned"
                icon={Layers}
                count={report.top_services_mentioned.length}
              >
                <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                  {report.top_services_mentioned.slice(0, 30).map((item, i) => (
                    <div key={i} className="flex items-center justify-between bg-slate-800 rounded px-3 py-1.5">
                      <span className="text-xs text-slate-300 truncate">{item.service}</span>
                      <span className="text-xs text-emerald-400 font-semibold ml-2 shrink-0">×{item.mention_count}</span>
                    </div>
                  ))}
                </div>
              </CollapsibleSection>
            )}

            {/* View in scan detail */}
            {report.scan_id && (
              <div className="flex justify-end">
                <button
                  onClick={() => navigate(`/scans/${report.scan_id}`)}
                  className="flex items-center gap-2 px-5 py-2.5 bg-slate-700 hover:bg-slate-600 text-white text-sm font-medium rounded-xl transition-colors"
                >
                  <Database className="w-4 h-4" />
                  View Full Report
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
