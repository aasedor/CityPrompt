import { useCallback } from 'react';

import { authApi, rendersApi } from '@/services/api';
import { useAuthStore } from '@/store';
import type { SavedRender } from '@/types';
import type { Community3DCaptureClaim } from '@/features/community3d/community3d';
import {
  GLOBE_STYLE_PROMPTS,
  REPROJECTING_STYLES,
  type GlobeRenderResult,
} from './useGlobeAIRender';
import type { Direct3DCaptureBundle, Direct3DProposalRole } from './direct3dCapture';
import type { ResidualLandscapeClaim } from './residualLandscape';

import { DEFAULT_OPENAI_IMAGE_MODEL, imageModelLabel, type OpenAIImageModel } from '@/config/imageModels';

export type Direct3DPresentationMode = 'source_anchored' | 'scene' | 'reproject';
export type Direct3DActivePresentationMode = Exclude<Direct3DPresentationMode, 'source_anchored'>;
export type Direct3DFidelityPolicy = 'precise' | 'balanced' | 'expressive';

// Direct reuses Classic's full aesthetic catalogue verbatim. The Classic
// renderer still owns all of its existing branching and prompting behavior;
// Direct only consumes this exported catalogue to keep style intent aligned.
export const DIRECT_3D_STYLE_IDS = Object.freeze(Object.keys(GLOBE_STYLE_PROMPTS));
export const DIRECT_3D_ALLOWED_STYLES = new Set(DIRECT_3D_STYLE_IDS);

/**
 * Direct 3D starts from an already designed, textured scene, so its defaults
 * describe only the desired finish. Classic's prompts also contain
 * polygon-to-building reconstruction instructions and remain deliberately
 * unchanged for the colored-polygon pipeline.
 */
