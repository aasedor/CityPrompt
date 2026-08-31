"""Isolated Direct 3D render endpoint.

Classic colored-polygon rendering remains in ``render.py``.  This module has
its own request contract and fail-closed service so Direct 3D can never invoke
the Classic path's maskless comparison fallback.
"""

from __future__ import annotations

import base64
import logging
import math
import re
from datetime import datetime, timezone

import boto3
from botocore.config import Config as BotoConfig
from fastapi import APIRouter, Depends, HTTPException, status
from geoalchemy2.shape import to_shape
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.render import (
    _WEEKLY_TOKEN_ALLOWANCE,
    _enforce_global_daily_render_cap,
    SaveRenderRequest,
    persist_render_to_gallery,
)
from app.core.config import get_settings
from app.core.database import get_db
from app.core.security import check_project_permission, is_admin_or_above, require_auth
from app.models.models import Building, RenderAuditLog, SiteZone, User
from app.schemas.direct_3d_render import Direct3DRenderRequest, Direct3DRenderResponse
from app.services.community_3d_scope import (
    Community3DScopeError,
    physical_community_3d_zones,
    resolve_community_3d_scope,
)
from app.services.direct_3d_render import (
    DIRECT_3D_MODEL,
    Direct3DProviderError,
    Direct3DRenderService,
    Direct3DValidationError,
    PreparedDirect3DCapture,
    estimate_direct_3d_token_cost,
    prepare_direct_3d_capture,
)
from app.services.direct_3d_identity import direct_3d_zone_design_identity
from app.services.public_realm_lego import (
    PUBLIC_REALM_FALLBACK_PROPERTY,
    PUBLIC_REALM_RECIPE_PROPERTY,
    PublicRealmPlanningError,
    plan_public_realm_zone_recipe,
    public_realm_fallback_marker,
    public_realm_recipe_identity,
)
from app.services.render_audit_images import put_image_with_thumbnail
from app.services.scene_revision import compiled_scene_revision_sha256
from app.services.residual_landscape import (
    ResidualSourceZone,
    community_3d_kind_for_source,
    community_3d_representation_hash,
    community_3d_source_hash,
    lock_residual_landscape_project,
    residual_landscape_source_hash,
)

logger = logging.getLogger(__name__)
router = APIRouter()
_DIRECT_RENDER_CAP_LOCK = 23_140_785_570_739


def _direct_state_conflict(message: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail={
            "code": "direct_3d_project_state_changed",
            "billed": False,
            "message": message,
        },
    )


def _direct_source_geometry(zone: SiteZone):
    """Read production GeoAlchemy geometry and legacy EWKT test fixtures."""

    try:
        return to_shape(zone.geometry)
    except (AssertionError, TypeError, ValueError, AttributeError):
        from shapely import wkt

        raw_geometry = str(zone.geometry)
        if ";" in raw_geometry and raw_geometry.upper().startswith("SRID="):
            raw_geometry = raw_geometry.split(";", 1)[1]
        try:
            return wkt.loads(raw_geometry)
        except Exception as exc:
            raise ValueError("Unusable Direct 3D source geometry") from exc


