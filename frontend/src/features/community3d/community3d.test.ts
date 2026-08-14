import { describe, expect, it } from 'vitest';
import type { Building, SiteZone } from '@/types';
import {
  filterBuildingsForVisibleCommunity3DScope,
  getCommunity3DCaptureClaims,
  getCommunity3DBuildingSourceZoneId,
  getCommunity3DMeta,
  getCurrentCommunity3DBuildingIds,
  hasCommunity3DSourceFingerprint,
  hasExecutablePublicRealmRecipe,
  isCurrentCommunity3DBuildingRepresentation,
  resolveCommunity3DAction,
  resolveCommunity3DKind,
  selectCommunity3DCompileZones,
  shouldMaskCommunityGroundTiles,
  shouldRenderCommunityGround,
  shouldRenderCommunityProps,
  withCommunity3DMeta,
} from './community3d';

function zone(zoneType: SiteZone['zone_type'], properties: Record<string, unknown> = {}): SiteZone {
  return {
    id: `zone-${zoneType}`,
    project_id: 'project-1',
    zone_type: zoneType,
    coordinates: [[-114, 51], [-113.99, 51], [-113.99, 51.01]],
    color: '#abcdef',
    properties,
    sort_order: 0,
    created_at: '2026-07-17T00:00:00Z',
    updated_at: '2026-07-17T00:00:00Z',
  };
}

const SHA_A = 'a'.repeat(64);
const SHA_B = 'b'.repeat(64);
const SHA_C = 'c'.repeat(64);

function pocketParkRecipe(): Record<string, unknown> {
  return {
    schema_version: 1,
    family_id: 'park_pocket_courtyard',
    family_version: 1,
    kind: 'park',
    generator: 'park_kit',
    archetype_id: 'urban_pocket_park',
    variant_id: 'urban_pocket_park_v0',
    profile_id: 'urban-pocket-park-v1',
    profile_version: 1,
    appearance_kit_id: 'rustic_timber_gravel_v1',
    planting_structure: 'garden_courtyard',
    component_set_ids: [
      'park_ground_program_v1',
      'landscape_instances_v1',
      'public_realm_furnishings_v1',
    ],
    terrain_policy: 'terrain_drape_and_metric_assemblies',
    target: { target_type: 'park_polygon', width_m: 30, depth_m: 30, area_m2: 900 },
    catalog_fingerprint: SHA_A,
    capability_fingerprint: SHA_B,
    recipe_hash: SHA_C,
  };
}

function localStreetRecipe(): Record<string, unknown> {
  return {
    schema_version: 1,
    family_id: 'street_local_public_realm',
    family_version: 1,
    kind: 'street',
    generator: 'street_section',
    archetype_id: 'narrow_residential_street',
    variant_id: 'narrow_residential_street_v0',
    profile_id: 'narrow-residential-street-v1',
    profile_version: 1,
    appearance_kit_id: 'calgary_contemporary_native',
    component_set_ids: [
      'street_metric_bands_v1',
      'street_edges_markings_v1',
      'public_realm_furnishings_v1',
    ],
    terrain_policy: 'terrain_drape_and_metric_assemblies',
    target: { target_type: 'street_segment', row_width_m: 14, length_m: 120 },
    catalog_fingerprint: SHA_A,
    capability_fingerprint: SHA_B,
    recipe_hash: SHA_C,
  };
}

