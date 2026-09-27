import * as THREE from 'three';
import type { StreetRouteStation } from './nativeStreetPilot';
import { stationNormals } from './streetMesh3D';
import { buildBrtStreetProgram, type BrtStop } from './brtStreetProgram';
import { buildSpecialistStreetProgram, CANAL_VARIANT, BRIDGE_VARIANT } from './specialistStreetProgram';

export function nativeStreetHasPreparedGround(preparedElevation: number | null, hasPreparedApproach: boolean, hasSharedGround: boolean) {
  return Number.isFinite(preparedElevation) || hasPreparedApproach || hasSharedGround;
}

export interface NativeStreetRegion { x:number;y:number;width:number;depth:number;material:string|null }
export interface NativeStreetProgram {
  schemaVersion:number;adapter:string;surfaceRegions:NativeStreetRegion[];
  details:Array<NativeStreetRegion & {z:number;height:number}>;
  /** Source-authored markings and low edging; rigid furniture stays in modules. */
  meshDetails?:Array<{material:string;positions:number[];indices:number[]}>;
  paving:string;pavingModuleM:number[];minLengthM:number;maxLengthM:number;preparedLevelOnly:boolean;
  baseLiftM:number;palette:Record<string,number[]|undefined>;
}

/** The same ordered ownership partition used by the original Blender builder. */
export function nativeStreetGroundCells(width:number,length:number,regions:NativeStreetRegion[]):NativeStreetRegion[] {
  const xs=[...new Set([-width/2,width/2,...regions.flatMap(r=>[r.x-r.width/2,r.x+r.width/2])])].sort((a,b)=>a-b);
  const ys=[...new Set([-length/2,length/2,...regions.flatMap(r=>[r.y-r.depth/2,r.y+r.depth/2])])].sort((a,b)=>a-b);
  const cells:NativeStreetRegion[]=[];
  for(let i=0;i<xs.length-1;i++)for(let j=0;j<ys.length-1;j++) {
    const x=(xs[i]+xs[i+1])/2,y=(ys[j]+ys[j+1])/2;
    let material:string|null='grass';
    for(const r of regions)if(Math.abs(x-r.x)<r.width/2 && Math.abs(y-r.y)<r.depth/2)material=r.material;
    if(material)cells.push({x,y,width:xs[i+1]-xs[i],depth:ys[j+1]-ys[j],material});
  }
  return cells;
}

