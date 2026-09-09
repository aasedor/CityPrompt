import type { Building, SiteZone } from '@/types';
import { getCommunity3DBuildingSourceZoneId } from '@/features/community3d/community3d';
import { assetForZone } from './catalogue';

/** Delete the authored catalogue object, not a replaceable compiled representation. */
export function catalogueZoneForBuilding(id: string, buildings: Building[], zones: SiteZone[]): SiteZone | undefined {
  const model = buildings.find(building => building.id === id);
  const owner = model ? getCommunity3DBuildingSourceZoneId(model) : null;
  return zones.find(zone => (zone.id === owner || zone.building_id === id || zone.building_ids?.includes(id))
    && (Boolean(assetForZone(zone)) || zone.properties?.pick_place_automatic_3d === true));
}
