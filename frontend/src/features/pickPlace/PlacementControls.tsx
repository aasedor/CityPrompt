import { useCallback, useEffect, useId, useState } from 'react';
import { placeAsset } from './catalogue';
import type { PlacementDraft } from './GlobePlacementPreview';
import { reviewedEntranceForAsset } from './reviewedEntrances';

export function PlacementControls({ draft, onChange, getPreviewDegrees }: {
  draft: PlacementDraft;
  onChange: (draft: PlacementDraft) => void;
  getPreviewDegrees?: () => number | null;
}) {
  const generated=draft.generatedModel;
  const asset=generated?null:placeAsset(draft.assetId);
  const entrance=asset?reviewedEntranceForAsset(asset):null;
  const minWidth=asset?.minWidth??2, minDepth=asset?.minDepth??2;
  const maxWidth=asset?(asset.maxWidth??asset.maxSize):100;
  const maxDepth=asset?(asset.maxDepth??asset.maxSize):100;
  const hintId = useId();
  const [values, setValues] = useState(draft.inputValues ?? { width: String(draft.width), depth: String(draft.depth), degrees: String(draft.degrees) });
  const update = useCallback((key: keyof typeof values, value: string) => {
    const next = { ...values, [key]: value };
    setValues(next);
    const valid = next.width.trim() !== '' && Number.isFinite(Number(next.width)) && Number(next.width) >= minWidth && Number(next.width) <= maxWidth
      && next.depth.trim() !== '' && Number.isFinite(Number(next.depth)) && Number(next.depth) >= minDepth && Number(next.depth) <= maxDepth
      && next.degrees.trim() !== '' && Number.isFinite(Number(next.degrees));
    // Keep text such as a trailing decimal while synchronizing the actual placement.
    // An unfinished entry must never silently place the previous valid dimensions.
    onChange(valid
      ? { ...draft, width: Number(next.width), depth: Number(next.depth), degrees: ((Number(next.degrees) % 360) + 360) % 360, faceStreet: key === 'degrees' ? false : draft.faceStreet, inputValues: next, inputError: undefined }
      : { ...draft, inputValues: next, inputError: 'Enter dimensions within the limits and a rotation to place your object.' });
  }, [values, draft, onChange, minWidth, minDepth, maxWidth, maxDepth]);
  useEffect(() => {
    const rotate = (event: KeyboardEvent) => {
      if (event.defaultPrevented || event.ctrlKey || event.metaKey || event.altKey || event.isComposing) return;
      const target = event.target;
      if (target instanceof Element && target.closest('input, textarea, select, [contenteditable]:not([contenteditable="false"]), [role="textbox"]')) return;
      const key = event.key.toLowerCase();
      if (key !== 'q' && key !== 'e') return;
      event.preventDefault();
      // Consume before the globe's selected-object shortcuts can rotate another object.
      event.stopImmediatePropagation();
      if (draft.inputError) return;
      const base = draft.faceStreet ? getPreviewDegrees?.() ?? draft.degrees : draft.degrees;
      const step = (event.shiftKey ? 1 : 15) * (key === 'q' ? 1 : -1);
      update('degrees', String(((base + step) % 360 + 360) % 360));
    };
    window.addEventListener('keydown', rotate, true);
    return () => window.removeEventListener('keydown', rotate, true);
  }, [draft.degrees, draft.faceStreet, draft.inputError, getPreviewDegrees, update]);
  return <div className="space-y-2 text-left" aria-keyshortcuts="Q E Shift+Q Shift+E">
    <p className="font-bold">{generated?.name??asset?.label}</p>
    {(generated || asset?.zoneType === 'building') && <label className="flex min-h-11 items-center gap-2 text-sm">
      <input type="checkbox" checked={draft.faceStreet === true} onChange={event => onChange({ ...draft, faceStreet: event.target.checked })} />
      Face nearby street
    </label>}
    <div className="grid grid-cols-3 gap-2">
      {(['width', 'depth', 'degrees'] as const).map(key => <label key={key} className="text-xs">{key === 'degrees' ? 'Rotation (°)' : `${key === 'width' ? 'Width' : 'Depth'} (m)`}
        <input aria-label={`Placement ${key}`} aria-describedby={hintId} type="number" step="any"
          min={key === 'degrees' ? undefined : key === 'width' ? minWidth : minDepth}
          max={key === 'degrees' ? undefined : key === 'width' ? maxWidth : maxDepth}
          disabled={asset?.properties.validation_fixed_fixture === true && key !== 'degrees'}
          value={values[key]} onChange={event => update(key, event.target.value)} className="mt-1 min-h-11 w-full rounded border border-slate-400 p-1" />
      </label>)}
    </div>
    <p className="text-xs text-slate-600">Q: rotate left · E: rotate right (15°). Hold Shift for 1°.</p>
    <p id={hintId} className="text-xs">Minimum {minWidth} × {minDepth} m; maximum {maxWidth} × {maxDepth} m.{asset?.properties.native_home_plot === true ? ' Houses repeat at their native size.' : ''}
      {generated && (generated.size_estimated ? ' The original plot size was unavailable; adjust this starting size if needed.' : ' The starting size matches the original plot.')}
    </p>
    <p role="status" className={draft.inputError ? 'text-xs text-red-700' : 'text-xs text-slate-600'}>{draft.inputError ?? (draft.faceStreet ? 'The preview faces a nearby street. Enter a rotation for manual control.' : 'Size and rotation update automatically.')}</p>
    {(generated || asset?.zoneType === 'building') && <p className="text-xs text-slate-600">Buildings settle into available space beside other plots.{generated ? ' Your saved model keeps its proportions as its plot size changes.' : ''}
      {entrance && (entrance.fixedNative || (Math.abs(draft.width-entrance.plotWidthM)<.05 && Math.abs(draft.depth-entrance.plotDepthM)<.05))
        ? ' This building connects to a nearby sidewalk automatically.' : ''}</p>}
  </div>;
}
