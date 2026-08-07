from __future__ import annotations

import json

import pytest
from pyproj import CRS
from shapely.geometry import LineString, Point, box

from app.services.public_realm_lego import (
    ParkPolygonTarget,
    PublicRealmPlanRequest,
    PublicRealmPlanningError,
    StreetNodeTarget,
    StreetSegmentTarget,
    build_public_realm_capability_catalog,
    normalize_legacy_ai_street_variant_properties,
    plan_public_realm_recipe,
    plan_public_realm_zone_recipe,
    public_realm_recipe_hash,
    public_realm_recipe_identity,
    public_realm_representation_hash,
)
from app.services.site_engine import build_transformer, project_geometry


def _sha256(value: str) -> None:
    assert len(value) == 64
    int(value, 16)


def _street_request(
    archetype_id: str,
    row_width_m: float,
    *,
    variant_id: str | None = None,
    length_m: float = 100,
) -> PublicRealmPlanRequest:
    return PublicRealmPlanRequest(
        archetype_id=archetype_id,
        variant_id=variant_id,
        target=StreetSegmentTarget(
            row_width_m=row_width_m,
            length_m=length_m,
        ),
    )


def test_catalog_is_deterministic_filtered_and_fingerprinted():
    first = build_public_realm_capability_catalog()
    second = build_public_realm_capability_catalog()
    parks = build_public_realm_capability_catalog(kinds=["park"])
    local_only = build_public_realm_capability_catalog(family_ids=["street_local_public_realm"])

    assert first == second
    assert first.family_ids == tuple(sorted(first.family_ids))
    assert set(parks.family_ids) == {
        "park_civic_plaza",
        "park_linear_greenway",
        "park_neighborhood_community",
        "park_pocket_courtyard",
        "park_skate_archetype_v0",
        "park_inclusive_playground_v0",
        "park_dog_archetype_v0",
        "park_splash_pad_v0",
        "park_community_garden_v0",
        "park_basketball_court_v0",
        "park_tennis_cluster_v0",
        "park_caged_soccer_v0",
        "park_athletics_fields_v0",
        "park_nature_play_v0",
        "park_pump_track_v0",
        "park_outdoor_fitness_v0",
        "park_memorial_garden_v0",
        "park_pickleball_community_v1",
        "park_track_oval_school_v2",
        "park_baseball_club_hub_v1",
        "park_cricket_village_green_v0",
        "park_sports_complex_tournament_v0",
        "park_water_ecology",
        "park_cultural_gardens",
        "park_urban_forest",
        "park_amphitheater_lawn_v0",
        "park_playground_adventure_v0",
        "park_disc_golf_wooded_v0",
        "park_bocce_piazza_v0",
        "park_climbing_competition_v0",
        "park_mini_golf_classic_v0",
        "park_beach_volleyball_competition_v0",
        "park_pollinator_prairie_v0",
        "park_orchard_heritage_v0",
        "park_bioswale_streetside_v0",
        "park_sculpture_museum_court_v0",
        "park_labyrinth_classical_v0",
        "park_ice_rink_multipurpose_v3",
        "park_kayak_river_launch_v0",
        "park_tidal_marsh_cordgrass_v0",
        "park_cinema_lawn_projection_v1",
        "park_food_truck_permanent_v1",
        "park_great_lawn_v2",
        "park_campus_meadow_quad_v0",
        "park_urban_beach_family_v2",
        "park_velodrome_open_air_v0",
            "park_mtb_skills_dirt_v2",
            "park_regional_english_landscape_v0",
            "park_beer_garden_munich_v0",
            "park_sunken_courtyard_v0",
            "park_terraced_cascade_v3",
            "park_market_festival_lawn_v1",
            "park_boardwalk_maritime_v0",
            "park_fountain_formal_pool_v1",
            "park_natural_swimming_pond_v0",
            "park_nature_preserve_prairie_v1",
            "park_riverfront_lake_beach_v1",
            "park_reclaimed_wharf_v0",
            "park_quarry_tier_cascade_v2",
            "park_estate_oak_picnic_v1",
            "park_constructed_wetland_boardwalk_v0",
            "park_academic_planted_court_v0",
            "park_campus_green_spine_v0",
            "park_botanical_rose_garden_v3",
            "park_research_arboretum_v0",
            "park_rewilding_reforestation_v1",
            "park_stormwater_arid_channel_v3",
            "park_urban_pocket_rustic_v0",
            "park_neighborhood_contemporary_v3",
            "park_cemetery_classical_v0",
            "park_courtyard_linear_water_v1",
            "park_parklet_sf_timber_v1",
            "park_french_parterre_axis_v1",
            "park_london_railed_square_v1",
            "park_halifax_rose_bandstand_v0",
            "park_olmsted_multilandscape_v3",
            "park_hilltop_viewpoint_v3",
            "park_amsterdam_hofje_garden_v0",
            "park_amsterdam_plein_v0",
            "park_amsterdam_vondelpark_pavilion_v3",
            "park_barcelona_pati_green_v0",
            "park_barcelona_xamfra_corner_v2",
            "park_barcelona_superilla_green_v1",
            "park_calgary_prairie_market_v1",
            "park_calgary_princes_island_festival_v0",
            "park_montreal_mount_royal_grove_v2",
            "park_montreal_neighbourhood_square_v3",
            "park_paris_place_royale_v2",
            "park_paris_square_tree_grid_v3",
            "park_london_circus_planted_v1",
            "park_newyork_pocket_water_v0",
            "park_newyork_community_greenhouse_v3",
            "park_vancouver_seawall_cycle_v2",
            "park_vancouver_beach_pavilion_v0",
            "park_toronto_ravine_creek_v1",
            "park_toronto_urban_market_v1",
            "park_halifax_coastal_fog_path_v2",
            "park_city_hall_modernist_fountain_v2",
            "park_cathedral_courtyard_fountain_v3",
            "park_cultural_museum_terrace_v0",
            "park_transit_green_civic_v2",
            "park_amphitheater_terraced_v0",
            "park_concert_timber_lawn_v2",
            "park_night_market_hawker_v0",
            "park_parade_national_mall_v3",
            "park_canal_ecological_wetland_v3",
            "park_custom_biophilic_urban_v1",
            "park_rooftop_intensive_garden_v0",
            "park_community_healing_garden_v2",
            "park_greenbelt_rail_trail_v1",
            "park_foothill_heathland_trail_v2",
            "park_marina_pacific_dock_v2",
            "park_working_pier_brooklyn_park_v3",
            "park_floating_meadow_loop_v2",
            "park_lighthouse_pacific_headland_v2",
            "park_lake_edge_timber_deck_v2",
            "park_stormwater_natural_creek_v0",
            "park_surface_parking_standard_v0",
            "park_structured_parking_urban_v2",
            "park_underground_parking_green_v1",
            "park_green_parking_infrastructure_v1",
            "park_airport_general_aviation_v2",
            "park_equestrian_working_stable_v1",
            "park_golf_seaside_links_v0",
            "park_driving_range_single_tier_v0",
            "park_multi_sport_track_field_v3",
            "park_retail_parking_landscaped_v1",
        }
    assert local_only.family_ids == ("street_local_public_realm",)
    assert "main_street_complete" not in local_only.archetype_ids
    assert local_only.variants_by_archetype["green_alley"] == ("green_alley_v0",)
    assert "EXECUTABLE PUBLIC REALM LEGO CATALOG" in first.prompt_vocabulary
    assert parks.fingerprint != first.fingerprint
    _sha256(first.fingerprint)


def test_canonical_park_recipe_is_persistable_and_stable():
    request = PublicRealmPlanRequest(
        archetype_id="urban_pocket_park",
        target=ParkPolygonTarget(width_m=30, depth_m=24, area_m2=650),
    )

    first = plan_public_realm_recipe(request)
    second = plan_public_realm_recipe(request)
    payload = first.model_dump(mode="json")

    assert first == second
    assert first.family_id == "park_pocket_courtyard"
    assert first.variant_id == "urban_pocket_park_v0"
    assert first.planting_structure == "garden_courtyard"
    assert first.target == ParkPolygonTarget(width_m=30, depth_m=24, area_m2=650)
    assert public_realm_recipe_hash(first) == first.recipe_hash
    assert json.loads(json.dumps(payload)) == payload
    _sha256(first.catalog_fingerprint)
    _sha256(first.capability_fingerprint)
    _sha256(first.recipe_hash)


def test_skate_park_v0_recipe_owns_exact_skin_and_metric_depth_assets():
    recipe = plan_public_realm_recipe(
        PublicRealmPlanRequest(
            archetype_id="skate_park",
            variant_id="skate_park_v0",
            target=ParkPolygonTarget(width_m=44, depth_m=36, area_m2=1_579),
        )
    )

    assert recipe.family_id == "park_skate_archetype_v0"
    assert recipe.appearance_kit_id == "skate_park_v0_reference_skin"
    assert recipe.planting_structure == "skate_archetype_v0"
    assert recipe.component_set_ids == (
        "skate_park_v0_ground_program",
        "skate_bowl_module_v1",
        "skate_stair_hubba_module_v1",
        "skate_rail_v1",
        "skate_ledge_v1",
        "skate_spectator_bench_v1",
    )


