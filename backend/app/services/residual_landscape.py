"""Deterministic landscaping for the un-authored remainder of a site.

The editable planning model stores one exterior-ring ``SiteZone`` per authored
program.  Residual land is a derived result instead: it can be a MultiPolygon
and can contain holes, so it is persisted as a recipe on the site boundary
rather than being coerced into another editable zone.
"""

from __future__ import annotations

import hashlib
import json
import math
import random
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Iterable, Literal

from pyproj import CRS
from shapely.geometry import Point, Polygon, mapping
from shapely.geometry.base import BaseGeometry
from shapely.ops import unary_union

from app.services.site_engine import (
    WGS84_CRS,
    build_transformer,
    iter_polygons,
    local_metric_crs_for_polygon,
    project_geometry,
)
from app.services.public_realm_lego import public_realm_fallback_identity, public_realm_recipe_identity


@dataclass(frozen=True)
class ResidualSourceZone:
    """A physical authored polygon participating in residual subtraction."""

    zone_id: str
    kind: str
    geometry: BaseGeometry
    role: str | None = None


_REGION_ORDER = {
    "foundation_planting": 0,
    "boulevard_planting": 1,
    "perimeter_planting": 2,
    "lawn": 3,
    "low_groundcover": 4,
}
_TREE_REGION_KINDS = {"boulevard_planting", "perimeter_planting", "lawn"}
# The widest approved overhead crown plane is 7.8 x 7.2 m, rendered at 0.88
# profile size and up to 1.08 placement scale. Its half-diagonal is 5.05 m.
# Keeping every centre 5.1 m inside eligible residual geometry guarantees the
# complete textured plane stays inside the parcel and outside authored parks,
# streets, water and buildings, not merely the trunk point.
_TREE_CANOPY_CLEARANCE_M = 5.1

_COMMUNITY_BUILDING_TYPES = {"building", "residential", "development_area", "development"}
_COMMUNITY_PARK_TYPES = {"green_space", "park", "plaza", "parking"}
_COMMUNITY_STREET_TYPES = {"road", "street", "path"}


def community_3d_kind_for_source(
    zone_type: str | None,
    properties: dict[str, Any] | None,
) -> Literal["building", "park", "street"] | None:
    """Backend source-of-truth for whether an authored polygon has a 3D owner."""

    if zone_type == "site_boundary":
        return None
    props = properties or {}
    role = props.get("_plan_role")
    if role == "framework_height":
        return None
    if role == "street" or zone_type in _COMMUNITY_STREET_TYPES:
        return "street"
    if role in {"open_space", "courtyard"} or zone_type in _COMMUNITY_PARK_TYPES:
        return "park"
    if role == "building" or zone_type in _COMMUNITY_BUILDING_TYPES or bool(props.get("development_archetype_id")):
        return "building"
    return None


def _semantic_text(value: Any, *, identifier: bool = False) -> str | None:
    if value is None:
        return None
    text = " ".join(str(value).strip().split())
    if not text:
        return None
    return text.lower() if identifier else text


def _semantic_number(value: Any, *, positive: bool = False) -> int | float | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(number) or (positive and number <= 0):
        return None
    return int(number) if number.is_integer() else number


def _canonical_semantic_value(value: Any) -> Any:
    """Canonicalize JSON-like semantic metadata without URLs/provenance logic."""

    if isinstance(value, dict):
        result = {
            str(key): canonical
            for key, item in value.items()
            if (canonical := _canonical_semantic_value(item)) not in (None, "", [], {})
        }
        return result or None
    if isinstance(value, (list, tuple)):
        result = [
            canonical for item in value if (canonical := _canonical_semantic_value(item)) not in (None, "", [], {})
        ]
        return result or None
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return _semantic_number(value)
    return _semantic_text(value)


def _compact_semantic_mapping(values: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in values.items() if value not in (None, "", [], {})}


