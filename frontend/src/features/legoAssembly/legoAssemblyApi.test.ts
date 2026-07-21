import { describe, it, expect, vi, beforeEach } from 'vitest';
import {
  legoArchetypeContextFromZone,
  legoAssemblyApi,
  type LegoAssemblyRecipe,
} from './legoAssemblyApi';

const { apiGet, apiPost, apiPut, apiDelete } = vi.hoisted(() => ({
  apiGet: vi.fn(),
  apiPost: vi.fn(),
  apiPut: vi.fn(),
  apiDelete: vi.fn(),
}));

vi.mock('@/services/api', () => ({
  api: { get: apiGet, post: apiPost, put: apiPut, delete: apiDelete },
}));

const recipeFixture: LegoAssemblyRecipe = {
  schema_version: 1,
  module_family: 'nordic_timber_midrise_family',
  archetype_id: 'nordic_timber_midrise',
  reuse_keys: ['nordic_timber_midrise'],
  target: { width_m: 32, depth_m: 20, floors: 6 },
  instances: [],
  assembled_height_m: 21.4,
  fit: { scale_x: 1, scale_y: 1, score: 0.95 },
  assembled_preview_url: null,
};

describe('legoAssemblyApi', () => {
  beforeEach(() => {
    vi.resetAllMocks();
  });

  it('plan() posts the request (including allow_setback) and returns the plan', async () => {
    const plan = { version: 1, family: 'f', reuse_keys: [], target: { width_m: 1, depth_m: 1, floors: 1 }, assembled_height_m: 3, instances: [], fit: { scale_x: 1, scale_y: 1, score: 1 } };
    apiPost.mockResolvedValue({ data: plan });

    const result = await legoAssemblyApi.plan({
      target_width_m: 32,
      target_depth_m: 20,
      target_floors: 6,
      archetype_id: 'nordic_timber_midrise',
      allow_setback: false,
    });

    expect(apiPost).toHaveBeenCalledWith(
      '/api/v1/lego-assembly/plan',
      expect.objectContaining({ allow_setback: false, archetype_id: 'nordic_timber_midrise' }),
    );
    expect(result).toEqual(plan);
  });

  it('saveRecipe() posts to the building recipe endpoint and unwraps legoAssembly', async () => {
    apiPost.mockResolvedValue({ data: { status: 'saved', building_id: 'bldg-1', legoAssembly: recipeFixture } });

    const saved = await legoAssemblyApi.saveRecipe('bldg-1', recipeFixture);

    expect(apiPost).toHaveBeenCalledWith('/api/v1/lego-assembly/recipes/bldg-1', recipeFixture);
    expect(saved).toEqual(recipeFixture);
  });

  it('compileCommunity() posts the mixed plan as one transaction', async () => {
    const response = {
      status: 'compiled' as const,
      compiled_at: '2026-07-17T01:00:00Z',
      counts: { building: 1, park: 1, street: 1 },
      items: [],
    };
    apiPost.mockResolvedValue({ data: response });
    const sourceUpdatedAt = '2026-07-17T00:00:00Z';

    await expect(legoAssemblyApi.compileCommunity([
      { zone_id: 'building-1', source_updated_at: sourceUpdatedAt, recipe: recipeFixture },
      { zone_id: 'park-1', source_updated_at: sourceUpdatedAt },
      { zone_id: 'street-1', source_updated_at: sourceUpdatedAt },
    ])).resolves.toEqual(response);

    expect(apiPost).toHaveBeenCalledWith('/api/v1/lego-assembly/place-community', {
      items: [
        { zone_id: 'building-1', source_updated_at: sourceUpdatedAt, recipe: recipeFixture },
        { zone_id: 'park-1', source_updated_at: sourceUpdatedAt },
        { zone_id: 'street-1', source_updated_at: sourceUpdatedAt },
      ],
    });
  });

  it('getRecipe() unwraps legoAssembly and passes null through', async () => {
    apiGet.mockResolvedValueOnce({ data: { legoAssembly: recipeFixture } });
    await expect(legoAssemblyApi.getRecipe('bldg-1')).resolves.toEqual(recipeFixture);
    expect(apiGet).toHaveBeenCalledWith('/api/v1/lego-assembly/recipes/bldg-1');

    apiGet.mockResolvedValueOnce({ data: { legoAssembly: null } });
    await expect(legoAssemblyApi.getRecipe('bldg-1')).resolves.toBeNull();
  });

  it('clearRecipe() deletes the building recipe', async () => {
    apiDelete.mockResolvedValue({ data: { status: 'deleted' } });
    await legoAssemblyApi.clearRecipe('bldg-1');
    expect(apiDelete).toHaveBeenCalledWith('/api/v1/lego-assembly/recipes/bldg-1');
  });
});

describe('legoArchetypeContextFromZone', () => {
  it('returns an empty context without properties', () => {
    expect(legoArchetypeContextFromZone(undefined)).toEqual({});
  });

  it('prefers generation_style_input archetypeId and downstream reuse keys', () => {
    const context = legoArchetypeContextFromZone({
      development_archetype_id: 'other_id',
      generation_style_input: {
        archetypeId: 'nordic_timber_midrise',
        downstreamHints: { reuseKeys: ['timber', 'midrise', ''] },
      },
    });

    expect(context.archetype_id).toBe('nordic_timber_midrise');
    expect(context.allow_setback).toBe(false);
    // Empty strings are filtered out.
    expect(context.reuse_keys).toEqual(['timber', 'midrise']);
  });

  it('preserves an explicitly selected design variant over the parent visual reference', () => {
    const context = legoArchetypeContextFromZone({
      development_selected_variant_id: 'toronto_junction_contemporary_addition',
      development_archetype_id: 'toronto_junction_converted_industrial_variant_0',
      generation_style_input: {
        archetypeId: 'toronto_junction_converted_industrial_variant_0',
      },
    });

    expect(context.archetype_id).toBe('toronto_junction_contemporary_addition');
  });

  it('falls back to development_* fields when no generation style input exists', () => {
    const context = legoArchetypeContextFromZone({
      development_archetype_id: 'nordic_timber_midrise',
      development_subcategory: 'midrise',
      development_aesthetic_category: 'timber',
    });

    expect(context.archetype_id).toBe('nordic_timber_midrise');
    expect(context.allow_setback).toBe(false);
    expect(context.reuse_keys).toEqual(['midrise', 'timber', 'nordic_timber_midrise']);
  });

  it('allows setbacks only when the archetype grammar explicitly asks for them', () => {
    const context = legoArchetypeContextFromZone({
      generation_style_input: {
        archetypeId: 'art_deco_setback_tower',
        generationTags: ['art_deco', 'setback_tower'],
        styleProfile: { massing: 'Tower on podium with stepped setbacks' },
      },
    });

    expect(context.allow_setback).toBe(true);
  });
});
