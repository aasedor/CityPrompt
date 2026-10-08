import { ParkLayoutControls } from '@/features/parks/ParkLayoutControls';
import { hasNativePark } from '@/features/parks/nativeParkRegistry';
import { flexibleParkFitProblem, isFlexiblePark } from '@/features/parks/flexibleParkFit';
import { useMemo, useState } from 'react';
import { X } from 'lucide-react';
import type { SiteZone } from '@/types';
import { assetForZone, type PlaceAssetId } from './catalogue';
import { rectangleAt, rectangleDimensions } from './geometry';
import { neighborhoodParkLayoutForZone } from '@/components/viewer/globe/neighborhoodParkLayout';
import { isParkTrio, parkTrioLayout } from '@/components/viewer/globe/parkTrioLayout';
import { parkOutlineDimensions, reshapeParkOutline, addParkOutlinePoint, type ParkOutlineShape } from './parkOutline';
import { ParkComponentControls } from './ParkComponentControls';
import { BenchDetailControls } from '@/features/parks/BenchDetailEditor';
import { BuildingDesignControls } from './BuildingDesignControls';
import type { SiteZoneProperties } from '@/types';

export function ReshapePanel({ zone, disabled, onReshape, onClose, onDelete, onDuplicate, onMore, onConnections, onTerrace, onUpdateDesign, zones = [], onUpdateParkLayout, onSaveDetails, onDetailsEditingChange }: {
  onDetailsEditingChange?: (editing:boolean) => void;
  onSaveDetails?: (properties: SiteZoneProperties) => Promise<unknown>;
  zones?: SiteZone[]; onUpdateParkLayout?: (data:{coordinates:number[][];properties:SiteZoneProperties})=>Promise<unknown>;
  zone: SiteZone; disabled: boolean;
  onReshape: (coordinates: number[][]) => boolean | void; onClose: () => void; onDelete: () => void;
  onDuplicate: (asset: PlaceAssetId, width: number, depth: number, degrees: number) => void;
  onMore: () => void;
  onConnections?: () => void;
  onTerrace?: () => void;
  onUpdateDesign?: (properties: SiteZoneProperties) => void;
}) {
  const asset = assetForZone(zone)!;
  const fixedFixture = zone.properties?.validation_fixed_fixture === true;
  const isPark = zone.zone_type === 'green_space' && !fixedFixture;
  const keepOutline = isPark || asset.reshapeMode === 'authored_footprint';
  const dimensions = keepOutline ? parkOutlineDimensions(zone.coordinates) : rectangleDimensions(zone.coordinates);
  const park = useMemo(() => asset.id === 'neighbourhood_park' ? neighborhoodParkLayoutForZone(zone,
    {lng:zone.coordinates[0][0],lat:zone.coordinates[0][1]}) : null, [asset.id, zone]);
  const structuredPark = useMemo(() => isParkTrio(zone) ? parkTrioLayout(zone,
    {lng:zone.coordinates[0][0],lat:zone.coordinates[0][1]}) : null, [zone]);
  const [width,setWidth] = useState(dimensions.width.toFixed(1));
  const [depth,setDepth] = useState(dimensions.depth.toFixed(1));
  const [degrees,setDegrees] = useState(dimensions.degrees.toFixed(0));
  const [outline,setOutline] = useState<ParkOutlineShape | ''>('');
  const [reshapeRejected,setReshapeRejected] = useState(false);
  const maxWidth = asset.maxWidth ?? asset.maxSize;
  const maxDepth = asset.maxDepth ?? asset.maxSize;
  // Fixed plots have read-only rounded labels. Rotate their exact saved
  // footprint; those display values must not shrink it or fail a fractional
  // native minimum (for example 25.148 m displayed as 25.1 m).
  const shapeWidth = fixedFixture ? dimensions.width : Number(width);
  const shapeDepth = fixedFixture ? dimensions.depth : Number(depth);
  const dimensionsValid = Number.isFinite(Number(width)) && Number.isFinite(Number(depth)) && Number.isFinite(Number(degrees))
    && (fixedFixture || (Number(width)>=asset.minWidth && Number(depth)>=asset.minDepth && Number(width)<=maxWidth && Number(depth)<=maxDepth));
  const flexibleProblem = useMemo(() => {
    if (!dimensionsValid || !isFlexiblePark(zone.properties)) return null;
    const candidate = reshapeParkOutline(zone.coordinates, Number(width), Number(depth), Number(degrees), outline || undefined);
    return flexibleParkFitProblem(candidate, zone.properties);
  }, [dimensionsValid, zone.coordinates, zone.properties, width, depth, degrees, outline]);
  const valid = dimensionsValid && !flexibleProblem;
  const button = 'min-h-11 rounded-lg border border-slate-700 bg-white px-3 text-sm font-semibold text-slate-900 disabled:opacity-40';
  return <aside aria-label="Reshape object" className="absolute bottom-4 inset-x-4 top-auto z-40 max-h-[42dvh] overflow-y-auto overscroll-contain rounded-xl border-2 border-slate-900 bg-[#fff9ec] p-3 shadow-xl sm:left-auto sm:w-72 sm:bottom-4 sm:top-28 sm:max-h-none">
    <div className="flex items-center justify-between"><h2 className="font-bold text-slate-900">{asset.label}</h2><button aria-label="Close reshape" onClick={onClose} className="flex h-11 w-11 items-center justify-center text-slate-900"><X size={18}/></button></div>
    <p className="mb-3 text-xs text-slate-600">{fixedFixture ? 'Fixed review model: move and rotate only. Extension is pending.' : isFlexiblePark(zone.properties) ? 'Drag white corners to make an irregular park. Add an outline point for more bends; the planted layout adapts when saved.' : isPark ? 'Drag the park to move it. Drag individual white corners to fit its outline to the site; use the orange handle to turn it.' : zone.properties?.native_home_plot === true ? 'Drag the Move handle on the selected plot to move this house. Use a corner to reshape or the orange handle to turn it.' : zone.properties?.native_plot_axes === true ? 'Drag the Move handle on the selected plot to move this building. Use a corner to reshape or the orange handle to turn it.' : 'Drag the object to move it. Drag a corner to reshape; use the orange handle to turn it.'}</p>
    {!isPark && !fixedFixture && onUpdateDesign && <BuildingDesignControls key={JSON.stringify([zone.id, zone.properties?.development_subcategory, zone.properties?.development_archetype_id, zone.properties?.development_selected_variant_id, zone.properties?.floors, zone.properties?.floor_count, zone.properties?.height, zone.properties?.height_m, zone.properties?.building_footprint_scale])} zone={zone} disabled={disabled} onSave={onUpdateDesign} />}
    {onUpdateParkLayout && <ParkLayoutControls key={`${zone.id}:${zone.updated_at}`} zone={zone} zones={zones} disabled={disabled} onSave={onUpdateParkLayout}/>}
    {isPark && !hasNativePark(zone) && onUpdateDesign && <ParkComponentControls key={`${zone.id}:${zone.properties?.skate_spectator_edge}`} zone={zone} disabled={disabled} onSave={onUpdateDesign} />}
    {isPark && onSaveDetails && <BenchDetailControls zone={zone} disabled={disabled} onSave={onSaveDetails} onEditingChange={onDetailsEditingChange}/>}
    {park && <div role="status" className="mb-3 rounded-lg bg-white p-2 text-xs text-slate-800">
      <p className="font-semibold">Current park · {park.status==='full'?'full programme':park.status==='compact'?'compact arrangement':park.loop.length?'reduced programme':'landscape layout'}</p>
      {park.notes.map(note=><p className="mt-1" key={note}>{note}</p>)}
    </div>}
    {structuredPark && structuredPark.notes.length > 0 && <div role="status" className="mb-3 rounded-lg bg-white p-2 text-xs text-slate-800">
      {structuredPark.notes.map(note=><p className="mt-1" key={note}>{note}</p>)}
    </div>}
    <form onSubmit={event => { event.preventDefault(); if(valid) { const problem = onReshape(keepOutline
      ? reshapeParkOutline(zone.coordinates,Number(width),Number(depth),Number(degrees),isPark ? outline || undefined : undefined)
      : rectangleAt(dimensions.center,shapeWidth,shapeDepth,Number(degrees)));
      setReshapeRejected(problem === false); } }}>
      {isPark && <div className="mb-3">
        <label className="text-xs font-semibold text-slate-800">Park outline<select aria-label="Park outline" value={outline} onChange={e=>setOutline(e.target.value as ParkOutlineShape | '')} className="mt-1 min-h-11 w-full rounded border border-slate-400 bg-white px-2 text-base text-slate-900">
          <option value="">Keep current outline</option><option value="rectangle">Rectangle</option><option value="triangle">Triangle</option><option value="l_shape">L shape</option>
        </select></label>
        <button type="button" className={`${button} mt-2 w-full`} disabled={disabled || zone.coordinates.length >= 128} onClick={()=>onReshape(addParkOutlinePoint(zone.coordinates))}>Add outline point</button>
        <p className="mt-2 text-xs text-slate-600">{isFlexiblePark(zone.properties) ? 'Resize keeps your outline. Paths and planting adapt to the saved shape; benches and trees keep their real size.' : 'Resize keeps your outline. Equipment and courts keep their real size; the selected complete layout must fit.'}</p>
      </div>}
      <div className="grid grid-cols-2 gap-2">
        <label className="text-xs font-semibold text-slate-800">Plot width (m)<input aria-label="Plot width (m)" disabled={fixedFixture} type="number" min={asset.minWidth} max={maxWidth} step="0.1" value={width} onChange={e=>setWidth(e.target.value)} className="mt-1 min-h-11 w-full rounded border border-slate-400 bg-white px-2 text-base text-slate-900" /></label>
        <label className="text-xs font-semibold text-slate-800">Plot depth (m)<input aria-label="Plot depth (m)" disabled={fixedFixture} type="number" min={asset.minDepth} max={maxDepth} step="0.1" value={depth} onChange={e=>setDepth(e.target.value)} className="mt-1 min-h-11 w-full rounded border border-slate-400 bg-white px-2 text-base text-slate-900" /></label>
      </div>
      <label className="mt-2 block text-xs font-semibold text-slate-800">Rotation (°)<input aria-label="Rotation (degrees)" type="number" step="1" value={degrees} onChange={e=>setDegrees(e.target.value)} className="ml-2 min-h-11 w-20 rounded border border-slate-400 bg-white px-2 text-base text-slate-900" /></label>
      <p className="my-3 text-xs text-slate-600">{asset.reshapeDescription}</p>
      {reshapeRejected && <p role="alert" className="mb-2 text-xs font-semibold text-red-700">Shape not saved. The existing plot is unchanged; check the placement message, then move the plot or try another size or angle.</p>}
      {!dimensionsValid && <p role="alert" className="mb-2 text-xs text-red-700">Use a width of {asset.minWidth}–{maxWidth} m and depth of {asset.minDepth}–{maxDepth} m.</p>}
      {flexibleProblem && <p role="alert" className="mb-2 text-xs text-red-700">{flexibleProblem}</p>}
      <button disabled={disabled||!valid} className={`${button} w-full !bg-[#c9ff3d]`}>{disabled?'Saving…':'Apply shape'}</button>
    </form>
    <div className="mt-2 grid grid-cols-2 gap-2"><button className={button} disabled={disabled} onClick={()=>onDuplicate(asset.id,Number(dimensions.width.toFixed(3)),Number(dimensions.depth.toFixed(3)),Number(dimensions.degrees.toFixed(3)))}>Place another</button><button className={button} disabled={disabled} onClick={onDelete}>Delete</button></div>
    {onConnections && <button onClick={onConnections} className={`${button} mt-3 w-full`}>Connections</button>}
    {onTerrace && !hasNativePark(zone) && <button onClick={onTerrace} className={`${button} mt-2 w-full`}>Terrace & path</button>}
    <button onClick={onMore} className="mt-2 min-h-11 text-xs text-slate-700 underline">More settings</button>
  </aside>;
}
