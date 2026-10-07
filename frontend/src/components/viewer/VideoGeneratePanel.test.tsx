import '@testing-library/jest-dom/vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { VideoGeneratePanel } from './VideoGeneratePanel';

const api = vi.hoisted(() => ({ capabilities: vi.fn(), list: vi.fn(), preflight: vi.fn(), generate: vi.fn() }));
vi.mock('@/services/api', () => ({
  direct3DAttempts: { capabilities: api.capabilities }, videoRenderApi: api,
  authApi: { me: vi.fn() }, resolveApiFileUrl: (url: string) => url,
  getApiErrorMessage: (_error: unknown, fallback: string) => fallback,
}));
vi.mock('@/features/community3d/community3d', () => ({
  getCommunity3DCaptureClaims: () => [{ zone_id: 'park', source_hash: 'source', representation_hash: 'representation' }],
}));

describe('free route preview when finished generation is unavailable', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    api.capabilities.mockResolvedValue({ video_enabled: false });
    vi.stubGlobal('Image', class {
      naturalWidth = 1280;
      naturalHeight = 720;
      onload: (() => void) | null = null;
      set src(_source: string) { queueMicrotask(() => this.onload?.()); }
    });
    vi.spyOn(HTMLCanvasElement.prototype, 'getContext').mockReturnValue({ drawImage: vi.fn() } as unknown as ReturnType<HTMLCanvasElement['getContext']>);
    vi.spyOn(HTMLCanvasElement.prototype, 'toDataURL').mockReturnValue('data:image/jpeg;base64,ZnJhbWU=');
  });
  afterEach(() => { vi.restoreAllMocks(); vi.unstubAllGlobals(); });

  it('captures and offers a bicycle guide download without requesting video history or generation', async () => {
    const captureRouteControls = vi.fn().mockResolvedValue({
      keyframesBase64: ['data:image/jpeg;base64,ZnJhbWU='],
      previewVideoBase64: 'data:video/mp4;base64,Z3VpZGU=', previewVideoMimeType: 'video/mp4',
      routeProfile: { distanceMeters: 24, averageSpeedMps: 3, eyeHeightMeters: 1.6 },
      previewCaptureProfile: { width: 1280, height: 720, renderWidth: 1280, renderHeight: 720 },
    });
    render(<VideoGeneratePanel projectId="trial" canvas={null} buildings={[]} siteZones={[]}
      captureAerialFrame={async () => 'data:image/jpeg;base64,ZnJhbWU='}
      captureRouteControls={captureRouteControls} onClose={vi.fn()} />);
    await screen.findByAltText('Captured City Prompt scene');
    expect(api.list).not.toHaveBeenCalled();
    expect(screen.getByRole('button', { name: 'Finished generation unavailable' })).toBeDisabled();
    expect(screen.getByRole('button', { name: 'Run free check' })).toBeDisabled();
    expect(screen.getByRole('button', { name: /Draft.*720p/ })).toHaveAttribute('aria-pressed', 'true');
    fireEvent.click(screen.getByRole('button', { name: /Bicycle ride/ }));
    const route = screen.getByLabelText('Add bicycle path vertex');
    vi.spyOn(route, 'getBoundingClientRect').mockReturnValue({ left: 0, top: 0, width: 100, height: 100 } as DOMRect);
    fireEvent.click(route, { clientX: 40, clientY: 65 });
    fireEvent.click(route, { clientX: 60, clientY: 65 });
    fireEvent.click(screen.getByRole('button', { name: 'Preview route · free' }));
    expect(await screen.findByRole('link', { name: 'Download preview' })).toHaveAttribute('download', 'city-prompt-guide.mp4');
    expect(captureRouteControls).toHaveBeenCalledWith(expect.objectContaining({
      cameraMotion: 'bicycle_ride', renderQuality: 'draft', durationSeconds: 8,
      routePoints: [{ x: .4, y: .65 }, { x: .6, y: .65 }],
    }));
    expect(screen.getByText(/24.0 m route · 10.8 km\/h average · 1.6 m camera height/)).toBeVisible();
    expect(screen.getByText('Draft source')).toBeVisible();
    expect(api.preflight).not.toHaveBeenCalled();
    expect(api.generate).not.toHaveBeenCalled();
  });

  it('keeps provider submission unavailable after a failed capability check', async () => {
    api.capabilities.mockRejectedValue(new Error('offline'));
    render(<VideoGeneratePanel projectId="trial" canvas={null} buildings={[]} siteZones={[]}
      captureAerialFrame={async () => 'data:image/jpeg;base64,ZnJhbWU='} onClose={vi.fn()} />);
    await waitFor(() => expect(api.capabilities).toHaveBeenCalledOnce());
    await screen.findByAltText('Captured City Prompt scene');
    expect(screen.getByRole('button', { name: 'Finished generation unavailable' })).toBeDisabled();
    expect(api.list).not.toHaveBeenCalled();
    expect(api.generate).not.toHaveBeenCalled();
  });
});