def _validate_direct_3d_project_zones(
    req: Direct3DRenderRequest,
    zones: list[SiteZone],
    available_buildings: dict[str, Building],
    *,
    bind_capture_instances: bool = True,
) -> list[dict[str, object]]:
    """Validate a paid capture against the locked, server-current parcel state.

    Image renders additionally bind every color-coded capture instance. Video
    uses the same scene-revision claims before reserving a run, but its browser
    route capture has its own temporal control manifest instead of one static
    instance-ID frame.
    """

    boundaries = [
        zone for zone in zones if zone.zone_type == "site_boundary" and getattr(zone, "is_active_boundary", True)
    ]
    all_physical_zones = physical_community_3d_zones(zones)
    if not all_physical_zones:
        raise _direct_state_conflict("This project has no compiled building, park, or street layers to render.")

    claims_by_zone = {str(claim.zone_id): claim for claim in req.community_3d_claims}
    try:
        physical_zones = resolve_community_3d_scope(
            all_physical_zones,
            claims_by_zone,
        )
    except Community3DScopeError:
        raise _direct_state_conflict(
            "The captured 3D layer set no longer matches this project. " "Run Generate to 3D again before rendering."
        )

    unsupported = [
        zone for zone in physical_zones if community_3d_kind_for_source(zone.zone_type, zone.properties) is None
    ]
    if unsupported:
        raise _direct_state_conflict(
            f"Direct 3D cannot safely represent {len(unsupported)} authored polygon"
            f"{'s' if len(unsupported) != 1 else ''}. Assign a supported building, "
            "park/plaza, street/path type before rendering."
        )

    stale_or_uncompiled: list[SiteZone] = []
    missing_buildings: list[SiteZone] = []
    for zone in physical_zones:
        kind = community_3d_kind_for_source(zone.zone_type, zone.properties)
        claim = claims_by_zone[str(zone.id)]
        stored_meta = (zone.properties or {}).get("community_3d")
        if (
            not isinstance(stored_meta, dict)
            or stored_meta.get("state") != "compiled"
            or stored_meta.get("kind") != kind
        ):
            stale_or_uncompiled.append(zone)
            continue
        stored_source_hash = stored_meta.get("source_hash")
        try:
            source_geometry = _direct_source_geometry(zone)
            current_source_hash = community_3d_source_hash(
                zone.zone_type,
                source_geometry,
                zone.properties,
            )
        except (AssertionError, TypeError, ValueError, AttributeError):
            stale_or_uncompiled.append(zone)
            continue
        if (
            not isinstance(stored_source_hash, str)
            or stored_source_hash.lower() != current_source_hash.lower()
            or claim.source_hash.lower() != current_source_hash.lower()
        ):
            stale_or_uncompiled.append(zone)
            continue
        building: Building | None = None
        if kind == "building":
            linked_building_id = str(zone.building_id) if zone.building_id else ""
            building = available_buildings.get(linked_building_id)
            specifications = building.specifications if building is not None else None
            generator = stored_meta.get("generator")
            representation_ready = bool(
                building is not None
                and (
                    (generator == "lego_assembly" and isinstance((specifications or {}).get("legoAssembly"), dict))
                    or (
                        generator == "planned_massing"
                        and isinstance((specifications or {}).get("plannedMassing"), dict)
                    )
                    or (
                        generator == "meshy"
                        and bool(
                            building.model_url or (isinstance(building.lod_urls, dict) and building.lod_urls.get("0"))
                        )
                    )
                )
            )
            if not linked_building_id or str(claim.building_id or "") != linked_building_id or not representation_ready:
                missing_buildings.append(zone)
                continue
        elif claim.building_id is not None:
            stale_or_uncompiled.append(zone)
            continue

        public_realm_recipe = (zone.properties or {}).get(PUBLIC_REALM_RECIPE_PROPERTY)
        public_realm_fallback = (zone.properties or {}).get(PUBLIC_REALM_FALLBACK_PROPERTY)
        plan_scenario = (zone.properties or {}).get("_plan_scenario")
        if kind in {"park", "street"} and not isinstance(public_realm_recipe, dict):
            canonical_fallback = public_realm_fallback_marker(
                zone.zone_type,
                zone.properties,
            )
            fallback_is_required = isinstance(plan_scenario, str) and bool(plan_scenario.strip())
            if (fallback_is_required or public_realm_fallback is not None) and (
                canonical_fallback is None or public_realm_fallback != canonical_fallback
            ):
                # AI/public-realm fallback is truthful only when Generate to
                # 3D explicitly stamped the current source identity. This
                # keeps pre-contract or edited layers from claiming fidelity.
                stale_or_uncompiled.append(zone)
                continue

        if kind in {"park", "street"} and isinstance(public_realm_recipe, dict):
            if public_realm_fallback is not None:
                stale_or_uncompiled.append(zone)
                continue
            try:
                canonical_recipe = plan_public_realm_zone_recipe(
                    zone.zone_type,
                    source_geometry,
                    zone.properties,
                    strict=True,
                )
            except (
                PublicRealmPlanningError,
                AssertionError,
                TypeError,
                ValueError,
                AttributeError,
            ):
                stale_or_uncompiled.append(zone)
                continue
            if canonical_recipe is None or canonical_recipe.model_dump(mode="json") != public_realm_recipe:
                # The stored recipe may be internally valid while describing a
                # different metric target. Direct must bind the claimed kit to
                # the exact locked source geometry, not merely to its own hash.
                stale_or_uncompiled.append(zone)
                continue

        generator = stored_meta.get("generator")
        stored_representation_hash = stored_meta.get("representation_hash")
        current_representation_hash = community_3d_representation_hash(
            kind=kind,
            generator=str(generator or ""),
            source_hash=current_source_hash,
            building=building,
            public_realm_recipe=public_realm_recipe,
            public_realm_fallback=(public_realm_fallback if not isinstance(public_realm_recipe, dict) else None),
        )
        if (
            current_representation_hash is None
            or not isinstance(stored_representation_hash, str)
            or stored_representation_hash.lower() != current_representation_hash.lower()
            or claim.representation_hash.lower() != current_representation_hash.lower()
        ):
            stale_or_uncompiled.append(zone)

    if stale_or_uncompiled:
        raise _direct_state_conflict(
            f"{len(stale_or_uncompiled)} compiled 3D layer"
            f"{'s are' if len(stale_or_uncompiled) != 1 else ' is'} stale or missing a "
            "source fingerprint. Run Generate to 3D again before rendering."
        )
    if missing_buildings:
        raise _direct_state_conflict(
            f"{len(missing_buildings)} compiled building model"
            f"{'s are' if len(missing_buildings) != 1 else ' is'} no longer available. "
            "Run Generate to 3D again before rendering."
        )

    server_inventory = (
        _bind_instance_manifest_to_server_zones(req, physical_zones, zones) if bind_capture_instances else []
    )
    server_inventory = _annotate_source_locked_rlasm_inventory(
        server_inventory,
        available_buildings,
    )
    if len(boundaries) > 1:
        raise _direct_state_conflict(
            "Direct 3D requires one authoritative site boundary. Resolve duplicate "
            "boundaries and run Generate to 3D again before rendering."
        )
    if not boundaries:
        if req.residual_landscape_claim is not None or len(physical_zones) > 1:
            raise _direct_state_conflict(
                "This multi-zone project no longer has its compiled site boundary. "
                "Refresh and rebuild the scene with Generate to 3D before rendering."
            )
        return server_inventory

    boundary = boundaries[0]
    stored = (boundary.properties or {}).get("community_3d_landscape")
    claim = req.residual_landscape_claim
    if not isinstance(stored, dict) or stored.get("state") != "compiled" or claim is None:
        raise _direct_state_conflict("Residual landscaping is not current. Run Generate to 3D again before rendering.")
    stored_hash = stored.get("source_hash")
    stored_boundary_id = stored.get("boundary_id")
    try:
        current_residual_hash = residual_landscape_source_hash(
            to_shape(boundary.geometry),
            [
                ResidualSourceZone(
                    zone_id=str(zone.id),
                    kind=(community_3d_kind_for_source(zone.zone_type, zone.properties) or str(zone.zone_type)),
                    role=(
                        str((zone.properties or {}).get("_plan_role"))
                        if (zone.properties or {}).get("_plan_role") is not None
                        else None
                    ),
                    geometry=to_shape(zone.geometry),
                )
                for zone in physical_zones
            ],
        )
    except (TypeError, ValueError, AttributeError):
        raise _direct_state_conflict(
            "The parcel geometry changed after capture. Refresh and rebuild the scene "
            "with Generate to 3D before spending on a Direct render."
        )
    if (
        stored_boundary_id != str(boundary.id)
        or str(claim.boundary_id) != str(boundary.id)
        or not isinstance(stored_hash, str)
        or stored_hash.lower() != current_residual_hash.lower()
        or claim.source_hash.lower() != current_residual_hash.lower()
    ):
        raise _direct_state_conflict(
            "The parcel changed after capture. Refresh and run Generate to 3D again before "
            "spending on a Direct render."
        )
    return server_inventory


