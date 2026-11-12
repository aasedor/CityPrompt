import { describe, expect, it } from 'vitest';
import * as THREE from 'three';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '../mapEngine/geoUtils';
import { RESIZE_TRIAL_SETTINGS } from '@/features/pickPlace/buildingResizeTrial';
import {
  buildLegoMassingCourtyardKitData, legoMassingCourtyardBays, type LegoMassingCourtyardStyle,
} from './legoMassingCourtyardKit';
import { buildLegoMassingKit, type LegoMassingKit } from './legoMassingKits';
import type { LegoMassingColoredMesh } from './legoMassingGeometry';

const longitude = -114, latitude = 51;
const ll = (x: number, y: number) => [longitude + x / metersPerDegLon(latitude), latitude + y / METERS_PER_DEG_LAT];
const rectangle = (width: number, depth: number) => [ll(-width / 2, -depth / 2), ll(width / 2, -depth / 2),
  ll(width / 2, depth / 2), ll(-width / 2, depth / 2)];
// The shipped tuning values, so a change to the file is a change to these expectations.
const shipped = RESIZE_TRIAL_SETTINGS.kits.brick_garden_courtyard;
if (shipped.type !== 'courtyard_block') throw new Error('The courtyard kit is missing from the tuning file');
const style: LegoMassingCourtyardStyle = { ...shipped, storeys: 4, surfaceOffsetM: RESIZE_TRIAL_SETTINGS.surfaceOffsetM };
const build = (ring: number[][], overrides: Partial<LegoMassingCourtyardStyle> = {}) =>
  buildLegoMassingCourtyardKitData(ring, longitude, latitude, { ...style, ...overrides })!;
const code = (sequence: string[]) => sequence.map(bay => bay === 'loggia' ? 'B' : 'W').join('');
/** Horizontal width of every upright quad painted in one kit colour. */
const widths = (mesh: LegoMassingColoredMesh, hex: string) => {
  const tone = new THREE.Color(hex), found = new Set<string>();
  for (let quad = 0; quad + 4 <= mesh.vertexCount; quad += 4) {
    const at = quad * 3;
    if (Math.abs(mesh.colors[at] - tone.r) > 1e-6 || Math.abs(mesh.colors[at + 1] - tone.g) > 1e-6
      || Math.abs(mesh.colors[at + 2] - tone.b) > 1e-6) continue;
    if (Math.abs(mesh.positions[at + 2] - mesh.positions[at + 5]) > 1e-6) continue;
    found.add(Math.hypot(mesh.positions[at + 3] - mesh.positions[at], mesh.positions[at + 4] - mesh.positions[at + 1]).toFixed(3));
  }
  return [...found].sort();
};
const extent = (mesh: LegoMassingColoredMesh) => {
  const box = new THREE.Box3();
  for (let index = 0; index < mesh.positions.length; index += 3) {
    box.expandByPoint(new THREE.Vector3(mesh.positions[index], mesh.positions[index + 1], mesh.positions[index + 2]));
  }
  return box;
};

describe('legoMassingCourtyardBays', () => {
  it('alternates balconies and windows from both ends, so every front is symmetrical', () => {
    const module = style.bayModuleM;
    expect([1, 2, 3, 4, 5, 6, 7].map(count => code(legoMassingCourtyardBays(count * module, module))))
      .toEqual(['B', 'BB', 'BWB', 'BWWB', 'BWBWB', 'BWBBWB', 'BWBWBWB']);
    expect(legoMassingCourtyardBays(module - 0.01, module)).toEqual([]);
    expect(legoMassingCourtyardBays(30, 0)).toEqual([]);
  });

  it('keeps a middle bay for the gateway on the front', () => {
    const module = style.bayModuleM;
    expect([1, 2, 3, 4, 6].map(count => code(legoMassingCourtyardBays(count * module, module, true))))
      .toEqual(['B', 'B', 'BWB', 'BWB', 'BWBWB']);
  });
});

