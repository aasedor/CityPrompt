import { describe, expect, it } from 'vitest';
import type { SiteZone } from '@/types';
import {
  MAX_FURNISHED_STREET_ZONES,
  selectDetailedStreetZones,
  selectFurnishedStreetIds,
  selectTreeStreetIds,
  shouldRenderLiveStreetTrees,
  streetTerrainSampleOffset,
} from './streetDetailLod';

function street(id: string, roadArchetypeId: string, streetRole?: string): SiteZone {
  return {
    id,
    project_id: 'project',
    zone_type: 'road',
    coordinates: [[0, 0], [1, 0], [1, 1], [0, 0]],
    color: '#777777',
    sort_order: 0,
    created_at: '2026-07-17T00:00:00Z',
    updated_at: '2026-07-17T00:00:00Z',
    properties: {
      road_archetype_id: roadArchetypeId,
      ...(streetRole ? { street_role: streetRole } : {}),
    },
  } as SiteZone;
}

describe('street detail LOD', () => {
  it('keeps non-tree archetype furniture across a normal 50-road community', () => {
    const zones = Array.from(
      { length: 50 },
      (_, index) => street(`local-${index}`, 'narrow_residential_street', 'local'),
    );
    expect(selectFurnishedStreetIds(zones)).toHaveLength(50);
    expect(MAX_FURNISHED_STREET_ZONES).toBeGreaterThanOrEqual(50);
  });

  it('keeps hierarchy streets when the detail budget is exceeded', () => {
    const zones = [
      street('lane-a', 'toronto_laneway', 'lane'),
      street('local-a', 'toronto_victorian_residential_street', 'local'),
      street('spine-a', '', 'spine'),
      street('roundabout-a', 'roundabout'),
      street('trail-a', 'multi_use_trail', 'trail'),
    ];
    expect(selectDetailedStreetZones(zones, 3).map((zone) => zone.id)).toEqual([
      'spine-a',
      'roundabout-a',
      'trail-a',
    ]);
  });

  it('budgets trees away from roundabouts and service lanes', () => {
    const ids = selectTreeStreetIds([
      street('lane-a', 'toronto_laneway', 'lane'),
      street('local-a', 'toronto_victorian_residential_street', 'local'),
      street('spine-a', '', 'spine'),
      street('roundabout-a', 'roundabout'),
    ], 2);
    expect([...ids]).toEqual(['spine-a', 'local-a']);
  });

  it('defers street trees to the final architectural render', () => {
    expect(shouldRenderLiveStreetTrees()).toBe(false);
  });

  it('assigns stable, bounded terrain-sampling phases', () => {
    expect(streetTerrainSampleOffset('road-42', 30)).toBe(streetTerrainSampleOffset('road-42', 30));
    expect(streetTerrainSampleOffset('road-42', 30)).toBeGreaterThanOrEqual(0);
    expect(streetTerrainSampleOffset('road-42', 30)).toBeLessThan(30);
  });
});
