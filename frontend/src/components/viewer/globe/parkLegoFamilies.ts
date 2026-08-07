import {
  archetypeOwnedParkKitForFamily,
  archetypeOwnedParkKitForSelection,
} from './parkArchetypeOwnedKits';
import { batch4ParkSkinForSelection } from './parkBatch4Skins';
import { batch5ParkSkinForSelection } from './parkBatch5Skins';
import { batch6ParkSkinForSelection } from './parkBatch6Skins';
import { batch7ParkSkinForSelection } from './parkBatch7Skins';
import { batch8ParkSkinForSelection } from './parkBatch8Skins';
import { batch9ParkSkinForSelection } from './parkBatch9Skins';
import { batch10ParkSkinForSelection } from './parkBatch10Skins';
import { batch11ParkSkinForSelection } from './parkBatch11Skins';
import { batch12ParkSkinForSelection } from './parkBatch12Skins';
import { batch13ParkSkinForSelection } from './parkBatch13Skins';
import { batch14ParkSkinForSelection } from './parkBatch14Skins';
import { batch15ParkSkinForSelection } from './parkBatch15Skins';
import { batch16ParkSkinForSelection } from './parkBatch16Skins';
import { batch17ParkSkinForSelection } from './parkBatch17Skins';
import { batch18ParkSkinForSelection } from './parkBatch18Skins';
import { batch19ParkSkinForSelection } from './parkBatch19Skins';
import { batch20ParkSkinForSelection } from './parkBatch20Skins';
import { batch21ParkSkinForSelection } from './parkBatch21Skins';
import { batch22ParkSkinForSelection } from './parkBatch22Skins';
import { batch23ParkSkinForSelection } from './parkBatch23Skins';
import { batch24ParkSkinForSelection } from './parkBatch24Skins';
import { batch25ParkSkinForSelection } from './parkBatch25Skins';
import { batch26ParkSkinForSelection } from './parkBatch26Skins';
import { batch27ParkSkinForSelection } from './parkBatch27Skins';

/** Public Realm LEGO V1 park families. These ids are shared with the backend
 * capability contract and are deliberately separate from catalog archetype
 * ids: one executable family can serve more than one compatible archetype. */
export const PARK_LEGO_FAMILY_VERSION = 1 as const;

export const PARK_LEGO_FAMILY_IDS = [
  'park_pocket_courtyard',
  'park_neighborhood_community',
  'park_civic_plaza',
  'park_linear_greenway',
  'park_skate_archetype_v0',
  'park_inclusive_playground_v0',
  'park_dog_archetype_v0',
  'park_splash_pad_v0',
  'park_community_garden_v0',
  'park_basketball_court_v0',
  'park_tennis_cluster_v0',
  'park_caged_soccer_v0',
  'park_athletics_fields_v0',
  'park_nature_play_v0',
  'park_pump_track_v0',
  'park_outdoor_fitness_v0',
  'park_memorial_garden_v0',
  'park_pickleball_community_v1',
  'park_track_oval_school_v2',
  'park_baseball_club_hub_v1',
  'park_cricket_village_green_v0',
  'park_sports_complex_tournament_v0',
  'park_water_ecology',
  'park_cultural_gardens',
  'park_urban_forest',
  'park_amphitheater_lawn_v0',
  'park_playground_adventure_v0',
  'park_disc_golf_wooded_v0',
  'park_bocce_piazza_v0',
  'park_climbing_competition_v0',
  'park_mini_golf_classic_v0',
  'park_beach_volleyball_competition_v0',
  'park_pollinator_prairie_v0',
  'park_orchard_heritage_v0',
  'park_bioswale_streetside_v0',
  'park_sculpture_museum_court_v0',
  'park_labyrinth_classical_v0',
  'park_ice_rink_multipurpose_v3',
  'park_kayak_river_launch_v0',
  'park_tidal_marsh_cordgrass_v0',
  'park_cinema_lawn_projection_v1',
  'park_food_truck_permanent_v1',
  'park_great_lawn_v2',
  'park_campus_meadow_quad_v0',
  'park_urban_beach_family_v2',
  'park_velodrome_open_air_v0',
  'park_mtb_skills_dirt_v2',
  'park_regional_english_landscape_v0',
  'park_beer_garden_munich_v0',
  'park_sunken_courtyard_v0',
  'park_terraced_cascade_v3',
  'park_market_festival_lawn_v1',
  'park_boardwalk_maritime_v0',
  'park_fountain_formal_pool_v1',
  'park_natural_swimming_pond_v0',
  'park_nature_preserve_prairie_v1',
  'park_riverfront_lake_beach_v1',
  'park_reclaimed_wharf_v0',
  'park_quarry_tier_cascade_v2',
  'park_estate_oak_picnic_v1',
  'park_constructed_wetland_boardwalk_v0',
  'park_academic_planted_court_v0',
  'park_campus_green_spine_v0',
  'park_botanical_rose_garden_v3',
  'park_research_arboretum_v0',
  'park_rewilding_reforestation_v1',
  'park_stormwater_arid_channel_v3',
  'park_urban_pocket_rustic_v0',
  'park_neighborhood_contemporary_v3',
  'park_cemetery_classical_v0',
  'park_courtyard_linear_water_v1',
  'park_parklet_sf_timber_v1',
  'park_french_parterre_axis_v1',
  'park_london_railed_square_v1',
  'park_halifax_rose_bandstand_v0',
  'park_olmsted_multilandscape_v3',
  'park_hilltop_viewpoint_v3',
  'park_amsterdam_hofje_garden_v0',
  'park_amsterdam_plein_v0',
  'park_amsterdam_vondelpark_pavilion_v3',
  'park_barcelona_pati_green_v0',
  'park_barcelona_xamfra_corner_v2',
  'park_barcelona_superilla_green_v1',
  'park_calgary_prairie_market_v1',
  'park_calgary_princes_island_festival_v0',
  'park_montreal_mount_royal_grove_v2',
  'park_montreal_neighbourhood_square_v3',
  'park_paris_place_royale_v2',
  'park_paris_square_tree_grid_v3',
  'park_london_circus_planted_v1',
  'park_newyork_pocket_water_v0',
  'park_newyork_community_greenhouse_v3',
  'park_vancouver_seawall_cycle_v2',
  'park_vancouver_beach_pavilion_v0',
  'park_toronto_ravine_creek_v1',
  'park_toronto_urban_market_v1',
  'park_halifax_coastal_fog_path_v2',
  'park_city_hall_modernist_fountain_v2',
  'park_cathedral_courtyard_fountain_v3',
  'park_cultural_museum_terrace_v0',
  'park_transit_green_civic_v2',
  'park_amphitheater_terraced_v0',
  'park_concert_timber_lawn_v2',
  'park_night_market_hawker_v0',
  'park_parade_national_mall_v3',
  'park_canal_ecological_wetland_v3',
  'park_custom_biophilic_urban_v1',
  'park_rooftop_intensive_garden_v0',
  'park_community_healing_garden_v2',
  'park_greenbelt_rail_trail_v1',
  'park_foothill_heathland_trail_v2',
  'park_marina_pacific_dock_v2',
  'park_working_pier_brooklyn_park_v3',
  'park_floating_meadow_loop_v2',
  'park_lighthouse_pacific_headland_v2',
  'park_lake_edge_timber_deck_v2',
  'park_stormwater_natural_creek_v0',
  'park_surface_parking_standard_v0',
  'park_structured_parking_urban_v2',
  'park_underground_parking_green_v1',
  'park_green_parking_infrastructure_v1',
  'park_airport_general_aviation_v2',
  'park_equestrian_working_stable_v1',
  'park_golf_seaside_links_v0',
  'park_driving_range_single_tier_v0',
  'park_multi_sport_track_field_v3',
  'park_retail_parking_landscaped_v1',
] as const;

export type ParkLegoFamilyId = (typeof PARK_LEGO_FAMILY_IDS)[number];
export type ParkLegoPlantingStructure =
  | 'garden_courtyard'
  | 'formal_quad'
  | 'naturalistic_grove'
  | 'open_meadow'
  | 'active_recreation';
export type ParkLegoMaterialPattern =
  | 'rustic_gravel'
  | 'modern_turf'
  | 'native_meadow'
  | 'urban_pavers'
  | 'english_pastoral'
  | 'modern_minimal'
  | 'mediterranean_xeriscape'
  | 'tropical_lush';
export type ParkLegoPlaygroundStyle = 'timber' | 'steel' | 'nature' | 'contemporary';
export type ParkLegoShadeStyle = 'timber_pergola' | 'fabric_sail' | 'steel_canopy' | 'thatched';

export interface ParkLegoPalette {
  ground: string;
  lawn: string;
  meadow: string;
  path: string;
  pathEdge: string;
  playSurface: string;
  pavilionPad: string;
  timber: string;
  timberDark: string;
  metal: string;
  accent: string;
  accentSecondary: string;
  shade: string;
  pavilionRoof: string;
  benchSeat: string;
  benchFrame: string;
}

export interface ParkLegoAppearance {
  familyId: ParkLegoFamilyId;
  familyVersion: typeof PARK_LEGO_FAMILY_VERSION;
  archetypeId: string;
  variantId: string;
  variantIndex: number;
  label: string;
  plantingStructure: ParkLegoPlantingStructure;
  materialPattern: ParkLegoMaterialPattern;
  playgroundStyle: ParkLegoPlaygroundStyle;
  shadeStyle: ParkLegoShadeStyle;
  palette: ParkLegoPalette;
}

export interface ParkLegoContract {
  familyId: ParkLegoFamilyId;
  familyVersion: number;
  archetypeId: string;
  variantId: string;
  source: 'public_realm_lego' | 'legacy';
  supported: boolean;
  schemaVersion?: number;
  kind?: string;
  generator?: string;
  plantingStructure?: string;
  appearanceKitId?: string;
  catalogFingerprint?: string;
  capabilityFingerprint?: string;
  recipeHash?: string;
}

export interface ParkProgramModuleSpec {
  playground: {
    safetyDiameterM: number;
    towerDeckM: readonly [number, number, number];
    towerHeightM: number;
    slideLengthM: number;
    swingBayM: readonly [number, number, number];
  };
  shade: {
    spanM: number;
    lowEdgeHeightM: number;
    highEdgeHeightM: number;
  };
  pavilion: {
    widthM: number;
    depthM: number;
    clearHeightM: number;
    roofHeightM: number;
  };
}

export interface ParkProgramAnchorLayout {
  /** Normalized coordinates in the park's oriented program frame. */
  playground?: readonly [number, number];
  pavilion?: readonly [number, number];
}

export const CIVIC_FOUNTAIN_ASSEMBLY_SPEC = Object.freeze({
  outerRadiusM: 4.8,
  waterRadiusM: 3.9,
  rimHeightM: 0.32,
  waterHeightM: 0.24,
  centerPlinthRadiusM: 0.72,
  centerPlinthHeightM: 0.62,
  wholeElementClearanceM: 6,
});

/** Metric program is invariant across appearance variants. A selected visual
 * style may recolour or reshape finishes, but never scales equipment with the
 * parcel or changes its safety envelope. */
export const PARK_PROGRAM_MODULE_SPEC: Readonly<ParkProgramModuleSpec> = Object.freeze({
  playground: Object.freeze({
    safetyDiameterM: 12,
    towerDeckM: Object.freeze([2.2, 2.2, 0.28] as const),
    towerHeightM: 3.2,
    slideLengthM: 3.4,
    swingBayM: Object.freeze([3.8, 2.4, 2.5] as const),
  }),
  shade: Object.freeze({
    spanM: 7.2,
    lowEdgeHeightM: 3.0,
    highEdgeHeightM: 3.7,
  }),
  pavilion: Object.freeze({
    widthM: 6,
    depthM: 5,
    clearHeightM: 2.8,
    roofHeightM: 1.15,
  }),
});

export const NEIGHBORHOOD_COMMUNITY_PROGRAM_ANCHORS: Readonly<ParkProgramAnchorLayout> = Object.freeze({
  playground: Object.freeze([0.82, 0.22] as const),
  pavilion: Object.freeze([0.77, 0.58] as const),
});

type ParkLegoZone = {
  properties?: unknown;
  zone_type?: string;
};

interface AppearanceDefinition {
  label: string;
  plantingStructure: ParkLegoPlantingStructure;
  materialPattern: ParkLegoMaterialPattern;
  playgroundStyle: ParkLegoPlaygroundStyle;
  shadeStyle: ParkLegoShadeStyle;
  palette: ParkLegoPalette;
}

const RUSTIC: ParkLegoPalette = {
  ground: '#6f805c',
  lawn: '#7fa45f',
  meadow: '#7c8d58',
  path: '#a88f68',
  pathEdge: '#77654d',
  playSurface: '#c3a36d',
  pavilionPad: '#837668',
  timber: '#9a6a3e',
  timberDark: '#66442d',
  metal: '#3d4545',
  accent: '#b65337',
  accentSecondary: '#d39a43',
  shade: '#d2bd89',
  pavilionRoof: '#765842',
  benchSeat: '#8a5c38',
  benchFrame: '#343a39',
};

const MODERN: ParkLegoPalette = {
  ground: '#6c845f',
  lawn: '#6f9a64',
  meadow: '#718369',
  path: '#a5a8a3',
  pathEdge: '#707876',
  playSurface: '#8a726d',
  pavilionPad: '#8d918e',
  timber: '#9d815f',
  timberDark: '#685744',
  metal: '#4c5c5b',
  accent: '#d66045',
  accentSecondary: '#e0b64f',
  shade: '#d7d6c8',
  pavilionRoof: '#697674',
  benchSeat: '#9b8060',
  benchFrame: '#364344',
};

const MEADOW: ParkLegoPalette = {
  ground: '#788259',
  lawn: '#83a263',
  meadow: '#96935a',
  path: '#aa9368',
  pathEdge: '#786b4e',
  playSurface: '#b58f59',
  pavilionPad: '#887b69',
  timber: '#8a633d',
  timberDark: '#5b442e',
  metal: '#48514b',
  accent: '#9d6940',
  accentSecondary: '#d2b45e',
  shade: '#c8a862',
  pavilionRoof: '#776047',
  benchSeat: '#806043',
  benchFrame: '#3e4741',
};

const CONTEMPORARY: ParkLegoPalette = {
  ground: '#687b69',
  lawn: '#739c6b',
  meadow: '#75866a',
  path: '#969b98',
  pathEdge: '#5f6c6d',
  playSurface: '#927168',
  pavilionPad: '#858b89',
  timber: '#ad845b',
  timberDark: '#6c543e',
  metal: '#34464d',
  accent: '#ce583e',
  accentSecondary: '#4f8ca3',
  shade: '#d9c966',
  pavilionRoof: '#53666a',
  benchSeat: '#9f7856',
  benchFrame: '#2f4147',
};

const PASTORAL: ParkLegoPalette = {
  ...RUSTIC,
  ground: '#71845e',
  lawn: '#83a965',
  meadow: '#849369',
  path: '#b0a078',
  pavilionRoof: '#6f5542',
};

const XERISCAPE: ParkLegoPalette = {
  ...MEADOW,
  ground: '#938968',
  lawn: '#839263',
  meadow: '#a69667',
  path: '#b19a70',
  pathEdge: '#806a4c',
  playSurface: '#b7775a',
  pavilionPad: '#9c876c',
  accent: '#ba5f42',
  shade: '#d3b270',
  pavilionRoof: '#a56647',
};

const TROPICAL: ParkLegoPalette = {
  ...CONTEMPORARY,
  ground: '#4f7659',
  lawn: '#5c9362',
  meadow: '#4e7858',
  path: '#9b8062',
  pathEdge: '#5f5142',
  playSurface: '#a76651',
  pavilionPad: '#81715e',
  timber: '#8b603c',
  timberDark: '#4f3728',
  shade: '#b49357',
  pavilionRoof: '#86683f',
};

