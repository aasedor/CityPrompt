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
        className="rounded-full border-2 border-[#151515] bg-white p-1.5 text-[#151515]/60 transition hover:bg-[#fff9ec] hover:text-[#151515] disabled:cursor-default disabled:opacity-30 disabled:hover:bg-white"
        title="Undo (Ctrl+Z)"
      >
        <Undo2 size={16} />
      </button>
      <button
        onClick={() => redo()}
        disabled={!canRedo || isRedoing}
        className="rounded-full border-2 border-[#151515] bg-white p-1.5 text-[#151515]/60 transition hover:bg-[#fff9ec] hover:text-[#151515] disabled:cursor-default disabled:opacity-30 disabled:hover:bg-white"
        title="Redo (Ctrl+Shift+Z)"
      >
        <Redo2 size={16} />
      </button>
    </div>
  );
}
