"""Master Planner — spec validation/repair, palette conversion, and the
engine's execution of variety (band rotation, per-bar characters, landscape
structure stamping, single-block typology)."""

import math
from dataclasses import replace
from types import SimpleNamespace

import pytest
from geoalchemy2.shape import from_shape
from shapely.geometry import LineString, Point, Polygon, box, mapping
from shapely.ops import unary_union

from app.services.master_planner import agent as master_planner_agent
from app.services.master_planner.agent import compose_master_plan
from app.services.master_planner.lego_catalog import (
    LegoArchetypeCapability,
    LegoPlanningCatalog,
)
from app.services.master_planner.spec import (
    BandAlternate,
    BandPlan,
    LandscapePlan,
    MasterPlanSpec,
    OpenSpaceProgram,
    PlanDiversity,
    PublicRealmPlan,
    CENTRAL_PARK_IDS,
    LOCAL_STREET_IDS,
    SPINE_STREET_IDS,
    diversity_plan_for_site,
    lego_fallback_spec,
    palette_from_spec,
    validate_spec,
)
from app.services.plan_geometry.generator import (
    _lego_park_identity_for_metric_polygon,
    _safe_plan_centerline_coordinates,
    generate_plan_geometry,
    recover_street_plan_centerline_wgs84,
    validate_street_plan_centerline_wgs84,
)
from app.services.master_planner.lego_geometry import bind_building_zones_to_lego
from app.services.plan_geometry.archetypes import load_dims_table
from app.services.plan_geometry.placement import (
    PALETTES,
    BandSpec,
    BlockContext,
    Palette,
    palette_for,
    plan_blocks,
)
from app.services.plan_geometry.community_rules import resolve_rules
from app.services.planning_agents.schemas import PhilosophyWeights, ScenarioDefinition
from app.services.public_realm_lego import plan_public_realm_zone_recipe, public_realm_fallback_marker

LAT, LON = 51.0405, -114.0850
M_LAT = 111_320.0
M_LON = M_LAT * math.cos(math.radians(LAT))


def _offset(lon_m, lat_m):
    return (LON + lon_m / M_LON, LAT + lat_m / M_LAT)


def _site(width_m=700.0, depth_m=520.0) -> Polygon:
    return Polygon([_offset(0, 0), _offset(width_m, 0), _offset(width_m, depth_m), _offset(0, depth_m)])


def test_recovers_safe_centerline_metadata_for_a_locked_legacy_street():
    street = Polygon(
        [
            _offset(0, 28),
            _offset(146, 28),
            _offset(146, 44),
            _offset(0, 44),
        ]
    )
    centerline = recover_street_plan_centerline_wgs84(street)
    assert centerline and len(centerline) == 2
    line = LineString(centerline)
    assert line.difference(street.buffer(1e-10)).is_empty
    assert line.length > 0


def test_clipped_connector_drops_a_stale_authored_centerline():
    """Regression: the larger Richmond pilot emitted this unsafe wedge chord."""

    connector = Polygon(
        [
            (-114.11859769490745, 51.0268459660692),
            (-114.11862277673409, 51.026813439064156),
            (-114.11896783021396, 51.026843801813506),
            (-114.11936381335292, 51.027069447446394),
            (-114.11936377514687, 51.02708086993554),
        ]
    )
    stale_chord = [
        [-114.1187588195544, 51.026825410060816],
        [-114.11914146536746, 51.026942745455926],
    ]

    assert not validate_street_plan_centerline_wgs84(connector, stale_chord)
    assert _safe_plan_centerline_coordinates(connector, stale_chord) is None


def test_locked_street_centerline_backfill_invalidates_compiled_proof():
    from app.tasks.urban_dna import _backfill_locked_street_plan_centerline

    street = Polygon(
        [
            _offset(0, 28),
            _offset(146, 28),
            _offset(146, 44),
            _offset(0, 44),
        ]
    )
    zone = SimpleNamespace(
        geometry=from_shape(street, srid=4326),
        properties={
            "_plan_role": "street",
            "community_3d": {
                "state": "compiled",
                "source_hash": "a" * 64,
            },
        },
    )

    assert _backfill_locked_street_plan_centerline(zone) is True
    assert len(zone.properties["plan_centerline"]) == 2
    assert zone.properties["community_3d"]["state"] == "stale"
    assert "centerline recovered" in zone.properties["community_3d"]["stale_reason"]
    assert _backfill_locked_street_plan_centerline(zone) is False


PARAMS = {
    "streets.row_width_m": {"value": 16.0},
    "buildings.floors": {"value": 6},
    "landscape.tree_density": {"value": 0.6},
}


@pytest.mark.parametrize(
    ("summary", "scale", "building_characters", "park_characters", "street_characters"),
    [
        ({"area_m2": 8_000, "est_blocks": 1}, "compact", 1, 1, 1),
        ({"area_m2": 16_000, "est_blocks": 2}, "neighborhood", 2, 2, 2),
        ({"area_m2": 10_000, "est_blocks": 3}, "neighborhood", 2, 2, 2),
        ({"area_m2": 52_000, "est_blocks": 6}, "district", 3, 3, 3),
        ({"area_m2": 40_000, "est_blocks": 8}, "district", 3, 3, 3),
    ],
)
def test_site_diversity_contract_scales_with_area_or_block_capacity(
    summary,
    scale,
    building_characters,
    park_characters,
    street_characters,
):
    diversity = diversity_plan_for_site(summary)

    assert diversity.scale == scale
    assert diversity.building_characters_per_band == building_characters
    assert diversity.park_characters == park_characters
    assert diversity.street_characters == street_characters


def test_plan_redraw_deletes_only_derived_buildings_owned_by_replaced_zones():
    import uuid
    from unittest.mock import MagicMock

    from app.models.models import Building
    from app.tasks.urban_dna import _delete_community_3d_buildings_for_replaced_zones

    project_id = uuid.uuid4()
    replaced_zone_id = uuid.uuid4()
    retained_zone_id = uuid.uuid4()

    def _building(name, marker=None):
        specifications = {"legoAssembly": {"module_family": "fixture"}}
        if marker is not None:
            specifications["community3DRepresentation"] = marker
        return Building(
            id=uuid.uuid4(),
            project_id=project_id,
            name=name,
            specifications=specifications,
        )

    obsolete = _building(
        "obsolete",
        {
            "schema_version": 1,
            "zone_id": str(replaced_zone_id),
            "generator": "lego_assembly",
            "representation_hash": "a" * 64,
            "compiled_at": "2026-07-21T12:00:00+00:00",
        },
    )
    retained = _building(
        "retained",
        {
            "schema_version": 1,
            "zone_id": str(retained_zone_id),
            "generator": "lego_assembly",
            "representation_hash": "b" * 64,
            "compiled_at": "2026-07-21T12:00:00+00:00",
        },
    )
    unmarked = _building("user-authored")
    session = MagicMock()
    session.query.return_value.filter.return_value.all.return_value = [
        obsolete,
        retained,
        unmarked,
    ]

    removed = _delete_community_3d_buildings_for_replaced_zones(
        session,
        project_id,
        {replaced_zone_id},
    )

    assert removed == 1
    session.delete.assert_called_once_with(obsolete)


