import type { SiteZone } from '@/types';
import { bufferLineToPolygon, collapseStraightStreetStations, extractZoneCenterline, parsePersistedCenterline } from '@/utils/roadGeometry';
import { metersPerDegLon, METERS_PER_DEG_LAT } from '@/components/viewer/mapEngine/geoUtils';
import { detectConnectedStreetIntersections } from '@/components/viewer/globe/streetGraphIntersections';
import { resolveStreetJunctionLayout } from '@/components/viewer/globe/streetJunctionGeometry';
import { isSpecialistStreet } from '@/components/viewer/globe/specialistStreetProgram';
import { isFixedSectionStreet, streetSectionWidth } from './streetPlacement';
import { streetConnectionProblem } from './streetConnectionProblem';
import { snapStreetEnds } from './streetSnapping';

type Point=[number,number];
/** Recover small drawing inaccuracies by moving the candidate geometry, never
 * by relaxing the junction renderer. Corrections retain the section width;
 * bends, specialist structures and reference streets keep their own editors. */
export function snapStreetJunctionPlacement(zone: SiteZone, zones: SiteZone[], isValid: (candidate: SiteZone)=>boolean): SiteZone {
  if (!isFixedSectionStreet(zone) || isSpecialistStreet(zone.properties?.road_selected_variant_id)
    || !streetConnectionProblem(zone,zones)) return zone;
  const controls=parsePersistedCenterline(zone.properties?.plan_route_controls);
  const route=collapseStraightStreetStations(extractZoneCenterline(zone));
  if (route.length!==2 || (controls && controls.length!==2)) return zone;
  const origin=route[0],sx=metersPerDegLon(origin[1]);
  const local=(p:number[]):Point=>[(p[0]-origin[0])*sx,(p[1]-origin[1])*METERS_PER_DEG_LAT];
  const world=([x,y]:Point)=>[origin[0]+x/sx,origin[1]+y/METERS_PER_DEG_LAT];
  const own=route.map(local),angle=Math.atan2(own[1][1],own[1][0]);
  const bounds=(ring:Point[])=>({minX:Math.min(...ring.map(p=>p[0])),maxX:Math.max(...ring.map(p=>p[0])),
    minY:Math.min(...ring.map(p=>p[1])),maxY:Math.max(...ring.map(p=>p[1]))});
  const ownBounds=bounds(zone.coordinates.map(local));
  const hosts=zones.filter(other=>other.id!==zone.id && isFixedSectionStreet(other)
    && !other.properties?._imported_from && !isSpecialistStreet(other.properties?.road_selected_variant_id))
    .filter(other=>{const box=bounds(other.coordinates.map(local));return box.minX<=ownBounds.maxX+3 && box.maxX>=ownBounds.minX-3
      && box.minY<=ownBounds.maxY+3 && box.maxY>=ownBounds.minY-3;});
  const proposals:{line:Point[];distance:number;host:SiteZone}[]=[];
  const seen=new Set<string>();
  const add=(line:Point[],host:SiteZone)=>{
    const distance=Math.max(...line.map((p,i)=>Math.hypot(p[0]-own[i][0],p[1]-own[i][1])));
    const key=`${host.id}:${line.flat().map(value=>value.toFixed(3)).join(',')}`;
    if(distance>.001 && distance<=3 && !seen.has(key)){seen.add(key);proposals.push({line,distance,host});}
  };
  const rotate=(delta:number,pivot:Point):Point[]=>own.map(([x,y])=>[
    pivot[0]+(x-pivot[0])*Math.cos(delta)-(y-pivot[1])*Math.sin(delta),
    pivot[1]+(x-pivot[0])*Math.sin(delta)+(y-pivot[1])*Math.cos(delta),
  ]);
  const normalAngle=(a:number)=>Math.atan2(Math.sin(a),Math.cos(a));
  for(const host of hosts) {
    const target=collapseStraightStreetStations(extractZoneCenterline(host)).map(local);
    add(snapStreetEnds(route,[host],zone.id,streetSectionWidth(zone)).map(local),host);
    for(let i=1;i<target.length;i++) {
      const a=target[i-1],b=target[i],dx=b[0]-a[0],dy=b[1]-a[1],length=Math.hypot(dx,dy);
      if(length<1)continue;
      const hostAngle=Math.atan2(dy,dx),center:Point=[(own[0][0]+own[1][0])/2,(own[0][1]+own[1][1])/2];
      for(const degrees of [0,30,45,60,90,120,135,150,180,210,225,240,270,300,315,330]) {
        const delta=normalAngle(hostAngle+degrees*Math.PI/180-angle);
        if(Math.abs(delta)>5*Math.PI/180)continue;
        add(rotate(delta,center),host);
      }
      // Short arms close to a host end can slide inward. Try both directions;
      // only a complete, still-connected junction can authorize the result.
      for(const offset of [-3,-2.5,-2,-1.5,-1,-.5,.5,1,1.5,2,2.5,3])
        add(own.map(([x,y])=>[x+offset*dx/length,y+offset*dy/length]),host);
      for(const ownIndex of [0,1])for(const targetIndex of [0,target.length-1]) {
        const p=own[ownIndex],q=target[targetIndex];
        if(Math.hypot(p[0]-q[0],p[1]-q[1])>3)continue;
        const nearest=normalAngle(hostAngle-angle),delta=Math.abs(nearest)>Math.PI/2?normalAngle(nearest+Math.PI):nearest;
        if(Math.abs(delta)>5*Math.PI/180)continue;
        add(rotate(delta,p).map(([x,y])=>[x+q[0]-p[0],y+q[1]-p[1]]),host);
      }
    }
  }
  for(const {line,host} of proposals.sort((a,b)=>a.distance-b.distance)) {
    const centerline=line.map(world),candidate={...zone,coordinates:bufferLineToPolygon(centerline,streetSectionWidth(zone)),
      properties:{...zone.properties,plan_centerline:centerline,...(controls?{plan_route_controls:centerline}:{})}};
    if(!isValid(candidate))continue;
    const preview={...candidate,properties:{...candidate.properties,junction_preview_candidate:true}};
    const network=[...zones.filter(other=>other.id!==zone.id),preview];
    const completeNode=detectConnectedStreetIntersections(network,true).some(node=>node.zoneIds.includes(zone.id)
      && node.zoneIds.includes(host.id) && resolveStreetJunctionLayout(node,network));
    const target=collapseStraightStreetStations(extractZoneCenterline(host)).map(local);
    const flush=([0,1] as const).some(index=>([0,target.length-1]).some(j=>{
      const p=line[index],q=target[j],r=line[1-index],s=target[j===0?1:target.length-2];
      if(!s || Math.hypot(p[0]-q[0],p[1]-q[1])>.02)return false;
      const ax=r[0]-p[0],ay=r[1]-p[1],bx=s[0]-q[0],by=s[1]-q[1];
      return (ax*bx+ay*by)/Math.hypot(ax,ay)/Math.hypot(bx,by)<-.999;
    }));
    if(completeNode||flush)return candidate;
  }
  return zone;
}
