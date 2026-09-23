import { describe, expect, it } from 'vitest';
import { createPublicRealmPlant } from './publicRealmPlantGeometry';
import { finishParkSurface } from './publicRealmSurfaceFinish';

describe('public realm planting pilot', () => {
  it.each(['shrub', 'grass', 'perennial'] as const)('%s stays inside the previous placement envelope with a bounded mesh', kind => {
    const g = createPublicRealmPlant(kind), p = g.getAttribute('position');
    expect(p.count / 3).toBeLessThan(400);
    expect(g.getAttribute('color').count).toBe(p.count);
    expect(Array.from(p.array).every(Number.isFinite)).toBe(true);
    expect(g.boundingBox!.min.z).toBeGreaterThanOrEqual(-.501);
    expect(g.boundingBox!.max.z).toBeLessThanOrEqual(.5);
    for (let i = 0; i < p.count; i++) expect(Math.hypot(p.getX(i),p.getY(i))).toBeLessThanOrEqual(.55);
    expect(Array.from(createPublicRealmPlant(kind).getAttribute('position').array)).toEqual(Array.from(p.array));
    g.dispose();
  });
  it('adds deterministic restrained surface grain without changing transparency or erasing path contrast', () => {
    const pixels = new Uint8ClampedArray([100,130,80,255,195,185,165,128]);
    const copy = pixels.slice();
    finishParkSurface(pixels,2,8); finishParkSurface(copy,2,8);
    expect(pixels).toEqual(copy);
    expect(pixels[3]).toBe(255); expect(pixels[7]).toBe(128);
    expect(pixels[4]-pixels[0]).toBeGreaterThan(75);
  });
});
