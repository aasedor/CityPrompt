import type { SiteZone } from '@/types';
import { getActiveSiteBoundary } from '@/utils/siteBoundary';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '../mapEngine/geoUtils';
import { resolvePreparedSiteTerrainForZone } from './sitePreparationSurface';
import { terraceOffset } from './terraceDefinition';
import { corridorInside, corridorOverlaps, pointInside } from './parkAccessConnections';
import { isNeighborhoodParkPilot, neighborhoodParkLayoutForZone } from './neighborhoodParkLayout';
import { stripFootprint } from './terraceGeometry';

type Point = [number,number];
export interface TerracePathDefinition {
  version: 1; targetId: string; sourceEdge: number; targetEdge: number;
  sourcePosition: number; targetPosition: number; widthM: number; approachM: number;
}
export interface TerracePathResult {
  ownerId: string; targetId: string; status: 'connected'|'unresolved'; reason: string;
  points: Array<[number,number,number]>; widthM: number; lengthM: number; gradePercent: number;
  rampFootprint: number[][];
}
export function readTerracePath(zone: SiteZone): TerracePathDefinition | null {
  const p=zone.properties?.terrace_connection as TerracePathDefinition|undefined;
  return p?.version===1&&typeof p.targetId==='string'&&[p.sourceEdge,p.targetEdge].every(v=>Number.isInteger(v)&&v>=0&&v<256)
    &&[p.sourcePosition,p.targetPosition].every(v=>Number.isFinite(v)&&v>=0&&v<=1)
    &&Number.isFinite(p.widthM)&&p.widthM>=1.2&&p.widthM<=4&&Number.isFinite(p.approachM)&&p.approachM>=0&&p.approachM<=10 ? p:null;
}
export function terracePort(zone:SiteZone,edge:number,position:number):Point|null {
  if(edge>=zone.coordinates.length)return null;
  const a=zone.coordinates[edge],b=zone.coordinates[(edge+1)%zone.coordinates.length];
  return [a[0]+(b[0]-a[0])*position,a[1]+(b[1]-a[1])*position];
}

/** Bounded search for a clear concept route, only on an explicit student action. */
export function suggestTerracePath(zones:SiteZone[],ownerId:string,targetId:string,current:TerracePathDefinition):TerracePathDefinition|null {
  const owner=zones.find(z=>z.id===ownerId),target=zones.find(z=>z.id===targetId);
  if(!owner||!target||owner.coordinates.length>8||target.coordinates.length>8)return null;
  let best:{definition:TerracePathDefinition;length:number}|null=null;
  for(let sourceEdge=0;sourceEdge<owner.coordinates.length;sourceEdge++)for(let targetEdge=0;targetEdge<target.coordinates.length;targetEdge++) {
    for(const sourcePosition of [.2,.5,.8])for(const targetPosition of [.2,.4,.5,.6,.8]) {
      const definition={...current,targetId,sourceEdge,targetEdge,sourcePosition,targetPosition};
      const path=buildTerraceScene(zones.map(z=>z.id===ownerId?{...z,properties:{...z.properties,terrace_connection:definition}}:z),0).paths.find(p=>p.ownerId===ownerId);
      if(path?.status==='connected'&&(!best||path.lengthM<best.length))best={definition,length:path.lengthM};
    }
  }
  return best?.definition??null;
}