const POCKET_VARIANTS: readonly AppearanceDefinition[] = Object.freeze([
  {
    label: 'Rustic Timber & Gravel',
    plantingStructure: 'garden_courtyard',
    materialPattern: 'rustic_gravel',
    playgroundStyle: 'timber',
    shadeStyle: 'timber_pergola',
    palette: RUSTIC,
  },
  {
    label: 'Modern Steel & Turf',
    plantingStructure: 'formal_quad',
    materialPattern: 'modern_turf',
    playgroundStyle: 'steel',
    shadeStyle: 'steel_canopy',
    palette: MODERN,
  },
  {
    label: 'Natural Meadow',
    plantingStructure: 'naturalistic_grove',
    materialPattern: 'native_meadow',
    playgroundStyle: 'nature',
    shadeStyle: 'timber_pergola',
    palette: MEADOW,
  },
  {
    label: 'Urban Contemporary',
    plantingStructure: 'garden_courtyard',
    materialPattern: 'urban_pavers',
    playgroundStyle: 'contemporary',
    shadeStyle: 'fabric_sail',
    palette: CONTEMPORARY,
  },
]);

const NEIGHBORHOOD_VARIANTS: readonly AppearanceDefinition[] = Object.freeze([
  {
    ...POCKET_VARIANTS[0],
    plantingStructure: 'active_recreation',
  },
  {
    ...POCKET_VARIANTS[1],
    plantingStructure: 'active_recreation',
  },
  {
    ...POCKET_VARIANTS[2],
    plantingStructure: 'naturalistic_grove',
  },
  {
    ...POCKET_VARIANTS[3],
    plantingStructure: 'active_recreation',
  },
]);

const COMMUNITY_VARIANTS: readonly AppearanceDefinition[] = Object.freeze([
  {
    label: 'English Pastoral',
    plantingStructure: 'naturalistic_grove',
    materialPattern: 'english_pastoral',
    playgroundStyle: 'timber',
    shadeStyle: 'timber_pergola',
    palette: PASTORAL,
  },
  {
    label: 'Modern Minimalist',
    plantingStructure: 'active_recreation',
    materialPattern: 'modern_minimal',
    playgroundStyle: 'steel',
    shadeStyle: 'steel_canopy',
    palette: MODERN,
  },
  {
    label: 'Mediterranean Xeriscape',
    plantingStructure: 'naturalistic_grove',
    materialPattern: 'mediterranean_xeriscape',
    playgroundStyle: 'nature',
    shadeStyle: 'fabric_sail',
    palette: XERISCAPE,
  },
  {
    label: 'Tropical Lush',
    plantingStructure: 'naturalistic_grove',
    materialPattern: 'tropical_lush',
    playgroundStyle: 'timber',
    shadeStyle: 'thatched',
    palette: TROPICAL,
  },
]);

/** Appearance-only kits for cricket variants that do not yet claim a full
 * compiler family. The dedicated cricket assembly owns the playable program;
 * these definitions only select compatible perimeter trees, benches and
 * materials after the drape is complete. */
const CRICKET_DRESSING_VARIANTS: readonly AppearanceDefinition[] = Object.freeze([
  {
    label: 'Village Green',
    plantingStructure: 'naturalistic_grove',
    materialPattern: 'english_pastoral',
    playgroundStyle: 'timber',
    shadeStyle: 'thatched',
    palette: PASTORAL,
  },
  {
    label: 'Municipal Oval',
    plantingStructure: 'active_recreation',
    materialPattern: 'modern_minimal',
    playgroundStyle: 'steel',
    shadeStyle: 'steel_canopy',
    palette: MODERN,
  },
  {
    label: 'South Asian Ground',
    plantingStructure: 'open_meadow',
    materialPattern: 'urban_pavers',
    playgroundStyle: 'contemporary',
    shadeStyle: 'fabric_sail',
    palette: CONTEMPORARY,
  },
  {
    label: 'Caribbean Beach Pitch',
    plantingStructure: 'open_meadow',
    materialPattern: 'tropical_lush',
    playgroundStyle: 'timber',
    shadeStyle: 'thatched',
    palette: TROPICAL,
  },
]);

interface ParkSelectionMapping {
  variantId: string;
  appearanceKitId: string;
  plantingStructure: string;
}

function fourVariantMappings(
  archetypeId: string,
  appearanceKitIds: readonly string[],
  plantingStructures: readonly string[],
): readonly ParkSelectionMapping[] {
  return Object.freeze(appearanceKitIds.map((appearanceKitId, index) => Object.freeze({
    variantId: `${archetypeId}_v${index}`,
    appearanceKitId,
    plantingStructure: plantingStructures[index],
  })));
}

function fourNamedVariantMappings(
  archetypeId: string,
  appearanceKitIds: readonly string[],
  plantingStructures: readonly string[],
): readonly ParkSelectionMapping[] {
  return Object.freeze(appearanceKitIds.map((appearanceKitId, index) => Object.freeze({
    variantId: `${archetypeId}_variant_${index}`,
    appearanceKitId,
    plantingStructure: plantingStructures[index],
  })));
}

/** Exact frontend mirror of the backend's executable park-family
 * selections. Nested recipes are never repaired here: incompatible identities
 * remain unsupported so the live scene cannot claim a different program than
 * the compiler persisted. */
const PARK_FAMILY_SELECTIONS: Readonly<
  Record<ParkLegoFamilyId, Readonly<Record<string, readonly ParkSelectionMapping[]>>>
