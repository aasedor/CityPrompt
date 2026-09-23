import { describe, expect, it } from 'vitest';
import { Vector3 } from 'three';
import { createLandscapeCrownGeometry, landscapeTreeTint } from './landscapeCrownGeometry';

describe('lightweight landscape crowns', () => {
  it('keeps a bounded mesh inside the metric species envelope', () => {
    const { foliage: geometry, branches } = createLandscapeCrownGeometry();
    const size = geometry.boundingBox!.getSize(new Vector3());
    for (const dimension of size.toArray()) expect(dimension).toBeCloseTo(1);
    expect(geometry.boundingBox!.getCenter(new Vector3()).length()).toBeLessThan(1e-6);
    expect(geometry.index!.count / 3).toBeLessThanOrEqual(2400);
    for (const value of geometry.getAttribute('normal').array) expect(Number.isFinite(value)).toBe(true);
    // Foliage must have both overhead and lateral faces, rather than a flat cap.
    const normals = geometry.getAttribute('normal');
    expect(Array.from({ length: normals.count }, (_, i) => normals.getZ(i)).some(z => z > 0.8)).toBe(true);
    expect(Array.from({ length: normals.count }, (_, i) => normals.getX(i)).some(x => x > 0.8)).toBe(true);
    expect(branches.index!.count / 3).toBeLessThanOrEqual(200);
    geometry.dispose();
    branches.dispose();
  });

  it('varies foliage subtly without random changes on reload', () => {
    expect(landscapeTreeTint(12.5, -8).equals(landscapeTreeTint(12.5, -8))).toBe(true);
    const colours = new Set(Array.from({ length: 20 }, (_, i) => landscapeTreeTint(i * 8, 4).getHex()));
    expect(colours.size).toBeGreaterThan(10);
  });
});
