"""Exact clay runtime choices preserve native geometry and never repeat."""

import copy
from dataclasses import replace
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
import uuid

import pytest
from geoalchemy2.shape import from_shape
from shapely.geometry import Polygon, box

from app.api.v1 import lego_assembly as endpoint
from app.services.lego_assembly import (
    AssemblyPlanningError,
    AssemblyRequest,
    descriptor_from_library_entry,
    plan_vertical_assembly,
    select_runtime_architecture_entries,
)
from app.services.master_planner.lego_catalog import build_lego_planning_catalog


def clay_entry(parent="calgary_modern_infill_house", variant="infill_flat_roof_minimal"):
    return SimpleNamespace(
        id="clay",
        name="Exact reviewed clay",
        model_url="/api/v1/files/library/clay.glb",
        is_public=True,
        metadata_={
            "rlasm": {
                "method_version": "6.1",
                "delivery_format": "architectural_clay",
                "runtime_enabled": True,
                "variant_id": variant,
                "continuous_resize_allowed": False,
            },
            "lego": {
                "enabled": True,
                "family": "native-clay",
                "role": "assembled",
                "width_m": 10.0,
                "depth_m": 8.0,
                "height_m": 7.0,
                "native_floors": 2,
                "min_floors": 2,
                "max_floors": 2,
                "repeatable_z": False,
                "archetype_ids": [parent, variant],
                "reuse_keys": [parent],
                "source_variant_id": variant,
                "generation_archetype_id": variant,
            },
        },
    )


def request(**changes):
    return replace(AssemblyRequest(30.0, 20.0, 2, archetype_id="infill_flat_roof_minimal"), **changes)


def plan(raw=None, **changes):
    module = descriptor_from_library_entry(raw or clay_entry())
    assert module is not None
    return plan_vertical_assembly([module], request(**changes), allow_forced_fit=True)


@pytest.mark.parametrize("width,depth", [(10, 8), (30, 20), (1000, 100), (8, 10)])
def test_exact_clay_has_one_unscaled_instance_even_on_a_detached_block(width, depth):
    actual = plan(target_width_m=width, target_depth_m=depth)
    assert len(actual["instances"]) == 1
    assert actual["instances"][0]["scale"] == [1.0, 1.0, 1.0]
    assert actual["instances"][0]["native_dimensions_m"] == [10.0, 8.0, 7.0]
    assert actual["fit"]["native_scale_locked"] is True
    assert actual["fit"]["delivery_format"] == "architectural_clay"
    assert actual["fit"]["assembly_mode"] == "fixed_landmark"
    assert actual["footprint_segments"][0]["length_m"] == 10.0
    assert actual["footprint_segments"][0]["thickness_m"] == 8.0


@pytest.mark.parametrize(
    "changes",
    [
        {"target_width_m": 9.5, "target_depth_m": 7.5},
        {"target_width_m": 2.0, "target_depth_m": 100},
        {"target_floors": 1},
        {"target_floors": 3},
    ],
)
def test_incompatible_clay_never_forces_scale_or_floor_substitution(changes):
    with pytest.raises(AssemblyPlanningError) as exc:
        plan(**changes)
    assert exc.value.code == "family_incompatible"


@pytest.mark.parametrize(
    "identity",
    ["calgary_modern_infill_house", "calgary_modern_infill_house_variant_0", "infill_gabled_modern", "unknown_sibling"],
)
def test_parent_alias_or_other_variant_cannot_select_exact_clay(identity):
    with pytest.raises(AssemblyPlanningError) as exc:
        plan(archetype_id=identity)
    assert exc.value.code == "family_not_found"


def test_clay_containment_uses_actual_concave_polygon_not_its_large_bounds():
    notched = Polygon([(-20, -20), (20, -20), (20, -5), (-5, -5), (-5, 20), (-20, 20)])
    with pytest.raises(AssemblyPlanningError) as exc:
        plan(target_width_m=40, target_depth_m=40, footprint_local_m=tuple(notched.exterior.coords))
    assert exc.value.code == "family_incompatible"
    contained = box(-20, -20, 20, 20).difference(box(12, 12, 20, 20))
    actual = plan(
        target_width_m=40,
        target_depth_m=40,
        footprint_profile="l_shape",
        footprint_local_m=tuple(contained.exterior.coords),
    )
    assert actual["instances"][0]["scale"] == [1.0, 1.0, 1.0]


@pytest.mark.parametrize(
    "section,key,value",
    [
        ("rlasm", "runtime_enabled", False),
        ("rlasm", "method_version", "6.0"),
        ("rlasm", "continuous_resize_allowed", True),
        ("lego", "source_variant_id", "sibling"),
        ("lego", "native_floors", None),
        ("lego", "repeatable_z", True),
        ("lego", "role", "floor"),
        ("lego", "width_m", float("nan")),
    ],
)
def test_disabled_or_inconsistent_clay_cannot_become_an_ordinary_module(section, key, value):
    raw = clay_entry()
    raw.metadata_[section][key] = value
    assert descriptor_from_library_entry(raw) is None