> = Object.freeze({
  park_pocket_courtyard: Object.freeze({
    urban_pocket_park: fourVariantMappings(
      'urban_pocket_park',
      ['rustic_timber_gravel_v1', 'modern_steel_turf_v1', 'natural_meadow_v1', 'urban_contemporary_v1'],
      ['garden_courtyard', 'formal_quad', 'naturalistic_grove', 'garden_courtyard'],
    ),
  }),
  park_neighborhood_community: Object.freeze({
    neighborhood_park: fourVariantMappings(
      'neighborhood_park',
      ['rustic_timber_gravel_v1', 'modern_steel_turf_v1', 'natural_meadow_v1', 'urban_contemporary_v1'],
      ['active_recreation', 'active_recreation', 'naturalistic_grove', 'active_recreation'],
    ),
    community_park: fourVariantMappings(
      'community_park',
      ['english_pastoral_v1', 'community_park_v1_modern_minimalist_skin', 'community_park_v2_mediterranean_xeriscape_skin', 'community_park_v3_tropical_lush_skin'],
      ['naturalistic_grove', 'community_modern_minimalist_v1', 'community_mediterranean_xeriscape_v2', 'community_tropical_lush_v3'],
    ),
  }),
  park_civic_plaza: Object.freeze({
    formal_civic_plaza: fourVariantMappings(
      'formal_civic_plaza',
      ['neoclassical_stone_v1', 'formal_civic_plaza_v1_contemporary_urban_skin', 'formal_civic_plaza_v2_green_civic_skin', 'formal_civic_plaza_v3_festival_market_skin'],
      ['paved_plaza', 'formal_civic_contemporary_v1', 'formal_civic_green_v2', 'formal_civic_festival_v3'],
    ),
  }),
  park_linear_greenway: Object.freeze({
    linear_park_greenway: fourVariantMappings(
      'linear_park_greenway',
      ['rail_trail_v1', 'linear_park_greenway_v1_riverfront_skin', 'linear_park_greenway_v2_daylighted_creek_skin', 'linear_park_greenway_v3_elevated_viaduct_skin'],
      ['naturalistic_grove', 'linear_riverfront_v1', 'linear_daylighted_creek_v2', 'linear_elevated_viaduct_v3'],
    ),
  }),
  park_skate_archetype_v0: Object.freeze({
    skate_park: fourVariantMappings(
      'skate_park',
      ['skate_park_v0_reference_skin', 'skate_park_v1_community_recreation_skin', 'skate_park_v2_naturalized_active_skin', 'skate_park_v3_urban_athletic_skin'],
      ['skate_archetype_v0', 'skate_community_recreation_v1', 'skate_naturalized_active_v2', 'skate_urban_athletic_v3'],
    ),
  }),
  park_inclusive_playground_v0: Object.freeze({
    inclusive_playground: fourVariantMappings(
      'inclusive_playground',
      ['inclusive_playground_v0_reference_skin', 'inclusive_playground_v1_sensory_skin', 'inclusive_playground_v2_mega_skin', 'inclusive_playground_v3_nature_skin'],
      ['inclusive_playground_v0', 'inclusive_sensory_v1', 'inclusive_mega_v2', 'inclusive_nature_v3'],
    ),
  }),
  park_dog_archetype_v0: Object.freeze({
    dog_park: fourVariantMappings(
      'dog_park',
      ['dog_park_v0_reference_skin', 'dog_park_v1_modern_steel_turf_skin', 'dog_park_v2_natural_meadow_skin', 'dog_park_v3_urban_contemporary_skin'],
      ['dog_park_v0', 'dog_modern_steel_turf_v1', 'dog_natural_meadow_v2', 'dog_urban_contemporary_v3'],
    ),
  }),
  park_splash_pad_v0: Object.freeze({
    splash_pad_area: fourVariantMappings(
      'splash_pad_area',
      ['splash_pad_area_v0_reference_skin', 'splash_pad_area_v1_modern_skin', 'splash_pad_area_v2_meadow_skin', 'splash_pad_area_v3_urban_skin'],
      ['splash_pad_area_v0', 'splash_pad_modern_v1', 'splash_pad_meadow_v2', 'splash_pad_urban_v3'],
    ),
  }),
  park_community_garden_v0: Object.freeze({
    community_garden: fourVariantMappings(
      'community_garden',
      ['community_garden_v0_reference_skin', 'community_garden_v1_modern_steel_turf_skin', 'community_garden_v2_natural_meadow_skin', 'community_garden_v3_urban_contemporary_skin'],
      ['community_garden_v0', 'community_garden_modern_v1', 'community_garden_meadow_v2', 'community_garden_urban_v3'],
    ),
  }),
  park_basketball_court_v0: Object.freeze({
    basketball_court: Object.freeze([
      Object.freeze({
        variantId: 'basketball_court_v0', appearanceKitId: 'basketball_court_v0_classic_asphalt_skin', plantingStructure: 'basketball_classic_v0',
      }),
      Object.freeze({
        variantId: 'basketball_court_v1', appearanceKitId: 'basketball_court_v1_pro_acrylic_skin', plantingStructure: 'basketball_pro_v1',
      }),
      Object.freeze({
        variantId: 'basketball_court_v2', appearanceKitId: 'basketball_court_v2_half_court_mural_skin', plantingStructure: 'basketball_half_court_v2',
      }),
      Object.freeze({
        variantId: 'basketball_court_v3', appearanceKitId: 'basketball_court_v3_streetball_skin', plantingStructure: 'basketball_streetball_v3',
      }),
    ]),
  }),
  park_tennis_cluster_v0: Object.freeze({
    tennis_court_cluster: fourVariantMappings(
      'tennis_court_cluster',
      ['tennis_court_cluster_v0_reference_skin', 'tennis_court_cluster_v1_community_recreation_skin', 'tennis_court_cluster_v2_naturalized_active_skin', 'tennis_court_cluster_v3_urban_athletic_skin'],
      ['tennis_court_cluster_v0', 'tennis_community_v1', 'tennis_naturalized_v2', 'tennis_urban_v3'],
    ),
  }),
  park_caged_soccer_v0: Object.freeze({
    soccer_pitch_caged: fourVariantMappings(
      'soccer_pitch_caged',
      ['soccer_pitch_caged_v0_reference_skin', 'soccer_pitch_caged_v1_community_skin', 'soccer_pitch_caged_v2_youth_training_skin', 'soccer_pitch_caged_v3_rooftop_skin'],
      ['caged_soccer_v0', 'caged_soccer_community_v1', 'caged_soccer_youth_v2', 'caged_soccer_rooftop_v3'],
    ),
  }),
  park_athletics_fields_v0: Object.freeze({
    athletics_precinct_sports_fields: fourNamedVariantMappings(
      'athletics_precinct_sports_fields',
      ['athletics_precinct_sports_fields_v0_reference_skin', 'athletics_precinct_sports_fields_v1_university_grandstand_skin', 'athletics_precinct_sports_fields_v2_campus_precinct_skin', 'athletics_precinct_sports_fields_v3_open_oval_skin'],
      ['athletics_fields_v0', 'athletics_university_v1', 'athletics_campus_v2', 'athletics_open_oval_v3'],
    ),
  }),
  park_nature_play_v0: Object.freeze({
    nature_play_area: fourVariantMappings(
      'nature_play_area',
      ['nature_play_area_v0_reference_skin', 'nature_play_area_v1_sensory_garden_skin', 'nature_play_area_v2_mud_water_skin', 'nature_play_area_v3_toddler_garden_skin'],
      ['nature_play_area_v0', 'nature_play_sensory_v1', 'nature_play_mud_water_v2', 'nature_play_toddler_v3'],
    ),
  }),
  park_pump_track_v0: Object.freeze({
    pump_track: fourVariantMappings(
      'pump_track',
      ['pump_track_v0_reference_skin', 'pump_track_v1_dirt_bmx_skin', 'pump_track_v2_family_skin', 'pump_track_v3_modular_skin'],
      ['pump_track_v0', 'pump_track_dirt_v1', 'pump_track_family_v2', 'pump_track_modular_v3'],
    ),
  }),
  park_outdoor_fitness_v0: Object.freeze({
    outdoor_fitness_circuit: fourVariantMappings(
      'outdoor_fitness_circuit',
      ['outdoor_fitness_circuit_v0_reference_skin', 'outdoor_fitness_circuit_v1_parkour_skin', 'outdoor_fitness_circuit_v2_nature_trail_skin', 'outdoor_fitness_circuit_v3_senior_wellness_skin'],
      ['outdoor_fitness_circuit_v0', 'fitness_parkour_v1', 'fitness_nature_trail_v2', 'fitness_senior_v3'],
    ),
  }),
  park_memorial_garden_v0: Object.freeze({
    memorial_garden: fourVariantMappings(
      'memorial_garden',
      ['memorial_garden_v0_reference_skin', 'memorial_garden_v1_woodland_naturalistic_skin', 'memorial_garden_v2_contemporary_sculptural_skin', 'memorial_garden_v3_cottage_romantic_skin'],
      ['memorial_garden_v0', 'memorial_woodland_v1', 'memorial_sculptural_v2', 'memorial_romantic_v3'],
    ),
  }),
  park_pickleball_community_v1: Object.freeze({
    pickleball_courts: fourVariantMappings(
      'pickleball_courts',
      ['pickleball_courts_v0_competition_grade_skin', 'pickleball_courts_v1_multi_angle_skin', 'pickleball_courts_v2_park_integrated_skin', 'pickleball_courts_v3_indoor_outdoor_skin'],
      ['pickleball_competition_v0', 'pickleball_community_v1', 'pickleball_park_integrated_v2', 'pickleball_hybrid_v3'],
    ),
  }),
  park_track_oval_school_v2: Object.freeze({
    running_track_oval: fourVariantMappings(
      'running_track_oval',
      ['running_track_oval_v0_competition_skin', 'running_track_oval_v1_community_skin', 'running_track_oval_v2_multi_angle_skin', 'running_track_oval_v3_park_loop_skin'],
      ['track_competition_v0', 'track_community_v1', 'track_oval_school_v2', 'track_park_loop_v3'],
    ),
  }),
  park_baseball_club_hub_v1: Object.freeze({
    baseball_softball_diamond: fourVariantMappings(
      'baseball_softball_diamond',
      ['baseball_softball_diamond_v0_classic_skin', 'baseball_softball_diamond_v1_multi_angle_skin', 'baseball_softball_diamond_v2_softball_skin', 'baseball_softball_diamond_v3_sandlot_skin'],
      ['baseball_classic_v0', 'baseball_club_hub_v1', 'baseball_softball_v2', 'baseball_sandlot_v3'],
    ),
  }),
  park_cricket_village_green_v0: Object.freeze({
    cricket_pitch_oval: fourVariantMappings(
      'cricket_pitch_oval',
      ['cricket_pitch_oval_v0_multi_angle_skin', 'cricket_pitch_oval_v1_municipal_skin', 'cricket_pitch_oval_v2_south_asian_skin', 'cricket_pitch_oval_v3_caribbean_skin'],
      ['cricket_village_green_v0', 'cricket_municipal_v1', 'cricket_south_asian_v2', 'cricket_caribbean_v3'],
    ),
  }),
  park_sports_complex_tournament_v0: Object.freeze({
    sports_field_complex: fourVariantMappings(
      'sports_field_complex',
      ['sports_field_complex_v0_multi_angle_skin', 'sports_field_complex_v1_community_recreation_skin', 'sports_field_complex_v2_naturalized_active_skin', 'sports_field_complex_v3_urban_athletic_skin'],
      ['sports_complex_tournament_v0', 'sports_complex_community_v1', 'sports_complex_naturalized_v2', 'sports_complex_urban_v3'],
    ),
  }),
  park_water_ecology: Object.freeze({
    stormwater_retention_pond: fourVariantMappings(
      'stormwater_retention_pond',
      ['naturalistic_pond_v1', 'stormwater_retention_pond_v1_formal_reflecting_skin', 'stormwater_retention_pond_v2_contemporary_interactive_skin', 'stormwater_retention_pond_v3_ecological_wetland_skin'],
      ['reservoir_perimeter', 'stormwater_formal_reflecting_v1', 'stormwater_interactive_v2', 'stormwater_ecological_wetland_v3'],
    ),
    pond_lake: Object.freeze([Object.freeze({
      variantId: 'pond_lake_v0', appearanceKitId: 'pond_lake_v0_naturalistic_skin', plantingStructure: 'pond_lake_v0',
    }), Object.freeze({ variantId: 'pond_lake_v1', appearanceKitId: 'pond_lake_v1_formal_reflecting_skin', plantingStructure: 'pond_formal_v1' }), Object.freeze({ variantId: 'pond_lake_v2', appearanceKitId: 'pond_lake_v2_contemporary_interactive_skin', plantingStructure: 'pond_interactive_v2' }), Object.freeze({ variantId: 'pond_lake_v3', appearanceKitId: 'pond_lake_v3_ecological_wetland_skin', plantingStructure: 'pond_wetland_v3' })]),
    wetland_rain_garden: fourVariantMappings(
      'wetland_rain_garden',
      ['wetland_rain_garden_v0_native_restoration_skin', 'wetland_rain_garden_v1_bioengineered_skin', 'wetland_rain_garden_v2_rewilded_urban_skin', 'wetland_rain_garden_v3_resilient_coastal_skin'],
      ['wetland_rain_garden_v0', 'wetland_bioengineered_v1', 'wetland_rewilded_v2', 'wetland_coastal_v3'],
    ),
    riparian_buffer: fourVariantMappings(
      'riparian_buffer',
      ['riparian_buffer_v0_native_restoration_skin', 'riparian_buffer_v1_bioengineered_skin', 'riparian_buffer_v2_rewilded_urban_skin', 'riparian_buffer_v3_resilient_coastal_skin'],
      ['riparian_buffer_v0', 'riparian_bioengineered_v1', 'riparian_rewilded_v2', 'riparian_coastal_v3'],
    ),
    reservoir_watershed_park: Object.freeze([Object.freeze({
      variantId: 'reservoir_watershed_park_v0', appearanceKitId: 'reservoir_watershed_park_v0_concrete_edge_skin', plantingStructure: 'reservoir_watershed_park_v0',
    }), Object.freeze({ variantId: 'reservoir_watershed_park_v1', appearanceKitId: 'reservoir_watershed_park_v1_stone_bank_skin', plantingStructure: 'reservoir_stone_bank_v1' }), Object.freeze({ variantId: 'reservoir_watershed_park_v2', appearanceKitId: 'reservoir_watershed_park_v2_forested_skin', plantingStructure: 'reservoir_forested_v2' }), Object.freeze({ variantId: 'reservoir_watershed_park_v3', appearanceKitId: 'reservoir_watershed_park_v3_earthen_dam_skin', plantingStructure: 'reservoir_earthen_dam_v3' })]),
  }),
  park_cultural_gardens: Object.freeze({
    japanese_garden: fourVariantMappings(
      'japanese_garden',
      ['japanese_garden_v0_stroll_skin', 'japanese_garden_v1_woodland_naturalistic_skin', 'japanese_garden_v2_contemporary_sculptural_skin', 'japanese_garden_v3_cottage_romantic_skin'],
      ['japanese_garden_v0', 'japanese_woodland_v1', 'japanese_sculptural_v2', 'japanese_romantic_v3'],
    ),
    botanical_garden: Object.freeze([
      Object.freeze({ variantId: 'botanical_garden_v0', appearanceKitId: 'botanical_garden_v0_collection_skin', plantingStructure: 'botanical_garden_v0' }),
      Object.freeze({ variantId: 'botanical_garden_v1', appearanceKitId: 'botanical_garden_v1_woodland_naturalistic_skin', plantingStructure: 'botanical_woodland_v1' }),
      Object.freeze({ variantId: 'botanical_garden_v2', appearanceKitId: 'botanical_garden_v2_contemporary_sculptural_skin', plantingStructure: 'botanical_sculptural_v2' }),
    ]),
  }),
  park_urban_forest: Object.freeze({
    urban_forest: fourVariantMappings(
      'urban_forest',
      ['urban_forest_v0_native_restoration_skin', 'urban_forest_v1_bioengineered_infrastructure_skin', 'urban_forest_v2_rewilded_urban_skin', 'urban_forest_v3_resilient_coastal_skin'],
      ['urban_forest_v0', 'urban_forest_bioengineered_v1', 'urban_forest_rewilded_v2', 'urban_forest_coastal_v3'],
    ),
  }),
  park_amphitheater_lawn_v0: Object.freeze({
    amphitheater_lawn: fourVariantMappings(
      'amphitheater_lawn',
      ['amphitheater_lawn_v0_terraced_performance_skin', 'amphitheater_lawn_v1_open_festival_skin', 'amphitheater_lawn_v2_intimate_garden_skin', 'amphitheater_lawn_v3_industrial_adaptive_skin'],
      ['amphitheater_lawn_v0', 'amphitheater_open_festival_v1', 'amphitheater_intimate_garden_v2', 'amphitheater_industrial_v3'],
    ),
  }),
  park_playground_adventure_v0: Object.freeze({
    playground_adventure: fourVariantMappings(
      'playground_adventure',
      ['playground_adventure_v0_rustic_timber_skin', 'playground_adventure_v1_modern_steel_skin', 'playground_adventure_v2_natural_meadow_skin', 'playground_adventure_v3_urban_contemporary_skin'],
      ['playground_adventure_v0', 'playground_modern_steel_v1', 'playground_natural_meadow_v2', 'playground_urban_contemporary_v3'],
    ),
  }),
  park_disc_golf_wooded_v0: Object.freeze({
    disc_golf_course: fourVariantMappings(
      'disc_golf_course',
      ['disc_golf_course_v0_wooded_championship_skin', 'disc_golf_course_v1_open_park_skin', 'disc_golf_course_v2_hillside_terrain_skin', 'disc_golf_course_v3_urban_short_skin'],
      ['disc_golf_wooded_v0', 'disc_golf_open_park_v1', 'disc_golf_hillside_v2', 'disc_golf_urban_short_v3'],
    ),
  }),
  park_bocce_piazza_v0: Object.freeze({
    bocce_petanque_court: fourVariantMappings(
      'bocce_petanque_court',
      ['bocce_petanque_court_v0_italian_piazza_skin', 'bocce_petanque_court_v1_french_petanque_skin', 'bocce_petanque_court_v2_modern_park_skin', 'bocce_petanque_court_v3_community_senior_skin'],
      ['bocce_piazza_v0', 'bocce_french_v1', 'bocce_modern_park_v2', 'bocce_community_senior_v3'],
    ),
  }),
  park_climbing_competition_v0: Object.freeze({
    climbing_bouldering_wall: fourVariantMappings(
      'climbing_bouldering_wall',
      ['climbing_bouldering_wall_v0_competition_skin', 'climbing_bouldering_wall_v1_natural_rock_skin', 'climbing_bouldering_wall_v2_kids_adventure_skin', 'climbing_bouldering_wall_v3_urban_art_skin'],
      ['climbing_competition_v0', 'climbing_natural_rock_v1', 'climbing_kids_adventure_v2', 'climbing_urban_art_v3'],
    ),
  }),
  park_mini_golf_classic_v0: Object.freeze({
    mini_golf_course: fourVariantMappings(
      'mini_golf_course',
      ['mini_golf_course_v0_classic_skin', 'mini_golf_course_v1_garden_putting_skin', 'mini_golf_course_v2_urban_art_skin', 'mini_golf_course_v3_nature_adventure_skin'],
      ['mini_golf_classic_v0', 'mini_golf_garden_putting_v1', 'mini_golf_urban_art_v2', 'mini_golf_nature_adventure_v3'],
    ),
  }),
  park_beach_volleyball_competition_v0: Object.freeze({
    beach_volleyball_courts: fourVariantMappings(
      'beach_volleyball_courts',
      ['beach_volleyball_courts_v0_competition_skin', 'beach_volleyball_courts_v1_beachside_skin', 'beach_volleyball_courts_v2_park_sand_skin', 'beach_volleyball_courts_v3_indoor_outdoor_skin'],
      ['beach_volleyball_competition_v0', 'beach_volleyball_beachside_v1', 'beach_volleyball_park_sand_v2', 'beach_volleyball_hybrid_v3'],
    ),
  }),
  park_pollinator_prairie_v0: Object.freeze({
    pollinator_meadow: fourVariantMappings(
      'pollinator_meadow',
      ['pollinator_meadow_v0_prairie_skin', 'pollinator_meadow_v1_butterfly_garden_skin', 'pollinator_meadow_v2_urban_strip_skin', 'pollinator_meadow_v3_formal_border_skin'],
      ['pollinator_prairie_v0', 'pollinator_butterfly_v1', 'pollinator_urban_strip_v2', 'pollinator_formal_border_v3'],
    ),
  }),
  park_orchard_heritage_v0: Object.freeze({
    urban_orchard_food_forest: fourVariantMappings(
      'urban_orchard_food_forest',
      ['urban_orchard_food_forest_v0_heritage_apple_skin', 'urban_orchard_food_forest_v1_permaculture_skin', 'urban_orchard_food_forest_v2_pick_your_own_skin', 'urban_orchard_food_forest_v3_citrus_grove_skin'],
      ['orchard_heritage_v0', 'orchard_permaculture_v1', 'orchard_pick_your_own_v2', 'orchard_citrus_grove_v3'],
    ),
  }),
  park_bioswale_streetside_v0: Object.freeze({
    bioswale_rain_garden: fourVariantMappings(
      'bioswale_rain_garden',
      ['bioswale_rain_garden_v0_streetside_skin', 'bioswale_rain_garden_v1_park_rain_garden_skin', 'bioswale_rain_garden_v2_terraced_steps_skin', 'bioswale_rain_garden_v3_parking_lot_skin'],
      ['bioswale_streetside_v0', 'bioswale_park_rain_garden_v1', 'bioswale_terraced_steps_v2', 'bioswale_parking_lot_v3'],
    ),
  }),
  park_sculpture_museum_court_v0: Object.freeze({
    sculpture_garden: fourVariantMappings(
      'sculpture_garden',
      ['sculpture_garden_v0_museum_court_skin', 'sculpture_garden_v1_landscape_art_skin', 'sculpture_garden_v2_interactive_kinetic_skin', 'sculpture_garden_v3_rotating_exhibition_skin'],
      ['sculpture_museum_court_v0', 'sculpture_landscape_art_v1', 'sculpture_kinetic_v2', 'sculpture_rotating_v3'],
    ),
  }),
  park_labyrinth_classical_v0: Object.freeze({
    labyrinth_meditation: fourVariantMappings(
      'labyrinth_meditation',
      ['labyrinth_meditation_v0_classical_stone_skin', 'labyrinth_meditation_v1_zen_rock_skin', 'labyrinth_meditation_v2_healing_garden_skin', 'labyrinth_meditation_v3_modern_mindfulness_skin'],
      ['labyrinth_classical_v0', 'labyrinth_zen_rock_v1', 'labyrinth_healing_garden_v2', 'labyrinth_modern_v3'],
    ),
  }),
  park_ice_rink_multipurpose_v3: Object.freeze({
    outdoor_ice_rink: fourVariantMappings(
      'outdoor_ice_rink',
      ['outdoor_ice_rink_v0_holiday_market_skin', 'outdoor_ice_rink_v1_urban_plaza_skin', 'outdoor_ice_rink_v2_nature_trail_skin', 'outdoor_ice_rink_v3_multipurpose_pad_skin'],
      ['ice_rink_holiday_market_v0', 'ice_rink_urban_plaza_v1', 'ice_rink_nature_trail_v2', 'ice_rink_multipurpose_v3'],
    ),
  }),
  park_kayak_river_launch_v0: Object.freeze({
    kayak_launch_dock: fourVariantMappings(
      'kayak_launch_dock',
      ['kayak_launch_dock_v0_river_launch_skin', 'kayak_launch_dock_v1_urban_harbour_skin', 'kayak_launch_dock_v2_lake_beach_skin', 'kayak_launch_dock_v3_community_boathouse_skin'],
      ['kayak_river_launch_v0', 'kayak_urban_harbour_v1', 'kayak_lake_beach_v2', 'kayak_community_boathouse_v3'],
    ),
  }),
  park_tidal_marsh_cordgrass_v0: Object.freeze({
    tidal_marsh_boardwalk: fourVariantMappings(
      'tidal_marsh_boardwalk',
      ['tidal_marsh_boardwalk_v0_cordgrass_skin', 'tidal_marsh_boardwalk_v1_mangrove_skin', 'tidal_marsh_boardwalk_v2_reedbed_skin', 'tidal_marsh_boardwalk_v3_bird_blind_skin'],
      ['tidal_marsh_cordgrass_v0', 'tidal_marsh_mangrove_v1', 'tidal_marsh_reedbed_v2', 'tidal_marsh_bird_blind_v3'],
    ),
  }),
  park_cinema_lawn_projection_v1: Object.freeze({
    outdoor_cinema_lawn: fourVariantMappings(
      'outdoor_cinema_lawn',
      ['outdoor_cinema_lawn_v0_popup_festival_skin', 'outdoor_cinema_lawn_v1_park_projection_skin', 'outdoor_cinema_lawn_v2_drive_in_skin', 'outdoor_cinema_lawn_v3_rooftop_skin'],
      ['cinema_popup_festival_v0', 'cinema_lawn_projection_v1', 'cinema_drive_in_v2', 'cinema_rooftop_v3'],
    ),
  }),
  park_food_truck_permanent_v1: Object.freeze({
    food_truck_plaza: fourVariantMappings(
      'food_truck_plaza',
      ['food_truck_plaza_v0_industrial_popup_skin', 'food_truck_plaza_v1_permanent_park_skin', 'food_truck_plaza_v2_adaptive_lot_skin', 'food_truck_plaza_v3_night_market_skin'],
      ['food_truck_industrial_v0', 'food_truck_permanent_v1', 'food_truck_adaptive_v2', 'food_truck_night_market_v3'],
    ),
  }),
  park_great_lawn_v2: Object.freeze({
    festival_event_lawn: fourVariantMappings(
      'festival_event_lawn',
      ['festival_event_lawn_v0_concert_skin', 'festival_event_lawn_v1_farmers_market_skin', 'festival_event_lawn_v2_great_lawn_skin', 'festival_event_lawn_v3_winter_market_skin'],
      ['festival_concert_v0', 'festival_farmers_market_v1', 'great_lawn_v2', 'festival_winter_market_v3'],
    ),
  }),
  park_campus_meadow_quad_v0: Object.freeze({
    campus_central_quad: fourNamedVariantMappings(
      'campus_central_quad',
      ['campus_central_quad_v0_naturalized_meadow_skin', 'campus_central_quad_v1_modern_plaza_skin', 'campus_central_quad_v2_garden_pavilion_skin', 'campus_central_quad_v3_formal_collegiate_skin'],
      ['campus_meadow_quad_v0', 'campus_modern_plaza_v1', 'campus_garden_pavilion_v2', 'campus_formal_collegiate_v3'],
    ),
  }),
  park_urban_beach_family_v2: Object.freeze({
    urban_beach: fourVariantMappings(
      'urban_beach',
      ['urban_beach_v0_paris_plages_skin', 'urban_beach_v1_riverfront_bar_skin', 'urban_beach_v2_family_splash_skin', 'urban_beach_v3_sand_garden_skin'],
      ['urban_beach_paris_v0', 'urban_beach_bar_v1', 'urban_beach_family_v2', 'urban_beach_sand_garden_v3'],
    ),
  }),
  park_velodrome_open_air_v0: Object.freeze({
    velodrome_cycling_track: fourNamedVariantMappings(
      'velodrome_cycling_track',
      ['velodrome_cycling_track_v0_open_air_skin', 'velodrome_cycling_track_v1_indoor_arena_skin', 'velodrome_cycling_track_v2_parkland_skin', 'velodrome_cycling_track_v3_community_training_skin'],
      ['velodrome_open_air_v0', 'velodrome_indoor_v1', 'velodrome_parkland_v2', 'velodrome_community_v3'],
    ),
  }),
  park_mtb_skills_dirt_v2: Object.freeze({
    mountain_bike_park: fourNamedVariantMappings(
      'mountain_bike_park',
      ['mountain_bike_park_v0_paved_pump_skin', 'mountain_bike_park_v1_hillside_skin', 'mountain_bike_park_v2_skills_dirt_skin', 'mountain_bike_park_v3_urban_dirt_skin'],
      ['mtb_paved_pump_v0', 'mtb_hillside_v1', 'mtb_skills_dirt_v2', 'mtb_urban_dirt_v3'],
    ),
  }),
  park_regional_english_landscape_v0: Object.freeze({
    regional_park: fourVariantMappings(
      'regional_park',
      ['regional_park_v0_english_landscape_skin', 'regional_park_v1_modern_minimalist_skin', 'regional_park_v2_mediterranean_xeriscape_skin', 'regional_park_v3_tropical_lush_skin'],
      ['regional_english_landscape_v0', 'regional_modern_minimalist_v1', 'regional_mediterranean_xeriscape_v2', 'regional_tropical_lush_v3'],
    ),
  }),
  park_beer_garden_munich_v0: Object.freeze({
    beer_garden: fourVariantMappings(
      'beer_garden',
      ['beer_garden_v0_munich_chestnut_skin', 'beer_garden_v1_brewery_tap_yard_skin', 'beer_garden_v2_pergola_terrace_skin', 'beer_garden_v3_rooftop_skin'],
      ['beer_garden_munich_v0', 'beer_garden_brewery_v1', 'beer_garden_pergola_v2', 'beer_garden_rooftop_v3'],
    ),
  }),
  park_sunken_courtyard_v0: Object.freeze({
    sunken_plaza: fourVariantMappings(
      'sunken_plaza',
      ['sunken_plaza_v0_intimate_courtyard_skin', 'sunken_plaza_v1_rockefeller_rink_skin', 'sunken_plaza_v2_corporate_atrium_skin', 'sunken_plaza_v3_asian_transit_skin'],
      ['sunken_courtyard_v0', 'sunken_rockefeller_v1', 'sunken_corporate_v2', 'sunken_asian_transit_v3'],
    ),
  }),
  park_terraced_cascade_v3: Object.freeze({
    stepped_terraced_plaza: fourVariantMappings(
      'stepped_terraced_plaza',
      ['stepped_terraced_plaza_v0_aegean_skin', 'stepped_terraced_plaza_v1_spanish_steps_skin', 'stepped_terraced_plaza_v2_federation_shard_skin', 'stepped_terraced_plaza_v3_modernist_cascade_skin'],
      ['terraced_aegean_v0', 'terraced_spanish_v1', 'terraced_federation_v2', 'terraced_cascade_v3'],
    ),
  }),
  park_market_festival_lawn_v1: Object.freeze({
    market_square: fourVariantMappings('market_square', ['market_square_v0_terraced_performance_skin', 'market_square_v1_open_festival_lawn_skin', 'market_square_v2_intimate_garden_skin', 'market_square_v3_industrial_adaptive_skin'], ['market_terraced_v0', 'market_festival_lawn_v1', 'market_garden_v2', 'market_industrial_v3']),
  }),
  park_boardwalk_maritime_v0: Object.freeze({
    promenade_boardwalk: fourVariantMappings('promenade_boardwalk', ['promenade_boardwalk_v0_maritime_skin', 'promenade_boardwalk_v1_modern_esplanade_skin', 'promenade_boardwalk_v2_tropical_resort_skin', 'promenade_boardwalk_v3_naturalized_riparian_skin'], ['boardwalk_maritime_v0', 'boardwalk_modern_v1', 'boardwalk_tropical_v2', 'boardwalk_riparian_v3']),
  }),
  park_fountain_formal_pool_v1: Object.freeze({
    fountain_water_feature: fourVariantMappings('fountain_water_feature', ['fountain_water_feature_v0_naturalistic_pond_skin', 'fountain_water_feature_v1_formal_pool_skin', 'fountain_water_feature_v2_contemporary_interactive_skin', 'fountain_water_feature_v3_ecological_wetland_skin'], ['fountain_naturalistic_v0', 'fountain_formal_pool_v1', 'fountain_interactive_v2', 'fountain_wetland_v3']),
  }),
  park_natural_swimming_pond_v0: Object.freeze({
    swimming_pool_complex: fourVariantMappings('swimming_pool_complex', ['swimming_pool_complex_v0_natural_pond_skin', 'swimming_pool_complex_v1_formal_reflecting_skin', 'swimming_pool_complex_v2_contemporary_interactive_skin', 'swimming_pool_complex_v3_ecological_wetland_skin'], ['natural_swimming_pond_v0', 'swimming_formal_v1', 'swimming_interactive_v2', 'swimming_wetland_v3']),
  }),
  park_nature_preserve_prairie_v1: Object.freeze({
    nature_preserve: fourVariantMappings('nature_preserve',
      ['nature_preserve_v0_wetland_boardwalk_skin', 'nature_preserve_v1_tallgrass_prairie_skin', 'nature_preserve_v2_coastal_dune_skin', 'nature_preserve_v3_old_growth_skin'],
      ['nature_preserve_wetland_v0', 'nature_preserve_prairie_v1', 'nature_preserve_dune_v2', 'nature_preserve_old_growth_v3']),
  }),
  park_riverfront_lake_beach_v1: Object.freeze({
    riverfront_park_beach: fourVariantMappings('riverfront_park_beach',
      ['riverfront_park_beach_v0_urban_river_skin', 'riverfront_park_beach_v1_lake_swimming_skin', 'riverfront_park_beach_v2_adventure_pier_skin', 'riverfront_park_beach_v3_naturalized_skin'],
      ['riverfront_urban_beach_v0', 'riverfront_lake_beach_v1', 'riverfront_adventure_pier_v2', 'riverfront_naturalized_v3']),
  }),
  park_reclaimed_wharf_v0: Object.freeze({
    reclaimed_industrial_park: fourVariantMappings('reclaimed_industrial_park',
      ['reclaimed_industrial_park_v0_wharf_skin', 'reclaimed_industrial_park_v1_gasworks_skin', 'reclaimed_industrial_park_v2_colliery_skin', 'reclaimed_industrial_park_v3_steelworks_skin'],
      ['reclaimed_wharf_v0', 'reclaimed_gasworks_v1', 'reclaimed_colliery_v2', 'reclaimed_steelworks_v3']),
  }),
  park_quarry_tier_cascade_v2: Object.freeze({
    quarry_sunken_garden_park: fourVariantMappings('quarry_sunken_garden_park',
      ['quarry_sunken_garden_park_v0_sculpture_bowl_skin', 'quarry_sunken_garden_park_v1_quarry_lake_skin', 'quarry_sunken_garden_park_v2_tier_cascade_skin', 'quarry_sunken_garden_park_v3_show_garden_skin'],
      ['quarry_sculpture_bowl_v0', 'quarry_lake_v1', 'quarry_tier_cascade_v2', 'quarry_show_garden_v3']),
  }),
  park_estate_oak_picnic_v1: Object.freeze({
    estate_picnic_grove: fourVariantMappings('estate_picnic_grove',
      ['estate_picnic_grove_v0_pine_creek_skin', 'estate_picnic_grove_v1_oak_skin', 'estate_picnic_grove_v2_meadow_pavilion_skin', 'estate_picnic_grove_v3_regional_plain_skin'],
      ['estate_pine_creek_v0', 'estate_oak_picnic_v1', 'estate_meadow_pavilion_v2', 'estate_regional_plain_v3']),
  }),
  park_constructed_wetland_boardwalk_v0: Object.freeze({
    constructed_wetland_eco_park: fourNamedVariantMappings('constructed_wetland_eco_park', ['constructed_wetland_eco_park_v0_boardwalk_skin','constructed_wetland_eco_park_v1_tidal_skin','constructed_wetland_eco_park_v2_wildlife_skin','constructed_wetland_eco_park_v3_nature_center_skin'], ['constructed_wetland_boardwalk_v0','constructed_wetland_tidal_v1','constructed_wetland_wildlife_v2','constructed_wetland_nature_center_v3']),
  }),
  park_academic_planted_court_v0: Object.freeze({
    academic_courtyard: fourNamedVariantMappings('academic_courtyard', ['academic_courtyard_v0_planted_skin','academic_courtyard_v1_corten_skin','academic_courtyard_v2_glass_canopy_skin','academic_courtyard_v3_timber_screen_skin'], ['academic_planted_court_v0','academic_corten_court_v1','academic_glass_canopy_v2','academic_timber_screen_v3']),
  }),
  park_campus_green_spine_v0: Object.freeze({
    campus_pedestrian_spine: fourNamedVariantMappings('campus_pedestrian_spine', ['campus_pedestrian_spine_v0_green_skin','campus_pedestrian_spine_v1_paved_skin','campus_pedestrian_spine_v2_pavilion_skin','campus_pedestrian_spine_v3_pergola_skin'], ['campus_green_spine_v0','campus_paved_spine_v1','campus_pavilion_spine_v2','campus_pergola_spine_v3']),
  }),
  park_botanical_rose_garden_v3: Object.freeze({
    botanical_garden: Object.freeze([Object.freeze({ variantId: 'botanical_garden_v3', appearanceKitId: 'botanical_garden_v3_rose_skin', plantingStructure: 'botanical_rose_garden_v3' })]),
  }),
  park_research_arboretum_v0: Object.freeze({
    research_garden_teaching_arboretum: fourNamedVariantMappings('research_garden_teaching_arboretum', ['research_garden_teaching_arboretum_v0_skin','research_garden_teaching_arboretum_v1_greenhouse_skin','research_garden_teaching_arboretum_v2_pavilion_skin','research_garden_teaching_arboretum_v3_plots_skin'], ['research_arboretum_v0','research_greenhouse_v1','research_pavilion_v2','research_plots_v3']),
  }),
  park_rewilding_reforestation_v1: Object.freeze({
    rewilding_ecological_restoration_zone: fourNamedVariantMappings('rewilding_ecological_restoration_zone', ['rewilding_ecological_restoration_zone_v0_prairie_skin','rewilding_ecological_restoration_zone_v1_skin','rewilding_ecological_restoration_zone_v2_interpretive_skin','rewilding_ecological_restoration_zone_v3_riparian_skin'], ['rewilding_prairie_v0','rewilding_reforestation_v1','rewilding_interpretive_v2','rewilding_riparian_v3']),
  }),
  park_stormwater_arid_channel_v3: Object.freeze({
    stormwater_resilience_park: fourNamedVariantMappings('stormwater_resilience_park', ['stormwater_resilience_park_v0_bioswale_skin','stormwater_resilience_park_v1_detention_skin','stormwater_resilience_park_v2_terraced_skin','stormwater_resilience_park_v3_arid_skin'], ['stormwater_bioswale_v0','stormwater_detention_v1','stormwater_terraced_v2','stormwater_arid_channel_v3']),
  }),
  park_urban_pocket_rustic_v0: Object.freeze({
    urban_pocket_park: Object.freeze([Object.freeze({ variantId: 'urban_pocket_park_v0', appearanceKitId: 'urban_pocket_park_v0_rustic_skin', plantingStructure: 'urban_pocket_rustic_v0' })]),
  }),
  park_neighborhood_contemporary_v3: Object.freeze({
    neighborhood_park: Object.freeze([Object.freeze({ variantId: 'neighborhood_park_v3', appearanceKitId: 'neighborhood_park_v3_contemporary_skin', plantingStructure: 'neighborhood_contemporary_v3' })]),
  }),
  park_cemetery_classical_v0: Object.freeze({
    cemetery_memorial_grounds: fourVariantMappings('cemetery_memorial_grounds',
      ['cemetery_memorial_grounds_v0_classical_skin', 'cemetery_memorial_grounds_v1_woodland_skin', 'cemetery_memorial_grounds_v2_sculptural_skin', 'cemetery_memorial_grounds_v3_cottage_skin'],
      ['cemetery_classical_v0', 'cemetery_woodland_v1', 'cemetery_sculptural_v2', 'cemetery_cottage_v3']),
  }),
  park_courtyard_linear_water_v1: Object.freeze({
    courtyard_plaza: fourVariantMappings('courtyard_plaza',
      ['courtyard_plaza_v0_neoclassical_skin', 'courtyard_plaza_v1_linear_water_skin', 'courtyard_plaza_v2_green_civic_skin', 'courtyard_plaza_v3_festival_market_skin'],
      ['courtyard_neoclassical_v0', 'courtyard_linear_water_v1', 'courtyard_green_civic_v2', 'courtyard_festival_v3']),
  }),
  park_parklet_sf_timber_v1: Object.freeze({
    street_plaza_parklet: fourVariantMappings('street_plaza_parklet',
      ['street_plaza_parklet_v0_nyc_skin', 'street_plaza_parklet_v1_sf_timber_skin', 'street_plaza_parklet_v2_tactical_skin', 'street_plaza_parklet_v3_european_skin'],
      ['parklet_nyc_v0', 'parklet_sf_timber_v1', 'parklet_tactical_v2', 'parklet_european_v3']),
  }),
  park_french_parterre_axis_v1: Object.freeze({
    parisian_jardin: fourVariantMappings('parisian_jardin',
      ['parisian_jardin_v0_clipped_parterre_skin', 'parisian_jardin_v1_water_axis_skin', 'parisian_jardin_v2_rill_garden_skin', 'parisian_jardin_v3_paved_forecourt_skin'],
      ['paris_jardin_clipped_parterre_v0', 'french_parterre_axis_v1', 'paris_jardin_rill_garden_v2', 'paris_jardin_paved_forecourt_v3']),
  }),
  park_london_railed_square_v1: Object.freeze({
    london_garden_square: fourVariantMappings('london_garden_square',
      ['london_garden_square_v0_open_skin', 'london_garden_square_v1_railed_skin', 'london_garden_square_v2_lush_brick_skin', 'london_garden_square_v3_cafe_skin'],
      ['london_garden_open_v0', 'london_railed_square_v1', 'london_garden_lush_brick_v2', 'london_garden_cafe_v3']),
  }),
  park_halifax_rose_bandstand_v0: Object.freeze({
    halifax_public_gardens: fourVariantMappings('halifax_public_gardens',
      ['halifax_public_gardens_v0_rose_skin', 'halifax_public_gardens_v1_bandstand_skin', 'halifax_public_gardens_v2_autumn_skin', 'halifax_public_gardens_v3_tulip_skin'],
      ['halifax_rose_bandstand_v0', 'halifax_bandstand_concert_v1', 'halifax_autumn_stroll_v2', 'halifax_spring_tulip_v3']),
  }),
  park_olmsted_multilandscape_v3: Object.freeze({
    picturesque_olmsted_park: fourVariantMappings('picturesque_olmsted_park',
      ['picturesque_olmsted_park_v0_heath_skin', 'picturesque_olmsted_park_v1_lookout_skin', 'picturesque_olmsted_park_v2_meadow_ravine_skin', 'picturesque_olmsted_park_v3_multilandscape_skin'],
      ['olmsted_heath_v0', 'olmsted_lookout_v1', 'olmsted_meadow_ravine_v2', 'olmsted_multilandscape_v3']),
  }),
  park_hilltop_viewpoint_v3: Object.freeze({
    hilltop_topographic_park: fourVariantMappings('hilltop_topographic_park',
      ['hilltop_topographic_park_v0_cypress_skin', 'hilltop_topographic_park_v1_switchback_skin', 'hilltop_topographic_park_v2_folly_skin', 'hilltop_topographic_park_v3_viewpoint_skin'],
      ['hilltop_cypress_v0', 'hilltop_switchback_v1', 'hilltop_folly_v2', 'hilltop_viewpoint_v3']),
  }),
  park_amsterdam_hofje_garden_v0: Object.freeze({
    amsterdam_hofje_garden: fourVariantMappings('amsterdam_hofje_garden',
      ['amsterdam_hofje_garden_v0_skin', 'amsterdam_hofje_garden_v1_lush_skin', 'amsterdam_hofje_garden_v2_pocket_skin', 'amsterdam_hofje_garden_v3_historic_lawn_skin'],
      ['amsterdam_hofje_v0', 'amsterdam_hofje_lush_v1', 'amsterdam_hofje_pocket_v2', 'amsterdam_hofje_historic_lawn_v3']),
  }),
  park_amsterdam_plein_v0: Object.freeze({
    amsterdam_plein: fourVariantMappings('amsterdam_plein',
      ['amsterdam_plein_v0_brick_skin', 'amsterdam_plein_v1_glass_canopy_skin', 'amsterdam_plein_v2_cafe_threshold_skin', 'amsterdam_plein_v3_open_brick_skin'],
      ['amsterdam_plein_v0', 'amsterdam_plein_glass_canopy_v1', 'amsterdam_plein_cafe_v2', 'amsterdam_plein_open_v3']),
  }),
  park_amsterdam_vondelpark_pavilion_v3: Object.freeze({
    amsterdam_vondelpark: fourVariantMappings('amsterdam_vondelpark',
      ['amsterdam_vondelpark_v0_neighbourhood_skin', 'amsterdam_vondelpark_v1_cafe_skin', 'amsterdam_vondelpark_v2_planted_corner_skin', 'amsterdam_vondelpark_v3_pavilion_skin'],
      ['amsterdam_vondelpark_neighbourhood_v0', 'amsterdam_vondelpark_cafe_v1', 'amsterdam_vondelpark_planted_v2', 'amsterdam_vondelpark_v3']),
  }),
  park_barcelona_pati_green_v0: Object.freeze({
    barcelona_pati_interior: fourVariantMappings('barcelona_pati_interior',
      ['barcelona_pati_interior_v0_green_skin', 'barcelona_pati_interior_v1_lawn_skin', 'barcelona_pati_interior_v2_social_paved_skin', 'barcelona_pati_interior_v3_shade_paved_skin'],
      ['barcelona_pati_green_v0', 'barcelona_pati_lawn_v1', 'barcelona_pati_social_v2', 'barcelona_pati_shade_v3']),
  }),
  park_barcelona_xamfra_corner_v2: Object.freeze({
    barcelona_placa_xamfra: fourVariantMappings('barcelona_placa_xamfra',
      ['barcelona_placa_xamfra_v0_cafe_skin', 'barcelona_placa_xamfra_v1_clear_skin', 'barcelona_placa_xamfra_v2_corner_skin', 'barcelona_placa_xamfra_v3_active_skin'],
      ['barcelona_xamfra_cafe_v0', 'barcelona_xamfra_clear_v1', 'barcelona_xamfra_v2', 'barcelona_xamfra_active_v3']),
  }),
  park_barcelona_superilla_green_v1: Object.freeze({
    barcelona_superilla: fourVariantMappings('barcelona_superilla',
      ['barcelona_superilla_v0_plaza_planter_skin', 'barcelona_superilla_v1_green_skin', 'barcelona_superilla_v2_green_corridor_skin', 'barcelona_superilla_v3_social_garden_skin'],
      ['barcelona_superilla_plaza_v0', 'barcelona_superilla_v1', 'barcelona_superilla_corridor_v2', 'barcelona_superilla_social_v3']),
  }),
  park_calgary_prairie_market_v1: Object.freeze({
    calgary_prairie_plaza: fourVariantMappings('calgary_prairie_plaza',
      ['calgary_prairie_plaza_v0_winter_skin', 'calgary_prairie_plaza_v1_market_skin', 'calgary_prairie_plaza_v2_indigenous_art_skin', 'calgary_prairie_plaza_v3_corporate_green_skin'],
      ['calgary_prairie_winter_v0', 'calgary_prairie_market_v1', 'calgary_prairie_indigenous_v2', 'calgary_prairie_corporate_v3']),
  }),
  park_calgary_princes_island_festival_v0: Object.freeze({
    calgary_princes_island: fourVariantMappings('calgary_princes_island',
      ['calgary_princes_island_v0_festival_skin', 'calgary_princes_island_v1_autumn_skin', 'calgary_princes_island_v2_winter_skin', 'calgary_princes_island_v3_flood_skin'],
      ['calgary_princes_island_v0', 'calgary_princes_autumn_v1', 'calgary_princes_winter_v2', 'calgary_princes_flood_v3']),
  }),
  park_montreal_mount_royal_grove_v2: Object.freeze({
    montreal_mount_royal: fourVariantMappings('montreal_mount_royal',
      ['montreal_mount_royal_v0_overlook_skin', 'montreal_mount_royal_v1_lawn_skin', 'montreal_mount_royal_v2_grove_skin', 'montreal_mount_royal_v3_hillside_skin'],
      ['montreal_mount_royal_overlook_v0', 'montreal_mount_royal_lawn_v1', 'montreal_mount_royal_v2', 'montreal_mount_royal_hillside_v3']),
  }),
  park_montreal_neighbourhood_square_v3: Object.freeze({
    montreal_square: fourVariantMappings('montreal_square',
      ['montreal_square_v0_hard_plaza_skin', 'montreal_square_v1_linear_bench_skin', 'montreal_square_v2_pocket_court_skin', 'montreal_square_v3_neighbourhood_skin'],
      ['montreal_square_hard_v0', 'montreal_square_linear_v1', 'montreal_square_pocket_v2', 'montreal_square_v3']),
  }),
  park_paris_place_royale_v2: Object.freeze({
    parisian_place: fourVariantMappings('parisian_place',
      ['parisian_place_v0_quiet_cobble_skin', 'parisian_place_v1_statue_axis_skin', 'parisian_place_v2_royale_skin', 'parisian_place_v3_cafe_paved_skin'],
      ['paris_place_quiet_v0', 'paris_place_statue_v1', 'paris_place_royale_v2', 'paris_place_cafe_v3']),
  }),
  park_paris_square_tree_grid_v3: Object.freeze({
    parisian_square: fourVariantMappings('parisian_square',
      ['parisian_square_v0_linear_edge_skin', 'parisian_square_v1_corner_cafe_skin', 'parisian_square_v2_compact_cobble_skin', 'parisian_square_v3_tree_grid_skin'],
      ['paris_square_linear_v0', 'paris_square_corner_cafe_v1', 'paris_square_compact_v2', 'paris_square_tree_grid_v3']),
  }),
  park_london_circus_planted_v1: Object.freeze({
    london_circus: fourVariantMappings('london_circus',
      ['london_circus_v0_round_island_skin', 'london_circus_v1_planted_skin', 'london_circus_v2_side_court_skin', 'london_circus_v3_passage_skin'],
      ['london_circus_round_v0', 'london_circus_planted_v1', 'london_circus_side_court_v2', 'london_circus_passage_v3']),
  }),
  park_newyork_pocket_water_v0: Object.freeze({
    newyork_pocket_park: fourVariantMappings('newyork_pocket_park',
      ['newyork_pocket_park_v0_water_skin', 'newyork_pocket_park_v1_linear_skin', 'newyork_pocket_park_v2_brick_skin', 'newyork_pocket_park_v3_promenade_skin'],
      ['newyork_pocket_water_v0', 'newyork_pocket_linear_v1', 'newyork_pocket_brick_v2', 'newyork_pocket_promenade_v3']),
  }),
  park_newyork_community_greenhouse_v3: Object.freeze({
    newyork_community_garden: fourVariantMappings('newyork_community_garden',
      ['newyork_community_garden_v0_allotment_skin', 'newyork_community_garden_v1_raised_grid_skin', 'newyork_community_garden_v2_shed_skin', 'newyork_community_garden_v3_greenhouse_skin'],
      ['newyork_community_allotment_v0', 'newyork_community_raised_v1', 'newyork_community_shed_v2', 'newyork_community_greenhouse_v3']),
  }),
  park_vancouver_seawall_cycle_v2: Object.freeze({
    vancouver_seawall: fourVariantMappings('vancouver_seawall',
      ['vancouver_seawall_v0_promenade_skin', 'vancouver_seawall_v1_bench_skin', 'vancouver_seawall_v2_cycle_skin', 'vancouver_seawall_v3_esplanade_skin'],
      ['vancouver_seawall_promenade_v0', 'vancouver_seawall_bench_v1', 'vancouver_seawall_cycle_v2', 'vancouver_seawall_esplanade_v3']),
  }),
  park_vancouver_beach_pavilion_v0: Object.freeze({
    vancouver_beach_park: fourVariantMappings('vancouver_beach_park',
      ['vancouver_beach_park_v0_pavilion_skin', 'vancouver_beach_park_v1_brick_pavilion_skin', 'vancouver_beach_park_v2_glazed_pavilion_skin', 'vancouver_beach_park_v3_waterfront_garden_skin'],
      ['vancouver_beach_pavilion_v0', 'vancouver_beach_brick_v1', 'vancouver_beach_glazed_v2', 'vancouver_beach_waterfront_v3']),
  }),
  park_toronto_ravine_creek_v1: Object.freeze({
    toronto_ravine: fourVariantMappings('toronto_ravine',
      ['toronto_ravine_v0_spring_skin', 'toronto_ravine_v1_creek_skin', 'toronto_ravine_v2_autumn_skin', 'toronto_ravine_v3_winter_skin'],
      ['toronto_ravine_spring_v0', 'toronto_ravine_creek_v1', 'toronto_ravine_autumn_v2', 'toronto_ravine_winter_v3']),
  }),
  park_toronto_urban_market_v1: Object.freeze({
    toronto_urban_square: fourVariantMappings('toronto_urban_square',
      ['toronto_urban_square_v0_winter_rink_skin', 'toronto_urban_square_v1_market_skin', 'toronto_urban_square_v2_modernist_pool_skin', 'toronto_urban_square_v3_rain_garden_skin'],
      ['toronto_square_winter_v0', 'toronto_urban_market_v1', 'toronto_square_modernist_v2', 'toronto_square_rain_garden_v3']),
  }),
  park_halifax_coastal_fog_path_v2: Object.freeze({
    halifax_coastal_park: fourVariantMappings('halifax_coastal_park',
      ['halifax_coastal_park_v0_storm_skin', 'halifax_coastal_park_v1_summer_skin', 'halifax_coastal_park_v2_fog_path_skin', 'halifax_coastal_park_v3_boardwalk_skin'],
      ['halifax_coastal_storm_v0', 'halifax_coastal_summer_v1', 'halifax_coastal_fog_path_v2', 'halifax_coastal_boardwalk_v3']),
  }),
  park_city_hall_modernist_fountain_v2: Object.freeze({
    city_hall_government_plaza: fourVariantMappings(
      'city_hall_government_plaza',
      ['city_hall_government_plaza_v0_compact_skin', 'city_hall_government_plaza_v1_historic_skin', 'city_hall_government_plaza_v2_modernist_skin', 'city_hall_government_plaza_v3_brutalist_skin'],
      ['city_hall_compact_v0', 'city_hall_historic_v1', 'city_hall_modernist_fountain_v2', 'city_hall_brutalist_v3'],
    ),
  }),
  park_cathedral_courtyard_fountain_v3: Object.freeze({
    cathedral_religious_forecourt: fourVariantMappings(
      'cathedral_religious_forecourt',
      ['cathedral_religious_forecourt_v0_asian_temple_skin', 'cathedral_religious_forecourt_v1_gothic_parvis_skin', 'cathedral_religious_forecourt_v2_renaissance_skin', 'cathedral_religious_forecourt_v3_courtyard_skin'],
      ['cathedral_asian_temple_v0', 'cathedral_gothic_parvis_v1', 'cathedral_renaissance_v2', 'cathedral_courtyard_fountain_v3'],
    ),
  }),
  park_cultural_museum_terrace_v0: Object.freeze({
    cultural_institution_forecourt: fourVariantMappings(
      'cultural_institution_forecourt',
      ['cultural_institution_forecourt_v0_museum_terrace_skin', 'cultural_institution_forecourt_v1_library_steps_skin', 'cultural_institution_forecourt_v2_concert_hall_skin', 'cultural_institution_forecourt_v3_arena_concourse_skin'],
      ['cultural_museum_terrace_v0', 'cultural_library_steps_v1', 'cultural_concert_hall_v2', 'cultural_arena_concourse_v3'],
    ),
  }),
  park_transit_green_civic_v2: Object.freeze({ transit_plaza: fourVariantMappings('transit_plaza', ['transit_plaza_v0_neoclassical_skin','transit_plaza_v1_contemporary_skin','transit_plaza_v2_green_civic_skin','transit_plaza_v3_festival_market_skin'], ['transit_neoclassical_v0','transit_contemporary_v1','transit_green_civic_v2','transit_festival_v3']) }),
  park_amphitheater_terraced_v0: Object.freeze({ amphitheater_performance_space: fourVariantMappings('amphitheater_performance_space', ['amphitheater_performance_space_v0_terraced_skin','amphitheater_performance_space_v1_open_festival_skin','amphitheater_performance_space_v2_intimate_garden_skin','amphitheater_performance_space_v3_industrial_skin'], ['amphitheater_terraced_v0','amphitheater_open_festival_v1','amphitheater_garden_v2','amphitheater_industrial_v3']) }),
  park_concert_timber_lawn_v2: Object.freeze({ concert_pavilion_lawn: fourVariantMappings('concert_pavilion_lawn', ['concert_pavilion_lawn_v0_stadium_skin','concert_pavilion_lawn_v1_wave_skin','concert_pavilion_lawn_v2_timber_skin','concert_pavilion_lawn_v3_bowl_skin'], ['concert_stadium_v0','concert_wave_v1','concert_timber_lawn_v2','concert_bowl_v3']) }),
  park_night_market_hawker_v0: Object.freeze({ night_market: fourVariantMappings('night_market', ['night_market_v0_hawker_skin','night_market_v1_christmas_skin','night_market_v2_latin_skin','night_market_v3_food_hall_skin'], ['night_market_hawker_v0','night_market_christmas_v1','night_market_latin_v2','night_market_food_hall_v3']) }),
  park_parade_national_mall_v3: Object.freeze({ parade_ground: fourVariantMappings('parade_ground', ['parade_ground_v0_stadium_skin','parade_ground_v1_mall_skin','parade_ground_v2_champ_de_mars_skin','parade_ground_v3_national_mall_skin'], ['parade_stadium_v0','parade_mall_v1','parade_champ_v2','parade_national_mall_v3']) }),
  park_canal_ecological_wetland_v3: Object.freeze({ canal_waterway: fourVariantMappings('canal_waterway', ['canal_waterway_v0_naturalistic_skin','canal_waterway_v1_formal_reflecting_skin','canal_waterway_v2_interactive_skin','canal_waterway_v3_ecological_skin'], ['canal_naturalistic_v0','canal_formal_v1','canal_interactive_v2','canal_ecological_wetland_v3']) }),
  park_custom_biophilic_urban_v1: Object.freeze({ custom_parks_plazas: fourVariantMappings('custom_parks_plazas', ['custom_parks_plazas_v0_eclectic_skin','custom_parks_plazas_v1_biophilic_skin','custom_parks_plazas_v2_tech_smart_skin','custom_parks_plazas_v3_heritage_skin'], ['custom_eclectic_v0','custom_biophilic_urban_v1','custom_tech_smart_v2','custom_heritage_v3']) }),
  park_rooftop_intensive_garden_v0: Object.freeze({ rooftop_garden: fourVariantMappings('rooftop_garden', ['rooftop_garden_v0_intensive_skin', 'rooftop_garden_v1_sedum_skin', 'rooftop_garden_v2_urban_farm_skin', 'rooftop_garden_v3_social_terrace_skin'], ['rooftop_intensive_garden_v0', 'rooftop_sedum_v1', 'rooftop_farm_v2', 'rooftop_social_v3']) }),
  park_community_healing_garden_v2: Object.freeze({ community_garden_enhanced: Object.freeze([
    Object.freeze({variantId:'garden_classic_allotment',appearanceKitId:'community_garden_enhanced_allotment_skin',plantingStructure:'community_allotment_v0'}),
    Object.freeze({variantId:'garden_permaculture_farm',appearanceKitId:'community_garden_enhanced_permaculture_skin',plantingStructure:'community_permaculture_v1'}),
    Object.freeze({variantId:'garden_healing',appearanceKitId:'community_garden_enhanced_healing_skin',plantingStructure:'community_healing_garden_v2'}),
    Object.freeze({variantId:'garden_intercultural',appearanceKitId:'community_garden_enhanced_intercultural_skin',plantingStructure:'community_intercultural_v3'}),
  ]) }),
  park_greenbelt_rail_trail_v1: Object.freeze({ greenbelt_buffer_park: fourVariantMappings('greenbelt_buffer_park', ['greenbelt_buffer_park_v0_suburban_lawn_skin','greenbelt_buffer_park_v1_rail_trail_skin','greenbelt_buffer_park_v2_hedgerow_skin','greenbelt_buffer_park_v3_active_spine_skin'], ['greenbelt_suburban_lawn_v0','greenbelt_rail_trail_v1','greenbelt_hedgerow_v2','greenbelt_active_spine_v3']) }),
  park_foothill_heathland_trail_v2: Object.freeze({ foothill_trail_park: fourVariantMappings('foothill_trail_park', ['foothill_trail_park_v0_sage_skin','foothill_trail_park_v1_eucalyptus_skin','foothill_trail_park_v2_heathland_skin','foothill_trail_park_v3_larch_skin'], ['foothill_sage_v0','foothill_eucalyptus_v1','foothill_heathland_trail_v2','foothill_larch_v3']) }),
  park_marina_pacific_dock_v2: Object.freeze({ marina_yacht_harbor: fourVariantMappings('marina_yacht_harbor', ['marina_yacht_harbor_v0_inland_skin','marina_yacht_harbor_v1_fishing_skin','marina_yacht_harbor_v2_pacific_skin','marina_yacht_harbor_v3_superyacht_skin'], ['marina_inland_v0','marina_fishing_v1','marina_pacific_dock_v2','marina_superyacht_v3']) }),
  park_working_pier_brooklyn_park_v3: Object.freeze({ working_pier_wharf_conversion: fourVariantMappings('working_pier_wharf_conversion', ['working_pier_wharf_conversion_v0_market_skin','working_pier_wharf_conversion_v1_retail_skin','working_pier_wharf_conversion_v2_industrial_skin','working_pier_wharf_conversion_v3_park_skin'], ['working_pier_market_v0','working_pier_retail_v1','working_pier_industrial_v2','working_pier_brooklyn_park_v3']) }),
  park_floating_meadow_loop_v2: Object.freeze({ floating_park_pool: fourVariantMappings('floating_park_pool', ['floating_park_pool_v0_plus_pool_skin','floating_park_pool_v1_harbour_bath_skin','floating_park_pool_v2_meadow_skin','floating_park_pool_v3_little_island_skin'], ['floating_plus_pool_v0','floating_harbour_bath_v1','floating_meadow_loop_v2','floating_little_island_v3']) }),
  park_lighthouse_pacific_headland_v2: Object.freeze({ lighthouse_point_park: fourVariantMappings('lighthouse_point_park', ['lighthouse_point_park_v0_cape_skin','lighthouse_point_park_v1_dune_skin','lighthouse_point_park_v2_pacific_skin','lighthouse_point_park_v3_fortress_skin'], ['lighthouse_cape_v0','lighthouse_dune_v1','lighthouse_pacific_headland_v2','lighthouse_fortress_v3']) }),
  park_lake_edge_timber_deck_v2: Object.freeze({ lake_edge_plaza: fourVariantMappings('lake_edge_plaza', ['lake_edge_plaza_v0_como_skin','lake_edge_plaza_v1_geneva_skin','lake_edge_plaza_v2_timber_skin','lake_edge_plaza_v3_chicago_skin'], ['lake_edge_como_v0','lake_edge_geneva_v1','lake_edge_timber_deck_v2','lake_edge_chicago_v3']) }),
  park_stormwater_natural_creek_v0: Object.freeze({ stormwater_naturalized_drainage_corridor: fourNamedVariantMappings('stormwater_naturalized_drainage_corridor', ['stormwater_naturalized_drainage_corridor_v0_creek_skin','stormwater_naturalized_drainage_corridor_v1_daylit_skin','stormwater_naturalized_drainage_corridor_v2_seasonal_skin','stormwater_naturalized_drainage_corridor_v3_shelter_skin'], ['stormwater_natural_creek_v0','stormwater_daylit_v1','stormwater_seasonal_v2','stormwater_shelter_v3']) }),
  park_surface_parking_standard_v0: Object.freeze({ surface_parking_lot: fourVariantMappings('surface_parking_lot', ['surface_parking_lot_v0_standard_skin','surface_parking_lot_v1_green_skin','surface_parking_lot_v2_urban_skin','surface_parking_lot_v3_screened_skin'], ['surface_parking_standard_v0','surface_parking_green_v1','surface_parking_urban_v2','surface_parking_screened_v3']) }),
  park_structured_parking_urban_v2: Object.freeze({ structured_parking_garage: fourVariantMappings('structured_parking_garage', ['structured_parking_garage_v0_standard_skin','structured_parking_garage_v1_green_skin','structured_parking_garage_v2_urban_skin','structured_parking_garage_v3_screened_skin'], ['structured_parking_standard_v0','structured_parking_green_v1','structured_parking_urban_v2','structured_parking_screened_v3']) }),
  park_underground_parking_green_v1: Object.freeze({ underground_parking_entry: fourVariantMappings('underground_parking_entry', ['underground_parking_entry_v0_standard_skin','underground_parking_entry_v1_green_skin','underground_parking_entry_v2_urban_skin','underground_parking_entry_v3_screened_skin'], ['underground_parking_standard_v0','underground_parking_green_v1','underground_parking_urban_v2','underground_parking_screened_v3']) }),
  park_green_parking_infrastructure_v1: Object.freeze({ green_parking_lot: fourVariantMappings('green_parking_lot', ['green_parking_lot_v0_standard_skin','green_parking_lot_v1_infrastructure_skin','green_parking_lot_v2_urban_skin','green_parking_lot_v3_screened_skin'], ['green_parking_standard_v0','green_parking_infrastructure_v1','green_parking_urban_v2','green_parking_screened_v3']) }),
  park_airport_general_aviation_v2: Object.freeze({ airport_airfield: fourNamedVariantMappings('airport_airfield', ['airport_airfield_v0_major_hub_skin','airport_airfield_v1_regional_skin','airport_airfield_v2_general_aviation_skin','airport_airfield_v3_mid_size_skin'], ['airport_major_hub_v0','airport_regional_v1','airport_general_aviation_v2','airport_mid_size_v3']) }),
  park_equestrian_working_stable_v1: Object.freeze({ equestrian_center: fourNamedVariantMappings('equestrian_center', ['equestrian_center_v0_boarding_skin','equestrian_center_v1_working_stable_skin','equestrian_center_v2_competition_skin','equestrian_center_v3_academy_skin'], ['equestrian_boarding_v0','equestrian_working_stable_v1','equestrian_competition_v2','equestrian_academy_v3']) }),
  park_golf_seaside_links_v0: Object.freeze({ golf_course_18_hole: fourNamedVariantMappings('golf_course_18_hole', ['golf_course_18_hole_v0_links_skin','golf_course_18_hole_v1_parkland_skin','golf_course_18_hole_v2_desert_skin','golf_course_18_hole_v3_modern_club_skin'], ['golf_seaside_links_v0','golf_parkland_v1','golf_desert_v2','golf_modern_club_v3']) }),
  park_driving_range_single_tier_v0: Object.freeze({ golf_driving_range: fourNamedVariantMappings('golf_driving_range', ['golf_driving_range_v0_single_tier_skin','golf_driving_range_v1_entertainment_skin','golf_driving_range_v2_parkland_skin','golf_driving_range_v3_modern_skin'], ['driving_range_single_tier_v0','driving_range_entertainment_v1','driving_range_parkland_v2','driving_range_modern_v3']) }),
  park_multi_sport_track_field_v3: Object.freeze({ multi_sport_complex: fourNamedVariantMappings('multi_sport_complex', ['multi_sport_complex_v0_community_skin','multi_sport_complex_v1_stadium_skin','multi_sport_complex_v2_dome_skin','multi_sport_complex_v3_track_field_skin'], ['multi_sport_community_v0','multi_sport_stadium_v1','multi_sport_dome_v2','multi_sport_track_field_v3']) }),
  park_retail_parking_landscaped_v1: Object.freeze({ suburban_retail_parking_lot: fourVariantMappings('suburban_retail_parking_lot', ['suburban_retail_parking_lot_v0_big_box_skin','suburban_retail_parking_lot_v1_landscaped_skin','suburban_retail_parking_lot_v2_gravel_skin','suburban_retail_parking_lot_v3_plaza_skin'], ['retail_parking_big_box_v0','retail_parking_landscaped_v1','retail_parking_gravel_v2','retail_parking_plaza_v3']) }),
});

