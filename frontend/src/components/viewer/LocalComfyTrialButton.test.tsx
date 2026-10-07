import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import '@testing-library/jest-dom/vitest';
import { LocalComfyTrialButton } from './LocalComfyTrialButton';
import { comfyTrialsApi, type ComfyJob, type ComfyPreset } from '@/services/comfyTrials';
import type { SavedRender } from '@/types';

vi.mock('@/services/comfyTrials', () => ({ comfyTrialsApi: { presets: vi.fn(), list: vi.fn(), generate: vi.fn(), recover: vi.fn(), resolveMissing: vi.fn() } }));
vi.mock('@/services/api', () => ({ resolveApiFileUrl: (url: string) => `${url}?asset_ticket=test`, getApiErrorMessage: (_: unknown, fallback: string) => fallback }));
const still = { id: 'saved-image', image_url: '/api/v1/files/projects/p/renders/saved-image.png', prompt: 'Finished image', created_at: '2026-10-06' } as SavedRender;
const presets: ComfyPreset[] = [
  { id: 'flux-klein', label: 'FLUX.2 Klein 4B · image', kind: 'image', available: true, message: 'Ready', default_prompt: 'Refine this view.', max_edge: 768, steps: 4, duration_seconds: null },
  { id: 'wan-video', label: 'Wan 2.2 5B · short video', kind: 'video', available: true, message: 'Ready', default_prompt: 'Very slow push-in.', max_edge: 640, steps: 20, duration_seconds: 49 / 24 },
];
const queued: ComfyJob = { id: 'gpu-job', request_id: 'request', source_render_id: still.id, preset: 'flux-klein', kind: 'image', status: 'queued', prompt: 'Refine this view.', created_at: '2026-10-06', generation_settings: { width: 768, height: 448, steps: 4, seed: 42 }, error: null, result: null };
beforeEach(() => {
  vi.clearAllMocks(); localStorage.clear();
  vi.mocked(comfyTrialsApi.presets).mockResolvedValue({ presets, credit_cost: 0 });
  vi.mocked(comfyTrialsApi.list).mockResolvedValue({ jobs: [] });
  vi.mocked(comfyTrialsApi.generate).mockResolvedValue(queued);
  vi.mocked(comfyTrialsApi.recover).mockResolvedValue({ ...queued, status: 'complete', result: { ...still, id: 'result', image_url: '/api/v1/files/projects/p/renders/result.png' } });
});
afterEach(cleanup);
async function open(source = still) {
  render(<LocalComfyTrialButton projectId="p" render={source} />);
  fireEvent.click(screen.getByRole('button', { name: 'Local model trials' }));
  await screen.findByLabelText('Model');
}

describe('local desktop render trials', () => {
  it('uses a full saved image and submits IDs only, once on double click', async () => {
    await open();
    expect(screen.getByAltText('Full saved source for local model trial')).toHaveAttribute('src', `${still.image_url}?asset_ticket=test`);
    fireEvent.change(screen.getByLabelText('Prompt'), { target: { value: 'Calm daylight.' } });
    const run = screen.getByRole('button', { name: 'Run local trial' });
    fireEvent.click(run); fireEvent.click(run);
    await screen.findByText('Local trial: queued');
    expect(comfyTrialsApi.generate).toHaveBeenCalledTimes(1);
    expect(comfyTrialsApi.generate).toHaveBeenCalledWith({ project_id: 'p', source_render_id: still.id, request_id: expect.any(String), preset: 'flux-klein', prompt: 'Calm daylight.' });
  });

  it('recovers a saved job without resubmission and displays its saved result', async () => {
    vi.mocked(comfyTrialsApi.list).mockResolvedValue({ jobs: [queued] });
    await open();
    fireEvent.click(screen.getByRole('button', { name: 'Check saved job' }));
    await screen.findByAltText('Local model result');
    expect(screen.getByRole('link', { name: 'Download result' })).toHaveAttribute('href', '/api/v1/files/projects/p/renders/result.png?asset_ticket=test');
    expect(comfyTrialsApi.generate).not.toHaveBeenCalled();
    expect(comfyTrialsApi.recover).toHaveBeenCalledWith('p', 'gpu-job');
  });

  it('does not run missing models', async () => {
    vi.mocked(comfyTrialsApi.presets).mockResolvedValue({ presets: presets.map(p => ({ ...p, available: false, message: 'Missing model files' })), credit_cost: 0 });
    await open();
    expect(screen.getByRole('button', { name: 'Run local trial' })).toBeDisabled();
    expect(screen.getByText('Missing model files')).toBeInTheDocument();
  });

  it('allows finishing a 3D source and hides new local video trials', async () => {
    await open({ ...still, presentation_strategy: 'authoritative_source' });
    expect(screen.getByRole('button', { name: 'Run local trial' })).toBeEnabled();
    expect(screen.queryByRole('option', { name: /Wan/ })).not.toBeInTheDocument();
  });

  it('preserves a pending request ID after a lost receipt', async () => {
    vi.mocked(comfyTrialsApi.generate).mockRejectedValue(new Error('network'));
    await open();
    fireEvent.click(screen.getByRole('button', { name: 'Run local trial' }));
    await screen.findByRole('alert');
    const submitted = vi.mocked(comfyTrialsApi.generate).mock.calls[0][0];
    expect(localStorage.getItem(`cityprompt.comfy.v1:p:${still.id}`)).toContain(submitted.request_id);
    fireEvent.click(screen.getByRole('button', { name: 'Close local trials' }));
    vi.mocked(comfyTrialsApi.list).mockResolvedValue({ jobs: [{ ...queued, request_id: submitted.request_id }] });
    fireEvent.click(screen.getByRole('button', { name: 'Local model trials' }));
    await waitFor(() => expect(screen.getByText('Local trial: queued')).toBeInTheDocument());
    expect(comfyTrialsApi.generate).toHaveBeenCalledTimes(1);
  });

  it('resolves a missing job explicitly without automatically generating a replacement', async () => {
    vi.mocked(comfyTrialsApi.list).mockResolvedValue({ jobs: [{ ...queued, status: 'submission_unknown', error: 'ComfyUI restarted.' }] });
    vi.mocked(comfyTrialsApi.resolveMissing).mockResolvedValue({ ...queued, status: 'failed', error: 'Missing job resolved.' });
    await open();
    fireEvent.click(screen.getByRole('button', { name: 'Mark missing job as failed' }));
    await screen.findByText('Local trial: failed');
    expect(comfyTrialsApi.generate).not.toHaveBeenCalled();
    expect(screen.getByRole('button', { name: 'Set up another trial' })).toBeEnabled();
  });
});
