"""Placement policy — strategic per-zone variety verified: deterministic
tagging, density transect, street hierarchy, park mix, typology massing,
laneways/pond/roundabouts, and graceful degradation on locked streets."""

import json
import math
from pathlib import Path

from shapely.geometry import Polygon

from app.services.plan_geometry.community_rules import LANE_ROW_M, MIN_ROW_M
from app.services.plan_geometry.generator import generate_plan_geometry
from app.services.plan_geometry.placement import (
    CATALOG_DEV_TYPES,
    PALETTES,
    Palette,
    runtime_lego_rectangle_fit,
    selected_target_footprint,
)
from app.services.site_engine import (
    build_transformer,
    local_metric_crs_for_polygon,
    project_geometry,
)

LAT, LON = 51.0405, -114.0850
M_LAT = 111_320.0
M_LON = M_LAT * math.cos(math.radians(LAT))


def _offset(lon_m, lat_m):
    return (LON + lon_m / M_LON, LAT + lat_m / M_LAT)


def _site(width_m=700.0, depth_m=520.0) -> Polygon:
    return Polygon([_offset(0, 0), _offset(width_m, 0), _offset(width_m, depth_m), _offset(0, depth_m)])


PARAMS = {
    "streets.row_width_m": {"value": 16.0},
    "buildings.floors": {"value": 6},
    "buildings.development_type": {"value": "mixed_use"},
    "buildings.development_aesthetic": {"value": "contemporary"},
    "landscape.tree_density": {"value": 0.6},
}


def _generate(scenario_id="climate_first", label="Climate First", site=None, params=None):
    return generate_plan_geometry(
        site_polygon_wgs84=site or _site(),
        scenario_id=scenario_id,
        scenario_label=label,
        parameters=params or PARAMS,
        road_features=[],
        district_features=[],
    )


def _metric_area(zone, site) -> float:
    tf = build_transformer("EPSG:4326", local_metric_crs_for_polygon(site))
    return project_geometry(Polygon(zone["coordinates"]), tf).area


def _catalog_ids(filename: str) -> set[str]:
    repo_root = Path(__file__).resolve().parents[2]
    payload = json.loads((repo_root / "frontend" / "src" / "data" / filename).read_text(encoding="utf-8"))
    return {str(item["id"]) for item in payload["archetypes"]}


def test_block_plans_resolve_archetypes_before_massing():
    from app.services.plan_geometry.archetypes import load_dims_table

    known_ids = {e["id"] for e in load_dims_table()}
    result = _generate()
    buildings = [z for z in result.zones if z["properties"].get("_plan_role") == "building"]
    assert buildings
    # Every emitted building zone resolved to a real catalog archetype.
    for z in buildings:
        arch = z["properties"].get("development_archetype_id")
        assert arch in known_ids, f"unresolved archetype for {z['name']}: {arch!r}"


def test_every_generated_public_realm_zone_has_a_valid_catalog_archetype():
    street_ids = _catalog_ids("streetPathArchetypes.json")
    open_space_ids = _catalog_ids("openSpaceArchetypes.json")
    courtyard_count = 0

    for scenario_id in sorted(PALETTES):
        result = _generate(scenario_id, scenario_id.replace("_", " ").title())
        roads = [zone for zone in result.zones if zone["zone_type"] == "road"]
        greens = [zone for zone in result.zones if zone["zone_type"] == "green_space"]
        assert roads, scenario_id
        assert greens, scenario_id

        for zone in roads:
            archetype_id = zone["properties"].get("road_archetype_id")
            assert archetype_id in street_ids, (
                scenario_id,
                zone["name"],
                archetype_id,
            )

        for zone in greens:
            archetype_id = zone["properties"].get("green_space_archetype_id")
            assert archetype_id in open_space_ids, (
                scenario_id,
                zone["name"],
                archetype_id,
            )
            if zone["properties"].get("_plan_role") == "courtyard":
                courtyard_count += 1

    assert courtyard_count > 0


