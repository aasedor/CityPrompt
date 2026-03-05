import { useEffect } from 'react';
import { useBlockEditorStore } from '@/store/blockEditorStore';

export function useBlockEditorKeyboard() {
  const { selectedBlockIndex, deleteBlock, duplicateBlock, undo, redo, selectBlock } = useBlockEditorStore();

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      // Don't intercept when typing in inputs
      const tag = (e.target as HTMLElement).tagName;
      if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT') return;

      if (e.key === 'Escape') {
        selectBlock(null);
        return;
      }

      if (e.key === 'Delete' || e.key === 'Backspace') {
        if (selectedBlockIndex !== null) {
          e.preventDefault();
          deleteBlock(selectedBlockIndex);
        }
        return;
      }

      if ((e.ctrlKey || e.metaKey) && e.key === 'd') {
        e.preventDefault();
        if (selectedBlockIndex !== null) {
          duplicateBlock(selectedBlockIndex);
        }
        return;
      }

      if ((e.ctrlKey || e.metaKey) && e.key === 'z') {
        e.preventDefault();
        if (e.shiftKey) {
          redo();
        } else {
          undo();
        }
        return;
      }

      if ((e.ctrlKey || e.metaKey) && e.key === 'y') {
        e.preventDefault();
        redo();
        return;
      }
    };

    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [selectedBlockIndex, deleteBlock, duplicateBlock, undo, redo, selectBlock]);
}
