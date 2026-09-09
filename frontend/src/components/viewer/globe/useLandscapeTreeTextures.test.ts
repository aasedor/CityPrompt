import { renderHook, waitFor } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import * as THREE from 'three';
import { landscapeFoliageFallback, useLandscapeTreeTextures } from './useLandscapeTreeTextures';

describe('landscape texture recovery', () => {
  it('keeps usable foliage when every optional texture fails, sharing duplicate requests', async () => {
    const load = vi.spyOn(THREE.TextureLoader.prototype, 'loadAsync').mockRejectedValue(new Error('404'));
    const warn = vi.spyOn(console, 'warn').mockImplementation(() => {});
    const first = renderHook(() => useLandscapeTreeTextures());
    await waitFor(() => expect(warn).toHaveBeenCalledTimes(3));
    expect(first.result.current).toHaveLength(7);
    expect(first.result.current.every(texture => texture === landscapeFoliageFallback())).toBe(true);
    const second = renderHook(() => useLandscapeTreeTextures());
    await waitFor(() => expect(second.result.current).toHaveLength(7));
    expect(load).toHaveBeenCalledTimes(3);
    first.unmount(); second.unmount();
    vi.restoreAllMocks();
  });
});