def _annotate_source_locked_rlasm_inventory(
    server_inventory: list[dict[str, object]],
    available_buildings: dict[str, Building],
) -> list[dict[str, object]]:
    """Attach a trusted pixel-lock marker to reviewed RLASM instances.

    The browser may describe only screen-space identity. Whether a linked GLB
    is a reviewed RLASM delivery remains server-owned state, so this marker is
    attached only after the normal project, representation-hash, and
    building-ID checks have passed.
    """

    annotated: list[dict[str, object]] = []
    for raw_item in server_inventory:
        item = dict(raw_item)
        building_id = str(item.get("building_id") or "")
        building = available_buildings.get(building_id)
        specifications = building.specifications if building is not None else None
        rlasm = specifications.get("rlasm") if isinstance(specifications, dict) else None
        source_locked = bool(
            building is not None
            and str(getattr(building, "generation_engine", None) or "").lower() == "rlasm"
            and isinstance(rlasm, dict)
            and rlasm.get("source_locked") is True
        )
        if source_locked:
            item["source_locked_rlasm"] = True
            delivery_sha256 = str(rlasm.get("delivery_sha256") or "").lower()
            if re.fullmatch(r"[a-f0-9]{64}", delivery_sha256):
                item["rlasm_delivery_sha256"] = delivery_sha256
        annotated.append(item)
    return annotated


def _fnv1a32(value: str) -> int:
    """Match the browser's ``Math.imul`` FNV-1a identity for ASCII zone IDs."""

    value_hash = 0x811C9DC5
    for character in value:
        value_hash ^= ord(character)
        value_hash = (value_hash * 0x01000193) & 0xFFFFFFFF
    return value_hash


def _canonical_junction_instance_id(source_zone_ids: list[str]) -> str:
    normalized = sorted({str(value).strip() for value in source_zone_ids if str(value).strip()})
    source_hash = _fnv1a32(":".join(normalized))
    return f"junction:zones-{source_hash:08x}:street"


def _valid_centerline_points(value: object) -> list[tuple[float, float]] | None:
    if not isinstance(value, list) or len(value) < 2:
        return None
    points: list[tuple[float, float]] = []
    for candidate in value:
        if not isinstance(candidate, (list, tuple)) or len(candidate) < 2:
            return None
        try:
            longitude = float(candidate[0])
            latitude = float(candidate[1])
        except (TypeError, ValueError):
            return None
        if not math.isfinite(longitude) or not math.isfinite(latitude) or abs(longitude) > 180 or abs(latitude) > 90:
            return None
        point = (longitude, latitude)
        if points and all(abs(a - b) < 1e-12 for a, b in zip(points[-1], point)):
            continue
        points.append(point)
    return points if len(points) >= 2 else None


def _street_zone_centerline(zone: SiteZone) -> list[tuple[float, float]] | None:
    """Read the persisted centerline, falling back to the authored geometry."""

    persisted = _valid_centerline_points((zone.properties or {}).get("plan_centerline"))
    if persisted is not None:
        return persisted
    try:
        geometry = _direct_source_geometry(zone)
    except ValueError:
        return None
    if geometry.geom_type == "LineString":
        return _valid_centerline_points([list(point) for point in geometry.coords])
    if geometry.geom_type == "MultiLineString":
        lines = list(geometry.geoms)
        if not lines:
            return None
        longest = max(lines, key=lambda line: line.length)
        return _valid_centerline_points([list(point) for point in longest.coords])
    if geometry.geom_type == "MultiPolygon":
        polygons = list(geometry.geoms)
        if not polygons:
            return None
        geometry = max(polygons, key=lambda polygon: polygon.area)
    if geometry.geom_type != "Polygon":
        return None
    # GeoJSON ring start/orientation is not a stable signal after PostGIS has
    # normalized a polygon. Recover the buffered street's dominant axis from
    # its minimum rotated rectangle instead of trusting vertex-pair order.
    rectangle = list(geometry.minimum_rotated_rectangle.exterior.coords)
    if len(rectangle) >= 4:
        latitude = float(geometry.centroid.y)
        meters_per_longitude = max(1.0, 111_320 * math.cos(math.radians(latitude)))
        longest = max(
            zip(rectangle, rectangle[1:]),
            key=lambda segment: math.hypot(
                (segment[1][0] - segment[0][0]) * meters_per_longitude,
                (segment[1][1] - segment[0][1]) * 111_320,
            ),
        )
        delta_longitude = float(longest[1][0] - longest[0][0])
        delta_latitude = float(longest[1][1] - longest[0][1])
        center_longitude = float(geometry.centroid.x)
        center_latitude = latitude
        rectangle_centerline = [
            [
                center_longitude - delta_longitude / 2,
                center_latitude - delta_latitude / 2,
            ],
            [
                center_longitude + delta_longitude / 2,
                center_latitude + delta_latitude / 2,
            ],
        ]
        recovered = _valid_centerline_points(rectangle_centerline)
        if recovered is not None:
            return recovered
    ring = [(float(x), float(y)) for x, y, *_rest in geometry.exterior.coords]
    if len(ring) > 2 and abs(ring[0][0] - ring[-1][0]) < 1e-10 and abs(ring[0][1] - ring[-1][1]) < 1e-10:
        ring = ring[:-1]
    half = len(ring) // 2
    if half < 2:
        return _valid_centerline_points([list(point) for point in ring])
    centerline = [
        (
            (ring[index][0] + ring[len(ring) - 1 - index][0]) / 2,
            (ring[index][1] + ring[len(ring) - 1 - index][1]) / 2,
        )
        for index in range(half)
    ]
    return _valid_centerline_points([list(point) for point in centerline])


def _effective_street_width(zone: SiteZone) -> float:
    properties = zone.properties or {}
    try:
        width = float(properties.get("width", 10))
    except (TypeError, ValueError):
        width = 10
    if not math.isfinite(width) or width <= 0:
        width = 10
    try:
        lanes = max(0.0, float(properties.get("lane_count", 2)))
    except (TypeError, ValueError):
        lanes = 2
    if not math.isfinite(lanes):
        lanes = 2
    lego = properties.get("public_realm_lego")
    lego = lego if isinstance(lego, dict) else {}
    semantic = " ".join(
        str(value or "").lower().replace("-", "_")
        for value in (
            properties.get("street_role"),
            properties.get("road_archetype_id"),
            lego.get("archetype_id"),
        )
    )
    if lanes == 0 or any(token in semantic for token in ("trail", "path", "cycleway", "multi_use", "laneway", "alley")):
        return width
    return max(width, lanes * 3.5)


