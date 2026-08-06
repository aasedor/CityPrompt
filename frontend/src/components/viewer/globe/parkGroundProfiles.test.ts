import { describe, expect, it } from 'vitest';
import type { SiteZone } from '@/types';
import openSpaceCatalog from '@/data/openSpaceArchetypes.json';
import {
  JAPANESE_GARDEN_BRIDGE_DIMENSIONS_M,
  PILOT_PARK_ARCHETYPE_IDS,
  buildParkRenderQualityInstruction,
  describeParkGroundGuideFit,
  fitParkGroundGuides,
  isParkGuideRenderedByLegoAssembly,
  parkGroundSourceSignature,
  resolveParkGuideDimensionsM,
  resolveParkGroundProfile,
  resolveParkPlacementGuides,
  resolveParkPlantingStructure,
  resolveParkSpecialtyStructureKind,
  shouldMountParkProgramFrame,
} from './parkGroundProfiles';
import {
  buildParkGroundPrompt,
  hasCurrentParkGroundSurface,
  isParkGroundZone,
  MAX_PARK_RENDER_GEOMETRY_REFERENCES,
  MAX_PARK_GROUND_BATCH_CALLS,
  replaceEdgeConnectedPaperWithTurf,
  resolveParkGroundSurfaceSource,
  selectLatestParkRenderReference,
  selectParkRenderGeometryZones,
  shouldDeferParkFinishingProp,
  shouldRenderLiveParkProp,
  takeParkGroundBatch,
} from './parkGroundTexture';

function zone(archetypeId: string): SiteZone {
  return {
    id: `zone-${archetypeId}`,
    project_id: 'project-1',
    zone_type: 'green_space',
    name: archetypeId,
    coordinates: [
      [-114.071, 51.041],
      [-114.069, 51.041],
      [-114.069, 51.042],
      [-114.071, 51.042],
    ],
    color: '#65a30d',
    properties: { green_space_archetype_id: archetypeId },
    sort_order: 0,
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
  };
}

function trustedParkRecipe(selection: Record<string, unknown>): Record<string, unknown> {
  return {
    schema_version: 1,
    kind: 'park',
    generator: 'park_kit',
    catalog_fingerprint: 'a'.repeat(64),
    capability_fingerprint: 'b'.repeat(64),
    recipe_hash: 'c'.repeat(64),
    ...selection,
  };
}

