"""Schemas for the isolated Direct 3D image-refinement pipeline.

This contract intentionally does not inherit from the colored-polygon render
request. Direct 3D starts from an authoritative viewport capture and always
requires an explicit proposal mask for validation and design QA, even when a
provider-first presentation mode deliberately omits that mask from generation.
"""

from __future__ import annotations

import math
import re
import uuid
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator


Direct3DSemanticClass = Literal["ground", "landscape", "street", "park", "building"]
Direct3DPresentationMode = Literal["source_anchored", "scene", "reproject"]
Direct3DFidelityPolicy = Literal["precise", "balanced", "expressive"]
Direct3DRenderOutcome = Literal["accepted", "review_required"]
Direct3DStyle = Literal[
    "photorealistic",
    "photomontage",
    "development",
    "atmospheric",
    "winter",
    "night",
    "watercolour",
    "charcoal",
    "marker-render",
    "pen-and-ink",
    "survey",
    "documentary",
    "site-plan",
    "site-plan-photo",
    "blueprint",
    "site-plan-watercolor",
    "isometric",
    "clay-maquette",
    "woodblock",
    "collage",
    "risograph",
    "pixel-art",
]


DIRECT_3D_REPROJECT_STYLES = frozenset(
    {
        "site-plan",
        "site-plan-photo",
        "blueprint",
        "site-plan-watercolor",
        "isometric",
        "clay-maquette",
    }
)


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


class Direct3DInstanceDescriptor(BaseModel):
    """One exact, server-bindable authored instance in the capture pass."""

    instance_id: str = Field(
        ...,
        min_length=1,
        max_length=180,
        pattern=r"^[A-Za-z0-9][A-Za-z0-9._:-]*$",
    )
    semantic_class: Direct3DSemanticClass
    zone_id: uuid.UUID | None = None
    building_id: uuid.UUID | None = None
    source_zone_ids: list[uuid.UUID] = Field(default_factory=list, max_length=2000)

    @field_validator("source_zone_ids")
    @classmethod
    def validate_unique_source_zone_ids(
        cls,
        source_zone_ids: list[uuid.UUID],
    ) -> list[uuid.UUID]:
        if len(source_zone_ids) != len(set(source_zone_ids)):
            raise ValueError("source_zone_ids may contain each zone only once")
        return source_zone_ids


class Direct3DMaterialDescriptor(BaseModel):
    """One capture-local source material represented by an exact ID color."""

    material_id: str = Field(
        ...,
        min_length=1,
        max_length=180,
        pattern=r"^[A-Za-z0-9][A-Za-z0-9._:-]*$",
    )
    label: str = Field(..., min_length=1, max_length=180)
    semantic_class: Direct3DSemanticClass
    material_family_id: str | None = Field(default=None, min_length=1, max_length=180)
    source_specific: bool = False


class Direct3DCameraManifest(BaseModel):
    """Exact renderer camera used by every v2 control pass."""

    projection: Literal["perspective", "orthographic", "other"]
    projection_matrix: list[float] = Field(..., min_length=16, max_length=16)
    matrix_world: list[float] = Field(..., min_length=16, max_length=16)
    position: tuple[float, float, float]
    quaternion: tuple[float, float, float, float]
    near: float | None = Field(default=None, gt=0)
    far: float | None = Field(default=None, gt=0)
    fov: float | None = Field(default=None, gt=0, lt=180)
    aspect: float | None = Field(default=None, gt=0)
    zoom: float | None = Field(default=None, gt=0)

    @model_validator(mode="after")
    def validate_finite_camera(self) -> "Direct3DCameraManifest":
        values = [
            *self.projection_matrix,
            *self.matrix_world,
            *self.position,
            *self.quaternion,
            *(value for value in (self.near, self.far, self.fov, self.aspect, self.zoom) if value is not None),
        ]
        if not all(math.isfinite(value) for value in values):
            raise ValueError("camera values must be finite")
        if self.near is not None and self.far is not None and self.far <= self.near:
            raise ValueError("camera far must be greater than near")
        return self


class Direct3DArchetypeReference(BaseModel):
    """Authored archetype artwork attached to the provider call.

    Unlike the metadata passes (class/instance/structure), these images are
    design sources: the prompt instructs the provider to apply each
    reference's materials and facade character to its named building.
    """

    image_base64: str = Field(min_length=1)
    label: str = Field(min_length=1, max_length=600)


