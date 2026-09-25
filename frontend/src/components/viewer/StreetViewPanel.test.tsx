import '@testing-library/jest-dom/vitest';
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

const mocks = vi.hoisted(() => ({ direct: vi.fn(), classic: vi.fn(), save: vi.fn(), imageModels: vi.fn(), references: vi.fn(), claims: vi.fn() }));
vi.mock('@/store', () => ({ useViewerStore: () => ({ streetViewPegman: { position: [-114, 51], angle: 0 }, setStreetViewAngle: vi.fn(), setStreetViewPosition: vi.fn(), setStreetViewActive: vi.fn() }) }));
vi.mock('./useStreetViewRender', () => ({ useStreetViewRender: () => ({ generateStreetView: mocks.classic }) }));
vi.mock('./globe/useDirect3DRender', async (importOriginal) => ({ ...await importOriginal<typeof import('./globe/useDirect3DRender')>(), useDirect3DRender: () => ({ renderDirect3D: mocks.direct }) }));
vi.mock('./globe/direct3dArchetypeReferences', () => ({ collectDirect3DArchetypeReferences: mocks.references }));
vi.mock('@/features/community3d/community3d', () => ({ getCommunity3DCaptureClaims: mocks.claims }));
vi.mock('./globe/residualLandscape', () => ({ getCurrentResidualLandscapeClaim: () => null }));
vi.mock('@/utils/renderPersistence', () => ({ getRenderImageKey: (r: {imageUrl: string}) => r.imageUrl, saveRenderedImage: mocks.save }));
vi.mock('@/services/api', () => ({ rendersApi: { imageModels: mocks.imageModels }, resolveApiFileUrl: (u: string) => u, getApiErrorMessage: () => 'failed' }));
vi.mock('./RenderEditModal', () => ({ RenderEditModal: () => null }));
vi.mock('react-hot-toast', () => ({ default: Object.assign(vi.fn(), { error: vi.fn(), success: vi.fn() }) }));

import { StreetViewPanel } from './StreetViewPanel';

