import type { SiteZone } from '@/types';
import { bufferLineToPolygon, extractRenderableStreetCenterline } from '@/utils/roadGeometry';
import { isFixedSectionStreet } from '@/features/pickPlace/streetPlacement';
import { resolvePilotStreetSectionProfile } from './streetSectionProfiles';

/** Clear only constructed bands. Transparent boundary setbacks must retain
 * their Google surface rather than becoming a narrow hole beside the street. */
export function streetSurfaceMaskZone(zone: SiteZone): SiteZone {
  if (!isFixedSectionStreet(zone)) return zone;
  const profile = resolvePilotStreetSectionProfile(zone);
  const line = extractRenderableStreetCenterline(zone);
  const bands = profile?.bands.filter(band => band.sourceType !== 'setback');
  if (!bands?.length || line.length < 2) return zone;
  const low = Math.min(...bands.map(band => band.startM)), high = Math.max(...bands.map(band => band.endM));
  // The four fixed sections have symmetric outer setback strips. Preserve
  // legacy ownership rather than invent an offset for an unsupported section.
  if (Math.abs(low + high) > 0.01) return zone;
  return {...zone, coordinates:bufferLineToPolygon(line,high-low)};
}
