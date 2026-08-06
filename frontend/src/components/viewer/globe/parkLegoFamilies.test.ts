import { describe, expect, it } from 'vitest';
import type { SiteZone } from '@/types';

import {
  NEIGHBORHOOD_COMMUNITY_PROGRAM_ANCHORS,
  PARK_LEGO_FAMILY_VERSION,
  PARK_PROGRAM_MODULE_SPEC,
  isExecutableParkLegoFamily,
  resolveParkDressingAppearance,
  resolveParkLegoAppearance,
  resolveParkLegoContract,
  resolveParkDressingFamily,
  resolveParkProgramAnchorLayout,
  usesArchetypeOwnedParkSurface,
} from './parkLegoFamilies';

function zone(properties: Record<string, unknown>): Pick<SiteZone, 'properties' | 'zone_type'> {
  return { zone_type: 'green_space', properties };
}

const TRUSTED_CATALOG_FINGERPRINT = 'a'.repeat(64);
const TRUSTED_CAPABILITY_FINGERPRINT = 'b'.repeat(64);
const TRUSTED_RECIPE_HASH = 'c'.repeat(64);

function trustedRecipe(selection: Record<string, unknown>): Record<string, unknown> {
  return {
    schema_version: 1,
    kind: 'park',
    generator: 'park_kit',
    catalog_fingerprint: TRUSTED_CATALOG_FINGERPRINT,
    capability_fingerprint: TRUSTED_CAPABILITY_FINGERPRINT,
    recipe_hash: TRUSTED_RECIPE_HASH,
    ...selection,
  };
}