export function buildNativeStreetProgram(program:NativeStreetProgram,width:number,fixtureLength:number,route:StreetRouteStation[],stops:BrtStop[]=[]) {
  if(program.adapter==='brt-v004-v1')return buildBrtStreetProgram(route,stops,program.baseLiftM);
  if(program.adapter==='canal-v005-v1')return buildSpecialistStreetProgram(CANAL_VARIANT,route);
  if(program.adapter==='bridge-v003-v1')return buildSpecialistStreetProgram(BRIDGE_VARIANT,route);
  const segments=route.slice(1).map((point,i)=>({from:route[i],to:point,length:Math.hypot(point.x-route[i].x,point.y-route[i].y),start:0})).filter(s=>s.length>1e-6);
  let total=0;for(const segment of segments){segment.start=total;total+=segment.length;}
  const groups=new Map<string,{positions:number[];indices:number[]}>();
  if(!segments.length)return [];
  const stations=[segments[0].from,...segments.map(s=>s.to)];
  const normals=stationNormals(stations);
  const point=(x:number,station:number,z:number):number[]=>{
    const index=segments.findIndex(s=>station<=s.start+s.length+1e-7);
    const i=index<0?segments.length-1:index,segment=segments[i];
    const t=(station-segment.start)/segment.length;
    // Use the same station frame as the shared street bands. Both sides of a
    // bend meet at one offset station rather than inheriting the previous arm.
    const nx=normals[i].x+(normals[i+1].x-normals[i].x)*t;
    const ny=normals[i].y+(normals[i+1].y-normals[i].y)*t;
    return [segment.from.x+(segment.to.x-segment.from.x)*t-nx*x,segment.from.y+(segment.to.y-segment.from.y)*t-ny*x,z+program.baseLiftM];
  };
  const quad=(material:string,vertices:number[][])=>{
    const group=groups.get(material)??{positions:[],indices:[]};const n=group.positions.length/3;
    group.positions.push(...vertices.flat());group.indices.push(n,n+1,n+2,n,n+2,n+3);groups.set(material,group);
  };
  const clipAtStation=(vertices:number[][], boundary:number, keepAfter:boolean):number[][]=>{
    const result:number[][]=[];
    for(let i=0;i<vertices.length;i++){
      const a=vertices[i],b=vertices[(i+1)%vertices.length];
      const insideA=keepAfter?a[1]>=boundary:a[1]<=boundary;
      const insideB=keepAfter?b[1]>=boundary:b[1]<=boundary;
      if(insideA)result.push(a);
      if(insideA!==insideB){const t=(boundary-a[1])/(b[1]-a[1]);result.push(a.map((v,j)=>v+(b[j]-v)*t));}
    }
    return result;
  };
  const rect=(material:string,x0:number,x1:number,y0:number,y1:number,z:number,height=0)=>{
    y0=Math.max(0,y0);y1=Math.min(total,y1);if(y1-y0<1e-6 || x1-x0<1e-6)return;
    const stations=[y0,...segments.slice(1).map(s=>s.start).filter(y=>y>y0+1e-7 && y<y1-1e-7),y1];
    for(let i=0;i<stations.length-1;i++){
      const a=point(x0,stations[i],z+height/2),b=point(x1,stations[i],z+height/2),c=point(x1,stations[i+1],z+height/2),d=point(x0,stations[i+1],z+height/2);
      quad(material,[a,b,c,d]);
      if(height>0){const low=[a,b,c,d].map(v=>[v[0],v[1],v[2]-height]);for(let j=0;j<4;j++)quad(material,[[a,b,c,d][j],low[j],low[(j+1)%4],[a,b,c,d][(j+1)%4]]);}
    }
  };
  const cells=nativeStreetGroundCells(width,fixtureLength,program.surfaceRegions);
  const centers=total<=fixtureLength?[total/2]:Array.from({length:Math.ceil(total/fixtureLength)},(_,i)=>fixtureLength*(i+.5));
  for(const center of centers){
    for(const cell of cells){
      const {x,y,width:w,depth:d}=cell,material=cell.material!;
      const a=x-w/2,b=x+w/2,c=y-d/2,e=y+d/2;
      rect(material,a,b,center+c,center+e,0);
      if(material==='paving' && program.paving==='stone'){
        for(let j=1;j<Math.trunc(d/.8);j++)rect('edge',a,b,center+c+j*.8-.0045,center+c+j*.8+.0045,.002);
        for(let j=1;j<Math.trunc(w/1.2);j++)rect('edge',a+j*1.2-.0045,a+j*1.2+.0045,center+c,center+e,.002);
      } else if(material==='paving' && program.paving==='brick'){
        const [tw,td]=program.pavingModuleM;
        for(let j=Math.floor(c/td);j<Math.ceil(e/td);j++){
          const y0=Math.max(c,j*td+.004),y1=Math.min(e,(j+1)*td-.004),offset=((j%2+2)%2)*tw/2;
          for(let i=Math.floor((a-offset)/tw);i<Math.ceil((b-offset)/tw);i++){
            rect(`paving.tile${((i*13+j*7)%4+4)%4}`,Math.max(a,i*tw+offset+.004),Math.min(b,(i+1)*tw+offset-.004),center+y0,center+y1,.003);
          }
        }
      }
    }
    for(const detail of program.details)rect(detail.material!,detail.x-detail.width/2,detail.x+detail.width/2,center+detail.y-detail.depth/2,center+detail.y+detail.depth/2,detail.z,detail.height);
    for(const detail of program.meshDetails??[])for(let i=0;i<detail.indices.length;i+=3){
      const triangle=detail.indices.slice(i,i+3).map(index=>[detail.positions[index*3],center+detail.positions[index*3+1],detail.positions[index*3+2]]);
      for(const segment of segments){
        const polygon=clipAtStation(clipAtStation(triangle,segment.start,true),segment.start+segment.length,false);
        if(polygon.length<3)continue;
        const group=groups.get(detail.material)??{positions:[],indices:[]},first=group.positions.length/3;
        group.positions.push(...polygon.flatMap(v=>point(v[0],v[1],v[2])));
        for(let j=1;j<polygon.length-1;j++)group.indices.push(first,first+j,first+j+1);
        groups.set(detail.material,group);
      }
    }
  }
  return [...groups].map(([material,data])=>{
    const geometry=new THREE.BufferGeometry();geometry.setAttribute('position',new THREE.Float32BufferAttribute(data.positions,3));geometry.setIndex(data.indices);geometry.computeVertexNormals();geometry.computeBoundingSphere();
    return {material,geometry};
  });
}
