// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: Novastra-ITSM — frontend/src/pages (SettingsPage.jsx)
// Date: 2026-05-19
// ---------------------------------------------------------------------------
import { useState, useEffect } from 'react'
import toast from 'react-hot-toast'
import { Save, Loader2, Bot, Key } from 'lucide-react'
import { getSettings, updateSettings } from '../services/api.js'

// Function: SettingsPage
export default function SettingsPage() {
  const [settings, setSettings] = useState(null)
  const [form, setForm] = useState({})
  const [saving, setSaving] = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getSettings()
      .then(({ data }) => { setSettings(data); setForm(data) })
      .catch((err) => toast.error(err.message))
      .finally(() => setLoading(false))
  }, [])

  // Function: save
  const save = async () => {
    setSaving(true)
    try {
      const payload = {
        llm_provider: form.llm_provider,
        ollama_model: form.ollama_model,
        ollama_base_url: form.ollama_base_url,
        openai_model: form.openai_model,
        openai_api_key: form.openai_api_key || undefined,
      }
      const { data } = await updateSettings(payload)
      setSettings(data)
      setForm(data)
      toast.success('Settings saved and applied.')
    } catch (err) {
      toast.error(err.response?.data?.detail || err.message)
    } finally { setSaving(false) }
  }

  if (loading) return <div className="flex items-center justify-center h-full text-gray-400 text-sm">Loading…</div>

  return (
    <div className="flex flex-col h-full overflow-y-auto">
      <header className="flex-shrink-0 px-6 py-4 border-b bg-white">
        <h1 className="font-semibold text-gray-900">LLM Settings</h1>
        <p className="text-xs text-gray-500">Choose between Ollama (open-source) and OpenAI</p>
      </header>

      <div className="flex-1 px-6 py-6 space-y-6 max-w-xl">
        {/* Provider selector */}
        <div className="card space-y-4">
          <h2 className="font-medium text-sm text-gray-700 flex items-center gap-2"><Bot size={16} /> LLM Provider</h2>
          <div className="flex gap-3">
            {['ollama', 'openai'].map((p) => (
              <button
                key={p}
                onClick={() => setForm(f => ({ ...f, llm_provider: p }))}
                className={`flex-1 py-3 rounded-xl border-2 text-sm font-semibold transition-all ${
                  form.llm_provider === p
                    ? 'border-brand-600 bg-brand-50 text-brand-700'
                    : 'border-gray-200 text-gray-500 hover:border-gray-300'
                }`}
              >
                {p === 'ollama' ? '🦙 Ollama (Open-Source)' : '✨ OpenAI'}
              </button>
            ))}
          </div>
        </div>

        {/* Ollama settings */}
        <div className={`card space-y-4 ${form.llm_provider !== 'ollama' ? 'opacity-50 pointer-events-none' : ''}`}>
          <h2 className="font-medium text-sm text-gray-700">Ollama Configuration</h2>
          <div>
            <label htmlFor="settings-ollama-base-url" className="label">Ollama Base URL</label>
            <input id="settings-ollama-base-url" className="input" value={form.ollama_base_url || ''} onChange={e => setForm(f => ({ ...f, ollama_base_url: e.target.value }))} placeholder="http://localhost:11434" />
          </div>
          <div>
            <label htmlFor="settings-ollama-model" className="label">Model Name</label>
            <input id="settings-ollama-model" className="input" value={form.ollama_model || ''} onChange={e => setForm(f => ({ ...f, ollama_model: e.target.value }))} placeholder="mistral" />
            <p className="text-xs text-gray-400 mt-1">Run <code>ollama pull mistral</code> to download a model locally.</p>
          </div>
        </div>

        {/* OpenAI settings */}
        <div className={`card space-y-4 ${form.llm_provider !== 'openai' ? 'opacity-50 pointer-events-none' : ''}`}>
          <h2 className="font-medium text-sm text-gray-700 flex items-center gap-2"><Key size={16} /> OpenAI Configuration</h2>
          <div>
            <label htmlFor="settings-openai-api-key" className="label">API Key</label>
            <input
              id="settings-openai-api-key"
              type="password"
              className="input"
              value={form.openai_api_key || ''}
              onChange={e => setForm(f => ({ ...f, openai_api_key: e.target.value }))}
              placeholder="sk-…"
            />
            {settings?.openai_configured && (
              <p className="text-xs text-green-600 mt-1">✓ OpenAI key is currently configured on the server.</p>
            )}
          </div>
          <div>
            <label htmlFor="settings-openai-model" className="label">Model</label>
            <input id="settings-openai-model" className="input" value={form.openai_model || ''} onChange={e => setForm(f => ({ ...f, openai_model: e.target.value }))} placeholder="gpt-4o-mini" />
          </div>
        </div>

        <button onClick={save} disabled={saving} className="btn-primary w-full justify-center">
          {saving ? <Loader2 size={16} className="animate-spin" /> : <Save size={16} />}
          Save Settings
        </button>
      </div>
    </div>
  )
}
