import type { BuildingApproachSection } from './buildingEntranceApproach';
import { resolveBuildingGroundContact, type GroundPoint } from './buildingGroundContact';

// Display geometry only: these dimensions do not certify guards or structure.
const EDGE_BAND_M = .08, MIN_CLEAR_WIDTH_M = 1.2, RAIL_HEIGHT_M = 1.05;
export interface ApproachDetailGeometry { positions: number[]; indices: number[] }
export interface ApproachDetails {
  rails: ApproachDetailGeometry; supports: ApproachDetailGeometry;
  clearWidthM: number; supportCount: number; guardedSectionKinds: BuildingApproachSection['kind'][];
}

/** Side members stay inside the validated route. Both route ends stay open.
 * Landing posts reuse the measured-footprint solver, never a guessed ground plane. */
export function buildApproachDetails(input: {
  sections: BuildingApproachSection[]; sectionDrops: number[]; steps: number; widthM: number;
  start: GroundPoint; toward: GroundPoint; baseHeightM: number; bodyDepthM: number;
  lng: number; lat: number; ground: Parameters<typeof resolveBuildingGroundContact>[3];
}): {status:'ready'; details:ApproachDetails} | {status:'unresolved'; reason:string} {
  const {sections,sectionDrops,steps,widthM,start,toward,baseHeightM,bodyDepthM,lng,lat,ground}=input;
  const rails:ApproachDetailGeometry={positions:[],indices:[]},supports:ApproachDetailGeometry={positions:[],indices:[]};
  const normal:GroundPoint=[-toward[1],toward[0]];
  const xy=(distance:number,offset:number):GroundPoint=>[
    start[0]+toward[0]*distance+normal[0]*offset,start[1]+toward[1]*distance+normal[1]*offset];
  const guarded=sections.filter((section,i)=>sectionDrops[i]>.3 ||
    (section.kind==='flight'&&Math.abs(section.endHeightM-section.startHeightM)>.3));
  const clearWidthM=widthM-(guarded.length?2*EDGE_BAND_M:0);
  if(clearWidthM<MIN_CLEAR_WIDTH_M-1e-6)return {status:'unresolved',reason:'entrance_clear_width_too_small'};
  // Prism with vertical sides, in route coordinates; sloped top/bottom for rails.
  const member=(from:number,to:number,offset:number,halfWidth:number,lowA:number,highA:number,lowB=lowA,highB=highA)=>{
    const base=rails.positions.length/3;
    for(const [distance,side,low,high] of [[from,offset-halfWidth,lowA,highA],[to,offset-halfWidth,lowB,highB],
      [to,offset+halfWidth,lowB,highB],[from,offset+halfWidth,lowA,highA]]){
      const [x,y]=xy(distance,side);rails.positions.push(x,y,low-baseHeightM,x,y,high-baseHeightM);
    }
    for(let edge=0;edge<4;edge++){const a=base+edge*2,b=base+(edge+1)%4*2;rails.indices.push(a,b,b+1,a,b+1,a+1);}
    rails.indices.push(base+1,base+3,base+5,base+1,base+5,base+7,base,base+4,base+2,base,base+6,base+4);
  };
  const length=sections[sections.length-1].endM;
  for(const section of guarded){
    const from=Math.max(.04,section.startM),to=Math.min(length-.04,section.endM);
    if(to<=from)continue;
    const ramp=(d:number)=>section.startHeightM+(section.endHeightM-section.startHeightM)*
      (d-section.startM)/(section.endM-section.startM);
    const tread=(d:number)=>{
      if(section.kind!=='flight')return section.endHeightM;
      const rise=section.endHeightM-section.startHeightM;
      const index=Math.min(steps-1,Math.floor((d-section.startM)/(section.endM-section.startM)*steps));
      return section.startHeightM+rise*(rise>=0?index+1:index)/steps;
    };
    for(const side of [-1,1]){
      const offset=side*(widthM/2-.04);
      member(from,to,offset,.03,ramp(from)+RAIL_HEIGHT_M-.04,ramp(from)+RAIL_HEIGHT_M,
        ramp(to)+RAIL_HEIGHT_M-.04,ramp(to)+RAIL_HEIGHT_M);
      const bays=Math.max(1,Math.ceil((to-from)/1.2));
      for(let i=0;i<=bays;i++){
        const d=from+(to-from)*i/bays;
        member(Math.max(from,d-.03),Math.min(to,d+.03),offset,.03,tread(d)-.03,ramp(d)+RAIL_HEIGHT_M);
      }
      const pickets=Math.ceil((to-from)/.11);
      for(let i=1;i<pickets;i++){
        const d=from+(to-from)*i/pickets;
        member(d-.01,d+.01,offset,.01,tread(d)-.01,ramp(d)+RAIL_HEIGHT_M-.02);
      }
    }
  }
  let supportCount=0;
  for(const section of sections.filter(section=>section.kind!=='flight')){
    const from=section.startM+.1,to=section.endM-.1;
    if(to<=from)continue;
    const bays=Math.max(1,Math.ceil((to-from)/1.5));
    for(let i=0;i<=bays;i++)for(const side of [-1,1]){
      const distance=from+(to-from)*i/bays,offset=side*(widthM/2-.1),half=.07;
      const ring=[xy(distance-half,offset-half),xy(distance+half,offset-half),
        xy(distance+half,offset+half),xy(distance-half,offset+half)];
      const pad=resolveBuildingGroundContact([ring],lng,lat,ground);
      if(pad.status!=='ready')return {status:'unresolved',reason:'incomplete_footprint_ground'};
      const underside=section.endHeightM-bodyDepthM;
      // Where terrain already meets the slab, it needs no visible post.
      if(pad.anchorHeight>=underside)continue;
      const base=supports.positions.length/3;
      for(let j=0;j<pad.positions.length;j+=3){
        const height=pad.positions[j+2]===0?underside:pad.positions[j+2]+pad.anchorHeight;
        supports.positions.push(pad.positions[j],pad.positions[j+1],height-baseHeightM);
      }
      supports.indices.push(...pad.indices.map(index=>index+base));supportCount++;
    }
  }
  return {status:'ready',details:{rails,supports,clearWidthM,supportCount,guardedSectionKinds:guarded.map(section=>section.kind)}};
}