def test_measured_dims_change_target_not_archetype():
    from app.services.plan_geometry.archetypes import MeasuredEntry

    base = _generate()
    base_buildings = {
        z["name"]: z["properties"].get("development_archetype_id")
        for z in base.zones
        if z["properties"].get("_plan_role") == "building"
    }
    arch_ids = {a for a in base_buildings.values() if a}
    fake_measured = {
        arch: MeasuredEntry(
            variant_id="default",
            dimensions={"long_per_height": 2.0, "short_per_height": 1.0, "aspect": 2.0},
        )
        for arch in arch_ids
    }
    measured_run = generate_plan_geometry(
        site_polygon_wgs84=_site(),
        scenario_id="climate_first",
        scenario_label="Climate First",
        parameters=PARAMS,
        road_features=[],
        district_features=[],
        measured_model_dims=fake_measured,
    )
    measured_buildings = {
        z["name"]: z["properties"].get("development_archetype_id")
        for z in measured_run.zones
        if z["properties"].get("_plan_role") == "building"
    }
    # Same archetype choices; only parcel geometry may differ.
    assert set(base_buildings.values()) == set(measured_buildings.values())


def test_runtime_lego_variant_native_dimensions_override_parent_card():
    from app.services.plan_geometry.archetypes import dims_by_id

    entry = dims_by_id()["london_heritage_mansion_block"]
    palette = Palette(
        bands={},
        allowed_archetype_ids=frozenset({entry["id"]}),
        target_dimensions_by_selectable_id={
            "london-heritage-mansion-portland-stone": (45.0, 27.0),
        },
    )

    target = selected_target_footprint(
        entry,
        5,
        None,
        palette,
        "london-heritage-mansion-portland-stone",
    )

    assert target is not None
    assert (target.width_m, target.depth_m, target.source) == (
        45.0,
        27.0,
        "runtime_lego",
    )


def test_runtime_alternates_allow_uniform_resize_but_reject_axis_distortion():
    # A 15x8 rowhouse fits a 13x7 cell with an almost uniform ~87% scale.
    assert runtime_lego_rectangle_fit(13.0, 7.0, 15.0, 8.0)
    # A 12x8 townhouse would need roughly 108% on one authored axis and 88%
    # on the other, visibly warping openings and facade textures.
    assert not runtime_lego_rectangle_fit(13.0, 7.0, 12.0, 8.0)


def _rect_stats(zone, site):
    """(aspect, rect_fill) of the zone's minimum rotated rectangle, metric."""
    tf = build_transformer("EPSG:4326", local_metric_crs_for_polygon(site))
    poly = project_geometry(Polygon(zone["coordinates"]), tf)
    rect = poly.minimum_rotated_rectangle
    coords = list(rect.exterior.coords)
    e1 = math.hypot(coords[1][0] - coords[0][0], coords[1][1] - coords[0][1])
    e2 = math.hypot(coords[2][0] - coords[1][0], coords[2][1] - coords[1][1])
    long_e, short_e = max(e1, e2), min(e1, e2)
    return (long_e / max(short_e, 0.01), poly.area / max(rect.area, 0.01))


def test_targeted_buildings_are_rectangular_modules():
    site = _site()
    result = _generate(site=site)
    targeted = [
        z for z in result.zones if z["properties"].get("_plan_role") == "building" and z["properties"].get("target_w_m")
    ]
    assert targeted, "expected model-targeted building zones"
    for z in targeted:
        aspect, rect_fill = _rect_stats(z, site)
        props = z["properties"]
        # Compare long/short both sides; the carved module may be batched up
        # to the effective module width (module_w_m) on small-unit archetypes
        # and stretched when a bar hits MAX_MODULES_PER_BAR.
        mod_w = props.get("module_w_m") or props["target_w_m"]
        mod_d = props.get("module_d_m") or props["target_d_m"]
        target_aspect = max(mod_w, mod_d) / max(min(mod_w, mod_d), 0.01)
        # No L-shapes: each module must essentially fill its bounding rect...
        assert rect_fill >= 0.65, f"{z['name']}: rect_fill {rect_fill:.2f}"
        # ...and stay within stretch tolerance of the carved module, with an
        # absolute rail for capped bars on oversized test blocks.
        assert aspect <= max(
            target_aspect * 1.6 + 0.35, 4.5
        ), f"{z['name']}: aspect {aspect:.2f} vs module {target_aspect:.2f}"


