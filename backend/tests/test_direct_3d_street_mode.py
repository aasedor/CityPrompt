"""Street view_mode contract for the Direct 3D pipeline (Stage 3 v1)."""

import base64
import io
from types import SimpleNamespace
from unittest.mock import AsyncMock

import httpx
import numpy as np
import pytest
from PIL import Image
from pydantic import ValidationError

from app.schemas.direct_3d_render import Direct3DRenderDiagnostics, Direct3DRenderRequest
from app.services import direct_3d_render as direct_service, site_context
from app.services.direct_3d_render import (
    Direct3DProviderError,
    Direct3DRenderService,
    Direct3DValidationError,
    _presentation_prompt,
    prepare_direct_3d_capture,
)
from tests.test_direct_3d_render import (
    _FakeResponse,
    _RecordingClient,
    _capture_images,
    _png_b64,
    _registration_context_scene,
    _request,
)


def _street_request(**overrides) -> Direct3DRenderRequest:
    base = _request(presentation_mode="scene", **overrides)
    return Direct3DRenderRequest(**{**base.model_dump(), "view_mode": "street"})


def test_view_mode_defaults_to_aerial():
    assert _request().view_mode == "aerial"


def test_street_requires_scene_presentation():
    base = _request(presentation_mode="reproject", style="site-plan")
    with pytest.raises(ValidationError, match="street"):
        Direct3DRenderRequest(**{**base.model_dump(), "view_mode": "street"})


def test_street_with_scene_is_valid():
    assert _street_request().view_mode == "street"


def test_aerial_requests_reject_street_view_context():
    payload = _request(presentation_mode="scene").model_dump()
    payload["street_view_context"] = {"latitude": 51.045535, "longitude": -114.067772, "heading": 90}
    with pytest.raises(ValidationError, match="street"):
        Direct3DRenderRequest.model_validate(payload)


@pytest.fixture
def existing_streetscape_request() -> Direct3DRenderRequest:
    beauty, _ = _capture_images()
    mask = Image.new("L", beauty.size, 0)
    black = _png_b64(Image.new("RGB", beauty.size))
    base = _street_request(beauty=beauty, mask=mask)
    identity = [float(index % 5 == 0) for index in range(16)]
    return Direct3DRenderRequest.model_validate(
        {
            **base.model_dump(),
            "street_view_context": {"latitude": 51.045347, "longitude": -114.058216, "heading": 257},
            "control_bundle_version": 2,
            "depth_image_base64": _png_b64(mask),
            "normal_image_base64": _png_b64(mask),
            "material_id_image_base64": black,
            "material_id_manifest": {"#020002": {"material_id": "wall", "label": "Wall", "semantic_class": "building"}},
            "camera": {
                "projection": "perspective",
                "projection_matrix": identity,
                "matrix_world": identity,
                "position": [0, 0, 10],
                "quaternion": [0, 0, 0, 1],
                "fov": 70,
            },
        }
    )


def test_street_view_accepts_a_camera_with_no_proposed_objects_in_frame(existing_streetscape_request):
    capture = prepare_direct_3d_capture(existing_streetscape_request)

    assert capture.proposal_coverage == 0
    assert capture.object_id_coverage == 0
    assert capture.instance_id_coverage == 0
    assert capture.normalized_material_id is not None


@pytest.mark.parametrize(
    ("field", "color"),
    [
        ("object_id_image_base64", (255, 0, 0)),
        ("instance_id_image_base64", (1, 0, 1)),
        ("material_id_image_base64", (2, 0, 2)),
    ],
)
def test_street_view_rejects_colored_proposal_ids_with_an_empty_mask(existing_streetscape_request, field, color):
    invalid_ids = Image.new("RGB", _capture_images()[0].size)
    invalid_ids.putpixel((0, 0), color)
    request = existing_streetscape_request.model_copy(update={field: _png_b64(invalid_ids)})

    with pytest.raises(Direct3DValidationError, match="ID image must be black"):
        prepare_direct_3d_capture(request)


