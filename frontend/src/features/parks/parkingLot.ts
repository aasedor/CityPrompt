import { BufferGeometry, Float32BufferAttribute } from 'three';
import polygonClipping from 'polygon-clipping';
export interface ParkingRecipe { version: 1; rowAngle: number }
type Point = number[];
export interface ParkingLayout { spaces: {corners:Point[]; front:'north'|'south'}[]; aisles:Point[][]; problem:string|null }
const STALL_WIDTH = 2.7, STALL_DEPTH = 5.5, AISLE = 6, MARGIN = .5;
const MODULE = STALL_DEPTH * 2 + AISLE;
const area = (ring:Point[]) => Math.abs(ring.reduce((sum,p,i)=>{
  const q=ring[(i+1)%ring.length]; return sum+p[0]*q[1]-p[1]*q[0];
},0))/2;
const rectangle = (x:number,y:number,w:number,h:number):Point[] => [[x,y],[x+w,y],[x+w,y+h],[x,y+h]];
/** Versioned concept recipe. Fixed bays and a shared side spine; no stretched stalls.
 * Complete two-row modules must connect to the spine. Concave cut-outs are never
 * bridged by paint or a drive aisle. Work is bounded and runs only on recipe edits. */
export function parkingLayout(outline:Point[],recipe:ParkingRecipe):ParkingLayout {
  const fail=(problem:string):ParkingLayout=>({spaces:[],aisles:[],problem});
  if(![0,90].includes(recipe.rowAngle))return fail('Choose rows along or across the first edge. Rotate the whole lot for another bearing.');
  if(recipe.version!==1 || !Number.isFinite(recipe.rowAngle) || Math.abs(recipe.rowAngle)>180
    || outline.length<3 || outline.length>64 || outline.some(p=>p.length!==2||!p.every(Number.isFinite)))
    return fail('Use a valid parking outline and row direction.');
  if(area(outline)<1 || area(outline)>15000)return fail('Keep each parking lot between 1 and 15,000 m².');
  // Work in metres along the first drawn edge, with a user-adjustable row bearing.
  const origin=outline[0],edge=outline[1];
  const angle=Math.atan2(edge[1]-origin[1],edge[0]-origin[0])+recipe.rowAngle*Math.PI/180;
  const c=Math.cos(angle),s=Math.sin(angle);
  const local=outline.map(p=>[(p[0]-origin[0])*c+(p[1]-origin[1])*s,-(p[0]-origin[0])*s+(p[1]-origin[1])*c]);
  const world=(p:Point)=>[origin[0]+p[0]*c-p[1]*s,origin[1]+p[0]*s+p[1]*c];
  const minX=Math.min(...local.map(p=>p[0])), maxX=Math.max(...local.map(p=>p[0]));
  const minY=Math.min(...local.map(p=>p[1])), maxY=Math.max(...local.map(p=>p[1]));
  if(maxX-minX>300 || maxY-minY>300)return fail('Keep each parking lot within 300 m across.');
  const ring=[...local,local[0]] as [number,number][];
  const fits=(points:Point[])=>{
    try {
      const remainder=polygonClipping.difference([[...points,points[0]] as [number,number][]],[ring]);
      return remainder.reduce((sum,p)=>sum+area(p[0]),0)<1e-5;
    } catch {return false;}
  };
  const spaces:ParkingLayout['spaces']=[], aisles:Point[][]=[];
  const bottom=minY+MARGIN;
  let left=minX+MARGIN;
  // A single continuous spine is deliberately reserved even when some rows do not fit.
  // Bounded half-metre search allows tapered edges without putting an aisle outside the lot.
  while(left+AISLE+STALL_WIDTH<=maxX-MARGIN && !fits(rectangle(left,bottom,AISLE,maxY-minY-2*MARGIN)))left+=.5;
  const spine=rectangle(left,bottom,AISLE,maxY-minY-2*MARGIN);
  const startX=left+AISLE;
  if(maxY-minY<2*MARGIN || !fits(spine))return {spaces,aisles,problem:'This outline has no clear side drive aisle. Change the row direction or split the lot.'};
  let lastRowTop=bottom;
  for(let y=bottom;y+MODULE<=maxY-MARGIN+1e-7;y+=MODULE){
    const row:ParkingLayout['spaces']=[];
    let endX=startX;
    for(let x=startX;x+STALL_WIDTH<=maxX-MARGIN+1e-7;x+=STALL_WIDTH){
      // Include the boundary setback, not just four painted corners.
      if(!fits(rectangle(x-MARGIN,y-MARGIN,STALL_WIDTH+2*MARGIN,MODULE+2*MARGIN)))break;
      if(!fits(rectangle(left,y+STALL_DEPTH,x+STALL_WIDTH-left,AISLE)))break;
      row.push({corners:rectangle(x,y,STALL_WIDTH,STALL_DEPTH).map(world),front:'north'},
        {corners:rectangle(x,y+STALL_DEPTH+AISLE,STALL_WIDTH,STALL_DEPTH).map(world),front:'south'});
      endX=x+STALL_WIDTH;
    }
    if(row.length){
      spaces.push(...row);
      aisles.push(rectangle(left,y+STALL_DEPTH,endX-left,AISLE).map(world));
      lastRowTop=y+MODULE;
    }
  }
  if(spaces.length>500)return fail('This lot exceeds 500 spaces. Split it into smaller lots.');
  if(spaces.length)aisles.unshift(rectangle(left,bottom,AISLE,lastRowTop-bottom).map(world));
  return {spaces,aisles,problem:spaces.length?null:'No complete parking rows fit. Enlarge the outline or change row direction.'};
}
/** Open edge faces the drive aisle. Only real thin paint quads, no backing plane. */
export function parkingMarkingSegments(layout:ParkingLayout):[Point,Point][] {
  return layout.spaces.flatMap(({corners:p,front})=>[
    [p[0],p[3]],[p[1],p[2]],front==='north'?[p[0],p[1]]:[p[3],p[2]],
  ] as [Point,Point][]);
}
export function parkingMarkingGeometry(layout:ParkingLayout, heightAt:(point:Point)=>number=()=>.025) {
  const vertices:number[]=[];
  for(const [a,b] of parkingMarkingSegments(layout)){
    const length=Math.hypot(b[0]-a[0],b[1]-a[1]);
    const dx=-(b[1]-a[1])/length*.05,dy=(b[0]-a[0])/length*.05;
    const p=[[a[0]+dx,a[1]+dy],[a[0]-dx,a[1]-dy],[b[0]-dx,b[1]-dy],[b[0]+dx,b[1]+dy]];
    for(const i of [0,1,2,0,2,3])vertices.push(p[i][0],p[i][1],heightAt(p[i])+.005);
  }
  const geometry=new BufferGeometry();
  geometry.setAttribute('position',new Float32BufferAttribute(vertices,3));
  geometry.computeVertexNormals();
  return geometry;
}