class Direct3DRenderRequest(BaseModel):
    """A clean 3D capture plus mode-specific presentation and design authority."""

    control_bundle_version: Literal[1, 2] = Field(
        default=1,
        description=(
            "Version 2 supplies same-camera depth, normal, material-ID, and camera controls. "
            "Version 1 remains accepted for saved legacy requests."
        ),
    )
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
    presentation_mode: Direct3DPresentationMode = Field(
        default="source_anchored",
        description=(
            "source_anchored preserves the legacy pixel-locked finish; scene "
            "permits a camera-locked full-frame presentation finish; reproject "
            "permits a style-directed plan or axonometric camera transform."
        ),
    )
    archetype_references: list[Direct3DArchetypeReference] = Field(
        default_factory=list,
        max_length=8,
        description=(
            "Authored archetype artwork (facade elevation sheets, catalogue "
            "cards) attached after the metadata passes. Each label names the "
            "building the reference styles and is quoted in the prompt."
        ),
    )
    view_mode: Literal["aerial", "street"] = Field(
        default="aerial",
        description=(
            "Camera family of the capture. 'aerial' (default) keeps every "
            "historical behavior. 'street' marks an eye-level capture: the "
            "aerial lower-frame-context gate is skipped, the prompt asserts a "
            "pedestrian standpoint, and the outcome is always review_required "
            "in this first version. Street requires presentation_mode='scene'."
        ),
    )
    style: Direct3DStyle = Field(
        default="photorealistic",
        description="The render panel style identifier governing the presentation treatment.",
    )
    object_id_image_base64: str | None = Field(
        default=None,
        min_length=32,
        max_length=20_000_000,
        description=(
            "Same-size class-ID PNG used only as a structural guide. Optional "
            "for legacy source_anchored; required for scene and reproject."
        ),
    )
    object_id_manifest: dict[str, Direct3DSemanticClass] | None = Field(
        default=None,
        description=(
            "Map from #RRGGBB class-ID colors to Direct 3D semantic classes; "
            "required with the class-ID PNG for scene and reproject."
        ),
    )
    instance_id_image_base64: str | None = Field(
        default=None,
        min_length=32,
        max_length=20_000_000,
        description=(
            "Same-size exact instance-ID PNG. Optional for legacy " "source_anchored; required for scene and reproject."
        ),
    )
    instance_id_manifest: dict[str, Direct3DInstanceDescriptor] | None = Field(
        default=None,
        description=(
            "Map from #RRGGBB instance colors to exact authored instance, " "semantic, zone, and building identities."
        ),
    )
    depth_image_base64: str | None = Field(default=None, min_length=32, max_length=20_000_000)
    normal_image_base64: str | None = Field(default=None, min_length=32, max_length=20_000_000)
    material_id_image_base64: str | None = Field(default=None, min_length=32, max_length=20_000_000)
    material_id_manifest: dict[str, Direct3DMaterialDescriptor] | None = Field(
        default=None,
        description="Map from exact material-ID colors to capture-local source materials.",
    )
    camera: Direct3DCameraManifest | None = None
    fidelity_policy: Direct3DFidelityPolicy = Field(
        default="balanced",
        description=(
            "Geometry/render trade-off. Precise retains the historical strict "
            "gate; balanced permits bounded artistic edge variation; expressive "
            "always requires human review."
        ),
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

    @field_validator("instance_id_manifest")
    @classmethod
    def validate_instance_id_manifest(
        cls,
        manifest: dict[str, Direct3DInstanceDescriptor] | None,
    ) -> dict[str, Direct3DInstanceDescriptor] | None:
        if manifest is None:
            return None
        if not 1 <= len(manifest) <= 2048:
            raise ValueError("instance_id_manifest must contain between 1 and 2048 colors")

        normalized: dict[str, Direct3DInstanceDescriptor] = {}
        instance_ids: set[str] = set()
        for color, descriptor in manifest.items():
            if not re.fullmatch(r"#[0-9a-fA-F]{6}", color):
                raise ValueError(f"Invalid instance-ID color {color!r}; expected #RRGGBB")
            normalized_color = color.upper()
            if normalized_color == "#000000":
                raise ValueError("#000000 is reserved for non-instance pixels")
            if normalized_color in normalized:
                raise ValueError(f"Duplicate instance-ID color {normalized_color}")
            if descriptor.instance_id in instance_ids:
                raise ValueError("instance_id_manifest may contain each instance_id only once")
            normalized[normalized_color] = descriptor
            instance_ids.add(descriptor.instance_id)
        return normalized

    @field_validator("material_id_manifest")
    @classmethod
    def validate_material_id_manifest(
        cls,
        manifest: dict[str, Direct3DMaterialDescriptor] | None,
    ) -> dict[str, Direct3DMaterialDescriptor] | None:
        if manifest is None:
            return None
        if not 1 <= len(manifest) <= 2048:
            raise ValueError("material_id_manifest must contain between 1 and 2048 colors")
        normalized: dict[str, Direct3DMaterialDescriptor] = {}
        material_ids: set[str] = set()
        for color, descriptor in manifest.items():
            if not re.fullmatch(r"#[0-9a-fA-F]{6}", color):
                raise ValueError(f"Invalid material-ID color {color!r}; expected #RRGGBB")
            normalized_color = color.upper()
            if normalized_color == "#000000":
                raise ValueError("#000000 is reserved for non-material pixels")
            if normalized_color in normalized:
                raise ValueError(f"Duplicate material-ID color {normalized_color}")
            if descriptor.material_id in material_ids:
                raise ValueError("material_id_manifest may contain each material_id only once")
            normalized[normalized_color] = descriptor
            material_ids.add(descriptor.material_id)
        return normalized

    @model_validator(mode="after")
    def validate_object_id_pair(self) -> "Direct3DRenderRequest":
        if self.view_mode == "street" and self.presentation_mode != "scene":
            raise ValueError("view_mode='street' requires presentation_mode='scene'")
        if bool(self.object_id_image_base64) != bool(self.object_id_manifest):
            raise ValueError("object_id_image_base64 and object_id_manifest must be supplied together")
        if self.presentation_mode in {"scene", "reproject"} and not self.object_id_image_base64:
            raise ValueError("scene and reproject require object_id_image_base64 and " "object_id_manifest")
        if bool(self.instance_id_image_base64) != bool(self.instance_id_manifest):
            raise ValueError("instance_id_image_base64 and instance_id_manifest must be " "supplied together")
        if self.presentation_mode in {"scene", "reproject"} and not self.instance_id_image_base64:
            raise ValueError("scene and reproject require instance_id_image_base64 and " "instance_id_manifest")
        if bool(self.material_id_image_base64) != bool(self.material_id_manifest):
            raise ValueError("material_id_image_base64 and material_id_manifest must be supplied together")
        if self.control_bundle_version == 2:
            missing = [
                name
                for name, value in (
                    ("depth_image_base64", self.depth_image_base64),
                    ("normal_image_base64", self.normal_image_base64),
                    ("material_id_image_base64", self.material_id_image_base64),
                    ("material_id_manifest", self.material_id_manifest),
                    ("camera", self.camera),
                )
                if value is None
            ]
            if missing:
                raise ValueError("control_bundle_version=2 requires " + ", ".join(missing))
        zone_ids = [claim.zone_id for claim in self.community_3d_claims]
        if len(zone_ids) != len(set(zone_ids)):
            raise ValueError("community_3d_claims may contain each zone only once")
        is_reproject_style = self.style in DIRECT_3D_REPROJECT_STYLES
        if self.presentation_mode == "scene" and is_reproject_style:
            raise ValueError(f"style {self.style!r} requires presentation_mode='reproject'")
        if self.presentation_mode == "reproject" and not is_reproject_style:
            raise ValueError(f"style {self.style!r} requires presentation_mode='scene' or " "'source_anchored'")
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
    translation_norm_px: float | None = None
    rotation_degrees: float
    maximum_translation_norm_px: float | None = None
    maximum_abs_rotation_degrees: float | None = None


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


class Direct3DMacroDesignFidelityDiagnostics(BaseModel):
    """Primary design-geometry checks for provider-first scene finishes."""

    passed: bool
    tolerance_px: int
    silhouette_edge_pixels: int
    silhouette_edge_recall: float | None = None
    coarse_edge_pixels: int
    coarse_edge_recall: float
    semantic_edge_pixels: int
    semantic_edge_recall: float | None = None
    evaluated_component_count: int
    semantic_component_min_recall: float | None = None
    reference_edge_p90_distance_px: float
    candidate_coarse_edge_pixels: int | None = None
    candidate_coarse_edge_precision: float | None = None
    candidate_coarse_edge_density_ratio: float | None = None
    minimum_silhouette_edge_recall: float | None = None
    minimum_coarse_edge_recall: float | None = None
    minimum_semantic_edge_recall: float | None = None
    minimum_semantic_component_recall: float | None = None
    maximum_reference_edge_p90_distance_px: float | None = None
    minimum_candidate_coarse_edge_precision: float | None = None
    maximum_candidate_coarse_edge_density_ratio: float | None = None
    building_internal_edges_required: Literal[False] = False


class Direct3DVisualChangeDiagnostics(BaseModel):
    """Evidence that a scene finish is more than a near-identity colour grade."""

    passed: Literal[True]
    whole_frame_mean_absolute_delta: float
    proposal_mean_absolute_delta: float
    proposal_detail_delta_p75: float
    proposal_photometric_residual_p95: float
    novel_detail_edge_coverage: float
    context_mean_absolute_delta: float | None = None
    context_photometric_residual_p95: float | None = None
    context_detail_delta_p75: float | None = None
    context_pixel_count: int | None = None
    context_frame_top_fraction: float | None = None
    minimum_whole_frame_mean_absolute_delta: float | None = None
    minimum_proposal_mean_absolute_delta: float
    minimum_proposal_detail_delta_p75: float
    minimum_proposal_photometric_residual_p95: float
    minimum_novel_detail_edge_coverage: float
    minimum_context_mean_absolute_delta: float | None = None
    minimum_context_photometric_residual_p95: float | None = None
    minimum_context_detail_delta_p75: float | None = None
    context_change_required: Literal[True] = True
    color_grade_only_rejected: Literal[True] = True


class Direct3DReprojectOutputSanityDiagnostics(BaseModel):
    """Minimum non-empty/content evidence for projection-changing output."""

    passed: Literal[True]
    whole_frame_mean_absolute_delta: float
    luminance_standard_deviation: float
    luminance_dynamic_range_p90: float
    structural_edge_coverage: float
    occupied_edge_cells: int
    significant_edge_component_count: int
    required_edge_component_count: int
    minimum_whole_frame_mean_absolute_delta: float
    minimum_luminance_standard_deviation: float
    minimum_luminance_dynamic_range_p90: float
    minimum_structural_edge_coverage: float
    maximum_structural_edge_coverage: float
    minimum_occupied_edge_cells: int
    semantic_inventory_proxy_only: Literal[True] = True


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
    control_bundle_version: Literal[1, 2] = 1
    processing_mode: Direct3DPresentationMode = "source_anchored"
    view_lock: Literal[
        "source_pixel_locked",
        "camera_registered",
        "not_applicable_layout_guided",
    ] = "source_pixel_locked"
    context_restyled: bool = False
    provider_first: bool = False
    provider_spatial_pixels_retained: bool = False
    fidelity_policy: Direct3DFidelityPolicy = "balanced"
    source_width: int
    source_height: int
    normalized_width: int
    normalized_height: int
    proposal_coverage: float
    context_coverage: float
    object_id_attached: bool
    object_id_coverage: float | None = None
    object_id_proposal_recall: float | None = None
    object_id_proposal_iou: float | None = None
    minimum_object_id_proposal_recall: float | None = None
    minimum_object_id_proposal_iou: float | None = None
    instance_id_attached: bool = False
    instance_count: int = 0
    depth_attached: bool = False
    normal_attached: bool = False
    material_id_attached: bool = False
    material_count: int = 0
    camera_attached: bool = False
    provider_raw_instance_source_presence: dict[str, object] | None = None
    provider_raw_unsupported_structure: dict[str, object] | None = None
    returned_safety_strategy: (
        Literal[
            "source_envelope",
            "source_envelope_all_authored_interiors",
            "source_envelope_building_interiors",
            "provider_full_scene",
            "provider_full_scene_rlasm_pixel_lock",
            "provider_full_scene_local_repairs",
            "global_tone_with_safe_building_interiors",
            "global_tone_only",
            "authoritative_source",
        ]
        | None
    ) = None
    local_repair_coverage: float | None = None
    maximum_local_repair_coverage: float | None = None
    instance_source_presence: dict[str, object] | None = None
    unsupported_structure: dict[str, object] | None = None
    server_inventory: dict[str, int] | None = None
    source_locked_rlasm_instance_count: int = 0
    source_locked_rlasm_pixel_lock_applied: bool = False
    source_locked_rlasm_pixel_coverage: float | None = None
    scene_lower_context_coverage: float | None = None
    minimum_scene_lower_context_coverage: float | None = None
    structural_edge_guide_attached: Literal[True] = True
    finish_fusion: Direct3DFinishFusionDiagnostics | None = None
    provider_raw_structural_edge_fidelity: Direct3DRawStructuralEdgeFidelityDiagnostics | None = None
    macro_design_fidelity: Direct3DMacroDesignFidelityDiagnostics | None = None
    visual_change: Direct3DVisualChangeDiagnostics | None = None
    reproject_output_sanity: Direct3DReprojectOutputSanityDiagnostics | None = None
    structural_edge_fidelity: Direct3DStructuralEdgeFidelityDiagnostics | None = None
    registration: Direct3DRegistrationDiagnostics | None = None
    exterior_pixel_count: int | None = None
    exterior_max_channel_delta: int | None = None
    inward_feather_px: float | None = None
    mask_retry_used: Literal[False] = False


class Direct3DRenderResponse(BaseModel):
    image_base64: str
    model: Literal["gpt-image-2"] = "gpt-image-2"
    outcome: Direct3DRenderOutcome = "accepted"
    warnings: list[str] = Field(default_factory=list)
    capture_fingerprint: str
    output_fingerprint: str
    diagnostics: Direct3DRenderDiagnostics
