"""Unit tests for site zone generation utility helpers."""

import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from shapely.geometry import Polygon, mapping

from app.api.v1.site_zones import (
    _boundary_covers_polygon,
    _coordinates_materially_changed,
    _invalidate_boundary_dependents,
    _invalidate_residual_landscape,
    _residual_source_identity,
    _restore_zone_snapshot,
    _normalize_building_ids,
    _resolve_unit_count,
    _safe_int,
    _safe_optional_float,
    _safe_optional_int,
    _validated_polygon_coordinates,
)
from app.services.plan_boundary_identity import (
    PLAN_BOUNDARY_RESTORE_STATE_KEY,
    plan_boundary_fingerprint,
    stamp_plan_boundary_identity,
)


def _query_result(items):
    result = MagicMock()
    result.scalars.return_value.all.return_value = items
    return result


def _boundary_dependents_db(plan, manual, snapshot, scenario):
    return SimpleNamespace(
        execute=AsyncMock(
            side_effect=[
                _query_result([plan, manual]),
                _query_result([snapshot]),
                _query_result([scenario]),
            ]
        )
    )


def test_boundary_coordinate_change_ignores_closing_point_and_float_noise() -> None:
    before = [[0.0, 0.0], [2.0, 0.0], [2.0, 2.0], [0.0, 0.0]]
    same_open_ring = [[0.0, 0.0], [2.0 + 1e-10, 0.0], [2.0, 2.0]]
    moved = [[0.0, 0.0], [2.01, 0.0], [2.0, 2.0]]

    assert not _coordinates_materially_changed(before, same_open_ring)
    assert _coordinates_materially_changed(before, moved)
    assert _coordinates_materially_changed(before, moved + [[0.0, 0.0]])


def test_plan_boundary_fingerprint_is_ring_order_independent() -> None:
    original = Polygon([(0, 0), (3, 0), (3, 2), (0, 2)])
    rotated_and_reversed = Polygon([(3, 2), (3, 0), (0, 0), (0, 2)])
    moved = Polygon([(0, 0), (3.00000001, 0), (3, 2), (0, 2)])

    assert plan_boundary_fingerprint(original) == plan_boundary_fingerprint(mapping(rotated_and_reversed))
    assert plan_boundary_fingerprint(original) != plan_boundary_fingerprint(moved)
    assert plan_boundary_fingerprint(None) is None


def test_generated_plan_zone_identity_clears_old_stale_markers() -> None:
    boundary_id = uuid.uuid4()
    snapshot_id = uuid.uuid4()

    stamped = stamp_plan_boundary_identity(
        {
            "_plan_role": "building",
            "_plan_boundary_stale": True,
            "_plan_boundary_changed_at": "yesterday",
        },
        fingerprint="source-fingerprint",
        boundary_zone_id=boundary_id,
        snapshot_id=snapshot_id,
    )

    assert stamped == {
        "_plan_role": "building",
        "_plan_boundary_fingerprint": "source-fingerprint",
        "_plan_boundary_zone_id": str(boundary_id),
        "_plan_snapshot_id": str(snapshot_id),
    }


def test_polygon_validation_drops_a_near_closing_vertex() -> None:
    coordinates = [
        [-114.16, 51.04],
        [-114.15, 51.04],
        [-114.15, 51.05],
        [-114.16000001, 51.04000001],
    ]

    normalized = _validated_polygon_coordinates(coordinates)

    assert normalized == coordinates[:3] + [coordinates[0]]


def test_polygon_validation_rejects_a_material_bow_tie() -> None:
    with pytest.raises(ValueError, match="self-intersects"):
        _validated_polygon_coordinates(
            [
                [0.0, 0.0],
                [1.0, 1.0],
                [0.0, 1.0],
                [1.0, 0.0],
            ]
        )


