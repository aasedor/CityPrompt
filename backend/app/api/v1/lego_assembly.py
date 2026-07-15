"""Experimental archetype-driven modular building assembly endpoints."""

from __future__ import annotations

import hashlib
import json
import uuid
from typing import Any

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from pydantic import BaseModel, Field
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified

from app.core.database import get_db
from app.core.security import require_auth
from app.models.models import Building, ModelLibraryEntry, Project, ProjectShare, SiteZone, User
from app.services.lego_assembly import (
    AssemblyPlanningError,
    AssemblyRequest,
    descriptor_from_library_entry,
    find_family_module_entry,
    lego_metadata_from_manifest,
    manifest_validation_errors,
    plan_vertical_assembly,
)

router = APIRouter()

# Namespaced key inside Building.specifications so recipes coexist with the
# existing model_url workflow fields without a schema migration.
RECIPE_SPEC_KEY = "legoAssembly"

_LEGO_CATEGORY = "lego_module"
_LEGO_ENGINE = "compiler"  # generation_engine is String(20) — keep short
_TAG_REUSE_KEY_LIMIT = 3
# Compiler modules are ~50-150 KB; anything near this cap is the wrong file.
_MAX_UPLOAD_BYTES = 75 * 1024 * 1024


class LegoAssemblyPlanRequest(BaseModel):
    target_width_m: float = Field(gt=0)
    target_depth_m: float = Field(gt=0)
    target_floors: int = Field(ge=1, le=100)
    archetype_id: str | None = None
    reuse_keys: list[str] = Field(default_factory=list)
    preferred_family: str | None = None
    allow_setback: bool = True


class LegoRecipeTarget(BaseModel):
    width_m: float = Field(gt=0)
    depth_m: float = Field(gt=0)
    floors: int = Field(ge=1)


class LegoRecipeRequest(BaseModel):
    """A saved assembly recipe — the persisted twin of ``POST /plan`` output."""

    schema_version: int = 1
    module_family: str = Field(min_length=1)
    archetype_id: str | None = None
    reuse_keys: list[str] = Field(default_factory=list)
    target: LegoRecipeTarget
    instances: list[dict[str, Any]]
    assembled_height_m: float | None = None
    fit: dict[str, Any] | None = None
    assembled_preview_url: str | None = None


class LegoPlaceRequest(LegoRecipeRequest):
    """Recipe payload for "Place": saved like /recipes, but zone-addressed so a
    zone without a generated building gets one created and linked first."""

    building_name: str | None = Field(default=None, max_length=255)


class LegoModuleMetadataRequest(BaseModel):
    role: str = Field(pattern="^(podium|floor|setback|roof|attachment)$")
    family: str = Field(min_length=1, max_length=100)
    width_m: float = Field(gt=0)
    depth_m: float = Field(gt=0)
    height_m: float = Field(gt=0)
    repeatable_z: bool = False
    archetype_ids: list[str] = Field(default_factory=list)
    reuse_keys: list[str] = Field(default_factory=list)
    min_floors: int | None = Field(default=None, ge=1)
    max_floors: int | None = Field(default=None, ge=1)


async def _accessible_entries(db: AsyncSession, user: User) -> list[ModelLibraryEntry]:
    result = await db.execute(
        select(ModelLibraryEntry)
        .where(
            or_(
                ModelLibraryEntry.owner_id == user.id,
                ModelLibraryEntry.is_public.is_(True),
            )
        )
        .order_by(ModelLibraryEntry.created_at.desc())
    )
    return list(result.scalars().all())


