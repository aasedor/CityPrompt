"""Server-owned scope resolution for visible Community 3D layers.

Imported master-plan scenarios remain persisted so users can compare them, but
the globe can deliberately hide whole imported layers.  Paid Direct rendering
must therefore accept a complete visible layer without trusting an arbitrary
client-selected subset of that layer.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable
from typing import Any

from geoalchemy2.shape import to_shape
from shapely.geometry.base import BaseGeometry


class Community3DScopeError(ValueError):
    """The requested Community 3D layer selection is not server-verifiable."""


def _normalized_property(properties: dict[str, Any], key: str) -> str | None:
    value = properties.get(key)
    if not isinstance(value, str):
        return None
    normalized = value.strip()
    return normalized or None


def _scope_group_key(zone: Any) -> tuple[str, ...] | None:
    properties = getattr(zone, "properties", None) or {}
    imported_from = _normalized_property(properties, "_imported_from")
    if imported_from:
        # This is exactly how the browser layer panel groups visibility.  A
        # persisted layer can be rendered only in its entirety.
        return ("import", imported_from)

    snapshot_id = _normalized_property(properties, "_plan_snapshot_id")
    scenario_id = _normalized_property(properties, "_plan_scenario")
    if snapshot_id and scenario_id:
        # Defensive fallback for older planner rows that have stable plan
        # identity but no imported-layer label.
        return ("plan", snapshot_id, scenario_id)
    return None


def physical_community_3d_zones(zones: Iterable[Any]) -> list[Any]:
    """Return authored physical zones, excluding boundaries and framework aids."""

    return [
        zone
        for zone in zones
        if getattr(zone, "zone_type", None) != "site_boundary"
        and (getattr(zone, "properties", None) or {}).get("_plan_role") != "framework_height"
    ]


def _zone_geometry(zone: Any) -> BaseGeometry:
    geometry = getattr(zone, "geometry", None)
    if isinstance(geometry, BaseGeometry):
        shape = geometry
    else:
        try:
            shape = to_shape(geometry)
        except (AssertionError, TypeError, ValueError) as exc:
            raise Community3DScopeError("The boundary-scoped Community 3D request contains unusable geometry.") from exc
    if shape.is_empty or not shape.is_valid:
        raise Community3DScopeError("The boundary-scoped Community 3D request contains unusable geometry.")
    return shape


def resolve_boundary_community_3d_scope(
    zones: Iterable[Any],
    selected_zone_ids: Iterable[str],
    boundary_zone_id: str,
) -> list[Any]:
    """Validate the exact physical scope intersecting one persisted boundary.

    Boundary compilation is intentionally narrower than normal visible-layer
    compilation. The client supplies the IDs returned by boundary analysis,
    while the server independently recomputes the intersection from the
    project rows loaded under the Community 3D project lock. This excludes
    unrelated project zones without trusting an arbitrary client subset.
    """

    project_zones = list(zones)
    boundary_id = str(boundary_zone_id)
    boundary = next(
        (zone for zone in project_zones if str(zone.id) == boundary_id),
        None,
    )
    if boundary is None or getattr(boundary, "zone_type", None) != "site_boundary":
        raise Community3DScopeError("The selected Community 3D boundary is not part of this project.")

    physical_zones = physical_community_3d_zones(project_zones)
    physical_ids = {str(zone.id) for zone in physical_zones}
    selected_ids = {str(zone_id) for zone_id in selected_zone_ids}
    if selected_ids - physical_ids:
        raise Community3DScopeError(
            "The selected Community 3D boundary scope references non-physical " "or out-of-project zones."
        )

    boundary_shape = _zone_geometry(boundary)
    intersecting_zones = [zone for zone in physical_zones if boundary_shape.intersects(_zone_geometry(zone))]
    intersecting_ids = {str(zone.id) for zone in intersecting_zones}
    if selected_ids != intersecting_ids:
        raise Community3DScopeError("The selected Community 3D boundary scope changed before compilation.")
    if not intersecting_zones:
        raise Community3DScopeError("The selected Community 3D boundary contains no physical zones.")
    return intersecting_zones


def resolve_community_3d_scope(
    zones: Iterable[Any],
    selected_zone_ids: Iterable[str],
    *,
    expand_groups: bool = False,
) -> list[Any]:
    """Resolve a visible, server-verifiable physical-zone scope.

    In exact mode (paid Direct preflight), every ungrouped zone is mandatory
    and every imported/plan group is either wholly selected or wholly omitted.
    In expansion mode (Community 3D compilation), one selected member is a
    trustworthy seed for its persisted group; the full group and all ungrouped
    authored zones participate in the derived residual landscape.
    """

    physical_zones = physical_community_3d_zones(zones)
    zones_by_id = {str(zone.id): zone for zone in physical_zones}
    selected_ids = {str(zone_id) for zone_id in selected_zone_ids}
    unknown_ids = selected_ids - set(zones_by_id)
    if unknown_ids:
        raise Community3DScopeError(
            "The selected Community 3D scope references zones outside the " "current physical project."
        )

    grouped_ids: dict[tuple[str, ...], set[str]] = defaultdict(set)
    ungrouped_ids: set[str] = set()
    group_by_zone_id: dict[str, tuple[str, ...]] = {}
    for zone_id, zone in zones_by_id.items():
        group_key = _scope_group_key(zone)
        if group_key is None:
            ungrouped_ids.add(zone_id)
            continue
        grouped_ids[group_key].add(zone_id)
        group_by_zone_id[zone_id] = group_key

    if expand_groups:
        active_ids = set(ungrouped_ids)
        active_ids.update(selected_ids)
        for selected_id in selected_ids:
            group_key = group_by_zone_id.get(selected_id)
            if group_key is not None:
                active_ids.update(grouped_ids[group_key])
    else:
        if not ungrouped_ids.issubset(selected_ids):
            raise Community3DScopeError("Every ungrouped authored zone must remain in the Community 3D scope.")
        for member_ids in grouped_ids.values():
            selected_members = selected_ids & member_ids
            if selected_members and selected_members != member_ids:
                raise Community3DScopeError("Imported Community 3D layers must be selected as complete groups.")
        active_ids = selected_ids

    if not active_ids:
        raise Community3DScopeError("The selected Community 3D scope contains no physical zones.")
    return [zone for zone in physical_zones if str(zone.id) in active_ids]
