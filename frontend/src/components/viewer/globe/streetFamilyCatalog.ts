/**
 * Executable Public Realm LEGO V1 street capability catalog.
 *
 * This catalog is deliberately small. It describes only the families the
 * live globe renderer can reproduce metrically and deterministically; the
 * much larger visual-reference catalog remains available to Classic render
 * and the manual street picker without implying executable 3D support.
 */

import nativeStreets from '@/data/nativeStreetPilots.json';

export const PUBLIC_REALM_STREET_FAMILY_VERSION = 1 as const;
type NativeStreetFamilyId = 'street_native_student_main_street_v1' | 'street_native_student_market_street_v1';

export type PublicRealmStreetFamilyId =
  | NativeStreetFamilyId
  | 'street_local_public_realm'
  | 'street_complete_main_18m'
  | 'street_complete_main_22m'
  | 'street_four_way_intersection'
  | 'street_compact_roundabout';

export type StreetAppearanceKitId =
  | 'calgary_contemporary_native'
  | 'heritage_brick_stone'
  | 'timber_biophilic'
  | 'industrial_adaptive_reuse'
  | 'green_corridor_v1'
  | 'dutch_woonerf_v1'
  | 'dutch_corner_islands_v1'
  | 'classic_tree_lined_v1'
  | 'modern_minimalist_v1'
  | 'european_cobblestone_v1'
  | 'tropical_boulevard_v1';

export interface StreetAppearancePalette {
  motor: string;
  parking: string;
  cycle: string;
  sidewalk: string;
  planting: string;
  buffer: string;
  shoulder: string;
  path: string;
  curb: string;
  marking: string;
  tactile: string;
  fixtureMetal: string;
  fixtureWood: string;
  roughness: number;
  metalness: number;
}

export interface StreetAppearanceKit {
  id: StreetAppearanceKitId;
  label: string;
  description: string;
  palette: StreetAppearancePalette;
}

export interface ExecutableStreetSectionBand {
  type: string;
  widthM: number;
  label: string;
  surface: string;
}

export interface PublicRealmStreetFamilyDefinition {
  id: PublicRealmStreetFamilyId;
  familyVersion: typeof PUBLIC_REALM_STREET_FAMILY_VERSION;
  label: string;
  description: string;
  sourceArchetypeIds: readonly string[];
  nativeRowM: number | null;
  crossSection: readonly ExecutableStreetSectionBand[];
  defaultAppearanceKitId: StreetAppearanceKitId;
  appearanceKitIds: readonly StreetAppearanceKitId[];
  capabilities: readonly string[];
  supportedNodeArmCounts?: readonly number[];
}

export interface PublicRealmStreetSelectionDefinition {
  familyId: PublicRealmStreetFamilyId;
  archetypeId: string;
  variantId: string;
  appearanceKitId: StreetAppearanceKitId;
  targetType: 'street_segment' | 'street_node';
  profileId?: string;
  rowWidthM?: number;
  componentSetIds?: readonly string[];
}

