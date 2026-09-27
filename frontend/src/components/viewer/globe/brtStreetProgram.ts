import * as THREE from 'three';
import type { StreetRouteStation } from './nativeStreetPilot';

export interface BrtStop { id: string; stationM: number }
export const BRT_VARIANT = 'brt_bus_rapid_transit_corridor_v0';
export const BRT_STOP_BOUNDS = { beforeM: 21, afterM: 33.5 } as const;
export interface BrtFixture {kind:string;x:number;y:number;z:number;yaw:number;scale:number}
export interface BrtBox {kind:'box';material:string;x:number;y:number;z:number;width:number;depth:number;height:number}
export interface BrtFace {kind:'face';material:string;points:number[][]}
export type BrtPrimitive = BrtBox | BrtFace;

/** The initial specialist capability is a straight, prepared-level corridor.
 * A stop owns the entire original platform/crossing assembly, never a repeated
 * shelter. Distances are measured from the authored first endpoint. */
export function brtRouteProblem(route:StreetRouteStation[], stops:unknown):string|null {
  if(!Array.isArray(stops) || stops.length>8)return 'BRT stops must be a list of at most eight selected positions.';
  if(route.length<2)return 'Draw a BRT route with two endpoints.';
  const a=route[0],b=route[route.length-1],dx=b.x-a.x,dy=b.y-a.y,length=Math.hypot(dx,dy);
  if(!Number.isFinite(length) || length<100-.01 || length>480+.01)return 'BRT needs a straight route 100–480 m long.';
  let previous=-1;
  for(const p of route){
    const along=((p.x-a.x)*dx+(p.y-a.y)*dy)/length;
    if(!Number.isFinite(along) || Math.abs((p.x-a.x)*dy-(p.y-a.y)*dx)/length>.05 || along<previous-.01)
      return 'Keep this BRT corridor straight. Its platform and crossing remain full size.';
    previous=along;
  }
  const ids=new Set<string>(); const positions:number[]=[];
  for(const raw of stops){
    if(!raw || typeof raw!=='object')return 'A BRT stop has an invalid position.';
    const stop=raw as BrtStop;
    if(typeof stop.id!=='string' || !/^[a-zA-Z0-9_-]{1,80}$/.test(stop.id) || ids.has(stop.id) || !Number.isFinite(stop.stationM))
      return 'A BRT stop has an invalid or duplicate identity.';
    ids.add(stop.id);
    if(stop.stationM<BRT_STOP_BOUNDS.beforeM || stop.stationM+BRT_STOP_BOUNDS.afterM>length+.001)
      return 'Leave 21 m before a stop and 33.5 m after it for the complete platform, ramps and crossing.';
    if(positions.some(p=>Math.abs(p-stop.stationM)<BRT_STOP_BOUNDS.beforeM+BRT_STOP_BOUNDS.afterM+2))
      return 'Separate stops by at least 56.5 m so their complete access areas do not overlap.';
    positions.push(stop.stationM);
  }
  return null;
}

function remaining(length:number, cuts:number[][]):number[][] {
  let spans=[[0,length]];
  for(const [lo,hi] of cuts)spans=spans.flatMap(([a,b])=>hi<=a || lo>=b?[[a,b]]:
    [[a,Math.max(a,lo)],[Math.min(b,hi),b]].filter(([x,y])=>y-x>1e-7));
  return spans;
}

/** Source brt-v004 coordinates are shifted by +50 m to route stationing.
 * Ground is reconstructed from its authoring dimensions; rigid equipment is
 * placed from the original module bytes. Source openings follow explicit stops. */
