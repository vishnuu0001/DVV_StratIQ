// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: OpportunityTracker — frontend/src/services (api.js)
// Date: 2025-08-22
// ---------------------------------------------------------------------------
import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_OT_API_URL ||
    (import.meta.env.DEV ? '/api/ot/' : '/api/ot'),
});

api.interceptors.response.use(
  (r) => r,
  (err) => {
    const isLoginCall = err.config?.url?.includes('auth/login');
    if (err.response?.status === 401 && !isLoginCall) {
      sessionStorage.removeItem('ot_auth');
      window.location.href = `${import.meta.env.BASE_URL}login`;
    }
    return Promise.reject(err);
  }
);

export default api;

// ── Wave Planning ────────────────────────────────────────────────────────

// Function: listWaveDatasets
export const listWaveDatasets = () => api.get('wave/datasets');
// Function: deleteWaveDataset
export const deleteWaveDataset = (datasetId) => api.delete(`wave/datasets/${datasetId}`);

// Function: uploadScopeDataset
export const uploadScopeDataset = (file) => {
  const form = new FormData();
  form.append('file', file);
  return api.post('wave/datasets/scope', form, { headers: { 'Content-Type': 'multipart/form-data' } });
};

// Function: uploadCategorizationDataset
export const uploadCategorizationDataset = (file) => {
  const form = new FormData();
  form.append('file', file);
  return api.post('wave/datasets/categorization', form, { headers: { 'Content-Type': 'multipart/form-data' } });
};

// Function: previewWaveCategories
export const previewWaveCategories = (scopeDatasetId, categorizationDatasetId) =>
  api.get('wave/analysis/preview-categories', {
    params: { scope_dataset_id: scopeDatasetId, categorization_dataset_id: categorizationDatasetId },
  });

// Function: submitWaveAnalysis
export const submitWaveAnalysis = (scopeDatasetId, categorizationDatasetId, categories, userGuidance) =>
  api.post('wave/analysis', {
    scope_dataset_id: scopeDatasetId,
    categorization_dataset_id: categorizationDatasetId,
    categories: categories?.length ? categories : null,
    user_guidance: userGuidance?.trim() ? userGuidance.trim() : null,
  });

// Function: getWaveJobStatus
export const getWaveJobStatus = (jobId) => api.get(`wave/analysis/${jobId}`);

// Function: POLL_DELAY_MS
const POLL_DELAY_MS = (attempt) => {
  if (attempt < 4) return 800;
  if (attempt < 16) return 1500;
  if (attempt < 60) return 3000;
  return 6000;
};
const MAX_POLLS = 600; // ~ up to ~35 min ceiling given the backoff schedule above

/**
 * Poll a wave-analysis job until done/failed, invoking onProgress on every tick
 * so the UI can show completed/total categories rather than a static spinner.
 */
// Function: pollWaveJob
export async function pollWaveJob(jobId, onProgress) {
  for (let attempt = 0; attempt < MAX_POLLS; attempt += 1) {
    const { data } = await getWaveJobStatus(jobId);
    onProgress?.(data);
    if (data.status === 'done' || data.status === 'failed') {
      return data;
    }
    await new Promise((resolve) => setTimeout(resolve, POLL_DELAY_MS(attempt)));
  }
  throw new Error('Wave analysis job polling timed out.');
}

// Function: listWaveCategories
export const listWaveCategories = (jobId) => api.get(`wave/analysis/${jobId}/categories`);
// Function: getWaveCategory
export const getWaveCategory = (jobId, category) => api.get(`wave/analysis/${jobId}/categories/${encodeURIComponent(category)}`);
// Function: listWaves
export const listWaves = (jobId, category) => api.get(`wave/analysis/${jobId}/categories/${encodeURIComponent(category)}/waves`);
// Function: listWaveApps
export const listWaveApps = (jobId, category, wave) =>
  api.get(`wave/analysis/${jobId}/categories/${encodeURIComponent(category)}/waves/${encodeURIComponent(wave)}/apps`);
// Function: getWaveRemediation
export const getWaveRemediation = (jobId, category) =>
  api.get(`wave/analysis/${jobId}/categories/${encodeURIComponent(category)}/remediation`);
// Function: getWaveGantt
export const getWaveGantt = (jobId, category) =>
  api.get(`wave/analysis/${jobId}/categories/${encodeURIComponent(category)}/gantt`);

// ── Opportunity import + Financial Dashboard ────────────────────────────────

// Function: importOpportunities
export const importOpportunities = (file) => {
  const form = new FormData();
  form.append('file', file);
  return api.post('opportunities/import', form, { headers: { 'Content-Type': 'multipart/form-data' } });
};

// Function: getFinancialSummary
export const getFinancialSummary = () => api.get('financial-summary');

// Function: startFinancialNarrative
export const startFinancialNarrative = (userGuidance) =>
  api.post('financial-summary/narrative', { user_guidance: userGuidance?.trim() ? userGuidance.trim() : null });

// Function: getFinancialNarrativeJob
export const getFinancialNarrativeJob = (jobId) => api.get(`financial-summary/narrative/${jobId}`);

/**
 * Poll a financial-narrative job until done/failed — same backoff shape as
 * pollWaveJob, since this is the exact same "Ollama call might take a while" UX.
 */
// Function: pollFinancialNarrative
export async function pollFinancialNarrative(jobId, onProgress) {
  for (let attempt = 0; attempt < MAX_POLLS; attempt += 1) {
    const { data } = await getFinancialNarrativeJob(jobId);
    onProgress?.(data);
    if (data.status === 'done' || data.status === 'failed') {
      return data;
    }
    await new Promise((resolve) => setTimeout(resolve, POLL_DELAY_MS(attempt)));
  }
  throw new Error('Financial narrative job polling timed out.');
}

// Function: downloadWaveExport
export async function downloadWaveExport(jobId, category) {
  const response = await api.get(`wave/analysis/${jobId}/export`, {
    params: { category },
    responseType: 'blob',
  });
  const url = URL.createObjectURL(response.data);
  const a = document.createElement('a');
  const disposition = response.headers['content-disposition'] || '';
  const match = disposition.match(/filename="?([^"]+)"?/);
  a.href = url;
  a.download = match ? match[1] : `WavePlan_${category}.xlsx`;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}
