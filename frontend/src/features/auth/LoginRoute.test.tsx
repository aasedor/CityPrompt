import { beforeEach, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MemoryRouter } from 'react-router-dom';
import App from '@/App';
import { useAuthStore } from '@/store';

vi.mock('@/services/api', () => ({
  authApi: { me: vi.fn() },
  subscribeAssetTicketChanges: () => () => {},
  getAssetTicketRevision: () => 0,
  refreshAssetTickets: async () => {},
}));
vi.mock('@/hooks/useGenerationPolling', () => ({ useGenerationPolling: () => {} }));

beforeEach(() => {
  localStorage.clear();
  useAuthStore.setState({ user: null, isAuthenticated: false, isLoading: false });
});

it('opens the current student landing and sign-in form at the login route', () => {
  render(<QueryClientProvider client={new QueryClient()}>
    <MemoryRouter initialEntries={['/login']}><App /></MemoryRouter>
  </QueryClientProvider>);
  expect(screen.getByRole('heading', { name: /build your\s*final project/i })).toBeDefined();
  expect(screen.getByLabelText('Email')).toBeDefined();
  expect(screen.getByLabelText('Password')).toBeDefined();
});
