"""Fail-closed Direct 3D image refinement through GPT Image 2.

The colored-polygon renderer deliberately remains separate.  This service
accepts a clean, authoritative 3D viewport capture, validates its proposal
mask, and makes exactly one request. Legacy mode applies a masked,
source-anchored finish; presentation modes use provider-first scene or
projection contracts with mode-appropriate design gates.
"""

from __future__ import annotations

import base64
import binascii
import hashlib
import io
import json
import logging
import math
from dataclasses import asdict, dataclass, fields
from typing import Any, Literal

import httpx
import numpy as np
from PIL import Image, ImageDraw

from app.schemas.direct_3d_render import Direct3DRenderRequest
from app.services.render_fidelity import RENDER_PRESERVATION_LOCK

logger = logging.getLogger(__name__)

DIRECT_3D_MODEL = "gpt-image-2"
# Presentation-first keeps photographic finish rather than transferring only
# tone. Same-camera finishes must now pass measured source agreement, and
# uncertain/failed checks return the clean source. All generative views remain
# review-required; a 2D comparison cannot certify exact 3D identity.
DIRECT_3D_PRESENTATION_FIRST = True
_OPENAI_EDIT_URL = "https://api.openai.com/v1/images/edits"
_MIN_PROVIDER_PIXELS = 655_360
DIRECT_3D_MAX_SOURCE_EDGE = 2_048
DIRECT_3D_MAX_SOURCE_PIXELS = 4_194_304
DIRECT_3D_MAX_PROVIDER_PIXELS = 3_686_400
# Direct 3D credit envelope, reviewed 2026-07-20. Credits cost $0.005 each.
# The 41-token/MP output allowance conservatively covers GPT Image 2 high
# reference pricing ($0.211 at 1024²; $0.165 at 1536×1024), while the fixed
# terms reserve high-fidelity input processing for beauty + optional class ID.
DIRECT_3D_OUTPUT_TOKENS_PER_MEGAPIXEL = 41
DIRECT_3D_BASE_INPUT_TOKENS = 4
DIRECT_3D_CLASS_ID_INPUT_TOKENS = 2
DIRECT_3D_INSTANCE_ID_INPUT_TOKENS = 2
DIRECT_3D_STRUCTURAL_GUIDE_INPUT_TOKENS = 2
DIRECT_3D_DEPTH_INPUT_TOKENS = 2
DIRECT_3D_NORMAL_INPUT_TOKENS = 2
DIRECT_3D_MATERIAL_ID_INPUT_TOKENS = 2
DIRECT_3D_MIN_TOKEN_COST = 13
_MAX_PROVIDER_PIXELS = DIRECT_3D_MAX_PROVIDER_PIXELS
_MAX_PROVIDER_EDGE = DIRECT_3D_MAX_SOURCE_EDGE
_EDGE_MULTIPLE = 16
_MIN_PROPOSAL_COVERAGE = 0.0025
_MAX_PROPOSAL_COVERAGE = 0.85
_MIN_PRESENTATION_OBJECT_ID_PROPOSAL_RECALL = 0.85
_MIN_PRESENTATION_OBJECT_ID_PROPOSAL_IOU = 0.84
_MIN_PRESENTATION_INSTANCE_ID_PROPOSAL_RECALL = 0.85
_MIN_PRESENTATION_INSTANCE_ID_PROPOSAL_IOU = 0.84
_MIN_REGISTRATION_SCORE = 0.65
_IDENTITY_SCORE = 0.985
_MIN_STRUCTURAL_CONTEXT_SCORE = 0.62
_MIN_STRUCTURAL_CONTEXT_EDGE_PIXELS = 256
_MAX_REGISTRATION_ROTATION_DEGREES = 2.0
# Scene registration drift is evidence for review/fallback selection, not a
# reason to discard an otherwise valid (and already billed) provider result.
# Precise work has the tightest automatic-acceptance envelope; expressive work
# permits more corrected camera motion before review.  The source-lock limits
# are deliberately wider: crossing them removes every provider spatial pixel
# from the return path while retaining only global colour statistics.
_SCENE_REGISTRATION_REVIEW_LIMITS: dict[str, tuple[float, float]] = {
    "precise": (6.0, 0.25),
    "balanced": (8.0, 0.35),
    "expressive": (12.0, 0.50),
}
_SCENE_REGISTRATION_SOURCE_LOCK_LIMITS: dict[str, tuple[float, float]] = {
    "precise": (12.0, 0.75),
    "balanced": (16.0, 1.00),
    "expressive": (24.0, 1.50),
}
_INWARD_FEATHER_PX = 2.0
_MIN_STRUCTURAL_EDGE_PIXELS = 64
_MIN_BEAUTY_EDGE_RECALL = 0.55
_MIN_COARSE_EDGE_RECALL = 0.58
_MIN_SEMANTIC_EDGE_RECALL = 0.76
_MIN_SEMANTIC_COMPONENT_RECALL = 0.68
_MIN_BUILDING_INTERNAL_EDGE_RECALL = 0.68
_MIN_MACRO_SILHOUETTE_EDGE_RECALL = 0.80
_MIN_MACRO_COARSE_EDGE_RECALL = 0.70
_MIN_MACRO_SEMANTIC_EDGE_RECALL = 0.78
_MIN_MACRO_SEMANTIC_COMPONENT_RECALL = 0.72
_MAX_MACRO_REFERENCE_P90_TOLERANCE_MULTIPLIER = 2.5
_MAX_MACRO_REFERENCE_P90_DISTANCE_PX = 6.0
_MIN_MACRO_CANDIDATE_COARSE_EDGE_PRECISION = 0.40
_MAX_MACRO_CANDIDATE_COARSE_EDGE_DENSITY_RATIO = 3.0
_MIN_SCENE_WHOLE_FRAME_MEAN_ABSOLUTE_DELTA = 5.0
_MIN_SCENE_PROPOSAL_MEAN_ABSOLUTE_DELTA = 12.0
_MIN_SCENE_PROPOSAL_DETAIL_DELTA_P75 = 3.0
_MIN_SCENE_NOVEL_DETAIL_EDGE_COVERAGE = 0.0015
_MIN_SCENE_PROPOSAL_PHOTOMETRIC_RESIDUAL_P95 = 6.0
_MIN_SCENE_CONTEXT_MEAN_ABSOLUTE_DELTA = 4.0
_MIN_SCENE_CONTEXT_PHOTOMETRIC_RESIDUAL_P95 = 4.0
_MIN_SCENE_CONTEXT_DETAIL_DELTA_P75 = 0.75
_SCENE_CONTEXT_TOP_FRACTION = 0.45
_MIN_SCENE_LOWER_CONTEXT_COVERAGE = 0.08
_MAX_SCENE_LOCAL_REPAIR_COVERAGE = 0.30
_MIN_REPROJECT_WHOLE_FRAME_MEAN_ABSOLUTE_DELTA = 8.0
_MIN_REPROJECT_LUMINANCE_STANDARD_DEVIATION = 10.0
_MIN_REPROJECT_LUMINANCE_DYNAMIC_RANGE_P90 = 35.0
_MIN_REPROJECT_STRUCTURAL_EDGE_COVERAGE = 0.002
_MAX_REPROJECT_STRUCTURAL_EDGE_COVERAGE = 0.30
_MIN_REPROJECT_OCCUPIED_EDGE_CELLS = 4
_FINISH_FUSION_REFERENCE_DIAGONAL = math.hypot(1280, 720)
_FINISH_FUSION_SIGMA_AT_REFERENCE_PX = 8.0
_FINISH_FUSION_RGB_DELTA_CLIP = 48.0
_FINISH_FUSION_DEFAULT_STRENGTH = 0.35
_FINISH_FUSION_ROLE_STRENGTHS = {
    "building": 0.24,
    "ground": 0.42,
    "landscape": 0.50,
    "street": 0.34,
    "park": 0.44,
}
# Source-owned material detail is remapped toward provider contrast, never
# replaced by provider structure.  The two caps correspond to the fine and
# medium source Laplacian bands respectively.
_FINISH_DETAIL_FINE_SIGMA_AT_REFERENCE_PX = 1.0
_FINISH_DETAIL_MEDIUM_SIGMA_AT_REFERENCE_PX = 3.5
_FINISH_DETAIL_CORRECTION_CLIP = 12.0
_FINISH_DETAIL_DEFAULT_GAIN_CAPS = (1.08, 1.15)
_FINISH_DETAIL_ROLE_GAIN_CAPS = {
    "building": (1.08, 1.24),
    "ground": (1.12, 1.25),
    "landscape": (1.04, 1.08),
    "street": (1.12, 1.25),
    "park": (1.06, 1.18),
}
_FINISH_DETAIL_MIN_ROBUST_CONTRAST = 0.05

# Provider high-frequency spatial phase is never copied.  Provider contrast is
# reduced to one robust statistic per role, then used to remap the source's own
# microtexture phase in protected interiors.  A nearly flat source may become
# subtly material rather than perfectly synthetic, but an exactly flat source
# remains flat and a provider-only roofline can never enter this term.
_FINISH_MICROTEXTURE_SIGMA_AT_REFERENCE_PX = 0.8
_FINISH_MICROTEXTURE_CORRECTION_CLIP = 3.0
_FINISH_MICROTEXTURE_DEFAULT_GAIN_CAP = 3.0
_FINISH_MICROTEXTURE_ROLE_GAIN_CAPS = {
    "building": 8.00,
    "ground": 4.00,
    "landscape": 1.10,
    "street": 1.25,
    "park": 1.15,
}
_FINISH_INTERIOR_EROSION_RADIUS_AT_REFERENCE_PX = 3
_FINISH_EDGE_DILATION_RADIUS_AT_REFERENCE_PX = 4
_FINISH_INTERIOR_FEATHER_AT_REFERENCE_PX = 3.0
_FINISH_LOW_GRADIENT_PERCENTILE = 65.0
_FINISH_LOW_GRADIENT_CAP = 48.0
_FINISH_MIN_ROLE_STAT_PIXELS = 24
_KNOWN_UNBILLED_PROVIDER_STATUSES = {400, 401, 403, 404, 409, 413, 415, 422, 429}


class Direct3DValidationError(ValueError):
    """The capture or generated result failed a geometry-safety check."""


class Direct3DProviderError(RuntimeError):
    """GPT Image 2 rejected the request or returned unusable image data."""

    def __init__(
        self,
        message: str,
        *,
        billing_status: Literal["unproduced", "produced", "unknown"],
        provider_image_base64: str | None = None,
    ) -> None:
        super().__init__(message)
        self.billing_status = billing_status
        self.refund_eligible = billing_status == "unproduced"
        self.provider_image_produced = billing_status == "produced"
        self.provider_image_base64 = provider_image_base64


@dataclass(frozen=True)
class PreparedDirect3DCapture:
    source_beauty: Image.Image
    source_proposal_mask: Image.Image
    normalized_beauty: Image.Image
    normalized_proposal_mask: Image.Image
    normalized_object_id: Image.Image | None
    normalized_instance_id: Image.Image | None
    normalized_depth: Image.Image | None
    normalized_normal: Image.Image | None
    normalized_material_id: Image.Image | None
    proposal_coverage: float
    object_id_coverage: float | None
    object_id_proposal_recall: float | None
    object_id_proposal_iou: float | None
    instance_id_coverage: float | None
    instance_id_proposal_recall: float | None
    instance_id_proposal_iou: float | None
    instance_count: int
    material_count: int
    scene_lower_context_coverage: float | None
    capture_fingerprint: str
    audit_input_base64: str


@dataclass(frozen=True)
class RegistrationResult:
    image: Image.Image
    method: str
    score: float
    score_metric: str
    photometric_score: float
    structural_context_score: float | None
    translation_x_px: float
    translation_y_px: float
    rotation_degrees: float


@dataclass(frozen=True)
class StructuralEdgeFidelityResult:
    """Directed edge-agreement measurements inside the editable proposal."""

    passed: bool
    tolerance_px: int
    reference_edge_pixels: int
    candidate_edge_pixels: int
    beauty_edge_recall: float
    coarse_edge_pixels: int
    coarse_edge_recall: float
    semantic_edge_pixels: int
    semantic_edge_recall: float | None
    semantic_component_min_recall: float | None
    building_internal_edge_pixels: int
    building_internal_edge_recall: float | None
    reference_edge_p90_distance_px: float


@dataclass(frozen=True)
class MacroDesignFidelityResult:
    """Macro design agreement for a provider-first, camera-locked scene."""

    passed: bool
    tolerance_px: int
    silhouette_edge_pixels: int
    silhouette_edge_recall: float | None
    coarse_edge_pixels: int
    coarse_edge_recall: float
    semantic_edge_pixels: int
    semantic_edge_recall: float | None
    evaluated_component_count: int
    semantic_component_min_recall: float | None
    reference_edge_p90_distance_px: float
    candidate_coarse_edge_pixels: int
    candidate_coarse_edge_precision: float
    candidate_coarse_edge_density_ratio: float


@dataclass(frozen=True)
class MacroFidelityThresholds:
    minimum_silhouette_edge_recall: float
    minimum_coarse_edge_recall: float
    minimum_semantic_edge_recall: float
    minimum_semantic_component_recall: float
    maximum_reference_p90_distance_px: float
    minimum_candidate_coarse_edge_precision: float
    maximum_candidate_coarse_edge_density_ratio: float


@dataclass(frozen=True)
class InstanceSourcePresenceResult:
    passed: bool
    evaluated_instance_count: int
    weakest_instance_recall: float | None
    missing_instance_ids: tuple[str, ...]
    instance_recalls: dict[str, float | None]


@dataclass(frozen=True)
class UnsupportedStructureResult:
    passed: bool
    largest_component_pixels: int
    largest_component_bbox_fraction: float
    proposal_component_count: int
    context_component_count: int


@dataclass(frozen=True)
class VisualChangeResult:
    """Measured scene enhancement beyond a near-identity colour grade."""

    passed: bool
    whole_frame_mean_absolute_delta: float
    proposal_mean_absolute_delta: float
    proposal_detail_delta_p75: float
    proposal_photometric_residual_p95: float
    novel_detail_edge_coverage: float
    context_mean_absolute_delta: float
    context_photometric_residual_p95: float
    context_detail_delta_p75: float
    context_pixel_count: int
    context_frame_top_fraction: float


@dataclass(frozen=True)
class ReprojectOutputSanityResult:
    """Deterministic minimum-content checks for a projection-changing result."""

    passed: bool
    whole_frame_mean_absolute_delta: float
    luminance_standard_deviation: float
    luminance_dynamic_range_p90: float
    structural_edge_coverage: float
    occupied_edge_cells: int
    significant_edge_component_count: int
    required_edge_component_count: int


@dataclass(frozen=True)
class FinishFusionResult:
    """Source-anchored finish image plus auditable material-transfer metrics."""

    image: Image.Image
    diagnostics: dict[str, Any]


@dataclass(frozen=True)
class Direct3DServiceResult:
    image_base64: str
    audit_input_base64: str
    capture_fingerprint: str
    output_fingerprint: str
    diagnostics: dict[str, Any]
    outcome: Literal["accepted", "review_required"] = "accepted"
    warnings: tuple[str, ...] = ()
    # Untouched provider image (canonical PNG b64) regardless of which safety
    # strategy shaped image_base64. The user paid for this image; the API layer
    # persists it to the gallery whenever a fallback replaced it.
    provider_image_base64: str | None = None


def estimate_direct_3d_token_cost(
    normalized_width: int,
    normalized_height: int,
    *,
    object_id_attached: bool,
    instance_id_attached: bool = False,
    control_bundle_version: Literal[1, 2] = 1,
) -> int:
    """Return the conservative credit reservation for one Direct 3D edit."""

    if normalized_width <= 0 or normalized_height <= 0:
        raise ValueError("Normalized Direct 3D dimensions must be positive")
    megapixels = normalized_width * normalized_height / 1_000_000
    estimated = math.ceil(
        DIRECT_3D_OUTPUT_TOKENS_PER_MEGAPIXEL * megapixels
        + DIRECT_3D_BASE_INPUT_TOKENS
        + (DIRECT_3D_CLASS_ID_INPUT_TOKENS if object_id_attached else 0)
        + (DIRECT_3D_INSTANCE_ID_INPUT_TOKENS if instance_id_attached else 0)
        + (
            DIRECT_3D_DEPTH_INPUT_TOKENS + DIRECT_3D_NORMAL_INPUT_TOKENS + DIRECT_3D_MATERIAL_ID_INPUT_TOKENS
            if control_bundle_version == 2
            else 0
        )
        + DIRECT_3D_STRUCTURAL_GUIDE_INPUT_TOKENS
    )
    return max(DIRECT_3D_MIN_TOKEN_COST, estimated)