@pytest.mark.parametrize(
    ("coverage", "context_only"),
    [("available", False), ("available", True), ("missing", False), ("invalid", False)],
)
async def test_street_context_is_attached_once_or_fails_before_the_image_provider(
    monkeypatch,
    coverage,
    context_only,
    existing_streetscape_request,
):
    location = {"latitude": 51.045535, "longitude": -114.067772, "heading": 90}
    base = existing_streetscape_request if context_only else _street_request()
    request = Direct3DRenderRequest.model_validate(
        {
            **base.model_dump(),
            "prompt": "Use the selected finish for the photographed streetscape and visible design.",
            "street_view_context": location,
        }
    )
    capture = prepare_direct_3d_capture(request)
    photo = _png_b64(Image.new("RGB", (640, 360), (28, 69, 47)))
    fixture = {
        "photo_base64": photo,
        "mime_type": "image/png",
        "pano_date": "2024-06",
        "pano_offset_m": 15.0,
    }
    if coverage == "invalid":
        fixture["photo_base64"] = "invalid-image"
    lookup = AsyncMock(return_value=None if coverage == "missing" else fixture)
    monkeypatch.setattr(site_context, "fetch_streetview_plate", lookup)
    monkeypatch.setattr(
        direct_service,
        "get_settings",
        lambda: SimpleNamespace(
            direct_3d_street_view_context_enabled=True,
            google_maps_api_key="test-maps-key",
        ),
    )
    monkeypatch.setattr(direct_service.httpx, "AsyncClient", _RecordingClient)
    _RecordingClient.calls = []
    _RecordingClient.response = _FakeResponse(200, {"data": [{"b64_json": _png_b64(capture.normalized_beauty)}]})
    service = Direct3DRenderService("test-image-key")
    if coverage == "available":
        result = await service.generate(request, capture)
        assert Direct3DRenderDiagnostics.model_validate(result.diagnostics).structural_edge_guide_attached is False
        assert result.diagnostics["street_view_context"] == {"pano_date": "2024-06", "offset_m": 15.0}
        assert len(_RecordingClient.calls) == 1
        call = _RecordingClient.calls[0]
        attachments = [attachment[1] for attachment in call["files"]]
        assert attachments[0] == ("street-view-context.png", base64.b64decode(photo), "image/png")
        prompt = call["data"]["prompt"]
        assert "Image 1 is the Street View photo" in prompt
        assert all(detail in prompt for detail in ("tree canopies", "open plazas", "entrance steps"))
        street_reference = prompt.split("EXISTING STREET REFERENCE: ", 1)[1]
        assert all(
            detail in street_reference
            for detail in ("temporary", "painted concrete barriers", "mural patterns", "spacing", "pedestrian gaps")
        )
        assert "only permanent features" not in street_reference
        if context_only:
            assert len(attachments) == 1
            assert "Image 2" not in prompt
        else:
            assert len(attachments) == 2
            assert attachments[1][0] == "direct-3d-authored-design.png"
            with Image.open(io.BytesIO(attachments[1][1])) as guide:
                assert guide.size == capture.normalized_beauty.size
                pixels = np.asarray(guide)
            mask = np.asarray(capture.normalized_proposal_mask)
            assert np.all(pixels[mask == 0] == 128)
            assert np.array_equal(pixels[mask == 255], np.asarray(capture.normalized_beauty)[mask == 255])
            assert "Image 2 is the authored design" in prompt
        assert "Preserve any people or vehicles already captured" not in prompt
        assert "photos guide appearance only" not in prompt
        assert "class-ID metadata" not in prompt
    else:
        message = "within 20 m" if coverage == "missing" else "invalid image"
        with pytest.raises(Direct3DProviderError, match=message) as error:
            await service.generate(request, capture)
        assert error.value.billing_status == "unproduced"
        assert _RecordingClient.calls == []
    lookup.assert_awaited_once()
    assert lookup.await_args.args[:3] == (location["latitude"], location["longitude"], location["heading"])
    assert lookup.await_args.kwargs == {"max_offset_m": 20}


