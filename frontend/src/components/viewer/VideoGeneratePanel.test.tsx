import '@testing-library/jest-dom/vitest';
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

const mocks = vi.hoisted(() => ({
  list: vi.fn(),
  preflight: vi.fn(),
  generate: vi.fn(),
  backfillFidelity: vi.fn(),
  setBenchmark: vi.fn(),
}));
vi.mock('@/services/api', () => ({
  videoRenderApi: {
    list: mocks.list,
    preflight: mocks.preflight,
    generate: mocks.generate,
    backfillFidelity: mocks.backfillFidelity,
    setBenchmark: mocks.setBenchmark,
  },
  resolveApiFileUrl: (url: string) => url,
  getApiErrorMessage: (_error: unknown, fallback: string) => fallback,
}));
vi.mock('react-hot-toast', () => ({ default: Object.assign(vi.fn(), { error: vi.fn(), success: vi.fn() }) }));
vi.mock('@/features/community3d/community3d', () => ({
  getCommunity3DCaptureClaims: () => [{ zone_id: 'zone-1', source_hash: 'src', representation_hash: 'rep' }],
}));
vi.mock('./globe/residualLandscape', () => ({ getCurrentResidualLandscapeClaim: () => null }));
vi.mock('@/features/pickPlace/catalogue', () => ({ isCatalogueOnlyScene: () => false, CATALOGUE_UPDATE_GUIDANCE: 'update' }));
vi.mock('./globe/useDirect3DRender', () => ({ useDirect3DRender: () => ({ renderDirect3D: vi.fn() }) }));

import { VideoGeneratePanel } from './VideoGeneratePanel';

function renderPanel() {
  return render(
    <VideoGeneratePanel
      projectId="project-1"
      canvas={null}
      siteZones={[]}
      buildings={[]}
      onClose={vi.fn()}
    />,
  );
}

describe('VideoGeneratePanel look sheet', () => {
  afterEach(cleanup);
  beforeEach(() => {
    vi.clearAllMocks();
    mocks.list.mockResolvedValue({
      attempts: [],
      attempts_used: 0,
      attempts_remaining: 49,
      max_attempts: 49,
      provider_usage: {},
    });
  });

  it('defaults to finishing the preview and hides the legacy modes behind Advanced', async () => {
    renderPanel();
    await waitFor(() => expect(mocks.list).toHaveBeenCalled());
    expect(screen.getByRole('button', { name: /Finish my preview/ })).toHaveAttribute('aria-pressed', 'true');
    expect(screen.queryByRole('button', { name: /Route keyframes/ })).not.toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /Single frame/ })).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Advanced modes' }));
    expect(screen.getByRole('button', { name: /Route keyframes/ })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Single frame/ })).toBeInTheDocument();
  });

  it('offers the look sheet instead of scene-lock prose for look-sheet engines', async () => {
    renderPanel();
    await waitFor(() => expect(mocks.list).toHaveBeenCalled());
    expect(screen.getByText('Look')).toBeInTheDocument();
    const photoreal = screen.getByRole('button', { name: /Photo Realistic/ });
    expect(photoreal).toHaveAttribute('aria-pressed', 'true');
    fireEvent.click(screen.getByRole('button', { name: /^Night/ }));
    expect(screen.getByRole('button', { name: /^Night/ })).toHaveAttribute('aria-pressed', 'true');
    expect(photoreal).toHaveAttribute('aria-pressed', 'false');
    const note = screen.getByLabelText(/Note to the video engine/) as HTMLTextAreaElement;
    expect(note.maxLength).toBe(240);
    expect(screen.queryByText(/source-fidelity animation/)).not.toBeInTheDocument();
  });

  it('lists the three look-sheet engines and keeps Structure Lock on the preview video', async () => {
    renderPanel();
    await waitFor(() => expect(mocks.list).toHaveBeenCalled());
    expect(screen.getByRole('button', { name: /Structure Lock/ })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Grok Video/ })).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Advanced modes' }));
    fireEvent.click(screen.getByRole('button', { name: /Structure Lock/ }));
    expect(screen.getByText(/Depth-guided finish/)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Finish my preview/ })).toHaveAttribute('aria-pressed', 'true');
    expect(screen.getByRole('button', { name: /Route keyframes/ })).toBeDisabled();
    fireEvent.click(screen.getByRole('button', { name: /Seedance Mini/ }));
    expect(screen.getByText('Scene lock')).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /Photo Realistic/ })).not.toBeInTheDocument();
  });

  it('offers the anchor frame only to engines that take a reference image', async () => {
    renderPanel();
    await waitFor(() => expect(mocks.list).toHaveBeenCalled());
    expect(screen.getByText('Anchor frame')).toBeInTheDocument();
    const renderAnchor = screen.getByRole('button', { name: 'Render anchor frame' });
    expect(renderAnchor).toBeDisabled(); // no captured source frame or route yet
    expect(screen.getByText(/same image engine as your stills/)).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: /Grok Video/ }));
    expect(screen.queryByText('Anchor frame')).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: /Structure Lock/ }));
    expect(screen.getByText('Anchor frame')).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: /Gemini Omni/ }));
    fireEvent.click(screen.getByRole('button', { name: 'Advanced modes' }));
    fireEvent.click(screen.getByRole('button', { name: /Single frame/ }));
    expect(screen.queryByText('Anchor frame')).not.toBeInTheDocument();
  });
});