def _lego_catalog() -> LegoPlanningCatalog:
    capabilities = (
        LegoArchetypeCapability(
            parent_id="industrial_brick_mixed_use",
            title="Industrial Brick Mixed Use",
            development_type="mixed_use",
            aesthetic_category="industrial_brick",
            target_width_m=30,
            target_depth_m=20,
            selectable_ids=("industrial_brick_original_mill",),
            variant_ids=("industrial_brick_original_mill",),
            supported_floors=(4,),
            supported_floors_by_selectable_id={
                "industrial_brick_original_mill": (4,),
            },
            target_dimensions_by_selectable_id={
                "industrial_brick_original_mill": (30, 20),
            },
            families=("industrial-mill-fixed",),
        ),
        LegoArchetypeCapability(
            parent_id="parisian_boulevard_corner",
            title="Parisian Boulevard Corner",
            development_type="mixed_use",
            aesthetic_category="parisian",
            target_width_m=18,
            target_depth_m=18,
            selectable_ids=("parisian_boulevard_corner",),
            variant_ids=(),
            supported_floors=(5, 6),
            supported_floors_by_selectable_id={
                "parisian_boulevard_corner": (5, 6),
            },
            target_dimensions_by_selectable_id={
                "parisian_boulevard_corner": (18, 18),
            },
            families=("parisian-corner",),
        ),
    )
    return LegoPlanningCatalog(
        capabilities=capabilities,
        parent_ids=tuple(capability.parent_id for capability in capabilities),
        variants_by_parent={capability.parent_id: capability.variant_ids for capability in capabilities},
        supported_floors_by_parent={capability.parent_id: capability.supported_floors for capability in capabilities},
        supported_floors_by_selectable_id={
            selectable_id: floors
            for capability in capabilities
            for selectable_id, floors in capability.supported_floors_by_selectable_id.items()
        },
        target_dimensions_by_selectable_id={
            selectable_id: dimensions
            for capability in capabilities
            for selectable_id, dimensions in (capability.target_dimensions_by_selectable_id.items())
        },
        parent_by_selectable_id={
            selectable_id: capability.parent_id
            for capability in capabilities
            for selectable_id in capability.selectable_ids
        },
        prompt_vocabulary="Imported LEGO test vocabulary",
        fingerprint="test-catalog",
    )


def _spec(**overrides) -> MasterPlanSpec:
    base = MasterPlanSpec(
        design_narrative="A varied, walkable quarter.",
        layout_strategy="transect_green",
        curvilinear=False,
        laneways=True,
        bands={
            "core": BandPlan(
                development_type="residential_multifamily",
                aesthetic="contemporary_urban",
                floors=7,
                typology="perimeter_block",
                alternates=[BandAlternate(development_type="residential_multifamily", aesthetic="classical")],
            ),
            "frontage": BandPlan(
                development_type="mixed_use",
                aesthetic="parisian",
                floors=5,
                typology="perimeter_block",
                alternates=[BandAlternate(development_type="commercial_retail", aesthetic="historical")],
            ),
            "mid": BandPlan(
                development_type="residential_multifamily",
                aesthetic="scandinavian_nordic",
                floors=4,
                typology="row_bars",
                alternates=[BandAlternate(development_type="residential_duplex", aesthetic="brownstone_rowhouse")],
            ),
            "edge": BandPlan(
                development_type="residential_single_family",
                aesthetic="traditional_vernacular",
                floors=2,
                typology="row_bars",
            ),
            "anchor": BandPlan(
                development_type="institutional_education",
                aesthetic="collegiate_gothic",
                floors=4,
                typology="anchor_mass",
            ),
        },
        open_space=OpenSpaceProgram(
            water_feature=True,
            plaza=True,
            water_archetype_id="pond_lake",
            central_park_archetype_id="neighborhood_park",
        ),
        landscape=LandscapePlan(
            park_structure="naturalistic_grove", courtyard_structure="formal_quad", greenway_structure="formal_allee"
        ),
    )
    return base.model_copy(update=overrides)


# --- validation / repair ----------------------------------------------------------


def test_validate_repairs_bad_band_and_ids():
    spec = _spec()
    spec.bands["core"] = BandPlan(development_type="floating_sky_city", aesthetic="x", floors=99, typology="hoverdome")
    spec.spine_archetype_id = "totally_fake_street"
    spec.landscape.park_structure = "chaos_scatter"
    validated, notes = validate_spec(spec, "city_policy")
    codes = {n["code"] for n in notes}
    # Unknown dev type: band dropped (conversion re-fills from the preset).
    assert "core" not in validated.bands
    assert "MASTER_PLAN_BAND_REPAIRED" in codes
    assert validated.spine_archetype_id is None
    assert "MASTER_PLAN_ID_DROPPED" in codes
    assert validated.landscape.park_structure == "naturalistic_grove"
    assert "MASTER_PLAN_LANDSCAPE_REPAIRED" in codes


def test_validate_clamps_floors_and_keeps_good_bands():
    spec = _spec()
    spec.bands["mid"] = BandPlan(
        development_type="Residential Multifamily", aesthetic="Scandinavian Nordic", floors=99, typology="row_bars"
    )
    validated, _ = validate_spec(spec, "city_policy")
    band = validated.bands["mid"]
    assert band.development_type == "residential_multifamily"  # normalized
    assert band.floors == 40  # clamped, not rejected
    assert validated.bands["anchor"].development_type == "institutional_education"


def test_validate_clamps_block_target_grain():
    spec = _spec(block_target_m=30.0)  # below the 60 m floor
    validated, notes = validate_spec(spec, "city_policy")
    assert validated.block_target_m == 60.0
    assert any(n["code"] == "MASTER_PLAN_GRAIN_CLAMPED" for n in notes)
    # A sensible grain passes through untouched.
    ok, _ = validate_spec(_spec(block_target_m=95.0), "city_policy")
    assert ok.block_target_m == 95.0
    # Absent grain stays None (scenario default used).
    default, _ = validate_spec(_spec(), "city_policy")
    assert default.block_target_m is None


def test_validate_drops_catalog_less_alternates():
    spec = _spec()
    spec.bands["mid"].alternates.append(BandAlternate(development_type="unobtainium_towers"))
    validated, notes = validate_spec(spec, "city_policy")
    alt_types = [a.development_type for a in validated.bands["mid"].alternates]
    assert "unobtainium_towers" not in alt_types
    assert any(n["code"] == "MASTER_PLAN_ALTERNATE_DROPPED" for n in notes)


def test_lego_tool_schema_exposes_all_trusted_building_parents():
    catalog = _lego_catalog()
    tool = master_planner_agent._master_plan_tool(catalog)
    band_schemas = tool["input_schema"]["properties"]["bands"]["properties"]
    trusted_parent_ids = sorted(entry["id"] for entry in load_dims_table() if entry.get("usable"))

    for key in ("core", "frontage", "mid", "edge", "anchor"):
        schema = band_schemas[key]
        assert "archetype_id" in schema["required"]
        assert schema["properties"]["archetype_id"]["enum"] == trusted_parent_ids
        alternate = schema["properties"]["alternates"]["items"]
        assert "archetype_id" in alternate["required"]
        assert alternate["properties"]["archetype_id"]["enum"] == trusted_parent_ids


