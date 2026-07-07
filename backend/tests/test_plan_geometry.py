"""Plan Geometry Engine — deterministic drawing verified against the P2 gates:
blocks in scale, parcels street-fronting, fire clear-widths pass, honest
degradation on degenerate sites, locked-streets path, ceiling clamps."""

import math

from shapely.geometry import Polygon, mapping

from app.services.plan_geometry.community_rules import MIN_ROW_M, resolve_rules
from app.services.plan_geometry.generator import generate_plan_geometry
from app.services.plan_geometry.parceling import building_mass_for_block, subdivide_block
from app.services.plan_geometry.street_graph import generate_street_network

# ~500 x 340 m site in the Beltline (WGS84)
LAT, LON = 51.0405, -114.0850
M_LAT = 111_320.0
M_LON = M_LAT * math.cos(math.radians(LAT))


def _offset(lon_m, lat_m):
    return (LON + lon_m / M_LON, LAT + lat_m / M_LAT)


def _site(width_m=500.0, depth_m=340.0) -> Polygon:
    return Polygon([_offset(0, 0), _offset(width_m, 0), _offset(width_m, depth_m), _offset(0, depth_m)])


def _road_feature(start, end):
    return {"geometry": mapping(__import__("shapely.geometry", fromlist=["LineString"]).LineString([start, end])),
            "properties": {"full_name": "12 AV SW", "ctp_class": "Arterial Street"}}


PARAMS = {
    "streets.row_width_m": {"value": 16.0},
    "buildings.floors": {"value": 6},
    "buildings.development_type": {"value": "mixed_use"},
    "buildings.development_aesthetic": {"value": "contemporary"},
    "landscape.tree_density": {"value": 0.6},
}


def test_rules_enforce_fire_clear_width_floor():
    rules, notes = resolve_rules("as_of_right", {"streets.row_width_m": {"value": 7.0}})
    assert rules.row_width_m == MIN_ROW_M
    assert rules.clear_width_m >= 6.0
    assert any(n["code"] == "FIRE_CLEAR_WIDTH_FLOOR" for n in notes)


def test_full_generation_meets_p2_gates():
    roads = [
        _road_feature(_offset(-80, 170), _offset(80, 170)),   # entering from the west
        _road_feature(_offset(250, -80), _offset(250, 80)),   # entering from the south
    ]
    result = generate_plan_geometry(
        site_polygon_wgs84=_site(), scenario_id="lap_compliant", scenario_label="LAP Aligned",
        parameters=PARAMS, road_features=roads, district_features=[],
    )

    types = {z["zone_type"] for z in result.zones}
    assert {"road", "green_space", "building"} <= types
    assert result.block_count >= 2
    assert result.parcel_count >= result.block_count  # every block subdivided
    assert all(len(z["coordinates"]) >= 3 for z in result.zones)
    assert all(z["properties"]["_plan_scenario"] == "lap_compliant" for z in result.zones)
    # Plan zones share one layer; height-framework zones form their OWN layer.
    for zone in result.zones:
        expected = ("Height framework — LAP Aligned"
                    if zone["properties"].get("_plan_role") == "framework_height"
                    else "Plan — LAP Aligned")
        assert zone["properties"]["_imported_from"] == expected

    codes = {n["code"] for n in result.notes}
    assert "FIRE_CLEAR_WIDTH_OK" in codes
    assert "PARCELS_LANDLOCKED" not in codes
    assert "MASS_STREET_COLLISION" not in codes

    gi = result.geometry_inputs
    # Land budget closes: streets + open + blocks ≈ gross (small boundary slivers allowed)
    assert abs(gi["row_area_m2"] + gi["open_space_area_m2"] + gi["net_block_area_m2"]
               - gi["site_area_m2"]) / gi["site_area_m2"] < 0.06
    assert gi["building_footprint_m2"] > 0
    assert gi["gfa_m2"] >= gi["building_footprint_m2"] * 5  # ~6 storeys

    buildings = [z for z in result.zones if z["zone_type"] == "building"]
    assert all(z["properties"]["floors"] > 0 and z["properties"]["height"] > 0 for z in buildings)
    assert result.intersection_density_per_km2 > 0

    # Semantic hints for the render pipeline's archetype resolver.
    assert all(z["properties"]["development_type"] == "mixed_use" for z in buildings)
    assert all(z["properties"]["development_aesthetic"] == "contemporary" for z in buildings)
    parks = [z for z in result.zones if z["zone_type"] == "green_space"]
    assert parks and all(z["properties"]["tree_density"] == 0.6 for z in parks)


