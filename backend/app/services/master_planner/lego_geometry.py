"""Final representation binding for AI-generated building polygons.

The Master Planner may select any authored catalogue identity, while only a
bounded subset has an imported LEGO family today. This pure pass mirrors the
browser's footprint measurement and proves an exact identity against
``plan_vertical_assembly``. A proven identity receives the executable
catalogue fingerprint. An unavailable or incompatible identity is preserved
unchanged and labelled family-pending so Community 3D can compile its exact
footprint and authoritative height as neutral planned massing.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Iterable

from app.services.lego_assembly import (
    AssemblyPlanningError,
    AssemblyRequest,
    descriptor_from_library_entry,
    plan_vertical_assembly,
)
from app.services.master_planner.lego_catalog import LegoPlanningCatalog

METRES_PER_DEG_LAT = 110_540.0
METRES_PER_DEG_LNG_EQUATOR = 111_320.0
NEAR_RECTANGLE_FILL_RATIO = 0.96


class LegoGeometryCompatibilityError(ValueError):
    """Raised before persistence when a generated polygon has no LEGO recipe."""


@dataclass(frozen=True)
class LegoGeometryBindingReport:
    building_count: int
    retained_count: int
    unchanged_count: int
    repaired_count: int
    omitted_count: int
    omitted_building_indices: tuple[int, ...]
    repairs: tuple[tuple[str, str, str], ...]
    omissions: tuple[tuple[str, float, float, int], ...]
    fallback_count: int
    fallbacks: tuple[tuple[str, str, float, float, int, str], ...]


def frontend_footprint_analysis(
    coordinates: object,
) -> tuple[float, float, str] | None:
    """Mirror the browser's dimensions and topology-profile classification."""

    if not isinstance(coordinates, list):
        return None
    ring = [
        (float(point[0]), float(point[1]))
        for point in coordinates
        if isinstance(point, (list, tuple))
        and len(point) >= 2
        and isinstance(point[0], (int, float))
        and isinstance(point[1], (int, float))
        and math.isfinite(float(point[0]))
        and math.isfinite(float(point[1]))
    ]
    if len(ring) > 3 and all(abs(a - b) < 1e-12 for a, b in zip(ring[0], ring[-1])):
        ring.pop()
    if len(ring) < 3:
        return None

    centroid_lng = sum(point[0] for point in ring) / len(ring)
    centroid_lat = sum(point[1] for point in ring) / len(ring)
    metres_per_deg_lng = METRES_PER_DEG_LNG_EQUATOR * math.cos(math.radians(centroid_lat))
    local = [
        (
            (lng - centroid_lng) * metres_per_deg_lng,
            (lat - centroid_lat) * METRES_PER_DEG_LAT,
        )
        for lng, lat in ring
    ]

    longest = 0.0
    angle = 0.0
    for index, current in enumerate(local):
        following = local[(index + 1) % len(local)]
        dx = following[0] - current[0]
        dy = following[1] - current[1]
        length = math.hypot(dx, dy)
        if length > longest:
            longest = length
            angle = math.atan2(dy, dx)
    cos_angle = math.cos(angle)
    sin_angle = math.sin(angle)
    u_values = [x * cos_angle + y * sin_angle for x, y in local]
    v_values = [-x * sin_angle + y * cos_angle for x, y in local]
    dimensions = sorted(
        (max(u_values) - min(u_values), max(v_values) - min(v_values)),
        reverse=True,
    )
    # JavaScript Math.round semantics for the positive dimensions consumed by
    # the browser (Python round uses bankers' rounding at exact .05 ties).
    raw_width = max(1.0, dimensions[0])
    raw_depth = max(1.0, dimensions[1])
    width = math.floor(raw_width * 10 + 0.5) / 10
    depth = math.floor(raw_depth * 10 + 0.5) / 10
    signed_area = (
        sum(
            current[0] * following[1] - following[0] * current[1]
            for current, following in zip(local, local[1:] + local[:1])
        )
        / 2
    )
    orientation = 1 if signed_area >= 0 else -1
    concave_vertices = 0
    for index, current in enumerate(local):
        previous = local[(index - 1) % len(local)]
        following = local[(index + 1) % len(local)]
        cross = (current[0] - previous[0]) * (following[1] - current[1]) - (current[1] - previous[1]) * (
            following[0] - current[0]
        )
        if abs(cross) > 1e-6 and (1 if cross > 0 else -1) != orientation:
            concave_vertices += 1
    fill_ratio = min(1.0, abs(signed_area) / max(raw_width * raw_depth, 1.0))
    # Match the browser's topology rule: a hand-drawn four-corner envelope is
    # a rectangle even when one imprecise point is slightly re-entrant.
    if len(ring) == 4 or fill_ratio >= NEAR_RECTANGLE_FILL_RATIO:
        profile = "rectangle"
    elif concave_vertices >= 3:
        profile = "courtyard"
    elif concave_vertices == 2:
        profile = "u_shape"
    elif concave_vertices == 1:
        profile = "l_shape"
    else:
        profile = "rectangle"
    return width, depth, profile


# Compatibility alias for existing focused tests and internal callers. New
# code should use the public spelling above.
_frontend_footprint_analysis = frontend_footprint_analysis


