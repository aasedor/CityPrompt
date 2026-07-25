"""Final executable-LEGO binding for AI-generated building polygons.

The Master Planner chooses a proven family at its catalog footprint, while the
geometry engine may stretch, clip, or segment that footprint to fit a real
block. This final pure pass mirrors the browser's footprint measurement and
proves the *actual* polygon against ``plan_vertical_assembly``. Incompatible
identities are deterministically rebound to the closest stylistic family that
can assemble at the exact polygon dimensions and storey count.
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
from app.services.plan_geometry.archetypes import _norm, compatible_families, family_of

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


# Geometry refinement can leave a very small clipped bar at a block edge. It
# is better to return that sliver to the residual landscape than to persist an
# AI building that the browser cannot assemble. The bounded policy prevents
# this safety valve from silently hollowing out an incompatible plan.
MAX_OMITTED_BUILDING_SHARE = 0.10
MAX_OMITTED_FOOTPRINT_SHARE = 0.05


def _frontend_footprint_analysis(
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
    metres_per_deg_lng = METRES_PER_DEG_LNG_EQUATOR * math.cos(
        math.radians(centroid_lat)
    )
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
    signed_area = sum(
        current[0] * following[1] - following[0] * current[1]
        for current, following in zip(local, local[1:] + local[:1])
    ) / 2
    orientation = 1 if signed_area >= 0 else -1
    concave_vertices = 0
    for index, current in enumerate(local):
        previous = local[(index - 1) % len(local)]
        following = local[(index + 1) % len(local)]
        cross = (
            (current[0] - previous[0]) * (following[1] - current[1])
            - (current[1] - previous[1]) * (following[0] - current[0])
        )
        if abs(cross) > 1e-6 and (1 if cross > 0 else -1) != orientation:
            concave_vertices += 1
    fill_ratio = min(1.0, abs(signed_area) / max(raw_width * raw_depth, 1.0))
    if fill_ratio >= NEAR_RECTANGLE_FILL_RATIO:
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


def _style_penalties(
    *,
    current_parent: str | None,
    current_type: str,
    current_aesthetic: str,
    candidate_parent: str,
    candidate_type: str,
    candidate_aesthetic: str,
) -> tuple[int, int, int]:
    current_family = family_of(current_parent)
    candidate_family = family_of(candidate_parent)
    family_penalty = 0
    if current_family and candidate_family:
        family_penalty = int(candidate_family not in compatible_families(current_family))
    type_penalty = int(_norm(candidate_type) != _norm(current_type))
    requested_aesthetic = _norm(current_aesthetic)
    offered_aesthetic = _norm(candidate_aesthetic)
    aesthetic_penalty = int(
        bool(requested_aesthetic)
        and requested_aesthetic not in offered_aesthetic
        and offered_aesthetic not in requested_aesthetic
    )
    return family_penalty, type_penalty, aesthetic_penalty


def bind_building_zones_to_lego(
    zones: Iterable[dict[str, Any]],
    library_entries: Iterable[Any],
    lego_catalog: LegoPlanningCatalog,
) -> tuple[list[dict[str, Any]], LegoGeometryBindingReport]:
    """Return zones whose every AI building is proven at its actual footprint."""

    descriptors = [
        descriptor
        for entry in library_entries
        if (descriptor := descriptor_from_library_entry(entry)) is not None
    ]
    capability_by_parent = {
        capability.parent_id: capability
        for capability in lego_catalog.capabilities
    }
    updated: list[dict[str, Any]] = []
    repairs: list[tuple[str, str, str]] = []
    omissions: list[tuple[str, float, float, int]] = []
    omitted_building_indices: list[int] = []
    measured_footprint_area = 0.0
    omitted_footprint_area = 0.0
    building_count = 0
    unchanged_count = 0

    def _plan(
        selectable_id: str,
        width_m: float,
        depth_m: float,
        floors: int,
        footprint_profile: str,
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
                ),
            )
        except AssemblyPlanningError:
            return None

    for zone in zones:
        properties = dict(zone.get("properties") or {})
        if properties.get("_plan_role") != "building":
            updated.append(zone)
            continue
        building_count += 1
        analysis = _frontend_footprint_analysis(zone.get("coordinates"))
        if analysis is None:
            raise LegoGeometryCompatibilityError(
                f"{zone.get('name') or 'Planned building'} has no measurable footprint."
            )
        width_m, depth_m, footprint_profile = analysis
        measured_footprint_area += width_m * depth_m
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
            or lego_catalog.parent_by_selectable_id.get(current_selectable)
            != parent_id
        ):
            current_plan = None

        chosen_parent = parent_id
        chosen_selectable = current_selectable
        if current_plan is None:
            candidates: list[tuple[tuple[Any, ...], str, str, dict[str, Any]]] = []
            for capability in lego_catalog.capabilities:
                for selectable_id in capability.selectable_ids:
                    if floors not in capability.supported_floors_by_selectable_id.get(
                        selectable_id, ()
                    ):
                        continue
                    plan = _plan(
                        selectable_id,
                        width_m,
                        depth_m,
                        floors,
                        footprint_profile,
                    )
                    if plan is None:
                        continue
                    penalties = _style_penalties(
                        current_parent=parent_id or None,
                        current_type=str(properties.get("development_type") or ""),
                        current_aesthetic=str(
                            properties.get("development_aesthetic") or ""
                        ),
                        candidate_parent=capability.parent_id,
                        candidate_type=capability.development_type,
                        candidate_aesthetic=capability.aesthetic_category,
                    )
                    fit = plan.get("fit") or {}
                    scale_x = max(float(fit.get("scale_x") or 1.0), 1e-6)
                    scale_y = max(float(fit.get("scale_y") or 1.0), 1e-6)
                    quality_penalty = int(
                        not (0.80 <= scale_x <= 1.20 and 0.80 <= scale_y <= 1.20)
                    ) + int(
                        not (0.67 <= scale_x <= 1.50 and 0.67 <= scale_y <= 1.50)
                    )
                    distortion = (
                        abs(math.log(scale_x))
                        + abs(math.log(scale_y))
                        + 0.5 * abs(math.log(scale_x / scale_y))
                    )
                    fit_score = float(fit.get("score") or 0.0)
                    score = (
                        quality_penalty,
                        *penalties,
                        distortion,
                        -fit_score,
                        capability.parent_id,
                        selectable_id,
                    )
                    candidates.append(
                        (score, capability.parent_id, selectable_id, plan)
                    )
            if not candidates:
                name = str(zone.get("name") or "Planned building")
                omissions.append((name, width_m, depth_m, floors))
                omitted_building_indices.append(building_count - 1)
                omitted_footprint_area += width_m * depth_m
                continue
            _, chosen_parent, chosen_selectable, current_plan = min(candidates)
            repairs.append(
                (
                    str(zone.get("name") or "Planned building"),
                    current_selectable or "unassigned",
                    chosen_selectable,
                )
            )
        else:
            unchanged_count += 1

        capability = capability_by_parent[chosen_parent]
        properties["development_archetype_id"] = chosen_parent
        properties["development_type"] = capability.development_type
        properties["development_aesthetic"] = capability.aesthetic_category
        properties["target_w_m"] = width_m
        properties["target_d_m"] = depth_m
        properties["_lego_actual_footprint_profile"] = footprint_profile
        properties["archetype_source"] = "runtime_lego_actual_footprint"
        properties["_lego_catalog_fingerprint"] = lego_catalog.fingerprint
        properties["_lego_runtime_selection_id"] = chosen_selectable
        if chosen_selectable != chosen_parent:
            properties["development_selected_variant_id"] = chosen_selectable
        else:
            properties.pop("development_selected_variant_id", None)
        if current_selectable and current_selectable != chosen_selectable:
            properties["_lego_runtime_repaired_from"] = current_selectable

        rebound = dict(zone)
        rebound["properties"] = properties
        updated.append(rebound)

    omitted_count = len(omissions)
    if omitted_count:
        omitted_footprint_share = omitted_footprint_area / max(
            measured_footprint_area, 1.0
        )
        allowed_count = max(
            1,
            math.ceil(building_count * MAX_OMITTED_BUILDING_SHARE),
        )
        if (
            omitted_count > allowed_count
            or omitted_footprint_share > MAX_OMITTED_FOOTPRINT_SHARE
        ):
            name, width_m, depth_m, floors = omissions[0]
            raise LegoGeometryCompatibilityError(
                f"{name} ({width_m:g} × {depth_m:g} m, {floors} floors) has no "
                "executable LEGO family; the incompatible footprints exceed the "
                "bounded residual-landscape allowance "
                f"({omitted_count}/{building_count} buildings, "
                f"{omitted_footprint_share:.1%} of building footprint)."
            )

    return updated, LegoGeometryBindingReport(
        building_count=building_count,
        retained_count=building_count - omitted_count,
        unchanged_count=unchanged_count,
        repaired_count=len(repairs),
        omitted_count=omitted_count,
        omitted_building_indices=tuple(omitted_building_indices),
        repairs=tuple(repairs),
        omissions=tuple(omissions),
    )


__all__ = [
    "LegoGeometryBindingReport",
    "LegoGeometryCompatibilityError",
    "bind_building_zones_to_lego",
]