@pytest.mark.parametrize(("archetype_id", "variant_id", "family_id", "appearance_id", "width", "depth"), (
    ("inclusive_playground", "inclusive_playground_v0", "park_inclusive_playground_v0", "inclusive_playground_v0_reference_skin", 55, 45),
    ("dog_park", "dog_park_v0", "park_dog_archetype_v0", "dog_park_v0_reference_skin", 90, 60),
    ("splash_pad_area", "splash_pad_area_v0", "park_splash_pad_v0", "splash_pad_area_v0_reference_skin", 35, 30),
    ("community_garden", "community_garden_v0", "park_community_garden_v0", "community_garden_v0_reference_skin", 55, 55),
    ("basketball_court", "basketball_court_v0", "park_basketball_court_v0", "basketball_court_v0_classic_asphalt_skin", 50, 40),
    ("basketball_court", "basketball_court_v1", "park_basketball_court_v0", "basketball_court_v1_pro_acrylic_skin", 70, 40),
    ("basketball_court", "basketball_court_v2", "park_basketball_court_v0", "basketball_court_v2_half_court_mural_skin", 25, 20),
    ("basketball_court", "basketball_court_v3", "park_basketball_court_v0", "basketball_court_v3_streetball_skin", 40, 30),
    ("tennis_court_cluster", "tennis_court_cluster_v0", "park_tennis_cluster_v0", "tennis_court_cluster_v0_reference_skin", 90, 50),
    ("soccer_pitch_caged", "soccer_pitch_caged_v0", "park_caged_soccer_v0", "soccer_pitch_caged_v0_reference_skin", 66, 24),
    ("athletics_precinct_sports_fields", "athletics_precinct_sports_fields_variant_0", "park_athletics_fields_v0", "athletics_precinct_sports_fields_v0_reference_skin", 220, 80),
    ("nature_play_area", "nature_play_area_v0", "park_nature_play_v0", "nature_play_area_v0_reference_skin", 45, 35),
    ("pump_track", "pump_track_v0", "park_pump_track_v0", "pump_track_v0_reference_skin", 55, 35),
    ("outdoor_fitness_circuit", "outdoor_fitness_circuit_v0", "park_outdoor_fitness_v0", "outdoor_fitness_circuit_v0_reference_skin", 35, 30),
    ("memorial_garden", "memorial_garden_v0", "park_memorial_garden_v0", "memorial_garden_v0_reference_skin", 55, 45),
    ("pickleball_courts", "pickleball_courts_v1", "park_pickleball_community_v1", "pickleball_courts_v1_multi_angle_skin", 85, 72),
    ("running_track_oval", "running_track_oval_v2", "park_track_oval_school_v2", "running_track_oval_v2_multi_angle_skin", 230, 145),
    ("baseball_softball_diamond", "baseball_softball_diamond_v1", "park_baseball_club_hub_v1", "baseball_softball_diamond_v1_multi_angle_skin", 240, 220),
    ("cricket_pitch_oval", "cricket_pitch_oval_v0", "park_cricket_village_green_v0", "cricket_pitch_oval_v0_multi_angle_skin", 200, 180),
    ("sports_field_complex", "sports_field_complex_v0", "park_sports_complex_tournament_v0", "sports_field_complex_v0_multi_angle_skin", 340, 255),
))
def test_archetype_owned_batch_recipes_keep_exact_identity(
    archetype_id, variant_id, family_id, appearance_id, width, depth,
):
    recipe = plan_public_realm_recipe(PublicRealmPlanRequest(
        archetype_id=archetype_id,
        variant_id=variant_id,
        target=ParkPolygonTarget(width_m=width, depth_m=depth, area_m2=width * depth),
    ))
    assert recipe.family_id == family_id
    assert recipe.appearance_kit_id == appearance_id
    basketball_planting = {
        "basketball_court_v0": "basketball_classic_v0",
        "basketball_court_v1": "basketball_pro_v1",
        "basketball_court_v2": "basketball_half_court_v2",
        "basketball_court_v3": "basketball_streetball_v3",
    }
    expected_planting = basketball_planting.get(variant_id) if family_id == "park_basketball_court_v0" else {
        "park_caged_soccer_v0": "caged_soccer_v0",
        "park_athletics_fields_v0": "athletics_fields_v0",
        "park_pickleball_community_v1": "pickleball_community_v1",
        "park_track_oval_school_v2": "track_oval_school_v2",
        "park_baseball_club_hub_v1": "baseball_club_hub_v1",
        "park_cricket_village_green_v0": "cricket_village_green_v0",
        "park_sports_complex_tournament_v0": "sports_complex_tournament_v0",
    }.get(family_id, variant_id)
    assert recipe.planting_structure == expected_planting


@pytest.mark.parametrize(("archetype_id", "family_id", "appearance_id", "width", "depth"), (
    ("community_park", "park_neighborhood_community", "english_pastoral_v1", 250, 160),
    ("pond_lake", "park_water_ecology", "pond_lake_v0_naturalistic_skin", 80, 60),
    ("wetland_rain_garden", "park_water_ecology", "wetland_rain_garden_v0_native_restoration_skin", 80, 60),
    ("japanese_garden", "park_cultural_gardens", "japanese_garden_v0_stroll_skin", 90, 70),
    ("botanical_garden", "park_cultural_gardens", "botanical_garden_v0_collection_skin", 200, 150),
    ("urban_forest", "park_urban_forest", "urban_forest_v0_native_restoration_skin", 250, 200),
    ("reservoir_watershed_park", "park_water_ecology", "reservoir_watershed_park_v0_concrete_edge_skin", 140, 80),
    ("amphitheater_lawn", "park_amphitheater_lawn_v0", "amphitheater_lawn_v0_terraced_performance_skin", 80, 60),
    ("riparian_buffer", "park_water_ecology", "riparian_buffer_v0_native_restoration_skin", 200, 50),
    ("playground_adventure", "park_playground_adventure_v0", "playground_adventure_v0_rustic_timber_skin", 45, 40),
))
def test_batch4_park_recipes_keep_exact_v0_identity(
    archetype_id, family_id, appearance_id, width, depth,
):
    recipe = plan_public_realm_recipe(PublicRealmPlanRequest(
        archetype_id=archetype_id,
        variant_id=f"{archetype_id}_v0",
        target=ParkPolygonTarget(width_m=width, depth_m=depth, area_m2=width * depth),
    ))
    assert recipe.family_id == family_id
    assert recipe.variant_id == f"{archetype_id}_v0"
    assert recipe.appearance_kit_id == appearance_id
    assert recipe.planting_structure in {"naturalistic_grove", f"{archetype_id}_v0"}


@pytest.mark.parametrize(("archetype_id", "family_id", "appearance_id", "planting", "width", "depth"), (
    ("disc_golf_course", "park_disc_golf_wooded_v0", "disc_golf_course_v0_wooded_championship_skin", "disc_golf_wooded_v0", 300, 200),
    ("bocce_petanque_court", "park_bocce_piazza_v0", "bocce_petanque_court_v0_italian_piazza_skin", "bocce_piazza_v0", 28, 16),
    ("climbing_bouldering_wall", "park_climbing_competition_v0", "climbing_bouldering_wall_v0_competition_skin", "climbing_competition_v0", 25, 20),
    ("mini_golf_course", "park_mini_golf_classic_v0", "mini_golf_course_v0_classic_skin", "mini_golf_classic_v0", 50, 30),
    ("beach_volleyball_courts", "park_beach_volleyball_competition_v0", "beach_volleyball_courts_v0_competition_skin", "beach_volleyball_competition_v0", 24, 16),
    ("pollinator_meadow", "park_pollinator_prairie_v0", "pollinator_meadow_v0_prairie_skin", "pollinator_prairie_v0", 80, 60),
    ("urban_orchard_food_forest", "park_orchard_heritage_v0", "urban_orchard_food_forest_v0_heritage_apple_skin", "orchard_heritage_v0", 60, 50),
    ("bioswale_rain_garden", "park_bioswale_streetside_v0", "bioswale_rain_garden_v0_streetside_skin", "bioswale_streetside_v0", 60, 15),
    ("sculpture_garden", "park_sculpture_museum_court_v0", "sculpture_garden_v0_museum_court_skin", "sculpture_museum_court_v0", 60, 50),
    ("labyrinth_meditation", "park_labyrinth_classical_v0", "labyrinth_meditation_v0_classical_stone_skin", "labyrinth_classical_v0", 20, 20),
))
def test_batch5_park_recipes_keep_exact_v0_identity(
    archetype_id, family_id, appearance_id, planting, width, depth,
):
    recipe = plan_public_realm_recipe(PublicRealmPlanRequest(
        archetype_id=archetype_id,
        variant_id=f"{archetype_id}_v0",
        target=ParkPolygonTarget(width_m=width, depth_m=depth, area_m2=width * depth),
    ))
    assert recipe.family_id == family_id
    assert recipe.variant_id == f"{archetype_id}_v0"
    assert recipe.appearance_kit_id == appearance_id
    assert recipe.planting_structure == planting


@pytest.mark.parametrize("archetype_id", (
    "disc_golf_course", "bocce_petanque_court", "climbing_bouldering_wall",
    "mini_golf_course", "beach_volleyball_courts", "pollinator_meadow",
    "urban_orchard_food_forest", "bioswale_rain_garden", "sculpture_garden",
    "labyrinth_meditation",
))
def test_batch5_unknown_variants_still_fail_closed(archetype_id):
    with pytest.raises(PublicRealmPlanningError) as exc:
        plan_public_realm_recipe(PublicRealmPlanRequest(
            archetype_id=archetype_id,
            variant_id=f"{archetype_id}_v99",
            target=ParkPolygonTarget(width_m=80, depth_m=60, area_m2=4_800),
        ))
    assert exc.value.code == "family_incompatible"


