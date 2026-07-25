"""Experimental archetype-driven modular building assembly endpoints."""

from __future__ import annotations

import hashlib
import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Literal

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from geoalchemy2.shape import from_shape, to_shape
from pydantic import BaseModel, Field
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified

from app.core.database import get_db
from app.core.security import require_auth
from app.models.models import Building, ModelLibraryEntry, Project, ProjectShare, SiteZone, User
from app.services.community_3d_artifacts import (
    COMMUNITY_REPRESENTATION_SPEC_KEY,
    stale_community_3d_buildings,
)
from app.services.lego_assembly import (
    AssemblyPlanningError,
    AssemblyRequest,
    descriptor_from_library_entry,
    find_family_module_entry,
    lego_metadata_from_manifest,
    manifest_validation_errors,
    plan_vertical_assembly,
)
from app.services.master_planner.lego_catalog import build_lego_planning_catalog
from app.services.public_realm_lego import (
    PUBLIC_REALM_RECIPE_PROPERTY,
    PublicRealmPlanningError,
    plan_public_realm_zone_recipe,
)
from app.services.residual_landscape import (
    ResidualSourceZone,
    build_residual_landscape_recipe,
    community_3d_kind_for_source,
    community_3d_representation_hash,
    community_3d_source_hash,
    derive_site_boundary_from_authored_zones,
    lock_residual_landscape_project,
    mark_linked_community_3d_stale,
)

router = APIRouter()
logger = logging.getLogger(__name__)

# Namespaced key inside Building.specifications so recipes coexist with the
# existing model_url workflow fields without a schema migration.
RECIPE_SPEC_KEY = "legoAssembly"
PLANNED_MASSING_SPEC_KEY = "plannedMassing"

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
    footprint_profile: Literal["rectangle", "l_shape", "u_shape", "courtyard"] = "rectangle"
    wing_depth_m: float | None = Field(default=None, gt=0)
    # When planning for a shared project, use the same owner-visible private
    # module inventory that the AI Master Planner used for that project.
    project_id: uuid.UUID | None = None


class LegoRecipeTarget(BaseModel):
    width_m: float = Field(gt=0)
    depth_m: float = Field(gt=0)
    floors: int = Field(ge=1)
    footprint_profile: Literal["rectangle", "l_shape", "u_shape", "courtyard"] = "rectangle"
    wing_depth_m: float | None = Field(default=None, gt=0)


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
    # AI Master Planner zones carry the exact executable catalogue revision
    # used to bind their archetype and geometry.  Manual recipes omit this
    # optional token and retain the historical save/place contract.
    catalog_fingerprint: str | None = Field(
        default=None,
        pattern=r"^[a-fA-F0-9]{64}$",
    )


class LegoPlaceRequest(LegoRecipeRequest):
    """Recipe payload for "Place": saved like /recipes, but zone-addressed so a
    zone without a generated building gets one created and linked first."""

    building_name: str | None = Field(default=None, max_length=255)


class Community3DCompileItem(BaseModel):
    """One planner zone participating in an atomic Community 3D build."""

    zone_id: uuid.UUID
    # Optimistic concurrency token from the exact zone snapshot used by the
    # browser to derive footprint dimensions, floors and archetype selection.
    # It is rechecked only after the project row lock is held, so a same-kind
    # edit in another tab cannot receive a recipe planned from stale geometry.
    source_updated_at: datetime
    # Supported buildings carry an assembly recipe. An unsupported building
    # intentionally omits it and becomes persisted exact-footprint massing.
    # Deterministic ground systems also derive from the zone and omit it.
    recipe: LegoPlaceRequest | None = None


class Community3DCompileRequest(BaseModel):
    # District plans can legitimately contain hundreds of buildings plus
    # public-realm zones. Keep the atomic all-or-nothing contract for a full
    # master plan instead of forcing large communities into partial batches.
    items: list[Community3DCompileItem] = Field(min_length=1, max_length=2000)


def _same_source_revision(client_revision: datetime, server_revision: datetime | None) -> bool:
    """Compare API and database timestamps without relying on ISO spelling.

    PostgreSQL returns timezone-aware values while a few historical SQLite
    fixtures return naive UTC datetimes. Pydantic also accepts either ``Z`` or
    ``+00:00`` from the browser, so normalize all three representations before
    the optimistic-concurrency comparison.
    """
    if server_revision is None:
        return False

    def utc(value: datetime) -> datetime:
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    return utc(client_revision) == utc(server_revision)