def test_module_widths_track_archetype_target():
    site = _site()
    result = _generate(site=site)
    tf = build_transformer("EPSG:4326", local_metric_crs_for_polygon(site))
    checked = 0
    for z in result.zones:
        props = z["properties"]
        if props.get("_plan_role") != "building" or not props.get("module_w_m"):
            continue
        poly = project_geometry(Polygon(z["coordinates"]), tf)
        rect = poly.minimum_rotated_rectangle
        coords = list(rect.exterior.coords)
        e1 = math.hypot(coords[1][0] - coords[0][0], coords[1][1] - coords[0][1])
        e2 = math.hypot(coords[2][0] - coords[1][0], coords[2][1] - coords[1][1])
        long_e = max(e1, e2)
        # Modules within stretch tolerance of the EFFECTIVE width, with the
        # MAX_MODULES_PER_BAR stretch rail for oversized test blocks.
        assert long_e <= max(
            props["module_w_m"] * 1.6, props["module_d_m"] * 4.5
        ), f"{z['name']}: {long_e:.1f}m module vs module_w {props['module_w_m']}m"
        checked += 1
    assert checked > 0


def test_zone_count_stays_bounded():
    # The 700x520m test site is an adversarial superblock district; real
    # sites are far smaller. MAX_MODULES_PER_BAR and MAX_BLOCKS_PER_AXIS guard
    # the ceiling — this asserts no runaway, not a target density. The finer
    # inner-city grain (subdivision guarantee + courtyard cap) legitimately
    # raises the count here (~27 blocks x ~12 ring bars); a true runaway would
    # be in the thousands.
    # Faithful footprints + 12 m fine-grain modules land ~15-16 buildings per
    # block here (~27 blocks); a true runaway would be thousands.
    result = _generate()
    buildings = [z for z in result.zones if z["properties"].get("_plan_role") == "building"]
    assert len(buildings) < 600, f"module segmentation exploded: {len(buildings)} building zones"


def test_generation_is_deterministic():
    a = _generate()
    b = _generate()
    assert [(z["name"], z["properties"]) for z in a.zones] == [(z["name"], z["properties"]) for z in b.zones]
    assert [z["coordinates"] for z in a.zones] == [z["coordinates"] for z in b.zones]


def test_transect_bands_and_single_anchor():
    result = _generate()
    buildings = [z for z in result.zones if z["properties"].get("_plan_role") == "building"]
    bands = {z["properties"]["_plan_band"] for z in buildings}
    assert "edge" in bands

    # Edge steps down; every type comes from the catalog; real variety.
    edge_floors = [z["properties"]["floors"] for z in buildings if z["properties"]["_plan_band"] == "edge"]
    other_floors = [
        z["properties"]["floors"] for z in buildings if z["properties"]["_plan_band"] not in ("edge", "anchor")
    ]
    assert edge_floors and max(edge_floors) <= 3.5
    assert other_floors and max(other_floors) > max(edge_floors)

    dev_types = {z["properties"]["development_type"] for z in buildings}
    assert dev_types <= CATALOG_DEV_TYPES
    assert len(dev_types) >= 3

    # Exactly one anchor BLOCK (its mass may decompose into several zones).
    anchor_blocks = {z["name"].split(" · Building")[0] for z in buildings if z["properties"]["_plan_band"] == "anchor"}
    assert len(anchor_blocks) == 1


