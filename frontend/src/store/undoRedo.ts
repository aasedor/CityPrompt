import { create } from 'zustand';

// =============================================================================
// Undo / Redo Store — Command Pattern
// =============================================================================

export interface UndoableAction {
  label: string;
  undo: () => Promise<void>;
  redo: () => Promise<void>;
}

const MAX_STACK_SIZE = 50;

interface UndoRedoState {
  undoStack: UndoableAction[];
  redoStack: UndoableAction[];
  isUndoing: boolean;
  isRedoing: boolean;
  /** When true, mutation onSuccess callbacks should NOT push new actions */
  _isSystemAction: boolean;
  pushAction: (action: UndoableAction) => void;
  undo: () => Promise<void>;
  redo: () => Promise<void>;
  clearHistory: (projectId?: string) => void;
}

export const useUndoRedoStore = create<UndoRedoState>((set, get) => ({
  undoStack: [],
  redoStack: [],
  isUndoing: false,
  isRedoing: false,
  _isSystemAction: false,

  pushAction: (action) =>
    set((state) => ({
      undoStack: [...state.undoStack, action].slice(-MAX_STACK_SIZE),
      redoStack: [], // clear redo on new action
    })),

  undo: async () => {
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
}));

// Selectors
export const selectCanUndo = (state: UndoRedoState) =>
  state.undoStack.length > 0 && !state.isUndoing && !state.isRedoing;
export const selectCanRedo = (state: UndoRedoState) =>
  state.redoStack.length > 0 && !state.isUndoing && !state.isRedoing;
