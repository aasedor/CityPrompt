import polygonClipping from 'polygon-clipping';
import type { SiteZone } from '@/types';
import { bufferLineToPolygon } from '@/utils/roadGeometry';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '@/components/viewer/mapEngine/geoUtils';
import { resolvePilotStreetSectionProfile } from '@/components/viewer/globe/streetSectionProfiles';
import type { PublicRoadContext } from '@/features/pickPlace/publicRoadSuggestions';
import { parkingLayout } from './parkingLot';
import type { PavingSurface } from './pavingSurfaces';
import { detailAsset, type DetailPropVariant } from './detailCatalogue';
import { rectangleAt } from '@/features/pickPlace/geometry';

type Point = number[];
export interface ParkingDriveway {
  version: 1;
  source: 'manual' | 'mapped' | 'authored';
  roadPoint: Point;
  streetId?: string;
}
export interface ParkingRoad {
  id: string; label: string; source: 'mapped' | 'authored'; compatible: boolean; coordinates: Point[];
}
const WIDTH=6, MAX_LENGTH=60;
const add=(a:Point,b:Point)=>[a[0]+b[0],a[1]+b[1]];
const sub=(a:Point,b:Point)=>[a[0]-b[0],a[1]-b[1]];
const mul=(a:Point,n:number)=>[a[0]*n,a[1]*n];
const length=(a:Point)=>Math.hypot(...a);
const dot=(a:Point,b:Point)=>a[0]*b[0]+a[1]*b[1];
const frame=(origin:Point)=>({
  local:(p:Point)=>[(p[0]-origin[0])*metersPerDegLon(origin[1]),(p[1]-origin[1])*METERS_PER_DEG_LAT],
  world:(p:Point)=>[origin[0]+p[0]/metersPerDegLon(origin[1]),origin[1]+p[1]/METERS_PER_DEG_LAT],
});
const area=(ring:Point[])=>Math.abs(ring.reduce((s,p,i)=>s+p[0]*ring[(i+1)%ring.length][1]-p[1]*ring[(i+1)%ring.length][0],0))/2;
function overlaps(a:Point[],b:Point[]) {
  try {return polygonClipping.intersection([a as [number,number][]],[b as [number,number][]])
    .some(poly=>area(poly[0])>.001);} catch {return true;}
}
function closest(point:Point,a:Point,b:Point,inset=0) {
  const d=sub(b,a),size=length(d);
  if(size<inset*2+.001)return null;
  const t=Math.max(inset/size,Math.min(1-inset/size,dot(sub(point,a),d)/(size*size)));
  return add(a,mul(d,t));
}

/** Bind clicks close to a known edge; also resolves older manual recipes on load. */
export function parkingRoadTarget(point:Point,roads:readonly ParkingRoad[]):ParkingDriveway {
  const f=frame(point);
  const candidates=roads.map(road=>({road,distance:Math.min(...road.coordinates.map((p,i)=>{
    const edge=closest([0,0],f.local(p),f.local(road.coordinates[(i+1)%road.coordinates.length]));
    return edge?length(edge):Infinity;
  }))})).filter(r=>r.distance<=1).sort((a,b)=>a.distance-b.distance||a.road.id.localeCompare(b.road.id));
  const road=candidates[0]?.road;
  return road?{version:1,source:road.source,streetId:road.id,roadPoint:point}
    :{version:1,source:'manual',roadPoint:point};
}

/** Mapped edges are estimates. Curbed authored streets require a real opening. */
export function parkingRoads(zones:readonly SiteZone[],context?:PublicRoadContext):ParkingRoad[] {
  return [
    ...zones.filter(z=>z.zone_type==='road'&&!z.id.startsWith('temp-')).map(z=>{
      const section=resolvePilotStreetSectionProfile(z);
      const compatible=Boolean(section && !section.renderCurbs
        && section.bands.some(b=>b.kind==='motor')
        && section.bands.every(b=>['motor','shoulder'].includes(b.kind)));
      return {id:z.id,label:z.name||'Authored street',source:'authored' as const,compatible,coordinates:z.coordinates};
    }),
    ...(context?.roads??[]).filter(r=>r.widthM>=3&&r.widthM<=20).map(r=>({
      id:`mapped:${r.id}`,label:r.label,source:'mapped' as const,compatible:true,
      coordinates:bufferLineToPolygon(r.points,r.widthM),
    })),
  ];
}

