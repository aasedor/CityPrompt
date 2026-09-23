import { describe, expect, it } from 'vitest';
import { createMeadowFurniture, type MeadowFurnitureKind } from './meadowFurnitureGeometry';

describe('meadow furniture in the authoritative placement envelopes', () => {
  const radii: Record<MeadowFurnitureKind, number> = {
    bench: 1.15, picnic_table: 1.42, bin: .4, light: .34,
    backless_bench: 1.15, bike_rack: 1.02, planter: .9,
  };
  for (const kind of Object.keys(radii) as MeadowFurnitureKind[]) {
    it(`${kind} has finite metre-scale geometry, supported feet and a bounded render cost`, () => {
      const geometry = createMeadowFurniture(kind);
      const positions = geometry.getAttribute('position');
      expect(positions.count / 3).toBeLessThan(1800);
      expect(geometry.getAttribute('color').count).toBe(positions.count);
      for (let i = 0; i < positions.count; i++) {
        expect(Number.isFinite(positions.getZ(i))).toBe(true);
        expect(Math.hypot(positions.getX(i), positions.getY(i))).toBeLessThanOrEqual(radii[kind]);
      }
      expect(geometry.boundingBox!.min.z).toBeCloseTo(0, 5);
      expect(geometry.boundingBox!.max.z).toBeLessThan(kind === 'light' ? 3.8 : kind === 'planter' ? 1.4 : 1);
      const repeated = createMeadowFurniture(kind);
      expect(repeated.getAttribute('position').array).toEqual(positions.array);
      repeated.dispose();
      geometry.dispose();
    });
  }
});
