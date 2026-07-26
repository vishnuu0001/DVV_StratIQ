// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: SSDLC_Process_Assessment — csm_frontend/src/api (client.ts)
// Date: 2025-09-18
// ---------------------------------------------------------------------------
import type { WorkbookUploadResponse } from '../types'

const API_BASE = '/api/csm'

export async function apiGet<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`)
  if (!res.ok) throw new Error(`API error ${res.status}: ${await res.text()}`)
  return res.json()
}

export async function apiPost<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) throw new Error(`API error ${res.status}: ${await res.text()}`)
  return res.json()
}

// Function: uploadWorkbook
export async function uploadWorkbook(file: File): Promise<WorkbookUploadResponse> {
  const form = new FormData()
  form.append('file', file)
  const res = await fetch(`${API_BASE}/workbooks/upload`, { method: 'POST', body: form })
  if (!res.ok) throw new Error(`Upload error ${res.status}: ${await res.text()}`)
  return res.json()
}
