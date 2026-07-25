import base64
import io
import struct
import uuid
import zlib
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import cv2
import numpy as np
import pytest
import httpx
from fastapi import HTTPException
from geoalchemy2.shape import from_shape, to_shape
from PIL import Image, ImageDraw
from pydantic import ValidationError
from shapely.geometry import box

from app.api.v1 import direct_3d_render as direct_api
from app.schemas.direct_3d_render import (
    Direct3DRenderDiagnostics,
    Direct3DRenderRequest,
)
from app.services import direct_3d_render as direct_service
from app.services.direct_3d_render import (
    Direct3DProviderError,
    Direct3DRenderService,
    Direct3DServiceResult,
    Direct3DValidationError,
    assess_macro_design_fidelity,
    assess_reproject_output_sanity,
    assess_scene_visual_change,
    assess_structural_edge_fidelity,
    _authoritative_prompt,
    _presentation_prompt,
    _load_image,
    _normalized_dimensions,
    build_openai_edit_mask,
    build_structural_edge_guide,
    estimate_direct_3d_token_cost,
    fuse_source_geometry_with_provider_finish,
    hard_composite_direct_3d,
    prepare_direct_3d_capture,
    register_generated_image,
)
from app.services.public_realm_lego import (
    PublicRealmPlanRequest,
    StreetSegmentTarget,
    plan_public_realm_recipe,
    plan_public_realm_zone_recipe,
)
from app.services.residual_landscape import (
    ResidualSourceZone,
    community_3d_representation_hash,
    community_3d_source_hash,
    residual_landscape_source_hash,
)


TEST_PROJECT_ID = uuid.UUID("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa")
TEST_ZONE_ID = uuid.UUID("bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb")


def _png_b64(image: Image.Image) -> str:
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("ascii")