/** Derive on edits/loading. Road endpoints stay fixed when the lot moves. */
export function parkingDriveway(surface:PavingSurface,roads:readonly ParkingRoad[],obstacles:Point[][]=[]) {
  const fail=(problem:string|null)=>({coordinates:[] as Point[],problem});
  const recipe=surface.parking?.driveway;
  if(!recipe)return fail(null);
  if(recipe.version!==1||recipe.roadPoint.length!==2||!recipe.roadPoint.every(Number.isFinite))return fail('Choose a valid road edge.');
  const f=frame(surface.coordinates[0]),outline=surface.coordinates.map(f.local);
  const layout=parkingLayout(outline,surface.parking!);
  if(layout.problem||!layout.aisles.length)return fail(layout.problem||'No clear side aisle is available.');
  let target=f.local(recipe.roadPoint);
  const resolved=recipe.source==='manual'&&!recipe.streetId?parkingRoadTarget(recipe.roadPoint,roads):recipe;
  const road=resolved.streetId?roads.find(r=>r.id===resolved.streetId):undefined;
  if(recipe.source!=='manual'&&!road)return fail('The connected street is missing or not loaded. Choose a road again.');
  if(road&&!road.compatible)return fail('This street needs a supported curb opening. Choose a flush access road or another target.');
  if(road){
    const ring=road.coordinates.map(f.local);
    const candidates=ring.map((p,i)=>closest(target,p,ring[(i+1)%ring.length],WIDTH/2+.1)).filter((p):p is Point=>!!p);
    candidates.sort((a,b)=>length(sub(a,target))-length(sub(b,target)));
    if(!candidates.length)return fail('This road edge is too short for a 6 m entrance.');
    target=candidates[0];
    if(length(sub(target,f.local(recipe.roadPoint)))>10)return fail('The connected road moved. Choose the road edge again.');
  }
  const spine=layout.aisles[0],center=mul(add(spine[0],spine[2]),.5);
  const blocked=[...obstacles.map(r=>r.map(f.local)),...layout.spaces.map(s=>s.corners),
    ...roads.filter(r=>r.id!==road?.id).map(r=>r.coordinates.map(f.local))];
  let obstruction=false;
  const candidates:Point[][]=[];
  // Exclude the fourth, bay-facing edge of the reserved circulation spine.
  for(const [i,j] of [[0,1],[2,3],[3,0]]){
    const edge=closest(target,spine[i],spine[j],Math.min(WIDTH/2,length(sub(spine[j],spine[i]))/2-.001));
    if(!edge)continue;
    const outward=sub(mul(add(spine[i],spine[j]),.5),center);
    const side=mul(outward,1/(length(outward)||1));
    const direction=sub(target,edge),distance=length(direction);
    if(distance<.2||distance>MAX_LENGTH||dot(direction,side)/distance<.5)continue;
    const unit=mul(direction,1/distance),normal=mul([-unit[1],unit[0]],WIDTH/2);
    const start=add(edge,mul(unit,-1)),end=add(target,mul(unit,.1));
    const quad=[add(start,normal),add(end,normal),sub(end,normal),sub(start,normal)];
    if(blocked.some(r=>overlaps(quad,r))){obstruction=true;continue;}
    if(road){
      const roadRing=road.coordinates.map(f.local);
      const endStrip=[add(add(target,mul(unit,-.03)),normal),add(end,normal),sub(end,normal),sub(add(target,mul(unit,-.03)),normal)];
      const intersection=polygonClipping.intersection([endStrip as [number,number][]],[roadRing as [number,number][]]);
      if(intersection.reduce((n,p)=>n+area(p[0]),0)<WIDTH*.07)continue;
    }
    candidates.push(quad);
  }
  candidates.sort((a,b)=>length(sub(a[1],a[0]))-length(sub(b[1],b[0])));
  return candidates.length?{coordinates:candidates[0].map(f.world),problem:null}
    :fail(obstruction?'The driveway is blocked by a bay, building, another lot or detail. Move the lot or choose another road edge.'
      :'No clear 6 m entrance reaches that road edge within 60 m. Move or rotate the lot, or choose another road edge.');
}

export function nearestParkingRoad(surface:PavingSurface,roads:readonly ParkingRoad[],obstacles:Point[][]=[]):ParkingDriveway|null {
  if(!surface.parking)return null;
  const f=frame(surface.coordinates[0]);
  const layout=parkingLayout(surface.coordinates.map(f.local),surface.parking);
  if(!layout.aisles.length)return null;
  const center=mul(add(layout.aisles[0][0],layout.aisles[0][2]),.5);
  const candidates:Array<{recipe:ParkingDriveway;distance:number}>=[];
  for(const road of roads.filter(r=>r.compatible)){
    const ring=road.coordinates.map(f.local);
    ring.forEach((a,i)=>{
      const p=closest(center,a,ring[(i+1)%ring.length],WIDTH/2+.1);
      if(!p)return;
      const recipe:ParkingDriveway={version:1,source:road.source,streetId:road.id,roadPoint:f.world(p)};
      if(!parkingDriveway({...surface,parking:{...surface.parking!,driveway:recipe}},roads,obstacles).problem)
        candidates.push({recipe,distance:length(sub(center,p))});
    });
  }
  candidates.sort((a,b)=>a.distance-b.distance||a.recipe.streetId!.localeCompare(b.recipe.streetId!));
  return candidates[0]?.recipe??null;
}

/** Shared obstacle footprints for plan edits and the 3D surface layer. */
export function parkingDetailFootprints(benches:readonly {lng:number;lat:number;angle:number}[]=[],
  trees:readonly {lng:number;lat:number;angle:number}[]=[],
  props:readonly {lng:number;lat:number;angle:number;variant:DetailPropVariant}[]=[]):Point[][] {
  return [
    ...benches.map(b=>rectangleAt([b.lng,b.lat],2.4,1.1,b.angle)),
    ...trees.map(b=>rectangleAt([b.lng,b.lat],1.4,1.4,b.angle)),
    ...props.map(b=>{const d=detailAsset(b.variant).dimensions;return rectangleAt([b.lng,b.lat],d[0]+.5,d[1]+.5,b.angle);}),
  ];
}
