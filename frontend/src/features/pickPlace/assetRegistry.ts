import { nativeParkLayouts } from '@/features/parks/nativeParkRegistry';
import validation from '@/data/validationCatalogue.json';
import expansion from '@/data/classroomExpansion.json';
import flexibleParks from '@/data/flexibleParks.json';
import type { SiteZoneProperties } from '@/types';
import streetCatalogue from '@/data/streetPathArchetypes.json';
import nativeStreets from '@/data/nativeStreetPilots.json';
import manualStreets from '@/data/streetManual.json';
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
  zoneType: 'building' | 'green_space' | 'road';
  reshapeMode: 'repeat_native' | 'adaptive_layout' | 'fixed_native' | 'authored_footprint';
  width: number;
  depth: number;
  minWidth: number;
  minDepth: number;
  maxSize: number;
  /** Optional reviewed per-axis limits. Legacy assets use maxSize for both. */
  maxWidth?: number;
  maxDepth?: number;
  nativeDimensions?: [number, number, number];
  /** Finite authored vertical assembly.  Fixed podium/roof modules keep their
   * geometry while a reviewed typical-storey module repeats between them. */
  storeyProgram?: {
    id: string;
    mode: 'fixed_authored_assembly' | 'repeat_authored_floor' | 'select_authored_assembly';
    nativeStoreys: number;
    minStoreys: number;
    maxStoreys: number;
    recommendedMinStoreys?: number;
    recommendedMaxStoreys?: number;
    podiumStoreys: number;
    podiumHeightM: number;
    repeatedStoreyHeightM: number;
    roofHeightM: number;
  };
  /** A reviewed, uniform horizontal scale band for the complete authored
   * assembly.  The parcel remains unchanged and Z is never scaled. */
  footprintProgram?: {
    id: string;
    mode: 'uniform_horizontal_scale';
    nativeWidthM: number;
    nativeDepthM: number;
    minScale: number;
    maxScale: number;
    defaultScale: number;
    step: number;
    /** False keeps the targeting contract active without exposing its control. */
    editable?: boolean;
  };
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