def _street_supports_v1_four_way_junction(zone: SiteZone) -> bool:
    """Mirror the browser's executable street-axis eligibility, fail closed."""

    properties = zone.properties or {}
    # Junction anchoring requires a centerline BOTH sides derive identically.
    # Without a valid persisted plan_centerline, the browser walks polygon
    # vertices while this proof takes the minimum-rotated-rectangle axis —
    # for degenerate planner fragments (e.g. a 4 m roundabout access stub
    # whose centerline the AI planner omitted) the two diverge and every
    # claim 409s forever. So: a present-but-invalid centerline never anchors
    # a junction, and a planner-authored street (markers below) must carry a
    # valid one. Hand-drawn streets (no markers, line-sourced) keep the
    # geometry fallback, which both sides derive the same way.
    persisted_centerline = _valid_centerline_points(properties.get("plan_centerline"))
    if persisted_centerline is None:
        if "plan_centerline" in properties:
            return False
        if "_plan_snapshot_id" in properties or "_imported_from" in properties:
            return False
    raw_recipe = properties.get(PUBLIC_REALM_RECIPE_PROPERTY)
    if not isinstance(raw_recipe, dict):
        return False
    identity = public_realm_recipe_identity(raw_recipe)
    if identity is None:
        return False
    recipe = identity["recipe"]
    if not isinstance(recipe, dict):
        return False
    target = recipe.get("target")
    if not isinstance(target, dict):
        return False
    if (
        recipe.get("schema_version") != 1
        or recipe.get("family_version") != 1
        or recipe.get("kind") != "street"
        or recipe.get("generator") != "street_section"
        or target.get("target_type") != "street_segment"
        or recipe.get("family_id")
        not in {
            "street_local_public_realm",
            "street_complete_main_18m",
            "street_complete_main_22m",
        }
    ):
        return False
    recipe_archetype_id = str(recipe.get("archetype_id") or "").strip()
    recipe_variant_id = str(recipe.get("variant_id") or "").strip()
    persisted_archetype_id = str(properties.get("road_archetype_id") or "").strip()
    persisted_variant_id = str(properties.get("road_selected_variant_id") or "").strip()
    if persisted_archetype_id and persisted_archetype_id != recipe_archetype_id:
        return False
    if persisted_variant_id and persisted_variant_id != recipe_variant_id:
        return False
    semantic = " ".join(
        str(value or "").lower().replace("-", "_")
        for value in (
            properties.get("street_role"),
            properties.get("road_archetype_id"),
            recipe.get("archetype_id"),
            recipe.get("family_id"),
        )
    )
    return _effective_street_width(zone) >= 6 and not any(
        token in semantic for token in ("trail", "path", "laneway", "alley", "roundabout")
    )


def _angle_distance(first: float, second: float) -> float:
    delta = abs((first - second) % (math.pi * 2))
    return min(delta, math.pi * 2 - delta)


def _undirected_angle(value: float) -> float:
    normalized = value % (math.pi * 2)
    return normalized - math.pi if normalized >= math.pi else normalized


def _undirected_angle_distance(first: float, second: float) -> float:
    delta = abs(_undirected_angle(first) - _undirected_angle(second))
    return min(delta, math.pi - delta)


def _closest_point_on_segment(
    point: tuple[float, float],
    start: tuple[float, float],
    end: tuple[float, float],
) -> tuple[float, float, float, float]:
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    length_squared = dx * dx + dy * dy
    interpolation = (
        max(
            0.0,
            min(
                1.0,
                ((point[0] - start[0]) * dx + (point[1] - start[1]) * dy) / length_squared,
            ),
        )
        if length_squared > 0
        else 0.0
    )
    x = start[0] + dx * interpolation
    y = start[1] + dy * interpolation
    return x, y, interpolation, math.hypot(point[0] - x, point[1] - y)


def _segment_intersection(
    first_start: tuple[float, float],
    first_end: tuple[float, float],
    second_start: tuple[float, float],
    second_end: tuple[float, float],
) -> tuple[float, float] | None:
    first_dx = first_end[0] - first_start[0]
    first_dy = first_end[1] - first_start[1]
    second_dx = second_end[0] - second_start[0]
    second_dy = second_end[1] - second_start[1]
    denominator = first_dx * second_dy - first_dy * second_dx
    if abs(denominator) < 1e-7:
        return None
    offset_x = second_start[0] - first_start[0]
    offset_y = second_start[1] - first_start[1]
    first_t = (offset_x * second_dy - offset_y * second_dx) / denominator
    second_t = (offset_x * first_dy - offset_y * first_dx) / denominator
    if first_t < -1e-6 or first_t > 1 + 1e-6 or second_t < -1e-6 or second_t > 1 + 1e-6:
        return None
    return (
        first_start[0] + first_dx * first_t,
        first_start[1] + first_dy * first_t,
    )