def test_lego_tool_schema_exposes_role_safe_public_realm_choices_with_optional_exact_variants():
    tool = master_planner_agent._master_plan_tool(_lego_catalog())
    schema = tool["input_schema"]
    properties = schema["properties"]

    assert "public_realm" in schema["required"]
    assert set(properties["spine_archetype_id"]["enum"]) == set(SPINE_STREET_IDS)
    assert set(properties["local_archetype_id"]["enum"]) == set(LOCAL_STREET_IDS)
    assert set(properties["open_space"]["properties"]["central_park_archetype_id"]["enum"]) == set(CENTRAL_PARK_IDS)
    assert properties["open_space"]["properties"]["water_archetype_id"]["enum"] == ["stormwater_retention_pond"]
    public_realm = properties["public_realm"]
    assert public_realm["required"] == []
    assert "main_street_complete_v3" in (public_realm["properties"]["spine_street_variant_id"]["enum"])

    legacy = master_planner_agent._master_plan_tool()
    assert "public_realm" not in legacy["input_schema"]["properties"]
    assert "public_realm" not in legacy["input_schema"]["required"]


def test_lego_validation_preserves_known_family_pending_public_realm_identity():
    raw = _spec(
        spine_archetype_id="haussmann_boulevard",
        local_archetype_id="london_terrace_street",
        open_space=OpenSpaceProgram(
            water_feature=True,
            water_archetype_id="pond_lake",
            plaza=True,
            central_park_archetype_id="london_garden_square",
        ),
        public_realm=PublicRealmPlan(
            spine_street_variant_id="haussmann_boulevard_v2",
            local_street_variant_id="london_terrace_street_v1",
            central_park_variant_id="london_garden_square_v3",
            pocket_park_variant_id="not_a_variant",
            courtyard_variant_id="urban_pocket_park_v3",
            greenway_variant_id="linear_park_greenway_v0",
        ),
    )

    validated, notes = validate_spec(
        raw,
        "city_policy",
        lego_catalog=_lego_catalog(),
    )

    assert validated.spine_archetype_id == "haussmann_boulevard"
    assert validated.local_archetype_id == "london_terrace_street"
    assert validated.open_space.central_park_archetype_id == "london_garden_square"
    assert validated.open_space.water_archetype_id == "pond_lake"
    assert validated.public_realm == PublicRealmPlan(
        spine_street_variant_id="haussmann_boulevard_v2",
        local_street_variant_id="london_terrace_street_v1",
        central_park_variant_id="london_garden_square_v3",
        pocket_park_variant_id="urban_pocket_park_v0",
        courtyard_variant_id="urban_pocket_park_v3",
        greenway_variant_id="linear_park_greenway_v0",
    )
    assert any(note["code"] == "MASTER_PLAN_PUBLIC_REALM_VARIANT_REPAIRED" for note in notes)
    assert not any(note["code"] == "MASTER_PLAN_PUBLIC_REALM_ARCHETYPE_REPAIRED" for note in notes)

    palette = palette_from_spec(
        validated,
        "city_policy",
        lego_catalog=_lego_catalog(),
    )
    assert palette.public_realm_variants == {
        "spine": "haussmann_boulevard_v2",
        "local": "london_terrace_street_v1",
        "central": "london_garden_square_v3",
        "pocket": "urban_pocket_park_v0",
        "courtyard": "urban_pocket_park_v3",
        "greenway": "linear_park_greenway_v0",
        "plaza": "formal_civic_plaza_v0",
        "pond": "stormwater_retention_pond_v0",
        "path": "multi_use_trail_v1",
        "lane": "toronto_laneway_v0",
        "roundabout": "roundabout_v0",
    }


def test_family_pending_ai_public_realm_ids_reach_generated_zone_properties_unchanged():
    raw = _spec(
        spine_archetype_id="scenic_parkway",
        open_space=OpenSpaceProgram(
            central_park_archetype_id="london_garden_square",
        ),
        public_realm=PublicRealmPlan(
            spine_street_variant_id="scenic_parkway_v3",
            central_park_variant_id="london_garden_square_v2",
        ),
    )
    validated, _ = validate_spec(raw, "city_policy", lego_catalog=_lego_catalog())
    palette = palette_from_spec(validated, "city_policy", lego_catalog=_lego_catalog())
    result = generate_plan_geometry(
        site_polygon_wgs84=_site(),
        scenario_id="city_policy",
        scenario_label="Family Pending",
        parameters=PARAMS,
        road_features=[],
        district_features=[],
        palette_override=palette,
    )

    spine_zones = [
        zone
        for zone in result.zones
        if zone["zone_type"] == "road" and zone["properties"].get("street_role") == "spine"
    ]
    assert spine_zones
    assert all(zone["properties"]["road_archetype_id"] == "scenic_parkway" for zone in spine_zones)
    assert all(zone["properties"]["road_selected_variant_id"] == "scenic_parkway_v3" for zone in spine_zones)
    central_zones = [zone for zone in result.zones if zone["properties"].get("green_kind") == "central"]
    assert central_zones
    assert all(zone["properties"]["green_space_archetype_id"] == "london_garden_square" for zone in central_zones)
    assert all(
        zone["properties"]["green_space_selected_variant_id"] == "london_garden_square_v2" for zone in central_zones
    )


def test_explicit_unbuilt_ai_building_survives_spec_geometry_and_binder_as_itself():
    raw = _spec()
    raw.bands = {
        key: BandPlan(
            development_type="commercial_light",
            aesthetic="art_deco",
            floors=3,
            typology="row_bars",
            archetype_id="deco_theater_mainstreet",
            variant_id="deco_theater_streamline",
        )
        for key in ("core", "frontage", "mid", "edge", "anchor")
    }
    validated, notes = validate_spec(raw, "city_policy", lego_catalog=_lego_catalog())
    mid = validated.bands["mid"]
    assert mid.archetype_id == "deco_theater_mainstreet"
    assert mid.variant_id == "deco_theater_streamline"
    assert mid.floors == 3
    assert any(note["code"] == "MASTER_PLAN_LEGO_FAMILY_PENDING" for note in notes)

    palette = palette_from_spec(validated, "city_policy", lego_catalog=_lego_catalog())
    assert "deco_theater_mainstreet" in palette.family_pending_archetype_ids
    result = generate_plan_geometry(
        site_polygon_wgs84=_site(140, 120),
        scenario_id="city_policy",
        scenario_label="Pending Building",
        parameters=PARAMS,
        road_features=[],
        district_features=[],
        palette_override=palette,
    )
    source_buildings = [
        zone for zone in result.zones if zone["properties"].get("development_archetype_id") == "deco_theater_mainstreet"
    ]
    assert source_buildings
    assert all(zone["properties"]["floors"] == 3 for zone in source_buildings)
    rebound, report = bind_building_zones_to_lego(source_buildings, [], _lego_catalog())
    assert report.fallback_count == len(source_buildings)
    assert all(zone["properties"]["development_archetype_id"] == "deco_theater_mainstreet" for zone in rebound)
    assert all(zone["properties"]["_lego_family_pending"] is True for zone in rebound)