export const LEGACY_OBJECT_ASSETS: PlaceAsset[] = [
  {
    id: 'infill_home', kind: 'object', definitionVersion: 2, readiness: 'pilot', reshapeMode: 'repeat_native', model: { variantId: 'infill_flat_roof_minimal', revision: 'calgary-infill-flat-roof-minimal-clay-v006', method: 'RLASM 6.1' }, label: 'Infill homes',
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

/** Shape-first parks use the existing measured public-realm kits. Their
 * programme adapts to the drawn parcel; they never scale a native assembly. */
export const FLEXIBLE_PARK_ASSETS: PlaceAsset[] = flexibleParks.programmes.map(programme => ({
  id: programme.id, kind: 'object', definitionVersion: 1,
  readiness: 'pilot', reshapeMode: 'authored_footprint',
  model: { variantId: programme.variantId, revision: 'flexible-outline-v1', method: 'public_realm_park_kit' },
  label: programme.label, description: programme.description, thumbnail: programme.thumbnail,
  calgaryGuide: classifyCalgaryAsset('park_plaza', { id: programme.archetypeId }),
  zoneType: 'green_space', width: programme.widthM, depth: programme.depthM,
  minWidth: programme.minWidthM, minDepth: programme.minDepthM, maxSize: programme.maxSizeM,
  reshapeDescription: programme.reshapeDescription,
  properties: { green_space_archetype_id: programme.archetypeId, green_space_selected_variant_id: programme.variantId,
    pick_place_flexible_park: programme.key, pick_place_automatic_3d: true },
}));

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
export function additionalStreet(archetypeId: string, label: string, description: string,
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

const NATIVE_STREET_ASSETS: StreetAsset[] = nativeStreets.map(street => ({
  id: street.id, kind: 'street', definitionVersion: 1, readiness: 'pilot', reshapeMode: 'fixed_section_route',
    label: street.title, description: street.id === 'amsterdam_gracht_v1' ? 'Draw a canal route with bends and a length that fits your site. Native-size banks, trees and arch crossing on prepared level ground.' : street.program ? `${street.widthM} m wide · ${street.program.minLengthM}–${street.program.maxLengthM} m routes · prepared level site` : `${street.widthM} m wide · curved routes with native-size furniture`,
  thumbnail: street.thumbnailUrl, sectionWidth: street.widthM,
  calgaryGuide: classifyCalgaryAsset('street_pathway', { id: street.sourceArchetypeId }),
  model: { variantId: street.id, revision: street.sourceRecipeSha256, method: 'native_street_modules_v1' },
  properties: { road_archetype_id: street.sourceArchetypeId, road_selected_variant_id: street.id,
    width: street.widthM, pick_place_street_section: street.id, pick_place_automatic_3d: true,
    pick_place_definition_version: 1, community_3d_mask_existing_tiles: true,
    road_standard_citation: 'City Prompt native-module teaching section' },
}));

export const ALL_MANUAL_STREET_ASSETS: StreetAsset[] = manualStreets.map(street => ({
  id: street.variantId, kind: 'street', definitionVersion: 1, readiness: 'pilot',
  reshapeMode: 'fixed_section_route', label: street.title,
  description: `${street.widthM} m right of way | ${street.sourceEdition ?? 'Street Manual draft · source check pending'} | ${street.section.limitations?.join(' ') ?? 'fixed lane and sidewalk widths'}`,
  thumbnail: street.thumbnailUrl, sectionWidth: street.widthM,
  calgaryGuide: classifyCalgaryAsset('street_pathway', { id: street.archetypeId }),
  model: { variantId: street.variantId, revision: street.sourceSectionSha256, method: 'manual_metric_section_v1' },
  properties: { road_archetype_id: street.archetypeId, road_selected_variant_id: street.variantId,
    width: street.widthM, pick_place_street_section: street.variantId, pick_place_automatic_3d: true,
    pick_place_definition_version: 1, community_3d_mask_existing_tiles: true,
    road_standard_citation: street.sourceEdition
      ? `Calgary Street Manual ${street.sourceEdition}, PDF page ${street.sourcePdfPage}. ${street.section.limitations?.join(' ') ?? ''}`.trim()
      : `Recorded Street Manual Draft 4.0, Figure ${street.figure}; source check pending` },
}));
const supersededManualVariants = new Set(manualStreets.filter(street => !street.sourceEdition).map(street => street.variantId));
export const MANUAL_STREET_ASSETS = ALL_MANUAL_STREET_ASSETS.filter(asset => !supersededManualVariants.has(asset.model.variantId));
export const STREET_ASSETS: StreetAsset[] = [...NATIVE_STREET_ASSETS, ...MANUAL_STREET_ASSETS];
// Saved metric streets stay editable without adding them to the seven candidates.
export const LEGACY_SECTION_STREET_ASSETS: StreetAsset[] = [
  ...ALL_MANUAL_STREET_ASSETS.filter(asset => supersededManualVariants.has(asset.model.variantId)), LOCAL_STREET_ASSET,
  additionalStreet('calgary_collector', 'Calgary collector street', 'Existing metric section', {groupId:'local',basis:'draft_manual'})];

/** New starter houses place one native model. Existing saved home plots keep
 * their explicit repeat flag and are resolved by assetForZone as legacy plots. */
export function individualStarterHome(asset: CatalogueAsset): CatalogueAsset {
  if (asset.kind !== 'object' || !['infill_home', 'trial_postwar_bungalow'].includes(asset.id)) return asset;
  return { ...asset, reshapeMode: 'fixed_native', definitionVersion: Math.max(2, asset.definitionVersion),
    minWidth: asset.width, minDepth: asset.depth,
    label: asset.id === 'infill_home' ? 'Infill home' : asset.label,
    description: asset.id === 'infill_home' ? 'A two-storey home. Place another to build your street.' : asset.description,
    reshapeDescription: 'One home keeps its size and proportions. Resize the surrounding plot; use Place another for the next home.',
    properties: { ...asset.properties, native_home_plot: false, native_plot_axes: true },
  };
}

export const LEGACY_VALIDATION_ASSETS = validation.assets as CatalogueAsset[];
function withStoreyMetadata(asset: CatalogueAsset): CatalogueAsset {
  if (asset.kind !== 'object' || asset.zoneType !== 'building' || asset.storeyProgram) return asset;
  const nativeStoreys = Number(asset.properties.floor_count ?? asset.properties.floors);
  const nativeHeightM = Number(asset.nativeDimensions?.[2]);
  if (!Number.isInteger(nativeStoreys) || nativeStoreys < 1 || !Number.isFinite(nativeHeightM) || nativeHeightM <= 0) {
    return asset;
  }
  return {
    ...asset,
    storeyProgram: {
      id: `${asset.model.variantId}-fixed-storeys-v001`,
      mode: 'fixed_authored_assembly',
      nativeStoreys,
      minStoreys: nativeStoreys,
      maxStoreys: nativeStoreys,
      recommendedMinStoreys: nativeStoreys,
      recommendedMaxStoreys: nativeStoreys,
      podiumStoreys: nativeStoreys,
      podiumHeightM: nativeHeightM,
      repeatedStoreyHeightM: 0,
      roofHeightM: 0,
    },
  };
}

export const CATALOGUE_ASSETS: CatalogueAsset[] = [...LEGACY_VALIDATION_ASSETS, ...expansion.assets as CatalogueAsset[], ...MANUAL_STREET_ASSETS].map((asset): CatalogueAsset => {
  if (asset.kind==='object' && asset.zoneType==='road') {
    const native=NATIVE_STREET_ASSETS.find(street=>street.model.variantId===asset.model.variantId);
    if(native)return {...native,calgaryGuide:asset.calgaryGuide};
  }
  if (asset.kind !== 'object' || asset.zoneType !== 'green_space') return withStoreyMetadata(asset);
  const layout = nativeParkLayouts.find(p => p.variantId === asset.model.variantId && p.mode === 'native_assembly' && p.status === 'pilot');
  if (!layout) return asset;
  const properties = {...asset.properties};
  for (const key of ['public_realm_trial_asset','validation_fixed_fixture','validation_native_url','park_trio_layout']) delete properties[key];
  return {...asset, id: `native-park:${layout.id}`, definitionVersion: 2, reshapeMode:'authored_footprint',
    description:'Complete native park layout. Objects retain their real dimensions.',
    reshapeDescription:'Choose a layout; its objects stay at native size when the surrounding parcel changes.',
    model:{...asset.model,revision:layout.contentRevision,method:'native_park_v2'},
    width:layout.occupiedWidthM,depth:layout.occupiedDepthM,minWidth:layout.occupiedWidthM,minDepth:layout.occupiedDepthM,
    properties:{...properties,green_space_native_layout_id:layout.id,pick_place_automatic_3d:true}};
}).concat(FLEXIBLE_PARK_ASSETS);
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
    const domain = asset.kind === 'street' || asset.zoneType === 'road' ? 'street_pathway' : asset.zoneType === 'building' ? 'building' : 'park_plaza';
    if (!group || group.domain !== domain) errors.push(`Invalid Calgary group: ${asset.id}`);
    if (asset.kind === 'object') {
      const maxWidth = asset.maxWidth ?? asset.maxSize;
      const maxDepth = asset.maxDepth ?? asset.maxSize;
      if (![asset.width, asset.depth, asset.minWidth, asset.minDepth, asset.maxSize, maxWidth, maxDepth].every(n => Number.isFinite(n) && n > 0)
        || asset.width < asset.minWidth || asset.depth < asset.minDepth
        || asset.width > maxWidth || asset.depth > maxDepth
        || maxWidth > asset.maxSize || maxDepth > asset.maxSize) errors.push(`Invalid dimensions: ${asset.id}`);
      const variant = asset.zoneType === 'building' ? asset.properties.development_selected_variant_id : asset.zoneType === 'road' ? asset.properties.road_selected_variant_id : asset.properties.green_space_selected_variant_id;
      if (variant !== asset.model.variantId) errors.push(`Variant mismatch: ${asset.id}`);
      if (asset.reshapeMode === 'repeat_native' && (!asset.nativeDimensions || asset.properties.native_home_plot !== true)) errors.push(`Missing native repeat contract: ${asset.id}`);
      if (asset.zoneType === 'building') {
        const program = asset.storeyProgram;
        if (program) {
          const nativeHeight = Number(asset.nativeDimensions?.[2]);
          const programmeHeight = program.podiumHeightM
            + (program.nativeStoreys - program.podiumStoreys) * program.repeatedStoreyHeightM
            + program.roofHeightM;
          if (!Number.isInteger(program.nativeStoreys)
            || !Number.isInteger(program.minStoreys)
            || !Number.isInteger(program.maxStoreys)
            || program.minStoreys < 1
            || program.minStoreys > program.nativeStoreys
            || program.nativeStoreys > program.maxStoreys
            || !Number.isFinite(programmeHeight)
            || !Number.isFinite(nativeHeight)
            || Math.abs(programmeHeight - nativeHeight) > 0.05
            || (program.mode === 'fixed_authored_assembly'
              && (program.minStoreys !== program.nativeStoreys || program.maxStoreys !== program.nativeStoreys))) {
            errors.push(`Invalid storey metadata: ${asset.id}`);
          }
        }
      }
    } else if (!Number.isFinite(asset.sectionWidth) || asset.sectionWidth <= 0 || asset.properties.width !== asset.sectionWidth || asset.properties.road_selected_variant_id !== asset.model.variantId) errors.push(`Invalid street section: ${asset.id}`);
  }
  return errors;
}