@router.get("/modules")
async def list_lego_modules(
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """List model-library items currently configured as LEGO modules."""
    descriptors = []
    for entry in await _accessible_entries(db, user):
        descriptor = descriptor_from_library_entry(entry)
        if descriptor:
            descriptors.append(
                {
                    "id": descriptor.id,
                    "name": descriptor.name,
                    "model_url": descriptor.model_url,
                    "family": descriptor.family,
                    "role": descriptor.role,
                    "width_m": descriptor.width_m,
                    "depth_m": descriptor.depth_m,
                    "height_m": descriptor.height_m,
                    "archetype_ids": list(descriptor.archetype_ids),
                    "reuse_keys": list(descriptor.reuse_keys),
                    "min_floors": descriptor.min_floors,
                    "max_floors": descriptor.max_floors,
                    "repeatable_z": descriptor.repeatable_z,
                }
            )
    return {"modules": descriptors, "count": len(descriptors)}


@router.put("/modules/{item_id}")
async def configure_lego_module(
    item_id: str,
    body: LegoModuleMetadataRequest,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Mark an existing model-library item as a modular building component."""
    result = await db.execute(
        select(ModelLibraryEntry).where(ModelLibraryEntry.id == item_id)
    )
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=404, detail="Model-library item not found")
    if entry.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Only the asset owner can configure it")

    if body.min_floors and body.max_floors and body.min_floors > body.max_floors:
        raise HTTPException(status_code=400, detail="min_floors cannot exceed max_floors")

    metadata = dict(entry.metadata_ or {})
    metadata["lego"] = {
        "enabled": True,
        "role": body.role,
        "family": body.family,
        "width_m": body.width_m,
        "depth_m": body.depth_m,
        "height_m": body.height_m,
        "repeatable_z": body.repeatable_z or body.role == "floor",
        "archetype_ids": body.archetype_ids,
        "reuse_keys": body.reuse_keys,
        "min_floors": body.min_floors,
        "max_floors": body.max_floors,
    }
    entry.metadata_ = metadata
    await db.flush()

    return {
        "status": "configured",
        "item_id": str(entry.id),
        "lego": metadata["lego"],
    }


@router.delete("/modules/{item_id}")
async def remove_lego_module_configuration(
    item_id: str,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    """Remove LEGO metadata without deleting the underlying library asset."""
    result = await db.execute(
        select(ModelLibraryEntry).where(ModelLibraryEntry.id == item_id)
    )
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=404, detail="Model-library item not found")
    if entry.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Only the asset owner can configure it")

    metadata = dict(entry.metadata_ or {})
    metadata.pop("lego", None)
    entry.metadata_ = metadata or None
    await db.flush()
    return {"status": "removed", "item_id": str(entry.id)}


@router.post("/plan")
async def create_lego_assembly_plan(
    body: LegoAssemblyPlanRequest,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Create a renderer-neutral vertical assembly recipe.

    ``archetype_id`` and ``reuse_keys`` are designed to be passed directly from
    the existing Urban Intelligence DNA ``generation_style_input`` object.
    """
    descriptors = [
        descriptor
        for entry in await _accessible_entries(db, user)
        if (descriptor := descriptor_from_library_entry(entry)) is not None
    ]

    try:
        return plan_vertical_assembly(
            descriptors,
            AssemblyRequest(
                target_width_m=body.target_width_m,
                target_depth_m=body.target_depth_m,
                target_floors=body.target_floors,
                archetype_id=body.archetype_id,
                reuse_keys=tuple(body.reuse_keys),
                preferred_family=body.preferred_family,
                allow_setback=body.allow_setback,
            ),
        )
    except AssemblyPlanningError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


# ---------------------------------------------------------------------------
# Compiler-manifest import
# ---------------------------------------------------------------------------


def _basename(filename: str) -> str:
    """Normalize an uploaded filename to its final path component."""
    return filename.replace("\\", "/").rsplit("/", 1)[-1]


def _module_storage_key(user_id: Any, family: str, role: str) -> str:
    """Deterministic storage key so re-imports overwrite the same object."""
    return f"library/lego/{user_id}/{family}/{role}.glb"


async def _parse_json_upload(upload: UploadFile, label: str) -> Any:
    raw = await upload.read()
    try:
        return json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise HTTPException(status_code=400, detail=f"{label} is not valid JSON: {exc}") from exc


@router.post("/import-manifest")
async def import_compiler_manifest(
    manifest: UploadFile = File(..., description="The *_manifest.json written by blender_generate.py"),
    files: list[UploadFile] = File(..., description="Module GLBs (and optionally the assembled GLB)"),
    thumbnail: UploadFile | None = File(default=None, description="Preview PNG for the family"),
    validation_report: UploadFile | None = File(default=None, description="validation_report.json"),
    force: bool = Query(default=False, description="Import even if the validation report did not pass"),
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Import a compiled archetype family into the model library as LEGO modules.

    One request ingests the whole output folder of ``generate_family.py``:
    every manifest module whose GLB was uploaded becomes (or refreshes) a
    ``ModelLibraryEntry`` with planner-ready ``metadata_["lego"]``. The
    pre-assembled preview GLB is stored too, but with ``enabled: false``.
    """
    manifest_data = await _parse_json_upload(manifest, "manifest")
    errors = manifest_validation_errors(manifest_data)
    if errors:
        raise HTTPException(status_code=400, detail="Invalid manifest: " + "; ".join(errors))

    validation_status = "unknown"
    if validation_report is not None:
        report_data = await _parse_json_upload(validation_report, "validation_report")
        validation_status = str((report_data or {}).get("status") or "unknown") if isinstance(report_data, dict) else "unknown"
        if validation_status != "pass" and not force:
            raise HTTPException(
                status_code=422,
                detail=(
                    f"validation_report status is '{validation_status}' (expected 'pass'). "
                    "Re-run validate_outputs.py, or retry with ?force=true to import anyway."
                ),
            )

    family = str(manifest_data["family"]).strip()
    archetype_id = str(manifest_data["archetype_id"]).strip()
    label = str(manifest_data.get("archetype_label") or "").strip() or family
    generator = manifest_data.get("generator") or {}
    generation_prompt = (
        f"Procedural module generated by {generator.get('name') or 'archetype_compiler'} "
        f"v{generator.get('version') or 'unknown'} from archetype {archetype_id}"
    )
    aesthetic_category_id = manifest_data.get("aesthetic_category_id")
    architectural_style = str(aesthetic_category_id)[:50] if aesthetic_category_id else None
    reuse_keys = [str(k) for k in (manifest_data.get("reuse_keys") or []) if str(k or "").strip()]

    uploads: dict[str, bytes] = {}
    for upload in files:
        if not upload.filename:
            continue
        data = await upload.read()
        if len(data) > _MAX_UPLOAD_BYTES:
            raise HTTPException(
                status_code=413,
                detail=(
                    f"{_basename(upload.filename)} is {len(data) / 1_048_576:.0f} MB; "
                    f"module GLBs are capped at {_MAX_UPLOAD_BYTES // 1_048_576} MB per file"
                ),
            )
        uploads[_basename(upload.filename)] = data

    # Storage helpers live in the Celery module; deferred import matches the
    # codebase convention (see admin.py, model_cache.py) and keeps tests free
    # to monkeypatch app.tasks.processing._upload_to_storage.
    from app.tasks.processing import _file_proxy_url, _upload_to_storage

    existing_result = await db.execute(
        select(ModelLibraryEntry).where(ModelLibraryEntry.owner_id == user.id)
    )
    existing_entries = list(existing_result.scalars().all())

    thumbnail_url: str | None = None
    if thumbnail is not None:
        thumb_key = f"library/lego/{user.id}/{family}/preview.png"
        thumb_data = await thumbnail.read()
        _upload_to_storage(thumb_key, thumb_data, "image/png")
        thumb_version = hashlib.sha256(thumb_data).hexdigest()[:12]
        thumbnail_url = f"{_file_proxy_url(thumb_key)}?v={thumb_version}"

    # Importable units: manifest modules plus the pre-assembled preview GLB
    # (synthesized as a pseudo-module so it lands in the library disabled).
    units: list[tuple[str, dict[str, Any]]] = [
        (str(module.get("role") or "").strip().lower(), dict(module))
        for module in manifest_data["modules"]
    ]
    assembled = manifest_data.get("assembled") or {}
    if assembled.get("filename"):
        dimensions = manifest_data.get("dimensions") or {}
        units.append(
            (
                "assembled",
                {
                    "role": "assembled",
                    "filename": assembled["filename"],
                    "width_m": dimensions.get("width_m"),
                    "depth_m": dimensions.get("depth_m"),
                    "height_m": assembled.get("height_m"),
                    "floor_height_m": dimensions.get("floor_height_m"),
                    "repeatable_z": False,
                    "triangle_count": assembled.get("triangle_count"),
                    "material_count": None,
                },
            )
        )

    imported: list[dict[str, Any]] = []
    matched_filenames: set[str] = set()

    for role, module in units:
        filename = _basename(str(module.get("filename") or ""))
        if filename not in uploads:
            continue
        matched_filenames.add(filename)

        key = _module_storage_key(user.id, family, role)
        module_bytes = uploads[filename]
        _upload_to_storage(key, module_bytes, "model/gltf-binary")
        content_hash = hashlib.sha256(module_bytes).hexdigest()
        model_url = f"{_file_proxy_url(key)}?v={content_hash[:12]}"

        lego_metadata = lego_metadata_from_manifest(
            manifest_data, module, role=role, validation_status=validation_status
        )
        lego_metadata["content_hash"] = content_hash
        name = f"{label} — {role}"[:255]
        tags = [family, role, *reuse_keys[:_TAG_REUSE_KEY_LIMIT]]

        entry = find_family_module_entry(existing_entries, family, role)
        if entry is not None:
            entry.name = name
            entry.category = _LEGO_CATEGORY
            entry.tags = tags
            entry.model_url = model_url
            entry.generation_prompt = generation_prompt
            entry.generation_engine = _LEGO_ENGINE
            entry.architectural_style = architectural_style
            if thumbnail_url:
                entry.thumbnail_url = thumbnail_url
            metadata = dict(entry.metadata_ or {})
            metadata["lego"] = lego_metadata
            entry.metadata_ = metadata
            action = "updated"
        else:
            entry = ModelLibraryEntry(
                id=uuid.uuid4(),
                owner_id=user.id,
                name=name,
                category=_LEGO_CATEGORY,
                tags=tags,
                model_url=model_url,
                thumbnail_url=thumbnail_url,
                generation_prompt=generation_prompt,
                generation_engine=_LEGO_ENGINE,
                architectural_style=architectural_style,
                is_public=False,
                metadata_={"lego": lego_metadata},
            )
            db.add(entry)
            existing_entries.append(entry)
            action = "created"

        imported.append(
            {"id": str(entry.id), "role": role, "action": action, "model_url": model_url}
        )

    if not imported:
        expected = sorted(_basename(str(m.get("filename") or "")) for _, m in units)
        raise HTTPException(
            status_code=400,
            detail=(
                "No uploaded files matched the manifest module filenames. "
                f"Expected any of: {', '.join(expected)}"
            ),
        )

    # A new preview refreshes every entry of the family, including modules not
    # re-uploaded in this request.
    if thumbnail_url:
        for entry in existing_entries:
            lego = (getattr(entry, "metadata_", None) or {}).get("lego") or {}
            if lego.get("family") == family:
                entry.thumbnail_url = thumbnail_url

    await db.flush()

    return {
        "family": family,
        "archetype_id": archetype_id,
        "imported": imported,
        "skipped": sorted(set(uploads) - matched_filenames),
    }


# ---------------------------------------------------------------------------
# Recipe persistence (Building.specifications["legoAssembly"])
# ---------------------------------------------------------------------------


async def _get_building_with_access(
    db: AsyncSession,
    building_id: uuid.UUID,
    user: User,
    *,
    require_editor: bool,
) -> Building:
    """Fetch a building and authorize project access.

    Mirrors the ownership/share checks in ``buildings.py::update_building`` so
    project editors can save recipes. Read access accepts any share.
    """
    result = await db.execute(select(Building).where(Building.id == building_id))
    building = result.scalar_one_or_none()
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")

    proj_result = await db.execute(select(Project).where(Project.id == building.project_id))
    project = proj_result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project.owner_id != user.id:
        conditions = [
            ProjectShare.project_id == building.project_id,
            (ProjectShare.user_id == user.id) | (ProjectShare.email == user.email),
        ]
        if require_editor:
            conditions.append(ProjectShare.permission == "editor")
        share_result = await db.execute(select(ProjectShare).where(*conditions))
        if not share_result.scalar_one_or_none():
            raise HTTPException(
                status_code=403,
                detail="Not authorized to edit buildings in this project"
                if require_editor
                else "Not authorized to view buildings in this project",
            )
    return building


async def _get_zone_with_access(
    db: AsyncSession,
    zone_id: uuid.UUID,
    user: User,
    *,
    require_editor: bool,
) -> SiteZone:
    """Fetch a zone and authorize project access (same policy as buildings)."""
    result = await db.execute(select(SiteZone).where(SiteZone.id == zone_id))
    zone = result.scalar_one_or_none()
    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")

    proj_result = await db.execute(select(Project).where(Project.id == zone.project_id))
    project = proj_result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project.owner_id != user.id:
        conditions = [
            ProjectShare.project_id == zone.project_id,
            (ProjectShare.user_id == user.id) | (ProjectShare.email == user.email),
        ]
        if require_editor:
            conditions.append(ProjectShare.permission == "editor")
        share_result = await db.execute(select(ProjectShare).where(*conditions))
        if not share_result.scalar_one_or_none():
            raise HTTPException(
                status_code=403,
                detail="Not authorized to edit zones in this project"
                if require_editor
                else "Not authorized to view zones in this project",
            )
    return zone


@router.post("/place/{zone_id}")
async def place_lego_assembly(
    zone_id: uuid.UUID,
    body: LegoPlaceRequest,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Place an assembled LEGO recipe on a zone.

    Ensures the zone has a linked ``Building`` (created from the zone's own
    geometry when generate-all never ran), then saves the recipe into
    ``Building.specifications["legoAssembly"]`` exactly like ``POST /recipes``.
    The globe layer picks the recipe up from the refetched project and swaps
    the zone's coloured polygon for the module stack.

    Multi-unit zones (``building_ids`` with several entries) place onto the
    primary ``building_id`` — one stack per zone is the v1 contract.
    """
    zone = await _get_zone_with_access(db, zone_id, user, require_editor=True)

    building: Building | None = None
    if zone.building_id is not None:
        result = await db.execute(select(Building).where(Building.id == zone.building_id))
        building = result.scalar_one_or_none()

    created = False
    if building is None:
        building = Building(
            id=uuid.uuid4(),  # assigned here, not at flush: the response needs it
            project_id=zone.project_id,
            name=(body.building_name or zone.name or body.archetype_id or "LEGO Building")[:255],
            footprint=zone.geometry,
            floor_count=body.target.floors,
            height_meters=body.assembled_height_m,
            specifications={},
        )
        db.add(building)
        zone.building_id = building.id
        zone.building_ids = [str(building.id)]
        created = True
    else:
        # The globe stack cannot mount without a footprint ring; a building
        # made by older flows may not have one — the zone polygon is the
        # honest footprint in that case.
        if building.footprint is None:
            building.footprint = zone.geometry
        if building.floor_count is None:
            building.floor_count = body.target.floors

    specifications = dict(building.specifications or {})
    specifications[RECIPE_SPEC_KEY] = body.model_dump(exclude={"building_name"})
    specifications["lego_placed"] = True
    building.specifications = specifications
    flag_modified(building, "specifications")
    await db.flush()

    return {
        "status": "placed",
        "zone_id": str(zone.id),
        "building_id": str(building.id),
        "building_created": created,
        RECIPE_SPEC_KEY: specifications[RECIPE_SPEC_KEY],
    }


@router.post("/recipes/{building_id}")
async def save_lego_recipe(
    building_id: uuid.UUID,
    body: LegoRecipeRequest,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Persist an assembly recipe on the building, namespaced so the existing
    model_url workflow fields in ``specifications`` stay untouched."""
    building = await _get_building_with_access(db, building_id, user, require_editor=True)

    specifications = dict(building.specifications or {})
    specifications[RECIPE_SPEC_KEY] = body.model_dump()
    building.specifications = specifications
    flag_modified(building, "specifications")
    await db.flush()

    return {
        "status": "saved",
        "building_id": str(building.id),
        RECIPE_SPEC_KEY: specifications[RECIPE_SPEC_KEY],
    }


@router.get("/recipes/{building_id}")
async def get_lego_recipe(
    building_id: uuid.UUID,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Return the saved recipe for a building (or None if none saved)."""
    building = await _get_building_with_access(db, building_id, user, require_editor=False)
    specifications = building.specifications or {}
    return {RECIPE_SPEC_KEY: specifications.get(RECIPE_SPEC_KEY)}


@router.delete("/recipes/{building_id}")
async def delete_lego_recipe(
    building_id: uuid.UUID,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Remove only the recipe key; the rest of specifications stays intact."""
    building = await _get_building_with_access(db, building_id, user, require_editor=True)

    specifications = dict(building.specifications or {})
    removed = specifications.pop(RECIPE_SPEC_KEY, None) is not None
    specifications.pop("lego_placed", None)  # stamp follows the recipe's lifecycle
    building.specifications = specifications
    flag_modified(building, "specifications")
    await db.flush()

    return {"status": "removed" if removed else "absent", "building_id": str(building.id)}
