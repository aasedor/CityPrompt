import { describe, expect, it } from 'vitest';
import type { SiteZone } from '@/types';
import {
  buildStreetNetworkPlacement,
  getCurrentStreetNetworkGroundMeta,
  getStreetNetworkStandards,
  getStreetNetworkGroundMeta,
  streetZoneSourceSignature,
  type StreetNetworkGroundTextureMeta,
} from './streetNetworkGroundTexture';

const PROJECT_ID = 'fc279bd0-8549-4607-811b-59606a2e6534';

function zone(overrides: Partial<SiteZone>): SiteZone {
  return {
    id: '110fd97c-bd94-4e0b-aff7-67ba239e531f',
    project_id: PROJECT_ID,
    zone_type: 'road',
    coordinates: [
      [-114.12, 51.027],
      [-114.119, 51.027],
      [-114.119, 51.0271],
      [-114.12, 51.0271],
    ],
    color: '#777777',
    properties: { _plan_role: 'street', width: 12, street_role: 'local' },
    sort_order: 1,
    created_at: '2026-08-04T00:00:00Z',
    updated_at: '2026-08-04T00:00:00Z',
    ...overrides,
  };
}

const boundary = zone({
  id: 'ebf8ae70-5851-493b-b197-76c70d20c376',
  zone_type: 'site_boundary',
  is_active_boundary: true,
  coordinates: [
    [-114.121, 51.0265],
    [-114.118, 51.0265],
    [-114.118, 51.028],
    [-114.121, 51.028],
  ],
  properties: {},
});

describe('connected street-network ground atlas', () => {
  it('places one north-up atlas against the active boundary at a 90% fit', () => {
    const placement = buildStreetNetworkPlacement([boundary, zone({})]);
    expect(placement).not.toBeNull();
    expect(placement?.road_zone_ids).toEqual(['110fd97c-bd94-4e0b-aff7-67ba239e531f']);
    expect(placement?.bbox).toEqual({
      west: -114.121,
      south: 51.0265,
      east: -114.118,
      north: 51.028,
    });
    expect(placement?.uv_rect.u0).toBeCloseTo(0.05, 6);
    expect(placement?.uv_rect.u1).toBeCloseTo(0.95, 6);
    expect(placement?.uv_rect.v0).toBeGreaterThan(0.05);
    expect(placement?.uv_rect.v1).toBeLessThan(0.95);
  });

  it('invalidates only when the owning road geometry or design inputs change', () => {
    const road = zone({});
    const placement = buildStreetNetworkPlacement([boundary, road]);
    expect(placement).not.toBeNull();
    const meta: StreetNetworkGroundTextureMeta = {
      schema_version: 1,
      url: '/api/v1/documents/atlas/file',
      document_id: 'atlas',
      bbox: placement!.bbox,
      uv_rect: placement!.uv_rect,
      size_m: placement!.size_m,
      model: 'gpt-image-2',
      provider: 'openai',
      generated_at: '2026-08-04T00:00:00Z',
      source_signature: placement!.source_signature,
      zone_source_signature: streetZoneSourceSignature(road),
      boundary_zone_id: boundary.id,
      road_zone_ids: [road.id],
      source: 'ai_network_atlas',
    };
    const persisted = zone({
      properties: { ...road.properties, street_network_ground_texture: meta },
    });
    expect(getStreetNetworkGroundMeta(persisted)).toEqual(meta);
    expect(getCurrentStreetNetworkGroundMeta([boundary, persisted])).toEqual(meta);

    const edited = zone({
      coordinates: persisted.coordinates.map((coordinate, index) => (
        index === 0 ? [coordinate[0] + 0.00001, coordinate[1]] : coordinate
      )),
      properties: persisted.properties,
    });
    expect(getStreetNetworkGroundMeta(edited)).toBeNull();
    expect(getCurrentStreetNetworkGroundMeta([boundary, edited])).toBeNull();
  });

  it('carries selected Calgary engineering sections into the shared street atlas contract', () => {
    const calgaryLocal = zone({
      properties: {
        ...zone({}).properties,
        road_archetype_id: 'calgary_local',
      },
    });
    const duplicateLocal = zone({
      id: '220fd97c-bd94-4e0b-aff7-67ba239e531f',
      properties: {
        ...zone({}).properties,
        road_archetype_id: 'calgary_local',
      },
    });
    const standards = getStreetNetworkStandards([boundary, calgaryLocal, duplicateLocal]);

    expect(standards).toHaveLength(1);
    expect(standards[0]).toMatchObject({
      archetypeId: 'calgary_local',
      sectionSvgUrl: '/archetypes/streets/calgary-local/section.svg',
      rowM: 16,
      targetSpeedKmh: 30,
    });
  });
});
