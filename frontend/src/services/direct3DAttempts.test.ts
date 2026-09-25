import type { AxiosInstance } from 'axios';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { createDirect3DAttemptClient, type ImageAttempt } from './direct3DAttempts';

const ROOT = '/api/v1/render/direct-3d-attempts';
const job = (status: ImageAttempt['status'], key = 'saved-key'): ImageAttempt => ({
  id: 'attempt-1', idempotency_key: key, project_id: 'project', status, style: 'photorealistic', model: 'test',
  created_at: '2026-09-23T18:00:00Z', finished_at: null, error: null,
});
function setup() {
  const get = vi.fn(); const post = vi.fn();
  const account = vi.fn(() => 'student');
  let clock = 0;
  const client = createDirect3DAttemptClient({ api: { get, post } as unknown as AxiosInstance,
    storage: () => localStorage, account, now: () => clock, wait: async ms => { clock += ms; } });
  return { client, get, post, account };
}

describe('saved image attempts', () => {
  beforeEach(() => localStorage.clear());

  it('submits once, polls the same attempt and returns its exact result', async () => {
    const f = setup();
    let key = '';
    f.get.mockResolvedValueOnce({ data: { enabled: true, images_enabled: true } })
      .mockImplementationOnce(async () => ({ data: job('running', key) })).mockImplementationOnce(async () => ({ data: job('completed', key) }))
      .mockImplementation(async () => ({ data: { response: { image_base64: 'saved-pixels' }, attempt: job('completed', key) } }));
    f.post.mockImplementation(async (_url, _body, config) => { key = config.headers['Idempotency-Key']; return { data: job('queued', key) }; });
    expect(await f.client.generate({ project_id: 'project' })).toEqual({ image_base64: 'saved-pixels' });
    expect(f.post).toHaveBeenCalledTimes(1);
    expect(f.post.mock.calls[0][0]).toBe(ROOT);
    expect(f.get.mock.calls.map(call => call[0])).toEqual([`${ROOT}/capabilities`, `${ROOT}/attempt-1`, `${ROOT}/attempt-1`, `${ROOT}/attempt-1/result`]);
    expect(localStorage.length).toBe(0);
  });

  it('a lost polling connection keeps the attempt and blocks a second paid submission after reload', async () => {
    const f = setup();
    f.get.mockResolvedValueOnce({ data: { enabled: true, images_enabled: true } }).mockRejectedValueOnce(new Error('offline'));
    f.post.mockImplementation(async (_url, _body, config) => ({ data: job('running', config.headers['Idempotency-Key']) }));
    await expect(f.client.generate({ project_id: 'project' })).rejects.toThrow('attempt is saved');
    const reloaded = setup();
    reloaded.get.mockResolvedValue({ data: { enabled: true, images_enabled: true } });
    await expect(reloaded.client.generate({ project_id: 'project' })).rejects.toThrow('Recover recent images');
    expect(reloaded.post).not.toHaveBeenCalled();
    expect(f.post).toHaveBeenCalledTimes(1);
  });

  it('reuses the idempotency key after an ambiguous submission instead of creating another', async () => {
    const f = setup();
    f.get.mockResolvedValue({ data: { enabled: true, images_enabled: true } });
    f.post.mockRejectedValue(new Error('lost submission response'));
    await expect(f.client.generate({ project_id: 'project' })).rejects.toThrow();
    await expect(f.client.generate({ project_id: 'project' })).rejects.toThrow();
    expect(f.post.mock.calls[0][2].headers['Idempotency-Key']).toBe(f.post.mock.calls[1][2].headers['Idempotency-Key']);
  });

  it('does not fall back to the synchronous paid route on capability failure', async () => {
    const f = setup();
    f.get.mockRejectedValue(new Error('offline'));
    await expect(f.client.generate({ project_id: 'project' })).rejects.toThrow('offline');
    expect(f.post).not.toHaveBeenCalled();
  });

  it('preserves the stopped job message and requires an explicit new Generate action', async () => {
    const f = setup();
    f.get.mockResolvedValue({ data: { enabled: true, images_enabled: true } });
    f.post.mockImplementation(async (_url, _body, config) => ({ data: { ...job('unknown', config.headers['Idempotency-Key']), error: { message: 'Credits restored; provider cost unknown.' } } }));
    await expect(f.client.generate({ project_id: 'project' })).rejects.toThrow('Credits restored');
    expect(localStorage.length).toBe(0);
    expect(f.post).toHaveBeenCalledTimes(1);
  });

  it('times out polling without re-posting or forgetting a saved attempt', async () => {
    const f = setup();
    f.get.mockResolvedValueOnce({ data: { enabled: true, images_enabled: true } }).mockResolvedValue({ data: job('running') });
    f.post.mockResolvedValue({ data: job('queued') });
    await expect(f.client.generate({ project_id: 'project' })).rejects.toThrow('may still be running');
    expect(f.post).toHaveBeenCalledTimes(1);
    expect(localStorage.length).toBe(1);
  });

  it('drops a result if the signed-in account changes during recovery', async () => {
    const f = setup();
    f.get.mockImplementation(async () => { f.account.mockReturnValue('another-student'); return { data: { response: { private: true } } }; });
    await expect(f.client.recover(job('completed'))).rejects.toThrow('account changed');
  });
});
