import '@testing-library/jest-dom/vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { sharesApi } from '@/services/api';
import { ShareModal } from './ShareModal';

vi.mock('@/services/api', () => ({ sharesApi: { list: vi.fn(), share: vi.fn(), revoke: vi.fn(), createPublicLink: vi.fn(), revokePublicLink: vi.fn() }, getApiErrorMessage: (_: unknown, fallback: string) => fallback }));
const pending = { id: 'share-1', project_id: 'p1', email: 'team@university.ca', permission: 'editor', is_public_link: false, invite_token: 'private-token', created_at: '2026-09-04' };
function setup() {
  return render(<QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false }, mutations: { retry: false } } })}><ShareModal projectId="p1" projectName="Team community" onClose={vi.fn()} /></QueryClientProvider>);
}
describe('Share project', () => {
  beforeEach(() => { vi.clearAllMocks(); vi.mocked(sharesApi.list).mockResolvedValue([]); });
  it('creates a pending invitation and presents the acceptance link, without claiming email was sent', async () => {
    vi.mocked(sharesApi.share).mockResolvedValue(pending);
    setup();
    await waitFor(() => expect(screen.getByLabelText('Teammate email')).toBeEnabled());
    fireEvent.change(screen.getByLabelText('Teammate email'), { target: { value: 'team@university.ca' } });
    fireEvent.change(screen.getByLabelText('Access'), { target: { value: 'editor' } });
    vi.mocked(sharesApi.list).mockResolvedValue([pending]);
    fireEvent.click(screen.getByRole('button', { name: 'Create invitation' }));
    expect(await screen.findByText('Can edit · Pending acceptance')).toBeInTheDocument();
    expect(screen.getByLabelText('Invitation link for team@university.ca')).toHaveValue(window.location.origin + '/invite/private-token');
    expect(screen.getByRole('status')).toHaveTextContent('Copy its invitation link');
    expect(sharesApi.share).toHaveBeenCalledWith('p1', 'team@university.ca', 'editor');
  });
  it('copies an invitation and keeps a manual-copy fallback when clipboard access is unavailable', async () => {
    vi.mocked(sharesApi.list).mockResolvedValue([pending]);
    const writeText = vi.fn().mockRejectedValue(new Error('denied'));
    Object.defineProperty(navigator, 'clipboard', { configurable: true, value: { writeText } });
    setup();
    fireEvent.click(await screen.findByRole('button', { name: 'Copy invitation' }));
    expect(await screen.findByRole('alert')).toHaveTextContent('copy it manually');
    expect(writeText).toHaveBeenCalledWith(window.location.origin + '/invite/private-token');
    expect(screen.getByLabelText('Invitation link for team@university.ca')).toBeVisible();
  });
});
