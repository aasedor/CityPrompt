"""Schemas for the isolated Direct 3D image-refinement pipeline.

This contract intentionally does not inherit from the colored-polygon render
request.  Direct 3D starts from an authoritative viewport capture and always
requires an explicit proposal mask.
"""

from __future__ import annotations

import re
import uuid
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator


Direct3DSemanticClass = Literal["ground", "landscape", "street", "park", "building"]


class Direct3DCaptureClaim(BaseModel):
    """Optional client measurements which the server verifies against pixels."""

    width: int = Field(..., ge=1, le=2048)
    height: int = Field(..., ge=1, le=2048)
    proposal_coverage: float = Field(..., ge=0.0, le=1.0)
    fingerprint: str | None = Field(default=None, pattern=r"^[a-fA-F0-9]{64}$")


class Direct3DResidualLandscapeClaim(BaseModel):
    """Version claim tying a paid capture to the server-current compiled parcel."""

    boundary_id: uuid.UUID
    source_hash: str = Field(..., pattern=r"^[a-fA-F0-9]{64}$")


class Direct3DCommunityZoneClaim(BaseModel):
    """Exact compiled zone/model identity observed by the captured browser scene."""

    zone_id: uuid.UUID
    source_hash: str = Field(..., pattern=r"^[a-fA-F0-9]{64}$")
    representation_hash: str = Field(..., pattern=r"^[a-fA-F0-9]{64}$")
    building_id: uuid.UUID | None = None


class Direct3DRenderRequest(BaseModel):
    """A clean 3D capture and exact mask to refine without moving geometry."""

    beauty_image_base64: str = Field(
        ...,
        min_length=32,
        max_length=40_000_000,
        description="Base64 PNG/JPEG/WebP clean 3D viewport capture.",
    )
    proposal_mask_base64: str = Field(
        ...,
        min_length=32,
        max_length=20_000_000,
        description=(
            "Same-size PNG proposal mask. Zero/black is immutable context; "
            "255/white is proposal area. An RGBA alpha channel is also accepted."
        ),
    )
    prompt: str = Field(..., min_length=1, max_length=20_000)
    object_id_image_base64: str | None = Field(
        default=None,
        min_length=32,
        max_length=20_000_000,
        description="Optional same-size class-ID PNG used only as a structural guide.",
    )
    object_id_manifest: dict[str, Direct3DSemanticClass] | None = Field(
        default=None,
        description="Map from #RRGGBB class-ID colors to Direct 3D semantic classes.",
    )
    capture: Direct3DCaptureClaim | None = None
    # Direct 3D is explicitly project-bound: omitting this identifier would
    # bypass the locked source/boundary/model freshness checks before spend.
    project_id: uuid.UUID
    community_3d_claims: list[Direct3DCommunityZoneClaim] = Field(
        ...,
        min_length=1,
        max_length=2000,
    )
    residual_landscape_claim: Direct3DResidualLandscapeClaim | None = None

    @field_validator("object_id_manifest")
    @classmethod
    def validate_object_id_manifest(
        cls,
        manifest: dict[str, Direct3DSemanticClass] | None,
    ) -> dict[str, Direct3DSemanticClass] | None:
        if manifest is None:
            return None
        if not 1 <= len(manifest) <= 64:
            raise ValueError("object_id_manifest must contain between 1 and 64 colors")

        normalized: dict[str, Direct3DSemanticClass] = {}
        for color, semantic_class in manifest.items():
            if not re.fullmatch(r"#[0-9a-fA-F]{6}", color):
                raise ValueError(f"Invalid object-ID color {color!r}; expected #RRGGBB")
            normalized[color.upper()] = semantic_class
        if "#000000" in normalized:
            raise ValueError("#000000 is reserved for non-proposal context")
        return normalized

    @model_validator(mode="after")
    def validate_object_id_pair(self) -> "Direct3DRenderRequest":
        if bool(self.object_id_image_base64) != bool(self.object_id_manifest):
            raise ValueError(
                "object_id_image_base64 and object_id_manifest must be supplied together"
            )
        zone_ids = [claim.zone_id for claim in self.community_3d_claims]
        if len(zone_ids) != len(set(zone_ids)):
            raise ValueError("community_3d_claims may contain each zone only once")
        return self


