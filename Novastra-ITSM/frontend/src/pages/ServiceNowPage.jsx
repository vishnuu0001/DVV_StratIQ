// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: Novastra-ITSM — frontend/src/pages (ServiceNowPage.jsx)
// Date: 2026-07-10
// ---------------------------------------------------------------------------
import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import toast from 'react-hot-toast'
import { Ticket, ClipboardList, Loader2 } from 'lucide-react'
import { clsx } from 'clsx'
import { snFetchResolve, snManualResolve } from '../services/api.js'
import SourceBadges from '../components/SourceBadges.jsx'
import ConfidenceBadge from '../components/ConfidenceBadge.jsx'
import { useSettings } from '../hooks/useSettings.js'

const TABS = [
  { id: 'live',   label: 'Live SN Ticket', icon: Ticket },
  { id: 'manual', label: 'Manual Input',   icon: ClipboardList },
]

// Function: ServiceNowPage
export default function ServiceNowPage() {
  const [tab, setTab] = useState('live')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const { settings } = useSettings()

  // Live SN
  const [ticketNum, setTicketNum] = useState('')
  const [extraCtx, setExtraCtx] = useState('')

  // Manual
  const [manual, setManual] = useState({
    incident_number: '', short_description: '', description: '',
    priority: '', category: '', additional_context: '',
  })

  const provider = settings?.llm_provider || 'ollama'

  // Function: handleLive
  const handleLive = async () => {
    if (!ticketNum.trim()) return toast.error('Enter a ticket number.')
    setLoading(true); setResult(null)
    try {
      const { data } = await snFetchResolve({ ticket_number: ticketNum, additional_context: extraCtx, llm_provider: provider })
      setResult(data)
    } catch (err) {
      toast.error(err.response?.data?.detail || err.message)
    } finally { setLoading(false) }
  }

  // Function: handleManual
  const handleManual = async () => {
    if (!manual.incident_number || !manual.short_description || !manual.description)
      return toast.error('Fill in Incident #, Short Description, and Description.')
    setLoading(true); setResult(null)
    try {
      const { data } = await snManualResolve({ ...manual, llm_provider: provider })
      setResult(data)
    } catch (err) {
      toast.error(err.response?.data?.detail || err.message)
    } finally { setLoading(false) }
  }

  return (
    <div className="flex flex-col h-full overflow-y-auto">
      <header className="flex-shrink-0 px-6 py-4 border-b bg-white">
        <h1 className="font-semibold text-gray-900">ServiceNow Resolution</h1>
        <p className="text-xs text-gray-500">Get AI-recommended resolutions · use Support Chat to attach screenshots</p>
      </header>

      <div className="flex-1 px-6 py-4 space-y-6 max-w-3xl w-full mx-auto">
        {/* Tab bar */}
        <div className="flex gap-1 bg-gray-100 p-1 rounded-lg">
          {TABS.map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              onClick={() => { setTab(id); setResult(null) }}
              className={clsx(
                'flex-1 flex items-center justify-center gap-2 py-2 rounded-md text-sm font-medium transition-colors',
                tab === id ? 'bg-white text-brand-700 shadow-sm' : 'text-gray-500 hover:text-gray-700'
              )}
            >
              <Icon size={14} />{label}
            </button>
          ))}
        </div>

        {/* Live SN */}
        {tab === 'live' && (
          <div className="card space-y-4">
            <h2 className="font-medium text-gray-800 text-sm">Fetch from ServiceNow</h2>
            <div>
              <label className="label">Ticket Number</label>
              <input className="input" placeholder="e.g. INC4692481" value={ticketNum} onChange={e => setTicketNum(e.target.value)} />
            </div>
            <div>
              <label className="label">Additional Context (optional)</label>
              <textarea className="input resize-none" rows={2} placeholder="Any extra details…" value={extraCtx} onChange={e => setExtraCtx(e.target.value)} />
            </div>
            <button onClick={handleLive} disabled={loading} className="btn-primary">
              {loading ? <Loader2 size={16} className="animate-spin" /> : <Ticket size={16} />}
              Get Resolution
            </button>
          </div>
        )}

        {/* Manual */}
        {tab === 'manual' && (
          <div className="card space-y-4">
            <h2 className="font-medium text-gray-800 text-sm">Manual Ticket Details</h2>
            {[
              ['incident_number', 'Incident Number', 'INC0000000'],
              ['short_description', 'Short Description', 'Brief summary of the issue'],
              ['priority', 'Priority', '1 - Critical'],
              ['category', 'Category', 'Software'],
            ].map(([key, lbl, ph]) => (
              <div key={key}>
                <label className="label">{lbl}</label>
                <input className="input" placeholder={ph} value={manual[key]} onChange={e => setManual(m => ({ ...m, [key]: e.target.value }))} />
              </div>
            ))}
            <div>
              <label className="label">Full Description <span className="text-red-500">*</span></label>
              <textarea className="input resize-none" rows={4} placeholder="Detailed description of the incident…" value={manual.description} onChange={e => setManual(m => ({ ...m, description: e.target.value }))} />
            </div>
            <div>
              <label className="label">Additional Context</label>
              <textarea className="input resize-none" rows={2} value={manual.additional_context} onChange={e => setManual(m => ({ ...m, additional_context: e.target.value }))} />
            </div>
            <button onClick={handleManual} disabled={loading} className="btn-primary">
              {loading ? <Loader2 size={16} className="animate-spin" /> : <ClipboardList size={16} />}
              Get Resolution
            </button>
          </div>
        )}

        {/* Screenshot */}
        {tab === 'screenshot' && null}

        {/* Result */}
        {result && (
          <div className="card border-l-4 border-brand-500 space-y-3">
            <h2 className="font-semibold text-gray-800 text-sm">Recommended Resolution</h2>
            <div className="answer-prose">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>{result.answer}</ReactMarkdown>
            </div>
            <div className="flex flex-wrap gap-2 pt-2 border-t border-gray-100">
              <ConfidenceBadge value={result.confidence} contextUsed={result.context_used} />
              {result.sources?.length > 0 && <SourceBadges sources={result.sources} />}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
