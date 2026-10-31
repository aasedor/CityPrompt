import { useEffect, useMemo, useState } from 'react';
import type { SiteZone, SiteZoneProperties } from '@/types';
import { nativeParkLayouts, nativeParkProperties, nativeParkFitProblem, readNativePark, type NativeParkLayout } from './nativeParkRegistry';
import { rectangleAt } from '@/features/pickPlace/geometry';
import { parkOutlineDimensions } from '@/features/pickPlace/parkOutline';
import { snapPlacement } from '@/features/pickPlace/snapPlacement';
import { getActiveSiteBoundary } from '@/utils/siteBoundary';
import { isFlexiblePark } from './flexibleParkFit';
import { courtSportGroup } from '@/features/pickPlace/courtCatalogueGroups';
import { COURT_ONLY_SPORT_ASSETS, isPlaceable } from '@/features/pickPlace/assetRegistry';

export function parkLayoutProposal(zone:SiteZone,layout:NativeParkLayout,zones:SiteZone[]) {
  const d=parkOutlineDimensions(zone.coordinates);
  // Rectangular parcels may grow in the explicit preview; freeform outlines stay intact.
  const rectangular=zone.coordinates.length===4 && d.normalized.every(([x,y])=>
    Math.min(Math.abs(x),Math.abs(x-1))<.0001 && Math.min(Math.abs(y),Math.abs(y-1))<.0001);
  const previous=readNativePark(zone);
  const coordinates=layout.archetypeId.startsWith('court_only_')
    ? rectangleAt(previous?[previous.selection.frame.longitude,previous.selection.frame.latitude]:d.center,
      layout.occupiedWidthM,layout.occupiedDepthM,previous?previous.selection.frame.yaw*180/Math.PI:d.degrees)
    : rectangular && (d.width<layout.occupiedWidthM-.02 || d.depth<layout.occupiedDepthM-.02)
    ? rectangleAt(d.center,Math.max(d.width,layout.occupiedWidthM),Math.max(d.depth,layout.occupiedDepthM),d.degrees) : zone.coordinates;
  const properties=nativeParkProperties(zone.properties??{},layout,coordinates);
  if (previous) properties.green_space_native_layout={
    layout_id:layout.id,content_revision:layout.contentRevision,frame:{...previous.selection.frame},
  };
  properties.pick_place_asset=`native-park:${layout.variantId}--native-v1`;
  properties.green_space_native_layout_id=layout.id;
  const fit=nativeParkFitProblem({...zone,coordinates,properties});
  // Preview never silently moves the proposed park to a different location.
  const spatial=snapPlacement(coordinates,zones,getActiveSiteBoundary(zones),zone.id,properties);
  return {coordinates,properties,problem:fit ?? (spatial.snapped?'This layout needs more room here. Enlarge or move the park first.':spatial.problem)};
}
export function ParkLayoutControls({zone,zones,disabled,onSave}:{zone:SiteZone;zones:SiteZone[];disabled:boolean;
  onSave:(data:{coordinates:number[][];properties:SiteZoneProperties})=>Promise<unknown>}) {
  const current=readNativePark(zone);
  const choices=useMemo(()=>{
    if(isFlexiblePark(zone.properties))return [];
    const sport=courtSportGroup(zone.properties?.green_space_archetype_id);
    return nativeParkLayouts.filter(p=>p.status==='pilot' && (p.variantId===zone.properties?.green_space_selected_variant_id
      || (sport && sport.aliases.includes(p.archetypeId)
        && (!p.archetypeId.startsWith('court_only_') || COURT_ONLY_SPORT_ASSETS.some(asset=>asset.model.variantId===p.variantId&&isPlaceable(asset))))));
  },[zone.properties]);
  const [selected,setSelected]=useState(current?.layout.id??choices[0]?.id??'');
  const [preview,setPreview]=useState(false),[saving,setSaving]=useState(false),[error,setError]=useState('');
  useEffect(()=>{
    setSelected(current?.layout.id??choices[0]?.id??'');setPreview(false);setError('');
  },[zone.id,current?.layout.id,choices]);
  const layout=choices.find(p=>p.id===selected);
  const proposal=useMemo(()=>layout?parkLayoutProposal(zone,layout,zones):null,[zone,zones,layout]);
  if(!choices.length)return null;
  const locked=disabled||saving;
  return <section aria-label="Park layout" className="mb-3 rounded-lg border border-slate-300 bg-white p-2 text-slate-900">
    <label className="text-sm font-semibold">{current?'Park layout':'Upgrade to the complete park'}
      <select aria-label="Park layout" className="mt-1 min-h-11 w-full rounded border px-2 text-sm" value={selected} disabled={locked}
        onChange={e=>{setSelected(e.target.value);setPreview(false);setError('');}}>
        {choices.map(p=><option key={p.id} value={p.id}>{p.archetypeId.startsWith('court_only_')?'Court only':p.label} · {p.widthM} × {p.depthM} m</option>)}
      </select>
    </label>
    <p className="my-2 text-xs">Dashed amber outline: reserved park parcel. Solid green outline: the fixed park layout inside it.</p>
    {current && <p className="my-2 text-xs font-semibold">Parcel: {parkOutlineDimensions(zone.coordinates).width.toFixed(1)} × {parkOutlineDimensions(zone.coordinates).depth.toFixed(1)} m. Fixed layout: {current.layout.widthM} × {current.layout.depthM} m.</p>}
    <p className="my-2 text-xs">{zone.properties?.court_only_native===true?'Court dimensions stay fixed. Choose a complete park layout to add the surrounding features.':'Enlarging the parcel reserves more space; it does not extend paving or stretch equipment. Use Add details → Custom paving to draw extra paved areas.'}</p>
    {layout && (layout.occupiedWidthM>layout.widthM || layout.occupiedDepthM>layout.depthM) && <p className="mb-2 text-xs">Placement space: {layout.occupiedWidthM} × {layout.occupiedDepthM} m, including projecting details.</p>}
    {!preview?<button className="min-h-11 w-full rounded border text-sm font-semibold" disabled={locked||current?.layout.id===selected}
      onClick={()=>setPreview(true)}>Preview layout</button>:<>
      {layout&&<svg role="img" aria-label={`${layout.label} layout preview`} viewBox={`0 0 ${layout.widthM} ${layout.depthM}`} className="my-2 w-full rounded bg-[#5b713e]">
        {layout.variantId==='basketball_court_v1'?(layout.mode==='module_assembly'?[-20,20]:[0]).map(x=><g key={x}>
          <rect x={layout.widthM/2+x-18} y={layout.depthM/2-11.5} width="36" height="23" fill="#4c8399" stroke="#fff" strokeWidth=".2"/>
          <rect x={layout.widthM/2+x-14} y={layout.depthM/2-7.5} width="28" height="15" fill="none" stroke="#fff" strokeWidth=".2"/>
          <circle cx={layout.widthM/2+x} cy={layout.depthM/2} r="1.8" fill="none" stroke="#fff" strokeWidth=".2"/>
        </g>):<text x="50%" y="50%" textAnchor="middle" fill="white" fontSize="3">Original native layout</text>}
      </svg>}
      <p className="text-xs">Preview: {layout?.widthM} × {layout?.depthM} m. Apply saves the layout and any shown parcel enlargement together.</p>
      {(proposal?.problem||error)&&<p role="alert" className="my-2 text-xs text-red-700">{proposal?.problem||error}</p>}
      <div className="mt-2 flex gap-2"><button className="min-h-11 flex-1 rounded bg-[#c9ff3d] text-sm font-semibold disabled:opacity-40" disabled={locked||!proposal||!!proposal.problem}
        onClick={async()=>{if(!proposal)return;setSaving(true);setError('');try{await onSave({coordinates:proposal.coordinates,properties:proposal.properties});setPreview(false);}catch{setError('The layout was not saved. Your previous park is unchanged; try again.');}finally{setSaving(false);}}}>{saving?'Saving…':'Apply layout'}</button>
        <button className="min-h-11 flex-1 rounded border text-sm" disabled={saving} onClick={()=>{setPreview(false);setSelected(current?.layout.id??choices[0].id);setError('');}}>Cancel</button></div>
    </>}
  </section>;
}