def _semantic_generation_input(properties: dict[str, Any], domain: str) -> dict[str, Any] | None:
    raw = properties.get("generation_style_input")
    if not isinstance(raw, dict):
        namespaces = properties.get("generation_style_inputs")
        raw = namespaces.get(domain) if isinstance(namespaces, dict) else None
    if not isinstance(raw, dict):
        return None

    style_profile = raw.get("styleProfile")
    if domain == "building" and isinstance(style_profile, dict):
        style_profile = {"massing": _semantic_text(style_profile.get("massing"))}
    elif not isinstance(style_profile, dict):
        style_profile = None
    downstream = raw.get("downstreamHints")
    tags = raw.get("generationTags")
    reuse_keys = downstream.get("reuseKeys") if isinstance(downstream, dict) else None
    return (
        _compact_semantic_mapping(
            {
                "archetype_id": _semantic_text(raw.get("archetypeId"), identifier=True),
                "generation_tags": sorted(
                    {
                        tag
                        for value in (tags if isinstance(tags, list) else [])
                        if (tag := _semantic_text(value, identifier=True))
                    }
                ),
                "style_profile": _canonical_semantic_value(style_profile),
                "reuse_keys": sorted(
                    {
                        key
                        for value in (reuse_keys if isinstance(reuse_keys, list) else [])
                        if (key := _semantic_text(value, identifier=True))
                    }
                ),
                "allow_setback": (
                    downstream.get("allowSetback")
                    if isinstance(downstream, dict) and isinstance(downstream.get("allowSetback"), bool)
                    else None
                ),
            }
        )
        or None
    )


def _semantic_custom_style(properties: dict[str, Any]) -> dict[str, Any] | None:
    enabled = properties.get("custom_style_enabled") is True
    if not enabled:
        return None
    attachments = properties.get("custom_style_attachments")
    stable_attachments = []
    if isinstance(attachments, list):
        for attachment in attachments:
            if not isinstance(attachment, dict) or attachment.get("kind") != "photo":
                continue
            document_id = _semantic_text(attachment.get("document_id"), identifier=True)
            if document_id:
                stable_attachments.append({"document_id": document_id, "kind": "photo"})
            if len(stable_attachments) == 3:
                break
    return _compact_semantic_mapping(
        {
            "enabled": True,
            "domain": _semantic_text(properties.get("custom_style_domain"), identifier=True),
            "prompt": _semantic_text(
                properties.get("custom_style_expanded_prompt") or properties.get("custom_style_prompt")
            ),
            "attachments": stable_attachments,
        }
    )


def _semantic_saved_layout(properties: dict[str, Any]) -> list[dict[str, Any]] | None:
    raw = properties.get("_saved_layout")
    buildings = raw.get("buildings") if isinstance(raw, dict) else None
    if not isinstance(buildings, list):
        return None
    projected = []
    numeric_fields = {
        "center_x",
        "center_y",
        "width_m",
        "depth_m",
        "rotation_deg",
        "height_m",
        "floors",
        "block_id",
        "setback_front_m",
        "setback_side_m",
    }
    text_fields = {"building_type", "building_typology", "description", "style"}
    for building in buildings:
        if not isinstance(building, dict):
            continue
        item = _compact_semantic_mapping(
            {
                **{key: _semantic_number(building.get(key)) for key in numeric_fields},
                **{
                    key: _semantic_text(
                        building.get(key),
                        identifier=key in {"building_type", "building_typology"},
                    )
                    for key in text_fields
                },
            }
        )
        if item:
            projected.append(item)
    projected.sort(key=lambda item: json.dumps(item, sort_keys=True, separators=(",", ":")))
    return projected or None


