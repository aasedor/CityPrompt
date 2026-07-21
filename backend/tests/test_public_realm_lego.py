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
    local_only = build_public_realm_capability_catalog(
        family_ids=["street_local_public_realm"]
    )

    assert first == second
    assert first.family_ids == tuple(sorted(first.family_ids))
    assert set(parks.family_ids) == {
        "park_civic_plaza",
        "park_linear_greenway",
        "park_neighborhood_community",
        "park_pocket_courtyard",
        "park_water_ecology",
    }
    assert local_only.family_ids == ("street_local_public_realm",)
    assert "main_street_complete" not in local_only.archetype_ids
    assert set(local_only.variants_by_archetype["green_alley"]) == {
        f"green_alley_v{index}" for index in range(4)
    }
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


@pytest.mark.parametrize(
    ("variant_id", "appearance_kit_id"),
    [
        ("main_street_complete_v0", "calgary_contemporary_native"),
        ("main_street_complete_v1", "heritage_brick_stone"),
        ("main_street_complete_v2", "timber_biophilic"),
        ("main_street_complete_v3", "industrial_adaptive_reuse"),
    ],
)
def test_main_street_variants_share_native_geometry_but_select_exact_appearance(
    variant_id,
    appearance_kit_id,
):
    recipe = plan_public_realm_recipe(
        _street_request(
            "main_street_complete",
            22,
            variant_id=variant_id,
        )
    )

    assert recipe.family_id == "street_complete_main_22m"
    assert recipe.profile_id == "complete-main-22m-v1"
    assert recipe.variant_id == variant_id
    assert recipe.appearance_kit_id == appearance_kit_id


def test_main_street_rejects_uniformly_stretched_legacy_row_with_structured_error():
    with pytest.raises(PublicRealmPlanningError) as raised:
        plan_public_realm_recipe(
            _street_request("main_street_complete", 18)
        )

    error = raised.value
    assert error.code == "family_incompatible"
    assert error.requested["target"]["row_width_m"] == 18
    assert error.supported_families[0]["family_id"] == "street_complete_main_22m"
    assert error.violations == [{
        "field": "target.row_width_m",
        "requested": 18.0,
        "supported": [21.95, 22.05],
    }]
    assert error.as_detail()["code"] == "family_incompatible"


def test_local_row_compatibility_is_source_specific():
    assert plan_public_realm_recipe(
        _street_request("woonerf_shared_street", 14)
    ).family_id == "street_local_public_realm"
    assert plan_public_realm_recipe(
        _street_request("multi_use_trail", 4)
    ).variant_id == "multi_use_trail_v1"

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
    assert raised.value.violations == [{
        "field": "target.arm_count",
        "requested": 3,
        "supported": [4],
    }]


def test_unknown_archetype_is_family_not_found_without_fallback():
    with pytest.raises(PublicRealmPlanningError) as raised:
        plan_public_realm_recipe(
            _street_request("invented_magic_boulevard", 22)
        )

    assert raised.value.code == "family_not_found"
    assert raised.value.requested["archetype_id"] == "invented_magic_boulevard"
    assert raised.value.supported_families


def test_recipe_identity_fails_closed_after_payload_or_catalog_hash_tampering():
    recipe = plan_public_realm_recipe(
        _street_request("narrow_residential_street", 12)
    )
    payload = recipe.model_dump(mode="json")
    original = public_realm_representation_hash(
        source_hash="a" * 64,
        recipe=payload,
    )

    assert original is not None
    assert public_realm_recipe_identity(payload) is not None
    assert public_realm_representation_hash(
        source_hash="b" * 64,
        recipe=payload,
    ) != original

    payload["appearance_kit_id"] = "tampered"
    assert public_realm_recipe_identity(payload) is None
    assert public_realm_representation_hash(
        source_hash="a" * 64,
        recipe=payload,
    ) is None

    # A self-hash proves only payload integrity.  Recomputing it must not turn
    # a non-canonical renderer recipe into an executable catalog identity.
    payload["recipe_hash"] = public_realm_recipe_hash(payload)
    assert public_realm_recipe_hash(payload) == payload["recipe_hash"]
    assert public_realm_recipe_identity(payload) is None


def test_linear_greenway_accepts_compact_corridor_but_rejects_square_pond_lobe():
    compact_corridor = plan_public_realm_recipe(PublicRealmPlanRequest(
        archetype_id="linear_park_greenway",
        target=ParkPolygonTarget(width_m=72, depth_m=15, area_m2=1_050),
    ))

    assert compact_corridor.family_id == "park_linear_greenway"
    with pytest.raises(PublicRealmPlanningError) as raised:
        plan_public_realm_recipe(PublicRealmPlanRequest(
            archetype_id="linear_park_greenway",
            target=ParkPolygonTarget(width_m=38, depth_m=34, area_m2=1_120),
        ))
    assert raised.value.violations[-1] == {
        "field": "target.aspect_ratio",
        "requested": pytest.approx(1.118, abs=0.001),
        "supported": {"min": 3.0},
    }


def test_pocket_courtyard_family_accepts_broad_clipped_courtyard_envelope():
    recipe = plan_public_realm_recipe(PublicRealmPlanRequest(
        archetype_id="urban_pocket_park",
        target=ParkPolygonTarget(width_m=86, depth_m=78, area_m2=2_000),
    ))

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

    assert plan_public_realm_zone_recipe(
        "green_space",
        geometry,
        properties,
        strict=False,
    ) is None

    with pytest.raises(PublicRealmPlanningError) as raised:
        plan_public_realm_zone_recipe(
            "green_space",
            geometry,
            {**properties, "_plan_scenario": "community_wellbeing"},
            strict=True,
        )
    assert raised.value.code == "family_not_found"


def test_zone_planner_rejects_non_polygonal_park_without_attribute_error():
    geometry = _to_wgs84(LineString([
        (700_000, 5_650_000),
        (700_030, 5_650_000),
    ]))

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
        plan_public_realm_recipe(PublicRealmPlanRequest(
            archetype_id="roundabout",
            target=StreetNodeTarget(
                approach_row_width_m=22,
                diameter_m=30,
                arm_count=3,
            ),
        ))

    assert raised.value.violations == [{
        "field": "target.arm_count",
        "requested": 3,
        "supported": [4],
    }]
