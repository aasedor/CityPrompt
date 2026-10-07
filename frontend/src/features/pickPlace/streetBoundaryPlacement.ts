import type { SiteZone, SiteZoneProperties } from '@/types';
import { bufferLineToPolygon, parsePersistedCenterline } from '@/utils/roadGeometry';
import { placementProblem } from './geometry';
import { snapFootprintToSiteBoundary } from './siteBoundarySnapping';
import { streetConnectionProblem } from './streetConnectionProblem';
import { streetEditConnectionCheck } from './streetEditConnections';
import { isFixedSectionStreet, streetSectionWidth } from './streetPlacement';

/** The coordinate-save pipeline samples editing controls itself. Passing an
 * already sampled boundary result back through it discards the small handle
 * array after a bend edit. Carry the translated controls to that pipeline. */
export function streetBoundaryEditCoordinates(zone: SiteZone, snapped: ReturnType<typeof snapStreetBoundaryPlacement>) {
  const controls = parsePersistedCenterline(snapped.properties.plan_route_controls);
  return isFixedSectionStreet(zone) && controls
    ? bufferLineToPolygon(controls, streetSectionWidth(zone)) : snapped.coordinates;
}

/** Carry the rigid shift into both route representations as one saved edit. */
function translatedProperties(properties: SiteZoneProperties, before: number[][], after: number[][]) {
  if (before === after) return properties;
  const dx = after[0][0] - before[0][0], dy = after[0][1] - before[0][1];
  const result = { ...properties };
  for (const key of ['plan_centerline', 'plan_route_controls'] as const) {
    const line = parsePersistedCenterline(properties[key]);
    if (line) result[key] = line.map(p => [p[0] + dx, p[1] + dy]);
  }
  return result;
}

export function snapStreetBoundaryPlacement(zone: SiteZone, zones: SiteZone[], boundary?: SiteZone | null) {
  const properties = zone.properties ?? {};
  // Explicit public-road extensions keep their existing dedicated validator.
  if (!boundary || properties.connect_to_public_road === true) {
    return { coordinates: zone.coordinates, properties, problem: null };
  }
  const context = zones.filter(row => row.id !== zone.id);
  const original = zones.find(row => row.id === zone.id) ?? zone;
  const connected = streetEditConnectionCheck(original, [...context, original]);
  const candidate = (coordinates: number[][]) => ({
    ...zone, coordinates, properties: translatedProperties(properties, zone.coordinates, coordinates),
  });
  const problem = (next: SiteZone) => placementProblem(next.coordinates, context, boundary, zone.id, { allowStreetIntersections: true })
    ?? streetConnectionProblem(next, context)
    ?? (connected(next) ? null : 'Keep the existing street junction connected.');
  const coordinates = snapFootprintToSiteBoundary(zone.coordinates, boundary, coords => !problem(candidate(coords)));
  const result = candidate(coordinates);
  return { coordinates: result.coordinates, properties: result.properties, problem: problem(result) };
}