@pytest.mark.asyncio
@pytest.mark.parametrize("building_is_live", [False, True])
async def test_restore_snapshot_skips_deleted_compiled_building_link(monkeypatch, building_is_live) -> None:
    project_id = uuid.uuid4()
    zone_id = uuid.uuid4()
    building_id = uuid.uuid4()
    live_ids = [building_id] if building_is_live else []
    live_result = _query_result(live_ids)
    missing_zone_result = MagicMock()
    missing_zone_result.scalar_one_or_none.return_value = None
    db = SimpleNamespace(
        execute=AsyncMock(side_effect=[live_result, missing_zone_result]),
        add=MagicMock(),
        flush=AsyncMock(),
        refresh=AsyncMock(),
    )
    monkeypatch.setattr("app.api.v1.site_zones.lock_residual_landscape_project", AsyncMock())
    monkeypatch.setattr("app.api.v1.site_zones._invalidate_residual_landscape", AsyncMock())

    restored = await _restore_zone_snapshot(
        db,
        {
            "id": str(zone_id),
            "project_id": str(project_id),
            "zone_type": "building",
            "coordinates": [[0, 0], [1, 0], [1, 1], [0, 1]],
            "properties": {},
            "building_id": str(building_id),
            "building_ids": [str(building_id)],
        },
        project_id=project_id,
        expected_zone_id=zone_id,
    )

    assert restored.id == zone_id
    assert restored.building_id == (building_id if building_is_live else None)
    assert restored.building_ids == ([str(building_id)] if building_is_live else None)
    db.flush.assert_awaited_once()


def test_active_boundary_containment_allows_edge_touching_but_rejects_escape() -> None:
    boundary = Polygon([(0, 0), (10, 0), (10, 10), (0, 10)])
    touching = Polygon([(0, 2), (4, 2), (4, 6), (0, 6)])
    escaped = Polygon([(-0.01, 2), (4, 2), (4, 6), (-0.01, 6)])

    assert _boundary_covers_polygon(boundary, touching)
    assert not _boundary_covers_polygon(boundary, escaped)


@pytest.mark.asyncio
async def test_boundary_change_marks_plans_dna_and_scenarios_stale(monkeypatch) -> None:
    original = Polygon([(0, 0), (2, 0), (2, 2), (0, 2)])
    expanded = Polygon([(-1, -1), (3, -1), (3, 3), (-1, 3)])
    boundary = SimpleNamespace(
        id=uuid.uuid4(),
        project_id=uuid.uuid4(),
        properties={"community_3d_landscape": {"state": "stale"}},
    )
    plan = SimpleNamespace(properties={"_plan_scenario": "economic"})
    manual = SimpleNamespace(properties={"description": "hand drawn"})
    snapshot = SimpleNamespace(
        id=uuid.uuid4(),
        dna={"site_boundary": mapping(original)},
        status="partial",
        error="One optional dataset was unavailable.",
    )
    scenario = SimpleNamespace(
        id=uuid.uuid4(),
        snapshot_id=snapshot.id,
        status="complete",
        error=None,
    )
    db = _boundary_dependents_db(plan, manual, snapshot, scenario)
    monkeypatch.setattr("app.api.v1.site_zones.flag_modified", lambda *_args: None)

    await _invalidate_boundary_dependents(
        db,
        boundary,
        previous_geometry=original,
        current_geometry=expanded,
    )

    assert plan.properties["_plan_boundary_stale"] is True
    assert plan.properties["_plan_boundary_zone_id"] == str(boundary.id)
    assert plan.properties["_plan_boundary_fingerprint"] == plan_boundary_fingerprint(original)
    assert plan.properties["_plan_snapshot_id"] == str(snapshot.id)
    assert "_plan_boundary_stale" not in manual.properties
    assert snapshot.status == "failed"
    assert scenario.status == "failed"
    assert "regenerate Site DNA" in snapshot.error
    restore_state = boundary.properties[PLAN_BOUNDARY_RESTORE_STATE_KEY]
    assert restore_state["source_fingerprint"] == plan_boundary_fingerprint(original)
    assert restore_state["snapshots"][0]["status"] == "partial"
    assert boundary.properties["community_3d_landscape"] == {"state": "stale"}


