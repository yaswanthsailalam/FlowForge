import api from '@/lib/api-client';

const workflowService = {
  // Draft Creation
  createBlankDraft: (data) => api.post('/workflows/draft/blank', data),
  createDraftFromModel: (modelId, data) => api.post(`/workflows/draft/from-model/${modelId}`, data),
  createDraftFromVariant: (variantId, data) => api.post(`/workflows/draft/from-variant/${variantId}`, data),
  createDraftFromTemplate: (templateId, data) => api.post(`/workflows/draft/from-template/${templateId}`, data),

  // Draft Management
  getDrafts: () => api.get('/workflows/drafts'),
  getDraft: (workflowId) => api.get(`/workflows/drafts/${workflowId}`),
  updateDraft: (workflowId, data) => api.patch(`/workflows/drafts/${workflowId}`, data),
  validateDraft: (workflowId) => api.post(`/workflows/drafts/${workflowId}/validate`),

  // Versions and Runs (Placeholder for potential future use or integration with existing POC)
  getVersions: (workflowId) => api.get(`/poc/workflows/${workflowId}/versions`),
  publishWorkflow: (workflowId) => api.post(`/poc/workflows/${workflowId}/publish`),
};

export default workflowService;
