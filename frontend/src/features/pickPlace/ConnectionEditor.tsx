import { useMemo, useState } from 'react';
import type { SiteZone } from '@/types';
import { StudioDialog } from '@/features/projects/StudioControls';
import { resolveManualParkAccess } from '@/components/viewer/globe/parkAccessConnections';
import { rectangleDimensions } from './geometry';
import { streetAssetForZone } from './streetPlacement';
import { EMPTY_TRANSPORT, type ExistingTransport } from '@/features/referenceLayers/existingTransport';
import { readBuildingEntrance, readCrossings, resolvePedestrianConnections, type BuildingEntrance, type StreetCrossing } from './pedestrianConnections';

const field='min-h-11 w-full rounded border border-slate-400 bg-white px-2 text-base text-slate-900';
const button='min-h-11 rounded-lg border border-slate-700 bg-white px-3 text-sm font-semibold text-slate-900 disabled:opacity-40';
const displayMetres = (value: number) => Math.round(value*1000)/1000;
export function ConnectionEditor({ zone, zones, visibleIds, disabled, onSave, onClose, transportContext=EMPTY_TRANSPORT }: {
  zone: SiteZone; zones: SiteZone[]; disabled: boolean;
  visibleIds?: string[];
  transportContext?: ExistingTransport;
  onSave: (properties: SiteZone['properties']) => Promise<unknown>; onClose: () => void;
}) {
  const isPark=zone.zone_type==='green_space', isStreet=zone.zone_type==='road';
  const dimensions=rectangleDimensions(zone.coordinates);
  const existing=readBuildingEntrance(zone);
  const park=zone.properties?.pedestrian_park_entrance as {edge:number;position:number;streetId:string;existingGroundConfirmed?:boolean}|undefined;
  const roads=zones.filter(z=>z.zone_type==='road' && !z.id.startsWith('temp-') && (!visibleIds || visibleIds.includes(z.id)));
  const roadLabel = (road: SiteZone) => road.name?.trim() || streetAssetForZone(road)?.label || 'Street';
  const roadOptionLabel = (road: SiteZone) => {
    const label = roadLabel(road), matches = roads.filter(candidate => roadLabel(candidate) === label);
    return matches.length > 1 ? `${label} ${matches.findIndex(candidate => candidate.id === road.id) + 1}` : label;
  };
  const [enabled,setEnabled]=useState(isPark ? Boolean(park) : Boolean(existing));
  const [streetId,setStreetId]=useState(existing?.streetId ?? park?.streetId ?? roads[0]?.id ?? '');
  const [groundConfirmed,setGroundConfirmed]=useState(park?.existingGroundConfirmed ?? false);
  const mappedPaths=useMemo(()=>transportContext.lines.filter(line=>line.kind==='path').map(line=>{
    const origin=dimensions.center, sx=111320*Math.cos(origin[1]*Math.PI/180);
    const local=(p:number[])=>[(p[0]-origin[0])*sx,(p[1]-origin[1])*111320];
    const distance=Math.min(...line.points.slice(1).map((end,i)=>{
      const a=local(line.points[i]),b=local(end),dx=b[0]-a[0],dy=b[1]-a[1];
      const t=Math.max(0,Math.min(1,-(a[0]*dx+a[1]*dy)/Math.max(1e-8,dx*dx+dy*dy)));
      return Math.hypot(a[0]+t*dx,a[1]+t*dy);
    }));
    return {...line,distance};
  }).filter(line=>line.distance<100 || line.id===streetId).sort((a,b)=>a.distance-b.distance).slice(0,30),[transportContext,dimensions.center,streetId]);
  const [x,setX]=useState(displayMetres(existing ? existing.xM*(existing.scaleWithPlot?dimensions.width/existing.referenceWidthM:1) : 0));
  const [y,setY]=useState(displayMetres(existing ? existing.yM*(existing.scaleWithPlot?dimensions.depth/existing.referenceDepthM:1) : -dimensions.depth/2+2));
  const [scale,setScale]=useState(existing?.scaleWithPlot ?? zone.properties?.native_home_plot !== true);
  const [width,setWidth]=useState(existing?.widthM ?? 1.8);
  const [edge,setEdge]=useState(park?.edge ?? 0),[position,setPosition]=useState(park?.position ?? 0.5);
  const [crossings,setCrossings]=useState<StreetCrossing[]>(()=>readCrossings(zone));
  const [busy,setBusy]=useState(false),[error,setError]=useState('');
  const properties=useMemo(()=>{
    if(isStreet)return {...zone.properties,pedestrian_crossings:crossings};
    if(isPark)return {...zone.properties,park_access_points:null,pedestrian_park_entrance:enabled ? {version:1,edge,position,streetId,existingGroundConfirmed:groundConfirmed}:null};
    const anchor:BuildingEntrance={version:1,xM:x,yM:y,referenceWidthM:dimensions.width,referenceDepthM:dimensions.depth,
      scaleWithPlot:scale,streetId,widthM:width};
    return {...zone.properties,pedestrian_building_entrance:enabled ? anchor:null};
  },[zone.properties,isStreet,isPark,crossings,enabled,edge,position,streetId,x,y,dimensions.width,dimensions.depth,scale,width,groundConfirmed]);
  const preview=useMemo(()=>{
    const next=zones.map(z=>z.id===zone.id?{...zone,properties}:z);
    return isPark ? resolveManualParkAccess(next,{},visibleIds?.filter(id=>zones.some(z=>z.id===id&&z.zone_type==='road')),transportContext).parks.filter(p=>p.parkZoneId===zone.id).map(p=>p.reason ?? 'Entrance connects to the selected sidewalk or mapped path.')
      : resolvePedestrianConnections(next,visibleIds).filter(p=>p.ownerId===zone.id).map(p=>p.reason);
  },[zones,zone,properties,isPark,visibleIds,transportContext]);
  const supported=isPark ? preview.length>0 : isStreet || zone.coordinates.length===4;
  const valid = isStreet ? crossings.every(c=>Number.isFinite(c.position)&&c.position>=0&&c.position<=1&&c.widthM>=1.8&&c.widthM<=5)
    : !enabled || Boolean(streetId) && (isPark ? Number.isFinite(position)&&position>=0&&position<=1
      : Number.isFinite(x)&&Number.isFinite(y)&&width>=1.2&&width<=4&&Math.abs(x)<=500&&Math.abs(y)<=500);
  return <StudioDialog title="Connections" onClose={onClose}>
    <form className="space-y-4 text-slate-900" onSubmit={async event=>{
      event.preventDefault();if(!valid||disabled||busy)return;setBusy(true);setError('');
      try{await onSave(properties);onClose();}catch{setError('Could not save. Your changes are still here; retry or close.');}finally{setBusy(false);}
    }}>
      <p className="text-sm font-semibold">{zone.name || (isPark?'Park':isStreet?'Street':'Building')}</p>
      {isStreet ? <>
        <p className="text-sm">Add a raised crossing where people should cross. Its position follows this street when you move or reshape it.</p>
        {crossings.map((crossing,index)=><fieldset key={crossing.id} className="rounded-lg border border-slate-300 p-3 space-y-2">
          <legend>Crossing {index+1}</legend>
          <label className="block text-sm">Position along street (%)<input className={field} type="number" min="0" max="100" step="1" value={Math.round(crossing.position*100)} onChange={e=>setCrossings(items=>items.map(c=>c.id===crossing.id?{...c,position:e.target.valueAsNumber/100}:c))}/></label>
          <label className="block text-sm">Crossing width (m)<input className={field} type="number" min="1.8" max="5" step="0.1" value={crossing.widthM} onChange={e=>setCrossings(items=>items.map(c=>c.id===crossing.id?{...c,widthM:e.target.valueAsNumber}:c))}/></label>
          <button className={button} type="button" onClick={()=>setCrossings(items=>items.filter(c=>c.id!==crossing.id))}>Remove crossing {index+1}</button>
        </fieldset>)}
        <button className={button} type="button" disabled={crossings.length>=8} onClick={()=>setCrossings(items=>[...items,{id:crypto.randomUUID(),position:0.5,widthM:3}])}>Add crossing</button>
        <p className="text-xs text-slate-600">Keep crossings clear of bends and intersections. These are design proposals; review slopes, visibility and local requirements.</p>
      </> : <>
        {!supported && <p role="alert" className="text-sm">{isPark?'Editable entrances are available for the neighbourhood and pocket park layouts and the park trio. This park needs a compatible path network first.':'Entrance anchors currently require a rectangular building plot.'}</p>}
        <label className="flex min-h-11 items-center gap-2"><input type="checkbox" disabled={!supported} checked={enabled} onChange={e=>setEnabled(e.target.checked)}/>{isPark?'Choose and lock a park entrance':'Link an entrance to a sidewalk'}</label>
        {isPark && Array.isArray(zone.properties?.park_access_points) && <p className="text-sm">Saving here replaces this park’s older authored access points with the settings shown below.</p>}
        {isPark && !enabled && <p className="text-sm">The park will choose a nearby suitable sidewalk automatically.</p>}
        {enabled && <>
          <label className="block text-sm">Sidewalk target<select className={field} value={streetId} onChange={e=>{setStreetId(e.target.value);setGroundConfirmed(false);}}><option value="">Choose a street or path</option>{roads.map(road=><option key={road.id} value={road.id}>{roadOptionLabel(road)}</option>)}{isPark&&<optgroup label="Existing mapped paths · nearest first">{mappedPaths.map(path=><option key={path.id} value={path.id}>{Math.round(path.distance)} m · {path.label} · {path.id.slice(-8)}</option>)}</optgroup>}</select></label>
          {isPark&&streetId.startsWith('existing:')&&<div className="rounded-lg bg-blue-50 p-3 text-sm">
            <p>Uses the recorded path width where available, otherwise its centreline. Check the Google scene: shared access routes may also carry vehicles, and mapped data does not establish precise curbs or elevation.</p>
            <label className="mt-2 flex min-h-11 items-center gap-2"><input type="checkbox" checked={groundConfirmed} onChange={e=>setGroundConfirmed(e.target.checked)}/>I checked that this is suitable pedestrian access at ground level</label>
          </div>}
          {isPark ? <>
            <label className="block text-sm">Entrance edge<select className={field} value={edge} onChange={e=>setEdge(Number(e.target.value))}>{zone.coordinates.map((_,i)=><option value={i} key={i}>{['Front','Right','Back','Left'][i] ?? `Edge ${i+1}`} · edge {i+1}</option>)}</select></label>
            <label className="block text-sm">Position along edge (%)<input className={field} type="number" min="0" max="100" value={Math.round(position*100)} onChange={e=>setPosition(e.target.valueAsNumber/100)}/></label>
            <p className="text-xs text-slate-600">The chosen edge and position rotate and resize with the park. If this entrance cannot connect, it stays unresolved.</p>
          </> : <>
            <p className="text-sm">Position the anchor at the door or foot of its entrance steps. Distances are from the plot centre in its own orientation.</p>
            <div className="grid grid-cols-2 gap-3">
              <label className="text-sm">Left / right (m)<input className={field} type="number" step="0.1" value={x} onChange={e=>setX(e.target.valueAsNumber)}/></label>
              <label className="text-sm">Front / back (m)<input className={field} type="number" step="0.1" value={y} onChange={e=>setY(e.target.valueAsNumber)}/></label>
            </div>
            <p className="text-xs text-slate-600">Negative values mean left or front; positive values mean right or back. Review the walkway against the actual door in 3D.</p>
            <label className="flex min-h-11 items-center gap-2 text-sm"><input type="checkbox" checked={scale} onChange={e=>setScale(e.target.checked)}/>Scale entrance offsets when the plot is resized</label>
            <p className="text-xs text-slate-600">Keep this off for an unscaled catalogue house. One entrance serves this plot; check its position if resizing adds more houses.</p>
            <label className="block text-sm">Walkway width (m)<input className={field} type="number" min="1.2" max="4" step="0.1" value={width} onChange={e=>setWidth(e.target.valueAsNumber)}/></label>
          </>}
        </>}
      </>}
      <div role="status" className="space-y-1 rounded-lg bg-slate-100 p-3 text-sm">{preview.length ? preview.map((message,i)=><p key={i}>{message}</p>):<p>No connections selected.</p>}</div>
      {error && <p role="alert" className="text-sm text-red-700">{error}</p>}
      <div className="flex gap-2"><button className={`${button} !bg-[#c9ff3d]`} disabled={!supported||!valid||disabled||busy}>{busy?'Saving…':'Save connections'}</button><button className={button} type="button" onClick={onClose}>Cancel</button></div>
    </form>
  </StudioDialog>;
}
