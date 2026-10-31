import type { SiteZone } from '@/types';
import type { PlaceAsset } from './assetRegistry';
import { hasBuildingOnlyFootprint } from './buildingOnlyFootprint';
import { rectangleAt,rectangleDimensions } from './geometry';

/** Explicit model replacement fits the new model atomically with its identity.
 * Ordinary reloads/height edits preserve a student's already-saved coordinates. */
export function buildingOnlySelectionCoordinates(zone:Pick<SiteZone,'coordinates'|'properties'>,asset:PlaceAsset):number[][] {
  if(!hasBuildingOnlyFootprint(asset) || (zone.properties?.pick_place_asset===asset.id
    && (!zone.properties?.pick_place_model_revision || zone.properties.pick_place_model_revision===asset.model.revision))) return zone.coordinates;
  const {center,degrees}=rectangleDimensions(zone.coordinates);
  return rectangleAt(center,asset.width,asset.depth,degrees);
}