def _street_sources_form_four_arm_junction(street_zones: list[SiteZone]) -> bool:
    """Independently prove the claimed street sources form one four-arm node."""

    if len(street_zones) < 2:
        return False
    geographic_axes: list[dict[str, object]] = []
    for zone in street_zones:
        centerline = _street_zone_centerline(zone)
        width = _effective_street_width(zone)
        if centerline is None or len(centerline) > 512 or not _street_supports_v1_four_way_junction(zone):
            return False
        geographic_axes.append(
            {
                "zone_id": str(zone.id),
                "width": width,
                "points": centerline,
            }
        )
    all_points = [point for axis in geographic_axes for point in axis["points"]]  # type: ignore[union-attr]
    origin_longitude = sum(point[0] for point in all_points) / len(all_points)
    origin_latitude = sum(point[1] for point in all_points) / len(all_points)
    meters_per_longitude = max(
        1.0,
        111_320 * math.cos(math.radians(origin_latitude)),
    )
    axes: list[dict[str, object]] = []
    for geographic_axis in geographic_axes:
        axes.append(
            {
                **geographic_axis,
                "points": [
                    (
                        (point[0] - origin_longitude) * meters_per_longitude,
                        (point[1] - origin_latitude) * 111_320,
                    )
                    for point in geographic_axis["points"]  # type: ignore[union-attr]
                ],
            }
        )

    candidates: list[dict[str, object]] = []
    for first_index, first in enumerate(axes):
        first_points = first["points"]
        first_width = float(first["width"])
        for second in axes[first_index + 1 :]:
            second_points = second["points"]
            second_width = float(second["width"])
            tolerance = max(first_width, second_width) / 2 + 2
            for a in range(len(first_points) - 1):  # type: ignore[arg-type]
                first_start = first_points[a]  # type: ignore[index]
                first_end = first_points[a + 1]  # type: ignore[index]
                first_bearing = math.atan2(
                    first_end[1] - first_start[1],
                    first_end[0] - first_start[0],
                )
                for b in range(len(second_points) - 1):  # type: ignore[arg-type]
                    second_start = second_points[b]  # type: ignore[index]
                    second_end = second_points[b + 1]  # type: ignore[index]
                    second_bearing = math.atan2(
                        second_end[1] - second_start[1],
                        second_end[0] - second_start[0],
                    )
                    crossing_angle = _undirected_angle_distance(
                        first_bearing,
                        second_bearing,
                    )
                    if crossing_angle < math.pi / 6 or crossing_angle > math.pi * 5 / 6:
                        continue
                    intersection = _segment_intersection(
                        first_start,
                        first_end,
                        second_start,
                        second_end,
                    )
                    if intersection is not None:
                        candidates.append(
                            {
                                "x": intersection[0],
                                "y": intersection[1],
                                "zone_ids": {
                                    str(first["zone_id"]),
                                    str(second["zone_id"]),
                                },
                            }
                        )
                        continue
                    for endpoint in (first_start, first_end):
                        projected = _closest_point_on_segment(
                            endpoint,
                            second_start,
                            second_end,
                        )
                        if projected[3] <= tolerance:
                            candidates.append(
                                {
                                    "x": projected[0],
                                    "y": projected[1],
                                    "zone_ids": {
                                        str(first["zone_id"]),
                                        str(second["zone_id"]),
                                    },
                                }
                            )
                    for endpoint in (second_start, second_end):
                        projected = _closest_point_on_segment(
                            endpoint,
                            first_start,
                            first_end,
                        )
                        if projected[3] <= tolerance:
                            candidates.append(
                                {
                                    "x": projected[0],
                                    "y": projected[1],
                                    "zone_ids": {
                                        str(first["zone_id"]),
                                        str(second["zone_id"]),
                                    },
                                }
                            )

    clusters: list[dict[str, object]] = []
    for candidate in candidates:
        cluster = next(
            (
                item
                for item in clusters
                if math.hypot(
                    float(item["x"]) - float(candidate["x"]),
                    float(item["y"]) - float(candidate["y"]),
                )
                <= 4
            ),
            None,
        )
        if cluster is None:
            clusters.append(
                {
                    "x": candidate["x"],
                    "y": candidate["y"],
                    "count": 1,
                    "zone_ids": set(candidate["zone_ids"]),
                }
            )
        else:
            count = int(cluster["count"])
            cluster["x"] = (float(cluster["x"]) * count + float(candidate["x"])) / (count + 1)
            cluster["y"] = (float(cluster["y"]) * count + float(candidate["y"])) / (count + 1)
            cluster["count"] = count + 1
            cluster_zone_ids = cluster["zone_ids"]
            if isinstance(cluster_zone_ids, set):
                cluster_zone_ids.update(candidate["zone_ids"])

    expected_zone_ids = {str(zone.id) for zone in street_zones}
    for cluster in clusters:
        arms: list[dict[str, object]] = []
        contributing_zone_ids: set[str] = set()
        cluster_zone_ids = cluster["zone_ids"]
        cluster_connection_tolerance = max(
            2.0,
            *(
                float(axis["width"]) / 2 + 2
                for axis in axes
                if isinstance(cluster_zone_ids, set) and str(axis["zone_id"]) in cluster_zone_ids
            ),
        )
        for axis in axes:
            points = axis["points"]
            best: tuple[float, float, float, float, int] | None = None
            for index in range(len(points) - 1):  # type: ignore[arg-type]
                closest = _closest_point_on_segment(
                    (float(cluster["x"]), float(cluster["y"])),
                    points[index],  # type: ignore[index]
                    points[index + 1],  # type: ignore[index]
                )
                candidate_best = (*closest, index)
                if best is None or candidate_best[3] < best[3]:
                    best = candidate_best
            if best is None or best[3] > max(
                float(axis["width"]) / 2 + 2,
                cluster_connection_tolerance,
            ):
                continue
            contributing_zone_ids.add(str(axis["zone_id"]))
            segment_index = best[4]
            start = points[segment_index]  # type: ignore[index]
            end = points[segment_index + 1]  # type: ignore[index]
            bearing = math.atan2(end[1] - start[1], end[0] - start[0])
            at_first_end = segment_index == 0 and best[2] < 0.08
            at_last_end = segment_index == len(points) - 2 and best[2] > 0.92  # type: ignore[arg-type]
            if not at_last_end:
                arms.append({"bearing": bearing, "width": float(axis["width"])})
            if not at_first_end:
                arms.append(
                    {
                        "bearing": (bearing + math.pi) % (math.pi * 2),
                        "width": float(axis["width"]),
                    }
                )
        if contributing_zone_ids != expected_zone_ids:
            continue
        grouped_arms: list[dict[str, float]] = []
        for arm in arms:
            matching = next(
                (
                    item
                    for item in grouped_arms
                    if _angle_distance(item["bearing"], float(arm["bearing"])) < math.pi / 9
                ),
                None,
            )
            if matching is None:
                grouped_arms.append(
                    {
                        "bearing": float(arm["bearing"]),
                        "width": float(arm["width"]),
                    }
                )
            else:
                matching["width"] = max(matching["width"], float(arm["width"]))
        if len(grouped_arms) != 4:
            continue
        orientations: list[float] = []
        for arm in grouped_arms:
            orientation = _undirected_angle(arm["bearing"])
            if not any(_undirected_angle_distance(existing, orientation) < math.pi / 12 for existing in orientations):
                orientations.append(orientation)
        if len(orientations) != 2:
            continue
        separation = _undirected_angle_distance(orientations[0], orientations[1])
        if math.pi / 6 <= separation <= math.pi * 5 / 6:
            return True
    return False