describe('student street render', () => {
  const pairAccess = {
    default_model: 'gpt-image-2.5-flare',
    models: [
      { id: 'gpt-image-2.5-flare', available: true },
      { id: 'gpt-image-2.5-sunburst', available: true },
      { id: 'gpt-image-2', available: true },
    ],
  };
  afterEach(cleanup);
  beforeEach(() => {
    mocks.imageModels.mockResolvedValue({ default_model: 'gpt-image-2', models: [{ id: 'gpt-image-2', available: true }] });
    vi.clearAllMocks();
    mocks.claims.mockReturnValue([{ zone_id: 'zone-1' }]);
    mocks.references.mockResolvedValue([]);
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
    expect(mocks.references).not.toHaveBeenCalled();
    expect(mocks.classic).not.toHaveBeenCalled();
    expect(mocks.direct.mock.calls[0][1].customPrompt).toContain('Do not add people. Do not add vehicles.');
    expect(mocks.direct.mock.calls[0][1].customPrompt).not.toContain('Scale people');
    expect(screen.getByAltText('AI render render')).toBeInTheDocument();
    expect(mocks.save).not.toHaveBeenCalled();
  });

  it('forwards explicitly selected street activity to the Direct request', async () => {
    render(<StreetViewPanel siteZones={[]} projectId="project-1" globeCapture={vi.fn().mockResolvedValue({ kind: 'model3d', direct3d: {} })} />);
    fireEvent.click(screen.getByRole('button', { name: 'Add People' }));
    fireEvent.click(screen.getByRole('button', { name: 'Add Vehicles' }));
    fireEvent.click(screen.getByRole('button', { name: 'Render' }));
    await waitFor(() => expect(mocks.direct).toHaveBeenCalledTimes(1));
    expect(mocks.direct.mock.calls[0][1].customPrompt).toContain('Include a few pedestrians on existing walking surfaces. Include a few vehicles on existing carriageways only.');
    expect(mocks.direct.mock.calls[0][1].customPrompt).toContain('Scale people using nearby doors and storeys');
    expect(mocks.direct.mock.calls[0][1].customPrompt).toContain('Respect occlusion');
    expect(mocks.direct.mock.calls[0][1].customPrompt).toContain('feet visible when the captured framing allows');
  });

  it('sends the visible custom prompt with a Direct 3D street render', async () => {
    render(<StreetViewPanel siteZones={[]} projectId="project-1" globeCapture={vi.fn().mockResolvedValue({ kind: 'model3d', direct3d: {} })} />);
    fireEvent.change(screen.getByRole('textbox', { name: /custom prompt/i }), { target: { value: 'Soft morning light on the planted courtyard.' } });
    fireEvent.click(screen.getByRole('button', { name: 'Render' }));
    await waitFor(() => expect(mocks.direct).toHaveBeenCalledTimes(1));
    expect(mocks.direct.mock.calls[0][1].customPrompt).toContain('Soft morning light on the planted courtyard.');
    expect(mocks.direct.mock.calls[0][1].customPrompt).toContain('Keep all buildings, facilities, paths and streets in their captured positions.');
  });

  it('sends the custom prompt through the classic street renderer', async () => {
    mocks.classic.mockResolvedValue({ imageUrl: 'data:image/png;base64,street', prompt: 'street' });
    render(<StreetViewPanel siteZones={[]} projectId="project-1" />);
    fireEvent.change(screen.getByRole('textbox', { name: /custom prompt/i }), { target: { value: 'Rainy evening with warm shop windows.' } });
    fireEvent.click(screen.getByRole('button', { name: 'Render' }));
    await waitFor(() => expect(mocks.classic).toHaveBeenCalledTimes(3));
    expect(mocks.classic.mock.calls.every(([, , , options]) => options.customPrompt === 'Rainy evening with warm shop windows.')).toBe(true);
  });

  it('shows the AI illustration first and keeps the source comparison without saving it twice', async () => {
    const original = { id: 'attempt-1', image_url: '/attempt.png', prompt: 'finish' };
    mocks.direct.mockResolvedValue({
      outcome: 'review_required', sourceImageUrl: '/source.png',
      render: { imageUrl: '/attempt.png', prompt: 'finish', providerLabel: 'AI render', savedRender: original },
      providerOriginalRender: original,
    });
    const saved = vi.fn();
    render(<StreetViewPanel siteZones={[]} projectId="project-1" globeCapture={vi.fn().mockResolvedValue({ kind: 'model3d', direct3d: {} })} onRenderSaved={saved} />);
    fireEvent.click(screen.getByRole('button', { name: 'Render' }));
    await waitFor(() => expect(saved).toHaveBeenCalledTimes(1));
    expect(screen.getAllByAltText('AI render render')[0]).toHaveAttribute('src', '/attempt.png');
    expect(screen.getByAltText('Original 3D view render')).toHaveAttribute('src', '/source.png');
    expect(mocks.save).not.toHaveBeenCalled();
  });

  it('compares all three models from the identical street capture and saves each', async () => {
    mocks.imageModels.mockResolvedValue(pairAccess);
    const bundle = { beautyImageBase64: 'same camera' };
    const capture = vi.fn().mockResolvedValue({ kind: 'model3d', direct3d: bundle });
    const saved = vi.fn();
    for (const engine of ['Image 2', 'Flare', 'Sunburst']) mocks.direct.mockResolvedValueOnce({
      outcome: 'review_required', sourceImageUrl: '/source.png',
      render: { imageUrl: `/${engine}.png`, prompt: 'finish', providerLabel: engine, savedRender: { id: engine } },
    });
    render(<StreetViewPanel siteZones={[]} projectId="project-1" globeCapture={capture} onRenderSaved={saved} />);
    await waitFor(() => expect(screen.getByRole('combobox', { name: 'Image engine' })).toHaveValue('gpt-image-2.5-flare'));
    fireEvent.change(screen.getByRole('combobox', { name: 'Image engine' }), { target: { value: 'compare-all-three' } });
    fireEvent.click(screen.getByRole('button', { name: 'Render' }));
    await waitFor(() => expect(saved).toHaveBeenCalledTimes(3));
    expect(capture).toHaveBeenCalledTimes(1);
    expect(mocks.direct.mock.calls.map(([input, options]) => [input, options.model])).toEqual([
      [bundle, 'gpt-image-2'], [bundle, 'gpt-image-2.5-flare'], [bundle, 'gpt-image-2.5-sunburst'],
    ]);
    expect(mocks.direct.mock.calls[0][0]).toBe(mocks.direct.mock.calls[1][0]);
    expect(screen.getAllByAltText('Flare render').length).toBeGreaterThan(0);
    expect(screen.getAllByAltText('Sunburst render').length).toBeGreaterThan(0);
    expect(mocks.save).not.toHaveBeenCalled();
  });

  it('keeps the Image 2 result visible if Flare fails', async () => {
    mocks.imageModels.mockResolvedValue(pairAccess);
    mocks.direct.mockResolvedValueOnce({
      outcome: 'review_required', sourceImageUrl: '/source.png',
      render: { imageUrl: '/Image2.png', prompt: 'finish', providerLabel: 'Image 2', savedRender: { id: 'Image2' } },
    }).mockRejectedValueOnce(new Error('Flare unavailable'));
    const saved = vi.fn();
    render(<StreetViewPanel siteZones={[]} projectId="project-1" globeCapture={vi.fn().mockResolvedValue({ kind: 'model3d', direct3d: {} })} onRenderSaved={saved} />);
    await waitFor(() => expect(screen.getByRole('combobox', { name: 'Image engine' })).toHaveValue('gpt-image-2.5-flare'));
    fireEvent.change(screen.getByRole('combobox', { name: 'Image engine' }), { target: { value: 'compare-all-three' } });
    fireEvent.click(screen.getByRole('button', { name: 'Render' }));
    await waitFor(() => expect(mocks.direct).toHaveBeenCalledTimes(2));
    await waitFor(() => expect(screen.getByRole('button', { name: 'Re-render Previews' })).not.toBeDisabled());
    expect(saved).toHaveBeenCalledTimes(1);
    expect(screen.getAllByAltText('Image 2 render').length).toBeGreaterThan(0);
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

  it('offers the 3D build controls before a paid capture when scene claims are missing', () => {
    mocks.claims.mockReturnValue(null);
    const capture = vi.fn();
    const prepare = vi.fn();
    render(<StreetViewPanel siteZones={[]} projectId="project-1" globeCapture={capture} onPrepareCommunity3D={prepare} />);
    expect(screen.getByText(/New or changed objects need Complete Community 3D/)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Render' })).toBeDisabled();
    fireEvent.click(screen.getByRole('button', { name: 'Open 3D build controls' }));
    expect(prepare).toHaveBeenCalledTimes(1);
    expect(capture).not.toHaveBeenCalled();
    expect(mocks.direct).not.toHaveBeenCalled();
  });
});