def community_3d_source_properties(
    zone_type: str | None,
    properties: dict[str, Any] | None,
) -> dict[str, Any]:
    """Project only authored semantic inputs that can change compiled 3D.

    Generated images, URLs, history, OSM/terrain caches, provenance, labels,
    timestamps and Building linkage deliberately stay out. Those lifecycle
    fields may refresh without changing the geometry the user approved.
    """

    props = properties or {}
    kind = community_3d_kind_for_source(zone_type, props)
    common = {
        "custom_style": _semantic_custom_style(props),
    }
    if kind == "building":
        profile = props.get("development_style_profile")
        profile_keys = {
            "materials",
            "massing",
            "facadeRhythm",
            "roofForm",
            "frontageType",
            "windowStyle",
            "heightTendency",
            "streetRelationship",
            "articulation",
        }
        return _compact_semantic_mapping(
            {
                **common,
                **({"native_home_plot": True} if props.get("native_home_plot") is True else {}),
                "dimensions": _compact_semantic_mapping(
                    {
                        "floors": _semantic_number(props.get("floors"), positive=True),
                        "floor_height": _semantic_number(props.get("floor_height"), positive=True),
                        "height": _semantic_number(
                            props.get("height_m") if props.get("height_m") is not None else props.get("height"),
                            positive=True,
                        ),
                        "unit_count": _semantic_number(props.get("unit_count"), positive=True),
                    }
                ),
                "identity": _compact_semantic_mapping(
                    {
                        key: _semantic_text(props.get(key), identifier=True)
                        for key in (
                            "development_type",
                            "development_aesthetic",
                            "development_aesthetic_category",
                            "development_subcategory",
                            "development_archetype_id",
                            "development_selected_variant_id",
                        )
                    }
                ),
                "generation": _semantic_generation_input(props, "building"),
                "style_profile": _canonical_semantic_value(
                    {key: profile.get(key) for key in profile_keys if isinstance(profile, dict) and key in profile}
                ),
                "appearance": _compact_semantic_mapping(
                    {
                        key: _canonical_semantic_value(props.get(key))
                        for key in (
                            "development_facade_detail",
                            "development_roof_detail",
                            "development_palette",
                            "development_variant_shade_id",
                            "facade_material",
                            "secondary_material",
                            "roof_style",
                            "roof_material",
                            "description_text",
                        )
                    }
                ),
                "saved_layout": _semantic_saved_layout(props),
            }
        )
    if kind == "park":
        return _compact_semantic_mapping(
            {
                **common,
                "green_space": _compact_semantic_mapping(
                    {
                        key.removeprefix("green_space_"): _canonical_semantic_value(props.get(key))
                        for key in (
                            "green_space_aesthetic",
                            "green_space_aesthetic_category",
                            "green_space_subcategory",
                            "green_space_archetype_id",
                            "green_space_selected_variant_id",
                            "green_space_style_profile",
                            "green_space_palette",
                            "green_space_variant_shade_id",
                        )
                    }
                ),
                "plaza": _compact_semantic_mapping(
                    {
                        key.removeprefix("plaza_"): _canonical_semantic_value(props.get(key))
                        for key in (
                            "plaza_aesthetic",
                            "plaza_aesthetic_category",
                            "plaza_subcategory",
                            "plaza_archetype_id",
                            "plaza_selected_variant_id",
                            "plaza_style_profile",
                            "plaza_palette",
                            "plaza_variant_shade_id",
                        )
                    }
                ),
                "landscape": _compact_semantic_mapping(
                    {
                        "planting_structure": _canonical_semantic_value(props.get("planting_structure")),
                        "tree_density": _semantic_number(props.get("tree_density")),
                        "park_access_points": _canonical_semantic_value(props.get("park_access_points")),
                        "neighborhood_park_layout": _semantic_text(props.get("neighborhood_park_layout"), identifier=True),
                        "paving_type": _canonical_semantic_value(props.get("paving_type")),
                        "planting_type": _canonical_semantic_value(props.get("planting_type")),
                        "water_features": _canonical_semantic_value(props.get("water_features")),
                    }
                ),
                "generation_parks": _semantic_generation_input(props, "parks"),
                "generation_plazas": _semantic_generation_input(props, "plazas"),
            }
        )
    if kind == "street":
        return _compact_semantic_mapping(
            {
                **common,
                "street": _compact_semantic_mapping(
                    {
                        key.removeprefix("road_"): (
                            _semantic_number(props.get(key), positive=True)
                            if key in {"width", "lane_count"}
                            else _canonical_semantic_value(props.get(key))
                        )
                        for key in (
                            "road_aesthetic",
                            "road_aesthetic_category",
                            "road_subcategory",
                            "road_archetype_id",
                            "road_selected_variant_id",
                            "street_role",
                            "width",
                            "lane_count",
                            "road_style_profile",
                            "road_palette",
                            "road_variant_shade_id",
                            "road_surface",
                            "surface_type",
                            "material",
                            "plan_centerline",
                        )
                    }
                ),
                "generation": _semantic_generation_input(props, "streets_paths"),
            }
        )
    return {}


def mark_community_3d_stale(
    zone: Any,
    *,
    reason: str,
    stale_at: str | None = None,
) -> bool:
    """Make a compiled zone inert while preserving its diagnostic metadata."""

    properties = dict(getattr(zone, "properties", None) or {})
    stored = properties.get("community_3d")
    if not isinstance(stored, dict) or stored.get("state") != "compiled":
        return False
    meta = dict(stored)
    meta.update(
        {
            "state": "stale",
            "stale_at": stale_at or datetime.now(timezone.utc).isoformat(),
            "stale_reason": reason,
        }
    )
    properties["community_3d"] = meta
    zone.properties = properties
    return True


