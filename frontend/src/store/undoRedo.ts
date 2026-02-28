import { create } from 'zustand';

// =============================================================================
// Undo / Redo Store — Command Pattern
// =============================================================================

export interface UndoableAction {
  label: string;
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
  /** When true, mutation onSuccess callbacks should NOT push new actions */
  _isSystemAction: boolean;
  /** Optional interceptor for drawing-mode vertex undo/redo */
  _drawingInterceptor: DrawingInterceptor | null;
  pushAction: (action: UndoableAction) => void;
  undo: () => Promise<void>;
  redo: () => Promise<void>;
  clearHistory: (projectId?: string) => void;
  setDrawingInterceptor: (interceptor: DrawingInterceptor) => void;
  clearDrawingInterceptor: () => void;
}

export const useUndoRedoStore = create<UndoRedoState>((set, get) => ({
  undoStack: [],
  redoStack: [],
  isUndoing: false,
  isRedoing: false,
  _isSystemAction: false,
  _drawingInterceptor: null,

  pushAction: (action) =>
    set((state) => ({
      undoStack: [...state.undoStack, action].slice(-MAX_STACK_SIZE),
      redoStack: [], // clear redo on new action
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
    set({ isUndoing: true, _isSystemAction: true });

    try {
      await action.undo();
      set((state) => ({
        undoStack: state.undoStack.slice(0, -1),
        redoStack: [...state.redoStack, action].slice(-MAX_STACK_SIZE),
      }));
    } finally {
      set({ isUndoing: false, _isSystemAction: false });
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
    set({ isRedoing: true, _isSystemAction: true });

    try {
      await action.redo();
      set((state) => ({
        redoStack: state.redoStack.slice(0, -1),
        undoStack: [...state.undoStack, action].slice(-MAX_STACK_SIZE),
      }));
    } finally {
      set({ isRedoing: false, _isSystemAction: false });
    }
  },

  clearHistory: () => set({ undoStack: [], redoStack: [] }),

  setDrawingInterceptor: (interceptor) => set({ _drawingInterceptor: interceptor }),
  clearDrawingInterceptor: () => set({ _drawingInterceptor: null }),
}));

// Selectors — account for drawing interceptor having its own undo/redo capability
export const selectCanUndo = (state: UndoRedoState) =>
  (state._drawingInterceptor?.canUndo() ||
    (state.undoStack.length > 0 && !state.isUndoing && !state.isRedoing));
export const selectCanRedo = (state: UndoRedoState) =>
  (state._drawingInterceptor?.canRedo() ||
    (state.redoStack.length > 0 && !state.isUndoing && !state.isRedoing));