def test_lego_validation_fills_missing_bands_but_preserves_explicit_pending_parent():
    raw = MasterPlanSpec(
        design_narrative="A partial response that must be made executable.",
        bands={
            "mid": BandPlan(
                development_type="mixed_use",
                aesthetic="industrial_brick",
                floors=11,
                typology="row_bars",
                archetype_id="industrial_brick_mixed_use",
                alternates=[
                    BandAlternate(
                        development_type="invented_type",
                        aesthetic="invented_style",
                        archetype_id="invented_archetype",
                    )
                ],
            )
        },
    )

    validated, notes = validate_spec(
        raw,
        "city_policy",
        lego_catalog=_lego_catalog(),
    )

    assert set(validated.bands) == {"core", "frontage", "mid", "edge", "anchor"}
    allowed = set(_lego_catalog().parent_ids)
    assert all(band.archetype_id in allowed for band in validated.bands.values())
    mid = validated.bands["mid"]
    assert mid.archetype_id == "industrial_brick_mixed_use"
    assert mid.variant_id is None
    assert mid.floors == 11
    assert not mid.alternates
    assert any(note["code"] == "MASTER_PLAN_LEGO_BAND_FILLED" for note in notes)
    assert any(note["code"] == "MASTER_PLAN_LEGO_FLOORS_SNAPPED" for note in notes)
    assert any(note["code"] == "MASTER_PLAN_LEGO_FAMILY_PENDING" for note in notes)


def test_neighborhood_diversity_contract_fills_missing_lego_alternates():
    base_catalog = _lego_catalog()
    industrial = replace(
        base_catalog.capabilities[0],
        supported_floors=(4, 5),
        supported_floors_by_selectable_id={"industrial_brick_original_mill": (4, 5)},
    )
    catalog = replace(
        base_catalog,
        capabilities=(industrial, base_catalog.capabilities[1]),
        supported_floors_by_parent={
            "industrial_brick_mixed_use": (4, 5),
            "parisian_boulevard_corner": (5, 6),
        },
        supported_floors_by_selectable_id={
            "industrial_brick_original_mill": (4, 5),
            "parisian_boulevard_corner": (5, 6),
        },
    )
    raw = MasterPlanSpec(
        diversity=PlanDiversity(
            scale="neighborhood",
            building_characters_per_band=2,
            park_characters=2,
            street_characters=2,
            max_repeat_share=0.7,
        ),
        bands={
            key: BandPlan(
                development_type="mixed_use",
                aesthetic="industrial_brick",
                floors=5,
                typology="perimeter_block",
                archetype_id="parisian_boulevard_corner",
            )
            for key in ("core", "frontage", "mid", "edge", "anchor")
        },
    )

    validated, notes = validate_spec(
        raw,
        "city_policy",
        lego_catalog=catalog,
    )

    for band in validated.bands.values():
        parent_ids = {band.archetype_id, *(alternate.archetype_id for alternate in band.alternates)}
        assert parent_ids == {"industrial_brick_mixed_use", "parisian_boulevard_corner"}
    assert any(note["code"] == "MASTER_PLAN_DIVERSITY_FILLED" for note in notes)


def test_lego_palette_carries_pending_parent_and_runtime_limits_without_substitution():
    catalog = _lego_catalog()
    raw = MasterPlanSpec(
        bands={
            key: BandPlan(
                development_type="mixed_use",
                aesthetic="industrial_brick",
                floors=4,
                typology="row_bars",
                archetype_id="industrial_brick_mixed_use",
                alternates=[
                    BandAlternate(
                        development_type="mixed_use",
                        aesthetic="parisian",
                        archetype_id="parisian_boulevard_corner",
                    )
                ],
            )
            for key in ("core", "frontage", "mid", "edge", "anchor")
        }
    )

    palette = palette_from_spec(raw, "city_policy", lego_catalog=catalog)

    assert palette.bands["mid"].variant_id is None
    assert "industrial_brick_mixed_use" in palette.family_pending_archetype_ids
    assert "mid" not in palette.alternates
    assert palette.allowed_archetype_ids == frozenset(catalog.parent_ids)
    assert palette.allowed_variant_ids_by_archetype == catalog.variants_by_parent
    assert palette.supported_floors_by_selectable_id == {
        "industrial_brick_original_mill": (4,),
        "parisian_boulevard_corner": (5, 6),
    }
    assert palette.target_dimensions_by_selectable_id == catalog.target_dimensions_by_selectable_id


def test_lego_fallback_spec_is_complete_and_deterministic():
    catalog = _lego_catalog()

    first = lego_fallback_spec("city_policy", catalog)
    second = lego_fallback_spec("city_policy", catalog)

    assert first == second
    assert set(first.bands) == {"core", "frontage", "mid", "edge", "anchor"}
    assert all(band.archetype_id in catalog.parent_ids for band in first.bands.values())
    assert all(
        int(band.floors) in catalog.supported_floors_by_selectable_id[band.variant_id or band.archetype_id]
        for band in first.bands.values()
    )


def test_neighborhood_palette_rotates_compatible_public_realm_variants():
    catalog = _lego_catalog()
    spec = lego_fallback_spec(
        "city_policy",
        catalog,
        site_summary={"area_m2": 20_000, "est_blocks": 4},
    )

    palette = palette_from_spec(spec, "city_policy", lego_catalog=catalog)

    assert spec.diversity.scale == "neighborhood"
    cycle_lengths = []
    for role in ("spine", "local", "central", "pocket", "courtyard", "greenway"):
        cycle = palette.public_realm_variant_cycles[role]
        assert cycle[0] == palette.public_realm_variants[role]
        assert 1 <= len(cycle) <= 2
        cycle_lengths.append(len(cycle))
    assert 2 in cycle_lengths, "installed multi-variant roles should use the neighborhood target"


def test_plan_blocks_cannot_escape_or_mispair_the_validated_lego_identity():
    catalog = _lego_catalog()
    raw = MasterPlanSpec(
        bands={
            key: BandPlan(
                development_type="mixed_use",
                aesthetic="industrial_brick",
                floors=19,
                typology="row_bars",
                archetype_id="industrial_brick_mixed_use",
            )
            for key in ("core", "frontage", "mid", "edge", "anchor")
        }
    )
    palette = palette_from_spec(raw, "city_policy", lego_catalog=catalog)
    context = BlockContext(
        index=0,
        area_m2=4_000,
        dist_to_centroid_m=0,
        dist_to_edge_m=0,
        transect=0,
        fronts_spine=False,
        touches_boundary=True,
        dist_to_green_m=math.inf,
        abuts_low_rise=False,
        ceiling_floors=None,
    )

    plan = plan_blocks(
        contexts=[context],
        palette=palette,
        rules=resolve_rules("city_policy", PARAMS),
        base_type=None,
        base_aesthetic=None,
    )[0]

    assert plan.archetype_id == "industrial_brick_mixed_use"
    assert plan.variant_id is None
    assert plan.floors_target == 19
    assert plan.archetype_id in palette.family_pending_archetype_ids


