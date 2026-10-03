import json
import math
from pathlib import Path
from types import SimpleNamespace

import pytest
from shapely.geometry import Polygon

from app.services.building_placement_edges import MANIFEST, building_contact_geometry, building_edge_contracts
from app.services.community_3d_scope import community_3d_building_overlaps


def zone(asset_id="validation_cast_iron_italianate", x=0, y=0, angle=0, width=29, depth=32, **overrides):
    row = building_edge_contracts()[asset_id]
    p = dict(
        pick_place_asset=asset_id,
        native_plot_axes=True,
        native_home_plot=False,
        development_selected_variant_id=row["variantId"],
        pick_place_model_revision=row["revision"],
    )
    p.update(overrides)
    east, r = 111320 * math.cos(math.radians(51)), math.radians(angle)
    c, s = math.cos(r), math.sin(r)
    ring = [
        (-114 + (x + a * c - b * s) / east, 51 + (y + a * s + b * c) / 111320)
        for a, b in ((-width / 2, -depth / 2), (width / 2, -depth / 2), (width / 2, depth / 2), (-width / 2, depth / 2))
    ]
    return SimpleNamespace(id=f"{x}:{y}", zone_type="building", properties=p, geometry=Polygon(ring))


def test_packaged_manifest_matches_browser_policy():
    frontend = Path(__file__).resolve().parents[2] / "frontend/src/data/buildingPlacementEdges.json"
    assert json.loads(MANIFEST.read_text()) == json.loads(frontend.read_text())


@pytest.mark.parametrize("angle", [0, 37, 90, 180])
def test_padded_plots_may_overlap_but_native_buildings_may_not(angle):
    width = building_edge_contracts()["validation_cast_iron_italianate"]["nativeWidthM"]
    r = math.radians(angle)
    a = zone(angle=angle)
    b = zone(x=(width + 0.02) * math.cos(r), y=(width + 0.02) * math.sin(r), angle=angle)
    assert a.geometry.intersection(b.geometry).area > 0
    assert community_3d_building_overlaps([a, b]) == []
    collision = zone(x=(width - 0.5) * math.cos(r), y=(width - 0.5) * math.sin(r), angle=angle)
    assert len(community_3d_building_overlaps([a, collision])) == 1


@pytest.mark.parametrize(
    "props",
    [
        dict(pick_place_model_revision="unknown"),
        dict(native_home_plot=True),
        dict(native_plot_axes=False),
        dict(development_selected_variant_id="unknown"),
        dict(building_footprint_scale=3),
        dict(development_height_override_m=999),
    ],
)
def test_unsupported_bindings_keep_whole_source_polygon(props):
    z = zone(**props)
    assert building_contact_geometry(z, z.geometry) is z.geometry


def test_asymmetric_duplex_keeps_left_access():
    z = zone("clay_montreal_plateau_duplex", width=16, depth=23)
    env = building_contact_geometry(z, z.geometry)
    east = 111320 * math.cos(math.radians(51))
    assert (env.bounds[0] + 114) * east == pytest.approx(-8, abs=0.001)
    assert (env.bounds[2] + 114) * east == pytest.approx(
        building_edge_contracts()[z.properties["pick_place_asset"]]["nativeWidthM"] / 2, abs=0.001
    )


@pytest.mark.parametrize(
    "asset_id",
    [
        "trial_postwar_bungalow",
        "trial_edwardian_foursquare",
        "validation_clapboard_north_end",
        "clay_vancouver_balcony_podium_tower",
    ],
)
def test_supported_heights_preserve_contact_geometry(asset_id):
    row = building_edge_contracts()[asset_id]
    z = zone(asset_id, width=52 if row["plotFit"] else 20, depth=44 if row["plotFit"] else 24)
    original = building_contact_geometry(z, z.geometry)
    assert original is not z.geometry
    for floors in [row["storeyProgram"]["minStoreys"], row["storeyProgram"]["maxStoreys"]]:
        program = row["storeyProgram"]
        height = round(
            program["podiumHeightM"]
            + (floors - program["podiumStoreys"]) * program["repeatedStoreyHeightM"]
            + program["roofHeightM"],
            2,
        )
        z.properties.update(floor_count=floors, development_height_override_m=height)
        assert building_contact_geometry(z, z.geometry).equals_exact(original, 0.000000001)


def test_scaling_and_vancouver_fit_use_model_bounds_not_unscaled_metadata():
    z = zone(
        "trial_postwar_bungalow",
        width=15,
        depth=20,
        building_footprint_scale=1.15,
        building_footprint_program_id="house-flex-pilot-v001",
    )
    env = building_contact_geometry(z, z.geometry)
    assert (51 - env.bounds[1]) * 111320 == pytest.approx(
        building_edge_contracts()[z.properties["pick_place_asset"]]["nativeDepthM"] * 1.15 / 2, abs=0.001
    )
    z = zone("clay_vancouver_balcony_podium_tower", width=57.5, depth=47.5)
    row = building_edge_contracts()[z.properties["pick_place_asset"]]
    scale = round(min(57.5 / row["nativeWidthM"], 47.5 / row["nativeDepthM"], 1.2), 5)
    env = building_contact_geometry(z, z.geometry)
    assert (51 - env.bounds[1]) * 111320 == pytest.approx(row["nativeDepthM"] * scale / 2, abs=0.001)


def test_legacy_custom_and_holey_plots_remain_conservative():
    z = zone()
    points = list(z.geometry.exterior.coords)
    points[1] = (points[1][0] + 0.00005, points[1][1] + 0.00005)
    custom = Polygon(points)
    assert building_contact_geometry(z, custom) is custom
    hole = z.geometry.buffer(-0.00005)
    holey = Polygon(z.geometry.exterior.coords, [hole.exterior.coords])
    assert building_contact_geometry(z, holey) is holey
