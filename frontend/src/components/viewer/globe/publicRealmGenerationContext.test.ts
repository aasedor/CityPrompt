import { describe, expect, it } from 'vitest';
import type { SiteZone } from '@/types';
import {
  buildPublicRealmContextPrompt,
  buildPublicRealmGenerationContext,
  buildPublicRealmSceneContextPrompt,
} from './publicRealmGenerationContext';

const ORIGIN_LNG = -114;
const ORIGIN_LAT = 51;
const METRES_PER_LNG = 70_100;
const METRES_PER_LAT = 111_320;

function point(x: number, y: number): [number, number] {
  return [ORIGIN_LNG + x / METRES_PER_LNG, ORIGIN_LAT + y / METRES_PER_LAT];
}

function rectangle(x0: number, y0: number, x1: number, y1: number): number[][] {
  return [point(x0, y0), point(x1, y0), point(x1, y1), point(x0, y1)];
}

function zone(
  id: string,
  zoneType: SiteZone['zone_type'],
  coordinates: number[][],
  properties: SiteZone['properties'] = {},
  name?: string,
): SiteZone {
  return {
    id,
    project_id: 'project-1',
    name,
    zone_type: zoneType,
    coordinates,
    color: '#4caf50',
    properties,
    sort_order: 0,
    created_at: '2026-08-02T00:00:00Z',
    updated_at: '2026-08-02T00:00:00Z',
  };
}

describe('public-realm generation context', () => {
  const park = zone(
    'park',
    'green_space',
    rectangle(0, 0, 20, 20),
    {
      _plan_role: 'open_space',
      green_space_archetype_id: 'neighborhood_park',
      terrain_elevation_m: 1100.4,
    },
    'Courtyard Park',
  );
  const street = zone(
    'street',
    'road',
    rectangle(20, 0, 30, 20),
    { _plan_role: 'street', road_archetype_id: 'complete_street', width: 10 },
    'Main Street',
  );
  const building = zone(
    'building',
    'building',
    rectangle(-15, 2, -5, 18),
    {
      _plan_role: 'building',
      development_archetype_id: 'haussmann_midrise',
      floors: 6,
      height_m: 22,
    },
    'Haussmann Block',
  );
  const remoteBuilding = zone(
    'remote-building',
    'building',
    rectangle(200, 200, 220, 220),
    { _plan_role: 'building', floors: 12 },
    'Remote Tower',
  );
  const contextCarrier = zone(
    'boundary',
    'site_boundary',
    rectangle(-40, -40, 80, 80),
    {
      _osm_context: {
        buildings: [],
        roads: [{
          osm_id: 77,
          coordinates: [point(-10, -8), point(30, -8)],
          width_m: 12,
          road_type: 'secondary',
          name: 'Existing Avenue',
        }],
        water: [],
        parks: [],
        fetched_at: '2026-08-02T00:00:00Z',
        buffer_m: 250,
      },
    },
  );
  const zones = [park, street, building, remoteBuilding, contextCarrier];

  it('finds edge-connected proposals, nearby buildings, mapped roads and terrain', () => {
    const context = buildPublicRealmGenerationContext(park, zones);

    expect(context).not.toBeNull();
    expect(context?.target_elevation_m).toBe(1100.4);
    expect(context?.neighbors.map((neighbor) => neighbor.id)).toEqual([
      'street',
      'osm-road-77',
      'building',
    ]);
    expect(context?.neighbors[0]).toMatchObject({
      kind: 'street',
      relation: 'edge-connected',
      direction: 'on the east edge',
      width_m: 10,
    });
    expect(context?.neighbors.find((neighbor) => neighbor.id === 'building')).toMatchObject({
      kind: 'building',
      relation: 'fronting',
      direction: 'on the west edge',
      floors: 6,
      height_m: 22,
    });
    expect(context?.neighbors.some((neighbor) => neighbor.id === 'remote-building')).toBe(false);
  });

  it('writes explicit interface and Google-tile instructions for a park API call', () => {
    const prompt = buildPublicRealmContextPrompt(park, zones, {
      sceneReferenceAttached: true,
    });

    expect(prompt).toContain('proposed street "Main Street"');
    expect(prompt).toContain('proposed building "Haussmann Block" (6 floors, 22 m high)');
    expect(prompt).toContain('existing mapped road "Existing Avenue"');
    expect(prompt).toContain('Put primary park gateways on street/path-facing edges');
    expect(prompt).toContain('current Google photogrammetry, terrain and mounted 3D buildings');
    expect(prompt).toContain('may not override the target polygon or locked internal geometry');
  });

  it('writes street-specific entrance, curb, crossing and park-gate coordination', () => {
    const prompt = buildPublicRealmContextPrompt(street, zones, {
      sceneReferenceAttached: true,
      compact: true,
    });

    expect(prompt).toContain('proposed park "Courtyard Park"');
    expect(prompt).toContain('Keep carriageways, paths, curbs and cycle tracks continuous');
    expect(prompt).toContain('align sidewalks and crossings with park gates and building entrances');
  });

  it('builds a bounded scene-wide clause for Classic and Direct 3D calls', () => {
    const prompt = buildPublicRealmSceneContextPrompt(zones, {
      sceneReferenceAttached: true,
    });

    expect(prompt).toContain('PUBLIC-REALM EDGE COORDINATION');
    expect(prompt).toContain('park "Courtyard Park"');
    expect(prompt).toContain('street "Main Street"');
    expect(prompt).toContain('captured Google-tile scene and mounted 3D buildings');
    expect(prompt).toContain('Missing connections remain missing');
    expect(prompt).not.toContain('Remote Tower');
  });
});