export function buildTerraceScene(zones:SiteZone[],fallback:number) {
  const boundary=getActiveSiteBoundary(zones), base=resolvePreparedSiteTerrainForZone(boundary??undefined,zones,fallback);
  const terraces=base===null?[]:zones.filter(z=>terraceOffset(z)!==null&&resolvePreparedSiteTerrainForZone(z,zones,fallback)!==null);
  const paths:TerracePathResult[]=[];
  for(const owner of zones.filter(z=>z.properties?.terrace_connection)) {
    const c=readTerracePath(owner),target=c?zones.find(z=>z.id===c.targetId):undefined;
    const result:TerracePathResult={ownerId:owner.id,targetId:c?.targetId??'',status:'unresolved',reason:'Choose two different objects inside a prepared site.',points:[],widthM:c?.widthM??2,lengthM:0,gradePercent:0,rampFootprint:[]};
    paths.push(result);
    if(!boundary||base===null||!c||!target||target.id===owner.id||zones.length>256
      ||![owner,target].every(z=>['building','residential','green_space'].includes(z.zone_type)))continue;
    const sourceHeight=resolvePreparedSiteTerrainForZone(owner,zones,fallback),targetHeight=resolvePreparedSiteTerrainForZone(target,zones,fallback);
    const a=terracePort(owner,c.sourceEdge,c.sourcePosition),b=terracePort(target,c.targetEdge,c.targetPosition);
    if(sourceHeight===null||targetHeight===null||!a||!b)continue;
    const east=metersPerDegLon(a[1]);
    const local=(p:number[]):Point=>[(p[0]-a[0])*east,(p[1]-a[1])*METERS_PER_DEG_LAT];
    const world=(p:Point):Point=>[a[0]+p[0]/east,a[1]+p[1]/METERS_PER_DEG_LAT];
    const end=local(b),gap=Math.hypot(...end);
    result.reason='Choose facing edges with a clear gap of at least 1 m; the path must stay inside the site.';
    if(gap<1||gap>100||!corridorInside([0,0],end,boundary.coordinates.map(local),c.widthM/2))continue;
    const startInset:Point=[end[0]/gap*.2,end[1]/gap*.2],endInset:Point=[end[0]*(1-.2/gap),end[1]*(1-.2/gap)];
    if(zones.some(z=>z.id!==boundary.id&&['building','residential','green_space','road','water','parking'].includes(z.zone_type)
      &&corridorOverlaps(startInset,endInset,z.coordinates.map(local),c.widthM/2))) {result.reason='The route crosses a plot or street. Choose facing edges or move the objects; a crossing must be deliberate.';continue;}
    const approach=(zone:SiteZone,port:Point,edge:number):Point|null=>{
      const p=local(port);
      const ring=zone.coordinates.map(local),v=ring[edge],w=ring[(edge+1)%ring.length];
      const edgeLength=Math.hypot(w[0]-v[0],w[1]-v[1]);
      if(edgeLength<.01)return null;
      let n:Point=[-(w[1]-v[1])/edgeLength,(w[0]-v[0])/edgeLength];
      if(!pointInside([p[0]+n[0]*.1,p[1]+n[1]*.1],ring))n=[-n[0],-n[1]];
      if(isNeighborhoodParkPilot(zone)) {
        const layout=neighborhoodParkLayoutForZone(zone,{lng:a[0],lat:a[1]});
        const candidates=layout.loop.flatMap((v,i)=>{
          const q=layout.loop[(i+1)%layout.loop.length],dx=q.x-v.x,dy=q.y-v.y,den=n[0]*dy-n[1]*dx;
          if(Math.abs(den)<1e-8)return [];
          const t=((v.x-p[0])*dy-(v.y-p[1])*dx)/den,u=((v.x-p[0])*n[1]-(v.y-p[1])*n[0])/den;
          return t>=0&&u>=0&&u<=1?[[p[0]+n[0]*t,p[1]+n[1]*t] as Point]:[];
        }).filter(q=>corridorInside(p,q,zone.coordinates.map(local),c.widthM/2)
          &&!layout.modules.some(m=>corridorOverlaps(p,q,m.envelope.map(v=>[v.x,v.y]),c.widthM/2+.2)));
        candidates.sort((u,v)=>Math.hypot(u[0]-p[0],u[1]-p[1])-Math.hypot(v[0]-p[0],v[1]-p[1]));
        return candidates[0]?world(candidates[0]):null;
      }
      if(zone.zone_type==='green_space')return null;
      const q:Point=[p[0]+n[0]*c.approachM,p[1]+n[1]*c.approachM];
      return corridorInside(p,q,ring,c.widthM/2)?world(q):null;
    };
    const from=approach(owner,a,c.sourceEdge),to=approach(target,b,c.targetEdge);
    if(!from||!to){result.reason='No clear approach reaches the park loop or plot interior. Try a different entrance edge. The park pilot supports neighbourhood parks.';continue;}
    result.points=[[...from,sourceHeight],[...a,sourceHeight],[...b,targetHeight],[...to,targetHeight]];
    result.lengthM=result.points.slice(1).reduce((sum,p,i)=>{const q=result.points[i];return sum+Math.hypot((p[0]-q[0])*east,(p[1]-q[1])*METERS_PER_DEG_LAT);},0);
    result.gradePercent=Math.abs(targetHeight-sourceHeight)/gap*100;
    // Extend openings into each plot so the retaining face is removed at both ends.
    result.rampFootprint=stripFootprint([-end[0]/gap*.15,-end[1]/gap*.15],[end[0]*(1+.15/gap),end[1]*(1+.15/gap)],c.widthM+.02).map(world);
    result.status='connected';
    result.reason=`${result.lengthM.toFixed(1)} m path; ${result.gradePercent.toFixed(1)}% connecting grade. ${result.gradePercent>5?'Steep route: review a longer alignment, landings or another terrace level.':'Review the entrance, landings and edge protection.'} This is not an accessibility compliance check.`;
  }
  return {boundary,base,terraces,paths};
}
