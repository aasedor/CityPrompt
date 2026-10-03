/** A bounded straight-road pilot. Coordinates are local metres: x along the
 * road, y across it, z up. Source ground is never edited by this planner. */
export interface CorridorProfilePoint { x: number; z: number }
export interface RoadTerrainTransitionOptions {
  profile: CorridorProfilePoint[];
  halfWidth: number;
  shoulderWidth: number;
  blendWidth: number;
  endBlend: number;
  startHeight: number;
  endHeight: number;
  tieLength: number;
  startCrossSection?: {y:number;z:number}[];
  endCrossSection?: {y:number;z:number}[];
  leftEdge?: 'slope' | 'retaining';
  rightEdge?: 'slope' | 'retaining';
  leftBlendWidth?: number;
  rightBlendWidth?: number;
}
export interface CorridorProbe { x: number; y: number; z: number | null }
export interface RoadTerrainTransition {
  length: number;
  outerWidth: number;
  options: RoadTerrainTransitionOptions;
  roadHeight: (x: number, y: number) => number;
  weight: (x: number, y: number) => number;
  groundHeight: (x: number, y: number, contextZ: number) => number;
  profileRetention: number;
  edgeAt: (y: number) => 'slope' | 'retaining';
  blendWidthAt: (y: number) => number;
  outerWidthAt: (y: number) => number;
  raisedGrade?: boolean;
}
const clamp = (v: number, a = 0, b = 1) => Math.max(a, Math.min(b, v));
/** Quintic falloff: height, slope and curvature vanish at the existing ground. */
export const corridorEase = (v: number) => { const t = clamp(v); return t*t*t*(t*(6*t-15)+10); };