describe('buildLegoMassingCourtyardKitData', () => {
  it('reproduces the archetype on its own footprint: seven bays, a passage and a courtyard', () => {
    const data = build(rectangle(30, 24.4));
    // Balcony, window, balcony, window, balcony, window, balcony: the model's front.
    expect(data.walls.map(wall => code(wall.bays))).toEqual(['BWBWBWB', 'WWWWWWW', 'BWBWBWB', 'WWWWWWW']);
    expect(data.gateway).toBe('passage');
    expect(data.walls.map(wall => wall.entrance)).toEqual([true, false, false, false]);
    // Six shops on the front beside the gateway, seven on the rear.
    expect(data.walls.map(wall => wall.groundWindows)).toEqual([6, 7, 7, 7]);
    expect(data.courtyardAreaM2).toBeCloseTo(19.2 * 13.6, 3);
    // Floor levels and parapet measured from the model: 4.2 m shops, 3.2 m homes.
    expect(data.floorLevelsM.map(level => Number(level.toFixed(2)))).toEqual([0.15, 4.35, 7.55, 10.75]);
    expect(data.wallHeightM).toBeCloseTo(14.59, 6);
  });

  it('stays on the drawn outline, apart from awnings, sills and the gateway apron', () => {
    const data = build(rectangle(30, 24.4)), box = extent(data.solid);
    expect(box.min.x).toBeGreaterThan(-15 - style.shopBandProjectionM - 1e-6);
    expect(box.max.x).toBeLessThan(15 + style.shopBandProjectionM + 1e-6);
    expect(box.min.y).toBeGreaterThan(-12.2 - style.awningProjectionM - 1e-6);
    expect(box.max.y).toBeLessThan(12.2 + style.awningProjectionM + 1e-6);
    expect(box.min.z).toBeGreaterThanOrEqual(0);
    // Roof plant stands above the coping.
    expect(box.max.z).toBeGreaterThan(data.wallHeightM);
    expect(box.max.z).toBeLessThan(data.wallHeightM + 1);
  });

  it('repeats bays on a longer front and never widens one', () => {
    const narrow = build(rectangle(30, 24.4)), wide = build(rectangle(60, 24.4));
    expect(code(wide.walls[0].bays)).toBe('BWBWBWBWBWBWB');
    expect(wide.walls[0].lengthM).toBeCloseTo(60, 3);
    // Glazing and frames come in the same widths however long the wall.
    expect(widths(wide.glass, style.colors.glass)).toEqual(widths(narrow.glass, style.colors.glass));
    expect(widths(wide.glass, style.colors.shopfront)).toEqual(widths(narrow.glass, style.colors.shopfront));
    // An even count gives up one bay so the gateway keeps a bay of its own.
    expect(code(build(rectangle(26, 24.4)).walls[0].bays)).toBe('BWBWB');
  });

  it('builds a solid block with a front door where no courtyard fits', () => {
    const small = build(rectangle(18, 14));
    expect(small.courtyardAreaM2).toBe(0);
    expect(small.gateway).toBe('door');
    expect(code(small.walls[0].bays)).toBe('BWB');
    const bar = build(rectangle(80, 14));
    expect(bar.courtyardAreaM2).toBe(0);
    expect(bar.gateway).toBe('door');
    // A front shorter than the gateway has neither door nor bays.
    const sliver = build([ll(-2, -10), ll(2, -10), ll(12, 10), ll(-12, 10)]);
    expect(sliver.gateway).toBe('none');
    expect(sliver.walls[0].bays).toEqual([]);
  });

  it('wraps the courtyard round any outline and treats walls along the front as street fronts', () => {
    const lOutline = [ll(-30, -23), ll(30, -23), ll(30, 1), ll(-6, 1), ll(-6, 23), ll(-30, 23)];
    const data = build(lOutline);
    expect(data.courtyardAreaM2).toBeCloseTo(49.2 * 13.2 + 13.2 * 22, 2);
    expect(data.gateway).toBe('passage');
    // Walls parallel to the front carry balconies; the others carry plain windows.
    expect(data.walls.map(wall => wall.bays.includes('loggia'))).toEqual([true, false, true, false, true, false]);
    const five = build([ll(-26, -18), ll(24, -20), ll(30, 6), ll(4, 22), ll(-24, 14)]);
    expect(five.courtyardAreaM2).toBeGreaterThan(900);
    expect(five.walls).toHaveLength(5);
  });

  it('treats the first drawn edge as the front whichever way the outline runs', () => {
    const ring = rectangle(30, 24.4);
    const clockwise = build([ring[0], ring[3], ring[2], ring[1]]);
    // The first edge is now a 24.4 m side of the rectangle, and it is the front.
    expect(clockwise.walls[0].lengthM).toBeCloseTo(24.4, 3);
    expect(clockwise.walls[0].entrance).toBe(true);
    expect(code(clockwise.walls[0].bays)).toBe('BWBWB');
  });

  it('follows the saved storey count and draws valid geometry', () => {
    const two = build(rectangle(30, 24.4), { storeys: 2 });
    expect(two.floorLevelsM).toHaveLength(2);
    expect(two.wallHeightM).toBeCloseTo(0.15 + 4.2 + 3.2 + 0.64, 6);
    const one = build(rectangle(30, 24.4), { storeys: 1 });
    expect(one.wallHeightM).toBeCloseTo(0.15 + 4.2 + 0.64, 6);
    for (const data of [build(rectangle(30, 24.4)), two, one, build(rectangle(18, 14))]) {
      for (const mesh of [data.solid, data.glass]) {
        expect(mesh.positions.every(Number.isFinite)).toBe(true);
        expect(mesh.positions).toHaveLength(mesh.vertexCount * 3);
        expect(mesh.colors).toHaveLength(mesh.vertexCount * 3);
        expect(Math.max(...mesh.indices)).toBeLessThan(mesh.vertexCount);
      }
    }
    expect(buildLegoMassingCourtyardKitData(rectangle(30, 24.4), longitude, latitude, { ...style, storeys: 0 })).toBeNull();
    expect(buildLegoMassingCourtyardKitData(rectangle(30, 24.4).slice(0, 2), longitude, latitude, style)).toBeNull();
    expect(buildLegoMassingCourtyardKitData(rectangle(30, 24.4), longitude, latitude, { ...style, bayModuleM: 2 })).toBeNull();
  });
});

describe('buildLegoMassingKit', () => {
  it('draws each building with the vocabulary its kit names', () => {
    const offset = { surfaceOffsetM: RESIZE_TRIAL_SETTINGS.surfaceOffsetM, floorLineHeightM: RESIZE_TRIAL_SETTINGS.floorLineHeightM };
    const courtyard = buildLegoMassingKit(rectangle(30, 24.4), longitude, latitude,
      { ...RESIZE_TRIAL_SETTINGS.kits.brick_garden_courtyard, ...offset, storeys: 4 } as LegoMassingKit)!;
    const bar = buildLegoMassingKit(rectangle(30, 24.4), longitude, latitude,
      { ...RESIZE_TRIAL_SETTINGS.kits.aspen_terrace, ...offset, storeys: 5 } as LegoMassingKit)!;
    expect('courtyardAreaM2' in courtyard).toBe(true);
    expect('courtyardAreaM2' in bar).toBe(false);
    expect(courtyard.wallHeightM).not.toBeCloseTo(bar.wallHeightM, 1);
  });
});
