import { useEffect, useState } from 'react';
import { placeAsset } from './catalogue';
import type { PlacementDraft } from './GlobePlacementPreview';

export function PlacementControls({ draft, onChange }: { draft: PlacementDraft; onChange: (draft: PlacementDraft) => void }) {
  const asset = placeAsset(draft.assetId);
  const [values, setValues] = useState({ width: String(draft.width), depth: String(draft.depth), degrees: String(draft.degrees) });
  useEffect(() => setValues({ width: String(draft.width), depth: String(draft.depth), degrees: String(draft.degrees) }), [draft]);
  const valid = Number.isFinite(Number(values.width)) && Number(values.width) >= asset.minWidth && Number(values.width) <= asset.maxSize
    && Number.isFinite(Number(values.depth)) && Number(values.depth) >= asset.minDepth && Number(values.depth) <= asset.maxSize
    && values.degrees.trim() !== '' && Number.isFinite(Number(values.degrees));
  return <form onSubmit={event => { event.preventDefault(); if (valid) onChange({ ...draft, width: Number(values.width), depth: Number(values.depth), degrees: ((Number(values.degrees) % 360) + 360) % 360 }); }} className="space-y-2 text-left">
    <p className="font-bold">{asset.label}</p>
    <div className="grid grid-cols-3 gap-2">
      {(['width', 'depth', 'degrees'] as const).map(key => <label key={key} className="text-xs">{key === 'degrees' ? 'Rotation (°)' : `${key === 'width' ? 'Width' : 'Depth'} (m)`}
        <input aria-label={`Placement ${key}`} type="number" step="any" value={values[key]} onChange={event => setValues(current => ({ ...current, [key]: event.target.value }))} className="mt-1 min-h-11 w-full rounded border border-slate-400 p-1" />
      </label>)}
    </div>
    <p className="text-xs">Minimum {asset.minWidth} × {asset.minDepth} m; maximum {asset.maxSize} m per side.{asset.properties.native_home_plot === true ? ' Houses repeat at their native size.' : ''}</p>
    <button disabled={!valid} className="min-h-11 w-full rounded-lg bg-lime-200 px-2 disabled:opacity-40">Update placement preview</button>
  </form>;
}