describe('community 3D plan contract', () => {
  it('shows compiled proposal buildings only with their visible source polygons', () => {
    const visible = { ...zone('building'), id: 'visible-zone', building_id: 'visible-building' };
    const hidden = { ...zone('building'), id: 'hidden-zone', building_id: 'hidden-building' };
    const compiledBuilding = (id: string, sourceZoneId: string): Building => ({
      id,
      project_id: 'project-1',
      footprint_coordinates: visible.coordinates,
      specifications: {
        community3DRepresentation: {
          schema_version: 1,
          zone_id: sourceZoneId,
          generator: 'lego_assembly',
          representation_hash: SHA_A,
          compiled_at: '2026-07-20T01:00:00Z',
        },
      },
      created_at: '2026-07-20T00:00:00Z',
    });
    const visibleBuilding = compiledBuilding('visible-building', visible.id);
    const hiddenBuilding = compiledBuilding('hidden-building', hidden.id);
    const orphanedGeneratedBuilding = compiledBuilding('orphaned-building', 'deleted-zone');
    const existingBuilding: Building = {
      id: 'existing-building',
      project_id: 'project-1',
      footprint_coordinates: visible.coordinates,
      model_url: '/existing.glb',
      created_at: '2026-07-20T00:00:00Z',
    };

    expect(getCommunity3DBuildingSourceZoneId(hiddenBuilding)).toBe(hidden.id);
    expect(filterBuildingsForVisibleCommunity3DScope(
      [visibleBuilding, hiddenBuilding, orphanedGeneratedBuilding, existingBuilding],
      [visible, hidden],
      [visible],
    )).toEqual([visibleBuilding, existingBuilding]);
  });

  it('uses legacy zone links for visibility while preserving zone-less existing buildings', () => {
    const visible = { ...zone('building'), id: 'visible-zone', building_ids: ['visible-legacy'] };
    const hidden = { ...zone('building'), id: 'hidden-zone', building_ids: ['hidden-legacy'] };
    const building = (id: string): Building => ({
      id,
      project_id: 'project-1',
      footprint_coordinates: visible.coordinates,
      created_at: '2026-07-20T00:00:00Z',
    });
    const visibleLegacy = building('visible-legacy');
    const hiddenLegacy = building('hidden-legacy');
    const existing = building('unlinked-existing');

    expect(filterBuildingsForVisibleCommunity3DScope(
      [visibleLegacy, hiddenLegacy, existing],
      [visible, hidden],
      [visible],
    )).toEqual([visibleLegacy, existing]);
  });

  it('classifies buildings, parks, and streets while excluding framework overlays', () => {
    expect(resolveCommunity3DKind(zone('building', { _plan_role: 'building' }))).toBe('building');
    expect(resolveCommunity3DKind(zone('green_space', { _plan_role: 'open_space' }))).toBe('park');
    expect(resolveCommunity3DKind(zone('road', { _plan_role: 'street' }))).toBe('street');
    expect(resolveCommunity3DKind(zone('parking'))).toBe('park');
    expect(resolveCommunity3DKind(zone('development_area', { _plan_role: 'framework_height' }))).toBeNull();
  });

  it('keeps master-plan ground as planning geometry until it is compiled', () => {
    const park = zone('green_space', { _plan_scenario: 'economic', _plan_role: 'open_space' });
    expect(shouldRenderCommunityGround(park)).toBe(false);

    const compiled = { ...park, properties: withCommunity3DMeta(park, 'park_kit', '2026-07-17T01:00:00Z') };
    expect(shouldRenderCommunityGround(compiled)).toBe(true);
    expect(getCommunity3DMeta(compiled)).toEqual(expect.objectContaining({
      kind: 'park',
      generator: 'park_kit',
      state: 'compiled',
    }));
  });

  it('keeps manual parks and streets flat until Generate 3D', () => {
    expect(shouldRenderCommunityGround(zone('road'))).toBe(false);
    expect(shouldRenderCommunityGround(zone('parking'))).toBe(false);
    expect(shouldRenderCommunityGround(zone('green_space', {
      _plan_scenario: 'climate_first',
      park_ground_texture: { document_id: 'doc-1' },
    }))).toBe(false);
  });

  it('keeps standing park props hidden until Generate 3D compiles the zone', () => {
    const park = zone('green_space', {
      green_space_archetype_id: 'reservoir_watershed_park',
      park_ground_texture: { document_id: 'rendered-ground' },
    });
    expect(shouldRenderCommunityGround(park)).toBe(false);
    expect(shouldRenderCommunityProps(park)).toBe(false);

    const compiled = {
      ...park,
      properties: withCommunity3DMeta(park, 'park_kit', '2026-07-17T01:00:00Z'),
    };
    expect(shouldRenderCommunityProps(compiled)).toBe(true);
  });

  it('replaces source tiles beneath authored park ground unless explicitly disabled', () => {
    const park = zone('green_space', {
      green_space_archetype_id: 'reservoir_watershed_park',
      park_ground_texture: { document_id: 'rendered-ground' },
    });
    const compiled = {
      ...park,
      properties: withCommunity3DMeta(park, 'park_kit', '2026-07-17T01:00:00Z'),
    };
    expect(shouldMaskCommunityGroundTiles(park)).toBe(true);
    expect(shouldMaskCommunityGroundTiles(compiled)).toBe(true);
    expect(shouldMaskCommunityGroundTiles({
      ...compiled,
      properties: { ...compiled.properties, community_3d_mask_existing_tiles: false },
    })).toBe(false);
  });

  it('keeps uncompiled park and street planning colours visible over source tiles', () => {
    expect(shouldMaskCommunityGroundTiles(zone('green_space'))).toBe(true);
    expect(shouldMaskCommunityGroundTiles(zone('road'))).toBe(true);
    expect(shouldMaskCommunityGroundTiles(zone('green_space', {
      community_3d_mask_existing_tiles: false,
    }))).toBe(false);
  });

  it('clears source tiles beneath procedural parks while compiled streets remain opt-in', () => {
    const park = zone('green_space', { green_space_archetype_id: 'neighborhood_park' });
    const compiledPark = {
      ...park,
      properties: withCommunity3DMeta(park, 'park_kit', '2026-07-17T01:00:00Z'),
    };
    expect(shouldMaskCommunityGroundTiles(compiledPark)).toBe(true);
    expect(shouldMaskCommunityGroundTiles({
      ...compiledPark,
      properties: { ...compiledPark.properties, community_3d_mask_existing_tiles: false },
    })).toBe(false);

    const street = zone('road');
    const compiledStreet = {
      ...street,
      properties: withCommunity3DMeta(street, 'street_section', '2026-07-17T01:00:00Z'),
    };
    expect(shouldMaskCommunityGroundTiles(compiledStreet)).toBe(false);
    expect(shouldMaskCommunityGroundTiles({
      ...compiledStreet,
      properties: { ...compiledStreet.properties, community_3d_mask_existing_tiles: true },
    })).toBe(true);
  });

  it('labels mixed-community work as generate, complete, or rebuild from persisted state', () => {
    const building = zone('building', { _plan_role: 'building' });
    const park = zone('green_space', { _plan_role: 'open_space' });
    const framework = zone('development_area', { _plan_role: 'framework_height' });
    expect(resolveCommunity3DAction([building, park, framework])).toBe('generate');

    const compiledPark = {
      ...park,
      properties: withCommunity3DMeta(park, 'park_kit', '2026-07-17T01:00:00Z'),
    };
    expect(resolveCommunity3DAction([building, compiledPark, framework])).toBe('complete');

    const compiledBuilding = {
      ...building,
      properties: withCommunity3DMeta(building, 'lego_assembly', '2026-07-17T01:00:00Z'),
    };
    expect(resolveCommunity3DAction([compiledBuilding, compiledPark, framework])).toBe('rebuild');
    expect(resolveCommunity3DAction([framework])).toBe('generate');
  });

  it('completes only unfinished zones while generate and rebuild own the full community', () => {
    const building = zone('building', { _plan_role: 'building' });
    const park = zone('green_space', { _plan_role: 'open_space' });
    const street = zone('road', { _plan_role: 'street' });
    const framework = zone('development_area', { _plan_role: 'framework_height' });
    const compiledPark = {
      ...park,
      properties: withCommunity3DMeta(park, 'park_kit', '2026-07-17T01:00:00Z'),
    };
    const zones = [building, compiledPark, street, framework];

    expect(selectCommunity3DCompileZones(zones, 'generate').map((item) => item.zone_type))
      .toEqual(['building', 'green_space', 'road']);
    expect(selectCommunity3DCompileZones(zones, 'complete').map((item) => item.zone_type))
      .toEqual(['building', 'road']);
    expect(selectCommunity3DCompileZones(zones, 'rebuild').map((item) => item.zone_type))
      .toEqual(['building', 'green_space', 'road']);
  });

  it('recompiles a building whose persisted compile marker outlived its model', () => {
    const building = zone('development_area', { _plan_role: 'building' });
    building.building_id = 'deleted-building';
    const compiledBuilding = {
      ...building,
      properties: withCommunity3DMeta(building, 'lego_assembly', '2026-07-17T01:00:00Z'),
    };
    const park = zone('green_space', { _plan_role: 'open_space' });
    const compiledPark = {
      ...park,
      properties: withCommunity3DMeta(park, 'park_kit', '2026-07-17T01:00:00Z'),
    };
    const availableBuildingIds = new Set<string>();

    expect(resolveCommunity3DAction(
      [compiledBuilding, compiledPark],
      availableBuildingIds,
    )).toBe('complete');
    expect(selectCommunity3DCompileZones(
      [compiledBuilding, compiledPark],
      'complete',
      availableBuildingIds,
    )).toEqual([compiledBuilding]);
  });

  it('attests only browser-executable nested recipes for AI public realm', () => {
    const aiPark = zone('green_space', {
      _plan_role: 'open_space',
      _plan_scenario: 'economic',
      green_space_archetype_id: 'urban_pocket_park',
      green_space_selected_variant_id: 'urban_pocket_park_v0',
    });
    expect(hasExecutablePublicRealmRecipe(aiPark)).toBe(false);

    const compiledPark = {
      ...aiPark,
      properties: {
        ...aiPark.properties,
        public_realm_lego: pocketParkRecipe(),
      },
    };
    expect(hasExecutablePublicRealmRecipe(compiledPark)).toBe(true);
    expect(hasExecutablePublicRealmRecipe({
      ...compiledPark,
      properties: {
        ...compiledPark.properties,
        public_realm_lego: {
          ...pocketParkRecipe(),
          family_id: 'future_park_family',
        },
      },
    })).toBe(false);

    const compiledStreet = zone('road', {
      _plan_role: 'street',
      _plan_scenario: 'economic',
      road_archetype_id: 'narrow_residential_street',
      road_selected_variant_id: 'narrow_residential_street_v0',
      public_realm_lego: localStreetRecipe(),
    });
    expect(hasExecutablePublicRealmRecipe(compiledStreet)).toBe(true);
    expect(hasExecutablePublicRealmRecipe({
      ...compiledStreet,
      properties: {
        ...compiledStreet.properties,
        public_realm_lego: { ...localStreetRecipe(), recipe_hash: 'not-a-hash' },
      },
    })).toBe(false);

    // Manual public realm without a nested V1 claim keeps the established
    // procedural Direct compatibility path.
    expect(hasExecutablePublicRealmRecipe(zone('green_space'))).toBe(true);
  });

  it('builds exact per-zone capture claims and rejects legacy or partial fingerprints', () => {
    const building = zone('building', {
      _plan_role: 'building',
      community_3d: {
        schema_version: 1,
        state: 'compiled',
        kind: 'building',
        generator: 'lego_assembly',
        compiled_at: '2026-07-20T01:00:00Z',
        source_hash: '1'.repeat(64),
        representation_hash: '2'.repeat(64),
      },
    });
    building.building_id = 'building-1';
    const buildingModel: Building = {
      id: 'building-1',
      project_id: 'project-1',
      footprint_coordinates: building.coordinates,
      specifications: {
        legoAssembly: { schema_version: 1, instances: [{ model_url: '/module.glb' }] },
        community3DRepresentation: {
          schema_version: 1,
          zone_id: building.id,
          generator: 'lego_assembly',
          representation_hash: '2'.repeat(64),
          compiled_at: '2026-07-20T01:00:00Z',
        },
      },
      created_at: '2026-07-20T00:00:00Z',
    };
    const park = zone('green_space', {
      _plan_role: 'open_space',
      community_3d: {
        schema_version: 1,
        state: 'compiled',
        kind: 'park',
        generator: 'park_kit',
        compiled_at: '2026-07-20T01:00:00Z',
        source_hash: '3'.repeat(64),
        representation_hash: '4'.repeat(64),
      },
    });

    expect(hasCommunity3DSourceFingerprint(building)).toBe(true);
    expect(isCurrentCommunity3DBuildingRepresentation(building, buildingModel)).toBe(true);
    expect([...getCurrentCommunity3DBuildingIds([building, park], [buildingModel])])
      .toEqual(['building-1']);
    expect(getCommunity3DCaptureClaims([building, park], [buildingModel])).toEqual([
      {
        zone_id: building.id,
        source_hash: '1'.repeat(64),
        representation_hash: '2'.repeat(64),
        building_id: 'building-1',
      },
      {
        zone_id: park.id,
        source_hash: '3'.repeat(64),
        representation_hash: '4'.repeat(64),
      },
    ]);
    expect(getCommunity3DCaptureClaims([{
      ...building,
      properties: {
        ...building.properties,
        community_3d: {
          ...(building.properties?.community_3d as Record<string, unknown>),
          representation_hash: undefined,
        },
      },
    }], [buildingModel])).toBeNull();
    expect(getCommunity3DCaptureClaims([building], [{
      ...buildingModel,
      specifications: {
        ...buildingModel.specifications,
        community3DRepresentation: {
          ...(buildingModel.specifications?.community3DRepresentation as Record<string, unknown>),
          representation_hash: '9'.repeat(64),
        },
      },
    }])).toBeNull();
    const legacyModel = {
      ...buildingModel,
      id: 'legacy-building',
      specifications: {
        legoAssembly: buildingModel.specifications?.legoAssembly,
      },
    } satisfies Building;
    expect(getCurrentCommunity3DBuildingIds([building], [buildingModel, legacyModel]).has('legacy-building'))
      .toBe(false);
  });
});
