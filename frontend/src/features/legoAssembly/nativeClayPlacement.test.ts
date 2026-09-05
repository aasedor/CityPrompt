import { describe, expect, it } from 'vitest';
import * as THREE from 'three';
import { centreNativeClayClone, isNativeClayPlan } from './nativeClayPlacement';

describe('native clay placement', () => {
  it('centres an asymmetric model by translation without changing its geometry, scale or cached source', () => {
    const source = new THREE.Group();
    source.position.set(3, 2, -4);
    const geometry = new THREE.BoxGeometry(11.12, 7.903, 12.91);
    const mesh = new THREE.Mesh(geometry);
    mesh.position.set(0.415, 3.9515, -0.7);
    source.add(mesh);
    const originalBounds = new THREE.Box3().setFromObject(source, true);
    const originalVertices = Array.from(geometry.getAttribute('position').array);
    const placed = centreNativeClayClone(source.clone(true));
    const bounds = new THREE.Box3().setFromObject(placed, true);
    expect(bounds.min.y).toBeCloseTo(0, 6);
    expect(bounds.getCenter(new THREE.Vector3()).x).toBeCloseTo(0, 6);
    expect(bounds.getCenter(new THREE.Vector3()).z).toBeCloseTo(0, 6);
    expect(bounds.getSize(new THREE.Vector3()).distanceTo(originalBounds.getSize(new THREE.Vector3()))).toBeLessThan(1e-6);
    expect(placed.scale.toArray()).toEqual([1, 1, 1]);
    expect(placed.children[0].scale.toArray()).toEqual([1, 1, 1]);
    expect(new THREE.Box3().setFromObject(source, true)).toEqual(originalBounds);
    expect(Array.from(geometry.getAttribute('position').array)).toEqual(originalVertices);
    // The planned transform applies to the wrapper without discarding the
    // geometry-centering offset. A quarter turn swaps width and depth only.
    placed.rotation.y = Math.PI / 2;
    placed.position.set(25, 10, 30);
    const moved = new THREE.Box3().setFromObject(placed, true);
    expect(moved.min.y).toBeCloseTo(10, 6);
    expect(moved.getCenter(new THREE.Vector3()).x).toBeCloseTo(25, 6);
    expect(moved.getCenter(new THREE.Vector3()).z).toBeCloseTo(30, 6);
    expect(moved.getSize(new THREE.Vector3()).x).toBeCloseTo(12.91, 5);
    expect(moved.getSize(new THREE.Vector3()).z).toBeCloseTo(11.12, 5);
    geometry.dispose();
  });

  it('only changes origins for explicitly native clay plans', () => {
    const fit = { scale_x: 1, scale_y: 1, score: 1 };
    expect(isNativeClayPlan({ fit })).toBe(false);
    expect(isNativeClayPlan({ fit: { ...fit, native_scale_locked: true } })).toBe(false);
    expect(isNativeClayPlan({ fit: { ...fit, delivery_format: 'architectural_clay' } })).toBe(false);
    expect(isNativeClayPlan({ fit: { ...fit, native_scale_locked: true, delivery_format: 'architectural_clay' } })).toBe(true);
  });
});
