import type { SiteZoneProperties } from '@/types';
import { metersPerDegLon, METERS_PER_DEG_LAT } from '@/components/viewer/mapEngine/geoUtils';
import { modularBridgeProgramFor } from '@/components/viewer/globe/modularBridgeProgram';

/** Drawing assistance only: retain the first anchor and bearing, and move an
 * approximate endpoint into the existing structural envelope. No asset or
 * validation limits change. Invalid/zero-length drafts still need direction. */
export function fitBridgeDrawingSpan(points: number[][], properties?: SiteZoneProperties | null): number[][] {
  const program = modularBridgeProgramFor(properties?.road_selected_variant_id);
  if (!program || points.length !== 2 || points.some(p => p.length < 2 || !p.slice(0, 2).every(Number.isFinite))) return points;
  const [a, b] = points, sx = metersPerDegLon(a[1]);
  if (Math.abs(sx) < 1e-6) return points;
  const dx = (b[0] - a[0]) * sx, dy = (b[1] - a[1]) * METERS_PER_DEG_LAT, length = Math.hypot(dx, dy);
  if (length < .3 || (length >= program.minLengthM && length <= program.maxLengthM)) return points;
  // A millimetre inside the limit absorbs geographic conversion round-off
  // without weakening the strict native source-span validator.
  const margin = Math.min(.001, (program.maxLengthM - program.minLengthM) / 4);
  const fitted = length < program.minLengthM ? program.minLengthM + margin : program.maxLengthM - margin;
  return [[...a], [a[0] + dx * fitted / length / sx, a[1] + dy * fitted / length / METERS_PER_DEG_LAT]];
}