def _zone_lego_catalog_fingerprint(zone: SiteZone) -> str | None:
    """Return the AI binder's catalogue token, rejecting corrupt stamps.

    The field is deliberately opt-in: hand-authored zones and legacy manual
    LEGO recipes have no stamp and continue through their existing workflow.
    """
    value = (zone.properties or {}).get("_lego_catalog_fingerprint")
    if value is None:
        return None
    if not isinstance(value, str) or len(value) != 64:
        raise HTTPException(
            status_code=409,
            detail=(
                "This AI Master Plan has an invalid LEGO catalogue revision; "
                "regenerate the plan before compiling Community 3D."
            ),
        )
    try:
        int(value, 16)
    except ValueError as exc:
        raise HTTPException(
            status_code=409,
            detail=(
                "This AI Master Plan has an invalid LEGO catalogue revision; "
                "regenerate the plan before compiling Community 3D."
            ),
        ) from exc
    return value.lower()


async def _assert_ai_lego_recipes_are_current(
    db: AsyncSession,
    user: User,
    project_id: uuid.UUID,
    resolved_items: list[
        tuple[Community3DCompileItem, SiteZone, Literal["building", "park", "street"]]
    ],
) -> None:
    """Fail closed when an AI recipe no longer matches its locked inventory.

    Catalogue binding and browser-side assembly planning are separate requests.
    This check runs only after the project mutation lock is held and before any
    derived Building is changed.  It protects both gaps: the catalogue token
    proves that the advertised family/floor vocabulary is unchanged, while a
    fresh server-side plan proves that the exact module IDs, URLs, dimensions,
    and stack geometry in the submitted recipe still match current rows.
    """
    protected: list[tuple[Community3DCompileItem, SiteZone, str]] = []
    for item, zone, kind in resolved_items:
        if kind != "building":
            continue
        expected_fingerprint = _zone_lego_catalog_fingerprint(zone)
        if expected_fingerprint is None:
            continue
        if item.recipe is None or item.recipe.catalog_fingerprint is None:
            raise HTTPException(
                status_code=409,
                detail=(
                    "An AI Master Plan building is missing its LEGO catalogue revision; "
                    "refresh the project and prepare Community 3D again."
                ),
            )
        if item.recipe.catalog_fingerprint.lower() != expected_fingerprint:
            raise HTTPException(
                status_code=409,
                detail=(
                    "An AI Master Plan building recipe came from a different LEGO catalogue; "
                    "refresh the project and prepare Community 3D again."
                ),
            )
        protected.append((item, zone, expected_fingerprint))

    if not protected:
        return

    entries = await _accessible_entries(
        db,
        user,
        project_id,
        lock_for_update=True,
    )
    current_catalog = build_lego_planning_catalog(entries)
    stale_catalog = next(
        (
            (zone, expected)
            for _, zone, expected in protected
            if expected != current_catalog.fingerprint
        ),
        None,
    )
    if stale_catalog is not None:
        raise HTTPException(
            status_code=409,
            detail=(
                "The executable LEGO catalogue changed after this AI Master Plan was created; "
                "regenerate the plan before compiling Community 3D."
            ),
        )

    descriptors = [
        descriptor
        for entry in entries
        if (descriptor := descriptor_from_library_entry(entry)) is not None
    ]
    for item, _, _ in protected:
        recipe = item.recipe
        assert recipe is not None  # established above; keeps type narrowing explicit
        try:
            current_plan = plan_vertical_assembly(
                descriptors,
                AssemblyRequest(
                    target_width_m=recipe.target.width_m,
                    target_depth_m=recipe.target.depth_m,
                    target_floors=recipe.target.floors,
                    archetype_id=recipe.archetype_id,
                    reuse_keys=tuple(recipe.reuse_keys),
                    footprint_profile=recipe.target.footprint_profile,
                    wing_depth_m=recipe.target.wing_depth_m,
                    # The AI binder and browser compiler deliberately disable
                    # optional setback modules. The locked re-plan must use
                    # that same deterministic policy.
                    allow_setback=False,
                ),
            )
        except AssemblyPlanningError as exc:
            raise HTTPException(
                status_code=409,
                detail=(
                    "A LEGO family used by this AI Master Plan is no longer executable; "
                    "regenerate the plan before compiling Community 3D."
                ),
            ) from exc

        if (
            current_plan["family"] != recipe.module_family
            or current_plan["instances"] != recipe.instances
            or current_plan["assembled_height_m"] != recipe.assembled_height_m
            or current_plan["fit"] != recipe.fit
        ):
            raise HTTPException(
                status_code=409,
                detail=(
                    "The LEGO modules used by this AI Master Plan changed while its 3D "
                    "recipes were being prepared; refresh and retry."
                ),
            )