@pytest.mark.parametrize(("archetype_id", "variant_id", "family_id", "appearance_id", "planting", "width", "depth"), (
    ("outdoor_ice_rink", "outdoor_ice_rink_v3", "park_ice_rink_multipurpose_v3", "outdoor_ice_rink_v3_multipurpose_pad_skin", "ice_rink_multipurpose_v3", 64, 38),
    ("kayak_launch_dock", "kayak_launch_dock_v0", "park_kayak_river_launch_v0", "kayak_launch_dock_v0_river_launch_skin", "kayak_river_launch_v0", 80, 35),
    ("tidal_marsh_boardwalk", "tidal_marsh_boardwalk_v0", "park_tidal_marsh_cordgrass_v0", "tidal_marsh_boardwalk_v0_cordgrass_skin", "tidal_marsh_cordgrass_v0", 150, 100),
    ("outdoor_cinema_lawn", "outdoor_cinema_lawn_v1", "park_cinema_lawn_projection_v1", "outdoor_cinema_lawn_v1_park_projection_skin", "cinema_lawn_projection_v1", 80, 50),
    ("food_truck_plaza", "food_truck_plaza_v1", "park_food_truck_permanent_v1", "food_truck_plaza_v1_permanent_park_skin", "food_truck_permanent_v1", 50, 40),
    ("festival_event_lawn", "festival_event_lawn_v2", "park_great_lawn_v2", "festival_event_lawn_v2_great_lawn_skin", "great_lawn_v2", 180, 120),
    ("campus_central_quad", "campus_central_quad_variant_0", "park_campus_meadow_quad_v0", "campus_central_quad_v0_naturalized_meadow_skin", "campus_meadow_quad_v0", 100, 80),
    ("urban_beach", "urban_beach_v2", "park_urban_beach_family_v2", "urban_beach_v2_family_splash_skin", "urban_beach_family_v2", 60, 45),
    ("velodrome_cycling_track", "velodrome_cycling_track_variant_0", "park_velodrome_open_air_v0", "velodrome_cycling_track_v0_open_air_skin", "velodrome_open_air_v0", 135, 82),
    ("mountain_bike_park", "mountain_bike_park_variant_2", "park_mtb_skills_dirt_v2", "mountain_bike_park_v2_skills_dirt_skin", "mtb_skills_dirt_v2", 90, 60),
))
def test_batch6_park_recipes_keep_exact_variant_identity(
    archetype_id, variant_id, family_id, appearance_id, planting, width, depth,
):
    recipe = plan_public_realm_recipe(PublicRealmPlanRequest(
        archetype_id=archetype_id,
        variant_id=variant_id,
        target=ParkPolygonTarget(width_m=width, depth_m=depth, area_m2=width * depth),
    ))
    assert recipe.family_id == family_id
    assert recipe.variant_id == variant_id
    assert recipe.appearance_kit_id == appearance_id
    assert recipe.planting_structure == planting


@pytest.mark.parametrize(("archetype_id", "unknown_variant"), (
    ("outdoor_ice_rink", "outdoor_ice_rink_v99"),
    ("kayak_launch_dock", "kayak_launch_dock_v99"),
    ("tidal_marsh_boardwalk", "tidal_marsh_boardwalk_v99"),
    ("outdoor_cinema_lawn", "outdoor_cinema_lawn_v99"),
    ("food_truck_plaza", "food_truck_plaza_v99"),
    ("festival_event_lawn", "festival_event_lawn_v99"),
    ("campus_central_quad", "campus_central_quad_variant_99"),
    ("urban_beach", "urban_beach_v99"),
    ("velodrome_cycling_track", "velodrome_cycling_track_variant_99"),
    ("mountain_bike_park", "mountain_bike_park_variant_99"),
))
def test_batch6_unknown_variants_fail_closed(archetype_id, unknown_variant):
    with pytest.raises(PublicRealmPlanningError) as exc:
        plan_public_realm_recipe(PublicRealmPlanRequest(
            archetype_id=archetype_id,
            variant_id=unknown_variant,
            target=ParkPolygonTarget(width_m=180, depth_m=120, area_m2=21_600),
        ))
    assert exc.value.code == "family_incompatible"


@pytest.mark.parametrize(
    ("archetype_id", "row_width_m", "variant_id", "appearance_kit_id"),
    [
        ("main_street_complete", 18, "main_street_complete_v0", "classic_tree_lined_v1"),
        ("main_street_complete", 18, "main_street_complete_v1", "modern_minimalist_v1"),
        ("main_street_complete", 18, "main_street_complete_v2", "european_cobblestone_v1"),
        ("main_street_complete", 18, "main_street_complete_v3", "tropical_boulevard_v1"),
        (
            "narrow_residential_street",
            10,
            "narrow_residential_street_v0",
            "classic_tree_lined_v1",
        ),
        (
            "narrow_residential_street",
            10,
            "narrow_residential_street_v1",
            "modern_minimalist_v1",
        ),
        (
            "narrow_residential_street",
            10,
            "narrow_residential_street_v2",
            "european_cobblestone_v1",
        ),
        (
            "narrow_residential_street",
            10,
            "narrow_residential_street_v3",
            "tropical_boulevard_v1",
        ),
    ],
)
def test_recurring_street_variants_select_semantically_exact_appearance(
    archetype_id,
    row_width_m,
    variant_id,
    appearance_kit_id,
):
    recipe = plan_public_realm_recipe(
        _street_request(
            archetype_id,
            row_width_m,
            variant_id=variant_id,
        )
    )

    if archetype_id == "main_street_complete":
        assert recipe.family_id == "street_complete_main_18m"
        assert recipe.profile_id == "complete-main-18m-v1"
    else:
        assert recipe.family_id == "street_local_public_realm"
    assert recipe.variant_id == variant_id
    assert recipe.appearance_kit_id == appearance_kit_id


@pytest.mark.parametrize("archetype_id", ["yield_street", "woonerf_shared_street"])
def test_dutch_shared_street_defaults_use_dutch_appearance(archetype_id):
    recipe = plan_public_realm_recipe(_street_request(archetype_id, 10, variant_id=f"{archetype_id}_v0"))

    assert recipe.appearance_kit_id == "dutch_woonerf_v1"


@pytest.mark.parametrize(
    ("archetype_id", "row_width_m", "appearance_kit_id"),
    [
        ("calgary_local", 16, "calgary_contemporary_native"),
        ("green_alley", 5, "green_corridor_v1"),
        ("toronto_laneway", 5, "calgary_contemporary_native"),
    ],
)
def test_single_reviewed_local_street_variants_use_honest_appearance(
    archetype_id,
    row_width_m,
    appearance_kit_id,
):
    recipe = plan_public_realm_recipe(
        _street_request(
            archetype_id,
            row_width_m,
            variant_id=f"{archetype_id}_v0",
        )
    )

    assert recipe.appearance_kit_id == appearance_kit_id


@pytest.mark.parametrize(
    "archetype_id",
    [
        "yield_street",
        "woonerf_shared_street",
        "calgary_local",
        "green_alley",
        "toronto_laneway",
    ],
)
def test_unbuilt_street_visual_variants_are_not_advertised(archetype_id):
    catalog = build_public_realm_capability_catalog()
    assert catalog.variants_by_archetype[archetype_id] == (f"{archetype_id}_v0",)
    with pytest.raises(PublicRealmPlanningError) as raised:
        plan_public_realm_recipe(_street_request(archetype_id, 10, variant_id=f"{archetype_id}_v1"))
    assert raised.value.code == "family_incompatible"


@pytest.mark.parametrize(
    ("archetype_id", "legacy_variant_id", "canonical_variant_id"),
    [
        ("yield_street", "yield_street_v1", "yield_street_v0"),
        ("yield_street", "yield_street_v3", "yield_street_v0"),
        (
            "woonerf_shared_street",
            "woonerf_shared_street_v2",
            "woonerf_shared_street_v0",
        ),
        ("calgary_local", "calgary_local_v3", "calgary_local_v0"),
        ("green_alley", "green_alley_v2", "green_alley_v0"),
        ("toronto_laneway", "toronto_laneway_v3", "toronto_laneway_v0"),
    ],
)
def test_known_legacy_ai_street_variants_normalize_without_mutating_source(
    archetype_id,
    legacy_variant_id,
    canonical_variant_id,
):
    source = {
        "_plan_scenario": "city_policy",
        "road_archetype_id": archetype_id,
        "road_selected_variant_id": legacy_variant_id,
    }

    normalized, migrated_from = normalize_legacy_ai_street_variant_properties(source)

    assert source["road_selected_variant_id"] == legacy_variant_id
    assert normalized["road_selected_variant_id"] == canonical_variant_id
    assert migrated_from == legacy_variant_id


def test_unknown_ai_street_variant_does_not_enter_legacy_migration_path():
    source = {
        "road_archetype_id": "yield_street",
        "road_selected_variant_id": "yield_street_v9",
    }

    normalized, migrated_from = normalize_legacy_ai_street_variant_properties(source)

    assert normalized == source
    assert migrated_from is None
    with pytest.raises(PublicRealmPlanningError) as raised:
        plan_public_realm_recipe(
            _street_request(
                "yield_street",
                10,
                variant_id="yield_street_v9",
            )
        )
    assert raised.value.code == "family_incompatible"


