import type { SiteZone } from '@/types';
import { detectConnectedStreetIntersections } from '@/components/viewer/globe/streetGraphIntersections';
import { resolveStreetJunctionLayout } from '@/components/viewer/globe/streetJunctionGeometry';
import { bufferLineToPolygon, extractCenterline, extractZoneCenterline, parsePersistedCenterline } from '@/utils/roadGeometry';
import { streetCoordinateUpdate, streetSectionWidth } from './streetPlacement';

/** Preserve working junctions, including their full sidewalk/road patch. A
 * touching street polygon alone is not evidence of a usable intersection. */
export function streetEditConnectionCheck(zone: SiteZone, zones: SiteZone[]) {
  const required = detectConnectedStreetIntersections(zones).filter(node =>
    node.zoneIds.includes(zone.id) && resolveStreetJunctionLayout(node, zones));
  return (candidate: SiteZone) => {
    if (!required.length) return true;
    const next = zones.map(item => item.id === zone.id ? candidate : item);
    const available = detectConnectedStreetIntersections(next).filter(node =>
      node.zoneIds.includes(zone.id) && resolveStreetJunctionLayout(node, next));
    // Consume matches: two crossings of the same streets need two patches.
    return required.every(before => {
      const index = available.findIndex(after => after.armCount === before.armCount
        && after.zoneIds.length === before.zoneIds.length
        && before.zoneIds.every(id => after.zoneIds.includes(id)));
      if (index < 0) return false;
      available.splice(index, 1);
      return true;
    });
  };
}

/** Clamp a move/bend to a nearby connected position. Only the edited street
 * moves; neighbouring authored routes and geometry tolerances stay unchanged. */
export function snapConnectedStreetEdit(zone: SiteZone, coordinates: number[][], zones: SiteZone[]) {
  const fits = streetEditConnectionCheck(zone, zones);
  const candidate = (coords: number[][]) => ({ ...zone, ...streetCoordinateUpdate(zone, coords) });
  if (fits(candidate(coordinates))) return coordinates;
  const target = extractCenterline(coordinates);
  const controls = parsePersistedCenterline(zone.properties?.plan_route_controls);
  const before = controls?.length === target.length ? controls : extractZoneCenterline(zone);
  if (before.length !== target.length) return zone.coordinates;
  let low = 0, high = 1, result = zone.coordinates;
  // A finite bisection keeps the preview near the student's gesture while
  // holding its last connected state when no movement is possible.
  for (let step = 0; step < 8; step++) {
    const t = (low + high) / 2;
    const line = before.map((point, i) => point.map((value, axis) =>
      value + (target[i][axis] - value) * t));
    const proposed = bufferLineToPolygon(line, streetSectionWidth(zone));
    if (fits(candidate(proposed))) { low = t; result = proposed; }
    else high = t;
  }
  return result;
}
