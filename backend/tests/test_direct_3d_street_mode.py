"""Street view_mode contract for the Direct 3D pipeline (Stage 3 v1)."""

from types import SimpleNamespace
from unittest.mock import AsyncMock

import numpy as np
import pytest
from PIL import Image
from pydantic import ValidationError

from app.schemas.direct_3d_render import Direct3DRenderRequest
from app.services import direct_3d_render as direct_service, site_context
from app.services.direct_3d_render import (
    Direct3DProviderError,
    Direct3DRenderService,
    _presentation_prompt,
    prepare_direct_3d_capture,
)
from tests.test_direct_3d_render import _FakeResponse, _RecordingClient, _capture_images, _png_b64, _request


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


@pytest.mark.parametrize("with_coverage", [True, False])
async def test_street_context_is_attached_once_or_fails_before_the_image_provider(monkeypatch, with_coverage):
    location = {"latitude": 51.045535, "longitude": -114.067772, "heading": 90}
    request = Direct3DRenderRequest.model_validate({
        **_street_request().model_dump(), "street_view_context": location,
    })
    capture = prepare_direct_3d_capture(request)
    fixture = {
        "photo_base64": _png_b64(capture.normalized_beauty),
        "mime_type": "image/png",
        "pano_date": "2024-06",
        "pano_offset_m": 15.0,
    }
    lookup = AsyncMock(return_value=fixture if with_coverage else None)
    monkeypatch.setattr(site_context, "fetch_streetview_plate", lookup)
    monkeypatch.setattr(direct_service, "get_settings", lambda: SimpleNamespace(
        direct_3d_street_view_context_enabled=True, google_maps_api_key="test-maps-key",
    ))
    monkeypatch.setattr(direct_service.httpx, "AsyncClient", _RecordingClient)
    _RecordingClient.calls = []
    _RecordingClient.response = _FakeResponse(200, {"data": [{"b64_json": _png_b64(capture.normalized_beauty)}]})
    service = Direct3DRenderService("test-image-key")
    if with_coverage:
        result = await service.generate(request, capture)
        assert result.diagnostics["street_view_context"] == {"pano_date": "2024-06", "offset_m": 15.0}
        assert len(_RecordingClient.calls) == 1
        call = _RecordingClient.calls[0]
        assert call["files"][0][1][0] == "direct-3d-beauty.png"
        assert call["files"][-1][1][0] == "street-view-context.png"
        assert "EXISTING STREET REFERENCE" in call["data"]["prompt"]
    else:
        with pytest.raises(Direct3DProviderError, match="within 20 m") as error:
            await service.generate(request, capture)
        assert error.value.billing_status == "unproduced"
        assert _RecordingClient.calls == []
    lookup.assert_awaited_once()
    assert lookup.await_args.args[:3] == (location["latitude"], location["longitude"], location["heading"])
    assert lookup.await_args.kwargs == {"max_offset_m": 20}


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
