from types import SimpleNamespace
from unittest.mock import AsyncMock
import uuid

import pytest
from fastapi import HTTPException
from shapely.geometry import box

from app.api.v1 import site_zones
from app.api.v1.site_zones import _assert_optional_boundary_covers


def test_authored_zone_does_not_require_a_site_boundary():
    _assert_optional_boundary_covers(
        None,
        box(10, 10, 11, 11),
        detail="outside",
    )


def test_existing_site_boundary_remains_authoritative():
    boundary = SimpleNamespace(geometry=box(0, 0, 5, 5))

    _assert_optional_boundary_covers(
        boundary,
        box(1, 1, 2, 2),
        detail="outside",
    )

    with pytest.raises(HTTPException) as exc_info:
        _assert_optional_boundary_covers(
            boundary,
            box(10, 10, 11, 11),
            detail="outside",
        )

    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == "outside"


@pytest.mark.anyio
async def test_boundary_exclusion_names_unnamed_student_objects(monkeypatch):
    project_id = uuid.uuid4()
    zones = [
        SimpleNamespace(zone_type="green_space", name=None, properties={}, geometry=box(1, 1, 2, 2)),
        SimpleNamespace(zone_type="road", name=None, properties={
            "road_selected_variant_id": "yield_street_v0", "width": 6,
        }, geometry=box(8, 8, 12, 12)),
        SimpleNamespace(zone_type="building", name="Tower", properties={}, geometry=box(11, 1, 12, 2)),
    ]
    result = SimpleNamespace(scalars=lambda: SimpleNamespace(all=lambda: zones))
    db = SimpleNamespace(execute=AsyncMock(return_value=result))
    monkeypatch.setattr(site_zones, "to_shape", lambda geometry: geometry)
    monkeypatch.setattr(site_zones, "public_road_connection_fits", lambda *args: False)

    with pytest.raises(HTTPException) as exc_info:
        await site_zones._assert_boundary_covers_existing_zones(db, project_id, box(0, 0, 10, 10))

    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == (
        "The site boundary must contain every authored zone. "
        "Outside the proposed boundary: Street #1 (Yield Street, 6 m), Tower."
    )