function normalizeId(value: unknown): string {
  return String(value ?? '').trim().toLowerCase().replace(/-/g, '_');
}

function isFamilyId(value: string): value is ParkLegoFamilyId {
  return (PARK_LEGO_FAMILY_IDS as readonly string[]).includes(value);
}

const LOWERCASE_HEX_64 = /^[0-9a-f]{64}$/;

function isTrustedRecipeHash(value: unknown): value is string {
  return typeof value === 'string' && LOWERCASE_HEX_64.test(value);
}

function familyForArchetype(archetypeId: string, role: string): ParkLegoFamilyId | null {
  if (archetypeId.startsWith('urban_pocket_park')) {
    return 'park_pocket_courtyard';
  }
  if (
    archetypeId.startsWith('neighborhood_park')
    || archetypeId.startsWith('community_park')
  ) {
    return 'park_neighborhood_community';
  }
  if (archetypeId.startsWith('formal_civic_plaza')) return 'park_civic_plaza';
  if (archetypeId.startsWith('linear_park_greenway')) return 'park_linear_greenway';
  if (archetypeId === 'skate_park') return 'park_skate_archetype_v0';
  if (archetypeId === 'inclusive_playground') return 'park_inclusive_playground_v0';
  if (archetypeId === 'dog_park') return 'park_dog_archetype_v0';
  if (archetypeId === 'splash_pad_area') return 'park_splash_pad_v0';
  if (archetypeId === 'community_garden') return 'park_community_garden_v0';
  if (archetypeId === 'basketball_court') return 'park_basketball_court_v0';
  if (archetypeId === 'tennis_court_cluster') return 'park_tennis_cluster_v0';
  if (archetypeId === 'soccer_pitch_caged') return 'park_caged_soccer_v0';
  if (archetypeId === 'athletics_precinct_sports_fields') return 'park_athletics_fields_v0';
  if (archetypeId === 'nature_play_area') return 'park_nature_play_v0';
  if (archetypeId === 'pump_track') return 'park_pump_track_v0';
  if (archetypeId === 'outdoor_fitness_circuit') return 'park_outdoor_fitness_v0';
  if (archetypeId === 'memorial_garden') return 'park_memorial_garden_v0';
  if (archetypeId === 'pickleball_courts') return 'park_pickleball_community_v1';
  if (archetypeId === 'running_track_oval') return 'park_track_oval_school_v2';
  if (archetypeId === 'baseball_softball_diamond') return 'park_baseball_club_hub_v1';
  if (archetypeId === 'cricket_pitch_oval') return 'park_cricket_village_green_v0';
  if (archetypeId === 'sports_field_complex') return 'park_sports_complex_tournament_v0';
  if (
    archetypeId.startsWith('stormwater_retention_pond')
    || archetypeId === 'pond_lake'
    || archetypeId === 'wetland_rain_garden'
    || archetypeId === 'riparian_buffer'
    || archetypeId === 'reservoir_watershed_park'
  ) return 'park_water_ecology';
  if (archetypeId === 'japanese_garden' || archetypeId === 'botanical_garden') {
    return 'park_cultural_gardens';
  }
  if (archetypeId === 'urban_forest') return 'park_urban_forest';
  if (archetypeId === 'amphitheater_lawn') return 'park_amphitheater_lawn_v0';
  if (archetypeId === 'playground_adventure') return 'park_playground_adventure_v0';
  if (archetypeId === 'disc_golf_course') return 'park_disc_golf_wooded_v0';
  if (archetypeId === 'bocce_petanque_court') return 'park_bocce_piazza_v0';
  if (archetypeId === 'climbing_bouldering_wall') return 'park_climbing_competition_v0';
  if (archetypeId === 'mini_golf_course') return 'park_mini_golf_classic_v0';
  if (archetypeId === 'beach_volleyball_courts') return 'park_beach_volleyball_competition_v0';
  if (archetypeId === 'pollinator_meadow') return 'park_pollinator_prairie_v0';
  if (archetypeId === 'urban_orchard_food_forest') return 'park_orchard_heritage_v0';
  if (archetypeId === 'bioswale_rain_garden') return 'park_bioswale_streetside_v0';
  if (archetypeId === 'sculpture_garden') return 'park_sculpture_museum_court_v0';
  if (archetypeId === 'labyrinth_meditation') return 'park_labyrinth_classical_v0';
  if (archetypeId === 'outdoor_ice_rink') return 'park_ice_rink_multipurpose_v3';
  if (archetypeId === 'kayak_launch_dock') return 'park_kayak_river_launch_v0';
  if (archetypeId === 'tidal_marsh_boardwalk') return 'park_tidal_marsh_cordgrass_v0';
  if (archetypeId === 'outdoor_cinema_lawn') return 'park_cinema_lawn_projection_v1';
  if (archetypeId === 'food_truck_plaza') return 'park_food_truck_permanent_v1';
  if (archetypeId === 'festival_event_lawn') return 'park_great_lawn_v2';
  if (archetypeId === 'campus_central_quad') return 'park_campus_meadow_quad_v0';
  if (archetypeId === 'urban_beach') return 'park_urban_beach_family_v2';
  if (archetypeId === 'velodrome_cycling_track') return 'park_velodrome_open_air_v0';
  if (archetypeId === 'mountain_bike_park') return 'park_mtb_skills_dirt_v2';
  if (archetypeId === 'regional_park') return 'park_regional_english_landscape_v0';
  if (archetypeId === 'beer_garden') return 'park_beer_garden_munich_v0';
  if (archetypeId === 'sunken_plaza') return 'park_sunken_courtyard_v0';
  if (archetypeId === 'stepped_terraced_plaza') return 'park_terraced_cascade_v3';
  if (archetypeId === 'market_square') return 'park_market_festival_lawn_v1';
  if (archetypeId === 'promenade_boardwalk') return 'park_boardwalk_maritime_v0';
  if (archetypeId === 'fountain_water_feature') return 'park_fountain_formal_pool_v1';
  if (archetypeId === 'swimming_pool_complex') return 'park_natural_swimming_pond_v0';
  if (archetypeId === 'nature_preserve') return 'park_nature_preserve_prairie_v1';
  if (archetypeId === 'riverfront_park_beach') return 'park_riverfront_lake_beach_v1';
  if (archetypeId === 'reclaimed_industrial_park') return 'park_reclaimed_wharf_v0';
  if (archetypeId === 'quarry_sunken_garden_park') return 'park_quarry_tier_cascade_v2';
  if (archetypeId === 'estate_picnic_grove') return 'park_estate_oak_picnic_v1';
  if (archetypeId === 'constructed_wetland_eco_park') return 'park_constructed_wetland_boardwalk_v0';
  if (archetypeId === 'academic_courtyard') return 'park_academic_planted_court_v0';
  if (archetypeId === 'campus_pedestrian_spine') return 'park_campus_green_spine_v0';
  if (archetypeId === 'research_garden_teaching_arboretum') return 'park_research_arboretum_v0';
  if (archetypeId === 'rewilding_ecological_restoration_zone') return 'park_rewilding_reforestation_v1';
  if (archetypeId === 'stormwater_resilience_park') return 'park_stormwater_arid_channel_v3';
  if (archetypeId === 'parisian_place') return 'park_paris_place_royale_v2';
  if (archetypeId === 'parisian_square') return 'park_paris_square_tree_grid_v3';
  if (archetypeId === 'parisian_jardin') return 'park_french_parterre_axis_v1';
  if (archetypeId === 'amsterdam_hofje_garden') return 'park_amsterdam_hofje_garden_v0';
  if (archetypeId === 'amsterdam_plein') return 'park_amsterdam_plein_v0';
  if (archetypeId === 'amsterdam_vondelpark') return 'park_amsterdam_vondelpark_pavilion_v3';
  if (archetypeId === 'barcelona_pati_interior') return 'park_barcelona_pati_green_v0';
  if (archetypeId === 'barcelona_placa_xamfra') return 'park_barcelona_xamfra_corner_v2';
  if (archetypeId === 'barcelona_superilla') return 'park_barcelona_superilla_green_v1';
  if (archetypeId === 'london_circus') return 'park_london_circus_planted_v1';
  if (archetypeId === 'newyork_pocket_park') return 'park_newyork_pocket_water_v0';
  if (archetypeId === 'newyork_community_garden') return 'park_newyork_community_greenhouse_v3';
  if (archetypeId === 'vancouver_seawall') return 'park_vancouver_seawall_cycle_v2';
  if (archetypeId === 'vancouver_beach_park') return 'park_vancouver_beach_pavilion_v0';
  if (archetypeId === 'toronto_ravine') return 'park_toronto_ravine_creek_v1';
  if (archetypeId === 'toronto_urban_square') return 'park_toronto_urban_market_v1';
  if (archetypeId === 'halifax_coastal_park') return 'park_halifax_coastal_fog_path_v2';
  if (archetypeId === 'city_hall_government_plaza') return 'park_city_hall_modernist_fountain_v2';
  if (archetypeId === 'cathedral_religious_forecourt') return 'park_cathedral_courtyard_fountain_v3';
  if (archetypeId === 'cultural_institution_forecourt') return 'park_cultural_museum_terrace_v0';
  if (archetypeId === 'transit_plaza') return 'park_transit_green_civic_v2';
  if (archetypeId === 'amphitheater_performance_space') return 'park_amphitheater_terraced_v0';
  if (archetypeId === 'concert_pavilion_lawn') return 'park_concert_timber_lawn_v2';
  if (archetypeId === 'night_market') return 'park_night_market_hawker_v0';
  if (archetypeId === 'parade_ground') return 'park_parade_national_mall_v3';
  if (archetypeId === 'canal_waterway') return 'park_canal_ecological_wetland_v3';
  if (archetypeId === 'custom_parks_plazas') return 'park_custom_biophilic_urban_v1';
  if (archetypeId === 'rooftop_garden') return 'park_rooftop_intensive_garden_v0';
  if (archetypeId === 'community_garden_enhanced') return 'park_community_healing_garden_v2';
  if (archetypeId === 'greenbelt_buffer_park') return 'park_greenbelt_rail_trail_v1';
  if (archetypeId === 'foothill_trail_park') return 'park_foothill_heathland_trail_v2';
  if (archetypeId === 'marina_yacht_harbor') return 'park_marina_pacific_dock_v2';
  if (archetypeId === 'working_pier_wharf_conversion') return 'park_working_pier_brooklyn_park_v3';
  if (archetypeId === 'floating_park_pool') return 'park_floating_meadow_loop_v2';
  if (archetypeId === 'lighthouse_point_park') return 'park_lighthouse_pacific_headland_v2';
  if (archetypeId === 'lake_edge_plaza') return 'park_lake_edge_timber_deck_v2';
  if (archetypeId === 'stormwater_naturalized_drainage_corridor') return 'park_stormwater_natural_creek_v0';
  if (archetypeId === 'surface_parking_lot') return 'park_surface_parking_standard_v0';
  if (archetypeId === 'structured_parking_garage') return 'park_structured_parking_urban_v2';
  if (archetypeId === 'underground_parking_entry') return 'park_underground_parking_green_v1';
  if (archetypeId === 'green_parking_lot') return 'park_green_parking_infrastructure_v1';
  if (archetypeId === 'airport_airfield') return 'park_airport_general_aviation_v2';
  if (archetypeId === 'equestrian_center') return 'park_equestrian_working_stable_v1';
  if (archetypeId === 'golf_course_18_hole') return 'park_golf_seaside_links_v0';
  if (archetypeId === 'golf_driving_range') return 'park_driving_range_single_tier_v0';
  if (archetypeId === 'multi_sport_complex') return 'park_multi_sport_track_field_v3';
  if (archetypeId === 'suburban_retail_parking_lot') return 'park_retail_parking_landscaped_v1';
  if (!archetypeId && role === 'courtyard') return 'park_pocket_courtyard';
  return null;
}