def test_block_scale_via_street_network():
    from app.services.site_engine import (
        build_transformer, cleanup_developable_blocks, local_metric_crs_for_polygon, project_geometry,
    )

    site = _site()
    crs = local_metric_crs_for_polygon(site)
    boundary_m = project_geometry(site, build_transformer("EPSG:4326", crs))
    rules, _ = resolve_rules("lap_compliant", PARAMS)
    network = generate_street_network(boundary_m, rules, [])
    # Same morphological opening the generator applies (hairline-bridge severing).
    developable = boundary_m.difference(network.street_area).buffer(-0.05).buffer(0.05)
    blocks = cleanup_developable_blocks(developable, sliver_area_threshold=400)
    assert len(blocks) >= 4
    for block in blocks:
        rect = block.minimum_rotated_rectangle
        coords = list(rect.exterior.coords)
        long_edge = max(math.hypot(x2 - x1, y2 - y1)
                        for (x1, y1), (x2, y2) in zip(coords[:-1], coords[1:]))
        assert long_edge <= rules.block_target_m + rules.row_width_m + 1.0


def test_parcels_front_the_street_and_slivers_merge():
    block = Polygon([(0, 0), (180, 0), (180, 70), (0, 70)])
    parcels = subdivide_block(block, 22.0)
    assert 6 <= len(parcels) <= 10
    assert all(p.area >= 120.0 for p in parcels)
    for parcel in parcels:
        assert parcel.distance(block.exterior) < 0.5  # street-fronting


def test_building_mass_respects_coverage_cap():
    from app.services.plan_geometry.community_rules import resolve_rules as rr
    rules, _ = rr("climate_first", PARAMS)  # coverage 0.45
    block = Polygon([(0, 0), (150, 0), (150, 120), (0, 120)])
    mass, info = building_mass_for_block(block, rules)
    assert mass is not None
    assert info["coverage_of_block"] <= rules.coverage_ratio + 0.05


def test_tiny_site_degrades_to_single_block_plan():
    result = generate_plan_geometry(
        site_polygon_wgs84=_site(60, 45), scenario_id="as_of_right", scenario_label="AoR",
        parameters=PARAMS, road_features=[], district_features=[],
    )
    codes = {n["code"] for n in result.notes}
    assert codes & {"SITE_TOO_SMALL", "NO_INTERNAL_STREETS"}
    assert result.block_count == 1
    assert any(z["zone_type"] == "building" for z in result.zones)  # still buildable


def test_locked_streets_are_reused_not_regenerated():
    site = _site()
    first = generate_plan_geometry(
        site_polygon_wgs84=site, scenario_id="lap_compliant", scenario_label="LAP",
        parameters=PARAMS, road_features=[], district_features=[],
    )
    street_rings = [z["coordinates"] for z in first.zones if z["zone_type"] == "road"]
    assert street_rings
    from shapely.ops import unary_union
    locked = unary_union([Polygon(r) for r in street_rings])

    second = generate_plan_geometry(
        site_polygon_wgs84=site, scenario_id="lap_compliant", scenario_label="LAP",
        parameters={**PARAMS, "streets.row_width_m": {"value": 20.0}},  # would change streets if unlocked
        road_features=[], district_features=[], locked_street_area_wgs84=locked,
    )
    assert any(n["code"] == "STREETS_LOCKED" for n in second.notes)
    locked_area = locked.area
    second_street_area = sum(
        Polygon(z["coordinates"]).area for z in second.zones if z["zone_type"] == "road"
    )
    assert abs(second_street_area - locked_area) / locked_area < 0.02  # same network


def test_height_framework_zones_are_emitted_per_block():
    result = generate_plan_geometry(
        site_polygon_wgs84=_site(), scenario_id="lap_compliant", scenario_label="LAP",
        parameters=PARAMS, road_features=[], district_features=[],
    )
    framework = [z for z in result.zones if z["properties"].get("_plan_role") == "framework_height"]
    assert len(framework) == result.block_count           # one banded sub-area per block
    assert all(z["zone_type"] == "development_area" for z in framework)
    assert all(z["properties"]["max_floors"] > 0 for z in framework)
    assert all(z["properties"]["_imported_from"] == "Height framework — LAP" for z in framework)
    assert all("storeys" in z["name"] for z in framework)


