import type { SiteZone } from '@/types';
import { getActiveSiteBoundary } from '@/utils/siteBoundary';
import { readParkTerrain } from './parkTerrain';
import { sampleSharedSiteGround, sharedSiteGroundContains } from './sharedSiteGround';
import { resolvePreparedSiteTerrainForZone } from './sitePreparationSurface';
import { terraceOffset } from './terraceDefinition';

/** Camera feet belong on the authored ground, not the Google mesh hidden
 * underneath it. Unprepared landscape and off-site context keep their hit. */
export function authoredCameraGround(zones: SiteZone[], lng: number, lat: number, measured: number): number {
  const contains = (zone: SiteZone) => sharedSiteGroundContains(zone.coordinates as [number, number][], lng, lat);
  for (const zone of zones.filter(contains)) {
    const parkHeight = sampleSharedSiteGround(readParkTerrain(zone), lng, lat);
    if (parkHeight !== null) return parkHeight;
    if (terraceOffset(zone) !== null) {
      const level = resolvePreparedSiteTerrainForZone(zone, zones, measured);
      if (level !== null) return level;
    }
  }
  const boundary = getActiveSiteBoundary(zones);
  if (!boundary || !contains(boundary) || boundary.properties?.terrain_strategy === 'landscape') return measured;
  return resolvePreparedSiteTerrainForZone(boundary, zones, measured) ?? measured;
}
