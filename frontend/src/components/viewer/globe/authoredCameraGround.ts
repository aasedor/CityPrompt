import { readNativePark, nativeParkFitProblem } from '@/features/parks/nativeParkRegistry';
import { nativePavingProbe } from '@/features/parks/nativeParkAccess';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '../mapEngine/geoUtils';
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
    const native = readNativePark(zone);
    if (native && !nativeParkFitProblem(zone)) {
      const level = resolvePreparedSiteTerrainForZone(zone, zones, measured);
      if (level !== null) {
        const f = native.selection.frame, c = Math.cos(f.yaw), s = Math.sin(f.yaw);
        const x = (lng - f.longitude) * metersPerDegLon(f.latitude), y = (lat - f.latitude) * METERS_PER_DEG_LAT;
        const local: [number,number] = [x*c + y*s, -x*s + y*c];
        if (Math.abs(local[0]) <= native.layout.widthM/2 && Math.abs(local[1]) <= native.layout.depthM/2) {
          try {
            const height = nativePavingProbe(native.layout, true)(local);
            if (height !== null) return level + height;
          } catch {
            // Loading/errors remain owned by NativeParkLayer and its capture guard.
            // Walking can retain site ground while the verified model loads.
          }
        }
      }
    }
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
