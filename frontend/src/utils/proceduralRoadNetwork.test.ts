import { describe, expect, it } from 'vitest';
import type { SiteZone } from '@/types';
import { roadDisplayZones, roadSnapTarget, snapRoadEndpoints, type RoadNetworkSnapshot } from './proceduralRoadNetwork';

const road: SiteZone = {
  id: 'parent', project_id: 'project', zone_type: 'road', coordinates: [[0, 0], [.001, 0], [.001, .0001], [0, .0001]],
  color: '#666666', sort_order: 0, created_at: '', updated_at: '',
  properties: { procedural_road: 1, plan_centerline: [[0, 0], [.001, 0]] },
};

describe('procedural road display adapter', () => {
  it('keeps source geometry while pending and never mutates editable zones', () => {
    expect(roadDisplayZones([road])[0]).toBe(road);
    const before = JSON.stringify(road);
    const network: RoadNetworkSnapshot = { version: 1, warnings: [], features: { type: 'FeatureCollection', features: [{
      type: 'Feature', properties: { kind: 'road_surface', id: 'edge', parentRoadId: 'parent' },
      geometry: { type: 'Polygon', coordinates: [[[0, 0], [1, 0], [1, 1], [0, 0]]] },
    }] } };
    const display = roadDisplayZones([road], network);
    expect(display).toHaveLength(1);
    expect(display[0].id).toBe('parent');
    expect(display[0].properties?._road_surface_key).toBe('edge:0');
    expect(display[0].properties?._road_parent_id).toBe('parent');
    expect(JSON.stringify(road)).toBe(before);
    expect(roadDisplayZones([], network)).toEqual([]);
  });
  it('snaps an endpoint to an existing midpoint in metres', () => {
    expect(roadSnapTarget([.0005, .00001], [road])).toEqual([.0005, 0]);
    expect(roadSnapTarget([.0005, .0001], [road])).toBeNull();
    expect(roadSnapTarget([.0005, .00001], [road], 1)).toBeNull();
    const line = [[.0005, .00001], [.0006, .00001], [.0005, .001]];
    expect(snapRoadEndpoints(line, [road])[1]).toEqual(line[1]);
    expect(line[0][1]).toBe(.00001);
  });
});
