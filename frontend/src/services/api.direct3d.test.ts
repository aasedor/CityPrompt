import { afterEach, describe, expect, it, vi } from 'vitest';

import { api, rendersApi } from './api';

describe('Direct 3D API timeout contract', () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('outlives the provider timeout and backend post-processing window', async () => {
    const request = {} as Parameters<typeof rendersApi.generateDirect3D>[0];
    const post = vi.spyOn(api, 'post').mockResolvedValue({ data: { ok: true } });

    await rendersApi.generateDirect3D(request);

    expect(post).toHaveBeenCalledWith(
      '/api/v1/render/generate-direct-3d',
      request,
      { timeout: 420_000 },
    );
  });
});