@pytest.mark.asyncio
async def test_compose_failure_returns_lego_constrained_fallback(monkeypatch):
    class FailingMessages:
        async def create(self, **_kwargs):
            raise RuntimeError("provider unavailable")

    class FailingClient:
        messages = FailingMessages()

        async def close(self):
            return None

    monkeypatch.setattr(
        master_planner_agent.anthropic,
        "AsyncAnthropic",
        lambda **_kwargs: FailingClient(),
    )
    definition = ScenarioDefinition(
        scenario_id="city_policy",
        label="City Policy",
        philosophy=PhilosophyWeights(primary="balanced"),
    )

    spec, usage, notes = await compose_master_plan(
        dna_json={},
        definition=definition,
        site_summary={"area_m2": 12_000, "est_blocks": 3},
        api_key="test",
        model="test-model",
        lego_catalog=_lego_catalog(),
    )

    assert spec is not None
    assert set(spec.bands) == {"core", "frontage", "mid", "edge", "anchor"}
    assert spec.diversity.scale == "neighborhood"
    assert spec.diversity.building_characters_per_band == 2
    assert usage["status"] == "error"
    assert any(note["code"] == "MASTER_PLANNER_LEGO_FALLBACK" for note in notes)


# --- palette conversion -----------------------------------------------------------


def test_palette_from_spec_maps_bands_and_fallbacks():
    spec, _ = validate_spec(_spec(), "city_policy")
    # This test exercises conversion, not cross-family coherence. Validation
    # correctly drops the intentionally New York duplex alternate from the
    # inferred Calgary family, so insert a validated-shape alternate here to
    # prove palette_from_spec preserves the raw triple for final-floor lookup.
    spec.bands["mid"].alternates = [
        BandAlternate(development_type="residential_duplex", aesthetic="brownstone_rowhouse")
    ]
    del spec.bands["edge"]  # simulate a band the planner failed to author
    palette = palette_from_spec(spec, "city_policy")
    assert palette.bands["core"].floors_abs == 7.0
    assert palette.bands["core"].floors_delta is None
    assert palette.bands["mid"].typology == "row_bars"
    # Missing band keeps the preset BandSpec (relative floors intact).
    assert palette.bands["edge"] is PALETTES["city_policy"].bands["edge"]
    assert palette.alternates["mid"] == (("residential_duplex", "brownstone_rowhouse", None),)
    assert palette.landscape["courtyard"] == "formal_quad"
    assert palette.central_archetype_id == "neighborhood_park"
    assert palette.water_archetype_id == "pond_lake"
    assert palette.laneways is True


# --- band rotation + per-bar options ----------------------------------------------


def _mid_context(index: int) -> BlockContext:
    return BlockContext(
        index=index,
        area_m2=8000.0,
        dist_to_centroid_m=50.0,
        dist_to_edge_m=100.0,
        transect=0.5,
        fronts_spine=False,
        touches_boundary=False,
        dist_to_green_m=math.inf,
        abuts_low_rise=False,
        ceiling_floors=None,
    )


def test_plan_blocks_rotates_band_alternates_across_blocks():
    rules, _ = resolve_rules("city_policy", PARAMS)
    palette = replace(
        palette_for("city_policy"),
        alternates={
            "mid": (("residential_multifamily", "scandinavian_nordic", None), ("mixed_use", "contemporary_urban", None))
        },
    )
    contexts = [_mid_context(i) for i in range(4)]
    plans = plan_blocks(contexts=contexts, palette=palette, rules=rules, base_type=None, base_aesthetic=None)
    combos = {(p.development_type, p.aesthetic) for p in plans.values()}
    assert len(combos) >= 2, f"rotation produced a monoculture: {combos}"
    # Rotation is deterministic: same inputs, same assignment.
    again = plan_blocks(contexts=contexts, palette=palette, rules=rules, base_type=None, base_aesthetic=None)
    assert {i: (p.development_type, p.aesthetic) for i, p in plans.items()} == {
        i: (p.development_type, p.aesthetic) for i, p in again.items()
    }


def test_plan_blocks_resolves_width_compatible_bar_options():
    rules, _ = resolve_rules("city_policy", PARAMS)
    palette = replace(
        palette_for("city_policy"),
        alternates={
            "mid": (("residential_multifamily", "classical", None), ("residential_multifamily", "mediterranean", None))
        },
    )
    plans = plan_blocks(contexts=[_mid_context(0)], palette=palette, rules=rules, base_type=None, base_aesthetic=None)
    plan = plans[0]
    assert plan.bar_options, "expected variant + alternate bar options"
    # Variant options lead: same archetype as the primary, distinct variant ids.
    variant_opts = [o for o in plan.bar_options if o.archetype_id == plan.archetype_id]
    assert variant_opts, "primary archetype's variants missing from bar options"
    assert len({o.variant_id for o in variant_opts}) == len(variant_opts)
    # Cross-archetype alternates that survived the width filter are resolved.
    alt_opts = [o for o in plan.bar_options if o.archetype_id != plan.archetype_id]
    assert all(o.archetype_id for o in alt_opts)


def test_runtime_bar_options_require_exact_rotatable_fit_and_floor_support():
    rules, _ = resolve_rules("economic", PARAMS)
    primary_parent = "rndsqr_terraced_mixed_use_midrise"
    primary_variant = "rndsqr_midrise_courtyard"
    rotated_variant = "rndsqr_midrise_terraced_garden"
    boundary_variant = "rndsqr_midrise_heritage_integrated"
    wrong_floor_variant = "rndsqr_midrise_inverted_rooftop_townhomes"
    compatible_parent = "minimalist_courtyard_block"
    incompatible_parent = "contemporary_townhouse_courtyard"
    primary_band = BandSpec(
        development_type="mixed_use",
        aesthetic="contemporary_urban",
        floors_delta=None,
        floors_abs=4.0,
        typology="perimeter_block",
        archetype_id=primary_parent,
        variant_id=primary_variant,
    )
    palette = Palette(
        bands={key: primary_band for key in ("core", "frontage", "mid", "edge", "anchor")},
        alternates={
            "mid": (
                (
                    "residential_multifamily",
                    "minimalist",
                    compatible_parent,
                    None,
                ),
                (
                    "residential_duplex",
                    "contemporary_urban",
                    incompatible_parent,
                    None,
                ),
            ),
        },
        allowed_archetype_ids=frozenset(
            {
                primary_parent,
                compatible_parent,
                incompatible_parent,
            }
        ),
        allowed_variant_ids_by_archetype={
            primary_parent: (
                primary_variant,
                rotated_variant,
                boundary_variant,
                wrong_floor_variant,
            ),
            compatible_parent: (),
            incompatible_parent: (),
        },
        supported_floors_by_selectable_id={
            primary_variant: (4,),
            rotated_variant: (4,),
            boundary_variant: (4,),
            wrong_floor_variant: (5,),
            compatible_parent: (4,),
            incompatible_parent: (4,),
        },
        target_dimensions_by_selectable_id={
            primary_variant: (25.0, 18.0),
            # Exact quarter-turn of the primary cell: valid.
            rotated_variant: (18.0, 25.0),
            # 0.833 x 0.818: inside the planner's raw 0.80 floor, but outside
            # the runtime safety margin that absorbs WGS remeasurement drift.
            boundary_variant: (30.0, 22.0),
            wrong_floor_variant: (25.0, 18.0),
            compatible_parent: (24.0, 18.0),
            incompatible_parent: (15.0, 8.0),
        },
    )

    plan = plan_blocks(
        contexts=[_mid_context(0)],
        palette=palette,
        rules=rules,
        base_type=None,
        base_aesthetic=None,
    )[0]
    identities = {(option.archetype_id, option.variant_id) for option in plan.bar_options}

    assert identities == {
        (primary_parent, rotated_variant),
        (compatible_parent, None),
    }