function defaultArchetype(familyId: ParkLegoFamilyId): string {
  switch (familyId) {
    case 'park_pocket_courtyard': return 'urban_pocket_park';
    case 'park_neighborhood_community': return 'neighborhood_park';
    case 'park_civic_plaza': return 'formal_civic_plaza';
    case 'park_linear_greenway': return 'linear_park_greenway';
    case 'park_skate_archetype_v0': return 'skate_park';
    case 'park_inclusive_playground_v0': return 'inclusive_playground';
    case 'park_dog_archetype_v0': return 'dog_park';
    case 'park_splash_pad_v0': return 'splash_pad_area';
    case 'park_community_garden_v0': return 'community_garden';
    case 'park_basketball_court_v0': return 'basketball_court';
    case 'park_tennis_cluster_v0': return 'tennis_court_cluster';
    case 'park_caged_soccer_v0': return 'soccer_pitch_caged';
    case 'park_athletics_fields_v0': return 'athletics_precinct_sports_fields';
    case 'park_nature_play_v0': return 'nature_play_area';
    case 'park_pump_track_v0': return 'pump_track';
    case 'park_outdoor_fitness_v0': return 'outdoor_fitness_circuit';
    case 'park_memorial_garden_v0': return 'memorial_garden';
    case 'park_pickleball_community_v1': return 'pickleball_courts';
    case 'park_track_oval_school_v2': return 'running_track_oval';
    case 'park_baseball_club_hub_v1': return 'baseball_softball_diamond';
    case 'park_cricket_village_green_v0': return 'cricket_pitch_oval';
    case 'park_sports_complex_tournament_v0': return 'sports_field_complex';
    case 'park_water_ecology': return 'stormwater_retention_pond';
    case 'park_cultural_gardens': return 'japanese_garden';
    case 'park_urban_forest': return 'urban_forest';
    case 'park_amphitheater_lawn_v0': return 'amphitheater_lawn';
    case 'park_playground_adventure_v0': return 'playground_adventure';
    case 'park_disc_golf_wooded_v0': return 'disc_golf_course';
    case 'park_bocce_piazza_v0': return 'bocce_petanque_court';
    case 'park_climbing_competition_v0': return 'climbing_bouldering_wall';
    case 'park_mini_golf_classic_v0': return 'mini_golf_course';
    case 'park_beach_volleyball_competition_v0': return 'beach_volleyball_courts';
    case 'park_pollinator_prairie_v0': return 'pollinator_meadow';
    case 'park_orchard_heritage_v0': return 'urban_orchard_food_forest';
    case 'park_bioswale_streetside_v0': return 'bioswale_rain_garden';
    case 'park_sculpture_museum_court_v0': return 'sculpture_garden';
    case 'park_labyrinth_classical_v0': return 'labyrinth_meditation';
    case 'park_ice_rink_multipurpose_v3': return 'outdoor_ice_rink';
    case 'park_kayak_river_launch_v0': return 'kayak_launch_dock';
    case 'park_tidal_marsh_cordgrass_v0': return 'tidal_marsh_boardwalk';
    case 'park_cinema_lawn_projection_v1': return 'outdoor_cinema_lawn';
    case 'park_food_truck_permanent_v1': return 'food_truck_plaza';
    case 'park_great_lawn_v2': return 'festival_event_lawn';
    case 'park_campus_meadow_quad_v0': return 'campus_central_quad';
    case 'park_urban_beach_family_v2': return 'urban_beach';
    case 'park_velodrome_open_air_v0': return 'velodrome_cycling_track';
    case 'park_mtb_skills_dirt_v2': return 'mountain_bike_park';
    case 'park_regional_english_landscape_v0': return 'regional_park';
    case 'park_beer_garden_munich_v0': return 'beer_garden';
    case 'park_sunken_courtyard_v0': return 'sunken_plaza';
    case 'park_terraced_cascade_v3': return 'stepped_terraced_plaza';
    case 'park_market_festival_lawn_v1': return 'market_square';
    case 'park_boardwalk_maritime_v0': return 'promenade_boardwalk';
    case 'park_fountain_formal_pool_v1': return 'fountain_water_feature';
    case 'park_natural_swimming_pond_v0': return 'swimming_pool_complex';
    case 'park_nature_preserve_prairie_v1': return 'nature_preserve';
    case 'park_riverfront_lake_beach_v1': return 'riverfront_park_beach';
    case 'park_reclaimed_wharf_v0': return 'reclaimed_industrial_park';
    case 'park_quarry_tier_cascade_v2': return 'quarry_sunken_garden_park';
    case 'park_estate_oak_picnic_v1': return 'estate_picnic_grove';
    case 'park_constructed_wetland_boardwalk_v0': return 'constructed_wetland_eco_park';
    case 'park_academic_planted_court_v0': return 'academic_courtyard';
    case 'park_campus_green_spine_v0': return 'campus_pedestrian_spine';
    case 'park_botanical_rose_garden_v3': return 'botanical_garden';
    case 'park_research_arboretum_v0': return 'research_garden_teaching_arboretum';
    case 'park_rewilding_reforestation_v1': return 'rewilding_ecological_restoration_zone';
    case 'park_stormwater_arid_channel_v3': return 'stormwater_resilience_park';
    case 'park_urban_pocket_rustic_v0': return 'urban_pocket_park';
    case 'park_neighborhood_contemporary_v3': return 'neighborhood_park';
    case 'park_cemetery_classical_v0': return 'cemetery_memorial_grounds';
    case 'park_courtyard_linear_water_v1': return 'courtyard_plaza';
    case 'park_parklet_sf_timber_v1': return 'street_plaza_parklet';
    case 'park_french_parterre_axis_v1': return 'parisian_jardin';
    case 'park_london_railed_square_v1': return 'london_garden_square';
    case 'park_halifax_rose_bandstand_v0': return 'halifax_public_gardens';
    case 'park_olmsted_multilandscape_v3': return 'picturesque_olmsted_park';
    case 'park_hilltop_viewpoint_v3': return 'hilltop_topographic_park';
    case 'park_amsterdam_hofje_garden_v0': return 'amsterdam_hofje_garden';
    case 'park_amsterdam_plein_v0': return 'amsterdam_plein';
    case 'park_amsterdam_vondelpark_pavilion_v3': return 'amsterdam_vondelpark';
    case 'park_barcelona_pati_green_v0': return 'barcelona_pati_interior';
    case 'park_barcelona_xamfra_corner_v2': return 'barcelona_placa_xamfra';
    case 'park_barcelona_superilla_green_v1': return 'barcelona_superilla';
    case 'park_calgary_prairie_market_v1': return 'calgary_prairie_plaza';
    case 'park_calgary_princes_island_festival_v0': return 'calgary_princes_island';
    case 'park_montreal_mount_royal_grove_v2': return 'montreal_mount_royal';
    case 'park_montreal_neighbourhood_square_v3': return 'montreal_square';
    case 'park_paris_place_royale_v2': return 'parisian_place';
    case 'park_paris_square_tree_grid_v3': return 'parisian_square';
    case 'park_london_circus_planted_v1': return 'london_circus';
    case 'park_newyork_pocket_water_v0': return 'newyork_pocket_park';
    case 'park_newyork_community_greenhouse_v3': return 'newyork_community_garden';
    case 'park_vancouver_seawall_cycle_v2': return 'vancouver_seawall';
    case 'park_vancouver_beach_pavilion_v0': return 'vancouver_beach_park';
    case 'park_toronto_ravine_creek_v1': return 'toronto_ravine';
    case 'park_toronto_urban_market_v1': return 'toronto_urban_square';
    case 'park_halifax_coastal_fog_path_v2': return 'halifax_coastal_park';
    case 'park_city_hall_modernist_fountain_v2': return 'city_hall_government_plaza';
    case 'park_cathedral_courtyard_fountain_v3': return 'cathedral_religious_forecourt';
    case 'park_cultural_museum_terrace_v0': return 'cultural_institution_forecourt';
    case 'park_transit_green_civic_v2': return 'transit_plaza';
    case 'park_amphitheater_terraced_v0': return 'amphitheater_performance_space';
    case 'park_concert_timber_lawn_v2': return 'concert_pavilion_lawn';
    case 'park_night_market_hawker_v0': return 'night_market';
    case 'park_parade_national_mall_v3': return 'parade_ground';
    case 'park_canal_ecological_wetland_v3': return 'canal_waterway';
    case 'park_custom_biophilic_urban_v1': return 'custom_parks_plazas';
    case 'park_rooftop_intensive_garden_v0': return 'rooftop_garden';
    case 'park_community_healing_garden_v2': return 'community_garden_enhanced';
    case 'park_greenbelt_rail_trail_v1': return 'greenbelt_buffer_park';
    case 'park_foothill_heathland_trail_v2': return 'foothill_trail_park';
    case 'park_marina_pacific_dock_v2': return 'marina_yacht_harbor';
    case 'park_working_pier_brooklyn_park_v3': return 'working_pier_wharf_conversion';
    case 'park_floating_meadow_loop_v2': return 'floating_park_pool';
    case 'park_lighthouse_pacific_headland_v2': return 'lighthouse_point_park';
    case 'park_lake_edge_timber_deck_v2': return 'lake_edge_plaza';
    case 'park_stormwater_natural_creek_v0': return 'stormwater_naturalized_drainage_corridor';
    case 'park_surface_parking_standard_v0': return 'surface_parking_lot';
    case 'park_structured_parking_urban_v2': return 'structured_parking_garage';
    case 'park_underground_parking_green_v1': return 'underground_parking_entry';
    case 'park_green_parking_infrastructure_v1': return 'green_parking_lot';
    case 'park_airport_general_aviation_v2': return 'airport_airfield';
    case 'park_equestrian_working_stable_v1': return 'equestrian_center';
    case 'park_golf_seaside_links_v0': return 'golf_course_18_hole';
    case 'park_driving_range_single_tier_v0': return 'golf_driving_range';
    case 'park_multi_sport_track_field_v3': return 'multi_sport_complex';
    case 'park_retail_parking_landscaped_v1': return 'suburban_retail_parking_lot';
  }
}

