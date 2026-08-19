"""Community program — the non-residential half of a neighbourhood.

A plan of only fabric is not a community: it has nowhere to walk TO. These
tests pin the program mechanism (doctrine: mobility.daily_needs,
legibility.civic_hierarchy) and — just as importantly — the render reference
budget that bounds how much of it one plan can carry.
"""

import math

from shapely.geometry import Polygon

from app.services.plan_geometry.generator import generate_plan_geometry
from app.services.plan_geometry.placement import (
    MAX_PROGRAM_SLOTS,
    PALETTES,
    ProgramSlot,
    estimate_dwellings,
)

LAT, LON = 51.0405, -114.0850
M_LAT = 111_320.0
M_LON = M_LAT * math.cos(math.radians(LAT))

CURRENT_PRESETS = ("economic", "city_policy", "city_beautiful", "environmental")


def _site(width_m: float, depth_m: float) -> Polygon:
    return Polygon(
        [
            (LON, LAT),
            (LON + width_m / M_LON, LAT),
            (LON + width_m / M_LON, LAT + depth_m / M_LAT),
            (LON, LAT + depth_m / M_LAT),
        ]
    )


def _plan(scenario_id: str, width_m: float, depth_m: float, floors: int = 4):
    return generate_plan_geometry(
        site_polygon_wgs84=_site(width_m, depth_m),
        scenario_id=scenario_id,
        scenario_label=scenario_id,
        parameters={
            "buildings.floors": {"value": floors},
            "streets.row_width_m": {"value": 18.0},
        },
        road_features=[],
        district_features=[],
    )


def _program_ids(result) -> set[str]:
    return {
        zone["properties"].get("development_archetype_id")
        for zone in result.zones
        if zone["properties"].get("_plan_role") == "building"
        and not str(zone["properties"].get("development_type", "")).startswith("residential")
        and zone["properties"].get("development_type") != "mixed_use"
    } - {None}


# ---------------------------------------------------------------------------
# Declaration integrity
# ---------------------------------------------------------------------------


def test_every_current_preset_declares_program():
    """A preset with no program can only ever draw housing."""
    for scenario_id in CURRENT_PRESETS:
        assert PALETTES[scenario_id].program, scenario_id


def test_program_slots_are_declared_largest_catchment_first():
    """assign_program takes the first qualifying slot, so the order IS the
    priority — a mis-ordered tuple silently gives a 2,000-home neighbourhood a
    corner shop and nothing else."""
    for scenario_id in CURRENT_PRESETS:
        thresholds = [slot.min_dwellings for slot in PALETTES[scenario_id].program]
        assert thresholds == sorted(thresholds, reverse=True), scenario_id


def test_program_archetypes_are_pinned_and_real():
    """development_type alone is too coarse: institutional_education spans a
    lecture hall to a parking structure, so an unpinned 'school' resolved to
    university_academic_complex in a 700-home neighbourhood."""
    from app.services.plan_geometry.archetypes import dims_by_id

    table = dims_by_id()
    for scenario_id in CURRENT_PRESETS:
        for slot in PALETTES[scenario_id].program:
            assert slot.archetype_id, (scenario_id, slot.label)
            entry = table.get(slot.archetype_id)
            assert entry is not None, slot.archetype_id
            assert entry["usable"]
            assert entry["development_type"] == slot.development_type


# ---------------------------------------------------------------------------
# Scale gating
# ---------------------------------------------------------------------------


def test_estimate_dwellings_grows_with_the_site():
    from app.services.plan_geometry.community_rules import resolve_rules
    from app.services.plan_geometry.placement import BlockContext

    rules, _ = resolve_rules("city_policy", {})

    def contexts(area: float) -> list[BlockContext]:
        return [
            BlockContext(
                index=0,
                area_m2=area,
                dist_to_centroid_m=0.0,
                dist_to_edge_m=0.0,
                transect=0.5,
                fronts_spine=False,
                touches_boundary=False,
                dist_to_green_m=math.inf,
                abuts_low_rise=False,
                ceiling_floors=None,
            )
        ]

    assert estimate_dwellings(contexts(10_000), rules) < estimate_dwellings(contexts(50_000), rules)


def test_a_bigger_neighbourhood_earns_more_program():
    """Catchment is what justifies a rec centre over a corner shop."""
    small = _program_ids(_plan("city_policy", 300, 200))
    large = _program_ids(_plan("city_policy", 700, 520))
    assert small and large
    assert large != small


def test_program_lands_on_real_blocks_and_is_never_rotated_away():
    """A program block IS that program — the band's alternates must not turn
    the clinic back into an apartment block."""
    for scenario_id in CURRENT_PRESETS:
        result = _plan(scenario_id, 700, 520)
        pinned = {slot.archetype_id for slot in PALETTES[scenario_id].program}
        drawn = _program_ids(result)
        assert drawn, scenario_id
        assert drawn <= pinned, (scenario_id, drawn - pinned)


def test_no_plan_exceeds_the_program_slot_cap():
    for scenario_id in CURRENT_PRESETS:
        assert len(_program_ids(_plan(scenario_id, 700, 520))) <= MAX_PROGRAM_SLOTS, scenario_id


# ---------------------------------------------------------------------------
# The render reference budget — the real constraint on plan richness
# ---------------------------------------------------------------------------


def test_every_current_preset_stays_inside_the_render_reference_budget():
    """The render pipeline keeps ~15 reference images per plan. Program, park
    breadth and building variety all spend from the SAME budget, and the
    existing cap test only covers one legacy palette at one site size — which
    is how a park-breadth change pushed city_policy at 700x520 m past the cap
    without any test noticing.
    """
    for scenario_id in CURRENT_PRESETS:
        for width, depth in ((300, 200), (700, 520)):
            result = _plan(scenario_id, width, depth)
            buildings = [z for z in result.zones if z["properties"].get("_plan_role") == "building"]
            triples = {
                (
                    z["properties"]["development_type"],
                    z["properties"]["development_aesthetic"],
                    z["properties"]["floors"],
                )
                for z in buildings
            }
            ids = {z["properties"].get("road_archetype_id") for z in result.zones} | {
                z["properties"].get("green_space_archetype_id") for z in result.zones
            }
            total = len(triples) + len(ids - {None}) + 3
            assert total <= 16, f"{scenario_id} {width}x{depth}: {total} references"


def test_program_slot_is_frozen():
    slot = PALETTES["city_policy"].program[0]
    assert isinstance(slot, ProgramSlot)
    try:
        slot.label = "changed"  # type: ignore[misc]
    except Exception:
        return
    raise AssertionError("ProgramSlot must be immutable")
