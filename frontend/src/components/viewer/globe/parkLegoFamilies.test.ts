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
    ['park_rooftop_intensive_garden_v0','rooftop_garden','rooftop_garden_v0','rooftop_garden_v0_intensive_skin','rooftop_intensive_garden_v0'],
    ['park_community_healing_garden_v2','community_garden_enhanced','garden_healing','community_garden_enhanced_healing_skin','community_healing_garden_v2'],
    ['park_greenbelt_rail_trail_v1','greenbelt_buffer_park','greenbelt_buffer_park_v1','greenbelt_buffer_park_v1_rail_trail_skin','greenbelt_rail_trail_v1'],
    ['park_foothill_heathland_trail_v2','foothill_trail_park','foothill_trail_park_v2','foothill_trail_park_v2_heathland_skin','foothill_heathland_trail_v2'],
    ['park_marina_pacific_dock_v2','marina_yacht_harbor','marina_yacht_harbor_v2','marina_yacht_harbor_v2_pacific_skin','marina_pacific_dock_v2'],
    ['park_working_pier_brooklyn_park_v3','working_pier_wharf_conversion','working_pier_wharf_conversion_v3','working_pier_wharf_conversion_v3_park_skin','working_pier_brooklyn_park_v3'],
    ['park_floating_meadow_loop_v2','floating_park_pool','floating_park_pool_v2','floating_park_pool_v2_meadow_skin','floating_meadow_loop_v2'],
    ['park_lighthouse_pacific_headland_v2','lighthouse_point_park','lighthouse_point_park_v2','lighthouse_point_park_v2_pacific_skin','lighthouse_pacific_headland_v2'],
    ['park_lake_edge_timber_deck_v2','lake_edge_plaza','lake_edge_plaza_v2','lake_edge_plaza_v2_timber_skin','lake_edge_timber_deck_v2'],
    ['park_stormwater_natural_creek_v0','stormwater_naturalized_drainage_corridor','stormwater_naturalized_drainage_corridor_variant_0','stormwater_naturalized_drainage_corridor_v0_creek_skin','stormwater_natural_creek_v0'],
  ] as const)('executes the exact reviewed Batch 13 selection %s',(familyId,archetypeId,variantId,appearanceKitId,plantingStructure)=>{const candidate=zone({public_realm_lego:trustedRecipe({family_id:familyId,family_version:1,archetype_id:archetypeId,variant_id:variantId,appearance_kit_id:appearanceKitId,planting_structure:plantingStructure})});expect(resolveParkLegoContract(candidate)).toMatchObject({familyId,archetypeId,variantId,supported:true});expect(isExecutableParkLegoFamily(candidate)).toBe(true);expect(usesArchetypeOwnedParkSurface(candidate)).toBe(true)});

  it.each([
    ['park_surface_parking_standard_v0','surface_parking_lot','surface_parking_lot_v0','surface_parking_lot_v0_standard_skin','surface_parking_standard_v0'],
    ['park_structured_parking_urban_v2','structured_parking_garage','structured_parking_garage_v2','structured_parking_garage_v2_urban_skin','structured_parking_urban_v2'],
    ['park_underground_parking_green_v1','underground_parking_entry','underground_parking_entry_v1','underground_parking_entry_v1_green_skin','underground_parking_green_v1'],
    ['park_green_parking_infrastructure_v1','green_parking_lot','green_parking_lot_v1','green_parking_lot_v1_infrastructure_skin','green_parking_infrastructure_v1'],
    ['park_airport_general_aviation_v2','airport_airfield','airport_airfield_variant_2','airport_airfield_v2_general_aviation_skin','airport_general_aviation_v2'],
    ['park_equestrian_working_stable_v1','equestrian_center','equestrian_center_variant_1','equestrian_center_v1_working_stable_skin','equestrian_working_stable_v1'],
    ['park_golf_seaside_links_v0','golf_course_18_hole','golf_course_18_hole_variant_0','golf_course_18_hole_v0_links_skin','golf_seaside_links_v0'],
    ['park_driving_range_single_tier_v0','golf_driving_range','golf_driving_range_variant_0','golf_driving_range_v0_single_tier_skin','driving_range_single_tier_v0'],
    ['park_multi_sport_track_field_v3','multi_sport_complex','multi_sport_complex_variant_3','multi_sport_complex_v3_track_field_skin','multi_sport_track_field_v3'],
    ['park_retail_parking_landscaped_v1','suburban_retail_parking_lot','suburban_retail_parking_lot_v1','suburban_retail_parking_lot_v1_landscaped_skin','retail_parking_landscaped_v1'],
  ] as const)('executes the exact reviewed Batch 14 selection %s',(familyId,archetypeId,variantId,appearanceKitId,plantingStructure)=>{const candidate=zone({public_realm_lego:trustedRecipe({family_id:familyId,family_version:1,archetype_id:archetypeId,variant_id:variantId,appearance_kit_id:appearanceKitId,planting_structure:plantingStructure})});expect(resolveParkLegoContract(candidate)).toMatchObject({familyId,archetypeId,variantId,supported:true});expect(isExecutableParkLegoFamily(candidate)).toBe(true);expect(usesArchetypeOwnedParkSurface(candidate)).toBe(true)});

  it('preserves an explicitly registered non-numeric catalogue variant in the legacy path',()=>{const candidate=zone({green_space_archetype_id:'community_garden_enhanced',green_space_selected_variant_id:'garden_healing'});expect(resolveParkLegoContract(candidate)).toMatchObject({familyId:'park_community_healing_garden_v2',variantId:'garden_healing',supported:true});expect(usesArchetypeOwnedParkSurface(candidate)).toBe(true)});

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
      supported: true,
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

  it.each([
    ['park_pickleball_community_v1', 'pickleball_courts', 'pickleball_courts_v3', 'pickleball_courts_v3_indoor_outdoor_skin', 'pickleball_hybrid_v3'],
    ['park_caged_soccer_v0', 'soccer_pitch_caged', 'soccer_pitch_caged_v2', 'soccer_pitch_caged_v2_youth_training_skin', 'caged_soccer_youth_v2'],
    ['park_track_oval_school_v2', 'running_track_oval', 'running_track_oval_v3', 'running_track_oval_v3_park_loop_skin', 'track_park_loop_v3'],
    ['park_outdoor_fitness_v0', 'outdoor_fitness_circuit', 'outdoor_fitness_circuit_v3', 'outdoor_fitness_circuit_v3_senior_wellness_skin', 'fitness_senior_v3'],
    ['park_baseball_club_hub_v1', 'baseball_softball_diamond', 'baseball_softball_diamond_v0', 'baseball_softball_diamond_v0_classic_skin', 'baseball_classic_v0'],
    ['park_cricket_village_green_v0', 'cricket_pitch_oval', 'cricket_pitch_oval_v2', 'cricket_pitch_oval_v2_south_asian_skin', 'cricket_south_asian_v2'],
    ['park_nature_play_v0', 'nature_play_area', 'nature_play_area_v2', 'nature_play_area_v2_mud_water_skin', 'nature_play_mud_water_v2'],
    ['park_inclusive_playground_v0', 'inclusive_playground', 'inclusive_playground_v1', 'inclusive_playground_v1_sensory_skin', 'inclusive_sensory_v1'],
    ['park_pump_track_v0', 'pump_track', 'pump_track_v3', 'pump_track_v3_modular_skin', 'pump_track_modular_v3'],
    ['park_splash_pad_v0', 'splash_pad_area', 'splash_pad_area_v2', 'splash_pad_area_v2_meadow_skin', 'splash_pad_meadow_v2'],
  ] as const)('executes the explicit Batch 17 selection for %s', (
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
    expect(resolveParkLegoContract(candidate)).toMatchObject({
      familyId, archetypeId, variantId, supported: true,
    });
    expect(isExecutableParkLegoFamily(candidate)).toBe(true);
    expect(usesArchetypeOwnedParkSurface(candidate)).toBe(true);
  });

  it.each([
    ['park_disc_golf_wooded_v0', 'disc_golf_course', 'disc_golf_course_v2', 'disc_golf_course_v2_hillside_terrain_skin', 'disc_golf_hillside_v2'],
    ['park_bocce_piazza_v0', 'bocce_petanque_court', 'bocce_petanque_court_v3', 'bocce_petanque_court_v3_community_senior_skin', 'bocce_community_senior_v3'],
    ['park_climbing_competition_v0', 'climbing_bouldering_wall', 'climbing_bouldering_wall_v1', 'climbing_bouldering_wall_v1_natural_rock_skin', 'climbing_natural_rock_v1'],
    ['park_mini_golf_classic_v0', 'mini_golf_course', 'mini_golf_course_v2', 'mini_golf_course_v2_urban_art_skin', 'mini_golf_urban_art_v2'],
    ['park_beach_volleyball_competition_v0', 'beach_volleyball_courts', 'beach_volleyball_courts_v1', 'beach_volleyball_courts_v1_beachside_skin', 'beach_volleyball_beachside_v1'],
    ['park_pollinator_prairie_v0', 'pollinator_meadow', 'pollinator_meadow_v3', 'pollinator_meadow_v3_formal_border_skin', 'pollinator_formal_border_v3'],
    ['park_orchard_heritage_v0', 'urban_orchard_food_forest', 'urban_orchard_food_forest_v2', 'urban_orchard_food_forest_v2_pick_your_own_skin', 'orchard_pick_your_own_v2'],
    ['park_bioswale_streetside_v0', 'bioswale_rain_garden', 'bioswale_rain_garden_v1', 'bioswale_rain_garden_v1_park_rain_garden_skin', 'bioswale_park_rain_garden_v1'],
    ['park_sculpture_museum_court_v0', 'sculpture_garden', 'sculpture_garden_v2', 'sculpture_garden_v2_interactive_kinetic_skin', 'sculpture_kinetic_v2'],
    ['park_labyrinth_classical_v0', 'labyrinth_meditation', 'labyrinth_meditation_v3', 'labyrinth_meditation_v3_modern_mindfulness_skin', 'labyrinth_modern_v3'],
  ] as const)('executes the explicit Batch 18 selection for %s', (
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
    expect(resolveParkLegoContract(candidate)).toMatchObject({
      familyId, archetypeId, variantId, supported: true,
    });
    expect(isExecutableParkLegoFamily(candidate)).toBe(true);
    expect(usesArchetypeOwnedParkSurface(candidate)).toBe(true);
  });

  it.each([
    ['park_ice_rink_multipurpose_v3', 'outdoor_ice_rink', 'outdoor_ice_rink_v0', 'outdoor_ice_rink_v0_holiday_market_skin', 'ice_rink_holiday_market_v0'],
    ['park_kayak_river_launch_v0', 'kayak_launch_dock', 'kayak_launch_dock_v3', 'kayak_launch_dock_v3_community_boathouse_skin', 'kayak_community_boathouse_v3'],
    ['park_tidal_marsh_cordgrass_v0', 'tidal_marsh_boardwalk', 'tidal_marsh_boardwalk_v2', 'tidal_marsh_boardwalk_v2_reedbed_skin', 'tidal_marsh_reedbed_v2'],
    ['park_cinema_lawn_projection_v1', 'outdoor_cinema_lawn', 'outdoor_cinema_lawn_v0', 'outdoor_cinema_lawn_v0_popup_festival_skin', 'cinema_popup_festival_v0'],
    ['park_food_truck_permanent_v1', 'food_truck_plaza', 'food_truck_plaza_v3', 'food_truck_plaza_v3_night_market_skin', 'food_truck_night_market_v3'],
    ['park_great_lawn_v2', 'festival_event_lawn', 'festival_event_lawn_v1', 'festival_event_lawn_v1_farmers_market_skin', 'festival_farmers_market_v1'],
    ['park_campus_meadow_quad_v0', 'campus_central_quad', 'campus_central_quad_variant_3', 'campus_central_quad_v3_formal_collegiate_skin', 'campus_formal_collegiate_v3'],
    ['park_urban_beach_family_v2', 'urban_beach', 'urban_beach_v0', 'urban_beach_v0_paris_plages_skin', 'urban_beach_paris_v0'],
    ['park_velodrome_open_air_v0', 'velodrome_cycling_track', 'velodrome_cycling_track_variant_2', 'velodrome_cycling_track_v2_parkland_skin', 'velodrome_parkland_v2'],
    ['park_mtb_skills_dirt_v2', 'mountain_bike_park', 'mountain_bike_park_variant_1', 'mountain_bike_park_v1_hillside_skin', 'mtb_hillside_v1'],
  ] as const)('executes the explicit Batch 19 selection for %s', (
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
    expect(resolveParkLegoContract(candidate)).toMatchObject({
      familyId, archetypeId, variantId, supported: true,
    });
    expect(isExecutableParkLegoFamily(candidate)).toBe(true);
    expect(usesArchetypeOwnedParkSurface(candidate)).toBe(true);
  });

  it.each([
    ['park_water_ecology', 'riparian_buffer', 'riparian_buffer_v2', 'riparian_buffer_v2_rewilded_urban_skin', 'riparian_rewilded_v2'],
    ['park_water_ecology', 'wetland_rain_garden', 'wetland_rain_garden_v3', 'wetland_rain_garden_v3_resilient_coastal_skin', 'wetland_coastal_v3'],
    ['park_playground_adventure_v0', 'playground_adventure', 'playground_adventure_v1', 'playground_adventure_v1_modern_steel_skin', 'playground_modern_steel_v1'],
    ['park_amphitheater_lawn_v0', 'amphitheater_lawn', 'amphitheater_lawn_v2', 'amphitheater_lawn_v2_intimate_garden_skin', 'amphitheater_intimate_garden_v2'],
    ['park_beer_garden_munich_v0', 'beer_garden', 'beer_garden_v3', 'beer_garden_v3_rooftop_skin', 'beer_garden_rooftop_v3'],
    ['park_city_hall_modernist_fountain_v2', 'city_hall_government_plaza', 'city_hall_government_plaza_v1', 'city_hall_government_plaza_v1_historic_skin', 'city_hall_historic_v1'],
    ['park_sunken_courtyard_v0', 'sunken_plaza', 'sunken_plaza_v1', 'sunken_plaza_v1_rockefeller_rink_skin', 'sunken_rockefeller_v1'],
    ['park_cathedral_courtyard_fountain_v3', 'cathedral_religious_forecourt', 'cathedral_religious_forecourt_v0', 'cathedral_religious_forecourt_v0_asian_temple_skin', 'cathedral_asian_temple_v0'],
    ['park_cultural_museum_terrace_v0', 'cultural_institution_forecourt', 'cultural_institution_forecourt_v3', 'cultural_institution_forecourt_v3_arena_concourse_skin', 'cultural_arena_concourse_v3'],
    ['park_terraced_cascade_v3', 'stepped_terraced_plaza', 'stepped_terraced_plaza_v1', 'stepped_terraced_plaza_v1_spanish_steps_skin', 'terraced_spanish_v1'],
  ] as const)('executes the explicit Batch 20 selection for %s', (
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
    expect(resolveParkLegoContract(candidate)).toMatchObject({
      familyId, archetypeId, variantId, supported: true,
    });
    expect(isExecutableParkLegoFamily(candidate)).toBe(true);
    expect(usesArchetypeOwnedParkSurface(candidate)).toBe(true);
  });

  it.each([
    ['park_athletics_fields_v0', 'athletics_precinct_sports_fields', 'athletics_precinct_sports_fields_variant_2', 'athletics_precinct_sports_fields_v2_campus_precinct_skin', 'athletics_campus_v2'],
    ['park_community_garden_v0', 'community_garden', 'community_garden_v2', 'community_garden_v2_natural_meadow_skin', 'community_garden_meadow_v2'],
    ['park_fountain_formal_pool_v1', 'fountain_water_feature', 'fountain_water_feature_v3', 'fountain_water_feature_v3_ecological_wetland_skin', 'fountain_wetland_v3'],
    ['park_water_ecology', 'pond_lake', 'pond_lake_v1', 'pond_lake_v1_formal_reflecting_skin', 'pond_formal_v1'],
    ['park_market_festival_lawn_v1', 'market_square', 'market_square_v0', 'market_square_v0_terraced_performance_skin', 'market_terraced_v0'],
    ['park_civic_plaza', 'formal_civic_plaza', 'formal_civic_plaza_v2', 'formal_civic_plaza_v2_green_civic_skin', 'formal_civic_green_v2'],
    ['park_linear_greenway', 'linear_park_greenway', 'linear_park_greenway_v3', 'linear_park_greenway_v3_elevated_viaduct_skin', 'linear_elevated_viaduct_v3'],
    ['park_boardwalk_maritime_v0', 'promenade_boardwalk', 'promenade_boardwalk_v2', 'promenade_boardwalk_v2_tropical_resort_skin', 'boardwalk_tropical_v2'],
    ['park_natural_swimming_pond_v0', 'swimming_pool_complex', 'swimming_pool_complex_v2', 'swimming_pool_complex_v2_contemporary_interactive_skin', 'swimming_interactive_v2'],
    ['park_rooftop_intensive_garden_v0', 'rooftop_garden', 'rooftop_garden_v3', 'rooftop_garden_v3_social_terrace_skin', 'rooftop_social_v3'],
  ] as const)('executes the explicit Batch 21 selection for %s', (
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
    expect(resolveParkLegoContract(candidate)).toMatchObject({
      familyId, archetypeId, variantId, supported: true,
    });
    expect(isExecutableParkLegoFamily(candidate)).toBe(true);
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

  it('uses the reviewed zen-rock identity instead of borrowing the v0 labyrinth skin', () => {
    const candidate = zone({
      green_space_archetype_id: 'labyrinth_meditation',
      green_space_selected_variant_id: 'labyrinth_meditation_v1',
    });
    expect(resolveParkLegoContract(candidate)).toMatchObject({
      familyId: 'park_labyrinth_classical_v0',
      variantId: 'labyrinth_meditation_v1',
      supported: true,
    });
    expect(usesArchetypeOwnedParkSurface(candidate)).toBe(true);
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
    ['park_cemetery_classical_v0', 'cemetery_memorial_grounds', 'cemetery_memorial_grounds_v2', 'cemetery_memorial_grounds_v2_sculptural_skin', 'cemetery_sculptural_v2'],
    ['park_courtyard_linear_water_v1', 'courtyard_plaza', 'courtyard_plaza_v0', 'courtyard_plaza_v0_neoclassical_skin', 'courtyard_neoclassical_v0'],
    ['park_transit_green_civic_v2', 'transit_plaza', 'transit_plaza_v3', 'transit_plaza_v3_festival_market_skin', 'transit_festival_v3'],
    ['park_amphitheater_terraced_v0', 'amphitheater_performance_space', 'amphitheater_performance_space_v2', 'amphitheater_performance_space_v2_intimate_garden_skin', 'amphitheater_garden_v2'],
    ['park_water_ecology', 'stormwater_retention_pond', 'stormwater_retention_pond_v3', 'stormwater_retention_pond_v3_ecological_wetland_skin', 'stormwater_ecological_wetland_v3'],
    ['park_canal_ecological_wetland_v3', 'canal_waterway', 'canal_waterway_v1', 'canal_waterway_v1_formal_reflecting_skin', 'canal_formal_v1'],
    ['park_custom_biophilic_urban_v1', 'custom_parks_plazas', 'custom_parks_plazas_v2', 'custom_parks_plazas_v2_tech_smart_skin', 'custom_tech_smart_v2'],
    ['park_nature_preserve_prairie_v1', 'nature_preserve', 'nature_preserve_v3', 'nature_preserve_v3_old_growth_skin', 'nature_preserve_old_growth_v3'],
    ['park_riverfront_lake_beach_v1', 'riverfront_park_beach', 'riverfront_park_beach_v0', 'riverfront_park_beach_v0_urban_river_skin', 'riverfront_urban_beach_v0'],
    ['park_parklet_sf_timber_v1', 'street_plaza_parklet', 'street_plaza_parklet_v2', 'street_plaza_parklet_v2_tactical_skin', 'parklet_tactical_v2'],
  ] as const)('executes the explicit Batch 22 selection for %s', (
    familyId, archetypeId, variantId, appearanceKitId, plantingStructure,
  ) => {
    const candidate = zone({ public_realm_lego: trustedRecipe({
      family_id: familyId, family_version: 1, archetype_id: archetypeId,
      variant_id: variantId, appearance_kit_id: appearanceKitId,
      planting_structure: plantingStructure,
    }) });
    expect(resolveParkLegoContract(candidate)).toMatchObject({ familyId, archetypeId, variantId, supported: true });
    expect(usesArchetypeOwnedParkSurface(candidate)).toBe(true);
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