async def lock_residual_landscape_project(db: Any, project_id: Any) -> None:
    """Serialize compile, source mutation and paid Direct preflight per project."""

    from sqlalchemy import select

    from app.models.models import Project

    await db.execute(select(Project.id).where(Project.id == project_id).with_for_update())


async def mark_linked_community_3d_stale(
    db: Any,
    *,
    project_id: Any,
    building_id: Any,
    reason: str,
) -> int:
    """Invalidate every compiled zone linked to a changed Building record.

    Callers acquire the project lock first. The JSON ``building_ids`` branch
    covers legacy multi-building layouts, while ``building_id`` remains the
    authoritative representation used by Community 3D.
    """

    from sqlalchemy import or_, select
    from sqlalchemy.orm.attributes import flag_modified

    from app.models.models import SiteZone

    result = await db.execute(
        select(SiteZone).where(
            SiteZone.project_id == project_id,
            or_(
                SiteZone.building_id == building_id,
                SiteZone.building_ids.contains([str(building_id)]),
            ),
        )
    )
    changed = 0
    for zone in result.scalars().all():
        if mark_community_3d_stale(zone, reason=reason):
            flag_modified(zone, "properties")
            changed += 1
    return changed


def lock_residual_landscape_project_sync(session: Any, project_id: Any) -> None:
    """Synchronous worker twin of :func:`lock_residual_landscape_project`."""

    from sqlalchemy import select

    from app.models.models import Project

    session.execute(select(Project.id).where(Project.id == project_id).with_for_update())


def mark_linked_community_3d_stale_sync(
    session: Any,
    *,
    project_id: Any,
    building_id: Any,
    reason: str,
) -> int:
    """Synchronous worker twin of :func:`mark_linked_community_3d_stale`."""

    from sqlalchemy import or_, select
    from sqlalchemy.orm.attributes import flag_modified

    from app.models.models import SiteZone

    result = session.execute(
        select(SiteZone).where(
            SiteZone.project_id == project_id,
            or_(
                SiteZone.building_id == building_id,
                SiteZone.building_ids.contains([str(building_id)]),
            ),
        )
    )
    changed = 0
    for zone in result.scalars().all():
        if mark_community_3d_stale(zone, reason=reason):
            flag_modified(zone, "properties")
            changed += 1
    return changed


def mark_residual_landscape_stale(
    boundary: Any,
    *,
    changed_zone_id: str,
    reason: str,
    stale_at: str | None = None,
) -> bool:
    """Preserve diagnostics but make a compiled boundary recipe inert.

    This small synchronous mutation is shared by async API CRUD and the sync
    master-plan worker so every geometry-producing workflow uses one state
    transition. The caller remains responsible for SQLAlchemy ``flag_modified``.
    """

    properties = dict(getattr(boundary, "properties", None) or {})
    stored = properties.get("community_3d_landscape")
    if not isinstance(stored, dict) or stored.get("state") != "compiled":
        return False
    recipe = dict(stored)
    recipe.update(
        {
            "state": "stale",
            "stale_at": stale_at or datetime.now(timezone.utc).isoformat(),
            "stale_reason": reason,
            "changed_zone_id": str(changed_zone_id),
        }
    )
    properties["community_3d_landscape"] = recipe
    boundary.properties = properties
    return True


def _repair_polygonal(geometry: BaseGeometry | None) -> BaseGeometry:
    if geometry is None or geometry.is_empty:
        return Polygon()
    repaired = geometry
    if not geometry.is_valid:
        # ``buffer(0)`` is a useful last-resort compatibility repair, but it
        # can silently keep only one lobe of a self-intersecting bow-tie. Use
        # GEOS MakeValid when available so every polygonal part continues to
        # occupy land in the residual subtraction.
        try:
            from shapely import make_valid
        except (ImportError, AttributeError):  # pragma: no cover - Shapely < 2
            try:
                from shapely.validation import make_valid
            except (ImportError, AttributeError):  # pragma: no cover - old GEOS
                make_valid = None
        if make_valid is not None:
            try:
                repaired = make_valid(geometry)
            except (TypeError, ValueError):  # pragma: no cover - defensive GEOS fallback
                repaired = geometry.buffer(0)
        else:
            repaired = geometry.buffer(0)
    polygons = [polygon for polygon in iter_polygons(repaired) if not polygon.is_empty]
    if not polygons:
        return Polygon()
    return polygons[0] if len(polygons) == 1 else unary_union(polygons)


