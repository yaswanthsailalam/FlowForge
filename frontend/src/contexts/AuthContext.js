import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { authService } from '../services/auth.service';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadUser = useCallback(async () => {
    const token = localStorage.getItem('token');
    if (!token) {
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      const userData = await authService.getCurrentUser();
      setUser(userData);
    } catch (err) {
      console.error('Failed to load user', err);
      // Only clear token if it's an authentication error
      if (err.response?.status === 401) {
        localStorage.removeItem('token');
        localStorage.removeItem('workspaceId');
        setUser(null);
      }
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadUser();
  }, [loadUser]);

  const mapErrorMessage = (err) => {
    const detail = err.response?.data?.detail;
    if (typeof detail === 'string') {
      switch (detail) {
        case 'EMAIL_ALREADY_REGISTERED':
          return 'An account with this email already exists.';
        case 'DATABASE_UNAVAILABLE':
          return 'Service is temporarily unavailable. Please try again later.';
        case 'DATABASE_CONFIGURATION_ERROR':
          return 'Internal service configuration error. Support has been notified.';
        case 'INCORRECT_CREDENTIALS':
          return 'Incorrect email or password.';
        case 'INACTIVE_USER':
          return 'Your account is inactive. Please contact support.';
        default:
          return detail;
      }
    }

    if (err.message === 'Network Error') {
        return 'Unable to reach the FlowForge service. Please check your connection.';
    }

    return null;
  };

  const login = async (email, password) => {
    setError(null);
    setLoading(true);
    try {
      const data = await authService.login(email, password);
      localStorage.setItem('token', data.access_token);
      const userData = await authService.getCurrentUser();
      setUser(userData);
      return userData;
    } catch (err) {
      const message = mapErrorMessage(err) || 'Login failed. Please check your credentials.';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const register = async (userData) => {
    setError(null);
    setLoading(true);
    try {
      return await authService.register(userData);
    } catch (err) {
      const message = mapErrorMessage(err) || 'Registration failed. Please try again.';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('workspaceId');
    setUser(null);
    window.location.href = '/login';
  };

  return (
    <AuthContext.Provider value={{ user, loading, error, login, register, logout, isAuthenticated: !!user }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