class LegoModuleMetadataRequest(BaseModel):
    role: str = Field(pattern="^(podium|floor|setback|crown|roof|attachment|assembled)$")
    family: str = Field(min_length=1, max_length=100)
    width_m: float = Field(gt=0)
    depth_m: float = Field(gt=0)
    height_m: float = Field(gt=0)
    repeatable_z: bool = False
    archetype_ids: list[str] = Field(default_factory=list)
    reuse_keys: list[str] = Field(default_factory=list)
    min_floors: int | None = Field(default=None, ge=1)
    max_floors: int | None = Field(default=None, ge=1)
    setback_min_floors: int | None = Field(default=None, ge=2)
    variant_key: str = Field(default="default", pattern="^[a-z0-9][a-z0-9_]{0,49}$")
    lod: int = Field(default=0, ge=0)
    allowed_levels: list[int] = Field(default_factory=list)


async def _accessible_entries(
    db: AsyncSession,
    user: User,
    project_id: uuid.UUID | None = None,
    *,
    lock_for_update: bool = False,
) -> list[ModelLibraryEntry]:
    # Without project context the caller's private library is the expected
    # workspace.  A project-scoped plan must instead use exactly the inventory
    # that the background Master Planner sees: project-owner private modules
    # plus public modules.  Including an editor's unrelated private library
    # would let the browser select a different family from the one preflighted
    # and persisted by the AI plan task.
    owner_ids = {user.id}
    if project_id is not None:
        project_result = await db.execute(
            select(Project).where(Project.id == project_id)
        )
        project = project_result.scalar_one_or_none()
        if project is None:
            raise HTTPException(status_code=404, detail="Project not found")
        if project.owner_id != user.id:
            share_result = await db.execute(
                select(ProjectShare).where(
                    ProjectShare.project_id == project_id,
                    (ProjectShare.user_id == user.id)
                    | (ProjectShare.email == user.email),
                )
            )
            if share_result.scalar_one_or_none() is None:
                raise HTTPException(status_code=403, detail="Not authorized")
        owner_ids = {project.owner_id}

    query = (
        select(ModelLibraryEntry)
        .where(
            or_(
                ModelLibraryEntry.owner_id.in_(owner_ids),
                ModelLibraryEntry.is_public.is_(True),
            )
        )
        .order_by(ModelLibraryEntry.created_at.desc(), ModelLibraryEntry.id.desc())
    )
    if lock_for_update:
        # Community compilation persists URLs and dimensions from these rows.
        # Hold the selected inventory stable until the request transaction
        # commits, so a concurrent re-import/configuration cannot land between
        # freshness validation and Building persistence.
        query = query.with_for_update()
    result = await db.execute(query)
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
                    "setback_min_floors": descriptor.setback_min_floors,
                    "repeatable_z": descriptor.repeatable_z,
                    "variant_key": descriptor.variant_key,
                    "lod": descriptor.lod,
                    "allowed_levels": list(descriptor.allowed_levels),
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
        "setback_min_floors": body.setback_min_floors,
        "variant_key": body.variant_key,
        "lod": body.lod,
        "allowed_levels": body.allowed_levels,
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
        for entry in await _accessible_entries(db, user, body.project_id)
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
                footprint_profile=body.footprint_profile,
                wing_depth_m=body.wing_depth_m,
            ),
        )
    except AssemblyPlanningError as exc:
        detail: dict[str, Any] = {
            "code": exc.code,
            "message": str(exc),
        }
        if exc.requested is not None:
            detail["requested"] = exc.requested
        if exc.supported_families is not None:
            detail["supported_families"] = exc.supported_families
        raise HTTPException(status_code=422, detail=detail) from exc


# ---------------------------------------------------------------------------
# Compiler-manifest import
# ---------------------------------------------------------------------------


def _basename(filename: str) -> str:
    """Normalize an uploaded filename to its final path component."""
    return filename.replace("\\", "/").rsplit("/", 1)[-1]


