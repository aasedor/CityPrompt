import type { SiteZone } from '@/types';
import bounds from '@/data/nativeStreetModuleBounds.json';
import { extractZoneCenterline } from '@/utils/roadGeometry';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '../mapEngine/geoUtils';
import { BRIDGE_VARIANT } from './specialistStreetProgram';
import type { NativeStreetPose } from './nativeStreetPilot';

const bridges = (zones: SiteZone[]) => zones.filter(z => z.zone_type === 'road'
  && z.properties?.road_selected_variant_id === BRIDGE_VARIANT && !z.properties?.validation_fixed_fixture);

/** Neighbour edits change overhead reservations even when this road is unchanged. */
export const bridgeClearanceKey = (zones: SiteZone[]) => JSON.stringify(bridges(zones)
  .map(z => [z.id, extractZoneCenterline(z)]).sort((a,b) => String(a[0]).localeCompare(String(b[0]))));

/** Whole tall modules yield to the rigid deck/support envelope. This is a
 * spatial clearance rule, never a performance-based reduction in furniture. */
export function clearBridgeOverhead(poses: NativeStreetPose[], origin: {lng:number;lat:number}, zones:SiteZone[], ownerId:string):NativeStreetPose[] {
  const reservations = bridges(zones).filter(z => z.id !== ownerId).flatMap(zone => {
    const line=extractZoneCenterline(zone),first=line[0],last=line[line.length-1];
    if(!first || !last)return [];
    const sx=metersPerDegLon(origin.lat),a={x:(first[0]-origin.lng)*sx,y:(first[1]-origin.lat)*METERS_PER_DEG_LAT};
    const dx=(last[0]-first[0])*sx,dy=(last[1]-first[1])*METERS_PER_DEG_LAT,length=Math.hypot(dx,dy);
    return length>100?[{a,dx:dx/length,dy:dy/length,start:(length-100)/2,end:(length+100)/2}]:[];
  });
  if(!reservations.length)return poses;
  const blocked=poses.filter(pose => {
    // Complete structures are never disposable overhead furniture. Their
    // compatibility is decided before saving by specialist/station fit checks.
    if (['bridge_structure', 'canal_ground', 'canal_crossing', 'canal_furnishings', 'station_program'].includes(pose.kind)) return false;
    const box=bounds[pose.sha256 as keyof typeof bounds];
    if(!box)throw new Error('The street component has no verified occupied bounds.');
    // Original tie girders reach 3.17 m; keep 7 cm tolerance to their underside.
    if(pose.z+pose.surfaceLiftM+box.height[1]*pose.scale<=3.10)return false;
    const c=Math.cos(pose.yaw),s=Math.sin(pose.yaw);
    const corners=[box.plan[0][0],box.plan[1][0]].flatMap(x=>[box.plan[0][1],box.plan[1][1]].map(y=>({
      x:pose.x+(x*c-y*s)*pose.scale,y:pose.y+(x*s+y*c)*pose.scale,
    })));
    return reservations.some(r=>{
      const projected=corners.map(p=>({x:(p.x-r.a.x)*r.dy-(p.y-r.a.y)*r.dx,y:(p.x-r.a.x)*r.dx+(p.y-r.a.y)*r.dy}));
      return Math.min(...projected.map(p=>p.x))<12.1 && Math.max(...projected.map(p=>p.x))>-12.1
        && Math.min(...projected.map(p=>p.y))<r.end && Math.max(...projected.map(p=>p.y))>r.start;
    });
  });
  // A tree and its separately modelled well are a single clearance group.
  return poses.filter(p=>!blocked.some(b=>Math.hypot(p.x-b.x,p.y-b.y)<.001));
}
