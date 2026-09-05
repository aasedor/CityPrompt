import { lazy, Suspense, useEffect, useSyncExternalStore } from 'react';
import { Routes, Route } from 'react-router-dom';
import { Layout } from '@/components/layout/Layout';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { GenerationProgressBar } from '@/components/GenerationProgressBar';
import { useGenerationPolling } from '@/hooks/useGenerationPolling';
import { LandingPage } from '@/features/landing/LandingPage';
import { ProjectListPage } from '@/features/projects/ProjectListPage';
import { SharedProjectPage } from '@/features/projects/SharedProjectPage';
import { InvitationPage } from '@/features/projects/InvitationPage';
import { LoginPage } from '@/features/auth/LoginPage';
import { RegisterPage } from '@/features/auth/RegisterPage';
import { OAuthCallbackPage } from '@/features/auth/OAuthCallbackPage';
import { ForgotPasswordPage } from '@/features/auth/ForgotPasswordPage';
import { ResetPasswordPage } from '@/features/auth/ResetPasswordPage';
import { ChangePasswordPage } from '@/features/auth/ChangePasswordPage';
import { FeedbackWidget } from '@/components/FeedbackWidget';
import { useAuthStore } from '@/store';
import { authApi, getAssetTicketRevision, refreshAssetTickets, subscribeAssetTicketChanges } from '@/services/api';
import '@/store/themeStore';

// Load the 3D editor and staff tools when those pages are opened. Joining a
// team or signing in should not first download the entire design workspace.
const ProjectViewPage = lazy(() => import('@/features/projects/ProjectViewPage').then((module) => ({ default: module.ProjectViewPage })));
const AdminDashboardPage = lazy(() => import('@/features/admin/AdminDashboardPage').then((module) => ({ default: module.AdminDashboardPage })));
const AdminUsersPage = lazy(() => import('@/features/admin/AdminUsersPage').then((module) => ({ default: module.AdminUsersPage })));
const AdminProjectsPage = lazy(() => import('@/features/admin/AdminProjectsPage').then((module) => ({ default: module.AdminProjectsPage })));
const AdminBuildingsPage = lazy(() => import('@/features/admin/AdminBuildingsPage').then((module) => ({ default: module.AdminBuildingsPage })));
const AdminRenderLogsPage = lazy(() => import('@/features/admin/AdminRenderLogsPage').then((module) => ({ default: module.AdminRenderLogsPage })));
const ConfirmRoleChangePage = lazy(() => import('@/features/admin/ConfirmRoleChangePage').then((module) => ({ default: module.ConfirmRoleChangePage })));
const CofounderAnalyticsPage = lazy(() => import('@/features/admin/CofounderAnalyticsPage').then((module) => ({ default: module.CofounderAnalyticsPage })));
const AdminFeedbackPage = lazy(() => import('@/features/admin/AdminFeedbackPage').then((module) => ({ default: module.AdminFeedbackPage })));

export default function App() {
  const { setUser, setLoading } = useAuthStore();
  // Ticket renewal rerenders saved media URLs, including videos played later
  // in a long studio session. Resume events cover sleeping/background tabs.
  useSyncExternalStore(subscribeAssetTicketChanges, getAssetTicketRevision, getAssetTicketRevision);
  useEffect(() => {
    const renew = () => { if (document.visibilityState === 'visible') void refreshAssetTickets(); };
    const timer = window.setInterval(renew, 60_000);
    window.addEventListener('focus', renew); window.addEventListener('online', renew);
    document.addEventListener('visibilitychange', renew);
    return () => { window.clearInterval(timer); window.removeEventListener('focus', renew);
      window.removeEventListener('online', renew); document.removeEventListener('visibilitychange', renew); };
  }, []);

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
    <Suspense fallback={<main role="status" className="p-8 text-center text-slate-700">Loading City Prompt…</main>}><Routes>
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
        <Route path="/admin/render-logs" element={<ProtectedRoute requiredRole="admin"><AdminRenderLogsPage /></ProtectedRoute>} />
        <Route path="/admin/feedback" element={<ProtectedRoute requiredRole="admin"><AdminFeedbackPage /></ProtectedRoute>} />
        <Route path="/admin/analytics" element={<ProtectedRoute requiredRole="cofounder"><CofounderAnalyticsPage /></ProtectedRoute>} />
        <Route path="/admin/confirm-role-change" element={<ProtectedRoute requiredRole="admin"><ConfirmRoleChangePage /></ProtectedRoute>} />
      </Route>
      {/* Shared project view (public link) */}
      <Route path="/shared/:token" element={<SharedProjectPage />} />
      <Route path="/invite/:token" element={<InvitationPage />} />
    </Routes></Suspense>
    <FeedbackWidget />
    <GenerationProgressBar />
    </>
  );
}