export function createRoadTerrainTransition(input: RoadTerrainTransitionOptions): RoadTerrainTransition {
  const o = { ...input, profile: input.profile.map(p => ({...p})),
    startCrossSection:input.startCrossSection?.map(p=>({...p})),endCrossSection:input.endCrossSection?.map(p=>({...p})) };
  const values = [o.halfWidth, o.shoulderWidth, o.blendWidth, o.endBlend,
    o.startHeight, o.endHeight, o.tieLength, o.leftBlendWidth??o.blendWidth,
    o.rightBlendWidth??o.blendWidth, ...o.profile.flatMap(p => [p.x,p.z])];
  if (values.some(v => !Number.isFinite(v)) || o.profile.length < 3 || o.profile.length > 301
    || o.profile[0].x !== 0 || o.halfWidth < 1.5 || o.halfWidth > 8
    || o.shoulderWidth < .3 || o.shoulderWidth > 3 || o.blendWidth < 4 || o.blendWidth > 20
    || [o.leftBlendWidth,o.rightBlendWidth].some(w=>w!==undefined&&(w<4||w>20))
    || [o.leftEdge,o.rightEdge].some(e=>e!==undefined&&e!=='slope'&&e!=='retaining')
    || o.endBlend < 4 || o.endBlend > 20 || o.tieLength < 10
    || o.profile.some((p,i) => i > 0 && (p.x <= o.profile[i-1].x || p.x-o.profile[i-1].x > 5))) {
    throw new Error('Invalid road transition dimensions or ground profile.');
  }
  const length = o.profile[o.profile.length-1].x;
  if (length < 25 || length > 300 || o.tieLength > length/2) throw new Error('Road transition needs a longer route.');
  // A small symmetric smoothing filter removes 2 m raster chatter. The original
  // source profile remains in options for provenance; no site datum is shifted.
  const smooth = o.profile.map((p,i,a) => ({x:p.x, z:
    (a[Math.max(0,i-1)].z + 2*p.z + a[Math.min(a.length-1,i+1)].z)/4}));
  const slopes = smooth.map((_,i,a) => {
    const left = a[Math.max(0,i-1)], right = a[Math.min(a.length-1,i+1)];
    return (right.z-left.z)/(right.x-left.x);
  });
  const sourceAt = (x: number) => {
    const v = clamp(x,0,length), i = Math.min(smooth.length-2, Math.max(0, smooth.findIndex(p=>p.x>=v)-1));
    const a=smooth[i], b=smooth[i+1], span=b.x-a.x, t=(v-a.x)/span;
    return (2*t**3-3*t*t+1)*a.z + (t**3-2*t*t+t)*span*slopes[i]
      + (-2*t**3+3*t*t)*b.z + (t**3-t*t)*span*slopes[i+1];
  };
  const desiredCentreAt = (x:number) => {
    const v=clamp(x,0,length);
    // Local endpoint corrections have compact support. Ground elsewhere and
    // the unmodified central source profile are not shifted to fit a junction.
    return sourceAt(v) + (o.startHeight-sourceAt(0))*(1-corridorEase(v/o.tieLength))
      + (o.endHeight-sourceAt(length))*(1-corridorEase((length-v)/o.tieLength));
  };
  const lineAt=(x:number)=>o.startHeight+(o.endHeight-o.startHeight)*clamp(x/length);
  if(Math.abs(o.endHeight-o.startHeight)/length>.10)throw new Error('Road grade exceeds the pilot limit; lengthen the connection transition.');
  let profileRetention=1;
  const centreAt=(x:number)=>lineAt(x)+profileRetention*(desiredCentreAt(x)-lineAt(x));
  const maximumGrade=()=>{
    let previous=centreAt(0),grade=0;
    for(let x=.25;x<=length;x+=.25){const z=centreAt(x);grade=Math.max(grade,Math.abs(z-previous)/.25);previous=z;}
    return grade;
  };
  // Grade the proposed road when the endpoint mismatch would otherwise make a
  // hump. This is local cut/fill design, not a correction to source elevations.
  // Keep as much of the source profile as the bounded grade can support.
  if(maximumGrade()>.10){
    let low=0,high=1;
    for(let i=0;i<24;i++){profileRetention=(low+high)/2;if(maximumGrade()<=.10)low=profileRetention;else high=profileRetention;}
    profileRetention=low;
  }
  for(const section of [o.startCrossSection,o.endCrossSection])if(section && (section.length<3
    || section[0].y> -o.halfWidth-o.shoulderWidth || section[section.length-1].y<o.halfWidth+o.shoulderWidth
    || section.some((p,i)=>!Number.isFinite(p.y)||!Number.isFinite(p.z)||i>0&&p.y<=section[i-1].y)))
    throw new Error('The complete measured road-end cross section is required.');
  const crossAt=(section:{y:number;z:number}[]|undefined,y:number,centre:number,crown:number)=>{
    if(!section)return crown;
    const v=clamp(y,section[0].y,section[section.length-1].y);
    const i=Math.max(0,Math.min(section.length-2,section.findIndex(p=>p.y>=v)-1));
    const a=section[i],b=section[i+1];return a.z+(b.z-a.z)*(v-a.y)/(b.y-a.y)-centre;
  };
  const roadHeight = (x:number,y:number) => {
    const crown=-Math.min(Math.abs(y),o.halfWidth)*.02;
    const crossTieLength=Math.max(6,o.tieLength);
    return centreAt(x)+crown+(crossAt(o.startCrossSection,y,o.startHeight,crown)-crown)*(1-corridorEase(x/crossTieLength))
      +(crossAt(o.endCrossSection,y,o.endHeight,crown)-crown)*(1-corridorEase((length-x)/crossTieLength));
  };
  const inner=o.halfWidth+o.shoulderWidth;
  const edgeAt=(y:number)=> (y>=0?o.leftEdge:o.rightEdge)??'slope';
  // The short retaining transition is entirely enclosed by the physical wall.
  // Never expose it as a steep grass slope or use it without the wall geometry.
  const blendWidthAt=(y:number)=>edgeAt(y)==='retaining'?.2:(y>=0?o.leftBlendWidth:o.rightBlendWidth)??o.blendWidth;
  const outerWidthAt=(y:number)=>inner+blendWidthAt(y);
  const outerWidth=Math.max(outerWidthAt(-1),outerWidthAt(1));
  const weight = (x:number,y:number) => Math.abs(y)>=outerWidthAt(y)-1e-9?0:
    (1-corridorEase((Math.abs(y)-inner)/blendWidthAt(y)))
    * (x<0 ? corridorEase((x+o.endBlend)/o.endBlend) : x>length ? 1-corridorEase((x-length)/o.endBlend) : 1);
  const groundHeight = (x:number,y:number,contextZ:number) => {
    const w=weight(x,y);
    return contextZ + w*(roadHeight(x,y)-.01-contextZ);
  };
  return {length,outerWidth,options:o,roadHeight,weight,groundHeight,profileRetention,edgeAt,blendWidthAt,outerWidthAt};
}