def test_main_street_prefers_18m_but_retains_exact_22m_migration_family():
    canonical = plan_public_realm_recipe(_street_request("main_street_complete", 18))
    migrated = plan_public_realm_recipe(_street_request("main_street_complete", 22))

    assert canonical.family_id == "street_complete_main_18m"
    assert canonical.target.row_width_m == 18
    assert migrated.family_id == "street_complete_main_22m"
    assert migrated.target.row_width_m == 22
    assert migrated.appearance_kit_id == "classic_tree_lined_v1"


def test_main_street_rejects_noncanonical_intermediate_row_with_structured_error():
    with pytest.raises(PublicRealmPlanningError) as raised:
        plan_public_realm_recipe(_street_request("main_street_complete", 20))

    error = raised.value
    assert error.code == "family_incompatible"
    assert error.requested["target"]["row_width_m"] == 20
    assert error.supported_families[0]["family_id"] == "street_complete_main_18m"
    assert {family["family_id"] for family in error.supported_families} == {
        "street_complete_main_18m",
        "street_complete_main_22m",
    }
    assert error.violations == [
        {
            "field": "target.row_width_m",
            "requested": 20.0,
            "supported": [17.95, 18.05],
        }
    ]
    assert error.as_detail()["code"] == "family_incompatible"


def test_local_row_compatibility_is_source_specific():
    assert (
        plan_public_realm_recipe(_street_request("woonerf_shared_street", 14)).family_id == "street_local_public_realm"
    )
    assert plan_public_realm_recipe(_street_request("multi_use_trail", 4)).variant_id == "multi_use_trail_v1"

    with pytest.raises(PublicRealmPlanningError) as raised:
        plan_public_realm_recipe(_street_request("multi_use_trail", 7))
    assert raised.value.violations[0]["field"] == "target.row_width_m"


def test_four_way_node_requires_exact_topology_and_reports_supported_arms():
    request = PublicRealmPlanRequest(
        archetype_id="protected_intersection",
        target=StreetNodeTarget(
            approach_row_width_m=22,
            diameter_m=30,
            arm_count=3,
        ),
    )

    with pytest.raises(PublicRealmPlanningError) as raised:
        plan_public_realm_recipe(request)

    assert raised.value.code == "family_incompatible"
    assert raised.value.violations == [
        {
            "field": "target.arm_count",
            "requested": 3,
            "supported": [4],
        }
    ]


def test_unknown_archetype_is_family_not_found_without_fallback():
    with pytest.raises(PublicRealmPlanningError) as raised:
        plan_public_realm_recipe(_street_request("invented_magic_boulevard", 22))

    assert raised.value.code == "family_not_found"
    assert raised.value.requested["archetype_id"] == "invented_magic_boulevard"
    assert raised.value.supported_families


def test_recipe_identity_fails_closed_after_payload_or_catalog_hash_tampering():
    recipe = plan_public_realm_recipe(_street_request("narrow_residential_street", 12))
    payload = recipe.model_dump(mode="json")
    original = public_realm_representation_hash(
        source_hash="a" * 64,
        recipe=payload,
    )

    assert original is not None
    assert public_realm_recipe_identity(payload) is not None
    assert (
        public_realm_representation_hash(
            source_hash="b" * 64,
            recipe=payload,
        )
        != original
    )

    payload["appearance_kit_id"] = "tampered"
    assert public_realm_recipe_identity(payload) is None
    assert (
        public_realm_representation_hash(
            source_hash="a" * 64,
            recipe=payload,
        )
        is None
    )

    # A self-hash proves only payload integrity.  Recomputing it must not turn
    # a non-canonical renderer recipe into an executable catalog identity.
    payload["recipe_hash"] = public_realm_recipe_hash(payload)
    assert public_realm_recipe_hash(payload) == payload["recipe_hash"]
    assert public_realm_recipe_identity(payload) is None


def test_linear_greenway_accepts_compact_corridor_but_rejects_square_pond_lobe():
    compact_corridor = plan_public_realm_recipe(
        PublicRealmPlanRequest(
            archetype_id="linear_park_greenway",
            target=ParkPolygonTarget(width_m=72, depth_m=15, area_m2=1_050),
        )
    )

    assert compact_corridor.family_id == "park_linear_greenway"
    with pytest.raises(PublicRealmPlanningError) as raised:
        plan_public_realm_recipe(
            PublicRealmPlanRequest(
                archetype_id="linear_park_greenway",
                target=ParkPolygonTarget(width_m=38, depth_m=34, area_m2=1_120),
            )
        )
    assert raised.value.violations[-1] == {
        "field": "target.aspect_ratio",
        "requested": pytest.approx(1.118, abs=0.001),
        "supported": {"min": 3.0},
    }


def test_pocket_courtyard_family_accepts_broad_clipped_courtyard_envelope():
    recipe = plan_public_realm_recipe(
        PublicRealmPlanRequest(
            archetype_id="urban_pocket_park",
            target=ParkPolygonTarget(width_m=86, depth_m=78, area_m2=2_000),
        )
    )

    assert recipe.family_id == "park_pocket_courtyard"


def _to_wgs84(geometry):
    transformer = build_transformer(CRS.from_epsg(32611), CRS.from_epsg(4326))
    return project_geometry(geometry, transformer)


def test_zone_planner_measures_metric_geometry_and_defaults_exact_variant():
    street = _to_wgs84(box(700_000, 5_650_000, 700_200, 5_650_022))
    recipe = plan_public_realm_zone_recipe(
        "road",
        street,
        {
            "_plan_scenario": "community_wellbeing",
            "_plan_role": "street",
            "road_archetype_id": "main_street_complete",
            "width": 22,
        },
        strict=True,
    )

    assert recipe is not None
    assert recipe.target.target_type == "street_segment"
    assert recipe.target.row_width_m == 22
    assert recipe.target.length_m == pytest.approx(200, abs=0.1)
    assert recipe.variant_id == "main_street_complete_v0"
    assert recipe.family_id == "street_complete_main_22m"


def test_skate_zone_planner_requires_complete_unscaled_program_inside_polygon():
    fitting = _to_wgs84(box(700_000, 5_650_000, 700_044, 5_650_036))
    recipe = plan_public_realm_zone_recipe(
        "green_space",
        fitting,
        {
            "green_space_archetype_id": "skate_park",
            "green_space_selected_variant_id": "skate_park_v0",
        },
        strict=True,
    )

    assert recipe is not None
    assert recipe.family_id == "park_skate_archetype_v0"
    assert recipe.target.width_m == pytest.approx(44, abs=0.1)
    assert recipe.target.depth_m == pytest.approx(36, abs=0.1)

    # The bounding box and area still pass the catalog envelope, but this
    # centre cutout makes a complete 40 x 30 m placement impossible.
    clipped_metric = box(700_000, 5_650_000, 700_044, 5_650_036).difference(
        box(700_016, 5_650_000, 700_028, 5_650_026)
    )
    clipped = _to_wgs84(clipped_metric)
    with pytest.raises(PublicRealmPlanningError) as raised:
        plan_public_realm_zone_recipe(
            "green_space",
            clipped,
            {
                "green_space_archetype_id": "skate_park",
                "green_space_selected_variant_id": "skate_park_v0",
            },
            strict=True,
        )
    assert raised.value.violations[0]["field"] == "target.polygon_fit"
    assert plan_public_realm_zone_recipe(
        "green_space",
        clipped,
        {
            "green_space_archetype_id": "skate_park",
            "green_space_selected_variant_id": "skate_park_v0",
        },
        strict=False,
    ) is None


def test_strict_street_attestation_rejects_claimed_width_that_geometry_disproves():
    street = _to_wgs84(box(700_000, 5_650_000, 700_146, 5_650_022))
    properties = {
        "_plan_scenario": "community_wellbeing",
        "_plan_role": "street",
        "road_archetype_id": "calgary_local",
        "road_selected_variant_id": "calgary_local_v0",
        "width": 16,
    }

    with pytest.raises(PublicRealmPlanningError) as raised:
        plan_public_realm_zone_recipe(
            "road",
            street,
            properties,
            strict=True,
        )

    assert raised.value.requested["target"]["row_width_m"] == pytest.approx(
        22,
        abs=0.1,
    )
    assert raised.value.violations[0]["field"] == "target.row_width_m"

    # Manual/legacy callers degrade to the procedural renderer instead of
    # persisting a V1 recipe that Direct would later reject.
    legacy = plan_public_realm_zone_recipe(
        "road",
        street,
        properties,
        strict=False,
    )
    assert legacy is None


def test_manual_compile_and_direct_replan_share_one_canonical_street_target():
    street = _to_wgs84(box(700_000, 5_650_000, 700_146, 5_650_016))
    properties = {
        "_plan_role": "street",
        "road_archetype_id": "calgary_local",
        "road_selected_variant_id": "calgary_local_v0",
        "width": 16,
    }

    manual_recipe = plan_public_realm_zone_recipe(
        "road",
        street,
        properties,
        strict=False,
    )
    direct_recipe = plan_public_realm_zone_recipe(
        "road",
        street,
        properties,
        strict=True,
    )

    assert manual_recipe is not None
    assert manual_recipe == direct_recipe