def test_installed_public_clay_tier_excludes_legacy_even_after_last_clay_disabled():
    clay = clay_entry()
    legacy = copy.deepcopy(clay)
    legacy.metadata_.pop("rlasm")
    assert select_runtime_architecture_entries([legacy]) == [legacy]
    assert select_runtime_architecture_entries([legacy, clay]) == [clay]
    clay.metadata_["rlasm"]["runtime_enabled"] = False
    assert select_runtime_architecture_entries([legacy, clay]) == []


def test_master_planner_advertises_same_exact_clay_catalogue_as_runtime():
    clay = clay_entry()
    legacy = copy.deepcopy(clay)
    legacy.id = "legacy"
    legacy.metadata_.pop("rlasm")
    legacy.metadata_["lego"].update(
        {
            "family": "legacy",
            "source_variant_id": "infill_gabled_modern",
            "generation_archetype_id": "infill_gabled_modern",
        }
    )
    raw = [legacy, clay]
    actual = build_lego_planning_catalog(raw)
    assert actual.fingerprint == build_lego_planning_catalog(select_runtime_architecture_entries(raw)).fingerprint
    assert actual.supported_floors_by_selectable_id == {"infill_flat_roof_minimal": (2,)}
    assert actual.target_dimensions_by_selectable_id["infill_flat_roof_minimal"] == (10, 8)
    clay.metadata_["rlasm"]["runtime_enabled"] = False
    assert build_lego_planning_catalog(raw).capabilities == ()


@pytest.mark.anyio
async def test_clay_tier_keeps_unsupported_choice_as_massing_even_when_legacy_family_exists(
    client, mock_db, test_user, auth_headers
):
    from tests.conftest import FakeProject
    from tests.test_lego_assembly import _community_item, _make_zone, entry

    project = FakeProject(owner_id=test_user.id)
    zone = _make_zone(
        project,
        properties={
            "_plan_role": "building",
            "development_archetype_id": "new_york_corner_bodega",
            "floors": 3,
            "floor_height": 3.5,
        },
    )
    legacy = [entry(role, role, role, height=3.5) for role in ("podium", "floor", "roof")]
    for item in legacy:
        item.metadata_["lego"]["archetype_ids"] = ["new_york_corner_bodega"]
    added = []
    mock_db.add.side_effect = added.append
    mock_db.execute.side_effect = [
        scalar(test_user),
        scalar(zone),
        scalar(project),
        scalar(project.id),
        scalar([zone]),
        scalar(project),
        scalar([*legacy, clay_entry()]),
        scalar([]),
    ]
    response = await client.post(
        "/api/v1/lego-assembly/place-community", headers=auth_headers, json={"items": [_community_item(zone)]}
    )
    assert response.status_code == 200, response.text
    assert response.json()["items"][0]["generator"] == "planned_massing"
    assert len(added) == 1
    assert added[0].footprint == zone.geometry
    assert "legoAssembly" not in added[0].specifications


def test_non_detached_clay_certification_derives_real_zone_coordinates(monkeypatch):
    raw = clay_entry("vancouver_special", "special_original_1970s")
    descriptor = descriptor_from_library_entry(raw)
    polygon = Polygon([(-20, -20), (20, -20), (20, -5), (-5, -5), (-5, 20), (-20, 20)])
    derive = MagicMock(return_value=tuple(polygon.exterior.coords))
    monkeypatch.setattr(endpoint, "detached_plot_local_coordinates", derive)
    zone = SimpleNamespace(geometry=from_shape(box(-114.1, 51.0, -114.0, 51.1), srid=4326))
    with pytest.raises(AssemblyPlanningError):
        endpoint._strict_locked_building_plan(
            [descriptor], "special_original_1970s", (40, 40, 2, "rectangle", None), {}, zone=zone
        )
    derive.assert_called_once()


def scalar(value):
    result = MagicMock()
    result.scalar_one_or_none.return_value = value
    result.scalars.return_value.all.return_value = value
    return result


@pytest.mark.anyio
@pytest.mark.parametrize("floors,status", [(2, 200), (3, 422)])
async def test_plan_api_enforces_native_clay_despite_forced_fit(
    client, mock_db, test_user, auth_headers, floors, status
):
    mock_db.execute.side_effect = [scalar(test_user), scalar([clay_entry()])]
    response = await client.post(
        "/api/v1/lego-assembly/plan",
        headers=auth_headers,
        json={
            "target_width_m": 40,
            "target_depth_m": 30,
            "target_floors": floors,
            "archetype_id": "infill_flat_roof_minimal",
            "allow_forced_fit": True,
            "footprint_local_m": [[-20, -15], [20, -15], [20, 15], [-20, 15]],
        },
    )
    assert response.status_code == status, response.text
    if status == 200:
        assert response.json()["instances"][0]["scale"] == [1, 1, 1]
    else:
        assert response.json()["detail"]["code"] == "family_incompatible"
    mock_db.add.assert_not_called()


