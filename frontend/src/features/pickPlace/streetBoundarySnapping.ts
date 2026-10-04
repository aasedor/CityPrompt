import type { SiteZone, SiteZoneProperties } from '@/types';
import { metersPerDegLon, METERS_PER_DEG_LAT, bufferLineToPolygon } from '@/components/viewer/mapEngine/geoUtils';
import { envelopeFits, pointInPark } from '@/components/viewer/globe/neighborhoodParkLayout';
import { roundAuthoredStreetRoute } from '@/utils/streetRouteCurves';
import { isSpecialistStreet } from '@/components/viewer/globe/specialistStreetProgram';
import { BRT_VARIANT } from '@/components/viewer/globe/brtStreetProgram';
import { TRAM_VARIANT } from '@/components/viewer/globe/tramStreetProgram';

const SNAP_DISTANCE_M = 6;
// Avoid inconsistent point-on-edge classification and projection round-off.
const INSET_M = .08;

/** Meet the parcel with a full-width, perpendicular end cap. Never clip the
 * model, relax containment, or infer a public road from satellite imagery. */
export function snapStreetToBoundary(points: number[][], width: number, boundary: SiteZone | null,
  properties: SiteZoneProperties): number[][] {
  if (!boundary || points.length < 2 || !(width > 0) || properties.connect_to_public_road === true) return points;
  const origin = points[0], sx = metersPerDegLon(origin[1]), sy = METERS_PER_DEG_LAT;
  const local = (p: number[]) => ({ x: (p[0] - origin[0]) * sx, y: (p[1] - origin[1]) * sy });
  const world = (p: { x: number; y: number }) => [origin[0] + p.x / sx, origin[1] + p.y / sy];
  const ring = boundary.coordinates.map(local);
  const variant = String(properties.road_selected_variant_id);
  const straightOnly = (isSpecialistStreet(variant) && variant !== 'amsterdam_gracht_v1') || [BRT_VARIANT, TRAM_VARIANT].includes(variant);
  let result = points.map(p => [...p]);
  // Work on the two endpoints only; interior waypoints remain authored.
  for (const reverse of [false, true]) {
    const route = reverse ? [...result].reverse() : [...result];
    const end = local(route[0]), next = local(route[1]);
    const candidates = ring.flatMap((a, i) => {
      const b = ring[(i + 1) % ring.length], dx = b.x - a.x, dy = b.y - a.y;
      const length = Math.hypot(dx, dy), margin = width / 2 + INSET_M;
      if (length < 2 * margin) return [];
      const ux = dx / length, uy = dy / length;
      const target = straightOnly ? next : end;
      const along = Math.max(margin, Math.min(length - margin, (target.x - a.x) * ux + (target.y - a.y) * uy));
      const edge = { x: a.x + along * ux, y: a.y + along * uy };
      const distance = Math.hypot(edge.x - end.x, edge.y - end.y);
      if (distance > SNAP_DISTANCE_M) return [];
      let nx = -uy, ny = ux;
      if (!pointInPark({ x: edge.x + nx * INSET_M, y: edge.y + ny * INSET_M }, ring)) { nx = -nx; ny = -ny; }
      const start = { x: edge.x + nx * INSET_M, y: edge.y + ny * INSET_M };
      if (!pointInPark(start, ring)) return [];
      const inward = (next.x - start.x) * nx + (next.y - start.y) * ny;
      const sideways = Math.abs((next.x - start.x) * ux + (next.y - start.y) * uy);
      if (inward < width) return [];
      // Straight approaches need no extra handle. Oblique approaches reserve a
      // full segment for the bend so the rounder retains a normal end cap.
      const approach = { x: start.x + nx * width * 1.25, y: start.y + ny * width * 1.25 };
      const needsBend = sideways > .01;
      if (straightOnly && needsBend) return [];
      if (needsBend && (inward < width * 2.25 || Math.hypot(next.x - approach.x, next.y - approach.y) < width)) return [];
      return [{ distance, route: [world(start), ...(needsBend ? [world(approach)] : []), ...route.slice(1)] }];
    }).sort((a, b) => a.distance - b.distance);
    if (candidates.length) result = reverse ? candidates[0].route.reverse() : candidates[0].route;
  }
  // The entire rounded street must fit, including concave parcel recesses.
  const footprint = bufferLineToPolygon(roundAuthoredStreetRoute(result, width, properties), width).map(local);
  return envelopeFits(footprint, ring) ? result : points;
}
