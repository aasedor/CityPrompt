from types import SimpleNamespace

import pytest
from shapely.geometry import box

from app.services.community_3d_scope import (
    Community3DScopeError,
    physical_community_3d_zones,
    resolve_boundary_community_3d_scope,
    resolve_community_3d_scope,
)


def _zone(
    zone_id: str,
    *,
    zone_type: str = "building",
    properties: dict[str, object] | None = None,
    geometry=None,
) -> SimpleNamespace:
    return SimpleNamespace(
        id=zone_id,
        zone_type=zone_type,
        properties=properties or {},
        geometry=geometry,
    )


def _plan_zone(
    zone_id: str,
    *,
    snapshot_id: str,
    scenario: str,
) -> SimpleNamespace:
    return _zone(
        zone_id,
        properties={
            "_plan_snapshot_id": snapshot_id,
            "_plan_scenario": scenario,
        },
    )


def _ids(zones: list[SimpleNamespace]) -> list[str]:
    return [str(zone.id) for zone in zones]


def test_physical_zones_exclude_boundary_and_height_framework() -> None:
    building = _zone("building")
    park = _zone("park", zone_type="park")
    boundary = _zone("boundary", zone_type="site_boundary")
    framework = _zone(
        "framework",
        properties={"_plan_role": "framework_height"},
    )

    assert physical_community_3d_zones([boundary, building, framework, park]) == [building, park]


def test_exact_scope_accepts_one_complete_plan_group_and_omits_sibling() -> None:
    policy_a = _plan_zone(
        "policy-a",
        snapshot_id="snapshot-1",
        scenario="city-policy",
    )
    policy_b = _plan_zone(
        "policy-b",
        snapshot_id="snapshot-1",
        scenario="city-policy",
    )
    economic_a = _plan_zone(
        "economic-a",
        snapshot_id="snapshot-1",
        scenario="economic",
    )
    economic_b = _plan_zone(
        "economic-b",
        snapshot_id="snapshot-1",
        scenario="economic",
    )

    resolved = resolve_community_3d_scope(
        [policy_a, economic_a, policy_b, economic_b],
        {"policy-a", "policy-b"},
    )

    assert resolved == [policy_a, policy_b]


def test_exact_scope_rejects_partial_plan_group() -> None:
    zones = [
        _plan_zone("policy-a", snapshot_id="snapshot-1", scenario="city-policy"),
        _plan_zone("policy-b", snapshot_id="snapshot-1", scenario="city-policy"),
    ]

    with pytest.raises(Community3DScopeError):
        resolve_community_3d_scope(zones, {"policy-a"})


def test_exact_scope_rejects_unknown_zone_id() -> None:
    zone = _plan_zone(
        "policy-a",
        snapshot_id="snapshot-1",
        scenario="city-policy",
    )

    with pytest.raises(Community3DScopeError):
        resolve_community_3d_scope([zone], {"policy-a", "not-in-project"})


def test_exact_scope_requires_every_ungrouped_physical_zone() -> None:
    manual_building = _zone("manual-building")
    manual_park = _zone("manual-park", zone_type="park")
    imported = _plan_zone(
        "policy-a",
        snapshot_id="snapshot-1",
        scenario="city-policy",
    )

    with pytest.raises(Community3DScopeError):
        resolve_community_3d_scope(
            [manual_building, manual_park, imported],
            {"manual-building", "policy-a"},
        )


def test_expansion_adds_complete_selected_group_and_all_ungrouped_zones() -> None:
    manual = _zone("manual")
    policy_a = _plan_zone(
        "policy-a",
        snapshot_id="snapshot-1",
        scenario="city-policy",
    )
    policy_b = _plan_zone(
        "policy-b",
        snapshot_id="snapshot-1",
        scenario="city-policy",
    )
    economic_a = _plan_zone(
        "economic-a",
        snapshot_id="snapshot-1",
        scenario="economic",
    )
    economic_b = _plan_zone(
        "economic-b",
        snapshot_id="snapshot-1",
        scenario="economic",
    )

    resolved = resolve_community_3d_scope(
        [economic_a, manual, policy_a, economic_b, policy_b],
        {"policy-a"},
        expand_groups=True,
    )

    assert _ids(resolved) == ["manual", "policy-a", "policy-b"]


def test_legacy_imported_layers_group_by_imported_from() -> None:
    legacy_a = _zone(
        "legacy-a",
        properties={"_imported_from": "Plan — Legacy"},
    )
    legacy_b = _zone(
        "legacy-b",
        properties={"_imported_from": "Plan — Legacy"},
    )
    sibling = _zone(
        "sibling",
        properties={"_imported_from": "Plan — Alternative"},
    )

    resolved = resolve_community_3d_scope(
        [legacy_a, sibling, legacy_b],
        {"legacy-a", "legacy-b"},
    )
    assert resolved == [legacy_a, legacy_b]

    with pytest.raises(Community3DScopeError):
        resolve_community_3d_scope(
            [legacy_a, sibling, legacy_b],
            {"legacy-a"},
        )


def test_boundary_scope_accepts_exact_intersections_and_excludes_outside() -> None:
    boundary = _zone(
        "boundary",
        zone_type="site_boundary",
        geometry=box(0, 0, 10, 10),
    )
    building = _zone("building", geometry=box(1, 1, 3, 3))
    park = _zone("park", zone_type="green_space", geometry=box(8, 8, 12, 12))
    outside = _zone("outside", geometry=box(20, 20, 30, 30))
    framework = _zone(
        "framework",
        properties={"_plan_role": "framework_height"},
        geometry=box(2, 2, 4, 4),
    )

    resolved = resolve_boundary_community_3d_scope(
        [outside, boundary, building, framework, park],
        {"building", "park"},
        "boundary",
    )

    assert _ids(resolved) == ["building", "park"]


def test_boundary_scope_rejects_missing_or_unrelated_zone_ids() -> None:
    boundary = _zone(
        "boundary",
        zone_type="site_boundary",
        geometry=box(0, 0, 10, 10),
    )
    inside = _zone("inside", geometry=box(1, 1, 2, 2))
    also_inside = _zone("also-inside", geometry=box(3, 3, 4, 4))
    outside = _zone("outside", geometry=box(20, 20, 21, 21))

    with pytest.raises(Community3DScopeError):
        resolve_boundary_community_3d_scope(
            [boundary, inside, also_inside, outside],
            {"inside"},
            "boundary",
        )

    with pytest.raises(Community3DScopeError):
        resolve_boundary_community_3d_scope(
            [boundary, inside, also_inside, outside],
            {"inside", "also-inside", "outside"},
            "boundary",
        )