@pytest.mark.anyio
@pytest.mark.parametrize(
    "change",
    [
        "none",
        "ticket_and_display_name",
        "different_path",
        "different_version",
        "scale",
        "unflagged",
        "old_family",
        "unknown_identity",
        "missing_link",
        "disabled",
    ],
)
async def test_saved_recipe_cannot_evade_activated_clay_native_contract(
    client,
    mock_db,
    test_user,
    auth_headers,
    monkeypatch,
    change,
):
    from app.models.models import Building
    from tests.conftest import FakeProject
    from tests.test_lego_assembly import _make_zone

    project = FakeProject(owner_id=test_user.id)
    building = Building(id=uuid.uuid4(), project_id=project.id, specifications={"existing": "preserved"})
    zone = _make_zone(
        project,
        building_id=building.id,
        properties={
            "_plan_role": "building",
            "development_selected_variant_id": "infill_flat_roof_minimal",
            "floors": 2,
        },
    )
    inventory = select_runtime_architecture_entries([clay_entry()])
    descriptor = descriptor_from_library_entry(inventory[0])
    actual = endpoint._strict_locked_building_plan(
        [descriptor],
        "infill_flat_roof_minimal",
        endpoint._locked_building_target(zone),
        zone.properties,
        zone=zone,
        allow_forced_fit=True,
    )
    body = {
        **actual,
        "module_family": actual["family"],
        "archetype_id": "infill_flat_roof_minimal",
        "catalog_fingerprint": build_lego_planning_catalog(inventory).fingerprint,
    }
    if change == "scale":
        body["instances"][0]["scale"] = [2, 2, 2]
    elif change == "ticket_and_display_name":
        body["instances"][0]["model_url"] += "?file_ticket=temporary-local-test-ticket"
        body["instances"][0]["asset_name"] = "Different display label"
    elif change == "different_path":
        body["instances"][0]["model_url"] = "/api/v1/files/library/other.glb"
    elif change == "different_version":
        body["instances"][0]["model_url"] += "?v=wrong-content-version"
    elif change == "unflagged":
        body["fit"].pop("native_scale_locked")
    elif change == "old_family":
        body["module_family"] = "old-stretched-house"
    elif change == "unknown_identity":
        zone.properties = {**zone.properties, "development_selected_variant_id": "unknown"}
        body["archetype_id"] = "unknown"
    elif change == "disabled":
        disabled = clay_entry()
        disabled.metadata_["rlasm"]["runtime_enabled"] = False
        inventory = select_runtime_architecture_entries([disabled])
    monkeypatch.setattr(endpoint, "_get_building_with_access", AsyncMock(return_value=building))
    monkeypatch.setattr(endpoint, "lock_residual_landscape_project", AsyncMock())
    monkeypatch.setattr(endpoint, "mark_linked_community_3d_stale", AsyncMock())
    monkeypatch.setattr(endpoint, "_accessible_entries", AsyncMock(return_value=inventory))
    mock_db.execute.side_effect = [scalar(test_user), scalar([] if change == "missing_link" else [zone])]
    response = await client.post(f"/api/v1/lego-assembly/recipes/{building.id}", headers=auth_headers, json=body)
    accepted = change in {"none", "ticket_and_display_name"}
    assert response.status_code == (200 if accepted else 409), response.text
    assert building.specifications["existing"] == "preserved"
    if accepted:
        assert building.specifications["legoAssembly"]["instances"][0]["scale"] == [1, 1, 1]
        assert building.specifications["legoAssembly"]["instances"][0]["model_url"] == descriptor.model_url
        assert building.specifications["legoAssembly"]["instances"][0]["asset_name"] == descriptor.name
    else:
        assert "legoAssembly" not in building.specifications


@pytest.mark.anyio
async def test_untrusted_manual_zone_cannot_apply_legacy_recipe_after_clay_activation(test_user, mock_db):
    from tests.conftest import FakeProject
    from tests.test_lego_assembly import _make_zone, _recipe_body
    from fastapi import HTTPException

    project = FakeProject(owner_id=test_user.id)
    zone = _make_zone(project, properties={"_plan_role": "building"})
    item = endpoint.Community3DCompileItem(
        zone_id=zone.id,
        source_updated_at=zone.updated_at,
        recipe=endpoint.LegoPlaceRequest.model_validate(_recipe_body()),
    )
    with pytest.raises(HTTPException) as exc:
        await endpoint._assert_ai_lego_recipes_are_current(
            mock_db,
            test_user,
            project.id,
            [(item, zone, "building")],
            entries=select_runtime_architecture_entries([clay_entry()]),
        )
    assert exc.value.status_code == 409
