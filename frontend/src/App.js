import "@/App.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "@/contexts/AuthContext";
import { WorkspaceProvider } from "@/contexts/WorkspaceContext";
import ProtectedRoute from "@/components/auth/ProtectedRoute";
import PublicRoute from "@/components/auth/PublicRoute";

// Pages
import LoginPage from "@/pages/auth/LoginPage";
import RegisterPage from "@/pages/auth/RegisterPage";
import WorkspaceListPage from "@/pages/workspaces/WorkspaceListPage";
import WorkspaceCreatePage from "@/pages/workspaces/WorkspaceCreatePage";
import DashboardPage from "@/pages/dashboard/DashboardPage";
import AppLayout from "@/components/layout/AppLayout";
import PlaceholderPage from "@/pages/PlaceholderPage";

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <WorkspaceProvider>
          <Routes>
            {/* Public Routes */}
            <Route
              path="/login"
              element={
                <PublicRoute>
                  <LoginPage />
                </PublicRoute>
              }
            />
            <Route
              path="/register"
              element={
                <PublicRoute>
                  <RegisterPage />
                </PublicRoute>
              }
            />

            {/* Protected Routes (No Workspace required) */}
            <Route
              path="/workspaces"
              element={
                <ProtectedRoute requireWorkspace={false}>
                  <WorkspaceListPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/workspaces/create"
              element={
                <ProtectedRoute requireWorkspace={false}>
                  <WorkspaceCreatePage />
                </ProtectedRoute>
              }
            />

            {/* Protected Routes (Workspace required) */}
            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <AppLayout />
                </ProtectedRoute>
              }
            >
              <Route index element={<Navigate to="/dashboard" replace />} />
              <Route path="dashboard" element={<DashboardPage />} />
              <Route path="processes" element={<PlaceholderPage title="Process Catalogue" />} />
              <Route path="workflows" element={<PlaceholderPage title="Workflows" />} />
              <Route path="runs" element={<PlaceholderPage title="Runs" />} />
              <Route path="tasks" element={<PlaceholderPage title="Tasks" />} />
              <Route path="approvals" element={<PlaceholderPage title="Approvals" />} />
              <Route path="audit-logs" element={<PlaceholderPage title="Audit Logs" />} />
              <Route path="integrations" element={<PlaceholderPage title="Integrations" />} />
              <Route path="settings" element={<PlaceholderPage title="Members and Settings" />} />
            </Route>

            {/* Fallback */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </WorkspaceProvider>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