export const STREET_APPEARANCE_KITS: Readonly<Record<StreetAppearanceKitId, StreetAppearanceKit>> = Object.freeze({
  calgary_contemporary_native: {
    id: 'calgary_contemporary_native',
    label: 'Calgary Contemporary / Native Prairie',
    description: 'Cool asphalt, pale concrete, native prairie planting, charcoal fixtures and warm timber seating.',
    palette: {
      motor: '#4f5559', parking: '#5b6164', cycle: '#8c5848', sidewalk: '#c5c1b7',
      planting: '#607a4e', buffer: '#8a9879', shoulder: '#827866', path: '#a5a39b',
      curb: '#a9adb0', marking: '#eee9dc', tactile: '#d0a83d',
      fixtureMetal: '#30383a', fixtureWood: '#8a6448', roughness: 0.88, metalness: 0.03,
    },
  },
  heritage_brick_stone: {
    id: 'heritage_brick_stone',
    label: 'Heritage Brick and Stone',
    description: 'Charcoal carriageway, warm brick furnishing areas, limestone walks and blackened iron fixtures.',
    palette: {
      motor: '#535150', parking: '#615b57', cycle: '#9a654f', sidewalk: '#c8bca8',
      planting: '#66784d', buffer: '#918875', shoulder: '#8b735f', path: '#b3a28d',
      curb: '#a69e92', marking: '#f0e6cf', tactile: '#c79c3b',
      fixtureMetal: '#262525', fixtureWood: '#744d35', roughness: 0.92, metalness: 0.02,
    },
  },
  timber_biophilic: {
    id: 'timber_biophilic',
    label: 'Timber / Biophilic',
    description: 'Low-carbon concrete, muted paving, layered green planting and dark bronze/timber furniture.',
    palette: {
      motor: '#555b59', parking: '#626965', cycle: '#527a65', sidewalk: '#c4c2b3',
      planting: '#55764d', buffer: '#849574', shoulder: '#837d69', path: '#aaa89b',
      curb: '#a8aaa4', marking: '#ece9d9', tactile: '#c9a542',
      fixtureMetal: '#38413d', fixtureWood: '#936f4e', roughness: 0.9, metalness: 0.025,
    },
  },
  industrial_adaptive_reuse: {
    id: 'industrial_adaptive_reuse',
    label: 'Industrial Adaptive-Reuse',
    description: 'Dark aggregate paving, weathered concrete, rust-red cycle surfacing and black steel furniture.',
    palette: {
      motor: '#484c4f', parking: '#565b5e', cycle: '#8f5143', sidewalk: '#aaa8a1',
      planting: '#5f724b', buffer: '#7e8872', shoulder: '#746e63', path: '#97958e',
      curb: '#92979a', marking: '#e8e4d8', tactile: '#d0a23a',
      fixtureMetal: '#252a2d', fixtureWood: '#795238', roughness: 0.86, metalness: 0.06,
    },
  },
  green_corridor_v1: {
    id: 'green_corridor_v1',
    label: 'Green Corridor',
    description: 'Smooth trail asphalt, soft aggregate shoulders, native meadow edges and timber rest furniture.',
    palette: {
      motor: '#555b59', parking: '#606763', cycle: '#547964', sidewalk: '#c0beb2',
      planting: '#55764d', buffer: '#839374', shoulder: '#807662', path: '#777b78',
      curb: '#a4a8a2', marking: '#eadfae', tactile: '#c8a43c',
      fixtureMetal: '#3a423e', fixtureWood: '#906947', roughness: 0.93, metalness: 0.01,
    },
  },
  dutch_woonerf_v1: {
    id: 'dutch_woonerf_v1',
    label: 'Dutch Woonerf',
    description: 'Warm herringbone brick, flush granite inlays, permeable tree islands, black bollards and informal shared-space furnishing.',
    palette: {
      motor: '#a45f42', parking: '#8e5a47', cycle: '#a45f42', sidewalk: '#bdad96',
      planting: '#607b4d', buffer: '#aaa08e', shoulder: '#b9ad98', path: '#aa6749',
      curb: '#aaa394', marking: '#eee5d4', tactile: '#c99e3b',
      fixtureMetal: '#2d3232', fixtureWood: '#79533b', roughness: 0.94, metalness: 0.01,
    },
  },
  dutch_corner_islands_v1: {
    id: 'dutch_corner_islands_v1',
    label: 'Dutch Protected Corner',
    description: 'High-contrast crossings, red cycle surfacing, pale corner islands and detectable-warning pads.',
    palette: {
      motor: '#4d5357', parking: '#5b6063', cycle: '#a45445', sidewalk: '#c9c5ba',
      planting: '#607a4e', buffer: '#b9b5aa', shoulder: '#817969', path: '#a4a29a',
      curb: '#afb2b2', marking: '#f5f0df', tactile: '#d2aa3c',
      fixtureMetal: '#30383b', fixtureWood: '#876147', roughness: 0.87, metalness: 0.025,
    },
  },
  classic_tree_lined_v1: {
    id: 'classic_tree_lined_v1',
    label: 'Classic Tree-Lined',
    description: 'Neutral asphalt, granite-toned curbs, green central planting and traditional dark fixtures.',
    palette: {
      motor: '#51565a', parking: '#5c6265', cycle: '#6a7370', sidewalk: '#c2beb3',
      planting: '#607b4d', buffer: '#889679', shoulder: '#807765', path: '#aaa79c',
      curb: '#a7aaab', marking: '#eee9dc', tactile: '#cca33b',
      fixtureMetal: '#292f31', fixtureWood: '#7e583d', roughness: 0.9, metalness: 0.02,
    },
  },
  modern_minimalist_v1: {
    id: 'modern_minimalist_v1',
    label: 'Modern Minimalist',
    description: 'Fine dark asphalt, light architectural concrete, steel tree grates, columnar planting and restrained brushed-metal furniture.',
    palette: {
      motor: '#50575b', parking: '#596064', cycle: '#657b78', sidewalk: '#cbc9c2',
      planting: '#66805a', buffer: '#a5aaa3', shoulder: '#85827a', path: '#b0aea7',
      curb: '#b6b9b9', marking: '#f0eee7', tactile: '#cba33c',
      fixtureMetal: '#4a5357', fixtureWood: '#80654f', roughness: 0.84, metalness: 0.06,
    },
  },
  european_cobblestone_v1: {
    id: 'european_cobblestone_v1',
    label: 'European Cobblestone',
    description: 'Natural stone setts, granite curbs, limestone walks, pollarded trees and vintage black iron furniture.',
    palette: {
      motor: '#716b64', parking: '#777068', cycle: '#756c62', sidewalk: '#c1b7a6',
      planting: '#63764f', buffer: '#9f9585', shoulder: '#8a7d6d', path: '#a99a88',
      curb: '#a5a29d', marking: '#eee4d1', tactile: '#c69b3b',
      fixtureMetal: '#252626', fixtureWood: '#76513b', roughness: 0.95, metalness: 0.01,
    },
  },
  tropical_boulevard_v1: {
    id: 'tropical_boulevard_v1',
    label: 'Tropical Boulevard',
    description: 'Warm asphalt and concrete, lush layered planting, coral-toned curbs, palms and decorative dark-bronze furniture.',
    palette: {
      motor: '#565956', parking: '#62645f', cycle: '#5d7d68', sidewalk: '#cbbd9f',
      planting: '#477446', buffer: '#7f9872', shoulder: '#8f8067', path: '#b9a987',
      curb: '#bdad94', marking: '#f2ead7', tactile: '#cda440',
      fixtureMetal: '#3a3730', fixtureWood: '#8c603e', roughness: 0.9, metalness: 0.025,
    },
  },
});