def test_street_hierarchy_spine_and_locals():
    result = _generate()
    roads = [z for z in result.zones if z["zone_type"] == "road"]
    spine = [z for z in roads if z["properties"].get("street_role") == "spine"]
    locals_ = [z for z in roads if z["properties"].get("street_role") == "local"]
    assert all(z["properties"].get("road_archetype_id") for z in roads)
    assert spine and all(z["properties"]["width"] >= 22.0 for z in spine)
    assert locals_ and all(MIN_ROW_M <= z["properties"]["width"] < 15.0 for z in locals_)

    # as_of_right stamps the arterial directly (unreachable via width bands).
    aor = _generate("as_of_right", "AoR")
    aor_spine = [z for z in aor.zones if z["properties"].get("street_role") == "spine"]
    assert aor_spine and all(z["properties"]["road_archetype_id"] == "arterial_boulevard" for z in aor_spine)


def test_park_mix_and_archetype_fallback_stamps():
    site = _site()
    result = _generate(site=site)
    greens = [z for z in result.zones if z["properties"].get("_plan_role") == "open_space"]
    assert greens
    # The old "resolver gap" is closed: every plan green now carries a catalog
    # id (central/pocket get generator fallbacks so the globe park kit
    # resolves a real furniture recipe instead of the trees-only default).
    assert all(z["properties"].get("green_space_archetype_id") for z in greens)
    by_kind: dict[str, set[str]] = {}
    for z in greens:
        by_kind.setdefault(str(z["properties"].get("green_kind")), set()).add(
            z["properties"]["green_space_archetype_id"]
        )
    if "central" in by_kind:
        assert by_kind["central"] == {"neighborhood_park"}
    if "pocket" in by_kind:
        assert by_kind["pocket"] == {"urban_pocket_park"}
    # Water/linear/plaza ids are untouched by the fallback.
    assert by_kind.get("pond", set()) <= {"stormwater_retention_pond", "fountain_water_feature"}
    assert by_kind.get("greenway", set()) <= {"linear_park_greenway"}
    assert by_kind.get("plaza", set()) <= {"formal_civic_plaza"}
    # Park mix still spans the neighborhood and pocket size bands.
    park_areas = [_metric_area(z, site) for z in greens if z["properties"].get("green_kind") in ("central", "pocket")]
    assert any(a >= 2000.0 for a in park_areas)
    assert any(a <= 900.0 for a in park_areas)


def test_every_generated_public_realm_zone_has_an_explicit_catalog_identity():
    result = _generate()
    roads = [zone for zone in result.zones if zone["zone_type"] == "road"]
    greens = [zone for zone in result.zones if zone["zone_type"] == "green_space"]

    assert roads and all(zone["properties"].get("road_archetype_id") for zone in roads)
    assert greens and all(zone["properties"].get("green_space_archetype_id") for zone in greens)


def test_palette_stays_under_render_caps():
    result = _generate()
    buildings = [z for z in result.zones if z["properties"].get("_plan_role") == "building"]
    triples = {
        (z["properties"]["development_type"], z["properties"]["development_aesthetic"], z["properties"]["floors"])
        for z in buildings
    }
    assert len(triples) <= 6
    ids = {z["properties"].get("road_archetype_id") for z in result.zones} | {
        z["properties"].get("green_space_archetype_id") for z in result.zones
    }
    assert len(triples) + len(ids - {None}) + 3 <= 16  # + street bands; GPT keeps 15 refs


