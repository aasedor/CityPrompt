from io import BytesIO
from types import SimpleNamespace
from unittest.mock import AsyncMock
from datetime import datetime, timezone
import uuid
import pytest
from PIL import Image
from shapely.geometry import box, shape, Polygon
from geoalchemy2.shape import from_shape
from app.services.site_landscape import (
    build_site_landscape,
    landscape_images,
    clip_custom_art,
    png_bytes,
    blend_site_edges,
)
from app.services.residual_landscape import ResidualSourceZone
from app.api.v1 import site_landscape as endpoint
from fastapi import HTTPException

BOUNDARY = box(-114.14, 51.01, -114.136, 51.013)
BUILDING = box(-114.139, 51.011, -114.1388, 51.0112)
ROUTE = [
    [-114.1391, 51.011],
    [-114.139, 51.011],
    [-114.139, 51.01],
    [-114.1391, 51.01],
    [-114.1391, 51.011],
]


def recipe(preset="gardens"):
    return build_site_landscape(
        BOUNDARY,
        [ResidualSourceZone("home", "building", BUILDING)],
        [ROUTE],
        preset,
        boundary_id="site",
        compiled_at="now",
    )


def test_presets_protect_buildings_routes_and_parcel():
    from shapely.geometry import Polygon

    results = [recipe(p) for p in ("gardens", "natural", "urban")]
    for value in results:
        ground = shape(value["geometry"])
        assert ground.intersection(BUILDING).area < 1e-14
        assert ground.intersection(Polygon(ROUTE)).area < 1e-14
        assert ground.difference(BOUNDARY).area < 1e-14
    assert any(r["kind"] == "meadow" for r in results[1]["regions"])
    assert any(r["kind"] == "shared_paving" for r in results[2]["regions"])
    assert len(results[2]["placements"]) < len(results[0]["placements"])


def test_custom_mask_never_bleeds_into_protected_holes_or_outside():
    _, _, mask = landscape_images(BOUNDARY, recipe(), 128)
    art = clip_custom_art(png_bytes(Image.new("RGB", (64, 64), "red")), mask)
    for allowed, alpha in zip(mask.tobytes(), art.getchannel("A").tobytes()):
        if allowed == 0:
            assert alpha == 0
    assert any(0 < a < 255 for a in art.getchannel("A").tobytes())


def test_transparent_provider_art_preserves_ground_and_protected_routes():
    mask = Image.new("L", (64, 64), 255)
    mask.paste(0, (28, 0, 36, 64))
    source = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    source.paste((80, 110, 70, 128), (0, 0, 24, 64))
    source.paste((80, 110, 70, 255), (28, 0, 36, 64))
    art = clip_custom_art(png_bytes(source), mask)
    assert art.getpixel((12, 32))[3] == 128
    assert art.getpixel((50, 32))[3] == 0
    assert art.getpixel((32, 32))[3] == 0
    # The real GPT pilot returned a different resolution than the mask.
    resized = clip_custom_art(png_bytes(source.resize((128, 128))), mask)
    assert resized.getpixel((50, 32))[3] == 0
    assert resized.getpixel((32, 32))[3] == 0


def test_continuous_base_covers_object_and_route_without_changing_tree_clearance():
    value = recipe()
    _, guide, mask = landscape_images(BOUNDARY, value, 256, base_surface=True)
    west, south, east, north = BOUNDARY.bounds

    def pixel(point):
        return (
            int((point.x - west) / (east - west) * mask.width),
            int((north - point.y) / (north - south) * mask.height),
        )

    for point in (BUILDING.centroid, Polygon(ROUTE).centroid):
        assert mask.getpixel(pixel(point)) == 255
        assert guide.getpixel(pixel(point)) != (119, 119, 119)
    assert mask.width < mask.height  # physical metre proportions at Calgary latitude
    remainder = shape(value["geometry"])
    assert remainder.intersection(BUILDING).area < 1e-14
    assert remainder.intersection(Polygon(ROUTE)).area < 1e-14