export function brtStreetLayout(length:number,stops:BrtStop[]) {
  const problem=brtRouteProblem([{x:0,y:0},{x:0,y:length}],stops);
  if(problem)throw new Error(problem);
  const primitives:BrtPrimitive[]=[],fixtures:BrtFixture[]=[];
  const box=(material:string,x:number,y:number,z:number,width:number,depth:number,height:number)=>{
    if(depth>1e-7 && width>1e-7)primitives.push({kind:'box',material,x,y,z,width,depth,height});
  };
  const slab=(material:string,x:number,width:number,a:number,b:number,bottom:number,top:number)=>
    box(material,x,(a+b)/2,(bottom+top)/2,width,b-a,top-bottom);
  const tile=(x:number,w:number,a:number,b:number)=>{
    const tw=.65,td=.45;
    // Retain the original world-phase, even when a stop moves.
    for(let j=Math.floor((a-50)/td);j<Math.ceil((b-50)/td);j++){
      const y0=Math.max(a,j*td+50+.006),y1=Math.min(b,(j+1)*td+50-.006),offset=((j%2+2)%2)*tw/2;
      for(let i=Math.floor((x-w/2-offset)/tw);i<Math.ceil((x+w/2-offset)/tw);i++){
        const x0=Math.max(x-w/2,i*tw+offset+.006),x1=Math.min(x+w/2,(i+1)*tw+offset-.006);
        box('paving',(x0+x1)/2,(y0+y1)/2,.152,x1-x0,y1-y0,0);
      }
    }
  };
  const place=(kind:string,x:number,y:number,z=0,yaw=0,scale=1)=>fixtures.push({kind,x,y,z,yaw,scale});
  slab('edge',0,40,0,length,-.31,-.05);slab('asphalt',0,29.8,0,length,-.05,0);
  const crossings=stops.map(s=>[s.stationM+19.5,s.stationM+33.5]);
  const treeStations:number[]=[];
  for(let y=8;y+3.5<=length;y+=14){
    if(!crossings.some(([a,b])=>y+.95>a && y-.95<b))treeStations.push(y);
  }
  for(const sign of [-1,1]){
    slab('bus_red',sign*2.4,3.4,0,length,-.026,.006);
    for(const [a,b] of remaining(length,stops.map(s=>[s.stationM+22.5,s.stationM+33.5]))){
      slab('paving',sign*18.55,2.9,a,b,0,.15);tile(sign*18.55,2.9,a,b);
    }
    const cuts=[0,length,...crossings.flat(),...treeStations.flatMap(y=>[y-.95,y+.95])]
      .filter(y=>y>=0 && y<=length).sort((a,b)=>a-b);
    for(let i=1;i<cuts.length;i++){
      const a=cuts[i-1],b=cuts[i],mid=(a+b)/2;
      if(crossings.some(([lo,hi])=>mid>lo && mid<hi))continue;
      if(treeStations.some(y=>Math.abs(mid-y)<.95)){
        slab('soil',sign*16.05,1.9,a,b,0,.16);
        slab('paving',sign*15,.2,a,b,0,.15);slab('paving',sign*17.05,.1,a,b,0,.15);
      }else{slab('paving',sign*16,2.2,a,b,0,.15);tile(sign*16,2.2,a,b);}
    }
    for(const y of treeStations){place('shade_tree',sign*16.05,y,.15,(y-50)*.21,.72);place('tree_well_grate',sign*16.05,y,.15);}
    for(let y=15;y+7<length;y+=28)if(!crossings.some(([a,b])=>y+.5>a && y-.5<b))place('light',sign*16.8,y,.15);
    for(let c=0;c<length;c+=100)for(const y of [c+10,c+88]){
      // A complete arrow and lettering must remain inside the route.
      if(y-6>=0 && y+6<=length)place('bus_symbol',sign*2.4,y,0,sign<0?Math.PI:0);
    }
    for(const x of [4.15,7,14.8])for(const [a,b] of remaining(length,stops.map(s=>[s.stationM+24,s.stationM+32])))
      slab('paint',sign*x,.09,a,b,.012,.012);
    for(let y=2;y<length;y+=7)slab('paint',sign*10.7,.1,y,Math.min(y+3,length),.012,.012);
  }
  for(const [lo,hi] of remaining(length,stops.map(s=>[s.stationM+19.5,s.stationM+32]))){
    if(hi-lo<1.2)throw new Error('There is not enough room for a complete rounded refuge island.');
    const p:number[][]=[];
    for(let j=0;j<=24;j++)p.push([.6*Math.cos(j*Math.PI/24),hi-.6+.6*Math.sin(j*Math.PI/24),.18]);
    for(let j=0;j<=24;j++)p.push([.6*Math.cos(Math.PI+j*Math.PI/24),lo+.6+.6*Math.sin(Math.PI+j*Math.PI/24),.18]);
    primitives.push({kind:'face',material:'curb',points:p});
    for(let i=0;i<p.length;i++){const a=p[i],b=p[(i+1)%p.length];primitives.push({kind:'face',material:'curb',points:[a,[a[0],a[1],0],[b[0],b[1],0],b]});}
  }
  for(const stop of stops)place('station_program',0,stop.stationM);
  return {primitives,fixtures};
}

/** BRT uses the common ENU frame and asset renderer. Specialist ground owns
 * physical height changes; no generic road plane can cover its ramps. */
export function buildBrtStreetProgram(route:StreetRouteStation[],stops:BrtStop[],baseLiftM:number) {
  const problem=brtRouteProblem(route,stops);if(problem)throw new Error(problem);
  const a=route[0],b=route[route.length-1],length=Math.hypot(b.x-a.x,b.y-a.y),dx=(b.x-a.x)/length,dy=(b.y-a.y)/length;
  const groups=new Map<string,{positions:number[];indices:number[]}>();
  const face=(material:string,points:number[][],triangles?:number[][])=>{
    const group=groups.get(material)??{positions:[],indices:[]},n=group.positions.length/3;
    for(const [x,y,z] of points)group.positions.push(a.x+dx*y+dy*x,a.y+dy*y-dx*x,z+baseLiftM);
    for(const triangle of triangles??[[0,1,2],[0,2,3]])group.indices.push(...triangle.map(i=>n+i));
    groups.set(material,group);
  };
  for(const item of brtStreetLayout(length,stops).primitives){
    if(item.kind==='face'){
      const triangles=item.points.length===4?undefined:THREE.ShapeUtils.triangulateShape(item.points.map(p=>new THREE.Vector2(p[0],p[1])),[]);
      face(item.material,item.points,triangles);continue;
    }
    const {x,y,z,width:w,depth:d,height:h}=item;
    const top=[[x-w/2,y-d/2,z+h/2],[x+w/2,y-d/2,z+h/2],[x+w/2,y+d/2,z+h/2],[x-w/2,y+d/2,z+h/2]];
    face(item.material,top);
    if(h>0)for(let i=0;i<4;i++){
      const p=top[i],q=top[(i+1)%4];face(item.material,[p,[p[0],p[1],p[2]-h],[q[0],q[1],q[2]-h],q]);
    }
  }
  return [...groups].map(([material,data])=>{
    const geometry=new THREE.BufferGeometry();geometry.setAttribute('position',new THREE.Float32BufferAttribute(data.positions,3));
    geometry.setIndex(data.indices);geometry.computeVertexNormals();geometry.computeBoundingSphere();return {material,geometry};
  });
}