def test_typology_masses_are_hole_free_and_courtyards_only_on_perimeter():
    for scenario in ("climate_first", "as_of_right", "lap_compliant"):
        result = _generate(scenario, scenario)
        buildings = [z for z in result.zones if z["properties"].get("_plan_role") == "building"]
        assert buildings
        for zone in buildings:
            poly = Polygon(zone["coordinates"])
            assert poly.is_valid and len(poly.interiors) == 0
            # Faithful footprints: depth comes from archetype metadata under a
            # loose SEAL cap (0.92) — solid blocks legitimately reach ~0.85.
            assert zone["properties"]["coverage_of_block"] <= 0.92 + 0.02
        # Courtyards may only come from perimeter-typology blocks.
        perimeter_blocks = {
            z["name"].split(" · Building")[0] for z in buildings if z["properties"].get("typology") == "perimeter_block"
        }
        for zone in result.zones:
            if zone["properties"].get("_plan_role") != "courtyard":
                continue
            block_name = zone["name"].rsplit(" courtyard", 1)[0]
            assert block_name in perimeter_blocks


def test_phase3_lanes_pond_roundabout_and_budget():
    site = _site()
    result = _generate(site=site)  # climate_first: laneways + water feature

    gi = result.geometry_inputs
    assert (
        abs(gi["row_area_m2"] + gi["open_space_area_m2"] + gi["net_block_area_m2"] - gi["site_area_m2"])
        / gi["site_area_m2"]
        < 0.06
    )

    lanes = [z for z in result.zones if z["properties"].get("street_role") == "lane"]
    assert lanes
    assert all(z["properties"]["width"] == LANE_ROW_M for z in lanes)
    assert all(z["properties"]["road_archetype_id"] == "toronto_laneway" for z in lanes)

    ponds = [z for z in result.zones if z["properties"].get("green_space_archetype_id") == "stormwater_retention_pond"]
    assert ponds
    pond_area = sum(_metric_area(z, site) for z in ponds)
    assert 300.0 <= pond_area <= 9600.0
    greenways = [z for z in result.zones if z["properties"].get("green_space_archetype_id") == "linear_park_greenway"]
    assert greenways
    for zone in ponds + greenways:
        poly = Polygon(zone["coordinates"])
        assert poly.is_valid and len(poly.interiors) == 0

    roundabouts = [z for z in result.zones if z["properties"].get("road_archetype_id") == "roundabout"]
    assert roundabouts
    radius = (result.rules["spine_row_width_m"] + 6.0) / 2
    for zone in roundabouts:
        assert abs(_metric_area(zone, site) - math.pi * radius**2) / (math.pi * radius**2) < 0.15

    # Pond geometry is stable across runs (site-hash seeded, no RNG).
    again = _generate(site=site)
    ponds_b = [z for z in again.zones if z["properties"].get("green_space_archetype_id") == "stormwater_retention_pond"]
    assert [z["coordinates"] for z in ponds] == [z["coordinates"] for z in ponds_b]


def test_locked_streets_degrade_gracefully():
    from shapely.ops import unary_union

    site = _site()
    first = _generate(site=site)
    locked = unary_union([Polygon(z["coordinates"]) for z in first.zones if z["zone_type"] == "road"])
    second = generate_plan_geometry(
        site_polygon_wgs84=site,
        scenario_id="climate_first",
        scenario_label="Climate First",
        parameters=PARAMS,
        road_features=[],
        district_features=[],
        locked_street_area_wgs84=locked,
    )
    assert any(n["code"] == "STREETS_LOCKED" for n in second.notes)
    roads = [z for z in second.zones if z["zone_type"] == "road"]
    assert roads
    # No new lanes on a frozen network — the user locked circulation.
    assert not any(z["properties"].get("street_role") == "lane" for z in roads)
    buildings = [z for z in second.zones if z["properties"].get("_plan_role") == "building"]
    assert buildings and all(z["properties"]["development_type"] in CATALOG_DEV_TYPES for z in buildings)


# ---------------------------------------------------------------------------
# Master-plan scenario palettes (economic / city_policy / city_beautiful /
# environmental) — each philosophy must draw a recognizably different plan.
# ---------------------------------------------------------------------------