def test_presets_rotate_variants_not_archetypes():
    rules, _ = resolve_rules("city_policy", PARAMS)
    contexts = [_mid_context(i) for i in range(3)]
    plans = plan_blocks(
        contexts=contexts, palette=palette_for("city_policy"), rules=rules, base_type=None, base_aesthetic=None
    )
    combos = {(p.development_type, p.aesthetic) for p in plans.values()}
    assert len(combos) == 1  # presets keep their single-character bands
    # Fine-grain variety now comes from the archetype's OWN variants: every
    # bar option shares the primary archetype, differing only by variant.
    for p in plans.values():
        assert all(o.archetype_id == p.archetype_id for o in p.bar_options)
        assert all(o.variant_id for o in p.bar_options)


# --- engine integration -----------------------------------------------------------


def test_generated_plan_carries_variety_and_landscape():
    spec, _ = validate_spec(_spec(), "city_policy")
    palette = palette_from_spec(spec, "city_policy")
    result = generate_plan_geometry(
        site_polygon_wgs84=_site(),
        scenario_id="city_policy",
        scenario_label="MP",
        parameters=PARAMS,
        road_features=[],
        district_features=[],
        palette_override=palette,
    )
    buildings = [z for z in result.zones if z["properties"].get("_plan_role") == "building"]
    assert buildings
    combos = {(z["properties"]["development_type"], z["properties"]["development_aesthetic"]) for z in buildings}
    assert len(combos) >= 2, f"plan is a monoculture: {combos}"

    greens = [z for z in result.zones if z["properties"].get("_plan_role") == "open_space"]
    planted = [z for z in greens if z["properties"].get("green_kind") != "pond"]
    assert planted
    assert all(z["properties"].get("planting_structure") for z in planted)

    courtyards = [z for z in result.zones if z["properties"].get("_plan_role") == "courtyard"]
    for z in courtyards:
        assert z["properties"]["planting_structure"] == "formal_quad"


def test_generated_lego_plan_stamps_public_realm_variant_identity_by_role():
    variants = {
        "spine": "main_street_complete_v2",
        "local": "narrow_residential_street_v3",
        "central": "neighborhood_park_v1",
        "pocket": "urban_pocket_park_v2",
        "courtyard": "urban_pocket_park_v3",
        "greenway": "linear_park_greenway_v0",
        "plaza": "formal_civic_plaza_v0",
        "pond": "stormwater_retention_pond_v0",
        "path": "multi_use_trail_v1",
        "lane": "toronto_laneway_v0",
        "roundabout": "roundabout_v0",
    }
    palette = replace(
        palette_for("environmental"),
        spine_archetype_id="main_street_complete",
        local_archetype_id="narrow_residential_street",
        central_archetype_id="neighborhood_park",
        water_archetype_id="stormwater_retention_pond",
        public_realm_variants=variants,
    )
    result = generate_plan_geometry(
        site_polygon_wgs84=_site(),
        scenario_id="environmental",
        scenario_label="Public Realm LEGO",
        parameters={**PARAMS, "streets.row_width_m": {"value": 28.0}},
        road_features=[],
        district_features=[],
        palette_override=palette,
    )

    assert result.rules["spine_row_width_m"] == 18.0
    assert result.rules["local_row_width_m"] == 14.0
    assert any(note["code"] == "PUBLIC_REALM_LEGO_NATIVE_STREET_WIDTHS" for note in result.notes)

    expected_road_variants = {
        "spine": variants["spine"],
        "local": variants["local"],
        "path": variants["path"],
        "lane": variants["lane"],
        "roundabout": variants["roundabout"],
    }
    roads = [zone for zone in result.zones if zone["zone_type"] == "road"]
    assert roads
    spine_centerlines = []
    for zone in roads:
        role = zone["properties"].get("street_role")
        if role in expected_road_variants:
            assert zone["properties"].get("road_selected_variant_id") == (expected_road_variants[role])
        if role == "spine":
            assert zone["properties"]["width"] == 18.0
            centerline = zone["properties"].get("plan_centerline")
            assert centerline and len(centerline) >= 2
            source_line = LineString(centerline)
            zone_polygon = Polygon(zone["coordinates"])
            assert source_line.difference(zone_polygon.buffer(1e-10)).is_empty
            spine_centerlines.append(source_line)
        if role == "local":
            assert zone["properties"]["width"] == 14.0
    assert spine_centerlines

    expected_green_variants = {
        "central": variants["central"],
        "pocket": variants["pocket"],
        "greenway": variants["greenway"],
        "plaza": variants["plaza"],
        "pond": variants["pond"],
    }
    greens = [zone for zone in result.zones if zone["properties"].get("_plan_role") == "open_space"]
    assert greens
    for zone in greens:
        kind = zone["properties"]["green_kind"]
        assert zone["properties"].get("green_space_selected_variant_id") == (expected_green_variants[kind])

    courtyards = [zone for zone in result.zones if zone["properties"].get("_plan_role") == "courtyard"]
    assert all(
        zone["properties"].get("green_space_selected_variant_id") == variants["courtyard"] for zone in courtyards
    )


def test_large_lego_plan_rotates_compatible_local_street_and_courtyard_appearances():
    variants = {
        "spine": "main_street_complete_v0",
        "local": "narrow_residential_street_v0",
        "central": "neighborhood_park_v0",
        "pocket": "urban_pocket_park_v0",
        "courtyard": "urban_pocket_park_v0",
        "greenway": "linear_park_greenway_v0",
        "plaza": "formal_civic_plaza_v0",
        "pond": "stormwater_retention_pond_v0",
        "path": "multi_use_trail_v1",
        "lane": "toronto_laneway_v0",
        "roundabout": "roundabout_v0",
    }
    palette = replace(
        palette_for("city_policy"),
        spine_archetype_id="main_street_complete",
        local_archetype_id="narrow_residential_street",
        central_archetype_id="neighborhood_park",
        water_archetype_id="stormwater_retention_pond",
        public_realm_variants=variants,
        public_realm_variant_cycles={
            "local": ("narrow_residential_street_v0", "narrow_residential_street_v2"),
            "pocket": ("urban_pocket_park_v0", "urban_pocket_park_v2"),
            "courtyard": ("urban_pocket_park_v0", "urban_pocket_park_v2"),
        },
    )

    result = generate_plan_geometry(
        site_polygon_wgs84=_site(),
        scenario_id="city_policy",
        scenario_label="Varied Public Realm LEGO",
        parameters=PARAMS,
        road_features=[],
        district_features=[],
        palette_override=palette,
    )

    local_variants = {
        zone["properties"].get("road_selected_variant_id")
        for zone in result.zones
        if zone["zone_type"] == "road" and zone["properties"].get("street_role") == "local"
    }
    courtyard_variants = {
        zone["properties"].get("green_space_selected_variant_id")
        for zone in result.zones
        if zone["properties"].get("_plan_role") == "courtyard"
    }
    assert local_variants == {"narrow_residential_street_v0", "narrow_residential_street_v2"}
    assert courtyard_variants == {"urban_pocket_park_v0", "urban_pocket_park_v2"}


