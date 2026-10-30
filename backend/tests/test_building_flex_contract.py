import pytest

from app.services.building_flex_contract import trusted_house_footprint_target


def properties(variant="bungalow_postwar_ranch", scale=1.0):
    return {
        "development_selected_variant_id": variant,
        "building_footprint_program_id": "house-flex-pilot-v001",
        "building_footprint_scale": scale,
        # These client values are intentionally false; the server must ignore
        # them and resolve the repository manifest instead.
        "building_footprint_native_width_m": 999,
        "building_footprint_native_depth_m": 999,
    }


def test_resolves_native_dimensions_from_the_trusted_manifest():
    assert trusted_house_footprint_target(properties()) == pytest.approx((10.8983240127563, 16.0500001907349))
    assert trusted_house_footprint_target(properties(scale=1.15)) == pytest.approx(
        (12.533072614669745, 18.457500219345134)
    )


def test_unrelated_properties_keep_the_ordinary_polygon_target():
    assert trusted_house_footprint_target({}) is None
    assert trusted_house_footprint_target({"building_footprint_program_id": "unknown"}) is None


@pytest.mark.parametrize("scale", [0.84, 1.16, float("nan")])
def test_rejects_scales_outside_the_reviewed_band(scale):
    with pytest.raises(ValueError, match="outside the reviewed range"):
        trusted_house_footprint_target(properties(scale=scale))


def test_rejects_a_variant_not_owned_by_the_program():
    with pytest.raises(ValueError, match="not part of this footprint programme"):
        trusted_house_footprint_target(properties(variant="some_other_house"))