NEW_SCENARIOS = ("economic", "city_policy", "city_beautiful", "environmental")


def test_new_scenarios_draw_distinct_archetype_palettes():
    site = _site()
    fingerprints = {}
    for scenario_id in NEW_SCENARIOS:
        result = _generate(
            scenario_id=scenario_id,
            label=scenario_id,
            site=site,
            params={
                "streets.row_width_m": {"value": 16.0},
                "buildings.floors": {"value": 6},
                "landscape.tree_density": {"value": 0.6},
            },
        )
        buildings = [z for z in result.zones if z["properties"].get("_plan_role") == "building"]
        assert buildings, scenario_id
        assert all(z["properties"]["development_type"] in CATALOG_DEV_TYPES for z in buildings)
        fingerprints[scenario_id] = frozenset(
            (z["properties"]["development_type"], z["properties"]["development_aesthetic"]) for z in buildings
        )
    # Every scenario pair must differ in its (type, aesthetic) mix.
    ids = list(fingerprints)
    distinct_pairs = sum(
        1 for i in range(len(ids)) for j in range(i + 1, len(ids)) if fingerprints[ids[i]] != fingerprints[ids[j]]
    )
    assert distinct_pairs >= 5, fingerprints  # at least 5 of 6 pairs differ


def test_city_beautiful_formal_ensemble():
    result = _generate(scenario_id="city_beautiful", label="City Beautiful")
    roads = [z for z in result.zones if z["zone_type"] == "road"]
    spine = [z for z in roads if z["properties"].get("street_role") == "spine"]
    assert spine and all(z["properties"].get("road_archetype_id") == "haussmann_boulevard" for z in spine)
    greens = [z for z in result.zones if z["zone_type"] == "green_space"]
    basins = [z for z in greens if z["properties"].get("green_kind") == "pond"]
    assert basins and all(z["properties"].get("green_space_archetype_id") == "fountain_water_feature" for z in basins)
    assert any(z["properties"].get("green_kind") == "plaza" for z in greens)


def test_environmental_locals_are_shared_streets():
    result = _generate(scenario_id="environmental", label="Environmental")
    locals_ = [z for z in result.zones if z["zone_type"] == "road" and z["properties"].get("street_role") == "local"]
    assert locals_ and all(z["properties"].get("road_archetype_id") == "woonerf_shared_street" for z in locals_)
    greens = [z for z in result.zones if z["zone_type"] == "green_space"]
    assert any(z["properties"].get("green_kind") == "pond" for z in greens)


def test_economic_context_match_caps_all_bands():
    dna = {"built_form": {"fields": {"context_avg_height_m": {"value": 6.4}}}}  # 2 storeys
    result = generate_plan_geometry(
        site_polygon_wgs84=_site(),
        scenario_id="economic",
        scenario_label="Economic",
        parameters={"streets.row_width_m": {"value": 16.0}, "buildings.floors": {"value": 8}},
        road_features=[],
        district_features=[],
        dna=dna,
    )
    buildings = [z for z in result.zones if z["properties"].get("_plan_role") == "building"]
    assert buildings
    # context avg 2F + 2 = 4F ceiling everywhere, despite the 8F parameter.
    assert all(z["properties"]["floors"] <= 4.01 for z in buildings), sorted(
        {z["properties"]["floors"] for z in buildings}
    )


def test_custom_palette_hint_maps_philosophy_to_palette():
    from app.services.plan_geometry.placement import PALETTES, palette_for

    assert palette_for("custom_abc", "city_beautiful") is PALETTES["city_beautiful"]
    assert palette_for("custom_abc", "developer_feasibility") is PALETTES["economic"]
    assert palette_for("custom_abc", "climate_resilience") is PALETTES["environmental"]
    assert palette_for("custom_abc", None) is PALETTES["city_policy"]  # default
    assert palette_for("economic", "city_beautiful") is PALETTES["economic"]  # preset wins
