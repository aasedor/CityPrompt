from types import SimpleNamespace

import pytest

from app.api.v1.site_zones import _validate_park_ground


@pytest.mark.parametrize("height", [0, -3.5, 1046.2])
def test_standalone_park_uses_its_own_saved_placement_elevation(height):
    _validate_park_ground({"terrain_elevation_m": height}, None)


@pytest.mark.parametrize("height", [None, True, "1046", float("nan"), float("inf")])
def test_standalone_park_never_invents_an_elevation(height):
    with pytest.raises(ValueError, match="ground"):
        _validate_park_ground({"terrain_elevation_m": height}, None)


def test_retained_or_natural_ground_is_not_claimed_as_a_prepared_park():
    for props in [
        {"community_3d_mask_existing_tiles": False},
        {"terrain_strategy": "landscape"},
        {"park_terrain": {"version": 1}},
    ]:
        with pytest.raises(ValueError):
            _validate_park_ground({"terrain_elevation_m": 1000, **props}, None)


def test_existing_boundary_remains_authoritative():
    _validate_park_ground({}, SimpleNamespace(properties={"community_3d_mask_existing_tiles": True}))
    for props in [{"community_3d_mask_existing_tiles": False}, {"terrain_strategy": "landscape"}, {}]:
        with pytest.raises(ValueError, match="prepared level site"):
            _validate_park_ground({"terrain_elevation_m": 1000}, SimpleNamespace(properties=props))
