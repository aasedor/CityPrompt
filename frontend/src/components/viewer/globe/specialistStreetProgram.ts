import * as THREE from 'three';
import type {StreetRouteStation} from './nativeStreetPilot';
import { ELEVATED_RAIL_VARIANT } from './elevatedRailProgram';

export const CANAL_VARIANT='amsterdam_gracht_v1';
export const BRIDGE_VARIANT='landmark_signature_bridge_v2';
export const isSpecialistStreet=(variant:unknown)=>variant===CANAL_VARIANT || variant===BRIDGE_VARIANT || variant===ELEVATED_RAIL_VARIANT;
export interface SpecialistFixture {kind:string;x:number;y:number;z:number;yaw:number;scale:number}

export function specialistRouteProblem(variant:string,route:StreetRouteStation[]):string|null {
  if(!isSpecialistStreet(variant))return null;
  const min=variant===ELEVATED_RAIL_VARIANT?48:variant===CANAL_VARIANT?80:260,max=variant===ELEVATED_RAIL_VARIANT?288:variant===CANAL_VARIANT?320:480;
  if(route.length<2)return 'Draw two endpoints for this straight specialist street.';
  const a=route[0],b=route[route.length-1],dx=b.x-a.x,dy=b.y-a.y,length=Math.hypot(dx,dy);
  if(!Number.isFinite(length)||length<min-.01||length>max+.01)
    return variant===ELEVATED_RAIL_VARIANT?'Keep the elevated rail route 48–288 m long.':variant===CANAL_VARIANT?'Keep the canal 80–320 m long so its basin and original crossing fit.':'Keep the bridge route 260–480 m long for its rigid span and two gradual approaches.';
  let previous=-1;
  for(const p of route){
    const x=p.x-a.x,y=p.y-a.y,station=(x*dx+y*dy)/length;
    if(!Number.isFinite(station)||Math.abs(x*dy-y*dx)/length>.05 || station<previous-.01)
      return 'Keep this route straight. Its crossing, banks or structural span cannot bend.';
    previous=station;
  }
  return null;
}

export function specialistFixtures(variant:string,length:number):SpecialistFixture[] {
  if(variant===ELEVATED_RAIL_VARIANT)throw new Error('Elevated rail fixtures require their locked source placements.');
  const fixtures:SpecialistFixture[]=[];
  const add=(kind:string,x:number,y:number,z=0,yaw=0)=>fixtures.push({kind,x,y,z,yaw,scale:1});
  if(variant===BRIDGE_VARIANT){add('bridge_structure',0,length/2);return fixtures;}
  // Three independent source programs reconstruct the native 80 m study once.
  // Only the open-channel end extends. The basin and arch never repeat.
  for(const kind of ['canal_ground','canal_crossing','canal_furnishings'])add(kind,0,40);
  for(let y=86;y+5<=length;y+=16)for(const sign of [-1,1]){
    add('canal_tree',sign*10.55,y,.065,sign<0?Math.PI:0);
    add('canal_bench',sign*10.25,y+4,0,sign<0?Math.PI:0);
    add('canal_lamp',sign*11.6,y-3);
  }
  for(let y=80;y+.1<=length;y+=8)for(const sign of [-1,1])add('canal_bollard',sign*9.45,y);
  return fixtures;
}

/** Source-height camera support, in metres above the prepared site. */
export function specialistWalkingHeight(variant:string,x:number,station:number,length:number):number|null {
  if(station<0||station>length)return null;
  // The public route stays below the protected tracks, including when a map
  // click initially hits the deck or train roof.
  if(variant===ELEVATED_RAIL_VARIANT)return Math.abs(x)<=13?.025:null;
  if(variant===BRIDGE_VARIANT){
    if(Math.abs(x)>12)return null;
    const approach=(length-100)/2;
    const grade=Math.min(1,station/approach,(length-station)/approach);
    return (Math.abs(x)>9.25?4.482:4.3)*Math.max(0,grade);
  }
  if(variant!==CANAL_VARIANT||Math.abs(x)>18)return null;
  const y=station-40,ax=Math.abs(x),halfdepth=3.2+Math.max(0,ax-9)*.3;
  const deck=.12+1.6*Math.max(0,1-(x/16)**2);
  if(ax<=16 && Math.abs(y-20)<=halfdepth)return deck;
  if(ax>=9){
    if(ax<16 && y>=8&&y<=32)return .123+1.6*Math.max(0,1-(x/16)**2)*Math.max(0,Math.min(1,(y-8)/(12-halfdepth),(32-y)/(12-halfdepth)));
    return .12;
  }
  if(y<=-32 || (ax>5 && y< -28-Math.sqrt(Math.max(0,16-(ax-5)**2))))return .12;
  // Open water is never a fictitious ground-level walking plane.
  return -2.05;
}