def _metric_crs_label(crs: CRS) -> str:
    authority = crs.to_authority()
    return f"{authority[0]}:{authority[1]}" if authority else crs.to_string()


def _normalized_wkb(geometry: BaseGeometry) -> str:
    try:
        from shapely import normalize

        return normalize(geometry).wkb_hex
    except (ImportError, AttributeError):  # pragma: no cover - Shapely < 2 fallback
        return geometry.wkb_hex


def community_3d_source_hash(
    zone_type: str | None,
    geometry: BaseGeometry,
    properties: dict[str, Any] | None,
) -> str:
    """Fingerprint the exact authored zone state that owns compiled 3D.

    The hash is persisted with ``community_3d`` and recomputed under the
    project lock before any paid Direct render. This independently catches
    stale metadata even if a future mutation path forgets to mark the zone.
    """

    repaired = _repair_polygonal(geometry)
    try:
        from shapely import set_precision

        repaired = _repair_polygonal(set_precision(repaired, grid_size=1e-7))
    except (ImportError, AttributeError):  # pragma: no cover - Shapely < 2 fallback
        pass
    payload = {
        "contract_version": 2,
        "zone_type": _semantic_text(zone_type, identifier=True) or "",
        "kind": community_3d_kind_for_source(zone_type, properties),
        "geometry": _normalized_wkb(repaired),
        "plan_role": _semantic_text(
            (properties or {}).get("_plan_role"),
            identifier=True,
        ),
        "design": community_3d_source_properties(zone_type, properties),
    }
    return hashlib.sha256(
        json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            default=str,
        ).encode("utf-8")
    ).hexdigest()


def _representation_geometry_identity(value: Any) -> str | None:
    """Return a stable WKB identity for a Building footprint-like value."""

    if value is None:
        return None
    geometry: BaseGeometry
    if isinstance(value, BaseGeometry):
        geometry = value
    else:
        try:
            from geoalchemy2.shape import to_shape

            geometry = to_shape(value)
        except (AssertionError, TypeError, ValueError, AttributeError):
            try:
                from shapely import wkt

                raw = str(value)
                if ";" in raw and raw.upper().startswith("SRID="):
                    raw = raw.split(";", 1)[1]
                geometry = wkt.loads(raw)
            except Exception:
                return None

    repaired = _repair_polygonal(geometry)
    if repaired.is_empty:
        return None
    try:
        from shapely import set_precision

        repaired = _repair_polygonal(set_precision(repaired, grid_size=1e-7))
    except (ImportError, AttributeError):  # pragma: no cover - Shapely < 2 fallback
        pass
    return _normalized_wkb(repaired)