const DISTRICT_APPEARANCE_IDS = Object.freeze([
  'calgary_contemporary_native',
  'heritage_brick_stone',
  'timber_biophilic',
  'industrial_adaptive_reuse',
] as const satisfies readonly StreetAppearanceKitId[]);
const LOCAL_APPEARANCE_IDS = Object.freeze([
  ...DISTRICT_APPEARANCE_IDS,
  'green_corridor_v1',
  'dutch_woonerf_v1',
  'classic_tree_lined_v1',
  'modern_minimalist_v1',
  'european_cobblestone_v1',
  'tropical_boulevard_v1',
] as const satisfies readonly StreetAppearanceKitId[]);
const CLASSIC_STREET_APPEARANCE_IDS = Object.freeze([
  'classic_tree_lined_v1',
  'modern_minimalist_v1',
  'european_cobblestone_v1',
  'tropical_boulevard_v1',
] as const satisfies readonly StreetAppearanceKitId[]);
const INTERSECTION_APPEARANCE_IDS: readonly StreetAppearanceKitId[] = Object.freeze([
  'dutch_corner_islands_v1',
]);
const ROUNDABOUT_APPEARANCE_IDS: readonly StreetAppearanceKitId[] = Object.freeze([
  'classic_tree_lined_v1',
]);