def _module_storage_key(
    user_id: Any,
    family: str,
    role: str,
    variant_key: str = "default",
    lod: int = 0,
) -> str:
    """Deterministic storage key so re-imports overwrite the same object."""
    return f"library/lego/{user_id}/{family}/{role}--{variant_key}--lod{lod}.glb"


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
                    "native_floors": assembled.get("floors"),
                    "floor_height_m": dimensions.get("floor_height_m"),
                    "repeatable_z": False,
                    "variant_key": "default",
                    "lod": 0,
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

        variant_key = str(module.get("variant_key") or "default")
        lod = max(0, int(module.get("lod") or 0))
        key = _module_storage_key(user.id, family, role, variant_key, lod)
        module_bytes = uploads[filename]
        _upload_to_storage(key, module_bytes, "model/gltf-binary")
        content_hash = hashlib.sha256(module_bytes).hexdigest()
        model_url = f"{_file_proxy_url(key)}?v={content_hash[:12]}"

        lego_metadata = lego_metadata_from_manifest(
            manifest_data, module, role=role, validation_status=validation_status
        )
        lego_metadata["content_hash"] = content_hash
        identity_label = role if variant_key == "default" else f"{role} / {variant_key}"
        name = f"{label} — {identity_label}"[:255]
        tags = [family, role, variant_key, *reuse_keys[:_TAG_REUSE_KEY_LIMIT]]

        entry = find_family_module_entry(existing_entries, family, role, variant_key, lod)
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

        imported.append({
            "id": str(entry.id), "role": role, "variant_key": variant_key,
            "lod": lod, "action": action, "model_url": model_url,
        })

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


def _community_3d_kind(zone: SiteZone) -> Literal["building", "park", "street"] | None:
    """Backend twin of the frontend Community 3D classification contract."""
    return community_3d_kind_for_source(zone.zone_type, zone.properties)


def _community_source_geometry(zone: SiteZone):
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
            raise HTTPException(
                status_code=422,
                detail=f"Zone {zone.id} has unusable Community 3D source geometry",
            ) from exc


def _public_realm_recipe_for_zone(
    zone: SiteZone,
    kind: Literal["park", "street"],
) -> dict[str, Any] | None:
    """Compile a canonical V1 recipe, strict only for AI Master Plan zones."""

    properties = zone.properties or {}
    strict = bool(
        isinstance(properties.get("_plan_scenario"), str)
        and properties.get("_plan_scenario", "").strip()
    )
    try:
        recipe = plan_public_realm_zone_recipe(
            zone.zone_type,
            _community_source_geometry(zone),
            properties,
            strict=strict,
        )
    except PublicRealmPlanningError as exc:
        detail = exc.as_detail()
        detail["zone_id"] = str(zone.id)
        detail["kind"] = kind
        logger.warning(
            "Community 3D public-realm preflight rejected zone %s (%s): %s",
            zone.id,
            kind,
            detail.get("message", detail),
        )
        raise HTTPException(status_code=422, detail=detail) from exc
    except ValueError as exc:
        logger.warning(
            "Community 3D public-realm geometry rejected zone %s (%s): %s",
            zone.id,
            kind,
            exc,
        )
        raise HTTPException(
            status_code=422,
            detail={
                "code": "family_incompatible",
                "message": str(exc),
                "zone_id": str(zone.id),
                "kind": kind,
            },
        ) from exc
    return recipe.model_dump(mode="json") if recipe is not None else None


def _stamp_community_3d(
    zone: SiteZone,
    kind: Literal["building", "park", "street"],
    compiled_at: str,
    building_generator: Literal["lego_assembly", "planned_massing", "meshy"] = "lego_assembly",
    building: Building | None = None,
    public_realm_recipe: dict[str, Any] | None = None,
) -> None:
    generator = {
        "building": building_generator,
        "park": "park_kit",
        "street": "street_section",
    }[kind]
    properties = dict(zone.properties or {})
    if kind in {"park", "street"}:
        if public_realm_recipe is None:
            # A manual legacy archetype may retain the historical procedural
            # representation, but an older V1 recipe must never survive an
            # explicit recompile to a different unsupported selection.
            properties.pop(PUBLIC_REALM_RECIPE_PROPERTY, None)
        else:
            properties[PUBLIC_REALM_RECIPE_PROPERTY] = public_realm_recipe
    source_geometry = _community_source_geometry(zone)
    source_hash = community_3d_source_hash(
        zone.zone_type,
        source_geometry,
        properties,
    )
    representation_hash = community_3d_representation_hash(
        kind=kind,
        generator=generator,
        source_hash=source_hash,
        building=building,
        public_realm_recipe=public_realm_recipe,
    )
    if representation_hash is None:
        raise HTTPException(
            status_code=422,
            detail=f"Zone {zone.id} does not have a complete {generator} representation",
        )
    properties["community_3d"] = {
        "schema_version": 1,
        "state": "compiled",
        "kind": kind,
        "generator": generator,
        "compiled_at": compiled_at,
        "source_hash": source_hash,
        "representation_hash": representation_hash,
    }
    zone.properties = properties
    if building is not None:
        # Mirror the per-zone revision onto the exact Building snapshot sent
        # to the globe. The browser requires this marker to match the zone
        # metadata before it can claim that the mounted model was captured;
        # this closes mixed-refetch windows where zones and models come from
        # different project revisions.
        specifications = dict(building.specifications or {})
        specifications[COMMUNITY_REPRESENTATION_SPEC_KEY] = {
            "schema_version": 1,
            "zone_id": str(zone.id),
            "generator": generator,
            "representation_hash": representation_hash,
            "compiled_at": compiled_at,
        }
        building.specifications = specifications
        flag_modified(building, "specifications")


