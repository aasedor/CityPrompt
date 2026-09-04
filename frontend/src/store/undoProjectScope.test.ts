import { beforeEach, describe, expect, it, vi } from 'vitest';
import { useUndoRedoStore } from './undoRedo';
import toast from 'react-hot-toast';

vi.mock('react-hot-toast', () => ({ default: { error: vi.fn() } }));

type Operation = 'undo' | 'redo' | 'undoForZone' | 'redoForZone';
const operations: Operation[] = ['undo', 'redo', 'undoForZone', 'redoForZone'];
const store = useUndoRedoStore.getState;

function defer() {
  let resolve!: () => void;
  let reject!: (error: unknown) => void;
  const promise = new Promise<void>((yes, no) => { resolve = yes; reject = no; });
  return { promise, resolve, reject };
}

function queueOperation(projectId: string, operation: Operation, promise: Promise<void>) {
  const action = { projectId, zoneId: projectId, label: 'Pending change', undo: () => promise, redo: () => promise };
  if (operation.startsWith('redo')) store().pushRedoAction(action);
  else store().pushAction(action);
  return operation.endsWith('ForZone')
    ? store()[operation as 'undoForZone' | 'redoForZone'](projectId)
    : store()[operation as 'undo' | 'redo']();
}

describe('project-scoped undo', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useUndoRedoStore.setState({ projectId: null, undoStack: [], redoStack: [], isUndoing: false, isRedoing: false,
      _isSystemAction: false, scopeVersion: 0, lastAppliedAction: null, _drawingInterceptor: null });
  });

  it('cannot undo another project after navigation', async () => {
    const undo = vi.fn();
    const store = useUndoRedoStore.getState;
    store().setProjectScope('first');
    store().pushAction({ projectId: 'first', label: 'Draw house', undo, redo: vi.fn() });
    store().setProjectScope('second');
    await store().undo();
    expect(undo).not.toHaveBeenCalled();
    expect(store().redoStack).toEqual([]);
  });

  it('ignores a late save action from the previous project', () => {
    const store = useUndoRedoStore.getState;
    store().setProjectScope('second');
    store().pushAction({ projectId: 'first', label: 'Late save', undo: vi.fn(), redo: vi.fn() });
    expect(store().undoStack).toEqual([]);
  });

  it('does not transfer a completed asynchronous undo into the next project', async () => {
    let finish!: () => void;
    const store = useUndoRedoStore.getState;
    store().setProjectScope('first');
    store().pushAction({ projectId: 'first', label: 'Draw', undo: () => new Promise<void>((resolve) => { finish = resolve; }), redo: vi.fn() });
    const pending = store().undo();
    store().setProjectScope('second');
    finish();
    await pending;
    expect(store().redoStack).toEqual([]);
    expect(store().lastAppliedAction).toBeNull();
    expect(store().isUndoing).toBe(false);
  });

  it.each(operations)('a pending %s does not suppress a new project edit', async (operation) => {
    const first = defer();
    store().setProjectScope('first');
    const pending = queueOperation('first', operation, first.promise);
    expect(store()._isSystemAction).toBe(true);
    store().setProjectScope('second');
    expect(store().isUndoing).toBe(false);
    expect(store().isRedoing).toBe(false);
    expect(store()._isSystemAction).toBe(false);
    const edit = { projectId: 'second', label: 'Draw park', undo: vi.fn(), redo: vi.fn() };
    // This is the guard used by normal mutation success callbacks.
    if (!store()._isSystemAction) store().pushAction(edit);
    first.resolve();
    await pending;
    expect(store().undoStack).toEqual([edit]);
    expect(store().redoStack).toEqual([]);
    expect(store().lastAppliedAction).toBeNull();
  });

  it.each(operations.flatMap((operation) => [
    { operation, failed: false }, { operation, failed: true },
  ]))('old $operation completion (failed=$failed) cannot clear a new project operation', async ({ operation, failed }) => {
    const first = defer();
    const second = defer();
    store().setProjectScope('first');
    const oldPending = queueOperation('first', operation, first.promise);
    store().setProjectScope('second');
    const newPending = queueOperation('second', operation, second.promise);
    expect(store()._isSystemAction).toBe(true);
    if (failed) first.reject({ response: { status: 409 } });
    else first.resolve();
    await oldPending;
    expect(store()._isSystemAction).toBe(true);
    expect(store().isUndoing).toBe(!operation.startsWith('redo'));
    expect(store().isRedoing).toBe(operation.startsWith('redo'));
    expect(toast.error).not.toHaveBeenCalled();
    second.resolve();
    await newPending;
    expect(store()._isSystemAction).toBe(false);
    expect(store().isUndoing).toBe(false);
    expect(store().isRedoing).toBe(false);
    expect(store().lastAppliedAction?.projectId).toBe('second');
  });
});
