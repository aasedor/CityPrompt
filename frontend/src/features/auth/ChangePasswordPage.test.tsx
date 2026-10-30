import { fireEvent, render, screen } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { afterEach, expect, it, vi } from 'vitest';
import toast from 'react-hot-toast';
import { authApi } from '@/services/api';
import { useAuthStore } from '@/store';
import { ChangePasswordPage } from './ChangePasswordPage';

vi.mock('@/services/api', () => ({ authApi: { changePassword: vi.fn() } }));
vi.mock('react-hot-toast', () => ({ default: { success: vi.fn(), error: vi.fn() } }));

afterEach(() => {
  vi.clearAllMocks();
  localStorage.clear();
  useAuthStore.getState().setUser(null);
});

it('returns to sign-in after a password change revokes the current session', async () => {
  vi.mocked(authApi.changePassword).mockResolvedValue({ message: 'Password changed successfully' });
  localStorage.setItem('access_token', 'old-access');
  localStorage.setItem('refresh_token', 'old-refresh');
  useAuthStore.getState().setUser({ id: 'student', email: 'student@example.com', role: 'editor', is_active: true, render_credits: 1000, created_at: '2026-10-01T00:00:00Z' });
  render(<QueryClientProvider client={new QueryClient()}>
    <MemoryRouter initialEntries={['/change-password']}>
      <Routes>
        <Route path="/change-password" element={<ChangePasswordPage />} />
        <Route path="/login" element={<h1>Sign in again</h1>} />
      </Routes>
    </MemoryRouter>
  </QueryClientProvider>);
  fireEvent.change(screen.getByLabelText('Current password'), { target: { value: 'old-password' } });
  fireEvent.change(screen.getByLabelText('New password'), { target: { value: 'new-password' } });
  fireEvent.change(screen.getByLabelText('Confirm new password'), { target: { value: 'new-password' } });
  fireEvent.click(screen.getByRole('button', { name: 'Change password' }));
  expect(await screen.findByRole('heading', { name: 'Sign in again' })).toBeDefined();
  expect(localStorage.getItem('access_token')).toBeNull();
  expect(localStorage.getItem('refresh_token')).toBeNull();
  expect(useAuthStore.getState().isAuthenticated).toBe(false);
  expect(toast.success).toHaveBeenCalledWith(expect.stringContaining('Sign in again'));
});
