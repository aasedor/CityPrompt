import { describe, expect, it } from 'vitest';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '../mapEngine/geoUtils';
import { buildLegoMassingDressingData, buildLegoMassingMeshData, legoMassingColor } from './legoMassingGeometry';

describe('buildLegoMassingMeshData', () => {
  it('extrudes every vertex of a concave footprint without bounding-box overhang', () => {
    const longitude = -114.15;
    const latitude = 51.04;
    const ring = [
      [longitude, latitude],
      [longitude + 0.0002, latitude],
      [longitude + 0.0002, latitude + 0.0001],
      [longitude + 0.0001, latitude + 0.0001],
      [longitude + 0.0001, latitude + 0.0002],
      [longitude, latitude + 0.0002],
      [longitude, latitude],
    ];

    const mesh = buildLegoMassingMeshData(ring, longitude + 0.0001, latitude + 0.0001, 18);

    expect(mesh).not.toBeNull();
    expect(mesh?.vertexCount).toBe(12);
    expect(mesh?.positions.filter((_value, index) => index % 3 === 2)).toEqual([
      0, 0, 0, 0, 0, 0,
      18, 18, 18, 18, 18, 18,
    ]);
    expect(mesh?.indices.length).toBeGreaterThan(0);
  });

  it('rejects degenerate rings and non-positive heights', () => {
    expect(buildLegoMassingMeshData([[0, 0], [1, 1]], 0, 0, 10)).toBeNull();
    expect(buildLegoMassingMeshData([[0, 0], [1, 0], [0, 1]], 0, 0, 0)).toBeNull();
  });

  it('uses stable muted massing colours instead of plan-zone colors', () => {
    expect(legoMassingColor('family-a:building-1')).toBe(legoMassingColor('family-a:building-1'));
    expect(legoMassingColor('family-a:building-1')).toMatch(/^#[0-9a-f]{6}$/i);
  });
});

describe('buildLegoMassingDressingData', () => {
  const longitude = -114, latitude = 51;
  const ll = (x: number, y: number) => [longitude + x / metersPerDegLon(latitude), latitude + y / METERS_PER_DEG_LAT];
  const rectangle = (width: number, depth: number) => [ll(-width / 2, -depth / 2), ll(width / 2, -depth / 2),
    ll(width / 2, depth / 2), ll(-width / 2, depth / 2)];
  const options = { storeys: 5, floorLineSpacingM: null, bayModuleM: 3.6, windowWidthM: 1.8, windowHeightM: 1.5,
    windowSillM: 0.9, wallEndMarginM: 0.9, floorLineHeightM: 0.12, surfaceOffsetM: 0.03 };
  const dress = (ring: number[][], overrides = {}) =>
    buildLegoMassingDressingData(ring, longitude, latitude, 19, { ...options, ...overrides })!;
  /** Width, sill and head of every window quad, from its four corners. */
  const windowQuads = (positions: number[]) => Array.from({ length: positions.length / 12 }, (_, index) => {
    const quad = positions.slice(index * 12, index * 12 + 12);
    return { width: Math.hypot(quad[3] - quad[0], quad[4] - quad[1]), sill: quad[2], head: quad[8],
      centre: [(quad[0] + quad[3]) / 2, (quad[1] + quad[4]) / 2] };
  });

  it('repeats whole window bays on a fixed module', () => {
    const data = dress(rectangle(36, 18));
    // (36 - 2 x 0.9) / 3.6 = 9 bays; (18 - 2 x 0.9) / 3.6 = 4 bays.
    expect(data.baysPerWall).toEqual([9, 4, 9, 4]);
    expect(data.windows.vertexCount).toBe((9 + 4 + 9 + 4) * 5 * 4);
    expect(data.windows.indices).toHaveLength((9 + 4 + 9 + 4) * 5 * 6);
  });

  it('adds bays as a wall grows and never stretches a window', () => {
    const widths = new Set<string>();
    const bays: number[] = [];
    for (const width of [9, 12.6, 20, 36, 50.4, 51, 118]) {
      const data = dress(rectangle(width, 18));
      bays.push(data.baysPerWall[0]);
      windowQuads(data.windows.positions).forEach(quad => widths.add(quad.width.toFixed(6)));
    }
    expect(bays).toEqual([2, 3, 5, 9, 13, 13, 32]);
    expect([...widths]).toEqual(['1.800000']);
  });

  it('centres each bay group so both wall ends keep the same solid margin', () => {
    const data = dress(rectangle(20, 18));
    const front = windowQuads(data.windows.positions).filter(quad => quad.centre[1] < -8.9 && quad.sill < 1);
    const xs = front.map(quad => quad.centre[0]).sort((a, b) => a - b);
    expect(xs).toHaveLength(5);
    expect(xs[0]).toBeCloseTo(-xs[4], 6);
    expect(xs[1] - xs[0]).toBeCloseTo(3.6, 6);
    // 20 m wall, five 3.6 m bays: 1 m of wall left at each end.
    expect(xs[0] - 0.9).toBeCloseTo(-10 + 1 + 0.9, 6);
  });

  it('leaves a wall bare when it cannot hold one whole bay', () => {
    const data = dress(rectangle(5, 18));
    expect(data.baysPerWall).toEqual([0, 4, 0, 4]);
  });

  it('draws one floor line per storey at the building’s own floor height', () => {
    const data = dress(rectangle(36, 18));
    expect(data.floorLevelsM).toHaveLength(4);
    data.floorLevelsM.forEach((level, index) => expect(level).toBeCloseTo((index + 1) * 19 / 5, 9));
    // Four walls, four intermediate floors, one band each.
    expect(data.floorLines.vertexCount).toBe(4 * 4 * 4);
    const quads = windowQuads(data.windows.positions);
    for (const quad of quads) {
      const storey = Math.floor(quad.sill / (19 / 5));
      expect(quad.sill).toBeCloseTo(storey * 19 / 5 + 0.9, 9);
      expect(quad.head - quad.sill).toBeCloseTo(1.5, 9);
      expect(quad.head).toBeLessThan((storey + 1) * 19 / 5);
    }
  });

  it('honours an explicit floor line spacing and keeps windows inside a low storey', () => {
    const data = dress(rectangle(36, 18), { floorLineSpacingM: 3, storeys: 6 });
    expect(data.floorLevelsM).toEqual([3, 6, 9, 12, 15]);
    const squat = dress(rectangle(36, 18), { floorLineSpacingM: 2.2 });
    for (const quad of windowQuads(squat.windows.positions)) {
      expect(quad.head - quad.sill).toBeCloseTo(2.2 - 0.9 - 0.12, 9);
    }
  });

  it('stands the dressing just outside the wall for either winding and on concave outlines', () => {
    const counterClockwise = rectangle(36, 18);
    for (const ring of [counterClockwise, [...counterClockwise].reverse()]) {
      const quads = windowQuads(dress(ring).windows.positions);
      for (const quad of quads) {
        const outside = Math.max(Math.abs(quad.centre[0]) - 18, Math.abs(quad.centre[1]) - 9);
        expect(outside).toBeCloseTo(0.03, 6);
      }
    }
    const lShape = [ll(-25, -15), ll(25, -15), ll(25, 0), ll(0, 0), ll(0, 15), ll(-25, 15)];
    const data = dress(lShape);
    expect(data.baysPerWall).toEqual([13, 3, 6, 3, 6, 7]);
    // The inner corner's walls face into the notch, away from the solid.
    const notch = windowQuads(data.windows.positions).filter(quad => quad.centre[0] > 0.5 && quad.centre[1] > 0.01 && quad.centre[1] < 0.1);
    expect(notch.length).toBe(6 * 5);
  });

  it('refuses degenerate input instead of drawing a guess', () => {
    expect(buildLegoMassingDressingData([[0, 0], [1, 1]], 0, 0, 19, options)).toBeNull();
    expect(buildLegoMassingDressingData(rectangle(36, 18), longitude, latitude, 0, options)).toBeNull();
    expect(buildLegoMassingDressingData(rectangle(36, 18), longitude, latitude, 19, { ...options, storeys: 0 })).toBeNull();
    expect(buildLegoMassingDressingData(rectangle(36, 18), longitude, latitude, 19, { ...options, windowWidthM: 3.6 })).toBeNull();
  });
});