export const DIRECT_3D_DEFAULT_ART_DIRECTIONS: Readonly<Record<string, string>> = Object.freeze({
  photorealistic: 'Photographically finish the supplied 3D view in soft natural daylight, with balanced exposure, realistic surface texture, subtle reflections in existing glazing and contact shadows. Retain each surface\'s visible material family and colour: enrich the material already present rather than selecting a new facade finish. Preserve the existing architecture, planting and ground surfaces without adding a landscaping scheme. Keep crisp architectural detail and restrained natural colours.',
  photomontage: 'Create a professional architectural photomontage from the supplied camera, with photographic surface texture and coherent lighting across the proposal and surrounding city. Match sun direction, shadow length, atmospheric depth, grain and colour temperature so the existing objects share one believable exposure. Retain the existing material palette and reflect the visible sky in existing glazing. Finish only the buildings, planting, furniture and surfaces already present. Balanced exposure and muted natural colours, suitable for a planning presentation.',
  development: 'Create a polished completed-development visualization. Treat the existing construction as newly finished: crisp facades in their current material palette, clean glazing, readable entrance details and neatly maintained existing planting and paving. Bright optimistic daylight with gentle directional sun, soft contact shadows and balanced exposure. Keep the public-realm design and furnishing inventory exactly as captured. Aspirational but credible, with restrained saturation and realistic surface texture.',
  atmospheric: 'Create cinematic architectural photography with warm late-day directional light raking across the existing facades, long soft shadows, gentle golden haze and layered atmospheric depth. Bring out texture in the current material palette and a restrained warm glow behind existing glazing. Keep foreground details readable and retain the captured planting and furnishing arrangement. Serene, muted warm colours, soft highlights and subtle film grain.',
  winter: 'Create convincing winter architectural photography. Add a thin snow treatment to existing roofs, lawns and planting beds while retaining their profiles. Show the existing walks cleared to their captured edges, bare deciduous branches and lightly snow-dusted evergreens in their original positions. Use cold overcast daylight, a pale grey-blue sky and soft blue-grey shadows with restrained warmth behind existing glazing. Keep facade identities and circulation clearly readable in a quiet desaturated palette.',
  night: 'Create realistic blue-hour architectural photography with an indigo sky and a faint warm horizon. Light the existing facades through their existing windows and fixtures, with soft contact shadows and subtle reflections in glazing and paving. Preserve the captured circulation and furnishings. Balance warm light against cool twilight so architectural details remain readable without blown highlights, new light fixtures or neon oversaturation.',
  watercolour: 'Paint the supplied view as a hand-painted architectural watercolour on warm cold-pressed paper. Use transparent overlapping washes, visible brush variation, pigment granulation and occasional pooling at wash edges. Let paper show through highlights; soften foliage with wet-on-wet colour while keeping building corners, roof profiles, openings and path edges legible with selective dry-brush definition. Translate the existing material colours into a restrained, harmonious pigment palette. Simplify surface texture without simplifying the design or filling in hidden features. The whole image, including the city context, should read as watercolour rather than a photograph with a paper-texture filter.',
  charcoal: 'Draw the supplied view as an architectural charcoal study on lightly textured warm paper. Use broad rubbed charcoal for sky and ground, visible directional strokes for surfaces, sharp charcoal-pencil edges for the existing architecture and lifted paper highlights. Keep deep shadows readable and soften distant context with lighter marks. Describe foliage with clustered strokes while retaining its position and silhouette. A hand-drawn monochrome tonal study, with clearly preserved roof profiles, openings and circulation.',
  'marker-render': 'Create a professional architectural marker rendering with precise ink linework, visible directional marker strokes, warm greys and ochres, restrained landscape colour and deliberate white highlights.',
  'pen-and-ink': 'Create a precise architectural pen-and-ink illustration on warm paper using varied line weights, discrete hatching and stippling, crisp construction edges and no colour wash.',
  survey: 'Create a neutral large-format architectural survey photograph from the supplied viewpoint, with even daylight, true-to-life colour, edge-to-edge clarity and highly legible materials, buildings, streets and landscape.',
  documentary: 'Create calm documentary architectural photography with flat natural daylight, restrained true-to-life colour, honest material variation and an ordinary inhabited quality without cinematic dramatization.',
  'site-plan': 'Create a clean north-up orthographic architectural site plan with precise linework, a restrained pastel palette, clear circulation, simple top-down trees and professional planning-drawing legibility.',
  'site-plan-photo': 'Create a near-nadir photographic drone site-plan view with realistic roofs, landscape, streets and short shadows, integrated seamlessly with the surrounding city context.',
  blueprint: 'Create a strict orthographic architectural blueprint with crisp white construction linework, hatching and tree symbols on a deep Prussian-blue cyanotype ground with subtle aged-paper texture.',
  'site-plan-watercolor': 'Create a near-nadir architectural site plan as a refined hand-painted watercolour with translucent ochre, sage, grey and ultramarine washes, faint pencil construction lines and clearly legible site organization.',
  isometric: 'Create a clean 30-degree axonometric architectural visualization with consistent parallel projection and no perspective distortion, in the manner of a contemporary urban-design diagram. Buildings keep their existing colours as softly lit matte volumes with crisp edges, simple readable facade detail and gentle ambient occlusion; streets and paths are tidy neutral bands; trees are neat stylized canopies; Place the scene on a flat white or very pale ground with soft consistent shadows to one side and an immaculate presentation-board finish.',
  'clay-maquette': 'Create high-angle studio photography of a monochrome pure-white plaster architectural scale model, using soft overhead light and ambient-occlusion shadows to reveal form without any coloured materials.',
  woodblock: 'Create a graphic architectural woodblock print with bold carved outlines, visible wood grain and a restrained vintage palette of crisp flat colours.',
  collage: 'Create a refined post-digital architectural collage with layered paper, carefully cut photographic textures, restrained colour blocks and competition-board composition while keeping the design clearly readable.',
  risograph: 'Create an architectural risograph using two or three restrained spot inks on warm uncoated paper. Use flat ink shapes, visible halftone dots and subtle ink-density variation. Keep structural contours registered to the source; confine slight ink misregistration to texture within surfaces so building edges, windows and path boundaries remain legible. Apply the print treatment consistently to proposal and context.',
  'pixel-art': 'Create a polished 16-bit architectural pixel-art scene with uniform grid-aligned pixels, a strict limited palette, selective outlines and checkerboard dithering.',
});

export function resolveDirect3DPresentationMode(style: string): Direct3DActivePresentationMode {
  return REPROJECTING_STYLES.has(style) ? 'reproject' : 'scene';
}