def test_zone_planner_preserves_legacy_fallback_but_ai_fails_closed():
    geometry = _to_wgs84(box(700_000, 5_650_000, 700_030, 5_650_030))
    properties = {
        "_plan_role": "open_space",
        "green_space_archetype_id": "botanical_garden",
    }

    assert (
        plan_public_realm_zone_recipe(
            "green_space",
            geometry,
            properties,
            strict=False,
        )
        is None
    )

    with pytest.raises(PublicRealmPlanningError) as raised:
        plan_public_realm_zone_recipe(
            "green_space",
            geometry,
            {**properties, "_plan_scenario": "community_wellbeing"},
            strict=True,
        )
    assert raised.value.code == "family_incompatible"


def test_zone_planner_rejects_non_polygonal_park_without_attribute_error():
    geometry = _to_wgs84(
        LineString(
            [
                (700_000, 5_650_000),
                (700_030, 5_650_000),
            ]
        )
    )

    with pytest.raises(ValueError, match="no measurable footprint"):
        plan_public_realm_zone_recipe(
            "green_space",
            geometry,
            {
                "_plan_scenario": "community_wellbeing",
                "_plan_role": "open_space",
                "green_space_archetype_id": "urban_pocket_park",
            },
            strict=True,
        )


def test_compact_roundabout_accepts_current_parametric_node():
    geometry = _to_wgs84(Point(700_000, 5_650_000).buffer(15, quad_segs=8))
    recipe = plan_public_realm_zone_recipe(
        "road",
        geometry,
        {
            "_plan_scenario": "community_wellbeing",
            "_plan_role": "street",
            "street_role": "roundabout",
            "road_archetype_id": "roundabout",
            "width": 22,
        },
        strict=True,
    )

    assert recipe is not None
    assert recipe.family_id == "street_compact_roundabout"
    assert recipe.target.target_type == "street_node"
    assert recipe.target.diameter_m == pytest.approx(30, abs=0.2)


def test_compact_roundabout_rejects_non_four_arm_topology():
    with pytest.raises(PublicRealmPlanningError) as raised:
        plan_public_realm_recipe(
            PublicRealmPlanRequest(
                archetype_id="roundabout",
                target=StreetNodeTarget(
                    approach_row_width_m=22,
                    diameter_m=30,
                    arm_count=3,
                ),
            )
        )

    assert raised.value.violations == [
        {
            "field": "target.arm_count",
            "requested": 3,
            "supported": [4],
        }
    ]


@pytest.mark.parametrize(
    ("family_id", "archetype_id", "variant_id", "appearance_kit_id"),
    [
        ("park_regional_english_landscape_v0", "regional_park", "regional_park_v0", "regional_park_v0_english_landscape_skin"),
        ("park_beer_garden_munich_v0", "beer_garden", "beer_garden_v0", "beer_garden_v0_munich_chestnut_skin"),
        ("park_sunken_courtyard_v0", "sunken_plaza", "sunken_plaza_v0", "sunken_plaza_v0_intimate_courtyard_skin"),
        ("park_terraced_cascade_v3", "stepped_terraced_plaza", "stepped_terraced_plaza_v3", "stepped_terraced_plaza_v3_modernist_cascade_skin"),
        ("park_market_festival_lawn_v1", "market_square", "market_square_v1", "market_square_v1_open_festival_lawn_skin"),
        ("park_boardwalk_maritime_v0", "promenade_boardwalk", "promenade_boardwalk_v0", "promenade_boardwalk_v0_maritime_skin"),
        ("park_fountain_formal_pool_v1", "fountain_water_feature", "fountain_water_feature_v1", "fountain_water_feature_v1_formal_pool_skin"),
        ("park_natural_swimming_pond_v0", "swimming_pool_complex", "swimming_pool_complex_v0", "swimming_pool_complex_v0_natural_pond_skin"),
        ("park_nature_preserve_prairie_v1", "nature_preserve", "nature_preserve_v1", "nature_preserve_v1_tallgrass_prairie_skin"),
        ("park_riverfront_lake_beach_v1", "riverfront_park_beach", "riverfront_park_beach_v1", "riverfront_park_beach_v1_lake_swimming_skin"),
    ],
)
def test_batch7_park_families_are_exact_executable_selections(
    family_id: str,
    archetype_id: str,
    variant_id: str,
    appearance_kit_id: str,
):
    catalog = build_public_realm_capability_catalog(family_ids=[family_id])
    assert catalog.family_ids == (family_id,)
    capability = catalog.capabilities[0]
    assert capability.kind == "park"
    assert capability.generator == "park_kit"
    selection = next(
        candidate
        for candidate in capability.selections
        if candidate.variant_id == variant_id
    )
    assert selection.archetype_id == archetype_id
    assert selection.variant_id == variant_id
    assert selection.appearance_kit_id == appearance_kit_id
    assert selection.is_default is True
    assert selection.component_set_ids


@pytest.mark.parametrize(
    ("family_id", "archetype_id", "variant_id", "width_m", "depth_m"),
    [
        ("park_regional_english_landscape_v0", "regional_park", "regional_park_v0", 220.0, 160.0),
        ("park_beer_garden_munich_v0", "beer_garden", "beer_garden_v0", 30.0, 28.0),
        ("park_sunken_courtyard_v0", "sunken_plaza", "sunken_plaza_v0", 30.0, 25.0),
        ("park_terraced_cascade_v3", "stepped_terraced_plaza", "stepped_terraced_plaza_v3", 90.0, 100.0),
        ("park_market_festival_lawn_v1", "market_square", "market_square_v1", 95.0, 75.0),
        ("park_boardwalk_maritime_v0", "promenade_boardwalk", "promenade_boardwalk_v0", 120.0, 22.0),
        ("park_fountain_formal_pool_v1", "fountain_water_feature", "fountain_water_feature_v1", 55.0, 35.0),
        ("park_natural_swimming_pond_v0", "swimming_pool_complex", "swimming_pool_complex_v0", 90.0, 70.0),
        ("park_nature_preserve_prairie_v1", "nature_preserve", "nature_preserve_v1", 180.0, 120.0),
        ("park_riverfront_lake_beach_v1", "riverfront_park_beach", "riverfront_park_beach_v1", 130.0, 90.0),
    ],
)
def test_batch7_nominal_sites_compile_without_image_calls(
    family_id: str,
    archetype_id: str,
    variant_id: str,
    width_m: float,
    depth_m: float,
):
    geometry = _to_wgs84(box(700_000, 5_650_000, 700_000 + width_m, 5_650_000 + depth_m))
    recipe = plan_public_realm_zone_recipe(
        "green_space",
        geometry,
        {
            "green_space_archetype_id": archetype_id,
            "green_space_selected_variant_id": variant_id,
        },
        strict=True,
    )
    assert recipe is not None
    assert recipe.family_id == family_id
    assert recipe.variant_id == variant_id
    assert recipe.generator == "park_kit"


@pytest.mark.parametrize(
    ("family_id", "archetype_id", "variant_id", "appearance_kit_id", "width_m", "depth_m"),
    [
        ("park_reclaimed_wharf_v0", "reclaimed_industrial_park", "reclaimed_industrial_park_v0", "reclaimed_industrial_park_v0_wharf_skin", 100.0, 50.0),
        ("park_quarry_tier_cascade_v2", "quarry_sunken_garden_park", "quarry_sunken_garden_park_v2", "quarry_sunken_garden_park_v2_tier_cascade_skin", 200.0, 150.0),
        ("park_estate_oak_picnic_v1", "estate_picnic_grove", "estate_picnic_grove_v1", "estate_picnic_grove_v1_oak_skin", 120.0, 100.0),
        ("park_constructed_wetland_boardwalk_v0", "constructed_wetland_eco_park", "constructed_wetland_eco_park_variant_0", "constructed_wetland_eco_park_v0_boardwalk_skin", 180.0, 110.0),
        ("park_academic_planted_court_v0", "academic_courtyard", "academic_courtyard_variant_0", "academic_courtyard_v0_planted_skin", 40.0, 38.0),
        ("park_campus_green_spine_v0", "campus_pedestrian_spine", "campus_pedestrian_spine_variant_0", "campus_pedestrian_spine_v0_green_skin", 30.0, 240.0),
        ("park_botanical_rose_garden_v3", "botanical_garden", "botanical_garden_v3", "botanical_garden_v3_rose_skin", 120.0, 90.0),
        ("park_research_arboretum_v0", "research_garden_teaching_arboretum", "research_garden_teaching_arboretum_variant_0", "research_garden_teaching_arboretum_v0_skin", 300.0, 220.0),
        ("park_rewilding_reforestation_v1", "rewilding_ecological_restoration_zone", "rewilding_ecological_restoration_zone_variant_1", "rewilding_ecological_restoration_zone_v1_skin", 300.0, 220.0),
        ("park_stormwater_arid_channel_v3", "stormwater_resilience_park", "stormwater_resilience_park_variant_3", "stormwater_resilience_park_v3_arid_skin", 200.0, 125.0),
    ],
)
def test_batch8_exact_families_compile_without_image_calls(
    family_id: str,
    archetype_id: str,
    variant_id: str,
    appearance_kit_id: str,
    width_m: float,
    depth_m: float,
):
    catalog = build_public_realm_capability_catalog(family_ids=[family_id])
    assert catalog.family_ids == (family_id,)
    selection = catalog.capabilities[0].selections[0]
    assert selection.archetype_id == archetype_id
    assert selection.variant_id == variant_id
    assert selection.appearance_kit_id == appearance_kit_id
    assert selection.is_default is True
    geometry = _to_wgs84(box(700_000, 5_650_000, 700_000 + width_m, 5_650_000 + depth_m))
    recipe = plan_public_realm_zone_recipe(
        "green_space",
        geometry,
        {"green_space_archetype_id": archetype_id, "green_space_selected_variant_id": variant_id},
        strict=True,
    )
    assert recipe is not None
    assert recipe.family_id == family_id
    assert recipe.variant_id == variant_id
    assert recipe.appearance_kit_id == appearance_kit_id
    assert recipe.generator == "park_kit"


