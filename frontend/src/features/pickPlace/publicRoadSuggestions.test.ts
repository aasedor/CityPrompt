import { describe, expect, it } from 'vitest';
import type { SiteZone } from '@/types';
import { suggestPublicRoad, type PublicRoadContext } from './publicRoadSuggestions';
import { streetDrawingGeometry } from './streetDrawingGeometry';
import { BRT_VARIANT } from '@/components/viewer/globe/brtStreetProgram';

const sx = 111320 * Math.cos(51 * Math.PI / 180);
const ll = (x: number, y: number) => [-114 + x / sx, 51 + y / 111320];
const ring = (x1: number, y1: number, x2: number, y2: number) => [[x1, y1], [x2, y1], [x2, y2], [x1, y2]].map(([x, y]) => ll(x, y));
const boundary = { id: 'parcel', zone_type: 'site_boundary', coordinates: ring(0, 0, 200, 200) } as SiteZone;
const context: PublicRoadContext = { source: 'OpenStreetMap', fetched_at: '2026-09-30', blockers: [],
  roads: [{ id: 'osm:way:1', label: 'Existing Avenue', widthM: 8, points: [ll(-8, 0), ll(-8, 200)] }] };
const properties = { width: 20, lane_count: 2, pick_place_street_section: 'test' };

describe('optional public-road suggestions', () => {
  it.each([false, true])('previews and persists a single full-width connection at either end: reverse=%s', reverse => {
    const points = [ll(0, 80), ll(100, 100)]; if (reverse) points.reverse();
    const result = streetDrawingGeometry(points, properties, [boundary], { publicRoads: context });
    expect(result.suggestion?.road.label).toBe('Existing Avenue');
    expect(result.suggestion?.end).toBe(reverse ? 'finish' : 'start');
    expect(Math.abs((result.suggestion!.endpoint[0] - ll(-4, 80)[0]) * sx)).toBeLessThan(.01);
    expect(result.properties.connect_to_public_road).toBe(true);
    expect(result.properties.plan_route_controls).toHaveLength(3);
    expect(result.properties.road_public_target).toMatchObject({ id: 'osm:way:1', estimated_edge: true });
    expect(result).toEqual(streetDrawingGeometry(points, properties, [boundary], { publicRoads: context }));
  });
  it('Alt bypass and unavailable data preserve authored geometry without public-connection flags', () => {
    const points = [ll(1, 80), ll(100, 100)];
    const bypassed = streetDrawingGeometry(points, properties, [boundary], { publicRoads: context, skipSnapping: true });
    expect(bypassed.suggestion).toBeUndefined();
    expect(bypassed.properties.plan_route_controls).toEqual(points);
    expect(bypassed.properties.connect_to_public_road).toBeUndefined();
    expect(streetDrawingGeometry(points, properties, [boundary]).suggestion).toBeUndefined();
  });
  it('does not suggest across mapped buildings or occupied proposal plots', () => {
    const points = [ll(0, 80), ll(100, 80)], obstacle = ring(-3, 75, 3, 85);
    expect(suggestPublicRoad(points, properties, [boundary], boundary, { ...context, blockers: [obstacle] })).toBeNull();
    expect(suggestPublicRoad(points, properties, [boundary, { id: 'house', zone_type: 'building', coordinates: obstacle } as SiteZone], boundary, context)).toBeNull();
  });
  it('rejects excessive extension, reentry, distant clicks, both ends outside and target-junction proximity', () => {
    const far = { ...context, roads: [{ ...context.roads[0], points: [ll(-40, 0), ll(-40, 200)] }] };
    expect(suggestPublicRoad([ll(-36, 80), ll(100, 80)], properties, [boundary], boundary, far)).toBeNull();
    for (const points of [[ll(20, 80), ll(100, 80)], [ll(0, 80), ll(-30, 80)],
      [ll(0, 1), ll(100, 1)], [ll(0, 80), ll(50, 80), ll(-20, 80), ll(100, 80)]]) {
      expect(suggestPublicRoad(points, properties, [boundary], boundary, context)).toBeNull();
    }
  });
  it('does not create automatic transit, pedestrian-only or already explicit connections', () => {
    for (const props of [{ ...properties, road_selected_variant_id: BRT_VARIANT }, { ...properties, lane_count: 0 },
      { ...properties, width: 40 }, { ...properties, connect_to_public_road: true }]) {
      expect(suggestPublicRoad([ll(0, 80), ll(100, 80)], props, [boundary], boundary, context)).toBeNull();
    }
  });
  it('does not claim a connection when no mapped road is available', () => {
    expect(suggestPublicRoad([ll(0, 80), ll(100, 80)], properties, [boundary], boundary, { ...context, roads: [] })).toBeNull();
  });
});
