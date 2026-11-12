import { describe, expect, it } from 'vitest';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '../mapEngine/geoUtils';
import * as THREE from 'three';
import contract from '@/data/buildingResizeTrial.json';
import {
  buildLegoMassingDressingData, buildLegoMassingKitData, buildLegoMassingMeshData, legoMassingColor, legoMassingKitBays,
  type LegoMassingColoredMesh, type LegoMassingKitStyle,
} from './legoMassingGeometry';

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

describe('buildLegoMassingKitData', () => {
  const longitude = -114, latitude = 51;
  const ll = (x: number, y: number) => [longitude + x / metersPerDegLon(latitude), latitude + y / METERS_PER_DEG_LAT];
  const rectangle = (width: number, depth: number) => [ll(-width / 2, -depth / 2), ll(width / 2, -depth / 2),
    ll(width / 2, depth / 2), ll(-width / 2, depth / 2)];
  const kit = contract.massing.kit;
  // The shipped tuning values, so a change to the file is a change to these expectations.
  const style: LegoMassingKitStyle = { storeys: 5, plinthHeightM: kit.plinth_height_m, groundFloorHeightM: kit.ground_floor_height_m,
    upperFloorHeightM: kit.upper_floor_height_m, parapetHeightM: kit.parapet_height_m, cornerPierM: kit.corner_pier_m,
    windowBayModuleM: kit.window_bay_module_m, windowWidthM: kit.window_width_m, windowHeightM: kit.window_height_m,
    windowSillM: kit.window_sill_m, groundWindowHeightM: kit.ground_window_height_m, groundWindowSillM: kit.ground_window_sill_m,
    loggiaBayModuleM: kit.loggia_bay_module_m, loggiaWidthM: kit.loggia_width_m, loggiaHeightM: kit.loggia_height_m,
    loggiaDepthM: kit.loggia_depth_m, loggiaMinWallM: kit.loggia_min_wall_m, railingHeightM: kit.railing_height_m,
    entranceWidthM: kit.entrance_width_m, entranceDepthM: kit.entrance_depth_m, entranceHeightM: kit.entrance_height_m,
    floorLineHeightM: contract.massing.floor_line_height_m, surfaceOffsetM: contract.massing.surface_offset_m, colors: kit.colors };
  const build = (ring: number[][], overrides: Partial<LegoMassingKitStyle> = {}) =>
    buildLegoMassingKitData(ring, longitude, latitude, { ...style, ...overrides })!;
  const bays = (text: string) => [...text].map(letter => letter === 'B' ? 'loggia' : 'window');
  const code = (sequence: string[]) => sequence.map(bay => bay === 'loggia' ? 'B' : 'W').join('');
  /** Horizontal width of every quad painted in one kit colour. */
  const widths = (mesh: LegoMassingColoredMesh, hex: string) => {
    const tone = new THREE.Color(hex), found = new Set<string>();
    for (let quad = 0; quad + 4 <= mesh.vertexCount; quad += 4) {
      const at = quad * 3;
      if (Math.abs(mesh.colors[at] - tone.r) > 1e-6 || Math.abs(mesh.colors[at + 1] - tone.g) > 1e-6
        || Math.abs(mesh.colors[at + 2] - tone.b) > 1e-6) continue;
      // Only upright quads: a width along the wall and a height.
      if (Math.abs(mesh.positions[at + 2] - mesh.positions[at + 5]) > 1e-6) continue;
      found.add(Math.hypot(mesh.positions[at + 3] - mesh.positions[at], mesh.positions[at + 4] - mesh.positions[at + 1]).toFixed(3));
    }
    return [...found].sort();
  };

  it('reproduces the archetype’s own front on a wall its size: window, three balconies, window', () => {
    expect(code(legoMassingKitBays(24, style))).toBe('WBBBW');
    const data = build(rectangle(24, 16));
    expect(data.walls.map(wall => code(wall.bays))).toEqual(['WBBBW', 'WWWW', 'WBBBW', 'WWWW']);
    expect(data.walls.map(wall => wall.entrance)).toEqual([true, false, false, false]);
    // Two ground windows each side of the entrance, as on the model.
    expect(data.walls[0].groundWindows).toBe(4);
  });

  it('uses the model’s real floor levels and parapet height', () => {
    const data = build(rectangle(24, 16));
    expect(data.floorLevelsM.map(level => Number(level.toFixed(2)))).toEqual([0.15, 4.15, 7.35, 10.55, 13.75]);
    expect(data.wallHeightM).toBeCloseTo(17.43, 2);
    const heights = data.solid.positions.filter((_value, index) => index % 3 === 2);
    expect(Math.min(...heights)).toBe(0);
    // Roof plant tops out at the model's recorded height.
    expect(Math.max(...heights)).toBeCloseTo(18.99, 2);
    expect(build(rectangle(24, 16), { storeys: 2 }).wallHeightM).toBeCloseTo(0.15 + 4 + 3.2 + 0.48, 6);
    expect(build(rectangle(24, 16), { storeys: 1 }).walls[0].bays).toHaveLength(3 + 2);
  });

  it('adds whole bays as a wall grows and keeps the facade symmetrical', () => {
    const sequences = [12, 18, 20, 24, 32.36, 40, 50, 90].map(length => code(legoMassingKitBays(length, style)));
    expect(sequences).toEqual(['WWW', 'WWWW', 'WBBW', 'WBBBW', 'WBBBBW', 'WBBBBBBW', 'WBBBBBBBW', 'WBBBBBBBBBBBBBBBW']);
    for (const sequence of sequences) expect(sequence).toBe([...sequence].reverse().join(''));
    for (let length = 4; length <= 120; length += 0.37) {
      const used = legoMassingKitBays(length, style).reduce((sum, bay) => sum + (bay === 'loggia' ? 5.3 : 3.5), 0);
      expect(used).toBeLessThanOrEqual(length - 2 * 0.55 + 1e-6);
    }
    expect(legoMassingKitBays(3, style)).toEqual([]);
    expect(legoMassingKitBays(19.9, style)).toEqual(bays('WWWWW'));
  });

  it('never stretches an opening: every size of building uses the same few widths', () => {
    const small = build(rectangle(24, 16)), large = build(rectangle(90, 40));
    for (const tone of [kit.colors.frame, kit.colors.glass, kit.colors.curtain]) {
      expect(widths(large.solid, tone)).toEqual(widths(small.solid, tone));
      expect(widths(large.glass, tone)).toEqual(widths(small.glass, tone));
    }
    // Window frames are exactly the window width; balcony doors a fixed share of the balcony.
    expect(widths(small.solid, kit.colors.frame)).toEqual(expect.arrayContaining(['2.500', (4.45 * 0.72).toFixed(3)]));
    expect(large.glass.vertexCount).toBeGreaterThan(small.glass.vertexCount * 2);
  });

  it('puts balconies only on long walls and the entrance only on the front', () => {
    const lShape = [ll(-25, -15), ll(25, -15), ll(25, 0), ll(0, 0), ll(0, 15), ll(-25, 15)];
    const data = build(lShape);
    expect(data.walls.map(wall => code(wall.bays))).toEqual(['WBBBBBBBW', 'WWW', 'WBBBW', 'WWW', 'WBBBW', 'WBBBBW']);
    expect(data.walls.map(wall => wall.entrance)).toEqual([true, false, false, false, false, false]);
    // A front too narrow for the canopy has no canopy entrance.
    expect(build(rectangle(9, 12)).walls.map(wall => [code(wall.bays), wall.entrance])).toEqual(
      [['WW', false], ['WWW', false], ['WW', false], ['WWW', false]]);
  });

  it('keeps the first drawn edge as the front for either winding', () => {
    const ring = rectangle(32.36, 17.98);
    const counterClockwise = build(ring);
    // The same outline drawn the other way round, still starting along the front edge.
    const clockwise = build([ring[1], ring[0], ring[3], ring[2]]);
    expect(clockwise.walls.map(wall => [Number(wall.lengthM.toFixed(3)), code(wall.bays), wall.entrance]))
      .toEqual(counterClockwise.walls.map(wall => [Number(wall.lengthM.toFixed(3)), code(wall.bays), wall.entrance]));
    expect(clockwise.solid.vertexCount).toBe(counterClockwise.solid.vertexCount);
  });

  it('emits well-formed, coloured meshes inside the outline’s reach', () => {
    const data = build(rectangle(32.36, 17.98));
    for (const mesh of [data.solid, data.glass]) {
      expect(mesh.positions).toHaveLength(mesh.vertexCount * 3);
      expect(mesh.colors).toHaveLength(mesh.vertexCount * 3);
      expect(mesh.positions.every(Number.isFinite)).toBe(true);
      expect(mesh.colors.every(value => value >= 0 && value <= 1)).toBe(true);
      expect(Math.max(...mesh.indices)).toBeLessThan(mesh.vertexCount);
      expect(mesh.indices.length % 3).toBe(0);
    }
    // Only the entrance canopy reaches beyond the drawn outline, and only by its own depth.
    const xs = data.solid.positions.filter((_value, index) => index % 3 === 0);
    const ys = data.solid.positions.filter((_value, index) => index % 3 === 1);
    expect(Math.max(...xs.map(Math.abs))).toBeLessThanOrEqual(32.36 / 2 + 0.07);
    expect(Math.max(...ys)).toBeLessThanOrEqual(17.98 / 2 + 0.07);
    expect(Math.min(...ys)).toBeGreaterThanOrEqual(-17.98 / 2 - kit.entrance_depth_m - 0.07);
  });

  it('refuses degenerate input instead of drawing a guess', () => {
    expect(buildLegoMassingKitData([[0, 0], [1, 1]], 0, 0, style)).toBeNull();
    expect(buildLegoMassingKitData(rectangle(24, 16), longitude, latitude, { ...style, storeys: 0 })).toBeNull();
    expect(buildLegoMassingKitData(rectangle(24, 16), longitude, latitude, { ...style, windowWidthM: 3.5 })).toBeNull();
    expect(buildLegoMassingKitData(rectangle(24, 16), longitude, latitude, { ...style, loggiaWidthM: 6 })).toBeNull();
  });
});
