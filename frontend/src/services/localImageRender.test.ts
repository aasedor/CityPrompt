import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { rendersApi } from './api';
import { comfyTrialsApi, type ComfyJob } from './comfyTrials';
import { renderLocalImage } from './localImageRender';
vi.mock('./api', () => ({ rendersApi: { save: vi.fn() } }));
vi.mock('./comfyTrials', () => ({ comfyTrialsApi: { list: vi.fn(), generate: vi.fn(), recover: vi.fn() } }));
const source = { id: 'source', image_url: '/source.png' };
const job = { id: 'job', source_render_id: 'source', preset: 'flux-klein', kind: 'image', status: 'queued', error: null } as ComfyJob;
const result = { id: 'output', image_url: '/output.png' };
const options = { projectId: 'p', model: 'flux-klein' as const, imageBase64: 'data:image/png;base64,pixels', prompt: 'Warm daylight.' };
beforeEach(() => {
  vi.clearAllMocks(); vi.useFakeTimers(); localStorage.clear();
  vi.mocked(rendersApi.save).mockResolvedValue(source as never);
  vi.mocked(comfyTrialsApi.list).mockResolvedValue({jobs:[]});
  vi.mocked(comfyTrialsApi.generate).mockResolvedValue(job);
  vi.mocked(comfyTrialsApi.recover).mockResolvedValue({...job,status:'complete',result:result as never});
});
afterEach(() => vi.useRealTimers());
describe('integrated local image engines', () => {
  it('saves the current source, submits once, recovers and returns the actual saved output', async () => {
    const pending = renderLocalImage(options);
    await vi.advanceTimersByTimeAsync(5000);
    await expect(pending).resolves.toEqual(result);
    expect(rendersApi.save).toHaveBeenCalledWith('p', expect.objectContaining({image_base64:'pixels',model:'3d-capture'}));
    expect(comfyTrialsApi.generate).toHaveBeenCalledExactlyOnceWith(expect.objectContaining({source_render_id:'source',preset:'flux-klein',prompt:'Warm daylight.'}));
    expect(comfyTrialsApi.recover).toHaveBeenCalledWith('p','job');
  });
  it('resumes an active job without another GPU submission', async () => {
    vi.mocked(comfyTrialsApi.list).mockResolvedValue({jobs:[job]});
    const pending = renderLocalImage(options);
    await vi.advanceTimersByTimeAsync(5000);
    await expect(pending).resolves.toEqual(result);
    expect(comfyTrialsApi.generate).not.toHaveBeenCalled();
  });
  it('keeps recovering a quality render beyond fifteen minutes without resubmitting', async () => {
    let checks = 0;
    vi.mocked(comfyTrialsApi.recover).mockImplementation(async () =>
      ++checks < 192 ? job : {...job,status:'complete',result:result as never});
    const pending = expect(renderLocalImage(options)).resolves.toEqual(result);
    await vi.advanceTimersByTimeAsync(16 * 60 * 1000);
    await pending;
    expect(comfyTrialsApi.generate).toHaveBeenCalledTimes(1);
    expect(comfyTrialsApi.recover).toHaveBeenCalledTimes(192);
  });
  it('reports a failed local job without replacement', async () => {
    vi.mocked(comfyTrialsApi.generate).mockResolvedValue({...job,status:'failed',error:'GPU memory'});
    await expect(renderLocalImage(options)).rejects.toThrow('GPU memory');
    expect(comfyTrialsApi.recover).not.toHaveBeenCalled();
    expect(comfyTrialsApi.generate).toHaveBeenCalledTimes(1);
  });
});
