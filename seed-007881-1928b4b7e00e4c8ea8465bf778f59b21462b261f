import { afterEach, describe, expect, it, vi } from 'vitest';
import type { SiteZone } from '@/types';
import { legoAssemblyApi, type LegoAssemblyPlan } from './legoAssemblyApi';
import {
  compileMixedCommunity3D,
  deriveGroundItems,
  deriveItems,
} from './communityCompiler';

function zone(
  id: string,
  zoneType: SiteZone['zone_type'],
  properties: SiteZone['properties'],
): SiteZone {
  return {
    id,
    project_id: 'project-1',
    zone_type: zoneType,
    name: id,
    coordinates: [
      [-114.071, 51.041],
      [-114.070, 51.041],
      [-114.070, 51.042],
      [-114.071, 51.042],
    ],
    color: '#888888',
    properties,
    sort_order: 0,
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
  };
}

const detailedPlan: LegoAssemblyPlan = {
  version: 1,
  family: 'supported-family',
  archetype_id: 'supported_building',
  reuse_keys: ['supported'],
  target: { width_m: 30, depth_m: 20, floors: 5, footprint_profile: 'rectangle' },
  assembled_height_m: 18,
  instances: [{
    asset_id: 'module-1',
    asset_name: 'Typical floor',
    model_url: '/module.glb',
    family: 'supported-family',
    role: 'floor',
    level: 0,
    position: [0, 0, 0],
    rotation_degrees: 0,
    scale: [1, 1, 1],
    native_dimensions_m: [30, 3.6, 20],
  }],
  fit: { scale_x: 1, scale_y: 1, score: 1 },
};

afterEach(() => {
  vi.restoreAllMocks();
});