function canonicalVariantId(archetypeId: string, raw: unknown): { id: string; index: number } {
  const normalized = normalizeId(raw);
  const exactFamilyId = familyForArchetype(archetypeId, '');
  const exactSelections = exactFamilyId
    ? PARK_FAMILY_SELECTIONS[exactFamilyId][archetypeId] ?? []
    : [];
  const exactIndex = exactSelections.findIndex((candidate) => candidate.variantId === normalized);
  if (exactIndex >= 0) return { id: normalized, index: exactIndex };
  const match = normalized.match(/(?:_variant_|_v)([0-3])$/);
  const index = match ? Number(match[1]) : 0;
  return {
    id: [
      'athletics_precinct_sports_fields',
      'campus_central_quad',
      'velodrome_cycling_track',
      'mountain_bike_park',
      'constructed_wetland_eco_park',
      'academic_courtyard',
      'campus_pedestrian_spine',
      'research_garden_teaching_arboretum',
      'rewilding_ecological_restoration_zone',
      'stormwater_resilience_park',
    ].includes(archetypeId)
      ? `${archetypeId}_variant_${index}`
      : `${archetypeId}_v${index}`,
    index,
  };
}

/** Resolve the nested compiler contract first, then legacy archetype fields.
 * Unsupported future family versions remain visible as contracts but are not
 * treated as executable V1 by the live procedural renderer. */
