import { useCallback } from 'react';

import { rendersApi } from '@/services/api';
import type { Community3DCaptureClaim } from '@/features/community3d/community3d';
import type { GlobeRenderResult } from './useGlobeAIRender';
import type { Direct3DCaptureBundle, Direct3DProposalRole } from './direct3dCapture';
import type { ResidualLandscapeClaim } from './residualLandscape';

const DIRECT_3D_STYLE_TREATMENTS: Record<string, string> = {
  photorealistic: 'Natural architectural photography with physically convincing materials and restrained daylight.',
  photomontage: 'A polished planning photomontage integrated into the surrounding captured city and atmosphere.',
  development: 'High-end development visualization with credible glazing, facade depth, roof materials and public realm.',
  atmospheric: 'Warm atmospheric architectural photography with soft haze, realistic shadows and planted richness.',
  winter: 'A convincing winter scene with seasonally appropriate vegetation, snow accumulation and cold daylight.',
  night: 'A realistic blue-hour or night scene with plausible interior light, street lighting and controlled reflections.',
  survey: 'Neutral, highly legible survey photography with even light and minimal cinematic exaggeration.',
  documentary: 'Honest documentary architecture photography with natural weathering and everyday material variation.',
  watercolour: 'A refined architectural watercolour treatment while retaining the captured camera and every silhouette.',
  charcoal: 'A tonal charcoal architectural illustration while retaining the captured camera and every silhouette.',
  'marker-render': 'A professional marker rendering while retaining the captured camera and every silhouette.',
  'pen-and-ink': 'A precise pen-and-ink architectural illustration while retaining the captured camera and every silhouette.',
  'clay-maquette': 'A crafted clay architectural model treatment while retaining the captured camera and every silhouette.',
  woodblock: 'A graphic woodblock treatment while retaining the captured camera and every silhouette.',
  collage: 'A layered architectural collage treatment while retaining the captured camera and every silhouette.',
  risograph: 'A controlled risograph treatment while retaining the captured camera and every silhouette.',
  'pixel-art': 'A polished pixel-art treatment while retaining the captured camera and every silhouette.',
};

// Direct 3D hard-preserves every context pixel outside the proposal mask.
// Only treatments that can look coherent as proposal-local refinements belong
// here. Whole-frame lighting, season, projection and art-media changes stay on
// the existing Classic pipeline, which was designed for those transformations.
export const DIRECT_3D_ALLOWED_STYLES = new Set([
  'photorealistic',
  'development',
  'survey',
  'documentary',
]);

export interface Direct3DRenderDiagnostics {
  source_width: number;
  source_height: number;
  normalized_width: number;
  normalized_height: number;
  proposal_coverage: number;
  context_coverage: number;
  object_id_attached: boolean;
  object_id_coverage?: number | null;
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
  registration: {
    method: 'identity' | 'ecc-euclidean';
    score: number;
    translation_x_px: number;
    translation_y_px: number;
    rotation_degrees: number;
  };
  exterior_pixel_count: number;
  exterior_max_channel_delta: number;
  inward_feather_px: number;
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
  const treatment = DIRECT_3D_STYLE_TREATMENTS[style]
    ?? DIRECT_3D_STYLE_TREATMENTS.photorealistic;
  const custom = customPrompt?.trim();
  return [
    `VISUAL FINISH: ${treatment}`,
    'The compiled 3D buildings, parks, streets, paths, residual landscape and placed trees are the final scene design.',
    'Improve material scale, glazing, foliage, weathering, illumination, contact shadows and atmospheric integration.',
    'Keep the source camera, perspective, object count, dimensions, placement, roof forms, circulation and occlusion unchanged.',
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
      throw new Error('This treatment changes the whole frame and must use Classic Polygons.');
    }
    if (!options.projectId) {
      throw new Error('Direct 3D requires a saved project before rendering.');
    }
    if (!options.community3DClaims.length) {
      throw new Error('Direct 3D requires current per-zone scene fingerprints.');
    }
    const prompt = buildDirect3DVisualPrompt(options.style, options.customPrompt, capture);
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
