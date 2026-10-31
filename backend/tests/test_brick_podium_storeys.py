import hashlib
import json
import math
import uuid
from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from scripts import brick_podium_storeys as pilot
from app.services.lego_assembly import (
    AssemblyPlanningError,
    AssemblyRequest,
    descriptor_from_library_entry,
    plan_vertical_assembly,
)
from app.api.v1.lego_assembly import (
    Community3DCompileItem,
    _assert_ai_lego_recipes_are_current,
    _locked_building_target,
)
from app.models.models import SiteZone
from app.services.master_planner.lego_catalog import build_lego_planning_catalog


def placed_tower(storeys, height, **overrides):
    # The placement plot reserves 1.5 m on each side of the exact 54 x 44 m
    # model. This is the ordinary student's saved zone, not a synthetic target.
    east = 111320 * math.cos(math.radians(51))
    ring = [
        (-114 + x / east, 51 + y / 111320)
        for x, y in [(-28.5, -23.5), (28.5, -23.5), (28.5, 23.5), (-28.5, 23.5), (-28.5, -23.5)]
    ]
    properties = dict(
        pick_place_asset="claude_trial_brick_podium_condo_tower",
        development_selected_variant_id=pilot.VARIANT,
        pick_place_model_revision=pilot.SOURCE,
        native_plot_axes=True,
        floors=storeys,
        floor_count=storeys,
        development_height_override_m=height,
        building_footprint_program_id="brick-podium-condo-native-footprint-v001",
        building_footprint_scale=1,
        building_footprint_native_width_m=54,
        building_footprint_native_depth_m=44,
    )
    properties.update(overrides)
    return SiteZone(
        id=uuid.uuid4(),
        project_id=uuid.uuid4(),
        zone_type="building",
        updated_at=datetime.now(timezone.utc),
        properties=properties,
        geometry="SRID=4326;POLYGON((" + ",".join(f"{x} {y}" for x, y in ring) + "))",
    )


@pytest.mark.anyio
@pytest.mark.parametrize(("storeys", "height"), [(15, 56.1), (25, 86.1), (40, 131.1)])
async def test_saved_tower_storey_edit_accepts_the_planned_native_target(program, storeys, height):
    _, rows = pilot.load_program(program)
    entries = [SimpleNamespace(**{**row, "metadata_": row["metadata"]}) for row in rows]
    descriptors = [descriptor_from_library_entry(row) for row in entries]
    plan = plan_vertical_assembly(
        descriptors,
        AssemblyRequest(
            54, 44, storeys, archetype_id=pilot.VARIANT, model_revision=pilot.SOURCE, reuse_keys=(pilot.VARIANT,)
        ),
        allow_forced_fit=False,
    )
    zone = placed_tower(storeys, height)
    item = Community3DCompileItem(
        zone_id=zone.id,
        source_updated_at=zone.updated_at,
        recipe=dict(
            module_family=plan["family"],
            archetype_id=plan["archetype_id"],
            reuse_keys=plan["reuse_keys"],
            target=plan["target"],
            instances=plan["instances"],
            assembled_height_m=plan["assembled_height_m"],
            fit=plan["fit"],
            catalog_fingerprint=build_lego_planning_catalog(entries).fingerprint,
        ),
    )
    await _assert_ai_lego_recipes_are_current(None, None, zone.project_id, [(item, zone, "building")], entries=entries)
    assert _locked_building_target(zone)[:3] == (54, 44, storeys)
    assert zone.properties["target_w_m"] == 54
    assert zone.properties["target_d_m"] == 44


def test_tower_footprint_contract_ignores_client_claimed_native_dimensions():
    zone = placed_tower(25, 86.1, building_footprint_native_width_m=999, building_footprint_native_depth_m=999)
    assert _locked_building_target(zone)[:3] == (54, 44, 25)


@pytest.mark.parametrize(
    "overrides",
    [
        {"building_footprint_scale": 1.1},
        {"building_footprint_scale": float("nan")},
        {"development_selected_variant_id": "another_tower"},
        {"pick_place_model_revision": "another_revision"},
        {"pick_place_asset": "another_asset"},
    ],
)
def test_tower_footprint_contract_refuses_unbound_or_rescaled_models(overrides):
    from fastapi import HTTPException

    with pytest.raises(HTTPException) as caught:
        _locked_building_target(placed_tower(25, 86.1, **overrides))
    assert caught.value.status_code == 409


@pytest.fixture
def program(tmp_path, monkeypatch):
    source = tmp_path / "source.glb"
    source.write_bytes(b"immutable-source-fixture")
    source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    monkeypatch.setattr(pilot, "SOURCE_HASH", source_hash)
    modules = []
    for role, lower, upper, storeys in pilot.BANDS:
        path = tmp_path / f"{role}.glb"
        path.write_bytes(role.encode())
        modules.append(
            dict(
                role=role,
                path=path.name,
                bytes=path.stat().st_size,
                sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                occupied_storeys=storeys,
                source_vertical_band_m=[lower, upper],
                native_dimensions_m=[54 if role == "podium" else 38, 44 if role == "podium" else 30, upper - lower],
            )
        )
    manifest = dict(id=pilot.PROGRAM, source=dict(path=str(source), sha256=source_hash), modules=modules)
    (tmp_path / "program.json").write_text(json.dumps(manifest), encoding="utf-8")
    return tmp_path


@pytest.mark.parametrize(("storeys", "height"), [(15, 56.1), (25, 86.1), (40, 131.1)])
def test_brick_podium_keeps_one_complete_base_and_roof_while_repeating_full_floors(program, storeys, height):
    manifest, rows = pilot.load_program(program)
    descriptors = [
        descriptor_from_library_entry(SimpleNamespace(**{**row, "metadata_": row["metadata"]})) for row in rows
    ]
    assert all(descriptors)
    plan = plan_vertical_assembly(
        descriptors,
        AssemblyRequest(54, 44, storeys, archetype_id=pilot.VARIANT, model_revision=pilot.SOURCE),
        allow_forced_fit=False,
    )
    roles = [instance["role"] for instance in plan["instances"]]
    assert roles.count("podium") == roles.count("roof") == 1
    assert roles.count("floor") == storeys - 3
    assert plan["assembled_height_m"] == pytest.approx(height)
    assert all(instance["scale"] == [1, 1, 1] for instance in plan["instances"])
    assert all(instance["position"][:2] == [0, 0] for instance in plan["instances"])
    assert plan["fit"]["delivery_format"] == "architectural_clay_module_v1"
    assert all(row["metadata"]["rlasm"]["source_model_sha256"] == manifest["source"]["sha256"] for row in rows)


@pytest.mark.parametrize("storeys", [12, 41])
def test_brick_program_refuses_out_of_range_storeys(program, storeys):
    _, rows = pilot.load_program(program)
    descriptors = [
        descriptor_from_library_entry(SimpleNamespace(**{**row, "metadata_": row["metadata"]})) for row in rows
    ]
    with pytest.raises(AssemblyPlanningError):
        plan_vertical_assembly(
            descriptors, AssemblyRequest(54, 44, storeys, archetype_id=pilot.VARIANT), allow_forced_fit=False
        )


def test_brick_program_refuses_changed_module_bytes(program):
    (program / "floor.glb").write_bytes(b"changed")
    with pytest.raises(ValueError, match="Changed derived module"):
        pilot.load_program(program)


def test_brick_program_refuses_changed_source_datums(program):
    path = program / "program.json"
    manifest = json.loads(path.read_text())
    manifest["modules"][1]["source_vertical_band_m"] = [15, 18]
    path.write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match="band contract changed"):
        pilot.load_program(program)
