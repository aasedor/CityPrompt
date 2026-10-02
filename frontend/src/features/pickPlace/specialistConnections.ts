import type {SiteZone} from '@/types';
import {extractZoneCenterline,effectiveRoadWidth} from '@/utils/roadGeometry';
import {CANAL_VARIANT,BRIDGE_VARIANT,isSpecialistStreet} from '@/components/viewer/globe/specialistStreetProgram';
import { isElevatedRail } from '@/components/viewer/globe/elevatedRailProgram';

function enters(a:number[],b:number[],left:number,right:number,lo:number,hi:number){
  let first=0,last=1;
  for(const [i,min,max] of [[0,left,right],[1,lo,hi]]){
    const d=b[i]-a[i];if(Math.abs(d)<1e-8){if(a[i]<=min||a[i]>=max)return false;continue;}
    const u=(min-a[i])/d,v=(max-a[i])/d;first=Math.max(first,Math.min(u,v));last=Math.min(last,Math.max(u,v));
    if(first>=last)return false;
  }
  return true;
}

/** A canal's centre is water; a bridge's centre is elevated. Neither is a
 * generic road node. Validate draft geometry as well as compiled neighbours. */
export function specialistConnectionProblem(candidate:Pick<SiteZone,'coordinates'|'properties'> & Partial<SiteZone>,zones:SiteZone[]):string|null {
  const next=[...zones.filter(z=>z.id!==candidate.id),{...candidate,id:candidate.id??'draft',zone_type:candidate.zone_type??'road'} as SiteZone];
  for(const zone of next){
    const variant=zone.properties?.road_selected_variant_id;
    if(!isSpecialistStreet(variant)||zone.properties?.validation_fixed_fixture)continue;
    const route=extractZoneCenterline(zone);if(route.length<2)continue;
    const a=route[0],b=route[route.length-1],sx=111320*Math.cos(a[1]*Math.PI/180),dx=(b[0]-a[0])*sx,dy=(b[1]-a[1])*111320,length=Math.hypot(dx,dy);
    if(length<1)continue;
    for(const other of next.filter(z=>z.zone_type==='road'&&z.id!==zone.id)){
      const points=extractZoneCenterline(other).map(p=>{const x=(p[0]-a[0])*sx,y=(p[1]-a[1])*111320;return [(x*dy-y*dx)/length,(x*dx+y*dy)/length];});
      const half=effectiveRoadWidth(other.properties)/2;
      if(isElevatedRail(variant)){
        if(points.slice(1).some((p,i)=>enters(points[i],p,-13-half,13+half,.1,length-.1)))
          return 'Keep other streets outside the elevated rail corridor. Its ground paths and supports need the full width; street crossings and rail junctions are not supported.';
      }else if(variant===CANAL_VARIANT){
        // Ends may touch the outer bank edge. An ordinary road cannot cut
        // through the protected crossing, basin, or lower open channel.
        // The 1.9 m outer walk is a dry connection apron. Small endpoint
        // movement may enter it, but cannot intrude into the bank travel lane.
        if(points.slice(1).some((p,i)=>enters(points[i],p,-16.1,16.1,-half,length+half)))
          return 'Connect at the canal’s outer bank edge. Use its original arch to cross the water; ordinary roads cannot cross the basin or channel.';
      }else if(variant===BRIDGE_VARIANT){
        const start=(length-100)/2,end=start+100;
        if(other.properties?.road_selected_variant_id===BRIDGE_VARIANT
          && points.slice(1).some((p,i)=>enters(points[i],p,-18-half,18+half,1,length-1)))
          return 'Keep fixed bridge structures separate. Bridge-to-bridge crossings are not supported; connect their ground-level endpoints instead.';
        // The clear opening is between the two 8 m abutments. At-grade roads
        // may pass below, but no generic intersection is created there.
        const clashes=points.slice(1).some((p,i)=>enters(points[i],p,-15-half,15+half,1,start+8+half)
          ||enters(points[i],p,-15-half,15+half,end-8-half,length-1));
        if(clashes)return 'Connect roads at a ground-level bridge endpoint, or pass beneath the clear central span. Keep approaches and abutments clear.';
      }
    }
  }
  return null;
}