export function resolveParkLegoContract(zone: ParkLegoZone): ParkLegoContract | null {
  const props = (zone.properties ?? {}) as Record<string, unknown>;
  const nested = props.public_realm_lego && typeof props.public_realm_lego === 'object'
    ? props.public_realm_lego as Record<string, unknown>
    : null;
  const role = normalizeId(props._plan_role);
  const legacyArchetype = normalizeId(
    props.green_space_archetype_id ?? props.plaza_archetype_id,
  );

  if (nested) {
    const nestedFamily = typeof nested.family_id === 'string' ? nested.family_id : '';
    if (!isFamilyId(nestedFamily)) return null;
    const familyId = nestedFamily;
    const familyVersion = typeof nested.family_version === 'number'
      ? nested.family_version
      : Number.NaN;
    const schemaVersion = typeof nested.schema_version === 'number'
      ? nested.schema_version
      : Number.NaN;
    const kind = typeof nested.kind === 'string' ? nested.kind : '';
    const generator = typeof nested.generator === 'string' ? nested.generator : '';
    const archetypeId = typeof nested.archetype_id === 'string' ? nested.archetype_id : '';
    const variantId = typeof nested.variant_id === 'string' ? nested.variant_id : '';
    const plantingStructure = typeof nested.planting_structure === 'string'
      ? nested.planting_structure
      : '';
    const appearanceKitId = typeof nested.appearance_kit_id === 'string'
      ? nested.appearance_kit_id
      : '';
    const selection = PARK_FAMILY_SELECTIONS[familyId][archetypeId]?.find(
      (candidate) => candidate.variantId === variantId,
    );
    const mappingIsExact = Boolean(
      selection
      && selection.appearanceKitId === appearanceKitId
      && selection.plantingStructure === plantingStructure,
    );
    const catalogFingerprint = nested?.catalog_fingerprint;
    const capabilityFingerprint = nested?.capability_fingerprint;
    const recipeHash = nested?.recipe_hash;
    const trustedRecipeIdentity = schemaVersion === 1
      && kind === 'park'
      && generator === 'park_kit'
      && isTrustedRecipeHash(catalogFingerprint)
      && isTrustedRecipeHash(capabilityFingerprint)
      && isTrustedRecipeHash(recipeHash);
    return {
      familyId,
      familyVersion,
      archetypeId,
      variantId,
      source: 'public_realm_lego',
      supported: familyVersion === PARK_LEGO_FAMILY_VERSION
        && mappingIsExact
        && trustedRecipeIdentity,
      ...(Number.isFinite(schemaVersion) ? { schemaVersion } : {}),
      ...(kind ? { kind } : {}),
      ...(generator ? { generator } : {}),
      ...(plantingStructure ? { plantingStructure } : {}),
      ...(appearanceKitId ? { appearanceKitId } : {}),
      ...(typeof catalogFingerprint === 'string'
        ? { catalogFingerprint }
        : {}),
      ...(typeof capabilityFingerprint === 'string'
        ? { capabilityFingerprint }
        : {}),
      ...(typeof recipeHash === 'string'
        ? { recipeHash }
        : {}),
    };
  }

  const familyId = familyForArchetype(legacyArchetype, role);
  if (!familyId) return null;
  const archetypeId = legacyArchetype || defaultArchetype(familyId);
  const variant = canonicalVariantId(
    archetypeId,
    props.green_space_selected_variant_id ?? props.plaza_selected_variant_id,
  );
  const legacySelection = PARK_FAMILY_SELECTIONS[familyId][archetypeId]?.find(
    (candidate) => candidate.variantId === variant.id,
  );
  return {
    familyId,
    familyVersion: PARK_LEGO_FAMILY_VERSION,
    archetypeId,
    variantId: variant.id,
    source: 'legacy',
    supported: Boolean(legacySelection),
  };
}

