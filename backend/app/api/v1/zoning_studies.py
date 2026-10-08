"""Student cartography stored as independent versioned reference layers.

No statutory zoning, development drawings, assessments or terrain are changed.
Project locking and content revisions protect classmates' concurrent edits.
"""
import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException
from geoalchemy2.shape import to_shape
from pydantic import BaseModel, Field, FiniteFloat, StringConstraints
from shapely.geometry import Polygon, mapping
from shapely.ops import unary_union
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

from app.core.database import get_db
from app.core.security import check_project_permission, require_auth
from app.models.models import Project, SiteZone, User
from app.models.reference_layers import ReferenceLayer
from app.schemas.reference_layers import ReferenceLayerResponse
from app.services.spatial_engine import SiteFrame

router = APIRouter()
Condition = Literal["existing", "proposed", "draft-2025"]
DRAFT_SOURCE = "https://www.calgary.ca/content/dam/www/pda/pd/documents/city-building-program/cbp.annotated-draft-zoning-bylaw-may2025.pdf"
Position = tuple[FiniteFloat, FiniteFloat]
Ring = Annotated[list[Position], Field(min_length=4, max_length=4096)]


class StudyDistrict(BaseModel):
    bylaw: Literal["draft-2025"] | None = None
    # A student's district reference, not a regulatory compliance assertion.
    # Full designation retains density/height modifiers and individual DC bylaws.
    designation: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=120)]
    code: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=40)] | None = None
    description: Annotated[str, StringConstraints(strip_whitespace=True, max_length=300)] | None = None


class StudyZone(BaseModel):
    id: str = Field(min_length=1, max_length=80, pattern=r"^[a-zA-Z0-9_-]+$")
    label: str = Field(min_length=1, max_length=120)
    color: str = Field(pattern=r"^#[0-9a-fA-F]{6}$")
    origin: Literal["student", "calgary-extract"] = "student"
    district: StudyDistrict | None = None
    custom: bool = False
    rings: list[Ring] = Field(min_length=1, max_length=32)


class StudyRequest(BaseModel):
    boundary_id: uuid.UUID
    boundary_coordinates: list[Position] = Field(min_length=3, max_length=1024)
    expected_hash: str | None = Field(default=None, pattern=r"^[a-f0-9]{64}$")
    zones: list[StudyZone] = Field(max_length=256)
    opacity: float = Field(default=0.4, ge=0, le=1, allow_inf_nan=False)


