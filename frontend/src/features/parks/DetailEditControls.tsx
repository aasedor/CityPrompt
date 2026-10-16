import { useEffect } from 'react';
import { detailAsset } from './detailCatalogue';
import type { DetailInteraction } from './DetailMapPreview';

export function DetailEditControls({ placement }: { placement: DetailInteraction }) {
  useEffect(() => {
    if (!placement.selected && !placement.editing) return;
    const key = (event: KeyboardEvent) => {
      if ((event.target instanceof Element && event.target.closest('input, textarea, select, [contenteditable="true"]')) || event.ctrlKey || event.metaKey || event.altKey) return;
      const lower = event.key.toLowerCase();
      if (!['q', 'e', 'escape', 'delete'].includes(lower) || placement.saving || event.repeat) return;
      if (lower === 'delete' && !placement.editing) return;
      event.preventDefault(); event.stopImmediatePropagation();
      if (lower === 'escape') placement.choose(null);
      else if (lower === 'delete') void placement.removeItem();
      else if (placement.editing && !placement.moving) void placement.rotateBy(lower === 'q' ? -15 : 15);
      else placement.setAngle(angle => (angle + (lower === 'q' ? -15 : 15) + 360) % 360);
    };
    window.addEventListener('keydown', key, true);
    return () => window.removeEventListener('keydown', key, true);
  }, [placement]);
  if (!placement.editing) return <p className="text-xs text-slate-600">Q / E to rotate · Click to place · Esc to stop. Click a placed item to select it, or use Placed items.</p>;
  return <div aria-label="Selected detail" className="space-y-3 rounded-xl border-2 border-slate-900 bg-lime-50 p-3">
    <p className="text-sm font-bold">Selected: {detailAsset(placement.editing.variant).label}</p>
    <p className="text-xs">{placement.moving ? 'Move the preview, then click to save its position.' : 'Move, rotate or delete this item. Changes save automatically.'}</p>
    <div className="flex gap-2">
      <button disabled={placement.saving || placement.moving} onClick={() => void placement.rotateBy(-15)} aria-label="Rotate left 15°" className="min-h-11 flex-1 rounded-lg border border-slate-400 bg-white px-2 text-sm">Rotate left 15°</button>
      <button disabled={placement.saving || placement.moving} onClick={() => void placement.rotateBy(15)} aria-label="Rotate right 15°" className="min-h-11 flex-1 rounded-lg border border-slate-400 bg-white px-2 text-sm">Rotate right 15°</button>
    </div>
    <label className="text-xs">Rotation <input aria-label="Selected detail rotation" type="number" step="15" value={placement.angle} disabled={placement.saving}
      onChange={e => placement.setAngle(Number(e.target.value) || 0)} className="w-20 rounded border p-2" /></label>
    <div className="flex flex-wrap gap-2">
      <button disabled={placement.saving} onClick={() => placement.setMoving(!placement.moving)} className="min-h-11 rounded-lg border-2 border-slate-900 bg-[#c9ff3d] px-3 font-semibold">{placement.moving ? 'Stop moving' : 'Move item'}</button>
      <button disabled={placement.saving} onClick={() => void placement.saveEdit()} className="min-h-10 rounded bg-lime-300 px-3">Save changes</button>
      <button disabled={placement.saving} onClick={() => placement.choose(placement.editing!.variant)} className="min-h-10 rounded border px-3">Place a copy</button>
      <button disabled={placement.saving} onClick={() => void placement.removeItem()} className="min-h-11 rounded-lg border border-red-300 bg-red-50 px-3 text-red-800">Delete item</button>
      <button disabled={placement.saving} onClick={() => placement.choose(null)} className="min-h-10 rounded border px-3">Done</button>
    </div>
  </div>;
}
