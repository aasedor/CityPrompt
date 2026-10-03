import { renderHook } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { rendersApi } from '@/services/api';
import {
  buildDirect3DVisualPrompt,
  DIRECT_3D_ALLOWED_STYLES,
  DIRECT_3D_DEFAULT_ART_DIRECTIONS,
  DIRECT_3D_STYLE_IDS,
  resolveDirect3DFidelityPolicy,
  resolveDirect3DPresentationMode,
  useDirect3DRender,
} from './useDirect3DRender';
import {
  buildPrompt,
  GLOBE_STYLE_PROMPTS,
  REPROJECTING_STYLES,
} from './useGlobeAIRender';
import {
  DIRECT_3D_CAPTURE_SCHEMA,
  DIRECT_3D_CLASS_ID_MANIFEST,
  type Direct3DCaptureBundle,
} from './direct3dCapture';
import type { SharedSiteGroundSnapshot } from './sharedSiteGround';

vi.mock('@/services/api', () => ({
  rendersApi: { generateDirect3D: vi.fn() },
  resolveApiFileUrl: (url: string) => url,
}));

const capture: Direct3DCaptureBundle = {
  schema: DIRECT_3D_CAPTURE_SCHEMA,
  beautyImageBase64: 'data:image/png;base64,beauty',
  proposalMaskBase64: 'data:image/png;base64,mask',
  classIdImageBase64: 'data:image/png;base64,classes',
  classIdManifest: DIRECT_3D_CLASS_ID_MANIFEST,
  instanceIdImageBase64: 'data:image/png;base64,instances',
  instanceIdManifest: {
    '#204060': {
      instance_id: 'zone:zone-building-1:building',
      semantic_class: 'building',
      zone_id: 'zone-building-1',
      building_id: 'building-1',
    },
  },
  depthImageBase64: 'data:image/png;base64,depth',
  normalImageBase64: 'data:image/png;base64,normals',
  materialIdImageBase64: 'data:image/png;base64,materials',
  materialIdManifest: {
    '#204060': {
      material_id: 'material:source-wall',
      label: 'Source wall',
      semantic_class: 'building',
      material_family_id: 'rlasm-source-wall',
      source_specific: true,
    },
  },
  camera: {
    projection: 'perspective',
    projection_matrix: Array.from({ length: 16 }, (_, index) => (index % 5 === 0 ? 1 : 0)),
    matrix_world: Array.from({ length: 16 }, (_, index) => (index % 5 === 0 ? 1 : 0)),
    position: [0, 0, 10],
    quaternion: [0, 0, 0, 1],
    near: 0.1,
    far: 10_000,
    fov: 50,
    aspect: 16 / 9,
    zoom: 1,
  },
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

const reprojectStyles = [
  'isometric',
  'site-plan',
  'site-plan-photo',
  'site-plan-watercolor',
  'blueprint',
  'clay-maquette',
] as const;

const response: Awaited<ReturnType<typeof rendersApi.generateDirect3D>> = {
  image_base64: 'rendered',
  model: 'gpt-image-2',
  outcome: 'accepted',
  warnings: [],
  capture_fingerprint: 'a'.repeat(64),
  output_fingerprint: 'b'.repeat(64),
  diagnostics: {
    processing_mode: 'scene',
    view_lock: 'camera_registered',
    context_restyled: true,
    provider_first: true,
    fidelity_policy: 'balanced',
    instance_id_attached: true,
    instance_count: 1,
    source_width: 1600,
    source_height: 900,
    normalized_width: 1600,
    normalized_height: 912,
    proposal_coverage: 0.25,
    context_coverage: 0.75,
    object_id_attached: true,
    object_id_coverage: 0.25,
    structural_edge_guide_attached: true,
    finish_fusion: null,
    provider_raw_structural_edge_fidelity: null,
    macro_design_fidelity: {
      passed: true,
      tolerance_px: 5,
      silhouette_edge_pixels: 6_400,
      silhouette_edge_recall: 0.94,
      coarse_edge_pixels: 3_200,
      coarse_edge_recall: 0.91,
      semantic_edge_pixels: 1_900,
      semantic_edge_recall: 0.9,
      evaluated_component_count: 8,
      semantic_component_min_recall: 0.84,
      reference_edge_p90_distance_px: 2.2,
      building_internal_edges_required: false,
    },
    visual_change: {
      passed: true,
      whole_frame_mean_absolute_delta: 14.2,
      proposal_mean_absolute_delta: 18.4,
      proposal_detail_delta_p75: 9.1,
      proposal_photometric_residual_p95: 12.7,
      novel_detail_edge_coverage: 0.22,
      context_mean_absolute_delta: 8.6,
      context_photometric_residual_p95: 9.2,
      context_pixel_count: 480_000,
      context_frame_top_fraction: 0.45,
      minimum_whole_frame_mean_absolute_delta: 5,
      minimum_proposal_mean_absolute_delta: 12,
      minimum_proposal_detail_delta_p75: 3,
      minimum_proposal_photometric_residual_p95: 6,
      minimum_novel_detail_edge_coverage: 0.0015,
      minimum_context_mean_absolute_delta: 4,
      minimum_context_photometric_residual_p95: 4,
      context_change_required: true,
      color_grade_only_rejected: true,
    },
    structural_edge_fidelity: null,
    registration: {
      method: 'identity',
      score: 0.96,
      score_metric: 'bidirectional-structural-edge-recall',
      photometric_score: 0.73,
      structural_context_score: 0.96,
      translation_x_px: 0,
      translation_y_px: 0,
      rotation_degrees: 0,
    },
    mask_retry_used: false,
  },
};

describe('Direct 3D presentation adapter', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(rendersApi.generateDirect3D).mockResolvedValue(response);
  });

  it('shows the paid AI image while retaining the 3D source for comparison', async () => {
    const original = { id: 'original-1', image_url: '/api/v1/files/original.png', prompt: 'finish', created_at: '2026-09-05', variant: 'provider_original' };
    vi.mocked(rendersApi.generateDirect3D).mockResolvedValue({
      ...response, outcome: 'review_required', provider_original_render: original,
      provider_image_base64: 'paid-image',
      diagnostics: { ...response.diagnostics, returned_safety_strategy: 'authoritative_source' },
    });
    const { result } = renderHook(() => useDirect3DRender());
    const direct = await result.current.renderDirect3D(capture, {
      style: 'photorealistic', projectId: 'project-1', community3DClaims,
    });
    expect(direct.providerOriginalRender).toEqual(original);
    expect(direct.render.providerLabel).toContain('Direct 3D');
    expect(direct.render.imageUrl).toBe('data:image/png;base64,paid-image');
    expect(direct.render.savedRender).toEqual(original);
    expect(direct.outputFingerprint).toBe(response.output_fingerprint);
    expect(direct.sourceImageUrl).toBe(capture.beautyImageBase64);
    expect(direct.outcome).toBe('review_required');
    expect(rendersApi.generateDirect3D).toHaveBeenCalledTimes(1);
  });

  it('still shows paid pixels when saving the original to the gallery fails', async () => {
    vi.mocked(rendersApi.generateDirect3D).mockResolvedValue({
      ...response, outcome: 'review_required', provider_original_render: null,
      provider_image_base64: 'unsaved-paid-image',
      diagnostics: { ...response.diagnostics, returned_safety_strategy: 'authoritative_source' },
    });
    const { result } = renderHook(() => useDirect3DRender());
    const direct = await result.current.renderDirect3D(capture, {
      style: 'photorealistic', projectId: 'project-1', community3DClaims,
    });
    expect(direct.render.imageUrl).toBe('data:image/png;base64,unsaved-paid-image');
    expect(direct.render.savedRender).toBeUndefined();
  });

  it('uses the same complete 22-style catalogue as Classic without changing Classic prompting', () => {
    expect(DIRECT_3D_STYLE_IDS).toHaveLength(22);
    expect(new Set(DIRECT_3D_STYLE_IDS)).toEqual(new Set(Object.keys(GLOBE_STYLE_PROMPTS)));
    expect(new Set(Object.keys(DIRECT_3D_DEFAULT_ART_DIRECTIONS)))
      .toEqual(new Set(DIRECT_3D_STYLE_IDS));
    expect(DIRECT_3D_ALLOWED_STYLES).toEqual(new Set(DIRECT_3D_STYLE_IDS));

    const classicPrompt = buildPrompt([], 'watercolour');
    expect(classicPrompt).toContain(`STYLE: ${GLOBE_STYLE_PROMPTS.watercolour}`);
    expect(classicPrompt).not.toContain('PRESENTATION MODE: SCENE');
  });

  it('maps exactly the six projection-changing styles to reproject and every other style to scene', () => {
    expect(REPROJECTING_STYLES).toEqual(new Set(reprojectStyles));
    for (const style of DIRECT_3D_STYLE_IDS) {
      expect(resolveDirect3DPresentationMode(style)).toBe(
        reprojectStyles.includes(style as (typeof reprojectStyles)[number]) ? 'reproject' : 'scene',
      );
    }
    expect(DIRECT_3D_STYLE_IDS.filter((style) => resolveDirect3DPresentationMode(style) === 'scene'))
      .toHaveLength(16);
  });

  it('keeps the selected Direct style while adding concise project-specific direction', () => {
    const custom = 'Bright softly overcast daylight. Warm limestone.';
    const prompt = buildDirect3DVisualPrompt('photorealistic', custom, capture);

    expect(prompt).toContain(DIRECT_3D_DEFAULT_ART_DIRECTIONS.photorealistic);
    expect(prompt).toContain(`PROJECT-SPECIFIC ART DIRECTION: ${custom}`);
    expect(prompt.match(/Bright softly overcast daylight/g)).toHaveLength(1);
    expect(prompt).not.toContain('Golden hour');
    expect(prompt).not.toContain('BALANCED FIDELITY');
    expect(prompt).not.toContain('Visible proposal classes');
    expect(prompt).not.toContain('DIRECT 3D STYLE ID');
  });

  it('uses a compact Direct-owned default when no custom direction is supplied', () => {
    const prompt = buildDirect3DVisualPrompt('site-plan-watercolor', undefined, capture);

    expect(prompt).toBe(DIRECT_3D_DEFAULT_ART_DIRECTIONS['site-plan-watercolor']);
    expect(prompt).toContain('hand-painted watercolour');
    expect(prompt).not.toContain('PRESENTATION MODE');
    expect(prompt).not.toContain('EXPRESSIVE FIDELITY');
  });

  it('finishes source materials without prescribing new facade or landscape elements', () => {
    const prompt = buildDirect3DVisualPrompt('photorealistic', undefined, capture);

    expect(prompt).toContain(DIRECT_3D_DEFAULT_ART_DIRECTIONS.photorealistic);
    expect(prompt).toContain('soft natural daylight');
    expect(prompt).toContain('visible material family');
    expect(prompt).toContain('restrained natural colours');
    expect(prompt).not.toContain('Golden hour');
    expect(prompt).not.toContain('ray-traced');
    expect(prompt).not.toContain('colored polygon');
    expect(prompt).toContain('footprint, height and roof massing');
    expect(buildDirect3DVisualPrompt('photorealistic', undefined, capture, 'precise')).toContain('openings and roof geometry');
    expect(prompt).not.toContain('floor-to-ceiling');
    expect(prompt).not.toContain('Add realistic public-realm activity');
  });

  it.each(['gpt-image-2.5-flare', 'gpt-image-2.5-sunburst'] as const)('forwards %s with the same geometry controls and reports the actual model', async (model) => {
    vi.mocked(rendersApi.generateDirect3D).mockResolvedValue({ ...response, model });
    const { result } = renderHook(() => useDirect3DRender());
    const direct = await result.current.renderDirect3D(capture, {
      style: 'photorealistic', model, projectId: 'project-1', community3DClaims,
    });
    expect(rendersApi.generateDirect3D).toHaveBeenCalledWith(expect.objectContaining({
      model, beauty_image_base64: capture.beautyImageBase64,
      proposal_mask_base64: capture.proposalMaskBase64,
      depth_image_base64: capture.depthImageBase64,
      normal_image_base64: capture.normalImageBase64,
      instance_id_manifest: capture.instanceIdManifest,
    }));
    expect(direct.render.model).toBe(model);
    expect(direct.render.providerLabel).toContain(model.endsWith('flare') ? 'Flare' : 'Sunburst');
    expect(rendersApi.generateDirect3D).toHaveBeenCalledTimes(1);
  });

  it('keeps missing connections and hidden facilities absent even after custom directions', () => {
    const prompt = buildDirect3DVisualPrompt('watercolour', 'Make this a lively park.', capture);
    expect(prompt.indexOf('do not invent connecting sidewalks')).toBeGreaterThan(prompt.indexOf('Make this a lively park.'));
    expect(prompt).toContain('Keep cropped and occluded elements cropped and occluded');
    expect(prompt).toContain('never build a new surface for them');
  });

  it.each(['photomontage', 'survey'])('keeps %s usable from a street camera without prescribing an aerial viewpoint', (style) => {
    const prompt = buildDirect3DVisualPrompt(style, 'Do not add people. Do not add vehicles.', capture);
    expect(prompt).not.toMatch(/drone photograph|aerial survey photograph/i);
    expect(prompt).toContain('Do not add people. Do not add vehicles.');
    expect(prompt).toContain('Keep cropped and occluded elements cropped and occluded');
  });

  it.each(['photomontage', 'development', 'atmospheric', 'winter', 'night'])('does not let the %s preset request new activity or site furniture', (style) => {
    const direction = DIRECT_3D_DEFAULT_ART_DIRECTIONS[style];
    expect(direction).not.toMatch(/pedestrians|cyclists?|cafe activity|moving cars|street life|freshly landscaped|headlight|taillight/i);
    const prompt = buildDirect3DVisualPrompt(style, undefined, capture);
    expect(prompt).toContain('do not invent connecting sidewalks');
  });

  it('describes the illustrative medium without asking to simplify the authored geometry', () => {
    const watercolour = buildDirect3DVisualPrompt('watercolour', undefined, capture);
    expect(watercolour).toContain('transparent overlapping washes');
    expect(watercolour).toContain('pigment granulation');
    expect(watercolour).toContain('roof profiles, openings and path edges');
    expect(watercolour).toContain('rather than a photograph with a paper-texture filter');
    const print = buildDirect3DVisualPrompt('risograph', undefined, capture);
    expect(print).toContain('Keep structural contours registered');
  });

  it('separates aesthetic style from the default fidelity policy', () => {
    expect(resolveDirect3DFidelityPolicy('survey')).toBe('balanced');
    expect(resolveDirect3DFidelityPolicy('documentary')).toBe('balanced');
    expect(resolveDirect3DFidelityPolicy('photorealistic')).toBe('balanced');
    expect(resolveDirect3DFidelityPolicy('winter')).toBe('balanced');
    expect(resolveDirect3DFidelityPolicy('watercolour')).toBe('expressive');
    expect(resolveDirect3DFidelityPolicy('isometric')).toBe('expressive');
    expect(resolveDirect3DFidelityPolicy('site-plan-photo')).toBe('expressive');
  });

  it('sends one request with the style, presentation mode and full capture contract', async () => {
    const { result } = renderHook(() => useDirect3DRender());

    const direct = await result.current.renderDirect3D(capture, {
      style: 'photorealistic',
      customPrompt: 'Natural spring planting.',
      projectId: 'project-1',
      community3DClaims,
      publicRealmContext: 'PUBLIC-REALM EDGE COORDINATION:\n- park touches Main Street.',
      residualLandscapeClaim: {
        boundary_id: 'boundary-1',
        source_hash: 'c'.repeat(64),
      },
    });

    expect(rendersApi.generateDirect3D).toHaveBeenCalledTimes(1);
    expect(rendersApi.generateDirect3D).toHaveBeenCalledWith(expect.objectContaining({
      add_people: false,
      add_vehicles: false,
      beauty_image_base64: capture.beautyImageBase64,
      proposal_mask_base64: capture.proposalMaskBase64,
      object_id_image_base64: capture.classIdImageBase64,
      instance_id_image_base64: capture.instanceIdImageBase64,
      instance_id_manifest: capture.instanceIdManifest,
      style: 'photorealistic',
      fidelity_policy: 'balanced',
      presentation_mode: 'scene',
      project_id: 'project-1',
      community_3d_claims: community3DClaims,
      residual_landscape_claim: {
        boundary_id: 'boundary-1',
        source_hash: 'c'.repeat(64),
      },
      capture: { width: 1600, height: 900, proposal_coverage: 0.25 },
    }));
    expect(vi.mocked(rendersApi.generateDirect3D).mock.calls[0][0].prompt)
      .toContain('Natural spring planting.');
    expect(vi.mocked(rendersApi.generateDirect3D).mock.calls[0][0].prompt)
      .toContain('park touches Main Street');
    expect(direct.render.imageUrl).toBe('data:image/png;base64,rendered');
    expect(direct.diagnostics.provider_first).toBe(true);
    expect(direct.diagnostics.macro_design_fidelity?.silhouette_edge_recall).toBe(0.94);
    expect(direct.outcome).toBe('accepted');
    expect(direct.sourceImageUrl).toBe(capture.beautyImageBase64);
  });

  it('sends explicit presentation selections without changing the authoritative camera', async () => {
    const { result } = renderHook(() => useDirect3DRender());
    await result.current.renderDirect3D(capture, {style:'atmospheric', projectId:'project-1', community3DClaims, addPeople:true, addVehicles:false});
    expect(rendersApi.generateDirect3D).toHaveBeenCalledWith(expect.objectContaining({add_people:true, add_vehicles:false, camera:capture.camera, presentation_mode:'scene'}));
  });

  it.each(['precise', 'balanced', 'expressive'] as const)('conditions %s scene requests without changing their source controls', async (fidelityPolicy) => {
    const { result } = renderHook(() => useDirect3DRender());
    const references = [{ image_base64: 'catalogue-photo', label: 'Different porch and roof', zone_ids: ['zone-1'] }];
    await result.current.renderDirect3D(capture, {
      style: 'photorealistic', projectId: 'project-1', community3DClaims,
      fidelityPolicy, archetypeReferences: references,
    });
    const request = vi.mocked(rendersApi.generateDirect3D).mock.calls[0][0];
    expect(request.archetype_references).toBeUndefined();
    expect(request.beauty_image_base64).toBe(capture.beautyImageBase64);
    expect(request.instance_id_manifest).toEqual(capture.instanceIdManifest);
    expect(request.depth_image_base64).toBe(capture.depthImageBase64);
    expect(references).toHaveLength(1);
  });

  it('retains design references for an explicit projection change', async () => {
    const { result } = renderHook(() => useDirect3DRender());
    const references = [{ image_base64: 'catalogue-photo', label: 'Exact facade', zone_ids: ['zone-1'] }];
    await result.current.renderDirect3D(capture, {
      style: 'isometric', projectId: 'project-1', community3DClaims,
      archetypeReferences: references,
    });
    expect(vi.mocked(rendersApi.generateDirect3D).mock.calls[0][0].archetype_references).toEqual(references);
  });

  it('submits the frozen park access snapshot captured with the image for server revision validation', async () => {
    const snapshot = { version: 1 as const, sourceSignature: 'pac1-12345678',
      eligibleStreetZoneIds: [],
      settings: { maxGapM: 8, pathWidthM: 2.2, obstacleClearanceM: 0.25, maxConnections: 2, gridStepM: 2 },
      sources: [{ zoneId: 'zone-building-1', updatedAt: '2026-09-04T18:00:00Z', geometrySignature: 'pac1-abcdef12' }],
      parks: [] };
    const { result } = renderHook(() => useDirect3DRender());
    await result.current.renderDirect3D({ ...capture, parkAccessSnapshot: snapshot }, {
      style: 'photorealistic', projectId: 'project-1', community3DClaims,
    });
    expect(rendersApi.generateDirect3D).toHaveBeenCalledWith(expect.objectContaining({ park_access_snapshot: snapshot }));
  });

  it('submits the exact measured ground captured with the scene', async () => {
    const snapshot: SharedSiteGroundSnapshot = {
      version: 1, source: 'google_3d_tiles', verticalReference: 'WGS84_ellipsoid',
      boundaryId: 'site-1', boundaryUpdatedAt: '2026-09-04T18:00:00Z',
      boundaryCoordinates: [[0, 0], [.0001, 0], [.0001, .0001], [0, .0001]],
      sourceSignature: 'ssg1-source', signature: 'ssg1-measured',
      grid: { west: 0, south: 0, rows: 2, columns: 2, stepLng: .0001, stepLat: .0001 },
      heights: [1025.1, 1025.2, 1025.3, 1025.4],
      quality: { sampleCount: 4, stablePasses: 2, maxPassDeltaM: .001, maxSlope: .03, maxLocalResidualM: 0 },
    };
    const { result } = renderHook(() => useDirect3DRender());
    await result.current.renderDirect3D({ ...capture, sharedGroundSnapshot: snapshot }, {
      style: 'photorealistic', projectId: 'project-1', community3DClaims,
    });
    expect(rendersApi.generateDirect3D).toHaveBeenCalledWith(expect.objectContaining({ shared_ground_snapshot: snapshot }));
  });

  it('accepts every catalogue style and sends its exact deterministic mode and Direct default', async () => {
    const { result } = renderHook(() => useDirect3DRender());

    for (const style of DIRECT_3D_STYLE_IDS) {
      await result.current.renderDirect3D(capture, {
        style,
        projectId: 'project-1',
        community3DClaims,
      });
    }

    expect(rendersApi.generateDirect3D).toHaveBeenCalledTimes(22);
    vi.mocked(rendersApi.generateDirect3D).mock.calls.forEach(([request], index) => {
      const style = DIRECT_3D_STYLE_IDS[index];
      expect(request.style).toBe(style);
      expect(request.presentation_mode).toBe(resolveDirect3DPresentationMode(style));
      expect(request.fidelity_policy).toBe(resolveDirect3DFidelityPolicy(style));
      expect(request.presentation_mode).not.toBe('source_anchored');
      expect(request.prompt).toContain(DIRECT_3D_DEFAULT_ART_DIRECTIONS[style]);
      expect(request.prompt.includes('Keep cropped and occluded elements cropped and occluded'))
        .toBe(resolveDirect3DPresentationMode(style) === 'scene');
    });
  });

  it('rejects only unknown style identifiers before spending a call', async () => {
    const { result } = renderHook(() => useDirect3DRender());

    await expect(result.current.renderDirect3D(capture, {
      style: 'not-a-style',
      projectId: 'project-1',
      community3DClaims,
    })).rejects.toThrow('Unknown Direct 3D style');
    expect(rendersApi.generateDirect3D).not.toHaveBeenCalled();
  });
});