const EXPRESSIVE_DIRECT_3D_STYLES = new Set([
  'site-plan',
  'site-plan-watercolor',
  'blueprint',
  'watercolour',
  'charcoal',
  'pen-and-ink',
  'isometric',
  'marker-render',
  'clay-maquette',
  'woodblock',
  'collage',
  'risograph',
  'pixel-art',
]);

export function resolveDirect3DFidelityPolicy(style: string): Direct3DFidelityPolicy {
  if (REPROJECTING_STYLES.has(style) || EXPRESSIVE_DIRECT_3D_STYLES.has(style)) return 'expressive';
  return 'balanced';
}

export interface Direct3DRenderDiagnostics {
  /** Missing on legacy source-anchored responses. */
  processing_mode?: Direct3DPresentationMode;
  view_lock?: 'source_pixel_locked' | 'camera_registered' | 'not_applicable_layout_guided';
  context_restyled?: boolean;
  provider_first?: boolean;
  provider_spatial_pixels_retained?: boolean;
  fidelity_policy?: Direct3DFidelityPolicy;
  instance_id_attached?: boolean;
  instance_count?: number;
  provider_raw_instance_source_presence?: {
    passed: boolean;
    evaluated_instance_count?: number;
    weakest_instance_recall?: number | null;
    missing_instance_ids?: string[];
  } | null;
  provider_raw_unsupported_structure?: {
    passed: boolean;
    largest_component_pixels?: number;
    largest_component_bbox_fraction?: number;
    proposal_component_count?: number;
    context_component_count?: number;
  } | null;
  returned_safety_strategy?:
    | 'source_envelope'
    | 'source_envelope_all_authored_interiors'
    | 'source_envelope_building_interiors'
    | 'provider_full_scene'
    | 'provider_full_scene_rlasm_pixel_lock'
    | 'provider_full_scene_local_repairs'
    | 'global_tone_with_safe_building_interiors'
    | 'global_tone_only'
    | 'authoritative_source'
    | null;
  local_repair_coverage?: number | null;
  maximum_local_repair_coverage?: number | null;
  instance_source_presence?: {
    passed: boolean;
    evaluated_instance_count?: number;
    weakest_instance_recall?: number | null;
    missing_instance_ids?: string[];
  } | null;
  unsupported_structure?: {
    passed: boolean;
    largest_component_pixels?: number;
    largest_component_bbox_fraction?: number;
    proposal_component_count?: number;
    context_component_count?: number;
  } | null;
  server_inventory?: {
    building?: number;
    park?: number;
    street?: number;
    ground?: number;
    landscape?: number;
    [key: string]: number | undefined;
  } | null;
  source_locked_rlasm_instance_count?: number;
  source_locked_rlasm_pixel_lock_applied?: boolean;
  source_locked_rlasm_pixel_coverage?: number | null;
  source_width: number;
  source_height: number;
  normalized_width: number;
  normalized_height: number;
  proposal_coverage: number;
  context_coverage: number;
  object_id_attached: boolean;
  object_id_coverage?: number | null;
  object_id_proposal_recall?: number | null;
  object_id_proposal_iou?: number | null;
  minimum_object_id_proposal_recall?: number | null;
  minimum_object_id_proposal_iou?: number | null;
  scene_lower_context_coverage?: number | null;
  minimum_scene_lower_context_coverage?: number | null;
  structural_edge_guide_attached: true;
  finish_fusion?: {
    method: 'source-geometry-multiscale-source-phase-detail-v2';
    sigma_px: number;
    rgb_delta_clip: number;
    default_strength: number;
    role_strengths: Record<Direct3DProposalRole, number>;
    detail_fine_sigma_px: number;
    detail_medium_sigma_px: number;
    detail_correction_clip: number;
    detail_role_gain_caps: Record<string, { fine: number; medium: number }>;
    microtexture_sigma_px: number;
    microtexture_correction_clip: number;
    microtexture_role_gain_caps: Record<string, number>;
    provider_high_frequency_phase_transferred: false;
    safe_microtexture_coverage: number;
    source_detail_correlation?: number | null;
    source_texture_p75?: number | null;
    fused_texture_p75?: number | null;
    texture_gain?: number | null;
    role_metrics: Record<string, {
      detail_fine_gain: number;
      detail_medium_gain: number;
      microtexture_gain: number;
      safe_microtexture_pixels: number;
      safe_microtexture_coverage: number;
      source_texture_p75?: number | null;
      fused_texture_p75?: number | null;
      texture_gain?: number | null;
      source_detail_correlation?: number | null;
    }>;
  } | null;
  provider_raw_structural_edge_fidelity?: {
    passed: boolean;
    beauty_edge_recall: number;
    coarse_edge_recall: number;
    semantic_edge_recall?: number | null;
    semantic_component_min_recall?: number | null;
    building_internal_edge_recall?: number | null;
  } | null;
  macro_design_fidelity?: {
    passed: boolean;
    tolerance_px: number;
    silhouette_edge_pixels: number;
    silhouette_edge_recall?: number | null;
    coarse_edge_pixels: number;
    coarse_edge_recall: number;
    semantic_edge_pixels: number;
    semantic_edge_recall?: number | null;
    evaluated_component_count: number;
    semantic_component_min_recall?: number | null;
    reference_edge_p90_distance_px: number;
    candidate_coarse_edge_pixels?: number | null;
    candidate_coarse_edge_precision?: number | null;
    candidate_coarse_edge_density_ratio?: number | null;
    minimum_silhouette_edge_recall?: number | null;
    minimum_coarse_edge_recall?: number | null;
    minimum_semantic_edge_recall?: number | null;
    minimum_semantic_component_recall?: number | null;
    maximum_reference_edge_p90_distance_px?: number | null;
    minimum_candidate_coarse_edge_precision?: number | null;
    maximum_candidate_coarse_edge_density_ratio?: number | null;
    building_internal_edges_required: false;
  } | null;
  visual_change?: {
    passed: true;
    whole_frame_mean_absolute_delta: number;
    proposal_mean_absolute_delta: number;
    proposal_detail_delta_p75: number;
    proposal_photometric_residual_p95: number;
    novel_detail_edge_coverage: number;
    context_mean_absolute_delta?: number | null;
    context_photometric_residual_p95?: number | null;
    context_detail_delta_p75?: number | null;
    context_pixel_count?: number | null;
    context_frame_top_fraction?: number | null;
    minimum_whole_frame_mean_absolute_delta?: number | null;
    minimum_proposal_mean_absolute_delta: number;
    minimum_proposal_detail_delta_p75: number;
    minimum_proposal_photometric_residual_p95: number;
    minimum_novel_detail_edge_coverage: number;
    minimum_context_mean_absolute_delta?: number | null;
    minimum_context_photometric_residual_p95?: number | null;
    minimum_context_detail_delta_p75?: number | null;
    context_change_required: true;
    color_grade_only_rejected: true;
  } | null;
  reproject_output_sanity?: {
    passed: true;
    whole_frame_mean_absolute_delta: number;
    luminance_standard_deviation: number;
    luminance_dynamic_range_p90: number;
    structural_edge_coverage: number;
    occupied_edge_cells: number;
    significant_edge_component_count: number;
    required_edge_component_count: number;
    minimum_whole_frame_mean_absolute_delta: number;
    minimum_luminance_standard_deviation: number;
    minimum_luminance_dynamic_range_p90: number;
    minimum_structural_edge_coverage: number;
    maximum_structural_edge_coverage: number;
    minimum_occupied_edge_cells: number;
    semantic_inventory_proxy_only: true;
  } | null;
  structural_edge_fidelity?: {
    passed: true;
    tolerance_px: number;
    reference_edge_pixels: number;
    candidate_edge_pixels: number;
    beauty_edge_recall: number;
    coarse_edge_pixels: number;
    coarse_edge_recall: number;
    semantic_edge_pixels: number;
    semantic_edge_recall?: number | null;
    semantic_component_min_recall?: number | null;
    building_internal_edge_pixels: number;
    building_internal_edge_recall?: number | null;
    reference_edge_p90_distance_px: number;
  } | null;
  registration?: {
    method: 'identity' | 'ecc-euclidean';
    score: number;
    score_metric?: 'luminance-correlation' | 'bidirectional-structural-edge-recall';
    photometric_score?: number | null;
    structural_context_score?: number | null;
    translation_x_px: number;
    translation_y_px: number;
    translation_norm_px?: number | null;
    rotation_degrees: number;
    maximum_translation_norm_px?: number | null;
    maximum_abs_rotation_degrees?: number | null;
  } | null;
  exterior_pixel_count?: number | null;
  exterior_max_channel_delta?: number | null;
  inward_feather_px?: number | null;
  mask_retry_used: false;
}