def _recipe_payload(body: LegoRecipeRequest) -> dict[str, Any]:
    """Serialize a recipe without inventing optional target fields.

    Pydantic includes nested defaults in ``model_dump()`` even when an older
    client never sent them. Preserve the stable top-level recipe defaults, but
    keep the target shape faithful so save/get and place/get round-trips remain
    backward compatible as footprint capabilities evolve.
    """
    payload = body.model_dump(exclude={"building_name"})
    payload["target"] = body.target.model_dump(exclude_unset=True)
    return payload


async def _place_recipe_on_zone(
    db: AsyncSession,
    zone: SiteZone,
    body: LegoPlaceRequest,
) -> tuple[Building, bool]:
    """Persist one LEGO recipe without committing, for single or batch use."""
    building: Building | None = None
    if zone.building_id is not None:
        result = await db.execute(select(Building).where(Building.id == zone.building_id))
        building = result.scalar_one_or_none()

    created = False
    if building is None:
        building = Building(
            id=uuid.uuid4(),
            project_id=zone.project_id,
            name=(body.building_name or zone.name or body.archetype_id or "LEGO Building")[:255],
            footprint=zone.geometry,
            floor_count=body.target.floors,
            height_meters=body.assembled_height_m,
            # SQLAlchemy's insert default is not visible until flush, but the
            # representation fingerprint is stamped before the final atomic
            # flush. Make the renderer's neutral rotation explicit so the
            # stored proof remains identical after the row round-trips.
            rotation_degrees=0.0,
            specifications={},
        )
        db.add(building)
        zone.building_id = building.id
        zone.building_ids = [str(building.id)]
        created = True
    else:
        # Older flows can link a Building without a usable footprint.
        if building.footprint is None:
            building.footprint = zone.geometry
        if building.floor_count is None:
            building.floor_count = body.target.floors

    specifications = dict(building.specifications or {})
    # A real family recipe upgrades the honest conceptual fallback in place.
    specifications.pop(PLANNED_MASSING_SPEC_KEY, None)
    specifications[RECIPE_SPEC_KEY] = _recipe_payload(body)
    specifications["lego_placed"] = True
    building.specifications = specifications
    flag_modified(building, "specifications")
    return building, created


def _positive_float(value: Any) -> float | None:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    return parsed if parsed > 0 else None


def _positive_int(value: Any) -> int | None:
    parsed = _positive_float(value)
    return max(1, round(parsed)) if parsed is not None else None


def _planned_massing_dimensions(zone: SiteZone) -> tuple[int | None, float]:
    """Resolve the planner's authoritative height without inventing a family."""
    properties = zone.properties or {}
    floors = _positive_int(properties.get("floors"))
    floor_height = _positive_float(properties.get("floor_height")) or 3.2
    height = (
        _positive_float(properties.get("height_m"))
        or _positive_float(properties.get("height"))
        or (floors * floor_height if floors is not None else None)
        or 10.0
    )
    return floors, height