export function resolveParkLegoAppearance(zone: ParkLegoZone): ParkLegoAppearance | null {
  const contract = resolveParkLegoContract(zone);
  if (!contract?.supported) return null;
  if (
    contract.familyId !== 'park_pocket_courtyard'
    && contract.familyId !== 'park_neighborhood_community'
  ) return null;
  const variantIndex = canonicalVariantId(contract.archetypeId, contract.variantId).index;
  const variants = contract.familyId === 'park_pocket_courtyard'
    ? POCKET_VARIANTS
    : contract.archetypeId.startsWith('community_park')
      ? COMMUNITY_VARIANTS
      : NEIGHBORHOOD_VARIANTS;
  const definition = variants[variantIndex] ?? variants[0];
  const contractPlanting = contract.plantingStructure;
  const knownPlanting = (
    contractPlanting === 'garden_courtyard'
    || contractPlanting === 'formal_quad'
    || contractPlanting === 'naturalistic_grove'
    || contractPlanting === 'open_meadow'
    || contractPlanting === 'active_recreation'
  ) ? contractPlanting : null;
  // The neighborhood/community family always owns playground and pavilion
  // programs. Formal-quad/garden furniture rules intentionally suppress those
  // modules, so they are incompatible even if a stale caller requests them.
  const plantingStructure = knownPlanting && (
    contract.familyId === 'park_pocket_courtyard'
    || knownPlanting === 'active_recreation'
    || knownPlanting === 'naturalistic_grove'
    || knownPlanting === 'open_meadow'
  ) ? knownPlanting : definition.plantingStructure;
  return {
    familyId: contract.familyId,
    familyVersion: PARK_LEGO_FAMILY_VERSION,
    archetypeId: contract.archetypeId,
    variantId: `${contract.archetypeId}_v${variantIndex}`,
    variantIndex,
    ...definition,
    plantingStructure,
  };
}

export function isExecutableParkLegoFamily(zone: ParkLegoZone): boolean {
  return resolveParkLegoContract(zone)?.supported === true;
}

/** Archetype-owned surface and depth kits bypass the paid AI drape. Their
 * exact material bundle and fixed geometry are the visual source of truth. */
export function usesArchetypeOwnedParkSurface(zone: ParkLegoZone): boolean {
  const contract = resolveParkLegoContract(zone);
  if (contract?.supported !== true) return false;
  if (
    contract.familyId === 'park_basketball_court_v0'
    || contract.familyId === 'park_caged_soccer_v0'
    || contract.familyId === 'park_athletics_fields_v0'
  ) return true;
  if (batch4ParkSkinForSelection(contract.archetypeId, contract.variantId)) return true;
  if (batch5ParkSkinForSelection(contract.archetypeId, contract.variantId)) return true;
  if (batch6ParkSkinForSelection(contract.archetypeId, contract.variantId)) return true;
  if (batch7ParkSkinForSelection(contract.archetypeId, contract.variantId)) return true;
  if (batch8ParkSkinForSelection(contract.archetypeId, contract.variantId)) return true;
  if (batch9ParkSkinForSelection(contract.archetypeId, contract.variantId)) return true;
  if (batch10ParkSkinForSelection(contract.archetypeId, contract.variantId)) return true;
  if (batch11ParkSkinForSelection(contract.archetypeId, contract.variantId)) return true;
  if (batch12ParkSkinForSelection(contract.archetypeId, contract.variantId)) return true;
  if (batch13ParkSkinForSelection(contract.archetypeId, contract.variantId)) return true;
  if (batch14ParkSkinForSelection(contract.archetypeId, contract.variantId)) return true;
  if (batch15ParkSkinForSelection(contract.archetypeId, contract.variantId)) return true;
  if (batch16ParkSkinForSelection(contract.archetypeId, contract.variantId)) return true;
  if (batch17ParkSkinForSelection(contract.archetypeId, contract.variantId)) return true;
  if (batch18ParkSkinForSelection(contract.archetypeId, contract.variantId)) return true;
  if (batch19ParkSkinForSelection(contract.archetypeId, contract.variantId)) return true;
  if (batch20ParkSkinForSelection(contract.archetypeId, contract.variantId)) return true;
  if (batch21ParkSkinForSelection(contract.archetypeId, contract.variantId)) return true;
  if (batch22ParkSkinForSelection(contract.archetypeId, contract.variantId)) return true;
  if (batch23ParkSkinForSelection(contract.archetypeId, contract.variantId)) return true;
  if (batch24ParkSkinForSelection(contract.archetypeId, contract.variantId)) return true;
  if (batch25ParkSkinForSelection(contract.archetypeId, contract.variantId)) return true;
  if (batch26ParkSkinForSelection(contract.archetypeId, contract.variantId)) return true;
  if (batch27ParkSkinForSelection(contract.archetypeId, contract.variantId)) return true;
  const kit = archetypeOwnedParkKitForFamily(contract.familyId);
  const selection = archetypeOwnedParkKitForSelection(contract.archetypeId, contract.variantId);
  return kit !== null && selection?.familyId === kit.familyId;
}

/** Choose a lightweight scene-dressing family even when an archetype does
 * not yet have a full compiler family. This never claims LEGO compatibility:
 * it only weights safe procedural props after the ground drape is complete. */
export function resolveParkDressingFamily(zone: ParkLegoZone): ParkLegoFamilyId {
  const contract = resolveParkLegoContract(zone);
  if (contract?.supported) return contract.familyId;
  const props = (zone.properties ?? {}) as Record<string, unknown>;
  const archetypeId = normalizeId(
    props.green_space_archetype_id
      ?? props.plaza_archetype_id
      ?? props.green_space_aesthetic
      ?? props.plaza_aesthetic,
  );
  const role = normalizeId(props._plan_role);
  const zoneType = normalizeId(zone.zone_type);
  if (
    zoneType === 'plaza'
    || zoneType === 'parking'
    || role === 'plaza'
    || archetypeId.includes('plaza')
    || archetypeId.includes('square')
  ) return 'park_civic_plaza';
  if (
    archetypeId.includes('pond')
    || archetypeId.includes('wetland')
    || archetypeId.includes('reservoir')
    || archetypeId.includes('watershed')
    || archetypeId.includes('riparian')
  ) return 'park_water_ecology';
  if (
    archetypeId.includes('linear')
    || archetypeId.includes('greenway')
    || archetypeId.includes('promenade')
    || archetypeId.includes('riverfront')
  ) return 'park_linear_greenway';
  if (
    role === 'courtyard'
    || archetypeId.includes('pocket')
    || archetypeId.includes('courtyard')
    || archetypeId.includes('garden')
  ) return 'park_pocket_courtyard';
  return 'park_neighborhood_community';
}

/** Resolve an archetype-specific visual kit for post-drape scene dressing.
 * Unlike `resolveParkLegoAppearance`, this function does not imply that the
 * archetype has a compiler-owned LEGO family or authorize generic program
 * modules such as playgrounds and picnic shelters. */
export function resolveParkDressingAppearance(
  zone: ParkLegoZone,
): ParkLegoAppearance | null {
  const executableAppearance = resolveParkLegoAppearance(zone);
  if (executableAppearance) return executableAppearance;
  const props = (zone.properties ?? {}) as Record<string, unknown>;
  const archetypeId = normalizeId(
    props.green_space_archetype_id ?? props.plaza_archetype_id,
  );
  if (!archetypeId.startsWith('cricket_pitch_oval')) return null;
  const variant = canonicalVariantId(
    'cricket_pitch_oval',
    props.green_space_selected_variant_id ?? props.plaza_selected_variant_id,
  );
  const definition = CRICKET_DRESSING_VARIANTS[variant.index]
    ?? CRICKET_DRESSING_VARIANTS[0];
  return {
    familyId: 'park_neighborhood_community',
    familyVersion: PARK_LEGO_FAMILY_VERSION,
    archetypeId: 'cricket_pitch_oval',
    variantId: variant.id,
    variantIndex: variant.index,
    ...definition,
  };
}

export function resolveParkProgramAnchorLayout(
  zone: ParkLegoZone,
): Readonly<ParkProgramAnchorLayout> | undefined {
  const contract = resolveParkLegoContract(zone);
  return contract?.supported && contract.familyId === 'park_neighborhood_community'
    ? NEIGHBORHOOD_COMMUNITY_PROGRAM_ANCHORS
    : undefined;
}