describe('Public Realm LEGO V1 park families', () => {
  it('fails closed on the unreviewed picnic-grove variant while retaining safe dressing', () => {
    const candidate = zone({ green_space_archetype_id: 'estate_picnic_grove' });
    expect(resolveParkLegoContract(candidate)).toMatchObject({
      familyId: 'park_estate_oak_picnic_v1',
      variantId: 'estate_picnic_grove_v0',
      supported: false,
    });
    expect(resolveParkDressingFamily(candidate)).toBe('park_neighborhood_community');
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
  ] as const)('executes the exact reviewed Batch 8 selection %s', (familyId, archetypeId, variantId, appearanceKitId, plantingStructure) => {
    const candidate = zone({
      public_realm_lego: trustedRecipe({
        family_id: familyId,
        family_version: 1,
        archetype_id: archetypeId,
        variant_id: variantId,
        appearance_kit_id: appearanceKitId,
        planting_structure: plantingStructure,
      }),
    });
    expect(resolveParkLegoContract(candidate)).toMatchObject({ familyId, archetypeId, variantId, supported: true });
    expect(isExecutableParkLegoFamily(candidate)).toBe(true);
    expect(usesArchetypeOwnedParkSurface(candidate)).toBe(true);
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
  ] as const)('executes the exact reviewed Batch 9 selection %s', (familyId, archetypeId, variantId, appearanceKitId, plantingStructure) => {
    const candidate = zone({
      public_realm_lego: trustedRecipe({
        family_id: familyId,
        family_version: 1,
        archetype_id: archetypeId,
        variant_id: variantId,
        appearance_kit_id: appearanceKitId,
        planting_structure: plantingStructure,
      }),
    });
    expect(resolveParkLegoContract(candidate)).toMatchObject({ familyId, archetypeId, variantId, supported: true });
    expect(isExecutableParkLegoFamily(candidate)).toBe(true);
    expect(usesArchetypeOwnedParkSurface(candidate)).toBe(true);
  });

  it.each([
    ['park_amsterdam_hofje_garden_v0', 'amsterdam_hofje_garden', 'amsterdam_hofje_garden_v0', 'amsterdam_hofje_garden_v0_skin', 'amsterdam_hofje_v0'],
    ['park_amsterdam_plein_v0', 'amsterdam_plein', 'amsterdam_plein_v0', 'amsterdam_plein_v0_brick_skin', 'amsterdam_plein_v0'],
    ['park_amsterdam_vondelpark_pavilion_v3', 'amsterdam_vondelpark', 'amsterdam_vondelpark_v3', 'amsterdam_vondelpark_v3_pavilion_skin', 'amsterdam_vondelpark_v3'],
    ['park_barcelona_pati_green_v0', 'barcelona_pati_interior', 'barcelona_pati_interior_v0', 'barcelona_pati_interior_v0_green_skin', 'barcelona_pati_green_v0'],
    ['park_barcelona_xamfra_corner_v2', 'barcelona_placa_xamfra', 'barcelona_placa_xamfra_v2', 'barcelona_placa_xamfra_v2_corner_skin', 'barcelona_xamfra_v2'],
    ['park_barcelona_superilla_green_v1', 'barcelona_superilla', 'barcelona_superilla_v1', 'barcelona_superilla_v1_green_skin', 'barcelona_superilla_v1'],
    ['park_calgary_prairie_market_v1', 'calgary_prairie_plaza', 'calgary_prairie_plaza_v1', 'calgary_prairie_plaza_v1_market_skin', 'calgary_prairie_market_v1'],
    ['park_calgary_princes_island_festival_v0', 'calgary_princes_island', 'calgary_princes_island_v0', 'calgary_princes_island_v0_festival_skin', 'calgary_princes_island_v0'],
    ['park_montreal_mount_royal_grove_v2', 'montreal_mount_royal', 'montreal_mount_royal_v2', 'montreal_mount_royal_v2_grove_skin', 'montreal_mount_royal_v2'],
    ['park_montreal_neighbourhood_square_v3', 'montreal_square', 'montreal_square_v3', 'montreal_square_v3_neighbourhood_skin', 'montreal_square_v3'],
  ] as const)('executes the exact reviewed Batch 10 selection %s', (familyId, archetypeId, variantId, appearanceKitId, plantingStructure) => {
    const candidate = zone({
      public_realm_lego: trustedRecipe({
        family_id: familyId,
        family_version: 1,
        archetype_id: archetypeId,
        variant_id: variantId,
        appearance_kit_id: appearanceKitId,
        planting_structure: plantingStructure,
      }),
    });
    expect(resolveParkLegoContract(candidate)).toMatchObject({ familyId, archetypeId, variantId, supported: true });
    expect(isExecutableParkLegoFamily(candidate)).toBe(true);
    expect(usesArchetypeOwnedParkSurface(candidate)).toBe(true);
  });

  it.each([
    ['park_paris_place_royale_v2','parisian_place','parisian_place_v2','parisian_place_v2_royale_skin','paris_place_royale_v2'],
    ['park_paris_square_tree_grid_v3','parisian_square','parisian_square_v3','parisian_square_v3_tree_grid_skin','paris_square_tree_grid_v3'],
    ['park_london_circus_planted_v1','london_circus','london_circus_v1','london_circus_v1_planted_skin','london_circus_planted_v1'],
    ['park_newyork_pocket_water_v0','newyork_pocket_park','newyork_pocket_park_v0','newyork_pocket_park_v0_water_skin','newyork_pocket_water_v0'],
    ['park_newyork_community_greenhouse_v3','newyork_community_garden','newyork_community_garden_v3','newyork_community_garden_v3_greenhouse_skin','newyork_community_greenhouse_v3'],
    ['park_vancouver_seawall_cycle_v2','vancouver_seawall','vancouver_seawall_v2','vancouver_seawall_v2_cycle_skin','vancouver_seawall_cycle_v2'],
    ['park_vancouver_beach_pavilion_v0','vancouver_beach_park','vancouver_beach_park_v0','vancouver_beach_park_v0_pavilion_skin','vancouver_beach_pavilion_v0'],
    ['park_toronto_ravine_creek_v1','toronto_ravine','toronto_ravine_v1','toronto_ravine_v1_creek_skin','toronto_ravine_creek_v1'],
    ['park_toronto_urban_market_v1','toronto_urban_square','toronto_urban_square_v1','toronto_urban_square_v1_market_skin','toronto_urban_market_v1'],
    ['park_halifax_coastal_fog_path_v2','halifax_coastal_park','halifax_coastal_park_v2','halifax_coastal_park_v2_fog_path_skin','halifax_coastal_fog_path_v2'],
  ] as const)('executes the exact reviewed Batch 11 selection %s', (familyId, archetypeId, variantId, appearanceKitId, plantingStructure) => {
    const candidate = zone({ public_realm_lego: trustedRecipe({ family_id: familyId, family_version: 1, archetype_id: archetypeId, variant_id: variantId, appearance_kit_id: appearanceKitId, planting_structure: plantingStructure }) });
    expect(resolveParkLegoContract(candidate)).toMatchObject({familyId,archetypeId,variantId,supported:true});
    expect(isExecutableParkLegoFamily(candidate)).toBe(true);
    expect(usesArchetypeOwnedParkSurface(candidate)).toBe(true);
  });

  it.each([
    ['park_city_hall_modernist_fountain_v2','city_hall_government_plaza','city_hall_government_plaza_v2','city_hall_government_plaza_v2_modernist_skin','city_hall_modernist_fountain_v2'],
    ['park_cathedral_courtyard_fountain_v3','cathedral_religious_forecourt','cathedral_religious_forecourt_v3','cathedral_religious_forecourt_v3_courtyard_skin','cathedral_courtyard_fountain_v3'],
    ['park_cultural_museum_terrace_v0','cultural_institution_forecourt','cultural_institution_forecourt_v0','cultural_institution_forecourt_v0_museum_terrace_skin','cultural_museum_terrace_v0'],
    ['park_transit_green_civic_v2','transit_plaza','transit_plaza_v2','transit_plaza_v2_green_civic_skin','transit_green_civic_v2'],
    ['park_amphitheater_terraced_v0','amphitheater_performance_space','amphitheater_performance_space_v0','amphitheater_performance_space_v0_terraced_skin','amphitheater_terraced_v0'],
    ['park_concert_timber_lawn_v2','concert_pavilion_lawn','concert_pavilion_lawn_v2','concert_pavilion_lawn_v2_timber_skin','concert_timber_lawn_v2'],
    ['park_night_market_hawker_v0','night_market','night_market_v0','night_market_v0_hawker_skin','night_market_hawker_v0'],
    ['park_parade_national_mall_v3','parade_ground','parade_ground_v3','parade_ground_v3_national_mall_skin','parade_national_mall_v3'],
    ['park_canal_ecological_wetland_v3','canal_waterway','canal_waterway_v3','canal_waterway_v3_ecological_skin','canal_ecological_wetland_v3'],
    ['park_custom_biophilic_urban_v1','custom_parks_plazas','custom_parks_plazas_v1','custom_parks_plazas_v1_biophilic_skin','custom_biophilic_urban_v1'],
  ] as const)('executes the exact reviewed Batch 12 selection %s', (familyId,archetypeId,variantId,appearanceKitId,plantingStructure) => {
    const candidate=zone({public_realm_lego:trustedRecipe({family_id:familyId,family_version:1,archetype_id:archetypeId,variant_id:variantId,appearance_kit_id:appearanceKitId,planting_structure:plantingStructure})});
    expect(resolveParkLegoContract(candidate)).toMatchObject({familyId,archetypeId,variantId,supported:true});
    expect(isExecutableParkLegoFamily(candidate)).toBe(true); expect(usesArchetypeOwnedParkSurface(candidate)).toBe(true);
  });

  it.each([
    [0, 'Village Green', 'english_pastoral', 'thatched'],
    [1, 'Municipal Oval', 'modern_minimal', 'steel_canopy'],
    [2, 'South Asian Ground', 'urban_pavers', 'fabric_sail'],
    [3, 'Caribbean Beach Pitch', 'tropical_lush', 'thatched'],
  ] as const)('gives cricket variant %s archetype-bound perimeter dressing', (
    index,
    label,
    materialPattern,
    shadeStyle,
  ) => {
    const candidate = zone({
      green_space_archetype_id: 'cricket_pitch_oval',
      green_space_selected_variant_id: `cricket_pitch_oval_v${index}`,
    });
    expect(resolveParkLegoContract(candidate)).toMatchObject({
      familyId: 'park_cricket_village_green_v0',
      variantId: `cricket_pitch_oval_v${index}`,
      supported: index === 0,
    });
    expect(resolveParkLegoAppearance(candidate)).toBeNull();
    expect(resolveParkDressingAppearance(candidate)).toMatchObject({
      label,
      materialPattern,
      shadeStyle,
      variantIndex: index,
    });
  });

  it('prefers and validates the canonical nested compiler contract', () => {
    const candidate = zone({
      green_space_archetype_id: 'community_park',
      green_space_selected_variant_id: 'community_park_v0',
      public_realm_lego: trustedRecipe({
        family_id: 'park_neighborhood_community',
        family_version: 1,
        archetype_id: 'community_park',
        variant_id: 'community_park_v0',
        planting_structure: 'naturalistic_grove',
        appearance_kit_id: 'english_pastoral_v1',
      }),
    });
    expect(resolveParkLegoContract(candidate)).toMatchObject({
      familyId: 'park_neighborhood_community',
      familyVersion: PARK_LEGO_FAMILY_VERSION,
      archetypeId: 'community_park',
      variantId: 'community_park_v0',
      plantingStructure: 'naturalistic_grove',
      source: 'public_realm_lego',
      supported: true,
    });
    expect(resolveParkLegoAppearance(candidate)).toMatchObject({
      label: 'English Pastoral',
      materialPattern: 'english_pastoral',
      shadeStyle: 'timber_pergola',
    });
  });

  it('normalizes legacy variant aliases without losing visual selection', () => {
    const candidate = zone({
      green_space_archetype_id: 'neighborhood_park',
      green_space_selected_variant_id: 'neighborhood_park_variant_2',
    });
    expect(resolveParkLegoContract(candidate)?.variantId).toBe('neighborhood_park_v2');
    expect(resolveParkLegoAppearance(candidate)).toMatchObject({
      familyId: 'park_neighborhood_community',
      variantIndex: 2,
      label: 'Natural Meadow',
      plantingStructure: 'naturalistic_grove',
      materialPattern: 'native_meadow',
    });
  });

  it('compiles a courtyard role to the approved pocket-park family', () => {
    const candidate = {
      zone_type: 'development_area' as const,
      properties: { _plan_role: 'courtyard' },
    };
    expect(resolveParkLegoContract(candidate)).toMatchObject({
      familyId: 'park_pocket_courtyard',
      archetypeId: 'urban_pocket_park',
      variantId: 'urban_pocket_park_v0',
    });
    expect(isExecutableParkLegoFamily(candidate)).toBe(true);
  });

  it('does not execute an unknown future family version', () => {
    const candidate = zone({
      public_realm_lego: trustedRecipe({
        family_id: 'park_pocket_courtyard',
        family_version: 2,
        archetype_id: 'urban_pocket_park',
        variant_id: 'urban_pocket_park_v1',
        planting_structure: 'formal_quad',
        appearance_kit_id: 'modern_steel_turf_v1',
      }),
    });
    expect(resolveParkLegoContract(candidate)?.supported).toBe(false);
    expect(resolveParkLegoAppearance(candidate)).toBeNull();
    expect(isExecutableParkLegoFamily(candidate)).toBe(false);
  });

  it('rejects rather than repairing an incompatible nested selection', () => {
    const candidate = zone({
      public_realm_lego: trustedRecipe({
        family_id: 'park_neighborhood_community',
        family_version: 1,
        archetype_id: 'neighborhood_park',
        variant_id: 'neighborhood_park_v0',
        planting_structure: 'formal_quad',
        appearance_kit_id: 'rustic_timber_gravel_v1',
      }),
    });
    expect(resolveParkLegoContract(candidate)).toMatchObject({
      archetypeId: 'neighborhood_park',
      variantId: 'neighborhood_park_v0',
      supported: false,
    });
    expect(resolveParkLegoAppearance(candidate)).toBeNull();
  });

  it.each([
    ['park_pocket_courtyard', 'urban_pocket_park', 'urban_pocket_park_v0', 'rustic_timber_gravel_v1', 'garden_courtyard'],
    ['park_neighborhood_community', 'neighborhood_park', 'neighborhood_park_v0', 'rustic_timber_gravel_v1', 'active_recreation'],
    ['park_civic_plaza', 'formal_civic_plaza', 'formal_civic_plaza_v0', 'neoclassical_stone_v1', 'paved_plaza'],
    ['park_linear_greenway', 'linear_park_greenway', 'linear_park_greenway_v0', 'rail_trail_v1', 'naturalistic_grove'],
    ['park_skate_archetype_v0', 'skate_park', 'skate_park_v0', 'skate_park_v0_reference_skin', 'skate_archetype_v0'],
    ['park_inclusive_playground_v0', 'inclusive_playground', 'inclusive_playground_v0', 'inclusive_playground_v0_reference_skin', 'inclusive_playground_v0'],
    ['park_dog_archetype_v0', 'dog_park', 'dog_park_v0', 'dog_park_v0_reference_skin', 'dog_park_v0'],
    ['park_splash_pad_v0', 'splash_pad_area', 'splash_pad_area_v0', 'splash_pad_area_v0_reference_skin', 'splash_pad_area_v0'],
    ['park_community_garden_v0', 'community_garden', 'community_garden_v0', 'community_garden_v0_reference_skin', 'community_garden_v0'],
    ['park_basketball_court_v0', 'basketball_court', 'basketball_court_v0', 'basketball_court_v0_classic_asphalt_skin', 'basketball_classic_v0'],
    ['park_basketball_court_v0', 'basketball_court', 'basketball_court_v1', 'basketball_court_v1_pro_acrylic_skin', 'basketball_pro_v1'],
    ['park_basketball_court_v0', 'basketball_court', 'basketball_court_v2', 'basketball_court_v2_half_court_mural_skin', 'basketball_half_court_v2'],
    ['park_basketball_court_v0', 'basketball_court', 'basketball_court_v3', 'basketball_court_v3_streetball_skin', 'basketball_streetball_v3'],
    ['park_tennis_cluster_v0', 'tennis_court_cluster', 'tennis_court_cluster_v0', 'tennis_court_cluster_v0_reference_skin', 'tennis_court_cluster_v0'],
    ['park_caged_soccer_v0', 'soccer_pitch_caged', 'soccer_pitch_caged_v0', 'soccer_pitch_caged_v0_reference_skin', 'caged_soccer_v0'],
    ['park_athletics_fields_v0', 'athletics_precinct_sports_fields', 'athletics_precinct_sports_fields_variant_0', 'athletics_precinct_sports_fields_v0_reference_skin', 'athletics_fields_v0'],
    ['park_nature_play_v0', 'nature_play_area', 'nature_play_area_v0', 'nature_play_area_v0_reference_skin', 'nature_play_area_v0'],
    ['park_pump_track_v0', 'pump_track', 'pump_track_v0', 'pump_track_v0_reference_skin', 'pump_track_v0'],
    ['park_outdoor_fitness_v0', 'outdoor_fitness_circuit', 'outdoor_fitness_circuit_v0', 'outdoor_fitness_circuit_v0_reference_skin', 'outdoor_fitness_circuit_v0'],
    ['park_memorial_garden_v0', 'memorial_garden', 'memorial_garden_v0', 'memorial_garden_v0_reference_skin', 'memorial_garden_v0'],
    ['park_water_ecology', 'stormwater_retention_pond', 'stormwater_retention_pond_v0', 'naturalistic_pond_v1', 'reservoir_perimeter'],
  ])('recognizes exact backend family mapping %s', (
    familyId,
    archetypeId,
    variantId,
    appearanceKitId,
    plantingStructure,
  ) => {
    const candidate = zone({
      public_realm_lego: trustedRecipe({
        family_id: familyId,
        family_version: 1,
        archetype_id: archetypeId,
        variant_id: variantId,
        appearance_kit_id: appearanceKitId,
        planting_structure: plantingStructure,
      }),
    });
    expect(resolveParkLegoContract(candidate)).toMatchObject({
      familyId,
      archetypeId,
      variantId,
      appearanceKitId,
      plantingStructure,
      supported: true,
      source: 'public_realm_lego',
    });
    expect(isExecutableParkLegoFamily(candidate)).toBe(true);
  });

  it('does not coerce a civic family carrying a neighborhood archetype', () => {
    const candidate = zone({
      public_realm_lego: trustedRecipe({
        family_id: 'park_civic_plaza',
        family_version: 1,
        archetype_id: 'neighborhood_park',
        variant_id: 'neighborhood_park_v0',
        appearance_kit_id: 'rustic_timber_gravel_v1',
        planting_structure: 'active_recreation',
      }),
    });
    expect(resolveParkLegoContract(candidate)).toMatchObject({
      familyId: 'park_civic_plaza',
      archetypeId: 'neighborhood_park',
      supported: false,
    });
    expect(resolveParkLegoAppearance(candidate)).toBeNull();
  });

  it.each([
    ['park_basketball_court_v0', 'basketball_court', 'basketball_court_v0', 'basketball_court_v0_classic_asphalt_skin', 'basketball_classic_v0'],
    ['park_basketball_court_v0', 'basketball_court', 'basketball_court_v1', 'basketball_court_v1_pro_acrylic_skin', 'basketball_pro_v1'],
    ['park_basketball_court_v0', 'basketball_court', 'basketball_court_v2', 'basketball_court_v2_half_court_mural_skin', 'basketball_half_court_v2'],
    ['park_basketball_court_v0', 'basketball_court', 'basketball_court_v3', 'basketball_court_v3_streetball_skin', 'basketball_streetball_v3'],
    ['park_caged_soccer_v0', 'soccer_pitch_caged', 'soccer_pitch_caged_v0', 'soccer_pitch_caged_v0_reference_skin', 'caged_soccer_v0'],
    ['park_athletics_fields_v0', 'athletics_precinct_sports_fields', 'athletics_precinct_sports_fields_variant_0', 'athletics_precinct_sports_fields_v0_reference_skin', 'athletics_fields_v0'],
  ])('treats regulation family %s as an archetype-owned no-drape surface', (
    familyId, archetypeId, variantId, appearanceKitId, plantingStructure,
  ) => {
    const candidate = zone({
      public_realm_lego: trustedRecipe({
        family_id: familyId,
        family_version: 1,
        archetype_id: archetypeId,
        variant_id: variantId,
        appearance_kit_id: appearanceKitId,
        planting_structure: plantingStructure,
      }),
    });
    expect(usesArchetypeOwnedParkSurface(candidate)).toBe(true);
  });

  it('keeps Skate Park v0 on its archetype-owned surface in legacy and compiled states', () => {
    const legacy = zone({
      green_space_archetype_id: 'skate_park',
      green_space_selected_variant_id: 'skate_park_v0',
    });
    expect(resolveParkLegoContract(legacy)).toMatchObject({
      familyId: 'park_skate_archetype_v0',
      variantId: 'skate_park_v0',
      supported: true,
    });
    expect(resolveParkLegoAppearance(legacy)).toBeNull();
    expect(usesArchetypeOwnedParkSurface(legacy)).toBe(true);

    const compiled = zone({
      public_realm_lego: trustedRecipe({
        family_id: 'park_skate_archetype_v0',
        family_version: 1,
        archetype_id: 'skate_park',
        variant_id: 'skate_park_v0',
        appearance_kit_id: 'skate_park_v0_reference_skin',
        planting_structure: 'skate_archetype_v0',
      }),
    });
    expect(usesArchetypeOwnedParkSurface(compiled)).toBe(true);
  });

  it.each([
    ['community_park', 'community_park_v0', 'park_neighborhood_community'],
    ['pond_lake', 'pond_lake_v0', 'park_water_ecology'],
    ['wetland_rain_garden', 'wetland_rain_garden_v0', 'park_water_ecology'],
    ['japanese_garden', 'japanese_garden_v0', 'park_cultural_gardens'],
    ['botanical_garden', 'botanical_garden_v0', 'park_cultural_gardens'],
    ['urban_forest', 'urban_forest_v0', 'park_urban_forest'],
    ['reservoir_watershed_park', 'reservoir_watershed_park_v0', 'park_water_ecology'],
    ['amphitheater_lawn', 'amphitheater_lawn_v0', 'park_amphitheater_lawn_v0'],
    ['riparian_buffer', 'riparian_buffer_v0', 'park_water_ecology'],
    ['playground_adventure', 'playground_adventure_v0', 'park_playground_adventure_v0'],
  ] as const)('compiles batch-4 %s/%s to an owned zero-call surface', (
    archetypeId, variantId, familyId,
  ) => {
    const candidate = zone({
      green_space_archetype_id: archetypeId,
      green_space_selected_variant_id: variantId,
    });
    expect(resolveParkLegoContract(candidate)).toMatchObject({
      familyId,
      archetypeId,
      variantId,
      supported: true,
    });
    expect(usesArchetypeOwnedParkSurface(candidate)).toBe(true);
  });

  it.each([
    ['disc_golf_course', 'park_disc_golf_wooded_v0'],
    ['bocce_petanque_court', 'park_bocce_piazza_v0'],
    ['climbing_bouldering_wall', 'park_climbing_competition_v0'],
    ['mini_golf_course', 'park_mini_golf_classic_v0'],
    ['beach_volleyball_courts', 'park_beach_volleyball_competition_v0'],
    ['pollinator_meadow', 'park_pollinator_prairie_v0'],
    ['urban_orchard_food_forest', 'park_orchard_heritage_v0'],
    ['bioswale_rain_garden', 'park_bioswale_streetside_v0'],
    ['sculpture_garden', 'park_sculpture_museum_court_v0'],
    ['labyrinth_meditation', 'park_labyrinth_classical_v0'],
  ] as const)('compiles batch-5 %s v0 to exact zero-call family %s', (archetypeId, familyId) => {
    const variantId = `${archetypeId}_v0`;
    const candidate = zone({
      green_space_archetype_id: archetypeId,
      green_space_selected_variant_id: variantId,
    });
    expect(resolveParkLegoContract(candidate)).toMatchObject({
      familyId, archetypeId, variantId, supported: true,
    });
    expect(usesArchetypeOwnedParkSurface(candidate)).toBe(true);
  });

  it('does not borrow the v0 labyrinth program or skin for an unreviewed variant', () => {
    const candidate = zone({
      green_space_archetype_id: 'labyrinth_meditation',
      green_space_selected_variant_id: 'labyrinth_meditation_v1',
    });
    expect(resolveParkLegoContract(candidate)).toMatchObject({
      familyId: 'park_labyrinth_classical_v0',
      variantId: 'labyrinth_meditation_v1',
      supported: false,
    });
    expect(usesArchetypeOwnedParkSurface(candidate)).toBe(false);
  });

  it.each([
    ['outdoor_ice_rink', 'outdoor_ice_rink_v3', 'park_ice_rink_multipurpose_v3'],
    ['kayak_launch_dock', 'kayak_launch_dock_v0', 'park_kayak_river_launch_v0'],
    ['tidal_marsh_boardwalk', 'tidal_marsh_boardwalk_v0', 'park_tidal_marsh_cordgrass_v0'],
    ['outdoor_cinema_lawn', 'outdoor_cinema_lawn_v1', 'park_cinema_lawn_projection_v1'],
    ['food_truck_plaza', 'food_truck_plaza_v1', 'park_food_truck_permanent_v1'],
    ['festival_event_lawn', 'festival_event_lawn_v2', 'park_great_lawn_v2'],
    ['campus_central_quad', 'campus_central_quad_variant_0', 'park_campus_meadow_quad_v0'],
    ['urban_beach', 'urban_beach_v2', 'park_urban_beach_family_v2'],
    ['velodrome_cycling_track', 'velodrome_cycling_track_variant_0', 'park_velodrome_open_air_v0'],
    ['mountain_bike_park', 'mountain_bike_park_variant_2', 'park_mtb_skills_dirt_v2'],
  ] as const)('compiles batch-6 %s/%s to exact zero-call family %s', (
    archetypeId, variantId, familyId,
  ) => {
    const candidate = zone({
      green_space_archetype_id: archetypeId,
      green_space_selected_variant_id: variantId,
    });
    expect(resolveParkLegoContract(candidate)).toMatchObject({
      familyId, archetypeId, variantId, supported: true,
    });
    expect(usesArchetypeOwnedParkSurface(candidate)).toBe(true);
  });

  it.each([
    ['regional_park', 'regional_park_v0', 'park_regional_english_landscape_v0'],
    ['beer_garden', 'beer_garden_v0', 'park_beer_garden_munich_v0'],
    ['sunken_plaza', 'sunken_plaza_v0', 'park_sunken_courtyard_v0'],
    ['stepped_terraced_plaza', 'stepped_terraced_plaza_v3', 'park_terraced_cascade_v3'],
    ['market_square', 'market_square_v1', 'park_market_festival_lawn_v1'],
    ['promenade_boardwalk', 'promenade_boardwalk_v0', 'park_boardwalk_maritime_v0'],
    ['fountain_water_feature', 'fountain_water_feature_v1', 'park_fountain_formal_pool_v1'],
    ['swimming_pool_complex', 'swimming_pool_complex_v0', 'park_natural_swimming_pond_v0'],
    ['nature_preserve', 'nature_preserve_v1', 'park_nature_preserve_prairie_v1'],
    ['riverfront_park_beach', 'riverfront_park_beach_v1', 'park_riverfront_lake_beach_v1'],
  ] as const)('compiles batch-7 %s/%s to exact zero-call family %s', (
    archetypeId, variantId, familyId,
  ) => {
    const candidate = zone({
      green_space_archetype_id: archetypeId,
      green_space_selected_variant_id: variantId,
    });
    expect(resolveParkLegoContract(candidate)).toMatchObject({
      familyId, archetypeId, variantId, supported: true,
    });
    expect(usesArchetypeOwnedParkSurface(candidate)).toBe(true);
  });

  it.each([
    ['regional_park', 'regional_park_v1'],
    ['beer_garden', 'beer_garden_v2'],
    ['stepped_terraced_plaza', 'stepped_terraced_plaza_v2'],
    ['market_square', 'market_square_v0'],
    ['nature_preserve', 'nature_preserve_v0'],
    ['riverfront_park_beach', 'riverfront_park_beach_v0'],
  ] as const)('fails closed for unreviewed batch-7 selection %s/%s', (archetypeId, variantId) => {
    const candidate = zone({
      green_space_archetype_id: archetypeId,
      green_space_selected_variant_id: variantId,
    });
    expect(resolveParkLegoContract(candidate)?.supported).toBe(false);
    expect(usesArchetypeOwnedParkSurface(candidate)).toBe(false);
  });

  it.each([
    ['outdoor_ice_rink', 'outdoor_ice_rink_v2'],
    ['outdoor_cinema_lawn', 'outdoor_cinema_lawn_v0'],
    ['campus_central_quad', 'campus_central_quad_variant_1'],
    ['velodrome_cycling_track', 'velodrome_cycling_track_variant_1'],
    ['mountain_bike_park', 'mountain_bike_park_variant_1'],
  ] as const)('fails closed for unreviewed batch-6 selection %s/%s', (archetypeId, variantId) => {
    const candidate = zone({
      green_space_archetype_id: archetypeId,
      green_space_selected_variant_id: variantId,
    });
    expect(resolveParkLegoContract(candidate)?.supported).toBe(false);
    expect(usesArchetypeOwnedParkSurface(candidate)).toBe(false);
  });

  it.each([
    ['inclusive_playground', 'inclusive_playground_v0'],
    ['dog_park', 'dog_park_v0'],
    ['splash_pad_area', 'splash_pad_area_v0'],
    ['community_garden', 'community_garden_v0'],
  ])('keeps %s/%s on its exact surface without a drape', (archetypeId, variantId) => {
    expect(usesArchetypeOwnedParkSurface(zone({
      green_space_archetype_id: archetypeId,
      green_space_selected_variant_id: variantId,
    }))).toBe(true);
  });

  it('does not normalize nested compiler identities or fall back to legacy fields', () => {
    const candidate = zone({
      green_space_archetype_id: 'urban_pocket_park',
      public_realm_lego: trustedRecipe({
        family_id: 'park-pocket-courtyard',
        family_version: 1,
        archetype_id: 'urban_pocket_park',
        variant_id: 'urban_pocket_park_v0',
        appearance_kit_id: 'rustic_timber_gravel_v1',
        planting_structure: 'garden_courtyard',
      }),
    });
    expect(resolveParkLegoContract(candidate)).toBeNull();
    expect(resolveParkLegoAppearance(candidate)).toBeNull();
    expect(isExecutableParkLegoFamily(candidate)).toBe(false);
  });

  it.each([
    ['schema version', { schema_version: '1' }],
    ['family version', { family_version: '1' }],
    ['kind', { kind: 'Park' }],
    ['generator', { generator: 'park-kit' }],
    ['catalog fingerprint', { catalog_fingerprint: 'A'.repeat(64) }],
    ['capability fingerprint', { capability_fingerprint: 'short' }],
    ['recipe hash', { recipe_hash: `${'d'.repeat(63)}g` }],
  ])('rejects a nested recipe with an untrusted %s', (_label, override) => {
    const candidate = zone({
      public_realm_lego: trustedRecipe({
        family_id: 'park_pocket_courtyard',
        family_version: 1,
        archetype_id: 'urban_pocket_park',
        variant_id: 'urban_pocket_park_v0',
        appearance_kit_id: 'rustic_timber_gravel_v1',
        planting_structure: 'garden_courtyard',
        ...override,
      }),
    });
    expect(resolveParkLegoContract(candidate)?.supported).toBe(false);
    expect(isExecutableParkLegoFamily(candidate)).toBe(false);
  });

  it('gives every visual variant a materially distinct palette or pattern', () => {
    const appearances = Array.from({ length: 4 }, (_, index) => resolveParkLegoAppearance(zone({
      green_space_archetype_id: 'urban_pocket_park',
      green_space_selected_variant_id: `urban_pocket_park_v${index}`,
    }))!);
    expect(new Set(appearances.map((entry) => entry.materialPattern)).size).toBe(4);
    expect(new Set(appearances.map((entry) => entry.palette.path)).size).toBe(4);
    expect(new Set(appearances.map((entry) => entry.palette.benchSeat)).size).toBe(4);
  });

  it('locks playground, shade and pavilion modules to real metre dimensions', () => {
    expect(PARK_PROGRAM_MODULE_SPEC.playground.safetyDiameterM).toBe(12);
    expect(PARK_PROGRAM_MODULE_SPEC.playground.towerHeightM).toBe(3.2);
    expect(PARK_PROGRAM_MODULE_SPEC.playground.slideLengthM).toBe(3.4);
    expect(PARK_PROGRAM_MODULE_SPEC.shade).toEqual({
      spanM: 7.2,
      lowEdgeHeightM: 3,
      highEdgeHeightM: 3.7,
    });
    expect(PARK_PROGRAM_MODULE_SPEC.pavilion).toEqual({
      widthM: 6,
      depthM: 5,
      clearHeightM: 2.8,
      roofHeightM: 1.15,
    });
  });

  it('shares exact program anchors with the neighborhood ground profile', () => {
    const candidate = zone({ green_space_archetype_id: 'neighborhood_park' });
    expect(resolveParkProgramAnchorLayout(candidate))
      .toBe(NEIGHBORHOOD_COMMUNITY_PROGRAM_ANCHORS);
    expect(resolveParkProgramAnchorLayout(zone({ green_space_archetype_id: 'urban_pocket_park' })))
      .toBeUndefined();
  });
});
