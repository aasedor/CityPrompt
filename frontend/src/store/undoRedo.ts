import { create } from 'zustand';
import toast from 'react-hot-toast';

// =============================================================================
// Undo / Redo Store — Command Pattern
// =============================================================================

export interface UndoableAction {
  projectId?: string;
  label: string;
  zoneId?: string;
  getZoneId?: () => string | null;
  matchesZoneId?: (zoneId: string) => boolean;
  undo: () => Promise<void>;
  redo: () => Promise<void>;
}

/** Interceptor that takes priority over the normal undo/redo stack (e.g. zone vertex drawing). */
export interface DrawingInterceptor {
  undo: () => boolean;  // returns true if handled
  redo: () => boolean;
  canUndo: () => boolean;
  canRedo: () => boolean;
}

const MAX_STACK_SIZE = 50;

interface UndoRedoState {
  projectId: string | null;
  scopeVersion: number;
  setProjectScope: (projectId: string | null) => void;
  undoStack: UndoableAction[];
  redoStack: UndoableAction[];
  isUndoing: boolean;
  isRedoing: boolean;
  historyVersion: number;
  lastAppliedAction: UndoableAction | null;
  /** When true, mutation onSuccess callbacks should NOT push new actions */
  _isSystemAction: boolean;
  /** Optional interceptor for drawing-mode vertex undo/redo */
  _drawingInterceptor: DrawingInterceptor | null;
  pushAction: (action: UndoableAction) => void;
  pushRedoAction: (action: UndoableAction) => void;
  undo: () => Promise<void>;
  redo: () => Promise<void>;
  /** Undo the most recent action for a specific zone */
  undoForZone: (zoneId: string) => Promise<void>;
  /** Redo the most recent undone action for a specific zone */
  redoForZone: (zoneId: string) => Promise<void>;
  clearHistory: (projectId?: string) => void;
  setDrawingInterceptor: (interceptor: DrawingInterceptor) => void;
  clearDrawingInterceptor: () => void;
}