def _bind_instance_manifest_to_server_zones(
    req: Direct3DRenderRequest,
    physical_zones: list[SiteZone],
    all_zones: list[SiteZone],
) -> list[dict[str, object]]:
    """Bind screen-space instances to the selected server-owned scene scope."""

    expected: dict[str, dict[str, str | None]] = {}
    for zone in physical_zones:
        semantic_class = community_3d_kind_for_source(
            zone.zone_type,
            zone.properties,
        )
        if semantic_class not in {"building", "park", "street"}:
            # Unsupported kinds were rejected by the caller above.
            continue
        expected[str(zone.id)] = {
            "semantic_class": semantic_class,
            "building_id": str(zone.building_id) if zone.building_id else None,
            "design_identity": direct_3d_zone_design_identity(
                semantic_class,
                zone.properties,
            ),
        }
    authorized_zone_ids = set(expected)
    authorized_zone_ids.update(str(zone.id) for zone in all_zones if zone.zone_type == "site_boundary")
    all_zones_by_id = {str(zone.id): zone for zone in all_zones if str(zone.id) in authorized_zone_ids}
    all_zone_ids = set(all_zones_by_id)
    allowed_supplemental_surfaces: set[tuple[str, str]] = set()
    for zone_id, zone in all_zones_by_id.items():
        source_kind = community_3d_kind_for_source(
            zone.zone_type,
            zone.properties,
        )
        # The frontend ground layer labels park/street fills with their primary
        # role. Building pads and non-program zones (principally the site
        # boundary) are the only server-derived ground supplements.
        if source_kind not in {"park", "street"}:
            allowed_supplemental_surfaces.add((zone_id, "ground"))

        stored_landscape = (zone.properties or {}).get("community_3d_landscape")
        if (
            zone.zone_type == "site_boundary"
            and isinstance(stored_landscape, dict)
            and stored_landscape.get("state") == "compiled"
            and str(stored_landscape.get("boundary_id")) == zone_id
            and isinstance(stored_landscape.get("placements"), list)
            and bool(stored_landscape["placements"])
        ):
            allowed_supplemental_surfaces.add((zone_id, "landscape"))

    if not req.instance_id_manifest:
        # Legacy source_anchored requests remain compatible, while their
        # provider prompt still receives a server-owned inventory.
        return [
            {
                "instance_id": f"zone:{zone_id}:{item['semantic_class']}",
                "semantic_class": item["semantic_class"],
                "zone_id": zone_id,
                "building_id": item["building_id"],
                "source_zone_ids": [],
                "design_identity": item["design_identity"],
            }
            for zone_id, item in sorted(expected.items())
        ]

    seen_primary_zone_ids: set[str] = set()
    seen_instance_ids: set[str] = set()
    server_inventory: list[dict[str, object]] = []
    for _color, descriptor in sorted(req.instance_id_manifest.items()):
        zone_id = str(descriptor.zone_id) if descriptor.zone_id else None
        source_zone_ids = sorted({str(value) for value in descriptor.source_zone_ids})
        expected_item = expected.get(zone_id) if zone_id is not None else None
        is_supplemental_surface = descriptor.semantic_class in {
            "ground",
            "landscape",
        }
        if descriptor.instance_id in seen_instance_ids:
            raise _direct_state_conflict(
                "The instance inventory repeats a screen-space identity. Refresh " "the scene before rendering."
            )
        seen_instance_ids.add(descriptor.instance_id)
        unknown_source_ids = sorted(set(source_zone_ids) - all_zone_ids)
        if unknown_source_ids:
            raise _direct_state_conflict(
                "The instance inventory references source zones that are no longer "
                "part of this project. Refresh the scene before rendering."
            )
        for source_zone_id in source_zone_ids:
            source_expected = expected.get(source_zone_id)
            if descriptor.semantic_class in {"building", "park"} and (
                source_expected is None or source_expected["semantic_class"] != descriptor.semantic_class
            ):
                raise _direct_state_conflict(
                    "The instance inventory source-zone role no longer matches the "
                    "compiled project. Refresh the scene before rendering."
                )
            if descriptor.semantic_class == "street" and (
                source_expected is None or source_expected["semantic_class"] != "street"
            ):
                raise _direct_state_conflict(
                    "Street topology instances may reference only compiled street "
                    "zones. Refresh the scene before rendering."
                )

        if zone_id is None:
            is_topology_street = descriptor.semantic_class == "street" and 2 <= len(source_zone_ids) <= 4
            if descriptor.semantic_class in {"building", "park", "street"} and not is_topology_street:
                raise _direct_state_conflict(
                    "Every building, park, and street instance must identify its "
                    "server-authored zone, except validated street junctions. "
                    "Refresh the scene before rendering."
                )
            if descriptor.semantic_class in {"ground", "landscape"}:
                raise _direct_state_conflict(
                    "Supplemental ground and landscape instances must identify their "
                    "server-authored zone. Refresh the scene before rendering."
                )
            if is_topology_street:
                canonical_junction_id = _canonical_junction_instance_id(source_zone_ids)
                if descriptor.instance_id != canonical_junction_id:
                    raise _direct_state_conflict(
                        "The street-junction identity does not match its persisted "
                        "street sources. Refresh the scene before rendering."
                    )
                source_streets = [all_zones_by_id[source_id] for source_id in source_zone_ids]
                if not _street_sources_form_four_arm_junction(source_streets):
                    raise _direct_state_conflict(
                        "The claimed street sources do not form a persisted four-arm "
                        "junction. Refresh the scene before rendering."
                    )
        else:
            if zone_id not in all_zone_ids:
                raise _direct_state_conflict(
                    "The instance inventory references a zone that is no longer "
                    "part of this project. Refresh the scene before rendering."
                )
            if source_zone_ids:
                raise _direct_state_conflict(
                    "Zone-bound instances cannot claim additional source zones. " "Refresh the scene before rendering."
                )
            canonical_instance_id = f"zone:{zone_id}:{descriptor.semantic_class}"
            if descriptor.instance_id != canonical_instance_id:
                raise _direct_state_conflict(
                    "The instance identity does not match its server-authored zone "
                    "and semantic role. Refresh the scene before rendering."
                )
            if is_supplemental_surface and (zone_id, descriptor.semantic_class) not in allowed_supplemental_surfaces:
                raise _direct_state_conflict(
                    "The supplemental surface is not present in the server-compiled "
                    "scene. Refresh the scene before rendering."
                )
            if not is_supplemental_surface:
                if expected_item is None:
                    raise _direct_state_conflict(
                        "Only supplemental ground or landscape may bind to the site "
                        "boundary. Refresh the scene before rendering."
                    )
                if zone_id in seen_primary_zone_ids:
                    raise _direct_state_conflict(
                        "The instance inventory represents one primary authored zone "
                        "more than once. Refresh the scene before rendering."
                    )
                if descriptor.semantic_class != expected_item["semantic_class"]:
                    raise _direct_state_conflict(
                        "The instance inventory relabels a server-authored zone. Refresh " "the scene before rendering."
                    )
                seen_primary_zone_ids.add(zone_id)
            expected_building_id = expected_item["building_id"] if expected_item is not None else None
            descriptor_building_id = str(descriptor.building_id) if descriptor.building_id else None
            primary_building = (
                not is_supplemental_surface
                and expected_item is not None
                and expected_item["semantic_class"] == "building"
            )
            if (primary_building and descriptor_building_id != expected_building_id) or (
                descriptor_building_id is not None and descriptor_building_id != expected_building_id
            ):
                raise _direct_state_conflict(
                    "The instance inventory building identity no longer matches the "
                    "compiled model. Refresh the scene before rendering."
                )
        server_inventory.append(
            {
                "instance_id": descriptor.instance_id,
                "semantic_class": descriptor.semantic_class,
                "zone_id": zone_id,
                "building_id": (str(descriptor.building_id) if descriptor.building_id else None),
                "source_zone_ids": source_zone_ids,
                "design_identity": (
                    expected_item["design_identity"]
                    if expected_item is not None and not is_supplemental_surface
                    else None
                ),
            }
        )

    if seen_primary_zone_ids != set(expected):
        raise _direct_state_conflict(
            "The exact instance inventory no longer matches every compiled building, "
            "park, and street. Refresh the scene before rendering."
        )
    return sorted(server_inventory, key=lambda item: str(item["instance_id"]))


