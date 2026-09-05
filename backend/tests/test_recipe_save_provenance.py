"""A repeated Save All must preserve the exact compiled representation proof."""

import copy
import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.api.v1 import lego_assembly as endpoint
from app.models.models import Building
from app.services.residual_landscape import community_3d_representation_hash
from app.services.lego_assembly import descriptor_from_library_entry, select_runtime_architecture_entries
from app.services.master_planner.lego_catalog import build_lego_planning_catalog
from tests.conftest import FakeProject
from tests.test_clay_runtime import clay_entry
from tests.test_lego_assembly import _make_zone, _recipe_body


def compiled_fixture(user):
    project = FakeProject(owner_id=user.id)
    zone = _make_zone(project, properties={"_plan_role": "building"})
    body = _recipe_body()
    building = Building(
        id=uuid.uuid4(),
        project_id=project.id,
        name="Saved house",
        footprint=zone.geometry,
        height_meters=18,
        floor_count=6,
        rotation_degrees=0,
        specifications={
            "legoAssembly": endpoint._recipe_payload(endpoint.LegoRecipeRequest.model_validate(body)),
            "lego_placed": True,
            "other_workflow": {"preserved": True},
        },
    )
    zone.building_id = building.id
    zone.building_ids = [str(building.id)]
    endpoint._stamp_community_3d(zone, "building", "2026-09-05T01:00:00Z", building=building)
    return project, zone, building, body


def result(value):
    item = MagicMock()
    item.scalar_one_or_none.return_value = value
    item.scalars.return_value.all.return_value = value
    return item


def access(monkeypatch, building):
    monkeypatch.setattr(endpoint, "_get_building_with_access", AsyncMock(return_value=building))
    monkeypatch.setattr(endpoint, "lock_residual_landscape_project", AsyncMock())
    monkeypatch.setattr(endpoint, "_accessible_entries", AsyncMock(return_value=[]))


def test_wing_depth_is_semantic_only_for_shaped_footprints():
    original = _recipe_body()
    rectangle = copy.deepcopy(original)
    rectangle["target"]["wing_depth_m"] = 4
    assert endpoint._recipe_save_identity(original) == endpoint._recipe_save_identity(rectangle)
    original["target"].update(footprint_profile="l_shape", wing_depth_m=3)
    rectangle["target"].update(footprint_profile="l_shape", wing_depth_m=4)
    assert endpoint._recipe_save_identity(original) != endpoint._recipe_save_identity(rectangle)


@pytest.mark.anyio
@pytest.mark.parametrize(
    "noise", ["identical", "target_defaults", "transport_ticket", "display_and_preview", "already_stale"]
)
async def test_repeated_recipe_save_keeps_original_compiled_proof(
    client, mock_db, test_user, auth_headers, monkeypatch, noise
):
    _, zone, building, body = compiled_fixture(test_user)
    if noise == "target_defaults":
        body["target"].update(footprint_profile="rectangle", wing_depth_m=None)
    elif noise == "transport_ticket":
        body["instances"][0]["model_url"] += "?file_ticket=temporary-test-ticket"
    elif noise == "display_and_preview":
        body["instances"][0]["asset_name"] = "A refreshed display label"
        body["assembled_preview_url"] = "/api/v1/files/preview.png"
    elif noise == "already_stale":
        zone.properties["community_3d"]["state"] = "stale"
    original_zone = copy.deepcopy(zone.properties)
    original_spec = copy.deepcopy(building.specifications)
    access(monkeypatch, building)
    stale = AsyncMock()
    monkeypatch.setattr(endpoint, "mark_linked_community_3d_stale", stale)
    mock_db.execute.side_effect = [result(test_user), result(test_user)]
    for _ in range(2):
        response = await client.post(f"/api/v1/lego-assembly/recipes/{building.id}", headers=auth_headers, json=body)
        assert response.status_code == 200, response.text
        assert response.json()["changed"] is False
        assert response.json()["legoAssembly"] == original_spec["legoAssembly"]
    assert building.specifications == original_spec
    assert zone.properties == original_zone
    meta = zone.properties["community_3d"]
    assert (
        community_3d_representation_hash(
            kind="building", generator="lego_assembly", source_hash=meta["source_hash"], building=building
        )
        == meta["representation_hash"]
    )
    assert building.specifications["community3DRepresentation"]["representation_hash"] == meta["representation_hash"]
    stale.assert_not_awaited()
    mock_db.flush.assert_not_awaited()


