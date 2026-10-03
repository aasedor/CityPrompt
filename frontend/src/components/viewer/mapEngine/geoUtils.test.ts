import { describe, expect, it } from 'vitest';
import type { SiteZone } from '@/types';
import {
  bufferLineToPolygon,
  METERS_PER_DEG_LAT,
  metersPerDegLon,
  polygonAreaM2,
  polygonDimensionsMeters,
  resolveZoneColor,
} from './geoUtils';
import { bufferLineToPolygon as editRoadBuffer } from '@/utils/roadGeometry';

describe('drawn street metric width', () => {
  const route = [
    [-114.10838321053419, 51.117357486642014],
    [-114.10864208085879, 51.11709678113251],
  ];

  it.each([route, [...route].reverse()])('keeps an 18 m diagonal section perpendicular at both ends', (start, end) => {
    const points = [start, end];
    const polygon = bufferLineToPolygon(points, 18);
    const lonScale = metersPerDegLon(start[1]);
    const metric = (a: number[], b: number[]) => [
      (a[0] - b[0]) * lonScale, (a[1] - b[1]) * METERS_PER_DEG_LAT,
    ];
    const delta = metric(end, start);
    const length = Math.hypot(...delta);
    for (let station = 0; station < 2; station += 1) {
      const section = metric(polygon[station], polygon[3 - station]);
      expect(Math.hypot(...section)).toBeCloseTo(18, 5);
      expect((section[0] * delta[0] + section[1] * delta[1]) / length).toBeCloseTo(0, 5);
    }
    expect(polygon).toEqual(editRoadBuffer(points, 18));
  });

  it('uses the same bounded bend geometry for drawing and editing without mutating the route', () => {
    const points = [...route, [-114.1089, 51.1170]];
    const original = structuredClone(points);
    expect(bufferLineToPolygon(points, 18)).toEqual(editRoadBuffer(points, 18));
    expect(points).toEqual(original);
  });
});

const CENTER_LNG = -114.0719;
const CENTER_LAT = 51.0447;

function localMeterPolygon(points: Array<[number, number]>): number[][] {
  const mPerDegLon = metersPerDegLon(CENTER_LAT);
  return points.map(([x, y]) => [
    CENTER_LNG + x / mPerDegLon,
    CENTER_LAT + y / METERS_PER_DEG_LAT,
  ]);
}

function rectangle(width: number, depth: number, angleDeg = 0): number[][] {
  const halfW = width / 2;
  const halfD = depth / 2;
  const angle = angleDeg * Math.PI / 180;
  const cos = Math.cos(angle);
  const sin = Math.sin(angle);

  return localMeterPolygon([
    [-halfW, -halfD],
    [halfW, -halfD],
    [halfW, halfD],
    [-halfW, halfD],
  ].map(([x, y]) => [
    x * cos - y * sin,
    x * sin + y * cos,
  ]));
}

describe('geoUtils map-meter footprint helpers', () => {
  it('computes area for a 10m by 10m drawn footprint', () => {
    const square = rectangle(10, 10);
    const dimensions = polygonDimensionsMeters(square);

    expect(polygonAreaM2(square)).toBeCloseTo(100, 0);
    expect(dimensions.area).toBeCloseTo(100, 0);
    expect(dimensions.width).toBeCloseTo(10, 0);
    expect(dimensions.depth).toBeCloseTo(10, 0);
  });

  it('reports oriented dimensions for a rotated footprint', () => {
    const footprint = rectangle(40, 20, 31);
    const dimensions = polygonDimensionsMeters(footprint);

    expect(dimensions.area).toBeCloseTo(800, 0);
    expect(dimensions.width).toBeCloseTo(40, 0);
    expect(dimensions.depth).toBeCloseTo(20, 0);
  });
});

function buildingZone(
  name: string,
  properties: Record<string, unknown>,
  id = name,
): SiteZone {
  return {
    id,
    project_id: 'p1',
    zone_type: 'building',
    name,
    coordinates: rectangle(20, 20),
    color: '#ff0000',
    sort_order: 0,
    created_at: '',
    updated_at: '',
    properties: {
      development_archetype_id: 'contemporary_townhouse_courtyard',
      ...properties,
    },
  } as unknown as SiteZone;
}

describe('resolveZoneColor plan-building differentiation', () => {
  it('keeps the canonical archetype shade for non-plan zones and bar A', () => {
    const plain = resolveZoneColor(buildingZone('Hand-drawn zone', {}));
    const barA = resolveZoneColor(
      buildingZone('As-of-Right · Block 1 · Building A', { _plan_role: 'building' }),
    );
    expect(barA).toBe(plain);
  });

  it('gives sibling bars of one block distinct fills', () => {
    const bars = ['A', 'B', 'C', 'D'].map((letter) =>
      resolveZoneColor(
        buildingZone(`As-of-Right · Block 1 · Building ${letter}`, { _plan_role: 'building' }),
      ),
    );
    expect(new Set(bars).size).toBe(4);
    for (const color of bars) expect(color).toMatch(/^#[0-9a-f]{6}$/i);
  });

  it('is deterministic for plan bars without a Building letter', () => {
    const make = () =>
      resolveZoneColor(
        buildingZone('As-of-Right · Block 2', { _plan_role: 'building' }, 'zone-uuid-42'),
      );
    expect(make()).toBe(make());
    expect(make()).toMatch(/^#[0-9a-f]{6}$/i);
  });
});
