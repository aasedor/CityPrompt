import type { SiteZone } from '@/types';
import { getActiveSiteBoundary } from '@/utils/siteBoundary';
import { publicRoadConnectionFits } from '@/features/pickPlace/publicRoadConnection';
import { streetSectionOwnsGround, streetSurfaceMaskZone } from './streetSurfaceMask';

/** A whole-site cut does not cover a public-road extension. Keep the exact
 * constructed bands clear outside it too; never clear an unrelated road or
 * transparent setback. The same footprints open the site's retaining face. */
export function preparedPublicRoadMasks(zones: SiteZone[]): SiteZone[] {
  const boundary = getActiveSiteBoundary(zones);
  if (!boundary || boundary.properties?.community_3d_mask_existing_tiles === false) return [];
  return zones.filter(zone => zone.properties?.community_3d_mask_existing_tiles !== false
    && streetSectionOwnsGround(zone)
    && publicRoadConnectionFits(zone, zone.coordinates, boundary)).map(streetSurfaceMaskZone);
}
