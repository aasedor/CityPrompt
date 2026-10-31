import { fireEvent, renderHook } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { useUndoRedoKeyboard } from './useUndoRedoKeyboard';

const history = vi.hoisted(() => ({ undo: vi.fn(), redo: vi.fn() }));
vi.mock('@/store/undoRedo', () => ({
  useUndoRedoStore: (selector: (value: typeof history) => unknown) =>
    selector(history),
}));

beforeEach(() => vi.clearAllMocks());

function shortcut(init: KeyboardEventInit, target: EventTarget = window) {
  const event = new KeyboardEvent('keydown', { bubbles: true, cancelable: true, ...init });
  target.dispatchEvent(event);
  return event;
}

describe('scene history keyboard isolation', () => {
  it.each([
    { key: 'Z', ctrlKey: true, shiftKey: true },
    { key: 'Z', metaKey: true, shiftKey: true },
    { key: 'Y', ctrlKey: true },
    { key: 'Y', metaKey: true },
  ])('redos with the browser uppercase keyboard event %j', init => {
    renderHook(() => useUndoRedoKeyboard());
    const event = shortcut(init);
    expect(history.redo).toHaveBeenCalledTimes(1);
    expect(history.undo).not.toHaveBeenCalled();
    expect(event.defaultPrevented).toBe(true);
  });

  it('undoes an uppercase Z without Shift, as with Caps Lock', () => {
    renderHook(() => useUndoRedoKeyboard());
    const event = shortcut({ key: 'Z', ctrlKey: true });
    expect(history.undo).toHaveBeenCalledTimes(1);
    expect(history.redo).not.toHaveBeenCalled();
    expect(event.defaultPrevented).toBe(true);
  });

  it.each(['input', 'textarea', 'contenteditable'])('leaves %s editing shortcuts to the browser', tag => {
    const target = document.createElement(tag === 'contenteditable' ? 'div' : tag);
    if (tag === 'contenteditable') Object.defineProperty(target, 'isContentEditable', { value: true });
    document.body.appendChild(target);
    try {
      renderHook(() => useUndoRedoKeyboard());
      const event = shortcut({ key: 'Z', ctrlKey: true, shiftKey: true }, target);
      expect(history.undo).not.toHaveBeenCalled();
      expect(history.redo).not.toHaveBeenCalled();
      expect(event.defaultPrevented).toBe(false);
    } finally {
      target.remove();
    }
  });

  it.each([
    { key: 'Z', shiftKey: true }, { key: 'Y' },
    { key: 'Z', shiftKey: true, altKey: true }, { key: 'q', ctrlKey: true },
  ])('leaves unrelated or unmodified keys untouched: %j', init => {
    renderHook(() => useUndoRedoKeyboard());
    const event = shortcut(init);
    expect(history.undo).not.toHaveBeenCalled();
    expect(history.redo).not.toHaveBeenCalled();
    expect(event.defaultPrevented).toBe(false);
  });

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
    shortcut({ key: 'Z', ctrlKey: true, shiftKey: true });
    shortcut({ key: 'Y', metaKey: true });
    expect(history.undo).toHaveBeenCalledTimes(1);
    expect(history.redo).not.toHaveBeenCalled();
    rerender({ paused: false });
    fireEvent.keyDown(window, { key: 'y', ctrlKey: true });
    expect(history.redo).toHaveBeenCalledTimes(1);
    unmount();
  });
});
