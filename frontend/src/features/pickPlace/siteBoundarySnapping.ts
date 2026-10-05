import type { SiteZone } from '@/types';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '@/components/viewer/mapEngine/geoUtils';
import { envelopeFits } from '@/components/viewer/globe/neighborhoodParkLayout';

export const SITE_BOUNDARY_SNAP_DISTANCE_M = 3;
const INSET_M = .08;
const CONTACT_TOLERANCE_M = .001;
type Point = { x: number; y: number };
type EdgeCorrection = Point & { shift: number };

/** Solve two edge constraints together, including non-square site corners. */
function cornerOffset(a: EdgeCorrection, b: EdgeCorrection): Point | null {
  const determinant = a.x * b.y - a.y * b.x;
  if (Math.abs(determinant) < .001) return null;
  return {
    x: (a.shift * b.y - a.y * b.shift) / determinant,
    y: (a.x * b.shift - a.shift * b.x) / determinant,
  };
}

/** Translate the complete saved footprint, never clip, shrink or rotate it.
 * Concave containment is checked on every candidate, including corner repairs. */
export function siteBoundarySnapCandidates(coordinates: number[][], boundary?: SiteZone | null) {
  if (!boundary || coordinates.length < 3 || boundary.coordinates.length < 3
    || [...coordinates, ...boundary.coordinates].some(p => p.length < 2 || !Number.isFinite(p[0] + p[1]))) return [];
  const origin = boundary.coordinates[0], east = metersPerDegLon(origin[1]);
  const local = (ring: number[][]): Point[] => ring.map(p => ({
    x: (p[0] - origin[0]) * east, y: (p[1] - origin[1]) * METERS_PER_DEG_LAT,
  }));
  const plot = local(coordinates), border = local(boundary.coordinates);
  const winding = Math.sign(border.reduce((sum, p, i) => {
    const q = border[(i + 1) % border.length];
    return sum + p.x * q.y - q.x * p.y;
  }, 0));
  if (!winding) return [];
  const corrections: EdgeCorrection[] = [], contacts: EdgeCorrection[] = [];
  for (let i = 0; i < border.length; i++) {
    const a = border[i], b = border[(i + 1) % border.length], size = Math.hypot(b.x - a.x, b.y - a.y);
    if (size < .01) continue;
    const tx = (b.x - a.x) / size, ty = (b.y - a.y) / size;
    const nx = -winding * ty, ny = winding * tx;
    const along = plot.map(p => (p.x - a.x) * tx + (p.y - a.y) * ty);
    if (Math.min(size, Math.max(...along)) - Math.max(0, Math.min(...along)) < .01) continue;
    const gap = Math.min(...plot.map(p => (p.x - a.x) * nx + (p.y - a.y) * ny));
    const shift = INSET_M - gap;
    if (Math.abs(shift) < CONTACT_TOLERANCE_M) {
      contacts.push({ x: nx, y: ny, shift: 0 });
    } else if (Math.abs(shift) <= SITE_BOUNDARY_SNAP_DISTANCE_M) {
      corrections.push({ x: nx, y: ny, shift });
    }
  }
  corrections.sort((a, b) => Math.abs(a.shift) - Math.abs(b.shift));
  const nearby = corrections.slice(0, 16), offsets: Point[] = [];
  for (const edge of nearby) {
    offsets.push({ x: edge.x * edge.shift, y: edge.y * edge.shift });
    // Preserve existing contact in narrow parcels and along oblique corners.
    for (const contact of contacts) {
      const offset = cornerOffset(edge, contact);
      if (offset) offsets.push(offset);
    }
  }
  // A small corner overhang may need both corrections before containment passes.
  for (let i = 0; i < nearby.length; i++) for (let j = i + 1; j < nearby.length; j++) {
    const offset = cornerOffset(nearby[i], nearby[j]);
    if (offset) offsets.push(offset);
  }
  return offsets.filter(offset => {
    const distance = Math.hypot(offset.x, offset.y);
    return distance >= CONTACT_TOLERANCE_M && distance <= SITE_BOUNDARY_SNAP_DISTANCE_M
      && contacts.every(axis => Math.abs(offset.x * axis.x + offset.y * axis.y) < CONTACT_TOLERANCE_M)
      && envelopeFits(plot.map(p => ({ x: p.x + offset.x, y: p.y + offset.y })), border);
  }).map(offset => ({
    distance: Math.hypot(offset.x, offset.y),
    coordinates: coordinates.map(p => [p[0] + offset.x / east, p[1] + offset.y / METERS_PER_DEG_LAT]),
  })).sort((a, b) => a.distance - b.distance);
}

export function snapFootprintToSiteBoundary(
  coordinates: number[][], boundary: SiteZone | null | undefined, isValid: (coords: number[][]) => boolean,
) {
  let result = coordinates;
  for (let pass = 0; pass < 2; pass++) {
    const candidate = siteBoundarySnapCandidates(result, boundary).find(row => isValid(row.coordinates));
    if (!candidate) break;
    result = candidate.coordinates;
  }
  return result;
}
