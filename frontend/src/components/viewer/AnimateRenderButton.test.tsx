import '@testing-library/jest-dom/vitest';
import { act, cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { AnimateRenderButton } from './AnimateRenderButton';
import { renderAnimationApi, videoRenderApi } from '@/services/api';

vi.mock('@/services/api', () => ({
  renderAnimationApi: { preflight: vi.fn(), generate: vi.fn(), recover: vi.fn() },
  videoRenderApi: { list: vi.fn() },
  authApi: { me: vi.fn().mockResolvedValue({ id: 'student' }) },
  getApiErrorMessage: (error: unknown, fallback: string) => error instanceof Error ? error.message : fallback,
  resolveApiFileUrl: (url: string) => `${url}?asset_ticket=test`,
}));
vi.mock('@/store', () => ({ useAuthStore: { getState: () => ({ user: { id: 'student' }, setUser: vi.fn() }) } }));

const still = { id: 'finished-render', image_url: '/api/v1/files/projects/p/renders/finished.png',
  prompt: 'Approved finish', created_at: '2026-10-06', outcome: 'accepted' };
const check = { ready: true, provider_called: false, source_render_id: still.id, width: 1600, height: 900,
  duration_seconds: 5, generate_audio: false, estimated_cost_usd: .56, credit_cost: 50,
  model: 'fal-ai/kling-video/v3/pro/image-to-video', attempts_remaining: 3 } as const;
const queued = { id: 'clip', request_id: 'saved-request', provider: 'kling' as const,
  mode: 'saved_render_animation' as const, source_render_id: still.id, recoverable: true,
  status: 'queued', style: 'architectural_film', camera_motion: 'slow_push_in', duration_seconds: 5,
  created_at: '2026-10-06', estimated_cost_usd: .56, interaction_id: 'remote-id' };
const complete = { ...queued, status: 'complete', recoverable: false,
  video_url: '/api/v1/files/projects/p/video-render/clip/kling-animation.mp4' };

beforeEach(() => {
  vi.clearAllMocks();
  localStorage.clear();
  vi.mocked(renderAnimationApi.preflight).mockResolvedValue(check);
  vi.mocked(videoRenderApi.list).mockResolvedValue({ attempts: [] });
  vi.mocked(renderAnimationApi.generate).mockResolvedValue(queued);
  vi.mocked(renderAnimationApi.recover).mockResolvedValue(complete);
});
afterEach(() => { cleanup(); vi.useRealTimers(); });

async function open(onSaved = vi.fn()) {
  render(<AnimateRenderButton projectId="p" render={still} onSaved={onSaved} />);
  fireEvent.click(screen.getByRole('button', { name: 'Animate this render' }));
  await waitFor(() => expect(screen.getByRole('button', { name: 'Create 5-second clip' })).toBeEnabled());
  return onSaved;
}

describe('saved finished render animation', () => {
  it('shows the full saved source and submits IDs only, once on a double click', async () => {
    await open();
    expect(screen.getByText('1600 × 900 source')).toBeInTheDocument();
    expect(screen.getByText('50 credits · provider estimate US$0.56')).toBeInTheDocument();
    const image = screen.getByAltText('Selected finished architectural render');
    expect(image.getAttribute('src')).toBe(`${still.image_url}?asset_ticket=test`);
    expect(image.getAttribute('src')).not.toContain('thumbnail');
    const button = screen.getByRole('button', { name: 'Create 5-second clip' });
    fireEvent.click(button); fireEvent.click(button);
    await screen.findByText('Animation queued');
    expect(renderAnimationApi.generate).toHaveBeenCalledTimes(1);
    expect(renderAnimationApi.generate).toHaveBeenCalledWith({ project_id: 'p', source_render_id: still.id,
      request_id: expect.any(String), confirm_paid_submission: true });
  });

  it('recovers the previous job, plays and downloads without submitting a new generation', async () => {
    vi.mocked(videoRenderApi.list).mockResolvedValue({ attempts: [queued] });
    const onSaved = vi.fn();
    render(<AnimateRenderButton projectId="p" render={still} onSaved={onSaved} />);
    fireEvent.click(screen.getByRole('button', { name: 'Animate this render' }));
    fireEvent.click(await screen.findByRole('button', { name: 'Check saved request' }));
    expect(await screen.findByText('Your clip is ready')).toBeInTheDocument();
    expect(renderAnimationApi.recover).toHaveBeenCalledWith('p', 'clip');
    expect(renderAnimationApi.generate).not.toHaveBeenCalled();
    expect(document.querySelector('video')?.getAttribute('src')).toContain('kling-animation.mp4');
    expect(screen.getByRole('link', { name: 'Download MP4' }).getAttribute('href')).toContain('download=true');
    expect(onSaved).toHaveBeenCalledWith(complete);
  });

  it('stops polling after the dialog closes and restores keyboard focus', async () => {
    await open();
    fireEvent.click(screen.getByRole('button', { name: 'Create 5-second clip' }));
    await screen.findByText('Animation queued');
    fireEvent.click(screen.getByRole('button', { name: 'Close animation' }));
    vi.useFakeTimers();
    await act(async () => { await vi.advanceTimersByTimeAsync(15000); });
    expect(renderAnimationApi.recover).not.toHaveBeenCalled();
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
  });

  it('never offers animation for an authoritative viewport fallback', () => {
    render(<AnimateRenderButton projectId="p" render={{ ...still, presentation_strategy: 'authoritative_source' }} />);
    expect(screen.queryByRole('button', { name: 'Animate this render' })).not.toBeInTheDocument();
    expect(renderAnimationApi.preflight).not.toHaveBeenCalled();
  });

  it('keeps generation disabled if saved history could not be checked', async () => {
    vi.mocked(videoRenderApi.list).mockRejectedValue(new Error('network unavailable'));
    render(<AnimateRenderButton projectId="p" render={still} />);
    fireEvent.click(screen.getByRole('button', { name: 'Animate this render' }));
    expect(await screen.findByRole('alert')).toHaveTextContent('Could not check existing animation jobs');
    expect(screen.getByRole('button', { name: 'Create 5-second clip' })).toBeDisabled();
    expect(renderAnimationApi.generate).not.toHaveBeenCalled();
  });

  it('retains the request key on a lost response and finds the existing paid receipt', async () => {
    await open();
    vi.mocked(renderAnimationApi.generate).mockRejectedValue(new Error('response interrupted'));
    vi.mocked(videoRenderApi.list).mockResolvedValue({ attempts: [queued] });
    fireEvent.click(screen.getByRole('button', { name: 'Create 5-second clip' }));
    expect(await screen.findByRole('button', { name: 'Check saved request' })).toBeInTheDocument();
    expect(localStorage.getItem('cityprompt.animation.v1:p:finished-render')).toBeTruthy();
    expect(renderAnimationApi.generate).toHaveBeenCalledTimes(1);
    fireEvent.click(screen.getByRole('button', { name: 'Check saved request' }));
    await screen.findByText('Your clip is ready');
    expect(localStorage.getItem('cityprompt.animation.v1:p:finished-render')).toBeNull();
    expect(renderAnimationApi.generate).toHaveBeenCalledTimes(1);
  });
});
