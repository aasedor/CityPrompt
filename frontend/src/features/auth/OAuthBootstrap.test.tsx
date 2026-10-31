import { render, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MemoryRouter } from 'react-router-dom';
import { afterEach, expect, it, vi } from 'vitest';
import App from '@/App';
import { authApi } from '@/services/api';
import { useAuthStore } from '@/store';

vi.mock('@/services/api', () => ({
  authApi: { me: vi.fn(async () => ({ id: 'previous-account' })) },
  subscribeAssetTicketChanges: () => () => {},
  getAssetTicketRevision: () => 0,
  refreshAssetTickets: async () => {},
}));
vi.mock('@/hooks/useGenerationPolling', () => ({ useGenerationPolling: () => {} }));
vi.mock('./OAuthCallbackPage', () => ({ OAuthCallbackPage: () => null }));

afterEach(() => {
  localStorage.clear();
  window.history.replaceState(null, '', '/');
  useAuthStore.getState().setUser(null);
  vi.clearAllMocks();
});

it('leaves callback authentication to its exchange instead of bootstrapping a previous account', async () => {
  window.history.replaceState(null, '', '/oauth/callback?code=opaque');
  localStorage.setItem('access_token', 'previous-account-access');
  render(<QueryClientProvider client={new QueryClient()}>
    <MemoryRouter initialEntries={['/oauth/callback?code=opaque']}><App /></MemoryRouter>
  </QueryClientProvider>);
  await waitFor(() => expect(useAuthStore.getState().isLoading).toBe(false));
  expect(authApi.me).not.toHaveBeenCalled();
  expect(useAuthStore.getState().isAuthenticated).toBe(false);
});
