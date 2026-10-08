import { act, renderHook } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { useDetailPlacement } from './useDetailPlacement';
import type { ProjectDetails } from './projectBenches';

const initial: ProjectDetails = { version: 1, revision: 4, can_edit: true, benches: [], trees: [], props: [], surfaces: [] };
describe('persistent detail placement', () => {
  it('places different chosen items using the last saved revision and preserves existing details', async () => {
    const save = vi.fn(async (data: ProjectDetails) => ({ ...data, revision: data.revision + 1 }));
    const { result } = renderHook(() => useDetailPlacement(initial, save));
    act(() => result.current.choose('timber-bench'));
    await act(() => result.current.place([-114.1, 51.1]));
    expect(result.current.selected).toBe('timber-bench');
    act(() => result.current.choose('oak-2'));
    await act(() => result.current.place([-114.2, 51.2]));
    expect(save.mock.calls[1][0]).toMatchObject({ revision: 5, benches: [{ lng: -114.1, lat: 51.1 }], trees: [{ lng: -114.2, lat: 51.2, variant: 'oak-2' }], surfaces: [] });
    expect(result.current.selected).toBe('oak-2');
  });
  it('ignores a second click while saving and retains selection on failure', async () => {
    let reject!: (error: Error) => void;
    const save = vi.fn(() => new Promise<ProjectDetails>((_resolve, fail) => { reject = fail; }));
    const { result } = renderHook(() => useDetailPlacement(initial, save));
    act(() => result.current.choose('timber-bench'));
    let pending!: Promise<void>;
    act(() => { pending = result.current.place([-114, 51]); });
    await act(() => result.current.place([-115, 52]));
    expect(save).toHaveBeenCalledTimes(1);
    await act(async () => { reject(new Error('offline')); await pending; });
    expect(result.current.selected).toBe('timber-bench');
    expect(result.current.error).toBeTruthy();
    expect(result.current.saving).toBe(false);
  });
  it('does not write for a read-only account', async () => {
    const save = vi.fn();
    const { result } = renderHook(() => useDetailPlacement({ ...initial, can_edit: false }, save));
    act(() => result.current.choose('timber-bench'));
    await act(() => result.current.place([-114, 51]));
    expect(save).not.toHaveBeenCalled();
  });
});
