import { resolveCommunity3DKind } from '@/features/community3d/community3d';
import type { SiteZone, SiteZoneProperties } from '@/types';
import type { LegoPlanRequest } from '@/features/legoAssembly/legoAssemblyApi';
import { CATALOGUE_ASSETS, isPlaceable, type PlaceAsset, type PlaceAssetId } from './assetRegistry';
import { canonicalParkById, canonicalParkForProperties } from './canonicalParkPlacement';
import { canonicalBuildingById, canonicalBuildingForProperties } from './canonicalBuildingPlacement';
import { reviewedEntranceForAsset } from './reviewedEntrances';
export type { PlaceAsset, PlaceAssetId } from './assetRegistry';
const OBJECT_ASSETS = CATALOGUE_ASSETS.filter((asset): asset is PlaceAsset => asset.kind === 'object');
export const PLACE_ASSETS = OBJECT_ASSETS.filter(isPlaceable);

/** Preview and saved compilation share the exact variant and native plot policy. */
export function placementPlanRequest(asset: PlaceAsset, width: number, depth: number, projectId?: string): LegoPlanRequest | null {
  if (asset.zoneType !== 'building' || asset.model.method === 'canonical_design') return null;
  return { target_width_m: width, target_depth_m: depth,
    target_floors: Number(asset.properties.floor_count),
    archetype_id: typeof asset.properties.development_selected_variant_id === 'string'
      ? asset.properties.development_selected_variant_id : undefined,
    native_home_plot: asset.properties.native_home_plot === true,
    allow_forced_fit: false, project_id: projectId };
}

export function placeAsset(id: PlaceAssetId): PlaceAsset {
  const asset = OBJECT_ASSETS.find(asset => asset.id === id) ?? canonicalBuildingById(id) ?? canonicalParkById(id);
  if (!asset) throw new Error(`Unknown placeable asset: ${id}`);
  return asset;
}
export function assetForZone(zone: Pick<SiteZone, 'properties'>): PlaceAsset | undefined {
  const properties = zone.properties ?? {};
  const native = OBJECT_ASSETS.find(asset => asset.id === properties.pick_place_asset);
  if (native?.reshapeMode === 'fixed_native' && properties.native_home_plot === true
    && ['infill_home', 'trial_postwar_bungalow'].includes(native.id)
    && properties.development_selected_variant_id === native.model.variantId && properties.development_height_override_m == null) {
    return { ...native, reshapeMode: 'repeat_native', properties: { ...native.properties, native_home_plot: true },
      ...(native.id === 'infill_home' ? { minDepth: 15 } : {}),
      reshapeDescription: 'This saved plot repeats complete homes at their native size.' };
  }
  if (native && properties.development_height_override_m == null && (!properties.development_selected_variant_id || native.model.variantId === properties.development_selected_variant_id)) return native;
  if (native || properties.pick_place_automatic_3d === true || String(properties.pick_place_asset).startsWith('canonical-building:') || String(properties.pick_place_asset).startsWith('canonical-park:')) {
    return canonicalBuildingForProperties(properties) ?? canonicalParkForProperties(properties);
  }
  return undefined;
}
export function placementProperties(asset: PlaceAsset, elevation?: number): SiteZoneProperties {
  const entrance = reviewedEntranceForAsset(asset);
  return { ...asset.properties, pick_place_asset: asset.id,
    pick_place_definition_version: asset.definitionVersion,
    ...(asset.model.revision ? { pick_place_model_revision: asset.model.revision } : {}),
    ...(entrance ? { pedestrian_building_entrance: {
      version: 1, automatic: true, sourceVariantId: asset.model.variantId,
      ...(asset.model.revision ? { sourceRevision: asset.model.revision } : {}), xM: entrance.xM, yM: entrance.yM,
      referenceWidthM: entrance.plotWidthM, referenceDepthM: entrance.plotDepthM,
      widthM: entrance.widthM, scaleWithPlot: false, streetId: '', heightAboveBaseM: 0,
      ...(entrance.fixedNative ? { fixedNative: true } : {}),
    } } : {}),
    ...(Number.isFinite(elevation) ? { terrain_elevation_m: elevation } : {}) };
}

/** Presentation guidance only; readiness still requires current compiled geometry. */
export function isCatalogueOnlyScene(zones: SiteZone[]): boolean {
  const physical = zones.filter(zone => resolveCommunity3DKind(zone) !== null);
  return physical.length > 0 && physical.every(zone => Boolean(assetForZone(zone)) || zone.properties?.pick_place_automatic_3d === true);
}
export const CATALOGUE_UPDATE_GUIDANCE = 'Your catalogue objects update in 3D automatically. Wait for “3D saved”, then try again. If an update failed, use “Retry 3D update” in the sidebar.';