export function buildSpecialistStreetProgram(variant:string,route:StreetRouteStation[]) {
  const problem=specialistRouteProblem(variant,route);if(problem)throw new Error(problem);
  const a=route[0],b=route[route.length-1],length=Math.hypot(b.x-a.x,b.y-a.y),dx=(b.x-a.x)/length,dy=(b.y-a.y)/length;
  const groups=new Map<string,{positions:number[];indices:number[]}>();
  const face=(material:string,points:number[][])=>{
    const group=groups.get(material)??{positions:[],indices:[]},n=group.positions.length/3;
    for(const [x,y,z] of points)group.positions.push(a.x+dx*y+dy*x,a.y+dy*y-dx*x,z);
    group.indices.push(n,n+1,n+2,n,n+2,n+3);groups.set(material,group);
  };
  const box=(material:string,x0:number,x1:number,y0:number,y1:number,top:number,bottom=top)=>{
    const p=[[x0,y0,top],[x1,y0,top],[x1,y1,top],[x0,y1,top]];face(material,p);
    if(top>bottom)for(let i=0;i<4;i++){const u=p[i],v=p[(i+1)%4];face(material,[u,[u[0],u[1],bottom],[v[0],v[1],bottom],v]);}
  };
  if(variant===CANAL_VARIANT && length>80){
    box('water',-9,9,80,length,-2.05);
    const wells=[];for(let y=86;y+5<=length;y+=16)wells.push(y);
    for(const sign of [-1,1]){
      const rect=(mat:string,l:number,r:number,lo:number,hi:number,z:number,bottom=z)=>box(mat,sign<0?-r:l,sign<0?-l:r,lo,hi,z,bottom);
      rect('mortar',9,18,80,length,0,-2.8);
      const ys=[80,...wells.flatMap(y=>[y-1,y+1]),length];
      for(let j=0;j<ys.length-1;j++){
        const lo=ys[j],hi=ys[j+1],well=wells.some(y=>Math.abs((lo+hi)/2-y)<1);
        const strips=well?[[9,9.55],[11.55,11.7],[11.7,16.1],[16.1,18]]:[[9,11.7],[11.7,16.1],[16.1,18]];
        for(const [left,right] of strips){
          rect('mortar',left,right,lo,hi,.11,0);
          // Original 0.30 × 0.15 m brick pieces, phase continuous at station 80.
          const x0=sign<0?-right:left,x1=sign<0?-left:right;
          for(let row=Math.floor((lo-40)/.15);row<Math.ceil((hi-40)/.15);row++){
            const ya=Math.max(lo,row*.15+40+.006),yb=Math.min(hi,(row+1)*.15+40-.006),offset=((row%2+2)%2)*.15;
            if(yb<=ya)continue;
            for(let col=Math.floor((x0-offset)/.3);col<Math.ceil((x1-offset)/.3);col++){
              const xa=Math.max(x0,col*.3+offset+.006),xb=Math.min(x1,(col+1)*.3+offset-.006);
              if(xb>xa)box(left>=11.7&&right<=16.1?'roadbrick':'paving',xa,xb,ya,yb,.12);
            }
          }
        }
        if(well)rect('soil',9.55,11.55,lo,hi,.06,0);
      }
      for(const y of wells){
        for(const x of [9.54,11.56])rect('coping',x-.0275,x+.0275,y-1.04,y+1.04,.16,.04);
        for(const yy of [y-1.01,y+1.01])rect('coping',9.51,11.59,yy-.0275,yy+.0275,.16,.04);
      }
      rect('coping',8.96,9.26,80,length,.2,0);
      for(const x of [11.7,16.1])rect('coping',x-.07,x+.07,80,length,.145);
      for(let row=0;row<19;row++)for(let j=Math.floor((80-12)/.3);12+j*.3<length;j++){
        const ya=Math.max(80,12+j*.3+(row%2)*.15),yb=Math.min(length,12+j*.3+(row%2)*.15+.286);
        if(yb>ya)face('brick',[[sign*8.985,ya,-2.24+row*.12],[sign*8.985,yb,-2.24+row*.12],[sign*8.985,yb,-2.132+row*.12],[sign*8.985,ya,-2.132+row*.12]]);
      }
    }
  }
  if(variant===BRIDGE_VARIANT){
    const approach=(length-100)/2;
    for(const reverse of [false,true]){
      const station=(y:number)=>reverse?length-y:y;
      const ramp=(material:string,x0:number,x1:number,z:number)=>face(material,[[x0,station(0),0],[x1,station(0),0],[x1,station(approach),z],[x0,station(approach),z]]);
      ramp('asphalt',-9.25,9.25,4.3);
      const patch=(material:string,x0:number,x1:number,y0:number,y1:number,height:number,lift=0)=>{
        face(material,[[x0,station(y0),height*y0/approach+lift],[x1,station(y0),height*y0/approach+lift],
          [x1,station(y1),height*y1/approach+lift],[x0,station(y1),height*y1/approach+lift]]);
      };
      for(const x of [-7,-3.5,-.12,.12,3.5,7]){
        if(Math.abs(x)===3.5){for(let y=0;y<approach;y+=6)patch('paint',x-.05,x+.05,y,Math.min(y+3,approach),4.3,.007);}
        else patch('paint',x-.05,x+.05,0,approach,4.3,.007);
      }
      for(const sign of [-1,1]){
        const left=sign<0?-12:9.25,right=sign<0?-9.25:12;
        ramp('concrete',left,right,4.48);
        for(let row=0;row<Math.ceil(approach/.45);row++){
          const lo=row*.45+.006,hi=Math.min(approach,(row+1)*.45-.006),offset=(row%2)*.325;
          for(let col=Math.floor((left-offset)/.65);col<Math.ceil((right-offset)/.65);col++){
            const xa=Math.max(left,col*.65+offset+.006),xb=Math.min(right,(col+1)*.65+offset-.006);
            if(xb>xa&&hi>lo)patch('paving',xa,xb,lo,hi,4.48,.002);
          }
        }
        const x=sign*12;
        face('concrete',[[x,station(0),0],[x,station(approach),0],[x,station(approach),4.482],[x,station(0),0]]);
        // Kerb follows the same graded plane without scaling source-span meshes.
        face('concrete',[[sign*9.25,station(0),0],[sign*9.25,station(approach),4.3],[sign*9.25,station(approach),4.482],[sign*9.25,station(0),0]]);
        // Source-style open steel railing joins the fixed span's rail at 4.48 m.
        for(let y=0;y<=approach;y+=.28){
          const yy=station(y),z=4.48*y/approach;
          box('steel',sign*11.9-.012,sign*11.9+.012,yy-.012,yy+.012,z+1.2,z);
        }
        for(const lift of [.1,1.2]){
          patch('steel',sign*11.9-.028,sign*11.9+.028,0,approach,4.48,lift);
          for(const side of [-1,1])face('steel',[[sign*11.9+side*.028,station(0),lift-.028],
            [sign*11.9+side*.028,station(approach),4.48+lift-.028],
            [sign*11.9+side*.028,station(approach),4.48+lift],
            [sign*11.9+side*.028,station(0),lift]]);
        }
      }
    }
  }
  return [...groups].map(([material,data])=>{
    const geometry=new THREE.BufferGeometry();geometry.setAttribute('position',new THREE.Float32BufferAttribute(data.positions,3));
    geometry.setIndex(data.indices);geometry.computeVertexNormals();geometry.computeBoundingSphere();return {material,geometry};
  });
}
