import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { workspaceService } from '../services/workspace.service';
import { useAuth } from './AuthContext';

const WorkspaceContext = createContext(null);

export const WorkspaceProvider = ({ children }) => {
  const { isAuthenticated } = useAuth();
  const [workspaces, setWorkspaces] = useState([]);
  const [activeWorkspace, setActiveWorkspace] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const refreshWorkspaces = useCallback(async () => {
    if (!isAuthenticated) return;

    setLoading(true);
    try {
      const list = await workspaceService.listWorkspaces();
      setWorkspaces(list);

      const savedId = localStorage.getItem('workspaceId');
      if (savedId) {
        const found = list.find(w => w.workspace_id === savedId);
        if (found) {
          setActiveWorkspace(found);
        } else {
          localStorage.removeItem('workspaceId');
          setActiveWorkspace(null);
        }
      } else if (list.length === 1) {
        // Auto-select if only one workspace
        selectWorkspace(list[0]);
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load workspaces');
    } finally {
      setLoading(false);
    }
  }, [isAuthenticated]);

  useEffect(() => {
    refreshWorkspaces();
  }, [refreshWorkspaces]);

  const selectWorkspace = (workspace) => {
    if (workspace) {
      localStorage.setItem('workspaceId', workspace.workspace_id);
    } else {
      localStorage.removeItem('workspaceId');
    }
    setActiveWorkspace(workspace);
  };

  const createWorkspace = async (name) => {
    setLoading(true);
    try {
      const newWorkspace = await workspaceService.createWorkspace({ name });
      await refreshWorkspaces();
      selectWorkspace(newWorkspace);
      return newWorkspace;
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create workspace');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return (
    <WorkspaceContext.Provider value={{
      workspaces,
      activeWorkspace,
      loading,
      error,
      selectWorkspace,
      createWorkspace,
      refreshWorkspaces
    }}>
      {children}
    </WorkspaceContext.Provider>
  );
};

export const useWorkspace = () => {
  const context = useContext(WorkspaceContext);
  if (!context) {
    throw new Error('useWorkspace must be used within a WorkspaceProvider');
  }
  return context;
};
