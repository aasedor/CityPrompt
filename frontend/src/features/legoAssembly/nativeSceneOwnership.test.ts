import { describe, expect, it } from 'vitest';
import * as THREE from 'three';
import { prepareOwnedNativeScene } from './buildingOnlyScene';

describe('source-owned native assemblies', () => {
  it('retains a complete deck without its touching far extension or mutating the cached source', () => {
    const source = new THREE.Group();
    const near = new THREE.BoxGeometry(8, 1.2, 166).toNonIndexed().translate(0, 7.8, 0);
    const far = new THREE.BoxGeometry(8, 1.2, 520).toNonIndexed().translate(0, 7.8, 343);
    const geometry = new THREE.BufferGeometry();
    for (const key of ['position', 'normal', 'uv']) geometry.setAttribute(key,
      new THREE.Float32BufferAttribute([...near.getAttribute(key).array, ...far.getAttribute(key).array], key === 'uv' ? 2 : 3));
    const mesh = new THREE.Mesh(geometry); mesh.name = 'DECK'; source.add(mesh);
    const result = prepareOwnedNativeScene(source, { regions: [], landscape: [], triangleRanges: { DECK: [[0, 12]] },
      triangleRegions: { DECK: [[-4.01, 7.19, -83.01, 4.01, 8.41, 83.01]] } });
    const kept = result.clone.getObjectByName('DECK') as THREE.Mesh;
    expect(kept.geometry.getIndex()?.count).toBe(36);
    expect(new THREE.Box3().setFromObject(kept).max.z).toBeCloseTo(83);
    expect(geometry.getAttribute('position').count).toBe(72);
    expect(kept.geometry.getAttribute('normal').count).toBe(36);
    expect(result.ownedGeometries).toEqual([kept.geometry]);
  });
});