@pytest.mark.parametrize(
    ("archetype_id", "variant_id"),
    [
        ("reclaimed_industrial_park", "reclaimed_industrial_park_v0"),
        ("quarry_sunken_garden_park", "quarry_sunken_garden_park_v2"),
        ("estate_picnic_grove", "estate_picnic_grove_v1"),
        ("constructed_wetland_eco_park", "constructed_wetland_eco_park_variant_0"),
        ("academic_courtyard", "academic_courtyard_variant_0"),
        ("campus_pedestrian_spine", "campus_pedestrian_spine_variant_0"),
        ("botanical_garden", "botanical_garden_v3"),
        ("research_garden_teaching_arboretum", "research_garden_teaching_arboretum_variant_0"),
        ("rewilding_ecological_restoration_zone", "rewilding_ecological_restoration_zone_variant_1"),
        ("stormwater_resilience_park", "stormwater_resilience_park_variant_3"),
    ],
)
def test_batch8_families_adapt_to_compact_urban_park_polygon(
    archetype_id: str,
    variant_id: str,
):
    """The reference acreage guides composition; it must not be a literal site requirement."""

    geometry = _to_wgs84(box(700_000, 5_650_000, 700_099, 5_650_037))
    recipe = plan_public_realm_zone_recipe(
        "green_space",
        geometry,
        {
            "green_space_archetype_id": archetype_id,
            "green_space_selected_variant_id": variant_id,
        },
        strict=True,
    )
    assert recipe is not None
    assert recipe.variant_id == variant_id
    assert recipe.generator == "park_kit"


@pytest.mark.parametrize(
    ("family_id", "archetype_id", "variant_id", "appearance_kit_id", "width_m", "depth_m"),
    [
        ("park_urban_pocket_rustic_v0", "urban_pocket_park", "urban_pocket_park_v0", "urban_pocket_park_v0_rustic_skin", 20.0, 20.0),
        ("park_neighborhood_contemporary_v3", "neighborhood_park", "neighborhood_park_v3", "neighborhood_park_v3_contemporary_skin", 100.0, 80.0),
        ("park_cemetery_classical_v0", "cemetery_memorial_grounds", "cemetery_memorial_grounds_v0", "cemetery_memorial_grounds_v0_classical_skin", 250.0, 200.0),
        ("park_courtyard_linear_water_v1", "courtyard_plaza", "courtyard_plaza_v1", "courtyard_plaza_v1_linear_water_skin", 35.0, 35.0),
        ("park_parklet_sf_timber_v1", "street_plaza_parklet", "street_plaza_parklet_v1", "street_plaza_parklet_v1_sf_timber_skin", 10.0, 6.0),
        ("park_french_parterre_axis_v1", "parisian_jardin", "parisian_jardin_v1", "parisian_jardin_v1_water_axis_skin", 180.0, 140.0),
        ("park_london_railed_square_v1", "london_garden_square", "london_garden_square_v1", "london_garden_square_v1_railed_skin", 100.0, 80.0),
        ("park_halifax_rose_bandstand_v0", "halifax_public_gardens", "halifax_public_gardens_v0", "halifax_public_gardens_v0_rose_skin", 200.0, 150.0),
        ("park_olmsted_multilandscape_v3", "picturesque_olmsted_park", "picturesque_olmsted_park_v3", "picturesque_olmsted_park_v3_multilandscape_skin", 400.0, 350.0),
        ("park_hilltop_viewpoint_v3", "hilltop_topographic_park", "hilltop_topographic_park_v3", "hilltop_topographic_park_v3_viewpoint_skin", 180.0, 180.0),
    ],
)
def test_batch9_exact_families_compile_without_image_calls(
    family_id: str,
    archetype_id: str,
    variant_id: str,
    appearance_kit_id: str,
    width_m: float,
    depth_m: float,
):
    catalog = build_public_realm_capability_catalog(family_ids=[family_id])
    assert catalog.family_ids == (family_id,)
    selection = next(
        candidate
        for candidate in catalog.capabilities[0].selections
        if candidate.variant_id == variant_id
    )
    assert selection.archetype_id == archetype_id
    assert selection.variant_id == variant_id
    assert selection.appearance_kit_id == appearance_kit_id
    assert selection.is_default is True
    geometry = _to_wgs84(box(700_000, 5_650_000, 700_000 + width_m, 5_650_000 + depth_m))
    recipe = plan_public_realm_zone_recipe(
        "green_space",
        geometry,
        {"green_space_archetype_id": archetype_id, "green_space_selected_variant_id": variant_id},
        strict=True,
    )
    assert recipe is not None
    assert recipe.family_id == family_id
    assert recipe.variant_id == variant_id
    assert recipe.appearance_kit_id == appearance_kit_id
    assert recipe.generator == "park_kit"


@pytest.mark.parametrize(
    ("archetype_id", "variant_id"),
    [
        ("neighborhood_park", "neighborhood_park_v3"),
        ("cemetery_memorial_grounds", "cemetery_memorial_grounds_v0"),
        ("courtyard_plaza", "courtyard_plaza_v1"),
        ("parisian_jardin", "parisian_jardin_v1"),
        ("london_garden_square", "london_garden_square_v1"),
        ("halifax_public_gardens", "halifax_public_gardens_v0"),
        ("picturesque_olmsted_park", "picturesque_olmsted_park_v3"),
        ("hilltop_topographic_park", "hilltop_topographic_park_v3"),
    ],
)
def test_large_batch9_families_adapt_to_compact_urban_park_polygon(
    archetype_id: str,
    variant_id: str,
):
    geometry = _to_wgs84(box(700_000, 5_650_000, 700_099, 5_650_037))
    recipe = plan_public_realm_zone_recipe(
        "green_space",
        geometry,
        {"green_space_archetype_id": archetype_id, "green_space_selected_variant_id": variant_id},
        strict=True,
    )
    assert recipe is not None
    assert recipe.variant_id == variant_id
    assert recipe.generator == "park_kit"