@pytest.mark.asyncio
async def test_exact_boundary_undo_restores_only_matching_plan_cohort(monkeypatch) -> None:
    original = Polygon([(0, 0), (2, 0), (2, 2), (0, 2)])
    changed = Polygon([(0, 0), (2.25, 0), (2, 2), (0, 2)])
    boundary = SimpleNamespace(id=uuid.uuid4(), project_id=uuid.uuid4(), properties={})
    plan = SimpleNamespace(properties={"_plan_scenario": "economic"})
    other_plan = SimpleNamespace(
        properties={
            "_plan_scenario": "environmental",
            "_plan_boundary_fingerprint": plan_boundary_fingerprint(changed),
        }
    )
    snapshot = SimpleNamespace(
        id=uuid.uuid4(),
        dna={"site_boundary": mapping(original)},
        status="partial",
        error="Original coverage warning",
    )
    scenario = SimpleNamespace(
        id=uuid.uuid4(),
        snapshot_id=snapshot.id,
        status="complete",
        error=None,
    )
    manual = SimpleNamespace(properties={"description": "hand drawn"})
    monkeypatch.setattr("app.api.v1.site_zones.flag_modified", lambda *_args: None)

    await _invalidate_boundary_dependents(
        _boundary_dependents_db(plan, manual, snapshot, scenario),
        boundary,
        previous_geometry=original,
        current_geometry=changed,
    )
    assert plan.properties["_plan_boundary_stale"] is True

    restore_db = SimpleNamespace(
        execute=AsyncMock(
            side_effect=[
                _query_result([plan, other_plan, manual]),
                _query_result([snapshot]),
                _query_result([scenario]),
            ]
        )
    )
    await _invalidate_boundary_dependents(
        restore_db,
        boundary,
        previous_geometry=changed,
        current_geometry=original,
    )

    assert "_plan_boundary_stale" not in plan.properties
    assert other_plan.properties["_plan_boundary_stale"] is True
    assert snapshot.status == "partial"
    assert snapshot.error == "Original coverage warning"
    assert scenario.status == "complete"
    assert scenario.error is None
    assert PLAN_BOUNDARY_RESTORE_STATE_KEY not in boundary.properties


@pytest.mark.asyncio
async def test_authored_zone_change_marks_compiled_residual_landscape_stale(monkeypatch) -> None:
    changed_zone_id = uuid.uuid4()
    boundary = SimpleNamespace(
        id=uuid.uuid4(),
        zone_type="site_boundary",
        properties={
            "community_3d_landscape": {
                "schema_version": 1,
                "state": "compiled",
                "source_hash": "old-plan",
            },
        },
    )

    result = MagicMock()
    result.scalars.return_value.all.return_value = [boundary]
    db = SimpleNamespace(execute=AsyncMock(return_value=result))
    monkeypatch.setattr("app.api.v1.site_zones.flag_modified", lambda *_args: None)

    await _invalidate_residual_landscape(
        db,
        uuid.uuid4(),
        changed_zone_id=changed_zone_id,
        reason="Zone changed",
    )

    recipe = boundary.properties["community_3d_landscape"]
    assert recipe["state"] == "stale"
    assert recipe["source_hash"] == "old-plan"
    assert recipe["changed_zone_id"] == str(changed_zone_id)
    assert recipe["stale_reason"] == "Zone changed"
    assert "stale_at" in recipe


