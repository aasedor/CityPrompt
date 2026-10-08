import { describe, expect, it } from 'vitest';
import type { SiteZone } from '@/types';
import { rectangleAt } from '@/features/pickPlace/geometry';
import {
  benchContext,
  resolveBenches,
  saveBenchDetails,
  readBenchDetails,
  benchPlacementProblem,
  plantingClearOfBenches,
} from './benchDetails';

const zone = {
  id: 'park',
  project_id: 'trial',
  name: 'Trial park',
  color: '#769952',
  sort_order: 0,
  created_at: '2026-10-08',
  updated_at: '2026-10-08',
  zone_type: 'green_space',
  coordinates: rectangleAt([-114, 51], 70, 55),
  properties: {
    green_space_archetype_id: 'neighborhood_park',
    green_space_selected_variant_id: 'neighborhood_park_v0',
    neighborhood_park_layout: 'adaptive_rustic_v1',
  },
} as SiteZone;
describe('rustic park bench edits', () => {
  it('keeps automatic planting clear of edited benches when the park planting regenerates', () => {
    const bench = { id: 'student-bench', point: { x: 20, y: 20 }, yaw: 0 };
    expect(
      plantingClearOfBenches(
        [
          { x: 20, y: 20 },
          { x: 30, y: 30 },
        ],
        [bench],
      ),
    ).toEqual([{ x: 30, y: 30 }]);
    expect(plantingClearOfBenches([{ x: 20, y: 20 }], [])).toEqual([
      { x: 20, y: 20 },
    ]);
  });
  it.each([
    [40, 35],
    [55, 45],
    [70, 55],
    [90, 70],
  ])(
    'accepts the automatic benches in a %s by %s metre park',
    (width, depth) => {
      const park = {
        ...zone,
        coordinates: rectangleAt([-114, 51], width, depth),
      };
      const context = benchContext(park),
        benches = resolveBenches(park, context);
      for (const bench of benches)
        expect(benchPlacementProblem(bench, benches, context)).toBeNull();
    },
  );
  it('starts with the actual automatic benches and persists removal of every bench', () => {
    const context = benchContext(zone),
      benches = resolveBenches(zone, context);
    expect(benches.length).toBeGreaterThan(0);
    const properties = saveBenchDetails(zone, [], context);
    expect(resolveBenches({ ...zone, properties }, context)).toEqual([]);
    expect(properties.green_space_archetype_id).toBe('neighborhood_park');
  });
  it('saves added and moved benches and retains their IDs and orientation after reload', () => {
    const context = benchContext(zone),
      benches = resolveBenches(zone, context);
    const edited = [
      { ...benches[0], point: { x: 20, y: 20 }, yaw: 0.6 },
      { id: 'added-1', point: { x: 30, y: 25 }, yaw: 1.2 },
    ];
    const saved = {
      ...zone,
      properties: JSON.parse(
        JSON.stringify(saveBenchDetails(zone, edited, context)),
      ),
    };
    resolveBenches(saved, context).forEach((bench, i) => {
      expect(bench.id).toBe(edited[i].id);
      expect(bench.point.x).toBeCloseTo(edited[i].point.x, 5);
      expect(bench.point.y).toBeCloseTo(edited[i].point.y, 5);
      expect(bench.yaw).toBeCloseTo(edited[i].yaw, 5);
    });
  });
  it('moves and rotates saved benches with the whole park without scaling the bench model', () => {
    const context = benchContext(zone),
      benches = resolveBenches(zone, context);
    const properties = saveBenchDetails(zone, benches, context);
    const moved = {
      ...zone,
      properties,
      coordinates: rectangleAt([-114.01, 51.02], 70, 55, 90),
    };
    const result = resolveBenches(moved, benchContext(moved));
    expect(result).toHaveLength(benches.length);
    expect(result[0].yaw - benches[0].yaw).toBeCloseTo(Math.PI / 2, 3);
    expect(readBenchDetails(properties)?.items).toEqual(
      readBenchDetails(saveBenchDetails(moved, result, benchContext(moved)))
        ?.items,
    );
  });
  it('uses the same world positions from different render/capture origins', () => {
    const context = benchContext(zone),
      properties = saveBenchDetails(
        zone,
        resolveBenches(zone, context),
        context,
      );
    const saved = { ...zone, properties };
    const a = benchContext(saved),
      b = benchContext(saved, { lng: -114.002, lat: 51.002 });
    const one = resolveBenches(saved, a),
      two = resolveBenches(saved, b);
    one.forEach((p, i) => {
      expect(a.toWorld(p.point)[0]).toBeCloseTo(b.toWorld(two[i].point)[0], 10);
      expect(a.toWorld(p.point)[1]).toBeCloseTo(b.toWorld(two[i].point)[1], 10);
    });
  });
  it('rejects malformed saved layouts and prevents placing a bench outside the park', () => {
    expect(
      readBenchDetails({
        bench_details: {
          version: 1,
          items: [{ id: 'bad', u: NaN, v: 0, angle: 0 }],
        },
      }),
    ).toBeNull();
    const context = benchContext(zone);
    expect(
      benchPlacementProblem(
        { id: 'new', point: { x: -100, y: -100 }, yaw: 0 },
        [],
        context,
      ),
    ).toMatch(/inside/);
  });
});
