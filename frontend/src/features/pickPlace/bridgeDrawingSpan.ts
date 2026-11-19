import type { SiteZoneProperties } from '@/types';
import { metersPerDegLon, METERS_PER_DEG_LAT } from '@/components/viewer/mapEngine/geoUtils';
import { modularBridgeProgramFor } from '@/components/viewer/globe/modularBridgeProgram';

/** Drawing assistance only: retain the first anchor and bearing, and move an
 * approximate endpoint into the existing structural envelope. No asset or
 * validation limits change. Invalid/zero-length drafts still need direction. */
export function fitBridgeDrawingSpan(points: number[][], properties?: SiteZoneProperties | null): number[][] {
  const program = modularBridgeProgramFor(properties?.road_selected_variant_id);
  if (!program || points.length !== 2 || points.some(p => p.length < 2 || !p.slice(0, 2).every(Number.isFinite))) return points;
  const [start, end] = points;
  const deltaLng = end[0] - start[0];
  const deltaLat = end[1] - start[1];
  const anchorLongitudeScale = metersPerDegLon(start[1]);
  const north = deltaLat * METERS_PER_DEG_LAT;
  const length = Math.hypot(deltaLng * anchorLongitudeScale, north);
  if (Math.abs(anchorLongitudeScale) < 1e-6 || !Number.isFinite(length) || length < .3) return points;

  const { minLengthM, maxLengthM } = program;
  const withinSpan = (distance: number) => distance >= minLengthM && distance <= maxLengthM;
  // The save validator measures from the anchor. The 3D ribbon projects at
  // the midpoint latitude, so both lengths must fit the authored envelope.
  const renderedLength = (distance: number) => {
    const ratio = distance / length;
    const midpointLat = start[1] + deltaLat * ratio / 2;
    return Math.hypot(deltaLng * ratio * metersPerDegLon(midpointLat), north * ratio);
  };
  if (withinSpan(length) && withinSpan(renderedLength(length))) return points;

  const margin = Math.min(.001, (maxLengthM - minLengthM) / 4);
  let lower = minLengthM + margin;
  let upper = maxLengthM - margin;
  let fitted = Math.min(upper, Math.max(lower, length));
  const rendered = renderedLength(fitted);
  if (!withinSpan(rendered)) {
    const target = rendered < minLengthM ? lower : upper;
    for (let step = 0; step < 24; step++) {
      const distance = (lower + upper) / 2;
      if (renderedLength(distance) < target) lower = distance;
      else upper = distance;
    }
    fitted = (lower + upper) / 2;
  }

  const ratio = fitted / length;
  return [[...start], [start[0] + deltaLng * ratio, start[1] + deltaLat * ratio]];
}
