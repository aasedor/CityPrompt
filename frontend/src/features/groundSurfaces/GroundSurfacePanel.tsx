import type {SiteZone,SiteZoneProperties} from '@/types';
import {GROUND_SURFACES,groundSurfaceFor} from './groundSurfaces';
export function GroundSurfacePanel({zone,disabled,onChange,onClose,onDelete}:{zone:SiteZone;disabled:boolean;onChange:(properties:SiteZoneProperties)=>void;onClose:()=>void;onDelete:()=>void}){
  return <aside aria-label="Ground surface settings" className="absolute right-4 top-28 z-40 w-72 rounded-xl border-2 border-slate-900 bg-[#fff9ec] p-3 shadow-xl">
    <div className="flex items-center justify-between"><h2 className="font-bold">Ground surface</h2><button className="min-h-11 min-w-11" aria-label="Close ground surface" onClick={onClose}>×</button></div>
    <p className="mb-3 text-xs text-slate-600">Drag the surface to move it. Drag a white corner to change its shape. Buildings and raised objects stay above it.</p>
    <label className="text-sm font-semibold">Surface finish<select aria-label="Surface finish" disabled={disabled} className="my-2 min-h-11 w-full rounded border border-slate-400 bg-white px-2" value={groundSurfaceFor(zone)?.id??'grass'} onChange={e=>onChange({...zone.properties,ground_surface_material:e.target.value})}>
      {GROUND_SURFACES.map(s=><option key={s.id} value={s.id}>{s.label}</option>)}
    </select></label>
    <button className="min-h-11 w-full rounded border border-slate-700 bg-white" disabled={disabled} onClick={onDelete}>Delete surface</button>
  </aside>;
}
