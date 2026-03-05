import { Plus, Magnet, ZoomIn, ZoomOut } from 'lucide-react';
import { useBlockEditorStore } from '@/store/blockEditorStore';
import type { LayoutBuildingData } from '@/types';

export function EditorToolbar() {
  const {
    zone, editedLayout, zoom, setZoom,
    snapToGrid, toggleSnapToGrid, addBlock,
  } = useBlockEditorStore();

  const handleAddBlock = () => {
    if (!zone || !editedLayout) return;
    const newBlock: LayoutBuildingData = {
      center_x: 0,
      center_y: 0,
      width_m: 20,
      depth_m: 15,
      height_m: 12,
      floors: 4,
      building_type: 'residential',
      rotation_deg: 0,
      setback_front_m: 3,
      setback_side_m: 2,
      name: `Building ${editedLayout.buildings.length + 1}`,
    };
    addBlock(newBlock);
  };

  return (
    <div className="absolute bottom-4 right-4 flex items-center gap-1 rounded-xl border border-white/[0.08] bg-primary-950/90 backdrop-blur-xl px-2 py-1.5 shadow-xl">
      <button
        onClick={handleAddBlock}
        className="flex items-center gap-1.5 rounded-lg px-2.5 py-1.5 text-[11px] font-medium text-neutral-300 hover:bg-white/[0.08] hover:text-white transition-colors"
        title="Add new block"
      >
        <Plus size={13} />
        Add Block
      </button>

      <div className="h-4 w-px bg-white/[0.1]" />

      <button
        onClick={toggleSnapToGrid}
        className={`rounded p-1.5 transition-colors ${snapToGrid ? 'bg-indigo-500/20 text-indigo-300' : 'text-neutral-500 hover:text-neutral-300'}`}
        title="Snap to grid"
      >
        <Magnet size={13} />
      </button>

      <div className="h-4 w-px bg-white/[0.1]" />

      <button
        onClick={() => setZoom(zoom / 1.2)}
        className="rounded p-1.5 text-neutral-400 hover:text-white transition-colors"
        title="Zoom out"
      >
        <ZoomOut size={13} />
      </button>
      <span className="w-10 text-center text-[10px] text-neutral-400 tabular-nums">
        {Math.round(zoom * 100)}%
      </span>
      <button
        onClick={() => setZoom(zoom * 1.2)}
        className="rounded p-1.5 text-neutral-400 hover:text-white transition-colors"
        title="Zoom in"
      >
        <ZoomIn size={13} />
      </button>
    </div>
  );
}
