import type { SiteZone, SiteZoneProperties } from '@/types';
import { classifyCalgaryAsset, type CalgaryClassification } from '@/features/calgaryCatalogue/guide';

export type PlaceAssetId = 'infill_home' | 'neighbourhood_park';
export interface PlaceAsset {
  id: PlaceAssetId;
  label: string;
  description: string;
  thumbnail: string;
  zoneType: 'building' | 'green_space';
  width: number;
  depth: number;
  minWidth: number;
  minDepth: number;
  maxSize: number;
  properties: SiteZoneProperties;
  calgaryGuide: CalgaryClassification;
}

// Reuse catalogue identities; this pilot does not promote new RLASM families.
export const PLACE_ASSETS: PlaceAsset[] = [
  {
    id: 'infill_home', label: 'Infill homes',
    calgaryGuide: classifyCalgaryAsset('building', { id: 'calgary_modern_infill_house', developmentType: 'residential_single_family' }),
    description: 'Two-storey homes. Widen the plot to fit more.',
    thumbnail: '/archetypes/buildings/calgary-modern-infill-house/variant_0.png',
    zoneType: 'building', width: 12, depth: 16, minWidth: 12, minDepth: 15, maxSize: 100,
    properties: { building_archetype_id: 'calgary_modern_infill_house',
      development_archetype_id: 'calgary_modern_infill_house',
      development_selected_variant_id: 'infill_flat_roof_minimal', native_home_plot: true,
      development_archetype_label: 'Calgary infill homes', floors: 2, floor_count: 2 },
  },
  {
    id: 'neighbourhood_park', label: 'Neighbourhood park',
    calgaryGuide: classifyCalgaryAsset('park_plaza', { id: 'neighborhood_park' }),
    description: 'Paths, trees and play spaces adapt to your area.',
    thumbnail: '/archetypes/openspaces/neighborhood-park/variant_0.png',
    zoneType: 'green_space', width: 40, depth: 35, minWidth: 30, minDepth: 30, maxSize: 110,
    properties: { green_space_archetype_id: 'neighborhood_park',
      green_space_selected_variant_id: 'neighborhood_park_v0',
      neighborhood_park_layout: 'adaptive_rustic_v1' },
  },
];

export function placeAsset(id: PlaceAssetId): PlaceAsset {
  return PLACE_ASSETS.find(asset => asset.id === id)!;
}
export function assetForZone(zone: SiteZone): PlaceAsset | undefined {
  return PLACE_ASSETS.find(asset => asset.id === zone.properties?.pick_place_asset);
}
export function placementProperties(asset: PlaceAsset, elevation?: number): SiteZoneProperties {
  return { ...asset.properties, pick_place_asset: asset.id,
    ...(Number.isFinite(elevation) ? { terrain_elevation_m: elevation } : {}) };
}
