import { useMemo } from 'react';
import { cleanup, renderHook } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import type { SiteZone } from '@/types';
import { bufferLineToPolygon } from '@/utils/roadGeometry';
import { detectConnectedStreetIntersections } from './streetGraphIntersections';
import { useStreetDetailZones } from './useStreetDetailZones';

afterEach(cleanup);

function road(id: string, line: number[][]): SiteZone {
  return { id, project_id: 'test', zone_type: 'road', coordinates: bufferLineToPolygon(line, 20),
    color: '#777', sort_order: 0, created_at: '', updated_at: '',
    properties: { width: 20, plan_centerline: line, road_archetype_id: 'calgary_collector',
      road_selected_variant_id: 'calgary_collector_v0', public_realm_fallback: { state: 'family_pending' } } };
}

describe('street inputs during navigation', () => {
  it('does not recompute junctions on unrelated parent renders, but does after a street edit', () => {
    const zones = [road('east-west', [[-114.061, 51.05], [-114.059, 51.05]]),
      road('north-south', [[-114.06, 51.049], [-114.06, 51.051]])];
    const build = vi.fn(detectConnectedStreetIntersections);
    const { result, rerender } = renderHook(({ source }) => {
      const inputs = useStreetDetailZones(source);
      return useMemo(() => build(inputs), [inputs]);
    }, { initialProps: { source: zones } });
    expect(result.current).toHaveLength(1);
    const original = result.current;
    for (let i = 0; i < 10; i++) rerender({ source: zones });
    expect(build).toHaveBeenCalledTimes(1);
    expect(result.current).toBe(original);

    const moved = road('north-south', [[-114.058, 51.049], [-114.058, 51.051]]);
    rerender({ source: [zones[0], moved] });
    expect(build).toHaveBeenCalledTimes(2);
    expect(result.current).toHaveLength(0);
    rerender({ source: [] });
    expect(build).toHaveBeenCalledTimes(3);
    expect(result.current).toHaveLength(0);
  });

  it('preserves boundary updates and excludes assets with their own renderer', () => {
    const boundary = { ...road('site', [[-114.061, 51.05], [-114.059, 51.05]]), zone_type: 'site_boundary' } as SiteZone;
    const trial = { ...road('trial', [[-114.061, 51.05], [-114.059, 51.05]]),
      properties: { public_realm_trial_asset: 'student_pickleball_garden_v1' } };
    const { result, rerender } = renderHook(({ source }) => useStreetDetailZones(source),
      { initialProps: { source: [boundary, trial] } });
    expect(result.current).toEqual([boundary]);
    const raised = { ...boundary, properties: { terrain_elevation_m: 1050 } };
    rerender({ source: [raised, trial] });
    expect(result.current).toEqual([raised]);
  });
});