def test_residual_source_identity_ignores_appearance_but_tracks_classification() -> None:
    original = {
        "_plan_role": "open_space",
        "green_space_archetype_id": "pocket-park",
        "park_ground_texture": {"image_url": "first.png"},
    }
    appearance_only = {
        **original,
        "park_ground_texture": {"image_url": "regenerated.png"},
        "community_3d": {"state": "compiled"},
    }

    assert _residual_source_identity("green_space", original) == _residual_source_identity(
        "green_space", appearance_only
    )
    assert _residual_source_identity("green_space", original) != _residual_source_identity(
        "green_space", {**appearance_only, "_plan_role": "framework_height"}
    )
    assert _residual_source_identity("green_space", {}) != _residual_source_identity(
        "green_space", {"development_archetype_id": "mixed-use"}
    )


@pytest.mark.asyncio
async def test_snapshot_restore_marks_residual_recipe_stale(monkeypatch) -> None:
    project_id = uuid.uuid4()
    zone_id = uuid.uuid4()
    zone = SimpleNamespace(id=zone_id, project_id=project_id, zone_type="building")
    boundary = SimpleNamespace(
        id=uuid.uuid4(),
        zone_type="site_boundary",
        properties={"community_3d_landscape": {"state": "compiled", "source_hash": "old"}},
    )

    existing_result = MagicMock()
    existing_result.scalar_one_or_none.return_value = zone
    boundaries_result = MagicMock()
    boundaries_result.scalars.return_value.all.return_value = [boundary]
    first_lock_result = MagicMock()
    invalidation_lock_result = MagicMock()
    db = SimpleNamespace(
        execute=AsyncMock(
            side_effect=[
                first_lock_result,
                existing_result,
                invalidation_lock_result,
                boundaries_result,
            ]
        ),
        flush=AsyncMock(),
        refresh=AsyncMock(),
        add=MagicMock(),
    )
    monkeypatch.setattr("app.api.v1.site_zones.flag_modified", lambda *_args: None)

    restored = await _restore_zone_snapshot(
        db,
        {
            "id": str(zone_id),
            "project_id": str(project_id),
            "zone_type": "building",
            "coordinates": [[-114.08, 51.04], [-114.079, 51.04], [-114.079, 51.041]],
            "properties": {"_plan_role": "building"},
        },
        project_id=project_id,
        expected_zone_id=zone_id,
    )

    assert restored is zone
    assert boundary.properties["community_3d_landscape"]["state"] == "stale"
    assert boundary.properties["community_3d_landscape"]["changed_zone_id"] == str(zone_id)
    db.refresh.assert_awaited_once_with(zone)


def test_safe_int_handles_blank_and_invalid_values() -> None:
    assert _safe_int("", 7) == 7
    assert _safe_int("12", 0) == 12
    assert _safe_int("12.9", 0) == 12
    assert _safe_int("abc", 5) == 5


def test_safe_optional_parsers_handle_invalid_values() -> None:
    assert _safe_optional_int("") is None
    assert _safe_optional_int("4") == 4
    assert _safe_optional_int("4.0") == 4
    assert _safe_optional_int("abc") is None

    assert _safe_optional_float("") is None
    assert _safe_optional_float("4.5") == 4.5
    assert _safe_optional_float("abc") is None


def test_normalize_building_ids_filters_invalid_entries() -> None:
    valid_1 = uuid.uuid4()
    valid_2 = uuid.uuid4()

    normalized = _normalize_building_ids(
        [
            str(valid_1),
            valid_2,
            "not-a-uuid",
            None,
            "",
        ]
    )

    assert normalized == [valid_1, valid_2]


def test_resolve_unit_count_is_robust_to_bad_property_values() -> None:
    residential_zone = SimpleNamespace(
        zone_type="residential",
        properties={"unit_count": "", "description_text": ""},
    )
    assert _resolve_unit_count(residential_zone) == 1

    parsed_zone = SimpleNamespace(
        zone_type="residential",
        properties={"unit_count": "abc", "description_text": "14 homes with front porches"},
    )
    assert _resolve_unit_count(parsed_zone) == 14

    development_zone = SimpleNamespace(
        zone_type="development_area",
        properties={"unit_count": "invalid", "description_text": ""},
    )
    assert _resolve_unit_count(development_zone) == 10
