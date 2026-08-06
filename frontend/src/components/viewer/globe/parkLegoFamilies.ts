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
    formal_civic_plaza: Object.freeze([Object.freeze({
      variantId: 'formal_civic_plaza_v0',
      appearanceKitId: 'neoclassical_stone_v1',
      plantingStructure: 'paved_plaza',
    })]),
  }),
  park_linear_greenway: Object.freeze({
    linear_park_greenway: Object.freeze([Object.freeze({
      variantId: 'linear_park_greenway_v0',
      appearanceKitId: 'rail_trail_v1',
      plantingStructure: 'naturalistic_grove',
    })]),
  }),
  park_skate_archetype_v0: Object.freeze({
    skate_park: fourVariantMappings(
      'skate_park',
      ['skate_park_v0_reference_skin', 'skate_park_v1_community_recreation_skin', 'skate_park_v2_naturalized_active_skin', 'skate_park_v3_urban_athletic_skin'],
      ['skate_archetype_v0', 'skate_community_recreation_v1', 'skate_naturalized_active_v2', 'skate_urban_athletic_v3'],
    ),
  }),
  park_inclusive_playground_v0: Object.freeze({
    inclusive_playground: Object.freeze([Object.freeze({
      variantId: 'inclusive_playground_v0', appearanceKitId: 'inclusive_playground_v0_reference_skin', plantingStructure: 'inclusive_playground_v0',
    })]),
  }),
  park_dog_archetype_v0: Object.freeze({
    dog_park: fourVariantMappings(
      'dog_park',
      ['dog_park_v0_reference_skin', 'dog_park_v1_modern_steel_turf_skin', 'dog_park_v2_natural_meadow_skin', 'dog_park_v3_urban_contemporary_skin'],
      ['dog_park_v0', 'dog_modern_steel_turf_v1', 'dog_natural_meadow_v2', 'dog_urban_contemporary_v3'],
    ),
  }),
  park_splash_pad_v0: Object.freeze({
    splash_pad_area: Object.freeze([Object.freeze({
      variantId: 'splash_pad_area_v0', appearanceKitId: 'splash_pad_area_v0_reference_skin', plantingStructure: 'splash_pad_area_v0',
    })]),
  }),
  park_community_garden_v0: Object.freeze({
    community_garden: Object.freeze([Object.freeze({
      variantId: 'community_garden_v0', appearanceKitId: 'community_garden_v0_reference_skin', plantingStructure: 'community_garden_v0',
    })]),
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
    soccer_pitch_caged: Object.freeze([Object.freeze({
      variantId: 'soccer_pitch_caged_v0', appearanceKitId: 'soccer_pitch_caged_v0_reference_skin', plantingStructure: 'caged_soccer_v0',
    })]),
  }),
  park_athletics_fields_v0: Object.freeze({
    athletics_precinct_sports_fields: Object.freeze([Object.freeze({
      variantId: 'athletics_precinct_sports_fields_variant_0', appearanceKitId: 'athletics_precinct_sports_fields_v0_reference_skin', plantingStructure: 'athletics_fields_v0',
    })]),
  }),
  park_nature_play_v0: Object.freeze({
    nature_play_area: Object.freeze([Object.freeze({
      variantId: 'nature_play_area_v0', appearanceKitId: 'nature_play_area_v0_reference_skin', plantingStructure: 'nature_play_area_v0',
    })]),
  }),
  park_pump_track_v0: Object.freeze({
    pump_track: Object.freeze([Object.freeze({
      variantId: 'pump_track_v0', appearanceKitId: 'pump_track_v0_reference_skin', plantingStructure: 'pump_track_v0',
    })]),
  }),
  park_outdoor_fitness_v0: Object.freeze({
    outdoor_fitness_circuit: Object.freeze([Object.freeze({
      variantId: 'outdoor_fitness_circuit_v0', appearanceKitId: 'outdoor_fitness_circuit_v0_reference_skin', plantingStructure: 'outdoor_fitness_circuit_v0',
    })]),
  }),
  park_memorial_garden_v0: Object.freeze({
    memorial_garden: fourVariantMappings(
      'memorial_garden',
      ['memorial_garden_v0_reference_skin', 'memorial_garden_v1_woodland_naturalistic_skin', 'memorial_garden_v2_contemporary_sculptural_skin', 'memorial_garden_v3_cottage_romantic_skin'],
      ['memorial_garden_v0', 'memorial_woodland_v1', 'memorial_sculptural_v2', 'memorial_romantic_v3'],
    ),
  }),
  park_pickleball_community_v1: Object.freeze({
    pickleball_courts: Object.freeze([Object.freeze({
      variantId: 'pickleball_courts_v1', appearanceKitId: 'pickleball_courts_v1_multi_angle_skin', plantingStructure: 'pickleball_community_v1',
    })]),
  }),
  park_track_oval_school_v2: Object.freeze({
    running_track_oval: Object.freeze([Object.freeze({
      variantId: 'running_track_oval_v2', appearanceKitId: 'running_track_oval_v2_multi_angle_skin', plantingStructure: 'track_oval_school_v2',
    })]),
  }),
  park_baseball_club_hub_v1: Object.freeze({
    baseball_softball_diamond: Object.freeze([Object.freeze({
      variantId: 'baseball_softball_diamond_v1', appearanceKitId: 'baseball_softball_diamond_v1_multi_angle_skin', plantingStructure: 'baseball_club_hub_v1',
    })]),
  }),
  park_cricket_village_green_v0: Object.freeze({
    cricket_pitch_oval: Object.freeze([Object.freeze({
      variantId: 'cricket_pitch_oval_v0', appearanceKitId: 'cricket_pitch_oval_v0_multi_angle_skin', plantingStructure: 'cricket_village_green_v0',
    })]),
  }),
  park_sports_complex_tournament_v0: Object.freeze({
    sports_field_complex: fourVariantMappings(
      'sports_field_complex',
      ['sports_field_complex_v0_multi_angle_skin', 'sports_field_complex_v1_community_recreation_skin', 'sports_field_complex_v2_naturalized_active_skin', 'sports_field_complex_v3_urban_athletic_skin'],
      ['sports_complex_tournament_v0', 'sports_complex_community_v1', 'sports_complex_naturalized_v2', 'sports_complex_urban_v3'],
    ),
  }),
  park_water_ecology: Object.freeze({
    stormwater_retention_pond: Object.freeze([Object.freeze({
      variantId: 'stormwater_retention_pond_v0',
      appearanceKitId: 'naturalistic_pond_v1',
      plantingStructure: 'reservoir_perimeter',
    })]),
    pond_lake: Object.freeze([Object.freeze({
      variantId: 'pond_lake_v0', appearanceKitId: 'pond_lake_v0_naturalistic_skin', plantingStructure: 'pond_lake_v0',
    })]),
    wetland_rain_garden: Object.freeze([Object.freeze({
      variantId: 'wetland_rain_garden_v0', appearanceKitId: 'wetland_rain_garden_v0_native_restoration_skin', plantingStructure: 'wetland_rain_garden_v0',
    })]),
    riparian_buffer: Object.freeze([Object.freeze({
      variantId: 'riparian_buffer_v0', appearanceKitId: 'riparian_buffer_v0_native_restoration_skin', plantingStructure: 'riparian_buffer_v0',
    })]),
    reservoir_watershed_park: Object.freeze([Object.freeze({
      variantId: 'reservoir_watershed_park_v0', appearanceKitId: 'reservoir_watershed_park_v0_concrete_edge_skin', plantingStructure: 'reservoir_watershed_park_v0',
    })]),
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
    amphitheater_lawn: Object.freeze([Object.freeze({
      variantId: 'amphitheater_lawn_v0', appearanceKitId: 'amphitheater_lawn_v0_terraced_performance_skin', plantingStructure: 'amphitheater_lawn_v0',
    })]),
  }),
  park_playground_adventure_v0: Object.freeze({
    playground_adventure: Object.freeze([Object.freeze({
      variantId: 'playground_adventure_v0', appearanceKitId: 'playground_adventure_v0_rustic_timber_skin', plantingStructure: 'playground_adventure_v0',
    })]),
  }),
  park_disc_golf_wooded_v0: Object.freeze({
    disc_golf_course: Object.freeze([Object.freeze({ variantId: 'disc_golf_course_v0', appearanceKitId: 'disc_golf_course_v0_wooded_championship_skin', plantingStructure: 'disc_golf_wooded_v0' })]),
  }),
  park_bocce_piazza_v0: Object.freeze({
    bocce_petanque_court: Object.freeze([Object.freeze({ variantId: 'bocce_petanque_court_v0', appearanceKitId: 'bocce_petanque_court_v0_italian_piazza_skin', plantingStructure: 'bocce_piazza_v0' })]),
  }),
  park_climbing_competition_v0: Object.freeze({
    climbing_bouldering_wall: Object.freeze([Object.freeze({ variantId: 'climbing_bouldering_wall_v0', appearanceKitId: 'climbing_bouldering_wall_v0_competition_skin', plantingStructure: 'climbing_competition_v0' })]),
  }),
  park_mini_golf_classic_v0: Object.freeze({
    mini_golf_course: Object.freeze([Object.freeze({ variantId: 'mini_golf_course_v0', appearanceKitId: 'mini_golf_course_v0_classic_skin', plantingStructure: 'mini_golf_classic_v0' })]),
  }),
  park_beach_volleyball_competition_v0: Object.freeze({
    beach_volleyball_courts: Object.freeze([Object.freeze({ variantId: 'beach_volleyball_courts_v0', appearanceKitId: 'beach_volleyball_courts_v0_competition_skin', plantingStructure: 'beach_volleyball_competition_v0' })]),
  }),
  park_pollinator_prairie_v0: Object.freeze({
    pollinator_meadow: Object.freeze([Object.freeze({ variantId: 'pollinator_meadow_v0', appearanceKitId: 'pollinator_meadow_v0_prairie_skin', plantingStructure: 'pollinator_prairie_v0' })]),
  }),
  park_orchard_heritage_v0: Object.freeze({
    urban_orchard_food_forest: Object.freeze([Object.freeze({ variantId: 'urban_orchard_food_forest_v0', appearanceKitId: 'urban_orchard_food_forest_v0_heritage_apple_skin', plantingStructure: 'orchard_heritage_v0' })]),
  }),
  park_bioswale_streetside_v0: Object.freeze({
    bioswale_rain_garden: Object.freeze([Object.freeze({ variantId: 'bioswale_rain_garden_v0', appearanceKitId: 'bioswale_rain_garden_v0_streetside_skin', plantingStructure: 'bioswale_streetside_v0' })]),
  }),
  park_sculpture_museum_court_v0: Object.freeze({
    sculpture_garden: Object.freeze([Object.freeze({ variantId: 'sculpture_garden_v0', appearanceKitId: 'sculpture_garden_v0_museum_court_skin', plantingStructure: 'sculpture_museum_court_v0' })]),
  }),
  park_labyrinth_classical_v0: Object.freeze({
    labyrinth_meditation: Object.freeze([Object.freeze({ variantId: 'labyrinth_meditation_v0', appearanceKitId: 'labyrinth_meditation_v0_classical_stone_skin', plantingStructure: 'labyrinth_classical_v0' })]),
  }),
  park_ice_rink_multipurpose_v3: Object.freeze({
    outdoor_ice_rink: Object.freeze([Object.freeze({ variantId: 'outdoor_ice_rink_v3', appearanceKitId: 'outdoor_ice_rink_v3_multipurpose_pad_skin', plantingStructure: 'ice_rink_multipurpose_v3' })]),
  }),
  park_kayak_river_launch_v0: Object.freeze({
    kayak_launch_dock: Object.freeze([Object.freeze({ variantId: 'kayak_launch_dock_v0', appearanceKitId: 'kayak_launch_dock_v0_river_launch_skin', plantingStructure: 'kayak_river_launch_v0' })]),
  }),
  park_tidal_marsh_cordgrass_v0: Object.freeze({
    tidal_marsh_boardwalk: Object.freeze([Object.freeze({ variantId: 'tidal_marsh_boardwalk_v0', appearanceKitId: 'tidal_marsh_boardwalk_v0_cordgrass_skin', plantingStructure: 'tidal_marsh_cordgrass_v0' })]),
  }),
  park_cinema_lawn_projection_v1: Object.freeze({
    outdoor_cinema_lawn: Object.freeze([Object.freeze({ variantId: 'outdoor_cinema_lawn_v1', appearanceKitId: 'outdoor_cinema_lawn_v1_park_projection_skin', plantingStructure: 'cinema_lawn_projection_v1' })]),
  }),
  park_food_truck_permanent_v1: Object.freeze({
    food_truck_plaza: Object.freeze([Object.freeze({ variantId: 'food_truck_plaza_v1', appearanceKitId: 'food_truck_plaza_v1_permanent_park_skin', plantingStructure: 'food_truck_permanent_v1' })]),
  }),
  park_great_lawn_v2: Object.freeze({
    festival_event_lawn: Object.freeze([Object.freeze({ variantId: 'festival_event_lawn_v2', appearanceKitId: 'festival_event_lawn_v2_great_lawn_skin', plantingStructure: 'great_lawn_v2' })]),
  }),
  park_campus_meadow_quad_v0: Object.freeze({
    campus_central_quad: Object.freeze([Object.freeze({ variantId: 'campus_central_quad_variant_0', appearanceKitId: 'campus_central_quad_v0_naturalized_meadow_skin', plantingStructure: 'campus_meadow_quad_v0' })]),
  }),
  park_urban_beach_family_v2: Object.freeze({
    urban_beach: Object.freeze([Object.freeze({ variantId: 'urban_beach_v2', appearanceKitId: 'urban_beach_v2_family_splash_skin', plantingStructure: 'urban_beach_family_v2' })]),
  }),
  park_velodrome_open_air_v0: Object.freeze({
    velodrome_cycling_track: Object.freeze([Object.freeze({ variantId: 'velodrome_cycling_track_variant_0', appearanceKitId: 'velodrome_cycling_track_v0_open_air_skin', plantingStructure: 'velodrome_open_air_v0' })]),
  }),
  park_mtb_skills_dirt_v2: Object.freeze({
    mountain_bike_park: Object.freeze([Object.freeze({ variantId: 'mountain_bike_park_variant_2', appearanceKitId: 'mountain_bike_park_v2_skills_dirt_skin', plantingStructure: 'mtb_skills_dirt_v2' })]),
  }),
  park_regional_english_landscape_v0: Object.freeze({
    regional_park: fourVariantMappings(
      'regional_park',
      ['regional_park_v0_english_landscape_skin', 'regional_park_v1_modern_minimalist_skin', 'regional_park_v2_mediterranean_xeriscape_skin', 'regional_park_v3_tropical_lush_skin'],
      ['regional_english_landscape_v0', 'regional_modern_minimalist_v1', 'regional_mediterranean_xeriscape_v2', 'regional_tropical_lush_v3'],
    ),
  }),
  park_beer_garden_munich_v0: Object.freeze({
    beer_garden: Object.freeze([Object.freeze({ variantId: 'beer_garden_v0', appearanceKitId: 'beer_garden_v0_munich_chestnut_skin', plantingStructure: 'beer_garden_munich_v0' })]),
  }),
  park_sunken_courtyard_v0: Object.freeze({
    sunken_plaza: Object.freeze([Object.freeze({ variantId: 'sunken_plaza_v0', appearanceKitId: 'sunken_plaza_v0_intimate_courtyard_skin', plantingStructure: 'sunken_courtyard_v0' })]),
  }),
  park_terraced_cascade_v3: Object.freeze({
    stepped_terraced_plaza: Object.freeze([Object.freeze({ variantId: 'stepped_terraced_plaza_v3', appearanceKitId: 'stepped_terraced_plaza_v3_modernist_cascade_skin', plantingStructure: 'terraced_cascade_v3' })]),
  }),
  park_market_festival_lawn_v1: Object.freeze({
    market_square: Object.freeze([Object.freeze({ variantId: 'market_square_v1', appearanceKitId: 'market_square_v1_open_festival_lawn_skin', plantingStructure: 'market_festival_lawn_v1' })]),
  }),
  park_boardwalk_maritime_v0: Object.freeze({
    promenade_boardwalk: Object.freeze([Object.freeze({ variantId: 'promenade_boardwalk_v0', appearanceKitId: 'promenade_boardwalk_v0_maritime_skin', plantingStructure: 'boardwalk_maritime_v0' })]),
  }),
  park_fountain_formal_pool_v1: Object.freeze({
    fountain_water_feature: Object.freeze([Object.freeze({ variantId: 'fountain_water_feature_v1', appearanceKitId: 'fountain_water_feature_v1_formal_pool_skin', plantingStructure: 'fountain_formal_pool_v1' })]),
  }),
  park_natural_swimming_pond_v0: Object.freeze({
    swimming_pool_complex: Object.freeze([Object.freeze({ variantId: 'swimming_pool_complex_v0', appearanceKitId: 'swimming_pool_complex_v0_natural_pond_skin', plantingStructure: 'natural_swimming_pond_v0' })]),
  }),
  park_nature_preserve_prairie_v1: Object.freeze({
    nature_preserve: Object.freeze([Object.freeze({ variantId: 'nature_preserve_v1', appearanceKitId: 'nature_preserve_v1_tallgrass_prairie_skin', plantingStructure: 'nature_preserve_prairie_v1' })]),
  }),
  park_riverfront_lake_beach_v1: Object.freeze({
    riverfront_park_beach: Object.freeze([Object.freeze({ variantId: 'riverfront_park_beach_v1', appearanceKitId: 'riverfront_park_beach_v1_lake_swimming_skin', plantingStructure: 'riverfront_lake_beach_v1' })]),
  }),
  park_reclaimed_wharf_v0: Object.freeze({
    reclaimed_industrial_park: Object.freeze([Object.freeze({ variantId: 'reclaimed_industrial_park_v0', appearanceKitId: 'reclaimed_industrial_park_v0_wharf_skin', plantingStructure: 'reclaimed_wharf_v0' })]),
  }),
  park_quarry_tier_cascade_v2: Object.freeze({
    quarry_sunken_garden_park: Object.freeze([Object.freeze({ variantId: 'quarry_sunken_garden_park_v2', appearanceKitId: 'quarry_sunken_garden_park_v2_tier_cascade_skin', plantingStructure: 'quarry_tier_cascade_v2' })]),
  }),
  park_estate_oak_picnic_v1: Object.freeze({
    estate_picnic_grove: Object.freeze([Object.freeze({ variantId: 'estate_picnic_grove_v1', appearanceKitId: 'estate_picnic_grove_v1_oak_skin', plantingStructure: 'estate_oak_picnic_v1' })]),
  }),
  park_constructed_wetland_boardwalk_v0: Object.freeze({
    constructed_wetland_eco_park: Object.freeze([Object.freeze({ variantId: 'constructed_wetland_eco_park_variant_0', appearanceKitId: 'constructed_wetland_eco_park_v0_boardwalk_skin', plantingStructure: 'constructed_wetland_boardwalk_v0' })]),
  }),
  park_academic_planted_court_v0: Object.freeze({
    academic_courtyard: Object.freeze([Object.freeze({ variantId: 'academic_courtyard_variant_0', appearanceKitId: 'academic_courtyard_v0_planted_skin', plantingStructure: 'academic_planted_court_v0' })]),
  }),
  park_campus_green_spine_v0: Object.freeze({
    campus_pedestrian_spine: Object.freeze([Object.freeze({ variantId: 'campus_pedestrian_spine_variant_0', appearanceKitId: 'campus_pedestrian_spine_v0_green_skin', plantingStructure: 'campus_green_spine_v0' })]),
  }),
  park_botanical_rose_garden_v3: Object.freeze({
    botanical_garden: Object.freeze([Object.freeze({ variantId: 'botanical_garden_v3', appearanceKitId: 'botanical_garden_v3_rose_skin', plantingStructure: 'botanical_rose_garden_v3' })]),
  }),
  park_research_arboretum_v0: Object.freeze({
    research_garden_teaching_arboretum: Object.freeze([Object.freeze({ variantId: 'research_garden_teaching_arboretum_variant_0', appearanceKitId: 'research_garden_teaching_arboretum_v0_skin', plantingStructure: 'research_arboretum_v0' })]),
  }),
  park_rewilding_reforestation_v1: Object.freeze({
    rewilding_ecological_restoration_zone: Object.freeze([Object.freeze({ variantId: 'rewilding_ecological_restoration_zone_variant_1', appearanceKitId: 'rewilding_ecological_restoration_zone_v1_skin', plantingStructure: 'rewilding_reforestation_v1' })]),
  }),
  park_stormwater_arid_channel_v3: Object.freeze({
    stormwater_resilience_park: Object.freeze([Object.freeze({ variantId: 'stormwater_resilience_park_variant_3', appearanceKitId: 'stormwater_resilience_park_v3_arid_skin', plantingStructure: 'stormwater_arid_channel_v3' })]),
  }),
  park_urban_pocket_rustic_v0: Object.freeze({
    urban_pocket_park: Object.freeze([Object.freeze({ variantId: 'urban_pocket_park_v0', appearanceKitId: 'urban_pocket_park_v0_rustic_skin', plantingStructure: 'urban_pocket_rustic_v0' })]),
  }),
  park_neighborhood_contemporary_v3: Object.freeze({
    neighborhood_park: Object.freeze([Object.freeze({ variantId: 'neighborhood_park_v3', appearanceKitId: 'neighborhood_park_v3_contemporary_skin', plantingStructure: 'neighborhood_contemporary_v3' })]),
  }),
  park_cemetery_classical_v0: Object.freeze({
    cemetery_memorial_grounds: Object.freeze([Object.freeze({ variantId: 'cemetery_memorial_grounds_v0', appearanceKitId: 'cemetery_memorial_grounds_v0_classical_skin', plantingStructure: 'cemetery_classical_v0' })]),
  }),
  park_courtyard_linear_water_v1: Object.freeze({
    courtyard_plaza: Object.freeze([Object.freeze({ variantId: 'courtyard_plaza_v1', appearanceKitId: 'courtyard_plaza_v1_linear_water_skin', plantingStructure: 'courtyard_linear_water_v1' })]),
  }),
  park_parklet_sf_timber_v1: Object.freeze({
    street_plaza_parklet: Object.freeze([Object.freeze({ variantId: 'street_plaza_parklet_v1', appearanceKitId: 'street_plaza_parklet_v1_sf_timber_skin', plantingStructure: 'parklet_sf_timber_v1' })]),
  }),
  park_french_parterre_axis_v1: Object.freeze({
    parisian_jardin: Object.freeze([Object.freeze({ variantId: 'parisian_jardin_v1', appearanceKitId: 'parisian_jardin_v1_water_axis_skin', plantingStructure: 'french_parterre_axis_v1' })]),
  }),
  park_london_railed_square_v1: Object.freeze({
    london_garden_square: Object.freeze([Object.freeze({ variantId: 'london_garden_square_v1', appearanceKitId: 'london_garden_square_v1_railed_skin', plantingStructure: 'london_railed_square_v1' })]),
  }),
  park_halifax_rose_bandstand_v0: Object.freeze({
    halifax_public_gardens: Object.freeze([Object.freeze({ variantId: 'halifax_public_gardens_v0', appearanceKitId: 'halifax_public_gardens_v0_rose_skin', plantingStructure: 'halifax_rose_bandstand_v0' })]),
  }),
  park_olmsted_multilandscape_v3: Object.freeze({
    picturesque_olmsted_park: Object.freeze([Object.freeze({ variantId: 'picturesque_olmsted_park_v3', appearanceKitId: 'picturesque_olmsted_park_v3_multilandscape_skin', plantingStructure: 'olmsted_multilandscape_v3' })]),
  }),
  park_hilltop_viewpoint_v3: Object.freeze({
    hilltop_topographic_park: Object.freeze([Object.freeze({ variantId: 'hilltop_topographic_park_v3', appearanceKitId: 'hilltop_topographic_park_v3_viewpoint_skin', plantingStructure: 'hilltop_viewpoint_v3' })]),
  }),
  park_amsterdam_hofje_garden_v0: Object.freeze({
    amsterdam_hofje_garden: Object.freeze([Object.freeze({ variantId: 'amsterdam_hofje_garden_v0', appearanceKitId: 'amsterdam_hofje_garden_v0_skin', plantingStructure: 'amsterdam_hofje_v0' })]),
  }),
  park_amsterdam_plein_v0: Object.freeze({
    amsterdam_plein: Object.freeze([Object.freeze({ variantId: 'amsterdam_plein_v0', appearanceKitId: 'amsterdam_plein_v0_brick_skin', plantingStructure: 'amsterdam_plein_v0' })]),
  }),
  park_amsterdam_vondelpark_pavilion_v3: Object.freeze({
    amsterdam_vondelpark: Object.freeze([Object.freeze({ variantId: 'amsterdam_vondelpark_v3', appearanceKitId: 'amsterdam_vondelpark_v3_pavilion_skin', plantingStructure: 'amsterdam_vondelpark_v3' })]),
  }),
  park_barcelona_pati_green_v0: Object.freeze({
    barcelona_pati_interior: Object.freeze([Object.freeze({ variantId: 'barcelona_pati_interior_v0', appearanceKitId: 'barcelona_pati_interior_v0_green_skin', plantingStructure: 'barcelona_pati_green_v0' })]),
  }),
  park_barcelona_xamfra_corner_v2: Object.freeze({
    barcelona_placa_xamfra: Object.freeze([Object.freeze({ variantId: 'barcelona_placa_xamfra_v2', appearanceKitId: 'barcelona_placa_xamfra_v2_corner_skin', plantingStructure: 'barcelona_xamfra_v2' })]),
  }),
  park_barcelona_superilla_green_v1: Object.freeze({
    barcelona_superilla: Object.freeze([Object.freeze({ variantId: 'barcelona_superilla_v1', appearanceKitId: 'barcelona_superilla_v1_green_skin', plantingStructure: 'barcelona_superilla_v1' })]),
  }),
  park_calgary_prairie_market_v1: Object.freeze({
    calgary_prairie_plaza: Object.freeze([Object.freeze({ variantId: 'calgary_prairie_plaza_v1', appearanceKitId: 'calgary_prairie_plaza_v1_market_skin', plantingStructure: 'calgary_prairie_market_v1' })]),
  }),
  park_calgary_princes_island_festival_v0: Object.freeze({
    calgary_princes_island: Object.freeze([Object.freeze({ variantId: 'calgary_princes_island_v0', appearanceKitId: 'calgary_princes_island_v0_festival_skin', plantingStructure: 'calgary_princes_island_v0' })]),
  }),
  park_montreal_mount_royal_grove_v2: Object.freeze({
    montreal_mount_royal: Object.freeze([Object.freeze({ variantId: 'montreal_mount_royal_v2', appearanceKitId: 'montreal_mount_royal_v2_grove_skin', plantingStructure: 'montreal_mount_royal_v2' })]),
  }),
  park_montreal_neighbourhood_square_v3: Object.freeze({
    montreal_square: Object.freeze([Object.freeze({ variantId: 'montreal_square_v3', appearanceKitId: 'montreal_square_v3_neighbourhood_skin', plantingStructure: 'montreal_square_v3' })]),
  }),
  park_paris_place_royale_v2: Object.freeze({
    parisian_place: Object.freeze([Object.freeze({ variantId: 'parisian_place_v2', appearanceKitId: 'parisian_place_v2_royale_skin', plantingStructure: 'paris_place_royale_v2' })]),
  }),
  park_paris_square_tree_grid_v3: Object.freeze({
    parisian_square: Object.freeze([Object.freeze({ variantId: 'parisian_square_v3', appearanceKitId: 'parisian_square_v3_tree_grid_skin', plantingStructure: 'paris_square_tree_grid_v3' })]),
  }),
  park_london_circus_planted_v1: Object.freeze({
    london_circus: Object.freeze([Object.freeze({ variantId: 'london_circus_v1', appearanceKitId: 'london_circus_v1_planted_skin', plantingStructure: 'london_circus_planted_v1' })]),
  }),
  park_newyork_pocket_water_v0: Object.freeze({
    newyork_pocket_park: Object.freeze([Object.freeze({ variantId: 'newyork_pocket_park_v0', appearanceKitId: 'newyork_pocket_park_v0_water_skin', plantingStructure: 'newyork_pocket_water_v0' })]),
  }),
  park_newyork_community_greenhouse_v3: Object.freeze({
    newyork_community_garden: Object.freeze([Object.freeze({ variantId: 'newyork_community_garden_v3', appearanceKitId: 'newyork_community_garden_v3_greenhouse_skin', plantingStructure: 'newyork_community_greenhouse_v3' })]),
  }),
  park_vancouver_seawall_cycle_v2: Object.freeze({
    vancouver_seawall: Object.freeze([Object.freeze({ variantId: 'vancouver_seawall_v2', appearanceKitId: 'vancouver_seawall_v2_cycle_skin', plantingStructure: 'vancouver_seawall_cycle_v2' })]),
  }),
  park_vancouver_beach_pavilion_v0: Object.freeze({
    vancouver_beach_park: Object.freeze([Object.freeze({ variantId: 'vancouver_beach_park_v0', appearanceKitId: 'vancouver_beach_park_v0_pavilion_skin', plantingStructure: 'vancouver_beach_pavilion_v0' })]),
  }),
  park_toronto_ravine_creek_v1: Object.freeze({
    toronto_ravine: Object.freeze([Object.freeze({ variantId: 'toronto_ravine_v1', appearanceKitId: 'toronto_ravine_v1_creek_skin', plantingStructure: 'toronto_ravine_creek_v1' })]),
  }),
  park_toronto_urban_market_v1: Object.freeze({
    toronto_urban_square: Object.freeze([Object.freeze({ variantId: 'toronto_urban_square_v1', appearanceKitId: 'toronto_urban_square_v1_market_skin', plantingStructure: 'toronto_urban_market_v1' })]),
  }),
  park_halifax_coastal_fog_path_v2: Object.freeze({
    halifax_coastal_park: Object.freeze([Object.freeze({ variantId: 'halifax_coastal_park_v2', appearanceKitId: 'halifax_coastal_park_v2_fog_path_skin', plantingStructure: 'halifax_coastal_fog_path_v2' })]),
  }),
  park_city_hall_modernist_fountain_v2: Object.freeze({ city_hall_government_plaza: Object.freeze([Object.freeze({ variantId:'city_hall_government_plaza_v2', appearanceKitId:'city_hall_government_plaza_v2_modernist_skin', plantingStructure:'city_hall_modernist_fountain_v2' })]) }),
  park_cathedral_courtyard_fountain_v3: Object.freeze({ cathedral_religious_forecourt: Object.freeze([Object.freeze({ variantId:'cathedral_religious_forecourt_v3', appearanceKitId:'cathedral_religious_forecourt_v3_courtyard_skin', plantingStructure:'cathedral_courtyard_fountain_v3' })]) }),
  park_cultural_museum_terrace_v0: Object.freeze({ cultural_institution_forecourt: Object.freeze([Object.freeze({ variantId:'cultural_institution_forecourt_v0', appearanceKitId:'cultural_institution_forecourt_v0_museum_terrace_skin', plantingStructure:'cultural_museum_terrace_v0' })]) }),
  park_transit_green_civic_v2: Object.freeze({ transit_plaza: Object.freeze([Object.freeze({ variantId:'transit_plaza_v2', appearanceKitId:'transit_plaza_v2_green_civic_skin', plantingStructure:'transit_green_civic_v2' })]) }),
  park_amphitheater_terraced_v0: Object.freeze({ amphitheater_performance_space: Object.freeze([Object.freeze({ variantId:'amphitheater_performance_space_v0', appearanceKitId:'amphitheater_performance_space_v0_terraced_skin', plantingStructure:'amphitheater_terraced_v0' })]) }),
  park_concert_timber_lawn_v2: Object.freeze({ concert_pavilion_lawn: Object.freeze([Object.freeze({ variantId:'concert_pavilion_lawn_v2', appearanceKitId:'concert_pavilion_lawn_v2_timber_skin', plantingStructure:'concert_timber_lawn_v2' })]) }),
  park_night_market_hawker_v0: Object.freeze({ night_market: Object.freeze([Object.freeze({ variantId:'night_market_v0', appearanceKitId:'night_market_v0_hawker_skin', plantingStructure:'night_market_hawker_v0' })]) }),
  park_parade_national_mall_v3: Object.freeze({ parade_ground: Object.freeze([Object.freeze({ variantId:'parade_ground_v3', appearanceKitId:'parade_ground_v3_national_mall_skin', plantingStructure:'parade_national_mall_v3' })]) }),
  park_canal_ecological_wetland_v3: Object.freeze({ canal_waterway: Object.freeze([Object.freeze({ variantId:'canal_waterway_v3', appearanceKitId:'canal_waterway_v3_ecological_skin', plantingStructure:'canal_ecological_wetland_v3' })]) }),
  park_custom_biophilic_urban_v1: Object.freeze({ custom_parks_plazas: Object.freeze([Object.freeze({ variantId:'custom_parks_plazas_v1', appearanceKitId:'custom_parks_plazas_v1_biophilic_skin', plantingStructure:'custom_biophilic_urban_v1' })]) }),
  park_rooftop_intensive_garden_v0: Object.freeze({ rooftop_garden: Object.freeze([Object.freeze({variantId:'rooftop_garden_v0',appearanceKitId:'rooftop_garden_v0_intensive_skin',plantingStructure:'rooftop_intensive_garden_v0'})]) }),
  park_community_healing_garden_v2: Object.freeze({ community_garden_enhanced: Object.freeze([Object.freeze({variantId:'garden_healing',appearanceKitId:'community_garden_enhanced_healing_skin',plantingStructure:'community_healing_garden_v2'})]) }),
  park_greenbelt_rail_trail_v1: Object.freeze({ greenbelt_buffer_park: Object.freeze([Object.freeze({variantId:'greenbelt_buffer_park_v1',appearanceKitId:'greenbelt_buffer_park_v1_rail_trail_skin',plantingStructure:'greenbelt_rail_trail_v1'})]) }),
  park_foothill_heathland_trail_v2: Object.freeze({ foothill_trail_park: Object.freeze([Object.freeze({variantId:'foothill_trail_park_v2',appearanceKitId:'foothill_trail_park_v2_heathland_skin',plantingStructure:'foothill_heathland_trail_v2'})]) }),
  park_marina_pacific_dock_v2: Object.freeze({ marina_yacht_harbor: Object.freeze([Object.freeze({variantId:'marina_yacht_harbor_v2',appearanceKitId:'marina_yacht_harbor_v2_pacific_skin',plantingStructure:'marina_pacific_dock_v2'})]) }),
  park_working_pier_brooklyn_park_v3: Object.freeze({ working_pier_wharf_conversion: Object.freeze([Object.freeze({variantId:'working_pier_wharf_conversion_v3',appearanceKitId:'working_pier_wharf_conversion_v3_park_skin',plantingStructure:'working_pier_brooklyn_park_v3'})]) }),
  park_floating_meadow_loop_v2: Object.freeze({ floating_park_pool: Object.freeze([Object.freeze({variantId:'floating_park_pool_v2',appearanceKitId:'floating_park_pool_v2_meadow_skin',plantingStructure:'floating_meadow_loop_v2'})]) }),
  park_lighthouse_pacific_headland_v2: Object.freeze({ lighthouse_point_park: Object.freeze([Object.freeze({variantId:'lighthouse_point_park_v2',appearanceKitId:'lighthouse_point_park_v2_pacific_skin',plantingStructure:'lighthouse_pacific_headland_v2'})]) }),
  park_lake_edge_timber_deck_v2: Object.freeze({ lake_edge_plaza: Object.freeze([Object.freeze({variantId:'lake_edge_plaza_v2',appearanceKitId:'lake_edge_plaza_v2_timber_skin',plantingStructure:'lake_edge_timber_deck_v2'})]) }),
  park_stormwater_natural_creek_v0: Object.freeze({ stormwater_naturalized_drainage_corridor: Object.freeze([Object.freeze({variantId:'stormwater_naturalized_drainage_corridor_variant_0',appearanceKitId:'stormwater_naturalized_drainage_corridor_v0_creek_skin',plantingStructure:'stormwater_natural_creek_v0'})]) }),
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