export interface Direct3DRenderResult {
  render: GlobeRenderResult;
  providerOriginalRender?: SavedRender;
  diagnostics: Direct3DRenderDiagnostics;
  captureFingerprint: string;
  outputFingerprint: string;
  outcome: 'accepted' | 'review_required';
  warnings: string[];
  sourceImageUrl: string;
  fidelityPolicy: Direct3DFidelityPolicy;
}

export function buildDirect3DVisualPrompt(
  style: string,
  customPrompt: string | undefined,
  _capture: Pick<Direct3DCaptureBundle, 'classCoverage'>,
  fidelityPolicy: Direct3DFidelityPolicy = resolveDirect3DFidelityPolicy(style),
  publicRealmContext?: string,
): string {
  const custom = customPrompt?.trim();
  const resolvedStyle = DIRECT_3D_ALLOWED_STYLES.has(style)
    ? style
    : 'photorealistic';
  const styleDirection = DIRECT_3D_DEFAULT_ART_DIRECTIONS[resolvedStyle];
  // Keep the selected aesthetic meaningful when the user adds only a short
  // project cue such as "New York brownstone multifamily." Defaults carry the
  // full art direction (palette-agnostic), so a custom brief refines material
  // and project intent without recreating the former constraint wall.
  const artDirection = custom
    ? `${styleDirection}\nPROJECT-SPECIFIC ART DIRECTION: ${custom}`
    : styleDirection;
  const direction = publicRealmContext?.trim()
    ? `${artDirection}\n${publicRealmContext.trim()}`
    : artDirection;
  if (resolveDirect3DPresentationMode(resolvedStyle) === 'scene' && fidelityPolicy === 'balanced') {
    return `${direction}\nCONCEPT FIDELITY: Preserve every building's count, position, footprint, height and roof massing; retain street routes and junctions, pedestrian access and each park's playing areas and programme. Refine surface materials, lighting, foliage and small details within that design. Do not add, remove, relocate or join buildings, roads, paths or sports facilities. Keep the source camera. Keep cropped and occluded elements cropped and occluded; do not complete hidden structures elsewhere. Leave gaps as drawn: do not invent connecting sidewalks, driveways or sports facilities.`;
  }
  return resolveDirect3DPresentationMode(resolvedStyle) === 'scene'
    ? `${direction}\nFinish only what is visible in the source camera. Keep cropped and occluded elements cropped and occluded; do not complete or relocate them elsewhere. Leave gaps between buildings, paths and parks as drawn: do not invent connecting sidewalks, driveways, planting beds or furniture. People, if requested, may use only already-visible walkable surfaces; never build a new surface for them. Preserve each building's own facade materials, openings and roof geometry. Style changes the finish, not the design.`
    : direction;
}

