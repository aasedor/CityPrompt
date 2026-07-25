/**
 * Executable Public Realm LEGO V1 street capability catalog.
 *
 * This catalog is deliberately small. It describes only the families the
 * live globe renderer can reproduce metrically and deterministically; the
 * much larger visual-reference catalog remains available to Classic render
 * and the manual street picker without implying executable 3D support.
 */

export const PUBLIC_REALM_STREET_FAMILY_VERSION = 1 as const;

export type PublicRealmStreetFamilyId =
  | 'street_local_public_realm'
  | 'street_complete_main_22m'
  | 'street_four_way_intersection'
  | 'street_compact_roundabout';

export type StreetAppearanceKitId =
  | 'calgary_contemporary_native'
  | 'heritage_brick_stone'
  | 'timber_biophilic'
  | 'industrial_adaptive_reuse'
  | 'green_corridor_v1'
  | 'dutch_corner_islands_v1'
  | 'classic_tree_lined_v1';

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
] as const satisfies readonly StreetAppearanceKitId[]);
const INTERSECTION_APPEARANCE_IDS: readonly StreetAppearanceKitId[] = Object.freeze([
  'dutch_corner_islands_v1',
]);
const ROUNDABOUT_APPEARANCE_IDS: readonly StreetAppearanceKitId[] = Object.freeze([
  'classic_tree_lined_v1',
]);

export const PUBLIC_REALM_STREET_FAMILIES: Readonly<Record<PublicRealmStreetFamilyId, PublicRealmStreetFamilyDefinition>> = Object.freeze({
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
      'multi_use_trail',
      'toronto_laneway',
    ]),
    nativeRowM: null,
    crossSection: Object.freeze([]),
    defaultAppearanceKitId: 'calgary_contemporary_native',
    appearanceKitIds: LOCAL_APPEARANCE_IDS,
    capabilities: Object.freeze(['metric_section', 'terrain_drape', 'street_trees', 'lighting', 'benches', 'accessible_intersection']),
  },
  street_complete_main_22m: {
    id: 'street_complete_main_22m',
    familyVersion: 1,
    label: '22 m Complete Main Street',
    description: 'A native 22 m main street with protected cycling, parking/loading, furnishing zones, sidewalks and two movement lanes.',
    sourceArchetypeIds: Object.freeze(['main_street_complete']),
    nativeRowM: 22,
    crossSection: Object.freeze([
      { type: 'sidewalk', widthM: 2.4, label: 'Clear accessible sidewalk', surface: 'architectural concrete' },
      { type: 'boulevard', widthM: 1.2, label: 'Tree / furnishing zone', surface: 'unit paving and tree grates' },
      { type: 'cycle_track', widthM: 1.6, label: 'Raised protected cycle track', surface: 'red asphalt' },
      { type: 'buffer', widthM: 0.4, label: 'Cycle buffer', surface: 'concrete separator' },
      { type: 'parking', widthM: 2, label: 'Parking / loading', surface: 'asphalt' },
      { type: 'travel_lane', widthM: 3.4, label: 'Movement lane', surface: 'asphalt' },
      { type: 'travel_lane', widthM: 3.4, label: 'Movement lane', surface: 'asphalt' },
      { type: 'parking', widthM: 2, label: 'Parking / loading', surface: 'asphalt' },
      { type: 'buffer', widthM: 0.4, label: 'Cycle buffer', surface: 'concrete separator' },
      { type: 'cycle_track', widthM: 1.6, label: 'Raised protected cycle track', surface: 'red asphalt' },
      { type: 'boulevard', widthM: 1.2, label: 'Tree / furnishing zone', surface: 'unit paving and tree grates' },
      { type: 'sidewalk', widthM: 2.4, label: 'Clear accessible sidewalk', surface: 'architectural concrete' },
    ]),
    defaultAppearanceKitId: 'calgary_contemporary_native',
    appearanceKitIds: DISTRICT_APPEARANCE_IDS,
    capabilities: Object.freeze(['metric_section', 'terrain_drape', 'protected_cycle', 'loading', 'street_trees', 'lighting', 'benches', 'accessible_intersection']),
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

const districtSelections = (
  familyId: PublicRealmStreetFamilyId,
  archetypeId: string,
): PublicRealmStreetSelectionDefinition[] => DISTRICT_APPEARANCE_IDS.map((appearanceKitId, index) => ({
  familyId,
  archetypeId,
  variantId: `${archetypeId}_v${index}`,
  appearanceKitId,
  targetType: 'street_segment',
}));

export const PUBLIC_REALM_STREET_SELECTIONS: readonly PublicRealmStreetSelectionDefinition[] = Object.freeze([
  ...['yield_street', 'narrow_residential_street', 'woonerf_shared_street', 'calgary_local', 'green_alley', 'toronto_laneway']
    .flatMap((archetypeId) => districtSelections('street_local_public_realm', archetypeId)),
  {
    familyId: 'street_local_public_realm',
    archetypeId: 'multi_use_trail',
    variantId: 'multi_use_trail_v1',
    appearanceKitId: 'green_corridor_v1',
    targetType: 'street_segment',
  },
  ...districtSelections('street_complete_main_22m', 'main_street_complete'),
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