def test_plan_sheet_builds_measurable_html():
    from app.services.plan_geometry.plan_sheet import build_plan_sheet

    result = generate_plan_geometry(
        site_polygon_wgs84=_site(), scenario_id="lap_compliant", scenario_label="LAP",
        parameters=PARAMS, road_features=[], district_features=[],
    )
    plan_zones = [
        {"role": z["properties"]["_plan_role"], "coordinates": z["coordinates"],
         "floors": z["properties"].get("floors")}
        for z in result.zones
        if z["properties"].get("_plan_role") in ("street", "open_space", "building")
    ]
    sheet = build_plan_sheet(
        scenario_label="LAP Aligned", scenario_id="lap_compliant",
        payload={
            "plan": {"status": "complete", "generated_at": "t", "final_score": 0.95,
                     "iterations": [{"iteration": 1, "overall_score": 0.95, "scores": {}, "revisions": []}],
                     "geometry_inputs": result.geometry_inputs, "rules": result.rules,
                     "block_count": result.block_count, "parcel_count": result.parcel_count,
                     "intersection_density_per_km2": 40.0, "notes": result.notes},
            "metrics": {"metrics": {"gfa_m2": {"label": "Gross floor area", "value": 100000,
                                               "unit": "m2", "derivation": "footprint × storeys"}},
                        "ceiling_reconciliation": [], "assumptions_used": {}},
            "trade_offs": [{"message": "narrow vs fire access"}],
        },
        boundary_wgs84=_site(), plan_zones=plan_zones, dna=None,
        snapshot_meta={"snapshot_id": "snap", "city_id": "calgary", "overall_confidence": 1.0},
    )
    assert "ILLUSTRATIVE — NOT AN APPROVED DESIGN" in sheet
    assert "<svg viewBox=" in sheet and "100 m" in sheet     # measurable drawing + scale bar
    assert "footprint × storeys" in sheet                     # derivations on the sheet
    assert "narrow vs fire access" in sheet
    assert sheet.count("<polygon") >= len(plan_zones)


def test_hearing_pack_pairs_renders_with_drawing_and_numbers():
    from app.services.plan_geometry.hearing_pack import build_hearing_pack
    from app.services.plan_geometry.plan_diagram import render_plan_diagram_png

    result = generate_plan_geometry(
        site_polygon_wgs84=_site(), scenario_id="climate_first", scenario_label="Climate First",
        parameters=PARAMS, road_features=[], district_features=[],
    )
    plan_zones = [
        {"role": z["properties"]["_plan_role"], "coordinates": z["coordinates"],
         "floors": z["properties"].get("floors")}
        for z in result.zones
        if z["properties"].get("_plan_role") in ("street", "open_space", "building")
    ]
    payload = {
        "plan": {"status": "complete", "final_score": 0.99,
                 "geometry_inputs": result.geometry_inputs, "rules": result.rules,
                 "block_count": result.block_count, "parcel_count": result.parcel_count},
        "metrics": {"metrics": {"units": {"label": "Units", "value": 2100, "unit": "units"}},
                    "assumptions_used": {}},
        "trade_offs": [{"message": "canopy vs parking supply"}],
    }
    tiny_png = render_plan_diagram_png(_site(), plan_zones, size_px=64)
    pack = build_hearing_pack(
        scenario_label="Climate First", scenario_id="climate_first",
        payload=payload, boundary_wgs84=_site(), plan_zones=plan_zones,
        dna=None,
        snapshot_meta={"snapshot_id": "snap", "city_id": "calgary", "overall_confidence": 1.0},
        diagram_png=tiny_png,
        renders=[{"png": tiny_png, "style": "Gemini / photorealistic", "created_at": "2026-07-07T00:00:00"}],
        sibling_scenarios=[
            {"label": "As-of-Right", "scenario_id": "as_of_right", "payload": payload},
            {"label": "Climate First", "scenario_id": "climate_first", "payload": payload},
        ],
    )
    assert "ILLUSTRATIVE — NOT AN APPROVED DESIGN" in pack
    assert "<svg viewBox=" in pack                        # to-scale drawing
    assert pack.count("data:image/png;base64,") >= 2      # diagram + render embedded
    assert "Scenario comparison" in pack and "Plan score" in pack
    assert "canopy vs parking supply" in pack
    assert "watermarked and provenance-tagged" in pack


def test_saved_render_watermark_and_provenance():
    from io import BytesIO

    from PIL import Image

    from app.api.v1.render import SaveRenderRequest, _watermark_and_provenance

    source = Image.new("RGB", (640, 360), (200, 200, 200))
    buffer = BytesIO()
    source.save(buffer, format="PNG")
    req = SaveRenderRequest(image_base64="ignored", prompt="test prompt",
                            style="photorealistic", seed=42, model="gemini")
    out_bytes = _watermark_and_provenance(buffer.getvalue(), req)

    out = Image.open(BytesIO(out_bytes))
    assert out.size == (640, 360)
    provenance = out.text.get("cityprompt:provenance")   # PNG tEXt chunk
    assert provenance and "NOT an approved design" not in provenance  # sanity: JSON not prose
    assert '"model": "gemini"' in provenance and '"seed": 42' in provenance
    # The banner darkens the bottom-left corner region.
    corner = out.convert("RGB").crop((0, 320, 200, 360))
    avg = sum(sum(px) / 3 for px in corner.getdata()) / (200 * 40)
    assert avg < 195  # plain source was uniform 200-grey


