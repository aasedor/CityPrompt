import { describe, expect, it, vi } from 'vitest';

import {
  buildStreetTransitShelterInstanceParts,
  createStreetTransitShelterResources,
  type StreetTransitShelterPlacement,
} from './GlobeStreetTransitShelterInstances';

function shelter(overrides: Partial<StreetTransitShelterPlacement> = {}): StreetTransitShelterPlacement {
  return {
    x: 10,
    y: 20,
    z: 3,
    yawRad: 0,
    scale: 1,
    ...overrides,
  };
}

describe('street transit shelter instance assembly', () => {
  it('builds deterministic frame, transparent-screen, roof and bench batches', () => {
    const placements = [shelter(), shelter({ x: 30, scale: 0.8 })];
    const first = buildStreetTransitShelterInstanceParts(placements);
    expect(buildStreetTransitShelterInstanceParts(placements)).toEqual(first);
    expect(first.frames).toHaveLength(14);
    expect(first.glass).toHaveLength(8);
    expect(first.roofs).toHaveLength(2);
    expect(first.benches).toHaveLength(8);
  });

  it('rotates every local offset with the shelter heading', () => {
    const unrotated = buildStreetTransitShelterInstanceParts([shelter()]);
    const rotated = buildStreetTransitShelterInstanceParts([
      shelter({ yawRad: Math.PI / 2 }),
    ]);
    expect(rotated.frames[0].x).toBeCloseTo(10 - (unrotated.frames[0].y - 20), 8);
    expect(rotated.frames[0].y).toBeCloseTo(20 + (unrotated.frames[0].x - 10), 8);
    [...rotated.frames, ...rotated.glass, ...rotated.roofs, ...rotated.benches]
      .forEach((part) => expect(part.yawRad).toBe(Math.PI / 2));
  });

  it('scales dimensions and local offsets uniformly while preserving the ground datum', () => {
    const base = buildStreetTransitShelterInstanceParts([shelter()]);
    const doubled = buildStreetTransitShelterInstanceParts([shelter({ scale: 2 })]);
    expect(doubled.roofs[0].scaleX).toBeCloseTo(base.roofs[0].scaleX * 2);
    expect(doubled.frames[0].x - 10).toBeCloseTo((base.frames[0].x - 10) * 2);
    expect(doubled.frames[0].z - 3).toBeCloseTo((base.frames[0].z - 3) * 2);
    [...doubled.frames, ...doubled.glass, ...doubled.roofs, ...doubled.benches]
      .forEach((part) => {
        expect(part.z - part.scaleZ / 2).toBeGreaterThanOrEqual(3 - 1e-8);
      });
  });

  it('owns physically distinct materials and disposes every resource exactly once', () => {
    const resources = createStreetTransitShelterResources();
    expect(resources.glassMaterial.transparent).toBe(true);
    expect(resources.glassMaterial.opacity).toBeLessThan(0.5);
    expect(resources.glassMaterial.transmission).toBeGreaterThan(0.5);
    expect(resources.glassMaterial.depthWrite).toBe(false);
    expect(resources.frameMaterial.metalness).toBeGreaterThan(0.5);
    expect(resources.benchMaterial.roughness).toBeGreaterThan(0.5);

    const disposeSpies = [
      vi.spyOn(resources.geometry, 'dispose'),
      vi.spyOn(resources.frameMaterial, 'dispose'),
      vi.spyOn(resources.glassMaterial, 'dispose'),
      vi.spyOn(resources.roofMaterial, 'dispose'),
      vi.spyOn(resources.benchMaterial, 'dispose'),
    ];
    resources.dispose();
    resources.dispose();
    disposeSpies.forEach((spy) => expect(spy).toHaveBeenCalledOnce());
  });
});
