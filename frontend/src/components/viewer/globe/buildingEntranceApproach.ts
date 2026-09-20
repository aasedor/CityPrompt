import type { PedestrianStrip } from '@/features/pickPlace/pedestrianConnections';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '../mapEngine/geoUtils';
import { resolveBuildingGroundContact, type BuildingGroundContact, type GroundPoint } from './buildingGroundContact';
import { corridorOverlaps } from './parkAccessConnections';

// Concept geometry limits, not an accessibility or building-code assessment.
const MAX_RISE_M = .18, MIN_GOING_M = .28, MAX_TOTAL_RISE_M = 3;
// Render the stair as a shallow connected flight. Full-height skirts from
// every tread make a 2 m street-to-door climb look like a row of retaining
// walls; the building foundation remains the separate measured-ground support.
const MAX_STAIR_BODY_DEPTH_M = .24;
export const ENTRANCE_REVIEW_RELIEF_M = .3;
type Ground = Parameters<typeof resolveBuildingGroundContact>[3];
export type BuildingApproach = { status: 'unresolved'; reason: string } | {
  status: 'ready'; positions: number[]; indices: number[]; steps: number;
  startHeightM: number; endHeightM: number;
};

/** Connect an explicitly authored foot-of-steps anchor to its selected street.
 * Every tread reuses the full-polygon support solver; native meshes and terrain
 * remain unchanged. A route through a pad or a terrain ridge is unresolved. */
export function buildBuildingEntranceApproach(input: {
  contact: BuildingGroundContact; footprints: readonly GroundPoint[][];
  lng: number; lat: number; ground: Ground; strip: PedestrianStrip; heightAboveBaseM: number;
}): BuildingApproach {
  const { contact, footprints, lng, lat, ground, strip, heightAboveBaseM } = input;
  const fail = (reason: string): BuildingApproach => ({ status: 'unresolved', reason });
  if (contact.status !== 'ready' || ground.status !== 'ready') return fail('ground_not_ready');
  if (!Number.isFinite(heightAboveBaseM) || heightAboveBaseM < 0 || heightAboveBaseM > 3)
    return fail('entrance_height_invalid');
  if (!Number.isFinite(strip.startLiftM)) return fail('entrance_height_invalid');
  const east = metersPerDegLon(lat);
  const local = ([x,y]: GroundPoint): GroundPoint => [(x-lng)*east,(y-lat)*METERS_PER_DEG_LAT];
  const a = local(strip.start), b = local(strip.end), length = Math.hypot(b[0]-a[0],b[1]-a[1]);
  if (!Number.isFinite(length) || length < .1 || length > 30 || !Number.isFinite(strip.widthM) || strip.widthM < 1.2 || strip.widthM > 4)
    return fail('entrance_approach_too_short');
  const distanceToEdge = Math.min(...footprints.flatMap(ring => ring.map((p,i) => {
    const q=ring[(i+1)%ring.length],dx=q[0]-p[0],dy=q[1]-p[1];
    const t=Math.max(0,Math.min(1,((b[0]-p[0])*dx+(b[1]-p[1])*dy)/(dx*dx+dy*dy||1)));
    return Math.hypot(b[0]-p[0]-t*dx,b[1]-p[1]-t*dy);
  })));
  if (distanceToEdge > .1) return fail('entrance_anchor_not_at_edge');
  const toward: GroundPoint = [(b[0]-a[0])/length,(b[1]-a[1])/length];
  // The final 20 cm at the pad can share its top; a descending run cannot
  // tunnel through the rest of this building or a detached module.
  const beforePad: GroundPoint = [b[0]-toward[0]*.2,b[1]-toward[1]*.2];
  if (footprints.some(ring => corridorOverlaps(a,beforePad,ring,strip.widthM/2)))
    return fail('entrance_approach_obstructed');
  const startGround = ground.heightAt(...strip.start);
  if (startGround === null || !Number.isFinite(startGround)) return fail('incomplete_footprint_ground');
  const startHeightM = startGround + strip.startLiftM, endHeightM = contact.anchorHeight + heightAboveBaseM;
  const rise = endHeightM-startHeightM, steps = Math.ceil(Math.abs(rise)/MAX_RISE_M);
  if (Math.abs(rise) > MAX_TOTAL_RISE_M || (steps > 1 && length/steps < MIN_GOING_M))
    return fail('entrance_approach_too_short');
  const normal: GroundPoint = [-toward[1]*strip.widthM/2,toward[0]*strip.widthM/2];
  const at = (t: number): GroundPoint => [a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t];
  const footprint = (p: GroundPoint,q: GroundPoint): GroundPoint[] => [
    [p[0]-normal[0],p[1]-normal[1]],[q[0]-normal[0],q[1]-normal[1]],
    [q[0]+normal[0],q[1]+normal[1]],[p[0]+normal[0],p[1]+normal[1]],
  ];
  const fullSupport = resolveBuildingGroundContact([footprint(a,b)],lng,lat,ground);
  if (fullSupport.status !== 'ready') return fail('incomplete_footprint_ground');
  const count = Math.max(1,steps), positions: number[] = [], indices: number[] = [];
  for (let i=0;i<count;i++) {
    const pad = resolveBuildingGroundContact([footprint(at(i/count),at((i+1)/count))],lng,lat,ground);
    if (pad.status !== 'ready') return fail('incomplete_footprint_ground');
    const top = rise >= 0 ? startHeightM+rise*(i+1)/count : startHeightM+rise*i/count;
    // No cut/fill guess: the entire tread must clear the measured triangle field.
    if (pad.anchorHeight-.04 > top+.005) return fail('entrance_terrain_intersection');
    const offset=positions.length/3;
    for (let j=0;j<pad.positions.length;j+=3) {
      const z=pad.positions[j+2];
      const height=z === 0 ? top : Math.max(z+pad.anchorHeight,top-MAX_STAIR_BODY_DEPTH_M);
      positions.push(pad.positions[j],pad.positions[j+1],height-contact.anchorHeight);
    }
    indices.push(...pad.indices.map(index=>index+offset));
  }
  // Two shallow continuous stringers make the stair read as one flight
  // supported at street and foundation, rather than disconnected slabs. They
  // are display massing only; this does not establish structural adequacy.
  const perpendicular: GroundPoint = [-toward[1],toward[0]];
  for (const side of [-1,1]) {
    const center=side*(strip.widthM/2-.1), halfWidth=.06;
    const offsets=[center-halfWidth,center+halfWidth];
    const xy=(point: GroundPoint, offset: number): GroundPoint =>
      [point[0]+perpendicular[0]*offset,point[1]+perpendicular[1]*offset];
    const corners=[xy(a,offsets[0]),xy(b,offsets[0]),xy(b,offsets[1]),xy(a,offsets[1])];
    const base=positions.length/3;
    corners.forEach(([x,y],index)=>{
      const top=(index===0||index===3?startHeightM:endHeightM)-.07-contact.anchorHeight;
      positions.push(x,y,top-MAX_STAIR_BODY_DEPTH_M,x,y,top);
    });
    for(let edge=0;edge<4;edge++){
      const p=base+edge*2,q=base+((edge+1)%4)*2;
      indices.push(p,q,q+1,p,q+1,p+1);
    }
    indices.push(base+1,base+3,base+5,base+1,base+5,base+7);
    indices.push(base,base+4,base+2,base,base+6,base+4);
  }
  return { status:'ready', positions, indices, steps:count, startHeightM, endHeightM };
}