const MAIN_STREET_RENDERLOCK_CROSS_SECTION: readonly ExecutableStreetSectionBand[] = Object.freeze([
  { type: 'sidewalk', widthM: 2, label: 'Wide commercial sidewalk', surface: 'architectural concrete' },
  { type: 'boulevard', widthM: 1.25, label: 'Tree / furnishing zone', surface: 'tree grates and planting' },
  { type: 'parking', widthM: 2.1, label: 'Parallel parking', surface: 'asphalt' },
  { type: 'travel_lane', widthM: 3.65, label: 'Travel / sharrow lane', surface: 'fine asphalt' },
  { type: 'travel_lane', widthM: 3.65, label: 'Travel / sharrow lane', surface: 'fine asphalt' },
  { type: 'parking', widthM: 2.1, label: 'Parallel parking', surface: 'asphalt' },
  { type: 'boulevard', widthM: 1.25, label: 'Tree / furnishing zone', surface: 'tree grates and planting' },
  { type: 'sidewalk', widthM: 2, label: 'Wide commercial sidewalk', surface: 'architectural concrete' },
]);

function nativeFamily(id: NativeStreetFamilyId): PublicRealmStreetFamilyDefinition {
  const street = nativeStreets.find(row => `street_native_${row.id}` === id);
  if (!street) throw new Error(`Missing packaged native street: ${id}`);
  const appearance: StreetAppearanceKitId = street.junctionSurface === 'cobble' ? 'european_cobblestone_v1' : 'heritage_brick_stone';
  return { id, familyVersion: 1, label: street.title, description: 'Native-size modules along a metric street route.',
    sourceArchetypeIds: [street.sourceArchetypeId], nativeRowM: street.widthM,
    crossSection: street.sections.map(band => ({ type: band.name, widthM: band.width, label: band.name.replace(/_/g, ' '), surface: band.material })),
    defaultAppearanceKitId: appearance, appearanceKitIds: [appearance], capabilities: ['rigid_modules', 'curved_route', 'shared_junctions'],
  };
}