describe('mixed community compiler', () => {
  it('uses the drawn parcel dimensions even when catalogue footprint guidance is absent', () => {
    const parcel = zone('actual-parcel', 'building', {
      _plan_role: 'building',
      development_archetype_id: 'uncatalogued_compatibility',
      floors: 4,
    });
    parcel.coordinates = [
      [-114.05722438038991, 51.04433410248642],
      [-114.05724663936313, 51.04393660027583],
      [-114.0567468295418, 51.043917942028784],
      [-114.05670681942766, 51.04430810706922],
    ];

    const [item] = deriveItems([parcel]);

    expect(item.targets.width_m).toBeGreaterThan(43);
    expect(item.targets.width_m).toBeLessThan(46);
    expect(item.targets.depth_m).toBeGreaterThan(34);
    expect(item.targets.depth_m).toBeLessThan(38);
  });

  it('treats a deleted model with a stale compile marker as ready to place again', () => {
    const parcel = zone('deleted-model', 'building', {
      _plan_role: 'building',
      development_archetype_id: 'supported_building',
      community_3d: {
        schema_version: 1,
        state: 'compiled',
        kind: 'building',
        generator: 'lego_assembly',
        compiled_at: '2026-07-18T00:00:00Z',
      },
    });
    delete parcel.building_id;
    parcel.building_ids = ['deleted-building-id'];

    expect(deriveItems([parcel])[0].placeState).toBeUndefined();
  });

  it('shares one zone derivation across detailed buildings, missing-family massing, parks, and streets', async () => {
    const zones = [
      zone('supported', 'development_area', {
        _plan_role: 'building',
        development_archetype_id: 'supported_building',
        floors: 5,
      }),
      zone('missing', 'development_area', {
        _plan_role: 'building',
        development_archetype_id: 'missing_building',
        floors: 4,
      }),
      zone('park', 'green_space', {
        _plan_role: 'open_space',
        green_space_archetype_id: 'neighborhood_park',
      }),
      zone('street', 'road', {
        _plan_role: 'street',
        road_archetype_id: 'complete_street',
      }),
    ];
    expect(deriveItems(zones).map((item) => item.zone.id)).toEqual(['supported', 'missing']);
    expect(deriveGroundItems(zones).map((item) => item.zone.id)).toEqual(['park', 'street']);

    vi.spyOn(legoAssemblyApi, 'plan').mockImplementation(async (request) => {
      if (request.archetype_id === 'missing_building') {
        throw { response: { status: 422 }, message: 'family unavailable' };
      }
      return detailedPlan;
    });
    const compile = vi.spyOn(legoAssemblyApi, 'compileCommunity').mockResolvedValue({
      status: 'compiled',
      compiled_at: '2026-07-18T00:00:00Z',
      counts: { building: 2, park: 1, street: 1 },
      items: [
        { zone_id: 'supported', kind: 'building', building_id: 'b-1', building_created: true, generator: 'lego_assembly' },
        { zone_id: 'missing', kind: 'building', building_id: 'b-2', building_created: true, generator: 'planned_massing' },
        { zone_id: 'park', kind: 'park', building_id: null, building_created: false, generator: 'park_kit' },
        { zone_id: 'street', kind: 'street', building_id: null, building_created: false, generator: 'street_section' },
      ],
    });
    const progress: string[] = [];

    const result = await compileMixedCommunity3D(zones, ({ completed, total }) => {
      progress.push(`${completed}/${total}`);
    });

    expect(compile).toHaveBeenCalledTimes(1);
    expect(compile.mock.calls[0][0]).toEqual([
      expect.objectContaining({
        zone_id: 'supported',
        source_updated_at: '2026-01-01T00:00:00Z',
        recipe: expect.objectContaining({ module_family: 'supported-family' }),
      }),
      { zone_id: 'missing', source_updated_at: '2026-01-01T00:00:00Z' },
      { zone_id: 'park', source_updated_at: '2026-01-01T00:00:00Z' },
      { zone_id: 'street', source_updated_at: '2026-01-01T00:00:00Z' },
    ]);
    expect(result).toMatchObject({
      detailedBuildings: 1,
      plannedMasses: 1,
      parks: 1,
      streets: 1,
    });
    expect(progress[0]).toBe('0/2');
    expect(progress[progress.length - 1]).toBe('2/2');
  });

  it('aborts before the atomic save when modular planning fails unexpectedly', async () => {
    const zones = [zone('broken', 'development_area', {
      _plan_role: 'building',
      development_archetype_id: 'broken_building',
    })];
    vi.spyOn(legoAssemblyApi, 'plan').mockRejectedValue({
      response: { status: 503, data: { detail: 'planner unavailable' } },
    });
    const compile = vi.spyOn(legoAssemblyApi, 'compileCommunity');

    await expect(compileMixedCommunity3D(zones)).rejects.toThrow('planner unavailable');
    expect(compile).not.toHaveBeenCalled();
  });

  it('classifies an existing Meshy representation as a detailed building', async () => {
    const generated = zone('generated', 'building', {
      _plan_role: 'building',
      development_archetype_id: 'generated_family',
      floors: 6,
    });
    vi.spyOn(legoAssemblyApi, 'plan').mockRejectedValue({
      response: {
        status: 422,
        headers: { 'x-city-prompt-error-code': 'MODULE_FAMILY_MISSING' },
      },
    });
    vi.spyOn(legoAssemblyApi, 'compileCommunity').mockResolvedValue({
      status: 'compiled',
      compiled_at: '2026-07-18T00:00:00Z',
      counts: { building: 1, park: 0, street: 0 },
      items: [{
        zone_id: 'generated',
        kind: 'building',
        building_id: 'b-generated',
        building_created: false,
        generator: 'meshy',
      }],
    });

    const result = await compileMixedCommunity3D([generated]);

    expect(result.detailedBuildings).toBe(1);
    expect(result.plannedMasses).toBe(0);
  });

  it('probes each explicitly missing family once instead of repeating hundreds of 422s', async () => {
    const archetypeIds = [
      'vernacular_courtyard_housing',
      'new_york_walk_up_tenement',
      'new_york_corner_bodega',
      'contemporary_civic',
    ];
    const zones = archetypeIds.flatMap((archetypeId) => (
      Array.from({ length: 3 }, (_, index) => zone(`${archetypeId}-${index}`, 'building', {
        _plan_role: 'building',
        development_archetype_id: archetypeId,
        floors: 3 + index,
      }))
    ));
    const plan = vi.spyOn(legoAssemblyApi, 'plan').mockImplementation(async (request) => {
      throw {
        response: {
          status: 422,
          data: {
            detail: `No module family explicitly matches archetype '${request.archetype_id}'. `
              + 'Import that archetype/variant instead of substituting an unrelated family.',
          },
        },
      };
    });
    const compile = vi.spyOn(legoAssemblyApi, 'compileCommunity').mockImplementation(async (items) => ({
      status: 'compiled',
      compiled_at: '2026-07-18T00:00:00Z',
      counts: { building: items.length, park: 0, street: 0 },
      items: items.map((item) => ({
        zone_id: item.zone_id,
        kind: 'building' as const,
        building_id: `building-${item.zone_id}`,
        building_created: true,
        generator: 'planned_massing' as const,
      })),
    }));
    const progress: number[] = [];

    const result = await compileMixedCommunity3D(zones, ({ completed }) => {
      progress.push(completed);
    });

    expect(plan).toHaveBeenCalledTimes(archetypeIds.length);
    expect(new Set(plan.mock.calls.map(([request]) => request.archetype_id))).toEqual(
      new Set(archetypeIds),
    );
    expect(compile).toHaveBeenCalledTimes(1);
    expect(compile.mock.calls[0][0]).toHaveLength(zones.length);
    expect(compile.mock.calls[0][0].every((item) => !('recipe' in item))).toBe(true);
    expect(result.plannedMasses).toBe(zones.length);
    expect(progress[progress.length - 1]).toBe(zones.length);
  });

  it('still plans sibling footprints after a family-specific fit rejection', async () => {
    const zones = [0, 1].map((index) => zone(`fit-${index}`, 'building', {
      _plan_role: 'building',
      development_archetype_id: 'available_but_size_sensitive',
      floors: 4,
    }));
    const plan = vi.spyOn(legoAssemblyApi, 'plan')
      .mockRejectedValueOnce({
        response: {
          status: 422,
          data: { detail: 'No compatible module family found for this target footprint.' },
        },
      })
      .mockResolvedValueOnce(detailedPlan);
    const compile = vi.spyOn(legoAssemblyApi, 'compileCommunity').mockResolvedValue({
      status: 'compiled',
      compiled_at: '2026-07-18T00:00:00Z',
      counts: { building: 2, park: 0, street: 0 },
      items: [
        { zone_id: 'fit-0', kind: 'building', building_id: 'b-0', building_created: true, generator: 'planned_massing' },
        { zone_id: 'fit-1', kind: 'building', building_id: 'b-1', building_created: true, generator: 'lego_assembly' },
      ],
    });

    const result = await compileMixedCommunity3D(zones);

    expect(plan).toHaveBeenCalledTimes(2);
    expect(compile.mock.calls[0][0][0]).toEqual({
      zone_id: 'fit-0',
      source_updated_at: '2026-01-01T00:00:00Z',
    });
    expect(compile.mock.calls[0][0][1]).toEqual(
      expect.objectContaining({ zone_id: 'fit-1', recipe: expect.any(Object) }),
    );
    expect(result.detailedBuildings).toBe(1);
    expect(result.plannedMasses).toBe(1);
  });

  it('rejects invalid building footprints before any planning or persistence request', async () => {
    const invalid = zone('invalid', 'development_area', {
      _plan_role: 'building',
      development_archetype_id: 'supported_building',
    });
    invalid.coordinates = [];
    const plan = vi.spyOn(legoAssemblyApi, 'plan');
    const compile = vi.spyOn(legoAssemblyApi, 'compileCommunity');

    await expect(compileMixedCommunity3D([invalid])).rejects.toThrow('no usable map footprint');
    expect(plan).not.toHaveBeenCalled();
    expect(compile).not.toHaveBeenCalled();
  });
});