def study_collection(request: StudyRequest, condition: Condition, site: Polygon):
    if site.is_empty or not site.is_valid or not 0 < SiteFrame.from_wgs84(site).area_m2 <= 25_000_000:
        raise ValueError("Use a valid site boundary smaller than 25 km².")
    if len({zone.id for zone in request.zones}) != len(request.zones):
        raise ValueError("Study zones need distinct IDs.")
    positions = 0
    shapes = []
    features = []
    for zone in request.zones:
        draft = condition == "draft-2025"
        if draft and zone.origin == "calgary-extract":
            raise ValueError("Draft zoning has no published City zoning boundaries to copy.")
        if zone.district and draft != (zone.district.bylaw == "draft-2025"):
            raise ValueError("Keep draft and current bylaw districts in their separate study layers.")
        positions += sum(len(ring) for ring in zone.rings)
        if positions > 50_000 or any(not 4 <= len(ring) <= 4096 or ring[0] != ring[-1] for ring in zone.rings):
            raise ValueError("Use closed outlines with 4–4,096 points and at most 50,000 points per study.")
        if any(abs(x) > 180 or abs(y) > 85 for ring in zone.rings for x, y in ring):
            raise ValueError("Study coordinates must be valid map locations.")
        shape = Polygon(zone.rings[0], zone.rings[1:])
        if not shape.is_valid or shape.is_empty or shape.area <= 0:
            raise ValueError("A zone crosses itself or has an invalid hole. Undo the edit and redraw it.")
        if not site.buffer(1e-9).covers(shape):
            raise ValueError("Keep every study zone inside the saved site boundary.")
        label = zone.label.strip()
        if not label:
            raise ValueError("Give each zone a label.")
        shapes.append(shape)
        properties = {"label": label, "color": zone.color, "origin": zone.origin}
        if zone.district is not None:
            if zone.custom:
                raise ValueError("A custom zone cannot also claim a Calgary district.")
            properties["district"] = zone.district.model_dump(exclude_none=True)
        if zone.custom:
            properties["custom"] = True
        features.append({"type": "Feature", "id": zone.id, "geometry": mapping(shape), "properties": properties})
    warnings = ["Student-authored graphic; consult official district data for statutory zoning."]
    if shapes:
        union = unary_union(shapes)
        if sum(shape.area for shape in shapes) - union.area > site.area * .0001:
            warnings.append("Some study zones overlap. Their colours stack in drawing order.")
    collection = {"type": "FeatureCollection", "features": features, "_citypromptStudy": {
        "schema": 1, "condition": condition, "boundaryId": str(request.boundary_id),
        "boundaryCoordinates": request.boundary_coordinates,
        "updatedAt": datetime.now(timezone.utc).isoformat(),
    }}
    encoded = json.dumps(collection, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    if len(encoded) > 2 * 1024 * 1024:
        raise ValueError("Use a smaller study; each layer supports up to 2 MB.")
    return collection, len(encoded), hashlib.sha256(encoded).hexdigest(), warnings


@router.put("/projects/{project_id}/{condition}", response_model=ReferenceLayerResponse)
async def save_zoning_study(
    project_id: uuid.UUID, condition: Condition, request: StudyRequest,
    user: User = Depends(require_auth), db: AsyncSession = Depends(get_db),
):
    await check_project_permission(project_id, user, db, required="editor")
    await db.execute(select(Project.id).where(Project.id == project_id).with_for_update())
    boundary = (await db.execute(select(SiteZone).where(SiteZone.id == request.boundary_id)
                                 .with_for_update())).scalar_one_or_none()
    if boundary is None or boundary.project_id != project_id or boundary.zone_type != "site_boundary" or not boundary.is_active_boundary:
        raise HTTPException(409, "The active site changed. Reopen the study using the current boundary.")
    site = to_shape(boundary.geometry)
    submitted = Polygon(request.boundary_coordinates)
    if not submitted.is_valid or not site.equals(submitted):
        raise HTTPException(409, "Wait for the site boundary to finish saving, then reopen the study.")
    filename = f"cityprompt-zoning-study-{condition}.geojson"
    layers = (await db.execute(select(ReferenceLayer).where(ReferenceLayer.project_id == project_id).with_for_update())).scalars().all()
    managed = [layer for layer in layers if layer.source_filename == filename
               and layer.feature_collection.get("_citypromptStudy", {}).get("condition") == condition]
    if len(managed) > 1:
        raise HTTPException(409, "This study has duplicate layers. Review the map layers before saving.")
    layer = managed[0] if managed else None
    if (layer.content_hash if layer else None) != request.expected_hash:
        raise HTTPException(409, "The shared study changed or was removed. Your draft is kept; reload the shared version to review it.")
    try:
        collection, size, digest, warnings = await run_in_threadpool(study_collection, request, condition, site)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    if (layer is None and len(layers) >= 20) or sum(row.storage_bytes for row in layers if row is not layer) + size > 12 * 1024 * 1024:
        raise HTTPException(409, "The project supports 20 map layers and 12 MB of reference data. Use a smaller study.")
    if layer is None:
        layer = ReferenceLayer(project_id=project_id, created_by=user.id)
        db.add(layer)
    layer.name = "Draft bylaw · May 2025 study" if condition == "draft-2025" else "Existing zoning study" if condition == "existing" else "Proposed land-use study"
    layer.kind = "zoning"
    layer.source_filename = filename
    layer.source_crs = "EPSG:4326"
    layer.source_url = "https://data.calgary.ca/Base-Maps/Land-Use-Districts/qe6k-p9nh" if any(zone.origin == "calgary-extract" or zone.district is not None for zone in request.zones) else None
    if condition == "draft-2025":
        layer.source_url = DRAFT_SOURCE
        warnings.append("May 2025 discussion draft; illustrative student colours, not statutory zoning or a compliance assessment.")
    layer.description = "Editable student graphic. Existing and proposed conditions are separate; official zoning and project drawings remain independent."
    layer.feature_collection = collection
    layer.feature_count = len(request.zones)
    layer.storage_bytes = size
    layer.content_hash = digest
    layer.bounds = list(site.bounds)
    layer.warnings = warnings
    layer.color = "#8b5e3c" if condition == "existing" else "#315f73"
    layer.opacity = request.opacity
    await db.flush()
    await db.refresh(layer)
    return layer
