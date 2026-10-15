import { describe, expect, it, vi } from 'vitest';
import * as THREE from 'three';
import { walkModelLocal } from './walkModelTransform';

describe('cached walking placement transforms', () => {
  it('reuses the inverse while a model stays still and refreshes parent translation, rotation and scale', () => {
    const parent = new THREE.Group(), object = new THREE.Group(); parent.add(object);
    parent.position.set(1_000_000, 2_000_000, 3_000_000);
    const point = new THREE.Vector3(1_000_005, 2_000_006, 3_000_007), result = new THREE.Vector3();
    const invert = vi.spyOn(THREE.Matrix4.prototype, 'invert');
    try {
      expect(walkModelLocal(object, point, result).toArray()).toEqual([5,6,7]);
      for (let i = 0; i < 20; i++) walkModelLocal(object, point, result);
      expect(invert).toHaveBeenCalledTimes(1);
      parent.position.x += 2; parent.rotation.y = .7; parent.scale.set(2,3,4);
      object.position.z = 8;
      walkModelLocal(object, point, result);
      expect(invert).toHaveBeenCalledTimes(2);
      expect(result.distanceTo(object.worldToLocal(point.clone()))).toBeLessThan(1e-8);
      expect(point.toArray()).toEqual([1_000_005,2_000_006,3_000_007]);
      const aliased = point.clone();
      expect(walkModelLocal(object, aliased, aliased)).toBe(aliased);
      expect(aliased.distanceTo(result)).toBeLessThan(1e-8);
    } finally { invert.mockRestore(); }
  });

  it('keeps independent placement caches and follows a reparented model', () => {
    const firstParent = new THREE.Group(), secondParent = new THREE.Group();
    const first = new THREE.Group(), second = new THREE.Group();
    firstParent.position.set(1_000_000, 2_000_000, 3_000_000);
    secondParent.position.set(1_000_030, 2_000_050, 3_000_070);
    firstParent.add(first); secondParent.add(second);
    const point = new THREE.Vector3(1_000_005, 2_000_006, 3_000_007);
    const target = new THREE.Vector3();
    expect(walkModelLocal(first, point, target).toArray()).toEqual([5,6,7]);
    expect(walkModelLocal(second, point, target).toArray()).toEqual([-25,-44,-63]);
    secondParent.add(first);
    secondParent.rotation.z = .5;
    secondParent.scale.set(2, 3, 4);
    const actual = walkModelLocal(first, point, target).clone();
    expect(actual.distanceTo(first.worldToLocal(point.clone()))).toBeLessThan(1e-8);
    expect(walkModelLocal(second, point, target).distanceTo(actual)).toBeLessThan(1e-8);
  });
});
