import type { StreetSurfaceMaterialKind } from './streetSurfaceMaterials';

export type StreetReferenceAngleDeg = 30 | 60 | 90;

export type StreetVisualElementId =
  | 'unmarked_yield_carriageway'
  | 'two_way_travel_lanes'
  | 'single_shared_lane'
  | 'single_lane_circulatory_ring'
  | 'multi_lane_circulatory_ring'
  | 'bilateral_parallel_parking'
  | 'informal_parking_pockets'
  | 'parking_stall_markings'
  | 'concrete_sidewalks'
  | 'separated_sidewalks'
  | 'grass_planting_strips'
  | 'tree_furnishing_zones'
  | 'tree_grates'
  | 'mature_deciduous_canopy'
  | 'palm_tree_palette'
  | 'granite_curbs'
  | 'raised_curbs'
  | 'flush_stone_edges'
  | 'continuous_flush_surface'
  | 'herringbone_brick_paving'
  | 'stone_paving_inlays'
  | 'chicane_delineation'
  | 'integrated_planting_beds'
  | 'raised_tables'
  | 'play_elements'
  | 'hydrangea_planters'
  | 'bollards'
  | 'benches'
  | 'ornamental_iron_lamps'
  | 'modern_stainless_fixtures'
  | 'transit_shelter'
  | 'sharrow_markings'
  | 'painted_centerline'
  | 'painted_lane_dividers'
  | 'standard_lane_markings'
  | 'zebra_crosswalks'
  | 'yield_markings'
  | 'raised_median'
  | 'separated_cycle_track'
  | 'truck_apron'
  | 'landscaped_central_island'
  | 'splitter_islands'
  | 'sidewalk_connections'
  | 'traffic_signals'
  | 'building_in_central_island'
  | 'parked_vehicles_in_travel_space'
  | 'trees_in_vehicle_clearance';

export type StreetSurfaceRole =
  | 'motor'
  | 'shared'
  | 'parking'
  | 'sidewalk'
  | 'planting'
  | 'edge'
  | 'apron'
  | 'splitter'
  | 'island';

export interface StreetVisualReferenceView {
  /** The catalog's default character view is the approximately 30 degree view. */
  angleDeg: StreetReferenceAngleDeg;
  purpose: 'character' | 'section' | 'plan';
  path: string;
}

export interface StreetVisualSurfaceExpectation {
  role: StreetSurfaceRole;
  material: StreetSurfaceMaterialKind;
  description: string;
  side: 'left' | 'right' | 'center' | 'bilateral' | 'radial' | 'punctual';
  /** Width of one band. For bilateral bands this is the width on each side. */
  widthM?: number;
  level: 'flush' | 'raised' | 'depressed';
  markings: 'none' | 'parking_stalls' | 'sharrows' | 'crosswalks_and_yield';
}

export interface StreetTreeRhythm {
  placement: 'bilateral_regular' | 'bilateral_staggered' | 'alternating_chicane' | 'central_island';
  character: string;
  spacingM?: readonly [minimum: number, maximum: number];
  count?: readonly [minimum: number, maximum: number];
  clearanceRule: string;
}

export interface StreetVehicleRhythm {
  presence: 'required' | 'sparse' | 'allowed' | 'forbidden';
  placement: 'bilateral_parking' | 'informal_pockets' | 'moving_only' | 'none';
  occupancyRange?: readonly [minimum: number, maximum: number];
  rule: string;
}

export type StreetFixtureId =
  | 'ornamental_iron_lamp'
  | 'bench'
  | 'bollard'
  | 'integrated_planter'
  | 'hydrangea_planter'
  | 'play_node'
  | 'transit_shelter'
  | 'yield_sign';

export interface StreetFixtureRhythm {
  fixture: StreetFixtureId;
  placement: string;
  spacingM?: readonly [minimum: number, maximum: number];
  minimumPer100M?: number;
}

export interface StreetVisualContract {
  schemaVersion: 1;
  contractId: string;
  archetypeId: string;
  variantId: string;
  label: string;
  scope: 'within_right_of_way';
  target:
    | { type: 'segment'; rowWidthM: number; crossSectionTruth: string }
    | { type: 'node'; armCount: 4; inscribedCircleDiameterM: number; crossSectionTruth: string };
  referenceViews: readonly StreetVisualReferenceView[];
  withinRow: {
    required: readonly StreetVisualElementId[];
    forbidden: readonly StreetVisualElementId[];
  };
  surfaces: readonly StreetVisualSurfaceExpectation[];
  rhythm: {
    trees: readonly StreetTreeRhythm[];
    vehicles: StreetVehicleRhythm;
    fixtures: readonly StreetFixtureRhythm[];
  };
}