def bind_building_zones_to_lego(
    zones: Iterable[dict[str, Any]],
    library_entries: Iterable[Any],
    lego_catalog: LegoPlanningCatalog,
) -> tuple[list[dict[str, Any]], LegoGeometryBindingReport]:
    """Bind exact families and preserve all other buildings as honest masses."""

    descriptors = [
        descriptor for entry in library_entries if (descriptor := descriptor_from_library_entry(entry)) is not None
    ]
    capability_by_parent = {capability.parent_id: capability for capability in lego_catalog.capabilities}
    updated: list[dict[str, Any]] = []
    repairs: list[tuple[str, str, str]] = []
    omissions: list[tuple[str, float, float, int]] = []
    omitted_building_indices: list[int] = []
    fallbacks: list[tuple[str, str, float, float, int, str]] = []
    building_count = 0
    unchanged_count = 0

    def _plan(
        selectable_id: str,
        width_m: float,
        depth_m: float,
        floors: int,
        footprint_profile: str,
        wing_depth_m: float | None = None,
    ) -> dict[str, Any] | None:
        try:
            return plan_vertical_assembly(
                descriptors,
                AssemblyRequest(
                    target_width_m=width_m,
                    target_depth_m=depth_m,
                    target_floors=floors,
                    archetype_id=selectable_id,
                    allow_setback=False,
                    footprint_profile=footprint_profile,
                    wing_depth_m=wing_depth_m,
                ),
                # Binding is a proof: genuine incompatibility must keep
                # raising so identities re-home instead of force-fitting.
                allow_forced_fit=False,
            )
        except AssemblyPlanningError:
            return None

    for zone in zones:
        properties = dict(zone.get("properties") or {})
        if properties.get("_plan_role") != "building":
            updated.append(zone)
            continue
        building_count += 1
        analysis = frontend_footprint_analysis(zone.get("coordinates"))
        if analysis is None:
            raise LegoGeometryCompatibilityError(
                f"{zone.get('name') or 'Planned building'} has no measurable footprint."
            )
        width_m, depth_m, footprint_profile = analysis
        floors = max(
            1,
            math.floor(float(properties.get("floors") or 1) + 0.5),
        )
        parent_id = str(properties.get("development_archetype_id") or "")
        selected_variant = str(properties.get("development_selected_variant_id") or "")
        current_selectable = selected_variant or parent_id
        current_plan = (
            _plan(
                current_selectable,
                width_m,
                depth_m,
                floors,
                footprint_profile,
            )
            if current_selectable
            else None
        )
        capability = capability_by_parent.get(parent_id)
        if (
            capability is None
            or current_selectable not in capability.selectable_ids
            or lego_catalog.parent_by_selectable_id.get(current_selectable) != parent_id
        ):
            current_plan = None

        if current_plan is None:
            reason = (
                "family_not_found"
                if capability is None
                or current_selectable not in capability.selectable_ids
                or lego_catalog.parent_by_selectable_id.get(current_selectable) != parent_id
                else "family_incompatible"
            )
            properties["target_w_m"] = width_m
            properties["target_d_m"] = depth_m
            properties["_lego_actual_footprint_profile"] = footprint_profile
            properties.pop("_lego_actual_wing_depth_m", None)
            properties["archetype_source"] = "runtime_planned_massing_actual_footprint"
            properties["_lego_family_pending"] = True
            properties["_lego_family_pending_reason"] = reason
            # These keys certify an exact executable inventory. Leaving one
            # on a family-pending zone makes a safe recipe-less compile look
            # like catalogue corruption and turns the fallback into a 409.
            properties.pop("_lego_catalog_fingerprint", None)
            properties.pop("_lego_runtime_selection_id", None)
            properties.pop("_lego_runtime_repaired_from", None)
            fallbacks.append(
                (
                    str(zone.get("name") or "Planned building"),
                    current_selectable or "unassigned",
                    width_m,
                    depth_m,
                    floors,
                    reason,
                )
            )
        else:
            unchanged_count += 1
            assert capability is not None
            properties["development_type"] = capability.development_type
            properties["development_aesthetic"] = capability.aesthetic_category
            properties["target_w_m"] = width_m
            properties["target_d_m"] = depth_m
            properties["_lego_actual_footprint_profile"] = footprint_profile
            if footprint_profile == "rectangle":
                properties.pop("_lego_actual_wing_depth_m", None)
            else:
                properties["_lego_actual_wing_depth_m"] = float(current_plan["target"]["wing_depth_m"])
            properties["archetype_source"] = "runtime_lego_actual_footprint"
            properties["_lego_catalog_fingerprint"] = lego_catalog.fingerprint
            properties["_lego_runtime_selection_id"] = current_selectable
            properties.pop("_lego_runtime_repaired_from", None)
            properties.pop("_lego_family_pending", None)
            properties.pop("_lego_family_pending_reason", None)

        rebound = dict(zone)
        rebound["properties"] = properties
        updated.append(rebound)

    return updated, LegoGeometryBindingReport(
        building_count=building_count,
        retained_count=building_count,
        unchanged_count=unchanged_count,
        repaired_count=len(repairs),
        omitted_count=len(omissions),
        omitted_building_indices=tuple(omitted_building_indices),
        repairs=tuple(repairs),
        omissions=tuple(omissions),
        fallback_count=len(fallbacks),
        fallbacks=tuple(fallbacks),
    )


__all__ = [
    "frontend_footprint_analysis",
    "LegoGeometryBindingReport",
    "LegoGeometryCompatibilityError",
    "bind_building_zones_to_lego",
]
