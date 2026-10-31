import { StrictMode } from 'react';
import { afterEach, beforeEach, expect, it, vi } from 'vitest';
import { act, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { authApi } from '@/services/api';
import { useAuthStore } from '@/store';
import { OAuthCallbackPage } from './OAuthCallbackPage';

vi.mock('@/services/api', () => ({ authApi: { me: vi.fn(), exchangeOAuthCode: vi.fn() } }));
vi.mock('react-hot-toast', () => ({ default: { success: vi.fn(), error: vi.fn() } }));

afterEach(() => {
  vi.restoreAllMocks();
  vi.clearAllMocks();
  localStorage.clear();
  sessionStorage.clear();
  useAuthStore.getState().setUser(null);
});

const user = { id: 'user-a', email: 'student@example.test', full_name: 'Student',
  role: 'editor', is_active: true, render_credits: 10, created_at: '2026-10-01T00:00:00Z' };

beforeEach(() => {
  vi.mocked(authApi.me).mockResolvedValue(user);
  sessionStorage.setItem('cityprompt_oauth_verifier', 'v'.repeat(43));
  vi.mocked(authApi.exchangeOAuthCode).mockResolvedValue({
    access_token: 'test-access', refresh_token: 'test-refresh', user, token_type: 'bearer',
  });
});

function renderCallback(url = '/oauth/callback?code=opaque-code', strict = false) {
  const tree = <QueryClientProvider client={new QueryClient()}>
    <MemoryRouter initialEntries={[url]}>
      <Routes>
        <Route path="/oauth/callback" element={<OAuthCallbackPage />} />
        <Route path="/login" element={<h1>Sign in</h1>} />
        <Route path="/projects" element={<h1>Projects</h1>} />
        <Route path="/projects/saved-project" element={<h1>Saved project</h1>} />
      </Routes>
    </MemoryRouter>
  </QueryClientProvider>;
  return render(strict ? <StrictMode>{tree}</StrictMode> : tree);
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

it.each([false, true])('completes valid sign-in when return preference access is blocked: %s', async blocked => {
  localStorage.setItem('oauth_return_to', '/projects/saved-project');
  if (blocked) {
    const getItem = Storage.prototype.getItem;
    vi.spyOn(Storage.prototype, 'getItem').mockImplementation(function (this: Storage, key) {
      if (key === 'oauth_return_to') throw new DOMException('Blocked', 'SecurityError');
      return getItem.call(this, key);
    });
    const removeItem = Storage.prototype.removeItem;
    vi.spyOn(Storage.prototype, 'removeItem').mockImplementation(function (this: Storage, key) {
      if (this === localStorage) throw new DOMException('Blocked', 'SecurityError');
      removeItem.call(this, key);
    });
  }
  renderCallback();
  expect(await screen.findByRole('heading', { name: blocked ? 'Projects' : 'Saved project' })).toBeDefined();
  expect(useAuthStore.getState().user).toEqual(user);
  expect(useAuthStore.getState().isAuthenticated).toBe(true);
  expect(localStorage.getItem('access_token')).toBe('test-access');
  expect(localStorage.getItem('refresh_token')).toBe('test-refresh');
  expect(toast.error).not.toHaveBeenCalled();
  if (!blocked) expect(localStorage.getItem('oauth_return_to')).toBeNull();
});

it('returns to sign in if storage is blocked during profile-error cleanup', async () => {
  vi.mocked(authApi.exchangeOAuthCode).mockRejectedValue(new Error('Exchange unavailable'));
  vi.spyOn(Storage.prototype, 'removeItem').mockImplementation(() => { throw new DOMException('Blocked', 'SecurityError'); });
  renderCallback();
  await waitFor(() => expect(screen.getByRole('heading', { name: 'Sign in' })).toBeDefined());
  expect(useAuthStore.getState().isAuthenticated).toBe(false);
});

it('exchanges once under StrictMode and removes the verifier', async () => {
  renderCallback(undefined, true);
  expect(await screen.findByRole('heading', { name: 'Projects' })).toBeDefined();
  expect(authApi.exchangeOAuthCode).toHaveBeenCalledExactlyOnceWith('opaque-code', 'v'.repeat(43));
  expect(sessionStorage.getItem('cityprompt_oauth_verifier')).toBeNull();
  expect(authApi.me).not.toHaveBeenCalled();
});

it.each(['?access_token=old-access&refresh_token=old-refresh', '#access_token=old-access&refresh_token=old-refresh'])('never accepts bearer callback credentials from %s', async suffix => {
  renderCallback('/oauth/callback' + suffix);
  expect(await screen.findByRole('heading', { name: 'Sign in' })).toBeDefined();
  expect(authApi.exchangeOAuthCode).not.toHaveBeenCalled();
  expect(localStorage.getItem('access_token')).toBeNull();
});

it('requires the initiating tab verifier before exchanging a code', async () => {
  sessionStorage.clear();
  renderCallback();
  expect(await screen.findByRole('heading', { name: 'Sign in' })).toBeDefined();
  expect(authApi.exchangeOAuthCode).not.toHaveBeenCalled();
});

it('does not publish an old exchange after the callback has unmounted', async () => {
  let release!: () => void;
  const wait = new Promise<void>(resolve => { release = resolve; });
  vi.mocked(authApi.exchangeOAuthCode).mockImplementationOnce(async () => {
    await wait;
    return { access_token: 'old-access', refresh_token: 'old-refresh', user, token_type: 'bearer' };
  });
  const view = renderCallback();
  view.unmount();
  localStorage.setItem('access_token', 'new-access');
  localStorage.setItem('refresh_token', 'new-refresh');
  await act(async () => { release(); });
  expect(localStorage.getItem('access_token')).toBe('new-access');
  expect(localStorage.getItem('refresh_token')).toBe('new-refresh');
});
