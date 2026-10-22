import { useState } from 'react';
import { MAX_MAP_CLEANUP_BOXES, validMapCleanupBoxes, type MapCleanupBox } from './mapCleanup';
import { metersPerDegLon, METERS_PER_DEG_LAT } from '../mapEngine/geoUtils';

interface Props {
  boxes: MapCleanupBox[];
  draft: MapCleanupBox | null;
  picking: boolean;
  onDraft: (box: MapCleanupBox | null) => void;
  onPick: (picking: boolean) => void;
  onSave: (boxes: MapCleanupBox[]) => Promise<void>;
  onClose: () => void;
}

export function MapCleanupControls({ boxes, draft, picking, onDraft, onPick, onSave, onClose }: Props) {
  const [saving, setSaving] = useState(false), [message, setMessage] = useState('');
  const button = 'min-h-11 rounded-lg border-2 border-slate-900 bg-white px-3 text-sm font-semibold disabled:opacity-40';
  const save = async (next: MapCleanupBox[]) => {
    if (validMapCleanupBoxes(next).length !== next.length) { setMessage('Use a box between 0.2 and 20 metres on each side.'); return; }
    setSaving(true); setMessage('');
    try { await onSave(next); setMessage('Cleanup saved. Undo restores the previous map view.'); }
    catch (error) { setMessage(error instanceof Error ? error.message : 'Cleanup could not save. Your draft is still here.'); }
    finally { setSaving(false); }
  };
  const nudge = (east: number, north: number, up = 0) => draft && onDraft({ ...draft,
    lng: draft.lng + east / metersPerDegLon(draft.lat), lat: draft.lat + north / METERS_PER_DEG_LAT,
    altitude: draft.altitude + up });
  const numberField = (label: string, key: 'width' | 'depth' | 'height' | 'altitude' | 'yaw', min: number, max: number) => (
    <label className="block text-xs font-semibold">{label}<input aria-label={label} type="number" min={min} max={max}
      step={key === 'yaw' ? 5 : 0.25} value={draft![key]} disabled={saving}
      onChange={event => onDraft({ ...draft!, [key]: Number(event.target.value) })}
      className="mt-1 min-h-11 w-full rounded-lg border border-slate-500 bg-white px-2" /></label>
  );
  return <section aria-label="Map cleanup pilot" className="absolute right-4 top-28 z-40 max-h-[75dvh] w-80 overflow-y-auto rounded-2xl border-2 border-slate-900 bg-[#fff9ec] p-4 text-slate-950 shadow-xl">
    <div className="flex items-center justify-between gap-2"><h2 className="font-bold">Map cleanup · local pilot</h2><button className={button} onClick={onClose} disabled={saving} aria-label="Close map cleanup">×</button></div>
    <p className="my-3 text-xs">Hide a small unwanted map fragment. Keep the box above the road and away from buildings you want to retain. Your placed models stay visible.</p>
    <button className={`${button} w-full bg-lime-200`} disabled={saving || (!picking && boxes.length >= MAX_MAP_CLEANUP_BOXES)} onClick={() => onPick(!picking)}>{picking ? 'Cancel pick' : 'Pick map fragment'}</button>
    {picking && <p role="status" className="mt-2 text-sm font-semibold">Click the floating fragment in the map. Escape cancels.</p>}
    {draft && <div className="mt-3 space-y-3">
      <p className="text-xs">The orange box previews the area. Apply when it encloses only the fragment.</p>
      <div className="grid grid-cols-2 gap-2">{numberField('Box width (m)', 'width', 0.2, 20)}{numberField('Box depth (m)', 'depth', 0.2, 20)}{numberField('Box height (m)', 'height', 0.2, 20)}{numberField('Rotation (°)', 'yaw', -360, 360)}</div>
      {numberField('Centre elevation (m)', 'altitude', -500, 9000)}
      <div className="grid grid-cols-3 gap-1">
        {([['West', -0.5, 0, 0], ['North', 0, 0.5, 0], ['Up', 0, 0, 0.5], ['East', 0.5, 0, 0], ['South', 0, -0.5, 0], ['Down', 0, 0, -0.5]] as const)
          .map(([label, east, north, up]) => <button key={label} className={button} disabled={saving} onClick={() => nudge(east, north, up)}>{label} 0.5 m</button>)}
      </div>
      <button className={`${button} w-full bg-lime-300`} disabled={saving || validMapCleanupBoxes([draft]).length !== 1}
        onClick={() => void save([...boxes.filter(box => box.id !== draft.id), draft])}>Apply cleanup</button>
      <button className={`${button} w-full`} disabled={saving} onClick={() => onDraft(null)}>Hide box</button>
    </div>}
    {boxes.length > 0 && <div className="mt-4 space-y-2"><h3 className="text-sm font-bold">Saved cleanups</h3>{boxes.map((box, index) => <div key={box.id} className="rounded-lg border border-slate-400 p-2 text-xs">
      <p>Fragment {index + 1} · {box.enabled ? 'hidden' : 'restored'} · {box.width} × {box.depth} × {box.height} m</p>
      <div className="mt-1 flex flex-wrap gap-1"><button className={button} disabled={saving} onClick={() => onDraft(box)} aria-label={`Edit fragment ${index + 1}`}>Edit</button>
        <button className={button} disabled={saving} aria-label={`${box.enabled ? 'Restore' : 'Hide'} fragment ${index + 1}`} onClick={() => void save(boxes.map(item => item.id === box.id ? { ...item, enabled: !item.enabled } : item))}>{box.enabled ? 'Restore' : 'Hide'}</button>
        <button className={button} disabled={saving} aria-label={`Remove cleanup ${index + 1}`} onClick={() => { onDraft(null); void save(boxes.filter(item => item.id !== box.id)); }}>Remove</button></div>
    </div>)}</div>}
    {message && <p role="status" className="mt-3 text-xs">{message}</p>}
  </section>;
}
