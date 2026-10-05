import { lazy, Suspense, useCallback, useState } from 'react';
import { useAuthStore } from '@/store';
import type { SiteZone } from '@/types';
import { getActiveSiteBoundary } from '@/utils/siteBoundary';
import type { ReferenceLayer } from './api';
import type { Position, ZoningOverlay } from './zoningLabels';
import { studyMetadata } from './zoningStudy';

const Editor=lazy(()=>import('./ZoningStudyEditor'));
export function ZoningStudyPanel({ projectId, projectName, zones, layers, canEdit, isLoading, zoningData, hiddenIds, onToggle }: {
  projectId:string; projectName:string; zones:SiteZone[]; layers:ReferenceLayer[]; canEdit:boolean; isLoading:boolean;
  zoningData?:ZoningOverlay; hiddenIds:Set<string>; onToggle:(id:string)=>void;
}) {
  const accountId=useAuthStore(state=>state.user?.id??'signed-out');
  const boundary=getActiveSiteBoundary(zones);
  const [open,setOpen]=useState(false);
  const close=useCallback(()=>setOpen(false),[]);
  const studies=layers.filter(layer=>studyMetadata(layer));
  return <section aria-label="Student zoning studies" className="max-w-sm space-y-3 rounded-2xl border border-[#151515]/20 bg-[#fffdf6]/95 p-3 text-[#151515] shadow-lg">
    <h3 className="text-sm font-bold">Zoning map studio</h3>
    <p className="text-xs leading-relaxed text-[#5c554d]">Redraw existing conditions and proposed land use as separate graphic layers. Export a styled map for your presentation.</p>
    <button className="min-h-11 w-full rounded-xl border border-[#151515] bg-[#c9ff3d] px-3 py-2 text-xs font-semibold disabled:opacity-50" disabled={!boundary||isLoading} onClick={()=>setOpen(true)}>Open zoning map studio</button>
    {!boundary&&<p className="text-xs">Draw a site boundary first.</p>}
    {studies.map(layer=><label key={layer.id} className="flex min-h-11 items-center justify-between gap-2 text-xs">{layer.name}<input type="checkbox" className="h-5 w-5 accent-[#151515]" checked={!hiddenIds.has(layer.id)} onChange={()=>onToggle(layer.id)}/></label>)}
    {open&&boundary&&<Suspense fallback={<p role="status" className="text-xs">Opening map studio…</p>}><Editor key={JSON.stringify([accountId,projectId,boundary.id,boundary.coordinates])} projectId={projectId} accountId={accountId} projectName={projectName} boundaryId={boundary.id} boundary={boundary.coordinates.map(([x,y])=>[x,y] as Position)} layers={layers} canEdit={canEdit} zoningData={zoningData} onClose={close}/></Suspense>}
  </section>;
}
