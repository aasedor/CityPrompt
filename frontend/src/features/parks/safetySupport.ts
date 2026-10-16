import type { BufferGeometry } from 'three';
import { useSyncExternalStore } from 'react';
import clipping from 'polygon-clipping';
import { metersPerDegLon, METERS_PER_DEG_LAT } from '@/components/viewer/mapEngine/geoUtils';
export interface SafetySurface { id:string; lng:number;lat:number;height:number;geometries:BufferGeometry[] }
type Point=[number,number,number];
interface Triangle { points:Point[]; minX:number;maxX:number;minY:number;maxY:number }
const surfaces=new Map<string,Omit<SafetySurface,'geometries'>&{triangles:Triangle[]}>();
const subscribers=new Set<()=>void>();let version=0;
const notify=()=>{version++;subscribers.forEach(fn=>fn());};
export function useSafetySurfaceVersion(){return useSyncExternalStore(fn=>{subscribers.add(fn);return()=>subscribers.delete(fn);},()=>version,()=>0);}
/** Snapshot the actual rendered surface at edits/drape completion, never per frame. */
export function registerSafetySurface(surface:SafetySurface) {
  const triangles:Triangle[]=[];
  for(const geometry of surface.geometries){
    const positions=geometry.attributes.position,index=geometry.index;
    for(let i=0;i<(index?.count??positions.count);i+=3){
      const points:Point[]=[0,1,2].map(k=>{const n=index?index.getX(i+k):i+k;return [positions.getX(n),positions.getY(n),positions.getZ(n)];});
      const [a,b,c]=points;
      if(points.some(p=>!p.every(Number.isFinite))||Math.abs((b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]))<1e-10)continue;
      triangles.push({points,minX:Math.min(...points.map(p=>p[0])),maxX:Math.max(...points.map(p=>p[0])),minY:Math.min(...points.map(p=>p[1])),maxY:Math.max(...points.map(p=>p[1]))});
    }
  }
  const snapshot={id:surface.id,lng:surface.lng,lat:surface.lat,height:surface.height,triangles};
  surfaces.set(surface.id,snapshot);notify();
  return()=>{if(surfaces.get(surface.id)===snapshot){surfaces.delete(surface.id);notify();}};
}
/** Exact polygon coverage and linear triangle heights, including narrow holes.
 * Bounds are source X/Z around the documented pivot, not recentered paint bounds.
 */
export function safetySurfaceSupport(pose:{lng:number;lat:number;angle:number},bounds:readonly number[],zoneIds:readonly string[]):
  {ok:true;height:number;hostId:string}|{ok:false;message:string} {
  const fail={ok:false as const,message:'Place the complete fixed-size item on a loaded, level road surface. Slopes and gaps are not supported.'};
  if(bounds.length!==4||![pose.lng,pose.lat,pose.angle,...bounds].every(Number.isFinite)||bounds[2]<=bounds[0]||bounds[3]<=bounds[1])return fail;
  for(const id of zoneIds){const surface=surfaces.get(id);if(!surface||!Number.isFinite(surface.height))continue;
    const x=(pose.lng-surface.lng)*metersPerDegLon(surface.lat),y=(pose.lat-surface.lat)*METERS_PER_DEG_LAT;
    const c=Math.cos(pose.angle*Math.PI/180),s=Math.sin(pose.angle*Math.PI/180);
    const footprint:[number,number][]=[[bounds[0],bounds[1]],[bounds[2],bounds[1]],[bounds[2],bounds[3]],[bounds[0],bounds[3]]]
      .map(([px,pz])=>[x+c*px+s*pz,y+s*px-c*pz]);
    const xs=footprint.map(p=>p[0]),ys=footprint.map(p=>p[1]);
    const minX=Math.min(...xs),maxX=Math.max(...xs),minY=Math.min(...ys),maxY=Math.max(...ys);
    const pieces:clipping.MultiPolygon[]=[];let low=Infinity,high=-Infinity;
    for(const t of surface.triangles){if(t.minX>maxX||t.maxX<minX||t.minY>maxY||t.maxY<minY)continue;
      const piece=clipping.intersection([footprint],[t.points.map(p=>[p[0],p[1]] as [number,number])]);if(!piece.length)continue;
      pieces.push(piece);const [a,b,d]=t.points;
      const denominator=(b[0]-a[0])*(d[1]-a[1])-(d[0]-a[0])*(b[1]-a[1]);
      for(const polygon of piece)for(const ring of polygon)for(const p of ring){
        const u=((p[0]-a[0])*(d[1]-a[1])-(d[0]-a[0])*(p[1]-a[1]))/denominator;
        const v=((b[0]-a[0])*(p[1]-a[1])-(p[0]-a[0])*(b[1]-a[1]))/denominator;
        const height=a[2]+u*(b[2]-a[2])+v*(d[2]-a[2]);low=Math.min(low,height);high=Math.max(high,height);
      }
    }
    if(!pieces.length||high-low>.001)continue;
    const missing=clipping.difference([footprint],...pieces);
    const area=missing.reduce((sum,p)=>sum+p.reduce((value,ring)=>value+Math.abs(ring.reduce((a,v,i)=>{const q=ring[(i+1)%ring.length];return a+v[0]*q[1]-q[0]*v[1];},0))/2,0),0);
    if(area>1e-7)continue;
    return {ok:true,height:surface.height+high,hostId:id};
  }
  return fail;
}
