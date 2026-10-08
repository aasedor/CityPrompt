import { fireEvent, renderHook } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { useUndoRedoKeyboard } from './useUndoRedoKeyboard';

const history = vi.hoisted(() => ({ undo: vi.fn(), redo: vi.fn() }));
vi.mock('@/store/undoRedo', () => ({
  useUndoRedoStore: (selector: (value: typeof history) => unknown) =>
    selector(history),
}));

describe('scene history keyboard isolation', () => {
  it('suspends scene undo/redo while a detail editor owns the keyboard and resumes after closing', () => {
    const { rerender, unmount } = renderHook(
      ({ paused }) => useUndoRedoKeyboard(paused),
      { initialProps: { paused: false } },
    );
    fireEvent.keyDown(window, { key: 'z', ctrlKey: true });
    expect(history.undo).toHaveBeenCalledTimes(1);
    rerender({ paused: true });
    fireEvent.keyDown(window, { key: 'z', ctrlKey: true });
    fireEvent.keyDown(window, { key: 'y', ctrlKey: true });
    expect(history.undo).toHaveBeenCalledTimes(1);
    expect(history.redo).not.toHaveBeenCalled();
    rerender({ paused: false });
    fireEvent.keyDown(window, { key: 'y', ctrlKey: true });
    expect(history.redo).toHaveBeenCalledTimes(1);
    unmount();
  });
});
