// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: AppRationalization â€” frontend/src/services (api.js)
// Date: 2025-11-26
// ---------------------------------------------------------------------------
import axios from 'axios';
import { getAuthToken } from './authSession';

/**
 * API base URL resolution:
 *  - Local dev (npm start):       .env.development.local â†’ http://localhost:5000/api
 *  - Production build (npm build): .env.production       â†’ https://api.aqorynthapp.org/api
 *  - Fallback when env var absent: same-origin /api
 */
// Function: resolveApiBase
const resolveApiBase = () => {
  const configured = process.env.REACT_APP_API_URL;
  if (configured) {
    return configured.replace(/\/+$/, '');
  }
  // No env var â€” infer from browser origin
  return window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:5001/api'
    : '/api';
};

export const API_BASE = resolveApiBase();

const apiClient = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.request.use((config) => {
  const token = getAuthToken();
  if (token) {
    config.headers = config.headers || {};
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Upload endpoints
// Function: uploadInfrastructure
export const uploadInfrastructure = (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return apiClient.post('/upload/infrastructure', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
};

// Function: uploadCodeAnalysis
export const uploadCodeAnalysis = (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return apiClient.post('/upload/code-analysis', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
};

// Function: extractCastAnalysis
export const extractCastAnalysis = (fileId) =>
  apiClient.post(`/upload/extract-cast-analysis/${fileId}`);

// Function: uploadIndustryTemplates
export const uploadIndustryTemplates = (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return apiClient.post('/upload/industry-templates', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
};

// Function: getUploadedFiles
export const getUploadedFiles = () => apiClient.get('/upload/files');
// Function: deleteFile
export const deleteFile = (fileId) => apiClient.delete(`/upload/file/${fileId}`);

// Industry Templates endpoints
// Function: getIndustryTemplates
export const getIndustryTemplates = () => apiClient.get('/upload/industry-templates/files');
// Function: getIndustryData
export const getIndustryData = (fileId, page = 1, perPage = 20) =>
  apiClient.get(`/upload/industry-templates/${fileId}/data`, {
    params: { page, per_page: perPage }
  });
// Function: deleteIndustryTemplate
export const deleteIndustryTemplate = (fileId) => apiClient.delete(`/upload/industry-templates/${fileId}`);
// Function: previewIndustryTemplate
export const previewIndustryTemplate = (fileId) => apiClient.get(`/upload/industry-templates/preview/${fileId}`);

// PDF Extraction endpoints
// Function: extractPDFData
export const extractPDFData = (fileId, page = 1, perPage = 20) => 
  apiClient.post(`/upload/extract-pdf/${fileId}`, null, {
    params: { page, per_page: perPage }
  });

// Function: getDiscoveredApplications
export const getDiscoveredApplications = (fileId, page = 1, perPage = 20) =>
  apiClient.get(`/upload/infrastructure/${fileId}/discovered-apps`, {
    params: { page, per_page: perPage }
  });

// Function: getPDFReports
export const getPDFReports = (type = null) => {
  const params = type ? { type } : {};
  return apiClient.get('/upload/reports/pdf', { params });
};

// Function: getPDFReport
export const getPDFReport = (reportId) =>
  apiClient.get(`/upload/reports/pdf/${reportId}`);

// Function: searchPDFReports
export const searchPDFReports = (query, type = null) => {
  const params = { q: query };
  if (type) params.type = type;
  return apiClient.get('/upload/reports/pdf/search', { params });
};

// Correlation endpoints
// Function: startCorrelation
export const startCorrelation = () =>
  apiClient.post('/correlation/start');

// Function: getCorrelationJobStatus
export const getCorrelationJobStatus = () =>
  apiClient.get('/correlation/job-status');

// Function: getCorrelationData
export const getCorrelationData = () =>
  apiClient.get('/correlation/latest');

// Function: getLlmAnalysis
export const getLlmAnalysis = () =>
  apiClient.get('/correlation/llm-analysis');

// Function: rerunLlmAnalysis
export const rerunLlmAnalysis = () =>
  apiClient.post('/correlation/llm-analysis/rerun', null, { timeout: 210_000 }); // 210s > 200s server limit

// Function: getCorrelationDashboards
export const getCorrelationDashboards = () =>
  apiClient.get('/correlation/dashboards');

// Function: getCorrelationMasterMatrix
export const getCorrelationMasterMatrix = (confidenceLevel = null, limit = 1000) => {
  const params = { limit };
  if (confidenceLevel) params.confidence_level = confidenceLevel;
  return apiClient.get('/correlation/master-matrix', { params });
};

// Function: getCorrelationStatistics
export const getCorrelationStatistics = () =>
  apiClient.get('/correlation/statistics');

// Consolidated DB + Ollama endpoints
// Function: getConsolidatedApps
export const getConsolidatedApps = () =>
  apiClient.get('/correlation/consolidated');

// Function: getConsolidatedStats
export const getConsolidatedStats = () =>
  apiClient.get('/correlation/consolidated/stats');

// Function: getOllamaStatus
export const getOllamaStatus = () =>
  apiClient.get('/correlation/ollama/status');

// Workspace pipeline endpoints â€” file copy, LLM fill, column traceability
// Function: getWorkspaceRuns
export const getWorkspaceRuns = (limit = 20) =>
  apiClient.get('/correlation/workspace/runs', { params: { limit } });

// Function: getWorkspaceColumnUpdates
export const getWorkspaceColumnUpdates = (runId = null, source = null, limit = 1000) => {
  const params = { limit };
  if (runId) params.run_id = runId;
  if (source) params.source = source;
  return apiClient.get('/correlation/workspace/column-updates', { params });
};

// Workspace row data (includes updated_rows per-row AI summary)
// Function: getWorkspaceCastRows
export const getWorkspaceCastRows = (runId = null, limit = 500) => {
  const params = { limit };
  if (runId) params.run_id = runId;
  return apiClient.get('/correlation/workspace/cast', { params });
};

// Function: getWorkspaceCorentRows
export const getWorkspaceCorentRows = (runId = null, limit = 500) => {
  const params = { limit };
  if (runId) params.run_id = runId;
  return apiClient.get('/correlation/workspace/corent', { params });
};

// Function: getWorkspaceBizRows
export const getWorkspaceBizRows = (runId = null, limit = 500) => {
  const params = { limit };
  if (runId) params.run_id = runId;
  return apiClient.get('/correlation/workspace/business', { params });
};

// Drill-down: apps by cloud-suitability group (L2) and single-app detail (L3)
// Function: getAppsByCloudGroup
export const getAppsByCloudGroup = () =>
  apiClient.get('/correlation/apps/cloud-groups');

// Function: getAppDetail
export const getAppDetail = (appId) =>
  apiClient.get(`/correlation/apps/${encodeURIComponent(appId)}/detail`);

// Function: getWorkspaceCorrelations
export const getWorkspaceCorrelations = (runId = null, matchType = null, limit = 500) => {
  const params = { limit };
  if (runId) params.run_id = runId;
  if (matchType) params.match_type = matchType;
  return apiClient.get('/correlation/workspace/correlations', { params });
};

// Analysis endpoints
// Function: correlateInfraAndCode
export const correlateInfraAndCode = (infrastructureId, repositoryId) =>
  apiClient.post('/analysis/correlate', {
    infrastructure_id: infrastructureId,
    repository_id: repositoryId,
  });

// Function: getInfrastructureSummary
export const getInfrastructureSummary = (infraId) =>
  apiClient.get(`/analysis/infrastructure/${infraId}/summary`);

// Function: getCodeSummary
export const getCodeSummary = (repoId) =>
  apiClient.get(`/analysis/code/${repoId}/summary`);

// Function: getAllApplications
export const getAllApplications = () => apiClient.get('/analysis/applications');
// Function: getAllInfrastructure
export const getAllInfrastructure = () => apiClient.get('/analysis/infrastructure');
// Function: getAllRepositories
export const getAllRepositories = () => apiClient.get('/analysis/code-repositories');
// Function: getAnalysisHistory
export const getAnalysisHistory = () => apiClient.get('/analysis/analysis-history');

// Capability endpoints
// Function: getCapabilities
export const getCapabilities = () => apiClient.get('/capabilities');
// Function: getCapabilityById
export const getCapabilityById = (id) => apiClient.get(`/capability/${id}`);
// Function: getCapabilityByName
export const getCapabilityByName = (name) => apiClient.get(`/capability/by-name/${name}`);
// Function: createCapabilityMapping
export const createCapabilityMapping = (data) =>
  apiClient.post('/capability-map', data);

// Rationalization endpoints
// Function: getRationalizationScenarios
export const getRationalizationScenarios = () =>
  apiClient.get('/rationalization-scenarios');

// Function: getRationalizationScenario
export const getRationalizationScenario = (id) =>
  apiClient.get(`/rationalization-scenario/${id}`);

// Function: getScenariosByCapability
export const getScenariosByCapability = (capability) =>
  apiClient.get(`/rationalization-scenarios/by-capability/${capability}`);

// Function: createRationalizationScenario
export const createRationalizationScenario = (data) =>
  apiClient.post('/rationalization-scenario', data);

// Dashboard endpoints
// Function: getDashboardData
export const getDashboardData = () => apiClient.get('/dashboard');
// Function: getTraceabilityMatrix
export const getTraceabilityMatrix = () => apiClient.get('/correlation/traceability/matrix');
// Function: getInitializationStatus
export const getInitializationStatus = () => apiClient.get('/initialization-status');
// Function: initializeTestData
export const initializeTestData = () => apiClient.post('/initialize-test-data');

// Initialize defaults
// Function: initializeDefaults
export const initializeDefaults = () =>
  apiClient.post('/initialize-defaults');

// Function: getTechnicalAssessmentData
export const getTechnicalAssessmentData = (dataset, page = 1, perPage = 25, search = '') =>
  apiClient.get(`/technical-assessment/${dataset}`, { params: { page, per_page: perPage, search } });

// Function: uploadTechnicalAssessment
export const uploadTechnicalAssessment = (dataset, file) => {
  const formData = new FormData();
  formData.append('file', file);
  return apiClient.post(`/technical-assessment/${dataset}/upload`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};

// Function: clearTechnicalAssessmentData
export const clearTechnicalAssessmentData = (dataset) =>
  apiClient.delete(`/technical-assessment/${dataset}/clear`);

// Technical Evaluation - Categorize dashboard endpoints
// Function: getTechnicalEvaluationCategorizeDashboard
export const getTechnicalEvaluationCategorizeDashboard = (topic = '', search = '') =>
  apiClient.get('/technical-assessment/technical-evaluation-categorize', {
    params: { topic: topic || undefined, search: search || undefined },
  });

// Function: uploadTechnicalEvaluationCategorize
export const uploadTechnicalEvaluationCategorize = (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return apiClient.post('/technical-assessment/technical-evaluation-categorize/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};

// Function: enrichTechnicalEvaluationCategorizeTopic
export const enrichTechnicalEvaluationCategorizeTopic = (topic) =>
  apiClient.post('/technical-assessment/technical-evaluation-categorize/enrich', { topic }, { timeout: 600_000 });

// Wave Plan endpoints
// Function: getWavePlanTopics
export const getWavePlanTopics = () => apiClient.get('/wave-plan/topics');
// Function: generateWavePlan
export const generateWavePlan = (payload) =>
  apiClient.post('/wave-plan/generate', payload, { timeout: 180_000 });
// Function: getLatestWavePlan
export const getLatestWavePlan = (topic) =>
  apiClient.get('/wave-plan/latest', { params: topic ? { topic } : {} });

// Wave Schedule endpoints (rule-based scaffold, always reviewed by Ollama)
// Function: getWaveScheduleTopics
export const getWaveScheduleTopics = () => apiClient.get('/wave-schedule/topics');
// Function: getWaveSchedule
// Synchronous variant â€” kept for small/API use, but "Predict Wave Planning"
// uses the async job endpoints below (batched Ollama review can take a
// while on this shared GPU, so it shouldn't block one HTTP request).
// Function: getWaveSchedule
export const getWaveSchedule = (topic, params = {}) =>
  apiClient.get('/wave-schedule', { params: { topic, ...params }, timeout: 220_000 });

// Function: startWaveSchedulePrediction
export const startWaveSchedulePrediction = (topic) =>
  apiClient.post('/wave-schedule/predict', topic ? { topic } : {});
// Function: getWaveScheduleJob
export const getWaveScheduleJob = (jobId) =>
  apiClient.get(`/wave-schedule/predict/${jobId}`);

// Function: downloadWaveScheduleExport
// Fetches the formatted .xlsx as a blob (via apiClient so the Bearer token
// is attached) and triggers a browser download â€” a plain <a href> can't
// carry the auth header this app requires.
// Function: downloadWaveScheduleExport
export const downloadWaveScheduleExport = async (scheduleId) => {
  const response = await apiClient.get(`/wave-schedule/export/${scheduleId}`, {
    responseType: 'blob',
  });
  const disposition = response.headers['content-disposition'] || '';
  const match = disposition.match(/filename="?([^";]+)"?/);
  const filename = match ? match[1] : `Wave_Plan_${scheduleId}.xlsx`;
  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
};

// Golden Data endpoints
// Function: generateGoldenData
export const generateGoldenData = () => apiClient.post('/golden-data/generate');
// Function: getGoldenDataPreview
export const getGoldenDataPreview = () => apiClient.get('/golden-data/preview');
// Function: getGoldenDataDownloadUrl
export const getGoldenDataDownloadUrl = () => `${API_BASE}/golden-data/download`;
// Function: clearGoldenData
export const clearGoldenData = () => apiClient.post('/golden-data/clear');
// Function: getGoldenDataRecords
export const getGoldenDataRecords = (page = 1, perPage = 200, search = '') =>
  apiClient.get('/golden-data/records', { params: { page, per_page: perPage, search } });
// Function: updateGoldenDataRecord
export const updateGoldenDataRecord = (appId, data) =>
  apiClient.put(`/golden-data/records/${encodeURIComponent(appId)}`, data);
// Function: regenerateGoldenExcel
export const regenerateGoldenExcel = () => apiClient.post('/golden-data/regenerate-excel');

export default apiClient;