def community_3d_representation_hash(
    *,
    kind: Literal["building", "park", "street"],
    generator: str,
    source_hash: str,
    building: Any | None = None,
    public_realm_recipe: dict[str, Any] | None = None,
    public_realm_fallback: dict[str, Any] | None = None,
) -> str | None:
    """Fingerprint the exact persisted representation mounted by the globe.

    ``source_hash`` binds deterministic park/street kits to their authored
    inputs. Buildings additionally bind the linked record, footprint,
    placement dimensions and the generator-specific content that the globe
    actually consumes. Returning ``None`` is fail-closed: an incomplete model
    cannot be claimed by a paid Direct capture.
    """

    payload: dict[str, Any] = {
        "contract_version": 1,
        "kind": kind,
        "generator": _semantic_text(generator, identifier=True) or "",
        "source_hash": source_hash.lower(),
    }
    if kind == "building":
        if building is None or getattr(building, "id", None) is None:
            return None
        footprint = _representation_geometry_identity(getattr(building, "footprint", None))
        if footprint is None:
            return None
        specifications = getattr(building, "specifications", None) or {}
        if not isinstance(specifications, dict):
            return None

        if generator == "lego_assembly":
            representation = specifications.get("legoAssembly")
            if not isinstance(representation, dict):
                return None
        elif generator == "planned_massing":
            representation = specifications.get("plannedMassing")
            if not isinstance(representation, dict):
                return None
        elif generator == "meshy":
            model_url = getattr(building, "model_url", None)
            lod_urls = getattr(building, "lod_urls", None)
            if not model_url and not (isinstance(lod_urls, dict) and lod_urls.get("0")):
                return None
            representation = {
                "model_url": _semantic_text(model_url),
                "lod_urls": _canonical_semantic_value(lod_urls),
            }
        else:
            return None

        payload["building"] = {
            "id": str(building.id),
            # Generated-model massing LODs use these as their visible color
            # seed when a detailed GLB is outside the camera budget or cannot
            # be loaded, so they are part of the captured representation.
            "name": _semantic_text(getattr(building, "name", None)),
            "architectural_style": _semantic_text(
                getattr(building, "architectural_style", None),
                identifier=True,
            ),
            "footprint": footprint,
            "height_meters": _semantic_number(getattr(building, "height_meters", None)),
            "floor_count": _semantic_number(getattr(building, "floor_count", None)),
            "floor_height_meters": _semantic_number(getattr(building, "floor_height_meters", None)),
            "rotation_degrees": _semantic_number(getattr(building, "rotation_degrees", None)),
            "representation": _canonical_semantic_value(representation),
        }
    elif public_realm_recipe is not None:
        # V1 Public Realm LEGO is a stronger contract than the legacy
        # deterministic park/street marker. Bind the exact canonical recipe,
        # its self-hash and the live executable capability revision. A stale
        # catalog or edited payload fails closed in Direct preflight.
        identity = public_realm_recipe_identity(public_realm_recipe)
        if identity is None:
            return None
        canonical_recipe = identity["recipe"]
        if canonical_recipe.get("kind") != kind or canonical_recipe.get("generator") != generator:
            return None
        payload["public_realm_lego"] = identity
    elif public_realm_fallback is not None:
        identity = public_realm_fallback_identity(public_realm_fallback)
        if identity is None:
            return None
        if identity.get("kind") != kind or identity.get("generator") != generator:
            return None
        payload["public_realm_fallback"] = identity

    return hashlib.sha256(
        json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            default=str,
        ).encode("utf-8")
    ).hexdigest()


