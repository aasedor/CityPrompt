import { afterEach, describe, expect, it, vi } from 'vitest';
import type { Building, SiteZone } from '@/types';
import { buildingsApi, siteZonesApi } from '@/services/api';
import {
  COMMUNITY_3D_PRESENTATION_READY_EVENT,
  type Community3DPresentationReadyDetail,
} from '@/features/community3d/community3dPresentation';
import { legoAssemblyApi, type LegoAssemblyPlan } from './legoAssemblyApi';
import { analyzeLegoFootprint } from './footprintProfiles';
import {
  communityCompileOptionsForZones,
  compileBoundaryCommunity3D,
  compileMixedCommunity3D,
  deriveGroundItems,
  deriveItems,
  recipeFromPlan,
} from './communityCompiler';
import { resetProjectCommunityCompileCoordinatorForTests } from './projectCommunityCompile';

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
  resetProjectCommunityCompileCoordinatorForTests();
  vi.restoreAllMocks();
});

describe('mixed community compiler', () => {
  it('carries the AI catalogue revision into the persisted LEGO recipe only when stamped', () => {
    const fingerprint = 'a'.repeat(64);
    const aiBuilding = zone('ai-building', 'building', {
      _plan_role: 'building',
      _plan_scenario: 'community_wellbeing',
      _lego_catalog_fingerprint: fingerprint,
      development_archetype_id: 'supported_building',
    });
    const manualBuilding = zone('manual-building', 'building', {
      development_archetype_id: 'supported_building',
    });

    const aiRecipe = recipeFromPlan({ ...deriveItems([aiBuilding])[0], plan: detailedPlan });
    const manualRecipe = recipeFromPlan({
      ...deriveItems([manualBuilding])[0],
      plan: detailedPlan,
    });

    expect(aiRecipe.catalog_fingerprint).toBe(fingerprint);
    expect(manualRecipe).not.toHaveProperty('catalog_fingerprint');
  });

  it('requires detailed LEGO buildings for AI Master Plan scopes only', () => {
    const aiBuilding = zone('ai-building', 'building', {
      _plan_role: 'building',
      _plan_scenario: 'community_wellbeing',
      development_archetype_id: 'supported_building',
    });
    const manualBuilding = zone('manual-building', 'building', {
      development_archetype_id: 'supported_building',
    });

    expect(communityCompileOptionsForZones([aiBuilding])).toEqual({
      requireDetailedBuildings: true,
    });
    expect(communityCompileOptionsForZones([manualBuilding])).toEqual({
      requireDetailedBuildings: false,
    });
    expect(communityCompileOptionsForZones([manualBuilding, aiBuilding])).toEqual({
      requireDetailedBuildings: true,
    });
  });

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
        throw {
          response: {
            status: 422,
            data: { detail: { code: 'family_not_found', message: 'family unavailable' } },
          },
        };
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
    const presentationReady = vi.fn((_event: Event) => undefined);
    window.addEventListener(
      COMMUNITY_3D_PRESENTATION_READY_EVENT,
      presentationReady,
    );

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
    expect(compile.mock.calls[0][1]).toEqual([
      'supported',
      'missing',
      'park',
      'street',
    ]);
    expect(result).toMatchObject({
      detailedBuildings: 1,
      plannedMasses: 1,
      parks: 1,
      streets: 1,
    });
    expect(progress[0]).toBe('0/2');
    expect(progress[progress.length - 1]).toBe('2/2');
    expect(presentationReady).toHaveBeenCalledTimes(1);
    expect(
      (presentationReady.mock.calls[0][0] as CustomEvent<Community3DPresentationReadyDetail>)
        .detail.zoneIds,
    ).toEqual([
      'supported',
      'missing',
      'park',
      'street',
    ]);
    window.removeEventListener(
      COMMUNITY_3D_PRESENTATION_READY_EVENT,
      presentationReady,
    );
  });

  it('refetches, replans, and retries once when a source revision changes during preparation', async () => {
    const originalBuilding = zone('changing-building', 'building', {
      _plan_role: 'building',
      development_archetype_id: 'supported_building',
      floors: 5,
    });
    const originalPark = zone('changing-park', 'green_space', {
      _plan_role: 'open_space',
      green_space_archetype_id: 'neighborhood_park',
    });
    const refreshedBuilding = {
      ...originalBuilding,
      updated_at: '2026-08-14T12:05:00Z',
      properties: { ...originalBuilding.properties, floors: 8 },
    };
    const refreshedPark = {
      ...originalPark,
      updated_at: '2026-08-14T12:05:01Z',
    };
    const plan = vi.spyOn(legoAssemblyApi, 'plan').mockResolvedValue(detailedPlan);
    const compile = vi.spyOn(legoAssemblyApi, 'compileCommunity')
      .mockRejectedValueOnce({
        response: {
          status: 409,
          data: {
            detail: 'A Community 3D source zone changed while its 3D recipe was being prepared; refresh and retry.',
          },
        },
      })
      .mockResolvedValueOnce({
        status: 'compiled',
        compiled_at: '2026-08-14T12:06:00Z',
        counts: { building: 1, park: 1, street: 0 },
        items: [
          { zone_id: refreshedBuilding.id, kind: 'building', building_id: 'b-1', building_created: false, generator: 'lego_assembly' },
          { zone_id: refreshedPark.id, kind: 'park', building_id: null, building_created: false, generator: 'park_kit' },
        ],
      });
    const list = vi.spyOn(siteZonesApi, 'list').mockResolvedValue([
      refreshedBuilding,
      refreshedPark,
    ]);

    await expect(compileMixedCommunity3D([originalBuilding, originalPark])).resolves.toMatchObject({
      detailedBuildings: 1,
      parks: 1,
    });

    expect(list).toHaveBeenCalledOnce();
    expect(plan).toHaveBeenCalledTimes(2);
    expect(plan).toHaveBeenLastCalledWith(expect.objectContaining({ target_floors: 8 }));
    expect(compile).toHaveBeenCalledTimes(2);
    expect(compile.mock.calls[1][0]).toEqual([
      expect.objectContaining({
        zone_id: refreshedBuilding.id,
        source_updated_at: refreshedBuilding.updated_at,
      }),
      { zone_id: refreshedPark.id, source_updated_at: refreshedPark.updated_at },
    ]);
  });

  it('does not retry a catalogue-integrity conflict as a source refresh', async () => {
    const building = zone('catalogue-conflict', 'building', {
      _plan_role: 'building',
      development_archetype_id: 'supported_building',
      floors: 5,
    });
    vi.spyOn(legoAssemblyApi, 'plan').mockResolvedValue(detailedPlan);
    vi.spyOn(legoAssemblyApi, 'compileCommunity').mockRejectedValue({
      response: {
        status: 409,
        data: { detail: 'The executable LEGO catalogue changed after this AI Master Plan was created.' },
      },
    });
    const list = vi.spyOn(siteZonesApi, 'list');

    await expect(compileMixedCommunity3D([building])).rejects.toMatchObject({
      response: { status: 409 },
    });
    expect(list).not.toHaveBeenCalled();
  });

  it('keeps the complete visible scope when Complete compiles only unfinished items', async () => {
    const alreadyCompiled = zone('compiled-building', 'building', {
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
    const unfinishedPark = zone('unfinished-park', 'green_space', {
      _plan_role: 'open_space',
      green_space_archetype_id: 'neighborhood_park',
    });
    const compile = vi.spyOn(legoAssemblyApi, 'compileCommunity').mockResolvedValue({
      status: 'compiled',
      compiled_at: '2026-07-18T00:00:00Z',
      counts: { building: 0, park: 1, street: 0 },
      items: [{
        zone_id: unfinishedPark.id,
        kind: 'park',
        building_id: null,
        building_created: false,
        generator: 'park_kit',
      }],
    });

    await compileMixedCommunity3D(
      [unfinishedPark],
      undefined,
      { scopeZoneIds: [alreadyCompiled.id, unfinishedPark.id] },
    );

    expect(compile).toHaveBeenCalledWith(
      [{ zone_id: unfinishedPark.id, source_updated_at: unfinishedPark.updated_at }],
      [alreadyCompiled.id, unfinishedPark.id],
    );
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

  it('routes a Site Boundary through fresh scoped LEGO Community 3D data, never legacy bulk Meshy', async () => {
    const boundaryId = 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa';
    const supported = zone('supported', 'building', {
      _plan_role: 'building',
      development_archetype_id: 'supported_building',
      floors: 5,
    });
    const park = zone('park', 'green_space', {
      _plan_role: 'open_space',
      green_space_archetype_id: 'neighborhood_park',
    });
    const unrelated = zone('outside-boundary', 'building', {
      _plan_role: 'building',
      development_archetype_id: 'outside_building',
    });
    vi.spyOn(siteZonesApi, 'list').mockResolvedValue([supported, park, unrelated]);
    vi.spyOn(siteZonesApi, 'getBoundaryAnalysis').mockResolvedValue({
      boundary_zone_id: boundaryId,
      contained_zones: [supported, park].map((item) => ({
        id: item.id,
        name: item.name,
        zone_type: item.zone_type,
        color: item.color,
        properties: item.properties ?? {},
        area_m2: 100,
      })),
      zone_summary: { building: 1, green_space: 1 },
      total_contained: 2,
      osm_context: {},
    });
    const legacyBulkMeshy = vi.spyOn(siteZonesApi, 'generateForBoundary');
    const listBuildings = vi.spyOn(buildingsApi, 'list').mockResolvedValue([]);
    vi.spyOn(legoAssemblyApi, 'plan').mockResolvedValue(detailedPlan);
    const compile = vi.spyOn(legoAssemblyApi, 'compileCommunity').mockResolvedValue({
      status: 'compiled',
      compiled_at: '2026-07-21T00:00:00Z',
      counts: { building: 1, park: 1, street: 0 },
      items: [
        { zone_id: supported.id, kind: 'building', building_id: 'b-1', building_created: true, generator: 'lego_assembly' },
        { zone_id: park.id, kind: 'park', building_id: null, building_created: false, generator: 'park_kit' },
      ],
    });

    const result = await compileBoundaryCommunity3D('project-1', boundaryId);

    expect(siteZonesApi.list).toHaveBeenCalledWith('project-1');
    expect(siteZonesApi.getBoundaryAnalysis).toHaveBeenCalledWith(boundaryId);
    expect(listBuildings).not.toHaveBeenCalled();
    expect(legacyBulkMeshy).not.toHaveBeenCalled();
    expect(compile).toHaveBeenCalledWith([
      expect.objectContaining({
        zone_id: supported.id,
        recipe: expect.objectContaining({ module_family: 'supported-family' }),
      }),
      { zone_id: park.id, source_updated_at: park.updated_at },
    ], [supported.id, park.id], boundaryId);
    expect(compile.mock.calls[0][0]).not.toEqual(
      expect.arrayContaining([expect.objectContaining({ zone_id: unrelated.id })]),
    );
    expect(result).toMatchObject({ detailedBuildings: 1, plannedMasses: 0, parks: 1 });
  });

  it('plans a saved one-building preview from its linked Building footprint', async () => {
    const boundaryId = 'bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb';
    const previewBuildingId = 'cccccccc-cccc-4ccc-8ccc-cccccccccccc';
    const previewZone = zone('preview-parcel', 'building', {
      _plan_role: 'building',
      development_archetype_id: 'supported_building',
      floors: 5,
      _saved_layout: {
        buildings: [{ width_m: 40, depth_m: 30, rotation_deg: 18 }],
        roads: [],
        green_spaces: [],
        layout_strategy: 'previewed_single_building',
      },
    });
    previewZone.building_id = previewBuildingId;
    previewZone.building_ids = [previewBuildingId];
    const originalParcel = previewZone.coordinates.map((point) => [...point]);
    const footprint = [
      [-114.07072, 51.04124],
      [-114.07012, 51.04144],
      [-114.07028, 51.04176],
      [-114.07088, 51.04156],
    ];
    const expected = analyzeLegoFootprint(footprint);
    expect(expected).not.toBeNull();

    vi.spyOn(siteZonesApi, 'list').mockResolvedValue([previewZone]);
    vi.spyOn(siteZonesApi, 'getBoundaryAnalysis').mockResolvedValue({
      boundary_zone_id: boundaryId,
      contained_zones: [{
        id: previewZone.id,
        name: previewZone.name,
        zone_type: previewZone.zone_type,
        color: previewZone.color,
        properties: previewZone.properties ?? {},
        area_m2: 1_000,
      }],
      zone_summary: { building: 1 },
      total_contained: 1,
      osm_context: {},
    });
    const linkedBuilding = {
      id: previewBuildingId,
      project_id: previewZone.project_id,
      footprint_coordinates: footprint,
      rotation_degrees: 18,
      created_at: '2026-07-21T00:00:00Z',
    } satisfies Building;
    const listBuildings = vi.spyOn(buildingsApi, 'list').mockResolvedValue([linkedBuilding]);
    const plan = vi.spyOn(legoAssemblyApi, 'plan').mockImplementation(async (request) => ({
      ...detailedPlan,
      target: {
        width_m: request.target_width_m,
        depth_m: request.target_depth_m,
        floors: request.target_floors,
        footprint_profile: request.footprint_profile,
      },
    }));
    const compile = vi.spyOn(legoAssemblyApi, 'compileCommunity').mockResolvedValue({
      status: 'compiled',
      compiled_at: '2026-07-21T00:00:00Z',
      counts: { building: 1, park: 0, street: 0 },
      items: [{
        zone_id: previewZone.id,
        kind: 'building',
        building_id: previewBuildingId,
        building_created: false,
        generator: 'lego_assembly',
      }],
    });

    await compileBoundaryCommunity3D(previewZone.project_id, boundaryId);

    expect(listBuildings).toHaveBeenCalledWith(previewZone.project_id);
    expect(plan).toHaveBeenCalledWith(expect.objectContaining({
      target_width_m: expected!.width_m,
      target_depth_m: expected!.depth_m,
      footprint_profile: expected!.profile,
    }));
    expect(compile).toHaveBeenCalledWith([
      expect.objectContaining({
        zone_id: previewZone.id,
        source_updated_at: previewZone.updated_at,
        recipe: expect.objectContaining({
          target: expect.objectContaining({
            width_m: expected!.width_m,
            depth_m: expected!.depth_m,
            footprint_profile: expected!.profile,
          }),
        }),
      }),
    ], [previewZone.id], boundaryId);
    expect(previewZone.coordinates).toEqual(originalParcel);
  });

  it('fails closed when a saved one-building preview has no usable linked footprint', async () => {
    const boundaryId = 'dddddddd-dddd-4ddd-8ddd-dddddddddddd';
    const previewZone = zone('stale-preview-parcel', 'building', {
      _plan_role: 'building',
      development_archetype_id: 'supported_building',
      _saved_layout: { buildings: [{}] },
    });
    previewZone.building_id = 'missing-footprint-building';
    previewZone.building_ids = ['missing-footprint-building'];
    vi.spyOn(siteZonesApi, 'list').mockResolvedValue([previewZone]);
    vi.spyOn(siteZonesApi, 'getBoundaryAnalysis').mockResolvedValue({
      boundary_zone_id: boundaryId,
      contained_zones: [{
        id: previewZone.id,
        name: previewZone.name,
        zone_type: previewZone.zone_type,
        color: previewZone.color,
        properties: previewZone.properties ?? {},
        area_m2: 1_000,
      }],
      zone_summary: { building: 1 },
      total_contained: 1,
      osm_context: {},
    });
    vi.spyOn(buildingsApi, 'list').mockResolvedValue([{
      id: 'missing-footprint-building',
      project_id: previewZone.project_id,
      created_at: '2026-07-21T00:00:00Z',
    }]);
    const plan = vi.spyOn(legoAssemblyApi, 'plan');
    const compile = vi.spyOn(legoAssemblyApi, 'compileCommunity');

    await expect(
      compileBoundaryCommunity3D(previewZone.project_id, boundaryId),
    ).rejects.toThrow('has no current linked Building footprint');
    expect(plan).not.toHaveBeenCalled();
    expect(compile).not.toHaveBeenCalled();
  });

  it('aborts a LEGO-only boundary compile before persistence instead of downgrading a missing family', async () => {
    const missing = zone('missing', 'building', {
      _plan_role: 'building',
      development_archetype_id: 'missing_building',
    });
    vi.spyOn(legoAssemblyApi, 'plan').mockRejectedValue({
      response: {
        status: 422,
        data: { detail: { code: 'family_not_found', message: 'family unavailable' } },
      },
    });
    const compile = vi.spyOn(legoAssemblyApi, 'compileCommunity');

    await expect(compileMixedCommunity3D(
      [missing],
      undefined,
      { requireDetailedBuildings: true },
    )).rejects.toThrow('installed archetyped LEGO families');
    expect(compile).not.toHaveBeenCalled();
  });

  it('rejects a strict server response that downgrades or adds a non-LEGO building', async () => {
    const supported = zone('supported', 'building', {
      _plan_role: 'building',
      development_archetype_id: 'supported_building',
      floors: 5,
    });
    vi.spyOn(legoAssemblyApi, 'plan').mockResolvedValue(detailedPlan);
    vi.spyOn(legoAssemblyApi, 'compileCommunity').mockResolvedValue({
      status: 'compiled',
      compiled_at: '2026-07-21T00:00:00Z',
      counts: { building: 2, park: 0, street: 0 },
      items: [
        {
          zone_id: supported.id,
          kind: 'building',
          building_id: 'b-supported',
          building_created: true,
          generator: 'planned_massing',
        },
        {
          zone_id: 'unexpected-meshy-zone',
          kind: 'building',
          building_id: 'b-unexpected',
          building_created: false,
          generator: 'meshy',
        },
      ],
    });

    await expect(compileMixedCommunity3D(
      [supported],
      undefined,
      { requireDetailedBuildings: true },
    )).rejects.toThrow('invalid LEGO-only Community 3D result');
  });
});