def test_courtyard_masses_decompose_into_hole_free_bars():
    # Zone coordinates are single-ring app-wide: a holed perimeter-ring mass
    # serialized by its exterior would draw as a SOLID slab (~2x the reported
    # footprint). The decomposition must yield simple bars whose summed area
    # still matches the reported footprint.
    from app.services.site_engine import iter_polygons

    rules, _ = resolve_rules("lap_compliant", PARAMS)
    block = Polygon([(0, 0), (200, 0), (200, 160), (0, 160)])  # big enough to ring
    mass, info = building_mass_for_block(block, rules)
    assert mass is not None
    polys = list(iter_polygons(mass))
    assert all(not p.interiors for p in polys)          # hole-free
    assert len(polys) >= 2                              # actually decomposed
    total = sum(p.area for p in polys)
    assert abs(total - info["footprint_m2"]) / info["footprint_m2"] < 0.02
    assert total < 0.85 * block.area                    # not a courtyard-less slab


def test_building_zone_exteriors_match_reported_footprint():
    # End-to-end version of the courtyard guarantee: the area a user SEES
    # (drawn zone exteriors) must equal the footprint the statistics report.
    from app.services.site_engine import (
        build_transformer, local_metric_crs_for_polygon, project_geometry,
    )

    result = generate_plan_geometry(
        site_polygon_wgs84=_site(), scenario_id="lap_compliant", scenario_label="LAP Aligned",
        parameters=PARAMS, road_features=[], district_features=[],
    )
    tf = build_transformer("EPSG:4326", local_metric_crs_for_polygon(_site()))
    drawn = 0.0
    for zone in result.zones:
        if zone["zone_type"] != "building":
            continue
        poly = Polygon(zone["coordinates"])
        assert poly.is_valid and len(poly.interiors) == 0
        drawn += project_geometry(poly, tf).area
    gi = result.geometry_inputs
    assert gi["building_footprint_m2"] > 0
    assert abs(drawn - gi["building_footprint_m2"]) / gi["building_footprint_m2"] < 0.05


def test_plan_diagram_is_flat_palette_nadir_png():
    # Conditioning input rules (diagram research): flat colors only, no text,
    # no anti-aliasing artifacts — every pixel must belong to the palette.
    from io import BytesIO

    from PIL import Image

    from app.services.plan_geometry.plan_diagram import DIAGRAM_COLORS, render_plan_diagram_png

    result = generate_plan_geometry(
        site_polygon_wgs84=_site(), scenario_id="climate_first", scenario_label="Climate First",
        parameters=PARAMS, road_features=[], district_features=[],
    )
    plan_zones = [
        {"role": z["properties"]["_plan_role"], "coordinates": z["coordinates"]}
        for z in result.zones
        if z["properties"].get("_plan_role") in ("street", "open_space", "building")
    ]
    png = render_plan_diagram_png(_site(), plan_zones, size_px=512)
    img = Image.open(BytesIO(png))
    assert img.size == (512, 512)
    colors = {color for _count, color in img.getcolors(maxcolors=1_000_000)}
    assert colors <= set(DIAGRAM_COLORS.values())
    assert DIAGRAM_COLORS["street"] in colors
    assert DIAGRAM_COLORS["building"] in colors
    assert DIAGRAM_COLORS["open_space"] in colors


def test_floors_clamped_by_district_ceiling():
    district = {
        "geometry": mapping(_site(1000, 1000)),  # covers everything
        "properties": {"lu_code": "CC-MH", "height": 19.2},  # 6 storeys at 3.2 m
    }
    result = generate_plan_geometry(
        site_polygon_wgs84=_site(), scenario_id="as_of_right", scenario_label="AoR",
        parameters={**PARAMS, "buildings.floors": {"value": 20}},
        road_features=[], district_features=[district],
    )
    buildings = [z for z in result.zones if z["zone_type"] == "building"]
    assert buildings
    assert all(z["properties"]["floors"] <= 6.01 for z in buildings)
    assert any(n["code"] == "FLOORS_CLAMPED" for n in result.notes)
