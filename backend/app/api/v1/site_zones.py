"""
Site Zone management API endpoints.
"""

import logging
import math
import re
import uuid
from datetime import datetime, timezone

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from geoalchemy2.elements import WKTElement
from geoalchemy2.functions import ST_Intersects
from geoalchemy2.shape import to_shape
from shapely.geometry import Polygon
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified

from app.core.database import get_db
from app.core.security import is_admin_or_above, require_auth
from app.models.models import Building, Project, ProjectShare, SiteZone, User
from app.schemas.schemas import (
    ApplyLayoutRequest,
    BuildingResponse,
    LayoutPreviewResponse,
    OSMContextResponse,
    RegenerateLayoutRequest,
    SiteLayoutResponse,
    SiteLayoutOption,
    SiteZoneCreate,
    SiteZoneResponse,
    SiteZoneUpdate,
)
from app.api.v1.buildings import _building_to_response
from app.services.layout_planner import LayoutPlanner
from app.services.osm_context import OSMContextFetcher

logger = logging.getLogger(__name__)

router = APIRouter()


def _safe_int(value, default: int) -> int:
    """Best-effort integer parsing with fallback."""
    try:
        if value is None:
            return default
        if isinstance(value, bool):
            return int(value)
        if isinstance(value, str):
            stripped = value.strip()
            if not stripped:
                return default
            return int(float(stripped))
        return int(value)
    except (TypeError, ValueError):
        return default


def _normalize_building_ids(raw_ids) -> list[uuid.UUID]:
    """Normalize zone building_ids payloads into valid UUID objects."""
    if raw_ids is None:
        return []

    candidates = raw_ids if isinstance(raw_ids, list) else [raw_ids]
    normalized: list[uuid.UUID] = []
    for item in candidates:
        try:
            normalized.append(item if isinstance(item, uuid.UUID) else uuid.UUID(str(item)))
        except (TypeError, ValueError, AttributeError):
            logger.warning("Skipping invalid building id in zone payload: %r", item)
    return normalized


def _safe_optional_int(value) -> int | None:
    """Best-effort optional integer parsing."""
    if value is None:
        return None
    try:
        if isinstance(value, bool):
            return int(value)
        if isinstance(value, str):
            stripped = value.strip()
            if not stripped:
                return None
            return int(float(stripped))
        return int(value)
    except (TypeError, ValueError):
        return None


def _safe_optional_float(value) -> float | None:
    """Best-effort optional float parsing."""
    if value is None:
        return None
    try:
        if isinstance(value, bool):
            return float(int(value))
        if isinstance(value, str):
            stripped = value.strip()
            if not stripped:
                return None
            return float(stripped)
        return float(value)
    except (TypeError, ValueError):
        return None

def _compact_spec_values(values: dict) -> dict:
    """Drop None/empty-string values while preserving False/0/list/dict payloads."""
    return {
        key: value
        for key, value in values.items()
        if value is not None and (not isinstance(value, str) or value.strip() != "")
    }


STYLE_METADATA_KEYS = (
    "development_subcategory",
    "development_aesthetic_category",
    "development_selected_reference",
    "development_archetype_id",
    "development_archetype_label",
    "development_archetype_image",
    "development_archetype_images",
    "development_style_profile",
    "generation_style_input",
)


def _extract_building_style_metadata(props: dict) -> dict:
    """Extract structured building style metadata from zone properties."""
    return _compact_spec_values({key: props.get(key) for key in STYLE_METADATA_KEYS})


def _base_building_specifications(props: dict, description_text: Optional[str] = None) -> dict:
    """Create a consistent baseline specifications payload for building records."""
    specs = {
        "development_type": props.get("development_type"),
        "development_aesthetic": props.get("development_aesthetic"),
        "development_aesthetic_category": props.get("development_aesthetic_category"),
        "description_text": description_text if description_text is not None else props.get("description_text"),
        "facade_material": props.get("facade_material"),
        "roof_style": props.get("roof_style"),
    }
    specs.update(_extract_building_style_metadata(props))
    return _compact_spec_values(specs)


def _build_neighbor_list(zones: list) -> list[dict]:
    """Build a neighbor list with geometry for AI layout context.

    Extracts coordinates, dimensions, and properties for each zone
    so the AI can understand spatial relationships.
    """
    neighbors = []
    for z in zones:
        zp = z.properties or {}
        coords = []
        center = None
        width_m = 0
        depth_m = 0
        try:
            shape = to_shape(z.geometry)
            coords = [[c[0], c[1]] for c in shape.exterior.coords[:-1]]
            centroid = shape.centroid
            center = [centroid.x, centroid.y]
            bounds = shape.bounds
            center_lat = centroid.y
            m_lon = 111320 * abs(math.cos(math.radians(center_lat)))
            width_m = abs(bounds[2] - bounds[0]) * m_lon
            depth_m = abs(bounds[3] - bounds[1]) * 111320
        except Exception:
            pass

        neighbors.append({
            "zone_type": z.zone_type,
            "name": z.name,
            "properties": zp,
            "coordinates": coords,
            "center": center,
            "width_m": round(width_m, 1),
            "depth_m": round(depth_m, 1),
        })
    return neighbors


MAX_PREVIEW_HISTORY = 20


async def _append_preview_history(
    zone: "SiteZone",
    db: AsyncSession,
    *,
    image_url: str,
    label: str,
    strategy: str,
    preview_type: str,
    option_index: int = 0,
    layout_data: Optional[dict] = None,
) -> None:
    """Append a preview entry to zone.properties._preview_history (capped at 20)."""
    props = zone.properties or {}
    history: list = props.get("_preview_history", [])
    entry = {
        "image_url": image_url,
        "label": label,
        "strategy": strategy,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "preview_type": preview_type,
        "option_index": option_index,
    }
    if layout_data is not None:
        entry["layout_data"] = layout_data
    history.append(entry)
    if len(history) > MAX_PREVIEW_HISTORY:
        history = history[-MAX_PREVIEW_HISTORY:]
    props["_preview_history"] = history
    zone.properties = props
    flag_modified(zone, "properties")
    db.add(zone)
    await db.flush()


def _zone_to_response(zone: SiteZone) -> dict:
    """Convert a SiteZone ORM object to a response dict with coordinates."""
    coords: list[list[float]] = []
    if zone.geometry is not None:
        try:
            shape = to_shape(zone.geometry)
            coords = [[c[0], c[1]] for c in shape.exterior.coords[:-1]]  # Exclude closing point
        except Exception:
            pass

    return {
        "id": zone.id,
        "project_id": zone.project_id,
        "name": zone.name,
        "zone_type": zone.zone_type,
        "coordinates": coords,
        "color": zone.color,
        "properties": zone.properties,
        "sort_order": zone.sort_order,
        "building_id": zone.building_id,
        "building_ids": _normalize_building_ids(zone.building_ids) or None,
        "created_at": zone.created_at,
        "updated_at": zone.updated_at,
    }


