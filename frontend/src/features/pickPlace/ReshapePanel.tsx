import { useMemo, useState } from 'react';
import { X } from 'lucide-react';
import type { SiteZone } from '@/types';
import { assetForZone, type PlaceAssetId } from './catalogue';
import { rectangleAt, rectangleDimensions } from './geometry';
import { neighborhoodParkLayoutForZone } from '@/components/viewer/globe/neighborhoodParkLayout';
import { isParkTrio, parkTrioLayout } from '@/components/viewer/globe/parkTrioLayout';
import { parkOutlineDimensions, reshapeParkOutline, addParkOutlinePoint, type ParkOutlineShape } from './parkOutline';

export function ReshapePanel({ zone, disabled, onReshape, onClose, onDelete, onDuplicate, onMore, onConnections, onTerrace }: {
  zone: SiteZone; disabled: boolean;
  onReshape: (coordinates: number[][]) => void; onClose: () => void; onDelete: () => void;
  onDuplicate: (asset: PlaceAssetId, width: number, depth: number, degrees: number) => void;
  onMore: () => void;
  onConnections?: () => void;
  onTerrace?: () => void;
}) {
  const asset = assetForZone(zone)!;
  const isPark = zone.zone_type === 'green_space';
  const dimensions = isPark ? parkOutlineDimensions(zone.coordinates) : rectangleDimensions(zone.coordinates);
  const park = useMemo(() => asset.id === 'neighbourhood_park' ? neighborhoodParkLayoutForZone(zone,
    {lng:zone.coordinates[0][0],lat:zone.coordinates[0][1]}) : null, [asset.id, zone]);
  const structuredPark = useMemo(() => isParkTrio(zone) ? parkTrioLayout(zone,
    {lng:zone.coordinates[0][0],lat:zone.coordinates[0][1]}) : null, [zone]);
  const [width,setWidth] = useState(dimensions.width.toFixed(1));
  const [depth,setDepth] = useState(dimensions.depth.toFixed(1));
  const [degrees,setDegrees] = useState(dimensions.degrees.toFixed(0));
  const [outline,setOutline] = useState<ParkOutlineShape | ''>('');
  const valid = Number.isFinite(Number(width)) && Number.isFinite(Number(depth)) && Number.isFinite(Number(degrees))
    && Number(width)>=asset.minWidth && Number(depth)>=asset.minDepth && Number(width)<=asset.maxSize && Number(depth)<=asset.maxSize;
  const button = 'min-h-11 rounded-lg border border-slate-700 bg-white px-3 text-sm font-semibold text-slate-900 disabled:opacity-40';
  return <aside aria-label="Reshape object" className="absolute bottom-4 inset-x-4 top-auto z-40 max-h-[42dvh] overflow-y-auto overscroll-contain rounded-xl border-2 border-slate-900 bg-[#fff9ec] p-3 shadow-xl sm:left-auto sm:w-72 sm:bottom-auto sm:top-20 sm:max-h-[80vh]">
    <div className="flex items-center justify-between"><h2 className="font-bold text-slate-900">{asset.label}</h2><button aria-label="Close reshape" onClick={onClose} className="flex h-11 w-11 items-center justify-center text-slate-900"><X size={18}/></button></div>
    <p className="mb-3 text-xs text-slate-600">{isPark ? 'Drag the park to move it. Drag individual white corners to fit its outline to the site; use the orange handle to turn it.' : 'Drag the object to move it. Drag a corner to reshape; use the orange handle to turn it.'}</p>
    {park && <div role="status" className="mb-3 rounded-lg bg-white p-2 text-xs text-slate-800">
      <p className="font-semibold">Current park · {park.status==='full'?'full programme':park.status==='compact'?'compact arrangement':park.loop.length?'reduced programme':'landscape layout'}</p>
      {park.notes.map(note=><p className="mt-1" key={note}>{note}</p>)}
    </div>}
    {structuredPark && structuredPark.notes.length > 0 && <div role="status" className="mb-3 rounded-lg bg-white p-2 text-xs text-slate-800">
      {structuredPark.notes.map(note=><p className="mt-1" key={note}>{note}</p>)}
    </div>}
    <form onSubmit={event => { event.preventDefault(); if(valid) onReshape(isPark
      ? reshapeParkOutline(zone.coordinates,Number(width),Number(depth),Number(degrees),outline || undefined)
      : rectangleAt(dimensions.center,Number(width),Number(depth),Number(degrees))); }}>
      {isPark && <div className="mb-3">
        <label className="text-xs font-semibold text-slate-800">Park outline<select aria-label="Park outline" value={outline} onChange={e=>setOutline(e.target.value as ParkOutlineShape | '')} className="mt-1 min-h-11 w-full rounded border border-slate-400 bg-white px-2 text-base text-slate-900">
          <option value="">Keep current outline</option><option value="rectangle">Rectangle</option><option value="triangle">Triangle</option><option value="l_shape">L shape</option>
        </select></label>
        <button type="button" className={`${button} mt-2 w-full`} disabled={disabled || zone.coordinates.length >= 128} onClick={()=>onReshape(addParkOutlinePoint(zone.coordinates))}>Add outline point</button>
        <p className="mt-2 text-xs text-slate-600">Resize keeps your outline. Equipment and courts keep their real size; only features that fit are placed.</p>
      </div>}
      <div className="grid grid-cols-2 gap-2">
        <label className="text-xs font-semibold text-slate-800">Plot width (m)<input aria-label="Plot width (m)" type="number" min={asset.minWidth} max={asset.maxSize} step="0.1" value={width} onChange={e=>setWidth(e.target.value)} className="mt-1 min-h-11 w-full rounded border border-slate-400 bg-white px-2 text-base text-slate-900" /></label>
        <label className="text-xs font-semibold text-slate-800">Plot depth (m)<input aria-label="Plot depth (m)" type="number" min={asset.minDepth} max={asset.maxSize} step="0.1" value={depth} onChange={e=>setDepth(e.target.value)} className="mt-1 min-h-11 w-full rounded border border-slate-400 bg-white px-2 text-base text-slate-900" /></label>
      </div>
      <label className="mt-2 block text-xs font-semibold text-slate-800">Rotation (°)<input aria-label="Rotation (degrees)" type="number" step="1" value={degrees} onChange={e=>setDegrees(e.target.value)} className="ml-2 min-h-11 w-20 rounded border border-slate-400 bg-white px-2 text-base text-slate-900" /></label>
      <p className="my-3 text-xs text-slate-600">{asset.reshapeDescription}</p>
      {!valid && <p role="alert" className="mb-2 text-xs text-red-700">Use a width of {asset.minWidth}–{asset.maxSize} m and depth of {asset.minDepth}–{asset.maxSize} m.</p>}
      <button disabled={disabled||!valid} className={`${button} w-full !bg-[#c9ff3d]`}>{disabled?'Saving…':'Apply shape'}</button>
    </form>
    <div className="mt-2 grid grid-cols-2 gap-2"><button className={button} disabled={disabled} onClick={()=>onDuplicate(asset.id,Number(dimensions.width.toFixed(3)),Number(dimensions.depth.toFixed(3)),Number(dimensions.degrees.toFixed(3)))}>Place another</button><button className={button} disabled={disabled} onClick={onDelete}>Delete</button></div>
    {onConnections && <button onClick={onConnections} className={`${button} mt-3 w-full`}>Connections</button>}
    {onTerrace && <button onClick={onTerrace} className={`${button} mt-2 w-full`}>Terrace & path</button>}
    <button onClick={onMore} className="mt-2 min-h-11 text-xs text-slate-700 underline">More settings</button>
  </aside>;
}
