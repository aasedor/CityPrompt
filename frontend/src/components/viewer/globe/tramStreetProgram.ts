import type { StreetRouteStation } from './nativeStreetPilot';
import type { BrtStop } from './brtStreetProgram';

export const TRAM_VARIANT='student_grass_tram_avenue_v1';
export const TRAM_STOP_MODULE='showcase_tram_stop';

/** Complete fixed-scale platform/ramps, with clearance at both route ends. */
export function tramRouteProblem(route:StreetRouteStation[],stops:BrtStop[]=[]):string|null {
  if(route.length<2 || route.some(p=>!Number.isFinite(p.x)||!Number.isFinite(p.y)))return 'Draw the tram route with two endpoints.';
  const a=route[0],b=route[route.length-1],dx=b.x-a.x,dy=b.y-a.y,length=Math.hypot(dx,dy);
  if(length<47.99 || length>480.01)return 'Garden Tram Avenue needs a straight route 48–480 m long.';
  let previous=-1;
  for(const p of route){
    const along=((p.x-a.x)*dx+(p.y-a.y)*dy)/length;
    if(Math.abs((p.x-a.x)*dy-(p.y-a.y)*dx)/length>.05 || along<previous-.01)return 'Keep this tram avenue straight so tracks, wires and platforms remain aligned.';
    previous=along;
  }
  if(!Array.isArray(stops)||stops.length>8)return 'Choose at most eight tram stops.';
  const ids=new Set<string>(),positions:number[]=[];
  for(const stop of stops){
    if(!stop || Object.keys(stop).sort().join(',')!=='id,stationM' || typeof stop.id!=='string' || !/^[a-zA-Z0-9_-]{1,80}$/.test(stop.id) || ids.has(stop.id) || !Number.isFinite(stop.stationM))return 'A tram stop needs a unique identity and valid position.';
    if(stop.stationM<15 || stop.stationM>length-15+.001)return 'Leave 15 m at each end for the complete tram platform and ramps.';
    if(positions.some(p=>Math.abs(p-stop.stationM)<32))return 'Place tram stops at least 32 m apart.';
    ids.add(stop.id);positions.push(stop.stationM);
  }
  return null;
}

interface Fixture {kind:string;x:number;y:number;z?:number;yaw?:number;scale?:number}
export function tramFixtures(placements:Fixture[],fixtureLength:number,total:number,stops:BrtStop[]):Required<Fixture>[] {
  if(tramRouteProblem([{x:0,y:0},{x:0,y:total}],stops))return [];
  const templates=placements.filter(p=>p.kind!==TRAM_STOP_MODULE);
  const centers=total<=fixtureLength?[total/2]:Array.from({length:Math.ceil(total/fixtureLength)},(_,i)=>fixtureLength*(i+.5));
  const fixtures=centers.flatMap(center=>templates.map(p=>({...p,y:p.y+center-total/2,z:p.z??0,yaw:p.yaw??0,scale:p.scale??1})));
  for(const stop of stops)for(const side of [-1,1])fixtures.push({kind:TRAM_STOP_MODULE,x:side*5.2,y:stop.stationM-total/2,z:0,yaw:side>0?0:Math.PI,scale:1});
  return fixtures;
}
