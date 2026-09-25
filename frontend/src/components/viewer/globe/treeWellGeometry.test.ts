import { describe, expect, it } from 'vitest';
import * as THREE from 'three';
import { createTreeWellGeometry, TREE_WELL_STYLES } from './treeWellGeometry';

describe('tree wells', () => {
  it.each(TREE_WELL_STYLES)('%s stays inside a bounded metric footprint with finite, coloured geometry', style => {
    const g = createTreeWellGeometry(style);
    expect([...g.attributes.position.array].every(Number.isFinite)).toBe(true);
    expect(g.attributes.color.count).toBe(g.attributes.position.count);
    expect(g.boundingBox!.min.x).toBeCloseTo(-.9, 5);
    expect(g.boundingBox!.max.x).toBeCloseTo(.9, 5);
    expect(g.boundingBox!.min.z).toBeCloseTo(0, 5);
    expect(g.boundingBox!.max.z).toBeLessThan(.51);
    expect(g.attributes.position.count / 3).toBeLessThan(1800);
    g.dispose();
  });
  it('leaves a real trunk opening and slots revealing soil instead of a solid grate slab', () => {
    const g = createTreeWellGeometry('grate');
    const material = new THREE.MeshBasicMaterial({ side: THREE.DoubleSide });
    const mesh = new THREE.Mesh(g, material);
    const height = (x: number, y: number) => {
      const ray = new THREE.Raycaster(new THREE.Vector3(x, y, 1), new THREE.Vector3(0, 0, -1));
      return ray.intersectObject(mesh)[0].point.z;
    };
    expect(height(.1, .1)).toBeCloseTo(.01, 5); // soil collar
    expect(height(.375, 0)).toBeGreaterThan(.02); // metal ring
    const angle = Math.PI / 32;
    expect(height(.44 * Math.cos(angle), .44 * Math.sin(angle))).toBeCloseTo(.01, 5);
    g.dispose(); material.dispose();
  });
});