describe('park ground pilot profiles', () => {
  it('gives each regulation LEGO assembly sole ownership of its playable surface', () => {
    expect(isParkGuideRenderedByLegoAssembly(
      'park_basketball_court_v0',
      'basketball_court',
    )).toBe(true);
    expect(isParkGuideRenderedByLegoAssembly(
      'park_tennis_cluster_v0',
      'tennis_court',
    )).toBe(true);
    expect(isParkGuideRenderedByLegoAssembly(
      'park_caged_soccer_v0',
      'soccer_field',
    )).toBe(true);
    expect(isParkGuideRenderedByLegoAssembly(
      'park_athletics_fields_v0',
      'soccer_field',
    )).toBe(true);
    expect(isParkGuideRenderedByLegoAssembly(
      'park_ice_rink_multipurpose_v3',
      'rounded_rectangle',
    )).toBe(true);
    expect(isParkGuideRenderedByLegoAssembly(
      'park_velodrome_open_air_v0',
      'track',
    )).toBe(true);
    expect(isParkGuideRenderedByLegoAssembly(
      'park_mtb_skills_dirt_v2',
      'track',
    )).toBe(true);
    expect(isParkGuideRenderedByLegoAssembly(
      'park_basketball_court_v0',
      'path_loop',
    )).toBe(false);
    expect(isParkGuideRenderedByLegoAssembly(
      'park_neighborhood_community',
      'basketball_court',
    )).toBe(false);
  });

  it.each([
    ['neighborhood_park', 'active_recreation'],
    ['urban_pocket_park', 'garden_courtyard'],
    ['linear_park_greenway', 'naturalistic_grove'],
    ['formal_civic_plaza', 'paved_plaza'],
    ['fountain_water_feature', 'paved_plaza'],
    ['stormwater_retention_pond', 'reservoir_perimeter'],
    ['pond_lake', 'pond_lake_v0'],
    ['tennis_court_cluster', 'sports_perimeter'],
    ['soccer_pitch_caged', 'caged_soccer_v0'],
    ['athletics_precinct_sports_fields', 'athletics_fields_v0'],
    ['wetland_rain_garden', 'water_ecology'],
    ['japanese_garden', 'japanese_stroll_garden'],
    ['sports_field_complex', 'sports_perimeter'],
    ['urban_forest', 'naturalistic_grove'],
    ['botanical_garden', 'botanical_collection'],
    ['nature_play_area', 'nature_play_grove'],
    ['reservoir_watershed_park', 'reservoir_perimeter'],
    ['amphitheater_lawn', 'amphitheater_lawn_v0'],
    ['riparian_buffer', 'riparian_buffer_v0'],
    ['playground_adventure', 'playground_adventure_v0'],
    ['disc_golf_course', 'disc_golf_wooded_v0'],
    ['bocce_petanque_court', 'bocce_piazza_v0'],
    ['climbing_bouldering_wall', 'climbing_competition_v0'],
    ['mini_golf_course', 'mini_golf_classic_v0'],
    ['beach_volleyball_courts', 'beach_volleyball_competition_v0'],
    ['pollinator_meadow', 'pollinator_prairie_v0'],
    ['urban_orchard_food_forest', 'orchard_heritage_v0'],
    ['bioswale_rain_garden', 'bioswale_streetside_v0'],
    ['sculpture_garden', 'sculpture_museum_court_v0'],
    ['labyrinth_meditation', 'labyrinth_classical_v0'],
    ['outdoor_ice_rink', 'ice_rink_multipurpose_v3'],
    ['kayak_launch_dock', 'kayak_river_launch_v0'],
    ['tidal_marsh_boardwalk', 'tidal_marsh_cordgrass_v0'],
    ['outdoor_cinema_lawn', 'cinema_lawn_projection_v1'],
    ['food_truck_plaza', 'food_truck_permanent_v1'],
    ['festival_event_lawn', 'great_lawn_v2'],
    ['campus_central_quad', 'campus_meadow_quad_v0'],
    ['urban_beach', 'urban_beach_family_v2'],
    ['velodrome_cycling_track', 'velodrome_open_air_v0'],
    ['mountain_bike_park', 'mtb_skills_dirt_v2'],
  ])('resolves %s with its coordinated planting structure', (id, planting) => {
    const candidate = zone(id);
    expect(resolveParkGroundProfile(candidate).isPilot).toBe(true);
    expect(resolveParkPlantingStructure(candidate)).toBe(planting);
  });

  it('gives specialty pilots authoritative program guides', () => {
    expect(resolveParkGroundProfile(zone('neighborhood_park')).guides).toHaveLength(9);
    expect(resolveParkGroundProfile(zone('japanese_garden')).guides).toHaveLength(4);
    expect(resolveParkGroundProfile(zone('sports_field_complex')).guides).toHaveLength(4);
    expect(resolveParkGroundProfile(zone('urban_forest')).guides).toHaveLength(3);
    expect(resolveParkGroundProfile(zone('botanical_garden')).guides).toHaveLength(5);
    expect(resolveParkGroundProfile(zone('nature_play_area')).guides).toHaveLength(5);
    expect(resolveParkGroundProfile(zone('tennis_court_cluster')).guides).toHaveLength(5);
    expect(resolveParkGroundProfile(zone('soccer_pitch_caged')).guides).toHaveLength(2);
    expect(resolveParkGroundProfile(zone('athletics_precinct_sports_fields')).guides).toHaveLength(2);
    expect(resolveParkGroundProfile(zone('wetland_rain_garden')).guides).toHaveLength(6);
    expect(resolveParkGroundProfile(zone('pond_lake_variant_0')).guides[0].kind)
      .toBe('ellipse');
    expect(resolveParkGroundProfile(zone('japanese_garden')).includeCentralPlaza).toBe(false);
    expect(resolveParkGroundProfile(zone('sports_field_complex')).includeCentralPlaza).toBe(false);
    expect(resolveParkGroundProfile(zone('neighborhood_park')).includeCentralPlaza).toBe(false);
  });

  it('keeps fixed specialty structures independent from render-only planting', () => {
    expect(resolveParkSpecialtyStructureKind(zone('japanese_garden')))
      .toBe('japanese_garden_bridge');
    expect(resolveParkSpecialtyStructureKind(zone('japanese_garden_variant_2')))
      .toBe('japanese_garden_bridge');
    expect(resolveParkSpecialtyStructureKind(zone('cricket_pitch_oval')))
      .toBe('cricket_ground_assembly');
    expect(resolveParkSpecialtyStructureKind(zone('sports_field_complex')))
      .toBe('sports_field_furniture');
    expect(resolveParkSpecialtyStructureKind(zone('athletics_precinct_sports_fields')))
      .toBe('sports_field_furniture');
    expect(resolveParkSpecialtyStructureKind(zone('soccer_pitch_caged')))
      .toBe('caged_soccer_v0_assembly');
    expect(resolveParkSpecialtyStructureKind(zone('tennis_court_cluster')))
      .toBe('tennis_court_furniture');
    expect(resolveParkSpecialtyStructureKind(zone('wetland_rain_garden')))
      .toBe('wetland_boardwalk');
    expect(resolveParkSpecialtyStructureKind(zone('botanical_garden')))
      .toBe('botanical_conservatory');
    expect(resolveParkSpecialtyStructureKind(zone('neighborhood_park'))).toBeNull();
    expect(shouldMountParkProgramFrame(zone('japanese_garden'), 0)).toBe(true);
    expect(shouldMountParkProgramFrame(zone('sports_field_complex'), 0)).toBe(true);
    expect(shouldMountParkProgramFrame(zone('cricket_pitch_oval'), 0)).toBe(true);
    expect(shouldMountParkProgramFrame(zone('wetland_rain_garden'), 0)).toBe(true);
    expect(shouldMountParkProgramFrame(zone('botanical_garden'), 0)).toBe(true);
    expect(shouldMountParkProgramFrame(zone('neighborhood_park'), 0)).toBe(false);
    expect(shouldMountParkProgramFrame(zone('neighborhood_park'), 1)).toBe(true);
  });

  it.each([
    ['park_water_ecology', 'pond_lake', 'pond_lake_v0', 'pond_lake_v0_naturalistic_skin', 'pond_lake_v0', 'pond_dock_assembly'],
    ['park_water_ecology', 'wetland_rain_garden', 'wetland_rain_garden_v0', 'wetland_rain_garden_v0_native_restoration_skin', 'wetland_rain_garden_v0', 'wetland_boardwalk'],
    ['park_water_ecology', 'riparian_buffer', 'riparian_buffer_v0', 'riparian_buffer_v0_native_restoration_skin', 'riparian_buffer_v0', 'riparian_bridge_assembly'],
    ['park_water_ecology', 'reservoir_watershed_park', 'reservoir_watershed_park_v0', 'reservoir_watershed_park_v0_concrete_edge_skin', 'reservoir_watershed_park_v0', 'reservoir_edge_assembly'],
    ['park_amphitheater_lawn_v0', 'amphitheater_lawn', 'amphitheater_lawn_v0', 'amphitheater_lawn_v0_terraced_performance_skin', 'amphitheater_lawn_v0', 'amphitheater_lawn_assembly'],
    ['park_playground_adventure_v0', 'playground_adventure', 'playground_adventure_v0', 'playground_adventure_v0_rustic_timber_skin', 'playground_adventure_v0', 'adventure_play_assembly'],
  ] as const)('resolves the batch-4 depth kit for %s/%s', (
    familyId, archetypeId, variantId, appearanceKitId, plantingStructure, expected,
  ) => {
    const candidate = zone(archetypeId);
    candidate.properties = {
      ...candidate.properties,
      public_realm_lego: trustedParkRecipe({
        family_id: familyId,
        family_version: 1,
        archetype_id: archetypeId,
        variant_id: variantId,
        appearance_kit_id: appearanceKitId,
        planting_structure: plantingStructure,
      }),
    };
    expect(resolveParkSpecialtyStructureKind(candidate)).toBe(expected);
  });

  it.each([
    ['park_disc_golf_wooded_v0', 'disc_golf_course', 'disc_golf_course_v0_wooded_championship_skin', 'disc_golf_wooded_v0'],
    ['park_bocce_piazza_v0', 'bocce_petanque_court', 'bocce_petanque_court_v0_italian_piazza_skin', 'bocce_piazza_v0'],
    ['park_climbing_competition_v0', 'climbing_bouldering_wall', 'climbing_bouldering_wall_v0_competition_skin', 'climbing_competition_v0'],
    ['park_mini_golf_classic_v0', 'mini_golf_course', 'mini_golf_course_v0_classic_skin', 'mini_golf_classic_v0'],
    ['park_beach_volleyball_competition_v0', 'beach_volleyball_courts', 'beach_volleyball_courts_v0_competition_skin', 'beach_volleyball_competition_v0'],
    ['park_pollinator_prairie_v0', 'pollinator_meadow', 'pollinator_meadow_v0_prairie_skin', 'pollinator_prairie_v0'],
    ['park_orchard_heritage_v0', 'urban_orchard_food_forest', 'urban_orchard_food_forest_v0_heritage_apple_skin', 'orchard_heritage_v0'],
    ['park_bioswale_streetside_v0', 'bioswale_rain_garden', 'bioswale_rain_garden_v0_streetside_skin', 'bioswale_streetside_v0'],
    ['park_sculpture_museum_court_v0', 'sculpture_garden', 'sculpture_garden_v0_museum_court_skin', 'sculpture_museum_court_v0'],
    ['park_labyrinth_classical_v0', 'labyrinth_meditation', 'labyrinth_meditation_v0_classical_stone_skin', 'labyrinth_classical_v0'],
  ] as const)('resolves the batch-5 depth kit for %s/%s', (
    familyId, archetypeId, appearanceKitId, plantingStructure,
  ) => {
    const candidate = zone(archetypeId);
    candidate.properties = {
      ...candidate.properties,
      public_realm_lego: trustedParkRecipe({
        family_id: familyId,
        family_version: 1,
        archetype_id: archetypeId,
        variant_id: `${archetypeId}_v0`,
        appearance_kit_id: appearanceKitId,
        planting_structure: plantingStructure,
      }),
    };
    expect(resolveParkSpecialtyStructureKind(candidate)).toBe('batch5_archetype_assembly');
    expect(resolveParkGroundProfile(candidate).guides.length).toBeGreaterThan(1);
  });

  it.each([
    ['park_ice_rink_multipurpose_v3', 'outdoor_ice_rink', 'outdoor_ice_rink_v3', 'outdoor_ice_rink_v3_multipurpose_pad_skin', 'ice_rink_multipurpose_v3'],
    ['park_kayak_river_launch_v0', 'kayak_launch_dock', 'kayak_launch_dock_v0', 'kayak_launch_dock_v0_river_launch_skin', 'kayak_river_launch_v0'],
    ['park_tidal_marsh_cordgrass_v0', 'tidal_marsh_boardwalk', 'tidal_marsh_boardwalk_v0', 'tidal_marsh_boardwalk_v0_cordgrass_skin', 'tidal_marsh_cordgrass_v0'],
    ['park_cinema_lawn_projection_v1', 'outdoor_cinema_lawn', 'outdoor_cinema_lawn_v1', 'outdoor_cinema_lawn_v1_park_projection_skin', 'cinema_lawn_projection_v1'],
    ['park_food_truck_permanent_v1', 'food_truck_plaza', 'food_truck_plaza_v1', 'food_truck_plaza_v1_permanent_park_skin', 'food_truck_permanent_v1'],
    ['park_great_lawn_v2', 'festival_event_lawn', 'festival_event_lawn_v2', 'festival_event_lawn_v2_great_lawn_skin', 'great_lawn_v2'],
    ['park_campus_meadow_quad_v0', 'campus_central_quad', 'campus_central_quad_variant_0', 'campus_central_quad_v0_naturalized_meadow_skin', 'campus_meadow_quad_v0'],
    ['park_urban_beach_family_v2', 'urban_beach', 'urban_beach_v2', 'urban_beach_v2_family_splash_skin', 'urban_beach_family_v2'],
    ['park_velodrome_open_air_v0', 'velodrome_cycling_track', 'velodrome_cycling_track_variant_0', 'velodrome_cycling_track_v0_open_air_skin', 'velodrome_open_air_v0'],
    ['park_mtb_skills_dirt_v2', 'mountain_bike_park', 'mountain_bike_park_variant_2', 'mountain_bike_park_v2_skills_dirt_skin', 'mtb_skills_dirt_v2'],
  ] as const)('resolves the batch-6 depth kit for %s/%s', (
    familyId, archetypeId, variantId, appearanceKitId, plantingStructure,
  ) => {
    const candidate = zone(archetypeId);
    candidate.properties = {
      ...candidate.properties,
      public_realm_lego: trustedParkRecipe({
        family_id: familyId,
        family_version: 1,
        archetype_id: archetypeId,
        variant_id: variantId,
        appearance_kit_id: appearanceKitId,
        planting_structure: plantingStructure,
      }),
    };
    expect(resolveParkSpecialtyStructureKind(candidate)).toBe('batch6_archetype_assembly');
    expect(resolveParkGroundProfile(candidate).guides.length).toBeGreaterThan(1);
  });

  it.each([
    ['park_regional_english_landscape_v0', 'regional_park', 'regional_park_v0', 'regional_park_v0_english_landscape_skin', 'regional_english_landscape_v0'],
    ['park_beer_garden_munich_v0', 'beer_garden', 'beer_garden_v0', 'beer_garden_v0_munich_chestnut_skin', 'beer_garden_munich_v0'],
    ['park_sunken_courtyard_v0', 'sunken_plaza', 'sunken_plaza_v0', 'sunken_plaza_v0_intimate_courtyard_skin', 'sunken_courtyard_v0'],
    ['park_terraced_cascade_v3', 'stepped_terraced_plaza', 'stepped_terraced_plaza_v3', 'stepped_terraced_plaza_v3_modernist_cascade_skin', 'terraced_cascade_v3'],
    ['park_market_festival_lawn_v1', 'market_square', 'market_square_v1', 'market_square_v1_open_festival_lawn_skin', 'market_festival_lawn_v1'],
    ['park_boardwalk_maritime_v0', 'promenade_boardwalk', 'promenade_boardwalk_v0', 'promenade_boardwalk_v0_maritime_skin', 'boardwalk_maritime_v0'],
    ['park_fountain_formal_pool_v1', 'fountain_water_feature', 'fountain_water_feature_v1', 'fountain_water_feature_v1_formal_pool_skin', 'fountain_formal_pool_v1'],
    ['park_natural_swimming_pond_v0', 'swimming_pool_complex', 'swimming_pool_complex_v0', 'swimming_pool_complex_v0_natural_pond_skin', 'natural_swimming_pond_v0'],
    ['park_nature_preserve_prairie_v1', 'nature_preserve', 'nature_preserve_v1', 'nature_preserve_v1_tallgrass_prairie_skin', 'nature_preserve_prairie_v1'],
    ['park_riverfront_lake_beach_v1', 'riverfront_park_beach', 'riverfront_park_beach_v1', 'riverfront_park_beach_v1_lake_swimming_skin', 'riverfront_lake_beach_v1'],
  ] as const)('resolves the batch-7 depth kit for %s/%s', (
    familyId, archetypeId, variantId, appearanceKitId, plantingStructure,
  ) => {
    const candidate = zone(archetypeId);
    candidate.properties = {
      ...candidate.properties,
      public_realm_lego: trustedParkRecipe({
        family_id: familyId,
        family_version: 1,
        archetype_id: archetypeId,
        variant_id: variantId,
        appearance_kit_id: appearanceKitId,
        planting_structure: plantingStructure,
      }),
    };
    expect(resolveParkSpecialtyStructureKind(candidate)).toBe('batch7_archetype_assembly');
    expect(resolveParkGroundProfile(candidate).guides.length).toBeGreaterThan(1);
  });

  it.each([
    ['park_reclaimed_wharf_v0', 'reclaimed_industrial_park', 'reclaimed_industrial_park_v0', 'reclaimed_industrial_park_v0_wharf_skin', 'reclaimed_wharf_v0'],
    ['park_quarry_tier_cascade_v2', 'quarry_sunken_garden_park', 'quarry_sunken_garden_park_v2', 'quarry_sunken_garden_park_v2_tier_cascade_skin', 'quarry_tier_cascade_v2'],
    ['park_estate_oak_picnic_v1', 'estate_picnic_grove', 'estate_picnic_grove_v1', 'estate_picnic_grove_v1_oak_skin', 'estate_oak_picnic_v1'],
    ['park_constructed_wetland_boardwalk_v0', 'constructed_wetland_eco_park', 'constructed_wetland_eco_park_variant_0', 'constructed_wetland_eco_park_v0_boardwalk_skin', 'constructed_wetland_boardwalk_v0'],
    ['park_academic_planted_court_v0', 'academic_courtyard', 'academic_courtyard_variant_0', 'academic_courtyard_v0_planted_skin', 'academic_planted_court_v0'],
    ['park_campus_green_spine_v0', 'campus_pedestrian_spine', 'campus_pedestrian_spine_variant_0', 'campus_pedestrian_spine_v0_green_skin', 'campus_green_spine_v0'],
    ['park_botanical_rose_garden_v3', 'botanical_garden', 'botanical_garden_v3', 'botanical_garden_v3_rose_skin', 'botanical_rose_garden_v3'],
    ['park_research_arboretum_v0', 'research_garden_teaching_arboretum', 'research_garden_teaching_arboretum_variant_0', 'research_garden_teaching_arboretum_v0_skin', 'research_arboretum_v0'],
    ['park_rewilding_reforestation_v1', 'rewilding_ecological_restoration_zone', 'rewilding_ecological_restoration_zone_variant_1', 'rewilding_ecological_restoration_zone_v1_skin', 'rewilding_reforestation_v1'],
    ['park_stormwater_arid_channel_v3', 'stormwater_resilience_park', 'stormwater_resilience_park_variant_3', 'stormwater_resilience_park_v3_arid_skin', 'stormwater_arid_channel_v3'],
  ] as const)('resolves the batch-8 exact depth kit for %s/%s', (
    familyId, archetypeId, variantId, appearanceKitId, plantingStructure,
  ) => {
    const candidate = zone(archetypeId);
    candidate.properties = {
      ...candidate.properties,
      public_realm_lego: trustedParkRecipe({
        family_id: familyId,
        family_version: 1,
        archetype_id: archetypeId,
        variant_id: variantId,
        appearance_kit_id: appearanceKitId,
        planting_structure: plantingStructure,
      }),
    };
    expect(resolveParkSpecialtyStructureKind(candidate)).toBe('batch8_archetype_assembly');
    const profile = resolveParkGroundProfile(candidate);
    expect(profile.id).toContain('lego-v1');
    expect(profile.guides.length).toBeGreaterThan(0);
  });

  it.each([
    ['park_urban_pocket_rustic_v0', 'urban_pocket_park', 'urban_pocket_park_v0', 'urban_pocket_park_v0_rustic_skin', 'urban_pocket_rustic_v0'],
    ['park_neighborhood_contemporary_v3', 'neighborhood_park', 'neighborhood_park_v3', 'neighborhood_park_v3_contemporary_skin', 'neighborhood_contemporary_v3'],
    ['park_cemetery_classical_v0', 'cemetery_memorial_grounds', 'cemetery_memorial_grounds_v0', 'cemetery_memorial_grounds_v0_classical_skin', 'cemetery_classical_v0'],
    ['park_courtyard_linear_water_v1', 'courtyard_plaza', 'courtyard_plaza_v1', 'courtyard_plaza_v1_linear_water_skin', 'courtyard_linear_water_v1'],
    ['park_parklet_sf_timber_v1', 'street_plaza_parklet', 'street_plaza_parklet_v1', 'street_plaza_parklet_v1_sf_timber_skin', 'parklet_sf_timber_v1'],
    ['park_french_parterre_axis_v1', 'parisian_jardin', 'parisian_jardin_v1', 'parisian_jardin_v1_water_axis_skin', 'french_parterre_axis_v1'],
    ['park_london_railed_square_v1', 'london_garden_square', 'london_garden_square_v1', 'london_garden_square_v1_railed_skin', 'london_railed_square_v1'],
    ['park_halifax_rose_bandstand_v0', 'halifax_public_gardens', 'halifax_public_gardens_v0', 'halifax_public_gardens_v0_rose_skin', 'halifax_rose_bandstand_v0'],
    ['park_olmsted_multilandscape_v3', 'picturesque_olmsted_park', 'picturesque_olmsted_park_v3', 'picturesque_olmsted_park_v3_multilandscape_skin', 'olmsted_multilandscape_v3'],
    ['park_hilltop_viewpoint_v3', 'hilltop_topographic_park', 'hilltop_topographic_park_v3', 'hilltop_topographic_park_v3_viewpoint_skin', 'hilltop_viewpoint_v3'],
  ] as const)('resolves the batch-9 exact depth kit for %s/%s', (
    familyId, archetypeId, variantId, appearanceKitId, plantingStructure,
  ) => {
    const candidate = zone(archetypeId);
    candidate.properties = {
      ...candidate.properties,
      public_realm_lego: trustedParkRecipe({
        family_id: familyId,
        family_version: 1,
        archetype_id: archetypeId,
        variant_id: variantId,
        appearance_kit_id: appearanceKitId,
        planting_structure: plantingStructure,
      }),
    };
    expect(resolveParkSpecialtyStructureKind(candidate)).toBe('batch9_archetype_assembly');
    const profile = resolveParkGroundProfile(candidate);
    expect(profile.id).toContain('lego-v1');
    expect(profile.guides.length).toBeGreaterThan(0);
  });

  it.each([
    ['outdoor_ice_rink', 'outdoor_ice_rink_v3', 64, 38],
    ['kayak_launch_dock', 'kayak_launch_dock_v0', 80, 35],
    ['tidal_marsh_boardwalk', 'tidal_marsh_boardwalk_v0', 150, 100],
    ['outdoor_cinema_lawn', 'outdoor_cinema_lawn_v1', 80, 50],
    ['food_truck_plaza', 'food_truck_plaza_v1', 50, 40],
    ['festival_event_lawn', 'festival_event_lawn_v2', 180, 120],
    ['campus_central_quad', 'campus_central_quad_variant_0', 100, 80],
    ['urban_beach', 'urban_beach_v2', 60, 45],
    ['velodrome_cycling_track', 'velodrome_cycling_track_variant_0', 135, 82],
    ['mountain_bike_park', 'mountain_bike_park_variant_2', 90, 60],
  ] as const)('fits the complete batch-6 %s/%s program inside its nominal parcel', (
    archetypeId, variantId, width, height,
  ) => {
    const candidate = zone(archetypeId);
    candidate.properties = {
      ...candidate.properties,
      green_space_selected_variant_id: variantId,
    };
    const profile = resolveParkGroundProfile(candidate);
    const fit = fitParkGroundGuides(profile.guides, { width, height });
    expect(fit.omittedGuides, archetypeId).toHaveLength(0);
    expect(fit.guides.length, archetypeId).toBe(profile.guides.length);
  });

  it.each([
    ['disc_golf_course', 300, 200],
    ['bocce_petanque_court', 28, 16],
    ['climbing_bouldering_wall', 25, 20],
    ['mini_golf_course', 50, 30],
    ['beach_volleyball_courts', 24, 16],
    ['pollinator_meadow', 80, 60],
    ['urban_orchard_food_forest', 60, 50],
    ['bioswale_rain_garden', 60, 15],
    ['sculpture_garden', 60, 50],
    ['labyrinth_meditation', 20, 20],
  ] as const)('fits the complete %s v0 program inside its catalogue nominal parcel', (
    archetypeId, width, height,
  ) => {
    const profile = resolveParkGroundProfile(zone(archetypeId));
    const fit = fitParkGroundGuides(profile.guides, { width, height });
    expect(fit.omittedGuides, `${archetypeId}: ${JSON.stringify(fit.omittedGuides)}`).toHaveLength(0);
    expect(fit.guides, archetypeId).toHaveLength(profile.guides.length);
  });

  it('gives every recurring master-planner public realm an authoritative layout guide', () => {
    const plannerArchetypes = [
      'neighborhood_park',
      'urban_pocket_park',
      'linear_park_greenway',
      'formal_civic_plaza',
      'fountain_water_feature',
      'stormwater_retention_pond',
    ];
    for (const id of plannerArchetypes) {
      const profile = resolveParkGroundProfile(zone(id));
      expect(profile.isPilot, id).toBe(true);
      expect(profile.guides.length, id).toBeGreaterThan(0);
      expect(profile.criticalConstraints.length, id).toBeGreaterThan(120);
    }
    expect(resolveParkGroundProfile(zone('linear_park_greenway')).guides[0].kind).toBe('axis');
  });

  it('invalidates the source signature after geometry, variant, or archetype changes', () => {
    const base = zone('neighborhood_park');
    const signature = parkGroundSourceSignature(base);
    const moved = { ...base, coordinates: base.coordinates.map(([x, y], i) => [x + (i === 0 ? 0.0001 : 0), y]) };
    const variant = { ...base, properties: { ...base.properties, green_space_selected_variant_id: 'neighborhood_park_v2' } };
    const access = { ...base, properties: { ...base.properties, park_access_points: [[-114.07, 51.041]] } };
    // Compatibility lock for existing paid orthophotos: the legacy V6 object
    // shape, property order and FNV-1a hash may not drift during LEGO rollout.
    expect(signature).toBe('pg6-ae6dfa95');
    expect(parkGroundSourceSignature(moved)).not.toBe(signature);
    expect(parkGroundSourceSignature(variant)).not.toBe(signature);
    expect(parkGroundSourceSignature(access)).not.toBe(signature);
    expect(parkGroundSourceSignature(zone('japanese_garden'))).not.toBe(signature);
  });

  it('keeps an untrusted nested recipe on the exact legacy V6 cache identity', () => {
    const legacy = zone('neighborhood_park');
    const untrusted = {
      ...legacy,
      properties: {
        ...legacy.properties,
        public_realm_lego: {
          family_id: 'park_neighborhood_community',
          family_version: 1,
          archetype_id: 'neighborhood_park',
          variant_id: 'neighborhood_park_v0',
          appearance_kit_id: 'rustic_timber_gravel_v1',
          planting_structure: 'active_recreation',
        },
      },
    } satisfies SiteZone;
    expect(parkGroundSourceSignature(untrusted)).toBe(parkGroundSourceSignature(legacy));
    expect(parkGroundSourceSignature(untrusted)).toMatch(/^pg6-/);
  });

  it('treats open and explicitly closed polygon rings as the same ground source', () => {
    const open = zone('reservoir_watershed_park_variant_0');
    const closed = {
      ...open,
      coordinates: [...open.coordinates, [...open.coordinates[0]]],
    } satisfies SiteZone;
    expect(parkGroundSourceSignature(closed)).toBe(parkGroundSourceSignature(open));
  });

  it('compiles catalog semantics for non-hand-authored parks instead of a neighborhood fallback', () => {
    const profile = resolveParkGroundProfile(zone('wetland_rain_garden'));
    expect(profile.isPilot).toBe(true);
    expect(profile.guides.length).toBeGreaterThan(0);
    expect(profile.plantingStructure).toBe('water_ecology');
    expect(profile.programDescription.toLowerCase()).toContain('wetland');
  });

  it('never mistakes courtyards or forecourts for sports courts', () => {
    for (const id of [
      'courtyard_plaza',
      'academic_courtyard',
      'cathedral_religious_forecourt',
      'cultural_institution_forecourt',
    ]) {
      const profile = resolveParkGroundProfile(zone(id));
      expect(profile.plantingStructure, id).not.toBe('sports_recreation');
      expect(profile.guides.some((guide) => guide.kind === 'tennis_court'), id).toBe(false);
      expect(profile.guides.some((guide) => guide.kind === 'soccer_field'), id).toBe(false);
    }
    expect(resolveParkGroundProfile(zone('pickleball_courts')).plantingStructure)
      .toBe('sports_perimeter');
    expect(resolveParkPlantingStructure(zone('cricket_pitch_oval')))
      .toBe('sports_perimeter');
  });

  it('prefers the nested Public Realm LEGO selection and records its family contract', () => {
    const candidate = zone('neighborhood_park');
    candidate.properties = {
      ...candidate.properties,
      public_realm_lego: trustedParkRecipe({
        family_id: 'park_neighborhood_community',
        family_version: 1,
        archetype_id: 'community_park',
        variant_id: 'community_park_v0',
        planting_structure: 'naturalistic_grove',
        appearance_kit_id: 'english_pastoral_v1',
      }),
    };
    const profile = resolveParkGroundProfile(candidate);
    expect(profile.archetypeId).toBe('community_park');
    expect(profile.title).toContain('English Pastoral');
    expect(profile.legoFamilyId).toBe('park_neighborhood_community');
    expect(profile.legoFamilyVersion).toBe(1);
    expect(profile.variantId).toBe('community_park_v0');
    expect(resolveParkPlantingStructure(candidate)).toBe('naturalistic_grove');
    expect(profile.guides).toHaveLength(5);
    const changedRecipe = {
      ...candidate,
      properties: {
        ...candidate.properties,
        public_realm_lego: {
          ...(candidate.properties?.public_realm_lego as Record<string, unknown>),
          recipe_hash: 'd'.repeat(64),
        },
      },
    } satisfies SiteZone;
    expect(parkGroundSourceSignature(changedRecipe))
      .not.toBe(parkGroundSourceSignature(candidate));
    expect(parkGroundSourceSignature(candidate)).toMatch(/^pg7-/);
  });

  it('binds civic, greenway, and water families to their executable signature assemblies', () => {
    const civic = zone('formal_civic_plaza');
    civic.properties = {
      ...civic.properties,
      planting_structure: 'active_recreation',
      public_realm_lego: trustedParkRecipe({
        family_id: 'park_civic_plaza',
        family_version: 1,
        archetype_id: 'formal_civic_plaza',
        variant_id: 'formal_civic_plaza_v0',
        appearance_kit_id: 'neoclassical_stone_v1',
        planting_structure: 'paved_plaza',
      }),
    };
    expect(resolveParkSpecialtyStructureKind(civic)).toBe('civic_fountain_assembly');
    expect(resolveParkPlantingStructure(civic)).toBe('paved_plaza');

    const water = zone('stormwater_retention_pond');
    water.properties = {
      ...water.properties,
      public_realm_lego: trustedParkRecipe({
        family_id: 'park_water_ecology',
        family_version: 1,
        archetype_id: 'stormwater_retention_pond',
        variant_id: 'stormwater_retention_pond_v0',
        appearance_kit_id: 'naturalistic_pond_v1',
        planting_structure: 'reservoir_perimeter',
      }),
    };
    expect(resolveParkSpecialtyStructureKind(water)).toBe('stormwater_control_assembly');
    const waterProfile = resolveParkGroundProfile(water);
    expect(waterProfile.archetypeId).toBe('stormwater_retention_pond');
    expect(waterProfile.guides.map(({ kind }) => kind))
      .toEqual(['ellipse', 'rectangle', 'rectangle', 'polyline']);
    expect(waterProfile.guideLegend.join(' ')).toContain('maintenance route');

    const greenway = zone('linear_park_greenway');
    greenway.properties = {
      ...greenway.properties,
      public_realm_lego: trustedParkRecipe({
        family_id: 'park_linear_greenway',
        family_version: 1,
        archetype_id: 'linear_park_greenway',
        variant_id: 'linear_park_greenway_v0',
        appearance_kit_id: 'rail_trail_v1',
        planting_structure: 'naturalistic_grove',
      }),
    };
    expect(resolveParkSpecialtyStructureKind(greenway)).toBe('greenway_edge_assembly');

    const skate = zone('skate_park');
    skate.properties = {
      ...skate.properties,
      public_realm_lego: trustedParkRecipe({
        family_id: 'park_skate_archetype_v0',
        family_version: 1,
        archetype_id: 'skate_park',
        variant_id: 'skate_park_v0',
        appearance_kit_id: 'skate_park_v0_reference_skin',
        planting_structure: 'skate_archetype_v0',
      }),
    };
    expect(resolveParkSpecialtyStructureKind(skate)).toBe('skate_park_v0_assembly');
    expect(resolveParkPlantingStructure(skate)).toBe('skate_archetype_v0');

    for (const [family_id, archetype_id, variant_id, appearance_kit_id, planting_structure, expected] of [
      ['park_inclusive_playground_v0', 'inclusive_playground', 'inclusive_playground_v0', 'inclusive_playground_v0_reference_skin', 'inclusive_playground_v0', 'inclusive_playground_v0_assembly'],
      ['park_dog_archetype_v0', 'dog_park', 'dog_park_v0', 'dog_park_v0_reference_skin', 'dog_park_v0', 'dog_park_v0_assembly'],
      ['park_splash_pad_v0', 'splash_pad_area', 'splash_pad_area_v0', 'splash_pad_area_v0_reference_skin', 'splash_pad_area_v0', 'splash_pad_v0_assembly'],
      ['park_community_garden_v0', 'community_garden', 'community_garden_v0', 'community_garden_v0_reference_skin', 'community_garden_v0', 'community_garden_v0_assembly'],
      ['park_tennis_cluster_v0', 'tennis_court_cluster', 'tennis_court_cluster_v0', 'tennis_court_cluster_v0_reference_skin', 'tennis_court_cluster_v0', 'tennis_cluster_v0_assembly'],
      ['park_nature_play_v0', 'nature_play_area', 'nature_play_area_v0', 'nature_play_area_v0_reference_skin', 'nature_play_area_v0', 'nature_play_v0_assembly'],
      ['park_pump_track_v0', 'pump_track', 'pump_track_v0', 'pump_track_v0_reference_skin', 'pump_track_v0', 'pump_track_v0_assembly'],
      ['park_outdoor_fitness_v0', 'outdoor_fitness_circuit', 'outdoor_fitness_circuit_v0', 'outdoor_fitness_circuit_v0_reference_skin', 'outdoor_fitness_circuit_v0', 'outdoor_fitness_v0_assembly'],
      ['park_memorial_garden_v0', 'memorial_garden', 'memorial_garden_v0', 'memorial_garden_v0_reference_skin', 'memorial_garden_v0', 'memorial_garden_v0_assembly'],
    ]) {
      const exact = zone(archetype_id);
      exact.properties = { ...exact.properties, public_realm_lego: trustedParkRecipe({
        family_id, family_version: 1, archetype_id, variant_id, appearance_kit_id, planting_structure,
      }) };
      expect(resolveParkSpecialtyStructureKind(exact)).toBe(expected);
    }
  });

  it('compiles every open-space catalog entry and variant to an explicit 3D ground contract', () => {
    const entries = openSpaceCatalog.archetypes;
    expect(entries).toHaveLength(130);
    expect(entries.reduce((sum, entry) => sum + entry.variants.length, 0)).toBe(520);
    for (const entry of entries) {
      const base = zone(entry.id);
      const profile = resolveParkGroundProfile(base);
      expect(profile.isPilot, entry.id).toBe(true);
      expect(profile.archetypeId, entry.id).toBe(entry.id);
      expect(profile.guides.length, entry.id).toBeGreaterThan(0);
      expect(profile.guideLegend.length, entry.id).toBeGreaterThan(0);
      expect(profile.criticalConstraints.length, entry.id).toBeGreaterThan(180);
      expect(profile.plantingStructure, entry.id).toBeTruthy();
      for (const variant of entry.variants) {
        const variantZone = {
          ...base,
          properties: {
            ...base.properties,
            green_space_selected_variant_id: variant.id,
          },
        } satisfies SiteZone;
        const variantProfile = resolveParkGroundProfile(variantZone);
        expect(variantProfile.title, `${entry.id}/${variant.id}`).toContain(variant.label);
        if (entry.id === 'basketball_court') {
          expect(variantProfile.isPilot).toBe(true);
          expect(variantProfile.programDescription).not.toContain('without changing the locked program');
          expect(variantProfile.plantingStructure).toContain(`v${variant.id.slice(-1)}`);
        } else if (PILOT_PARK_ARCHETYPE_IDS.includes(entry.id)) {
          expect(variantProfile.programDescription, `${entry.id}/${variant.id}`)
            .toContain(`Selected variant style: ${variant.label}`);
          expect(variantProfile.renderSummary, `${entry.id}/${variant.id}`)
            .toContain('without changing the locked program');
        } else {
          expect(variantProfile.programDescription, `${entry.id}/${variant.id}`)
            .toContain(variant.description);
        }
        expect(parkGroundSourceSignature(variantZone), `${entry.id}/${variant.id}`)
          .not.toBe(parkGroundSourceSignature(base));
      }
    }
  });

  it('keeps common court and field archetypes at regulation metric scale', () => {
    const tennis = resolveParkGroundProfile(zone('tennis_court_cluster')).guides
      .filter((guide) => guide.kind === 'tennis_court');
    expect(tennis).toHaveLength(4);
    for (const court of tennis) {
      expect(resolveParkGuideDimensionsM(court, { width: 82, height: 46 }))
        .toEqual({ width: 36.58, height: 18.29 });
    }
    const pickleball = resolveParkGroundProfile(zone('pickleball_courts')).guides;
    expect(pickleball).toHaveLength(2);
    for (const court of pickleball) {
      expect(resolveParkGuideDimensionsM(court, { width: 45, height: 30 }))
        .toEqual({ width: 18.29, height: 9.14 });
    }
    const basketballBase = zone('basketball_court');
    for (const variantIndex of [0, 1, 3]) {
      const basketball = resolveParkGroundProfile({
        ...basketballBase,
        properties: {
          ...basketballBase.properties,
          green_space_selected_variant_id: `basketball_court_v${variantIndex}`,
        },
      }).guides;
      expect(basketball).toHaveLength(variantIndex === 3 ? 1 : 2);
      for (const court of basketball) {
        expect(court.kind).toBe('basketball_court');
        expect(resolveParkGuideDimensionsM(court, { width: 80, height: 45 }))
          .toEqual({ width: 32, height: 19 });
      }
    }
    const halfCourt = resolveParkGroundProfile({
      ...basketballBase,
      properties: {
        ...basketballBase.properties,
        green_space_selected_variant_id: 'basketball_court_v2',
      },
    }).guides;
    expect(halfCourt).toHaveLength(1);
    expect(resolveParkGuideDimensionsM(halfCourt[0], { width: 25, height: 20 }))
      .toEqual({ width: 19, height: 17 });
    const track = resolveParkGroundProfile(zone('running_track_oval')).guides[0];
    expect(resolveParkGuideDimensionsM(track, { width: 220, height: 130 }))
      .toEqual({ width: 176.91, height: 92.52 });
    for (const pitch of resolveParkGroundProfile(zone('soccer_pitch_caged')).guides) {
      expect(resolveParkGuideDimensionsM(pitch, { width: 90, height: 40 }))
        .toEqual({ width: 30, height: 18 });
    }
    for (const field of resolveParkGroundProfile(zone('athletics_precinct_sports_fields')).guides) {
      expect(resolveParkGuideDimensionsM(field, { width: 260, height: 150 }))
        .toEqual({ width: 100, height: 64 });
    }
  });

  it('keeps toolbar plazas hardscaped instead of falling back to a lawn park', () => {
    const plaza = {
      ...zone('formal_civic_plaza'),
      zone_type: 'parking' as const,
      properties: { plaza_archetype_id: 'formal_civic_plaza' },
    };
    const profile = resolveParkGroundProfile(plaza);
    expect(profile.title.toLowerCase()).toContain('plaza');
    expect(profile.archetypeId).toBe('formal_civic_plaza');
    expect(resolveParkPlantingStructure(plaza)).toBe('paved_plaza');
    expect(profile.groundDescription.toLowerCase()).not.toContain('mowed lawn');
    expect(buildParkGroundPrompt(
      plaza,
      { width: 50, height: 35 },
      { playground: 0, pavilion: 0, bench: 2, plaza: 0 },
    )).toContain('warm-grey polygon is the plaza parcel');
    expect(isParkGroundZone(plaza)).toBe(true);
  });

  it('accepts planner courtyards even when their legacy zone type is development-like', () => {
    const courtyard = {
      ...zone('urban_pocket_park'),
      zone_type: 'development_area' as const,
      properties: { _plan_role: 'courtyard', green_space_archetype_id: 'urban_pocket_park' },
    };
    expect(isParkGroundZone(courtyard)).toBe(true);
  });

  it('does not inject the neighborhood plaza into specialty park prompts', () => {
    const emptyMarkers = { playground: 0, pavilion: 0, bench: 0, plaza: 0 };
    const japanese = buildParkGroundPrompt(zone('japanese_garden'), { width: 60, height: 50 }, emptyMarkers);
    const sports = buildParkGroundPrompt(zone('sports_field_complex'), { width: 140, height: 90 }, emptyMarkers);
    const neighborhood = buildParkGroundPrompt(zone('neighborhood_park'), { width: 80, height: 60 }, emptyMarkers);
    expect(japanese).not.toContain('small circular paved plaza');
    expect(sports).not.toContain('small circular paved plaza');
    expect(neighborhood).not.toContain('small circular paved plaza');
  });

  it('treats an authored specialty diagram as a tracing template instead of inventing circulation', () => {
    const prompt = buildParkGroundPrompt(
      zone('botanical_garden'),
      { width: 146, height: 80 },
      { playground: 0, pavilion: 0, bench: 0, plaza: 0, access: 0 },
    );
    expect(prompt).toContain('Do not add any new path, spur, axis, ring, radial connection, plaza or entrance');
    expect(prompt).not.toContain('Provide a connected internal path network');
    expect(prompt).toContain('FINAL PIXEL-TO-PIXEL TOPOLOGY LOCK');
    expect(prompt).toContain('Do not create any additional hardscape, path branch, radial axis, circle, plaza, bed, water feature or structure.');
  });

  it('uses a saved render as appearance only while preserving diagram topology', () => {
    const prompt = buildParkGroundPrompt(
      zone('wetland_rain_garden'),
      { width: 80, height: 60 },
      { playground: 0, pavilion: 0, bench: 0, plaza: 0, access: 0 },
      true,
    );
    expect(prompt).toContain('APPEARANCE TARGET');
    expect(prompt).toContain('do not copy the render camera');
    expect(prompt).toContain('the diagram always wins for boundary, scale, count and topology');
    expect(prompt).toContain('looping boardwalk network');
    expect(prompt).toContain('FINAL PIXEL-TO-PIXEL TOPOLOGY LOCK');
  });

  it('includes measured surroundings without weakening the diagram topology lock', () => {
    const prompt = buildParkGroundPrompt(
      zone('neighborhood_park'),
      { width: 80, height: 60 },
      { playground: 0, pavilion: 0, bench: 0, plaza: 0, access: 2 },
      false,
      'SURROUNDING-SITE CONTEXT:\n- proposed street "Main Street" touches on the east edge\nEDGE RESPONSE: align park gateways with the street.',
    );

    expect(prompt).toContain('proposed street "Main Street"');
    expect(prompt).toContain('align park gateways with the street');
    expect(prompt).toContain('FINAL PIXEL-TO-PIXEL TOPOLOGY LOCK');
    expect(prompt.indexOf('SURROUNDING-SITE CONTEXT'))
      .toBeLessThan(prompt.indexOf('FINAL PIXEL-TO-PIXEL TOPOLOGY LOCK'));
  });

  it('selects the newest saved render as the drape appearance target', () => {
    expect(selectLatestParkRenderReference([
      { id: 'older', created_at: '2026-07-17T12:00:00Z' },
      { id: 'newest', created_at: '2026-07-18T12:00:00Z' },
      { id: 'middle', created_at: '2026-07-18T06:00:00Z' },
    ])?.id).toBe('newest');
    expect(selectLatestParkRenderReference([])).toBeNull();
  });

  it('locks the five same-geography alternatives to distinct programs', () => {
    const emptyMarkers = { playground: 0, pavilion: 0, bench: 0, plaza: 0, access: 2 };
    const prompts = Object.fromEntries([
      'sports_field_complex',
      'urban_forest',
      'botanical_garden',
      'japanese_garden',
      'nature_play_area',
    ].map((id) => [id, buildParkGroundPrompt(zone(id), { width: 146, height: 80 }, emptyMarkers)]));

    expect(prompts.sports_field_complex).toContain('100 by 64 metre football/soccer pitch');
    expect(prompts.sports_field_complex).toContain('36.58 by 18.29 metres');
    expect(prompts.urban_forest).toContain('three quarters of the parcel must read as woodland habitat');
    expect(prompts.botanical_garden).toContain('conservatory pad');
    expect(prompts.japanese_garden).toContain('exact red lacquer bridge-deck footprint');
    expect(prompts.nature_play_area).toContain('two linked activity clearings');
  });

  it('keeps fixed park programs at real-world metre dimensions on the trial parcel', () => {
    const trialSize = { width: 146, height: 80 };
    const sports = resolveParkGroundProfile(zone('sports_field_complex')).guides;
    const football = sports.find((guide) => guide.kind === 'soccer_field');
    const tennis = sports.filter((guide) => guide.kind === 'tennis_court');
    expect(football && resolveParkGuideDimensionsM(football, trialSize)).toEqual({
      width: 100,
      height: 64,
    });
    expect(tennis).toHaveLength(3);
    for (const court of tennis) {
      expect(resolveParkGuideDimensionsM(court, trialSize)).toEqual({
        width: 36.58,
        height: 18.29,
      });
    }

    const japanese = resolveParkGroundProfile(zone('japanese_garden')).guides;
    expect(resolveParkGuideDimensionsM(japanese[1], trialSize)).toEqual({ width: 34, height: 20 });
    expect(resolveParkGuideDimensionsM(japanese[2], trialSize)).toEqual({ width: 22, height: 14 });
    expect(resolveParkGuideDimensionsM(japanese[3], trialSize)).toEqual({
      width: JAPANESE_GARDEN_BRIDGE_DIMENSIONS_M.length,
      height: 0,
    });

    const botanical = resolveParkGroundProfile(zone('botanical_garden')).guides;
    expect(resolveParkGuideDimensionsM(botanical[1], trialSize)).toEqual({ width: 24, height: 14 });
    const naturePlay = resolveParkGroundProfile(zone('nature_play_area')).guides;
    expect(resolveParkGuideDimensionsM(naturePlay[2], trialSize)).toEqual({ width: 28, height: 22 });
    expect(resolveParkGuideDimensionsM(naturePlay[3], trialSize)).toEqual({ width: 30, height: 22 });
    expect(resolveParkGuideDimensionsM(naturePlay[4], trialSize)).toEqual({ width: 14, height: 5 });
  });

  it('omits a complete tennis court when a concave parcel would clip it', () => {
    const sports = resolveParkGroundProfile(zone('sports_field_complex')).guides;
    const fit = fitParkGroundGuides(
      sports,
      { width: 144, height: 76.8 },
      [[0, 0], [0.82, 0], [0.82, 0.34], [1, 0.34], [1, 1], [0, 1]],
    );

    expect(fit.guides.filter((guide) => guide.kind === 'soccer_field')).toHaveLength(1);
    expect(fit.guides.filter((guide) => guide.kind === 'tennis_court')).toHaveLength(2);
    expect(fit.omittedGuides.filter((guide) => guide.kind === 'tennis_court')).toHaveLength(1);
    expect(describeParkGroundGuideFit(fit)).toContain('2 complete tennis courts fit out of 3');
  });

  it('reduces a four-court archetype to one complete court on a small parcel', () => {
    const tennis = resolveParkGroundProfile(zone('tennis_court_cluster')).guides;
    const fit = fitParkGroundGuides(tennis, { width: 46, height: 26 });

    expect(fit.guides.filter((guide) => guide.kind === 'tennis_court')).toHaveLength(1);
    expect(fit.omittedGuides.filter((guide) => guide.kind === 'tennis_court')).toHaveLength(3);
    expect(describeParkGroundGuideFit(fit)).toContain('1 complete tennis court fits out of 4');
  });

  it('adds a second complete caged pitch instead of stretching one on an oversized site', () => {
    const pitches = resolveParkGroundProfile(zone('soccer_pitch_caged')).guides;
    const compact = fitParkGroundGuides(pitches, { width: 38, height: 24 });
    const oversized = fitParkGroundGuides(pitches, { width: 75, height: 24 });

    expect(compact.guides.filter((guide) => guide.kind === 'soccer_field')).toHaveLength(1);
    expect(oversized.guides.filter((guide) => guide.kind === 'soccer_field')).toHaveLength(2);
    for (const pitch of [...compact.guides, ...oversized.guides]) {
      expect(resolveParkGuideDimensionsM(pitch, { width: 75, height: 24 }))
        .toEqual({ width: 30, height: 18 });
    }
  });

  it('adapts a full-size athletics precinct by complete 100 x 64 metre fields', () => {
    const fields = resolveParkGroundProfile(zone('athletics_precinct_sports_fields')).guides;
    const compact = fitParkGroundGuides(fields, { width: 120, height: 80 });
    const oversized = fitParkGroundGuides(fields, { width: 230, height: 80 });

    expect(compact.guides.filter((guide) => guide.kind === 'soccer_field')).toHaveLength(1);
    expect(oversized.guides.filter((guide) => guide.kind === 'soccer_field')).toHaveLength(2);
    for (const field of [...compact.guides, ...oversized.guides]) {
      expect(resolveParkGuideDimensionsM(field, { width: 230, height: 80 }))
        .toEqual({ width: 100, height: 64 });
    }
  });

  it('finds orientations for the field and all three whole courts in the current sloped trial parcel', () => {
    const sports = resolveParkGroundProfile(zone('sports_field_complex')).guides;
    const fit = fitParkGroundGuides(
      sports,
      { width: 144, height: 76.8 },
      [
        [0, 0.9172],
        [0.0316, 0],
        [1, 0.1288],
        [0.983, 1],
      ],
    );

    const fittedField = fit.guides.find((guide) => guide.kind === 'soccer_field');
    expect(fittedField).toBeDefined();
    expect(fit.guides.filter((guide) => guide.kind === 'tennis_court')).toHaveLength(3);
    expect(fit.omittedGuides.filter((guide) => guide.kind === 'tennis_court')).toHaveLength(0);
    expect(fittedField?.rotationDeg).not.toBe(0);
    expect(describeParkGroundGuideFit(fit)).toBe('');
  });

  it('turns a regulation court to an alternate orientation when that is the only whole fit', () => {
    const fit = fitParkGroundGuides([{
      kind: 'tennis_court',
      x: 0.5,
      y: 0.5,
      width: 0.9,
      height: 0.9,
      widthM: 36.58,
      heightM: 18.29,
      color: '#3f6f82',
      strokeColor: '#f4f2df',
      strokeWidthM: 0.08,
    }], { width: 20, height: 40 });

    expect(fit.guides).toHaveLength(1);
    expect(Math.abs(fit.guides[0].rotationDeg ?? 0)).toBe(90);
    expect(resolveParkGuideDimensionsM(fit.guides[0], { width: 20, height: 40 }))
      .toEqual({ width: 36.58, height: 18.29 });
  });

  it('removes every part of a grouped object when its outer envelope does not fit', () => {
    const fit = fitParkGroundGuides([
      {
        kind: 'ellipse', x: 0.5, y: 0.5, width: 1, height: 1,
        widthM: 120, heightM: 120, color: '#668855', atomicGroup: 'cricket-field',
      },
      {
        kind: 'rectangle', x: 0.5, y: 0.5, width: 0.1, height: 0.1,
        widthM: 22.56, heightM: 3.05, color: '#aa9966', atomicGroup: 'cricket-field',
      },
    ], { width: 100, height: 100 });

    expect(fit.guides).toHaveLength(0);
    expect(fit.omittedGuides).toHaveLength(2);
  });

  it('keeps an omitted cricket oval as clearance-only placement geometry', () => {
    const cricket = resolveParkGroundProfile(zone('cricket_pitch_oval')).guides;
    const fit = fitParkGroundGuides(cricket, { width: 137, height: 71 });
    const placementGuides = resolveParkPlacementGuides(fit);

    expect(fit.guides).toHaveLength(0);
    expect(placementGuides).toHaveLength(1);
    expect(placementGuides[0]).toMatchObject({
      kind: 'track',
      width: 0.86,
      height: 0.76,
      fitPolicy: 'clip',
    });
    expect(placementGuides[0].widthM).toBeUndefined();
    expect(placementGuides[0].heightM).toBeUndefined();
  });

  it('tells the image model to keep only complete parcel-compatible elements', () => {
    const sportsZone = zone('sports_field_complex');
    sportsZone.coordinates = [
      [0, 1], [0.82, 1], [0.82, 0.66], [1, 0.66], [1, 0], [0, 0],
    ];
    const prompt = buildParkGroundPrompt(
      sportsZone,
      { width: 144, height: 76.8 },
      { playground: 0, pavilion: 0, bench: 0, plaza: 0 },
    );

    expect(prompt).toContain('2 complete tennis courts fit out of 3');
    expect(prompt).toContain('Do not draw, reconstruct, crop, truncate, squeeze or scale');
  });

  it('forces the reservoir drape to cover all dry land without diagram-paper margins', () => {
    const prompt = buildParkGroundPrompt(
      zone('reservoir_watershed_park'),
      { width: 148, height: 84 },
      { playground: 0, pavilion: 0, bench: 6, plaza: 0 },
    );
    expect(prompt).toContain('covering about 42 percent of the parcel');
    expect(prompt).toContain('fully rendered edge-to-edge');
    expect(prompt).toContain('zero white, blank, unpainted or paper-like ground');
    expect(prompt).toContain('Every dry-land pixel');
  });

  it('locks the five added planner grounds to their actual programs', () => {
    const emptyMarkers = { playground: 0, pavilion: 0, bench: 0, plaza: 0, access: 2 };
    const prompts = Object.fromEntries([
      'urban_pocket_park',
      'linear_park_greenway',
      'formal_civic_plaza',
      'fountain_water_feature',
      'stormwater_retention_pond',
    ].map((id) => [id, buildParkGroundPrompt(zone(id), { width: 90, height: 50 }, emptyMarkers)]));

    expect(prompts.urban_pocket_park).toContain('one usable clear room');
    expect(prompts.urban_pocket_park).toContain('no playground');
    expect(prompts.linear_park_greenway).toContain('exact continuous 3.5-metre multi-use trail');
    expect(prompts.linear_park_greenway).toContain('one continuous, obstruction-free route');
    expect(prompts.formal_civic_plaza).toContain('generous contiguous hardscape event area');
    expect(prompts.fountain_water_feature).toContain('one clear circular water basin');
    expect(prompts.stormwater_retention_pond).toContain('functioning stormwater infrastructure');
    expect(prompts.stormwater_retention_pond).toContain('No trees, benches, paths, buildings or decorative features may enter the water');
  });

  it('cleans only edge-connected paper while preserving enclosed pale hardscape', () => {
    const width = 5;
    const height = 5;
    const pixels = new Uint8ClampedArray(width * height * 4);
    for (let pixel = 0; pixel < width * height; pixel += 1) {
      pixels.set([248, 248, 246, 255], pixel * 4);
    }
    // A green ring disconnects the pale centre hardscape from the white edge.
    for (const pixel of [6, 7, 8, 11, 13, 16, 17, 18]) {
      pixels.set([82, 118, 58, 255], pixel * 4);
    }
    pixels.set([245, 245, 242, 255], 12 * 4);

    expect(replaceEdgeConnectedPaperWithTurf(pixels, width, height)).toBe(16);
    expect(Array.from(pixels.slice(12 * 4, 12 * 4 + 3))).toEqual([245, 245, 242]);
    expect(pixels[1]).toBeLessThan(200);
  });

  it('shows finishing props only after a park surface is compiled', () => {
    const candidate = zone('urban_pocket_park');
    const profile = resolveParkGroundProfile(candidate);
    const generated = {
      ...candidate,
      properties: {
        ...candidate.properties,
        community_3d: {
          schema_version: 1,
          state: 'compiled',
          kind: 'park',
          generator: 'park_kit',
          compiled_at: '2026-07-17T00:00:00Z',
        },
        park_ground_texture: {
          url: '/park.png',
          document_id: 'doc-1',
          bbox: { west: -114.071, south: 51.041, east: -114.069, north: 51.042 },
          uv_rect: { u0: 0.1, v0: 0.1, u1: 0.9, v1: 0.9 },
          size_m: { width: 140, height: 110 },
          model: 'gemini-3.1-flash-image',
          generated_at: '2026-07-17T00:00:00Z',
          source_signature: parkGroundSourceSignature(candidate),
          profile_id: profile.id,
          profile_version: profile.version,
          archetype_id: profile.archetypeId,
        },
      },
    } satisfies SiteZone;
    expect(shouldDeferParkFinishingProp(generated, 'tree')).toBe(false);
    expect(shouldDeferParkFinishingProp(generated, 'bench')).toBe(false);
    expect(shouldDeferParkFinishingProp(generated, 'playground')).toBe(false);
    expect(shouldDeferParkFinishingProp(candidate, 'tree')).toBe(true);
    expect(shouldRenderLiveParkProp(candidate, 'tree', true)).toBe(false);
    expect(shouldRenderLiveParkProp(generated, 'tree', true)).toBe(true);
    expect(shouldRenderLiveParkProp(candidate, 'bench', true)).toBe(false);
    expect(shouldRenderLiveParkProp(candidate, 'playground', false)).toBe(false);
    expect(shouldRenderLiveParkProp(candidate, 'playground', true)).toBe(true);
    expect(shouldRenderLiveParkProp(candidate, 'pavilion', false)).toBe(false);
  });

  it('does not pre-author bench locations before paths and water are finalized', () => {
    const prompt = buildParkGroundPrompt(
      zone('reservoir_watershed_park'),
      { width: 148, height: 84 },
      { playground: 0, pavilion: 0, bench: 6, plaza: 0 },
    );
    expect(prompt).not.toContain('DARK dash');
    expect(prompt).not.toContain('bench spot');
    expect(prompt).not.toContain('bench pad');
    expect(prompt).toContain('mature trees and benches are completed by the final architectural render');
  });

  it('uses a zero-call procedural surface after Generate 3D and lets AI ground win', () => {
    const candidate = zone('linear_park_greenway');
    expect(resolveParkGroundSurfaceSource(candidate)).toBe('none');
    expect(hasCurrentParkGroundSurface(candidate)).toBe(false);

    const compiled = {
      ...candidate,
      properties: {
        ...candidate.properties,
        community_3d: {
          schema_version: 1,
          state: 'compiled',
          kind: 'park',
          generator: 'park_kit',
          compiled_at: '2026-07-17T01:00:00Z',
        },
      },
    } satisfies SiteZone;
    expect(resolveParkGroundSurfaceSource(compiled)).toBe('procedural');
    expect(hasCurrentParkGroundSurface(compiled)).toBe(true);

    const profile = resolveParkGroundProfile(compiled);
    const upgraded = {
      ...compiled,
      properties: {
        ...compiled.properties,
        park_ground_texture: {
          url: '/park.png',
          document_id: 'doc-1',
          bbox: { west: -114.071, south: 51.041, east: -114.069, north: 51.042 },
          uv_rect: { u0: 0.1, v0: 0.1, u1: 0.9, v1: 0.9 },
          size_m: { width: 140, height: 110 },
          model: 'gemini-3.1-flash-image',
          generated_at: '2026-07-17T00:00:00Z',
          source_signature: parkGroundSourceSignature(compiled),
          profile_id: profile.id,
          profile_version: profile.version,
          archetype_id: profile.archetypeId,
        },
      },
    } satisfies SiteZone;
    expect(resolveParkGroundSurfaceSource(upgraded)).toBe('ai');
  });

  it('keeps exact Skate Park v0 flat until compile, then overrides a stale AI drape', () => {
    const skate = zone('skate_park');
    skate.properties = {
      ...skate.properties,
      green_space_selected_variant_id: 'skate_park_v0',
      park_ground_texture: {
        url: '/old-flat-drape.png',
        document_id: 'old-doc',
        bbox: { west: -114.071, south: 51.041, east: -114.069, north: 51.042 },
        uv_rect: { u0: 0, v0: 0, u1: 1, v1: 1 },
        size_m: { width: 44, height: 36 },
        model: 'gemini-3.1-flash-image',
        generated_at: '2026-07-17T00:00:00Z',
        source_signature: parkGroundSourceSignature(skate),
        profile_id: 'legacy',
        profile_version: 1,
        archetype_id: 'skate_park',
      },
    };
    expect(resolveParkGroundSurfaceSource(skate)).toBe('none');
    expect(hasCurrentParkGroundSurface(skate)).toBe(false);

    skate.properties = {
      ...skate.properties,
      community_3d: {
        schema_version: 1,
        state: 'compiled',
        kind: 'park',
        generator: 'park_kit',
        compiled_at: '2026-07-17T01:00:00Z',
      },
    };
    expect(resolveParkGroundSurfaceSource(skate)).toBe('procedural');
    expect(hasCurrentParkGroundSurface(skate)).toBe(true);
  });

  it('keeps Basketball Court variants out of the scene until Generate to 3D', () => {
    const basketball = zone('basketball_court');
    basketball.properties = {
      ...basketball.properties,
      green_space_selected_variant_id: 'basketball_court_v3',
    };
    expect(resolveParkGroundSurfaceSource(basketball)).toBe('none');

    basketball.properties = {
      ...basketball.properties,
      community_3d: {
        schema_version: 1,
        state: 'compiled',
        kind: 'park',
        generator: 'park_kit',
        compiled_at: '2026-07-17T01:00:00Z',
      },
    };
    expect(resolveParkGroundSurfaceSource(basketball)).toBe('procedural');
  });

  it('gives all six recurring public-realm archetypes a zero-call compiled ground contract', () => {
    const recurring = [
      'neighborhood_park',
      'urban_pocket_park',
      'linear_park_greenway',
      'formal_civic_plaza',
      'fountain_water_feature',
      'stormwater_retention_pond',
    ];
    for (const archetypeId of recurring) {
      const candidate = zone(archetypeId);
      const compiled = {
        ...candidate,
        properties: {
          ...candidate.properties,
          community_3d: {
            schema_version: 1,
            state: 'compiled',
            kind: 'park',
            generator: 'park_kit',
            compiled_at: '2026-07-18T00:00:00Z',
          },
        },
      } satisfies SiteZone;
      expect(resolveParkGroundProfile(compiled).isPilot, archetypeId).toBe(true);
      expect(resolveParkGroundSurfaceSource(compiled), archetypeId).toBe('procedural');
      expect(hasCurrentParkGroundSurface(compiled), archetypeId).toBe(true);
      expect(shouldDeferParkFinishingProp(compiled, 'tree'), archetypeId).toBe(false);
      expect(shouldDeferParkFinishingProp(compiled, 'bench'), archetypeId).toBe(false);
    }
  });

  it('caps a paid multi-park action to a deliberate six-call batch', () => {
    const pending = Array.from({ length: 83 }, (_, index) => `park-${index}`);
    expect(MAX_PARK_GROUND_BATCH_CALLS).toBe(6);
    expect(takeParkGroundBatch(pending)).toEqual(pending.slice(0, 6));
    expect(takeParkGroundBatch(pending.slice(0, 3))).toEqual(pending.slice(0, 3));
  });

  it('bounds final-render park geometry references and prioritizes critical water/program layouts', () => {
    const candidates = [
      zone('neighborhood_park'),
      zone('formal_civic_plaza'),
      zone('sports_field_complex'),
      zone('japanese_garden'),
      zone('stormwater_retention_pond'),
      zone('reservoir_watershed_park'),
      zone('botanical_garden'),
    ];
    expect(MAX_PARK_RENDER_GEOMETRY_REFERENCES).toBe(4);
    expect(selectParkRenderGeometryZones(candidates).map((candidate) => candidate.name)).toEqual([
      'reservoir_watershed_park',
      'stormwater_retention_pond',
      'japanese_garden',
      'sports_field_complex',
    ]);
    expect(selectParkRenderGeometryZones(candidates, 1)[0].name)
      .toBe('reservoir_watershed_park');
    expect(selectParkRenderGeometryZones(candidates, 0)).toEqual([]);
  });

  it('routes park paths through exact master-plan gateways', () => {
    const prompt = buildParkGroundPrompt(
      zone('neighborhood_park'),
      { width: 80, height: 60 },
      { playground: 0, pavilion: 0, bench: 0, plaza: 0, access: 3 },
    );
    expect(prompt).toContain('3 PALE-CREAM circles');
    expect(prompt).toContain('continuous path centerline to every gateway');
    expect(prompt).toContain('surrounding street/path network');
    expect(prompt).toContain('Never use one perfect circular track');
    expect(prompt).toContain('native meadow and rain-garden');
  });

  it('sets a mature park quality bar appropriate to nadir and oblique views', () => {
    const profile = resolveParkGroundProfile(zone('botanical_garden'));
    const nadir = buildParkRenderQualityInstruction(profile, 18);
    const oblique = buildParkRenderQualityInstruction(profile, 52);
    expect(nadir).toContain('NEAR-NADIR QUALITY');
    expect(nadir).toContain('aerial mosaic');
    expect(oblique).toContain('OBLIQUE QUALITY');
    expect(oblique).toContain('canopy depth');
    expect(oblique).toContain('No cloned evenly spaced trees');
    expect(oblique).toContain('Trees and benches are render-finishing elements');
    expect(oblique).toContain('chosen only after the exact path, water and fixed-program layout is understood');
    expect(oblique).toContain('paved furnishing shoulders directly beside paths');
    expect(oblique).toContain('never put a bench or tree on a path centerline');
  });
});
