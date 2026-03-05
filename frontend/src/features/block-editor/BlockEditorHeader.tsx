import { ArrowLeft, Undo2, Redo2, Save, Wand2, Grid3X3, Ruler } from 'lucide-react';
import { useBlockEditorStore } from '@/store/blockEditorStore';

interface BlockEditorHeaderProps {
  onBack: () => void;
  onSave: () => void;
  onGenerate3D: () => void;
  isSaving: boolean;
  isGenerating: boolean;
}

export function BlockEditorHeader({
  onBack, onSave, onGenerate3D, isSaving, isGenerating,
}: BlockEditorHeaderProps) {
  const {
    zone, options, activeOptionIndex, switchOption,
    undo, redo, undoStack, redoStack, editedLayout,
    showGrid, toggleGrid, showDimensions, toggleDimensions,
  } = useBlockEditorStore();

  const buildingCount = editedLayout?.buildings.length ?? 0;

  return (
    <div className="flex items-center justify-between border-b border-white/[0.08] bg-primary-950/95 backdrop-blur-xl px-4 py-2.5">
      {/* Left: Back + Zone info */}
      <div className="flex items-center gap-3">
        <button
          onClick={onBack}
          className="flex items-center gap-1.5 rounded-lg px-2 py-1.5 text-sm text-neutral-400 hover:bg-white/[0.06] hover:text-white transition-colors"
        >
          <ArrowLeft size={16} />
          Back
        </button>
        <div className="h-5 w-px bg-white/[0.1]" />
        <div>
          <h2 className="text-sm font-semibold text-white">
            {zone?.name || 'Block Editor'}
          </h2>
          <span className="text-[10px] text-neutral-500">
            {buildingCount} blocks
          </span>
        </div>
      </div>

      {/* Center: Option tabs */}
      <div className="flex items-center gap-1">
        {options.map((opt, idx) => (
          <button
            key={idx}
            onClick={() => switchOption(idx)}
            className={`rounded-lg px-3 py-1 text-xs font-medium transition-all ${
              idx === activeOptionIndex
                ? 'bg-indigo-500/20 text-indigo-300 ring-1 ring-indigo-400/30'
                : 'text-neutral-400 hover:bg-white/[0.06] hover:text-neutral-200'
            }`}
          >
            {opt.option_label || `Option ${idx + 1}`}
          </button>
        ))}
      </div>

      {/* Right: Tools + Actions */}
      <div className="flex items-center gap-2">
        {/* View toggles */}
        <button
          onClick={toggleGrid}
          className={`rounded p-1.5 transition-colors ${showGrid ? 'bg-white/10 text-white' : 'text-neutral-500 hover:text-neutral-300'}`}
          title="Toggle grid"
        >
          <Grid3X3 size={14} />
        </button>
        <button
          onClick={toggleDimensions}
          className={`rounded p-1.5 transition-colors ${showDimensions ? 'bg-white/10 text-white' : 'text-neutral-500 hover:text-neutral-300'}`}
          title="Toggle dimensions"
        >
          <Ruler size={14} />
        </button>

        <div className="h-5 w-px bg-white/[0.1]" />

        {/* Undo/Redo */}
        <button
          onClick={undo}
          disabled={undoStack.length === 0}
          className="rounded p-1.5 text-neutral-400 hover:bg-white/[0.06] hover:text-white disabled:opacity-30 disabled:cursor-not-allowed"
          title="Undo (Ctrl+Z)"
        >
          <Undo2 size={14} />
        </button>
        <button
          onClick={redo}
          disabled={redoStack.length === 0}
          className="rounded p-1.5 text-neutral-400 hover:bg-white/[0.06] hover:text-white disabled:opacity-30 disabled:cursor-not-allowed"
          title="Redo (Ctrl+Shift+Z)"
        >
          <Redo2 size={14} />
        </button>

        <div className="h-5 w-px bg-white/[0.1]" />

        {/* Save */}
        <button
          onClick={onSave}
          disabled={isSaving}
          className="flex items-center gap-1.5 rounded-lg bg-white/[0.08] px-3 py-1.5 text-xs font-medium text-neutral-200 hover:bg-white/[0.12] disabled:opacity-50"
        >
          <Save size={12} />
          {isSaving ? 'Saving...' : 'Save'}
        </button>

        {/* Generate 3D */}
        <button
          onClick={onGenerate3D}
          disabled={isGenerating || buildingCount === 0}
          className="flex items-center gap-1.5 rounded-lg bg-gradient-to-r from-indigo-500 to-purple-500 px-4 py-1.5 text-xs font-semibold text-white shadow-lg shadow-indigo-500/25 hover:from-indigo-400 hover:to-purple-400 disabled:opacity-50 transition-all"
        >
          <Wand2 size={13} />
          {isGenerating ? 'Generating...' : 'Generate 3D'}
        </button>
      </div>
    </div>
  );
}
