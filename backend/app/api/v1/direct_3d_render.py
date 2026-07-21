"""Isolated Direct 3D render endpoint.

Classic colored-polygon rendering remains in ``render.py``.  This module has
its own request contract and fail-closed service so Direct 3D can never invoke
the Classic path's maskless comparison fallback.
"""

from __future__ import annotations

import base64
import logging
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
)
from app.core.config import get_settings
from app.core.database import get_db
from app.core.security import check_project_permission, is_admin_or_above, require_auth
from app.models.models import Building, RenderAuditLog, SiteZone, User
from app.schemas.direct_3d_render import Direct3DRenderRequest, Direct3DRenderResponse
from app.services.direct_3d_render import (
    DIRECT_3D_MODEL,
    Direct3DProviderError,
    Direct3DRenderService,
    Direct3DValidationError,
    PreparedDirect3DCapture,
    estimate_direct_3d_token_cost,
    prepare_direct_3d_capture,
)
from app.services.public_realm_lego import (
    PUBLIC_REALM_RECIPE_PROPERTY,
    PublicRealmPlanningError,
    plan_public_realm_zone_recipe,
)
from app.services.render_audit_images import put_image_with_thumbnail
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
) -> None:
    """Validate a paid capture against the locked, server-current parcel state."""

    boundaries = [zone for zone in zones if zone.zone_type == "site_boundary"]
    physical_zones = [
        zone
        for zone in zones
        if zone.zone_type != "site_boundary"
        and (zone.properties or {}).get("_plan_role") != "framework_height"
    ]
    if not physical_zones:
        raise _direct_state_conflict(
            "This project has no compiled building, park, or street layers to render."
        )
    unsupported = [
        zone
        for zone in physical_zones
        if community_3d_kind_for_source(zone.zone_type, zone.properties) is None
    ]
    if unsupported:
        raise _direct_state_conflict(
            f"Direct 3D cannot safely represent {len(unsupported)} authored polygon"
            f"{'s' if len(unsupported) != 1 else ''}. Assign a supported building, "
            "park/plaza, street/path type before rendering."
        )

    claims_by_zone = {str(claim.zone_id): claim for claim in req.community_3d_claims}
    physical_zone_ids = {str(zone.id) for zone in physical_zones}
    if set(claims_by_zone) != physical_zone_ids:
        raise _direct_state_conflict(
            "The captured Community 3D layer set no longer matches this project. "
            "Refresh the scene before rendering."
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
                    (generator == "lego_assembly" and isinstance(
                        (specifications or {}).get("legoAssembly"), dict
                    ))
                    or (generator == "planned_massing" and isinstance(
                        (specifications or {}).get("plannedMassing"), dict
                    ))
                    or (
                        generator == "meshy"
                        and bool(
                            building.model_url
                            or (
                                isinstance(building.lod_urls, dict)
                                and building.lod_urls.get("0")
                            )
                        )
                    )
                )
            )
            if (
                not linked_building_id
                or str(claim.building_id or "") != linked_building_id
                or not representation_ready
            ):
                missing_buildings.append(zone)
                continue
        elif claim.building_id is not None:
            stale_or_uncompiled.append(zone)
            continue

        public_realm_recipe = (zone.properties or {}).get(
            PUBLIC_REALM_RECIPE_PROPERTY
        )
        plan_scenario = (zone.properties or {}).get("_plan_scenario")
        if (
            kind in {"park", "street"}
            and isinstance(plan_scenario, str)
            and bool(plan_scenario.strip())
            and not isinstance(public_realm_recipe, dict)
        ):
            # Pre-contract AI plans must be rebuilt once so a paid Direct
            # capture cannot claim LEGO fidelity from the legacy generator-only
            # fingerprint. Manual public-realm zones retain that compatibility.
            stale_or_uncompiled.append(zone)
            continue

        if kind in {"park", "street"} and isinstance(public_realm_recipe, dict):
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
            if (
                canonical_recipe is None
                or canonical_recipe.model_dump(mode="json") != public_realm_recipe
            ):
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
            f"{len(stale_or_uncompiled)} Community 3D layer"
            f"{'s are' if len(stale_or_uncompiled) != 1 else ' is'} stale or missing a "
            "source fingerprint. Rebuild Community 3D before rendering."
        )
    if missing_buildings:
        raise _direct_state_conflict(
            f"{len(missing_buildings)} compiled building model"
            f"{'s are' if len(missing_buildings) != 1 else ' is'} no longer available. "
            "Rebuild Community 3D before rendering."
        )
    if len(boundaries) > 1:
        raise _direct_state_conflict(
            "Direct 3D requires one authoritative site boundary. Resolve duplicate "
            "boundaries and rebuild Community 3D before rendering."
        )
    if not boundaries:
        if len(physical_zones) > 1:
            raise _direct_state_conflict(
                "This multi-zone project no longer has its compiled site boundary. "
                "Rebuild Community 3D before rendering."
            )
        if req.residual_landscape_claim is not None:
            raise _direct_state_conflict(
                "The compiled site boundary changed after capture. Refresh and rebuild "
                "Community 3D before rendering."
            )
        return

    boundary = boundaries[0]
    stored = (boundary.properties or {}).get("community_3d_landscape")
    claim = req.residual_landscape_claim
    if not isinstance(stored, dict) or stored.get("state") != "compiled" or claim is None:
        raise _direct_state_conflict(
            "Residual landscaping is not current. Rebuild Community 3D before rendering."
        )
    stored_hash = stored.get("source_hash")
    stored_boundary_id = stored.get("boundary_id")
    try:
        current_residual_hash = residual_landscape_source_hash(
            to_shape(boundary.geometry),
            [
                ResidualSourceZone(
                    zone_id=str(zone.id),
                    kind=(
                        community_3d_kind_for_source(zone.zone_type, zone.properties)
                        or str(zone.zone_type)
                    ),
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
            "The parcel geometry changed after capture. Refresh and rebuild "
            "Community 3D before spending on a Direct render."
        )
    if (
        stored_boundary_id != str(boundary.id)
        or str(claim.boundary_id) != str(boundary.id)
        or not isinstance(stored_hash, str)
        or stored_hash.lower() != current_residual_hash.lower()
        or claim.source_hash.lower() != current_residual_hash.lower()
    ):
        raise _direct_state_conflict(
            "The parcel changed after capture. Refresh and rebuild Community 3D before "
            "spending on a Direct render."
        )


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
    """Stylize an authoritative clean 3D capture with an exact edit mask."""

    settings = get_settings()

    await check_project_permission(req.project_id, user, db, required="viewer")
    await lock_residual_landscape_project(db, req.project_id)
    zones_result = await db.execute(
        select(SiteZone)
        .where(SiteZone.project_id == req.project_id)
        .execution_options(populate_existing=True)
    )
    buildings_result = await db.execute(
        select(Building).where(Building.project_id == req.project_id)
    )
    current_buildings = list(buildings_result.scalars().all())
    _validate_direct_3d_project_zones(
        req,
        list(zones_result.scalars().all()),
        {str(building.id): building for building in current_buildings},
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
    )

    reservation = await _reserve_direct_render(
        db,
        user,
        token_cost=token_cost,
        daily_cap=settings.render_global_daily_token_cap,
        prompt=req.prompt,
        project_id=req.project_id,
    )
    try:
        result = await Direct3DRenderService(settings.openai_api_key).generate(req, capture)
    except Direct3DProviderError as exc:
        logger.warning("Direct 3D provider failure: %s", exc)
        if not exc.refund_eligible:
            status_label = (
                "billed safety failure"
                if exc.billing_status == "produced"
                else "billing unknown"
            )
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
        await _finalize_direct_audit(
            db,
            reservation,
            input_b64=result.audit_input_base64,
            output_b64=result.image_base64,
            status_label="success",
            detail=req.prompt,
        )
    except Exception as audit_exc:
        logger.warning("Failed to save Direct 3D render audit log: %s", audit_exc)

    return Direct3DRenderResponse(
        image_base64=result.image_base64,
        capture_fingerprint=result.capture_fingerprint,
        output_fingerprint=result.output_fingerprint,
        diagnostics=result.diagnostics,
    )
