import { useEffect } from 'react';
import { detailAsset } from './detailCatalogue';
import type { DetailInteraction } from './DetailMapPreview';

export function DetailEditControls({ placement }: { placement: DetailInteraction }) {
  useEffect(() => {
    if (!placement.selected && !placement.editing) return;
    const key = (event: KeyboardEvent) => {
      if ((event.target as HTMLElement)?.closest('input, textarea, select, [contenteditable="true"]') || event.ctrlKey || event.metaKey || event.altKey) return;
      const lower = event.key.toLowerCase();
      if (!['q', 'e', 'escape'].includes(lower) || placement.saving) return;
      event.preventDefault(); event.stopImmediatePropagation();
      if (lower === 'escape') placement.choose(null);
      else placement.setAngle(angle => (angle + (lower === 'q' ? -15 : 15) + 360) % 360);
    };
    window.addEventListener('keydown', key, true);
    return () => window.removeEventListener('keydown', key, true);
  }, [placement]);
  if (!placement.editing) return <p className="text-xs text-slate-600">Q / E to rotate · Click to place · Esc to stop. Stop placing to select an existing item.</p>;
  return <div aria-label="Selected detail" className="space-y-2">
    <p className="text-sm font-bold">Selected: {detailAsset(placement.editing.variant).label}</p>
    <p className="text-xs">{placement.moving ? 'Move the preview, then click to save its position.' : 'Q / E to rotate. Save changes when finished.'}</p>
    <label className="text-xs">Rotation <input aria-label="Selected detail rotation" type="number" step="15" value={placement.angle} disabled={placement.saving}
      onChange={e => placement.setAngle(Number(e.target.value) || 0)} className="w-20 rounded border p-2" /></label>
    <div className="flex flex-wrap gap-2">
      <button disabled={placement.saving} onClick={() => placement.setMoving(!placement.moving)} className="min-h-10 rounded border px-3">{placement.moving ? 'Stop moving' : 'Move item'}</button>
      <button disabled={placement.saving} onClick={() => void placement.saveEdit()} className="min-h-10 rounded bg-lime-300 px-3">Save changes</button>
      <button disabled={placement.saving} onClick={() => void placement.removeItem()} className="min-h-10 rounded border px-3">Delete item</button>
      <button disabled={placement.saving} onClick={() => placement.choose(null)} className="min-h-10 rounded border px-3">Done</button>
    </div>
  </div>;
}
