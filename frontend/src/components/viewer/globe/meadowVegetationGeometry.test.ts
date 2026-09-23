import { describe, expect, it } from 'vitest';
import { createMeadowVegetation, MEADOW_VEGETATION_SPECS, type MeadowVegetationKind } from './meadowVegetationGeometry';

describe('meadow vegetation prototypes', () => {
  for (const kind of Object.keys(MEADOW_VEGETATION_SPECS) as MeadowVegetationKind[]) {
    it(`${kind} stays in its metric canopy envelope and triangle budget across seeds`, () => {
      const spec = MEADOW_VEGETATION_SPECS[kind];
      for (const seed of [1, 17, 91]) {
        const parts = createMeadowVegetation(kind, seed);
        let triangles = 0;
        for (const geometry of Object.values(parts)) {
          const positions = geometry.getAttribute('position');
          triangles += positions.count / 3;
          expect(positions.count).toBeGreaterThan(0);
          expect(geometry.getAttribute('color').count).toBe(positions.count);
          for (let i = 0; i < positions.count; i++) {
            const x = positions.getX(i), y = positions.getY(i), z = positions.getZ(i);
            expect(Number.isFinite(x + y + z)).toBe(true);
            expect(Math.hypot(x, y)).toBeLessThanOrEqual(spec.radiusM);
            expect(z).toBeGreaterThanOrEqual(-.04); // tiny angled stem-foot bevel
            expect(z).toBeLessThanOrEqual(spec.maxHeightM);
          }
          geometry.dispose();
        }
        expect(triangles).toBeLessThanOrEqual(spec.maxTriangles);
      }
    }, 20_000);
  }
  it('repeats a seed exactly and gives different branch geometry for another seed', () => {
    const first = createMeadowVegetation('shade_tree', 17);
    const repeated = createMeadowVegetation('shade_tree', 17);
    const other = createMeadowVegetation('shade_tree', 18);
    expect(first.foliage.getAttribute('position').array).toEqual(repeated.foliage.getAttribute('position').array);
    expect(first.wood.getAttribute('position').array).not.toEqual(other.wood.getAttribute('position').array);
    [first, repeated, other].forEach(parts => Object.values(parts).forEach(g => g.dispose()));
  });
});
