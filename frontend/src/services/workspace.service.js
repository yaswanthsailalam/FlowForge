import api from '../lib/api-client';

export const workspaceService = {
  async listWorkspaces() {
    const response = await api.get('/workspaces/');
    return response.data;
  },

  async createWorkspace(data) {
    const response = await api.post('/workspaces/', data);
    return response.data;
  },

  async getActiveWorkspace() {
    const response = await api.get('/workspaces/me');
    return response.data;
  },
};