@pytest.mark.parametrize(
    ("family_id", "archetype_id", "variant_id", "appearance_kit_id", "width_m", "depth_m"),
    [
        ("park_amsterdam_hofje_garden_v0", "amsterdam_hofje_garden", "amsterdam_hofje_garden_v0", "amsterdam_hofje_garden_v0_skin", 25.0, 25.0),
        ("park_amsterdam_plein_v0", "amsterdam_plein", "amsterdam_plein_v0", "amsterdam_plein_v0_brick_skin", 70.0, 55.0),
        ("park_amsterdam_vondelpark_pavilion_v3", "amsterdam_vondelpark", "amsterdam_vondelpark_v3", "amsterdam_vondelpark_v3_pavilion_skin", 250.0, 160.0),
        ("park_barcelona_pati_green_v0", "barcelona_pati_interior", "barcelona_pati_interior_v0", "barcelona_pati_interior_v0_green_skin", 50.0, 40.0),
        ("park_barcelona_xamfra_corner_v2", "barcelona_placa_xamfra", "barcelona_placa_xamfra_v2", "barcelona_placa_xamfra_v2_corner_skin", 30.0, 28.0),
        ("park_barcelona_superilla_green_v1", "barcelona_superilla", "barcelona_superilla_v1", "barcelona_superilla_v1_green_skin", 130.0, 130.0),
        ("park_calgary_prairie_market_v1", "calgary_prairie_plaza", "calgary_prairie_plaza_v1", "calgary_prairie_plaza_v1_market_skin", 70.0, 55.0),
        ("park_calgary_princes_island_festival_v0", "calgary_princes_island", "calgary_princes_island_v0", "calgary_princes_island_v0_festival_skin", 400.0, 200.0),
        ("park_montreal_mount_royal_grove_v2", "montreal_mount_royal", "montreal_mount_royal_v2", "montreal_mount_royal_v2_grove_skin", 500.0, 400.0),
        ("park_montreal_neighbourhood_square_v3", "montreal_square", "montreal_square_v3", "montreal_square_v3_neighbourhood_skin", 70.0, 55.0),
        ("park_paris_place_royale_v2", "parisian_place", "parisian_place_v2", "parisian_place_v2_royale_skin", 85.0, 65.0),
        ("park_paris_square_tree_grid_v3", "parisian_square", "parisian_square_v3", "parisian_square_v3_tree_grid_skin", 70.0, 55.0),
        ("park_london_circus_planted_v1", "london_circus", "london_circus_v1", "london_circus_v1_planted_skin", 75.0, 60.0),
        ("park_newyork_pocket_water_v0", "newyork_pocket_park", "newyork_pocket_park_v0", "newyork_pocket_park_v0_water_skin", 32.0, 24.0),
        ("park_newyork_community_greenhouse_v3", "newyork_community_garden", "newyork_community_garden_v3", "newyork_community_garden_v3_greenhouse_skin", 45.0, 32.0),
        ("park_vancouver_seawall_cycle_v2", "vancouver_seawall", "vancouver_seawall_v2", "vancouver_seawall_v2_cycle_skin", 140.0, 24.0),
        ("park_vancouver_beach_pavilion_v0", "vancouver_beach_park", "vancouver_beach_park_v0", "vancouver_beach_park_v0_pavilion_skin", 130.0, 70.0),
        ("park_toronto_ravine_creek_v1", "toronto_ravine", "toronto_ravine_v1", "toronto_ravine_v1_creek_skin", 220.0, 90.0),
        ("park_toronto_urban_market_v1", "toronto_urban_square", "toronto_urban_square_v1", "toronto_urban_square_v1_market_skin", 90.0, 65.0),
        ("park_halifax_coastal_fog_path_v2", "halifax_coastal_park", "halifax_coastal_park_v2", "halifax_coastal_park_v2_fog_path_skin", 180.0, 100.0),
        ("park_city_hall_modernist_fountain_v2", "city_hall_government_plaza", "city_hall_government_plaza_v2", "city_hall_government_plaza_v2_modernist_skin", 80.0, 60.0),
        ("park_cathedral_courtyard_fountain_v3", "cathedral_religious_forecourt", "cathedral_religious_forecourt_v3", "cathedral_religious_forecourt_v3_courtyard_skin", 70.0, 55.0),
        ("park_cultural_museum_terrace_v0", "cultural_institution_forecourt", "cultural_institution_forecourt_v0", "cultural_institution_forecourt_v0_museum_terrace_skin", 95.0, 65.0),
        ("park_transit_green_civic_v2", "transit_plaza", "transit_plaza_v2", "transit_plaza_v2_green_civic_skin", 75.0, 48.0),
        ("park_amphitheater_terraced_v0", "amphitheater_performance_space", "amphitheater_performance_space_v0", "amphitheater_performance_space_v0_terraced_skin", 90.0, 70.0),
        ("park_concert_timber_lawn_v2", "concert_pavilion_lawn", "concert_pavilion_lawn_v2", "concert_pavilion_lawn_v2_timber_skin", 140.0, 95.0),
        ("park_night_market_hawker_v0", "night_market", "night_market_v0", "night_market_v0_hawker_skin", 85.0, 40.0),
        ("park_parade_national_mall_v3", "parade_ground", "parade_ground_v3", "parade_ground_v3_national_mall_skin", 220.0, 90.0),
        ("park_canal_ecological_wetland_v3", "canal_waterway", "canal_waterway_v3", "canal_waterway_v3_ecological_skin", 180.0, 75.0),
        ("park_custom_biophilic_urban_v1", "custom_parks_plazas", "custom_parks_plazas_v1", "custom_parks_plazas_v1_biophilic_skin", 75.0, 60.0),
        ("park_rooftop_intensive_garden_v0", "rooftop_garden", "rooftop_garden_v0", "rooftop_garden_v0_intensive_skin", 25.0, 20.0),
        ("park_community_healing_garden_v2", "community_garden_enhanced", "garden_healing", "community_garden_enhanced_healing_skin", 60.0, 50.0),
        ("park_greenbelt_rail_trail_v1", "greenbelt_buffer_park", "greenbelt_buffer_park_v1", "greenbelt_buffer_park_v1_rail_trail_skin", 600.0, 180.0),
        ("park_foothill_heathland_trail_v2", "foothill_trail_park", "foothill_trail_park_v2", "foothill_trail_park_v2_heathland_skin", 400.0, 400.0),
        ("park_marina_pacific_dock_v2", "marina_yacht_harbor", "marina_yacht_harbor_v2", "marina_yacht_harbor_v2_pacific_skin", 140.0, 120.0),
        ("park_working_pier_brooklyn_park_v3", "working_pier_wharf_conversion", "working_pier_wharf_conversion_v3", "working_pier_wharf_conversion_v3_park_skin", 180.0, 100.0),
        ("park_floating_meadow_loop_v2", "floating_park_pool", "floating_park_pool_v2", "floating_park_pool_v2_meadow_skin", 80.0, 70.0),
        ("park_lighthouse_pacific_headland_v2", "lighthouse_point_park", "lighthouse_point_park_v2", "lighthouse_point_park_v2_pacific_skin", 180.0, 180.0),
        ("park_lake_edge_timber_deck_v2", "lake_edge_plaza", "lake_edge_plaza_v2", "lake_edge_plaza_v2_timber_skin", 200.0, 40.0),
        ("park_stormwater_natural_creek_v0", "stormwater_naturalized_drainage_corridor", "stormwater_naturalized_drainage_corridor_variant_0", "stormwater_naturalized_drainage_corridor_v0_creek_skin", 375.0, 40.0),
        ("park_surface_parking_standard_v0", "surface_parking_lot", "surface_parking_lot_v0", "surface_parking_lot_v0_standard_skin", 50.0, 40.0),
        ("park_structured_parking_urban_v2", "structured_parking_garage", "structured_parking_garage_v2", "structured_parking_garage_v2_urban_skin", 50.0, 20.0),
        ("park_underground_parking_green_v1", "underground_parking_entry", "underground_parking_entry_v1", "underground_parking_entry_v1_green_skin", 20.0, 20.0),
        ("park_green_parking_infrastructure_v1", "green_parking_lot", "green_parking_lot_v1", "green_parking_lot_v1_infrastructure_skin", 40.0, 30.0),
        ("park_airport_general_aviation_v2", "airport_airfield", "airport_airfield_variant_2", "airport_airfield_v2_general_aviation_skin", 2200.0, 1360.0),
        ("park_equestrian_working_stable_v1", "equestrian_center", "equestrian_center_variant_1", "equestrian_center_v1_working_stable_skin", 250.0, 160.0),
        ("park_golf_seaside_links_v0", "golf_course_18_hole", "golf_course_18_hole_variant_0", "golf_course_18_hole_v0_links_skin", 1000.0, 600.0),
        ("park_driving_range_single_tier_v0", "golf_driving_range", "golf_driving_range_variant_0", "golf_driving_range_v0_single_tier_skin", 120.0, 290.0),
        ("park_multi_sport_track_field_v3", "multi_sport_complex", "multi_sport_complex_variant_3", "multi_sport_complex_v3_track_field_skin", 250.0, 160.0),
        ("park_retail_parking_landscaped_v1", "suburban_retail_parking_lot", "suburban_retail_parking_lot_v1", "suburban_retail_parking_lot_v1_landscaped_skin", 70.0, 50.0),
    ],
)
def test_batch10_exact_families_compile_without_image_calls(
    family_id: str,
    archetype_id: str,
    variant_id: str,
    appearance_kit_id: str,
    width_m: float,
    depth_m: float,
):
    catalog = build_public_realm_capability_catalog(family_ids=[family_id])
    selection = next(
        candidate
        for candidate in catalog.capabilities[0].selections
        if candidate.variant_id == variant_id
    )
    assert selection.archetype_id == archetype_id
    assert selection.variant_id == variant_id
    assert selection.appearance_kit_id == appearance_kit_id
    assert selection.is_default is True
    geometry = _to_wgs84(box(700_000, 5_650_000, 700_000 + width_m, 5_650_000 + depth_m))
    recipe = plan_public_realm_zone_recipe(
        "green_space",
        geometry,
        {"green_space_archetype_id": archetype_id, "green_space_selected_variant_id": variant_id},
        strict=True,
    )
    assert recipe is not None
    assert recipe.family_id == family_id
    assert recipe.variant_id == variant_id
    assert recipe.appearance_kit_id == appearance_kit_id
    assert recipe.generator == "park_kit"


def test_batch15_closes_all_four_variants_for_the_final_ten_parents():
    expected = {
        "park_surface_parking_standard_v0": "surface_parking_lot",
        "park_structured_parking_urban_v2": "structured_parking_garage",
        "park_underground_parking_green_v1": "underground_parking_entry",
        "park_green_parking_infrastructure_v1": "green_parking_lot",
        "park_airport_general_aviation_v2": "airport_airfield",
        "park_equestrian_working_stable_v1": "equestrian_center",
        "park_golf_seaside_links_v0": "golf_course_18_hole",
        "park_driving_range_single_tier_v0": "golf_driving_range",
        "park_multi_sport_track_field_v3": "multi_sport_complex",
        "park_retail_parking_landscaped_v1": "suburban_retail_parking_lot",
    }
    named_variant_parents = {
        "airport_airfield",
        "equestrian_center",
        "golf_course_18_hole",
        "golf_driving_range",
        "multi_sport_complex",
    }
    catalog = build_public_realm_capability_catalog(family_ids=list(expected))
    assert len(catalog.capabilities) == 10
    for capability in catalog.capabilities:
        archetype_id = expected[capability.family_id]
        expected_variants = {
            f"{archetype_id}_variant_{index}" if archetype_id in named_variant_parents else f"{archetype_id}_v{index}"
            for index in range(4)
        }
        assert {selection.variant_id for selection in capability.selections} == expected_variants
        assert {selection.archetype_id for selection in capability.selections} == {archetype_id}
        assert len({selection.appearance_kit_id for selection in capability.selections}) == 4
        assert len({selection.planting_structure for selection in capability.selections}) == 4
        assert all(selection.component_set_ids for selection in capability.selections)
        assert sum(selection.is_default for selection in capability.selections) == 1


