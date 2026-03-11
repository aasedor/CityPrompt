import { Trash2, Copy, RotateCw, MapPin, TreePine, Route, Layers } from 'lucide-react';
import { useBlockEditorStore } from '@/store/blockEditorStore';

export function BlockPropertiesPanel() {
  const {
    editedLayout, selectedBlockIndex, selectedBlockIndices, zone,
    selectedElementType, selectedElementIndex,
    updateBlockProperties, deleteBlock, deleteSelectedBlocks,
    duplicateBlock, duplicateSelectedBlocks,
    copySelectedBlocks,
    updateRoadProperties, updateGreenSpaceProperties,
  } = useBlockEditorStore();

  // Road properties panel
  if (selectedElementType === 'road' && selectedElementIndex !== null && editedLayout) {
    const road = editedLayout.roads?.[selectedElementIndex];
    if (!road) return null;
    return (
      <div data-scrollable className="w-72 border-l border-white/[0.08] bg-primary-950/95 backdrop-blur-xl overflow-y-auto">
        <div className="p-4 space-y-4">
          <div className="flex items-center gap-2">
            <Route size={14} className="text-amber-400" />
            <h3 className="text-sm font-semibold text-white">Road</h3>
          </div>

          <Field label="Name">
            <input type="text" value={road.name || ''}
              onChange={(e) => updateRoadProperties(selectedElementIndex, { name: e.target.value })}
              placeholder="Main Street"
              className="w-full rounded-lg border border-white/[0.1] bg-white/[0.05] px-3 py-1.5 text-xs text-white placeholder-neutral-500 focus:border-indigo-400/50 focus:outline-none" />
          </Field>

          <Field label="Road Type">
            <select value={road.road_type || 'access'}
              onChange={(e) => updateRoadProperties(selectedElementIndex, { road_type: e.target.value })}
              className="w-full rounded-lg border border-white/[0.1] bg-white/[0.05] px-3 py-1.5 text-xs text-white focus:border-indigo-400/50 focus:outline-none">
              <option value="main">Main Road</option>
              <option value="collector">Collector</option>
              <option value="access">Access Road</option>
              <option value="pedestrian">Pedestrian</option>
              <option value="service">Service Road</option>
            </select>
          </Field>

          <Field label="Width (m)">
            <input type="number" value={road.width_m || ''}
              onChange={(e) => updateRoadProperties(selectedElementIndex, { width_m: parseFloat(e.target.value) || 6 })}
              min={2} step={0.5}
              className="w-full rounded-lg border border-white/[0.1] bg-white/[0.05] px-3 py-1.5 text-xs text-white focus:border-indigo-400/50 focus:outline-none" />
          </Field>

          <Field label="3D Description">
            <textarea value={road.description || ''}
              onChange={(e) => updateRoadProperties(selectedElementIndex, { description: e.target.value })}
              placeholder="Describe this road for 3D generation..."
              rows={3}
              className="w-full rounded-lg border border-white/[0.1] bg-white/[0.05] px-3 py-1.5 text-xs text-white placeholder-neutral-500 focus:border-indigo-400/50 focus:outline-none resize-none" />
          </Field>
        </div>
      </div>
    );
  }

  // Green space properties panel
  if (selectedElementType === 'green_space' && selectedElementIndex !== null && editedLayout) {
    const gs = editedLayout.green_spaces?.[selectedElementIndex];
    if (!gs) return null;
    return (
      <div data-scrollable className="w-72 border-l border-white/[0.08] bg-primary-950/95 backdrop-blur-xl overflow-y-auto">
        <div className="p-4 space-y-4">
          <div className="flex items-center gap-2">
            <TreePine size={14} className="text-emerald-400" />
            <h3 className="text-sm font-semibold text-white">Green Space</h3>
          </div>

          <Field label="Name">
            <input type="text" value={gs.name || ''}
              onChange={(e) => updateGreenSpaceProperties(selectedElementIndex, { name: e.target.value })}
              placeholder="Central Park"
              className="w-full rounded-lg border border-white/[0.1] bg-white/[0.05] px-3 py-1.5 text-xs text-white placeholder-neutral-500 focus:border-indigo-400/50 focus:outline-none" />
          </Field>

          <Field label="Space Type">
            <select value={gs.space_type || 'park'}
              onChange={(e) => updateGreenSpaceProperties(selectedElementIndex, { space_type: e.target.value })}
              className="w-full rounded-lg border border-white/[0.1] bg-white/[0.05] px-3 py-1.5 text-xs text-white focus:border-indigo-400/50 focus:outline-none">
              <option value="park">Park</option>
              <option value="plaza">Plaza</option>
              <option value="courtyard">Courtyard</option>
              <option value="garden">Garden</option>
              <option value="playground">Playground</option>
              <option value="buffer">Buffer / Setback</option>
            </select>
          </Field>

          <Field label="3D Description">
            <textarea value={gs.description || ''}
              onChange={(e) => updateGreenSpaceProperties(selectedElementIndex, { description: e.target.value })}
              placeholder="Describe this green space for 3D generation..."
              rows={3}
              className="w-full rounded-lg border border-white/[0.1] bg-white/[0.05] px-3 py-1.5 text-xs text-white placeholder-neutral-500 focus:border-indigo-400/50 focus:outline-none resize-none" />
          </Field>
        </div>
      </div>
    );
  }

  // Multi-selection panel
  if (selectedBlockIndices.length > 1 && editedLayout) {
    const totalArea = selectedBlockIndices.reduce((sum, i) => {
      const b = editedLayout.buildings[i];
      return b ? sum + b.width_m * b.depth_m : sum;
    }, 0);
    return (
      <div data-scrollable className="w-72 border-l border-white/[0.08] bg-primary-950/95 backdrop-blur-xl overflow-y-auto">
        <div className="p-4 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Layers size={14} className="text-indigo-400" />
              <h3 className="text-sm font-semibold text-white">{selectedBlockIndices.length} Blocks Selected</h3>
            </div>
            <div className="flex gap-1">
              <button onClick={() => copySelectedBlocks()}
                className="rounded p-1.5 text-neutral-400 hover:bg-white/10 hover:text-white" title="Copy (Ctrl+C)">
                <Copy size={13} />
              </button>
              <button onClick={() => duplicateSelectedBlocks()}
                className="rounded p-1.5 text-neutral-400 hover:bg-white/10 hover:text-white" title="Duplicate (Ctrl+D)">
                <Copy size={13} />
              </button>
              <button onClick={() => deleteSelectedBlocks()}
                className="rounded p-1.5 text-red-400 hover:bg-red-500/10 hover:text-red-300" title="Delete (Del)">
                <Trash2 size={13} />
              </button>
            </div>
          </div>

          <div className="rounded-lg border border-white/[0.06] bg-white/[0.03] p-3 space-y-1">
            <InfoRow label="Blocks" value={String(selectedBlockIndices.length)} />
            <InfoRow label="Total area" value={`${Math.round(totalArea).toLocaleString()} m\u00B2`} />
          </div>

          <p className="text-[10px] text-neutral-500 leading-relaxed">
            Use arrow keys or drag to move all selected blocks together. Press Escape to deselect.
          </p>
        </div>
      </div>
    );
  }

  // No selection
  if (selectedBlockIndex === null || !editedLayout) {
    return (
      <div data-scrollable className="w-72 border-l border-white/[0.08] bg-primary-950/95 backdrop-blur-xl overflow-y-auto">
        <div className="flex h-full items-center justify-center p-6">
          <div className="text-center">
            <div className="text-neutral-600 mb-2">
              <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className="mx-auto"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>
            </div>
            <p className="text-xs text-neutral-500">Click a block, road, or green space to edit</p>
            <p className="text-[10px] text-neutral-600 mt-1">Edit name, style, dimensions, and 3D description</p>
          </div>
        </div>
      </div>
    );
  }

  // Building properties
  const block = editedLayout.buildings[selectedBlockIndex];
  if (!block) return null;

  const zoneDescription = (zone?.properties?.description_text as string) || '';

  const update = (props: Record<string, unknown>) => {
    updateBlockProperties(selectedBlockIndex, props as Partial<typeof block>);
  };

  return (
    <div data-scrollable className="w-72 border-l border-white/[0.08] bg-primary-950/95 backdrop-blur-xl overflow-y-auto">
      <div className="p-4 space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold text-white">Block #{selectedBlockIndex + 1}</h3>
          <div className="flex gap-1">
            <button onClick={() => duplicateBlock(selectedBlockIndex)}
              className="rounded p-1.5 text-neutral-400 hover:bg-white/10 hover:text-white" title="Duplicate (Ctrl+D)">
              <Copy size={13} />
            </button>
            <button onClick={() => deleteBlock(selectedBlockIndex)}
              className="rounded p-1.5 text-red-400 hover:bg-red-500/10 hover:text-red-300" title="Delete (Del)">
              <Trash2 size={13} />
            </button>
          </div>
        </div>

        {zoneDescription && (
          <div className="rounded-lg border border-white/[0.06] bg-white/[0.03] p-2.5 space-y-1">
            <div className="flex items-center gap-1.5">
              <MapPin size={10} className="text-amber-400" />
              <span className="text-[10px] font-medium uppercase tracking-wide text-amber-400/80">Zone Description</span>
            </div>
            <p className="text-[10px] leading-relaxed text-neutral-400 line-clamp-4">
              {zoneDescription}
            </p>
          </div>
        )}

        <Field label="Name">
          <input type="text" value={(block as any).name || ''}
            onChange={(e) => update({ name: e.target.value })}
            placeholder={`Building ${selectedBlockIndex + 1}`}
            className="w-full rounded-lg border border-white/[0.1] bg-white/[0.05] px-3 py-1.5 text-xs text-white placeholder-neutral-500 focus:border-indigo-400/50 focus:outline-none" />
        </Field>

        <Field label="Type">
          <select value={block.building_type}
            onChange={(e) => update({ building_type: e.target.value })}
            className="w-full rounded-lg border border-white/[0.1] bg-white/[0.05] px-3 py-1.5 text-xs text-white focus:border-indigo-400/50 focus:outline-none">
            <option value="residential">Residential</option>
            <option value="commercial">Commercial</option>
            <option value="mixed_use">Mixed Use</option>
            <option value="institutional">Institutional</option>
            <option value="park_plaza">Park / Plaza</option>
          </select>
        </Field>

        <div className="grid grid-cols-2 gap-2">
          <Field label="Width (m)">
            <input type="number" value={Math.round(block.width_m * 10) / 10}
              onChange={(e) => update({ width_m: parseFloat(e.target.value) || 3 })}
              min={3} step={0.5}
              className="w-full rounded-lg border border-white/[0.1] bg-white/[0.05] px-3 py-1.5 text-xs text-white focus:border-indigo-400/50 focus:outline-none" />
          </Field>
          <Field label="Depth (m)">
            <input type="number" value={Math.round(block.depth_m * 10) / 10}
              onChange={(e) => update({ depth_m: parseFloat(e.target.value) || 3 })}
              min={3} step={0.5}
              className="w-full rounded-lg border border-white/[0.1] bg-white/[0.05] px-3 py-1.5 text-xs text-white focus:border-indigo-400/50 focus:outline-none" />
          </Field>
        </div>

        <div className="grid grid-cols-2 gap-2">
          <Field label="Floors">
            <input type="number" value={block.floors ?? ''}
              onChange={(e) => {
                const floors = parseInt(e.target.value) || undefined;
                if (!floors) { update({ floors: undefined }); return; }
                const floorH = block.height_m && block.floors ? block.height_m / block.floors : 3;
                update({ floors, height_m: Math.round(floors * floorH * 10) / 10 });
              }}
              min={1} max={100} placeholder="Auto"
              className="w-full rounded-lg border border-white/[0.1] bg-white/[0.05] px-3 py-1.5 text-xs text-white placeholder-neutral-500 focus:border-indigo-400/50 focus:outline-none" />
          </Field>
          <Field label="Height (m)">
            <input type="number" value={block.height_m ?? ''}
              onChange={(e) => update({ height_m: parseFloat(e.target.value) || undefined })}
              min={3} step={1} placeholder="Auto"
              className="w-full rounded-lg border border-white/[0.1] bg-white/[0.05] px-3 py-1.5 text-xs text-white placeholder-neutral-500 focus:border-indigo-400/50 focus:outline-none" />
            {block.floors && block.height_m ? (
              <p className="mt-0.5 text-[10px] text-neutral-500">{(block.height_m / block.floors).toFixed(1)}m per floor</p>
            ) : null}
          </Field>
        </div>

        <Field label="Rotation">
          <div className="flex items-center gap-2">
            <input type="range" min={0} max={360} step={5} value={block.rotation_deg}
              onChange={(e) => update({ rotation_deg: parseFloat(e.target.value) })} className="flex-1" />
            <span className="w-10 text-right text-[10px] text-neutral-400 tabular-nums">
              {Math.round(block.rotation_deg)}{'\u00B0'}
            </span>
            <button onClick={() => update({ rotation_deg: 0 })}
              className="rounded p-1 text-neutral-500 hover:text-white" title="Reset rotation">
              <RotateCw size={11} />
            </button>
          </div>
        </Field>

        <Field label="3D Generation Prompt">
          <textarea value={(block as any).description || zoneDescription || ''}
            onFocus={() => {
              if (!(block as any).description && zoneDescription) {
                update({ description: zoneDescription });
              }
            }}
            onChange={(e) => update({ description: e.target.value })}
            placeholder="Describe this building for 3D generation..."
            rows={3}
            className="w-full rounded-lg border border-white/[0.1] bg-white/[0.05] px-3 py-1.5 text-xs text-white placeholder-neutral-500 focus:border-indigo-400/50 focus:outline-none resize-none" />
        </Field>

        <Field label="Architectural Style">
          <select value={(block as any).style || ''}
            onChange={(e) => update({ style: e.target.value || undefined })}
            className="w-full rounded-lg border border-white/[0.1] bg-white/[0.05] px-3 py-1.5 text-xs text-white focus:border-indigo-400/50 focus:outline-none">
            <option value="">Use zone default</option>
            <option value="modern">Modern</option>
            <option value="classical">Classical</option>
            <option value="minimalist">Minimalist</option>
            <option value="brutalist">Brutalist</option>
            <option value="art_deco">Art Deco</option>
            <option value="victorian">Victorian</option>
            <option value="mediterranean">Mediterranean</option>
            <option value="industrial">Industrial</option>
            <option value="futuristic">Futuristic</option>
            <option value="tropical">Tropical</option>
          </select>
        </Field>

        <div className="rounded-lg border border-white/[0.06] bg-white/[0.03] p-3 space-y-1">
          <InfoRow label="Area" value={`${Math.round(block.width_m * block.depth_m)} m\u00B2`} />
          {block.height_m && (
            <InfoRow label="Volume" value={`${Math.round(block.width_m * block.depth_m * block.height_m).toLocaleString()} m\u00B3`} />
          )}
          {block.floors && (
            <InfoRow label="Total floor area" value={`${Math.round(block.width_m * block.depth_m * block.floors).toLocaleString()} m\u00B2`} />
          )}
        </div>
      </div>
    </div>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="space-y-1">
      <label className="block text-[10px] font-medium uppercase tracking-wide text-neutral-500">
        {label}
      </label>
      {children}
    </div>
  );
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between text-[10px]">
      <span className="text-neutral-500">{label}</span>
      <span className="text-neutral-300">{value}</span>
    </div>
  );
}