def residual_landscape_source_hash(
    boundary: BaseGeometry,
    zones: Iterable[ResidualSourceZone],
) -> str:
    """Canonical identity of the parcel remainder's geometry inputs."""

    payload = {
        "schema_version": 1,
        "boundary": _normalized_wkb(boundary),
        "zones": sorted(
            (
                {
                    "id": zone.zone_id,
                    "kind": zone.kind,
                    "role": zone.role,
                    "geometry": _normalized_wkb(_repair_polygonal(zone.geometry)),
                }
                for zone in zones
                if zone.role != "framework_height"
            ),
            key=lambda item: (item["id"], item["kind"], item["geometry"]),
        ),
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def _geojson(geometry: BaseGeometry, to_wgs84) -> dict[str, Any]:
    # Revalidate after inverse projection: a clipped band that meets the site
    # shell can acquire a sub-nanometre self-touch during the CRS transform.
    # Keep the resulting double precision intact. Decimal rounding can turn
    # that harmless separation back into an invalid shell/hole contact.
    projected = _repair_polygonal(project_geometry(geometry, to_wgs84))
    return json.loads(json.dumps(mapping(projected)))


def _minimum_width(polygon: Polygon) -> float:
    rectangle = polygon.minimum_rotated_rectangle
    coordinates = list(rectangle.exterior.coords)
    if len(coordinates) < 4:
        return 0.0
    sides = [
        math.hypot(
            coordinates[index + 1][0] - coordinates[index][0],
            coordinates[index + 1][1] - coordinates[index][1],
        )
        for index in range(4)
    ]
    return min(sides) if sides else 0.0


def _sorted_polygons(geometry: BaseGeometry) -> list[Polygon]:
    return sorted(
        iter_polygons(_repair_polygonal(geometry)),
        key=lambda polygon: (
            -round(float(polygon.area), 6),
            tuple(round(value, 6) for value in polygon.bounds),
            _normalized_wkb(polygon),
        ),
    )


def _classify_residual(
    residual: BaseGeometry,
    boundary: BaseGeometry,
    buildings: BaseGeometry,
    streets: BaseGeometry,
) -> list[tuple[str, Polygon]]:
    """Partition every square metre of residual land into one landscape class."""

    remaining = _repair_polygonal(residual)
    classified: list[tuple[str, Polygon]] = []

    bands = [
        (
            "foundation_planting",
            (
                _repair_polygonal(buildings.buffer(2.25, cap_style=2, join_style=2))
                if not buildings.is_empty
                else Polygon()
            ),
        ),
        (
            "boulevard_planting",
            _repair_polygonal(streets.buffer(3.5, cap_style=2, join_style=2)) if not streets.is_empty else Polygon(),
        ),
        (
            "perimeter_planting",
            _repair_polygonal(boundary.boundary.buffer(3.0).intersection(boundary)),
        ),
    ]

    for kind, band in bands:
        if remaining.is_empty or band.is_empty:
            continue
        selected = _repair_polygonal(remaining.intersection(band))
        for polygon in _sorted_polygons(selected):
            classified.append((kind, polygon))
        remaining = _repair_polygonal(remaining.difference(selected))

    for polygon in _sorted_polygons(remaining):
        kind = "lawn" if polygon.area >= 220.0 and _minimum_width(polygon) >= 7.5 else "low_groundcover"
        classified.append((kind, polygon))

    classified.sort(
        key=lambda item: (
            _REGION_ORDER[item[0]],
            -round(float(item[1].area), 6),
            tuple(round(value, 6) for value in item[1].bounds),
        )
    )
    return classified


def _tree_placements(
    regions: list[tuple[str, Polygon]],
    boundary: BaseGeometry,
    buildings: BaseGeometry,
    streets: BaseGeometry,
    *,
    seed_hex: str,
    to_wgs84,
) -> list[dict[str, Any]]:
    candidate_polygons = [polygon for kind, polygon in regions if kind in _TREE_REGION_KINDS]
    if not candidate_polygons:
        return []

    candidates = _repair_polygonal(unary_union(candidate_polygons))
    safe = _repair_polygonal(candidates.buffer(-_TREE_CANOPY_CLEARANCE_M))
    safe = safe.intersection(boundary.buffer(-_TREE_CANOPY_CLEARANCE_M))
    if not buildings.is_empty:
        safe = safe.difference(buildings.buffer(4.5, cap_style=2, join_style=2))
    if not streets.is_empty:
        safe = safe.difference(streets.buffer(2.25, cap_style=2, join_style=2))
    safe = _repair_polygonal(safe)
    if safe.is_empty:
        return []

    # One canopy per ~260 m² is intentionally restrained. Authored parks own
    # their denser tree recipes, while residual planting should frame the plan.
    target_count = min(48, max(0, int(safe.area / 260.0)))
    if (
        target_count == 0
        and safe.area >= 120.0
        and _minimum_width(max(_sorted_polygons(safe), key=lambda p: p.area)) >= 7.5
    ):
        target_count = 1
    if target_count == 0:
        return []

    rng = random.Random(int(seed_hex[:16], 16))
    min_x, min_y, max_x, max_y = safe.bounds
    spacing = 9.5
    origin_x = min_x + rng.random() * spacing
    origin_y = min_y + rng.random() * spacing
    points: list[Point] = []
    grid: list[Point] = []
    y = origin_y
    while y <= max_y and len(grid) < 5000:
        x = origin_x
        while x <= max_x and len(grid) < 5000:
            jitter_x = (rng.random() - 0.5) * spacing * 0.46
            jitter_y = (rng.random() - 0.5) * spacing * 0.46
            grid.append(Point(x + jitter_x, y + jitter_y))
            x += spacing
        y += spacing
    rng.shuffle(grid)

    for point in grid:
        if len(points) >= target_count:
            break
        if not safe.covers(point):
            continue
        if point.distance(safe.boundary) < 0.1:
            continue
        if any(point.distance(existing) < spacing for existing in points):
            continue
        points.append(point)

    points.sort(key=lambda point: (round(point.y, 5), round(point.x, 5)))
    placements: list[dict[str, Any]] = []
    for index, point in enumerate(points, start=1):
        wgs_point = project_geometry(point, to_wgs84)
        placements.append(
            {
                "id": f"tree-{index:04d}",
                "kind": "tree",
                "lng": round(float(wgs_point.x), 8),
                "lat": round(float(wgs_point.y), 8),
                "yaw_rad": round(rng.random() * math.tau, 5),
                "scale": round(0.84 + rng.random() * 0.24, 3),
            }
        )
    return placements


def build_residual_landscape_recipe(
    boundary: BaseGeometry,
    authored_zones: Iterable[ResidualSourceZone],
    *,
    boundary_id: str,
    compiled_at: str,
) -> dict[str, Any]:
    """Build the site-boundary remainder and its deterministic landscape recipe."""

    boundary_wgs84 = _repair_polygonal(boundary)
    if boundary_wgs84.is_empty:
        raise ValueError("Site boundary does not contain usable polygon geometry")

    zones = [zone for zone in authored_zones if zone.role != "framework_height"]
    source_hash = residual_landscape_source_hash(boundary_wgs84, zones)
    metric_crs = local_metric_crs_for_polygon(boundary_wgs84)
    to_metric = build_transformer(WGS84_CRS, metric_crs)
    to_wgs84 = build_transformer(metric_crs, WGS84_CRS)
    boundary_metric = _repair_polygonal(project_geometry(boundary_wgs84, to_metric))

    occupied_by_kind: dict[str, list[BaseGeometry]] = {}
    occupied: list[BaseGeometry] = []
    for zone in zones:
        geometry = _repair_polygonal(project_geometry(_repair_polygonal(zone.geometry), to_metric))
        if geometry.is_empty:
            continue
        clipped = _repair_polygonal(geometry.intersection(boundary_metric))
        if clipped.is_empty:
            continue
        occupied.append(clipped)
        occupied_by_kind.setdefault(zone.kind, []).append(clipped)

    occupied_union = _repair_polygonal(unary_union(occupied)) if occupied else Polygon()
    residual = _repair_polygonal(boundary_metric.difference(occupied_union))
    buildings = (
        _repair_polygonal(unary_union(occupied_by_kind.get("building", [])))
        if occupied_by_kind.get("building")
        else Polygon()
    )
    streets = (
        _repair_polygonal(unary_union(occupied_by_kind.get("street", [])))
        if occupied_by_kind.get("street")
        else Polygon()
    )

    classified = _classify_residual(residual, boundary_metric, buildings, streets)
    kind_counts: dict[str, int] = {}
    regions: list[dict[str, Any]] = []
    for kind, polygon in classified:
        kind_counts[kind] = kind_counts.get(kind, 0) + 1
        regions.append(
            {
                "id": f"{kind.replace('_planting', '')}-{kind_counts[kind]:04d}",
                "kind": kind,
                "area_sqm": round(float(polygon.area), 2),
                "minimum_width_m": round(_minimum_width(polygon), 2),
                "geometry": _geojson(polygon, to_wgs84),
            }
        )

    placements = _tree_placements(
        classified,
        boundary_metric,
        buildings,
        streets,
        seed_hex=source_hash,
        to_wgs84=to_wgs84,
    )
    return {
        "schema_version": 1,
        "state": "compiled",
        "generator": "residual_landscape",
        "boundary_id": boundary_id,
        "compiled_at": compiled_at,
        "source_hash": source_hash,
        "metric_crs": _metric_crs_label(metric_crs),
        "area_sqm": round(float(residual.area), 2),
        "occupied_area_sqm": round(float(occupied_union.area), 2),
        "geometry": _geojson(residual, to_wgs84),
        "regions": regions,
        "placements": placements,
    }


def derive_site_boundary_from_authored_zones(
    geometries: Iterable[BaseGeometry],
) -> BaseGeometry:
    """Infer a conservative editable boundary for legacy boundary-less plans.

    The hull is computed in metres, not longitude/latitude degrees. It adds no
    arbitrary setback: the outermost authored polygons define the inferred
    parcel, while their interstitial gaps become the residual landscape.
    """

    polygonal = [repaired for geometry in geometries if not (repaired := _repair_polygonal(geometry)).is_empty]
    if len(polygonal) < 2:
        raise ValueError("At least two authored polygons are required to infer a site boundary")
    union_wgs84 = _repair_polygonal(unary_union(polygonal))
    metric_crs = local_metric_crs_for_polygon(union_wgs84)
    to_metric = build_transformer(WGS84_CRS, metric_crs)
    to_wgs84 = build_transformer(metric_crs, WGS84_CRS)
    union_metric = _repair_polygonal(project_geometry(union_wgs84, to_metric))
    hull_metric = _repair_polygonal(union_metric.convex_hull)
    if hull_metric.is_empty or hull_metric.area <= 0:
        raise ValueError("Authored polygons do not define a usable site boundary")
    return _repair_polygonal(project_geometry(hull_metric, to_wgs84))
