import { afterEach, expect, it, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { authApi } from '@/services/api';
import { useAuthStore } from '@/store';
import { OAuthCallbackPage } from './OAuthCallbackPage';

vi.mock('@/services/api', () => ({ authApi: { me: vi.fn() } }));
vi.mock('react-hot-toast', () => ({ default: { success: vi.fn(), error: vi.fn() } }));

afterEach(() => {
  vi.restoreAllMocks();
  vi.clearAllMocks();
  localStorage.clear();
  useAuthStore.getState().setUser(null);
});

function renderCallback() {
  return render(<QueryClientProvider client={new QueryClient()}>
    <MemoryRouter initialEntries={['/oauth/callback?access_token=test-access&refresh_token=test-refresh']}>
      <Routes>
        <Route path="/oauth/callback" element={<OAuthCallbackPage />} />
        <Route path="/login" element={<h1>Sign in</h1>} />
      </Routes>
    </MemoryRouter>
  </QueryClientProvider>);
}

it.each(['SecurityError', 'QuotaExceededError'])('returns to sign in when OAuth credential storage fails with %s', async name => {
  const setItem = Storage.prototype.setItem;
  vi.spyOn(Storage.prototype, 'setItem').mockImplementation(function (this: Storage, key, value) {
    if (key === 'refresh_token') throw new DOMException('Unavailable', name);
    setItem.call(this, key, value);
  });
  renderCallback();
  expect(await screen.findByRole('heading', { name: 'Sign in' })).toBeDefined();
  expect(authApi.me).not.toHaveBeenCalled();
  expect(localStorage.getItem('access_token')).toBeNull();
  expect(useAuthStore.getState().isAuthenticated).toBe(false);
  expect(toast.error).toHaveBeenCalledWith(expect.stringContaining('browser storage'));
});

it('returns to sign in if storage is blocked during profile-error cleanup', async () => {
  vi.mocked(authApi.me).mockRejectedValue(new Error('Profile unavailable'));
  vi.spyOn(Storage.prototype, 'removeItem').mockImplementation(() => { throw new DOMException('Blocked', 'SecurityError'); });
  renderCallback();
  await waitFor(() => expect(screen.getByRole('heading', { name: 'Sign in' })).toBeDefined());
  expect(useAuthStore.getState().isAuthenticated).toBe(false);
});
