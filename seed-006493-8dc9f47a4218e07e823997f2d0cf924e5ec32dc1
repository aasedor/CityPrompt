import { describe, expect, it } from 'vitest';
import type { Building, SiteZone } from '@/types';
import { withModeledBuildingRenderZones } from './modelRenderZones';

const building: Building = {
  id: 'building-1',
  project_id: 'project-1',
  name: 'Railway Hotel',
  height_meters: 24,
  floor_count: 5,
  footprint_coordinates: [[-114, 51], [-113.999, 51], [-113.999, 51.001]],
  specifications: {
    legoAssembly: { archetype_id: 'chateauesque_grand_railway_hotel' },
  },
  created_at: '2026-01-01T00:00:00.000Z',
};

describe('withModeledBuildingRenderZones', () => {
  it('creates a transient render zone for a visible model whose source zone was deleted', () => {
    const result = withModeledBuildingRenderZones([], [building], new Set([building.id]), 'project-1');

    expect(result).toHaveLength(1);
    expect(result[0]).toMatchObject({
      id: 'modeled-building:building-1',
      zone_type: 'building',
      building_id: 'building-1',
      coordinates: building.footprint_coordinates,
      properties: {
        height: 24,
        floors: 5,
        archetype_id: 'chateauesque_grand_railway_hotel',
        _model_footprint_render_zone: true,
      },
    });
  });

  it('does not duplicate an existing building zone', () => {
    const existing = {
      id: 'zone-1', project_id: 'project-1', zone_type: 'building',
      coordinates: building.footprint_coordinates!, color: '#fff', sort_order: 0,
      building_id: building.id, created_at: '', updated_at: '',
    } satisfies SiteZone;

    const result = withModeledBuildingRenderZones([existing], [building], new Set([building.id]), 'project-1');
    expect(result).toEqual([existing]);
  });

  it('ignores unmounted models and buildings without valid footprints', () => {
    expect(withModeledBuildingRenderZones([], [building], new Set(), 'project-1')).toEqual([]);
    expect(withModeledBuildingRenderZones(
      [], [{ ...building, footprint_coordinates: [] }], new Set([building.id]), 'project-1',
    )).toEqual([]);
  });
});