async def _place_planned_massing_on_zone(
    db: AsyncSession,
    zone: SiteZone,
) -> tuple[Building, bool]:
    """Persist an exact-footprint neutral mass for an unsupported family.

    The linked Building gives the globe and render pipeline the same stable ID
    handshake as LEGO/Meshy geometry. When a real family is imported later,
    ``_place_recipe_on_zone`` reuses this record and removes the fallback flag.
    """
    building: Building | None = None
    if zone.building_id is not None:
        result = await db.execute(select(Building).where(Building.id == zone.building_id))
        building = result.scalar_one_or_none()

    floors, height = _planned_massing_dimensions(zone)
    properties = zone.properties or {}
    archetype_id = properties.get("development_archetype_id")
    created = False
    if building is None:
        building = Building(
            id=uuid.uuid4(),
            project_id=zone.project_id,
            name=(zone.name or str(archetype_id or "Planned Building"))[:255],
            footprint=zone.geometry,
            floor_count=floors,
            height_meters=height,
            rotation_degrees=0.0,
            specifications={},
        )
        db.add(building)
        zone.building_id = building.id
        zone.building_ids = [str(building.id)]
        created = True
    else:
        if building.footprint is None:
            building.footprint = zone.geometry
        if building.floor_count is None:
            building.floor_count = floors
        if building.height_meters is None:
            building.height_meters = height

    specifications = dict(building.specifications or {})
    # This compiler branch explicitly represents a family-pending building,
    # so an older LEGO recipe must not keep winning the globe coexistence
    # filter. A generated model, when present, still takes visual priority and
    # is stamped as Meshy below by the caller.
    specifications.pop(RECIPE_SPEC_KEY, None)
    specifications.pop("lego_placed", None)
    specifications[PLANNED_MASSING_SPEC_KEY] = {
        "schema_version": 1,
        "source": "community_3d",
        "source_zone_id": str(zone.id),
        "archetype_id": str(archetype_id) if archetype_id else None,
        "floor_count": floors,
        "height_meters": height,
    }
    building.specifications = specifications
    flag_modified(building, "specifications")
    return building, created


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
    await lock_residual_landscape_project(db, zone.project_id)
    await db.refresh(zone)

    freshness_item = Community3DCompileItem(
        zone_id=zone.id,
        source_updated_at=zone.updated_at or datetime.now(timezone.utc),
        recipe=body,
    )
    await _assert_ai_lego_recipes_are_current(
        db,
        user,
        zone.project_id,
        [(freshness_item, zone, "building")],
    )

    building, created = await _place_recipe_on_zone(db, zone, body)
    _stamp_community_3d(
        zone,
        "building",
        datetime.now(timezone.utc).isoformat(),
        building=building,
    )
    await db.flush()

    return {
        "status": "placed",
        "zone_id": str(zone.id),
        "building_id": str(building.id),
        "building_created": created,
        RECIPE_SPEC_KEY: building.specifications[RECIPE_SPEC_KEY],
    }


