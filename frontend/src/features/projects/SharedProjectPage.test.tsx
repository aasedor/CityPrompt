import '@testing-library/jest-dom/vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { api, resolveApiFileUrl, sharesApi } from '@/services/api';
import { SharedProjectPage } from './SharedProjectPage';

vi.mock('@/services/api', () => ({
  api: { get: vi.fn(), post: vi.fn() }, sharesApi: { getSharedProject: vi.fn() },
  getApiErrorMessage: (_: unknown, fallback: string) => fallback,
  resolveApiFileUrl: vi.fn((url: string, options: { shareToken: string }) => url + '?share_token=' + options.shareToken),
}));
function setup() {
  return render(<QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}><MemoryRouter initialEntries={['/shared/public-token']}><Routes><Route path="/shared/:token" element={<SharedProjectPage />} /></Routes></MemoryRouter></QueryClientProvider>);
}
describe('Public presentation', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(sharesApi.getSharedProject).mockResolvedValue({ id: 'p1', name: 'A better community', buildings: [] } as never);
    vi.mocked(api.get).mockImplementation(async (url) => {
      if (String(url).endsWith('/zones')) return { data: [{ id: 'park', name: 'Central park', zone_type: 'green_space', coordinates: [[-114, 51], [-113.999, 51], [-113.999, 51.001]] }] };
      if (String(url).endsWith('/renders')) return { data: [{ id: 'image', image_url: '/api/v1/files/p1/image.png', created_at: '2026-09-04T12:00:00Z' }] };
      return { data: { attempts: [{ id: 'video', status: 'complete', video_url: '/api/v1/files/p1/video.mp4', created_at: '2026-09-04T12:00:00Z' }] } };
    });
  });
  it('shows actual stored outlines and saved media while preserving the public token', async () => {
    setup();
    await screen.findByRole('img', { name: /Community plan, north up/ });
    fireEvent.change(screen.getByLabelText('Inspect a drawing'), { target: { value: 'park' } });
    expect(screen.getByRole('status')).toHaveTextContent('Central park');
    expect(await screen.findByRole('img', { name: /presentation image 1/ })).toHaveAttribute('src', '/api/v1/files/p1/image.png?share_token=public-token');
    expect(screen.getByLabelText('A better community — video 1')).toHaveAttribute('src', '/api/v1/files/p1/video.mp4?share_token=public-token');
    expect(resolveApiFileUrl).toHaveBeenCalledWith('/api/v1/files/p1/image.png', { projectId: 'p1', shareToken: 'public-token' });
    expect(api.get).toHaveBeenCalledTimes(3);
    for (const call of vi.mocked(api.get).mock.calls) expect(call[1]).toEqual({ params: { share_token: 'public-token' } });
    expect(api.post).not.toHaveBeenCalled();
    expect(screen.queryByRole('link', { name: 'Open 3D Viewer' })).not.toBeInTheDocument();
  });
  it('reports a revoked link and never requests project assets', async () => {
    vi.mocked(sharesApi.getSharedProject).mockRejectedValue(new Error('revoked'));
    setup();
    await screen.findByRole('heading', { name: 'Presentation unavailable' });
    expect(api.get).not.toHaveBeenCalled();
  });
  it('keeps a failed image readable as an error instead of a broken presentation', async () => {
    setup();
    fireEvent.error(await screen.findByRole('img', { name: /presentation image 1/ }));
    await waitFor(() => expect(screen.getByText(/This saved image is unavailable/)).toBeInTheDocument());
  });
});
