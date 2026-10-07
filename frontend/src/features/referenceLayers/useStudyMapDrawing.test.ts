import { act, renderHook } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { useViewerStore } from '@/store';
import { useStudyMapDrawing } from './useStudyMapDrawing';

beforeEach(() => useViewerStore.getState().setActiveSitePlannerTool(null));
describe('globe study drawing bridge', () => {
  it('marks study drawings and completes them through the study callback', () => {
    const { result, unmount } = renderHook(() => useStudyMapDrawing('trial'));
    const accept = vi.fn().mockReturnValue(true), cancelled = vi.fn();
    act(() => result.current.controls.begin(accept, cancelled));
    expect(useViewerStore.getState().activeToolProperties).toMatchObject({ cartography_study: true });
    const points = [[-114.1, 51.05], [-114.09, 51.05], [-114.1, 51.06]];
    act(() => { expect(result.current.complete(points)).toBe(true); });
    expect(accept).toHaveBeenCalledWith(points);
    expect(cancelled).not.toHaveBeenCalled();
    expect(useViewerStore.getState().activeSitePlannerTool).toBeNull();
    expect(result.current.complete(points)).toBe(false);
    unmount();
  });
  it('keeps rejected outlines editable, cancels with Escape/tool changes and clears on close', () => {
    const { result, unmount } = renderHook(() => useStudyMapDrawing('trial'));
    const accept = vi.fn().mockReturnValue(false), cancelled = vi.fn();
    act(() => result.current.controls.begin(accept, cancelled));
    act(() => { expect(result.current.complete([])).toBe(false); });
    expect(useViewerStore.getState().activeSitePlannerTool).toBe('development_area');
    act(() => window.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' })));
    expect(cancelled).toHaveBeenCalledOnce();
    act(() => result.current.controls.begin(accept, cancelled));
    act(() => useViewerStore.getState().setActiveSitePlannerTool('site_boundary'));
    expect(cancelled).toHaveBeenCalledTimes(2);
    expect(useViewerStore.getState().activeSitePlannerTool).toBe('site_boundary');
    act(() => result.current.controls.begin(accept, cancelled));
    unmount();
    expect(useViewerStore.getState().activeSitePlannerTool).toBeNull();
    expect(useViewerStore.getState().activeToolProperties).toBeNull();
  });
});