@router.post("/place-community")
async def place_community_3d(
    body: Community3DCompileRequest,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Atomically compile a mixed master plan into the live 3D community.

    No commit occurs inside the loop. Any invalid, inaccessible, or failed item
    aborts the request, allowing the request-scoped transaction to roll back
    every recipe, building link, and compile marker together.
    """
    zone_ids = [item.zone_id for item in body.items]
    if len(set(zone_ids)) != len(zone_ids):
        raise HTTPException(status_code=422, detail="Each zone may appear only once")

    # Resolve and validate the whole request before mutating any linked
    # building. This also closes a subtle hole in the previous endpoint, which
    # allowed one atomic request to span several accessible projects.
    resolved_items: list[
        tuple[Community3DCompileItem, SiteZone, Literal["building", "park", "street"]]
    ] = []
    project_id: uuid.UUID | None = None
    for item in body.items:
        zone = await _get_zone_with_access(db, item.zone_id, user, require_editor=True)
        if project_id is None:
            project_id = zone.project_id
        elif zone.project_id != project_id:
            raise HTTPException(
                status_code=422,
                detail="A Community 3D compile must contain zones from one project",
            )
        kind = _community_3d_kind(zone)
        if kind is None:
            raise HTTPException(
                status_code=422,
                detail=f"Zone {zone.id} is not compilable Community 3D content",
            )
        if kind != "building" and item.recipe is not None:
            raise HTTPException(
                status_code=422,
                detail=f"{kind.title()} zone {zone.id} cannot carry a building recipe",
            )
        resolved_items.append((item, zone, kind))

    # Residual land is a project-level derived result. Incremental `Complete`
    # requests omit already-compiled zones, but those polygons still occupy
    # land, so derive from every persisted zone in the project rather than the
    # request subset.
    await lock_residual_landscape_project(db, project_id)
    project_zones_result = await db.execute(
        select(SiteZone)
        .where(SiteZone.project_id == project_id)
        .order_by(SiteZone.sort_order, SiteZone.created_at, SiteZone.id)
        .execution_options(populate_existing=True)
    )
    project_zones = list(project_zones_result.scalars().all())
    zones_by_id = {zone.id: zone for zone in project_zones}
    refreshed_items: list[
        tuple[Community3DCompileItem, SiteZone, Literal["building", "park", "street"]]
    ] = []
    for item, previous_zone, previous_kind in resolved_items:
        zone = zones_by_id.get(previous_zone.id)
        if zone is None:
            raise HTTPException(
                status_code=409,
                detail="A Community 3D source zone changed before compilation; refresh and retry.",
            )
        kind = _community_3d_kind(zone)
        if kind != previous_kind:
            raise HTTPException(
                status_code=409,
                detail="A Community 3D source zone changed before compilation; refresh and retry.",
            )
        if not _same_source_revision(item.source_updated_at, zone.updated_at):
            raise HTTPException(
                status_code=409,
                detail=(
                    "A Community 3D source zone changed while its 3D recipe was being prepared; "
                    "refresh and retry."
                ),
            )
        refreshed_items.append((item, zone, kind))
    resolved_items = refreshed_items

    # AI-bound recipes must still match both the catalogue revision stamped on
    # their source zones and the exact project-visible modules.  This runs
    # under the project lock and before boundary/building persistence begins.
    await _assert_ai_lego_recipes_are_current(
        db,
        user,
        project_id,
        resolved_items,
    )

    # Resolve every public-realm recipe under the same project/source lock and
    # before boundary or linked-building mutation. Unsupported AI content
    # therefore aborts the whole transaction; manual legacy content keeps its
    # existing procedural renderer without claiming V1 capability coverage.
    public_realm_recipes: dict[uuid.UUID, dict[str, Any]] = {}
    for _, zone, kind in resolved_items:
        if kind not in {"park", "street"}:
            continue
        recipe = _public_realm_recipe_for_zone(zone, kind)
        if recipe is not None:
            public_realm_recipes[zone.id] = recipe

    boundaries = [zone for zone in project_zones if zone.zone_type == "site_boundary"]
    if len(boundaries) > 1:
        raise HTTPException(
            status_code=422,
            detail=(
                "Community 3D requires one authoritative site boundary; "
                f"this project has {len(boundaries)}. Merge or remove duplicate boundaries first."
            ),
        )
    derived_boundary_count = 0
    if not boundaries:
        authored_shapes = []
        for zone in project_zones:
            if (zone.properties or {}).get("_plan_role") == "framework_height":
                continue
            try:
                authored_shapes.append(to_shape(zone.geometry))
            except (AssertionError, TypeError, ValueError):
                # Legacy unit fixtures and corrupt historical rows can lack a
                # GeoAlchemy value. They simply cannot participate in hull
                # inference; the normal no-boundary behavior remains safe.
                continue
        if len(authored_shapes) >= 2:
            try:
                inferred_boundary = derive_site_boundary_from_authored_zones(authored_shapes)
            except ValueError:
                inferred_boundary = None
            if inferred_boundary is not None and not inferred_boundary.is_empty:
                boundary = SiteZone(
                    id=uuid.uuid4(),
                    project_id=project_id,
                    name="Site Boundary",
                    zone_type="site_boundary",
                    geometry=from_shape(inferred_boundary, srid=4326),
                    color="#7dd3fc",
                    properties={
                        "_derived_site_boundary": True,
                        "_derived_site_boundary_method": "authored_plan_metric_convex_hull",
                    },
                    sort_order=-1000,
                )
                db.add(boundary)
                project_zones.append(boundary)
                boundaries = [boundary]
                derived_boundary_count = 1

    # A master-plan redraw can replace source zones or reuse a source UUID for
    # a park/street. Older Community 3D buildings can therefore outlive the
    # building polygon that explicitly owns them and appear as ghosts beside
    # the newly compiled plan. Remove only rows with our complete
    # derived-artifact marker; unmarked/user-authored buildings are
    # intentionally preserved. This remains inside the request transaction,
    # so any later compile failure rolls the cleanup back too.
    project_buildings_result = await db.execute(
        select(Building).where(Building.project_id == project_id)
    )
    project_buildings = list(project_buildings_result.scalars().all())
    stale_buildings = stale_community_3d_buildings(
        project_buildings,
        (
            zone.id
            for zone in project_zones
            if _community_3d_kind(zone) == "building"
        ),
    )
    stale_building_ids = {building.id for building in stale_buildings}
    stale_building_id_strings = {str(building_id) for building_id in stale_building_ids}
    for project_zone in project_zones:
        if project_zone.building_id in stale_building_ids:
            project_zone.building_id = None
        if isinstance(project_zone.building_ids, list):
            retained_building_ids = [
                building_id
                for building_id in project_zone.building_ids
                if str(building_id) not in stale_building_id_strings
            ]
            if retained_building_ids != project_zone.building_ids:
                project_zone.building_ids = retained_building_ids
    for stale_building in stale_buildings:
        await db.delete(stale_building)

    compiled_at = datetime.now(timezone.utc).isoformat()
    boundary_recipes: list[tuple[SiteZone, dict[str, Any]]] = []
    try:
        for boundary in boundaries:
            if (
                (boundary.properties or {}).get("_derived_site_boundary") is True
                and boundary.name == "Generated Site Boundary"
            ):
                # Normalize the early pilot label without exposing an
                # implementation detail in the planning overlay.
                boundary.name = "Site Boundary"
            source_zones: list[ResidualSourceZone] = []
            for zone in project_zones:
                if zone.id == boundary.id or zone.zone_type == "site_boundary":
                    continue
                properties = zone.properties or {}
                role = properties.get("_plan_role")
                if role == "framework_height":
                    continue
                source_zones.append(
                    ResidualSourceZone(
                        zone_id=str(zone.id),
                        kind=_community_3d_kind(zone) or str(zone.zone_type),
                        role=str(role) if role is not None else None,
                        geometry=to_shape(zone.geometry),
                    )
                )
            boundary_recipes.append((
                boundary,
                build_residual_landscape_recipe(
                    to_shape(boundary.geometry),
                    source_zones,
                    boundary_id=str(boundary.id),
                    compiled_at=compiled_at,
                ),
            ))
    except (TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=422,
            detail=f"Residual landscape could not be derived: {exc}",
        ) from exc

    results: list[dict[str, Any]] = []
    counts = {"building": 0, "park": 0, "street": 0}

    for item, zone, kind in resolved_items:

        building_id: str | None = None
        building: Building | None = None
        building_created = False
        building_generator: Literal[
            "lego_assembly", "planned_massing", "meshy"
        ] = "lego_assembly"
        if kind == "building":
            if item.recipe is not None:
                building, building_created = await _place_recipe_on_zone(db, zone, item.recipe)
            else:
                building, building_created = await _place_planned_massing_on_zone(db, zone)
                building_generator = (
                    "meshy"
                    if (
                        building.model_url
                        or (
                            isinstance(building.lod_urls, dict)
                            and building.lod_urls.get("0")
                        )
                    )
                    else "planned_massing"
                )
            building_id = str(building.id)

        _stamp_community_3d(
            zone,
            kind,
            compiled_at,
            building_generator,
            building=building,
            public_realm_recipe=public_realm_recipes.get(zone.id),
        )
        counts[kind] += 1
        results.append({
            "zone_id": str(zone.id),
            "kind": kind,
            "building_id": building_id,
            "building_created": building_created,
            "generator": (
                building_generator
                if kind == "building"
                else "park_kit" if kind == "park" else "street_section"
            ),
        })

    for boundary, recipe in boundary_recipes:
        properties = dict(boundary.properties or {})
        properties["community_3d_landscape"] = recipe
        boundary.properties = properties
        flag_modified(boundary, "properties")

    await db.flush()
    residual_area = round(sum(recipe["area_sqm"] for _, recipe in boundary_recipes), 2)
    residual_placements = sum(len(recipe["placements"]) for _, recipe in boundary_recipes)
    return {
        "status": "compiled",
        "compiled_at": compiled_at,
        "counts": counts,
        "items": results,
        "residual_landscape": {
            "boundary_count": len(boundary_recipes),
            "derived_boundary_count": derived_boundary_count,
            "area_sqm": residual_area,
            "placement_count": residual_placements,
        },
        "stale_buildings_removed": len(stale_buildings),
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
    await lock_residual_landscape_project(db, building.project_id)
    await db.refresh(building)

    specifications = dict(building.specifications or {})
    specifications[RECIPE_SPEC_KEY] = _recipe_payload(body)
    building.specifications = specifications
    flag_modified(building, "specifications")
    await mark_linked_community_3d_stale(
        db,
        project_id=building.project_id,
        building_id=building.id,
        reason="LEGO assembly recipe changed; rebuild Community 3D before Direct rendering.",
    )
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
    await lock_residual_landscape_project(db, building.project_id)
    await db.refresh(building)

    specifications = dict(building.specifications or {})
    removed = specifications.pop(RECIPE_SPEC_KEY, None) is not None
    specifications.pop("lego_placed", None)  # stamp follows the recipe's lifecycle
    building.specifications = specifications
    flag_modified(building, "specifications")
    await mark_linked_community_3d_stale(
        db,
        project_id=building.project_id,
        building_id=building.id,
        reason="LEGO assembly recipe removed; rebuild Community 3D before Direct rendering.",
    )
    await db.flush()

    return {"status": "removed" if removed else "absent", "building_id": str(building.id)}
