import axios from 'axios';

const api = axios.create({
  baseURL: `${process.env.REACT_APP_BACKEND_URL}/api`,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  const workspaceId = localStorage.getItem('workspaceId');
  if (workspaceId && !config.url.startsWith('/auth') && !config.url.startsWith('/workspaces')) {
    config.headers['X-Workspace-Id'] = workspaceId;
  }

  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('workspaceId');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
