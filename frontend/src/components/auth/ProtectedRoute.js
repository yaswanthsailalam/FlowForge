import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { useWorkspace } from '../../contexts/WorkspaceContext';

const ProtectedRoute = ({ children, requireWorkspace = true }) => {
  const { isAuthenticated, loading: authLoading } = useAuth();
  const { activeWorkspace, loading: wsLoading } = useWorkspace();
  const location = useLocation();

  if (authLoading) {
    return <div className="flex h-screen items-center justify-center">Loading...</div>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (requireWorkspace && !wsLoading && !activeWorkspace) {
    // If we're not on the workspace selection/creation pages, redirect there
    if (location.pathname !== '/workspaces' && location.pathname !== '/workspaces/create') {
      return <Navigate to="/workspaces" replace />;
    }
  }

  return children;
};

export default ProtectedRoute;
