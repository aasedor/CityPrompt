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
export type Direct3DFidelityPolicy = 'precise' | 'balanced' | 'expressive';

// Direct reuses Classic's full aesthetic catalogue verbatim. The Classic
// renderer still owns all of its existing branching and prompting behavior;
// Direct only consumes this exported catalogue to keep style intent aligned.
export const DIRECT_3D_STYLE_IDS = Object.freeze(Object.keys(GLOBE_STYLE_PROMPTS));
export const DIRECT_3D_ALLOWED_STYLES = new Set(DIRECT_3D_STYLE_IDS);

export function resolveDirect3DPresentationMode(style: string): Direct3DActivePresentationMode {
  return REPROJECTING_STYLES.has(style) ? 'reproject' : 'scene';
}

const PRECISE_DIRECT_3D_STYLES = new Set(['survey', 'documentary']);
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
  if (PRECISE_DIRECT_3D_STYLES.has(style)) return 'precise';
  if (REPROJECTING_STYLES.has(style) || EXPRESSIVE_DIRECT_3D_STYLES.has(style)) return 'expressive';
  return 'balanced';
}

export interface Direct3DRenderDiagnostics {
  /** Missing on legacy source-anchored responses. */
  processing_mode?: Direct3DPresentationMode;
  view_lock?: 'source_pixel_locked' | 'camera_registered' | 'not_applicable_layout_guided';
  context_restyled?: boolean;
  provider_first?: boolean;
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
    | 'global_tone_with_safe_building_interiors'
    | 'global_tone_only'
    | 'authoritative_source'
    | null;
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
  diagnostics: Direct3DRenderDiagnostics;
  captureFingerprint: string;
  outputFingerprint: string;
  outcome: 'accepted' | 'review_required';
  warnings: string[];
  sourceImageUrl: string;
  fidelityPolicy: Direct3DFidelityPolicy;
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
  fidelityPolicy: Direct3DFidelityPolicy = resolveDirect3DFidelityPolicy(style),
): string {
  const presentationMode = resolveDirect3DPresentationMode(style);
  const custom = customPrompt?.trim();
  const fidelityInstruction = fidelityPolicy === 'precise'
    ? 'PRECISE FIDELITY: retain surveyed silhouettes, rooflines, dimensions, camera and context structure; improve only finish, material realism, lighting and atmosphere.'
    : fidelityPolicy === 'expressive'
      ? 'EXPRESSIVE FIDELITY: artistic edge and projection interpretation is permitted, but the exact authored building, park, street and protected-feature inventory and topology remain binding.'
      : 'BALANCED FIDELITY: improve facade, roof, landscape and public-realm presentation with modest edge variation while preserving every authored building, park, street, intersection and protected feature.';
  return [
    `DIRECT 3D STYLE ID: ${DIRECT_3D_ALLOWED_STYLES.has(style) ? style : 'photorealistic'}.`,
    `PRESENTATION MODE: ${presentationMode.toUpperCase()}.`,
    fidelityInstruction,
    'The server-supplied semantic, instance and structural guides are authoritative. Do not add, remove, split or merge permanent buildings or major site features.',
    'Outside the parcel, preserve the existing building, road, water and open-space inventory. Changes to material, light, weather and atmospheric finish are allowed.',
    'Allowed additions are limited to non-permanent scale entourage such as people and vehicles unless the instance inventory explicitly identifies another authored feature.',
    visibleClassSummary(capture.classCoverage),
    custom ? `ADDITIONAL ART DIRECTION: ${custom}` : '',
  ].filter(Boolean).join('\n');
}

export function useDirect3DRender() {
  const renderDirect3D = useCallback(async (
    capture: Direct3DCaptureBundle,
    options: {
      style: string;
      fidelityPolicy?: Direct3DFidelityPolicy;
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
    const fidelityPolicy = options.fidelityPolicy
      ?? resolveDirect3DFidelityPolicy(options.style);
    const prompt = buildDirect3DVisualPrompt(
      options.style,
      options.customPrompt,
      capture,
      fidelityPolicy,
    );
    const presentationMode = resolveDirect3DPresentationMode(options.style);
    const response = await rendersApi.generateDirect3D({
      beauty_image_base64: capture.beautyImageBase64,
      proposal_mask_base64: capture.proposalMaskBase64,
      object_id_image_base64: capture.classIdImageBase64,
      object_id_manifest: { ...capture.classIdManifest },
      instance_id_image_base64: capture.instanceIdImageBase64,
      instance_id_manifest: { ...capture.instanceIdManifest },
      capture: {
        width: capture.width,
        height: capture.height,
        proposal_coverage: capture.maskCoverage,
      },
      prompt,
      style: options.style,
      fidelity_policy: fidelityPolicy,
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
      outcome: response.outcome,
      warnings: [...response.warnings],
      sourceImageUrl: capture.beautyImageBase64,
      fidelityPolicy,
    };
  }, []);

  return { renderDirect3D };
}
