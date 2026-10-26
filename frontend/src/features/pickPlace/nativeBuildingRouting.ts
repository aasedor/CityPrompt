import type { SiteZone } from '@/types';
import { nativeBuildingUrl } from './nativeBuildingContract';

/** Saved trial identities retain ownership even when their catalogue is absent
 * or their exact revision is unavailable. Never reveal their planned massing. */
export function isLocalTeachingBuilding(zone: Pick<SiteZone, 'properties'>): boolean {
  const id = zone.properties?.pick_place_asset;
  return typeof id === 'string' && id.startsWith('local_teaching_');
}

export function nativeBuildingRoutes<T extends { id: string }>(zones: SiteZone[], buildings: T[]) {
  const reviewZones = zones.filter(zone => ['building', 'residential', 'development_area'].includes(zone.zone_type)
    && (Boolean(nativeBuildingUrl(zone)) || isLocalTeachingBuilding(zone)));
  const buildingIds = new Set(reviewZones.flatMap(zone => [zone.building_id, ...(zone.building_ids ?? [])])
    .filter((id): id is string => typeof id === 'string' && id.length > 0));
  return { reviewZones, buildingIds,
    unavailableZones: reviewZones.filter(zone => !nativeBuildingUrl(zone)),
    otherBuildings: buildings.filter(building => !buildingIds.has(building.id)) };
}
