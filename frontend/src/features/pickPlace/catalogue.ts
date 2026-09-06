import type { SiteZone, SiteZoneProperties } from '@/types';
import type { LegoPlanRequest } from '@/features/legoAssembly/legoAssemblyApi';
import { CATALOGUE_ASSETS, isPlaceable, type PlaceAsset, type PlaceAssetId } from './assetRegistry';
export type { PlaceAsset, PlaceAssetId } from './assetRegistry';
const OBJECT_ASSETS = CATALOGUE_ASSETS.filter((asset): asset is PlaceAsset => asset.kind === 'object');
export const PLACE_ASSETS = OBJECT_ASSETS.filter(isPlaceable);

/** Preview and saved compilation share the exact variant and native plot policy. */
export function placementPlanRequest(asset: PlaceAsset, width: number, depth: number, projectId?: string): LegoPlanRequest | null {
  if (asset.zoneType !== 'building') return null;
  return { target_width_m: width, target_depth_m: depth,
    target_floors: Number(asset.properties.floor_count),
    archetype_id: typeof asset.properties.development_selected_variant_id === 'string'
      ? asset.properties.development_selected_variant_id : undefined,
    native_home_plot: asset.properties.native_home_plot === true,
    allow_forced_fit: false, project_id: projectId };
}

export function placeAsset(id: PlaceAssetId): PlaceAsset {
  const asset = OBJECT_ASSETS.find(asset => asset.id === id);
  if (!asset) throw new Error(`Unknown placeable asset: ${id}`);
  return asset;
}
export function assetForZone(zone: Pick<SiteZone, 'properties'>): PlaceAsset | undefined {
  return OBJECT_ASSETS.find(asset => asset.id === zone.properties?.pick_place_asset);
}
export function placementProperties(asset: PlaceAsset, elevation?: number): SiteZoneProperties {
  return { ...asset.properties, pick_place_asset: asset.id,
    pick_place_definition_version: asset.definitionVersion,
    ...(Number.isFinite(elevation) ? { terrain_elevation_m: elevation } : {}) };
}