@pytest.mark.anyio
@pytest.mark.parametrize(
    "change",
    [
        "scale",
        "position",
        "rotation",
        "asset_path",
        "asset_version",
        "floors",
        "height",
        "fit",
        "family",
        "removed_instance",
    ],
)
async def test_real_recipe_changes_still_invalidate_compiled_proposal(
    client, mock_db, test_user, auth_headers, monkeypatch, change
):
    _, zone, building, body = compiled_fixture(test_user)
    if change == "scale":
        body["instances"][0]["scale"] = [2, 1, 1]
    elif change == "position":
        body["instances"][0]["position"] = [1, 0, 0]
    elif change == "rotation":
        body["instances"][0]["rotation_degrees"] = 45
    elif change == "asset_path":
        body["instances"][0]["model_url"] = "/api/v1/files/different.glb"
    elif change == "asset_version":
        body["instances"][0]["model_url"] += "?v=2"
    elif change == "floors":
        body["target"]["floors"] = 7
    elif change == "height":
        body["assembled_height_m"] = 20
    elif change == "fit":
        body["fit"]["scale_x"] = 1.1
    elif change == "family":
        body["module_family"] = "other-family"
    elif change == "removed_instance":
        body["instances"].pop()
    access(monkeypatch, building)
    mock_db.execute.side_effect = [result(test_user), result([zone])]
    response = await client.post(f"/api/v1/lego-assembly/recipes/{building.id}", headers=auth_headers, json=body)
    assert response.status_code == 200, response.text
    assert response.json()["changed"] is True
    assert zone.properties["community_3d"]["state"] == "stale"
    assert building.specifications["other_workflow"] == {"preserved": True}


@pytest.mark.anyio
@pytest.mark.parametrize("change", ["same", "ticket_and_defaults", "disabled_catalogue", "changed_source"])
async def test_native_recipe_noop_keeps_proof_but_still_validates_current_source_and_catalogue(
    client,
    mock_db,
    test_user,
    auth_headers,
    monkeypatch,
    change,
):
    project = FakeProject(owner_id=test_user.id)
    zone = _make_zone(
        project,
        properties={
            "_plan_role": "building",
            "development_selected_variant_id": "infill_flat_roof_minimal",
            "floors": 2,
        },
    )
    inventory = select_runtime_architecture_entries([clay_entry()])
    plan = endpoint._strict_locked_building_plan(
        [descriptor_from_library_entry(inventory[0])],
        "infill_flat_roof_minimal",
        endpoint._locked_building_target(zone),
        zone.properties,
        zone=zone,
        allow_forced_fit=True,
    )
    recipe = endpoint.LegoPlaceRequest.model_validate(
        {
            **plan,
            "module_family": plan["family"],
            "catalog_fingerprint": build_lego_planning_catalog(inventory).fingerprint,
        }
    )
    item = endpoint.Community3DCompileItem(zone_id=zone.id, source_updated_at=zone.updated_at, recipe=recipe)
    await endpoint._assert_ai_lego_recipes_are_current(
        mock_db, test_user, project.id, [(item, zone, "building")], entries=inventory
    )
    building = Building(
        id=uuid.uuid4(),
        project_id=project.id,
        name="Native house",
        footprint=zone.geometry,
        height_meters=recipe.assembled_height_m,
        floor_count=2,
        rotation_degrees=0,
        specifications={"legoAssembly": endpoint._recipe_payload(recipe), "lego_placed": True},
    )
    zone.building_id = building.id
    zone.building_ids = [str(building.id)]
    endpoint._stamp_community_3d(zone, "building", "2026-09-05T01:00:00Z", building=building)
    original_zone, original_spec = copy.deepcopy(zone.properties), copy.deepcopy(building.specifications)
    body = copy.deepcopy(original_spec["legoAssembly"])
    if change == "ticket_and_defaults":
        body["instances"][0]["model_url"] += "?file_ticket=rotated-ticket"
        body["instances"][0]["asset_name"] = "Updated display name"
        body["target"]["wing_depth_m"] = None
        body["catalog_fingerprint"] = body["catalog_fingerprint"].upper()
    elif change == "disabled_catalogue":
        disabled = clay_entry()
        disabled.metadata_["rlasm"]["runtime_enabled"] = False
        inventory = select_runtime_architecture_entries([disabled])
    elif change == "changed_source":
        zone.properties = {**zone.properties, "floors": 3}
    access(monkeypatch, building)
    monkeypatch.setattr(endpoint, "_accessible_entries", AsyncMock(return_value=inventory))
    stale, modified = AsyncMock(), MagicMock()
    monkeypatch.setattr(endpoint, "mark_linked_community_3d_stale", stale)
    monkeypatch.setattr(endpoint, "flag_modified", modified)
    mock_db.execute.side_effect = [result(test_user), result([zone])]
    response = await client.post(f"/api/v1/lego-assembly/recipes/{building.id}", headers=auth_headers, json=body)
    expected = 200 if change in {"same", "ticket_and_defaults"} else 409
    assert response.status_code == expected, response.text
    if expected == 200:
        assert response.json()["changed"] is False
        assert zone.properties == original_zone
    assert building.specifications == original_spec
    stale.assert_not_awaited()
    modified.assert_not_called()
