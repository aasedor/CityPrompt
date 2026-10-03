import {corridorEase,type CorridorProbe,type RoadTerrainTransition} from './roadTerrainTransition';

/** Raise a road over independently verified ground across its full width.
 * Endpoint cross sections stay fixed. If the grade cannot reach an intervening
 * rise, refuse the route rather than silently digging a trench through it. */
export function raiseRoadAboveGround(base:RoadTerrainTransition,probes:CorridorProbe[],
  expected:(x:number,y:number)=>number|null,clearance=.12,requestedRaise=0):RoadTerrainTransition {
  const spacing=.5,rows=Math.round(base.length/spacing),width=base.options.halfWidth+.5;
  if(Math.abs(rows*spacing-base.length)>1e-6||clearance<.05||clearance>.3||!Number.isFinite(clearance)
    ||!Number.isFinite(requestedRaise)||requestedRaise<0||requestedRaise>1.5)
    throw new Error('Invalid raised-road sampling dimensions.');
  const columns=Math.ceil(width*2/.5);
  const samples=Array.from({length:rows+1},()=>new Map<number,number>());
  for(const p of probes) {
    const row=Math.round(p.x/spacing),column=Math.round((p.y+width)/(2*width)*columns);
    if(row<0||row>rows||column<0||column>columns||Math.abs(row*spacing-p.x)>1e-6
      ||Math.abs(-width+2*width*column/columns-p.y)>1e-6||samples[row].has(column))
      throw new Error('The complete raised-road ground grid is required.');
    const reference=expected(p.x,p.y);
    if(p.z===null||!Number.isFinite(p.z)||reference===null||!Number.isFinite(reference))
      throw new Error('Ground beneath the road is incomplete. Wait for the map or move the route.');
    if(Math.abs(p.z-reference)>.75)
      throw new Error('An object or uncertain surface is beneath the road. Move the route to clear ground.');
    samples[row].set(column,p.z);
  }
  if(samples.some(row=>row.size!==columns+1))throw new Error('The complete raised-road ground grid is required.');
  const offset=(x:number,y:number)=>base.roadHeight(x,y)-base.roadHeight(x,0);
  const floor=samples.map((row,i)=>{
    const x=i*spacing,distance=Math.min(x,base.length-x);
    const pad=clearance*corridorEase(distance/4)+requestedRaise*corridorEase(distance/base.options.tieLength);
    return Math.max(...[...row].map(([column,z])=>z+pad-offset(x,-width+2*width*column/columns)));
  });
  // Bound every sampled longitudinal strip, including crowned road edges.
  // Difference constraints account for the measured crossfall at both joins.
  const limits=Array.from({length:rows},(_,i)=>{
    const changes=Array.from({length:columns+1},(_,j)=>{
      const y=-width+2*width*j/columns;return offset((i+1)*spacing,y)-offset(i*spacing,y);
    });
    return {low:Math.max(...changes.map(d=>-.10*spacing-d)),high:Math.min(...changes.map(d=>.10*spacing-d))};
  });
  const start=base.roadHeight(0,0),end=base.roadHeight(base.length,0);
  const feasible=(h:number[])=>h[0]<=start+1e-6&&h[rows]<=end+1e-6;
  const project=(h:number[])=>{
    for(let i=rows-1;i>=0;i--)h[i]=Math.max(h[i],h[i+1]-limits[i].high);
    for(let i=1;i<=rows;i++)h[i]=Math.max(h[i],h[i-1]+limits[i-1].low);
    return h;
  };
  let heights=project(floor.slice());
  if(limits.some(l=>l.low>l.high)||!feasible(heights))
    throw new Error(`This route cannot stay above the ground and meet both street ends at the supported grade. Lengthen the approach or move the route. ${JSON.stringify({start,end,requiredStart:heights[0],requiredEnd:heights[rows]})}`);
  heights[0]=start;heights[rows]=end;
  // Round local height chatter while maintaining the measured lower bound and
  // grade limits. Fixed iteration count; original DEM and samples stay intact.
  for(let pass=0;pass<12;pass++) {
    const smoothed=project(heights.map((z,i)=>i===0?start:i===rows?end:
      Math.max(floor[i],(heights[i-1]+2*z+heights[i+1])/4)));
    if(!feasible(smoothed))break;
    smoothed[0]=start;smoothed[rows]=end;heights=smoothed;
  }
  const centreAt=(x:number)=>{
    const v=Math.max(0,Math.min(rows,x/spacing)),i=Math.min(rows-1,Math.floor(v));
    return heights[i]+(heights[i+1]-heights[i])*(v-i);
  };
  const roadHeight=(x:number,y:number)=>centreAt(x)+offset(x,y);
  return {...base,raisedGrade:true,roadHeight,groundHeight:(x,y,z)=>z+base.weight(x,y)*(roadHeight(x,y)-.01-z)};
}