async def test_unchecked_street_render_keeps_its_3d_guides_and_skips_photo_lookup(monkeypatch):
    request = _street_request()
    capture = prepare_direct_3d_capture(request)
    lookup = AsyncMock()
    monkeypatch.setattr(site_context, "fetch_streetview_plate", lookup)
    monkeypatch.setattr(
        direct_service,
        "get_settings",
        lambda: SimpleNamespace(direct_3d_street_view_context_enabled=True, google_maps_api_key="test-maps-key"),
    )
    monkeypatch.setattr(direct_service.httpx, "AsyncClient", _RecordingClient)
    _RecordingClient.calls = []
    _RecordingClient.response = _FakeResponse(200, {"data": [{"b64_json": _png_b64(capture.normalized_beauty)}]})

    result = await Direct3DRenderService("test-image-key").generate(request, capture)

    lookup.assert_not_awaited()
    assert result.diagnostics["structural_edge_guide_attached"] is True
    assert not result.diagnostics.get("street_view_context")
    (call,) = _RecordingClient.calls
    assert [attachment[1][0] for attachment in call["files"]] == [
        "direct-3d-beauty.png",
        "direct-3d-class-id.png",
        "direct-3d-instance-id.png",
        "direct-3d-structural-edges.png",
    ]
    assert "EXISTING STREET REFERENCE:" not in call["data"]["prompt"]


@pytest.mark.parametrize("with_photo", [False, True])
async def test_registered_street_finish_keeps_photo_guided_context_changes_only_when_requested(monkeypatch, with_photo):
    beauty, mask = _registration_context_scene()
    base = _street_request(beauty=beauty, mask=mask)
    request = Direct3DRenderRequest.model_validate(
        {
            **base.model_dump(),
            "street_view_context": (
                {"latitude": 51.045395, "longitude": -114.058189, "heading": 99} if with_photo else None
            ),
        }
    )
    capture = prepare_direct_3d_capture(request)
    source = np.asarray(capture.normalized_beauty)
    exterior = np.asarray(capture.normalized_proposal_mask) == 0
    candidate = source.copy()
    candidate[exterior] = np.clip(source[exterior].astype(np.int16) + 8, 0, 255).astype(np.uint8)
    monkeypatch.setattr(Direct3DRenderService, "_call_openai", AsyncMock(return_value=Image.fromarray(candidate)))

    result = await Direct3DRenderService("test-image-key").generate(request, capture)

    assert result.outcome == "review_required"
    assert result.diagnostics["provider_spatial_pixels_retained"]
    assert result.diagnostics["context_restyled"] is with_photo
    with Image.open(io.BytesIO(base64.b64decode(result.image_base64))) as image:
        assert image.getpixel((0, 0)) == tuple(candidate[0, 0] if with_photo else source[0, 0])


async def test_street_view_uses_newest_aligned_outdoor_panorama(monkeypatch):
    lat, lng = 51.045347, -114.058216
    image_requests = []

    def google(request: httpx.Request) -> httpx.Response:
        params = request.url.params
        if request.url.path.endswith("/metadata"):
            sample_lat, sample_lng = map(float, params["location"].split(","))
            if sample_lng < lng - 0.00006:
                pano, date, position = "too-far", "2026-11", (lat, lng - 0.0004)
            elif sample_lat > lat + 0.00004:
                pano, date, position = "too-far-sideways", "2026-10", (lat + 0.00012, lng)
            elif sample_lng > lng + 0.00005:
                pano, date, position = "july", "2026-07", (lat + 0.000021, lng + 0.000065)
            elif sample_lat < lat - 0.00004:
                pano, date, position = "same-month-farther", "2026-07", (lat - 0.00005, lng + 0.0001)
            else:
                pano, date, position = "nearest", "2017-06", (lat, lng)
            return httpx.Response(
                200,
                json={
                    "status": "OK",
                    "pano_id": pano,
                    "date": date,
                    "location": {"lat": position[0], "lng": position[1]},
                },
            )
        image_requests.append(params)
        return httpx.Response(200, headers={"content-type": "image/jpeg"}, content=b"july-photo")

    async_client = httpx.AsyncClient
    monkeypatch.setattr(
        site_context.httpx,
        "AsyncClient",
        lambda **kwargs: async_client(transport=httpx.MockTransport(google), **kwargs),
    )
    monkeypatch.setattr(site_context, "get_settings", lambda: SimpleNamespace(google_maps_api_key="test-maps-key"))

    plate = await site_context.fetch_streetview_plate(lat, lng, 82.5, 125, 640, 235, max_offset_m=20)

    assert plate is not None
    assert plate["pano_date"] == "2026-07"
    assert plate["pano_offset_m"] == pytest.approx(5.1, abs=0.2)
    assert [params["pano"] for params in image_requests] == ["july"]
    assert float(image_requests[0]["heading"]) == 82.5
    assert float(image_requests[0]["fov"]) == 120
    assert image_requests[0]["size"] == "640x235"