export const useUndoRedoStore = create<UndoRedoState>((set, get) => ({
  projectId: null,
  scopeVersion: 0,
  setProjectScope: (projectId) => {
    if (projectId === get().projectId) return;
    set((state) => ({
      projectId,
      scopeVersion: state.scopeVersion + 1,
      undoStack: [], redoStack: [], lastAppliedAction: null,
      isUndoing: false, isRedoing: false, _isSystemAction: false,
      _drawingInterceptor: null,
    }));
  },
  undoStack: [],
  redoStack: [],
  isUndoing: false,
  isRedoing: false,
  historyVersion: 0,
  lastAppliedAction: null,
  _isSystemAction: false,
  _drawingInterceptor: null,

  pushAction: (action) =>
    set((state) => action.projectId && state.projectId !== action.projectId ? state : ({
      undoStack: [...state.undoStack, action].slice(-MAX_STACK_SIZE),
      redoStack: [], // clear redo on new action
    })),

  pushRedoAction: (action) =>
    set((state) => action.projectId && state.projectId !== action.projectId ? state : ({
      redoStack: [...state.redoStack, action].slice(-MAX_STACK_SIZE),
    })),

  undo: async () => {
    // Drawing interceptor takes priority (e.g. removing last placed vertex)
    const interceptor = get()._drawingInterceptor;
    if (interceptor?.canUndo()) {
      interceptor.undo();
      return;
    }

    const { undoStack, isUndoing, isRedoing } = get();
    if (isUndoing || isRedoing || undoStack.length === 0) return;

    const action = undoStack[undoStack.length - 1];
    const operationScope = get().scopeVersion;
    set({ isUndoing: true, _isSystemAction: true });

    try {
      await action.undo();
      if (get().scopeVersion !== operationScope) return;
      set((state) => ({
        undoStack: state.undoStack.slice(0, -1),
        redoStack: [...state.redoStack, action].slice(-MAX_STACK_SIZE),
        historyVersion: state.historyVersion + 1,
        lastAppliedAction: action,
      }));
    } catch (error) {
      if (get().scopeVersion !== operationScope) return;
      const status = (error as { response?: { status?: number } })?.response?.status;
      toast.error(status === 409
        ? 'Another session changed this drawing. Refresh the plan before trying again.'
        : 'This change could not be undone or redone. Your history is kept; please try again.');
    } finally {
      if (get().scopeVersion === operationScope) {
        set({ isUndoing: false, _isSystemAction: false });
      }
    }
  },

  redo: async () => {
    // Drawing interceptor takes priority (e.g. re-adding a removed vertex)
    const interceptor = get()._drawingInterceptor;
    if (interceptor?.canRedo()) {
      interceptor.redo();
      return;
    }

    const { redoStack, isUndoing, isRedoing } = get();
    if (isUndoing || isRedoing || redoStack.length === 0) return;

    const action = redoStack[redoStack.length - 1];
    const operationScope = get().scopeVersion;
    set({ isRedoing: true, _isSystemAction: true });

    try {
      await action.redo();
      if (get().scopeVersion !== operationScope) return;
      set((state) => ({
        redoStack: state.redoStack.slice(0, -1),
        undoStack: [...state.undoStack, action].slice(-MAX_STACK_SIZE),
        historyVersion: state.historyVersion + 1,
        lastAppliedAction: action,
      }));
    } catch (error) {
      if (get().scopeVersion !== operationScope) return;
      const status = (error as { response?: { status?: number } })?.response?.status;
      toast.error(status === 409
        ? 'Another session changed this drawing. Refresh the plan before trying again.'
        : 'This change could not be undone or redone. Your history is kept; please try again.');
    } finally {
      if (get().scopeVersion === operationScope) {
        set({ isRedoing: false, _isSystemAction: false });
      }
    }
  },

  undoForZone: async (zoneId: string) => {
    const { undoStack, isUndoing, isRedoing } = get();
    if (isUndoing || isRedoing) return;

    // Find the most recent action for this zone (search from end)
    const idx = findLastIndex(undoStack, (a) => undoableActionMatchesZoneId(a, zoneId));
    if (idx === -1) return;

    const action = undoStack[idx];
    const operationScope = get().scopeVersion;
    set({ isUndoing: true, _isSystemAction: true });

    try {
      await action.undo();
      if (get().scopeVersion !== operationScope) return;
      set((state) => ({
        undoStack: [...state.undoStack.slice(0, idx), ...state.undoStack.slice(idx + 1)],
        redoStack: [...state.redoStack, action].slice(-MAX_STACK_SIZE),
        historyVersion: state.historyVersion + 1,
        lastAppliedAction: action,
      }));
    } catch (error) {
      if (get().scopeVersion !== operationScope) return;
      const status = (error as { response?: { status?: number } })?.response?.status;
      toast.error(status === 409
        ? 'Another session changed this drawing. Refresh the plan before trying again.'
        : 'This change could not be undone or redone. Your history is kept; please try again.');
    } finally {
      if (get().scopeVersion === operationScope) {
        set({ isUndoing: false, _isSystemAction: false });
      }
    }
  },

  redoForZone: async (zoneId: string) => {
    const { redoStack, isUndoing, isRedoing } = get();
    if (isUndoing || isRedoing) return;

    const idx = findLastIndex(redoStack, (a) => undoableActionMatchesZoneId(a, zoneId));
    if (idx === -1) return;

    const action = redoStack[idx];
    const operationScope = get().scopeVersion;
    set({ isRedoing: true, _isSystemAction: true });

    try {
      await action.redo();
      if (get().scopeVersion !== operationScope) return;
      set((state) => ({
        redoStack: [...state.redoStack.slice(0, idx), ...state.redoStack.slice(idx + 1)],
        undoStack: [...state.undoStack, action].slice(-MAX_STACK_SIZE),
        historyVersion: state.historyVersion + 1,
        lastAppliedAction: action,
      }));
    } catch (error) {
      if (get().scopeVersion !== operationScope) return;
      const status = (error as { response?: { status?: number } })?.response?.status;
      toast.error(status === 409
        ? 'Another session changed this drawing. Refresh the plan before trying again.'
        : 'This change could not be undone or redone. Your history is kept; please try again.');
    } finally {
      if (get().scopeVersion === operationScope) {
        set({ isRedoing: false, _isSystemAction: false });
      }
    }
  },

  clearHistory: () => set({ undoStack: [], redoStack: [], lastAppliedAction: null }),

  setDrawingInterceptor: (interceptor) => set({ _drawingInterceptor: interceptor }),
  clearDrawingInterceptor: () => set({ _drawingInterceptor: null }),
}));

export function getUndoableActionZoneId(action: UndoableAction): string | null {
  return action.getZoneId?.() ?? action.zoneId ?? null;
}

export function undoableActionMatchesZoneId(action: UndoableAction, zoneId: string): boolean {
  return action.matchesZoneId?.(zoneId) ?? getUndoableActionZoneId(action) === zoneId;
}

function findLastIndex<T>(arr: T[], predicate: (item: T) => boolean): number {
  for (let i = arr.length - 1; i >= 0; i--) {
    if (predicate(arr[i])) return i;
  }
  return -1;
}

// Selectors — account for drawing interceptor having its own undo/redo capability
export const selectCanUndo = (state: UndoRedoState) =>
  (state._drawingInterceptor?.canUndo() ||
    (state.undoStack.length > 0 && !state.isUndoing && !state.isRedoing));
export const selectCanRedo = (state: UndoRedoState) =>
  (state._drawingInterceptor?.canRedo() ||
    (state.redoStack.length > 0 && !state.isUndoing && !state.isRedoing));

export const selectCanUndoForZone = (zoneId: string | null) => (state: UndoRedoState) =>
  !!zoneId && !state.isUndoing && !state.isRedoing && state.undoStack.some((a) => undoableActionMatchesZoneId(a, zoneId));
export const selectCanRedoForZone = (zoneId: string | null) => (state: UndoRedoState) =>
  !!zoneId && !state.isUndoing && !state.isRedoing && state.redoStack.some((a) => undoableActionMatchesZoneId(a, zoneId));