async def _reserve_direct_render(
    db: AsyncSession,
    user: User,
    *,
    token_cost: int,
    daily_cap: int,
    prompt: str,
    project_id,
) -> RenderAuditLog:
    """Atomically reserve credits and a daily-cap audit row before OpenAI."""

    try:
        if daily_cap > 0:
            # All Direct 3D requests serialize the cap check + reservation in
            # one PostgreSQL transaction. The committed reservation is then
            # visible to the next request's daily sum before it can proceed.
            await db.execute(
                text("SELECT pg_advisory_xact_lock(:lock_key)"),
                {"lock_key": _DIRECT_RENDER_CAP_LOCK},
            )
            await _enforce_global_daily_render_cap(db, token_cost, daily_cap)

        if not is_admin_or_above(user):
            await db.refresh(user, with_for_update=True)
            now = datetime.now(timezone.utc)
            if user.credits_reset_at is None or (now - user.credits_reset_at).days >= 7:
                user.render_credits = _WEEKLY_TOKEN_ALLOWANCE
                user.credits_reset_at = now
            if user.render_credits < token_cost:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=(
                        f"Not enough tokens. This Direct 3D render costs {token_cost} tokens "
                        f"but you have {user.render_credits}. Tokens reset weekly."
                    ),
                )
            user.render_credits -= token_cost
            db.add(user)

        reservation = RenderAuditLog(
            user_id=user.id,
            user_email=user.email,
            model=DIRECT_3D_MODEL,
            tokens_spent=token_cost,
            project_id=project_id,
            prompt_preview=f"[Direct 3D reserved] {prompt[:470]}",
        )
        db.add(reservation)
        await db.commit()
        return reservation
    except Exception:
        await db.rollback()
        raise


async def _refund_unproduced_direct_render(
    db: AsyncSession,
    user: User,
    reservation: RenderAuditLog,
    *,
    token_cost: int,
    detail: str,
) -> None:
    """Release a reservation only when OpenAI produced no image."""

    try:
        if not is_admin_or_above(user):
            await db.refresh(user, with_for_update=True)
            user.render_credits += token_cost
            db.add(user)
        reservation.tokens_spent = 0
        reservation.prompt_preview = f"[Direct 3D unbilled failure] {detail[:450]}"
        db.add(reservation)
        await db.commit()
    except Exception:
        await db.rollback()
        logger.exception("Failed to refund unproduced Direct 3D reservation %s", reservation.id)
        raise


async def _finalize_direct_audit(
    db: AsyncSession,
    reservation: RenderAuditLog,
    *,
    input_b64: str,
    output_b64: str | None,
    status_label: str,
    detail: str,
) -> None:
    """Attach canonical images to the pre-call reservation audit row."""

    # Persist billed outcome text before touching object storage. Even when S3
    # is unavailable, the cap/credit reservation remains an auditable attempt.
    reservation.prompt_preview = f"[Direct 3D {status_label}] {detail[:460]}"
    db.add(reservation)
    await db.commit()

    settings = get_settings()
    s3 = boto3.client(
        "s3",
        endpoint_url=settings.s3_endpoint_url,
        aws_access_key_id=settings.s3_access_key,
        aws_secret_access_key=settings.s3_secret_key,
        region_name=settings.s3_region,
        config=BotoConfig(signature_version="s3v4"),
    )
    bucket = settings.s3_bucket_name
    try:
        s3.head_bucket(Bucket=bucket)
    except Exception:
        s3.create_bucket(Bucket=bucket)

    input_raw = base64.b64decode(input_b64, validate=True)
    input_key = f"render-audit/{reservation.id}/input.png"
    put_image_with_thumbnail(s3, bucket, input_key, input_raw)
    reservation.input_image_key = input_key
    if output_b64:
        output_raw = base64.b64decode(output_b64, validate=True)
        output_key = f"render-audit/{reservation.id}/output.png"
        put_image_with_thumbnail(s3, bucket, output_key, output_raw)
        reservation.output_image_key = output_key
    db.add(reservation)
    await db.commit()


