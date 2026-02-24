"""
Site Zone management API endpoints.
"""

import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from geoalchemy2.elements import WKTElement
from geoalchemy2.shape import to_shape
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_auth
from app.models.models import Building, Project, ProjectShare, SiteZone, User
from app.schemas.schemas import BuildingResponse, SiteZoneCreate, SiteZoneResponse, SiteZoneUpdate
from app.api.v1.buildings import _building_to_response

router = APIRouter()


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

    # Check editor permission
    if project.owner_id != user.id:
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

    return _zone_to_response(zone)


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

    # Check editor permission on parent project
    proj_result = await db.execute(select(Project).where(Project.id == zone.project_id))
    project = proj_result.scalar_one_or_none()
    if project.owner_id != user.id:
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

    # Check editor permission on parent project
    proj_result = await db.execute(select(Project).where(Project.id == zone.project_id))
    project = proj_result.scalar_one_or_none()
    if project.owner_id != user.id:
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


@router.post("/{zone_id}/create-building", response_model=BuildingResponse)
async def create_building_from_zone(
    zone_id: uuid.UUID,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Auto-create a Building record from a zone's geometry and properties."""
    result = await db.execute(select(SiteZone).where(SiteZone.id == zone_id))
    zone = result.scalar_one_or_none()
    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")

    if zone.zone_type not in ("building", "residential"):
        raise HTTPException(status_code=400, detail="Only building or residential zones can create buildings")

    # Check editor permission on parent project
    proj_result = await db.execute(select(Project).where(Project.id == zone.project_id))
    project = proj_result.scalar_one_or_none()
    if project.owner_id != user.id:
        share_result = await db.execute(
            select(ProjectShare).where(
                ProjectShare.project_id == zone.project_id,
                (ProjectShare.user_id == user.id) | (ProjectShare.email == user.email),
                ProjectShare.permission == "editor",
            )
        )
        if not share_result.scalar_one_or_none():
            raise HTTPException(status_code=403, detail="Not authorized")

    # If zone already has a linked building, return it
    if zone.building_id:
        existing = await db.execute(select(Building).where(Building.id == zone.building_id))
        building = existing.scalar_one_or_none()
        if building:
            return _building_to_response(building)

    # Extract properties from zone
    props = zone.properties or {}

    building = Building(
        project_id=zone.project_id,
        name=zone.name or "Building from Zone",
        footprint=zone.geometry,
        height_meters=props.get("height"),
        floor_count=props.get("floors"),
        roof_type=props.get("roof_style"),
    )

    db.add(building)
    await db.flush()
    await db.refresh(building)

    # Link the zone to the new building
    zone.building_id = building.id
    await db.flush()

    return _building_to_response(building)


# =============================================================================
# AI Prompt Composition
# =============================================================================

logger = logging.getLogger(__name__)


def compose_zone_prompt(zone: SiteZone, all_zones: list | None = None) -> str:
    """Build a rich AI generation prompt from zone properties.

    Includes building type, dimensions from geometry, height/floors,
    facade material, roof style, user description, neighbor context,
    and quality directives for walkthrough-grade models.
    """
    props = zone.properties or {}
    parts: list[str] = []

    # 1. Building type + aesthetic
    aesthetic = props.get("development_aesthetic", "")
    dev_type = props.get("development_type", zone.zone_type)
    aesthetic_label = aesthetic.replace("_", " ").title() if aesthetic else ""
    type_label = dev_type.replace("_", " ").title()
    if aesthetic_label:
        parts.append(f"A {aesthetic_label} {type_label} building")
    else:
        parts.append(f"A {type_label} building")

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
    parts.append(
        "Realistic architectural style with detailed facade, visible windows, "
        "entrance doors, and appropriate material textures. "
        "Suitable for close-up walkthrough viewing. "
        "Single standalone building, no background or ground plane."
    )

    return ". ".join(parts)


# =============================================================================
# Batch Generate All
# =============================================================================

@router.post("/projects/{project_id}/generate-all")
async def generate_all(
    project_id: uuid.UUID,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Batch-generate buildings + queue AI 3D model generation for all building/residential zones."""
    # Verify project & permissions
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project.owner_id != user.id:
        share_result = await db.execute(
            select(ProjectShare).where(
                ProjectShare.project_id == project_id,
                (ProjectShare.user_id == user.id) | (ProjectShare.email == user.email),
                ProjectShare.permission == "editor",
            )
        )
        if not share_result.scalar_one_or_none():
            raise HTTPException(status_code=403, detail="Not authorized")

    # Fetch all zones for this project
    zones_result = await db.execute(
        select(SiteZone).where(SiteZone.project_id == project_id)
    )
    all_zones = zones_result.scalars().all()

    buildings_created = 0
    generations_queued = 0
    total_zones = len(all_zones)

    for zone in all_zones:
        if zone.zone_type not in ("building", "residential"):
            continue

        zone_props = zone.properties or {}
        ref_images = zone_props.get("reference_images") or []

        # If zone already has a linked building, skip creation
        if zone.building_id:
            existing = await db.execute(select(Building).where(Building.id == zone.building_id))
            building = existing.scalar_one_or_none()
            if building:
                # Queue generation if not currently in progress
                if building.generation_status != "generating":
                    prompt = compose_zone_prompt(zone, all_zones)
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
                    except Exception as e:
                        logger.warning("Failed to queue generation for building %s: %s", building.id, e)
                continue

        # Create a new building from the zone
        building = Building(
            project_id=zone.project_id,
            name=zone.name or "Building from Zone",
            footprint=zone.geometry,
            height_meters=zone_props.get("height"),
            floor_count=zone_props.get("floors"),
            roof_type=zone_props.get("roof_style"),
        )
        db.add(building)
        await db.flush()
        await db.refresh(building)

        # Link zone to building
        zone.building_id = building.id
        await db.flush()
        buildings_created += 1

        # Compose prompt and queue generation
        prompt = compose_zone_prompt(zone, all_zones)
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
        except Exception as e:
            logger.warning("Failed to queue generation for building %s: %s", building.id, e)

    return {
        "total_zones": total_zones,
        "buildings_created": buildings_created,
        "generations_queued": generations_queued,
    }