async def test_street_view_can_use_an_undated_match_when_other_metadata_requests_fail(monkeypatch):
    lat, lng = 51.045347, -114.058216

    def google(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/metadata"):
            _, sample_lng = map(float, request.url.params["location"].split(","))
            if sample_lng <= lng:
                raise httpx.ReadTimeout("metadata did not arrive", request=request)
            return httpx.Response(
                200, json={"status": "OK", "pano_id": "undated", "location": {"lat": lat, "lng": lng + 0.00005}}
            )
        assert request.url.params["pano"] == "undated"
        return httpx.Response(200, headers={"content-type": "image/jpeg"}, content=b"undated-photo")

    async_client = httpx.AsyncClient
    monkeypatch.setattr(
        site_context.httpx,
        "AsyncClient",
        lambda **kwargs: async_client(transport=httpx.MockTransport(google), **kwargs),
    )
    monkeypatch.setattr(site_context, "get_settings", lambda: SimpleNamespace(google_maps_api_key="test-maps-key"))

    plate = await site_context.fetch_streetview_plate(lat, lng, 90, 90, 640, 360, max_offset_m=20)

    assert plate is not None
    assert plate["pano_date"] is None
    assert plate["pano_offset_m"] == pytest.approx(3.5, abs=0.1)


async def test_street_view_rejects_placeholder_when_panorama_image_is_unavailable(monkeypatch):
    lat, lng = 51.045535, -114.067772

    def google(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/metadata"):
            return httpx.Response(
                200, json={"status": "OK", "pano_id": "test-pano", "location": {"lat": lat, "lng": lng}}
            )
        if request.url.params.get("return_error_code") == "true":
            return httpx.Response(404)
        return httpx.Response(200, headers={"content-type": "image/jpeg"}, content=b"placeholder")

    async_client = httpx.AsyncClient
    monkeypatch.setattr(
        site_context.httpx,
        "AsyncClient",
        lambda **kwargs: async_client(transport=httpx.MockTransport(google), **kwargs),
    )
    monkeypatch.setattr(site_context, "get_settings", lambda: SimpleNamespace(google_maps_api_key="test-maps-key"))
    assert await site_context.fetch_streetview_plate(lat, lng, 90, 90, 640, 360, max_offset_m=20) is None


def _street_framed_mask(size: tuple[int, int]) -> Image.Image:
    """Proposal fills everything below a context (sky) band — a street frame.

    The top 30% is context, with no context in the lower band.
    Both aerial close-ups and street views legitimately use this framing.
    """
    width, height = size
    pixels = np.full((height, width), 255, dtype=np.uint8)
    pixels[: int(height * 0.30), :] = 0
    return Image.fromarray(pixels, mode="L")


def test_prepare_accepts_closeup_framing_for_aerial_and_street():
    beauty = _capture_images()[0]
    mask = _street_framed_mask(beauty.size)

    aerial = _request(beauty=beauty, mask=mask, presentation_mode="scene")
    assert prepare_direct_3d_capture(aerial).scene_lower_context_coverage == 0.0

    street = Direct3DRenderRequest(**{**aerial.model_dump(), "view_mode": "street"})
    capture = prepare_direct_3d_capture(street)
    assert capture.scene_lower_context_coverage == 0.0


def test_presentation_prompt_street_framing():
    aerial = _presentation_prompt(
        "warm brick",
        presentation_mode="scene",
        style="photorealistic",
        object_id_manifest={"#FF0000": "building"},
    )
    street = _presentation_prompt(
        "warm brick",
        presentation_mode="scene",
        style="photorealistic",
        object_id_manifest={"#FF0000": "building"},
        view_mode="street",
    )
    assert "street-level" not in aerial
    assert "street-level" in street
    assert "pedestrian standpoint" in street
    assert "never merge, float or stack" in street
    # The inventory lock must still close the prompt in street mode.
    assert street.rstrip().endswith("buildings.")
