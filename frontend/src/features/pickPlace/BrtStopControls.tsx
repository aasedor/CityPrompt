import {useEffect,useState} from 'react';
import type {SiteZone,SiteZoneProperties} from '@/types';
import {extractZoneCenterline} from '@/utils/roadGeometry';
import {brtRouteProblem,type BrtStop} from '@/components/viewer/globe/brtStreetProgram';

export function BrtStopControls({zone,disabled,onSave}:{zone:SiteZone;disabled:boolean;
  onSave:(data:{coordinates:number[][];properties:SiteZoneProperties})=>void}) {
  const [distance,setDistance]=useState('32');
  const [editing,setEditing]=useState<string|null>(null);
  const [problem,setProblem]=useState<string|null>(null);
  const stops=zone.properties?.road_native_stops??[];
  useEffect(()=>{
    const pick=(event:Event)=>{
      const detail=(event as CustomEvent<{zoneId:string;stationM:number}>).detail;
      if(detail?.zoneId!==zone.id || !Number.isFinite(detail.stationM))return;
      setDistance(detail.stationM.toFixed(1));setEditing(null);setProblem(null);
    };
    window.addEventListener('cityprompt:brt-stop-position',pick);
    return()=>window.removeEventListener('cityprompt:brt-stop-position',pick);
  },[zone.id]);
  const save=(next:BrtStop[])=>{
    const points=extractZoneCenterline(zone),origin=points[0],sx=111320*Math.cos((origin?.[1]??0)*Math.PI/180);
    const error=brtRouteProblem(points.map(p=>({x:(p[0]-origin[0])*sx,y:(p[1]-origin[1])*111320})),next);
    setProblem(error);if(error)return;
    onSave({coordinates:zone.coordinates,properties:{...zone.properties,road_native_stops:next}});
    setEditing(null);
  };
  return <section aria-label="BRT stops" className="mb-3 rounded-lg border border-slate-300 p-2 text-sm text-slate-900">
    <h3 className="font-bold">Stations / stops</h3>
    <p className="my-2 text-xs">Right-click the selected route to choose a stop position, then add it here. Stops include the full platform, shelter, ramps and crossing.</p>
    <label className="block text-xs">Metres from the first route point
      <input aria-label="Stop distance from route start" type="number" step="0.1" value={distance} disabled={disabled}
        className="mt-1 min-h-11 w-full rounded border border-slate-400 bg-white px-2" onChange={e=>setDistance(e.target.value)}/>
    </label>
    <button type="button" disabled={disabled || !distance.trim()} className="mt-2 min-h-11 w-full rounded border border-slate-700 bg-white font-semibold disabled:opacity-40"
      onClick={()=>{const stop={id:editing??crypto.randomUUID(),stationM:Number(distance)};save(editing?stops.map(s=>s.id===editing?stop:s):[...stops,stop]);}}>
      {editing?'Move stop':'Add station / stop'}
    </button>
    {editing && <button className="min-h-11 underline" onClick={()=>{setEditing(null);setProblem(null);}}>Cancel move</button>}
    {problem && <p role="alert" className="mt-2 text-xs text-red-800">{problem}</p>}
    {stops.map((stop,index)=><div key={stop.id} className="mt-2 border-t border-slate-200 pt-1">
      <span>Stop {index+1} · {stop.stationM.toFixed(1)} m</span>
      <div className="flex gap-4"><button disabled={disabled} className="min-h-11 underline" onClick={()=>{setEditing(stop.id);setDistance(String(stop.stationM));setProblem(null);}}>Move stop {index+1}</button>
        <button disabled={disabled} className="min-h-11 underline" onClick={()=>save(stops.filter(s=>s.id!==stop.id))}>Remove stop {index+1}</button></div>
    </div>)}
  </section>;
}