def test_batch16_closes_twenty_nine_variants_across_ten_shared_families():
    expected = {
        "park_neighborhood_community": {"community_park": 4},
        "park_regional_english_landscape_v0": {"regional_park": 4},
        "park_dog_archetype_v0": {"dog_park": 4},
        "park_skate_archetype_v0": {"skate_park": 4},
        "park_sports_complex_tournament_v0": {"sports_field_complex": 4},
        "park_tennis_cluster_v0": {"tennis_court_cluster": 4},
        "park_cultural_gardens": {"botanical_garden": 3, "japanese_garden": 4},
        "park_memorial_garden_v0": {"memorial_garden": 4},
        "park_urban_forest": {"urban_forest": 4},
    }
    catalog = build_public_realm_capability_catalog(family_ids=list(expected))
    assert len(catalog.capabilities) == 9
    for capability in catalog.capabilities:
        for archetype_id, count in expected[capability.family_id].items():
            selections = [
                selection
                for selection in capability.selections
                if selection.archetype_id == archetype_id
            ]
            assert len(selections) == count
            assert len({selection.variant_id for selection in selections}) == count
            assert len({selection.appearance_kit_id for selection in selections}) == count
            assert len({selection.planting_structure for selection in selections}) == count
            assert all(selection.component_set_ids for selection in selections)


def test_batch16_dog_park_uses_a_whole_compact_program_on_smaller_parcels():
    geometry = _to_wgs84(box(700_000, 5_650_000, 700_040, 5_650_030))
    recipe = plan_public_realm_zone_recipe(
        "green_space",
        geometry,
        {
            "green_space_archetype_id": "dog_park",
            "green_space_selected_variant_id": "dog_park_v3",
        },
        strict=True,
    )
    assert recipe is not None
    assert recipe.family_id == "park_dog_archetype_v0"
    assert recipe.variant_id == "dog_park_v3"
    assert recipe.appearance_kit_id == "dog_park_v3_urban_contemporary_skin"


def test_batch17_closes_thirty_variants_across_ten_activity_families():
    expected = {
        "park_pickleball_community_v1": "pickleball_courts",
        "park_caged_soccer_v0": "soccer_pitch_caged",
        "park_track_oval_school_v2": "running_track_oval",
        "park_outdoor_fitness_v0": "outdoor_fitness_circuit",
        "park_baseball_club_hub_v1": "baseball_softball_diamond",
        "park_cricket_village_green_v0": "cricket_pitch_oval",
        "park_nature_play_v0": "nature_play_area",
        "park_inclusive_playground_v0": "inclusive_playground",
        "park_pump_track_v0": "pump_track",
        "park_splash_pad_v0": "splash_pad_area",
    }
    catalog = build_public_realm_capability_catalog(family_ids=list(expected))
    assert len(catalog.capabilities) == 10
    for capability in catalog.capabilities:
        archetype_id = expected[capability.family_id]
        selections = [
            selection
            for selection in capability.selections
            if selection.archetype_id == archetype_id
        ]
        assert len(selections) == 4
        assert {selection.variant_id for selection in selections} == {
            f"{archetype_id}_v{index}" for index in range(4)
        }
        assert len({selection.appearance_kit_id for selection in selections}) == 4
        assert len({selection.planting_structure for selection in selections}) == 4
        assert all(selection.component_set_ids for selection in selections)


def test_batch18_closes_thirty_variants_across_ten_specialty_families():
    expected = {
        "park_disc_golf_wooded_v0": "disc_golf_course",
        "park_bocce_piazza_v0": "bocce_petanque_court",
        "park_climbing_competition_v0": "climbing_bouldering_wall",
        "park_mini_golf_classic_v0": "mini_golf_course",
        "park_beach_volleyball_competition_v0": "beach_volleyball_courts",
        "park_pollinator_prairie_v0": "pollinator_meadow",
        "park_orchard_heritage_v0": "urban_orchard_food_forest",
        "park_bioswale_streetside_v0": "bioswale_rain_garden",
        "park_sculpture_museum_court_v0": "sculpture_garden",
        "park_labyrinth_classical_v0": "labyrinth_meditation",
    }
    catalog = build_public_realm_capability_catalog(family_ids=list(expected))
    assert len(catalog.capabilities) == 10
    for capability in catalog.capabilities:
        archetype_id = expected[capability.family_id]
        selections = [
            selection
            for selection in capability.selections
            if selection.archetype_id == archetype_id
        ]
        assert len(selections) == 4
        assert {selection.variant_id for selection in selections} == {
            f"{archetype_id}_v{index}" for index in range(4)
        }
        assert len({selection.appearance_kit_id for selection in selections}) == 4
        assert len({selection.planting_structure for selection in selections}) == 4
        assert all(selection.component_set_ids for selection in selections)


def test_batch19_closes_thirty_variants_across_ten_destination_families():
    expected = {
        "park_ice_rink_multipurpose_v3": "outdoor_ice_rink",
        "park_kayak_river_launch_v0": "kayak_launch_dock",
        "park_tidal_marsh_cordgrass_v0": "tidal_marsh_boardwalk",
        "park_cinema_lawn_projection_v1": "outdoor_cinema_lawn",
        "park_food_truck_permanent_v1": "food_truck_plaza",
        "park_great_lawn_v2": "festival_event_lawn",
        "park_campus_meadow_quad_v0": "campus_central_quad",
        "park_urban_beach_family_v2": "urban_beach",
        "park_velodrome_open_air_v0": "velodrome_cycling_track",
        "park_mtb_skills_dirt_v2": "mountain_bike_park",
    }
    catalog = build_public_realm_capability_catalog(family_ids=list(expected))
    assert len(catalog.capabilities) == 10
    for capability in catalog.capabilities:
        archetype_id = expected[capability.family_id]
        selections = [
            selection
            for selection in capability.selections
            if selection.archetype_id == archetype_id
        ]
        assert len(selections) == 4
        assert len({selection.variant_id for selection in selections}) == 4
        assert len({selection.appearance_kit_id for selection in selections}) == 4
        assert len({selection.planting_structure for selection in selections}) == 4
        assert all(selection.component_set_ids for selection in selections)


def test_batch19_compact_food_truck_popup_uses_its_own_site_envelope():
    recipe = plan_public_realm_recipe(PublicRealmPlanRequest(
        archetype_id="food_truck_plaza",
        variant_id="food_truck_plaza_v0",
        target=ParkPolygonTarget(width_m=39.723, depth_m=31.185, area_m2=1192.878),
    ))
    assert recipe.family_id == "park_food_truck_permanent_v1"
    assert recipe.variant_id == "food_truck_plaza_v0"
    assert recipe.appearance_kit_id == "food_truck_plaza_v0_industrial_popup_skin"
    assert recipe.target.area_m2 == 1192.878


def test_batch20_closes_thirty_variants_across_ten_ecological_and_civic_families():
    expected = {
        "park_water_ecology": ("riparian_buffer", "wetland_rain_garden"),
        "park_playground_adventure_v0": ("playground_adventure",),
        "park_amphitheater_lawn_v0": ("amphitheater_lawn",),
        "park_beer_garden_munich_v0": ("beer_garden",),
        "park_city_hall_modernist_fountain_v2": ("city_hall_government_plaza",),
        "park_sunken_courtyard_v0": ("sunken_plaza",),
        "park_cathedral_courtyard_fountain_v3": ("cathedral_religious_forecourt",),
        "park_cultural_museum_terrace_v0": ("cultural_institution_forecourt",),
        "park_terraced_cascade_v3": ("stepped_terraced_plaza",),
    }
    catalog = build_public_realm_capability_catalog(family_ids=list(expected))
    assert len(catalog.capabilities) == 9
    for capability in catalog.capabilities:
        for archetype_id in expected[capability.family_id]:
            selections = [
                selection
                for selection in capability.selections
                if selection.archetype_id == archetype_id
            ]
            assert len(selections) == 4
            assert {selection.variant_id for selection in selections} == {
                f"{archetype_id}_v{index}" for index in range(4)
            }
            assert len({selection.appearance_kit_id for selection in selections}) == 4
            assert len({selection.planting_structure for selection in selections}) == 4
            assert all(selection.component_set_ids for selection in selections)


@pytest.mark.parametrize(
    ("archetype_id", "variant_id"),
    [
        ("amsterdam_hofje_garden", "amsterdam_hofje_garden_v0"),
        ("amsterdam_plein", "amsterdam_plein_v0"),
        ("amsterdam_vondelpark", "amsterdam_vondelpark_v3"),
        ("barcelona_pati_interior", "barcelona_pati_interior_v0"),
        ("barcelona_placa_xamfra", "barcelona_placa_xamfra_v2"),
        ("barcelona_superilla", "barcelona_superilla_v1"),
        ("calgary_prairie_plaza", "calgary_prairie_plaza_v1"),
        ("calgary_princes_island", "calgary_princes_island_v0"),
        ("montreal_mount_royal", "montreal_mount_royal_v2"),
        ("montreal_square", "montreal_square_v3"),
    ],
)
def test_batch10_families_adapt_to_shared_compact_trial_polygon(archetype_id: str, variant_id: str):
    geometry = _to_wgs84(box(700_000, 5_650_000, 700_099, 5_650_000 + 37))
    recipe = plan_public_realm_zone_recipe(
        "green_space",
        geometry,
        {"green_space_archetype_id": archetype_id, "green_space_selected_variant_id": variant_id},
        strict=True,
    )
    assert recipe is not None
    assert recipe.variant_id == variant_id
    assert recipe.generator == "park_kit"
