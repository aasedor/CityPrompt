import '@testing-library/jest-dom/vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { VideoGeneratePanel } from './VideoGeneratePanel';

const api = vi.hoisted(() => ({ capabilities: vi.fn(), list: vi.fn(), preflight: vi.fn(), generate: vi.fn(), imageGenerate: vi.fn(), imageList: vi.fn(), imageRecover: vi.fn() }));
vi.mock('@/services/api', () => ({
  direct3DAttempts: { capabilities: api.capabilities, list: api.imageList, generate: api.imageGenerate, recover: api.imageRecover }, videoRenderApi: api,
  authApi: { me: vi.fn() }, resolveApiFileUrl: (url: string) => url,
  getApiErrorMessage: (_error: unknown, fallback: string) => fallback,
}));
vi.mock('@/features/community3d/community3d', () => ({
  getCommunity3DCaptureClaims: () => [{ zone_id: 'park', source_hash: 'source', representation_hash: 'representation' }],
}));

describe('free route preview when finished generation is unavailable', () => {
  it('restores a paid guide with its exact original MP4 after reload instead of recapturing it', async () => {
    api.capabilities.mockResolvedValue({ video_enabled: true });
    api.list.mockResolvedValue({ attempts: [], attempts_used: 0, attempts_remaining: 2, max_attempts: 2 });
    const attempt = {id:'guide', style:'video-appearance',status:'completed',created_at:'2026-10-21T00:00:00Z'};
    api.imageList.mockResolvedValue([attempt]);
    api.imageRecover.mockResolvedValue({ response: {purpose:'video_appearance',attempt_id:'guide',image_base64:'cGhvdG8='},
      source_request: {project_id:'trial',provider:'omni',control_mode:'preview_video',render_quality:'draft',duration_seconds:4,
        camera_motion:'path_follow',guide_frame_base64:'original-native-frame',preview_video_base64:'data:video/mp4;base64,b3JpZ2luYWw=',
        preview_video_mime_type:'video/mp4',route_points:[{x:.3,y:.7},{x:.5,y:.7}],custom_prompt:'Realistic daylight.',
        route_keyframes_base64:[],community_3d_claims:[],details_revision:1,
        character_reference_base64:'hidden-old-reference', character_reference_mime_type:'image/png'} });
    api.preflight.mockResolvedValue({ready:true,provider:'omni',attempts_used:0,attempts_remaining:2,max_attempts:2});
    const captureRouteControls = vi.fn();
    render(<VideoGeneratePanel projectId="trial" canvas={null} buildings={[]} siteZones={[]} detailsRevision={1}
      captureAerialFrame={async () => 'data:image/jpeg;base64,ZnJhbWU='} captureRouteControls={captureRouteControls} onClose={vi.fn()} />);
    await screen.findByAltText('Captured City Prompt scene');
    fireEvent.click(screen.getByRole('checkbox',{name:'Photographic finish'}));
    fireEvent.click(screen.getByText('Recover saved guides'));
    fireEvent.click(await screen.findByRole('button',{name:/Recover guide$/}));
    fireEvent.click(await screen.findByRole('button',{name:'Use guide and restore original route'}));
    await screen.findByText(/Using the original saved route recording/);
    fireEvent.click(screen.getByRole('button',{name:'Run free check'}));
    await waitFor(() => expect(api.preflight).toHaveBeenCalledOnce());
    expect(api.preflight).toHaveBeenCalledWith(expect.objectContaining({
      appearance_attempt_id:'guide',omni_reference_mode:'appearance_references',use_custom_prompt_only:true,
      guide_frame_base64:'original-native-frame',route_keyframes_base64:['data:image/png;base64,cGhvdG8='],
      preview_video_base64:'data:video/mp4;base64,b3JpZ2luYWw='}));
    expect(captureRouteControls).not.toHaveBeenCalled();
    expect(api.generate).not.toHaveBeenCalled();
    expect(api.imageGenerate).not.toHaveBeenCalled();
    expect(api.preflight.mock.calls[0][0].character_reference_base64).toBeUndefined();
    fireEvent.change(screen.getByLabelText('Character appearance reference (optional)'), {
      target: { files: [new File(['new-person'], 'person.png', {type:'image/png'})] },
    });
    await screen.findByAltText('Character appearance reference');
    fireEvent.click(screen.getByRole('button',{name:'Run free check'}));
    await waitFor(() => expect(api.preflight).toHaveBeenCalledTimes(2));
    expect(api.preflight.mock.calls[1][0].character_reference_base64).toBe('data:image/png;base64,bmV3LXBlcnNvbg==');
    fireEvent.click(screen.getByRole('button',{name:'Remove reference'}));
    fireEvent.click(screen.getByRole('button',{name:'Run free check'}));
    await waitFor(() => expect(api.preflight).toHaveBeenCalledTimes(3));
    expect(api.preflight.mock.calls[2][0].character_reference_base64).toBeUndefined();
    fireEvent.click(screen.getByRole('button',{name:'8 seconds'}));
    expect(screen.getByRole('button',{name:/Generate trial/})).toBeDisabled();
  });
  it('offers photographic finishing only for Omni route edits and requires a reviewed guide before video', async () => {
    api.capabilities.mockResolvedValue({ video_enabled: true });
    api.list.mockResolvedValue({ attempts: [], attempts_used: 0, attempts_remaining: 2, max_attempts: 2 });
    api.imageList.mockResolvedValue([]);
    render(<VideoGeneratePanel projectId="trial" canvas={null} buildings={[]} siteZones={[]}
      captureAerialFrame={async () => 'data:image/jpeg;base64,ZnJhbWU='} onClose={vi.fn()} />);
    await screen.findByAltText('Captured City Prompt scene');
    fireEvent.click(screen.getByRole('checkbox', {name: 'Photographic finish'}));
    expect(screen.getByRole('button', {name: /Create photographic guide.*26 tokens/})).toBeVisible();
    expect(screen.getByText(/Video is a separate paid step after review/)).toBeVisible();
    expect(api.imageGenerate).not.toHaveBeenCalled();
    expect(api.generate).not.toHaveBeenCalled();
    fireEvent.click(screen.getByRole('button', {name: /Single frame/}));
    expect(screen.queryByRole('button', {name: /Create photographic guide/})).not.toBeInTheDocument();
  });
  it('binds scene reference frames to the free check and invalidates it when disabled', async () => {
    api.capabilities.mockResolvedValue({ video_enabled: true });
    api.list.mockResolvedValue({ attempts: [], attempts_used: 0, attempts_remaining: 2, max_attempts: 2 });
    api.preflight.mockResolvedValue({ ready: true, width: 1280, height: 720,
      model: 'gemini-omni-1.1-flash', scene_revision_sha256: 'b'.repeat(64) });
    const captureRouteControls = vi.fn().mockResolvedValue({
      keyframesBase64: ['start-frame', 'middle-frame', 'end-frame'],
      previewVideoBase64: 'data:video/mp4;base64,Z3VpZGU=', previewVideoMimeType: 'video/mp4',
    });
    render(<VideoGeneratePanel projectId="trial" canvas={null} buildings={[]} siteZones={[]}
      captureAerialFrame={async () => 'data:image/jpeg;base64,ZnJhbWU='}
      captureRouteControls={captureRouteControls} onClose={vi.fn()} />);
    await screen.findByAltText('Captured City Prompt scene');
    fireEvent.click(screen.getByRole('checkbox', { name: 'Use scene reference frames' }));
    const route = screen.getByLabelText('Add drone path vertex');
    vi.spyOn(route, 'getBoundingClientRect').mockReturnValue({ left: 0, top: 0, width: 100, height: 100 } as DOMRect);
    fireEvent.click(route, { clientX: 40, clientY: 65 });
    fireEvent.click(route, { clientX: 60, clientY: 65 });
    fireEvent.click(screen.getByRole('button', { name: 'Run free check' }));
    await waitFor(() => expect(api.preflight).toHaveBeenCalledOnce());
    expect(api.preflight).toHaveBeenCalledWith(expect.objectContaining({
      omni_reference_mode: 'architecture_references',
      route_keyframes_base64: ['data:image/jpeg;base64,ZnJhbWU=', 'data:image/jpeg;base64,ZnJhbWU='],
      preview_video_base64: 'data:video/mp4;base64,Z3VpZGU=',
    }));
    await waitFor(() => expect(screen.getByRole('button', { name: /Generate trial/ })).toBeEnabled());
    fireEvent.click(screen.getByRole('checkbox', { name: 'Use scene reference frames' }));
    expect(screen.getByRole('button', { name: /Generate trial/ })).toBeDisabled();
    expect(api.generate).not.toHaveBeenCalled();
  });
  it('captures four seconds with opt-in people motion and invalidates the free check when duration changes', async () => {
    api.capabilities.mockResolvedValue({ video_enabled: true });
    api.list.mockResolvedValue({ attempts: [], attempts_used: 0, attempts_remaining: 2, max_attempts: 2 });
    api.preflight.mockResolvedValue({ ready: true, width: 1280, height: 720,
      model: 'gemini-omni-1.1-flash', estimated_cost_usd: .51, scene_revision_sha256: 'b'.repeat(64) });
    const captureRouteControls = vi.fn().mockResolvedValue({
      keyframesBase64: ['data:image/jpeg;base64,ZnJhbWU='],
      previewVideoBase64: 'data:video/mp4;base64,Z3VpZGU=', previewVideoMimeType: 'video/mp4',
      previewCaptureProfile: { encoder: 'webcodecs_h264', frameCount: 96, fps: 24, width: 1280, height: 720 },
    });
    render(<VideoGeneratePanel projectId="trial" canvas={null} buildings={[]} siteZones={[]}
      captureAerialFrame={async () => 'data:image/jpeg;base64,ZnJhbWU='}
      captureRouteControls={captureRouteControls} onClose={vi.fn()} />);
    await screen.findByAltText('Captured City Prompt scene');
    fireEvent.click(screen.getByRole('button', { name: '4 seconds' }));
    fireEvent.click(screen.getByRole('checkbox', { name: 'Animate placed people' }));
    const route = screen.getByLabelText('Add drone path vertex');
    vi.spyOn(route, 'getBoundingClientRect').mockReturnValue({ left: 0, top: 0, width: 100, height: 100 } as DOMRect);
    fireEvent.click(route, { clientX: 40, clientY: 65 });
    fireEvent.click(route, { clientX: 60, clientY: 65 });
    fireEvent.click(screen.getByRole('button', { name: 'Run free check' }));
    await waitFor(() => expect(api.preflight).toHaveBeenCalledOnce());
    expect(captureRouteControls).toHaveBeenCalledWith(expect.objectContaining({ durationSeconds: 4, animatePeople: true }));
    expect(api.preflight).toHaveBeenCalledWith(expect.objectContaining({ duration_seconds: 4,
      capture_profile: expect.objectContaining({ frame_count: 96 }) }));
    await waitFor(() => expect(screen.getByRole('button', { name: /Generate trial/ })).toBeEnabled());
    fireEvent.click(screen.getByRole('button', { name: '8 seconds' }));
    expect(screen.getByRole('button', { name: /Generate trial/ })).toBeDisabled();
    expect(api.generate).not.toHaveBeenCalled();
  });
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

  it('binds the uploaded appearance image to preflight and clears approval when removed', async () => {
    api.capabilities.mockResolvedValue({ video_enabled: true });
    api.list.mockResolvedValue({ attempts: [], attempts_used: 0, attempts_remaining: 2, max_attempts: 2 });
    api.preflight.mockResolvedValue({ ready: true, width: 1280, height: 720, model: 'gemini-omni-1.1-flash' });
    const captureRouteControls = vi.fn().mockResolvedValue({ keyframesBase64: ['data:image/jpeg;base64,ZnJhbWU='],
      previewVideoBase64: 'data:video/mp4;base64,Z3VpZGU=', previewVideoMimeType: 'video/mp4' });
    render(<VideoGeneratePanel projectId="trial" canvas={null} buildings={[]} siteZones={[]}
      captureAerialFrame={async () => 'data:image/jpeg;base64,ZnJhbWU='}
      captureRouteControls={captureRouteControls} onClose={vi.fn()} />);
    await screen.findByAltText('Captured City Prompt scene');
    fireEvent.change(screen.getByLabelText('Character appearance reference (optional)'), {
      target: { files: [new File(['reference'], 'maya.png', { type: 'image/png' })] },
    });
    await screen.findByAltText('Character appearance reference');
    const route = screen.getByLabelText('Add drone path vertex');
    vi.spyOn(route, 'getBoundingClientRect').mockReturnValue({ left: 0, top: 0, width: 100, height: 100 } as DOMRect);
    fireEvent.click(route, { clientX: 40, clientY: 65 }); fireEvent.click(route, { clientX: 60, clientY: 65 });
    fireEvent.click(screen.getByRole('button', { name: 'Run free check' }));
    await waitFor(() => expect(api.preflight).toHaveBeenCalledOnce());
    expect(api.preflight).toHaveBeenCalledWith(expect.objectContaining({ character_reference_base64: 'data:image/png;base64,cmVmZXJlbmNl', character_reference_mime_type: 'image/png' }));
    await waitFor(() => expect(screen.getByRole('button', { name: /Generate trial/ })).toBeEnabled());
    fireEvent.click(screen.getByRole('button', { name: 'Remove reference' }));
    expect(screen.getByRole('button', { name: /Generate trial/ })).toBeDisabled();
    expect(api.generate).not.toHaveBeenCalled();
  });

  it('includes optional scene details in preflight and invalidates approval when they change', async () => {
    api.capabilities.mockResolvedValue({ video_enabled: true });
    api.list.mockResolvedValue({ attempts: [], attempts_used: 0, attempts_remaining: 2, max_attempts: 2 });
    api.preflight.mockResolvedValue({ ready: true, width: 1280, height: 720,
      model: 'gemini-omni-1.1-flash', estimated_cost_usd: .81, scene_revision_sha256: 'a'.repeat(64) });
    const captureRouteControls = vi.fn().mockResolvedValue({
      keyframesBase64: ['data:image/jpeg;base64,ZnJhbWU='],
      previewVideoBase64: 'data:video/mp4;base64,Z3VpZGU=', previewVideoMimeType: 'video/mp4',
      previewCaptureProfile: { width: 1280, height: 720, renderWidth: 1280, renderHeight: 720 },
    });
    render(<VideoGeneratePanel projectId="trial" canvas={null} buildings={[]} siteZones={[]}
      captureAerialFrame={async () => 'data:image/jpeg;base64,ZnJhbWU='}
      captureRouteControls={captureRouteControls} onClose={vi.fn()} />);
    await screen.findByAltText('Captured City Prompt scene');
    const prompt = screen.getByRole('textbox', { name: 'Custom prompt (optional)' });
    expect(screen.getByText(/targets live-action architectural footage/)).toBeVisible();
    expect(screen.getByText(/Output estimate allows 10 seconds/)).toBeVisible();
    expect(prompt).toHaveAttribute('maxLength', '600');
    fireEvent.change(prompt, { target: { value: 'A woman walks her dog on the sidewalk.' } });
    const route = screen.getByLabelText('Add drone path vertex');
    vi.spyOn(route, 'getBoundingClientRect').mockReturnValue({ left: 0, top: 0, width: 100, height: 100 } as DOMRect);
    fireEvent.click(route, { clientX: 40, clientY: 65 });
    fireEvent.click(route, { clientX: 60, clientY: 65 });
    fireEvent.click(screen.getByRole('button', { name: 'Run free check' }));
    await waitFor(() => expect(api.preflight).toHaveBeenCalledOnce());
    expect(api.preflight).toHaveBeenCalledWith(expect.objectContaining({
      custom_prompt: 'A woman walks her dog on the sidewalk.', duration_seconds: 8,
    }));
    await waitFor(() => expect(screen.getByRole('button', { name: /Generate trial/ })).toBeEnabled());
    fireEvent.click(screen.getByRole('checkbox', { name: 'Use only my prompt' }));
    expect(screen.getByRole('button', { name: /Generate trial/ })).toBeDisabled();
    fireEvent.click(screen.getByRole('button', { name: 'Run free check' }));
    await waitFor(() => expect(api.preflight).toHaveBeenCalledTimes(2));
    expect(api.preflight).toHaveBeenLastCalledWith(expect.objectContaining({
      use_custom_prompt_only: true, custom_prompt: 'A woman walks her dog on the sidewalk.',
    }));
    await waitFor(() => expect(screen.getByRole('button', { name: /Generate trial/ })).toBeEnabled());
    fireEvent.change(prompt, { target: { value: 'Warm evening light.' } });
    expect(screen.getByRole('button', { name: /Generate trial/ })).toBeDisabled();
    expect(api.generate).not.toHaveBeenCalled();
  });

  it('shows measured output facts and warnings when a saved result differs from the request', async () => {
    api.capabilities.mockResolvedValue({ video_enabled: true });
    api.list.mockResolvedValue({ attempts_used: 1, attempts_remaining: 0, max_attempts: 1,
      attempts: [{ id: 'measured', status: 'complete', provider: 'omni', camera_motion: 'bicycle_ride',
        style: 'source_fidelity', request_id: 'measured-request', created_at: '2026-10-21T00:00:00Z',
        duration_seconds: 8, video_url: '/measured.mp4', estimated_cost_usd: 1.0136,
        output_media: { width: 1280, height: 720, fps: 24, frame_count: 245, duration_seconds: 10.2 },
        media_warning: 'The provider changed the clip duration.' }] });
    render(<VideoGeneratePanel projectId="trial" canvas={null} buildings={[]} siteZones={[]}
      captureAerialFrame={async () => 'data:image/jpeg;base64,ZnJhbWU='} onClose={vi.fn()} />);
    expect(await screen.findByText(/10.2 sec · 1280×720 output/)).toBeVisible();
    expect(screen.getByText('The provider changed the clip duration.')).toBeVisible();
    expect(api.generate).not.toHaveBeenCalled();
  });
});