@pytest.mark.parametrize(
    ("scenario_id", "width_m", "depth_m"),
    [
        ("economic", 700.0, 520.0),
        ("city_policy", 700.0, 520.0),
        ("environmental", 700.0, 520.0),
        ("economic", 146.0, 72.0),
        ("city_policy", 146.0, 72.0),
        ("environmental", 146.0, 72.0),
        ("city_policy", 400.0, 100.0),
        ("economic", 1_600.0, 1_000.0),
    ],
)
def test_every_generated_lego_public_realm_zone_compiles_or_has_trusted_fallback(
    scenario_id,
    width_m,
    depth_m,
):
    """The AI vocabulary and geometry emitter form one executable contract."""

    lego_catalog = _lego_catalog()
    spec = lego_fallback_spec(scenario_id, lego_catalog)
    palette = palette_from_spec(
        spec,
        scenario_id,
        lego_catalog=lego_catalog,
    )
    result = generate_plan_geometry(
        site_polygon_wgs84=_site(width_m, depth_m),
        scenario_id=scenario_id,
        scenario_label=f"LEGO contract {scenario_id}",
        parameters=PARAMS,
        road_features=[],
        district_features=[],
        palette_override=palette,
    )
    public_realm = [zone for zone in result.zones if zone["zone_type"] in {"green_space", "road"}]
    assert public_realm

    failures: list[str] = []
    for zone in public_realm:
        try:
            if zone["zone_type"] == "road" and "plan_centerline" in zone["properties"]:
                assert validate_street_plan_centerline_wgs84(
                    Polygon(zone["coordinates"]),
                    zone["properties"]["plan_centerline"],
                )
            recipe = plan_public_realm_zone_recipe(
                zone["zone_type"],
                Polygon(zone["coordinates"]),
                zone["properties"],
                strict=True,
            )
            assert recipe is not None
        except (AssertionError, TypeError, ValueError) as exc:
            if public_realm_fallback_marker(zone["zone_type"], zone["properties"]) is None:
                failures.append(f"{zone['name']}: {exc}")
    assert failures == []


def test_lego_context_connectors_keep_their_executable_metric_sections():
    """Frontage links must enter the site, not become half-width edge bands."""

    lego_catalog = _lego_catalog()
    spec = lego_fallback_spec("economic", lego_catalog)
    palette = palette_from_spec(
        spec,
        "economic",
        lego_catalog=lego_catalog,
    )
    frontage_road = {
        "geometry": mapping(LineString([_offset(-20, -15), _offset(520, -15)])),
        "properties": {"road_type": "residential", "name": "Context Street"},
    }
    frontage_path = {
        "geometry": mapping(LineString([_offset(65, -12), _offset(95, -12)])),
        "properties": {"asset_type": "multi use pathway"},
    }

    result = generate_plan_geometry(
        site_polygon_wgs84=_site(500.0, 340.0),
        scenario_id="economic",
        scenario_label="LEGO frontage contract",
        parameters=PARAMS,
        road_features=[frontage_road],
        path_features=[frontage_path],
        district_features=[],
        palette_override=palette,
    )
    context_zones = [zone for zone in result.zones if zone["properties"].get("context_connection") is True]

    assert {zone["properties"].get("street_role") for zone in context_zones} == {
        "local",
        "path",
    }
    for zone in context_zones:
        recipe = plan_public_realm_zone_recipe(
            zone["zone_type"],
            Polygon(zone["coordinates"]),
            zone["properties"],
            strict=True,
        )
        assert recipe is not None
        assert recipe.target.row_width_m == zone["properties"]["width"]


def test_locked_lego_street_area_keeps_exact_calgary_local_contract():
    lego_catalog = _lego_catalog()
    base = lego_fallback_spec("city_policy", lego_catalog)
    spec = base.model_copy(
        update={
            "local_archetype_id": "calgary_local",
            "public_realm": base.public_realm.model_copy(
                update={
                    "local_street_variant_id": "calgary_local_v0",
                }
            ),
        }
    )
    palette = palette_from_spec(
        spec,
        "city_policy",
        lego_catalog=lego_catalog,
    )
    locked_street = Polygon(
        [
            _offset(0, 28),
            _offset(146, 28),
            _offset(146, 44),
            _offset(0, 44),
        ]
    )
    result = generate_plan_geometry(
        site_polygon_wgs84=_site(146, 72),
        scenario_id="city_policy",
        scenario_label="Locked LEGO",
        parameters=PARAMS,
        road_features=[],
        district_features=[],
        locked_street_area_wgs84=locked_street,
        palette_override=palette,
    )

    assert result.rules["local_row_width_m"] == 16.0
    roads = [zone for zone in result.zones if zone["zone_type"] == "road"]
    assert roads
    for zone in roads:
        assert zone["properties"]["width"] == 16.0
        assert zone["properties"]["road_archetype_id"] == "calgary_local"
        assert zone["properties"]["road_selected_variant_id"] == "calgary_local_v0"
        centerline = zone["properties"].get("plan_centerline")
        assert centerline and len(centerline) == 2
        source_line = LineString(centerline)
        zone_polygon = Polygon(zone["coordinates"])
        assert source_line.difference(zone_polygon.buffer(1e-10)).is_empty
        assert source_line.length > 0
        assert (
            plan_public_realm_zone_recipe(
                zone["zone_type"],
                Polygon(zone["coordinates"]),
                zone["properties"],
                strict=True,
            )
            is not None
        )


def test_locked_18m_street_prefers_exact_native_spine_over_local_overlap():
    lego_catalog = _lego_catalog()
    base = lego_fallback_spec("city_policy", lego_catalog)
    spec = base.model_copy(
        update={
            "local_archetype_id": "calgary_local",
            "public_realm": base.public_realm.model_copy(
                update={
                    "local_street_variant_id": "calgary_local_v0",
                }
            ),
        }
    )
    palette = palette_from_spec(
        spec,
        "city_policy",
        lego_catalog=lego_catalog,
    )
    locked_street = Polygon(
        [
            _offset(0, 27),
            _offset(146, 27),
            _offset(146, 45),
            _offset(0, 45),
        ]
    )
    result = generate_plan_geometry(
        site_polygon_wgs84=_site(146, 72),
        scenario_id="city_policy",
        scenario_label="Locked 18 m spine",
        parameters=PARAMS,
        road_features=[],
        district_features=[],
        locked_street_area_wgs84=locked_street,
        palette_override=palette,
    )

    roads = [zone for zone in result.zones if zone["zone_type"] == "road"]
    assert roads
    for zone in roads:
        assert zone["properties"]["width"] == 18.0
        assert zone["properties"]["street_role"] == "spine"
        assert zone["properties"]["road_archetype_id"] == "main_street_complete"
        assert zone["properties"]["road_selected_variant_id"] == ("main_street_complete_v0")
        recipe = plan_public_realm_zone_recipe(
            zone["zone_type"],
            Polygon(zone["coordinates"]),
            zone["properties"],
            strict=True,
        )
        assert recipe is not None
        assert recipe.family_id == "street_complete_main_18m"


