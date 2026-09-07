import { useMemo, useState } from 'react';
import type { SiteZone } from '@/types';
import { terraceOffset } from '@/components/viewer/globe/terraceDefinition';
import { buildTerraceScene, readTerracePath, suggestTerracePath, type TerracePathDefinition } from '@/components/viewer/globe/terraceScene';
import { assetForZone } from './catalogue';
import { metersPerDegLon, METERS_PER_DEG_LAT } from '@/components/viewer/mapEngine/geoUtils';

function EntrancePreview({source,target,points}:{source:SiteZone;target?:SiteZone;points:number[][]}) {
  const rings=[source,...(target?[target]:[])];
  const origin=source.coordinates[0],east=metersPerDegLon(origin[1]);
  const local=(p:number[])=>[(p[0]-origin[0])*east,-(p[1]-origin[1])*METERS_PER_DEG_LAT];
  const coords=rings.flatMap(z=>z.coordinates.map(local)),minX=Math.min(...coords.map(p=>p[0]))-4,minY=Math.min(...coords.map(p=>p[1]))-4;
  const width=Math.max(...coords.map(p=>p[0]))-minX+4,height=Math.max(...coords.map(p=>p[1]))-minY+4;
  return <svg role="img" aria-label="Entrance plan: purple is this object, green is destination; numbered edges match the entrance controls" className="my-2 h-44 w-full rounded bg-white" viewBox={`${minX} ${minY} ${width} ${height}`}>
    {rings.map((z,index)=><g key={z.id}><polygon points={z.coordinates.map(p=>local(p).join(',')).join(' ')} fill={index?'#dcfce7':'#ede9fe'} stroke={index?'#166534':'#6d28d9'} strokeWidth=".3"/>{z.coordinates.map((p,i)=>{const a=local(p),b=local(z.coordinates[(i+1)%z.coordinates.length]);return <text key={i} x={(a[0]+b[0])/2} y={(a[1]+b[1])/2} textAnchor="middle" fontSize="2.5">{i}</text>;})}</g>)}
    {points.length>1&&<polyline points={points.map(p=>local(p).join(',')).join(' ')} fill="none" stroke="#b45309" strokeWidth="1"/>}
  </svg>;
}