def _decode_base64_payload(value: str, *, label: str) -> bytes:
    payload = value.split(",", 1)[1] if "," in value[:128] else value
    try:
        return base64.b64decode(payload, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise Direct3DValidationError(f"{label} is not valid base64") from exc


def _load_image(raw: bytes, *, label: str, allowed_formats: set[str]) -> Image.Image:
    try:
        image = Image.open(io.BytesIO(raw))
    except Image.DecompressionBombError as exc:
        raise Direct3DValidationError(f"{label} exceeds the safe decoded-image limit") from exc
    except Exception as exc:
        raise Direct3DValidationError(f"{label} is not a readable image") from exc

    image_format = (image.format or "").upper()
    if image_format not in allowed_formats:
        formats = ", ".join(sorted(allowed_formats))
        raise Direct3DValidationError(f"{label} must use one of these formats: {formats}")
    width, height = image.size
    if width <= 0 or height <= 0 or width > DIRECT_3D_MAX_SOURCE_EDGE or height > DIRECT_3D_MAX_SOURCE_EDGE:
        image.close()
        raise Direct3DValidationError(
            f"{label} decoded dimensions must each be between 1 and " f"{DIRECT_3D_MAX_SOURCE_EDGE} pixels"
        )
    if width * height > DIRECT_3D_MAX_SOURCE_PIXELS:
        image.close()
        raise Direct3DValidationError(f"{label} exceeds the {DIRECT_3D_MAX_SOURCE_PIXELS}-pixel decoded-image limit")
    try:
        if getattr(image, "n_frames", 1) != 1:
            raise Direct3DValidationError(f"{label} must be a single-frame image")
    except Image.DecompressionBombError as exc:
        raise Direct3DValidationError(f"{label} exceeds the safe decoded-image limit") from exc
    try:
        image.load()
    except Image.DecompressionBombError as exc:
        raise Direct3DValidationError(f"{label} exceeds the safe decoded-image limit") from exc
    except Exception as exc:
        raise Direct3DValidationError(f"{label} is not a readable image") from exc
    if getattr(image, "n_frames", 1) != 1:
        raise Direct3DValidationError(f"{label} must be a single-frame image")
    return image


def _extract_proposal_alpha(mask: Image.Image) -> Image.Image:
    """Read proposal coverage from alpha, or luminance for RGB capture masks."""

    if mask.mode in {"RGBA", "LA"}:
        alpha = mask.getchannel("A")
        extrema = alpha.getextrema()
        # An opaque black/white PNG from WebGL carries its signal in RGB.  A
        # non-constant alpha channel is treated as the authoritative signal.
        if extrema[0] != extrema[1]:
            return alpha
    return mask.convert("L")


def _registration_context_mask(proposal_mask: Image.Image) -> np.ndarray:
    """Return context pixels that remain fully immutable after edge erosion."""

    import cv2

    proposal = np.asarray(proposal_mask.convert("L"), dtype=np.uint8)
    context_mask = np.where(proposal <= 4, 255, 0).astype(np.uint8)
    return cv2.erode(
        context_mask,
        np.ones((5, 5), dtype=np.uint8),
        iterations=1,
    )


def _scene_lower_context_mask(proposal_mask: Image.Image) -> np.ndarray:
    """Return mask-zero context in the lower, predominantly non-sky frame."""

    proposal = np.asarray(proposal_mask.convert("L"), dtype=np.uint8) >= 128
    lower_context = np.zeros(proposal.shape, dtype=bool)
    start_row = min(
        proposal_mask.height - 1,
        max(0, round(proposal_mask.height * _SCENE_CONTEXT_TOP_FRACTION)),
    )
    lower_context[start_row:, :] = True
    return lower_context & ~proposal


def _normalized_dimensions(width: int, height: int) -> tuple[int, int]:
    """Choose an explicit GPT Image 2 size while preserving capture aspect.

    GPT Image 2 accepts arbitrary dimensions within broader provider limits,
    but this product tier accepts source captures up to 2048 px while keeping
    provider output at or below the reviewed 3,686,400-pixel non-experimental
    ceiling. Search near the required scale for the valid 16-pixel-multiple
    pair with the least aspect-ratio error.
    """

    if width <= 0 or height <= 0:
        raise Direct3DValidationError("Capture dimensions must be positive")
    aspect = width / height
    if not (1 / 3 <= aspect <= 3):
        raise Direct3DValidationError("Direct 3D capture aspect ratio must be between 1:3 and 3:1")

    pixels = width * height
    scale = 1.0
    if pixels < _MIN_PROVIDER_PIXELS:
        scale = math.sqrt(_MIN_PROVIDER_PIXELS / pixels)
    if pixels * scale * scale > _MAX_PROVIDER_PIXELS:
        scale = math.sqrt(_MAX_PROVIDER_PIXELS / pixels)
    if max(width, height) * scale > _MAX_PROVIDER_EDGE:
        scale = _MAX_PROVIDER_EDGE / max(width, height)

    target_width = width * scale
    target_height = height * scale
    center_w = max(_EDGE_MULTIPLE, round(target_width / _EDGE_MULTIPLE) * _EDGE_MULTIPLE)
    center_h = max(_EDGE_MULTIPLE, round(target_height / _EDGE_MULTIPLE) * _EDGE_MULTIPLE)

    candidates: list[tuple[float, float, int, int]] = []
    for delta_w in range(-12, 13):
        candidate_w = center_w + delta_w * _EDGE_MULTIPLE
        if candidate_w <= 0 or candidate_w > _MAX_PROVIDER_EDGE:
            continue
        for delta_h in range(-12, 13):
            candidate_h = center_h + delta_h * _EDGE_MULTIPLE
            if candidate_h <= 0 or candidate_h > _MAX_PROVIDER_EDGE:
                continue
            candidate_pixels = candidate_w * candidate_h
            candidate_aspect = candidate_w / candidate_h
            if not (_MIN_PROVIDER_PIXELS <= candidate_pixels <= _MAX_PROVIDER_PIXELS):
                continue
            if not (1 / 3 <= candidate_aspect <= 3):
                continue
            aspect_error = abs(math.log(candidate_aspect / aspect))
            scale_error = abs(candidate_w - target_width) / max(target_width, 1) + abs(
                candidate_h - target_height
            ) / max(target_height, 1)
            candidates.append((aspect_error, scale_error, candidate_w, candidate_h))

    if not candidates:
        raise Direct3DValidationError("Could not normalize capture to a valid GPT Image 2 size")

    _, _, normalized_width, normalized_height = min(candidates)
    if abs((normalized_width / normalized_height) / aspect - 1.0) > 0.01:
        raise Direct3DValidationError("Normalized capture would distort the source aspect ratio")
    return normalized_width, normalized_height


def _hex_to_rgb(value: str) -> tuple[int, int, int]:
    return tuple(int(value[index : index + 2], 16) for index in (1, 3, 5))  # type: ignore[return-value]


def _capture_fingerprint(
    beauty: Image.Image,
    proposal_mask: Image.Image,
    object_id: Image.Image | None,
    manifest: dict[str, str] | None,
    instance_id: Image.Image | None = None,
    instance_manifest: dict[str, Any] | None = None,
    depth: Image.Image | None = None,
    normal: Image.Image | None = None,
    material_id: Image.Image | None = None,
    material_manifest: dict[str, Any] | None = None,
    camera: Any | None = None,
    bundle_version: Literal[1, 2] = 1,
) -> str:
    digest = hashlib.sha256(f"siteforge-direct-3d-capture-v{bundle_version}\0".encode("ascii"))
    digest.update(beauty.width.to_bytes(4, "big"))
    digest.update(beauty.height.to_bytes(4, "big"))
    digest.update(beauty.tobytes())
    digest.update(proposal_mask.tobytes())
    if object_id is not None:
        digest.update(object_id.tobytes())
    if manifest:
        digest.update(json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode("utf-8"))
    if instance_id is not None:
        digest.update(instance_id.tobytes())
    if instance_manifest:
        serializable_manifest = {
            color: (descriptor.model_dump(mode="json") if hasattr(descriptor, "model_dump") else descriptor)
            for color, descriptor in instance_manifest.items()
        }
        digest.update(
            json.dumps(
                serializable_manifest,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        )
    for image in (depth, normal, material_id):
        if image is not None:
            digest.update(image.tobytes())
    if material_manifest:
        serializable_materials = {
            color: (descriptor.model_dump(mode="json") if hasattr(descriptor, "model_dump") else descriptor)
            for color, descriptor in material_manifest.items()
        }
        digest.update(json.dumps(serializable_materials, sort_keys=True, separators=(",", ":")).encode("utf-8"))
    if camera is not None:
        serializable_camera = camera.model_dump(mode="json") if hasattr(camera, "model_dump") else camera
        digest.update(json.dumps(serializable_camera, sort_keys=True, separators=(",", ":")).encode("utf-8"))
    return digest.hexdigest()


def prepare_direct_3d_capture(req: Direct3DRenderRequest) -> PreparedDirect3DCapture:
    beauty_raw = _decode_base64_payload(req.beauty_image_base64, label="beauty_image_base64")
    mask_raw = _decode_base64_payload(req.proposal_mask_base64, label="proposal_mask_base64")
    beauty_image = _load_image(
        beauty_raw,
        label="beauty_image_base64",
        allowed_formats={"PNG", "JPEG", "WEBP"},
    ).convert("RGB")
    mask_image = _load_image(
        mask_raw,
        label="proposal_mask_base64",
        allowed_formats={"PNG"},
    )

    width, height = beauty_image.size
    if width < 256 or height < 256 or width > DIRECT_3D_MAX_SOURCE_EDGE or height > DIRECT_3D_MAX_SOURCE_EDGE:
        raise Direct3DValidationError(
            "Direct 3D beauty capture dimensions must each be between 256 and " f"{DIRECT_3D_MAX_SOURCE_EDGE} pixels"
        )
    if width * height > DIRECT_3D_MAX_SOURCE_PIXELS:
        raise Direct3DValidationError(
            "Direct 3D beauty capture exceeds the " f"{DIRECT_3D_MAX_SOURCE_PIXELS}-pixel source limit"
        )
    if mask_image.size != beauty_image.size:
        raise Direct3DValidationError("Proposal mask dimensions must exactly match the beauty capture")

    proposal_mask = _extract_proposal_alpha(mask_image)
    proposal_values = np.asarray(proposal_mask, dtype=np.float32) / 255.0
    proposal_coverage = float(proposal_values.mean())
    if not (_MIN_PROPOSAL_COVERAGE <= proposal_coverage <= _MAX_PROPOSAL_COVERAGE):
        raise Direct3DValidationError(
            "Proposal coverage must be between "
            f"{_MIN_PROPOSAL_COVERAGE:.2%} and {_MAX_PROPOSAL_COVERAGE:.0%}; "
            f"received {proposal_coverage:.2%}"
        )

    if req.capture:
        if (req.capture.width, req.capture.height) != beauty_image.size:
            raise Direct3DValidationError("Client capture dimensions do not match decoded pixels")
        if abs(req.capture.proposal_coverage - proposal_coverage) > 0.005:
            raise Direct3DValidationError("Client proposal coverage does not match decoded mask pixels")

    object_id_image: Image.Image | None = None
    object_id_coverage: float | None = None
    object_id_proposal_recall: float | None = None
    object_id_proposal_iou: float | None = None
    if req.object_id_image_base64 and req.object_id_manifest:
        object_id_raw = _decode_base64_payload(
            req.object_id_image_base64,
            label="object_id_image_base64",
        )
        object_id_image = _load_image(
            object_id_raw,
            label="object_id_image_base64",
            allowed_formats={"PNG"},
        ).convert("RGB")
        if object_id_image.size != beauty_image.size:
            raise Direct3DValidationError("Object-ID image dimensions must exactly match the beauty capture")

        object_pixels = np.asarray(object_id_image)
        classified = np.zeros((height, width), dtype=bool)
        for color in req.object_id_manifest:
            rgb = np.asarray(_hex_to_rgb(color), dtype=np.uint8)
            classified |= np.all(object_pixels == rgb, axis=2)
        object_id_coverage = float(classified.mean())
        if object_id_coverage < _MIN_PROPOSAL_COVERAGE:
            raise Direct3DValidationError("Object-ID image does not contain enough classified proposal pixels")
        proposal_active = proposal_values >= 0.5
        intersection_count = int(np.count_nonzero(classified & proposal_active))
        proposal_count = int(np.count_nonzero(proposal_active))
        union_count = int(np.count_nonzero(classified | proposal_active))
        object_id_proposal_recall = float(intersection_count / max(1, proposal_count))
        object_id_proposal_iou = float(intersection_count / max(1, union_count))
        outside = proposal_values < (8 / 255)
        leak_count = int(np.count_nonzero(classified & outside))
        classified_count = int(np.count_nonzero(classified))
        if leak_count / max(classified_count, 1) > 0.01:
            raise Direct3DValidationError("Object-ID classes extend materially outside the proposal mask")
        if req.presentation_mode in {"scene", "reproject"} and (
            object_id_proposal_recall < _MIN_PRESENTATION_OBJECT_ID_PROPOSAL_RECALL
            or object_id_proposal_iou < _MIN_PRESENTATION_OBJECT_ID_PROPOSAL_IOU
        ):
            raise Direct3DValidationError(
                "Presentation object-ID classes must cover the proposal "
                f"(recall {object_id_proposal_recall:.3f}, "
                f"IoU {object_id_proposal_iou:.3f})"
            )
    elif req.presentation_mode in {"scene", "reproject"}:
        raise Direct3DValidationError("Presentation modes require an object-ID image and manifest")

    instance_id_image: Image.Image | None = None
    instance_id_coverage: float | None = None
    instance_id_proposal_recall: float | None = None
    instance_id_proposal_iou: float | None = None
    if req.instance_id_image_base64 and req.instance_id_manifest:
        instance_id_raw = _decode_base64_payload(
            req.instance_id_image_base64,
            label="instance_id_image_base64",
        )
        instance_id_image = _load_image(
            instance_id_raw,
            label="instance_id_image_base64",
            allowed_formats={"PNG"},
        ).convert("RGB")
        if instance_id_image.size != beauty_image.size:
            raise Direct3DValidationError("Instance-ID image dimensions must exactly match the beauty capture")

        instance_pixels = np.asarray(instance_id_image)
        classified_instances = np.zeros((height, width), dtype=bool)
        semantic_pixels = np.asarray(object_id_image) if object_id_image is not None else None
        semantic_colors: dict[str, np.ndarray] = {}
        if req.object_id_manifest:
            for color, semantic_class in req.object_id_manifest.items():
                semantic_colors[semantic_class] = semantic_colors.get(
                    semantic_class,
                    np.zeros((height, width), dtype=bool),
                ) | np.all(
                    semantic_pixels == np.asarray(_hex_to_rgb(color), dtype=np.uint8),
                    axis=2,
                )

        for color, descriptor in req.instance_id_manifest.items():
            rgb = np.asarray(_hex_to_rgb(color), dtype=np.uint8)
            matches = np.all(instance_pixels == rgb, axis=2)
            classified_instances |= matches
            if np.any(matches) and semantic_colors:
                expected_semantic_pixels = semantic_colors.get(
                    descriptor.semantic_class,
                    np.zeros((height, width), dtype=bool),
                )
                agreement = float(np.mean(expected_semantic_pixels[matches]))
                if agreement < 0.90:
                    raise Direct3DValidationError(
                        "Instance-ID semantic class conflicts with the class-ID image "
                        f"for {descriptor.instance_id!r} (agreement {agreement:.3f})"
                    )

        non_black = np.any(instance_pixels != 0, axis=2)
        unmanifested_count = int(np.count_nonzero(non_black & ~classified_instances))
        if unmanifested_count:
            raise Direct3DValidationError(
                "Instance-ID image contains non-black colors absent from "
                f"instance_id_manifest ({unmanifested_count} pixels)"
            )

        instance_id_coverage = float(classified_instances.mean())
        if instance_id_coverage < _MIN_PROPOSAL_COVERAGE:
            raise Direct3DValidationError("Instance-ID image does not contain enough classified proposal pixels")
        proposal_active = proposal_values >= 0.5
        intersection_count = int(np.count_nonzero(classified_instances & proposal_active))
        proposal_count = int(np.count_nonzero(proposal_active))
        union_count = int(np.count_nonzero(classified_instances | proposal_active))
        instance_id_proposal_recall = float(intersection_count / max(1, proposal_count))
        instance_id_proposal_iou = float(intersection_count / max(1, union_count))
        outside = proposal_values < (8 / 255)
        leak_count = int(np.count_nonzero(classified_instances & outside))
        classified_count = int(np.count_nonzero(classified_instances))
        if leak_count / max(classified_count, 1) > 0.01:
            raise Direct3DValidationError("Instance-ID classes extend materially outside the proposal mask")
        if req.presentation_mode in {"scene", "reproject"} and (
            instance_id_proposal_recall < _MIN_PRESENTATION_INSTANCE_ID_PROPOSAL_RECALL
            or instance_id_proposal_iou < _MIN_PRESENTATION_INSTANCE_ID_PROPOSAL_IOU
        ):
            raise Direct3DValidationError(
                "Presentation instance-ID classes must cover the proposal "
                f"(recall {instance_id_proposal_recall:.3f}, "
                f"IoU {instance_id_proposal_iou:.3f})"
            )
    elif req.presentation_mode in {"scene", "reproject"}:
        raise Direct3DValidationError("Presentation modes require an instance-ID image and manifest")

    depth_image: Image.Image | None = None
    normal_image: Image.Image | None = None
    for field_name, payload in (
        ("depth_image_base64", req.depth_image_base64),
        ("normal_image_base64", req.normal_image_base64),
    ):
        if not payload:
            continue
        image = _load_image(
            _decode_base64_payload(payload, label=field_name),
            label=field_name,
            allowed_formats={"PNG"},
        ).convert("RGB")
        if image.size != beauty_image.size:
            raise Direct3DValidationError(f"{field_name} dimensions must exactly match the beauty capture")
        if field_name == "depth_image_base64":
            depth_image = image
        else:
            normal_image = image

    material_id_image: Image.Image | None = None
    if req.material_id_image_base64 and req.material_id_manifest:
        material_id_image = _load_image(
            _decode_base64_payload(
                req.material_id_image_base64,
                label="material_id_image_base64",
            ),
            label="material_id_image_base64",
            allowed_formats={"PNG"},
        ).convert("RGB")
        if material_id_image.size != beauty_image.size:
            raise Direct3DValidationError("Material-ID image dimensions must exactly match the beauty capture")
        material_pixels = np.asarray(material_id_image)
        classified_materials = np.zeros((height, width), dtype=bool)
        semantic_pixels = np.asarray(object_id_image) if object_id_image is not None else None
        semantic_colors: dict[str, np.ndarray] = {}
        if req.object_id_manifest and semantic_pixels is not None:
            for color, semantic_class in req.object_id_manifest.items():
                semantic_colors[semantic_class] = semantic_colors.get(
                    semantic_class,
                    np.zeros((height, width), dtype=bool),
                ) | np.all(
                    semantic_pixels == np.asarray(_hex_to_rgb(color), dtype=np.uint8),
                    axis=2,
                )
        for color, descriptor in req.material_id_manifest.items():
            matches = np.all(
                material_pixels == np.asarray(_hex_to_rgb(color), dtype=np.uint8),
                axis=2,
            )
            classified_materials |= matches
            if np.any(matches) and semantic_colors:
                expected_semantic = semantic_colors.get(
                    descriptor.semantic_class,
                    np.zeros((height, width), dtype=bool),
                )
                agreement = float(np.mean(expected_semantic[matches]))
                if agreement < 0.90:
                    raise Direct3DValidationError(
                        "Material-ID semantic class conflicts with the class-ID image "
                        f"for {descriptor.material_id!r} (agreement {agreement:.3f})"
                    )
        non_black = np.any(material_pixels != 0, axis=2)
        unmanifested_count = int(np.count_nonzero(non_black & ~classified_materials))
        if unmanifested_count:
            raise Direct3DValidationError(
                "Material-ID image contains non-black colors absent from "
                f"material_id_manifest ({unmanifested_count} pixels)"
            )
        proposal_active = proposal_values >= 0.5
        intersection_count = int(np.count_nonzero(classified_materials & proposal_active))
        proposal_count = int(np.count_nonzero(proposal_active))
        union_count = int(np.count_nonzero(classified_materials | proposal_active))
        material_recall = float(intersection_count / max(1, proposal_count))
        material_iou = float(intersection_count / max(1, union_count))
        if material_recall < 0.85 or material_iou < 0.84:
            raise Direct3DValidationError(
                "Material-ID classes must cover the proposal " f"(recall {material_recall:.3f}, IoU {material_iou:.3f})"
            )

    normalized_size = _normalized_dimensions(width, height)
    normalized_beauty = beauty_image.resize(normalized_size, Image.Resampling.LANCZOS)
    normalized_mask = proposal_mask.resize(normalized_size, Image.Resampling.LANCZOS)
    immutable_context_coverage = float(
        np.count_nonzero(_registration_context_mask(normalized_mask)) / (normalized_mask.width * normalized_mask.height)
    )
    if immutable_context_coverage < 0.10:
        raise Direct3DValidationError("Proposal mask must preserve at least 10% fully immutable context")
    scene_lower_context_coverage: float | None = None
    # The lower-frame-context gate encodes an AERIAL framing assumption (site
    # ground ringed by real context). A street capture legitimately fills the
    # lower band with proposal street surface, so street view skips the gate.
    if req.presentation_mode == "scene" and req.view_mode != "street":
        scene_lower_context_coverage = float(
            np.count_nonzero(_scene_lower_context_mask(normalized_mask))
            / (normalized_mask.width * normalized_mask.height)
        )
        if scene_lower_context_coverage < _MIN_SCENE_LOWER_CONTEXT_COVERAGE:
            raise Direct3DValidationError(
                "Scene capture must preserve at least "
                f"{_MIN_SCENE_LOWER_CONTEXT_COVERAGE:.0%} lower-frame context; "
                f"received {scene_lower_context_coverage:.2%}"
            )
    normalized_object_id = (
        object_id_image.resize(normalized_size, Image.Resampling.NEAREST) if object_id_image is not None else None
    )
    normalized_instance_id = (
        instance_id_image.resize(normalized_size, Image.Resampling.NEAREST) if instance_id_image is not None else None
    )
    normalized_depth = (
        depth_image.resize(normalized_size, Image.Resampling.NEAREST) if depth_image is not None else None
    )
    normalized_normal = (
        normal_image.resize(normalized_size, Image.Resampling.NEAREST) if normal_image is not None else None
    )
    normalized_material_id = (
        material_id_image.resize(normalized_size, Image.Resampling.NEAREST) if material_id_image is not None else None
    )
    capture_fingerprint = _capture_fingerprint(
        beauty_image,
        proposal_mask,
        object_id_image,
        req.object_id_manifest,
        instance_id_image,
        req.instance_id_manifest,
        depth_image,
        normal_image,
        material_id_image,
        req.material_id_manifest,
        req.camera,
        req.control_bundle_version,
    )
    if req.capture and req.capture.fingerprint:
        if req.capture.fingerprint.lower() != capture_fingerprint:
            raise Direct3DValidationError("Client capture fingerprint does not match decoded pixels")

    return PreparedDirect3DCapture(
        source_beauty=beauty_image,
        source_proposal_mask=proposal_mask,
        normalized_beauty=normalized_beauty,
        normalized_proposal_mask=normalized_mask,
        normalized_object_id=normalized_object_id,
        normalized_instance_id=normalized_instance_id,
        normalized_depth=normalized_depth,
        normalized_normal=normalized_normal,
        normalized_material_id=normalized_material_id,
        proposal_coverage=proposal_coverage,
        object_id_coverage=object_id_coverage,
        object_id_proposal_recall=object_id_proposal_recall,
        object_id_proposal_iou=object_id_proposal_iou,
        instance_id_coverage=instance_id_coverage,
        instance_id_proposal_recall=instance_id_proposal_recall,
        instance_id_proposal_iou=instance_id_proposal_iou,
        instance_count=len(req.instance_id_manifest or {}),
        material_count=len(req.material_id_manifest or {}),
        scene_lower_context_coverage=scene_lower_context_coverage,
        capture_fingerprint=capture_fingerprint,
        audit_input_base64=base64.b64encode(_png_bytes(beauty_image)).decode("ascii"),
    )


def _png_bytes(image: Image.Image) -> bytes:
    buffer = io.BytesIO()
    image.save(buffer, format="PNG", optimize=False)
    return buffer.getvalue()


def build_openai_edit_mask(proposal_mask: Image.Image) -> Image.Image:
    """Convert 0=context/255=proposal coverage to OpenAI edit alpha.

    OpenAI edits transparent pixels.  RGB is deliberately fixed to black so
    the proposal signal exists in alpha only, as required by the edit API.
    """

    coverage = proposal_mask.convert("L")
    edit_alpha = coverage.point(lambda value: 255 - value)
    edit_mask = Image.new("RGBA", coverage.size, (0, 0, 0, 255))
    edit_mask.putalpha(edit_alpha)
    return edit_mask


def _beauty_structural_edges(
    beauty: Image.Image,
    proposal_mask: Image.Image,
    *,
    coarse: bool = False,
) -> np.ndarray:
    """Extract long, high-confidence scene edges without material texture noise."""

    if beauty.size != proposal_mask.size:
        raise Direct3DValidationError("Structural guide beauty and proposal mask must have identical dimensions")

    import cv2

    rgb = np.asarray(beauty.convert("RGB"), dtype=np.uint8)
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    diagonal = math.hypot(beauty.width, beauty.height)
    sigma = min(4.0, max(2.5, diagonal / 500.0)) if coarse else min(2.2, max(1.0, diagonal / 900.0))
    blurred = cv2.GaussianBlur(gray, (0, 0), sigmaX=sigma, sigmaY=sigma)
    gradient_x = cv2.Sobel(blurred, cv2.CV_32F, 1, 0, ksize=3)
    gradient_y = cv2.Sobel(blurred, cv2.CV_32F, 0, 1, ksize=3)
    gradient = cv2.magnitude(gradient_x, gradient_y)
    active = np.asarray(proposal_mask.convert("L"), dtype=np.uint8) >= 32
    active_gradient = gradient[active]
    nonzero_gradient = active_gradient[active_gradient > 1.0]
    adaptive_high = float(np.percentile(nonzero_gradient, 72)) if nonzero_gradient.size else 48.0
    high_threshold = min(140.0, max(42.0, adaptive_high))
    low_threshold = max(16.0, high_threshold * 0.42)
    edges = (
        cv2.Canny(
            blurred,
            threshold1=low_threshold,
            threshold2=high_threshold,
            L2gradient=True,
        )
        > 0
    )
    edges &= active

    # Isolated texture flecks are not geometry. Preserve connected facade,
    # roof, path and canopy contours while removing only tiny components.
    component_floor = max(4, round(diagonal / (220.0 if coarse else 320.0)))
    count, labels, stats, _centroids = cv2.connectedComponentsWithStats(
        edges.astype(np.uint8),
        connectivity=8,
    )
    filtered = np.zeros_like(edges)
    for component in range(1, count):
        if int(stats[component, cv2.CC_STAT_AREA]) >= component_floor:
            filtered[labels == component] = True
    return filtered


def _semantic_boundary_edges(
    object_id: Image.Image | None,
    object_id_manifest: dict[str, str] | None,
    proposal_mask: Image.Image,
    *,
    stable_only: bool,
) -> np.ndarray:
    """Return exact class transitions from the machine-readable ID pass."""

    height, width = proposal_mask.height, proposal_mask.width
    boundaries = np.zeros((height, width), dtype=bool)
    if object_id is None or not object_id_manifest:
        return boundaries
    if object_id.size != proposal_mask.size:
        raise Direct3DValidationError(
            "Structural guide object-ID image and proposal mask must have identical dimensions"
        )

    pixels = np.asarray(object_id.convert("RGB"), dtype=np.uint8)
    labels = np.zeros((height, width), dtype=np.int16)
    stable = np.zeros((height, width), dtype=bool)
    for index, (color, semantic_class) in enumerate(
        sorted(object_id_manifest.items()),
        start=1,
    ):
        matches = np.all(pixels == np.asarray(_hex_to_rgb(color), dtype=np.uint8), axis=2)
        labels[matches] = index
        if semantic_class != "landscape":
            stable[matches] = True

    def mark_pair(
        left: tuple[slice, slice],
        right: tuple[slice, slice],
    ) -> None:
        different = labels[left] != labels[right]
        classified = (labels[left] != 0) | (labels[right] != 0)
        selected = different & classified
        if stable_only:
            selected &= stable[left] | stable[right]
            # Tree crowns and foliage may legitimately become more organic.
            # Do not turn their pixel-perfect cutouts into a hard failure.
            selected &= ~((labels[left] != 0) & ~stable[left])
            selected &= ~((labels[right] != 0) & ~stable[right])
        boundaries[left] |= selected
        boundaries[right] |= selected

    mark_pair((slice(None), slice(0, -1)), (slice(None), slice(1, None)))
    mark_pair((slice(0, -1), slice(None)), (slice(1, None), slice(None)))
    boundaries &= np.asarray(proposal_mask.convert("L"), dtype=np.uint8) >= 32
    return boundaries


def _visible_semantic_components(
    object_id: Image.Image | None,
    object_id_manifest: dict[str, str] | None,
) -> tuple[dict[str, int], list[tuple[str, int, int]]]:
    """Count and label sizeable disjoint 2D class regions deterministically."""

    if object_id is None or not object_id_manifest:
        return {}, []

    import cv2

    pixels = np.asarray(object_id.convert("RGB"), dtype=np.uint8)
    semantic_regions = {
        semantic_class: np.zeros((object_id.height, object_id.width), dtype=bool)
        for semantic_class in {"building", "street", "park"}
    }
    for color, semantic_class in sorted(object_id_manifest.items()):
        if semantic_class in semantic_regions:
            semantic_regions[semantic_class] |= np.all(
                pixels == np.asarray(_hex_to_rgb(color), dtype=np.uint8),
                axis=2,
            )

    component_floor = max(64, round(object_id.width * object_id.height * 0.0001))
    prefixes = {"building": "B", "street": "S", "park": "P"}
    summary: dict[str, int] = {}
    labels: list[tuple[str, int, int]] = []
    for semantic_class in ("building", "street", "park"):
        region = semantic_regions[semantic_class].astype(np.uint8)
        count, component_labels, stats, _centroids = cv2.connectedComponentsWithStats(
            region,
            connectivity=8,
        )
        components: list[tuple[int, int, np.ndarray]] = []
        for component in range(1, count):
            if int(stats[component, cv2.CC_STAT_AREA]) < component_floor:
                continue
            component_region = (component_labels == component).astype(np.uint8)
            components.append(
                (
                    int(stats[component, cv2.CC_STAT_TOP]),
                    int(stats[component, cv2.CC_STAT_LEFT]),
                    component_region,
                )
            )
        components.sort(key=lambda item: (item[0], item[1]))
        if components:
            summary[semantic_class] = len(components)
        for index, (_top, _left, component_region) in enumerate(components, start=1):
            # The deepest interior pixel is deterministic and keeps the label
            # away from the authoritative component outline where possible.
            interior_distance = cv2.distanceTransform(
                component_region,
                cv2.DIST_L2,
                3,
            )
            y, x = np.unravel_index(int(np.argmax(interior_distance)), interior_distance.shape)
            labels.append((f"{prefixes[semantic_class]}{index}", int(x), int(y)))
    return summary, labels


def build_structural_edge_guide(
    beauty: Image.Image,
    proposal_mask: Image.Image,
    object_id: Image.Image | None = None,
    object_id_manifest: dict[str, str] | None = None,
) -> Image.Image:
    """Build a deterministic black-on-white geometry guide for Image 2/3."""

    import cv2

    beauty_edges = _beauty_structural_edges(beauty, proposal_mask)
    semantic_edges = _semantic_boundary_edges(
        object_id,
        object_id_manifest,
        proposal_mask,
        stable_only=False,
    )
    combined = beauty_edges | semantic_edges
    combined = (
        cv2.dilate(
            combined.astype(np.uint8),
            np.ones((3, 3), dtype=np.uint8),
            iterations=1,
        )
        > 0
    )
    guide = np.full(combined.shape, 255, dtype=np.uint8)
    guide[combined] = 0
    guide_image = Image.fromarray(guide, mode="L")
    _component_summary, component_labels = _visible_semantic_components(
        object_id,
        object_id_manifest,
    )
    draw = ImageDraw.Draw(guide_image)
    for label, center_x, center_y in component_labels:
        draw.text(
            (max(0, center_x - 6), max(0, center_y - 5)),
            label,
            fill=0,
            stroke_width=1,
            stroke_fill=255,
        )
    return guide_image.point(lambda value: 0 if value < 128 else 255, mode="L")


def _finish_fusion_sigma(width: int, height: int) -> float:
    return max(
        4.0,
        min(
            16.0,
            _FINISH_FUSION_SIGMA_AT_REFERENCE_PX * math.hypot(width, height) / _FINISH_FUSION_REFERENCE_DIAGONAL,
        ),
    )


def _finish_detail_scale(width: int, height: int) -> float:
    """Scale sub-pixel finish analysis conservatively around the 720p pilot."""

    return max(
        0.5,
        min(2.0, math.hypot(width, height) / _FINISH_FUSION_REFERENCE_DIAGONAL),
    )


def _finish_role_masks(
    alpha: np.ndarray,
    object_id: Image.Image | None,
    object_id_manifest: dict[str, str] | None,
) -> dict[str, np.ndarray]:
    """Return disjoint semantic interiors plus a proposal-only fallback role."""

    active = alpha >= 0.5
    classified = np.zeros(active.shape, dtype=bool)
    role_masks: dict[str, np.ndarray] = {}
    if object_id is not None and object_id_manifest:
        object_pixels = np.asarray(object_id.convert("RGB"), dtype=np.uint8)
        for color, semantic_class in sorted(object_id_manifest.items()):
            matches = active & np.all(
                object_pixels == np.asarray(_hex_to_rgb(color), dtype=np.uint8),
                axis=2,
            )
            if not np.any(matches):
                continue
            if semantic_class in role_masks:
                role_masks[semantic_class] |= matches
            else:
                role_masks[semantic_class] = matches
            classified |= matches
    fallback = active & ~classified
    if np.any(fallback):
        role_masks["default"] = fallback
    return role_masks


def _finish_band_contrast(band: np.ndarray, selected: np.ndarray) -> float:
    """Robust band magnitude that is insensitive to a few residual edges."""

    if int(np.count_nonzero(selected)) < _FINISH_MIN_ROLE_STAT_PIXELS:
        return 0.0
    magnitude = np.abs(band) if band.ndim == 2 else np.sqrt(np.mean(np.square(band, dtype=np.float32), axis=2))
    return float(np.percentile(magnitude[selected], 75))


def _finish_gradient_magnitude(rgb: np.ndarray) -> np.ndarray:
    import cv2

    gray = cv2.cvtColor(rgb.astype(np.uint8), cv2.COLOR_RGB2GRAY)
    gray = cv2.GaussianBlur(
        gray,
        (0, 0),
        sigmaX=0.5,
        sigmaY=0.5,
        borderType=cv2.BORDER_REFLECT,
    )
    gradient_x = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
    gradient_y = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
    return cv2.magnitude(gradient_x, gradient_y)


def _finish_low_gradient_threshold(
    gradient: np.ndarray,
    selected: np.ndarray,
) -> float:
    values = gradient[selected]
    if values.size < _FINISH_MIN_ROLE_STAT_PIXELS:
        return 0.0
    return min(
        _FINISH_LOW_GRADIENT_CAP,
        float(np.percentile(values, _FINISH_LOW_GRADIENT_PERCENTILE)),
    )


def _finish_detail_correlation(
    source_detail: np.ndarray,
    fused_detail: np.ndarray,
    selected: np.ndarray,
) -> float | None:
    if int(np.count_nonzero(selected)) < _FINISH_MIN_ROLE_STAT_PIXELS:
        return None
    source_values = source_detail[selected].astype(np.float64)
    fused_values = fused_detail[selected].astype(np.float64)
    source_values -= float(np.mean(source_values))
    fused_values -= float(np.mean(fused_values))
    denominator = float(np.sqrt(np.sum(source_values * source_values) * np.sum(fused_values * fused_values)))
    if denominator <= 1e-8:
        return None
    return float(np.clip(np.sum(source_values * fused_values) / denominator, -1.0, 1.0))


def _finish_luminance(rgb: np.ndarray) -> np.ndarray:
    return (rgb[..., 0] * 0.2126 + rgb[..., 1] * 0.7152 + rgb[..., 2] * 0.0722).astype(np.float32)


def _finish_texture_p75(detail: np.ndarray, selected: np.ndarray) -> float | None:
    if int(np.count_nonzero(selected)) < _FINISH_MIN_ROLE_STAT_PIXELS:
        return None
    return float(np.percentile(np.abs(detail[selected]), 75))


def _fuse_source_geometry_with_provider_finish(
    source: Image.Image,
    provider: Image.Image,
    proposal_mask: Image.Image,
    object_id: Image.Image | None = None,
    object_id_manifest: dict[str, str] | None = None,
) -> FinishFusionResult:
    """Transfer provider tone/statistics while every spatial detail stays source-owned.

    Provider-minus-source color is blurred with normalized, mask-aware Gaussian
    filtering, clipped, and applied at conservative semantic-role strengths. Fine,
    medium and micro material contrast can increase only by scaling the source's
    own spatial bands. Provider high-frequency pixels are never composited, so a
    provider-only line, roof feature or facade rhythm cannot ghost into the result.
    """

    if source.size != provider.size or source.size != proposal_mask.size:
        raise Direct3DValidationError("Finish-fusion images and proposal mask must have identical dimensions")
    if object_id is not None and object_id.size != source.size:
        raise Direct3DValidationError("Finish-fusion object-ID image must match the source dimensions")

    import cv2

    source_rgb = np.asarray(source.convert("RGB"), dtype=np.uint8)
    provider_rgb = np.asarray(provider.convert("RGB"), dtype=np.uint8)
    if np.array_equal(source_rgb, provider_rgb):
        return FinishFusionResult(
            image=source.convert("RGB").copy(),
            diagnostics={
                "safe_microtexture_coverage": 0.0,
                "source_detail_correlation": 1.0,
                "source_texture_p75": None,
                "fused_texture_p75": None,
                "texture_gain": None,
                "role_metrics": {},
            },
        )

    alpha = np.asarray(proposal_mask.convert("L"), dtype=np.float32) / 255.0
    np.clip(alpha, 0.0, 1.0, out=alpha)
    sigma = _finish_fusion_sigma(source.width, source.height)
    scale = _finish_detail_scale(source.width, source.height)
    fine_sigma = max(0.5, _FINISH_DETAIL_FINE_SIGMA_AT_REFERENCE_PX * scale)
    medium_sigma = max(
        1.75,
        _FINISH_DETAIL_MEDIUM_SIGMA_AT_REFERENCE_PX * scale,
    )
    microtexture_sigma = max(
        0.4,
        _FINISH_MICROTEXTURE_SIGMA_AT_REFERENCE_PX * scale,
    )

    # Provider edge locations are used only as exclusion zones. From this
    # point onward provider material detail is reduced to per-role scalars.
    protected_edges = (
        _beauty_structural_edges(source, proposal_mask)
        | _beauty_structural_edges(provider, proposal_mask)
        | _semantic_boundary_edges(
            object_id,
            object_id_manifest,
            proposal_mask,
            stable_only=False,
        )
    )
    edge_radius = max(
        2,
        round(_FINISH_EDGE_DILATION_RADIUS_AT_REFERENCE_PX * scale),
    )
    protected_edges = (
        cv2.dilate(
            protected_edges.astype(np.uint8),
            np.ones((edge_radius * 2 + 1, edge_radius * 2 + 1), dtype=np.uint8),
            iterations=1,
        )
        > 0
    )
    erosion_radius = max(
        2,
        round(_FINISH_INTERIOR_EROSION_RADIUS_AT_REFERENCE_PX * scale),
    )
    erosion_kernel = np.ones(
        (erosion_radius * 2 + 1, erosion_radius * 2 + 1),
        dtype=np.uint8,
    )
    feather_distance = max(
        1.5,
        _FINISH_INTERIOR_FEATHER_AT_REFERENCE_PX * scale,
    )
    role_masks = _finish_role_masks(alpha, object_id, object_id_manifest)

    def safe_interior(role_mask: np.ndarray) -> np.ndarray:
        eroded = (
            cv2.erode(
                role_mask.astype(np.uint8),
                erosion_kernel,
                iterations=1,
            )
            > 0
        )
        return eroded & ~protected_edges

    # The analysis pass is luminance-only and sequential. This avoids retaining
    # six full-resolution float32 RGB bands at the provider's maximum size.
    source_luminance = cv2.cvtColor(source_rgb, cv2.COLOR_RGB2GRAY).astype(np.float32)
    provider_luminance = cv2.cvtColor(provider_rgb, cv2.COLOR_RGB2GRAY).astype(np.float32)
    source_gradient = _finish_gradient_magnitude(source_rgb)
    provider_gradient = _finish_gradient_magnitude(provider_rgb)
    contrast_stats: dict[str, dict[str, tuple[float, float]]] = {semantic_class: {} for semantic_class in role_masks}

    source_fine_blur = cv2.GaussianBlur(
        source_luminance,
        (0, 0),
        sigmaX=fine_sigma,
        sigmaY=fine_sigma,
        borderType=cv2.BORDER_REFLECT,
    )
    provider_fine_blur = cv2.GaussianBlur(
        provider_luminance,
        (0, 0),
        sigmaX=fine_sigma,
        sigmaY=fine_sigma,
        borderType=cv2.BORDER_REFLECT,
    )
    source_fine_band = source_luminance - source_fine_blur
    provider_fine_band = provider_luminance - provider_fine_blur
    for semantic_class, role_mask in sorted(role_masks.items()):
        selected = safe_interior(role_mask)
        contrast_stats[semantic_class]["fine"] = (
            _finish_band_contrast(source_fine_band, selected),
            _finish_band_contrast(provider_fine_band, selected),
        )
    del source_fine_band, provider_fine_band

    source_medium_blur = cv2.GaussianBlur(
        source_luminance,
        (0, 0),
        sigmaX=medium_sigma,
        sigmaY=medium_sigma,
        borderType=cv2.BORDER_REFLECT,
    )
    provider_medium_blur = cv2.GaussianBlur(
        provider_luminance,
        (0, 0),
        sigmaX=medium_sigma,
        sigmaY=medium_sigma,
        borderType=cv2.BORDER_REFLECT,
    )
    source_medium_band = source_fine_blur - source_medium_blur
    provider_medium_band = provider_fine_blur - provider_medium_blur
    for semantic_class, role_mask in sorted(role_masks.items()):
        selected = safe_interior(role_mask)
        contrast_stats[semantic_class]["medium"] = (
            _finish_band_contrast(source_medium_band, selected),
            _finish_band_contrast(provider_medium_band, selected),
        )
    del (
        source_fine_blur,
        provider_fine_blur,
        source_medium_blur,
        provider_medium_blur,
        source_medium_band,
        provider_medium_band,
    )

    source_micro_blur = cv2.GaussianBlur(
        source_luminance,
        (0, 0),
        sigmaX=microtexture_sigma,
        sigmaY=microtexture_sigma,
        borderType=cv2.BORDER_REFLECT,
    )
    provider_micro_blur = cv2.GaussianBlur(
        provider_luminance,
        (0, 0),
        sigmaX=microtexture_sigma,
        sigmaY=microtexture_sigma,
        borderType=cv2.BORDER_REFLECT,
    )
    source_micro_band = source_luminance - source_micro_blur
    provider_micro_band = provider_luminance - provider_micro_blur
    for semantic_class, role_mask in sorted(role_masks.items()):
        selected = safe_interior(role_mask)
        source_threshold = _finish_low_gradient_threshold(source_gradient, selected)
        provider_threshold = _finish_low_gradient_threshold(provider_gradient, selected)
        statistics_region = (
            selected & (source_gradient <= source_threshold + 1e-6) & (provider_gradient <= provider_threshold + 1e-6)
        )
        contrast_stats[semantic_class]["microtexture"] = (
            _finish_band_contrast(source_micro_band, statistics_region),
            _finish_band_contrast(provider_micro_band, statistics_region),
        )
    del (
        source_luminance,
        provider_luminance,
        source_micro_blur,
        provider_micro_blur,
        source_micro_band,
        provider_micro_band,
    )

    # Gain maps are single-channel. Their spatial phase comes solely from the
    # source role/interior masks; provider contrast contributes one scalar.
    fine_gain_map = np.zeros(alpha.shape, dtype=np.float32)
    medium_gain_map = np.zeros(alpha.shape, dtype=np.float32)
    microtexture_gain_map = np.zeros(alpha.shape, dtype=np.float32)
    target_gains: dict[str, tuple[float, float, float]] = {}
    for semantic_class, role_mask in sorted(role_masks.items()):
        selected = safe_interior(role_mask)
        if int(np.count_nonzero(selected)) < _FINISH_MIN_ROLE_STAT_PIXELS:
            continue
        interior_distance = cv2.distanceTransform(
            selected.astype(np.uint8),
            cv2.DIST_L2,
            3,
        )
        interior_weight = np.clip(
            interior_distance / feather_distance,
            0.0,
            1.0,
        ).astype(np.float32)
        interior_weight *= alpha
        fine_cap, medium_cap = _FINISH_DETAIL_ROLE_GAIN_CAPS.get(
            semantic_class,
            _FINISH_DETAIL_DEFAULT_GAIN_CAPS,
        )
        source_fine_contrast, provider_fine_contrast = contrast_stats[semantic_class]["fine"]
        source_medium_contrast, provider_medium_contrast = contrast_stats[semantic_class]["medium"]
        source_micro_contrast, provider_micro_contrast = contrast_stats[semantic_class]["microtexture"]
        fine_gain = (
            min(fine_cap, max(1.0, provider_fine_contrast / source_fine_contrast))
            if source_fine_contrast >= _FINISH_DETAIL_MIN_ROBUST_CONTRAST
            else 1.0
        )
        medium_gain = (
            min(
                medium_cap,
                max(1.0, provider_medium_contrast / source_medium_contrast),
            )
            if source_medium_contrast >= _FINISH_DETAIL_MIN_ROBUST_CONTRAST
            else 1.0
        )
        microtexture_cap = _FINISH_MICROTEXTURE_ROLE_GAIN_CAPS.get(
            semantic_class,
            _FINISH_MICROTEXTURE_DEFAULT_GAIN_CAP,
        )
        microtexture_gain = (
            min(
                microtexture_cap,
                max(1.0, provider_micro_contrast / source_micro_contrast),
            )
            if source_micro_contrast >= _FINISH_DETAIL_MIN_ROBUST_CONTRAST
            else 1.0
        )
        source_threshold = _finish_low_gradient_threshold(source_gradient, selected)
        application_region = selected & (source_gradient <= source_threshold + 1e-6)
        fine_gain_map += interior_weight * (fine_gain - 1.0)
        medium_gain_map += interior_weight * (medium_gain - 1.0)
        microtexture_gain_map += interior_weight * application_region.astype(np.float32) * (microtexture_gain - 1.0)
        target_gains[semantic_class] = (
            float(fine_gain),
            float(medium_gain),
            float(microtexture_gain),
        )
    del role_masks, source_gradient, provider_gradient, contrast_stats

    # Synthesis is a single sequential source-RGB pass. Each blur is reused as
    # its own source-phase band and released before the broad tone pass.
    source_float = source_rgb.astype(np.float32)
    source_fine_blur = cv2.GaussianBlur(
        source_float,
        (0, 0),
        sigmaX=fine_sigma,
        sigmaY=fine_sigma,
        borderType=cv2.BORDER_REFLECT,
    )
    source_medium_blur = cv2.GaussianBlur(
        source_float,
        (0, 0),
        sigmaX=medium_sigma,
        sigmaY=medium_sigma,
        borderType=cv2.BORDER_REFLECT,
    )
    source_medium_blur *= -1.0
    source_medium_blur += source_fine_blur
    source_medium_blur *= medium_gain_map[..., None]
    detail_correction = source_medium_blur
    del source_medium_blur, medium_gain_map
    source_fine_blur *= -1.0
    source_fine_blur += source_float
    source_fine_blur *= fine_gain_map[..., None]
    detail_correction += source_fine_blur
    del source_fine_blur, fine_gain_map
    np.clip(
        detail_correction,
        -_FINISH_DETAIL_CORRECTION_CLIP,
        _FINISH_DETAIL_CORRECTION_CLIP,
        out=detail_correction,
    )
    source_micro_blur = cv2.GaussianBlur(
        source_float,
        (0, 0),
        sigmaX=microtexture_sigma,
        sigmaY=microtexture_sigma,
        borderType=cv2.BORDER_REFLECT,
    )
    source_micro_blur *= -1.0
    source_micro_blur += source_float
    source_micro_blur *= microtexture_gain_map[..., None]
    np.clip(
        source_micro_blur,
        -_FINISH_MICROTEXTURE_CORRECTION_CLIP,
        _FINISH_MICROTEXTURE_CORRECTION_CLIP,
        out=source_micro_blur,
    )
    detail_correction += source_micro_blur
    del source_micro_blur, microtexture_gain_map

    # Existing broad, mask-aware tone transfer remains byte-compatible in
    # purpose but is evaluated only after detail buffers have been released.
    broad_delta = provider_rgb.astype(np.float32)
    broad_delta -= source_float
    broad_delta *= alpha[..., None]
    broad_delta = cv2.GaussianBlur(
        broad_delta,
        (0, 0),
        sigmaX=sigma,
        sigmaY=sigma,
        borderType=cv2.BORDER_REFLECT,
    )
    normalized_weight = cv2.GaussianBlur(
        alpha,
        (0, 0),
        sigmaX=sigma,
        sigmaY=sigma,
        borderType=cv2.BORDER_REFLECT,
    )
    broad_delta /= np.maximum(normalized_weight[..., None], 0.02)
    del normalized_weight
    np.clip(
        broad_delta,
        -_FINISH_FUSION_RGB_DELTA_CLIP,
        _FINISH_FUSION_RGB_DELTA_CLIP,
        out=broad_delta,
    )
    role_strength = np.full(
        alpha.shape,
        _FINISH_FUSION_DEFAULT_STRENGTH,
        dtype=np.float32,
    )
    if object_id is not None and object_id_manifest:
        object_pixels = np.asarray(object_id.convert("RGB"), dtype=np.uint8)
        for color, semantic_class in sorted(object_id_manifest.items()):
            matches = np.all(
                object_pixels == np.asarray(_hex_to_rgb(color), dtype=np.uint8),
                axis=2,
            )
            role_strength[matches] = _FINISH_FUSION_ROLE_STRENGTHS.get(
                semantic_class,
                _FINISH_FUSION_DEFAULT_STRENGTH,
            )
    strength_sigma = max(2.0, sigma / 2.0)
    role_strength *= alpha
    smooth_strength = cv2.GaussianBlur(
        role_strength,
        (0, 0),
        sigmaX=strength_sigma,
        sigmaY=strength_sigma,
        borderType=cv2.BORDER_REFLECT,
    )
    del role_strength
    strength_weight = cv2.GaussianBlur(
        alpha,
        (0, 0),
        sigmaX=strength_sigma,
        sigmaY=strength_sigma,
        borderType=cv2.BORDER_REFLECT,
    )
    smooth_strength /= np.maximum(strength_weight, 0.02)
    del strength_weight
    fused_float = source_float.copy()
    broad_delta *= smooth_strength[..., None]
    fused_float += broad_delta
    fused_float += detail_correction
    del broad_delta, smooth_strength, detail_correction
    fused_inside = np.clip(np.rint(fused_float), 0, 255).astype(np.uint8)
    del fused_float
    fused_float = fused_inside.astype(np.float32)
    fused_float *= alpha[..., None]
    source_context = source_float.copy()
    source_context *= (1.0 - alpha)[..., None]
    fused_float += source_context
    del source_context, source_float
    fused = np.rint(fused_float).astype(np.uint8)
    del fused_float
    exterior = alpha == 0
    fused[exterior] = source_rgb[exterior]

    # Diagnostics are intentionally recomputed from compact luminance planes
    # after synthesis, keeping instrumentation out of the peak-memory phase.
    source_luminance = cv2.cvtColor(source_rgb, cv2.COLOR_RGB2GRAY).astype(np.float32)
    fused_luminance = cv2.cvtColor(fused, cv2.COLOR_RGB2GRAY).astype(np.float32)
    source_detail_luminance = source_luminance - cv2.GaussianBlur(
        source_luminance,
        (0, 0),
        sigmaX=medium_sigma,
        sigmaY=medium_sigma,
        borderType=cv2.BORDER_REFLECT,
    )
    fused_detail_luminance = fused_luminance - cv2.GaussianBlur(
        fused_luminance,
        (0, 0),
        sigmaX=medium_sigma,
        sigmaY=medium_sigma,
        borderType=cv2.BORDER_REFLECT,
    )
    source_micro_luminance = source_luminance - cv2.GaussianBlur(
        source_luminance,
        (0, 0),
        sigmaX=microtexture_sigma,
        sigmaY=microtexture_sigma,
        borderType=cv2.BORDER_REFLECT,
    )
    fused_micro_luminance = fused_luminance - cv2.GaussianBlur(
        fused_luminance,
        (0, 0),
        sigmaX=microtexture_sigma,
        sigmaY=microtexture_sigma,
        borderType=cv2.BORDER_REFLECT,
    )
    del source_luminance, fused_luminance
    source_gradient = _finish_gradient_magnitude(source_rgb)
    role_masks = _finish_role_masks(alpha, object_id, object_id_manifest)
    combined_detail_region = np.zeros(alpha.shape, dtype=bool)
    combined_microtexture_region = np.zeros(alpha.shape, dtype=bool)
    role_metrics: dict[str, dict[str, float | int | None]] = {}
    for semantic_class, role_mask in sorted(role_masks.items()):
        if semantic_class not in target_gains:
            continue
        detail_region = safe_interior(role_mask)
        source_threshold = _finish_low_gradient_threshold(
            source_gradient,
            detail_region,
        )
        microtexture_region = detail_region & (source_gradient <= source_threshold + 1e-6)
        combined_detail_region |= detail_region
        combined_microtexture_region |= microtexture_region
        source_texture_p75 = _finish_texture_p75(
            source_micro_luminance,
            microtexture_region,
        )
        fused_texture_p75 = _finish_texture_p75(
            fused_micro_luminance,
            microtexture_region,
        )
        texture_gain = (
            fused_texture_p75 / source_texture_p75
            if source_texture_p75 is not None
            and fused_texture_p75 is not None
            and source_texture_p75 >= _FINISH_DETAIL_MIN_ROBUST_CONTRAST
            else None
        )
        correlation = _finish_detail_correlation(
            source_detail_luminance,
            fused_detail_luminance,
            detail_region,
        )
        fine_gain, medium_gain, microtexture_gain = target_gains[semantic_class]
        safe_microtexture_pixels = int(np.count_nonzero(microtexture_region))
        role_metrics[semantic_class] = {
            "detail_fine_gain": round(fine_gain, 6),
            "detail_medium_gain": round(medium_gain, 6),
            "microtexture_gain": round(microtexture_gain, 6),
            "safe_microtexture_pixels": safe_microtexture_pixels,
            "safe_microtexture_coverage": round(
                safe_microtexture_pixels / max(1, int(np.count_nonzero(role_mask))),
                6,
            ),
            "source_texture_p75": (round(source_texture_p75, 6) if source_texture_p75 is not None else None),
            "fused_texture_p75": (round(fused_texture_p75, 6) if fused_texture_p75 is not None else None),
            "texture_gain": round(texture_gain, 6) if texture_gain is not None else None,
            "source_detail_correlation": (round(correlation, 6) if correlation is not None else None),
        }
    source_texture_p75 = _finish_texture_p75(
        source_micro_luminance,
        combined_microtexture_region,
    )
    fused_texture_p75 = _finish_texture_p75(
        fused_micro_luminance,
        combined_microtexture_region,
    )
    texture_gain = (
        fused_texture_p75 / source_texture_p75
        if source_texture_p75 is not None
        and fused_texture_p75 is not None
        and source_texture_p75 >= _FINISH_DETAIL_MIN_ROBUST_CONTRAST
        else None
    )
    source_detail_correlation = _finish_detail_correlation(
        source_detail_luminance,
        fused_detail_luminance,
        combined_detail_region,
    )
    proposal_pixel_count = max(1, int(np.count_nonzero(alpha >= 0.5)))
    return FinishFusionResult(
        image=Image.fromarray(fused, mode="RGB"),
        diagnostics={
            "safe_microtexture_coverage": round(
                int(np.count_nonzero(combined_microtexture_region)) / proposal_pixel_count,
                6,
            ),
            "source_detail_correlation": (
                round(source_detail_correlation, 6) if source_detail_correlation is not None else None
            ),
            "source_texture_p75": (round(source_texture_p75, 6) if source_texture_p75 is not None else None),
            "fused_texture_p75": (round(fused_texture_p75, 6) if fused_texture_p75 is not None else None),
            "texture_gain": round(texture_gain, 6) if texture_gain is not None else None,
            "role_metrics": role_metrics,
        },
    )


def fuse_source_geometry_with_provider_finish(
    source: Image.Image,
    provider: Image.Image,
    proposal_mask: Image.Image,
    object_id: Image.Image | None = None,
    object_id_manifest: dict[str, str] | None = None,
) -> Image.Image:
    """Return source-owned geometry with bounded provider finish statistics."""

    return _fuse_source_geometry_with_provider_finish(
        source,
        provider,
        proposal_mask,
        object_id,
        object_id_manifest,
    ).image


def assess_structural_edge_fidelity(
    source: Image.Image,
    candidate: Image.Image,
    proposal_mask: Image.Image,
    object_id: Image.Image | None = None,
    object_id_manifest: dict[str, str] | None = None,
) -> StructuralEdgeFidelityResult:
    """Fail-closed geometry check tolerant of recoloring and new material detail.

    This is deliberately a directed comparison: authoritative source edges
    must remain near an output edge, while additional fine material edges are
    allowed. Semantic class transitions and each sizeable hard-surface object
    receive stricter checks than beauty-pass edges.
    """

    if source.size != candidate.size or source.size != proposal_mask.size:
        raise Direct3DValidationError("Structural fidelity images and proposal mask must have identical dimensions")

    import cv2

    diagonal = math.hypot(source.width, source.height)
    # At 720p this permits roughly two raster pixels of antialiasing/material
    # drift; the allowance scales to four pixels at the largest provider size.
    tolerance_px = max(2, min(4, round(diagonal * 0.0015)))
    proposal = np.asarray(proposal_mask.convert("L"), dtype=np.uint8) >= 128
    evaluation_mask = (
        cv2.erode(
            proposal.astype(np.uint8),
            np.ones((tolerance_px * 2 + 1, tolerance_px * 2 + 1), dtype=np.uint8),
            iterations=1,
        )
        > 0
    )
    if np.count_nonzero(evaluation_mask) < _MIN_STRUCTURAL_EDGE_PIXELS:
        evaluation_mask = proposal

    source_edges = _beauty_structural_edges(source, proposal_mask) & evaluation_mask
    candidate_edges = _beauty_structural_edges(candidate, proposal_mask) & evaluation_mask
    source_coarse_edges = (
        _beauty_structural_edges(
            source,
            proposal_mask,
            coarse=True,
        )
        & evaluation_mask
    )
    candidate_coarse_edges = (
        _beauty_structural_edges(
            candidate,
            proposal_mask,
            coarse=True,
        )
        & evaluation_mask
    )
    raw_semantic_edges = (
        _semantic_boundary_edges(
            object_id,
            object_id_manifest,
            proposal_mask,
            stable_only=True,
        )
        & evaluation_mask
    )
    source_anchor_edges = source_edges | source_coarse_edges
    candidate_anchor_edges = candidate_edges | candidate_coarse_edges
    semantic_anchor_band = (
        cv2.dilate(
            raw_semantic_edges.astype(np.uint8),
            np.ones((tolerance_px * 2 + 1, tolerance_px * 2 + 1), dtype=np.uint8),
            iterations=1,
        )
        > 0
    )
    # A class transition is a useful geometry requirement only where the
    # authoritative beauty pass actually depicts a structural edge. Ownership
    # changes between visually continuous surfaces must not invent an edge.
    semantic_edges = source_anchor_edges & semantic_anchor_band & evaluation_mask
    reference_edges = source_edges | semantic_edges
    reference_count = int(np.count_nonzero(reference_edges))
    candidate_count = int(np.count_nonzero(candidate_edges))

    identical = np.array_equal(
        np.asarray(source.convert("RGB")),
        np.asarray(candidate.convert("RGB")),
    )
    if candidate_count:
        distance_to_candidate = cv2.distanceTransform(
            (~candidate_edges).astype(np.uint8),
            cv2.DIST_L2,
            3,
        )
    else:
        distance_to_candidate = np.full(
            reference_edges.shape,
            diagonal,
            dtype=np.float32,
        )
    if np.any(candidate_anchor_edges):
        distance_to_candidate_anchor = cv2.distanceTransform(
            (~candidate_anchor_edges).astype(np.uint8),
            cv2.DIST_L2,
            3,
        )
    else:
        distance_to_candidate_anchor = np.full(
            reference_edges.shape,
            diagonal,
            dtype=np.float32,
        )

    def recall(edges: np.ndarray) -> float:
        count = int(np.count_nonzero(edges))
        if count == 0:
            return 1.0
        return float(np.mean(distance_to_candidate[edges] <= tolerance_px))

    def anchor_recall(edges: np.ndarray) -> float:
        count = int(np.count_nonzero(edges))
        if count == 0:
            return 1.0
        return float(np.mean(distance_to_candidate_anchor[edges] <= tolerance_px))

    if np.any(candidate_coarse_edges):
        distance_to_candidate_coarse = cv2.distanceTransform(
            (~candidate_coarse_edges).astype(np.uint8),
            cv2.DIST_L2,
            3,
        )
    else:
        distance_to_candidate_coarse = np.full(
            reference_edges.shape,
            diagonal,
            dtype=np.float32,
        )

    beauty_recall = recall(source_edges)
    coarse_count = int(np.count_nonzero(source_coarse_edges))
    coarse_recall = (
        float(np.mean(distance_to_candidate_coarse[source_coarse_edges] <= tolerance_px)) if coarse_count else 1.0
    )
    semantic_count = int(np.count_nonzero(semantic_edges))
    semantic_recall = anchor_recall(semantic_edges) if semantic_count else None
    reference_p90 = float(np.percentile(distance_to_candidate[reference_edges], 90)) if reference_count else 0.0

    component_recalls: list[float] = []
    building_region = np.zeros(reference_edges.shape, dtype=bool)
    if object_id is not None and object_id_manifest:
        object_pixels = np.asarray(object_id.convert("RGB"), dtype=np.uint8)
        for color, semantic_class in sorted(object_id_manifest.items()):
            color_region = np.all(
                object_pixels == np.asarray(_hex_to_rgb(color), dtype=np.uint8),
                axis=2,
            )
            if semantic_class == "building":
                building_region |= color_region
            if semantic_class not in {"building", "street", "park"}:
                continue
            class_region = color_region.astype(np.uint8)
            component_count, component_labels, component_stats, _centroids = cv2.connectedComponentsWithStats(
                class_region, connectivity=8
            )
            for component in range(1, component_count):
                if int(component_stats[component, cv2.CC_STAT_AREA]) < 64:
                    continue
                region = (component_labels == component).astype(np.uint8)
                raw_component_edge = (
                    cv2.morphologyEx(
                        region,
                        cv2.MORPH_GRADIENT,
                        np.ones((3, 3), dtype=np.uint8),
                    )
                    > 0
                ) & evaluation_mask
                component_anchor_band = (
                    cv2.dilate(
                        raw_component_edge.astype(np.uint8),
                        np.ones(
                            (tolerance_px * 2 + 1, tolerance_px * 2 + 1),
                            dtype=np.uint8,
                        ),
                        iterations=1,
                    )
                    > 0
                )
                component_edge = source_anchor_edges & component_anchor_band & evaluation_mask
                if np.count_nonzero(component_edge) >= 16:
                    component_recalls.append(anchor_recall(component_edge))
    component_min_recall = min(component_recalls) if component_recalls else None
    building_internal_edges = source_edges & building_region & evaluation_mask
    building_internal_count = int(np.count_nonzero(building_internal_edges))
    building_internal_recall = recall(building_internal_edges) if building_internal_count else None

    beauty_pass = beauty_recall >= _MIN_BEAUTY_EDGE_RECALL
    coarse_pass = coarse_recall >= _MIN_COARSE_EDGE_RECALL
    semantic_pass = semantic_recall is None or semantic_recall >= _MIN_SEMANTIC_EDGE_RECALL
    component_pass = component_min_recall is None or component_min_recall >= _MIN_SEMANTIC_COMPONENT_RECALL
    building_internal_pass = (
        building_internal_recall is None or building_internal_recall >= _MIN_BUILDING_INTERNAL_EDGE_RECALL
    )
    passed = identical or (beauty_pass and coarse_pass and semantic_pass and component_pass and building_internal_pass)
    return StructuralEdgeFidelityResult(
        passed=passed,
        tolerance_px=tolerance_px,
        reference_edge_pixels=reference_count,
        candidate_edge_pixels=candidate_count,
        beauty_edge_recall=beauty_recall,
        coarse_edge_pixels=coarse_count,
        coarse_edge_recall=coarse_recall,
        semantic_edge_pixels=semantic_count,
        semantic_edge_recall=semantic_recall,
        semantic_component_min_recall=component_min_recall,
        building_internal_edge_pixels=building_internal_count,
        building_internal_edge_recall=building_internal_recall,
        reference_edge_p90_distance_px=reference_p90,
    )


def assess_macro_design_fidelity(
    source: Image.Image,
    candidate: Image.Image,
    proposal_mask: Image.Image,
    object_id: Image.Image | None = None,
    object_id_manifest: dict[str, str] | None = None,
    *,
    fidelity_policy: Literal["precise", "balanced", "expressive"] = "precise",
) -> MacroDesignFidelityResult:
    """Verify primary scene design while permitting new photographic detail.

    The comparison is deliberately directed from the authoritative 3D capture
    to the provider image. Extra facade, foliage and material edges are welcome;
    source building-internal/window edges are not an acceptance requirement.
    """

    if source.size != candidate.size or source.size != proposal_mask.size:
        raise Direct3DValidationError("Macro fidelity images and proposal mask must have identical dimensions")
    if object_id is not None and object_id.size != source.size:
        raise Direct3DValidationError("Macro fidelity object-ID image must match the source dimensions")

    import cv2

    diagonal = math.hypot(source.width, source.height)
    # Keep the existing reviewed 2px-at-720p / 4px-at-max scale. Relaxation
    # comes from measuring only macro/semantic boundaries, not by permitting
    # the multi-pixel drift that allowed the rejected calibration redesign.
    tolerance_px = max(2, min(4, round(diagonal * 0.0015)))
    active = np.asarray(proposal_mask.convert("L"), dtype=np.uint8) >= 128
    source_edges = _beauty_structural_edges(source, proposal_mask)
    source_coarse = _beauty_structural_edges(source, proposal_mask, coarse=True)
    candidate_edges = _beauty_structural_edges(candidate, proposal_mask)
    candidate_coarse = _beauty_structural_edges(candidate, proposal_mask, coarse=True)
    source_anchor = (source_edges | source_coarse) & active
    candidate_anchor = (candidate_edges | candidate_coarse) & active

    if np.any(candidate_anchor):
        distance_to_candidate = cv2.distanceTransform(
            (~candidate_anchor).astype(np.uint8),
            cv2.DIST_L2,
            3,
        )
    else:
        distance_to_candidate = np.full(active.shape, diagonal, dtype=np.float32)

    def recall(reference: np.ndarray) -> float:
        if not np.any(reference):
            return 0.0
        return float(np.mean(distance_to_candidate[reference] <= tolerance_px))

    # Directed source recall alone can be gamed by replacing the proposal with
    # dense noise or stripes: unrelated edges eventually land near every
    # source edge. Evaluate the reverse direction at the coarse scale so new
    # fine photographic texture remains welcome while unrelated coarse edge
    # fields fail closed.
    if np.any(source_anchor):
        distance_to_source = cv2.distanceTransform(
            (~source_anchor).astype(np.uint8),
            cv2.DIST_L2,
            3,
        )
    else:
        distance_to_source = np.full(active.shape, diagonal, dtype=np.float32)
    candidate_coarse_active = candidate_coarse & active
    candidate_coarse_count = int(np.count_nonzero(candidate_coarse_active))
    candidate_coarse_precision = (
        float(np.mean(distance_to_source[candidate_coarse_active] <= tolerance_px)) if candidate_coarse_count else 0.0
    )

    boundary_kernel = np.ones(
        (tolerance_px * 2 + 1, tolerance_px * 2 + 1),
        dtype=np.uint8,
    )
    proposal_boundary = (
        cv2.morphologyEx(
            active.astype(np.uint8),
            cv2.MORPH_GRADIENT,
            np.ones((3, 3), dtype=np.uint8),
        )
        > 0
    )
    proposal_boundary_band = (
        cv2.dilate(
            proposal_boundary.astype(np.uint8),
            boundary_kernel,
            iterations=1,
        )
        > 0
    )
    silhouette_edges = source_anchor & proposal_boundary_band
    silhouette_count = int(np.count_nonzero(silhouette_edges))
    silhouette_recall = recall(silhouette_edges) if silhouette_count else None

    coarse_edges = source_coarse & active
    coarse_count = int(np.count_nonzero(coarse_edges))
    coarse_recall = recall(coarse_edges)
    candidate_coarse_density_ratio = float(candidate_coarse_count / max(1, coarse_count))

    raw_semantic = (
        _semantic_boundary_edges(
            object_id,
            object_id_manifest,
            proposal_mask,
            stable_only=True,
        )
        & active
    )
    semantic_band = (
        cv2.dilate(
            raw_semantic.astype(np.uint8),
            boundary_kernel,
            iterations=1,
        )
        > 0
    )
    semantic_edges = source_anchor & semantic_band
    semantic_count = int(np.count_nonzero(semantic_edges))
    semantic_recall = recall(semantic_edges) if semantic_count else None

    component_recalls: list[float] = []
    if object_id is not None and object_id_manifest:
        object_pixels = np.asarray(object_id.convert("RGB"), dtype=np.uint8)
        for color, semantic_class in sorted(object_id_manifest.items()):
            if semantic_class not in {"building", "street", "park"}:
                continue
            color_region = np.all(
                object_pixels == np.asarray(_hex_to_rgb(color), dtype=np.uint8),
                axis=2,
            ).astype(np.uint8)
            component_count, component_labels, component_stats, _centroids = cv2.connectedComponentsWithStats(
                color_region, connectivity=8
            )
            for component in range(1, component_count):
                if int(component_stats[component, cv2.CC_STAT_AREA]) < 64:
                    continue
                component_region = (component_labels == component).astype(np.uint8)
                raw_component_edge = (
                    cv2.morphologyEx(
                        component_region,
                        cv2.MORPH_GRADIENT,
                        np.ones((3, 3), dtype=np.uint8),
                    )
                    > 0
                )
                component_band = (
                    cv2.dilate(
                        raw_component_edge.astype(np.uint8),
                        boundary_kernel,
                        iterations=1,
                    )
                    > 0
                )
                component_edge = source_anchor & component_band
                if np.count_nonzero(component_edge) >= 16:
                    component_recalls.append(recall(component_edge))
    component_min = min(component_recalls) if component_recalls else None

    macro_reference = silhouette_edges | coarse_edges | semantic_edges
    reference_p90 = float(np.percentile(distance_to_candidate[macro_reference], 90)) if np.any(macro_reference) else 0.0
    thresholds = _macro_fidelity_thresholds(
        fidelity_policy,
        tolerance_px=tolerance_px,
    )
    silhouette_pass = silhouette_recall is None or silhouette_recall >= thresholds.minimum_silhouette_edge_recall
    semantic_pass = semantic_recall is None or semantic_recall >= thresholds.minimum_semantic_edge_recall
    component_pass = component_min is None or component_min >= thresholds.minimum_semantic_component_recall
    passed = (
        coarse_count >= 16
        and silhouette_pass
        and coarse_recall >= thresholds.minimum_coarse_edge_recall
        and semantic_pass
        and component_pass
        and reference_p90 <= thresholds.maximum_reference_p90_distance_px
        and candidate_coarse_precision >= thresholds.minimum_candidate_coarse_edge_precision
        and candidate_coarse_density_ratio <= thresholds.maximum_candidate_coarse_edge_density_ratio
    )
    return MacroDesignFidelityResult(
        passed=passed,
        tolerance_px=tolerance_px,
        silhouette_edge_pixels=silhouette_count,
        silhouette_edge_recall=silhouette_recall,
        coarse_edge_pixels=coarse_count,
        coarse_edge_recall=coarse_recall,
        semantic_edge_pixels=semantic_count,
        semantic_edge_recall=semantic_recall,
        evaluated_component_count=len(component_recalls),
        semantic_component_min_recall=component_min,
        reference_edge_p90_distance_px=reference_p90,
        candidate_coarse_edge_pixels=candidate_coarse_count,
        candidate_coarse_edge_precision=candidate_coarse_precision,
        candidate_coarse_edge_density_ratio=candidate_coarse_density_ratio,
    )


def _macro_fidelity_thresholds(
    fidelity_policy: Literal["precise", "balanced", "expressive"],
    *,
    tolerance_px: int,
) -> MacroFidelityThresholds:
    """Return reviewed, policy-specific macro thresholds.

    Precise is byte-for-byte the historical acceptance policy. Balanced only
    relaxes the source-directed silhouette/semantic measures that artistic
    facade and planting finishes legitimately perturb; reverse precision and
    density stay strict so noise cannot game the gate. Expressive is an
    advisory assessment because its result is always review-required.
    """

    if fidelity_policy == "precise":
        return MacroFidelityThresholds(
            minimum_silhouette_edge_recall=_MIN_MACRO_SILHOUETTE_EDGE_RECALL,
            minimum_coarse_edge_recall=_MIN_MACRO_COARSE_EDGE_RECALL,
            minimum_semantic_edge_recall=_MIN_MACRO_SEMANTIC_EDGE_RECALL,
            minimum_semantic_component_recall=(_MIN_MACRO_SEMANTIC_COMPONENT_RECALL),
            maximum_reference_p90_distance_px=min(
                _MAX_MACRO_REFERENCE_P90_DISTANCE_PX,
                tolerance_px * _MAX_MACRO_REFERENCE_P90_TOLERANCE_MULTIPLIER,
            ),
            minimum_candidate_coarse_edge_precision=(_MIN_MACRO_CANDIDATE_COARSE_EDGE_PRECISION),
            maximum_candidate_coarse_edge_density_ratio=(_MAX_MACRO_CANDIDATE_COARSE_EDGE_DENSITY_RATIO),
        )
    if fidelity_policy == "balanced":
        return MacroFidelityThresholds(
            minimum_silhouette_edge_recall=0.70,
            minimum_coarse_edge_recall=0.70,
            minimum_semantic_edge_recall=0.70,
            minimum_semantic_component_recall=0.70,
            maximum_reference_p90_distance_px=6.0,
            minimum_candidate_coarse_edge_precision=0.40,
            maximum_candidate_coarse_edge_density_ratio=3.0,
        )
    return MacroFidelityThresholds(
        minimum_silhouette_edge_recall=0.50,
        minimum_coarse_edge_recall=0.55,
        minimum_semantic_edge_recall=0.55,
        minimum_semantic_component_recall=0.65,
        maximum_reference_p90_distance_px=10.0,
        minimum_candidate_coarse_edge_precision=0.25,
        maximum_candidate_coarse_edge_density_ratio=4.5,
    )


def assess_instance_source_presence(
    source: Image.Image,
    candidate: Image.Image,
    proposal_mask: Image.Image,
    instance_id: Image.Image | None,
    instance_id_manifest: dict[str, Any] | None,
    *,
    fidelity_policy: Literal["precise", "balanced", "expressive"],
) -> InstanceSourcePresenceResult:
    """Measure source-edge presence independently for every visible authored instance."""

    if instance_id is None or not instance_id_manifest:
        return InstanceSourcePresenceResult(
            passed=True,
            evaluated_instance_count=0,
            weakest_instance_recall=None,
            missing_instance_ids=(),
            instance_recalls={},
        )
    if not (source.size == candidate.size == proposal_mask.size == instance_id.size):
        raise Direct3DValidationError("Instance-presence images must have identical dimensions")

    import cv2

    tolerance_px = max(2, min(4, round(math.hypot(*source.size) * 0.0015)))
    active = np.asarray(proposal_mask.convert("L"), dtype=np.uint8) >= 128
    source_anchor = (
        _beauty_structural_edges(source, proposal_mask) | _beauty_structural_edges(source, proposal_mask, coarse=True)
    ) & active
    candidate_anchor = (
        _beauty_structural_edges(candidate, proposal_mask)
        | _beauty_structural_edges(candidate, proposal_mask, coarse=True)
    ) & active
    if np.any(candidate_anchor):
        distance_to_candidate = cv2.distanceTransform(
            (~candidate_anchor).astype(np.uint8),
            cv2.DIST_L2,
            3,
        )
    else:
        distance_to_candidate = np.full(
            active.shape,
            math.hypot(*source.size),
            dtype=np.float32,
        )
    minimum_recall = {
        "precise": 0.72,
        "balanced": 0.60,
        "expressive": 0.45,
    }[fidelity_policy]
    instance_pixels = np.asarray(instance_id.convert("RGB"), dtype=np.uint8)
    kernel = np.ones(
        (tolerance_px * 2 + 1, tolerance_px * 2 + 1),
        dtype=np.uint8,
    )
    recalls: dict[str, float | None] = {}
    missing: list[str] = []
    evaluated: list[float] = []
    for color, descriptor in sorted(instance_id_manifest.items()):
        instance_identifier = str(descriptor.instance_id)
        if descriptor.semantic_class not in {"building", "street", "park"}:
            recalls[instance_identifier] = None
            continue
        region = np.all(
            instance_pixels == np.asarray(_hex_to_rgb(color), dtype=np.uint8),
            axis=2,
        )
        if int(np.count_nonzero(region)) < 16:
            # Fully occluded inventory entries remain server-bound but cannot
            # produce screen-space evidence in this capture.
            recalls[instance_identifier] = None
            continue
        region_band = (
            cv2.dilate(
                region.astype(np.uint8),
                kernel,
                iterations=1,
            )
            > 0
        )
        reference = source_anchor & region_band
        if int(np.count_nonzero(reference)) < 16:
            recalls[instance_identifier] = None
            continue
        instance_recall = float(np.mean(distance_to_candidate[reference] <= tolerance_px))
        recalls[instance_identifier] = instance_recall
        evaluated.append(instance_recall)
        if instance_recall < minimum_recall:
            missing.append(instance_identifier)
    return InstanceSourcePresenceResult(
        passed=not missing,
        evaluated_instance_count=len(evaluated),
        weakest_instance_recall=min(evaluated) if evaluated else None,
        missing_instance_ids=tuple(sorted(missing)),
        instance_recalls=recalls,
    )


def _unsupported_coarse_structure_analysis(
    source: Image.Image,
    candidate: Image.Image,
    proposal_mask: Image.Image,
    instance_id: Image.Image | None = None,
    instance_id_manifest: dict[str, Any] | None = None,
    *,
    detect_slender_additions: bool = False,
) -> tuple[UnsupportedStructureResult, Image.Image]:
    """Detect unsupported components and return a bounded local repair mask."""

    if source.size != candidate.size or source.size != proposal_mask.size:
        raise Direct3DValidationError("Unsupported-structure images must have identical dimensions")
    if instance_id is not None and instance_id.size != source.size:
        raise Direct3DValidationError("Unsupported-structure instance-ID image must match the source")

    import cv2

    full_frame_mask = Image.new("L", source.size, 255)
    source_anchor = _beauty_structural_edges(source, full_frame_mask) | _beauty_structural_edges(
        source, full_frame_mask, coarse=True
    )
    candidate_coarse = _beauty_structural_edges(
        candidate,
        full_frame_mask,
        coarse=True,
    )
    tolerance_px = max(3, min(6, round(math.hypot(*source.size) * 0.0025)))
    if np.any(source_anchor):
        distance_to_source = cv2.distanceTransform(
            (~source_anchor).astype(np.uint8),
            cv2.DIST_L2,
            3,
        )
    else:
        distance_to_source = np.full(
            source_anchor.shape,
            math.hypot(*source.size),
            dtype=np.float32,
        )
    unsupported = candidate_coarse & (distance_to_source > tolerance_px)

    # New facade/window detail is allowed only inside an existing building's
    # safely eroded source envelope. The boundary itself remains testable.
    if instance_id is not None and instance_id_manifest:
        pixels = np.asarray(instance_id.convert("RGB"), dtype=np.uint8)
        erosion_kernel = np.ones(
            (tolerance_px * 2 + 1, tolerance_px * 2 + 1),
            dtype=np.uint8,
        )
        for color, descriptor in instance_id_manifest.items():
            if descriptor.semantic_class != "building":
                continue
            region = np.all(
                pixels == np.asarray(_hex_to_rgb(color), dtype=np.uint8),
                axis=2,
            )
            allowed_interior = (
                cv2.erode(
                    region.astype(np.uint8),
                    erosion_kernel,
                    iterations=1,
                )
                > 0
            )
            unsupported &= ~allowed_interior

    unsupported = cv2.morphologyEx(
        unsupported.astype(np.uint8),
        cv2.MORPH_CLOSE,
        np.ones((5, 5), dtype=np.uint8),
        iterations=1,
    )
    component_count, labels, stats, _centroids = cv2.connectedComponentsWithStats(
        unsupported,
        connectivity=8,
    )
    frame_pixels = source.width * source.height
    # Connected edge pixels scale with perimeter, not frame area. An uncapped
    # area-relative floor therefore becomes less sensitive as capture
    # resolution grows: at 2048x1536 it used to ignore coherent 50x30 and
    # 80x20 additions. Keep a small noise floor, but cap it and independently
    # require a meaningful two-dimensional span/bounding area. These limits
    # remain strict enough to ignore isolated paving/foliage specks while
    # detecting building-sized structures at every supported capture size.
    component_floor = max(48, min(96, round(frame_pixels * 0.00012)))
    bbox_area_floor = max(256, min(900, round(frame_pixels * 0.00030)))
    bbox_min_span = max(8, min(16, round(min(source.size) * 0.01)))
    # A slender tower or long new street is still permanent structure. A
    # perimeter's density decreases with its size, so the earlier 8%/0.24
    # thresholds discarded coherent elongated additions at capture resolution.
    minimum_component_density = 0.04 if detect_slender_additions else 0.08
    minimum_component_aspect_ratio = 0.12 if detect_slender_additions else 0.24
    proposal = np.asarray(proposal_mask.convert("L"), dtype=np.uint8) >= 128
    proposal_components = 0
    context_components = 0
    largest_pixels = 0
    largest_bbox_fraction = 0.0
    repair_mask = np.zeros(source_anchor.shape, dtype=np.uint8)
    repair_pad = max(
        tolerance_px * 2,
        min(28, round(min(source.size) * 0.012)),
    )
    component_records: list[dict[str, Any]] = []
    qualifying_components: list[int] = []
    for component in range(1, component_count):
        pixel_count = int(stats[component, cv2.CC_STAT_AREA])
        bbox_x = int(stats[component, cv2.CC_STAT_LEFT])
        bbox_y = int(stats[component, cv2.CC_STAT_TOP])
        bbox_width = int(stats[component, cv2.CC_STAT_WIDTH])
        bbox_height = int(stats[component, cv2.CC_STAT_HEIGHT])
        bbox_area = bbox_width * bbox_height
        bbox_fraction = float(bbox_area / max(1, frame_pixels))
        bbox_aspect_ratio = min(bbox_width, bbox_height) / max(
            1,
            max(bbox_width, bbox_height),
        )
        component_density = pixel_count / max(1, bbox_area)
        if (
            pixel_count >= max(24, component_floor // 3)
            and bbox_area >= 96
            and component_density >= 0.035
            and bbox_aspect_ratio >= 0.18
        ):
            component_records.append(
                {
                    "component": component,
                    "x0": bbox_x,
                    "y0": bbox_y,
                    "x1": bbox_x + bbox_width,
                    "y1": bbox_y + bbox_height,
                }
            )
        if (
            pixel_count < component_floor
            or bbox_area < bbox_area_floor
            or min(bbox_width, bbox_height) < bbox_min_span
            # A coherent permanent addition produces a genuinely
            # two-dimensional, substantially closed edge component. Sparse
            # material grain, foliage, hatch and long photogrammetry seams are
            # legitimate full-frame finish and must not masquerade as a new
            # building merely because their loose bounding box is large.
            or component_density < minimum_component_density
            or bbox_aspect_ratio < minimum_component_aspect_ratio
        ):
            continue
        component_region = labels == component
        if np.any(component_region & proposal):
            proposal_components += 1
        if np.any(component_region & ~proposal):
            context_components += 1
        if pixel_count > largest_pixels:
            largest_pixels = pixel_count
            largest_bbox_fraction = bbox_fraction
        qualifying_components.append(component)

    # Authoritative source edges can split one invented object into several
    # unsupported fragments. Group only nearby, reasonably two-dimensional
    # fragments around each qualifying seed, then fill their convex hull. This
    # removes the whole object without replacing a conspicuous rectangular
    # neighborhood of otherwise valid provider pixels.
    records_by_component = {int(record["component"]): record for record in component_records}
    for seed_component in qualifying_components:
        seed = records_by_component.get(seed_component)
        if seed is None:
            continue
        grouped = {seed_component}
        group_x0 = int(seed["x0"])
        group_y0 = int(seed["y0"])
        group_x1 = int(seed["x1"])
        group_y1 = int(seed["y1"])
        changed = True
        while changed:
            changed = False
            link_distance = max(
                repair_pad * 2,
                round(
                    max(
                        group_x1 - group_x0,
                        group_y1 - group_y0,
                    )
                    * 0.18
                ),
            )
            for record in component_records:
                record_component = int(record["component"])
                if record_component in grouped:
                    continue
                dx = max(
                    0,
                    group_x0 - int(record["x1"]),
                    int(record["x0"]) - group_x1,
                )
                dy = max(
                    0,
                    group_y0 - int(record["y1"]),
                    int(record["y0"]) - group_y1,
                )
                if dx > link_distance or dy > link_distance:
                    continue
                grouped.add(record_component)
                group_x0 = min(group_x0, int(record["x0"]))
                group_y0 = min(group_y0, int(record["y0"]))
                group_x1 = max(group_x1, int(record["x1"]))
                group_y1 = max(group_y1, int(record["y1"]))
                changed = True

        grouped_pixels = np.isin(labels, list(grouped))
        grouped_yx = np.argwhere(grouped_pixels)
        if grouped_yx.shape[0] < 3:
            continue
        grouped_xy = grouped_yx[:, [1, 0]].astype(np.int32)
        hull = cv2.convexHull(grouped_xy)
        cv2.fillConvexPoly(repair_mask, hull, 255)

    if np.any(repair_mask):
        repair_mask = cv2.dilate(
            repair_mask,
            np.ones(
                (repair_pad * 2 + 1, repair_pad * 2 + 1),
                dtype=np.uint8,
            ),
            iterations=1,
        )
    return (
        UnsupportedStructureResult(
            passed=(proposal_components + context_components) == 0,
            largest_component_pixels=largest_pixels,
            largest_component_bbox_fraction=largest_bbox_fraction,
            proposal_component_count=proposal_components,
            context_component_count=context_components,
        ),
        Image.fromarray(repair_mask, mode="L"),
    )


def assess_unsupported_coarse_structure(
    source: Image.Image,
    candidate: Image.Image,
    proposal_mask: Image.Image,
    instance_id: Image.Image | None = None,
    instance_id_manifest: dict[str, Any] | None = None,
    *,
    detect_slender_additions: bool = False,
) -> UnsupportedStructureResult:
    """Detect large new coarse components outside approved building envelopes."""

    result, _repair_mask = _unsupported_coarse_structure_analysis(
        source,
        candidate,
        proposal_mask,
        instance_id,
        instance_id_manifest,
        detect_slender_additions=detect_slender_additions,
    )
    return result


def _safe_instance_interior_mask(
    instance_id: Image.Image,
    instance_id_manifest: dict[str, Any],
    missing_instance_ids: set[str],
    *,
    semantic_classes: frozenset[str],
) -> Image.Image:
    """Build a safely inset mask from server-bound persisted instances.

    The mask is deliberately only an admission envelope. Every composite made
    with it must still pass the authoritative instance-presence and unsupported
    coarse-structure gates before it can be returned.
    """

    import cv2

    pixels = np.asarray(instance_id.convert("RGB"), dtype=np.uint8)
    safe_interiors = np.zeros(
        (instance_id.height, instance_id.width),
        dtype=np.uint8,
    )
    scale = _finish_detail_scale(instance_id.width, instance_id.height)
    unsupported_tolerance_px = max(
        3,
        min(6, round(math.hypot(*instance_id.size) * 0.0025)),
    )
    erosion_radius = max(
        unsupported_tolerance_px,
        3,
        round(4 * scale),
    )
    erosion_kernel = np.ones(
        (erosion_radius * 2 + 1, erosion_radius * 2 + 1),
        dtype=np.uint8,
    )
    for color, descriptor in sorted(instance_id_manifest.items()):
        if descriptor.semantic_class not in semantic_classes or descriptor.instance_id in missing_instance_ids:
            continue
        region = np.all(
            pixels == np.asarray(_hex_to_rgb(color), dtype=np.uint8),
            axis=2,
        )
        safe_interiors |= cv2.erode(
            region.astype(np.uint8),
            erosion_kernel,
            iterations=1,
        )
    return Image.fromarray(safe_interiors * 255, mode="L")


def _scene_hybrid_with_instance_interiors(
    source: Image.Image,
    provider: Image.Image,
    object_id: Image.Image | None,
    object_id_manifest: dict[str, str] | None,
    instance_id: Image.Image,
    instance_id_manifest: dict[str, Any],
    missing_instance_ids: set[str],
    *,
    semantic_classes: frozenset[str],
) -> tuple[Image.Image, FinishFusionResult]:
    """Finish source phase, then admit provider pixels in persisted interiors."""

    full_frame_mask = Image.new("L", source.size, 255)
    source_phase = _fuse_source_geometry_with_provider_finish(
        source,
        provider,
        full_frame_mask,
        object_id,
        object_id_manifest,
    )
    scale = _finish_detail_scale(source.width, source.height)
    safe_interiors = _safe_instance_interior_mask(
        instance_id,
        instance_id_manifest,
        missing_instance_ids,
        semantic_classes=semantic_classes,
    )
    hybrid, _exterior_count, _exterior_delta = hard_composite_direct_3d(
        source_phase.image,
        provider,
        safe_interiors,
        inward_feather_px=max(2.0, 2.5 * scale),
    )
    return hybrid, source_phase


def _balanced_scene_hybrid(
    source: Image.Image,
    provider: Image.Image,
    object_id: Image.Image | None,
    object_id_manifest: dict[str, str] | None,
    instance_id: Image.Image,
    instance_id_manifest: dict[str, Any],
    missing_instance_ids: set[str],
) -> tuple[Image.Image, FinishFusionResult]:
    """Source-phase public realm plus provider pixels in building interiors.

    Parks, streets, ground and landscape receive only source-owned spatial
    detail whose contrast/tone is informed by provider statistics. Raw provider
    pixels are limited to safely inset persisted building envelopes, preventing
    a facade, pavilion or other invented structure from hiding inside a broad
    public-realm instance.
    """

    return _scene_hybrid_with_instance_interiors(
        source,
        provider,
        object_id,
        object_id_manifest,
        instance_id,
        instance_id_manifest,
        missing_instance_ids,
        semantic_classes=frozenset({"building"}),
    )


def _locally_repair_scene_candidate(
    source: Image.Image,
    provider: Image.Image,
    proposal_mask: Image.Image,
    object_id: Image.Image | None,
    object_id_manifest: dict[str, str] | None,
    instance_id: Image.Image,
    instance_id_manifest: dict[str, Any],
    missing_instance_ids: set[str],
) -> tuple[Image.Image, FinishFusionResult, float]:
    """Repair only unsupported additions or missing persisted instances.

    The full registered provider render remains authoritative everywhere
    outside the bounded repair mask. Unsupported provider-only objects are
    removed with style-preserving local inpainting; missing authored instances
    are restored from source-owned phase pixels. The unchanged inventory gates
    validate the result before it can be returned.
    """

    import cv2

    _unsupported, unsupported_mask = _unsupported_coarse_structure_analysis(
        source,
        provider,
        proposal_mask,
        instance_id,
        instance_id_manifest,
    )
    unsupported_pixels = np.asarray(
        unsupported_mask.convert("L"),
        dtype=np.uint8,
    ).copy()
    missing_restore = np.zeros(unsupported_pixels.shape, dtype=np.uint8)

    if missing_instance_ids:
        instance_pixels = np.asarray(instance_id.convert("RGB"), dtype=np.uint8)
        for color, descriptor in sorted(instance_id_manifest.items()):
            if descriptor.instance_id not in missing_instance_ids:
                continue
            region = np.all(
                instance_pixels == np.asarray(_hex_to_rgb(color), dtype=np.uint8),
                axis=2,
            )
            missing_restore |= cv2.dilate(
                region.astype(np.uint8),
                np.ones((5, 5), dtype=np.uint8),
                iterations=1,
            )

    source_phase = _fuse_source_geometry_with_provider_finish(
        source,
        provider,
        Image.new("L", source.size, 255),
        object_id,
        object_id_manifest,
    )
    repair_pixels = unsupported_pixels | (missing_restore * 255)
    repair_coverage = float(np.count_nonzero(repair_pixels) / max(1, repair_pixels.size))
    if not np.any(repair_pixels):
        return provider.convert("RGB").copy(), source_phase, repair_coverage

    repaired = provider.convert("RGB").copy()
    if np.any(unsupported_pixels):
        provider_bgr = cv2.cvtColor(
            np.asarray(repaired, dtype=np.uint8),
            cv2.COLOR_RGB2BGR,
        )
        inpaint_radius = max(
            3.0,
            min(
                9.0,
                5.0 * _finish_detail_scale(source.width, source.height),
            ),
        )
        inpainted_bgr = cv2.inpaint(
            provider_bgr,
            unsupported_pixels,
            inpaint_radius,
            cv2.INPAINT_TELEA,
        )
        repaired = Image.fromarray(
            cv2.cvtColor(inpainted_bgr, cv2.COLOR_BGR2RGB),
            mode="RGB",
        )

    if np.any(missing_restore):
        repaired, _exterior_count, _exterior_delta = hard_composite_direct_3d(
            repaired,
            source_phase.image,
            Image.fromarray(missing_restore * 255, mode="L"),
            inward_feather_px=max(
                2.0,
                2.5 * _finish_detail_scale(source.width, source.height),
            ),
        )
    return repaired, source_phase, repair_coverage


def _global_tone_source_finish(
    source: Image.Image,
    provider: Image.Image,
) -> Image.Image:
    """Apply bounded provider colour statistics without provider spatial structure.

    The transform is one affine operation per RGB channel. Its coefficients are
    derived from whole-frame robust statistics, so provider pixels cannot create
    a line, silhouette, building, or other local feature in the returned image.
    Source contrast and all source-owned spatial detail remain in place.
    """

    if source.size != provider.size:
        raise Direct3DValidationError("Source-locked tone images must have identical dimensions")

    source_rgb = np.asarray(source.convert("RGB"), dtype=np.float32)
    provider_rgb = np.asarray(provider.convert("RGB"), dtype=np.float32)
    source_flat = source_rgb.reshape((-1, 3))
    provider_flat = provider_rgb.reshape((-1, 3))
    source_p10, source_median, source_p90 = np.percentile(
        source_flat,
        (10, 50, 90),
        axis=0,
    )
    provider_p10, provider_median, provider_p90 = np.percentile(
        provider_flat,
        (10, 50, 90),
        axis=0,
    )
    source_span = np.maximum(source_p90 - source_p10, 1.0)
    provider_span = np.maximum(provider_p90 - provider_p10, 1.0)

    # Keep the fallback visibly finished but deliberately conservative. Large
    # provider exposure/white-balance changes are review information, not a
    # reason to crush or erase source edges in the safe returned image.
    scale = np.clip(provider_span / source_span, 0.90, 1.10)
    shift = np.clip(provider_median - source_median, -18.0, 18.0)
    transformed = (
        (source_rgb - source_median.reshape((1, 1, 3))) * scale.reshape((1, 1, 3))
        + source_median.reshape((1, 1, 3))
        + shift.reshape((1, 1, 3))
    )
    # A partial blend further protects low-contrast source structure while
    # retaining provider-derived colour and exposure direction.
    finished = source_rgb * 0.55 + transformed * 0.45
    return Image.fromarray(
        np.clip(np.rint(finished), 0, 255).astype(np.uint8),
        mode="RGB",
    )


def _source_locked_scene_fallback(
    source: Image.Image,
    provider: Image.Image,
    instance_id: Image.Image,
    instance_id_manifest: dict[str, Any],
    missing_instance_ids: set[str],
    *,
    admit_building_interiors: bool,
) -> Image.Image:
    """Return a source-geometry fallback with optional safe facade interiors."""

    toned_source = _global_tone_source_finish(source, provider)
    if not admit_building_interiors:
        return toned_source

    import cv2

    pixels = np.asarray(instance_id.convert("RGB"), dtype=np.uint8)
    safe_buildings = np.zeros((source.height, source.width), dtype=np.uint8)
    scale = _finish_detail_scale(source.width, source.height)
    # Match or exceed the unsupported-structure gate's building-envelope
    # erosion so provider pixels cannot reach an authored silhouette.
    unsupported_tolerance_px = max(
        3,
        min(6, round(math.hypot(*source.size) * 0.0025)),
    )
    erosion_radius = max(
        unsupported_tolerance_px,
        3,
        round(4 * scale),
    )
    erosion_kernel = np.ones(
        (erosion_radius * 2 + 1, erosion_radius * 2 + 1),
        dtype=np.uint8,
    )
    for color, descriptor in sorted(instance_id_manifest.items()):
        if descriptor.semantic_class != "building" or descriptor.instance_id in missing_instance_ids:
            continue
        region = np.all(
            pixels == np.asarray(_hex_to_rgb(color), dtype=np.uint8),
            axis=2,
        )
        safe_buildings |= cv2.erode(
            region.astype(np.uint8),
            erosion_kernel,
            iterations=1,
        )

    if not np.any(safe_buildings):
        return toned_source
    hybrid, _exterior_count, _exterior_delta = hard_composite_direct_3d(
        toned_source,
        provider,
        Image.fromarray(safe_buildings * 255, mode="L"),
        inward_feather_px=max(2.0, 2.5 * scale),
    )
    return hybrid


def assess_scene_visual_change(
    source: Image.Image,
    candidate: Image.Image,
    proposal_mask: Image.Image,
) -> VisualChangeResult:
    """Reject an expensive scene result that is only identity/colour grading."""

    if source.size != candidate.size or source.size != proposal_mask.size:
        raise Direct3DValidationError("Visual-change images and proposal mask must have identical dimensions")

    import cv2

    source_rgb = np.asarray(source.convert("RGB"), dtype=np.float32)
    candidate_rgb = np.asarray(candidate.convert("RGB"), dtype=np.float32)
    active = np.asarray(proposal_mask.convert("L"), dtype=np.uint8) >= 128
    if not np.any(active):
        raise Direct3DValidationError("Visual-change assessment requires proposal pixels")
    absolute_delta = np.abs(candidate_rgb - source_rgb)
    whole_frame_mad = float(np.mean(absolute_delta))
    proposal_mad = float(np.mean(absolute_delta[active]))

    # Full-scene presentation quality must reach the surrounding built/ground
    # context, not merely the proposal or an easy-to-change sky. Measure only
    # mask-zero pixels in the lower 55% of the frame for this evidence.
    context = _scene_lower_context_mask(proposal_mask)
    context_pixel_count = int(np.count_nonzero(context))
    context_mad = float(np.mean(absolute_delta[context])) if context_pixel_count else 0.0

    source_luma = _finish_luminance(source_rgb)
    candidate_luma = _finish_luminance(candidate_rgb)
    source_detail = source_luma - cv2.GaussianBlur(
        source_luma,
        (0, 0),
        sigmaX=1.2,
        sigmaY=1.2,
        borderType=cv2.BORDER_REFLECT,
    )
    candidate_detail = candidate_luma - cv2.GaussianBlur(
        candidate_luma,
        (0, 0),
        sigmaX=1.2,
        sigmaY=1.2,
        borderType=cv2.BORDER_REFLECT,
    )
    detail_delta_p75 = float(np.percentile(np.abs(candidate_detail - source_detail)[active], 75))
    context_detail_delta_p75 = (
        float(
            np.percentile(
                np.abs(candidate_detail - source_detail)[context],
                75,
            )
        )
        if context_pixel_count
        else 0.0
    )

    # Regress out a global luminance gain/offset before looking for spatial
    # change. This makes the floor invariant to ordinary exposure, contrast and
    # colour grading while retaining provider-authored material/foliage detail.
    def _photometric_residual_p95(region: np.ndarray) -> float:
        if not np.any(region):
            return 0.0
        source_values = source_luma[region].astype(np.float32, copy=False)
        candidate_values = candidate_luma[region].astype(np.float32, copy=False)
        source_centered = source_values - float(np.mean(source_values))
        denominator = float(np.dot(source_centered, source_centered))
        gain = (
            float(
                np.dot(
                    source_centered,
                    candidate_values - np.mean(candidate_values),
                )
            )
            / denominator
            if denominator > 1e-8
            else 1.0
        )
        offset = float(np.mean(candidate_values) - gain * np.mean(source_values))
        residual = candidate_values - (source_values * gain + offset)
        return float(np.percentile(np.abs(residual), 95))

    photometric_residual_p95 = _photometric_residual_p95(active)
    context_photometric_residual_p95 = _photometric_residual_p95(context)

    source_edges = _beauty_structural_edges(source, proposal_mask)
    candidate_edges = _beauty_structural_edges(candidate, proposal_mask)
    exclusion_radius = max(4, min(8, round(math.hypot(*source.size) * 0.0025)))
    source_edge_band = (
        cv2.dilate(
            source_edges.astype(np.uint8),
            np.ones(
                (exclusion_radius * 2 + 1, exclusion_radius * 2 + 1),
                dtype=np.uint8,
            ),
            iterations=1,
        )
        > 0
    )
    # Ignore the proposal seam itself: an additive colour grade creates a
    # synthetic mask-boundary edge even though it added no scene detail.
    safe_active = (
        cv2.erode(
            active.astype(np.uint8),
            np.ones((7, 7), dtype=np.uint8),
            iterations=1,
        )
        > 0
    )
    novel_edges = candidate_edges & ~source_edge_band & safe_active
    novel_edge_coverage = float(np.count_nonzero(novel_edges) / max(1, int(np.count_nonzero(active))))
    passed = (
        whole_frame_mad >= _MIN_SCENE_WHOLE_FRAME_MEAN_ABSOLUTE_DELTA
        and proposal_mad >= _MIN_SCENE_PROPOSAL_MEAN_ABSOLUTE_DELTA
        and photometric_residual_p95 >= _MIN_SCENE_PROPOSAL_PHOTOMETRIC_RESIDUAL_P95
        and (
            detail_delta_p75 >= _MIN_SCENE_PROPOSAL_DETAIL_DELTA_P75
            or novel_edge_coverage >= _MIN_SCENE_NOVEL_DETAIL_EDGE_COVERAGE
        )
        and (
            context_mad >= _MIN_SCENE_CONTEXT_MEAN_ABSOLUTE_DELTA
            or context_photometric_residual_p95 >= _MIN_SCENE_CONTEXT_PHOTOMETRIC_RESIDUAL_P95
        )
        and context_detail_delta_p75 >= _MIN_SCENE_CONTEXT_DETAIL_DELTA_P75
    )
    return VisualChangeResult(
        passed=passed,
        whole_frame_mean_absolute_delta=whole_frame_mad,
        proposal_mean_absolute_delta=proposal_mad,
        proposal_detail_delta_p75=detail_delta_p75,
        proposal_photometric_residual_p95=photometric_residual_p95,
        novel_detail_edge_coverage=novel_edge_coverage,
        context_mean_absolute_delta=context_mad,
        context_photometric_residual_p95=context_photometric_residual_p95,
        context_detail_delta_p75=context_detail_delta_p75,
        context_pixel_count=context_pixel_count,
        context_frame_top_fraction=_SCENE_CONTEXT_TOP_FRACTION,
    )


def assess_reproject_output_sanity(
    source: Image.Image,
    candidate: Image.Image,
    object_id: Image.Image | None = None,
    object_id_manifest: dict[str, str] | None = None,
) -> ReprojectOutputSanityResult:
    """Reject empty, unchanged, or noise-like projection outputs.

    Screen-space macro comparison is invalid after an intentional camera
    transformation. This is therefore a conservative content/inventory proxy,
    not proof of semantic correctness: the result must be materially changed,
    have usable tonal range, carry bounded structural edges across the frame,
    and contain enough significant edge components for the visible source
    inventory. Human visual review remains required for reproject styles.
    """

    if source.size != candidate.size:
        raise Direct3DValidationError("Reproject source and provider image must have identical dimensions")
    if object_id is not None and object_id.size != source.size:
        raise Direct3DValidationError("Reproject object-ID image must match the source dimensions")

    import cv2

    source_rgb = np.asarray(source.convert("RGB"), dtype=np.float32)
    candidate_rgb = np.asarray(candidate.convert("RGB"), dtype=np.float32)
    whole_frame_mad = float(np.mean(np.abs(candidate_rgb - source_rgb)))
    luminance = _finish_luminance(candidate_rgb)
    luminance_standard_deviation = float(np.std(luminance))
    luminance_dynamic_range_p90 = float(np.percentile(luminance, 95) - np.percentile(luminance, 5))

    luminance_u8 = np.clip(luminance, 0, 255).astype(np.uint8)
    blurred = cv2.GaussianBlur(
        luminance_u8,
        (0, 0),
        sigmaX=1.0,
        sigmaY=1.0,
        borderType=cv2.BORDER_REFLECT,
    )
    gradient_x = cv2.Sobel(blurred, cv2.CV_32F, 1, 0, ksize=3)
    gradient_y = cv2.Sobel(blurred, cv2.CV_32F, 0, 1, ksize=3)
    gradient = cv2.magnitude(gradient_x, gradient_y)
    nonzero_gradient = gradient[gradient > 1.0]
    high_threshold = float(np.percentile(nonzero_gradient, 70)) if nonzero_gradient.size else 48.0
    high_threshold = min(140.0, max(42.0, high_threshold))
    edges = (
        cv2.Canny(
            blurred,
            threshold1=max(16.0, high_threshold * 0.42),
            threshold2=high_threshold,
            L2gradient=True,
        )
        > 0
    )
    structural_edge_coverage = float(np.mean(edges))

    occupied_edge_cells = 0
    for row in range(4):
        top = round(row * source.height / 4)
        bottom = round((row + 1) * source.height / 4)
        for column in range(4):
            left = round(column * source.width / 4)
            right = round((column + 1) * source.width / 4)
            cell = edges[top:bottom, left:right]
            if cell.size and float(np.mean(cell)) >= 0.001:
                occupied_edge_cells += 1

    connected_edges = cv2.morphologyEx(
        edges.astype(np.uint8),
        cv2.MORPH_CLOSE,
        np.ones((3, 3), dtype=np.uint8),
        iterations=1,
    )
    component_count, _labels, stats, _centroids = cv2.connectedComponentsWithStats(
        connected_edges,
        connectivity=8,
    )
    component_area_floor = max(12, round(source.width * source.height * 0.00002))
    significant_edge_component_count = sum(
        int(stats[index, cv2.CC_STAT_AREA]) >= component_area_floor for index in range(1, component_count)
    )
    source_inventory, _labels = _visible_semantic_components(
        object_id,
        object_id_manifest,
    )
    expected_inventory_count = sum(source_inventory.values())
    required_edge_component_count = max(1, min(3, expected_inventory_count))

    passed = (
        whole_frame_mad >= _MIN_REPROJECT_WHOLE_FRAME_MEAN_ABSOLUTE_DELTA
        and luminance_standard_deviation >= _MIN_REPROJECT_LUMINANCE_STANDARD_DEVIATION
        and luminance_dynamic_range_p90 >= _MIN_REPROJECT_LUMINANCE_DYNAMIC_RANGE_P90
        and structural_edge_coverage >= _MIN_REPROJECT_STRUCTURAL_EDGE_COVERAGE
        and structural_edge_coverage <= _MAX_REPROJECT_STRUCTURAL_EDGE_COVERAGE
        and occupied_edge_cells >= _MIN_REPROJECT_OCCUPIED_EDGE_CELLS
        and significant_edge_component_count >= required_edge_component_count
    )
    return ReprojectOutputSanityResult(
        passed=passed,
        whole_frame_mean_absolute_delta=whole_frame_mad,
        luminance_standard_deviation=luminance_standard_deviation,
        luminance_dynamic_range_p90=luminance_dynamic_range_p90,
        structural_edge_coverage=structural_edge_coverage,
        occupied_edge_cells=occupied_edge_cells,
        significant_edge_component_count=significant_edge_component_count,
        required_edge_component_count=required_edge_component_count,
    )


_PRESENTATION_STYLE_TREATMENTS: dict[str, str] = {
    "photorealistic": "a high-end contemporary architectural visualization with photographic realism",
    "photomontage": "a polished architectural photomontage integrated seamlessly into the photographed city",
    "development": "a completed-development visualization with crisp facades, credible roofs and public realm",
    "atmospheric": "warm atmospheric architectural photography with soft haze, directional light and planted depth",
    "winter": "convincing winter architectural photography with seasonal vegetation, snow and cold daylight",
    "night": "realistic blue-hour architectural photography with plausible interior and street lighting",
    "watercolour": "a refined architectural watercolour on textured paper",
    "charcoal": "a controlled tonal charcoal architectural illustration",
    "marker-render": "a professional architectural marker rendering with deliberate material strokes",
    "pen-and-ink": "a precise architectural pen-and-ink illustration",
    "survey": "neutral, highly legible large-format survey photography",
    "documentary": "honest documentary architectural photography with restrained natural variation",
    "site-plan": "a clean top-down orthographic architectural site plan",
    "site-plan-photo": "a near-nadir photographic drone site-plan view",
    "blueprint": "a strict orthographic architectural blueprint",
    "site-plan-watercolor": "a near-nadir watercolour architectural site plan",
    "isometric": "a clean 30-degree axonometric architectural visualization",
    "clay-maquette": "high-angle studio photography of a monochrome architectural clay maquette",
    "woodblock": "a graphic architectural woodblock print",
    "collage": "a layered post-digital architectural collage",
    "risograph": "a controlled limited-palette architectural risograph",
    "pixel-art": "a polished grid-aligned architectural pixel-art scene",
}

_REPROJECT_VIEW_INSTRUCTIONS: dict[str, str] = {
    "site-plan": "Transform the camera to a strict north-up orthographic plan looking straight down.",
    "site-plan-photo": "Transform the camera to a near-nadir drone view, about 15-20 degrees from vertical.",
    "blueprint": "Transform the camera to a strict north-up orthographic plan looking straight down.",
    "site-plan-watercolor": "Transform the camera to a near-nadir architectural plan view.",
    "isometric": "Transform the camera to a consistent 30-degree axonometric view with no perspective distortion.",
    "clay-maquette": "Transform the camera to a high-angle isometric studio-model view.",
}


def _presentation_prompt(
    client_prompt: str,
    *,
    presentation_mode: Literal["scene", "reproject"],
    style: str,
    object_id_manifest: dict[str, str] | None,
    instance_id_manifest: dict[str, Any] | None = None,
    server_inventory: list[dict[str, Any]] | None = None,
    visible_component_summary: dict[str, int] | None = None,
    view_mode: Literal["aerial", "street"] = "aerial",
    archetype_reference_labels: list[str] | None = None,
    control_bundle_version: Literal[1, 2] = 1,
) -> str:
    """Build a natural provider-first prompt with one final design lock."""

    del visible_component_summary
    has_object_id = bool(object_id_manifest)
    has_instance_id = bool(instance_id_manifest)
    base_guide_number = 2 + int(has_object_id) + int(has_instance_id)
    geometry_control_count = 3 if control_bundle_version == 2 else 0
    guide_number = base_guide_number + geometry_control_count
    image_roles = [
        "Image 1 is the clean 3D source and primary visual reference",
    ]
    if has_object_id:
        image_roles.append("Image 2 is class-ID metadata for distinguishing proposal roles")
    if has_instance_id:
        instance_number = 2 + int(has_object_id)
        image_roles.append(
            f"Image {instance_number} is instance-ID metadata in which each "
            "non-black colour is one authored instance"
        )
    if control_bundle_version == 2:
        image_roles.extend(
            [
                f"Image {base_guide_number} is renderer depth metadata",
                f"Image {base_guide_number + 1} is renderer view-normal metadata",
                f"Image {base_guide_number + 2} is exact source-material ID metadata",
            ]
        )
    image_roles.append(f"Image {guide_number} is monochrome structure and layout metadata")
    guide = (
        "REFERENCE IMAGES: "
        + "; ".join(image_roles)
        + "; use the metadata only as design evidence and never render its "
        "colours, contours, labels or text."
    )
    if archetype_reference_labels:
        reference_roles = [
            f"Image {guide_number + 1 + offset}: {label}" for offset, label in enumerate(archetype_reference_labels)
        ]
        guide += (
            " ARCHETYPE REFERENCES: "
            + "; ".join(reference_roles)
            + ". Unlike the metadata above, these are authored design sources: "
            "apply every BUILDING reference strictly to its named building; "
            "apply every PARK or STREET reference to its named public-realm "
            "zone for material finish only. Capacity and placement are already resolved in Image 1. "
            "Reference identity overrides generic material examples while "
            "Image 1 remains authoritative for geometry, massing, position, "
            "polygon extent, cross-section and camera."
        )
    archetype_identity_lock = (
        " ARCHETYPE IDENTITY LOCK: Attached building references are strict: "
        "preserve their selected architectural language, material hierarchy, "
        "facade rhythm, openings, roof character and detailing; never replace "
        "them with another period or style. Attached park and street references "
        "provide surface and material detail only: retain Image 1's exact path, "
        "pavilion, play-feature, tree and furnishing positions and counts. Do not "
        "copy the reference layout or exchange facilities. Generic art-"
        "direction material examples apply only when that material already exists "
        "in Image 1 or its attached reference."
        if archetype_reference_labels
        else ""
    )
    inventory = _server_inventory_prompt(server_inventory)
    treatment = _PRESENTATION_STYLE_TREATMENTS.get(
        style,
        _PRESENTATION_STYLE_TREATMENTS["photorealistic"],
    )
    if presentation_mode == "scene":
        if view_mode == "street":
            task = (
                f"FULL-FRAME TASK: Image 1 is a street-level, eye-height (~1.7 m) "
                f"pedestrian view of the authored development standing in real "
                f"photographed context. Transform all of it into {treatment}, "
                "re-rendering the modelled buildings and surrounding context as "
                "one coherent finished image with consistent materials, light, "
                "shadows, weather and atmospheric depth while removing visible "
                "CGI and photogrammetry seams. Keep the pedestrian standpoint "
                "and lens exactly — no aerial, elevated or pulled-back "
                "reinterpretation."
            )
        else:
            task = (
                f"FULL-FRAME TASK: Transform all of Image 1 into {treatment}, "
                "re-rendering the proposal and surrounding photographed or Google "
                "Tiles context as one coherent finished image with consistent "
                "materials, light, shadows, weather and atmospheric depth while "
                "removing visible CGI and photogrammetry seams. Blend the proposal "
                "site's edges seamlessly into the surrounding streets and "
                "sidewalks with natural curbs, grading and planting — never render "
                "the site boundary as a raised platform, plinth, retaining wall, "
                "or visible cut edge."
            )
        final_lock = (
            "FINAL PRESERVATION LOCK: Preserve Image 1's exact camera angle, "
            "projection, framing, horizon, permanent building count, massing, "
            "floor count, facade proportions and opening pattern, footprints, "
            "setbacks, rooflines, site layout, terrain, street, intersection and "
            "path topology, park boundaries, water bodies and major occlusions. "
            "Do not add, remove, split, merge, move or redesign any permanent "
            "building, road, park, water body or site feature. You may add only "
            "non-permanent entourage and finish detail such as people, bicycles, "
            "vehicles, cafe seating, planting, benches and lighting." + archetype_identity_lock + " "
            "CONTEXT IDENTITY: every existing building around the proposal is a "
            "real photographed structure — keep each one recognizably itself, "
            "with its own cladding colours, materials, window pattern and roof "
            "form, improving only photographic clarity. Never re-clad, restyle, "
            "modernize or replace a neighbouring building."
            " " + RENDER_PRESERVATION_LOCK
        )
        if view_mode == "street":
            final_lock += (
                " Respect Image 1's depth ordering exactly: nearer volumes "
                "occlude farther ones; never merge, float or stack separate "
                "buildings."
            )
    else:
        task = (
            f"FULL-FRAME TASK: Transform all of Image 1 into {treatment}. "
            f"{_REPROJECT_VIEW_INSTRUCTIONS[style]} Re-render the proposal and "
            "surrounding context as one coherent finished image."
        )
        final_lock = (
            "FINAL PRESERVATION LOCK: Apply only the requested projection change; "
            "preserve the exact authored permanent-instance count, relative massing, "
            "floor count, facade proportions and opening pattern, footprints, "
            "rooflines, site layout, street, intersection and path topology, park "
            "boundaries, water bodies and adjacency relationships. Do not add, "
            "remove, split, merge, move or redesign any permanent building, road, "
            "park, water body or site feature." + archetype_identity_lock
            + " " + RENDER_PRESERVATION_LOCK
        )
    prompt_prefix = "\n".join(
        [
            task,
            guide,
            inventory,
            "PRIMARY ART DIRECTION: ",
        ]
    )
    prompt_suffix = f"\n{final_lock}"
    # Truncate only client-controlled art direction. The final inventory lock
    # must remain present and last even when a caller supplies the maximum
    # accepted prompt length.
    available_art_direction = max(
        0,
        31_900 - len(prompt_prefix) - len(prompt_suffix),
    )
    prompt = prompt_prefix + client_prompt.strip()[:available_art_direction] + prompt_suffix
    return prompt


def _authoritative_prompt(
    client_prompt: str,
    object_id_manifest: dict[str, str] | None,
    instance_id_manifest: dict[str, Any] | None = None,
    server_inventory: list[dict[str, Any]] | None = None,
    visible_component_summary: dict[str, int] | None = None,
    archetype_reference_labels: list[str] | None = None,
    control_bundle_version: Literal[1, 2] = 1,
) -> str:
    has_object_id = bool(object_id_manifest)
    has_instance_id = bool(instance_id_manifest)
    base_guide_number = 2 + int(has_object_id) + int(has_instance_id)
    geometry_control_count = 3 if control_bundle_version == 2 else 0
    structural_guide_number = base_guide_number + geometry_control_count
    id_guidance = (
        " Image 2 is a machine-readable class-ID guide only; use its classes to "
        "understand object ownership. Its legend is metadata only: never reproduce, "
        "blend, or expose any class-ID color in the rendered image."
        if has_object_id
        else ""
    )
    legend = ""
    if object_id_manifest:
        entries = "; ".join(f"{color}={semantic_class}" for color, semantic_class in sorted(object_id_manifest.items()))
        legend = f"\n\nCLASS-ID METADATA LEGEND (Image 2 only): {entries}."
    instance_guidance = ""
    if has_instance_id:
        instance_number = 2 + int(has_object_id)
        instance_guidance = (
            f" Image {instance_number} is exact instance-ID metadata only. "
            "Every non-black color denotes one existing authored instance; "
            "preserve each exactly once and never reproduce these colors."
        )
    geometry_guidance = ""
    if control_bundle_version == 2:
        geometry_guidance = (
            f" Images {base_guide_number}, {base_guide_number + 1}, and "
            f"{base_guide_number + 2} are same-camera depth, view-normal, and "
            "source-material ID metadata. Use them to preserve occlusion, surface "
            "orientation, material boundaries, returns, and contacts; never reproduce "
            "their encoded colors."
        )
    edge_guidance = (
        f" Image {structural_guide_number} is the authoritative monochrome structural-edge "
        "guide deterministically extracted from the clean scene and class boundaries. "
        "Every black contour other than its compact B/S/P region labels represents geometry "
        "that must remain in the same location and orientation. Use it as a constraint only; "
        "never draw, tint, or expose its contours or labels in the rendered image."
    )
    component_guidance = ""
    if visible_component_summary:
        component_entries = ", ".join(
            f"{count} visibly disjoint {semantic_class} region" f"{'s' if count != 1 else ''}"
            for semantic_class, count in sorted(visible_component_summary.items())
        )
        component_guidance = (
            f" The class-ID pass contains {component_entries}. Preserve every labeled "
            "region independently; do not merge or bridge them. These are visible 2D "
            "components, not a claim about real-world object count, because occlusion can "
            "split one object into multiple visible regions. The compact B/S/P identifiers "
            "exist only in the guide as metadata and must never appear in the render."
        )
    reference_guidance = ""
    reference_lock = ""
    if archetype_reference_labels:
        reference_entries = "; ".join(
            f"Image {structural_guide_number + 1 + offset}: {label}"
            for offset, label in enumerate(archetype_reference_labels)
        )
        reference_guidance = (
            "\n\nARCHETYPE REFERENCES: "
            + reference_entries
            + ". These are authored design sources, not metadata images."
        )
        reference_lock = (
            " ARCHETYPE IDENTITY LOCK: apply building references strictly to "
            "their named buildings. Use park and street references for material finish only; "
            "capacity and placement are already resolved in Image 1. Their selected material, planting, "
            "surface and furnishing identities override generic style examples."
        )
    authority = (
        "DIRECT 3D GEOMETRY LOCK: Image 1 is the authoritative clean 3D scene. "
        "Preserve its exact camera, projection, framing, horizon, terrain, building "
        "count, silhouettes, footprints, heights, setbacks, rooflines, street and path "
        "alignments, park geometry, tree locations, and all occlusions. Refine only "
        "materials, glazing, foliage realism, lighting, weathering, contact shadows, "
        "and atmospheric polish inside the transparent edit mask. Do not invent, "
        "remove, move, resize, rotate, or recompose any designed element. Preserve all "
        "unmasked context exactly. The result must be a direct stylization of Image 1, "
        "not a redesigned scene."
        + id_guidance
        + instance_guidance
        + geometry_guidance
        + edge_guidance
        + component_guidance
        + reference_lock
    )
    inventory = _server_inventory_prompt(server_inventory)
    # Repeat the non-negotiable lock after user prose so a client prompt cannot
    # weaken the geometry rules through recency or contradictory instructions.
    prompt = (
        f"{authority}{legend}{reference_guidance}\n\n{inventory}\n\nDESIRED VISUAL TREATMENT:\n"
        f"{client_prompt.strip()}\n\n{authority}"
    )
    if len(prompt) > 31_900:
        available = max(
            1,
            31_900 - len(authority) * 2 - len(legend) - len(reference_guidance) - len(inventory) - 44,
        )
        prompt = (
            f"{authority}{legend}{reference_guidance}\n\n{inventory}\n\nDESIRED VISUAL TREATMENT:\n"
            f"{client_prompt.strip()[:available]}\n\n{authority}"
        )
    return prompt


def _server_inventory_prompt(
    server_inventory: list[dict[str, Any]] | None,
) -> str:
    """Summarize server-validated inventory without provider-irrelevant IDs."""

    if not server_inventory:
        return "SERVER-VALIDATED AUTHORED INVENTORY: no separately listed instances."
    counts: dict[str, int] = {}
    for item in server_inventory:
        semantic_class = str(item["semantic_class"])
        counts[semantic_class] = counts.get(semantic_class, 0) + 1
    count_text = ", ".join(f"{semantic_class}={count}" for semantic_class, count in sorted(counts.items()))
    identity_counts: dict[str, int] = {}
    for item in server_inventory:
        identity = item.get("design_identity")
        if isinstance(identity, str) and identity.strip():
            normalized = identity.strip()
            identity_counts[normalized] = identity_counts.get(normalized, 0) + 1
    identity_text = ""
    if identity_counts:
        identity_text = "; design identities: " + ", ".join(
            f"{count}x {identity}" for identity, count in sorted(identity_counts.items())
        )
    return (
        "SERVER-VALIDATED AUTHORED INVENTORY (binding): "
        f"{count_text}{identity_text}; preserve every instance exactly once."
    )


def _masked_correlation(
    template: np.ndarray,
    candidate: np.ndarray,
    mask: np.ndarray,
) -> float:
    active = mask > 0
    if np.count_nonzero(active) < 256:
        raise Direct3DValidationError("Too few immutable context pixels for registration")
    left = template[active].astype(np.float64)
    right = candidate[active].astype(np.float64)
    if np.array_equal(left, right):
        return 1.0
    left -= left.mean()
    right -= right.mean()
    denominator = math.sqrt(float(np.dot(left, left) * np.dot(right, right)))
    if denominator <= 1e-9:
        return 0.0
    return float(np.dot(left, right) / denominator)


def _structural_context_agreement(
    source: Image.Image,
    candidate: Image.Image,
    proposal_mask: Image.Image,
) -> float:
    """Measure bidirectional geometry agreement in immutable context.

    Provider edits commonly relight or rematerialize the surrounding city even
    when the camera and projected geometry are unchanged. Luminance
    correlation is deliberately retained as the primary registration gate,
    while this fallback compares only long, high-confidence edges. Requiring
    agreement in both directions prevents a texture-heavy provider image from
    passing merely because it places some edge near every source contour.
    """

    if source.size != candidate.size or source.size != proposal_mask.size:
        raise Direct3DValidationError("Structural context images and mask must have identical dimensions")

    import cv2

    immutable_context = _registration_context_mask(proposal_mask)
    context_image = Image.fromarray(immutable_context, mode="L")
    active = immutable_context > 0
    source_edges = _beauty_structural_edges(source, context_image) & active
    candidate_edges = _beauty_structural_edges(candidate, context_image) & active
    source_count = int(np.count_nonzero(source_edges))
    candidate_count = int(np.count_nonzero(candidate_edges))
    if source_count < _MIN_STRUCTURAL_CONTEXT_EDGE_PIXELS or candidate_count < _MIN_STRUCTURAL_CONTEXT_EDGE_PIXELS:
        return 0.0

    diagonal = math.hypot(source.width, source.height)
    tolerance_px = max(2, min(4, round(diagonal * 0.002)))
    distance_to_candidate = cv2.distanceTransform(
        (~candidate_edges).astype(np.uint8),
        cv2.DIST_L2,
        3,
    )
    distance_to_source = cv2.distanceTransform(
        (~source_edges).astype(np.uint8),
        cv2.DIST_L2,
        3,
    )
    source_recall = float(np.mean(distance_to_candidate[source_edges] <= tolerance_px))
    candidate_recall = float(np.mean(distance_to_source[candidate_edges] <= tolerance_px))
    return min(source_recall, candidate_recall)


def register_generated_image(
    source: Image.Image,
    generated: Image.Image,
    proposal_mask: Image.Image,
    *,
    enforce_transform_limits: bool = True,
) -> RegistrationResult:
    """Align generated pixels to the clean capture using immutable context.

    Source-anchored callers retain the historical transform limits. Scene
    callers may request the measured transform even when it is large so the
    service can report the drift and select a source-locked safe fallback
    instead of turning a produced provider image into a billed rejection.
    """

    if source.size != generated.size or source.size != proposal_mask.size:
        raise Direct3DValidationError("Registration images and mask must have identical dimensions")

    import cv2

    source_rgb = np.asarray(source.convert("RGB"))
    generated_rgb = np.asarray(generated.convert("RGB"))
    source_gray = cv2.cvtColor(source_rgb, cv2.COLOR_RGB2GRAY).astype(np.float32) / 255.0
    generated_gray = cv2.cvtColor(generated_rgb, cv2.COLOR_RGB2GRAY).astype(np.float32) / 255.0
    context_mask = _registration_context_mask(proposal_mask)
    context_coverage = float(np.count_nonzero(context_mask) / context_mask.size)
    if context_coverage < 0.10:
        raise Direct3DValidationError("At least 10% immutable context is required for registration")

    identity_score = _masked_correlation(source_gray, generated_gray, context_mask)
    if identity_score >= _IDENTITY_SCORE:
        return RegistrationResult(
            image=generated.convert("RGB"),
            method="identity",
            score=identity_score,
            score_metric="luminance-correlation",
            photometric_score=identity_score,
            structural_context_score=None,
            translation_x_px=0.0,
            translation_y_px=0.0,
            rotation_degrees=0.0,
        )

    warp = np.eye(2, 3, dtype=np.float32)
    criteria = (
        cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT,
        120,
        1e-6,
    )
    try:
        _score, warp = cv2.findTransformECC(
            source_gray,
            generated_gray,
            warp,
            cv2.MOTION_EUCLIDEAN,
            criteria,
            inputMask=context_mask,
            gaussFiltSize=5,
        )
    except cv2.error as exc:
        raise Direct3DValidationError("Generated image could not be registered to the 3D capture") from exc

    translation_x = float(warp[0, 2])
    translation_y = float(warp[1, 2])
    rotation_degrees = math.degrees(math.atan2(float(warp[1, 0]), float(warp[0, 0])))
    max_translation = max(12.0, math.hypot(source.width, source.height) * 0.025)
    if enforce_transform_limits and math.hypot(translation_x, translation_y) > max_translation:
        raise Direct3DValidationError("Generated image drift exceeds the Direct 3D translation limit")
    if enforce_transform_limits and abs(rotation_degrees) > _MAX_REGISTRATION_ROTATION_DEGREES:
        raise Direct3DValidationError("Generated image rotation exceeds the Direct 3D limit")

    registered_rgb = cv2.warpAffine(
        generated_rgb,
        warp,
        source.size,
        flags=cv2.INTER_CUBIC | cv2.WARP_INVERSE_MAP,
        borderMode=cv2.BORDER_REFLECT,
    )
    registered_gray = cv2.cvtColor(registered_rgb, cv2.COLOR_RGB2GRAY).astype(np.float32) / 255.0
    registered_score = _masked_correlation(source_gray, registered_gray, context_mask)
    structural_context_score: float | None = None
    score = registered_score
    score_metric = "luminance-correlation"
    if registered_score < _MIN_REGISTRATION_SCORE:
        structural_context_score = _structural_context_agreement(
            source,
            Image.fromarray(registered_rgb, mode="RGB"),
            proposal_mask,
        )
        if structural_context_score >= _MIN_STRUCTURAL_CONTEXT_SCORE:
            score = structural_context_score
            score_metric = "bidirectional-structural-edge-recall"
        else:
            raise Direct3DValidationError(
                "Generated image does not retain enough registered context "
                f"(luminance score {registered_score:.3f}, structural score "
                f"{structural_context_score:.3f})"
            )

    return RegistrationResult(
        image=Image.fromarray(registered_rgb, mode="RGB"),
        method="ecc-euclidean",
        score=score,
        score_metric=score_metric,
        photometric_score=registered_score,
        structural_context_score=structural_context_score,
        translation_x_px=translation_x,
        translation_y_px=translation_y,
        rotation_degrees=rotation_degrees,
    )


def hard_composite_direct_3d(
    source: Image.Image,
    generated: Image.Image,
    proposal_mask: Image.Image,
    *,
    inward_feather_px: float = _INWARD_FEATHER_PX,
) -> tuple[Image.Image, int, int]:
    """Composite generated content inward; never touch mask-zero pixels."""

    if source.size != generated.size or source.size != proposal_mask.size:
        raise Direct3DValidationError("Composite images and mask must have identical dimensions")

    import cv2

    source_array = np.asarray(source.convert("RGB"), dtype=np.uint8)
    generated_array = np.asarray(generated.convert("RGB"), dtype=np.uint8)
    raw_alpha = np.asarray(proposal_mask.convert("L"), dtype=np.float32) / 255.0
    inside = (raw_alpha > 0).astype(np.uint8)
    if inward_feather_px > 0:
        distance = cv2.distanceTransform(inside, cv2.DIST_L2, 3)
        inward = np.clip(distance / inward_feather_px, 0.0, 1.0)
        blend_alpha = np.minimum(raw_alpha, inward)
    else:
        blend_alpha = raw_alpha

    output = np.rint(
        generated_array.astype(np.float32) * blend_alpha[..., None]
        + source_array.astype(np.float32) * (1.0 - blend_alpha[..., None])
    ).astype(np.uint8)
    exterior = raw_alpha == 0
    exterior_count = int(np.count_nonzero(exterior))
    exterior_max_delta = (
        int(np.max(np.abs(output[exterior].astype(np.int16) - source_array[exterior].astype(np.int16))))
        if exterior_count
        else 0
    )
    if exterior_max_delta != 0:
        raise Direct3DValidationError("Hard composite changed immutable exterior pixels")
    return Image.fromarray(output, mode="RGB"), exterior_count, exterior_max_delta


def _macro_diagnostics(
    result: MacroDesignFidelityResult,
    fidelity_policy: Literal["precise", "balanced", "expressive"],
) -> dict[str, Any]:
    thresholds = _macro_fidelity_thresholds(
        fidelity_policy,
        tolerance_px=result.tolerance_px,
    )
    return {
        "passed": result.passed,
        "tolerance_px": result.tolerance_px,
        "silhouette_edge_pixels": result.silhouette_edge_pixels,
        "silhouette_edge_recall": result.silhouette_edge_recall,
        "coarse_edge_pixels": result.coarse_edge_pixels,
        "coarse_edge_recall": result.coarse_edge_recall,
        "semantic_edge_pixels": result.semantic_edge_pixels,
        "semantic_edge_recall": result.semantic_edge_recall,
        "evaluated_component_count": result.evaluated_component_count,
        "semantic_component_min_recall": result.semantic_component_min_recall,
        "reference_edge_p90_distance_px": result.reference_edge_p90_distance_px,
        "candidate_coarse_edge_pixels": result.candidate_coarse_edge_pixels,
        "candidate_coarse_edge_precision": result.candidate_coarse_edge_precision,
        "candidate_coarse_edge_density_ratio": (result.candidate_coarse_edge_density_ratio),
        "minimum_silhouette_edge_recall": (thresholds.minimum_silhouette_edge_recall),
        "minimum_coarse_edge_recall": thresholds.minimum_coarse_edge_recall,
        "minimum_semantic_edge_recall": thresholds.minimum_semantic_edge_recall,
        "minimum_semantic_component_recall": (thresholds.minimum_semantic_component_recall),
        "maximum_reference_edge_p90_distance_px": (thresholds.maximum_reference_p90_distance_px),
        "minimum_candidate_coarse_edge_precision": (thresholds.minimum_candidate_coarse_edge_precision),
        "maximum_candidate_coarse_edge_density_ratio": (thresholds.maximum_candidate_coarse_edge_density_ratio),
        "building_internal_edges_required": False,
    }


def _instance_presence_diagnostics(
    result: InstanceSourcePresenceResult,
) -> dict[str, Any]:
    return {
        "passed": result.passed if result.evaluated_instance_count else None,
        "status": ("passed" if result.passed else "failed") if result.evaluated_instance_count else "not_evaluated",
        "evaluated_instance_count": result.evaluated_instance_count,
        "weakest_instance_recall": result.weakest_instance_recall,
        "missing_instance_ids": list(result.missing_instance_ids),
        "instance_recalls": result.instance_recalls,
    }


def _unsupported_structure_diagnostics(
    result: UnsupportedStructureResult,
) -> dict[str, Any]:
    return {
        "passed": result.passed,
        "largest_component_pixels": result.largest_component_pixels,
        "largest_component_bbox_fraction": result.largest_component_bbox_fraction,
        "proposal_component_count": result.proposal_component_count,
        "context_component_count": result.context_component_count,
    }


def _visual_change_diagnostics(result: VisualChangeResult) -> dict[str, Any]:
    return {
        "passed": True,
        "whole_frame_mean_absolute_delta": (result.whole_frame_mean_absolute_delta),
        "proposal_mean_absolute_delta": result.proposal_mean_absolute_delta,
        "proposal_detail_delta_p75": result.proposal_detail_delta_p75,
        "proposal_photometric_residual_p95": (result.proposal_photometric_residual_p95),
        "novel_detail_edge_coverage": result.novel_detail_edge_coverage,
        "context_mean_absolute_delta": result.context_mean_absolute_delta,
        "context_photometric_residual_p95": (result.context_photometric_residual_p95),
        "context_detail_delta_p75": result.context_detail_delta_p75,
        "context_pixel_count": result.context_pixel_count,
        "context_frame_top_fraction": result.context_frame_top_fraction,
        "minimum_whole_frame_mean_absolute_delta": (_MIN_SCENE_WHOLE_FRAME_MEAN_ABSOLUTE_DELTA),
        "minimum_proposal_mean_absolute_delta": (_MIN_SCENE_PROPOSAL_MEAN_ABSOLUTE_DELTA),
        "minimum_proposal_detail_delta_p75": (_MIN_SCENE_PROPOSAL_DETAIL_DELTA_P75),
        "minimum_proposal_photometric_residual_p95": (_MIN_SCENE_PROPOSAL_PHOTOMETRIC_RESIDUAL_P95),
        "minimum_novel_detail_edge_coverage": (_MIN_SCENE_NOVEL_DETAIL_EDGE_COVERAGE),
        "minimum_context_mean_absolute_delta": (_MIN_SCENE_CONTEXT_MEAN_ABSOLUTE_DELTA),
        "minimum_context_photometric_residual_p95": (_MIN_SCENE_CONTEXT_PHOTOMETRIC_RESIDUAL_P95),
        "minimum_context_detail_delta_p75": (_MIN_SCENE_CONTEXT_DETAIL_DELTA_P75),
        "context_change_required": True,
        "color_grade_only_rejected": True,
    }


def _server_inventory_counts(
    server_inventory: list[dict[str, Any]] | None,
) -> dict[str, int] | None:
    if server_inventory is None:
        return None
    counts: dict[str, int] = {}
    for item in server_inventory:
        semantic_class = str(item["semantic_class"])
        counts[semantic_class] = counts.get(semantic_class, 0) + 1
    return counts


def _source_locked_rlasm_instance_ids(
    server_inventory: list[dict[str, Any]] | None,
) -> tuple[str, ...]:
    return tuple(
        sorted(
            {
                str(item.get("instance_id") or "")
                for item in (server_inventory or [])
                if item.get("source_locked_rlasm") is True and str(item.get("instance_id") or "")
            }
        )
    )


def _restore_source_locked_instances(
    source: Image.Image,
    candidate: Image.Image,
    instance_id_image: Image.Image | None,
    instance_id_manifest: dict[str, Any] | None,
    protected_instance_ids: tuple[str, ...],
) -> tuple[Image.Image, float]:
    """Restore exact source pixels for server-certified RLASM instances."""

    if not protected_instance_ids:
        return candidate.convert("RGB"), 0.0
    if instance_id_image is None or not instance_id_manifest:
        raise Direct3DValidationError("Source-locked RLASM rendering requires the exact instance-ID pass")
    if source.size != candidate.size or source.size != instance_id_image.size:
        raise Direct3DValidationError("Source-locked RLASM source, candidate, and instance-ID images must align")

    protected = set(protected_instance_ids)
    instance_pixels = np.asarray(instance_id_image.convert("RGB"))
    mask = np.zeros(instance_pixels.shape[:2], dtype=bool)
    matched: set[str] = set()
    for color, descriptor in instance_id_manifest.items():
        instance_id = str(getattr(descriptor, "instance_id", "") or "")
        if instance_id not in protected:
            continue
        rgb = tuple(int(color[index : index + 2], 16) for index in (1, 3, 5))
        mask |= np.all(instance_pixels == np.asarray(rgb, dtype=np.uint8), axis=2)
        matched.add(instance_id)
    if matched != protected:
        missing = ", ".join(sorted(protected - matched))
        raise Direct3DValidationError(f"Source-locked RLASM instance mask is missing {missing}")
    if not np.any(mask):
        raise Direct3DValidationError("Source-locked RLASM instance masks contain no pixels")

    source_pixels = np.asarray(source.convert("RGB"))
    candidate_pixels = np.asarray(candidate.convert("RGB")).copy()
    candidate_pixels[mask] = source_pixels[mask]
    return (
        Image.fromarray(candidate_pixels, mode="RGB"),
        float(np.count_nonzero(mask) / mask.size),
    )


def _reproject_sanity_diagnostics(result: ReprojectOutputSanityResult) -> dict[str, Any]:
    return {
        **asdict(result),
        "minimum_whole_frame_mean_absolute_delta": _MIN_REPROJECT_WHOLE_FRAME_MEAN_ABSOLUTE_DELTA,
        "minimum_luminance_standard_deviation": _MIN_REPROJECT_LUMINANCE_STANDARD_DEVIATION,
        "minimum_luminance_dynamic_range_p90": _MIN_REPROJECT_LUMINANCE_DYNAMIC_RANGE_P90,
        "minimum_structural_edge_coverage": _MIN_REPROJECT_STRUCTURAL_EDGE_COVERAGE,
        "maximum_structural_edge_coverage": _MAX_REPROJECT_STRUCTURAL_EDGE_COVERAGE,
        "minimum_occupied_edge_cells": _MIN_REPROJECT_OCCUPIED_EDGE_CELLS,
        "semantic_inventory_proxy_only": True,
    }


def _same_camera_presentation_result(
    req: Direct3DRenderRequest,
    capture: PreparedDirect3DCapture,
    generated: Image.Image,
    common_diagnostics: dict[str, Any],
    source_locked_rlasm_ids: tuple[str, ...],
) -> Direct3DServiceResult:
    """Measure a same-camera finish and preserve source-owned context/occlusion.

    These image checks detect drift; they are not proof of three-dimensional
    identity. Never demand visibility from fully occluded inventory entries.
    """
    diagnostics = dict(common_diagnostics)
    warnings = []
    try:
        registration = register_generated_image(
            capture.normalized_beauty,
            generated,
            capture.normalized_proposal_mask,
        )
        diagnostics["registration"] = {
            field.name: getattr(registration, field.name) for field in fields(registration) if field.name != "image"
        }
        raw_presence = assess_instance_source_presence(
            capture.normalized_beauty, registration.image, capture.normalized_proposal_mask,
            capture.normalized_instance_id, req.instance_id_manifest, fidelity_policy=req.fidelity_policy,
        )
        diagnostics["provider_raw_instance_source_presence"] = _instance_presence_diagnostics(raw_presence)
        presentation, exterior_count, exterior_delta = hard_composite_direct_3d(
            capture.normalized_beauty, registration.image, capture.normalized_proposal_mask,
        )
        diagnostics.update(exterior_pixel_count=exterior_count, exterior_max_channel_delta=exterior_delta)
        protected_coverage = 0.0
        if source_locked_rlasm_ids:
            presentation, protected_coverage = _restore_source_locked_instances(
                capture.normalized_beauty, presentation, capture.normalized_instance_id,
                req.instance_id_manifest, source_locked_rlasm_ids,
            )
        macro = assess_macro_design_fidelity(
            capture.normalized_beauty, presentation, capture.normalized_proposal_mask,
            capture.normalized_object_id, req.object_id_manifest, fidelity_policy=req.fidelity_policy,
        )
        presence = assess_instance_source_presence(
            capture.normalized_beauty, presentation, capture.normalized_proposal_mask,
            capture.normalized_instance_id, req.instance_id_manifest, fidelity_policy=req.fidelity_policy,
        )
        unsupported = assess_unsupported_coarse_structure(
            capture.normalized_beauty, presentation, capture.normalized_proposal_mask,
            capture.normalized_instance_id, req.instance_id_manifest,
            detect_slender_additions=True,
        )
        diagnostics.update(
            macro_design_fidelity=_macro_diagnostics(macro, req.fidelity_policy),
            instance_source_presence=_instance_presence_diagnostics(presence),
            unsupported_structure=_unsupported_structure_diagnostics(unsupported),
        )
        failures = []
        if not macro.passed:
            failures.append("source silhouette/layout agreement was insufficient")
        if not presence.passed:
            failures.append("visible source instances lost structural evidence")
        if not unsupported.passed:
            failures.append("new unsupported structure was detected")
        if failures:
            raise Direct3DValidationError("; ".join(failures))
        strategy = "provider_full_scene_rlasm_pixel_lock" if source_locked_rlasm_ids else "provider_full_scene_local_repairs"
        diagnostics.update(
            view_lock="camera_registered", context_restyled=False, provider_first=True,
            provider_spatial_pixels_retained=True, returned_safety_strategy=strategy,
            source_locked_rlasm_pixel_lock_applied=bool(source_locked_rlasm_ids),
            source_locked_rlasm_pixel_coverage=protected_coverage,
        )
        warnings.append(
            "AI finish passed the available image checks. Source context and foreground occlusions "
            "outside the visible proposal remain unchanged; review building heights, footprints "
            "and public realm against the clean 3D source. These checks do not certify exact geometry."
        )
        if presence.evaluated_instance_count == 0:
            warnings.append("No visible instance had enough edge evidence for an individual check; hidden objects remain hidden.")
    except Direct3DValidationError as exc:
        presentation = capture.normalized_beauty.convert("RGB")
        diagnostics.update(
            view_lock="source_pixel_locked", context_restyled=False, provider_first=False,
            provider_spatial_pixels_retained=False, returned_safety_strategy="authoritative_source",
            source_locked_rlasm_pixel_lock_applied=bool(source_locked_rlasm_ids),
            source_locked_rlasm_pixel_coverage=1.0 if source_locked_rlasm_ids else None,
        )
        warnings.append(
            "Clean 3D source returned because the AI finish could not be verified: "
            f"{exc}. The provider original is retained separately for review."
        )
    output_png = _png_bytes(presentation)
    return Direct3DServiceResult(
        image_base64=base64.b64encode(output_png).decode("ascii"),
        audit_input_base64=capture.audit_input_base64,
        capture_fingerprint=capture.capture_fingerprint,
        output_fingerprint=hashlib.sha256(output_png).hexdigest(),
        outcome="review_required", warnings=tuple(warnings), diagnostics=diagnostics,
        provider_image_base64=base64.b64encode(_png_bytes(generated)).decode("ascii"),
    )


class Direct3DRenderService:
    def __init__(self, api_key: str):
        self.api_key = api_key

    async def _call_openai(
        self,
        req: Direct3DRenderRequest,
        capture: PreparedDirect3DCapture,
        *,
        server_inventory: list[dict[str, Any]] | None = None,
    ) -> Image.Image:
        if not self.api_key:
            raise Direct3DProviderError(
                "OpenAI is not configured",
                billing_status="unproduced",
            )

        normalized_width, normalized_height = capture.normalized_beauty.size
        beauty_png = _png_bytes(capture.normalized_beauty.convert("RGB"))
        structural_guide_png = _png_bytes(
            build_structural_edge_guide(
                capture.normalized_beauty,
                capture.normalized_proposal_mask,
                capture.normalized_object_id,
                req.object_id_manifest,
            )
        )
        visible_component_summary, _component_labels = _visible_semantic_components(
            capture.normalized_object_id,
            req.object_id_manifest,
        )
        files: list[tuple[str, tuple[str, bytes, str]]] = [
            ("image[]", ("direct-3d-beauty.png", beauty_png, "image/png")),
        ]
        if capture.normalized_object_id is not None:
            files.append(
                (
                    "image[]",
                    ("direct-3d-class-id.png", _png_bytes(capture.normalized_object_id), "image/png"),
                )
            )
        if capture.normalized_instance_id is not None:
            files.append(
                (
                    "image[]",
                    (
                        "direct-3d-instance-id.png",
                        _png_bytes(capture.normalized_instance_id),
                        "image/png",
                    ),
                )
            )
        if req.control_bundle_version == 2:
            geometry_controls = (
                ("direct-3d-depth.png", capture.normalized_depth),
                ("direct-3d-normal.png", capture.normalized_normal),
                ("direct-3d-material-id.png", capture.normalized_material_id),
            )
            for filename, image in geometry_controls:
                if image is None:
                    raise Direct3DValidationError(f"Control bundle v2 is missing prepared {filename}")
                files.append(("image[]", (filename, _png_bytes(image), "image/png")))
        files.append(
            (
                "image[]",
                ("direct-3d-structural-edges.png", structural_guide_png, "image/png"),
            )
        )
        # Authored archetype artwork rides after the metadata passes so the
        # prompt's ARCHETYPE REFERENCES numbering lines up with attachment
        # order. These are design sources the provider applies, not metadata.
        for reference_index, reference in enumerate(req.archetype_references):
            try:
                reference_bytes = base64.b64decode(reference.image_base64.split(",", 1)[-1])
            except (ValueError, binascii.Error) as exc:
                raise Direct3DValidationError(f"Archetype reference {reference_index + 1} is not valid base64") from exc
            is_png = reference_bytes[:8] == b"\x89PNG\r\n\x1a\n"
            files.append(
                (
                    "image[]",
                    (
                        f"archetype-ref-{reference_index + 1}.{'png' if is_png else 'jpg'}",
                        reference_bytes,
                        "image/png" if is_png else "image/jpeg",
                    ),
                )
            )
        if req.presentation_mode == "source_anchored":
            edit_mask_png = _png_bytes(build_openai_edit_mask(capture.normalized_proposal_mask))
            files.append(
                (
                    "mask",
                    ("direct-3d-edit-mask.png", edit_mask_png, "image/png"),
                )
            )
        prompt = (
            _authoritative_prompt(
                req.prompt,
                object_id_manifest=req.object_id_manifest,
                instance_id_manifest=req.instance_id_manifest,
                server_inventory=server_inventory,
                visible_component_summary=visible_component_summary,
                archetype_reference_labels=[reference.label for reference in req.archetype_references],
                control_bundle_version=req.control_bundle_version,
            )
            if req.presentation_mode == "source_anchored"
            else _presentation_prompt(
                req.prompt,
                presentation_mode=req.presentation_mode,
                style=req.style,
                object_id_manifest=req.object_id_manifest,
                instance_id_manifest=req.instance_id_manifest,
                server_inventory=server_inventory,
                visible_component_summary=visible_component_summary,
                view_mode=req.view_mode,
                archetype_reference_labels=[reference.label for reference in req.archetype_references],
                control_bundle_version=req.control_bundle_version,
            )
        )
        data = {
            "model": DIRECT_3D_MODEL,
            "prompt": prompt,
            "n": "1",
            "size": f"{normalized_width}x{normalized_height}",
            "quality": "high",
            "output_format": "png",
        }
        headers = {"Authorization": f"Bearer {self.api_key}"}
        attachment_inventory = [
            {
                "field": field_name,
                "filename": file_value[0],
                "bytes": len(file_value[1]),
            }
            for field_name, file_value in files
        ]
        logger.info(
            "Direct 3D edit request: model=%s mode=%s style=%s fidelity=%s size=%s coverage=%.3f object_id=%s instance_id=%s fingerprint=%s attachments=%s total_attachment_bytes=%d",
            DIRECT_3D_MODEL,
            req.presentation_mode,
            req.style,
            req.fidelity_policy,
            data["size"],
            capture.proposal_coverage,
            capture.normalized_object_id is not None,
            capture.normalized_instance_id is not None,
            capture.capture_fingerprint[:16],
            attachment_inventory,
            sum(item["bytes"] for item in attachment_inventory),
        )

        # Exactly one provider call. Legacy source-anchored mode includes its
        # strict edit mask; provider-first presentation modes deliberately omit
        # it. No mode retries with a different mask contract.
        try:
            async with httpx.AsyncClient(timeout=300.0) as client:
                response = await client.post(
                    _OPENAI_EDIT_URL,
                    data=data,
                    files=files,
                    headers=headers,
                )
        except (httpx.ConnectError, httpx.ConnectTimeout, httpx.PoolTimeout) as exc:
            # These failures happen before a response body or generated image
            # can exist, so releasing the reservation is safe.
            raise Direct3DProviderError(
                f"OpenAI Direct 3D connection failed before generation: {exc}",
                billing_status="unproduced",
            ) from exc
        except httpx.HTTPError as exc:
            # Read/write/protocol failures can occur after the upload reached
            # OpenAI. Billing cannot be inferred from the missing response.
            logger.warning(
                "OpenAI Direct 3D transport failure after submission: type=%s repr=%r",
                type(exc).__name__,
                exc,
            )
            raise Direct3DProviderError(
                "OpenAI Direct 3D request outcome is unknown: " f"{type(exc).__name__}: {exc!r}",
                billing_status="unknown",
            ) from exc
        if response.status_code != 200:
            body = response.text[:500]
            logger.error("Direct 3D OpenAI edit returned %d: %s", response.status_code, body)
            billing_status = "unproduced" if response.status_code in _KNOWN_UNBILLED_PROVIDER_STATUSES else "unknown"
            raise Direct3DProviderError(
                f"OpenAI Direct 3D error ({response.status_code}): {body}",
                billing_status=billing_status,
            )

        try:
            response_data = response.json().get("data") or []
            image_b64 = response_data[0].get("b64_json") if response_data else None
        except (AttributeError, IndexError, TypeError, ValueError) as exc:
            raise Direct3DProviderError(
                "OpenAI Direct 3D response was malformed",
                billing_status="unknown",
            ) from exc
        if not image_b64:
            response_has_image_reference = bool(
                response_data and isinstance(response_data[0], dict) and response_data[0].get("url")
            )
            raise Direct3DProviderError(
                "OpenAI Direct 3D response did not contain b64_json",
                billing_status="produced" if response_has_image_reference else "unknown",
            )

        canonical_generated_b64: str | None = None
        try:
            generated_raw = _decode_base64_payload(image_b64, label="OpenAI Direct 3D output")
            generated = _load_image(
                generated_raw,
                label="OpenAI Direct 3D output",
                allowed_formats={"PNG"},
            ).convert("RGB")
            canonical_generated_b64 = base64.b64encode(_png_bytes(generated)).decode("ascii")
            if generated.size != capture.normalized_beauty.size:
                raise Direct3DValidationError(
                    "OpenAI Direct 3D output dimensions do not match the explicit normalized size"
                )
        except Exception as exc:
            raise Direct3DProviderError(
                f"OpenAI produced an unusable Direct 3D image: {exc}",
                billing_status="produced",
                provider_image_base64=canonical_generated_b64,
            ) from exc
        return generated

    async def generate(
        self,
        req: Direct3DRenderRequest,
        capture: PreparedDirect3DCapture | None = None,
        *,
        server_inventory: list[dict[str, Any]] | None = None,
    ) -> Direct3DServiceResult:
        capture = capture or prepare_direct_3d_capture(req)
        generated = await self._call_openai(
            req,
            capture,
            server_inventory=server_inventory,
        )
        provider_image_base64: str | None = None
        try:
            provider_image_base64 = base64.b64encode(_png_bytes(generated)).decode("ascii")
            common_diagnostics: dict[str, Any] = {
                "control_bundle_version": req.control_bundle_version,
                "processing_mode": req.presentation_mode,
                "fidelity_policy": req.fidelity_policy,
                "source_width": capture.source_beauty.width,
                "source_height": capture.source_beauty.height,
                "normalized_width": capture.normalized_beauty.width,
                "normalized_height": capture.normalized_beauty.height,
                "proposal_coverage": capture.proposal_coverage,
                "context_coverage": 1.0 - capture.proposal_coverage,
                "object_id_attached": capture.normalized_object_id is not None,
                "object_id_coverage": capture.object_id_coverage,
                "object_id_proposal_recall": capture.object_id_proposal_recall,
                "object_id_proposal_iou": capture.object_id_proposal_iou,
                "minimum_object_id_proposal_recall": (
                    _MIN_PRESENTATION_OBJECT_ID_PROPOSAL_RECALL
                    if req.presentation_mode in {"scene", "reproject"}
                    else None
                ),
                "minimum_object_id_proposal_iou": (
                    _MIN_PRESENTATION_OBJECT_ID_PROPOSAL_IOU
                    if req.presentation_mode in {"scene", "reproject"}
                    else None
                ),
                "instance_id_attached": (capture.normalized_instance_id is not None),
                "instance_count": capture.instance_count,
                "depth_attached": capture.normalized_depth is not None,
                "normal_attached": capture.normalized_normal is not None,
                "material_id_attached": capture.normalized_material_id is not None,
                "material_count": capture.material_count,
                "camera_attached": req.camera is not None,
                "instance_source_presence": None,
                "unsupported_structure": None,
                "server_inventory": _server_inventory_counts(server_inventory),
                "source_locked_rlasm_instance_count": len(_source_locked_rlasm_instance_ids(server_inventory)),
                "source_locked_rlasm_pixel_lock_applied": False,
                "source_locked_rlasm_pixel_coverage": None,
                "scene_lower_context_coverage": (capture.scene_lower_context_coverage),
                "minimum_scene_lower_context_coverage": (
                    _MIN_SCENE_LOWER_CONTEXT_COVERAGE if req.presentation_mode == "scene" else None
                ),
                "structural_edge_guide_attached": True,
                "finish_fusion": None,
                "provider_raw_structural_edge_fidelity": None,
                "macro_design_fidelity": None,
                "visual_change": None,
                "reproject_output_sanity": None,
                "structural_edge_fidelity": None,
                "registration": None,
                "exterior_pixel_count": None,
                "exterior_max_channel_delta": None,
                "inward_feather_px": None,
                "mask_retry_used": False,
            }
            source_locked_rlasm_ids = _source_locked_rlasm_instance_ids(server_inventory)

            if req.view_mode == "street":
                # The input was already captured at eye level. Finishing it
                # must not change cameras or expose hidden facilities. Use
                # the same registered, masked, source-preserving checks as
                # any other same-camera image, rather than content sanity
                # alone. Sparse street evidence safely falls back to source.
                street_result = _same_camera_presentation_result(
                    req, capture, generated, common_diagnostics, source_locked_rlasm_ids,
                )
                street_result.diagnostics["view_mode"] = "street"
                return street_result

            if DIRECT_3D_PRESENTATION_FIRST and req.presentation_mode == "scene":
                return _same_camera_presentation_result(
                    req, capture, generated, common_diagnostics, source_locked_rlasm_ids,
                )

            if DIRECT_3D_PRESENTATION_FIRST and req.presentation_mode == "reproject":
                sanity = assess_reproject_output_sanity(
                    capture.normalized_beauty, generated, capture.normalized_object_id, req.object_id_manifest,
                )
                presentation = generated if sanity.passed else capture.normalized_beauty
                output_png = _png_bytes(presentation)
                warning = (
                    "Projection-changing output cannot be registered to the original capture. "
                    "Review the source inventory, heights, footprints and occlusions; exact identity is not verified."
                    if sanity.passed else
                    "Clean 3D source returned because the provider output failed minimum image-content checks. "
                    "This retains the source camera, not the requested new projection. The provider original is retained for review."
                )
                return Direct3DServiceResult(
                    image_base64=base64.b64encode(output_png).decode("ascii"),
                    audit_input_base64=capture.audit_input_base64,
                    capture_fingerprint=capture.capture_fingerprint,
                    output_fingerprint=hashlib.sha256(output_png).hexdigest(),
                    outcome="review_required", provider_image_base64=provider_image_base64,
                    warnings=(warning,),
                    diagnostics={
                        **common_diagnostics,
                        "view_lock": "not_applicable_layout_guided" if sanity.passed else "source_pixel_locked",
                        "context_restyled": sanity.passed,
                        "provider_first": sanity.passed,
                        "provider_spatial_pixels_retained": sanity.passed,
                        "returned_safety_strategy": "provider_full_scene" if sanity.passed else "authoritative_source",
                        "reproject_output_sanity": _reproject_sanity_diagnostics(sanity),
                    },
                )

            if req.presentation_mode == "reproject":
                reproject_sanity = assess_reproject_output_sanity(
                    capture.normalized_beauty,
                    generated,
                    capture.normalized_object_id,
                    req.object_id_manifest,
                )
                if not reproject_sanity.passed:
                    raise Direct3DValidationError(
                        "Provider reproject output failed minimum content sanity "
                        f"(whole-frame MAD "
                        f"{reproject_sanity.whole_frame_mean_absolute_delta:.3f}, "
                        "luminance std "
                        f"{reproject_sanity.luminance_standard_deviation:.3f}, "
                        "luminance P90 range "
                        f"{reproject_sanity.luminance_dynamic_range_p90:.3f}, "
                        "edge coverage "
                        f"{reproject_sanity.structural_edge_coverage:.5f}, "
                        "occupied cells "
                        f"{reproject_sanity.occupied_edge_cells}, components "
                        f"{reproject_sanity.significant_edge_component_count}/"
                        f"{reproject_sanity.required_edge_component_count})"
                    )
                output_png = _png_bytes(generated)
                return Direct3DServiceResult(
                    image_base64=base64.b64encode(output_png).decode("ascii"),
                    audit_input_base64=capture.audit_input_base64,
                    capture_fingerprint=capture.capture_fingerprint,
                    output_fingerprint=hashlib.sha256(output_png).hexdigest(),
                    outcome="review_required",
                    provider_image_base64=provider_image_base64,
                    warnings=(
                        "Projection-changing Direct 3D renders require human review " "against the source inventory.",
                    ),
                    diagnostics={
                        **common_diagnostics,
                        "view_lock": "not_applicable_layout_guided",
                        "context_restyled": True,
                        "provider_first": True,
                        "reproject_output_sanity": {
                            "passed": True,
                            "whole_frame_mean_absolute_delta": (reproject_sanity.whole_frame_mean_absolute_delta),
                            "luminance_standard_deviation": (reproject_sanity.luminance_standard_deviation),
                            "luminance_dynamic_range_p90": (reproject_sanity.luminance_dynamic_range_p90),
                            "structural_edge_coverage": (reproject_sanity.structural_edge_coverage),
                            "occupied_edge_cells": (reproject_sanity.occupied_edge_cells),
                            "significant_edge_component_count": (reproject_sanity.significant_edge_component_count),
                            "required_edge_component_count": (reproject_sanity.required_edge_component_count),
                            "minimum_whole_frame_mean_absolute_delta": (_MIN_REPROJECT_WHOLE_FRAME_MEAN_ABSOLUTE_DELTA),
                            "minimum_luminance_standard_deviation": (_MIN_REPROJECT_LUMINANCE_STANDARD_DEVIATION),
                            "minimum_luminance_dynamic_range_p90": (_MIN_REPROJECT_LUMINANCE_DYNAMIC_RANGE_P90),
                            "minimum_structural_edge_coverage": (_MIN_REPROJECT_STRUCTURAL_EDGE_COVERAGE),
                            "maximum_structural_edge_coverage": (_MAX_REPROJECT_STRUCTURAL_EDGE_COVERAGE),
                            "minimum_occupied_edge_cells": (_MIN_REPROJECT_OCCUPIED_EDGE_CELLS),
                            "semantic_inventory_proxy_only": True,
                        },
                    },
                )

            registration: RegistrationResult | None = None
            scene_registration_error: str | None = None
            if req.presentation_mode == "scene":
                try:
                    registration = register_generated_image(
                        capture.normalized_beauty,
                        generated,
                        capture.normalized_proposal_mask,
                        enforce_transform_limits=False,
                    )
                except Direct3DValidationError as exc:
                    # A provider image already exists. Failed or unreliable
                    # screen registration therefore selects the non-spatial
                    # source-locked fallback below rather than becoming a
                    # billed rejection. The original error is retained in the
                    # human-review warning; diagnostics report registration as
                    # unavailable instead of inventing an identity transform.
                    scene_registration_error = str(exc)
                    logger.warning(
                        "Direct 3D scene registration was unreliable; using " "source-locked fallback: %s",
                        exc,
                    )
            else:
                registration = register_generated_image(
                    capture.normalized_beauty,
                    generated,
                    capture.normalized_proposal_mask,
                )

            provider_analysis_image = registration.image if registration is not None else generated
            scene_translation_norm_px = (
                math.hypot(
                    registration.translation_x_px,
                    registration.translation_y_px,
                )
                if registration is not None
                else None
            )
            scene_review_translation_px: float | None = None
            scene_review_rotation_degrees: float | None = None
            scene_drift_requires_review = False
            scene_drift_requires_source_lock = False
            if req.presentation_mode == "scene":
                (
                    scene_review_translation_px,
                    scene_review_rotation_degrees,
                ) = _SCENE_REGISTRATION_REVIEW_LIMITS[req.fidelity_policy]
                (
                    source_lock_translation_px,
                    source_lock_rotation_degrees,
                ) = _SCENE_REGISTRATION_SOURCE_LOCK_LIMITS[req.fidelity_policy]
                scene_drift_requires_review = (
                    registration is None
                    or scene_translation_norm_px is None
                    or scene_translation_norm_px > scene_review_translation_px
                    or abs(registration.rotation_degrees) > scene_review_rotation_degrees
                )
                scene_drift_requires_source_lock = (
                    registration is None
                    or scene_translation_norm_px is None
                    or scene_translation_norm_px > source_lock_translation_px
                    or abs(registration.rotation_degrees) > source_lock_rotation_degrees
                )
            provider_edge_fidelity = assess_structural_edge_fidelity(
                capture.normalized_beauty,
                provider_analysis_image,
                capture.normalized_proposal_mask,
                capture.normalized_object_id,
                req.object_id_manifest,
            )
            provider_edge_diagnostics = {
                "passed": provider_edge_fidelity.passed,
                "beauty_edge_recall": provider_edge_fidelity.beauty_edge_recall,
                "coarse_edge_recall": provider_edge_fidelity.coarse_edge_recall,
                "semantic_edge_recall": provider_edge_fidelity.semantic_edge_recall,
                "semantic_component_min_recall": (provider_edge_fidelity.semantic_component_min_recall),
                "building_internal_edge_recall": (provider_edge_fidelity.building_internal_edge_recall),
            }

            if req.presentation_mode == "scene":
                macro_fidelity = assess_macro_design_fidelity(
                    capture.normalized_beauty,
                    provider_analysis_image,
                    capture.normalized_proposal_mask,
                    capture.normalized_object_id,
                    req.object_id_manifest,
                    fidelity_policy=req.fidelity_policy,
                )
                instance_presence = assess_instance_source_presence(
                    capture.normalized_beauty,
                    provider_analysis_image,
                    capture.normalized_proposal_mask,
                    capture.normalized_instance_id,
                    req.instance_id_manifest,
                    fidelity_policy=req.fidelity_policy,
                )
                unsupported_structure = assess_unsupported_coarse_structure(
                    capture.normalized_beauty,
                    provider_analysis_image,
                    capture.normalized_proposal_mask,
                    capture.normalized_instance_id,
                    req.instance_id_manifest,
                )
                severe_macro_redesign = (
                    (macro_fidelity.silhouette_edge_recall is not None and macro_fidelity.silhouette_edge_recall < 0.55)
                    or macro_fidelity.coarse_edge_recall < 0.55
                    or (macro_fidelity.semantic_edge_recall is not None and macro_fidelity.semantic_edge_recall < 0.60)
                    or (
                        macro_fidelity.semantic_component_min_recall is not None
                        and macro_fidelity.semantic_component_min_recall < 0.55
                    )
                )
                provider_quality_warnings: list[str] = []
                provider_quality_requires_source_lock = False
                if req.fidelity_policy == "precise" and severe_macro_redesign and not scene_drift_requires_source_lock:
                    provider_quality_requires_source_lock = True
                    provider_quality_warnings.append(
                        "The provider materially changed macro design geometry under "
                        "the precise policy; the returned image uses only source-owned "
                        "spatial pixels."
                    )
                visual_change = assess_scene_visual_change(
                    capture.normalized_beauty,
                    provider_analysis_image,
                    capture.normalized_proposal_mask,
                )
                if not visual_change.passed and not scene_drift_requires_source_lock:
                    provider_quality_requires_source_lock = True
                    provider_quality_warnings.append(
                        "The provider result was too close to a colour grade to prove "
                        "a useful spatial finish; the returned image uses only "
                        "source-owned spatial pixels."
                    )

                # Dense noise can satisfy directed source recall by chance and
                # is not useful even as a review candidate.
                if not scene_drift_requires_source_lock and (
                    macro_fidelity.candidate_coarse_edge_precision < 0.18
                    or macro_fidelity.candidate_coarse_edge_density_ratio > 5.5
                ):
                    provider_quality_requires_source_lock = True
                    provider_quality_warnings.append(
                        "The provider produced an invalid coarse edge field; the "
                        "returned image uses only source-owned spatial pixels."
                    )

                scene_source_lock_required = scene_drift_requires_source_lock or provider_quality_requires_source_lock

                outcome: Literal["accepted", "review_required"] = "accepted"
                warnings: list[str] = list(provider_quality_warnings)
                if capture.normalized_instance_id is None or not req.instance_id_manifest:
                    raise Direct3DValidationError("Scene output requires exact instance inventory")

                def assess_returned_scene(
                    candidate: Image.Image,
                ) -> tuple[
                    InstanceSourcePresenceResult,
                    UnsupportedStructureResult,
                ]:
                    return (
                        assess_instance_source_presence(
                            capture.normalized_beauty,
                            candidate,
                            capture.normalized_proposal_mask,
                            capture.normalized_instance_id,
                            req.instance_id_manifest,
                            fidelity_policy=req.fidelity_policy,
                        ),
                        assess_unsupported_coarse_structure(
                            capture.normalized_beauty,
                            candidate,
                            capture.normalized_proposal_mask,
                            capture.normalized_instance_id,
                            req.instance_id_manifest,
                        ),
                    )

                missing_instance_ids = set(instance_presence.missing_instance_ids)
                local_repair_coverage: float | None = None
                local_repair_exceeded_limit = False
                if scene_source_lock_required:
                    # Gross or unreliable camera drift makes every local
                    # provider pixel spatially untrustworthy. Retain only
                    # provider-derived whole-frame colour statistics; the
                    # returned topology remains entirely source-owned.
                    safety_strategy = "global_tone_only"
                    presentation_normalized = _source_locked_scene_fallback(
                        capture.normalized_beauty,
                        generated,
                        capture.normalized_instance_id,
                        req.instance_id_manifest,
                        missing_instance_ids,
                        admit_building_interiors=False,
                    )
                    safe_presence, safe_unsupported = assess_returned_scene(presentation_normalized)
                else:
                    # Keep the registered full-frame AI finish whenever the
                    # authoritative inventory gates accept it. If the provider
                    # added a structure or weakened an authored instance,
                    # restore only those bounded regions from source phase so
                    # the surrounding Google Tiles treatment and public-realm
                    # finish survive.
                    presentation_normalized = provider_analysis_image.convert("RGB").copy()
                    safety_strategy = "provider_full_scene"
                    safe_presence, safe_unsupported = assess_returned_scene(presentation_normalized)
                    if not safe_presence.passed or not safe_unsupported.passed:
                        (
                            presentation_normalized,
                            _source_phase,
                            local_repair_coverage,
                        ) = _locally_repair_scene_candidate(
                            capture.normalized_beauty,
                            presentation_normalized,
                            capture.normalized_proposal_mask,
                            capture.normalized_object_id,
                            req.object_id_manifest,
                            capture.normalized_instance_id,
                            req.instance_id_manifest,
                            set(safe_presence.missing_instance_ids),
                        )
                        safety_strategy = "provider_full_scene_local_repairs"
                        safe_presence, safe_unsupported = assess_returned_scene(presentation_normalized)
                        local_repair_exceeded_limit = local_repair_coverage > _MAX_SCENE_LOCAL_REPAIR_COVERAGE
                    if not local_repair_exceeded_limit and (not safe_presence.passed or not safe_unsupported.passed):
                        (
                            presentation_normalized,
                            _source_phase,
                            second_repair_coverage,
                        ) = _locally_repair_scene_candidate(
                            capture.normalized_beauty,
                            presentation_normalized,
                            capture.normalized_proposal_mask,
                            capture.normalized_object_id,
                            req.object_id_manifest,
                            capture.normalized_instance_id,
                            req.instance_id_manifest,
                            set(safe_presence.missing_instance_ids),
                        )
                        local_repair_coverage = min(
                            1.0,
                            (local_repair_coverage or 0.0) + second_repair_coverage,
                        )
                        local_repair_exceeded_limit = local_repair_coverage > _MAX_SCENE_LOCAL_REPAIR_COVERAGE
                        safe_presence, safe_unsupported = assess_returned_scene(presentation_normalized)
                    if local_repair_exceeded_limit or not safe_presence.passed or not safe_unsupported.passed:
                        presentation_normalized, _source_phase = _balanced_scene_hybrid(
                            capture.normalized_beauty,
                            provider_analysis_image,
                            capture.normalized_object_id,
                            req.object_id_manifest,
                            capture.normalized_instance_id,
                            req.instance_id_manifest,
                            missing_instance_ids,
                        )
                        safety_strategy = "source_envelope_building_interiors"
                        safe_presence, safe_unsupported = assess_returned_scene(presentation_normalized)
                    if not safe_presence.passed or not safe_unsupported.passed:
                        safety_strategy = "global_tone_with_safe_building_interiors"
                        presentation_normalized = _source_locked_scene_fallback(
                            capture.normalized_beauty,
                            provider_analysis_image,
                            capture.normalized_instance_id,
                            req.instance_id_manifest,
                            missing_instance_ids,
                            admit_building_interiors=True,
                        )
                        safe_presence, safe_unsupported = assess_returned_scene(presentation_normalized)

                if not safe_presence.passed or not safe_unsupported.passed:
                    safety_strategy = "global_tone_only"
                    presentation_normalized = _source_locked_scene_fallback(
                        capture.normalized_beauty,
                        generated,
                        capture.normalized_instance_id,
                        req.instance_id_manifest,
                        missing_instance_ids,
                        admit_building_interiors=False,
                    )
                    safe_presence, safe_unsupported = assess_returned_scene(presentation_normalized)

                if not safe_presence.passed or not safe_unsupported.passed:
                    # The exact authoritative capture is the deterministic last
                    # resort after a paid provider response. It prevents both an
                    # unsafe return and an avoidable post-generation hard block.
                    safety_strategy = "authoritative_source"
                    presentation_normalized = capture.normalized_beauty.convert("RGB").copy()
                    safe_presence, safe_unsupported = assess_returned_scene(presentation_normalized)

                if not safe_presence.passed or not safe_unsupported.passed:
                    raise Direct3DValidationError(
                        "Authoritative source fallback could not produce a safe, "
                        "inventory-preserving result "
                        f"(instance presence={safe_presence.passed}, "
                        f"unsupported structure={safe_unsupported.passed}, "
                        "weakest instance recall="
                        f"{safe_presence.weakest_instance_recall}, "
                        "unsupported components="
                        f"{safe_unsupported.proposal_component_count + safe_unsupported.context_component_count})"
                    )

                if scene_registration_error is not None:
                    warnings.append(
                        "Provider scene registration was unreliable "
                        f"({scene_registration_error}); the returned image is "
                        "source-locked and contains no provider spatial pixels."
                    )
                elif scene_drift_requires_source_lock:
                    warnings.append(
                        "Provider scene camera drift was too large for safe local "
                        "pixel transfer "
                        f"({scene_translation_norm_px:.2f}px translation, "
                        f"{abs(registration.rotation_degrees):.3f} degree rotation); "
                        "the returned image is source-locked and contains no "
                        "provider spatial pixels."
                    )
                elif scene_drift_requires_review:
                    warnings.append(
                        "Provider scene camera drift exceeded the "
                        f"{req.fidelity_policy} automatic threshold "
                        f"({scene_translation_norm_px:.2f}px translation versus "
                        f"{scene_review_translation_px:.2f}px, "
                        f"{abs(registration.rotation_degrees):.3f} degree rotation "
                        f"versus {scene_review_rotation_degrees:.3f}); review the "
                        "source/candidate comparison before saving."
                    )

                if req.fidelity_policy == "balanced":
                    if not macro_fidelity.passed:
                        warnings.append(
                            "The provider varied macro geometry beyond the balanced "
                            "automatic threshold; the inventory-safe returned image "
                            "requires source/candidate review."
                        )
                    if not instance_presence.passed:
                        warnings.append(
                            "One or more authored instances were weak in the provider "
                            "image and were restored from source geometry."
                        )
                    if not unsupported_structure.passed:
                        warnings.append(
                            "Unsupported coarse structures were detected in the provider "
                            "image and repaired against the authoritative source before "
                            "the final inventory gate."
                        )
                    if warnings:
                        outcome = "review_required"
                elif req.fidelity_policy == "precise":
                    if not instance_presence.passed:
                        warnings.append(
                            "One or more authored instances were weak in the provider "
                            "image and were restored from source geometry."
                        )
                    if not unsupported_structure.passed:
                        warnings.append(
                            "Unsupported coarse structures were detected in the provider "
                            "image and repaired against the authoritative source before "
                            "the final inventory gate."
                        )
                    if not macro_fidelity.passed:
                        warnings.append(
                            "The render exceeded precise macro-geometry tolerances; "
                            "compare it with the source before approval."
                        )
                    if warnings:
                        outcome = "review_required"
                else:
                    outcome = "review_required"
                    warnings.append(
                        "Expressive Direct 3D renders require human review against "
                        "the source and exact instance inventory."
                    )
                    if not macro_fidelity.passed:
                        warnings.append("The expressive render materially reinterpreted source edges.")
                    if not instance_presence.passed:
                        warnings.append("At least one authored instance has weak source-presence evidence.")
                    if not unsupported_structure.passed:
                        warnings.append(
                            "Unsupported coarse structures were repaired against the "
                            "authoritative source before the final inventory gate."
                        )

                if safety_strategy not in {
                    "provider_full_scene",
                    "provider_full_scene_local_repairs",
                }:
                    outcome = "review_required"
                    if not scene_source_lock_required:
                        warnings.append(
                            "Bounded provider repair did not pass the authoritative "
                            "inventory gate, so the returned image uses the "
                            f"safer {safety_strategy.replace('_', ' ')} fallback."
                        )

                returned_visual_change = assess_scene_visual_change(
                    capture.normalized_beauty,
                    presentation_normalized,
                    capture.normalized_proposal_mask,
                )
                provider_spatial_pixels_retained = safety_strategy in {
                    "provider_full_scene",
                    "provider_full_scene_local_repairs",
                }
                if provider_spatial_pixels_retained and not returned_visual_change.passed:
                    outcome = "review_required"
                    warnings.append(
                        "The inventory-safe returned image did not retain enough "
                        "full-scene spatial enhancement for automatic acceptance; "
                        "review it against the source before saving."
                    )

                presentation = presentation_normalized.resize(
                    capture.source_beauty.size,
                    Image.Resampling.LANCZOS,
                )
                source_pixels = np.asarray(capture.source_beauty.convert("RGB"))
                output_pixels = np.asarray(presentation.convert("RGB"))
                exterior = np.asarray(capture.source_proposal_mask.convert("L")) == 0
                exterior_count = int(np.count_nonzero(exterior))
                exterior_max_delta = (
                    int(
                        np.max(
                            np.abs(output_pixels[exterior].astype(np.int16) - source_pixels[exterior].astype(np.int16))
                        )
                    )
                    if exterior_count
                    else 0
                )
                returned_source_pixel_locked = safety_strategy in {
                    "global_tone_only",
                    "authoritative_source",
                }
                registration_diagnostics = (
                    {
                        "method": registration.method,
                        "score": registration.score,
                        "score_metric": registration.score_metric,
                        "photometric_score": registration.photometric_score,
                        "structural_context_score": (registration.structural_context_score),
                        "translation_x_px": registration.translation_x_px,
                        "translation_y_px": registration.translation_y_px,
                        "translation_norm_px": scene_translation_norm_px,
                        "rotation_degrees": registration.rotation_degrees,
                        "maximum_translation_norm_px": (scene_review_translation_px),
                        "maximum_abs_rotation_degrees": (scene_review_rotation_degrees),
                    }
                    if registration is not None
                    else None
                )
                visual_change_diagnostics = (
                    _visual_change_diagnostics(returned_visual_change) if returned_visual_change.passed else None
                )
                output_png = _png_bytes(presentation)
                return Direct3DServiceResult(
                    image_base64=base64.b64encode(output_png).decode("ascii"),
                    audit_input_base64=capture.audit_input_base64,
                    capture_fingerprint=capture.capture_fingerprint,
                    output_fingerprint=hashlib.sha256(output_png).hexdigest(),
                    outcome=outcome,
                    provider_image_base64=provider_image_base64,
                    warnings=tuple(warnings),
                    diagnostics={
                        **common_diagnostics,
                        "view_lock": ("source_pixel_locked" if returned_source_pixel_locked else "camera_registered"),
                        "context_restyled": (provider_spatial_pixels_retained and returned_visual_change.passed),
                        "provider_first": provider_spatial_pixels_retained,
                        "provider_spatial_pixels_retained": (provider_spatial_pixels_retained),
                        "provider_raw_structural_edge_fidelity": provider_edge_diagnostics,
                        "provider_raw_instance_source_presence": (_instance_presence_diagnostics(instance_presence)),
                        "provider_raw_unsupported_structure": (
                            _unsupported_structure_diagnostics(unsupported_structure)
                        ),
                        "returned_safety_strategy": safety_strategy,
                        "local_repair_coverage": local_repair_coverage,
                        "maximum_local_repair_coverage": (_MAX_SCENE_LOCAL_REPAIR_COVERAGE),
                        "macro_design_fidelity": _macro_diagnostics(
                            macro_fidelity,
                            req.fidelity_policy,
                        ),
                        "instance_source_presence": (_instance_presence_diagnostics(safe_presence)),
                        "unsupported_structure": (_unsupported_structure_diagnostics(safe_unsupported)),
                        "visual_change": visual_change_diagnostics,
                        "registration": registration_diagnostics,
                        "exterior_pixel_count": exterior_count,
                        "exterior_max_channel_delta": exterior_max_delta,
                        "inward_feather_px": 0.0,
                    },
                )

            finish_fusion = _fuse_source_geometry_with_provider_finish(
                capture.normalized_beauty,
                registration.image,
                capture.normalized_proposal_mask,
                capture.normalized_object_id,
                req.object_id_manifest,
            )
            fused = finish_fusion.image
            edge_fidelity = assess_structural_edge_fidelity(
                capture.normalized_beauty,
                fused,
                capture.normalized_proposal_mask,
                capture.normalized_object_id,
                req.object_id_manifest,
            )
            if not edge_fidelity.passed:
                semantic_detail = (
                    f", semantic recall {edge_fidelity.semantic_edge_recall:.3f}"
                    if edge_fidelity.semantic_edge_recall is not None
                    else ""
                )
                component_detail = (
                    ", weakest object recall " f"{edge_fidelity.semantic_component_min_recall:.3f}"
                    if edge_fidelity.semantic_component_min_recall is not None
                    else ""
                )
                building_detail = (
                    ", building-internal recall " f"{edge_fidelity.building_internal_edge_recall:.3f}"
                    if edge_fidelity.building_internal_edge_recall is not None
                    else ""
                )
                raise Direct3DValidationError(
                    "Generated image materially redesigned internal geometry "
                    f"(beauty-edge recall {edge_fidelity.beauty_edge_recall:.3f}"
                    f", coarse-edge recall {edge_fidelity.coarse_edge_recall:.3f}"
                    f"{semantic_detail}{component_detail}{building_detail})"
                )
            registered_source_size = fused.resize(
                capture.source_beauty.size,
                Image.Resampling.LANCZOS,
            )
            composited, exterior_count, exterior_max_delta = hard_composite_direct_3d(
                capture.source_beauty,
                registered_source_size,
                capture.source_proposal_mask,
            )
            output_png = _png_bytes(composited)
            output_fingerprint = hashlib.sha256(output_png).hexdigest()
            return Direct3DServiceResult(
                image_base64=base64.b64encode(output_png).decode("ascii"),
                audit_input_base64=capture.audit_input_base64,
                capture_fingerprint=capture.capture_fingerprint,
                output_fingerprint=output_fingerprint,
                provider_image_base64=provider_image_base64,
                diagnostics={
                    "processing_mode": "source_anchored",
                    "fidelity_policy": req.fidelity_policy,
                    "view_lock": "source_pixel_locked",
                    "context_restyled": False,
                    "provider_first": False,
                    "source_width": capture.source_beauty.width,
                    "source_height": capture.source_beauty.height,
                    "normalized_width": capture.normalized_beauty.width,
                    "normalized_height": capture.normalized_beauty.height,
                    "proposal_coverage": capture.proposal_coverage,
                    "context_coverage": 1.0 - capture.proposal_coverage,
                    "object_id_attached": capture.normalized_object_id is not None,
                    "object_id_coverage": capture.object_id_coverage,
                    "object_id_proposal_recall": (capture.object_id_proposal_recall),
                    "object_id_proposal_iou": capture.object_id_proposal_iou,
                    "minimum_object_id_proposal_recall": None,
                    "minimum_object_id_proposal_iou": None,
                    "instance_id_attached": (capture.normalized_instance_id is not None),
                    "instance_count": capture.instance_count,
                    "instance_source_presence": None,
                    "unsupported_structure": None,
                    "server_inventory": _server_inventory_counts(server_inventory),
                    "scene_lower_context_coverage": None,
                    "minimum_scene_lower_context_coverage": None,
                    "structural_edge_guide_attached": True,
                    "finish_fusion": {
                        "method": "source-geometry-multiscale-source-phase-detail-v2",
                        "sigma_px": _finish_fusion_sigma(
                            capture.normalized_beauty.width,
                            capture.normalized_beauty.height,
                        ),
                        "rgb_delta_clip": _FINISH_FUSION_RGB_DELTA_CLIP,
                        "default_strength": _FINISH_FUSION_DEFAULT_STRENGTH,
                        "role_strengths": dict(_FINISH_FUSION_ROLE_STRENGTHS),
                        "detail_fine_sigma_px": max(
                            0.5,
                            _FINISH_DETAIL_FINE_SIGMA_AT_REFERENCE_PX
                            * _finish_detail_scale(
                                capture.normalized_beauty.width,
                                capture.normalized_beauty.height,
                            ),
                        ),
                        "detail_medium_sigma_px": max(
                            1.75,
                            _FINISH_DETAIL_MEDIUM_SIGMA_AT_REFERENCE_PX
                            * _finish_detail_scale(
                                capture.normalized_beauty.width,
                                capture.normalized_beauty.height,
                            ),
                        ),
                        "detail_correction_clip": _FINISH_DETAIL_CORRECTION_CLIP,
                        "detail_role_gain_caps": {
                            semantic_class: {
                                "fine": gain_caps[0],
                                "medium": gain_caps[1],
                            }
                            for semantic_class, gain_caps in sorted(_FINISH_DETAIL_ROLE_GAIN_CAPS.items())
                        },
                        "microtexture_sigma_px": max(
                            0.4,
                            _FINISH_MICROTEXTURE_SIGMA_AT_REFERENCE_PX
                            * _finish_detail_scale(
                                capture.normalized_beauty.width,
                                capture.normalized_beauty.height,
                            ),
                        ),
                        "microtexture_correction_clip": (_FINISH_MICROTEXTURE_CORRECTION_CLIP),
                        "microtexture_role_gain_caps": dict(_FINISH_MICROTEXTURE_ROLE_GAIN_CAPS),
                        "provider_high_frequency_phase_transferred": False,
                        **finish_fusion.diagnostics,
                    },
                    "provider_raw_structural_edge_fidelity": provider_edge_diagnostics,
                    "structural_edge_fidelity": {
                        "passed": edge_fidelity.passed,
                        "tolerance_px": edge_fidelity.tolerance_px,
                        "reference_edge_pixels": edge_fidelity.reference_edge_pixels,
                        "candidate_edge_pixels": edge_fidelity.candidate_edge_pixels,
                        "beauty_edge_recall": edge_fidelity.beauty_edge_recall,
                        "coarse_edge_pixels": edge_fidelity.coarse_edge_pixels,
                        "coarse_edge_recall": edge_fidelity.coarse_edge_recall,
                        "semantic_edge_pixels": edge_fidelity.semantic_edge_pixels,
                        "semantic_edge_recall": edge_fidelity.semantic_edge_recall,
                        "semantic_component_min_recall": (edge_fidelity.semantic_component_min_recall),
                        "building_internal_edge_pixels": (edge_fidelity.building_internal_edge_pixels),
                        "building_internal_edge_recall": (edge_fidelity.building_internal_edge_recall),
                        "reference_edge_p90_distance_px": (edge_fidelity.reference_edge_p90_distance_px),
                    },
                    "registration": {
                        "method": registration.method,
                        "score": registration.score,
                        "score_metric": registration.score_metric,
                        "photometric_score": registration.photometric_score,
                        "structural_context_score": (registration.structural_context_score),
                        "translation_x_px": registration.translation_x_px,
                        "translation_y_px": registration.translation_y_px,
                        "rotation_degrees": registration.rotation_degrees,
                    },
                    "exterior_pixel_count": exterior_count,
                    "exterior_max_channel_delta": exterior_max_delta,
                    "inward_feather_px": _INWARD_FEATHER_PX,
                    "mask_retry_used": False,
                },
            )
        except Exception as exc:
            # Once a valid provider image has been returned, every registration,
            # compositing, encoding, or diagnostic failure remains billable.
            raise Direct3DProviderError(
                f"Generated Direct 3D image failed post-processing safety checks: {exc}",
                billing_status="produced",
                provider_image_base64=provider_image_base64,
            ) from exc
