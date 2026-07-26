"""Street view_mode contract for the Direct 3D pipeline (Stage 3 v1)."""

import numpy as np
import pytest
from PIL import Image
from pydantic import ValidationError

from app.schemas.direct_3d_render import Direct3DRenderRequest
from app.services.direct_3d_render import (
    Direct3DValidationError,
    _presentation_prompt,
    prepare_direct_3d_capture,
)
from tests.test_direct_3d_render import _capture_images, _request


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


def _street_framed_mask(size: tuple[int, int]) -> Image.Image:
    """Proposal fills everything below a context (sky) band — a street frame.

    The top 30% context keeps the global >=10% immutable-context gate happy
    while leaving ZERO context in the lower band the aerial scene gate checks.
    """
    width, height = size
    pixels = np.full((height, width), 255, dtype=np.uint8)
    pixels[: int(height * 0.30), :] = 0
    return Image.fromarray(pixels, mode="L")


def test_prepare_skips_lower_context_gate_for_street():
    beauty = _capture_images()[0]
    mask = _street_framed_mask(beauty.size)

    aerial = _request(beauty=beauty, mask=mask, presentation_mode="scene")
    with pytest.raises(Direct3DValidationError, match="lower-frame context"):
        prepare_direct_3d_capture(aerial)

    street = Direct3DRenderRequest(**{**aerial.model_dump(), "view_mode": "street"})
    capture = prepare_direct_3d_capture(street)
    assert capture.scene_lower_context_coverage is None


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
