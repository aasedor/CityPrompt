import * as THREE from 'three';
import { describe, expect, it } from 'vitest';
import { createSharedGroundTriangulation, drapeSharedGroundGeometry, type SharedGroundTriangulation } from './sharedGroundGeometry';
import { createSharedSiteGroundSnapshot, sampleSharedSiteGround, type SharedSiteGroundLayout } from './sharedSiteGround';
import { METERS_PER_DEG_LAT, metersPerDegLon } from '../mapEngine/geoUtils';

function surface() {
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute('position', new THREE.Float32BufferAttribute([0, 0, .12, 12, 0, .12, 12, 12, .12, 0, 12, .12], 3));
  geometry.setAttribute('uv', new THREE.Float32BufferAttribute([0, 0, 1, 0, 1, 1, 0, 1], 2));
  geometry.setIndex([0, 1, 2, 0, 2, 3]);
  geometry.addGroup(0, 3, 0); geometry.addGroup(3, 3, 1);
  return geometry;
}
describe('shared terrain geometry', () => {
  it('samples interior relief while preserving lifts, UVs, orientation, area and material ownership', () => {
    const source = surface();
    const ground = (x: number, y: number) => Math.sin(x / 6) * .3 + y * .02;
    const result = drapeSharedGroundGeometry(source, ground)!;
    const p = result.getAttribute('position'), uv = result.getAttribute('uv'), index = result.index!;
    let area = 0;
    for (let i = 0; i < p.count; i += 1) {
      expect(p.getZ(i)).toBeCloseTo(.12 + ground(p.getX(i), p.getY(i)), 5);
      expect(uv.getX(i)).toBeCloseTo(p.getX(i) / 12, 6);
      expect(uv.getY(i)).toBeCloseTo(p.getY(i) / 12, 6);
    }
    for (let i = 0; i < index.count; i += 3) {
      const [a, b, c] = [0, 1, 2].map((k) => index.getX(i + k));
      const cross = (p.getX(b) - p.getX(a)) * (p.getY(c) - p.getY(a))
        - (p.getY(b) - p.getY(a)) * (p.getX(c) - p.getX(a));
      expect(cross).toBeGreaterThan(0); area += cross / 2;
      for (const [u, v] of [[a, b], [b, c], [c, a]]) expect(Math.hypot(p.getX(u) - p.getX(v), p.getY(u) - p.getY(v))).toBeLessThanOrEqual(4.00001);
    }
    expect(area).toBeCloseTo(144, 6);
    expect(result.groups.map((g) => g.materialIndex)).toEqual([0, 1]);
    expect(result.groups.reduce((count, g) => count + g.count, 0)).toBe(index.count);
    expect(source.getAttribute('position').count).toBe(4);
    expect(source.getAttribute('position').getZ(0)).toBeCloseTo(.12);
    result.dispose(); source.dispose();
  });
  it('rejects missing samples and a bounded mesh budget without changing the source', () => {
    const source = surface();
    expect(drapeSharedGroundGeometry(source, (x) => x > 5 ? null : 0)).toBeNull();
    expect(drapeSharedGroundGeometry(source, () => 0, 1, 6)).toBeNull();
    expect(source.index!.count).toBe(6);
    expect(source.getAttribute('position').count).toBe(4);
    source.dispose();
  });
  it('matches the shared triangle planes throughout every face, including interior peaks and UVs', () => {
    const layout: SharedSiteGroundLayout = { boundaryId: 'site', boundaryUpdatedAt: 'now', sourceSignature: 'site',
      boundaryCoordinates: [[0, 0], [12 / METERS_PER_DEG_LAT, 0], [12 / METERS_PER_DEG_LAT, 12 / METERS_PER_DEG_LAT], [0, 12 / METERS_PER_DEG_LAT]],
      grid: { west: 0, south: 0, columns: 4, rows: 4, stepLng: 4 / METERS_PER_DEG_LAT, stepLat: 4 / METERS_PER_DEG_LAT } };
    const heights = Array(16).fill(1000); heights[5] += .5;
    const snapshot = createSharedSiteGroundSnapshot(layout, heights, heights)!;
    const ground = (x: number, y: number) => sampleSharedSiteGround(snapshot, x / METERS_PER_DEG_LAT, y / METERS_PER_DEG_LAT)! - 1000;
    const source = surface(), result = drapeSharedGroundGeometry(source, ground, 4, 60000, createSharedGroundTriangulation(snapshot, 0, 0))!;
    const p = result.getAttribute('position'), uv = result.getAttribute('uv'), indices = result.index!;
    let area = 0;
    for (let start = 0; start < indices.count; start += 3) {
      const ids = [0, 1, 2].map((index) => indices.getX(start + index));
      const [a, b, c] = ids;
      area += ((p.getX(b) - p.getX(a)) * (p.getY(c) - p.getY(a)) - (p.getY(b) - p.getY(a)) * (p.getX(c) - p.getX(a))) / 2;
      for (const weights of [[1 / 3, 1 / 3, 1 / 3], [.1, .3, .6], [.45, .5, .05]]) {
        const x = ids.reduce((sum, id, index) => sum + p.getX(id) * weights[index], 0);
        const y = ids.reduce((sum, id, index) => sum + p.getY(id) * weights[index], 0);
        const z = ids.reduce((sum, id, index) => sum + p.getZ(id) * weights[index], 0);
        expect(z).toBeCloseTo(.12 + ground(x, y), 6);
      }
    }
    for (let index = 0; index < p.count; index += 1) {
      expect(uv.getX(index)).toBeCloseTo(p.getX(index) / 12, 6);
      expect(uv.getY(index)).toBeCloseTo(p.getY(index) / 12, 6);
    }
    expect(area).toBeCloseTo(144, 6);
    expect(result.groups.map((group) => group.materialIndex)).toEqual([0, 1]);
    expect(source.getAttribute('position').count).toBe(4);
    source.dispose(); result.dispose();
  });
  it('retains vertical curb faces on a grid diagonal and outer boundary exactly once', () => {
    const grid: SharedGroundTriangulation = { westX: 0, southY: 0, stepX: 4, stepY: 4, columns: 2, rows: 2 };
    for (const [a, b] of [[[0, 0], [4, 4]], [[4, 0], [4, 4]]]) {
      const source = new THREE.BufferGeometry().setAttribute('position', new THREE.Float32BufferAttribute([
        ...a, 0, ...b, 0, ...b, .15, ...a, .15,
      ], 3)).setIndex([0, 1, 2, 0, 2, 3]);
      const result = drapeSharedGroundGeometry(source, () => 0, 4, 60000, grid)!;
      const p = result.getAttribute('position'), indices = result.index!; let area = 0;
      for (let i = 0; i < indices.count; i += 3) {
        const points = [0, 1, 2].map((j) => new THREE.Vector3().fromBufferAttribute(p, indices.getX(i + j)));
        area += points[1].sub(points[0]).cross(points[2].sub(points[0])).length() / 2;
      }
      expect(area).toBeCloseTo(Math.hypot(b[0] - a[0], b[1] - a[1]) * .15, 6);
      source.dispose(); result.dispose();
    }
  });
  it('translates geographic grid lines into a shifted geometry frame and rejects unsupported pieces', () => {
    const grid: SharedGroundTriangulation = { westX: 0, southY: 0, stepX: 4, stepY: 4, columns: 4, rows: 4 };
    const source = surface();
    expect(drapeSharedGroundGeometry(source, () => null, 4, 60000, grid)).toBeNull();
    expect(drapeSharedGroundGeometry(source, () => 0, 4, 5, grid)).toBeNull();
    expect(drapeSharedGroundGeometry(source, () => 0, 4, 60000, { ...grid, columns: 3 })).toBeNull();
    const snapshot = { grid: { west: -114, south: 51, stepLng: .001, stepLat: .002, columns: 4, rows: 5 } } as Parameters<typeof createSharedGroundTriangulation>[0];
    const translated = createSharedGroundTriangulation(snapshot, -114.001, 51.001, 3, 7);
    expect(translated.westX).toBeCloseTo(.001 * metersPerDegLon(51.001) - 3, 6);
    expect(translated.southY).toBeCloseTo(-.001 * METERS_PER_DEG_LAT - 7, 6);
    expect(translated.stepX).toBeCloseTo(.001 * metersPerDegLon(51.001), 6);
    source.dispose();
  });
});