export const PUBLIC_REALM_STREET_FAMILIES: Readonly<Record<PublicRealmStreetFamilyId, PublicRealmStreetFamilyDefinition>> = Object.freeze({
  street_native_student_main_street_v1: nativeFamily('street_native_student_main_street_v1'),
  street_native_student_market_street_v1: nativeFamily('street_native_student_market_street_v1'),
  street_local_public_realm: {
    id: 'street_local_public_realm',
    familyVersion: 1,
    label: 'Residential Local Public Realm',
    description: 'A source-profile family for local streets, woonerfs, green alleys, laneways and trails; each source keeps its reviewed native metric section.',
    sourceArchetypeIds: Object.freeze([
      'calgary_local',
      'yield_street',
      'narrow_residential_street',
      'woonerf_shared_street',
      'green_alley',
      'neighborhood_greenway',
      'multi_use_trail',
      'toronto_laneway',
    ]),
    nativeRowM: null,
    crossSection: Object.freeze([]),
    defaultAppearanceKitId: 'calgary_contemporary_native',
    appearanceKitIds: LOCAL_APPEARANCE_IDS,
    capabilities: Object.freeze(['metric_section', 'terrain_drape', 'street_trees', 'lighting', 'benches', 'accessible_intersection']),
  },
  street_complete_main_18m: {
    id: 'street_complete_main_18m',
    familyVersion: 1,
    label: '18 m Classic Complete Main Street',
    description: 'The render-locked two-lane main street with parallel parking, broad sidewalks, tree/furnishing zones and sharrow travel lanes.',
    sourceArchetypeIds: Object.freeze(['main_street_complete']),
    nativeRowM: 18,
    crossSection: MAIN_STREET_RENDERLOCK_CROSS_SECTION,
    defaultAppearanceKitId: 'classic_tree_lined_v1',
    appearanceKitIds: CLASSIC_STREET_APPEARANCE_IDS,
    capabilities: Object.freeze(['metric_section', 'terrain_drape', 'parking', 'sharrows', 'street_trees', 'lighting', 'benches', 'accessible_intersection']),
  },
  street_complete_main_22m: {
    id: 'street_complete_main_22m',
    familyVersion: 1,
    label: 'Legacy 22 m Complete Main Street Envelope',
    description: 'Migration family that fits the render-locked complete-main-street program to existing 22 m authored polygons.',
    sourceArchetypeIds: Object.freeze(['main_street_complete']),
    nativeRowM: 18,
    crossSection: MAIN_STREET_RENDERLOCK_CROSS_SECTION,
    defaultAppearanceKitId: 'classic_tree_lined_v1',
    appearanceKitIds: CLASSIC_STREET_APPEARANCE_IDS,
    capabilities: Object.freeze(['metric_section', 'terrain_drape', 'parking', 'sharrows', 'street_trees', 'lighting', 'benches', 'accessible_intersection']),
  },
  street_four_way_intersection: {
    id: 'street_four_way_intersection',
    familyVersion: 1,
    label: 'Accessible Four-Way Intersection',
    description: 'A graph-owned crossing assembly with zebra crossings, directional curb ramps and high-contrast tactile warning pads.',
    sourceArchetypeIds: Object.freeze(['protected_intersection']),
    nativeRowM: null,
    crossSection: Object.freeze([]),
    defaultAppearanceKitId: 'dutch_corner_islands_v1',
    appearanceKitIds: INTERSECTION_APPEARANCE_IDS,
    capabilities: Object.freeze(['graph_node', 'terrain_anchor', 'zebra_crossing', 'directional_curb_ramps', 'tactile_warning']),
    supportedNodeArmCounts: Object.freeze([4]),
  },
  street_compact_roundabout: {
    id: 'street_compact_roundabout',
    familyVersion: 1,
    label: 'Compact Roundabout',
    description: 'The existing metric roundabout assembly exposed as a versioned Public Realm LEGO family.',
    sourceArchetypeIds: Object.freeze(['roundabout']),
    nativeRowM: null,
    crossSection: Object.freeze([]),
    defaultAppearanceKitId: 'classic_tree_lined_v1',
    appearanceKitIds: ROUNDABOUT_APPEARANCE_IDS,
    capabilities: Object.freeze(['metric_ring', 'truck_apron', 'central_island', 'splitter_islands', 'terrain_anchor']),
    supportedNodeArmCounts: Object.freeze([4]),
  },
});

const explicitSelections = (
  familyId: PublicRealmStreetFamilyId,
  archetypeId: string,
  appearanceKitIds: readonly StreetAppearanceKitId[],
): PublicRealmStreetSelectionDefinition[] => appearanceKitIds.map((appearanceKitId, index) => ({
  familyId,
  archetypeId,
  variantId: `${archetypeId}_v${index}`,
  appearanceKitId,
  targetType: 'street_segment',
}));

