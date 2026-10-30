import type { SiteZone, SiteZoneProperties } from '@/types';
import { parkingLayout, type ParkingLayout } from './parkingLot';
import { pavingLocalPoints, pavingProblem } from './pavingSurfaces';
import { computeCentroid, metersPerDegLon, METERS_PER_DEG_LAT } from '@/components/viewer/mapEngine/geoUtils';

export type ParkingRowDirection = 'auto' | 'along' | 'across';
export const drawnParkingProperties = (): SiteZoneProperties => ({
  ground_surface_material: 'asphalt', parking_layout_version: 1, parking_row_direction: 'auto',
});
export const isDrawnParking = (zone: Pick<SiteZone, 'properties'>) =>
  zone.properties?.ground_surface_material === 'asphalt' && zone.properties?.parking_layout_version === 1;
export function parkingRowDirection(zone: Pick<SiteZone, 'properties'>): ParkingRowDirection {
  const direction = zone.properties?.parking_row_direction;
  return direction === 'along' || direction === 'across' ? direction : 'auto';
}

export function parkingOutlineProblem(coordinates: number[][]): string | null {
  const problem = pavingProblem(coordinates);
  if (problem) return problem;
  const local = pavingLocalPoints(coordinates);
  const area = Math.abs(local.reduce((sum, p, i) => {
    const q = local[(i + 1) % local.length]; return sum + p[0] * q[1] - p[1] * q[0];
  }, 0)) / 2;
  return area > 15000 || [0, 1].some(axis => Math.max(...local.map(p => p[axis])) - Math.min(...local.map(p => p[axis])) > 300)
    ? 'Split this into smaller parking lots (up to 15,000 m² and 300 m across).' : null;
}

/** Stable longest edge: reordering the same saved polygon must not change its paint. */
function rowOutline(outline: number[][]): number[][] {
  const ring = outline.slice();
  const last = ring[ring.length - 1];
  if (ring.length > 1 && ring[0][0] === last[0] && ring[0][1] === last[1]) ring.pop();
  if (ring.length < 3) return ring;
  const compare = (a: number[], b: number[]) => a[0] - b[0] || a[1] - b[1];
  const edges = ring.map((p, i) => {
    const q = ring[(i + 1) % ring.length];
    return { length: Math.hypot(q[0] - p[0], q[1] - p[1]), a: compare(p, q) < 0 ? p : q, b: compare(p, q) < 0 ? q : p };
  }).sort((a, b) => b.length - a.length || compare(a.a, b.a) || compare(a.b, b.b));
  const edge = edges[0];
  let start = ring.indexOf(edge.a);
  if (ring[(start + 1) % ring.length] !== edge.b) { ring.reverse(); start = ring.indexOf(edge.a); }
  return [...ring.slice(start), ...ring.slice(0, start)];
}

/** Same bounded metric layout as existing lots; only the choice of row direction is automatic. */
export function drawnParkingLayout(outline: number[][], direction: ParkingRowDirection = 'auto'): ParkingLayout {
  if (outline.length > 64 || outline.some(p => p.length !== 2 || !p.every(Number.isFinite)))
    return { spaces: [], aisles: [], problem: 'Use up to 64 valid parking corners.' };
  const ring = rowOutline(outline);
  let best = parkingLayout(ring, { version: 1, rowAngle: direction === 'across' ? 90 : 0 }, true);
  if (ring.length < 3 || best.problem?.includes('15,000')) return best;
  const edge = Math.atan2(ring[1][1] - ring[0][1], ring[1][0] - ring[0][0]);
  for (const rowAngle of direction === 'auto' ? [0, 90] : [direction === 'across' ? 90 : 0]) {
    const angle = edge + rowAngle * Math.PI / 180;
    const ys = ring.map(p => -(p[0] - ring[0][0]) * Math.sin(angle) + (p[1] - ring[0][1]) * Math.cos(angle));
    const depth = Math.max(...ys) - Math.min(...ys) - 1;
    // Try both boundary alignments of a full 17m module and an 11.5m single row.
    // Six bounded candidates at most; no per-frame or open-ended packing search.
    for (const offset of new Set([0, depth % 17, depth % 11.5].filter(n => n >= 0))) {
      const candidate = parkingLayout(ring, { version: 1, rowAngle }, true, offset);
      if (candidate.spaces.length > best.spaces.length) best = candidate;
    }
  }
  return best;
}

/** Shared render/panel frame: counts and visible paint use identical metre coordinates. */
export function drawnParkingZoneLayout(zone: Pick<SiteZone, 'coordinates' | 'properties'>): ParkingLayout {
  return drawnParkingLayout(parkingZoneOutline(zone), parkingRowDirection(zone));
}
export function parkingZoneOutline(zone: Pick<SiteZone, 'coordinates'>): number[][] {
  const origin = computeCentroid(zone.coordinates), east = metersPerDegLon(origin[1]);
  return zone.coordinates.map(p => [(p[0] - origin[0]) * east, (p[1] - origin[1]) * METERS_PER_DEG_LAT]);
}
