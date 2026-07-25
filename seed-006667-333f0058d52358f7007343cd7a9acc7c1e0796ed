import { create } from 'zustand';
import { setSkipHistory } from '@/services/api';

// =============================================================================
// Undo / Redo Store — Command Pattern
// =============================================================================

export interface UndoableAction {
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
  undoStack: [],
  redoStack: [],
  isUndoing: false,
  isRedoing: false,
  historyVersion: 0,
  lastAppliedAction: null,
  _isSystemAction: false,
  _drawingInterceptor: null,

  pushAction: (action) =>
    set((state) => ({
      undoStack: [...state.undoStack, action].slice(-MAX_STACK_SIZE),
      redoStack: [], // clear redo on new action
    })),

  pushRedoAction: (action) =>
    set((state) => ({
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
    set({ isUndoing: true, _isSystemAction: true }); setSkipHistory(true);

    try {
      await action.undo();
      set((state) => ({
        undoStack: state.undoStack.slice(0, -1),
        redoStack: [...state.redoStack, action].slice(-MAX_STACK_SIZE),
        historyVersion: state.historyVersion + 1,
        lastAppliedAction: action,
      }));
    } finally {
      set({ isUndoing: false, _isSystemAction: false }); setSkipHistory(false);
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
    set({ isRedoing: true, _isSystemAction: true }); setSkipHistory(true);

    try {
      await action.redo();
      set((state) => ({
        redoStack: state.redoStack.slice(0, -1),
        undoStack: [...state.undoStack, action].slice(-MAX_STACK_SIZE),
        historyVersion: state.historyVersion + 1,
        lastAppliedAction: action,
      }));
    } finally {
      set({ isRedoing: false, _isSystemAction: false }); setSkipHistory(false);
    }
  },

  undoForZone: async (zoneId: string) => {
    const { undoStack, isUndoing, isRedoing } = get();
    if (isUndoing || isRedoing) return;

    // Find the most recent action for this zone (search from end)
    const idx = findLastIndex(undoStack, (a) => undoableActionMatchesZoneId(a, zoneId));
    if (idx === -1) return;

    const action = undoStack[idx];
    set({ isUndoing: true, _isSystemAction: true }); setSkipHistory(true);

    try {
      await action.undo();
      set((state) => ({
        undoStack: [...state.undoStack.slice(0, idx), ...state.undoStack.slice(idx + 1)],
        redoStack: [...state.redoStack, action].slice(-MAX_STACK_SIZE),
        historyVersion: state.historyVersion + 1,
        lastAppliedAction: action,
      }));
    } finally {
      set({ isUndoing: false, _isSystemAction: false }); setSkipHistory(false);
    }
  },

  redoForZone: async (zoneId: string) => {
    const { redoStack, isUndoing, isRedoing } = get();
    if (isUndoing || isRedoing) return;

    const idx = findLastIndex(redoStack, (a) => undoableActionMatchesZoneId(a, zoneId));
    if (idx === -1) return;

    const action = redoStack[idx];
    set({ isRedoing: true, _isSystemAction: true }); setSkipHistory(true);

    try {
      await action.redo();
      set((state) => ({
        redoStack: [...state.redoStack.slice(0, idx), ...state.redoStack.slice(idx + 1)],
        undoStack: [...state.undoStack, action].slice(-MAX_STACK_SIZE),
        historyVersion: state.historyVersion + 1,
        lastAppliedAction: action,
      }));
    } finally {
      set({ isRedoing: false, _isSystemAction: false }); setSkipHistory(false);
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
