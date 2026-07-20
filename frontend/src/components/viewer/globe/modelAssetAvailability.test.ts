import { afterEach, describe, expect, it, vi } from 'vitest';

import {
  clearModelAssetAvailabilityCacheForTests,
  modelAssetAvailable,
} from './modelAssetAvailability';

describe('modelAssetAvailable', () => {
  afterEach(() => {
    clearModelAssetAvailabilityCacheForTests();
  });

  it('deduplicates HEAD checks and rejects a stale immutable key', async () => {
    const fetcher = vi.fn(async () => ({ status: 404 }) as Response);

    const [first, second] = await Promise.all([
      modelAssetAvailable('/api/v1/files/missing.glb', fetcher),
      modelAssetAvailable('/api/v1/files/missing.glb', fetcher),
    ]);

    expect(first).toBe(false);
    expect(second).toBe(false);
    expect(fetcher).toHaveBeenCalledTimes(1);
    expect(fetcher).toHaveBeenCalledWith('/api/v1/files/missing.glb', {
      method: 'HEAD',
      cache: 'force-cache',
      credentials: 'same-origin',
    });
  });

  it('allows a confirmed model and an older server without HEAD support', async () => {
    const fetcher = vi.fn()
      .mockResolvedValueOnce({ status: 200 } as Response)
      .mockResolvedValueOnce({ status: 405 } as Response);

    await expect(modelAssetAvailable('/api/v1/files/present.glb', fetcher)).resolves.toBe(true);
    await expect(modelAssetAvailable('/legacy/model.glb', fetcher)).resolves.toBe(true);
  });

  it('lets the GLTF loader retry after a transient HEAD network failure', async () => {
    const fetcher = vi.fn(async () => { throw new Error('offline'); });

    await expect(modelAssetAvailable('/api/v1/files/transient.glb', fetcher)).resolves.toBe(true);
  });
});
