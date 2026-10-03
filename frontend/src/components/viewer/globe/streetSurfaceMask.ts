import type { SiteZone } from '@/types';
import { bufferLineToPolygon, extractRenderableStreetCenterline } from '@/utils/roadGeometry';
import { isFixedSectionStreet } from '@/features/pickPlace/streetPlacement';
import { resolvePilotStreetSectionProfile } from './streetSectionProfiles';

/** Detailed bands own the ground for catalogue sections, including streets
 * wholly inside the site. A second flat zone slab can bury their sidewalks
 * when the tile level changes with the camera. */
export function streetSectionOwnsGround(zone: SiteZone): boolean {
  return zone.coordinates.length >= 4 && (isFixedSectionStreet(zone) || zone.properties?.connect_to_public_road === true)
    && Boolean(resolvePilotStreetSectionProfile(zone)) && extractRenderableStreetCenterline(zone).length >= 2;
}

/** Clear only constructed bands. Transparent boundary setbacks must retain
 * their Google surface rather than becoming a narrow hole beside the street. */
export function streetSurfaceMaskZone(zone: SiteZone): SiteZone {
  if (!isFixedSectionStreet(zone)) return zone;
  const profile = resolvePilotStreetSectionProfile(zone);
  const line = extractRenderableStreetCenterline(zone);
  const bands = profile?.bands.filter(band => band.sourceType !== 'setback');
  if (!bands?.length || line.length < 2) return zone;
  const low = Math.min(...bands.map(band => band.startM)), high = Math.max(...bands.map(band => band.endM));
  // Take the two independently offset edges from the same bounded-miter
  // algorithm as the saved route. Asymmetric utility strips remain unmasked.
  const positive = bufferLineToPolygon(line, Math.abs(high) * 2).slice(0, line.length);
  const negative = bufferLineToPolygon(line, Math.abs(low) * 2).slice(line.length);
  return {...zone, coordinates:[...positive, ...negative]};
}