export function useDirect3DRender() {
  const renderDirect3D = useCallback(async (
    capture: Direct3DCaptureBundle,
    options: {
      style: string;
      model?: OpenAIImageModel;
      fidelityPolicy?: Direct3DFidelityPolicy;
      customPrompt?: string;
      addPeople?: boolean;
      addVehicles?: boolean;
      projectId: string;
      community3DClaims: Community3DCaptureClaim[];
      residualLandscapeClaim?: ResidualLandscapeClaim | null;
      /** 'street' marks an eye-level capture: scene presentation is forced and
       *  the server returns review_required in this first version. */
      viewMode?: 'aerial' | 'street';
      /** Authored archetype artwork (facade sheets, catalogue cards) the
       *  provider applies to the named buildings. Max 8, server-enforced. */
      archetypeReferences?: Array<{ image_base64: string; label: string; zone_ids?: string[] }>;
      /** Measured park/street/building interfaces derived from source zones. */
      publicRealmContext?: string;
    },
  ): Promise<Direct3DRenderResult> => {
    if (!DIRECT_3D_ALLOWED_STYLES.has(options.style)) {
      throw new Error(`Unknown Direct 3D style: ${options.style}`);
    }
    if (!options.projectId) {
      throw new Error('Direct 3D requires a saved project before rendering.');
    }
    if (!options.community3DClaims.length) {
      throw new Error('Direct 3D requires current per-zone scene fingerprints.');
    }
    const fidelityPolicy = options.fidelityPolicy
      ?? resolveDirect3DFidelityPolicy(options.style);
    const prompt = buildDirect3DVisualPrompt(
      options.style,
      options.customPrompt,
      capture,
      fidelityPolicy,
      options.publicRealmContext,
    );
    const viewMode = options.viewMode ?? 'aerial';
    const presentationMode = viewMode === 'street'
      ? 'scene'
      : resolveDirect3DPresentationMode(options.style);
    if (
      !capture.depthImageBase64
      || !capture.normalImageBase64
      || !capture.materialIdImageBase64
      || !capture.materialIdManifest
    ) {
      throw new Error(
        'Direct 3D high-resolution rendering requires a complete geometry control capture.',
      );
    }
    const response = await rendersApi.generateDirect3D({
      model: options.model ?? DEFAULT_OPENAI_IMAGE_MODEL,
      control_bundle_version: 2,
      view_mode: viewMode,
      // The captured 3D model owns identity for every same-camera style.
      // Catalogue artwork can prescribe different roofs, openings or materials.
      ...(options.archetypeReferences?.length && presentationMode !== 'scene'
        ? { archetype_references: options.archetypeReferences.slice(0, 8) }
        : {}),
      beauty_image_base64: capture.beautyImageBase64,
      proposal_mask_base64: capture.proposalMaskBase64,
      object_id_image_base64: capture.classIdImageBase64,
      object_id_manifest: { ...capture.classIdManifest },
      instance_id_image_base64: capture.instanceIdImageBase64,
      instance_id_manifest: { ...capture.instanceIdManifest },
      depth_image_base64: capture.depthImageBase64,
      normal_image_base64: capture.normalImageBase64,
      material_id_image_base64: capture.materialIdImageBase64,
      material_id_manifest: { ...capture.materialIdManifest },
      camera: capture.camera,
      capture: {
        width: capture.width,
        height: capture.height,
        proposal_coverage: capture.maskCoverage,
      },
      prompt,
      style: options.style,
      add_people: options.addPeople === true,
      add_vehicles: options.addVehicles === true,
      fidelity_policy: fidelityPolicy,
      presentation_mode: presentationMode,
      project_id: options.projectId,
      community_3d_claims: options.community3DClaims,
        park_access_snapshot: capture.parkAccessSnapshot,
        shared_ground_snapshot: capture.sharedGroundSnapshot,
      residual_landscape_claim: options.residualLandscapeClaim ?? undefined,
    });
    // Refresh after the server charge, without hiding a successful render if
    // the balance request fails or restoring a user who signed out meanwhile.
    const requestingUserId = useAuthStore.getState().user?.id;
    if (requestingUserId) void authApi.me().then(user => {
      if (user.id === requestingUserId && useAuthStore.getState().user?.id === requestingUserId) useAuthStore.getState().setUser(user);
    }).catch(() => { /* The next account refresh will reconcile the balance. */ });
    // Respect the server's fidelity decision. The rejected provider image stays
    // available separately for QA; it must never replace the returned source.
    return {
      render: {
        imageUrl: `data:image/png;base64,${response.image_base64}`,
        prompt,
        model: response.model,
        imageQuality: 'high',
        savedRender: response.saved_render ?? undefined,
        providerLabel: response.diagnostics.returned_safety_strategy === 'authoritative_source'
          ? 'Original 3D view · AI finish needs review'
          : viewMode === 'street'
          ? `Direct 3D Street · ${imageModelLabel(response.model)}`
          : `Direct 3D · ${imageModelLabel(response.model)}`,
      },
      diagnostics: response.diagnostics,
      providerOriginalRender: response.provider_original_render ?? undefined,
      captureFingerprint: response.capture_fingerprint,
      outputFingerprint: response.output_fingerprint,
      outcome: response.outcome,
      warnings: [...response.warnings],
      sourceImageUrl: capture.beautyImageBase64.startsWith('data:') ? capture.beautyImageBase64 : `data:image/png;base64,${capture.beautyImageBase64}`,
      fidelityPolicy,
    };
  }, []);

  return { renderDirect3D };
}
