import { afterEach, describe, expect, it, vi } from 'vitest';
import {
  legoAssemblyApi,
  type Community3DCompileResponse,
  type LegoAssemblyRecipe,
} from './legoAssemblyApi';
import {
  compileProjectCommunity3D,
  resetProjectCommunityCompileCoordinatorForTests,
} from './projectCommunityCompile';

const response: Community3DCompileResponse = {
  status: 'compiled',
  compiled_at: '2026-08-14T12:00:00Z',
  counts: { building: 1, park: 1, street: 0 },
  items: [
    {
      zone_id: 'building-1',
      kind: 'building',
      building_id: 'building-record-1',
      building_created: true,
      generator: 'lego_assembly',
    },
    {
      zone_id: 'park-1',
      kind: 'park',
      building_id: null,
      building_created: false,
      generator: 'park_kit',
    },
  ],
};

const sourceItems = [
  { zone_id: 'building-1', source_updated_at: '2026-08-14T11:00:00Z' },
  { zone_id: 'park-1', source_updated_at: '2026-08-14T11:00:01Z' },
];

const detailedRecipe: LegoAssemblyRecipe = {
  schema_version: 1,
  module_family: 'courtyard-family',
  reuse_keys: ['courtyard-base'],
  target: { width_m: 24, depth_m: 18, floors: 4 },
  instances: [],
};

const equivalentDetailedRecipe: LegoAssemblyRecipe = {
  instances: [],
  target: { floors: 4, depth_m: 18, width_m: 24 },
  reuse_keys: ['courtyard-base'],
  module_family: 'courtyard-family',
  schema_version: 1,
};

const sourceItemsWithRecipe = [
  { ...sourceItems[0], recipe: detailedRecipe },
  sourceItems[1],
];

afterEach(() => {
  resetProjectCommunityCompileCoordinatorForTests();
  vi.restoreAllMocks();
});

describe('project Community 3D compile coordination', () => {
  it('joins duplicate in-flight submissions from separate mounted components', async () => {
    let resolveCompile: ((value: Community3DCompileResponse) => void) | undefined;
    const compile = vi.spyOn(legoAssemblyApi, 'compileCommunity').mockImplementation(() => (
      new Promise((resolve) => {
        resolveCompile = resolve;
      })
    ));

    const first = compileProjectCommunity3D(
      'project-1',
      sourceItemsWithRecipe,
      ['building-1', 'park-1', 'park-1'],
      'boundary-1',
    );
    const second = compileProjectCommunity3D(
      'project-1',
      [sourceItems[1], { ...sourceItems[0], recipe: equivalentDetailedRecipe }],
      ['park-1', 'building-1'],
      'boundary-1',
    );

    expect(compile).toHaveBeenCalledTimes(1);
    resolveCompile?.(response);
    await expect(first).resolves.toEqual(response);
    await expect(second).resolves.toEqual(response);
    expect(compile).toHaveBeenCalledTimes(1);
  });

  it('reuses a recent successful source snapshot instead of sending a stale second POST', async () => {
    const compile = vi.spyOn(legoAssemblyApi, 'compileCommunity').mockResolvedValue(response);

    await compileProjectCommunity3D(
      'project-1',
      sourceItemsWithRecipe,
      ['building-1', 'park-1'],
      'boundary-1',
    );
    await compileProjectCommunity3D(
      'project-1',
      [sourceItems[1], { ...sourceItems[0], recipe: equivalentDetailedRecipe }],
      ['park-1', 'building-1', 'building-1'],
      'boundary-1',
    );

    expect(compile).toHaveBeenCalledTimes(1);
  });

  it('does not coalesce requests that carry a different building recipe', async () => {
    const compile = vi.spyOn(legoAssemblyApi, 'compileCommunity').mockResolvedValue(response);
    const alternateRecipe: LegoAssemblyRecipe = {
      ...detailedRecipe,
      module_family: 'perimeter-block-family',
    };

    await compileProjectCommunity3D('project-1', sourceItemsWithRecipe);
    await compileProjectCommunity3D('project-1', [
      { ...sourceItems[0], recipe: alternateRecipe },
      sourceItems[1],
    ]);

    expect(compile).toHaveBeenCalledTimes(2);
  });

  it('does not coalesce requests that carry a different scope or boundary', async () => {
    const compile = vi.spyOn(legoAssemblyApi, 'compileCommunity').mockResolvedValue(response);

    await compileProjectCommunity3D(
      'project-1',
      sourceItems,
      ['building-1', 'park-1'],
      'boundary-1',
    );
    await compileProjectCommunity3D(
      'project-1',
      sourceItems,
      ['building-1', 'park-1', 'street-1'],
      'boundary-1',
    );
    await compileProjectCommunity3D(
      'project-1',
      sourceItems,
      ['building-1', 'park-1', 'street-1'],
      'boundary-2',
    );

    expect(compile).toHaveBeenCalledTimes(3);
  });

  it('keeps an omitted scope distinct from an explicitly empty scope', async () => {
    const compile = vi.spyOn(legoAssemblyApi, 'compileCommunity').mockResolvedValue(response);

    await compileProjectCommunity3D('project-1', sourceItems);
    await compileProjectCommunity3D('project-1', sourceItems, []);

    expect(compile).toHaveBeenCalledTimes(2);
  });

  it('isolates identical request identities between projects', async () => {
    const compile = vi.spyOn(legoAssemblyApi, 'compileCommunity').mockResolvedValue(response);

    await compileProjectCommunity3D('project-1', sourceItems);
    await compileProjectCommunity3D('project-2', sourceItems);

    expect(compile).toHaveBeenCalledTimes(2);
  });

  it('clears a failed request so the same project snapshot can be retried', async () => {
    const compile = vi.spyOn(legoAssemblyApi, 'compileCommunity')
      .mockRejectedValueOnce(new Error('connection lost'))
      .mockResolvedValueOnce(response);

    const first = compileProjectCommunity3D('project-1', sourceItems);
    const duplicate = compileProjectCommunity3D('project-1', [...sourceItems].reverse());
    expect(duplicate).toBe(first);
    const attempts = await Promise.allSettled([first, duplicate]);
    expect(attempts.map((attempt) => attempt.status)).toEqual(['rejected', 'rejected']);

    await expect(compileProjectCommunity3D('project-1', sourceItems)).resolves.toEqual(response);
    expect(compile).toHaveBeenCalledTimes(2);
  });

  it('allows a legitimate rebuild after refetch supplies newer zone revisions', async () => {
    const compile = vi.spyOn(legoAssemblyApi, 'compileCommunity').mockResolvedValue(response);

    await compileProjectCommunity3D('project-1', sourceItems, ['building-1', 'park-1']);
    await compileProjectCommunity3D('project-1', sourceItems.map((item) => ({
      ...item,
      source_updated_at: '2026-08-14T12:01:00Z',
    })), ['building-1', 'park-1']);

    expect(compile).toHaveBeenCalledTimes(2);
  });
});
