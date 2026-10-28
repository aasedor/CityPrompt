import type { SiteZone } from '@/types';
import { nativeStreetPilotForZone } from './nativeStreetPilot';
import { resolvePilotStreetSectionProfile } from './streetSectionProfiles';

/** Below 30 degrees the junction becomes a merge with a long overlap. */
export const MIN_STREET_JUNCTION_ANGLE = Math.PI / 6;
export const MIN_STREET_JUNCTION_SINE = Math.sin(MIN_STREET_JUNCTION_ANGLE);
// Local longitude scales vary slightly along a route; this is under 0.006°.
export const STREET_JUNCTION_ANGLE_EPSILON = 1e-4;

/** Only authored, flush, car-free sections can use a continuous paved join
 * around bends. Motor streets retain their carriageways, curbs and crossings. */
export function isFlushPedestrianStreet(zone: SiteZone, preview = false): boolean {
  if (!nativeStreetPilotForZone(zone, preview)?.program) return false;
  const profile = resolvePilotStreetSectionProfile(zone);
  return Boolean(profile && !profile.renderCurbs
    && profile.bands.some(band => band.kind === 'path' || band.kind === 'sidewalk')
    && !profile.bands.some(band => band.kind === 'motor' || band.kind === 'parking'));
}
