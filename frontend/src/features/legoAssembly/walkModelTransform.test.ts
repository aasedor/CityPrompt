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
      expect(walkModelLocal(object, point.clone(), point.clone()).distanceTo(result)).toBeLessThan(1e-8);
    } finally { invert.mockRestore(); }
  });
});
