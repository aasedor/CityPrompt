import { describe, expect, it } from 'vitest';
import type { SiteZone } from '@/types';
import {
  getCommunity3DMeta,
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

describe('community 3D plan contract', () => {
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

  it('preserves immediate previews for manual zones and older authored park drapes', () => {
    expect(shouldRenderCommunityGround(zone('road'))).toBe(true);
    expect(shouldRenderCommunityGround(zone('parking'))).toBe(true);
    expect(shouldRenderCommunityGround(zone('green_space', {
      _plan_scenario: 'climate_first',
      park_ground_texture: { document_id: 'doc-1' },
    }))).toBe(true);
  });

  it('keeps standing park props hidden until Generate 3D compiles the zone', () => {
    const park = zone('green_space', {
      green_space_archetype_id: 'reservoir_watershed_park',
      park_ground_texture: { document_id: 'rendered-ground' },
    });
    expect(shouldRenderCommunityGround(park)).toBe(true);
    expect(shouldRenderCommunityProps(park)).toBe(false);

    const compiled = {
      ...park,
      properties: withCommunity3DMeta(park, 'park_kit', '2026-07-17T01:00:00Z'),
    };
    expect(shouldRenderCommunityProps(compiled)).toBe(true);
  });

  it('does not cut a pale tile hole beneath public realm unless explicitly requested', () => {
    const park = zone('green_space', {
      green_space_archetype_id: 'reservoir_watershed_park',
      park_ground_texture: { document_id: 'rendered-ground' },
    });
    const compiled = {
      ...park,
      properties: withCommunity3DMeta(park, 'park_kit', '2026-07-17T01:00:00Z'),
    };
    expect(shouldMaskCommunityGroundTiles(compiled)).toBe(false);
    expect(shouldMaskCommunityGroundTiles({
      ...compiled,
      properties: { ...compiled.properties, community_3d_mask_existing_tiles: true },
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
});
