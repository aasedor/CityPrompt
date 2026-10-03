import type { SiteZone, SiteZoneProperties } from '@/types';
import { bufferLineToPolygon, metersPerDegLon, METERS_PER_DEG_LAT } from '@/components/viewer/mapEngine/geoUtils';
import { envelopesOverlap, pointInPark } from '@/components/viewer/globe/neighborhoodParkLayout';
import { roundAuthoredStreetRoute } from '@/utils/streetRouteCurves';
import { isSpecialistStreet } from '@/components/viewer/globe/specialistStreetProgram';
import { BRT_VARIANT } from '@/components/viewer/globe/brtStreetProgram';
import { TRAM_VARIANT } from '@/components/viewer/globe/tramStreetProgram';
import { publicRoadConnectionFits } from './publicRoadConnection';
import { placementProblem } from './geometry';
import { streetRouteProblem } from './streetPlacement';

export interface PublicRoad { id: string; label: string; points: number[][]; widthM: number }
export interface PublicRoadContext { source: string; fetched_at: string; roads: PublicRoad[]; blockers: number[][][] }
export interface PublicRoadSuggestion { road: PublicRoad; endpoint: number[]; edge: number[][]; end: 'start' | 'finish' }

export function supportsPublicRoadSuggestions(properties: SiteZoneProperties) {
  const variant = String(properties.road_selected_variant_id);
  return Number(properties.width) >= 3 && Number(properties.width) <= 30 && properties.lane_count !== 0
    && !isSpecialistStreet(variant) && ![BRT_VARIANT, TRAM_VARIANT].includes(variant);
}

/** One proposed connection, chosen from mapped eligible surface streets only.
 * The road centreline/width estimate is never treated as a surveyed kerb. */
export function suggestPublicRoad(points: number[][], properties: SiteZoneProperties, zones: SiteZone[],
  boundary: SiteZone | null, context?: PublicRoadContext) {
  if (!context || !boundary || points.length < 2 || !supportsPublicRoadSuggestions(properties)
    || properties.connect_to_public_road === true) return null;
  const width = Number(properties.width), origin = points[0], sx = metersPerDegLon(origin[1]), sy = METERS_PER_DEG_LAT;
  const local = (p: number[]) => ({ x: (p[0] - origin[0]) * sx, y: (p[1] - origin[1]) * sy });
  const world = (x: number, y: number) => [origin[0] + x / sx, origin[1] + y / sy];
  const ring = boundary.coordinates.map(local);
  const candidates: { distance: number; controls: number[][]; suggestion: PublicRoadSuggestion }[] = [];
  for (const reverse of [false, true]) {
    const route = reverse ? [...points].reverse() : points;
    const end = local(route[0]), next = local(route[1]);
    for (const road of context.roads) for (let i = 1; i < road.points.length; i++) {
      const a = local(road.points[i - 1]), b = local(road.points[i]);
      const dx = b.x - a.x, dy = b.y - a.y, length = Math.hypot(dx, dy);
      if (length < width + 2 || !Number.isFinite(length) || !(road.widthM >= 3 && road.widthM <= 20)) continue;
      const ux = dx / length, uy = dy / length;
      const along = (end.x - a.x) * ux + (end.y - a.y) * uy;
      // Avoid junctions and sharp target-road bends; do not jump to a segment endpoint.
      if (along < width / 2 + 1 || along > length - width / 2 - 1) continue;
      const q = { x: a.x + along * ux, y: a.y + along * uy };
      const sign = ((next.x - q.x) * -uy + (next.y - q.y) * ux) >= 0 ? 1 : -1;
      const nx = -uy * sign, ny = ux * sign;
      const target = { x: q.x + nx * road.widthM / 2, y: q.y + ny * road.widthM / 2 };
      const distance = Math.hypot(end.x - target.x, end.y - target.y);
      if (distance > 10 || pointInPark(target, ring)) continue;
      const inward = (next.x - target.x) * nx + (next.y - target.y) * ny;
      if (inward < width) continue;
      const sideways = Math.abs((next.x - target.x) * ux + (next.y - target.y) * uy);
      const approach = { x: target.x + nx * width * 1.25, y: target.y + ny * width * 1.25 };
      const bend = sideways > .01;
      if (bend && (inward < width * 2.25 || Math.hypot(next.x - approach.x, next.y - approach.y) < width)) continue;
      const controls = [world(target.x, target.y), ...(bend ? [world(approach.x, approach.y)] : []), ...route.slice(1)];
      if (reverse) controls.reverse();
      candidates.push({ distance, controls, suggestion: { road, endpoint: world(target.x, target.y), end: reverse ? 'finish' : 'start',
        edge: [-1, 1].map(s => world(target.x + s * ux * (width / 2 + 3), target.y + s * uy * (width / 2 + 3))) } });
    }
  }
  candidates.sort((a, b) => a.distance - b.distance || a.suggestion.road.id.localeCompare(b.suggestion.road.id));
  for (const candidate of candidates) {
    const centerline = roundAuthoredStreetRoute(candidate.controls, width, properties);
    const coordinates = bufferLineToPolygon(centerline, width);
    const nextProperties = { ...properties, connect_to_public_road: true, plan_centerline: centerline, plan_route_controls: candidate.controls,
      road_public_target: { id: candidate.suggestion.road.id, label: candidate.suggestion.road.label,
        source: context.source, estimated_edge: true, endpoint: candidate.suggestion.endpoint, end: candidate.suggestion.end } };
    if (!publicRoadConnectionFits({ zone_type: 'road', properties: nextProperties }, coordinates, boundary)
      || streetRouteProblem(coordinates, width, candidate.controls)
      || placementProblem(coordinates, zones, null, undefined, { allowStreetIntersections: true })) continue;
    const footprint = coordinates.map(local);
    if (context.blockers.some(blocker => envelopesOverlap(footprint, blocker.map(local)))) continue;
    return { coordinates, properties: nextProperties, suggestion: candidate.suggestion };
  }
  return null;
}
