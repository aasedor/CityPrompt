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

/**
 * Direct 3D starts from an already designed, textured scene, so its defaults
 * describe only the desired finish. Classic's prompts also contain
 * polygon-to-building reconstruction instructions and remain deliberately
 * unchanged for the colored-polygon pipeline.
 */
export const DIRECT_3D_DEFAULT_ART_DIRECTIONS: Readonly<Record<string, string>> = Object.freeze({
  photorealistic: 'Create a high-end contemporary architectural competition visualization. Keep the existing material palette of every building but render each surface with convincing real-world texture: brick with visible mortar depth, timber with warm grain, metal panels with soft sheen, concrete with subtle tonal variation, and clear floor-to-ceiling glazing with believable reflections and slightly warm interior illumination visible through the glass. Use a bright, softly overcast daytime atmosphere with a pale blue sky, gentle directional sunlight, soft contact shadows and natural atmospheric depth toward the horizon. Add realistic public-realm activity at true pedestrian scale: people walking and sitting, cyclists, cafe seating, ornamental grasses, young street trees and understated contemporary street furniture. The composition should feel calm, elegant, civic and inviting, with clean architectural lines, restrained landscaping, balanced exposure, muted natural colours, crisp facade detail and a subtly softened photographic finish with gentle depth of field. Avoid dramatic sunset lighting, oversaturated colours, glossy CGI materials, distorted people and dense overgrown landscaping.',
  photomontage: 'Create a professional architectural photomontage that reads as a real drone photograph of the completed proposal. Match material response, sun direction, shadow length, atmospheric haze, lens character, grain and colour temperature across the proposal and surrounding city so there is no visible compositing seam. Keep the existing material palette but give every surface true photographic texture, with glazing reflecting the actual sky. Add modest believable street life: pedestrians at accurate scale, parked and moving cars, and street trees consistent with the neighbourhood. Balanced exposure and muted natural colours, like an honest planning-submission photomontage.',
  development: 'Create a polished completed-development marketing visualization of institutional quality. Render the buildings as newly finished construction: crisp facades in their existing material palette, clean glazing with warm interior light, welcoming entrances with signage-scale detail, and a freshly landscaped public realm with young street trees, planting beds, benches and clear paving patterns. Bright optimistic daylight with gentle directional sun and soft shadows. Populate lightly with pedestrians, cyclists and cafe activity at accurate scale so the proposal feels built, occupied and integrated. Aspirational but credible, with clean lines and minimal clutter; avoid oversaturation and glossy CGI sheen.',
  atmospheric: 'Create cinematic architectural photography with warm late-day directional light raking across the facades, long soft shadows, gentle golden haze and layered atmospheric depth between foreground and horizon. Bring out material texture in the existing palette; let interior lights begin to glow warmly through the glazing. Add sparse contemplative street life: a few pedestrians, a cyclist, people lingering on benches. Keep the mood serene and restrained with muted warm colours, soft highlights and natural film-like grain, elegant rather than theatrical or oversaturated.',
  winter: 'Create convincing winter architectural photography. Lay a fresh but tidy snow cover on roofs, lawns and planting beds with cleared walks and subtle snow piles at their edges; deciduous trees bare with fine branch detail, evergreens holding light snow, and subtle melt and salt-grit detail on paving. Cold soft overcast daylight with a pale grey-blue sky and soft blue-grey shadows, warmed by restrained interior light glowing through the glazing. Keep the existing facade materials readable through the winter light, with sparse winter-dressed pedestrians at accurate scale and a quiet desaturated palette with crisp cold-air clarity.',
  night: 'Create realistic blue-hour architectural photography. A deep twilight sky grades from indigo to a faint warm horizon; facades in their existing materials are lit by warm interior light spilling from windows, understated facade fixtures and soft pools of street lighting, with subtle reflections on glazing and softly reflective paving. Streets show gentle headlight and taillight presence without light trails, plus sparse evening pedestrians. Keep exposure balanced and believable: readable shadow detail, no blown highlights, no neon oversaturation, the calm quality of a professional dusk shoot.',
  watercolour: 'Create a refined architectural watercolour on textured paper with translucent layered washes, restrained earth colours, soft pigment blooms, loose foliage and enough precise edge definition to keep the design clearly legible.',
  charcoal: 'Create a controlled architectural charcoal illustration on textured paper with a full tonal range, confident structural edges, atmospheric smudging and deep but readable shadows.',
  'marker-render': 'Create a professional architectural marker rendering with precise ink linework, visible directional marker strokes, warm greys and ochres, restrained landscape colour and deliberate white highlights.',
  'pen-and-ink': 'Create a precise architectural pen-and-ink illustration on warm paper using varied line weights, discrete hatching and stippling, crisp construction edges and no colour wash.',
  survey: 'Create a neutral large-format aerial survey photograph with even daylight, true-to-life colour, edge-to-edge clarity and highly legible materials, roofs, streets and landscape.',
  documentary: 'Create calm documentary architectural photography with flat natural daylight, restrained true-to-life colour, honest material variation and an ordinary inhabited quality without cinematic dramatization.',
  'site-plan': 'Create a clean north-up orthographic architectural site plan with precise linework, a restrained pastel palette, clear circulation, simple top-down trees and professional planning-drawing legibility.',
  'site-plan-photo': 'Create a near-nadir photographic drone site-plan view with realistic roofs, landscape, streets and short shadows, integrated seamlessly with the surrounding city context.',
  blueprint: 'Create a strict orthographic architectural blueprint with crisp white construction linework, hatching and tree symbols on a deep Prussian-blue cyanotype ground with subtle aged-paper texture.',
  'site-plan-watercolor': 'Create a near-nadir architectural site plan as a refined hand-painted watercolour with translucent ochre, sage, grey and ultramarine washes, faint pencil construction lines and clearly legible site organization.',
  isometric: 'Create a clean 30-degree axonometric architectural visualization with consistent parallel projection and no perspective distortion, in the manner of a contemporary urban-design diagram. Buildings keep their existing colours as softly lit matte volumes with crisp edges, simple readable facade detail and gentle ambient occlusion; streets and paths are tidy neutral bands; trees are neat stylized canopies; a few small-scale people and vehicles add life. Place the scene on a flat white or very pale ground with soft consistent shadows to one side and an immaculate presentation-board finish.',
  'clay-maquette': 'Create high-angle studio photography of a monochrome pure-white plaster architectural scale model, using soft overhead light and ambient-occlusion shadows to reveal form without any coloured materials.',
  woodblock: 'Create a graphic architectural woodblock print with bold carved outlines, visible wood grain and a restrained vintage palette of crisp flat colours.',
  collage: 'Create a refined post-digital architectural collage with layered paper, carefully cut photographic textures, restrained colour blocks and competition-board composition while keeping the design clearly readable.',
  risograph: 'Create an architectural risograph with a controlled two- or three-colour spot palette, halftone texture, light grain and subtle intentional colour misregistration.',
  'pixel-art': 'Create a polished 16-bit architectural pixel-art scene with uniform grid-aligned pixels, a strict limited palette, selective outlines and checkerboard dithering.',
});

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

export function buildDirect3DVisualPrompt(
  style: string,
  customPrompt: string | undefined,
  _capture: Pick<Direct3DCaptureBundle, 'classCoverage'>,
  _fidelityPolicy: Direct3DFidelityPolicy = resolveDirect3DFidelityPolicy(style),
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
  return publicRealmContext?.trim()
    ? `${artDirection}\n${publicRealmContext.trim()}`
    : artDirection;
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
      /** 'street' marks an eye-level capture: scene presentation is forced and
       *  the server returns review_required in this first version. */
      viewMode?: 'aerial' | 'street';
      /** Authored archetype artwork (facade sheets, catalogue cards) the
       *  provider applies to the named buildings. Max 8, server-enforced. */
      archetypeReferences?: Array<{ image_base64: string; label: string }>;
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
    const response = await rendersApi.generateDirect3D({
      view_mode: viewMode,
      ...(options.archetypeReferences?.length
        ? { archetype_references: options.archetypeReferences.slice(0, 8) }
        : {}),
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
        providerLabel: viewMode === 'street'
          ? 'Direct 3D Street · GPT Image 2'
          : 'Direct 3D · GPT Image 2',
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
