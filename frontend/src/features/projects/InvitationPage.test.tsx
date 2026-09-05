import '@testing-library/jest-dom/vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MemoryRouter, Route, Routes, useLocation } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { sharesApi } from '@/services/api';
import { useAuthStore } from '@/store';
import { InvitationPage } from './InvitationPage';

vi.mock('@/services/api', () => ({ sharesApi: { getInvitation: vi.fn(), acceptInvitation: vi.fn() }, authApi: { logout: vi.fn() }, getApiErrorMessage: (_: unknown, fallback: string) => fallback }));
vi.mock('@/utils/sessionReset', () => ({ resetSessionState: vi.fn() }));
function Destination() { return <p>Destination: {useLocation().pathname}</p>; }
function setup() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false }, mutations: { retry: false } } });
  return render(<QueryClientProvider client={client}><MemoryRouter initialEntries={['/invite/secret-token']}><Routes><Route path="/invite/:token" element={<InvitationPage />} /><Route path="/projects/:id" element={<Destination />} /></Routes></MemoryRouter></QueryClientProvider>);
}
describe('Project invitation', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useAuthStore.setState({ user: null, isAuthenticated: false, isLoading: false });
    vi.mocked(sharesApi.getInvitation).mockResolvedValue({ project_name: 'Our community', email: 'student@university.ca', permission: 'editor', accepted: false });
  });
  it('preserves the invitation through sign-in or registration without accepting automatically', async () => {
    setup();
    await screen.findByRole('heading', { name: 'Join Our community' });
    expect(screen.getByRole('link', { name: 'Sign in to continue' })).toHaveAttribute('href', '/login?returnTo=%2Finvite%2Fsecret-token');
    expect(screen.getByRole('link', { name: 'Create account' })).toHaveAttribute('href', '/register?returnTo=%2Finvite%2Fsecret-token');
    expect(sharesApi.acceptInvitation).not.toHaveBeenCalled();
  });
  it('requires the intended account, then opens the project only after acceptance succeeds', async () => {
    useAuthStore.setState({ user: { id: 'student', email: 'STUDENT@university.ca' } as never, isAuthenticated: true });
    vi.mocked(sharesApi.acceptInvitation).mockResolvedValue({ project_id: 'project-7' } as never);
    setup();
    fireEvent.click(await screen.findByRole('button', { name: 'Accept invitation' }));
    await screen.findByText('Destination: /projects/project-7');
    expect(sharesApi.acceptInvitation).toHaveBeenCalledWith('secret-token');
  });
  it('does not offer acceptance to a different signed-in account', async () => {
    useAuthStore.setState({ user: { id: 'other', email: 'other@example.com' } as never, isAuthenticated: true });
    setup();
    await screen.findByRole('alert');
    expect(screen.queryByRole('button', { name: 'Accept invitation' })).not.toBeInTheDocument();
    expect(sharesApi.acceptInvitation).not.toHaveBeenCalled();
  });
  it('keeps acceptance errors visible and allows a retry', async () => {
    useAuthStore.setState({ user: { id: 'student', email: 'student@university.ca' } as never, isAuthenticated: true });
    vi.mocked(sharesApi.acceptInvitation).mockRejectedValue(new Error('offline'));
    setup();
    fireEvent.click(await screen.findByRole('button', { name: 'Accept invitation' }));
    await screen.findByRole('alert');
    await waitFor(() => expect(screen.getByRole('button', { name: 'Accept invitation' })).toBeEnabled());
  });
});
