"""Unit tests for site zone generation utility helpers."""

import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.api.v1.site_zones import (
    _coordinates_materially_changed,
    _invalidate_boundary_dependents,
    _normalize_building_ids,
    _resolve_unit_count,
    _safe_int,
    _safe_optional_float,
    _safe_optional_int,
    _validated_polygon_coordinates,
)


def test_boundary_coordinate_change_ignores_closing_point_and_float_noise() -> None:
    before = [[0.0, 0.0], [2.0, 0.0], [2.0, 2.0], [0.0, 0.0]]
    same_open_ring = [[0.0, 0.0], [2.0 + 1e-10, 0.0], [2.0, 2.0]]
    moved = [[0.0, 0.0], [2.01, 0.0], [2.0, 2.0]]

    assert not _coordinates_materially_changed(before, same_open_ring)
    assert _coordinates_materially_changed(before, moved)
    assert _coordinates_materially_changed(before, moved + [[0.0, 0.0]])


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
        _validated_polygon_coordinates([
            [0.0, 0.0],
            [1.0, 1.0],
            [0.0, 1.0],
            [1.0, 0.0],
        ])


@pytest.mark.asyncio
async def test_boundary_change_marks_plans_dna_and_scenarios_stale(monkeypatch) -> None:
    boundary = SimpleNamespace(id=uuid.uuid4(), project_id=uuid.uuid4())
    plan = SimpleNamespace(properties={"_plan_scenario": "economic"})
    manual = SimpleNamespace(properties={"description": "hand drawn"})
    snapshot = SimpleNamespace(id=uuid.uuid4(), status="complete", error=None)
    scenario = SimpleNamespace(status="complete", error=None)

    def result_for(items):
        result = MagicMock()
        result.scalars.return_value.all.return_value = items
        return result

    db = SimpleNamespace(execute=AsyncMock(side_effect=[
        result_for([plan, manual]),
        result_for([snapshot]),
        result_for([scenario]),
    ]))
    monkeypatch.setattr("app.api.v1.site_zones.flag_modified", lambda *_args: None)

    await _invalidate_boundary_dependents(db, boundary)

    assert plan.properties["_plan_boundary_stale"] is True
    assert plan.properties["_plan_boundary_zone_id"] == str(boundary.id)
    assert "_plan_boundary_stale" not in manual.properties
    assert snapshot.status == "failed"
    assert scenario.status == "failed"
    assert "regenerate Site DNA" in snapshot.error


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

    normalized = _normalize_building_ids([
        str(valid_1),
        valid_2,
        "not-a-uuid",
        None,
        "",
    ])

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
