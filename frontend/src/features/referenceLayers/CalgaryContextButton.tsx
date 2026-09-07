import { useRef, useState } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import type { SiteZone } from '@/types';
import { getActiveSiteBoundary } from '@/utils/siteBoundary';
import { referenceLayerQueryKey, referenceLayersApi, type ReferenceLayer } from './api';
import { CALGARY_TRANSPORT_ROOT, fetchCalgaryTransport } from './existingTransport';

export function CalgaryContextButton({projectId,zones,layers}:{projectId:string;zones:SiteZone[];layers:ReferenceLayer[]}) {
  const client=useQueryClient(),busyRef=useRef(false);
  const [busy,setBusy]=useState(false),[message,setMessage]=useState('');
  const boundary=getActiveSiteBoundary(zones),loaded=layers.some(layer=>layer.source_url===CALGARY_TRANSPORT_ROOT);
  return <div className="max-w-sm space-y-1">
    <button type="button" className="min-h-11 w-full rounded-full border-2 border-[#151515] bg-white px-3 text-sm font-bold disabled:opacity-50"
      disabled={!boundary||loaded||busy} onClick={async()=>{
        if(!boundary||busyRef.current)return;
        busyRef.current=true;setBusy(true);setMessage('');
        const lngs=boundary.coordinates.map(p=>p[0]),lats=boundary.coordinates.map(p=>p[1]);
        const lat=(Math.min(...lats)+Math.max(...lats))/2,dy=100/111320,dx=dy/Math.cos(lat*Math.PI/180);
        try {
          const features=await fetchCalgaryTransport([Math.min(...lngs)-dx,Math.min(...lats)-dy,Math.max(...lngs)+dx,Math.max(...lats)+dy],AbortSignal.timeout(30_000));
          await referenceLayersApi.import(projectId,new File([JSON.stringify({type:'FeatureCollection',features})],'calgary-existing-transport.geojson',{type:'application/geo+json'}),{
            name:'Calgary existing streets & paths',kind:'reference',source_url:CALGARY_TRANSPORT_ROOT,
            description:`City of Calgary public street centreline and pathway services. Snapshot ${new Date().toISOString().slice(0,10)}. Includes 100 m around the site. Lines show mapped routes, not surveyed curbs or complete sidewalk coverage. Pathway reuse terms require confirmation before redistribution.`});
          await client.invalidateQueries({queryKey:referenceLayerQueryKey(projectId)});
          setMessage('Nearby routes loaded. Select a park and open Connections to choose an existing path.');
        }catch(error){setMessage(error instanceof Error?error.message:'Context could not load. Try again.');}
        finally{busyRef.current=false;setBusy(false);}
      }}>{busy?'Loading nearby routes…':loaded?'Calgary routes loaded':'Load nearby Calgary streets & paths'}</button>
    <p className="text-xs text-slate-600">{!boundary?'Draw a site boundary first.':'Pilot · Existing routes stay separate from your design. Hide the overlay for a clean view; saved connections stay active.'}</p>
    {message&&<p role="status" className="text-sm text-slate-700">{message}</p>}
  </div>;
}