def test_context_colours_blend_only_inside_the_six_metre_edge_band():
    _, _, mask = landscape_images(BOUNDARY, recipe(), 256, base_surface=True)
    original = Image.new("RGBA", mask.size, (40, 90, 30, 255))
    samples = [{"lng": x, "lat": y, "color": [180, 170, 140]} for x, y in BOUNDARY.exterior.coords]
    blended = blend_site_edges(original, mask, BOUNDARY, samples)
    assert blended.getpixel((mask.width // 2, mask.height // 2)) == (40, 90, 30, 255)
    edge = blended.getpixel((0, mask.height // 2))
    assert edge[0] > 120 and edge[1] > 140
    assert blended.getchannel("A").tobytes() == original.getchannel("A").tobytes()


@pytest.mark.asyncio
async def test_landscape_default_cost_matches_gpt_25_renderer():
    from app.api.v1.render import _MODEL_TOKEN_COST

    options = await endpoint.landscape_options(SimpleNamespace())
    assert options["model"] == "gpt-image-2.5-flare"
    assert options["tokens"] == _MODEL_TOKEN_COST[options["model"]] == 26


@pytest.mark.asyncio
async def test_apply_rejects_modified_or_expired_preview_before_writing():
    payload = {"expires_at": 0, "recipe": {}}
    with pytest.raises(HTTPException) as error:
        await endpoint.apply_landscape(
            uuid.uuid4(),
            endpoint.LandscapeApplyRequest(preview=payload, signature=endpoint.signature(payload)),
            SimpleNamespace(),
            AsyncMock(),
        )
    assert error.value.status_code == 409
    payload["expires_at"] = 9999999999
    with pytest.raises(HTTPException):
        await endpoint.apply_landscape(
            uuid.uuid4(),
            endpoint.LandscapeApplyRequest(preview=payload, signature="0" * 64),
            SimpleNamespace(),
            AsyncMock(),
        )


@pytest.mark.asyncio
async def test_apply_rejects_changed_context_and_preserves_current_objects(monkeypatch):
    boundary = SimpleNamespace(
        id=uuid.uuid4(),
        project_id=uuid.uuid4(),
        properties={},
        geometry=from_shape(BOUNDARY, srid=4326),
    )
    payload = {
        "boundary_id": str(boundary.id),
        "project_id": str(boundary.project_id),
        "context_hash": "old",
        "expires_at": 9999999999,
        "recipe": recipe(),
    }
    monkeypatch.setattr(endpoint, "_get_zone_with_access", AsyncMock(return_value=boundary))
    monkeypatch.setattr(endpoint, "lock_residual_landscape_project", AsyncMock())
    monkeypatch.setattr(endpoint, "scene", AsyncMock(return_value=(boundary, [])))
    db = AsyncMock()
    with pytest.raises(HTTPException) as error:
        await endpoint.apply_landscape(
            boundary.id,
            endpoint.LandscapeApplyRequest(preview=payload, signature=endpoint.signature(payload)),
            SimpleNamespace(),
            db,
        )
    assert error.value.status_code == 409
    assert boundary.properties == {}
    db.flush.assert_not_awaited()


def test_preview_signature_survives_browser_number_serialization():
    assert endpoint.signature({"x": 1.0, "y": -0.0, "z": 1e-7}) == endpoint.signature({"x": 1, "y": 0, "z": 0.0000001})
    assert endpoint.signature({"p": (1.0, 2.0)}) == endpoint.signature({"p": [1, 2]})
    assert endpoint.signature({"x": 1}) != endpoint.signature({"x": 2})
    assert endpoint.signature({"x": 1}) != endpoint.signature({"x": ["number", "1"]})
    assert endpoint.signature({"x": 1}) != endpoint.signature({"x": "number:1"})


@pytest.mark.asyncio
@pytest.mark.parametrize("context_available", [True, False])
async def test_custom_preview_uses_budgeted_renderer_and_hard_clips_result(monkeypatch, context_available):
    from app.api.v1 import render

    boundary = SimpleNamespace(
        id=uuid.uuid4(),
        project_id=uuid.uuid4(),
        properties={},
        geometry=from_shape(BOUNDARY, srid=4326),
        updated_at=datetime.now(timezone.utc),
    )
    home = SimpleNamespace(
        id=uuid.uuid4(),
        zone_type="building",
        properties={},
        geometry=from_shape(BUILDING, srid=4326),
        updated_at=datetime.now(timezone.utc),
    )
    monkeypatch.setattr(endpoint, "_get_zone_with_access", AsyncMock(return_value=boundary))
    monkeypatch.setattr(endpoint, "scene", AsyncMock(return_value=(boundary, [home])))
    import base64

    mock_generate = AsyncMock(
        return_value=SimpleNamespace(
            image_base64=base64.b64encode(png_bytes(Image.new("RGB", (64, 64), "red"))).decode()
        )
    )
    monkeypatch.setattr(render, "generate_render", mock_generate)

    class Storage:
        def put_object(self, **kwargs):
            self.data = kwargs["Body"]

    storage = Storage()
    monkeypatch.setattr(endpoint.boto3, "client", lambda *a, **kw: storage)
    request = endpoint.LandscapePreviewRequest(
        preset="gardens",
        prompt="marble paving",
        context_image_base64=base64.b64encode(png_bytes(Image.new("RGB", (96, 96), "green"))).decode(),
        corridors=[ROUTE],
        context_edge_samples=[{"lng": -114.14, "lat": 51.01, "color": [160, 150, 120]}] * 8,
        revisions={str(z.id): z.updated_at.isoformat() for z in [boundary, home]},
    )
    if not context_available:
        request.context_image_base64 = None
        with pytest.raises(HTTPException) as error:
            await endpoint.preview_landscape(boundary.id, request, SimpleNamespace(), AsyncMock())
        assert error.value.status_code == 422
        mock_generate.assert_not_awaited()
        assert boundary.properties == {}
        return
    result = await endpoint.preview_landscape(boundary.id, request, SimpleNamespace(), AsyncMock())
    assert mock_generate.await_count == 1
    assert mock_generate.call_args.args[0].project_id == boundary.project_id
    assert mock_generate.call_args.args[0].mask_base64
    request_to_model = mock_generate.call_args.args[0]
    assert request_to_model.guide_image_kind == "landscape_base"
    assert request_to_model.model == "gpt-image-2.5-flare"
    assert request_to_model.image_quality == "high"
    assert result["preview"]["recipe"]["surface_mode"] == "site_base"
    assert "No interior cutouts" in request_to_model.prompt
    assert request_to_model.site_scene_reference_base64
    assert "surrounding Google tiles" in request_to_model.prompt
    assert "approximately" in request_to_model.prompt
    assert result["preview"]["recipe"]["surface_context"]["source"] == "development_with_google_tiles"
    assert result["preview"]["recipe"]["surface_image_url"].startswith(
        f"/api/v1/files/projects/{boundary.project_id}/landscape/"
    )
    assert result["signature"] == endpoint.signature(result["preview"])
    art = Image.open(BytesIO(storage.data))
    assert art.mode == "RGBA"
    # This rectangular site fills the whole frame, including authored plots.
    assert art.getchannel("A").getextrema() == (255, 255)
    assert boundary.properties == {}


def test_preview_rejects_nonfinite_corridor_coordinates():
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        endpoint.LandscapePreviewRequest(preset="gardens", revisions={}, corridors=[[(float("nan"), 51.0)]])


def test_scene_reference_is_bounded_and_invalid_images_rejected():
    import base64
    from app.services.site_landscape import normalize_scene_reference

    source = Image.new("RGB", (1600, 800), "green")
    value = normalize_scene_reference("data:image/png;base64," + base64.b64encode(png_bytes(source)).decode())
    assert Image.open(BytesIO(base64.b64decode(value))).size == (1280, 640)
    for bad in [
        "https://example.invalid/image.png",
        "not an image",
        base64.b64encode(png_bytes(Image.new("RGB", (1, 1)))).decode(),
    ]:
        with pytest.raises(ValueError, match="reference could not be read"):
            normalize_scene_reference(bad)
