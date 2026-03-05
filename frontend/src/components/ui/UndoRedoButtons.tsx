import { Undo2, Redo2 } from 'lucide-react';
import { useUndoRedoStore, selectCanUndo, selectCanRedo } from '@/store/undoRedo';

export function UndoRedoButtons() {
  const canUndo = useUndoRedoStore(selectCanUndo);
  const canRedo = useUndoRedoStore(selectCanRedo);
  const undo = useUndoRedoStore((s) => s.undo);
  const redo = useUndoRedoStore((s) => s.redo);
  const isUndoing = useUndoRedoStore((s) => s.isUndoing);
  const isRedoing = useUndoRedoStore((s) => s.isRedoing);

  return (
    <div className="flex items-center gap-1">
      <button
        onClick={() => undo()}
        disabled={!canUndo || isUndoing}
        className="rounded-lg p-1.5 text-primary-950/50 hover:bg-primary-950/[0.06] hover:text-primary-950 disabled:cursor-default disabled:text-primary-950/20 disabled:hover:bg-transparent"
        title="Undo (Ctrl+Z)"
      >
        <Undo2 size={16} />
      </button>
      <button
        onClick={() => redo()}
        disabled={!canRedo || isRedoing}
        className="rounded-lg p-1.5 text-primary-950/50 hover:bg-primary-950/[0.06] hover:text-primary-950 disabled:cursor-default disabled:text-primary-950/20 disabled:hover:bg-transparent"
        title="Redo (Ctrl+Shift+Z)"
      >
        <Redo2 size={16} />
      </button>
    </div>
  );
}
