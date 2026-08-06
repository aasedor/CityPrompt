from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from shapely.geometry import box

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