class Direct3DRegistrationDiagnostics(BaseModel):
    method: Literal["identity", "ecc-euclidean"]
    score: float
    score_metric: Literal[
        "luminance-correlation",
        "bidirectional-structural-edge-recall",
    ] = "luminance-correlation"
    photometric_score: float | None = None
    structural_context_score: float | None = None
    translation_x_px: float
    translation_y_px: float
    rotation_degrees: float


class Direct3DStructuralEdgeFidelityDiagnostics(BaseModel):
    passed: Literal[True]
    tolerance_px: int
    reference_edge_pixels: int
    candidate_edge_pixels: int
    beauty_edge_recall: float
    coarse_edge_pixels: int
    coarse_edge_recall: float
    semantic_edge_pixels: int
    semantic_edge_recall: float | None = None
    semantic_component_min_recall: float | None = None
    building_internal_edge_pixels: int
    building_internal_edge_recall: float | None = None
    reference_edge_p90_distance_px: float


class Direct3DRawStructuralEdgeFidelityDiagnostics(BaseModel):
    """Geometry diagnostics for the untrusted provider image before fusion."""

    passed: bool
    beauty_edge_recall: float
    coarse_edge_recall: float
    semantic_edge_recall: float | None = None
    semantic_component_min_recall: float | None = None
    building_internal_edge_recall: float | None = None


class Direct3DFinishDetailGainCaps(BaseModel):
    """Maximum source-owned contrast gain for one semantic role."""

    fine: float
    medium: float


class Direct3DFinishRoleMetrics(BaseModel):
    """Auditable source-phase detail measurements for one proposal role."""

    detail_fine_gain: float
    detail_medium_gain: float
    microtexture_gain: float
    safe_microtexture_pixels: int
    safe_microtexture_coverage: float
    source_texture_p75: float | None = None
    fused_texture_p75: float | None = None
    texture_gain: float | None = None
    source_detail_correlation: float | None = None


class Direct3DFinishFusionDiagnostics(BaseModel):
    """Finish transfer settings applied while source geometry stays authoritative."""

    method: Literal["source-geometry-multiscale-source-phase-detail-v2"]
    sigma_px: float
    rgb_delta_clip: float
    default_strength: float
    role_strengths: dict[str, float]
    detail_fine_sigma_px: float
    detail_medium_sigma_px: float
    detail_correction_clip: float
    detail_role_gain_caps: dict[str, Direct3DFinishDetailGainCaps]
    microtexture_sigma_px: float
    microtexture_correction_clip: float
    microtexture_role_gain_caps: dict[str, float]
    provider_high_frequency_phase_transferred: Literal[False]
    safe_microtexture_coverage: float
    source_detail_correlation: float | None = None
    source_texture_p75: float | None = None
    fused_texture_p75: float | None = None
    texture_gain: float | None = None
    role_metrics: dict[str, Direct3DFinishRoleMetrics]


class Direct3DRenderDiagnostics(BaseModel):
    source_width: int
    source_height: int
    normalized_width: int
    normalized_height: int
    proposal_coverage: float
    context_coverage: float
    object_id_attached: bool
    object_id_coverage: float | None = None
    structural_edge_guide_attached: Literal[True] = True
    finish_fusion: Direct3DFinishFusionDiagnostics | None = None
    provider_raw_structural_edge_fidelity: (
        Direct3DRawStructuralEdgeFidelityDiagnostics | None
    ) = None
    structural_edge_fidelity: Direct3DStructuralEdgeFidelityDiagnostics | None = None
    registration: Direct3DRegistrationDiagnostics
    exterior_pixel_count: int
    exterior_max_channel_delta: int
    inward_feather_px: float
    mask_retry_used: Literal[False] = False


class Direct3DRenderResponse(BaseModel):
    image_base64: str
    model: Literal["gpt-image-2"] = "gpt-image-2"
    capture_fingerprint: str
    output_fingerprint: str
    diagnostics: Direct3DRenderDiagnostics
