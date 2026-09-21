import { PARK_TRIO_ASSETS } from './parkTrioAssets';
import type { SiteZoneProperties } from '@/types';
import { PUBLISHED_BUILDING_ASSETS } from './publishedBuildingAssets';
import streetCatalogue from '@/data/streetPathArchetypes.json';
import { classifyCalgaryAsset, calgaryGroup, CALGARY_GROUPS, type CalgaryClassification } from '@/features/calgaryCatalogue/guide';

export type PlaceAssetId = string;
export type AssetReadiness = 'candidate' | 'pilot' | 'ready' | 'retired';
interface AssetRecord {
  /** Stable saved identity. Never reuse an ID for a different design. */
  id: string;
  definitionVersion: number;
  label: string;
  description: string;
  thumbnail: string;
  readiness: AssetReadiness;
  model: { variantId: string; revision: string | null; method: string };
  calgaryGuide: CalgaryClassification;
  properties: SiteZoneProperties;
}
export interface PlaceAsset extends AssetRecord {
  kind: 'object';
  zoneType: 'building' | 'green_space';
  reshapeMode: 'repeat_native' | 'adaptive_layout' | 'fixed_native' | 'authored_footprint';
  width: number;
  depth: number;
  minWidth: number;
  minDepth: number;
  maxSize: number;
  nativeDimensions?: [number, number, number];
  /** Reviewed native step foot, in the plot frame. Register per exact variant,
   * never infer a doorway from a generic bounding box. */
  entranceSnap?: { xM: number; yM: number; plotWidthM: number; plotDepthM: number; widthM: number };
  reshapeDescription: string;
}
export interface StreetAsset extends AssetRecord {
  kind: 'street';
  reshapeMode: 'fixed_section_route';
  sectionWidth: number;
}
export type CatalogueAsset = PlaceAsset | StreetAsset;

