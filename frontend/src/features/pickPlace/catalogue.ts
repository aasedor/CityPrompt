import type { SiteZone, SiteZoneProperties } from '@/types';
import { classifyCalgaryAsset, type CalgaryClassification } from '@/features/calgaryCatalogue/guide';
import type { LegoPlanRequest } from '@/features/legoAssembly/legoAssemblyApi';

export type PlaceAssetId = 'infill_home' | 'craftsman_bungalow' | 'neighbourhood_park';
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
  nativeDimensions?: [number, number, number];
  reshapeDescription: string;
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
    nativeDimensions: [8.45, 11.75, 6.98001],
    reshapeDescription: 'Homes stay two storeys and retain their proportions. A larger plot fits additional whole homes with space between them.',
    properties: { building_archetype_id: 'calgary_modern_infill_house',
      development_archetype_id: 'calgary_modern_infill_house',
      development_selected_variant_id: 'infill_flat_roof_minimal', native_home_plot: true,
      development_archetype_label: 'Calgary infill homes', floors: 2, floor_count: 2 },
  },
  {
    id: 'craftsman_bungalow', label: 'Craftsman bungalows',
    calgaryGuide: classifyCalgaryAsset('building', { id: 'vancouver_craftsman_bungalow', developmentType: 'residential_single_family' }),
    description: 'Gabled homes with porches. A deeper plot preserves their shape.',
    thumbnail: '/archetypes/buildings/vancouver-craftsman-bungalow/variant_0.png',
    // Complete reviewed GLB envelope, including roof and porch projections,
    // plus at least 1.5 m conceptual clearance on each edge (not a zoning claim).
    zoneType: 'building', width: 15, depth: 24, minWidth: 15, minDepth: 24, maxSize: 100,
    nativeDimensions: [11.84718, 20.69, 8.72],
    reshapeDescription: 'Bungalows keep their authored roof, porch and proportions. A larger plot fits additional whole bungalows with space between them.',
    properties: { building_archetype_id: 'vancouver_craftsman_bungalow',
      development_archetype_id: 'vancouver_craftsman_bungalow',
      development_selected_variant_id: 'craftsman_classic', native_home_plot: true,
      development_archetype_label: 'Craftsman bungalows', floors: 1, floor_count: 1 },
  },
  {
    id: 'neighbourhood_park', label: 'Neighbourhood park',
    calgaryGuide: classifyCalgaryAsset('park_plaza', { id: 'neighborhood_park' }),
    description: 'Paths, trees and play spaces adapt to your area.',
    thumbnail: '/archetypes/openspaces/neighborhood-park/variant_0.png',
    zoneType: 'green_space', width: 40, depth: 35, minWidth: 30, minDepth: 30, maxSize: 110,
    reshapeDescription: 'Play equipment keeps its real size. The park rearranges paths, trees and activity areas to fit.',
    properties: { green_space_archetype_id: 'neighborhood_park',
      green_space_selected_variant_id: 'neighborhood_park_v0',
      neighborhood_park_layout: 'adaptive_rustic_v1' },
  },
];

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
  return PLACE_ASSETS.find(asset => asset.id === id)!;
}
export function assetForZone(zone: SiteZone): PlaceAsset | undefined {
  return PLACE_ASSETS.find(asset => asset.id === zone.properties?.pick_place_asset);
}
export function placementProperties(asset: PlaceAsset, elevation?: number): SiteZoneProperties {
  return { ...asset.properties, pick_place_asset: asset.id,
    ...(Number.isFinite(elevation) ? { terrain_elevation_m: elevation } : {}) };
}
