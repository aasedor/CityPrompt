import '@testing-library/jest-dom/vitest';
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

const mocks = vi.hoisted(() => ({ direct: vi.fn(), classic: vi.fn(), save: vi.fn() }));
vi.mock('@/store', () => ({ useViewerStore: () => ({ streetViewPegman: { position: [-114, 51], angle: 0 }, setStreetViewAngle: vi.fn(), setStreetViewPosition: vi.fn(), setStreetViewActive: vi.fn() }) }));
vi.mock('./useStreetViewRender', () => ({ useStreetViewRender: () => ({ generateStreetView: mocks.classic }) }));
vi.mock('./globe/useDirect3DRender', () => ({ DIRECT_3D_ALLOWED_STYLES: new Set(['photorealistic']), useDirect3DRender: () => ({ renderDirect3D: mocks.direct }) }));
vi.mock('./globe/direct3dArchetypeReferences', () => ({ collectDirect3DArchetypeReferences: async () => [] }));
vi.mock('@/features/community3d/community3d', () => ({ getCommunity3DCaptureClaims: () => [{ zone_id: 'zone-1' }] }));
vi.mock('./globe/residualLandscape', () => ({ getCurrentResidualLandscapeClaim: () => null }));
vi.mock('@/utils/renderPersistence', () => ({ getRenderImageKey: (r: {imageUrl: string}) => r.imageUrl, saveRenderedImage: mocks.save }));
vi.mock('@/services/api', () => ({ resolveApiFileUrl: (u: string) => u, getApiErrorMessage: () => 'failed' }));
vi.mock('./RenderEditModal', () => ({ RenderEditModal: () => null }));
vi.mock('react-hot-toast', () => ({ default: Object.assign(vi.fn(), { error: vi.fn(), success: vi.fn() }) }));

import { StreetViewPanel } from './StreetViewPanel';

describe('student street render', () => {
  afterEach(cleanup);
  beforeEach(() => {
    vi.clearAllMocks();
    mocks.direct.mockResolvedValue({
      outcome: 'review_required',
      render: { imageUrl: 'data:image/png;base64,source', prompt: 'finish', model: 'gpt-image-2', providerLabel: 'Original 3D view', savedRender: { id: 'source-1' } },
      providerOriginalRender: { id: 'attempt-1', image_url: '/attempt.png', prompt: 'finish' },
    });
  });

  it('defaults a globe scene to one Direct render and exposes both saved results without a duplicate save', async () => {
    const saved = vi.fn();
    render(<StreetViewPanel siteZones={[]} projectId="project-1" globeCapture={vi.fn().mockResolvedValue({ kind: 'model3d', direct3d: {} })} onRenderSaved={saved} />);
    expect(screen.getByRole('button', { name: '✓ Direct 3D · 1 image' })).toBeInTheDocument();
    expect(screen.queryByRole('checkbox')).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Render' }));
    await waitFor(() => expect(saved).toHaveBeenCalledTimes(2));
    expect(mocks.direct).toHaveBeenCalledTimes(1);
    expect(mocks.classic).not.toHaveBeenCalled();
    expect(mocks.direct.mock.calls[0][1].customPrompt).toContain('Do not add people. Do not add vehicles.');
    expect(screen.getByAltText('AI attempt · unverified render')).toBeInTheDocument();
    expect(mocks.save).not.toHaveBeenCalled();
  });

  it('forwards explicitly selected street activity to the Direct request', async () => {
    render(<StreetViewPanel siteZones={[]} projectId="project-1" globeCapture={vi.fn().mockResolvedValue({ kind: 'model3d', direct3d: {} })} />);
    fireEvent.click(screen.getByRole('button', { name: 'Add People' }));
    fireEvent.click(screen.getByRole('button', { name: 'Add Vehicles' }));
    fireEvent.click(screen.getByRole('button', { name: 'Render' }));
    await waitFor(() => expect(mocks.direct).toHaveBeenCalledTimes(1));
    expect(mocks.direct.mock.calls[0][1].customPrompt).toContain('Include a few pedestrians on existing walking surfaces. Include a few vehicles on existing carriageways only.');
  });

  it('retains the classic path for a map without a 3D capture', () => {
    render(<StreetViewPanel siteZones={[]} projectId="project-1" />);
    expect(screen.getByRole('checkbox')).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: '✓ Direct 3D · 1 image' })).not.toBeInTheDocument();
  });

  it('previews the actual street capture without calling an image provider', async () => {
    const capture = vi.fn().mockResolvedValue({ imageBase64: 'data:image/png;base64,preview' });
    render(<StreetViewPanel siteZones={[]} projectId="project-1" globeCapture={capture} />);
    fireEvent.click(screen.getByRole('button', { name: 'Preview 3D view' }));
    expect(await screen.findByAltText('Street view 3D preview')).toHaveAttribute('src', 'data:image/png;base64,preview');
    expect(capture).toHaveBeenCalledTimes(1);
    expect(mocks.direct).not.toHaveBeenCalled();
    expect(mocks.classic).not.toHaveBeenCalled();
  });
});