const OBJECT_ASSETS: PlaceAsset[] = [
  {
    id: 'infill_home', kind: 'object', definitionVersion: 1, readiness: 'pilot', reshapeMode: 'repeat_native', model: { variantId: 'infill_flat_roof_minimal', revision: null, method: 'RLASM 6.1' }, label: 'Infill homes',
    calgaryGuide: classifyCalgaryAsset('building', { id: 'calgary_modern_infill_house', developmentType: 'residential_single_family' }),
    description: 'Two-storey homes. Widen the plot to fit more.',
    thumbnail: '/archetypes/buildings/calgary-modern-infill-house/variant_0.png',
    zoneType: 'building', width: 12, depth: 16, minWidth: 12, minDepth: 15, maxSize: 100,
    nativeDimensions: [8.45, 11.75, 6.98001],
    entranceSnap: { xM: 3.2, yM: -5.9, plotWidthM: 12, plotDepthM: 16, widthM: 1.8 },
    reshapeDescription: 'Homes stay two storeys and retain their proportions. A larger plot fits additional whole homes with space between them.',
    properties: { building_archetype_id: 'calgary_modern_infill_house',
      development_archetype_id: 'calgary_modern_infill_house',
      development_selected_variant_id: 'infill_flat_roof_minimal', native_home_plot: true,
      development_archetype_label: 'Calgary infill homes', floors: 2, floor_count: 2 },
  },
  {
    id: 'craftsman_bungalow', kind: 'object', definitionVersion: 1, readiness: 'pilot', reshapeMode: 'repeat_native', model: { variantId: 'craftsman_classic', revision: null, method: 'RLASM 6.1' }, label: 'Craftsman bungalows',
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
    id: 'neighbourhood_park', kind: 'object', definitionVersion: 1, readiness: 'pilot', reshapeMode: 'adaptive_layout', model: { variantId: 'neighborhood_park_v0', revision: 'neighborhood-rustic-v5', method: 'adaptive_rustic_v1' }, label: 'Neighbourhood park',
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

const streetSource = streetCatalogue.archetypes.find(entry => entry.id === 'calgary_local')!;
export const LOCAL_STREET_ASSET: StreetAsset = {
  id: 'calgary_local_street', kind: 'street', definitionVersion: 1,
  label: 'Calgary local street', description: '16 m wide · sidewalks and tree boulevards',
  thumbnail: '/archetypes/streets/calgary-local/variant_0.png',
  readiness: 'pilot', reshapeMode: 'fixed_section_route',
  model: { variantId: 'calgary_local_v0', revision: 'draft-4.0-figure-2', method: 'metric_street_section' },
  sectionWidth: streetSource.section!.row_m,
  calgaryGuide: { groupId: 'local', basis: 'draft_manual' },
  properties: {
    ...streetSource.propertyPresets,
    road_archetype_id: streetSource.id,
    road_selected_variant_id: 'calgary_local_v0',
    pick_place_street_section: 'calgary_local_v0',
    pick_place_automatic_3d: true,
    community_3d_mask_existing_tiles: true,
    pick_place_definition_version: 1,
    road_standard_citation: 'Street Manual Draft 4.0, Figure 2',
  },
};

/** Bounded placement release. Widths come from the existing metric catalogue;
 * the section viewer and 3D renderer resolve the same source profiles. */
function additionalStreet(archetypeId: string, label: string, description: string,
  calgaryGuide: CalgaryClassification): StreetAsset {
  const source = streetCatalogue.archetypes.find(entry => entry.id === archetypeId)!;
  const variantId = `${archetypeId}_v0`;
  return {
    id: `${archetypeId}_street`, kind: 'street', definitionVersion: 1,
    label, description, readiness: 'pilot', reshapeMode: 'fixed_section_route',
    thumbnail: `/archetypes/streets/${archetypeId.replace(/_/g, '-')}/variant_0.png`,
    sectionWidth: source.propertyPresets.width!, calgaryGuide,
    model: { variantId, revision: archetypeId === 'calgary_collector' ? 'draft-4.0-figure-6' : 'representative-section-v1', method: 'metric_street_section' },
    properties: {
      ...source.propertyPresets, road_archetype_id: archetypeId,
      road_selected_variant_id: variantId, pick_place_street_section: variantId,
      pick_place_automatic_3d: true, pick_place_definition_version: 1,
      community_3d_mask_existing_tiles: true,
      road_standard_citation: archetypeId === 'calgary_collector'
        ? 'Street Manual Draft 4.0, Figure 6' : 'City Prompt representative teaching section',
    },
  };
}

export const STREET_ASSETS: StreetAsset[] = [LOCAL_STREET_ASSET,
  additionalStreet('green_alley', 'Planted laneway', '5 m wide · 3.5 m shared lane with planted edges', { groupId: 'alley', basis: 'form_reference' }),
  additionalStreet('yield_street', 'Shared street', '6 m wide · 5.4 m shared surface with flush edges', { groupId: 'local', basis: 'form_reference' }),
  additionalStreet('calgary_collector', 'Calgary collector', '20 m wide · two lanes, pathway, sidewalk and boulevards', { groupId: 'collector', basis: 'draft_manual' }),
];

export const CATALOGUE_ASSETS: CatalogueAsset[] = [...OBJECT_ASSETS, ...STREET_ASSETS,
  ...PUBLISHED_BUILDING_ASSETS,
  ...PARK_TRIO_ASSETS];
/** Pilot visibility preserves the existing local trial; it is not release approval. */
export function isPlaceable(asset: CatalogueAsset): boolean {
  return asset.readiness === 'pilot' || asset.readiness === 'ready';
}
export function browseAssets(query = '', groupId = '', assets = CATALOGUE_ASSETS): CatalogueAsset[] {
  const terms = query.toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim().split(/\s+/).filter(Boolean);
  return assets.filter(asset => {
    const group = calgaryGroup(asset.calgaryGuide);
    if (!group) return false;
    const haystack = [asset.label, asset.description, group.label, ...group.districts].join(' ').toLowerCase().replace(/[^a-z0-9]+/g, ' ');
    return isPlaceable(asset) && (!groupId || groupId === group.id) && terms.every(term => haystack.includes(term));
  });
}
export function availableGroups(assets = CATALOGUE_ASSETS) {
  return CALGARY_GROUPS.filter(group => assets.some(asset => isPlaceable(asset) && asset.calgaryGuide.groupId === group.id));
}
/** Run in tests before adding a record; do not load GLBs to browse the picker. */
export function validateRegistry(assets: CatalogueAsset[]): string[] {
  const errors: string[] = [];
  const ids = new Set<string>();
  for (const asset of assets) {
    if (!asset.id || ids.has(asset.id)) errors.push(`Duplicate or empty asset ID: ${asset.id}`);
    ids.add(asset.id);
    if (!Number.isInteger(asset.definitionVersion) || asset.definitionVersion < 1 || !asset.model.variantId) errors.push(`Invalid version/variant: ${asset.id}`);
    const group = CALGARY_GROUPS.find(g => g.id === asset.calgaryGuide.groupId);
    const domain = asset.kind === 'street' ? 'street_pathway' : asset.zoneType === 'building' ? 'building' : 'park_plaza';
    if (!group || group.domain !== domain) errors.push(`Invalid Calgary group: ${asset.id}`);
    if (asset.kind === 'object') {
      if (![asset.width, asset.depth, asset.minWidth, asset.minDepth, asset.maxSize].every(n => Number.isFinite(n) && n > 0)
        || asset.width < asset.minWidth || asset.depth < asset.minDepth || asset.width > asset.maxSize || asset.depth > asset.maxSize) errors.push(`Invalid dimensions: ${asset.id}`);
      const variant = asset.zoneType === 'building' ? asset.properties.development_selected_variant_id : asset.properties.green_space_selected_variant_id;
      if (variant !== asset.model.variantId) errors.push(`Variant mismatch: ${asset.id}`);
      if (asset.reshapeMode === 'repeat_native' && (!asset.nativeDimensions || asset.properties.native_home_plot !== true)) errors.push(`Missing native repeat contract: ${asset.id}`);
    } else if (!Number.isFinite(asset.sectionWidth) || asset.sectionWidth <= 0 || asset.properties.width !== asset.sectionWidth || asset.properties.road_selected_variant_id !== asset.model.variantId) errors.push(`Invalid street section: ${asset.id}`);
  }
  return errors;
}
