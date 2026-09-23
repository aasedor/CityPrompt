import type { SiteZone } from '@/types';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '@/components/viewer/mapEngine/geoUtils';
import { envelopeFits, envelopesOverlap } from '@/components/viewer/globe/neighborhoodParkLayout';
import { placementProblem, rectangleAt, rectangleDimensions } from './geometry';
import { streetFacingDegrees } from './streetFacing';
import { bufferLineToPolygon, effectiveRoadWidth, extractRenderableStreetCenterline } from '@/utils/roadGeometry';
import { readBuildingEntrance, resolvePedestrianConnections } from './pedestrianConnections';
import { resolvePilotStreetSectionProfile } from '@/components/viewer/globe/streetSectionProfiles';

type Point = { x: number; y: number };
export function snapBuildingMove(zone: SiteZone, coordinates: number[][], zones: SiteZone[], boundary?: SiteZone | null) {
  const entrance = zone.properties?.pedestrian_building_entrance as { automatic?: boolean } | undefined;
  if (entrance?.automatic && coordinates.length === 4) {
    const d = rectangleDimensions(coordinates);
    coordinates = rectangleAt(d.center,d.width,d.depth,streetFacingDegrees(d.center,zones,d.degrees));
  }
  return snapPlacement(coordinates,zones,boundary,zone.id,zone.properties);
}
/** Find a nearby clear position without changing the student's size or rotation.
 * Search is bounded for live dragging. Every candidate passes the same polygon
 * checks as a save, including concave boundaries and all neighbouring plots. */