export const PUBLIC_REALM_STREET_SELECTIONS: readonly PublicRealmStreetSelectionDefinition[] = Object.freeze([
  ...nativeStreets.map(street => ({
    familyId: `street_native_${street.id}` as NativeStreetFamilyId,
    archetypeId: street.sourceArchetypeId, variantId: street.id,
    appearanceKitId: (street.junctionSurface === 'cobble' ? 'european_cobblestone_v1' : 'heritage_brick_stone') as StreetAppearanceKitId,
    targetType: 'street_segment' as const, rowWidthM: street.widthM,
    profileId: `native-${street.id.replace(/_/g, '-')}-v1`,
    componentSetIds: [
      `source_recipe:${street.sourceRecipeSha256}`, `source_assembly:${street.sourceAssemblySha256}`, `reference:${street.referenceSha256}`,
      ...Object.entries(street.modules).sort(([a], [b]) => a.localeCompare(b)).map(([kind, module]) => `module_${kind}:${module.sha256}`),
    ],
  })),
  {
    familyId: 'street_local_public_realm',
    archetypeId: 'calgary_local',
    variantId: 'calgary_local_v0',
    appearanceKitId: 'calgary_contemporary_native',
    targetType: 'street_segment',
  },
  {
    familyId: 'street_local_public_realm',
    archetypeId: 'green_alley',
    variantId: 'green_alley_v0',
    appearanceKitId: 'green_corridor_v1',
    targetType: 'street_segment',
  },
  {
    familyId: 'street_local_public_realm',
    archetypeId: 'toronto_laneway',
    variantId: 'toronto_laneway_v0',
    appearanceKitId: 'calgary_contemporary_native',
    targetType: 'street_segment',
  },
  ...explicitSelections('street_local_public_realm', 'narrow_residential_street', CLASSIC_STREET_APPEARANCE_IDS),
  ...[
    'yield_street',
    'woonerf_shared_street',
  ].map((archetypeId) => ({
    familyId: 'street_local_public_realm' as const,
    archetypeId,
    variantId: `${archetypeId}_v0`,
    appearanceKitId: 'dutch_woonerf_v1' as const,
    targetType: 'street_segment' as const,
  })),
  {
    familyId: 'street_local_public_realm',
    archetypeId: 'multi_use_trail',
    variantId: 'multi_use_trail_v1',
    appearanceKitId: 'green_corridor_v1',
    targetType: 'street_segment',
  },
  ...['neighborhood_greenway_v0', 'neighborhood_greenway_v1', 'neighborhood_greenway_v2'].map((variantId) => ({
    familyId: 'street_local_public_realm' as const,
    archetypeId: 'neighborhood_greenway',
    variantId,
    appearanceKitId: 'green_corridor_v1' as const,
    targetType: 'street_segment' as const,
  })),
  ...explicitSelections('street_complete_main_18m', 'main_street_complete', CLASSIC_STREET_APPEARANCE_IDS),
  ...explicitSelections('street_complete_main_22m', 'main_street_complete', CLASSIC_STREET_APPEARANCE_IDS),
  {
    familyId: 'street_four_way_intersection',
    archetypeId: 'protected_intersection',
    variantId: 'protected_intersection_v0',
    appearanceKitId: 'dutch_corner_islands_v1',
    targetType: 'street_node',
  },
  {
    familyId: 'street_compact_roundabout',
    archetypeId: 'roundabout',
    variantId: 'roundabout_v0',
    appearanceKitId: 'classic_tree_lined_v1',
    targetType: 'street_node',
  },
]);

function stableStringify(value: unknown): string {
  if (Array.isArray(value)) return `[${value.map(stableStringify).join(',')}]`;
  if (value && typeof value === 'object') {
    const record = value as Record<string, unknown>;
    return `{${Object.keys(record).sort().map((key) => `${JSON.stringify(key)}:${stableStringify(record[key])}`).join(',')}}`;
  }
  return JSON.stringify(value);
}

function fnv1a(value: string, seed: number): string {
  let hash = seed >>> 0;
  for (let index = 0; index < value.length; index += 1) {
    hash ^= value.charCodeAt(index);
    hash = Math.imul(hash, 16777619);
  }
  return (hash >>> 0).toString(16).padStart(8, '0');
}

export function fingerprintPublicRealmStreetCatalog(
  catalog: typeof PUBLIC_REALM_STREET_FAMILIES = PUBLIC_REALM_STREET_FAMILIES,
): string {
  const serialized = stableStringify(catalog);
  return `street-v1-${fnv1a(serialized, 2166136261)}${fnv1a(serialized, 2246822519)}`;
}

export const PUBLIC_REALM_STREET_CATALOG_FINGERPRINT = fingerprintPublicRealmStreetCatalog();

export function isPublicRealmStreetFamilyId(value: unknown): value is PublicRealmStreetFamilyId {
  return typeof value === 'string' && value in PUBLIC_REALM_STREET_FAMILIES;
}

export function resolveStreetAppearanceKit(
  family: PublicRealmStreetFamilyDefinition,
  requestedId: unknown,
): StreetAppearanceKit {
  const normalized = String(requestedId ?? '').toLowerCase().trim().replace(/-/g, '_');
  const selectedId = family.appearanceKitIds.find((candidate) => candidate === normalized)
    ?? family.defaultAppearanceKitId;
  return STREET_APPEARANCE_KITS[selectedId];
}
