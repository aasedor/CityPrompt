import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { act, cleanup, renderHook } from '@testing-library/react';
import { useCollaboration } from './collaboration';

const socketConstructor = vi.fn();

beforeEach(() => {
  vi.useFakeTimers();
  socketConstructor.mockClear();
  vi.stubGlobal('WebSocket', socketConstructor);
});

afterEach(() => {
  cleanup();
  vi.useRealTimers();
  vi.unstubAllGlobals();
});

describe('paused live collaboration', () => {
  it.each([undefined, 'project-a', 'project-b'])(
    'reports unavailable without connecting for project %s',
    (projectId) => {
      const { result } = renderHook(() => useCollaboration(projectId, 'Alice'));
      expect(result.current.status).toBe('unavailable');
      expect(result.current.unavailableReason).toContain('Shared project access and saving remain available');
      expect(result.current.isConnected).toBe(false);
      expect(result.current.connectionId).toBeNull();
      expect(result.current.users).toEqual([]);
      expect(result.current.cursors.size).toBe(0);
      expect(socketConstructor).not.toHaveBeenCalled();
    },
  );

  it('never opens or reconnects after project changes, elapsed timers, or unmount', () => {
    const { rerender, unmount } = renderHook(
      ({ projectId, userName }) => useCollaboration(projectId, userName),
      { initialProps: { projectId: 'project-a', userName: 'Alice' } },
    );
    rerender({ projectId: 'project-b', userName: 'Bob' });
    act(() => vi.advanceTimersByTime(120_000));
    unmount();
    act(() => vi.advanceTimersByTime(120_000));
    expect(socketConstructor).not.toHaveBeenCalled();
    expect(vi.getTimerCount()).toBe(0);
  });

  it('does not broadcast edits or claim presence through the compatibility methods', () => {
    const { result } = renderHook(() => useCollaboration('project-a', 'Alice'));
    const onEdit = vi.fn();
    const onSelect = vi.fn();
    const onCamera = vi.fn();
    act(() => {
      result.current.onEdit(onEdit);
      result.current.onSelect(onSelect);
      result.current.onCamera(onCamera);
      result.current.sendEdit('private-building', { height_meters: 900 });
      result.current.sendSelect('private-building');
      result.current.sendCursor([1, 2, 3], [4, 5, 6]);
      result.current.setFollowing('another-student');
      vi.advanceTimersByTime(120_000);
    });
    expect(onEdit).not.toHaveBeenCalled();
    expect(onSelect).not.toHaveBeenCalled();
    expect(onCamera).not.toHaveBeenCalled();
    expect(socketConstructor).not.toHaveBeenCalled();
    expect(result.current.followingUserId).toBeNull();
    expect(result.current.users).toEqual([]);
    expect(result.current.cursors.size).toBe(0);
  });
});
