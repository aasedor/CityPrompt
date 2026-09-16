import { act, renderHook } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { useVideoRoutePreview } from './useVideoRoutePreview';
import type { VideoRouteCaptureResult } from './videoRouteControls';

const guide: VideoRouteCaptureResult = { keyframesBase64: ['start', 'end'], previewVideoBase64: 'local-guide', previewVideoMimeType: 'video/mp4' };

describe('local video guide ownership', () => {
  it('reuses a guide for the same scene but recaptures after a scene revision', async () => {
    const capture = vi.fn().mockResolvedValue(guide);
    const { result, rerender } = renderHook(({ signature }) => useVideoRoutePreview(signature), { initialProps: { signature: 'project:scene1:route1:frame1' } });
    await act(async () => { await result.current.prepare(capture); });
    await act(async () => { await result.current.prepare(capture); });
    expect(capture).toHaveBeenCalledTimes(1);
    rerender({ signature: 'project:scene2:route1:frame1' });
    await act(async () => { await result.current.prepare(capture); });
    expect(capture).toHaveBeenCalledTimes(2);
    expect(result.current.routeControls?.signature).toBe('project:scene2:route1:frame1');
  });

  it('deduplicates capture and rejects a late guide after the scene changes', async () => {
    let resolve!: (guide: VideoRouteCaptureResult) => void;
    const capture = vi.fn(() => new Promise<VideoRouteCaptureResult>(done => { resolve = done; }));
    const { result, rerender } = renderHook(({ signature }) => useVideoRoutePreview(signature), { initialProps: { signature: 'old-scene' } });
    let first!: Promise<VideoRouteCaptureResult>, second!: Promise<VideoRouteCaptureResult>;
    await act(async () => { first = result.current.prepare(capture); second = result.current.prepare(capture); });
    expect(first).toBe(second);
    expect(capture).toHaveBeenCalledTimes(1);
    rerender({ signature: 'edited-scene' });
    await expect(result.current.prepare(capture)).rejects.toThrow('previous preview');
    await act(async () => { resolve(guide); await expect(first).rejects.toThrow('design or route changed'); });
    expect(result.current.routeControls).toBeNull();
    expect(result.current.isPreparingControls).toBe(false);
  });

  it('allows a manual retry after capture fails', async () => {
    const capture = vi.fn().mockRejectedValueOnce(new Error('Context unavailable')).mockResolvedValue(guide);
    const { result } = renderHook(() => useVideoRoutePreview('scene'));
    await act(async () => { await expect(result.current.prepare(capture)).rejects.toThrow('Context unavailable'); });
    expect(capture).toHaveBeenCalledTimes(1);
    await act(async () => { await result.current.prepare(capture); });
    expect(result.current.routeControls?.previewVideoBase64).toBe('local-guide');
  });
});
