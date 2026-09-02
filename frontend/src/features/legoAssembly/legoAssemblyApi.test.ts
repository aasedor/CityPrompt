import { describe, it, expect, vi, beforeEach } from 'vitest';
import {
  legoArchetypeContextFromZone,
  legoAssemblyApi,
  getLegoPlanningFailure,
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

  it('listModules() scopes private family readiness to the current project', async () => {
    apiGet.mockResolvedValue({ data: { modules: [] } });

    await expect(legoAssemblyApi.listModules('project-1')).resolves.toEqual([]);

    expect(apiGet).toHaveBeenCalledWith(
      '/api/v1/lego-assembly/modules',
      { params: { project_id: 'project-1' } },
    );
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
      allow_forced_fit: false,
    });

    expect(apiPost).toHaveBeenCalledWith(
      '/api/v1/lego-assembly/plan',
      expect.objectContaining({
        allow_setback: false,
        allow_forced_fit: false,
        archetype_id: 'nordic_timber_midrise',
      }),
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

  it('compileCommunity() sends the complete visible scope separately from incremental items', async () => {
    const response = {
      status: 'compiled' as const,
      compiled_at: '2026-07-17T01:00:00Z',
      counts: { building: 0, park: 1, street: 0 },
      items: [],
    };
    apiPost.mockResolvedValue({ data: response });
    const item = {
      zone_id: 'unfinished-park',
      source_updated_at: '2026-07-17T00:00:00Z',
    };

    await legoAssemblyApi.compileCommunity(
      [item],
      ['compiled-building', 'unfinished-park'],
    );

    expect(apiPost).toHaveBeenCalledWith('/api/v1/lego-assembly/place-community', {
      items: [item],
      scope_zone_ids: ['compiled-building', 'unfinished-park'],
    });
  });

  it('compileCommunity() sends a server-verifiable Site Boundary scope', async () => {
    const response = {
      status: 'compiled' as const,
      compiled_at: '2026-07-17T01:00:00Z',
      counts: { building: 1, park: 0, street: 0 },
      items: [],
    };
    apiPost.mockResolvedValue({ data: response });
    const item = {
      zone_id: 'inside-building',
      source_updated_at: '2026-07-17T00:00:00Z',
    };

    await legoAssemblyApi.compileCommunity(
      [item],
      ['inside-building'],
      'site-boundary',
    );

    expect(apiPost).toHaveBeenCalledWith('/api/v1/lego-assembly/place-community', {
      items: [item],
      scope_zone_ids: ['inside-building'],
      scope_boundary_id: 'site-boundary',
    });
  });

  it('preserves explicit empty scope and boundary values for server validation', async () => {
    apiPost.mockResolvedValue({
      data: {
        status: 'compiled',
        compiled_at: '2026-08-14T12:00:00Z',
        counts: { building: 0, park: 0, street: 0 },
        items: [],
      },
    });

    await legoAssemblyApi.compileCommunity([], [], '');

    expect(apiPost).toHaveBeenCalledWith('/api/v1/lego-assembly/place-community', {
      items: [],
      scope_zone_ids: [],
      scope_boundary_id: '',
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

describe('getLegoPlanningFailure', () => {
  it('parses structured missing and incompatible family failures', () => {
    expect(getLegoPlanningFailure({
      response: {
        status: 422,
        data: { detail: { code: 'family_not_found', message: 'No family is installed.' } },
      },
    })).toEqual({ code: 'family_not_found', message: 'No family is installed.' });

    expect(getLegoPlanningFailure({
      response: {
        status: 422,
        data: {
          detail: {
            code: 'family_incompatible',
            message: 'The installed family does not fit.',
            supported_families: [{
              family: 'industrial-brick-brewery',
              widths_m: [40],
              depths_m: [26],
              min_floors: 2,
              max_floors: 5,
            }],
          },
        },
      },
    })).toEqual(expect.objectContaining({
      code: 'family_incompatible',
      supported_families: [expect.objectContaining({ family: 'industrial-brick-brewery' })],
    }));
  });

  it('recognizes only narrow legacy planner failures and ignores unrelated 422s', () => {
    expect(getLegoPlanningFailure({
      response: { status: 422, data: { detail: 'No module family covers archetype industrial_brick_mixed_use.' } },
    })?.code).toBe('family_not_found');
    expect(getLegoPlanningFailure({
      response: { status: 422, data: { detail: 'No compatible module family found for this target.' } },
    })?.code).toBe('family_incompatible');
    expect(getLegoPlanningFailure({
      response: { status: 422, data: { detail: [{ loc: ['body'], msg: 'Invalid request' }] } },
    })).toBeNull();
  });
});

describe('legoArchetypeContextFromZone', () => {
  it('returns an empty context without properties', () => {
    expect(legoArchetypeContextFromZone(undefined)).toEqual({});
  });

  it('prefers the current parent archetype over stale generation input', () => {
    const context = legoArchetypeContextFromZone({
      development_archetype_id: 'other_id',
      generation_style_input: {
        archetypeId: 'nordic_timber_midrise',
        downstreamHints: { reuseKeys: ['timber', 'midrise', ''] },
      },
    });

    expect(context.archetype_id).toBe('other_id');
    expect(context.allow_setback).toBe(false);
    // Empty strings are filtered out.
    expect(context.reuse_keys).toEqual(['timber', 'midrise']);
  });

  it('falls back to generation input when no current selection is stored', () => {
    const context = legoArchetypeContextFromZone({
      generation_style_input: {
        archetypeId: 'nordic_timber_midrise',
      },
    });

    expect(context.archetype_id).toBe('nordic_timber_midrise');
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

  it('uses the parent generation reference after an explicit variant is cleared', () => {
    const context = legoArchetypeContextFromZone({
      development_subcategory: 'industrial_brick_mixed_use',
      development_archetype_id: 'industrial_brick_mixed_use_variant_0',
      development_selected_variant_id: undefined,
      generation_style_input: {
        archetypeId: 'industrial_brick_mixed_use_variant_0',
      },
    });

    expect(context.archetype_id).toBe('industrial_brick_mixed_use_variant_0');
    expect(context.archetype_id).not.toBe('industrial_brick_brewery');
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

  it('retains the exact architectural-clay archetype when the private family is planner-disabled', () => {
    const context = legoArchetypeContextFromZone({
      architectural_clay_archetype_id: 'amsterdam-bell-gable-house',
      architectural_clay_family: 'amsterdam-bell-gable-semantic-clay-v001',
    });

    expect(context.archetype_id).toBe('amsterdam-bell-gable-house');
    expect(context.reuse_keys).toEqual(['amsterdam-bell-gable-house']);
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