/** Optional concept grading; changes use the ordinary zone save/undo history. */
export function TerraceEditor({zone,zones,disabled,onSave,onClose}:{zone:SiteZone;zones:SiteZone[];disabled:boolean;onSave:(properties:SiteZone['properties'])=>Promise<void>;onClose:()=>void}) {
  const [enabled,setEnabled]=useState(terraceOffset(zone)!==null);
  const [offset,setOffset]=useState(String(terraceOffset(zone)??0));
  const [pathEnabled,setPathEnabled]=useState(Boolean(readTerracePath(zone)));
  const [path,setPath]=useState<TerracePathDefinition>(readTerracePath(zone)??{version:1,targetId:'',sourceEdge:0,targetEdge:0,sourcePosition:.5,targetPosition:.5,widthM:2,approachM:2});
  const [error,setError]=useState('');
  const [saving,setSaving]=useState(false);
  const candidates=zones.filter(z=>z.id!==zone.id&&['building','residential','green_space'].includes(z.zone_type));
  const properties={...zone.properties,proposed_terrace:enabled?{version:1,offsetM:Number(offset)}:null,terrace_connection:pathEnabled?path:null};
  const preview=useMemo(()=>buildTerraceScene(zones.map(z=>z.id===zone.id?{...z,properties:{...z.properties,proposed_terrace:enabled?{version:1,offsetM:Number(offset)}:null,terrace_connection:pathEnabled?path:null}}:z),0),[zones,zone.id,enabled,offset,pathEnabled,path]);
  const result=preview.paths.find(p=>p.ownerId===zone.id);
  const valid=(!enabled||(offset.trim()!==''&&Number.isFinite(Number(offset))&&Math.abs(Number(offset))<=20))&&(!pathEnabled||Boolean(readTerracePath({...zone,properties})));
  const input='mt-1 min-h-11 w-full rounded border border-slate-400 bg-white px-2 text-base text-slate-900';
  const numberField=(label:string,key:'sourceEdge'|'targetEdge'|'sourcePosition'|'targetPosition'|'widthM'|'approachM',min:number,max:number,step:number)=> <label className="text-xs font-semibold">{label}<input aria-label={label} className={input} type="number" min={min} max={max} step={step} value={Number.isFinite(path[key])?path[key]:''} onChange={e=>setPath({...path,[key]:e.target.valueAsNumber})}/></label>;
  if(zone.properties?.park_terrain) return <aside aria-label="Park terrain" className="absolute right-4 top-20 z-50 w-[min(24rem,calc(100%-2rem))] rounded-xl border-2 border-slate-900 bg-[#fff9ec] p-4 text-slate-900 shadow-xl">
    <h2 className="font-bold">This park follows the hillside</h2><p className="my-3 text-sm">Lawn and paths use the measured ground. Only activity pads stay level. After moving or resizing the park, open Review ground to measure its new location. The old terrace connector needs a new graded alignment.</p>
    <button className="min-h-11 px-3" onClick={onClose}>Close</button>
  </aside>;
  return <aside aria-label="Terrace and path" className="absolute right-4 top-20 z-50 max-h-[80dvh] w-[min(24rem,calc(100%-2rem))] overflow-y-auto rounded-xl border-2 border-slate-900 bg-[#fff9ec] p-4 text-slate-900 shadow-xl">
    <div className="flex items-center justify-between"><h2 className="font-bold">Terrace & path · pilot</h2><button className="min-h-11 px-3" aria-label="Close terrace editor" onClick={onClose}>Close</button></div>
    <p className="mb-3 text-sm">The terrace follows this object's plot when you move or reshape it. Start with a level prepared site in Ground review.</p>
    {preview.base===null&&<p role="alert">Prepare the site ground before adding terraces.</p>}
    <form onSubmit={async e=>{e.preventDefault();if(!valid||preview.base===null||saving)return;setSaving(true);setError('');try{await onSave(properties);onClose();}catch{setError('Could not save. Your draft is still here; try again.');}finally{setSaving(false);}}}>
      <label className="flex min-h-11 items-center gap-2"><input type="checkbox" checked={enabled} onChange={e=>setEnabled(e.target.checked)}/>Use a level terrace</label>
      {enabled&&<label className="block text-sm">Height above site ground (m)<input aria-label="Terrace height offset" className={input} type="number" min={-20} max={20} step="0.1" value={offset} onChange={e=>setOffset(e.target.value)}/><span className="text-xs">Negative values lower the terrace. Changing the site level shifts all terraces together.</span></label>}
      <label className="mt-3 flex min-h-11 items-center gap-2"><input type="checkbox" checked={pathEnabled} onChange={e=>setPathEnabled(e.target.checked)}/>Connect to another terrace</label>
      {pathEnabled&&<>
        <label className="block text-sm">Destination<select aria-label="Terrace destination" className={input} value={path.targetId} onChange={e=>setPath({...path,targetId:e.target.value,targetEdge:0})}><option value="">Choose an object</option>{candidates.map(z=><option key={z.id} value={z.id}>{z.name||assetForZone(z)?.label||z.zone_type}</option>)}</select></label>
        <button type="button" className="mt-2 min-h-11 w-full rounded border border-slate-600 bg-white disabled:opacity-40" disabled={!path.targetId} onClick={()=>{const suggestion=suggestTerracePath(zones.map(z=>z.id===zone.id?{...z,properties}:z),zone.id,path.targetId,path);if(suggestion){setPath(suggestion);setError('');}else setError('No clear route found. Move the objects or adjust the entrances.');}}>Find a clear connection</button>
        <EntrancePreview source={zone} target={candidates.find(z=>z.id===path.targetId)} points={result?.points??[]}/>
        <p className="my-2 text-xs">Choose facing plot edges (numbered from 0 in drawing order). The path reaches the neighbourhood park loop. Align the building approach with the foot of its entrance steps; this pilot does not locate doors automatically.</p>
        <details><summary className="min-h-11 cursor-pointer py-2 text-sm">Adjust entrances and width</summary><div className="grid grid-cols-2 gap-2">
          {numberField('From edge','sourceEdge',0,zone.coordinates.length-1,1)}
          {numberField('To edge','targetEdge',0,(candidates.find(z=>z.id===path.targetId)?.coordinates.length??1)-1,1)}
          {numberField('From position (0–1)','sourcePosition',0,1,.05)}
          {numberField('To position (0–1)','targetPosition',0,1,.05)}
          {numberField('Path width (m)','widthM',1.2,4,.1)}
          {numberField('Building approach (m)','approachM',0,10,.1)}
        </div></details>
        <p role="status" className="my-3 rounded bg-white p-2 text-sm">{result?.reason??'Choose a destination.'}</p>
      </>}
      <p className="my-3 text-xs">Concept grading only. Retaining edges, drainage, landings and accessible routes need further design. Steep routes remain editable.</p>
      {error&&<p role="alert">{error}</p>}
      <button className="min-h-11 w-full rounded-lg border border-slate-900 bg-[#c9ff3d] font-bold disabled:opacity-40" disabled={disabled||saving||!valid||preview.base===null}>{saving?'Saving…':'Save terrace and path'}</button>
    </form>
  </aside>;
}
