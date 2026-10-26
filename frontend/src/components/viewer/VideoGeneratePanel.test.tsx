import '@testing-library/jest-dom/vitest';
import { act, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { VideoGeneratePanel } from './VideoGeneratePanel';
import type {VideoRouteCaptureResult} from './videoRouteControls';
const BrowserURL=URL;

const api = vi.hoisted(() => ({ capabilities: vi.fn(), list: vi.fn(), preflight: vi.fn(), generate: vi.fn(), imageGenerate: vi.fn(), imageList: vi.fn(), imageRecover: vi.fn() }));
vi.mock('@/services/api', () => ({
  direct3DAttempts: { capabilities: api.capabilities, list: api.imageList, generate: api.imageGenerate, recover: api.imageRecover }, videoRenderApi: api,
  authApi: { me: vi.fn() }, resolveApiFileUrl: (url: string) => url,
  getApiErrorMessage: (_error: unknown, fallback: string) => fallback,
}));
vi.mock('@/features/community3d/community3d', () => ({
  getCommunity3DCaptureClaims: () => [{ zone_id: 'park', source_hash: 'source', representation_hash: 'representation' }],
}));

describe('Omni video preparation and saved-video recovery', () => {
  it('defaults to photographic finish, previews freely and prepares its guide only on Generate', async () => {
    api.capabilities.mockResolvedValue({video_enabled:true});
    api.list.mockResolvedValue({attempts:[],attempts_used:0,attempts_remaining:2,max_attempts:2});
    api.imageList.mockResolvedValue([]);
    api.preflight.mockResolvedValue({ready:true,provider:'omni',estimated_cost_usd:.81,scene_revision_sha256:'scene',attempts_remaining:2});
    api.imageGenerate.mockResolvedValue({purpose:'video_appearance',attempt_id:'guide',image_base64:'photo',source_video_sha256:'source',scene_revision_sha256:'scene'});
    api.generate.mockRejectedValue(new Error('response lost'));
    render(<VideoGeneratePanel projectId="trial" canvas={null} buildings={[]} siteZones={[]}
      captureAerialFrame={async ()=>'data:image/jpeg;base64,ZnJhbWU='}
      captureRouteControls={async()=>({keyframesBase64:['start'],previewVideoBase64:'data:video/mp4;base64,Z3VpZGU=',previewVideoMimeType:'video/mp4'})} onClose={vi.fn()}/>);
    await screen.findByAltText('Captured City Prompt scene');
    expect(screen.getByRole('checkbox',{name:'Photographic finish'})).toBeChecked();
    expect(api.imageGenerate).not.toHaveBeenCalled();
    fireEvent.click(screen.getByRole('button',{name:'Preview · free'}));
    const generate=await screen.findByRole('button',{name:/Generate video.*26 tokens/});
    await waitFor(()=>expect(generate).toBeEnabled());
    expect(api.imageGenerate).not.toHaveBeenCalled();
    fireEvent.click(generate);
    await waitFor(()=>expect(api.generate).toHaveBeenCalledOnce());
    expect(api.imageGenerate).toHaveBeenCalledOnce();
    expect(api.generate.mock.calls[0][0]).toMatchObject({appearance_attempt_id:'guide',omni_reference_mode:'appearance_references',route_keyframes_base64:['data:image/png;base64,photo'],preview_video_base64:'data:video/mp4;base64,Z3VpZGU='});
    await waitFor(()=>expect(screen.getByRole('button',{name:/Generate video/})).toBeEnabled());
    fireEvent.click(screen.getByRole('button',{name:/Generate video/}));
    await waitFor(()=>expect(api.generate).toHaveBeenCalledTimes(2));
    expect(api.imageGenerate).toHaveBeenCalledOnce();
    expect(api.generate.mock.calls[1][0].request_id).toBe(api.generate.mock.calls[0][0].request_id);
  });
  it('allows cancelling a free capture without submitting its late result or a paid request', async () => {
    api.capabilities.mockResolvedValue({video_enabled:true});
    api.list.mockResolvedValue({attempts:[],attempts_used:0,attempts_remaining:2,max_attempts:2});
    const captureRouteControls=vi.fn((request)=>new Promise<VideoRouteCaptureResult>((_resolve,reject)=>{
      request.signal.addEventListener('abort',()=>reject(new DOMException('Cancelled','AbortError')),{once:true});
    }));
    render(<VideoGeneratePanel projectId="trial" canvas={null} buildings={[]} siteZones={[]}
      captureAerialFrame={async()=>'data:image/jpeg;base64,ZnJhbWU='}
      captureRouteControls={captureRouteControls} onClose={vi.fn()}/>);
    await screen.findByAltText('Captured City Prompt scene');
    fireEvent.click(screen.getByRole('button',{name:'Preview · free'}));
    await screen.findByRole('button',{name:'Cancel preview'});
    expect(screen.getByRole('button',{name:'Close Video Render'})).toBeEnabled();
    fireEvent.click(screen.getByRole('button',{name:'Cancel preview'}));
    await waitFor(()=>expect(screen.getByRole('button',{name:'Preview · free'})).toBeEnabled());
    expect(api.preflight).not.toHaveBeenCalled();
    expect(api.generate).not.toHaveBeenCalled();
    expect(screen.queryByRole('alert')).not.toBeInTheDocument();
  });
  it('prepares an Omni shot from the current view with one free Preview and a separate paid Generate', async () => {
    api.capabilities.mockResolvedValue({ video_enabled: true });
    api.list.mockResolvedValue({ attempts: [], attempts_used: 0, attempts_remaining: 2, max_attempts: 2 });
    api.preflight.mockResolvedValue({ ready: true, provider: 'omni', estimated_cost_usd: .81,
      attempts_used: 0, attempts_remaining: 2, max_attempts: 2 });
    const captureRouteControls = vi.fn().mockResolvedValue({ keyframesBase64: ['start'],
      previewVideoBase64: 'data:video/mp4;base64,Z3VpZGU=', previewVideoMimeType: 'video/mp4' });
    render(<VideoGeneratePanel projectId="trial" canvas={null} buildings={[]} siteZones={[]}
      captureAerialFrame={async () => 'data:image/jpeg;base64,ZnJhbWU='}
      captureRouteControls={captureRouteControls} onClose={vi.fn()} />);
    await screen.findByAltText('Captured City Prompt scene');
    expect(screen.getByRole('button', {name: /Aerial/})).toBeVisible();
    expect(screen.getByRole('button', {name: /Street/})).toBeVisible();
    expect(screen.getByRole('button', {name: /Follow a person/})).toBeVisible();
    expect(screen.queryByRole('button', {name: /Seedance|Internal Enhance|Single frame|Route keyframes|Preview-video edit/})).not.toBeInTheDocument();
    expect(screen.getByLabelText('Custom prompt (optional)')).toBeVisible();
    expect(screen.queryByLabelText('Add drone path vertex')).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', {name: 'Preview · free'}));
    await waitFor(() => expect(api.preflight).toHaveBeenCalledOnce());
    expect(captureRouteControls.mock.calls[0][0].routePoints.length).toBeGreaterThanOrEqual(2);
    expect(api.preflight).toHaveBeenCalledWith(expect.objectContaining({provider: 'omni', control_mode: 'preview_video'}));
    expect(await screen.findByRole('button', {name: /Generate.*0.81/})).toBeEnabled();
    expect(api.generate).not.toHaveBeenCalled();
    expect(api.imageGenerate).not.toHaveBeenCalled();
    fireEvent.click(screen.getByText('Advanced'));
    expect(screen.queryByRole('button', {name: /Seedance|Internal Enhance|Single frame|Route keyframes|Preview-video edit/})).not.toBeInTheDocument();
  });

  it('keeps saved actions in custom-only prompts and invalidates preview after an action change', async () => {
    api.capabilities.mockResolvedValue({ video_enabled: true });
    api.list.mockResolvedValue({ attempts: [], attempts_used: 0, attempts_remaining: 2, max_attempts: 2 });
    api.preflight.mockResolvedValue({ ready: true, provider: 'omni', estimated_cost_usd: .81,
      attempts_used: 0, attempts_remaining: 2, max_attempts: 2 });
    const captureRouteControls = vi.fn().mockResolvedValue({ keyframesBase64: ['start'],
      previewVideoBase64: 'data:video/mp4;base64,Z3VpZGU=', previewVideoMimeType: 'video/mp4' });
    const props = { projectId: 'trial', canvas: null, buildings: [], siteZones: [],
      captureAerialFrame: async () => 'data:image/jpeg;base64,ZnJhbWU=', captureRouteControls, onClose: vi.fn() };
    const {rerender} = render(<VideoGeneratePanel {...props} peopleDirection="Actor 7 is reading at the saved position." />);
    await screen.findByAltText('Captured City Prompt scene');
    fireEvent.click(screen.getByRole('checkbox',{name:'Photographic finish'}));
    fireEvent.change(screen.getByLabelText('Custom prompt (optional)'), {target: {value: 'Warm daylight.'}});
    fireEvent.click(screen.getByText('Advanced'));
    fireEvent.click(screen.getByLabelText('Use only my prompt'));
    fireEvent.click(screen.getByRole('button', {name: 'Preview · free'}));
    await waitFor(() => expect(api.preflight).toHaveBeenCalledOnce());
    expect(api.preflight.mock.calls[0][0]).toMatchObject({use_custom_prompt_only: true,
      custom_prompt: 'Warm daylight.'});
    expect(api.preflight.mock.calls[0][0].scene_brief).toContain('Actor 7 is reading at the saved position.');
    expect(screen.getByRole('button', {name: /Generate video/})).toBeEnabled();
    rerender(<VideoGeneratePanel {...props} peopleDirection="Actor 7 is waving at the saved position." />);
    expect(screen.getByRole('button', {name: /Generate video/})).toBeDisabled();
    fireEvent.click(screen.getByRole('button', {name: 'Preview · free'}));
    await waitFor(() => expect(api.preflight).toHaveBeenCalledTimes(2));
    expect(captureRouteControls).toHaveBeenCalledTimes(2);
    expect(api.preflight.mock.calls[1][0].scene_brief).toContain('Actor 7 is waving at the saved position.');
    expect(api.generate).not.toHaveBeenCalled();
  });

  it.each([undefined, NaN, -1])('rejects a ready response without a valid cost (%s)', async (cost) => {
    api.capabilities.mockResolvedValue({ video_enabled: true });
    api.list.mockResolvedValue({ attempts: [], attempts_used: 0, attempts_remaining: 2, max_attempts: 2 });
    api.preflight.mockResolvedValue({ ready: true, provider: 'omni', estimated_cost_usd: cost,
      attempts_used: 0, attempts_remaining: 2, max_attempts: 2 });
    render(<VideoGeneratePanel projectId="trial" canvas={null} buildings={[]} siteZones={[]}
      captureAerialFrame={async () => 'data:image/jpeg;base64,ZnJhbWU='}
      captureRouteControls={async () => ({keyframesBase64:['start'], previewVideoBase64:'data:video/mp4;base64,Z3VpZGU=', previewVideoMimeType:'video/mp4'})}
      onClose={vi.fn()} />);
    await screen.findByAltText('Captured City Prompt scene');
    fireEvent.click(screen.getByRole('button', {name: 'Preview · free'}));
    await waitFor(() => expect(api.preflight).toHaveBeenCalledOnce());
    expect(screen.getByRole('button', {name: /Generate video/})).toBeDisabled();
    expect(api.generate).not.toHaveBeenCalled();
  });

  it('submits the exact checked body once and replays its request ID only after another explicit click', async () => {
    api.capabilities.mockResolvedValue({ video_enabled: true });
    api.list.mockResolvedValue({ attempts: [], attempts_used: 0, attempts_remaining: 2, max_attempts: 2 });
    api.preflight.mockResolvedValue({ ready: true, provider: 'omni', estimated_cost_usd: .81,
      attempts_used: 0, attempts_remaining: 2, max_attempts: 2 });
    let reject!: (reason: Error) => void;
    api.generate.mockImplementation(() => new Promise((_resolve, fail) => { reject = fail; }));
    render(<VideoGeneratePanel projectId="trial" canvas={null} buildings={[]} siteZones={[]}
      captureAerialFrame={async () => 'data:image/jpeg;base64,ZnJhbWU='}
      captureRouteControls={async () => ({keyframesBase64:['start'], previewVideoBase64:'data:video/mp4;base64,Z3VpZGU=', previewVideoMimeType:'video/mp4'})}
      onClose={vi.fn()} />);
    await screen.findByAltText('Captured City Prompt scene');
    fireEvent.click(screen.getByRole('checkbox',{name:'Photographic finish'}));
    fireEvent.click(screen.getByRole('button', {name: 'Preview \u00b7 free'}));
    const generate = await screen.findByRole('button', {name: /Generate.*0.81/});
    act(() => { fireEvent.click(generate); fireEvent.click(generate); });
    expect(api.generate).toHaveBeenCalledOnce();
    const submitted = api.generate.mock.calls[0][0];
    const {prepare_photographic_finish: _quoteOnly, ...checked} = api.preflight.mock.calls[0][0];
    expect(submitted).toEqual({...checked, request_id: expect.any(String), confirm_paid_submission: true});
    await act(async () => { reject(new Error('response lost')); });
    await waitFor(() => expect(screen.getByRole('button', {name: /Generate.*0.81/})).toBeEnabled());
    expect(api.generate).toHaveBeenCalledOnce();
    fireEvent.click(screen.getByRole('button', {name: 'Preview \u00b7 free'}));
    await waitFor(() => expect(api.preflight).toHaveBeenCalledTimes(2));
    await waitFor(() => expect(screen.getByRole('button', {name: /Generate.*0.81/})).toBeEnabled());
    fireEvent.click(screen.getByRole('button', {name: /Generate.*0.81/}));
    expect(api.generate).toHaveBeenCalledTimes(2);
    expect(api.generate.mock.calls[1][0]).toEqual(submitted);
    await act(async () => { reject(new Error('still unavailable')); });
  });

  it('rejects an outdated free check when saved actions change while it is pending', async () => {
    api.capabilities.mockResolvedValue({ video_enabled: true });
    api.list.mockResolvedValue({ attempts: [], attempts_used: 0, attempts_remaining: 2, max_attempts: 2 });
    let resolve!: (value: unknown) => void;
    api.preflight.mockImplementation(() => new Promise(done => {resolve = done;}));
    const props = {projectId:'trial',canvas:null,buildings:[],siteZones:[],onClose:vi.fn(),
      captureAerialFrame:async () => 'data:image/jpeg;base64,ZnJhbWU=',
      captureRouteControls:async () => ({keyframesBase64:['start'],previewVideoBase64:'data:video/mp4;base64,Z3VpZGU=',previewVideoMimeType:'video/mp4'})};
    const view = render(<VideoGeneratePanel {...props} peopleDirection="Actor reads." />);
    await screen.findByAltText('Captured City Prompt scene');
    fireEvent.click(screen.getByRole('button', {name:'Preview \u00b7 free'}));
    await waitFor(() => expect(api.preflight).toHaveBeenCalledOnce());
    view.rerender(<VideoGeneratePanel {...props} peopleDirection="Actor waves." />);
    await act(async () => {resolve({ready:true,provider:'omni',estimated_cost_usd:.81,attempts_used:0,attempts_remaining:2,max_attempts:2});});
    expect(screen.getByRole('button', {name:/Generate video/})).toBeDisabled();
    expect(screen.getByRole('alert')).toBeVisible();
    expect(api.generate).not.toHaveBeenCalled();
  });

  it('keeps the separate photographic-guide purchase behind a successful free check', async () => {
    api.capabilities.mockResolvedValue({video_enabled:true});
    api.list.mockResolvedValue({attempts:[],attempts_used:0,attempts_remaining:2,max_attempts:2});
    api.imageList.mockResolvedValue([]);
    api.preflight.mockResolvedValue({ready:false});
    api.imageGenerate.mockRejectedValue(new Error('should not buy'));
    render(<VideoGeneratePanel projectId="trial" canvas={null} buildings={[]} siteZones={[]} peopleDirection="Actor 7 is reading."
      captureAerialFrame={async () => 'data:image/jpeg;base64,ZnJhbWU='}
      captureRouteControls={async () => ({keyframesBase64:['start'],previewVideoBase64:'data:video/mp4;base64,Z3VpZGU=',previewVideoMimeType:'video/mp4'})}
      onClose={vi.fn()} />);
    await screen.findByAltText('Captured City Prompt scene');
    fireEvent.click(screen.getByText('Advanced'));

    fireEvent.click(screen.getByRole('button',{name:/Prepare and review guide separately/}));
    await screen.findByRole('alert');
    expect(api.preflight).toHaveBeenCalledOnce();
    expect(api.imageGenerate).not.toHaveBeenCalled();
    expect(api.generate).not.toHaveBeenCalled();
  });

  it('keeps the full optional guide prompt within its 600-character API limit and carries actions as scene context', async () => {
    api.capabilities.mockResolvedValue({video_enabled:true});
    api.list.mockResolvedValue({attempts:[],attempts_used:0,attempts_remaining:2,max_attempts:2});
    api.imageList.mockResolvedValue([]);
    api.preflight.mockResolvedValue({ready:true});
    api.imageGenerate.mockResolvedValue({purpose:'video_appearance',attempt_id:'guide',image_base64:'cGhvdG8='});
    const props = {projectId:'trial',canvas:null,buildings:[],siteZones:[],onClose:vi.fn(),
      captureAerialFrame:async () => 'data:image/jpeg;base64,ZnJhbWU=',
      captureRouteControls:async () => ({keyframesBase64:['start'],previewVideoBase64:'data:video/mp4;base64,Z3VpZGU=',previewVideoMimeType:'video/mp4'})};
    const view = render(<VideoGeneratePanel {...props} peopleDirection="Actor 7 is reading." />);
    await screen.findByAltText('Captured City Prompt scene');
    fireEvent.change(screen.getByLabelText('Custom prompt (optional)'), {target:{value:'A'.repeat(600)}});
    fireEvent.click(screen.getByText('Advanced'));

    expect(api.imageGenerate).not.toHaveBeenCalled();
    fireEvent.click(screen.getByRole('button',{name:/Prepare and review guide separately/}));
    await screen.findByAltText('Photographic video guide to review');
    expect(api.imageGenerate).toHaveBeenCalledOnce();
    expect(api.imageGenerate.mock.calls[0][0].prompt).toBe('A'.repeat(600));
    expect(api.imageGenerate.mock.calls[0][0].source_request.scene_brief).toContain('Actor 7 is reading.');
    fireEvent.click(screen.getByRole('button',{name:'Use this guide'}));
    view.rerender(<VideoGeneratePanel {...props} peopleDirection="Actor 7 is waving." />);
    expect(screen.queryByAltText('Photographic video guide to review')).not.toBeInTheDocument();
    expect(screen.getByText(/scene or route changed.*matching guide/)).toBeVisible();
    expect(api.generate).not.toHaveBeenCalled();
  });

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
    api.preflight.mockResolvedValue({ready:true,estimated_cost_usd:.81,provider:'omni',attempts_used:0,attempts_remaining:2,max_attempts:2});
    const captureRouteControls = vi.fn();
    render(<VideoGeneratePanel projectId="trial" canvas={null} buildings={[]} siteZones={[]} detailsRevision={1}
      captureAerialFrame={async () => 'data:image/jpeg;base64,ZnJhbWU='} captureRouteControls={captureRouteControls} onClose={vi.fn()} />);
    await screen.findByAltText('Captured City Prompt scene');
    fireEvent.click(screen.getByText('Advanced'));
    fireEvent.click(screen.getByText('Recover saved guides'));
    fireEvent.click(await screen.findByRole('button',{name:/Recover guide$/}));
    fireEvent.click(await screen.findByRole('button',{name:'Use guide and restore original route'}));
    await screen.findByText(/Using the original saved route recording/);
    fireEvent.click(screen.getByRole('button',{name:'Preview \u00b7 free'}));
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
    fireEvent.click(screen.getByRole('button',{name:'Preview \u00b7 free'}));
    await waitFor(() => expect(api.preflight).toHaveBeenCalledTimes(2));
    expect(api.preflight.mock.calls[1][0].character_reference_base64).toBe('data:image/png;base64,bmV3LXBlcnNvbg==');
    fireEvent.click(screen.getByRole('button',{name:'Remove reference'}));
    fireEvent.click(screen.getByRole('button',{name:'Preview \u00b7 free'}));
    await waitFor(() => expect(api.preflight).toHaveBeenCalledTimes(3));
    expect(api.preflight.mock.calls[2][0].character_reference_base64).toBeUndefined();
    fireEvent.click(screen.getByRole('button',{name:'8 seconds'}));
    expect(screen.getByRole('button',{name:/Generate video/})).toBeDisabled();
  });
  it('explains automatic photographic finishing and keeps separate preparation in optional recovery', async () => {
    api.capabilities.mockResolvedValue({ video_enabled: true });
    api.list.mockResolvedValue({ attempts: [], attempts_used: 0, attempts_remaining: 2, max_attempts: 2 });
    api.imageList.mockResolvedValue([]);
    render(<VideoGeneratePanel projectId="trial" canvas={null} buildings={[]} siteZones={[]}
      captureAerialFrame={async () => 'data:image/jpeg;base64,ZnJhbWU='} onClose={vi.fn()} />);
    await screen.findByAltText('Captured City Prompt scene');
    fireEvent.click(screen.getByText('Advanced'));

    fireEvent.click(screen.getByText('Recover saved guides'));
    expect(screen.getByRole('button', {name: /Prepare and review guide separately.*26 tokens/})).toBeVisible();
    expect(screen.getByText(/Preview, loading and changing options are free/)).toBeVisible();
    expect(api.imageGenerate).not.toHaveBeenCalled();
    expect(api.generate).not.toHaveBeenCalled();
    expect(screen.getByRole('button', {name: /Generate video/})).toBeDisabled();
    expect(screen.queryByRole('button', {name: /Single frame/})).not.toBeInTheDocument();
  });
  it('binds scene reference frames to the free check and invalidates it when disabled', async () => {
    api.capabilities.mockResolvedValue({ video_enabled: true });
    api.list.mockResolvedValue({ attempts: [], attempts_used: 0, attempts_remaining: 2, max_attempts: 2 });
    api.preflight.mockResolvedValue({ ready: true, estimated_cost_usd: .81, width: 1280, height: 720,
      model: 'gemini-omni-1.1-flash', scene_revision_sha256: 'b'.repeat(64) });
    const captureRouteControls = vi.fn().mockResolvedValue({
      keyframesBase64: ['start-frame', 'middle-frame', 'end-frame'],
      previewVideoBase64: 'data:video/mp4;base64,Z3VpZGU=', previewVideoMimeType: 'video/mp4',
    });
    render(<VideoGeneratePanel projectId="trial" canvas={null} buildings={[]} siteZones={[]}
      captureAerialFrame={async () => 'data:image/jpeg;base64,ZnJhbWU='}
      captureRouteControls={captureRouteControls} onClose={vi.fn()} />);
    await screen.findByAltText('Captured City Prompt scene');
    fireEvent.click(screen.getByRole('checkbox',{name:'Photographic finish'}));
    fireEvent.click(screen.getByText('Advanced'));
    fireEvent.click(screen.getByRole('checkbox', { name: 'Use scene reference frames' }));
    fireEvent.click(screen.getByLabelText('Edit route on preview'));
    fireEvent.click(screen.getByRole('button', {name: 'Draw new route'}));
    const route = screen.getByLabelText('Camera route drawing area');
    vi.spyOn(route, 'getBoundingClientRect').mockReturnValue({ left: 0, top: 0, width: 100, height: 100 } as DOMRect);
    fireEvent.click(route, { clientX: 40, clientY: 65 });
    fireEvent.click(route, { clientX: 60, clientY: 65 });
    fireEvent.click(screen.getByRole('button', { name: 'Preview \u00b7 free' }));
    await waitFor(() => expect(api.preflight).toHaveBeenCalledOnce());
    expect(api.preflight).toHaveBeenCalledWith(expect.objectContaining({
      omni_reference_mode: 'architecture_references',
      route_keyframes_base64: ['data:image/jpeg;base64,ZnJhbWU=', 'data:image/jpeg;base64,ZnJhbWU='],
      preview_video_base64: 'data:video/mp4;base64,Z3VpZGU=',
    }));
    await waitFor(() => expect(screen.getByRole('button', { name: /Generate video/ })).toBeEnabled());
    fireEvent.click(screen.getByRole('checkbox', { name: 'Use scene reference frames' }));
    expect(screen.getByRole('button', { name: /Generate video/ })).toBeDisabled();
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
    fireEvent.click(screen.getByText('Advanced'));
    fireEvent.click(screen.getByRole('button', { name: '4 seconds' }));
    expect(screen.getByRole('checkbox', { name: 'Animate placed people' })).toBeChecked();
    fireEvent.click(screen.getByLabelText('Edit route on preview'));
    fireEvent.click(screen.getByRole('button', {name: 'Draw new route'}));
    const route = screen.getByLabelText('Camera route drawing area');
    vi.spyOn(route, 'getBoundingClientRect').mockReturnValue({ left: 0, top: 0, width: 100, height: 100 } as DOMRect);
    fireEvent.click(route, { clientX: 40, clientY: 65 });
    fireEvent.click(route, { clientX: 60, clientY: 65 });
    fireEvent.click(screen.getByRole('button', { name: 'Preview \u00b7 free' }));
    await waitFor(() => expect(api.preflight).toHaveBeenCalledOnce());
    expect(captureRouteControls).toHaveBeenCalledWith(expect.objectContaining({ durationSeconds: 4, animatePeople: true }));
    expect(api.preflight).toHaveBeenCalledWith(expect.objectContaining({ duration_seconds: 4,
      capture_profile: expect.objectContaining({ frame_count: 96 }) }));
    await waitFor(() => expect(screen.getByRole('button', { name: /Generate video/ })).toBeEnabled());
    fireEvent.click(screen.getByRole('button', { name: '8 seconds' }));
    expect(screen.getByRole('button', { name: /Generate video/ })).toBeDisabled();
    expect(api.generate).not.toHaveBeenCalled();
  });
  beforeEach(() => {
    vi.clearAllMocks();
    vi.stubGlobal('URL',class extends BrowserURL {
      static createObjectURL=()=> 'blob:test-preview';
      static revokeObjectURL=()=>{};
    });
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
    fireEvent.click(screen.getByText('Advanced'));
    expect(api.list).not.toHaveBeenCalled();
    expect(screen.getByRole('button', { name: 'Finished generation unavailable' })).toBeDisabled();
    expect(screen.getByRole('button', { name: 'Preview \u00b7 free' })).toBeEnabled();
    expect(screen.getByRole('button', { name: /Draft.*720p/ })).toHaveAttribute('aria-pressed', 'true');
    fireEvent.click(screen.getByRole('button', { name: /Bicycle ride/ }));
    fireEvent.click(screen.getByLabelText('Edit route on preview'));
    fireEvent.click(screen.getByRole('button', {name: 'Draw new route'}));
    const route = screen.getByLabelText('Camera route drawing area');
    vi.spyOn(route, 'getBoundingClientRect').mockReturnValue({ left: 0, top: 0, width: 100, height: 100 } as DOMRect);
    fireEvent.click(route, { clientX: 40, clientY: 65 });
    fireEvent.click(route, { clientX: 60, clientY: 65 });
    fireEvent.click(screen.getByRole('button', { name: 'Preview \u00b7 free' }));
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
    fireEvent.click(screen.getByText('Advanced'));
    expect(screen.getByRole('button', { name: 'Finished generation unavailable' })).toBeDisabled();
    expect(api.list).not.toHaveBeenCalled();
    expect(api.generate).not.toHaveBeenCalled();
  });

  it('binds the uploaded appearance image to preflight and clears approval when removed', async () => {
    api.capabilities.mockResolvedValue({ video_enabled: true });
    api.list.mockResolvedValue({ attempts: [], attempts_used: 0, attempts_remaining: 2, max_attempts: 2 });
    api.preflight.mockResolvedValue({ ready: true, estimated_cost_usd: .81, width: 1280, height: 720, model: 'gemini-omni-1.1-flash' });
    const captureRouteControls = vi.fn().mockResolvedValue({ keyframesBase64: ['data:image/jpeg;base64,ZnJhbWU='],
      previewVideoBase64: 'data:video/mp4;base64,Z3VpZGU=', previewVideoMimeType: 'video/mp4' });
    render(<VideoGeneratePanel projectId="trial" canvas={null} buildings={[]} siteZones={[]}
      captureAerialFrame={async () => 'data:image/jpeg;base64,ZnJhbWU='}
      captureRouteControls={captureRouteControls} onClose={vi.fn()} />);
    await screen.findByAltText('Captured City Prompt scene');
    fireEvent.click(screen.getByText('Advanced'));
    fireEvent.change(screen.getByLabelText('Character appearance reference (optional)'), {
      target: { files: [new File(['reference'], 'maya.png', { type: 'image/png' })] },
    });
    await screen.findByAltText('Character appearance reference');
    fireEvent.click(screen.getByLabelText('Edit route on preview'));
    fireEvent.click(screen.getByRole('button', {name: 'Draw new route'}));
    const route = screen.getByLabelText('Camera route drawing area');
    vi.spyOn(route, 'getBoundingClientRect').mockReturnValue({ left: 0, top: 0, width: 100, height: 100 } as DOMRect);
    fireEvent.click(route, { clientX: 40, clientY: 65 }); fireEvent.click(route, { clientX: 60, clientY: 65 });
    fireEvent.click(screen.getByRole('button', { name: 'Preview \u00b7 free' }));
    await waitFor(() => expect(api.preflight).toHaveBeenCalledOnce());
    expect(api.preflight).toHaveBeenCalledWith(expect.objectContaining({ character_reference_base64: 'data:image/png;base64,cmVmZXJlbmNl', character_reference_mime_type: 'image/png' }));
    await waitFor(() => expect(screen.getByRole('button', { name: /Generate video/ })).toBeEnabled());
    fireEvent.click(screen.getByRole('button', { name: 'Remove reference' }));
    expect(screen.getByRole('button', { name: /Generate video/ })).toBeDisabled();
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
    fireEvent.click(screen.getByRole('checkbox',{name:'Photographic finish'}));
    fireEvent.click(screen.getByText('Advanced'));
    const prompt = screen.getByRole('textbox', { name: 'Custom prompt (optional)' });
    expect(screen.getByText(/targets live-action architectural footage/)).toBeVisible();
    expect(screen.getByText(/Output estimate allows 10 seconds/)).toBeVisible();
    expect(prompt).toHaveAttribute('maxLength', '600');
    fireEvent.change(prompt, { target: { value: 'A woman walks her dog on the sidewalk.' } });
    fireEvent.click(screen.getByLabelText('Edit route on preview'));
    fireEvent.click(screen.getByRole('button', {name: 'Draw new route'}));
    const route = screen.getByLabelText('Camera route drawing area');
    vi.spyOn(route, 'getBoundingClientRect').mockReturnValue({ left: 0, top: 0, width: 100, height: 100 } as DOMRect);
    fireEvent.click(route, { clientX: 40, clientY: 65 });
    fireEvent.click(route, { clientX: 60, clientY: 65 });
    fireEvent.click(screen.getByRole('button', { name: 'Preview \u00b7 free' }));
    await waitFor(() => expect(api.preflight).toHaveBeenCalledOnce());
    expect(api.preflight).toHaveBeenCalledWith(expect.objectContaining({
      custom_prompt: 'A woman walks her dog on the sidewalk.', duration_seconds: 8,
    }));
    await waitFor(() => expect(screen.getByRole('button', { name: /Generate video/ })).toBeEnabled());
    fireEvent.click(screen.getByRole('checkbox', { name: 'Use only my prompt' }));
    expect(screen.getByRole('button', { name: /Generate video/ })).toBeDisabled();
    fireEvent.click(screen.getByRole('button', { name: 'Preview \u00b7 free' }));
    await waitFor(() => expect(api.preflight).toHaveBeenCalledTimes(2));
    expect(api.preflight).toHaveBeenLastCalledWith(expect.objectContaining({
      use_custom_prompt_only: true, custom_prompt: 'A woman walks her dog on the sidewalk.',
    }));
    await waitFor(() => expect(screen.getByRole('button', { name: /Generate video/ })).toBeEnabled());
    fireEvent.change(prompt, { target: { value: 'Warm evening light.' } });
    expect(screen.getByRole('button', { name: /Generate video/ })).toBeDisabled();
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