function threeViews(slug: string): readonly StreetVisualReferenceView[] {
  const base = `/archetypes/streets/${slug}/variant_0`;
  return Object.freeze([
    { angleDeg: 30, purpose: 'character', path: `${base}.png` },
    { angleDeg: 60, purpose: 'section', path: `${base}_angle_60.jpg` },
    { angleDeg: 90, purpose: 'plan', path: `${base}_angle_90.jpg` },
  ]);
}

/**
 * Executable visual acceptance vocabulary for the five current-project street
 * keepers. Reference imagery governs character; the metric target and surface
 * bands govern what is constructible inside the right-of-way.
 */
export const STREET_VISUAL_CONTRACTS = Object.freeze([
  {
    schemaVersion: 1,
    contractId: 'narrow_residential_street/narrow_residential_street_v0',
    archetypeId: 'narrow_residential_street',
    variantId: 'narrow_residential_street_v0',
    label: 'Classic Tree-Lined Narrow Residential Street',
    scope: 'within_right_of_way',
    target: {
      type: 'segment',
      rowWidthM: 10,
      crossSectionTruth: 'Two 1.2 m sidewalks, two 0.6 m planting strips, two 1.4 m parking bands and one 3.6 m unmarked yield carriageway.',
    },
    referenceViews: threeViews('narrow-residential-street'),
    withinRow: {
      required: Object.freeze([
        'unmarked_yield_carriageway',
        'bilateral_parallel_parking',
        'concrete_sidewalks',
        'grass_planting_strips',
        'granite_curbs',
        'mature_deciduous_canopy',
        'ornamental_iron_lamps',
      ]),
      forbidden: Object.freeze([
        'painted_centerline',
        'painted_lane_dividers',
        'raised_median',
        'separated_cycle_track',
        'palm_tree_palette',
        'modern_stainless_fixtures',
        'parked_vehicles_in_travel_space',
        'trees_in_vehicle_clearance',
      ]),
    },
    surfaces: Object.freeze([
      { role: 'sidewalk', material: 'concrete', description: 'traditional pale concrete sidewalk', side: 'bilateral', widthM: 1.2, level: 'raised', markings: 'none' },
      { role: 'planting', material: 'planting_grass', description: 'manicured grass tree strip', side: 'bilateral', widthM: 0.6, level: 'raised', markings: 'none' },
      { role: 'parking', material: 'parking_asphalt', description: 'parallel parking band without formal bays', side: 'bilateral', widthM: 1.4, level: 'flush', markings: 'none' },
      { role: 'motor', material: 'asphalt', description: 'dark unmarked low-speed carriageway', side: 'center', widthM: 3.6, level: 'flush', markings: 'none' },
      { role: 'edge', material: 'buffer_stone', description: 'granite curb edge', side: 'bilateral', level: 'raised', markings: 'none' },
    ]),
    rhythm: {
      trees: Object.freeze([{
        placement: 'bilateral_regular',
        character: 'mature broad-canopy deciduous trees forming a continuous shaded room',
        spacingM: [9, 11],
        clearanceRule: 'Remain centered in each grass strip; crowns may overlap the road but trunks may not enter parking or sidewalk clearance.',
      }]),
      vehicles: {
        presence: 'required',
        placement: 'bilateral_parking',
        occupancyRange: [0.25, 0.55],
        rule: 'Parallel only, varied colors and gaps, no center-carriageway parking.',
      },
      fixtures: Object.freeze([{
        fixture: 'ornamental_iron_lamp',
        placement: 'staggered along the outer sidewalk edge',
        spacingM: [20, 30],
      }]),
    },
  },
  {
    schemaVersion: 1,
    contractId: 'main_street_complete/main_street_complete_v0',
    archetypeId: 'main_street_complete',
    variantId: 'main_street_complete_v0',
    label: 'Classic Tree-Lined Complete Main Street',
    scope: 'within_right_of_way',
    target: {
      type: 'segment',
      rowWidthM: 18,
      crossSectionTruth: 'Two 2.0 m sidewalks, two 1.25 m furnishing zones, two 2.1 m parking bands and two 3.65 m travel/sharrow lanes.',
    },
    referenceViews: threeViews('main-street-complete'),
    withinRow: {
      required: Object.freeze([
        'two_way_travel_lanes',
        'bilateral_parallel_parking',
        'parking_stall_markings',
        'concrete_sidewalks',
        'tree_furnishing_zones',
        'tree_grates',
        'mature_deciduous_canopy',
        'granite_curbs',
        'ornamental_iron_lamps',
        'sharrow_markings',
        'zebra_crosswalks',
        'transit_shelter',
      ]),
      forbidden: Object.freeze([
        'painted_centerline',
        'raised_median',
        'separated_cycle_track',
        'palm_tree_palette',
        'modern_stainless_fixtures',
        'parked_vehicles_in_travel_space',
        'trees_in_vehicle_clearance',
      ]),
    },
    surfaces: Object.freeze([
      { role: 'sidewalk', material: 'concrete', description: 'wide traditional concrete sidewalk', side: 'bilateral', widthM: 2, level: 'raised', markings: 'none' },
      { role: 'planting', material: 'planting_grass', description: 'tree and furnishing zone with grates and planting', side: 'bilateral', widthM: 1.25, level: 'raised', markings: 'none' },
      { role: 'parking', material: 'parking_asphalt', description: 'marked parallel parking band', side: 'bilateral', widthM: 2.1, level: 'flush', markings: 'parking_stalls' },
      { role: 'motor', material: 'asphalt', description: 'paired travel lanes carrying sharrow symbols', side: 'center', widthM: 3.65, level: 'flush', markings: 'sharrows' },
      { role: 'edge', material: 'buffer_stone', description: 'granite curb edge', side: 'bilateral', level: 'raised', markings: 'none' },
    ]),
    rhythm: {
      trees: Object.freeze([{
        placement: 'bilateral_regular',
        character: 'mature broad-canopy deciduous trees in grates, repeated as a civic allée',
        spacingM: [8, 12],
        clearanceRule: 'Keep trunks in furnishing zones and preserve storefront, transit-stop and crosswalk sight lines.',
      }]),
      vehicles: {
        presence: 'required',
        placement: 'bilateral_parking',
        occupancyRange: [0.3, 0.65],
        rule: 'Populate marked bays with gaps at crossings and transit stops; add only sparse moving traffic.',
      },
      fixtures: Object.freeze([
        { fixture: 'ornamental_iron_lamp', placement: 'regular bilateral rows in furnishing zones', spacingM: [18, 24] },
        { fixture: 'bench', placement: 'facing the sidewalk activity zone without blocking clear path', spacingM: [30, 45] },
        { fixture: 'transit_shelter', placement: 'one furnished curbside stop on a representative block', minimumPer100M: 1 },
      ]),
    },
  },
  {
    schemaVersion: 1,
    contractId: 'woonerf_shared_street/woonerf_shared_street_v0',
    archetypeId: 'woonerf_shared_street',
    variantId: 'woonerf_shared_street_v0',
    label: 'Dutch Residential Woonerf',
    scope: 'within_right_of_way',
    target: {
      type: 'segment',
      rowWidthM: 10,
      crossSectionTruth: 'Two 0.4 m flush stone edges, two 1.25 m alternating planter edges and one 6.7 m warm-brick shared surface; no raised curbs.',
    },
    referenceViews: threeViews('woonerf-shared-street'),
    withinRow: {
      required: Object.freeze([
        'single_shared_lane',
        'continuous_flush_surface',
        'herringbone_brick_paving',
        'stone_paving_inlays',
        'flush_stone_edges',
        'chicane_delineation',
        'integrated_planting_beds',
        'raised_tables',
        'play_elements',
        'bollards',
        'benches',
      ]),
      forbidden: Object.freeze([
        'raised_curbs',
        'painted_centerline',
        'standard_lane_markings',
        'separated_sidewalks',
        'parking_stall_markings',
        'traffic_signals',
        'raised_median',
        'parked_vehicles_in_travel_space',
        'trees_in_vehicle_clearance',
      ]),
    },
    surfaces: Object.freeze([
      { role: 'edge', material: 'buffer_stone', description: 'flush natural-stone edge', side: 'bilateral', widthM: 0.4, level: 'flush', markings: 'none' },
      { role: 'planting', material: 'unit_pavers', description: 'permeable paved planter and social edge', side: 'bilateral', widthM: 1.25, level: 'flush', markings: 'none' },
      { role: 'shared', material: 'unit_pavers', description: 'warm red-brown herringbone brick shared surface', side: 'center', widthM: 6.7, level: 'flush', markings: 'none' },
      { role: 'planting', material: 'planting_grass', description: 'punctual integrated planting beds', side: 'punctual', level: 'raised', markings: 'none' },
    ]),
    rhythm: {
      trees: Object.freeze([{
        placement: 'alternating_chicane',
        character: 'small-to-medium deciduous trees integrated with sociable planting rooms',
        spacingM: [14, 22],
        clearanceRule: 'Alternate tree pits across the section while retaining one continuous emergency and walking clear route.',
      }]),
      vehicles: {
        presence: 'sparse',
        placement: 'informal_pockets',
        occupancyRange: [0.05, 0.2],
        rule: 'Cars are guests: use isolated pockets between planters, never a continuous parking row or obstruction of play space.',
      },
      fixtures: Object.freeze([
        { fixture: 'bollard', placement: 'entry thresholds and alternating chicane edges', spacingM: [3, 6] },
        { fixture: 'integrated_planter', placement: 'alternating sides to deflect vehicle movement', spacingM: [12, 20] },
        { fixture: 'bench', placement: 'paired with planting and facing shared social space', spacingM: [20, 35] },
        { fixture: 'play_node', placement: 'visible widening or raised-table node', spacingM: [35, 60] },
      ]),
    },
  },
  {
    schemaVersion: 1,
    contractId: 'yield_street/yield_street_v0',
    archetypeId: 'yield_street',
    variantId: 'yield_street_v0',
    label: 'Dutch Woonerf Yield Street',
    scope: 'within_right_of_way',
    target: {
      type: 'segment',
      rowWidthM: 6,
      crossSectionTruth: 'Two 0.3 m flush edges and one 5.4 m red-brown brick shared surface; no raised curbs.',
    },
    referenceViews: threeViews('yield-street'),
    withinRow: {
      required: Object.freeze([
        'single_shared_lane',
        'continuous_flush_surface',
        'herringbone_brick_paving',
        'flush_stone_edges',
        'chicane_delineation',
        'hydrangea_planters',
        'bollards',
      ]),
      forbidden: Object.freeze([
        'raised_curbs',
        'painted_centerline',
        'standard_lane_markings',
        'separated_sidewalks',
        'parking_stall_markings',
        'traffic_signals',
        'raised_median',
        'parked_vehicles_in_travel_space',
        'trees_in_vehicle_clearance',
      ]),
    },
    surfaces: Object.freeze([
      { role: 'edge', material: 'unit_pavers', description: 'narrow flush unit-paver edge', side: 'bilateral', widthM: 0.3, level: 'flush', markings: 'none' },
      { role: 'shared', material: 'unit_pavers', description: 'red-brown clay brick in herringbone pattern', side: 'center', widthM: 5.4, level: 'flush', markings: 'none' },
      { role: 'planting', material: 'planting_grass', description: 'punctual tree pits and hydrangea planters', side: 'punctual', level: 'raised', markings: 'none' },
    ]),
    rhythm: {
      trees: Object.freeze([{
        placement: 'alternating_chicane',
        character: 'intermittent medium deciduous trees in square beds with hydrangea understory',
        spacingM: [18, 28],
        clearanceRule: 'Trees may pinch the visual corridor but must leave the single yield path continuously passable.',
      }]),
      vehicles: {
        presence: 'sparse',
        placement: 'informal_pockets',
        occupancyRange: [0.05, 0.18],
        rule: 'Use occasional single cars in edge pockets; never place opposing or parked cars side-by-side in the yield path.',
      },
      fixtures: Object.freeze([
        { fixture: 'bollard', placement: 'regular edge cadence and chicane thresholds', spacingM: [3, 5] },
        { fixture: 'hydrangea_planter', placement: 'alternating facade-edge and tree-bed clusters', spacingM: [10, 18] },
        { fixture: 'yield_sign', placement: 'entry threshold only', minimumPer100M: 1 },
      ]),
    },
  },
  {
    schemaVersion: 1,
    contractId: 'roundabout/roundabout_v0',
    archetypeId: 'roundabout',
    variantId: 'roundabout_v0',
    label: 'Classic Tree-Lined Compact Roundabout',
    scope: 'within_right_of_way',
    target: {
      type: 'node',
      armCount: 4,
      inscribedCircleDiameterM: 28,
      crossSectionTruth: 'A 28 m ICD compact roundabout with a 5.5 m single circulatory lane, 1.5 m truck apron, raised planted center and four splitter-island approaches.',
    },
    referenceViews: threeViews('roundabout'),
    withinRow: {
      required: Object.freeze([
        'single_lane_circulatory_ring',
        'truck_apron',
        'landscaped_central_island',
        'splitter_islands',
        'zebra_crosswalks',
        'yield_markings',
        'sidewalk_connections',
        'granite_curbs',
        'mature_deciduous_canopy',
        'ornamental_iron_lamps',
      ]),
      forbidden: Object.freeze([
        'multi_lane_circulatory_ring',
        'traffic_signals',
        'bilateral_parallel_parking',
        'parking_stall_markings',
        'separated_cycle_track',
        'building_in_central_island',
        'palm_tree_palette',
        'modern_stainless_fixtures',
        'parked_vehicles_in_travel_space',
        'trees_in_vehicle_clearance',
      ]),
    },
    surfaces: Object.freeze([
      { role: 'motor', material: 'asphalt', description: 'single dark-asphalt circulatory lane', side: 'radial', widthM: 5.5, level: 'flush', markings: 'crosswalks_and_yield' },
      { role: 'apron', material: 'concrete', description: 'mountable light-concrete truck apron', side: 'radial', widthM: 1.5, level: 'raised', markings: 'none' },
      { role: 'island', material: 'planting_grass', description: 'raised lawn, shrubs and signature tree', side: 'center', level: 'raised', markings: 'none' },
      { role: 'splitter', material: 'concrete', description: 'four raised concrete splitter islands with low planting', side: 'radial', level: 'raised', markings: 'none' },
      { role: 'sidewalk', material: 'concrete', description: 'connected perimeter sidewalks behind crossings', side: 'radial', level: 'raised', markings: 'crosswalks_and_yield' },
      { role: 'edge', material: 'buffer_stone', description: 'granite curb edges', side: 'radial', level: 'raised', markings: 'none' },
    ]),
    rhythm: {
      trees: Object.freeze([
        {
          placement: 'central_island',
          character: 'one dominant mature deciduous signature tree over low ornamental planting',
          count: [1, 1],
          clearanceRule: 'Keep the trunk near island center and all approach sight triangles clear.',
        },
        {
          placement: 'bilateral_regular',
          character: 'mature deciduous approach trees continuing the classic streetscape',
          spacingM: [9, 13],
          clearanceRule: 'Begin beyond crosswalk sight triangles and keep trunks behind perimeter curbs.',
        },
      ]),
      vehicles: {
        presence: 'allowed',
        placement: 'moving_only',
        occupancyRange: [0, 0.2],
        rule: 'Use only sparse moving vehicles in the ring or approaches; no parking in the node.',
      },
      fixtures: Object.freeze([
        { fixture: 'ornamental_iron_lamp', placement: 'paired behind each approach crosswalk', minimumPer100M: 4 },
        { fixture: 'yield_sign', placement: 'one at each entry behind the yield line', minimumPer100M: 4 },
      ]),
    },
  },
] satisfies StreetVisualContract[]);

function canonicalVisualId(value: unknown): string {
  return typeof value === 'string'
    ? value.trim().toLowerCase().replace(/[\s-]+/g, '_')
    : '';
}

export function streetVisualContractKey(archetypeId: unknown, variantId: unknown): string {
  return `${canonicalVisualId(archetypeId)}/${canonicalVisualId(variantId)}`;
}

const STREET_VISUAL_CONTRACT_BY_KEY = new Map(
  STREET_VISUAL_CONTRACTS.map((contract) => [
    streetVisualContractKey(contract.archetypeId, contract.variantId),
    contract,
  ]),
);

/** Resolve an exact catalog selection; broad archetype-only requests fail closed. */
export function resolveStreetVisualContract(
  archetypeId: unknown,
  variantId: unknown,
): StreetVisualContract | null {
  if (!canonicalVisualId(archetypeId) || !canonicalVisualId(variantId)) return null;
  return STREET_VISUAL_CONTRACT_BY_KEY.get(
    streetVisualContractKey(archetypeId, variantId),
  ) ?? null;
}