/** Check the complete transition footprint before any tile is changed. The
 * caller samples a regular grid and supplies an independent bare-earth model.
 * A canopy hit is not usable ground, even if it is repeatable. */
export function validateCorridorContext(field:RoadTerrainTransition, probes:CorridorProbe[],
  expectedGround:(x:number,y:number)=>number|null): {ok:boolean; reason?:string; problem?:CorridorProbe; maxChangeM:number} {
  let maxChangeM=0;
  if(!probes.length) return {ok:false,reason:'Ground samples are missing.',maxChangeM};
  for(const p of probes) {
    if(field.weight(p.x,p.y)===0)continue;
    const expected=expectedGround(p.x,p.y);
    if(p.z===null || !Number.isFinite(p.z) || expected===null || !Number.isFinite(expected))
      return {ok:false,reason:'Ground coverage is incomplete. Move the route or measure again.',maxChangeM};
    if(Math.abs(p.z-expected) > .75)
      return {ok:false,reason:'A tree, structure or uncertain surface intersects the transition. Move the route to clear ground.',problem:p,maxChangeM};
    const change=Math.abs(field.groundHeight(p.x,p.y,p.z)-p.z);
    maxChangeM=Math.max(maxChangeM,change);
    // Quintic transition's maximum derivative is 1.875. Reject a short, steep
    // verge rather than concealing a large datum mismatch with a narrow skirt.
    if(field.edgeAt(p.y)==='retaining') {
      if(change>2.5)return {ok:false,reason:'The retaining edge would exceed the supported height. Move or lengthen the route.',problem:p,maxChangeM};
    } else if(1.875*Math.abs(field.roadHeight(p.x,p.y)-.01-p.z)*field.weight(p.x,0)/field.blendWidthAt(p.y) > .4)
      return {ok:false,reason:'The verge needs more room to meet the existing ground.',problem:p,maxChangeM};
  }
  return {ok:true,maxChangeM};
}

/** Finite choices: prefer both natural slopes, then one retaining edge, then
 * two. Every candidate still passes the same independent ground/object checks.
 * A caller must build and validate the physical walls before installation. */
export function fitRoadTerrainEdges(options:RoadTerrainTransitionOptions,probes:CorridorProbe[],
  expectedGround:(x:number,y:number)=>number|null,
  grade:(field:RoadTerrainTransition)=>RoadTerrainTransition=field=>field) {
  let last:ReturnType<typeof validateCorridorContext>|undefined;
  for(const [leftEdge,rightEdge] of [['slope','slope'],['retaining','slope'],['slope','retaining'],['retaining','retaining']] as const) {
    const field=grade(createRoadTerrainTransition({...options,leftEdge,rightEdge}));
    const validation=validateCorridorContext(field,probes,expectedGround);
    if(validation.ok)return {field,validation};
    last=validation;
  }
  throw new Error(`${last!.reason} ${JSON.stringify({problem:last!.problem})}`);
}
