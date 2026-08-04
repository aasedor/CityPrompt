"""Deterministic checks on the drawn plan. Findings are ValidationNote dicts."""

from __future__ import annotations

import math
from typing import Any

from shapely.geometry import Polygon
from shapely.geometry.base import BaseGeometry
from shapely.ops import unary_union

from app.services.plan_geometry.community_rules import FIRE_CLEAR_WIDTH_M, RuleProfile
from app.services.plan_geometry.street_graph import StreetNetwork

BLOCK_EDGE_MIN_M = 60.0
# Jacobs long-axis max / Calgary Complete Streets 150 m intersection spacing —
# the "consider a mid-block connection" advisory fires on genuinely long
# blocks (2026-07-12 morphology research). Distinct from street_graph's 220 m
# curve-headroom bound.
BLOCK_EDGE_MAX_M = 150.0


def _block_edge_lengths(block_m: Polygon) -> tuple[float, float]:
    rect = block_m.minimum_rotated_rectangle
    coords = list(rect.exterior.coords)
    lengths = sorted(math.hypot(x2 - x1, y2 - y1) for (x1, y1), (x2, y2) in zip(coords[:-1], coords[1:]))
    return lengths[0], lengths[-1]


def validate_plan(
    *,
    rules: RuleProfile,
    network: StreetNetwork,
    blocks_m: list[Polygon],
    parcels_by_block: list[list[Polygon]],
    masses_m: list[Polygon],
    open_spaces_m: list[BaseGeometry] | None = None,
) -> list[dict[str, Any]]:
    notes: list[dict[str, Any]] = []

    # Existing-context continuity is a measured plan invariant, not a prompt
    # aspiration. Only score source anchors that were actually detected; a
    # site with no available road/path dataset remains neutral and its data
    # limitation is disclosed elsewhere by Site DNA.
    context_total = network.entries_total + network.path_entries_total
    context_served = network.entries_served + network.path_entries_served
    if context_total:
        if context_served == context_total:
            notes.append(
                {
                    "code": "CONTEXT_CONNECTIVITY_OK",
                    "severity": "info",
                    "message": f"All {context_total} detected frontage connection(s) are joined "
                    "topologically to the internal street/path network "
                    f"({network.entries_served} road, {network.path_entries_served} path).",
                    "source_phase": "connectivity_validation",
                }
            )
        else:
            notes.append(
                {
                    "code": "CONTEXT_CONNECTIVITY_PARTIAL",
                    "severity": "warning",
                    "message": f"{context_served} of {context_total} detected frontage connection(s) "
                    "reach the internal network; review the remaining boundary anchors.",
                    "source_phase": "connectivity_validation",
                }
            )

    # Fire access — the hard rule, checked on the resolved profile.
    if rules.clear_width_m + 1e-6 < FIRE_CLEAR_WIDTH_M:
        notes.append(
            {
                "code": "FIRE_CLEAR_WIDTH_FAIL",
                "severity": "error",
                "message": f"Internal ROW {rules.row_width_m:g} m leaves {rules.clear_width_m:g} m clear "
                f"< CSPS033 {FIRE_CLEAR_WIDTH_M:g} m.",
                "source_phase": "row_geometry",
            }
        )
    else:
        notes.append(
            {
                "code": "FIRE_CLEAR_WIDTH_OK",
                "severity": "info",
                "message": f"All internal streets keep {rules.clear_width_m:g} m clear "
                f"(ROW {rules.row_width_m:g} m) ≥ CSPS033 {FIRE_CLEAR_WIDTH_M:g} m.",
                "source_phase": "row_geometry",
            }
        )

    # Block scale.
    oversize = undersize = 0
    for block in blocks_m:
        short_edge, long_edge = _block_edge_lengths(block)
        if long_edge > BLOCK_EDGE_MAX_M:
            oversize += 1
        if short_edge < BLOCK_EDGE_MIN_M:
            undersize += 1
    if oversize:
        notes.append(
            {
                "code": "BLOCKS_OVERSIZE",
                "severity": "warning",
                "message": f"{oversize} of {len(blocks_m)} blocks exceed {BLOCK_EDGE_MAX_M:.0f} m — "
                "walkability suffers; consider a mid-block connection.",
                "source_phase": "parceling",
            }
        )
    if undersize:
        notes.append(
            {
                "code": "BLOCKS_UNDERSIZE",
                "severity": "info",
                "message": f"{undersize} blocks have a sub-{BLOCK_EDGE_MIN_M:.0f} m edge (boundary remnants).",
                "source_phase": "parceling",
            }
        )

    # Parcel frontage: every parcel must touch its block's street edge.
    landlocked = 0
    for block, parcels in zip(blocks_m, parcels_by_block):
        edge = block.exterior
        for parcel in parcels:
            if parcel.distance(edge) > 0.5:
                landlocked += 1
    if landlocked:
        notes.append(
            {
                "code": "PARCELS_LANDLOCKED",
                "severity": "error",
                "message": f"{landlocked} parcels have no street frontage.",
                "source_phase": "parceling",
            }
        )

    # Building masses must not overlap streets, parks/courtyards, or each
    # other. Boundary contact is expected, so only material (>1 m²) area
    # intersections fail. Keeping this invariant in metric space prevents a
    # later 3D extrusion from turning a subtle plan collision into a park or
    # reservoir visibly hovering through a building.
    if masses_m:
        mass_union = unary_union(masses_m)
        mass_self_overlap = sum(float(mass.area) for mass in masses_m) - float(mass_union.area)
        if mass_self_overlap > 1.0:
            notes.append(
                {
                    "code": "MASS_MASS_COLLISION",
                    "severity": "error",
                    "message": f"Building masses overlap each other by {mass_self_overlap:,.0f} m².",
                    "source_phase": "collision_validation",
                }
            )

        if network.street_area is not None and not network.street_area.is_empty:
            overlap = mass_union.intersection(network.street_area)
            if overlap.area > 1.0:
                notes.append(
                    {
                        "code": "MASS_STREET_COLLISION",
                        "severity": "error",
                        "message": f"Building mass overlaps street ROW by {overlap.area:,.0f} m².",
                        "source_phase": "collision_validation",
                    }
                )

        usable_open_spaces = [geom for geom in (open_spaces_m or []) if not geom.is_empty]
        if usable_open_spaces:
            overlap = mass_union.intersection(unary_union(usable_open_spaces))
            if overlap.area > 1.0:
                notes.append(
                    {
                        "code": "MASS_OPEN_SPACE_COLLISION",
                        "severity": "error",
                        "message": f"Building mass overlaps park/courtyard space by " f"{overlap.area:,.0f} m².",
                        "source_phase": "collision_validation",
                    }
                )

    return notes