def test_locked_lego_street_reclassifies_geometry_that_disproves_local_width():
    lego_catalog = _lego_catalog()
    base = lego_fallback_spec("city_policy", lego_catalog)
    spec = base.model_copy(
        update={
            "local_archetype_id": "calgary_local",
            "public_realm": base.public_realm.model_copy(
                update={
                    "local_street_variant_id": "calgary_local_v0",
                }
            ),
        }
    )
    palette = palette_from_spec(
        spec,
        "city_policy",
        lego_catalog=lego_catalog,
    )
    locked_street = Polygon(
        [
            _offset(0, 25),
            _offset(146, 25),
            _offset(146, 47),
            _offset(0, 47),
        ]
    )
    result = generate_plan_geometry(
        site_polygon_wgs84=_site(146, 72),
        scenario_id="city_policy",
        scenario_label="Locked LEGO mismatch",
        parameters=PARAMS,
        road_features=[],
        district_features=[],
        locked_street_area_wgs84=locked_street,
        palette_override=palette,
    )

    roads = [zone for zone in result.zones if zone["zone_type"] == "road"]
    assert roads
    for zone in roads:
        assert zone["properties"]["width"] == 22.0
        assert zone["properties"]["street_role"] == "spine"
        assert zone["properties"]["road_archetype_id"] == "main_street_complete"
        assert zone["properties"]["road_selected_variant_id"] == ("main_street_complete_v0")
        assert len(zone["properties"]["plan_centerline"]) == 2
        assert (
            plan_public_realm_zone_recipe(
                zone["zone_type"],
                Polygon(zone["coordinates"]),
                zone["properties"],
                strict=True,
            )
            is not None
        )


def test_oversized_greenway_preserves_source_identity_for_family_pending_fallback():
    assert _lego_park_identity_for_metric_polygon(
        kind="greenway",
        archetype_id="linear_park_greenway",
        geometry_m=box(0, 0, 1_200, 80),
    ) == ("greenway", "linear_park_greenway")


def test_preset_scenarios_stamp_landscape_structures():
    result = generate_plan_geometry(
        site_polygon_wgs84=_site(),
        scenario_id="environmental",
        scenario_label="Env",
        parameters=PARAMS,
        road_features=[],
        district_features=[],
    )
    greens = [
        z
        for z in result.zones
        if z["properties"].get("_plan_role") == "open_space"
        and z["properties"].get("green_kind") in ("central", "pocket", "greenway")
    ]
    assert greens
    assert all(z["properties"].get("planting_structure") for z in greens)
    ponds = [z for z in result.zones if z["properties"].get("green_kind") == "pond"]
    greenways = [z for z in result.zones if z["properties"].get("green_kind") == "greenway"]
    assert ponds
    assert all(z["properties"].get("green_space_archetype_id") == "stormwater_retention_pond" for z in ponds)
    assert greenways
    assert all(z["properties"].get("green_space_archetype_id") == "linear_park_greenway" for z in greenways)


def test_city_beautiful_stamps_fountain_and_civic_plaza_archetypes():
    result = generate_plan_geometry(
        site_polygon_wgs84=_site(),
        scenario_id="city_beautiful",
        scenario_label="Beautiful",
        parameters=PARAMS,
        road_features=[],
        district_features=[],
    )
    open_spaces = [z for z in result.zones if z["properties"].get("_plan_role") == "open_space"]
    fountains = [z for z in open_spaces if z["properties"].get("green_kind") == "pond"]
    plazas = [z for z in open_spaces if z["properties"].get("green_kind") == "plaza"]
    assert fountains
    assert all(z["properties"].get("green_space_archetype_id") == "fountain_water_feature" for z in fountains)
    assert plazas
    assert all(z["properties"].get("green_space_archetype_id") == "formal_civic_plaza" for z in plazas)


@pytest.mark.parametrize("scenario_id", sorted(PALETTES))
def test_every_nonwater_public_space_connects_to_the_plan_network(scenario_id):
    from app.services.site_engine import (
        build_transformer,
        local_metric_crs_for_polygon,
        project_geometry,
    )

    site = _site()
    result = generate_plan_geometry(
        site_polygon_wgs84=site,
        scenario_id=scenario_id,
        scenario_label=f"Connected {scenario_id}",
        parameters=PARAMS,
        road_features=[],
        district_features=[],
    )
    public_spaces = [
        zone
        for zone in result.zones
        if zone["properties"].get("_plan_role") == "open_space" and zone["properties"].get("green_kind") != "pond"
    ]

    assert public_spaces
    assert all(zone["properties"].get("park_access_points") for zone in public_spaces), [
        (zone.get("name"), zone["properties"].get("green_kind"))
        for zone in public_spaces
        if not zone["properties"].get("park_access_points")
    ]

    to_metric = build_transformer("EPSG:4326", local_metric_crs_for_polygon(site))
    street_ground = unary_union(
        [
            project_geometry(Polygon(zone["coordinates"]), to_metric)
            for zone in result.zones
            if zone["properties"].get("_plan_role") == "street"
        ]
    )
    for zone in public_spaces:
        park = project_geometry(Polygon(zone["coordinates"]), to_metric)
        for coordinates in zone["properties"]["park_access_points"]:
            gateway = project_geometry(Point(coordinates), to_metric)
            assert park.boundary.distance(gateway) < 0.1
            assert street_ground.distance(gateway) < 3.1


def test_single_block_site_honors_master_plan_typology():
    spec, _ = validate_spec(_spec(single_block_typology="row_bars"), "city_policy")
    palette = palette_from_spec(spec, "city_policy")
    small = _site(width_m=130.0, depth_m=110.0)  # too tight for internal streets
    result = generate_plan_geometry(
        site_polygon_wgs84=small,
        scenario_id="city_policy",
        scenario_label="Tiny",
        parameters=PARAMS,
        road_features=[],
        district_features=[],
        palette_override=palette,
    )
    buildings = [z for z in result.zones if z["properties"].get("_plan_role") == "building"]
    if result.block_count == 1 and buildings:
        typologies = {z["properties"].get("typology") for z in buildings}
        # row_bars requested; perimeter_block only as the degenerate fallback.
        assert typologies <= {"row_bars", "perimeter_block"}
        assert "row_bars" in typologies


def test_single_block_tod_keeps_a_real_park_and_buildable_remainder():
    spec, _ = validate_spec(
        _spec(single_block_typology="row_bars").model_copy(
            update={
                "open_space": OpenSpaceProgram(
                    water_feature=False,
                    plaza=False,
                    central_park_archetype_id="neighborhood_park",
                )
            }
        ),
        "city_policy",
    )
    palette = palette_from_spec(spec, "city_policy")
    compact = _site(width_m=95.0, depth_m=78.0)

    result = generate_plan_geometry(
        site_polygon_wgs84=compact,
        scenario_id="city_policy",
        scenario_label="Compact TOD",
        parameters=PARAMS,
        road_features=[],
        district_features=[],
        palette_override=palette,
    )

    parks = [
        zone
        for zone in result.zones
        if zone["properties"].get("_plan_role") == "open_space"
        and zone["properties"].get("green_kind") == "central"
    ]
    buildings = [zone for zone in result.zones if zone["properties"].get("_plan_role") == "building"]

    assert len(parks) == 1
    assert result.geometry_inputs["open_space_area_m2"] >= 900.0
    assert buildings
    assert result.geometry_inputs["building_footprint_m2"] > 0.0