@router.get("/projects/{project_id}/zones", response_model=list[SiteZoneResponse])
async def list_zones(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """List all site zones in a project, ordered by sort_order."""
    result = await db.execute(
        select(SiteZone)
        .where(SiteZone.project_id == project_id)
        .order_by(SiteZone.sort_order, SiteZone.created_at)
    )
    zones = result.scalars().all()
    return [_zone_to_response(z) for z in zones]


@router.post(
    "/projects/{project_id}/zones",
    response_model=SiteZoneResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_zone(
    project_id: uuid.UUID,
    zone_in: SiteZoneCreate,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Create a site zone in a project."""
    # Verify project exists
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Check editor permission (admins bypass)
    if project.owner_id != user.id and not is_admin_or_above(user):
        share_result = await db.execute(
            select(ProjectShare).where(
                ProjectShare.project_id == project_id,
                (ProjectShare.user_id == user.id) | (ProjectShare.email == user.email),
                ProjectShare.permission == "editor",
            )
        )
        if not share_result.scalar_one_or_none():
            raise HTTPException(status_code=403, detail="Not authorized to add zones to this project")

    # Convert coordinates to WKT POLYGON
    coords = zone_in.coordinates
    # De-duplicate nearly-identical consecutive vertices
    unique_coords: list[list[float]] = []
    for c in coords:
        if not unique_coords or abs(c[0] - unique_coords[-1][0]) > 1e-7 or abs(c[1] - unique_coords[-1][1]) > 1e-7:
            unique_coords.append(c)
    coords = unique_coords
    if len(coords) < 3:
        raise HTTPException(status_code=400, detail="Polygon must have at least 3 unique vertices")
    # Close the polygon if not already closed
    if coords[0] != coords[-1]:
        coords.append(coords[0])
    coords_str = ", ".join(f"{c[0]} {c[1]}" for c in coords)

    zone = SiteZone(
        project_id=project_id,
        name=zone_in.name,
        zone_type=zone_in.zone_type,
        geometry=WKTElement(f"POLYGON(({coords_str}))", srid=4326),
        color=zone_in.color,
        properties=zone_in.properties,
        sort_order=zone_in.sort_order,
    )

    db.add(zone)
    await db.flush()
    await db.refresh(zone)

    # Auto-fetch OSM context when creating a site_boundary zone
    if zone_in.zone_type == "site_boundary":
        try:
            shape = to_shape(zone.geometry)
            fetcher = OSMContextFetcher()
            osm_context = await fetcher.fetch(shape)
            updated_props = dict(zone.properties or {})
            updated_props["_osm_context"] = osm_context
            zone.properties = updated_props
            await db.flush()
            await db.refresh(zone)
            logger.info(
                "Auto-fetched OSM context for site_boundary %s: %d buildings, %d roads",
                zone.id,
                len(osm_context.get("buildings", [])),
                len(osm_context.get("roads", [])),
            )
        except Exception as e:
            logger.warning("Failed to auto-fetch OSM context for zone %s: %s", zone.id, e)

    return _zone_to_response(zone)


# =============================================================================
# OSM Context Endpoints
# =============================================================================

@router.post("/{zone_id}/fetch-context", response_model=OSMContextResponse)
async def fetch_context(
    zone_id: uuid.UUID,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Fetch OSM features for a site_boundary zone and store in properties."""
    result = await db.execute(select(SiteZone).where(SiteZone.id == zone_id))
    zone = result.scalar_one_or_none()
    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")

    if zone.zone_type != "site_boundary":
        raise HTTPException(status_code=400, detail="Only site_boundary zones support context fetching")

    shape = to_shape(zone.geometry)
    fetcher = OSMContextFetcher()
    osm_context = await fetcher.fetch(shape)

    # Store in zone properties
    updated_props = dict(zone.properties or {})
    updated_props["_osm_context"] = osm_context
    zone.properties = updated_props
    await db.flush()
    await db.refresh(zone)

    # Convert to response schema
    from app.schemas.schemas import OSMContextBuilding, OSMContextRoad, OSMContextFeature
    return OSMContextResponse(
        buildings=[OSMContextBuilding(
            osm_id=b["osm_id"],
            coordinates=b["coordinates"],
            height_m=b.get("height_m"),
            building_type=b.get("building_type", "yes"),
            name=b.get("name"),
            levels=b.get("levels"),
        ) for b in osm_context.get("buildings", [])],
        roads=[OSMContextRoad(
            osm_id=r["osm_id"],
            coordinates=r["coordinates"],
            width_m=r.get("width_m", 6.0),
            road_type=r.get("road_type", "residential"),
            name=r.get("name"),
            surface=r.get("surface"),
            lanes=r.get("lanes"),
        ) for r in osm_context.get("roads", [])],
        water=[OSMContextFeature(
            osm_id=w["osm_id"],
            coordinates=w["coordinates"],
            feature_type=w.get("water_type", "water"),
            name=w.get("name"),
        ) for w in osm_context.get("water", [])],
        parks=[OSMContextFeature(
            osm_id=p["osm_id"],
            coordinates=p["coordinates"],
            feature_type=p.get("park_type", "park"),
            name=p.get("name"),
        ) for p in osm_context.get("parks", [])],
        fetched_at=osm_context.get("fetched_at", ""),
        buffer_m=osm_context.get("buffer_m", 50),
    )


@router.put("/{zone_id}", response_model=SiteZoneResponse)
async def update_zone(
    zone_id: uuid.UUID,
    zone_in: SiteZoneUpdate,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Update a site zone's properties or geometry."""
    result = await db.execute(select(SiteZone).where(SiteZone.id == zone_id))
    zone = result.scalar_one_or_none()
    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")

    # Check editor permission on parent project (admins bypass)
    proj_result = await db.execute(select(Project).where(Project.id == zone.project_id))
    project = proj_result.scalar_one_or_none()
    if project.owner_id != user.id and not is_admin_or_above(user):
        share_result = await db.execute(
            select(ProjectShare).where(
                ProjectShare.project_id == zone.project_id,
                (ProjectShare.user_id == user.id) | (ProjectShare.email == user.email),
                ProjectShare.permission == "editor",
            )
        )
        if not share_result.scalar_one_or_none():
            raise HTTPException(status_code=403, detail="Not authorized to edit zones in this project")

    update_data = zone_in.model_dump(exclude_unset=True)

    # Handle coordinates → geometry conversion
    if "coordinates" in update_data:
        coords = update_data.pop("coordinates")
        if coords and len(coords) >= 3:
            if coords[0] != coords[-1]:
                coords.append(coords[0])
            coords_str = ", ".join(f"{c[0]} {c[1]}" for c in coords)
            zone.geometry = WKTElement(f"POLYGON(({coords_str}))", srid=4326)

    for field, value in update_data.items():
        setattr(zone, field, value)

    await db.flush()

    # Propagate relevant property changes to linked building(s)
    if "properties" in update_data:
        new_props = update_data["properties"] or {}
        bids = zone.building_ids or ([str(zone.building_id)] if zone.building_id else [])
        if bids:
            for bid_str in bids:
                try:
                    b_result = await db.execute(select(Building).where(Building.id == uuid.UUID(str(bid_str))))
                    b = b_result.scalar_one_or_none()
                    if b:
                        if "height" in new_props and new_props["height"] is not None:
                            b.height_meters = new_props["height"]
                        if "floors" in new_props and new_props["floors"] is not None:
                            b.floor_count = new_props["floors"]
                        if "floor_height" in new_props and new_props["floor_height"] is not None:
                            b.floor_height_meters = new_props["floor_height"]
                        if "roof_style" in new_props and new_props["roof_style"] is not None:
                            b.roof_type = new_props["roof_style"]
                except Exception:
                    pass
            await db.flush()

    await db.refresh(zone)
    return _zone_to_response(zone)


@router.delete("/{zone_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_zone(
    zone_id: uuid.UUID,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Delete a site zone."""
    result = await db.execute(select(SiteZone).where(SiteZone.id == zone_id))
    zone = result.scalar_one_or_none()
    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")

    # Check editor permission on parent project (admins bypass)
    proj_result = await db.execute(select(Project).where(Project.id == zone.project_id))
    project = proj_result.scalar_one_or_none()
    if project.owner_id != user.id and not is_admin_or_above(user):
        share_result = await db.execute(
            select(ProjectShare).where(
                ProjectShare.project_id == zone.project_id,
                (ProjectShare.user_id == user.id) | (ProjectShare.email == user.email),
                ProjectShare.permission == "editor",
            )
        )
        if not share_result.scalar_one_or_none():
            raise HTTPException(status_code=403, detail="Not authorized to delete zones in this project")

    await db.delete(zone)


def _parse_unit_count_from_text(text: str) -> int:
    """Parse unit count from description text like '10 homes', '5 houses', '20 units'."""
    if not text:
        return 0
    match = re.search(r'(\d+)\s*(homes?|houses?|units?|buildings?|townhomes?|condos?)', text, re.I)
    if match:
        return int(match.group(1))
    return 0


def _resolve_unit_count(zone: SiteZone) -> int:
    """Determine unit count from zone properties and description text, taking the max.

    Uses zone-type-aware defaults: development_area defaults to 10 (matching
    the frontend) since subdivisions are inherently multi-unit.
    """
    props = zone.properties or {}
    # Zone-type-aware default: development_area is inherently multi-unit
    default = 10 if zone.zone_type == "development_area" else 1
    prop_count = _safe_int(props.get("unit_count"), default)
    desc = props.get("description_text", "") or ""
    parsed_count = _parse_unit_count_from_text(desc)
    return max(prop_count, parsed_count, 1)


def _is_orientation_window_zone(zone: SiteZone, unit_count: int) -> bool:
    """Return True when this zone should expose orientation-window options."""
    if unit_count < 6:
        return False
    props = zone.properties or {}
    zone_type = str(zone.zone_type or "").lower()
    dev_type = str(props.get("development_type", zone_type) or zone_type).lower()
    return (
        zone_type in ("residential", "development_area")
        or dev_type in ("residential", "mixed_use", "park_plaza")
    )


def _estimate_zone_area_m2(zone: SiteZone) -> float:
    """Estimate zone area from geometry bounds (meters squared)."""
    try:
        shape = to_shape(zone.geometry)
        minx, miny, maxx, maxy = shape.bounds
        center_lat = (miny + maxy) / 2
        meters_per_deg_lon = METERS_PER_DEG_LAT * abs(math.cos(math.radians(center_lat)))
        width_m = abs(maxx - minx) * meters_per_deg_lon
        depth_m = abs(maxy - miny) * METERS_PER_DEG_LAT
        return width_m * depth_m
    except Exception:
        return 0.0


def _resolve_layout_option_count(zone: SiteZone, unit_count: int) -> int:
    """Choose number of preview options based on zone scale/type."""
    if not _is_orientation_window_zone(zone, unit_count):
        return 3

    area_ha = _estimate_zone_area_m2(zone) / 10000.0
    if unit_count >= 24 or area_ha >= 4.0:
        return 8
    if unit_count >= 12 or area_ha >= 2.0:
        return 6
    return 5


def compute_unit_positions(zone_geometry, unit_count: int):
    """Compute grid positions for N units within zone bounding box.

    Returns list of (cx, cy, cell_w, cell_h) tuples — center coordinates
    and cell dimensions in degrees.
    """
    shape = to_shape(zone_geometry)
    minx, miny, maxx, maxy = shape.bounds

    # Inset by margin (~5m in degrees)
    margin_deg = 0.000045
    minx += margin_deg
    miny += margin_deg
    maxx -= margin_deg
    maxy -= margin_deg

    # Ensure inset didn't collapse the box
    if maxx <= minx or maxy <= miny:
        # Fallback: use original bounds without margin
        minx, miny, maxx, maxy = shape.bounds

    cols = math.ceil(math.sqrt(unit_count))
    rows = math.ceil(unit_count / cols)

    cell_w = (maxx - minx) / cols
    cell_h = (maxy - miny) / rows

    positions = []
    for i in range(unit_count):
        row = i // cols
        col = i % cols
        cx = minx + (col + 0.5) * cell_w
        cy = miny + (row + 0.5) * cell_h
        positions.append((cx, cy, cell_w, cell_h))

    return positions


def _make_footprint_polygon(cx: float, cy: float, cell_w: float, cell_h: float, fill_ratio: float = 0.7) -> str:
    """Create a WKT POLYGON string for a rectangular footprint centered at (cx, cy)."""
    hw = cell_w * fill_ratio / 2
    hh = cell_h * fill_ratio / 2
    coords = [
        f"{cx - hw} {cy - hh}",
        f"{cx + hw} {cy - hh}",
        f"{cx + hw} {cy + hh}",
        f"{cx - hw} {cy + hh}",
        f"{cx - hw} {cy - hh}",
    ]
    return f"POLYGON(({', '.join(coords)}))"


def _make_rotated_footprint(
    cx: float, cy: float, half_w_m: float, half_h_m: float, rotation_deg: float,
    center_lat: float = 0.0,
) -> str:
    """Create a WKT POLYGON for a rotated rectangular footprint centered at (cx, cy).

    half_w_m/half_h_m are half-dimensions in METERS.
    Rotation is performed in meter space to avoid distortion from non-uniform
    degree scaling at high latitudes, then converted to degree offsets.
    """
    # Build corners in meter space and rotate there
    corners_m = [
        (-half_w_m, -half_h_m),
        ( half_w_m, -half_h_m),
        ( half_w_m,  half_h_m),
        (-half_w_m,  half_h_m),
    ]

    rad = math.radians(rotation_deg)
    cos_r = math.cos(rad)
    sin_r = math.sin(rad)

    m_per_deg_lon = METERS_PER_DEG_LAT * abs(math.cos(math.radians(center_lat or cy)))

    rotated = []
    for dx_m, dy_m in corners_m:
        # Rotate in meter space
        rx_m = dx_m * cos_r - dy_m * sin_r
        ry_m = dx_m * sin_r + dy_m * cos_r
        # Convert rotated meter offsets to degree offsets
        d_lon = rx_m / m_per_deg_lon
        d_lat = ry_m / METERS_PER_DEG_LAT
        rotated.append(f"{cx + d_lon} {cy + d_lat}")
    # Close polygon
    rotated.append(rotated[0])

    return f"POLYGON(({', '.join(rotated)}))"


METERS_PER_DEG_LAT = 111320


def _m_to_deg_lon(m: float, lat: float) -> float:
    return m / (METERS_PER_DEG_LAT * abs(math.cos(math.radians(lat))))


def _m_to_deg_lat(m: float) -> float:
    return m / METERS_PER_DEG_LAT


async def _generate_layout_for_zone(
    zone: SiteZone,
    unit_count: int,
    all_zones: list | None = None,
) -> "SiteLayoutResponse":
    """Call LayoutPlanner to generate an AI-powered site layout for a zone.

    Falls back to algorithmic layout if AI is unavailable.
    """
    from app.schemas.schemas import SiteLayoutResponse

    shape = to_shape(zone.geometry)
    if not isinstance(shape, Polygon):
        # If geometry is not a polygon, convert bounds to polygon
        minx, miny, maxx, maxy = shape.bounds
        shape = Polygon([(minx, miny), (maxx, miny), (maxx, maxy), (minx, maxy)])

    props = zone.properties or {}

    # Build neighbor context
    neighbors = None
    if all_zones:
        neighbors = []
        for other in all_zones:
            if other.id == zone.id:
                continue
            neighbors.append({
                "zone_type": other.zone_type,
                "name": other.name,
            })

    planner = LayoutPlanner()
    layout = await planner.generate_layout(
        zone_polygon=shape,
        zone_type=zone.zone_type,
        unit_count=unit_count,
        properties=props,
        neighbors=neighbors,
    )
    return layout


# =============================================================================
# Layout Preview + Apply Endpoints
# =============================================================================

@router.post("/{zone_id}/preview-layouts", response_model=LayoutPreviewResponse)
async def preview_layouts(
    zone_id: uuid.UUID,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Generate multiple layout options for a multi-unit zone without creating buildings.

    Returns multiple layout strategies for the user to compare and choose from.
    Pure read-only preview — does NOT modify any records.
    """
    result = await db.execute(select(SiteZone).where(SiteZone.id == zone_id))
    zone = result.scalar_one_or_none()
    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")

    if zone.zone_type not in ("building", "residential", "development_area"):
        raise HTTPException(status_code=400, detail="Only building, residential, or development_area zones support layout preview")

    # Check editor permission
    proj_result = await db.execute(select(Project).where(Project.id == zone.project_id))
    project = proj_result.scalar_one_or_none()
    if project.owner_id != user.id and not is_admin_or_above(user):
        share_result = await db.execute(
            select(ProjectShare).where(
                ProjectShare.project_id == zone.project_id,
                (ProjectShare.user_id == user.id) | (ProjectShare.email == user.email),
                ProjectShare.permission == "editor",
            )
        )
        if not share_result.scalar_one_or_none():
            raise HTTPException(status_code=403, detail="Not authorized")

    unit_count = max(_resolve_unit_count(zone), 1)
    option_count = _resolve_layout_option_count(zone, unit_count)

    # Generate layout options
    shape = to_shape(zone.geometry)
    props = zone.properties or {}

    # Gather neighbor context with geometry
    all_zones_result = await db.execute(
        select(SiteZone).where(
            SiteZone.project_id == zone.project_id,
            SiteZone.id != zone.id,
        )
    )
    all_zones = all_zones_result.scalars().all()
    neighbors = _build_neighbor_list(all_zones)

    # Find parent site_boundary OSM context for any zone inside a boundary
    reference_context = None
    for z in all_zones:
        if z.zone_type == "site_boundary":
            z_props = z.properties or {}
            if "_osm_context" in z_props:
                reference_context = z_props["_osm_context"]
                break

    planner = LayoutPlanner()
    options = await planner.generate_layout_options(
        zone_polygon=shape,
        zone_type=zone.zone_type,
        unit_count=unit_count,
        properties=props,
        neighbors=neighbors if neighbors else None,
        count=option_count,
        reference_context=reference_context,
    )

    return LayoutPreviewResponse(
        options=options,
        zone_id=str(zone_id),
    )


@router.post("/{zone_id}/render-layout-preview")
async def render_layout_preview(
    zone_id: uuid.UUID,
    body: dict,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Generate an AI-rendered 2D preview image for a layout option using Gemini.

    Accepts a layout option and returns a URL to the rendered PNG image.
    """
    result = await db.execute(select(SiteZone).where(SiteZone.id == zone_id))
    zone = result.scalar_one_or_none()
    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")

    # Check editor permission
    proj_result = await db.execute(select(Project).where(Project.id == zone.project_id))
    project = proj_result.scalar_one_or_none()
    if project.owner_id != user.id and not is_admin_or_above(user):
        share_result = await db.execute(
            select(ProjectShare).where(
                ProjectShare.project_id == zone.project_id,
                (ProjectShare.user_id == user.id) | (ProjectShare.email == user.email),
                ProjectShare.permission == "editor",
            )
        )
        if not share_result.scalar_one_or_none():
            raise HTTPException(status_code=403, detail="Not authorized")

    # Parse layout from body
    layout_data = body.get("layout")
    if not layout_data:
        raise HTTPException(status_code=400, detail="Missing 'layout' in request body")

    try:
        option = SiteLayoutOption(**layout_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid layout data: {e}")

    shape = to_shape(zone.geometry)
    props = zone.properties or {}

    # Gather full site context for realistic rendering
    all_zones_result = await db.execute(
        select(SiteZone).where(
            SiteZone.project_id == zone.project_id,
            SiteZone.id != zone.id,
        )
    )
    all_zones = all_zones_result.scalars().all()
    neighbors = _build_neighbor_list(all_zones)

    reference_context = None
    for z in all_zones:
        if z.zone_type == "site_boundary":
            z_props = z.properties or {}
            if "_osm_context" in z_props:
                reference_context = z_props["_osm_context"]
                break

    try:
        from app.services.layout_planner import _upload_image_to_storage
        planner = LayoutPlanner()
        image_bytes = await planner.generate_layout_preview_image(
            shape, option, props,
            neighbors=neighbors if neighbors else None,
            reference_context=reference_context,
        )

        # Upload to MinIO
        preview_key = f"projects/{zone.project_id}/layout-previews/{zone_id}_{uuid.uuid4()}.png"
        _upload_image_to_storage(preview_key, image_bytes, "image/png")

        # Return API-relative URL (proxied through /api/v1/files/)
        image_url = f"/api/v1/files/{preview_key}"

        # Save to preview history (include layout data so user can re-apply later)
        await _append_preview_history(
            zone, db,
            image_url=image_url,
            label=option.option_label or f"Option {option.option_index + 1}",
            strategy=option.layout_strategy,
            preview_type="layout",
            option_index=option.option_index,
            layout_data={
                "option_index": option.option_index,
                "option_label": option.option_label,
                "buildings": [b.dict() if hasattr(b, 'dict') else b for b in option.buildings],
                "roads": [r.dict() if hasattr(r, 'dict') else r for r in option.roads],
                "green_spaces": [g.dict() if hasattr(g, 'dict') else g for g in option.green_spaces],
                "layout_strategy": option.layout_strategy,
                "reasoning": option.reasoning,
                "density_achieved": option.density_achieved,
                "orientation_deg": option.orientation_deg,
                "orientation_mode": option.orientation_mode,
            },
        )
        await db.commit()

        return {"image_url": image_url, "zone_id": str(zone_id)}
    except Exception as e:
        logger.error("Layout preview image generation failed for zone %s: %s", zone_id, e)
        raise HTTPException(status_code=500, detail=f"Image generation failed: {e}")


@router.post("/{zone_id}/render-site-preview")
async def render_site_preview(
    zone_id: uuid.UUID,
    body: dict,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Generate an AI-rendered 2D preview image for the ENTIRE site boundary.

    Takes combined layout data from all buildable zones and renders one
    comprehensive aerial view of the whole site including existing infrastructure.
    """
    result = await db.execute(select(SiteZone).where(SiteZone.id == zone_id))
    boundary_zone = result.scalar_one_or_none()
    if not boundary_zone:
        raise HTTPException(status_code=404, detail="Zone not found")
    if boundary_zone.zone_type != "site_boundary":
        raise HTTPException(status_code=400, detail="Zone must be a site_boundary")

    # Check editor permission
    proj_result = await db.execute(select(Project).where(Project.id == boundary_zone.project_id))
    project = proj_result.scalar_one_or_none()
    if project.owner_id != user.id and not is_admin_or_above(user):
        share_result = await db.execute(
            select(ProjectShare).where(
                ProjectShare.project_id == boundary_zone.project_id,
                (ProjectShare.user_id == user.id) | (ProjectShare.email == user.email),
                ProjectShare.permission == "editor",
            )
        )
        if not share_result.scalar_one_or_none():
            raise HTTPException(status_code=403, detail="Not authorized")

    # Parse zone_layouts: { zoneId: LayoutOption }
    zone_layouts = body.get("zone_layouts")
    option_index = body.get("option_index", 0)
    if not zone_layouts:
        raise HTTPException(status_code=400, detail="Missing 'zone_layouts' in request body")

    # Load all contained zones
    all_zones_result = await db.execute(
        select(SiteZone).where(
            SiteZone.project_id == boundary_zone.project_id,
        )
    )
    all_zones = all_zones_result.scalars().all()

    # Build zone lookup and parse layout options
    zone_lookup = {str(z.id): z for z in all_zones}
    parsed_layouts = []
    for zid, layout_data in zone_layouts.items():
        zone_obj = zone_lookup.get(zid)
        if not zone_obj:
            continue
        try:
            option = SiteLayoutOption(**layout_data)
            shape = to_shape(zone_obj.geometry)
            parsed_layouts.append({
                "zone": zone_obj,
                "shape": shape,
                "option": option,
                "properties": zone_obj.properties or {},
            })
        except Exception as e:
            logger.warning("Skipping zone %s: invalid layout data: %s", zid, e)

    # Gather non-buildable zones (roads, green spaces, water, parking)
    non_buildable = []
    # Gather buildable zones that don't have layouts (their properties/descriptions still matter)
    buildable_without_layouts = []
    layout_zone_ids = set(zone_layouts.keys())
    for z in all_zones:
        if str(z.id) == str(zone_id):
            continue  # skip the boundary itself
        if z.zone_type in ("road", "green_space", "water", "parking"):
            try:
                shape = to_shape(z.geometry)
                non_buildable.append({
                    "zone_type": z.zone_type,
                    "shape": shape,
                    "properties": z.properties or {},
                    "name": z.name,
                    "zone_id": str(z.id),
                })
            except Exception:
                pass
        elif z.zone_type in ("building", "residential", "development_area") and str(z.id) not in layout_zone_ids:
            # Buildable zone without a generated layout — still include its properties
            try:
                shape = to_shape(z.geometry)
                buildable_without_layouts.append({
                    "zone": z,
                    "shape": shape,
                    "properties": z.properties or {},
                })
            except Exception:
                pass

    boundary_shape = to_shape(boundary_zone.geometry)
    boundary_props = boundary_zone.properties or {}
    reference_context = boundary_props.get("_osm_context")

    # Parse optional map screenshots (base64 data URLs from frontend canvas capture)
    map_screenshots = None
    satellite_b64 = body.get("map_screenshot_satellite")
    zones_b64 = body.get("map_screenshot_with_zones")
    if satellite_b64 and zones_b64:
        map_screenshots = {"satellite": satellite_b64, "with_zones": zones_b64}

    # Parse optional zone metadata (colors, names, types for prompt context)
    zone_meta = body.get("zone_meta", {})

    try:
        from app.services.layout_planner import _upload_image_to_storage
        planner = LayoutPlanner()
        image_bytes = await planner.generate_site_preview_image(
            boundary_polygon=boundary_shape,
            zone_layouts=parsed_layouts,
            non_buildable_zones=non_buildable,
            reference_context=reference_context,
            map_screenshots=map_screenshots,
            zone_meta=zone_meta,
            buildable_without_layouts=buildable_without_layouts,
        )

        # Upload to MinIO
        preview_key = f"projects/{boundary_zone.project_id}/site-previews/{zone_id}_{option_index}_{uuid.uuid4()}.png"
        _upload_image_to_storage(preview_key, image_bytes, "image/png")

        # Return API-relative URL (proxied through /api/v1/files/)
        image_url = f"/api/v1/files/{preview_key}"

        # Build per-zone layout data for history (so user can re-apply later)
        zone_layouts_for_history = {}
        for zid, layout_dict in zone_layouts.items():
            try:
                opt = SiteLayoutOption(**layout_dict) if isinstance(layout_dict, dict) else layout_dict
                zone_layouts_for_history[zid] = {
                    "option_index": opt.option_index,
                    "option_label": opt.option_label,
                    "buildings": [b.dict() if hasattr(b, 'dict') else b for b in opt.buildings],
                    "roads": [r.dict() if hasattr(r, 'dict') else r for r in opt.roads],
                    "green_spaces": [g.dict() if hasattr(g, 'dict') else g for g in opt.green_spaces],
                    "layout_strategy": opt.layout_strategy,
                    "reasoning": opt.reasoning,
                    "density_achieved": opt.density_achieved,
                    "orientation_deg": opt.orientation_deg,
                    "orientation_mode": opt.orientation_mode,
                }
            except Exception:
                pass

        # Save to preview history on the boundary zone
        await _append_preview_history(
            boundary_zone, db,
            image_url=image_url,
            label=f"Site Preview (option {option_index + 1})",
            strategy="site_preview",
            preview_type="site",
            option_index=option_index,
            layout_data={"zone_layouts": zone_layouts_for_history} if zone_layouts_for_history else None,
        )
        await db.commit()

        return {"image_url": image_url, "zone_id": str(zone_id), "option_index": option_index}
    except Exception as e:
        logger.error("Site preview image generation failed for boundary %s: %s", zone_id, e)
        raise HTTPException(status_code=500, detail=f"Image generation failed: {e}")


@router.post("/{zone_id}/apply-layout", response_model=BuildingResponse)
async def apply_layout(
    zone_id: uuid.UUID,
    body: ApplyLayoutRequest,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Apply a chosen layout option to a zone, creating Building records.

    Takes the chosen layout from a preview and creates Building records.
    Does NOT queue 3D generation — user triggers that separately.
    """
    result = await db.execute(select(SiteZone).where(SiteZone.id == zone_id))
    zone = result.scalar_one_or_none()
    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")

    if zone.zone_type not in ("building", "residential", "development_area"):
        raise HTTPException(status_code=400, detail="Only building, residential, or development_area zones can apply layouts")

    # Check editor permission
    proj_result = await db.execute(select(Project).where(Project.id == zone.project_id))
    project = proj_result.scalar_one_or_none()
    if project.owner_id != user.id and not is_admin_or_above(user):
        share_result = await db.execute(
            select(ProjectShare).where(
                ProjectShare.project_id == zone.project_id,
                (ProjectShare.user_id == user.id) | (ProjectShare.email == user.email),
                ProjectShare.permission == "editor",
            )
        )
        if not share_result.scalar_one_or_none():
            raise HTTPException(status_code=403, detail="Not authorized")

    # If zone already has linked buildings, delete them first (re-applying layout)
    if zone.building_ids:
        for old_bid in _normalize_building_ids(zone.building_ids):
            old_result = await db.execute(select(Building).where(Building.id == old_bid))
            old_building = old_result.scalar_one_or_none()
            if old_building:
                await db.delete(old_building)
        zone.building_id = None
        zone.building_ids = []
        await db.flush()

    layout = body.layout
    props = zone.properties or {}

    # Create buildings from the chosen layout
    shape = to_shape(zone.geometry)
    centroid = shape.centroid
    center_lat = centroid.y
    all_building_ids: list[str] = []
    first_building = None

    for i, lb in enumerate(layout.buildings):
        abs_cx = centroid.x + lb.center_x
        abs_cy = centroid.y + lb.center_y

        footprint_wkt = _make_rotated_footprint(abs_cx, abs_cy, lb.width_m / 2, lb.depth_m / 2, lb.rotation_deg, center_lat)

        building = Building(
            project_id=zone.project_id,
            name=lb.name or f"{zone.name or 'Unit'} #{i + 1}",
            footprint=WKTElement(footprint_wkt, srid=4326),
            height_meters=lb.height_m if lb.height_m is not None else _safe_optional_float(props.get("height")),
            floor_count=lb.floors if lb.floors is not None else _safe_optional_int(props.get("floors")),
            roof_type=props.get("roof_style"),
            rotation_degrees=lb.rotation_deg,
            generation_prompt=lb.description or props.get("description_text") or "",
            specifications={
                **_base_building_specifications(props, lb.description or props.get("description_text")),
                "building_type": lb.building_type,
                "style": lb.style,
                "width_m": lb.width_m,
                "depth_m": lb.depth_m,
            },
        )
        db.add(building)
        await db.flush()
        await db.refresh(building)
        all_building_ids.append(str(building.id))

        if i == 0:
            first_building = building

    if not first_building:
        raise HTTPException(status_code=500, detail="Layout contained no valid buildings")

    # Store layout metadata in zone properties
    updated_props = dict(props)
    updated_props["_layout_strategy"] = layout.layout_strategy
    updated_props["_layout_reasoning"] = layout.reasoning
    updated_props["_layout_roads"] = [r.model_dump() for r in layout.roads]
    updated_props["_layout_green_spaces"] = [g.model_dump() for g in layout.green_spaces]
    if layout.density_achieved:
        updated_props["_layout_density"] = layout.density_achieved
    zone.properties = updated_props

    # Link zone to all buildings
    zone.building_id = first_building.id
    zone.building_ids = all_building_ids
    await db.flush()

    return _building_to_response(first_building)


@router.post("/{zone_id}/regenerate-layout", response_model=LayoutPreviewResponse)
async def regenerate_layout(
    zone_id: uuid.UUID,
    body: RegenerateLayoutRequest,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Regenerate layout with locked layers preserved.

    Keeps locked roads/buildings/green_spaces from the current layout
    and generates new elements around them.
    """
    result = await db.execute(select(SiteZone).where(SiteZone.id == zone_id))
    zone = result.scalar_one_or_none()
    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")

    if zone.zone_type not in ("building", "residential", "development_area"):
        raise HTTPException(status_code=400, detail="Only building, residential, or development_area zones support layout regeneration")

    # Check editor permission
    proj_result = await db.execute(select(Project).where(Project.id == zone.project_id))
    project = proj_result.scalar_one_or_none()
    if project.owner_id != user.id and not is_admin_or_above(user):
        share_result = await db.execute(
            select(ProjectShare).where(
                ProjectShare.project_id == zone.project_id,
                (ProjectShare.user_id == user.id) | (ProjectShare.email == user.email),
                ProjectShare.permission == "editor",
            )
        )
        if not share_result.scalar_one_or_none():
            raise HTTPException(status_code=403, detail="Not authorized")

    unit_count = _resolve_unit_count(zone)
    option_count = _resolve_layout_option_count(zone, unit_count)
    shape = to_shape(zone.geometry)
    props = zone.properties or {}

    # Build locked layers from existing layout data
    locked_layers = None
    existing_roads = props.get("_layout_roads", [])
    existing_green_spaces = props.get("_layout_green_spaces", [])

    if body.locked_roads or body.locked_buildings or body.locked_green_spaces:
        locked_layers = {
            "roads": [existing_roads[i] for i in body.locked_roads if i < len(existing_roads)],
            "buildings": [],  # Building positions from last applied layout
            "green_spaces": [existing_green_spaces[i] for i in body.locked_green_spaces if i < len(existing_green_spaces)],
        }

    # Gather neighbor context and reference context
    all_zones_result = await db.execute(
        select(SiteZone).where(
            SiteZone.project_id == zone.project_id,
            SiteZone.id != zone.id,
        )
    )
    all_zones = all_zones_result.scalars().all()
    neighbors = _build_neighbor_list(all_zones)

    reference_context = None
    for z in all_zones:
        if z.zone_type == "site_boundary":
            z_props = z.properties or {}
            if "_osm_context" in z_props:
                reference_context = z_props["_osm_context"]
                break

    planner = LayoutPlanner()
    options = await planner.generate_layout_options(
        zone_polygon=shape,
        zone_type=zone.zone_type,
        unit_count=unit_count,
        properties=props,
        neighbors=neighbors if neighbors else None,
        count=option_count,
        reference_context=reference_context,
        locked_layers=locked_layers,
    )

    return LayoutPreviewResponse(
        options=options,
        zone_id=str(zone_id),
    )


@router.post("/{zone_id}/create-building", response_model=BuildingResponse)
async def create_building_from_zone(
    zone_id: uuid.UUID,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Auto-create Building record(s) from a zone's geometry and properties.

    For residential zones with unit_count > 1, creates N buildings in a grid
    layout within the zone, all sharing the same model after generation.
    Returns the first building (the one that triggers AI generation).
    """
    result = await db.execute(select(SiteZone).where(SiteZone.id == zone_id))
    zone = result.scalar_one_or_none()
    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")

    if zone.zone_type not in ("building", "residential", "development_area"):
        raise HTTPException(status_code=400, detail="Only building or residential zones can create buildings")

    # Check editor permission on parent project (admins bypass)
    proj_result = await db.execute(select(Project).where(Project.id == zone.project_id))
    project = proj_result.scalar_one_or_none()
    if project.owner_id != user.id and not is_admin_or_above(user):
        share_result = await db.execute(
            select(ProjectShare).where(
                ProjectShare.project_id == zone.project_id,
                (ProjectShare.user_id == user.id) | (ProjectShare.email == user.email),
                ProjectShare.permission == "editor",
            )
        )
        if not share_result.scalar_one_or_none():
            raise HTTPException(status_code=403, detail="Not authorized")

    # If zone already has linked buildings, return the first one
    if zone.building_id:
        existing = await db.execute(select(Building).where(Building.id == zone.building_id))
        building = existing.scalar_one_or_none()
        if building:
            return _building_to_response(building)

    # Extract properties from zone
    props = zone.properties or {}
    unit_count = _resolve_unit_count(zone)

    if unit_count <= 1:
        # Single building - original behavior
        building = Building(
            project_id=zone.project_id,
            name=zone.name or "Building from Zone",
            footprint=zone.geometry,
            height_meters=_safe_optional_float(props.get("height")),
            floor_count=_safe_optional_int(props.get("floors")),
            roof_type=props.get("roof_style"),
            specifications=_base_building_specifications(props),
        )
        db.add(building)
        await db.flush()
        await db.refresh(building)

        zone.building_id = building.id
        zone.building_ids = [str(building.id)]
        await db.flush()

        return _building_to_response(building)

    # Multi-unit: generate AI-powered layout (falls back to algorithmic)
    try:
        layout = await _generate_layout_for_zone(zone, unit_count)
    except Exception as e:
        logger.warning("Layout generation failed for zone %s, falling back to grid: %s", zone_id, e)
        # Last-resort fallback to old grid
        grid_positions = compute_unit_positions(zone.geometry, unit_count)
        all_building_ids_fallback: list[str] = []
        first_building_fallback = None
        for i, (cx, cy, cell_w, cell_h) in enumerate(grid_positions):
            footprint_wkt = _make_footprint_polygon(cx, cy, cell_w, cell_h)
            building = Building(
                project_id=zone.project_id,
                name=f"{zone.name or 'Unit'} #{i + 1}",
                footprint=WKTElement(footprint_wkt, srid=4326),
                height_meters=_safe_optional_float(props.get("height")),
                floor_count=_safe_optional_int(props.get("floors")),
                roof_type=props.get("roof_style"),
                specifications=_base_building_specifications(props),
            )
            db.add(building)
            await db.flush()
            await db.refresh(building)
            all_building_ids_fallback.append(str(building.id))
            if i == 0:
                first_building_fallback = building
        zone.building_id = first_building_fallback.id
        zone.building_ids = all_building_ids_fallback
        await db.flush()
        return _building_to_response(first_building_fallback)

    # Use AI-generated layout to create buildings
    shape = to_shape(zone.geometry)
    centroid = shape.centroid
    center_lat = centroid.y
    all_building_ids: list[str] = []
    first_building = None

    for i, lb in enumerate(layout.buildings):
        abs_cx = centroid.x + lb.center_x
        abs_cy = centroid.y + lb.center_y

        footprint_wkt = _make_rotated_footprint(abs_cx, abs_cy, lb.width_m / 2, lb.depth_m / 2, lb.rotation_deg, center_lat)

        building = Building(
            project_id=zone.project_id,
            name=f"{zone.name or 'Unit'} #{i + 1}",
            footprint=WKTElement(footprint_wkt, srid=4326),
            height_meters=lb.height_m if lb.height_m is not None else _safe_optional_float(props.get("height")),
            floor_count=lb.floors if lb.floors is not None else _safe_optional_int(props.get("floors")),
            roof_type=props.get("roof_style"),
            rotation_degrees=lb.rotation_deg,
            specifications={
                **_base_building_specifications(props),
                "building_type": lb.building_type,
                "width_m": lb.width_m,
                "depth_m": lb.depth_m,
            },
        )
        db.add(building)
        await db.flush()
        await db.refresh(building)
        all_building_ids.append(str(building.id))

        if i == 0:
            first_building = building

    if not first_building:
        raise HTTPException(status_code=500, detail="Layout generation produced no valid buildings")

    # Store layout metadata in zone properties
    updated_props = dict(props)
    updated_props["_layout_strategy"] = layout.layout_strategy
    updated_props["_layout_reasoning"] = layout.reasoning
    updated_props["_layout_roads"] = [r.model_dump() for r in layout.roads]
    updated_props["_layout_green_spaces"] = [g.model_dump() for g in layout.green_spaces]
    if layout.density_achieved:
        updated_props["_layout_density"] = layout.density_achieved
    zone.properties = updated_props

    # Link zone to all buildings
    zone.building_id = first_building.id
    zone.building_ids = all_building_ids
    await db.flush()

    return _building_to_response(first_building)


# =============================================================================
# AI Prompt Composition
# =============================================================================


def compose_zone_prompt(zone: SiteZone, all_zones: list | None = None, site_context: dict | None = None) -> str:
    """Build a rich AI generation prompt from zone properties.

    Includes building type, dimensions from geometry, height/floors,
    facade material, roof style, user description, neighbor context,
    and quality directives for walkthrough-grade models.

    When unit_count > 1, the prompt asks for a single representative
    home suitable for instancing, not an aerial view of a subdivision.

    If site_context is provided, appends a SITE CONTEXT section with
    sibling zone details (types, aesthetics, heights, materials) and
    OSM infrastructure summary (buildings by type, roads by type).
    """
    props = zone.properties or {}
    parts: list[str] = []

    # Determine unit count
    unit_count = _resolve_unit_count(zone)

    # 1. Building type + aesthetic
    aesthetic = props.get("development_aesthetic", "")
    dev_type = props.get("development_type", zone.zone_type)
    aesthetic_label = aesthetic.replace("_", " ").title() if aesthetic else ""
    type_label = dev_type.replace("_", " ").title()
    if unit_count > 1:
        if aesthetic_label:
            parts.append(f"A single {aesthetic_label} {type_label} home suitable for a neighborhood of {unit_count} homes")
        else:
            parts.append(f"A single {type_label} home suitable for a neighborhood of {unit_count} homes")
    elif aesthetic_label:
        parts.append(f"A {aesthetic_label} {type_label} building")
    else:
        parts.append(f"A {type_label} building")

    aesthetic_category = props.get("development_aesthetic_category", "")
    if isinstance(aesthetic_category, str) and aesthetic_category.strip():
        parts.append(f"Aesthetic category: {aesthetic_category.replace('_', ' ').title()}")

    selected_reference = props.get("development_selected_reference")
    if isinstance(selected_reference, dict):
        ref_label = selected_reference.get("label")
        if isinstance(ref_label, str) and ref_label.strip():
            parts.append(f"Archetype reference: {ref_label}")

    archetype_label = props.get("development_archetype_label")
    if isinstance(archetype_label, str) and archetype_label.strip():
        parts.append(f"Archetype profile: {archetype_label}")

    style_profile = props.get("development_style_profile")
    if isinstance(style_profile, dict):
        materials = style_profile.get("materials")
        if isinstance(materials, list):
            valid_materials = [str(item).strip() for item in materials if str(item).strip()]
            if valid_materials:
                parts.append(f"Style materials: {', '.join(valid_materials)}")
        for key, label in (
            ("massing", "Style massing"),
            ("facadeRhythm", "Facade rhythm"),
            ("roofForm", "Roof form"),
            ("frontageType", "Frontage type"),
            ("articulation", "Articulation"),
            ("publicRealm", "Public realm intent"),
        ):
            value = style_profile.get(key)
            if isinstance(value, str) and value.strip():
                parts.append(f"{label}: {value.strip()}")

    generation_style_input = props.get("generation_style_input")
    if isinstance(generation_style_input, dict):
        subcategory = generation_style_input.get("buildingSubcategory")
        if isinstance(subcategory, str) and subcategory.strip():
            parts.append(f"Building subcategory: {subcategory.replace('_', ' ')}")

    # 2. Dimensions from PostGIS geometry
    try:
        shape = to_shape(zone.geometry)
        bounds = shape.bounds  # (minx, miny, maxx, maxy)
        # Approximate width and depth in meters
        center_lat = (bounds[1] + bounds[3]) / 2
        meters_per_deg_lon = 111320 * abs(
            __import__("math").cos(__import__("math").radians(center_lat))
        )
        meters_per_deg_lat = 111320
        width_m = abs(bounds[2] - bounds[0]) * meters_per_deg_lon
        depth_m = abs(bounds[3] - bounds[1]) * meters_per_deg_lat
        area_m2 = width_m * depth_m
        if width_m > 1 and depth_m > 1:
            parts.append(
                f"Building footprint approximately {width_m:.0f}m wide by "
                f"{depth_m:.0f}m deep ({area_m2:.0f} sq meters)"
            )
    except Exception:
        pass

    # 3. Height / floors
    floors = props.get("floors")
    height = props.get("height")
    floor_height = props.get("floor_height", 3)
    if floors and height:
        parts.append(
            f"{floors} stories tall ({height}m total height), "
            f"each floor {floor_height}m high"
        )
    elif floors:
        total = floors * floor_height
        parts.append(
            f"{floors} stories tall ({total}m total height), "
            f"each floor {floor_height}m high"
        )

    # 4. Facade material + roof style
    facade = props.get("facade_material")
    roof = props.get("roof_style")
    if facade and roof:
        parts.append(f"{facade} facade material, {roof} roof style")
    elif facade:
        parts.append(f"{facade} facade material")
    elif roof:
        parts.append(f"{roof} roof style")

    # 5. User description text (pass through verbatim)
    desc = props.get("description_text")
    if desc:
        parts.append(desc)

    # 6. Neighbor context
    if all_zones:
        try:
            buffered = zone.geometry.ST_Buffer(0.0002)  # ~20m buffer at equator
            neighbor_types: set[str] = set()
            for other in all_zones:
                if other.id == zone.id:
                    continue
                if other.geometry is not None:
                    neighbor_types.add(other.zone_type.replace("_", " "))
            if neighbor_types:
                parts.append(f"Surrounded by: {', '.join(sorted(neighbor_types))}")
        except Exception:
            pass

    # 7. Quality directives
    if unit_count > 1:
        parts.append(
            "Realistic architectural style with detailed facade, visible windows, "
            "entrance doors, and appropriate material textures. "
            "Suitable for close-up walkthrough viewing. "
            "Single standalone unit, no surrounding buildings or landscape, "
            "no background or ground plane."
        )
    else:
        parts.append(
            "Realistic architectural style with detailed facade, visible windows, "
            "entrance doors, and appropriate material textures. "
            "Suitable for close-up walkthrough viewing. "
            "Single standalone building, no background or ground plane."
        )

    # 8. Site context (boundary-scoped)
    if site_context:
        ctx_parts: list[str] = []
        # Sibling zones summary
        sibling_zones = site_context.get("sibling_zones", [])
        if sibling_zones:
            zone_summaries = []
            for sz in sibling_zones:
                desc = sz.get("zone_type", "").replace("_", " ").title()
                if sz.get("aesthetic"):
                    desc = f"{sz['aesthetic'].replace('_', ' ').title()} {desc}"
                if sz.get("height"):
                    desc += f" ({sz['height']}m)"
                if sz.get("facade_material"):
                    desc += f", {sz['facade_material']}"
                zone_summaries.append(desc)
            ctx_parts.append(f"Sibling zones in the site: {'; '.join(zone_summaries)}")
        # OSM buildings summary
        osm_buildings = site_context.get("osm_buildings", {})
        if osm_buildings.get("count"):
            osm_desc = f"{osm_buildings['count']} existing buildings nearby"
            if osm_buildings.get("avg_height"):
                osm_desc += f" (avg height {osm_buildings['avg_height']:.0f}m)"
            by_type = osm_buildings.get("by_type", {})
            if by_type:
                type_parts = [f"{v} {k}" for k, v in sorted(by_type.items(), key=lambda x: -x[1])[:5]]
                osm_desc += f" — {', '.join(type_parts)}"
            ctx_parts.append(osm_desc)
        # OSM roads summary
        osm_roads = site_context.get("osm_roads", {})
        if osm_roads.get("count"):
            road_desc = f"{osm_roads['count']} existing roads nearby"
            named = osm_roads.get("named_roads", [])
            if named:
                road_desc += f" including {', '.join(named[:5])}"
            ctx_parts.append(road_desc)
        if ctx_parts:
            parts.append("SITE CONTEXT: " + ". ".join(ctx_parts))

    return ". ".join(parts)


# =============================================================================
# Boundary Analysis
# =============================================================================


def _build_site_context(boundary_zone: SiteZone, contained_zones: list[SiteZone]) -> dict:
    """Build a site_context dict from a boundary zone and its contained zones."""
    sibling_zones = []
    for z in contained_zones:
        if z.id == boundary_zone.id:
            continue
        zp = z.properties or {}
        sibling_zones.append({
            "zone_type": z.zone_type,
            "name": z.name,
            "aesthetic": zp.get("development_aesthetic"),
            "height": zp.get("height"),
            "floors": zp.get("floors"),
            "facade_material": zp.get("facade_material"),
            "description": zp.get("description_text"),
        })

    # Extract OSM context from boundary properties (stored during creation as _osm_context)
    # Summarize raw arrays into prompt-friendly dicts
    boundary_props = boundary_zone.properties or {}
    osm_ctx = boundary_props.get("_osm_context", {})

    osm_buildings_summary = {}
    raw_buildings = osm_ctx.get("buildings", [])
    if raw_buildings and isinstance(raw_buildings, list):
        heights = [b.get("height_m") for b in raw_buildings if b.get("height_m")]
        by_type: dict[str, int] = {}
        for b in raw_buildings:
            bt = b.get("building_type", "unknown")
            by_type[bt] = by_type.get(bt, 0) + 1
        osm_buildings_summary = {
            "count": len(raw_buildings),
            "avg_height": round(sum(heights) / len(heights), 1) if heights else None,
            "by_type": by_type,
        }

    osm_roads_summary = {}
    raw_roads = osm_ctx.get("roads", [])
    if raw_roads and isinstance(raw_roads, list):
        named = list({r.get("name") for r in raw_roads if r.get("name")})
        by_road_type: dict[str, int] = {}
        for r in raw_roads:
            rt = r.get("road_type", "unknown")
            by_road_type[rt] = by_road_type.get(rt, 0) + 1
        osm_roads_summary = {
            "count": len(raw_roads),
            "named_roads": sorted(named),
            "by_type": by_road_type,
        }

    return {
        "sibling_zones": sibling_zones,
        "osm_buildings": osm_buildings_summary,
        "osm_roads": osm_roads_summary,
    }


def _compute_zone_area(zone: SiteZone) -> float:
    """Compute approximate area in m² from zone geometry."""
    try:
        shape = to_shape(zone.geometry)
        bounds = shape.bounds
        center_lat = (bounds[1] + bounds[3]) / 2
        meters_per_deg_lon = 111320 * abs(math.cos(math.radians(center_lat)))
        meters_per_deg_lat = 111320
        width_m = abs(bounds[2] - bounds[0]) * meters_per_deg_lon
        depth_m = abs(bounds[3] - bounds[1]) * meters_per_deg_lat
        return width_m * depth_m
    except Exception:
        return 0.0


@router.get("/{zone_id}/boundary-analysis")
async def boundary_analysis(
    zone_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Analyze a site boundary: find all zones within it and return summary."""
    result = await db.execute(select(SiteZone).where(SiteZone.id == zone_id))
    boundary = result.scalar_one_or_none()
    if not boundary:
        raise HTTPException(status_code=404, detail="Zone not found")
    if boundary.zone_type != "site_boundary":
        raise HTTPException(status_code=400, detail="Zone is not a site_boundary")

    # Find all zones that intersect this boundary (same project, exclude self)
    contained_result = await db.execute(
        select(SiteZone).where(
            SiteZone.project_id == boundary.project_id,
            SiteZone.id != boundary.id,
            ST_Intersects(boundary.geometry, SiteZone.geometry),
        )
    )
    contained_zones = contained_result.scalars().all()

    # Build zone details for response
    zone_details = []
    type_counts: dict[str, int] = {}
    for z in contained_zones:
        zp = z.properties or {}
        zone_details.append({
            "id": str(z.id),
            "name": z.name,
            "zone_type": z.zone_type,
            "color": z.color,
            "properties": zp,
            "area_m2": _compute_zone_area(z),
        })
        type_counts[z.zone_type] = type_counts.get(z.zone_type, 0) + 1

    # OSM context from boundary properties (stored as _osm_context)
    # Summarize raw arrays into frontend-friendly structure
    boundary_props = boundary.properties or {}
    raw_osm = boundary_props.get("_osm_context", {})

    osm_summary: dict = {}
    raw_buildings = raw_osm.get("buildings", [])
    if raw_buildings and isinstance(raw_buildings, list):
        heights = [b.get("height_m") for b in raw_buildings if b.get("height_m")]
        by_type: dict[str, int] = {}
        for b in raw_buildings:
            bt = b.get("building_type", "unknown")
            by_type[bt] = by_type.get(bt, 0) + 1
        osm_summary["buildings"] = {
            "count": len(raw_buildings),
            "avg_height": round(sum(heights) / len(heights), 1) if heights else None,
            "by_type": by_type,
        }

    raw_roads = raw_osm.get("roads", [])
    if raw_roads and isinstance(raw_roads, list):
        named = list({r.get("name") for r in raw_roads if r.get("name")})
        by_road_type: dict[str, int] = {}
        for r in raw_roads:
            rt = r.get("road_type", "unknown")
            by_road_type[rt] = by_road_type.get(rt, 0) + 1
        osm_summary["roads"] = {
            "count": len(raw_roads),
            "named_roads": sorted(named),
            "by_type": by_road_type,
        }

    return {
        "boundary_zone_id": str(boundary.id),
        "contained_zones": zone_details,
        "zone_summary": type_counts,
        "total_contained": len(contained_zones),
        "osm_context": osm_summary,
    }


# =============================================================================
# Batch Generate All
# =============================================================================

@router.post("/projects/{project_id}/generate-all")
async def generate_all(
    project_id: uuid.UUID,
    boundary_zone_id: Optional[uuid.UUID] = Query(None, description="Scope generation to zones within this site boundary"),
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Batch-generate buildings + queue AI 3D model generation for building/residential zones.

    When boundary_zone_id is provided, only zones within that boundary are processed
    and the AI prompt is enriched with site context (sibling zones + OSM data).
    """
    # Verify project & permissions
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project.owner_id != user.id and not is_admin_or_above(user):
        share_result = await db.execute(
            select(ProjectShare).where(
                ProjectShare.project_id == project_id,
                (ProjectShare.user_id == user.id) | (ProjectShare.email == user.email),
                ProjectShare.permission == "editor",
            )
        )
        if not share_result.scalar_one_or_none():
            raise HTTPException(status_code=403, detail="Not authorized")

    # Build zone list — scoped to boundary if provided
    site_context: dict | None = None

    if boundary_zone_id:
        # Validate boundary zone
        boundary_result = await db.execute(
            select(SiteZone).where(SiteZone.id == boundary_zone_id)
        )
        boundary_zone = boundary_result.scalar_one_or_none()
        if not boundary_zone:
            raise HTTPException(status_code=404, detail="Boundary zone not found")
        if boundary_zone.zone_type != "site_boundary":
            raise HTTPException(status_code=400, detail="Specified zone is not a site_boundary")
        if boundary_zone.project_id != project_id:
            raise HTTPException(status_code=400, detail="Boundary zone does not belong to this project")

        # Fetch only zones within the boundary
        zones_result = await db.execute(
            select(SiteZone).where(
                SiteZone.project_id == project_id,
                SiteZone.id != boundary_zone_id,
                ST_Intersects(boundary_zone.geometry, SiteZone.geometry),
            )
        )
        all_zones = zones_result.scalars().all()

        # Build enriched site context
        site_context = _build_site_context(boundary_zone, all_zones)
    else:
        # Fetch all zones for this project (original behavior)
        zones_result = await db.execute(
            select(SiteZone).where(SiteZone.project_id == project_id)
        )
        all_zones = zones_result.scalars().all()

    buildings_created = 0
    generations_queued = 0
    queued_buildings = []
    total_zones = len(all_zones)
    failed_zones = []

    for zone in all_zones:
        if zone.zone_type not in ("building", "residential", "development_area"):
            continue

        try:
            zone_props = zone.properties or {}
            ref_images = zone_props.get("reference_images") or []
            if isinstance(ref_images, list):
                ref_images = [
                    img for img in ref_images
                    if isinstance(img, str) and img.lower().startswith(("http://", "https://"))
                ]
            else:
                ref_images = []

            # If zone already has linked buildings, queue generation for all valid IDs.
            existing_ids = _normalize_building_ids(zone.building_ids)
            if existing_ids:
                for bid in existing_ids:
                    existing = await db.execute(select(Building).where(Building.id == bid))
                    building = existing.scalar_one_or_none()
                    if not building:
                        continue
                    if building.generation_status == "generating":
                        continue

                    prompt = compose_zone_prompt(zone, all_zones, site_context=site_context)
                    building.generation_status = "generating"
                    building.generation_prompt = prompt
                    await db.flush()

                    try:
                        from app.tasks.processing import generate_3d_model_ai
                        if ref_images:
                            generate_3d_model_ai.delay(str(building.id), prompt, "image", ref_images[0])
                        else:
                            generate_3d_model_ai.delay(str(building.id), prompt, "text")
                        generations_queued += 1
                        queued_buildings.append({"id": str(building.id), "name": building.name or "Building"})
                    except Exception as e:
                        logger.warning("Failed to queue generation for building %s: %s", building.id, e)
                continue
            elif zone.building_ids:
                logger.warning("Zone %s had invalid building_ids payload; regenerating from zone geometry", zone.id)
                zone.building_id = None
                zone.building_ids = []
                await db.flush()

            # Determine unit count for this zone
            unit_count = _resolve_unit_count(zone)

            if unit_count <= 1:
                # Single building
                building = Building(
                    project_id=zone.project_id,
                    name=zone.name or "Building from Zone",
                    footprint=zone.geometry,
                    height_meters=_safe_optional_float(zone_props.get("height")),
                    floor_count=_safe_optional_int(zone_props.get("floors")),
                    roof_type=zone_props.get("roof_style"),
                    specifications=_base_building_specifications(zone_props),
                )
                db.add(building)
                await db.flush()
                await db.refresh(building)

                zone.building_id = building.id
                zone.building_ids = [str(building.id)]
                await db.flush()
                buildings_created += 1
            else:
                # Multi-unit: generate AI-powered layout
                try:
                    layout = await _generate_layout_for_zone(zone, unit_count, all_zones)
                except Exception as layout_err:
                    logger.warning("Layout gen failed for zone %s in batch, falling back to grid: %s", zone.id, layout_err)
                    grid_positions = compute_unit_positions(zone.geometry, unit_count)
                    all_building_ids_fb: list[str] = []
                    first_building_fb = None

                    for i, (cx, cy, cell_w, cell_h) in enumerate(grid_positions):
                        footprint_wkt = _make_footprint_polygon(cx, cy, cell_w, cell_h)
                        b = Building(
                            project_id=zone.project_id,
                            name=f"{zone.name or 'Unit'} #{i + 1}",
                            footprint=WKTElement(footprint_wkt, srid=4326),
                            height_meters=_safe_optional_float(zone_props.get("height")),
                            floor_count=_safe_optional_int(zone_props.get("floors")),
                            roof_type=zone_props.get("roof_style"),
                            specifications=_base_building_specifications(zone_props),
                        )
                        db.add(b)
                        await db.flush()
                        await db.refresh(b)
                        all_building_ids_fb.append(str(b.id))
                        if i == 0:
                            first_building_fb = b

                    if not first_building_fb:
                        raise ValueError("Fallback layout produced no buildings")

                    zone.building_id = first_building_fb.id
                    zone.building_ids = all_building_ids_fb
                    await db.flush()
                    buildings_created += len(all_building_ids_fb)

                    building = first_building_fb
                    prompt = compose_zone_prompt(zone, all_zones, site_context=site_context)
                    building.generation_status = "generating"
                    building.generation_prompt = prompt
                    await db.flush()

                    try:
                        from app.tasks.processing import generate_3d_model_ai
                        if ref_images:
                            generate_3d_model_ai.delay(str(building.id), prompt, "image", ref_images[0])
                        else:
                            generate_3d_model_ai.delay(str(building.id), prompt, "text")
                        generations_queued += 1
                        queued_buildings.append({"id": str(building.id), "name": building.name or "Building"})
                    except Exception as e:
                        logger.warning("Failed to queue generation for building %s: %s", building.id, e)
                    continue

                # Use AI layout to create buildings
                shape = to_shape(zone.geometry)
                centroid = shape.centroid
                center_lat = centroid.y
                all_building_ids: list[str] = []
                first_building = None

                for i, lb in enumerate(layout.buildings):
                    abs_cx = centroid.x + lb.center_x
                    abs_cy = centroid.y + lb.center_y
                    footprint_wkt = _make_rotated_footprint(abs_cx, abs_cy, lb.width_m / 2, lb.depth_m / 2, lb.rotation_deg, center_lat)

                    b = Building(
                        project_id=zone.project_id,
                        name=f"{zone.name or 'Unit'} #{i + 1}",
                        footprint=WKTElement(footprint_wkt, srid=4326),
                        height_meters=lb.height_m if lb.height_m is not None else _safe_optional_float(zone_props.get("height")),
                        floor_count=lb.floors if lb.floors is not None else _safe_optional_int(zone_props.get("floors")),
                        roof_type=zone_props.get("roof_style"),
                        rotation_degrees=lb.rotation_deg,
                        specifications={
                            **_base_building_specifications(zone_props),
                            "building_type": lb.building_type,
                            "width_m": lb.width_m,
                            "depth_m": lb.depth_m,
                        },
                    )
                    db.add(b)
                    await db.flush()
                    await db.refresh(b)
                    all_building_ids.append(str(b.id))
                    if i == 0:
                        first_building = b

                if not first_building:
                    raise ValueError("Layout generation produced no valid buildings")

                updated_props = dict(zone_props)
                updated_props["_layout_strategy"] = layout.layout_strategy
                updated_props["_layout_reasoning"] = layout.reasoning
                updated_props["_layout_roads"] = [r.model_dump() for r in layout.roads]
                updated_props["_layout_green_spaces"] = [g.model_dump() for g in layout.green_spaces]
                if layout.density_achieved:
                    updated_props["_layout_density"] = layout.density_achieved
                zone.properties = updated_props

                zone.building_id = first_building.id
                zone.building_ids = all_building_ids
                await db.flush()
                buildings_created += len(layout.buildings)
                building = first_building

            # Compose prompt and queue generation (single building for this zone)
            prompt = compose_zone_prompt(zone, all_zones, site_context=site_context)
            building.generation_status = "generating"
            building.generation_prompt = prompt
            await db.flush()
            try:
                from app.tasks.processing import generate_3d_model_ai
                if ref_images:
                    generate_3d_model_ai.delay(str(building.id), prompt, "image", ref_images[0])
                else:
                    generate_3d_model_ai.delay(str(building.id), prompt, "text")
                generations_queued += 1
                queued_buildings.append({"id": str(building.id), "name": building.name or "Building"})
            except Exception as e:
                logger.warning("Failed to queue generation for building %s: %s", building.id, e)

        except Exception as zone_err:
            logger.exception("Batch generation failed for zone %s: %s", zone.id, zone_err)
            failed_zones.append({"zone_id": str(zone.id), "zone_name": zone.name, "error": str(zone_err)})
            continue

    return {
        "total_zones": total_zones,
        "buildings_created": buildings_created,
        "generations_queued": generations_queued,
        "queued_buildings": queued_buildings,
        "failed_zones": failed_zones,
    }


# =============================================================================
# Save Layout (persist edited layout without creating buildings)
# =============================================================================


from pydantic import BaseModel as _BaseModel

class SaveLayoutRequest(_BaseModel):
    """Request to save an edited layout to zone properties."""
    layout: SiteLayoutResponse


@router.put("/{zone_id}/save-layout")
async def save_layout(
    zone_id: uuid.UUID,
    body: SaveLayoutRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_auth),
):
    """Save an edited layout to zone properties AND sync building records."""
    result = await db.execute(select(SiteZone).where(SiteZone.id == zone_id))
    zone = result.scalar_one_or_none()
    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")

    # 1. Save layout to zone properties
    props = zone.properties or {}
    props["_saved_layout"] = body.layout.model_dump()
    zone.properties = props
    flag_modified(zone, "properties")

    # 2. Sync building records with layout blocks
    shape = to_shape(zone.geometry)
    centroid = shape.centroid
    center_lat = centroid.y

    bid_list = _normalize_building_ids(zone.building_ids)
    layout_buildings = body.layout.buildings
    buildings_updated = 0
    buildings_created = 0
    buildings_deleted = 0

    # Update existing buildings that still have a corresponding layout block
    for i, bid in enumerate(bid_list):
        if i >= len(layout_buildings):
            # Extra building record with no layout block - delete it
            bld_result = await db.execute(select(Building).where(Building.id == bid))
            building = bld_result.scalar_one_or_none()
            if building:
                await db.delete(building)
                buildings_deleted += 1
            continue

        lb = layout_buildings[i]
        bld_result = await db.execute(select(Building).where(Building.id == bid))
        building = bld_result.scalar_one_or_none()
        if not building:
            continue

        # Update footprint geometry
        abs_cx = centroid.x + lb.center_x
        abs_cy = centroid.y + lb.center_y
        footprint_wkt = _make_rotated_footprint(abs_cx, abs_cy, lb.width_m / 2, lb.depth_m / 2, lb.rotation_deg, center_lat)
        building.footprint = WKTElement(footprint_wkt, srid=4326)

        # Update building metadata from block editor (always sync all fields)
        building.name = lb.name or building.name
        building.height_meters = lb.height_m or building.height_meters
        building.floor_count = lb.floors or building.floor_count
        building.rotation_degrees = lb.rotation_deg
        building.generation_prompt = lb.description or props.get("description_text") or building.generation_prompt or ""
        specs = building.specifications or {}
        specs.update(_base_building_specifications(props, lb.description or props.get("description_text") or specs.get("description_text")))
        specs["style"] = lb.style or specs.get("style")
        specs["building_type"] = lb.building_type
        specs["width_m"] = lb.width_m
        specs["depth_m"] = lb.depth_m
        building.specifications = _compact_spec_values(specs)
        flag_modified(building, "specifications")

        buildings_updated += 1

    # Create new buildings for layout blocks beyond existing building_ids
    new_bid_list = [str(bid) for i, bid in enumerate(bid_list) if i < len(layout_buildings)]
    for i in range(len(bid_list), len(layout_buildings)):
        lb = layout_buildings[i]
        abs_cx = centroid.x + lb.center_x
        abs_cy = centroid.y + lb.center_y
        footprint_wkt = _make_rotated_footprint(abs_cx, abs_cy, lb.width_m / 2, lb.depth_m / 2, lb.rotation_deg, center_lat)

        building = Building(
            project_id=zone.project_id,
            name=lb.name or f"{zone.name or 'Unit'} #{i + 1}",
            footprint=WKTElement(footprint_wkt, srid=4326),
            height_meters=lb.height_m if lb.height_m is not None else _safe_optional_float(props.get("height")),
            floor_count=lb.floors if lb.floors is not None else _safe_optional_int(props.get("floors")),
            roof_type=props.get("roof_style"),
            rotation_degrees=lb.rotation_deg,
            generation_prompt=lb.description or props.get("description_text") or "",
            specifications={
                **_base_building_specifications(props, lb.description or props.get("description_text")),
                "building_type": lb.building_type,
                "style": lb.style,
                "width_m": lb.width_m,
                "depth_m": lb.depth_m,
            },
        )
        db.add(building)
        await db.flush()
        await db.refresh(building)
        new_bid_list.append(str(building.id))
        buildings_created += 1

    # Update zone building_ids to match the current layout
    zone.building_ids = new_bid_list
    if new_bid_list:
        zone.building_id = uuid.UUID(new_bid_list[0])
    flag_modified(zone, "building_ids")

    await db.commit()

    return {
        "status": "saved",
        "zone_id": str(zone_id),
        "buildings_updated": buildings_updated,
        "buildings_created": buildings_created,
        "buildings_deleted": buildings_deleted,
    }

