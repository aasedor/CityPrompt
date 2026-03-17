import { useEffect } from 'react';
import { Routes, Route } from 'react-router-dom';
import { Layout } from '@/components/layout/Layout';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { GenerationProgressBar } from '@/components/GenerationProgressBar';
import { useGenerationPolling } from '@/hooks/useGenerationPolling';
import { LandingPage } from '@/features/landing/LandingPage';
import { ProjectListPage } from '@/features/projects/ProjectListPage';
import { ProjectViewPage } from '@/features/projects/ProjectViewPage';
import { ViewerPage } from '@/features/projects/ViewerPage';
import { SharedProjectPage } from '@/features/projects/SharedProjectPage';
import { LoginPage } from '@/features/auth/LoginPage';
import { RegisterPage } from '@/features/auth/RegisterPage';
import { OAuthCallbackPage } from '@/features/auth/OAuthCallbackPage';
import { ForgotPasswordPage } from '@/features/auth/ForgotPasswordPage';
import { ResetPasswordPage } from '@/features/auth/ResetPasswordPage';
import { ChangePasswordPage } from '@/features/auth/ChangePasswordPage';
import { AdminDashboardPage } from '@/features/admin/AdminDashboardPage';
import { AdminUsersPage } from '@/features/admin/AdminUsersPage';
import { AdminProjectsPage } from '@/features/admin/AdminProjectsPage';
import { AdminBuildingsPage } from '@/features/admin/AdminBuildingsPage';
import { ConfirmRoleChangePage } from '@/features/admin/ConfirmRoleChangePage';
import { CofounderAnalyticsPage } from '@/features/admin/CofounderAnalyticsPage';
import { BlockEditorPage } from '@/features/block-editor/BlockEditorPage';
import { useAuthStore } from '@/store';
import { authApi } from '@/services/api';


export default function App() {
  const { setUser, setLoading } = useAuthStore();

  // Global generation progress polling — runs on all pages
  useGenerationPolling();

  // On mount, check if we have a valid token and load user
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      // Safety timeout: if the API never responds, stop loading after 10s
      const safetyTimeout = setTimeout(() => setUser(null), 10000);
      authApi
        .me()
        .then((user) => setUser(user))
        .catch(() => {
          setUser(null);
        })
        .finally(() => clearTimeout(safetyTimeout));
    } else {
      setLoading(false);
    }
  }, [setUser, setLoading]);

  return (
    <>
    <Routes>
      {/* Public landing page */}
      <Route path="/" element={<LandingPage />} />

      {/* Auth routes */}
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/oauth/callback" element={<OAuthCallbackPage />} />
      <Route path="/forgot-password" element={<ForgotPasswordPage />} />
      <Route path="/reset-password" element={<ResetPasswordPage />} />

      {/* App routes — require authentication */}
      <Route element={<ProtectedRoute><Layout /></ProtectedRoute>}>
        <Route path="/projects" element={<ProjectListPage />} />
        <Route path="/projects/:id" element={<ProjectViewPage />} />
        <Route path="/settings/password" element={<ChangePasswordPage />} />
        {/* Admin routes — require admin role */}
        <Route path="/admin" element={<ProtectedRoute requiredRole="admin"><AdminDashboardPage /></ProtectedRoute>} />
        <Route path="/admin/users" element={<ProtectedRoute requiredRole="admin"><AdminUsersPage /></ProtectedRoute>} />
        <Route path="/admin/projects" element={<ProtectedRoute requiredRole="admin"><AdminProjectsPage /></ProtectedRoute>} />
        <Route path="/admin/buildings" element={<ProtectedRoute requiredRole="admin"><AdminBuildingsPage /></ProtectedRoute>} />
        <Route path="/admin/analytics" element={<ProtectedRoute requiredRole="cofounder"><CofounderAnalyticsPage /></ProtectedRoute>} />
        <Route path="/admin/confirm-role-change" element={<ProtectedRoute requiredRole="admin"><ConfirmRoleChangePage /></ProtectedRoute>} />
      </Route>
      {/* Block Editor - full-screen interactive layout editor */}
      <Route path="/projects/:id/block-editor/:zoneId" element={<ProtectedRoute><BlockEditorPage /></ProtectedRoute>} />
      {/* Viewer is full-screen, no layout wrapper */}
      <Route path="/projects/:id/viewer" element={<ProtectedRoute><ViewerPage /></ProtectedRoute>} />
      {/* Shared project view (public link) */}
      <Route path="/shared/:token" element={<SharedProjectPage />} />
    </Routes>
    <GenerationProgressBar />
    </>
  );
}
