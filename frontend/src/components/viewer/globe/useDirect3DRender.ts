import { useCallback } from 'react';

import { rendersApi } from '@/services/api';
import type { Community3DCaptureClaim } from '@/features/community3d/community3d';
import {
  GLOBE_STYLE_PROMPTS,
  REPROJECTING_STYLES,
  type GlobeRenderResult,
} from './useGlobeAIRender';
import type { Direct3DCaptureBundle, Direct3DProposalRole } from './direct3dCapture';
import type { ResidualLandscapeClaim } from './residualLandscape';

export type Direct3DPresentationMode = 'source_anchored' | 'scene' | 'reproject';
export type Direct3DActivePresentationMode = Exclude<Direct3DPresentationMode, 'source_anchored'>;

// Direct reuses Classic's full aesthetic catalogue verbatim. The Classic
// renderer still owns all of its existing branching and prompting behavior;
// Direct only consumes this exported catalogue to keep style intent aligned.
export const DIRECT_3D_STYLE_IDS = Object.freeze(Object.keys(GLOBE_STYLE_PROMPTS));
export const DIRECT_3D_ALLOWED_STYLES = new Set(DIRECT_3D_STYLE_IDS);

export function resolveDirect3DPresentationMode(style: string): Direct3DActivePresentationMode {
  return REPROJECTING_STYLES.has(style) ? 'reproject' : 'scene';
}

export interface Direct3DRenderDiagnostics {
  /** Missing on legacy source-anchored responses. */
  processing_mode?: Direct3DPresentationMode;
  view_lock?: 'source_pixel_locked' | 'camera_registered' | 'not_applicable_layout_guided';
  context_restyled?: boolean;
  provider_first?: boolean;
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
    passed: true;
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
  diagnostics: Direct3DRenderDiagnostics;
  captureFingerprint: string;
  outputFingerprint: string;
}

function visibleClassSummary(
  coverage: Partial<Record<Direct3DProposalRole, number>>,
): string {
  const parts = Object.entries(coverage)
    .filter((entry): entry is [Direct3DProposalRole, number] => Number.isFinite(entry[1]) && entry[1] > 0)
    .map(([role, amount]) => `${role} ${(amount * 100).toFixed(1)}%`);
  return parts.length ? `Visible proposal classes: ${parts.join(', ')}.` : '';
}

export function buildDirect3DVisualPrompt(
  style: string,
  customPrompt: string | undefined,
  capture: Pick<Direct3DCaptureBundle, 'classCoverage'>,
): string {
  const treatment = GLOBE_STYLE_PROMPTS[style]
    ?? GLOBE_STYLE_PROMPTS.photorealistic;
  const presentationMode = resolveDirect3DPresentationMode(style);
  const custom = customPrompt?.trim();
  const presentationInstructions = presentationMode === 'reproject'
    ? [
        'PRESENTATION MODE: REPROJECT (style-directed full-frame re-render).',
        'You may change the projection, viewpoint and camera orientation only as needed to achieve the selected plan, orthographic, axonometric or maquette aesthetic.',
        'Preserve the complete object inventory, site layout and circulation topology, adjacency, relative dimensions, building footprints and heights, park and street design, major tree anchors, and the identity of every designed element.',
        'Re-render the entire frame cohesively in the selected medium, including the proposal and surrounding city context; replace raw real-time CG and Google photogrammetry artifacts with a deliberate finished presentation.',
      ]
    : [
        'PRESENTATION MODE: SCENE (camera-preserving full-frame re-render).',
        'The captured camera, perspective, framing, crop, horizon and aspect ratio are locked.',
        'The compiled scene is binding for macro design: preserve object inventory, silhouettes, footprints, heights, roof forms, park and street topology, relative dimensions, occlusion order, and major tree anchors.',
        'Visibly re-render the entire frame as one cohesive finished image, including both the designed site and its surrounding city context. Replace raw real-time CG and Google photogrammetry artifacts with convincing materials, foliage, light, atmosphere and detail in the selected medium.',
      ];
  return [
    `STYLE: ${treatment}`,
    ...presentationInstructions,
    'The compiled 3D buildings, parks, streets, paths, residual landscape and placed trees are authoritative design input, not loose inspiration.',
    'If the STYLE text mentions colored polygon fills, apply that instruction to unfinished real-time 3D surfaces; do not invent or retain polygon overlays.',
    'QUALITY BAR: Produce a presentation-grade architectural visualization, not a textured viewport. Fully resolve facade depth, glazing, roofs, building-to-ground contact, continuous terrain to the parcel edge, curbs, paving, road markings, planting beds, natural tree canopies, and public-realm furniture. Add only plausible people and vehicles that clarify scale.',
    'Use coherent light direction, contact shadows, reflections and atmospheric depth wherever the selected medium supports them. Remove labels, selection outlines, white or grey parcel voids, ground seams, floating elements, repeated procedural artifacts, and blurry photogrammetry failure geometry.',
    'This must be a visible generative re-render of the complete image, not a color grade, texture overlay, source-pixel preservation pass, or proposal-only local edit.',
    visibleClassSummary(capture.classCoverage),
    custom ? `ADDITIONAL ART DIRECTION: ${custom}` : '',
  ].filter(Boolean).join('\n');
}

export function useDirect3DRender() {
  const renderDirect3D = useCallback(async (
    capture: Direct3DCaptureBundle,
    options: {
      style: string;
      customPrompt?: string;
      projectId: string;
      community3DClaims: Community3DCaptureClaim[];
      residualLandscapeClaim?: ResidualLandscapeClaim | null;
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
    const prompt = buildDirect3DVisualPrompt(options.style, options.customPrompt, capture);
    const presentationMode = resolveDirect3DPresentationMode(options.style);
    const response = await rendersApi.generateDirect3D({
      beauty_image_base64: capture.beautyImageBase64,
      proposal_mask_base64: capture.proposalMaskBase64,
      object_id_image_base64: capture.classIdImageBase64,
      object_id_manifest: { ...capture.classIdManifest },
      capture: {
        width: capture.width,
        height: capture.height,
        proposal_coverage: capture.maskCoverage,
      },
      prompt,
      style: options.style,
      presentation_mode: presentationMode,
      project_id: options.projectId,
      community_3d_claims: options.community3DClaims,
      residual_landscape_claim: options.residualLandscapeClaim ?? undefined,
    });
    return {
      render: {
        imageUrl: `data:image/png;base64,${response.image_base64}`,
        prompt,
        model: response.model,
        imageQuality: 'high',
        providerLabel: 'Direct 3D · GPT Image 2',
      },
      diagnostics: response.diagnostics,
      captureFingerprint: response.capture_fingerprint,
      outputFingerprint: response.output_fingerprint,
    };
  }, []);

  return { renderDirect3D };
}
