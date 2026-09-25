import { useId, useState } from 'react';
import { placeAsset } from './catalogue';
import type { PlacementDraft } from './GlobePlacementPreview';
import { reviewedEntranceForAsset } from './reviewedEntrances';

export function PlacementControls({ draft, onChange }: { draft: PlacementDraft; onChange: (draft: PlacementDraft) => void }) {
  const asset = placeAsset(draft.assetId);
  const entrance = reviewedEntranceForAsset(asset);
  const hintId = useId();
  const [values, setValues] = useState(draft.inputValues ?? { width: String(draft.width), depth: String(draft.depth), degrees: String(draft.degrees) });
  function update(key: keyof typeof values, value: string) {
    const next = { ...values, [key]: value };
    setValues(next);
    const valid = next.width.trim() !== '' && Number.isFinite(Number(next.width)) && Number(next.width) >= asset.minWidth && Number(next.width) <= asset.maxSize
      && next.depth.trim() !== '' && Number.isFinite(Number(next.depth)) && Number(next.depth) >= asset.minDepth && Number(next.depth) <= asset.maxSize
      && next.degrees.trim() !== '' && Number.isFinite(Number(next.degrees));
    // Keep text such as a trailing decimal while synchronizing the actual placement.
    // An unfinished entry must never silently place the previous valid dimensions.
    onChange(valid
      ? { ...draft, width: Number(next.width), depth: Number(next.depth), degrees: ((Number(next.degrees) % 360) + 360) % 360, faceStreet: key === 'degrees' ? false : draft.faceStreet, inputValues: next, inputError: undefined }
      : { ...draft, inputValues: next, inputError: 'Enter dimensions within the limits and a rotation to place your object.' });
  }
  return <div className="space-y-2 text-left">
    <p className="font-bold">{asset.label}</p>
    {asset.zoneType === 'building' && <label className="flex min-h-11 items-center gap-2 text-sm">
      <input type="checkbox" checked={draft.faceStreet === true} onChange={event => onChange({ ...draft, faceStreet: event.target.checked })} />
      Face nearby street
    </label>}
    <div className="grid grid-cols-3 gap-2">
      {(['width', 'depth', 'degrees'] as const).map(key => <label key={key} className="text-xs">{key === 'degrees' ? 'Rotation (°)' : `${key === 'width' ? 'Width' : 'Depth'} (m)`}
        <input aria-label={`Placement ${key}`} aria-describedby={hintId} type="number" step="any"
          min={key === 'degrees' ? undefined : key === 'width' ? asset.minWidth : asset.minDepth}
          max={key === 'degrees' ? undefined : asset.maxSize}
          disabled={asset.properties.validation_fixed_fixture === true && key !== 'degrees'}
          value={values[key]} onChange={event => update(key, event.target.value)} className="mt-1 min-h-11 w-full rounded border border-slate-400 p-1" />
      </label>)}
    </div>
    <p id={hintId} className="text-xs">Minimum {asset.minWidth} × {asset.minDepth} m; maximum {asset.maxSize} m per side.{asset.properties.native_home_plot === true ? ' Houses repeat at their native size.' : ''}</p>
    <p role="status" className={draft.inputError ? 'text-xs text-red-700' : 'text-xs text-slate-600'}>{draft.inputError ?? (draft.faceStreet ? 'The preview faces a nearby street. Enter a rotation for manual control.' : 'Size and rotation update automatically.')}</p>
    {asset.zoneType === 'building' && <p className="text-xs text-slate-600">Buildings settle into available space beside other plots.
      {entrance && (entrance.fixedNative || (Math.abs(draft.width-entrance.plotWidthM)<.05 && Math.abs(draft.depth-entrance.plotDepthM)<.05))
        ? ' This building connects to a nearby sidewalk automatically.' : ''}</p>}
  </div>;
}