@router.post("/generate-direct-3d", response_model=Direct3DRenderResponse)
async def generate_direct_3d_render(
    req: Direct3DRenderRequest,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
) -> Direct3DRenderResponse:
    """Render an authoritative clean 3D capture under the requested mode contract."""

    settings = get_settings()

    await check_project_permission(req.project_id, user, db, required="viewer")
    await lock_residual_landscape_project(db, req.project_id)
    zones_result = await db.execute(
        select(SiteZone).where(SiteZone.project_id == req.project_id).execution_options(populate_existing=True)
    )
    buildings_result = await db.execute(select(Building).where(Building.project_id == req.project_id))
    current_buildings = list(buildings_result.scalars().all())
    server_inventory = _validate_direct_3d_project_zones(
        req,
        list(zones_result.scalars().all()),
        {str(building.id): building for building in current_buildings},
    )
    scene_revision_sha256 = compiled_scene_revision_sha256(
        req.community_3d_claims,
        req.residual_landscape_claim,
    )

    if not settings.openai_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Direct 3D rendering is unavailable because OpenAI is not configured.",
        )

    try:
        capture: PreparedDirect3DCapture = prepare_direct_3d_capture(req)
    except Direct3DValidationError as exc:
        logger.info("Direct 3D capture rejected: %s", exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    token_cost = estimate_direct_3d_token_cost(
        capture.normalized_beauty.width,
        capture.normalized_beauty.height,
        object_id_attached=capture.normalized_object_id is not None,
        instance_id_attached=capture.normalized_instance_id is not None,
        control_bundle_version=req.control_bundle_version,
    )

    reservation = await _reserve_direct_render(
        db,
        user,
        token_cost=token_cost,
        daily_cap=settings.render_global_daily_token_cap,
        prompt=(f"[mode={req.presentation_mode} style={req.style}] {req.prompt}"),
        project_id=req.project_id,
    )
    try:
        result = await Direct3DRenderService(settings.openai_api_key).generate(
            req,
            capture,
            server_inventory=server_inventory,
        )
    except Direct3DProviderError as exc:
        logger.warning("Direct 3D provider failure: %s", exc)
        if not exc.refund_eligible:
            status_label = "billed safety failure" if exc.billing_status == "produced" else "billing unknown"
            try:
                await _finalize_direct_audit(
                    db,
                    reservation,
                    input_b64=capture.audit_input_base64,
                    output_b64=exc.provider_image_base64,
                    status_label=status_label,
                    detail=str(exc),
                )
            except Exception as audit_exc:
                logger.warning("Failed to finalize billed Direct 3D failure audit: %s", audit_exc)
            if exc.billing_status == "produced":
                error_detail = {
                    "code": "direct_3d_billed_safety_rejection",
                    "billed": True,
                    "message": (
                        "An image was produced but rejected by Direct 3D safety checks; "
                        f"this attempt was charged. {exc}"
                    ),
                }
            else:
                error_detail = {
                    "code": "direct_3d_billing_unknown",
                    "billed": True,
                    "message": (
                        "The provider request outcome could not be confirmed after submission; "
                        f"the reservation was conservatively retained. {exc}"
                    ),
                }
        else:
            await _refund_unproduced_direct_render(
                db,
                user,
                reservation,
                token_cost=token_cost,
                detail=str(exc),
            )
            error_detail = {
                "code": "direct_3d_unproduced_refunded",
                "billed": False,
                "message": f"No provider image was produced; the reservation was refunded. {exc}",
            }
        raise HTTPException(status_code=502, detail=error_detail) from exc
    except Exception as exc:
        await _refund_unproduced_direct_render(
            db,
            user,
            reservation,
            token_cost=token_cost,
            detail=f"Unexpected pre-image failure: {exc}",
        )
        logger.exception("Unexpected Direct 3D failure before a provider image was produced")
        raise HTTPException(
            status_code=502,
            detail={
                "code": "direct_3d_unproduced_refunded",
                "billed": False,
                "message": "No provider image was produced; the reservation was refunded.",
            },
        ) from exc

    try:
        processing_mode = str(result.diagnostics.get("processing_mode", "source_anchored"))
        provider_first = bool(result.diagnostics.get("provider_first", False))
        await _finalize_direct_audit(
            db,
            reservation,
            input_b64=result.audit_input_base64,
            output_b64=result.image_base64,
            status_label=(
                f"{result.outcome} provider-first {processing_mode}"
                if provider_first
                else f"{result.outcome} source-anchored"
            ),
            detail=(f"[mode={processing_mode} style={req.style}] {req.prompt}"),
        )
    except Exception as audit_exc:
        logger.warning("Failed to save Direct 3D render audit log: %s", audit_exc)

    # The user paid for every produced image: persist all results to the
    # project gallery, and keep the untouched provider image whenever a safety
    # fallback replaced it (parity with pasting the capture into an external
    # image chat). Gallery failures never block returning the render.
    try:
        strategy = result.diagnostics.get("returned_safety_strategy")
        await persist_render_to_gallery(
            db,
            req.project_id,
            SaveRenderRequest(
                image_base64=result.image_base64,
                prompt=req.prompt,
                style=req.style,
                model="gpt-image-2",
                image_quality="high",
            ),
            variant="final",
            outcome=(f"{result.outcome} · {strategy}" if strategy else str(result.outcome)),
            scene_revision_sha256=scene_revision_sha256,
        )
        if result.provider_image_base64 and strategy not in (
            None,
            "provider_full_scene",
        ):
            await persist_render_to_gallery(
                db,
                req.project_id,
                SaveRenderRequest(
                    image_base64=result.provider_image_base64,
                    prompt=req.prompt,
                    style=req.style,
                    model="gpt-image-2",
                    image_quality="high",
                ),
                variant="provider_original",
                outcome="review_required",
                scene_revision_sha256=scene_revision_sha256,
            )
    except Exception as gallery_exc:
        logger.warning("Failed to auto-save Direct 3D render to gallery: %s", gallery_exc)

    return Direct3DRenderResponse(
        image_base64=result.image_base64,
        outcome=result.outcome,
        warnings=list(result.warnings),
        capture_fingerprint=result.capture_fingerprint,
        output_fingerprint=result.output_fingerprint,
        diagnostics=result.diagnostics,
    )
