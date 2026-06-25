import api from '../lib/api-client';

export const authService = {
  async login(email, password) {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);

    const response = await api.post('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    return response.data;
  },

  async register(data) {
    const response = await api.post('/auth/register', data);
    return response.data;
  },

  async getCurrentUser() {
    const response = await api.get('/users/me');
    return response.data;
  },
};
