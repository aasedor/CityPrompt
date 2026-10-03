import type {SiteZone} from '@/types';
import {extractZoneCenterline,effectiveRoadWidth} from '@/utils/roadGeometry';
import {BRT_VARIANT,BRT_STOP_BOUNDS} from '@/components/viewer/globe/brtStreetProgram';

function crossesBox(a:number[],b:number[],low:number[],high:number[]) {
  let enter=0,leave=1;
  for(let axis=0;axis<2;axis++){
    const delta=b[axis]-a[axis];
    if(Math.abs(delta)<1e-8){if(a[axis]<low[axis] || a[axis]>high[axis])return false;continue;}
    const u=(low[axis]-a[axis])/delta,v=(high[axis]-a[axis])/delta;
    enter=Math.max(enter,Math.min(u,v));leave=Math.min(leave,Math.max(u,v));if(enter>leave)return false;
  }
  return true;
}

/** Check all BRT reservations, including when a different street moves into one.
 * The first release joins outside stations; it never paints a generic junction
 * across a rigid boarding platform or its authored crossing. */
export function brtConnectionProblem(candidate:Pick<SiteZone,'coordinates'|'properties'> & Partial<SiteZone>,zones:SiteZone[]):string|null {
  const next=[...zones.filter(z=>z.id!==candidate.id),{...candidate,id:candidate.id??'draft-brt-check',zone_type:candidate.zone_type??'road'} as SiteZone];
  if(!next.some(z=>z.properties?.road_selected_variant_id===BRT_VARIANT && z.properties?.road_native_stops?.length))return null;
  for(const zone of next){
    if(zone.properties?.road_selected_variant_id!==BRT_VARIANT || zone.properties?.validation_fixed_fixture)continue;
    const line=extractZoneCenterline(zone);if(line.length<2)continue;
    const a=line[0],b=line[line.length-1],sx=111320*Math.cos(a[1]*Math.PI/180);
    const dx=(b[0]-a[0])*sx,dy=(b[1]-a[1])*111320,length=Math.hypot(dx,dy);if(length<1)continue;
    for(const other of next.filter(n=>n.zone_type==='road' && n.id!==zone.id)){
      // Draft roads have no compiled graph node yet. Inspect their full route
      // corridor now, before a save/compile could obscure the rigid station.
      const otherLine=extractZoneCenterline(other).map(p=>{
        const x=(p[0]-a[0])*sx,y=(p[1]-a[1])*111320;
        return [(x*dy-y*dx)/length,(x*dx+y*dy)/length];
      });
      const radius=Math.max(20,effectiveRoadWidth(other.properties)/2)+4;
      for(const stop of zone.properties?.road_native_stops??[]){
        const low=stop.stationM-BRT_STOP_BOUNDS.beforeM,high=stop.stationM+BRT_STOP_BOUNDS.afterM;
        if(otherLine.slice(1).some((point,index)=>crossesBox(otherLine[index],point,[-20-radius,low-radius],[20+radius,high+radius])))
          return 'Move the junction or BRT stop farther apart. The full platform, ramps and crossing need their own clear space.';
      }
    }
  }
  return null;
}