def _capture_images(size: tuple[int, int] = (512, 512)) -> tuple[Image.Image, Image.Image]:
    width, height = size
    x = np.linspace(0, 255, width, dtype=np.uint8)
    y = np.linspace(0, 255, height, dtype=np.uint8)
    xx, yy = np.meshgrid(x, y)
    beauty = Image.fromarray(
        np.stack((xx, yy, ((xx.astype(np.uint16) + yy) // 2).astype(np.uint8)), axis=2),
        mode="RGB",
    )
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).rectangle(
        (width // 4, height // 4, width * 3 // 4, height * 3 // 4),
        fill=255,
    )
    return beauty, mask


def _structured_scene() -> tuple[Image.Image, Image.Image, Image.Image]:
    """Synthetic proposal with stable silhouettes and internal roof/facade edges."""

    size = (512, 512)
    beauty = Image.new("RGB", size, (72, 91, 102))
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).rectangle((48, 48, 463, 463), fill=255)
    draw = ImageDraw.Draw(beauty)
    draw.rectangle((48, 48, 463, 463), fill=(126, 142, 116))
    draw.polygon([(48, 350), (463, 305), (463, 385), (48, 430)], fill=(91, 91, 96))
    draw.ellipse((178, 220, 348, 360), fill=(72, 130, 76), outline=(224, 211, 163), width=7)

    buildings = [
        [(82, 244), (82, 124), (150, 82), (224, 124), (224, 244)],
        [(286, 274), (286, 142), (355, 104), (430, 142), (430, 274)],
    ]
    for polygon in buildings:
        draw.polygon(polygon, fill=(194, 177, 150), outline=(42, 43, 48), width=5)
    for y in (150, 184, 218):
        draw.line((92, y, 214, y), fill=(49, 62, 72), width=5)
    for y in (169, 205, 241):
        draw.line((296, y, 420, y), fill=(49, 62, 72), width=5)
    for x in (112, 154, 196, 318, 360, 402):
        draw.line((x, 145 if x < 250 else 162, x, 236 if x < 250 else 264), fill=(58, 70, 78), width=3)

    object_id = Image.new("RGB", size, (0, 0, 0))
    id_draw = ImageDraw.Draw(object_id)
    for polygon in buildings:
        id_draw.polygon(polygon, fill=(255, 0, 0))
    return beauty, mask, object_id


def _registration_context_scene() -> tuple[Image.Image, Image.Image]:
    """Geometry-rich context whose colors can change without moving edges."""

    size = (512, 512)
    beauty = Image.new("RGB", size, (35, 60, 90))
    draw = ImageDraw.Draw(beauty)
    for x in range(0, size[0], 48):
        draw.line(
            (x, 0, x, size[1]),
            fill=((x * 3) % 256, (x * 5 + 60) % 256, (x * 7 + 100) % 256),
            width=5,
        )
    for y in range(0, size[1], 44):
        draw.line(
            (0, y, size[0], y),
            fill=((y * 7 + 20) % 256, (y * 2 + 100) % 256, (y * 5) % 256),
            width=4,
        )
    for index in range(12):
        x = (index * 83) % 450
        y = (index * 131) % 450
        draw.rectangle(
            (
                x,
                y,
                x + 35 + (index % 3) * 15,
                y + 25 + (index % 4) * 10,
            ),
            fill=((index * 43) % 256, (200 - index * 17) % 256, (index * 79) % 256),
            outline="white",
            width=3,
        )
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).rectangle((145, 145, 366, 366), fill=255)
    return beauty, mask


def _style_shift_without_geometry_change(image: Image.Image) -> Image.Image:
    pixels = np.asarray(image.convert("RGB"), dtype=np.uint8)
    shifted = np.stack(
        (255 - pixels[..., 0], pixels[..., 1], 255 - pixels[..., 2]),
        axis=2,
    )
    return Image.fromarray(shifted, mode="RGB")


def _provider_first_finish_without_geometry_change(image: Image.Image) -> Image.Image:
    """Add deterministic full-frame finish/detail while retaining source edges."""

    source = np.asarray(image.convert("RGB"), dtype=np.float32)
    yy, xx = np.indices((image.height, image.width))
    texture = (
        10 * np.sin((2 * np.pi * xx) / 12)
        + 6 * np.cos((2 * np.pi * yy) / 18)
    )
    candidate = np.clip(
        source
        + np.asarray([22, 12, 4], dtype=np.float32)[None, None, :]
        + texture[..., None],
        0,
        255,
    ).astype(np.uint8)
    return Image.fromarray(candidate, mode="RGB")


def _watercolour_finish_preserving_layout(image: Image.Image) -> Image.Image:
    source = np.asarray(image.convert("RGB"), dtype=np.uint8)
    softened = cv2.bilateralFilter(source, 7, 32, 5).astype(np.float32)
    yy, xx = np.indices((image.height, image.width))
    paper = 7 * np.sin((2 * np.pi * xx) / 14) + 4 * np.cos(
        (2 * np.pi * yy) / 21
    )
    rendered = np.clip(
        softened * 0.72
        + source.astype(np.float32) * 0.28
        + np.asarray([22, 14, 8], dtype=np.float32)[None, None, :]
        + paper[..., None],
        0,
        255,
    ).astype(np.uint8)
    return Image.fromarray(rendered, mode="RGB")


def _limited_palette_line_finish_preserving_layout(image: Image.Image) -> Image.Image:
    source = np.asarray(image.convert("RGB"), dtype=np.uint8)
    quantized = np.clip((source // 48) * 48 + 24, 0, 255).astype(np.uint8)
    yy, xx = np.indices((image.height, image.width))
    halftone = np.where(((xx + yy) // 3) % 2 == 0, 3, -3)
    gray = cv2.cvtColor(source, cv2.COLOR_RGB2GRAY)
    edges = cv2.Canny(gray, 35, 95, L2gradient=True) > 0
    rendered = np.clip(
        quantized.astype(np.int16) + halftone[..., None],
        0,
        255,
    ).astype(np.uint8)
    rendered[edges] = (24, 28, 34)
    return Image.fromarray(rendered, mode="RGB")


def _request(
    *,
    beauty: Image.Image | None = None,
    mask: Image.Image | None = None,
    object_id: Image.Image | None = None,
    data_urls: bool = False,
    presentation_mode: str = "source_anchored",
    style: str = "photorealistic",
    auto_presentation_object_id: bool = True,
) -> Direct3DRenderRequest:
    beauty = beauty or _capture_images()[0]
    mask = mask or _capture_images(beauty.size)[1]
    if (
        object_id is None
        and auto_presentation_object_id
        and presentation_mode in {"scene", "reproject"}
    ):
        object_pixels = np.zeros((beauty.height, beauty.width, 3), dtype=np.uint8)
        object_pixels[np.asarray(mask.convert("L")) >= 128] = (255, 0, 0)
        object_id = Image.fromarray(object_pixels, mode="RGB")
    beauty_b64 = _png_b64(beauty)
    mask_b64 = _png_b64(mask)
    payload = {
        "beauty_image_base64": (
            f"data:image/png;base64,{beauty_b64}" if data_urls else beauty_b64
        ),
        "proposal_mask_base64": (
            f"data:image/png;base64,{mask_b64}" if data_urls else mask_b64
        ),
        "prompt": "Natural stone, convincing glazing, soft afternoon light.",
        "presentation_mode": presentation_mode,
        "style": style,
        "project_id": TEST_PROJECT_ID,
        "community_3d_claims": [{
            "zone_id": TEST_ZONE_ID,
            "source_hash": "c" * 64,
            "representation_hash": "d" * 64,
        }],
    }
    if object_id is not None:
        object_id_b64 = _png_b64(object_id)
        payload.update({
            "object_id_image_base64": (
                f"data:image/png;base64,{object_id_b64}" if data_urls else object_id_b64
            ),
            "object_id_manifest": {"#FF0000": "building"},
        })
    return Direct3DRenderRequest(**payload)


def _oversized_png_header(width: int = 5000, height: int = 3000) -> bytes:
    def chunk(kind: bytes, data: bytes) -> bytes:
        checksum = zlib.crc32(kind + data) & 0xFFFFFFFF
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", checksum)

    header = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header) + chunk(b"IEND", b"")


def _fake_service_result(audit_input_base64: str) -> Direct3DServiceResult:
    return Direct3DServiceResult(
        image_base64=_png_b64(Image.new("RGB", (2, 2), "green")),
        audit_input_base64=audit_input_base64,
        capture_fingerprint="a" * 64,
        output_fingerprint="b" * 64,
        diagnostics={
            "source_width": 512,
            "source_height": 512,
            "normalized_width": 816,
            "normalized_height": 816,
            "proposal_coverage": 0.25,
            "context_coverage": 0.75,
            "object_id_attached": False,
            "object_id_coverage": None,
            "registration": {
                "method": "identity",
                "score": 1.0,
                "translation_x_px": 0.0,
                "translation_y_px": 0.0,
                "rotation_degrees": 0.0,
            },
            "exterior_pixel_count": 100,
            "exterior_max_channel_delta": 0,
            "inward_feather_px": 2.0,
            "mask_retry_used": False,
        },
    )


def test_normalized_dimensions_preserve_aspect_and_provider_constraints():
    width, height = _normalized_dimensions(1733, 997)

    assert width % 16 == 0
    assert height % 16 == 0
    assert width <= 2048 and height <= 2048
    assert 655_360 <= width * height <= 3_686_400
    assert abs((width / height) / (1733 / 997) - 1) <= 0.01


def test_maximum_square_source_normalizes_to_non_experimental_provider_ceiling():
    assert _normalized_dimensions(2048, 2048) == (1920, 1920)


def test_direct_request_requires_project_identity_and_unique_zone_claims():
    payload = _request().model_dump()
    payload.pop("project_id")
    with pytest.raises(ValidationError, match="project_id"):
        Direct3DRenderRequest(**payload)

    payload = _request().model_dump()
    payload["community_3d_claims"] *= 2
    with pytest.raises(ValidationError, match="each zone only once"):
        Direct3DRenderRequest(**payload)


def test_presentation_mode_and_style_categories_are_validated_without_breaking_legacy():
    legacy = _request()
    assert legacy.presentation_mode == "source_anchored"
    assert legacy.style == "photorealistic"
    assert _request(presentation_mode="scene", style="documentary")
    assert _request(presentation_mode="reproject", style="isometric")

    with pytest.raises(ValidationError, match="require object_id_image_base64"):
        _request(
            presentation_mode="scene",
            style="documentary",
            auto_presentation_object_id=False,
        )
    with pytest.raises(ValidationError, match="require object_id_image_base64"):
        _request(
            presentation_mode="reproject",
            style="isometric",
            auto_presentation_object_id=False,
        )

    with pytest.raises(ValidationError, match="requires presentation_mode='reproject'"):
        _request(presentation_mode="scene", style="site-plan")
    with pytest.raises(ValidationError, match="requires presentation_mode='scene'"):
        _request(presentation_mode="reproject", style="photorealistic")
    with pytest.raises(ValidationError, match="style"):
        _request(style="not-a-render-style")


def _project_request(
    project_id: uuid.UUID,
    boundary_id: uuid.UUID | None = None,
    source_hash: str | None = None,
    *,
    community_claims: list[dict] | None = None,
) -> Direct3DRenderRequest:
    payload = _request().model_dump()
    payload["project_id"] = project_id
    if community_claims is not None:
        payload["community_3d_claims"] = community_claims
    if boundary_id is not None and source_hash is not None:
        payload["residual_landscape_claim"] = {
            "boundary_id": boundary_id,
            "source_hash": source_hash,
        }
    return Direct3DRenderRequest(**payload)


def _zone(
    zone_id: uuid.UUID,
    zone_type: str,
    *,
    properties: dict | None = None,
    building_id: uuid.UUID | None = None,
):
    return SimpleNamespace(
        id=zone_id,
        zone_type=zone_type,
        properties=properties or {},
        geometry=from_shape(box(-114.08, 51.04, -114.079, 51.041), srid=4326),
        building_id=building_id,
    )


def _calgary_rectangle_ewkt(length_m: float, width_m: float) -> str:
    """Small WGS84 rectangle suitable for metric public-realm preflight tests."""

    origin_lon = -114.08
    origin_lat = 51.04
    longitude_span = length_m / 70_000.0
    latitude_span = width_m / 111_000.0
    return (
        "SRID=4326;POLYGON(("
        f"{origin_lon} {origin_lat},"
        f"{origin_lon + longitude_span} {origin_lat},"
        f"{origin_lon + longitude_span} {origin_lat + latitude_span},"
        f"{origin_lon} {origin_lat + latitude_span},"
        f"{origin_lon} {origin_lat}"
        "))"
    )


def _compiled_zone(
    zone_type: str,
    *,
    properties: dict | None = None,
    building_id: uuid.UUID | None = None,
):
    zone = _zone(uuid.uuid4(), zone_type, properties=dict(properties or {}), building_id=building_id)
    kind = direct_api.community_3d_kind_for_source(zone.zone_type, zone.properties)
    generator = "lego_assembly" if kind == "building" else (
        "park_kit" if kind == "park" else "street_section"
    )
    source_hash = community_3d_source_hash(
        zone.zone_type,
        to_shape(zone.geometry),
        zone.properties,
    )
    building = _compiled_building(building_id) if kind == "building" and building_id else None
    zone.properties["community_3d"] = {
        "schema_version": 1,
        "state": "compiled",
        "kind": kind,
        "generator": generator,
        "compiled_at": "2026-07-20T12:00:00Z",
        "source_hash": source_hash,
        "representation_hash": community_3d_representation_hash(
            kind=kind,
            generator=generator,
            source_hash=source_hash,
            building=building,
        ),
    }
    return zone


def _compiled_building(building_id: uuid.UUID, generator: str = "lego_assembly"):
    specifications = {
        "lego_assembly": {"legoAssembly": {"schema_version": 1}},
        "planned_massing": {"plannedMassing": {"schema_version": 1}},
    }.get(generator, {})
    return SimpleNamespace(
        id=building_id,
        specifications=specifications,
        model_url="/model.glb" if generator == "meshy" else None,
        lod_urls=None,
        footprint=from_shape(box(-114.08, 51.04, -114.079, 51.041), srid=4326),
        height_meters=18,
        floor_count=5,
        floor_height_meters=3.2,
        rotation_degrees=0,
    )


def _claims_for(zones) -> list[dict]:
    claims = []
    for zone in zones:
        meta = (zone.properties or {}).get("community_3d")
        if not isinstance(meta, dict):
            continue
        claim = {
            "zone_id": zone.id,
            "source_hash": meta["source_hash"],
            "representation_hash": meta["representation_hash"],
        }
        if zone.building_id:
            claim["building_id"] = zone.building_id
        claims.append(claim)
    return claims


def test_paid_project_preflight_requires_matching_current_residual_claim():
    project_id = uuid.uuid4()
    boundary_id = uuid.uuid4()
    building_id = uuid.uuid4()
    boundary = _zone(boundary_id, "site_boundary")
    building_zone = _compiled_zone("building", building_id=building_id)
    source_hash = residual_landscape_source_hash(
        to_shape(boundary.geometry),
        [ResidualSourceZone(
            zone_id=str(building_zone.id),
            kind="building",
            role=None,
            geometry=to_shape(building_zone.geometry),
        )],
    )
    boundary.properties["community_3d_landscape"] = {
        "state": "compiled",
        "boundary_id": str(boundary_id),
        "source_hash": source_hash,
    }
    zones = [boundary, building_zone]
    request = _project_request(
        project_id,
        boundary_id,
        source_hash,
        community_claims=_claims_for(zones),
    )

    direct_api._validate_direct_3d_project_zones(
        request,
        zones,
        {str(building_id): _compiled_building(building_id)},
    )

    stale_request = _project_request(
        project_id,
        boundary_id,
        "d" * 64,
        community_claims=_claims_for(zones),
    )
    with pytest.raises(HTTPException) as exc_info:
        direct_api._validate_direct_3d_project_zones(
            stale_request,
            zones,
            {str(building_id): _compiled_building(building_id)},
        )
    assert exc_info.value.status_code == 409
    assert exc_info.value.detail["billed"] is False

    boundary.geometry = from_shape(
        box(-114.08, 51.04, -114.078, 51.042), srid=4326
    )
    with pytest.raises(HTTPException, match="parcel changed") as geometry_changed:
        direct_api._validate_direct_3d_project_zones(
            request,
            zones,
            {str(building_id): _compiled_building(building_id)},
        )
    assert geometry_changed.value.detail["billed"] is False


def test_paid_project_preflight_rejects_unrepresented_or_boundaryless_multi_zone_plan():
    project_id = uuid.uuid4()
    boundary_id = uuid.uuid4()
    source_hash = "e" * 64
    boundary = _zone(boundary_id, "site_boundary", properties={
        "community_3d_landscape": {
            "state": "compiled",
            "boundary_id": str(boundary_id),
            "source_hash": source_hash,
        },
    })

    with pytest.raises(HTTPException, match="authored polygon"):
        direct_api._validate_direct_3d_project_zones(
            _project_request(project_id, boundary_id, source_hash),
            [boundary, _zone(uuid.uuid4(), "water")],
            {},
        )

    building_id = uuid.uuid4()
    single_zones = [_compiled_zone("building", building_id=building_id)]
    boundaryless = _project_request(
        project_id,
        community_claims=_claims_for(single_zones),
    )
    direct_api._validate_direct_3d_project_zones(
        boundaryless,
        single_zones,
        {str(building_id): _compiled_building(building_id)},
    )
    multi_zones = [
        _compiled_zone("building", building_id=building_id),
        _compiled_zone("green_space", properties={"_plan_role": "open_space"}),
    ]
    with pytest.raises(HTTPException, match="no longer has"):
        direct_api._validate_direct_3d_project_zones(
            _project_request(project_id, community_claims=_claims_for(multi_zones)),
            multi_zones,
            {str(building_id): _compiled_building(building_id)},
        )


def test_paid_project_preflight_rejects_same_kind_edit_and_missing_model():
    project_id = uuid.uuid4()
    building_id = uuid.uuid4()
    zone = _compiled_zone(
        "building",
        properties={"_plan_role": "building", "floors": 5},
        building_id=building_id,
    )
    request = _project_request(project_id, community_claims=_claims_for([zone]))

    zone.properties["floors"] = 12
    with pytest.raises(HTTPException, match="source fingerprint") as stale:
        direct_api._validate_direct_3d_project_zones(
            request,
            [zone],
            {str(building_id): _compiled_building(building_id)},
        )
    assert stale.value.detail["billed"] is False

    zone = _compiled_zone("building", building_id=building_id)
    request = _project_request(project_id, community_claims=_claims_for([zone]))
    with pytest.raises(HTTPException, match="no longer available") as missing:
        direct_api._validate_direct_3d_project_zones(request, [zone], {})
    assert missing.value.detail["billed"] is False


def test_paid_project_preflight_rejects_stale_tab_claim_after_same_kind_rebuild():
    project_id = uuid.uuid4()
    building_id = uuid.uuid4()
    stale_zone = _compiled_zone(
        "building",
        properties={"_plan_role": "building", "floors": 5},
        building_id=building_id,
    )
    stale_claims = _claims_for([stale_zone])

    current_zone = _compiled_zone(
        "building",
        properties={"_plan_role": "building", "floors": 12},
        building_id=building_id,
    )
    current_zone.id = stale_zone.id

    with pytest.raises(HTTPException, match="stale or missing") as exc_info:
        direct_api._validate_direct_3d_project_zones(
            _project_request(project_id, community_claims=stale_claims),
            [current_zone],
            {str(building_id): _compiled_building(building_id)},
        )
    assert exc_info.value.detail["billed"] is False


def test_paid_project_preflight_accepts_the_same_lod_zero_fallback_as_the_globe():
    project_id = uuid.uuid4()
    building_id = uuid.uuid4()
    zone = _compiled_zone("building", building_id=building_id)
    building = _compiled_building(building_id, generator="meshy")
    building.model_url = None
    building.lod_urls = {"0": "/api/v1/files/lod-zero.glb"}
    meta = zone.properties["community_3d"]
    meta["generator"] = "meshy"
    meta["representation_hash"] = community_3d_representation_hash(
        kind="building",
        generator="meshy",
        source_hash=meta["source_hash"],
        building=building,
    )

    direct_api._validate_direct_3d_project_zones(
        _project_request(project_id, community_claims=_claims_for([zone])),
        [zone],
        {str(building_id): building},
    )


def test_paid_project_preflight_rejects_stale_representation_claim_after_recipe_rebuild():
    project_id = uuid.uuid4()
    building_id = uuid.uuid4()
    zone = _compiled_zone("building", building_id=building_id)
    stale_claims = _claims_for([zone])
    building = _compiled_building(building_id)
    building.specifications = {
        "legoAssembly": {
            "schema_version": 1,
            "instances": [{"model_url": "/modules/rebuilt-floor.glb"}],
        },
    }
    meta = zone.properties["community_3d"]
    meta["representation_hash"] = community_3d_representation_hash(
        kind="building",
        generator="lego_assembly",
        source_hash=meta["source_hash"],
        building=building,
    )

    with pytest.raises(HTTPException, match="stale or missing") as exc_info:
        direct_api._validate_direct_3d_project_zones(
            _project_request(project_id, community_claims=stale_claims),
            [zone],
            {str(building_id): building},
        )
    assert exc_info.value.detail["billed"] is False


def test_paid_project_preflight_binds_public_realm_recipe_and_live_capability():
    project_id = uuid.uuid4()
    zone = _zone(
        uuid.uuid4(),
        "green_space",
        properties={
            "_plan_role": "open_space",
            "_plan_scenario": "community_wellbeing",
            "green_space_archetype_id": "urban_pocket_park",
        },
    )
    zone.geometry = _calgary_rectangle_ewkt(30, 30)
    source_geometry = direct_api._direct_source_geometry(zone)
    planned_recipe = plan_public_realm_zone_recipe(
        zone.zone_type,
        source_geometry,
        zone.properties,
        strict=True,
    )
    assert planned_recipe is not None
    recipe = planned_recipe.model_dump(mode="json")
    zone.properties["public_realm_lego"] = recipe
    source_hash = community_3d_source_hash(
        zone.zone_type,
        source_geometry,
        zone.properties,
    )
    representation_hash = community_3d_representation_hash(
        kind="park",
        generator="park_kit",
        source_hash=source_hash,
        public_realm_recipe=recipe,
    )
    assert representation_hash is not None
    zone.properties["community_3d"] = {
        "schema_version": 1,
        "state": "compiled",
        "kind": "park",
        "generator": "park_kit",
        "compiled_at": "2026-07-21T12:00:00Z",
        "source_hash": source_hash,
        "representation_hash": representation_hash,
    }
    request = _project_request(project_id, community_claims=_claims_for([zone]))

    direct_api._validate_direct_3d_project_zones(request, [zone], {})

    # Operational recipe metadata is excluded from source_hash, so this edit
    # proves Direct preflight independently binds and validates the recipe.
    zone.properties["public_realm_lego"]["appearance_kit_id"] = "tampered"
    with pytest.raises(HTTPException, match="stale or missing") as exc_info:
        direct_api._validate_direct_3d_project_zones(request, [zone], {})
    assert exc_info.value.detail["billed"] is False


def test_paid_project_preflight_rejects_canonical_recipe_for_different_metric_target():
    project_id = uuid.uuid4()
    zone = _zone(
        uuid.uuid4(),
        "road",
        properties={
            "_plan_role": "street",
            "_plan_scenario": "community_wellbeing",
            "road_archetype_id": "narrow_residential_street",
            "width": 22,
        },
    )
    # The locked source is a 200 m x 22 m street, but the stored recipe is a
    # completely valid, self-consistent recipe for a different 10 m target.
    # Its source, recipe, representation and browser-claim hashes are all
    # recomputed to prove target-to-geometry binding is the rejecting check.
    zone.geometry = _calgary_rectangle_ewkt(200, 22)
    source_geometry = direct_api._direct_source_geometry(zone)
    wrong_recipe = plan_public_realm_recipe(PublicRealmPlanRequest(
        archetype_id="narrow_residential_street",
        target=StreetSegmentTarget(row_width_m=10, length_m=200),
    )).model_dump(mode="json")
    zone.properties["public_realm_lego"] = wrong_recipe
    source_hash = community_3d_source_hash(
        zone.zone_type,
        source_geometry,
        zone.properties,
    )
    representation_hash = community_3d_representation_hash(
        kind="street",
        generator="street_section",
        source_hash=source_hash,
        public_realm_recipe=wrong_recipe,
    )
    assert representation_hash is not None
    zone.properties["community_3d"] = {
        "schema_version": 1,
        "state": "compiled",
        "kind": "street",
        "generator": "street_section",
        "compiled_at": "2026-07-21T12:00:00Z",
        "source_hash": source_hash,
        "representation_hash": representation_hash,
    }

    with pytest.raises(HTTPException, match="stale or missing") as exc_info:
        direct_api._validate_direct_3d_project_zones(
            _project_request(project_id, community_claims=_claims_for([zone])),
            [zone],
            {},
        )
    assert exc_info.value.detail["billed"] is False


def test_paid_project_preflight_requires_v1_recipe_for_ai_public_realm():
    project_id = uuid.uuid4()
    legacy_ai_park = _compiled_zone(
        "green_space",
        properties={
            "_plan_role": "open_space",
            "_plan_scenario": "community_wellbeing",
            "green_space_archetype_id": "urban_pocket_park",
        },
    )

    with pytest.raises(HTTPException, match="stale or missing") as exc_info:
        direct_api._validate_direct_3d_project_zones(
            _project_request(
                project_id,
                community_claims=_claims_for([legacy_ai_park]),
            ),
            [legacy_ai_park],
            {},
        )
    assert exc_info.value.detail["billed"] is False


def _project_preflight_db(monkeypatch):
    """Endpoint accounting tests isolate provider/audit behavior from project validation."""

    monkeypatch.setattr(direct_api, "check_project_permission", AsyncMock())
    monkeypatch.setattr(direct_api, "lock_residual_landscape_project", AsyncMock())
    monkeypatch.setattr(direct_api, "_validate_direct_3d_project_zones", lambda *_args: None)
    empty_result = MagicMock()
    empty_result.scalars.return_value.all.return_value = []
    db = AsyncMock()
    db.execute = AsyncMock(side_effect=[empty_result, empty_result])
    return db


@pytest.mark.parametrize(
    ("width", "height", "object_id_attached", "expected_tokens"),
    [
        (816, 816, False, 34),
        (1024, 1024, False, 49),
        (1024, 1024, True, 51),
        (1536, 1024, False, 71),
        (1920, 1920, False, 158),
        (1920, 1920, True, 160),
    ],
)
def test_direct_token_estimator_prices_normalized_size_and_inputs(
    width,
    height,
    object_id_attached,
    expected_tokens,
):
    assert estimate_direct_3d_token_cost(
        width,
        height,
        object_id_attached=object_id_attached,
    ) == expected_tokens


def test_openai_mask_uses_transparent_alpha_only_for_proposal():
    proposal = Image.new("L", (4, 2), 0)
    proposal.putpixel((1, 0), 255)
    proposal.putpixel((2, 0), 128)

    edit_mask = build_openai_edit_mask(proposal)

    assert edit_mask.mode == "RGBA"
    assert edit_mask.getpixel((0, 0)) == (0, 0, 0, 255)
    assert edit_mask.getpixel((1, 0)) == (0, 0, 0, 0)
    assert edit_mask.getpixel((2, 0)) == (0, 0, 0, 127)


def test_prepare_accepts_rgb_black_white_mask_and_validates_object_ids():
    beauty, luminance_mask = _capture_images()
    rgb_mask = luminance_mask.convert("RGB")
    object_id = Image.new("RGB", beauty.size, (0, 0, 0))
    object_id.paste((255, 0, 0), box=(128, 128, 385, 385))

    capture = prepare_direct_3d_capture(
        _request(beauty=beauty, mask=rgb_mask, object_id=object_id)
    )

    assert capture.proposal_coverage == pytest.approx(np.asarray(luminance_mask).mean() / 255)
    assert capture.object_id_coverage is not None
    assert capture.normalized_object_id is not None
    assert len(capture.capture_fingerprint) == 64


def test_prepare_rejects_mask_with_different_dimensions():
    beauty, _mask = _capture_images()
    wrong_mask = Image.new("L", (511, 512), 255)

    with pytest.raises(Direct3DValidationError, match="dimensions must exactly match"):
        prepare_direct_3d_capture(_request(beauty=beauty, mask=wrong_mask))


def test_image_header_dimensions_are_rejected_before_pixel_decompression():
    with pytest.raises(Direct3DValidationError, match="decoded dimensions"):
        _load_image(
            _oversized_png_header(),
            label="oversized test image",
            allowed_formats={"PNG"},
        )


def test_prepare_rejects_source_long_edge_above_initial_2048_product_cap():
    beauty = Image.new("RGB", (2049, 256), (80, 100, 120))
    mask = Image.new("L", beauty.size, 0)
    ImageDraw.Draw(mask).rectangle((800, 40, 1200, 210), fill=255)

    with pytest.raises(Direct3DValidationError, match="between 1 and 2048"):
        prepare_direct_3d_capture(_request(beauty=beauty, mask=mask))


@pytest.mark.parametrize("fill", [0, 255])
def test_prepare_rejects_empty_or_nearly_contextless_masks(fill):
    beauty, _mask = _capture_images()
    invalid_mask = Image.new("L", beauty.size, fill)

    with pytest.raises(Direct3DValidationError, match="Proposal coverage"):
        prepare_direct_3d_capture(_request(beauty=beauty, mask=invalid_mask))


def test_prepare_rejects_fully_soft_mask_before_provider_reservation():
    beauty, _mask = _capture_images()
    fully_soft_mask = Image.new("L", beauty.size, 128)

    with pytest.raises(Direct3DValidationError, match="fully immutable context"):
        prepare_direct_3d_capture(_request(beauty=beauty, mask=fully_soft_mask))


def test_prepare_rejects_object_id_pixels_outside_proposal():
    beauty, mask = _capture_images()
    object_id = Image.new("RGB", beauty.size, (255, 0, 0))

    with pytest.raises(Direct3DValidationError, match="outside the proposal mask"):
        prepare_direct_3d_capture(_request(beauty=beauty, mask=mask, object_id=object_id))


def test_presentation_object_id_must_cover_the_proposal():
    beauty, mask = _capture_images()
    partial_object_id = Image.new("RGB", beauty.size, (0, 0, 0))
    ImageDraw.Draw(partial_object_id).rectangle(
        (192, 192, 320, 320),
        fill=(255, 0, 0),
    )

    with pytest.raises(Direct3DValidationError, match="must cover the proposal"):
        prepare_direct_3d_capture(
            _request(
                beauty=beauty,
                mask=mask,
                object_id=partial_object_id,
                presentation_mode="scene",
                style="documentary",
            )
        )

    # Legacy keeps its existing optional/partial structural-guide behavior.
    legacy_capture = prepare_direct_3d_capture(
        _request(beauty=beauty, mask=mask, object_id=partial_object_id)
    )
    assert legacy_capture.object_id_proposal_recall is not None
    assert legacy_capture.object_id_proposal_recall < 0.85


def test_presentation_object_id_reports_conservative_coverage_metrics():
    request = _request(presentation_mode="scene", style="documentary")
    capture = prepare_direct_3d_capture(request)

    assert capture.object_id_proposal_recall == pytest.approx(1.0)
    assert capture.object_id_proposal_iou == pytest.approx(1.0)


def test_scene_prepare_rejects_insufficient_lower_frame_context():
    beauty = Image.new("RGB", (512, 512), (80, 100, 120))
    mask = Image.new("L", beauty.size, 0)
    ImageDraw.Draw(mask).rectangle((0, 160, 511, 511), fill=255)
    request = _request(
        beauty=beauty,
        mask=mask,
        presentation_mode="scene",
        style="documentary",
    )

    with pytest.raises(Direct3DValidationError, match="lower-frame context"):
        prepare_direct_3d_capture(request)

    legacy_capture = prepare_direct_3d_capture(
        _request(beauty=beauty, mask=mask)
    )
    assert legacy_capture.scene_lower_context_coverage is None


def test_authoritative_prompt_includes_each_object_id_mapping_exactly_once():
    prompt = _authoritative_prompt(
        "Warm realistic materials.",
        {"#FF0000": "building", "#00FF00": "park", "#0000FF": "street"},
    )

    assert prompt.count("#FF0000=building") == 1
    assert prompt.count("#00FF00=park") == 1
    assert prompt.count("#0000FF=street") == 1
    assert "metadata only" in prompt
    assert "never reproduce, blend, or expose any class-ID color" in prompt
    assert "Image 3 is the authoritative monochrome structural-edge guide" in prompt
    assert "never draw, tint, or expose its contours or labels" in prompt


def test_provider_first_prompts_use_one_concise_mode_specific_authority_clause():
    scene = _presentation_prompt(
        "Warm limestone and mature planting.",
        presentation_mode="scene",
        style="development",
        object_id_manifest={"#FF0000": "building"},
        visible_component_summary={"building": 2, "park": 1},
    )
    reproject = _presentation_prompt(
        "Restrained line weights.",
        presentation_mode="reproject",
        style="isometric",
        object_id_manifest=None,
    )

    assert scene.count("MACRO DESIGN AUTHORITY") == 1
    assert scene.count("Warm limestone and mature planting.") == 1
    assert scene.count("#FF0000=building") == 1
    assert "Re-render the full frame" in scene
    assert "new photographic surface detail" in scene
    assert "source pixel" not in scene.lower()
    assert reproject.count("LAYOUT AUTHORITY") == 1
    assert "30-degree axonometric" in reproject
    assert "do not copy Image 1's screen coordinates" in reproject


def test_structural_guide_is_deterministic_binary_and_includes_semantic_edges():
    beauty, mask, object_id = _structured_scene()
    manifest = {"#FF0000": "building"}

    first = build_structural_edge_guide(beauty, mask, object_id, manifest)
    second = build_structural_edge_guide(beauty, mask, object_id, manifest)

    assert first.mode == "L"
    assert first.size == beauty.size
    assert set(np.unique(np.asarray(first))) == {0, 255}
    assert first.tobytes() == second.tobytes()
    # The gable ridge is part of both the beauty and object-ID structure.
    assert first.getpixel((150, 82)) == 0


def test_structural_edge_fidelity_passes_material_and_color_restylization():
    beauty, mask, object_id = _structured_scene()
    source = np.asarray(beauty, dtype=np.uint8)
    candidate = source.copy()
    proposal = np.asarray(mask) > 0
    transformed = source[proposal].astype(np.float32)
    transformed = transformed[:, [1, 2, 0]] * np.asarray([0.86, 0.92, 0.80]) + 18
    candidate[proposal] = np.clip(transformed, 0, 255).astype(np.uint8)

    result = assess_structural_edge_fidelity(
        beauty,
        Image.fromarray(candidate, mode="RGB"),
        mask,
        object_id,
        {"#FF0000": "building"},
    )

    assert result.passed is True
    assert result.beauty_edge_recall >= 0.58
    assert result.coarse_edge_recall >= 0.58
    assert result.semantic_edge_recall is not None
    assert result.semantic_edge_recall >= 0.76
    assert result.semantic_component_min_recall is not None
    assert result.semantic_component_min_recall >= 0.68


def test_structural_edge_fidelity_rejects_merged_buildings_and_flat_roofs():
    beauty, mask, object_id = _structured_scene()
    redesigned = beauty.copy()
    draw = ImageDraw.Draw(redesigned)
    draw.rectangle((48, 48, 463, 463), fill=(132, 145, 118))
    draw.rectangle((78, 128, 434, 276), fill=(198, 181, 154), outline=(42, 43, 48), width=5)
    draw.rectangle((48, 350, 463, 430), fill=(91, 91, 96))

    result = assess_structural_edge_fidelity(
        beauty,
        redesigned,
        mask,
        object_id,
        {"#FF0000": "building"},
    )

    assert result.passed is False
    assert (
        result.beauty_edge_recall < 0.58
        or result.coarse_edge_recall < 0.58
        or (result.semantic_edge_recall or 0) < 0.76
        or (result.semantic_component_min_recall or 0) < 0.68
    )


def test_macro_gate_allows_new_surface_edges_but_rejects_moved_merged_design():
    beauty, mask, object_id = _structured_scene()
    detailed = beauty.copy()
    detail_draw = ImageDraw.Draw(detailed)
    for x in range(102, 416, 18):
        detail_draw.line((x, 158, x, 232), fill=(225, 230, 222), width=2)
    accepted = assess_macro_design_fidelity(
        beauty,
        detailed,
        mask,
        object_id,
        {"#FF0000": "building"},
    )

    redesigned = beauty.copy()
    redesigned_draw = ImageDraw.Draw(redesigned)
    redesigned_draw.rectangle((48, 48, 463, 463), fill=(132, 145, 118))
    redesigned_draw.rectangle(
        (78, 128, 434, 276),
        fill=(198, 181, 154),
        outline=(42, 43, 48),
        width=5,
    )
    rejected = assess_macro_design_fidelity(
        beauty,
        redesigned,
        mask,
        object_id,
        {"#FF0000": "building"},
    )

    assert accepted.passed is True
    assert accepted.coarse_edge_recall >= 0.70
    assert accepted.semantic_component_min_recall is not None
    assert accepted.candidate_coarse_edge_precision >= 0.40
    assert accepted.candidate_coarse_edge_density_ratio <= 3.0
    assert rejected.passed is False
    assert (
        (rejected.silhouette_edge_recall or 0) < 0.80
        or rejected.coarse_edge_recall < 0.70
        or (rejected.semantic_edge_recall or 0) < 0.78
        or (rejected.semantic_component_min_recall or 0) < 0.72
        or rejected.reference_edge_p90_distance_px > 6.0
    )


def test_macro_gate_rejects_random_noise_that_games_directed_edge_recall():
    beauty, mask, object_id = _structured_scene()
    candidate = np.asarray(
        _provider_first_finish_without_geometry_change(beauty)
    ).copy()
    proposal = np.asarray(mask) >= 128
    candidate[proposal] = np.random.default_rng(20260722).integers(
        0,
        256,
        size=(int(np.count_nonzero(proposal)), 3),
        dtype=np.uint8,
    )
    rendered = Image.fromarray(candidate, mode="RGB")

    result = assess_macro_design_fidelity(
        beauty,
        rendered,
        mask,
        object_id,
        {"#FF0000": "building"},
    )

    # These source-directed recalls demonstrate the original bypass. The
    # reverse coarse-edge precision must be what rejects the noise field.
    assert result.coarse_edge_recall >= 0.90
    assert (result.semantic_edge_recall or 0) >= 0.90
    assert (result.semantic_component_min_recall or 0) >= 0.90
    assert result.candidate_coarse_edge_precision < 0.40
    assert result.passed is False
    assert assess_scene_visual_change(beauty, rendered, mask).passed is True


def test_macro_gate_rejects_dense_stripes_that_game_edge_proximity():
    beauty, mask = _registration_context_scene()
    candidate = np.asarray(
        _provider_first_finish_without_geometry_change(beauty)
    ).copy()
    proposal = np.asarray(mask) >= 128
    _yy, xx = np.indices(proposal.shape)
    stripe = ((xx // 3) % 2 * 255).astype(np.uint8)
    stripe_rgb = np.stack((stripe, 255 - stripe, stripe), axis=2)
    candidate[proposal] = stripe_rgb[proposal]

    result = assess_macro_design_fidelity(
        beauty,
        Image.fromarray(candidate, mode="RGB"),
        mask,
    )

    assert result.coarse_edge_recall >= 0.90
    assert (result.silhouette_edge_recall or 0) >= 0.80
    assert result.candidate_coarse_edge_precision < 0.40
    assert result.passed is False


def test_scene_visual_change_rejects_colour_grade_only_and_accepts_new_detail():
    beauty, mask, _object_id = _structured_scene()
    source = np.asarray(beauty, dtype=np.uint8)
    proposal = np.asarray(mask) > 0
    graded = source.copy()
    graded[proposal] = np.clip(
        graded[proposal].astype(np.int16) + np.asarray([8, 6, 4]),
        0,
        255,
    ).astype(np.uint8)
    grade_result = assess_scene_visual_change(
        beauty,
        Image.fromarray(graded, mode="RGB"),
        mask,
    )

    detailed = _provider_first_finish_without_geometry_change(beauty)
    draw = ImageDraw.Draw(detailed)
    for y in range(112, 330, 14):
        draw.line((92, y, 430, y), fill=(232, 225, 210), width=2)
    detail_result = assess_scene_visual_change(beauty, detailed, mask)

    assert grade_result.whole_frame_mean_absolute_delta < 5.0
    assert grade_result.proposal_mean_absolute_delta < 12.0
    assert grade_result.context_mean_absolute_delta == 0.0
    assert grade_result.passed is False
    assert detail_result.passed is True
    assert detail_result.whole_frame_mean_absolute_delta >= 5.0
    assert detail_result.proposal_mean_absolute_delta >= 12.0
    assert detail_result.proposal_photometric_residual_p95 >= 6.0
    assert (
        detail_result.proposal_detail_delta_p75 >= 3.0
        or detail_result.novel_detail_edge_coverage >= 0.0015
    )
    assert (
        detail_result.context_mean_absolute_delta >= 4.0
        or detail_result.context_photometric_residual_p95 >= 4.0
    )


def test_scene_visual_change_rejects_proposal_and_sky_only_change():
    beauty, mask = _registration_context_scene()
    source = np.asarray(beauty, dtype=np.uint8)
    proposal = np.asarray(mask) > 0
    candidate = source.copy()
    sky = np.zeros(proposal.shape, dtype=bool)
    sky[: beauty.height * 2 // 5, :] = True
    changed = proposal | sky
    candidate[changed] = np.stack(
        (
            255 - source[..., 0],
            source[..., 1],
            255 - source[..., 2],
        ),
        axis=2,
    )[changed]
    # Draw into the array-backed image explicitly so proposal detail clears the
    # spatial-change branch while lower mask-zero context remains untouched.
    rendered = Image.fromarray(candidate, mode="RGB")
    draw = ImageDraw.Draw(rendered)
    for y in range(170, 350, 12):
        draw.line((160, y, 350, y), fill=(245, 226, 201), width=2)

    result = assess_scene_visual_change(beauty, rendered, mask)

    assert result.whole_frame_mean_absolute_delta >= 5.0
    assert result.proposal_mean_absolute_delta >= 12.0
    assert result.context_mean_absolute_delta == 0.0
    assert result.context_photometric_residual_p95 == 0.0
    assert result.passed is False


def test_scene_visual_change_rejects_flat_lower_context_tint():
    beauty, mask = _registration_context_scene()
    source = np.asarray(beauty, dtype=np.uint8)
    proposal = np.asarray(mask) >= 128
    candidate = source.copy()
    finished = np.asarray(
        _provider_first_finish_without_geometry_change(beauty)
    )
    candidate[proposal] = finished[proposal]

    sky = np.zeros(proposal.shape, dtype=bool)
    sky[: beauty.height * 2 // 5, :] = True
    sky &= ~proposal
    candidate[sky] = np.clip(
        candidate[sky].astype(np.int16) + 20,
        0,
        255,
    ).astype(np.uint8)
    lower_context = np.zeros(proposal.shape, dtype=bool)
    lower_context[round(beauty.height * 0.45) :, :] = True
    lower_context &= ~proposal
    candidate[lower_context] = np.clip(
        candidate[lower_context].astype(np.int16) + 5,
        0,
        255,
    ).astype(np.uint8)

    result = assess_scene_visual_change(
        beauty,
        Image.fromarray(candidate, mode="RGB"),
        mask,
    )

    assert result.whole_frame_mean_absolute_delta >= 5.0
    assert result.proposal_mean_absolute_delta >= 12.0
    assert result.context_mean_absolute_delta >= 4.0
    assert result.context_photometric_residual_p95 < 4.0
    assert result.context_detail_delta_p75 < 0.75
    assert result.passed is False


@pytest.mark.parametrize(
    "transform",
    [
        _watercolour_finish_preserving_layout,
        _limited_palette_line_finish_preserving_layout,
    ],
    ids=["soft-watercolour", "limited-palette-line-art"],
)
def test_common_scene_gates_accept_representative_artistic_finishes(transform):
    beauty, mask = _registration_context_scene()
    candidate = transform(beauty)
    registration = register_generated_image(beauty, candidate, mask)

    assert np.hypot(
        registration.translation_x_px,
        registration.translation_y_px,
    ) <= 8.0
    assert abs(registration.rotation_degrees) <= 0.35
    macro = assess_macro_design_fidelity(
        beauty,
        registration.image,
        mask,
    )
    visual = assess_scene_visual_change(
        beauty,
        registration.image,
        mask,
    )

    assert macro.passed is True
    assert macro.candidate_coarse_edge_precision >= 0.40
    assert macro.candidate_coarse_edge_density_ratio <= 3.0
    assert visual.passed is True
    assert visual.context_detail_delta_p75 >= 0.75


def test_semantic_requirements_ignore_invisible_class_boundaries_for_one_value_change():
    beauty, mask, _object_id = _structured_scene()
    object_id = Image.new("RGB", beauty.size, (0, 0, 0))
    # This ownership region lies on visually continuous grass. Its class edge
    # is not an edge the generated beauty image should be required to invent.
    ImageDraw.Draw(object_id).rectangle((238, 96, 270, 190), fill=(255, 0, 0))
    changed = np.asarray(beauty).copy()
    changed[140, 250, 1] = min(255, int(changed[140, 250, 1]) + 1)

    result = assess_structural_edge_fidelity(
        beauty,
        Image.fromarray(changed, mode="RGB"),
        mask,
        object_id,
        {"#FF0000": "building"},
    )

    assert result.passed is True
    assert result.beauty_edge_recall == pytest.approx(1.0)
    assert result.coarse_edge_recall == pytest.approx(1.0)
    assert result.semantic_edge_recall is None or result.semantic_edge_recall >= 0.76
    assert (
        result.semantic_component_min_recall is None
        or result.semantic_component_min_recall >= 0.68
    )


def test_source_phase_finish_fusion_salvages_style_without_provider_geometry():
    beauty, mask, object_id = _structured_scene()
    redesigned = beauty.copy()
    draw = ImageDraw.Draw(redesigned)
    draw.rectangle((48, 48, 463, 463), fill=(154, 173, 128))
    draw.rectangle((78, 128, 434, 276), fill=(218, 172, 125), outline=(25, 38, 51), width=5)
    draw.rectangle((48, 350, 463, 430), fill=(72, 88, 114))
    manifest = {"#FF0000": "building"}

    raw_fidelity = assess_structural_edge_fidelity(
        beauty,
        redesigned,
        mask,
        object_id,
        manifest,
    )
    fused = fuse_source_geometry_with_provider_finish(
        beauty,
        redesigned,
        mask,
        object_id,
        manifest,
    )
    fused_fidelity = assess_structural_edge_fidelity(
        beauty,
        fused,
        mask,
        object_id,
        manifest,
    )

    exterior = np.asarray(mask) == 0
    assert raw_fidelity.passed is False
    assert fused_fidelity.passed is True
    assert np.array_equal(np.asarray(fused)[exterior], np.asarray(beauty)[exterior])
    assert not np.array_equal(np.asarray(fused)[~exterior], np.asarray(beauty)[~exterior])
    assert fused_fidelity.coarse_edge_recall >= 0.58


def test_source_phase_finish_fusion_keeps_identity_byte_exact():
    beauty, mask, object_id = _structured_scene()

    fused = fuse_source_geometry_with_provider_finish(
        beauty,
        beauty.copy(),
        mask,
        object_id,
        {"#FF0000": "building"},
    )

    assert fused.tobytes() == beauty.tobytes()


def test_flat_source_without_reference_edges_is_safe_after_source_owned_fusion():
    beauty = Image.new("RGB", (512, 512), (96, 112, 104))
    mask = Image.new("L", beauty.size, 0)
    ImageDraw.Draw(mask).rectangle((96, 96, 415, 415), fill=255)
    provider = beauty.copy()
    ImageDraw.Draw(provider).rectangle((96, 96, 415, 415), fill=(142, 126, 108))

    fused = fuse_source_geometry_with_provider_finish(beauty, provider, mask)
    fidelity = assess_structural_edge_fidelity(beauty, fused, mask)

    assert fidelity.reference_edge_pixels == 0
    assert fidelity.beauty_edge_recall == pytest.approx(1.0)
    assert fidelity.coarse_edge_recall == pytest.approx(1.0)
    assert fidelity.reference_edge_p90_distance_px == pytest.approx(0.0)
    assert fidelity.passed is True


def test_source_phase_detail_gains_texture_without_copying_provider_line():
    import cv2

    width = height = 512
    yy, xx = np.indices((height, width))
    proposal = (xx >= 48) & (xx <= 463) & (yy >= 48) & (yy <= 463)
    source_pixels = np.zeros((height, width, 3), dtype=np.uint8)
    source_pixels[:] = (70, 82, 92)
    source_pixels[proposal] = (154, 158, 160)
    source_noise = np.random.default_rng(7).integers(
        -1,
        2,
        (height, width),
        dtype=np.int16,
    )
    for channel in range(3):
        source_pixels[..., channel][proposal] = (
            source_pixels[..., channel][proposal].astype(np.int16)
            + source_noise[proposal]
        )

    # Provider microtexture has independent spatial phase, plus a high-contrast
    # vertical feature absent from the source. Neither is allowed to become
    # output geometry; only its per-role robust contrast statistic may be used.
    provider_pixels = np.zeros_like(source_pixels)
    provider_pixels[:] = (70, 82, 92)
    provider_pixels[proposal] = (168, 168, 167)
    provider_noise = np.random.default_rng(19).integers(
        -5,
        6,
        (height, width),
        dtype=np.int16,
    )
    for channel in range(3):
        provider_pixels[..., channel][proposal] = np.clip(
            provider_pixels[..., channel][proposal].astype(np.int16)
            + provider_noise[proposal],
            0,
            255,
        )
    provider_pixels[70:442, 255:258] = (32, 36, 40)
    mask_pixels = np.where(proposal, 255, 0).astype(np.uint8)
    object_id_pixels = np.zeros_like(source_pixels)
    object_id_pixels[proposal] = (255, 0, 0)
    source = Image.fromarray(source_pixels, mode="RGB")
    provider = Image.fromarray(provider_pixels, mode="RGB")
    mask = Image.fromarray(mask_pixels, mode="L")
    object_id = Image.fromarray(object_id_pixels, mode="RGB")

    fusion = direct_service._fuse_source_geometry_with_provider_finish(
        source,
        provider,
        mask,
        object_id,
        {"#FF0000": "building"},
    )
    fused_pixels = np.asarray(fusion.image)
    fidelity = assess_structural_edge_fidelity(
        source,
        fusion.image,
        mask,
        object_id,
        {"#FF0000": "building"},
    )

    def micro_detail(pixels: np.ndarray) -> np.ndarray:
        gray = cv2.cvtColor(pixels, cv2.COLOR_RGB2GRAY).astype(np.float32)
        return gray - cv2.GaussianBlur(gray, (0, 0), 0.8)

    source_detail = micro_detail(source_pixels)
    provider_detail = micro_detail(provider_pixels)
    fused_detail = micro_detail(fused_pixels)
    material_sample = proposal & (xx < 230)
    source_phase_correlation = float(
        np.corrcoef(
            source_detail[material_sample],
            fused_detail[material_sample],
        )[0, 1]
    )
    provider_line = (
        (xx >= 255)
        & (xx <= 257)
        & (yy >= 80)
        & (yy <= 430)
    )
    source_texture_p75 = float(
        np.percentile(np.abs(source_detail[material_sample]), 75)
    )
    fused_texture_p75 = float(
        np.percentile(np.abs(fused_detail[material_sample]), 75)
    )
    provider_line_p95 = float(
        np.percentile(np.abs(provider_detail[provider_line]), 95)
    )
    fused_line_p95 = float(
        np.percentile(np.abs(fused_detail[provider_line]), 95)
    )
    exterior = ~proposal
    building_metrics = fusion.diagnostics["role_metrics"]["building"]

    assert fidelity.passed is True
    assert np.array_equal(fused_pixels[exterior], source_pixels[exterior])
    assert source_phase_correlation > 0.95
    assert fused_texture_p75 > source_texture_p75 * 1.25
    assert fused_line_p95 < provider_line_p95 * 0.10
    assert building_metrics["texture_gain"] > 1.25
    assert building_metrics["source_detail_correlation"] > 0.95


def test_identity_registration_uses_immutable_context():
    beauty, mask = _capture_images()
    generated = beauty.copy()
    generated.paste((240, 40, 20), box=(128, 128, 385, 385))

    registration = register_generated_image(beauty, generated, mask)

    assert registration.method == "identity"
    assert registration.score == pytest.approx(1.0)
    assert registration.translation_x_px == 0


def test_registration_accepts_style_shift_when_context_geometry_is_unchanged():
    beauty, mask = _registration_context_scene()
    generated = _style_shift_without_geometry_change(beauty)

    registration = register_generated_image(beauty, generated, mask)

    assert registration.method == "ecc-euclidean"
    assert registration.score_metric == "bidirectional-structural-edge-recall"
    assert registration.photometric_score < 0.65
    assert registration.structural_context_score is not None
    assert registration.structural_context_score >= 0.62
    assert abs(registration.translation_x_px) < 3
    assert abs(registration.translation_y_px) < 1
    assert abs(registration.rotation_degrees) < 0.1


def test_registration_structural_fallback_does_not_weaken_translation_limit():
    beauty, mask = _registration_context_scene()
    translated = cv2.warpAffine(
        np.asarray(beauty),
        np.asarray(((1, 0, 20), (0, 1, 0)), dtype=np.float32),
        beauty.size,
        borderMode=cv2.BORDER_REFLECT,
    )

    with pytest.raises(Direct3DValidationError, match="translation limit"):
        register_generated_image(beauty, Image.fromarray(translated), mask)


def test_registration_structural_fallback_does_not_weaken_rotation_limit():
    beauty, mask = _registration_context_scene()
    rotation = cv2.getRotationMatrix2D(
        (beauty.width / 2, beauty.height / 2),
        2.0,
        1.0,
    )
    rotated = cv2.warpAffine(
        np.asarray(beauty),
        rotation,
        beauty.size,
        borderMode=cv2.BORDER_REFLECT,
    )

    with pytest.raises(Direct3DValidationError, match="rotation exceeds"):
        register_generated_image(beauty, Image.fromarray(rotated), mask)


def test_hard_composite_keeps_every_mask_zero_pixel_byte_identical():
    beauty, mask = _capture_images()
    generated = Image.new("RGB", beauty.size, (255, 0, 255))

    composited, exterior_count, exterior_max_delta = hard_composite_direct_3d(
        beauty,
        generated,
        mask,
    )

    source_pixels = np.asarray(beauty)
    output_pixels = np.asarray(composited)
    exterior = np.asarray(mask) == 0
    assert exterior_count == int(np.count_nonzero(exterior))
    assert exterior_max_delta == 0
    assert np.array_equal(output_pixels[exterior], source_pixels[exterior])
    assert tuple(output_pixels[256, 256]) == (255, 0, 255)


def test_hard_composite_uses_white_as_proposal_and_preserves_soft_alpha():
    source = Image.new("RGB", (3, 1), (0, 0, 0))
    generated = Image.new("RGB", source.size, (200, 100, 50))
    mask = Image.fromarray(np.asarray(((0, 128, 255),), dtype=np.uint8), mode="L")

    composited, exterior_count, exterior_max_delta = hard_composite_direct_3d(
        source,
        generated,
        mask,
        inward_feather_px=0,
    )

    assert list(composited.getdata()) == [
        (0, 0, 0),
        (100, 50, 25),
        (200, 100, 50),
    ]
    assert exterior_count == 1
    assert exterior_max_delta == 0


def test_hard_composite_feathers_only_inward_from_the_exact_context_seam():
    source = Image.new("RGB", (9, 9), (0, 0, 0))
    generated = Image.new("RGB", source.size, (255, 255, 255))
    mask = Image.new("L", source.size, 0)
    ImageDraw.Draw(mask).rectangle((2, 2, 6, 6), fill=255)

    composited, _exterior_count, exterior_max_delta = hard_composite_direct_3d(
        source,
        generated,
        mask,
    )
    pixels = np.asarray(composited)
    exterior = np.asarray(mask) == 0

    assert exterior_max_delta == 0
    assert np.array_equal(pixels[exterior], np.zeros((int(exterior.sum()), 3), dtype=np.uint8))
    assert 0 < int(pixels[2, 4, 0]) < 255
    assert int(pixels[4, 4, 0]) > int(pixels[2, 4, 0])


def test_hard_composite_rejects_alpha_or_image_dimension_mismatch():
    source = Image.new("RGB", (8, 8), "black")
    generated = Image.new("RGB", (8, 8), "white")
    wrong_mask = Image.new("L", (7, 8), 255)

    with pytest.raises(Direct3DValidationError, match="identical dimensions"):
        hard_composite_direct_3d(source, generated, wrong_mask)


class _FakeResponse:
    def __init__(self, status_code: int, body: dict | None = None, text: str = ""):
        self.status_code = status_code
        self._body = body or {}
        self.text = text

    def json(self):
        return self._body


class _RecordingClient:
    calls: list[dict] = []
    response: _FakeResponse | Exception

    def __init__(self, *args, **kwargs):
        self.timeout = kwargs.get("timeout")

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, traceback):
        return False

    async def post(self, url, **kwargs):
        self.__class__.calls.append({"url": url, **kwargs})
        if isinstance(self.__class__.response, Exception):
            raise self.__class__.response
        return self.__class__.response


@pytest.mark.asyncio
async def test_provider_call_uses_explicit_size_png_alpha_mask_and_no_fidelity_parameter(monkeypatch):
    request = _request()
    capture = prepare_direct_3d_capture(request)
    generated = capture.normalized_beauty.copy()
    _RecordingClient.calls = []
    _RecordingClient.response = _FakeResponse(
        200,
        {"data": [{"b64_json": _png_b64(generated)}]},
    )
    monkeypatch.setattr(direct_service.httpx, "AsyncClient", _RecordingClient)

    output = await Direct3DRenderService("test-key")._call_openai(request, capture)

    assert output.size == capture.normalized_beauty.size
    assert len(_RecordingClient.calls) == 1
    call = _RecordingClient.calls[0]
    assert call["data"]["model"] == "gpt-image-2"
    assert call["data"]["quality"] == "high"
    assert call["data"]["size"] == f"{output.width}x{output.height}"
    assert "input_fidelity" not in call["data"]
    image_file = next(item for item in call["files"] if item[0] == "image[]")
    image_files = [item for item in call["files"] if item[0] == "image[]"]
    mask_file = next(item for item in call["files"] if item[0] == "mask")
    sent_image = Image.open(io.BytesIO(image_file[1][1]))
    sent_guide = Image.open(io.BytesIO(image_files[-1][1][1]))
    sent_mask = Image.open(io.BytesIO(mask_file[1][1]))
    assert sent_image.format == "PNG" and sent_mask.format == "PNG"
    assert sent_image.size == sent_mask.size == output.size
    assert len(image_files) == 2
    assert image_files[-1][1][0] == "direct-3d-structural-edges.png"
    assert sent_guide.mode == "L"
    assert sent_guide.size == output.size
    assert sent_mask.mode == "RGBA"
    assert sent_mask.getchannel("A").getextrema() == (0, 255)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("presentation_mode", "style", "authority"),
    [
        ("scene", "development", "MACRO DESIGN AUTHORITY"),
        ("reproject", "isometric", "LAYOUT AUTHORITY"),
    ],
)
async def test_provider_first_payload_omits_mask_and_keeps_one_concise_authority(
    monkeypatch,
    presentation_mode,
    style,
    authority,
):
    request = _request(presentation_mode=presentation_mode, style=style)
    capture = prepare_direct_3d_capture(request)
    _RecordingClient.calls = []
    _RecordingClient.response = _FakeResponse(
        200,
        {"data": [{"b64_json": _png_b64(capture.normalized_beauty)}]},
    )
    monkeypatch.setattr(direct_service.httpx, "AsyncClient", _RecordingClient)

    await Direct3DRenderService("test-key")._call_openai(request, capture)

    call = _RecordingClient.calls[0]
    assert not [item for item in call["files"] if item[0] == "mask"]
    assert call["data"]["size"] == (
        f"{capture.normalized_beauty.width}x{capture.normalized_beauty.height}"
    )
    assert call["data"]["prompt"].count(authority) == 1
    assert call["data"]["prompt"].count(request.prompt) == 1


@pytest.mark.asyncio
async def test_provider_attaches_object_id_image_and_exact_semantic_legend(monkeypatch):
    beauty, mask = _capture_images()
    object_id = Image.new("RGB", beauty.size, (0, 0, 0))
    object_id.paste((255, 0, 0), box=(128, 128, 385, 385))
    request = _request(beauty=beauty, mask=mask, object_id=object_id)
    capture = prepare_direct_3d_capture(request)
    _RecordingClient.calls = []
    _RecordingClient.response = _FakeResponse(
        200,
        {"data": [{"b64_json": _png_b64(capture.normalized_beauty)}]},
    )
    monkeypatch.setattr(direct_service.httpx, "AsyncClient", _RecordingClient)

    await Direct3DRenderService("test-key")._call_openai(request, capture)

    call = _RecordingClient.calls[0]
    image_files = [item for item in call["files"] if item[0] == "image[]"]
    assert len(image_files) == 3
    assert [item[1][0] for item in image_files] == [
        "direct-3d-beauty.png",
        "direct-3d-class-id.png",
        "direct-3d-structural-edges.png",
    ]
    assert call["data"]["prompt"].count("#FF0000=building") == 1
    assert "Image 3 is the authoritative monochrome structural-edge guide" in call["data"]["prompt"]
    assert "1 visibly disjoint building region" in call["data"]["prompt"]
    assert "visible 2D components, not a claim about real-world object count" in call["data"]["prompt"]
    assert "identifiers exist only in the guide as metadata" in call["data"]["prompt"]
    assert "never reproduce, blend, or expose any class-ID color" in call["data"]["prompt"]


@pytest.mark.asyncio
async def test_provider_mask_rejection_fails_after_exactly_one_call(monkeypatch):
    request = _request()
    capture = prepare_direct_3d_capture(request)
    _RecordingClient.calls = []
    _RecordingClient.response = _FakeResponse(400, text="invalid mask alpha")
    monkeypatch.setattr(direct_service.httpx, "AsyncClient", _RecordingClient)

    with pytest.raises(Direct3DProviderError, match=r"\(400\)") as exc_info:
        await Direct3DRenderService("test-key")._call_openai(request, capture)

    assert len(_RecordingClient.calls) == 1
    assert exc_info.value.billing_status == "unproduced"
    assert exc_info.value.refund_eligible is True


@pytest.mark.asyncio
async def test_provider_read_timeout_is_ambiguous_and_not_refund_eligible(monkeypatch):
    request = _request()
    capture = prepare_direct_3d_capture(request)
    _RecordingClient.calls = []
    _RecordingClient.response = httpx.ReadTimeout(
        "response dropped after upload",
        request=httpx.Request("POST", "https://api.openai.com/v1/images/edits"),
    )
    monkeypatch.setattr(direct_service.httpx, "AsyncClient", _RecordingClient)

    with pytest.raises(Direct3DProviderError, match="outcome is unknown") as exc_info:
        await Direct3DRenderService("test-key")._call_openai(request, capture)

    assert len(_RecordingClient.calls) == 1
    assert exc_info.value.billing_status == "unknown"
    assert exc_info.value.refund_eligible is False


@pytest.mark.asyncio
async def test_provider_connect_failure_is_known_unproduced_and_refundable(monkeypatch):
    request = _request()
    capture = prepare_direct_3d_capture(request)
    _RecordingClient.calls = []
    _RecordingClient.response = httpx.ConnectError(
        "connection refused before upload",
        request=httpx.Request("POST", "https://api.openai.com/v1/images/edits"),
    )
    monkeypatch.setattr(direct_service.httpx, "AsyncClient", _RecordingClient)

    with pytest.raises(Direct3DProviderError, match="before generation") as exc_info:
        await Direct3DRenderService("test-key")._call_openai(request, capture)

    assert exc_info.value.billing_status == "unproduced"
    assert exc_info.value.refund_eligible is True


@pytest.mark.asyncio
async def test_unexpected_processing_after_valid_b64_is_classified_as_produced(monkeypatch):
    request = _request()
    capture = prepare_direct_3d_capture(request)
    _RecordingClient.calls = []
    _RecordingClient.response = _FakeResponse(
        200,
        {"data": [{"b64_json": _png_b64(capture.normalized_beauty)}]},
    )
    monkeypatch.setattr(direct_service.httpx, "AsyncClient", _RecordingClient)
    monkeypatch.setattr(
        direct_service,
        "_load_image",
        MagicMock(side_effect=RuntimeError("unexpected decoder failure")),
    )

    with pytest.raises(Direct3DProviderError, match="unusable") as exc_info:
        await Direct3DRenderService("test-key")._call_openai(request, capture)

    assert exc_info.value.billing_status == "produced"
    assert exc_info.value.refund_eligible is False


@pytest.mark.asyncio
async def test_unexpected_post_provider_registration_error_remains_billed(monkeypatch):
    request = _request()
    capture = prepare_direct_3d_capture(request)
    monkeypatch.setattr(
        Direct3DRenderService,
        "_call_openai",
        AsyncMock(return_value=capture.normalized_beauty.copy()),
    )
    monkeypatch.setattr(
        direct_service,
        "register_generated_image",
        MagicMock(side_effect=RuntimeError("unexpected registration crash")),
    )

    with pytest.raises(Direct3DProviderError, match="post-processing") as exc_info:
        await Direct3DRenderService("test-key").generate(request, capture)

    assert exc_info.value.billing_status == "produced"
    assert exc_info.value.refund_eligible is False
    assert exc_info.value.provider_image_base64 is not None


@pytest.mark.asyncio
async def test_service_returns_byte_exact_exterior_and_diagnostics(monkeypatch):
    beauty, mask, object_id = _structured_scene()
    request = _request(beauty=beauty, mask=mask, object_id=object_id)
    capture = prepare_direct_3d_capture(request)
    generated = capture.normalized_beauty.copy()
    normalized_mask = np.asarray(capture.normalized_proposal_mask) > 127
    generated_pixels = np.asarray(generated).copy()
    restyled = generated_pixels[normalized_mask].astype(np.float32)
    generated_pixels[normalized_mask] = np.clip(
        restyled * np.asarray([0.82, 0.88, 0.78]) + 22,
        0,
        255,
    ).astype(np.uint8)
    generated = Image.fromarray(generated_pixels, mode="RGB")
    monkeypatch.setattr(
        Direct3DRenderService,
        "_call_openai",
        AsyncMock(return_value=generated),
    )

    result = await Direct3DRenderService("test-key").generate(request)

    output = Image.open(io.BytesIO(base64.b64decode(result.image_base64))).convert("RGB")
    source = capture.source_beauty
    exterior = np.asarray(capture.source_proposal_mask) == 0
    assert np.array_equal(np.asarray(output)[exterior], np.asarray(source)[exterior])
    assert result.diagnostics["exterior_max_channel_delta"] == 0
    assert result.diagnostics["mask_retry_used"] is False
    assert result.diagnostics["registration"]["method"] == "identity"
    assert result.diagnostics["structural_edge_guide_attached"] is True
    assert result.diagnostics["structural_edge_fidelity"]["passed"] is True
    assert len(result.output_fingerprint) == 64


@pytest.mark.asyncio
async def test_service_context_locks_style_shifted_provider_exterior(monkeypatch):
    beauty, mask = _registration_context_scene()
    request = _request(beauty=beauty, mask=mask)
    capture = prepare_direct_3d_capture(request)
    generated = _style_shift_without_geometry_change(capture.normalized_beauty)
    monkeypatch.setattr(
        Direct3DRenderService,
        "_call_openai",
        AsyncMock(return_value=generated),
    )

    result = await Direct3DRenderService("test-key").generate(request, capture)

    output = Image.open(io.BytesIO(base64.b64decode(result.image_base64))).convert("RGB")
    source_pixels = np.asarray(capture.source_beauty)
    output_pixels = np.asarray(output)
    exterior = np.asarray(capture.source_proposal_mask) == 0
    assert output.size == capture.source_beauty.size
    assert np.array_equal(output_pixels[exterior], source_pixels[exterior])
    assert result.diagnostics["exterior_max_channel_delta"] == 0
    assert result.diagnostics["registration"]["score_metric"] == (
        "bidirectional-structural-edge-recall"
    )
    assert result.diagnostics["registration"]["photometric_score"] < 0.65
    assert result.diagnostics["structural_edge_fidelity"]["passed"] is True


@pytest.mark.asyncio
async def test_service_fuses_provider_finish_without_accepting_provider_geometry(monkeypatch):
    beauty, mask, object_id = _structured_scene()
    request = _request(beauty=beauty, mask=mask, object_id=object_id)
    capture = prepare_direct_3d_capture(request)
    generated = capture.normalized_beauty.copy()
    proposal = np.asarray(capture.normalized_proposal_mask) > 127
    generated_pixels = np.asarray(generated).copy()
    generated_pixels[proposal] = (132, 145, 118)
    generated = Image.fromarray(generated_pixels, mode="RGB")
    draw = ImageDraw.Draw(generated)
    draw.rectangle(
        (
            generated.width * 3 // 20,
            generated.height // 4,
            generated.width * 17 // 20,
            generated.height * 11 // 20,
        ),
        fill=(198, 181, 154),
        outline=(42, 43, 48),
        width=7,
    )
    provider = AsyncMock(return_value=generated)
    monkeypatch.setattr(Direct3DRenderService, "_call_openai", provider)

    result = await Direct3DRenderService("test-key").generate(request, capture)

    provider.assert_awaited_once()
    assert result.diagnostics["provider_raw_structural_edge_fidelity"]["passed"] is False
    assert result.diagnostics["structural_edge_fidelity"]["passed"] is True
    assert result.diagnostics["finish_fusion"]["method"] == (
        "source-geometry-multiscale-source-phase-detail-v2"
    )
    assert (
        result.diagnostics["finish_fusion"][
            "provider_high_frequency_phase_transferred"
        ]
        is False
    )
    assert result.diagnostics["finish_fusion"]["safe_microtexture_coverage"] >= 0
    assert isinstance(result.diagnostics["finish_fusion"]["role_metrics"], dict)


@pytest.mark.asyncio
async def test_scene_mode_keeps_provider_pixels_and_allows_context_restyling(monkeypatch):
    beauty, mask = _registration_context_scene()
    request = _request(
        beauty=beauty,
        mask=mask,
        presentation_mode="scene",
        style="documentary",
    )
    capture = prepare_direct_3d_capture(request)
    generated = _provider_first_finish_without_geometry_change(
        capture.normalized_beauty
    )
    draw = ImageDraw.Draw(generated)
    for y in range(generated.height * 3 // 10, generated.height * 7 // 10, 18):
        draw.line(
            (
                generated.width * 3 // 10,
                y,
                generated.width * 7 // 10,
                y,
            ),
            fill=(242, 228, 205),
            width=2,
        )
    monkeypatch.setattr(
        Direct3DRenderService,
        "_call_openai",
        AsyncMock(return_value=generated),
    )

    result = await Direct3DRenderService("test-key").generate(request, capture)

    output = Image.open(io.BytesIO(base64.b64decode(result.image_base64))).convert("RGB")
    source_pixels = np.asarray(capture.source_beauty)
    output_pixels = np.asarray(output)
    exterior = np.asarray(capture.source_proposal_mask) == 0
    assert output.size == capture.source_beauty.size
    assert not np.array_equal(output_pixels[exterior], source_pixels[exterior])
    assert result.diagnostics["processing_mode"] == "scene"
    assert result.diagnostics["view_lock"] == "camera_registered"
    assert result.diagnostics["context_restyled"] is True
    assert result.diagnostics["provider_first"] is True
    assert result.diagnostics["finish_fusion"] is None
    assert result.diagnostics["object_id_proposal_recall"] == pytest.approx(1.0)
    assert result.diagnostics["object_id_proposal_iou"] == pytest.approx(1.0)
    assert result.diagnostics["minimum_object_id_proposal_recall"] == 0.85
    assert result.diagnostics["minimum_object_id_proposal_iou"] == 0.84
    assert result.diagnostics["scene_lower_context_coverage"] >= 0.08
    assert result.diagnostics["minimum_scene_lower_context_coverage"] == 0.08
    assert result.diagnostics["macro_design_fidelity"]["passed"] is True
    assert (
        result.diagnostics["macro_design_fidelity"][
            "building_internal_edges_required"
        ]
        is False
    )
    assert result.diagnostics["visual_change"]["passed"] is True
    assert (
        result.diagnostics["visual_change"][
            "minimum_whole_frame_mean_absolute_delta"
        ]
        == 5.0
    )
    assert (
        result.diagnostics["visual_change"][
            "minimum_proposal_mean_absolute_delta"
        ]
        == 12.0
    )
    assert result.diagnostics["visual_change"]["context_change_required"] is True
    assert (
        result.diagnostics["macro_design_fidelity"][
            "minimum_silhouette_edge_recall"
        ]
        == 0.80
    )
    assert (
        result.diagnostics["macro_design_fidelity"][
            "maximum_reference_edge_p90_distance_px"
        ]
        <= 6.0
    )
    assert (
        result.diagnostics["macro_design_fidelity"][
            "minimum_candidate_coarse_edge_precision"
        ]
        == 0.40
    )
    assert (
        result.diagnostics["macro_design_fidelity"][
            "maximum_candidate_coarse_edge_density_ratio"
        ]
        == 3.0
    )
    assert (
        result.diagnostics["visual_change"][
            "minimum_context_detail_delta_p75"
        ]
        == 0.75
    )
    assert result.diagnostics["registration"]["maximum_translation_norm_px"] == 8.0
    assert (
        result.diagnostics["registration"]["maximum_abs_rotation_degrees"]
        == 0.35
    )
    assert result.diagnostics["exterior_max_channel_delta"] > 0
    Direct3DRenderDiagnostics.model_validate(result.diagnostics)


@pytest.mark.asyncio
async def test_scene_mode_rejects_gross_moved_or_merged_proposal_geometry(monkeypatch):
    beauty, mask, _object_id = _structured_scene()
    request = _request(
        beauty=beauty,
        mask=mask,
        presentation_mode="scene",
        style="development",
    )
    capture = prepare_direct_3d_capture(request)
    generated = capture.normalized_beauty.copy()
    draw = ImageDraw.Draw(generated)
    proposal_box = (
        generated.width // 10,
        generated.height // 10,
        generated.width * 9 // 10,
        generated.height * 9 // 10,
    )
    draw.rectangle(proposal_box, fill=(135, 150, 122))
    draw.rectangle(
        (
            generated.width * 3 // 20,
            generated.height // 4,
            generated.width * 17 // 20,
            generated.height * 11 // 20,
        ),
        fill=(198, 181, 154),
        outline=(42, 43, 48),
        width=7,
    )
    monkeypatch.setattr(
        Direct3DRenderService,
        "_call_openai",
        AsyncMock(return_value=generated),
    )

    with pytest.raises(Direct3DProviderError, match="macro design geometry") as exc_info:
        await Direct3DRenderService("test-key").generate(request, capture)

    assert exc_info.value.billing_status == "produced"
    assert exc_info.value.provider_image_base64 is not None


@pytest.mark.asyncio
async def test_scene_mode_rejects_near_identity_colour_grade_only(monkeypatch):
    beauty, mask, _object_id = _structured_scene()
    request = _request(
        beauty=beauty,
        mask=mask,
        presentation_mode="scene",
        style="photorealistic",
    )
    capture = prepare_direct_3d_capture(request)
    generated_pixels = np.asarray(capture.normalized_beauty).copy()
    proposal = np.asarray(capture.normalized_proposal_mask) >= 128
    generated_pixels[proposal] = np.clip(
        generated_pixels[proposal].astype(np.int16) + np.asarray([12, 8, 6]),
        0,
        255,
    ).astype(np.uint8)
    generated = Image.fromarray(generated_pixels, mode="RGB")
    monkeypatch.setattr(
        Direct3DRenderService,
        "_call_openai",
        AsyncMock(return_value=generated),
    )

    with pytest.raises(Direct3DProviderError, match="photographic detail") as exc_info:
        await Direct3DRenderService("test-key").generate(request, capture)

    assert exc_info.value.billing_status == "produced"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("translation_x", "translation_y", "rotation", "message"),
    [
        (8.01, 0.0, 0.0, "8px translation limit"),
        (0.0, 0.0, 0.351, "0.35 degree rotation limit"),
    ],
)
async def test_scene_mode_rejects_camera_drift_beyond_scene_limits(
    monkeypatch,
    translation_x,
    translation_y,
    rotation,
    message,
):
    beauty, mask = _registration_context_scene()
    request = _request(
        beauty=beauty,
        mask=mask,
        presentation_mode="scene",
        style="documentary",
    )
    capture = prepare_direct_3d_capture(request)
    generated = _style_shift_without_geometry_change(capture.normalized_beauty)
    monkeypatch.setattr(
        Direct3DRenderService,
        "_call_openai",
        AsyncMock(return_value=generated),
    )
    monkeypatch.setattr(
        direct_service,
        "register_generated_image",
        MagicMock(
            return_value=direct_service.RegistrationResult(
                image=generated,
                method="ecc-euclidean",
                score=0.9,
                score_metric="luminance-correlation",
                photometric_score=0.9,
                structural_context_score=None,
                translation_x_px=translation_x,
                translation_y_px=translation_y,
                rotation_degrees=rotation,
            )
        ),
    )

    with pytest.raises(Direct3DProviderError, match=message) as exc_info:
        await Direct3DRenderService("test-key").generate(request, capture)

    assert exc_info.value.billing_status == "produced"


@pytest.mark.asyncio
async def test_reproject_returns_provider_output_without_screen_registration(monkeypatch):
    beauty, mask = _registration_context_scene()
    request = _request(
        beauty=beauty,
        mask=mask,
        presentation_mode="reproject",
        style="isometric",
    )
    capture = prepare_direct_3d_capture(request)
    generated = _limited_palette_line_finish_preserving_layout(
        capture.normalized_beauty
    )
    monkeypatch.setattr(
        Direct3DRenderService,
        "_call_openai",
        AsyncMock(return_value=generated),
    )
    register = MagicMock(side_effect=AssertionError("registration must be bypassed"))
    macro = MagicMock(side_effect=AssertionError("macro gate must be bypassed"))
    monkeypatch.setattr(direct_service, "register_generated_image", register)
    monkeypatch.setattr(direct_service, "assess_macro_design_fidelity", macro)

    result = await Direct3DRenderService("test-key").generate(request, capture)

    output = Image.open(io.BytesIO(base64.b64decode(result.image_base64))).convert("RGB")
    assert output.size == capture.normalized_beauty.size
    assert np.array_equal(np.asarray(output), np.asarray(generated))
    assert result.diagnostics["processing_mode"] == "reproject"
    assert result.diagnostics["view_lock"] == "not_applicable_layout_guided"
    assert result.diagnostics["registration"] is None
    assert result.diagnostics["provider_first"] is True
    assert result.diagnostics["reproject_output_sanity"]["passed"] is True
    assert (
        result.diagnostics["reproject_output_sanity"][
            "semantic_inventory_proxy_only"
        ]
        is True
    )
    Direct3DRenderDiagnostics.model_validate(result.diagnostics)
    register.assert_not_called()
    macro.assert_not_called()


@pytest.mark.asyncio
async def test_reproject_rejects_solid_provider_output(monkeypatch):
    beauty, mask = _registration_context_scene()
    request = _request(
        beauty=beauty,
        mask=mask,
        presentation_mode="reproject",
        style="isometric",
    )
    capture = prepare_direct_3d_capture(request)
    generated = Image.new("RGB", capture.normalized_beauty.size, (23, 91, 177))
    monkeypatch.setattr(
        Direct3DRenderService,
        "_call_openai",
        AsyncMock(return_value=generated),
    )

    sanity = assess_reproject_output_sanity(
        capture.normalized_beauty,
        generated,
    )
    assert sanity.structural_edge_coverage == 0.0
    assert sanity.passed is False
    with pytest.raises(Direct3DProviderError, match="content sanity") as exc_info:
        await Direct3DRenderService("test-key").generate(request, capture)

    assert exc_info.value.billing_status == "produced"


def test_reproject_sanity_rejects_random_noise():
    beauty, _mask = _registration_context_scene()
    noise = Image.fromarray(
        np.random.default_rng(20260722).integers(
            0,
            256,
            size=(beauty.height, beauty.width, 3),
            dtype=np.uint8,
        ),
        mode="RGB",
    )

    result = assess_reproject_output_sanity(beauty, noise)

    assert result.structural_edge_coverage > 0.30
    assert result.passed is False


@pytest.mark.asyncio
async def test_direct_endpoint_canonicalizes_frontend_data_url_before_audit(monkeypatch):
    request = _request(data_urls=True)
    prepared = prepare_direct_3d_capture(request)
    generated = prepared.normalized_beauty.copy()
    events: list[str] = []

    async def fake_reserve(*args, **kwargs):
        events.append("reserve")
        return SimpleNamespace(id=uuid.uuid4(), tokens_spent=13)

    async def fake_provider(*args, **kwargs):
        events.append("provider")
        return generated

    async def fake_finalize(*args, **kwargs):
        events.append("audit")

    reserve_mock = AsyncMock(side_effect=fake_reserve)
    provider_mock = AsyncMock(side_effect=fake_provider)
    finalize_mock = AsyncMock(side_effect=fake_finalize)
    monkeypatch.setattr(direct_api, "_reserve_direct_render", reserve_mock)
    monkeypatch.setattr(Direct3DRenderService, "_call_openai", provider_mock)
    monkeypatch.setattr(direct_api, "_finalize_direct_audit", finalize_mock)
    monkeypatch.setattr(
        direct_api,
        "get_settings",
        lambda: SimpleNamespace(openai_api_key="test-key", render_global_daily_token_cap=0),
    )
    db = _project_preflight_db(monkeypatch)
    user = SimpleNamespace(role="admin", email="admin@example.com", id="admin")

    response = await direct_api.generate_direct_3d_render(request, user=user, db=db)

    assert response.model == "gpt-image-2"
    assert response.diagnostics.mask_retry_used is False
    assert response.diagnostics.finish_fusion is not None
    assert response.diagnostics.finish_fusion.sigma_px > 0
    assert response.diagnostics.provider_raw_structural_edge_fidelity is not None
    assert events == ["reserve", "provider", "audit"]
    assert reserve_mock.await_args.kwargs["token_cost"] == estimate_direct_3d_token_cost(
        prepared.normalized_beauty.width,
        prepared.normalized_beauty.height,
        object_id_attached=False,
    )
    audited_input = finalize_mock.await_args.kwargs["input_b64"]
    assert not audited_input.startswith("data:")
    audited_image = Image.open(io.BytesIO(base64.b64decode(audited_input, validate=True)))
    assert audited_image.format == "PNG"
    assert audited_image.size == (512, 512)
    assert finalize_mock.await_args.kwargs["status_label"] == "success source-anchored"
    assert "mode=source_anchored" in finalize_mock.await_args.kwargs["detail"]


@pytest.mark.asyncio
async def test_success_audit_marks_provider_first_scene_final(monkeypatch):
    request = _request(presentation_mode="scene", style="development")
    prepared = prepare_direct_3d_capture(request)
    result = _fake_service_result(prepared.audit_input_base64)
    result.diagnostics.update({
        "processing_mode": "scene",
        "view_lock": "camera_registered",
        "context_restyled": True,
        "provider_first": True,
    })
    finalize_mock = AsyncMock()
    monkeypatch.setattr(
        direct_api,
        "_reserve_direct_render",
        AsyncMock(return_value=SimpleNamespace(id=uuid.uuid4(), tokens_spent=13)),
    )
    monkeypatch.setattr(
        Direct3DRenderService,
        "generate",
        AsyncMock(return_value=result),
    )
    monkeypatch.setattr(direct_api, "_finalize_direct_audit", finalize_mock)
    monkeypatch.setattr(
        direct_api,
        "get_settings",
        lambda: SimpleNamespace(openai_api_key="test-key", render_global_daily_token_cap=0),
    )

    response = await direct_api.generate_direct_3d_render(
        request,
        user=SimpleNamespace(role="admin", email="admin@example.com", id="admin"),
        db=_project_preflight_db(monkeypatch),
    )

    assert response.diagnostics.processing_mode == "scene"
    assert response.diagnostics.provider_first is True
    assert finalize_mock.await_args.kwargs["status_label"] == (
        "success provider-first scene"
    )
    assert "mode=scene style=development" in finalize_mock.await_args.kwargs["detail"]


@pytest.mark.asyncio
async def test_direct_endpoint_refunds_when_provider_produces_no_image(monkeypatch):
    request = _request()
    reservation = SimpleNamespace(id=uuid.uuid4(), tokens_spent=13)
    reserve_mock = AsyncMock(return_value=reservation)
    refund_mock = AsyncMock()
    finalize_mock = AsyncMock()
    monkeypatch.setattr(direct_api, "_reserve_direct_render", reserve_mock)
    monkeypatch.setattr(direct_api, "_refund_unproduced_direct_render", refund_mock)
    monkeypatch.setattr(direct_api, "_finalize_direct_audit", finalize_mock)
    monkeypatch.setattr(
        Direct3DRenderService,
        "generate",
        AsyncMock(
            side_effect=Direct3DProviderError(
                "provider unavailable",
                billing_status="unproduced",
            )
        ),
    )
    monkeypatch.setattr(
        direct_api,
        "get_settings",
        lambda: SimpleNamespace(openai_api_key="test-key", render_global_daily_token_cap=0),
    )

    with pytest.raises(HTTPException) as exc_info:
        await direct_api.generate_direct_3d_render(
            request,
            user=SimpleNamespace(role="admin", email="admin@example.com", id=uuid.uuid4()),
            db=_project_preflight_db(monkeypatch),
        )

    assert exc_info.value.status_code == 502
    assert exc_info.value.detail["code"] == "direct_3d_unproduced_refunded"
    assert exc_info.value.detail["billed"] is False
    reserve_mock.assert_awaited_once()
    refund_mock.assert_awaited_once()
    finalize_mock.assert_not_awaited()


@pytest.mark.asyncio
async def test_direct_endpoint_keeps_charge_and_audits_post_provider_safety_failure(monkeypatch):
    request = _request()
    reservation = SimpleNamespace(id=uuid.uuid4(), tokens_spent=13)
    provider_output = _png_b64(Image.new("RGB", (816, 816), "orange"))
    reserve_mock = AsyncMock(return_value=reservation)
    refund_mock = AsyncMock()
    finalize_mock = AsyncMock()
    monkeypatch.setattr(direct_api, "_reserve_direct_render", reserve_mock)
    monkeypatch.setattr(direct_api, "_refund_unproduced_direct_render", refund_mock)
    monkeypatch.setattr(direct_api, "_finalize_direct_audit", finalize_mock)
    monkeypatch.setattr(
        Direct3DRenderService,
        "generate",
        AsyncMock(
            side_effect=Direct3DProviderError(
                "registration drift",
                billing_status="produced",
                provider_image_base64=provider_output,
            )
        ),
    )
    monkeypatch.setattr(
        direct_api,
        "get_settings",
        lambda: SimpleNamespace(openai_api_key="test-key", render_global_daily_token_cap=0),
    )

    with pytest.raises(HTTPException) as exc_info:
        await direct_api.generate_direct_3d_render(
            request,
            user=SimpleNamespace(role="admin", email="admin@example.com", id=uuid.uuid4()),
            db=_project_preflight_db(monkeypatch),
        )

    assert exc_info.value.status_code == 502
    assert exc_info.value.detail["code"] == "direct_3d_billed_safety_rejection"
    assert exc_info.value.detail["billed"] is True
    refund_mock.assert_not_awaited()
    finalize_mock.assert_awaited_once()
    assert finalize_mock.await_args.kwargs["output_b64"] == provider_output


@pytest.mark.asyncio
async def test_direct_endpoint_retains_ambiguous_reservation_with_stable_detail(monkeypatch):
    request = _request()
    reservation = SimpleNamespace(id=uuid.uuid4(), tokens_spent=13)
    refund_mock = AsyncMock()
    finalize_mock = AsyncMock()
    monkeypatch.setattr(
        direct_api,
        "_reserve_direct_render",
        AsyncMock(return_value=reservation),
    )
    monkeypatch.setattr(direct_api, "_refund_unproduced_direct_render", refund_mock)
    monkeypatch.setattr(direct_api, "_finalize_direct_audit", finalize_mock)
    monkeypatch.setattr(
        Direct3DRenderService,
        "generate",
        AsyncMock(
            side_effect=Direct3DProviderError(
                "read timed out after upload",
                billing_status="unknown",
            )
        ),
    )
    monkeypatch.setattr(
        direct_api,
        "get_settings",
        lambda: SimpleNamespace(openai_api_key="test-key", render_global_daily_token_cap=0),
    )

    with pytest.raises(HTTPException) as exc_info:
        await direct_api.generate_direct_3d_render(
            request,
            user=SimpleNamespace(role="admin", email="admin@example.com", id=uuid.uuid4()),
            db=_project_preflight_db(monkeypatch),
        )

    assert exc_info.value.status_code == 502
    assert exc_info.value.detail == {
        "code": "direct_3d_billing_unknown",
        "billed": True,
        "message": (
            "The provider request outcome could not be confirmed after submission; "
            "the reservation was conservatively retained. read timed out after upload"
        ),
    }
    refund_mock.assert_not_awaited()
    finalize_mock.assert_awaited_once()
    assert finalize_mock.await_args.kwargs["status_label"] == "billing unknown"


@pytest.mark.asyncio
async def test_reservation_charges_user_and_creates_cap_row_before_provider():
    user = SimpleNamespace(
        id=uuid.uuid4(),
        email="editor@example.com",
        role="editor",
        render_credits=100,
        credits_reset_at=datetime.now(timezone.utc),
    )
    db = SimpleNamespace(
        refresh=AsyncMock(),
        add=MagicMock(),
        commit=AsyncMock(),
        rollback=AsyncMock(),
    )

    reservation = await direct_api._reserve_direct_render(
        db,
        user,
        token_cost=13,
        daily_cap=0,
        prompt="test prompt",
        project_id=None,
    )

    assert user.render_credits == 87
    assert reservation.tokens_spent == 13
    assert reservation.model == "gpt-image-2"
    db.refresh.assert_awaited_once_with(user, with_for_update=True)
    db.commit.assert_awaited_once()
    db.rollback.assert_not_awaited()


@pytest.mark.asyncio
async def test_unproduced_refund_restores_credit_and_releases_cap_tokens():
    user = SimpleNamespace(
        id=uuid.uuid4(),
        email="editor@example.com",
        role="editor",
        render_credits=87,
    )
    reservation = SimpleNamespace(
        id=uuid.uuid4(),
        tokens_spent=13,
        prompt_preview="[Direct 3D reserved] test",
    )
    db = SimpleNamespace(
        refresh=AsyncMock(),
        add=MagicMock(),
        commit=AsyncMock(),
        rollback=AsyncMock(),
    )

    await direct_api._refund_unproduced_direct_render(
        db,
        user,
        reservation,
        token_cost=13,
        detail="provider returned no image",
    )

    assert user.render_credits == 100
    assert reservation.tokens_spent == 0
    assert "unbilled failure" in reservation.prompt_preview
    db.refresh.assert_awaited_once_with(user, with_for_update=True)
    db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_reservation_serializes_daily_cap_check_before_committing_row():
    token_total_result = SimpleNamespace(scalar=lambda: 10)
    db = SimpleNamespace(
        execute=AsyncMock(side_effect=[SimpleNamespace(), token_total_result]),
        add=MagicMock(),
        commit=AsyncMock(),
        rollback=AsyncMock(),
    )
    user = SimpleNamespace(
        id=uuid.uuid4(),
        email="admin@example.com",
        role="admin",
    )

    reservation = await direct_api._reserve_direct_render(
        db,
        user,
        token_cost=13,
        daily_cap=50,
        prompt="test prompt",
        project_id=None,
    )

    assert reservation.tokens_spent == 13
    assert db.execute.await_count == 2
    assert "pg_advisory_xact_lock" in str(db.execute.await_args_list[0].args[0])
    db.commit.assert_awaited_once()


def test_direct_route_is_registered_separately_from_classic_route():
    from app.api.v1.render import RenderRequest, router as classic_router

    paths = {route.path for route in direct_api.router.routes}
    classic_paths = {route.path for route in classic_router.routes}

    assert "/generate-direct-3d" in paths
    assert "/generate" not in paths
    assert "/generate" in classic_paths
    assert "presentation_mode" not in RenderRequest.model_fields
    assert "style" not in RenderRequest.model_fields
