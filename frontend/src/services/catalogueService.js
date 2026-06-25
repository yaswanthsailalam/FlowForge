import api from '@/lib/api-client';

const catalogueService = {
  getIndustries: () => api.get('/catalogue/industries'),
  getBusinessSegments: (industryId) => api.get('/catalogue/business-segments', { params: { industry_id: industryId } }),
  getDepartments: () => api.get('/catalogue/departments'),
  getTeams: (departmentId) => api.get('/catalogue/teams', { params: { department_id: departmentId } }),
  getProcessFamilies: () => api.get('/catalogue/process-families'),

  getProcessModels: (params) => api.get('/catalogue/process-models', { params }),
  getProcessModel: (modelId) => api.get(`/catalogue/process-models/${modelId}`),
  createProcessModel: (data) => api.post('/catalogue/process-models', data),
  updateProcessModel: (modelId, data) => api.patch(`/catalogue/process-models/${modelId}`, data),
  publishProcessModel: (modelId) => api.post(`/catalogue/process-models/${modelId}/publish`),
  archiveProcessModel: (modelId) => api.post(`/catalogue/process-models/${modelId}/archive`),

  getVariants: (modelId) => api.get(`/catalogue/process-models/${modelId}/variants`),
  getVariant: (variantId) => api.get(`/catalogue/variants/${variantId}`),
  createVariant: (data) => api.post('/catalogue/variants', data),

  getWorkflowTemplates: (params) => api.get('/catalogue/workflow-templates', { params }),
  getWorkflowTemplate: (templateId) => api.get(`/catalogue/workflow-templates/${templateId}`),
  createWorkflowTemplate: (data) => api.post('/catalogue/workflow-templates', data),

  toggleFavourite: (modelId) => api.post(`/catalogue/process-models/${modelId}/favourite`),
  getFavourites: () => api.get('/catalogue/favourites'),
};

export default catalogueService;