export function snapPlacement(coordinates: number[][], zones: SiteZone[], boundary?: SiteZone | null, ignoreId?: string, properties?: SiteZone['properties']) {
  const context=zones.filter(z=>z.id!==ignoreId);
  const connectionFits = (coords:number[][]) => {
    if (!(properties?.pedestrian_building_entrance as {automatic?:boolean}|undefined)?.automatic) return true;
    const owner={id:ignoreId??'placement-preview',zone_type:'building',coordinates:coords,properties} as SiteZone;
    if (!readBuildingEntrance(owner,context)) return true; // Wait for a nearby street.
    const plan=resolvePedestrianConnections([...context,owner]).find(p=>p.ownerId===owner.id);
    return plan?.status==='connected' && plan.strips.every(strip=>Math.hypot(
      (strip.end[0]-strip.start[0])*metersPerDegLon(strip.start[1]),
      (strip.end[1]-strip.start[1])*METERS_PER_DEG_LAT) >= 2.5);
  };
  // Protect the street and already-working approaches as part of the usable
  // neighbourhood, rather than solving one plot overlap by blocking a route.
  const reserves: SiteZone[] = zones.filter(z=>z.zone_type==='road').flatMap(road=>{
    const line=extractRenderableStreetCenterline(road);
    const section=resolvePilotStreetSectionProfile(road);
    const width=section?.metricWidthLocked ? section.targetRowM ?? section.rowM : effectiveRoadWidth(road.properties);
    return line.length<2 ? [] : [{...road,id:`snap-road:${road.id}`,zone_type:'parking' as const,coordinates:bufferLineToPolygon(line,width+6)}];
  });
  for (const plan of resolvePedestrianConnections(context)) {
    if (plan.ownerId===ignoreId || plan.status!=='connected') continue;
    const owner=zones.find(z=>z.id===plan.ownerId)!;
    for (const strip of plan.strips) reserves.push({...owner,id:`snap-path:${strip.id}`,zone_type:'parking',coordinates:bufferLineToPolygon([strip.start,strip.end],strip.widthM+.3)});
  }
  zones=[...zones,...reserves];
  const problem = placementProblem(coordinates, zones, boundary, ignoreId) ?? (connectionFits(coordinates) ? null : 'Leave room for the entrance path.');
  if (!problem) return { coordinates, snapped: false, problem: null };
  if (coordinates.length < 3 || coordinates.some(p => !Number.isFinite(p[0] + p[1])))
    return { coordinates, snapped: false, problem };
  const origin = coordinates[0], east = metersPerDegLon(origin[1]);
  const local = (ring: number[][]): Point[] => ring.map(p => ({ x: (p[0] - origin[0]) * east, y: (p[1] - origin[1]) * METERS_PER_DEG_LAT }));
  const footprint = local(coordinates), border = boundary && local(boundary.coordinates);
  const obstacles = zones.filter(z => z.id !== ignoreId && ['building', 'residential', 'green_space', 'parking'].includes(z.zone_type)).map(z => local(z.coordinates));
  const axes = (ring: Point[]) => ring.map((p, i) => {
    const q = ring[(i + 1) % ring.length], size = Math.hypot(q.x - p.x, q.y - p.y);
    return size > .001 ? { x: -(q.y - p.y) / size, y: (q.x - p.x) / size } : null;
  }).filter((p): p is Point => p !== null);
  const project = (ring: Point[], axis: Point) => ring.map(p => p.x * axis.x + p.y * axis.y);
  const pending: Point[] = [{ x: 0, y: 0 }], seen = new Set<string>();
  // Plots already include separation around native models. A 2 cm numerical
  // margin keeps touching polygons from oscillating between valid/overlapping.
  const gap = .02, maxDistance = 30;
  for (let attempt = 0; pending.length && attempt < 64; attempt++) {
    pending.sort((a, b) => Math.hypot(a.x, a.y) - Math.hypot(b.x, b.y) || a.x - b.x || a.y - b.y);
    const offset = pending.shift()!;
    const ring = footprint.map(p => ({ x: p.x + offset.x, y: p.y + offset.y }));
    const hits = obstacles.filter(other => envelopesOverlap(ring, other));
    const outside = border && !envelopeFits(ring, border);
    if (!hits.length && !outside) {
      const result = coordinates.map(p => [p[0] + offset.x / east, p[1] + offset.y / METERS_PER_DEG_LAT]);
      if (!placementProblem(result, zones, boundary, ignoreId) && connectionFits(result)) return { coordinates: result, snapped: true, problem: null };
    }
    const add = (axis: Point, distance: number) => {
      const next = { x: offset.x + axis.x * distance, y: offset.y + axis.y * distance };
      const key = `${next.x.toFixed(3)},${next.y.toFixed(3)}`;
      if (Math.hypot(next.x, next.y) <= maxDistance && !seen.has(key)) { seen.add(key); pending.push(next); }
    };
    for (const obstacle of hits) for (const axis of [...axes(ring), ...axes(obstacle)]) {
      const a = project(ring, axis), b = project(obstacle, axis);
      add(axis, Math.max(...b) - Math.min(...a) + gap);
      add(axis, Math.min(...b) - Math.max(...a) - gap);
    }
    if (outside && border) for (const [i, axis] of axes(border).entries()) {
      const edge = border[i], plane = edge.x * axis.x + edge.y * axis.y, a = project(ring, axis);
      add(axis, plane - Math.min(...a) + gap);
      add(axis, plane - Math.max(...a) - gap);
    }
    // Check the whole frontier before expanding more intersections. Otherwise
    // two close rotated neighbours can keep producing shorter, still-blocked
    // candidates and starve an already available clear edge position.
    const clear = pending.filter(candidate => {
      const candidateRing = footprint.map(p => ({ x:p.x+candidate.x, y:p.y+candidate.y }));
      return (!border || envelopeFits(candidateRing,border)) && !obstacles.some(other=>envelopesOverlap(candidateRing,other))
        && connectionFits(coordinates.map(p=>[p[0]+candidate.x/east,p[1]+candidate.y/METERS_PER_DEG_LAT]));
    }).sort((a,b)=>Math.hypot(a.x,a.y)-Math.hypot(b.x,b.y))[0];
    if (clear) {
      const result=coordinates.map(p=>[p[0]+clear.x/east,p[1]+clear.y/METERS_PER_DEG_LAT]);
      if (!placementProblem(result,zones,boundary,ignoreId)) return {coordinates:result,snapped:true,problem:null};
    }
    // Retain nearest candidates only; crowded scenes cannot grow an open loop.
    if (pending.length > 256) {
      pending.sort((a, b) => Math.hypot(a.x, a.y) - Math.hypot(b.x, b.y));
      pending.length = 256;
    }
  }
  return { coordinates, snapped: false, problem: 'There isn’t room here yet. Try a little farther away or choose a smaller building.' };
}
