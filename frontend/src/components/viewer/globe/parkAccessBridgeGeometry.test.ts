import { describe, expect, it } from 'vitest';
import { buildParkAccessBridgeGeometry } from './parkAccessBridgeGeometry';
import { PUBLIC_REALM_GROUND_SURFACE_LIFT_METERS, PUBLIC_REALM_STREET_SIDEWALK_SURFACE_LIFT_METERS } from './publicRealmDepthPolicy';

describe('park access arrival strip', () => {
  it('keeps its physical width and meets the sampled sidewalk and park datums', () => {
    const geometry = buildParkAccessBridgeGeometry({ start: [4, 1], end: [4, 5], widthM: 2.2,
      streetLiftM: PUBLIC_REALM_STREET_SIDEWALK_SURFACE_LIFT_METERS, startGroundM: 0.5, endGroundM: 0.1 })!;
    const positions = geometry.getAttribute('position');
    expect(Math.abs(positions.getX(1) - positions.getX(0))).toBeCloseTo(2.2);
    expect(positions.getZ(0)).toBeCloseTo(0.5 + PUBLIC_REALM_STREET_SIDEWALK_SURFACE_LIFT_METERS + 0.003);
    expect(positions.getZ(2)).toBeCloseTo(0.1 + PUBLIC_REALM_GROUND_SURFACE_LIFT_METERS + 0.003);
    expect(geometry.index?.count).toBe(6);
    geometry.dispose();
  });
  it('does not manufacture a surface for a zero-length connection', () => {
    expect(buildParkAccessBridgeGeometry({ start: [1, 2], end: [1, 2], widthM: 2.2, streetLiftM: 0.2 })).toBeNull();
  });
  it('drapes every subdivided vertex on the shared ground and preserves construction lifts', () => {
    const groundAt = (x: number, y: number) => x * 0.02 + y * 0.04;
    const geometry = buildParkAccessBridgeGeometry({ start: [0, 0], end: [0, 8], widthM: 2.2,
      streetLiftM: 0.2, startGroundM: 999, endGroundM: 999, groundAt })!;
    const positions = geometry.getAttribute('position');
    expect(positions.count).toBeGreaterThan(4);
    for (let i = 0; i < positions.count; i += 1) {
      const x = positions.getX(i), y = positions.getY(i), t = y / 8;
      expect(positions.getZ(i)).toBeCloseTo(groundAt(x, y) + 0.2 * (1 - t) + PUBLIC_REALM_GROUND_SURFACE_LIFT_METERS * t + 0.003, 5);
    }
    geometry.dispose();
    expect(buildParkAccessBridgeGeometry({ start: [0, 0], end: [0, 8], widthM: 2.2, streetLiftM: 0.2,
      groundAt: (x, y) => y > 3 && y < 5 ? null : groundAt(x, y) })).toBeNull();
  });
  it('joins shared triangle planes exactly even when a short bridge crosses a grid diagonal', () => {
    const groundAt = (x: number, y: number) => Math.max(x, y) * .1;
    const geometry = buildParkAccessBridgeGeometry({ start: [2, 1], end: [2, 3], widthM: 2,
      streetLiftM: .2, groundAt, groundGrid: { westX: 0, southY: 0, stepX: 4, stepY: 4, columns: 2, rows: 2 } })!;
    const p = geometry.getAttribute('position'), indices = geometry.index!;
    for (let i = 0; i < indices.count; i += 3) {
      const ids = [0, 1, 2].map((j) => indices.getX(i + j));
      const x = ids.reduce((sum, id) => sum + p.getX(id), 0) / 3;
      const y = ids.reduce((sum, id) => sum + p.getY(id), 0) / 3;
      const z = ids.reduce((sum, id) => sum + p.getZ(id), 0) / 3, t = (y - 1) / 2;
      expect(z).toBeCloseTo(groundAt(x, y) + .2 * (1 - t) + PUBLIC_REALM_GROUND_SURFACE_LIFT_METERS * t + .003, 6);
    }
    geometry.dispose();
  });
});
