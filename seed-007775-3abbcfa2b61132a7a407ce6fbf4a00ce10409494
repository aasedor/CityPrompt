import { renderHook } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { rendersApi } from '@/services/api';
import {
  buildDirect3DVisualPrompt,
  useDirect3DRender,
} from './useDirect3DRender';
import {
  DIRECT_3D_CAPTURE_SCHEMA,
  DIRECT_3D_CLASS_ID_MANIFEST,
  type Direct3DCaptureBundle,
} from './direct3dCapture';

vi.mock('@/services/api', () => ({
  rendersApi: { generateDirect3D: vi.fn() },
}));

const capture: Direct3DCaptureBundle = {
  schema: DIRECT_3D_CAPTURE_SCHEMA,
  beautyImageBase64: 'data:image/png;base64,beauty',
  proposalMaskBase64: 'data:image/png;base64,mask',
  classIdImageBase64: 'data:image/png;base64,classes',
  classIdManifest: DIRECT_3D_CLASS_ID_MANIFEST,
  width: 1600,
  height: 900,
  proposalPixelCount: 360_000,
  contextPixelCount: 1_080_000,
  maskCoverage: 0.25,
  classCoverage: { building: 0.18, park: 0.07 },
  fingerprint: 'd3d-1600x900-deadbeef',
};
const community3DClaims = [{
  zone_id: 'zone-building-1',
  source_hash: '1'.repeat(64),
  representation_hash: '2'.repeat(64),
  building_id: 'building-1',
}];

describe('Direct 3D render adapter', () => {
  beforeEach(() => vi.clearAllMocks());

  it('builds camera-preserving visual direction without Classic zone language', () => {
    const prompt = buildDirect3DVisualPrompt('development', 'Warm limestone.', capture);

    expect(prompt).toContain('compiled 3D buildings, parks, streets');
    expect(prompt).toContain('Keep the source camera');
    expect(prompt).toContain('building 18.0%');
    expect(prompt).toContain('Warm limestone');
    expect(prompt.toLowerCase()).not.toContain('polygon');
  });

  it('sends one isolated capture bundle and maps diagnostics into a render', async () => {
    vi.mocked(rendersApi.generateDirect3D).mockResolvedValue({
      image_base64: 'rendered',
      model: 'gpt-image-2',
      capture_fingerprint: 'a'.repeat(64),
      output_fingerprint: 'b'.repeat(64),
      diagnostics: {
        source_width: 1600,
        source_height: 900,
        normalized_width: 1600,
        normalized_height: 912,
        proposal_coverage: 0.25,
        context_coverage: 0.75,
        object_id_attached: true,
        object_id_coverage: 0.25,
        structural_edge_guide_attached: true,
        finish_fusion: {
          method: 'source-geometry-multiscale-source-phase-detail-v2',
          sigma_px: 8,
          rgb_delta_clip: 48,
          default_strength: 0.35,
          role_strengths: {
            building: 0.24,
            ground: 0.42,
            landscape: 0.5,
            street: 0.34,
            park: 0.44,
          },
          detail_fine_sigma_px: 1,
          detail_medium_sigma_px: 3.5,
          detail_correction_clip: 12,
          detail_role_gain_caps: {
            building: { fine: 1.08, medium: 1.24 },
          },
          microtexture_sigma_px: 0.8,
          microtexture_correction_clip: 3,
          microtexture_role_gain_caps: { building: 8 },
          provider_high_frequency_phase_transferred: false,
          safe_microtexture_coverage: 0.42,
          source_detail_correlation: 0.99,
          source_texture_p75: 0.2,
          fused_texture_p75: 0.6,
          texture_gain: 3,
          role_metrics: {
            building: {
              detail_fine_gain: 1.08,
              detail_medium_gain: 1.24,
              microtexture_gain: 3,
              safe_microtexture_pixels: 1_024,
              safe_microtexture_coverage: 0.42,
              source_texture_p75: 0.2,
              fused_texture_p75: 0.6,
              texture_gain: 3,
              source_detail_correlation: 0.99,
            },
          },
        },
        provider_raw_structural_edge_fidelity: {
          passed: false,
          beauty_edge_recall: 0.58,
          coarse_edge_recall: 0.44,
          semantic_edge_recall: 0.57,
          semantic_component_min_recall: 0.53,
          building_internal_edge_recall: 0.57,
        },
        structural_edge_fidelity: {
          passed: true,
          tolerance_px: 2,
          reference_edge_pixels: 12_400,
          candidate_edge_pixels: 13_100,
          beauty_edge_recall: 0.82,
          coarse_edge_pixels: 3_200,
          coarse_edge_recall: 0.78,
          semantic_edge_pixels: 1_900,
          semantic_edge_recall: 0.91,
          semantic_component_min_recall: 0.86,
          building_internal_edge_pixels: 8_700,
          building_internal_edge_recall: 0.8,
          reference_edge_p90_distance_px: 1.4,
        },
        registration: {
          method: 'identity',
          score: 0.99,
          translation_x_px: 0,
          translation_y_px: 0,
          rotation_degrees: 0,
        },
        exterior_pixel_count: 1_080_000,
        exterior_max_channel_delta: 0,
        inward_feather_px: 2,
        mask_retry_used: false,
      },
    });
    const { result } = renderHook(() => useDirect3DRender());

    const direct = await result.current.renderDirect3D(capture, {
      style: 'photorealistic',
      projectId: 'project-1',
      community3DClaims,
      residualLandscapeClaim: {
        boundary_id: 'boundary-1',
        source_hash: 'c'.repeat(64),
      },
    });

    expect(rendersApi.generateDirect3D).toHaveBeenCalledTimes(1);
    expect(rendersApi.generateDirect3D).toHaveBeenCalledWith(expect.objectContaining({
      beauty_image_base64: capture.beautyImageBase64,
      proposal_mask_base64: capture.proposalMaskBase64,
      object_id_image_base64: capture.classIdImageBase64,
      project_id: 'project-1',
      community_3d_claims: community3DClaims,
      residual_landscape_claim: {
        boundary_id: 'boundary-1',
        source_hash: 'c'.repeat(64),
      },
      capture: { width: 1600, height: 900, proposal_coverage: 0.25 },
    }));
    expect(direct.render.imageUrl).toBe('data:image/png;base64,rendered');
    expect(direct.render.providerLabel).toBe('Direct 3D · GPT Image 2');
    expect(direct.diagnostics.exterior_max_channel_delta).toBe(0);
    expect(direct.diagnostics.finish_fusion?.sigma_px).toBe(8);
    expect(direct.diagnostics.provider_raw_structural_edge_fidelity?.passed).toBe(false);
    expect(direct.diagnostics.structural_edge_fidelity?.building_internal_edge_recall).toBe(0.8);
  });

  it.each(['site-plan', 'night', 'winter', 'watercolour']) (
    'fails locally before any request for whole-frame style %s',
    async (style) => {
    const { result } = renderHook(() => useDirect3DRender());

    await expect(result.current.renderDirect3D(capture, {
      style,
      projectId: 'project-1',
      community3DClaims,
    }))
      .rejects.toThrow('must use Classic Polygons');
    expect(rendersApi.generateDirect3D).not.toHaveBeenCalled();
    },
  );
});
